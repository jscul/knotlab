"""Finite checks of BOARD-DIST-20261110-001A's theorems. They calibrate the proofs; they prove nothing.

0. Theorem 1, truncations: every equivalence on B_1, and 2,000 random ones on B_2 and B_3 closed under
   the letter moves inside the ball, is the restriction of a finite board built as in the proof.
1. Theorem 5(a): two different finite boards differ on more and more pairs of names in B_L as L grows.
2. Theorem 7(b): a set of views admits compatible permutations iff its class counts balance (all 2^16
   subsets of a 16-view law and 3,000 random subsets of the full law).
3. Theorem 7(c): the swap of the proof turns every plane-like abelian view board found for the census's
   laws into a non-abelian one.
4. Theorem 4: for every finite board G with at most 4 places, the Cayley-type law with identity of
   indiscernibles at radius 0 allows exactly G among the finite boards with at most 6 places.
5. Theorem 8, the commutator rule: among the finite boards with at most 6 places, those identifying
   u with u x y X Y at every place are exactly the abelian ones.

Usage: check.py [--out result.json]
"""
import argparse
import itertools
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
LIB = os.path.join(ROOT, 'experiments', 'BOARD-DIST-20261110-001B', 'BOARD-DIST-20261110-001B-E001_which_boards_one_bit_laws_allow')
sys.path.insert(0, LIB)
import board_lib as bl  # noqa: E402

INVERSE = {'x': 'X', 'X': 'x', 'y': 'Y', 'Y': 'y'}
LIDX = {'x': 0, 'X': 1, 'y': 2, 'Y': 3}


def ball(L):
    words, layer = [''], ['']
    for _ in range(L):
        layer = [w + g for w in layer for g in 'xXyY' if not (w and w[-1] == INVERSE[g])]
        words.extend(layer)
    return words


def times(u, g):
    return u[:-1] if u and u[-1] == INVERSE[g] else u + g


def close(names, pairs):
    """The least equivalence on the ball containing pairs and closed under in-ball letter moves."""
    S = set(names)
    parent = {u: u for u in names}

    def find(u):
        while parent[u] != u:
            parent[u] = parent[parent[u]]
            u = parent[u]
        return u
    todo = list(pairs)
    while todo:
        u, v = todo.pop()
        a, b = find(u), find(v)
        if a == b:
            continue
        parent[a] = b
        cls = {}
        for w in names:
            cls.setdefault(find(w), []).append(w)
        for members in cls.values():
            for g in 'xXyY':
                img = [times(w, g) for w in members if times(w, g) in S]
                for i in range(1, len(img)):
                    if find(img[i]) != find(img[0]):
                        todo.append((img[0], img[i]))
    return {u: find(u) for u in names}


def extend_and_restrict(names, cls):
    """Theorem 1's construction: the partial injections on classes extended to permutations of the
    classes; read each name from the base class. Returns True when the restriction equals cls."""
    S = set(names)
    reps = sorted(set(cls.values()))
    idx = {r: i for i, r in enumerate(reps)}
    n = len(reps)
    perms = []
    for g in 'xy':
        part = {}
        for u in names:
            ug = times(u, g)
            if ug in S:
                a, b = idx[cls[u]], idx[cls[ug]]
                if part.get(a, b) != b:
                    return False
                part[a] = b
        if len(set(part.values())) != len(part):
            return False
        free_src = [i for i in range(n) if i not in part]
        free_dst = [i for i in range(n) if i not in set(part.values())]
        perm = dict(part)
        perm.update(zip(free_src, free_dst))
        perms.append(perm)
    sx, sy = perms
    six = {v: k for k, v in sx.items()}
    siy = {v: k for k, v in sy.items()}
    step = {'x': sx, 'X': six, 'y': sy, 'Y': siy}
    base = idx[cls['']]
    place = {}
    for u in names:
        p = base
        for g in u:
            p = step[g][p]
        place[u] = p
    return all((place[u] == place[v]) == (cls[u] == cls[v]) for u, v in itertools.combinations(names, 2))


def check0():
    out = {}
    names = ball(1)
    parts = 0
    good = 0
    for labels in itertools.product(range(5), repeat=5):
        if labels[0] != 0 or any(labels[i] > max(labels[:i]) + 1 for i in range(1, 5)):
            continue
        cls = {u: labels[i] for i, u in enumerate(names)}
        closed = close(names, [(u, v) for u, v in itertools.combinations(names, 2) if cls[u] == cls[v]])
        if all((closed[u] == closed[v]) == (cls[u] == cls[v]) for u, v in itertools.combinations(names, 2)):
            parts += 1
            good += extend_and_restrict(names, closed)
    out['B1'] = {'closed_partitions': parts, 'extend': good}
    rng = random.Random(92)
    for L in (2, 3):
        names = ball(L)
        good = 0
        for _ in range(2000 if L == 2 else 300):
            k = rng.randint(1, 4)
            pairs = [tuple(rng.sample(names, 2)) for _ in range(k)]
            good += extend_and_restrict(names, close(names, pairs))
        out['B%d' % L] = {'samples': 2000 if L == 2 else 300, 'extend': good}
    out['passed'] = out['B1']['extend'] == out['B1']['closed_partitions'] and all(
        out['B%d' % L]['extend'] == out['B%d' % L]['samples'] for L in (2, 3))
    return out


def place_of(board, u):
    sx, sy = board
    step = {'x': sx, 'X': bl._inverse(sx), 'y': sy, 'Y': bl._inverse(sy)}
    p = 0
    for g in u:
        p = step[g][p]
    return p


def check1():
    boards = bl.finite_boards(3) + bl.finite_boards(4)
    rng = random.Random(92)
    rows = []
    for _ in range(40):
        a, b = rng.sample(boards, 2)
        diffs = []
        for L in (1, 2, 3, 4):
            names = ball(L)
            pa = {u: place_of(a, u) for u in names}
            pb = {u: place_of(b, u) for u in names}
            diffs.append(sum((pa[u] == pa[v]) != (pb[u] == pb[v]) for u, v in itertools.combinations(names, 2)))
        rows.append(diffs)
    grows = sum(1 for d in rows if d[-1] > d[-2] > 0 or (d[-1] > 0 and d[-1] >= 2 * max(1, d[0])))
    return {'pairs': len(rows), 'differ_more_at_L4': grows, 'examples': rows[:5], 'passed': grows == len(rows)}


def balanced(V, g):
    src = [(bl.centre(t), bl.nb(t, g)) for t in V]
    dst = [(bl.nb(t, bl.INV[g]), bl.centre(t)) for t in V]
    return sorted(src) == sorted(dst)


def has_perms(V, g):
    """Existence of a compatible permutation by bipartite matching (independent of the counts)."""
    V = list(V)
    match = {}

    def aug(t, seen):
        for u in V:
            if bl.compat(t, g, u) and u not in seen:
                seen.add(u)
                if u not in match or aug(match[u], seen):
                    match[u] = t
                    return True
        return False
    return all(aug(t, set()) for t in V)


def check2():
    law = bl.lifelike_mask(bl.PARITY0)
    T = bl.patterns_of(law)
    agree = total = 0
    for mask in range(1, 1 << len(T)):
        V = [T[i] for i in range(len(T)) if (mask >> i) & 1]
        for g in (bl.X_, bl.Y_):
            total += 1
            agree += balanced(V, g) == has_perms(V, g)
    rng = random.Random(92)
    full = list(range(32))
    for _ in range(3000):
        V = rng.sample(full, rng.randint(1, 32))
        for g in (bl.X_, bl.Y_):
            total += 1
            agree += balanced(V, g) == has_perms(V, g)
    return {'tests': total, 'agree': agree, 'passed': agree == total}


def swap(V, sx, sy):
    """Theorem 7(c)'s swap: two sources in one x-class, exchange their targets."""
    for t1, t2 in itertools.combinations(V, 2):
        if (bl.centre(t1), bl.nb(t1, bl.X_)) == (bl.centre(t2), bl.nb(t2, bl.X_)):
            nx = dict(sx)
            nx[t1], nx[t2] = sx[t2], sx[t1]
            return nx
    return None


def check3(keys):
    done = nonab = 0
    for m in keys:
        L = bl.lifelike_mask(m)
        cert = bl.ioi1_sat(L, 'planelike')
        if cert is None:
            continue
        V, sx, sy = cert
        nx = swap(V, sx, sy)
        done += 1
        if nx is not None and bl.verify_ioi1(L, V, nx, sy) and any(nx[sy[t]] != sy[nx[t]] for t in V):
            nonab += 1
    return {'planelike_boards': done, 'swapped_nonabelian': nonab, 'passed': done == nonab and done > 0}


def check4():
    small = bl.finite_boards(1) + bl.finite_boards(2) + bl.finite_boards(3) + bl.finite_boards(4)
    targets = small
    others = small + bl.finite_boards(5) + bl.finite_boards(6)
    ok = 0
    for G in targets:
        gx, gy = G
        allowed = []
        for j, H in enumerate(others):
            hx, hy = H
            if len(hx) != len(gx):
                continue
            # an allowed colouring of H: equivariant c with c(hx v) = gx c(v), c(hy v) = gy c(v), injective
            found = False
            for c0 in range(len(gx)):
                c = {0: c0}
                stack = [0]
                good = True
                while stack and good:
                    v = stack.pop()
                    for (h, g) in ((hx, gx), (hy, gy), (bl._inverse(hx), bl._inverse(gx)), (bl._inverse(hy), bl._inverse(gy))):
                        w, cw = h[v], g[c[v]]
                        if w in c:
                            if c[w] != cw:
                                good = False
                                break
                        else:
                            c[w] = cw
                            stack.append(w)
                if good and len(set(c.values())) == len(c):
                    found = True
                    break
            if found:
                allowed.append(j)
        same = [j for j in allowed if bl.canon(*others[j])[0] == bl.canon(*G)[0]]
        ok += len(allowed) == 1 and len(same) == 1
    return {'targets': len(targets), 'exactly_one_allowed': ok, 'passed': ok == len(targets)}


def check5():
    boards = []
    for n in range(1, 7):
        boards.extend(bl.finite_boards(n))
    agree = 0
    for b in boards:
        sx, sy = b
        six, siy = bl._inverse(sx), bl._inverse(sy)
        closes = all(siy[six[sy[sx[v]]]] == v for v in range(len(sx)))
        agree += closes == bl.is_abelian(sx, sy)
    return {'boards': len(boards), 'agree': agree, 'passed': agree == len(boards)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(HERE, 'result.json'))
    args = ap.parse_args()
    res = {'check0_truncations': check0(), 'check1_changes_are_infinite': check1(),
           'check2_balance': check2(),
           'check3_swap': check3([m for m in range(1024)]),
           'check4_finite_forcing': check4(), 'check5_commutator': check5()}
    res['passed'] = all(v['passed'] for v in res.values())
    res['status'] = 'passed' if res['passed'] else 'failed'
    with open(args.out, 'w') as fh:
        json.dump(res, fh, indent=1, sort_keys=True)
    print(json.dumps({k: (v['passed'] if isinstance(v, dict) else v) for k, v in res.items()}, indent=1))


if __name__ == '__main__':
    main()
