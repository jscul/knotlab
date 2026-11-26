"""Check returns and selected boundary cases using the independent complete round."""

import argparse
from collections import Counter
from dataclasses import replace
from math import gcd
import json
from pathlib import Path
import resource
from time import perf_counter

import networkx as nx
from growth import Law, Structure, complete_round

HERE = Path(__file__).resolve().parent
TICKET = HERE.parents[1] / (HERE.parent.name + "A")
LAWS = json.loads((TICKET / "laws.json").read_text())
BASES = {row["name"]: Law.from_record(row) for row in LAWS["recorded"] + LAWS["holding"]}
STARTS = {name: row["stars"] for name, row in json.loads((TICKET / "starts.json").read_text())["starts"].items()}


def ring(n, loose):
    return [[(k-1) % n, k, *range(n+k*loose,n+(k+1)*loose)] for k in range(n)]


def roster(state):
    usable = state.usable()
    members = set(usable)
    past = not any(state.meetings[k] & members for k in members)
    met = {frozenset(group) for others in state.meetings if len(group := others & members) >= 2}
    ordered = sorted(met, key=len, reverse=True)
    groups = []
    for group in ordered:
        if not any(group <= larger for larger in groups):
            groups.append(group)
    graph = nx.Graph()
    for k, places in usable.items():
        graph.add_node(k, mark=(len(places), sum(d in state.barred for d in state.stars[k])))
    for i, group in enumerate(groups, 1):
        graph.add_node(-i, mark=(-1, len(group)))
        graph.add_edges_from((-i,k) for k in group)
    parts = []
    for part in nx.connected_components(graph):
        sub = graph.subgraph(part).copy()
        signature = tuple(sorted((sub.nodes[k]["mark"], sub.degree(k)) for k in sub))
        parts.append((part & members, signature, sub))
    return past, sorted(parts, key=lambda part: min(part[0]))


def history(stars, law, rounds, bound):
    state = Structure(stars)
    parents = [()] * len(stars)
    steps = [0] * len(stars)
    rosters = []
    for _ in range(rounds):
        r = complete_round(state, law)
        if r.status != "changed":
            break
        for birth in r.births:
            parents.append(birth.parents)
            steps.append(1 + max(steps[k] for k in birth.parents))
        rosters.append(roster(state))
        if len(state.stars) > bound:
            break
    return rosters, parents, steps


def first_return(data):
    rosters, parents, steps = data
    for s, (past, initial) in enumerate(rosters, 1):
        if not past:
            continue
        choices = []
        for members, signature, graph in initial:
            descendants = set(members)
            for k in range(min(members) + 1, len(parents)):
                if any(p in descendants for p in parents[k]):
                    descendants.add(k)
            for t, (_, later) in enumerate(rosters[s:], s + 1):
                for other, sig, sub in later:
                    if signature != sig or not other <= descendants:
                        continue
                    matcher = nx.isomorphism.GraphMatcher(graph, sub, node_match=lambda a,b: a["mark"] == b["mark"])
                    assignment = next(matcher.isomorphisms_iter(), None)
                    if assignment is None:
                        continue
                    shifts = sorted({steps[assignment[k]] - steps[k] for k in members})
                    choices.append(dict(s=s,t=t,period=t-s,members=sorted(members),returned=sorted(other),
                                        start_steps=sorted({steps[k] for k in members}),shifts=shifts))
                if choices and min(row["t"] for row in choices) <= t:
                    break
        if choices:
            return min(choices, key=lambda row: row["t"])
    return None


def period_check(stars, law, rounds, bound):
    base = first_return(history(stars, law, rounds, bound))
    if not base or len(base["shifts"]) != 1 or len({p % 3 for p in base["start_steps"]}) != 1:
        return None
    expected = base["period"] * 3 // gcd(3, base["shifts"][0])
    readings = {form: first_return(history(stars, replace(law, form=form), rounds, bound)) for form in ("PB","BB")}
    return {"base":base, "predicted":expected, "marked": readings}


def small_examples():
    cases = [
        ("retire together",ring(5,1),"F1R",["BB"],2),
        ("added distinctions span demand",[list(range(5))],"C3WF",["PU","PB"],2),
        ("closing after added distinctions",[[0,1,2]],"C3WF",[None,"PB","BB"],4),
    ]
    out = {}
    for name,stars,law,forms,rounds in cases:
        group = {"stars":stars,"law":law,"forms":{}}
        for form in forms:
            state = Structure(stars)
            records = []
            for _ in range(rounds):
                r = complete_round(state, replace(BASES[law],form=form))
                records.append({"births":len(r.births),"retired":sorted(r.retired),"closing":r.closing,
                                "status":r.status,"barred":len(state.barred),"usable":sum(map(len,state.usable().values())),
                                "birth_stats":sorted([*weights,multiplicity] for weights,multiplicity in
                                  Counter((len(b.parents),b.demand,b.base_fresh,b.added,b.barred_at_birth) for b in r.births).items())})
                if r.status != "changed":
                    break
            group["forms"][form or "base"] = records
        out[name] = group
    return out


def unequal_parents_example():
    stars = [[0,1,2],[0,3,5],[1,3,4,6],[2,4,7,8]]
    state = Structure(stars)
    depth = [0] * len(stars)
    for t in range(1, 4):
        turn = complete_round(state, replace(BASES["R3W"], form="BB"))
        for b in turn.births:
            parents = [depth[p] for p in b.parents]
            depth.append(max(parents) + 1)
            if len(set(parents)) > 1:
                return {"stars":stars,"round":t,"child":b.knot,"parent_steps":parents,
                        "written_barred_residue":b.barred_at_birth % 3,"stamp":depth[-1] % 3}
    raise ValueError("No mixed-parent birth")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(1_500_000_000,1_500_000_000))
    start = perf_counter()
    # Registered ring comparisons stop at the first returns; all run to at least round seven.
    rings = [(size, law) for size in (5,7) for law in ("C3W","C3WF")]
    output = {"registered_rings":{}, "examples":small_examples(), "unequal_parents":unequal_parents_example()}
    for n, law in rings[:1] if args.pilot else rings:
        output["registered_rings"][f"{n} knots, {law}"] = period_check(ring(n,3),BASES[law],7,1000)
    # Fixed order; stop at the first observed return with a different positive period.
    found = None
    trials = 0
    for name,stars in STARTS.items():
        for law in BASES:
            trials += 1
            result = period_check(stars,BASES[law],8,200)
            if result and any(r and r["period"] != result["predicted"] for r in result["marked"].values()):
                found = {"name":name,"stars":stars,"law":law,**result}
                break
        if found or args.pilot:
            break
    output.update(search_cases=trials, differing_return=found)
    if not args.pilot:
        (HERE / "return_counts.json").write_text(json.dumps(output,indent=2)+"\n")
    print("seconds",round(perf_counter()-start,2),"cases",trials,"differing_return",found)

if __name__ == "__main__":
    main()
