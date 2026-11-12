"""TWO-BIT-ROWS-R1: the referee's own rebuild of TWO-BIT-ROWS-20261112-001's generations, and checks of the hop harmonies.

  ref_two.py hop W N        every hop rule with one or two knots, as frozen and with the collision at position 0 dropped
                            -> result_hop_<w>.jsonl
  ref_two.py late           the census's unexplained and smallest harmony rules to depth 80 -> result_late.json
  ref_two.py summary        -> result_summary.json
"""
import glob
import itertools
import json
import sys
from collections import Counter
from pathlib import Path

from pysat.solvers import Solver

HERE = Path(__file__).resolve().parent
CENSUS = HERE.parents[2] / "artifacts" / "TWO-BIT-ROWS-20261112-001A" / "TWO-BIT-ROWS-20261112-001A-E001_two_bit_rules"
HOP = [("o", 0, 0), ("o", 0, 1), ("o", "half", 0), ("o", "half", 1), ("n", -1, 0), ("n", -1, 1), ("n", 0, 0), ("n", 0, 1)]
FLAT = [("o", d, b) for d in (-1, 0, 1) for b in (0, 1)] + [("n", d, b) for d in (-1, 0) for b in (0, 1)]
REL = {"hop": HOP, "flat": FLAT}


def var(r, p, b):
    """Generation r has 2 + r positions of two distinctions; numbered generation by generation."""
    return sum(2 * (2 + q) for q in range(r)) + 2 * p + b + 1


def clauses(variant, rule, t, drop_collision=False):
    rel = REL[variant]
    cl = []
    for r in range(1, t + 1):
        n_old = 2 + r - 1
        for i in range(2 + r):
            if drop_collision and variant == "hop" and i // 2 == i:
                continue                                  # position 0: old i and old floor(i/2) are the same position
            for tr in rule:
                vs = []
                for j in tr:
                    side, off, b = rel[j]
                    p = i // 2 if off == "half" else i + off
                    size = n_old if side == "o" else 2 + r
                    vs.append(var(r - 1 if side == "o" else r, p, b) if 0 <= p < size else None)
                if None not in vs and len(set(vs)) == 3:
                    cl += [vs, [-v for v in vs]]
    last = [var(t, p, b) for p in range(2 + t) for b in (0, 1)]
    for k in range(len(last) - 2):
        cl += [last[k:k + 3], [-v for v in last[k:k + 3]]]
    return cl


def read(variant, rule, tmax=40, drop_collision=False):
    alive, top = [], []
    first = [var(0, p, b) for p in range(2) for b in (0, 1)]
    for t in range(1, tmax + 1):
        with Solver(name="glucose4", bootstrap_with=clauses(variant, rule, t, drop_collision)) as s:
            a = s.solve()
            alive.append(a)
            cls = ["".join(map(str, (0,) + bits)) for bits in itertools.product((0, 1), repeat=3)
                   if a and s.solve(assumptions=[v if x else -v for v, x in zip(first, (0,) + bits)])]
            top.append("|".join(cls))
    return alive, top


def classify(seq, pmax=10, amax=20):
    if all(x == seq[0] for x in seq):
        return "constant"
    for p in range(1, pmax + 1):
        for a in range(amax):
            if all(seq[t] == seq[t + p] for t in range(a, len(seq) - p)):
                return "eventually constant" if p == 1 else f"harmony {p}"
    return "unexplained"


def changes(seq):
    return [t + 1 for t in range(1, len(seq)) if seq[t] != seq[t - 1]]


def census_rows(variant=None, source=None):
    rows = [json.loads(x) for n in sorted(glob.glob(str(CENSUS / "*.jsonl"))) for x in open(n)]
    return [r for r in rows if (variant is None or r["variant"] == variant) and (source is None or r["source"] == source)]


def hop(worker, workers):
    rec = {tuple(map(tuple, r["rule"])): r for r in census_rows("hop", "all")}
    idx = -1
    with open(HERE / f"result_hop_{worker}.jsonl", "w") as f:
        for m in (1, 2):
            for rule in itertools.combinations(itertools.combinations(range(8), 3), m):
                idx += 1
                if idx % workers != worker:
                    continue
                alive, top = read("hop", list(rule))
                c = rec[tuple(rule)]
                a2, t2 = read("hop", list(rule), drop_collision=True)
                f.write(json.dumps(dict(rule=rule, match=(alive == c["alive"] and top == c["top"]),
                                        frozen=[classify(alive), classify(top)], no_collision=[classify(a2), classify(t2)])) + "\n")


def late():
    out = []
    rows = census_rows("hop")
    pick = [r for r in rows if "unexplained" in (r["alive_class"][0], r["top_class"][0])]
    pick += [r for r in rows if r["m"] <= 3 and "harmony" in (r["alive_class"][0], r["top_class"][0])]
    for r in pick:
        alive, top = read("hop", r["rule"], tmax=80)
        a2, t2 = read("hop", r["rule"], tmax=40, drop_collision=True)
        out.append(dict(m=r["m"], census=[r["alive_class"][0], r["top_class"][0]],
                        match40=(alive[:40] == r["alive"] and top[:40] == r["top"]),
                        alive_changes_to_80=changes(alive), top_changes_to_80=changes(top),
                        classified_80=[classify(alive, amax=60), classify(top, amax=60)],
                        no_collision_40=[classify(a2), classify(t2)], rule=r["rule"]))
        print(json.dumps({k: v for k, v in out[-1].items() if k != "rule"}), flush=True)
    json.dump(out, open(HERE / "result_late.json", "w"), indent=1)


def summarize():
    rows = [json.loads(x) for n in sorted(HERE.glob("result_hop_*.jsonl")) for x in open(n)]
    S = dict(hop_rules=len(rows), match=sum(r["match"] for r in rows))
    S["frozen"] = dict(Counter("|".join(r["frozen"]) for r in rows if r["frozen"] != ["constant", "constant"]))
    S["no_collision"] = dict(Counter("|".join(r["no_collision"]) for r in rows if r["no_collision"] != ["constant", "constant"]))
    S["harmonies_frozen"] = sum(any(x.startswith("harmony") for x in r["frozen"]) for r in rows)
    S["harmonies_without_the_collision"] = sum(any(x.startswith("harmony") for x in r["no_collision"]) for r in rows)
    late_path = HERE / "result_late.json"
    if late_path.exists():
        S["late"] = [{k: v for k, v in r.items() if k != "rule"} for r in json.load(open(late_path))]
    json.dump(S, open(HERE / "result_summary.json", "w"), indent=1)
    print(json.dumps(S, indent=1))


if __name__ == "__main__":
    {"hop": lambda: hop(int(sys.argv[2]), int(sys.argv[3])), "late": late, "summary": summarize}[sys.argv[1]]()
