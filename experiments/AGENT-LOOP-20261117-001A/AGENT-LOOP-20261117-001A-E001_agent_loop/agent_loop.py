"""The learned agent as the fast loop under the proof-based slow loop (AGENT-LOOP-20261117-001A).

The slow loop is EARN-BUDGET's eager batched one:
- **Budget.** After each epoch of the fast loop, it spends rho times that epoch's charged fast work on tie probes (bounded
  refutations by propagation).
- **Batching.** It keeps the ties it proves, and rebuilds the pattern when they reach rb times the current classes.
- **The moves keep the allowed states.**

The fast loop is one of:
- **"agent":** MEET-TRANSFER's learned agent through SIGNED-NAV's handle (copied into `agent/`). At a rebuild its whole state is
  either carried by SIGNED-NAV's carry rule ("carry") or restarted from the mapped values with fresh memory ("restart").
- **"nov":** Novelty+ in this study's engine; its state (values, ages) is kept at a rebuild, as in EARN-BUDGET.
- **"none":** no fast loop, the slow loop alone. Each round it probes with the budget of an epoch of n' flips at the fixed unit
  (below) and rebuilds when it can; it solves only if the pattern collapses to no knots, and it stops, unsolved, when a round
  finds nothing and no unprobed knot is left.

The slow budget of an epoch is rho times one of:
- **the epoch's own charged fast work** (EARN-BUDGET's rule, the default);
- **the epoch's flips times a fixed unit** `pol["unit"]` (50 incidences, about Novelty+'s cost per flip on the local
  patterns), so that two fast loops of different cost per flip get the same proof effort per flip.

Probe targets are one of:
- **"random":** unprobed knots drawn uniformly (EARN-BUDGET's Gpr);
- **"coflip":** the co-knotted pairs the fast loop keeps moving together (SPEC-MERGE's stability counts), most stable first,
  each tested by the pair probe. This is SPEC-MERGE's gate D signal used as a guide for what to prove, not as a licence to
  merge.

The charge is v2:
- the fast loop's own incidences (for the agent, its engine's count, reads included);
- the probes;
- the stability counts (4 per pair, 2 per distinction);
- every rebuild with its sorting, the carry's mapping (one per old distinction and knot, plus the sort of the knot keys), and the
  new handles' counts.

Whole-run thread CPU is reported beside it. Every reported state is mapped back and checked on the original knots.
"""
from __future__ import annotations

import ctypes
import math
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "agent"))
import engine as AE  # noqa: E402  (the agent's engine)
import handle as AH  # noqa: E402
import slow_loop as S  # noqa: E402
import spec_merge as M  # noqa: E402

GPR = {"e": 1.0, "rho": 3.0, "pb": 4000, "rb": 0.003}


def _canon(rv, rs):
    o = np.argsort(rv, axis=1, kind="stable")
    rv = np.take_along_axis(rv, o, axis=1)
    rs = np.take_along_axis(rs, o, axis=1)
    return rv, rs ^ rs[:, :1]


class _Fast:
    """The fast loop on the current pattern: its handle, run, state read and rebuild."""

    def __init__(self, kind, inst, params, theta, flags, seed):
        self.kind, self.params, self.theta, self.flags, self.seed = kind, params, theta, flags, seed
        if kind == "agent":
            self.h = AH.AgentHandle(AE.Instance(inst.n, inst.knots), "policy", (), theta, flags, seed)
        elif kind == "none":
            self.x = np.zeros(inst.n, np.uint8)
        else:
            x, r = S.initial_state(inst.n, seed)
            self.h, self.w0 = S._handle(inst.n, inst.knots, np.zeros(inst.knots.shape, np.uint8), x,
                                        np.full(inst.n, -1, np.int64), r, S.run_seed("slow", seed), 0, None)
            S.lib().fl_set_sortlog(self.h, 1)
            self.p = np.zeros(4)
            self.p[: len(params)] = params

    def run(self, budget):
        if self.kind == "agent":
            r = self.h.run(budget)
            return r["flips"], r["solved"], r["work"], r["cpu"], r["minviol"]
        out = np.zeros(5)
        S.lib().fl_run(self.h, 4, self.p, int(budget), out)
        return int(out[0]), bool(out[1]), int(out[3]), float(out[4]), int(out[2])

    def values(self, n, m):
        if self.kind == "none":
            return self.x
        if self.kind == "agent":
            return self.h.state().x.astype(np.uint8)
        x, _, _, _, _ = M._state(self.h, n, m)
        return x


def run_loop(inst: S.Instance, fast: str, seed: int, cap: int, pol: dict = GPR, memory: str = "carry",
             target: str = "random", params=(0.7, 0.01), theta=None, flags: int = 0, rho_override=None,
             debug: bool = False) -> dict:
    c0 = time.thread_time()
    L = S.lib()
    n0 = inst.n
    rho = pol["rho"] if rho_override is None else rho_override
    ties = S.Ties(n0)
    roots = np.arange(n0)
    kv, ks = inst.knots.copy(), np.zeros(inst.knots.shape, np.uint8)
    kvn = kv
    F = _Fast(fast, inst, params, theta, flags, seed)
    flips = work_fast = work_slow = work_rebuild = 0
    cpu_fast = 0.0
    work_fast += 3 * inst.m if fast == "agent" else (0 if fast == "none" else F.w0)
    # the probe handle on the current pattern (its values are not read by the probes)
    ph, w0 = S._handle(n0, kv, ks, np.zeros(n0, np.uint8), np.full(n0, -1, np.int64), np.zeros(2, np.uint64),
                       S.run_seed("probe", seed), 0, None)
    L.fl_set_sortlog(ph, 1)
    work_rebuild += w0
    capt = 4 * inst.m + 16
    tie_buf = np.zeros(3 * capt, np.int32)
    br_buf = np.zeros(6 * 16, np.int32)
    sl_out = np.zeros(6)
    pend: list = []
    probed_keys = np.zeros(0, np.int64)
    pair_probed: set = set()
    stats = None
    if target == "coflip":
        x0 = F.values(n0, inst.m)
        nf = np.zeros(n0, np.int32) if fast == "agent" else M._state(F.h, n0, inst.m)[4]
        stats = M.Stats(kvn.astype(np.int64), x0, nf)
        prev_t_flip = None
    rebuilds = probes = epochs = 0
    flips_first = None  # flips made before the first rebuild (None: never rebuilt)
    solved = False
    lf_prev = None

    def moved_counts():
        """Per current distinction, a count that grows whenever it flips: the engine's counter for Novelty+; for the agent,
        its last-flip step, which changes whenever it flips."""
        if fast == "agent":
            st = F.h.state()
            return st.x.astype(np.uint8), (st.lastflip + 1).astype(np.int64)
        x, _, _, _, nf = M._state(F.h, len(roots), len(ks))
        return x, nf.astype(np.int64)

    while True:
        nr = len(roots)
        budget = min(cap - flips, max(100, int(round(pol["e"] * nr))))
        if fast == "none":
            fl, ok, wk, cpu = 0, False, 0, 0.0
        else:
            fl, ok, wk, cpu, mv = F.run(budget)
        flips += fl
        work_fast += wk
        cpu_fast += cpu
        epochs += 1
        if ok:
            solved = True
            break
        if flips >= cap or (fast == "none" and work_slow + work_rebuild >= cap * pol.get("unit", 50)):
            break
        if fast == "none":
            b = int(rho * pol.get("unit", 50) * budget)
        elif pol.get("unit"):
            b = int(rho * pol["unit"] * fl)
        else:
            b = int(rho * wk)
        stuck = False
        if b >= 1:
            if target == "random":
                L.sl_probe(ph, 1, b, int(pol["pb"]), 0.0, 2, 0, tie_buf, capt, br_buf, 16, sl_out)
                if fast == "none" and int(sl_out[0]) == 0:  # random draws found no unprobed knot: sweep for one
                    work_slow += int(sl_out[3]) + len(ks)  # the sweep reads every knot's probed mark
                    L.sl_probe(ph, 2, b, int(pol["pb"]), 0.0, 2, 0, tie_buf, capt, br_buf, 16, sl_out)
                    stuck = int(sl_out[0]) == 0
                work_slow += int(sl_out[3])
                probes += int(sl_out[0])
                nt = int(sl_out[1])
                if nt:
                    tb = tie_buf[: 3 * nt].reshape(-1, 3).astype(np.int64)
                    pend.extend(zip(roots[tb[:, 0]].tolist(), roots[tb[:, 1]].tolist(), tb[:, 2].tolist()))
            else:
                x, cnt = moved_counts()
                work_slow += stats.update(x, cnt) + nr
                cand = np.nonzero(stats.stab >= 1)[0]
                order = cand[np.lexsort((cand, -stats.stab[cand]))]
                work_slow += S._sortcost(len(cand))
                spent = 0
                wo = np.zeros(1)
                for j in order:
                    if spent >= b:
                        break
                    a, c = int(stats.a[j]), int(stats.b[j])
                    key = (min(a, c), max(a, c))
                    if key in pair_probed:
                        continue
                    pair_probed.add(key)
                    res = L.sl_pair_probe(ph, a, c, int(pol["pb"]), wo)
                    spent += int(wo[0]) + 1
                    probes += 1
                    if res in (1, 2):
                        pend.append((int(roots[a]), int(roots[c]), 1 if res == 1 else 0))
                work_slow += spent
        if stuck and not pend:  # the slow loop alone: nothing left to prove
            break
        if len(pend) < max(1, int(math.ceil(pol["rb"] * nr))) and not stuck:
            continue
        # ---- rebuild on the proven ties
        rebuilds += 1
        if rebuilds == 1:
            flips_first = flips
        x_cur = F.values(nr, len(ks))
        xr = np.zeros(n0, np.uint8)
        xr[roots] = x_cur
        xo = (xr[ties.root] ^ ties.rpar).astype(np.uint8)
        mcur = len(ks)
        prb = np.zeros(max(1, mcur), np.uint8)
        L.fl_get(ph, np.zeros(nr, np.uint8), np.zeros(nr, np.int64), np.zeros(2, np.uint64), None,
                 np.zeros(max(1, mcur), np.int32), prb)
        if mcur:
            newk = S.sig_keys(*_canon(kv[prb[:mcur] == 1].astype(np.int64), ks[prb[:mcur] == 1]), n0) \
                if prb[:mcur].any() else np.zeros(0, np.int64)
            work_rebuild += S._sortcost(len(probed_keys) + len(newk)) + mcur
            probed_keys = np.union1d(probed_keys, newk)
        kv_old, ks_old, roots_old = kv, ks, roots
        st_old = F.h.state() if fast == "agent" else None
        roots, kv, ks, w = S.reduce_pattern(inst.knots, [], ties, np.array(pend, np.int32).reshape(-1, 3))
        pend = []
        work_rebuild += w + n0 + S._sortcost(inst.m) + S._sortcost(n0) + len(kv)
        idx = np.full(n0, -1, np.int64)
        idx[roots] = np.arange(len(roots))
        kvn = idx[kv].astype(np.int32)
        imp = xo ^ ties.rpar
        vote = np.bincount(ties.root, weights=imp, minlength=n0)
        size = np.bincount(ties.root, minlength=n0)
        xr2 = np.where(2 * vote > size, 1, np.where(2 * vote < size, 0, xo)).astype(np.uint8)
        x_new = xr2[roots]
        work_rebuild += 4 * n0
        n_new, m_new = len(roots), len(kv)
        if m_new == 0:  # every knot always holds now: any state of the classes is a solution
            F_final = x_new
            solved = True
            if fast == "agent":
                F.h.close()
            break
        if fast == "none":
            F.x = x_new
        elif fast == "agent":
            cls = idx[ties.root[roots_old]]
            par = ties.rpar[roots_old].astype(np.uint8)
            dist_from = [[] for _ in range(n_new)]
            for j, c in enumerate(cls):
                dist_from[int(c)].append(j)
            keys_new = S.sig_keys(kv, ks, n0)
            pos = {int(k): i for i, k in enumerate(keys_new)}
            rv = ties.root[kv_old.astype(np.int64)]
            rs = (ks_old ^ ties.rpar[kv_old.astype(np.int64)]).astype(np.uint8)
            keep = (rv[:, 0] != rv[:, 1]) & (rv[:, 0] != rv[:, 2]) & (rv[:, 1] != rv[:, 2])
            knot_from = [[] for _ in range(m_new)]
            if keep.any():
                cv, cs = _canon(rv[keep], rs[keep])
                ko = S.sig_keys(cv, cs, n0)
                for k_old, key in zip(np.nonzero(keep)[0], ko):
                    i = pos.get(int(key))
                    if i is not None:
                        knot_from[i].append(int(k_old))
            work_rebuild += len(roots_old) + len(kv_old) + S._sortcost(len(kv_old) + m_new)
            ainst = AE.Instance(n_new, kvn, signs=ks)
            F.h.close()
            if memory == "carry":
                st2 = AH.carry(st_old, n_new, m_new, dist_from, par, knot_from, x_new=x_new)
                F.h = AH.AgentHandle(ainst, "policy", (), theta, flags, seed, state=st2)
            else:
                F.h = AH.AgentHandle(ainst, "policy", (), theta, flags, S.run_seed("restart", seed, rebuilds), x0=x_new)
            work_rebuild += 3 * m_new
        else:
            xs_old, lf_old, rngst, t, _ = M._state(F.h, len(roots_old), len(ks_old))
            lfr = np.full(n0, -1, np.int64)
            lfr[roots_old] = lf_old
            S.lib().fl_free(F.h)
            F.h, w1 = S._handle(n_new, kvn, ks, x_new, lfr[roots], rngst, S.run_seed("slow", seed, rebuilds), t, None)
            S.lib().fl_set_sortlog(F.h, 1)
            work_rebuild += w1
        L.fl_free(ph)
        pr = np.isin(S.sig_keys(kv, ks, n0), probed_keys).astype(np.uint8) if len(probed_keys) else None
        ph, w2 = S._handle(n_new, kvn, ks, np.zeros(n_new, np.uint8), np.full(n_new, -1, np.int64),
                           np.zeros(2, np.uint64), S.run_seed("probe", seed, rebuilds), 0, pr)
        L.fl_set_sortlog(ph, 1)
        work_rebuild += w2 + (S._sortcost(len(kv) + len(probed_keys)) if len(probed_keys) else 0)
        if target == "coflip":
            x, cnt = moved_counts()
            stats = M.Stats(kvn.astype(np.int64), x, cnt)
            pair_probed = set()
    # map back and check on the original knots
    if solved and "F_final" in locals():
        x_cur = F_final
    else:
        x_cur = F.values(len(roots), len(ks))
        if fast == "agent":
            F.h.close()
        elif fast != "none":
            S.lib().fl_free(F.h)
    L.fl_free(ph)
    xr = np.zeros(n0, np.uint8)
    xr[roots] = x_cur
    xo = (xr[ties.root] ^ ties.rpar).astype(np.uint8)
    ok = inst.satisfied(xo) if solved else None
    work = work_fast + work_slow + work_rebuild
    res = {"flips": flips, "solved": solved, "verified": ok, "work": work, "work_fast": work_fast, "work_slow": work_slow,
           "work_rebuild": work_rebuild, "cpu": time.thread_time() - c0, "cpu_fast": cpu_fast, "epochs": epochs,
           "rebuilds": rebuilds, "probes": probes, "n_final": int(len(roots)), "m_final": int(len(kv)),
           "flips_first": flips_first}
    if debug:
        res["state"] = xo
        res["root"], res["rpar"] = ties.root.copy(), ties.rpar.copy()
    return res


def run_agent_alone(inst: S.Instance, seed: int, cap: int, theta, flags: int) -> dict:
    """Dr alone, in its own engine, from the same initial state as every arm (the engine draws it from the seed)."""
    c0 = time.thread_time()
    r = AE.run(AE.Instance(inst.n, inst.knots), "policy", (), theta=theta, flags=flags, seed=seed, max_flips=cap,
               want_state=True)
    ok = inst.satisfied(r["state"].astype(np.uint8)) if r["solved"] else None
    return {"flips": r["flips"], "solved": r["solved"], "verified": ok, "work": r["work"], "work_fast": r["work"],
            "work_slow": 0, "work_rebuild": 0, "cpu": time.thread_time() - c0, "cpu_fast": r["cpu"], "rebuilds": 0}
