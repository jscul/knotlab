"""A loop on the frozen tree's own places, and a separate test of a single reader.

The two small starts use ordinary growth. Every candidate group on the
constructed trajectories has two parents or is an offshoot. The checks below
reject a trajectory outside that class.
"""

import argparse
import contextlib
import io
import itertools
import json
import resource
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))
from knotlab.cli import main as knot_check


def subset_mask(members):
    return sum(1 << member for member in members)


def reduce_mask(value, basis):
    for pivot in sorted(basis, reverse=True):
        if value >> pivot & 1:
            value ^= basis[pivot]
    return value


def row_basis(values):
    basis = {}
    for value in values:
        value = reduce_mask(value, basis)
        if value:
            basis[value.bit_length() - 1] = value
    return basis


def project(word, places):
    return sum(((word >> original) & 1) << position for position, original in enumerate(places))


def parity(word, support):
    return (word & support).bit_count() % 2


class Holdings:
    def __init__(self):
        self.supports = []
        self.holders = []

    def new_knot(self):
        self.supports.append([])
        return len(self.supports) - 1

    def new_distinction(self, *owners):
        label = len(self.holders)
        self.holders.append(list(owners))
        for knot in owners:
            self.supports[knot].append(label)

    def share(self, distinction, knot):
        assert len(self.holders[distinction]) == 1
        self.holders[distinction].append(knot)
        self.supports[knot].append(distinction)

    def incidence(self):
        # Unused loose ends meet one extra formal holder. The parity there
        # already follows by summing all the actual knot laws.
        end = len(self.supports)
        adj = [[] for _ in range(end + 1)]
        for index, owners in enumerate(self.holders):
            a = owners[0]
            b = owners[1] if len(owners) == 2 else end
            adj[a].append((b, index))
            adj[b].append((a, index))
        return adj


def source_rings(number, size):
    system = Holdings()
    rings = [[system.new_knot() for _ in range(size)] for _ in range(number)]
    for ring in rings:
        for a, b in zip(ring, ring[1:] + ring[:1]):
            system.new_distinction(a, b)
    for ring in rings:
        for knot in ring:
            for _ in range(2):
                system.new_distinction(knot)
    return system, rings


def three_split_rings(size):
    system, rings = source_rings(3, size)
    positions = [0, 0, 0]
    for i, j in itertools.combinations(range(3), 2):
        a, b = system.new_knot(), system.new_knot()
        for index, joining in ((i, a), (j, b)):
            start = positions[index]
            positions[index] += 1
            for offset in (0, 2):
                system.new_distinction(joining, rings[index][start + offset])
        for _ in range(2):
            system.new_distinction(a, b)
    return system


def three_rings_of_four():
    return three_split_rings(4)


def six_rings_of_five():
    system, rings = source_rings(6, 5)
    for i, j, steps in [(0, 1, 3), (3, 4, 3), (1, 2, 4), (2, 5, 5), (5, 3, 5)]:
        for anchor in (0, 1):
            route = [rings[i][anchor]]
            route.extend(system.new_knot() for _ in range(steps - 1))
            route.append(rings[j][anchor])
            for a, b in zip(route, route[1:]):
                for _ in range(2):
                    system.new_distinction(a, b)
    return system


def loose_distinctions(system):
    groups = defaultdict(list)
    for index, owners in enumerate(system.holders):
        if len(owners) == 1:
            groups[owners[0]].append(index)
    return groups


def source_neighbors(system):
    neighbors = [set() for _ in system.supports]
    for owners in system.holders:
        if len(owners) == 2:
            a, b = owners
            neighbors[a].add(b)
            neighbors[b].add(a)
    return neighbors


def shared_witness_pairs(neighbors, live):
    return {pair for group in neighbors for pair in itertools.combinations(sorted(group & live), 2)}


def pair_only(pairs):
    peers = defaultdict(set)
    for a, b in pairs:
        peers[a].add(b)
        peers[b].add(a)
    return all(not (peers[a] & peers[b]) for a, b in pairs)


def components(names, pairs):
    groups = [{a} for a in names]
    for a, b in sorted(pairs):
        first = next(group for group in groups if a in group)
        second = next(group for group in groups if b in group)
        if first is not second:
            first.update(second)
            groups.remove(second)
    return sorted(map(frozenset, groups), key=min)


def family_distances(system):
    live = set(loose_distinctions(system))
    neighbors = source_neighbors(system)
    families = components(live, shared_witness_pairs(neighbors, live))
    distances = {}
    for i, family in enumerate(families):
        counts = {knot: 0 for knot in family}
        queue = deque(family)
        while queue:
            knot = queue.popleft()
            for peer in neighbors[knot] - counts.keys():
                counts[peer] = counts[knot] + 1
                queue.append(peer)
        for j in range(i + 1, len(families)):
            distances[i, j] = min(counts[knot] for knot in families[j])
    return families, distances


def distance_tree(m, distances):
    before = [frozenset({i}) for i in range(m)]
    children = {}
    for threshold in sorted(set(distances.values())):
        after = components(range(m), (pair for pair, steps in distances.items() if steps <= threshold))
        for cluster in after:
            if cluster not in before:
                children[cluster] = [old for old in before if old <= cluster]
        before = after
    depth = {frozenset(range(m)): 0}
    for parent in sorted(children, key=len, reverse=True):
        for child in children[parent]:
            depth[child] = depth[parent] + 1
    places = sorted((p for p in depth if depth[p]), key=lambda p: (len(p), sorted(p)))
    parts = []
    for parent, kids in children.items():
        inside = kids + ([parent] if depth[parent] else [])
        parts.append(sorted(places.index(place) for place in inside))
    return places, parts, depth


def grow(system, lineage):
    loose = loose_distinctions(system)
    pairs = shared_witness_pairs(source_neighbors(system), loose.keys())
    assert pair_only(pairs) and all(len(values) == 2 for values in loose.values())
    available = {knot: iter(seq) for knot, seq in loose.items()}
    plan = [(pair, [next(available[parent]) for parent in pair]) for pair in sorted(pairs)]
    plan.extend(((parent,), [d]) for parent, seq in available.items() for d in seq)
    children = defaultdict(set)
    for number, (parents, _) in enumerate(plan):
        for parent in parents:
            children[parent].add(number)
    next_pairs = {pair for group in children.values() for pair in itertools.combinations(sorted(group), 2)}
    assert pair_only(next_pairs)
    next_demand = Counter(knot for pair in next_pairs for knot in pair)
    newborn = {}
    carried = defaultdict(list)
    for number, (parents, inputs) in enumerate(plan):
        group = {lineage[parent] for parent in parents}
        assert len(group) == 1
        family = group.pop()
        knot = system.new_knot()
        newborn[knot] = family
        for distinction in inputs:
            system.share(distinction, knot)
        # Each input is only one of two loose distinctions at its parent,
        # hence changing both at that parent witnesses input nonimplication.
        fresh_count = max(1, 3 - len(inputs), next_demand[number])
        for _ in range(fresh_count):
            carried[family].append(len(system.holders))
            system.new_distinction(knot)
    return newborn, carried


def shortest_mark_change(adj, marked):
    # Every allowed change splits into simple closed changes. An odd sum
    # in the chosen carrier needs one odd summand. The shortest closed walk
    # that changes the parity gives the exact least such sum.
    best = 2 * len(adj) + 1
    for start in range(len(adj)):
        queue = deque([(start, 0, 0)])
        seen = {(start, 0)}
        while queue:
            here, value, distance = queue.popleft()
            if distance + 1 >= best:
                continue
            for peer, distinction in adj[here]:
                after = value ^ (distinction in marked)
                if peer == start and after:
                    best = distance + 1
                    break
                if (peer, after) not in seen:
                    seen.add((peer, after))
                    queue.append((peer, after, distance + 1))
    return best if best <= 2 * len(adj) else None


def local_class_counts(adj, limit):
    # At a single holder a simple closed change restricts to exactly
    # two distinctions. Find all obtainable pairs within the threshold
    # by removing that holder and completing the change between the peers.
    dimensions = Counter()
    for knot in range(len(adj) - 1):
        links = adj[knot]
        small_pairs = []
        for i, (initial, _) in enumerate(links):
            around = {initial: 0}
            queue = deque([initial])
            while queue:
                here = queue.popleft()
                if around[here] >= limit - 2:
                    continue
                for peer, _ in adj[here]:
                    if peer != knot and peer not in around:
                        around[peer] = around[here] + 1
                        queue.append(peer)
            small_pairs.extend((1 << i) | (1 << j) for j in range(i) if links[j][0] in around)
        all_pairs = []
        # Repeat without a threshold to avoid assuming the local relation
        # contains every even word at a holder that separates the start.
        remaining = set(range(len(adj))) - {knot}
        peer_group = {}
        while remaining:
            root = remaining.pop()
            queue = [root]
            while queue:
                here = queue.pop()
                peer_group[here] = root
                for peer, _ in adj[here]:
                    if peer in remaining:
                        remaining.remove(peer)
                        queue.append(peer)
        for i, (peer, _) in enumerate(links):
            all_pairs.extend((1 << i) | (1 << j) for j in range(i)
                             if peer_group[links[j][0]] == peer_group[peer])
        dimensions[len(row_basis(all_pairs)) - len(row_basis(small_pairs))] += 1
    return dict(sorted(dimensions.items()))


def image(rows, carriers):
    basis = row_basis(rows)
    forms = [reduce_mask(subset_mask(carrier), basis) for carrier in carriers]
    values = {0}
    active = set().union(*(set(i for i in range(form.bit_length()) if form >> i & 1) for form in forms))
    for i in sorted(active):
        on_generator = sum(((form >> i) & 1) << j for j, form in enumerate(forms))
        values |= {word ^ on_generator for word in values}
    return sorted(values)


def canonical_check(words, size):
    names = [f"v{i}" for i in range(size)]
    clauses = [" ".join(("~" if word >> i & 1 else "") + name for i, name in enumerate(names))
               for word in range(1 << size) if word not in words]
    results = []
    for i, contact in enumerate(names):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = knot_check(["check", "--cnf", ";".join(clauses), "--loops",
                               *(names[:i] + names[i + 1:]), "--contact", contact, "--json"])
        assert code == 0
        check = json.loads(out.getvalue())
        results.append(all(check[key] for key in ("binding", "loss_on_erasure", "coexistence", "is_knot")))
    return results


def minimal_relations(words, n):
    minimal = []
    for size in range(1, n + 1):
        for places in itertools.combinations(range(n), size):
            support = subset_mask(places)
            if any(subset_mask(knot) & support == subset_mask(knot) for knot in minimal):
                continue
            if all(not parity(word, support) for word in words):
                minimal.append(places)
    return minimal


def next_layer(words, n, knots):
    least_weight = min(word.bit_count() for word in words if word)
    least = [word for word in words if word.bit_count() == least_weight]
    classes = {}
    for mask in range(1, 1 << n):
        if any(parity(word, mask) for word in least):
            continue
        values = sum(parity(word, mask) << i for i, word in enumerate(words))
        if values:
            classes.setdefault(values, mask)
    records = []
    local = []
    for table, mask in classes.items():
        readers = []
        separating_words = []
        for i, knot in enumerate(knots):
            by_local_word = defaultdict(set)
            for j, word in enumerate(words):
                by_local_word[project(word, knot)].add(table >> j & 1)
            if all(len(readings) == 1 for readings in by_local_word.values()):
                readers.append(i)
            else:
                separating_words.append(next(word for word in words if not project(word, knot) and parity(word, mask)))
        record = {"representative": mask, "single readers": readers}
        if not readers:
            record["word agreeing with zero on each knot in order and flipping this fact"] = separating_words
        records.append(record)
        if readers:
            local.append(table)
    return {"least words": least, "least weight": least_weight, "least rank": len(row_basis(least)),
            "class dimension": len(row_basis(classes)), "class facts": records,
            "local span dimension": len(row_basis(local))}


def certificate(builder, rounds, pilot):
    system = builder()
    families, distances = family_distances(system)
    places, parts, depth = distance_tree(len(families), distances)
    lineage = {knot: i for i, family in enumerate(families) for knot in family}
    born_in = []
    cohorts = [defaultdict(list)]
    for knot, seq in loose_distinctions(system).items():
        cohorts[0][lineage[knot]].extend(seq)
    milestones = [[len(system.supports), len(system.holders)]]
    for _ in range(rounds):
        lineage, carried = grow(system, lineage)
        born_in.append(lineage)
        cohorts.append(carried)
        milestones.append([len(system.supports), len(system.holders)])
    carriers = [set().union(*(cohorts[depth[place] - 1][i] for i in place)) for place in places]
    assert sum(map(len, carriers)) == len(set.union(*carriers))
    rows = [subset_mask(seq) for seq in system.supports]
    words = image(rows, carriers)
    abstract = sorted({sum(parity(family_word, subset_mask(place)) << i for i, place in enumerate(places))
                       for family_word in range(1 << len(families)) if not family_word.bit_count() % 2})
    assert abstract == words
    knots = minimal_relations(words, len(places))
    assert all(tuple(group) in knots for group in parts)
    four = [group for group in knots if len(group) == 4]
    loop = [group for group in itertools.combinations(four, 3)
            if sorted(len(set(a) & set(b)) for a, b in itertools.combinations(group, 2)) == [1, 1, 1]
            and not set.intersection(*(set(knot) for knot in group))]
    checks = []
    for group in knots:
        subwords = {project(word, group) for word in words}
        checks.append({"places": group, "number of allowed words": len(subwords),
                       "canonical check for each contact": canonical_check(subwords, len(group))})
    assert all(all(item["canonical check for each contact"]) for item in checks)
    adj = system.incidence()
    minima = [shortest_mark_change(adj, support) for support in carriers]
    local = local_class_counts(adj, 12)
    result = {"start families": [sorted(g) for g in families],
              "pair holder-step counts": [[*pair, d] for pair, d in distances.items()],
              "knots and distinctions through rounds": milestones,
              "places as family sets": [sorted(p) for p in places],
              "generation of each carrier": [depth[p] - 1 for p in places],
              "disjoint carriers as distinction numbers": [sorted(seq) for seq in carriers],
              "least changes": minima, "single-knot class dimension histogram at scale twelve": local,
              "node with children, in place numbers": parts,
              "allowed words": words, "minimal relations": checks,
              "three four-place knots sharing three different places": loop,
              "next layer on node with children": next_layer(words, len(places), parts),
              "next layer on all minimal relations": next_layer(words, len(places), knots)}
    if builder == three_rings_of_four:
        assert len(loop) == 1 and len(knots) == 11
        # Each first-round birth belongs to one family. Test every one,
        # including those not used to distinguish the three relations.
        deletions = Counter()
        for knot, family in born_in[0].items():
            cut_words = image(rows[:knot] + rows[knot + 1:], carriers)
            free = [list(k) for k in four if len({project(word, k) for word in cut_words}) == 1 << len(k)]
            key = (family, tuple(tuple(row) for row in free))
            deletions[key] += 1
        result["first-round law deletions and the four-place relations they free"] = [
            {"birth family": family, "relations freed": freed, "laws": count}
            for (family, freed), count in sorted(deletions.items())]
        assert all(len(freed) == 1 for _, freed in deletions)
    else:
        assert len(result["next layer on node with children"]["class facts"]) == 7
        assert sum(not fact["single readers"] for fact in result["next layer on node with children"]["class facts"]) == 2
    if not pilot:
        assert all(value > 12 for value in minima) and local == {0: len(system.supports)}
    return result


def generation_certificate(rounds, pilot):
    system = three_split_rings(5)
    families, _ = family_distances(system)
    assert len(families) == 3
    lineage = {knot: i for i, family in enumerate(families) for knot in family}
    source = defaultdict(list)
    for knot, seq in loose_distinctions(system).items():
        source[lineage[knot]].extend(seq)
    cohorts = [source]
    born_in = []
    milestones = [[len(system.supports), len(system.holders)]]
    for _ in range(rounds):
        lineage, fresh = grow(system, lineage)
        cohorts.append(fresh)
        born_in.append(lineage)
        milestones.append([len(system.supports), len(system.holders)])
    carriers = [set(group[family]) for group in cohorts for family in range(3)]
    assert len(set.union(*carriers)) == sum(map(len, carriers))
    rows = [subset_mask(seq) for seq in system.supports]
    words = image(rows, carriers)
    assert len(words) == 4
    relations = minimal_relations(words, len(carriers))
    counts = Counter(map(len, relations))
    assert counts == {2: 3 * rounds * (rounds + 1) // 2, 3: (rounds + 1) ** 3}
    examples = [tuple(sorted(i + (3 if selected == i else 0) for i in range(3))) for selected in range(3)]
    assert all(group in relations for group in examples)
    measured = {group: sorted({project(word, group) for word in words}) for group in examples}
    checks = [canonical_check(measured[group], len(group)) for group in examples]
    assert all(all(row) for row in checks)
    freed = Counter()
    for knot, family in born_in[0].items():
        cut_words = image(rows[:knot] + rows[knot + 1:], carriers)
        free = tuple(i for i, group in enumerate(examples) if len({project(word, group) for word in cut_words}) == 8)
        assert free == (family,)
        freed[(family, free)] += 1
    adj = system.incidence()
    minima = [shortest_mark_change(adj, support) for support in carriers]
    local = local_class_counts(adj, 12)
    if not pilot:
        assert minima == [13] * len(carriers) and local == {0: len(system.supports)}
    nonzero_weights = [word.bit_count() for word in words if word]
    assert len(set(nonzero_weights)) == 1
    return {"start families": [sorted(group) for group in families],
            "knots and distinctions through rounds": milestones,
            "place order": "Three starting family carriers, then three fresh family carriers per generation.",
            "disjoint physical carriers": [sorted(seq) for seq in carriers],
            "allowed words": words, "minimal relations by size": dict(counts),
            "three triples in first-round family order": [
                {"places": group, "allowed words": measured[group], "canonical check for each contact": check}
                for group, check in zip(examples, checks)],
            "pairwise shared places": [sorted(set(a) & set(b)) for a, b in itertools.combinations(examples, 2)],
            "first-round law deletions": [
                {"birth family": family, "freed triples": altered, "laws": count}
                for (family, altered), count in sorted(freed.items())],
            "least changes": minima, "single-knot class dimension histogram at scale twelve": local,
            "weights of nonzero second-layer changes": nonzero_weights,
            "class dimension under all least changes": len(row_basis(words)) -
            len(row_basis(word for word in words if word.bit_count() == min(nonzero_weights)))}


def small_control():
    system, _ = source_rings(1, 3)
    rows = [subset_mask(seq) for seq in system.supports]
    words = [word for word in range(1 << len(system.holders)) if all(not parity(word, law) for law in rows)]
    adj = system.incidence()
    checked = 0
    fixed = 0
    for mask in range(1, 1 << len(system.holders)):
        literal = min((word.bit_count() for word in words if parity(word, mask)), default=None)
        marked = {i for i in range(len(system.holders)) if mask >> i & 1}
        assert shortest_mark_change(adj, marked) == literal
        checked += 1
        fixed += literal is None
    local = {}
    for scale in (2, 3, 4):
        histogram = Counter()
        for support in system.supports:
            all_reads = row_basis(project(word, support) for word in words)
            small_reads = row_basis(project(word, support) for word in words if word.bit_count() <= scale)
            histogram[len(all_reads) - len(small_reads)] += 1
        assert histogram == local_class_counts(adj, scale)
        local[scale] = dict(histogram)
    assert any(dim > 0 for dim in local[2]) and local[4] == {0: 3}
    return {"start": "One ring of three knots, two loose distinctions each.",
            "allowed assignments": len(words), "parities whose minimum was checked literally": checked,
            "fixed parities among them": fixed, "literal single-knot class dimensions by scale": local}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (2 << 30, 2 << 30))
    tasks = [(three_rings_of_four, 1 if args.pilot else 5), (six_rings_of_five, 2 if args.pilot else 5)]
    outcome = {builder.__name__: certificate(builder, rounds, args.pilot) for builder, rounds in tasks}
    outcome["three_rings_of_five_with_every_generation"] = generation_certificate(1 if args.pilot else 4, args.pilot)
    control = small_control()
    if args.pilot:
        print({key: row["knots and distinctions through rounds"][-1] for key, row in outcome.items()})
    else:
        outcome["literal control"] = control
        (HERE / "natural_places.json").write_text(json.dumps(outcome, indent=2) + "\n")


if __name__ == "__main__":
    main()
