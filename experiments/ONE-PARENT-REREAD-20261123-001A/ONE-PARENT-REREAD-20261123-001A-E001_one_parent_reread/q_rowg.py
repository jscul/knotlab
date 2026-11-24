"""Checks of row G (pre-registration "Predictions (frozen)", G).  One part per run (--part):

  off        With re-reading switched off (qlaw.QGrowth(reread=False), exact last rounds) the engine equals the
             recorded driver lib.grow (stars, knots per stage, outcome) on the seven sources and the 280 funded draws,
             under each law, 12 rounds or 5,000 knots.  --law, and --what sources|draws (--arm for draws).
  parts500   With re-reading switched off the census engine (qcen.grow_census(reread=False)) gives ticket B's stars,
             knots and distinctions per stage and outcome, and per stage its numbers of tables, hidden tables and tables
             with a hidden excess under ticket B's three-law assignments (its seed), by direct contraction, on 500
             parts drawn from the census population by numpy default_rng(2026112372).  --lo/--hi slice the 500.
  stages     Tables agree with word-by-word enumeration on 100 drawn grown stages: stages t >= 1 of the census histories
             (rule Q) with at most 24 distinctions, drawn by default_rng(2026112373), one mixed-arm assignment of the
             stage drawn; direct contraction equals ticket B's brute_table, and the reduced table is proportional to it
             with the same evaluation.  Needs the census outputs.
  reduction  The reduction (effective assignments) against direct contraction on every prefix row of every stage of
             every history of the 27 liftable parts and of 200 parts drawn by default_rng(2026112374): equal numbers of
             hidden tables and tables with a hidden excess, and equal exact scores of every hidden table.
  addedknot  A stage-1 table with exactly one not-all-equal re-reading birth that has one fresh distinction, every other
             newborn parity, equals ticket C's table for the added knot on the same set (2M - M_T by ticket C's
             gates.table_with_T; and the table ticket C stored, where it stored one): every history of every census
             part in --lo/--hi, every such birth, every even/odd assignment of the other round-1 newborns when there are at
             most 64, else 64 drawn by default_rng([2026112376, target, mask, kind, j, birth]).  Direct contraction.
  extension  Every old word extends on every round of (b) (and of (a)) whose stage has at most 22 distinctions: from the
             stored prefixes, ticket A's words.Stage.extends (each birth's fresh distinctions are its own, so a word
             extends exactly when every birth has an assignment of its fresh distinctions satisfying its law); and, where
             the next stage has at most 24 distinctions, ticket A's words.projection_check.
  scorer     The evaluator against the recorded scorer evaluate(M) on every gain table written in full, every control
             table, and 1,000 drawn census tables (default_rng(2026112375)).  Needs the census outputs.
  verify     Every gain written in full whose stage has at most --maxd distinctions: every word of the four finished
             structures enumerated (ticket B's verify_excess.brute_joint_all via cstudy.full_check); hidden, exact score
             and the four record tables compared with the old-word table.  --lo/--hi slice the sorted list.
usage (repo root): timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file> --part P [...]
"""
import argparse
import importlib.util
import itertools
import json
import sys
import time
from collections import Counter
from fractions import Fraction
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qcen  # noqa: E402

qlaw, cs, bc = qcen.qlaw, qcen.cs, qcen.bc
SEED_PARTS500, SEED_STAGES, SEED_REDUCTION, SEED_SCORER, SEED_ADDED = 2026112372, 2026112373, 2026112374, 2026112375, 2026112376


def load_by_path(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def same_as_recorded(g, h):
    return [tuple(s) for s in h['stars']] == g.stars and h['n_at'] == g.n_at and h['outcome'] == g.outcome


# ---------------------------------------------------------------------------------------------------------------------
def part_off(law, what, arm):
    res = Counter()
    bad = []
    if what == 'sources':
        items = [(name, st) for name, st in qlaw.lib.recorded_sources().items()]
    else:
        items = [((d['arm'], d['draw']), d['stars']) for d in qlaw.lib.p3_draws() if d['arm'] == arm]
    for key, st in items:
        h = qlaw.lib.grow(st, law, qlaw.HORIZON, qlaw.CAP, time_limit=None)
        if what == 'draws' and (h['outcome'] == 'stall' or not h['births']):
            continue
        res['compared'] += 1
        g = qlaw.run_ab(st, law, 'O', reread=False, bound_next=False)
        ok = same_as_recorded(g, h)
        res['equal'] += ok
        res['rounds'] += len(g.rounds)
        res['zero_fresh_births'] += sum(x['zero_fresh'] for x in g.rounds)
        if law == 'parity':
            res['elim_vs_shortcut_disagree'] += sum(x['elim_vs_shortcut'] or 0 for x in g.rounds)
        if not ok:
            bad.append(dict(key=key, mine=[g.n_at, g.outcome], recorded=[h['n_at'], h['outcome']]))
    return dict(law=law, what=what, arm=arm, counts=dict(res), mismatches=bad, ok=not bad)


# ---------------------------------------------------------------------------------------------------------------------
def part_parts500(lo, hi):
    S = cs.starts()
    Bl = cs.b_lines('c3')
    pop = qcen.population()
    rng = np.random.default_rng(SEED_PARTS500)
    pick = sorted(int(x) for x in rng.choice(pop, size=500, replace=False))
    ev = cs.Eval()
    res = Counter()
    fails = []
    for si in pick[lo:hi]:
        s = S[si]
        stars, laws, names, obs = cs.start_struct(si)
        nf = len(stars)
        h = qcen.grow_census(stars, 'O', reread=False)
        hb = bc.grow(stars, 'nae')
        bl = Bl[si]
        res['parts'] += 1
        same = (h['stars'] == [tuple(x) for x in hb['stars']] and h['n_at'] == bl['n_at'] and h['D_at'] == bl['D_at']
                and h['outcome'] == bl['outcome'])
        res['stars_knots_distinctions_outcome_equal'] += same
        n_new = h['n_at'][-1] - nf
        A, mode = bc.assignments(n_new, (s['tid'], s['mask']), k=3)
        ok_tab = True
        for t, n in enumerate(h['n_at']):
            nb = n - nf
            R = np.unique(A[:, :nb], axis=0) if nb else np.zeros((1, 0), dtype=np.int8)
            T = bc.stage_tables(h['stars'], laws, nf, n, R, obs, choices=qcen.CH3)
            evs = ev.run(T)
            hid = sum(bool(e[0] and e[1]) for e in evs)
            exc = sum(bool(cs.is_excess(e)) for e in evs)
            bs = bl['stages'][t] if t < len(bl['stages']) else None
            res['stages'] += 1
            res['tables'] += len(R)
            res['excess_tables'] += exc
            eq_b = bs is not None and bs['tables'] == len(R) and bs['hidden'] == hid and bs['excess'] == exc
            res['stage_counts_equal_B'] += eq_b
            ok_tab &= eq_b
        if not (same and ok_tab):
            fails.append(dict(si=si, same=same, tables_ok=ok_tab, mine=[h['n_at'], h['D_at'], h['outcome']],
                              B=[bl['n_at'], bl['D_at'], bl['outcome']]))
    return dict(seed=SEED_PARTS500, drawn=pick[lo:hi], counts=dict(res), failures=fails, ok=not fails)


# ---------------------------------------------------------------------------------------------------------------------
def census_lines(kind='hist'):
    return [l for f in sorted(qcen.ART.glob(f'census_{kind}_c_*.jsonl.gz')) for l in qlaw.load(f)]


def part_stages(lo, hi):
    L = census_lines('hist')
    cand = [(li, t) for li, l in enumerate(L) for t in range(1, len(l['n_at'])) if l['D_at'][t] <= 24]
    rng = np.random.default_rng(SEED_STAGES)
    pick = [cand[int(i)] for i in rng.choice(len(cand), size=min(100, len(cand)), replace=False)]
    ev = cs.Eval()
    res = Counter()
    rows, fails = [], []
    for li, t in pick[lo:hi]:
        l = L[li]
        h, ix, ch, (stars, laws, names, obs) = qcen.history_by_key(l['si'], l['kind'], l['j'])
        assert h['n_at'] == l['n_at'] and h['D_at'] == l['D_at']
        nf = len(stars)
        n = h['n_at'][t]
        nb = n - nf
        A, _ = qcen.assignments3(h['n_at'][-1] - nf, (l['tid'], l['mask'], qcen.KIND_CODE[l['kind']], l['j']))
        R = np.unique(A[:, :nb], axis=0)
        row = R[int(rng.integers(0, len(R)))][None, :]
        nb_prev = h['n_at'][t - 1] - nf
        E, inv = qcen.c_arm1.effective_rows(row, nb_prev, qcen.multi_input_cols(h, nb_prev, nb))
        Td = bc.stage_tables(h['stars'], laws, nf, n, row, obs, choices=qcen.CH3)[0]
        Tr = bc.stage_tables(h['stars'], laws, nf, n, E, obs, choices=qcen.CH3)[0]
        laws_all = list(laws) + [qcen.CH3[int(v)] for v in row[0]]
        Tb = bc.brute_table(h['stars'][:n], laws_all[:n], obs)
        eq = np.array_equal(np.array([int(v) for v in Td]), Tb)
        prop = bc.proportional(Tr, Tb)
        ed, er = ev.run(np.stack([np.array([int(v) for v in Td]), np.array([int(v) for v in Tr])]))
        res['stages'] += 1
        res['direct_equal_enumeration'] += eq
        res['reduced_proportional'] += prop
        res['eval_equal'] += ed == er
        res['with_reread_births'] += any(b['reread'] for rd in h['births'][:t] for b in rd)
        rows.append(dict(si=l['si'], kind=l['kind'], j=l['j'], t=t, D=h['D_at'][t],
                         laws=''.join(str(int(v)) for v in row[0]), equal=bool(eq), proportional=bool(prop)))
        if not (eq and prop and ed == er):
            fails.append(rows[-1])
    return dict(seed=SEED_STAGES, candidates=len(cand), rows=rows, counts=dict(res), failures=fails, ok=not fails)


# ---------------------------------------------------------------------------------------------------------------------
def part_reduction(lo, hi):
    pop = qcen.population()
    lift = sorted(qcen.liftable_parts())
    rng = np.random.default_rng(SEED_REDUCTION)
    others = [si for si in pop if si not in set(lift)]
    pick = lift + sorted(int(x) for x in rng.choice(others, size=200, replace=False))
    S = cs.starts()
    ev = cs.Eval()
    res = Counter()
    fails = []
    for si in pick[lo:hi]:
        s = S[si]
        hs, crec, (stars, laws, names, obs) = qcen.histories_of_part(si)
        nf = len(stars)
        res['parts'] += 1
        for kind, j, ix, ch, h in hs:
            res['histories'] += 1
            A, _ = qcen.assignments3(h['n_at'][-1] - nf, (s['tid'], s['mask'], qcen.KIND_CODE[kind], j))
            nb_prev = 0
            for t in range(1, len(h['n_at'])):
                n = h['n_at'][t]
                nb = n - nf
                R = np.unique(A[:, :nb], axis=0)
                E, inv = qcen.c_arm1.effective_rows(R, nb_prev, qcen.multi_input_cols(h, nb_prev, nb))
                er = ev.run(bc.stage_tables(h['stars'], laws, nf, n, E, obs, choices=qcen.CH3))
                ed = ev.run(bc.stage_tables(h['stars'], laws, nf, n, R, obs, choices=qcen.CH3))
                hid_r = sum(bool(er[inv[i]][0] and er[inv[i]][1]) for i in range(len(R)))
                hid_d = sum(bool(e[0] and e[1]) for e in ed)
                exc_r = sum(bool(cs.is_excess(er[inv[i]])) for i in range(len(R)))
                exc_d = sum(bool(cs.is_excess(e)) for e in ed)
                same_eval = all((er[inv[i]][0], er[inv[i]][1], er[inv[i]][3]) == (ed[i][0], ed[i][1], ed[i][3])
                                for i in range(len(R)))
                res['stages'] += 1
                res['tables'] += len(R)
                res['excess_tables'] += exc_d
                ok = hid_r == hid_d and exc_r == exc_d and same_eval
                res['stages_equal'] += ok
                if not ok:
                    fails.append(dict(si=si, kind=kind, j=j, t=t, reduced=[hid_r, exc_r], direct=[hid_d, exc_d]))
                nb_prev = nb
    return dict(seed=SEED_REDUCTION, parts=pick[lo:hi], counts=dict(res), failures=fails, ok=not fails)


# ---------------------------------------------------------------------------------------------------------------------
def part_addedknot(lo, hi):
    c_gates = load_by_path('c_gates_ticketC', qcen.C_EXP / 'gates.py')
    lift = qcen.liftable_parts()
    S = cs.starts()
    pop = qcen.population()
    ev = cs.Eval()
    res = Counter()
    fails = []
    for pos in range(lo, min(hi, len(pop))):
        si = pop[pos]
        s = S[si]
        if s['D0'] > qcen.DMAX:
            continue
        hs, crec, (stars, laws, names, obs) = qcen.histories_of_part(si)
        nf = len(stars)
        stored = {}
        if si in lift:
            for g in lift[si]['gains']:
                if 'table' in g:
                    stored[frozenset(g['T'])] = g['table']
        Ccache = {}
        for kind, j, ix, ch, h in hs:
            if len(h['n_at']) < 2:
                continue
            rd = h['births'][0]
            n1 = h['n_at'][1]
            nb1 = n1 - nf
            for bi, b in enumerate(rd):
                if not (b['reread'] and b['fresh'] == 1):
                    continue
                others = [k for k in range(nb1) if k != bi]
                if 2 ** len(others) <= 64:
                    combos = list(itertools.product((0, 1), repeat=len(others)))
                else:
                    rng = np.random.default_rng([SEED_ADDED, s['tid'], s['mask'], qcen.KIND_CODE[kind], j, bi])
                    seen = set()
                    combos = []
                    while len(combos) < 64:
                        c = tuple(int(x) for x in rng.integers(0, 2, size=len(others)))
                        if c not in seen:
                            seen.add(c)
                            combos.append(c)
                rows = np.zeros((len(combos), nb1), dtype=np.int8)
                for r, c in enumerate(combos):
                    for k, v in zip(others, c):
                        rows[r, k] = v
                    rows[r, bi] = qcen.NAE
                T = sorted(b['inputs'])
                if tuple(T) not in Ccache:
                    Ccache[tuple(T)] = c_gates.table_with_T(stars, laws, obs, T)[1]
                Tc = Ccache[tuple(T)]
                Tq = bc.stage_tables(h['stars'], laws, nf, n1, rows, obs, choices=qcen.CH3)
                nc = bc.normalize(Tc)
                for r in range(len(rows)):
                    res['tables_compared'] += 1
                    eq = np.array_equal(np.array([int(v) for v in bc.normalize(Tq[r])], dtype=object),
                                        np.array([int(v) for v in nc], dtype=object))
                    res['equal'] += eq
                    if not eq:
                        fails.append(dict(si=si, kind=kind, j=j, birth=bi, T=[qcen.name_of(names, d) for d in T],
                                          laws=''.join(str(int(v)) for v in rows[r])))
                key = frozenset(qcen.name_of(names, d) for d in T)
                if key in stored:
                    res['stored_compared'] += 1
                    res['stored_equal'] += np.array_equal(np.array([int(v) for v in bc.normalize(Tc)]),
                                                          np.array([int(v) for v in bc.normalize(stored[key])]))
                res['births'] += 1
                e = ev.run(np.array([int(v) for v in Tc], dtype=np.int64)[None, :])[0]
                res['ticketC_table_excess'] += bool(cs.is_excess(e))
    return dict(lo=lo, hi=hi, counts=dict(res), failures=fails[:50], n_failures=len(fails), ok=not fails)


# ---------------------------------------------------------------------------------------------------------------------
def part_extension():
    words = load_by_path('words_ticketA', qlaw.A_EXP / 'words.py')
    res = {}
    for test in ('a', 'b'):
        c = Counter()
        failures = []
        for f in sorted((qlaw.ART / 'prefixes').glob(f'{test}_*.jsonl.gz')):
            for pre in qlaw.load(f):
                stars = [tuple(s) for s in pre['stars']]
                n_at = pre['n_at']
                law = pre['law']
                c['histories'] += 1
                for t in range(len(n_at) - 1):
                    old = stars[:n_at[t]]
                    old_names = {d for s in old for d in s}
                    if len(old_names) > 22:
                        break
                    new = stars[n_at[t]:n_at[t + 1]]
                    births = [(tuple(d for d in s if d in old_names), sum(1 for d in s if d not in old_names)) for s in new]
                    stage = words.Stage(old, law)
                    bad_words, bad_births = stage.extends(births)
                    c['rounds'] += 1
                    c['births'] += len(births)
                    c['zero_fresh_births'] += sum(1 for _, f_ in births if f_ == 0)
                    c['births_taking_shared'] += sum(1 for tk, _ in births
                                                     if any(sum(d in s for s in old) >= 2 for d in tk))
                    c['words_checked'] += stage.n_ok
                    c['words_failing'] += bad_words
                    c['births_failing'] += bad_births
                    if bad_words:
                        failures.append({k: pre.get(k) for k in ('test', 'arm', 'draw', 'source', 'law', 'conv')}
                                        | {'t': t + 1, 'failing_words': bad_words})
                    names_next = old_names | {d for s in new for d in s}
                    if len(names_next) <= 24:
                        n_old, n_new, reached, equal = words.projection_check(old, new, law)
                        c['projection_checks'] += 1
                        c['projection_equal'] += equal
        res[test] = dict(counts=dict(c), failures=failures)
    res['ok'] = all(not res[t]['failures'] for t in ('a', 'b'))
    return res


# ---------------------------------------------------------------------------------------------------------------------
def part_scorer():
    ns = bc.load_starter()
    evaluate = ns['evaluate']
    ev = cs.Eval()
    tabs = []
    for g in census_lines('gains'):
        if 'table' in g:
            tabs.append(('gain_' + g['arm'], g['table']))
        if 'control' in g:
            tabs.append(('control_' + g['arm'], g['control']['table']))
    L = [l for l in census_lines('hist') if len(l['n_at']) >= 2]
    rng = np.random.default_rng(SEED_SCORER)
    for _ in range(1000):
        l = L[int(rng.integers(0, len(L)))]
        t = int(rng.integers(1, len(l['n_at'])))
        h, ix, ch, (stars, laws, names, obs) = qcen.history_by_key(l['si'], l['kind'], l['j'])
        nf = len(stars)
        A, _ = qcen.assignments3(h['n_at'][-1] - nf, (l['tid'], l['mask'], qcen.KIND_CODE[l['kind']], l['j']))
        R = np.unique(A[:, :h['n_at'][t] - nf], axis=0)
        row = R[int(rng.integers(0, len(R)))][None, :]
        T = bc.stage_tables(h['stars'], laws, nf, h['n_at'][t], row, obs, choices=qcen.CH3)[0]
        tabs.append(('drawn', [int(v) for v in bc.normalize(T)]))
    res = Counter()
    fails = []
    for kind, t in tabs:
        tn = bc.normalize(np.array([int(v) for v in t], dtype=object))
        if tn.dtype == object:
            res[kind + '_too_large_for_int64'] += 1
            continue
        M = np.array(tn, dtype=np.int64).reshape(8, 8)
        r = evaluate(M)
        e = ev.run(tn[None, :])[0]
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


# ---------------------------------------------------------------------------------------------------------------------
def part_verify(maxd, lo, hi):
    items = [g for g in census_lines('gains') if 'knots' in g]
    items.sort(key=lambda g: (g['D'], g['knots_n'], Fraction(g['eval'][3])))
    res = Counter()
    rows = []
    for g in items[lo:hi]:
        knots = [bc.parse_knots([k])[0] for k in g['knots']]
        D = len({m for _, mem in knots for m in mem})
        if D > maxd:
            res['not_enumerated_' + g['arm']] += 1
            continue
        fc = cs.full_check(knots)
        Jt = cs.joint_from_table(g['table'])
        tab_eq = all(np.array_equal(fc['J'][k], Jt[k]) for k in Jt)
        good = fc['hidden'] and str(fc['score']) == g['eval'][3] and Fraction(g['eval'][3]) > 2 and tab_eq
        res['enumerated_' + g['arm']] += 1
        res['agree_' + g['arm']] += bool(good)
        rows.append(dict(arm=g['arm'], si=g['si'], kind=g['kind'], j=g['j'], t=g['t'], laws=g['laws'], D=D,
                         score_table=g['eval'][3],
                         full_enumeration=dict(hidden=fc['hidden'], score=str(fc['score']), change=str(fc['change']),
                                               words=fc['words'], distinctions_finished=fc['distinctions_finished'],
                                               joint_equals_table=bool(tab_eq))))
    return dict(items=len(items), lo=lo, hi=hi, counts=dict(res), rows=rows,
                ok=sum(v for k, v in res.items() if k.startswith('enumerated')) == sum(
                    v for k, v in res.items() if k.startswith('agree')))


def part_stalled():
    """The 6,312 two-holder starts with no hidden excess that stall at round 1 under ordinary growth (ticket B's record):
    round 1 under rule Q (both conventions) stalls too, with the same short knots as the recorded operator."""
    S = cs.starts()
    res = Counter()
    fails = []
    for si in qcen.stalled_two_holder():
        stars, laws, names, obs = cs.start_struct(si)
        res['parts'] += 1
        turn = qlaw.lib.EO.step(bc.from_stars_ext(stars), 'nae')
        for conv in ('O', 'N'):
            r = qlaw.QGrowth(stars, 'nae', conv).plan(None)
            ok = r.status == 'stall' and turn.status == 'stall' and tuple(r.shortages) == tuple(turn.shortages)
            res[f'stall_{conv}'] += ok
            if not ok:
                fails.append(dict(si=si, conv=conv, status=r.status, recorded=turn.status))
    return dict(counts=dict(res), failures=fails[:50], ok=not fails)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--part', required=True,
                    choices=('off', 'parts500', 'stages', 'reduction', 'addedknot', 'extension', 'scorer', 'verify',
                             'stalled'))
    ap.add_argument('--law', choices=('nae', 'parity'))
    ap.add_argument('--what', choices=('sources', 'draws'))
    ap.add_argument('--arm', type=int)
    ap.add_argument('--lo', type=int, default=0)
    ap.add_argument('--hi', type=int, default=10 ** 9)
    ap.add_argument('--maxd', type=int, default=26)
    args = ap.parse_args()
    t0 = time.time()
    if args.part == 'off':
        out = part_off(args.law, args.what, args.arm)
        name = f'gate_off_{args.what}_{args.law}' + ('' if args.arm is None else f'_arm{args.arm}')
    else:
        out = {'parts500': lambda: part_parts500(args.lo, args.hi), 'stages': lambda: part_stages(args.lo, args.hi),
               'reduction': lambda: part_reduction(args.lo, args.hi),
               'addedknot': lambda: part_addedknot(args.lo, args.hi), 'extension': part_extension,
               'scorer': part_scorer, 'verify': lambda: part_verify(args.maxd, args.lo, args.hi),
               'stalled': part_stalled}[args.part]()
        sfx = '' if (args.lo == 0 and args.hi == 10 ** 9) else f'_{args.lo}-{min(args.hi, 10 ** 6)}'
        name = f'gate_{args.part}{sfx}'
    out['seconds'] = round(time.time() - t0, 1)
    out['rlaw_sha256'] = qlaw.sha256(qlaw.A_EXP / 'rlaw.py')
    (qlaw.ART / f'{name}.json').write_text(json.dumps(out, indent=1, default=str) + '\n')
    print(json.dumps(dict(part=args.part, ok=out.get('ok'), counts=out.get('counts'), seconds=out['seconds']),
                     default=str)[:3000])


if __name__ == '__main__':
    main()
