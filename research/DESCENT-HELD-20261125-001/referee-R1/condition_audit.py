"""Recover the first disagreeing births and the retirement comparisons absent from the census rows."""
import argparse
from collections import Counter, defaultdict
from dataclasses import replace
import json
import resource
from time import perf_counter

import networkx as nx
from census_audit import ARTIFACTS, census, places, rows
from growth import Structure, complete_round
from return_audit import BASES, HERE, STARTS


def first_disagreement(stars, law, expected_round):
    state = Structure(stars)
    steps = [0] * len(stars)
    seen = mismatches = 0
    for t in range(1, expected_round + 1):
        turn = complete_round(state,law)
        for b in turn.births:
            previous = [steps[k] for k in b.parents]
            steps.append(1 + max(previous))
            if len({step % 3 for step in previous}) > 1:
                seen += 1
                amount = sum(d in state.barred for d in state.stars[b.knot]) if law.form == "BB" else len(state.stars[b.knot])
                parent_counts = [(sum(d in state.barred for d in state.stars[k]) if law.form == "BB"
                                  else len(state.stars[k])) % 3 for k in b.parents]
                mismatches += (t != expected_round or len(set(parent_counts)) == 1
                               or all((amount-k) % 3 == 1 for k in parent_counts))
    return Counter(runs=1, first_round_births=seen, disagreements=mismatches+int(not seen))


def retiring(stars, law, expected_right):
    state = Structure(stars)
    parents = [set() for _ in stars]
    barred_at_birth = [0] * len(stars)
    retired = set()
    tally = Counter(runs=1)
    any_wrong = False
    any_two = set()
    for turn_no in range(9):
        if turn_no:
            turn = complete_round(state,law)
            retired.update(turn.retired)
            for b in turn.births:
                parents.append(set(b.parents))
                barred_at_birth.append(b.barred_at_birth)
        current = [sum(d in state.barred for d in star) for star in state.stars]
        added = [b-z for b,z in zip(current,barred_at_birth,strict=True)]
        for holders in state.holders.values():
            if len(holders) != 2:
                continue
            a,b = holders
            for x,y in ((a,b),(b,a)):
                e = (added[y] - added[x]) % 3
                if y in parents[x]:
                    kind, predicted = "parent", e != 0
                elif x in parents[y]:
                    kind, predicted = "child", e == 1
                else:
                    assert x < len(stars) and y < len(stars)
                    kind, predicted = "start", e == 2
                wrong = ((current[x]-current[y]) % 3 == 1) != (kind == "parent")
                tally["shared_places_over_snapshots"] += 1
                tally["formula_mismatches"] += wrong != predicted
                tally["wrong_places_over_snapshots"] += wrong
                any_wrong |= wrong
                if {x,y} <= retired:
                    any_two.add(kind)
        if turn_no and (turn.status != "changed" or len(state.stars) > 3000):
            break
    tally["any_wrong"] = int(any_wrong)
    tally["whole_run_disagreements"] = int(any_wrong == expected_right)
    for kind in any_two:
        tally["both_holders_retired_at_"+kind+"_place"] = 1
    return tally


def evaluate(stars, law_name, form, knot_law, row, totals):
    law = replace(BASES[law_name], form=form, knot_law=knot_law)
    if form in ("PU","PB") and not row["a"]:
        # In three residues unequal holders necessarily yield a false parent on one side at round zero.
        totals["wrong_at_start"]["runs"] += 1
        totals["wrong_at_start"]["first_error_reported_after_round_zero"] += row["first_round_with_a_wrong_place"] > 0
    if row["a"] and row["c"] and row["d"] and not row["bprime"]:
        totals["mixed_first_births"].update(first_disagreement(stars,law,row["bprime_first_round"]))
    if form == "BB" and law.treatment == "CANCEL-RETIRE" and row["a"] and row["bprime"] and row["d"]:
        totals["retirement"].update(retiring(stars,law,row["right_on_every_structure"]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot",action="store_true")
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(1_500_000_000,1_500_000_000))
    t = perf_counter()
    atlas = nx.graph_atlas_g()
    starts = [s for size in range(1,6) for s in census(atlas,size)]
    counted = {part: defaultdict(Counter) for part in ("census","named")}
    for row in rows(ARTIFACTS/"part1_runs.json.gz","census_rows"):
        i = row["idx"]
        if args.pilot and i % 101 != 0:
            continue
        stars = places(starts[i],atlas)
        for key,data in row["armw"].items():
            law,form = key.split("|")
            evaluate(stars,law,form,"parity",data,counted["census"])
    for i,row in enumerate(rows(ARTIFACTS/"part4.json","runs")):
        if args.pilot and i % 5 != 0:
            continue
        for form,data in row["forms"].items():
            if form != "base":
                evaluate(STARTS[row["start"]],row["law"],form,row["knot_law"],data,counted["named"])
    if not args.pilot:
        (HERE/"condition_counts.json").write_text(json.dumps(counted,indent=2)+"\n")
    print("seconds", round(perf_counter()-t,2), json.dumps(counted))

if __name__ == "__main__":
    main()
