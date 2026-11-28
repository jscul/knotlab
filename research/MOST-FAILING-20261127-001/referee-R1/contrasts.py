"""Matched populations, weighting controls, and small counterexamples to the prose."""

from collections import Counter, defaultdict
from fractions import Fraction

import networkx as nx

from recount import HERE, jsonl, save, words


def meeting_pattern(code):
    holders = defaultdict(list)
    for u, knot in enumerate(code["supports"]):
        for d in knot:
            holders[d].append(u)
    counts = Counter(tuple(pair) for pair in holders.values())
    graph = nx.Graph()
    graph.add_weighted_edges_from((a, b, mult) for (a, b), mult in counts.items())
    return graph


def classify(codes):
    buckets = defaultdict(list)
    representatives, members = [], defaultdict(list)
    for row in codes:
        graph = meeting_pattern(row)
        # This inexpensive key only excludes impossible matches. Equality is always checked by isomorphism.
        key = (tuple(sorted(dict(graph.degree()).values())), tuple(sorted(dict(graph.degree(weight="weight")).values())))
        for index in buckets[key]:
            if nx.is_isomorphic(graph, representatives[index], edge_match=nx.algorithms.isomorphism.numerical_edge_match("weight", 1)):
                break
        else:
            index = len(representatives)
            representatives.append(graph)
            buckets[key].append(index)
        members[index].append(row)
    return members


def small_cases(codes):
    out = []
    for c in codes:
        if "start" not in c or c["knots"] != 4:
            continue
        assert len(c["groups"]) == 3
        parity_votes = sum(len(group) % 2 for group in c["groups"])
        results = []
        for w in words(c):
            counts = [sum((w >> i) & 1 for i in group) for group in c["groups"]]
            sign = (w & c["cost"]).bit_count() % 2
            assert all(v % 2 == sign for v in counts)
            results.append({"pairs": [p for j, p in enumerate(c["pairs"]) if w >> j & 1],
                            "sign": sign, "pair score": w.bit_count(), "occupied types": sum(v > 0 for v in counts),
                            "fractional pair score": str(sum(Fraction(v, len(g)) for v, g in zip(counts, c["groups"]))),
                            "types different from all-pairs word": sum(v < len(g) for v, g in zip(counts, c["groups"]))})
        best = max(r["pair score"] for r in results)
        assert all(r["sign"] == int(parity_votes >= 2) for r in results if r["pair score"] == best)
        if c["start"] == 43:
            assert {r["sign"] for r in results if r["occupied types"] == 3} == {1}
            fractional = [Fraction(r["fractional pair score"]) for r in results]
            assert max(fractional) == 2 and {r["sign"] for r, v in zip(results, fractional) if v == 2} == {0, 1}
            assert {r["sign"] for r in results if r["types different from all-pairs word"] == 1} == {0}
        out.append({"start": c["start"], "sizes of the three pairings": list(map(len, c["groups"])), "words": results})
    return out


def main():
    codes = jsonl(HERE / "codes.jsonl")
    closure = {r["start"]: r for r in jsonl(HERE / "closures.jsonl")}
    types = {r["type"]: r for r in jsonl(HERE / "types.jsonl")}
    cohorts = classify([c for c in codes if "start" in c or "type" in c])
    rows = []
    for members in cohorts.values():
        grown = [c for c in members if "start" in c]
        static = [c for c in members if "type" in c]
        assert len(static) <= 1
        rows.append({"grown starts": [c["start"] for c in grown], "census types": [c["type"] for c in static],
                     "pair maximum by grown start": dict(Counter(closure[c["start"]]["max principle"] for c in grown)),
                     "pair maximum as census type": types[static[0]["type"]]["max principle"] if static else None})
    shared = [r for r in rows if r["grown starts"] and r["census types"]]
    grown = [r for r in rows if r["grown starts"]]
    label_weight = Counter()
    for c in codes:
        if "type" in c:
            label_weight[types[c["type"]]["max principle"]] += c["labelled"]
    totals = Counter()
    for row in grown:
        for verdict, count in row["pair maximum by grown start"].items():
            totals[verdict] += Fraction(count, len(row["grown starts"]))
    paired_votes = Counter()
    for r in shared:
        for v, n in r["pair maximum by grown start"].items():
            paired_votes[(v, r["pair maximum as census type"])] += n
    summary = {"grown distinct finished patterns": len(grown), "types also reached": len(shared),
               "type-matched starts": sum(len(r["grown starts"]) for r in shared),
               "type-matched maximum pairs [grown, finished, count]": [[a,b,n] for (a,b),n in sorted(paired_votes.items())],
               "grown patterns with varying pair verdict across histories": sum(len(r["pair maximum by grown start"]) > 1 for r in grown),
               "one vote per grown finished pattern, divided among its eligible starts": {v: str(n) for v, n in totals.items()},
               "labelled-pattern votes on the same 173 finished types": dict(label_weight),
               "grown starts with fewer decidable pairs than in finished reading": sum(
                   "start" in c and not c["all unheld decidable"] for c in codes),
               "four-knot hand check": small_cases(codes), "partition": rows}
    save(HERE / "contrasts.json", summary)


if __name__ == "__main__":
    main()
