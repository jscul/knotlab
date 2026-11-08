"""PATH-GROWTH-20261108-001B-E001: where growth breaks a native path (exploratory; see contract.json).

    .venv/bin/python3 -B run.py           the measure (long-running); writes artifacts/PATH-GROWTH-20261108-001B/
                                          PATH-GROWTH-20261108-001B-E001_where_growth_breaks/run/result.json and shapes.json
    .venv/bin/python3 -B run.py --pilot   times random paths and prints no verdicts
Part 1, the funnel: at each full level of PATH-GROWTH-20261108-001A (four rings of 3, 4 or 5 cells; 4 or 5 rings), how many paths keep
all three contacts persistent, how many of those are native, and the last contact's row period. Part 2, a map of shapes around
3/5/5/3: end rings of 3, 4 or 5 cells, both middle rings of m = 4 to 7 cells with antipodal contacts (index m // 2 or m - m // 2,
per ring), every linear rule on each ring and every law at each contact. Verdicts are exact by the row-sequence reduction; a row
sequence that does not repeat within 200,000 lags is undecided."""
from __future__ import annotations

import itertools
import json
import random
import sys
import time
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "experiments/PATH-GROWTH-20261108-001A/PATH-GROWTH-20261108-001A-E001_size_sweep"))
import growth_lib as G  # noqa: E402

PL = G.PL
OUT = ROOT / "artifacts" / "PATH-GROWTH-20261108-001B" / "PATH-GROWTH-20261108-001B-E001_where_growth_breaks" / "run"
RULES = sorted(PL.LIN)
LAWS = [("proposals",)] + [("self-blind", x, y) for x in sorted(PL.ULIN) for y in sorted(PL.ULIN)]
VARIANTS = [(0, 0), (0, 1), (1, 0), (1, 1)]
CAP = 200000


def orbit(rows, start, test, L):
    """(holds, period): test at every lag from L on (all phases of the cycle included), or (None, None) if no repeat within CAP"""
    seen, seq, r, T = {}, [], start, 0
    tabs = None
    while T < CAP:
        if T == 64:
            tabs = G._tables(rows)
        r = G._step(rows, r) if tabs is None else G._step_tab(tabs, r)
        T += 1
        if r in seen:
            T1 = seen[r]
            return all(test(seq[t - 1]) for t in range(min(T1, L), T)), T - T1
        seen[r] = T
        seq.append(r)
    return None, None


def funnel(rules, sizes, ks, laws):
    """("not persistent" | "persistent" | "native" | "undecided", the last contact's period or None)"""
    rows, N, blocks = PL.linear_matrix(rules, sizes, ks, laws)
    n = len(sizes)
    m = [PL.mask(blocks, f"R{i}") for i in range(n)]
    undecided = False
    for c in [n - 2] + list(range(n - 2)):
        ok = G.contact_ok(rows, 1 << c, lambda r, a=m[c], b=m[c + 1]: bool(r & a) and bool(r & b), lambda r: True, 1, CAP)
        if ok is False:
            return "not persistent", None
        undecided |= ok is None
    if undecided:
        return "undecided", None
    L = PL.light_cone(sizes, ks)
    ends, period = orbit(rows, 1 << (n - 2), lambda r: bool(r & m[0]) and bool(r & m[-1]), L)
    if ends is None:
        return "undecided", None
    return ("native" if ends else "persistent"), period


def bucket(p):
    return "1" if p == 1 else "2-12" if p <= 12 else "13-100" if p <= 100 else "101-1000" if p <= 1000 else ">1000"


def level_job(item):
    schedule, s, rules = item
    counts, periods, natives = Counter(), Counter(), []
    variants = [(0, 0), (1, 1)] if schedule == "longer" else VARIANTS
    shapes = set()
    for v in variants:
        sizes, ks = G.shape(schedule, s, v)
        if (sizes, tuple(ks)) in shapes:
            continue
        shapes.add((sizes, tuple(ks)))
        for laws in itertools.product(LAWS, repeat=3):
            verdict, per = funnel(*G.path(schedule, s, rules, laws, v))
            counts["paths"] += 1
            counts[verdict] += 1
            if verdict in ("persistent", "native"):
                periods[(verdict, bucket(per))] += 1
    return f"{schedule} {s}", counts, periods


def shape_job(item):
    m0, m3, m, v, rules = item
    k = lambda x: m // 2 if x == 0 else m - m // 2
    sizes, ks = (m0, m, m, m3), [k(v[0]), k(v[1])]
    counts, natives = Counter(), []
    for laws in itertools.product(LAWS, repeat=3):
        verdict, per = funnel(tuple(rules), sizes, ks, laws)
        counts["paths"] += 1
        counts[verdict] += 1
        if verdict == "native":
            natives.append([list(rules), list(sizes), ks, [list(l) for l in laws], per])
    return (sizes, tuple(ks)), counts, natives


def shape_items():
    out = []
    for m0, m3 in itertools.product((3, 4, 5), repeat=2):
        for m in (4, 5, 6, 7):
            seen = set()
            for v in VARIANTS:
                ks = (m // 2 if v[0] == 0 else m - m // 2, m // 2 if v[1] == 0 else m - m // 2)
                if ks in seen:
                    continue
                seen.add(ks)
                out.extend((m0, m3, m, v, r) for r in itertools.product(RULES, repeat=4))
    return out


def main():
    t0 = time.time()
    levels = [("antipodal", s, r) for s in (3, 4, 5) for r in itertools.product(RULES, repeat=4)] + \
             [("longer", n, r) for n in (4, 5) for r in itertools.product(RULES, repeat=3)]
    shapes = shape_items()
    if "--pilot" in sys.argv:
        rng = random.Random(3)
        s0 = time.time()
        for _ in range(20000):
            m0, m3, m, v, rules = rng.choice(shapes)
            ks = [m // 2 if v[0] == 0 else m - m // 2, m // 2 if v[1] == 0 else m - m // 2]
            funnel(rules, (m0, m, m, m3), ks, tuple(rng.choice(LAWS) for _ in range(3)))
        print("pilot: 20,000 map paths in", round(time.time() - s0, 1), "s; level items", len(levels), "map items", len(shapes),
              "map paths", len(shapes) * 1000)
        return
    OUT.mkdir(parents=True, exist_ok=True)
    with Pool(16) as pool:
        lev = pool.map(level_job, levels, chunksize=4)
        shp = pool.map(shape_job, shapes, chunksize=8)
    funnel_counts, funnel_periods = defaultdict(Counter), defaultdict(Counter)
    for name, counts, periods in lev:
        funnel_counts[name].update(counts)
        funnel_periods[name].update(periods)
    by_shape, natives = defaultdict(Counter), []
    for key, counts, nat in shp:
        by_shape[key].update(counts)
        natives.extend(nat)
    shape_rows = [[list(k[0]), list(k[1]), dict(v)] for k, v in sorted(by_shape.items())]
    result = {
        "experiment": "PATH-GROWTH-20261108-001B-E001",
        "part 1, the funnel at the full levels": {k: dict(v) for k, v in sorted(funnel_counts.items())},
        "part 1, the last contact's row period (verdict, period range: paths)": {
            k: {f"{a} {b}": c for (a, b), c in sorted(v.items())} for k, v in sorted(funnel_periods.items())},
        "part 2, shapes with a native path": [r for r in shape_rows if r[2].get("native")],
        "part 2, persistent and native paths by end-ring and middle-ring sizes": {
            f"{m0}/{m}/{m}/{m3}": {"paths": sum(r[2]["paths"] for r in shape_rows if r[0] == [m0, m, m, m3]),
                                    "persistent or native": sum(r[2].get("persistent", 0) + r[2].get("native", 0) for r in shape_rows if r[0] == [m0, m, m, m3]),
                                    "native": sum(r[2].get("native", 0) for r in shape_rows if r[0] == [m0, m, m, m3]),
                                    "undecided": sum(r[2].get("undecided", 0) for r in shape_rows if r[0] == [m0, m, m, m3])}
            for m0 in (3, 4, 5) for m3 in (3, 4, 5) for m in (4, 5, 6, 7)},
        "control: 3/5/5/3 gives PATH-HYBRID-20261108-001A's 16 native and 13,464 persistent paths, and 3/4/4/3 its 3,728 persistent and none native": None,
        "native paths in the map": len(natives),
        "native paths in the map by rules (top 12)": [[list(k), v] for k, v in Counter(tuple(x[0]) for x in natives).most_common(12)],
        "seconds": None}
    c3553 = result["part 2, persistent and native paths by end-ring and middle-ring sizes"]["3/5/5/3"]
    c3443 = result["part 2, persistent and native paths by end-ring and middle-ring sizes"]["3/4/4/3"]
    result["control: 3/5/5/3 gives PATH-HYBRID-20261108-001A's 16 native and 13,464 persistent paths, and 3/4/4/3 its 3,728 persistent and none native"] = (
        c3553["native"] == 16 and c3553["persistent or native"] == 13464 and c3443["persistent or native"] == 3728 and c3443["native"] == 0)
    result["seconds"] = round(time.time() - t0, 1)
    (OUT / "shapes.json").write_text(json.dumps({"columns": ["sizes", "positions", "counts"], "rows": shape_rows,
                                                 "native paths (rules, sizes, positions, laws, last contact's period)": natives}) + "\n")
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if not k.startswith("part 2, persistent")}, indent=1)[:6000])


if __name__ == "__main__":
    main()
