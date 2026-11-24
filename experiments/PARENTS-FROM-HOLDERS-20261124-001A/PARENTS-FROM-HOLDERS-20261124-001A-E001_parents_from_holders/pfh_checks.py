"""Run 1: the three checks of the code, before any other run (pre-registration, "Runs (frozen)", item 1).

  (a) on 200 drawn small looks (at most 8 knots), alike by the code equals alike by trying every renaming;
  (b) the advisor's pair on the two-knot start under (FLOOR1, CANCEL-OFFSHOOT, RELEASE): confusable exactly for
      d <= R - 2, for R = 4 to 9;
  (c) a planted difference: one barred mark changed four steps from x is not seen at distances 1 to 3 and is seen
      from distance 4.

    python -B pfh_checks.py        # writes artifacts/.../checks.json; exit status 1 if a check fails
"""
from __future__ import annotations

import itertools
import json
import random
import sys
import time
from collections import Counter

import pfh_common as PC
import pfh_iso as ISO
import pfh_look as LK
from pfh_struct import Struct

E = PC.E


# ============================================================================== the code's verdict

def code_alike(LA, LB):
    """The code's verdict: the search of pfh_iso on the compressed forms, then the place-by-place check."""
    GA, iA = LK.compress(LA)
    GB, iB = LK.compress(LB)
    m = ISO.find_renaming(GA, GB)
    if m is None:
        return False, None
    km, dm = LK.full_renaming(LA, iA, LB, iB, m)
    ok, why = LK.check_renaming(LA, LB, km, dm)
    if not ok:
        raise AssertionError('a renaming of compressed forms did not extend: %s' % why)
    return True, (km, dm)


# ============================================================================== trying every renaming

def brute_alike(LA, LB):
    """Every one-to-one renaming of knots with x to x; for each, the distinctions can be renamed exactly when the
    multisets of (mark, images of holders, is a) agree.  Independent of pfh_iso and of the compressed form."""
    if LA.variant != LB.variant:
        return False
    if len(LA.knots) != len(LB.knots) or len(LA.marks) != len(LB.marks):
        return False
    sigB = Counter((LB.marks[f], tuple(sorted(LB.holders[f])), f == LB.a) for f in LB.marks)
    restA = [y for y in LA.knots if y != LA.x]
    restB = [y for y in LB.knots if y != LB.x]
    for perm in itertools.permutations(restB):
        phi = {LA.x: LB.x}
        phi.update(zip(restA, perm))
        if LA.variant == 'c2' and any(LA.kattr[y] != LB.kattr[phi[y]] for y in LA.knots):
            continue
        sigA = Counter((LA.marks[e], tuple(sorted(phi[h] for h in LA.holders[e])), e == LA.a) for e in LA.marks)
        if sigA == sigB:
            return True
    return False


# ============================================================================== small structures

def struct_from_stars(stars, barred_labels=(), parents=None):
    """A structure from stars (lists of distinction labels); every knot a start knot unless parents is given."""
    labels = sorted({d for s in stars for d in s})
    idx = {lab: i for i, lab in enumerate(labels)}
    places = [[idx[d] for d in s] for s in stars]
    holders = [[] for _ in labels]
    for u, P in enumerate(places):
        for d in P:
            holders[d].append(u)
    barred = [False] * len(labels)
    for lab in barred_labels:
        barred[idx[lab]] = True
    n = len(stars)
    if parents is None:
        parents = [()] * n
    is_start = [len(p) == 0 for p in parents]
    return Struct(places, holders, barred, [tuple(p) for p in parents], is_start)


def random_struct(rng):
    k = rng.randint(2, 8)
    stars = [[] for _ in range(k)]
    lab = 0
    # a connected backbone, then extra sharings
    for i in range(1, k):
        j = rng.randrange(i)
        stars[i].append(lab)
        stars[j].append(lab)
        lab += 1
    for i in range(k):
        for j in range(i + 1, k):
            if rng.random() < 0.25:
                for _ in range(1 if rng.random() < 0.8 else 2):
                    stars[i].append(lab)
                    stars[j].append(lab)
                    lab += 1
    barred = []
    for i in range(k):
        for _ in range(rng.randint(0, 3)):
            stars[i].append(lab)
            if rng.random() < 0.35:
                barred.append(lab)
            lab += 1
    return struct_from_stars(stars, barred)


def hand_pairs():
    """Hand-built pairs testing the two choices of the text, with the expected verdict.

    Choice 1: two knots both at distance d sharing a distinction are seen as one distinction; against the same knots each
    sharing with a different unseen knot: not alike.  Choice 2: two shared places of two rim knots leading to one unseen
    knot are not seen as leading to one knot; against two different unseen knots: alike."""
    out = []
    # x=0 shares with y1=1 and y2=2; y1,y2 share 12; each y has one loose
    s1 = [[0, 1, 90], [0, 12, 91], [1, 12, 92]]
    # y1 and y2 each share with an unseen knot z1, z2
    s2 = [[0, 1, 90], [0, 13, 91], [1, 14, 92], [13, 95], [14, 96]]
    A = struct_from_stars(s1)
    B = struct_from_stars(s2)
    out.append(('choice 1: shared by two rim knots vs two one-holder shared', A, 0, 0, B, 0, 0, 1, False))
    # choice 2: y1 and y2 each share with the same unseen z vs two different unseen knots
    s3 = [[0, 1, 90], [0, 13, 91], [1, 14, 92], [13, 14, 95]]
    C = struct_from_stars(s3)
    out.append(('choice 2: two rim places to one unseen knot vs to two', C, 0, 0, B, 0, 0, 1, True))
    # choice 1 at d = 2 with a longer chain
    s4 = [[0, 1], [0, 2, 3], [1, 4, 5], [2, 6, 7], [4, 6, 8], [3, 98], [5, 99], [7, 97], [8, 96]]
    s5 = [[0, 1], [0, 2, 3], [1, 4, 5], [2, 6, 7], [4, 9, 8], [3, 98], [5, 99], [7, 97], [8, 96], [6, 9]]
    D4 = struct_from_stars(s4)
    D5 = struct_from_stars(s5)
    out.append(('choice 1 at d = 2', D4, 0, D4.sh[0][0][0], D5, 0, D5.sh[0][0][0], 2, False))
    # a mark at the rim: U against B
    s6 = [[0, 1, 2], [0, 3, 4], [1, 5]]
    E6 = struct_from_stars(s6)
    F6 = struct_from_stars(s6, barred_labels=[4])
    out.append(('a mark at the rim, usable against barred', E6, 0, 0, F6, 0, 0, 1, False))
    out.append(('the same, without the usable-or-barred mark (C1)', E6, 0, 0, F6, 0, 0, 1, True))
    return out


# ============================================================================== check (a)

def draw_population_looks(rng, want):
    """Looks of at most 8 knots from small structures of the populations (every law), d from 1 to 3."""
    looks = []
    sources = []
    for start, fam, rc in PC.gate_pairs():
        S = PC.start_struct(start)
        law = PC.ref_law(fam)
        for t in range(1, 4):
            S, rec = E.round_step(S, law)
            sources.append(('%s %s round %d' % (start, PC.LAW_SHORT[fam], t), Struct.from_engine(S)))
            if rec['stopped']:
                break
    tries = 0
    while len(looks) < want and tries < 200000:
        tries += 1
        name, T = sources[rng.randrange(len(sources))]
        if not T.items:
            continue
        x, a = T.items[rng.randrange(len(T.items))]
        d = rng.randint(1, 3)
        v = LK.VARIANTS[rng.randrange(3)]
        L = LK.extract(T, x, a, d, v)
        if len(L.knots) <= 8:
            looks.append(('population: %s, place (%d, %d), d %d' % (name, x, a, d), T, L))
    return looks


def rename_struct(T, rng):
    """A copy of T with knots and distinctions renumbered at random; returns it and the map of knots."""
    n = T.n
    perm = list(range(n))
    rng.shuffle(perm)                       # old knot -> new knot
    inv = [0] * n
    for old, new in enumerate(perm):
        inv[new] = old
    keys = list(T.holders) if isinstance(T.holders, dict) else list(range(len(T.holders)))
    newids = list(range(1000, 1000 + len(keys)))
    rng.shuffle(newids)
    dm = dict(zip(keys, newids))
    places = [[dm[e] for e in T.places[inv[k]]] for k in range(n)]
    for P in places:
        rng.shuffle(P)
    holders = {dm[e]: [perm[h] for h in (T.holders[e])] for e in keys}
    barred = {dm[e]: bool(T.barred[e]) for e in keys}
    parents = [tuple(perm[p] for p in T.parents[inv[k]]) for k in range(n)]
    is_start = [T.is_start[inv[k]] for k in range(n)]
    return Struct(places, holders, barred, parents, is_start, strict=T.strict), perm, dm


def check_a(seed=20261124):
    rng = random.Random(seed)
    looks = draw_population_looks(rng, 80)
    # random small structures
    while len(looks) < 140:
        T = random_struct(rng)
        if not T.items:
            continue
        x, a = T.items[rng.randrange(len(T.items))]
        d = rng.randint(1, 3)
        v = LK.VARIANTS[rng.randrange(3)]
        L = LK.extract(T, x, a, d, v)
        if len(L.knots) <= 8:
            looks.append(('random structure, d %d' % d, T, L))
    base = list(looks)
    # renamed copies: knots and distinctions renumbered at random (alike to their source by construction)
    while len(looks) < 170:
        i = rng.randrange(len(base))
        desc, T, L = base[i]
        T2, perm, dm = rename_struct(T, rng)
        L2 = LK.extract(T2, perm[L.x], dm[L.a], L.d, L.variant)
        looks.append(('renamed copy of look %d (%s)' % (i, desc), T2, L2))
    # one detail changed: a mark at the rim, or a distinction between two rim knots split into two one-holder shared
    k = 0
    while len(looks) < 200 and k < 100000:
        k += 1
        desc, T, L = base[rng.randrange(len(base))]
        rim = [y for y in L.knots if L.dist[y] == L.d]
        if not rim:
            continue
        if rng.random() < 0.5:
            cand = [(y, e) for y in rim for e in T.Ul[y] + T.Bl[y]]
            if not cand:
                continue
            y, e = cand[rng.randrange(len(cand))]
            barred = dict(T.barred) if isinstance(T.barred, dict) else list(T.barred)
            barred[e] = not barred[e]
            T2 = Struct(T.places, T.holders, barred, T.parents, T.is_start, made=T.made, strict=T.strict)
            what = 'mark of %r at the rim changed' % (e,)
        else:
            cand = [e for y in rim for e, z in T.sh[y] if z in L.dist and L.dist[z] == L.d and y < z]
            if not cand:
                continue
            e = cand[rng.randrange(len(cand))]
            T2 = split_distinction(T, e)
            what = 'rim distinction %r split into two one-holder shared distinctions' % (e,)
        L2 = LK.extract(T2, L.x, L.a, L.d, L.variant)
        if len(L2.knots) <= 8:
            looks.append(('changed (%s) from: %s' % (what, desc), T2, L2))
    n = len(looks)
    pairs = 0
    agree = 0
    alike_pairs = 0
    alike_by_code = 0
    disagreements = []
    t0 = time.time()
    for i in range(n):
        for j in range(i + 1, n):
            LA = looks[i][2]
            LB = looks[j][2]
            if LA.variant != LB.variant:
                continue
            c, _ = code_alike(LA, LB)
            b = brute_alike(LA, LB)
            pairs += 1
            if c == b:
                agree += 1
            else:
                disagreements.append({'i': i, 'j': j, 'code': c, 'every_renaming': b,
                                      'looks': [looks[i][0], looks[j][0]]})
            alike_pairs += b
            alike_by_code += c
    hand = []
    for desc, A, xa, aa, B, xb, ab, d, expected in hand_pairs():
        variant = 'c1' if '(C1)' in desc else 'full'
        LA = LK.extract(A, xa, aa, d, variant)
        LB = LK.extract(B, xb, ab, d, variant)
        c, _ = code_alike(LA, LB)
        b = brute_alike(LA, LB)
        hand.append({'pair': desc, 'd': d, 'variant': variant, 'expected': expected, 'code': c, 'every_renaming': b,
                     'pass': c == b == expected})
    ok = (not disagreements) and all(h['pass'] for h in hand) and n == 200
    by_variant = Counter(L.variant for _, _, L in looks)
    sizes = Counter(len(L.knots) for _, _, L in looks)
    return {'pass': ok, 'n_looks': n, 'looks_by_kind': dict(by_variant), 'looks_by_knots': dict(sorted(sizes.items())),
            'sources': {'population': 80, 'random structures': 60, 'renamed copies': 30, 'one detail changed': n - 170},
            'pairs_compared': pairs, 'pairs_agreeing': agree, 'pairs_alike_by_every_renaming': alike_pairs,
            'pairs_alike_by_code': alike_by_code,
            'note': 'pairs of two different looks of the same kind (a look is not compared with itself)',
            'disagreements': disagreements[:50], 'hand_pairs': hand, 'seconds': round(time.time() - t0, 1)}


def split_distinction(T, e):
    """A copy of T in which the shared distinction e of holders (y, z) is replaced by two distinctions, each shared with a
    new knot that holds it and one loose distinction (so y and z each see a one-holder shared place in a look that does
    not reach the new knots)."""
    places = [list(P) for P in T.places]
    if isinstance(T.holders, dict):
        holders = {k: list(v) for k, v in T.holders.items()}
        barred = dict(T.barred)
        nxt = max(holders) + 1
    else:
        holders = {k: list(v) for k, v in enumerate(T.holders)}
        barred = dict(enumerate(T.barred))
        nxt = len(T.holders)
    y, z = holders[e]
    del holders[e]
    del barred[e]
    places[y].remove(e)
    places[z].remove(e)
    parents = list(T.parents)
    is_start = list(T.is_start)
    for h in (y, z):
        f = nxt
        g = nxt + 1
        nxt += 2
        w = len(places)
        places[h].append(f)
        places.append([f, g])
        holders[f] = [h, w]
        holders[g] = [w]
        barred[f] = False
        barred[g] = False
        parents.append(())
        is_start.append(True)
    return Struct(places, holders, barred, parents, is_start, strict=False)


# ============================================================================== check (b)

def check_b():
    fam = ('FLOOR1', 'CANCEL-OFFSHOOT')
    law = PC.ref_law(fam)
    S = PC.start_struct('TWO-KNOT')
    rows = []
    ok = True
    for R in range(1, 10):
        S, rec = E.round_step(S, law)
        if R < 4:
            continue
        T = Struct.from_engine(S)
        offs = sorted(x for x in range(T.n) if T.parents[x] == (0,) and T.made[x] == 1)
        if len(offs) != 2:
            raise AssertionError('start knot 0 does not have two round-1 offshoots')
        a1, a2 = offs
        js = [x for x in range(T.n) if set(T.parents[x]) == {a1, a2}]
        if len(js) != 1:
            raise AssertionError('no single join of a1 and a2')
        j = js[0]
        pA = [e for e, y in T.sh[a1] if y == 0]
        pj = [e for e, y in T.sh[a1] if y == j]
        if len(pA) != 1 or len(pj) != 1:
            raise AssertionError('places of a1 not found')
        pA, pj = pA[0], pj[0]
        kinds = (T.kinds[T.item_index[(a1, pA)]], T.kinds[T.item_index[(a1, pj)]])
        res = {}
        renamings = {}
        for v in LK.VARIANTS:
            alike_at = []
            for d in range(1, R + 2):
                LA = LK.extract(T, a1, pA, d, v)
                LB = LK.extract(T, a1, pj, d, v)
                c, rn = code_alike(LA, LB)
                if c:
                    alike_at.append(d)
                    if v == 'full' and d == R - 2:
                        renamings[d] = LK.renaming_record(LA, LB, *rn)
            res[v] = alike_at
        full = res['full']
        thr = max(full) if full else 0
        exact = full == list(range(1, R - 1))
        ok &= exact
        rows.append({'R': R, 'knots': T.n, 'a1': a1, 'a2': a2, 'A': 0, 'j': j, 'place_with_A': pA,
                     'place_with_j': pj, 'kinds': list(kinds), 'alike_at_full': full,
                     'alike_at_c1': res['c1'], 'alike_at_c2': res['c2'],
                     'threshold_found': thr, 'least_separating_distance': thr + 1,
                     'expected_threshold': R - 2, 'exact': exact,
                     'renaming_at_R_minus_2': renamings.get(R - 2)})
    return {'pass': ok, 'rows': rows}


# ============================================================================== check (c)

def check_c(seed=4, n_plants=60):
    rng = random.Random(seed)
    sources = []
    for start, fam, rc in PC.gate_pairs():
        S = PC.start_struct(start)
        law = PC.ref_law(fam)
        for t in range(1, 8):
            S, rec = E.round_step(S, law)
            if S.n_knots > 600 or rec['stopped']:
                break
        sources.append(('%s %s round %d' % (start, PC.LAW_SHORT[fam], S.round), Struct.from_engine(S), fam))
    plants = []
    tries = 0
    laws_seen = Counter()
    while len(plants) < n_plants and tries < 100000:
        tries += 1
        name, T, fam = sources[len(plants) % len(sources)] if tries < 40 else sources[rng.randrange(len(sources))]
        if not T.items:
            continue
        x, a = T.items[rng.randrange(len(T.items))]
        dist = T.dist_from(x, 4)
        far = [y for y, dy in dist.items() if dy == 4 and (T.Ul[y] or T.Bl[y])]
        if not far:
            continue
        y = far[rng.randrange(len(far))]
        loose = T.Ul[y] + T.Bl[y]
        e = loose[rng.randrange(len(loose))]
        barred = list(T.barred)
        barred[e] = not barred[e]
        T2 = Struct(T.places, T.holders, barred, T.parents, T.is_start, made=T.made)
        seen = []
        for d in range(1, 7):
            LA = LK.extract(T, x, a, d, 'full')
            LB = LK.extract(T2, x, a, d, 'full')
            c, _ = code_alike(LA, LB)
            seen.append(not c)
        ok = seen == [False, False, False, True, True, True]
        laws_seen[PC.LAW_SHORT[fam]] += 1
        plants.append({'structure': name, 'x': x, 'a': a, 'planted_knot': y, 'distinction': e,
                       'changed': 'usable to barred' if barred[e] else 'barred to usable',
                       'seen_at_d1_to_6': seen, 'pass': ok})
    return {'pass': len(plants) == n_plants and all(p['pass'] for p in plants), 'n_plants': len(plants),
            'plants_by_law': dict(laws_seen), 'plants': plants}


def main():
    PC.check_frozen()
    t0 = time.time()
    out = {'check_a': check_a(), 'check_b': check_b(), 'check_c': check_c()}
    out['pass'] = out['check_a']['pass'] and out['check_b']['pass'] and out['check_c']['pass']
    out['seconds'] = round(time.time() - t0, 1)
    out['search_stats'] = dict(ISO.STATS)
    PC.OUT.mkdir(parents=True, exist_ok=True)
    (PC.OUT / 'checks.json').write_text(json.dumps(out, indent=1, default=PC._default) + '\n')
    a = out['check_a']
    print('check (a):', 'PASS' if a['pass'] else 'FAIL', a['n_looks'], 'looks', a['pairs_compared'], 'pairs',
          a['pairs_alike_by_every_renaming'], 'alike', len(a['disagreements']), 'disagreements',
          [h['pass'] for h in a['hand_pairs']])
    b = out['check_b']
    print('check (b):', 'PASS' if b['pass'] else 'FAIL',
          [(r['R'], r['threshold_found'], r['expected_threshold']) for r in b['rows']])
    c = out['check_c']
    print('check (c):', 'PASS' if c['pass'] else 'FAIL', c['n_plants'], 'plants', c['plants_by_law'])
    print('all checks', 'PASS' if out['pass'] else 'FAIL', out['seconds'], 's')
    return 0 if out['pass'] else 1


if __name__ == '__main__':
    sys.exit(main())
