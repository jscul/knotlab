"""The study readings of FOLLOWS-THE-FORM-20261125-001A-E001 (FF 6 to FF 11), from the per-run records alone: nothing is
grown here.

  python -B ff_read.py --runset R1      # writes studies_R1.jsonl.gz and tables_R1.json

Per study: R*, L, runs read by round, the classes (own descent and wider record), the pairs of forms by first told
apart, after the first round, fates on the window, the count profile.  Per run set: the tables in the form of
disclosed.json's.
"""
import sys

sys.dont_write_bytecode = True

import argparse
import json
from collections import Counter, OrderedDict, defaultdict

import ff_core as C

FAMILY_ORDER = None


def load_runs(runset, n=8):
    recs = []
    for i in range(n):
        recs += list(C.read_jsonl(C.out_path('runs_%s_%dof%d.jsonl.gz' % (runset, i, n))))
    return recs


def seed_order():
    s = C.load_seeds()
    return {fam: [x['name'] for x in lst] for fam, lst in s['second'].items()}


def mk(seq, R):
    return tuple(tuple(tuple(e) for e in m) for m in seq[:R])


def partition(keys):
    """{name: key} -> list of classes (lists of names, in the given order), classes in order of first member."""
    by = OrderedDict()
    for name, k in keys.items():
        by.setdefault(k, []).append(name)
    return list(by.values())


def fate(own, first, R):
    """FF 7 on the window R-2, R-1, R."""
    if R < 4:
        return 'not read'
    x = own[R - 3:R]
    w = first[R - 3:R]
    if all(v == 0 for v in x):
        return 'ends, no births' if all(v == 0 for v in w) else 'ends, taken up'
    if x[0] == x[1] == x[2]:
        return 'steady'
    if x[0] < x[1] < x[2]:
        return 'grows'
    if x[0] > x[1] > x[2]:
        return 'shrinks'
    return 'other'


def is_function(profile, cls):
    """FF 11: no two forms with the same profile in different classes."""
    seen = {}
    for name, p in profile.items():
        c = cls[name]
        if p in seen and seen[p] != c:
            return False
        seen.setdefault(p, c)
    return True


def read_study(key, runs, order, seeds):
    """runs: {second name or None: record}.  order: the family's second seeds in data order."""
    runset, kl, fam, first, take, ration, treat = key
    assert set(runs) == set([None] + order), (key, len(runs))
    for r in runs.values():
        assert 'error' not in r, (key, r.get('error'))
    names = order
    rr = {n: runs[n]['rounds_read'] for n in [None] + names}
    Rs = min(rr.values())
    L = max(rr.values())
    Rmax = C.rounds_for(fam)
    read_by_round = [sum(1 for v in rr.values() if v >= t) for t in range(1, Rmax + 1)]
    own = {n: mk(runs[n]['make'], Rs) for n in [None] + names}
    wid = {n: mk(runs[n]['wider'], Rs) for n in [None] + names}
    label = {n: ('(none)' if n is None else n) for n in [None] + names}
    classes_all = partition(OrderedDict((label[n], own[n]) for n in [None] + names))
    forms_cls = partition(OrderedDict((n, own[n]) for n in names))
    wider_cls = partition(OrderedDict((n, wid[n]) for n in names))
    cls_of = {}
    for i, c in enumerate(forms_cls):
        for n in c:
            cls_of[n] = i
    bare_own = sum(1 for n in names if own[n] == own[None]) == 0
    in_bare = sum(1 for n in names if own[n] == own[None])
    # pairs of forms
    fta = Counter()
    after = Counter()
    pairs = []
    full_make = {n: [tuple(tuple(e) for e in m) for m in runs[n]['make']] for n in names}
    full_wider = {n: [tuple(tuple(e) for e in m) for m in runs[n]['wider']] for n in names}
    told_at_R = 0
    for i in range(len(names)):
        a = names[i]
        for j in range(i + 1, len(names)):
            b = names[j]
            r = min(rr[a], rr[b])
            t_first = None
            for t in range(1, r + 1):
                if full_make[a][t - 1] != full_make[b][t - 1]:
                    t_first = t
                    break
            if t_first is None:
                lab = 'never' if r == L else 'not read further'
            else:
                lab = str(t_first)
            fta[lab] += 1
            apart = cls_of[a] != cls_of[b]
            told_at_R += apart
            if t_first is not None and t_first >= 2:
                after['first told apart in round 2 or later'] += 1
                if full_wider[a][0] == full_wider[b][0]:
                    after['of those, the wider record of round 1 the same'] += 1
                if t_first >= 3 and full_wider[a][:2] == full_wider[b][:2]:
                    after['in round 3 or later with the wider records the same through round 2'] += 1
            pairs.append((a, b, lab, apart))
    after['pairs'] = len(pairs)
    after['told apart at R*'] = told_at_R
    for k in ('first told apart in round 2 or later', 'of those, the wider record of round 1 the same',
              'in round 3 or later with the wider records the same through round 2'):
        after[k] += 0
    fates = {n: fate(runs[n]['n_own'], runs[n]['n_of_first'], Rs) for n in names}
    held = {n: tuple(C.held_profile(seeds[fam][n])) for n in names}
    births = {n: tuple(runs[n]['sec_only'][:Rs]) for n in names}
    both = {n: (held[n], births[n]) for n in names}
    prof = {'the held knot': is_function(held, cls_of), "the second seed's births by round": is_function(births, cls_of),
            'both': is_function(both, cls_of)}
    return {
        'key': list(key), 'R*': Rs, 'L': L, 'runs read by round': read_by_round,
        'classes': classes_all, 'n_classes_forms': len(forms_cls), 'n_classes_wider': len(wider_cls),
        'classes_wider': wider_cls, 'bare_own_class': bare_own, 'forms_in_bare_class': in_bare,
        'every_form_in_bare_class': in_bare == len(names), 'n_forms': len(names),
        'first_told_apart': dict(fta), 'after': dict(after), 'fates': fates, 'profile_function': prof,
        'pairs': [[a, b, lab, int(ap)] for a, b, lab, ap in pairs],
        'stops': dict(Counter(str(runs[n]['stop']) for n in [None] + names)),
    }


def row_of(key):
    return '%s, %s' % (key[4], key[6])


def law_of(key):
    return '%s, %s, %s' % (key[4], key[5], key[6])


def depth_table(studies, seeds):
    """FF 9 on the chain studies: per law, pooled over first seeds: {cell: [told apart, pairs]}."""
    cells = ['depth 0', '1 against 2 knots', 'depth 1', '2 against 3 knots', 'depth 2', '3 against 4 knots',
             'depth 3', '4 against 5 knots', 'depth 4']
    out = OrderedDict()
    for st in studies:
        key = st['key']
        law = law_of(key)
        tab = out.setdefault(law, OrderedDict((c, [0, 0]) for c in cells))
        lc = {n: tuple(C.chain_counts(seeds['chains'][n])) for n in seeds['chains']}
        apart = {}
        for a, b, lab, ap in st['pairs']:
            apart[(a, b)] = ap
            apart[(b, a)] = ap
        names = list(lc)
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a, b = names[i], names[j]
                va, vb = lc[a], lc[b]
                cell = None
                if len(va) == len(vb):
                    diff = [k for k in range(len(va)) if va[k] != vb[k]]
                    if len(diff) == 1 and {va[diff[0]], vb[diff[0]]} == {2, 3}:
                        cell = 'depth %d' % diff[0]
                elif abs(len(va) - len(vb)) == 1:
                    s, l = (va, vb) if len(va) < len(vb) else (vb, va)
                    if l[:len(s)] == s:
                        cell = '%d against %d knots' % (len(s), len(l))
                if cell is not None:
                    tab[cell][0] += apart[(a, b)]
                    tab[cell][1] += 1
    return out


def tables(runset, studies, seeds):
    fams = sorted({s['key'][2] for s in studies})
    T = OrderedDict()
    rows = ['none, CANCEL-RETIRE', 'none, CANCEL-OFFSHOOT', 'none, CANCEL-WAIT', 'sole, CANCEL-RETIRE',
            'sole, CANCEL-OFFSHOOT', 'sole, CANCEL-WAIT']
    for fam in fams:
        ss = [s for s in studies if s['key'][2] == fam]
        if fam == 'chains':
            firsts = ''.join(sorted({s['key'][3] for s in ss}))
            T['depth, chains, first seeds %s to %s together (told apart / pairs)' % (firsts[0], firsts[-1])] = \
                depth_table(ss, seeds)
        fta = OrderedDict((r, Counter()) for r in rows)
        aft = OrderedDict((r, Counter()) for r in rows)
        fat = OrderedDict((r, Counter()) for r in rows)
        rst = OrderedDict((r, Counter()) for r in rows)
        prof = Counter()
        for s in ss:
            r = row_of(s['key'])
            fta[r].update(s['first_told_apart'])
            aft[r].update(s['after'])
            fat[r].update(Counter(s['fates'].values()))
            rst[r][str(s['R*'])] += 1
            for k, v in s['profile_function'].items():
                prof[k] += int(v)
            prof['studies'] += 1
        T['first told apart, %s' % fam] = {r: dict(v) for r, v in fta.items()}
        T.setdefault('after the first round', OrderedDict())[fam] = {r: dict(v) for r, v in aft.items()}
        T.setdefault('fates on the window', OrderedDict())[fam] = {r: dict(v) for r, v in fat.items()}
        T.setdefault('the count profile (studies in which the class is a function of it)', OrderedDict())[fam] = {
            'the held knot': prof['the held knot'], "the second seed's births by round":
                prof["the second seed's births by round"], 'both': prof['both'], 'studies': prof['studies']}
        T.setdefault('R*', OrderedDict())[fam] = {r: dict(v) for r, v in rst.items()}
        T.setdefault('wider record against own descent (studies)', OrderedDict())[fam] = dict(Counter(
            'more' if s['n_classes_wider'] > s['n_classes_forms'] else
            ('fewer' if s['n_classes_wider'] < s['n_classes_forms'] else 'equal') for s in ss))
        T.setdefault('classes among the forms (studies by number)', OrderedDict())[fam] = dict(sorted(Counter(
            s['n_classes_forms'] for s in ss).items()))
        T.setdefault('classes by the wider record (studies by number)', OrderedDict())[fam] = dict(sorted(Counter(
            s['n_classes_wider'] for s in ss).items()))
        T.setdefault('bare start a class of its own (studies)', OrderedDict())[fam] = [
            sum(s['bare_own_class'] for s in ss), len(ss)]
        T.setdefault('every form in the bare start\'s class (studies)', OrderedDict())[fam] = [
            sum(s['every_form_in_bare_class'] for s in ss), len(ss)]
    return T


def read_runset(runset):
    recs = load_runs(runset)
    order = seed_order()
    seeds = C.seeds_cached()['second']
    by = defaultdict(dict)
    for r in recs:
        key = (r['runset'], r['knot_law'], r['family'], r['first'], r['take'], r['ration'], r['treatment'])
        assert r['second'] not in by[key], ('duplicate run', key, r['second'])
        by[key][r['second']] = r
    # studies in the registered order
    reg = []
    seen = set()
    for r in C.runset_runs(runset):
        k = C.study_key(r)
        if k not in seen:
            seen.add(k)
            reg.append(k)
    assert set(reg) == set(by), (len(reg), len(by))
    studies = [read_study(k, by[k], order[k[2]], seeds) for k in reg]
    out = C.JsonLines(C.out_path('studies_%s.jsonl.gz' % runset))
    for s in studies:
        out.write(s)
    out.close()
    T = tables(runset, studies, seeds)
    with open(C.out_path('tables_%s.json' % runset), 'w') as f:
        json.dump(T, f, indent=1)
    C.log(runset, len(studies), 'studies;', len(recs), 'runs read')
    return studies, T, recs


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--runset', required=True)
    a = ap.parse_args()
    read_runset(a.runset)
