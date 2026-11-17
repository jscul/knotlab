"""The saturated composite automaton (TWO-ENDS-20261117-001, part B1, the thread's own code, 2026-11-17).

For a description with orbits of at most four addresses (window_tree.WindowTree), a saturated step from an orbit of type t to its
child ci is the relation between t's assignment x and the child's z: some assignment y of t's children with (x, y) in t's window, y
equal to z on child ci and feasible (F[r0]) on every other child. A downward path's state is (start type, current type, composite),
the composite restricted to feasible assignments at both ends. Breadth-first search over all child choices gives every state
reachable in exactly l steps, for l = 0, 1, ...; the sets of states by length are eventually periodic (threshold T, period q).

Growth test (advisor, design.md): if every composite of exactly l0 steps is a product (every pairing of its two projections occurs),
then so is every longer one (a product composed with a relation is a product), the allowed states factor across any window of l0
member-free levels at remaining depth >= R, and L >= (s - R) / l0 + 1 at every depth, with R = r0 + 1. Also reported: the composites
on the periodic part that are not products (the only way a bounded bond can cross a long stretch)."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'research/DIRECT-REACH-20261115-001/exploratory'))
from window_tree import WindowTree  # noqa: E402


def is_product(T):
    if not T:
        return True
    A = {a for a, _ in T}
    B = {b for _, b in T}
    return len(T) == len(A) * len(B)


def automaton(tree, lmax=400):
    F = tree.feasible(20)
    r0 = next(r for r in range(19) if F[r] == F[r + 1])
    Fc = F[r0]
    steps = {}
    for t in range(len(tree.types)):
        for ci in range(len(tree.children[t])):
            rel = tree.step(t, Fc, ci, frozenset((x, x) for x in range(1 << tree.m[t])))
            steps[(t, ci)] = rel

    def compose(T, t, ci):
        R = steps[(t, ci)]
        by = {}
        for x, z in R:
            by.setdefault(x, set()).add(z)
        c = tree.children[t][ci][0]
        return frozenset((a, z) for a, x in T for z in by.get(x, ()) if z in Fc[c])

    level = frozenset((t, t, frozenset((x, x) for x in Fc[t])) for t in range(len(tree.types)) if Fc[t])
    seen, seq = {}, []
    for l in range(lmax + 1):
        if level in seen:
            start = seen[level]
            break
        seen[level] = l
        seq.append(level)
        nxt = set()
        for t0, t, T in level:
            for ci in range(len(tree.children[t])):
                nxt.add((t0, tree.children[t][ci][0], compose(T, t, ci)))
        level = frozenset(nxt)
    else:
        raise RuntimeError('no repeat within %d' % lmax)
    period = len(seq) - start
    states = set().union(*seq)
    l0 = next((l for l, S in enumerate(seq) if all(is_product(T) for _, _, T in S)), None)
    cyc = set().union(*seq[start:])
    nonprod = [(t0, t, T) for t0, t, T in cyc if not is_product(T)]
    return dict(r0=r0, types=len(tree.types), states=len(states), threshold=start, period=period, l0=l0,
                periodic_states=len(cyc), periodic_nonproduct=len(nonprod), nonproduct_examples=nonprod[:3])


if __name__ == '__main__':
    import json
    third = json.load(open(ROOT / 'research/KEEP-REACH-20261117-001/third_class.json'))['third']
    for idx in sys.argv[1:]:
        r = automaton(WindowTree(third[idx]['key']))
        r.pop('nonproduct_examples')
        print(idx, r, flush=True)
