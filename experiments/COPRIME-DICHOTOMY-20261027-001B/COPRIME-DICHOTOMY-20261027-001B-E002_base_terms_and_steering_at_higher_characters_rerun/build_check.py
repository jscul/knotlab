"""Construction check for run.py (no measurement): build every R3 single-insertion braid, every R4 gadget and the control
braids, and instantiate the braid models (linear parts only). Added after E001 crashed on a construction error."""
import glob, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(1, glob.glob(os.path.join(ROOT, "proofs/COPRIME-DICHOTOMY-20261027-001A/*P001_*"))[0])
sys.path.insert(2, glob.glob(os.path.join(ROOT, "experiments/TRIPLE-SYSTEM-20261027-001B/*E001_*"))[0])
sys.path.insert(3, glob.glob(os.path.join(ROOT, "proofs/COPRIME-CLASS2-20261026-001B/*P001_*"))[0])
import gd, mlib
import cp_lib as C
from cd_lib import BraidAlg, CyclicBraidModel, root_of_unity
src = open(os.path.join(HERE, "run.py")).read()
steer_cases = eval(re.search(r"steer_cases = (\[.*?\])\n", src, re.S).group(1), {"gd": gd})
gadget_cases = eval(re.search(r"gadget_cases = (\[.*?\])\n", src, re.S).group(1), {"gd": gd})
n_built = 0
for (p, d, e, summ, nc) in steer_cases + [(7, 6, 1, gd.torus_cable(7, 3), 6), (13, 3, 1, gd.AMPH["8_17"], 6), (7, 3, 1, gd.CHIRAL["6_1"], 6)]:
    base, n = C.connected_sum([summ] * nc)
    for off in (0, 1):
        assert n >= off + 4 * d, (p, d, n)
        w2 = base + C.cable(mlib.P4, d, offset=off)
        assert max(abs(g) for g in w2) <= n - 1
        A = BraidAlg(gd.four_way(p, d, e), root_of_unity(p, d))
        CyclicBraidModel(w2, n, A, p); n_built += 1
for (p, d, e, summ, gname, (nv, edges)) in gadget_cases:
    word, n, events, vstr, pb = gd.build_gadget(nv, edges, d, summ, summ)
    assert max(abs(g) for g in word) <= n - 1
    CyclicBraidModel(word, n, BraidAlg(gd.four_way(p, d, e), root_of_unity(p, d)), p); n_built += 1
print("construction check ok:", n_built, "braid models built")
