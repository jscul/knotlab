#!/usr/bin/env python3
"""Checks for TWO-BIT-SCREEN-20261105-001A: hidden points and the two-bit screening lemma.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx, python-sat). Uses up to 22 processes."""
import collections
import hashlib
import importlib.util
import itertools
import json
import random
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import screen_lib as SL  # noqa: E402

GL, CL, E = SL.GL, SL.CL, SL.E
SP = GL.SP
T0 = time.time()
OUT = {}
PERMS = list(itertools.permutations(range(3)))


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str), round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def sat_solutions(lines, signs, n, skip=None):
    """all solutions by SAT model enumeration, as rows in claim_lib.solutions order (ascending code)"""
    import numpy as np
    from pysat.solvers import Solver
    clauses = []
    for i, (L, sg) in enumerate(zip(lines, signs)):
        if i == skip:
            continue
        lit = [(q + 1) if t == 0 else -(q + 1) for q, t in zip(L, sg)]
        clauses += [lit, [-x for x in lit]]
    with Solver(name="cadical153", bootstrap_with=clauses) as s:
        codes = sorted({sum(1 << (abs(v) - 1) for v in m if 0 < v <= n) for m in s.enum_models()})
    codes = np.array(codes, dtype=np.int64)
    if len(codes) == 0:
        return np.zeros((0, n), dtype=np.int8)
    return ((codes[:, None] >> np.arange(n)) & 1).astype(np.int8)


def threefold_census(nmax=22):
    path = ROOT / "proofs/NATIVE-GENUS-20261104-001B/NATIVE-GENUS-20261104-001B-P001_counting_and_locating_handles/check.py"
    spec = importlib.util.spec_from_file_location("ngb_check_for_two_bit", path)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(path.parent))
    spec.loader.exec_module(mod)
    return [(name, S) for name, S, kinds in mod.census() if S.n <= nmax]


def larger_spaces():
    F = GL.FANO
    out = {}
    for k in (4, 5, 6):
        out["prism over a %d-cycle" % (2 * k)] = GL.PL.to_space(GL.PL.prism(k))
    S = GL.attach_point(GL.base(*F), ("g", 0), F, 0, "A")
    out["Fano + Fano atom at a point"] = (S.H, S.s, S.n)
    S = GL.attach_line(GL.base(*F), ("g", 0), F, 0, "A")
    out["Fano + Fano atom at a line"] = (S.H, S.s, S.n)
    S = GL.attach_point(GL.base(*GL.C58), ("g", 0), F, 0, "A")
    out["census 58 + Fano atom at a point"] = (S.H, S.s, S.n)
    S = GL.attach_line(GL.base(*GL.PL.to_space(GL.PL.prism(4))), ("g", 0), F, 0, "A")
    out["prism(4) + Fano atom at a line"] = (S.H, S.s, S.n)
    return out


# ------------------------------------------------------------------------------------------------ 1. the tetrahedron rule
def task_tetra(args):
    H, s, n, M = args
    AN = CL.solutions(H, s, n, skip=M)
    c = collections.Counter()
    for l in range(len(H)):
        if l == M or not GL.six(AN, H[l]):
            continue
        for fname, F in SL.FARS:
            d = SL.closure_data(AN, H, s, n, l, F)
            t = SL.tetra_closure(d["cset"], d["base"])
            c["splices"] += 1
            c["equal"] += t == d["gen"]
            c["classes in the closure"] += len(t)
    return c


# ------------------------------------------------------------------------------------------------ 3. receiving sides
def task_receiver(args):
    bname, Nhat, L0, Qname, Q, p, perm = args
    N = GL.base(*Nhat)
    S = GL.attach_line(N, ("g", L0), Q, p, "R", perm)
    nN, nS = Nhat[2], S.n
    X = list(Nhat[0][L0])
    c = collections.Counter()
    for M in range(len(Nhat[0])):
        if M == L0:
            continue
        AS = CL.solutions(S.H, S.s, S.n, skip=S.line(("g", M)))
        AN = CL.solutions(Nhat[0], Nhat[1], nN, skip=M)
        for l in range(len(Nhat[0])):
            if l in (M, L0):
                continue
            lS = S.line(("g", l))
            if not GL.six(AN, Nhat[0][l]):
                continue
            for fname, F in SL.FARS:
                dS = SL.closure_data(AS, S.H, S.s, nS, lS, F)
                dN = SL.closure_data(AN, Nhat[0], Nhat[1], nN, l, F)
                rep = dS["rep"]
                hidden = {rep[q] for q in range(nN, nS)} - {rep[w] for w in range(dS["n"]) if not nN <= w < nS}
                wpt = {}
                for w in range(dS["n"]):
                    if not nN <= w < nS and rep[w] not in wpt:
                        wpt[rep[w]] = w
                # a class of S holding a point off the side, as a class of the closed space
                toN = lambda r: dN["rep"][wpt[r] if wpt[r] < nN else wpt[r] - nS + nN]  # noqa: E731
                c["cases"] += 1
                # (i) W-classes keep their status: compare the new knots off the hidden points
                newS_W = sorted(sum(1 << toN(q) for q in SL.bits(m)) for m in dS["new"] if not any(q in hidden for q in SL.bits(m)))
                newN = sorted(dN["new"])
                c["new knots off the side equal"] += newS_W == newN
                c["creation equal"] += bool(dS["new"]) == bool(dN["new"])
                c["closed space creates"] += bool(dN["new"])
                for T in dS["cset"]:
                    hid = [q for q in SL.bits(T) if q in hidden]
                    if not hid:
                        continue
                    if T in dS["base"]:
                        continue
                    if len(hid) >= 2:
                        c["crossing classes through two hidden classes"] += 1
                        continue
                    rest = [toN(q) for q in SL.bits(T) if q not in hidden]
                    restc = {dN["rep"][q] for q in rest}
                    shadows = []
                    for x in X:
                        if dN["rep"][x] in restc:
                            continue
                        m = E.canon(sum(1 << q for q in rest) | (1 << x), dN["rep"])
                        if bin(m).count("1") == 3 and m in dN["cset"]:
                            shadows.append(m in dN["gen"])
                    gen = T in dS["gen"]
                    c["crossing knots through one hidden class"] += 1
                    c["... with at least one port shadow"] += bool(shadows)
                    if gen:
                        c["... generated"] += 1
                        c["...... with every shadow generated"] += all(shadows)
                    else:
                        c["... new"] += 1
                        c["...... with every shadow new"] += not any(shadows)
    return (bname, Qname), c


# ------------------------------------------------------------------------------------------------ 4. pendant lines
def task_pendant(args):
    kind, H, s, n, M, s_, u_, sig, ls_, fars = args
    AN = CL.solutions(H, s, n, skip=M) if M is not None else CL.solutions(H, s, n)
    c = collections.Counter()
    if len(AN) == 0:
        return kind, c
    AP = SL.pendant(AN, s_, u_, sig)
    for l in (ls_ if ls_ is not None else range(len(H))):
        if l == M or len(set(H[l])) < 3 or not GL.six(AN, H[l]):
            continue
        for fname, F in SL.FARS[:fars]:
            eqW, eqC, nc, sc, thr = SL.compare_hidden(AN, AP, H, s, n, 1, l, F)
            c["cases"] += 1
            c["new knots off the point equal"] += eqW
            c["creation equal"] += eqC
            c["closed side creates"] += nc
            c["new knots through the point"] += thr
    return kind, c


def pendant_tasks():
    tasks = []
    for bname in (58, 21, 38, 6):
        H, s, n = SP[bname]
        for M in range(len(H)):
            for s_, u_ in itertools.combinations(range(n), 2):
                for sig in itertools.product((0, 1), repeat=3):
                    if sig[0] == 0:
                        tasks.append(("census near sides (every pendant line)", H, s, n, M, s_, u_, sig, None, 4))
    rnd = random.Random(7)
    for name, (H, s, n) in larger_spaces().items():
        pairs = list(itertools.combinations(range(n), 2))
        for i in range(40):
            s_, u_ = rnd.choice(pairs)
            sig = (0, rnd.randint(0, 1), rnd.randint(0, 1))
            Ms = rnd.sample(range(len(H)), min(5, len(H)))
            for M in Ms:
                AN = CL.solutions(H, s, n, skip=M)
                lines = [l for l in range(len(H)) if l != M and GL.six(AN, H[l])]
                tasks.append(("larger near sides (sampled)", H, s, n, M, s_, u_, sig, rnd.sample(lines, min(6, len(lines))), 2))
    for seed in range(1500):
        r = random.Random(seed)
        n = r.randint(7, 10)
        m = r.randint(n - 2, n + 3)
        H = [tuple(r.sample(range(n), 3)) for _ in range(m)]
        s = [[r.randint(0, 1) for _ in range(3)] for _ in range(m)]
        for _ in range(2):
            s_, u_ = r.sample(range(n), 2)
            tasks.append(("random near sides", H, s, n, None, s_, u_, (0, r.randint(0, 1), r.randint(0, 1)), None, 4))
    return tasks


# ------------------------------------------------------------------------------------------------ 5. gadgets that encode
def task_profile(args):
    bname, L0, prof = args
    H, s, n = SP[bname]
    R, P = SL.profile_gadget(tuple(s[L0]), prof)
    X = list(H[L0])
    c = collections.Counter()
    for M in range(len(H)):
        if M == L0:
            continue
        AN = CL.solutions(H, s, n, skip=M)
        AS = SL.extend(AN, X, R)
        for l in range(len(H)):
            if l in (M, L0) or not GL.six(AN, H[l]):
                continue
            for fname, F in SL.FARS:
                eqW, eqC, nc, sc, thr = SL.compare_hidden(AN, AS, H, s, n, 1, l, F)
                c["cases"] += 1
                c["new knots off the point equal"] += eqW
                c["creation equal"] += eqC
    excl = [{x for x in P if (v,) not in R[x]} for v in (0, 1)]
    return prof, all(SL.subcube(S, P) for S in excl), c


def task_two_point(args):
    bname, L0, idx = args
    H, s, n = SP[bname]
    G, P = SL.two_point_gadgets(tuple(s[L0]))
    R = G[idx]
    X = list(H[L0])
    c = collections.Counter()
    for M in range(len(H)):
        if M == L0:
            continue
        AN = CL.solutions(H, s, n, skip=M)
        AS = SL.extend(AN, X, R)
        for l in range(len(H)):
            if l in (M, L0) or not GL.six(AN, H[l]):
                continue
            for fname, F in SL.FARS:
                eqW, eqC, nc, sc, thr = SL.compare_hidden(AN, AS, H, s, n, 2, l, F)
                c["cases"] += 1
                c["new knots off the points equal"] += eqW
                c["creation equal"] += eqC
    return (bname, L0, idx), SL.pair_types(R, P), c


# ------------------------------------------------------------------------------------------------ 6. what lifting is not
def task_local_fano(args):
    Nhat, L0, Q, p, perm = args
    N = GL.base(*Nhat)
    S = GL.attach_line(N, ("g", L0), Q, p, "R", perm)
    nN, nS = Nhat[2], S.n
    X = list(Nhat[0][L0])
    c = collections.Counter()
    for M in range(len(Nhat[0])):
        if M == L0:
            continue
        AS = CL.solutions(S.H, S.s, S.n, skip=S.line(("g", M)))
        for l in range(len(Nhat[0])):
            if l in (M, L0):
                continue
            lS = S.line(("g", l))
            if not GL.six(AS, S.H[lS]):
                continue
            for fname, F in SL.FARS:
                d = SL.closure_data(AS, S.H, S.s, nS, lS, F)
                rep = d["rep"]
                hidden = {rep[q] for q in range(nN, nS)} - {rep[w] for w in range(nS + F[2] - 1) if not nN <= w < nS}
                crossB = {T for T in d["cset"] if T not in d["base"] and any(q in hidden for q in SL.bits(T))}
                seed = d["cset"] - crossB
                Xc = {rep[x] for x in X}
                Yc = {rep[y] for y in Nhat[0][l]}
                for T in crossB:
                    lc = SL.local_closure(set(SL.bits(T)) | Xc | Yc, d["cset"], seed)
                    st = "generated" if T in d["gen"] else "new"
                    c[(st, "derived inside the knot, the ports and the gluing line" if T in lc else "not derived there")] += 1
    return c


def task_global(args):
    kind, H, s, n, M, s_, u_, sig = args
    AN = CL.solutions(H, s, n, skip=M) if M is not None else CL.solutions(H, s, n)
    c = collections.Counter()
    if len(AN) == 0:
        return c
    AP = SL.pendant(AN, s_, u_, sig)
    b = n
    for l in range(len(H)):
        if l == M or len(set(H[l])) < 3 or not GL.six(AN, H[l]):
            continue
        for fname, F in SL.FARS:
            d = SL.closure_data(AP, H, s, n + 1, l, F)
            rep = d["rep"]
            if rep[b] != b:
                continue
            farc = {rep[q] for q in d["far"]}
            hasfar = lambda T: any(q in farc for q in SL.bits(T))  # noqa: E731
            seed = {T for T in d["cset"] if not (T >> b & 1) or not hasfar(T)} | d["base"]
            g = E.closure(set(d["cset"]), seed, d["n"])
            miss = [T for T in d["cset"] if (T >> b & 1) and hasfar(T) and T not in g]
            if miss:
                newN = SL.new_knots(AN, H, s, n, l, F)
                c[(kind, "missed even with every other knot seeded")] += len(miss)
                c[(kind, "... where the side without the point creates")] += len(miss) if newN else 0
            c[(kind, "crossing knots through the point")] += sum(1 for T in d["cset"] if (T >> b & 1) and hasfar(T))
    return c


def task_twin(args):
    kind, H, s, n, M = args
    AN = CL.solutions(H, s, n, skip=M) if M is not None else CL.solutions(H, s, n)
    c = collections.Counter()
    if len(AN) == 0:
        return c
    import numpy as np
    for l in range(len(H)):
        if l == M or len(set(H[l])) < 3 or not GL.six(AN, H[l]):
            continue
        F = SL.FARS[0][1]
        d = SL.closure_data(AN, H, s, n, l, F)
        lines, signs, far, AF = SL.J.far_side(SL.G, H, s, n, l, *F)
        Xl = list(H[l])
        by = collections.defaultdict(list)
        for r in AF:
            by[tuple(int(v) for v in r[len(far):])].append([int(v) for v in r[:len(far)]])
        TS = np.array([[int(v) for v in r] + fr for r in AN for fr in by.get(tuple(int(r[x]) for x in Xl), [])], dtype=np.int8)
        rep = d["rep"]
        reps = sorted(set(rep[q] for q in range(TS.shape[1])))
        status = {d["can"][k]: ("generated" if d["can"][k] in d["gen"] else "new") for k in d["knots"] if d["can"][k] not in d["base"]}
        for p, q in itertools.combinations(reps, 2):
            for vp, vq in itertools.product((0, 1), repeat=2):
                sel = (TS[:, p] == vp) & (TS[:, q] == vq)
                if not sel.any():
                    continue
                forced = [z for z in reps if z not in (p, q) and len(np.unique(TS[sel, z])) == 1]
                for a, b in itertools.combinations(forced, 2):
                    Fa, Fb = (1 << p) | (1 << q) | (1 << a), (1 << p) | (1 << q) | (1 << b)
                    if Fa in status and Fb in status:
                        c["twin pairs"] += 1
                        c["... with different statuses"] += status[Fa] != status[Fb]
    return c


# ------------------------------------------------------------------------------------------------ 7. the gluing line suffices
def task_yloc(args):
    H, s, n, M, pend = args
    AN = CL.solutions(H, s, n, skip=M)
    near = n
    if pend is not None:
        AN = SL.pendant(AN, *pend)
        near = n + 1
    c = collections.Counter()
    for l in range(len(H)):
        if l == M or not GL.six(AN, H[l]):
            continue
        for fname, F in SL.FARS:
            d = SL.closure_data(AN, H, s, near, l, F)
            Yc = sorted({d["rep"][y] for y in H[l]})
            r = SL.restricted_closure(d["cset"], d["base"], d["n"], Yc)
            crossing = d["cset"] - d["base"]
            c["crossing classes"] += len(crossing)
            c["generated"] += len(crossing & d["gen"])
            c["generated through the gluing line alone"] += len(crossing & r)
    return c


# ------------------------------------------------------------------------------------------------ 8. profiles of knot-space sides
def task_gadget_profile(args):
    name, H, s, n, p = args
    through = [i for i, m in enumerate(H) if p in m]
    lines = [tuple((n + through.index(i)) if q == p else q for q in m) for i, m in enumerate(H)]
    A = sat_solutions(lines, s, n + 3)
    rows = [tuple(int(x) for x in r) for r in A]
    ports = [n, n + 1, n + 2]
    c = collections.Counter()
    for b in range(n):
        if b == p:
            continue
        P, ex = SL.exclusions(rows, ports, [b])
        if len(P) != 6:
            c["sides not showing six patterns"] += 1
            continue
        for v, S in ex.items():
            c[SL.exclusion_type(S, P)] += 1
    return name, c


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(".json") and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})

    with Pool(22) as pool:
        # 1
        tasks = [(*SP[b], M) for b in SP for M in range(len(SP[b][0]))]
        tot = collections.Counter()
        for c in pool.imap_unordered(task_tetra, tasks):
            tot.update(c)
        check("1 the closure behind creation is the tetrahedron rule: on every census near side, removal, gluing line and far side, the "
              "elimination closure equals the least set of class triples, containing the non-crossing knots, in which every four classes "
              "with two triples in the set have all their knot triples in it", tot["splices"] == tot["equal"] > 0, dict(tot))

        # 2
        F = GL.FANO
        info2, ok2 = {}, True
        types2 = collections.Counter()
        for p in range(7):
            rows, ports, interior = SL.gadget(F, p)
            P = sorted({tuple(r[q] for q in ports) for r in rows})
            ok2 &= len(P) == 6 and all(len(set(x)) == 2 for x in P)
            through = [i for i, m in enumerate(F[0]) if p in m]
            for b in interior:
                port = next(t for t, i in enumerate(through) if b in F[0][i])
                P_, ex = SL.exclusions(rows, ports, [b])
                e0, e1 = ex[(0,)], ex[(1,)]
                one = len(e0) == 1 and len(e1) == 1
                x0 = next(iter(e0)) if one else None
                comp = one and next(iter(e1)) == tuple(1 - t for t in x0)
                odd = one and [i for i in range(3) if x0[i] != x0[(i + 1) % 3] and x0[i] != x0[(i + 2) % 3]] == [port]
                majority = one and x0[(port + 1) % 3] == 1  # value 0 is excluded where the majority is 1
                ok2 &= one and comp and odd and majority
            for b1, b2 in itertools.combinations(interior, 2):
                P_, ex = SL.exclusions(rows, ports, [b1, b2])
                same_cut = any(b1 in F[0][i] and b2 in F[0][i] for i in through)
                for v, S in ex.items():
                    t = SL.exclusion_type(S, P)
                    types2[(t, "points on one cut line" if same_cut else "other pairs")] += 1
                    if t.startswith("other") or (t == "antipodal class" and not same_cut):
                        ok2 = False
        info2["pair exclusion types (value pairs)"] = {"%s, %s" % k: v for k, v in sorted(types2.items())}
        check("2 the Fano side (exhaustive, all seven split points): it shows the six non-constant port patterns; each hidden point is "
              "forced exactly on the two patterns whose odd port lies on its cut line, to their majority, and is free on the other four; "
              "each value pair of two hidden points excludes a subcube of the patterns, or (only for the two points of one cut line) "
              "that line's antipodal class, or nothing", ok2, info2)

        # 3
        tasks = []
        for bname in SP:
            Nhat = SP[bname]
            for L0 in range(len(Nhat[0])):
                for perm in PERMS:
                    tasks.append((bname, Nhat, L0, "Fano", F, 0, perm))
        for name, Nhat in larger_spaces().items():
            if Nhat[2] > 14:
                continue
            for L0 in range(0, len(Nhat[0]), 3):
                tasks.append((name, Nhat, L0, "Fano", F, 0, (0, 1, 2)))
        for bname in (58, 21, 38):
            Nhat = SP[bname]
            for Qn in (58, 14, 38):
                for L0 in (0, 2):
                    for p in (0, 3):
                        tasks.append((bname, Nhat, L0, "census %d" % Qn, SP[Qn], p, (0, 1, 2)))
        fano, other = collections.Counter(), collections.Counter()
        for (bname, Qname), c in pool.imap_unordered(task_receiver, tasks):
            (fano if Qname == "Fano" else other).update(c)
        ok3 = (fano["cases"] == fano["new knots off the side equal"] and fano["crossing classes through two hidden classes"] == 0
               and fano["... generated"] == fano["...... with every shadow generated"])
        check("3 the no-loss theorem for Fano sides, checked on every census near side at every line and port permutation and on larger "
              "near sides: the new knots off the side are those of the closed space; every generated crossing knot through a hidden class "
              "has all its port shadows generated; no crossing class meets two hidden classes", ok3, dict(fano))
        ok3b = fano["cases"] == fano["creation equal"] and fano["... new"] == fano["...... with every shadow new"]
        check("3b the lifting half for Fano sides (computed, not proved): creation is unchanged in every case, and every new crossing knot "
              "through a hidden class has all its port shadows new", ok3b,
              {"cases": fano["cases"], "creation equal": fano["creation equal"], "new through a hidden class": fano["... new"],
               "with every shadow new": fano["...... with every shadow new"]})
        check("3c other receiving sides (census 58, 14 and 38 split at a point; computed): the new knots off the side and creation are "
              "unchanged", other["cases"] == other["new knots off the side equal"] == other["creation equal"], dict(other))

        # 4
        tot = collections.defaultdict(collections.Counter)
        for kind, c in pool.imap_unordered(task_pendant, pendant_tasks(), chunksize=4):
            tot[kind].update(c)
        ok4 = all(c["cases"] == c["new knots off the point equal"] for c in tot.values())
        ok4b = all(c["cases"] == c["creation equal"] for c in tot.values())
        check("4 pendant lines (one new point on one new line through two near points, any signs): the new knots off the point never "
              "change (proved, the same closure argument), and creation never changes (computed)", ok4 and ok4b,
              {k: dict(v) for k, v in tot.items()})

        # 5
        profiles = list(itertools.product(("free", "majority", "minority"), repeat=3))
        tasks = [(b, L0, prof) for b in (58, 21, 38, 45) for L0 in (0, 3) for prof in profiles]
        per = collections.defaultdict(collections.Counter)
        cube = {}
        for prof, is_cube, c in pool.imap_unordered(task_profile, tasks):
            per[prof].update(c)
            cube[prof] = is_cube
        changes = {prof: per[prof]["cases"] - per[prof]["creation equal"] for prof in profiles}
        offW = {prof: per[prof]["cases"] - per[prof]["new knots off the point equal"] for prof in profiles}
        ok5 = all((changes[pr] > 0) == (not cube[pr]) for pr in profiles) and not any(offW.values())
        check("5 one hidden point on a line's three points, all 27 profiles (free, majority or minority on each antipodal class), on four "
              "bases at two lines: creation changes exactly for the 8 profiles whose exclusion sets are not subcubes (a majority or "
              "minority of the ports, or a copy of one port that is free on that port's own class); the new knots off the point never "
              "change", ok5, {"creation changes (cases), by profile": {"/".join(pr): changes[pr] for pr in profiles},
                              "profiles with subcube exclusions": sum(cube.values())})
        tasks = []
        for b in (58, 38):
            G2, P2 = SL.two_point_gadgets(tuple(SP[b][1][0]))
            tasks += [(b, 0, i) for i in range(len(G2))]
        fails = collections.Counter()
        cond = collections.Counter()
        offW2 = 0
        for key, types, c in pool.imap_unordered(task_two_point, tasks, chunksize=2):
            fail = c["cases"] != c["creation equal"]
            offW2 += c["cases"] - c["new knots off the points equal"]
            fails[(key[0], fail)] += 1
            cond[("pairs exclude only subcubes or antipodal classes" if all(t != "other" for t in types) else "some pair excludes "
                  "other sets", "changes creation" if fail else "keeps creation")] += 1
        ok5b = cond[("pairs exclude only subcubes or antipodal classes", "changes creation")] == 0 and offW2 == 0
        check("5b two hidden points whose single points have subcube exclusions, up to symmetry, on census 58 and census 38: some still "
              "change creation, but none whose value pairs exclude only subcubes or antipodal classes (the Fano side's kinds); the new "
              "knots off the points never change", ok5b,
              {"gadgets (base, changes creation)": {"census %d, %s" % (k[0], "changes" if k[1] else "keeps"): v for k, v in sorted(fails.items())},
               "by pair condition": {"%s: %s" % k: v for k, v in sorted(cond.items())}})

        # 6
        tasks = [(SP[b], L0, F, 0, perm) for b in (58, 21, 38, 45, 56) for L0 in (0, 2) for perm in ((0, 1, 2), (1, 0, 2))]
        loc = collections.Counter()
        for c in pool.imap_unordered(task_local_fano, tasks):
            loc.update(c)
        nd = loc[("new", "not derived there")]
        ok6 = loc[("generated", "not derived there")] == 0 and nd > 0
        check("6 lifting is not local: every generated crossing knot through a hidden Fano point is derived inside the knot, the ports and "
              "the gluing line; but some new ones are not derived there even when every other knot there is seeded", ok6,
              {"%s, %s" % k: v for k, v in sorted(loc.items())})
        tasks = []
        rnd = random.Random(11)
        for i in range(300):
            if i % 2:
                b = rnd.choice([58, 38, 21, 45, 56])
                H, s, n = SP[b]
                M = rnd.randrange(len(H))
                kind = "census near sides"
            else:
                n = rnd.randint(7, 10)
                m = rnd.randint(n - 2, n + 3)
                H = [tuple(rnd.sample(range(n), 3)) for _ in range(m)]
                s = [[rnd.randint(0, 1) for _ in range(3)] for _ in range(m)]
                M, kind = None, "random near sides"
            for _ in range(3):
                s_, u_ = rnd.sample(range(n), 2)
                tasks.append((kind, H, s, n, M, s_, u_, (0, rnd.randint(0, 1), rnd.randint(0, 1))))
        glo = collections.Counter()
        for c in pool.imap_unordered(task_global, tasks, chunksize=2):
            glo.update(c)
        misses = sum(v for k, v in glo.items() if k[1] == "missed even with every other knot seeded")
        where = sum(v for k, v in glo.items() if k[1] == "... where the side without the point creates")
        check("6b lifting is not a consequence of the knots alone: with every knot off a pendant point, and every knot through it without a "
              "far point, seeded, the closure still misses some crossing knots through the point; every such miss occurs where the side "
              "without the point creates", misses > 0 and misses == where, {"%s: %s" % k: v for k, v in sorted(glo.items())})
        tasks = [("census", *SP[b], M) for b in (58, 38, 21, 45, 56) for M in range(len(SP[b][0]))]
        rnd = random.Random(5)
        for i in range(200):
            n = rnd.randint(7, 10)
            m = rnd.randint(n - 2, n + 3)
            H = [tuple(rnd.sample(range(n), 3)) for _ in range(m)]
            s = [[rnd.randint(0, 1) for _ in range(3)] for _ in range(m)]
            tasks.append(("random", H, s, n, None))
        tw = collections.Counter()
        for c in pool.imap_unordered(task_twin, tasks, chunksize=2):
            tw.update(c)
        check("6c the twin statement is false: when one assignment to two classes forces two others, the two knots it makes need not "
              "share their status (so lifting must use more than the shadows' membership)", tw["... with different statuses"] > 0, dict(tw))

        # 7
        tasks = [(*SP[b], M, None) for b in (58, 38, 21, 45, 56, 6) for M in range(len(SP[b][0]))]
        tasks += [(*SP[b], M, (s_, u_, (0, 0, 1))) for b in (58, 38) for M in (0, 3) for s_, u_ in list(itertools.combinations(range(8), 2))[::4]]
        yl = collections.Counter()
        for c in pool.imap_unordered(task_yloc, tasks):
            yl.update(c)
        check("7 the gluing line suffices (computed): eliminating only through classes of the gluing line's points generates every "
              "crossing class the full closure generates", yl["generated"] == yl["generated through the gluing line alone"] > 0, dict(yl))

        # 8
        tasks = []
        for i, Q in SP.items():
            for p in range(Q[2]):
                tasks.append(("census %d" % i, Q[0], Q[1], Q[2], p))
        for k in (3, 4, 5):
            H, s, n = GL.PL.to_space(GL.PL.prism(k))
            for p in range(n):
                tasks.append(("prism over a %d-cycle" % (2 * k), H, s, n, p))
        for name, S in threefold_census(22):
            for p in range(S.n):
                tasks.append(("three-fold spaces up to 22 points", S.H, S.s, S.n, p))
        prof8 = collections.defaultdict(collections.Counter)
        for name, c in pool.imap_unordered(task_gadget_profile, tasks, chunksize=4):
            prof8[name].update(c)
        bad8 = {k: dict(v) for k, v in prof8.items() if any(t.startswith("other") or t == "antipodal class" for t in v)}
        check("8 every knot space tried, split at any point (the census, prisms, and every three-fold space up to 22 points), shows the "
              "six patterns and gives every hidden point subcube exclusion sets: none encodes a majority or a parity of its ports",
              not bad8 and all(v.get("sides not showing six patterns", 0) == 0 for v in prof8.values()),
              {k: dict(v) for k, v in sorted(prof8.items())})

    OUT["seconds"] = round(time.time() - T0, 1)
    print("ALL OK", OUT["seconds"], "s")
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "status": "passed", "claim": manifest["claim"],
              "checks": {k: v for k, v in OUT.items() if k != "seconds"}}
    text = json.dumps(result, indent=1, sort_keys=True, default=str) + "\n"
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(text)
    elif not (HERE / "result.json").exists() or json.loads((HERE / "result.json").read_text()) != json.loads(text):
        print("result.json does not match a fresh run; rerun with --write after review")
        sys.exit(1)
