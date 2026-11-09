#!/usr/bin/env python3
"""Independent checks for GROW-ALL-20261109-001's run: (1) choose_lib's row insertions against GROW-RUN-20261109-001A's growrun_lib, which
check 5 there validated by actual bits; (2) the doubling while running (a band at every cut, fresh split, at lags 0, 1 and 2 on the 3 x 3
tube at g = 2) against actual bits from a separate re-implementation of the carry-over (old own cells keep their values, every contact
and every new ring cell is born), flipping one first-row cell at a time. Writes validate.json beside this file.

    PYTHONHASHSEED=0 .venv/bin/python3 -B validate.py      (the random bits come from hash(), fixed by the seed)"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments/GROW-CHOOSE-20261109-001A/GROW-CHOOSE-20261109-001A-E001_dynamics_chosen_growth"))
sys.path.insert(0, str(ROOT / "proofs/GROW-RUN-20261109-001A/GROW-RUN-20261109-001A-P001_a_band_inserted_while_running_keeps_only_the_knots_it_has_not_reached"))
import choose_lib as C  # noqa: E402
import growrun_lib as GR  # noqa: E402


def deps(run, keys_of):
    return {run.tube.keys[i]: frozenset(keys_of[v] for v in range(run.nvar) if run.state[i] >> v & 1) for i in range(len(run.state))}


def rows_vs_growrun():
    bad = 0
    for split in ("lower", "upper", "fresh", "copy"):
        a, b = C.Run2(C.Tube2([0, 1, 2], [0, 1, 2], 2)), GR.Run(GR.Tube(3, [0, 1, 2], 2))
        for _ in range(5):
            a.step()
            b.step()
        a.insert('row', 0, 0.5, split)
        b.insert_band(0, 0.5, split)
        for _ in range(20):
            a.step()
            b.step()
            bad += deps(a, a.vkey) != deps(b, b.vkey)
    return bad


def double(run, t):
    cuts = [('row', x) for x in run.tube.rows] + [('col', x) for x in run.tube.cols]
    for k, (kind, x) in enumerate(cuts):
        run.insert(kind, x, ('b', t, k), 'fresh')


H, INS = 14, (0, 1, 2)


def brute(flipkey):
    shape = C.Run2(C.Tube2([0, 1, 2], [0, 1, 2], 2))
    bits = {k: hash(('first', k, 5)) & 1 for k in shape.tube.keys}
    if flipkey is not None:
        bits[flipkey] ^= 1
    out = {}
    for t in range(H):
        if t in INS:
            double(shape, t)
            bits = {k: (bits[k] if (k in bits and k[0] == 'o') else hash(('born', t, k, 5)) & 1) for k in shape.tube.keys}
        vec = [bits[k] for k in shape.tube.keys]
        nxt = []
        for row in shape.tube.M:
            v, x = 0, row
            while x:
                low = x & -x
                v ^= vec[low.bit_length() - 1]
                x ^= low
            nxt.append(v)
        bits = {k: nxt[i] for i, k in enumerate(shape.tube.keys)}
        out[t + 1] = bits
    return out


def doubling_vs_bits():
    ref = C.Run2(C.Tube2([0, 1, 2], [0, 1, 2], 2))
    first = list(ref.vkey)
    hist = {}
    for t in range(H):
        if t in INS:
            double(ref, t)
        ref.step()
        hist[t + 1] = (list(ref.state), list(ref.tube.keys))
    base = brute(None)
    bad = read = 0
    for x in first[::7]:
        o = brute(x)
        v = first.index(x)
        for t in range(1, H + 1):
            st, keys = hist[t]
            dep = {keys[i] for i in range(len(keys)) if st[i] >> v & 1}
            diff = {k for k in base[t] if base[t][k] != o[t][k]}
            read += 1
            bad += dep != diff
    return read, bad


out = {"row insertions vs growrun_lib, mismatching lags": rows_vs_growrun()}
read, bad = doubling_vs_bits()
out["doubling vs actual bits"] = {"flips read": read, "mismatches": bad}
out["pass"] = out["row insertions vs growrun_lib, mismatching lags"] == 0 and bad == 0
(HERE / "validate.json").write_text(json.dumps(out, indent=1) + "\n")
print(out)
