"""Read-out of CARRY-STRANDS-20261116-001A-E001 against the frozen predictions.

python3 -B summarize.py RUN_DIR
"""

import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from longrun import load_results  # noqa: E402

OUT = os.path.join(ROOT, "artifacts", "CARRY-STRANDS-20261116-001A", "CARRY-STRANDS-20261116-001A-E001_carried")


def med(xs):
    xs = [x for x in xs if x is not None]
    return float(np.median(xs)) if xs else float("nan")


def ok(rec, key):
    return key in rec["laws"] and "cap" not in rec["laws"][key]


def main(run_dir):
    recs = load_results(run_dir)
    res = {k: v["result"] for k, v in recs.items() if v.get("status") == "ok"}
    bad = sorted(k for k, v in recs.items() if v.get("status") != "ok")
    caps = sorted(f"{k}:{law}" for k, r in res.items() for law, v in r["laws"].items() if "cap" in v)
    V, tabs = {}, {}
    V["G (in-run part)"] = {"not_ok": bad, "holds": not bad}

    rand = {}
    for k, r in res.items():
        if k.startswith("rand-"):
            rand.setdefault(r["n"], []).append(r)
    rt = {}
    q1 = q2 = True
    q1b = True
    for n in sorted(rand):
        rs = rand[n]
        eq = [r["laws"]["w2k"]["P"] == math.ceil(r["laws"]["w1"]["P"] / 2) for r in rs if ok(r, "w2k")]
        ratio = [r["laws"]["w2"]["T"] / r["laws"]["w1"]["T"] for r in rs if ok(r, "w2") and r["laws"]["w1"]["T"]]
        le = [r["laws"]["w2"]["T"] <= r["laws"]["w1"]["T"] for r in rs if ok(r, "w2")]
        gain = [r["laws"]["w2k"].get("keep_gain_fraction") for r in rs if ok(r, "w2k")]
        gb = [r["laws"]["w2k"].get("keep_gain_before") for r in rs if ok(r, "w2k")]
        ga = [r["laws"]["w2k"].get("keep_gain_after") for r in rs if ok(r, "w2k")]
        row = {"samples": len(rs), "sigma": med([r["sigma_max"] for r in rs]), "R": med([r["R"] for r in rs]),
               "P1": med([r["laws"]["w1"]["P"] for r in rs]), "T1": med([r["laws"]["w1"]["T"] for r in rs]),
               "P2_spend": med([r["laws"]["w2"]["P"] for r in rs if ok(r, "w2")]),
               "T2_spend": med([r["laws"]["w2"]["T"] for r in rs if ok(r, "w2")]),
               "P2_keep": med([r["laws"]["w2k"]["P"] for r in rs if ok(r, "w2k")]),
               "T2_keep": med([r["laws"]["w2k"]["T"] for r in rs if ok(r, "w2k")]),
               "share_P2keep_eq_ceil": float(np.mean(eq)) if eq else None,
               "share_T2_le_T1": float(np.mean(le)) if le else None,
               "median_T2_over_T1": med(ratio), "keep_gain_fraction": med(gain),
               "keep_gain_before": med(gb), "keep_gain_after": med(ga)}
        if any(ok(r, "w3") for r in rs):
            row.update({"P3_spend": med([r["laws"]["w3"]["P"] for r in rs if ok(r, "w3")]),
                        "P3_keep": med([r["laws"]["w3k"]["P"] for r in rs if ok(r, "w3k")]),
                        "T3_spend": med([r["laws"]["w3"]["T"] for r in rs if ok(r, "w3")])})
        rt[n] = row
        if n >= 256:
            q1 &= (row["share_P2keep_eq_ceil"] or 0) >= 0.75
            q2 &= (row["share_T2_le_T1"] or 0) >= 0.9
        if n >= 1024:
            q2 &= 0.8 <= row["median_T2_over_T1"] <= 0.95
        q1b &= row["keep_gain_fraction"] <= 0.10
        if n >= 512:
            q1b &= row["keep_gain_after"] > row["keep_gain_before"]
    tabs["random"] = rt
    V["Q1"] = {"holds": bool(q1)}
    V["Q1b"] = {"holds": bool(q1b)}
    V["Q2"] = {"holds": bool(q2)}

    lay = {}
    for k, r in res.items():
        if k.startswith("lay-"):
            lay.setdefault((r["width"], r["d"]), []).append(r)
    lt = {}
    for (w, d), rs in sorted(lay.items()):
        rel = []
        for r in rs:
            if ok(r, "w2k") and r["laws"]["w1"]["P"] > 0:
                c = math.ceil(r["laws"]["w1"]["P"] / 2)
                rel.append((c - r["laws"]["w2k"]["P"]) / c)
        lt[f"w{w}-d{d}"] = {"sigma": med([r["sigma_max"] for r in rs]), "P1": med([r["laws"]["w1"]["P"] for r in rs]),
                            "P2_spend": med([r["laws"]["w2"]["P"] for r in rs if ok(r, "w2")]),
                            "P2_keep": med([r["laws"]["w2k"]["P"] for r in rs if ok(r, "w2k")]),
                            "T1": med([r["laws"]["w1"]["T"] for r in rs]),
                            "T2_keep": med([r["laws"]["w2k"]["T"] for r in rs if ok(r, "w2k")]),
                            "rel_keep_gain": med(rel),
                            "P3_keep": med([r["laws"]["w3k"]["P"] for r in rs if ok(r, "w3k")])}
    tabs["layered"] = lt
    g4, g16, g32 = (lt[f"w{w}-d32"]["rel_keep_gain"] for w in (4, 16, 32))
    V["Q3"] = {"gain_w4": g4, "gain_w16": g16, "gain_w32": g32, "holds": g4 > g32 and g16 >= g32}

    nar = [r for k, r in res.items() if k.startswith("narrow-")]
    nb = [(r["width"], r["d"], r["laws"][f"w{2 * r['width']}k"].get("P")) for r in nar]
    V["Q3b"] = {"values": nb, "holds": all(P is not None and P <= 1 for _, _, P in nb)}

    pyr = {k: r for k, r in res.items() if k.startswith("pyramid-")}
    q4, pv = True, {}
    for k, r in sorted(pyr.items()):
        h = int(k.split("-")[1])
        for w in range(1, 5):
            ks, kk = f"w{w}", f"w{w}k"
            if not ok(r, ks):
                continue
            ps = r["laws"][ks]["P"]
            pk = r["laws"][kk]["P"] if w > 1 and ok(r, kk) else ps
            ts = r["laws"][ks]["T"]
            tk = r["laws"][kk]["T"] if w > 1 and ok(r, kk) else ts
            pv[f"h{h}-w{w}"] = [ps, pk, ts, tk]
            q4 &= ps == pk == math.ceil(h / w) and ts == tk
    V["Q4"] = {"values": pv, "holds": bool(q4)}

    sub = {k: r for k, r in res.items() if k.startswith("subtree-")}
    sv = {k: {law: r["laws"][law]["T"] for law in r["laws"] if "cap" not in r["laws"][law]} for k, r in sub.items()}
    a4, a6 = sv.get("subtree-d4-l16", {}), sv.get("subtree-d6-l16", {})
    V["Q5"] = {"values": sv, "holds": bool(a4 and a6 and a4["w2"] < a4["w1"] and a6["w2"] < a6["w1"] and a4["w3"] < a4["w2"])}

    tabs["structured"] = {k: r for k, r in res.items() if k.split("-")[0] in ("ladder", "pyramid", "subtree")}
    unl = {}
    for k, r in res.items():
        if k.startswith("unl-"):
            unl.setdefault(k.split("-")[1], []).append(r)
    tabs["unlayered"] = {g: {"sigma": med([r["sigma_max"] for r in rs]), "P1": med([r["laws"]["w1"]["P"] for r in rs]),
                             "P2_keep": med([r["laws"]["w2k"]["P"] for r in rs if ok(r, "w2k")])} for g, rs in unl.items()}
    out = {"cases_ok": len(res), "not_ok": bad, "capped": caps, "verdicts": V, "tables": tabs}
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "summary.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True, default=str)
    for k, v in V.items():
        print(k, "HOLDS" if v["holds"] else "FAILS", {x: y for x, y in v.items() if x not in ("holds", "values")})
    print("capped:", caps)


if __name__ == "__main__":
    main(sys.argv[1])
