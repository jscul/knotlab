#!/usr/bin/env python3
"""Checks of the native paths found away from 3/5/5/3 (PATH-GROWTH-20261108-001B's map and NATIVE-PATH-S1), a few minutes.

    .venv/bin/python3 -B research/PATH-GROWTH-20261108-001/new_natives.py   writes new_natives.json
- Rule 150 on all four rings: every shape with end rings of 3 to 6 cells and middle rings of 4 to 8 (every position with the
  contacts at least two apart, as NATIVE-PATH-S1 ran it), every law: which shapes have native paths.
- Families: is any family (rules, laws, positions relative to the antipodal choice) native at more than one shape of the map?
- One size past: each native path of the map and of rule 150 everywhere with one more cell on every ring, on the end rings only and
  on the middle rings only (the middle contacts kept antipodal, or kept at their distance), every law kept.
- Full state spaces: the smallest native path at each new shape, by path_lib's full-state-space check (NATIVE-PATH-20261108-001A)."""
import importlib.util
import itertools
import json
import sys
import time
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments/PATH-GROWTH-20261108-001A/PATH-GROWTH-20261108-001A-E001_size_sweep"))
import growth_lib as G  # noqa: E402

PL = G.PL
MAP = ROOT / "artifacts/PATH-GROWTH-20261108-001B/PATH-GROWTH-20261108-001B-E001_where_growth_breaks/run/shapes.json"
LAWS = [("proposals",)] + [("self-blind", x, y) for x in sorted(PL.ULIN) for y in sorted(PL.ULIN)]
SPEC = importlib.util.spec_from_file_location(
    "native_path_check", ROOT / "proofs/NATIVE-PATH-20261108-001A/NATIVE-PATH-20261108-001A-P001_paths_reduce_to_row_sequences/check.py")


def r150_job(shape):
    sizes, ks = shape
    out = []
    for laws in itertools.product(LAWS, repeat=3):
        if G.native((150, 150, 150, 150), sizes, ks, laws) == "native":
            out.append([[150, 150, 150, 150], list(sizes), ks, [list(l) for l in laws]])
    return out


def grown(p):
    rules, sizes, ks, laws = tuple(p[0]), tuple(p[1]), p[2], tuple(tuple(l) for l in p[3])
    m0, m1, m2, m3 = sizes
    res = {}
    anti = lambda m, k, m_new: m_new // 2 if k == m // 2 else m_new - m_new // 2
    for name, new in (("every ring", (m0 + 1, m1 + 1, m2 + 1, m3 + 1)), ("end rings", (m0 + 1, m1, m2, m3 + 1)),
                      ("middle rings", (m0, m1 + 1, m2 + 1, m3))):
        verdicts = set()
        for rule in ("antipodal", "same distance"):
            if rule == "antipodal":
                nk = [anti(m1, ks[0], new[1]), anti(m2, ks[1], new[2])]
            else:
                nk = [ks[0] if ks[0] <= m1 - ks[0] else new[1] - (m1 - ks[0]), ks[1] if ks[1] <= m2 - ks[1] else new[2] - (m2 - ks[1])]
            verdicts.add(G.native(rules, new, nk, laws))
        res[name] = sorted(verdicts)
    return res


def full(p):
    mod = importlib.util.module_from_spec(SPEC)
    SPEC.loader.exec_module(mod)
    b = mod.brute(tuple(p[0]), tuple(p[1]), p[2], tuple(tuple(l) for l in p[3]))
    return None if b is None else (all(b[0]) and b[1])


def main():
    t0 = time.time()
    middle = [(m, k) for m in (4, 5, 6, 7, 8) for k in range(2, m - 1)]
    shapes = [((m0, m1, m2, m3), [k1, k2]) for m0 in (3, 4, 5, 6) for m3 in (3, 4, 5, 6) for (m1, k1) in middle for (m2, k2) in middle]
    data = json.loads(MAP.read_text())
    map_nat = data["native paths (rules, sizes, positions, laws, last contact's period)"]
    with Pool(16) as pool:
        r150 = [x for chunk in pool.map(r150_job, shapes, chunksize=4) for x in chunk]
        everything = [x[:4] for x in map_nat] + r150
        grow = pool.map(grown, everything, chunksize=4)
    # families across the map's shapes: a family is its rules, laws and which antipodal choice each middle ring takes
    fam = defaultdict(set)
    for x in map_nat:
        rules, sizes, ks, laws = x[:4]
        v = tuple(0 if k == m // 2 else 1 for k, m in zip(ks, sizes[1:3]))
        fam[(json.dumps(rules), json.dumps(laws), v)].add(tuple(sizes))
    smallest = {}
    for x in everything:
        key = tuple(x[1])
        if key != (3, 5, 5, 3) and key not in smallest:
            smallest[key] = x
    with Pool(4) as pool:
        verified = pool.map(full, list(smallest.values()))
    out = {
        "rule 150 on all four rings: native paths by shape and positions": [[list(k[0]), list(k[1]), v] for k, v in
                                                                            Counter((tuple(x[1]), tuple(x[2])) for x in r150).most_common()],
        "rule 150 on all four rings: native paths": len(r150),
        "map: native paths by shape": [[list(k), v] for k, v in Counter(tuple(x[1]) for x in map_nat).most_common()],
        "map: native paths by rules and shape": [[list(k[0]), list(k[1]), v] for k, v in Counter((tuple(x[0]), tuple(x[1])) for x in map_nat).most_common()],
        "map: last contact's period of the native paths": dict(Counter(str(x[4]) for x in map_nat)),
        "map: families native at more than one shape": sum(1 for s in fam.values() if len(s) > 1),
        "one size past (native paths of the map and of rule 150 everywhere)": {
            name: dict(Counter("/".join(g[name]) for g in grow)) for name in ("every ring", "end rings", "middle rings")},
        "one size past: paths still native in some way of growing": sum(1 for g in grow if any("native" in v for v in g.values())),
        "full state spaces: the smallest native path at each new shape": [[x, ok] for x, ok in zip(smallest.values(), verified)],
        "seconds": round(time.time() - t0, 1)}
    (HERE / "new_natives.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items() if not k.startswith("full")}, indent=1)[:5000])
    print("verified:", [(x[1], ok) for x, ok in zip(smallest.values(), verified)])


if __name__ == "__main__":
    main()
