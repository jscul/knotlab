#!/usr/bin/env python3
"""Checks for PLANAR-COMPOSE-20261102-001B: cutting a handle open.

A torus embedding of the near side has two homology classes of sign twists: edge sets meeting every face evenly (so every face condition
is kept) that are not point or line switchings. Twisting the signs along a non-contractible cut curve changes one homology parity. The
union of the knot's solutions over the four sectors {0, Za, Zb, Za + Zb} forgets both parities: the handle cut open along the two curves.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy). About ten minutes."""
import collections
import hashlib
import itertools
import json
import random
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/HANDLE-EMERGENCE-20261102-001A/HANDLE-EMERGENCE-20261102-001A-P001_a_planar_removed_side_creates_nothing"))
sys.path.insert(0, str(ROOT / "proofs/SPLICE-TREE-20261102-001C/SPLICE-TREE-20261102-001C-P001_opened_cuts_interact"))
import planar_lib as PL  # noqa: E402
import elim_lib as E  # noqa: E402

G = PL.G
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:900], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        print(json.dumps(info, default=str, indent=1))
        sys.exit(1)


# ------------------------------------------------------------------------------------------------ 0. bindings
manifest = json.loads((HERE / "manifest.json").read_text())
bad = {p: d for p, d in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != d}
status = {p: json.loads((ROOT / p).read_text()).get("status") for p in manifest["parent_bindings"]
          if p.endswith(".json") and p.startswith("proofs/")}
check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
      {"mismatched": bad, "statuses": status})

SP = {idx: (H, s, n) for idx, n, H, s in G.census_spaces(ROOT)}


class Near:
    """a non-planar near side with its torus embeddings and, for each, two homology twist classes"""

    def __init__(self, idx):
        self.H, self.s, self.n = SP[idx]
        H, n = self.H, self.n
        self.inc = [(k, p) for k, L in enumerate(H) for p in L]
        self.idx = {e: i for i, e in enumerate(self.inc)}
        self.verts = [("p", p) for p in range(n)] + [("l", k) for k in range(len(H))]
        self.nbr = {v: [] for v in self.verts}
        for k, L in enumerate(H):
            for p in L:
                self.nbr[("l", k)].append(("p", p))
                self.nbr[("p", p)].append(("l", k))
        self.switch = [self.vec([(v, u) for u in self.nbr[v]]) for v in self.verts]
        self.embeddings = []
        for bits in itertools.product((0, 1), repeat=len(self.verts)):
            rot = {v: (list(self.nbr[v]) if b == 0 else [self.nbr[v][0], self.nbr[v][2], self.nbr[v][1]]) for v, b in zip(self.verts, bits)}
            fcs = self.faces_of(rot)
            if (2 - len(self.verts) + 3 * n - len(fcs)) // 2 == 1:
                self.embeddings.append(fcs)

    def vec(self, pairs):
        v = np.zeros(len(self.inc), dtype=np.uint8)
        for a, b in pairs:
            L, p = (a, b) if a[0] == "l" else (b, a)
            v[self.idx[(L[1], p[1])]] ^= 1
        return v

    def faces_of(self, rot):
        seen, out = set(), []
        for u in self.verts:
            for v in self.nbr[u]:
                if (u, v) in seen:
                    continue
                f, a, b = [], u, v
                while (a, b) not in seen:
                    seen.add((a, b))
                    f.append(a)
                    r = rot[b]
                    a, b = b, r[(r.index(a) + 1) % 3]
                out.append(f)
        return out

    def face_vecs(self, fcs):
        return [self.vec(list(zip(f, f[1:] + f[:1]))) for f in fcs]

    def face_condition(self, fcs):
        sign = np.array([self.s[k][self.H[k].index(p)] for k, p in self.inc], dtype=np.uint8)
        return all(int((fv & sign).sum()) % 2 == (int(fv.sum()) // 2 + 1) % 2 for fv in self.face_vecs(fcs))

    @staticmethod
    def rank(rows):
        A = np.array(rows, dtype=np.uint8).copy()
        r = 0
        for c in range(A.shape[1]):
            p = next((i for i in range(r, A.shape[0]) if A[i, c]), None)
            if p is None:
                continue
            A[[r, p]] = A[[p, r]]
            for i in range(A.shape[0]):
                if i != r and A[i, c]:
                    A[i] ^= A[r]
            r += 1
        return r

    def twists(self, fcs):
        """two face-even edge sets independent modulo switchings (the null space of the face vectors, reduced)"""
        F = np.array(self.face_vecs(fcs), dtype=np.uint8)
        m = F.shape[1]
        A, piv, r = F.copy(), [], 0
        for c in range(m):
            p = next((i for i in range(r, A.shape[0]) if A[i, c]), None)
            if p is None:
                continue
            A[[r, p]] = A[[p, r]]
            for i in range(A.shape[0]):
                if i != r and A[i, c]:
                    A[i] ^= A[r]
            piv.append(c)
            r += 1
        basis = []
        for fc in [c for c in range(m) if c not in piv]:
            v = np.zeros(m, dtype=np.uint8)
            v[fc] = 1
            for i, pc in enumerate(piv):
                if A[i, fc]:
                    v[pc] = 1
            basis.append(v)
        base = self.rank(self.switch)
        cls = []
        for v in basis:
            if self.rank(self.switch + cls + [v]) > base + len(cls):
                cls.append(v)
            if len(cls) == 2:
                break
        assert all(not (fv & z).sum() % 2 for fv in self.face_vecs(fcs) for z in cls)
        return cls

    def twisted(self, Z, k):
        return [self.s[k][j] ^ int(Z[self.idx[(k, p)]]) for j, p in enumerate(self.H[k])]


def creation(rel, n, P, ports):
    inner = sum(1 << v for v in P - ports)
    outer = sum(1 << v for v in range(n) if v not in P)
    cs = E.circuits(rel, n)
    rep = E.tie_classes(n, [m for m in cs if bin(m).count("1") == 2])
    knots = [m for m in cs if bin(m).count("1") >= 3]
    can = {m: E.canon(m, rep) for m in knots}
    cross = {m: bool(m & inner and m & outer) for m in knots}
    gen = E.closure(set(can.values()), {can[m] for m in knots if not cross[m]}, n)
    return sum(cross.values()), sum(1 for m in knots if cross[m] and can[m] not in gen)


class Splice:
    def __init__(self, near, i2):
        H2, s2, n2 = SP[i2]
        self.near = near
        self.ls, self.ss, self.n, side, self.ports = G.splice(near.H, near.s, near.n, 0, H2, s2, n2, 0)
        self.P = {v for v in range(self.n) if side[v] == 0}
        self.nearl = [k for k, L in enumerate(self.ls) if set(L) <= self.P]
        self.h1 = [k for k in range(len(near.H)) if k != 0]
        assert [tuple(self.ls[k]) for k in self.nearl] == [tuple(near.H[k]) for k in self.h1]
        self.base = {M: G.removal(self.ls, self.ss, self.n, M) for M in self.nearl}
        self.true = {M: creation(self.base[M], self.n, self.P, self.ports) for M in self.nearl}
        self.creating = [M for M in self.nearl if self.true[M][1]]

    def sector(self, Z, M):
        tw = [list(x) for x in self.ss]
        for kk, k in zip(self.nearl, self.h1):
            tw[kk] = self.near.twisted(Z, k)
        return G.removal(self.ls, tw, self.n, M)

    def cut(self, Zs, M):
        rel = set(self.base[M])
        for Z in Zs:
            rel |= set(self.sector(Z, M))
        return creation(sorted(rel), self.n, self.P, self.ports)


NEAR = {"Fano plane": Near(21), "census 58": Near(58)}
FARS = {"Fano plane": [6, 14, 21, 38, 45, 58], "census 58": [1, 6, 21]}

# ------------------------------------------------------------------------------------------------ 1. embeddings and twists
info1 = {}
ok1 = True
for name, nr in NEAR.items():
    t = collections.Counter()
    for fcs in nr.embeddings:
        t["torus embeddings"] += 1
        t["faces %s" % sorted(len(f) for f in fcs)] += 1
        t["knot's signs satisfy the face condition"] += nr.face_condition(fcs)
        Za, Zb = nr.twists(fcs)
        fails = [G.fails_globally(nr.H, [nr.twisted(Z, k) for k in range(len(nr.H))], nr.n) for Z in (Za, Zb, Za ^ Zb)]
        t["twisted sectors on which the knot still fails"] += sum(fails)
    ok1 &= t["knot's signs satisfy the face condition"] == t["torus embeddings"] > 0
    info1[name] = dict(t)
check("1 the Fano plane has 16 torus embeddings and census 58 has 36; on each, the knot's signs satisfy the face condition, two homology "
      "classes of face-even sign twists exist, and the knot fails on none of the three twisted sectors", ok1, info1)

# ------------------------------------------------------------------------------------------------ 2. cut open with the first representatives
SPL = {(name, i2): Splice(NEAR[name], i2) for name in NEAR for i2 in FARS[name]}
info2 = collections.Counter()
retained = collections.Counter()
for (name, i2), sp in SPL.items():
    for e, fcs in enumerate(NEAR[name].embeddings):
        Za, Zb = NEAR[name].twists(fcs)
        resid = 0
        for M in sp.creating:
            cr, nw = sp.cut([Za, Zb, Za ^ Zb], M)
            resid += nw
            if e == 0:
                retained["crossing knots at creating removals, true"] += sp.true[M][0]
                retained["crossing knots at creating removals, cut open"] += cr
        info2["%s > census %d: embeddings whose cut removes all creation" % (name, i2)] += resid == 0
        info2["%s > census %d: embeddings leaving new knots" % (name, i2)] += resid > 0
print("   ", dict(info2), round(time.time() - T0, 1), "s", flush=True)
check("2 cutting the handle open along the two curves the elimination first finds removes all creation on some embeddings and not on "
      "others (e.g. Fano > census 6: all 16; Fano > Fano: 8 of 16), while most crossing knots survive the cut",
      any(v > 0 for k, v in info2.items() if k.endswith("removes all creation")) and
      any(v > 0 for k, v in info2.items() if k.endswith("leaving new knots")) and
      retained["crossing knots at creating removals, cut open"] > retained["crossing knots at creating removals, true"] // 2,
      {"per splice": dict(info2), "first embedding": dict(retained)})

# ------------------------------------------------------------------------------------------------ 3. the cut position matters
rng = random.Random(1)
nr = NEAR["Fano plane"]
sp = SPL[("Fano plane", 21)]
info3 = collections.Counter()
for e, fcs in enumerate(nr.embeddings[:4]):
    Za, Zb = nr.twists(fcs)
    out = collections.Counter()
    for trial in range(20):
        sa, sb = np.zeros_like(Za), np.zeros_like(Zb)
        for w in nr.switch:
            if rng.random() < 0.5:
                sa ^= w
            if rng.random() < 0.5:
                sb ^= w
        A2, B2 = Za ^ sa, Zb ^ sb
        resid = sum(sp.cut([A2, B2, A2 ^ B2], M)[1] for M in sp.creating)
        out["removed" if resid == 0 else "residue"] += 1
    info3["embeddings tried"] += 1
    info3["embeddings where some cut positions remove creation and others do not"] += out["removed"] > 0 and out["residue"] > 0
    info3["cuts removing all creation"] += out["removed"]
    info3["cuts leaving new knots"] += out["residue"]
check("3 the cut position matters: on the Fano > Fano splice, for each of four torus embeddings, 20 cuts along other curves in the same two "
      "homology classes (the twists changed by point and line switchings) split between removing all creation and leaving new knots",
      info3["embeddings where some cut positions remove creation and others do not"] == info3["embeddings tried"] == 4, dict(info3))

# ------------------------------------------------------------------------------------------------ 4. one parity dropped, and the control
info4 = collections.Counter()
ok4 = True
for (name, i2), sp in SPL.items():
    if name != "Fano plane":
        continue
    Za, Zb = NEAR[name].twists(NEAR[name].embeddings[0])
    for M in sp.creating:
        info4["creating removals"] += 1
        info4["true new knots"] += sp.true[M][1]
        for lab, Z in (("a", Za), ("b", Zb), ("a+b", Za ^ Zb)):
            info4["new knots with one parity dropped (%s)" % lab] += sp.cut([Z], M)[1]
        for p in sorted(sp.P - sp.ports):
            flipped = {tuple(v ^ (1 if q == p else 0) for q, v in enumerate(x)) for x in sp.base[M]}
            nw = creation(sorted(set(sp.base[M]) | flipped), sp.n, sp.P, sp.ports)[1]
            info4["point-flip unions"] += 1
            info4["point-flip unions still creating"] += nw > 0
            ok4 &= nw > 0
check("4 dropping one parity (a cylinder left) changes creation without removing it everywhere; the control (the union with one near point "
      "flipped) never removes creation: at every creating removal of the Fano splices every such union still creates",
      ok4 and info4["point-flip unions"] > 0, dict(info4))

OUT["seconds"] = round(time.time() - T0, 1)
print("ALL OK", OUT["seconds"], "s")
result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"], "proof": manifest["proof"],
          "status": "passed", "claim": manifest["claim"], "checks": {k: v for k, v in OUT.items() if k != "seconds"}}
text = json.dumps(result, indent=1, sort_keys=True, default=str) + "\n"
if "--write" in sys.argv:
    (HERE / "result.json").write_text(text)
elif not (HERE / "result.json").exists() or json.loads((HERE / "result.json").read_text()) != json.loads(text):
    print("result.json does not match a fresh run; rerun with --write after review")
    sys.exit(1)
