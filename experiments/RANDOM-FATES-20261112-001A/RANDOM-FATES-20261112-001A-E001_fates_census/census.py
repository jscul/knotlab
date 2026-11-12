"""The frozen census of RANDOM-FATES-20261112-001A-E001 (contract.json beside this file): outcomes of random meeting patterns
under the not-all-equal law, and what the law reads off them.

Parts (frozen):
  U   uniform knots on n = 50, 100, 200, 300 distinctions, added one at a time until no state is allowed (200 runs each for
      n <= 200, 60 at 300): the death knot count m*, a minimal contradiction (every run for n <= 200, the first 5 at 300); for the
      first 30 runs of each n, readings at f = 0.5, 0.75, 0.9 of m* and at k = 1, 10, 50 knots before the death knot (full),
      and at k = 2, 3, 5, 20 (tie classes only). k = 1 is the last base.
  G   growth processes to a horizon of 2,000 moves, 100 runs each: X(q) q in {0.1, 0.2, 0.3, 0.35, 0.5}; O global q in {0,
      0.05, 0.1, 0.2, 0.3}; O local q in {0.05, 0.1, 0.2, 0.3}; L(w, q) w in {4, 5, 6}, q in {0.3, 0.5, 0.7}: fate, steps and
      distinctions at the end, a minimal contradiction of every growth that ended; for the first 30 runs, readings at the horizon
      (still a base) or
      at k = 1, 10, 50 before the death knot (full) and k = 2, 3, 5, 20 (tie classes only).
  T   the control with no cycle of knots: 30 runs of 300 moves, read in full at the end.

Run from the repository root:
    .venv/bin/python -B experiments/RANDOM-FATES-20261112-001A/RANDOM-FATES-20261112-001A-E001_fates_census/census.py [--workers 10]
    .venv/bin/python -B experiments/RANDOM-FATES-20261112-001A/RANDOM-FATES-20261112-001A-E001_fates_census/census.py --summary
Output: artifacts/RANDOM-FATES-20261112-001A/RANDOM-FATES-20261112-001A-E001_fates_census/runs.jsonl (one line per run,
written as it finishes; a rerun skips runs already written), summary.json and census_log.txt.
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import sys
import time
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import fates as F  # noqa: E402

OUT = os.path.join(ROOT, "artifacts", "RANDOM-FATES-20261112-001A", "RANDOM-FATES-20261112-001A-E001_fates_census")
if "--out" in sys.argv:
    OUT = sys.argv[sys.argv.index("--out") + 1]
RUNS = os.path.join(OUT, "runs.jsonl")

# Frozen parameters (contract.json, "definitions")
U_SIZES = {50: 200, 100: 200, 200: 200, 300: 60}
U_CORES = {50: 200, 100: 200, 200: 200, 300: 5}
READ_RUNS = 30
F_FULL = (0.5, 0.75, 0.9)
K_FULL = (1, 10, 50)
K_TIES = (2, 3, 5, 20)
HORIZON = 2000
G_RUNS = 100
SETTINGS = ([("X", q) for q in (0.1, 0.2, 0.3, 0.35, 0.5)]
            + [("Og", q) for q in (0.0, 0.05, 0.1, 0.2, 0.3)]
            + [("Ol", q) for q in (0.05, 0.1, 0.2, 0.3)]
            + [("L", (w, q)) for w in (4, 5, 6) for q in (0.3, 0.5, 0.7)])
T_RUNS, T_STEPS = 30, 300


def seed_of(*parts):
    return int(hashlib.sha256(":".join(map(str, parts)).encode()).hexdigest()[:12], 16)


def label(kind, p):
    if kind == "L":
        return f"L{p[0]}_{p[1]}"
    return f"{kind}{p}"


def make_gen(kind, p, rng, n=None):
    if kind == "U":
        return F.proc_uniform(n, rng)
    if kind == "X":
        return F.proc_expand(p, rng)
    if kind == "Og":
        return F.proc_overlap(p, rng, local=False)
    if kind == "Ol":
        return F.proc_overlap(p, rng, local=True)
    if kind == "L":
        return F.proc_band(p[0], p[1], rng)
    if kind == "T":
        return F.proc_tree(rng)
    raise ValueError(kind)


def core_info(knots):
    core = F.death_core(knots)
    cv = sorted({v for t in core for v in t})
    return {"core_knots": len(core), "core_distinctions": len(cv), "core_index_span": cv[-1] - cv[0],
            "core_has_killer": knots[-1] in core}


def killer_check(n, base, killer, rng, seed):
    """The last base must tie the killing knot's three distinctions equal (by definition): a check of the code."""
    rd = F.Reader(n, base, samples=50, seed=seed)
    classes = rd.tie_classes()
    rd.close()
    for c in classes:
        mem = dict(c)
        if all(v in mem for v in killer):
            rel = {mem[v] for v in killer}
            return len(rel) == 1
    return False


def task(spec):
    kind, p, run = spec
    t0 = time.time()
    lab = "U" + str(p) if kind == "U" else ("T" if kind == "T" else label(kind, p))
    rng = random.Random(seed_of(lab, run, "grow"))
    rrng = random.Random(seed_of(lab, run, "read"))
    rec = {"label": lab, "kind": kind, "param": p, "run": run}
    if kind == "U":
        n = p
        knots, dead = F.grow(make_gen("U", None, rng, n=n), 50 * n)
        assert dead
        rec.update({"dead": True, "death_knot": len(knots), "density": len(knots) / n})
        if run < U_CORES[n]:
            rec.update(core_info(knots))
        if run < READ_RUNS:
            M = len(knots)
            reads = {}
            for f in F_FULL:
                m = int(round(f * M))
                reads[f"f{f}"] = F.read_base(n, knots[:m], rrng, full=True, seed=run)
            for k in K_FULL + K_TIES:
                if M - k >= 1:
                    reads[f"k{k}"] = F.read_base(n, knots[:M - k], rrng, full=(k in K_FULL), seed=run)
            rec["reads"] = reads
            rec["killer_tied_equal"] = killer_check(n, knots[:-1], knots[-1], rrng, run)
    elif kind == "T":
        knots, dead = F.grow(make_gen("T", None, rng), T_STEPS)
        n = max(v for t in knots for v in t) + 1
        rec.update({"dead": dead, "knots": len(knots), "n": n})
        rec["reads"] = {"end": F.read_base(n, knots, rrng, full=True, seed=run)}
    else:
        knots, dead = F.grow(make_gen(kind, p, rng), HORIZON)
        n = max(v for t in knots for v in t) + 1
        rec.update({"dead": dead, "knots": len(knots), "n": n})
        if dead:
            rec.update(core_info(knots))
            rec["n_at_death"] = len({v for t in knots[:-1] for v in t})
        if run < READ_RUNS:
            reads = {}
            if not dead:
                reads["end"] = F.read_base(n, knots, rrng, full=True, seed=run)
            else:
                M = len(knots)
                for k in K_FULL + K_TIES:
                    if M - k >= 1:
                        reads[f"k{k}"] = F.read_base(n, knots[:M - k], rrng, full=(k in K_FULL), seed=run)
                rec["killer_tied_equal"] = killer_check(n, knots[:-1], knots[-1], rrng, run)
            rec["reads"] = reads
    rec["seconds"] = round(time.time() - t0, 2)
    return rec


def all_specs():
    specs = []
    for n, runs in U_SIZES.items():
        specs += [("U", n, r) for r in range(runs)]
    for kind, p in SETTINGS:
        specs += [(kind, p, r) for r in range(G_RUNS)]
    specs += [("T", None, r) for r in range(T_RUNS)]
    return specs


def log(*a):
    msg = " ".join(str(x) for x in a)
    print(msg, flush=True)
    with open(os.path.join(OUT, "census_log.txt"), "a") as f:
        f.write(msg + "\n")


def run(workers):
    os.makedirs(OUT, exist_ok=True)
    done = set()
    if os.path.exists(RUNS):
        with open(RUNS) as f:
            for line in f:
                r = json.loads(line)
                done.add((r["label"], r["run"]))
    specs = []
    for kind, p, r in all_specs():
        lab = "U" + str(p) if kind == "U" else ("T" if kind == "T" else label(kind, p))
        if (lab, r) not in done:
            specs.append((kind, p, r))
    # read-heavy runs first, largest first, so the long ones start early
    specs.sort(key=lambda s: (s[2] >= READ_RUNS, -(s[1] if s[0] == "U" else 0)))
    log(f"start {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())} UTC: {len(specs)} runs to do, {len(done)} already written")
    t0 = time.time()
    with Pool(workers) as pool, open(RUNS, "a") as f:
        for i, rec in enumerate(pool.imap_unordered(task, specs, chunksize=1)):
            f.write(json.dumps(rec) + "\n")
            f.flush()
            if (i + 1) % 100 == 0:
                log(f"{i + 1}/{len(specs)} runs, {time.time() - t0:.0f} s")
    log(f"done {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())} UTC, {time.time() - t0:.0f} s")


# ----------------------------------------------------------------------------------------------------------------------
# The frozen evaluation.
# ----------------------------------------------------------------------------------------------------------------------

def load():
    recs = []
    with open(RUNS) as f:
        for line in f:
            recs.append(json.loads(line))
    return recs


def frac(xs):
    xs = list(xs)
    return (sum(1 for x in xs if x) / len(xs)) if xs else None


def prof_shares(reads, d):
    """Over the sampled pairs at d steps in the given readings: shares with least bond d + 2 (ruler), below (shortcut), none."""
    sizes = [s for r in reads for (_, _, s, _) in r.get("bond_profile", {}).get(str(d), [])]
    if not sizes:
        return {"pairs": 0}
    return {"pairs": len(sizes), "ruler": frac(s == d + 2 for s in sizes),
            "shortcut": frac(s is not None and s < d + 2 for s in sizes), "none": frac(s is None for s in sizes),
            "sizes": {str(k): sum(1 for s in sizes if s == k) for k in sorted({s for s in sizes if s is not None})}}


def lfrac(r):
    return r["largest_class"] / max(1, r["n_used"])


def spearman(x, y):
    if len(x) < 3:
        return None
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    if rx.std() == 0 or ry.std() == 0:
        return 0.0
    return float(np.corrcoef(rx, ry)[0, 1])


def summarize():
    recs = load()
    by = {}
    for r in recs:
        by.setdefault(r["label"], []).append(r)
    S = {"runs": len(recs), "settings": {}}
    for lab, rs in sorted(by.items()):
        rs.sort(key=lambda r: r["run"])
        e = {"runs": len(rs), "dead": sum(1 for r in rs if r["dead"])}
        if lab.startswith("U"):
            dens = [r["density"] for r in rs]
            e["death_density"] = {"median": float(np.median(dens)), "q10": float(np.quantile(dens, 0.1)),
                                  "q90": float(np.quantile(dens, 0.9))}
        else:
            e["alive_fraction"] = 1 - e["dead"] / len(rs)
            life = [r["knots"] for r in rs if r["dead"]]
            if life:
                e["knots_at_death"] = {"median": float(np.median(life)), "min": min(life), "max": max(life)}
        cores = [r for r in rs if "core_knots" in r]
        if cores:
            e["core"] = {"knots_median": float(np.median([r["core_knots"] for r in cores])),
                         "distinctions_median": float(np.median([r["core_distinctions"] for r in cores])),
                         "index_span_median": float(np.median([r["core_index_span"] for r in cores])),
                         "share_le20_knots_span20": frac(r["core_knots"] <= 20 and r["core_index_span"] <= 20 for r in cores)}
            if lab.startswith("U"):
                e["core"]["over_death_knot_median"] = float(np.median([r["core_knots"] / r["death_knot"] for r in cores]))
        read = [r for r in rs if "reads" in r]
        pts = {}
        for key in sorted({k for r in read for k in r["reads"]}):
            rr = [r["reads"][key] for r in read if key in r["reads"] and r["reads"][key].get("state")]
            if not rr:
                continue
            p = {"bases": len(rr), "largest_class_frac_median": float(np.median([lfrac(x) for x in rr])),
                 "largest_class_median": float(np.median([x["largest_class"] for x in rr])),
                 "tie_free_share": frac(x["tied_pairs"] == 0 for x in rr),
                 "tie_reach_median": float(np.median([x["tie_reach"] for x in rr])),
                 "tie_reach_le8_share": frac(x["tie_reach"] <= 8 for x in rr),
                 "max_knots_on_pair_median": float(np.median([x["max_knots_on_pair"] for x in rr])),
                 "n_used_median": float(np.median([x["n_used"] for x in rr]))}
            if any("bond_profile" in x for x in rr):
                p["profile"] = {str(d): prof_shares(rr, d) for d in (1, 2, 3)}
                b = [x["step_balls"] for x in rr if "step_balls" in x]
                p["ball_B3_over_B1_median"] = float(np.median([bb[2] / bb[0] for x in b for bb in x if bb[0]]))
                p["ball_B6_median"] = float(np.median([bb[5] for x in b for bb in x]))
            if any("faithful" in x for x in rr):
                p["faithful_share"] = frac(x.get("faithful") for x in rr if "faithful" in x)
            pts[key] = p
        e["readings"] = pts
        kt = [r["killer_tied_equal"] for r in read if "killer_tied_equal" in r]
        if kt:
            e["killer_tied_equal_all"] = all(kt)
        S["settings"][lab] = e
    P = {}
    st = S["settings"]
    # P1
    ok = True
    detail = {}
    for n in (100, 200, 300):
        for f in ("f0.5", "f0.75"):
            p = st[f"U{n}"]["readings"][f]
            detail[f"U{n} {f}"] = {"tie_free": p["tie_free_share"],
                                   **{f"ruler d={d}": p["profile"][str(d)]["ruler"] for d in (1, 2, 3)}}
            ok &= p["tie_free_share"] >= 0.9 and all(p["profile"][str(d)]["ruler"] >= 0.95 for d in (1, 2, 3))
    P["P1"] = {"holds": ok, "detail": detail}
    # P2
    a = all(frac(lfrac(r["reads"]["k50"]) <= 0.05 for r in by[f"U{n}"] if "reads" in r and "k50" in r["reads"]) >= 0.9
            for n in (50, 100, 200, 300))
    b = all(st[f"U{n}"]["readings"]["k1"]["largest_class_frac_median"] >= 0.4 for n in (100, 200, 300))
    c_detail = {}
    c = True
    for k in (1, 5, 10, 20):
        x100 = st["U100"]["readings"][f"k{k}"]["largest_class_frac_median"]
        x300 = st["U300"]["readings"][f"k{k}"]["largest_class_frac_median"]
        c_detail[f"k{k}"] = [x100, x300]
        c &= (x100 <= 0.05 and x300 <= 0.05) or (x100 > 0 and 0.5 <= x300 / x100 <= 2)
    P["P2"] = {"a": a, "b": b, "c": c, "c_detail": c_detail}
    # P3
    P["P3"] = {"holds": all(st[f"U{n}"]["core"]["over_death_knot_median"] >= 0.5 for n in (100, 200)),
               "detail": {f"U{n}": st[f"U{n}"]["core"]["over_death_knot_median"] for n in (50, 100, 200, 300)}}
    # P4
    lab = lambda k, p: label(k, p)
    P["P4"] = {
        "a": all(st[x]["alive_fraction"] == 1.0 for x in ("L4_0.3", "L4_0.5", "L4_0.7", "Og0.0")),
        "b": all(st[f"L{w}_{q}"]["alive_fraction"] <= 0.1 for w in (5, 6) for q in (0.5, 0.7)),
        "c": all(st[f"X{q}"]["alive_fraction"] >= 0.8 for q in (0.1, 0.2))
        and all(st[f"X{q}"]["alive_fraction"] <= 0.2 for q in (0.35, 0.5)),
        "d": st["Og0.3"]["alive_fraction"] <= 0.2 and st["Ol0.3"]["alive_fraction"] <= 0.2,
        "alive": {x: st[x].get("alive_fraction") for x in st if not x.startswith("U") and x != "T"}}
    # P5
    Lrecs = [r for x in by for r in by[x] if x.startswith(("L5", "L6")) and r["dead"]]
    a5 = frac(r["core_knots"] <= 20 and r["core_index_span"] <= 20 for r in Lrecs) >= 0.9 if Lrecs else None
    Lread = [r for r in Lrecs if "reads" in r and "k1" in r["reads"]]
    big = [r["reads"]["k1"]["largest_class"] for r in Lread]
    age = [r["n_at_death"] for r in Lread]
    rho = spearman(age, big)
    b5 = (frac(x <= 40 for x in big) >= 0.9 and rho is not None and rho < 0.3) if big else None
    XO = [r for x in by for r in by[x] if x.startswith(("X", "Og", "Ol")) and r["dead"] and "reads" in r and "k1" in r["reads"]]
    c5 = frac(lfrac(r["reads"]["k1"]) >= 0.1 for r in XO) >= 0.7 if XO else None
    P["P5"] = {"a": a5, "b": b5, "c": c5, "rho_age_largest": rho, "L_last_bases": len(big), "XO_last_bases": len(XO),
               "XO_share_ge_0.1": frac(lfrac(r["reads"]["k1"]) >= 0.1 for r in XO) if XO else None}
    # P6
    ok6, d6 = True, {}
    for x in ("X0.1", "X0.2", "Og0.0", "Og0.05", "Og0.1"):
        p = st[x]["readings"].get("end")
        if not p:
            ok6 = False
            continue
        d6[x] = {**{f"ruler d={d}": p["profile"][str(d)]["ruler"] for d in (1, 2, 3)}, "B3/B1": p["ball_B3_over_B1_median"]}
        ok6 &= all(p["profile"][str(d)]["ruler"] >= 0.9 for d in (1, 2, 3)) and p["ball_B3_over_B1_median"] >= 9
    P["P6"] = {"holds": ok6, "detail": d6}
    # P7
    d7 = {}
    a7 = b7 = c7 = True
    for x in ("L4_0.5", "L4_0.7"):
        rr = [r["reads"]["end"] for r in by[x] if "reads" in r and "end" in r["reads"]]
        sizes = [(int(d), s) for q in rr for d in ("2", "3") for (_, _, s, _) in q["bond_profile"][d]]
        sc = frac(s is not None and s < d + 2 for d, s in sizes)
        tr = frac(q["tie_reach"] <= 8 for q in rr)
        b6 = float(np.median([bb[5] for q in rr for bb in q["step_balls"]]))
        d7[x] = {"shortcut_share_d23": sc, "tie_reach_le8": tr, "B6_median": b6}
        a7 &= sc >= 0.3
        b7 &= tr >= 0.9
        c7 &= b6 <= 60
    P["P7"] = {"a": a7, "b": b7, "c": c7, "detail": d7}
    # controls
    t = st["T"]["readings"]["end"]
    P["C1_killer_tied_equal"] = all(e.get("killer_tied_equal_all", True) for e in st.values())
    P["C2_tree_ruler"] = {"holds": t["tie_free_share"] == 1.0 and all(t["profile"][str(d)]["ruler"] == 1.0 for d in (1, 2, 3)),
                          "profile": t["profile"]}
    S["predictions"] = P
    with open(os.path.join(OUT, "summary.json"), "w") as f:
        json.dump(S, f, indent=1, sort_keys=True)
    print(json.dumps(P, indent=1, sort_keys=True))


if __name__ == "__main__":
    if "--summary" in sys.argv:
        summarize()
    elif "--task" in sys.argv:          # one run, for timing and checks: --task KIND PARAM RUN
        i = sys.argv.index("--task")
        kind, p, r = sys.argv[i + 1], sys.argv[i + 2], int(sys.argv[i + 3])
        p = None if p == "None" else (int(p) if kind == "U" else (tuple(json.loads(p)) if kind == "L" else float(p)))
        print(json.dumps(task((kind, p, r)))[:3000])
    else:
        w = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 10
        run(w)
