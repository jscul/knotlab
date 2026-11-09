"""FLIP-RULE-20261109-001A-E001: the flip rule on the snub and elongated tilings and their duals (exploratory; see contract.json).

    .venv/bin/python3 -B run.py    writes artifacts/FLIP-RULE-20261109-001A/FLIP-RULE-20261109-001A-E001_snub_and_elongated/run/result.json
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
import flip_lib as FL  # noqa: E402

TL = FL.TL
OUT = ROOT / "artifacts" / "FLIP-RULE-20261109-001A" / "FLIP-RULE-20261109-001A-E001_snub_and_elongated" / "run"
MAX_CONTACTS = 400


def hnf(N):
    for p in range(1, N + 1):
        if N % p == 0:
            for q in range(p):
                yield ((p, 0), (q, N // p))


def build(name, B):
    if name.startswith("snub square"):
        base = TL.torus("square", B)
        m = None if base is None else FL.snub(*base)
    elif name.startswith("snub hexagonal"):
        base = TL.torus("triangular", B)
        m = None if base is None else FL.snub(*base)
    else:
        (p, z), (q, r) = B
        m = FL.elongated(((p, 0), (q, 2 * r)))
    if m is not None and "dual" in name:
        m = TL.dual(*m)
    return m


TILINGS = ["snub square 3.3.4.3.4", "snub hexagonal 3.3.3.3.6", "elongated triangular 3.3.3.4.4",
           "Cairo pentagonal (dual of 3.3.4.3.4)", "floret pentagonal (dual of 3.3.3.3.6)", "prismatic pentagonal (dual of 3.3.3.4.4)"]
BASE = {"snub square 3.3.4.3.4": "snub square", "Cairo pentagonal (dual of 3.3.4.3.4)": "snub square dual",
        "snub hexagonal 3.3.3.3.6": "snub hexagonal", "floret pentagonal (dual of 3.3.3.3.6)": "snub hexagonal dual",
        "elongated triangular 3.3.3.4.4": "elongated", "prismatic pentagonal (dual of 3.3.3.4.4)": "elongated dual"}


def task(args):
    name, B = args
    m = build(BASE[name], B)
    if m is None:
        return name, B, None
    rot, edges = m
    if any(u == w for u, w in edges):
        return name, B, "loop"
    if len(edges) > MAX_CONTACTS:
        return name, B, "too large"
    sizes, contacts, n, out, rc = TL.network(rot, edges)
    bad = set(TL.persistent_all(sizes, contacts, n, out))
    flips = {e for e in range(len(edges)) if TL.has_flip(rot, edges, e)}
    persistent = set(range(n)) - bad
    return name, B, {"contacts": n, "rings": len(rot), "persistent": len(persistent), "with a flip": len(flips),
                     "persistent exactly the flipped": persistent == flips}


def main():
    t0 = time.time()
    jobs = [(name, B) for name in TILINGS for N in range(1, 13) for B in hnf(N)]
    with Pool(16) as pool:
        res = pool.map(task, jobs, chunksize=2)
    by = collections.defaultdict(list)
    for name, B, r in res:
        by[name].append(r)
    summary = {}
    for name, rows in by.items():
        read = [r for r in rows if isinstance(r, dict)]
        summary[name] = {"tori read": len(read), "skipped": len(rows) - len(read),
                         "persistent exactly the flipped on every torus read": all(r["persistent exactly the flipped"] for r in read),
                         "tori with every contact persistent": sum(1 for r in read if r["persistent"] == r["contacts"]),
                         "contacts persistent / read": [sum(r["persistent"] for r in read), sum(r["contacts"] for r in read)]}
    result = {"experiment": "FLIP-RULE-20261109-001A-E001", "summary": summary,
              "H1 holds on every tiling": all(s["persistent exactly the flipped on every torus read"] for s in summary.values()),
              "H2 tilings with a torus keeping every contact persistent": [k for k, s in summary.items() if s["tori with every contact persistent"]],
              "rows": [[nm, [list(b) for b in B], r] for nm, B, r in res], "seconds": round(time.time() - t0, 1)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
