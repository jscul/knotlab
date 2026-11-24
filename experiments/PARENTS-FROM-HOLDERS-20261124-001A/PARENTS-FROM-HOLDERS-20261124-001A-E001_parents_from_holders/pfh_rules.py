"""Run 6: where a rule exists, the simplest description of the table of looks found by the code's author, checked
against every chosen place (pre-registration, "Runs (frozen)", item 6).

A rule here reads only the extracted look (pfh_look.FullLook, full look): the marks of its knots and which knots of the
look share a distinction.  It is checked on every place of every structure of the populations named, and its failures
are counted by kind; the guard count of each population is written beside it.

    python -B pfh_rules.py          # writes artifacts/.../rules.json
"""
from __future__ import annotations

import time
from collections import Counter

import pfh_common as PC
import pfh_look as LK
from pfh_classes import LawRun


def look_tables(L):
    """Marks (U, B, S) of every knot of the look and its neighbours in the look (knots it shares a distinction with)."""
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
    """Is there a cycle of four distinct knots x - y - w - z' - x in the look (with z' = z when z is given)?"""
    for w in nb[y]:
        if w == x:
            continue
        for z2 in (nb[w] if z is None else [z]):
            if z2 in (x, y, w):
                continue
            if z2 in nb[w] and x in nb[z2]:
                return True
    return False


def rule_F1R(L):
    """(FLOOR1, CANCEL-RETIRE, RELEASE), distance 2.  Words used: a knot is *fresh* when it holds two usable places and
    one shared place; a *join mark* when it holds three places, one of them loose (usable or barred) and two shared.
      1. If x does not hold exactly three places, a is not a parent place (x is a start knot).
      2. If x is fresh or a join mark, a is a parent place.
      3. Otherwise, if y is fresh or a join mark, a is not a parent place.
      4. Otherwise, if some other neighbour j of x is a join mark: a is a parent place exactly when x, y, some knot w
         and j form a cycle of four (x - y - w - j - x).
      5. Otherwise: a is not a parent place when x and y lie on a cycle of four; else a is a parent place exactly when
         some neighbour of y other than x is a join mark."""
    mk, nb = look_tables(L)
    x = L.x
    hs = L.holders[L.a]
    y = hs[0] if hs[1] == x else hs[1]

    def fresh(z):
        return mk[z] == (2, 0, 1)

    def join(z):
        return mk[z] in ((1, 0, 2), (0, 1, 2))
    if sum(mk[x]) != 3:
        return False
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


RULES = {
    'F1R': {'d': 2, 'rule': rule_F1R, 'text': rule_F1R.__doc__},
}


def check_rule(short, populations=('P2', 'P1 reference', 'P1 serial')):
    spec = RULES[short]
    d = spec['d']
    lr = LawRun(short, log=lambda *a: None)
    lr.build()
    out = {'law': PC.LAW_NAMES[lr.fam], 'distance': d, 'description': spec['text'], 'populations': {}}
    for pop in populations:
        good = 0
        bad = Counter()
        n = 0
        guard = 0
        examples = []
        for rec in lr.structs:
            if pop == 'P2' and rec.kind != 'P2':
                continue
            if pop == 'P1 reference' and not (rec.kind == 'P2' and rec.in_p1):
                continue
            if pop == 'P1 serial' and rec.kind != 'serial':
                continue
            T = rec.T
            ds = T.dist_start()
            dm = T.dist_member()
            for k, (x, a) in enumerate(T.items):
                n += 1
                if min(ds[x], dm[x] if dm[x] >= 0 else 10 ** 6) > d:
                    guard += 1
                L = LK.extract(T, x, a, d, 'full')
                r = spec['rule'](L)
                truth = T.kinds[k] == 'P'
                if r == truth:
                    good += 1
                else:
                    bad[T.kinds[k]] += 1
                    if len(examples) < 10:
                        examples.append({'structure': rec.label, 'knot': x, 'distinction': a, 'kind': T.kinds[k],
                                         'rule_says_parent_place': r})
        out['populations'][pop] = {'places': n, 'reproduced': good, 'failures_by_kind': dict(bad),
                                   'guard_count': guard, 'failure_examples': examples}
    return out


def serial_guard_counts():
    """The guard count of P1's serial structures per run (deviations.md, item 24): places whose look within d holds no
    start knot and no member, summed over the run's distinct states, for d = 1..6."""
    out = {}
    for short in ('F1O', 'F1R', 'R3W', 'ORD'):
        lr = LawRun(short, log=lambda *a: None)
        lr.build()
        per = {}
        for rec in lr.structs:
            if rec.kind != 'serial':
                continue
            T = rec.T
            ds = T.dist_start()
            dm = T.dist_member()
            row = per.setdefault(rec.run, {'states': 0, 'places': 0, 'guard_d1_to_6': [0] * 6})
            row['states'] += 1
            for (x, a) in T.items:
                row['places'] += 1
                g = min(ds[x], dm[x] if dm[x] >= 0 else 10 ** 6)
                for d in range(1, 7):
                    if g > d:
                        row['guard_d1_to_6'][d - 1] += 1
        out[short] = per
    return out


def main():
    PC.check_frozen()
    t0 = time.time()
    res = {'serial_guard_counts': serial_guard_counts()}
    for short in RULES:
        res[short] = check_rule(short)
        for pop, r in res[short]['populations'].items():
            print(short, pop, 'places', r['places'], 'reproduced', r['reproduced'], 'failures', r['failures_by_kind'],
                  'guard', r['guard_count'], flush=True)
    res['seconds'] = round(time.time() - t0, 1)
    PC.write_json(PC.OUT / 'rules.json', res)


if __name__ == '__main__':
    main()
