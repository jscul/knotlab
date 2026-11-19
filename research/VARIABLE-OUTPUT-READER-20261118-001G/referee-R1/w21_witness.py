"""Referee R1 for VARIABLE-OUTPUT-READER-20261118-001G: the width-21 pairs found by `referee_g.py cutoff 21`, where a source with
junctions of at most four distinctions and exactly two three-fresh joins has a rival whose table clipped through K = 4 is
isometric to its own and whose triple verdicts differ (the two-addition row's sharpness, below the study's width-27 example).

  ../../../.venv/bin/python -B w21_witness.py > referee_g_w21_witness.json      (from this directory)

For each pair: both presentations' supports, a legal history of each (found by search), the isometry, a triple whose verdict it
changes, the first horizon at which the clipped tables stop being isometric, and the full tables.
"""
import json
import sys
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/VARIABLE-OUTPUT-READER-20261118-001F/referee-R1"))
import referee_f as F  # noqa: E402


def _prep(T):
    J, n = F.supports(T)
    K, _ = F.bond_table(J, n)
    return T, max(map(len, J)) <= 4, n - 1 - 2 * T[0], F.invariant(F.clip(K, 4))


def main():
    levels = F.census(21)
    with Pool(20) as pool:
        rows = pool.map(_prep, levels[21], chunksize=32)
    bucket = defaultdict(list)
    for i, r in enumerate(rows):
        bucket[r[3]].append(i)
    out = []
    for i, (T, small, s, inv) in enumerate(rows):
        if not (small and s == 2):
            continue
        for k in bucket[inv]:
            if k == i:
                continue
            R = rows[k][0]
            JH, n = F.supports(T)
            JR, _ = F.supports(R)
            KH, _ = F.bond_table(JH, n)
            KR, _ = F.bond_table(JR, n)
            p = F.isometric(F.clip(KH, 4), F.clip(KR, 4))
            if p is None:
                continue
            lh, lr = F.legal_triples(T, JH), F.legal_triples(R, JR)
            img = {frozenset(p[x] for x in t) for t in lh}
            if img == lr:
                continue
            flip = next(iter(img - lr)) if img - lr else None
            pre = None
            if flip is not None:
                inv_p = {v: u for u, v in enumerate(p)}
                pre = sorted(inv_p[x] for x in flip)
            later = {L: F.isometric(F.clip(KH, L), F.clip(KR, L)) is not None for L in range(4, 12)}
            out.append({"source supports": JH, "source birth order (sites)": F.find_history(T),
                        "rival supports": JR, "rival birth order (sites)": F.find_history(R),
                        "source largest junction": max(map(len, JH)), "rival largest junction": max(map(len, JR)),
                        "source three-fresh joins": s, "rival junctions": len(JR), "source junctions": len(JH),
                        "isometry through K = 4 (source name -> rival name)": p,
                        "a legal source triple": pre, "its image (forbidden in the rival)": sorted(flip) if flip else None,
                        "legal triples (source, rival)": [len(lh), len(lr)],
                        "clipped tables isometric through K = L": later,
                        "full tables isometric": F.isometric(KH, KR) is not None})
    return out


if __name__ == "__main__":
    print(json.dumps(main(), indent=1, default=str))
