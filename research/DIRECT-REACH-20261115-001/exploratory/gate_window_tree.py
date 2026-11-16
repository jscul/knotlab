"""Gate for window_tree.py (the thread's own): exact joints J of two orbits against SAT projections of the full pattern, and life
F_N against SAT, on the population-D descriptions with orbits of at most 4 addresses, at depth N = 6 by default, or the depth given as the first argument (address-level, no merging)."""
import itertools
import random
import sys
from pathlib import Path

from pysat.solvers import Cadical195

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex'))
from window_tree import WindowTree  # noqa: E402
from window_types import population_D  # noqa: E402
from pattern import pattern, clauses  # noqa: E402


def aid(addr):
    n = len(addr)
    return int(''.join(map(str, addr)) or '0', 2) + (1 << n) - 1


def orbits_by_level(tree, N, F):
    """Address-level orbits with Up messages: level -> list of (type, Up, addresses)."""
    out = {0: [(0, frozenset(range(2)), [()])]}
    for n in range(N):
        nxt = []
        for t, up, addrs in out[n]:
            for ci, (c, pos) in enumerate(tree.children[t]):
                rel = tree.step(t, F[N - n - 1], ci, frozenset((0, x) for x in up))
                nxt.append((c, frozenset(z for _, z in rel), [addrs[p // 2] + (p % 2,) for p in pos]))
        out[n + 1] = nxt
    return out


def joint_exact(tree, N, F, lv, iu, k, iv, ks):
    """J for orbit iu at level k and orbit iv at level ks, by the tree path (address-level)."""
    # find ancestors: rebuild paths by address prefix of the first member is not valid (orbits are not prefix-closed), so search
    parent = {}
    for n in range(ks):
        idx = 0
        for pi, (t, up, addrs) in enumerate(lv[n]):
            for ci, (c, pos) in enumerate(tree.children[t]):
                parent[(n + 1, idx)] = (n, pi, ci)
                idx += 1
    def chain(n, i):
        out = [(n, i)]
        while n > 0:
            n, i, _ = parent[(n, i)]
            out.append((n, i))
        return out[::-1]
    cu, cv = chain(k, iu), chain(ks, iv)
    b = max(j for j in range(len(cu)) if j < len(cv) and cu[j] == cv[j])
    Bn, Bi = cu[b]
    tB, upB, _ = lv[Bn][Bi]
    def child_index(n, i):
        return parent[(n, i)][2]
    if (Bn, Bi) == (k, iu):
        J = frozenset((x, x) for x in upB)
        cur_t = tB
        for (n, i) in cv[b + 1:]:
            ci = child_index(n, i)
            J = tree.step(cur_t, F[N - n], ci, J)
            cur_t = lv[n][i][0]
        return frozenset((a, z) for a, z in J if z in F[N - ks][cur_t])
    kids = tree.children[tB]
    c1, c2 = child_index(*cu[b + 1]), child_index(*cv[b + 1])
    J = set()
    for x, y in tree.W[tB]:
        if x in upB and all(tree.restrict(y, pos) in F[N - Bn - 1][c] for kk, (c, pos) in enumerate(kids) if kk not in (c1, c2)):
            J.add((tree.restrict(y, kids[c1][1]), tree.restrict(y, kids[c2][1])))
    J = frozenset(J)
    t1, t2 = kids[c1][0], kids[c2][0]
    for (n, i) in cu[b + 2:]:
        ci = child_index(n, i)
        rel = tree.step(t1, F[N - n], ci, frozenset((z2, z1) for z1, z2 in J))
        J = frozenset((z1, z2) for z2, z1 in rel)
        t1 = lv[n][i][0]
    for (n, i) in cv[b + 2:]:
        ci = child_index(n, i)
        J = tree.step(t2, F[N - n], ci, J)
        t2 = lv[n][i][0]
    return frozenset((a, z) for a, z in J if a in F[N - k][t1] and z in F[N - ks][t2])


def joint_sat(K, au, av):
    allv = [aid(a) for a in au] + [aid(a) for a in av]
    out = set()
    with Cadical195(bootstrap_with=clauses(K)) as s:
        for bits in itertools.product((0, 1), repeat=len(allv)):
            if len(set(allv)) < len(allv):
                raise AssertionError('orbit overlap')
            if s.solve(assumptions=[v + 1 if b else -(v + 1) for v, b in zip(allv, bits)]):
                a = sum(b << i for i, b in enumerate(bits[:len(au)]))
                z = sum(b << i for i, b in enumerate(bits[len(au):]))
                out.add((a, z))
    return frozenset(out)


if __name__ == '__main__':
    rng = random.Random(20261115)
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    checked = mism = cases = 0
    life_checked = life_mism = 0
    for cid, key, prof, cls in population_D():
        try:
            tree = WindowTree(key)
        except ValueError:
            continue
        cases += 1
        F = tree.feasible(max(N, 6) + 2)
        for n in range(2, max(N, 6) + 3):
            with Cadical195(bootstrap_with=clauses(pattern(key, n))) as s:
                life_checked += 1
                life_mism += (s.solve() != bool(F[n][0]))
        lv = orbits_by_level(tree, N, F)
        K = pattern(key, N)
        for _ in range(6):
            k = rng.randint(1, 3)
            ks = rng.randint(k + 1, N)
            iu, iv = rng.randrange(len(lv[k])), rng.randrange(len(lv[ks]))
            J1 = joint_exact(tree, N, F, lv, iu, k, iv, ks)
            J2 = joint_sat(K, lv[k][iu][2], lv[ks][iv][2])
            checked += 1
            if J1 != J2:
                mism += 1
                print('MISMATCH', cid[:12], k, ks, iu, iv, len(J1), len(J2))
    print('cases', cases, 'joints checked', checked, 'mismatches', mism, 'life checks', life_checked, 'life mismatches', life_mism)
