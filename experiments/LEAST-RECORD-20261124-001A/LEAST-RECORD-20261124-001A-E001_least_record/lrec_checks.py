"""Run 1 of LEAST-RECORD-20261124-001A: the four checks of the code before any other run (pre-registration, "Runs
(frozen)", item 1; deviations.md, items 13-16).

  (a) the earlier study's three checks still pass with the stamp NONE (and, as an addition, the comparison with the
      trial of every renaming on looks with stamps shown);
  (b) with a stamp that is the same on every knot, every class of looks is unchanged;
  (c) the five-knot structure: generations 0, 0, 1, 1, 2 and the kinds of its shared places as stated by hand;
  (d) a stamp changed on one knot four steps from the centre is unseen at distances 1 to 3 and seen from 4.

    python -B lrec_checks.py        # writes artifacts/.../checks.json; exit status 1 if a check fails
"""
from __future__ import annotations

import json
import random
import resource
import sys
import time
from collections import Counter

import pfh_checks as CK
import pfh_common as PC
import pfh_look as LK
from pfh_classes import LawRun
from pfh_report import population_tables
from pfh_struct import Struct

E = PC.E
EARLIER_ART = PC.ROOT / 'artifacts/PARENTS-FROM-HOLDERS-20261124-001A/PARENTS-FROM-HOLDERS-20261124-001A-E001_parents_from_holders'


# ============================================================================== (a)

def check_a():
    a = CK.check_a()
    b = CK.check_b()
    c = CK.check_c()
    return {'pass': a['pass'] and b['pass'] and c['pass'], 'earlier_check_a': a, 'earlier_check_b': b,
            'earlier_check_c': c}


def check_a_stamped(seed=7, n_looks=200):
    """Addition: the code against the trial of every renaming, with stamps shown."""
    rng = random.Random(seed)
    stamps = ['HAS-CHILD', 'START-KNOT', 'JOIN', 'GENERATION-MOD-2', 'GENERATION-MOD-3', 'GENERATION']
    sources = []
    for start, fam, rc in PC.gate_pairs():
        S = PC.start_struct(start)
        law = PC.ref_law(fam)
        for t in range(1, 4):
            S, rec = E.round_step(S, law)
            sources.append(('%s %s round %d' % (start, PC.LAW_SHORT[fam], t), S.copy()))
            if rec['stopped']:
                break
    looks = []
    tries = 0
    while len(looks) < n_looks and tries < 200000:
        tries += 1
        name, S = sources[rng.randrange(len(sources))]
        st = stamps[len(looks) % len(stamps)]
        T = Struct.from_engine(S)
        T.set_stamp(st)
        if not T.items:
            continue
        x, a = T.items[rng.randrange(len(T.items))]
        d = rng.randint(1, 3)
        if rng.random() < 0.25 and looks:
            # a renamed copy of an earlier look of the same stamp
            same = [L for L in looks if L[1] == st]
            if same:
                desc, st0, T0, L0 = same[rng.randrange(len(same))]
                T2, perm, dm = CK.rename_struct(T0, rng)
                T2.set_stamp(st)
                L = LK.extract(T2, perm[L0.x], dm[L0.a], L0.d, 'full')
                looks.append(('renamed copy of: ' + desc, st, T2, L))
                continue
        L = LK.extract(T, x, a, d, 'full')
        if len(L.knots) <= 8:
            looks.append(('%s, place (%d, %d), d %d' % (name, x, a, d), st, T, L))
    pairs = agree = alike = 0
    dis = []
    for i in range(len(looks)):
        for j in range(i + 1, len(looks)):
            if looks[i][1] != looks[j][1]:
                continue
            c, _ = CK.code_alike(looks[i][3], looks[j][3])
            b = CK.brute_alike(looks[i][3], looks[j][3])
            pairs += 1
            agree += (c == b)
            alike += b
            if c != b:
                dis.append([looks[i][0], looks[j][0], looks[i][1], c, b])
    return {'pass': not dis and len(looks) == n_looks, 'n_looks': len(looks),
            'looks_by_stamp': dict(Counter(L[1] for L in looks)), 'pairs_compared': pairs, 'pairs_agreeing': agree,
            'pairs_alike_by_every_renaming': alike, 'disagreements': dis[:20]}


# ============================================================================== (b)

def check_b(laws=('F1R', 'F1O')):
    out = {}
    ok = True
    for short in laws:
        lr = LawRun(short, log=lambda *a: None)
        lr.build()
        lr.compute_stamp('NONE')
        lr.compute_stamp('CONSTANT')
        same = {}
        for d in range(1, 7):
            same[d] = list(lr.cls[('NONE', d)]) == list(lr.cls[('CONSTANT', d)])
            ok &= same[d]
        # addition: NONE against the earlier study's published tables (full look)
        tabs = population_tables(lr, 'NONE')['tables']
        diffs = []
        for pop in ('P1', 'P2', 'P1P2'):
            old = json.loads((EARLIER_ART / ('%s_%s.json' % (short, pop))).read_text())['tables']
            for d in range(1, 7):
                o = old['full d=%d' % d][pop]
                nw = tabs['d=%d' % d][pop]
                for key in ('places', 'classes', 'mixed_classes', 'mixed_by_group', 'classes_child_and_start_only',
                            'guard_count'):
                    if o[key] != nw[key]:
                        diffs.append({'population': pop, 'd': d, 'key': key, 'earlier': o[key], 'now': nw[key]})
        out[short] = {'same_partition_by_distance': same, 'places': lr.n_items,
                      'classes_NONE_by_distance': {d: len(set(lr.cls[('NONE', d)])) for d in range(1, 7)},
                      'earlier_tables_reproduced': not diffs, 'differences_from_earlier_tables': diffs[:20]}
    return {'pass': ok, 'laws': out}


# ============================================================================== (c)

def check_c():
    stars = [[0, 1, 2], [0, 3, 4], [1, 5, 6], [2, 7, 8], [5, 7, 9]]
    names = ['A', 'B', 'a1', 'a2', 'J']
    parents = [(), (), (0,), (0,), (2, 3)]
    T = CK.struct_from_stars(stars, parents=parents)
    idx = {lab: i for i, lab in enumerate(sorted({d for s in stars for d in s}))}
    gen_ok = T.gen == [0, 0, 1, 1, 2]
    expected = {('A', 0): 'S', ('B', 0): 'S', ('A', 1): 'C', ('a1', 1): 'P', ('A', 2): 'C', ('a2', 2): 'P',
                ('a1', 5): 'C', ('J', 5): 'P', ('a2', 7): 'C', ('J', 7): 'P'}
    got = {}
    for k, (x, e) in enumerate(T.items):
        lab = [l for l, i in idx.items() if i == e][0]
        got[(names[x], lab)] = T.kinds[k]
    kinds_ok = got == expected
    stamps = {}
    for st in ('NOT-MEMBER', 'HAS-CHILD', 'JOIN', 'START-KNOT', 'GENERATION-MOD-2', 'GENERATION-MOD-3',
               'HAS-CHILD+START-KNOT', 'PARENT-COUNT', 'GENERATION'):
        T.set_stamp(st)
        stamps[st] = dict(zip(names, T.stamp))
    return {'pass': gen_ok and kinds_ok, 'generations': dict(zip(names, T.gen)), 'generations_as_stated': gen_ok,
            'kinds': {'%s %s' % k: v for k, v in sorted(got.items())},
            'kinds_as_stated': kinds_ok, 'stamps_of_the_five_knots': stamps}


# ============================================================================== (d)

def check_d(seed=5, n_plants=60):
    rng = random.Random(seed)
    stamps = ['GENERATION-MOD-3', 'GENERATION-MOD-2', 'HAS-CHILD', 'START-KNOT']
    sources = []
    for start, fam, rc in PC.gate_pairs():
        S = PC.start_struct(start)
        law = PC.ref_law(fam)
        for t in range(1, 8):
            S, rec = E.round_step(S, law)
            if S.n_knots > 600 or rec['stopped']:
                break
        sources.append(('%s %s round %d' % (start, PC.LAW_SHORT[fam], S.round), S.copy(), fam))
    plants = []
    tries = 0
    while len(plants) < n_plants and tries < 100000:
        tries += 1
        name, S, fam = sources[len(plants) % len(sources)] if tries < 60 else sources[rng.randrange(len(sources))]
        st = stamps[len(plants) % len(stamps)]
        T = Struct.from_engine(S)
        T.set_stamp(st)
        if not T.items:
            continue
        x, a = T.items[rng.randrange(len(T.items))]
        dist = T.dist_from(x, 4)
        far = [y for y, dy in dist.items() if dy == 4]
        if not far:
            continue
        y = far[rng.randrange(len(far))]
        T2 = Struct.from_engine(S)
        T2.set_stamp(st)
        new = list(T2.stamp)
        new[y] = (new[y] + 1) % 3 if st == 'GENERATION-MOD-3' else 1 - new[y]
        T2.stamp = new
        seen = []
        for d in range(1, 7):
            c, _ = CK.code_alike(LK.extract(T, x, a, d, 'full'), LK.extract(T2, x, a, d, 'full'))
            seen.append(not c)
        ok = seen == [False, False, False, True, True, True]
        plants.append({'structure': name, 'stamp': st, 'x': x, 'a': a, 'planted_knot': y,
                       'stamp_before': T.stamp[y], 'stamp_after': new[y], 'seen_at_d1_to_6': seen, 'pass': ok})
    return {'pass': len(plants) == n_plants and all(p['pass'] for p in plants), 'n_plants': len(plants),
            'plants_by_stamp': dict(Counter(p['stamp'] for p in plants)),
            'plants_by_law': dict(Counter(p['structure'].split()[1] for p in plants)), 'plants': plants}


def main():
    resource.setrlimit(resource.RLIMIT_AS, (8 << 30, 8 << 30))
    PC.check_frozen()
    t0 = time.time()
    out = {'check_a': check_a()}
    out['check_a_addition_stamped'] = check_a_stamped()
    out['check_c'] = check_c()
    out['check_d'] = check_d()
    out['check_b'] = check_b()
    out['pass'] = all(out[k]['pass'] for k in ('check_a', 'check_b', 'check_c', 'check_d'))
    out['seconds'] = round(time.time() - t0, 1)
    PC.OUT.mkdir(parents=True, exist_ok=True)
    (PC.OUT / 'checks.json').write_text(json.dumps(out, indent=1, default=PC._default) + '\n')
    a = out['check_a']
    print('check (a):', 'PASS' if a['pass'] else 'FAIL', 'earlier (a)', a['earlier_check_a']['pass'],
          a['earlier_check_a']['pairs_compared'], 'pairs', len(a['earlier_check_a']['disagreements']), 'disagreements;',
          'earlier (b) thresholds', [r['threshold_found'] for r in a['earlier_check_b']['rows']],
          'earlier (c)', a['earlier_check_c']['pass'])
    s = out['check_a_addition_stamped']
    print('check (a) addition, stamped:', 'PASS' if s['pass'] else 'FAIL', s['pairs_compared'], 'pairs',
          s['pairs_alike_by_every_renaming'], 'alike', len(s['disagreements']), 'disagreements')
    b = out['check_b']
    print('check (b):', 'PASS' if b['pass'] else 'FAIL',
          {k: (all(v['same_partition_by_distance'].values()), v['earlier_tables_reproduced']) for k, v in b['laws'].items()})
    c = out['check_c']
    print('check (c):', 'PASS' if c['pass'] else 'FAIL', c['generations'], c['kinds'])
    dd = out['check_d']
    print('check (d):', 'PASS' if dd['pass'] else 'FAIL', dd['n_plants'], dd['plants_by_stamp'], dd['plants_by_law'])
    print('all checks', 'PASS' if out['pass'] else 'FAIL', out['seconds'], 's')
    return 0 if out['pass'] else 1


if __name__ == '__main__':
    sys.exit(main())
