"""Independent check of the carriers' bonds (CARRIER-20261117-001, the thread's own code, 2026-11-17): for each of the 25 open patterns
at depth N and s, find a least orbit-and-block or stem bond on an actual pair of orbits (address level, as gate_window_tree), map its
bits to addresses, and check by SAT on the whole depth-N pattern that the set is constrained and every subset one smaller is free
(so it is a bond meeting level 3 and level 3 + s). Writes verify_bonds.json. Usage: verify_bonds.py [N] [s ...]."""
import itertools
import json
import sys
from pathlib import Path

from pysat.solvers import Cadical195

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'research/DIRECT-REACH-20261115-001/exploratory'))
sys.path.insert(0, str(ROOT / 'experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex'))
from head_bond import WindowTree, free_flags  # noqa: E402
from gate_window_tree import aid, orbits_by_level, joint_exact  # noqa: E402
from gate_head import stem_exact  # noqa: E402
from pattern import pattern, clauses  # noqa: E402


def least_set(rows, mu, nh, mv, nc, cap):
    n = nh + mv + nc
    free = free_flags(rows, n)
    vmask, umask = ((1 << mv) - 1) << nh, (1 << mu) - 1
    for size in range(2, min(cap, n) + 1):
        for S in itertools.combinations(range(n), size):
            M = sum(1 << i for i in S)
            if (M & umask) and (M & vmask) and not free[M] and all(free[M & ~(1 << i)] for i in S):
                return S
    return None


def is_bond(K, vs):
    with Cadical195(bootstrap_with=clauses(K)) as s:
        def free(sub):
            return all(s.solve(assumptions=[v + 1 if b else -(v + 1) for v, b in zip(sub, bits)])
                       for bits in itertools.product((0, 1), repeat=len(sub)))
        return (not free(vs)) and all(free([v for j, v in enumerate(vs) if j != i]) for i in range(len(vs)))


def carriers(tree, N, F, lv, k, ks):
    """Yield (kind, rows, mu, nh, mv, nc, addresses) for every pair O_u at level k, O_v at level ks."""
    for iu in range(len(lv[k])):
        for iv in range(len(lv[ks])):
            t1, t2 = lv[k][iu][0], lv[ks][iv][0]
            mu, mv = tree.m[t1], tree.m[t2]
            if ks < N:
                J = joint_exact(tree, N, F, lv, iu, k, iv, ks)
                by_x = {}
                for x, y in tree.W[t2]:
                    if all(tree.restrict(y, pos) in F[N - ks - 1][c] for c, pos in tree.children[t2]):
                        by_x.setdefault(x, []).append(y)
                rows = frozenset(a | (x << mu) | (y << (mu + mv)) for a, x in J for y in by_x.get(x, ()))
                av = lv[ks][iv][2]
                yield ('block', rows, mu, mu, mv, 2 * mv,
                       list(lv[k][iu][2]) + list(av) + [av[p // 2] + (p % 2,) for p in range(2 * mv)])
            if ks - k > 2:
                rows, addrs = stem_exact(tree, N, F, lv, iu, k, iv, ks, 2)
                nh = len(addrs) - mv
                yield ('stem', rows, mu, nh, mv, 0, addrs)


if __name__ == '__main__':
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 11
    s_values = [int(x) for x in sys.argv[2:]] or [5, 6]
    third = json.load(open(ROOT / 'research/KEEP-REACH-20261117-001/third_class.json'))['third']
    open25 = [i for i, r in third.items() if not r['kind'].startswith('forget')]
    block = json.load(open(HERE / 'block_25.json'))
    stems = {json.load(open(f))['index']: json.load(open(f)) for f in (HERE / 'head').glob('*_d2.json')}

    def at(e, r, s, first, R):
        P = e['sequences']['r=%d' % r if r < R else 'r>=%d' % R]
        j = s - first
        while j >= len(P):
            j -= e['period']
        return P[j] if j >= 0 else None

    def expected(idx, s):
        vals = [at(block[idx], N - 3 - s, s, 1, block[idx]['r0'] + 1)]
        if idx in stems:
            vals.append(at(stems[idx], N - 3 - s, s, 3, stems[idx]['r0']))
        vals = [v for v in vals if v is not None]
        return min(vals) if vals else None

    out = {}
    for idx in open25:
        key = third[idx]['key']
        tree = WindowTree(key)
        F = tree.feasible(N + 2)
        lv = orbits_by_level(tree, N, F)
        K = pattern(key, N)
        res = {}
        for s in s_values:
            best, want = None, expected(idx, s)
            if want is None:
                res[s] = None
                continue
            for kind, rows, mu, nh, mv, nc, addrs in carriers(tree, N, F, lv, 3, 3 + s):
                if not rows or len(addrs) > 18:
                    continue
                S = least_set(rows, mu, nh, mv, nc, want)
                if S is not None:
                    best = (kind, S, [aid(addrs[i]) for i in S])
                    break
            if best is None:
                res[s] = dict(expected=want, found=None)
                continue
            ok = is_bond(K, best[2])
            res[s] = dict(expected=want, kind=best[0], size=len(best[1]), addresses=best[2], sat_bond=ok)
        out[idx] = res
        print(idx, {s: (r and (r.get('kind'), r.get('size'), r.get('sat_bond'), r['expected'])) for s, r in res.items()}, flush=True)
        json.dump(dict(N=N, s=s_values, results=out), open(HERE / ('verify_bonds_N%d.json' % N), 'w'), indent=1)
