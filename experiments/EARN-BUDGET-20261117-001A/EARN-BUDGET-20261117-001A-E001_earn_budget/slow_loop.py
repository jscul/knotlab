"""Instances, the fast loop and the slow loop for SLOW-LOOP-20261117-001A, copied for EARN-BUDGET-20261117-001A.

EARN-BUDGET-20261117-001A adds the earned budget (policy key "earn") and the heavy-tailed family (MEET-TRANSFER-20261117-001A's
generator). Every other path is SLOW-LOOP's, unchanged (gate G9 checks it run for run).

A knot pattern here is n distinctions and m signed three-place not-all-equal knots: knot (a, b, c) with signs
(sa, sb, sc) allows every joint state except the two in which x_a ^ sa, x_b ^ sb and x_c ^ sc are all equal. The
test patterns are unsigned (every sign 0, the knot law of WHERE-NEXT-20261116-001A); signs appear only after the
slow loop merges tie classes or adds derived knots.

Families (the generator is MEET-TRANSFER-20261117-001A's, copied unchanged so that the streams agree):
  rand   each knot binds three distinct distinctions drawn uniformly (the literature's planted random 3-uniform
         hypergraph 2-colouring);
  block  distinctions in consecutive blocks of w; with probability 3/4 a knot binds three distinctions of one
         uniformly drawn block, otherwise three drawn from all;
  local  distinctions in a fixed cyclic order; each knot binds a uniformly drawn distinction and two more within w
         places of it in that order.
Every instance is planted: a hidden state is drawn first and only knots it allows are kept.

The two moves of the slow loop keep the allowed states:
  tie merge    a tie (x_p = x_q ^ parity in every allowed state, found by a refutation) merges p into q's tie class;
               the allowed states of the merged pattern are in one-to-one correspondence with the original's;
  shadow knot  a signed three-place knot that every allowed state satisfies (the pattern's shadow on three distinctions,
               found by a refutation; it passes K1-K3) is added; the allowed states are unchanged.
A state found on the mutated pattern is mapped back to the original distinctions and checked on every original knot.
"""
from __future__ import annotations

import ctypes
import hashlib
import math
import os
import subprocess
import tempfile
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SRC = HERE / "slow_engine.c"
ALGOS = {"probsat_poly": 2, "novelty_plus": 4}


def _build() -> Path:
    digest = hashlib.sha256(SRC.read_bytes()).hexdigest()[:16]
    cache = Path(os.environ.get("SLOW_LOOP_BUILD", Path(tempfile.gettempdir()) / "slow_loop_build"))
    cache.mkdir(parents=True, exist_ok=True)
    lib = cache / f"slow_engine_{digest}.so"
    if not lib.exists():
        tmp = cache / f".{lib.name}.{os.getpid()}"
        subprocess.run(["gcc", "-O2", "-fPIC", "-shared", "-o", str(tmp), str(SRC), "-lm"], check=True)
        os.replace(tmp, lib)
    return lib


_LIB = None
i32p = np.ctypeslib.ndpointer(dtype=np.int32, flags="C_CONTIGUOUS")
u8p = np.ctypeslib.ndpointer(dtype=np.uint8, flags="C_CONTIGUOUS")
i64p = np.ctypeslib.ndpointer(dtype=np.int64, flags="C_CONTIGUOUS")
u64p = np.ctypeslib.ndpointer(dtype=np.uint64, flags="C_CONTIGUOUS")
f64p = np.ctypeslib.ndpointer(dtype=np.float64, flags="C_CONTIGUOUS")


def lib():
    global _LIB
    if _LIB is None:
        L = ctypes.CDLL(str(_build()))
        L.fl_init_state.argtypes = [ctypes.c_int, ctypes.c_uint64, u8p, u64p]
        L.fl_new.argtypes = [ctypes.c_int, ctypes.c_int, i32p, u8p, u8p, i64p, u64p, ctypes.c_uint64, ctypes.c_int64,
                             ctypes.c_void_p, ctypes.POINTER(ctypes.c_int64)]
        L.fl_new.restype = ctypes.c_void_p
        L.fl_free.argtypes = [ctypes.c_void_p]
        L.fl_get.argtypes = [ctypes.c_void_p, u8p, i64p, u64p, ctypes.POINTER(ctypes.c_int64), i32p, u8p]
        L.fl_nviol.argtypes = [ctypes.c_void_p]
        L.fl_set_sortlog.argtypes = [ctypes.c_void_p, ctypes.c_int]
        L.fl_run.argtypes = [ctypes.c_void_p, ctypes.c_int, f64p, ctypes.c_int64, f64p]
        L.fl_run.restype = ctypes.c_int
        L.sl_probe.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int64, ctypes.c_int64, ctypes.c_double,
                               ctypes.c_int, ctypes.c_int, i32p, ctypes.c_int, i32p, ctypes.c_int, f64p]
        L.sl_probe.restype = ctypes.c_int
        L.sl_reduce.argtypes = [ctypes.c_int, ctypes.c_int, i32p, u8p, i32p, u8p, i32p, ctypes.c_int, i32p, i32p, u8p,
                                i32p, u8p, u8p, f64p]
        _LIB = L
    return _LIB


class Instance:
    def __init__(self, n: int, knots: np.ndarray, hidden: np.ndarray | None = None, name: str = ""):
        self.n = int(n)
        self.knots = np.ascontiguousarray(knots, dtype=np.int32)
        self.m = len(self.knots)
        self.hidden = hidden
        self.name = name

    def satisfied(self, x: np.ndarray) -> bool:
        s = x[self.knots].astype(np.int64).sum(axis=1)
        return bool(np.all((s == 1) | (s == 2)))

    def cnf(self, break_symmetry: bool = True):
        a = self.knots + 1
        clauses = [list(map(int, r)) for r in a] + [list(map(int, -r)) for r in a]
        if break_symmetry:
            clauses.append([1])
        return clauses


def planted(family: str, n: int, alpha: float, seed: int, w: int = 10) -> Instance:
    """MEET-TRANSFER-20261117-001A's generator, unchanged: the stream depends only on (family, n, alpha, w, seed)."""
    tag = f"{family}|{n}|{alpha:.6f}|{w}|{seed}".encode()
    rng = np.random.default_rng(int.from_bytes(hashlib.sha256(tag).digest()[:8], "little"))
    m = int(round(alpha * n))
    hidden = rng.integers(0, 2, n, dtype=np.int8)
    while hidden.min() == hidden.max():
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
        elif family == "heavy":
            # MEET-TRANSFER-20261117-001A's heavy-tailed degrees: distinction i drawn with weight (i + 10)^(-1/2)
            wts = (np.arange(n) + 10.0) ** -0.5
            t = rng.choice(n, size=(batch, 3), p=wts / wts.sum())
        elif family == "block":
            nb = n // w
            blk = rng.integers(0, nb, batch)
            inside = rng.random(batch) < 0.75
            t_in = blk[:, None] * w + rng.integers(0, w, (batch, 3))
            t_out = rng.integers(0, n, (batch, 3))
            t = np.where(inside[:, None], t_in, t_out)
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


def planted_embed(n: int, seed: int, frac: float = 0.25, alpha_r: float = 2.1, alpha_l: float = 4.0, alpha_c: float = 0.1,
                  w: int = 10) -> Instance:
    """SLOW-LOOP-20261117-001A's embedded pattern, two weakly coupled sub-patterns under one hidden state: a local
    sub-pattern (density alpha_l, window w, cyclic order) on the first frac * n distinctions, a uniform one (density
    alpha_r) on the others, and alpha_c * n coupling knots drawn uniformly from all n; the knots in a uniformly shuffled
    order. Planted as in planted()."""
    tag = f"embed|{n}|{frac:.6f}|{alpha_r:.6f}|{alpha_l:.6f}|{alpha_c:.6f}|{w}|{seed}".encode()
    rng = np.random.default_rng(int.from_bytes(hashlib.sha256(tag).digest()[:8], "little"))
    hidden = rng.integers(0, 2, n, dtype=np.int8)
    while hidden.min() == hidden.max():
        hidden = rng.integers(0, 2, n, dtype=np.int8)
    ne = int(round(frac * n))
    while hidden[:ne].min() == hidden[:ne].max() or hidden[ne:].min() == hidden[ne:].max():
        hidden = rng.integers(0, 2, n, dtype=np.int8)  # a constant part allows no knot (only at tiny n; SLOW-LOOP referee)

    def draw(need, kind):
        out = []
        while need > 0:
            batch = max(64, int(need * 1.6))
            if kind == "local":
                c = rng.integers(0, ne, batch)
                off = rng.integers(-w, w + 1, (batch, 2))
                t = np.stack([c, (c + off[:, 0]) % ne, (c + off[:, 1]) % ne], axis=1)
            elif kind == "rest":
                t = rng.integers(ne, n, (batch, 3))
            else:
                t = rng.integers(0, n, (batch, 3))
            ok = (t[:, 0] != t[:, 1]) & (t[:, 0] != t[:, 2]) & (t[:, 1] != t[:, 2])
            sm = hidden[t].sum(axis=1)
            ok &= (sm == 1) | (sm == 2)
            t = t[ok][:need]
            out.append(t)
            need -= len(t)
        return np.concatenate(out) if out else np.zeros((0, 3), np.int64)

    knots = np.concatenate([draw(int(round(alpha_l * ne)), "local"), draw(int(round(alpha_r * (n - ne))), "rest"),
                            draw(int(round(alpha_c * n)), "all")])
    knots = knots[rng.permutation(len(knots))].astype(np.int32)
    return Instance(n, knots, hidden, name=tag.decode())


def run_seed(*parts) -> int:
    return int.from_bytes(hashlib.sha256("|".join(map(str, parts)).encode()).digest()[:8], "little")


# ---------------------------------------------------------------- the fast loop alone

def _handle(n, kv, ks, x, lastflip, rngst, sseed, t, probed=None):
    w = ctypes.c_int64(0)
    pr = None if probed is None else np.ascontiguousarray(probed, dtype=np.uint8)
    h = lib().fl_new(int(n), int(np.asarray(ks).size // 3), np.ascontiguousarray(kv.reshape(-1), dtype=np.int32),
                     np.ascontiguousarray(ks.reshape(-1), dtype=np.uint8), np.ascontiguousarray(x, dtype=np.uint8),
                     np.ascontiguousarray(lastflip, dtype=np.int64), np.ascontiguousarray(rngst, dtype=np.uint64),
                     ctypes.c_uint64(sseed & (2**64 - 1)), int(t),
                     pr.ctypes.data if pr is not None else None, ctypes.byref(w))
    return h, int(w.value)


def initial_state(n: int, seed: int):
    x = np.zeros(n, dtype=np.uint8)
    r = np.zeros(2, dtype=np.uint64)
    lib().fl_init_state(int(n), ctypes.c_uint64(seed & (2**64 - 1)), x, r)
    return x, r


def run_fast(inst: Instance, algo: str, params, seed: int, cap: int) -> dict:
    """The fast loop alone on the original pattern: one call, as WHERE-NEXT's engine runs it."""
    c0 = time.thread_time()
    x, r = initial_state(inst.n, seed)
    h, w0 = _handle(inst.n, inst.knots, np.zeros(inst.knots.shape, np.uint8), x, np.full(inst.n, -1, np.int64), r,
                    0, 0)
    p = np.zeros(4)
    p[: len(params)] = params
    out = np.zeros(5)
    lib().fl_run(h, ALGOS[algo], p, int(cap), out)
    xs = np.zeros(inst.n, dtype=np.uint8)
    lib().fl_get(h, xs, np.zeros(inst.n, np.int64), np.zeros(2, np.uint64), None, np.zeros(max(1, inst.m), np.int32),
                 np.zeros(max(1, inst.m), np.uint8))
    lib().fl_free(h)
    solved = bool(out[1])
    ok = inst.satisfied(xs) if solved else None
    return {"flips": int(out[0]), "solved": solved, "verified": ok, "work_fast": int(out[3]) + w0, "work_slow": 0,
            "work_rebuild": 0, "work": int(out[3]) + w0, "cpu": time.thread_time() - c0, "minviol": int(out[2])}


# ---------------------------------------------------------------- tie classes and the rebuilt pattern

class Ties:
    """Tie classes with parity, kept in C (sl_reduce): x_v = x_root(v) ^ parity(v) in every allowed state."""

    def __init__(self, n: int):
        self.n = n
        self.parent = np.arange(n, dtype=np.int32)
        self.par = np.zeros(n, dtype=np.uint8)
        self.size = np.ones(n, dtype=np.int32)
        self.root = np.arange(n, dtype=np.int32)
        self.rpar = np.zeros(n, dtype=np.uint8)
        self.contradiction = False


def sig_keys(kv: np.ndarray, ks: np.ndarray, n0: int) -> np.ndarray:
    """One integer per signed knot (members in original ids, canonical signs)."""
    k = kv.astype(np.int64)
    return (((k[:, 0] * n0 + k[:, 1]) * n0 + k[:, 2]) * 8 + ks[:, 0].astype(np.int64) * 4
            + ks[:, 1].astype(np.int64) * 2 + ks[:, 2].astype(np.int64))


def reduce_pattern(knots0: np.ndarray, shadows: list, ties: Ties, new_ties: np.ndarray):
    """Merge the new ties and every tie that merging forces (C, worklist); map every original and derived knot
    through the tie classes, drop knots that always hold, canonicalize. Returns (roots, kv, ks, work) with kv in
    original root ids."""
    if shadows:
        b = np.array(shadows, dtype=np.int64)
        kv_all = np.concatenate([knots0.astype(np.int64), b[:, :3]]).astype(np.int32)
        ks_all = np.concatenate([np.zeros((len(knots0), 3), np.uint8), b[:, 3:].astype(np.uint8)])
    else:
        kv_all = np.ascontiguousarray(knots0, dtype=np.int32)
        ks_all = np.zeros((len(knots0), 3), np.uint8)
    nt = np.ascontiguousarray(new_ties.reshape(-1), dtype=np.int32) if len(new_ties) else np.zeros(3, np.int32)
    out = np.zeros(2)
    m = len(kv_all)
    kvo = np.zeros(3 * m, np.int32)
    kso = np.zeros(3 * m, np.uint8)
    keep = np.zeros(m, np.uint8)
    lib().sl_reduce(ties.n, m, np.ascontiguousarray(kv_all.reshape(-1)), np.ascontiguousarray(ks_all.reshape(-1)),
                    ties.parent, ties.par, ties.size, len(new_ties), nt, ties.root, ties.rpar, kvo, kso, keep, out)
    ties.contradiction |= bool(out[0])
    keep = keep.astype(bool)
    kv = kvo.reshape(-1, 3)[keep]
    ks = kso.reshape(-1, 3)[keep]
    _, idx = np.unique(sig_keys(kv, ks, ties.n), return_index=True)
    idx.sort()
    kv, ks = kv[idx], ks[idx]
    roots = np.unique(ties.root)
    return roots, kv, ks, int(out[1])


# ---------------------------------------------------------------- fast and slow loops together

DEFAULT_POLICY = {"e": 1.0, "rho": 0.3, "beta": 0.0, "J": 2, "pb": 4000, "backoff": True, "mode": 0}


CHARGE = "v2"


def _sortcost(k: int) -> int:
    """Charge for sorting or set-merging k items: k ceil(log2(k + 1)) operations."""
    return int(k * math.ceil(math.log2(k + 1))) if k > 0 else 0


def run_slow(inst: Instance, algo: str, params, seed: int, cap: int, policy: dict, static: bool = False,
             debug: bool = False, mutant: bool = False, charge: str | None = None) -> dict:
    """The fast loop in epochs of e * n flips (n the current number of tie classes); after each epoch the slow loop
    spends at most rho times the epoch's fast work on probes (guided by where the fast loop dwelt, or random), and the
    pattern is rebuilt when it found a move. With backoff, an epoch whose probes found nothing halves the next epoch's
    slow budget (down to rho / 64); a find restores it.
    static=True: probe every knot before the search (each followed by shadow-knot probes with probability
    policy['beta']), repeating passes on the rebuilt pattern (knots whose signature changed) while a pass finds a move, at
    most policy['passes'] passes; a pass that has probed policy['abort'] * m knots without a find stops (abort 0: never).
    Then the fast loop alone to the cap.
    mutant=True (gate G4 only): every tie is applied with the wrong parity.
    charge "v2" (the default; EARN-BUDGET-20261117-001A, after SLOW-LOOP's referee): the rebuild's Python-side operations are
    charged too: the dedup and the roots' unique, the probed flags' isin, the probed-key union, the majority vote, and the
    guided order's sort, each sort or set merge of k items as k ceil(log2(k + 1)). "v1" is SLOW-LOOP's charge, which omits them.
    Earned budget (policy["earn"], EARN-BUDGET-20261117-001A): the slow budget starts at rho_min. After an epoch's slow pass
    and rebuild, q = (classes merged / classes before) / ((probe work + rebuild work) / the epoch's fast work), the share of
    the pattern removed per unit of relative slow cost. The next budget doubles (up to rho_max) when q >= theta and halves
    (down to rho_min) otherwise, including when nothing was found.
    Batched rebuilds (policy["rb"] > 0, EARN-BUDGET-20261117-001A; for the earned budget and for a fixed one): since a rebuild
    costs about ten reads per knot whatever it merges, the moves found are kept, and the pattern is rebuilt only when those
    found since the last rebuild number at least rb times the current classes (at least one); q is measured over all the
    epochs since the last rebuild. Without rb the driver is SLOW-LOOP's, run for run."""
    c0 = time.thread_time()
    L = lib()
    n0 = inst.n
    p = np.zeros(4)
    p[: len(params)] = params
    xr, rngst = initial_state(n0, seed)  # state, indexed by original distinction, valid at roots
    lfr = np.full(n0, -1, dtype=np.int64)
    ties = Ties(n0)
    shadows: list = []
    probed_keys = np.zeros(0, dtype=np.int64)
    t = 0
    flips = work_fast = work_slow = work_rebuild = 0
    cpu_slow = cpu_fast = cpu_rebuild = 0.0
    minviol = None
    epochs = rebuilds = targets = nties = nshadows = 0
    contra = False
    capt = 4 * inst.m + 16
    capb = 4 * inst.m + 16
    tie_buf = np.zeros(3 * capt, dtype=np.int32)
    br_buf = np.zeros(6 * capb, dtype=np.int32)
    sl_out = np.zeros(6)
    fl_out = np.zeros(5)

    v2 = (charge or CHARGE) == "v2"

    def build(new_ties):
        nonlocal work_rebuild
        roots, kv, ks, w = reduce_pattern(inst.knots, shadows, ties, new_ties)
        idx = np.full(n0, -1, dtype=np.int64)
        idx[roots] = np.arange(len(roots))
        kvn = idx[kv].astype(np.int32)
        pr = np.isin(sig_keys(kv, ks, n0), probed_keys).astype(np.uint8) if len(probed_keys) else None
        work_rebuild += w + n0
        if v2:
            work_rebuild += _sortcost(len(inst.knots) + len(shadows)) + _sortcost(n0) + len(kv)
            if len(probed_keys):
                work_rebuild += _sortcost(len(kv) + len(probed_keys))
        return roots, kv, ks, kvn, pr

    # the unmutated pattern as given, so that until the first move the fast loop runs exactly as it runs alone
    roots, kv, ks, pr = np.arange(n0), inst.knots.copy(), np.zeros(inst.knots.shape, np.uint8), None
    kvn = kv
    h, w0 = _handle(len(roots), kvn, ks, xr[roots], lfr[roots], rngst, run_seed("slow", seed), t, pr)
    L.fl_set_sortlog(h, int(v2))
    work_fast += w0
    earn = bool(policy.get("earn"))
    batch = (not static) and policy.get("rb", 0) > 0
    assert batch or not earn, "the earned budget needs batched rebuilds (rb > 0)"
    pend_ties: list = []
    ws_acc = wf_acc = 0
    rho_eff = policy["rho_min"] if earn else policy.get("rho", 0.0)
    rho_top = rho_eff
    doublings = 0
    passes_done = 0
    pass_cap = policy.get("passes", 8)
    while True:
        nr = len(roots)
        if static:
            budget_flips = cap - flips if passes_done >= pass_cap else 0
        else:
            budget_flips = min(cap - flips, max(policy.get("epoch_min", 100), int(round(policy["e"] * nr))))
        if budget_flips > 0 or L.fl_nviol(h) == 0:
            L.fl_run(h, ALGOS[algo], p, int(budget_flips), fl_out)
            flips += int(fl_out[0])
            work_fast += int(fl_out[3])
            cpu_fast += float(fl_out[4])
            minviol = int(fl_out[2]) if minviol is None else min(minviol, int(fl_out[2]))
            epochs += 1
            if fl_out[1] or flips >= cap:
                break
        # the slow loop
        abort_after = 0
        if static:
            mode, budget, beta = 2, 0, policy.get("beta", 0.0)
            if policy.get("abort", 0) > 0:
                abort_after = max(1, int(np.ceil(policy["abort"] * len(ks))))
        else:
            mode, budget, beta = policy["mode"], int(rho_eff * fl_out[3]), policy["beta"]
            if budget < 1:
                continue
        nfound = L.sl_probe(h, mode, budget, int(policy["pb"]), float(beta), int(policy["J"]), abort_after, tie_buf, capt,
                            br_buf, capb, sl_out)
        targets += int(sl_out[0])
        work_slow += int(sl_out[3])
        cpu_slow += float(sl_out[4])
        contra |= bool(sl_out[5])
        passes_done += 1
        nt, nb = int(sl_out[1]), int(sl_out[2])
        if static and nfound == 0:
            passes_done = pass_cap
        if batch:
            ws_acc += int(sl_out[3])
            wf_acc += int(fl_out[3])
            if nt:
                tb = tie_buf[: 3 * nt].reshape(-1, 3).astype(np.int64)
                pend_ties.extend(zip(roots[tb[:, 0]].tolist(), roots[tb[:, 1]].tolist(), (tb[:, 2] ^ int(mutant)).tolist()))
                nties += nt
            for j in range(nb):
                a, b, c, sa, sb, sc = br_buf[6 * j: 6 * j + 6]
                shadows.append((int(roots[a]), int(roots[b]), int(roots[c]), int(sa), int(sb), int(sc)))
            nshadows += nb
            if nfound and len(pend_ties) + nb < max(1, int(np.ceil(policy["rb"] * nr))):
                continue  # keep the moves for a later rebuild; the budget is left as it is
        if nfound == 0:
            if earn:
                rho_eff = max(policy["rho_min"], rho_eff / 2.0)
            elif not static and policy["backoff"]:
                rho_eff = max(policy["rho"] / 64.0, rho_eff / 2.0)
            continue
        if not earn:
            rho_eff = policy.get("rho", 0.0)
        n_before, wr_before = nr, work_rebuild
        c_rb = time.thread_time()
        # read the state back to original ids, record what was probed, apply the moves, rebuild
        mcur = len(ks)
        xs = np.zeros(nr, dtype=np.uint8)
        lf = np.zeros(nr, dtype=np.int64)
        tt = ctypes.c_int64(0)
        prb = np.zeros(max(1, mcur), dtype=np.uint8)
        L.fl_get(h, xs, lf, rngst, ctypes.byref(tt), np.zeros(max(1, mcur), np.int32), prb)
        t = int(tt.value)
        xr[roots] = xs
        lfr[roots] = lf
        if mcur:
            newk = sig_keys(kv[prb[:mcur] == 1], ks[prb[:mcur] == 1], n0)
            if v2:
                work_rebuild += _sortcost(len(probed_keys) + len(newk)) + mcur
            probed_keys = np.union1d(probed_keys, newk)
        if batch:
            new_ties = np.array(pend_ties, dtype=np.int32).reshape(-1, 3)
            pend_ties = []
        else:
            tb = tie_buf[: 3 * nt].reshape(-1, 3).astype(np.int64)
            new_ties = np.stack([roots[tb[:, 0]], roots[tb[:, 1]], tb[:, 2] ^ int(mutant)], axis=1).astype(np.int32) \
                if nt else np.zeros((0, 3), np.int32)
            nties += nt
            for j in range(nb):
                a, b, c, sa, sb, sc = br_buf[6 * j: 6 * j + 6]
                shadows.append((int(roots[a]), int(roots[b]), int(roots[c]), int(sa), int(sb), int(sc)))
            nshadows += nb
        L.fl_free(h)
        xo = xr[ties.root] ^ ties.rpar  # the current state of every original distinction
        roots, kv, ks, kvn, pr = build(new_ties)
        rebuilds += 1
        # a merged class takes the value most of its members hold now (ties go to the root's own); the root's age
        imp = xo ^ ties.rpar
        vote = np.bincount(ties.root, weights=imp, minlength=n0)
        size = np.bincount(ties.root, minlength=n0)
        xr = np.where(2 * vote > size, 1, np.where(2 * vote < size, 0, xo)).astype(np.uint8)
        if v2:
            work_rebuild += 4 * n0  # the current state, the vote, the class sizes, the new values
        h, w0 = _handle(len(roots), kvn, ks, xr[roots], lfr[roots], rngst, run_seed("slow", seed, rebuilds), t, pr)
        L.fl_set_sortlog(h, int(v2))
        work_rebuild += w0
        contra |= ties.contradiction
        cpu_rebuild += time.thread_time() - c_rb
        if batch:
            cost = (ws_acc + work_rebuild - wr_before) / max(1, wf_acc)
            ws_acc = wf_acc = 0
        if earn:
            q = ((n_before - len(roots)) / n_before) / max(cost, 1e-12)
            if q >= policy["theta"]:
                rho_eff = min(policy["rho_max"], 2.0 * rho_eff)
                doublings += 1
            else:
                rho_eff = max(policy["rho_min"], rho_eff / 2.0)
            rho_top = max(rho_top, rho_eff)
    # map back and check on the original knots
    xs = np.zeros(len(roots), dtype=np.uint8)
    L.fl_get(h, xs, np.zeros(len(roots), np.int64), np.zeros(2, np.uint64), None, np.zeros(max(1, len(ks)), np.int32),
             np.zeros(max(1, len(ks)), np.uint8))
    L.fl_free(h)
    xr[roots] = xs
    xo = (xr[ties.root] ^ ties.rpar).astype(np.uint8)
    solved = bool(fl_out[1])
    ok = inst.satisfied(xo) if solved else None
    work = work_fast + work_slow + work_rebuild
    res = {"flips": flips, "solved": solved, "verified": ok, "work_fast": work_fast, "work_slow": work_slow,
           "work_rebuild": work_rebuild, "work": work, "cpu": time.thread_time() - c0, "cpu_fast": cpu_fast,
           "cpu_slow": cpu_slow, "cpu_rebuild": cpu_rebuild, "minviol": minviol if minviol is not None else -1,
           "epochs": epochs, "rebuilds": rebuilds, "targets": targets, "ties": nties, "shadows": nshadows,
           "n_final": int(len(roots)), "m_final": int(len(ks)), "contradiction": bool(contra),
           "rho_top": float(rho_top), "doublings": doublings}
    if debug:
        res.update({"root": ties.root.copy(), "rpar": ties.rpar.copy(), "shadow_list": list(shadows), "state": xo,
                    "kv": kv.copy(), "ks": ks.copy(), "roots": roots.copy()})
    return res


def cadical(inst: Instance, time_limit: float = 60.0, solver_name: str = "cadical195") -> dict:
    """Exact search (CDCL with its own preprocessing and inprocessing) on the CNF encoding."""
    import threading

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
    ok = None
    if model is not None:
        x = np.zeros(inst.n, dtype=np.int8)
        for lit in model:
            if abs(lit) <= inst.n:
                x[abs(lit) - 1] = 1 if lit > 0 else 0
        ok = inst.satisfied(x)
    return {"result": res, "cpu": time.process_time() - t0, "wall": time.perf_counter() - w0,
            "conflicts": int(stats.get("conflicts", -1)), "propagations": int(stats.get("propagations", -1)),
            "decisions": int(stats.get("decisions", -1)), "model_ok": ok}
