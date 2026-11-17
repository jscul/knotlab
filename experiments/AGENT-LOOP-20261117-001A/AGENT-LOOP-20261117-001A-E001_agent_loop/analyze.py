"""Frozen analysis of AGENT-LOOP-20261117-001A.

  python3 analyze.py <test dir> <summary.json>

The statistic, as in SLOW-LOOP, EARN-BUDGET and SPEC-MERGE: per instance the geometric mean of five runs; per cell and arm the
median over instances; a ratio between arms is the ratio of those cell medians, with a 99% paired bootstrap interval over
instances (10,000 resamples). R is against F, the better of Novelty+ (0.7, 0.01) and (0.8, 0.01), re-chosen per resample. A capped
run enters at the cap. A ratio is a bound, and no test holds on it, when either arm has more than 10% capped runs on the cell.

Each measure is read under the budget that makes it fair:
- **flips** under the per-flip budget (the same proofs per flip for every fast loop): DrCf, DrRf, GNf;
- **charged work** under EARN-BUDGET's rule (each fast loop spends the same share of its work on proofs): DrC, DrR, GN.

The tests, each computed for each seed of Dr; a test holds on a cell only when both seeds pass ("seeds disagree" when one does):
- **M1, memory.** Carried over restarted memory, DrCf/DrRf in flips and DrC/DrR in work. Read on a cell only if it has room
  under that budget (the median share of the restarted runs' flips made after the first rebuild is at least one half, both
  seeds). Carry helps at <= 0.9 with the upper end below 1; it hurts at >= 1.11 with the lower end above 1.
- **M2, the slow loop helps the agent.** DrCf/Dr in flips, DrC/Dr in work: <= 0.8 with the upper end below 0.9.
- **M3, the agent under the loop beats Novelty+ under the loop.** DrCf/GNf in flips, DrC/GN in work: <= 0.9, upper end below 1.
- **M4, the loop helps the agent more than it helps Novelty+** (the interaction). (DrCf/Dr)/(GNf/NOV) in flips and
  (DrC/Dr)/(GN/NOV) in work: <= 0.9 with the upper end below 1.

A test holds on a family when it holds on the family's first cell (never run before the freeze) and on at least one second cell.
The first cell's own verdict is reported as the headline, the second cells as replication.

Two frozen verdicts:
- **Memory** (first), per family and measure: carry helps, carry hurts, no difference shown, no room, or a bound; "budget-dependent"
  when, in flips, M1 under EARN-BUDGET's rule (context) passes the opposite way on the first cell.
- **Loop** (second), per family, from the measures in which M2 and M3 hold, in this order: (1) both in charged work; (2) both in
  flips; (3) both, in different measures; (4) M2 only; (5) M3 only; (6) neither.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "scripts"))
from longrun import load_results  # noqa: E402

B = 10_000
MEASURES = ("flips", "work", "cpu")
FAMILIES = {"local": ("local-w30-3200", ["local-w10-3200", "local-w20-3200"]),
            "block": ("block-w40-3200", ["block-w20-3200"])}
SEEDS = ("0", "1")
CAPPED_MAX = 0.10
# (test, measure) -> (numerator, denominator[, numerator 2, denominator 2]) with {s} the seed of Dr
TESTS = {
    ("M1", "flips"): ("DrCf{s}", "DrRf{s}"), ("M1", "work"): ("DrC{s}", "DrR{s}"),
    ("M2", "flips"): ("DrCf{s}", "Dr{s}"), ("M2", "work"): ("DrC{s}", "Dr{s}"),
    ("M3", "flips"): ("DrCf{s}", "GNf"), ("M3", "work"): ("DrC{s}", "GN"),
    ("M4", "flips"): ("DrCf{s}", "Dr{s}", "GNf", "NOV"), ("M4", "work"): ("DrC{s}", "Dr{s}", "GN", "NOV"),
}
CONTEXT = {"M1 under EARN-BUDGET's rule": ("DrC{s}", "DrR{s}"), "M1 per-flip": ("DrCf{s}", "DrRf{s}"),
           "M2 under EARN-BUDGET's rule": ("DrC{s}", "Dr{s}"), "M3 under EARN-BUDGET's rule": ("DrC{s}", "GN"),
           "M3 per-flip": ("DrCf{s}", "GNf")}
NAMES = {"M1": "memory carried beats restarted", "M2": "the slow loop helps the agent",
         "M3": "the agent under the loop beats Novelty+ under the loop",
         "M4": "the loop helps the agent more than it helps Novelty+"}


def fig(arm_res, key):
    return {i: float(np.exp(np.mean(np.log([max(x[key], 1e-9) for x in r["runs"]])))) for i, r in arm_res.items()}


def boot(f, arms, idx, rng):
    """Ratio of cell medians med(a)/med(b) [/ (med(c)/med(d))]; for a list of denominators (R) the smallest is used."""
    if len(arms) == 2 and isinstance(arms[1], list):
        a = np.array([f[arms[0]][i] for i in idx])
        ds = [np.array([f[d][i] for i in idx]) for d in arms[1]]
        point = np.median(a) / min(np.median(d) for d in ds)
        sel = rng.integers(0, len(idx), (B, len(idx)))
        r = np.median(a[sel], axis=1) / np.min(np.stack([np.median(d[sel], axis=1) for d in ds]), axis=0)
    else:
        v = [np.array([f[x][i] for i in idx]) for x in arms]
        point = np.median(v[0]) / np.median(v[1])
        sel = rng.integers(0, len(idx), (B, len(idx)))
        r = np.median(v[0][sel], axis=1) / np.median(v[1][sel], axis=1)
        if len(arms) == 4:
            point /= np.median(v[2]) / np.median(v[3])
            r = r / (np.median(v[2][sel], axis=1) / np.median(v[3][sel], axis=1))
    lo, hi = np.quantile(r, [0.005, 0.995])
    return [float(point), float(lo), float(hi)]


def passes(t, test, kind="helps"):
    if kind == "hurts":
        return t[0] >= 1.11 and t[1] > 1.0
    thr = 0.8 if test == "M2" else 0.9
    return t[0] <= thr and t[2] < thr + 0.1


def room(runs):
    """The median share of a run's flips made after its first rebuild (0 for a run that never rebuilt)."""
    return float(np.median([(x["flips"] - x["flips_first"]) / x["flips"] if x.get("flips_first") is not None and x["flips"]
                            else 0.0 for x in runs]))


def main(d, out):
    rng = np.random.default_rng(20261117)
    data = {}
    for k, r in load_results(d).items():
        if r.get("status") != "ok":
            continue
        res = r["result"]
        data.setdefault(res["cell"], {}).setdefault(res["arm"], {})[int(k.split("|")[-1])] = res
    summ = {}
    for cell, arms in data.items():
        idx = sorted(set.intersection(*[set(v) for v in arms.values()]))
        F = {m: {a: fig(v, m) for a, v in arms.items() if a != "SL"} for m in MEASURES}
        c = {"instances": len(idx), "arms": {}, "room": {}, "tests": {}, "context": {}}
        for a, v in arms.items():
            runs = [x for i in idx for x in v[i]["runs"]]
            row = {"capped": sum(not x["solved"] for x in runs) / len(runs),
                   "unverified": sum(bool(x["solved"]) and not x.get("verified") for x in runs),
                   "median": {m: float(np.median([float(np.exp(np.mean(np.log([max(x[m], 1e-9) for x in v[i]["runs"]]))))
                                                  for i in idx])) for m in MEASURES},
                   "rebuilds": float(np.median([x.get("rebuilds", 0) for x in runs])),
                   "n_final": float(np.median([x.get("n_final", 0) for x in runs])),
                   "flips_after_first_per_rebuild": float(np.median(
                       [(x["flips"] - x["flips_first"]) / max(1, x.get("rebuilds", 0))
                        for x in runs if x.get("flips_first") is not None] or [0.0]))}
            if a == "SL":
                row = {"solved": sum(bool(x["solved"]) for x in runs), "runs": len(runs),
                       "unverified": row["unverified"], "rebuilds": row["rebuilds"], "n_final": row["n_final"],
                       "median_work": row["median"]["work"]}
            elif a not in ("NOV", "NOV8"):
                bound = row["capped"] > CAPPED_MAX or min(sum(not x["solved"] for i in idx for x in arms[b][i]["runs"])
                                                         / len(runs) for b in ("NOV", "NOV8")) > CAPPED_MAX
                row["R"] = {m: boot(F[m], [a, ["NOV", "NOV8"]], idx, rng) + (["bound"] if bound else [])
                            for m in MEASURES}
            if a[:3] in ("DrC", "DrR"):
                c["room"][a] = room(runs)
            c["arms"][a] = row
        capped = {a: c["arms"][a]["capped"] for a in arms if a != "SL"}
        for (test, m), spec in TESTS.items():
            per_seed = {}
            for s in SEEDS:
                names = [x.format(s=s) for x in spec]
                if not all(x in arms for x in names):
                    continue
                t = boot(F[m], names, idx, rng)
                per_seed[s] = {"ratio": t, "bound": any(capped[x] > CAPPED_MAX for x in names)}
            if len(per_seed) < 2:
                continue
            entry = {"seeds": per_seed}
            if test == "M1":
                rest = "f" if m == "flips" else ""
                entry["room"] = all(c["room"].get(f"DrR{rest}{s}", 0.0) >= 0.5 for s in SEEDS)
            for kind in (("helps", "hurts") if test == "M1" else ("helps",)):
                if any(p["bound"] for p in per_seed.values()):
                    v = "bound"
                elif test == "M1" and not entry["room"]:
                    v = "no room"
                else:
                    k = sum(passes(p["ratio"], test, kind) for p in per_seed.values())
                    v = "holds" if k == 2 else "seeds disagree" if k == 1 else "fails"
                entry[kind] = v
            c["tests"][f"{test} {m}"] = entry
        for name, spec in CONTEXT.items():
            for s in SEEDS:
                names = [x.format(s=s) for x in spec]
                if all(x in arms for x in names):
                    c["context"][f"{name} s{s}"] = {m: boot(F[m], names, idx, rng) for m in MEASURES}
        if "GNco" in arms and "GN" in arms:
            c["context"]["co-flip/random targets"] = {m: boot(F[m], ["GNco", "GN"], idx, rng) for m in MEASURES}
        summ[cell] = c

    def fam_verdict(fam, test, m, kind="helps"):
        first, rest = FAMILIES[fam]
        if first not in summ or f"{test} {m}" not in summ[first]["tests"]:
            return {"family": None}
        v1 = summ[first]["tests"][f"{test} {m}"][kind]
        reps = {c: summ[c]["tests"][f"{test} {m}"][kind] for c in rest if c in summ and f"{test} {m}" in summ[c]["tests"]}
        fam_v = v1 if v1 != "holds" else ("holds" if any(v == "holds" for v in reps.values()) else "not replicated")
        return {"first cell": v1, "replication": reps, "family": fam_v}

    verdicts = {fam: {f"{test} {m}" + (f" {kind}" if test == "M1" else ""): fam_verdict(fam, test, m, kind)
                      for (test, m) in TESTS for kind in (("helps", "hurts") if test == "M1" else ("helps",))}
                for fam in FAMILIES}
    memory = {}
    for fam in FAMILIES:
        for m in ("flips", "work"):
            h, u = verdicts[fam][f"M1 {m} helps"]["family"], verdicts[fam][f"M1 {m} hurts"]["family"]
            if h in ("no room", "bound", None):
                v = h or "missing"
            else:
                v = "carry helps" if h == "holds" else "carry hurts" if u == "holds" else "no difference shown"
            if m == "flips" and v in ("carry helps", "carry hurts"):
                first = FAMILIES[fam][0]
                ctx = [summ[first]["context"].get(f"M1 under EARN-BUDGET's rule s{s}") for s in SEEDS]
                if all(ctx):
                    other = "hurts" if v == "carry helps" else "helps"
                    if all(passes(x["flips"], "M1", other) for x in ctx):
                        v += " (budget-dependent: the other budget passes the opposite way)"
            memory[f"{fam} {m}"] = v
    loop = {}
    for fam in FAMILIES:
        p2 = {m for m in ("flips", "work") if verdicts[fam][f"M2 {m}"]["family"] == "holds"}
        p3 = {m for m in ("flips", "work") if verdicts[fam][f"M3 {m}"]["family"] == "holds"}
        if "work" in p2 & p3:
            loop[fam] = "1 every part pays in charged work: the loop helps the agent, and the agent under the loop beats " \
                        "Novelty+ under the loop"
        elif "flips" in p2 & p3:
            loop[fam] = "2 every part pays in flips only: the loop helps the agent, and the agent under the loop beats " \
                        "Novelty+ under the loop, in flips"
        elif p2 and p3:
            loop[fam] = f"3 both, in different measures: the loop helps the agent in {', '.join(sorted(p2))}, and the agent " \
                        f"under the loop beats Novelty+ under the loop in {', '.join(sorted(p3))}"
        elif p2:
            loop[fam] = f"4 the loop helps the agent (in {', '.join(sorted(p2))}), but the agent under the loop does not " \
                        "beat Novelty+ under the loop"
        elif p3:
            loop[fam] = f"5 the agent under the loop beats Novelty+ under the loop (in {', '.join(sorted(p3))}), but the " \
                        "loop does not help the agent"
        else:
            loop[fam] = "6 no mechanism gain"
    summ["verdicts"] = verdicts
    summ["memory"] = memory
    summ["loop"] = loop
    Path(out).write_text(json.dumps(summ, indent=1))
    f = lambda t: f"{t[0]:.2f} [{t[1]:.2f}, {t[2]:.2f}]" + (" bound" if len(t) > 3 else "")
    for cell, c in summ.items():
        if not isinstance(c, dict) or "arms" not in c:
            continue
        print("==", cell, "| room", {k: round(v, 2) for k, v in c["room"].items()})
        for a, row in c["arms"].items():
            if a == "SL":
                print(f"  SL     solved {row['solved']}/{row['runs']} rebuilds {row['rebuilds']:.0f} n_final "
                      f"{row['n_final']:.0f} work {row['median_work']:.3g}")
                continue
            line = (f"  {a:6s} capped {row['capped']:.3f} rebuilds {row['rebuilds']:.0f} n_final {row['n_final']:.0f} "
                    f"median flips {row['median']['flips']:.3g} work {row['median']['work']:.3g}")
            if "R" in row:
                line += f" | R flips {f(row['R']['flips'])} work {f(row['R']['work'])} cpu {f(row['R']['cpu'])}"
            print(line)
        for k, v in c["tests"].items():
            print(f"   {k}: " + " ".join(f"s{s} {f(p['ratio'])}" for s, p in v["seeds"].items()) +
                  " | " + ", ".join(f"{kind} {v[kind]}" for kind in ("helps", "hurts") if kind in v))
        for k, v in c["context"].items():
            print(f"   ({k}): flips {f(v['flips'])} work {f(v['work'])} cpu {f(v['cpu'])}")
    print(json.dumps(verdicts, indent=1))
    print("memory:", json.dumps(memory, indent=1))
    print("loop:", json.dumps(loop, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
