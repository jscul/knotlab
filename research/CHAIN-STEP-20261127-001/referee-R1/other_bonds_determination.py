"""Find all possible carriers of a stage bond which determines a named upper reading."""

import argparse
from collections import Counter
import gzip
from itertools import combinations, product
import json
from pathlib import Path
import resource
from time import perf_counter

from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
BARE_PAIRS = (((3, 4, 5), (11, 12, 13)), ((0, 1, 10), (6, 15, 16)), ((7, 8, 9), (2, 14)))


def carried_pairs(supports, chain):
    knots = [set(supports[j]) for j in chain]
    joins = [(a & b).pop() for a, b in zip(knots, knots[1:])]
    labels = sorted(knots[0] - {joins[0]})
    for j in range(1, 7):
        labels.extend((joins[j - 1], (knots[j] - {joins[j - 1], joins[j]}).pop()))
    labels.extend((joins[-1], *sorted(knots[-1] - {joins[-1]})))
    assert len(set(labels)) == 17
    return tuple(tuple(tuple(sorted(labels[i] for i in carrier)) for carrier in pair) for pair in BARE_PAIRS)


def mask_of(carrier):
    return sum(1 << d for d in carrier)


def ids(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def agreed(word, mask):
    return word & mask in (0, mask)


class Stage:
    def __init__(self, supports):
        self.supports = tuple(tuple(sorted(k)) for k in supports)
        self.masks = tuple(map(mask_of, self.supports))
        self.n = max(map(max, self.supports)) + 1
        self.universe = (1 << self.n) - 1
        self.owners = [[] for _ in range(self.n)]
        self.solver = Solver()
        for j, k in enumerate(self.supports):
            for d in k:
                self.owners[d].append(j)
            for copy in range(2):
                raw = self.raw_literals(k, copy)
                self.solver.add_clause(raw)
                self.solver.add_clause([-u for u in raw])
        self.next_id = 2 * self.n
        self.truth = self.fresh()
        self.solver.add_clause([self.truth])
        self.eq = {}
        self.bit_same = tuple(self.equal_literals((1 + d, 1 + d + self.n)) for d in range(self.n))
        self.free_except = tuple(self.change_assumptions(d) for d in range(self.n))
        self.gates = {}

    def fresh(self):
        self.next_id += 1
        return self.next_id

    def raw_literals(self, raw, copy=0):
        return [1 + d + copy * self.n for d in raw]

    def equal_literals(self, literals):
        key = tuple(sorted(literals))
        if len(key) < 2:
            return self.truth
        if key not in self.eq:
            out = self.fresh()
            for x in key[1:]:
                self.solver.add_clause([-out, -key[0], x])
                self.solver.add_clause([-out, key[0], -x])
            self.solver.add_clause([out, *key])
            self.solver.add_clause([out, *(-x for x in key)])
            self.eq[key] = out
        return self.eq[key]

    def agreement(self, raw, copy=0):
        return self.equal_literals(self.raw_literals(raw, copy))

    def change_assumptions(self, d, omit=None):
        return tuple(-self.agreement([v for v in self.supports[j] if v not in (d, omit)]) for j in self.owners[d])

    def upper_literal(self, pair, both, copy):
        key = pair, both, copy
        if key not in self.gates:
            a, b = [self.agreement(x, copy) for x in pair]
            u = self.fresh()
            if both:
                clauses = ((-u, a), (-u, b), (u, -a, -b))
            else:
                clauses = ((u, -a), (u, -b), (-u, a, b))
            for clause in clauses:
                self.solver.add_clause(clause)
            self.gates[key] = u
        return self.gates[key]

    def raw_state(self):
        return sum(1 << d for d, value in enumerate(self.solver.get_model()[:self.n]) if value > 0)

    def flippable(self, state):
        blocked = 0
        for law in self.masks:
            ones = state & law
            zeros = ones ^ law
            if ones.bit_count() == 1:
                blocked |= ones
            if zeros.bit_count() == 1:
                blocked |= zeros
        return self.universe ^ blocked

    def group_collision(self, group, required):
        """Counterexample changing only members of this one potential carrier."""
        equality = self.equal_literals(tuple(self.agreement(group, j) for j in range(2)))
        fixing = [self.bit_same[x] for x in range(self.n) if x not in group]
        return self.solver.solve(assumptions=[equality, *required, *fixing])

    def determining(self, groups, required):
        equal = [self.equal_literals(tuple(self.agreement(g, j) for j in range(2))) for g in groups]
        return not self.solver.solve(assumptions=[*equal, *required])

    def bond(self, groups):
        r = [self.agreement(g) for g in groups]
        words = [w for w in product((0, 1), repeat=3)
                 if self.solver.solve(assumptions=[v if b else -v for v, b in zip(r, w)])]
        if len(words) == 8 or not all(len({(w[i], w[j]) for w in words}) == 4 for i, j in combinations(range(3), 2)):
            return None
        for k in self.supports:
            fixing = [self.bit_same[x] for x in k]
            for g in groups:
                if not self.solver.solve(assumptions=[*fixing, self.agreement(g), -self.agreement(g, 1)]):
                    return None
        return [''.join(map(str, w)) for w in words]

    def reducer(self, pair, both, force_all_doubles=False):
        pair = tuple(tuple(sorted(x)) for x in pair)
        masks = tuple(map(mask_of, pair))
        domain = masks[0] | masks[1]
        def upper(state):
            a, b = (agreed(state, m) for m in masks)
            return (a and b) if both else (a or b)
        outside = self.universe ^ domain
        required = [self.upper_literal(pair, both, 0), -self.upper_literal(pair, both, 1)]
        allowed_outside = {}
        samples = {}
        for side, group in enumerate(pair):
            other = self.agreement(pair[1 - side])
            for d in group:
                own = self.agreement([v for v in group if v != d])
                query = [*self.free_except[d], own, other if both else -other]
                if not self.solver.solve(assumptions=query):
                    continue
                remaining = outside
                witnesses = []
                def incorporate():
                    nonlocal remaining
                    state = self.raw_state()
                    flipped = state ^ (1 << d)
                    assert upper(state) != upper(flipped)
                    assert all(not agreed(flipped, m) for m in self.masks)
                    free = self.flippable(state) & self.flippable(flipped)
                    remaining &= ~free
                    witnesses.append(state)
                incorporate()
                for e in ids(remaining):
                    if remaining & (1 << e):
                        enabled = self.change_assumptions(e, d)
                        if -self.truth not in enabled and self.solver.solve(assumptions=[*query, *enabled]):
                            incorporate()
                            assert not (remaining & (1 << e))
                allowed_outside[d] = remaining
                samples[d] = witnesses
        mandatory = mask_of(allowed_outside)
        if not mandatory:
            raise ValueError('No essential raw distinction; the reducer requires a nonempty cover')
        candidate = set()
        for d in ids(mandatory):
            others = tuple(ids((domain | allowed_outside[d]) ^ (1 << d)))
            for count in (1, 2):
                for rest in combinations(others, count):
                    raw = tuple(sorted((d, *rest)))
                    group_mask = mask_of(raw)
                    if any(group_mask & outside & ~allowed_outside[v] for v in ids(group_mask & mandatory)):
                        continue
                    candidate.add(raw)
        survivors = []
        for raw in sorted(candidate):
            m = mask_of(raw)
            if len(raw) == 3 and any(
                not agreed(s, m ^ (1 << d)) for d in raw if d in samples for s in samples[d]
            ):
                continue
            if raw in pair or not self.group_collision(raw, required):
                survivors.append(raw)
        covers_two = []
        covers_three = []
        determining_bonds = []
        remaining_two = []
        for count in (1, 2, 3):
            for groups in combinations(survivors, count):
                raw_masks = list(map(mask_of, groups))
                union = 0
                for m in raw_masks:
                    if union & m:
                        break
                    union |= m
                else:
                    if mandatory & ~union:
                        continue
                    if count == 1:
                        raise ValueError(f'A single group covers all mandatory distinctions: {groups}')
                    if count == 2:
                        covers_two.append(groups)
                        if set(groups) == set(pair) and not force_all_doubles:
                            continue
                        remaining_two.append(groups)
                    else:
                        covers_three.append(groups)
                        if self.determining(groups, required):
                            words = self.bond(groups)
                            if words:
                                determining_bonds.append({'groups': groups, 'words': words})
        return {
            'mandatory': list(ids(mandatory)), 'admissible_outsider_counts': [m.bit_count() for m in allowed_outside.values()],
            'raw_flip_states': sum(map(len, samples.values())), 'candidate_groups': len(candidate), 'surviving_groups': survivors,
            'two_touching_groups': covers_two, 'two_touching_groups_left_to_examine': remaining_two,
            'three_touching_group_covers': len(covers_three), 'determining_three_touching_bonds': determining_bonds,
        }


def rows():
    with gzip.open(HERE / 'stages.jsonl.gz', 'rt') as f:
        return [r for line in f if (r := json.loads(line))['checked_chains']]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pilot', action='store_true')
    ap.add_argument('--stage', type=int, nargs=2, action='append')
    ns = ap.parse_args()
    stages = rows()
    if ns.stage:
        chosen = set(map(tuple, ns.stage))
        stages = [r for r in stages if (r['start'], r['round']) in chosen]
    if ns.pilot:
        stages = [min(stages, key=lambda r: max(map(max, r['supports']))),
                  max(stages, key=lambda r: max(map(max, r['supports']))),
                  next(r for r in stages if r['start'] == 90),
                  next(r for r in stages if r['start'] == 0 and r['round'] == 6)]
    tag = 'pilot' if ns.pilot else 'subset' if ns.stage else 'counts'
    total = Counter()
    largest = Counter()
    begin = perf_counter()
    timings = []
    with gzip.open(HERE / f'other_bonds_determination_{tag}.jsonl.gz', 'wt', compresslevel=5) as out:
        for row in stages:
            start_time = perf_counter()
            stage = Stage(row['supports'])
            memo = {}
            diagnostics = Counter()
            for rank, chain in enumerate(row['checked_chains']):
                for pos, pair in enumerate(carried_pairs(row['supports'], chain)):
                    for both in (False, True):
                        key = tuple(sorted(pair)), both
                        if key not in memo:
                            memo[key] = stage.reducer(pair, both)
                        result = memo[key]
                        record = {'start': row['start'], 'round': row['round'], 'chain_index_zero_based': rank,
                                  'pair_index_zero_based': pos, 'mode': 'both' if both else 'either', 'pair': pair, **result}
                        out.write(json.dumps(record, separators=(',', ':')) + '\n')
                        diagnostics['functions_counting_each_chain'] += 1
                        diagnostics['all_raw_members_mandatory'] += (len(result['mandatory']) == sum(map(len, pair)))
                        diagnostics['unexamined_noncanonical_two_group_covers'] += len(result['two_touching_groups_left_to_examine'])
                        diagnostics['three_group_covers'] += result['three_touching_group_covers']
                        diagnostics['three_group_determining_bonds'] += len(result['determining_three_touching_bonds'])
                        largest['candidate_group_count'] = max(largest['candidate_group_count'], result['candidate_groups'])
                        largest['survivor_group_count'] = max(largest['survivor_group_count'], len(result['surviving_groups']))
            stage.solver.delete()
            total.update(diagnostics)
            total['stage_distinct_function_queries'] += len(memo)
            timings.append({'start': row['start'], 'round': row['round'], 'raw_distinctions': stage.n,
                            'seconds': round(perf_counter() - start_time, 3)})
    rec = {'mode': tag, 'stages': len(stages), 'counts': total, 'largest': largest,
           'seconds': round(perf_counter() - begin, 3), 'peak_resident_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
           'stage_times': timings if ns.pilot else sorted(timings, key=lambda x: x['seconds'], reverse=True)[:6]}
    (HERE / f'other_bonds_determination_{tag}.json').write_text(json.dumps(rec, indent=2) + '\n')
    print(json.dumps(rec, separators=(',', ':')))


if __name__ == '__main__':
    main()
