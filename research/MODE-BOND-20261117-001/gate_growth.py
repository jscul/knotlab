"""Gate for growth13.py (MODE-BOND-20261117-001, the thread's own code, 2026-11-17), by SAT on the address-level pattern at depth 11,
for the 5 patterns: every pair (O, O') with O at level 3 or 4 in the component of level 3 and O' a descendant 5 or 6 levels below
along joined children has a pair projection that is a product (Theorem G's hypothesis on the component, l0 = 5). Also: for every
self-similar orbit at levels 4 to 6, the pair projection with its parent is a product (no knot joins them). Writes gate_growth.json."""
import json
import sys
from pathlib import Path

from pysat.solvers import Cadical195

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex'))
from decorated import Decorated  # noqa: E402
from growth13 import joined_children, PATTERNS  # noqa: E402
from mode_bond import orbit_tree, aid, children  # noqa: E402
from pattern import pattern, clauses  # noqa: E402


def pair_projection(S, A, B):
    rel = set()
    for x in range(1 << len(A)):
        lx = [(aid(a) + 1) * (1 if (x >> i) & 1 else -1) for i, a in enumerate(A)]
        if not S.solve(assumptions=lx):
            continue
        for z in range(1 << len(B)):
            lz = [(aid(b) + 1) * (1 if (z >> i) & 1 else -1) for i, b in enumerate(B)]
            if S.solve(assumptions=lx + lz):
                rel.add((x, z))
    return rel


def is_product(rel):
    return len(rel) == len({x for x, _ in rel}) * len({z for _, z in rel})


if __name__ == '__main__':
    third = json.load(open(ROOT / 'research/KEEP-REACH-20261117-001/third_class.json'))['third']
    out = {}
    N = 11
    for idx in PATTERNS:
        D = Decorated.__new__(Decorated)
        from window_tree import WindowTree
        D.tree = WindowTree(third[idx]['key'])
        tree = D.tree
        joined = {t: joined_children(tree, t) for t in range(len(tree.types))}
        ss = [t for t in range(len(tree.types)) if [c for c, _ in tree.children[t]] == [t] * len(tree.children[t])]
        K = pattern(third[idx]['key'], N)
        ot = orbit_tree(tree, N)
        checked = bad = 0
        sep_checked = sep_bad = 0
        with Cadical195(bootstrap_with=clauses(K)) as S:
            for lvl in (3, 4):
                for t, aa in ot[lvl]:
                    if t in ss:
                        continue
                    frontier = [(t, aa)]
                    for depth in range(1, 7):
                        nxt = []
                        for tt, a2 in frontier:
                            for ci in joined[tt]:
                                nxt.append(children(tree, tt, a2)[ci])
                        frontier = nxt
                        if depth in (5, 6):
                            for t2, b2 in frontier:
                                checked += 1
                                if not is_product(pair_projection(S, aa, b2)):
                                    bad += 1
            for lvl in (4, 5, 6):
                for t, aa in ot[lvl - 1]:
                    for ci, (c, ba) in enumerate(children(tree, t, aa)):
                        if c in ss and ci not in joined[t]:
                            sep_checked += 1
                            if not is_product(pair_projection(S, aa, ba)):
                                sep_bad += 1
        out[idx] = dict(depth=N, joined_pairs_checked=checked, joined_pairs_not_product=bad,
                        unjoined_self_similar_children_checked=sep_checked, not_product=sep_bad)
        print(idx, out[idx], flush=True)
    out['passed'] = all(v['joined_pairs_not_product'] == 0 and v['not_product'] == 0 for v in out.values() if isinstance(v, dict))
    json.dump(out, open(HERE / 'gate_growth.json', 'w'), indent=1)
    print(out['passed'])
