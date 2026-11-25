"""Run 4 (and the rule of run 6) of LEAST-RECORD-20261124-001A: rules stated and checked against every chosen place
(deviations.md, item 18).

Each rule reads only the extracted look at distance 1: the stamps of x and of the other holder y of the chosen place.
  GENERATION-MOD-3   y is a parent exactly when its stamp is one less than x's, modulo 3
  GENERATION         y is a parent exactly when its stamp is smaller than x's
  GENERATION-MOD-m   (m = 2 Delta + 1, run 6) y is a parent exactly when (x's stamp - y's stamp) mod m is in 1..Delta
Further rules, for other stamps where run 2 finds a rule that counts, are added in RULES with their statement.

    python -B lrec_rules.py             # writes artifacts/.../rules.json
"""
from __future__ import annotations

import json
import resource
import time
from collections import Counter, defaultdict

import pfh_common as PC
import pfh_look as LK
from pfh_classes import LawRun


def other(L):
    hs = L.holders[L.a]
    return hs[0] if hs[1] == L.x else hs[1]


def rule_mod3(L):
    return L.stamp[other(L)] == (L.stamp[L.x] - 1) % 3


def rule_gen(L):
    return L.stamp[other(L)] < L.stamp[L.x]


def make_rule_mod(m):
    delta = (m - 1) // 2

    def rule(L):
        return 1 <= (L.stamp[L.x] - L.stamp[other(L)]) % m <= delta
    rule.__doc__ = 'y is a parent exactly when (stamp(x) - stamp(y)) mod %d is between 1 and %d' % (m, delta)
    return rule


def _tables(L):
    mk = {}
    nb = {}
    for y in L.knots:
        U = B = S = 0
        N = []
        for e in L.kplaces[y]:
            m = L.marks[e]
            if m == 'U':
                U += 1
            elif m == 'B':
                B += 1
            else:
                S += 1
                hs = L.holders[e]
                if len(hs) == 2:
                    N.append(hs[0] if hs[1] == y else hs[1])
        mk[y] = (U, B, S)
        nb[y] = N
    return mk, nb


def _square(nb, x, y, z=None):
    for w in nb[y]:
        if w == x:
            continue
        for z2 in (nb[w] if z is None else [z]):
            if z2 in (x, y, w):
                continue
            if z2 in nb[w] and x in nb[z2]:
                return True
    return False


def rule_f1r_start(L, start_bit=lambda v: v == 1):
    """(FLOOR1, CANCEL-RETIRE), START-KNOT shown, distance 2.  The earlier study's rule for this law (its run 6), with
    its first test, which read a start knot from its number of places, replaced by the stamp:
      0. If x is a start knot, a is not a parent place; if y is and x is not, a is a parent place.
      1. If x is fresh (two usable places and one shared) or a join mark (three places, one loose and two shared),
         a is a parent place.
      2. Otherwise, if y is fresh or a join mark, a is not a parent place.
      3. Otherwise, if another neighbour j of x is a join mark, a is a parent place exactly when x - y - w - j - x is a
         cycle for some w.
      4. Otherwise a is not a parent place when x and y lie on a cycle of four knots; else it is a parent place exactly
         when some neighbour of y other than x is a join mark."""
    mk, nb = _tables(L)
    x = L.x
    y = other(L)
    if start_bit(L.stamp[x]):
        return False
    if start_bit(L.stamp[y]):
        return True

    def fresh(z):
        return mk[z] == (2, 0, 1)

    def join(z):
        return mk[z] in ((1, 0, 2), (0, 1, 2))
    if fresh(x) or join(x):
        return True
    if fresh(y) or join(y):
        return False
    J = [z for z in nb[x] if z != y and join(z)]
    if J:
        return any(_square(nb, x, y, j) for j in J)
    if _square(nb, x, y):
        return False
    return any(join(z) for z in nb[y] if z != x)


def rule_f1r_hcs(L):
    """The same rule with HAS-CHILD with START-KNOT shown (values 2 has-child + start): the start bit is the value
    modulo 2."""
    return rule_f1r_start(L, start_bit=lambda v: v % 2 == 1)


def _cycles(nb, x, y):
    cs = set()
    for w in nb[y]:
        if w == x:
            continue
        for z in nb[w]:
            if z in (x, y, w):
                continue
            if x in nb[z]:
                cs.add((w, z))
    return cs


def rule_floor1_parent_count(L):
    """FLOOR1 laws, PARENT-COUNT shown, distance 2.  p(z) is a knot's stamp (its number of parents).
      1. If p(x) = 0 (x is a start knot), a is not a parent place; if p(y) = 0, it is.
      2. If x holds a loose place (usable or barred), a is a parent place; if y does, it is not.
      3. If p(x) >= 2 (x is a join), a is a parent place exactly when x and y lie on a cycle of four knots.
      4. If p(y) >= 2, a is a parent place exactly when they do not.
      5. Otherwise (both have one parent): if they lie on a cycle of four x - y - w - z - x, a is a parent place exactly
         when some such z has p(z) >= 2; if not, exactly when no other neighbour of x has p >= 2."""
    mk, nb = _tables(L)
    x = L.x
    y = other(L)
    st = L.stamp
    if st[x] == 0:
        return False
    if st[y] == 0:
        return True
    if mk[x][0] + mk[x][1] > 0:
        return True
    if mk[y][0] + mk[y][1] > 0:
        return False
    cs = _cycles(nb, x, y)
    if st[x] >= 2:
        return bool(cs)
    if st[y] >= 2:
        return not cs
    if cs:
        return any(st[z] >= 2 for w, z in cs)
    return not any(st[z] >= 2 for z in nb[x] if z != y)


RULES_BY_LAW = {
    'F1R': {'START-KNOT': (2, rule_f1r_start, rule_f1r_start.__doc__),
            'HAS-CHILD+START-KNOT': (2, rule_f1r_hcs, rule_f1r_start.__doc__ + ' ' + rule_f1r_hcs.__doc__),
            'PARENT-COUNT': (2, rule_floor1_parent_count, rule_floor1_parent_count.__doc__)},
    'F1O': {'PARENT-COUNT': (2, rule_floor1_parent_count, rule_floor1_parent_count.__doc__)},
}


RULES = {
    'GENERATION-MOD-3': (1, rule_mod3, 'the other holder is a parent exactly when its stamp is one less, modulo 3'),
    'GENERATION': (1, rule_gen, 'the other holder is a parent exactly when its stamp is smaller'),
}


def check(lr, stamp, d, rule):
    lr.set_stamp(stamp)
    if not hasattr(lr, '_struct_stamped'):
        lr._struct_stamped = True
    res = defaultdict(lambda: {'places': 0, 'reproduced': 0, 'failures_by_kind': Counter(), 'failures': []})
    for rec in lr.structs:
        T = rec.T
        if rec.kind == 'serial':
            pops = ['P1', 'P1 serial']
        elif rec.kind == 'P2':
            pops = ['P2'] + (['P1', 'P1 reference'] if rec.in_p1 else [])
        else:
            pops = ['P3']
        tag = ' | holds' if rec.cond else ' | fails'
        pops = pops + [p + tag for p in pops]
        for k, (x, a) in enumerate(T.items):
            L = LK.extract(T, x, a, d, 'full')
            r = rule(L)
            truth = T.kinds[k] == 'P'
            for p in pops:
                q = res[p]
                q['places'] += 1
                if r == truth:
                    q['reproduced'] += 1
                else:
                    q['failures_by_kind'][T.kinds[k]] += 1
                    if len(q['failures']) < 10:
                        y = other(L)
                        q['failures'].append({'structure': rec.label, 'knot': x, 'distinction': a, 'kind': T.kinds[k],
                                              'other_holder': y, 'stamp_of_knot': L.stamp[x],
                                              'stamp_of_other_holder': L.stamp[y], 'generation_of_knot': T.gen[x],
                                              'generation_of_other_holder': T.gen[y], 'parents_of_knot': list(T.parents[x]),
                                              'parents_of_other_holder': list(T.parents[y]),
                                              'reference_knot': T.ref_id[x] if T.ref_id else x,
                                              'rule_says_parent_place': r})
    out = {}
    for p, q in res.items():
        q['failures_by_kind'] = dict(q['failures_by_kind'])
        q['all_reproduced'] = q['reproduced'] == q['places']
        out[p] = q
    return out


def main():
    resource.setrlimit(resource.RLIMIT_AS, (8 << 30, 8 << 30))
    PC.check_frozen()
    gens = json.loads((PC.OUT / 'generations.json').read_text())
    t0 = time.time()
    out = {'rules': {k: v[2] for k, v in RULES.items()}, 'by_law': {},
           'rules_by_law': {law: {k: v[2] for k, v in rs.items()} for law, rs in RULES_BY_LAW.items()}}
    for short in ('F1O', 'F1R', 'R3W', 'ORD') + PC.HOLD_LAWS:
        lr = LawRun(short, log=lambda *a: None)
        lr.build()
        rules = dict(RULES)
        rules.update(RULES_BY_LAW.get(short, {}))
        for key, m in gens['moduli_for_run_6'].items():
            if key.startswith(short + ' '):
                r = make_rule_mod(m)
                rules['GENERATION-MOD-%d' % m] = (1, r, r.__doc__)
                out['rules']['GENERATION-MOD-%d' % m] = r.__doc__
        law = {}
        for stamp, (d, rule, text) in rules.items():
            law[stamp] = {'distance': d, 'rule': text, 'populations': check(lr, stamp, d, rule)}
            print(short, stamp, {p: (q['reproduced'], q['places'], q['failures_by_kind'])
                                 for p, q in law[stamp]['populations'].items() if ' | ' in p}, flush=True)
        out['by_law'][short] = law
    out['seconds'] = round(time.time() - t0, 1)
    PC.write_json(PC.OUT / 'rules.json', out)


if __name__ == '__main__':
    main()
