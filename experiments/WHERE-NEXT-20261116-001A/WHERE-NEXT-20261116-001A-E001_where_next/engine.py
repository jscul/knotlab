"""Instances, the C local-search engine and exact search for WHERE-NEXT-20261116-001A.

A knot pattern here is n distinctions and m three-place not-all-equal knots (the knot law; each knot
allows every joint state of its three distinctions except 000 and 111). Instances are planted: a hidden
state is drawn first and only knots it satisfies are kept, so every instance allows a state.

Families:
  rand   each knot binds three distinct distinctions drawn uniformly (the literature's planted random
         3-uniform hypergraph 2-colouring, or planted NAE-3-SAT without signs);
  local  distinctions in a fixed cyclic order; each knot binds a uniformly drawn distinction and two more
         within w places of it in that order (a local meeting pattern).
"""
from __future__ import annotations

import ctypes
import hashlib
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SRC = HERE / "nae_engine.c"

ALGOS = {"rw": 0, "walksat": 1, "probsat_poly": 2, "probsat_exp": 3, "novelty_plus": 4,
         "greedy_where": 5, "policy": 6, "sticky": 7, "fms": 8}
LEARN_WHERE, MEM_AGE, MEM_RNN, WHAT_PROBSAT = 1, 2, 4, 8
LAYOUT_NAMES = ["W_W1", "W_B1", "W_W2", "K_W1", "K_B1", "K_W2", "R_WH", "R_WS", "R_B", "NTHETA",
                "HID", "HR", "DW", "DK", "DS"]


def _build() -> Path:
    digest = hashlib.sha256(SRC.read_bytes()).hexdigest()[:16]
    cache = Path(os.environ.get("WHERE_NEXT_BUILD", Path(tempfile.gettempdir()) / "where_next_build"))
    cache.mkdir(parents=True, exist_ok=True)
    lib = cache / f"nae_engine_{digest}.so"
    if not lib.exists():
        tmp = cache / f".{lib.name}.{os.getpid()}"
        subprocess.run(["gcc", "-O2", "-fPIC", "-shared", "-o", str(tmp), str(SRC), "-lm"], check=True)
        os.replace(tmp, lib)
    return lib


_LIB = None


def lib():
    global _LIB
    if _LIB is None:
        L = ctypes.CDLL(str(_build()))
        i32p = np.ctypeslib.ndpointer(dtype=np.int32, flags="C_CONTIGUOUS")
        f64p = np.ctypeslib.ndpointer(dtype=np.float64, flags="C_CONTIGUOUS")
        L.nae_run.argtypes = [ctypes.c_int, ctypes.c_int, i32p, i32p, i32p, ctypes.c_int, f64p, f64p,
                              ctypes.c_int, ctypes.c_uint64, ctypes.c_int64, f64p, ctypes.c_void_p]
        L.nae_run.restype = ctypes.c_int
        L.nae_ntheta.restype = ctypes.c_int
        L.nae_layout.argtypes = [ctypes.POINTER(ctypes.c_int)]
        L.nae_selftest.argtypes = [ctypes.c_int, ctypes.c_int, i32p, i32p, i32p, ctypes.c_uint64, ctypes.c_int64]
        L.nae_selftest.restype = ctypes.c_int
        _LIB = L
    return _LIB


def ntheta() -> int:
    return lib().nae_ntheta()


def layout() -> dict:
    buf = (ctypes.c_int * len(LAYOUT_NAMES))()
    lib().nae_layout(buf)
    return dict(zip(LAYOUT_NAMES, list(buf)))


class Instance:
    def __init__(self, n: int, knots: np.ndarray, hidden: np.ndarray | None = None, name: str = ""):
        self.n = int(n)
        self.knots = np.ascontiguousarray(knots, dtype=np.int32)
        self.m = len(self.knots)
        self.hidden = hidden
        self.name = name
        flat = self.knots.reshape(-1)
        order = np.argsort(flat, kind="stable")
        self.occ = np.ascontiguousarray(order // 3, dtype=np.int32)
        counts = np.bincount(flat, minlength=self.n)
        self.os = np.zeros(self.n + 1, dtype=np.int32)
        np.cumsum(counts, out=self.os[1:])
        self.kv = np.ascontiguousarray(flat, dtype=np.int32)

    def satisfied(self, x: np.ndarray) -> bool:
        s = x[self.knots].sum(axis=1)
        return bool(np.all((s == 1) | (s == 2)))

    def cnf(self, break_symmetry: bool = True):
        a = self.knots + 1
        clauses = [list(map(int, r)) for r in a] + [list(map(int, -r)) for r in a]
        if break_symmetry:
            clauses.append([1])
        return clauses


def planted(family: str, n: int, alpha: float, seed: int, w: int = 10) -> Instance:
    """Planted instance; the generator stream depends only on (family, n, alpha, w, seed)."""
    tag = f"{family}|{n}|{alpha:.6f}|{w}|{seed}".encode()
    rng = np.random.default_rng(int.from_bytes(hashlib.sha256(tag).digest()[:8], "little"))
    m = int(round(alpha * n))
    hidden = rng.integers(0, 2, n, dtype=np.int8)
    while hidden.min() == hidden.max():  # a constant hidden state satisfies no knot (only at tiny n)
        hidden = rng.integers(0, 2, n, dtype=np.int8)
    out = []
    need = m
    tries = 0
    while need > 0:
        tries += 1
        if tries > 10_000:
            raise RuntimeError(f"no knot fits the hidden state: {tag!r}")
        batch = max(64, int(need * 1.6))
        if family == "rand":
            t = rng.integers(0, n, (batch, 3))
        elif family == "local":
            c = rng.integers(0, n, batch)
            off = rng.integers(-w, w + 1, (batch, 2))
            t = np.stack([c, (c + off[:, 0]) % n, (c + off[:, 1]) % n], axis=1)
        else:
            raise ValueError(family)
        ok = (t[:, 0] != t[:, 1]) & (t[:, 0] != t[:, 2]) & (t[:, 1] != t[:, 2])
        s = hidden[t].sum(axis=1)
        ok &= (s == 1) | (s == 2)
        t = t[ok][:need]
        out.append(t)
        need -= len(t)
    knots = np.concatenate(out).astype(np.int32)
    return Instance(n, knots, hidden, name=tag.decode())


def run(inst: Instance, algo: str, params=(), theta=None, flags: int = 0, seed: int = 0,
        max_flips: int = 10**6, want_state: bool = False) -> dict:
    p = np.zeros(4, dtype=np.float64)
    p[: len(params)] = params
    th = np.zeros(ntheta(), dtype=np.float64) if theta is None else np.ascontiguousarray(theta, dtype=np.float64)
    assert th.shape == (ntheta(),)
    out = np.zeros(10, dtype=np.float64)
    xs = np.zeros(inst.n, dtype=np.uint8) if want_state else None
    lib().nae_run(inst.n, inst.m, inst.kv, inst.os, inst.occ, ALGOS[algo], p, th, int(flags),
                  ctypes.c_uint64(seed & (2**64 - 1)), int(max_flips), out,
                  xs.ctypes.data if xs is not None else None)
    r = {"flips": int(out[0]), "solved": bool(out[1]), "minviol": int(out[2]), "work": int(out[3]),
         "cpu": float(out[4]), "new_chosen": int(out[5]), "new_avail": int(out[6]),
         "distinct_sum": int(out[7]), "where_steps": int(out[8]), "accepted": int(out[9])}
    if want_state:
        r["state"] = xs
    return r


def selftest(inst: Instance, seed: int, nflips: int) -> int:
    return lib().nae_selftest(inst.n, inst.m, inst.kv, inst.os, inst.occ, ctypes.c_uint64(seed), int(nflips))


def cadical(inst: Instance, time_limit: float = 60.0, solver_name: str = "cadical195") -> dict:
    """Exact search (CDCL) on the CNF encoding: two clauses per knot, plus one unit fixing the complement."""
    import threading
    import time

    from pysat.solvers import Solver

    t0 = time.process_time()
    w0 = time.perf_counter()
    with Solver(name=solver_name, bootstrap_with=inst.cnf()) as s:
        timer = threading.Timer(time_limit, s.interrupt)
        timer.start()
        res = s.solve_limited(expect_interrupt=True)
        timer.cancel()
        stats = s.accum_stats() or {}
        model = s.get_model() if res else None
    cpu = time.process_time() - t0
    wall = time.perf_counter() - w0
    ok = None
    if model is not None:
        x = np.zeros(inst.n, dtype=np.int8)
        for lit in model:
            if abs(lit) <= inst.n:
                x[abs(lit) - 1] = 1 if lit > 0 else 0
        ok = inst.satisfied(x)
    return {"result": res, "cpu": cpu, "wall": wall, "conflicts": int(stats.get("conflicts", -1)),
            "decisions": int(stats.get("decisions", -1)), "model_ok": ok}


if __name__ == "__main__":
    inst = planted("rand", 100, 2.0, 0)
    print(inst.n, inst.m, ntheta(), layout())
    for a, prm in [("rw", ()), ("walksat", (0.3,)), ("probsat_poly", (2.5, 1.0)), ("novelty_plus", (0.4, 0.01)),
                   ("greedy_where", (2.5, 1.0, 0.2)), ("sticky", (2.3, 1.0, 0.5)), ("fms", (0.3,)), ("policy", ())]:
        r = run(inst, a, prm, seed=1, max_flips=10**6, want_state=True)
        print(a, {k: v for k, v in r.items() if k != "state"}, inst.satisfied(r["state"].astype(np.int8)))
    print(cadical(inst, 10))
    sys.exit(0)
