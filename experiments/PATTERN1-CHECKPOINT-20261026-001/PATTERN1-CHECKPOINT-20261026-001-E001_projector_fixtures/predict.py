"""Kernel counts N = #{(c1, c2, c3) : T(c1, c2, .) = 0, T(c1, ., c3) = 0, T(., c2, c3) = 0} for gadget tensors on
V_zeta x V_zeta^2 x V_zeta^3 over F_7 (the free class-2 group on three generators, characters zeta, zeta^2, zeta^3)."""
import itertools
import numpy as np
P = 7

def count(T):
    d1, d2, d3 = T.shape
    n = 0
    V1 = list(itertools.product(range(P), repeat=d1)); V2 = list(itertools.product(range(P), repeat=d2)); V3 = list(itertools.product(range(P), repeat=d3))
    for c1 in V1:
        A = np.tensordot(np.array(c1), T, axes=(0, 0)) % P            # d2 x d3
        for c2 in V2:
            if np.any((np.array(c2) @ A) % P):
                continue
            for c3 in V3:
                if np.any((A @ np.array(c3)) % P):
                    continue
                if np.any((np.tensordot(T, np.array(c2), axes=(1, 0)) @ np.array(c3)) % P):
                    continue
                n += 1
    return n

def gadget(n, edges, gains):
    """T = sum_e (x_u - g_e x_v) (x) y_e (x) t_e"""
    m = len(edges)
    T = np.zeros((n, m, m), dtype=np.int64)
    for e, ((u, v), g) in enumerate(zip(edges, gains)):
        T[u, e, e] += 1
        T[v, e, e] -= g
    return T % P

if __name__ == "__main__":
    print("K2", count(gadget(2, [(0, 1)], [1])))
    print("digon balanced", count(gadget(2, [(0, 1), (0, 1)], [1, 1])))
    for g in (3, 5, 2, 4, 6):
        print("digon, second edge gain", g, count(gadget(2, [(0, 1), (0, 1)], [1, g])))
    print("no moves K2", count(np.zeros((2, 1, 1), dtype=np.int64)), "digon", count(np.zeros((2, 2, 2), dtype=np.int64)))
