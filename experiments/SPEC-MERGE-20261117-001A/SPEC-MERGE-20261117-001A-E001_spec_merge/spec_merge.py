"""Speculative merges from the fast loop's own co-flip evidence (SPEC-MERGE-20261117-001A).

The fast loop is Novelty+ on the knot pattern, in epochs. After each epoch the slow loop updates, for every co-knotted pair
(p, q) of the current pattern, a stability count: it grows by one when both p and q flipped during the epoch and their relative
value x_p ^ x_q is what it was at the end of the last epoch, and it returns to 0 when the relative value changed. A pair with a
high count is one the search keeps moving together.

The co-flip rule merges the most stable pairs speculatively, without proof, at their current relative value. The
random-pair control merges as many pairs drawn uniformly among those that both flipped in the last epoch, so that it merges
where the search is active, as the co-flip rule does, without its evidence. The search then runs on the coarser pattern.

These merges do NOT keep the allowed states. A wrong merge can leave the coarser pattern with no allowed state at all, and the
search then stalls. The slow loop acts only when the search is stuck (no new least violated count for `patience` epochs):
- if its latest round of merges has not taken the least violated count below where the search was stuck before that round,
  it undoes the round (the counts are read on different patterns, so this is a heuristic, charged nothing extra);
- otherwise it merges a new round of the most stable pairs.
A round whose merges contradict each other, or force a knot into a contradiction, is undone at once. Every state the loop reports is mapped back and checked on
the original knots. A state of the coarser pattern maps to one that satisfies every original knot, since the merged classes
only fix relative values, so a reported solution is a solution of the original pattern.

The hidden planted state is never read by the loop. `gate_d` and the diagnostics read it only after the fact.
"""
from __future__ import annotations

import math
import time

import numpy as np

import slow_loop as S

PAIRS = np.array([[0, 1], [0, 2], [1, 2]])


def _pair_arrays(kvn: np.ndarray):
    """The three co-knotted pairs of every knot of the current pattern, as two arrays of current ids."""
    if len(kvn) == 0:
        return np.zeros(0, np.int64), np.zeros(0, np.int64)
    a = kvn[:, PAIRS[:, 0]].reshape(-1).astype(np.int64)
    b = kvn[:, PAIRS[:, 1]].reshape(-1).astype(np.int64)
    return a, b


class Stats:
    """Stability counts of the co-knotted pairs of one pattern; charged 4 reads per pair (the two flip parities and the two
    moved flags) and 2 per distinction per update."""

    def __init__(self, kvn: np.ndarray, x: np.ndarray, nflip: np.ndarray):
        self.a, self.b = _pair_arrays(kvn)
        self.rel = (x[self.a] ^ x[self.b]).astype(np.uint8)
        self.snap = nflip.copy()
        self.stab = np.zeros(len(self.a), np.int32)
        self.both = np.zeros(len(self.a), bool)

    def update(self, x: np.ndarray, nflip: np.ndarray) -> int:
        rel = (x[self.a] ^ x[self.b]).astype(np.uint8)
        both = (nflip[self.a] > self.snap[self.a]) & (nflip[self.b] > self.snap[self.b])
        self.stab = np.where(rel != self.rel, 0, np.where(both, self.stab + 1, self.stab)).astype(np.int32)
        self.both = both
        self.rel = rel
        self.snap = nflip.copy()
        return 4 * len(self.a) + 2 * len(x)


def _state(h, n, m):
    x = np.zeros(n, np.uint8)
    lf = np.zeros(n, np.int64)
    r = np.zeros(2, np.uint64)
    import ctypes
    t = ctypes.c_int64(0)
    S.lib().fl_get(h, x, lf, r, ctypes.byref(t), np.zeros(max(1, m), np.int32), np.zeros(max(1, m), np.uint8))
    nf = np.zeros(n, np.int32)
    S.lib().fl_get_flips(h, nf)
    return x, lf, r, int(t.value), nf


def _select(stats: Stats, x, n_cur, pol, rng, mode):
    """Pairs to merge in this round: (current a, current b, parity), at most mu * n_cur of them, distinct."""
    cand = np.nonzero(stats.stab >= pol["s"])[0]
    k = min(len(cand), int(math.ceil(pol["mu"] * n_cur)))
    if k == 0:
        return np.zeros((0, 3), np.int64), S._sortcost(len(cand))
    if mode == "coflip":
        order = cand[np.lexsort((cand, -stats.stab[cand]))]
    else:  # the same number of pairs, drawn uniformly among the co-knotted pairs that both flipped in the last epoch
        active = np.nonzero(stats.both)[0]
        order = active[rng.permutation(len(active))]
    a, b = stats.a[order], stats.b[order]
    lo, hi = np.minimum(a, b), np.maximum(a, b)
    _, first = np.unique(lo * (n_cur + 1) + hi, return_index=True)
    keep = np.sort(first)[:k]
    sel = order[keep]
    par = (x[stats.a[sel]] ^ x[stats.b[sel]]).astype(np.int64)
    return np.stack([stats.a[sel], stats.b[sel], par], axis=1), S._sortcost(len(order)) + len(order)


def run_spec(inst: S.Instance, params, seed: int, cap: int, pol: dict, mode: str = "coflip", debug: bool = False) -> dict:
    """Novelty+ (params) in epochs of max(100, e * n') flips with speculative merges and un-merges; charge v2."""
    c0 = time.thread_time()
    L = S.lib()
    n0 = inst.n
    p = np.zeros(4)
    p[: len(params)] = params
    xr, rngst = S.initial_state(n0, seed)
    lfr = np.full(n0, -1, np.int64)
    rng = np.random.default_rng(S.run_seed("spec", seed))
    rounds: list = []          # each round: an array of ties (original root a, original root b, parity)
    flips = work_fast = work_stats = work_rebuild = 0
    cpu_rebuild = 0.0
    epochs = merges = undos = contra_undos = stall_undos = n_rounds = 0
    merged_ever: list = []
    round_log: list = []       # [the round's ties, kept?]; a round once kept is never undone later
    fl_out = np.zeros(5)

    def build(all_ties: np.ndarray):
        """A fresh tie structure from the active rounds; the coarser pattern; charge v2."""
        nonlocal work_rebuild
        ties = S.Ties(n0)
        roots, kv, ks, w = S.reduce_pattern(inst.knots, [], ties, all_ties.astype(np.int32).reshape(-1, 3))
        idx = np.full(n0, -1, np.int64)
        idx[roots] = np.arange(len(roots))
        kvn = idx[kv].astype(np.int32)
        work_rebuild += w + n0 + S._sortcost(len(inst.knots)) + S._sortcost(n0) + len(kv)
        return ties, roots, kv, ks, kvn

    ties = S.Ties(n0)
    roots, kv, ks, kvn = np.arange(n0), inst.knots.copy(), np.zeros(inst.knots.shape, np.uint8), inst.knots.copy()
    h, w0 = S._handle(n0, kvn, ks, xr, lfr, rngst, S.run_seed("slow", seed), 0, None)
    L.fl_set_sortlog(h, 1)
    work_fast += w0
    t = 0
    x, lf, _, _, nf = _state(h, n0, len(ks))
    stats = Stats(kvn.astype(np.int64), x, nf)
    best = None
    since_best = 0
    pre_best = None
    last_was_merge = False

    def rebuild_to(new_rounds):
        """Rebuild on the active rounds; a merged class takes the majority value of its members' current values."""
        nonlocal h, ties, roots, kv, ks, kvn, xr, lfr, stats, t, work_fast, work_rebuild, cpu_rebuild
        c1 = time.thread_time()
        x, lf, r, t, nf = _state(h, len(roots), len(ks))
        xr[roots] = x
        lfr[roots] = lf
        xo = xr[ties.root] ^ ties.rpar
        all_t = np.concatenate(new_rounds) if new_rounds else np.zeros((0, 3), np.int64)
        L.fl_free(h)
        ties, roots, kv, ks, kvn = build(all_t)
        imp = xo ^ ties.rpar
        vote = np.bincount(ties.root, weights=imp, minlength=n0)
        size = np.bincount(ties.root, minlength=n0)
        xr = np.where(2 * vote > size, 1, np.where(2 * vote < size, 0, xo)).astype(np.uint8)
        work_rebuild += 4 * n0
        h, w1 = S._handle(len(roots), kvn, ks, xr[roots], lfr[roots], r, S.run_seed("slow", seed, epochs), t, None)
        L.fl_set_sortlog(h, 1)
        work_rebuild += w1
        x2, _, _, _, nf2 = _state(h, len(roots), len(ks))
        stats = Stats(kvn.astype(np.int64), x2, nf2)
        cpu_rebuild += time.thread_time() - c1
        return ties.contradiction

    while True:
        nr = len(roots)
        budget = min(cap - flips, max(pol.get("epoch_min", 100), int(round(pol["e"] * nr))))
        L.fl_run(h, 4, p, int(budget), fl_out)
        flips += int(fl_out[0])
        work_fast += int(fl_out[3])
        work_stats += int(fl_out[0])  # the flip counter
        epochs += 1
        if fl_out[1] or flips >= cap:
            break
        mv = int(fl_out[2])
        if best is None or mv < best:
            best, since_best = mv, 0
        else:
            since_best += 1
        x, _, _, _, nf = _state(h, nr, len(ks))
        work_stats += stats.update(x, nf) + nr
        # the slow loop acts only when the search is stuck: no new least violated count for `patience` epochs
        if since_best < pol["patience"] or epochs < pol["warmup"]:
            continue
        if rounds and last_was_merge and (pre_best is None or best >= pre_best):
            # the latest merges did not take the search below where it was stuck before them: undo them
            rounds.pop()
            undos += 1
            stall_undos += 1
            round_log[-1][1] = False
            rebuild_to(rounds)
            last_was_merge = False
        elif n_rounds < pol["max_rounds"]:
            sel, wsel = _select(stats, x, nr, pol, rng, mode)
            work_stats += wsel
            if len(sel):
                new = np.stack([roots[sel[:, 0]], roots[sel[:, 1]], sel[:, 2]], axis=1)
                pre_best = best
                rounds.append(new)
                n_rounds += 1
                merges += len(new)
                merged_ever.append(new)
                round_log.append([new, True])
                last_was_merge = True
                if rebuild_to(rounds):  # the merges contradict each other or the knots: undo at once
                    rounds.pop()
                    undos += 1
                    contra_undos += 1
                    round_log[-1][1] = False
                    rebuild_to(rounds)
                    last_was_merge = False
        else:
            last_was_merge = False
        best, since_best = None, 0
    xs = np.zeros(len(roots), np.uint8)
    L.fl_get(h, xs, np.zeros(len(roots), np.int64), np.zeros(2, np.uint64), None, np.zeros(max(1, len(ks)), np.int32),
             np.zeros(max(1, len(ks)), np.uint8))
    L.fl_free(h)
    xr[roots] = xs
    xo = (xr[ties.root] ^ ties.rpar).astype(np.uint8)
    solved = bool(fl_out[1])
    ok = inst.satisfied(xo) if solved else None
    work = work_fast + work_stats + work_rebuild
    res = {"flips": flips, "solved": solved, "verified": ok, "work_fast": work_fast, "work_slow": work_stats,
           "work_rebuild": work_rebuild, "work": work, "cpu": time.thread_time() - c0, "cpu_rebuild": cpu_rebuild,
           "minviol": best if best is not None else -1, "epochs": epochs, "rounds": n_rounds, "merges": merges,
           "undos": undos, "stall_undos": stall_undos, "contra_undos": contra_undos,
           "active_merges": int(sum(len(r) for r in rounds)), "n_final": int(len(roots)), "contradiction": False}
    if inst.hidden is not None:  # diagnostics only, after the run
        hid = inst.hidden.astype(np.int64)
        # each round: did all its merges agree with the planted state, and was it kept or undone
        res["round_log"] = [[int(np.all((hid[r[:, 0]] ^ hid[r[:, 1]]) == r[:, 2])), int(kept)] for r, kept in round_log]
        if merged_ever:
            allm = np.concatenate(merged_ever)
            res["precision_all"] = float(np.mean((hid[allm[:, 0]] ^ hid[allm[:, 1]]) == allm[:, 2]))
        if rounds:
            act = np.concatenate(rounds)
            res["precision_active"] = float(np.mean((hid[act[:, 0]] ^ hid[act[:, 1]]) == act[:, 2]))
    if debug:
        res["state"] = xo
    return res


def gate_d(inst: S.Instance, params, seed: int, checkpoints=(4, 8, 16), frac: float = 0.01, s_min: int = 1,
           probe: bool = False, pb: int = 4000, found_cap: int = 10**8) -> dict:
    """Gate D on one run: Novelty+ alone in epochs of n flips. At each checkpoint, the k = frac * n most stable co-knotted
    pairs (stability >= s_min) against k uniformly drawn co-knotted pairs, by agreement of their current relative value with
    the planted one (complement-invariant) and, with probe=True, by the share tied by a pair probe."""
    L = S.lib()
    n = inst.n
    p = np.zeros(4)
    p[: len(params)] = params
    x0, r = S.initial_state(n, seed)
    h, _ = S._handle(n, inst.knots, np.zeros(inst.knots.shape, np.uint8), x0, np.full(n, -1, np.int64), r, 1, 0)
    rng = np.random.default_rng(S.run_seed("gate", seed))
    hid = inst.hidden.astype(np.int64)
    x, _, _, _, nf = _state(h, n, inst.m)
    st = Stats(inst.knots.astype(np.int64), x, nf)
    out = {"checkpoints": {}}
    fl = np.zeros(5)
    kept_pairs = {}
    for ep in range(1, max(checkpoints) + 1):
        L.fl_run(h, 4, p, n, fl)
        if fl[1]:
            out["solved_at_epoch"] = ep
            break
        x, _, _, _, nf = _state(h, n, inst.m)
        st.update(x, nf)
        if ep in checkpoints:
            k = max(1, int(frac * n))
            cand = np.nonzero(st.stab >= s_min)[0]
            top = cand[np.lexsort((cand, -st.stab[cand]))][:k]
            ran = rng.choice(len(st.a), size=k, replace=False)
            row = {"k": int(k), "candidates": int(len(cand))}
            for name, sel in (("coflip", top), ("random", ran)):
                if len(sel) == 0:
                    row[name] = None
                    continue
                a, b = st.a[sel], st.b[sel]
                cur = x[a] ^ x[b]
                row[name] = {"pairs": int(len(sel)), "agree_planted": float(np.mean(cur == (hid[a] ^ hid[b]))),
                             "median_stab": float(np.median(st.stab[sel]))}
                kept_pairs[(ep, name)] = (a.copy(), b.copy(), cur.copy())
                if probe:
                    tied = 0
                    wo = np.zeros(1)
                    for aa, bb in zip(a, b):
                        tied += L.sl_pair_probe(h, int(aa), int(bb), int(pb), wo) != 0
                    row[name]["tied_share"] = tied / len(sel)
            row["state_agree_planted"] = float(max(np.mean(x == hid), np.mean(x != hid)))
            out["checkpoints"][ep] = row
    if not fl[1]:  # run on to a solution, and read every checkpoint's pairs against the solution this run found
        S.lib().fl_run(h, 4, p, int(found_cap), fl)
    if fl[1]:
        xf, _, _, _, _ = _state(h, n, inst.m)
        for (ep, name), (a, b, cur) in kept_pairs.items():
            out["checkpoints"][ep][name]["agree_found"] = float(np.mean(cur == (xf[a] ^ xf[b])))
    S.lib().fl_free(h)
    return out
