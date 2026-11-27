"""Compare prescribed families of overlapping first-round groups under both knot laws."""

import argparse
from collections import Counter
from itertools import combinations, combinations_with_replacement, product
import json
from pathlib import Path
import random
import resource
import signal
import sys
import time

from core import build_core
from reader import predict_core
from sample import make_start


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'LOOK-ALIKE-20261126-001'))
from alike import grow


class Cutoff(Exception):
    pass


timing_case = False


def expire(*_):
    if timing_case:
        raise Cutoff()


def cases():
    # The first group pair and its nearly identical control are available as a small prefix.
    base = [(0, 1, 2), (0, 1, 3)]
    yield 'two overlapping groups, one chain', base, (1, 1, 1, 2)
    yield 'same two groups, one fewer offshoot at both common knots', base, (0, 0, 1, 2)
    for common_count, private_count in ((2, 2), (3, 2), (2, 3)):
        groups = [(*range(common_count), common_count + i) for i in range(private_count)]
        for common in combinations_with_replacement(range(3), common_count):
            for other in combinations_with_replacement(range(3), private_count - 1):
                extra = common + (1,) + other
                if common_count == private_count == 2 and extra in ((1, 1, 1, 2), (0, 0, 1, 2)):
                    continue
                yield f'{private_count} groups sharing {common_count} knots', groups, extra
    for length in (3, 4):
        groups = [tuple(range(i, i + 3)) for i in range(length)]
        for common in product(range(2), repeat=length):
            for last in range(3):
                yield 'successive groups sharing two knots', groups, (1,) + common + (last,)
    for depth in (1, 2, 3):
        groups = base + [(2, 4)] + [(i, i + 1) for i in range(4, 3 + depth)]
        for a, b in combinations_with_replacement(range(3), 2):
            for c, d in product(range(2), range(3)):
                yield 'chain on an attached sequence of pair groups', groups, (a, b, c, d, *([0] * (depth - 1)), 1)


def start(groups, extra):
    # A separate spent knot for each common-neighbour pair realises exactly these
    # maximal groups. The pair groups in the last family are uncovered pairs.
    blocks = sorted({pair for group in groups for pair in combinations(sorted(group), 2)})
    loose = [sum(i in g for g in groups) + amount for i, amount in enumerate(extra)]
    return make_start(blocks, loose, random.Random(3)), loose


def positives(row, other):
    def counts(view):
        return Counter({tuple(k): value for k, value in view['sig0']})
    return [[list(k), v] for k, v in sorted((counts(row) - counts(other)).items())]


def evaluation(record, rounds, bound):
    description, groups, extra = record
    stars, loose = start(groups, extra)
    out = dict(family=description, groups=groups, loose=loose, knots=len(stars))
    # Both laws have the same first-round groups and finite core birth parents.
    for law in ('nae', 'parity'):
        core = build_core(stars, law)
        piece, = core.pieces
        if law == 'nae':
            out.update(cycle=piece.cycle, stop=piece.stop, chain_count=sum(piece.chains.values()),
                       core_births=piece.birth_count, births_in_ranks=list(map(len, piece.ranks.values())),
                       least_twin_round=piece.twin_rank - 1 if piece.twin else None)
            if piece.twin:
                t = piece.twin
                out['witness'] = dict(births=t.births, parents=t.parents, grandparent=t.grandparent,
                                      chain_base=t.chain_base)
        rows, status = predict_core(core, rounds, law)
        if rows is None:
            out[law] = dict(reading=status)
            continue
        grown = grow(stars, rounds, bound, law)
        actual = grown['rows']
        first = {key: next((i for i, (a, b) in enumerate(zip(actual, rows), 1) if a[key] != b[key]), None)
                 for key in ('n', 'sig0', 'sig1')}
        out[law] = dict(reading=status, grown_to=len(actual), end=grown['end'], first=first)
        if first['sig0']:
            i = first['sig0'] - 1
            out[law].update(grown_extra=positives(actual[i], rows[i]), read_extra=positives(rows[i], actual[i]))
    return out


def groups_from_parents(donors):
    """Small independent subset check of Lemma R for the certificate."""
    pairs = {frozenset((a, b)) for a, b in combinations(donors, 2) if donors[a] & donors[b]}
    neighbours = {a: {b for b in donors if frozenset((a, b)) in pairs} for a in donors}
    valid = set()
    for a in donors:
        later = sorted(b for b in neighbours[a] if a < b)
        for size in range(2, len(later) + 1):
            for others in combinations(later, size):
                group = frozenset((a, *others))
                if (all(frozenset(pair) in pairs for pair in combinations(others, 2))
                        and not set.intersection(*(donors[x] for x in group))):
                    valid.add(group)
    large = {g for g in valid if not any(g < h for h in valid)}
    return large | {p for p in pairs if not any(p <= g for g in large)}


def certificate():
    """Check the entire finite core and all chain group rosters up to the first difference."""
    groups = [tuple(range(i, i + 3)) for i in range(4)]
    stars, loose = start(groups, (1, 0, 0, 0, 0, 1))
    core = build_core(stars)
    piece, = core.pieces
    chain_bases = tuple(sorted(piece.chains))
    assert [piece.chains[b] for b in chain_bases] == [1, 1]
    assert piece.finished and piece.cycle and piece.twin is None
    # From the supplied start itself, reconstruct both the groups and each leftover birth.
    owners = {d: {i for i, knot in enumerate(stars) if d in knot} for knot in stars for d in knot}
    start_loose = [sum(len(owners[d]) == 1 for d in knot) for knot in stars]
    neighbours = {i: set().union(*(owners[d] for d in stars[i])) - {i}
                  for i, count in enumerate(start_loose) if count}
    assert set(neighbours) == set(piece.ranks[1])
    first = [piece.nodes[k].parents for k in piece.ranks[2]]
    assert groups_from_parents(neighbours) == {frozenset(p) for p in first if len(p) > 1}
    assert Counter(k for parents in first for k in parents) == Counter({k: start_loose[k] for k in neighbours})
    overlaps = []
    for rank in range(2, max(piece.ranks) + 1):
        donors = {i: set(piece.nodes[i].parents) for i in piece.ranks[rank]}
        expected = {frozenset(piece.nodes[i].parents) for i in piece.ranks.get(rank + 1, ())}
        assert groups_from_parents(donors) == expected
        for a, b in combinations(donors, 2):
            for c, d in combinations(sorted(donors[a] & donors[b]), 2):
                common = sorted(set(piece.nodes[c].parents) & set(piece.nodes[d].parents))
                held = [sorted(piece.nodes[q].points & set(chain_bases)) for q in common]
                assert not any(held)
                overlaps.append(dict(round=rank - 1, births=[a, b], parents=[c, d],
                                     common_grandparents=common, their_chain_bases=held))

    def expanded(round_number):
        donors = {}
        for i, birth in piece.nodes.items():
            length = round_number - (birth.rank - 1)
            for left in range(length + 1):
                right = length - left
                anchors = {p for p, n in zip(chain_bases, (left, right)) if n}
                if not anchors <= birth.points:
                    continue
                ps = {(p, left, right) for p in birth.parents if anchors <= piece.nodes[p].points}
                if left:
                    ps.add((i, left - 1, right))
                if right:
                    ps.add((i, left, right - 1))
                donors[i, left, right] = ps
        return donors

    direct = []
    for round_number in range(1, 10):
        parents = expanded(round_number)
        true_groups = groups_from_parents(parents)
        next_states = expanded(round_number + 1)
        read_groups = {frozenset(p) for p in next_states.values() if len(p) >= 2}
        extra = sorted(sorted(g) for g in true_groups - read_groups)
        missing = sorted(sorted(g) for g in read_groups - true_groups)
        # Every checked round makes several births, so a single birth cannot
        # consume all loose distinctions. Lemma R's ordinary fresh count applies.
        assert len(parents) >= 2 and len(true_groups) >= 2
        demand = Counter(k for g in true_groups for k in g)
        true_fresh = {k: max(demand[k], 3 - len(ps), 1) for k, ps in parents.items()}
        read_fresh = Counter(k for ps in next_states.values() for k in ps)
        changed = [dict(birth=k, grown_fresh=f, read_fresh=read_fresh[k])
                   for k, f in true_fresh.items() if f != read_fresh[k]]
        assert len(read_groups) == sum(len(ps) >= 2 for ps in next_states.values())
        offshoots = sum(true_fresh[k] - demand[k] for k in parents)
        direct.append(dict(round=round_number, grown_groups_for_next_round=len(true_groups),
                           read_groups_for_next_round=len(read_groups), true_offshoots_for_next_round=offshoots,
                           read_offshoots_for_next_round=len(next_states) - len(read_groups),
                           extra=extra, missing=missing, fresh_differences=changed))
    assert all(r['extra'] == r['missing'] == r['fresh_differences'] == [] for r in direct[:-1])
    last = direct[-1]
    assert len(last['extra']) == 2 and len(last['missing']) == 1
    u, v = sorted(piece.ranks[8])
    z, = piece.ranks[9]
    left, right = (z, 1, 0), (z, 0, 1)
    from_u, from_v = (u, 1, 1), (v, 1, 1)
    assert not (parents[from_u] & parents[from_v])
    assert last['missing'] == [sorted([from_u, from_v, left, right])]
    assert last['extra'] == sorted([sorted([from_u, left, right]), sorted([from_v, left, right])])
    assert {(tuple(item['birth']), item['grown_fresh'], item['read_fresh'])
            for item in last['fresh_differences']} == {(left, 3, 2), (right, 3, 2)}
    by_law = {}
    for law in ('nae', 'parity'):
        rows, _ = predict_core(build_core(stars, law), 10, law)
        actual = grow(stars, 10, 800, law)['rows']
        assert len(rows) == len(actual) == 10
        by_law[law] = dict(grown_birth_counts=[r['n'] for r in actual],
                           read_birth_counts=[r['n'] for r in rows],
                           round_9_grown_sig0=actual[8]['sig0'], round_9_read_sig0=rows[8]['sig0'])
    return dict(groups=groups, loose=loose, stars=stars, cyclic_incidence_count=3,
                core_births_from_start_on=list(map(len, piece.ranks.values())),
                chain_bases=chain_bases, core_birth_pairs_with_two_common_parents=overlaps,
                chain_state_key=['core birth', 'length at first chain base', 'length at second chain base'],
                supports_of_common_parents={str(i): sorted(piece.nodes[i].points & set(chain_bases))
                                           for i in set(piece.nodes[u].parents) & set(piece.nodes[v].parents)},
                disjoint_parent_sets=[dict(birth=state, parents=sorted(parents[state]))
                                      for state in (from_u, from_v)],
                next_round_group_comparison=direct, ordinary_growth=by_law)


def later_twin_certificate():
    """Connect the spent knots of two starts while keeping their live pieces separate."""
    early_groups = [tuple(range(i, i + 3)) for i in range(4)]
    early_extra = (1, 0, 0, 0, 0, 1)
    late_groups = [(0, 1, 2), (0, 1, 3), (2, 4), (4, 5), (5, 6), (6, 7), (7, 8)]
    late_extra = (1, 1, 0, 0, 0, 0, 0, 0, 1)
    joint_groups = early_groups + [tuple(k + 6 for k in g) for g in late_groups]
    out = {}
    for name, groups, extra, expected_round in (
        ('positive_control', late_groups, late_extra, 10),
        ('combined_start', joint_groups, early_extra + late_extra, 9),
    ):
        stars, loose = start(groups, extra)
        entry = dict(groups=groups, loose=loose, stars=stars, knots=len(stars))
        for law in ('nae', 'parity'):
            core = build_core(stars, law)
            pieces = [dict(cycle=p.cycle, chains=sum(p.chains.values()), stop=p.stop,
                           core_births=p.birth_count, least_twin_round=p.twin_rank - 1 if p.twin else None)
                      for p in core.pieces]
            assert all(p.cycle and p.finished for p in core.pieces)
            assert min(p.twin_rank - 1 for p in core.pieces if p.twin) == 10
            predicted, status = predict_core(core, 10, law)
            actual = grow(stars, 10, 800, law)['rows']
            assert status == 'predicted' and len(actual) == len(predicted) == 10
            first = {v: next((i for i, (a, b) in enumerate(zip(actual, predicted), 1) if a[v] != b[v]), None)
                     for v in ('n', 'sig0', 'sig1')}
            assert first['sig0'] == first['sig1'] == expected_round
            i = expected_round - 1
            entry[law] = dict(pieces=pieces, first=first, grown_counts=[r['n'] for r in actual],
                              read_counts=[r['n'] for r in predicted],
                              first_grown_extra=positives(actual[i], predicted[i]),
                              first_read_extra=positives(predicted[i], actual[i]))
        out[name] = entry
    return out


def main():
    global timing_case
    parser = argparse.ArgumentParser()
    parser.add_argument('--first', default=0, type=int)
    parser.add_argument('--stop', type=int)
    parser.add_argument('--rounds', default=10, type=int)
    parser.add_argument('--bound', default=800, type=int)
    parser.add_argument('--seconds', default=0.25, type=float)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--certificate-only', action='store_true')
    opts = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (1_400_000_000, 1_400_000_000))
    if opts.certificate_only:
        checked = dict(two_chain_certificate=certificate(), later_twin_certificate=later_twin_certificate())
        if opts.output:
            result = json.loads(opts.output.read_text())
            result.update(checked)
            opts.output.write_text(json.dumps(result, indent=1) + '\n')
        else:
            print(json.dumps(checked))
        return
    if opts.stop is None:
        parser.error('--stop is required for a series')
    signal.signal(signal.SIGPROF, expire)
    rows = []
    for i, case in enumerate(cases()):
        if i < opts.first:
            continue
        if i >= opts.stop:
            break
        before = time.process_time()
        try:
            timing_case = True
            signal.setitimer(signal.ITIMER_PROF, opts.seconds)
            try:
                row = evaluation(case, opts.rounds, opts.bound)
            finally:
                timing_case = False
                signal.setitimer(signal.ITIMER_PROF, 0)
        except (Cutoff, MemoryError, RecursionError) as err:
            timing_case = False
            signal.setitimer(signal.ITIMER_PROF, 0)
            row = dict(family=case[0], groups=case[1], extra=case[2], cut=type(err).__name__)
        row.update(index=i, cpu_seconds=round(time.process_time() - before, 5))
        if opts.output:
            rows.append(row)
        else:
            print(json.dumps(row), flush=True)
    if opts.output:
        summary = Counter()
        for row in rows:
            if 'cut' in row:
                summary['cut during construction or comparison'] += 1
                continue
            for law in ('nae', 'parity'):
                score = row[law]
                if score['reading'] != 'predicted':
                    outcome = score['reading']
                elif row['least_twin_round'] is not None and score['grown_to'] < row['least_twin_round']:
                    outcome = 'growth ended before the first twins'
                elif score['first']['sig0'] == score['first']['sig1'] == row['least_twin_round']:
                    outcome = 'matched twin round' if row['least_twin_round'] else 'chain, no twins, readings agree'
                else:
                    outcome = 'different from least twin round'
                summary[f'{law} / {outcome}'] += 1
        result = dict(rounds=opts.rounds, bound=opts.bound, process_bytes=1_400_000_000,
                      cpu_seconds_per_start=opts.seconds, constructor_seed=3,
                      generation_order='targeted.py cases(), zero-based; --stop is exclusive',
                      first=opts.first, requested_stop=opts.stop, completed_or_cut=len(rows),
                      summary=dict(summary), cases=rows, two_chain_certificate=certificate(),
                      later_twin_certificate=later_twin_certificate())
        opts.output.write_text(json.dumps(result, indent=1) + '\n')
        print(json.dumps(summary, sort_keys=True))


if __name__ == '__main__':
    main()
