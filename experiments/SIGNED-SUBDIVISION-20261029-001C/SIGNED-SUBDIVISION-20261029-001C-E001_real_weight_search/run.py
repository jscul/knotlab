"""SIGNED-SUBDIVISION-20261029-001C-E001: search for exact real weightings on every rule shape (contract.json).

For each of the 122 rule shapes, each scale k in {2, 3} and each sign class (rw_lib.sign_classes), minimize over the gauge slice
(free log-magnitudes in [-ln 100, ln 100], the others 0) a residual with one entry per exactness equation on the coarse 2-torus,
each normalized by its own scale (side_residual), from N_START random starts with scipy's bounded least squares.  Every (shape,
scale, class) whose best residual is below CAND is searched again on the coarse 2- and 3-tori jointly, from its best point and
N_JOINT random starts; it is confirmed when the joint residual is below CONF, some allowed assignment keeps |F(x)| above NONDEG
times the sum of the absolute values of its terms on both tori (so c != 0), and, at scale 2, the residual on the coarse 4-torus
is below CONF too.
Shapes are labelled by SIGNED-SUBDIVISION-20261029-001B: excluded (sign-parity obstruction), affine (the 22 counted-exact shapes) or
open.  Run: .venv/bin/python -B run.py [--workers N] [--only N]   (numpy, scipy)"""
import argparse, itertools, json, os, sys, time
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from scipy.optimize import least_squares

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
BDIR = os.path.join(ROOT, "proofs", "SIGNED-SUBDIVISION-20261029-001B",
                    "SIGNED-SUBDIVISION-20261029-001B-P001_real_weights_under_shared_subdivision")
OUT = os.path.join(ROOT, "artifacts", "SIGNED-SUBDIVISION-20261029-001C", "SIGNED-SUBDIVISION-20261029-001C-E001_real_weight_search")
sys.path.insert(0, BDIR)
import ss_lib as S  # noqa: E402
import rw_lib as R  # noqa: E402

N_START, N_JOINT, BOX, CAND, CONF, NONDEG, SEED = 24, 8, float(np.log(100.0)), 1e-8, 1e-9, 1e-6, 20261029


def name(s, P1, P2):
    ex = lambda P: " ".join("".join(map(str, t)) for t in sorted(set(S.cube) - P))
    return f"{s} {S.kind(P1)} excl {ex(P1)}" + (f" / {ex(P2)}" if P2 is not None else "")


_TF = {}


def transfer(L, wup, wdn):
    """float transfer matrix; index arrays cached per L"""
    if L not in _TF:
        bits = S.bits_of(L)
        up = [bits[:, i][:, None] * 4 + bits[:, (i + 1) % L][:, None] * 2 + bits[:, i][None, :] for i in range(L)]
        dn = [bits[:, (i + 1) % L][:, None] * 4 + bits[:, i][None, :] * 2 + bits[:, (i + 1) % L][None, :] for i in range(L)]
        _TF[L] = (up, dn)
    up, dn = _TF[L]
    T = np.ones((1 << L, 1 << L))
    for i in range(L):
        T *= wup[up[i]]
        if wdn is not None:
            T *= wdn[dn[i]]
    return T


_KEYS = {}


def blocks(m, k, wup, wdn):
    """M[a][b] = rows of T^k with coarse value a, columns with coarse value b (fine rows of length k m)"""
    L = k * m
    if (m, k) not in _KEYS:
        bits = S.bits_of(L)
        key = (bits[:, ::k] * (1 << np.arange(m))[None, :]).sum(1)
        _KEYS[(m, k)] = [np.nonzero(key == x)[0] for x in range(1 << m)]
    idx = _KEYS[(m, k)]
    Tk = np.linalg.matrix_power(transfer(L, wup, wdn), k)
    return [[Tk[np.ix_(idx[a], idx[b])] for b in range(1 << m)] for a in range(1 << m)]


def fine(m, k, wup, wdn):
    """F over the coarse assignments of the m-torus (rows x_0..x_{m-1}): trace of the cyclic product of blocks"""
    M = blocks(m, k, wup, wdn)
    n = 1 << m
    xs = list(itertools.product(range(n), repeat=m))
    if m == 2:
        return np.array([np.sum(M[a][b] * M[b][a].T) for a, b in xs])
    if m == 3:
        P = {(a, b, c): M[a][b] @ M[b][c] for a in range(n) for b in range(n) for c in range(n)}
        return np.array([np.sum(P[(a, b, c)] * M[c][a].T) for a, b, c in xs])
    Mt = np.array([[M[a][b] for b in range(n)] for a in range(n)])  # (n, n, d, d)
    return np.einsum("abij,bcjk,cdkl,dali->abcd", Mt, Mt, Mt, Mt, optimize=True).reshape(-1)  # m == 4


def coarse(m, wup, wdn):
    T = transfer(m, wup, wdn)
    return np.array([np.prod([T[xs[j], xs[(j + 1) % m]] for j in range(m)]) for xs in itertools.product(range(1 << m), repeat=m)])


def weights(P1, P2, sign, free, theta):
    n1 = len(P1)
    mags = np.ones(len(sign))
    mags[free] = np.exp(theta)
    w = np.array(sign) * mags
    w1 = np.zeros(8); w2 = None
    for t, v in zip(sorted(P1), w[:n1]):
        w1[t[0] * 4 + t[1] * 2 + t[2]] = v
    if P2 is not None:
        w2 = np.zeros(8)
        for t, v in zip(sorted(P2), w[n1:]):
            w2[t[0] * 4 + t[1] * 2 + t[2]] = v
    return w1, w2


def side_residual(m, k, w1, w2):
    """one entry per exactness equation, each normalized by its own scale (so concentration cannot hide a violation):
    allowed x != x0: (F(x) W(x0) - F(x0) W(x)) / (|F(x) W(x0)| + |F(x0) W(x)|); forbidden x with extensions: F(x) / A(x), where A
    is F computed with |w| (the sum of the absolute values of the terms)"""
    f = fine(m, k, w1, w2)
    a = fine(m, k, np.abs(w1), None if w2 is None else np.abs(w2))
    w = coarse(m, w1, w2)
    al = np.nonzero(w != 0)[0]
    out = []
    if len(al):
        x0 = al[0]
        for x in al[1:]:
            num = f[x] * w[x0] - f[x0] * w[x]
            den = abs(f[x] * w[x0]) + abs(f[x0] * w[x])
            out.append(num / den if den > 0 else 0.0)
    fb = np.nonzero((w == 0) & (a > 0))[0]
    out += list(f[fb] / a[fb])
    return np.array(out)


def nondegeneracy(theta, P1, P2, sign, free, k, m):
    """max over coarse-allowed x of |F(x)| / A(x): an exact weighting needs F != 0 on allowed assignments (c != 0)"""
    w1, w2 = weights(P1, P2, sign, free, theta)
    f = fine(m, k, w1, w2)
    a = fine(m, k, np.abs(w1), None if w2 is None else np.abs(w2))
    al = coarse(m, w1, w2) != 0
    return float(np.max(np.abs(f[al]) / a[al])) if al.any() else 0.0


def resid(theta, P1, P2, sign, free, k, sides=(2,)):
    w1, w2 = weights(P1, P2, sign, free, theta)
    r = np.concatenate([side_residual(m, k, w1, w2) for m in sides])
    return np.where(np.isfinite(r), r, 1.0)


def task(args):
    si, k, ci = args
    s, P1, P2 = S.rule_shapes()[si]
    reps, _ = R.sign_classes(P1, P2)
    sign = reps[ci]
    free, _ = R.slice_free(P1, P2)
    rng = np.random.default_rng([SEED, si, k, ci])
    best = (np.inf, None)
    if not free:
        r = float(np.linalg.norm(resid(np.zeros(0), P1, P2, sign, free, k)))
        best = (r, [])
    else:
        for _ in range(N_START):
            th0 = rng.uniform(-BOX, BOX, len(free))
            try:
                sol = least_squares(resid, th0, args=(P1, P2, sign, free, k), bounds=(-BOX, BOX), method="trf",
                                    xtol=1e-15, ftol=1e-15, gtol=1e-15, max_nfev=300)
            except Exception:
                continue
            r = float(np.linalg.norm(sol.fun))
            if r < best[0]:
                best = (r, sol.x.tolist())
    rec = {"shape": name(s, P1, P2), "scale": k, "class": ci, "sign": list(sign), "free": len(free), "best": best[0], "theta": best[1],
           "at_box": bool(best[1] is not None and len(best[1]) and max(abs(v) for v in best[1]) > BOX - 1e-6)}
    if best[0] < CAND:
        sides = (2, 3)
        jbest = (float(np.linalg.norm(resid(np.array(best[1]), P1, P2, sign, free, k, sides))), np.array(best[1]))
        if len(free):
            starts = [np.array(best[1])] + [rng.uniform(-BOX, BOX, len(free)) for _ in range(N_JOINT)]
            for th0 in starts:
                try:
                    sol = least_squares(resid, th0, args=(P1, P2, sign, free, k, sides), bounds=(-BOX, BOX), method="trf",
                                        xtol=1e-15, ftol=1e-15, gtol=1e-15, max_nfev=300)
                except Exception:
                    continue
                v = float(np.linalg.norm(sol.fun))
                if v < jbest[0]:
                    jbest = (v, sol.x)
        joint, th = jbest
        side4 = float(np.linalg.norm(resid(th, P1, P2, sign, free, k, (4,)))) if k == 2 and joint < CONF else None
        nondeg = min(nondegeneracy(th, P1, P2, sign, free, k, m) for m in sides)
        rec.update({"joint_2_3": joint, "side4": side4, "theta_joint": th.tolist(), "nondegeneracy": nondeg,
                    "confirmed": bool(joint < CONF and nondeg > NONDEG and (k == 3 or (side4 is not None and side4 < CONF)))})
    return rec


def golden(shapes):
    """targeted record for the recommendation's starting point: the Fibonacci laws (no lone one, and its complement no lone
    zero), on up triangles and on all triangles, with weights sigma_|t| phi^(s |t|) depending on the Hamming weight |t| of the
    tuple (sigma_0 = 1, the other two signs free, s in {+-1/4, +-1/2, +-1}); largest per-equation residual on the coarse 2- and
    3-tori at both scales"""
    phi = (1 + 5 ** 0.5) / 2
    out = {}
    for excl, label in (({(0, 0, 1), (0, 1, 0), (1, 0, 0)}, "no lone one"), ({(0, 1, 1), (1, 0, 1), (1, 1, 0)}, "no lone zero")):
        for s_, P1, P2 in shapes:
            if set(S.cube) - P1 != excl or (P2 is not None and P2 != P1):
                continue
            classes = sorted({sum(t) for t in P1} - {0})
            best = {}
            for k in (2, 3):
                vals = []
                for sx in (-1, -0.5, -0.25, 0.25, 0.5, 1):
                    for sg in itertools.product((1, -1), repeat=len(classes)):
                        sig = dict(zip(classes, sg)); sig[0] = 1
                        w = np.zeros(8)
                        for t in P1:
                            w[t[0] * 4 + t[1] * 2 + t[2]] = sig[sum(t)] * phi ** (sx * sum(t))
                        r = np.concatenate([side_residual(m, k, w, None if P2 is None else w) for m in (2, 3)])
                        vals.append(float(np.max(np.abs(r))))
                best[f"scale {k}"] = min(vals)
            out[f"{s_} {label}"] = best
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--only", type=int, default=None, help="prototype: first N tasks only, no result file")
    a = ap.parse_args()
    b_res = json.load(open(os.path.join(BDIR, "result.json")))["checks"]
    excluded = {2: set(b_res["excluded"]["scale 2"]), 3: set(b_res["excluded"]["scale 3"])}
    open_ = {2: set(b_res["open"]["scale 2"]), 3: set(b_res["open"]["scale 3"])}
    shapes = S.rule_shapes()
    tasks = [(si, k, ci) for si, (s, P1, P2) in enumerate(shapes) for k in (2, 3) for ci in range(len(R.sign_classes(P1, P2)[0]))]
    if a.only:
        tasks = tasks[:a.only]
    t0 = time.time()
    with ProcessPoolExecutor(a.workers) as ex:
        recs = list(ex.map(task, tasks, chunksize=4))
    affine = set(b_res["affine"])
    excl_on_2torus = {k: {nm for nm, v in b_res["excluded"][f"scale {k}"].items() if v[0] == 2} for k in (2, 3)}
    for r in recs:
        k = r["scale"]
        r["label"] = "affine" if r["shape"] in affine else ("excluded" if r["shape"] in excluded[k] else "open")
    summary = {}
    for k in (2, 3):
        for lab in ("excluded", "open", "affine"):
            rs = [r for r in recs if r["scale"] == k and r["label"] == lab]
            if not rs:
                continue
            per_shape = {}
            for r in rs:
                per_shape[r["shape"]] = min(per_shape.get(r["shape"], np.inf), r["best"])
            summary[f"scale {k}, {lab}"] = {
                "shapes": len(per_shape), "classes": len(rs),
                "min over shapes of the best 2-torus residual": min(per_shape.values()),
                "shapes with a 2-torus candidate": sorted(sh for sh, v in per_shape.items() if v < CAND),
                "candidates (shape, class)": sum(1 for r in rs if r["best"] < CAND),
                "confirmed (shape, class)": [(r["shape"], r["class"]) for r in rs if r.get("confirmed")],
                "best residual at the box boundary": sum(1 for r in rs if r["at_box"])}
    # predictions and the cheapest control (contract.json)
    exact_classes = {2: {(nm, tuple(sg)) for nm, v in b_res["affine"].items() for sg, q in v["scale 2, sides 2-6"]},
                     3: {(nm, tuple(sg)) for nm, v in b_res["affine"].items() for sg, q in v["scale 3, sides 2-4"]}}
    conf = {(r["shape"], tuple(r["sign"]), r["scale"]) for r in recs if r.get("confirmed")}
    si0 = next(i for i, (s, P1, P2) in enumerate(shapes) if s == "S1" and set(S.cube) - P1 == {(0, 0, 0)} and P2 == P1)
    s0, P10, P20 = shapes[si0]
    free0, _ = R.slice_free(P10, P20)
    ctrl = float(np.max(np.abs(resid(np.array([-4.558, -4.572, -3.621, 3.059]), P10, P20, R.sign_classes(P10, P20)[0][0], free0, 2))))
    summary["predictions"] = {
        "P1 no open shape confirmed": not any(r.get("confirmed") for r in recs if r["label"] == "open"),
        "P2 every exact plus-minus-one class of the affine shapes confirmed": all((nm, sg, k) in conf for k in (2, 3) for nm, sg in exact_classes[k]),
        "P2 counts (scale 2, scale 3)": [len(exact_classes[2]), len(exact_classes[3])],
        "P3 no excluded shape confirmed": not any(r.get("confirmed") for r in recs if r["label"] == "excluded"),
        "P3 no shape excluded on the coarse 2-torus reaches a 2-torus candidate": not any(
            r["best"] < CAND for r in recs if r["label"] == "excluded" and r["shape"] in excl_on_2torus[r["scale"]]),
        "confirmed classes of the affine shapes beyond the exact plus-minus-one classes": sorted(
            (nm, k) for nm, sg, k in conf if nm in affine and (nm, sg) not in exact_classes[k]),
        "cheapest control: largest per-equation residual at the old flawed weighting (must exceed 0.1)": ctrl}
    gold = golden(shapes)
    summary["golden weights of the Fibonacci laws: smallest largest-residual over the grid (coarse 2- and 3-tori)"] = gold
    summary["predictions"]["P4 no golden weighting of the Fibonacci laws is exact"] = all(v > CONF for d in gold.values() for v in d.values())
    pred = summary["predictions"]
    all_pass = all(v is True for k, v in pred.items() if k.startswith("P") and isinstance(v, bool)) and pred[
        "cheapest control: largest per-equation residual at the old flawed weighting (must exceed 0.1)"] > 0.1
    summary["all pass"] = all_pass
    print(json.dumps(summary, indent=1, default=str))
    print("seconds", round(time.time() - t0, 1))
    if not a.only:
        os.makedirs(OUT, exist_ok=True)
        json.dump({"schema_version": 1, "experiment_id": "SIGNED-SUBDIVISION-20261029-001C-E001", "parameters":
                   {"N_START": N_START, "N_JOINT": N_JOINT, "BOX": BOX, "CAND": CAND, "CONF": CONF, "NONDEG": NONDEG, "SEED": SEED}, "all pass": summary["all pass"], "summary": summary, "records": recs,
                   "seconds": round(time.time() - t0, 1)}, open(os.path.join(OUT, "result.json"), "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
