"""does every single row single out the Pfaffian class? For each line a, the rows of all classes of the glue without a, and how many
share the Pfaffian class's row a. CONTRA-READ-P2 (docs/LONG_RUNNING.md, unit contra-read-p2) ran it on seeds 1, 192, 240, 246 and 300 with 8 processes.
usage (from the repository root): python3 -B research/CONTRA-READ-20261108-001/stress_test_p2.py SEED OUT.json [processes]"""
import json, sys, time
from multiprocessing import Pool
from pathlib import Path
import networkx as nx
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "proofs/SWITCH-PROOF-20261108-001A/SWITCH-PROOF-20261108-001A-P001_creation_between_glue_lines_sees_only_the_switching_class"))
import proof_lib as PL
TR = PL.TR
TL = TR.engine().TL
seed = int(sys.argv[1])
run = PL.SW.generate([seed], 0)[seed]
glue = [tuple(l) for l in run["glue"]]
g = len(glue); n = 1 + max(max(l) for l in glue)
G = PL.SW.incidence_of_glue(glue)
T = nx.minimum_spanning_tree(G)
key = lambda e: tuple(sorted(e, key=str))
off = sorted({key(e) for e in G.edges()} - {key(e) for e in T.edges()}, key=str)
idx = {frozenset(e): k for k, e in enumerate(off)}
FUND = []
for u, w in off:
    p = nx.shortest_path(T, u, w)
    FUND.append({frozenset(e) for e in zip(p, p[1:])} | {frozenset((u, w))})
free = lambda v: None if v is None else (bool(v[0]), bool(v[2]), bool(v[3]))
def signing(mask):
    return [([v for v in e if v[0] == "L"][0][1], [v for v in e if v[0] == "P"][0][1]) for k, e in enumerate(off) if mask >> k & 1]
def mask_of(S):
    E = {frozenset((("L", i), ("P", p))) for i, p in S}
    return sum((len(E & C) & 1) << k for k, C in enumerate(FUND))
def cyc_vec(cyc):
    v = 0
    for u, w in zip(cyc, cyc[1:] + cyc[:1]):
        k = idx.get(frozenset((u, w)))
        if k is not None:
            v ^= 1 << k
    return v
BASIS = []
for a in range(g):
    Ga = G.copy(); Ga.remove_node(("L", a))
    BASIS.append([cyc_vec(c) for c in nx.cycle_basis(Ga)])
restr = lambda a, m: tuple(bin(m & v).count("1") & 1 for v in BASIS[a])
MEMO = {}
def verdict(mm):
    if mm is None:
        return None
    k = (frozenset(mm[0]), frozenset(mm[1]))
    if k not in MEMO:
        MEMO[k] = free(TL.verdict_from_masks(*mm))
    return MEMO[k]
def row(job):
    a, m = job
    signs = PL.signs_of(glue, signing(m))
    AN = TL.solutions(glue, signs, n, skip=a)
    return a, m, [verdict(TR.fast_masks(AN, list(glue[b]), signs[b], [q for q in range(n) if q not in glue[b]])) if len(AN) else None
                  for b in range(g) if b != a]
def count(m):
    return m, len(TL.solutions(glue, PL.signs_of(glue, signing(m)), n))
if __name__ == "__main__":
    t = time.time()
    N = 1 << len(off)
    pf = mask_of([tuple(x) for x in run["minimal"]])
    per_line = []
    with Pool(int(sys.argv[3]) if len(sys.argv) > 3 else 8) as pool:
        for a in range(g):
            reps = {}
            for m in range(N):
                reps.setdefault(restr(a, m), m)
            rows = {restr(a, m): r for a_, m, r in pool.map(row, [(a, m) for m in reps.values()], chunksize=8)}
            target = rows[restr(a, pf)]
            same = sorted(r for r, v in rows.items() if v == target)
            per_line.append({"line": a, "classes of the glue without the line": len(rows), "sharing the Pfaffian row": len(same),
                             "distinct rows": len({json.dumps(v) for v in rows.values()}), "Pfaffian row": target})
            print("seed", seed, "line", a, "restricted classes", len(rows), "sharing the Pfaffian row", len(same), round(time.time() - t, 1), "s", flush=True)
    json.dump({"seed": seed, "lines": g, "cycle rank": len(off), "pfaffian class": pf, "per line": per_line}, open(sys.argv[2], "w"), indent=1)
    print("seed", seed, "every row singles out the Pfaffian class:", all(x["sharing the Pfaffian row"] == 1 for x in per_line), round(time.time() - t, 1), "s", flush=True)
