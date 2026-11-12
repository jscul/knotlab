"""Referee's independent bond verifier for any size: the family of distinct reachable window-state masks (at most 256) is
tracked exactly for a fixed set S, over all 2^|S| patterns at once (no antichain reduction, no complement trick)."""
import sys, json
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/f0f2b323-7667-54e0-bff8-c1ab470fc84d/scratchpad/referee_C")
from regen import *
import exhpy
from multiprocessing import Pool
def tables(N, knots):
    rows = exhpy.trans_table(N, knots)
    T = [[[rows[(m * 8 + s) * 2 + x] for x in (0, 1)] for s in range(8)] for m in range(N)]
    MS = [[[0] * 256 for _ in (0, 1)] for _ in range(N)]
    FS = [[0] * 256 for _ in range(N)]
    for m in range(N):
        for R in range(256):
            o = [0, 0]
            for s in range(8):
                if R >> s & 1:
                    for x in (0, 1):
                        t = T[m][s][x]
                        if t >= 0: o[x] |= 1 << t
            MS[m][0][R], MS[m][1][R] = o; FS[m][R] = o[0] | o[1]
    return MS, FS
def is_free(N, MS, FS, S):
    S = set(S); fam = {255}
    for m in range(N):
        if m in S:
            fam = {MS[m][x][R] for R in fam for x in (0, 1)}
        else:
            fam = {FS[m][R] for R in fam}
    return 0 not in fam
def task(rec):
    q, b = rec["q"], rec["base"]
    k = regen(q, b); N = 800
    MS, FS = tables(N, k)
    out = []
    for p in rec["pairs"]:
        if p["status"] != "ok": continue
        S = p["members"]
        okshape = p["i"] in S and p["j"] in S and len(set(S)) == p["L"] and min(S) >= p["i"] - 8 and max(S) <= p["j"] + 8
        cons = not is_free(N, MS, FS, S)
        dels = all(is_free(N, MS, FS, [x for x in S if x != y]) for y in S)
        out.append((p["g"], p["L"], okshape, cons, dels))
    return q, b, out
if __name__ == "__main__":
    bases = load_bases()
    allres = []
    with Pool(int(sys.argv[1])) as pool:
        for q, b, out in pool.imap_unordered(task, bases):
            bad = [o for o in out if not (o[2] and o[3] and o[4])]
            print(q, b, len(out), "bad", bad, flush=True)
            allres.append((q, b, out))
    json.dump(allres, open("verify_bonds.json", "w"))
