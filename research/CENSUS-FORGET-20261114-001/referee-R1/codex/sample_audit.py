"""Fresh offline R1 audit of 120 CENSUS-FORGET families.

Interface: exactly 120 deterministic, verdict-stratified census keys.  Rebuild
the usual greatest fixed point by assignment enumeration, project each R_i by
fresh SAT queries, and decide rectangularity through the nonrectangular-product
automaton.  Reproduce the producer's length-set orbit separately, with its
250000-entry resource cap.  Caps never mean non-forgetting.  No growth theorem
or inference about untested families is made here.

Only the input-language dlang module is imported from experiment directories.
No Python in either prohibited FREE-TARGET or CENSUS-FORGET tree is read or
imported.  All outputs are sample_* files beside this source.
"""
from __future__ import annotations

import os
for _thread_var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_thread_var] = "1"

import collections
import gzip
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import resource
import time

resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))
from pysat.solvers import Solver

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
RESULTS = ROOT / "experiments/CENSUS-FORGET-20261114-001A/CENSUS-FORGET-20261114-001A-E001_forget_census/full/results.jsonl"
CENSUS = ROOT / "artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/families.jsonl.gz"
DLANG = ROOT / "experiments/SHORT-DESC-20261112-001A/SHORT-DESC-20261112-001A-E001_description_census/dlang.py"
SEED = "CENSUS-FORGET-R1-independent-sample-v1"
TARGETED_PREFIXES = {"f25a8e17968d", "3fe70047c198", "f3c4843e45fa", "ec647c80edb0", "c6cbc657bedb"}
DELAY_TARGETED_PREFIXES = {"e8ce853eb78a", "6227f3d37d32"}
READS = {}


def content(path):
    forbidden = ("experiments/FREE-TARGET-20261114-001A/", "experiments/CENSUS-FORGET-20261114-001A/")
    relative = str(path.relative_to(ROOT))
    assert not (path.suffix == ".py" and relative.startswith(forbidden))
    data = path.read_bytes()
    READS[relative] = hashlib.sha256(data).hexdigest()
    return data


def read_rows(path):
    data = content(path)
    if path.suffix == ".gz":
        data = gzip.decompress(data)
    return [json.loads(line) for line in data.splitlines() if line.strip()]


def mask(values):
    result = 0
    for state in values:
        result |= 1 << state
    return result


def project(state, arguments):
    return sum(((state >> variable) & 1) << j for j, variable in enumerate(arguments))


def usual(raw):
    return [(k, own, [(callee, tuple(args)) for callee, args in calls] +
             ([("K", (0, 1, 2))] if any(c == "SELF" and sorted(a) == [0, 1, 2]
                                                  for c, a in calls) else []))
            for k, own, calls in raw]


def self_types(defs):
    return [i for i, (_, _, calls) in enumerate(defs)
            if any(c == "SELF" for c, _ in calls)]


def evaluate(defs, previous):
    """Direct finite assignment enumeration; no dlang evaluation is used."""
    relations = []
    for i, (arity, own, calls) in enumerate(defs):
        allowed = set()
        for state in range(1 << (arity + own)):
            good = True
            for callee, arguments in calls:
                value = project(state, arguments)
                relation = ({1, 2, 3, 4, 5, 6} if callee == "K" else
                            previous[i] if callee == "SELF" else relations[callee])
                if value not in relation:
                    good = False
                    break
            if good:
                allowed.add(state % (1 << arity))
        relations.append(allowed)
    return relations


def limit(defs):
    types = self_types(defs)
    previous = {i: set(range(8)) for i in types}
    history = [{str(i): hex(mask(previous[i])) for i in types}]
    while True:
        all_relations = evaluate(defs, previous)
        current = {i: all_relations[i] for i in types}
        assert all(current[i] <= previous[i] for i in types)
        history.append({str(i): hex(mask(current[i])) for i in types})
        if current == previous:
            return all_relations, current, history
        previous = current


def flatten(defs, which):
    types = set(self_types(defs))
    next_id = defs[which][0]
    calls = []

    def expand(index, actual):
        nonlocal next_id
        arity, own, body = defs[index]
        assert len(actual) == arity
        local = tuple(range(next_id, next_id + own))
        next_id += own
        environment = tuple(actual) + local
        for callee, arguments in body:
            mapped = tuple(environment[a] for a in arguments)
            if callee == "K":
                calls.append(("K", mapped))
            elif callee == "SELF":
                calls.append((index, mapped))
            elif callee in types:
                calls.append((callee, mapped))
            else:
                expand(callee, mapped)

    expand(which, tuple(range(defs[which][0])))
    return next_id, calls


def clauses_for_relation(arguments, allowed):
    return [[-(variable + 1) if (state >> j) & 1 else variable + 1
             for j, variable in enumerate(arguments)]
            for state in range(1 << len(arguments)) if state not in allowed]


def derive_R(size, calls, G, chosen):
    clauses = []
    for j, (callee, arguments) in enumerate(calls):
        if j != chosen:
            allowed = {1, 2, 3, 4, 5, 6} if callee == "K" else G[callee]
            clauses.extend(clauses_for_relation(arguments, allowed))
    result = 0
    with Solver(name="cadical153", bootstrap_with=clauses) as solver:
        for a in range(8):
            incoming = [j + 1 if (a >> j) & 1 else -(j + 1) for j in range(3)]
            for b in range(8):
                outgoing = [v + 1 if (b >> j) & 1 else -(v + 1)
                            for j, v in enumerate(calls[chosen][1])]
                if solver.solve(assumptions=incoming + outgoing):
                    result |= 1 << (8 * a + b)
    # An independent small-block enumeration cross-checks the SAT projection.
    enumerated = None
    if size <= 12:
        enumerated = 0
        for state in range(1 << size):
            if all(j == chosen or project(state, args) in
                   ({1, 2, 3, 4, 5, 6} if c == "K" else G[c])
                   for j, (c, args) in enumerate(calls)):
                enumerated |= 1 << (8 * (state & 7) + project(state, calls[chosen][1]))
        assert result == enumerated
    return result, enumerated is not None


def rectangular(relation, q=8):
    nonzero = set()
    for a in range(q):
        row = (relation >> (q * a)) & ((1 << q) - 1)
        if row:
            nonzero.add(row)
    return len(nonzero) <= 1


def pairs(relation, q):
    return {(a, b) for a in range(q) for b in range(q)
            if (relation >> (q * a + b)) & 1}


def compose_sets(left, right, q):
    return mask(a * q + c for a, b in pairs(left, q)
                for bb, c in pairs(right, q) if b == bb)


def composition_machine(generators, q=8):
    # Each possible left row is mapped to the union of corresponding right rows.
    # No arbitrary product cache can grow across families.
    tables = []
    for generator in generators:
        rows = [(generator >> (q * b)) & ((1 << q) - 1) for b in range(q)]
        table = [0] * (1 << q)
        for subset in range(1, 1 << q):
            bit = subset & -subset
            table[subset] = table[subset ^ bit] | rows[bit.bit_length() - 1]
        tables.append(table)

    def apply(left, label):
        table = tables[label]
        return sum(table[(left >> (q * a)) & ((1 << q) - 1)] << (q * a)
                   for a in range(q))
    return apply


def identity(q):
    return mask(a * q + a for a in range(q))


def verify_lasso(generators, word, q=8):
    if not word or not word.get("cycle"):
        return {"valid": False, "reason": "no nonempty cycle"}
    labels = word.get("prefix", []) + word["cycle"]
    if not all(type(label) is int and 0 <= label < len(generators) for label in labels):
        return {"valid": False, "reason": "invalid label"}
    state = identity(q)
    good = True
    for label in word.get("prefix", []):
        state = compose_sets(state, generators[label], q)
        good &= not rectangular(state, q)
    beginning = state
    before = []
    after = []
    for label in word["cycle"]:
        before.append(hex(state))
        state = compose_sets(state, generators[label], q)
        after.append(hex(state))
        good &= not rectangular(state, q)
    good &= state == beginning
    if "prefix_product" in word:
        good &= beginning == int(word["prefix_product"], 16)
    convention = None
    if "cycle_products" in word:
        recorded = [hex(int(p, 16)) for p in word["cycle_products"]]
        convention = "before each step" if recorded == before else "after each step" if recorded == after else "invalid"
        good &= convention != "invalid"
    return {"valid": bool(good), "prefix_product": hex(beginning),
            "cycle_products_before": before, "cycle_products_after": after,
            "returns_to_same_product": state == beginning,
            "recorded_metadata_convention": convention}


def graph_decision(generators, q=8, max_states=250000):
    """An exact lasso proves non-forgetting; exhausting an acyclic automaton gives r."""
    apply = composition_machine(generators, q)
    initial = identity(q)
    stack = [[initial, 0, 0]]  # relation, next label, longest nonrectangular suffix
    active = {initial: 0}
    closed = {}
    labels = []
    transitions = 0
    while stack:
        state, next_label, longest = stack[-1]
        if next_label == len(generators):
            closed[state] = longest
            del active[state]
            stack.pop()
            if stack:
                labels.pop()
                stack[-1][2] = max(stack[-1][2], longest + 1)
            continue
        stack[-1][1] += 1
        transitions += 1
        target = apply(state, next_label)
        if rectangular(target, q):
            continue
        if target in active:
            at = active[target]
            word = {"prefix": labels[:at], "cycle": labels[at:] + [next_label]}
            check = verify_lasso(generators, word, q)
            assert check["valid"]
            return {"verdict": "non-forgetting", "r": None, "lasso": word,
                    "lasso_check": check, "nonrectangular_states_seen": len(active) + len(closed),
                    "transitions_examined": transitions, "exhausted_nonrectangular_automaton": False}
        if target in closed:
            stack[-1][2] = max(stack[-1][2], 1 + closed[target])
            continue
        if len(active) + len(closed) >= max_states:
            return {"verdict": "capped", "r": None, "reason": "nonrectangular-state resource cap",
                    "nonrectangular_states_seen": len(active) + len(closed),
                    "transitions_examined": transitions, "exhausted_nonrectangular_automaton": False}
        active[target] = len(stack)
        stack.append([target, 0, 0])
        labels.append(next_label)
    return {"verdict": "certified", "r": closed[initial] + 1, "lasso": None,
            "nonrectangular_states_seen": len(closed), "transitions_examined": transitions,
            "exhausted_nonrectangular_automaton": True}


def length_orbit(generators, q=8, cap=250000):
    apply = composition_machine(generators, q)
    current = frozenset(generators)
    seen = {}
    sizes = []
    all_rect = []
    stored = 0
    empty_lengths = []
    certificate_products = None
    r = None
    while current not in seen:
        length = len(sizes) + 1
        if stored + len(current) > cap:
            return {"complete": False, "cap": cap, "completed_lengths": len(sizes),
                    "stored_products": stored, "next_level_products": len(current),
                    "length_set_sizes": sizes, "all_rectangular_by_length": all_rect,
                    "empty_product_lengths": empty_lengths}
        seen[current] = length
        stored += len(current)
        sizes.append(len(current))
        rectangular_level = all(rectangular(p, q) for p in current)
        all_rect.append(rectangular_level)
        if rectangular_level and r is None:
            r = length
            certificate_products = sorted(hex(p) for p in current)
        if 0 in current:
            empty_lengths.append(length)
        current = frozenset(apply(p, label) for p in current for label in range(len(generators)))
    start = seen[current]
    return {"complete": True, "r": r, "repeat_start": start,
            "period": len(sizes) + 1 - start, "length_set_sizes": sizes,
            "all_rectangular_by_length": all_rect, "repeat_all_rectangular": all_rect[start - 1:],
            "stored_products": stored, "empty_product_lengths": empty_lengths,
            "P_r": certificate_products}


def controls():
    product_checks = 0
    graph_checks = 0
    for left in range(16):
        domain = {a for a, _ in pairs(left, 2)}
        image = {b for _, b in pairs(left, 2)}
        assert rectangular(left, 2) == (pairs(left, 2) == set(itertools.product(domain, image)))
        for right in range(16):
            apply = composition_machine([right], 2)
            assert apply(left, 0) == compose_sets(left, right, 2)
            if rectangular(left, 2) or rectangular(right, 2):
                assert rectangular(apply(left, 0), 2)
            product_checks += 1
        for right in range(left, 16):
            generators = [left, right]
            graph = graph_decision(generators, 2)
            orbit = length_orbit(generators, 2)
            assert orbit["complete"] and graph["r"] == orbit["r"]
            assert (graph["verdict"] == "certified") == (orbit["r"] is not None)
            graph_checks += 1
    fixtures = []
    for name, generators, q, expected in [
        ("empty_is_rectangular", [0], 2, 1),
        ("proper_rectangular", [2], 2, 1),
        ("identity_nonforgetting", [9], 2, None),
        ("permutation_period_two", [6], 2, None),
        ("mixed_nonforgetting_choice", [15, 9], 2, None),
        ("first_rectangular_at_two", [2 | 32 | 256], 3, 2),
    ]:
        result = graph_decision(generators, q)
        assert result["r"] == expected
        fixtures.append({"name": name, "result": result})
    false_lasso_rejected = not verify_lasso([15], {"prefix": [], "cycle": [0]}, 2)["valid"]
    assert false_lasso_rejected
    # A cap before a certificate is undecided even when the true answer is finite r.
    capped_fixture = length_orbit([2 | 32 | 256], 3, cap=1)
    assert not capped_fixture["complete"]
    # TOP selects the greatest fixed point; starting at empty gives another one.
    fixed_defs = usual([[3, 0, [["SELF", [0, 1, 2]]]]])
    _, greatest, history = limit(fixed_defs)
    assert greatest == {0: set(range(1, 7))}
    assert evaluate(fixed_defs, {0: set()}) == [set()]
    # The selected call contributes no G; an unselected other-type call does.
    side_calls = [("SELF-TARGET", (0, 1, 2)), (7, (0, 1, 2))]
    side_R, side_enum = derive_R(3, side_calls, {7: set(range(1, 7))}, 0)
    open_R, _ = derive_R(3, side_calls[:1], {}, 0)
    empty_R, _ = derive_R(3, side_calls, {7: set()}, 0)
    assert side_R == mask(8 * a + a for a in range(1, 7))
    assert open_R == identity(8) and empty_R == 0 and side_R != open_R
    return {"passed": True, "two_state_product_checks": product_checks,
            "two_state_generator_pair_graph_vs_orbit_checks": graph_checks,
            "false_lasso_rejected": false_lasso_rejected,
            "cap_is_not_nonforgetting_control": capped_fixture,
            "greatest_vs_least_fixed_point_control": {"greatest_history": history,
                "greatest": hex(mask(greatest[0])), "least": "0x0"},
            "side_call_constraint_projection_control": {"with_side": hex(side_R),
                "without_side": hex(open_R), "impossible_side": hex(empty_R),
                "SAT_vs_enumeration": side_enum}, "named": fixtures}


def stratum(record):
    result = record["result"]
    return "chain" if result["chain"] else "c>=2" if result["c"] >= 2 else "c1_nonchain"


def select_sample(records):
    quotas = {("c>=2", "certified"): 24, ("c>=2", "non-forgetting"): 24,
              ("c>=2", "capped"): 24, ("c1_nonchain", "certified"): 12,
              ("c1_nonchain", "non-forgetting"): 12, ("chain", "certified"): 12,
              ("chain", "non-forgetting"): 12}
    sample = []
    buckets = []
    for (group, verdict), quota in quotas.items():
        candidates = [row for row in records if stratum(row) == group and row["result"]["verdict"] == verdict]

        def rank(row):
            return hashlib.sha256((SEED + "\0" + group + "/" + verdict + "\0" + row["case"]).encode()).hexdigest()

        picked = {}
        if verdict == "certified":
            for r in sorted({row["result"]["r"] for row in candidates}):
                anchor = min((row for row in candidates if row["result"]["r"] == r), key=rank)
                picked[anchor["case"]] = (anchor, "least SHA256 within r=" + str(r))
        assert len(picked) <= quota
        for row in sorted(candidates, key=rank):
            if len(picked) == quota:
                break
            picked.setdefault(row["case"], (row, "least remaining SHA256"))
        for row, reason in picked.values():
            sample.append((row, {"stratum": group, "recorded_verdict": verdict,
                                 "selection_reason": reason, "selection_sha256": rank(row)}))
        buckets.append({"stratum": group, "recorded_verdict": verdict,
                        "population": len(candidates), "sample": len(picked)})
    assert len(sample) == 120 and len({row["case"] for row, _ in sample}) == 120
    return sorted(sample, key=lambda x: (x[1]["stratum"], x[1]["recorded_verdict"], x[0]["case"])), buckets


def main():
    started = time.monotonic()
    records = read_rows(RESULTS)
    sample, buckets = select_sample(records)
    target_matches = [row for row in records if hashlib.sha256(row["case"].encode()).hexdigest()[:12] in TARGETED_PREFIXES]
    assert len(target_matches) == 5
    base_keys = {row["case"] for row, _ in sample}
    for row in target_matches:
        if row["case"] not in base_keys:
            sample.append((row, {"stratum": stratum(row), "recorded_verdict": row["result"]["verdict"],
                                 "selection_reason": "targeted main-lane all-type-target counterexample",
                                 "selection_sha256": hashlib.sha256(row["case"].encode()).hexdigest()}))
    delay_matches = [row for row in records if hashlib.sha256(row["case"].encode()).hexdigest()[:12] in DELAY_TARGETED_PREFIXES]
    assert len(delay_matches) == 2
    previous_keys = {row["case"] for row, _ in sample}
    assert all(row["case"] not in previous_keys for row in delay_matches)
    for row in delay_matches:
        sample.append((row, {"stratum": stratum(row), "recorded_verdict": row["result"]["verdict"],
                             "selection_reason": "targeted main-lane zero-own delaying-type counterexample",
                             "selection_sha256": hashlib.sha256(row["case"].encode()).hexdigest()}))
    keys = {row["case"] for row, _ in sample}
    # Stream the census, retaining only selected rows.
    census_bytes = content(CENSUS)
    census = {row["key"]: row for row in (json.loads(line) for line in gzip.decompress(census_bytes).splitlines())
              if row.get("key") in keys}
    assert set(census) == keys
    content(DLANG)
    spec = importlib.util.spec_from_file_location("permitted_input_dlang", DLANG)
    language = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(language)
    control_results = controls()
    families = []
    all_mismatches = []
    for index, (source, selection) in enumerate(sample):
        case_started = time.monotonic()
        key = source["case"]
        recorded = source["result"]
        raw = json.loads(key)
        defs = usual(raw)
        all_G, G, history = limit(defs)
        # This comparison starts before the shared preparation boundary.
        _, _, language_G = language.depth_sequence(defs, language.TOP)
        language_relations = language.relations(defs, language_G)
        G_language = {i: {j for j, allowed in enumerate(rel) if allowed} for i, rel in language_G.items()}
        all_language = [{j for j, allowed in enumerate(rel) if allowed} for rel in language_relations]
        S = census[key]["S"]
        main_id = len(defs) - 1
        size, calls = flatten(defs, S)
        main_size, main_calls = flatten(defs, main_id)
        selected = [j for j, (callee, _) in enumerate(calls) if callee == S]
        matrices = []
        enumeration_checks = 0
        for chosen in selected:
            relation, checked = derive_R(size, calls, G, chosen)
            matrices.append(relation)
            enumeration_checks += checked
        body_counts = collections.Counter(c for c, _ in calls if c != "K")
        main_counts = collections.Counter(c for c, _ in main_calls if c != "K")
        fresh_chain = body_counts == {S: 1} and main_counts == {S: 1}
        graph = graph_decision(matrices)
        orbit = length_orbit(matrices)
        own_mismatches = []

        def compare(field, fresh, reported):
            if fresh != reported:
                own_mismatches.append({"field": field, "fresh": fresh, "recorded": reported})

        compare("greatest_fixed_point_vs_input_dlang", G, G_language)
        compare("all_definition_relations_vs_input_dlang", all_G, all_language)
        compare("n_defs", len(defs), recorded["n_defs"])
        compare("c", len(selected), recorded["c"])
        compare("chain", fresh_chain, recorded["chain"])
        compare("other_holding_calls_in_main_or_S", any(c not in ("K", S) for c, _ in calls + main_calls), recorded["other_holding_calls"])
        compare("usual_limit_alive", bool(all_G[-1]), census[key]["usual_limit_alive"])
        compare("s_block_size", size, census[key]["s_block_size"])
        compare("main_block_size", main_size, census[key]["main_block_size"])
        compare("R_i", matrices, [int(value, 16) for value in recorded["R_i"]])
        compare("empty_relation", any(value == 0 for value in matrices), recorded["empty_relation"])
        reported_word_check = None
        if recorded["verdict"] != "capped":
            compare("graph.verdict", graph["verdict"], recorded["verdict"])
            compare("graph.r", graph["r"], recorded["r"])
            compare("orbit.complete", orbit["complete"], True)
            if orbit["complete"]:
                for field in ("r", "repeat_start", "period", "length_set_sizes", "all_rectangular_by_length",
                              "repeat_all_rectangular", "stored_products"):
                    compare("semigroup." + field, orbit[field], recorded["semigroup"][field])
                compare("graph_vs_orbit.r", graph["r"], orbit["r"])
            if recorded["verdict"] == "non-forgetting":
                reported_word_check = verify_lasso(matrices, recorded["recurring_word"])
                compare("reported_lasso_valid", reported_word_check["valid"], True)
        else:
            # A fresh decision refines an undecided source row; it does not contradict it.
            compare("recorded_cap_kind", recorded["cap"], "P_n construction product cap 250000")
        if graph["verdict"] == "certified":
            assert orbit["complete"] and orbit["P_r"]
            assert all(rectangular(int(value, 16)) for value in orbit["P_r"])
        other_types = []
        for i in self_types(defs):
            if i != S:
                n, other_calls = flatten(defs, i)
                other_types.append({"definition": i, "flat_own": n - defs[i][0],
                                    "G": hex(mask(G[i])), "flat_calls": [[c, list(a)] for c, a in other_calls]})
        family = {"index": index, "key": key, **selection,
                  "n_defs": len(defs), "S": S, "main": main_id,
                  "main_equals_S": main_id == S, "main_size": main_size, "S_size": size,
                  "c": len(selected), "fresh_chain": fresh_chain,
                  "S_holding_call_counts": dict(body_counts), "main_holding_call_counts": dict(main_counts),
                  "recorded_other_holding_calls": recorded["other_holding_calls"],
                  "fresh_other_holding_calls_in_S": any(c not in ("K", S) for c, _ in calls),
                  "fresh_other_holding_calls_in_main": any(c not in ("K", S) for c, _ in main_calls),
                  "G": {str(i): hex(mask(value)) for i, value in G.items()},
                  "all_definition_port_relations": [hex(mask(value)) for value in all_G],
                  "greatest_fixed_point_history_including_TOP": history,
                  "fixed_point_matches_input_dlang": G == G_language and all_G == all_language,
                  "other_self_holding_types": other_types,
                  "R_i": [{"flat_call_index": j, "arguments": list(calls[j][1]), "hex": hex(relation)}
                          for j, relation in zip(selected, matrices)],
                  "SAT_queries": 64 * len(selected), "SAT_vs_assignment_enumeration_comparisons": enumeration_checks,
                  "fresh_graph_decision": graph, "fresh_length_set_orbit": orbit,
                  "reported_lasso_check": reported_word_check,
                  "recorded_cap": recorded.get("cap"), "mismatches": own_mismatches,
                  "seconds": round(time.monotonic() - case_started, 6)}
        families.append(family)
        all_mismatches.extend({"key": key, **mismatch} for mismatch in own_mismatches)
        print(json.dumps({"completed": index + 1, "stratum": selection["stratum"],
                          "recorded": recorded["verdict"], "fresh": graph["verdict"],
                          "seconds": family["seconds"], "mismatches": len(own_mismatches)}), flush=True)
    summary = {
        "base_stratified_families": 120, "targeted_counterexample_families": 5,
        "targeted_zero_own_delay_families": 2,
        "targeted_counterexamples_already_in_base": sum(row["case"] in base_keys for row in target_matches),
        "sample_families": len(families), "sample_R_i": sum(row["c"] for row in families),
        "SAT_queries": sum(row["SAT_queries"] for row in families),
        "SAT_vs_assignment_enumeration_comparisons": sum(row["SAT_vs_assignment_enumeration_comparisons"] for row in families),
        "all_fixed_points_match_input_dlang": all(row["fixed_point_matches_input_dlang"] for row in families),
        "source_completed_verdicts": sum(row["recorded_verdict"] != "capped" for row in families),
        "source_completed_verdicts_matched": sum(row["recorded_verdict"] != "capped" and
             row["recorded_verdict"] == row["fresh_graph_decision"]["verdict"] for row in families),
        "fresh_decisions": dict(collections.Counter(row["fresh_graph_decision"]["verdict"] for row in families)),
        "sampled_source_caps_fresh_decisions": dict(collections.Counter(row["fresh_graph_decision"]["verdict"]
             for row in families if row["recorded_verdict"] == "capped")),
        "sampled_source_caps_repeat_length_set_cap": sum(not row["fresh_length_set_orbit"]["complete"]
             for row in families if row["recorded_verdict"] == "capped"),
        "sampled_source_caps_length_set_orbit_completed_independently": sum(row["fresh_length_set_orbit"]["complete"]
             for row in families if row["recorded_verdict"] == "capped"),
        "sampled_completed_orbits_reproduced": sum(row["fresh_length_set_orbit"]["complete"]
             for row in families if row["recorded_verdict"] != "capped"),
        "sampled_families_with_nonTOP_self_G": sum(any(value != "0xff" for value in row["G"].values()) for row in families),
        "sampled_families_with_multiple_fixed_point_iterations": sum(len(row["greatest_fixed_point_history_including_TOP"]) > 2 for row in families),
        "sampled_families_with_main_not_S": sum(not row["main_equals_S"] for row in families),
        "sampled_families_with_other_self_types": sum(bool(row["other_self_holding_types"]) for row in families),
        "sampled_other_types_with_positive_flat_own": sum(t["flat_own"] > 0 for row in families for t in row["other_self_holding_types"]),
        "sampled_families_with_empty_generator": sum(any(int(r["hex"], 16) == 0 for r in row["R_i"]) for row in families),
        "sampled_families_with_empty_product_in_completed_lengths": sum(bool(row["fresh_length_set_orbit"]["empty_product_lengths"]) for row in families),
        "mismatches": len(all_mismatches),
    }
    output = {"status": "pass" if not all_mismatches else "fail", "summary": summary,
              "sampling": {"seed": SEED, "method": "Within each certified cell choose the least SHA256 key at each r, then fill by least remaining SHA256. Other cells use least SHA256. Purposive deterministic audit, no population estimate.", "strata": buckets},
              "controls": control_results, "families": families, "mismatches": all_mismatches,
              "independence": "Fresh assignment-enumerated greatest fixed point and fresh SAT R_i projection. Fresh nonrectangular-product DFS with set-composition lasso validation; separate full length-set orbit. Only dlang is imported from experiment source trees; producer code in FREE-TARGET and CENSUS-FORGET is never read/imported.",
              "evidence_class": "V2 same-task independent AI recomputation; not external replication or a growth proof",
              "input_sha256": READS, "seconds": round(time.monotonic() - started, 6),
              "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "python": os.sys.executable, "CODEX_THREAD_ID": os.environ.get("CODEX_THREAD_ID")}
    (HERE / "sample_audit.json").write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": output["status"], "summary": summary,
                      "seconds": output["seconds"], "peak_rss_kib": output["peak_rss_kib"]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
