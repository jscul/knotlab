#!/usr/bin/env python3
"""Rebuild every certificate, replay its actual expansion, and test invalid guards."""
import copy
import json
from collections import Counter
from itertools import combinations
from pathlib import Path

import balanced_guards
import fact_library
import seven_guard_stress
import solver
import terminal_library


def programs():
    return {"six_terminal_dag":solver.six_terminal_certificate(),
            "direct_same_queries":solver.six_terminal_certificate(route=False),
            "direct_even_input_tree":solver.literal_certificate(False),
            "literal_live_lemma":solver.unequal_live_certificate(),
            "literal_specialized_rival":solver.unequal_live_certificate(True),
            "source_three_global":solver.source_certificate("global"),
            "source_two_global":solver.source_certificate("two_groups"),
            "source_prefix_local":solver.source_certificate("prefix"),
            "source_whole_totals":solver.source_certificate("direct"),
            "translation_control":solver.translated_certificate()}


def capacity():
    # Enumerate RREF parity systems of codimension three in the seven scalar coordinates (x,s).
    honest = [x | ((x & (x>>1) & 31).bit_count()%2 << 6) for x in range(64)]
    histogram = Counter()
    columns = [sum(solver.parity(x & mask) << i for i,x in enumerate(honest)) for mask in range(128)]
    all_honest = (1 << 64)-1
    subspaces = 0
    for pivot in combinations(range(7),3):
        slots = [(i,c) for i,start in enumerate(pivot) for c in range(start+1,7) if c not in pivot]
        for code in range(1 << len(slots)):
            rows = [1 << p for p in pivot]
            for j in solver.indices(code):
                i,c=slots[j]
                rows[i] ^= 1 << c
            cells = [all_honest]
            for row in rows:
                pos = columns[row]
                cells = [z for cell in cells for z in (cell & pos,cell & ~pos)]
            histogram.update(z.bit_count() for z in cells)
            subspaces += 1
    solver.ensure(subspaces==11811 and sum(histogram.values())==94488 and max(histogram)==12,
                  "scalar honest-mass capacity")
    return {"linear_spaces":subspaces,"affine_cosets":sum(histogram.values()),
            "honest_input_size_histogram":{str(s):v for s,v in sorted(histogram.items())}}


def conservative_rejections(proofs):
    rejected = {}
    def fail(label,p,message,charge=None):
        try:
            solver.verify(p,charge=charge)
        except ValueError as e:
            solver.ensure(message in str(e),f"unexpected failure in {label}: {e}")
            rejected[label]=str(e)
        else:
            raise ValueError(f"invalid proof admitted: {label}")

    bad = copy.deepcopy(proofs["six_terminal_dag"])
    bad["nodes"][0]["guard"] = bad["nodes"][2]["guard"]
    fail("wrong_guard_at_first_route",bad,"does not establish")
    bad = copy.deepcopy(proofs["source_three_global"])
    bad["nodes"][0]["guard"] = []
    fail("erase_guard_of_rich_u_zero",bad,"fails on guarded evaluator")
    honest = solver.evaluator_sets((1,6),0)["left"]
    violation = honest & ~solver.equation_points(solver.U,0)
    solver.ensure(195 in set(solver.indices(violation)),"raw matched counterexample to unguarded u=0")
    bad = copy.deepcopy(proofs["literal_live_lemma"])
    use = next(node for node in bad["nodes"] if node["rule"]=="use")
    use["guard"] = [row for row in use["guard"] if row[0]!=solver.V]
    fail("omit_discharged_lemma_guard",bad,"guard not entailed")
    bad = copy.deepcopy(proofs["literal_live_lemma"])
    next(node for node in bad["nodes"] if node["rule"]=="discharge")["claim"]=(1,1)
    fail("reverse_discharged_literal",bad,"does not refute the opposite")
    bad = copy.deepcopy(proofs["six_terminal_dag"])
    bad["nodes"][-1]["query"] = 512
    fail("ask_for_an_extra_coordinate",bad,"only the nine")
    bad = copy.deepcopy(proofs["six_terminal_dag"])
    bad["nodes"][1]["parents"]=[1]
    fail("circular_citation",bad,"cyclic or forward")
    bad = copy.deepcopy(proofs["six_terminal_dag"])
    bad["nodes"][5]["parents"] = [3]
    fail("indirect_guard_called_directly_terminal", bad, "directly checked terminal proof")
    fail("matched_charge_cannot_be_refuted",proofs["six_terminal_dag"],"remains live",0)
    bad=copy.deepcopy(proofs["translation_control"])
    bad["translations"]=False
    fail("transport_in_literal_model",bad,"disabled")
    return {"rejected":rejected,"honest_point_refuting_unguarded_u_zero":195,
            "matched_charge_full_solutions":(honest & solver.evaluator_sets((1,6),0)["right"]).bit_count()}


def direct_leaf_orders(proof):
    sides = solver.evaluator_sets(tuple(proof["masks"]), proof["charge"])
    per_leaf = []
    for node in proof["nodes"]:
        if node["rule"] != "terminal":
            continue
        cell = solver.guard_points(node["guard"])
        costs = []
        for first in ("left", "right"):
            final, calls, _ = solver.sequential(cell, sides, first)
            solver.ensure(final == 0, "an unguarded leaf survived")
            costs.append(calls)
        per_leaf.append(costs)
    solver.ensure(per_leaf == [[3, 4], [3, 4], [2, 3], [3, 4]] * 2,
                  "sequential orders at the unchanged raw leaves")
    return {"rich_first_then_plain_first_by_leaf": per_leaf,
            "sum_with_best_order_per_leaf": sum(min(costs) for costs in per_leaf)}


def main():
    home=Path(__file__).resolve().parent
    cert=json.loads(json.dumps(programs()))
    source=home/"certificates.json"
    solver.ensure(json.loads(source.read_text())==cert,"the saved proofs differ from their reproducible construction")
    reports={}
    for label,p in cert.items():
        actual=solver.verify(p)
        expanded=solver.verify(solver.unfold(p))
        solver.ensure(actual["unfolded_nodes"] == expanded["nodes"] and
                      actual["unfolded_parent_references"]==expanded["parent_references"] and
                      actual["unfolded_rules"]==expanded["rules"],"real expansion and node count disagree")
        detail={k:actual[k] for k in ("nodes","rules","parent_references","source_checks","source_support_visits",
                                      "xor_additions","rich_route_support_visits","sequential_calls_then_support_visits")}
        detail["expansion"]={k:expanded[k] for k in ("nodes","rules","parent_references","source_support_visits",
                                                       "rich_route_support_visits","sequential_calls_then_support_visits")}
        if actual["literal_lemma_uses"]:
            detail["literal_lemma_uses"]=actual["literal_lemma_uses"]
        if actual["rich_routes"]:
            detail["rich_routes"]=actual["rich_routes"]
        if label == "direct_same_queries":
            detail["leaf_orders"] = direct_leaf_orders(p)
        reports[label]=detail

    six=reports["six_terminal_dag"]
    solver.ensure(six["rules"]["terminal"]==6 and six["expansion"]["rules"]["terminal"]==8 and
                  six["sequential_calls_then_support_visits"]["right"]==[12,96],"primary certificate accounting")
    fixed=reports["literal_live_lemma"]["literal_lemma_uses"]
    solver.ensure([v["live_points_before"] for v in fixed]==[128,64] and
                  [v["saturated_live_points_after"] for v in fixed]==[32,16],"two genuinely live consumers")
    control=solver.literal_certificate()
    solver.ensure(solver.verify(control)["unfolded_rules"]["terminal"]==10,"shorter same-guard live control")
    result={"status":"passed","five_product_proofs":reports,"scalar_capacity":capacity(),
            "guarded_terminal_replay":terminal_library.replay(),"balanced_whole_case_control":balanced_guards.replay(),
            "direct_source_fact_library":fact_library.search(),"seven_product_stress":seven_guard_stress.replay(),
            "semantic_negative_controls":conservative_rejections(cert)}
    saved=home/"checks.json"
    if saved.exists():
        solver.ensure(json.loads(saved.read_text())==result,"saved numerical result mismatch")
    print(json.dumps(result,sort_keys=True,indent=2))


if __name__=="__main__":
    main()
