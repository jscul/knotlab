"""Independent FREE-TARGET-R1 relation/semigroup audit.

Only standard-library code is imported.  The producer's Python and the earlier
path/ray implementations are neither opened nor imported.  The usual-limit and
inlining semantics below are transcribed from the description language and the
REACH-CENSUS mathematical specification, rather than from method code.
"""
from __future__ import annotations

import gzip
import hashlib
import itertools
import json
import resource
import time
from collections import Counter, deque
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent / "relations_audit.json"
DATA = ROOT / "experiments/FREE-TARGET-20261114-001A/FREE-TARGET-20261114-001A-E001_free_target/codex"
SAMPLE = ROOT / "experiments/EVERY-RAY-20261113-001A/EVERY-RAY-20261113-001A-E001_min_over_paths/codex/sample"
CENSUS = ROOT / "artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/families.jsonl.gz"
READS: dict[str, str] = {}


def read(path: Path) -> bytes:
    # Deliberately explicit: no producer or earlier method source can enter.
    if path.suffix == ".py":
        raise ValueError("This audit reads no Python source")
    data = path.read_bytes()
    READS[str(path.relative_to(ROOT))] = hashlib.sha256(data).hexdigest()
    return data


def rows(path: Path):
    data = read(path)
    if path.suffix == ".gz":
        data = gzip.decompress(data)
    return [json.loads(line) for line in data.splitlines() if line.strip()]


def packed(values):
    return sum(int(v) << j for j, v in enumerate(values))


def argstate(assignment: int, arguments) -> int:
    return packed((assignment >> j) & 1 for j in arguments)


def self_types(defs):
    return [i for i, (_, _, calls) in enumerate(defs)
            if any(callee == "SELF" for callee, _ in calls)]


def usual(defs):
    result = []
    for arity, local, calls in defs:
        calls = [(callee, tuple(args)) for callee, args in calls]
        if any(callee == "SELF" and sorted(args) == [0, 1, 2]
               for callee, args in calls):
            calls.append(("K", (0, 1, 2)))
        result.append((arity, local, calls))
    return result


def evaluate(defs, previous):
    relations = []
    for i, (arity, local, calls) in enumerate(defs):
        mask = 0
        for assignment in range(1 << (arity + local)):
            valid = True
            for callee, args in calls:
                value = argstate(assignment, args)
                if callee == "K":
                    ok = value not in (0, 7)
                else:
                    relation = previous[i] if callee == "SELF" else relations[callee]
                    ok = bool((relation >> value) & 1)
                if not ok:
                    valid = False
                    break
            if valid:
                mask |= 1 << (assignment & ((1 << arity) - 1))
        relations.append(mask)
    return relations


def greatest_limit(defs):
    types = self_types(defs)
    previous = {i: 255 for i in types}
    history = []
    while True:
        relations = evaluate(defs, previous)
        current = {i: relations[i] for i in types}
        history.append([current[i] for i in types])
        assert all((current[i] & previous[i]) == current[i] for i in types)
        if current == previous:
            return relations, current, history
        previous = current


def flatten(defs, definition):
    """Expand non-self-holding calls; retain every self-holding call by type."""
    types = set(self_types(defs))
    arity = defs[definition][0]
    nextvar = arity
    calls = []
    owners = []

    def visit(i, actual):
        nonlocal nextvar
        k, local, body = defs[i]
        new = list(range(nextvar, nextvar + local))
        nextvar += local
        owners.extend((v, i) for v in new)
        env = list(actual) + new
        assert len(actual) == k
        for callee, args in body:
            mapped = tuple(env[a] for a in args)
            if callee == "K":
                calls.append(("K", mapped))
            elif callee == "SELF":
                calls.append((i, mapped))
            elif callee in types:
                calls.append((callee, mapped))
            else:
                visit(callee, mapped)

    visit(definition, tuple(range(arity)))
    return nextvar, calls, owners


def relation_for_call(size, calls, G, selected, drop=None, input_arity=3):
    allowed = 0
    args_out = calls[selected][1]
    for assignment in range(1 << size):
        ok = True
        for j, (callee, args) in enumerate(calls):
            if j == selected or j == drop:
                continue
            state = argstate(assignment, args)
            if (callee == "K" and state in (0, 7)) or (
                callee != "K" and not ((G[callee] >> state) & 1)
            ):
                ok = False
                break
        if ok:
            source = assignment & ((1 << input_arity) - 1)
            target = argstate(assignment, args_out)
            allowed |= 1 << (8 * source + target)
    return allowed


def pair_set(mask, q):
    return {(a, b) for a in range(q) for b in range(q)
            if (mask >> (a * q + b)) & 1}


@lru_cache(maxsize=200000)
def compose(left, right, q=8):
    result = 0
    rows_right = [(right >> (q * b)) & ((1 << q) - 1) for b in range(q)]
    for a in range(q):
        row = 0
        middle = (left >> (q * a)) & ((1 << q) - 1)
        for b in range(q):
            if (middle >> b) & 1:
                row |= rows_right[b]
        result |= row << (q * a)
    return result


def rectangular(mask, q=8):
    nonempty_rows = {(mask >> (q * a)) & ((1 << q) - 1)
                     for a in range(q)} - {0}
    return len(nonempty_rows) <= 1


def set_rectangular(mask, q):
    relation = pair_set(mask, q)
    domain = {a for a, _ in relation}
    image = {b for _, b in relation}
    return relation == set(itertools.product(domain, image))


def rectangular_between(mask, nrows, ncols):
    return len({(mask >> (a * ncols)) & ((1 << ncols) - 1)
                for a in range(nrows)} - {0}) <= 1


def compose_entry(entry, right, nrows):
    result = 0
    for source in range(nrows):
        out = 0
        row = (entry >> (8 * source)) & 255
        for middle in range(8):
            if (row >> middle) & 1:
                out |= (right >> (8 * middle)) & 255
        result |= out << (8 * source)
    return result


def audit_main_entries(msize, mcalls, main_arity, G, S, generators, r):
    entries = [j for j, (callee, _) in enumerate(mcalls) if callee == S]
    relations = [relation_for_call(msize, mcalls, G, j, input_arity=main_arity)
                 for j in entries]
    products = frozenset([identity(8)])
    levels = []
    # At length r+1 every S suffix contains r factors and is rectangular.
    for length in range(1, r + 2):
        joined = {compose_entry(entry, p, 1 << main_arity)
                  for entry in relations for p in products}
        rectangular_products = sum(rectangular_between(p, 1 << main_arity, 8)
                                   for p in joined)
        levels.append({"total_length_from_main": length,
                       "suffix_length_in_S": length - 1,
                       "S_suffix_products": len(products),
                       "entry_products": len(joined),
                       "rectangular_products": rectangular_products,
                       "all_rectangular": rectangular_products == len(joined)})
        products = frozenset(compose(p, g) for p in products for g in generators)
    return {"entry_count": len(entries),
            "relations": [{"flat_call_index": j, "arguments": list(mcalls[j][1]), "hex": hex(p)}
                          for j, p in zip(entries, relations)],
            "levels": levels,
            "all_first_r_products_rectangular": levels[r - 1]["all_rectangular"],
            "least_initial_rectangular_length": next(z["total_length_from_main"] for z in levels if z["all_rectangular"])}


def identity(q):
    return sum(1 << (q * a + a) for a in range(q))


def recurrent_word(generators, q):
    """Find a cycle in the prefix-nonrectangular product automaton."""
    active = {}
    closed = set()
    stack_states = []
    stack_labels = []

    def visit(state):
        active[state] = len(stack_states)
        stack_states.append(state)
        for label, generator in enumerate(generators):
            target = compose(state, generator, q)
            if rectangular(target, q):
                continue
            if target in active:
                at = active[target]
                return {"prefix": stack_labels[:at],
                        "cycle": stack_labels[at:] + [label]}
            if target not in closed:
                stack_labels.append(label)
                result = visit(target)
                if result is not None:
                    return result
                stack_labels.pop()
        stack_states.pop()
        del active[state]
        closed.add(state)
        return None

    result = visit(identity(q))
    assert result is not None
    assert check_word(generators, result, q)["valid"]
    return result


def check_word(generators, word, q=8):
    if not word or not word.get("cycle"):
        return {"valid": False, "reason": "no nonempty cycle"}
    labels = word["prefix"] + word["cycle"]
    if not all(isinstance(i, int) and 0 <= i < len(generators) for i in labels):
        return {"valid": False, "reason": "invalid call label"}
    state = identity(q)
    valid = True
    prefix_products = []
    for label in word["prefix"]:
        state = compose(state, generators[label], q)
        prefix_products.append(hex(state))
        valid &= not rectangular(state, q)
    at_cycle = state
    cycle_products = []
    for label in word["cycle"]:
        state = compose(state, generators[label], q)
        cycle_products.append(hex(state))
        valid &= not rectangular(state, q)
    valid &= state == at_cycle
    if "prefix_product" in word:
        valid &= at_cycle == int(word["prefix_product"], 16)
    metadata_convention = None
    if "cycle_products" in word:
        stored = [hex(int(x, 16)) for x in word["cycle_products"]]
        before_steps = [hex(at_cycle)] + cycle_products[:-1]
        if stored == before_steps:
            metadata_convention = "products before each cycle step"
        elif stored == cycle_products:
            metadata_convention = "products after each cycle step"
        else:
            valid = False
            metadata_convention = "neither before-step nor after-step products"
    return {"valid": bool(valid), "prefix_products": prefix_products,
            "at_cycle": hex(at_cycle), "cycle_products": cycle_products,
            "recorded_cycle_products_convention": metadata_convention,
            "returns_to_same_product": state == at_cycle}


def decide(generators, q=8):
    current = frozenset(generators)
    seen = {}
    levels = []
    r = None
    while current not in seen:
        length = len(levels) + 1
        seen[current] = length
        all_rect = all(rectangular(p, q) for p in current)
        if all_rect and r is None:
            r = length
        levels.append(current)
        current = frozenset(compose(p, g, q) for p in current for g in generators)
        # Resource gate, never interpreted as a mathematical verdict.
        if len(levels) > 10000 or sum(map(len, levels)) > 200000:
            raise RuntimeError("independent audit semigroup resource gate")
    repeat_start = seen[current]
    period = len(levels) + 1 - repeat_start
    all_rect = [all(rectangular(p, q) for p in level) for level in levels]
    if r is not None:
        assert all(all_rect[r - 1:])
        assert all(all_rect[repeat_start - 1:])
    word = recurrent_word(generators, q) if r is None else None
    return {"r": r, "repeat_start": repeat_start, "period": period,
            "length_set_sizes": [len(x) for x in levels],
            "all_rectangular_by_length": all_rect,
            "P_r": sorted(hex(x) for x in levels[r - 1]) if r else None,
            "recurrent_word": word,
            "reachable_level_product_entries": sum(map(len, levels))}


def controls():
    comparisons = 0
    factor_tests = 0
    for left in range(16):
        assert rectangular(left, 2) == set_rectangular(left, 2)
        for right in range(16):
            a, b = pair_set(left, 2), pair_set(right, 2)
            derived = {(x, z) for x, y in a for yy, z in b if y == yy}
            assert pair_set(compose(left, right, 2), 2) == derived
            if rectangular(left, 2) or rectangular(right, 2):
                assert rectangular(compose(left, right, 2), 2)
                factor_tests += 1
            comparisons += 1
    named = []
    fixtures = [
        ("full", [15], 2, 1),
        ("proper_product", [2], 2, 1),
        ("empty_product", [0], 2, 1),
        ("identity_recurrence", [9], 2, None),
        ("swap_recurrence", [6], 2, None),
        ("one_nonforgetting_choice", [15, 9], 2, None),
        ("first_rectangular_at_two", [2 | 32 | 256], 3, 2),
    ]
    for name, generators, q, expected in fixtures:
        result = decide(generators, q)
        assert result["r"] == expected
        named.append({"name": name, "generators": list(map(hex, generators)),
                      "q": q, "expected_r": expected, "derived": result})
    # A false claim that identity is rectangular, and a false lasso, reject.
    assert not rectangular(identity(8))
    malformed = check_word([15], {"prefix": [], "cycle": [0]}, 2)
    assert not malformed["valid"]
    # Boundary control: a wrapper adds a nonforgetting entry step.  S(a,b,c)
    # introduces u,v,h,t, imposes NAE(a,u,h) and t=a, and calls S(b,u,v).
    # Its port relation is out[0]=in[1], with least rectangular power two.
    # With C1 the wrapper entry, {main.b, h_2, t_4} is precisely NAE: a_2=b,
    # a_4=u_2=t_4.  All other helpers can be chosen independently to extend.
    shift = 0
    for assignment in range(1 << 7):
        a, b, c, u, v, h, t = [(assignment >> j) & 1 for j in range(7)]
        if len({a, u, h}) > 1 and a == t:
            shift |= 1 << (8 * packed((a, b, c)) + packed((b, u, v)))
    shift_decision = decide([shift])
    assert shift_decision["r"] == 2
    assert not rectangular(compose(identity(8), shift))
    # Equality is supplied using only the declared NAE language, with a
    # finite nonrecursive macro.  Six triples of the classical Fano pattern,
    # with its terminal triple removed, force the three terminals equal.
    equality_macro = (3, 4, [("K", a) for a in (
        (0, 3, 4), (0, 5, 6), (1, 3, 5),
        (1, 4, 6), (2, 3, 6), (2, 4, 5))])
    assert evaluate([equality_macro], {}) == [129]
    boundary_defs = [equality_macro,
                     (3, 5, [("K", (0, 3, 5)), (0, (0, 6, 7)),
                             ("SELF", (1, 3, 4))]),
                     (3, 0, [(1, (0, 1, 2))])]
    _, boundary_G, _ = greatest_limit(boundary_defs)
    boundary_size, boundary_calls, _ = flatten(boundary_defs, 1)
    continuation = next(i for i, (c, _) in enumerate(boundary_calls) if c == 1)
    presented_shift = relation_for_call(boundary_size, boundary_calls, boundary_G, continuation)
    assert boundary_G == {1: 255}
    assert presented_shift == shift
    bond_states = [s for s in range(8) if s not in (0, 7)]
    deletions_full = []
    for drop in range(3):
        keep = [j for j in range(3) if j != drop]
        deletions_full.append(len({argstate(s, keep) for s in bond_states}) == 4)
    assert all(deletions_full)
    wrapper_control = {"S_rule": "NAE(a,u,h), t=a; SELF(b,u,v)",
                       "main_rule": "main(a,b,c) calls S(a,b,c)",
                       "R": hex(shift), "least_r": shift_decision["r"],
                       "depth_convention": "C0=main, C1=entry S",
                       "s": 4, "bond": ["main.b", "C2.h", "C4.t"],
                       "allowed_bond_states": bond_states,
                       "all_one_forgotten_projections_full": deletions_full,
                       "bond_size": 3,
                       "NAE_description": boundary_defs,
                       "NAE_equality_macro_port_relation": hex(129),
                       "NAE_flat_S_size": boundary_size,
                       "NAE_limit_G_S": hex(boundary_G[1]),
                       "unshifted_bound": 2 + 4 // 2,
                       "shifted_bound": 2 + (4 - 1) // 2,
                       "unshifted_uniform_wrapper_claim_rejected": 3 < 2 + 4 // 2,
                       "scope": "general gap arithmetic control, not a member of the frozen 66; the NAE description obeys the original raw language caps"}
    return {"passed": True, "all_two_state_products_checked": comparisons,
            "rectangular_factor_products_checked": factor_tests,
            "false_identity_rectangular_claim_rejected": True,
            "false_recurrence_claim_rejected": True, "named": named,
            "wrapper_boundary_counterexample": wrapper_control}


def main():
    started = time.monotonic()
    raw_G = rows(SAMPLE / "G.jsonl")
    phase2 = rows(SAMPLE / "phase2.jsonl")
    population = {r["key"]: r for r in raw_G}
    # The replacement is restricted to G keys: phase2 may contain other strata.
    for row in phase2:
        if row["key"] in population:
            population[row["key"]] = row
    population = {key: row for key, row in population.items()
                  if row.get("class_path") == "grows"}
    assert len(population) == 66
    frozen = json.loads(read(DATA / "population.json"))
    assert set(population) == set(frozen["keys"])
    recorded_gate = {r["key"]: r for r in rows(DATA / "gate_relations.jsonl")}
    recorded_full = {r["case"]: r["result"] for r in rows(DATA / "full/results.jsonl")}
    read(CENSUS)
    census = {}
    with gzip.open(CENSUS, "rt") as handle:
        for line in handle:
            row = json.loads(line)
            if row.get("key") in population:
                census[row["key"]] = row
    assert len(census) == len(population)
    control_result = controls()
    results = []
    mismatches = []
    mutants = []
    for index, key in enumerate(sorted(population)):
        raw = json.loads(key)
        defs = usual(raw)
        types = self_types(defs)
        relations, G, iterations = greatest_limit(defs)
        main_id = len(defs) - 1
        msize, mcalls, mowners = flatten(defs, main_id)
        S = main_id if main_id in types else next(c for c, _ in mcalls if c != "K")
        ssize, scalls, sowners = flatten(defs, S)
        selected = [j for j, (callee, _) in enumerate(scalls) if callee == S]
        matrices = [relation_for_call(ssize, scalls, G, j) for j in selected]
        decision = decide(matrices)
        recorded = recorded_full[key]
        gate = recorded_gate[key]
        own_mismatches = []

        def compare(field, actual, expected):
            if actual != expected:
                own_mismatches.append({"field": field, "fresh": actual, "recorded": expected})

        compare("S vs census", S, census[key]["S"])
        compare("n_defs", len(defs), recorded["preparation"]["n_defs"])
        compare("main_block_size", msize, recorded["preparation"]["main_block_size"])
        compare("s_block_size", ssize, recorded["preparation"]["s_block_size"])
        compare("c vs population", len(selected), population[key]["c"])
        compare("c vs full", len(selected), recorded["c"])
        compare("limit alive", bool(relations[-1]), recorded["preparation"]["usual_limit_alive"])
        compare("R_i full", matrices, [int(x["hex"], 16) for x in recorded["R_i"]])
        compare("R_i gate", matrices, [int(x["hex"], 16) for x in gate["R_i"]])
        compare("R_i flat call indices", selected, [x["flat_call_index"] for x in recorded["R_i"]])
        compare("R_i arguments", [list(scalls[j][1]) for j in selected],
                [x["arguments"] for x in recorded["R_i"]])
        for name in ("r", "repeat_start", "period", "length_set_sizes", "all_rectangular_by_length"):
            compare("semigroup." + name, decision[name], recorded["semigroup"][name])
            compare("gate.semigroup." + name, decision[name], gate["semigroup"][name])
        if decision["r"] is not None:
            compare("P_r", set(decision["P_r"]), {hex(int(x, 16)) for x in recorded["semigroup"]["P_r"]})
            compare("verdict", "grows", recorded["verdict"])
            # Set-based rectangularity rechecks the exact certifying products.
            assert all(set_rectangular(int(x, 16), 8) for x in decision["P_r"])
            reported_word_check = None
        else:
            reported_word_check = check_word(matrices, recorded["recurring_word"])
            compare("recorded recurring word valid", reported_word_check["valid"], True)
            compare("gate recurring word valid", check_word(matrices, gate["semigroup"]["recurring_word"])["valid"], True)
            assert check_word(matrices, decision["recurrent_word"])["valid"]
        compare("r top level", decision["r"], recorded["r"])
        entry_types = Counter(c for c, _ in mcalls if c != "K")
        body_types = Counter(c for c, _ in scalls if c != "K")
        other_types = []
        for i in types:
            if i == S:
                continue
            n, calls, owners = flatten(defs, i)
            other_types.append({"definition": i, "arity": defs[i][0],
                                "raw_own": defs[i][1], "flat_own": n - defs[i][0],
                                "G": hex(G[i]), "flat_calls": [[c, list(a)] for c, a in calls]})
        record = {"population_index_sorted": index, "key": key,
                  "n_defs": len(defs), "S": S, "main": main_id,
                  "main_equals_S": main_id == S, "c": len(selected),
                  "main_size": msize, "S_size": ssize,
                  "G": {str(k): hex(v) for k, v in G.items()},
                  "fixed_point_history": iterations,
                  "main_entries_by_type": dict(entry_types),
                  "S_calls_by_type": dict(body_types),
                  "other_self_holding_definitions": other_types,
                  "R_i": [{"call_index": i, "flat_call_index": j,
                           "arguments": list(scalls[j][1]), "hex": hex(matrices[i])}
                          for i, j in enumerate(selected)],
                  "semigroup": decision, "reported_word_check": reported_word_check,
                  "reported_verdict": recorded["verdict"],
                  "lambda_path": population[key]["lambda_path"],
                  "mismatches": own_mismatches}
        if main_id != S and decision["r"] is not None:
            record["main_entry_prefix_audit"] = audit_main_entries(
                msize, mcalls, defs[main_id][0], G, S, matrices, decision["r"])
        results.append(record)
        mismatches.extend({"key": key, **item} for item in own_mismatches)
        # Fresh sensitivity panel: every side SELF can be erased, not merely a
        # chosen first call whose exact G may already be TOP.
        for side in selected:
            mutated = [relation_for_call(ssize, scalls, G, j, drop=side) for j in selected]
            changed = [i for i, (a, b) in enumerate(zip(matrices, mutated)) if a != b]
            if changed:
                mutants.append({"key": key, "dropped_flat_call": side,
                                "changed_call_indices": changed,
                                "before": list(map(hex, matrices)),
                                "after": list(map(hex, mutated)),
                                "before_r": decision["r"],
                                "after_r": decide(mutated)["r"]})
    growers = [r for r in results if r["semigroup"]["r"] is not None]
    summary = {"population": len(results), "calls": sum(r["c"] for r in results),
               "finite_r": len(growers), "recurrent_nonrectangular": len(results) - len(growers),
               "r_counts": dict(Counter(r["semigroup"]["r"] for r in growers)),
               "several_definitions": sum(r["n_defs"] > 1 for r in results),
               "growers_several_definitions": sum(r["n_defs"] > 1 for r in growers),
               "main_not_S": sum(not r["main_equals_S"] for r in results),
               "growers_main_not_S": sum(not r["main_equals_S"] for r in growers),
               "wrapper_growers_first_r_products_rectangular": sum(
                   r.get("main_entry_prefix_audit", {}).get("all_first_r_products_rectangular", False)
                   for r in growers if not r["main_equals_S"]),
               "families_with_other_self_holding_definitions": sum(bool(r["other_self_holding_definitions"]) for r in results),
               "growers_with_other_self_holding_definitions": sum(bool(r["other_self_holding_definitions"]) for r in growers),
               "all_other_self_types_have_zero_flat_own": all(
                   t["flat_own"] == 0 for r in results for t in r["other_self_holding_definitions"]),
               "relation_or_semigroup_mismatches": len(mismatches),
               "mutant_changed_families": len({r["key"] for r in mutants})}
    output = {"status": "pass" if not mismatches else "fail", "summary": summary,
              "independence": "Independent standard-library reimplementation; no producer Python, paths_dp.py, or reach_dp.py opened/imported",
              "validation": "V2 same-task independently authored AI lane, not external replication",
              "controls": control_result, "mismatches": mismatches,
              "mutant_changes": mutants, "families": results, "input_sha256": READS,
              "seconds": round(time.monotonic() - started, 6),
              "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    OUT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": output["status"], "summary": summary,
                      "seconds": output["seconds"], "peak_rss_kib": output["peak_rss_kib"]}, indent=2))


if __name__ == "__main__":
    main()
