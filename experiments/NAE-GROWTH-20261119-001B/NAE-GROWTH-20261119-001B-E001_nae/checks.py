"""Gate checks for NAE-GROWTH-20261119-001B-E001 (run before the census; output in checks_output.json).

G1  structural parity "implied" equals GF(2) elimination: every 50th census arrangement grown both ways, counts and flags equal.
G2  naelib's SAT "implied" equals brute force over the allowed states, on the advisor's two implied cases and 300 random joins.
G3  bondlib's parity table equals the least supports of the dual code (the span of the junction equations) on 40 stages.
G4  the canonical checker (knotlab check): not-all-equal on 3 to 6 places and parity on 3 to 5 pass K1-K3; one-in-k and
    majority on 3 to 5 places fail (no junction under them is a knot, so the cheapest growth has nothing to make).
G5  the advisor's stronger lemma by brute force: on 400 random not-all-equal presentations (every bit in at most two junctions,
    every junction of at least three places), every set of bits that leaves each junction two places outside it is free; and
    the condition is sharp (some set leaving a junction one place is not free).
G6  the keep clause for laws failing K2: on the lone knot of three places, the first join under one-in-three removes an old
    state for every fresh count 1 to 4; under majority it does for 1 and 2 fresh bits and not for 3 or 4.
"""
import itertools
import json
import random
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import job  # noqa: E402
import naelib as N  # noqa: E402
import bondlib as B  # noqa: E402
J = N.J


def g1():
    keys = sorted(job.arrlib.arrangements(5))[::50]
    bad = 0
    for k in keys:
        sz, e = job.edges_of(k)
        a = job.grow(sz, e, 'parity', rounds=10, maxj=1500)
        P = N.S.from_junctions(J.stars_from(sz, e))
        flags = []

        def rec(P, info, rng):
            flags.extend([P.rounds, i['p']] for i in info if i['implied'])
            return N.F.fewest(P, info, rng)
        rule = N.S.gf2(rec)
        for _ in range(10):
            r = P.step(rule, None)
            if r is None or r['new'] == 0 or len(P.bits_of) > 1500:
                break
        if P.counts_by_round() != a['counts'] or flags != [x[:2] for x in a['implied']]:
            bad += 1
    return {'arrangements': len(keys), 'differ': bad, 'pass': bad == 0}


def brute_implied(stars, n, bits):
    st = B.states(n, stars, 'nae')
    v = np.zeros(len(st), dtype=np.int64)
    for b in bits:
        v += (st >> b) & 1
    return not bool(np.any((v == 0) | (v == len(bits))))


class Pres:
    def __init__(self, stars):
        self.bits_of = [list(s) for s in stars]


def g2():
    out = {}
    # the advisor's case: the lone knot after one round, a six-place junction on all six loose bits
    stars = [[0, 1, 2], [0, 3, 4], [1, 5, 6], [2, 7, 8]]
    out['six_place'] = [N.nae_implied(Pres(stars), 4, [3, 4, 5, 6, 7, 8]), brute_implied(stars, 9, [3, 4, 5, 6, 7, 8])]
    out['swallow'] = [N.nae_implied(Pres(stars), 4, [0, 3, 4]), brute_implied(stars, 9, [0, 3, 4])]
    out['one_each'] = [N.nae_implied(Pres(stars), 4, [3, 5, 7]), brute_implied(stars, 9, [3, 5, 7])]
    rng = random.Random(5)
    agree = total = implied = 0
    while total < 300:
        stars, n = random_pres(rng, 12)
        if stars is None:
            continue
        k = rng.randint(2, min(6, n))
        bits = rng.sample(range(n), k)
        a, b = N.nae_implied(Pres(stars), len(stars), bits), brute_implied(stars, n, bits)
        total += 1
        agree += a == b
        implied += b
    out['random'] = {'cases': total, 'agree': agree, 'implied': implied}
    out['pass'] = (out['six_place'] == [True, True] and out['swallow'] == [True, True] and out['one_each'] == [False, False]
                   and agree == total and 0 < implied < total)
    return out


def random_pres(rng, nmax):
    """Random not-all-equal presentation: junctions of 3 to 5 places, every bit in one or two junctions, at most nmax bits."""
    m = rng.randint(2, 5)
    sizes = [rng.randint(3, 5) for _ in range(m)]
    slots = [(j, s) for j in range(m) for s in range(sizes[j])]
    rng.shuffle(slots)
    stars = [[] for _ in range(m)]
    b = 0
    while slots:
        j, _ = slots.pop()
        partner = next((i for i, (j2, _) in enumerate(slots) if j2 != j and b not in stars[j2]), None)
        stars[j].append(b)
        if partner is not None and rng.random() < 0.5:
            j2, _ = slots.pop(partner)
            stars[j2].append(b)
        b += 1
    if b > nmax:
        return None, b
    return stars, b


def g3():
    rows = []
    for k in sorted(job.arrlib.arrangements(3)):
        sz, e = job.edges_of(k)
        stages = []
        job.grow(sz, e, 'nae', rounds=4, stages=stages)
        rows += [s for s in stages if 1 + max(x for t in s for x in t) <= 13]
    rows = rows[::max(1, len(rows) // 40)][:40]
    bad = 0
    for stars in rows:
        n = 1 + max(x for t in stars for x in t)
        T = B.table(n, B.states(n, stars, 'parity'), n)
        span = [0]
        for s in stars:
            eq = 0
            for x in s:
                eq ^= 1 << x
            span += [r ^ eq for r in span]
        span = sorted(set(span) - {0}, key=lambda r: (bin(r).count('1'), r))
        minimal = []
        for r in span:
            if all(r & p != p for p in minimal):
                minimal.append(r)
        D = {}
        for r in minimal:
            sup = [x for x in range(n) if r >> x & 1]
            for x, y in itertools.combinations(sup, 2):
                D[(x, y)] = min(D.get((x, y), n), len(sup) - 1)
        if any(T[p] != D.get(p, n) for p in T):
            bad += 1
    return {'stages': len(rows), 'differ': bad, 'pass': bad == 0 and len(rows) >= 30}


def knotlab(cnf, k):
    vs = [f'x{i}' for i in range(k)]
    r = subprocess.run([sys.executable, '-B', '-m', 'knotlab', 'check', '--cnf', cnf(vs), '--loops', *vs[:-1], '--contact', vs[-1],
                        '--json'], capture_output=True, text=True, env={'PYTHONPATH': str(N.ROOT / 'tools')}, cwd=N.ROOT)
    return json.loads(r.stdout)['is_knot']


def g4():
    def nae(vs):
        return ' '.join(vs) + '; ' + ' '.join('~' + v for v in vs)

    def parity(vs):      # even parity: one clause excluding each odd assignment
        return '; '.join(' '.join(('~' + v) if a else v for v, a in zip(vs, sg))
                         for sg in itertools.product((0, 1), repeat=len(vs)) if sum(sg) % 2 == 1)

    def one_in_three(vs):
        return ' '.join(vs) + '; ' + '; '.join(f'~{a} ~{b}' for a, b in itertools.combinations(vs, 2))

    def majority(vs):    # more than half are 1: every set of (k + 1) // 2 + ... places holds a 1
        k = len(vs)
        return '; '.join(' '.join(c) for c in itertools.combinations(vs, k // 2 + 1))
    out = {f'nae{k}': knotlab(nae, k) for k in range(3, 7)}
    out.update({f'parity{k}': knotlab(parity, k) for k in range(3, 6)})
    out.update({f'one_in_{k}': knotlab(one_in_three, k) for k in range(3, 6)})
    out.update({f'majority{k}': knotlab(majority, k) for k in range(3, 6)})
    out['pass'] = all(out[f'nae{k}'] for k in range(3, 7)) and all(out[f'parity{k}'] for k in range(3, 6)) \
        and not any(out[f'one_in_{k}'] or out[f'majority{k}'] for k in range(3, 6))
    return out


def free(st, bits):
    idx = np.zeros(len(st), dtype=np.int64)
    for i, b in enumerate(bits):
        idx |= ((st >> b) & 1) << i
    return np.unique(idx).size == 1 << len(bits)


def g5():
    rng = random.Random(11)
    tested = held = sharp_tested = sharp_nonfree = 0
    pres = 0
    while pres < 400:
        stars, n = random_pres(rng, 14)
        if stars is None:
            continue
        st = B.states(n, stars, 'nae')
        if len(st) == 0:
            continue
        pres += 1
        for _ in range(10):
            S = [b for b in range(n) if rng.random() < 0.4]
            kept = [len([b for b in s if b not in S]) for s in stars]
            if not S:
                continue
            if min(kept) >= 2:
                tested += 1
                held += free(st, S)
            elif min(kept) == 1:
                sharp_tested += 1
                sharp_nonfree += not free(st, S)
    return {'presentations': pres, 'sets_two_kept': tested, 'free': held, 'sets_one_kept': sharp_tested,
            'not_free_among_them': sharp_nonfree, 'pass': tested > 500 and held == tested and sharp_nonfree > 0}


def g6():
    laws = {'one_in_three': lambda c, k: c == 1, 'majority': lambda c, k: 2 * c > k}
    out = {}
    # the lone knot (bits 0, 1, 2) and two offshoots (0, 3, 4), (1, 5, 6); the first join takes 3 and 5, with f fresh bits
    for name, ok in laws.items():
        res = {}
        for f in range(1, 5):
            stars = [[0, 1, 2], [0, 3, 4], [1, 5, 6]]
            n_old = 7
            new = [3, 5] + list(range(n_old, n_old + f))

            def allowed(stars, n):
                s = np.arange(1 << n, dtype=np.int64)
                m = np.ones(1 << n, dtype=bool)
                for S in stars:
                    c = sum((s >> b) & 1 for b in S)
                    m &= ok(c, len(S))
                return s[m]
            old = set((allowed(stars, n_old)).tolist())
            after = set((allowed(stars + [new], n_old + f) & ((1 << n_old) - 1)).tolist())
            res[f] = {'old_states': len(old), 'kept': len(after & old), 'removes': len(old - after) > 0}
        out[name] = res
    # one-in-three removes an old state at every count; majority keeps them once the fresh bits outnumber the old (f > 2)
    out['pass'] = (all(r['removes'] and r['old_states'] > 0 for r in out['one_in_three'].values())
                   and all(out['majority'][f]['removes'] == (f <= 2) for f in range(1, 5)))
    return out


if __name__ == '__main__':
    res = {'G1': g1(), 'G2': g2(), 'G3': g3(), 'G4': g4(), 'G5': g5(), 'G6': g6()}
    res['all_pass'] = all(v['pass'] for v in res.values() if isinstance(v, dict))
    (HERE / 'checks_output.json').write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps({k: (v['pass'] if isinstance(v, dict) else v) for k, v in res.items()}))
