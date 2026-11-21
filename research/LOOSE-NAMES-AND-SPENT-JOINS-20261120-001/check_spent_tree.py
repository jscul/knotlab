"""Independent tree calculation from parent sets and cuts of the original holder tree."""
from collections import Counter, defaultdict, deque
from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
# This existing ordinary operator supplies only the ordinary co-input proposals on non-tree cuts.
ORDINARY = "ORDINARY-DYNAMICS-20261120-001A"
sys.path.insert(0, str(ROOT / "experiments" / ORDINARY / (ORDINARY + "-E001_ordinary")))
import end_operator


def distances(n, links, start, omitted=None):
    adjacent = [set() for _ in range(n)]
    for i, j in links:
        if (i, j) != omitted:
            adjacent[i].add(j)
            adjacent[j].add(i)
    seen = {k: 0 for k in start}
    queue = deque(seen)
    while queue:
        i = queue.popleft()
        for j in adjacent[i]:
            if j not in seen:
                seen[j] = seen[i] + 1
                queue.append(j)
    return seen


def grouped_distance(n, groups, left, right):
    graph = set()
    for group in groups:
        graph.update(combinations(sorted(group), 2))
    result = distances(n, graph, left)
    return min((result[i] for i in right if i in result), default=None)


def build(length, q, extra=False, close_middle=False):
    arities = [q] * length
    edges = [(k, k + 1) for k in range(length - 1)]
    if extra:
        first_added = []
        for i in range(1, length - 1):
            for _ in range(q - 2):
                vertex = len(arities)
                edges.append((i, vertex))
                arities.append(q)
                if i == length // 2:
                    first_added.append(vertex)
        if close_middle:
            for i in first_added:
                for _ in range(q - 1):
                    edges.append((i, len(arities)))
                    arities.append(q)
    return edges, arities


def tree_report(edges, arities, marks, rival):
    n = len(arities)
    neighbors = [set() for _ in arities]
    for i, j in edges:
        neighbors[i].add(j)
        neighbors[j].add(i)
    loose = {i:q-len(neighbors[i]) for i,q in enumerate(arities) if q>len(neighbors[i])}
    assert all(arities[i]>=max(3,len(neighbors[i])) for i in range(n))
    both = set(loose)
    groups = {pair for adjacent in neighbors for pair in combinations(sorted(both & adjacent), 2)}
    base = set(groups)
    if rival:
        for i,j in edges:
            if i in both or j in both:
                continue
            a, b = neighbors[i] & both, neighbors[j] & both
            if a and b:
                groups.add(tuple(sorted(a | b)))
    charge = Counter(i for row in groups for i in row)
    missing = {i:charge[i]-v for i,v in loose.items() if charge[i]>v}
    report = {"knots": n, "initial_extra": len(groups-base), "initial_missing": missing}
    if missing:
        return report
    children = sorted(groups) + [(i,) for i,v in loose.items() for _ in range(v-charge[i])]
    related = defaultdict(set)
    for k,parents in enumerate(children):
        for parent in parents:
            related[parent].add(k)
    ordinary = end_operator.End(dict.fromkeys(range(len(children)),1),tuple(tuple(js) for js in related.values()))
    groups1 = set(end_operator.proposals(ordinary))
    original_groups1 = set(groups1)
    if rival:
        for i,j in edges:
            if i not in loose or j not in loose:
                continue
            # A child connected to old parents on both sides gives an alternative
            # route around this original name. Fresh private names cannot supply such a route.
            side = set(distances(n, edges, [i], (i,j)))
            if any(side.intersection(g) and side.intersection(g)!=set(g) for g in children):
                continue
            groups1.add(tuple(sorted(related[i] | related[j])))
    demands1 = Counter(i for group in groups1 for i in group)
    fresh = [max(1,3-len(row),demands1[k]) for k,row in enumerate(children)]
    assert len(children)>=2
    assert all(fresh[i]>=demands1[i] for i in range(len(children)))
    meeting = grouped_distance(len(children), groups1, related[marks[0]], related[marks[1]])
    via = distances(n, edges, [marks[0]])
    back = distances(n, edges, [marks[1]])
    h = via[marks[1]]
    route = [i for i in range(n) if via[i]+back[i]==h]
    C = Fraction(1)
    for i in route:
        C *= Fraction(-1,2**(arities[i]-1)-1)
    report.update(disagreement=str((1-C)/2),bond=sum(arities[i] for i in route)-2*h-1,
                  first_births=len(children),first_fresh=sum(fresh),next_extra=len(groups1-original_groups1),
                  next_multi=len(groups1),meeting=None if meeting is None else 1+meeting)
    return report


def run():
    fixtures = [(2,3,False,False,(0,1)),(3,3,False,False,(0,1)),
                (5,6,False,False,(0,4)),(5,6,True,False,(0,4)),(5,6,True,True,(0,4)),
                (7,6,False,False,(0,6)),(7,6,True,False,(0,6))]
    results=[]
    for length,q,extra,close,marked in fixtures:
        edges,arities=build(length,q,extra,close)
        results.append(dict(ordinary=tree_report(edges,arities,marked,False),
                            spent_join=tree_report(edges,arities,marked,True)))
    return results


if __name__ == "__main__":
    print(json.dumps(run(),indent=2))
