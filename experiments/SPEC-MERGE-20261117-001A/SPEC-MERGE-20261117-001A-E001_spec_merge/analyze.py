"""Frozen analysis of SPEC-MERGE-20261117-001A.

  python3 analyze.py gate <gate dir> <gate_summary.json>
  python3 analyze.py test <test dir> <summary.json>

Gate D: per checkpoint (4, 8, 16 epochs) and cell, the mean over instances of (co-flip pairs' agreement with the planted
relative values - random pairs'), and on local w10 of (co-flip pairs' tied share - random pairs'), with 99% bootstrap intervals
over instances (10,000 resamples). Test: as SLOW-LOOP and EARN-BUDGET (per instance the geometric mean of five runs of charged
work, per cell the median, R against the better of NOV and NOVt re-chosen per resample, 99% paired bootstrap), plus the
ratios A/Arand, A0/Arand0, Aloc/Arandloc, A/Gpr and Aloc/Gpr.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "scripts"))
from longrun import load_results  # noqa: E402

B = 10_000


def ci(v, rng):
    v = np.asarray(v, float)
    sel = rng.integers(0, len(v), (B, len(v)))
    m = v[sel].mean(axis=1)
    lo, hi = np.quantile(m, [0.005, 0.995])
    return [float(v.mean()), float(lo), float(hi)]


def gate(d, out):
    rng = np.random.default_rng(1117)
    recs = [r["result"] for r in load_results(d).values() if r.get("status") == "ok"]
    summ = {}
    for cell in sorted({r["cell"] for r in recs}):
        rows = [r for r in recs if r["cell"] == cell]
        summ[cell] = {"instances": len(rows), "solved_before_16": sum("solved_at_epoch" in r["gate"] for r in rows)}
        for cp in ("4", "8", "16"):
            ag, tie, abs_c, abs_r = [], [], [], []
            for r in rows:
                c = r["gate"]["checkpoints"].get(cp)
                if not c or not c.get("coflip") or not c.get("random"):
                    continue
                ag.append(c["coflip"]["agree_planted"] - c["random"]["agree_planted"])
                abs_c.append(c["coflip"]["agree_planted"])
                abs_r.append(c["random"]["agree_planted"])
                if "tied_share" in c["coflip"]:
                    tie.append((c["coflip"]["tied_share"], c["random"]["tied_share"]))
            if not ag:
                continue
            row = {"instances": len(ag), "agree_diff": ci(ag, rng), "agree_coflip": float(np.mean(abs_c)),
                   "agree_random": float(np.mean(abs_r))}
            fd = [(r["gate"]["checkpoints"][cp]["coflip"]["agree_found"], r["gate"]["checkpoints"][cp]["random"]["agree_found"])
                  for r in rows if r["gate"]["checkpoints"].get(cp, {}).get("coflip", {}) and
                  "agree_found" in r["gate"]["checkpoints"][cp]["coflip"]]
            if fd:
                fd = np.array(fd)
                row["found_diff"] = ci(fd[:, 0] - fd[:, 1], rng)
                row["agree_found_coflip"], row["agree_found_random"] = float(fd[:, 0].mean()), float(fd[:, 1].mean())
            if tie:
                t = np.array(tie)
                row["tied_diff"] = ci(t[:, 0] - t[:, 1], rng)
                row["tied_coflip"], row["tied_random"] = float(t[:, 0].mean()), float(t[:, 1].mean())
            summ[cell][cp] = row
    # frozen gate rules
    r = summ.get("rand-3200", {})
    d_rand = any(r.get(cp, {}).get("agree_diff", [0, -1, 0])[0] >= 0.10 and r[cp]["agree_diff"][1] > 0
                 for cp in ("4", "8", "16"))
    l = summ.get("local-w10-3200", {})
    d_local = any(l.get(cp, {}).get("tied_coflip", 0) >= 1.5 * l.get(cp, {}).get("tied_random", 1)
                  and l[cp]["tied_diff"][1] > 0 for cp in ("4", "8", "16") if cp in l)
    summ["D_rand"], summ["D_local"] = d_rand, d_local
    Path(out).write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


def figures(arm_res, key):
    out = {}
    for i, res in arm_res.items():
        v = [max(run[key], 1e-9) for run in res["runs"]]
        out[i] = float(np.exp(np.mean(np.log(v))))
    return out


def boot(fig, num, dens, idx, rng):
    a = np.array([fig[num][i] for i in idx])
    ds = [np.array([fig[d][i] for i in idx]) for d in dens]
    point = np.median(a) / min(np.median(d) for d in ds)
    sel = rng.integers(0, len(idx), (B, len(idx)))
    r = np.median(a[sel], axis=1) / np.min(np.stack([np.median(d[sel], axis=1) for d in ds]), axis=0)
    lo, hi = np.quantile(r, [0.005, 0.995])
    return [float(point), float(lo), float(hi)]


def verdict(rw, rc):
    if rw[0] <= 0.8 and rw[2] < 0.9:
        return "charged win" if rc[2] < 1 else "work win"
    if rw[1] > 1.1:
        return "loss"
    return "parity or inconclusive"


def test(d, out):
    rng = np.random.default_rng(20261117)
    data = {}
    recs = {}
    for one in d.split(","):  # the test ran in two parts: the fixed arms, then the tuned ones once tuning was done
        recs.update(load_results(one))
    for k, r in recs.items():
        if r.get("status") != "ok":
            continue
        res = r["result"]
        data.setdefault(res["cell"], {}).setdefault(res["arm"], {})[int(k.split("|")[-1])] = res
    summ = {}
    for cell, arms in data.items():
        idx = sorted(set.intersection(*[set(v) for v in arms.values()]))
        fw = {a: figures(v, "work") for a, v in arms.items()}
        fc = {a: figures(v, "cpu") for a, v in arms.items()}
        cs = {a: sum(not x["solved"] for i in idx for x in v[i]["runs"]) / (5 * len(idx)) for a, v in arms.items()}
        cell_s = {"instances": len(idx), "arms": {}, "ratios": {}}
        for a, v in arms.items():
            row = {"W": float(np.median([fw[a][i] for i in idx])), "censored": cs[a],
                   "unverified": sum(x["solved"] and not x["verified"] for i in idx for x in v[i]["runs"])}
            if a not in ("NOV", "NOVt"):
                row["R_W"] = boot(fw, a, ["NOV", "NOVt"], idx, rng)
                row["R_W_vs_NOV"] = boot(fw, a, ["NOV"], idx, rng)
                row["R_CPU"] = boot(fc, a, ["NOV", "NOVt"], idx, rng)
                row["verdict"] = verdict(row["R_W"], row["R_CPU"])
                if cs[a] > 0.05 or max(cs["NOV"], cs["NOVt"]) > 0.05:
                    row["verdict"] += " (censoring over 5%: a bound)"
                for key in ("merges", "undos", "active_merges", "precision_all", "precision_active", "n_final"):
                    vals = [x[key] for i in idx for x in v[i]["runs"] if key in x]
                    if vals:
                        row[key] = float(np.median(vals))
                # rounds: planted-consistent or not, against kept or undone (does the undo catch the bad rounds?)
                rl = [tuple(t) for i in idx for x in v[i]["runs"] for t in x.get("round_log", [])]
                if rl:
                    row["rounds_by_consistent_kept"] = {f"{c}{k}": sum(1 for t in rl if t == (c, k))
                                                        for c in (0, 1) for k in (0, 1)}
            cell_s["arms"][a] = row
        for num, den in (("A", "Arand"), ("A0", "Arand0"), ("AE", "AErand"), ("Aloc", "Arandloc"), ("A", "Gpr"),
                         ("Aloc", "Gpr"), ("A0", "Gpr"), ("AE", "Gpr")):
            if num in fw and den in fw:
                cell_s["ratios"][f"{num}/{den}"] = {"W": boot(fw, num, [den], idx, rng), "CPU": boot(fc, num, [den], idx, rng)}
        summ[cell] = cell_s
    Path(out).write_text(json.dumps(summ, indent=1))
    f = lambda t: f"{t[0]:.2f} [{t[1]:.2f}, {t[2]:.2f}]"
    for cell, c in summ.items():
        print("==", cell)
        for a, row in c["arms"].items():
            if "R_W" in row:
                print(f"  {a:9s} R_W {f(row['R_W'])} R_CPU {f(row['R_CPU'])} {row['verdict']} cens {row['censored']:.3f} "
                      f"merges {row.get('merges', 0):.0f} undos {row.get('undos', 0):.0f} prec {row.get('precision_all', -1):.3f}")
        for k, v in c["ratios"].items():
            print(f"   {k} {f(v['W'])}")


if __name__ == "__main__":
    {"gate": gate, "test": test}[sys.argv[1]](sys.argv[2], sys.argv[3])
