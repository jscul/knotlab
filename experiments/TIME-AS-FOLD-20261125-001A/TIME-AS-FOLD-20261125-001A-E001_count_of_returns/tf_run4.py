"""Run 4: every run of runs 1 to 3 with a clock (TD 2.5, series taken without "past its start"): the tests of TD 3 to 6
for each clock form once (dev 26), j = 0 and 1 where four equal periods follow, every X of TD 3.1; then the second pass
(through round t_j + 7 periods + 1, knot bound 30,000) of every test with no failure decided and some bar undecided.

Usage: python -B tf_run4.py first|second|p10 [--procs 6] [--inputs run1.jsonl.gz,run2.jsonl.gz,run3.jsonl.gz]
"""
from __future__ import annotations

import argparse
import gzip
import json
import multiprocessing as mp
import time
from collections import defaultdict

import tf_common as C
import tf_engine as E
import tf_runs as RN
import tf_series as Se
import tf_tests as Tt

ITEM_KEYS = ('group', 'start', 'base', 'rule', 'choice', 'knot_law', 'k')


def item_of(r):
    return {k: r[k] for k in ITEM_KEYS if k in r}


def select(inputs):
    out = []
    for fn in inputs:
        for r in C.jsonl(fn):
            if r.get('unfinished'):
                continue
            if r.get('nopast', {}).get('n_clocks', 0) > 0:
                out.append(item_of(r))
    return out


def chosen_clocks(series):
    groups = {}
    for s in series:
        if not s['clock']:
            continue
        key = (s['size'], tuple(sorted(set(s['periods']))), s['t0'] % 2)     # dev 26 (revised, dev 39)
        if key not in groups or s['P0'][0] < groups[key]['P0'][0]:
            groups[key] = s
    return [groups[k] for k in sorted(groups, key=lambda k: (groups[k]['t0'], groups[k]['P0'][0]))]


def strip(row):
    return row


def test_job(arg):
    it, mode, only = arg
    t0 = time.process_time()
    clock = E.Clock(600)
    rows = []
    head = dict(it)
    try:
        stars = RN.stars_of(it['start'])
        law = RN.law_of(it)
        if mode == 'first':
            rounds, kb = RN.bounds_of(it)
        else:
            rounds, kb = only['rounds'], 30000
        A = E.Run(E.from_stars(stars), law, rounds=rounds, knot_bound=kb, clock=clock)
        if A.stop == 'limit':
            return [dict(head, unfinished='run A: limit while growing', mode=mode)]
        ser, _ = Se.build_series(A, False, clock=clock)
        Se.describe(ser)
    except E.LimitReached:
        return [dict(head, unfinished='run A: limit while reading', mode=mode)]
    secA = time.process_time() - t0
    comps = Tt.Comparisons(A, law, rounds, kb)
    clocks = chosen_clocks(ser)
    for s in clocks:
        for j in (0, 1):
            if only is not None and (s['t0'], tuple(s['P0']), j) != (only['t0'], tuple(only['P0']), only['j']):
                continue
            try:
                trs = Tt.run_tests(A, law, s, j, comps, second_pass=(mode == 'second'))
            except E.LimitReached:
                trs = [{'t0': s['t0'], 'P_0': s['P0'], 'j': j, 'unfinished': 'limit in a comparison'}]
            for r in trs:
                if only is not None and only.get('X') is not None and r.get('X') != only['X']:
                    continue
                r.update(head)
                r['mode'] = mode
                r['P0'] = s['P0']
                r['run_A'] = {'rounds': A.rounds_done, 'stop': A.stop, 'knots': A.S.n_knots, 'sec': round(secA, 2)}
                rows.append(r)
    if not clocks:
        rows.append(dict(head, mode=mode, note='no clock in the regrown run'))
    return rows


def _init():
    C.cap_memory()


def run_first(inputs, procs, out='run4.jsonl.gz', items=None):
    items = items if items is not None else select(inputs)
    C.log('run 4: %d runs with a clock' % len(items))
    path = C.out_path(out)
    n = 0
    t0 = time.time()
    with gzip.open(path, 'wt') as f, mp.Pool(procs, initializer=_init, maxtasksperchild=10) as pool:
        for i, rows in enumerate(pool.imap_unordered(test_job, [(it, 'first', None) for it in items])):
            for r in rows:
                f.write(json.dumps(r, sort_keys=True, default=C._default) + '\n')
                n += 1
            if (i + 1) % 50 == 0 or i + 1 == len(items):
                C.log('run 4: %d/%d runs, %d rows, %.0f s wall' % (i + 1, len(items), n, time.time() - t0))
                f.flush()
    return path


def needs_second(r):
    if r.get('unfinished') or 'verdict_C' not in r:
        return False
    no_fail = r['verdict_C'] != 'fails' and r['verdict_C_iii'] != 'fails'
    undecided = r['verdict_C'] == 'undecided' or r['verdict_C_iii'] == 'undecided'
    return no_fail and undecided


def run_second(procs, src='run4.jsonl.gz', out='run4_second.jsonl.gz'):
    args = []
    with gzip.open(C.out_path(src), 'rt') as f:
        for line in f:
            r = json.loads(line)
            if needs_second(r):
                R2 = r['t_j'] + 7 * r['period'] + 1
                args.append((item_of(r), 'second', {'t0': r['t0'], 'P0': r['P0'], 'j': r['j'], 'X': r['X'],
                                                    'rounds': R2}))
    C.log('run 4, second pass: %d tests' % len(args))
    path = C.out_path(out)
    with gzip.open(path, 'wt') as f, mp.Pool(procs, initializer=_init, maxtasksperchild=5) as pool:
        for i, rows in enumerate(pool.imap_unordered(test_job, args)):
            for r in rows:
                f.write(json.dumps(r, sort_keys=True, default=C._default) + '\n')
            if (i + 1) % 20 == 0 or i + 1 == len(args):
                C.log('run 4, second pass: %d/%d' % (i + 1, len(args)))
                f.flush()
    return path


def p10():
    """P10, the test with X barred on the two-knot case: with the part of four barred at round 4, the one-member part
    returns at every round; with either part of three barred at round 3, the other does not return."""
    out = []
    for kl in ('nae', 'parity'):
        for ch in ('OLDEST', 'IN-TURN'):
            it = {'group': 'main', 'start': 'two-knot', 'base': 'COPY-LAW(OFFSHOOT)', 'rule': 'STEPS-1',
                  'choice': ch, 'knot_law': kl}
            A, law = RN.grow(it)
            comps = Tt.Comparisons(A, law, 18, 4000)
            R4 = A.roster(4)
            R3 = A.roster(3)
            four = [P for P in R4.parts if len(P) == 4]
            ones = [P for P in R4.parts if len(P) == 1]
            threes = [P for P in R3.parts if len(P) == 3]
            row = dict(it, parts_r4=[list(P) for P in R4.parts], parts_r3=[list(P) for P in R3.parts])
            if four and ones:
                B, _ = comps.run(('XB', 4, tuple(four[0])), 4, bar=tuple(four[0]))
                row['one_member_ticks_A'] = [Tt.y_chain(A, 4, list(P)) for P in ones]
                row['one_member_ticks_four_barred'] = [Tt.y_chain(B, 4, list(P)) for P in ones]
            if len(threes) == 2:
                res = []
                for a, b in ((0, 1), (1, 0)):
                    B, _ = comps.run(('XB', 3, tuple(threes[a])), 3, bar=tuple(threes[a]))
                    res.append({'barred': list(threes[a]), 'other': list(threes[b]),
                                'other_ticks_A': Tt.y_chain(A, 3, list(threes[b])),
                                'other_ticks_barred': Tt.y_chain(B, 3, list(threes[b]))})
                row['three_barred'] = res
            out.append(row)
    ok = all(all(len(t) > 0 and t == list(range(5, 19)) for t in r.get('one_member_ticks_four_barred', [[]]))
             and all(x['other_ticks_barred'] == [] for x in r.get('three_barred', [{'other_ticks_barred': [0]}]))
             for r in out)
    C.write_json('p10.json', {'rows': out, 'structural_clause_holds': ok})
    C.log('P10', ok)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('what')
    ap.add_argument('--procs', type=int, default=6)
    ap.add_argument('--inputs', default='run1.jsonl.gz,run2.jsonl.gz,run3.jsonl.gz')
    ap.add_argument('--out', default=None)
    ap.add_argument('--time-sample', type=int, default=0)
    ap.add_argument('--first', type=int, default=0, help='run only the first N registered runs (dev 40)')
    ap.add_argument('--skip', type=int, default=0, help='skip the first N registered runs (the remainder)')
    a = ap.parse_args()
    C.cap_memory()
    if a.what == 'first':
        items = select(a.inputs.split(','))
        if a.time_sample:
            import random
            items = random.Random(2026112506).sample(items, min(a.time_sample, len(items)))
        else:
            if a.skip:
                items = items[a.skip:]
            if a.first:
                items = items[:a.first]
        run_first(None, a.procs, out=a.out or ('run4.jsonl.gz' if not a.time_sample else 'run4_timing.jsonl.gz'),
                  items=items)
    elif a.what == 'second':
        run_second(a.procs)
    elif a.what == 'p10':
        p10()


if __name__ == '__main__':
    main()
