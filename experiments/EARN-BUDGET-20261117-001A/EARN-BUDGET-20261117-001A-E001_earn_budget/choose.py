"""Choices between stages of EARN-BUDGET-20261117-001A, by the frozen scores.

  python3 choose.py retune <R1 dir> <retuned.json>     best NOV and PS per cell: least mean log charged work over
                                                        8 instances x 3 runs; an unsolved run scores log(work at the cap)
                                                        + log(1 + least violated count)
  python3 choose.py policy <P1 dir> <policies.json>    score of a setting on a pattern: the mean over 8 instances x 3 runs
                                                        of log(W_setting) - log(W_NOV) from the same initial state.
                                                        E, Gb, Gm, ST: least mean over rand-800, block-800, local-w10-800;
                                                        Erb: least mean over rand-800 and block-800 (earned grid).
                                                        Tie rule for E, Erb and Gb: among settings within 0.01 of the best,
                                                        the first in grid order, which is the most eager (smallest theta,
                                                        then largest rho_max, largest rho_min, smallest rb; for Gb largest
                                                        rho, then smallest rb). ErbL: Erb's score with the opposite tie rule
                                                        (the last, most lazy, within 0.01). Gm and ST: the least score.
  python3 choose.py oracle <O1 dir> <oracle_policies.json>   GbO per test cell: the fixed batched setting of least mean
                                                        paired score on that cell's tuning instances
  python3 choose.py retune12800 <R2 dir> <retuned12800.json>  NOV and PS per stress cell over the neighbourhood tried
"""
from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "scripts"))
from longrun import load_results  # noqa: E402

import job  # noqa: E402


def score(run):
    s = math.log(run["work"])
    if not run["solved"]:
        s += math.log1p(max(0, run.get("minviol", 0)))
    return s


def ok_records(d):
    recs = load_results(d)
    bad = [k for k, r in recs.items() if r.get("status") != "ok"]
    if bad:
        raise SystemExit(f"{len(bad)} cases not ok, e.g. {bad[:3]}")
    return {k: r["result"] for k, r in recs.items()}


def retune(d, out):
    res = ok_records(d)
    acc = defaultdict(list)
    for r in res.values():
        tag = "NOV" if r["algo"] == "novelty_plus" else "PS"
        for run in r["runs"]:
            acc[(r["cell"], tag, tuple(r["prm"]))].append(score(run))
    choice, table = {}, {}
    for name, *_ in job.CELLS + job.TUNE_CELLS:
        choice[name], table[name] = {}, {}
        for tag, grid in (("NOV", job.NOV_GRID), ("PS", job.PS_GRID)):
            rows = {prm: sum(v) / len(v) for (c, t, prm), v in acc.items() if c == name and t == tag}
            assert len(rows) == len(grid) and all(len(acc[(name, tag, p)]) == 24 for p in rows), (name, tag)
            best = min(rows, key=rows.get)
            choice[name][tag] = list(best)
            table[name][tag] = {str(list(p)): round(v, 4) for p, v in sorted(rows.items(), key=lambda kv: kv[1])}
            edge = (tag == "NOV" and (best[0] in (0.5, 0.9) or best[1] in (0.0, 0.1))) or \
                   (tag == "PS" and best[0] in (0.6, 3.0))
            if edge:
                print(f"note: {name} {tag} best {best} sits on a grid edge")
    Path(out).write_text(json.dumps({**choice, "_scores": table}, indent=1))
    for name in choice:
        print(name, choice[name])


def pick(scores, tie, lazy=False):
    best = min(scores.values())
    if not tie:
        return min(scores, key=scores.get)
    near = [k for k, v in scores.items() if v <= best + 0.01]
    return max(near) if lazy else min(near)


def policy(d, out):
    res = ok_records(d)
    base = {(r["cell"], r["seed"], j): score(run) for r in res.values() if r["grid"] == "base"
            for j, run in enumerate(r["runs"])}
    acc = defaultdict(lambda: defaultdict(list))
    for r in res.values():
        if r["grid"] != "base":
            for j, run in enumerate(r["runs"]):
                acc[(r["grid"], r["k"])][r["cell"]].append(score(run) - base[(r["cell"], r["seed"], j)])
    pat = {}
    for key, cells in acc.items():
        assert all(len(v) == 24 for v in cells.values()) and len(cells) == 3, key
        pat[key] = {c: sum(v) / len(v) for c, v in cells.items()}
    three = ("rand-800", "block-800", "local-w10-800")
    two = ("rand-800", "block-800")

    def sc(g, cells):
        return {k: sum(pat[(g, k)][c] for c in cells) / len(cells) for (gg, k) in pat if gg == g}

    s_e, s_erb, s_gb, s_gm, s_st = sc("earn", three), sc("earn", two), sc("fixb", three), sc("sl", three), sc("st", three)
    k = {"E": pick(s_e, True), "Erb": pick(s_erb, True), "ErbL": pick(s_erb, True, lazy=True), "Gb": pick(s_gb, True),
         "Gm": pick(s_gm, False), "ST": pick(s_st, False)}
    grid_of = {"E": "earn", "Erb": "earn", "ErbL": "earn", "Gb": "fixb", "Gm": "sl", "ST": "st"}
    score_of = {"E": s_e, "Erb": s_erb, "ErbL": s_erb, "Gb": s_gb, "Gm": s_gm, "ST": s_st}
    outd = {a: job.GRIDS[grid_of[a]][k[a]] for a in k}
    outd["_k"] = k
    outd["_chosen_scores"] = {a: round(score_of[a][k[a]], 4) for a in k}
    outd["_per_pattern"] = {f"{g}{kk}": {c: round(v, 4) for c, v in cells.items()} for (g, kk), cells in sorted(pat.items())}
    Path(out).write_text(json.dumps(outd, indent=1))
    for a in k:
        print(a, k[a], outd[a], outd["_chosen_scores"][a], {c: round(pat[(grid_of[a], k[a])][c], 3) for c in three})


def oracle(d, out):
    res = ok_records(d)
    base = {(r["cell"], r["seed"], j): score(run) for r in res.values() if r["grid"] == "base"
            for j, run in enumerate(r["runs"])}
    acc = defaultdict(list)
    for r in res.values():
        if r["grid"] != "base":
            for j, run in enumerate(r["runs"]):
                acc[(r["cell"], r["k"])].append(score(run) - base[(r["cell"], r["seed"], j)])
    outd, sc = {}, {}
    for name, *_ in job.CELLS:
        rows = {k: sum(v) / len(v) for (c, k), v in acc.items() if c == name}
        assert len(rows) == len(job.FIXB_GRID) and all(len(acc[(name, k)]) == 24 for k in rows), name
        k = min(rows, key=rows.get)
        outd[name] = job.FIXB_GRID[k]
        sc[name] = {"k": k, "score": round(rows[k], 4)}
        print(name, k, job.FIXB_GRID[k], round(rows[k], 4))
    outd["_chosen"] = sc
    Path(out).write_text(json.dumps(outd, indent=1))


def retune12800(d, out):
    res = ok_records(d)
    acc = defaultdict(list)
    for r in res.values():
        tag = "NOV" if r["algo"] == "novelty_plus" else "PS"
        for run in r["runs"]:
            acc[(r["cell"], tag, tuple(r["prm"]))].append(score(run))
    outd = {}
    for name, *_ in job.STRESS_CELLS:
        outd[name] = {}
        for tag in ("NOV", "PS"):
            rows = {prm: sum(v) / len(v) for (c, t, prm), v in acc.items() if c == name and t == tag}
            outd[name][tag] = list(min(rows, key=rows.get))
            outd[name]["_" + tag] = {str(list(p)): round(v, 4) for p, v in sorted(rows.items(), key=lambda kv: kv[1])}
        print(name, outd[name]["NOV"], outd[name]["PS"])
    Path(out).write_text(json.dumps(outd, indent=1))


if __name__ == "__main__":
    {"retune": retune, "policy": policy, "oracle": oracle, "retune12800": retune12800}[sys.argv[1]](sys.argv[2],
                                                                                                    sys.argv[3])
