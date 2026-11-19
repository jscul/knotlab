"""Compare named scalar continuations of the complementary L and M caps."""

from collections import Counter, defaultdict, deque
from functools import lru_cache
from hashlib import sha256
from itertools import chain, combinations, permutations, product
import json
from pathlib import Path
from runpy import run_path

import numpy as np


PROOFS = Path(__file__).resolve().parents[2]
STEM = "VARIABLE-OUTPUT-READER-20261118-001"


def source(branch, file):
    return next((PROOFS / (STEM + branch)).glob("*/" + file))


native = run_path(str(source("C", "check_gluing.py")))
incidence = native["incidence"]
legal = native["legal_parents"]
frontier = run_path(str(source("J", "frontier.py")))["old"]
isometry = run_path(str(source("A", "check_classes.py")))
short_reader = run_path(str(source("I", "fixtures.py")))


def roots(branch):
    if branch == "M":
        entry = json.loads(source("M", "examples.json").read_text())["first_complement"]
        operands = entry["chosen"]
        base = entry["common_prefix"]
    else:
        entry = json.loads(source("L", "empty_witness.json").read_text())
        operands = [item["operands"] for item in entry["final_joins"]]
        base = entry["common_prefix"]
    prefix = tuple(map(tuple, base))
    out = [(*prefix, (*p, 30, 31)) for p in operands]
    for rows in out:
        native["replay"](rows)
    return out


def graph_and_labels(rows):
    holders, neighbors = incidence(rows)
    n = len(rows)
    ordered = sorted(holders, key=lambda bit: (*((holders[bit] + [n])[:2]), bit))
    graph = tuple(tuple((holders[bit] + [n])[:2]) for bit in ordered)
    return graph, ordered


@lru_cache(maxsize=None)
def structural_matrix(graph):
    """Both shores must be connected, including the wired exterior."""
    n = max(b for _, b in graph)
    width = len(graph)
    adjacent = [0] * (n + 1)
    stars = [0] * n
    for bit, (a, b) in enumerate(graph):
        adjacent[a] |= 1 << b
        adjacent[b] |= 1 << a
        stars[a] |= 1 << bit
        if b < n:
            stars[b] |= 1 << bit
    assert n < 24 and width < 64
    sets = np.arange(1 << (n + 1), dtype=np.uint32)
    near = np.zeros(sets.shape, dtype=np.uint32)
    for i, adj in enumerate(adjacent):
        half = 1 << i
        near[half:2 * half] = near[:half] | adj
    seen = sets & (np.uint32(0) - sets)
    while True:
        expanded = seen | (near[seen] & sets)
        if np.array_equal(seen, expanded):
            break
        seen = expanded
    connected = seen == sets
    words = np.zeros(1 << n, dtype=np.uint64)
    for i, star in enumerate(stars):
        half = 1 << i
        words[half:2 * half] = words[:half] ^ np.uint64(star)
    both_sides = connected[:1 << n] & connected[::-1][:1 << n]
    both_sides[0] = False
    bonds = words[both_sides]
    sizes = np.bitwise_count(bonds)
    table = np.zeros((width, width), dtype=np.uint8)
    remaining = [(1 << width) - 1 - (1 << i) for i in range(width)]
    for k in range(3, width + 1):
        bucket = bonds[sizes == k]
        if len(bucket) == 0:
            continue
        for i, pending in enumerate(remaining):
            if not pending:
                continue
            matches = bucket[(bucket & np.uint64(1 << i)) != 0]
            filled = int(np.bitwise_or.reduce(matches, initial=np.uint64(0))) & pending
            remaining[i] ^= filled
            while filled:
                low = filled & -filled
                table[i, low.bit_length() - 1] = k
                filled ^= low
        if not any(remaining):
            break
    assert not any(remaining) and np.array_equal(table, table.T)
    return table


def pair_table(rows):
    graph, labels = graph_and_labels(rows)
    matrix = structural_matrix(graph)
    positions = np.argsort(labels)
    a, b = np.triu_indices(len(labels), 1)
    return matrix[positions[a], positions[b]].tobytes()


def groups(rows, needed, representative=False):
    holders, neighbors = incidence(rows)
    loose = sorted(b for b, sites in holders.items() if len(sites) == 1)
    if representative:
        loose = sorted({holders[b][0]: b for b in loose}.values())
    for group in combinations(loose, needed):
        if legal([holders[b][0] for b in group], neighbors):
            yield group


def advance(rows, inputs, h):
    width = len(incidence(rows)[0])
    return (*rows, (*inputs, *range(width, width + h)))


def histories(base, steps, representative=False):
    layer = [(base, (), False)]
    for _ in range(steps):
        updated = []
        for rows, trace, used in layer:
            for p in (1, 2, 3):
                for group in groups(rows, p, representative):
                    for h in (2, 3):
                        if (p == 1 and h == 2) or (used and h == 3):
                            continue
                        updated.append((advance(rows, group, h), (*trace, (group, h)), used or h == 3))
        layer = updated
    return layer


def annotations(rows, mark):
    holders, neighbors = incidence(rows)
    parents = [holders[b][0] for b in mark]
    witnesses = [sorted(neighbors[a] & neighbors[b]) for a, b in combinations(parents, 2)]
    return {"mark": mark, "parents": parents, "pair_witnesses": witnesses}


@lru_cache(maxsize=100_000)
def pin_cap(front):
    colors = []
    for i, count in enumerate(front.loose):
        from_retired = sorted((row.bit_count(), row & 1) for row in front.retired if row & (1 << i))
        colors.append((count, front.adjacent[i].bit_count(), front.adjacent[i] & 1, tuple(from_retired)))
    groups = [tuple(i for i in range(1, len(colors)) if colors[i] == color) for color in sorted(set(colors[1:]))]
    orders = ((0, *chain.from_iterable(parts)) for parts in product(*(permutations(g) for g in groups)))
    return min((front.restrict(order), order) for order in orders)


def cap_snapshot(rows):
    users, adj = incidence(rows)
    loose = defaultdict(list)
    for bit, owners in sorted(users.items()):
        if len(owners) == 1:
            loose[owners[0]].append(bit)
    active = (13, *sorted(set(loose) - {13}))
    masks = [sum(1 << i for i, v in enumerate(active) if v in ns) for ns in adj]
    retired = tuple(sorted({r for j, r in enumerate(masks) if j not in active and r.bit_count() >= 2}))
    raw = frontier.Frontier(tuple(len(loose[v]) for v in active), tuple(masks[v] for v in active), retired)
    normal, order = pin_cap(raw)
    return normal, tuple(active[i] for i in order), loose


def cap_step(front, parents, h):
    new = len(front.loose)
    loose = tuple(count - (i in parents) for i, count in enumerate(front.loose))
    adj = tuple(r | (1 << new if i in parents else 0) for i, r in enumerate(front.adjacent))
    retired = (*front.retired, *(adj[i] for i in range(1, new) if not loose[i]))
    retained = (0, *(i for i in range(1, new) if loose[i]), new)
    extended = frontier.Frontier((*loose, h), (*adj, frontier.mask(parents)), retired)
    return pin_cap(extended.restrict(retained))[0]


def cap_roles(base, save_paths=False):
    initial = (cap_snapshot(base)[0], False)
    representatives = {initial: (base, ())}
    todo = deque([initial])
    transitions = Counter()
    roles = Counter()
    first = {}
    witness_depths = Counter()
    ancestors = defaultdict(set)
    successors = defaultdict(list)
    targets = set()
    while todo:
        key = todo.popleft()
        node, used = key
        rows, history = representatives[key]
        actual, sites, loose = cap_snapshot(rows)
        assert actual == node
        parents = [p for p in frontier.possible_parents(node) if all(node.loose[i] for i in p)]
        _, adj = incidence(rows)
        plain = {tuple(g) for p in (1, 2, 3) for g in combinations(range(len(sites)), p)
                 if all(loose[sites[i]] for i in g) and legal([sites[i] for i in g], adj)}
        assert set(parents) == plain
        events = set()
        for group in parents:
            operands = tuple(loose[sites[i]][0] for i in group)
            if used and len(group) == 3:
                details = annotations(rows, operands)
                wits = details["pair_witnesses"]
                live = {"any"}
                if 13 in details["parents"]:
                    live.add("cap_is_holder")
                if any(13 in pair for pair in wits):
                    live.add("cap_is_pair_witness")
                if [13] in wits:
                    live.add("cap_is_sole_pair_witness")
                for kind in sorted(live):
                    events.add(kind)
                    first.setdefault(kind, {"steps": len(history), "trace": history, **details})
            for h in (2, 3):
                if (len(group) == 1 and h == 2) or (used and h == 3):
                    continue
                suffix = cap_step(node, group, h)
                following = (suffix, used or h == 3)
                grown = advance(rows, operands, h)
                assert cap_snapshot(grown)[0] == suffix
                transitions[used, len(group), h] += 1
                ancestors[following].add(key)
                successors[key].append(following)
                if following not in representatives:
                    representatives[following] = (grown, (*history, (operands, h)))
                    todo.append(following)
        roles.update(events)
        if "cap_is_pair_witness" in events:
            witness_depths[len(history)] += 1
            targets.add(key)
    work = deque(targets)
    retained = set(targets)
    while work:
        later = work.popleft()
        prev = ancestors[later] - retained
        retained.update(prev)
        work.extend(prev)
    indegree = {node: len(ancestors[node] & retained) for node in retained}
    sources = deque(node for node in retained if indegree[node] == 0)
    ordered = []
    while sources:
        node = sources.popleft()
        ordered.append(node)
        for later in set(successors[node]) & retained:
            indegree[later] -= 1
            if indegree[later] == 0:
                sources.append(later)
    reverse_trim = {"nodes": len(retained), "removed_by_topological_order": len(ordered)}
    if len(ordered) == len(retained):
        counts = Counter({initial: 1})
        lengths = {initial: 0}
        for node in ordered:
            for later in successors[node]:
                if later in retained:
                    counts[later] += counts[node]
                    lengths[later] = max(lengths.get(later, 0), lengths[node] + 1)
        reverse_trim["group_paths_to_a_witness"] = sum(counts[node] for node in targets)
        reverse_trim["maximum_depth"] = max(lengths[node] for node in targets)
    depth = Counter(used for _, used in representatives)
    result = {"records_before_fourth": depth[False], "records_after_fourth": depth[True],
            "transitions": [[*k, v] for k, v in sorted(transitions.items())],
            "positive_records_by_role": dict(sorted(roles.items())), "first": first,
            "witness_records_by_minimum_depth": dict(sorted(witness_depths.items())),
            "predecessors_of_witness_records": reverse_trim}
    if save_paths:
        return result, retained, targets
    return result


def small_words(rows, limit=5):
    """A remaining p-input h-output step can lower a word's weight by at most p-h."""
    old = set()
    steps = []
    for row in rows:
        p = len(old.intersection(row))
        h = len(row) - p
        steps.append((sum(1 << b for b in row), max(0, p - h)))
        old.update(row)
    loss = sum(k for _, k in steps)
    words = [0]
    for star, change in steps:
        loss -= change
        threshold = limit + loss
        words = [candidate for w in words for candidate in (w, w ^ star) if candidate.bit_count() <= threshold]
    return set(words) - {0}


def linear_basis(words):
    pivots = {}
    for w in words:
        while w:
            i = w.bit_length() - 1
            if i not in pivots:
                pivots[i] = w
                break
            w ^= pivots[i]
    return tuple(pivots.values())


def short_certificate(rows):
    """Force the unique possible support of each qualifying minimum pair."""
    width = len(incidence(rows)[0])
    actual = small_words(rows)
    assert min(w.bit_count() for w in actual) == 3
    table = dict.fromkeys(combinations(range(width), 2), 6)
    for w in actual:
        for pair in combinations(short_reader["bits"](w), 2):
            table[pair] = min(table[pair], w.bit_count())
    shapes = set.union(*(short_reader["cliques"](table, width, k) for k in (3, 4, 5)))
    obligations = defaultdict(set)
    for w in shapes:
        for pair in combinations(short_reader["bits"](w), 2):
            if table[pair] == w.bit_count():
                obligations[pair].add(w)
    assert set(obligations) == {p for p, k in table.items() if k <= 5}
    forced = {next(iter(choices)) for choices in obligations.values() if len(choices) == 1}
    assert forced <= actual
    stars = {sum(1 << b for b in row) for row in rows}
    return len(linear_basis(forced)), len(rows), len(stars - forced)


def all_direct_sources(base, retained, targets):
    by_depth = Counter()
    by_gap = Counter()
    missing_stars = Counter()
    fourth_parent_counts = Counter()
    first_missing = None
    stack = [(base, False, ())]
    while stack:
        rows, used, trace = stack.pop()
        node, active, loose = cap_snapshot(rows)
        if (node, used) in targets:
            rank, n, missing = short_certificate(rows)
            by_depth[len(trace)] += 1
            by_gap[n-rank] += 1
            missing_stars[missing] += 1
            fourth_parent_counts[next(len(p) for p,h in trace if h == 3)] += 1
            if rank != n and first_missing is None:
                first_missing = {"deficit": n-rank, "inputs_and_output_counts": trace}
        for p in frontier.possible_parents(node):
            if not all(node.loose[i] for i in p):
                continue
            inputs = tuple(loose[active[i]][0] for i in p)
            for h in (2, 3):
                if (len(p) == 1 and h == 2) or (used and h == 3):
                    continue
                if (cap_step(node, p, h), used or h == 3) in retained:
                    stack.append((advance(rows, inputs, h), used or h == 3, (*trace, (inputs, h))))
    return {"parent_group_paths_by_depth": dict(sorted(by_depth.items())),
            "paths_by_unforced_rank": dict(sorted(by_gap.items())),
            "paths_by_stars_without_a_unique_pair": dict(sorted(missing_stars.items())),
            "paths_by_fourth_parent_count": dict(sorted(fourth_parent_counts.items())),
            "first_incomplete": first_missing}


def marked_tables(base_left, base_right, event):
    initial_users, _ = incidence(base_left)
    cap_left = base_left[-1]
    cap_right = base_right[-1]
    prefix_users, _ = incidence(base_left[:-1])
    by_holder = {prefix_users[b][0]: b for b in cap_right[:-2]}
    swap = {}
    for b in cap_left[:-2]:
        alternate = by_holder[prefix_users[b][0]]
        swap[b], swap[alternate] = alternate, b
    assert len(swap) == 6 and len(initial_users) == 32
    left, right = base_left, base_right
    for operands, h in event["trace"]:
        left = advance(left, operands, h)
        right = advance(right, tuple(swap.get(b, b) for b in operands), h)
    native["replay"](left)
    native["replay"](right)
    for row, other in zip(left, right, strict=True):
        assert sorted(swap.get(b, b) for b in row) == sorted(other)
    first, second = pair_table(left), pair_table(right)
    width = len(incidence(left)[0])
    indices = tuple(combinations(range(width), 2))
    table, rival = dict(zip(indices, first)), dict(zip(indices, second))
    for rows, full in ((left, table), (right, rival)):
        clipped = dict.fromkeys(indices, 6)
        for w in small_words(rows):
            for pair in combinations(short_reader["bits"](w), 2):
                clipped[pair] = min(clipped[pair], w.bit_count())
        assert clipped == {p: min(k, 6) for p,k in full.items()}
    assert all(table[p] == rival[tuple(sorted(swap.get(b, b) for b in p))] for p in indices)
    diff = [(p,table[p],rival[p]) for p in indices if table[p] != rival[p]]
    matrix = tuple(tuple(0 if a == b else table[tuple(sorted((a, b)))] for b in range(width)) for a in range(width))
    quotient = isometry["Quotient"].make(matrix)
    order, classes, generators = quotient.automorphisms()
    physical = {frozenset(row) for row in left}
    menu = {frozenset(g) for g in groups(left, 3)}
    changing_menu = 0
    changing_stars = 0
    for perm in generators:
        assert isometry["disagreement"](matrix, matrix, perm) is None
        changing_menu += {frozenset(perm[b] for b in g) for g in menu} != menu
        changing_stars += {frozenset(perm[b] for b in g) for g in physical} != physical
    return {"width": width, "entries_checked": len(indices), "identity_disagreements": len(diff),
            "first_K_difference": min((min(a,b) for _,a,b in diff), default=None),
            "example_K_difference": next((r for r in diff if min(r[1:]) == min(min(a,b) for _,a,b in diff)), None),
            "exact_physical_transport": sorted(swap.items()), "legal_triples": sorted(sorted(g) for g in menu),
            "automorphism_order": order, "quotient_automorphisms": classes, "generators": len(generators),
            "nonidentity_generator_images": [[[i,j] for i,j in enumerate(g) if i != j] for g in generators],
            "generators_changing_menu": changing_menu, "generators_changing_stars": changing_stars,
            "left_K_digest": sha256(first).hexdigest(), "right_K_digest": sha256(second).hexdigest()}


def fixed_names(branch, sides, depth):
    by_table = []
    records = []
    for base in sides:
        grouped = defaultdict(list)
        count = 0
        positive = 0
        for rows, trace, extra in histories(base, depth):
            if not extra:
                continue
            count += 1
            menu = frozenset(groups(rows, 3))
            positive += bool(menu)
            grouped[pair_table(rows)].append((trace, menu))
        by_table.append(grouped)
        records.append({"histories": count, "positive": positive, "distinct_named_tables": len(grouped)})
    matches = []
    for table in by_table[0].keys() & by_table[1].keys():
        for left_trace, left_menu in by_table[0][table]:
            for right_trace, right_menu in by_table[1][table]:
                matches.append({"left": left_trace, "right": right_trace,
                                "left_menu": sorted(left_menu), "right_menu": sorted(right_menu),
                                "K_digest": sha256(table).hexdigest()})
    matches.sort(key=lambda case: (case["left"], case["right"]))
    return {"branch": branch, "steps": depth, "side_counts": records,
            "all_cross_pairs": records[0]["histories"] * records[1]["histories"],
            "exact_identity_matches": matches}


def run():
    answer = {}
    initial = None
    closure = None
    for family in ("L", "M"):
        sides = roots(family)
        base = pair_table(sides[0])
        assert base == pair_table(sides[1]) and len(base) == 496
        if family == "M":
            frozen = json.loads(source("M", "examples.json").read_text())["first_complement"]
            assert base == bytes(d + 1 for d in frozen["full_distances_row_major"])
        else:
            frozen = json.loads(source("L", "empty_witness.json").read_text())
            assert base == bytes(frozen["K_upper_triangle"])
        current = cap_snapshot(sides[0])[0]
        assert cap_snapshot(sides[1])[0] == current
        if initial is None:
            initial = current
            closure, retained, targets = cap_roles(sides[0], save_paths=True)
            trim = closure["predecessors_of_witness_records"]
            assert trim["removed_by_topological_order"] == trim["nodes"]
        else:
            assert current == initial
        answer[family] = {"width_32_K_digest": sha256(base).hexdigest(),
                          "fixed_named_comparisons": [fixed_names(family, sides, d) for d in (1, 2)]}
        # Rebuild witness input names with the same ordinary holder path on this exact prefix.
        traces = {}
        template = roots("L")[0]
        template_prefix, _ = incidence(template[:-1])
        this_prefix, _ = incidence(sides[0][:-1])
        holder_map = {template_prefix[a][0]: this_prefix[b][0]
                      for a, b in zip(template[-1][:-2], sides[0][-1][:-2], strict=True)}
        for kind, event in closure["first"].items():
            if kind == "any":
                continue
            rows, other = template, sides[0]
            steps = []
            for inputs, h in event["trace"]:
                holders, _ = incidence(rows)
                other_users, _ = incidence(other)
                mapped = tuple(min(bit for bit, sites in other_users.items()
                                   if sites == [holder_map.get(holders[x][0], holders[x][0])]) for x in inputs)
                steps.append((mapped, h))
                rows, other = advance(rows, inputs, h), advance(other, mapped, h)
            other_users, _ = incidence(other)
            mark = tuple(min(bit for bit, sites in other_users.items()
                             if sites == [holder_map.get(parent, parent)]) for parent in event["parents"])
            local = {"steps": len(steps), "trace": steps, **annotations(other, mark)}
            traces[kind] = {**local, **marked_tables(*sides, local)}
        answer[family]["direct_involvement_controls"] = traces
        cases = all_direct_sources(sides[0], retained, targets)
        path_count = closure["predecessors_of_witness_records"]["group_paths_to_a_witness"]
        assert cases["paths_by_unforced_rank"] == {0: path_count}
        answer[family]["all_direct_role_sources"] = cases
    answer["cap_frontier"] = closure
    return answer


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
