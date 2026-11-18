"""Shared-runner job for FRESH-COUNT-20261118-001B-E001: parity growth with the fresh count left to a rule."""
import random
import sys
from math import comb
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import freelib as F  # noqa: E402
import ideals  # noqa: E402
import bonds  # noqa: E402

MENU = {'fewest': F.fewest, 'axis': F.axis, 'inherit_max': F.inherit(max), 'inherit_min': F.inherit(min),
        'balance': F.balance}


def cases():
    for cap in (None, 3):
        for a in range(3, 8):
            for c in range(1, a + 4):
                yield f'uniform-cap{cap}-a{a}-c{c}', {'part': 'uniform', 'cap': cap, 'a': a, 'c': c}
    for a in range(3, 7):
        for name in MENU:
            yield f'menu-{name}-a{a}', {'part': 'menu', 'rule': name, 'a': a}
    for a in (3, 4):
        for K in range(2, 7):
            for s in range(200):
                yield f'blind-a{a}-K{K}-s{s}', {'part': 'blind', 'a': a, 'K': K, 'seed': 100000 * a + 1000 * K + s}
    for a in (3, 4):
        for q in (0.05, 0.1, 0.2, 0.4):
            for s in range(200):
                yield f'surplus-a{a}-q{q}-s{s}', {'part': 'surplus', 'a': a, 'q': q, 'seed': 200000 * a + int(1000 * q) * 300 + s}
    for s in range(200):
        yield f'handover-s{s}', {'part': 'handover', 'seed': 900000 + s}
    for a in range(3, 7):
        yield f'crossed-a{a}', {'part': 'crossed', 'a': a}
    for a, T in ((3, 0), (3, 1), (3, 2), (3, 3), (4, 0), (4, 1), (4, 2), (5, 0), (5, 1)):
        yield f'reader-uniform-a{a}-r{T}', {'part': 'reader', 'kind': 'uniform', 'a': a, 'rounds': T}
    for a, T in ((3, 0), (3, 1), (3, 2), (3, 3), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4)):
        yield f'reader-fewest-a{a}-r{T}', {'part': 'reader', 'kind': 'fewest', 'a': a, 'rounds': T}
    for s in range(60):
        yield f'reader-mixed-s{s}', {'part': 'reader_mixed', 'seed': 700000 + s}


def summary(P, outcome, log, check_ideals=True):
    out = {'outcome': outcome, 'rounds': P.rounds, 'counts': P.counts_by_round(), 'offshoots': P.offshoots_by_round(),
           'junctions': len(P.bits_of), 'bits': P.nbits, 'forced_bits': len(P.forced_bits())}
    if check_ideals and outcome != 'stall':
        out['ideals'] = ideals.check(P)
    if P.linalg:
        out['rank'] = len(P.basis)
        out['implied_mismatch'] = P.implied_mismatch
    if log and 'cap_agrees' in log[0]:
        out['cap_rounds'] = [[r['cap_agrees'], r['max_group']] for r in log]
    return out


def reader_check(P):
    stars = [frozenset(S) for S in P.bits_of]
    if len(stars) > 21:
        return {'skipped': 'too many junctions'}
    try:
        allbits, d = bonds.distances(stars, limit=3_000_000)
    except RuntimeError:
        return {'skipped': 'too many connected sets'}
    kmax = max(len(S) for S in stars)
    got = set(bonds.read_stars(allbits, d, kmax))
    true = set(stars)
    loose = frozenset(b for b, js in P.owner.items() if len(js) == 1)
    uniform_size = len({len(S) for S in stars if len(S) > 0}) == 1
    if got == true:
        verdict = 'exact'
    elif got == true | {loose}:
        verdict = 'exact_plus_all_loose'
    else:
        verdict = 'misread'
    loose_is_small_bond = loose in bonds.bonds(stars) and 3 <= len(loose) <= kmax
    return {'verdict': verdict, 'junctions': len(stars), 'kmax': kmax, 'all_loose_small_bond': loose_is_small_bond,
            'extra': len(got - true), 'missing': len(true - got)}


def run(case_id, p):
    part = p['part']
    if part == 'uniform':
        P, outcome, log = F.run(p['a'], F.uniform(p['c']), 8, cap=p['cap'], max_junctions=6000)
        out = summary(P, outcome, log, check_ideals=(p['c'] == p['a']))
        out['stall_round'] = P.rounds + 1 if outcome == 'stall' else None
        a = p['a']
        out['matches_Na'] = all(P.counts_by_round()[t] == comb(t + a - 1, a - 1) for t in range(P.rounds + 1))
        return out
    if part == 'menu':
        a = p['a']
        P, outcome, log = F.run(a, MENU[p['rule']], 10, max_junctions=6000, linalg=(a <= 4))
        out = summary(P, outcome, log)
        out['stall_round'] = P.rounds + 1 if outcome == 'stall' else None
        out['matches_Na'] = all(P.counts_by_round()[t] == comb(t + a - 1, a - 1) for t in range(P.rounds + 1))
        out['matches_boolean'] = P.counts_by_round() == [comb(a, j) for j in range(a + 1)]
        out['arities'] = sorted({len(S) for S in P.bits_of})
        return out
    if part == 'blind':
        P, outcome, log = F.run(p['a'], F.blind(p['K']), 10, seed=p['seed'], max_junctions=3000)
        out = summary(P, outcome, log)
        out['stall_round'] = P.rounds + 1 if outcome == 'stall' else None
        return out
    if part == 'surplus':
        P, outcome, log = F.run(p['a'], F.surplus(p['q']), 10, seed=p['seed'], max_junctions=2500, compare_cap=True)
        return summary(P, outcome, log)
    if part == 'handover':
        rng = random.Random(p['seed'])
        a = rng.choice([3, 4])
        h = rng.randint(1, 4)
        q = rng.choice([0.2, 0.4])
        P = F.Presentation(a)
        outcome = 'alive'
        for _ in range(h):
            r = P.step(F.surplus(q), None, rng)
            if r is None or r['new'] == 0:
                outcome = 'ended before hand-over'
                break
        res = {'a': a, 'h': h, 'q': q}
        if outcome != 'alive':
            res.update(summary(P, outcome, []))
            return res
        for _ in range(25):
            r = P.step(F.fewest, None, rng)
            if r is None:
                outcome = 'stall'
                break
            if r['new'] == 0:
                outcome = 'closed'
                break
            if len(P.bits_of) > 2500:
                outcome = 'big'
                break
        res.update(summary(P, outcome, []))
        # offshoots born in round h + 1 (their counts were the first F chose) and their demand at birth
        first = [j for j in range(len(P.bits_of)) if P.round_of[j] == h + 1 and P.parents[j] == 1]
        res['handover_offshoots'] = len(first)
        res['handover_offshoots_demand1'] = sum(1 for j in first if P.demand_at_birth[j] == 1)
        res['handover_offshoots_demand0'] = sum(1 for j in first if P.demand_at_birth[j] == 0)
        return res
    if part == 'crossed':
        a = p['a']
        P, outcome, log = F.run(a, F.crossed_then_fewest(a), 12, max_junctions=5000)
        return summary(P, outcome, log)
    if part == 'reader':
        a, T = p['a'], p['rounds']
        rule = F.uniform(a) if p['kind'] == 'uniform' else F.fewest
        P = F.Presentation(a)
        for _ in range(T):
            P.step(rule)
        return reader_check(P)
    if part == 'reader_mixed':
        rng = random.Random(p['seed'])
        a = rng.choice([3, 4])
        q = rng.choice([0.1, 0.2, 0.4])
        P = F.Presentation(a)
        stages = []
        for _ in range(6):
            if len(P.bits_of) > 16:
                break
            r = reader_check(P)
            r['round'] = P.rounds
            stages.append(r)
            s = P.step(F.surplus(q), None, rng)
            if s is None or s['new'] == 0:
                break
        return {'a': a, 'q': q, 'stages': stages}
    raise ValueError(part)
