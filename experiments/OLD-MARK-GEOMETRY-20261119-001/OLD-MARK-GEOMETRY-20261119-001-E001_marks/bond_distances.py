"""Read literal bond distances between persistent source distinctions."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name
FEEDBACK = "STATE-FEEDS-GROWTH-20261119-001"
EDDY = "EDDY-WORLD-20261119-001"
FEEDBACK_CODE = ROOT / "experiments" / FEEDBACK / (FEEDBACK + "-E001_feedback")
EDDY_CODE = ROOT / "experiments" / EDDY / (EDDY + "-E001_world")
OLD_RECORD = ROOT / "artifacts" / FEEDBACK / (FEEDBACK + "-E001_feedback") / "original_marks.json"
STUDY_SOURCES = HERE / "inputs.json"
CASES = ("J1", "B", "J0", "J2", "C1", "T4", "T8", "J1x2")
NAMED = ((0, 2), (2, 5), (3, 4), (8, 12), (0, 15))
sys.path[:0] = [str(FEEDBACK_CODE), str(EDDY_CODE)]
import growth  # noqa: E402
from world_bonds import literal_states_distances  # noqa: E402


def members(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def bitset(ids):
    result = 0
    for j in ids:
        result |= 1 << j
    return result


def reached(first, domain, neighbors):
    seen = pending = first
    while pending:
        bit = pending & -pending
        v = bit.bit_length() - 1
        new = neighbors[v] & domain & ~seen
        seen |= new
        pending = (pending ^ bit) | new
    return seen


class Wiring:
    def __init__(self, stars):
        self.stars = tuple(map(frozenset, stars))
        incidence = defaultdict(list)
        for v, support in enumerate(self.stars):
            for name in support:
                incidence[name].append(v)
        self.n = len(self.stars)
        self.exterior = self.n if any(len(row) == 1 for row in incidence.values()) else self.n - 1
        self.total = self.exterior + 1
        self.full = (1 << self.total) - 1
        self.edge = {}
        self.neighbors = [0] * self.total
        for name, row in sorted(incidence.items()):
            assert len(row) in (1, 2)
            u, v = tuple(row) if len(row) == 2 else (row[0], self.exterior)
            self.edge[name] = u, v
            self.neighbors[u] |= 1 << v
            self.neighbors[v] |= 1 << u
        assert reached(1, self.full, self.neighbors) == self.full

    def witness(self, inside, marks=(), cost=None):
        """Independently re-read the literal cut, both connected sides and parity sum."""
        assert 0 < inside < 1 << self.exterior
        assert reached(inside & -inside, inside, self.neighbors) == inside
        outside = self.full ^ inside
        assert reached(1 << self.exterior, outside, self.neighbors) == outside
        cut = [name for name, (u, v) in self.edge.items() if ((inside >> u) ^ (inside >> v)) & 1]
        assert set(marks) <= set(cut) and (cost is None or cost == len(cut))
        parity_sum = set()
        for v in members(inside):
            parity_sum.symmetric_difference_update(self.stars[v])
        assert parity_sum == set(cut)
        return {"distinctions": cut, "knots": list(members(inside))}


def weighted_projection(source, frame):
    """Extract first-layer link weights from the physical distinctions."""
    assert source.exterior == source.n and frame.exterior == frame.n
    assert source.stars == frame.stars[:source.n]
    shared = {d: (u, v) for d, (u, v) in source.edge.items() if v < source.n}
    assert all(frame.edge[d] == ends for d, ends in shared.items())
    loose = [0] * source.n
    for d, (u, v) in source.edge.items():
        if v == source.exterior:
            loose[u] += 1
            fu, fv = frame.edge[d]
            assert fu == u and fv >= source.n
    assert all(loose)
    binary = []
    for kid in range(source.n, frame.n):
        parents = [a for d in frame.stars[kid] if (a := frame.edge[d][0]) < source.n]
        fresh = frame.stars[kid] - source.edge.keys()
        assert all(frame.edge[d] == (kid, frame.exterior) for d in fresh)
        assert len(parents) in (1, 2) and len(set(parents)) == len(parents)
        assert len(fresh) >= 1 and len(frame.stars[kid]) == len(fresh) + len(parents)
        if len(parents) == 2:
            binary.append((kid, *sorted(parents), len(fresh)))
    return shared, loose, binary


def expand_old(inside, shared, binary):
    """Replay the minimum connecting child choice for this fixed old subset."""
    parent = {v: v for v in members(inside)}

    def root(v):
        while v != parent[v]:
            v = parent[v]
        return v

    def merge(a, b):
        u, v = root(a), root(b)
        parent[u] = v
        return u != v

    for u, v in shared.values():
        if u in parent and v in parent:
            merge(u, v)
    for kid, u, v, fresh in sorted(binary, key=lambda row: row[-1]):
        if u in parent and v in parent:
            merges = merge(u, v)
            if fresh <= 2 or merges:
                inside |= 1 << kid
    return inside


def projection(binary, source, frame):
    shared, loose, children = weighted_projection(source, frame)
    if frame.n == source.n:
        assert frame.edge == source.edge
    data = [f"{source.n} {len(shared)} {len(children)}", " ".join(map(str, loose))]
    data.extend(f"{u} {v}" for u, v in shared.values())
    data.extend(f"{u} {v} {fresh}" for _, u, v, fresh in children)
    raw = subprocess.run([binary], input="\n".join(data) + "\n", text=True,
                         capture_output=True, check=True).stdout.splitlines()
    nsubsets = int(raw[0])
    marks = list(shared)
    result = {}
    witnesses = {}
    for line in raw[1:]:
        i, j, cost, old = map(int, line.split())
        pair = marks[i], marks[j]
        assert cost >= 2
        inside = expand_old(old, shared, children)
        if inside not in witnesses:
            witnesses[inside] = frame.witness(inside, pair, cost)
        else:
            cut = witnesses[inside]["distinctions"]
            assert set(pair) <= set(cut) and len(cut) == cost
        result[pair] = (cost - 1, inside)
    assert len(result) == len(marks) * (len(marks) - 1) // 2
    return result, witnesses, nsubsets


def control(binary):
    """All old pairs on two four-node fixtures, by exhaustive allowed states."""
    original = [[0, 2, 3], [0, 1, 4, 5], [1, 6, 7], [2, 8, 9]]
    checks = []
    for fresh in (1, 4):
        actual = original + [[3, 6, *range(10, 10 + fresh)], [4, 8, 10 + fresh],
                             [5, 11 + fresh], [7, 12 + fresh], [9, 13 + fresh]]
        # Every source distinction retains at least one holder. The exhaustive
        # allowed-state computation uses independent small literal controls.
        expected, states, bonds = literal_states_distances(actual)
        exact, _, subsets = projection(binary, Wiring(original), Wiring(actual))
        for (i, j), (value, _) in exact.items():
            assert value == expected[i][j], ((i, j), value, expected[i][j])
        checks.append({"fresh_at_chosen_binary": fresh, "checked_pairs": len(exact),
                       "allowed_states": states, "minimal_nonfree_projections": len(bonds),
                       "connected_old_subsets": subsets})
    return checks


def pair_groups(spec):
    marks = spec["roles"]["anchors"]
    rmarks = sum(spec["roles"]["ring_edges"], [])
    out = {"path_path": list(combinations(marks, 2)),
           "ring_path": list(product(rmarks, marks)),
           "ring_ring": list(combinations(rmarks, 2))}
    return {key: [tuple(sorted(a)) for a in pairs] for key, pairs in out.items() if pairs}


def input_cases(selection):
    # The leading J1 replay is independent of the shared fixture producer.
    manifest = json.loads(STUDY_SOURCES.read_text())
    inputs = ROOT / manifest["source"]
    assert sha256(inputs.read_bytes()).hexdigest() == manifest["sha256"]
    original = {s["id"]: s for s in json.loads(inputs.read_text())["cases"]}
    if selection == ["J1"]:
        return [(original["J1"], {"0": frozenset(), "1": frozenset(original["J1"]["roles"]["ring_edges"][0])})]
    import sources
    roster = sources.cases()
    values = roster if isinstance(roster, dict) else {s["id"]: s for s in roster}
    return [(values[key], sources.loads(values[key])) for key in selection]


def old_regression(result, quiet, loaded):
    prior = json.loads(OLD_RECORD.read_text())
    verified = Counter()
    previous_unresolved = {}
    for group, rows in prior["pairs"].items():
        unresolved = Counter()
        for a, b, old_q, old_l, label in rows:
            pair = tuple(sorted((a, b)))
            q, l = result[quiet][pair][0], result[loaded][pair][0]
            for old, new in ((old_q, q), (old_l, l)):
                if isinstance(old, int):
                    assert new == old
                    verified["exact_arms"] += 1
                elif old.startswith(">"):
                    assert new > int(old[1:])
                    verified["bounded_arms"] += 1
                else:
                    raise ValueError(old)
            if label == "unresolved":
                outcome = "longer" if l > q else "shorter" if l < q else "equal"
                unresolved[outcome] += 1
        previous_unresolved[group] = dict(unresolved)
    return {"predecessor_receipts": dict(verified), "resolved_earlier_unknown_comparisons": previous_unresolved}


def encode_frame(frame, result, witnesses, subsets):
    ordered = sorted(witnesses)
    idx = {mask: j for j, mask in enumerate(ordered)}
    return {"knots": frame.n, "distinctions": len(frame.edge),
            "connected_old_subsets": subsets,
            "pair_columns": ["first", "second", "bond_distance", "witness_index"],
            "pairs": [[a, b, value, idx[mask]] for (a, b), (value, mask) in sorted(result.items())],
            "witnesses": [witnesses[mask] for mask in ordered]}


def contrasts(spec, loads, by_mask, result):
    quiet = next(code for code, names in loads.items() if not names)
    baseline = result[by_mask[quiet]]
    groups = pair_groups(spec)
    detail = {}
    for code in loads:
        arm = result[by_mask[code]]
        changed = {}
        for group, pairs in groups.items():
            shifts = Counter(arm[p][0] - baseline[p][0] for p in pairs)
            changed[group] = dict(sorted(shifts.items()))
        detail[code] = changed
    path = spec["roles"]["anchors"]
    named = []
    for i, j in NAMED:
        pair = tuple(sorted((path[i], path[j])))
        named.append([i, j, {code: result[by_mask[code]][pair][0] for code in loads}])
    answer = {"from_quiet": detail, "named_path_pairs": named}
    if len(spec["roles"]["ring_edges"]) == 2:
        r0, r1 = map(frozenset, spec["roles"]["ring_edges"])
        words = {names: result[by_mask[code]] for code, names in loads.items()}
        neither, first, second, both = [words[word] for word in (frozenset(), r0, r1, r0 | r1)]
        answer["path_interaction"] = [
            [i, j, both[p][0] - first[p][0] - second[p][0] + neither[p][0]]
            for i, j in combinations(range(len(path)), 2)
            if (p := tuple(sorted((path[i], path[j])))) in neither]
    if spec["id"] == "J1x2":
        by_dose = defaultdict(list)
        for code, names in loads.items():
            by_dose[len(names)].append(result[by_mask[code]])
        answer["path_dose"] = [
            [i, j, {dose: {"min": min(values), "max": max(values), "sum": sum(values),
                           "assignments": len(values)}
                    for dose, arms in sorted(by_dose.items())
                    if (values := [arm[tuple(sorted((path[i], path[j])))][0] for arm in arms])}]
            for i, j in combinations(range(len(path)), 2)
        ]
    return answer


def read_first(binary, spec, loads):
    original = growth.predecessor().source_stars(spec)
    source = Wiring(original)
    source_reading, source_witness, source_subsets = projection(binary, source, source)
    source_result = encode_frame(source, source_reading, source_witness, source_subsets)
    arms, result, by_mask, unique = {}, {}, {}, {}
    assert all(isinstance(code, str) for code in loads)
    loads = {code: frozenset(names) for code, names in loads.items()}
    for code, names in loads.items():
        growth._state(original, names)
        active = tuple(v for v, row in enumerate(source.stars) if not row.isdisjoint(names))
        if active not in unique:
            active_id = str(len(unique))
            unique[active] = active_id
            frame = growth.step(original, names, ("P", "V"))
            assert frame["status"] == "extend"
            wiring = Wiring(frame["stars"])
            reading, witnesses, subsets = projection(binary, source, wiring)
            for p, (distance, _) in reading.items():
                original_d, original_shore = source_reading[p]
                assert distance <= original_d
                lifted = wiring.witness(original_shore, p, original_d + 1)
                assert lifted == source_witness[original_shore]
            result[active_id] = reading
            arms[active_id] = {"active_knots": active, "tested_assignment": code,
                               **encode_frame(wiring, reading, witnesses, subsets)}
        by_mask[code] = unique[active]
    summary = contrasts(spec, loads, by_mask, result)
    if spec["id"] == "J1":
        quiet = next(k for k, names in loads.items() if not names)
        hot = next(k for k, names in loads.items() if names)
        summary["predecessor_audit"] = old_regression(result, by_mask[quiet], by_mask[hot])
    return {"source": source_result, "age_one_by_activity": arms,
            "assignments": {code: {"occupied": sorted(names), "activity_id": by_mask[code]}
                            for code, names in loads.items()},
            "roles": spec["roles"], "contrasts": summary}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--cases", nargs="+", choices=CASES, default=list(CASES))
    parser.add_argument("--out", type=Path, default=OUTPUT / "bond_first.json")
    options = parser.parse_args()
    with TemporaryDirectory(prefix="old-mark-bonds-") as directory:
        binary = Path(directory) / "bond_first"
        subprocess.run(["g++", "-O3", "-std=c++20", "-Wall", "-Wextra",
                        str(HERE / "bond_first.cpp"), "-o", str(binary)], check=True)
        controls = control(binary)
        result = {}
        for spec, loads in input_cases(options.cases):
            result[spec["id"]] = read_first(binary, spec, loads)
            print(spec["id"], len(loads), len(result[spec["id"]]["age_one_by_activity"]),
                  result[spec["id"]]["contrasts"]["from_quiet"] if spec["id"] != "J1x2" else "dose done",
                  flush=True)
    output = {"schema": 1, "frame_ages": [0, 1], "unit": "bond size minus one",
              "sources_sha256": sha256(STUDY_SOURCES.read_bytes()).hexdigest(),
              "controls": controls, "cases": result}
    options.out.parent.mkdir(parents=True, exist_ok=True)
    options.out.write_text(json.dumps(output, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
