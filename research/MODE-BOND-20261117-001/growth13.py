"""Why the 13 grow (MODE-BOND-20261117-001, the thread's own code, 2026-11-17).

The decorated test found no gadget for any of the 5 patterns. The reason is plain once the blocks are read: in the blocks of the
self-similar type and of its two parent types, every knot lies in the orbit and its first child, so the second child is joined to its
parent by no knot. Every self-similar orbit is a second child of a self-similar or a parent-type orbit, so all the self-similar
subtrees lie in components that never reach level 3. A bond lies in one component.

This script, for each of the 5 patterns:
1. lists each block's joined children (those holding a member of some knot of the block);
2. runs the saturated composite automaton (composite.py's construction) along joined children only, from the types joined to a
   level-3 orbit, and reads l0, the length from which every composite is a product (Theorem G's hypothesis on the component);
3. checks by the census's component labelling (pattern.components) at depth 11 that no address of a self-similar orbit shares a
   component with a level-3 address.
Writes growth13.json."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'research/TWO-ENDS-20261117-001'))
sys.path.insert(0, str(ROOT / 'experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex'))
from decorated import Decorated, level_types  # noqa: E402
from composite import is_product  # noqa: E402
from mode_bond import orbit_tree, aid  # noqa: E402
from pattern import pattern, components  # noqa: E402

PATTERNS = ['8db5da810c00-73', '8db5da810c00-76', '8db5da810c00-81', '8db5da810c00-89', '8db5da810c00-100']


def joined_children(tree, t):
    T = tree.types[t]
    m = len(T)
    nv, knots = tree.D.window(T)
    used = {v for k in knots for v in k if v >= m}
    return [ci for ci, (c, pos) in enumerate(tree.children[t]) if any(m + p in used for p in pos)]


def joined_automaton(D, lmax=400):
    tree, Fc = D.tree, D.Fc
    joined = {t: joined_children(tree, t) for t in range(D.nt)}
    reach = set(level_types(tree, 3))
    frontier = list(reach)
    while frontier:
        t = frontier.pop()
        for ci in joined[t]:
            c = tree.children[t][ci][0]
            if c not in reach:
                reach.add(c)
                frontier.append(c)
    steps = {(t, ci): tree.step(t, Fc, ci, frozenset((x, x) for x in Fc[t])) for t in reach for ci in joined[t]}

    def compose(T, t, ci):
        by = {}
        for x, z in steps[(t, ci)]:
            by.setdefault(x, set()).add(z)
        c = tree.children[t][ci][0]
        return frozenset((a, z) for a, x in T for z in by.get(x, ()) if z in Fc[c])

    level = frozenset((t, t, frozenset((x, x) for x in Fc[t])) for t in reach)
    seen, seq = {}, []
    for l in range(lmax + 1):
        if level in seen:
            start = seen[level]
            break
        seen[level] = l
        seq.append(level)
        level = frozenset((t0, tree.children[t][ci][0], compose(T, t, ci)) for t0, t, T in level for ci in joined[t])
    period = len(seq) - start
    l0 = next((l for l, S in enumerate(seq) if all(is_product(T) for _, _, T in S)), None)
    nonprod_periodic = sum(1 for S in seq[start:] for _, _, T in S if not is_product(T))
    return dict(joined={str(t): v for t, v in joined.items()}, component_types=sorted(reach), states=len(set().union(*seq)),
                threshold=start, period=period, l0=l0, periodic_nonproducts=nonprod_periodic)


if __name__ == '__main__':
    third = json.load(open(ROOT / 'research/KEEP-REACH-20261117-001/third_class.json'))['third']
    out = {}
    for idx in PATTERNS:
        D = Decorated(third[idx]['key'])
        a = joined_automaton(D)
        ss = [t for t in range(D.nt) if [c for c, _ in D.tree.children[t]] == [t] * len(D.tree.children[t])]
        N = 11
        K = pattern(third[idx]['key'], N)
        lab = components(K, (1 << (N + 1)) - 1)
        ot = orbit_tree(D.tree, N)
        top = {lab[aid(a_)] for _, aa in ot[3] for a_ in aa}
        ss_addr = [aid(a_) for n in range(N + 1) for t, aa in ot[n] if t in ss for a_ in aa]
        shared = sum(1 for v in ss_addr if lab[v] in top)
        out[idx] = dict(self_similar=ss, **a, depth=N, self_similar_addresses=len(ss_addr), sharing_a_component_with_level3=shared)
        print(idx, {k: v for k, v in out[idx].items() if k != 'joined'}, flush=True)
    json.dump(out, open(HERE / 'growth13.json', 'w'), indent=1)
