"""Construction orders (TD 8.1): knots built from nothing in a supplied order, counted from the start renormalised."""
from __future__ import annotations

import json
import sys
import time
from multiprocessing import Pool

import lemma
import specs
import tc

S = tc.load_structures()
ORD = json.load(open(tc.REPO + '/research/TWO-COUNTINGS-20261125-001A/construction_orders.json'))


def knot_lists():
    """Index meanings of construction_orders.json's "about"."""
    KA, KB = specs.setting_knots()
    eleven = list(S['eleven (start)'])
    gain = list(S['smallest gain: part + rule-Q round 1'])
    assert gain[:7] == S['smallest gain: part']
    assert gain[7] == ('nae', ('y3', 's2', 'f')) and gain[8] == ('nae', ('y2', 'y1', 'g'))
    return {'eleven': (eleven, 11, 12), 'gain': (gain, 9, 10)}, KA, KB


def order_history(base, ia, ib, order, a, b, KA, KB):
    ks = {i: k for i, k in enumerate(base)}
    ks[ia] = KA[a][0]
    ks[ib] = KB[b][0]
    return tc.History([[]] + [[ks[i]] for i in order])


def in_class(base, ia, ib, order, KA, KB):
    """Both setting knots bring only their own fresh distinction, for both settings (TD 8.1)."""
    pos = {k: i for i, k in enumerate(order)}

    def held_before(i):
        out = set()
        for j in order[:pos[i]]:
            if j in (ia, ib):
                continue
            out |= set(base[j][1])
        return out
    # a setting knot may also find the other setting knot's distinctions earlier; take the union for both settings
    hA = held_before(ia) | (set(KB[0][0][1]) & set(KB[1][0][1]) if pos[ib] < pos[ia] else set())
    hB = held_before(ib) | (set(KA[0][0][1]) & set(KA[1][0][1]) if pos[ia] < pos[ib] else set())
    okA = all(set(KA[a][0][1]) - {'za'} <= hA for a in (0, 1))
    okB = all(set(KB[b][0][1]) - {'zb'} <= hB for b in (0, 1))
    return okA and okB, {'first setting knot': okA, 'second setting knot': okB}


def evaluate_order(job):
    tc.cap_memory()
    lst, oi, order = job
    bases, KA, KB = knot_lists()
    base, ia, ib = bases['eleven' if lst.startswith('eleven') else 'gain']
    P, kept = {}, {}
    Hs = {}
    for a in (0, 1):
        for b in (0, 1):
            H = order_history(base, ia, ib, order, a, b, KA, KB)
            W, k = tc.counting(H, 0)
            kept[(a, b)] = k
            P[(a, b)] = tc.joint(H, W, specs.REC_A, specs.REC_B) if W is not None else {}
            Hs[(a, b)] = H
    ev = lemma.evaluate(P, specs.REC_A, specs.REC_B)
    cls, detail = in_class(base, ia, ib, order, KA, KB)
    if cls:
        verdict = ('in the class, at 2, hidden' if ev['score_all'] == 2 and ev['hidden']
                   else 'in the class and not at 2 hidden (C5 fails)')
    else:
        verdict = 'outside the class'
    lost = {str(k): tc.fstr(1 - v) for k, v in kept.items()}
    return {'list': lst, 'index': oi, 'order': order, 'in class': cls, 'class detail': detail,
            'score_all': tc.fstr(ev['score_all']), 'score_parity': tc.fstr(ev['score_parity']),
            'score_parity_abs': tc.fstr(ev['score_parity_abs']),
            'change_first': tc.fstr(ev['change_first']), 'change_second': tc.fstr(ev['change_second']),
            'hidden': ev['hidden'], 'weight lost': lost,
            'weight lost equally across the setting pairs': len(set(kept.values())) == 1,
            'any weight lost': any(v != 1 for v in kept.values()), 'verdict': verdict}
