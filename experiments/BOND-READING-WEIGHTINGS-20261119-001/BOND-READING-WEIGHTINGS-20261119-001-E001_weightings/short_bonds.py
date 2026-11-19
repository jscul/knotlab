"""Sufficient pair certificates from exact short bonds and singleton minima."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from ctypes import CDLL, POINTER, c_int, c_uint8, c_uint64
import fcntl
from functools import cache
from hashlib import sha256
from itertools import combinations, product
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import NamedTemporaryFile, gettempdir

from order_reader import BondIndex, Budget, Group, Stage as ShoreStage, WorkLimit
import networkx as nx

from scale_reader import Stage, bit_indices, insert, minimum_rows, unique_basis


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARTIFACTS = ROOT / "artifacts" / HERE.parent.name / HERE.name
MAX_HALVES = 1_500_000
MAX_MATCHES = 16_000_000
MAX_GROUP_NODES = 100_000
DEFAULT_CUTOFF = 6


@cache
def library():
    source = HERE / "short_bonds.cpp"
    digest = sha256(source.read_bytes()).hexdigest()[:24]
    directory = Path(gettempdir()) / f"prespatial-short-bonds-{os.getuid()}"
    directory.mkdir(mode=0o700, exist_ok=True)
    if directory.is_symlink() or directory.stat().st_uid != os.getuid() or directory.stat().st_mode & 0o077:
        raise RuntimeError("Expected a private per-user kernel cache")
    binary = directory / (digest + ".so")
    with (directory / "compile.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if not binary.exists():
            pending = binary.with_suffix(".building")
            subprocess.run(["c++", "-O3", "-std=c++20", "-shared", "-fPIC", str(source), "-o", str(pending)],
                           check=True)
            os.replace(pending, binary)
    handle = CDLL(str(binary))
    kernel = handle.short_bond_table
    kernel.argtypes = (c_int, c_int, POINTER(c_int), c_int, c_uint64, c_uint64,
                       POINTER(c_uint8), POINTER(c_uint64))
    kernel.restype = c_int
    return handle


def short_table(stage, cutoff=DEFAULT_CUTOFF, *, half_limit=MAX_HALVES, match_limit=MAX_MATCHES):
    """Return exact bundled K(x,y) through cutoff, with cutoff+1 for higher or absent."""
    if not 1 <= cutoff <= 6:
        raise ValueError("Expected a cutoff from one to six")
    if half_limit < 1 or not 0 <= match_limit < (1 << 31):
        raise ValueError("Expected valid subset and bucket-pair budgets")
    size = len(stage.links)
    data = [(a, b, len(bag)) for (a, b), bag in zip(stage.links, stage.bags, strict=True)]
    raw = (c_int * (3 * size))(*(x for link in data for x in link))
    output = (c_uint8 * (size * size))()
    counts = (c_uint64 * 10)()
    status = library().short_bond_table(stage.vertices, size, raw, cutoff, half_limit, match_limit, output, counts)
    features = {"cycle_rank": counts[0], "half_subsets": counts[1], "bucket_pairs": counts[2],
                "whole_candidates": counts[3], "bonds_by_weight": list(counts[4:4 + cutoff])}
    if status == 1:
        raise ValueError("Expected valid connected holder incidence")
    if status:
        features["limit_hit"] = {2: "half_subsets", 3: "bucket_pairs"}[status]
        return None, features
    raw = bytes(output)
    return [raw[i:i+size] for i in range(0, len(raw), size)], features


def feature_group(stage, table, cutoff, prices, membership, group_limit, three=()):
    """Check the entire stabilizer of the capped table, singleton data and fixed end."""
    width = len(stage.names)
    which = [0] * width
    for group, bag in enumerate(stage.bags):
        for x in bag:
            which[x] = group
    fixed = sorted(x for group in stage.fixed for x in stage.bags[group])
    free = sorted(x for group in stage.free for x in stage.bags[group])
    fixed_mask = sum(1 << x for x in fixed)
    third = defaultdict(int)
    three_sets = set(three)
    for a, b, c in three:
        for x, y, z in ((a, b, c), (a, c, b), (b, c, a)):
            third[x, y] |= 1 << z
            third[y, x] |= 1 << z

    # A cell holds both directed bits, so preserving one orientation preserves
    # the other. The orientation is material when prices differ.
    def entry(u, v):
        a, b = which[u], which[v]
        low = min(table[a][b], cutoff + 1)
        value = 4 * low + ((membership[a] >> b) & 1) + 2 * ((membership[b] >> a) & 1)
        if three:
            possible = third[u, v]
            return value, possible & fixed_mask, (possible & ~fixed_mask).bit_count()
        return value

    profiles = {}
    for x in free:
        values = tuple(entry(x, f) for f in fixed)
        if three:
            # Fixed-mark triples are already in values. The entirely movable
            # triples additionally give a count for each movable distinction.
            mobile = sum((third[x, y] & ~fixed_mask).bit_count() for y in free)
            values = (values, mobile)
        profiles[x] = prices[which[x]], values
    cells = defaultdict(list)
    for x in free:
        cells[profiles[x]].append(x)

    features = {"fixed_names": len(fixed), "movable_names": len(free), "profiles": len(cells)}
    if all(stage.permits_transpositions(cell) for cell in cells.values()):
        return True, {**features, "method": "profile_cells"}

    pair = {x: {y: entry(x, y) for y in free} for x in free}

    def twins(x, y):
        if pair[x][y] != pair[y][x] or any(pair[x][z] != pair[y][z] for z in free if z not in (x, y)):
            return False
        if three:
            return all(tuple(sorted(y if z == x else x if z == y else z for z in members)) in three_sets
                       for members in three if (x in members) != (y in members))
        return True

    blocks = []
    for cell in cells.values():
        local = []
        for x in cell:
            for block in local:
                if twins(x, block[0]):
                    block.append(x)
                    break
            else:
                local.append([x])
        blocks.extend(local)

    features["twin_blocks"] = len(blocks)
    for block in blocks:
        swap = stage.unsafe_swap(block)
        if swap is not None:
            a, b = swap
            return False, {**features, "method": "unsafe_feature_twins", "unsafe_feature_map": [[a, b], [b, a]]}

    # Only genuine transposition twins are pooled. Arbitrary maps within any
    # block preserve the equations, and matching blocks lift by fixed ordering.
    labels = [(profiles[b[0]], len(b), pair[b[0]][b[1]] if len(b) > 1 else None) for b in blocks]
    matrix = [[pair[a[0]][b[0]] for b in blocks] for a in blocks]
    budget = Budget(group_limit)
    group = Group(labels, matrix, budget)
    refined = defaultdict(list)
    for i, domain in enumerate(group.domains):
        refined[domain].append(i)
    features.update(refined_cells=group.cells, largest_refined_cell=max(map(len, refined.values()), default=0))
    if all(stage.carries_blocks(blocks, [(cell[0], i), (i, cell[0])])
           for cell in refined.values() for i in cell[1:]):
        return True, {**features, "method": "refined_cells"}

    if three:
        movable = sum(domain for domain in refined if domain.bit_count() > 1)
        checked = compatible = 0
        try:
            for image in group.solutions(list(range(len(blocks))), movable, movable):
                checked += 1
                changes = [(a, b) for a, b in enumerate(image) if a != b]
                mapping = dict((x, y) for a, b in changes for x, y in zip(blocks[a], blocks[b], strict=True))
                if any(tuple(sorted(mapping.get(z, z) for z in members)) not in three_sets for members in three):
                    continue
                compatible += 1
                if not stage.carries_blocks(blocks, changes):
                    named = [[stage.names[x], stage.names[y]] for x, y in sorted(mapping.items())]
                    return False, {**features, "method": "unsafe_feature_permutation", "unsafe_feature_map": named,
                                   "permutations_checked": checked, "three_bond_compatible": compatible}
        except WorkLimit:
            return False, {**features, "method": "feature_group_limit", "permutations_checked": checked,
                           "group_nodes": group_limit}
        return True, {**features, "method": "all_three_bond_permutations_safe", "permutations_checked": checked,
                      "three_bond_compatible": compatible, "group_nodes": group_limit - budget.remaining}

    checked = 0
    try:
        for image in group.generators():
            changes = [(a, b) for a, b in enumerate(image) if a != b]
            assert all(labels[a] == labels[b] for a, b in changes)
            assert all(matrix[a][b] == matrix[image[a]][image[b]] for a in range(len(blocks))
                       for b in range(len(blocks)) if a != b)
            checked += 1
            if not stage.carries_blocks(blocks, changes):
                mapping = [[stage.names[x], stage.names[y]] for a, b in changes
                           for x, y in zip(blocks[a], blocks[b], strict=True)]
                return False, {**features, "method": "unsafe_feature_generator", "unsafe_feature_map": mapping,
                               "generators_checked": checked, "group_nodes": group_limit - budget.remaining}
    except WorkLimit:
        return False, {**features, "method": "feature_group_limit", "generators_checked": checked,
                       "group_nodes": group_limit}
    return True, {**features, "method": "all_feature_generators_safe", "generators_checked": checked,
                  "group_nodes": group_limit - budget.remaining}


def short_pair_certificate(stars, *, cutoff=DEFAULT_CUTOFF):
    """Certify sufficiency at order two when `certified` is true.

    An unsafe map of the coarser feature graph or a work cap leaves the full
    pair question open. This API does not establish a lower bound on order.
    """
    stage = Stage(stars)
    table, counts = short_table(stage, cutoff)
    if table is None:
        return {"certified": False, "cutoff": cutoff, "method": "bond_work_limit", "features": counts}
    prices, membership = minimum_rows(stage)
    certified, details = feature_group(stage, table, cutoff, prices, membership, MAX_GROUP_NODES)
    return {"certified": certified, "cutoff": cutoff, "features": counts, **details}


def three_bonds(stage):
    """Every weight-three bond is a zero-syndrome triple of nonzero columns."""
    syndrome = stage.syndromes
    return [members for members in combinations(range(len(syndrome)), 3)
            if all(syndrome[x] for x in members)
            and (syndrome[members[0]] ^ syndrome[members[1]] ^ syndrome[members[2]]) == 0]


def three_certificate(stage, table, prices, membership):
    bonds = three_bonds(stage)
    basis, _, _ = unique_basis(stage, prices, membership)
    for members in bonds:
        insert(basis, sum(1 << x for x in members))
    details = {"three_bonds": len(bonds), "rank": len(basis), "target_rank": len(stage.basis)}
    if len(basis) == len(stage.basis):
        return {"certified": True, "method": "three_bond_span", **details}
    safe, certificate = feature_group(stage, table, 6, prices, membership, MAX_GROUP_NODES, bonds)
    return {"certified": safe, **details, **certificate}


def opposite_spokes(stage, mapping):
    """Find an exact full-pair ambiguity supported on five core distinctions.

    With connected remainder Q and terminal cut one, the opposite spokes
    have equal internal pair rows. Every mixed pair transfers by moving the
    two private holders, preserving the Q cut and both connected shores.
    """
    if len(mapping) != 2 or mapping[0] != list(reversed(mapping[1])):
        return None
    x, y = (stage.names.index(r[0]) for r in mapping)
    for (a, c), (b, d) in product((stage.ends[x], stage.ends[x][::-1]),
                                   (stage.ends[y], stage.ends[y][::-1])):
        if len({a, b, c, d}) != 4 or max(a, b, c, d) >= len(stage.stars):
            continue
        if set(stage.graph[c]) != {a, b, d} or set(stage.graph[d]) != {a, b, c}:
            continue
        if stage.graph.has_edge(a, b):
            continue
        core = {a, b, c, d}
        internal = {tuple(ends): j for j, ends in enumerate(stage.links) if set(ends) <= core}
        if len(internal) != 5 or any(len(stage.bags[j]) != 1 or j in stage.fixed for j in internal.values()):
            continue
        remainder = stage.graph.subgraph(set(stage.graph) - {c, d})
        if not nx.is_connected(remainder):
            continue
        bridges_at_poles = [[stage.names[i] for i, ends in enumerate(stage.ends)
                             if pole in ends and c not in ends and d not in ends] for pole in (a, b)]
        if all(len(incident) != 1 for incident in bridges_at_poles):
            continue
        shared = lambda u, v: stage.bags[internal[tuple(sorted((u, v)))]][0]
        source_triple = (x, shared(b, c), shared(c, d))
        image_triple = (y, *source_triple[1:])
        assert set(source_triple) == set(bit_indices(stage.stars[c]))
        assert stage.syndromes[image_triple[0]] ^ stage.syndromes[image_triple[1]] ^ stage.syndromes[image_triple[2]]
        return {"method": "opposite_spokes_terminal_cut_one", "poles": [a, b], "middle_holders": [c, d],
                "remainder_attachments": bridges_at_poles, "swap": mapping,
                "three_mark_witness": [sorted(stage.names[z] for z in marks)
                                       for marks in (source_triple, image_triple)]}
    return None


def independent_control(stars, stage, table, cutoff, witness=None):
    """Check all entries and every bond count by an independent shore sweep."""
    independent = ShoreStage(stars)
    assert tuple(stage.links) == independent.edges
    bonds = BondIndex(independent)
    size = len(bonds.columns)
    expected = [[cutoff + 1] * size for _ in range(size)]
    for a, b in combinations(range(size), 2):
        weight = bonds.minimum(bonds.columns[a] & bonds.columns[b])
        expected[a][b] = expected[b][a] = min(weight, cutoff + 1) if weight > 0 else cutoff + 1
    for a, mask in enumerate(bonds.columns):
        weight = bonds.minimum(mask)
        expected[a][a] = min(weight, cutoff + 1) if weight > 0 else cutoff + 1
    assert table == list(map(bytes, expected))
    if witness is not None:
        a, b = (independent.of[stage.names.index(x)] for x, _ in witness["swap"])
        for c in range(size):
            if c in (a, b):
                continue
            col = bonds.columns[c]
            assert bonds.minimum(bonds.columns[a] & col) == bonds.minimum(bonds.columns[b] & col)
        assert bonds.minimum(bonds.columns[a]) == bonds.minimum(bonds.columns[b])
    counts = Counter(bonds.costs)
    return [counts[w] for w in range(1, cutoff + 1)]


@cache
def population():
    index = json.loads((ARTIFACTS / "sample_shape_index.json").read_text())
    baseline = json.loads((ARTIFACTS / "pair_certificates.json").read_text())
    cases = {str(row["shape"]): row for row in index["shapes"] if baseline[str(row["shape"])]["hi"] > 2}
    assert len(cases) == 34 and sum(len(row["observations"]) for row in cases.values()) == 59
    assert all(baseline[key]["lo"] == 2 for key in cases)
    return cases


def cases():
    for key, row in population().items():
        yield key, row


def run(case_id, row):
    stage = Stage(row["stars"])
    evidence = {}
    extension = {}
    table, counts = short_table(stage)
    if table is not None:
        prices, membership = minimum_rows(stage)
        for cutoff in (5, 6):
            certified, details = feature_group(stage, table, cutoff, prices, membership, MAX_GROUP_NODES)
            evidence[str(cutoff)] = {"certified": certified, **details}
        assert not evidence["5"]["certified"] or evidence["6"]["certified"]
        if not evidence["6"]["certified"]:
            witness = evidence["6"].get("unsafe_feature_map", [])
            lower = opposite_spokes(stage, witness)
            extension = {"full_pair_failure": lower,
                         "third_order": three_certificate(stage, table, prices, membership)}
            assert extension["third_order"]["three_bonds"] == counts["bonds_by_weight"][2]
        if stage.vertices <= 18:
            assert independent_control(row["stars"], stage, table, 6,
                                       extension.get("full_pair_failure")) == counts["bonds_by_weight"]
            counts["whole_shore_control"] = True
    else:
        for cutoff in (5, 6):
            evidence[str(cutoff)] = short_pair_certificate(row["stars"], cutoff=cutoff)
    return {"shape": int(case_id), "J": row["J"], "n": row["n"], "observations": len(row["observations"]),
            "counts": counts, "results": evidence, **extension}


def controls():
    path = (ROOT / "artifacts/GROWN-END-MEET-ONCE-20261119-001/"
            "GROWN-END-MEET-ONCE-20261119-001-E001_rounds/two_histories.json")
    witness = json.loads(path.read_text())["seven_at_round_one"]
    stage = witness["stages"][1]
    # In this known failure there is a full-pair automorphism which changes the
    # later pair table. Every coarser feature graph still admits that map.
    refused = short_pair_certificate(stage)
    assert not refused["certified"] and refused["method"].startswith("unsafe")
    positive = [[0, 1, 2], [0, 3, 4]]
    series = [[0, 1], [1, 2], [2, 3], [3, 4]]
    cases = {"parallel_loose_control": positive, "series_control": series, "known_pair_failure": stage}
    results = {}
    for name, stars in cases.items():
        data = Stage(stars)
        table, counted = short_table(data)
        assert table is not None
        assert independent_control(stars, data, table, 6) == counted["bonds_by_weight"]
        results[name] = counted
    assert short_pair_certificate(positive)["certified"]
    capped = short_table(Stage(positive), half_limit=1)
    assert capped[0] is None and capped[1]["limit_hit"] == "half_subsets"
    results["limit_control"] = capped[1]
    results["known_pair_failure"]["feature_test"] = refused
    return results


def collect(run_dir, output):
    sys.path.insert(0, str(ROOT / "scripts"))
    from longrun import load_results

    records = load_results(run_dir)
    assert set(records) == set(population()) and all(row["status"] == "ok" for row in records.values())
    results = [records[key]["result"] for key in population()]
    summary = {}
    for cutoff in ("5", "6"):
        solved = [row for row in results if row["results"][cutoff]["certified"]]
        summary[cutoff] = {"new_exact_twos": len(solved), "observations_resolved": sum(r["observations"] for r in solved),
                           "remaining_shapes": [r["shape"] for r in results if r not in solved]}
    exact_threes = [row for row in results if row.get("full_pair_failure") and row["third_order"]["certified"]]
    summary["order_three"] = {"shapes": [row["shape"] for row in exact_threes],
                              "observations": sum(row["observations"] for row in exact_threes),
                              "full_pair_failures": [row["shape"] for row in results if row.get("full_pair_failure")]}
    payload = {"baseline_unresolved_shapes": len(results), "baseline_unresolved_observations": 59,
               "verdicts": summary, "controls": controls(), "cases": results}
    output.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(mode="w", encoding="ascii", dir=output.parent, delete=False,
                            prefix="short_bonds_pending_") as pending:
        json.dump(payload, pending, indent=2, sort_keys=True)
        pending.write("\n")
    Path(pending.name).replace(output)
    return summary


def main():
    parser = ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("controls")
    one = sub.add_parser("shape")
    one.add_argument("ids", nargs="+")
    combine = sub.add_parser("collect")
    combine.add_argument("run_dir", type=Path)
    combine.add_argument("--output", type=Path, default=ARTIFACTS / "short_bonds.json")
    args = parser.parse_args()
    if args.command == "controls":
        result = controls()
    elif args.command == "collect":
        result = collect(args.run_dir, args.output)
    else:
        result = [run(key, population()[key]) for key in args.ids]
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
