"""A persistent handle on the navigating agent's run, and the rule that carries its memory across a rebuild
(SIGNED-NAV-20261117-001, groundwork for the slow loop; no claims).

    h = AgentHandle(inst, algo, params, theta, flags, seed, state=None)
    h.run(budget)            -> the engine's out dict for this call
    st = h.state()           -> AgentState (x, every memory array, the random stream, t, the recurrent state, ...)
    st2 = carry(st, old, new, dist_from, par, knot_from, x_new=None)
    h2 = AgentHandle(new, algo, params, theta, flags, seed, state=st2)

**The carry rule** (what the memory of a distinction or knot becomes when the pattern is rebuilt). The caller gives, for
each new distinction c, the old distinctions it comes from (`dist_from[c]`, with parities `par[v]`: x_old[v] = x_new[c] ^
par[v]), and for each new knot the old knots it comes from (`knot_from[k]`, possibly empty). A merge lists several old
distinctions or knots under one new one; a split lists one old one under several new ones; an unchanged pattern lists
each under itself.
- **Value.** `x_new` if the caller gives it (the slow loop takes a majority vote); otherwise the first listed member's
  value, corrected by its parity.
- **Last flip.** The most recent last flip among the members (never flipped only if none was). A class remembers its
  latest change; a part of a split inherits its source's.
- **Recent counts.** One member: its count as it stands. Several: each member's 50-step count decayed to the present, summed,
  stamped now. A split part inherits the whole count.
- **Knots.** The same: the most recent last visit among its old knots, and their visit counts decayed and summed. A knot
  with no old knot is new: never visited.
- **The run.** The random stream, the step counter t, the recurrent state and the last flipped distinction (mapped to its
  new class, or none) carry over unchanged.
- **Attention.** The violated list keeps its order for knots that survive (new ones follow by index), and the knots the last
  flip violated are mapped to their new knots, dropping any that have no new knot.
On an unchanged pattern (each distinction and knot listed under itself, parity 0) the rule restores the state exactly, so
the run continues as if never interrupted (gate H-rebuild-identity).
"""
from __future__ import annotations

import ctypes
import math
from dataclasses import dataclass, field, replace
from pathlib import Path

import numpy as np

import engine as E

HR = 6
TAU = 50.0


def _lib():
    L = E.lib()
    if not getattr(L, "_na_ready", False):
        vp = ctypes.c_void_p
        L.na_new.argtypes = [ctypes.c_int, ctypes.c_int, vp, vp, vp, vp, vp, ctypes.c_int, vp, vp, ctypes.c_int,
                             ctypes.c_uint64, vp, vp, vp, vp, vp, vp, vp, vp, ctypes.c_int64, vp, ctypes.c_int,
                             vp, ctypes.c_int, vp, ctypes.c_int]
        L.na_new.restype = vp
        L.na_run.argtypes = [vp, ctypes.c_int64, vp]
        L.na_get.argtypes = [vp] + [vp] * 10 + [vp, vp, vp, vp, vp]
        L.na_free.argtypes = [vp]
        L.na_nviol.argtypes = [vp]
        L.na_work_total.argtypes = [vp]
        L.na_work_total.restype = ctypes.c_int64
        L._na_ready = True
    return L


def _p(a):
    return None if a is None else a.ctypes.data


@dataclass
class AgentState:
    x: np.ndarray
    lastflip: np.ndarray
    fcnt: np.ndarray
    fcnt_t: np.ndarray
    lastvisit: np.ndarray
    vcnt: np.ndarray
    vcnt_t: np.ndarray
    rngst: np.ndarray
    t: int
    h: np.ndarray
    last_var: int
    vlist: np.ndarray = field(default_factory=lambda: np.zeros(0, np.int32))
    newk: np.ndarray = field(default_factory=lambda: np.zeros(0, np.int32))


class AgentHandle:
    def __init__(self, inst: E.Instance, algo: str, params=(), theta=None, flags: int = 0, seed: int = 0,
                 state: AgentState | None = None, x0: np.ndarray | None = None):
        """state: carry a whole state (carry()); otherwise a fresh run seeded from seed, from x0 if given (else drawn as
        nae_run_signed draws it)."""
        L = _lib()
        self.inst = inst
        self.params = np.zeros(4)
        self.params[: len(params)] = params
        self.theta = np.zeros(E.ntheta()) if theta is None else np.ascontiguousarray(theta, dtype=np.float64)
        st = state
        c = np.ascontiguousarray
        if st is not None:
            arrs = dict(x=c(st.x, dtype=np.uint8), lf=c(st.lastflip, dtype=np.int64), fc=c(st.fcnt, dtype=np.float64),
                        ft=c(st.fcnt_t, dtype=np.int64), lv=c(st.lastvisit, dtype=np.int64), vc=c(st.vcnt, dtype=np.float64),
                        vt=c(st.vcnt_t, dtype=np.int64), rs=c(st.rngst, dtype=np.uint64), h=c(st.h, dtype=np.float64),
                        vo=c(st.vlist, dtype=np.int32), nk=c(st.newk, dtype=np.int32))
            self._keep = arrs
            self.h = L.na_new(inst.n, inst.m, inst.kv.ctypes.data, inst.os.ctypes.data, inst.occ.ctypes.data,
                              _p(inst.signs), _p(inst.ocs), E.ALGOS[algo], self.params.ctypes.data,
                              self.theta.ctypes.data, int(flags), ctypes.c_uint64(seed & (2**64 - 1)),
                              arrs["x"].ctypes.data, arrs["lf"].ctypes.data, arrs["fc"].ctypes.data, arrs["ft"].ctypes.data,
                              arrs["lv"].ctypes.data, arrs["vc"].ctypes.data, arrs["vt"].ctypes.data, arrs["rs"].ctypes.data,
                              int(st.t), arrs["h"].ctypes.data, int(st.last_var),
                              arrs["vo"].ctypes.data if len(arrs["vo"]) else None, len(arrs["vo"]),
                              arrs["nk"].ctypes.data if len(arrs["nk"]) else None, len(arrs["nk"]))
        else:
            xa = None if x0 is None else c(x0, dtype=np.uint8)
            self._keep = {"x": xa}
            self.h = L.na_new(inst.n, inst.m, inst.kv.ctypes.data, inst.os.ctypes.data, inst.occ.ctypes.data,
                              _p(inst.signs), _p(inst.ocs), E.ALGOS[algo], self.params.ctypes.data,
                              self.theta.ctypes.data, int(flags), ctypes.c_uint64(seed & (2**64 - 1)),
                              _p(xa), None, None, None, None, None, None, None, 0, None, -1, None, 0, None, 0)

    def run(self, budget: int) -> dict:
        out = np.zeros(10)
        _lib().na_run(self.h, int(budget), out.ctypes.data)
        return {"flips": int(out[0]), "solved": bool(out[1]), "minviol": int(out[2]), "work": int(out[3]),
                "cpu": float(out[4]), "new_chosen": int(out[5]), "new_avail": int(out[6]),
                "distinct_sum": int(out[7]), "where_steps": int(out[8]), "accepted": int(out[9])}

    def nviol(self) -> int:
        return _lib().na_nviol(self.h)

    def work_total(self) -> int:
        return _lib().na_work_total(self.h)

    def state(self) -> AgentState:
        n, m = self.inst.n, self.inst.m
        x = np.zeros(n, np.uint8)
        lf = np.zeros(n, np.int64)
        fc = np.zeros(n)
        ft = np.zeros(n, np.int64)
        lv = np.zeros(max(m, 1), np.int64)
        vc = np.zeros(max(m, 1))
        vt = np.zeros(max(m, 1), np.int64)
        rs = np.zeros(2, np.uint64)
        hs = np.zeros(HR)
        vl = np.zeros(max(m, 1), np.int32)
        nk = np.zeros(3, np.int32)
        t = ctypes.c_int64()
        lv_ = ctypes.c_int()
        nv = ctypes.c_int()
        nn = ctypes.c_int()
        _lib().na_get(self.h, x.ctypes.data, lf.ctypes.data, fc.ctypes.data, ft.ctypes.data, lv.ctypes.data, vc.ctypes.data,
                      vt.ctypes.data, rs.ctypes.data, ctypes.addressof(t), hs.ctypes.data, ctypes.addressof(lv_),
                      vl.ctypes.data, ctypes.addressof(nv), nk.ctypes.data, ctypes.addressof(nn))
        return AgentState(x, lf, fc, ft, lv[:m], vc[:m], vt[:m], rs, int(t.value), hs, int(lv_.value),
                          vl[: nv.value].copy(), nk[: nn.value].copy())

    def close(self):
        if self.h:
            _lib().na_free(self.h)
            self.h = None

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


def _decayed(c, ct, t):
    return np.where(ct < 0, 0.0, c * np.exp(-(t - ct) / TAU))


def carry(st: AgentState, n_new: int, m_new: int, dist_from: list, par: np.ndarray, knot_from: list,
          x_new: np.ndarray | None = None) -> AgentState:
    """The carry rule (module docstring). dist_from[c]: old distinctions of new distinction c; par[v]: parity of old v
    (x_old[v] = x_new[class(v)] ^ par[v]); knot_from[k]: old knots of new knot k."""
    t = st.t
    fdec = _decayed(st.fcnt, st.fcnt_t, t)
    vdec = _decayed(st.vcnt, st.vcnt_t, t)
    x = np.zeros(n_new, np.uint8)
    lf = np.full(n_new, -1, np.int64)
    fc = np.zeros(n_new)
    ft = np.full(n_new, -1, np.int64)
    cls = {}
    for c, members in enumerate(dist_from):
        members = list(members)
        if not members:
            continue
        x[c] = st.x[members[0]] ^ par[members[0]]
        lf[c] = max(int(st.lastflip[v]) for v in members)
        if len(members) == 1:
            fc[c], ft[c] = st.fcnt[members[0]], st.fcnt_t[members[0]]
        elif any(st.fcnt_t[v] >= 0 for v in members):
            fc[c], ft[c] = float(sum(fdec[v] for v in members)), t
        for v in members:
            cls.setdefault(v, c)
    if x_new is not None:
        x = np.ascontiguousarray(x_new, dtype=np.uint8)
    lv = np.full(m_new, -1, np.int64)
    vc = np.zeros(m_new)
    vt = np.full(m_new, -1, np.int64)
    kmap = {}
    for k, olds in enumerate(knot_from):
        olds = list(olds)
        if not olds:
            continue
        lv[k] = max(int(st.lastvisit[j]) for j in olds)
        if len(olds) == 1:
            vc[k], vt[k] = st.vcnt[olds[0]], st.vcnt_t[olds[0]]
        elif any(st.vcnt_t[j] >= 0 for j in olds):
            vc[k], vt[k] = float(sum(vdec[j] for j in olds)), t
        for j in olds:
            kmap.setdefault(j, k)
    vlist = np.array([kmap[j] for j in st.vlist if j in kmap], dtype=np.int32)
    newk = np.array([kmap[j] for j in st.newk if j in kmap], dtype=np.int32)
    last_var = cls.get(st.last_var, -1) if st.last_var >= 0 else -1
    return AgentState(x, lf, fc, ft, lv, vc, vt, st.rngst.copy(), t, st.h.copy(), last_var, vlist, newk)


def identity_maps(inst: E.Instance):
    return [[v] for v in range(inst.n)], np.zeros(inst.n, np.uint8), [[k] for k in range(inst.m)]
