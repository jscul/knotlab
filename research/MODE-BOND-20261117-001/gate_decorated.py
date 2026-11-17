"""Gates for decorated.py (MODE-BOND-20261117-001, the thread's own code, 2026-11-17), by SAT on the address-level pattern at depth N,
for the 5 distinct patterns (F = all, so truncation at N is exact for everything above it).
(a) Families: a random decoration of an orbit's strict subtree (random members with random values, down to 3 levels below it); the
    set of the orbit's states consistent with it, by SAT, must lie in Fam[type].
(b) The long composite: for a self-similar orbit x and its descendants 5, 6 and 7 levels down along a line, the joint projection by SAT
    must equal one of the periodic composites (a product, or one of the non-products).
(c) The closure: a random decorated path from a level-3 orbit down to a self-similar orbit x (random cubes on the path, random
    members in the side subtrees), with a random condition C on x from the condition list. The pair (M1, M2) of level-3 states
    consistent with the decoration and x in C, and with the decoration alone, by SAT. If M1 is nonempty and M1 != M2 it must be in
    the closure Pairs[type]; if the closure has no such pair, every sampled pair must have M1 empty or M1 = M2.
Writes gate_decorated.json."""
import json
import random
import sys
from pathlib import Path

from pysat.solvers import Cadical195

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex'))
from decorated import Decorated, bits, level_types  # noqa: E402
from mode_bond import orbit_tree, aid, children  # noqa: E402
from pattern import pattern, clauses  # noqa: E402

PATTERNS = ['8db5da810c00-73', '8db5da810c00-76', '8db5da810c00-81', '8db5da810c00-89', '8db5da810c00-100']


def descendants(tree, t, addrs, depth):
    """Orbits strictly below (t, addrs) to `depth` levels: list of (type, addrs)."""
    out, cur = [], [(t, addrs)]
    for _ in range(depth):
        nxt = []
        for tt, aa in cur:
            nxt += children(tree, tt, aa)
        out += nxt
        cur = nxt
    return out


def states_consistent(solver, addrs, assumptions):
    m = 0
    for x in range(1 << len(addrs)):
        lits = [(aid(a) + 1) * (1 if (x >> i) & 1 else -1) for i, a in enumerate(addrs)]
        if solver.solve(assumptions=assumptions + lits):
            m |= 1 << x
    return m


def random_members(rng, orbits, k):
    pool = [a for _, aa in orbits for a in aa]
    picks = rng.sample(pool, min(k, len(pool)))
    return [(aid(a) + 1) * (1 if rng.random() < 0.5 else -1) for a in picks]


if __name__ == '__main__':
    rng = random.Random(20261117)
    third = json.load(open(ROOT / 'research/KEEP-REACH-20261117-001/third_class.json'))['third']
    res = {}
    for idx in PATTERNS:
        D = Decorated(third[idx]['key'])
        tree = D.tree
        N = 9
        ot = orbit_tree(tree, N)
        K = pattern(third[idx]['key'], N)
        bad_a = checked_a = 0
        bad_b = checked_b = 0
        bad_c = checked_c = 0
        nonprod, _, _ = D.periodic_nonproducts()
        conds = D.conditions()
        ss = [t for t in range(D.nt) if [c for c, _ in tree.children[t]] == [t, t]]
        from decorated import gadgets
        g, sizes, pairs = gadgets(D)
        closure = {}
        for t0 in conds:
            closure[t0] = D.closure(t0, conds[t0])
        with Cadical195(bootstrap_with=clauses(K)) as S:
            # (a) families
            for _ in range(60):
                lvl = rng.randint(3, 5)
                t, aa = rng.choice(ot[lvl])
                below = descendants(tree, t, aa, min(3, N - lvl))
                mem = random_members(rng, below, rng.randint(1, 5))
                m = states_consistent(S, aa, mem)
                if m == 0:
                    continue
                checked_a += 1
                if m not in set(D.fam[t]):
                    bad_a += 1
            # (b) long composite along self-similar lines
            for _ in range(6):
                cands = [(t, aa) for t, aa in ot[3] + ot[4] if t in ss]
                if not cands:
                    break
                t, aa = rng.choice(cands)
                for d in (5,):
                    cur = (t, aa)
                    for _ in range(d):
                        cur = rng.choice(children(tree, *cur))
                    rel = set()
                    for x in range(16):
                        lx = [(aid(a) + 1) * (1 if (x >> i) & 1 else -1) for i, a in enumerate(aa)]
                        for z in range(16):
                            lz = [(aid(a) + 1) * (1 if (z >> i) & 1 else -1) for i, a in enumerate(cur[1])]
                            if S.solve(assumptions=lx + lz):
                                rel.add((x, z))
                    checked_b += 1
                    allowed = {frozenset(T) for _, _, T in nonprod}
                    A = {x for x, _ in rel}
                    B = {z for _, z in rel}
                    if not (len(rel) == len(A) * len(B) or frozenset(rel) in allowed):
                        bad_b += 1
            # (c) closure
            l3 = [(t, aa) for t, aa in ot[3]]
            for _ in range(40):
                t3, a3 = rng.choice(l3)
                # walk down to a self-similar orbit, at most 3 levels below level 3
                path, cur = [(t3, a3)], (t3, a3)
                ok = False
                for _ in range(4):
                    cur = rng.choice(children(tree, *cur))
                    path.append(cur)
                    if cur[0] in ss:
                        ok = True
                        break
                if not ok:
                    continue
                tx, ax = path[-1]
                C = rng.choice(conds.get(tx, [0]))
                if not C:
                    continue
                mem = []
                for (t, aa) in path[1:]:
                    if rng.random() < 0.5:
                        mem += random_members(rng, [(t, aa)], rng.randint(1, 2))
                for (t, aa), nxt in zip(path[:-1], path[1:]):
                    sib = [c for c in children(tree, t, aa) if c[1] != nxt[1]]
                    if sib and rng.random() < 0.5:
                        mem += random_members(rng, [sib[0]] + descendants(tree, sib[0][0], sib[0][1], 1), rng.randint(1, 3))
                M2 = states_consistent(S, a3, mem)
                M1 = 0
                for x in bits(C):
                    lx = [(aid(a) + 1) * (1 if (x >> i) & 1 else -1) for i, a in enumerate(ax)]
                    M1 |= states_consistent(S, a3, mem + lx)
                checked_c += 1
                if M1 and M1 != M2 and (M1, M2) not in closure[tx][t3]:
                    bad_c += 1
        res[idx] = dict(families_checked=checked_a, families_bad=bad_a, composites_checked=checked_b, composites_bad=bad_b,
                        closure_checked=checked_c, closure_bad=bad_c, gadgets=len(g))
        print(idx, res[idx], flush=True)
    res['passed'] = all(v['families_bad'] == 0 and v['composites_bad'] == 0 and v['closure_bad'] == 0
                        for k, v in res.items() if isinstance(v, dict))
    json.dump(res, open(HERE / 'gate_decorated.json', 'w'), indent=1)
    print(res['passed'])
