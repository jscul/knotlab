"""Replay the unrestricted-arity census ordered by positive-age junction count."""

import argparse
from collections import Counter
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations, permutations, product
import json
import os
from pathlib import Path
from shutil import which
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[3]
ARCHIVE = Path("GROWN-END-SWAP-20261119-001/GROWN-END-SWAP-20261119-001-E001_reached")
CPP = Path(__file__).with_suffix(".cpp")
VERIFIER = ROOT / "experiments" / ARCHIVE / "verify.py"
CONNECTED_GRAPHS = (0, 1, 1, 2, 6, 21, 112, 853, 11117, 261080)
SOURCE_VERSION = "ae990a00539d7a2e336afdf8c3628b1ac47370860306c51a581adbe3fa49c718"
COUNTERS = (
    "admissible_histories", "at_most_one_movable", "only_offshoots_next",
    "short_group_equation_certificate", "exact_group_equation_certificate", "exact_successor_certificate",
    "failures", "unresolved", "short_generators_examined", "full_generators_examined",
    "non_equation_full_generators", "successors_measured",
)


def verifier():
    assert sha256(VERIFIER.read_bytes()).hexdigest() == SOURCE_VERSION
    spec = spec_from_file_location("reached_bound_preceding_verifier", VERIFIER)
    v = module_from_spec(spec)
    sys.modules[spec.name] = v
    spec.loader.exec_module(v)
    return v


def geng_args(geng, n, width):
    args = [str(geng), "-cq", str(n)]
    if width:
        bound = min(n * (n - 1) // 2, width - 6)
        assert bound >= n - 1
        args.append(f"{n-1}:{bound}")
    return args


def sweep(binary, geng, env, n, cap, width):
    source = subprocess.Popen(geng_args(geng, n, width), stdout=subprocess.PIPE, env=env)
    try:
        result = subprocess.run([binary, "sweep", str(n), str(cap), str(width)],
                                stdin=source.stdout, capture_output=True, check=True)
    finally:
        source.stdout.close()
        code = source.wait()
    if code:
        raise subprocess.CalledProcessError(code, source.args)
    data = json.loads(result.stdout)
    assert data["predecessor_junctions"] == n
    if not width:
        assert CONNECTED_GRAPHS[n] == data["unlabeled_graphs"]
    return data


def literals(rows):
    return [str(len(rows)), *(f"{len(row)} " + " ".join(map(str, row)) for row in rows)]


def run_binary(binary, form, blocks):
    result = subprocess.run([binary, form], input="\n".join(blocks) + "\n",
                            text=True, capture_output=True, check=True)
    return result.stdout


def resolve_pending(binary, rows):
    pending = [x for p in rows for t in p["reached_tiers"] for x in t.get("pending_successors", ())]
    if not pending:
        return []
    stream = [str(len(pending))]
    for p in pending:
        maps = p["non_equation_generators"]
        width = 1 + max(x for row in p["current"] for x in row)
        stream.extend(literals(p["next"]))
        stream.append(f"{width} {len(maps[0])} {len(maps)}")
        stream.extend(" ".join(map(str, row)) for row in maps)
    lines = run_binary(binary, "wide", stream).splitlines()
    settled = []
    for p, line in zip(pending, lines, strict=True):
        test = json.loads(line)
        assert sum(test[key] for key in ("identity_extensions", "other_extensions", "failed_extensions")) == len(p["non_equation_generators"])
        settled.append({"predecessor_junctions": len(p["start"]), "current_junctions": len(p["current"]), **test})
    return settled


def edge_rows(n, pairs, loose):
    rows = [[] for _ in range(n)]
    for i, (u, v) in enumerate(sorted(pairs)):
        rows[u].append(i)
        rows[v].append(i)
    size = len(pairs)
    for j, count in enumerate(loose):
        rows[j].extend(range(size, size + count))
        size += count
    return rows


def compare_literal(binary, V, start, here, after, image):
    A, B, C = [V.Arrangement.parse(rows) for rows in (start, here, after)]
    assert V.start_audit(A)["census_open_legal"]
    first, second = V.round_replay(A, B), V.round_replay(B, C)
    result = json.loads(run_binary(binary, "control", [*literals(here), *literals(after), " ".join(map(str, image))]))
    left = V.exact_table(B, 1 << 18)[0]
    right = V.exact_table(C, 1 << 18)[0]
    for name, table in (("current", left), ("successor", right)):
        expected = [9999 if value is None else value+1 for value in table.values()]
        assert result.pop(name + "_K_upper") == expected
    assert result["old_table_isometry"] == all(
        val == left[tuple(sorted((image[x], image[y])))] for (x, y), val in left.items())
    if result["old_pair"][0] >= 0:
        x, y = result["old_pair"]
        assert result["successor_K"] == [right[x,y]+1, right[tuple(sorted((image[x], image[y])))]+1]
    return result, first, second


def controls(binary):
    V = verifier()
    past = json.loads((ROOT / "artifacts" / ARCHIVE / "construct_6.json").read_text())
    old = past["a"]
    perm = [q for _, q in sorted(past["permutation"])]
    meet_twice, _, _ = compare_literal(binary, V, old["start"], old["current"], old["next"], perm)
    assert meet_twice["fixes_live_supports"] and meet_twice["old_table_isometry"] and not meet_twice["extends"]

    pairs = [(0, 2), (1, 2), (0, 3), (1, 3), (2, 3), (0, 4), (0, 5), (0, 6)]
    seed = edge_rows(7, pairs, [0, 2, 0, 0, 2, 2, 2])
    out = json.loads(run_binary(binary, "rounds", literals(seed)))
    here, after = out["current"], out["next"]
    A, B = V.Arrangement.parse(here), V.Arrangement.parse(after)
    for stage in (V.Arrangement.parse(seed), A, B):
        shared = [tuple(holders) for holders in stage.owners.values() if len(holders) == 2]
        assert len(set(shared)) == len(shared)
    ac, bc = sorted(pairs).index((0, 2)), sorted(pairs).index((1, 2))
    image = list(A.labels)
    image[ac], image[bc] = image[bc], image[ac]
    seven, first, second = compare_literal(binary, V, seed, here, after, image)
    assert seven["current_width"] == 23 and len(here) == 12
    assert seven["fixes_live_supports"] and seven["old_table_isometry"] and not seven["extends"]
    identity, _, _ = compare_literal(binary, V, seed, here, after, list(A.labels))
    assert identity["fixes_live_supports"] and identity["old_table_isometry"] and identity["extends"]
    invalid_map = list(A.labels)
    x, y = ac, min(A.loose)
    invalid_map[x], invalid_map[y] = invalid_map[y], invalid_map[x]
    illegal, _, _ = compare_literal(binary, V, seed, here, after, invalid_map)
    assert not illegal["fixes_live_supports"] and not illegal["old_table_isometry"]
    wide_control = resolve_pending(binary, [{"reached_tiers": [{"pending_successors": [
        {"start": seed, "current": here, "next": after, "non_equation_generators": [image]},
    ]}]}])[0]
    assert wide_control["failed_extensions"] == 1
    assert wide_control["first_failed_old_pair"] == seven["old_pair"]
    assert wide_control["first_failed_K"] == seven["successor_K"]
    return {
        "archived_meet_twice": meet_twice, "identity": identity, "invalid_source_map": illegal,
        "rooted_flow_control": wide_control,
        "meet_once_7_to_12": {**seven, "start": seed, "current": here, "next": after,
                              "permutation": image, "first_round": first, "second_round": second},
    }


def referee_growth():
    path = ROOT / "research/FIRST-KNOT-20261118-001/referee-R1"
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
    import referee_first
    return referee_first


def same_arrangement(A, B):
    import networkx as nx

    def graph(arrangement):
        g = nx.Graph()
        loose = Counter(arrangement.loose.values())
        for i, neighbors in enumerate(arrangement.neighbors):
            g.add_node(i, loose=loose[i])
            g.add_edges_from((i,j) for j in neighbors)
        return g

    return nx.is_isomorphic(graph(A), graph(B), node_match=lambda x,y: x["loose"] == y["loose"])


def peel(current, V, RF):
    if any(set(current.neighbors[i]) & current.live for i in current.live):
        return None, {"reason": "current_live_junctions_meet"}
    older = [row for i, row in enumerate(current.stars) if i not in current.live]
    if not older:
        return None, {"reason": "peeling_leaves_no_junction"}
    order = {x:i for i,x in enumerate(sorted(set().union(*older)))}
    rows = [sorted(order[x] for x in row) for row in older]
    attempt = {"candidate_predecessor": rows}
    if any(len(row) < 3 for row in rows):
        return None, {**attempt, "reason": "start_arity_floor"}
    try:
        old = V.Arrangement.parse(rows)
    except ValueError:
        return None, {**attempt, "reason": "disconnected_predecessor"}
    if not V.start_audit(old)["census_open_legal"]:
        return None, {**attempt, "reason": "start_gate"}
    grown = RF.Start(rows)
    state = grown.step(RF.fewest, None, None)
    if state != "ok":
        return None, {**attempt, "reason": "no_complete_round", "regrowth_status": state}
    replayed = V.Arrangement.parse([sorted(s) for s in grown.bits])
    V.round_replay(old, replayed)
    if not same_arrangement(current,replayed):
        return None, {**attempt, "reason": "regrowth_differs", "regrown_rows": [sorted(s) for s in replayed.stars]}
    return old, attempt


def audit_threshold(binary, raw):
    V, RF = verifier(), referee_growth()
    fixtures = [f for p in raw for t in p["reached_tiers"] for f in t.get("all_failing_histories",())]
    histories, descriptions, arrangements = [], [], []
    for i, item in enumerate(fixtures):
        start, current = (V.Arrangement.parse(item[key]) for key in ("start","current"))
        counts = Counter(start.loose.values())
        descriptions.append({"allocation_index": i, "ordinary_shared_pairs": sorted(
            tuple(holders) for holders in start.owners.values() if len(holders)==2),
            "loose_vector": [counts[j] for j in range(len(start.stars))], **item})
        existing = next((i for i, A in enumerate(arrangements) if same_arrangement(A,current)), None)
        if existing is not None:
            histories[existing]["allocation_indices"].append(i)
            continue
        arrangements.append(current)
        permutation = [*item["old_movable_permutation"], *current.labels[len(item["old_movable_permutation"]):]]
        check, _, _ = compare_literal(binary,V,item["start"],item["current"],item["next"],permutation)
        assert check["current_width"] == 23 and check["current_junctions"] == 12
        assert check["old_table_isometry"] and check["fixes_live_supports"] and not check["extends"]
        depth, chain = 0, []
        latest = current
        while True:
            older, attempt = peel(latest,V,RF)
            if older is None:
                break
            latest = older
            depth += 1
            chain.append(attempt)
        assert depth > 0
        histories.append({
            "allocation_indices": [i], "replayed_witness": check,
            "earliest_start_junctions": len(latest.stars), "earliest_start_width": len(latest.labels),
            "reached_age_from_earliest_start": depth, "successful_peels": chain, "first_rejected_peel": attempt,
        })
    return {"failing_allocations": descriptions, "distinct_failing_presentations": histories,
            "fewest_starting_junctions_at_both_current_minima": min(h["earliest_start_junctions"] for h in histories)}


def small_crosscheck(geng, env, cap=7):
    """Independently enumerate literal loose vectors and every pinned table map."""
    import networkx as nx

    V = verifier()
    RF = referee_growth()

    histories, symmetries, mismatches = Counter(), Counter(), Counter()
    for n in range(1, cap-2):
        data = subprocess.check_output(geng_args(geng,n,0), env=env).splitlines()
        for line in data:
            graph = nx.from_graph6_bytes(line)
            edges = [tuple(sorted(e)) for e in graph.edges]
            for loose in product(range(cap-n+1), repeat=n):
                if not any(loose) or any(graph.degree(j) + loose[j] < 3 for j in range(n)):
                    continue
                seed = edge_rows(n, edges, loose)
                if not V.start_audit(V.Arrangement.parse(seed))["census_open_legal"]:
                    continue
                grown = RF.Start(seed)
                if grown.step(RF.fewest, None, None) != "ok":
                    continue
                here = [list(r) for r in grown.bits]
                if not n+3 <= len(here) <= cap:
                    continue
                m = len(here)
                histories[m] += 1
                if len(edges) <= 1:
                    continue
                A = V.Arrangement.parse(here)
                assert grown.step(RF.fewest, None, None) == "ok"
                B = V.Arrangement.parse([list(r) for r in grown.bits])
                k = V.exact_table(A, 1 << 17)[0]
                later = V.exact_table(B, 1 << 17)[0]
                for test in permutations(range(len(edges))):
                    image = dict(zip(A.labels, (*test, *A.labels[len(edges):]), strict=True))
                    if any(k[tuple(sorted((image[x],image[y])))] != value for (x,y),value in k.items()):
                        continue
                    symmetries[m] += int(any(p != q for p, q in image.items()))
                    if any(later[tuple(sorted((image[x],image[y])))] != later[x,y]
                           for x,y in combinations(A.labels,2)):
                        mismatches[m] += 1
                    else:
                        fresh = set(B.labels) - set(A.labels)
                        domain = {q: {image[q]} if q in image else fresh for q in B.labels}
                        ext = V.find_matching(later, later, domain, image)
                        mismatches[m] += ext is None
    return {"cap": cap, "histories": dict(sorted(histories.items())),
            "nonidentity_old_maps": dict(sorted(symmetries.items())), "failing_old_maps": dict(sorted(mismatches.items()))}


def summarize(parts, settled):
    merged = {}
    for p in parts:
        for t in p["reached_tiers"]:
            j = t["junctions"]
            total = merged.setdefault(j, Counter())
            for k in COUNTERS:
                total[k] += t[k]
            total["max_width"] = max(total["max_width"], t["max_width"])
            total["max_measured_successor_junctions"] = max(total["max_measured_successor_junctions"], t["max_measured_successor_junctions"])
    for s in settled:
        total = merged[s["current_junctions"]]
        total["unresolved"] -= 1
        total["failures" if s["failed_extensions"] else "exact_successor_certificate"] += 1
        total["successors_measured"] += 1
        total["max_measured_successor_junctions"] = max(total["max_measured_successor_junctions"], s["successor_junctions"])
    return [{"junctions": j, **values} for j, values in sorted(merged.items())]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cap", type=int, default=11)
    parser.add_argument("--width", type=int, default=0)
    parser.add_argument("--geng", default=which("nauty-geng") or which("geng"))
    parser.add_argument("--geng-library")
    parser.add_argument("--controls-only", action="store_true")
    parser.add_argument("--skip-small-control", action="store_true")
    args = parser.parse_args()
    assert 4 <= args.cap <= (13 if args.width else 11)
    if not args.controls_only and not args.geng:
        parser.error("Install nauty-geng or geng, or pass --geng with an executable path.")
    env = dict(os.environ)
    if args.geng_library:
        env["LD_LIBRARY_PATH"] = args.geng_library
    with TemporaryDirectory(prefix="reached-junction-bound-") as tmp:
        binary = str(Path(tmp) / "reach_bound")
        subprocess.run(["c++", "-O3", "-std=c++20", str(CPP), "-o", binary], check=True)
        checked = controls(binary)
        if args.controls_only:
            print(json.dumps(checked, indent=2))
            return
        raw = []
        for n in range(1, args.cap-2):
            raw.append(sweep(binary, args.geng, env, n, args.cap, args.width))
            print(f"Completed predecessor order {n}", file=sys.stderr, flush=True)
        settled = resolve_pending(binary, raw)
        merged = summarize(raw, settled)
        result = {
            "junction_cap": args.cap, "current_width_cap": args.width or None,
            "preceding_newborn_counts_1_and_2_covered_theoretically": True,
            "predecessor_parts": raw, "large_successor_replays": settled,
            "reached_tiers": merged, "named_controls": checked,
        }
        if not args.width and args.cap >= 7 and not args.skip_small_control:
            small = small_crosscheck(args.geng, env)
            assert small["histories"] == {r["junctions"]: r["admissible_histories"] for r in merged if r["junctions"] <= small["cap"]}
            assert not any(small["failing_old_maps"].values())
            result["independent_small_control"] = small
        if (args.cap,args.width)==(12,23):
            assert not any(s["failed_extensions"] for s in settled)
            result["joint_minimum_audit"] = audit_threshold(binary,raw)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
