"""LATE-HOP-20261112-001A: the late-changing rules of TWO-BIT-ROWS-20261112-001, read to depth 200.

Selection (frozen, from TWO-BIT-ROWS's records, deterministic): every hopping rule unexplained within 40 or whose first-generation
relation or life last differs from the depth before at depth 16 or later; every flat harmony and the four flat rules with the latest
change (ties broken by record order). Readings as in TWO-BIT-ROWS (its census.py, imported unchanged) for t = 1..200.
Classes: constant; eventually periodic with the smallest period p <= 50 holding from some depth a <= 100 to depth 200 (eventually
constant when p = 1); neither within 200. Also the depths at which each sequence differs from the depth before, against the depths
where the last generation's length 2 + t is a power of two.
Run from the repository root:  census.py --select  |  census.py --run WORKER WORKERS  |  census.py --summary
"""
import glob, importlib.util, json, os, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
TB_DIR = os.path.join(HERE, "../../TWO-BIT-ROWS-20261112-001A/TWO-BIT-ROWS-20261112-001A-E001_two_bit_rules")
_s = importlib.util.spec_from_file_location("tb", os.path.join(TB_DIR, "census.py"))
TB = importlib.util.module_from_spec(_s); _s.loader.exec_module(TB)
TB.TMAX, TB.PMAX, TB.AMAX = 200, 50, 100
SRC = os.path.join(HERE, "../../../artifacts/TWO-BIT-ROWS-20261112-001A/TWO-BIT-ROWS-20261112-001A-E001_two_bit_rules")
OUT = os.environ.get("LH_OUT") or os.path.join(HERE, "../../../artifacts/LATE-HOP-20261112-001A/LATE-HOP-20261112-001A-E001_deep_read")


def last_diff(seq):
    return max([t + 1 for t in range(1, len(seq)) if seq[t] != seq[t - 1]] + [0])


def select():
    rows = [json.loads(x) for n in sorted(glob.glob(os.path.join(SRC, "*.jsonl"))) for x in open(n)]
    pick = []
    for r in rows:
        late = max(last_diff(r["alive"]), last_diff(r["top"]))
        if r["variant"] == "hop" and ("unexplained" in (r["alive_class"][0], r["top_class"][0]) or late >= 16):
            pick.append(dict(variant="hop", rule=r["rule"], why="unexplained" if "unexplained" in (r["alive_class"][0], r["top_class"][0]) else "late"))
    flat = [r for r in rows if r["variant"] == "flat"]
    harm = [r for r in flat if "harmony" in (r["alive_class"][0], r["top_class"][0])]
    pick += [dict(variant="flat", rule=r["rule"], why="harmony") for r in harm]
    rest = sorted([r for r in flat if r not in harm], key=lambda r: -max(last_diff(r["alive"]), last_diff(r["top"])))[:4]
    pick += [dict(variant="flat", rule=r["rule"], why="latest") for r in rest]
    os.makedirs(OUT, exist_ok=True)
    json.dump(pick, open(os.path.join(OUT, "selection.json"), "w"), indent=1)
    print(len(pick), Counter((p["variant"], p["why"]) for p in pick))


def run(worker, workers):
    pick = json.load(open(os.path.join(HERE, "selection.json")))
    f = open(os.path.join(OUT, f"runs_{worker}.jsonl"), "w")
    for k, p in enumerate(pick):
        if k % workers != worker:
            continue
        alive, top = TB.read(p["variant"], [tuple(t) for t in p["rule"]])
        f.write(json.dumps(dict(k=k, **p, alive=alive, top=top, alive_class=TB.classify(alive), top_class=TB.classify(top),
                                alive_changes=[t + 1 for t in range(1, len(alive)) if alive[t] != alive[t - 1]],
                                top_changes=[t + 1 for t in range(1, len(top)) if top[t] != top[t - 1]][:60])) + "\n")
        f.flush()
    f.close()


def summarize():
    rows = [json.loads(x) for n in sorted(glob.glob(os.path.join(OUT, "runs_*.jsonl"))) for x in open(n)]
    pow2 = {t for t in range(1, 201) if ((t + 2) & (t + 1)) == 0}           # depths where 2 + t is a power of two
    near = lambda t: any(abs(t - q) <= 2 for q in pow2)
    S = dict(read=len(rows))
    S["classes"] = {f"{r['variant']}/{r['why']}": None for r in rows}
    S["classes"] = dict(Counter((r["variant"], r["why"], r["alive_class"][0], r["top_class"][0]) for r in rows))
    S["classes"] = {"|".join(k): v for k, v in S["classes"].items()}
    S["L1_neither"] = [r["k"] for r in rows if "neither within 200" in (r["alive_class"][0], r["top_class"][0]) or "unexplained" in (r["alive_class"][0], r["top_class"][0])]
    late = [r for r in rows if r["why"] == "unexplained"]
    S["unexplained_five"] = [dict(k=r["k"], alive=r["alive_class"], top=r["top_class"], alive_changes=r["alive_changes"][:12],
                                  top_changes=r["top_changes"][:12]) for r in late]
    S["changes_after_40"] = {r["k"]: [t for t in r["alive_changes"] + r["top_changes"] if t > 40][:20] for r in rows
                             if any(t > 40 for t in r["alive_changes"] + r["top_changes"])}
    S["L2_changes_after_40_not_near_power_of_two"] = {k: [t for t in v if not near(t)] for k, v in S["changes_after_40"].items()
                                                       if any(not near(t) for t in v)}
    S["periods"] = dict(Counter(r[c][1] for r in rows for c in ("alive_class", "top_class") if r[c][0] == "harmony"))
    return S


if __name__ == "__main__":
    if sys.argv[1] == "--select":
        select()
    elif sys.argv[1] == "--run":
        run(int(sys.argv[2]), int(sys.argv[3]))
    elif sys.argv[1] == "--summary":
        S = summarize()
        json.dump(S, open(os.path.join(OUT, "summary.json"), "w"), indent=1)
        print(json.dumps(S, indent=1))
