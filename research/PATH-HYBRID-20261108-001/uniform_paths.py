#!/usr/bin/env python3
"""How the 16 uniform native paths of PATH-HYBRID-20261108-001A work, read from their row sequences (exact, a few seconds).

    .venv/bin/python3 -B research/PATH-HYBRID-20261108-001/uniform_paths.py   writes uniform_paths.json
- c2's law: which cells it reads, against the short arcs between the contacts of each middle ring.
- The end rings: from lag 3 on, a contact's input from its 3-cell shift end ring is its own value two and three lags back, so the
  end ring with its contact is a feedback shift register with polynomial x^3 + x + 1.
- The same paths with rule 150 on both end rings (a member of NATIVE-PATH-20261108-001B's first family): which contacts persist,
  the first lag at which c1 misses ring A, and whether a 3-cell rule-150 end ring's two cells are equal from lag 1 on.
- The rank of each native path's linear map."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "proofs/NATIVE-PATH-20261108-001A/NATIVE-PATH-20261108-001A-P001_paths_reduce_to_row_sequences"))
import path_lib as PL  # noqa: E402

W = PL.W
A_PATHS = ROOT / "artifacts/PATH-HYBRID-20261108-001A/PATH-HYBRID-20261108-001A-E001_broad_sweep/run/paths.json"
LAGS = 40


def times(rows, start, T):
    """the row of a cell at lags 0 .. T"""
    out, r = [start], start
    for _ in range(T):
        v, x = 0, r
        while x:
            low = x & -x
            v ^= rows[low.bit_length() - 1]
            x ^= low
        r = v
        out.append(r)
    return out


def rank(rows, N):
    rs, r = list(rows), 0
    for bit in range(N):
        piv = next((i for i in range(r, N) if rs[i] >> bit & 1), None)
        if piv is None:
            continue
        rs[r], rs[piv] = rs[piv], rs[r]
        for i in range(N):
            if i != r and rs[i] >> bit & 1:
                rs[i] ^= rs[r]
        r += 1
    return r


def short_arc(m, k):
    """the cells strictly between index 0 and index k of a ring of m cells on the short way round"""
    return list(range(1, k)) if k <= m - k else list(range(k + 1, m))


def one(x):
    rules, sizes, ks, laws = tuple(x[0]), tuple(x[1]), x[2], tuple(tuple(l) for l in x[3])
    rows, N, blocks = PL.linear_matrix(rules, sizes, ks, laws)
    rings, _, _ = PL.layout(sizes, ks)
    out = {"path": [list(rules), list(sizes), ks, [list(l) for l in laws]], "rank of the linear map": [rank(rows, N), N]}
    # c2: the cells it reads, by ring index, and the short arcs
    read = [j for j in range(N) if rows[1] >> j & 1]
    B, Cr = rings[1], rings[2]
    arcB = [B[j] for j in short_arc(sizes[1], ks[0])]
    arcC = [Cr[j] for j in short_arc(sizes[2], ks[1])]
    out["c2 reads exactly one short-arc cell on each middle ring"] = (sorted(read) == sorted(arcB + arcC) and len(arcB) == len(arcC) == 1)
    # the end rings: the contact's input from its end ring is its own value two and three lags back, from lag 3 on
    loops = []
    for c, R in ((0, rings[0]), (2, rings[3])):
        seq = times(rows, 1 << c, LAGS)
        nb = [times(rows, 1 << b, LAGS) for b in (R[1], R[-1])]                     # the contact's two end-ring neighbours
        loops.append(all(nb[0][T - 1] ^ nb[1][T - 1] == seq[T - 2] ^ seq[T - 3] for T in range(3, LAGS + 1)))
    out["end-ring input = own value two and three lags back, lags 3 to 40 (c1, c3)"] = loops
    # the same path with rule 150 on both end rings
    r150 = (150, rules[1], rules[2], 150)
    a = PL.analyze(r150, sizes, ks, laws)
    rows2, _, blocks2 = PL.linear_matrix(r150, sizes, ks, laws)
    mA = PL.mask(blocks2, "R0")
    s1 = times(rows2, 1 << 0, LAGS)
    first_miss = next((T for T in range(1, LAGS + 1) if not s1[T] & mA), None)
    R = PL.layout(sizes, ks)[0][0]
    a1, a2 = times(rows2, 1 << R[1], LAGS), times(rows2, 1 << R[2], LAGS)
    out["with rule 150 on the end rings"] = {"contacts persisting": a["persists"], "native": a["all persist"] and a["ends at the last contact"],
                                             "first lag at which c1 misses ring A": first_miss,
                                             "ring A's two cells equal at lags 1 to 40": all(a1[T] == a2[T] for T in range(1, LAGS + 1))}
    return out


def main():
    rows = json.loads(A_PATHS.read_text())["rows"]
    nat = sorted([r for r in rows if r[4]], key=lambda r: (r[2], r[0]))
    res = [one(x) for x in nat]
    summary = {
        "native paths": len(res),
        "c2 reads exactly one short-arc cell on each middle ring": sum(r["c2 reads exactly one short-arc cell on each middle ring"] for r in res),
        "both end rings are x^3 + x + 1 feedback loops": sum(all(r["end-ring input = own value two and three lags back, lags 3 to 40 (c1, c3)"]) for r in res),
        "ranks": sorted({tuple(r["rank of the linear map"]) for r in res}),
        "with rule 150 on the end rings: native": sum(r["with rule 150 on the end rings"]["native"] for r in res),
        "with rule 150 on the end rings: contacts persisting": sorted({tuple(r["with rule 150 on the end rings"]["contacts persisting"]) for r in res}),
        "with rule 150 on the end rings: first lag c1 misses ring A": sorted({r["with rule 150 on the end rings"]["first lag at which c1 misses ring A"] for r in res}, key=str),
        "with rule 150 on the end rings: ring A's cells equal from lag 1": sum(r["with rule 150 on the end rings"]["ring A's two cells equal at lags 1 to 40"] for r in res),
    }
    (HERE / "uniform_paths.json").write_text(json.dumps({"summary": summary, "paths": res}, indent=1) + "\n")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
