"""INTERFERENCE-20261029-001C-E001: independent replay of the cancellation cores of the two 2026 ETH refutations.

Parts (see contract.json):
  1 Anthropic eq. (12), the eight-square identity, and the factorization costs of its two terms
  2 Anthropic Lemma 2: grouped pieces A_i for t = 1, 2 blocks of three bits
  3 Anthropic Theorem B: pieces A_s for lambda = 1, 2, 3 bits (h = 2, 4, 6), sum identity and factorization ranks
  4 OpenAI's swap-matrix construction as simplified by Kintali: A = V f(W) at small parameters
Each part runs one control that must fail.  Writes artifacts/<ticket>/<id>/result.json.
Run: .venv/bin/python -B run.py [--parts 1,2,3,4] [--lambdas 1,2,3]"""
import argparse, itertools, json, math, os, sys, time
from fractions import Fraction
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "artifacts", "INTERFERENCE-20261029-001C", "INTERFERENCE-20261029-001C-E001_cancellation_cores_replay")
sys.path.insert(0, HERE)
import thm_b_pieces as TB  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--parts", default="1,2,3,4")
ap.add_argument("--lambdas", default="1,2,3")
args = ap.parse_args()
PARTS = {int(p) for p in args.parts.split(",")}
res = {"experiment_id": "INTERFERENCE-20261029-001C-E001", "parts": {}}
T00 = time.time()


def log(*a):
    print(*a, flush=True)


V3 = list(itertools.product((0, 1), repeat=3))


def phi(p, q):
    t = sum(p[k] * q[kp] for k in range(3) for kp in range(k, 3))
    t += q[0] * p[1] * p[2] + p[0] * q[1] * p[2] + p[0] * p[1] * q[2]
    return t % 2


def sigma(p, q, flip=None):
    s = -1 if phi(p, q) else 1
    if flip is not None and (p, q) == flip:
        s = -s
    return s


def xor(*vs):
    return tuple(sum(c) % 2 for c in zip(*vs))


def rank(M):
    return int(np.linalg.matrix_rank(np.asarray(M, dtype=float)))


# ---------------------------------------------------------------- part 1
if 1 in PARTS:
    def eight_square_violations(flip=None):
        bad = 0
        for x, y, u, v in itertools.product(V3, repeat=4):
            lhs = 2 * (x == v) * (y == u)
            rhs = (xor(x, y, u, v) == (0, 0, 0)) * (sigma(x, y, flip) * sigma(v, u, flip) + sigma(x, u, flip) * sigma(v, y, flip))
            bad += lhs != rhs
        return bad
    viol = eight_square_violations()
    rowterm = lambda x, y, u, v: (xor(x, y, u, v) == (0, 0, 0)) * sigma(x, y) * sigma(v, u)
    colterm = lambda x, y, u, v: (xor(x, y, u, v) == (0, 0, 0)) * sigma(x, u) * sigma(v, y)
    cross = lambda x, y, u, v: 2 * (x == v) * (y == u)

    def flat_rows(f):
        return [[f(x, y, u, v) for u in V3 for v in V3] for x in V3 for y in V3]

    def flat_cols(f):
        return [[f(x, y, u, v) for y in V3 for v in V3] for x in V3 for u in V3]
    costs = {name: {"rows bits": math.log2(rank(flat_rows(f))), "columns bits": math.log2(rank(flat_cols(f)))}
             for name, f in (("crossing 2[x=v][y=u]", cross), ("row choice", rowterm), ("column choice", colterm))}
    S = np.array([[sigma(p, q) for q in V3] for p in V3])
    hadamard = bool(np.array_equal(S @ S.T, 8 * np.eye(8)))
    ctrl = eight_square_violations(flip=((0, 0, 1), (0, 1, 0)))
    # knot test (K1-K3 on allowed states, tools/knotlab) for one bit-slice of the hyperedge and for the two equalities
    import subprocess
    par_cnf = ";".join(" ".join(("~" + nm if b else nm) for nm, b in zip("xyuv", a))
                       for a in itertools.product((0, 1), repeat=4) if sum(a) % 2 == 1)
    eq_cnf = "~x v; x ~v; ~y u; y ~u"
    knot = {}
    for name, cnf in (("parity hyperedge x+y+u+v=0 (one bit)", par_cnf), ("two equalities x=v, y=u", eq_cnf)):
        r = subprocess.run([sys.executable, "-B", "-m", "knotlab", "check", "--cnf", cnf, "--loops", "x", "y", "u",
                            "--contact", "v", "--json"], cwd=ROOT, env=dict(os.environ, PYTHONPATH=os.path.join(ROOT, "tools")),
                           capture_output=True, text=True)
        try:
            j = json.loads(r.stdout)
            knot[name] = {k: j.get(k) for k in ("is_knot", "binding", "loss_on_erasure", "coexistence", "minimum_width")}
        except Exception:
            knot[name] = {"raw": r.stdout[-400:], "err": r.stderr[-400:]}
    res["parts"]["1 eight-square identity"] = {
        "settings": 4096, "violations": viol, "costs (log2 rank)": costs,
        "sign table is a Hadamard matrix": hadamard,
        "knotlab check": knot,
        "control: one flipped sign-table entry, violations": ctrl,
        "pass": viol == 0 and costs["row choice"]["rows bits"] == 3 and costs["column choice"]["columns bits"] == 3
        and costs["crossing 2[x=v][y=u]"]["rows bits"] == 6 and ctrl > 0
        and knot["parity hyperedge x+y+u+v=0 (one bit)"].get("is_knot") is True
        and knot["two equalities x=v, y=u"].get("is_knot") is False}
    log("part 1", res["parts"]["1 eight-square identity"])

# ---------------------------------------------------------------- part 2
if 2 in PARTS:
    def lemma2(t, swap_costs=False):
        strings = list(itertools.product(V3, repeat=t))
        idx = {s: i for i, s in enumerate(strings)}
        N = len(strings)
        # A_i as tensors over (x, y, u, v), each a t-tuple of 3-bit blocks
        A = [np.zeros((N, N, N, N)) for _ in range(t + 1)]
        R = np.zeros((8, 8, 8, 8)); C = np.zeros((8, 8, 8, 8))
        for x, y, u, v in itertools.product(range(8), repeat=4):
            X, Y, U, Vv = V3[x], V3[y], V3[u], V3[v]
            par = xor(X, Y, U, Vv) == (0, 0, 0)
            R[x, y, u, v] = par * sigma(X, Y) * sigma(Vv, U)
            C[x, y, u, v] = par * sigma(X, U) * sigma(Vv, Y)
        for S in itertools.product((0, 1), repeat=t):  # S[j] = 1: column choice in block j
            i = sum(S)
            term = np.ones((1, 1, 1, 1))
            for j in range(t):
                blk = C if S[j] else R
                term = np.einsum("abcd,efgh->aebfcgdh", term, blk).reshape(term.shape[0] * 8, term.shape[1] * 8,
                                                                          term.shape[2] * 8, term.shape[3] * 8)
            A[i] += term
        total = sum(A)
        target = np.zeros_like(total)
        for a, b in itertools.product(range(N), repeat=2):
            target[a, b, b, a] = 2 ** t
        sum_ok = bool(np.array_equal(total, target))
        rows = []
        for i in range(t + 1):
            Mr = A[i].reshape(N * N, N * N)
            Mc = A[i].transpose(0, 2, 1, 3).reshape(N * N, N * N)
            rr, rc = rank(Mr), rank(Mc)
            br = t + 3 * (t - i) + 6 * i
            bc = t + 6 * (t - i) + 3 * i
            if swap_costs:
                br, bc = bc, br
            rows.append({"i": i, "rank rows": rr, "bound rows 2^": br, "rank columns": rc, "bound columns 2^": bc,
                         "within": rr <= 2 ** br and rc <= 2 ** bc})
        return sum_ok, rows
    p2 = {}
    for t in (1, 2):
        tt = time.time()
        ok, rows = lemma2(t)
        p2[f"t={t}"] = {"sum = 2^t [x=v][y=u]": ok, "pieces": rows, "seconds": round(time.time() - tt, 1)}
        log("part 2 t =", t, p2[f"t={t}"])
    okc, rowsc = lemma2(2, swap_costs=True)
    p2["control: rows and columns costs swapped (t=2) violates a bound"] = not all(r["within"] for r in rowsc)
    p2["pass"] = all(p2[f"t={t}"]["sum = 2^t [x=v][y=u]"] and all(r["within"] for r in p2[f"t={t}"]["pieces"]) for t in (1, 2)) \
        and p2["control: rows and columns costs swapped (t=2) violates a bound"]
    res["parts"]["2 Lemma 2 grouped pieces"] = p2

# ---------------------------------------------------------------- part 3
if 3 in PARTS:
    def p_of(n):
        return sum(1 for _ in TB.partitions(n)) if n >= 0 else 0
    p3 = {}
    for lam in [int(x) for x in args.lambdas.split(",")]:
        tt = time.time()
        h, mus, pieces, ok, dt = TB.run(lam)
        n = 2 ** lam
        rows = []
        for s in range(-2 * h, 2 * h + 1):
            M = np.zeros((n, n, n, n))
            for (ss, x, y, u, v), val in pieces.items():
                if ss == s:
                    M[x, y, u, v] = val
            rr = rank(M.reshape(n * n, n * n))
            rc = rank(M.transpose(0, 2, 1, 3).reshape(n * n, n * n))
            Rrow = sum(p_of(s + i) for i in range(0, 2 * h + 1))
            Rcol = sum(p_of(2 * h - s - i) for i in range(0, 2 * h + 1))
            rows.append({"s": s, "rank rows": rr, "R_s^row": Rrow, "rank columns": rc, "R_s^col": Rcol,
                         "within": rr <= Rrow and rc <= Rcol})
        worst = max(math.log2(r["R_s^row"]) + math.log2(r["R_s^col"]) for r in rows)
        p3[f"lambda={lam}"] = {"h": h, "sum = h! [x=v][y=u]": ok, "pieces within stated counts": all(r["within"] for r in rows),
                               "max over s of log2 R^row + log2 R^col": round(worst, 3), "diagonal cost 4*lambda": 4 * lam,
                               "pieces": rows, "seconds": round(time.time() - tt, 1)}
        log("part 3 lambda =", lam, {k: v for k, v in p3[f"lambda={lam}"].items() if k != "pieces"})
    # control: drop the sign (-1)^i in Q_s at lambda = 1
    orig = TB.Q_s_apply

    def Q_nosign(a, b, s, h, f):
        out = {}
        for i in range(0, 2 * h + 1):
            g = TB.apply_poly(b, h - s - i, f)
            if not g:
                continue
            TB.add(out, TB.apply_poly(TB.a_angle(a, i, h), s - h + i, g), 1)
        return out
    TB.Q_s_apply = Q_nosign
    _, _, _, okc, _ = TB.run(1)
    TB.Q_s_apply = orig
    p3["control: sign (-1)^i dropped breaks the sum identity (lambda=1)"] = not okc
    p3["pass"] = all(v["sum = h! [x=v][y=u]"] and v["pieces within stated counts"] for k, v in p3.items()
                     if k.startswith("lambda=")) and p3["control: sign (-1)^i dropped breaks the sum identity (lambda=1)"]
    res["parts"]["3 Theorem B pieces"] = p3

# ---------------------------------------------------------------- part 4
if 4 in PARTS:
    def swap_case(r, Q, R, degree_shift=0):
        pair = list(itertools.product(range(r), repeat=2))
        B = list(itertools.product(pair, repeat=Q))  # u = ((a(1),d(1)), ..., (a(Q),d(Q)))
        idx = {u: i for i, u in enumerate(B)}
        D = len(B)

        def swapped(u, t):
            lst = list(u); a, d = lst[t]; lst[t] = (d, a); return tuple(lst)
        Pi = []
        for t in range(Q):
            M = np.zeros((D, D))
            for u in B:
                M[idx[u], idx[swapped(u, t)]] = 1
            Pi.append(M)
        Vm = np.eye(D)
        for M in Pi:
            Vm = Vm @ M
        Wm = sum(0.5 * (np.eye(D) - M) for M in Pi)
        p = (r - 1) / (2 * r)
        mu = Q * p
        RR = R + degree_shift
        b = math.ceil(mu - (RR - 1) / 2)
        b = max(0, min(b, Q - RR + 1))
        I0 = list(range(b, b + RR))
        # f of degree <= RR-1 with f(j) = (-1)^j on I0, as exact Lagrange coefficients applied to W
        def f_of_W():
            out = np.zeros((D, D))
            for j in I0:
                term = np.eye(D) * ((-1) ** j)
                for hh in I0:
                    if hh != j:
                        term = term @ ((Wm - hh * np.eye(D)) / (j - hh))
                out += term
            return out
        A = Vm @ f_of_W()
        # one-pair basis: e_aa, e_ab + e_ba (+1), e_ab - e_ba (-1)
        one = []
        for a in range(r):
            v = np.zeros((r, r)); v[a, a] = 1; one.append((v.flatten(), 0))
        for a in range(r):
            for c in range(a + 1, r):
                v = np.zeros((r, r)); v[a, c] = 1; v[c, a] = 1; one.append((v.flatten(), 0))
                v = np.zeros((r, r)); v[a, c] = 1; v[c, a] = -1; one.append((v.flatten(), 1))
        basis_ok, bad_count, nonzero_corr = True, 0, 0
        for choice in itertools.product(range(len(one)), repeat=Q):
            vec = np.ones(1); jneg = 0
            for ci in choice:
                vec = np.kron(vec, one[ci][0]); jneg += one[ci][1]
            # map kron ordering (pair index per node, node-major) to B ordering
            psi = np.zeros(D)
            for k, u in enumerate(B):
                pass
            psi = vec  # B is itertools.product over pair (lexicographic), matching np.kron of per-node r*r vectors
            Apsi = A @ psi
            if jneg in I0:
                basis_ok &= bool(np.allclose(Apsi, psi))
            else:
                bad_count += 1
                fj = sum(((-1) ** j) * np.prod([(jneg - hh) / (j - hh) for hh in I0 if hh != j]) for j in I0)
                if abs(1 - ((-1) ** jneg) * fj) > 1e-9:
                    nonzero_corr += 1
        rk = int(np.linalg.matrix_rank(np.eye(D) - A, tol=1e-7))
        maxdis = 0
        for u in B:
            for w in B:
                if abs(A[idx[u], idx[w]]) > 1e-9:
                    dis = sum(1 for t in range(Q) if w[t][0] != u[t][1])
                    maxdis = max(maxdis, dis)
        return {"r": r, "Q": Q, "R": R, "degree": RR - 1, "D": D, "window": I0,
                "A fixes every basis vector with j in the window": basis_ok,
                "exceptional basis vectors": bad_count, "with nonzero correction": nonzero_corr,
                "rank(I - A)": rk, "max disagreements of a nonzero entry": maxdis,
                "pass": basis_ok and rk == nonzero_corr and maxdis <= R - 1}
    p4 = {}
    for (r, Q, R) in ((2, 4, 2), (2, 5, 2), (3, 3, 2), (2, 6, 3)):
        tt = time.time()
        p4[f"(r,Q,R)=({r},{Q},{R})"] = swap_case(r, Q, R)
        log("part 4", p4[f"(r,Q,R)=({r},{Q},{R})"], round(time.time() - tt, 1), "s")
    ctrl = swap_case(2, 5, 2, degree_shift=1)
    p4["control: degree R instead of R-1 exceeds the disagreement bound"] = ctrl["max disagreements of a nonzero entry"] > 1
    p4["pass"] = all(v["pass"] for k, v in p4.items() if k.startswith("(r,Q,R)")) and \
        p4["control: degree R instead of R-1 exceeds the disagreement bound"]
    res["parts"]["4 swap-matrix construction"] = p4

res["all pass"] = all(v.get("pass", False) for v in res["parts"].values())
res["seconds"] = round(time.time() - T00, 1)
os.makedirs(OUT, exist_ok=True)
tag = "_".join(sorted(str(p) for p in PARTS)) + ("_lambda_" + args.lambdas.replace(",", "") if 3 in PARTS else "")
json.dump(res, open(os.path.join(OUT, f"result_parts_{tag}.json"), "w"), indent=1, default=str)
log("ALL PASS" if res["all pass"] else "SOME PART FAILED", res["seconds"], "s")
