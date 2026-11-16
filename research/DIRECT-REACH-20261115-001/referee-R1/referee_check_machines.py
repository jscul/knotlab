"""Referee R1, item (c): finite-reader states.

My own all-level check (a joint product over ALL used words at once, unlike the study's per-placement product): a configuration
at address v is (for every used word: its section at v and the machine's state after reading the word's image of v; and which
images of v are equal). Every placement's knot at v is evaluated from it; a breadth-first search over reachable configurations
decides whether the machine's values satisfy every knot at every level.
Also: an explicit check at depth NX with numpy (my builder, my machine evaluation), every knot of P_NX; and the study's
check_all_levels (exploratory/automatic_life.py, CALLED AS THE THING UNDER TEST) on the same machines and on random machines.
Usage: referee_check_machines.py OUT.json NX NRANDOM"""
import json
import random
import sys
import time
from collections import deque

import numpy as np

sys.path.insert(0, '/home/jscul/p-vs-np-contact-first/research/DIRECT-REACH-20261115-001/referee-R1')
from referee_pattern import Aut, load_population, STUDY  # noqa: E402

sys.path.insert(0, str(STUDY / 'exploratory'))
from automatic_life import check_all_levels  # noqa: E402  (under test)


def read(sw, d, word, b):
    c, new = b, list(word)
    for i in range(len(word) - 1, -1, -1):
        q = word[i]
        new[i] = d[c][q]
        c ^= sw[q]
    return c, tuple(new)


def my_all_levels(key, M, cap=3_000_000):
    s, sw, d0, d1, placements = key
    d = [list(d0), list(d1)]
    W = [()] + [(q,) for q in range(s)] + [(q, r) for q in range(s) for r in range(s)]
    P = sorted({tuple(sorted(int(t) for t in p)) for p in placements})
    used = sorted({t // 3 for p in P for t in p})
    idx = {wi: j for j, wi in enumerate(used)}
    K = len(used)
    delta, out, start = M
    terms = [[(idx[t // 3], t % 3) for t in p] for p in P]
    full = (1 << (K * K)) - 1                       # eq bit j*K + j2: images j and j2 equal so far
    init = (tuple(tuple(W[wi]) for wi in used), (start,) * K, full)
    seen, q = {init}, deque([init])
    while q:
        secs, mus, eq = q.popleft()
        for tl in terms:
            vals, ok = [], True
            for j, e in tl:
                vals.append(out[mus[j]] if e == 0 else out[delta[mus[j]][e - 1]])
            distinct = True
            for a in range(3):
                for b in range(a + 1, 3):
                    (j, e), (j2, e2) = tl[a], tl[b]
                    same_img = (eq >> (j * K + j2)) & 1
                    if (e == 0) != (e2 == 0):
                        continue
                    if same_img and e == e2:
                        distinct = False
            if distinct and vals[0] == vals[1] == vals[2]:
                return False, len(seen)
        for b in (0, 1):
            outs, nsecs = [], []
            for w in secs:
                c, nw = read(sw, d, w, b)
                outs.append(c)
                nsecs.append(nw)
            nmus = tuple(delta[mu][c] for mu, c in zip(mus, outs))
            neq = eq
            for j in range(K):
                for j2 in range(K):
                    if outs[j] != outs[j2]:
                        neq &= ~(1 << (j * K + j2))
            cfg = (tuple(nsecs), nmus, neq)
            if cfg not in seen:
                seen.add(cfg)
                q.append(cfg)
                if len(seen) > cap:
                    raise RuntimeError('too many configurations')
    return True, len(seen)


def values(M, N):
    """Heap-ordered values of every address of levels 0..N (my own evaluation, vectorised)."""
    delta, out, start = M
    dl = np.array(delta, dtype=np.int64)
    ol = np.array(out, dtype=np.int8)
    st = np.array([start], dtype=np.int64)
    vals = [ol[st]]
    for n in range(1, N + 1):
        st = np.stack([dl[st, 0], dl[st, 1]], axis=1).reshape(-1)     # children 2y, 2y + 1
        vals.append(ol[st])
    return np.concatenate(vals)


def explicit_ok(A, M, NX, cache):
    v = values(M, NX)
    for n in range(NX + 1):
        if n not in cache:
            cache[n] = A.level_knots(n, NX)
        K = cache[n]
        if len(K):
            ssum = v[K[:, 0]] + v[K[:, 1]] + v[K[:, 2]]
            if np.any((ssum == 0) | (ssum == 3)):
                return False, n
    return True, None


def random_machine(rng, k):
    return ([[rng.randrange(k), rng.randrange(k)] for _ in range(k)], [rng.getrandbits(1) for _ in range(k)], 0)


def mutant(rng, M):
    """A valid machine with one output flipped or one transition redirected (or a new state added): a discriminating test."""
    delta = [list(r) for r in M[0]]
    out = list(M[1])
    k = len(out)
    r = rng.random()
    if r < 0.3:
        i = rng.randrange(k)
        out[i] ^= 1
    elif r < 0.8:
        delta[rng.randrange(k)][rng.getrandbits(1)] = rng.randrange(k)
    else:
        delta.append([rng.randrange(k + 1), rng.randrange(k + 1)])
        out.append(rng.getrandbits(1))
        delta[rng.randrange(k)][rng.getrandbits(1)] = k
    return (delta, out, M[2])


if __name__ == '__main__':
    out_path, NX, NRAND = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    rng = random.Random(3)
    pop = load_population()
    auto = json.load(open(STUDY / 'exploratory/automatic_search.json'))
    chains = {}
    for name in ('chain_ties_constant-2.json', 'chain_bounded3_constant-3.json'):
        for cid, row in json.load(open(STUDY / name)).items():
            chains.setdefault(cid, []).extend(row.get('machines') or [])
    res, problems = {}, []
    t0 = time.time()
    tally = dict(with_machine=0, max_states_le5=0, machines_checked=0, random_checked=0)
    for d in pop:
        cid, key = d['case'], d['key']
        A = Aut(key)
        Ms = []
        if auto.get(cid):
            Ms.append(('automatic_search', auto[cid]['machine']))
            tally['with_machine'] += 1
            if len(auto[cid]['machine'][1]) <= 5:
                tally['max_states_le5'] += 1
        for M in chains.get(cid, []):
            Ms.append(('chain machines', M))
        cache = {}
        rec = dict(profile=d['profile'], machines=[])
        for src, M in Ms:
            mine, cfgs = my_all_levels(key, M)
            exp, at = explicit_ok(A, M, NX, cache)
            theirs, _ = check_all_levels(key, M)
            tally['machines_checked'] += 1
            rec['machines'].append(dict(source=src, states=len(M[1]), mine=mine, configs=cfgs, explicit=exp, study=theirs))
            if not (mine and exp and theirs):
                problems.append(dict(case=cid, source=src, machine=M, mine=mine, explicit=(exp, at), study=theirs))
        # random machines: my checker against the explicit check and the study's checker (soundness of all three)
        rnd = dict(n=0, pass_mine=0, disagree=[])
        for _ in range(NRAND):
            M = mutant(rng, rng.choice(Ms)[1]) if Ms and rng.random() < 0.8 else random_machine(rng, rng.randint(2, 4))
            mine, _ = my_all_levels(key, M)
            exp, _ = explicit_ok(A, M, min(NX, 12), {})
            theirs, _ = check_all_levels(key, M)
            rnd['n'] += 1
            rnd['pass_mine'] += int(mine)
            tally['random_checked'] += 1
            if mine != theirs or (mine and not exp):
                rnd['disagree'].append(dict(machine=M, mine=mine, explicit12=exp, study=theirs))
                problems.append(dict(case=cid, source='random', machine=M, mine=mine, explicit12=exp, study=theirs))
        rec['random'] = rnd
        res[cid] = rec
        print(cid[:12], d['profile'], 'machines', len(Ms), 'all ok' if all(m['mine'] and m['explicit'] and m['study'] for m in rec['machines']) else 'PROBLEM',
              'random pass', rnd['pass_mine'], '/', rnd['n'], 'disagree', len(rnd['disagree']), flush=True)
    tally['seconds'] = time.time() - t0
    json.dump(dict(NX=NX, tally=tally, problems=problems, cases=res), open(out_path, 'w'), indent=0)
    print(tally, 'problems', len(problems))
