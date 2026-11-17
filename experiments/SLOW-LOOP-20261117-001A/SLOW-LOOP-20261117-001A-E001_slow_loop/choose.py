"""Choices between stages of SLOW-LOOP-20261117-001A, by the frozen scores.

  python3 choose.py retune <S1 dir>[,<S1b dir>] <retuned.json>
                                                        best NOV and PS per cell: least mean log charged work over
                                                        8 instances x 3 runs; an unsolved run scores log(work at the
                                                        cap) + log(1 + least violated count)
  python3 choose.py policy <S2 dir> <policies.json>    G: least mean over rand-800 and block-800 of each pattern's
                                                        mean paired log(W_setting) - log(W_NOV); GO: the same on
                                                        local-w10-800; ST: the static settings, scored as G
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
        s += math.log1p(run.get("minviol", 0))
    return s


def ok_records(d):
    recs = {}
    for one in d.split(","):
        recs.update(load_results(one))
    bad = [k for k, r in recs.items() if r.get("status") != "ok"]
    if bad:
        raise SystemExit(f"{len(bad)} cases not ok, e.g. {bad[:3]}")
    return {k: r["result"] for k, r in recs.items()}


def retune(d, out):
    res = ok_records(d)
    acc = defaultdict(list)
    for k, r in res.items():
        tag = "NOV" if r["algo"] == "novelty_plus" else "PS"
        for run in r["runs"]:
            acc[(r["cell"], tag, tuple(r["prm"]))].append(score(run))
    choice, table = {}, {}
    for name, *_ in job.CELLS:
        choice[name] = {}
        table[name] = {}
        for tag in ("NOV", "PS"):
            rows = {prm: sum(v) / len(v) for (c, t, prm), v in acc.items() if c == name and t == tag}
            want = (30 + (len(job.NOV_EXT) if name in job.EXT_NOV_CELLS and "," in d else 0)) if tag == "NOV" else \
                (8 + (len(job.PS_EXT) if name in job.EXT_PS_CELLS and "," in d else 0))
            assert len(rows) == want and all(len(acc[(name, tag, p)]) == 24 for p in rows), (name, tag, len(rows), want)
            best = min(rows, key=rows.get)
            choice[name][tag] = list(best)
            table[name][tag] = {str(list(p)): round(v, 4) for p, v in sorted(rows.items(), key=lambda kv: kv[1])}
    Path(out).write_text(json.dumps({**choice, "_scores": table}, indent=1))
    for name in choice:
        if not name.startswith("_"):
            print(name, choice[name])


def policy(d, out):
    res = ok_records(d)
    base = {}
    for k, r in res.items():
        if r["k"] < 0:
            for j, run in enumerate(r["runs"]):
                base[(r["cell"], r["seed"], j)] = score(run)
    acc = defaultdict(lambda: defaultdict(list))
    for k, r in res.items():
        if r["k"] >= 0:
            key = ("st", r["k"]) if r.get("static") else r["k"]
            for j, run in enumerate(r["runs"]):
                acc[key][r["cell"]].append(score(run) - base[(r["cell"], r["seed"], j)])
    pat = defaultdict(dict)
    for k, cells in acc.items():
        for c, v in cells.items():
            assert len(v) == 24
            pat[k][c] = sum(v) / len(v)
    dyn = [k for k in pat if not isinstance(k, tuple)]
    sta = [k for k in pat if isinstance(k, tuple)]
    assert len(dyn) == len(job.POLICY_GRID) and len(sta) == len(job.STATIC_GRID)
    g = {k: (pat[k]["rand-800"] + pat[k]["block-800"]) / 2 for k in dyn}
    go = {k: pat[k]["local-w10-800"] for k in dyn}
    st = {k: (pat[k]["rand-800"] + pat[k]["block-800"]) / 2 for k in sta}
    kg, kgo, kst = min(g, key=g.get), min(go, key=go.get), min(st, key=st.get)
    out_d = {"G": job.POLICY_GRID[kg], "GO": job.POLICY_GRID[kgo], "ST": job.STATIC_GRID[kst[1]],
             "_k": {"G": kg, "GO": kgo, "ST": kst[1]},
             "_scores": {str(k): {"G": round(g[k], 4), "GO": round(go[k], 4), **{c: round(v, 4) for c, v in pat[k].items()}}
                         for k in sorted(dyn)},
             "_static_scores": {str(k[1]): {"ST": round(st[k], 4), **{c: round(v, 4) for c, v in pat[k].items()}}
                                for k in sorted(sta)}}
    Path(out).write_text(json.dumps(out_d, indent=1))
    print("G", kg, job.POLICY_GRID[kg], round(g[kg], 4), "| GO", kgo, job.POLICY_GRID[kgo], round(go[kgo], 4),
          "| ST", kst[1], job.STATIC_GRID[kst[1]], round(st[kst], 4))


def posthoc(d, out):
    """STO (post hoc, not frozen): the static setting least in mean paired log(W_setting) - log(W_NOV) on local-w10-800"""
    res = ok_records(d)
    base = {(r["seed"], j): score(run) for r in res.values() if r["k"] < 0 for j, run in enumerate(r["runs"])}
    acc = defaultdict(list)
    for r in res.values():
        if r["k"] >= 0:
            for j, run in enumerate(r["runs"]):
                acc[r["k"]].append(score(run) - base[(r["seed"], j)])
    assert len(acc) == len(job.STATIC_GRID) and all(len(v) == 24 for v in acc.values())
    sc = {k: sum(v) / len(v) for k, v in acc.items()}
    k = min(sc, key=sc.get)
    Path(out).write_text(json.dumps({"STO": job.STATIC_GRID[k], "_k": k, "_scores": {str(a): round(b, 4) for a, b in
                                                                                       sorted(sc.items())}}, indent=1))
    print("STO", k, job.STATIC_GRID[k], round(sc[k], 4))


if __name__ == "__main__":
    {"retune": retune, "policy": policy, "posthoc": posthoc}[sys.argv[1]](sys.argv[2], sys.argv[3])
