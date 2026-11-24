"""Self-checks of engine.py (part of gate G).

1. A second, deliberately naive implementation of one complete round, written again from the definitions: met sets read
   by scanning every knot of the structure, groups by enumerating every subset of members (no clique routine), maximal
   met sets never formed.  It is compared with the engine, exactly, on random small starts under random laws.
2. The group rule alone on random families of met sets, naive subset enumeration against the engine.
3. The knot tests against brute-force enumeration of allowed states: both parity methods (and a per-knot row
   elimination), the not-all-equal SAT test, and the parity extension test.
4. A planted failing knot (both parity methods fail it and agree) and a small not-all-equal case that fails.
5. Determinism: the same run twice gives identical output.

Writes artifacts/.../test_engine.json and prints one line per check.  Run:
    .venv/bin/python -B test_engine.py
"""
import itertools
import json
import os
import random
import sys
import time
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import engine as E  # noqa: E402

OUT = os.path.join(HERE, '..', '..', '..', 'artifacts', 'RING-IN-BALANCE-20261123-001A',
                   'RING-IN-BALANCE-20261123-001A-E001_ring')
OUT = os.path.normpath(OUT)

# =====================================================================================  naive implementation


def naive_from_structure(S):
    return {'places': [list(P) for P in S.places],
            'barred': {d for d in range(S.n_distinctions) if S.barred[d] and len(S.holders[d]) == 1},
            'parents': [tuple(p) for p in S.parents],
            'ndist': S.n_distinctions}


def n_holders(places):
    H = defaultdict(list)
    for u, P in enumerate(places):
        for d in P:
            H[d].append(u)
    return H


def n_usable(places, H, barred, u):
    return sorted(d for d in places[u] if len(H[d]) == 1 and d not in barred)


def n_metsets(places, members):
    """Every met set (not only the maximal ones): the members a knot meets, when at least two."""
    out = set()
    for w in range(len(places)):
        Pw = set(places[w])
        M = frozenset(m for m in members if m != w and Pw & set(places[m]))
        if len(M) >= 2:
            out.add(M)
    return out


def n_groups(members, msets):
    members = sorted(members)

    def joinable(a, b):
        return any(a in M and b in M for M in msets)
    fam = []
    for r in range(3, len(members) + 1):
        for Q in itertools.combinations(members, r):
            if all(joinable(a, b) for a, b in itertools.combinations(Q, 2)) and not any(set(Q) <= M for M in msets):
                fam.append(frozenset(Q))
    maximal = [Q for Q in fam if not any(Q < R for R in fam)]
    pairs = [frozenset(e) for e in itertools.combinations(members, 2)
             if joinable(*e) and not any(set(e) <= Q for Q in maximal)]
    return sorted(tuple(sorted(g)) for g in maximal + pairs)


def n_fresh(ration, p, D):
    q = max(D, 3 - p, 1)
    if ration == 'ORD':
        return q
    if ration.startswith('CAP-'):
        return min(q, int(ration.split('-')[1]))
    if ration.startswith('RATION-'):
        return max(int(ration.split('-')[1]), 3 - p)
    if ration == 'ONE-FEWER':
        return min(q, max(3 - p, 0, q - 1))
    if ration == 'FLOOR0':
        return max(3 - p, 0)
    if ration == 'FLOOR1':
        return max(3 - p, 1)
    raise ValueError(ration)


def naive_round(st, law):
    places = [list(P) for P in st['places']]
    barred = set(st['barred'])
    parents = list(st['parents'])
    ndist = st['ndist']
    H = n_holders(places)
    members = [u for u in range(len(places)) if n_usable(places, H, barred, u)]
    h = {u: len(n_usable(places, H, barred, u)) for u in members}
    msets = n_metsets(places, members)
    groups = n_groups(members, msets)
    owe = {u: sum(1 for g in groups if u in g) for u in members}
    short = sorted(u for u in members if owe[u] > h[u])
    total_loose = sum(1 for d in H if len(H[d]) == 1)
    info = {'groups': groups, 'short': short, 'births': [], 'closing': False, 'stalled': False}
    if law.treatment == 'STALL' and short:
        info['stalled'] = True
        return {'places': places, 'barred': barred, 'parents': parents, 'ndist': ndist}, info
    kept = [g for g in groups if not set(g) & set(short)]
    cancelled = [g for g in groups if set(g) & set(short)]
    give = {u: n_usable(places, H, barred, u) for u in members}
    newk = []   # (parents, taken)
    for g in kept:
        taken = []
        for u in g:
            taken.append(give[u].pop(0))
        newk.append((g, taken))
    for u in members:
        if u in short:
            if law.treatment == 'CANCEL-OFFSHOOT':
                for d in list(give[u]):
                    newk.append(((u,), [d]))
                give[u] = []
            elif law.treatment == 'CANCEL-RETIRE':
                barred |= set(give[u])
                give[u] = []
        else:
            nheld = sum(1 for g in cancelled if u in g) if law.release == 'HOLD' else 0
            rest = give[u][nheld:]
            if law.no_offshoot:
                barred |= set(rest)
            else:
                for d in rest:
                    newk.append(((u,), [d]))
    first_new = len(places)
    for g, taken in newk:
        places.append(list(taken))
        parents.append(tuple(g))
    H2 = n_holders(places)
    new_ids = list(range(first_new, len(places)))
    old_left = [u for u in members if n_usable(places, H2, barred, u)]
    dmembers = new_ids + old_left
    dgroups = n_groups(dmembers, n_metsets(places, dmembers))
    closing = law.knot_law == 'parity' and len(newk) == 1 and len(newk[0][1]) == total_loose
    info['closing'] = closing
    for x in new_ids:
        p = len(parents[x])
        D = sum(1 for g in dgroups if x in g)
        f = 0 if closing else n_fresh(law.ration, p, D)
        nu = min(f, D) if law.fillers else f
        for i in range(f):
            places[x].append(ndist)
            if i >= nu:
                barred.add(ndist)
            ndist += 1
        info['births'].append((x, tuple(parents[x]), D, f, nu))
    return {'places': places, 'barred': barred, 'parents': parents, 'ndist': ndist}, info


# ===========================================================================================  random inputs

def random_stars(rng, nmax=6, loose_max=3):
    n = rng.randint(2, nmax)
    stars = [[] for _ in range(n)]
    d = 0
    for _ in range(rng.randint(n - 1, 2 * n)):
        a, b = rng.sample(range(n), 2)
        stars[a].append(d)
        stars[b].append(d)
        d += 1
    for u in range(n):
        for _ in range(rng.randint(0, loose_max)):
            stars[u].append(d)
            d += 1
        while len(stars[u]) < 3:
            stars[u].append(d)
            d += 1
    return stars


RATIONS = ['ORD', 'ONE-FEWER', 'FLOOR0', 'FLOOR1', 'RATION-2', 'RATION-3', 'RATION-4', 'CAP-2', 'CAP-3', 'CAP-4']


def random_law(rng):
    t = rng.choice(E.TREATMENTS)
    no = rng.random() < 0.25 and t != 'CANCEL-OFFSHOOT'
    return E.Law(rng.choice(RATIONS), t, rng.choice(E.RELEASES), no_offshoot=no, fillers=rng.random() < 0.3,
                 knot_law=rng.choice(E.KNOT_LAWS))


# ===================================================================================  brute-force knot test

def brute_allowed(S, law):
    nd = S.n_distinctions
    out = []
    for bits in range(1 << nd):
        ok = True
        for P in S.places:
            vals = [(bits >> d) & 1 for d in P]
            if law == 'parity':
                if sum(vals) % 2:
                    ok = False
                    break
            else:
                if all(vals) or not any(vals):
                    ok = False
                    break
        if ok:
            out.append(bits)
    return out


def brute_knot_pass(S, law):
    allowed = brute_allowed(S, law)
    res = []
    for P in S.places:
        pr = {tuple((b >> d) & 1 for d in P) for b in allowed}
        if law == 'parity':
            want = {t for t in itertools.product((0, 1), repeat=len(P)) if sum(t) % 2 == 0}
        else:
            want = {t for t in itertools.product((0, 1), repeat=len(P)) if 0 < sum(t) < len(P)}
        res.append(pr == want)
    return res


def brute_extends(before, after):
    A0 = set(brute_allowed(before, 'parity'))
    mask = (1 << before.n_distinctions) - 1
    A1 = {b & mask for b in brute_allowed(after, 'parity')}
    return A0 == A1


# ===================================================================================================  checks

RESULTS = {}


def report(name, ok, **info):
    RESULTS[name] = dict(ok=bool(ok), **info)
    print('%-58s %s  %s' % (name, 'PASS' if ok else 'FAIL', json.dumps(info, sort_keys=True)[:200]))


def check_group_rule(rng, trials=3000):
    bad = 0
    for _ in range(trials):
        m = rng.randint(2, 9)
        members = list(range(m))
        msets = set()
        for _ in range(rng.randint(1, 7)):
            k = rng.randint(2, min(m, 4))
            msets.add(frozenset(rng.sample(members, k)))
        sc = {M: [i] for i, M in enumerate(sorted(msets, key=sorted))}
        maxsets, _ = E.maximal_sets(sc)
        if E.groups_from(members, maxsets) != n_groups(members, msets):
            bad += 1
    report('group rule vs subset enumeration (random met-set families)', bad == 0, trials=trials, mismatches=bad)


def struct_equal(S, st):
    if [list(P) for P in S.places] != st['places']:
        return 'places'
    if [tuple(p) for p in S.parents] != list(st['parents']):
        return 'parents'
    b = {d for d in range(S.n_distinctions) if S.barred[d] and len(S.holders[d]) == 1}
    if b != st['barred']:
        return 'barred'
    if S.n_distinctions != st['ndist']:
        return 'ndist'
    return None


def check_rounds_vs_naive(rng, trials=1500, rounds=3, max_members=11):
    compared = 0
    bad = []
    laws_seen = set()
    for trial in range(trials):
        if trial % 5 == 0:
            n = rng.randint(2, 6)
            a = rng.randint(1, 4)
            start = rng.choice([E.ring(n, a), E.d2(n, min(a, 2)), E.dw(n, min(a, 2))]) if n <= 4 else E.ring(n, a)
        else:
            start = E.from_stars(random_stars(rng))
        law = random_law(rng)
        S = start.copy()
        st = naive_from_structure(S)
        for r in range(rounds):
            if len(E.live_members(S)) > max_members:
                break
            S_next, rec = E.round_step(S, law)
            persisting = sum(1 for (u, _, _) in E.live_members(S) if S_next.hk(u)[0] > 0)
            if rec['n_births'] + persisting > max_members + 2:
                break     # the naive subset enumeration of the demand roster would be too large
            S = S_next
            st, info = naive_round(st, law)
            compared += 1
            laws_seen.add(law.name())
            why = struct_equal(S, st)
            eb = [(b['id'], tuple(b['parents']), b['D'], b['f'], b['usable']) for b in rec['births']]
            if why is None and eb != info['births']:
                why = 'births'
            if why is None and [tuple(g) for g in rec['groups']] != info['groups']:
                why = 'groups'
            if why is None and (rec['short'] != info['short'] or rec['closing'] != info['closing']
                                or rec['stalled'] != info['stalled']):
                why = 'short/closing/stall'
            if why is not None:
                bad.append({'trial': trial, 'round': r + 1, 'law': law.name(), 'why': why})
                break
            S.check()
    report('one full round vs naive implementation (random starts, laws)', not bad,
           rounds_compared=compared, distinct_laws=len(laws_seen), mismatches=bad[:5])


def check_named_vs_naive():
    cases = [(E.ring(5, 3), E.TWO_ADDED, 3), (E.ring(5, 3), E.THREE_ADDED, 4), (E.ring(3, 3), E.TWO_ADDED, 2),
             (E.ring(4, 3), E.TWO_ADDED, 2), (E.ring(6, 2), E.THREE_ADDED, 3), (E.d2(4, 2), E.TWO_ADDED, 2),
             (E.dw(4, 2), E.Law('RATION-3', 'CANCEL-WAIT'), 2), (E.ring(5, 3), E.Law('CAP-3', 'CANCEL-WAIT', 'HOLD'), 3),
             (E.ring(5, 3), E.Law('CAP-3', 'STALL'), 3), (E.ring(5, 3), E.Law('CAP-3', 'CANCEL-OFFSHOOT'), 2),
             (E.ring(5, 3), E.Law('CAP-3', 'CANCEL-RETIRE', no_offshoot=True), 3), (E.ring(3, 1), E.ORDINARY, 2),
             (E.ring(4, 1), E.Law('FLOOR0', 'CANCEL-WAIT'), 3)]
    compared = 0
    bad = []
    for ci, (start, law, R) in enumerate(cases):
        S = start.copy()
        st = naive_from_structure(S)
        for r in range(R):
            S_next, rec = E.round_step(S, law)
            persisting = sum(1 for (u, _, _) in E.live_members(S) if S_next.hk(u)[0] > 0)
            if rec['n_births'] + persisting > 16 or len(E.live_members(S)) > 16:
                break
            S = S_next
            st, info = naive_round(st, law)
            compared += 1
            why = struct_equal(S, st)
            eb = [(b['id'], tuple(b['parents']), b['D'], b['f'], b['usable']) for b in rec['births']]
            if why is None and eb != info['births']:
                why = 'births'
            if why is None and [tuple(g) for g in rec['groups']] != info['groups']:
                why = 'groups'
            if why is not None:
                bad.append({'case': ci, 'round': r + 1, 'law': law.name(), 'why': why})
                break
    report('one full round vs naive implementation (named small cases)', not bad, rounds_compared=compared,
           mismatches=bad)


def check_knot_tests(rng, trials=400):
    bad = []
    n_struct = n_knots = n_fail_seen = 0
    for trial in range(trials):
        start = E.from_stars(random_stars(rng, nmax=4, loose_max=2))
        law = random_law(rng)
        S = start
        for r in range(rng.randint(0, 2)):
            if S.n_distinctions > 11:
                break
            S2, _ = E.round_step(S, law)
            if S2.n_distinctions <= 14:
                if not brute_extends(S, S2) == E.extension_test_parity(S, S2)['extends']:
                    bad.append({'trial': trial, 'what': 'extension'})
            S = S2
        if S.n_distinctions > 14:
            continue
        n_struct += 1
        n_knots += S.n_knots
        bp = brute_knot_pass(S, 'parity')
        res = E.parity_knot_test(S)
        rank_pass = [u not in set(res['rank_fail']) for u in range(S.n_knots)]
        cut_pass = [u not in set(res['cut_fail']) for u in range(S.n_knots)]
        naive_vals = E.parity_rank_values_naive(S)
        dc_vals, _ = E.parity_rank_values(S)
        n_fail_seen += sum(1 for x in bp if not x)
        if bp != rank_pass or bp != cut_pass or naive_vals != dc_vals:
            bad.append({'trial': trial, 'what': 'parity', 'brute': bp, 'rank': rank_pass, 'cut': cut_pass})
        bn = brute_knot_pass(S, 'nae')
        nae = E.nae_knot_test(S)
        nae_pass = [u not in set(nae['fail']) for u in range(S.n_knots)]
        if bn != nae_pass:
            bad.append({'trial': trial, 'what': 'nae'})
    report('knot tests vs brute-force allowed states (parity x3, NAE, ext.)', not bad,
           structures=n_struct, knots=n_knots, parity_failing_knots_seen=n_fail_seen, mismatches=bad[:5])


def check_planted():
    # knot 0 = [a,b,l1,l2,l3]; knot 1 = [a,b,e,f,g]; knot 2 = [e,f,g]: knots 1 and 2 hold no loose distinction,
    # so the rule of knot 0 is joined by a = b: knot 0 fails; knot 1 fails too; knot 2 passes.
    S = E.from_stars([['a', 'b', 'l1', 'l2', 'l3'], ['a', 'b', 'e', 'f', 'g'], ['e', 'f', 'g']])
    res = E.parity_knot_test(S)
    brute = brute_knot_pass(S, 'parity')
    ok = (0 in res['rank_fail'] and 0 in res['cut_fail'] and not res['disagree']
          and brute == [False, False, True])
    report('planted failing parity knot: both methods fail it and agree', ok,
           rank_fail=res['rank_fail'], cut_fail=res['cut_fail'], disagree=res['disagree'], brute=brute)
    # a small not-all-equal case that fails (found by brute-force search over small structures)
    T = E.from_stars([[0, 1, 4], [0, 1, 2, 3], [2, 3, 4]])
    nae = E.nae_knot_test(T)
    bn = brute_knot_pass(T, 'nae')
    report('small not-all-equal case that fails', nae['fail'] == [1] and bn == [True, False, True],
           sat_fail=nae['fail'], brute=bn)
    # and a closed parity structure (no loose distinction): reading D1 of the cut method
    C = E.from_stars([[0, 1, 2], [0, 1, 2]])
    rc = E.parity_knot_test(C)
    report('closed structure: rank and cut (reading D1) agree, both pass', rc['all_pass'] and not rc['disagree'],
           rank_fail=rc['rank_fail'], cut_fail=rc['cut_fail'])


def run_signature(run):
    return json.dumps({'trace': run.trace(with_births=True), 'returns': run.find_returns(),
                       'records': run.records, 'summary': run.summary(),
                       'structure': run.S.to_dict()}, sort_keys=True)


def check_determinism():
    pairs = [(E.ring(7, 3), E.TWO_ADDED, 10), (E.ring(5, 3), E.THREE_ADDED, 12), (E.generator7(), E.ORDINARY, 4),
             (E.d2(5, 3), E.Law('RATION-3', 'CANCEL-WAIT'), 6), (E.ring(9, 3), E.Law('CAP-4', 'CANCEL-RETIRE'), 6)]
    same = True
    for start, law, R in pairs:
        a = run_signature(E.Run(start, law, R))
        b = run_signature(E.Run(start, law, R))
        same = same and a == b
    report('determinism: same run twice, identical output (in process)', same, runs=len(pairs))


def check_isomorphism():
    # sameness is exact: a 6-cycle of pairs vs two 3-cycles of pairs (same invariants per vertex)
    def mk(edges, n):
        maxsets = [frozenset(e) for e in edges]
        return E.Roster(range(n), {u: 2 for u in range(n)}, {u: 0 for u in range(n)},
                        sorted(maxsets, key=sorted), [(0,)] * len(maxsets), set())
    six = mk([(i, (i + 1) % 6) for i in range(6)], 6)
    two3 = mk([(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3)], 6)
    six_b = mk([(0, 3), (3, 1), (1, 4), (4, 2), (2, 5), (5, 0)], 6)
    ok = (not E.same_rosters(six, two3)) and E.same_rosters(six, six_b)
    report('roster sameness: exact on a 6-cycle vs two 3-cycles', ok)


def main():
    t0 = time.time()
    rng = random.Random(20261123)
    check_group_rule(rng)
    check_rounds_vs_naive(rng)
    check_named_vs_naive()
    check_knot_tests(rng)
    check_planted()
    check_isomorphism()
    check_determinism()
    allok = all(v['ok'] for v in RESULTS.values())
    RESULTS['_all_ok'] = allok
    RESULTS['_seconds'] = round(time.time() - t0, 1)
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, 'test_engine.json'), 'w') as f:
        json.dump(RESULTS, f, indent=1, sort_keys=True)
    print('ALL SELF-CHECKS', 'PASS' if allok else 'FAIL', '(%.1f s)' % (time.time() - t0))
    return 0 if allok else 1


if __name__ == '__main__':
    sys.exit(main())
