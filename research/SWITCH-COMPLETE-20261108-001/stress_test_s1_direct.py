"""every switching class of one glue's signings (representative: signs only off a spanning tree of the incidence graph) and its signed
glue's creation map (the glue block), with far-side verdicts memoized by their masks. The direct run that the row-by-row method was checked against on seed 3 (6 processes).
usage (from the repository root): python3 -B research/SWITCH-COMPLETE-20261108-001/stress_test_s1_direct.py SEED OUT.json [processes]"""
import json, sys, time
import networkx as nx
from multiprocessing import Pool
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "proofs/SWITCH-PROOF-20261108-001A/SWITCH-PROOF-20261108-001A-P001_creation_between_glue_lines_sees_only_the_switching_class"))
import proof_lib as PL
TR = PL.TR
TL = TR.engine().TL
seed = int(sys.argv[1])
glue = [tuple(l) for l in PL.SW.generate([seed], 0)[seed]["glue"]]
g = len(glue); n = 1 + max(max(l) for l in glue)
G = PL.SW.incidence_of_glue(glue)
T = nx.minimum_spanning_tree(G)
key = lambda e: tuple(sorted(e, key=str))
off = sorted({key(e) for e in G.edges()} - {key(e) for e in T.edges()}, key=str)
free = lambda v: None if v is None else (bool(v[0]), bool(v[2]), bool(v[3]))
MEMO = {}
def verdict(mm):
    if mm is None:
        return None
    k = (frozenset(mm[0]), frozenset(mm[1]))
    if k not in MEMO:
        MEMO[k] = free(TL.verdict_from_masks(*mm))
    return MEMO[k]
def signing(mask):
    S = []
    for k, e in enumerate(off):
        if mask >> k & 1:
            S.append(([v for v in e if v[0] == "L"][0][1], [v for v in e if v[0] == "P"][0][1]))
    return S
def job(mask):
    signs = PL.signs_of(glue, signing(mask))
    full = len(TL.solutions(glue, signs, n))
    block, sols = [], []
    for a in range(g):
        AN = TL.solutions(glue, signs, n, skip=a)
        sols.append(len(AN))
        for b in range(g):
            if b != a:
                l = glue[b]
                block.append(verdict(TR.fast_masks(AN, list(l), signs[b], [q for q in range(n) if q not in l]) if len(AN) else None))
    return mask, full, sols, block
if __name__ == "__main__":
    t = time.time()
    with Pool(int(sys.argv[3]) if len(sys.argv) > 3 else 6) as pool:
        res = pool.map(job, range(1 << len(off)), chunksize=8)
    json.dump({"seed": seed, "glue": glue, "off-tree incidences": off, "classes": [
        {"mask": m, "solutions": f, "solutions with each line removed": s, "block": b} for m, f, s, b in res]}, open(sys.argv[2], "w"))
    print("seed", seed, "lines", g, "points", n, "cycle rank", len(off), "classes", len(res),
          "distinct blocks", len({json.dumps(r[3]) for r in res}), round(time.time() - t, 1), "s")
