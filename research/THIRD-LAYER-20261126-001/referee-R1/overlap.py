"""Check overlapping parity knots using supports in two connected, perpetually funded starts.

The four outer five-knot rings each have two loose distinctions per knot. Each
ring attaches by two separate three-knot strings to alternate knots of one
central ring of four. Its four shared distinctions have parity X. The sums of
the left and right starting laws give A+B+X and C+D+X. The four outer parities
also have the lone family relation A+B+C+D. All five retain different carriers.

The live candidate relation of each outer ring is a five-cycle. Its five
two-parent births use the two loose places of every parent, and have two fresh
distinctions each: the next candidate pairs are consecutive pairs of births
through the old parents. There is no cross-ring candidate. This repeats. For
any nontrivial sum of family parities, an odd flip uses at least two distinctions
of every subsequent generation: each generation reproduces each family's old
parity by summing its birth laws, and all families together have even parity.
A shortest starting flip is one path between opposite families closed using a
loose distinction at each end. Extend those loose ends independently through a
child, choosing one of its fresh distinctions. The minimum is exactly p + 2t.

Two further readings use seven or thirteen of the same outer rings in one
cycle. The selected facts and second-layer knots are choices. Both checks
include every tied shortest change and test a different roster of knots.
"""

import argparse
import itertools
import json
import resource
import sys
from collections import Counter, defaultdict, deque
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from time import monotonic

import growth

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))
from knotlab.cli import main as knot_check


class Start:
    def __init__(self, count):
        self.knots = []
        self.next_distinction = 0
        self.rings = [tuple(self.knot() for _ in range(5)) for _ in range(count)]
        self.loose = []
        for ring in self.rings:
            for i, k in enumerate(ring):
                self.share(k, ring[(i + 1) % 5])
            self.loose.append(tuple(self.share(k) for k in ring for _ in range(2)))

    def knot(self):
        self.knots.append([])
        return len(self.knots) - 1

    def share(self, *holders):
        d = self.next_distinction
        self.next_distinction += 1
        for k in holders:
            self.knots[k].append(d)
        return d

    def double(self, first, second):
        self.share(first, second)
        self.share(first, second)

    def supports(self):
        return tuple(tuple(row) for row in self.knots)


def central_start():
    start = Start(4)
    center = [start.knot() for _ in range(4)]
    middle = [start.share(k, center[(j + 1) % 4]) for j, k in enumerate(center)]
    preparations = [set(ring) for ring in start.rings] + [set(center)]
    left = {center[0], center[2]}
    for i, ring in enumerate(start.rings):
        if i < 2:
            left.update(ring)
        for p in range(2):
            outer, inner, last = [start.knot() for _ in range(3)]
            for z in (p, p + 2):
                start.share(ring[z], outer)
            start.double(outer, inner)
            start.double(inner, last)
            start.double(last, center[2 * p + i // 2])
            preparations[i].add(outer)
            preparations[-1].update((inner, last))
            if i < 2:
                left.update((outer, inner, last))
    return start, middle, center, preparations, left


def circular_start(count):
    start = Start(count)
    for i, ring in enumerate(start.rings):
        a, b = start.knot(), start.knot()
        for p in (0, 2):
            start.share(a, ring[p])
            start.share(b, start.rings[(i + 1) % count][p + 1])
        start.double(a, b)
    return start


def mask(xs):
    number = 0
    for x in xs:
        number ^= 1 << x
    return number


def positions(value):
    while value:
        bit = value & -value
        yield bit.bit_length() - 1
        value ^= bit


def parity_word(value, places):
    return sum(((value >> p) & 1) << i for i, p in enumerate(places))


def words(values, size):
    return sorted("".join(str((v >> k) & 1) for k in range(size)) for v in values)


def insert(basis, item):
    while item:
        p = item.bit_length()
        if p not in basis:
            basis[p] = item
            return
        item ^= basis[p]


def span(vectors):
    values = {0}
    basis = {}
    for v in vectors:
        insert(basis, v)
    for v in basis.values():
        values.update(x ^ v for x in tuple(values))
    return values


class Changes:
    """Even changes are sums of closed trails, joining loose ends at one extra holder."""

    def __init__(self, stage, removed_laws=()):
        self.count = len(stage)
        holders = defaultdict(list)
        for k, row in enumerate(stage):
            for d in row:
                owners = holders[d]
                if k not in removed_laws:
                    owners.append(k)
        self.ends = {d: tuple(h + [self.count] * (2 - len(h))) for d, h in holders.items()}
        self.neighbors = [[] for _ in range(self.count + 1)]
        for d, (a, b) in self.ends.items():
            self.neighbors[a].append((b, d))
            self.neighbors[b].append((a, d))

    def image(self, supports, fixed=()):
        """Sums around a spanning forest's closed trails generate all the readings."""
        return span(self.image_basis(supports, fixed).values())

    def image_basis(self, supports, fixed=()):
        tags = defaultdict(int)
        for k, support in enumerate(supports):
            for d in support:
                tags[d] ^= 1 << k
        avoided = set(fixed)
        values = {}
        result = {}
        for origin in range(self.count + 1):
            if origin in avoided or origin in values:
                continue
            values[origin] = 0
            pending = [origin]
            while pending:
                v = pending.pop()
                for u, d in self.neighbors[v]:
                    if u in avoided:
                        continue
                    through = values[v] ^ tags[d]
                    if u in values:
                        insert(result, values[u] ^ through)
                    else:
                        values[u] = through
                        pending.append(u)
        return result

    def detour(self, a, b, *, excluded_edge=None, excluded_knot=None, signed=None):
        """Least walk after a deletion, with even parity when a sign is supplied."""
        marked = set() if signed is None else signed
        queue = deque([(a, 0, 0)])
        seen = {(a, 0)}
        while queue:
            v, s, n = queue.popleft()
            if v == b and s == 0:
                return n
            for u, d in self.neighbors[v]:
                if d == excluded_edge or u == excluded_knot:
                    continue
                other = s ^ (d in marked)
                if (u, other) not in seen:
                    seen.add((u, other))
                    queue.append((u, other, n + 1))
        return None

    def least_flip(self, support):
        signed = set(support)
        lengths = []
        for d in signed:
            a, b = self.ends[d]
            n = self.detour(a, b, excluded_edge=d, signed=signed)
            if n is not None:
                lengths.append(n + 1)
        return min(lengths, default=None)

    def shortest_max(self):
        lengths = []
        for d, (a, b) in self.ends.items():
            n = self.detour(a, b, excluded_edge=d)
            assert n is not None
            lengths.append(n + 1)
        return max(lengths)

    def local_bound(self, stage):
        """Sufficient size for every even local change to be spanned at any one knot.

        A pair of incident distinctions can change without changing any other
        distinction at that holder iff their other ends can be joined with the
        holder deleted. A connected selection of these pairs spans even changes.
        """
        bounds = []
        for v, row in enumerate(stage):
            end = {d: next(u for u in self.ends[d] if u != v) for d in row}
            pairs = []
            for a, b in itertools.combinations(row, 2):
                n = self.detour(end[a], end[b], excluded_knot=v)
                if n is not None:
                    pairs.append((n + 2, a, b))
            basis = {}
            for length, a, b in sorted(pairs):
                insert(basis, (1 << a) ^ (1 << b))
                if len(basis) == len(row) - 1:
                    bounds.append(length)
                    break
            else:
                raise ValueError("a knot's even local changes did not span")
        return Counter(bounds)


def canonical(image, arity):
    """Pass the actual projected states to the canonical knot check."""
    names = [f"x{k}" for k in range(arity)]
    excluded = set(range(1 << arity)) - image
    if not excluded:
        return {"allowed": words(image, arity), "is_knot": False, "free": True}
    clauses = [" ".join(("~" if v >> k & 1 else "") + x for k, x in enumerate(names))
               for v in sorted(excluded)]
    out = StringIO()
    with redirect_stdout(out):
        assert knot_check(["check", "--cnf", "; ".join(clauses), "--loops", *names[:-1],
                           "--contact", names[-1], "--json"]) == 0
    answer = json.loads(out.getvalue())
    assert set(answer["allowed"]) == set(words(image, arity))
    return {k: answer[k] for k in ("allowed", "binding", "loss_on_erasure", "coexistence", "is_knot")}


def grown_stages(start, max_round):
    stage = start.supports()
    family_at = {k: i for i, ring in enumerate(start.rings) for k in ring}
    gen = [tuple(start.loose)]
    expected = tuple(tuple(r) for r in start.rings)
    assert growth.families(stage) == (expected, tuple(start.loose))
    for t in range(max_round + 1):
        if t:
            stage, status, births = growth.grow(stage)
            assert status == "funded" and len(births) == 5 * len(start.rings)
            new = [[] for _ in start.rings]
            count = Counter()
            for b in births:
                assert b["p"] == b["f"] == b["D"] == 2 and not b["old_inputs_already_imply_law"]
                families = {family_at[p] for p in b["parents"]}
                assert len(families) == 1
                i = families.pop()
                family_at[b["knot"]] = i
                count[i] += 1
                new[i].extend(b["fresh"])
            assert set(count.values()) == {5} and len(count) == len(start.rings)
            gen.append(tuple(tuple(g) for g in new))
        yield t, stage, family_at, gen


def is_cycle(changes, support):
    links = defaultdict(list)
    for d in support:
        a, b = changes.ends[d]
        if changes.count in (a, b):
            return False
        links[a].append(b)
        links[b].append(a)
    visited = set()
    pending = [next(iter(links))]
    while pending:
        k = pending.pop()
        if k not in visited:
            visited.add(k)
            pending.extend(links[k])
    return len(visited) == len(links) and all(len(row) == 2 for row in links.values())


def central_check(max_round):
    start, shared, center, preparations, left = central_start()
    source = start.supports()
    other = set(range(len(source))) - left
    facts = [*start.loose, shared]
    assert len(set.union(*(set(s) for s in facts))) == sum(map(len, facts))
    for side, ring_ids in ((left, (0, 1)), (other, (2, 3))):
        support = set(shared)
        for i in ring_ids:
            support ^= set(facts[i])
        for k in side:
            support ^= set(source[k])
        assert not support
    answer = {
        "fact order": ["A", "B", "C", "D", "X"],
        "physical carriers": facts,
        "source knots": source,
        "source law sets for A+B+X and C+D+X": [sorted(left), sorted(other)],
        "rounds": [],
    }
    first_minimum = None
    expected = {v for v in range(32) if (v & 19).bit_count() % 2 == (v & 28).bit_count() % 2 == 0}
    for t, stage, family_at, _ in grown_stages(start, max_round):
        ch = Changes(stage)
        minima = [ch.least_flip(g) for g in facts]
        if first_minimum is None:
            first_minimum = minima
        assert minima == [p + 2 * t for p in first_minimum]
        shortest_max = ch.shortest_max()
        assert ch.image(facts) == expected
        row = {"round": t, "knots": len(stage), "distinctions": len(ch.ends), "least flips": minima,
               "largest shortest change through one distinction": shortest_max,
               "five single cycles in fact order": [is_cycle(ch, s) for s in facts],
               "five invariant at the fixed scale eleven": [n > 11 for n in minima]}
        assert row["five single cycles in fact order"] == [t > 0] * 4 + [True]
        if t in (0, 1, max_round):
            local_bound = ch.local_bound(stage)
            row["least sufficient scales from changes on incident pairs"] = dict(sorted(local_bound.items()))
            row["nonconstant local class parities at scale eleven"] = 0 if max(local_bound) <= 11 else None
            row["knots fixed separately, retaining all eight tuples"] = sum(
                ch.image(facts, fixed=(k,)) == expected for k in range(len(stage)))
            assert row["knots fixed separately, retaining all eight tuples"] == len(stage)
        answer["rounds"].append(row)
    image = ch.image(facts)
    assert all(is_cycle(ch, g) for g in facts)
    assert all(len(ch.image([[d] for d in g])) == 1 << len(g) for g in facts)
    answer["joint states"] = words(image, 5)
    answer["five disjoint single cycles"] = [len(g) for g in facts]
    answer["isolated carrier projections"] = [len(ch.image([[d] for d in g])) for g in facts]
    answer["two ternary projections and one canonical quartet"] = [
        canonical({parity_word(v, ix) for v in image}, len(ix))
        for ix in ((0, 1, 4), (2, 3, 4), (0, 1, 2, 3))]
    for k, i in family_at.items():
        preparations[i].add(k)
    assert set.union(*preparations) == set(range(len(stage)))
    assert sum(map(len, preparations)) == len(stage)
    parts = []
    for g, keep in zip(facts, preparations, strict=True):
        prep = Changes([stage[k] for k in sorted(keep)])
        least = prep.least_flip(g)
        assert prep.image([g]) == {0, 1}
        fixed_count = sum(len(prep.image([g], (k,))) == 2 for k in range(prep.count))
        parts.append({"holders retained": sorted(keep), "least isolated flip": least,
                      "knots individually fixed leaving both values": fixed_count,
                      "knots": prep.count, "both values": True})
        assert fixed_count == prep.count
    answer["five disjoint preparations at final round"] = parts
    answer["free tuple count when prepared separately"] = 2 ** len(parts)
    answer["preparation operation"] = ("Take the five displayed disjoint sets of holders. In each retain its "
        "knots and distinctions. A distinction held across two preparations gives a free loose end to each "
        "when they are prepared separately. Each fact stays open, invariant at scale five at round eight, "
        "and unread by any one of its own holders.")
    control = {}
    for which in ((center[0],), (center[1],), (center[0], center[1])):
        occupied = Changes(stage, removed_laws=which).image(facts)
        control[str(which)] = {"joint tuples": len(occupied), "left triple": len({parity_word(v, (0, 1, 4)) for v in occupied}),
                               "right triple": len({parity_word(v, (2, 3, 4)) for v in occupied})}
    assert [r["joint tuples"] for r in control.values()] == [16, 16, 32]
    answer["removing a left, a right, or both central laws"] = control
    # Within the canonical quartet, shortest changes are every pair. In each
    # of the two triples the size-two changes and the four through X span all.
    small = set()
    for i in range(5):
        through = {v for v in expected if v >> i & 1}
        small.update(v for v in through if v.bit_count() == min(x.bit_count() for x in through))
    answer["shortest-change reading on the five facts"] = {
        "changes": words(small, 5), "span size": len(span(small)), "third class bits": 3 - (len(span(small)).bit_length() - 1)}
    return answer


def separately_carry(recipes, gen):
    """Different occurrences of a ring use different, equivalent generations."""
    occurrences = Counter(i for v in recipes for i in positions(v))
    limit = max(occurrences.values()) - 1
    assert len(gen) > limit
    allocated = Counter()
    carriers = []
    recipe_holders = []
    for s in recipes:
        support, assigned = [], []
        for i in positions(s):
            age = allocated[i]
            support.extend(gen[age][i])
            assigned.append([i, age])
            allocated[i] += 1
        carriers.append(support)
        recipe_holders.append(assigned)
    assert len(set.union(*(set(s) for s in carriers))) == sum(map(len, carriers))
    return carriers, recipe_holders, limit


def whole_ring_holders(start, family_at, i):
    count = len(start.rings)
    # The two outer attachment knots meet ring i only. The last connector of
    # the preceding link and the first of the next are its two half-links.
    return [k for k, family in family_at.items() if family == i] + [
        5 * count + 2 * i, 5 * count + 2 * ((i - 1) % count) + 1]


def circular_read(max_round):
    start = circular_start(7)
    g = mask((0, 1, 5))
    t = [1 << i for i in range(5)]
    b = [v ^ g for v in t]
    r = [v ^ t[(i - 1) % 5] for i, v in enumerate(t)]
    recipes = t + b + r
    assert len(set(recipes)) == 15 and len(set(recipes + [g])) == 16
    for stage_round, stage, family_at, gen in grown_stages(start, max_round):
        pass
    assert stage_round == max_round
    carriers, recipe_holders, limit = separately_carry(recipes, gen)
    ch = Changes(stage)
    image = ch.image(carriers)
    expected = {sum(((s & v).bit_count() % 2) << j for j, s in enumerate(recipes)) for v in range(64)}
    assert image == expected and len(image) == 64
    quartet = (0, 5, 1, 6)
    stars = [(j, (j - 1) % 5, j + 10) for j in range(5)] + [
        (j + 5, (j - 1) % 5 + 5, j + 10) for j in range(5)]
    reports = [canonical({parity_word(v, indices) for v in image}, 3) for indices in stars]
    both_g = {v: ((v >> 0) ^ (v >> 5)) & 1 for v in image}
    ranks_after_fixing = [len({both_g[v] for v in image if parity_word(v, star) == 0}) for star in stars]
    assert all(report["is_knot"] for report in reports) and set(ranks_after_fixing) == {2}
    other = canonical({parity_word(v, quartet) for v in image}, 4)
    assert other["is_knot"] and len({both_g[v] for v in image if parity_word(v, quartet) == 0}) == 1
    small = set()
    for j in range(15):
        through = {v for v in image if v >> j & 1}
        least = min(x.bit_count() for x in through)
        small.update(v for v in through if v.bit_count() == least)
    basis = span(small)
    assert len(small) == 5 and len(basis) == 32 and all(both_g[v] == 0 for v in basis)
    source_g = [d for i in positions(g) for d in start.loose[i]]
    local = [len(ch.image([source_g], fixed=whole_ring_holders(start, family_at, i))) for i in range(7)]
    before = Changes(start.supports())
    base_flips = [before.least_flip([d for i in positions(v) for d in start.loose[i]]) for v in recipes + [g]]
    flips = [ch.least_flip(f) for f in carriers + [source_g]]
    assert flips == [p + 2 * max_round for p in base_flips]
    assert set(local) == {2}
    assert all(ch.image(carriers, (k,)) == expected for k in range(len(stage)))
    return {"round": max_round, "knots": len(stage), "distinctions": len(ch.ends),
            "seven starting ring facts with their sole joint parity": "F0 F1 F2 F3 F4 F5 F6",
            "g": "F0+F1+F5", "fact order": "t0,...,t4,b0,...,b4,r0,...,r4",
            "fifteen source masks": recipes, "carriers as [ring,generation] pairs": recipe_holders,
            "largest carrier generation": limit,
            "disjoint carrier sizes": list(map(len, carriers)),
            "least starting flips for fifteen facts and g": base_flips,
            "least grown flips for same functions": flips,
            "largest shortest change through an underlying distinction": ch.shortest_max(),
            "least sufficient scales from changes on incident pairs": dict(sorted(ch.local_bound(stage).items())),
            "joint states": words(image, 15), "knots individually fixed leaving all 64 states": len(stage),
            "whole rings including their births and their two attachment knots fixed separately, number of g values": local,
            "ten chosen triples": stars, "canonical ternary test": reports[0],
            "chosen triples passing": sum(x["is_knot"] for x in reports),
            "number of g values with each chosen triple zero": ranks_after_fixing,
            "shortest layer-two changes": words(small, 15), "their span size": len(basis),
            "least layer-two change flipping g": min(v.bit_count() for v in image if both_g[v]),
            "extra four-fact knot": quartet, "extra four-fact knot check": other,
            "g values with the extra knot zero": 1}


def two_joined_readings(max_round):
    """Two copies of the previous second-layer pattern share one distinction and its holders."""
    start = circular_start(13)
    g = [mask((0, 1, 5)), mask((6, 7, 11))]
    recipes = []
    names = []
    holders = defaultdict(list)
    copy_index = {}

    def holder(copy, bank, place):
        # Both ends of the shared distinction are the same holders in the two copies.
        return (0 if place == 0 else copy, bank, place)

    def new_distinction(copy, kind, place, a, b, value):
        d = len(recipes)
        copy_index[copy, kind, place] = d
        recipes.append(value)
        names.append(f"{copy + 1}.{kind}{place}")
        holders[a].append(d)
        holders[b].append(d)

    for c in range(2):
        top = [1 << (6 * c + i) for i in range(5)]
        for i, val in enumerate(top):
            for bank, kind in enumerate(("t", "b")):
                new_distinction(c, kind, i, holder(c, bank, i), holder(c, bank, (i + 1) % 5),
                                val ^ (g[c] if bank else 0))
            rung = val ^ top[(i - 1) % 5]
            if c == 1 and i == 0:
                d = copy_index[0, "r", 0]
                copy_index[1, "r", 0] = d
                recipes[d] ^= rung
            else:
                new_distinction(c, "r", i, holder(c, 0, i), holder(c, 1, i), rung)
    assert len(set(recipes)) == len(recipes) == 29 and len(holders) == 18
    for stage_round, stage, family_at, gen in grown_stages(start, max_round):
        pass
    assert stage_round == max_round
    carriers, itinerary, limit = separately_carry(recipes, gen)
    ch = Changes(stage)
    image = ch.image(carriers)
    assert len(image) == 4096

    stage_two = list(holders.values())
    law_basis = {}
    for local in stage_two:
        insert(law_basis, mask(local))
    assert len(law_basis) == 17 and len(image) == 1 << (len(recipes) - len(law_basis))
    assert all((v & mask(local)).bit_count() % 2 == 0 for v in image for local in stage_two)
    all_knots = [canonical({parity_word(v, s) for v in image}, len(s)) for s in stage_two]
    assert all(x["is_knot"] for x in all_knots)
    idx = lambda c, kind, p: copy_index[c, kind, p]
    pair = lambda c, p: (idx(c, "t", p), idx(c, "b", p))
    third = [pair(0, 1), pair(1, 1), pair(0, 3) + pair(1, 3)]
    assert sum(map(len, third)) == len(set.union(*(set(s) for s in third)))
    third_values = {v: sum(((v & mask(s)).bit_count() % 2) << j for j, s in enumerate(third))
                    for v in image}
    third_knot = canonical(set(third_values.values()), 3)
    assert third_knot["is_knot"]
    conditioned = [len({third_values[v] for v in image if v & mask(s) == 0}) for s in stage_two]
    assert set(conditioned) == {4}
    small = set()
    shortest_sizes = []
    for d in range(len(recipes)):
        through = {v for v in image if v >> d & 1}
        least = min(v.bit_count() for v in through)
        shortest_sizes.append(least)
        small.update(v for v in through if v.bit_count() == least)
    assert set(shortest_sizes) == {4} and len(small) == 10 and len(span(small)) == 1024
    assert all(third_values[v] == 0 for v in small)
    tier_minima = [min(v.bit_count() for v, third_read in third_values.items() if third_read >> j & 1)
                   for j in range(3)]
    assert tier_minima == [5, 5, 5]
    source_facts = [[d for i in positions(v) for d in start.loose[i]] for v in (g[0], g[1], g[0] ^ g[1])]
    conditioned_rings = [len(ch.image(source_facts, whole_ring_holders(start, family_at, j))) for j in range(13)]
    assert set(conditioned_rings) == {4}
    fixed_counts = sum(len(ch.image_basis(carriers, (k,))) == 12 for k in range(len(stage)))
    assert fixed_counts == len(stage)
    initial_ch = Changes(start.supports())
    source_minima = [initial_ch.least_flip([d for i in positions(v) for d in start.loose[i]]) for v in
                     recipes + [g[0], g[1], g[0] ^ g[1]]]
    physical_minima = [ch.least_flip(f) for f in carriers + source_facts]
    assert set(source_minima) == {5} and set(physical_minima) == {5 + 2 * max_round}
    local_bound = ch.local_bound(stage)
    shortest_max = ch.shortest_max()
    # Two additional lawful four-place knots read the two independent third facts.
    extra = [pair(c, 1) + pair(c, 2) for c in range(2)]
    extra_checks = [canonical({parity_word(v, s) for v in image}, len(s)) for s in extra]
    assert all(x["is_knot"] for x in extra_checks)
    after_extra = [len({(third_values[v] >> c) & 1 for v in image if v & mask(s) == 0})
                   for c, s in enumerate(extra)]
    assert after_extra == [1, 1]
    return {
        "source": "Thirteen five-knot rings joined cyclically as in the seven-ring example. Each pair's connection consists of two doubled-linked attachment knots; each attachment meets two ring knots at separation two.",
        "round": max_round, "source knots": len(start.knots), "stage knots": len(stage),
        "stage distinctions": len(ch.ends), "third fact masks on the thirteen ring parities": [g[0], g[1], g[0] ^ g[1]],
        "29 second-layer distinctions": names, "their source masks": recipes,
        "their disjoint carriers as lists of [ring,generation]": itinerary, "last carrier generation": limit,
        "number of starting and grown least-flip calculations": len(physical_minima),
        "physical least flips [at start, at this round] for every listed fact": [min(source_minima), min(physical_minima)],
        "largest shortest change through an underlying distinction": shortest_max,
        "least sufficient scales from changes on incident pairs": dict(sorted(local_bound.items())),
        "underlying knots fixed one at a time leaving all 4096 states": fixed_counts,
        "whole rings including their births and two attachment knots fixed separately, number of third tuples": conditioned_rings,
        "eighteen selected second-layer knots": stage_two, "knots by number of places": dict(Counter(map(len, stage_two))),
        "canonical tests passing": sum(r["is_knot"] for r in all_knots),
        "independent laws from these knots": len(law_basis), "dimension of all their allowed states": 29 - len(law_basis),
        "number of states realized by the physical parities": len(image),
        "all shortest layer-two changes as sets of its distinctions": [list(positions(v)) for v in sorted(small)],
        "rank of shortest changes": len(span(small)).bit_length() - 1,
        "third facts as three disjoint sets of second-layer distinctions": third,
        "third fact names": [[names[d] for d in s] for s in third],
        "least layer-two change flipping each third fact": tier_minima,
        "number of third tuples with each chosen second-layer knot fixed to zero": conditioned,
        "third-layer projected knot": third_knot,
        "more eligible second-layer knots checked": extra, "extra knot checks": extra_checks,
        "number of g1 or g2 values when its extra knot is zero": after_extra,
        "cutoff control": "At layer-two scale five a change flips each of the three projected facts. At scale four all ten shortest changes preserve them. Both are exact enumerations.",
        "qualification": "The reduced layer was built by choosing a roster of separately carried sums. The 18 local parity knots generate its entire joint code and none reads a class fact. Two additional legitimate four-place knots read the two independent class facts, so they span the third if admitted. The calculation supplies no rule selecting this roster."
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (2_000_000_000, 2_000_000_000))
    start = monotonic()
    # Same start, independent growth implementation, and exact checks. The
    # pilot checks the shorter prefix of the main witness. For the other
    # reading the carrier construction itself needs six or more generations,
    # so time that same calculation on its full declared case.
    result = {"four outer rings and one central ring": central_check(1 if args.pilot else 8),
              "analysis": {
                  "sole canonical relation": "On a connected, nonempty loose source with at most two holders per distinction, a sum of laws containing only loose distinctions has equal law coefficients at the two holders of every shared distinction. The coefficients are constant. Every family contributes a nonempty, disjoint block. Thus the only formal nonzero relation on those m named blocks is the sum of all m, and the allowed family tuples are all even. With m=0 the empty tuple has no nonzero relation; m=1 is fixed and m=2 tied. Neither is a three-place knot. Even m>=3 still needs an unreadability test.",
                  "other relations": "The two sums on the left and right of the central ring both include its four shared distinctions. Their sum is the sole relation supported entirely on the loose distinctions. X has its own originally disjoint support, and under the laws is also A+B and C+D.",
                  "lasting": "At every funded generation two changed ends are necessary, one in each complementary set of families. A shortest starting flip has just two loose ends in opposite groups and can be extended for one extra distinction at each end per round. All generations consist of five two-parent births for each outer ring, with two fresh distinctions each.",
                  "all-round joint state with a knot fixed": "For a starting knot held fixed, its deletion leaves a connected route among all four outer rings, with loose distinctions remaining in each. Extend an allowed starting state along the rings. For a later fixed birth, any required two-ring change can use a starting loose distinction that follows a different sequence of births in its family, avoiding the fixed birth. The five-cycle of births supplies at least two separate ways forward. These two-ring changes span all even tuples. Translation treats any feasible fixed local value.",
                  "scale": "A connected set of two-distinction changes on a knot's places spans its entire even local subspace. The pair changes counted here extend via shortest detours avoiding that knot. At any scale reaching the largest local sufficient bound there is therefore no nonconstant locally readable class parity at any knot.",
                  "readers": "The fifteen-fact and twenty-nine-fact readings use selected sums and generations. Their nonconstant class facts depend on the choice of second-layer knots. Additional four-place knots read them or span them. On the canonical family-fact tuple the two-place changes already span all its allowed even tuples for m>=2. An intrinsic rule choosing the next facts, knots and changes is still required.",
                  "why other readings exist": "On the cyclic starts with m outer rings, m-1 independent family facts can supply the information variables of any selected binary linear code of dimension at most m-1. Use each coordinate's linear expression in those information variables. Whenever the same ring occurs in different expressions, use different generations of that ring's ten distinctions. The parity is unchanged by summing the relevant birth laws, while these physical supports are disjoint. Any nonconstant chosen coordinate has minimum 5+2t on these cyclic starts. This argument explains the freedom in the reader; it does not select one.",
                  "closed source changes": "All three values of the projected third-layer knot have representatives supported entirely on original loose distinctions. Every starting change with zero loose distinctions fixes all three. The 18-knot reading binds these facts through an inherited code chosen from the lasting loose parities, and never requires a source closed change to flip a third fact.",
              }}
    result["four-ring seconds"] = round(monotonic() - start, 3)
    second = monotonic()
    result["seven-ring chosen reading"] = circular_read(8 if args.pilot else 12)
    result["seven-ring seconds"] = round(monotonic() - second, 3)
    third = monotonic()
    result["thirteen-ring chosen third knot"] = two_joined_readings(10 if args.pilot else 24)
    result["thirteen-ring seconds"] = round(monotonic() - third, 3)
    if args.pilot:
        print(json.dumps({k: v for k, v in result.items() if k.endswith("seconds")}))
    else:
        (HERE / "overlap_counts.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps({k: v for k, v in result.items() if k.endswith("seconds")}))


if __name__ == "__main__":
    main()
