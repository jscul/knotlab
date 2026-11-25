"""Setting tests: the four setting pairs' histories, every counting of the family, the scores, hiding, the lemma's
hypotheses (TD 9) in checkable form and the three-way verdict (claim, section 8, item 2).

A spec is a dict:
  name, pre (list of stages common to the four histories: S_0 .. S_s), KA {a: [knots]}, KB {b: [knots]},
  recA, recB (lists of distinction names),
  variants: list of {'label', 'extra': {(a, b): [knots of the setting stage that are no setting knot]},
                     'post': {(a, b): [later stages]}}  (default one variant with nothing),
  extra_side: 'A' or 'B' (with which side's setting knot the extra knots go in the mixed stages; default 'B').
"""
from __future__ import annotations

from collections import defaultdict
from fractions import Fraction as Fr

import tc

PAIRS = [(0, 0), (0, 1), (1, 0), (1, 1)]


def histories(spec, var, mode):
    """mode: 'one' (setting knots one stage), 'A' (A's setting knot first), 'B' (B's first)."""
    out = {}
    pre = spec['pre']
    side = spec.get('extra_side', 'B')
    for a, b in PAIRS:
        ex = var.get('extra', {}).get((a, b), [])
        post = var.get('post', {}).get((a, b), [])
        KA, KB = list(spec['KA'][a]), list(spec['KB'][b])
        if mode == 'one':
            st = list(pre) + [KA + KB + ex] + list(post)
        elif mode == 'A':
            st = list(pre) + ([KA + ex, KB] if side == 'A' else [KA, KB + ex]) + list(post)
        else:
            st = list(pre) + ([KB + ex, KA] if side == 'B' else [KB, KA + ex]) + list(post)
        out[(a, b)] = tc.History(st)
    return out


def tables(Hs, s, recA, recB):
    P, kept = {}, {}
    for ab, H in Hs.items():
        W, k = tc.counting(H, s if s >= 0 else H.t)
        kept[ab] = k
        P[ab] = tc.joint(H, W, recA, recB) if W is not None else {}
    return P, kept


def evaluate(P, recA, recB):
    ca, cb = tc.record_changes(P)
    return {'score_all': tc.score_all(P), 'score_parity': tc.score_parity(P, len(recA), len(recB)),
            'score_parity_abs': tc.score_parity(P, len(recA), len(recB), absval=True),
            'change_first': ca, 'change_second': cb, 'hidden': ca == 0 and cb == 0}


def kept_by_old(H, s, s_old):
    """The kept fraction of every allowed state o of S_{s_old} (s <= s_old): the sum over its final extensions w of
    prod_{j > s_old} 1/c_j(w); it does not depend on s."""
    import numpy as np
    if all(H.extends(j) for j in range(s_old + 1, H.t + 1)):
        return {int(x): Fr(1) for x in H.A[s_old]}      # nothing lost after s_old: every o keeps all its weight
    F = H.A[H.t]
    cm = H.cmat()
    den = np.ones(len(F), dtype=object)
    for j in range(s_old + 1, H.t + 1):
        den = den * cm[j - 1].astype(object)
    o = F & np.int64(H.mask_at(s_old))
    g = tc._group([o], den, Fr(1))
    return {int(x): g.get((int(x),), Fr(0)) for x in H.A[s_old]}


def hypotheses(spec, var, Hs, s_from):
    """TD 9 for counting from stage s_from <= s, s = the last pre stage (R 7)."""
    s = len(spec['pre']) - 1
    held = set()
    for st in spec['pre']:
        held |= set(tc.variables_of(st))
    fA = {a: set(tc.variables_of(spec['KA'][a])) - held for a in (0, 1)}
    fB = {b: set(tc.variables_of(spec['KB'][b])) - held for b in (0, 1)}
    vA = {a: set(tc.variables_of(spec['KA'][a])) for a in (0, 1)}
    vB = {b: set(tc.variables_of(spec['KB'][b])) for b in (0, 1)}
    res = {}
    fails = []
    res['h0'] = s_from <= s
    if not res['h0']:
        fails.append('h0')
    # h1'
    c1 = all((vA[a] - fA[a]) <= held for a in (0, 1)) and all((vB[b] - fB[b]) <= held for b in (0, 1))
    c2 = fA[0] == fA[1] and fB[0] == fB[1]
    c3 = all(not (fA[a] & vB[b]) and not (fB[b] & vA[a]) for a in (0, 1) for b in (0, 1))
    res['h1p'] = {'old places held in S_s': c1, 'same fresh for both settings': c2,
                  'fresh held by no knot of the other side': c3}
    if not (c1 and c2 and c3):
        fails.append('h1′')
    # loss at the setting stage and after; the lost-weight rule
    lost_setting = False
    lost_later = False
    kept_sets = {}
    rule_ok = True
    for ab, H in Hs.items():
        sst = s + 1
        if not H.extends(sst):
            lost_setting = True
        for j in range(sst + 1, H.t + 1):
            if not H.extends(j):
                lost_later = True
        ko = kept_by_old(H, s_from, s)
        if any(x not in (0, 1) for x in ko.values()):
            rule_ok = False
        kept_sets[ab] = frozenset(o for o, x in ko.items() if x == 1)
    if len(set(kept_sets.values())) > 1:
        rule_ok = False
    res['weight lost at the setting stage'] = lost_setting
    res['weight lost at a later stage'] = lost_later
    res['lost-weight rule'] = rule_ok
    res['h2'] = (not lost_setting) or rule_ok
    if not res['h2']:
        fails.append('h2')
    # h3'
    post_knots = {}
    for ab in PAIRS:
        ks = list(var.get('extra', {}).get(ab, []))
        for st in var.get('post', {}).get(ab, []):
            ks += st
        post_knots[ab] = [tc.as_knot(k) for k in ks]
    d1 = all(not (fA[a] & fB[b]) for a in (0, 1) for b in (0, 1))
    d2 = all(not (set(P) & fA[a] and set(P) & fB[b]) for (a, b) in PAIRS for _, P in post_knots[(a, b)])
    res['h3p'] = {'fresh sets disjoint': d1, 'no later knot holds fresh of both': d2}
    if not (d1 and d2):
        fails.append('h3′')
    # h4
    e1 = (not lost_later) or rule_ok
    recA, recB = set(spec['recA']), set(spec['recB'])
    e2 = recA <= (held | fA[0] | fA[1]) and recB <= (held | fB[0] | fB[1])
    res['h4'] = {'no later loss (or the lost-weight rule)': e1, 'records hold only S_s and own setting-fresh': e2}
    if not (e1 and e2):
        fails.append('h4')
    res['fails'] = fails
    res['met'] = not fails
    return res


def three_way(hyp, ev):
    if hyp['met']:
        if ev['score_all'] <= 2 and ev['score_parity'] <= 2 and ev['hidden'] and ev['score_all'] == 2:
            return 'hypotheses met and at most 2 (exactly 2 over all two-valued functions), both records hidden'
        return 'hypotheses met and a score above 2 or a record changed (the lemma or the engine is wrong)'
    return 'a hypothesis fails (%s), score %s' % (', '.join(hyp['fails']), tc.fstr(ev['score_all']))


def run_spec(spec, mixed=True, extra_marginals=None):
    """Every counting of the family for every variant; pooled rows when there are several variants."""
    variants = spec.get('variants') or [{'label': 'only'}]
    recA, recB = spec['recA'], spec['recB']
    s = len(spec['pre']) - 1
    out = {'name': spec['name'], 'variants': []}
    pooled_tables = defaultdict(list)    # counting -> [(P, nu_finish_weight)]
    for var in variants:
        Hs = histories(spec, var, 'one')
        rows = {}
        for sf in range(s + 1):
            P, kept = tables(Hs, sf, recA, recB)
            ev = evaluate(P, recA, recB)
            hyp = hypotheses(spec, var, Hs, sf)
            ev.update({'kept': {str(k): v for k, v in kept.items()}, 'hypotheses': hyp,
                       'verdict': three_way(hyp, ev)})
            name = 'from the start' if sf == 0 else 'from stage %d' % sf
            rows[name] = ev
            pooled_tables[name].append((P, None))
        P, kept = tables(Hs, -1, recA, recB)
        ev = evaluate(P, recA, recB)
        ev['kept'] = {str(k): v for k, v in kept.items()}
        rows['from the finish'] = ev
        sizes = {ab: len(H.A[H.t]) for ab, H in Hs.items()}
        pooled_tables['from the finish'].append((P, sizes))
        if mixed:
            for mode in ('A', 'B'):
                Hm = histories(spec, var, mode)
                P, kept = tables(Hm, s + 1, recA, recB)
                ev = evaluate(P, recA, recB)
                ev['kept'] = {str(k): v for k, v in kept.items()}
                rows['mixed stage (%s first)' % ('the first observer' if mode == 'A' else 'the second observer')] = ev
        info = {'allowed at the finish': {str(ab): n for ab, n in sizes.items()},
                'allowed at S_s': len(Hs[(0, 0)].A[s]), 'distinctions': len(Hs[(0, 0)].vars),
                'knots at the finish': {str(ab): len(H.knots()) for ab, H in Hs.items()}}
        if extra_marginals:
            info['marginals'] = {}
            for label, names in extra_marginals.items():
                for sf, cname in ((0, 'from the start'), (-1, 'from the finish')):
                    mv = {}
                    for ab, H in Hs.items():
                        W, _ = tc.counting(H, sf if sf >= 0 else H.t)
                        mv[ab] = tc.marginal(H, W, names)
                    ch = max(max(tc.tv(mv[(a, 0)], mv[(a, 1)]) for a in (0, 1)),
                             Fr(0))
                    chA = max(tc.tv(mv[(0, b)], mv[(1, b)]) for b in (0, 1))
                    info['marginals']['%s %s' % (label, cname)] = {
                        'change under the second observer\'s setting': ch,
                        'change under the first observer\'s setting': chA}
        out['variants'].append({'label': var.get('label', 'only'), 'rows': rows, 'info': info,
                                'finished': {str(ab): [tc.kstr(k) for k in H.knots()] for ab, H in Hs.items()}})
    if len(variants) > 1:
        pooled = {}
        n = len(variants)
        for name, lst in pooled_tables.items():
            P = {ab: defaultdict(Fr) for ab in PAIRS}
            if name == 'from the finish':
                # TD 3.5: each (history, state) once; and nu uniform per history
                for ab in PAIRS:
                    tot = sum(sz[ab] for _, sz in lst)
                    for Pv, sz in lst:
                        for k, x in Pv[ab].items():
                            P[ab][k] += x * Fr(sz[ab], tot)
                pooled['from the finish, pooled (each history and state once, TD 3.5)'] = evaluate(
                    {ab: dict(v) for ab, v in P.items()}, recA, recB)
                P = {ab: defaultdict(Fr) for ab in PAIRS}
                for Pv, _ in lst:
                    for ab in PAIRS:
                        for k, x in Pv[ab].items():
                            P[ab][k] += x / n
                pooled['from the finish, nu uniform over histories'] = evaluate(
                    {ab: dict(v) for ab, v in P.items()}, recA, recB)
            else:
                for Pv, _ in lst:
                    for ab in PAIRS:
                        for k, x in Pv[ab].items():
                            P[ab][k] += x / n
                pooled['%s, pooled (nu uniform over histories)' % name] = evaluate(
                    {ab: dict(v) for ab, v in P.items()}, recA, recB)
        out['pooled'] = pooled
    return out
