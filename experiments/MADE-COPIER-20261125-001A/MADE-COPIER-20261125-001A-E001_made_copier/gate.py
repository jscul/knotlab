"""Run G (the gate P0, the controls of the readings P14, the third-pattern starts of P2) and run R (P4).

usage: python -B gate.py fold|ties|same|controls|third|record
Writes gate_<part>.json to the artifact folder.
"""
import argparse
import itertools
import json
import os
import random
import sys
import time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common as C  # noqa: E402
import mc  # noqa: E402

pm, K, P = mc.pm, mc.K, mc.P


# --------------------------------------------------------------------------------------------- P0: the wiring
def part_fold(args):
    rows, bad = 0, []
    for name, stars in mc.STARTS['fold study starts'].items():
        for base in mc.BASES_COPY + mc.BASES_CAP3:
            for take in ('MET', 'STEPS-1'):
                for ch in mc.RULES:
                    for kl in ('nae', 'parity'):
                        law = mc.make_law(base, take, ch, kl)
                        a = mc.grow(pm.from_stars(stars), law, rounds=6)
                        b = pm.Run(pm.from_stars(stars), law, rounds=6, knot_bound=mc.KNOT_BOUND)
                        rows += 1
                        if a.rounds_done != b.rounds_done or a.stop != b.stop or any(
                                a.snap[t].places != b.snap[t].places or a.snap[t].parents != b.snap[t].parents or
                                a.snap[t].barred != b.snap[t].barred for t in range(a.rounds_done + 1)):
                            bad.append((name, base, take, ch, kl))
    out = {'runs': rows, 'mismatches': bad}
    C.write_json('gate_fold.json', out)
    C.log(out)


# ------------------------------------------------------------------------------------- P0: ties against brute force
def drawn_structures():
    """P, run G: random.Random('2026112505'): 2 to 7 knots of 3 to 5 places over 4 to 11 distinctions, unused
    distinctions dropped (the draw's procedure is this engine's own, R 17)."""
    rng = random.Random('2026112505')
    out = []
    for i in range(600):
        nk = rng.randint(2, 7)
        D = rng.randint(4, 11)
        stars = []
        for _ in range(nk):
            m = rng.randint(3, min(5, D))
            stars.append(sorted(rng.sample(range(D), m)))
        used = sorted({d for st in stars for d in st})
        ren = {d: j for j, d in enumerate(used)}
        out.append([[ren[d] for d in st] for st in stars])
    return out


def part_ties(args):
    agg = Counter()
    bad = []
    for i, stars in enumerate(drawn_structures()):
        S = pm.from_stars(stars)
        for kl in ('parity', 'nae'):
            br = mc.ties_brute(S, kl)
            T = mc.ties(S, kl, seed=i)
            agg['structures ' + kl] += 1
            if br is None:
                agg['no allowed state ' + kl] += 1
                if not T.unsat:
                    bad.append((i, kl, 'unsat differs'))
                continue
            mine = {frozenset(c) for c in T.classes}
            agg['classes ' + kl] += len(br['classes'])
            agg['frozen ' + kl] += len(br['frozen'])
            if mine != br['classes'] or T.frozen != br['frozen']:
                bad.append((i, kl, sorted(map(sorted, mine)), sorted(map(sorted, br['classes'])),
                            sorted(T.frozen), sorted(br['frozen'])))
            # signs (equal / unequal) against brute force
            allowed = mc._brute_allowed(S, kl)
            for c in T.classes:
                r = c[0]
                for m in c[1:]:
                    rel = {((x >> r) & 1) ^ ((x >> m) & 1) for x in allowed}
                    if rel != {T.sign[m] ^ T.sign[r]}:
                        bad.append((i, kl, 'sign', r, m))
    out = {'counts': dict(agg), 'mismatches': bad[:50], 'n_mismatches': len(bad)}
    C.write_json('gate_ties.json', out)
    C.log(out['counts'], 'mismatches', len(bad))


# ------------------------------------------------------------------------- P0: sameness and renamings, brute force
def same_brute(R1, part1, R2, part2):
    """Every one-to-one map of members: h, k and the family of maximal met sets carried onto the other."""
    if len(part1) != len(part2):
        return False
    m1 = [M for M in R1.maxsets if next(iter(M)) in set(part1)]
    m2 = {frozenset(M) for M in R2.maxsets if next(iter(M)) in set(part2)}
    if len(m1) != len(m2):
        return False
    for perm in itertools.permutations(part2):
        f = dict(zip(part1, perm))
        if any((R1.h[u], R1.k[u]) != (R2.h[f[u]], R2.k[f[u]]) for u in part1):
            continue
        if {frozenset(f[u] for u in M) for M in m1} == m2:
            return True
    return False


def part_same(args):
    agg = Counter()
    bad = []
    law = mc.make_law('COPY-LAW(OFFSHOOT)', 'MET', 'OLDEST', 'parity')
    for i, stars in enumerate(drawn_structures()):
        A = pm.Run(pm.from_stars(stars), law, rounds=1)
        if A.rounds_done < 1:
            continue
        S1 = A.snap[1]
        R1 = pm.roster_of(S1.copy(), law)
        made = [u for u in range(S1.n_knots) if S1.made[u] == 1]
        for pi, part in enumerate(R1.parts):
            if len(part) > 7:
                agg['parts too large for brute force'] += 1
                continue
            ref = mc.Reference(S1, R1, list(part), 0)
            for pj, other in enumerate(R1.parts):
                if len(other) > 7:
                    continue
                a = mc.same_as(ref, R1, other)
                b = same_brute(R1, list(part), R1, list(other))
                agg['sameness pairs'] += 1
                agg['same'] += a
                if a != b:
                    bad.append((i, 'same', pi, pj, a, b))
            # renamings of the part's knots among the knots made in that round
            pat = ref.built
            n, c = len(pat.knots), len(made)
            perms = 1
            for j in range(n):
                perms *= max(c - j, 0)
            if perms > 300000:
                agg['renaming cases too large for brute force'] += 1
                continue
            mine = mc.find_renamings(pat, S1, made, mode='count')
            br = mc.renamings_brute(pat, S1, made)
            agg['renaming cases'] += 1
            agg['renamings found'] += len(br)
            if {frozenset(x) for x in mine['sets']} != br:
                bad.append((i, 'renaming', pi, mine['sets'], sorted(map(sorted, br))))
    # positives by construction: the structure after round 1 with a renamed copy of a part's knots added
    pos = Counter()
    for i, stars in enumerate(drawn_structures()[:200]):
        A = pm.Run(pm.from_stars(stars), law, rounds=1)
        S1 = A.snap[1]
        R1 = pm.roster_of(S1.copy(), law)
        if not R1.parts:
            continue
        part = list(R1.parts[0])
        ref = mc.Reference(S1, R1, part, 0)
        T, newk = place_copy(S1, ref.knots, s_round=1)
        R2 = pm.roster_of(T.copy(), law)
        made_new = [u for u in range(T.n_knots) if T.kind[u] == 'placed']
        mine = mc.find_renamings(ref.built, T, made_new, mode='count')
        pos['copies placed'] += 1
        pos['found exactly one'] += (mine['n'] == 1)
        same_new = sum(1 for p_ in R2.parts if any(T.kind[u] == 'placed' for u in p_) and mc.same_as(ref, R2, p_))
        pos['part found'] += (same_new == 1)
    out = {'counts': dict(agg), 'positives': dict(pos), 'mismatches': bad[:40], 'n_mismatches': len(bad)}
    C.write_json('gate_same.json', out)
    C.log(out['counts'], out['positives'], 'mismatches', len(bad))


def place_copy(S_target, yknots, s_round, barred_from=None, pattern=None):
    """D 3.6 placed by hand: one new knot per pattern knot, one new distinction per place, held as the originals are;
    barred as the original was (in `barred_from`, default S); for each place with a holder outside the pattern's knots a
    further new knot holding it and two new distinctions, and a last new knot holding those two and one new barred
    distinction."""
    S = pattern if pattern is not None else S_target     # the pattern's knots as they were (D 2.4: after round s)
    B = barred_from or S
    T = S_target.copy()
    kset = set(yknots)
    pls = sorted(mc.places_of(S, yknots))
    newd = {}
    for d in pls:
        nd = len(T.holders)
        T.holders.append([])
        T.barred.append(bool(B.barred[d]))
        newd[d] = nd
    newk = {}
    for u in yknots:
        x = T.n_knots
        T.places.append([newd[d] for d in S.places[u]])
        T.parents.append(())
        T.made.append(s_round)
        T.kind.append('placed')
        for d in S.places[u]:
            T.holders[newd[d]].append(x)
        T.cand.add(x)
        newk[u] = x
    for d in pls:
        if any(w not in kset for w in S.holders[d]):
            a, b, c = len(T.holders), len(T.holders) + 1, len(T.holders) + 2
            for _ in range(3):
                T.holders.append([])
                T.barred.append(False)
            T.barred[c] = True
            f = T.n_knots
            T.places.append([newd[d], a, b])
            T.parents.append(())
            T.made.append(s_round)
            T.kind.append('placed')
            for z in (newd[d], a, b):
                T.holders[z].append(f)
            T.cand.add(f)
            g = T.n_knots
            T.places.append([a, b, c])
            T.parents.append(())
            T.made.append(s_round)
            T.kind.append('placed')
            for z in (a, b, c):
                T.holders[z].append(g)
            T.cand.add(g)
    T.span = pm.build_span(T)
    return T, newk


# ------------------------------------------------------------------------------- P14: the controls of the readings
def part_controls(args):
    out = {'two-knot': {}, 'placed': {}}
    want = mc.STARTS['counts for P3']['counts']
    ok = True
    for t3 in mc.T3:
        base = 'COPY-LAW(%s)' % mc.TS[t3]
        law = mc.make_law(base, None, 'OLDEST', 'parity')
        A = mc.grow(pm.from_stars([[0, 1, 2], [0, 3, 4]]), law, rounds=7)
        v = P.RunView(A)
        Y, s = [4, 5], 1
        ref = mc.Reference(A.snap[s], v.roster(s), Y, s)
        form_c, built_c = [], []
        for t in range(2, 8):
            S_t = A.snap[t]
            R_t = v.roster(t)
            desc = mc.descent_map(S_t, [2, 3], Y, s)
            form_c.append(len(mc.form_reading(ref, S_t, R_t, desc)))
            made = [u for u in range(S_t.n_knots) if S_t.made[u] > s]
            built_c.append(mc.find_renamings(ref.built, S_t, made, mode='count')['n'])
        key = 'two-knot|FLOOR1-%s' % mc.TS[t3]
        exp = want[key][2:8]
        good = form_c == exp and built_c == exp
        ok = ok and good
        out['two-knot'][base] = {'form': form_c, 'built (counting mode)': built_c, 'N(t) rounds 2-7': exp,
                                 'equal': good}
    for name in ('made-3', 'made-4', 'ystart-one-3', 'ystart-two-23'):
        d = mc.design(name)
        law = mc.make_law('CAP-3(OFFSHOOT)', 'MET', 'OLDEST', 'parity')
        A = mc.grow(d, law, rounds=3)
        v = P.RunView(A)
        S_s = A.snap[d.s]
        ref = mc.Reference(S_s, v.roster(d.s), d.Y, d.s, X=d.X)
        S3 = A.snap[3]
        R3 = pm.roster_of(S3.copy(), law)
        desc = mc.descent_map(S3, d.X, d.Y, d.s)
        f0 = len(mc.form_reading(ref, S3, R3, desc))
        made = [u for u in range(S3.n_knots) if S3.made[u] > d.s]
        b0 = mc.find_renamings(ref.built, S3, made, mode='count')['n']
        outside = [dd for dd in ref.built.places if ref.built.key[dd][1]]
        T, newk = place_copy(S3, ref.knots, s_round=3, pattern=S_s)
        RT = pm.roster_of(T.copy(), law)
        descT = mc.descent_map(T, d.X, d.Y, d.s)
        f1 = len(mc.form_reading(ref, T, RT, descT))
        madeT = [u for u in range(T.n_knots) if T.made[u] > d.s or T.kind[u] == 'placed']
        b1 = mc.find_renamings(ref.built, T, madeT, mode='count')['n']
        good = (f1 == f0 + 1 and b1 == b0 + 1 and len(outside) == 1)
        ok = ok and good
        out['placed'][name] = {'form before': f0, 'form after': f1, 'built before': b0, 'built after': b1,
                               'places with an outside holder': len(outside), 'one more each': good}
    out['P14'] = 'holds' if ok else 'fails'
    C.write_json('gate_controls.json', out)
    C.log(json.dumps(out)[:2000])


# ------------------------------------------------------------------------------- P2: the 60 third-pattern starts
def part_third(args):
    rows = []
    for ky in mc.KINDS:
        for kz in mc.KINDS:
            if kz == ky:
                continue
            for where in ('before', 'after'):
                d = mc.third(ky, kz, where)
                S = d.start()
                e = S.labels.index(1000)
                r = {'Y': ky, 'Z': kz, 'where': where, 'holders_of_e': len(S.holders[e])}
                for kl in ('parity', 'nae'):
                    T = mc.ties(S, kl)
                    r[kl] = {'classes': T.classes, 'frozen': sorted(T.frozen), 'unsat': T.unsat}
                rows.append(r)
    n_tie = sum(1 for r in rows for kl in ('parity', 'nae') if r[kl]['classes'] or r[kl]['frozen'])
    out = {'starts': len(rows), 'with a tie or a frozen distinction (start x knot law)': n_tie,
           'e has three holders in all': all(r['holders_of_e'] == 3 for r in rows), 'rows': rows}
    C.write_json('gate_third.json', out)
    C.log({k: v for k, v in out.items() if k != 'rows'})


# ------------------------------------------------------------------------------------------------ run R (P4)
def labelled_structures():
    """One to three knots of three or four places; each place loose or shared with exactly one place of another knot;
    knots and places ordered (P: 80,811 structures)."""
    for n in (1, 2, 3):
        for sizes in itertools.product((3, 4), repeat=n):
            owners = [k for k, sz in enumerate(sizes) for _ in range(sz)]
            npl = len(owners)

            def rec(i, pairing):
                if i == npl:
                    yield dict(pairing)
                    return
                if i in pairing:
                    yield from rec(i + 1, pairing)
                    return
                yield from rec(i + 1, pairing)          # place i loose
                for j in range(i + 1, npl):
                    if j not in pairing and owners[j] != owners[i]:
                        pairing[i] = j
                        pairing[j] = i
                        yield from rec(i + 1, pairing)
                        del pairing[i]
                        del pairing[j]
            for pairing in rec(0, {}):
                name = {}
                nxt = 0
                stars = [[] for _ in sizes]
                for i in range(npl):
                    if i in name:
                        d = name[i]
                    else:
                        d = nxt
                        nxt += 1
                        name[i] = d
                        if i in pairing:
                            name[pairing[i]] = d
                    stars[owners[i]].append(d)
                yield stars


def part_record(args):
    rec = json.load(open(os.path.join(mc.DATA, 'record_structures.json')))
    out = {}
    # parity, two holders
    agg = Counter()
    bad = []
    for i, st in enumerate(rec['parity, at most two holders']):
        S = pm.from_stars(st['knots'])
        T = mc.ties_parity(S)
        loose = {d for d in range(S.n_distinctions) if len(S.holders[d]) == 1}
        for c in T.classes:
            nl = sum(1 for d in c if d in loose)
            if len(c) >= 3:
                agg['tie classes with three or more members'] += 1
                agg['  of them, loose members'] += nl
            if nl >= 3:
                bad.append((i, 'a tie class with three loose members'))
            if nl >= 2 and len(loose) > 2:
                bad.append((i, 'two loose tied while a third loose exists'))
        agg['structures'] += 1
        for part in st['parts']:
            sub = [S.places[u] for u in part]
            Sp = pm.from_stars(sub)
            ends = [d for d in range(Sp.n_distinctions) if len(Sp.holders[d]) == 1]
            Tp = mc.ties_parity(Sp)
            agg['parts drawn'] += 1
            if Tp.frozen or len(ends) < 2:
                agg['parts with a frozen distinction or fewer than two ends'] += 1
                continue
            agg['parts read'] += 1
            if len(ends) == 2:
                agg['parts with exactly two ends'] += 1
                if not Tp.tied(ends[0], ends[1]):
                    bad.append((i, 'two ends not tied', part))
            else:
                agg['parts with three or more ends'] += 1
                if any(Tp.tied(a, b) for a, b in itertools.combinations(ends, 2)):
                    bad.append((i, 'two of three or more ends tied', part))
    out['parity'] = {'counts': dict(agg), 'violations': bad[:20], 'n_violations': len(bad)}
    # not-all-equal, two holders
    agg = Counter()
    bad = []
    for i, st in enumerate(rec['not-all-equal, at most two holders']):
        S = pm.from_stars(st['knots'])
        T = mc.ties_nae(S, seed=i)
        agg['drawn'] += 1
        if T.classes or T.unsat:
            bad.append((i, T.classes, T.unsat))
    n_lab = 0
    for stars in labelled_structures():
        n_lab += 1
        S = pm.from_stars(stars)
        T = mc.ties_nae(S, seed=n_lab)
        if T.classes or T.unsat:
            bad.append(('labelled', stars, T.classes, T.unsat))
    agg['labelled'] = n_lab
    out['nae'] = {'counts': dict(agg), 'violations': bad[:20], 'n_violations': len(bad)}
    # by hand
    hand = {}
    for name, st in rec['by hand'].items():
        S = pm.from_stars(st)
        r = {}
        for kl in ('parity', 'nae'):
            T = mc.ties(S, kl)
            kt = K.parity_test(S) if kl == 'parity' else None
            passes = (not kt['fail']) if kt else all(K.nae_direct(S, S.knots()).values())
            r[kl] = {'classes': T.classes, 'frozen': sorted(T.frozen), 'every knot passes': passes,
                     'loose': [d for d in range(S.n_distinctions) if len(S.holders[d]) == 1]}
        hand[name] = r
    # the counterexample's join: a knot taking 7 and 8 with one fresh distinction, not-all-equal
    ce = [k for k in rec['by hand'] if 'counterexample' in k][0]
    st = rec['by hand'][ce]
    S = pm.from_stars(st + [[7, 8, 9]])
    T = mc.ties_nae(S)
    hand['the counterexample with a join of 7 and 8 (fresh 9), not-all-equal'] = {
        'classes': T.classes, 'signs': {str(d): T.sign.get(d) for c in T.classes for d in c},
        '9 tied to 7': T.tied(9, 7)}
    out['by hand'] = hand
    fano = [k for k in rec['by hand'] if k.startswith('the Fano piece')][0]
    prec = [k for k in rec['by hand'] if 'precision' in k][0]
    three = [k for k in rec['by hand'] if 'three loose' in k][0]
    checks = {
        'parity cut statements': out['parity']['n_violations'] == 0,
        'not-all-equal: no tie with two holders': out['nae']['n_violations'] == 0,
        'Fano piece ties 2, 4, 5 under not-all-equal, all shared, every knot passing':
            [2, 4, 5] in hand[fano]['nae']['classes'] and not hand[fano]['nae']['loose'] and
            hand[fano]['nae']['every knot passes'],
        'counterexample: 7 and 8 tied (not-all-equal)': any(7 in c and 8 in c for c in hand[ce]['nae']['classes']),
        'counterexample: the join\'s fresh distinction tied to 7':
            hand['the counterexample with a join of 7 and 8 (fresh 9), not-all-equal']['9 tied to 7'],
        'precision example ties 0, 2, 9 (parity)': any(set(c) >= {0, 2, 9} for c in hand[prec]['parity']['classes']),
        'one value at three loose places under parity': any(set(c) >= {0, 3, 4} for c in
                                                             hand[three]['parity']['classes'])
        and hand[three]['parity']['every knot passes'] and not hand[three]['nae']['classes'],
    }
    out['checks'] = checks
    out['P4'] = 'holds' if all(checks.values()) else 'fails'
    C.write_json('gate_record.json', out)
    C.log(out['P4'], checks, out['parity']['counts'], out['nae']['counts'])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('part', choices=('fold', 'ties', 'same', 'controls', 'third', 'record'))
    args = ap.parse_args()
    C.cap_memory(6)
    {'fold': part_fold, 'ties': part_ties, 'same': part_same, 'controls': part_controls, 'third': part_third,
     'record': part_record}[args.part](args)


if __name__ == '__main__':
    main()
