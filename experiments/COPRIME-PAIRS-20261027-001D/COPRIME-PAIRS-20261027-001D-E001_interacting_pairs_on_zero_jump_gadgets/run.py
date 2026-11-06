"""COPRIME-PAIRS-20261027-001D-E001: interacting pair failures on zero-jump gadgets (frozen contract: contract.json).

Cases (free graded algebras, interacting at d; summands from pf_lib.summand_types):
  A1 free class 3 on (1, 1), d = 5, p = 11, slots (1, 1, 2)
  A2 free class 3 on (1, 2), d = 5, p = 11, slots (1, 2, 3)
  A3 free class 4 on x (0), y (1), d = 5, p = 11, slots (1, 1, 2)   (m_d of class 3)
  A4 free class 3 on (1, 2, 2), d = 4, p = 5, slots (2, 1, 3)        (cable summands)
  A5 free class 3 on (1, 2), d = 4, p = 5, slots (2, 1, 3)           (cable summands)
Controls: X1 = A1 on the cumulative (plain) design; X2 = A1 with the dual slot given type +-1 (no duals at +-2).
Run: python3 -B run.py  (writes the artifact directory)"""
import json, os, sys, time, itertools
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pf_lib import *  # noqa: E402

T0 = time.time()
ART = os.path.join(os.path.abspath(os.path.join(HERE, "..", "..", "..")), "artifacts", "COPRIME-PAIRS-20261027-001D",
                   os.path.basename(HERE))
os.makedirs(ART, exist_ok=True)
LOG = open(os.path.join(ART, "run_log.txt"), "w")


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True); LOG.write(s + "\n"); LOG.flush()


CASES = [("A1", 11, 5, [1, 1], 3, (1, 1, 2)), ("A2", 11, 5, [1, 2], 3, (1, 2, 3)), ("A3", 11, 5, [0, 1], 4, (1, 1, 2)),
         ("A4", 5, 4, [1, 2, 2], 3, (2, 1, 3)), ("A5", 5, 4, [1, 2], 3, (2, 1, 3))]
REPS = {"A1": (5, 5, 4, 3, 3), "A2": (5, 5, 4, 3, 3), "A3": (5, 5, 4, 3, 3), "A4": (2, 2, 1, 1, 2), "A5": (5, 5, 4, 3, 3)}
rows, machinery_failures, failures = [], [], []


def machinery(G, name, rng):
    p, d = G.p, G.d
    bad = []
    for bi, B in enumerate(G.blocks):
        if G.kinds[bi][0] not in ("vertex", "private"): continue
        for c in range(1, d):
            v = class_vec(B.word, B.n, pow(G.zeta, c, p), p)
            if v is None: continue
            r = B.tags.index("read")
            cps = [q for q, t in enumerate(B.tags) if t == "copy"]
            if v[0] % p or v[-1] % p or not v[r] % p or any((v[q] - v[r]) % p for q in cps): bad.append(("M1 block", bi, c))
    for c in range(1, d):
        want = 1 + sum(1 for (bi, cc) in G.cls if cc == c)
        got = len(fixed(G.word, G.n, pow(G.zeta, c, p), p))
        if got != want: bad.append(("M2 cocycle dimension", c, got, want))
    # M3: all equations of layers <= l vanish  <=>  no unsolvable layer <= l (checked through the last layer)
    vals = rng.integers(0, p, (48, len(G.var)))
    E = G.evaluate(vals) % p
    L = G.L
    V = np.zeros((48, G.n, L.D), dtype=np.int64)
    ch = lambda k: int(L.chars[k]) % d
    add = {}
    for j, (bi, k) in enumerate(G.var):
        add[k] = (add.get(k, 0) + vals[:, j:j + 1] * G.cls[(bi, ch(k))][None, :]) % p
    okall = np.ones(48, dtype=bool)
    for lay in range(1, int(L.layer.max()) + 1):
        R = G.Mo.run(V)
        for k in [k for k in range(L.D) if L.layer[k] == lay]:
            X, b = solve_any(G.Mo.Lin[ch(k)], (-R[:, :, k]).T % p, p)
            okall &= ~b
            V[:, :, k] = (X.T + add.get(k, 0)) % p
    eq_ok = ~E.any(axis=1)
    if not (eq_ok == okall).all(): bad.append(("M3 equations vs solvability", int((eq_ok != okall).sum())))
    for b in bad: machinery_failures.append((name,) + tuple(b))
    return bad


def private_index(G, e):
    vs = G.var_sites()
    return [j for j, s in enumerate(vs) if s == ("e", e)]


def vertex_index(G, v):
    vs = G.var_sites()
    return [j for j, s in enumerate(vs) if s == ("v", v)]


def p3_locality(G3, K2, rng, ncfg=3, nsig=3):  # noqa: C901
    """for configurations (sigma_1, sigma_2, pi_1) and several sigma_0: the e0 solution sets on P3 equal the K2 solution sets, the e1
    equation values are constant over all of them, and vertex pairings vanish"""
    p = G3.p
    i0 = private_index(G3, 0); i1 = private_index(G3, 1)
    v0, v1, v2 = vertex_index(G3, 0), vertex_index(G3, 1), vertex_index(G3, 2)
    eqs = G3.eq_sites()
    c_e0 = [c for c, s in enumerate(eqs) if s == ("e", 0)]; c_e1 = [c for c, s in enumerate(eqs) if s == ("e", 1)]
    c_v = [c for c, s in enumerate(eqs) if s[0] == "v"]
    combos = np.array(list(itertools.product(range(p), repeat=len(i0))), dtype=np.int64)
    out = []
    for cfg in range(ncfg):
        s1, s2 = rng.integers(0, p, len(v1)), rng.integers(0, p, len(v2))
        pi1 = rng.integers(0, p, len(i1))
        e1_values, same_sets, vbad, nsol = set(), True, 0, 0
        for k in range(nsig):
            s0 = rng.integers(0, p, len(v0))
            vals = np.zeros((len(combos), len(G3.var)), dtype=np.int64)
            vals[:, i0] = combos; vals[:, v0] = s0; vals[:, v1] = s1; vals[:, v2] = s2; vals[:, i1] = pi1
            E = evaluate_chunked(G3, vals) % p
            sol = ~E[:, c_e0].any(axis=1)
            nsol += int(sol.sum())
            for row in E[sol][:, c_e1]: e1_values.add(tuple(int(x) for x in row))
            vbad += int(E[sol][:, c_v].any(axis=1).sum()) if c_v else 0
            f, _, _, S = edge_count(K2, s0, s1)
            same_sets &= (len(S) == int(sol.sum())) and set(map(tuple, S.tolist())) == set(map(tuple, combos[sol].tolist()))
        out.append({"e0 solutions": nsol, "distinct e1 equation values": len(e1_values), "e0 sets equal K2 sets": bool(same_sets),
                    "vertex pairings nonzero": vbad})
    return out


rng = np.random.default_rng(20261027)
for (name, p, d, gens, cls, slots) in CASES:
    L = free_graded(p, d, gens, cls)
    T = summand_types(p, d, slots)
    K2 = Gadget(L, d, p, T, 2, [(0, 1)])
    P3 = Gadget(L, d, p, T, 3, [(0, 1), (1, 2)])
    mb = machinery(K2, name + " K2", rng) + machinery(P3, name + " P3", rng)
    nv = len(vertex_index(K2, 0)); npv = len(private_index(K2, 0)); Fmax = p ** npv
    th0_vars = [j for j in vertex_index(K2, 0) if int(L.layer[K2.var[j][1]]) == 1 and int(L.chars[K2.var[j][1]]) % d == slots[0] % d]
    n1, n2, n3, ncfg, nsig = REPS[name]
    R1 = []
    for _ in range(n1):
        s = rng.integers(0, p, nv)
        f, vb, tot, _ = edge_count(K2, s, s)
        R1.append({"F": f, "vertex pairings nonzero": vb})
    R2 = []
    for _ in range(n2):
        D = np.zeros(nv, dtype=np.int64)
        D[[vertex_index(K2, 0).index(j) for j in th0_vars]] = rng.integers(1, p, len(th0_vars))
        f1, vb1, _, _ = edge_count(K2, np.zeros(nv, dtype=np.int64), D)
        f2, vb2, _, _ = edge_count(K2, D, np.zeros(nv, dtype=np.int64))
        R2.append({"Delta": D.tolist(), "F(0,D)": f1, "F(D,0)": f2, "vertex pairings nonzero": vb1 + vb2})
    R3 = []
    for _ in range(n3):
        su, sv = rng.integers(0, p, nv), rng.integers(0, p, nv)
        f, vb, _, _ = edge_count(K2, su, sv)
        R3.append({"F": f, "vertex pairings nonzero": vb})
    R4 = p3_locality(P3, K2, rng, ncfg, nsig)
    ok = (all(r["F"] == Fmax and r["vertex pairings nonzero"] == 0 for r in R1)
          and all(1 <= r["F(0,D)"] < Fmax and 1 <= r["F(D,0)"] < Fmax and r["vertex pairings nonzero"] == 0 for r in R2)
          and all(r["vertex pairings nonzero"] == 0 for r in R3)
          and all(r["distinct e1 equation values"] <= 1 and r["e0 sets equal K2 sets"] and r["vertex pairings nonzero"] == 0
                  and r["e0 solutions"] > 0 for r in R4))
    minors = [Fmax ** 4 - (r["F(0,D)"] * r["F(D,0)"]) ** 2 for r in R2]
    row = {"case": name, "p": p, "d": d, "generator characters": gens, "class": cls, "slots": slots,
           "summands": [T[i][3] for i in range(3)], "K2 strands": K2.n, "K2 crossings": len(K2.word), "P3 strands": P3.n,
           "P3 crossings": len(P3.word), "vertex variables": nv, "private variables": npv, "F_max": Fmax,
           "machinery failures": mb, "R1 diagonal": R1, "R2 across a pair-failing difference": R2, "R3 random pairs": R3,
           "R4 P3 locality": R4, "R5 minors F_max^4 - (F(0,D) F(D,0))^2": minors, "predictions hold": bool(ok)}
    rows.append(row)
    if not ok: failures.append(name)
    log(json.dumps(row, default=str)[:1500], f"({time.time() - T0:.0f}s)")

# ---------------------------------------------------------------- controls
controls = []
L = free_graded(11, 5, [1, 1], 3)
T = summand_types(11, 5, (1, 1, 2))
K2c = Gadget(L, 5, 11, T, 2, [(0, 1)], zero_jump=False)
P3c = Gadget(L, 5, 11, T, 3, [(0, 1), (1, 2)], zero_jump=False, pad=0)
R4c = p3_locality(P3c, K2c, rng)
matched = all(r["distinct e1 equation values"] <= 1 and r["e0 sets equal K2 sets"] for r in R4c)
controls.append({"control": "X1 A1 on the cumulative design: locality should fail", "rows": R4c, "matched (locality held)": matched})
log("X1", json.dumps(R4c), f"({time.time() - T0:.0f}s)")
L = free_graded(11, 5, [1, 1], 3)
Tw = summand_types(11, 5, (1, 1, 1))                      # slot 2 given the type of slot 0: no duals at +-2
K2w = Gadget(L, 5, 11, Tw, 2, [(0, 1)])
nvw = len(vertex_index(K2w, 0)); Fmw = 11 ** len(private_index(K2w, 0))
rw = []
for _ in range(3):
    D = np.zeros(nvw, dtype=np.int64); D[:2] = rng.integers(1, 11, 2)
    f, vb, _, _ = edge_count(K2w, np.zeros(nvw, dtype=np.int64), D)
    rw.append({"Delta": D.tolist(), "F(0,D)": f, "F_max": Fmw})
matched2 = any(r["F(0,D)"] < r["F_max"] for r in rw)
controls.append({"control": "X2 A1 with the dual slot given type +-1 (no duals at +-2): F should be constant (no deficit)",
                 "rows": rw, "matched (a deficit appeared)": matched2})
log("X2", json.dumps(rw), f"({time.time() - T0:.0f}s)")

verdict = "invalid" if machinery_failures or matched or matched2 else ("supported" if not failures else "refuted")
res = {"experiment_id": "COPRIME-PAIRS-20261027-001D-E001", "verdict": verdict, "machinery_failures": machinery_failures,
       "failures": failures, "controls": controls, "cases": len(rows), "seconds": round(time.time() - T0, 1)}
json.dump(rows, open(os.path.join(ART, "rows.json"), "w"), indent=1, default=str)
json.dump(res, open(os.path.join(ART, "result.json"), "w"), indent=1, default=str)
log("VERDICT", verdict, f"({time.time() - T0:.0f}s)")
