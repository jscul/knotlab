"""Runs 1, 2 and 3 of the pre-registration: every series with and without "past its start" (TD 2), per run.

Usage: python -B tf_runs.py run1|run2|run3 [--procs 6] [--limit-items N] [--out NAME] [--time-sample N]
Each run A has the registered limit of 600 seconds of process time (growth and the reading of its series).
Output: one JSONL line per run (gzip), a progress log.
"""
from __future__ import annotations

import argparse
import gzip
import json
import multiprocessing as mp
import os
import random
import sys
import time
from collections import Counter

import tf_common as C
import tf_engine as E
import tf_series as Se

RULES_RUN1 = ['Q', 'MET', 'STEPS-1', 'STEPS-2', 'UP-TO-2', 'MET:offshoot', 'MET:join', 'STEPS-1:join',
              'STEPS-1:offshoot', 'STEPS-2:join', 'STEPS-2:offshoot', 'STEPS-3:join', 'STEPS-3:offshoot']
CHOICES = ['OLDEST', 'NEWEST', 'IN-TURN', 'BY-COUNT']
KNOT_LAWS = ['nae', 'parity']
LAWS_OF_THE_COUNT = ('Q', 'MET', 'MET:offshoot', 'STEPS-1', 'UP-TO-2')
RING_STARTS = ('Ring(5,3)', 'Ring(7,3)', 'Ring(9,3)', 'Ring(5,4)', 'D2(4,3)', 'D2(5,3)', 'D2(6,3)', 'DW(5,3)')


def choices_for(rule):
    if rule is None:
        return ['OLDEST']
    if rule == 'MET:join':
        return ['OLDEST', 'NEWEST', 'BY-COUNT']        # IN-TURN is OLDEST for joins (TD 1.4)
    return CHOICES


def items_run1():
    """Run 1's items in their registered order (dev 28): group main (the control and the thirteen rules), then the
    taking laws with the fresh count by parents, then with demand taken before the takes; within a group the starts in
    the order of starts.json, the base laws, the rules in the order of rules.json, the choices, the knot laws."""
    named = list(C.named_stars())
    order = [r['id'] for r in C.rules()['rules']]
    rules = sorted(RULES_RUN1, key=order.index)
    out = []
    for group in ('main', 'fbp', 'dbt'):
        for st in named:
            for base in E.BASE_ORDER:
                for rule in ([None] if group == 'main' else []) + rules:
                    for ch in choices_for(rule):
                        for kl in KNOT_LAWS:
                            out.append({'group': group, 'start': st, 'base': base, 'rule': rule, 'choice': ch,
                                        'knot_law': kl})
    return out


def items_run2():
    out = []
    for nm, stars in C.ring227():
        for rule in (None, 'MET'):
            for ch in choices_for(rule):
                for kl in KNOT_LAWS:
                    out.append({'group': 'ring227', 'start': nm, 'base': 'RING-LAW', 'rule': rule, 'choice': ch,
                                'knot_law': kl})
    return out


LADDER_STARTS = ('Ring(5,3)', 'Ring(7,3)', 'Ring(9,3)', 'D2(4,3)', 'D2(5,3)', 'D2(6,3)', 'DW(5,3)')


def items_run3():
    out = []
    for st in LADDER_STARTS:
        for k in range(1, 9):
            for ch in CHOICES:
                for kl in KNOT_LAWS:
                    out.append({'group': 'ladder', 'start': st, 'base': 'RING-LAW', 'rule': 'STEPS-%d' % k,
                                'choice': ch, 'knot_law': kl, 'k': k})
    return out


def stars_of(name):
    named = C.named_stars()
    if name in named:
        return named[name]
    for nm, stars in C.ring227():
        if nm == name:
            return stars
    raise KeyError(name)


def law_of(it):
    kw = {}
    if it['group'] == 'fbp':
        kw['fresh_by_parents'] = True
    if it['group'] == 'dbt':
        kw['demand_before_takes'] = True
    return E.Law.from_base(it['base'], knot_law=it['knot_law'], take=it['rule'], choice=it['choice'], **kw)


def bounds_of(it):
    if it['group'] == 'ladder':
        return 2 * it['k'] + 4, 6000
    return 18, 4000


def grow(it, stars=None, clock=None):
    law = law_of(it)
    rounds, kb = bounds_of(it)
    S0 = E.from_stars(stars if stars is not None else stars_of(it['start']))
    return E.Run(S0, law, rounds=rounds, knot_bound=kb, clock=clock), law


def first_takes(A):
    """The first round at which any birth takes, any offshoot takes, and an offshoot of a ring member takes (dev 29)."""
    fb = fo = None
    for rec in A.records:
        for b in rec['births']:
            if b['rule_takes']:
                if fb is None:
                    fb = rec['round']
                if b['kind'] == 'offshoot' and fo is None:
                    fo = rec['round']
    return fb, fo


def ring_member_first_take(A, returns):
    S = A.S
    R0 = A.roster(0)
    ring = set(R0.members)
    whole = tuple(R0.members)
    for t in returns:
        Rt = A.roster(t)
        for Q in Rt.parts:
            if len(Q) == len(whole) and Se.same_parts(R0, whole, Rt, Q):
                ring |= set(Q)
                break
    for rec in A.records:
        for b in rec['births']:
            if b['kind'] == 'offshoot' and b['rule_takes'] and b['parents'][0] in ring:
                return rec['round']
    return None


def analyse(it, convention_swap=False):
    clock = E.Clock(600)
    t0 = time.process_time()
    out = dict(it)
    try:
        A, law = grow(it, clock=clock)
        out.update({'rounds': A.rounds_done, 'stop': A.stop, 'guard': A.guard, 'knots': A.S.n_knots})
        if A.stop == 'limit':
            out['unfinished'] = 'limit while growing'
            out['sec'] = round(time.process_time() - t0, 2)
            return out
        out['per_round'] = [[t, len(A.roster(t).members), len(A.roster(t).parts),
                             (A.records[t - 1]['n_births'] if t else 0), (A.records[t - 1]['n_knots'] if t else
                                                                           A.S.n_start)]
                            for t in range(A.rounds_done + 1)]
        out['stalled'] = any(r['stalled'] for r in A.records)
        out['jammed'] = any(r['jammed'] for r in A.records)
        out['stopped'] = any(r['stopped'] for r in A.records)
        k = None
        if it['rule'] and it['rule'].startswith('STEPS-') and ':' not in it['rule']:
            k = int(it['rule'][6:])
        conventions = ['least'] + (['greatest'] if convention_swap else [])
        for conv in conventions:
            for past in (True, False):
                key = ('past' if past else 'nopast') + ('' if conv == 'least' else '_greatest')
                ser, _ = Se.build_series(A, past, conv, clock=clock)
                Se.describe(ser)
                summ = Se.series_summary(ser)
                if conv == 'least':
                    # P2: ticks giving parts off or with copies against the start knots acting (and STEPS-k's bound)
                    worst = None
                    for s_ in ser:
                        if not s_['ticks']:
                            continue
                        n_st, n_k = Se.acting_knots(A, s_, k)
                        val = s_['ticks_off_or_copies']
                        cand = {'ticks_off_or_copies': val, 'start_knots_acting': n_st, 'k_bound': n_k if k else None,
                                't0': s_['t0'], 'size': s_['size']}
                        s_['acting'] = cand
                        if worst is None or val - n_st > worst['ticks_off_or_copies'] - worst['start_knots_acting']:
                            worst = cand
                    summ['p2_worst'] = worst
                    summ['p2_exceeds_start_bound'] = sum(1 for s_ in ser if s_.get('acting') and
                                                         s_['acting']['ticks_off_or_copies'] >
                                                         s_['acting']['start_knots_acting'])
                    if k:
                        summ['p2_exceeds_k_bound'] = sum(1 for s_ in ser if s_.get('acting') and
                                                         s_['acting']['ticks_off_or_copies'] >
                                                         s_['acting']['k_bound'])
                out[key] = summ
                if conv == 'least':
                    out[key + '_series'] = Se.compact([s_ for s_ in ser if s_['size'] >= 2 or s_['ticks_off']], 200)
                    out[key + '_endless'] = [[s_['t0'], s_['P0'], [tk['t'] for tk in s_['ticks']]] for s_ in ser
                                             if s_['size'] == 1 and s_['ticks']][:50]
                else:
                    out[key + '_series'] = Se.compact([s_ for s_ in ser if s_['size'] >= 2], 200)
        if it['start'] in RING_STARTS or it['group'] == 'ladder':
            rr = Se.start_roster_returns(A)
            out['start_roster_returns'] = rr
            out['first_take_round'], out['first_offshoot_take_round'] = first_takes(A)
            out['ring_member_offshoot_first_take'] = ring_member_first_take(A, rr)
        if it['group'] == 'main' and it['rule'] is None or it['rule'] in LAWS_OF_THE_COUNT or True:
            # per birth: births other than offshoots of start knots that gain a usable loose distinction (P2's count)
            gain = 0
            nb = 0
            for rec in A.records:
                for b in rec['births']:
                    nb += 1
                    if b['kind'] == 'offshoot' and len(A.S.parents[b['parents'][0]]) == 0:
                        continue
                    given = len(b['loose'])
                    if b['usable'] > given:
                        gain += 1
            out['births'] = nb
            out['births_gaining_outside_start_offshoots'] = gain
    except E.LimitReached:
        out['unfinished'] = 'limit while reading the series'
    except MemoryError:
        out['unfinished'] = 'memory cap'
    out['sec'] = round(time.process_time() - t0, 2)
    return out


def job(it):
    return analyse(it, convention_swap=(it['group'] == 'main' and it['rule'] is not None))


def _init():
    C.cap_memory()


def run_items(items, procs, out_name, log_every=200):
    path = C.out_path(out_name)
    done = 0
    t0 = time.time()
    secs = 0.0
    with gzip.open(path, 'wt') as f, mp.Pool(procs, initializer=_init, maxtasksperchild=25) as pool:
        for r in pool.imap_unordered(job, items, chunksize=1):
            f.write(json.dumps(r, sort_keys=True, default=C._default) + '\n')
            done += 1
            secs += r.get('sec', 0)
            if done % log_every == 0 or done == len(items):
                C.log('%s: %d/%d runs, %.0f s of process time, %.0f s wall' % (out_name, done, len(items), secs,
                                                                               time.time() - t0))
                f.flush()
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('what')
    ap.add_argument('--procs', type=int, default=6)
    ap.add_argument('--limit-items', type=int, default=0)
    ap.add_argument('--time-sample', type=int, default=0)
    ap.add_argument('--out', default=None)
    a = ap.parse_args()
    C.cap_memory()
    items = {'run1': items_run1, 'run2': items_run2, 'run3': items_run3}[a.what]()
    C.log('%s: %d registered items' % (a.what, len(items)))
    if a.time_sample:
        rng = random.Random(2026112505)
        items = rng.sample(items, a.time_sample)
    elif a.limit_items:
        items = items[:a.limit_items]
    out = a.out or ('%s.jsonl.gz' % a.what if not a.time_sample else '%s_timing_sample.jsonl.gz' % a.what)
    run_items(items, a.procs, out)


if __name__ == '__main__':
    main()
