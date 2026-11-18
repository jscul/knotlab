"""RING-GROWTH-20261118-001B: the ring of four four-place knots and one five-place knot against the (v, S) model.
Run with the workspace .venv (networkx):  .venv/bin/python -B check.py  -> writes results.json beside the artifacts."""
import json
import subprocess
import sys
from math import comb
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from ring import ring, grow  # noqa: E402
from bm import berlekamp_massey  # noqa: E402

out = {}
P = grow(ring([4, 4, 4, 4, 5]), 40)
c = P.counts_by_round()
out['counts'] = c


def m(a, b, n=5):
    return max(a // n + b // n + 1, 0)


model = [sum(comb(m(a, h - a), t - h) for h in range(t + 1) for a in range(5)) for t in range(len(c))]
out['model_counts_equal'] = model == c
L, C = berlekamp_massey(c)
out['berlekamp_massey'] = {'order': L, 'coefficients': [str(x) for x in C]}
out['recurrence_holds'] = all(c[t] == c[t - 5] + c[t - 6] for t in range(6, len(c)))
iso = {}
for T in (8, 12, 16, 20):
    r = subprocess.run([sys.executable, '-B', str(HERE / 'iso.py'), str(T)], capture_output=True, text=True, cwd=HERE)
    iso[T] = r.stdout.strip().splitlines()[-1]
out['isomorphism'] = iso
a = subprocess.run([sys.executable, '-B', str(HERE / 'model.py')], capture_output=True, text=True, cwd=HERE).stdout
b = subprocess.run([sys.executable, '-B', str(HERE / 'simhist.py')], capture_output=True, text=True, cwd=HERE).stdout
out['histograms_equal_rounds_1_to_22'] = a.replace(' ', '') == b.replace(' ', '')
dest = HERE.parents[2] / 'artifacts/RING-GROWTH-20261118-001B/RING-GROWTH-20261118-001B-E001_rings/results.json'
dest.write_text(json.dumps(out, indent=1))
print(json.dumps({k: v for k, v in out.items() if k != 'counts'}, indent=1))
