"""Shared helpers for the referee R1 checks (copied from WHERE-NEXT-20261116-001's referee-R1 for
SCALE-MEMORY-20261116-001; run() gains a CPU-time guard and returns the time-out flag).

- builds and loads the referee's own C engine (referee_sls.c) into the session scratchpad;
- regenerates the study's planted instances with the study's `engine.planted` (data only) and checks
  each independently (three distinct in-range distinctions per knot, m = round(alpha n), the hidden
  state not constant and satisfying every knot);
- runs the referee engine and checks every reported solution against the knots;
- a fork-based pool (at most 8 workers) and the statistics used by the task scripts.
"""
from __future__ import annotations

import ctypes
import hashlib
import json
import math
import os
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EXP = ROOT / "experiments/WHERE-NEXT-20261116-001A/WHERE-NEXT-20261116-001A-E001_where_next"
ART = ROOT / "artifacts/WHERE-NEXT-20261116-001A/WHERE-NEXT-20261116-001A-E001_where_next"
SRC = HERE / "referee_sls.c"
BUILD = Path(os.environ.get("REFEREE_BUILD",
                            "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/"
                            "866db0bb-326b-5add-835e-78bf03179706/scratchpad/build"))

ALPHA = {"rand": 2.1, "local": 4.0}
CAP = {("rand", 200): 10**6, ("rand", 800): 10**7, ("rand", 3200): 2 * 10**8, ("rand", 12800): 2 * 10**9,
       ("local", 200): 10**6, ("local", 800): 2 * 10**7, ("local", 3200): 4 * 10**8}
TEST_SEED0 = {"rand": 3_000_000, "local": 3_500_000}
RETUNE_SEED0 = {"rand": 4_000_000, "local": 4_500_000}
ALGO = {"walksat": 0, "probsat": 1, "novelty_plus": 2, "adapt_novelty_plus": 3, "novelty_pp": 4}
NB_AGE, NB_DEC = 2048, 2200

sys.dont_write_bytecode = True
sys.path.insert(0, str(EXP))
import engine as _study_engine  # noqa: E402  (only `planted` is used: instance generation is data)

_LIB = None


def lib():
    global _LIB
    if _LIB is None:
        BUILD.mkdir(parents=True, exist_ok=True)
        dig = hashlib.sha256(SRC.read_bytes()).hexdigest()[:12]
        so = BUILD / f"referee_sls_{dig}.so"
        if not so.exists():
            tmp = BUILD / f".{so.name}.{os.getpid()}"
            subprocess.run(["gcc", "-O2", "-march=native", "-fPIC", "-shared", "-o", str(tmp), str(SRC), "-lm"],
                           check=True)
            os.replace(tmp, so)
        L = ctypes.CDLL(str(so))
        i32 = np.ctypeslib.ndpointer(dtype=np.int32, flags="C_CONTIGUOUS")
        f64 = np.ctypeslib.ndpointer(dtype=np.float64, flags="C_CONTIGUOUS")
        L.ref_run.argtypes = [ctypes.c_int, ctypes.c_int, i32, ctypes.c_int, f64, ctypes.c_uint64, ctypes.c_int64,
                              f64, ctypes.c_void_p, ctypes.c_void_p]
        L.ref_run.restype = ctypes.c_int
        L.ref_selftest.argtypes = [ctypes.c_int, ctypes.c_int, i32, ctypes.c_uint64, ctypes.c_int64]
        L.ref_selftest.restype = ctypes.c_int
        L.ref_hist_size.restype = ctypes.c_int
        _LIB = L
    return _LIB


def seed_of(*parts) -> int:
    return int.from_bytes(hashlib.sha256(("referee-R1|" + "|".join(map(str, parts))).encode()).digest()[:8], "little")


def check_instance(inst, fam: str, n: int) -> list[str]:
    """Independent check that the instance is planted as published."""
    errs = []
    K = np.asarray(inst.knots)
    m = int(round(ALPHA[fam] * n))
    if K.shape != (m, 3):
        errs.append(f"shape {K.shape} != ({m}, 3)")
    if K.min() < 0 or K.max() >= n:
        errs.append("index out of range")
    if np.any(K[:, 0] == K[:, 1]) or np.any(K[:, 0] == K[:, 2]) or np.any(K[:, 1] == K[:, 2]):
        errs.append("a knot with a repeated distinction")
    h = np.asarray(inst.hidden).astype(np.int64)
    if h.min() == h.max():
        errs.append("constant hidden state")
    s = h[K].sum(axis=1)
    if not np.all((s == 1) | (s == 2)):
        errs.append(f"hidden state violates {int(np.sum((s == 0) | (s == 3)))} knots")
    if fam == "local":
        # every knot: one centre and two more within 10 places of it in the cyclic order
        def cd(a, b):
            d = np.abs(a - b) % n
            return np.minimum(d, n - d)
        ok = np.zeros(len(K), dtype=bool)
        for c in range(3):
            o = [j for j in range(3) if j != c]
            ok |= (cd(K[:, c], K[:, o[0]]) <= 10) & (cd(K[:, c], K[:, o[1]]) <= 10)
        if not ok.all():
            errs.append("local knot wider than the window")
    return errs


_CACHE: dict = {}


def instance(fam: str, n: int, seed: int):
    key = (fam, n, seed)
    if key not in _CACHE:
        if len(_CACHE) > 8:
            _CACHE.clear()
        inst = _study_engine.planted(fam, n, ALPHA[fam], seed)
        errs = check_instance(inst, fam, n)
        if errs:
            raise RuntimeError(f"instance {key}: {errs}")
        _CACHE[key] = (inst, np.ascontiguousarray(inst.knots.reshape(-1), dtype=np.int32))
    return _CACHE[key]


def run(fam, n, iseed, algo, params, rseed, cap, hist=False, tlimit=0.0) -> dict:
    inst, kv = instance(fam, n, iseed)
    p = np.zeros(4, dtype=np.float64)
    p[: len(params)] = params
    assert len(params) <= 3
    p[3] = tlimit
    out = np.zeros(7, dtype=np.float64)
    x = np.zeros(inst.n, dtype=np.uint8)
    H = np.zeros(lib().ref_hist_size(), dtype=np.int64) if hist else None
    lib().ref_run(inst.n, inst.m, kv, ALGO[algo], p, ctypes.c_uint64(rseed & (2**64 - 1)), int(cap), out,
                  H.ctypes.data if H is not None else None, x.ctypes.data)
    solved = bool(out[1])
    if solved:
        s = x.astype(np.int64)[inst.knots].sum(axis=1)
        if not np.all((s == 1) | (s == 2)):
            raise RuntimeError(f"reported solution does not satisfy every knot: {fam} {n} {iseed} {algo}")
    r = {"flips": int(out[0]), "solved": solved, "minviol": int(out[2]), "cpu": float(out[3]),
         "final_noise": float(out[4]), "mean_noise": float(out[5]), "timed_out": bool(out[6])}
    if hist:
        r["hist"] = H
    return r


def pool_map(fn, jobs, procs=8):
    import multiprocessing as mp
    ctx = mp.get_context("fork")
    lib()
    with ctx.Pool(min(procs, 8)) as P:
        return list(P.imap_unordered(fn, jobs, chunksize=1))


def study_results(path: Path | None = None) -> dict:
    """{(fam, n, arm): {seed: (flips, solved)}} from the study's test results."""
    path = path or ART / "test/results.jsonl"
    d = defaultdict(dict)
    with open(path) as fh:
        for line in fh:
            r = json.loads(line)["result"]
            d[(r["fam"], r["n"], r["arm"])][r["seed"]] = (r["flips"], r["solved"], tuple(r["params"]))
    return d


def median_ratio_boot(a_by_inst: dict, b_by_inst: dict, B=10000, rng_seed=1, level=0.95):
    """Paired bootstrap over instances of median(a) / median(b). Values are lists of flips per instance
    (one or more runs)."""
    keys = sorted(set(a_by_inst) & set(b_by_inst))
    A = [np.asarray(a_by_inst[k], dtype=float) for k in keys]
    Bv = [np.asarray(b_by_inst[k], dtype=float) for k in keys]
    point = np.median(np.concatenate(A)) / np.median(np.concatenate(Bv))
    rng = np.random.default_rng(rng_seed)
    na, nb = len(A[0]), len(Bv[0])
    Aa = np.stack(A) if all(len(x) == na for x in A) else None
    Bb = np.stack(Bv) if all(len(x) == nb for x in Bv) else None
    rs = np.empty(B)
    for i in range(B):
        idx = rng.integers(0, len(keys), len(keys))
        rs[i] = np.median(Aa[idx]) / np.median(Bb[idx])
    lo, hi = np.quantile(rs, [(1 - level) / 2, 1 - (1 - level) / 2])
    return {"point": float(point), "lo": float(lo), "hi": float(hi), "level": level, "instances": len(keys)}


def mwu(a, b):
    from scipy.stats import mannwhitneyu
    r = mannwhitneyu(a, b, alternative="two-sided")
    return {"U": float(r.statistic), "p": float(r.pvalue)}


def jdump(obj, path: Path):
    def conv(o):
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, float) and (math.isinf(o) or math.isnan(o)):
            return str(o)
        raise TypeError(type(o))
    path.write_text(json.dumps(obj, indent=1, default=conv) + "\n")
