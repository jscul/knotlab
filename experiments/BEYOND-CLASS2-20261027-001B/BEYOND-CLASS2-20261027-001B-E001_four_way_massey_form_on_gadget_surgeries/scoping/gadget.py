"""four-way gadget: base = closure of s1^p s2^p ... sN^p (N = n + 6m summands T(2,p), strands 0..N); vertex v <-> strand v (1..n);
edge e = (u, v), u < v: private strands b+1..b+6, b = n + 6e; insertion gamma . cable(P4, 2, offset b-1) . gamma^-1 at the top,
gamma drags strand v then strand u over to positions b, b-1."""
import sys, os
import numpy as np
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/6694d27d-4771-575f-adbb-a5c8aaccce97/scratchpad/bc")
from bm import BraidModel
import mlib
d = "/home/jscul/p-vs-np-contact-first/proofs/COPRIME-CLASS2-20261026-001B/"; sys.path.insert(0, d + os.listdir(d)[0])
import cp_lib as C

def gadget_word(n, edges, p):
    m = len(edges)
    N = n + 6 * m
    word, mids = [], []
    for e, (u, v) in enumerate(edges):
        u, v = min(u, v), max(u, v)
        b = n + 6 * e
        gam = list(range(v + 1, b + 1)) + list(range(u + 1, b))
        mids.append((len(word) + len(gam), b - 1))
        word += gam + C.cable(mlib.P4, 2, offset=b - 1) + [-g for g in reversed(gam)]
    base = sum(([k] * p for k in range(1, N + 1)), [])
    return word + base, N + 1, mids, N

def transport(sv, word, upto, p):
    sv = sv.copy()
    for g in word[:upto]:
        i = abs(g) - 1
        a, b = sv[:, i].copy(), sv[:, i + 1].copy()
        if g > 0: sv[:, i], sv[:, i + 1] = (2 * a - b) % p, a
        else: sv[:, i], sv[:, i + 1] = b, (2 * b - a) % p
    return sv

def milnor_tensor(p):
    st = mlib.artin_conj(mlib.P4, 4)
    return [{k: v for k, v in mlib.magnus(st[j][0], 3, p).items() if len(k) == 3} for j in range(4)]

def predicted_Q(cols, word, mids, p, M3, kappa=2, leaves_override=None):
    bs = cols["s"].shape[0]
    pred = np.zeros(bs, dtype=np.int64)
    for e, (lev, off) in enumerate(mids):
        T = {nm: transport(v, word, lev, p) for nm, v in cols.items()}
        ell = lambda nm, k: (T[nm][:, off + 2 * k + 1] - T[nm][:, off + 2 * k]) % p
        for j in range(4):
            Lam = np.zeros(bs, dtype=np.int64)
            for (i1, i2, i3), v in M3[j].items():
                Lam = (Lam + v * ell("y", i1) * ell("x", i2) * ell("w", i3)) % p
            pred = (pred + kappa * Lam * ell("s", j)) % p
    return pred

if __name__ == "__main__":
    p = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    rng = np.random.default_rng(7)
    M3 = milnor_tensor(p)
    graphs = {"K2": (2, [(1, 2)]), "P3": (3, [(1, 2), (2, 3)]), "digon": (2, [(1, 2), (1, 2)]),
              "K3": (3, [(1, 2), (2, 3), (1, 3)]), "star": (4, [(1, 2), (1, 3), (1, 4)])}
    for name, (n, edges) in graphs.items():
        word, nstr, mids, N = gadget_word(n, edges, p)
        Mo = BraidModel(word, nstr, p)
        bs = 48
        rc = lambda: (rng.integers(0, p, (bs, len(Mo.Fix))) @ Mo.Fix) % p
        cols = {"y": rc(), "x": rc(), "w": rc(), "s": rc()}
        o, _ = Mo.obstruction(cols["y"], cols["x"], cols["w"])
        Q = (o * Mo.y_of(cols["s"])).sum(axis=1) % p
        pred = predicted_Q(cols, word, mids, p, M3)
        # closed-form leaves: vertex leaf s_v - s_u, private leaves s_{b+2k} - s_{b+2k-1} at the top
        ok_leaves = True
        for e, (lev, off) in enumerate(mids):
            u, v = sorted(edges[e]); b = n + 6 * e
            T = transport(cols["s"], word, lev, p)
            top = cols["s"]
            ok_leaves &= ((T[:, off + 1] - T[:, off] - (top[:, v] - top[:, u])) % p == 0).all()
            for k in (1, 2, 3):
                ok_leaves &= ((T[:, off + 2 * k + 1] - T[:, off + 2 * k] - (top[:, b + 2 * k] - top[:, b + 2 * k - 1])) % p == 0).all()
        # control: drop the last edge's tensor
        pred_drop = predicted_Q(cols, word, mids[:-1], p, M3)
        print(f"p={p} {name}: crossings {len(word)}, strands {nstr}, dim V {len(Mo.Fix) - 1} (N={N}); "
              f"Q nonzero {int((Q != 0).sum())}/{bs}; Q == predicted: {bool((Q == pred).all())}; "
              f"closed-form leaves: {bool(ok_leaves)}; control (one edge dropped) equal: {bool((Q == pred_drop).all())}", flush=True)
