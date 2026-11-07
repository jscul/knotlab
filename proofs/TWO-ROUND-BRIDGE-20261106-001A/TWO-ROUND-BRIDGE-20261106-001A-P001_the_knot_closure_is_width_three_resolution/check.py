#!/usr/bin/env python3
"""Checks for TWO-ROUND-BRIDGE-20261106-001A: the knot closure is width-3 resolution.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy). Uses PROCS processes (default 12)."""
import collections
import hashlib
import itertools
import json
import os
import random
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import bridge_lib as BL  # noqa: E402

LL = BL.LL
SL = LL.SL
CL, GL, J, G, E = SL.CL, SL.GL, SL.J, SL.G, SL.E
T0 = time.time()
OUT = {}
REL = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str), round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


# ------------------------------------------------------------------------------------------------ 1. the elimination lemma
def lemma():
    """two knots sharing two variables: width-3 resolvents exist exactly when sign-compatible, and are then the clauses of the
    knot that the two knots imply on the remaining three variables"""
    tally = collections.Counter()
    # variables 0 = h (eliminated), 1 = s (kept shared), 2 = t (only in A), 3 = u (only in B)
    for va in itertools.product((0, 1), repeat=3):          # A on (h, s, t) forbids va and its complement
        for vb in itertools.product((0, 1), repeat=3):      # B on (h, s, u) forbids vb and its complement
            def cl(vars_, v):
                return (sum(1 << q for q, b in zip(vars_, v) if b == 0), sum(1 << q for q, b in zip(vars_, v) if b == 1))
            A = [cl((0, 1, 2), va), cl((0, 1, 2), tuple(1 - b for b in va))]
            B = [cl((0, 1, 3), vb), cl((0, 1, 3), tuple(1 - b for b in vb))]
            res = set()
            for (p1, n1), (p2, n2) in itertools.product(A, B):
                clash = (p1 & n2) | (n1 & p2)
                if clash and not clash & (clash - 1):
                    p, n = (p1 | p2) & ~clash, (n1 | n2) & ~clash
                    if BL.popcount(p | n) <= 3:
                        res.add((p, n))
            compat = (va[0] ^ va[1]) != (vb[0] ^ vb[1])
            # the semantic projection of A and B onto (s, t, u) and onto (h, t, u)
            rows = [r for r in itertools.product((0, 1), repeat=4)
                    if (r[0], r[1], r[2]) not in (va, tuple(1 - b for b in va)) and
                    (r[0], r[1], r[3]) not in (vb, tuple(1 - b for b in vb))]
            want = set()
            for tri in ((1, 2, 3), (0, 2, 3)):
                kc = BL.knot_clauses(rows, tri)
                if kc:
                    want |= set(kc)
            tally["compatible" if compat else "incompatible"] += 1
            tally["resolvents equal the implied knots" if res == want else "MISMATCH"] += 1
            tally["width-3 resolvents exist exactly when compatible" if bool(res) == compat else "MISMATCH"] += 1
    return tally


# ------------------------------------------------------------------------------------------------ 2. the exhaustive local check
def local_task(args):
    fname, k, cols = args
    F = dict(SL.FARS)[fname]
    reps, rows = LL.far_classes(F)
    fr = LL.far_relation(rows, cols)
    if k not in REL:
        REL[k] = LL.near_relations(k)
    rel = REL[k]
    L = BL.Bridge(k, fr, len(cols))
    tot = collections.Counter()
    step = 1 << 20
    for a in range(0, len(rel), step):
        chunk = rel[a:a + step]
        A = L.analyse(chunk)
        ok = A["ok"]
        eq = L.types(chunk, A)
        R2 = L.two_rounds(A)
        NR, bad = L.two_rounds_nr(A, eq)
        NRx, _ = L.two_rounds_nr(A, eq, mode="incompatible")
        tot["relations"] += len(ok)
        tot["non-degenerate"] += int(ok.sum())
        for tri in A["knot"]:
            cnt = eq[(tri, "count")]
            tot["non-degenerate knots missing other than one class"] += int((ok & A["knot"][tri] & (cnt != 1)).sum())
        tot["compatible steps whose conclusion is not a knot"] += int((ok & bad).sum())
        for tri in R2:
            kk = ok & A["knot"][tri]
            shape = "".join(sorted(L.kind(q) for q in tri))
            tot["crossing knots"] += int(kk.sum())
            tot["reached by the two-round rule"] += int((kk & R2[tri]).sum())
            tot["reached by its literal steps taken sign-compatible"] += int((kk & NR[tri]).sum())
            tot["%s: reached, but every literal two-round step is sign-incompatible" % shape] += int((kk & R2[tri] & ~NR[tri]).sum())
            tot["%s: reached by the two-round rule" % shape] += int((kk & R2[tri]).sum())
            tot["literal compatible steps reaching an unreached knot"] += int((kk & NR[tri] & ~R2[tri]).sum())
            tot["control: disagreement with incompatible steps"] += int((kk & (R2[tri] != NRx[tri])).sum())
        tot["round-one witnesses that are incompatible"] += int(L.incompatible_witness(A, eq).sum())
    return args, tot


# ------------------------------------------------------------------------------------------------ 3. widths on small relations
def width_task(args):
    fname, k, cols = args
    F = dict(SL.FARS)[fname]
    reps, frows = LL.far_classes(F)
    fr = LL.far_relation(frows, cols)
    rel = LL.near_relations(k)
    L = LL.Local(k, fr, len(cols))
    A = L.analyse(rel)
    R2 = L.two_rounds(A)
    m = len(cols)
    npts = 3 + k + m
    near_cols = [0, 1, 2] + list(range(3, 3 + k))
    far_cols = [0, 1, 2] + list(range(3 + k, npts))
    T = 1 << k
    tot = collections.Counter()
    for idx in np.nonzero(A["ok"])[0]:
        crossing = [t for t in R2 if A["knot"][t][idx]]
        if not crossing:
            continue
        r = int(rel[idx])
        nrows = {PYi + tuple((t >> j) & 1 for j in range(k)) for i, PYi in enumerate(LL.PY) for t in range(T) if r >> (i * T + t) & 1}
        frows_ = {LL.PY[i] + tuple(f) for i, f in fr}
        rows = [nr + fv[3:] for nr in nrows for fv in frows_ if fv[:3] == nr[:3]]
        ax = BL.implicates([tuple(x[c] for c in near_cols) for x in rows], near_cols, 3) | \
            BL.implicates([tuple(x[c] for c in far_cols) for x in rows], far_cols, 3)
        # semantic content of the axioms on all local points
        J3 = [x for x in itertools.product((0, 1), repeat=npts)
              if all(any((x[q] == 1 and (p >> q) & 1) or (x[q] == 0 and (n >> q) & 1) for q in range(npts)) for p, n in ax)]
        targets = {t: BL.knot_clauses(rows, t) for t in crossing}
        flat = [c for t in crossing for c in targets[t]]
        got = {}
        for w in (3, 4, 5):
            got[w] = BL.saturate(ax, w, flat)
        onY = {w: BL.saturate(ax, w, flat, pivots=0b111) for w in (3, 4)}
        for t in crossing:
            shape = "".join(sorted({0: "Y", 1: "Y", 2: "Y"}.get(p, "N" if p < 3 + k else "C") for p in t))
            d = {w: all(c in got[w] for c in targets[t]) for w in (3, 4, 5)}
            depth = {w: max(got[w][c] for c in targets[t]) if d[w] else None for w in (3, 4, 5)}
            s3 = len({tuple(x[p] for p in t) for x in J3}) < 8
            reached = bool(R2[t][idx])
            tot[(shape, "reached" if reached else "new", "count")] += 1
            tot[(shape, "reached" if reached else "new", "width-3 derivable" if d[3] else "not width-3 derivable")] += 1
            tot[(shape, "reached" if reached else "new", "implied by one-sided implicates of <= 3 variables" if s3 else "NOT implied")] += 1
            least = next((w for w in (3, 4, 5) if d[w]), None)
            tot[(shape, "reached" if reached else "new", "least width %s" % least)] += 1
            if least:
                tot[(shape, "reached" if reached else "new", "depth at least width %d: %d" % (least, depth[least]))] += 1
            tot["width-3 derivability agrees with the two-round rule" if d[3] == reached else "DISAGREEMENT"] += 1
            if least in (3, 4):
                yd = all(c in onY[least] for c in targets[t])
                ydep = max(onY[least][c] for c in targets[t]) if yd else None
                tot[(shape, "reached" if reached else "new", "at the least width, resolving only on gluing-line variables: %s"
                     % ("same depth" if yd and ydep == depth[least] else ("derivable, depth %s" % ydep if yd else "NOT derivable")))] += 1
    return args, tot


# ------------------------------------------------------------------------------------------------ 5. the route to {c, x, w}
def route_task(args):
    """on every near relation on {x, w} + Y and one far class: which depth-two width-3 route reaches {c, x, w}"""
    fname, c0 = args
    F = dict(SL.FARS)[fname]
    reps, rows = LL.far_classes(F)
    fr = LL.far_relation(rows, [c0])
    rel = LL.near_relations(2)
    L = BL.Bridge(2, fr, 1)
    A = L.analyse(rel)
    eq = L.types(rel, A)
    R2 = L.two_rounds(A)
    K = lambda *p: A["knot"][tuple(sorted(p))]  # noqa: E731

    def E(t, a, b):
        t = tuple(sorted(t))
        return eq[(t, a, b) if (t, a, b) in eq else (t, b, a)]
    c = L.C[0]
    x, w = L.N
    T = tuple(sorted((c, x, w)))
    r1 = {}
    for xx in (x, w):
        for y in L.Y:
            acc = np.zeros(len(rel), dtype=bool)
            for z in L.Y:
                if z != y:
                    acc |= K(c, y, z) & K(xx, y, z) & (E((c, y, z), y, z) ^ E((xx, y, z), y, z))
            r1[(xx, y)] = K(c, xx, y) & acc
    near_route = np.zeros(len(rel), dtype=bool)
    pairs = np.zeros(len(rel), dtype=bool)
    for y in L.Y:
        near_route |= r1[(x, y)] & K(x, w, y) & (E((c, x, y), x, y) ^ E((x, w, y), x, y))
        near_route |= r1[(w, y)] & K(x, w, y) & (E((c, w, y), w, y) ^ E((x, w, y), w, y))
        pairs |= r1[(x, y)] & r1[(w, y)] & (E((c, x, y), c, y) ^ E((c, w, y), c, y))
    kk = A["ok"] & A["knot"][T]
    out = collections.Counter()
    out["{c, x, w} reached"] += int((kk & R2[T]).sum())
    out["reached by a compatible round-one knot and a near knot {x, w, y}"] += int((kk & R2[T] & near_route).sum())
    out["reached by the literal pairs step taken compatible"] += int((kk & R2[T] & pairs).sum())
    out["near-knot route on an unreached knot"] += int((kk & ~R2[T] & near_route).sum())
    return out


# ------------------------------------------------------------------------------------------------ 4. whole splices
def near_side(seed):
    r = random.Random(seed)
    if seed % 2:
        b = r.choice(sorted(GL.SP))
        H, s, n = GL.SP[b]
        return H, s, n, CL.solutions(H, s, n, skip=r.randrange(len(H)))
    n = r.randint(7, 10)
    m = r.randint(n - 2, n + 3)
    H = [tuple(r.sample(range(n), 3)) for _ in range(m)]
    s = [[r.randint(0, 1) for _ in range(3)] for _ in range(m)]
    return H, s, n, CL.solutions(H, s, n)


def join_projection(AN, n_near, AF, far, Y, pts):
    """the patterns of the splice (near rows AN joined with far rows AF over Y) on the points pts"""
    nfar = len(far)
    fidx = {q: i for i, q in enumerate(far)}
    pn = [q for q in pts if q < n_near]
    pf = [q for q in pts if q >= n_near]
    near = collections.defaultdict(set)
    for row in AN:
        near[tuple(int(row[y]) for y in Y)].add(tuple(int(row[q]) for q in pn))
    farm = collections.defaultdict(set)
    for row in AF:
        farm[tuple(int(v) for v in row[nfar:])].add(tuple(int(row[fidx[q]]) for q in pf))
    out = set()
    for key, A in near.items():
        for a in A:
            for b in farm.get(key, ()):
                val = dict(zip(pn, a)) | dict(zip(pf, b))
                out.add(tuple(val[q] for q in pts))
    return out


def nr_closure(cset, base, eqtype):
    """the closure of base under sign-compatible eliminations (two knots sharing two classes h, s, with forbidden patterns relating
    h and s differently, give the knots on their union minus h and minus s); returns it and the number of compatible conclusions that
    are not knots"""
    gen = set(base)
    misses = 0
    changed = True
    while changed:
        changed = False
        items = list(gen)
        for A, B in itertools.combinations(items, 2):
            sh = A & B
            if bin(sh).count("1") != 2:
                continue
            h, s = BL_bits(sh)
            if eqtype[(A, h, s)] == eqtype[(B, h, s)]:
                continue
            for e in (h, s):
                T = (A | B) & ~(1 << e)
                if T not in cset:
                    misses += 1
                    continue
                if T not in gen:
                    gen.add(T)
                    changed = True
    return gen, misses


def BL_bits(m):
    return [q for q in range(m.bit_length()) if m >> q & 1]


def global_task(seed):
    H, s, n, AN = near_side(seed)
    out = collections.Counter()
    if len(AN) == 0:
        return out
    for l in range(len(H)):
        if len(set(H[l])) < 3 or not GL.six(AN, H[l]):
            continue
        for fname, F in SL.FARS:
            d = SL.closure_data(AN, H, s, n, l, F)
            lines, signs, far, AF = J.far_side(G, H, s, n, l, *F)
            eqtype = {}
            for T in d["cset"]:
                pts = BL_bits(T)
                if len(pts) != 3:
                    continue
                P = join_projection(AN, n, AF, far, list(H[l]), pts)
                miss = [v for v in itertools.product((0, 1), repeat=3) if v not in P]
                v = miss[0]
                for i, j in itertools.combinations(range(3), 2):
                    eqtype[(T, pts[i], pts[j])] = eqtype[(T, pts[j], pts[i])] = (v[i] == v[j])
                out["knots"] += 1
                out["knots missing exactly one complementary pair"] += len(miss) == 2 and miss[0] == tuple(1 - b for b in miss[1])
            gen, misses = nr_closure(d["cset"], d["base"], eqtype)
            crossing = d["cset"] - d["base"]
            out["crossing classes"] += len(crossing)
            out["generated by the closure"] += len(crossing & d["gen"])
            out["generated by sign-compatible eliminations"] += len(crossing & gen)
            out["the two closures agree"] += sum(1 for T in crossing if (T in d["gen"]) == (T in gen))
            out["compatible conclusions that are not knots"] += misses
    return out


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(".json") and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})

    lt = lemma()
    check("1 the elimination lemma: two knots sharing two variables have width-3 resolvents exactly when sign-compatible, and the "
          "resolvents are then the clauses of the knots they imply on the other two triples", lt["MISMATCH"] == 0 and
          lt["compatible"] == lt["incompatible"] == 32, dict(lt))

    only = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None
    with Pool(int(os.environ.get("PROCS", "12"))) as pool:
        if not only or "2" in only:
            tasks = []
            for fname, F in SL.FARS:
                reps, rows = LL.far_classes(F)
                tasks += [(fname, 3, [c]) for c in reps]
                tasks += [(fname, 2, list(p)) for p in itertools.combinations(reps, 2)]
                tasks += [(fname, 1, list(t)) for t in itertools.combinations(reps, 3)]
            total = collections.defaultdict(collections.Counter)
            for args, tot in pool.imap_unordered(local_task, tasks):
                total["%s, %d near classes, %d far" % (args[0], args[1], len(args[2]))].update(tot)
            allc = collections.Counter()
            for c in total.values():
                allc.update(c)
            ok2 = (allc["CNY: reached, but every literal two-round step is sign-incompatible"] == 0
                   and allc["compatible steps whose conclusion is not a knot"] == 0
                   and allc["non-degenerate knots missing other than one class"] == 0
                   and allc["literal compatible steps reaching an unreached knot"] == 0
                   and allc["reached by the two-round rule"] > 0 and allc["control: disagreement with incompatible steps"] > 0)
            check("2 exhaustive local check (every non-degenerate local configuration): every non-degenerate knot misses exactly one "
                  "complementary pair; every sign-compatible step concludes a knot; a knot {c, x, y} reached in round one always has a "
                  "sign-compatible witness (one pair of width-3 resolution steps); for {c, x, w} and {c, c', x} the rule's literal round-two "
                  "steps can all be incompatible (counted here; check 3 finds another width-3 route of depth two); the control that "
                  "demands incompatible steps disagrees (the check can fail)", ok2,
                  {"totals": dict(allc), "by shape": {k: dict(v) for k, v in sorted(total.items())}})

        if not only or "3" in only:
            tasks = []
            for fname, F in SL.FARS:
                reps, rows = LL.far_classes(F)
                tasks += [(fname, 1, [c]) for c in reps]                              # {c, x, y}
                tasks += [(fname, 2, [c]) for c in reps]                              # {c, x, w}
                tasks += [(fname, 1, list(p)) for p in itertools.combinations(reps, 2)]   # {c, c', x}
            wt = collections.Counter()
            for args, tot in pool.imap_unordered(width_task, tasks):
                wt.update(tot)
            ok3 = wt["DISAGREEMENT"] == 0 and not any("NOT implied" in str(k) for k in wt) and \
                not any(k[2] == "least width None" for k in wt if isinstance(k, tuple))
            check("3 widths on small relations: from the one-sided implicates on at most three variables, width-3 resolution derives "
                  "exactly the knots the two-round rule reaches; every crossing knot is implied by those implicates; the least width "
                  "and depth that derive each crossing knot, by shape", ok3, {str(k): v for k, v in sorted(wt.items(), key=str)})

        if not only or "4" in only:
            glo = collections.Counter()
            for c in pool.imap_unordered(global_task, range(600), chunksize=2):
                glo.update(c)
            check("4 whole splices (census and random near sides, every gluing line and far side): the closure under sign-compatible "
                  "eliminations equals the knot closure on every crossing class", glo["crossing classes"] == glo["the two closures agree"]
                  > 0 and glo["compatible conclusions that are not knots"] == 0 and glo["knots"] ==
                  glo["knots missing exactly one complementary pair"], dict(glo))

        if not only or "5" in only:
            rt = collections.Counter()
            tasks = [(fname, c0) for fname, F in SL.FARS for c0 in LL.far_classes(F)[0]]
            for c in pool.imap_unordered(route_task, tasks):
                rt.update(c)
            check("5 the route to {c, x, w} (every near relation on {x, w} and the gluing line, every far class): each reached knot "
                  "{c, x, w} is the resolvent of a compatible round-one knot {c, x, y} and a near knot {x, w, y} on y, so every crossing "
                  "derivation is a linear chain from one far knot through at most two near knots; the literal pairs step is rarely "
                  "compatible, and the near-knot route never reaches an unreached knot", rt["{c, x, w} reached"] ==
                  rt["reached by a compatible round-one knot and a near knot {x, w, y}"] > 0 and
                  rt["near-knot route on an unreached knot"] == 0, dict(rt))

    OUT["seconds"] = round(time.time() - T0, 1)
    print("ALL OK", OUT["seconds"], "s")
    if only:
        sys.exit(0)
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "status": "passed", "claim": manifest["claim"],
              "checks": {k: v for k, v in OUT.items() if k != "seconds"}}
    text = json.dumps(result, indent=1, sort_keys=True, default=str) + "\n"
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(text)
    elif not (HERE / "result.json").exists() or json.loads((HERE / "result.json").read_text()) != json.loads(text):
        print("result.json does not match a fresh run; rerun with --write after review")
        sys.exit(1)
