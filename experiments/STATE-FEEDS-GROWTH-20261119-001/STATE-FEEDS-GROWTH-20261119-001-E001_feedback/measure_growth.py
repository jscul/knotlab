"""Enumerate the frozen feedback panel and exact small allocation controls."""

from argparse import ArgumentParser
from base64 import b64decode, b64encode
from collections import Counter
from functools import lru_cache
from hashlib import sha256
from itertools import permutations, product
import json
from pathlib import Path
from tempfile import NamedTemporaryFile
import zlib

import growth


INPUTS = growth.HERE / "inputs.json"
OUT = growth.ROOT / "artifacts" / growth.HERE.parent.name / growth.HERE.name / "growth.json"
TABLES = tuple(product(growth.ACTIONS, repeat=2))
DERIVED = {"parent_sets": "parents", "consumed": "spent", "fresh": "fresh"}


def read_inputs():
    design = json.loads(INPUTS.read_text())
    source = (growth.ROOT / design["source"]).read_bytes()
    assert sha256(source).hexdigest() == design["sha256"]
    by_id = {row["id"]: row for row in json.loads(source)["cases"]}
    return design, {key: by_id[key] for key in design["source_cases"]}


def run_id(case, family, table, mask):
    return "/".join((case, family, "".join(table), str(mask)))


def ring_state(spec, mask):
    return frozenset(bit for i, row in enumerate(spec["roles"]["ring_edges"]) if mask & (1 << i) for bit in row)


def matched_pulse(spec, frame):
    """Use evaluator roles only to prepare the same actual ordinary four-response."""
    seam, = spec["roles"]["seams"]
    n = len(spec["sizes"])
    path = set(spec["roles"]["background"])
    stars = frame["stars"]
    legs = [v for v in range(n) if v not in path and set(stars[seam]) & set(stars[v])]
    u, v = legs
    child, = (w for w in frame["born"] if set(frame["parent_sets"][w]) == set(legs))
    old = {d for w in legs for d in set(stars[seam]) & set(stars[w])}
    spent = {d for w, d in frame["consumed"][child]}
    support = old | spent
    assert len(support) == 4 and not support.intersection(d for row in frame["loose"].values() for d in row)
    assert {j for j, row in enumerate(stars) if not support.isdisjoint(row)} == {seam, u, v, child}
    return support, {"seam": seam, "ring_leg_holders": legs, "hot_first_child": child, "support": sorted(support)}


def fixture_runs(design, specs, *, through=None):
    """Yield the literal age-indexed records with source marks kept for grading."""
    cap = {"junctions": design["cap_knots"], "distinctions": design["cap_distinctions"]}
    age = design["age_limit"] if through is None else through
    prior = growth.predecessor()

    @lru_cache(maxsize=128)
    def continuation(stars, occupied, table, remaining, start):
        return growth.grow(stars, occupied, table, remaining, caps=cap, start_age=start)

    def case(spec, family, table, mask, occupied, prefix=None, marks=None, comparison_family=None):
        tag = spec["id"]
        start = int(prefix is not None)
        begin = ({"stars": tuple(map(tuple, prior.source_stars(spec)))} if prefix is None
                 else prefix["stages"]["1"])
        grown = continuation(begin["stars"], frozenset(occupied), table, age - start, start)
        stages = grown["stages"]
        if start:
            stages = {"0": prefix["stages"]["0"], **stages}
            stages["1"] = {**begin, "occupied": sorted(occupied)}
        key = run_id(tag, family, table, mask)
        return key, {
            "base_case": tag, "arm": f"{family}:{mask}", "family": family, "table": table,
            "load_mask": mask if family in {"source", "late_raw", "late_branch_raw"} else None,
            "injection_age": start, "injected_distinctions": sorted(occupied),
            "matched_quiet": run_id(tag, comparison_family or family, table, 0),
            "input": spec, "preparation": marks, "stages": stages, "termination": grown["termination"],
        }

    for tag, spec in specs.items():
        masks = range(1 << len(spec["roles"]["ring_edges"]))
        standard = case(spec, "source", growth.ORDINARY, 0, ())[1]
        for table in TABLES:
            primary = [case(spec, "source", table, mask, ring_state(spec, mask)) for mask in masks]
            yield from primary
            if age < 1:
                continue
            own = primary[0][1]
            if len(masks) > 1:
                for family, prefix in (("late_raw", standard), ("late_branch_raw", own)):
                    if "1" in prefix["stages"]:
                        for mask in masks:
                            yield case(spec, family, table, mask, ring_state(spec, mask), prefix)
            if tag in {"J1", "C1"}:
                shift, mark = matched_pulse(spec, standard["stages"]["1"])
                yield case(spec, "pulse", table, 0, (), standard, mark)
                yield case(spec, "pulse", table, 1, shift, standard, mark)
                if tag == "J1":
                    yield case(spec, "pulse_plus_raw_ring", table, 1, shift ^ ring_state(spec, 1),
                               standard, mark, comparison_family="pulse")


def rank(masks):
    basis = {}
    for row in masks:
        while row:
            top = row.bit_length() - 1
            if top not in basis:
                basis[top] = row
                break
            row ^= basis[top]
    return len(basis)


def verify_projections(old, frame):
    """Check projection codimensions independently by GF(2) rank on eliminated columns."""
    masks = [sum(1 << d for d in row) for row in frame["stars"]]
    r = rank(masks)
    old_mask = 0
    for m in masks[:len(old)]:
        old_mask |= m
    assert r == frame["equation_rank"]
    assert r - rank(m & ~old_mask for m in masks) == rank(masks[:len(old)])
    assert all(r - rank(m & ~k for m in masks) == 1 for k in masks)


def tiny_allocations():
    """Exhaust all old loose allocations and all minimum fresh lifts on a three-knot path."""
    stars = ((0, 2, 3), (0, 1, 4), (1, 5, 6))
    source = {frozenset(row) for row in stars}
    rows = {}
    for prep, lit in (("blank", frozenset()), ("mixed", frozenset((0, 1, 2, 5)))):
        sym = [p for p in permutations(range(7)) if
               {frozenset(p[d] for d in row) for row in source} == source and
               frozenset(p[d] for d in lit) == lit]
        assert sym
        for table in TABLES:
            plan = growth.plan_round(stars, lit, table)
            assert plan.status == "extend"
            holders = tuple(plan.stage.loose)
            pointwise = set()
            colored = set()
            hot_fresh = Counter()
            examples = {}
            for orders in product(*(permutations(plan.stage.loose[v]) for v in holders)):
                ports = {v: iter(order) for v, order in zip(holders, orders, strict=True)}
                alloc = tuple(tuple(next(ports[v]) for v in b.parents) for b in plan.births)
                choice_ranges = [range(b.fresh) for b, row in zip(plan.births, alloc, strict=True)
                                 if len(lit.intersection(row)) % 2]
                for indices in product(*choice_ranges):
                    chooser = iter(indices)
                    frame = growth.realize_round(plan, allocation=alloc, choose_fresh=lambda ds: ds[next(chooser)])
                    verify_projections(stars, frame)
                    n = len(frame["new_occupied"])
                    hot_fresh[n] += 1
                    examples.setdefault(n, {"spent": alloc, "new_occupied": frame["new_occupied"]})

                    def key(p):
                        lit_fresh = set(frame["new_occupied"])
                        return tuple(sorted((tuple(sorted(p[d] for d in row)), b.fresh,
                                             len(lit_fresh.intersection(frame["fresh"][j])))
                                            for j, (row, b) in enumerate(zip(alloc, plan.births, strict=True), 3)))

                    pointwise.add(key(tuple(range(7))))
                    colored.add(min(key(p) for p in sym))
            rows[prep + "/" + "".join(table)] = {"literal_histories": sum(hot_fresh.values()),
                "colored_outcomes": len(colored), "old_names_fixed_outcomes": len(pointwise),
                "source_colored_isometries": len(sym), "hot_fresh_histories": dict(sorted(hot_fresh.items())),
                "examples_by_hot_fresh_count": examples}
            if prep == "mixed":
                assert (len(colored) == 1) == (table[1] == "V")
                assert (len(pointwise) == 1) == (table[1] == "V")
                assert set(hot_fresh) == ({2} if table[1] == "V" else {0, 2})
            else:
                assert len(colored) == 1 and (len(pointwise) == 1) == (table[0] == "V")
    return {"stars": stars, "mixed_occupied": [0, 1, 2, 5], "rows": rows}


def reordered_round(before, after, table):
    """Reverse all funded sibling allocations and enact the resulting plan backwards."""
    plan = growth.plan_round(before["stars"], before["occupied"], table)
    assert plan.status == "extend"
    assignment = growth.literal_allocation(plan)
    old_count = len(plan.stage.stars)
    size = len(plan.births)
    old_names = {d: d for d in plan.stage.names}
    for row in plan.stage.loose.values():
        old_names.update(zip(row, reversed(row), strict=True))
    assert {old_names[d] for d in plan.occupied} == plan.occupied
    other = growth.realize_round(plan, allocation=[tuple(old_names[d] for d in ds) for ds in assignment],
                                 birth_order=reversed(range(size)))
    names = dict(old_names)
    moved = {v: v for v in range(old_count)}
    for j in range(size):
        u, v = old_count + j, old_count + size - 1 - j
        moved[u] = v
        names.update(zip(after["fresh"][u], other["fresh"][v], strict=True))
    assert {names[d] for d in after["occupied"]} == set(other["occupied"])
    for v, s in enumerate(after["stars"]):
        assert {names[d] for d in s} == set(other["stars"][moved[v]])
    for field in ("parent_sets", "demand_at_birth"):
        assert {moved[v]: row for v, row in after[field].items()} == other[field]
    assert {frozenset(moved[v] for v in g) for g in after["lookahead_groups"]} == set(
        map(frozenset, other["lookahead_groups"]))


def fixture_controls(specs, cases, design):
    caps = {"junctions": design["cap_knots"], "distinctions": design["cap_distinctions"]}
    source_matches = {}
    for name, spec in specs.items():
        record = cases[run_id(name, "source", growth.ORDINARY, 0)]
        through = max(map(int, record["stages"]))
        prior = growth.predecessor().grow_case(spec, through, caps)
        assert prior["qualification"]["canonical"]
        assert tuple(record["stages"]) == tuple(prior["stages"])
        for age, frame in record["stages"].items():
            other = prior["stages"][age]
            assert tuple(map(frozenset, frame["stars"])) == tuple(map(frozenset, other["stars"]))
            assert frame["equation_rank"] == other["equation_rank"]
            assert frame["born"] == other["born"]
            if age != "0":
                assert frame["parent_sets"] == {int(j): tuple(g) for j, g in other["parent_sets"].items()}
                assert frame["fresh"] == {int(j): tuple(ds) for j, ds in other["fresh"].items()}
        source_matches[name] = len(record["stages"])

    checked = Counter()
    for key, record in cases.items():
        stages = record["stages"]
        reference = cases[record["matched_quiet"]]["stages"]
        table = record["table"]
        if key != record["matched_quiet"] and (table[0] == table[1] or record["family"].startswith("late_")):
            assert tuple(stages) == tuple(reference)
            assert record["termination"] == cases[record["matched_quiet"]]["termination"]
            assert all(stages[age]["stars"] == reference[age]["stars"] for age in stages)
            checked["constant_or_late_equal_trajectories"] += 1
        start = record["injection_age"]
        for age in range(start + 1, max(map(int, stages)) + 1):
            before, after = stages[str(age - 1)], stages[str(age)]
            assert not after["new_occupied"] and not after["spent_occupied"]
            assert before["occupied"] == after["occupied"]
            if age > start + 1:
                assert not after["hot_live_parents"]
            checked["shared_only_transitions"] += 1

    C3 = ((0, 2, 3), (0, 1, 4), (1, 2, 5))
    closures = {}
    for action in growth.ACTIONS:
        frame = growth.step(C3, (), (action, action))
        verify_projections(C3, frame)
        assert frame["implied_closure"] == (action != "V")
        closures[action] = {"new_knots": len(frame["born"]), "fresh_counts": list(map(len, frame["fresh"].values())),
                            "closed": not frame["loose"]}

    assert all(cases[run_id("J1", "pulse", table, 1)]["stages"].keys() ==
               cases[run_id("J1", "pulse_plus_raw_ring", table, 1)]["stages"].keys() for table in TABLES)
    for table in TABLES:
        pulse = cases[run_id("J1", "pulse", table, 1)]
        combined = cases[run_id("J1", "pulse_plus_raw_ring", table, 1)]
        assert pulse["termination"] == combined["termination"]
        assert all(row["stars"] == combined["stages"][age]["stars"] for age, row in pulse["stages"].items())
        assert all(row.get("hot_live_parents") == combined["stages"][age].get("hot_live_parents")
                   for age, row in pulse["stages"].items())
        checked["distinct_state_same_live_parent_mask"] += 1

        keys = [run_id(tag, "source", table, mask) for tag, mask in (("R0", 1), ("J1", 1), ("T4", 3))]
        keys += [run_id(tag, "pulse", table, 1) for tag in ("J1", "C1")]
        for key in keys:
            record = cases[key]
            start = record["injection_age"]
            if str(start + 1) not in record["stages"]:
                continue
            before, after = (record["stages"][str(k)] for k in (start, start + 1))
            verify_projections(before["stars"], after)
            reordered_round(before, after, table)
            checked["projection_rank_and_reversed_allocations"] += 1
    return {"predecessor_completed_frames": source_matches, "invariants": dict(checked), "implied_closure": closures}


def pack(result):
    """Store each distinct literal frame once and keep only added supports in its geometry."""
    geometries, frames, stops, cases = [], [], [], {}
    geometry_keys, frame_keys, stop_keys = {}, {}, {}

    def lookup_interned(row, rows, keys):
        signature = sha256(json.dumps(row, separators=(",", ":")).encode()).digest()
        hits = keys.setdefault(signature, [])
        ref = next((i for i in hits if rows[i] == row), None)
        if ref is None:
            ref = len(rows)
            hits.append(ref)
            rows.append(row)
        return ref

    for key, record in result["cases"].items():
        references = {}
        parent = None
        prior_stars = ()
        for age, stage in record["stages"].items():
            stars = stage["stars"]
            geometry = geometry_keys.setdefault(stars, len(geometries))
            if geometry == len(geometries):
                assert stars[:len(prior_stars)] == prior_stars
                geometries.append([parent, stars[len(prior_stars):]])
            frame = {k: value for k, value in stage.items()
                     if k not in DERIVED and k not in {"stars", "demand_at_birth"}}
            frame["geometry"] = geometry
            references[age] = lookup_interned(frame, frames, frame_keys)
            parent, prior_stars = geometry, stars
        stop = record["termination"]
        cases[key] = {**record, "stages": references,
                      "terminal_ref": lookup_interned(stop, stops, stop_keys),
                      "termination": {k: stop[k] for k in ("status", "last_age", "next_age") if k in stop}}

    compressor = zlib.compressobj()
    chunks = [compressor.compress(b"[")]
    for t, array in enumerate((geometries, frames, stops)):
        chunks.append(compressor.compress(b",[" if t else b"["))
        for i, record in enumerate(array):
            if i:
                chunks.append(compressor.compress(b","))
            chunks.append(compressor.compress(json.dumps(record, separators=(",", ":")).encode()))
        chunks.append(compressor.compress(b"]"))
    chunks += [compressor.compress(b"]"), compressor.flush()]
    return {**result, "schema": 4, "cases": cases, "frame_count": len(frames),
            "records_zlib_base64": b64encode(b"".join(chunks)).decode("ascii")}


def load_growth(path=OUT):
    """Read the growth receipt, returning shared immutable-by-convention literal frames."""
    result = json.loads(Path(path).read_text())
    if result["schema"] == 1:
        return result
    assert result["schema"] in (2, 3, 4)
    if result["schema"] == 2:
        geometry_records = result.pop("geometries")
        frames = result.pop("frames")
    elif result["schema"] == 3:
        geometry_records = result.pop("geometries")
        frames = json.loads(zlib.decompress(b64decode(result.pop("frames_zlib_base64"))))
        assert len(frames) == result["frame_count"]
    else:
        geometry_records, frames, stops = json.loads(zlib.decompress(b64decode(result.pop("records_zlib_base64"))))
        assert len(frames) == result["frame_count"]
        for record in result["cases"].values():
            record["termination"] = stops[record.pop("terminal_ref")]
    geometries = []
    for parent, added in geometry_records:
        geometries.append(added if parent is None else geometries[parent] + added)
    for frame in frames:
        frame["stars"] = geometries[frame.pop("geometry")]
        for field, birth_field in DERIVED.items():
            frame[field] = {str(row["knot"]): row[birth_field] for row in frame["births"]}
        if frame.get("status") == "extend":
            frame["demand_at_birth"] = {str(row["knot"]): row["demand"] for row in frame["births"]}
    for record in result["cases"].values():
        record["stages"] = {age: frames[ref] for age, ref in record["stages"].items()}
    return result


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--through", type=int)
    parser.add_argument("--literal", action="store_true")
    args = parser.parse_args()
    design, specs = read_inputs()
    if args.through is not None and not 1 <= args.through <= design["age_limit"]:
        parser.error("--through must be within the frozen ages 1 through 6")
    controls = tiny_allocations()
    cases = dict(fixture_runs(design, specs, through=args.through))
    checks = fixture_controls(specs, cases, design)
    result = {
        "schema": 1, "sha256": design["sha256"],
        "caps": {"junctions": design["cap_knots"], "distinctions": design["cap_distinctions"]},
        "age_limit": design["age_limit"] if args.through is None else args.through,
        "family_counts": dict(Counter(r["family"] for r in cases.values())),
        "termination_counts": dict(Counter(r["termination"]["status"] for r in cases.values())),
        "controls": {"tiny_allocations": controls, **checks}, "cases": cases,
    }
    artifact = result if args.literal else pack(result)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile("w", dir=args.out.parent, delete=False) as out:
        path = Path(out.name)
        json.dump(artifact, out, separators=(",", ":"))
        out.write("\n")
    path.replace(args.out)
    summary = {k: v for k, v in result.items() if k not in {"controls", "cases"}}
    print(json.dumps({**summary, "schema": artifact["schema"], "bytes": args.out.stat().st_size}))


if __name__ == "__main__":
    main()
