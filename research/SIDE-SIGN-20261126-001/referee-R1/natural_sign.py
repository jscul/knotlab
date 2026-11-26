"""An invariant sign on a connected ordinary start and its first round.

Run with --pilot first to time one eighth of the exact assignment range
for each combination of law and stage. The default run counts all words.
The four readouts use the same states and the same weighting in every setting.
"""

import argparse
import gzip
import itertools
import json
import sys
import time
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path


START = (
    ("r", "s", "t"), ("R", "S", "T"),
    ("r", "R", "p"), ("s", "S", "q"),
    ("hA", "a", "p"), ("hB", "b", "q"),
    ("hA", "hB", "z", "w"),
    ("z", "i", "j"), ("w", "k", "l"),
    ("i", "k", "m"), ("j", "l", "m"),
)
READERS = (("a", "hA"), ("b", "hB"))
SIGNS = ("constant", "configuration_orbit", "disagreeing_distinctions")


def incidence(knots):
    holders = defaultdict(set)
    for holder, names in enumerate(knots):
        for name in names:
            holders[name].add(holder)
    neighbors = [set() for _ in knots]
    for holding in holders.values():
        for left, right in itertools.combinations(holding, 2):
            neighbors[left].add(right)
            neighbors[right].add(left)
    return holders, neighbors


def identify_exchange(knots):
    """Exchange the unique two knots satisfying the stated incidence test."""
    holders, neighbors = incidence(knots)
    matches = []
    for left, right in itertools.combinations(range(len(knots)), 2):
        common = neighbors[left]
        if common != neighbors[right]:
            continue
        if all(y not in neighbors[x] for x, y in itertools.combinations(common, 2)):
            matches.append((left, right))
    assert len(matches) == 1, matches
    first, second = matches[0]
    by_holding = defaultdict(list)
    for name, holding in holders.items():
        by_holding[frozenset(holding)].append(name)

    def permute_knot(knot):
        return {first: second, second: first}.get(knot, knot)

    pairs = []
    for name, holding in holders.items():
        transported = frozenset(map(permute_knot, holding))
        if transported != holding:
            images = by_holding[transported]
            assert len(images) == 1
            image = images[0]
            if name < image:
                pairs.append((name, image))
    moves = {name: image for pair in pairs for name, image in (pair, pair[::-1])}
    for knot, names in enumerate(knots):
        assert {moves.get(name, name) for name in names} == set(knots[permute_knot(knot)])
    return matches[0], sorted(pairs)


def only_birth(knots):
    """Check that the structure funds exactly one maximal group and no offshoot."""
    holders, neighbors = incidence(knots)
    loose = defaultdict(list)
    for name, holding in holders.items():
        if len(holding) == 1:
            loose[next(iter(holding))].append(name)
    live = tuple(sorted(loose))
    pairs = {pair for pair in itertools.combinations(live, 2)
             if neighbors[pair[0]] & neighbors[pair[1]]}
    valid = []
    for size in range(3, len(live) + 1):
        for group in itertools.combinations(live, size):
            if all(pair in pairs for pair in itertools.combinations(group, 2)):
                if not set.intersection(*(neighbors[knot] for knot in group)):
                    valid.append(frozenset(group))
    groups = [group for group in valid if not any(group < other for other in valid)]
    uncovered = [p for p in pairs if not any(set(p) <= group for group in groups)]
    assert len(groups) == 1 and not uncovered
    parents = sorted(groups[0])
    assert parents == list(live) and all(len(loose[knot]) == 1 for knot in live)
    return tuple(sorted(loose[knot][0] for knot in parents))


def encode_fraction(x):
    return str(Fraction(x))


def measurement(tables, squared):
    correlations = []
    probabilities = []
    for counts in tables:
        weights = [n * n for n in counts] if squared else counts
        total = sum(weights)
        if not total:
            return {"undefined_contexts": [index for index, table in enumerate(tables)
                                            if not sum(n * n if squared else n for n in table)]}
        row = [Fraction(n, total) for n in weights]
        probabilities.append(row)
        correlations.append(row[0] - row[1] - row[2] + row[3])
    alice = [row[2] + row[3] for row in probabilities]
    bob = [row[1] + row[3] for row in probabilities]
    score = correlations[0] + correlations[1] + correlations[2] - correlations[3]
    return {
        "correlations": list(map(encode_fraction, correlations)),
        "absolute_chsh": encode_fraction(abs(score)),
        "nonnegative": all(value >= 0 for row in probabilities for value in row),
        "fair": all(value == Fraction(1, 2) for value in alice + bob),
        "nonsignalling": alice[0] == alice[1] and alice[2] == alice[3]
                         and bob[0] == bob[2] and bob[1] == bob[3],
        "probabilities": [list(map(encode_fraction, row)) for row in probabilities],
    }


def count(knots, law, pilot):
    names = sorted(set().union(*map(set, knots)))
    positions = {name: place for place, name in enumerate(names)}
    masks = [sum(1 << positions[name] for name in knot) for knot in knots]
    exchanged, pairs = identify_exchange(knots)
    pair_masks = [sum(1 << positions[name] for name in pair) for pair in pairs]
    a_names, b_names = READERS
    readings = [(positions[a], positions[b]) for a in a_names for b in b_names]
    tables = {sign: [[0] * 4 for _ in readings] for sign in SIGNS}
    signs = {sign: Counter() for sign in SIGNS}
    allowed = fixed = 0
    limit = 1 << (len(names) - (3 if pilot else 0))
    projections = Counter()
    values_seen = [0 for _ in names]
    orbit_member_changes = 0
    # All four marks must be fixed by the recovered permutation for the
    # alternating projection to remove each complete reading cell.
    assert set(sum(READERS, ())).isdisjoint(name for pair in pairs for name in pair)
    start = time.monotonic()
    for state in range(limit):
        if law == "parity":
            if any((state & mask).bit_count() % 2 for mask in masks):
                continue
        elif any((state & mask) in (0, mask) for mask in masks):
            continue
        allowed += 1
        disagreed = [mask for mask in pair_masks if 0 < (state & mask) < mask]
        moved = len(disagreed)
        image = state
        for mask in disagreed:
            image ^= mask
        orbit_member_changes += moved != sum(0 < (image & mask) < mask for mask in pair_masks)
        fixed += not moved
        outcomes = [2 * ((state >> a) & 1) + ((state >> b) & 1) for a, b in readings]
        for sign_name, coefficient in zip(SIGNS, (1, 1 if not moved else -1, (-1) ** moved)):
            signs[sign_name][coefficient] += 1
            for table, outcome in zip(tables[sign_name], outcomes):
                table[outcome] += coefficient
        projection = tuple((state >> positions[name]) & 1 for name in ("hA", "hB", "p", "q"))
        projections[projection] += 1
        for place in range(len(names)):
            values_seen[place] |= 1 << ((state >> place) & 1)
    elapsed = time.monotonic() - start
    result = {
        "distinctions": names, "knots": len(knots), "tested_words": limit,
        "allowed": allowed, "fixed": fixed, "exchange_knot_indices": list(exchanged),
        "exchanged_distinctions": pairs, "orbit_member_signature_changes": orbit_member_changes,
        "each_distinction_takes_both_values": all(values == 3 for values in values_seen),
        "projected_counts_hA_hB_p_q": {"".join(map(str, key)): n
                                      for key, n in sorted(projections.items())},
        "results": {sign: {
            "sign_counts": dict(sorted(signs[sign].items())),
            "signed_outcome_sums": tables[sign],
            "linear": measurement(tables[sign], False),
            "sum_then_square": measurement(tables[sign], True),
        } for sign in SIGNS},
    }
    if pilot:
        return {"tested_words": limit, "allowed": allowed, "elapsed_seconds": round(elapsed, 4),
                "estimated_full_seconds": round(elapsed * 8, 3)}
    assert orbit_member_changes == 0
    return result


def parity_forms(knots, places, extra=()):
    """Classes of the coordinate functionals modulo the parity equations."""
    basis = {}
    def reduce(mask):
        for pivot in sorted(basis, reverse=True):
            if (mask >> pivot) & 1:
                mask ^= basis[pivot]
        return mask
    for row in itertools.chain(knots, extra):
        value = reduce(sum(1 << places[name] for name in row))
        if value:
            basis[value.bit_length() - 1] = value
    return 1 << (len(places) - len(basis)), {name: reduce(1 << i) for name, i in places.items()}


def pair_counts(size, u, v):
    return [size * (1 + left * (u == 0) + right * (v == 0) + left * right * (u == v)) // 4
            for left in (1, -1) for right in (1, -1)]


def lift_pools(holders, shared, perm, lift):
    import networkx as nx

    moved = {k for k in range(len(perm)) if perm[k] != k}
    sigma = {}
    for holding, values in shared.items():
        other = tuple(sorted(perm[k] for k in holding))
        images = list(shared[other])
        assert len(images) == len(values)
        if holding == other and lift == "maximal":
            for index in range(1, len(images), 2):
                images[index - 1], images[index] = images[index], images[index - 1]
        sigma.update(zip(values, images))
    side_graph = nx.Graph()
    side_graph.add_nodes_from(moved)
    for holding, names in shared.items():
        if len(holding) == 2 and moved.issuperset(holding) and any(sigma[d] != d for d in names):
            side_graph.add_edge(*holding)
    components = list(nx.connected_components(side_graph))
    if len(components) == 2 and perm[next(iter(components[0]))] in components[1]:
        pools = [sorted(name for name, h in holders.items() if h <= side) for side in components]
        return sigma, pools, "two"
    ds = sorted(d for d in sigma if d != sigma[d])
    kind = "one" if any(perm[next(iter(c))] in c for c in components) else "several"
    return sigma, [ds, ds], kind


def stage_involutions(knots):
    import networkx as nx
    from networkx.algorithms.isomorphism import GraphMatcher

    holders, _ = incidence(knots)
    shared = defaultdict(list)
    for name, holding in sorted(holders.items()):
        shared[tuple(sorted(holding))].append(name)
    graph = nx.Graph()
    for k, support in enumerate(knots):
        graph.add_node(k, color=(len(support), len(shared.get((k,), ()))))
    for holding, names in shared.items():
        if len(holding) == 2:
            graph.add_edge(*holding, multiplicity=len(names))
    matcher = GraphMatcher(graph, graph, node_match=lambda a, b: a == b, edge_match=lambda a, b: a == b)
    for perm in matcher.isomorphisms_iter():
        moved = {k for k in graph if perm[k] != k}
        if not moved or any(perm[perm[k]] != k for k in moved):
            continue
        for lift in ("minimal", "maximal"):
            yield perm, lift, *lift_pools(holders, shared, perm, lift)


def census_stage(knots):
    holders, _ = incidence(knots)
    places = {name: rank for rank, name in enumerate(sorted(holders))}
    c_size, c_form = parity_forms(knots, places)
    n_placements = n_swaps = 0
    for perm, lift, sigma, pools, kind in stage_involutions(knots):
        n_swaps += 1
        if min(map(len, pools)) < 2:
            continue
        extra = [(d, image) for d, image in sigma.items() if d < image]
        f_size, f_form = parity_forms(knots, places, extra)
        sums = {}
        for a, b in itertools.product(*pools):
            if holders[a] & holders[b]:
                continue
            c = pair_counts(c_size, c_form[a], c_form[b])
            fixed = pair_counts(f_size, f_form[a], f_form[b])
            sums[a, b] = [2 * y - x for x, y in zip(c, fixed)]
        for aa in itertools.combinations(pools[0], 2):
            for bb in itertools.combinations(pools[1], 2):
                pairs = list(itertools.product(aa, bb))
                if any(pair not in sums for pair in pairs):
                    continue
                n_placements += 1
                raw = [sums[pair] for pair in pairs]
                for mode, squared in (("R1", False), ("R2", True)):
                    cells = [[x * x for x in row] for row in raw] if squared else raw
                    z = [sum(row) for row in cells]
                    if not z[0] or len(set(z)) != 1 or any(x * z[0] < 0 for row in cells for x in row):
                        continue
                    ma = [row[2] + row[3] for row in cells]
                    mb = [row[1] + row[3] for row in cells]
                    if ma[0] != ma[1] or ma[2] != ma[3] or mb[0] != mb[2] or mb[1] != mb[3]:
                        continue
                    e = [row[0] - row[1] - row[2] + row[3] for row in cells]
                    score = max(abs(sum(e) - 2 * val) for val in e)
                    if score > 2 * abs(z[0]):
                        both_readings = {}
                        for label, sq in (("R1", False), ("R2", True)):
                            q = [[n*n for n in row] for row in raw] if sq else raw
                            normals = [sum(row) for row in q]
                            both_readings[label] = measurement(raw, sq)
                            both_readings[label]["normalizers"] = normals
                        # Test constancy of the orbit sign on the four-read fibers.
                        # The zero fiber meets Fix. All fibers of the linear read
                        # have the same kernel and Fix is a subspace.
                        mark_zero = [(d,) for d in aa + bb]
                        zero_size, _ = parity_forms(knots, places, mark_zero)
                        fixed_zero_size, _ = parity_forms(knots, places, extra + mark_zero)
                        return n_swaps, n_placements, {
                            "knots": knots, "involution": [perm[k] for k in range(len(knots))],
                            "lift": lift, "swapped_distinctions": extra, "sides": kind, "reader_pools": pools,
                            "readers": [aa, bb], "c_size": c_size, "f_size": f_size,
                            "signed_outcome_sums": raw, "first_passing_reading": mode,
                            "maximum_chsh": encode_fraction(Fraction(score, abs(z[0]))),
                            "four_mark_zero_fiber": zero_size, "fixed_in_zero_fiber": fixed_zero_size,
                            "on_four_reads_only": zero_size == fixed_zero_size, "readings": both_readings,
                        }
    return n_swaps, n_placements, None


def canonical_growth():
    from importlib.util import module_from_spec, spec_from_file_location
    research = Path(__file__).resolve().parents[2]
    predecessor = research / "FORBID-EDITS-20261126-001"
    spec = spec_from_file_location("ordinary_predecessor", predecessor / "forbid.py")
    engine = module_from_spec(spec)
    sys.modules[spec.name] = engine
    old_argv, sys.argv = sys.argv, [sys.argv[0]]
    try:
        spec.loader.exec_module(engine)
    finally:
        sys.argv = old_argv
    starts = json.loads((predecessor / "starts.json").read_text())
    return engine, starts


def ordinary_census(pilot, record):
    """Post-comparison test, using only the starts and the canonical growth implementation."""
    engine, starts = canonical_growth()
    # Named start chosen as a direct tie control, followed by the census in
    # its stored order. Stop at the first valid excess or 128 census starts.
    order = [3097, 26] + [i for i in range(128) if i != 26]
    if pilot:
        order = order[:2]
    clocks = []
    tested_stages = placements = lifted_swaps = 0
    answer = None
    for ordinal, start in enumerate(order):
        before = time.monotonic()
        knots = engine.supports_of(starts[start])
        for round_number in range(3):
            tested_stages += 1
            swap_count, n, answer = census_stage(knots)
            placements += n
            lifted_swaps += swap_count
            if answer:
                answer.update({"start": start, "round": round_number, "start_specification": starts[start]})
                break
            if round_number < 2:
                knots, _ = engine.grow(knots, "parity", "ordinary", engine.ENGINE)
                if knots is None:
                    break
        clocks.append(time.monotonic() - before)
        if answer:
            break
    data = {"order": "3097, 26, then starts 0 through 127 excluding 26; at most two rounds per start, stop at first eligible excess.",
            "starts_tested": ordinal + 1, "stages_tested": tested_stages,
            "lifted_swaps_visited": lifted_swaps, "eligible_placements_visited": placements, "witness": answer}
    if pilot:
        data["seconds_per_start"] = clocks
        data["estimated_seconds_for_all_129_starts_at_pilot_mean"] = 129 * sum(clocks) / len(clocks)
    if record:
        assert not pilot
        output = Path(__file__).with_suffix(".json")
        existing = json.loads(output.read_text())
        existing["post_comparison_census_test"] = data
        output.write_text(json.dumps(existing, sort_keys=True, indent=2) + "\n")
    print(json.dumps(data, indent=2, sort_keys=True))


def exact_orbit_read(knots, c_size, c_forms, sigma, aa, bb):
    """Independently enumerate configurations by their free parity bits."""
    nonpivots = sorted({i for form in c_forms.values() for i in range(form.bit_length()) if form & (1 << i)})
    assert 1 << len(nonpivots) == c_size
    marks = aa + bb
    pairs = [(d, image) for d, image in sigma.items() if d < image]
    forms = [c_forms[d] for d in marks] + [c_forms[u] ^ c_forms[v] for u, v in pairs]
    # Only these linear functionals can affect a sign or an outcome. Sum
    # their images, retaining the multiplicity of every actual full word.
    images = Counter({0: 1})
    for i in nonpivots:
        action = sum(((form >> i) & 1) << j for j, form in enumerate(forms))
        updated = images.copy()
        for word, multiplicity in images.items():
            updated[word ^ action] += multiplicity
        images = updated
    raw = [[0] * 4 for _ in range(4)]
    fixed = 0
    completions = defaultdict(Counter)
    for image, n in images.items():
        sign = -1 if image >> 4 else 1
        fixed += n if sign == 1 else 0
        completions[image & 15][sign] += n
        for k, (a, b) in enumerate(itertools.product(range(2), range(2, 4))):
            cell = 2 * ((image >> a) & 1) + ((image >> b) & 1)
            raw[k][cell] += sign * n
    assert sum(images.values()) == c_size
    gates = {}
    for mode, sq in (("R1", False), ("R2", True)):
        table = measurement(raw, sq)
        normals = [sum(x*x if sq else x for x in row) for row in raw]
        table["normalizers"] = normals
        assert len(set(normals)) == 1 and normals[0]
        assert table["absolute_chsh"] == "4" and table["nonsignalling"] and table["nonnegative"]
        gates[mode] = table
    return {"full_state_count": c_size, "fixed_state_count": fixed, "readers": [aa, bb],
            "swapped_distinctions": pairs, "signed_outcome_sums": raw, "readings": gates,
            "all_four_marks_sign_counts": {format(word, "04b")[::-1]: dict(sorted(count.items()))
                                           for word, count in sorted(completions.items())},
            "on_four_reads_only": all(len(count) == 1 for count in completions.values())}


def rank_scan(pilot, record):
    """Test the sharp parity condition on the frozen stage and lifted swap index."""
    start_time = time.monotonic()
    engine, starts = canonical_growth()
    archive = Path(__file__).resolve().parent.parent / "census_results.jsonl.gz"
    stages = {}
    with gzip.open(archive, "rt") as source:
        for line in source:
            for row in json.loads(line)["result"]["rows"]:
                if row["law"] == "parity":
                    choice = [(item["perm"], item["lift"]) for item in row["classes"]]
                    stages[row["start"], row["round"]] = choice
    index_seconds = time.monotonic() - start_time
    selected = sorted(stages)
    if pilot:
        selected = selected[:64]
    previous_start = None
    tested = swaps = rank_two = 0
    answer = None
    counts = Counter()
    for start, round_number in selected:
        if previous_start != start:
            knots = engine.supports_of(starts[start])
            grown_round = 0
            previous_start = start
        while grown_round < round_number:
            knots, _ = engine.grow(knots, "parity", "ordinary", engine.ENGINE)
            assert knots is not None
            grown_round += 1
        tested += 1
        holders, _ = incidence(knots)
        shared = defaultdict(list)
        for name, h in sorted(holders.items()):
            shared[tuple(sorted(h))].append(name)
        places = {name: rank for rank, name in enumerate(sorted(holders))}
        size, forms = parity_forms(knots, places)
        for permutation, name_lift in stages[start, round_number]:
            swaps += 1
            lift = "minimal" if name_lift == "min" else "maximal"
            sigma, pools, kind = lift_pools(holders, shared, permutation, lift)
            pairs = [(d, image) for d, image in sigma.items() if d < image]
            fsize, ff = parity_forms(knots, places, pairs)
            rank = (size // fsize).bit_length() - 1
            counts[rank] += 1
            if rank != 2:
                continue
            rank_two += 1
            restricted = [{}, {}]
            for side, pool in enumerate(pools):
                for d in pool:
                    if ff[d]:
                        restricted[side].setdefault(ff[d], []).append(d)
            for f in sorted(restricted[0].keys() & restricted[1].keys()):
                left, right = restricted[0][f], restricted[1][f]
                for a1, b1 in itertools.product(left, right):
                    if forms[a1] != forms[b1] or holders[a1] & holders[b1]:
                        continue
                    for a0, b0 in itertools.product(left, right):
                        if len({forms[a1], forms[a0], forms[b0]}) < 3:
                            continue
                        if holders[a0] & holders[b0] or holders[a0] & holders[b1] or holders[a1] & holders[b0]:
                            continue
                        answer = exact_orbit_read(knots, size, forms, sigma, (a0, a1), (b0, b1))
                        assert answer["fixed_state_count"] == fsize
                        answer.update({"start": start, "round": round_number, "start_specification": starts[start],
                                       "knots": knots, "permutation": permutation, "lift": lift, "sides": kind,
                                       "reader_pools": pools})
                        break
                    if answer:
                        break
                if answer:
                    break
            if answer:
                break
        if answer:
            break
    result = {"scope": "Archived parity stages in ascending start and round order, both recorded lifts for each representative when distinct, stop at the first witness.",
              "indexed_stages": len(stages), "stages_tested": tested,
              "lifted_swap_rows_tested": swaps, "fixed_codimension_counts": dict(sorted(counts.items())),
              "fixed_codimension_two": rank_two, "witness": answer}
    if pilot:
        work = time.monotonic() - start_time - index_seconds
        result["index_seconds"] = round(index_seconds, 3)
        result["work_seconds"] = round(work, 3)
        result["estimated_full_seconds_at_pilot_mean"] = round(index_seconds + len(stages) * work/tested, 2)
    if record:
        assert not pilot
        output = Path(__file__).with_suffix(".json")
        existing = json.loads(output.read_text())
        existing["post_comparison_rank_search"] = result
        output.write_text(json.dumps(existing, sort_keys=True, indent=2) + "\n")
    print(json.dumps(result, sort_keys=True, indent=2))


def projected_audit(pilot, record):
    """Check every nested pair of four-bit projection spaces at all archived ranks."""
    then = time.monotonic()
    spaces = {frozenset((0,))}
    for v in range(1, 16):
        spaces |= {space | {x ^ v for x in space} for space in spaces}
    linear = sorted(spaces, key=lambda s: (len(s), sorted(s)))
    assert len(linear) == 67
    subpairs = [(p, q) for p in linear for q in linear if q <= p]
    assert len(subpairs) == 513
    positions = list(itertools.product((0, 1), (2, 3)))
    counts = {}
    for p in linear:
        tables = [[0] * 4 for _ in positions]
        for x in p:
            for j, (a, b) in enumerate(positions):
                tables[j][2*((x >> a) & 1) + ((x >> b) & 1)] += 1
        counts[p] = tables

    def gates(sums, squared):
        tables = [[n*n for n in row] for row in sums] if squared else sums
        z = [sum(row) for row in tables]
        if not all(z):
            return "G0", None
        if any(n*den < 0 for row, den in zip(tables, z) for n in row):
            return "G1", None
        if len(set(z)) != 1:
            return "G2", None
        ma = [row[2] + row[3] for row in tables]
        mb = [row[1] + row[3] for row in tables]
        if ma[0] != ma[1] or ma[2] != ma[3] or mb[0] != mb[2] or mb[1] != mb[3]:
            return "G3", None
        d = [row[0] - row[1] - row[2] + row[3] for row in tables]
        best = Fraction(max(abs(sum(d) - 2*n) for n in d), abs(z[0]))
        return ("hit" if best > 2 else "G4"), best

    archive = json.loads(Path(__file__).with_suffix(".json").read_text())
    ranks = sorted(map(int, archive["post_comparison_rank_search"]["fixed_codimension_counts"]))
    totals = {}
    matching = []
    n_fixed_mark = 0
    for r in ranks:
        checks = {"R1": Counter(), "R2": Counter()}
        considered = 0
        for j, (p, q) in enumerate(subpairs):
            if len(p) > len(q) << r or (pilot and j % 8):
                continue
            considered += 1
            n_fixed_mark += any(all(not ((word >> mark) & 1) for word in p) for mark in range(4))
            # These signed counts are 2^(1-r) U_Q - U_P multiplied by the
            # common positive integer 2^r |P| |Q|.
            sums = [[2*len(p)*nc - (1 << r)*len(q)*np for np, nc in zip(row, frow)]
                    for row, frow in zip(counts[p], counts[q])]
            ties = sum(all(((x >> a) ^ (x >> b)) & 1 == 0 for x in p) for a, b in positions)
            expected = r == 2 and q == frozenset((0, 15)) and ties == 1
            for reading, squared in (("R1", False), ("R2", True)):
                status, best = gates(sums, squared)
                checks[reading][status] += 1
                assert (status == "hit") == expected, (r, p, q, reading, status)
                if expected:
                    assert best == 4
            if expected:
                matching.append({"fixed_codimension": r, "projected_states": sorted(p),
                                 "projected_fixed_states": sorted(q), "cross_ties": ties})
        totals[r] = {"projected_cases": considered,
                     "first_failed_gate_or_hit": {name: dict(counter) for name, counter in checks.items()}}
    result = {"four_bit_subspaces": len(linear), "nested_pairs_before_rank_filter": len(subpairs),
              "tested_cases": sum(row["projected_cases"] for row in totals.values()),
              "cases_with_a_fixed_read_mark": n_fixed_mark, "ranks": ranks, "per_rank": totals,
              "projected_cases_passing_either_reading": matching,
              "criterion_disagreements": 0,
              "interpretation": "The four marks have the same nonzero restriction to the fixed states exactly when Q contains just 0000 and 1111. With fixed codimension two, exactly one pair of marks across the readers must also agree on every allowed state. For the indexed codimensions both readings pass all gates exactly on these cases."}
    if pilot:
        result["elapsed_seconds"] = round(time.monotonic() - then, 4)
        result["estimated_full_seconds"] = round(8*(time.monotonic() - then), 3)
    else:
        assert len(matching) == 4 and result["tested_cases"] == 5472
    if record:
        assert not pilot
        archive["projected_rank_audit"] = result
        Path(__file__).with_suffix(".json").write_text(json.dumps(archive, sort_keys=True, indent=2) + "\n")
    print(json.dumps(result, sort_keys=True, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--census-orbit", action="store_true")
    parser.add_argument("--census-rank", action="store_true")
    parser.add_argument("--projected-audit", action="store_true")
    parser.add_argument("--record-followup", action="store_true")
    args = parser.parse_args()
    if args.projected_audit:
        projected_audit(args.pilot, args.record_followup)
        return
    if args.census_rank:
        rank_scan(args.pilot, args.record_followup)
        return
    if args.census_orbit:
        ordinary_census(args.pilot, args.record_followup)
        return
    birth = only_birth(START)
    assert set(birth) == {"a", "b", "t", "T"}
    # Parity on the inputs is implied. All-equal input assignments exist
    # under NAE. With one child there is no next-round demand from siblings.
    added = {"parity": birth, "not_all_equal": birth + ("fresh",)}
    ledger = {}
    for law in added:
        for stage, knots in (
            ("start", START), ("after_one_round", START + (added[law],)),
        ):
            ledger[(law, stage)] = count(knots, law, args.pilot)
    result = {law: {stage: ledger[law, stage] for stage in ("start", "after_one_round")}
              for law in added}
    if not args.pilot:
        assert ledger["parity", "start"]["allowed"] == ledger["parity", "after_one_round"]["allowed"]
        for stage in ("start", "after_one_round"):
            item = ledger["parity", stage]
            assert item["allowed"] == 4 * item["fixed"]
            for reading in ("linear", "sum_then_square"):
                measured = item["results"]["configuration_orbit"][reading]
                assert measured["absolute_chsh"] == "4" and measured["fair"] and measured["nonnegative"]
                assert measured["nonsignalling"]
        # NAE old states all extend. Exactly the old all-equal input states
        # have one extension, the others have two under the new five-place law.
        old_nae = ledger["not_all_equal", "start"]["allowed"]
        grown_nae = ledger["not_all_equal", "after_one_round"]["allowed"]
        assert old_nae < grown_nae < 2 * old_nae
        result.update({
            "start": START, "readers_in_setting_order": READERS,
            "setting_order": ["00", "01", "10", "11"],
            "outcome_order": ["00", "01", "10", "11"], "first_birth": added,
            "nae_old_words_with_all_equal_birth_inputs": 2 * old_nae - grown_nae,
            "sign_definitions": {
                "constant": "Every allowed configuration gets +1.",
                "configuration_orbit": "Sign of the permutation of the configuration's orbit induced by the involution.",
                "disagreeing_distinctions": "Sign of the involution restricted to the distinctions on which the word differs from its exchanged word.",
            },
            "reading_definitions": {
                "linear": "Divide each signed outcome sum by the total signed sum.",
                "sum_then_square": "Square each signed outcome sum and normalize the four squares in its setting.",
            },
            "scope": "An explicit prescription on one constructed start. Ordinary growth supplies the holdings and allowed configurations. The use of the permutation sign as a weighting and the two probability readings are supplied.",
        })
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
