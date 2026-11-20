"""First-layer route formula, exact long-route saturation and an old-loose control."""
from collections import Counter, defaultdict, deque
from itertools import combinations
import json
from pathlib import Path

from sources import cases, generate, loads, growth

DATA = Path(__file__).resolve().parents[3] / "artifacts" / Path(__file__).resolve().parent.parent.name / Path(__file__).resolve().parent.name


def physical_incidence(stars):
    adjacent = defaultdict(list)
    for k, support in enumerate(stars):
        for distinction in support:
            knot = ("k", k)
            bit = ("d", distinction)
            adjacent[knot].append(bit)
            adjacent[bit].append(knot)
    return adjacent


def route_row(adjacent, origin):
    distance, ways = {origin: 0}, Counter({origin: 1})
    queue = deque([origin])
    while queue:
        v = queue.popleft()
        for nxt in adjacent[v]:
            if nxt not in distance:
                distance[nxt] = distance[v] + 1
                queue.append(nxt)
            if distance[nxt] == distance[v] + 1:
                ways[nxt] += ways[v]
    return distance, ways


def first_routes(i,j,hot):
    """Tile the old interval by ordinary steps and two-step routes through one newborn."""
    left, right = i+1,j
    count = {left: 1}
    for v in range(left+1, right+1):
        count[v] = count[v-1]
        if v >= left+2 and v not in hot and v-2 not in hot:
            count[v] += count[v-2]
    return count[right]


def compare(spec,occupied,marks):
    frames=list(generate(spec,occupied,max_age=1))
    old, grown = [frame for _,frame in frames]
    hot = {k for k,row in enumerate(old["stars"]) if not occupied.isdisjoint(row)}
    neighbors=physical_incidence(grown["stars"])
    answer={}
    for i in range(len(marks)):
        distance, ways=route_row(neighbors,("d",marks[i]))
        for j in range(i+1,len(marks)):
            predicted=first_routes(i,j,hot)
            assert distance[("d",marks[j])] == 2*(j-i)
            assert ways[("d",marks[j])] == predicted
            answer[f"{i},{j}"]=predicted
    return answer


def loose_control():
    # Two nonadjacent source holders on a bare five-ring have one two-step contact.
    base=growth.predecessor()
    p=Path(__file__).resolve().parents[3] / "experiments/EDDY-WORLD-20261119-001/EDDY-WORLD-20261119-001-E001_world/inputs.json"
    spec=next(x for x in json.loads(p.read_text())["cases"] if x["id"]=="R0")
    stars=base.source_stars(spec)
    old=growth.plan_round(stars).stage
    pairs=[(a,b) for a in old.loose[0] for b in old.loose[2]]
    result={}
    for tag,rows in (("source",stars),("quiet",growth.step(stars,(),("P","V"))["stars"]),
                     ("loaded",growth.step(stars,spec["roles"]["ring_edges"][0],("P","V"))["stars"])):
        graph=physical_incidence(rows)
        result[tag] = [[a,b,route_row(graph,("d",a))[0][("d",b)]//2] for a,b in pairs]
    assert sorted(x[2] for x in result["source"])==[3]*4
    assert sorted(x[2] for x in result["loaded"])==[3]*4
    assert min(x[2] for x in result["quiet"])==1
    return result


def main():
    by_case={}
    for tag in ("B","J0","J1","J2","C1","T4","T8","J1x2"):
        spec=cases()[tag]
        by_case[tag]={label: compare(spec,state,spec["roles"]["anchors"]) for label,state in loads(spec).items()}
    base=by_case["J1"]["0"]
    other=by_case["J1"]["1"]
    changed=[p for p in base if base[p]!=other[p]]
    two={}
    for tag in ("T4","T8"):
        arms=by_case[tag]
        two[tag] = {p:arms["3"][p]-arms["2"][p]-arms["1"][p]+arms["0"][p] for p in base}
    result={"by_case":by_case,"loose_pairs":loose_control(),"j1_changed":changed,
            "two_ring_route_interactions":two,"checked_first_layer_pairs":sum(120*len(s) for s in by_case.values())}
    (DATA/"ordinary_formula.json").write_text(json.dumps(result,separators=(",",":"))+"\n")
    print("First layer formula checks", result["checked_first_layer_pairs"], "J1 route counts changed", len(changed))
    print("e0/e15 routes",base["0,15"],other["0,15"],"two-loop interaction",[(k,v["0,15"]) for k,v in two.items()])
    print("Old loose control",result["loose_pairs"])


if __name__=="__main__":
    main()
