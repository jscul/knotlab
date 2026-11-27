"""Check disjoint stage bonds which omit a carried upper function's named carrier.

Raw sets are encoded by bit masks. All negative decisions about existence use
the full stage or an explicit allowed witness. The finite pool of allowed
assignments only accelerates witness discovery.
"""

import argparse
import gzip
import json
import math
import random
import resource
import time
from collections import Counter
from functools import cache
from itertools import combinations, combinations_with_replacement
from pathlib import Path

from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
PATTERN = ((3, 4, 5), (11, 12, 13), (0, 1, 10), (6, 15, 16), (7, 8, 9), (2, 14))


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit
        mask ^= bit


def encode(items):
    return sum(1 << x for x in items)


def subsets(mask, size):
    return (sum(c) for c in combinations(bits(mask), size))


def carried_pairs(supports, chain):
    raw = [set(supports[i]) for i in chain]
    shared = [next(iter(a & b)) for a, b in zip(raw, raw[1:])]
    assert len(shared) == len(set(shared)) == 7
    raw_order = sorted(raw[0] - {shared[0]})
    for j in range(1, 7):
        raw_order.append(shared[j - 1])
        own, = raw[j] - {shared[j - 1], shared[j]}
        raw_order.append(own)
    raw_order.append(shared[-1])
    raw_order.extend(sorted(raw[-1] - {shared[-1]}))
    assert len(raw_order) == len(set(raw_order)) == 17
    readings = [encode(raw_order[i] for i in positions) for positions in PATTERN]
    return tuple(zip(readings[::2], readings[1::2]))


def pairs_free(image):
    return all({w & pair for w in range(8) if image & (1 << w)} ==
               {w & pair for w in range(8)} for pair in (3, 5, 6))


def cells(columns, universe):
    values = [universe]
    for col in columns:
        values = [value & ~col for value in values] + [value & col for value in values]
    return values


@cache
def covers_count(n, x_size, y_size):
    named = x_size + y_size
    total = 0
    for arities in combinations_with_replacement((2, 3), 3):
        used = sum(arities)
        if used < named or used > n:
            continue
        multiplicities = Counter(arities)
        ways = math.factorial(used)
        for v in (*arities, *multiplicities.values()):
            ways //= math.factorial(v)
        total += ways * math.comb(n - named, used - named)
    return total - sum(math.comb(n - named, k) for k in (2, 3))


class Copies:
    """Two complete stage assignments, independently extendible on request."""

    def __init__(self, n, laws):
        self.n = n
        self.top = 2 * n
        self.solver = Solver()
        self.solver.add_clause([1])  # All tests are invariant under joint complementation.
        self.agreements = {}
        self.same_agreements = {}
        self.uppers = {}
        self.raw_equal = {}
        for offset in (0, n):
            for law in laws:
                clause = [b.bit_length() + offset for b in bits(law)]
                self.solver.add_clause(clause)
                self.solver.add_clause([-v for v in clause])
        for i in range(n):
            self.raw_equal[1 << i] = self.same_when_requested(i + 1, n + i + 1)

    def fresh(self):
        self.top += 1
        return self.top

    def same_when_requested(self, a, b):
        condition = self.fresh()
        self.solver.add_clause([-condition, -a, b])
        self.solver.add_clause([-condition, a, -b])
        return condition

    def agreement(self, carrier, copy):
        key = carrier, copy
        if key not in self.agreements:
            var = self.fresh()
            xs = [b.bit_length() + self.n * copy for b in bits(carrier)]
            for a, b in zip(xs, xs[1:]):
                self.solver.add_clause([-var, a, -b])
                self.solver.add_clause([-var, -a, b])
            self.solver.add_clause([var] + xs)
            self.solver.add_clause([var] + [-x for x in xs])
            self.agreements[key] = var
        return self.agreements[key]

    def same(self, carrier):
        if carrier not in self.same_agreements:
            self.same_agreements[carrier] = self.same_when_requested(
                self.agreement(carrier, 0), self.agreement(carrier, 1))
        return self.same_agreements[carrier]

    def upper(self, a, b, both, copy):
        key = a, b, both, copy
        if key not in self.uppers:
            x, y = self.agreement(a, copy), self.agreement(b, copy)
            var = self.fresh()
            # Use one conjunction encoding; De Morgan gives 'either'.
            u, v, w = (x, y, var) if both else (-x, -y, -var)
            self.solver.add_clause([-w, u])
            self.solver.add_clause([-w, v])
            self.solver.add_clause([w, -u, -v])
            self.uppers[key] = var
        return self.uppers[key]


class FreeBit:
    """A single assignment on which a fixed raw distinction can be changed."""

    def __init__(self, stage, d):
        self.laws = [law & ~d for law in stage.laws]
        self.solver = Solver()
        self.top = stage.n
        self.agreements = {}
        self.guards = {}
        self.impossible = 0
        self.solver.add_clause([1])
        for law in self.laws:
            self.nae(law)
        for e in bits(stage.raw ^ d):
            if any(law.bit_count() <= 2 and law & e for law in self.laws):
                self.impossible |= e
                continue
            self.top += 1
            self.guards[e] = self.top
            for law in self.laws:
                if law & e:
                    self.nae(law ^ e, [-self.top])
        self.n = stage.n

    def nae(self, law, extra=()):
        raw = [v.bit_length() for v in bits(law)]
        self.solver.add_clause(list(extra) + raw)
        self.solver.add_clause(list(extra) + [-v for v in raw])

    def equality(self, carrier):
        if carrier not in self.agreements:
            self.top += 1
            z = self.top
            places = [v.bit_length() for v in bits(carrier)]
            self.solver.add_clause([z] + places)
            self.solver.add_clause([z] + [-v for v in places])
            for a, b in zip(places, places[1:]):
                self.solver.add_clause([-z, a, -b])
                self.solver.add_clause([-z, -a, b])
            self.agreements[carrier] = z
        return self.agreements[carrier]

    def unresolved(self, pool_failed, same_group, other_group, both):
        pending = pool_failed & ~self.impossible
        rejected = pool_failed & self.impossible
        if not pending:
            return rejected
        other = self.equality(other_group)
        assumptions = [other if both else -other]
        if same_group.bit_count() > 1:
            assumptions.append(self.equality(same_group))
        while pending:
            e = pending & -pending
            if not self.solver.solve(assumptions=assumptions + [self.guards[e]]):
                rejected |= e
                pending ^= e
                continue
            model = self.solver.get_model()[:self.n]
            witness = sum(1 << (v - 1) for v in model if v > 0)
            blocked = 0
            for law in self.laws:
                ones = witness & law
                zeros = law ^ ones
                if ones.bit_count() == 1:
                    blocked |= ones
                if zeros.bit_count() == 1:
                    blocked |= zeros
            assert not blocked & e
            pending &= blocked
        return rejected


class Stage:
    def __init__(self, supports, n_samples=192):
        self.laws = tuple(map(encode, supports))
        self.n = max(self.laws).bit_length()
        self.raw = (1 << self.n) - 1
        self.support = {b: tuple(s for s in self.laws if b & s) for b in bits(self.raw)}
        assert all(self.support.values())
        self.sat = Copies(self.n, self.laws)
        self.law_literals = [[self.sat.raw_equal[b] for b in bits(s)] for s in self.laws]
        self.eligible_carrier = {}
        self.eligible_triples = {}
        self.queries = {}
        self.free_bit = {}
        self.contained = {c for support in self.laws for n in (2, 3) for c in subsets(support, n)}
        # A finite pool is a source of positive extension witnesses. A missing
        # image or witness in the pool never decides an existence claim.
        raw_examples = self.witness_pool(n_samples)
        self.pool = (1 << len(raw_examples)) - 1
        self.columns = {b: sum(1 << j for j, word in enumerate(raw_examples) if word & b)
                        for b in bits(self.raw)}
        self.agree_after = cache(self.agree_after)
        self.valid_after = cache(self.valid_after)
        self.outside_equal = cache(self.outside_equal)
        self.single_changes = {b: self.valid_after(b) for b in bits(self.raw)}

    def close(self):
        self.sat.solver.delete()
        for f in self.free_bit.values():
            f.solver.delete()
        for method in (self.agree_after, self.valid_after, self.outside_equal):
            method.cache_clear()

    def witness_pool(self, count):
        rng = random.Random(69473)
        words = []
        source_bits = {law: tuple(bits(law)) for law in self.laws}
        while len(words) < count:
            word = rng.getrandbits(self.n)
            for _ in range(400):
                failed = next((s for s in self.laws if word & s in (0, s)), None)
                if failed is None:
                    words.append(word)
                    break
                word ^= rng.choice(source_bits[failed])
        return words

    def agree_after(self, carrier, flipped):
        comp, zeros, ones = self.pool, self.pool, self.pool
        for bit in bits(carrier):
            col = self.columns[bit]
            if bit & flipped:
                col ^= comp
            zeros &= ~col
            ones &= col
        return zeros | ones

    def valid_after(self, flipped):
        valid = self.pool
        touched = set().union(*(self.support[d] for d in bits(flipped)))
        for law in touched:
            changed = flipped & law
            if law != changed:
                valid &= ~self.agree_after(law, changed)
        return valid

    def outside_equal(self, carrier):
        return [self.sat.raw_equal[d] for d in bits(self.raw ^ carrier)]

    def nonlocal_carrier(self, carrier):
        if carrier not in self.eligible_carrier:
            if carrier in self.contained:
                self.eligible_carrier[carrier] = False
            else:
                # Existence of two allowed states which agree on a source law
                # and disagree on this one lower reading.
                target = [self.sat.agreement(carrier, 0), -self.sat.agreement(carrier, 1)]
                self.eligible_carrier[carrier] = all(
                    self.sat.solver.solve(assumptions=target + equal) for equal in self.law_literals)
        return self.eligible_carrier[carrier]

    def bond(self, triple):
        if triple in self.eligible_triples:
            return self.eligible_triples[triple]
        values = cells([self.agree_after(c, 0) for c in triple], self.pool)
        valid = False
        if not all(values):
            image = sum(1 << w for w, possible in enumerate(values) if possible)
            lits = [self.sat.agreement(c, 0) for c in triple]
            for w, possible in enumerate(values):
                if not possible and self.sat.solver.solve(assumptions=[
                        a if w & (1 << j) else -a for j, a in enumerate(lits)]):
                    image |= 1 << w
            valid = (0 < image < 255 and pairs_free(image)
                     and all(self.nonlocal_carrier(c) for c in triple))
        self.eligible_triples[triple] = valid
        return valid

    def consider(self, a, b, both):
        key = min(a, b), max(a, b), both
        if key not in self.queries:
            self.queries[key] = Query(self, *key).run()
        return self.queries[key]


class Query:
    def __init__(self, stage, a, b, both):
        self.s = stage
        self.a, self.b, self.both = a, b, both
        self.named = a | b
        assert not a & b
        self.pool_upper = self.upper_words(0)
        self.difference = {0: 0}
        self.sensitive = {}
        self.opposite = None

    def upper_words(self, flip):
        left = self.s.agree_after(self.a, flip & self.a)
        right = self.s.agree_after(self.b, flip & self.b)
        return left & right if self.both else left | right

    def changed(self, flip):
        named_flip = flip & self.named
        if named_flip not in self.difference:
            self.difference[named_flip] = self.pool_upper ^ self.upper_words(named_flip)
        return self.difference[named_flip]

    def opposite_values(self):
        if self.opposite is None:
            self.opposite = [self.s.sat.upper(self.a, self.b, self.both, 0),
                             -self.s.sat.upper(self.a, self.b, self.both, 1)]
        return self.opposite

    def outside_options(self):
        options = {}
        for d in bits(self.named):
            changes = self.s.single_changes[d] & self.changed(d)
            if not changes:
                # A positive instance here gives two states equal off d. The
                # reduction only runs when every named distinction is required.
                if not self.s.sat.solver.solve(assumptions=
                        self.opposite_values() + self.s.outside_equal(d)):
                    raise ValueError(('No single-distinction witness', self.a, self.b, self.both, d))
            self.sensitive[d] = changes
            unresolved = 0
            for e in bits(self.s.raw ^ self.named):
                # These are whole-stage witnesses for all four values of d,e
                # with identical remaining bits. Since e is outside the named
                # pair, e cannot change the upper value on either d-slice.
                if not (changes & self.s.single_changes[e] & self.s.valid_after(d | e)):
                    unresolved |= e
            if unresolved:
                if d not in self.s.free_bit:
                    self.s.free_bit[d] = FreeBit(self.s, d)
                group, other = (self.a, self.b) if self.a & d else (self.b, self.a)
                unresolved = self.s.free_bit[d].unresolved(unresolved, group ^ d, other, self.both)
            options[d] = unresolved
        return options

    def compatible(self, carrier):
        if carrier in (self.a, self.b):
            return True
        if carrier in self.s.contained:
            return False
        local_upper = self.changed(carrier)
        if local_upper & self.s.valid_after(carrier):
            return False  # Complementing a whole carrier always preserves its agreement.
        if carrier.bit_count() == 3:
            for d in bits(carrier & self.named):
                if self.sensitive[d] & ~self.s.agree_after(carrier ^ d, 0):
                    return False
            for pair in subsets(carrier, 2):
                if (self.changed(pair) & self.s.valid_after(pair) & ~self.s.agree_after(pair, 0)):
                    return False
        # Same raw bits outside this carrier, same lower reading here,
        # opposite upper values. This pair excludes the carrier from every
        # determining triple of disjoint carriers.
        conditions = self.opposite_values() + [self.s.sat.same(carrier)] + self.s.outside_equal(carrier)
        return not self.s.sat.solver.solve(assumptions=conditions)

    def possible_carriers(self):
        outside = self.outside_options()
        answer = []
        for inside_count in (1, 2, 3):
            for inside in subsets(self.named, inside_count):
                remaining = self.s.raw ^ self.named
                for d in bits(inside):
                    remaining &= outside[d]
                for arity in (2, 3):
                    if arity < inside_count:
                        continue
                    for rest in subsets(remaining, arity - inside_count):
                        c = inside | rest
                        if self.compatible(c):
                            answer.append(c)
        return answer

    def candidate_triples(self, carriers):
        by_raw = {d: [c for c in carriers if c & d] for d in bits(self.named)}

        def visit(chosen, used, needed):
            if not needed:
                if len(chosen) == 3:
                    yield 3, tuple(sorted(chosen))
                elif len(chosen) == 2 and set(chosen) != {self.a, self.b}:
                    available = self.s.raw ^ used
                    for arity in (2, 3):
                        for third in subsets(available, arity):
                            yield 2, tuple(sorted((*chosen, third)))
                return
            if len(chosen) == 3:
                return
            d = needed & -needed
            for c in by_raw[d]:
                if not used & c:
                    yield from visit((*chosen, c), used | c, needed & ~c)

        return visit((), 0, self.named)

    def determines(self, triple):
        for part in cells([self.s.agree_after(c, 0) for c in triple], self.s.pool):
            if part & self.pool_upper and part & ~self.pool_upper:
                return False
        constraints = self.opposite_values() + [self.s.sat.same(c) for c in triple]
        return not self.s.sat.solver.solve(assumptions=constraints)

    def run(self):
        carriers = self.possible_carriers()
        counts = Counter()
        counts['all_disjoint_nonpaired_covers'] = covers_count(
            self.s.n, self.a.bit_count(), self.b.bit_count())
        counts['single_distinctions_witnessed'] = self.named.bit_count()
        hits = []
        for touching, triple in self.candidate_triples(carriers):
            counts['tested_' + str(touching)] += 1
            if self.s.bond(triple):
                counts['eligible_' + str(touching)] += 1
                if self.determines(triple):
                    counts['determining_' + str(touching)] += 1
                    hits.append(triple)
        return counts, tuple(hits)


def process_stage(row, dest, totals, prefix_totals):
    # A cut can leave gaps in the raw names retained from an ordinary growth
    # proposal. Remove the gaps while preserving each support's order.
    names = sorted({v for support in row['supports'] for v in support})
    positions = {v: j for j, v in enumerate(names)}
    supports = [tuple(positions[v] for v in law) for law in row['supports']]
    stage = Stage(supports)
    try:
        for j, chain in enumerate(row['chains']):
            hit_counts = []
            tested = []
            eligible = []
            detailed = []
            for pair in carried_pairs(supports, chain):
                for both in (True, False):
                    counts, hits = stage.consider(*pair, both)
                    totals.update(counts)
                    if j < 3:
                        prefix_totals.update(counts)
                    hit_counts.append(len(hits))
                    tested.append([counts['tested_2'], counts['tested_3']])
                    eligible.append([counts['eligible_2'], counts['eligible_3']])
                    if hits:
                        raw_hits = [[encode(names[d.bit_length() - 1] for d in bits(c)) for c in triple]
                                    for triple in hits]
                        detailed.append([len(hit_counts) - 1, raw_hits])
            record = {'stage': row['id'], 'chain_index': j, 'determiners': hit_counts,
                      'tested_by_cover_size': tested, 'eligible_by_cover_size': eligible}
            if detailed:
                record['determining_carrier_masks'] = detailed
            dest.write(json.dumps(record, separators=(',', ':')) + '\n')
        totals['distinct_stage_functions'] += len(stage.queries)
        totals['distinct_residual_lower_triples'] += len(stage.eligible_triples)
        totals['distinct_eligible_residual_lower_bonds'] += sum(stage.eligible_triples.values())
    finally:
        stage.close()


def run(selected, prefix):
    t = time.monotonic()
    totals, prefix_totals = Counter(), Counter()
    times = []
    with gzip.open(HERE / (prefix + '_rows.jsonl.gz'), 'wt', compresslevel=3) as dest:
        for row in selected:
            begin = time.monotonic()
            process_stage(row, dest, totals, prefix_totals)
            times.append([row['id'], len(row['chains']), round(time.monotonic() - begin, 4)])
    for counts in (totals, prefix_totals):
        for name in ('tested', 'eligible', 'determining'):
            for size in (2, 3):
                counts.setdefault(f'{name}_{size}', 0)
    results = {'stages': len(times), 'chain_occurrences': sum(t[1] for t in times),
               'first_three_occurrences': sum(min(3, t[1]) for t in times),
               'pool_witnesses_per_stage': 192, 'pool_seed': 69473,
               'by_upper_function_occurrence': dict(totals), 'first_three_by_upper_function_occurrence': dict(prefix_totals),
               'stage_seconds': times, 'seconds': round(time.monotonic() - t, 4),
               'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    (HERE / (prefix + '.json')).write_text(json.dumps(results, indent=2) + '\n')
    print(json.dumps({k: v for k, v in results.items() if k != 'stage_seconds'}), flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pilot', action='store_true')
    ap.add_argument('--ids', help='Stage IDs separated by commas; reads the full input.')
    ap.add_argument('--output-prefix')
    args = ap.parse_args()
    path = HERE / ('step_stages_pilot.jsonl.gz' if args.pilot else 'step_stages.jsonl.gz')
    ids = set(map(int, args.ids.split(','))) if args.ids else None
    prefix = args.output_prefix or ('step_nonpaired_pilot' if args.pilot else 'step_nonpaired')
    with gzip.open(path, 'rt') as source:
        rows = (json.loads(line) for line in source)
        run((r for r in rows if ids is None or r['id'] in ids), prefix)


if __name__ == '__main__':
    main()
