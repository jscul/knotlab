"""Referee's fresh recomputation for RIGID-LEVEL-R1: #2's knots by level (pattern builder from LEVEL-RETURN-R1's referee),
the pair graph's bipartiteness and one-sided closure of each knot's same-parity pair, levels 5..12. Does not use the study's scripts."""
import json, sys
from pathlib import Path
from collections import deque
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "research/LEVEL-RETURN-20261113-001/referee-R1/codex/automata"))
import vector_levels as vl

key = json.loads((vl.SOURCE / (vl.KEYS["two"] + ".json")).read_bytes())["key"]
s, swaps, zero, one, placements = key
words = [()] + [(q,) for q in range(s)] + [(q, r) for q in range(s) for r in range(s)]
out = {"key_sha": vl.KEYS["two"], "placements": placements, "levels": {}}
for n, actions, parity, first_last, t0, _ in vl.iterate(key, 12):
    if n < 5:
        continue
    knots = set()
    for pl in placements:
        imgs = np.stack([actions[w] for w in pl])  # placement entries index the words list
        for x in range(1 << n):
            t = tuple(sorted(int(v) for v in imgs[:, x]))
            if len(set(t)) == 3:
                knots.add(t)
    allpar = [k for k in knots if parity[k[0]] == parity[k[1]] == parity[k[2]]]
    kept = [k for k in knots if k not in set(allpar)]
    adj = {}
    pairs = []
    for k in kept:
        ps = [parity[v] for v in k]
        apex = [v for v in k if ps.count(parity[v]) == 1][0]
        pair = tuple(v for v in k if v != apex)
        pairs.append((pair, apex))
        a, b = pair
        adj.setdefault(a, set()).add(b); adj.setdefault(b, set()).add(a)
    colour, bip = {}, True
    for v0 in adj:
        if v0 in colour: continue
        colour[v0] = 0; dq = deque([v0])
        while dq and bip:
            v = dq.popleft()
            for u in adj[v]:
                if u not in colour: colour[u] = 1 - colour[v]; dq.append(u)
                elif colour[u] == colour[v]: bip = False
    by_pair = {}
    for pair, apex in pairs:
        by_pair.setdefault(pair, set()).add(apex)
    sizes = []
    for pair0, _ in pairs:
        C = set(pair0); changed = True
        while changed:
            changed = False
            for pair, apexes in by_pair.items():
                if pair[0] in C and pair[1] in C and not apexes <= C:
                    C |= apexes; changed = True
        sizes.append(len(C))
    out["levels"][n] = {"knots": len(knots), "parity_violated_knots": len(allpar), "kept": len(kept),
                        "pair_graph_bipartite": bip, "closure_min": min(sizes), "closure_max": max(sizes)}
    print(n, out["levels"][n], flush=True)
(Path(__file__).with_suffix(".json")).write_text(json.dumps(out, indent=1))
