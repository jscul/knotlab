"""Export complete bounded stages of the established cheapest parity growth."""

from argparse import ArgumentParser
from collections import Counter, defaultdict, deque
from functools import cache, lru_cache
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations, product
import json
from math import comb
from pathlib import Path
import sys
from tempfile import NamedTemporaryFile
from types import MethodType, SimpleNamespace


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
INPUTS = HERE / "inputs.json"
STAGES = ROOT / "artifacts" / HERE.parent.name / HERE.name / "stages.json"
STARTLIB = ROOT / (
    "experiments/FIRST-KNOT-20261118-001B/FIRST-KNOT-20261118-001B-E001_two_knots/startlib.py"
)
FASTLIB = ROOT / (
    "experiments/JOIN-GROWTH-20261118-001B/JOIN-GROWTH-20261118-001B-E001_joins/fastlib.py"
)


def import_file(name, path):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@cache
def production():
    return import_file("eddy_world_startlib", STARTLIB), import_file("eddy_world_fastlib", FASTLIB)


@lru_cache(maxsize=2)
def _read_stages(path, mtime_ns):
    return json.loads(path.read_text())


def load_study(*, path=STAGES):
    path = Path(path).resolve()
    return _read_stages(path, path.stat().st_mtime_ns)


def load_stage(case, age, *, path=STAGES):
    """Return one literal stage, with unrestricted use of the evaluator metadata."""
    return load_study(path=path)["cases"][case]["stages"][str(age)]


def source_stars(case):
    """Assign the shared source IDs in frozen input order, and then loose IDs."""
    if "stars" in case:
        return [sorted(row) for row in case["stars"]]
    sizes, meetings = case["sizes"], case["meetings"]
    stars = [[] for _ in sizes]
    for bit, (u, v) in enumerate(meetings):
        if not (0 <= u < len(sizes) and 0 <= v < len(sizes) and u != v):
            raise ValueError(f"invalid meeting {u, v}")
        stars[u].append(bit)
        stars[v].append(bit)
    bit = len(meetings)
    for j, arity in enumerate(sizes):
        if len(stars[j]) > arity:
            raise ValueError(f"junction {j} holds too many shared distinctions")
        count = arity - len(stars[j])
        stars[j].extend(range(bit, bit + count))
        bit += count
    return stars


def reached(neighbors, source, omitted=-1):
    seen = {source}
    queue = deque([source])
    while queue:
        v = queue.popleft()
        for w in neighbors[v] - seen - {omitted}:
            seen.add(w)
            queue.append(w)
    return seen


def maximal_blocks(neighbors, live):
    live = set(live)
    masks = {frozenset(row & live) for row in neighbors}
    contained_at = defaultdict(list)
    maximal = []
    for row in sorted((row for row in masks if len(row) >= 2), key=lambda x: (-len(x), sorted(x))):
        v = min(row, key=lambda j: len(contained_at[j]))
        if any(row <= other for other in contained_at[v]):
            continue
        maximal.append(row)
        for v in row:
            contained_at[v].append(row)
    return sorted(map(sorted, maximal))


@cache
def canonical_projection(pattern):
    """Use K1–K3 directly on small exact port projections."""
    if len(pattern) < 3:
        return False
    masks = [tuple(i for i, label in enumerate(pattern) if label == part)
             for part in sorted(set(pattern))]
    if len(pattern) > 7:
        return len(masks) == 1
    sys.path.insert(0, str(ROOT / "tools"))
    from knotlab.knots import check_knot
    from knotlab.relations import Relation

    names = tuple(str(i) for i in range(len(pattern)))
    rows = frozenset(row for row in product((False, True), repeat=len(names))
                     if all(sum(row[i] for i in group) % 2 == 0 for group in masks))
    result = check_knot(Relation(names, rows), names[:-1], names[-1]).is_knot
    assert result == (len(masks) == 1)
    return result


def qualify_source(state, live, groups):
    """Project each source support by components after removing its junction."""
    stars, owners = state.bits_of, state.owner
    outside = len(stars)
    if len(reached(state.nbr, 0)) != outside:
        raise ValueError("source junctions must form a connected presentation")
    wired = [set(row) for row in state.nbr] + [set()]
    for sites in owners.values():
        if len(sites) == 1:
            v = sites[0]
            wired[v].add(outside)
            wired[outside].add(v)
    demand = Counter(v for group in groups for v in group)
    checks = []
    for v, row in enumerate(stars):
        components = {}
        parts = []
        pattern = []
        for bit in row:
            other = next((w for w in owners[bit] if w != v), outside)
            if other not in components:
                index = len(parts)
                components.update((w, index) for w in reached(wired, other, v))
                parts.append([])
            part = components[other]
            parts[part].append(bit)
            pattern.append(part)
        checks.append({
            "junction": v, "projection_checks": parts,
            "allowed_projected_rows": 1 << (len(row) - len(parts)),
            "canonical_K1_K3": canonical_projection(tuple(pattern)),
            "checked_with_knotlab": 3 <= len(row) <= 7,
        })
    opens = {v: len(state.loose(v)) for v in live}
    s3 = all(len(g) == 2 for g in groups)
    s4 = all(len(state.nbr[u] & state.nbr[v]) <= 1 for u, v in combinations(live, 2))
    no_stall = all(opens[v] >= demand[v] for v in live)
    unique = len({tuple(row) for row in stars}) == len(stars)
    return {
        "junctions": checks,
        "canonical": unique and all(row["canonical_K1_K3"] for row in checks),
        "unique_supports": unique,
        "live_junctions": live,
        "source_demand": {str(v): demand[v] for v in live},
        "source_loose_counts": {str(v): opens[v] for v in live},
        "DOUBLE_IDENT": {
            "S3": s3, "S4": s4, "S0": no_stall, "at_least_two_loose": sum(opens.values()) >= 2,
            "in_class": s3 and s4 and no_stall and sum(opens.values()) >= 2,
        },
    }


def snapshot(state, age, born, data, origins, marks):
    loose = {str(v): row for v in state.live if (row := state.loose(v))}
    live = list(map(int, loose))
    assert all(v in born for v in live)
    assert len(state.basis) == len(state.bits_of) - (not loose)
    return {
        "age": age,
        "stars": [list(row) for row in state.bits_of],
        "born": born,
        "live": live,
        "loose": loose,
        "growing_end": [{"junction": v, "support": list(state.bits_of[v]), "loose": loose[str(v)]}
                        for v in live],
        "candidate_blocks": maximal_blocks(state.nbr, live),
        "source_coordinate_maps": {"declared": marks, "ancestry": list(origins)},
        "junction_count": len(state.bits_of),
        "distinction_count": state.nbits,
        "equation_rank": len(state.basis),
        "state_dimension": state.nbits - len(state.basis),
        **data,
    }


def forecast(state, groups, fast, caps):
    live = [v for v in state.live if state.loose(v)]
    if not live:
        return {"status": "closed"}
    loose = {v: state.loose(v) for v in live}
    used = Counter(v for g in groups for v in g)
    shortages = {str(v): used[v] - len(loose[v]) for v in live if used[v] > len(loose[v])}
    if shortages:
        return {"status": "stall", "shortages": shortages}
    parents = [tuple(sorted(g)) for g in groups]
    parents += [(v,) for v in live for _ in range(len(loose[v]) - used[v])]
    total_loose = sum(map(len, loose.values()))
    old_count = len(state.bits_of)
    projected_count = old_count + len(parents)
    if projected_count > caps["junctions"]:
        return {"status": "junction_cap", "planned_new_junctions": len(parents),
                "planned_total_junctions": projected_count,
                "planned_total_distinctions_lower": state.nbits + sum(
                    max(3 - len(row), 1) for row in parents if len(row) != total_loose)}

    neighbors = defaultdict(set)
    born = list(range(old_count, projected_count))
    for v, row in zip(born, parents, strict=True):
        for p in row:
            neighbors[v].add(p)
            neighbors[p].add(v)
    next_groups = fast.groups_among(SimpleNamespace(nbr=neighbors), born)
    demand = Counter(v for g in next_groups for v in g)
    fresh = [demand[v] if len(row) == total_loose else max(demand[v], 3 - len(row), 1)
             for v, row in zip(born, parents, strict=True)]
    projected_width = state.nbits + sum(fresh)
    if projected_width > caps["distinctions"]:
        return {"status": "distinction_cap", "planned_new_junctions": len(parents),
                "planned_total_junctions": projected_count, "planned_total_distinctions": projected_width}
    taken = Counter()
    consumed = []
    for row in parents:
        used_bits = []
        for p in row:
            used_bits.append((p, loose[p][taken[p]]))
            taken[p] += 1
        consumed.append(used_bits)
    assert all(taken[v] == len(bits) for v, bits in loose.items())
    return {"status": "extend", "parents": parents, "fresh": fresh, "consumed": consumed,
            "born": born, "next_groups": next_groups, "demand": demand,
            "lookahead_maximum_group": max(map(len, next_groups), default=0)}


def advance(state, plan, policy, origins):
    prior_width = state.nbits
    prior_rank = len(state.basis)
    assert state.step(policy, None)["new"] == len(plan["born"])
    assert state.implied_mismatch == 0
    parent_sets = {}
    consumed = {}
    fresh = {}
    implied = []
    fresh_id = prior_width
    for j, row, inputs, k in zip(plan["born"], plan["parents"], plan["consumed"], plan["fresh"], strict=True):
        fresh_bits = list(range(fresh_id, fresh_id + k))
        source_bits = [bit for _, bit in inputs]
        assert state.bits_of[j] == source_bits + fresh_bits
        assert state.parents[j] == len(row) and state.fresh[j] == k
        assert state.demand_at_birth[j] == plan["demand"][j]
        assert all(state.owner[bit] == [p, j] for p, bit in inputs)
        assert all(state.owner[bit] == [j] for bit in fresh_bits)
        origins.append(sorted({source for p in row for source in origins[p]}))
        parent_sets[str(j)] = list(row)
        consumed[str(j)] = [list(pair) for pair in inputs]
        fresh[str(j)] = fresh_bits
        if not k:
            implied.append(j)
        fresh_id += k
    assert fresh_id == state.nbits
    assert prior_rank + len(plan["born"]) - len(implied) == len(state.basis)
    return {
        "parent_sets": parent_sets, "consumed": consumed, "fresh": fresh, "implied": implied,
        "demand_at_birth": {str(j): plan["demand"][j] for j in plan["born"]},
        "lookahead_maximum_group": plan["lookahead_maximum_group"],
        "old_states_preserved": True,
    }


def grow_case(case, max_age, caps):
    engine, fast = production()
    stars = source_stars(case)
    if not stars or any(len(row) != len(set(row)) or not row for row in stars):
        raise ValueError(f"{case['id']} has an empty or repeated distinction in a support")
    bits = {bit for row in stars for bit in row}
    if bits != set(range(len(bits))):
        raise ValueError(f"{case['id']} must use consecutive source distinction IDs")
    if len(stars) > caps["junctions"] or len(bits) > caps["distinctions"]:
        raise ValueError(f"{case['id']} already exceeds the study's physical size limits")
    state = engine.from_junctions(stars)
    state.groups_among = MethodType(fast.groups_among, state)
    live = [v for v in state.live if state.loose(v)]
    groups = state.groups_among(live)
    source = qualify_source(state, live, groups)
    if source["canonical"] != case.get("expect_canonical", True):
        raise ValueError(f"{case['id']} unexpected source K1–K3 verdict: {source}")
    marks = case.get("roles", case.get("source_coordinate_maps", {}))
    origins = [[v] for v in range(len(stars))]
    data = {"parent_sets": {}, "consumed": {}, "fresh": {}, "implied": []}
    stages = {"0": snapshot(state, 0, list(range(len(stars))), data, origins, marks)}
    stop = {"status": "age_limit", "last_age": max_age}
    for age in range(1, max_age + 1):
        live = [v for v in state.live if state.loose(v)]
        if len(live) <= 18:
            assert state.groups_among(live) == type(state).groups_among(state, live)
        plan = forecast(state, groups, fast, caps)
        if plan["status"] != "extend":
            stop = {"last_age": age - 1, "next_age": age, **plan}
            break
        data = advance(state, plan, engine.F.fewest, origins)
        stages[str(age)] = snapshot(state, age, plan["born"], data, origins, marks)
        groups = plan["next_groups"]
    if not stages[next(reversed(stages))]["live"]:
        stop = {"status": "closed", "last_age": int(next(reversed(stages)))}
    return {"input": case, "qualification": source, "stages": stages, "termination": stop}


def run_document(document, input_sha256):
    caps = document["caps"]
    cases = document["cases"]
    if isinstance(cases, dict):
        cases = [{"id": case, **value} for case, value in cases.items()]
    assert len({case["id"] for case in cases}) == len(cases)
    return {
        "schema": 1,
        "input_sha256": input_sha256,
        "caps": caps,
        "cases": {
            case["id"]: grow_case(case, case.get("max_age", document["max_age"]), caps) for case in cases
        },
    }


def source_map(record):
    stage = record["stages"]["0"]
    baseline = record["qualification"]
    live = stage["live"]
    source_count = len(stage["stars"])
    blocks = {i: tuple(row) for i, row in enumerate(stage["candidate_blocks"], start=source_count)}
    together = defaultdict(list)
    neighbors = defaultdict(set)
    for block, row in blocks.items():
        neighbors[block].update(row)
        for v in row:
            neighbors[v].add(block)
            together[v].append(block)
    loose = {v: len(stage["loose"][str(v)]) for v in live}
    spare = {v: loose[v] - baseline["source_demand"][str(v)] for v in live}
    rays = {v: spare[v] * max(0, 3 - loose[v]) for v in live}
    pieces = []
    remaining = set(live)
    while remaining:
        piece = reached(neighbors, min(remaining))
        points = set(live) & piece
        remaining -= points
        rank = sum(len(neighbors[v]) for v in piece) // 2 - len(piece) + 1
        rays_in_piece = [v for v in sorted(points) for _ in range(rays[v])]
        assert rank or rays_in_piece
        profile = {"source_junctions": len(points), "cycle_rank": rank,
                   "endless_chain_holders": rays_in_piece}
        if rank == 1:
            degree = {v: len(neighbors[v]) for v in piece}
            tips = deque(v for v, d in degree.items() if d == 1)
            while tips:
                v = tips.popleft()
                degree[v] = 0
                for w in neighbors[v]:
                    if degree[w]:
                        degree[w] -= 1
                        if degree[w] == 1:
                            tips.append(w)
            core = {v for v, d in degree.items() if d > 0}
            core_spares = sum(spare[v] for v in points & core)
            arms = sorted((u, v) for u in core for v in neighbors[u] - core)
            covered_arms = set()
            ends = []
            for u, v in arms:
                previous = u
                while True:
                    assert v not in covered_arms and v not in core
                    covered_arms.add(v)
                    following = neighbors[v] - {previous}
                    if not following:
                        assert rays[v] == spare[v] == 1
                        ends.append(v)
                        break
                    assert len(following) == 1 and spare.get(v, 0) == 0
                    previous, v = v, next(iter(following))
            assert covered_arms == piece - core
            assert sorted(ends) == rays_in_piece and all(loose[v] >= 3 for v in points & core if spare[v])
            profile.update(cycle_source_junctions=len(points & core),
                           cycle_leftovers=core_spares, attached_endless_paths=sorted(ends))
        pieces.append(profile)
    return live, blocks, together, loose, spare, pieces


def cluster_counts(live, blocks, together, loose, spare, size_limit):
    """Count by size and number of source-type points on the unrolled map."""
    def multiply(left, right):
        result = Counter()
        for (n, p), a in left.items():
            for (m, q), b in right.items():
                if n + m <= size_limit:
                    result[n + m, p + q] += a * b
        return result

    point = {}
    for v in live:
        ray_count = max(0, 3 - loose[v])
        optional = {(0, 0): 1, (1, 0): 1}
        if ray_count:
            for k in range(1, size_limit):
                optional[k + 1, 0] = comb(k + ray_count - 1, ray_count - 1)
        point[v] = {(1, 1): 1}
        for _ in range(spare[v]):
            point[v] = multiply(point[v], optional)

    def rooted(v, entered, messages):
        result = point[v]
        for block in together[v]:
            if block != entered:
                for w in blocks[block]:
                    if w != v:
                        result = multiply(result, messages[w, block] | {(0, 0): 1})
        return result

    messages = {(v, block): {} for v in live for block in together[v]}
    for _ in range(size_limit - 1):
        messages = {label: rooted(*label, messages) for label in messages}
    pointed = Counter()
    for v in live:
        pointed.update(rooted(v, None, messages))
    unpointed = [0] * size_limit
    for (n, k), count in pointed.items():
        assert k and count % k == 0
        unpointed[n - 1] += count // k
    return unpointed


def verify_export(result):
    receipts = {}
    for case, record in result["cases"].items():
        qualification = record["qualification"]
        assert qualification["canonical"] and qualification["DOUBLE_IDENT"]["in_class"]
        assert len(qualification["live_junctions"]) == len(record["stages"]["0"]["stars"])
        live, blocks, at, loose, spare, pieces = source_map(record)
        observed = [len(s["born"]) for s in record["stages"].values()]
        expected = cluster_counts(live, blocks, at, loose, spare, len(observed))
        assert expected == observed, (case, expected, observed)
        termination = record["termination"]
        receipt = {"matched_cluster_sizes": len(observed), "map_pieces": pieces,
                   "born_by_age": observed, "termination": termination}
        if termination["status"] == "junction_cap":
            # Reconstruct the final stage and price the omitted round without a birth.
            engine, fast = production()
            stage = record["stages"][str(termination["last_age"])]
            state = engine.from_junctions(stage["stars"])
            state.live = stage["live"]
            groups = fast.groups_among(state, state.live)
            limits = {"junctions": termination["planned_total_junctions"], "distinctions": 0}
            plan = forecast(state, groups, fast, limits)
            assert plan["status"] == "distinction_cap"
            assert plan["planned_total_junctions"] == termination["planned_total_junctions"]
            receipt["prospective_total_distinctions"] = plan["planned_total_distinctions"]
        receipts[case] = receipt
    if "C1" in receipts:
        cut = result["cases"]["C1"]
        joined = result["cases"]["J1"]
        assert cut["qualification"]["source_loose_counts"] == joined["qualification"]["source_loose_counts"]
        before = {tuple(sorted(pair)) for pair in joined["input"]["meetings"]}
        after = {tuple(sorted(pair)) for pair in cut["input"]["meetings"]}
        ring = joined["input"]["roles"]["rings"][0]
        assert before - after == {tuple(sorted(ring[2:4]))} and after <= before
        assert receipts["C1"]["map_pieces"][0]["cycle_rank"] == 0
        assert receipts["C1"]["map_pieces"][1]["cycle_rank"] == 0
    return receipts


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, default=INPUTS)
    parser.add_argument("--output", type=Path, default=STAGES)
    parser.add_argument("--verify", action="store_true",
                        help="check an existing export, including independent map counts, without writing")
    args = parser.parse_args()
    raw = args.inputs.read_bytes()
    result = run_document(json.loads(raw), sha256(raw).hexdigest())
    if args.verify:
        assert load_study(path=args.output) == result, "literal export differs from a fresh replay"
        print(json.dumps(verify_export(result), indent=2))
        return
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile("w", dir=args.output.parent, suffix=".json", delete=False) as stream:
        temporary = Path(stream.name)
        try:
            json.dump(result, stream, separators=(",", ":"))
            print(file=stream)
            stream.flush()
            temporary.replace(args.output)
        finally:
            temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
