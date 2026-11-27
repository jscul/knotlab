"""Rebuild the two reported witnesses from their construction and recorded masks."""

import argparse
import json
import resource
import sys
from collections import Counter, defaultdict, deque
from contextlib import redirect_stdout
from io import StringIO
from itertools import combinations
from pathlib import Path
from time import perf_counter


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from knotlab.cli import main as knotlab_check


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def mask(places):
    return sum(1 << place for place in set(places))


def parity(value):
    return value.bit_count() % 2


def calculate_basis(values):
    basis = {}
    for value in values:
        while value:
            pivot = value.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = value
                break
            value ^= basis[pivot]
    return list(basis.values())


def combinations_of(generators):
    result = {0}
    for g in calculate_basis(generators):
        result.update(v ^ g for v in tuple(result))
    return result


def observe(value, supports):
    return sum(parity(value & support) << i for i, support in enumerate(supports))


def words(values, width):
    return sorted("".join(str((value >> i) & 1) for i in range(width)) for value in values)


def components(neighbors):
    remaining = set(neighbors)
    while remaining:
        first = min(remaining)
        remaining.remove(first)
        component = [first]
        for current in component:
            for other in sorted(neighbors[current] & remaining):
                remaining.remove(other)
                component.append(other)
        yield tuple(sorted(component))


class Presentation:
    def __init__(self, count):
        self.knots = [set() for _ in range(count)]
        self.distinctions = []

    def knot(self):
        self.knots.append(set())
        return len(self.knots) - 1

    def distinction(self, *holders):
        index = len(self.distinctions)
        self.distinctions.append(holders)
        for holder in holders:
            self.knots[holder].add(index)
        return index

    def end(self):
        loose = defaultdict(list)
        neighbors = defaultdict(set)
        for i, holds in enumerate(self.distinctions):
            if len(holds) == 1:
                loose[holds[0]].append(i)
            else:
                u, v = holds
                neighbors[u].add(v)
                neighbors[v].add(u)
        live = set(loose)
        witnesses = [holds & live for holds in neighbors.values()]
        return loose, witnesses

    def grow(self):
        loose, witnesses = self.end()
        assert loose
        groups = proposed_groups(loose, witnesses)
        available = {k: deque(ds) for k, ds in loose.items()}
        takes = [tuple(available[k].popleft() for k in group) for group in groups]
        for knot, remainder in sorted(available.items()):
            groups.extend([(knot,)] * len(remainder))
            takes.extend((d,) for d in remainder)

        children = defaultdict(set)
        for i, parents in enumerate(groups):
            for parent in parents:
                children[parent].add(i)
        next_groups = proposed_groups(range(len(groups)), children.values())
        demand = Counter(knot for group in next_groups for knot in group)

        births = []
        for i, (parents, inputs) in enumerate(zip(groups, takes)):
            knot = self.knot()
            for d in inputs:
                self.distinctions[d] += (knot,)
                self.knots[knot].add(d)
            # All stages checked here are connected. A sole birth takes all loose distinctions.
            fresh_count = max(demand[i], 3 - len(parents), 1) if len(groups) > 1 else 0
            fresh = tuple(self.distinction(knot) for _ in range(fresh_count))
            births.append((knot, parents, fresh))
        return births


def live_neighbors(live, witnesses):
    adjacent = {k: set() for k in live}
    for witness in witnesses:
        for a, b in combinations(witness, 2):
            adjacent[a].add(b)
            adjacent[b].add(a)
    return adjacent


def maximal_cliques(adjacent):
    def visit(current, possible, excluded):
        if not possible and not excluded:
            yield current
            return
        pivot = max(possible | excluded, key=lambda k: len(possible & adjacent[k]))
        for node in sorted(possible - adjacent[pivot]):
            yield from visit(current | {node}, possible & adjacent[node], excluded & adjacent[node])
            possible.remove(node)
            excluded.add(node)

    # Split components before clique search so the unwitnessed groups stay local.
    for component in components(adjacent):
        yield from visit(set(), set(component), set())


def proposed_groups(live, witnesses):
    witnesses = list(witnesses)
    adjacent = live_neighbors(live, witnesses)
    # Any larger clique containing an unwitnessed clique also lacks a witness.
    groups = [tuple(sorted(c)) for c in maximal_cliques(adjacent)
              if len(c) >= 3 and not any(c <= w for w in witnesses)]
    covered = {pair for c in groups for pair in combinations(c, 2)}
    groups.extend((a, b) for a in adjacent for b in adjacent[a]
                  if a < b and (a, b) not in covered)
    return sorted(groups)


def ring_start(count, size, circular):
    pattern = Presentation(count * size)
    rings = [tuple(range(i * size, (i + 1) * size)) for i in range(count)]

    def make_ring(ring):
        for i, knot in enumerate(ring):
            pattern.distinction(knot, ring[(i + 1) % size])

    def give_loose(ring):
        return tuple(pattern.distinction(k) for k in ring for _ in range(2))

    if circular:
        loose = []
        for ring in rings:
            make_ring(ring)
            loose.append(give_loose(ring))
        links = [(i, (i + 1) % count, (0, 2), (1, 3)) for i in range(count)]
    else:
        for ring in rings:
            make_ring(ring)
        loose = [give_loose(ring) for ring in rings]
        ports = Counter()
        links = []
        for i, j in combinations(range(count), 2):
            links.append((i, j, (ports[i], ports[i] + 2), (ports[j], ports[j] + 2)))
            ports.update((i, j))
    for i, j, left, right in links:
        a, b = pattern.knot(), pattern.knot()
        for slot in left:
            pattern.distinction(a, rings[i][slot])
        for slot in right:
            pattern.distinction(b, rings[j][slot])
        pattern.distinction(a, b)
        pattern.distinction(a, b)
    return pattern, rings, loose


class Changes:
    """Represent even changes by closed trails, using one auxiliary holder."""

    def __init__(self, pattern, forgotten_knot=None):
        self.outside = len(pattern.knots)
        self.incident = [[] for _ in range(self.outside + 1)]
        self.ends = []
        for d, owners in enumerate(pattern.distinctions):
            mapped = [self.outside if h == forgotten_knot else h for h in owners]
            u, v = mapped if len(mapped) == 2 else (mapped[0], self.outside)
            self.ends.append((u, v))
            self.incident[u].append((v, d))
            self.incident[v].append((u, d))

    def cycle_basis(self):
        # Fundamental cycles from a spanning forest give every allowed change.
        path = {}
        tree_distinctions = set()
        for root in range(len(self.incident)):
            if root in path:
                continue
            path[root] = 0
            search = [root]
            for u in search:
                for v, d in self.incident[u]:
                    if v not in path:
                        path[v] = path[u] ^ (1 << d)
                        tree_distinctions.add(d)
                        search.append(v)
        for d, (u, v) in enumerate(self.ends):
            if d not in tree_distinctions:
                yield path[u] ^ path[v] ^ (1 << d)

    def image(self, supports):
        return combinations_of(observe(v, supports) for v in self.cycle_basis())

    def least_flip(self, support):
        # An odd closed trail in the doubled graph contains an odd simple cycle.
        # XOR its distinctions to recover a real change; length bounds its size.
        marked = set(bits(support))
        starts = {u for d in marked for u in self.ends[d]}
        best = None
        for start in sorted(starts):
            origin, target = 2 * start, 2 * start + 1
            visits = {origin: (0, 0)}
            queue = deque([origin])
            while queue and target not in visits:
                state = queue.popleft()
                size, change = visits[state]
                if best is not None and size + 1 >= best.bit_count():
                    continue
                for neighbor, d in self.incident[state // 2]:
                    new = 2 * neighbor + (state % 2 ^ (d in marked))
                    if new not in visits:
                        visits[new] = (size + 1, change ^ (1 << d))
                        queue.append(new)
            if target in visits:
                best = visits[target][1]
        if best is not None:
            holder_parities = Counter(h for d in bits(best) for h in self.ends[d])
            assert all(v % 2 == 0 for v in holder_parities.values())
            assert parity(best & support) == 1
        return best

    def shortest_steps(self, start, ignore, limit):
        found = {start: 0}
        queue = deque([start])
        while queue:
            current = queue.popleft()
            steps = found[current] + 1
            if steps > limit:
                continue
            for other, _ in self.incident[current]:
                if other != ignore and other not in found:
                    found[other] = steps
                    queue.append(other)
        return found

    def local_class_functions(self, scale):
        # A simple cycle visiting a holder uses a pair of incident distinctions.
        # These pairs generate the projected small changes at that holder.
        cycles = list(self.cycle_basis())
        local = []
        for k, held in enumerate(self.incident[:self.outside]):
            reachable = {}
            adjacency = {d: set() for _, d in held}
            for (v, d), (w, e) in combinations(held, 2):
                if v not in reachable:
                    reachable[v] = self.shortest_steps(v, k, scale - 2)
                if w in reachable[v]:
                    adjacency[d].add(e)
                    adjacency[e].add(d)
            places = [mask(c) for c in components(adjacency)]
            # The entire parity law is fixed. A connected adjacency leaves no other candidates.
            functions = set()
            if len(places) > 1:
                signatures = [functional(cycles, p) for p in places]
                functions = combinations_of(signatures) - {0}
            local.append(functions)
        return cycles, local


def functional(generators, support):
    return sum(parity(v & support) << i for i, v in enumerate(generators))


def canonical(image, width, all_contacts=False):
    names = [f"p{i}" for i in range(width)]
    excluded = sorted(set(range(1 << width)) - image)
    assert excluded
    cnf = "; ".join(" ".join(("~" if v >> j & 1 else "") + p for j, p in enumerate(names))
                    for v in excluded)
    results = []
    for contact in (names if all_contacts else names[-1:]):
        capture = StringIO()
        with redirect_stdout(capture):
            status = knotlab_check(["check", "--cnf", cnf, "--loops",
                                    *(p for p in names if p != contact), "--contact", contact, "--json"])
        report = json.loads(capture.getvalue())
        # The checker displays its loop order followed by the selected contact.
        order = [i for i, p in enumerate(names) if p != contact] + [names.index(contact)]
        relabeled = {observe(v, [1 << i for i in order]) for v in image}
        assert sorted(report["allowed"]) == words(relabeled, width)
        results.append({k: report[k] for k in ("binding", "loss_on_erasure", "coexistence", "is_knot")})
        assert status == int(not report["is_knot"])
    return results if all_contacts else results[0]


def check_small_calculation():
    """Compare the graph calculations with every literal state of one small fixture."""
    pattern = Presentation(4)
    for a, b in [(0, 1), (0, 1), (1, 2), (2, 3), (2, 3)]:
        pattern.distinction(a, b)
    for a in [0, 0, 3, 3]:
        pattern.distinction(a)
    ch = Changes(pattern)
    width = len(pattern.distinctions)
    laws = list(map(mask, pattern.knots))
    states = {v for v in range(1 << width) if observe(v, laws) == 0}
    assert combinations_of(ch.cycle_basis()) == states
    for f in range(1, 1 << width):
        expected = min((s.bit_count() for s in states if parity(f & s)), default=None)
        change = ch.least_flip(f)
        assert (change.bit_count() if change is not None else None) == expected
    for scale in range(2, 6):
        cycles, loc = ch.local_class_functions(scale)
        small = [v for v in states if v.bit_count() <= scale]
        for places, actual in zip(pattern.knots, loc):
            good = {functional(cycles, s) for s in combinations_of(1 << d for d in places)
                    if all(not parity(v & s) for v in small)} - {0}
            assert actual == good
    return {"distinctions": width, "literal states": len(states), "least-flip comparisons": (1 << width) - 1,
            "local class comparisons": 4 * len(pattern.knots)}


def overlap(pilot):
    pattern, rings, initial_loose = ring_start(3, 4, circular=False)
    loose, witnesses = pattern.end()
    families = list(components(live_neighbors(loose, witnesses)))
    halves = [set(f) for f in families if set(f) <= set(rings[0])]
    assert halves == [{0, 2}, {1, 3}]
    raw = json.loads((HERE.parent / "overlap.json").read_text())
    result = {"source knots": len(pattern.knots), "source distinctions": len(pattern.distinctions),
              "alternating first-ring families": [sorted(f) for f in halves], "rounds": []}
    expected_knots = [mask(p) for p in [(0, 1, 2), (3, 4, 0)]]
    for t in range(1, 2 if pilot else 7):
        births = pattern.grow()
        if t == 1:
            family_births = [[b for b in births if set(b[1]) <= f] for f in halves]
            extra_loose = [tuple(d for _, _, fresh in b for d in fresh) for b in family_births]
            carriers = initial_loose + extra_loose
            supports = list(map(mask, carriers))
            assert len(set.union(*(set(c) for c in carriers))) == sum(map(len, carriers))
            result["carrier distinctions R S T P Q"] = carriers

        comparisons = raw["stages"][t - 1]
        ch = Changes(pattern)
        image = ch.image(supports)
        triples = [set(observe(v, [1 << p for p in places]) for v in image)
                   for places in [(0, 1, 2), (3, 4, 0)]]
        assert image == {v for v in range(32) if observe(v, expected_knots) == 0}
        changes = [ch.least_flip(s) for s in supports]
        sizes = [v.bit_count() for v in changes]
        row = {"round": t, "knots": len(pattern.knots), "distinctions": len(pattern.distinctions),
               "five-place allowed tuples": words(image, 5), "least flips": sizes,
               "one realizing change per carrier": [list(bits(v)) for v in changes]}
        if t == 1:
            result["projected triples"] = [words(rel, 3) for rel in triples]
            result["canonical checks for each contact choice"] = [canonical(rel, 3, True) for rel in triples]
        assert len(image) == comparisons["words of the five"]
        assert all(row[k] == comparisons[k] for k in ("knots", "distinctions", "least flips"))
        if t >= 4:
            cycles, local = ch.local_class_functions(12)
            local_span = combinations_of(f for owned in local for f in owned)
            flags = [size > 12 for size in sizes]
            unread = [functional(cycles, s) not in local_span for s in supports]
            row["scale 12"] = {"class facts": flags, "outside local span": unread,
                              "local fact occurrences": sum(map(len, local))}
            assert flags == [x["class fact at k"] for x in comparisons["scale 12"]]
            assert unread == [x["held by no part at k"] for x in comparisons["scale 12"]]
            assert sum(map(len, local)) == comparisons["single-knot class facts at 12"]
        if t == 5:
            # Forget exactly one law, while retaining every distinction and carrier.
            first_births = {k for family in family_births for k, _, _ in family}
            deletion = defaultdict(list)
            for k in range(len(pattern.knots)):
                actual = Changes(pattern, forgotten_knot=k).image(supports)
                remaining = expected_knots[1:] if k < 18 else expected_knots[:1] if k in first_births else expected_knots
                assert actual == {v for v in range(32) if observe(v, remaining) == 0}
                outcome = "both triples still bound"
                if k < 18:
                    outcome = "RST released"
                elif k in first_births:
                    outcome = "PQR released"
                deletion[outcome].append(k)
            row["law removals by result"] = dict(deletion)
            assert len(deletion["RST released"]) == comparisons["single law removals freeing each triple"]["R S T"]["start"]
            assert len(deletion["PQR released"]) == comparisons["single law removals freeing each triple"]["P Q R"]["born"]
        result["rounds"].append(row)
    return result


def class_signature(words_generating_code, small, support):
    return functional(words_generating_code, support) if all(not parity(v & support) for v in small) else 0


def algebra(archive):
    recipes = archive["their source masks"]
    expected = json.loads((HERE.parent / "third_algebra.json").read_text())
    selected = archive["eighteen selected second-layer knots"]
    extras = archive["more eligible second-layer knots checked"]
    width = len(recipes)
    image = {observe(v, recipes) for v in range(1 << 13) if parity(v) == 0}
    generators = calculate_basis(sorted(image))
    assert all(observe(v, list(map(mask, selected))) == 0 for v in image)
    equation_rank = len(calculate_basis(list(map(mask, selected))))
    assert len(image) == 1 << (width - equation_rank) == expected["states"]
    reports = [canonical({observe(v, [1 << d for d in knot]) for v in image}, len(knot))
               for knot in selected + extras]
    assert all(r["is_knot"] for r in reports)

    tied_shortest = set()
    shortest_sizes = []
    for d in range(width):
        possible = {v for v in image if v >> d & 1}
        size = min(v.bit_count() for v in possible)
        shortest_sizes.append(size)
        tied_shortest.update(v for v in possible if v.bit_count() == size)
    assert {tuple(bits(v)) for v in tied_shortest} == {
        tuple(x) for x in archive["all shortest layer-two changes as sets of its distinctions"]}
    move_rank = len(calculate_basis(sorted(tied_shortest)))
    assert move_rank == expected["rank of least changes"]
    third_supports = list(map(mask, archive["third facts as three disjoint sets of second-layer distinctions"]))
    assert not any(a & b for a, b in combinations(third_supports, 2))
    third_image = {observe(v, third_supports) for v in image}
    third_checks = canonical(third_image, 3, True)
    assert all(r["is_knot"] for r in third_checks)
    class_dimension = len(generators) - move_rank
    assert class_dimension == expected["layer-three class-fact dimension"]
    third_signatures = [class_signature(generators, tied_shortest, m) for m in third_supports]
    assert all(third_signatures) and len(calculate_basis(third_signatures)) == class_dimension
    least = [min(v.bit_count() for v in image if parity(v & m)) for m in third_supports]
    assert least == expected["least layer-two change flipping each third fact"]

    def conditional(knot):
        settings = defaultdict(set)
        for v in image:
            settings[v & mask(knot)].add(observe(v, third_supports))
        return {"settings": len(settings), "third tuple counts": sorted({len(x) for x in settings.values()}),
                "third tuples at zero": words(settings[0], 3)}

    def local(knot):
        return {class_signature(generators, tied_shortest, m)
                for m in combinations_of(1 << p for p in knot)} - {0}

    baseline_controls = [conditional(knot) for knot in selected]
    assert all(c["third tuple counts"] == [4] for c in baseline_controls)
    baseline_local = [local(knot) for knot in selected]
    assert not any(baseline_local)
    extra_local = [local(knot) for knot in extras]
    assert extra_local == [{third_signatures[0]}, {third_signatures[1]}]
    with_extras = combinations_of(f for facts in extra_local for f in facts)
    assert set(third_signatures) < with_extras
    extra_controls = [conditional(knot) for knot in extras]
    assert all(c["third tuple counts"] == [2] for c in extra_controls)
    fixed_both = {observe(v, third_supports) for v in image if all(not v & mask(knot) for knot in extras)}
    assert fixed_both == {0}

    return {"layer two distinctions": width, "joint states": len(image), "joint dimension": len(generators),
            "independent chosen laws": equation_rank, "chosen knot checks": reports[:len(selected)],
            "tied shortest changes through any distinction": [list(bits(v)) for v in sorted(tied_shortest)],
            "shortest sizes through individual distinctions": shortest_sizes, "shortest change rank": move_rank,
            "layer three class function dimension": class_dimension, "third allowed tuples": words(third_image, 3),
            "third canonical checks for each contact choice": third_checks,
            "third least flipping sizes": least, "class functions read by a chosen knot": sum(map(len, baseline_local)),
            "conditioning on each chosen knot": baseline_controls, "extra knot checks": reports[len(selected):],
            "conditioning on each extra knot": extra_controls, "third tuples fixing both extras": words(fixed_both, 3),
            "local class span dimension with both extras": len(calculate_basis(sorted(with_extras)))}


def physical(archive, pilot):
    pattern, rings, initial_loose = ring_start(13, 5, circular=True)
    label = {k: i for i, r in enumerate(rings) for k in r}
    loose, witnesses = pattern.end()
    assert list(components(live_neighbors(loose, witnesses))) == rings
    recipes = archive["their source masks"]
    extra_recipes = archive["third fact masks on the thirteen ring parities"]
    source = Changes(pattern)
    source_supports = [mask(d for i in bits(recipe) for d in initial_loose[i]) for recipe in recipes + extra_recipes]
    source_minima = [source.least_flip(f).bit_count() for f in source_supports]
    assert set(source_minima) == {5}
    generations = [initial_loose]
    tmax = 1 if pilot else archive["round"]
    for t in range(1, tmax + 1):
        before = len(pattern.knots)
        layer = [[] for _ in rings]
        births = pattern.grow()
        for knot, parents, fresh in births:
            owners = {label[p] for p in parents}
            assert len(owners) == 1 and len(parents) == len(fresh) == 2
            label[knot] = owners.pop()
            layer[label[knot]].extend(fresh)
        assert len(pattern.knots) - before == 65 and set(map(len, layer)) == {10}
        generations.append(layer)
    itineraries = []
    used = Counter()
    for recipe in recipes:
        itinerary = [(i, used[i]) for i in bits(recipe)]
        used.update(bits(recipe))
        itineraries.append(itinerary)
    assert [[list(pair) for pair in read] for read in itineraries] == archive["their disjoint carriers as lists of [ring,generation]"]
    chosen = [n for n, read in enumerate(itineraries) if all(age <= tmax for _, age in read)]
    supports = [mask(d for i, age in itineraries[n] for d in generations[age][i]) for n in chosen]
    assert sum(s.bit_count() for s in supports) == mask(d for s in supports for d in bits(s)).bit_count()
    grown = Changes(pattern)
    measured = grown.image(supports)
    assert measured == {observe(v, [recipes[n] for n in chosen]) for v in range(1 << 13) if parity(v) == 0}
    all_minima = [grown.least_flip(f).bit_count() for f in supports + source_supports[len(recipes):]]
    assert set(all_minima) == {tmax * 2 + 5}
    scale = 2 * tmax + 4
    _, local = grown.local_class_functions(scale)
    local_count = sum(map(len, local))
    if not pilot:
        assert len(pattern.knots) == archive["stage knots"]
        assert len(pattern.distinctions) == archive["stage distinctions"]
        assert len(measured) == archive["number of states realized by the physical parities"]
        assert local_count == 0
    return {"round": tmax, "knots": len(pattern.knots), "distinctions": len(pattern.distinctions),
            "disjoint carrier sizes": [s.bit_count() for s in supports], "physical allowed tuple count": len(measured),
            "starting minima for all named facts": source_minima, "grown minima for checked facts": all_minima,
            "physical scale": scale, "single-knot class functions": local_count}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    limit = min(2 << 30, resource.getrlimit(resource.RLIMIT_AS)[0])
    resource.setrlimit(resource.RLIMIT_AS, (2 << 30 if limit == resource.RLIM_INFINITY else limit,
                                           resource.getrlimit(resource.RLIMIT_AS)[1]))
    archive_path = ROOT / "research" / "THIRD-LAYER-20261126-001" / "referee-R1" / "overlap_counts.json"
    archive = json.loads(archive_path.read_text())["thirteen-ring chosen third knot"]
    result = {}
    for name, check in [("literal calibration", check_small_calculation),
                        ("overlap", lambda: overlap(args.pilot)), ("third algebra", lambda: algebra(archive)),
                        ("physical thirteen-ring replay", lambda: physical(archive, args.pilot))]:
        start = perf_counter()
        result[name] = check()
        print(f"{name} completed in {perf_counter() - start:.3f} s", flush=True)
    if not args.pilot:
        target = HERE / "witness_check.json"
        serialized = json.dumps(result, indent=2) + "\n"
        if args.verify:
            assert target.read_text() == serialized
        else:
            target.write_text(serialized)


if __name__ == "__main__":
    main()
