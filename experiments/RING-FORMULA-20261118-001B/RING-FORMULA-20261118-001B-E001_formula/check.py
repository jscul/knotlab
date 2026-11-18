"""RING-FORMULA-20261118-001B checks.  python3 -B check.py <out json>
For each ring (odd length 5, 7, 9; knots of 4 to 6 places), compare the grown per-round counts (to 13 rounds or 8,000 junctions)
with the model's; on the model alone (to 80 rounds) test the recurrence c(t) = sum_i C(j, i) c(t - n - i) and the rate."""
import json
import sys
from math import comb
from multiprocessing import Pool
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from formula import model_counts, predicted_rate  # noqa: E402
from ring import ring, grow  # noqa: E402

RINGS = [[4, 4, 4, 4, 5], [4, 4, 4, 5, 5], [4, 4, 5, 4, 5], [4, 4, 5, 5, 5], [4, 5, 5, 5, 5], [5, 5, 5, 5, 5], [4, 4, 4, 4, 6],
         [4, 4, 4, 5, 6], [4, 4, 4, 4, 4, 4, 5], [4, 4, 4, 4, 4, 5, 5], [4, 4, 4, 4, 5, 4, 5], [4, 4, 4, 5, 4, 4, 5],
         [4, 4, 5, 5, 5, 4, 4], [5, 5, 5, 5, 5, 5, 5], [4, 4, 4, 4, 4, 4, 4, 4, 5], [4, 4, 4, 4, 5, 4, 4, 4, 5], [6, 4, 4, 4, 4, 4, 4]]


def one(sz):
    P = grow(ring(sz), 13, maxj=8000)
    c = P.counts_by_round()
    m = model_counts(sz, len(c) - 1)
    n, j = len(sz), sum(s - 4 for s in sz)
    M = model_counts(sz, 80)
    rec = [t for t in range(n + j, 81) if M[t] != sum(comb(j, i) * M[t - n - i] for i in range(j + 1))]
    first = max(rec) + 1 if rec else n + j
    ratio = M[80] / M[79]
    return {'ring': sz, 'n': n, 'j': j, 'grown_rounds': P.rounds, 'grown': c, 'model_equal': c == m,
            'recurrence_from_round': first, 'ratio_80': ratio, 'predicted_rate': predicted_rate(n, j)}


if __name__ == '__main__':
    with Pool(9) as pool:
        out = pool.map(one, RINGS)
    for r in out:
        print(r['ring'], r['model_equal'], r['grown_rounds'], 'rec from', r['recurrence_from_round'], round(r['ratio_80'], 5), round(r['predicted_rate'], 5), flush=True)
    Path(sys.argv[1]).write_text(json.dumps(out, indent=1))
