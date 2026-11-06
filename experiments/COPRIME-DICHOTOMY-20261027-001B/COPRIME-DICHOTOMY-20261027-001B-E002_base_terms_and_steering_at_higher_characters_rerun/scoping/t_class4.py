import sys, glob, os, time
import numpy as np
S = "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/6694d27d-4771-575f-adbb-a5c8aaccce97/scratchpad"
ROOT = "/home/jscul/p-vs-np-contact-first"
sys.path.insert(0, S + "/cdB")
sys.path.insert(1, glob.glob(ROOT + "/proofs/COPRIME-DICHOTOMY-20261027-001A/*P001_*")[0])
sys.path.insert(2, glob.glob(ROOT + "/experiments/TRIPLE-SYSTEM-20261027-001B/*E001_*")[0])
sys.path.insert(3, glob.glob(ROOT + "/proofs/COPRIME-CLASS2-20261026-001B/*P001_*")[0])
import gd
from cd_lib import BraidAlg, CyclicBraidModel, root_of_unity, pair_failures, triple_failures
rng = np.random.default_rng(3)
for (p, d, e, summ, graph) in [(7, 3, 1, gd.AMPH["6_3"], (2, [(0, 1)])), (13, 4, 1, gd.torus_cable(13, 2), (2, [(0, 1)])),
                                (7, 6, 1, gd.torus_cable(7, 3), (2, [(0, 1)]))]:
    t0 = time.time()
    zeta = root_of_unity(p, d)
    L = gd.layer4_algebra(p, d, e); A = BraidAlg(L, zeta)
    odd = [k for k in range(L.D) if L.chars[k] % d]
    print("algebra dim", L.D, "names", [L.names[k] + f"(l{L.layer[k]},c{L.chars[k]})" for k in odd], "pairs", pair_failures(L), "triples", triple_failures(L))
    nv, edges = graph
    word, n, events, vstr, pb = gd.build_gadget(nv, edges, d, summ, summ)
    Mo = CyclicBraidModel(word, n, A, p)
    bs = 8
    def rc(c): return (rng.integers(0, p, (bs, len(Mo.cocycles[c]))) @ Mo.cocycles[c]) % p
    inputs = {k: rc(int(L.chars[k])) for k in odd if L.layer[k] <= 3}
    res = []
    for lay in (3, 4):
        for comp in [k for k in odd if L.layer[k] == lay]:
            s = rc((-int(L.chars[comp])) % d)
            Qm, ok, _, _ = gd.measure_Q(Mo, inputs, lay, comp, s)
            data = {k: v for k, v in inputs.items() if L.layer[k] <= 2}
            Qp = gd.predict_Q(L, A, word, n, events, data, s, comp, p)
            res.append((lay, L.names[comp], bool((Qm == Qp).all()), int((Qm != 0).sum()), bool(ok.all())))
    print(p, d, e, res, round(time.time() - t0, 1), "s", flush=True)
