"""Readout of the referee's eddy search up to six knots (runs/referee-loop-search6, from job_search6.py).

Every start is keyed up to isomorphism (knots coloured by their spares).  A start grows fast when the referee calls it
exponential or explosive, or when its case reached the 2 GB limit or its time limit (every such case is checked against the
study's counts where the study grew it).  A fast start is minimal when no start one step smaller (one spare removed, or one knot
removed; a disconnected remainder counts by its fastest piece) grows fast.  Each minimal start is compared with the catalogue's
entries (`catalogue.json`) and with the starts the study's rule could not decide (`undecided.json`, part U), both read as data.

  ../../../.venv/bin/python -B search6_readout.py > referee_loop_search6.json
"""
import itertools
import json
from collections import Counter
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parents[3]
EXP = ROOT / "experiments/LOOP-CATALOGUE-20261119-001B/LOOP-CATALOGUE-20261119-001B-E001_catalogue"
FAST = {"exponential", "explosive", "case limit (memory)", "case limit (timeout)"}


def graph(n, edges, spares):
    G = nx.Graph()
    for v in range(n):
        G.add_node(v, s=spares[v])
    G.add_edges_from(tuple(e) for e in edges)
    return G


NM = nx.algorithms.isomorphism.categorical_node_match("s", 0)


def key(G):
    return (G.number_of_nodes(), G.number_of_edges(), tuple(sorted(G.nodes[v]["s"] for v in G)),
            nx.weisfeiler_lehman_graph_hash(G, node_attr="s"))


class Index:
    def __init__(self):
        self.by = {}

    def add(self, G, val):
        self.by.setdefault(key(G), []).append((G, val))

    def get(self, G):
        for H, v in self.by.get(key(G), []):
            if nx.is_isomorphic(G, H, node_match=NM):
                return v
        return None


def main():
    idx = Index()
    rows = []
    job = {}
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import job_search6 as J
    for cid, p in J.cases():
        job[cid] = p
    for line in open(ROOT / "runs/referee-loop-search6/results.jsonl"):
        r = json.loads(line)
        p = job[r["case"]]
        spares = [0] * p["n"]
        for v in p["spares"]:
            spares[v] += 1
        cls = r["result"]["class"] if r["status"] == "ok" else f"case limit ({r['status']})"
        G = graph(p["n"], p["edges"], spares)
        idx.add(G, cls)
        rows.append((G, cls, p))

    def fast_of(G):
        if not nx.is_connected(G):
            return any(fast_of(G.subgraph(c).copy()) for c in nx.connected_components(G))
        if G.number_of_nodes() < 2:
            return False
        H = nx.convert_node_labels_to_integers(G)
        v = idx.get(H)
        return v in FAST if v is not None else None

    fast = [(G, c, p) for G, c, p in rows if c in FAST]
    minimal = []
    for G, c, p in fast:
        reds = []
        for v in G.nodes:
            if G.nodes[v]["s"]:
                H = G.copy()
                H.nodes[v]["s"] -= 1
                reds.append(H)
        for v in G.nodes:
            H = G.copy()
            H.remove_node(v)
            reds.append(H)
        vals = [fast_of(H) for H in reds]
        if not any(x is True for x in vals):
            minimal.append((G, c, p, vals.count(None)))
    cat = Index()
    for e in json.load(open(EXP / "catalogue.json")):
        cat.add(graph(e["n"], e["edges"], e["spares"]), "catalogue")
    und = Index()
    for e in json.load(open(EXP / "undecided.json")):
        und.add(graph(e["n"], e["edges"], e["spares"]), "undecided")
    out = []
    for G, c, p, unknown in minimal:
        out.append({"n": G.number_of_nodes(), "edges": sorted(tuple(sorted(e)) for e in G.edges()),
                    "spares": [G.nodes[v]["s"] for v in sorted(G.nodes)], "class": c,
                    "a catalogue entry": cat.get(nx.convert_node_labels_to_integers(G)) == "catalogue",
                    "in the study's undecided list (part U)": und.get(nx.convert_node_labels_to_integers(G)) == "undecided",
                    "reductions not in the search": unknown})
    print(json.dumps({"starts": len(rows), "classes": dict(Counter(c for _, c, _ in rows)), "fast": len(fast),
                      "minimal fast starts": len(out),
                      "minimal: catalogue entries": sum(o["a catalogue entry"] for o in out),
                      "minimal: in part U's undecided list": sum(o["in the study's undecided list (part U)"] for o in out),
                      "minimal: neither": [o for o in out if not o["a catalogue entry"] and not o["in the study's undecided list (part U)"]],
                      "minimal": out}, indent=1, default=str))


if __name__ == "__main__":
    main()
