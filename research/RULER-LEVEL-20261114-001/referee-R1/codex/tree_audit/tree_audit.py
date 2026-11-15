"""Independent Theorem-A audit; imports only the prior independent referees.

No producer functions, forest/ruler shortcut in exact search, or subprocesses.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools as it
import json
import os
from pathlib import Path
import random
import resource
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[5]
REF = ROOT / "research/LEVEL-REACH-20261114-001/referee-R1/codex"
sys.path.insert(0, str(REF))
import fresh_pattern as fp
import fresh_search as fs

spec = importlib.util.spec_from_file_location("independent_brute_supports", REF / "brute_audit/brute_supports.py")
brute = importlib.util.module_from_spec(spec)
spec.loader.exec_module(brute)

SEED = "tree-referee-R1-fresh-20261115"


def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(",", ":")).encode()).hexdigest()


def fresh_keys(count):
    rng = random.Random(SEED)
    keys = []
    for _ in range(count):
        s = rng.randrange(1, 6)
        swaps = tuple(rng.randrange(2) for _ in range(s))
        d0 = tuple(rng.randrange(s) for _ in range(s))
        d1 = tuple(rng.randrange(s) for _ in range(s))
        w = len(fp.previous.words(s))
        g, h0, h1 = [rng.randrange(w) for _ in range(3)]
        keys.append((s, swaps, d0, d1, (tuple(sorted((3*g, 3*h0+1, 3*h1+2))),)))
    return keys


def incidence(knots, nvars):
    """Union-find detects cycles, including the two-shared-distinction cycle."""
    size = nvars + len(knots)
    parents = list(range(size))
    def find(x):
        while parents[x] != x:
            parents[x] = parents[parents[x]]
            x = parents[x]
        return x
    cycles = 0
    for i, row in enumerate(knots):
        q = nvars+i
        for v in row:
            a, b = find(q), find(v)
            if a == b:
                cycles += 1
            else:
                parents[b] = a
    components = len({find(x) for x in range(size)})
    pair_use = {}
    for i, row in enumerate(knots):
        for pair in it.combinations(row, 2):
            pair_use.setdefault(pair, []).append(i)
    repeated_pairs = [{"pair": list(pair), "knots": ids}
                      for pair, ids in pair_use.items() if len(ids) > 1]
    return {"acyclic": cycles == 0, "cycle_rank": cycles,
            "components": components, "connected": components == 1,
            "no_pair_of_knots_shares_two": not repeated_pairs,
            "repeated_pairs": repeated_pairs}


def structure(knots, N):
    nvars = (1 << (N+1))-1
    upper = [0]*nvars
    lower = [0]*nvars
    parent = {}
    children = {}
    correct_type = True
    for row in knots:
        levs = [fp.level(v) for v in row]
        lo = min(levs)
        ups = [v for v in row if fp.level(v) == lo]
        downs = [v for v in row if fp.level(v) == lo+1]
        typed = len(ups) == 1 and len(downs) == 2
        correct_type &= typed
        if typed:
            u = ups[0]
            upper[u] += 1
            children.setdefault(u, []).extend(downs)
            for v in downs:
                lower[v] += 1
                parent[v] = u
    inv = incidence(knots, nvars)
    valid_addresses = all(0 <= v < nvars for row in knots for v in row)
    unique_triples = len(knots) == len(set(map(tuple, knots)))
    unique_upper = all(upper[v] == int(fp.level(v) < N) for v in range(nvars))
    unique_lower = all(lower[v] == int(v != 0) for v in range(nvars))
    root_ascents = True
    chain_checks = 0
    chain_failure = None
    if correct_type and unique_upper and unique_lower:
        for v in range(nvars):
            x = v
            for _ in range(fp.level(v)):
                x = parent.get(x, -1)
            if x != 0:
                root_ascents = False
        for v in range(nvars):
            x = v
            for target in range(fp.level(v)+1, N+1):
                cs = children.get(x, [])
                if len(cs) != 2 or any(fp.level(y) != target for y in cs):
                    chain_failure = {"start": v, "target": target, "current": x}
                    break
                x = cs[0]
                chain_checks += 1
            if chain_failure:
                break
    else:
        root_ascents = False
        chain_failure = {"reason": "parent/child premise fails"}
    flags = {
        "addresses_valid": valid_addresses,
        "three_distinct_per_knot": all(len(row) == len(set(row)) == 3 for row in knots),
        "distinct_knots": unique_triples,
        "expected_knot_count": len(knots) == (1 << N)-1,
        "one_upper_two_lower": correct_type,
        "upper_unique_at_all_nontop_levels": unique_upper,
        "lower_unique_except_root": unique_lower,
        "all_addresses_ascend_to_root": root_ascents,
        "descending_chains_from_every_address_at_every_available_length": chain_failure is None,
        "incidence_acyclic": inv["acyclic"],
        "incidence_connected": inv["connected"],
        "no_pair_of_knots_shares_two": inv["no_pair_of_knots_shares_two"],
    }
    nonprefix_parents = 0
    for v, u in parent.items():
        vn, un = fp.level(v), fp.level(u)
        vx, ux = v-((1 << vn)-1), u-((1 << un)-1)
        nonprefix_parents += int(vx >> 1 != ux)
    return {"all_pass": all(flags.values()), "flags": flags,
            "N": N, "nvars": nvars, "knots": len(knots),
            "incidence": inv, "chain_checks": chain_checks,
            "chain_failure": chain_failure, "pattern_sha256": digest(knots),
            "nonprefix_parent_count": nonprefix_parents}


def automorphisms(key, N):
    """Finite permutation, length, prefix, and letterwise agreement checks."""
    cat = fp.previous.words(key[0])
    prev_images = None
    checked_images = 0
    for n in range(N+1):
        maps = fp.previous.state_actions(key, n)
        images = []
        for word in cat:
            image = list(range(1 << n))
            direct = list(range(1 << n))
            for q in reversed(word):
                image = [maps[q][x] for x in image]
                direct = [fp.previous.direct_state(key, q, x, n) for x in direct]
            assert image == direct, ("word_action_disagreement", key, n, word)
            assert sorted(image) == list(range(1 << n)), ("not_bijection", key, n, word)
            if n:
                assert all(image[x] >> 1 == prev_images[len(images)][x >> 1]
                           for x in range(1 << n)), ("prefix_failure", key, n, word)
            checked_images += len(image)
            images.append(image)
        prev_images = images
    return {"all_registered_words_pass": True, "catalogue_size": len(cat),
            "depth": N, "word_address_images_checked": checked_images}


def structural_run(count):
    rows = []
    action_rows = []
    for j, key in enumerate(fresh_keys(count)):
        action_rows.append({"case": j, **automorphisms(key, 7)})
        for N in (0, 1, 2, 4, 6, 7, 9):
            start = time.perf_counter()
            knots = fp.build(key, N)
            # Two other prior-referee constructions, not producer agreement.
            direct = fp.direct_build(key, N)
            loop = brute.placement_pattern(key, N)
            assert knots == direct == loop, ("builder_disagreement", j, N)
            checked = structure(knots, N)
            assert checked["all_pass"], ("structure_failure", j, key, checked)
            rows.append({"case": j, "key": key, "three_referee_builds_agree": True,
                         **checked, "seconds": time.perf_counter()-start})
        if j % 20 == 0:
            print(json.dumps({"phase": "structural", "descriptions_done": j+1,
                              "patterns_done": len(rows)}), flush=True)
    return {"descriptions": count, "patterns": len(rows),
            "all_pass": all(r["all_pass"] for r in rows),
            "word_checks": action_rows, "rows": rows}


def controls_run():
    plain = (1, (0,), (0,), (0,), ((0, 1, 2),))
    base = fp.build(plain, 2)
    # All triples distinct; these test mathematical content, not a marker.
    specs = [
        ("two_knots_share_two", sorted(set(base + [(0, 1, 3)])), 2,
         ["incidence_acyclic", "no_pair_of_knots_shares_two"]),
        ("long_cycle_with_only_single_overlaps", [(0, 1, 2), (2, 3, 4), (0, 4, 5)], 2,
         ["incidence_acyclic"]),
        ("missing_parent_disconnected", base[1:], 2,
         ["incidence_connected", "lower_unique_except_root"]),
        ("one_lower_duplicate_parent", sorted(set(base + [(1, 3, 5)])), 2,
         ["upper_unique_at_all_nontop_levels", "lower_unique_except_root"]),
        ("only_within_level", [(3, 4, 5)], 2,
         ["one_upper_two_lower"]),
    ]
    results = []
    for name, knots, N, gates in specs:
        result = structure(knots, N)
        failures = [g for g in gates if not result["flags"][g]]
        assert failures == gates, ("malformed_control_not_rejected", name, result, gates)
        assert not result["all_pass"]
        results.append({"name": name, "knots": knots, "gates_expected_false": gates,
                        "rejected": True, "result": result})
    # Independently enumerate *every* state and support on these tiny relations.
    tiny = [
        ("one_knot", [(0, 1, 2)], 3, [0], [2]),
        ("two_step_tree", [(0, 1, 2), (2, 3, 4)], 5, [0], [4]),
        ("connected_cycle_no_cross_bond", [(0, 1, 2), (1, 2, 3)], 4, [0], [3]),
        ("disconnected", [(0, 1, 2), (3, 4, 5)], 6, [0], [5]),
    ]
    exact_controls = []
    for name, knots, nvars, A, B in tiny:
        truth = brute.enumerated_bonds(knots, nvars, A, B)
        got = fs.search(knots, nvars, A, B, cap=nvars, seconds=10)
        normalized = "none" if got["L"] == f"> {nvars}" else got["L"]
        assert got["exact"] and normalized == truth["L"], (name, truth, got)
        exact_controls.append({"name": name, "knots": knots, "A": A, "B": B,
                               "truth": truth, "search": got, "agree": True})
    # A root-lane supplied input illustrates why syntactic-A coverage is only
    # sufficient. No root-lane program, conclusion, or output is imported.
    redundant_key = (1, (0,), (0,), (0,), ((1, 3, 5), (3, 6, 7)))
    redundant = []
    for N in (0, 1, 3, 6, 7):
        got = fp.build(redundant_key, N)
        assert got == fp.direct_build(redundant_key, N) == brute.placement_pattern(redundant_key, N)
        assert got == fp.build(plain, N)
        result = structure(got, N)
        assert result["all_pass"]
        redundant.append(result)
    # A finite forest may connect the designated levels through an extra
    # within-level knot without admitting a two-knot descending chain.
    # This is a counterexample to the overview's stronger "no bond otherwise"
    # reading in the theorem's abstract layered-forest setting. It is not
    # claimed to be a registered-description instance.
    detour = [(1, 3, 4), (4, 5, 6), (6, 7, 8)]
    A, B = fs.levels(1, 2)
    detour_search = fs.search(detour, 15, A, B, cap=5, seconds=10)
    detour_brute = brute.least_bond(detour, 15, A, B, cap=5)
    detour_incidence = incidence(detour, 15)
    cross_12 = [set(t) for t in detour if sorted(set(map(fp.level, t))) == [1, 2]]
    cross_23 = [set(t) for t in detour if sorted(set(map(fp.level, t))) == [2, 3]]
    has_descending_two = any(x.intersection(y) for x in cross_12 for y in cross_23)
    assert not has_descending_two and detour_incidence["acyclic"]
    assert detour_search["L"] == detour_brute["L"] == 5
    return {"structural": results, "exact": exact_controls,
            "redundant_non_A_full_tree": {"key": redundant_key, "checks": redundant},
            "overview_detour_counterexample": {"knots": detour, "nvars": 15,
                "k0": 1, "s": 2, "A": A, "B": B, "incidence": detour_incidence,
                "descending_chain_length_two": has_descending_two,
                "independent_search": detour_search, "support_enumeration": detour_brute,
                "not_claimed_registered_description": True}}


def verify_bond(knots, nvars, result):
    oracle = brute.ProjectionOracle(knots, nvars)
    try:
        assert oracle.alive
        support = result["bond"]
        assert oracle.missing(support) is not None
        assert all(oracle.missing(support[:i]+support[i+1:]) is None
                   for i in range(len(support)))
        return {"fresh_brute_projection_check": True, "sat_calls": oracle.calls}
    finally:
        oracle.close()


def exact_run(mode):
    rows = []
    keys = fresh_keys(5)
    # Distinct automata; all chosen cases independent of output.
    cases = ((0, 4, 1, (1, 2, 3)), (0, 5, 1, (1, 2, 3)), (0, 6, 1, (1, 2, 3))) if mode == "smoke" else (
        (1, 6, 1, (1, 2, 3)), (2, 6, 2, (1, 2, 3)),
        (1, 7, 1, (1, 2, 3)), (2, 7, 2, (1, 2, 3)),
        (0, 6, 1, (1, 2, 3)), (4, 6, 2, (1, 2, 3)),
        (0, 7, 1, (1, 2, 3)), (4, 7, 2, (1, 2, 3)))
    for j, N, k0, ss in cases:
        key = keys[j]
        knots = fp.build(key, N)
        assert knots == brute.placement_pattern(key, N)
        checked_structure = structure(knots, N)
        assert checked_structure["all_pass"]
        if j in (0, 4):
            assert checked_structure["nonprefix_parent_count"] > 0
        nvars = (1 << (N+1))-1
        precompiled = fs.compile_existence(knots, nvars, time.monotonic()+30, width_limit=4)
        for s in ss:
            A, B = fs.levels(k0, s)
            result = fs.search(knots, nvars, A, B, cap=s+2, seconds=45,
                               width_limit=4, precompiled=precompiled)
            validation = verify_bond(knots, nvars, result) if isinstance(result["L"], int) else {}
            row = {"case": j, "key": key, "N": N, "k0": k0, "s": s,
                   "nvars": nvars, "knots": len(knots), "pattern_sha256": digest(knots),
                   "nonprefix_parent_count": checked_structure["nonprefix_parent_count"],
                   "expected_from_A": s+2, "search": result, **validation}
            rows.append(row)
            print(json.dumps({"phase": mode, "case": j, "N": N, "k0": k0, "s": s,
                              "L": result["L"], "exact": result["exact"],
                              "seconds": result["stats"].get("seconds")}), flush=True)
    return {"cases": len(cases), "searches": len(rows),
            "all_decided_agree": all(r["search"]["L"] == r["expected_from_A"]
                                    for r in rows if r["search"]["exact"]),
            "undecided": sum(not r["search"]["exact"] for r in rows), "rows": rows}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("structural", "controls", "smoke", "exact"))
    parser.add_argument("--count", type=int, default=120)
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (2300*1024**2, 2300*1024**2))
    started = time.perf_counter()
    if args.phase == "structural":
        result = structural_run(args.count)
    elif args.phase == "controls":
        result = controls_run()
    else:
        result = exact_run(args.phase)
    sources = [Path(__file__), REF/"fresh_pattern.py", REF/"fresh_search.py",
               REF/"brute_audit/brute_supports.py", Path(fp.previous.__file__)]
    out = {"scope_id": "RULER-LEVEL-20261114-001", "phase": args.phase,
           "seed": SEED, "validation": "V2 relative to producer; same-task AI referee, no external replication",
           "seconds": time.perf_counter()-started,
           "peak_rss_KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
           "address_space_limit_MiB": 2300,
           "thread_id": os.environ.get("CODEX_THREAD_ID"),
           "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
           "result": result}
    path = HERE/f"{args.phase}.json"
    path.write_text(json.dumps(out, indent=2)+"\n")
    print(json.dumps({"output": str(path.relative_to(ROOT)), "seconds": out["seconds"],
                      "peak_rss_KiB": out["peak_rss_KiB"]}), flush=True)


if __name__ == "__main__":
    main()
