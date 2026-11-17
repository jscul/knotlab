"""Exploratory (KEEP-REACH-20261117-001, after the read-out): for third-class mutants, from level 3 at stable depth, s = 1..12: whether
some two-orbit joint is non-product, the least two-orbit bond, and whether every non-product joint's missing pairs are exposed
(advisor's lemma: an exposed missing pair gives a bond meeting both orbits)."""
import itertools
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'research/DIRECT-REACH-20261115-001/exploratory'))
from look_four import rectangular  # noqa: E402
from two_orbit import least_cross_bond  # noqa: E402
import window_tree as W  # noqa: E402


def pair_states(tree, k, smax):
    F = tree.feasible(12)
    r0 = next(r for r in range(12) if F[r] == F[r + 1])
    Fc = F[r0]
    st = W.level_states(tree, k, [Fc] * (k + 2))
    S0 = {(t, t, frozenset((x, x) for x in up)) for t, up in st[k]}
    for b in range(k):
        for t, up in st[b]:
            kids = tree.children[t]
            for c1, c2 in itertools.permutations(range(len(kids)), 2):
                J = {(tree.restrict(y, kids[c1][1]), tree.restrict(y, kids[c2][1])) for x, y in tree.W[t]
                     if x in up and all(tree.restrict(y, pos) in Fc[c] for kk, (c, pos) in enumerate(kids) if kk not in (c1, c2))}
                cur = {(kids[c1][0], kids[c2][0], frozenset(J))}
                for lvl in range(b + 1, k):
                    nxt = set()
                    for t1, t2, J in cur:
                        for ci in range(len(tree.children[t1])):
                            rel = tree.step(t1, Fc, ci, frozenset((z2, z1) for z1, z2 in J))
                            J1 = frozenset((z1, z2) for z2, z1 in rel)
                            for cj in range(len(tree.children[t2])):
                                nxt.add((tree.children[t1][ci][0], tree.children[t2][cj][0], tree.step(t2, Fc, cj, J1)))
                    cur = nxt
                for t1, t2, J in cur:
                    S0.add((t1, t2, frozenset((a, z) for a, z in J if a in Fc[t1])))
    S = frozenset(S0)
    out = []
    for s in range(1, smax + 1):
        S = frozenset((t1, tree.children[t2][cj][0], tree.step(t2, Fc, cj, J)) for t1, t2, J in S for cj in range(len(tree.children[t2])))
        out.append([(t1, t2, frozenset((a, z) for a, z in J if z in Fc[t2])) for t1, t2, J in S])
    return out


def exposed(states, m):
    """States of an orbit (marginal set) that are exposed: some subset T free on the marginal, with the state the only one with its
    restriction to T."""
    out = set()
    for x in states:
        for size in range(0, m + 1):
            for T in itertools.combinations(range(m), size):
                proj = {tuple((y >> i) & 1 for i in T) for y in states}
                if len(proj) != 1 << len(T):
                    continue
                if sum(1 for y in states if all(((y >> i) & 1) == ((x >> i) & 1) for i in T)) == 1:
                    out.add(x)
                    break
            if x in out:
                break
    return out


if __name__ == '__main__':
    rows = [json.loads(l) for l in open(HERE.parent / 'mutants_keep.jsonl')] + [json.loads(l) for l in open(HERE.parent / 'sample_keep.jsonl')]
    pick = [r for r in rows if r.get('small_orbits') and r.get('alive_every_depth') and r.get('r_all') is None and not r.get('timeout')
            and not r['two_orbit_every_s']]
    res = {}
    for r in pick:
        tree = W.WindowTree(r['key'])
        seq = pair_states(tree, 3, 12)
        line = []
        for s, joints in enumerate(seq, 1):
            nonprod = [(t1, t2, J) for t1, t2, J in joints if J and not rectangular(J)]
            cross = [least_cross_bond(J, tree.m[t1], tree.m[t2]) for t1, t2, J in joints]
            cross = [c for c in cross if c]
            unexposed = 0
            for t1, t2, J in nonprod:
                A = {a for a, _ in J}
                B = {z for _, z in J}
                ea, eb = exposed(A, tree.m[t1]), exposed(B, tree.m[t2])
                missing = [(a, z) for a in A for z in B if (a, z) not in J]
                if not any(a in ea and z in eb for a, z in missing):
                    unexposed += 1
            line.append((s, len(nonprod), min(cross) if cross else None, unexposed))
        res[str(r['index'])] = line
        print(r['index'], line, flush=True)
    json.dump(res, open(HERE / 'third_detail.json', 'w'), indent=1)
