#!/usr/bin/env python3
"""The native four-ring paths of PATH-HYBRID-20261108-001 in one file, for later work on them (native separation, cycles of rings,
restrictions), and a check that every one of them is native.

    .venv/bin/python3 -B research/PATH-HYBRID-20261108-001/verify_native_paths.py          check native_paths.json (about a minute)
    .venv/bin/python3 -B research/PATH-HYBRID-20261108-001/verify_native_paths.py --write  rebuild it from the two tickets' outputs

native_paths.json lists 1,136 paths: ticket A's 16 with one rule per ring and ticket B's 1,120 with a hybrid second middle ring.
Each path is [rules, sizes, positions, laws]:
- rules: one elementary rule per ring A, B, C, D; a hybrid ring is a list with one rule per cell, entries at contact cells unused;
- sizes: the four ring sizes; positions [k1, k2]: c2 sits at index k1 of ring B and c3 at index k2 of ring C;
- laws: one per contact, ["self-blind", u, v] with u and v in 12 (left neighbour), 10 (right neighbour) or 6 (both), the first for
  the contact's first ring.
The layout, laws and verdicts are those of path_lib (NATIVE-PATH-20261108-001A) as extended to hybrid rings by hybrid_lib
(PATH-HYBRID-20261108-001B): H.analyze(tuple(rules), tuple(sizes), positions, tuple(map(tuple, laws))) decides every verdict
exactly, and H.mixed_state_map gives the full dynamics. The check recomputes every verdict that way and confirms the four smallest
of each kind on their full state spaces."""
import hashlib
import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments/PATH-HYBRID-20261108-001B/PATH-HYBRID-20261108-001B-E001_hybrid_middles"))
import hybrid_lib as H  # noqa: E402

PL, C = H.PL, H.C
A_PATHS = ROOT / "artifacts/PATH-HYBRID-20261108-001A/PATH-HYBRID-20261108-001A-E001_broad_sweep/run/paths.json"
B_PATHS = ROOT / "artifacts/PATH-HYBRID-20261108-001B/PATH-HYBRID-20261108-001B-E001_hybrid_middles/run/paths.json"
OUT = HERE / "native_paths.json"


def norm(rules, sizes, ks, laws):
    return (tuple(r if isinstance(r, int) else tuple(r) for r in rules), tuple(sizes), tuple(ks), tuple(tuple(l) for l in laws))


def build():
    a = json.loads(A_PATHS.read_text())
    b = json.loads(B_PATHS.read_text())
    ia, ib = a["columns"].index("native"), b["columns"].index("native")
    uniform = [r[:4] for r in a["rows"] if r[ia]]
    hybrid = [r[:4] for r in b["rows"] if r[ib]]
    key = lambda r: (sum(r[1]), r[1], r[2], json.dumps(r[0]), json.dumps(r[3]))
    data = {"description": "Native four-ring paths across time of PATH-HYBRID-20261108-001 (see verify_native_paths.py)",
            "columns": ["rules", "sizes", "positions", "laws"],
            "uniform (ticket A)": sorted(uniform, key=key), "hybrid (ticket B)": sorted(hybrid, key=key),
            "sources": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in (A_PATHS, B_PATHS)}}
    OUT.write_text(json.dumps(data) + "\n")
    print("wrote", OUT.name, len(uniform), "uniform and", len(hybrid), "hybrid paths")


def verdict(path):
    rules, sizes, ks, laws = path
    rules = tuple(r if isinstance(r, int) else list(r) for r in rules)
    a = H.analyze(rules, tuple(sizes), list(ks), tuple(tuple(l) for l in laws))
    return a["all persist"] and a["ends at the last contact"] and a["last contact binds every ring"]


def full_state_space(path):
    """each contact binds its two rings at every lag, and c3 binds the end rings from the light cone on, read off the full dynamics"""
    rules, sizes, ks, laws = path
    rules = tuple(r if isinstance(r, int) else list(r) for r in rules)
    nxt, N, blocks = H.mixed_state_map(rules, tuple(sizes), list(ks), tuple(tuple(l) for l in laws))
    L = PL.light_cone(tuple(sizes), list(ks))
    names = ["R0", "R1", "R2", "R3"]
    binds = lambda F, ns: F.min() != F.max() and not any(C.decides_outside(F, *blocks[x], N) for x in ns)
    cur = np.arange(len(nxt), dtype=np.int64)
    seen, per = {}, {"p0": [], "p1": [], "p2": [], "ends": []}
    for T in range(1, 8193):
        cur = nxt[cur]
        key = hashlib.blake2b(cur.tobytes(), digest_size=16).digest()
        if key in seen:
            T1, period = seen[key], T - seen[key]
            hold = lambda seq, start: all(seq[min(start, T1) - 1:T1 + period - 1]) and all(seq[start - 1:])
            return all([hold(per["p0"], 1), hold(per["p1"], 1), hold(per["p2"], 1), hold(per["ends"], L)])
        seen[key] = T
        Fs = [((cur >> c) & 1).astype(np.uint8) for c in range(3)]
        per["p0"].append(binds(Fs[0], ("R0", "R1")))
        per["p1"].append(binds(Fs[1], ("R1", "R2")))
        per["p2"].append(binds(Fs[2], ("R2", "R3")))
        per["ends"].append(binds(Fs[2], ("R0", "R3")))
    return None


def main():
    if "--write" in sys.argv:
        build()
    data = json.loads(OUT.read_text())
    paths = data["uniform (ticket A)"] + data["hybrid (ticket B)"]
    with Pool(16) as pool:
        ok = pool.map(verdict, paths, chunksize=16)
        smallest = data["uniform (ticket A)"][:4] + data["hybrid (ticket B)"][:4]
        full = pool.map(full_state_space, smallest)
    res = {"paths": len(paths), "native by row sequences (and the last contact binding every ring)": sum(ok),
           "smallest eight confirmed on full state spaces": sum(1 for f in full if f)}
    print(json.dumps(res))
    sys.exit(0 if all(ok) and all(full) else 1)


if __name__ == "__main__":
    main()
