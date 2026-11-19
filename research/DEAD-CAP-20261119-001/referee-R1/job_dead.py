"""Shared-runner job for the referee's check of DEAD-CAP-20261119-001.

The study's random and skeleton samplers (job.py's sample_rand and sample_skel, same seeds) are run only to regenerate the study's
own starts.  Its rate functions (deadlib.rate_of, deadlib.branch_rate) and exact counts (deadlib.exact_counts) are run as the
object under test, labelled.  Everything else is the referee's own:
- growth: the FIRST-KNOT-R1 engine with the program's rule, the implied test read structurally (CAP-CHAINS-R1's light engine);
- the exact minimal recurrence of the referee's counts (BREAK-EDDIES-R1, Berlekamp-Massey over Q) and its dominant root;
- the radius of the branch system computed by the referee's own code: the system written from the proof's Theorem 3, its least
  solution by Newton's method at fixed z, and z below the radius when that solution is finite with Jacobian spectral radius below 1.

Parts:
- D4 (per sampler case): every rank-1 exponential piece of the case, which D4 scored: the study's root of W(1/x) = 1, the study's
  estimator at its 4,000 iterations, the referee's radius, the referee's growth rate from its own counts; for the first two pieces
  of the case also the estimator at 40,000 iterations.
- R2 (per skeleton case): the first ten starts with a piece of rank >= 2: the referee's growth against the study's exact counts on
  every round reached, and the referee's radius against the study's estimate.
- TH: the theta, grown by the referee to round 13, against the series 11, 12, 20, ..., 18,375, and its radius.
- PF: Lemma 1's profile bound on the regenerated random and skeleton starts and on the touch census's in-class starts with a dead
  knot, from the referee's own blocks.

  .venv/bin/python -B scripts/longrun.py launch research/DEAD-CAP-20261119-001/referee-R1/job_dead.py \\
      --out runs/referee-dead --unit referee-dead --workers 4 --case-timeout 7200 --case-mem 3G --mem-max 16G
"""
import importlib.util
import itertools
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in ("research/CAP-CHAINS-20261119-001/referee-R1", "research/WEIGHTINGS-20261119-001/referee-R1",
          "research/DOUBLE-IDENT-20261119-001/referee-R1", "research/RELAY-IDENT-20261119-001/referee-R1",
          "research/CHAIN-IDENT-20261119-001/referee-R1", "research/RING-IDENT-20261119-001/referee-R1",
          "research/FIRST-KNOT-20261118-001/referee-R1", "research/TOUCH-CENSUS-20261118-001/referee-R1",
          "research/BREAK-EDDIES-20261119-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))
PROOF = ROOT / "proofs/DEAD-CAP-20261119-001A/DEAD-CAP-20261119-001A-P001_dead"
PARAMS = {}
PROFILES = {(), (2,), (3,), (4,), (5,), (2, 2), (2, 3)}


def setup(params):
    PARAMS.update(params)


def study():
    sys.path.insert(0, str(PROOF))
    spec = importlib.util.spec_from_file_location("dc_job", PROOF / "job.py")
    JOB = importlib.util.module_from_spec(spec)
    sys.modules["dc_job"] = JOB
    spec.loader.exec_module(JOB)
    return JOB, JOB.DL


# ---- the referee's own map and branch system ----

def my_map(sizes, edges):
    n = len(sizes)
    sh = Counter()
    nb = defaultdict(set)
    for a, b in edges:
        sh[a] += 1
        sh[b] += 1
        nb[a].add(b)
        nb[b].add(a)
    opn = [sizes[k] - sh[k] for k in range(n)]
    live = {k for k in range(n) if opn[k] >= 1}
    blocks = {w: frozenset(nb[w] & live) for w in range(n) if len(nb[w] & live) >= 2}
    of = defaultdict(list)
    for w, B in blocks.items():
        for k in B:
            of[k].append(w)
    d = {k: sum(len(blocks[w]) - 1 for w in of[k]) for k in live}
    spares = {k: (opn[k] - d[k]) if opn[k] >= 3 else 0 for k in live}
    raypend = {k: (opn[k] - d[k]) if opn[k] <= 2 else 0 for k in live}
    # pieces of the incidence graph
    parent = {}

    def find(x):
        while parent.setdefault(x, x) != x:
            x = parent[x]
        return x
    for w, B in blocks.items():
        for k in B:
            parent[find(("p", k))] = find(("b", w))
    comps = defaultdict(lambda: {"points": set(), "blocks": set()})
    for k in live:
        comps[find(("p", k))]["points"].add(k)
    for w in blocks:
        comps[find(("b", w))]["blocks"].add(w)
    pieces = []
    for c in comps.values():
        inc = sum(len(blocks[w]) for w in c["blocks"])
        rank = inc - (len(c["points"]) + len(c["blocks"])) + 1
        pieces.append({"points": sorted(c["points"]), "blocks": sorted(c["blocks"]), "rank": rank})
    return {"n": n, "open": opn, "live": live, "blocks": blocks, "of": of, "d": d, "spares": spares, "raypend": raypend,
            "pieces": pieces, "deg": {k: len(nb[k]) for k in range(n)}, "sh": sh, "sizes": sizes}


def my_radius(M, P):
    """1/rho of the piece's branch system (the referee's own: Newton at fixed z, spectral radius test, bisection)."""
    inc = [(p, w) for w in P["blocks"] for p in M["blocks"][w]]
    idx = {x: i for i, x in enumerate(inc)}
    terms = [[(q, [idx[(q, w2)] for w2 in M["of"][q] if w2 != w]) for q in M["blocks"][w] if q != p] for (p, w) in inc]

    def e(q, z):
        v = (1 + z) ** M["spares"][q]
        rp, o = M["raypend"][q], M["open"][q]
        if rp and o == 2:
            v *= (1 / (1 - z)) ** rp
        elif rp and o == 1:
            v *= (1 + z / (1 - z) ** 2) ** rp
        return v

    def F(b, z):
        out = np.empty(len(inc))
        for i, fac in enumerate(terms):
            prod = 1.0
            for q, js in fac:
                t = z * e(q, z)
                for j in js:
                    t *= b[j]
                prod *= 1 + t
            out[i] = prod
        return out

    def Jac(b, z):
        m = len(inc)
        Jm = np.zeros((m, m))
        for i, fac in enumerate(terms):
            vals = []
            for q, js in fac:
                t = z * e(q, z)
                for j in js:
                    t *= b[j]
                vals.append(1 + t)
            tot = np.prod(vals)
            for k, (q, js) in enumerate(fac):
                rest = tot / vals[k]
                for j in js:
                    dd = z * e(q, z)
                    for j2 in js:
                        if j2 != j:
                            dd *= b[j2]
                    Jm[i, j] += rest * dd
        return Jm

    def below(z):
        b = np.ones(len(inc))
        for _ in range(200):
            nb_ = F(b, z)
            if not np.all(np.isfinite(nb_)) or nb_.max() > 1e9:
                return False
            b = nb_
        for _ in range(80):
            g = F(b, z) - b
            if (np.abs(g) / np.maximum(1.0, np.abs(b))).max() < 1e-13:
                break
            try:
                b = b - np.linalg.solve(Jac(b, z) - np.eye(len(inc)), g)
            except np.linalg.LinAlgError:
                return False
            if not np.all(np.isfinite(b)) or b.min() < 1 - 1e-9:
                return False
        if (np.abs(F(b, z) - b) / np.maximum(1.0, np.abs(b))).max() > 1e-9:
            return False
        return max(abs(np.linalg.eigvals(Jac(b, z)))) < 1
    lo, hi = 0.0, 1.0
    for _ in range(48):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if below(mid) else (lo, mid)
    return 1 / lo


def my_growth(sizes, edges, rounds, maxj):
    import job_cap as JC
    return [c for c in JC.light_counts(sizes, edges, rounds, maxj=maxj) if isinstance(c, int)]


def growth_rate(num):
    import break_readout as BR
    rd = BR.read(num)
    return (rd or {}).get("rate"), (rd or {}).get("order"), (rd or {}).get("factors")


def regen(JOB, case):
    kind, *rest = case.split("-")
    if kind == "rand":
        n = int(rest[0])
        rng = random.Random(f"dead-cap-rand-{n}")
        ss, _ = JOB.sample_rand(n, rng, JOB.N_RAND // 11 + 1)
    else:
        k, s = int(rest[0]), int(rest[1])
        rng = random.Random(f"dead-cap-skel-{k}-{s}")
        ss, _ = JOB.sample_skel(k, rng, JOB.N_SKEL)
    return ss


def part_d4(case):
    JOB, DL = study()
    rows = []
    s = Counter()
    for sizes, e in regen(JOB, case):
        A = DL.analyse(sizes, e)
        M = my_map(sizes, e)
        if max(P["rank"] for P in A["pieces"]) != 1:
            continue
        for P in A["pieces"]:
            if P["rank"] != 1:
                continue
            nn, W = DL.one_cycle_W(A, P)
            r1 = DL.rate_of(W)
            if r1 <= 1.0:
                continue
            s["rank-1 exponential pieces"] += 1
            r4000 = DL.branch_rate(A, P)
            mp = next(Q for Q in M["pieces"] if Q["points"] == P["points"])
            rmine = my_radius(M, mp)
            num = my_growth(sizes, e, 40, 30000)
            gr, order, facs = growth_rate(num)
            row = {"knots": len(sizes), "root of W(1/x)=1 (study)": round(r1, 9), "estimator, 4,000 iterations (study)": round(r4000, 6),
                   "referee's radius of the branch system": round(rmine, 9), "referee's growth: rate of its exact recurrence": gr,
                   "recurrence order": order, "rounds grown": len(num) - 1,
                   "referee's growth: last ratio of counts": round(num[-1] / num[-2], 6) if len(num) > 2 else None}
            if s["rank-1 exponential pieces"] <= 2:
                row["estimator, 40,000 iterations (study)"] = round(DL.branch_rate(A, P, iters=40000), 6)
            s["referee's radius equals the root (1e-6)"] += abs(rmine - r1) < 1e-6
            s["estimator at 4,000 equals the root (1e-6)"] += abs(r4000 - r1) < 1e-6
            s["estimator at 4,000 below the root"] += r4000 < r1 - 1e-6
            if gr is not None:
                s["growth rate found"] += 1
                s["growth rate equals the root (1e-6)"] += abs(gr - r1) < 1e-6
            rows.append(row)
    return {"counts": dict(s), "rows": rows}


def part_r2(case):
    JOB, DL = study()
    rows = []
    s = Counter()
    for sizes, e in regen(JOB, case):
        A = DL.analyse(sizes, e)
        if max(P["rank"] for P in A["pieces"]) < 2:
            continue
        if s["starts"] >= 10:
            break
        s["starts"] += 1
        num = my_growth(sizes, e, 14, 6000)
        ex = DL.exact_counts(A, len(num) - 1)
        s["growth equals the exact counts on every round"] += num == ex
        M = my_map(sizes, e)
        best = max(my_radius(M, Q) for Q in M["pieces"] if Q["rank"] >= 2)
        est = max(DL.branch_rate(A, P) for P in A["pieces"] if P["rank"] >= 2)
        rows.append({"knots": len(sizes), "rank": max(P["rank"] for P in A["pieces"]), "rounds": len(num) - 1,
                     "equal": num == ex, "referee's radius": round(best, 7), "study's estimate": round(est, 7)})
        s["referee's radius within 1e-4 of the study's estimate"] += abs(best - est) < 1e-4
    return {"counts": dict(s), "rows": rows}


def part_th():
    e = []
    for i in range(3):
        e += [(0, 2 + i), (1, 5 + i), (2 + i, 8 + i), (5 + i, 8 + i)]
    e = [tuple(sorted(x)) for x in e]
    sizes = [3, 3] + [5] * 6 + [3] * 3
    num = my_growth(sizes, e, 13, 200000)
    M = my_map(sizes, e)
    th = [11, 12, 20, 33, 54, 92, 162, 297, 562, 1092, 2166, 4365, 8910, 18375]
    rad = max(my_radius(M, Q) for Q in M["pieces"] if Q["rank"] >= 2)
    import numpy.polynomial.polynomial as Pn
    roots = Pn.polyroots([-1, 0, 4, 4])
    z = min(r.real for r in roots if abs(r.imag) < 1e-12 and r.real > 0)
    return {"referee's growth": num, "equals the series to round 13": num == th[:len(num)],
            "pieces (rank, points, blocks)": [[P["rank"], len(P["points"]), len(P["blocks"])] for P in M["pieces"]],
            "referee's radius": rad, "1/z for 4z^3 + 4z^2 = 1": 1 / z, "knots": len(sizes), "dead knots": sum(o == 0 for o in M["open"])}


def check_profiles(M, s):
    for k in M["live"]:
        prof = tuple(sorted(len(M["blocks"][w]) for w in M["of"][k]))
        r = len(M["of"][k])
        bound = M["sizes"][k] - (M["deg"][k] - r) - (M["open"][k] - M["d"][k])
        s["live knots"] += 1
        s["profile sum within the bound"] += sum(prof) <= bound
        s["profile in Lemma 1's list"] += prof in PROFILES
    s["blocks"] += len(M["blocks"])
    s["blocks of at most five points"] += sum(len(B) <= 5 for B in M["blocks"].values())
    bl = list(M["blocks"].values())
    s["block pairs sharing two or more points"] += sum(len(a & b) >= 2 for a, b in itertools.combinations(bl, 2))


def part_pf():
    JOB, DL = study()
    import job_double as JD
    s = Counter()
    for case in [f"rand-{n:02d}" for n in range(6, 17)] + [f"skel-{k}-{t}" for k in (2, 3, 4) for t in (0, 1)]:
        for sizes, e in regen(JOB, case):
            check_profiles(my_map(sizes, e), s)
            s["starts"] += 1
    for line in open(ROOT / "runs/touch-census/results.jsonl"):
        r = json.loads(line)
        if r.get("status") != "ok":
            continue
        for a in r["result"]["arrangements"]:
            sizes, flat = a["key"]
            if JD.classify(sizes, flat) not in ("in", "one loose", "none"):
                continue
            n = len(sizes)
            edges = []
            for (i, j), m in zip(itertools.combinations(range(n), 2), flat):
                edges += [(i, j)] * m
            M = my_map(sizes, edges)
            if all(o > 0 for o in M["open"]):
                continue
            check_profiles(M, s)
            s["census starts with a dead knot"] += 1
    return dict(s)


def cases():
    only = set(PARAMS["only"].split(",")) if PARAMS.get("only") else None
    allc = [("TH", {"part": "TH"}), ("PF", {"part": "PF"})]
    for c in ["rand-07", "rand-13", "rand-16"] + [f"skel-{k}-{t}" for k in (2, 3, 4) for t in (0, 1)]:
        allc.append((f"D4-{c}", {"part": "D4", "case": c}))
    for c in [f"skel-{k}-{t}" for k in (2, 3, 4) for t in (0, 1)]:
        allc.append((f"R2-{c}", {"part": "R2", "case": c}))
    for cid, p in allc:
        if only is None or cid in only:
            yield cid, p


def run(case_id, p):
    if p["part"] == "D4":
        return part_d4(p["case"])
    if p["part"] == "R2":
        return part_r2(p["case"])
    if p["part"] == "TH":
        return part_th()
    return part_pf()
