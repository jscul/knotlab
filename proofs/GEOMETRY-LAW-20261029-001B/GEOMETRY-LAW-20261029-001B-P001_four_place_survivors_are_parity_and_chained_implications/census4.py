"""Four-bit knots under native gadgets of their own copies (four legs), exhaustive for 2 and 3 copies, random for 4.
Library for GEOMETRY-LAW-20261029-001B; run directly for a report."""
import itertools, json, random, sys, time
from collections import Counter, defaultdict
import numpy as np

N = 4
CUBE = list(itertools.product((0, 1), repeat=N))
PERMS = list(itertools.permutations(range(N)))


def knots():
    res = []
    def grow(start, E):
        if E:
            res.append(frozenset(s for s in CUBE if s not in E))
        for i in range(start, len(CUBE)):
            s = CUBE[i]
            if all(sum(a != b for a, b in zip(s, e)) >= 2 for e in E):
                grow(i + 1, E + [s])
    grow(0, [])
    return res


def permute(K, p):
    return frozenset(tuple(s[p[i]] for i in range(len(p))) for s in K)


def stabilizer(K):
    return [p for p in PERMS if permute(K, p) == K]


def orbit_key(K):
    return min(tuple(sorted(permute(K, p))) for p in PERMS)


def tensor(K):
    T = np.zeros((2,) * N, dtype=np.int64)
    for s in K:
        T[s] = 1
    return T


def matchings(items):
    if not items:
        yield []
        return
    a = items[0]
    for j in range(1, len(items)):
        for m in matchings(items[1:j] + items[j + 1:]):
            yield [(a, items[j])] + m


def connected(m, edges):
    adj = defaultdict(set)
    for a, b in edges:
        adj[a].add(b); adj[b].add(a)
    seen, st = {0}, [0]
    while st:
        u = st.pop()
        for w in adj[u]:
            if w not in seen:
                seen.add(w); st.append(w)
    return len(seen) == m


def canon(m, edges, legs):
    best = None
    for p in itertools.permutations(range(m)):
        e = tuple(sorted(tuple(sorted((p[a], p[b]))) for a, b in edges))
        l = tuple(legs[p.index(v)] for v in range(m))
        if best is None or (l, e) < best:
            best = (l, e)
    return best


def shapes(m, k=4, loops=False):
    out = {}
    for combo in itertools.combinations_with_replacement(range(m), k):
        cnt = Counter(combo)
        if max(cnt.values()) > N:
            continue
        legs = [cnt[v] for v in range(m)]
        slots = [(v, s) for v in range(m) for s in range(legs[v], N)]
        if len(slots) % 2:
            continue
        for mt in matchings(slots):
            if not loops and any(a[0] == b[0] for a, b in mt):
                continue
            edges = [(a[0], b[0]) for a, b in mt]
            if m > 1 and not connected(m, edges):
                continue
            key = canon(m, edges, legs)
            if key not in out:
                out[key] = (legs, mt)
    return list(out.values())


LETTERS = "abcdefghijklmnopqrstuvwxyz"


class Gadget:
    def __init__(self, m, legs, mt):
        self.m, self.legs, self.mt = m, legs, mt
        lab = {}
        k = 0
        for v in range(m):
            for s in range(legs[v]):
                lab[(v, s)] = LETTERS[k]; k += 1
        self.nlegs = k
        for j, (a, b) in enumerate(mt):
            lab[a] = lab[b] = LETTERS[self.nlegs + j]
        self.spec = ",".join("".join(lab[(v, s)] for s in range(N)) for v in range(m)) + "->" + LETTERS[:self.nlegs]
        self.chain = None

    def relation(self, tensors):
        R = np.einsum(self.spec, *tensors) > 0
        return frozenset(s for s in itertools.product((0, 1), repeat=self.nlegs) if R[s])

    def is_pair_chain(self):
        """copies in a path, consecutive copies sharing exactly two distinctions, two legs at each end copy"""
        mult = Counter(tuple(sorted((a[0], b[0]))) for a, b in self.mt)
        adj = defaultdict(set)
        for (u, w), c in mult.items():
            adj[u].add(w); adj[w].add(u)
        if any(c != 2 for c in mult.values()):
            return False
        if self.m == 1:
            return True
        ends = [v for v in range(self.m) if len(adj[v]) == 1]
        return len(mult) == self.m - 1 and len(ends) == 2 and all(self.legs[v] == 2 for v in ends) and \
            all(self.legs[v] == 0 for v in range(self.m) if v not in ends)


def survey(m_values=(2, 3), rand_m=(4,), rand_n=300, seed=20261029, loops=False, relations=None, log=print):
    allK = knots() if relations is None else relations
    orbits = {}
    for K in allK:
        orbits.setdefault(orbit_key(K), K)
    reps = list(orbits.values())
    placements = {}
    for K in reps:
        placements[orbit_key(K)] = sorted({permute(K, p) for p in PERMS}, key=sorted)
    rebuilt = defaultdict(set)        # orbit -> set of (m, shape index, is chain)
    outputs = defaultdict(Counter)    # orbit -> Counter of output orbit keys / 'full'
    excluded_drop = defaultdict(lambda: 0)
    for m in m_values:
        S = shapes(m, loops=loops)
        log(f"copies {m}: {len(S)} shapes", flush=True)
        for si, (legs, mt) in enumerate(S):
            G = Gadget(m, legs, mt)
            chain = G.is_pair_chain()
            for K in reps:
                key = orbit_key(K)
                P = [tensor(Q) for Q in placements[key]]
                for choice in itertools.product(range(len(P)), repeat=m):
                    R = G.relation([P[c] for c in choice])
                    if len(R) == 2 ** N:
                        outputs[key]["full"] += 1
                        continue
                    if R and all(sum(a != b for a, b in zip(s, e)) >= 2 for s in set(itertools.product((0, 1), repeat=N)) - R
                                 for e in set(itertools.product((0, 1), repeat=N)) - R if s != e):
                        okey = orbit_key(R)
                        outputs[key][okey] += 1
                        if okey == key:
                            rebuilt[key].add((m, si, chain))
                    else:
                        outputs[key]["not co-independent or empty"] += 1
    rng = random.Random(seed)
    for m in rand_m:
        made = 0
        while made < rand_n:
            combo = sorted(rng.choice(range(m)) for _ in range(4))
            cnt = Counter(combo)
            legs = [cnt[v] for v in range(m)]
            if max(legs) > N:
                continue
            slots = [(v, s) for v in range(m) for s in range(legs[v], N)]
            rng.shuffle(slots)
            mt = [(slots[2 * i], slots[2 * i + 1]) for i in range(len(slots) // 2)]
            if (not loops and any(a[0] == b[0] for a, b in mt)) or not connected(m, [(a[0], b[0]) for a, b in mt]):
                continue
            made += 1
            G = Gadget(m, legs, mt)
            chain = G.is_pair_chain()
            for K in reps:
                key = orbit_key(K)
                Ps = placements[key]
                choice = [tensor(rng.choice(Ps)) for _ in range(m)]
                R = G.relation(choice)
                if len(R) == 2 ** N:
                    outputs[key]["full"] += 1
                elif R and orbit_key(R) == key:
                    rebuilt[key].add((m, -1, chain))
                    outputs[key][key] += 1
                elif R:
                    outputs[key][orbit_key(R)] += 1
    return reps, placements, rebuilt, outputs


def describe(K):
    E = sorted(set(CUBE) - K)
    st = stabilizer(K)
    affine = len(E) == 8
    # pairwise between parities of complementary pairs: K = {x : (x_i+x_j, x_k+x_l) != (a, b)}
    pp = None
    for (i, j, k, l) in ((0, 1, 2, 3), (0, 2, 1, 3), (0, 3, 1, 2)):
        for a, b in itertools.product((0, 1), repeat=2):
            if K == frozenset(x for x in CUBE if ((x[i] + x[j]) % 2, (x[k] + x[l]) % 2) != (a, b)):
                pp = ((i, j), (k, l), (a, b))
    return {"excluded": len(E), "stabilizer": len(st), "affine": affine, "pairwise between pair parities": pp}


if __name__ == "__main__":
    T0 = time.time()
    reps, placements, rebuilt, outputs = survey()
    print(len(reps), "orbits", f"({time.time() - T0:.0f}s)")
    for key, sh in sorted(rebuilt.items(), key=lambda kv: -len(kv[1])):
        K = frozenset(key)
        print("rebuilt:", describe(K), "by", sorted(sh)[:12], "all chains:", all(c for (_, _, c) in sh))
    # flow arrows decrease excluded count?
    dec = True
    for key, cnt in outputs.items():
        for okey in cnt:
            if okey in ("full", "not co-independent or empty") or okey == key:
                continue
            if 16 - len(okey) >= 16 - len(key):
                dec = False
                print("non-decreasing arrow", describe(frozenset(key)), "->", describe(frozenset(okey)))
    print("arrows decrease excluded count (except rebuilt):", dec)
    print("non-co-independent outputs:", sum(c["not co-independent or empty"] for c in outputs.values()))
    print(f"done {time.time() - T0:.0f}s")
