"""CREATED-PAIR-20261119-001A: every table isometry of GROW-SMALL's reached pairs with one table and other states.

For each of GROW-SMALL's 87 pairs (two members in different state groups) small enough for full tables by bonds (both at most 15
vertices: 64 pairs, the created one among them), every isometry of the full tables is enumerated directly (VF2 on the edge-coloured
complete graphs with Weisfeiler-Leman colours; no twin quotient, so isometries that break holder classes are included; cap
200,000).  For each isometry: how many junctions of one member it carries onto junctions of the other; whether it carries the loose
distinctions onto the loose distinctions; whether it also carries every junction holding a loose distinction onto a junction (the
growing end kept); whether it carries the last round's junctions (the live ones of an open stage; the
closing junction of a closed one) onto junctions of the other's last round; and, as a check, that it never carries the equation
space (other states).  A pair's origin (carried or created) is GROW-SMALL's origin.json.  E0: the loose counts and the sizes
of the loose twin classes of both members (if they differ, no bijection keeps the loose distinctions).
Run: .venv/bin/python -B isos.py -> isos.json beside the artifacts."""
import json
import sys
from collections import Counter
from itertools import combinations
from multiprocessing import Pool
from pathlib import Path

from networkx.algorithms import isomorphism

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PR = ROOT / 'experiments/PARENT-RULE-20261119-001B/PARENT-RULE-20261119-001B-E001_parent'
sys.path.insert(0, str(PR))
import plib as L  # noqa: E402
GS = ROOT / 'artifacts/GROW-SMALL-20261119-001A/GROW-SMALL-20261119-001A-E001_grow'
CAP = 200000


def pairs():
    d = json.loads((GS / 'grow_pairs.json').read_text())
    origin = {tuple(map(tuple, p['starts'])): p['kind'] for p in json.loads((GS / 'origin.json').read_text())['pairs']}
    out = []
    for g in (x for x in d['groups'] if x.get('other_states_collision')):
        sg = {i: i for i in range(g['classes'])}
        for rep, i, v, _ in g['tests']:
            if v == 'same':
                sg[i] = sg[rep]
        ms = g['members']
        for i, j in combinations(range(len(ms)), 2):
            if sg[i] != sg[j]:
                key = (tuple(ms[i]['prov'][0]), tuple(ms[j]['prov'][0]))
                out.append({'a': ms[i]['stars'], 'b': ms[j]['stars'], 'prov': [ms[i]['prov'][0], ms[j]['prov'][0]],
                            'origin': origin.get(key, origin.get(key[::-1], 'unknown'))})
    return out


def last_round(stars):
    live = L.live_set(stars)
    return set(live) if live else {len(stars) - 1}


def analyse(p):
    a = [frozenset(s) for s in p['a']]
    b = [frozenset(s) for s in p['b']]
    if L.graph_of(a)[0] > 15 or L.graph_of(b)[0] > 15:
        return {'origin': p['origin'], 'prov': p['prov'], 'skipped': 'more than 15 vertices'}
    ta, la = L.table(a)
    tb, lb = L.table(b)
    ga, gb = L.coloured(ta, la), L.coloured(tb, lb)
    own_a, own_b = L.owners(a), L.owners(b)
    loose_a = {x for x, js in own_a.items() if len(js) == 1}
    loose_b = {x for x, js in own_b.items() if len(js) == 1}
    bset = set(b)
    lr_a, lr_b = last_round(a), last_round(b)
    live_a = L.live_set(a)
    e0 = {'loose': [len(loose_a), len(loose_b)],
          'loose_classes': [sorted(Counter(own_a[x][0] for x in loose_a).values()), sorted(Counter(own_b[x][0] for x in loose_b).values())]}
    lr_b_stars = {b[j] for j in lr_b}
    idxb = {x: i for i, x in enumerate(lb)}
    wb = [sum(1 << idxb[x] for x in s) for s in b]
    rb = L.rank(wb)
    m = isomorphism.GraphMatcher(ga, gb, node_match=lambda x, y: x['k'] == y['k'], edge_match=lambda x, y: x['d'] == y['d'])
    n = 0
    best = 0
    c = Counter()
    for phi in m.isomorphisms_iter():
        n += 1
        img = [frozenset(phi[x] for x in s) for s in a]
        k = sum(1 for s in img if s in bset)
        best = max(best, k)
        c[f'junctions_kept_{k}'] += 1
        keeps_loose = {phi[x] for x in loose_a} == loose_b
        keeps_last = all(img[j] in lr_b_stars for j in lr_a)
        # the growing end: loose onto loose, and every junction holding a loose distinction carried onto a junction
        keeps_end = keeps_loose and all(img[j] in bset for j in live_a)
        c['keeps_growing_end'] += keeps_end
        c['keeps_loose'] += keeps_loose
        c['keeps_last_round'] += keeps_last
        c['keeps_loose_and_last_round'] += keeps_loose and keeps_last
        mapped = [sum(1 << idxb[phi[x]] for x in s) for s in a]
        c['carries_states'] += L.rank(wb + mapped) == rb and L.rank(mapped) == rb
        if n >= CAP:
            c['capped'] += 1
            break
    moved = None
    if best == len(a) - 1:
        # the one junction not carried, under some isometry keeping all the others: what moves
        for phi in m.isomorphisms_iter():
            img = [frozenset(phi[x] for x in s) for s in a]
            if sum(1 for s in img if s in bset) == best:
                j = next(j for j, s in enumerate(img) if s not in bset)
                other = next(s for s in b if s not in set(img))
                moved = {'junction': sorted(a[j]), 'image': sorted(img[j]), 'other_junction': sorted(other),
                         'in_last_round': j in lr_a, 'size': len(a[j]),
                         'out': sorted(img[j] - other), 'in': sorted(other - img[j])}
                break
    return {'origin': p['origin'], 'prov': p['prov'], 'junctions': len(a), 'distinctions': len(la), 'isometries': n,
            'most_junctions_kept': best, 'counts': dict(c), 'moved': moved, 'E0': e0}


def main():
    ps = pairs()
    with Pool(8) as pool:
        rows = pool.map(analyse, ps, chunksize=1)
    s = Counter()
    for r in rows:
        if 'skipped' in r:
            s['skipped'] += 1
            continue
        o = 'created' if r['origin'].startswith('created') else 'carried'
        s[f'{o}_pairs'] += 1
        s[f'{o}_some_isometry_keeps_loose'] += r['counts'].get('keeps_loose', 0) > 0
        s[f'{o}_some_isometry_keeps_last_round'] += r['counts'].get('keeps_last_round', 0) > 0
        s[f'{o}_some_isometry_keeps_both'] += r['counts'].get('keeps_loose_and_last_round', 0) > 0
        s[f'{o}_some_isometry_keeps_growing_end'] += r['counts'].get('keeps_growing_end', 0) > 0
        s[f'{o}_loose_counts_equal'] += r['E0']['loose'][0] == r['E0']['loose'][1]
        s[f'{o}_loose_classes_equal'] += r['E0']['loose_classes'][0] == r['E0']['loose_classes'][1]
        s[f'{o}_isometries'] += r['isometries']
        s[f'{o}_isometries_keeping_loose'] += r['counts'].get('keeps_loose', 0)
        s[f'{o}_all_but_one_junction_kept'] += r['most_junctions_kept'] == r['junctions'] - 1
        s[f'{o}_any_isometry_carries_states'] += r['counts'].get('carries_states', 0) > 0
        s[f'{o}_capped'] += r['counts'].get('capped', 0)
        if r['moved']:
            s[f"{o}_moved_junction_in_last_round"] += r['moved']['in_last_round']
    dest = ROOT / 'artifacts/CREATED-PAIR-20261119-001A/CREATED-PAIR-20261119-001A-E001_isos'
    dest.mkdir(parents=True, exist_ok=True)
    (dest / 'isos.json').write_text(json.dumps({'summary': dict(sorted(s.items())), 'rows': rows}, indent=1))
    print(json.dumps(dict(sorted(s.items())), indent=1))


if __name__ == '__main__':
    main()
