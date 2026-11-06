import sys, glob, os, time
import numpy as np
S = "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/6694d27d-4771-575f-adbb-a5c8aaccce97/scratchpad"
ROOT = "/home/jscul/p-vs-np-contact-first"
sys.path.insert(0, S + "/cdB")
sys.path.insert(1, glob.glob(ROOT + "/proofs/COPRIME-DICHOTOMY-20261027-001A/*P001_*")[0])
sys.path.insert(2, glob.glob(ROOT + "/experiments/TRIPLE-SYSTEM-20261027-001B/*E001_*")[0])
sys.path.insert(3, glob.glob(ROOT + "/proofs/COPRIME-CLASS2-20261026-001B/*P001_*")[0])
import gd
from cd_lib import BraidAlg, CyclicBraidModel, root_of_unity
rng = np.random.default_rng(2)
for (p, d, e, summ, graph) in [(7, 3, 1, gd.AMPH["6_3"], (2, [(0, 1)])), (7, 3, 2, gd.AMPH["6_3"], (3, [(0, 1), (1, 2)])),
                                (13, 4, 1, gd.torus_cable(13, 2), (2, [(0, 1)])), (7, 6, 1, gd.torus_cable(7, 3), (2, [(0, 1)]))]:
    t0 = time.time()
    zeta = root_of_unity(p, d)
    L = gd.four_way(p, d, e); A = BraidAlg(L, zeta)
    nv, edges = graph
    word, n, events, vstr, pb = gd.build_gadget(nv, edges, d, summ, summ)
    Mo = CyclicBraidModel(word, n, A, p)
    ix, iy, iw, it = (A.idx[s] for s in "xywt")
    bs = 8
    def rc(c): return (rng.integers(0, p, (bs, len(Mo.cocycles[c]))) @ Mo.cocycles[c]) % p
    inputs = {ix: rc(e % d), iy: rc((-e) % d), iw: rc((-e) % d)}
    s = rc(e % d)
    Qm, ok, _, _ = gd.measure_Q(Mo, inputs, 3, it, s)
    Qp = gd.predict_Q(L, A, word, n, events, inputs, s, it, p)
    print(p, d, e, "n", n, "len", len(word), "dimZ1", len(Mo.cocycles[e % d]), "match", bool((Qm == Qp).all()), "nonzero", int((Qm != 0).sum()),
          "lower ok", bool(ok.all()), round(time.time() - t0, 1), "s", flush=True)
