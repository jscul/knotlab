#!/usr/bin/env python3
"""Referee PARITY-MIX-R1, a fairer local baseline: generalized arc consistency on classes. For every surviving placement with a count
fixed but unreached (result_p3.jsonl / result_p4.jsonl), and for every class tuple on count 0 that some state has (enumerated by SAT),
start from count 0's classes and every other copy's full class set and prune, knot by knot (count 0 enumerated and fixing recomputed with the lighter encoding of ref_parity_enum.py), every class with no support in the other
two members' sets (support: the knot's relation projected to classes, i.e. some flips make the three states a stitch triple, or the
three classes sum to zero for a parity knot), to a fixpoint. Count r is reached by this propagation when every copy of it is left with
one class for every such tuple on count 0. A count fixed but unreached by the frozen rule and reached here is local after all.

    python3 -B ref_gac.py p3|p4      (writes result_gac_p3.json / result_gac_p4.json)"""
import itertools
import gzip
import json
import sys
import time
from pathlib import Path

from pysat.solvers import Glucose4

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ref_parity as RP  # noqa: E402
import ref_parity_enum as E  # noqa: E402
import ref_parity_fast as F  # noqa: E402
from pysat.solvers import Solver  # noqa: E402

CAP = 5000


def read_lines(path):
    """the rows, from the plain file or its gzip copy (result_p4.jsonl is kept compressed)"""
    if path.exists():
        return path.read_text().splitlines()
    with gzip.open(str(path) + ".gz", "rt") as fh:
        return fh.read().splitlines()


def class_relations(st):
    W, full, P = st["W"], st["full"], st["P"]
    ri = st["rep index"]
    nae = {(ri[u], ri[v], ri[w]) for u in W for v in W for w in W if RP.stitch(u, v, w, st)}
    reps = st["reps"]
    C = len(reps)
    canon = lambda x: min(x, x ^ full)
    idx = {r: j for j, r in enumerate(reps)}
    par = {(a, b, idx[canon(reps[a] ^ reps[b])]) for a in range(C) for b in range(C) if canon(reps[a] ^ reps[b]) in idx}
    return nae, par


def count0_tuples(st, n, K):
    """the class tuples on count 0 over all states (lighter encoding, blocking each count-0 tuple up to flips)"""
    P, full = st["P"], st["full"]
    idx = {r: j for j, r in enumerate(st["reps"])}
    cl = F.light_cnf(st, n, K)
    var = lambda x, i: x * P + i + 1
    nxt = max(abs(l) for c in cl for l in c) + 1
    out = []
    with Solver(name="cadical153", bootstrap_with=cl) as s:
        while s.solve() and len(out) < CAP:
            m = s.get_model()
            words = [sum(1 << i for i in range(P) if m[var(x, i) - 1] > 0) for x in range(n)]
            out.append(tuple(idx[min(w, w ^ full)] for w in words))
            block = []
            for x, w in enumerate(words):
                d, e, g = nxt, nxt + 1, nxt + 2
                nxt += 3
                s.add_clause([-d] + [(-var(x, i) if (w >> i) & 1 else var(x, i)) for i in range(P)])
                s.add_clause([-e] + [(var(x, i) if (w >> i) & 1 else -var(x, i)) for i in range(P)])
                s.add_clause([-g, d])
                s.add_clause([-g, e])
                block.append(g)
            s.add_clause(block)
    return out, len(out) >= CAP


def gac(n, K, rels, C, t0):
    v = lambda r, c: (r % n) * n + (c % n)
    D = [set(range(C)) for _ in range(n * n)]
    for c in range(n):
        D[v(0, c)] = {t0[c]}
    knots = [(r * n + c, (v(r, c), v(r, c + 1), v(r + 1, c))) for r in range(n) for c in range(n)]
    changed = True
    while changed:
        changed = False
        for cell, (x, y, z) in knots:
            rel = rels[1] if cell in K else rels[0]
            ok = [t for t in rel if t[0] in D[x] and t[1] in D[y] and t[2] in D[z]]
            for j, w in enumerate((x, y, z)):
                new = {t[j] for t in ok}
                if new != D[w]:
                    D[w] = new
                    changed = True
    return [all(len(D[v(r, c)]) == 1 for c in range(n)) for r in range(1, n)]


def main():
    part = sys.argv[1]
    t0 = time.time()
    hs = {RP.setup(h)["name"]: h for h in RP.hs()}
    out = {"placements with a count fixed but unreached": 0, "such counts": 0, "of them reached by arc consistency": 0,
           "placements with one left after arc consistency": 0, "count-0 tuples capped": 0, "by deepest source left": {}}
    for line in read_lines(HERE / f"result_{part}.jsonl"):
        res = json.loads(line)
        st = RP.setup(hs[res["harmony"]])
        rels = class_relations(st)
        C = len(st["reps"])
        n = res["n"]
        func = RP.census(st)["functional slots"]
        for row in res["rows"]:
            if not row.get("state") or not row.get("fixed but unreached") or not (0 < row["k"] < n * n):
                continue
            K = frozenset(row["cells"])
            frozen, fixed = E.fixing_light(st, n, E.light_variant(st, n, K, "whole"))
            reach = RP.propagation(n, n, K, func)
            fbu = [r for r in range(n - 1) if fixed[r] and not frozen[r] and not reach[r]]
            tuples, capped = count0_tuples(st, n, K)
            out["count-0 tuples capped"] += capped
            reached = [all(x) for x in zip(*(gac(n, K, rels, C, t) for t in tuples))]
            left = [r for r in fbu if not reached[r]]
            out["placements with a count fixed but unreached"] += 1
            out["such counts"] += len(fbu)
            out["of them reached by arc consistency"] += len(fbu) - len(left)
            if left:
                out["placements with one left after arc consistency"] += 1
                srcs = [s for r, s in zip(fbu, row["sources"]) if r in left]
                deep = max(srcs, key=["B1 parity algebra", "B2 parity and states", "BN stitches alone", "only the whole"].index)
                out["by deepest source left"][deep] = out["by deepest source left"].get(deep, 0) + 1
        print(res["harmony"][:40], out, round(time.time() - t0), "s", flush=True)
    (HERE / f"result_gac_{part}.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
