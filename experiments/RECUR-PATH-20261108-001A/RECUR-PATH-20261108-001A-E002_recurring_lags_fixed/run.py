"""RECUR-PATH-20261108-001A-E002: composition at recurring lags across sizes, rerun with the every-lag reading fixed (exploratory;
see contract.json).

    .venv/bin/python3 -B run.py           the census (long-running); writes artifacts/RECUR-PATH-20261108-001A/
                                          RECUR-PATH-20261108-001A-E002_recurring_lags_fixed/run/result.json and families.json
    .venv/bin/python3 -B run.py --pilot   times random paths and prints no verdicts
Stage 1, full levels: every path of PATH-GROWTH-20261108-001A's families with four rings of 3 cells (antipodal contacts) and of 4
cells (where the antipodal and two-apart schedules coincide), and with four rings in the longer schedule. Stage 2: every family that
composes at recurring lags with every contact binding there (recur_lib's weakest recurring reading) at the smallest size of its
schedule is followed through the larger sizes until neither recurring reading holds, or to the largest size. Every verdict is exact
by the row-sequence reduction; a row sequence that does not repeat within 200,000 lags, or a joint cycle over 1,000,000 lags, is
undecided."""
from __future__ import annotations

import hashlib
import itertools
import json
import random
import sys
import time
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import recur_lib as R  # noqa: E402

G, PL = R.G, R.PL
C = PL.C
OUT = ROOT / "artifacts" / "RECUR-PATH-20261108-001A" / "RECUR-PATH-20261108-001A-E002_recurring_lags_fixed" / "run"
RULES = sorted(PL.LIN)
LAWS = [("proposals",)] + [("self-blind", x, y) for x in sorted(PL.ULIN) for y in sorted(PL.ULIN)]
VARIANTS = [(0, 0), (0, 1), (1, 0), (1, 1)]
READINGS = ("every lag", "recurring, persistent", "recurring, binding there")


def triple(a):
    return [a[k] for k in READINGS]


def level_job(item):
    """one rules tuple at one full level: every law triple and every distinct position variant"""
    schedule, s, rules = item
    counts, keep = Counter(), []
    variants = [(0, 0), (1, 1)] if schedule == "longer" else VARIANTS
    shapes = {}
    for v in variants:
        sizes, ks = G.shape(schedule, s, v)
        key = (sizes, tuple(ks))
        if key not in shapes:
            res = {}
            for laws in itertools.product(LAWS, repeat=3):
                a = R.analyze(*G.path(schedule, s, rules, laws, v))
                res[laws] = triple(a)
                counts["paths"] += 1
                counts["persistent"] += a["persist"] is True
                for k in READINGS:
                    counts[k] += a[k] is True
                counts["undecided"] += any(x is None for x in res[laws])
            shapes[key] = res
        for laws, t in shapes[key].items():
            if t[2] is not False:          # meets the weakest recurring reading, or undecided
                keep.append([list(rules), [list(l) for l in laws], list(v), t])
    return schedule, s, counts, keep


def follow_job(fam):
    """a family through the sizes of its schedule after the first, until neither recurring reading holds"""
    schedule, rules, laws, v, start = fam
    out = {}
    for s in [x for x in G.SIZES[schedule] if x > start]:
        a = R.analyze(*G.path(schedule, s, tuple(rules), tuple(tuple(l) for l in laws), tuple(v)))
        out[s] = triple(a)
        if out[s][1] is False and out[s][2] is False:
            break
    return [schedule, rules, laws, v, out]


def brute(rules, sizes, ks, laws, cap=4096):
    """the three readings off the full state space: binding by PROCESS-CHAIN-20261108-001A's blockwise decisiveness test"""
    nxt, N, blocks = PL.mixed_state_map(rules, sizes, ks, laws)
    n = len(sizes)
    names = [f"R{i}" for i in range(n)]
    L = PL.light_cone(sizes, ks)
    binds = lambda F, ns: F.min() != F.max() and not any(C.decides_outside(F, *blocks[x], N) for x in ns)
    cur = np.arange(len(nxt), dtype=np.int64)
    seen, own, ends = {}, [], []
    for T in range(1, cap + 1):
        cur = nxt[cur]
        key = hashlib.blake2b(cur.tobytes(), digest_size=16).digest()
        if key in seen:
            T1 = seen[key]
            cyc = range(T1 - 1, T - 1)
            some = any(ends[t] for t in cyc)
            persist = all(all(o) for o in own)
            every = persist and all(ends[t] for t in range(L - 1, T - 1)) and all(ends[t] for t in cyc)
            there = some and all(all(own[t]) for t in cyc if ends[t])
            return [every, persist and some, there]
        seen[key] = T
        Fs = [((cur >> c) & 1).astype(np.uint8) for c in range(n - 1)]
        own.append([binds(Fs[c], (names[c], names[c + 1])) for c in range(n - 1)])
        ends.append(binds(Fs[-1], (names[0], names[-1])))
    return None


def main():
    t0 = time.time()
    level_items = [("antipodal", 3, r) for r in itertools.product(RULES, repeat=4)] + \
                  [("antipodal", 4, r) for r in itertools.product(RULES, repeat=4)] + \
                  [("longer", 4, r) for r in itertools.product(RULES, repeat=3)]
    if "--pilot" in sys.argv:
        rng = random.Random(4)
        for s in (3, 4):
            s0 = time.time()
            for _ in range(5000):
                schedule, _, rules = rng.choice([x for x in level_items if x[1] == s and x[0] == "antipodal"])
                R.analyze(*G.path(schedule, s, rules, tuple(rng.choice(LAWS) for _ in range(3)), rng.choice(VARIANTS)))
            print("pilot: s =", s, "5,000 paths in", round(time.time() - s0, 1), "s")
        print("level items", len(level_items))
        return
    OUT.mkdir(parents=True, exist_ok=True)
    with Pool(16) as pool:
        res = pool.map(level_job, level_items, chunksize=4)
    levels, kept = defaultdict(Counter), defaultdict(list)
    for schedule, s, counts, keep in res:
        levels[f"{schedule} {s}"].update(counts)
        kept[(schedule, s)].extend(keep)
    # families to follow: antipodal from 3 cells, two apart from 4 cells (every variant: at 4 cells they give the same path), longer
    # from four rings
    fams = [("antipodal", x[0], x[1], x[2], 3) for x in kept[("antipodal", 3)]]
    fams += [("two apart", x[0], x[1], list(v), 4) for x in kept[("antipodal", 4)] for v in VARIANTS]
    fams += [("longer", x[0], x[1], x[2], 4) for x in kept[("longer", 4)]]
    first = {}
    for x in kept[("antipodal", 3)]:
        first[("antipodal", json.dumps(x[0]), json.dumps(x[1]), tuple(x[2]))] = x[3]
    for x in kept[("antipodal", 4)]:
        for v in VARIANTS:
            first[("two apart", json.dumps(x[0]), json.dumps(x[1]), v)] = x[3]
    for x in kept[("longer", 4)]:
        first[("longer", json.dumps(x[0]), json.dumps(x[1]), tuple(x[2]))] = x[3]
    with Pool(16) as pool:
        profiles = pool.map(follow_job, fams, chunksize=8)
    summary = {}
    for schedule in ("antipodal", "two apart", "longer"):
        sizes = list(G.SIZES[schedule])
        ps = [p for p in profiles if p[0] == schedule]
        for p in ps:
            p[4] = {sizes[0]: first[(schedule, json.dumps(p[1]), json.dumps(p[2]), tuple(p[3]))], **p[4]}
        def at_every(i, allow_none=False):
            return [p for p in ps if all(s in p[4] and (p[4][s][i] is True or (allow_none and p[4][s][i] is None)) for s in sizes)]
        runs = {}
        for i, k in enumerate(READINGS):
            c = Counter()
            for p in ps:
                n_ok = 0
                for s in sizes:
                    if s in p[4] and p[4][s][i] is True:
                        n_ok += 1
                    else:
                        break
                c[n_ok] += 1
            runs[k] = dict(sorted(c.items()))
        summary[schedule] = {
            "sizes": sizes, "families followed": len(ps),
            "families meeting each reading at every size": {k: len(at_every(i)) for i, k in enumerate(READINGS)},
            "families meeting each reading at every size, undecided allowed": {k: len(at_every(i, True)) for i, k in enumerate(READINGS)},
            "families by the number of consecutive sizes from the smallest meeting each reading": runs,
            "examples meeting a recurring reading at every size": [p for p in ps if all(s in p[4] and (p[4][s][1] or p[4][s][2]) for s in sizes)][:12]}
    # controls: the every-lag counts reproduce PATH-GROWTH-20261108-001A, and small paths agree on their full state spaces
    lv = {k: dict(v) for k, v in sorted(levels.items())}
    control_growth = lv["antipodal 3"]["every lag"] == 0 and lv["antipodal 4"]["every lag"] == 0 and lv["longer 4"]["every lag"] == 8
    sample = []
    for want in ([False, True, True], [False, False, True]):
        xs = [x for x in kept[("antipodal", 3)] if x[3] == want][:5]
        sample.extend(G.path("antipodal", 3, tuple(x[0]), tuple(tuple(l) for l in x[1]), tuple(x[2])) for x in xs)
    agree = []
    for p in sample:
        a = triple(R.analyze(*p))
        b = brute(*p)
        agree.append({"path": [list(p[0]), list(p[1]), p[2], [list(l) for l in p[3]]], "row sequences": a, "full state space": b,
                      "agree": a == b})
    result = {"experiment": "RECUR-PATH-20261108-001A-E002", "full levels": lv, "schedules": summary,
              "control: every-lag counts reproduce PATH-GROWTH-20261108-001A (0, 0 and 8)": control_growth,
              "control: small paths on their full state spaces": agree,
              "control passes": control_growth and all(x["agree"] for x in agree),
              "families meeting a recurring reading at every size of a schedule": {
                  s: {k: summary[s]["families meeting each reading at every size"][k] for k in READINGS[1:]} for s in summary},
              "seconds": round(time.time() - t0, 1)}
    (OUT / "families.json").write_text(json.dumps({"columns": ["schedule", "rules", "laws", "variant",
                                                               "readings by size (every lag, recurring persistent, recurring binding there)"],
                                                   "rows": profiles}) + "\n")
    (OUT / "result.json").write_text(json.dumps(result, indent=1, default=str) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "schedules"}, indent=1, default=str)[:4000])
    print(json.dumps({s: {k: v for k, v in d.items() if not k.startswith("examples")} for s, d in summary.items()}, indent=1, default=str))


if __name__ == "__main__":
    main()
