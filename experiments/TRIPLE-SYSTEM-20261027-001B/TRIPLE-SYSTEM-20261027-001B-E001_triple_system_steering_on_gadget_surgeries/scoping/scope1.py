"""scoping: steering in the general model for the four-way algebra (regression), free class 3 on two minus generators,
the cross-layer class-3 algebra (no obstruction expected), and the cross-layer class-4 algebra (one obstruction along c3)"""
import sys, os, itertools
import numpy as np
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/6694d27d-4771-575f-adbb-a5c8aaccce97/scratchpad/r2")
sys.path.insert(1, "/home/jscul/p-vs-np-contact-first/experiments/BEYOND-CLASS2-20261027-001B/BEYOND-CLASS2-20261027-001B-E001_four_way_massey_form_on_gadget_surgeries")
from lm import LieAlg, LieBraidModel, transport
import mlib
import fixtures as FX

def algebras(p):
    return {
     "four-way": LieAlg(p, "x y w z u t".split(), [1, 1, 1, 2, 2, 3], [-1, -1, -1, 1, 1, -1],
                        {("x", "y"): {"z": 1}, ("w", "x"): {"u": 1}, ("w", "z"): {"t": 1}, ("y", "u"): {"t": -1}}),
     "free3(-,-)": LieAlg(p, "y1 y2 z t1 t2".split(), [1, 1, 2, 3, 3], [-1, -1, 1, -1, -1],
                          {("y1", "y2"): {"z": 1}, ("z", "y1"): {"t1": 1}, ("z", "y2"): {"t2": 1}}),
     "cross3(+,-)": LieAlg(p, "x y z a b".split(), [1, 1, 2, 3, 3], [1, -1, -1, -1, 1],
                           {("x", "y"): {"z": 1}, ("x", "z"): {"a": 1}, ("y", "z"): {"b": 1}}),
     "cross4(+,-)": LieAlg(p, "x y z a b c1 c2 c3".split(), [1, 1, 2, 3, 3, 4, 4, 4], [1, -1, -1, -1, 1, -1, 1, -1],
                           {("x", "y"): {"z": 1}, ("x", "z"): {"a": 1}, ("y", "z"): {"b": 1}, ("x", "a"): {"c1": 1},
                            ("y", "a"): {"c2": 1}, ("x", "b"): {"c2": 1}, ("y", "b"): {"c3": 1}})}

SPEC = {"four-way": (["x", "y", "w"], ["t"]), "free3(-,-)": (["y1", "y2"], ["t1", "t2"]),
        "cross3(+,-)": (["y", "z", "a"], []), "cross4(+,-)": (["y", "z", "a", "c1"], ["c3"])}

def lie_W3(L, M, A):
    """(1/3) sum_w M(w) [A_w1, [A_w2, A_w3]] (Dynkin) for batched leaf vectors A[i] (batch, D)"""
    p = L.p; third = pow(3, p - 2, p)
    out = np.zeros_like(A[0])
    for (i1, i2, i3), v in M.items():
        out = (out + v * L.br(A[i1], L.br(A[i2], A[i3]))) % p
    return out * third % p

def predict(L, word, events, cols, inputs, measured, T):
    p = L.p
    bs = cols["s"][measured[0]].shape[0] if measured else 1
    pred = np.zeros(bs, dtype=np.int64)
    for lev, off, braid in events:
        mids = {k: transport(cols[k], word, lev, p) for k in inputs}
        smid = {b: transport(cols["s"][b], word, lev, p) for b in measured}
        A = []
        for leaf in range(4):
            vec = np.zeros((bs, L.D), dtype=np.int64)
            for k in inputs:
                ell = (mids[k][:, off + 2 * leaf + 1] - mids[k][:, off + 2 * leaf]) % p
                vec[:, L.idx[k]] = ell
            A.append(vec)
        for j in range(4):
            lam = lie_W3(L, T[braid][j], A)
            for b in measured:
                ellj = (smid[b][:, off + 2 * j + 1] - smid[b][:, off + 2 * j]) % p
                pred = (pred + 2 * lam[:, L.idx[b]] * ellj) % p
    return pred

if __name__ == "__main__":
    rng = np.random.default_rng(5)
    for p in (5, 7):
        T = FX.tensors(p)
        for name, L in algebras(p).items():
            ins, meas = SPEC[name]
            for fx_name, spec, inserts in [("4_1x4 P4 (0,0)", ("knot", "4_1", 4), [(0, "P4", 0, [])]),
                                           ("4_1x4 P4B (6,1)", ("knot", "4_1", 4), [(6, "P4B", 1, [])]),
                                           ("T(2,p)x8 P4 (0,1)+P4B(3p,0)", ("torus", 8), [(0, "P4", 1, []), (15, "P4B", 0, [])])]:
                if spec[0] == "knot" and p != 5: continue
                base, n = FX.base_word(spec, p)
                ins_ = [(lev if lev != 15 else 3 * p, b, o, g) for lev, b, o, g in inserts]
                word, events = FX.build(base, ins_)
                Mo = LieBraidModel(word, n, L)
                bs = 32
                rc = lambda: (rng.integers(0, p, (bs, len(Mo.Fix))) @ Mo.Fix) % p
                inputs = {k: rc() for k in ins}
                cols = dict(inputs); cols["s"] = {b: rc() for b in meas}
                try:
                    out = Mo.solve({L.idx[k]: v for k, v in inputs.items()}, [L.idx[b] for b in meas])
                except AssertionError as e:
                    print(f"p={p} {name} {fx_name}: solve failed: {e}", flush=True); continue
                if not meas:
                    print(f"p={p} {name} {fx_name}: no obstruction anywhere (all {bs} samples lift)", flush=True); continue
                Q = np.zeros(bs, dtype=np.int64)
                for b in meas:
                    Q = (Q + (out[L.idx[b]] * Mo.y_of(cols["s"][b])).sum(axis=1)) % p
                pred = predict(L, word, events, cols, ins, meas, T)
                ratios = {int(a * pow(int(c), p - 2, p) % p) for a, c in zip(Q, pred) if c}
                print(f"p={p} {name} {fx_name}: Q nonzero {int((Q != 0).sum())}/{bs}, Q == pred: {bool((Q == pred).all())}, "
                      f"ratios {ratios}, zero where pred zero: {all(a == 0 for a, c in zip(Q, pred) if c == 0)}", flush=True)
