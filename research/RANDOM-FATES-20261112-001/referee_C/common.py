"""Referee helpers: import the frozen code read-only (run python with -B so nothing is written there)."""
import sys, os, itertools, random
ROOT = "/home/jscul/p-vs-np-contact-first"
EXP = os.path.join(ROOT, "experiments/RANDOM-FATES-20261112-001C/RANDOM-FATES-20261112-001C-E001_newest_four_count")
FATES = os.path.join(ROOT, "experiments/RANDOM-FATES-20261112-001A/RANDOM-FATES-20261112-001A-E001_fates_census")
sys.dont_write_bytecode = True
sys.path.insert(0, EXP); sys.path.insert(0, FATES)
import bonddp as B
import fates as F
import importlib.util as _iu
_spec = _iu.spec_from_file_location('census_C', os.path.join(EXP, 'census.py'))
C = _iu.module_from_spec(_spec); _spec.loader.exec_module(C)
import numpy as np

def brute_all_pairs(n, knots):
    """Independent: allowed states by enumeration, extendability of every partial assignment ({0,1,*}^n) by a
    star-filling transform, freeness of every subset, bonds, and least bond for every pair. No complement trick."""
    st = np.arange(1 << n, dtype=np.int64)
    ok = np.ones(1 << n, bool)
    for t in knots:
        s = sum((st >> v) & 1 for v in t)
        ok &= (s != 0) & (s != 3)
    # ext over {0,1,2}^n with axis v <-> variable v; build from full assignments
    arr = np.zeros((3,) * n, bool)
    full = ok.reshape((2,) * n)  # index order: axis 0 = most significant bit = variable n-1
    # reorder so that axis k corresponds to variable k
    full = np.transpose(full, axes=list(range(n - 1, -1, -1)))
    arr[(slice(0, 2),) * n] = full
    for v in range(n):
        idx2 = [slice(None)] * n; idx2[v] = 2
        idx0 = [slice(None)] * n; idx0[v] = 0
        idx1 = [slice(None)] * n; idx1[v] = 1
        arr[tuple(idx2)] = arr[tuple(idx0)] | arr[tuple(idx1)]
    # free[S]: axis v -> size 2 (0: v not in S -> star; 1: v in S -> AND of both values)
    fr = arr
    for v in range(n):
        a2 = np.take(fr, 2, axis=v)
        a01 = np.take(fr, 0, axis=v) & np.take(fr, 1, axis=v)
        fr = np.stack([a2, a01], axis=v)
    # fr[b0, b1, ..., b_{n-1}] with b_v = 1 iff v in S
    free = {}
    flat = fr.reshape(-1)  # C order: axis 0 most significant
    masks = np.arange(1 << n)
    # convert flat index (axis0 MSB) to subset mask with bit v for variable v
    def to_mask(k):
        m = 0
        for v in range(n):
            if (k >> (n - 1 - v)) & 1:
                m |= 1 << v
        return m
    freearr = np.zeros(1 << n, bool)
    for k in range(1 << n):
        freearr[to_mask(k)] = flat[k]
    bonds = []
    for m in range(1 << n):
        if freearr[m]:
            continue
        if all(freearr[m & ~(1 << v)] for v in range(n) if m >> v & 1):
            bonds.append(m)
    L = {}
    for i in range(n):
        for j in range(i + 1, n):
            pm = (1 << i) | (1 << j)
            sizes = [bin(m).count("1") for m in bonds if m & pm == pm]
            L[(i, j)] = min(sizes) if sizes else None
    return L, bonds, ok.any()
