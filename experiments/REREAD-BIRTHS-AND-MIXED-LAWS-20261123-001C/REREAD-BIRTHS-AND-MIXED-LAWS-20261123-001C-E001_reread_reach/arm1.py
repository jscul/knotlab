"""Arm 1: growth under rule R on the stalled starts (REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C, "Arm 1", "Paying
birth", "Gain through a payment").

For each start that stalls at round 1 under ordinary growth (ticket B's record), in the class asked (two-holder or
three-holder): growth under rule R by ticket A's engine on full holdings, structure rule not-all-equal (a fresh
distinction for every birth), 3 rounds or until a stage passes 20 distinctions, under conventions O and N.  A
two-holder start is also grown under every allowed round-1 payment choice when there are at most 64, otherwise under 62
more drawn by seed 2026112350 (later rounds by convention O, and also by N when a later round has a short knot).  Every
newborn is even parity, odd parity or not-all-equal: every assignment when 3^n <= 4,096, otherwise 4,096 drawn by seed
2026112351, one generator per history.  At every stage and for every assignment (restricted to the newborns of that
stage) the table of allowed words on the target's six observer distinctions is computed exactly and tested for a hidden
excess; a gain is a hidden excess at a later stage of a start with none at stage 0; for every gain the same stage with
every paying birth changed to even parity is tested (gain through a payment).

Exact reduction used for speed (checked in gates.py against direct contraction): at stage t a newborn of round t holds
fresh distinctions that nothing else holds, so its factor summed over them is a constant unless it is not-all-equal with
two or more parents (then it counts an old word 2^f - [inputs all equal] times).  Tables are therefore computed once per
"effective" assignment (round-t newborns: one-parent -> even, parity -> even, not-all-equal with two or more parents ->
not-all-equal; earlier newborns as assigned) and every assignment takes the table (up to a constant) of its class.  Every
gain is recomputed by direct contraction with its actual assignment.

One JSON line per history to arm1_<cls>_<lo>-<hi>.jsonl.gz; every gain (at most 50 per stage and history in full, all
counted) to arm1_gains_<cls>_<lo>-<hi>.jsonl.gz.
usage (repo root): timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file> --cls two|three --lo A --hi B
"""
import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cstudy as cs  # noqa: E402

bc = cs.bc
KIND_CODE = {'O': 0, 'N': 1, 'choice': 2, 'choiceN': 3}
HIT_CAP = 50


def stalled_list(cls):
    S = cs.starts()
    B = cs.b_lines('c3')
    return [i for i in range(len(S)) if B[i]['outcome'] == 'stall' and cs.start_class(S[i]) == cls]


def histories_of(si, cls):
    """The histories of one stalled start: [(kind, j, choice or None, history dict)], and the choice record."""
    s = cs.starts()[si]
    stars, laws, names, obs = cs.start_struct(si)
    hs = [('O', 0, None, cs.grow_R(stars, 'O')), ('N', 0, None, cs.grow_R(stars, 'N'))]
    crec = None
    if cls == 'two':
        r, per, total, g = cs.round1_options(stars)
        assert per is not None, 'a stalled start with no short knot under R'
        cO = cs.convention_choice(stars, 'O')
        cN = cs.convention_choice(stars, 'N')
        iO = None if cO is None else cs.index_of_choice(per, cO)
        iN = None if cN is None else cs.index_of_choice(per, cN)
        assert (cO is None or iO is not None) and (cN is None or iN is not None), 'a convention choice is not allowed'
        if total == 0:
            idx, mode = [], 'none'
        elif total <= cs.CHOICE_CAP:
            idx, mode = cs.all_choice_indices(per), 'all'
        else:
            idx = cs.drawn_choice_indices(per, s['tid'], s['mask'], [i for i in (iO, iN) if i is not None])
            mode = 'drawn'
        crec = dict(total=total, mode=mode, per_knot=[len(o) for _, o in per], index_O=iO, index_N=iN,
                    shortages=[list(x) for x in r.shortages])
        for j, ix in enumerate(idx):
            ch = cs.choice_from_index(per, ix)
            h = cs.grow_R(stars, 'O', first_choice=ch, conv_later='O')
            hs.append(('choice', j, list(ix), h))
            if any(len(x) for x in h['short'][1:]):
                h2 = cs.grow_R(stars, 'O', first_choice=ch, conv_later='N')
                if h2['stars'] != h['stars'] or h2['n_at'] != h['n_at']:
                    hs.append(('choiceN', j, list(ix), h2))
    return hs, crec, (stars, laws, names, obs)


def effective_rows(R, nb_prev, multi_cols):
    """R: unique prefix rows (B, nb) at a stage whose round-t newborns are columns nb_prev..nb-1.  Returns (E, inv):
    effective rows (unique) and for each row of R the index of its effective row."""
    E = R.copy()
    if R.shape[1] > nb_prev:
        cols = np.arange(nb_prev, R.shape[1])
        for j in cols:
            if j in multi_cols:
                E[:, j] = np.where(R[:, j] == 2, 2, 0)
            else:
                E[:, j] = 0
    if E.shape[1] == 0:
        return E[:1], np.zeros(len(R), dtype=np.int64)
    U, inv = np.unique(E, axis=0, return_inverse=True)
    return U, inv.reshape(-1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cls', required=True, choices=('two', 'three'))
    ap.add_argument('--lo', type=int, required=True)
    ap.add_argument('--hi', type=int, required=True)
    ap.add_argument('--tag', default='')
    args = ap.parse_args()
    t0 = time.time()
    assert cs.rlaw_sha() == cs.RLAW_SHA, 'rlaw.py differs from the engine at the freeze'
    S = cs.starts()
    B = cs.b_lines('c3')
    lst = stalled_list(args.cls)
    ev = cs.Eval()
    lines, gains_out = [], []
    totals = Counter()
    for pos in range(args.lo, min(args.hi, len(lst))):
        si = lst[pos]
        s = S[si]
        hs, crec, (stars, laws, names, obs) = histories_of(si, args.cls)
        nf = len(stars)
        T0 = bc.stage_tables(stars, laws, nf, nf, np.zeros((1, 0), np.int8), obs, choices=cs.CH3)
        e0 = ev.run(T0)[0]
        stage0_excess = bool(cs.is_excess(e0))
        assert stage0_excess == bool(B[si]['stage0_excess']), 'stage 0 differs from ticket B'
        sup0 = cs.support(T0[0])
        cache = {}   # (stage knots, effective row bytes) -> (normalized table, eval)
        for kind, j, ix, h in hs:
            st = h['stars']
            n_new = h['n_at'][-1] - nf
            A, lmode = cs.assignments3(n_new, (s['tid'], s['mask'], KIND_CODE[kind], j))
            # round of each newborn and whether it has two or more parents
            multi = []
            for rd in h['births']:
                for b in rd:
                    multi.append(len(b['parents']) >= 2)
            paying_cols = [k for k, b in enumerate(b for rd in h['births'] for b in rd) if b['paying']]
            rec = dict(pos=pos, si=si, tid=s['tid'], mask=s['mask'], cls=args.cls, kind=kind, j=j, choice=ix,
                       choice_mode=(None if crec is None else crec['mode']), n_at=h['n_at'], D_at=h['D_at'],
                       outcome=h['outcome'], residual=h['residual'], residual_round=h['residual_round'],
                       short=[len(x) for x in h['short']], max_holders=h['max_holders'],
                       births=[[len(rd), sum(len(b['parents']) >= 2 for b in rd), sum(b['paying'] for b in rd),
                                sum(sum(b['paid']) for b in rd)] for rd in h['births']],
                       newborns=n_new, assignments=int(A.shape[0]), law_mode=lmode, stage0_excess=stage0_excess,
                       stage0_eval=[e0[0], e0[1], e0[2], cs.frac(e0[3])], stages=[])
            if kind == 'O' and crec is not None:
                rec['choice_record'] = crec
            prev_sup_of_row = None
            nb_prev = 0
            for t, n in enumerate(h['n_at']):
                nb = n - nf
                if t == 0:
                    rec['stages'].append(dict(t=0, D=h['D_at'][0], knots=n, tables=1, hidden=int(e0[0] and e0[1]),
                                              excess=int(stage0_excess), gains=0, gains_pay=0,
                                              best_hidden_exact=cs.frac(e0[3]),
                                              best_hidden_float=(e0[2] if e0[0] and e0[1] else None),
                                              support_changes=0))
                    prev_sup_of_row = {b''.join([]): sup0}
                    nb_prev = 0
                    continue
                R = np.unique(A[:, :nb], axis=0)
                multi_cols = {k for k in range(nb_prev, nb) if multi[k]}
                E, inv = effective_rows(R, nb_prev, multi_cols)
                key_st = tuple(st[:n])
                todo = [i for i in range(len(E)) if (key_st, E[i].tobytes()) not in cache]
                if todo:
                    Tn = bc.stage_tables(st, laws, nf, n, E[todo], obs, choices=cs.CH3)
                    evs = ev.run(Tn)
                    for i, row, e in zip(todo, Tn, evs):
                        cache[(key_st, E[i].tobytes())] = (cs.support(row), e)
                ent = [cache[(key_st, E[i].tobytes())] for i in range(len(E))]
                hid = np.array([bool(ent[inv[i]][1][0] and ent[inv[i]][1][1]) for i in range(len(R))])
                exc = np.array([bool(cs.is_excess(ent[inv[i]][1])) for i in range(len(R))])
                # allowed observer words: compare with the same assignment one stage before
                changes = 0
                cur = {}
                for i in range(len(R)):
                    sp = ent[inv[i]][0]
                    cur[R[i].tobytes()] = sp
                    if prev_sup_of_row is not None:
                        ps = prev_sup_of_row[R[i, :nb_prev].tobytes()]
                        changes += ps != sp
                prev_sup_of_row = cur
                best = max([ent[k][1][3] for k in range(len(ent)) if ent[k][1][3] is not None and ent[k][1][0]
                            and ent[k][1][1]], default=None)
                best_f = max([ent[k][1][2] for k in range(len(ent)) if ent[k][1][2] is not None and ent[k][1][0]
                              and ent[k][1][1]], default=None)
                gains = np.nonzero(exc)[0] if not stage0_excess else np.array([], dtype=np.int64)
                gains_pay = 0
                if len(gains):
                    # direct contraction with the actual assignment, and with every paying birth changed to even
                    Rg = R[gains]
                    Rm = Rg.copy()
                    for k in paying_cols:
                        if k < nb:
                            Rm[:, k] = 0
                    Tg = bc.stage_tables(st, laws, nf, n, Rg, obs, choices=cs.CH3)
                    Tm = bc.stage_tables(st, laws, nf, n, Rm, obs, choices=cs.CH3)
                    eg = ev.run(Tg)
                    em = ev.run(Tm)
                    written = 0
                    for gi in range(len(gains)):
                        assert cs.is_excess(eg[gi]), 'the reduced table and the direct contraction disagree'
                        assert eg[gi][3] == ent[inv[gains[gi]]][1][3]
                        through = not cs.is_excess(em[gi])
                        gains_pay += through
                        if written < HIT_CAP:
                            written += 1
                            laws_all = list(laws) + [cs.CH3[int(v)] for v in Rg[gi]]
                            gains_out.append(dict(
                                pos=pos, si=si, tid=s['tid'], mask=s['mask'], cls=args.cls, kind=kind, j=j, choice=ix,
                                t=t, D=h['D_at'][t], knots_n=n, newborn_laws=[cs.CH3[int(v)] for v in Rg[gi]],
                                knots=cs.knots_text(st[:n], laws_all, names),
                                births=h['births'][:t], paying_cols=[k for k in paying_cols if k < nb],
                                table=[int(v) for v in Tg[gi]],
                                eval=[eg[gi][0], eg[gi][1], eg[gi][2], cs.frac(eg[gi][3])],
                                through_payment=bool(through),
                                even_payers_laws=[cs.CH3[int(v)] for v in Rm[gi]],
                                even_payers_table=[int(v) for v in Tm[gi]],
                                even_payers_eval=[em[gi][0], em[gi][1], em[gi][2], cs.frac(em[gi][3])],
                                law_mode=lmode, choice_mode=rec['choice_mode']))
                rec['stages'].append(dict(t=t, D=h['D_at'][t], knots=n, tables=int(len(R)), effective=int(len(E)),
                                          hidden=int(hid.sum()), excess=int(exc.sum()), gains=int(len(gains)),
                                          gains_pay=int(gains_pay), best_hidden_exact=cs.frac(best),
                                          best_hidden_float=best_f, support_changes=int(changes)))
                nb_prev = nb
            totals['histories'] += 1
            totals['tables'] += sum(x['tables'] for x in rec['stages'])
            lines.append(rec)
    tag = args.tag or args.cls
    cs.dump(cs.ART / f'arm1_{tag}_{args.lo:05d}-{args.hi:05d}.jsonl.gz', lines)
    cs.dump(cs.ART / f'arm1_gains_{tag}_{args.lo:05d}-{args.hi:05d}.jsonl.gz', gains_out)
    print(json.dumps(dict(cls=args.cls, lo=args.lo, hi=args.hi, starts=min(args.hi, len(lst)) - args.lo,
                          histories=totals['histories'], tables=totals['tables'], gains_written=len(gains_out),
                          exact_calls=ev.exact_calls, seconds=round(time.time() - t0, 1))))


if __name__ == '__main__':
    main()
