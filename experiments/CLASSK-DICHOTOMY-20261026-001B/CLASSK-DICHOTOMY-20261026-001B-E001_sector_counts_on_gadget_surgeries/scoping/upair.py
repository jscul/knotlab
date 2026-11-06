"""scoping: is u u v nonzero in H^2(X; F_tau) for twist-knot exteriors X and v in V_tau?"""
import sys, glob
sys.path.insert(0, glob.glob("/home/jscul/p-vs-np-contact-first/proofs/COPRIME-CLASS2-20261026-001B/COPRIME-CLASS2-20261026-001B-P001_*")[0])
import cp_lib as C
KN = {"3_1": ([1, 1, 1], 2), "4_1": ([1, -2, 1, -2], 3), "5_2": ([1, 1, 1, 2, -1, 2], 3), "6_1": ([1, 1, 2, -1, -3, 2, -3], 4)}
for (p, r, z) in [(7, 6, 3), (5, 4, 2), (13, 12, 2)]:
    for kn, (w, n) in KN.items():
        U, rels, _ = C.presentation(w, n, r)
        rels = rels[:-1]                       # knot group
        for e in range(1, r):
            tau = pow(z, e, p)
            H, _, _ = C.cohomology(U, rels, tau, 1, p)
            if not H:
                continue
            Hu, _, _ = C.cohomology(U, rels, 1, 1, p)     # trivial character: u
            assert len(Hu) == 1
            G = C.Group(p, r, 1, tau)
            Dz = C.fox_rows(U, rels, tau, 1, p)
            cols = [[Dz[i][g] for i in range(len(rels))] for g in range(U)]
            red = C.Reducer(cols, p, len(rels))
            for v in H:
                imgs = [(Hu[0][g], v[g], 0, 1) for g in range(U)]
                vec = []
                for rel in rels:
                    X, Y, Zc, ee = G.word(rel, imgs)
                    assert X == 0 and Y == 0 and ee == 0
                    vec.append(Zc)
                cl = red.reduce(vec)
                print(p, r, kn, "tau =", tau, "dim V =", len(H), "u u v nonzero:", any(cl))
