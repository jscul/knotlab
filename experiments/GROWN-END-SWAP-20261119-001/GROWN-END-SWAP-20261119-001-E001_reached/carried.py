"""Exact old-map extensions on the archived GROWN-PAIR reached groups."""

from collections import Counter, defaultdict
from functools import cache
import gzip
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations, permutations, product
import json
from math import factorial, prod
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

import networkx as nx

ROOT = Path(__file__).resolve().parents[3]
GROWN = ROOT / "artifacts/GROWN-PAIR-20261119-001A/GROWN-PAIR-20261119-001A-E001_pairs"
EXPERIMENT = ROOT / "experiments/CENSUS-READ-20261118-001A/CENSUS-READ-20261118-001A-E001_census"
N = ROOT / "proofs/VARIABLE-OUTPUT-READER-20261118-001N/VARIABLE-OUTPUT-READER-20261118-001N-P001_fourth_at_the_parents"
GS = ROOT / "research/GROW-SMALL-20261119-001/referee-R1/job_growsmall.py"
FIRST_REFEREE = ROOT / "research/FIRST-KNOT-20261118-001/referee-R1"
MAX_NEXT = 30
MAX_CLASS_MAPS = 20_000
MAX_RIGID_MAPS = 20_000
PRIORITY = (0, 34, 74)


def load(path, name):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


C = load(EXPERIMENT / "job.py", "carried_census")
T = load(N / "table_tools.py", "carried_exact_tables")
MATRIX = T.TABLES


@cache
def binary():
    directory = TemporaryDirectory(prefix="grown-end-carried-")
    return directory, T.compiler(Path(directory.name) / "cuts")


@cache
def fallback():
    sys.path.insert(0, str(FIRST_REFEREE))
    return load(GS, "carried_large_tables")


def supports(rows):
    return tuple(tuple(sorted(r)) for r in rows)


def owners(rows):
    own = defaultdict(list)
    for j, row in enumerate(rows):
        for b in row:
            own[b].append(j)
    assert all(len(v) in (1, 2) for v in own.values())
    assert set(own) == set(range(len(own)))
    return own


@cache
def table(rows):
    own = owners(rows)
    if len(rows) <= 20 and len(own) <= 63 and any(len(v) == 1 for v in own.values()):
        return T.all_tables(binary()[1], [rows])[0]
    matrix, _, _, _ = fallback().full_table(rows)
    # The referee's sentinel is 99. Here widths and finite reported
    # cardinalities remain below it. Use one sentinel in both engines.
    assert len(own) < 99
    return tuple(tuple(int(k) if k != 99 else T.INFINITY for k in row) for row in matrix)


def isometry(a, b, colors_a=None, colors_b=None):
    if len(a) != len(b):
        return None
    if colors_a is None:
        return T.isometry(a, b)
    left = MATRIX.ColoredMatrix.make(a, colors_a)
    right = MATRIX.ColoredMatrix.make(b, colors_b)
    return next(MATRIX.isometries(left, right), None)


def incidence_graph(rows):
    graph = nx.Graph()
    for j, row in enumerate(rows):
        graph.add_node(("j", j), kind="junction")
        for x in row:
            graph.add_node(("b", x), kind="distinction")
            graph.add_edge(("j", j), ("b", x))
    return graph


def same_arrangement(a, b):
    return nx.is_isomorphic(incidence_graph(a), incidence_graph(b),
                            node_match=lambda x, y: x["kind"] == y["kind"])


def one_round(presentation):
    result = presentation.step(C.S.gf2(C.F.fewest), None)
    if result is None:
        return None, "stalled"
    if not result["new"]:
        return None, "closed"
    return supports(presentation.bits_of), "grown"


def stage(start, round_index):
    present = C.S.from_junctions(start)
    here = supports(start)
    for _ in range(round_index):
        here, _ = one_round(present)
        assert here is not None
    next_rows, status = one_round(present)
    if next_rows is not None:
        assert next_rows[:len(here)] == here
    return here, next_rows, status


def reading(rows):
    own = owners(rows)
    neighbors = defaultdict(set)
    loose = defaultdict(list)
    for bit, sites in sorted(own.items()):
        if len(sites) == 1:
            loose[sites[0]].append(bit)
        else:
            a, b = sites
            neighbors[a].add(b)
            neighbors[b].add(a)
    live = set(loose)
    family = {frozenset(neighbors[j] & live) for j in range(len(rows))}
    family = {f for f in family if len(f) >= 2}
    maximal = {f for f in family if not any(f < other for other in family)}
    return dict(sorted(loose.items())), family, maximal


def reading_matrix(rows, exact, read):
    loose, _, maximal = read
    shared = tuple(x for x, u in sorted(owners(rows).items()) if len(u) == 2)
    blocks = (*((x,) for x in shared), *map(tuple, loose.values()))
    sites = (*(-1 for _ in shared), *loose.keys())
    families = tuple(sorted(tuple(sorted(f)) for f in maximal))
    colors = tuple((int(site != -1), len(group), exact[group[0]][group[1]] if len(group) > 1 else 0)
                   for group, site in zip(blocks, sites, strict=True))
    colors += tuple((2, len(family), 0) for family in families)
    matrix = [[0] * len(colors) for _ in colors]
    for i, j in combinations(range(len(colors)), 2):
        if j < len(blocks):
            u, v = sites[i], sites[j]
            bit, other = blocks[i][0], blocks[j][0]
            in_live_star = (u != -1 and v == -1 and other in rows[u]) or (v != -1 and u == -1 and bit in rows[v])
            weight = 2 * exact[bit][other] + in_live_star
        elif i < len(blocks):
            weight = -1 if sites[i] in families[j - len(blocks)] else -2
        else:
            weight = -3
        matrix[i][j] = matrix[j][i] = weight
    return MATRIX.ColoredMatrix.make(tuple(map(tuple, matrix)), colors), blocks, sites


def reading_maps(a, b, ka, kb, ra, rb):
    ma, ba, sa = reading_matrix(a, ka, ra)
    mb, bb, sb = reading_matrix(b, kb, rb)
    for mapping in MATRIX.isometries(ma, mb):
        phi = [-1] * len(ka)
        psi = {}
        for i, left in enumerate(ba):
            j = mapping[i]
            for x, y in zip(left, bb[j], strict=True):
                phi[x] = y
            if sa[i] != -1:
                psi[sa[i]] = sb[j]
        assert MATRIX.disagreement(ka, kb, phi) is None
        assert all(set(phi[x] for x in a[u]) == set(b[v]) for u, v in psi.items())
        assert {frozenset(psi[i] for i in f) for f in ra[2]} == rb[2]
        whole = {frozenset(psi[i] for i in f) for f in ra[1]} == rb[1]
        yield tuple(phi), psi, whole


def basis(rows):
    current = {}
    for value in rows:
        word = value
        while word:
            pivot = word.bit_length() - 1
            if pivot not in current:
                current[pivot] = word
                break
            word ^= current[pivot]
    return current


def carries(a, b, mapping):
    right = T.masks(b)
    left = tuple(sum(1 << mapping[x] for x in s) for s in a)
    return len(basis(left)) == len(basis(right)) == len(basis((*left, *right)))


def new_sites(old, new):
    own = owners(old)
    for row in new[len(old):]:
        taken = {own[bit][0]: bit for bit in row if bit in own}
        assert len(taken) == sum(bit in own for bit in row)
        yield taken, tuple(bit for bit in row if bit not in own)


def lift(phi, psi, a, b, na, nb):
    pool = defaultdict(list)
    for taken, fresh in new_sites(b, nb):
        pool[tuple(sorted(taken)), len(fresh)].append((taken, fresh))
    image = list(phi) + [-1] * (len(owners(na)) - len(phi))
    for taken, fresh in new_sites(a, na):
        key = tuple(sorted(psi[p] for p in taken)), len(fresh)
        if not pool[key]:
            return None
        used, new = pool[key].pop()
        for j, bit in taken.items():
            image[bit] = used[psi[j]]
        for x, y in zip(fresh, new, strict=True):
            image[x] = y
    return tuple(image) if len(image) == len(owners(nb)) and sorted(image) == list(range(len(image))) else None


def witness_row(ka, kb, phi, pair):
    x, y = pair
    return {"left_pair": pair, "right_pair": (phi[x], phi[y]), "left_K": ka[x][y], "right_K": kb[phi[x]][phi[y]]}


def compatible_iso(ka, kb, phi, loose_a, loose_b, psi, rigid):
    if len(ka) != len(kb):
        return None
    ca, cb = [(0, 0)] * len(ka), [(0, 0)] * len(kb)
    if not rigid:
        for u, us in loose_a.items():
            for x in us:
                ca[x] = (1, u)
            for y in loose_b[psi[u]]:
                cb[y] = (1, u)
    for x, y in enumerate(phi):
        if ca[x][0] == 0:
            ca[x] = cb[y] = (2, x)
    return isometry(ka, kb, tuple(ca), tuple(cb))


def actual_old_maps(phi, loose):
    for assignments in product(*(permutations(phi[i] for i in row) for row in loose.values())):
        perm = list(phi)
        for positions, images in zip(loose.values(), assignments, strict=True):
            for i, j in zip(positions, images, strict=True):
                perm[i] = j
        yield tuple(perm)


def compare(a, b, na, nb, ka, kb):
    ra, rb = reading(a), reading(b)
    variants = prod(factorial(len(row)) for row in ra[0].values())
    shared = tuple(x for x, u in sorted(owners(a).items()) if len(u) == 2)
    c = Counter()
    report = {"map_counts": c, "loose_permutations_per_class": variants}
    if na is None or nb is None:
        next_status = "no_complete_round"
    elif max(len(na), len(nb)) > MAX_NEXT or max(len(owners(na)), len(owners(nb))) >= 99:
        next_status = "successor_size_cap"
    else:
        next_status = "eligible"
    report["successor_status"] = next_status
    next_tables = None
    for index, (phi, psi, whole) in enumerate(reading_maps(a, b, ka, kb, ra, rb)):
        if index == MAX_CLASS_MAPS:
            report["class_map_cap"] = True
            break
        c["maximal_R_classes"] += 1
        if whole:
            c["whole_R_classes"] += 1
        equation = carries(a, b, phi)
        c["equation_carrying" if equation else "equation_changing"] += variants
        if next_status != "eligible":
            c["successor_unmeasured_maps"] += variants
            continue
        if next_tables is None:
            next_tables = table(na), table(nb)
        l, r = next_tables
        extension = lift(phi, psi, a, b, na, nb)
        if extension is None:
            c["growth_correspondence_missing"] += variants
            report.setdefault("unmatched_round", {"old_map": phi, "holder_map": psi})
            continue
        bad = MATRIX.disagreement(l, r, extension)
        if bad is None:
            c["canonical_lift_valid"] += variants
            assert not equation or carries(na, nb, extension)
        else:
            c["canonical_lift_invalid"] += variants
            fixed = next(((x, y) for x, y in combinations(shared, 2)
                          if l[x][y] != r[phi[x]][phi[y]]), None)
            rescue = None if fixed is not None else compatible_iso(l, r, phi, ra[0], rb[0], psi, False)
            c["shared_pair_obstruction"] += variants * (fixed is not None)
            c["loose_repair_still_impossible" if rescue is None else "other_scalar_extension_exists"] += variants
            report.setdefault("lift_failure", {
                "old_map": phi, "holder_map": psi, "canonical_successor_map": extension, "whole_R": whole,
                "old_equations_carried": equation, "first_difference": witness_row(l, r, extension, bad),
                "shared_pair_difference": witness_row(l, r, phi, fixed) if fixed else None,
                "alternative_scalar_extension": rescue,
            })
        for rigid in actual_old_maps(phi, ra[0]):
            if c["rigid_tested"] >= MAX_RIGID_MAPS:
                break
            c["rigid_tested"] += 1
            if rigid == extension[:len(phi)] and bad is None:
                rigid_ok = True
            else:
                old_pairs_agree = all(l[x][y] == r[rigid[x]][rigid[y]] for x, y in combinations(range(len(phi)), 2))
                rigid_ok = old_pairs_agree and compatible_iso(l, r, rigid, ra[0], rb[0], psi, True) is not None
            c["rigid_valid" if rigid_ok else "rigid_invalid"] += 1
    if next_status == "eligible" and c["maximal_R_classes"]:
        l, r = next_tables or (table(na), table(nb))
        report["successor_any_isometry"] = isometry(l, r) is not None
    c["maximal_R_maps"] = c["maximal_R_classes"] * variants
    c["whole_R_maps"] = c["whole_R_classes"] * variants
    c["rigid_untested"] = c["maximal_R_maps"] - c["rigid_tested"]
    return report


def raw_source_maps(a, b, ka, kb):
    """Independent, uncompressed full-table maps with literal reading tests."""
    def graph(exact):
        g = nx.Graph()
        for i, row in enumerate(exact):
            g.add_node(i, histogram=tuple(sorted(row)))
        for i, j in combinations(range(len(exact)), 2):
            g.add_edge(i, j, size=exact[i][j])
        return g

    gm = nx.algorithms.isomorphism.GraphMatcher(
        graph(ka), graph(kb), node_match=lambda x, y: x["histogram"] == y["histogram"],
        edge_match=lambda x, y: x["size"] == y["size"],
    )
    loose_a, full_a, max_a = reading(a)
    loose_b, full_b, max_b = reading(b)
    boundary_b = {x for group in loose_b.values() for x in group}
    stars_b = {frozenset(b[j]): j for j in loose_b}
    counts = Counter()
    for named in gm.isomorphisms_iter():
        if counts["full_table_maps"] == MAX_CLASS_MAPS:
            return {"count_complete": False, **counts}
        phi = tuple(named[i] for i in range(len(ka)))
        assert MATRIX.disagreement(ka, kb, phi) is None
        counts["full_table_maps"] += 1
        counts["equation_carrying"] += carries(a, b, phi)
        if {phi[x] for group in loose_a.values() for x in group} != boundary_b:
            continue
        counts["loose_set"] += 1
        images = {j: frozenset(phi[x] for x in a[j]) for j in loose_a}
        if set(images.values()) != stars_b.keys():
            continue
        counts["live_supports"] += 1
        psi = {j: stars_b[img] for j, img in images.items()}
        counts["maximal_R"] += {frozenset(psi[j] for j in f) for f in max_a} == max_b
        counts["whole_R"] += {frozenset(psi[j] for j in f) for f in full_a} == full_b
    return {"count_complete": True, **counts}


def archive_rows():
    with gzip.open(GROWN / "results_grown-pair.jsonl.gz", "rt") as stream:
        for line in stream:
            record = json.loads(line)
            if record["status"] == "ok":
                yield from record["result"]["stages"]


def cases():
    groups = json.loads((GROWN / "other_states.json").read_text())["group_list"]
    assert len(groups) == 152
    assert tuple(i for i, g in enumerate(groups) if g["next_tables_isomorphic"] is False) == PRIORITY
    ordered = PRIORITY
    tags = {tuple(groups[i]["reps"][0]["prov"][0]): i for i in ordered}
    hashes = {tags[(s["index"], s["round"])]: s["table_hash"]
              for s in archive_rows() if (s["index"], s["round"]) in tags}
    assert hashes.keys() == set(ordered)
    buckets = defaultdict(list)
    needed = set(hashes.values())
    for row in archive_rows():
        if row["round"] > 0 and row["table_hash"] in needed:
            buckets[row["table_hash"]].append(row)
    for i in ordered:
        yield f"g{i:03d}", {"group": groups[i], "members": sorted(buckets[hashes[i]], key=lambda s: (s["index"], s["round"]))}


def run(case_id, payload):
    group, members = payload["group"], payload["members"]
    ref = table(supports(group["reps"][0]["stars"]))
    classes = []
    hashed_only = []
    for row in members:
        index, rd = row["index"], row["round"]
        start = supports(C.A.stars_of(tuple(map(tuple, row["key"]))))
        here, nxt, status = stage(start, rd)
        stored = supports(row["stars"])
        assert here == stored or same_arrangement(here, stored)
        measured = table(here)
        if isometry(ref, measured) is None:
            hashed_only.append((index, rd))
            continue
        same = next((c for c in classes if same_arrangement(c["here"], here)), None)
        if same is None:
            loose, family, maximal = reading(here)
            classes.append({
                "start": start, "here": here, "next": nxt, "status": status, "origins": [(index, rd)],
                "source_width": len(measured), "successor_width": len(owners(nxt)) if nxt is not None else None,
                "loose_groups_by_holder": loose,
                "meeting_family": sorted(tuple(sorted(f)) for f in family),
                "maximal_meeting_family": sorted(tuple(sorted(f)) for f in maximal),
            })
        else:
            same["origins"].append((index, rd))
    matches = []
    for i, j in combinations(range(len(classes)), 2):
        a, b = classes[i], classes[j]
        ka, kb = table(a["here"]), table(b["here"])
        measured = compare(a["here"], b["here"], a["next"], b["next"], ka, kb)
        raw = raw_source_maps(a["here"], b["here"], ka, kb)
        assert raw["full_table_maps"]
        if raw["count_complete"] and not measured.get("class_map_cap"):
            assert raw.get("maximal_R", 0) == measured["map_counts"]["maximal_R_maps"]
            assert raw.get("whole_R", 0) == measured["map_counts"]["whole_R_maps"]
        measured["raw_source_check"] = raw
        if group["next_tables_isomorphic"] is False and measured["successor_status"] == "eligible":
            measured["successor_any_isometry"] = isometry(table(a["next"]), table(b["next"])) is not None
        matches.append({"members": (i, j), **measured})
    return {"id": case_id, "recorded_successor_tables_isometric": group["next_tables_isomorphic"],
            "recorded_state_groups": group["state_groups"], "regrown_provenances": len(members),
            "hash_only_provenances": hashed_only, "classes": classes, "comparisons": matches}


def relabeling_control(member):
    a, na = member["here"], member["next"]
    ka, kna = table(a), table(na)
    w, w1 = len(ka), len(kna)
    phi = tuple(reversed(range(w)))
    extension = (*phi, *range(w1 - 1, w - 1, -1))
    b = tuple(tuple(sorted(phi[x] for x in row)) for row in a)
    nb = tuple(tuple(sorted(extension[x] for x in row)) for row in na)
    kb, knb = table(b), table(nb)
    assert MATRIX.disagreement(ka, kb, phi) is None and MATRIX.disagreement(kna, knb, extension) is None
    ra, rb = reading(a), reading(b)
    psi = next(psi for test, psi, whole in reading_maps(a, b, ka, kb, ra, rb)
               if whole and all(set(test[x] for x in row) == set(phi[x] for x in row) for row in a))
    assert carries(a, b, phi) and carries(na, nb, extension)
    direct = lift(phi, psi, a, b, na, nb)
    assert MATRIX.disagreement(kna, knb, direct) is None
    assert compatible_iso(kna, knb, phi, ra[0], rb[0], psi, True) is not None
    for group in ra[0].values():
        for x, y in combinations(group, 2):
            twisted = list(phi)
            twisted[x], twisted[y] = twisted[y], twisted[x]
            bad = next(((i, j) for i, j in combinations(range(w), 2)
                        if kna[i][j] != knb[twisted[i]][twisted[j]]), None)
            if bad is None:
                continue
            assert MATRIX.disagreement(ka, kb, twisted) is None and carries(a, b, twisted)
            assert lift(twisted, psi, a, b, na, nb) == direct
            return {"known_simultaneous_map": extension, "repaired_successor_map": direct,
                    "injected_loose_name_exchange": (x, y),
                    "rigid_old_pair_difference": witness_row(kna, knb, twisted, bad)}
    raise AssertionError("no loose-name exchange changes an old successor entry in the control")


def main():
    records = [run(case_id, p) for case_id, p in cases()]
    print(json.dumps({"max_successor_sites": MAX_NEXT, "max_class_maps_per_pair": MAX_CLASS_MAPS,
                      "max_rigid_maps_per_pair": MAX_RIGID_MAPS, "groups": records,
                      "injected_relabeling_control": relabeling_control(records[0]["classes"][0])}, indent=2))


if __name__ == "__main__":
    main()
