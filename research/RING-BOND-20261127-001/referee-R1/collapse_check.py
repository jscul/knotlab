"""Check each agreement word by literal substitution. Retain the archive order."""
import argparse
import json
import sys
from collections import Counter
from itertools import combinations, product
from pathlib import Path
from time import perf_counter

from pysat.solvers import Solver

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parents[1]
sys.path.insert(0, str(RESEARCH / 'NAE-LAYER-20261127-001' / 'referee-R1'))
from growth_rule import advance, supports_of


def missing_mask(supports, carriers, law):
    """For a word, identify equal literals, reverse a disagreeing pair, and
    treat a disagreeing triple as a further not-all-equal requirement."""
    result = 0
    for word in range(8):
        rename = {}
        unequal = []
        for i, group in enumerate(carriers):
            agree = word & (4 >> i)
            if agree or len(group) == 2:
                for j, x in enumerate(group):
                    rename[x] = (1 if agree or j == 0 else -1) * (group[0] + 1)
            else:
                unequal.append(group)
        clauses = []
        for support, kind in [(s, law) for s in supports] + [(c, 'nae') for c in unequal]:
            literals = [rename.get(x, x + 1) for x in support]
            if kind == 'nae':
                clauses.extend((literals, [-v for v in literals]))
            else:
                # A parity law excludes assignments with an odd number of ones.
                # Signed repetitions after substitution are allowed in a clause.
                for bits in product((0, 1), repeat=len(literals)):
                    if sum(bits) % 2:
                        clauses.append([-v if bit else v for v, bit in zip(literals, bits)])
        with Solver(bootstrap_with=clauses) as solver:
            if not solver.solve():
                result |= 1 << word
    return result


def states(supports, n):
    return [s for s in range(1 << n)
            if all(len({s >> x & 1 for x in support}) == 2 for support in supports)]


def reading(s, group):
    return int(len({s >> x & 1 for x in group}) == 1)


def local_fix_info(supports, allowed, group):
    local = []
    for support in supports:
        bins = {}
        for s in allowed:
            key = tuple(s >> x & 1 for x in support)
            bins.setdefault(key, set()).add(reading(s, group))
        local.append(max(map(len, bins.values())) == 1)
    return any(local)


def controls(limit):
    ring = ((0, 1, 3), (1, 2, 4), (0, 2, 5), (3, 4, 5, 6))
    allowed = states(ring, 7)
    carriers = list(combinations(range(7), 2)) + list(combinations(range(7), 3))
    local = {c: local_fix_info(ring, allowed, c) for c in carriers}
    counts = Counter()
    sample = {}
    for cs in combinations(carriers, 3):
        if len(set().union(*cs)) < sum(map(len, cs)):
            continue
        images = [{s: reading(s, c) for s in allowed} for c in cs]
        words = {4 * images[0][s] + 2 * images[1][s] + images[2][s] for s in allowed}
        mask = 255 - sum(1 << w for w in words)
        assert mask == missing_mask(ring, cs, 'nae')
        recent = 'contains a locally determined reading' if any(local[c] for c in cs) else 'all unread'
        free_pairs = all(len({(w >> i & 1, w >> j & 1) for w in words}) == 4
                         for i, j in combinations(range(3), 2))
        outcome = ('free' if mask == 0 else 'knot' if free_pairs else 'constrained pair')
        key = f'{outcome}, {recent}'
        counts[key] += 1
        sample.setdefault(key, {'carriers': cs, 'missing': [f'{w:03b}' for w in range(8) if mask >> w & 1]})
        if sum(counts.values()) == limit:
            break
    return {'all disjoint agreement triples, grown three-knot ring': sum(counts.values()),
            'image and determination': dict(sorted(counts.items())), 'examples': sample,
            'distinct feasible local fixings by knot': [
                len({tuple(s >> x & 1 for x in support) for s in allowed}) for support in ring]}


def stage_bonds(supports, law):
    if law == 'parity':
        from parity_replay import enumerate_stage
        bonds, _, _ = enumerate_stage(supports, born=0)
        return ((cs, data[0]) for cs, data in bonds.items())
    from census_replay import stage_records
    records = stage_records(supports, 4)
    return ((cs, mask) for cs, (mask, holders, readable) in records.items()
            if not readable and mask == holders[0][1])


def prefix(law, limit):
    starts = json.loads((RESEARCH / 'FORBID-EDITS-20261126-001' / 'starts.json').read_text())
    rows = []
    counts = Counter()
    for index in range(limit):
        start = supports_of(starts[index])
        if law == 'parity':
            from parity_replay import stages_for_start
            stages = stages_for_start(index)
        else:
            step = advance(start)
            stages = [start] + ([step.supports] if step.status == 'funded' else [])
        row = {'archive index': index, 'rounds': []}
        for supports in stages:
            checked = mismatches = 0
            for cs, mask in stage_bonds(supports, law):
                new_mask = missing_mask(supports, cs, law)
                checked += 1
                if mask != new_mask:
                    mismatches += 1
                    row.setdefault('differences', []).append([cs, mask, new_mask])
            row['rounds'].append({'knots': len(supports), 'bonds': checked, 'differences': mismatches})
            counts.update({'bonds': checked, 'differences': mismatches, 'stages': 1})
        rows.append(row)
    return {'law': law, 'prefix length': limit, 'totals': dict(counts), 'rows': rows}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('part', choices=['controls', 'nae', 'parity'])
    parser.add_argument('limit', type=int)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    started = perf_counter()
    result = controls(args.limit) if args.part == 'controls' else prefix(args.part, args.limit)
    result['seconds'] = round(perf_counter() - started, 4)
    if args.out:
        args.out.write_text(json.dumps(result, indent=2) + '\n')
        print({k: v for k, v in result.items() if k not in ('rows','examples')})
    else:
        print(json.dumps(result))
