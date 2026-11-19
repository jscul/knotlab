"""Referee R1 for RING-READ-20261118-001: LABELLED CROSS-CHECK that runs the study's own code read-only (ticket A's ringread.py
for the ring and its side-limited table, ticket B's reader3.py for the reader). It asks one question: one size past the study,
at round 30 (largest junction 11, so the reader needs D through 10), does the side-limited table differ from the exact one, and
does the study's reader still return the true junctions from each?

  ../../../.venv/bin/python -B crosscheck_reader.py T > referee_ringread_crosscheck_T.json      (from this directory)

The exact table is the referee's (referee_ringread.search_root: every bond of at most K + 1 distinctions, whatever its sides).
"""
import itertools
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "experiments/RING-READ-20261118-001B/RING-READ-20261118-001B-E001_incremental"))
import reader3 as R3  # noqa: E402  (the study's code, read-only)
import referee_ringread as RRD  # noqa: E402

R = R3.R


def exact_table(st, K):
    stars = [frozenset(s) for s in st]
    masks = [sum(1 << b for b in s) for s in stars]
    n, adj, own = RRD.graph(stars)
    adjd = {u: dict(v) for u, v in adj.items()}
    with Pool(20) as pool:
        res = pool.map(RRD.search_root, [(adjd, n, r, K + 1, 10 ** 9, K + 1, masks) for r in range(n)])
    best = {}
    for _, _, _, keep in res:
        for side, w in keep:
            bits = [b for b in range(w.bit_length()) if w >> b & 1]
            for p in itertools.combinations(bits, 2):
                if best.get(p, K + 2) > len(bits):
                    best[p] = len(bits)
    labels = sorted(own)
    return {p: min(best.get(p, K + 2), K + 2) - 1 for p in itertools.combinations(labels, 2)}


def main(T):
    t0 = time.time()
    P = R.grow(T)
    st = R.stars_of(P)
    truth = set(st)
    K = max(map(len, st))
    tab, _ = R.bond_table(st, 6, K)
    ex = exact_table(st, K)
    diff = sorted((p, tab[p], ex[p]) for p in tab if tab[p] != ex[p])
    out = {"T": T, "junctions": len(st), "largest junction": K, "table entries": len(tab),
           "entries where the side-6 table differs from the exact one (pair, side-6 D, exact D)": [[list(p), a, b] for p, a, b in diff],
           "seconds for the tables": round(time.time() - t0)}
    for name, t in (("side-6 table", tab), ("exact table", ex)):
        got = R3.r3(t, K)
        out[f"reader on the {name} at full horizon: exact"] = got == truth
        out[f"reader on the {name}: missed / spurious"] = [len(truth - got), len(got - truth)]
        for H in (K - 1, K - 2):
            pt = R.pooled(t, H)
            g2 = R3.r3(pt, H + 1)
            out[f"reader on the {name} pooled above D = {H}: exact"] = g2 == truth
            out[f"reader on the {name} pooled above D = {H}: missed / spurious"] = [len(truth - g2), len(g2 - truth)]
        print(json.dumps(out), file=sys.stderr, flush=True)
    out["seconds"] = round(time.time() - t0)
    return out


if __name__ == "__main__":
    print(json.dumps(main(int(sys.argv[1])), indent=1, default=str))
