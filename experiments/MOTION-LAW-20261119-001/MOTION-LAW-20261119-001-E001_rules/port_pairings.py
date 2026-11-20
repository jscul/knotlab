"""Test invariant pairings on anonymous induced balls before giving a marked arrival."""

from collections import Counter
import json

import networkx as nx

from sources import DATA, cases, source_and_stage


def matchings(legs):
    if not legs:
        yield frozenset()
        return
    a = min(legs)
    for b in legs - {a}:
        pair = frozenset((a, b))
        for smaller in matchings(legs - pair):
            yield smaller | {pair}


def fixed_matchings(graph, v, radius):
    legs = set(graph[v])
    options = list(matchings(legs))
    if len(options) <= 1:
        return options
    ball = nx.ego_graph(graph, v, radius=radius)
    for w in ball:
        ball.nodes[w]["root"] = w == v
    maps = nx.algorithms.isomorphism.GraphMatcher(ball, ball, node_match=lambda a, b: a == b)
    for perm in maps.isomorphisms_iter():
        options = [pairs for pairs in options if
                   frozenset(frozenset(perm[x] for x in pair) for pair in pairs) == pairs]
        if not options:
            break
    return options


def run(spec):
    stars, reader = source_and_stage(spec)
    graph = nx.Graph(reader.graph)
    names = {frozenset(row): v for v, row in enumerate(reader.stars)}
    seam_ids = {names[frozenset(stars[i])]: i for i in spec["roles"].get("seams", [])}
    totals = Counter()
    seams = []
    for v in graph:
        for radius in (1, 2):
            options = fixed_matchings(graph, v, radius)
            totals[radius, graph.degree[v], len(options)] += 1
            if v in seam_ids:
                computed = {frozenset((x, y)) for x in graph[v] for y in reader.exits((x, v))}
                seams.append(dict(source_seam=seam_ids[v], radius=radius, invariant_matchings=len(options),
                                  agrees_with_registered_pairs=bool(len(options) == 1 and computed == options[0])))
    return dict(source_knots=len(graph), seams=sorted(seams, key=lambda s: (s["source_seam"], s["radius"])),
                counts=[dict(radius=r, degree=g, matchings=m, knots=n) for (r,g,m),n in sorted(totals.items())])


if __name__ == "__main__":
    result = {c["id"]: run(c) for c in cases()}
    (DATA / "port_pairings.json").write_text(json.dumps(result, indent=2)+"\n")
    print("Knots:", sum(r["source_knots"] for r in result.values()),
          "attachment cases:", sum(len(r["seams"])//2 for r in result.values()))
