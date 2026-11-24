"""Arm 2: one added knot (REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C, "Arm 2, one added knot", "Classes of T",
"The known shape").

For each two-holder start with no hidden excess at stage 0 (ticket B's record): for every set T of 2, 3 or 4 of the
start's distinctions, one not-all-equal knot on T and one fresh distinction.  It counts an old word twice when T is not
all equal in it and once when it is, so the new table of old observer words is 2*M - M_T, where M is the start's table
and M_T counts the old words with T all equal.  M and every M_T are computed exactly from the start's allowed words
(enumerated by joining its knots; M is checked against ticket B's contraction on every start).  No growth is run.

Each T is classed: by the number of shared distinctions in it (0, 1, 2 or more); by its relation to the observers (inside
one observer's three distinctions; observer distinctions of one side only and others; observer distinctions of both
sides; none); by origin (some round-1 birth under ordinary growth takes exactly T; some round-1 birth under rule R takes
exactly T for some allowed choice, every choice when there are at most 4,096, else not decided).  Beside the frozen
ordinary origin (the recorded wrapper's placement of loose distinctions) a supplementary origin is recorded: some
placement of the parents' loose distinctions gives a round-1 birth that takes T.

One JSON line per start (counts by class, and every gain) to arm2_<lo>-<hi>.jsonl.gz.
usage (repo root): timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file> --lo A --hi B
"""
import argparse
import itertools
import json
import sys
import time
from collections import Counter
from fractions import Fraction
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cstudy as cs  # noqa: E402

bc = cs.bc
OBS_CLASSES = ('inside_one_observer', 'one_side_and_others', 'both_sides', 'none')
TABLE_CAP = 50


def population():
    S = cs.starts()
    B = cs.b_lines('c3')
    return [i for i in range(len(S)) if cs.start_class(S[i]) == 'two' and not B[i]['stage0_excess']]


def mask_of(ds):
    m = 0
    for d in ds:
        m |= 1 << d
    return m


def origins(si, stars):
    """(ordinary input sets (masks) of round-1 births with two or more parents; the same under any placement of loose
    distinctions; R input sets or None when not decided; record)."""
    Bl = cs.b_lines('c3')[si]
    rec = {}
    ordinary, anyplace = set(), set()
    if Bl['outcome'] != 'stall':
        h = bc.grow(stars, 'nae', rounds=1, dmax=10 ** 9)   # round 1 as the recorded wrapper makes it (no size stop)
        rec['ordinary_outcome'] = h['outcome']
        if h['births']:
            # loose distinctions of each knot, in its order
            counts = Counter(d for s in stars for d in s)
            loose = {k: [d for d in s if counts[d] == 1] for k, s in enumerate(stars)}
            for parents, inputs, made in h['births'][0]:
                if len(parents) >= 2:
                    ordinary.add(mask_of(inputs))
                    for combo in itertools.product(*[loose[p] for p in parents]):
                        anyplace.add(mask_of(combo))
            rec['ordinary_births'] = len(h['births'][0])
    else:
        rec['ordinary_outcome'] = 'stall'
    r, per, total, g = cs.round1_options(stars)
    rec['R_choices'] = total
    if r.status == 'closed':
        Rset = set()
        rec['R_status'] = 'closed'
    elif per is None:
        Rset = {mask_of(row) for row, ps in zip(r.inputs, r.parents) if len(ps) >= 2}
        rec['R_status'] = 'no short knot'
        assert Rset == ordinary, 'rule R and ordinary growth differ on a round with no short knot'
    elif total > cs.ORIGIN_CAP:
        Rset = None
        rec['R_status'] = 'not decided'
    else:
        Rset = set()
        rec['R_status'] = 'short'
        for ix in cs.all_choice_indices(per):
            ch = cs.choice_from_index(per, ix)
            for row, ps in zip(cs.round1_input_sets(g, r, ch), r.parents):
                if len(ps) >= 2:
                    Rset.add(mask_of(row))
    return ordinary, anyplace, Rset, rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lo', type=int, required=True)
    ap.add_argument('--hi', type=int, required=True)
    ap.add_argument('--tag', default='')
    args = ap.parse_args()
    t0 = time.time()
    assert cs.rlaw_sha() == cs.RLAW_SHA, 'rlaw.py differs from the engine at the freeze'
    S = cs.starts()
    pop = population()
    ev = bc.Evaluator()
    lines = []
    tot = Counter()
    for pos in range(args.lo, min(args.hi, len(pop))):
        si = pop[pos]
        s = S[si]
        stars, laws, names, obs = cs.start_struct(si)
        nf = len(stars)
        D = len(names)
        holders = Counter(d for st in stars for d in st)
        shared = [holders[d] >= 2 for d in range(D)]
        assert max(holders.values()) <= 2
        words = cs.allowed_words(stars, laws)
        oi = cs.obs_index(words, obs)
        M = np.bincount(oi, minlength=64).astype(np.int64)
        T0 = bc.stage_tables(stars, laws, nf, nf, np.zeros((1, 0), np.int8), obs, choices=cs.CH3)[0]
        assert np.array_equal(M, np.array([int(v) for v in T0], dtype=np.int64)), 'allowed words disagree with B'
        N = len(words)
        assert 2 * N < (1 << 24)
        order = np.argsort(oi, kind='stable')
        ws, os_ = words[order], oi[order]
        present, bounds = np.unique(os_, return_index=True)
        ordinary, anyplace, Rset, orec = origins(si, stars)
        aset, bset = set(obs[:3]), set(obs[3:])
        Tlist = [T for k in (2, 3, 4) for T in itertools.combinations(range(D), k)]
        tm = np.array([mask_of(T) for T in Tlist], dtype=np.int64)
        tables = np.empty((len(Tlist), 64), dtype=np.int64)
        B = max(16, (1 << 23) // max(N, 1))
        for lo in range(0, len(Tlist), B):
            t = tm[lo:lo + B]
            a = ws[:, None] & t[None, :]
            eq = (a == 0) | (a == t[None, :])
            red = np.add.reduceat(eq, bounds, axis=0, dtype=np.int64)        # (len(present), b)
            MT = np.zeros((len(t), 64), dtype=np.int64)
            MT[:, present] = red.T
            tables[lo:lo + B] = 2 * M[None, :] - MT
        sup_ok = bool(((tables > 0) == (M[None, :] > 0)).all())
        hA, hB = bc.hidden_batch(tables.reshape(-1, 8, 8))
        hid = hA & hB
        exact = [None] * len(Tlist)
        fsc = np.full(len(Tlist), np.nan)
        hidx = np.nonzero(hid)[0]
        if len(hidx):
            U, inv = np.unique(tables[hidx], axis=0, return_inverse=True)
            inv = inv.reshape(-1)
            evs = ev.run([bc.normalize(u) for u in U])
            for j, i in enumerate(hidx):
                e = evs[inv[j]]
                assert e[0] and e[1]
                fsc[i] = e[2]
                exact[i] = e[3]
        counts = Counter()
        gains = []
        best_f = float(np.nanmax(fsc)) if len(hidx) else None
        for i, T in enumerate(Tlist):
            nsh = sum(shared[d] for d in T)
            sh_cls = '0' if nsh == 0 else ('1' if nsh == 1 else '2+')
            ts = set(T)
            if ts <= aset or ts <= bset:
                oc = 'inside_one_observer'
            elif ts & aset and ts & bset:
                oc = 'both_sides'
            elif ts & aset or ts & bset:
                oc = 'one_side_and_others'
            else:
                oc = 'none'
            m = int(tm[i])
            o_ord = m in ordinary
            o_any = m in anyplace
            o_R = None if Rset is None else (m in Rset)
            gain = bool(hid[i] and exact[i] is not None and exact[i] > 2)
            key = (len(T), sh_cls, oc, int(o_ord), (-1 if o_R is None else int(o_R)), int(o_any))
            c = counts.setdefault(key, [0, 0, 0])
            c[0] += 1
            c[1] += bool(hid[i])
            c[2] += gain
            if gain:
                loose_obs = [d for d in T if not shared[d] and d in obs]
                known = len(T) == 4 and nsh == 3 and len(loose_obs) == 1
                g = dict(T=[names[d] for d in T], size=len(T), shared=nsh, shared_names=[names[d] for d in T if shared[d]],
                         obs_class=oc, origin_ordinary=o_ord, origin_anyplace=o_any, origin_R=o_R,
                         known_shape=known, score=str(exact[i]), score_float=float(fsc[i]))
                if len(gains) < TABLE_CAP:
                    g['table'] = [int(v) for v in tables[i]]
                gains.append(g)
        line = dict(pos=pos, si=si, tid=s['tid'], mask=s['mask'], knots=nf, D=D, N=int(N),
                    loose=[names[d] for d in range(D) if not shared[d]], shared=[names[d] for d in range(D) if shared[d]],
                    start_knots=cs.knots_text(stars, laws, names), M=[int(v) for v in M],
                    stalled=cs.b_lines('c3')[si]['outcome'] == 'stall', sets=len(Tlist), hidden=int(hid.sum()),
                    support_unchanged=sup_ok, best_hidden_float=best_f, origin=orec,
                    n_ordinary=len(ordinary), n_anyplace=len(anyplace), n_R=(None if Rset is None else len(Rset)),
                    counts=[list(k) + v for k, v in sorted(counts.items(), key=str)], gains=gains, n_gains=len(gains))
        lines.append(line)
        tot['sets'] += len(Tlist)
        tot['gains'] += len(gains)
        tot['hidden'] += int(hid.sum())
    tag = args.tag or 'all'
    cs.dump(cs.ART / f'arm2_{tag}_{args.lo:05d}-{args.hi:05d}.jsonl.gz', lines)
    print(json.dumps(dict(lo=args.lo, hi=args.hi, starts=len(lines), sets=tot['sets'], hidden=tot['hidden'],
                          gains=tot['gains'], exact_calls=ev.exact_calls, seconds=round(time.time() - t0, 1))))


if __name__ == '__main__':
    main()
