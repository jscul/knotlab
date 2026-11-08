"""PATH-GROWTH-20261108-001A-E001: families of paths native at every size (exploratory; see contract.json).

    .venv/bin/python3 -B run.py           the sweep (long-running); writes artifacts/PATH-GROWTH-20261108-001A/
                                          PATH-GROWTH-20261108-001A-E001_size_sweep/run/result.json and families.json
    .venv/bin/python3 -B run.py --pilot   times random paths of the full levels and prints no verdicts
Full levels: every family of four rings of s cells at s = 3, 4 and 5 (the antipodal and two-apart schedules coincide at s = 4 and 5),
and every "longer" family at n = 4 and 5 rings. Every family native at a full level is then followed through every size of its
schedule. Every verdict is exact by NATIVE-PATH-20261108-001A's row-sequence reduction (growth_lib.native); a row sequence that does
not repeat within 200,000 lags is undecided."""
from __future__ import annotations

import hashlib
import importlib.util
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
sys.path.insert(0, str(HERE))
import growth_lib as G  # noqa: E402

PL = G.PL
OUT = ROOT / "artifacts" / "PATH-GROWTH-20261108-001A" / "PATH-GROWTH-20261108-001A-E001_size_sweep" / "run"
RULES = sorted(PL.LIN)
LAWS = [("proposals",)] + [("self-blind", x, y) for x in sorted(PL.ULIN) for y in sorted(PL.ULIN)]
VARIANTS = [(0, 0), (0, 1), (1, 0), (1, 1)]
SPEC = importlib.util.spec_from_file_location(
    "native_path_check", ROOT / "proofs/NATIVE-PATH-20261108-001A/NATIVE-PATH-20261108-001A-P001_paths_reduce_to_row_sequences/check.py")


def level_job(item):
    """one rules tuple at one full level: every law triple and every distinct position variant"""
    schedule, s, rules = item
    counts, natives = Counter(), []
    variants = [(0, 0), (1, 1)] if schedule == "longer" else VARIANTS
    by_shape = {}                                      # variants that give the same path at this size share its verdicts
    for v in variants:
        sizes, ks = G.shape(schedule, s, v)
        key = (sizes, tuple(ks))
        if key not in by_shape:
            verdicts = {}
            for laws in itertools.product(LAWS, repeat=3):
                r, sz, k, lw = G.path(schedule, s, rules, laws, v)
                verdicts[laws] = G.native(r, sz, k, lw)
                counts["paths"] += 1
                counts[verdicts[laws]] += 1
            by_shape[key] = verdicts
        for laws, verdict in by_shape[key].items():
            if verdict != "not native":
                natives.append([list(rules), [list(l) for l in laws], list(v), verdict])
    return schedule, s, counts, natives


def follow_job(fam):
    """a family through every size of its schedule"""
    schedule, rules, laws, v = fam
    out = {}
    for s in G.SIZES[schedule]:
        variant = tuple(v)
        r, sz, k, lw = G.path(schedule, s, tuple(rules), tuple(tuple(l) for l in laws), variant)
        out[s] = G.native(r, sz, k, lw)
    return [schedule, rules, laws, v, out]


def brute(rules, sizes, ks, laws):
    mod = importlib.util.module_from_spec(SPEC)
    SPEC.loader.exec_module(mod)
    b = mod.brute(rules, sizes, ks, laws)
    return None if b is None else (all(b[0]) and b[1])


def main():
    t0 = time.time()
    four = [("antipodal", s, r) for s in (3, 4, 5) for r in itertools.product(RULES, repeat=4)]
    longer = [("longer", n, r) for n in (4, 5) for r in itertools.product(RULES, repeat=3)]
    if "--pilot" in sys.argv:
        rng = random.Random(1)
        for name, pool_ in (("s = 5", [x for x in four if x[1] == 5]), ("n = 5", [x for x in longer if x[1] == 5])):
            s0 = time.time()
            for _ in range(2000):
                schedule, s, rules = rng.choice(pool_)
                v = (0, 0) if schedule == "longer" else rng.choice(VARIANTS)
                G.native(*G.path(schedule, s, rules, tuple(rng.choice(LAWS) for _ in range(3)), v))
            print("pilot:", name, "2,000 paths in", round(time.time() - s0, 1), "s")
        print("items", len(four) + len(longer))
        return
    OUT.mkdir(parents=True, exist_ok=True)
    with Pool(16) as pool:
        res = pool.map(level_job, four + longer, chunksize=4)
    levels, found = defaultdict(Counter), defaultdict(list)
    for schedule, s, counts, natives in res:
        levels[f"{schedule} {s}"].update(counts)
        for x in natives:
            found[(schedule, s)].append(x)
    # every family native (or undecided) at a full level, in each schedule it belongs to
    fams = set()
    for (schedule, s), xs in found.items():
        for rules, laws, v, verdict in xs:
            key = (json.dumps(rules), json.dumps(laws), tuple(v))
            if schedule == "longer":
                fams.add(("longer",) + key)
            else:
                if s in (3, 4, 5):
                    fams.add(("antipodal",) + key)
                if s in (4, 5):
                    fams.add(("two apart",) + key)
    fam_list = sorted(fams)
    with Pool(16) as pool:
        profiles = pool.map(follow_job, [(f[0], json.loads(f[1]), json.loads(f[2]), list(f[3])) for f in fam_list], chunksize=1)
    summary = {}
    for schedule in ("antipodal", "two apart", "longer"):
        ps = [p for p in profiles if p[0] == schedule]
        sizes = list(G.SIZES[schedule])
        every = [p for p in ps if all(p[4][s] == "native" for s in sizes)]
        every_or_und = [p for p in ps if all(p[4][s] != "not native" for s in sizes)]
        run_len = Counter()
        for p in ps:
            best = cur = 0
            for s in sizes:
                cur = cur + 1 if p[4][s] == "native" else 0
                best = max(best, cur)
            run_len[best] += 1
        summary[schedule] = {
            "sizes": sizes, "families followed": len(ps),
            "native at each size (followed families)": {s: sum(1 for p in ps if p[4][s] == "native") for s in sizes},
            "undecided at each size (followed families)": {s: sum(1 for p in ps if p[4][s] == "undecided") for s in sizes},
            "families by their longest run of consecutive native sizes": dict(sorted(run_len.items())),
            "native at every size": len(every), "native or undecided at every size": len(every_or_und),
            "examples native at every size": every[:10], "examples native or undecided at every size": every_or_und[:10]}
    # overlaps at the full levels (four-ring families): native at s and at s + 1
    key4 = lambda x: (json.dumps(x[0]), json.dumps(x[1]), tuple(x[2]))
    nat = {s: {key4(x) for x in found[("antipodal", s)] if x[3] == "native"} for s in (3, 4, 5)}
    # at s = 4 every variant gives the same path, so a family native at 4 is native in all four variants
    nat4_any = {(a, b) for (a, b, v) in nat[4]}
    overlaps = {"native at 3 and 4": sum(1 for (a, b, v) in nat[3] if (a, b) in nat4_any),
                "native at 4 and 5": sum(1 for (a, b, v) in nat[5] if (a, b) in nat4_any),
                "native at 3, 4 and 5 (antipodal: same variant at 3 and 5)": sum(1 for (a, b, v) in nat[3] if (a, b) in nat4_any and (a, b, v) in nat[5])}
    # control: the ten smallest native paths of the full levels on their full state spaces
    smallest = []
    for (schedule, s) in sorted(found, key=lambda x: (x[1], x[0])):
        for rules, laws, v, verdict in found[(schedule, s)]:
            if verdict == "native":
                smallest.append(G.path(schedule, s, tuple(rules), tuple(tuple(l) for l in laws), tuple(v)))
    smallest = sorted(smallest, key=lambda p: (sum(p[1]), p[1], p[2]))[:10]
    verified = []
    for p in smallest:
        b = brute(*p)
        verified.append({"path": [list(p[0]), list(p[1]), p[2], [list(l) for l in p[3]]], "full state space agrees": b})
    result = {"experiment": "PATH-GROWTH-20261108-001A-E001",
              "full levels": {k: dict(v) for k, v in sorted(levels.items())},
              "overlaps at the full levels": overlaps, "schedules": summary,
              "H1 (some family is native at every size of its schedule)": any(summary[s]["native at every size"] for s in summary),
              "control: the ten smallest native paths on their full state spaces": verified,
              "control passes": all(v["full state space agrees"] for v in verified) if verified else None,
              "seconds": round(time.time() - t0, 1)}
    (OUT / "families.json").write_text(json.dumps({"columns": ["schedule", "rules", "laws", "variant", "verdict by size"],
                                                   "rows": profiles}) + "\n")
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "schedules"}, indent=1)[:3000])
    print(json.dumps({s: {k: v for k, v in d.items() if not k.startswith("examples")} for s, d in summary.items()}, indent=1))


if __name__ == "__main__":
    main()
