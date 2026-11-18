"""Score the frozen predictions of research/COUNT-BALLS-20261118-001/preregistration.md from the run's parts."""
import json
import math
from pathlib import Path

import numpy as np

A_LIT = 0.6322260804          # the literature's amplitude as the advisor gave it (Stephenson 1970), registered in W4
BALL_CONST = 2 * math.pi / (3 * math.sqrt(3))   # own-class density 2/(3 sqrt3) times pi; ball = BALL_CONST a^4 u^-4


def load(art, name):
    p = art / "parts" / f"{name}.json"
    return json.load(open(p))["result"] if p.exists() else None


def score_weave(rays, scan, pred):
    row = rays["row (0 deg)"]
    r = np.array([p["r"] for p in row])
    A = np.array([math.sqrt(p["r"]) * float(p["C"]) for p in row])
    sel = r >= 30
    X = np.stack([np.ones(sel.sum()), 1 / r[sel] ** 2], axis=1)
    coef, *_ = np.linalg.lstsq(X, A[sel], rcond=None)
    a_inf, c2 = coef
    a_row = lambda x: a_inf * (1 + c2 / a_inf / x ** 2)
    out = {"a_row_fit": a_inf, "c2_row": c2 / a_inf}
    devs = {}
    for name in ("(4,1) (10.9 deg)", "(5,2) (16.1 deg)", "(1,1) (30 deg)"):
        pts = rays[name]
        rr = np.array([p["r"] for p in pts])
        AA = np.array([math.sqrt(p["r"]) * float(p["C"]) for p in pts])
        dev = AA / a_row(rr) - 1
        mid = int(np.argmin(abs(rr - rr[-1] / 2)))
        devs[name] = {"r_max": rr[-1], "dev_max": dev[-1], "r_mid": rr[mid], "dev_mid": dev[mid],
                      "dev_r2_max": dev[-1] * rr[-1] ** 2, "ratio_max": 1 + dev[-1]}
    out["rays"] = devs
    pred["W1"] = all(abs(d["dev_max"]) < 1e-3 and abs(d["ratio_max"] - 0.931) > 0.05 for d in devs.values())
    pred["W1b"] = all(abs(d["dev_max"]) < abs(d["dev_mid"]) for d in devs.values())
    co = [devs[n]["dev_r2_max"] for n in ("(4,1) (10.9 deg)", "(5,2) (16.1 deg)", "(1,1) (30 deg)")]
    pred["W1c"] = 0 < co[0] < co[1] < co[2]
    C = {p["k"] * 3: float(p["C"]) for p in row}
    slope = (math.log(C[60]) - math.log(C[57])) / (math.log(60) - math.log(57))
    out["log_slope_57_60"] = slope
    pred["W2"] = abs(slope + 0.5) < 0.005
    cr = {int(p["r"]): math.sqrt(p["r"]) * float(p["C"]) for p in rays["row, other classes"]}
    mean = (cr[58] + cr[59]) / 2
    out["cross_58_59"] = [cr[58], cr[59], mean / a_inf]
    pred["W3"] = abs(mean / a_inf + 0.5) < 2e-3
    reld = (cr[58] - cr[59]) / mean
    expect = 1 / (4 * 58) + 1 / (4 * 59)
    out["cross_rel_diff"] = [reld, expect]
    pred["W3b"] = abs(reld / expect - 1) < 0.2
    pred["W4"] = abs(a_inf / A_LIT - 1) < 1e-3
    # the scan: signs, balls and outlines of the raw count
    sites = scan["sites"]
    own = [s for s in sites if s["class"] == 0]
    other = [s for s in sites if s["class"] != 0]
    pred["W5a"] = all(s["C"] > 0 for s in own) and all(s["C"] < 0 for s in other)
    cmap = {tuple(s["site"]): s["C"] for s in sites}
    cmap[(0, 0)] = 1.0
    near = sorted(((v, k) for k, v in cmap.items() if k != (0, 0)), reverse=True)[:6]
    nb = [k for _, k in near]
    out["six_nearest"] = nb
    balls = []
    for u in [0.30, 0.27, 0.24, 0.21, 0.19, 0.17, 0.16, 0.15]:
        inside = {k for k, v in cmap.items() if v >= u}
        edge = [k for k in inside if any((k[0] + d[0], k[1] + d[1]) not in inside for d in nb)]
        reach = max(math.hypot(k[0] + k[1] / 2, k[1] * math.sqrt(3) / 2) for k in inside)
        balls.append({"u": u, "ball": len(inside), "outline": len(edge), "predicted_ball": BALL_CONST * a_inf ** 4 / u ** 4,
                      "farthest": reach, "only_own_class": all((k[0] + 2 * k[1]) % 3 == 0 for k in inside)})
    out["balls"] = balls
    pred["W5b"] = all(abs(b["ball"] / b["predicted_ball"] - 1) < 0.05 for b in balls if b["u"] in (0.17, 0.15))
    lb = np.log([b["ball"] for b in balls])
    lo = np.log([b["outline"] for b in balls])
    lu = np.log([1 / b["u"] for b in balls])
    s_out = float(np.polyfit(lb, lo, 1)[0])
    s_ball = float(np.polyfit(lu, lb, 1)[0])
    out["outline_vs_ball_slope"] = s_out
    out["ball_vs_1/u_slope"] = s_ball
    pred["W6"] = 0.40 <= s_out <= 0.60
    pred["W6b"] = 3.5 <= s_ball <= 4.5
    return out


def score_chain(rays, scan, cf, pred):
    out = {}
    ok_all, ok_simple, aniso = True, True, {}
    for lk, rs in rays.items():
        out[lk] = {}
        for name, ray in rs.items():
            pts = [p for p in ray["points"] if p["rel_agree"] < 1e-8]
            norm = math.hypot(*ray["vec"])
            m = []
            for p, q in zip(pts, pts[1:]):
                k = p["k"]
                est = (math.log(abs(p["C_dual"])) - math.log(abs(q["C_dual"])) - 0.5 * math.log((k + 1) / k)) / norm
                m.append((k, est))
            if len(m) < 6:
                out[lk][name] = {"stable_points": len(pts), "note": "fewer than 6 stable points; not scored"}
                continue
            (ka, ma), (kb, mb) = m[-3], m[-1]
            mR = (kb ** 2 * mb - ka ** 2 * ma) / (kb ** 2 - ka ** 2)
            exact = ray["rate_closed_form"]
            out[lk][name] = {"stable_points": len(pts), "r_max": pts[-1]["r"], "m_last": mb, "m_richardson": mR,
                             "closed_form": exact, "rel_last": mb / exact - 1, "rel_richardson": mR / exact - 1}
            ok_all &= abs(mR / exact - 1) < 1e-3
            ok_simple &= abs(mb / exact - 1) < 3e-3
        if "(1,0)" in out[lk] and "m_richardson" in out[lk].get("(1,1)", {}) and "m_richardson" in out[lk]["(1,0)"]:
            meas = out[lk]["(1,1)"]["m_richardson"] / out[lk]["(1,0)"]["m_richardson"]
            aniso[lk] = {"measured": meas, "closed_form": cf[lk]["anisotropy"]}
    pred["C1"] = ok_all
    pred["C1b"] = ok_simple
    out["anisotropy"] = aniso
    pred["C1c"] = "l=1" in aniso and abs(aniso["l=1"]["measured"] / aniso["l=1"]["closed_form"] - 1) < 1e-3
    # scan: one eighth, unfolded by the eight symmetries
    cm = {}
    for s in scan["sites"]:
        a, b = s["site"]
        for x, y in {(a, b), (b, a)}:
            for sx in (1, -1):
                for sy in (1, -1):
                    cm[(sx * x, sy * y)] = s["C"]
    cm[(0, 0)] = 1.0
    pred["C4c"] = all((v > 0) == ((abs(k[0]) + abs(k[1])) % 2 == 0) for k, v in cm.items() if k != (0, 0))
    tau = {k: -math.log(abs(v)) / math.log(3) for k, v in cm.items()}
    nb = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    balls = []
    for t0 in [2.0, 3.0, 4.0, 5.0, 6.0, 7.0]:
        inside = {k for k, v in tau.items() if v <= t0}
        edge = [k for k in inside if any((k[0] + d[0], k[1] + d[1]) not in inside for d in nb)]
        balls.append({"tau": t0, "ball": len(inside), "outline": len(edge),
                      "farthest_axis": max(abs(k[0]) for k in inside if k[1] == 0),
                      "farthest_diag": max(abs(k[0]) for k in inside if abs(k[0]) == abs(k[1]))})
    out["balls"] = balls
    lb = np.log([b["ball"] for b in balls])
    lo = np.log([b["outline"] for b in balls])
    lt = np.log([b["tau"] for b in balls])
    out["outline_vs_ball_slope"] = float(np.polyfit(lb, lo, 1)[0])
    out["ball_vs_tau_slope"] = float(np.polyfit(lt, lb, 1)[0])
    pred["C4"] = 0.40 <= out["outline_vs_ball_slope"] <= 0.60
    pred["C4b"] = 1.6 <= out["ball_vs_tau_slope"] <= 2.4
    return out


def score_census(cen, pred):
    det = lambda pop, n, key: cen[pop][str(n)]["readings"][key]
    g1 = all(det("cheap", n, "a")["fail_k"] == 0 and det("cheap", n, "a")["fail_lam"] == 0 for n in range(4, 13))
    g1 &= all(det("one-split", n, "a")["fail_k"] == 0 and det("one-split", n, "a")["fail_lam"] == 0 for n in range(4, 8))
    pred["G1"] = g1
    pred["G2"] = any(det("one-split", n, "c")["fail_k"] > 0 for n in (4, 5))
    pred["G3"] = "8" in cen["one-split"] and det("one-split", 8, "a")["fail_k"] == 0 and det("one-split", 8, "a")["fail_lam"] == 0
    return {pop: {n: {"classes": v["classes"], **{k: {x: v["readings"][k][x] for x in ("groups", "multi", "fail_k", "fail_lam")}
                                                   for k in ("a", "b", "c")}} for n, v in cen[pop].items()} for pop in cen}


def main(art):
    pred, res = {}, {}
    wr, ws = load(art, "weave_rays"), load(art, "weave_scan")
    if wr and ws:
        res["weave"] = score_weave(wr, ws, pred)
    cr, cs, cf = load(art, "chain_rays"), load(art, "chain_scan"), load(art, "outline_cf")
    if cr and cs and cf:
        res["chain"] = score_chain(cr, cs, cf, pred)
        res["outline_closed_form"] = cf
    cen = load(art, "census")
    if cen:
        res["census"] = score_census(cen, pred)
    ss = load(art, "state_side")
    if ss:
        res["state_side"] = ss
    res["predictions"] = pred
    json.dump(res, open(art / "results.json", "w"), indent=1, default=str)
    for k, v in pred.items():
        print(k, "held" if v else "FAILED")
