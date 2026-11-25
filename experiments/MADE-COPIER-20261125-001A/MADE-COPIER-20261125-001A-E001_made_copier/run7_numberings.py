"""Added after the freeze (deviations 51): every case that passes the registered renamings for its design, run under a
wider family of numberings of the start, the same law, rule and reading.

- a start of at most six distinctions: every order of its distinctions, each with the start knots as given and reversed;
- otherwise, of n distinctions: the n shifts of the order of its distinctions (shift i: the distinction at position i
  named first, the order otherwise kept cyclically), each as given or reversed, with the start knots as given or
  reversed (4n numberings).

X and Y are carried to the renumbered run by what they are: start knots by their place in the start's list, knots made
in round 1 by their parent and their order among that parent's offshoots.

usage: python -B run7_numberings.py
"""
import itertools
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common as C  # noqa: E402
import mc  # noqa: E402

pm, K, P = mc.pm, mc.K, mc.P


def numberings(stars):
    labels = sorted({l for k in stars for l in k})
    n = len(labels)
    out = []
    if n <= 6:
        for perm in itertools.permutations(range(n)):
            m = {labels[i]: perm[i] for i in range(n)}
            for kr in (False, True):
                out.append({'order': [labels[perm.index(j)] for j in range(n)], 'knots reversed': kr, 'map': m})
    else:
        for i in range(n):
            order = [labels[(i + j) % n] for j in range(n)]
            for rev in (False, True):
                od = list(reversed(order)) if rev else order
                m = {lab: j for j, lab in enumerate(od)}
                for kr in (False, True):
                    out.append({'shift': i, 'reversed': rev, 'knots reversed': kr, 'order': od, 'map': m})
    return out


def renumbered(stars, nb):
    st = [[nb['map'][l] for l in k] for k in stars]
    idx = list(range(len(stars)))
    if nb['knots reversed']:
        st = list(reversed(st))
        idx = list(reversed(idx))
    return st, idx          # idx[j] = the original start knot now at position j


def carry(pattern, s, A0, A1, idx):
    """The pattern's knots in run A1 (renumbered start): start knots by position; knots made in round 1 by parent and
    order among that parent's offshoots."""
    inv = {orig: j for j, orig in enumerate(idx)}
    out = []
    for u in pattern:
        if A0.snap[0].n_knots > u:
            out.append(inv[u])
            continue
        S0 = A0.snap[1]
        par = S0.parents[u][0]
        sib = [w for w in range(A0.snap[0].n_knots, S0.n_knots) if S0.parents[w] == (par,)]
        k = sib.index(u)
        S1 = A1.snap[1]
        sib1 = [w for w in range(A1.snap[0].n_knots, S1.n_knots) if S1.parents[w] == (inv[par],)]
        out.append(sib1[k])
    return out


def read(design, law, kl, reading, stars, nb=None):
    d0 = mc.design(design)
    if nb is None:
        st, idx = stars, list(range(len(stars)))
    else:
        st, idx = renumbered(stars, nb)
    A0 = mc.grow(pm.from_stars(stars), law)
    A = mc.grow(pm.from_stars(st), law)
    X = carry(d0.X, d0.s, A0, A, idx)
    Y = carry(d0.Y, d0.s, A0, A, idx)
    view = P.RunView(A)
    if A.rounds_done < d0.s + 1:
        return {'passes': False, 'note': 'ended before round s + 1'}
    ref = mc.Reference(A.snap[d0.s], view.roster(d0.s), Y, d0.s, X=X)
    rr = mc.readings_per_round(A, ref, X, Y, d0.s, kl, built=(reading == 'built'), values=(reading == 'values'),
                               form=(reading == 'form'))
    if reading == 'form':
        hit = mc.form_flags(rr)['two_by_X_some']
    elif reading == 'values':
        hit = mc.values_flags(rr)['Y_by_X_some']
    else:
        hit = mc.built_flags(rr)['two_by_X_some']
    named = tuple(tuple(sorted(k)) for k in pm.from_stars(st).places)
    return {'passes': hit is not None, 'round': hit, 'named start': named, 'knot fails': mc.knot_tests_A(A)['n_fails']}


def main():
    C.cap_memory(6)
    cases = []
    for x in C.read_jsonl('run5_cases.jsonl'):
        if x.get('survives every registered renaming'):
            cases.append(x['case'])
    out = {'cases passing the registered renamings': len(cases), 'rows': []}
    for c in cases:
        law = mc.make_law(c['base'], c['take'], c['choice'], c['knot_law'])
        stars = mc.STARTS['designs'][c['design']]['stars']
        base_row = read(c['design'], law, c['knot_law'], c['reading'], stars)
        nbs = numberings(stars)
        rows = []
        for nb in nbs:
            r = read(c['design'], law, c['knot_law'], c['reading'], stars, nb)
            r.update({k: v for k, v in nb.items() if k != 'map'})
            rows.append(r)
        distinct = len({r['named start'] for r in rows})
        distinct_pass = len({r['named start'] for r in rows if r['passes']})
        # where the names decide: by the position of each start distinction and by the knot order
        labels = sorted({l for k in stars for l in k})
        by = {}
        for lab in labels:
            by['position of label %s: passing' % lab] = dict(Counter(r['order'].index(lab) for r in rows
                                                                      if r['passes']))
            by['position of label %s: all' % lab] = dict(Counter(r['order'].index(lab) for r in rows))
        by['knots reversed: passing / all'] = [sum(1 for r in rows if r['passes'] and r['knots reversed']),
                                               sum(1 for r in rows if r['knots reversed'])]
        out['rows'].append({'case': c, 'as registered': base_row['passes'], 'numberings run': len(rows),
                            'distinct up to the start\'s symmetries (distinct named starts)': distinct,
                            'passes': sum(r['passes'] for r in rows),
                            'distinct named starts passing': distinct_pass,
                            'verdict': ('passes the registered renamings and every numbering run'
                                        if all(r['passes'] for r in rows) else 'under a supplied numbering'),
                            'where': by,
                            'numberings': [{k: v for k, v in r.items() if k != 'named start'} for r in rows]})
    C.write_json('run7_numberings.json', out)
    for r in out['rows']:
        C.log(r['case']['design'], r['case']['base'], r['case']['take'], r['case']['choice'], r['case']['knot_law'],
              r['numberings run'], r['passes'], r['verdict'])


if __name__ == '__main__':
    main()
