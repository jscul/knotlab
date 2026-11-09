"""PLANE-PLAIN-20261109-001A-E001: which contacts of periodic plane tilings persist (exploratory; see contract.json).

    .venv/bin/python3 -B run.py    writes artifacts/PLANE-PLAIN-20261109-001A/PLANE-PLAIN-20261109-001A-E001_tilings/run/result.json
"""
import collections
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import tiling_lib as TL  # noqa: E402

OUT = ROOT / "artifacts" / "PLANE-PLAIN-20261109-001A" / "PLANE-PLAIN-20261109-001A-E001_tilings" / "run"
M, Tr, D = TL.medial, TL.truncation, TL.dual
TILINGS = {
    "square 4.4.4.4": ("square", lambda t: t),
    "triangular 3.3.3.3.3.3": ("triangular", lambda t: t),
    "honeycomb 6.6.6": ("honeycomb", lambda t: t),
    "kagome 3.6.3.6": ("honeycomb", lambda t: M(*t)),
    "truncated square 4.8.8": ("square", lambda t: Tr(*t)),
    "truncated hexagonal 3.12.12": ("honeycomb", lambda t: Tr(*t)),
    "rhombitrihexagonal 3.4.6.4": ("honeycomb", lambda t: M(*M(*t))),
    "truncated trihexagonal 4.6.12": ("honeycomb", lambda t: Tr(*M(*t))),
    "rhombille (dual of 3.6.3.6)": ("honeycomb", lambda t: D(*M(*t))),
    "tetrakis square (dual of 4.8.8)": ("square", lambda t: D(*Tr(*t))),
    "triakis triangular (dual of 3.12.12)": ("honeycomb", lambda t: D(*Tr(*t))),
    "deltoidal trihexagonal (dual of 3.4.6.4)": ("honeycomb", lambda t: D(*M(*M(*t)))),
    "kisrhombille (dual of 4.6.12)": ("honeycomb", lambda t: D(*Tr(*M(*t)))),
}
INDEX = range(3, 13)
MAX_CONTACTS = 400


def hnf(N):
    for p in range(1, N + 1):
        if N % p == 0:
            for q in range(p):
                yield ((p, 0), (q, N // p))


def task(args):
    name, B = args
    kind, op = TILINGS[name]
    base = TL.torus(kind, B)
    if base is None:
        return name, B, None
    try:
        rot, edges = op(base)
    except ValueError:
        return name, B, "loop"
    if any(u == w for u, w in edges):
        return name, B, "loop"   # the contract's skip rule: a result that joins a ring to itself
    if len(edges) > MAX_CONTACTS:
        return name, B, "too large"
    sizes, contacts, n, out, rc = TL.network(rot, edges)
    bad = set(TL.persistent_all(sizes, contacts, n, out))
    flips = {e for e in range(len(edges)) if TL.has_flip(rot, edges, e)}
    persistent = set(range(n)) - bad
    return name, B, {"contacts": n, "rings": len(rot), "persistent": len(persistent), "with a flip": len(flips),
                     "persistent exactly the flipped": persistent == flips,
                     "persistent without a flip": len(persistent - flips), "flipped but not persistent": len(flips - persistent)}


def main():
    t0 = time.time()
    jobs = [(name, B) for name in TILINGS for N in INDEX for B in hnf(N)]
    with Pool(16) as pool:
        res = pool.map(task, jobs, chunksize=2)
    by = collections.defaultdict(list)
    for name, B, r in res:
        by[name].append((B, r))
    summary = {}
    for name, rows in by.items():
        read = [r for B, r in rows if isinstance(r, dict)]
        summary[name] = {"tori read": len(read), "skipped (invalid, loop or over the size cap)": len(rows) - len(read),
                         "H1 persistent exactly the flipped, on every torus read": all(r["persistent exactly the flipped"] for r in read),
                         "tori with every contact persistent": sum(1 for r in read if r["persistent"] == r["contacts"]),
                         "contacts persistent / read": [sum(r["persistent"] for r in read), sum(r["contacts"] for r in read)]}
    full = [nm for nm, s in summary.items() if s["tori read"] and s["tori with every contact persistent"] == s["tori read"]]
    some = [nm for nm, s in summary.items() if s["tori with every contact persistent"] > 0]
    result = {"experiment": "PLANE-PLAIN-20261109-001A-E001", "summary": summary,
              "H1 holds on every tiling": all(s["H1 persistent exactly the flipped, on every torus read"] for s in summary.values()),
              "H2 tilings with every contact persistent on every torus read": full,
              "tilings with some torus fully persistent": some,
              "rows": [[nm, [list(b) for b in B], r] for nm, B, r in res], "seconds": round(time.time() - t0, 1)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
