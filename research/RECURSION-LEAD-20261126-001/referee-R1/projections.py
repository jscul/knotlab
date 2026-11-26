"""Check exchanged parity relations and the number of individual pins a return needs."""
from argparse import ArgumentParser
from collections import Counter
from functools import cache
from itertools import combinations
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
from time import perf_counter

from growth import advance, census, ring

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def positions(bits):
    while bits:
        bit = bits & -bits
        yield bit.bit_length() - 1
        bits ^= bit


def kernel(rows, names):
    # Pair each dependence among columns with its original choice of columns.
    columns = {}
    result = []
    for i in names:
        check = sum(1 << j for j, row in enumerate(rows) if i in row)
        used = 1 << i
        while check:
            p = check.bit_length()
            if p not in columns:
                columns[p] = (check, used)
                break
            other, history = columns[p]
            check ^= other
            used ^= history
        else:
            result.append(used)
    return result


def span(generators):
    words = [0]
    for word in generators:
        words += [previous ^ word for previous in words]
    return words


def mobile_count(stage, fixed):
    names = set().union(*stage)
    moved = 0
    for change in kernel(stage, sorted(names - set(fixed))):
        moved |= change
    return moved.bit_count()


def shortest(stage, fixed):
    names = set().union(*stage)
    generators = kernel(stage, sorted(names - set(fixed)))
    if len(generators) > 21:
        raise ValueError('Literal check would exceed its small-case allocation.')
    best, through = {}, {}
    for word in span(generators)[1:]:
        weight = word.bit_count()
        for i in positions(word):
            if i not in best or weight < best[i]:
                best[i], through[i] = weight, []
            if weight == best[i]:
                through[i].append(word)
    chosen = set().union(*through.values()) if through else set()
    return tuple(frozenset(positions(w)) for w in sorted(chosen))


@cache
def knot_test(arity, allowed):
    names = [f'x{i}' for i in range(arity)]
    excluded = sorted(set(range(1 << arity)) - set(allowed))
    clauses = [' '.join(('-' if w >> i & 1 else '') + v for i, v in enumerate(names))
               for w in excluded]
    p = subprocess.run(
        [sys.executable, '-B', '-m', 'knotlab', 'check', '--loops', *names[:-1],
         '--contact', names[-1], '--cnf', ';'.join(clauses), '--erasure', 'forgetting', '--json'],
        capture_output=True, check=True, text=True,
        env={**os.environ, 'PYTHONPATH': str(ROOT/'tools')})
    r = json.loads(p.stdout)
    assert {sum(int(x) << i for i, x in enumerate(w)) for w in r['allowed']} == set(allowed)
    return r['is_knot']


def projections(stage, extra=()):
    names = sorted(set().union(*stage))
    generators = kernel(tuple(stage) + tuple(extra), names)
    out = []
    for support in stage:
        local = [sum((1 << j) for j,i in enumerate(sorted(support)) if g >> i & 1)
                 for g in generators]
        possible = {0}
        for g in set(local):
            possible |= {v ^ g for v in possible}
        allowed = tuple(sorted(possible))
        out.append({'places': sorted(support), 'allowed_states': list(allowed),
                    'passes_forgetting_test': knot_test(len(support), allowed)})
    return out


def pin_test(start, all_subsets):
    grown, status, _ = advance(start)
    assert status == 'funded'
    holders = Counter(x for row in grown for x in row)
    loose = tuple(sorted(x for x, n in holders.items() if n == 1))
    names = set().union(*start)
    expected = set(shortest(grown, loose))
    assert len(set().union(*expected)) == len(names)
    counts = {}
    # In any connected arrangement, two free loose distinctions can change together
    # along a chain of shared distinctions. Mobility can only increase as pins lift.
    # Check every choice of released pairs and all single releases on every positive.
    sizes = range(len(loose)+1) if all_subsets else [0, 1, 2, len(loose)]
    for amount in sorted(set(sizes)):
        d = Counter()
        for freed in combinations(loose, amount):
            fixed = set(loose) - set(freed)
            width = mobile_count(grown, fixed)
            if width == len(names):
                assert set(shortest(grown, fixed)) == expected
                d['same exchange'] += 1
            else:
                assert width > len(names)
                d['too many mobile distinctions'] += 1
        counts[amount] = d
    pins = tuple((x,) for x in loose)
    return dict(start=[sorted(s) for s in start], grown=[sorted(s) for s in grown],
                loose=list(loose), source_distinctions=len(names),
                exchange=[sorted(s) for s in sorted(expected, key=lambda s: tuple(sorted(s)))],
                source_projections=projections(start),
                grown_projections_pinned=projections(grown,pins),
                release_sizes=counts)


def main():
    args = ArgumentParser()
    args.add_argument('--pilot', action='store_true')
    args.add_argument('--output', type=Path)
    opts = args.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (1 << 30, 1 << 30))
    start_time = perf_counter()
    cases = census()
    archive = [json.loads(line) for line in (HERE.parent/'recur_census.jsonl').read_text().splitlines()]
    selected = [i for i,r in enumerate(archive) if 'lawful' in (r['free exchange'], r['pinned exchange'])]
    if opts.pilot:
        selected = [165]
    totals, rows = Counter(), []
    for i in selected:
        s = cases[i]
        grown, status, _ = advance(s)
        assert status == 'funded'
        held = Counter(x for k in grown for x in k)
        for mode in ('pinned','free'):
            if archive[i][mode+' exchange'] != 'lawful':
                continue
            pins = {x for x,n in held.items() if n == 1 and mode == 'pinned'}
            e = shortest(grown, pins)
            checks = projections(e)
            passed = sum(p['passes_forgetting_test'] for p in checks)
            assert min(map(len, e)) >= 3 and max(Counter(x for s in e for x in s).values()) <= 2
            totals[mode+' exchanges'] += 1
            totals[mode+' supports'] += len(e)
            totals[mode+' supports passing'] += passed
            totals[mode+' all supports pass'] += passed == len(e)
            rows.append(dict(census=i,arm=mode,exchange=checks))
    pins = {'four knots, one without loose distinctions': pin_test(cases[165], True)}
    for n in ([5] if opts.pilot else [5,7,8,9,10]):
        pins[f'ring of {n} knots'] = pin_test(ring(n, 2), False)
    result = dict(lawful_exchange_totals=totals, exchanged_relations=rows,
                  partial_pinning=pins, elapsed_seconds=round(perf_counter()-start_time,4),
                  max_rss_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    if opts.output:
        opts.output.write_text(json.dumps(result, separators=(',',':'))+'\n')
    print(json.dumps(totals), f"{result['elapsed_seconds']} s")


if __name__ == '__main__':
    main()
