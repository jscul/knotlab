"""every switching class of one glue's signings and its signed glue's creation map (the glue block), computed row by row: by
SWITCH-PROOF's theorem applied to the glue without line a, row a depends only on the signing's switching class there, so each row is
computed once per class of the glue without that line and the blocks are assembled from the rows; a sample of rows is recomputed
directly as a check. SWITCH-COMPLETE-S1 (docs/LONG_RUNNING.md, unit sw-complete-s1) ran it for seeds 3, 6 and 36 with 8 processes.
usage (from the repository root): python3 -B research/SWITCH-COMPLETE-20261108-001/stress_test_s1_blocks.py SEED OUT.json [processes]"""
import json, random, sys, time
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
idx = {frozenset(e): k for k, e in enumerate(off)}
free = lambda v: None if v is None else (bool(v[0]), bool(v[2]), bool(v[3]))
def signing(mask):
    return [([v for v in e if v[0] == "L"][0][1], [v for v in e if v[0] == "P"][0][1]) for k, e in enumerate(off) if mask >> k & 1]
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
    """far-side verdicts depend only on the masks; memoized within each process"""
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
    out = []
    for b in range(g):
        if b != a:
            l = glue[b]
            out.append(verdict(TR.fast_masks(AN, list(l), signs[b], [q for q in range(n) if q not in l])) if len(AN) else None)
    return a, m, out
def count(m):
    return m, len(TL.solutions(glue, PL.signs_of(glue, signing(m)), n))
if __name__ == "__main__":
    t = time.time()
    N = 1 << len(off)
    reps = [{} for a in range(g)]
    for m in range(N):
        for a in range(g):
            reps[a].setdefault(restr(a, m), m)
    jobs = [(a, m) for a in range(g) for m in sorted(reps[a].values())]
    rnd = random.Random(seed)
    sample = [(a, rnd.randrange(N)) for a in range(g) for _ in range(4)]
    with Pool(int(sys.argv[3]) if len(sys.argv) > 3 else 8) as pool:
        rows = pool.map(row, jobs + sample, chunksize=4)
        counts = dict(pool.map(count, range(N), chunksize=64))
    R = {(a, restr(a, m)): out for a, m, out in rows[:len(jobs)]}
    sample_ok = all(R[(a, restr(a, m))] == out for a, m, out in rows[len(jobs):])
    classes = [{"mask": m, "solutions": counts[m], "block": [x for a in range(g) for x in R[(a, restr(a, m))]]} for m in range(N)]
    json.dump({"seed": seed, "glue": glue, "off-tree incidences": off, "rows computed": len(jobs), "sampled rows recomputed directly": len(sample),
               "sampled rows agree": sample_ok, "classes": classes}, open(sys.argv[2], "w"))
    print("seed", seed, "lines", g, "points", n, "cycle rank", len(off), "classes", N, "rows", len(jobs), "sample ok", sample_ok,
          "distinct blocks", len({json.dumps(c["block"]) for c in classes}), round(time.time() - t, 1), "s", flush=True)
