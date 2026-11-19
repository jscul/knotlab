"""EXTEND-ROUND-20261119-001A: does a table isometry that keeps what the round reads extend one round?

What one complete round reads of an arrangement (the census's law, as in FRESH-COUNT's step and PARENT-RULE's Lemma 1):
- L, the live junctions (those holding a loose distinction), and each one's loose count;
- which live junctions meet each other;
- the family F of sets of live junctions that one junction meets all of (a candidate pair, a group, and "no junction meets them
  all" are read from F alone);
- nothing else: the implied test is "holds every loose distinction" in a connected arrangement (PARENT-RULE Lemma 2), and the
  fresh counts read only the new junctions' parent sets.
A table isometry phi keeps the reading when it carries the loose distinctions onto the loose distinctions and every live junction's
distinctions onto a live junction's (this defines psi on L), and psi carries F onto F.  Then the two rounds correspond: psi
carries each new junction's parent set onto one of the other round's, with the same fresh count.  The extension phi' sends each new
junction's taken distinctions and fresh distinctions to its counterpart's (loose distinctions of one junction are twins in the
table, so phi may be re-paired inside each live junction).  Question: is phi' an isometry of the next tables?
Pairs: PARENT-RULE's 1,034 static other-states pairs and GROW-SMALL's reached ones with both members at most 15 vertices.  Next
tables: by bonds (plib) when at most 15 vertices, else exact_table_v2 with no bound, under an alarm (undecided past it).
Run: .venv/bin/python -B extend.py -> extend.json beside the artifacts."""
import importlib.util
import json
import signal
import sys
from collections import Counter, defaultdict
from itertools import combinations
from multiprocessing import Pool
from pathlib import Path

from networkx.algorithms import isomorphism

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'experiments/PARENT-RULE-20261119-001B/PARENT-RULE-20261119-001B-E001_parent'))
import plib as L  # noqa: E402
import census_job as C  # noqa: E402  (the census's law)
_x = importlib.util.spec_from_file_location('xt2e', ROOT / 'experiments/CENSUS-READ-20261118-001A/CENSUS-READ-20261118-001A-E001_census/exact_table_v2.py')
X = importlib.util.module_from_spec(_x)
_x.loader.exec_module(X)
CAP_ISO = 20000
CAP_EXT = 50
LIMIT = 600


class Late(Exception):
    pass


def _late(s, f):
    raise Late()


def grow1(stars):
    P = C.S.from_junctions([sorted(s) for s in stars])
    res = P.step(C.S.gf2(C.F.fewest), None)
    if res is None or res['new'] == 0:
        return None
    return [frozenset(b) for b in P.bits_of]


def reading(stars):
    own = L.owners(stars)
    nb = L.neighbours(stars, own)
    live = L.live_set(stars, own)
    lv = set(live)
    fam = set()
    for w in range(len(stars)):
        m = frozenset(u for u in nb[w] if u in lv)
        if len(m) >= 2:
            fam.add(m)
    fmax = {s for s in fam if not any(s < t for t in fam)}
    loose = {u: frozenset(x for x in stars[u] if len(own[x]) == 1) for u in live}
    return live, loose, fmax


def full_table(stars):
    labels = sorted(L.owners(stars))
    if L.graph_of(stars)[0] <= 15:
        return L.table(stars)
    t = X.exact_table(stars, len(labels))
    return t, labels


def keeps_reading(phi, a, b, ra, rb):
    live_a, loose_a, fa = ra
    live_b, loose_b, fb = rb
    if {phi[x] for u in live_a for x in loose_a[u]} != {x for u in live_b for x in loose_b[u]}:
        return None
    star_b = {b[u]: u for u in live_b}
    psi = {}
    for u in live_a:
        img = frozenset(phi[x] for x in a[u])
        if img not in star_b:
            return None
        psi[u] = star_b[img]
    if {frozenset(psi[u] for u in s) for s in fa} != fb:
        return None
    return psi


def extension(phi, psi, a, b, a1, b1):
    """phi' on a1's distinctions, or None if the rounds do not correspond under psi."""
    na, nb = len(a), len(b)
    own_a, own_b = L.owners(a), L.owners(b)
    old_a, old_b = set(own_a), set(own_b)

    def new_junctions(base, grown, old):
        out = []
        for j in range(len(base), len(grown)):
            taken = sorted(x for x in grown[j] if x in old)
            fresh = sorted(x for x in grown[j] if x not in old)
            out.append((j, taken, fresh))
        return out
    nja, njb = new_junctions(a, a1, old_a), new_junctions(b, b1, old_b)
    if len(nja) != len(njb):
        return None
    by_parents = defaultdict(list)
    for j, taken, fresh in njb:
        key = (frozenset(own_b[x][0] for x in taken), len(fresh))
        by_parents[key].append((j, taken, fresh))
    phi2 = dict(phi)
    # re-pair loose distinctions inside each live junction to match the assignment
    used = defaultdict(list)
    for j, taken, fresh in nja:
        parents = [own_a[x][0] for x in taken]
        key = (frozenset(psi[u] for u in parents), len(fresh))
        if not by_parents.get(key):
            return None
        jb, takenb, freshb = by_parents[key].pop()
        pb = {own_b[x][0]: x for x in takenb}
        for x, u in zip(taken, parents):
            phi2[x] = pb[psi[u]]
        for x, y in zip(fresh, freshb):
            phi2[x] = y
    if sorted(phi2.values()) != sorted(set(L.owners(b1))):
        return None
    return phi2


def analyse(item):
    kind, A, B, meta = item
    a = [frozenset(s) for s in A]
    b = [frozenset(s) for s in B]
    out = {'kind': kind, 'meta': meta, 'junctions': [len(a), len(b)]}
    signal.signal(signal.SIGALRM, _late)
    signal.alarm(LIMIT)
    try:
        ta, la = full_table(a)
        tb, lb = full_table(b)
        ra, rb = reading(a), reading(b)
        ga, gb = L.coloured(ta, la), L.coloured(tb, lb)
        m = isomorphism.GraphMatcher(ga, gb, node_match=lambda x, y: x['k'] == y['k'], edge_match=lambda x, y: x['d'] == y['d'])
        a1, b1 = grow1(a), grow1(b)
        out['grows'] = [a1 is not None, b1 is not None]
        n = keeping = 0
        exts = Counter()
        t1 = None
        for phi in m.isomorphisms_iter():
            n += 1
            psi = keeps_reading(phi, a, b, ra, rb)
            if psi is not None:
                keeping += 1
                if a1 is not None and b1 is not None and sum(exts.values()) < CAP_EXT:
                    if t1 is None:
                        t1 = (full_table(a1), full_table(b1))
                    phi2 = extension(phi, psi, a, b, a1, b1)
                    if phi2 is None:
                        exts['rounds_do_not_correspond'] += 1
                    else:
                        (ta1, la1), (tb1, lb1) = t1
                        ok = all(ta1[(x, y)] == tb1[tuple(sorted((phi2[x], phi2[y])))] for (x, y) in ta1)
                        exts['extension_is_isometry' if ok else 'extension_not_isometry'] += 1
            if n >= CAP_ISO:
                out['capped'] = True
                break
        out.update({'isometries': n, 'keeping_reading': keeping, 'extensions': dict(exts)})
        if a1 is not None and b1 is not None:
            if t1 is None:
                t1 = (full_table(a1), full_table(b1))
            (ta1, la1), (tb1, lb1) = t1
            out['next_tables_isometric'] = len(la1) == len(lb1) and L.iso(L.coloured(ta1, la1), L.coloured(tb1, lb1))
            if out['next_tables_isometric']:
                # the advisor's split: does some isometry of the next tables carry the old distinctions onto the old ones?
                old_a, old_b = set(la), set(lb)
                m1 = isomorphism.GraphMatcher(L.coloured(ta1, la1), L.coloured(tb1, lb1), node_match=lambda x, y: x['k'] == y['k'],
                                              edge_match=lambda x, y: x['d'] == y['d'])
                k = 0
                out['next_isometry_respects_age'] = False
                for phi1 in m1.isomorphisms_iter():
                    k += 1
                    if {phi1[x] for x in old_a} == old_b:
                        out['next_isometry_respects_age'] = True
                        break
                    if k >= CAP_ISO:
                        out['next_isometry_age_capped'] = True
                        break
    except Late:
        out['undecided_late'] = True
    finally:
        signal.alarm(0)
    return out


def items():
    out = []
    sp = json.loads((ROOT / 'artifacts/PARENT-RULE-20261119-001B/PARENT-RULE-20261119-001B-E001_parent/static_pairs.json').read_text())
    for gi, g in enumerate(sp['other_states_groups']):
        ms = g['members']
        for i, j in combinations(range(len(ms)), 2):
            if ms[i]['state_group'] != ms[j]['state_group']:
                out.append(('static', ms[i]['stars'], ms[j]['stars'], {'group': gi, 'loose': [ms[i]['row']['loose'], ms[j]['row']['loose']]}))
    gp = json.loads((ROOT / 'artifacts/GROW-SMALL-20261119-001A/GROW-SMALL-20261119-001A-E001_grow/grow_pairs.json').read_text())
    origin = {tuple(map(tuple, p['starts'])): p['kind'] for p in
              json.loads((ROOT / 'artifacts/GROW-SMALL-20261119-001A/GROW-SMALL-20261119-001A-E001_grow/origin.json').read_text())['pairs']}
    for g in (x for x in gp['groups'] if x.get('other_states_collision')):
        sg = {i: i for i in range(g['classes'])}
        for rep, i, v, _ in g['tests']:
            if v == 'same':
                sg[i] = sg[rep]
        ms = g['members']
        for i, j in combinations(range(len(ms)), 2):
            if sg[i] != sg[j]:
                a, b = ms[i]['stars'], ms[j]['stars']
                if L.graph_of([frozenset(s) for s in a])[0] <= 15 and L.graph_of([frozenset(s) for s in b])[0] <= 15:
                    key = (tuple(ms[i]['prov'][0]), tuple(ms[j]['prov'][0]))
                    o = origin.get(key, origin.get(key[::-1], 'unknown'))
                    out.append(('reached ' + ('created' if o.startswith('created') else 'carried'), a, b, {'prov': [ms[i]['prov'][0], ms[j]['prov'][0]]}))
    return out


def main():
    its = items()
    with Pool(8) as pool:
        rows = pool.map(analyse, its, chunksize=1)
    s = defaultdict(Counter)
    for r in rows:
        k = r['kind']
        s[k]['pairs'] += 1
        if r.get('undecided_late'):
            s[k]['undecided_late'] += 1
            continue
        both = all(r['grows'])
        s[k]['both_grow'] += both
        s[k]['some_isometry_keeps_reading'] += r['keeping_reading'] > 0
        s[k]['both_grow_and_keeping'] += both and r['keeping_reading'] > 0
        for e, v in r['extensions'].items():
            s[k]['ext_' + e] += v
        s[k]['pairs_with_an_extension_failing'] += r['extensions'].get('extension_not_isometry', 0) > 0 or r['extensions'].get('rounds_do_not_correspond', 0) > 0
        if both:
            s[k]['next_isometric'] += bool(r.get('next_tables_isometric'))
            s[k]['next_isometric_with_keeping'] += bool(r.get('next_tables_isometric')) and r['keeping_reading'] > 0
            s[k]['next_isometric_without_keeping'] += bool(r.get('next_tables_isometric')) and r['keeping_reading'] == 0
            s[k]['next_parted_without_keeping'] += (not r.get('next_tables_isometric')) and r['keeping_reading'] == 0
            s[k]['next_parted_with_keeping'] += (not r.get('next_tables_isometric')) and r['keeping_reading'] > 0
            s[k]['next_isometric_age_respecting'] += bool(r.get('next_isometry_respects_age'))
    summary = {k: dict(v) for k, v in s.items()}
    dest = ROOT / 'artifacts/EXTEND-ROUND-20261119-001A/EXTEND-ROUND-20261119-001A-E001_extend'
    dest.mkdir(parents=True, exist_ok=True)
    (dest / 'extend.json').write_text(json.dumps({'summary': summary, 'rows': rows}, indent=1, default=str))
    print(json.dumps(summary, indent=1))


if __name__ == '__main__':
    main()
