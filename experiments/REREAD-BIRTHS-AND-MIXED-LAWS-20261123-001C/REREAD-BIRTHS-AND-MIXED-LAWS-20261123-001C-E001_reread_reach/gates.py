"""Checks of row G (REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C, "Predictions (frozen)", G), and the full enumerations.

Parts (one per run, --part):
  g1two    500 two-holder starts (drawn by seed 2026112352) with no short knot in any round: ticket A's engine under rule
           R gives ticket B's stars, knots and distinctions per stage and outcome, and, under ticket B's three-law
           assignments (its seed), its numbers of tables, hidden tables and tables with a hidden excess per stage.  Also:
           arm 1's reduced evaluation gives the same hidden and excess counts as the direct contraction on every table.
  g1three  the same on 500 three-holder starts (seed 2026112353); reported, not judged.
  known    the ten known starts (targets 135 to 144 without nae(y3,Bh1,Bh2,Bh3)): arm 2's table for T = {y3, Bh1, Bh2,
           Bh3} gives 271/135 (two) and 541/270 (eight), hidden, by the table and by enumerating every word of the four
           finished structures; and no knot is short there under rule R in any round.
  pairs    200 drawn pairs of start and T of arm 2 (seed 2026112355): 2*M - M_T equals the table of the start with the
           added knot by word-by-word enumeration.
  stages   100 drawn grown stages of arm 1 with at most 24 distinctions (seed 2026112354), one drawn assignment each: the
           direct contraction equals word-by-word enumeration, and arm 1's reduced table is proportional to it with the
           same evaluation.  Needs arm 1's outputs.
  scorer   the evaluator against the recorded scorer evaluate(M) on every gain table of both arms and on 1,000 drawn
           tables of each arm.  Needs both arms' outputs.
  verify   every gain of both arms whose finished structures have at most --maxd distinctions: enumerate every word of the
           four finished structures; hidden and exact score compared with the table's.  Needs both arms' outputs.
usage (repo root): timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file> --part P [--lo A --hi B]
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
import arm1  # noqa: E402
import arm2  # noqa: E402
import cstudy as cs  # noqa: E402

bc = cs.bc


def reduced_counts(st, laws, nf, n_at, A, obs, h, ev):
    """Arm 1's reduced evaluation (arm1.effective_rows) per stage: (tables, hidden, excess) counts."""
    multi = [len(b['parents']) >= 2 for rd in h['births'] for b in rd]
    out = []
    nb_prev = 0
    for t, n in enumerate(n_at):
        nb = n - nf
        if t == 0:
            out.append(None)
            continue
        R = np.unique(A[:, :nb], axis=0)
        E, inv = arm1.effective_rows(R, nb_prev, {k for k in range(nb_prev, nb) if multi[k]})
        Tn = bc.stage_tables(st, laws, nf, n, E, obs, choices=cs.CH3)
        evs = ev.run(Tn)
        hid = sum(bool(evs[inv[i]][0] and evs[inv[i]][1]) for i in range(len(R)))
        exc = sum(bool(cs.is_excess(evs[inv[i]])) for i in range(len(R)))
        out.append((len(R), hid, exc))
        nb_prev = nb
    return out


def part_g1(cls, seed, lo, hi):
    S = cs.starts()
    Bl = cs.b_lines('c3')
    pool = [i for i in range(len(S)) if cs.start_class(S[i]) == cls and Bl[i]['outcome'] != 'stall']
    rng = np.random.default_rng(seed)
    pick = sorted(int(x) for x in rng.choice(pool, size=500, replace=False))
    ev = cs.Eval()
    res = Counter()
    fails = []
    for si in pick[lo:hi]:
        s = S[si]
        stars, laws, names, obs = cs.start_struct(si)
        nf = len(stars)
        h = cs.grow_R(stars, 'O')
        hb = bc.grow(stars, 'nae')
        bl = Bl[si]
        res['starts'] += 1
        short = any(len(x) for x in h['short'])
        res['short_knot'] += short
        same = (h['stars'] == [tuple(x) for x in hb['stars']] and h['n_at'] == bl['n_at'] and h['D_at'] == bl['D_at']
                and {'closed': 'closed'}.get(h['outcome'], h['outcome']) == bl['outcome'])
        res['stars_knots_distinctions_outcome_equal'] += same
        # ticket B's three-law assignments (its seed), direct contraction per unique prefix
        n_new = h['n_at'][-1] - nf
        A, mode = bc.assignments(n_new, (s['tid'], s['mask']), k=3)
        red = reduced_counts(h['stars'], laws, nf, h['n_at'], A, obs, h, ev)
        ok_tab = True
        for t, n in enumerate(h['n_at']):
            nb = n - nf
            R = np.unique(A[:, :nb], axis=0) if nb else np.zeros((1, 0), dtype=np.int8)
            T = bc.stage_tables(h['stars'], laws, nf, n, R, obs, choices=cs.CH3)
            evs = ev.run(T)
            hid = sum(bool(e[0] and e[1]) for e in evs)
            exc = sum(bool(cs.is_excess(e)) for e in evs)
            bs = bl['stages'][t] if t < len(bl['stages']) else None
            res['stages'] += 1
            res['tables'] += len(R)
            eq_b = bs is not None and bs['tables'] == len(R) and bs['hidden'] == hid and bs['excess'] == exc
            res['stage_counts_equal_B'] += eq_b
            res['excess_tables'] += exc
            if t >= 1:
                res['grown_stages'] += 1
                eq_r = red[t] == (len(R), hid, exc)
                res['reduced_equal_direct'] += eq_r
                ok_tab &= eq_r
            ok_tab &= eq_b
        if not (same and ok_tab and not short):
            fails.append(dict(si=si, same=same, short=short, tables_ok=ok_tab, mine=[h['n_at'], h['D_at'], h['outcome']],
                              B=[bl['n_at'], bl['D_at'], bl['outcome']]))
    out = dict(cls=cls, seed=seed, drawn=pick[lo:hi], counts=dict(res), failures=fails, ok=not fails)
    return out


def known_starts():
    """The ten known starts: (si, tid, mask) of targets 135..144 without nae(y3,Bh1,Bh2,Bh3)."""
    S = cs.starts()
    tk = cs.target_knots()
    out = []
    for tid in range(135, 145):
        ks = tk[tid]
        j = [i for i, (law, mem) in enumerate(ks) if law == 'nae' and tuple(mem) == ('y3', 'Bh1', 'Bh2', 'Bh3')]
        assert len(j) == 1, (tid, ks)
        mask = ((1 << len(ks)) - 1) & ~(1 << j[0])
        si = [i for i, s in enumerate(S) if s['tid'] == tid and s['mask'] == mask]
        assert len(si) == 1
        out.append((si[0], tid, mask))
    return out


def table_with_T(stars, laws, obs, T):
    words = cs.allowed_words(stars, laws)
    oi = cs.obs_index(words, obs)
    M = np.bincount(oi, minlength=64).astype(np.int64)
    m = arm2.mask_of(T)
    a = words & m
    eq = (a == 0) | (a == m)
    MT = np.bincount(oi[eq], minlength=64).astype(np.int64)
    return M, 2 * M - MT


def part_known():
    pop = set(arm2.population())
    ev = cs.Eval()
    rows = []
    want = Counter()
    for si, tid, mask in known_starts():
        stars, laws, names, obs = cs.start_struct(si)
        T = [names.index(x) for x in ('y3', 'Bh1', 'Bh2', 'Bh3')]
        M, Tab = table_with_T(stars, laws, obs, T)
        e = ev.run(Tab[None, :])[0]
        e0 = ev.run(M[None, :])[0]
        knots = cs.named_knots(stars, laws, names) + [('nae', ('y3', 'Bh1', 'Bh2', 'Bh3', 'fT'))]
        fc = cs.full_check(knots)
        Jt = cs.joint_from_table(Tab)
        joint_eq = all(np.array_equal(fc['J'][k], Jt[k]) for k in Jt)
        h = cs.grow_R(stars, 'O')
        hN = cs.grow_R(stars, 'N')
        rows.append(dict(si=si, tid=tid, mask=mask, in_population=si in pop, start=cs.knots_text(stars, laws, names),
                         stage0=[e0[0], e0[1], e0[2], cs.frac(e0[3])], hidden=bool(e[0] and e[1]),
                         score=cs.frac(e[3]), full_enumeration=dict(hidden=fc['hidden'], score=str(fc['score']),
                                                                    change=str(fc['change']), words=fc['words'],
                                                                    joint_equals_table=joint_eq),
                         short_knots_O=[len(x) for x in h['short']], short_knots_N=[len(x) for x in hN['short']]))
        want[cs.frac(e[3])] += 1
    ok = (want == Counter({'271/135': 2, '541/270': 8}) and all(r['hidden'] and r['in_population'] for r in rows)
          and all(r['full_enumeration']['hidden'] and r['full_enumeration']['score'] == r['score']
                  and r['full_enumeration']['joint_equals_table'] for r in rows)
          and all(not any(r['short_knots_O']) and not any(r['short_knots_N']) for r in rows))
    return dict(rows=rows, scores=dict(want), ok=ok)


def part_pairs(lo, hi):
    S = cs.starts()
    pop = arm2.population()
    rng = np.random.default_rng(cs.SEED_G_PAIRS)
    sis = [pop[int(i)] for i in rng.choice(len(pop), size=200, replace=False)]
    picks = []
    for si in sis:
        D = S[si]['D0']
        Tl = [T for k in (2, 3, 4) for T in itertools.combinations(range(D), k)]
        picks.append((si, Tl[int(rng.integers(0, len(Tl)))]))
    ev = cs.Eval()
    res = Counter()
    fails = []
    for si, T in picks[lo:hi]:
        stars, laws, names, obs = cs.start_struct(si)
        D = len(names)
        M, Tab = table_with_T(stars, laws, obs, list(T))
        st2 = list(stars) + [tuple(T) + (D,)]
        Tb = bc.brute_table(st2, list(laws) + ['nae'], obs)
        eq = np.array_equal(Tb, Tab)
        res['pairs'] += 1
        res['equal'] += eq
        e1, e2 = ev.run(np.stack([Tab, Tb]))
        res['eval_equal'] += (e1 == e2)
        if not eq:
            fails.append(dict(si=si, T=[names[d] for d in T]))
    return dict(picks=[[si, list(T)] for si, T in picks[lo:hi]], counts=dict(res), failures=fails, ok=not fails)


def arm1_lines():
    return [l for f in sorted(cs.ART.glob('arm1_two_*.jsonl.gz')) + sorted(cs.ART.glob('arm1_three_*.jsonl.gz'))
            for l in cs.jl_load(f)]


def history_struct(line):
    """Rebuild a history of arm 1 from its line (deterministic)."""
    hs, crec, (stars, laws, names, obs) = arm1.histories_of(line['si'], line['cls'])
    for kind, j, ix, h in hs:
        if kind == line['kind'] and j == line['j']:
            assert h['n_at'] == line['n_at'] and h['D_at'] == line['D_at']
            return h, (stars, laws, names, obs)
    raise KeyError(line['si'])


def part_stages(lo, hi):
    L = arm1_lines()
    cand = [(li, t) for li, l in enumerate(L) for t in range(1, len(l['n_at'])) if l['D_at'][t] <= 24]
    rng = np.random.default_rng(cs.SEED_G_STAGES)
    pick = [cand[int(i)] for i in rng.choice(len(cand), size=min(100, len(cand)), replace=False)]
    ev = cs.Eval()
    res = Counter()
    fails = []
    rows = []
    for li, t in pick[lo:hi]:
        l = L[li]
        h, (stars, laws, names, obs) = history_struct(l)
        nf = len(stars)
        n = h['n_at'][t]
        nb = n - nf
        A, _ = cs.assignments3(h['n_at'][-1] - nf, (l['tid'], l['mask'], arm1.KIND_CODE[l['kind']], l['j']))
        R = np.unique(A[:, :nb], axis=0)
        row = R[int(rng.integers(0, len(R)))][None, :]
        nb_prev = h['n_at'][t - 1] - nf
        multi = [len(b['parents']) >= 2 for rd in h['births'] for b in rd]
        E, inv = arm1.effective_rows(row, nb_prev, {k for k in range(nb_prev, nb) if multi[k]})
        Td = bc.stage_tables(h['stars'], laws, nf, n, row, obs, choices=cs.CH3)[0]
        Tr = bc.stage_tables(h['stars'], laws, nf, n, E, obs, choices=cs.CH3)[0]
        laws_all = list(laws) + [cs.CH3[int(v)] for v in row[0]]
        Tb = bc.brute_table(h['stars'][:n], laws_all[:n], obs)
        eq = np.array_equal(np.array([int(v) for v in Td]), Tb)
        prop = bc.proportional(Tr, Tb)
        ed, er = ev.run(np.stack([np.array([int(v) for v in Td]), np.array([int(v) for v in Tr])]))
        res['stages'] += 1
        res['direct_equal_enumeration'] += eq
        res['reduced_proportional'] += prop
        res['eval_equal'] += ed == er
        rows.append(dict(si=l['si'], kind=l['kind'], j=l['j'], t=t, D=h['D_at'][t], laws=[cs.CH3[int(v)] for v in row[0]],
                         equal=bool(eq), proportional=bool(prop)))
        if not (eq and prop and ed == er):
            fails.append(rows[-1])
    return dict(candidates=len(cand), rows=rows, counts=dict(res), failures=fails, ok=not fails)


def arm2_lines():
    return [l for f in sorted(cs.ART.glob('arm2_all_*.jsonl.gz')) for l in cs.jl_load(f)]


def arm1_gains():
    return [g for f in sorted(cs.ART.glob('arm1_gains_two_*.jsonl.gz')) + sorted(cs.ART.glob('arm1_gains_three_*.jsonl.gz'))
            for g in cs.jl_load(f)]


def part_scorer():
    ns = bc.load_starter()
    evaluate = ns['evaluate']
    ev = cs.Eval()
    rng = np.random.default_rng(2026112356)
    tabs = []
    for g in arm1_gains():
        tabs.append(('arm1_gain', g['table']))
        tabs.append(('arm1_gain_even_payers', g['even_payers_table']))
    L2 = arm2_lines()
    for l in L2:
        for g in l['gains']:
            if 'table' in g:
                tabs.append(('arm2_gain', g['table']))
    # 1,000 drawn arm-2 tables (start, T drawn), recomputed
    pop_lines = [l for l in L2]
    for _ in range(1000):
        l = pop_lines[int(rng.integers(0, len(pop_lines)))]
        stars, laws, names, obs = cs.start_struct(l['si'])
        D = len(names)
        Tl = [T for k in (2, 3, 4) for T in itertools.combinations(range(D), k)]
        T = Tl[int(rng.integers(0, len(Tl)))]
        tabs.append(('arm2_drawn', [int(v) for v in table_with_T(stars, laws, obs, list(T))[1]]))
    # 1,000 drawn arm-1 tables (history with a grown stage, stage, assignment drawn), by direct contraction
    L1 = [l for l in arm1_lines() if len(l['n_at']) >= 2]
    for _ in range(1000):
        l = L1[int(rng.integers(0, len(L1)))]
        t = int(rng.integers(1, len(l['n_at'])))
        h, (stars, laws, names, obs) = history_struct(l)
        nf = len(stars)
        A, _ = cs.assignments3(h['n_at'][-1] - nf, (l['tid'], l['mask'], arm1.KIND_CODE[l['kind']], l['j']))
        R = np.unique(A[:, :h['n_at'][t] - nf], axis=0)
        row = R[int(rng.integers(0, len(R)))][None, :]
        T = bc.stage_tables(h['stars'], laws, nf, h['n_at'][t], row, obs, choices=cs.CH3)[0]
        tabs.append(('arm1_drawn', [int(v) for v in bc.normalize(T)]))
    res = Counter()
    fails = []
    for kind, t in tabs:
        M = np.array(t, dtype=np.int64).reshape(8, 8)
        r = evaluate(M)
        e = ev.run(np.array(t, dtype=np.int64)[None, :])[0]
        res[kind] += 1
        if r is None:
            res[kind + '_scorer_none'] += 1
            continue
        hid = bool(e[0] and e[1])
        ok = hid == bool(r[1]) and (not hid or abs(e[2] - r[0]) < 1e-9)
        res[kind + '_agree'] += ok
        if not ok:
            fails.append(dict(kind=kind, table=t, mine=[e[0], e[1], e[2]], recorded=[r[0], bool(r[1])]))
    return dict(counts=dict(res), failures=fails[:20], n_failures=len(fails), ok=not fails)


def part_verify(maxd, lo, hi):
    """Enumerate every word of the four finished structures of each gain (arm 1: stage knots; arm 2: start + the added
    knot) with at most maxd distinctions before the setting births."""
    rows = []
    items = []
    for g in arm1_gains():
        knots = [bc.parse_knots([k])[0] for k in g['knots']]
        items.append(('arm1', g, knots, g['eval'][3]))
    for l in arm2_lines():
        for g in l['gains']:
            knots = [bc.parse_knots([k])[0] for k in l['start_knots']] + [('nae', tuple(g['T']) + ('fT',))]
            items.append(('arm2', dict(si=l['si'], T=g['T'], table=g.get('table')), knots, g['score']))
    items.sort(key=lambda x: (len({m for _, mem in x[2] for m in mem}), len(x[2])))
    res = Counter()
    for arm, g, knots, score in items[lo:hi]:
        D = len({m for _, mem in knots for m in mem})
        if D > maxd:
            res['not_enumerated_' + arm] += 1
            continue
        fc = cs.full_check(knots)
        good = fc['hidden'] and str(fc['score']) == score and Fraction(score) > 2
        tab_eq = None
        if g.get('table') is not None:
            Jt = cs.joint_from_table(g['table'])
            tab_eq = all(np.array_equal(fc['J'][k], Jt[k]) for k in Jt)
        res['enumerated_' + arm] += 1
        res['agree_' + arm] += bool(good and tab_eq is not False)
        rows.append(dict(arm=arm, si=g['si'], kind=g.get('kind'), j=g.get('j'), t=g.get('t'), T=g.get('T'), D=D,
                         knots=[bc.fmt_knot(lw, m) for lw, m in knots], score_table=score,
                         full_enumeration=dict(hidden=fc['hidden'], score=str(fc['score']), change=str(fc['change']),
                                               words=fc['words'], arg=fc['arg'], joint_equals_table=tab_eq)))
    return dict(items=len(items), counts=dict(res), rows=rows, ok=res.get('enumerated_arm1', 0) + res.get('enumerated_arm2', 0)
                == res.get('agree_arm1', 0) + res.get('agree_arm2', 0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--part', required=True, choices=('g1two', 'g1three', 'known', 'pairs', 'stages', 'scorer', 'verify'))
    ap.add_argument('--lo', type=int, default=0)
    ap.add_argument('--hi', type=int, default=10 ** 9)
    ap.add_argument('--maxd', type=int, default=26)
    args = ap.parse_args()
    t0 = time.time()
    assert cs.rlaw_sha() == cs.RLAW_SHA
    if args.part == 'g1two':
        out = part_g1('two', cs.SEED_G_TWO, args.lo, args.hi)
    elif args.part == 'g1three':
        out = part_g1('three', cs.SEED_G_THREE, args.lo, args.hi)
    elif args.part == 'known':
        out = part_known()
    elif args.part == 'pairs':
        out = part_pairs(args.lo, args.hi)
    elif args.part == 'stages':
        out = part_stages(args.lo, args.hi)
    elif args.part == 'scorer':
        out = part_scorer()
    else:
        out = part_verify(args.maxd, args.lo, args.hi)
    out['seconds'] = round(time.time() - t0, 1)
    sfx = '' if (args.lo == 0 and args.hi == 10 ** 9) else f'_{args.lo}-{min(args.hi, 10 ** 6)}'
    (cs.ART / f'gates_{args.part}{sfx}.json').write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps(dict(part=args.part, ok=out.get('ok'), counts=out.get('counts', out.get('scores')),
                          seconds=out['seconds']), default=str))


if __name__ == '__main__':
    main()
