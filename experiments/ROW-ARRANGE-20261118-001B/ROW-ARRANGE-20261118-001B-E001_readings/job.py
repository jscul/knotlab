"""Shared-runner job for ROW-ARRANGE-20261118-001B-E001.

Cases:
- full-<n>-<i>: shard i of the exhaustive one-split population at n = 7 and n = 8 (every class), and the cheapest population at
  n = 4..12 (one shard each): per class, k, lam, N and every reading's name.
- family<m>-<i>: one size past, by families (the advisor's design): 25 parents of m - 1 distinctions drawn at random (seed i) from
  the exhaustive population, and every one-split child of each at m distinctions; m = 9, and m = 8 as the calibration against the
  exhaustive n = 8.
setup() enumerates the populations once before the workers fork."""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import readings as RD  # noqa: E402

RADII = [2, 4, 6, 8, 10, 12, 14]
SHARDS = {7: 4, 8: 48}
POP = {}


def setup(params):
    canon, lv = RD.CB.reachable("one-split", 8)
    for m in (7, 8):
        POP[("one-split", m)] = [list(canon.reps[c][0]) for c in lv[m]]
    canon, lv = RD.CB.reachable("cheap", 12)
    for m in range(4, 13):
        POP[("cheap", m)] = [list(canon.reps[c][0]) for c in lv[m]]


def cases():
    for n in (7, 8):
        for i in range(SHARDS[n]):
            yield f"full-{n}-{i}", {"pop": "one-split", "n": n, "shard": i, "of": SHARDS[n]}
    for n in range(4, 13):
        yield f"cheap-{n}", {"pop": "cheap", "n": n, "shard": 0, "of": 1}
    for m in (8, 9):
        for i in range(12):
            yield f"family{m}-{i}", {"family": m, "seed": 1000 * m + i, "parents": 25}


def reading_row(st, n):
    D = RD.table(st, n)
    k, lam = RD.targets(st, n)
    row = {"k": k, "lam": lam, "N": len(st), **RD.diagnostics(D)}
    for name, f in RD.READINGS.items():
        row[name] = RD.intern(f(D))
    for r in RADII:
        row[f"B{r}"] = RD.intern(RD.read_B(D, r))
    return row


def children(st, n):
    out = []
    for (a0, a1) in RD.R.extensions(st, n, 3):
        if RD.pc(a0) + RD.pc(a1) <= len(st) + 2:
            out.append(RD.R.apply(st, n, a0, a1))
    return out


def run(case_id, payload):
    if "family" in payload:
        m = payload["family"]
        rng = random.Random(payload["seed"])
        pool = POP[("one-split", m - 1)]
        out = []
        for p in rng.sample(range(len(pool)), payload["parents"]):
            for st in children(pool[p], m - 1):
                out.append({"parent": p, "states": st, **reading_row(st, m)})
        return {"bases": out}
    bases = POP[(payload["pop"], payload["n"])]
    sel = range(payload["shard"], len(bases), payload["of"])
    return {"rows": [{"i": i, **reading_row(bases[i], payload["n"])} for i in sel]}
