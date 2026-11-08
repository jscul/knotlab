#!/usr/bin/env python3
"""Does the proof of RECUR-PROOF-20261108-001A cover the other families of RECUR-PATH-20261108-001A? (exact, under a minute)

    .venv/bin/python3 -B research/RECUR-PROOF-20261108-001/rule90_scope.py   writes rule90_scope.json
- Rule 102: the proof's check 1 shows every two-apart family with a rule-102 ring is a mirror image of a rule-60 family.
- The 196 longer families (end rings of 3 cells, middle rings of 5, 4 to 9 rings), most with rule-90 rings: for each, at 4 to 12 rings,
  (a) does every contact read exactly two partners, one on each ring, as Lemma 1 needs; (b) does every contact keep one fixed
  first-row cell of each of its rings at every lag (a uniform witness); (c) the last contact's composing share, and whether it is a
  power of two as in the proof; (d) the readings themselves, recurring with every contact persistent, at 4 to 20 rings."""
import importlib.util
import json
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
E2 = ROOT / "experiments/RECUR-PATH-20261108-001A/RECUR-PATH-20261108-001A-E002_recurring_lags_fixed"
FAMS = ROOT / "artifacts/RECUR-PATH-20261108-001A/RECUR-PATH-20261108-001A-E002_recurring_lags_fixed/run/families.json"
sys.path.insert(0, str(E2))
spec = importlib.util.spec_from_file_location("recur_run", E2 / "run.py")
RUN = importlib.util.module_from_spec(spec)
spec.loader.exec_module(RUN)
R, G, PL = RUN.R, RUN.G, RUN.PL


def partners_ok(rules, sizes, ks, laws):
    """every contact reads exactly two cells that read only it and themselves, one on each of its rings, plus anything else"""
    rows, N, blocks = PL.linear_matrix(rules, sizes, ks, laws)
    n = len(sizes)
    m = [PL.mask(blocks, f"R{i}") for i in range(n)]
    for c in range(n - 1):
        reads = [j for j in range(N) if rows[c] >> j & 1]
        part = [j for j in reads if rows[j] == ((1 << c) | (1 << j))]
        if not (any(m[c] >> j & 1 for j in part) and any(m[c + 1] >> j & 1 for j in part)):
            return False
    return True


def main():
    t0 = time.time()
    rows = json.loads(FAMS.read_text())["rows"]
    fams = [p for p in rows if p[0] == "longer" and all(str(s) in p[4] and p[4][str(s)][1] is True for s in G.SIZES["longer"])]
    lemma, witness, shares, power2, holds = Counter(), Counter(), Counter(), Counter(), Counter()
    for p in fams:
        rules3, laws3, v = tuple(p[1]), tuple(tuple(l) for l in p[2]), tuple(p[3])
        for n in range(4, 13):
            path = G.path("longer", n, rules3, laws3, v)
            lemma[partners_ok(*path)] += 1
            rows_, N, blocks = PL.linear_matrix(*path)
            msk = [PL.mask(blocks, f"R{i}") for i in range(n)]
            ok = True
            for c in range(n - 1):
                o = R.orbit(rows_, 1 << c, 10 ** 6)
                inter = ~0
                for T in range(1, o[1] + o[2]):
                    inter &= R.row_at(o, T)
                ok &= bool(inter & msk[c]) and bool(inter & msk[c + 1])
            witness[ok] += 1
            o = R.orbit(rows_, 1 << (n - 2), 10 ** 6)
            cyc = [o[0][o[1] - 1 + j] for j in range(o[2])]
            share = sum(1 for r in cyc if r & msk[0] and r & msk[-1]) / o[2]
            shares[round(share, 4)] += 1
            power2[share > 0 and (1 / share).is_integer() and (int(1 / share) & (int(1 / share) - 1)) == 0] += 1
        for n in range(4, 21):
            holds[R.analyze(*G.path("longer", n, rules3, laws3, v))["recurring, persistent"] is True] += 1
    out = {"longer families": len(fams),
           "paths at 4 to 12 rings where every contact has Lemma 1's two partners (yes, no)": [lemma[True], lemma[False]],
           "paths at 4 to 12 rings where every contact keeps a fixed witness cell on both rings (yes, no)": [witness[True], witness[False]],
           "the last contact's composing share at 4 to 12 rings (share: paths)": dict(sorted(shares.items())),
           "shares that are a power of two (yes, no)": [power2[True], power2[False]],
           "recurring with every contact persistent at 4 to 20 rings (yes, no)": [holds[True], holds[False]],
           "rules (first, middle, last: families)": [[list(k), v] for k, v in Counter(tuple(p[1]) for p in fams).most_common()],
           "seconds": round(time.time() - t0, 1)}
    (HERE / "rule90_scope.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1)[:3000])


if __name__ == "__main__":
    main()
