"""Check whether the displayed three-place laws in counted chains keep every allowed word on the full stage."""
import argparse
from collections import Counter
from functools import cache
import gzip
from itertools import product
import json
from pathlib import Path
from time import perf_counter

from pysat.solvers import Solver
from growth import load_census, stage_rows
from local_witness import Assignments, CLAUSES, REFERENCE

HERE = Path(__file__).resolve().parent


def earlier_failure_law(supports, chain):
    knots = [set(supports[k]) for k in chain]
    first_shared, = knots[0] & knots[1]
    second_shared, = knots[1] & knots[2]
    third_shared, = knots[2] & knots[3]
    fifth, = knots[2] - {second_shared,third_shared}
    return (knots[0] - {first_shared}) | {fifth}


def chain_labels(supports, chain):
    knots = [set(supports[k]) for k in chain]
    joins = [next(iter(a&b)) for a,b in zip(knots,knots[1:])]
    numbered = sorted(knots[0]-{joins[0]})
    for i in range(1,7):
        numbered.append(joins[i-1])
        numbered.extend(knots[i]-{joins[i-1],joins[i]})
    numbered.append(joins[-1])
    numbered.extend(sorted(knots[-1]-{joins[-1]}))
    return {name:j for j,name in enumerate(numbered)}


@cache
def bare_with_extra(law):
    supports = [tuple(range(2*j,2*j+3)) for j in range(8)]+[law]
    system = Assignments(supports)
    readings = [system.agreement(g) for g in REFERENCE]
    return tuple(sum(1<<i for i,n in enumerate(system.counts([readings[j] for j in t])) if n)
                 for t in CLAUSES)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pilot", action="store_true")
    args = p.parse_args()
    start = perf_counter()
    totals = Counter()
    failures = []
    occurrence_counts = Counter()
    distinguishing_cases = Counter()
    sufficient = Counter()
    repeated, prefix = set(), set()
    with gzip.open(HERE/"step_incidence.jsonl.gz","rt") as handle:
        source = {rec["stage"]:rec["start"] for line in handle
                  if (rec:=json.loads(line))["arm"]=="one_fewer"}
    with gzip.open(HERE/"step_reading_rows.jsonl.gz","rt") as handle:
        lower_failures = {(rec["stage"],rec["chain_index"]):tuple(rec["lower"]) for rec in map(json.loads,handle)
                          if any(m!=127 for m in rec["lower"])}
    opportunities = {}
    census = load_census()
    for arm in ("one_fewer","arity_floor"):
        rounds = [Counter() for _ in range(7)]
        for i in range(0,len(census),100 if args.pilot else 1):
            for stage in stage_rows(census[i],arm):
                three = [k for k in stage.supports if len(k)==3]
                room = len(three)>=8 and len(set().union(*three))>=17
                counts = rounds[stage.round]
                counts["reached"] += 1
                counts["eight_three_place_laws"] += len(three)>=8
                counts["and_at_least_seventeen_distinctions_in_these_laws"] += room
                counts["and_actual_eight_knot_chain"] += bool(stage.chains)
                assert room or not stage.chains
        opportunities[arm] = rounds
    with gzip.open(HERE/"step_stages.jsonl.gz","rt") as stages:
        for line in stages:
            record = json.loads(line)
            # Use a systematic prefix of each hundred, preserving stage order.
            if args.pilot and record["id"]%100:
                continue
            supports = [tuple(x+1 for x in law) for law in record["supports"]]
            indexed = {frozenset(law) for law in record["supports"]}
            for j,chain in enumerate(record["chains"]):
                key = source[record["id"]],tuple(chain)
                repeated.add(key)
                if j<3:
                    prefix.add(key)
                earlier = earlier_failure_law(record["supports"],chain) in indexed
                failed_lower = (record["id"],j) in lower_failures
                if failed_lower:
                    numbered = chain_labels(record["supports"],chain)
                    internal = sorted(tuple(sorted(numbered[d] for d in support))
                                      for i,support in enumerate(record["supports"])
                                      if i not in chain and set(support)<=numbered.keys())
                    distinguishing_cases[str(internal)] += 1
                    matching = [s for s in internal if bare_with_extra(s) == lower_failures[record["id"],j]]
                    sufficient[str(matching)] += 1
                name = "present" if earlier else "absent"
                reading = "lower_fails" if failed_lower else "lower_passes"
                occurrence_counts[f"earlier_extra_law_{name}_{reading}"] += 1
            clauses = [list(sign*x for x in law) for law in supports for sign in (1,-1)]
            with Solver(bootstrap_with=clauses) as solver:
                totals["stages"] += 1
                used = set().union(*record["chains"])
                failed = set()
                for k in sorted(used):
                    members = supports[k]
                    assert len(members) == 3
                    missing = []
                    for word in product((0,1),repeat=3):
                        literals = [x if v else -x for x,v in zip(members,word)]
                        observed = solver.solve(assumptions=literals)
                        allowed = 0 < sum(word) < 3
                        if observed != allowed:
                            missing.append(word)
                    totals["distinct_chain_laws_by_stage"] += 1
                    if missing:
                        failures.append(dict(stage=record["id"],knot=k,lost_words=missing))
                        failed.add(k)
                totals["chain_occurrences"] += len(record["chains"])
                totals["chains_with_changed_source_law"] += sum(not failed.isdisjoint(c) for c in record["chains"])
    data = dict(unit="One copy of each distinct numbered chain-positive stage, shared by the two rival laws.",
                totals=totals, failures=failures, pilot=args.pilot, rounds_with_room=opportunities,
                once_per_start_and_chain=dict(all=len(repeated), first_three=len(prefix)),
                prior_extra_law_by_lower_result=occurrence_counts,
                lower_failures_by_all_extra_laws_entirely_on_the_chain=distinguishing_cases,
                lower_failures_by_single_extra_laws_sufficient_to_reproduce_the_defining_triples=sufficient,
                seconds=round(perf_counter()-start,3))
    (HERE/("source_pilot.json" if args.pilot else "source_projections.json")).write_text(json.dumps(data,indent=2)+"\n")
    print(totals, data["seconds"])

if __name__ == "__main__":
    main()
