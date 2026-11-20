"""Find certified residual pairs between pure three-parent children of start-01."""
import argparse
from collections import defaultdict
from itertools import combinations
import json
from pathlib import Path

from quotient_next import OUTPUT, Roster, bits, invert, load, touching


def pure_triangle_graph(roster):
    adjacency = [0] * len(roster.blocks)
    high = 0
    low = {}
    for u, mark in enumerate(roster.affiliation):
        assert mark.bit_count() >= 2
        if mark.bit_count() != 2:
            high |= 1 << u
            continue
        b, c = bits(mark)
        assert (b,c) not in low
        adjacency[b] |= 1 << c
        adjacency[c] |= 1 << b
        low[b,c] = u

    block_high = [block & high for block in roster.blocks]
    chosen, parents = [], []
    incident = defaultdict(list)
    for b, c in low:
        upper = adjacency[b] & adjacency[c]
        for d in bits(upper >> (c+1) << (c+1)):
            high_extension = (block_high[b] & block_high[c]) | (block_high[b] & block_high[d]) | (block_high[c] & block_high[d])
            if high_extension:
                continue
            group = (low[b,c],low[b,d],low[c,d])
            i = len(chosen)
            chosen.append((b,c,d))
            parents.append(sum(1 << x for x in group))
            incident[b,c].append((d,i))
            incident[b,d].append((c,i))
            incident[c,d].append((b,i))

    protected = [[] for _ in chosen]
    evidence_count = 0
    disjoint = None
    first = None
    for (b,c), local in incident.items():
        outside_base = ~(block_high[b] | block_high[c])
        for (d,i),(e,j) in combinations(local,2):
            if adjacency[d] >> e & 1 or block_high[d] & block_high[e] & outside_base:
                continue
            protected[i].append(j)
            protected[j].append(i)
            evidence_count += 1
            if first is None:
                first = (i,j)
            elif disjoint is None and not set(first) & {i,j}:
                disjoint = (first,(i,j))
    return chosen, parents, protected, evidence_count, disjoint


def closed_turn_or_path(graph, parents, limit):
    exhausted = {}
    best = []
    examined = 0

    def following(edge):
        u,v = edge
        return ((v,w) for w in graph[v] if not parents[u] & parents[w])

    for i, neighbors in enumerate(graph):
        for j in neighbors:
            edge = (i,j)
            if edge in exhausted:
                continue
            route = [edge]
            place = {edge: 0}
            stack = [following(edge)]
            distance = [0]
            exit_choice = [None]
            while stack:
                if examined >= limit:
                    return None, best, examined, False
                tail = next(stack[-1], None)
                if tail is None:
                    finished = route.pop()
                    stack.pop()
                    del place[finished]
                    length = distance.pop()+1
                    exhausted[finished] = (length, exit_choice.pop())
                    if length > len(best):
                        best = [finished]
                        while (nxt := exhausted[best[-1]][1]) is not None:
                            best.append(nxt)
                    if distance and length > distance[-1]:
                        distance[-1] = length
                        exit_choice[-1] = finished
                    continue
                examined += 1
                if tail in place:
                    return route[place[tail]:], best, examined, True
                if tail in exhausted:
                    length = exhausted[tail][0]
                    if length > distance[-1]:
                        distance[-1] = length
                        exit_choice[-1] = tail
                    continue
                place[tail] = len(route)
                route.append(tail)
                stack.append(following(tail))
                distance.append(0)
                exit_choice.append(None)
    return None, best, examined, True


def verify_edges(roster, triangles, parents, pairs):
    output = []
    for i,j in pairs:
        a,b = parents[i],parents[j]
        overlap = a & b
        assert overlap.bit_count() == 1
        p = next(bits(overlap))
        crossing = []
        for u in bits(a ^ overlap):
            for v in bits(b ^ overlap):
                related = bool(roster.rows[u] >> v & 1)
                if related:
                    assert roster.rows[u] & roster.rows[v] & ~roster.rows[p] == 0
                crossing.append((u,v,related))
        assert roster.is_unheld_maximum(a) and roster.is_unheld_maximum(b)
        output.append({"block_triples": [triangles[i],triangles[j]],
                       "child_parents": [list(bits(a)),list(bits(b))], "shared_parent": p,
                       "crossings_checked": crossing})
    return output


def separated_triangles(roster, triangles, parents, cap):
    n = len(roster.blocks)
    blocks = [1 << b for b in range(n)]
    for mark in set(roster.affiliation):
        for b in bits(mark):
            blocks[b] |= mark
    patterns = [sum(1 << b for b in tri) for tri in triangles]
    occurrences = invert(n, patterns)
    full = (1 << len(triangles)) - 1
    order = sorted(range(len(triangles)), key=lambda i: (touching(patterns[i], blocks).bit_count(), i))
    best = (1, None, None)
    for i in order[:cap]:
        radius = patterns[i]
        gap = 2
        while radius != (1 << n) - 1:
            viable = full ^ touching(radius, occurrences)
            if not viable:
                break
            if gap > best[0]:
                best = gap,i,next(bits(viable))
            enlarged = touching(radius, blocks)
            assert enlarged != radius, "archive age-ten candidate end must be connected"
            radius = enlarged
            gap += 1
    bound,i,j = best
    if i is None:
        return None
    a,b = parents[i],parents[j]
    assert roster.is_unheld_maximum(a) and roster.is_unheld_maximum(b)
    checked = 0
    seen = a
    while not seen & b:
        enlarged = touching(seen, roster.rows)
        assert enlarged != seen
        seen = enlarged
        checked += 1
    assert checked >= bound
    return {"triangle_block_names": [triangles[i],triangles[j]],
            "parents": [list(bits(a)),list(bits(b))], "source_candidate_set_distance": checked,
            "new_children_candidate_distance": checked+1,
            "covered_noncomplete_through_age": 10+checked,
            "at_least_two_births_through_age": 11+checked,
            "triangles_used_as_search_roots": min(cap,len(triangles))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_dir", type=Path)
    args = parser.parse_args()
    src = load("pair_star_residual_start01")
    assert src["residual_pairs"] == 0
    roster = Roster(args.input_dir / src["input"], src["input_sha256"])
    triangles, parents, graph, records, disjoint = pure_triangle_graph(roster)
    separation = separated_triangles(roster, triangles, parents, 128)
    cycle, path, turns, complete = closed_turn_or_path(graph, parents, 4_000_000)
    if cycle:
        assert all(y == p and not parents[x] & parents[q]
                   for (x,y),(p,q) in zip(cycle,cycle[1:]+cycle[:1]))
    if path:
        assert all(y == p and not parents[x] & parents[q] for (x,y),(p,q) in zip(path,path[1:]))
    if disjoint:
        assert not set(disjoint[0]) & set(disjoint[1])
    result = {"source_sha256": roster.digest, "live_child_age": 11,
              "pure_triangle_children": len(triangles), "certified_residual_pairs_at_age_11": records,
              "turns_examined": turns, "turn_search_has_definite_cycle_verdict": complete,
              "separated_triangle_children": separation,
              "disjoint_residual_grandchildren_at_age_12": verify_edges(roster, triangles, parents, disjoint or []),
              "protected_cycle": verify_edges(roster, triangles, parents, cycle or []),
              "protected_path": verify_edges(roster, triangles, parents, path)}
    (OUTPUT / "quotient_triangles01.json").write_text(json.dumps(result,indent=2) + "\n")
    print(len(triangles), records, bool(disjoint), len(cycle or []), len(path), turns, complete, separation)


if __name__ == "__main__":
    main()
