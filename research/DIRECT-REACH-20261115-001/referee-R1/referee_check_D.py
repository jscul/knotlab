"""Referee R1, item (b): Theorem D's descents.

(b1) chain_ties.Extended (CALLED AS THE THING UNDER TEST): its images of every composite m_j . m_i^(-1) on random addresses of
     levels 1..LMAX against my own brute-force inversion (letter by letter with my forward action) followed by m_j.
(b2) chain_ties.initial_type/next_type/window_knots (UNDER TEST): the block of S_k from the type evolution against the block
     from explicit addresses (every address v of level k, every placement, my own action), levels k0..KMAX.
(b3) my own explicit union of the descent's blocks (levels k0..k): at every level, the per-level claim of D1 (an anchor tied to an
     element of S_(k+1)) or D2 (a tie, or a constrained {x, x', y} with (x, x') free by two machines with different parities,
     or a constrained {x, y, y'} with (y, y') free so), decided by SAT on the explicit union; my own machine evaluation.
(b4) the per-level witnesses of (b3) at levels <= NP in the whole pattern P_NP by SAT (ties forced, triples constrained, the
     one-level pair free).
The descents are read from chain_ties_constant-2.json and chain_bounded3_constant-3.json (data under test); machines for D1 from
exploratory/automatic_search.json, for D2 from the chain JSON's machines list.
Usage: referee_check_D.py OUT.json LMAX KMAX NP [case-prefix ...]"""
import itertools
import json
import random
import sys
import time

import numpy as np
from pysat.solvers import Cadical195

sys.path.insert(0, '/home/jscul/p-vs-np-contact-first/research/DIRECT-REACH-20261115-001/referee-R1')
from referee_pattern import Aut, Oracle, hid, load_population, STUDY  # noqa: E402

sys.path.insert(0, str(STUDY))
sys.path.insert(0, str(STUDY / 'exploratory'))
from chain_ties import Extended, initial_type, next_type, window_knots  # noqa: E402  (under test)
from window_types import Description  # noqa: E402  (under test, only to build Extended's input)


def my_inverse(A, word, y):
    """The unique x with word(x) = y, letter by letter (word(x)'s first p letters depend only on x's first p letters)."""
    x = []
    for p in range(len(y)):
        hits = [a for a in (0, 1) if A.act_bits(word, x + [a])[p] == y[p]]
        assert len(hits) == 1, 'not a bijection on a level'
        x.append(hits[0])
    return tuple(x)


def machine_values(M, addrs):
    """addrs: list of bit tuples. My own evaluation: read from the first letter, value = out[state]."""
    delta, out, start = M
    res = []
    for a in addrs:
        q = start
        for b in a:
            q = delta[q][b]
        res.append(out[q])
    return res


def letters(chain, step):
    pre, cyc = chain['prefix'], chain['cycle']
    return pre[step] if step < len(pre) else cyc[(step - len(pre)) % len(cyc)]


def explicit_block(A, S, k):
    """Knots placed at level k (every address v) with all members in S ∪ S·{0,1}; local variables j (S[j]) and n + 2j + b."""
    n = len(S)
    loc = {}
    for j, x in enumerate(S):
        loc[(k, x)] = j
        loc[(k + 1, 2 * x)] = n + 2 * j
        loc[(k + 1, 2 * x + 1)] = n + 2 * j + 1
    imgs = {wi: A.act(A.W[wi], k) for wi in A.used}
    Sarr = np.array(S, dtype=np.int64)
    out = set()
    for p in A.placements:
        terms = [divmod(t, 3) for t in p]
        mem_ok = np.ones(1 << k, dtype=bool)
        for wi, e in terms:
            y = imgs[wi]
            mem_ok &= np.isin(y, Sarr)          # members w(v) or w(v).e lie in S ∪ S·{0,1} iff w(v) ∈ S
        for v in np.nonzero(mem_ok)[0]:
            mem = []
            for wi, e in terms:
                y = int(imgs[wi][v])
                mem.append(loc[(k, y)] if e == 0 else loc[(k + 1, 2 * y + e - 1)])
            if len(set(mem)) == 3:
                out.add(tuple(sorted(mem)))
    return tuple(sorted(out))


def to_int(bits):
    return int(''.join(map(str, bits)) or '0', 2)


def check_descent(case, key, chain, kind, Ms, LMAX, KMAX, NP, rng):
    A = Aut(key)
    D = Description(key)
    E = Extended(D)
    rec = dict(kind=kind, k0=chain['k0'], S=chain['S'], prefix=chain['prefix'], cycle=chain['cycle'], machines=len(Ms))
    # (b1) composite images
    nb1 = bad1 = 0
    for (j, i), comp in sorted(E.comp.items()):
        for L in range(1, LMAX + 1):
            for _ in range(4):
                x = tuple(rng.getrandbits(1) for _ in range(L))
                got, _ = E.image(comp, x)
                want = A.act_bits(D.maps[j], my_inverse(A, D.maps[i], x))
                nb1 += 1
                if tuple(got) != tuple(want):
                    bad1 += 1
    rec['b1'] = dict(images=nb1, wrong=bad1)
    # (b2) blocks from the type evolution against explicit blocks
    k0 = chain['k0']
    S_bits = [tuple(int(ch) for ch in x) for x in chain['S']]
    T = initial_type(E, S_bits)
    cur = list(S_bits)
    levels = []               # (k, S_k as ints, explicit block in local variables)
    nb2 = bad2 = 0
    for step in range(KMAX - k0 + 1):
        k = k0 + step
        c = letters(chain, step)
        Sk = [to_int(x) for x in cur]
        eb = explicit_block(A, Sk, k)
        nb2 += 1
        if tuple(window_knots(E, T)) != eb:
            bad2 += 1
        levels.append((k, Sk, eb, c))
        T = next_type(E, T, c)
        cur = [x + (c[i],) for i, x in enumerate(cur)]
    rec['b2'] = dict(levels=nb2, wrong=bad2, k_range=[k0, KMAX])
    # (b3) per-level claims in the explicit union of blocks
    n = len(S_bits)
    anchors = [hid(to_int(x), k0) for x in S_bits]
    top_free = set()
    vals0 = [machine_values(M, S_bits) for M in Ms]
    for a, b in itertools.combinations(range(n), 2):
        if len({v[a] ^ v[b] for v in vals0}) == 2:
            top_free.add((a, b))
    solver = Cadical195()
    witnesses, failures, kinds = [], [], []
    for k, Sk, eb, c in levels:
        gl = []
        for j in range(n):
            gl.append(hid(Sk[j], k))
        child = {}
        for j in range(n):
            for b in (0, 1):
                child[n + 2 * j + b] = hid(2 * Sk[j] + b, k + 1)
        for kn in eb:
            g = [gl[v] if v < n else child[v] for v in kn]
            solver.add_clause([v + 1 for v in g])
            solver.add_clause([-v - 1 for v in g])
        deep_bits = [tuple(int(ch) for ch in format(2 * Sk[j] + c[j], '0%db' % (k + 1))) for j in range(n)]
        deep = [hid(2 * Sk[j] + c[j], k + 1) for j in range(n)]
        if not solver.solve():
            failures.append((k, 'union dead'))
            break

        def sat(lits):
            return solver.solve(assumptions=lits)

        def pats(vs):
            return {p for p in range(1 << len(vs)) if sat([(v + 1) if (p >> i) & 1 else -(v + 1) for i, v in enumerate(vs)])}
        found = None
        for i in range(n):
            for j in range(n):
                P = pats([anchors[i], deep[j]])
                if len(P) == 2 and len({((p & 1) ^ (p >> 1)) for p in P}) == 1:
                    found = ('tie', anchors[i], deep[j])
                    break
            if found:
                break
        if not found and kind == 'D2':
            for (a, b) in sorted(top_free):
                for j in range(n):
                    if len(pats([anchors[a], anchors[b], deep[j]])) < 8:
                        found = ('top-top-deep', anchors[a], anchors[b], deep[j])
                        break
                if found:
                    break
        if not found and kind == 'D2':
            vd = [machine_values(M, deep_bits) for M in Ms]
            for j, j2 in itertools.combinations(range(n), 2):
                if len({v[j] ^ v[j2] for v in vd}) != 2:
                    continue
                for i in range(n):
                    if len(pats([anchors[i], deep[j], deep[j2]])) < 8:
                        found = ('top-deep-deep', anchors[i], deep[j], deep[j2])
                        break
                if found:
                    break
        kinds.append(found[0] if found else None)
        if not found:
            failures.append((k, 'no certificate at this level'))
        else:
            witnesses.append((k,) + found)
    solver.delete()
    rec['b3'] = dict(levels=len(kinds), failures=failures, kinds=kinds)
    # (b4) witnesses in the whole pattern P_NP
    O = Oracle(key, NP)
    assert O.alive()
    nb4 = bad4 = 0
    for w in witnesses:
        k, what = w[0], w[1]
        if k + 1 > NP:
            continue
        nb4 += 1
        if what == 'tie':
            P = O.patterns([w[2], w[3]], np.zeros((0, O.nv), dtype=bool))
            ok = len(P) == 2 and len({((p & 1) ^ (p >> 1)) for p in P}) == 1
        else:
            P = O.patterns(list(w[2:]), np.zeros((0, O.nv), dtype=bool))
            ok = len(P) < 8
            pair = (w[2], w[3]) if what == 'top-top-deep' else (w[3], w[4])
            Pp = O.patterns(list(pair), np.zeros((0, O.nv), dtype=bool))
            ok = ok and len(Pp) == 4
        if not ok:
            bad4 += 1
    O.close()
    rec['b4'] = dict(N=NP, claims=nb4, false=bad4)
    return rec


if __name__ == '__main__':
    out_path, LMAX, KMAX, NP = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    prefixes = sys.argv[5:]
    rng = random.Random(11)
    keys = {d['case']: d['key'] for d in load_population()}
    auto = json.load(open(STUDY / 'exploratory/automatic_search.json'))
    todo = []
    for name, kind in (('chain_ties_constant-2.json', 'D1'), ('chain_bounded3_constant-3.json', 'D2')):
        for cid, row in json.load(open(STUDY / name)).items():
            if row.get('chain'):
                Ms = row.get('machines') or ([auto[cid]['machine']] if auto.get(cid) else [])
                todo.append((cid, kind, row['chain'], Ms, row['bounded_orbits']))
    if prefixes:
        todo = [t for t in todo if any(t[0].startswith(p) for p in prefixes)]
    res = {}
    t0 = time.time()
    for cid, kind, chain, Ms, bounded in todo:
        t1 = time.time()
        rec = check_descent(cid, keys[cid], chain, kind, Ms, LMAX, KMAX, NP, rng)
        rec['bounded_orbits'] = bounded
        rec['seconds'] = time.time() - t1
        res[cid] = rec
        print(cid[:12], kind, 'b1', rec['b1'], 'b2', rec['b2']['wrong'], 'b3 fail', rec['b3']['failures'], 'b4', rec['b4'],
              '%.1fs' % rec['seconds'], flush=True)
        json.dump(dict(LMAX=LMAX, KMAX=KMAX, NP=NP, cases=res, seconds=time.time() - t0), open(out_path, 'w'), indent=0)
    print('done', len(res), '%.0fs' % (time.time() - t0))
