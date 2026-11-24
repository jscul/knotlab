"""Test (c): the census of parts under rule Q (pre-registration "(c) Census of parts", "Uniform arm", "Mixed arm",
"Control").

For each census part (two-holder founder starts of ticket B with no hidden excess and no stall at round 1 under ordinary
growth; positions --lo to --hi of qcen.population()): growth under rule Q (structure rule not-all-equal: every birth
has a fresh distinction), 3 rounds or until a stage passes 20 distinctions, under conventions O and N and under every
round-1 choice (at most 64; else 62 more drawn by seed 2026112370), later rounds of a choice history by convention O.
  * Uniform arm: every newborn not-all-equal; one table per grown stage.
  * Mixed arm: each newborn even parity, odd parity or not-all-equal; every assignment when 3^n <= 4,096, else 4,096
    drawn by seed 2026112371 with one generator per history; at each stage the distinct prefixes.
At every grown stage the table of allowed words on the six observer distinctions (every other distinction forgotten)
is tested for a hidden excess (ticket B's evaluator).  A gain is a hidden excess at a grown stage (every part has none at
stage 0).  For each gain at stage 1 the control is computed: the same births and laws with the shared input removed from
every re-reading birth (fresh distinctions kept).

Exact reduction for speed (as ticket C's deviations A9, with the newborns' number of INPUTS): at stage t a newborn of
round t holds fresh distinctions nothing else holds yet, so its factor summed over them is a constant unless it is
not-all-equal with two or more inputs; so each table equals, up to a positive constant, the table of its effective
assignment (round-t newborns not-all-equal with two or more inputs kept, every other one even parity).  Every gain is
recomputed by direct contraction with its actual assignment (asserted equal); q_rowg.py re-verifies the reduction.

Outputs (artifacts folder): census_hist_<lo>-<hi>.jsonl.gz (one line per history), census_parts_<lo>-<hi>.jsonl.gz (one
line per part), census_gains_<lo>-<hi>.jsonl.gz (one line per gain table; the table and knots in full for at most 50
per stage, history and arm, all counted).
usage (repo root): timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file> --lo A --hi B
"""
import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qcen  # noqa: E402

cs, bc = qcen.cs, qcen.bc
HIT_CAP = 50


def ev_record(e):
    return [bool(e[0]), bool(e[1]), e[2], cs.frac(e[3])]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lo', type=int, required=True)
    ap.add_argument('--hi', type=int, required=True)
    ap.add_argument('--tag', default='')
    args = ap.parse_args()
    t_run = time.time()
    S = cs.starts()
    B = cs.b_lines('c3')
    pop = qcen.population()
    lift = set(qcen.liftable_parts())
    ev = cs.Eval()
    hist_lines, part_lines, gain_lines = [], [], []
    tot = Counter()
    for pos in range(args.lo, min(args.hi, len(pop))):
        si = pop[pos]
        s = S[si]
        hs, crec, (stars, laws, names, obs) = qcen.histories_of_part(si)
        nf = len(stars)
        T0 = bc.stage_tables(stars, laws, nf, nf, np.zeros((1, 0), np.int8), obs, choices=qcen.CH3)
        e0 = ev.run(T0)[0]
        assert not cs.is_excess(e0) and not B[si]['stage0_excess'], 'a census part has a hidden excess at stage 0'
        sup0 = cs.support(T0[0])
        cache = {}
        part_gain = Counter()
        digests = set()

        def tables_for(st, n, E):
            key_st = tuple(st[:n])
            todo = [i for i in range(len(E)) if (key_st, E[i].tobytes()) not in cache]
            if todo:
                Tn = bc.stage_tables(st, laws, nf, n, E[todo], obs, choices=qcen.CH3)
                evs = ev.run(Tn)
                for i, row, e in zip(todo, Tn, evs):
                    cache[(key_st, E[i].tobytes())] = (cs.support(row), e)
            return [cache[(key_st, E[i].tobytes())] for i in range(len(E))]

        for kind, j, ix, ch, h in hs:
            st = h['stars']
            digests.add((tuple(st), tuple(h['n_at'])))
            n_new = h['n_at'][-1] - nf
            info = qcen.newborn_info(h)
            A, lmode = qcen.assignments3(n_new, (s['tid'], s['mask'], qcen.KIND_CODE[kind], j))
            rec = dict(pos=pos, si=si, tid=s['tid'], mask=s['mask'], liftable=si in lift, kind=kind, j=j, choice=ix,
                       choice_dict=(None if ch is None else sorted([int(k), int(v)] for k, v in ch.items())),
                       choice_mode=crec['mode'], n_at=h['n_at'], D_at=h['D_at'], outcome=h['outcome'], stall=h['stall'],
                       holders_at=h['holders_at'],
                       births=[dict(n=len(rd), multi=sum(len(b['parents']) >= 2 for b in rd),
                                    reread=sum(b['reread'] for b in rd),
                                    reread_fresh=dict(Counter(str(b['fresh']) for b in rd if b['reread'])),
                                    fresh=dict(Counter(str(b['fresh']) for b in rd)),
                                    siblings=qcen.sibling_class(rd)) for rd in h['births']],
                       newborns=n_new, assignments=int(A.shape[0]), law_mode=lmode, uniform=[], stages=[])
            # ---------------- uniform arm ----------------
            nb_prev = 0
            for t in range(1, len(h['n_at'])):
                n = h['n_at'][t]
                nb = n - nf
                row = np.full((1, nb), qcen.NAE, dtype=np.int8)
                mc = qcen.multi_input_cols(h, nb_prev, nb)
                E, inv = c_eff(row, nb_prev, mc)
                sp, e = tables_for(st, n, E)[0]
                exc = bool(cs.is_excess(e))
                rec['uniform'].append(dict(t=t, eval=ev_record(e), excess=exc, support_changed=bool(sp != sup0)))
                tot['uniform_tables'] += 1
                if exc:
                    part_gain['uniform', t] += 1
                    gain_lines.append(gain_record('uniform', rec, h, st, laws, names, obs, nf, t, n, row[0], e, ev,
                                                  write=True, info=info))
                nb_prev = nb
            # ---------------- mixed arm ----------------
            prev_sup = {b'': sup0}
            nb_prev = 0
            for t in range(1, len(h['n_at'])):
                n = h['n_at'][t]
                nb = n - nf
                R = np.unique(A[:, :nb], axis=0)
                mc = qcen.multi_input_cols(h, nb_prev, nb)
                E, inv = c_eff(R, nb_prev, mc)
                ent = tables_for(st, n, E)
                hid = np.array([bool(ent[inv[i]][1][0] and ent[inv[i]][1][1]) for i in range(len(R))])
                exc = np.array([bool(cs.is_excess(ent[inv[i]][1])) for i in range(len(R))])
                changes = 0
                cur = {}
                for i in range(len(R)):
                    sp = ent[inv[i]][0]
                    cur[R[i].tobytes()] = sp
                    changes += prev_sup[R[i, :nb_prev].tobytes()] != sp
                prev_sup = cur
                hidden_exact = [ent[k][1][3] for k in range(len(ent)) if ent[k][1][0] and ent[k][1][1]
                                and ent[k][1][3] is not None]
                hidden_float = [ent[k][1][2] for k in range(len(ent)) if ent[k][1][0] and ent[k][1][1]
                                and ent[k][1][2] is not None]
                gains = np.nonzero(exc)[0]
                written = 0
                for gi in gains:
                    part_gain['mixed', t] += 1
                    gain_lines.append(gain_record('mixed', rec, h, st, laws, names, obs, nf, t, n, R[gi], ent[inv[gi]][1],
                                                  ev, write=written < HIT_CAP, info=info))
                    written += 1
                rec['stages'].append(dict(t=t, D=h['D_at'][t], knots=n, tables=int(len(R)), effective=int(len(E)),
                                          hidden=int(hid.sum()), excess=int(exc.sum()), support_changes=int(changes),
                                          best_hidden_exact=cs.frac(max(hidden_exact, default=None)),
                                          best_hidden_float=max(hidden_float, default=None)))
                tot['mixed_tables'] += int(len(R))
                tot['contracted'] += 0
                nb_prev = nb
            hist_lines.append(rec)
            tot['histories'] += 1
        part_lines.append(dict(pos=pos, si=si, tid=s['tid'], mask=s['mask'], knots=nf, D0=s['D0'], liftable=si in lift,
                               stage0_eval=ev_record(e0), choice_record=crec, histories=len(hs),
                               distinct_histories=len(digests),
                               gains={f'{a}_{t}': v for (a, t), v in sorted(part_gain.items())},
                               cache_tables=len(cache)))
        tot['parts'] += 1
        tot['contracted_tables'] += len(cache)
    tag = args.tag or 'c'
    sfx = f'{args.lo:05d}-{args.hi:05d}'
    qcen.qlaw.dump(qcen.ART / f'census_hist_{tag}_{sfx}.jsonl.gz', hist_lines)
    qcen.qlaw.dump(qcen.ART / f'census_parts_{tag}_{sfx}.jsonl.gz', part_lines)
    qcen.qlaw.dump(qcen.ART / f'census_gains_{tag}_{sfx}.jsonl.gz', gain_lines)
    print(json.dumps(dict(lo=args.lo, hi=args.hi, parts=tot['parts'], histories=tot['histories'],
                          uniform_tables=tot['uniform_tables'], mixed_tables=tot['mixed_tables'],
                          contracted_tables=tot['contracted_tables'], gains=len(gain_lines),
                          gains_uniform=sum(1 for g in gain_lines if g['arm'] == 'uniform'),
                          exact_calls=ev.exact_calls, seconds=round(time.time() - t_run, 1))))


def c_eff(R, nb_prev, multi_cols):
    """ticket C's arm1.effective_rows (read-only), with this study's columns kept: the round-t newborns with two or more
    inputs."""
    return qcen.c_arm1.effective_rows(R, nb_prev, multi_cols)


def gain_record(arm, rec, h, st, laws, names, obs, nf, t, n, row, e_red, ev, write, info):
    """One gain table: direct contraction with the actual assignment (asserted to be a hidden excess with the same exact
    score as the reduced table), the laws and fresh counts of the re-reading births in the stage, the siblings' choice,
    and for t = 1 the control (shared input removed from every re-reading birth of round 1)."""
    row = np.asarray(row, dtype=np.int8)[None, :]
    Td = bc.stage_tables(st, laws, nf, n, row, obs, choices=qcen.CH3)
    ed = ev.run(Td)[0]
    assert cs.is_excess(ed) and ed[3] == e_red[3], 'the reduced table and the direct contraction disagree'
    rr = []
    for k, (rd_t, i, n_in, reread, f) in enumerate(info[:n - nf]):
        if reread:
            b = h['births'][rd_t - 1][i]
            rr.append(dict(round=rd_t, birth=i, parent=b['parents'][0], loose=b['loose'][0], shared=b['shared'],
                           fresh=f, law=qcen.CH3[int(row[0, k])]))
    multi = []
    for k, (rd_t, i, n_in, reread, f) in enumerate(info[:n - nf]):
        if not reread and n_in >= 2:
            multi.append(dict(round=rd_t, birth=i, inputs=n_in, fresh=f, law=qcen.CH3[int(row[0, k])]))
    g = dict(arm=arm, pos=rec['pos'], si=rec['si'], tid=rec['tid'], mask=rec['mask'], liftable=rec['liftable'],
             kind=rec['kind'], j=rec['j'], choice=rec['choice'], choice_dict=rec['choice_dict'], t=t, D=h['D_at'][t],
             knots_n=n, laws=''.join(str(int(v)) for v in row[0]), eval=ev_record(ed), reread=rr, multi_input=multi,
             siblings=[qcen.sibling_class(rd) for rd in h['births'][:t]])
    if t == 1:
        cst = qcen.control_stars(h, n, nf)
        Tc = bc.stage_tables(cst, laws, nf, n, row, obs, choices=qcen.CH3)
        ec = ev.run(Tc)[0]
        g['control'] = dict(eval=ev_record(ec), excess=bool(cs.is_excess(ec)), table=[int(v) for v in Tc[0]])
    if write:
        laws_all = list(laws) + [qcen.CH3[int(v)] for v in row[0]]
        g['knots'] = qcen.knots_text(st[:n], laws_all, names)
        g['table'] = [int(v) for v in Td[0]]
        g['births'] = h['births'][:t]
    return g


if __name__ == '__main__':
    main()
