"""Mode bonds (MODE-BOND-20261117-001, the thread's own code, 2026-11-17).

For the 13 mutants of 8db5da810c00, every saturated composite of five or more steps is a product except the two along the
self-similar type (children both of its own type), which carry the class of an all-equal orbit (TWO-ENDS-20261117-001). A bond across
a long member-free stretch must cross it along such a line. This builds the real pattern with the self-similar subtree of one orbit X
cut down to a single path of L0 steps to an orbit V, and runs the census's certified least-bond search for a bond with a member at
level 3 and one in V, its members restricted to the region outside the path, plus V.

Exactness. For these patterns F[r] holds every assignment of every orbit of four addresses at every r, so a full subtree hanging
below a kept orbit can be dropped with its knots: every assignment of the kept orbit extends into it. The path's interior and the
siblings along it are kept as variables but not allowed as members, so the projection onto the allowed region is that of the real
pattern, with the path's composite between X and V. A path of the same composite exists at every length L0 + 2j (Lemma S, threshold
5, period 2), so a bond found here is a bond of the real pattern at every depth for s = level(V) - 3 + 2j, j >= 0, with the members
outside the path in the same places.

build() returns the pruned knots and the variable sets; search_mode() runs the search."""
import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'research/DIRECT-REACH-20261115-001/exploratory'))
LEVEL = ROOT / 'experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex'
sys.path.insert(0, str(LEVEL))
from window_tree import WindowTree  # noqa: E402
from pattern import pattern  # noqa: E402


def aid(addr):
    n = len(addr)
    return int(''.join(map(str, addr)) or '0', 2) + (1 << n) - 1


def orbit_tree(tree, N):
    """Address-level orbits: level -> list of (type, addresses), children computed from the type's positions."""
    out = {0: [(0, [()])]}
    for n in range(N):
        nxt = []
        for t, addrs in out[n]:
            for c, pos in tree.children[t]:
                nxt.append((c, [addrs[p // 2] + (p % 2,) for p in pos]))
        out[n + 1] = nxt
    return out


def children(tree, t, addrs):
    return [(c, [addrs[p // 2] + (p % 2,) for p in pos]) for c, pos in tree.children[t]]


def self_similar(tree):
    return [t for t in range(len(tree.types)) if [c for c, _ in tree.children[t]] == [t] * len(tree.children[t])]


def build(key, a, xi, L0, m_out, choice=0, v_children=False):
    """X = the xi-th orbit at level a (must be self-similar); path of L0 steps taking child `choice` each time; the region outside X's
    subtree kept to level m_out. Returns dict(K, nvars, A, B, allowed, X, V, path, levels)."""
    tree = WindowTree(key)
    F = tree.feasible(12)
    full = [t for t in range(len(tree.types)) if tree.m[t] == 4]
    assert all(len(F[r][t]) == 16 for r in range(12) for t in full), 'F is not every assignment: pruning would not be exact'
    ot = orbit_tree(tree, max(m_out, a))
    tX, X = ot[a][xi]
    assert tX in self_similar(tree), 'X is not of the self-similar type'
    depth = max(m_out, a + L0 + (1 if v_children else 0))
    K = pattern(key, depth)
    xset = set(map(tuple, X))
    keep = set()
    for n in range(m_out + 1):
        for t, addrs in ot.get(n, []):
            for ad in addrs:
                if not any(ad[:a] == x and len(ad) > a for x in xset):
                    keep.add(ad)
    keep |= xset
    path, side = [(tX, X)], []
    for _ in range(L0):
        t, addrs = path[-1]
        ch = children(tree, t, addrs)
        path.append(ch[choice])
        side += [c for i, c in enumerate(ch) if i != choice]
    for t, addrs in path[1:] + side:
        keep |= set(map(tuple, addrs))
    tV, V = path[-1]
    if v_children:
        for c in children(tree, tV, V):
            keep |= set(map(tuple, c[1]))
    ids = sorted(aid(x) for x in keep)
    index = {v: i for i, v in enumerate(ids)}
    rows = [[index[int(v)] for v in row] for row in K if all(int(v) in index for v in row)]
    interior = {aid(tuple(x)) for t, addrs in path[1:-1] + side for x in addrs}
    allowed = sorted(index[v] for v in ids if v not in interior)
    A = sorted(index[aid(x)] for x in keep if len(x) == 3)
    B = sorted(index[aid(tuple(x))] for x in V)
    return dict(K=rows, nvars=len(ids), A=A, B=B, allowed=allowed, ids=ids, X=[aid(tuple(x)) for x in X],
                V=[aid(tuple(x)) for x in V], path_types=[t for t, _ in path], levels=dict(a=a, v=a + L0, m_out=m_out))


def search_mode(built, budget, kmax=10, store_dir=None):
    """The census's certified search (LEVEL-REACH search.SearchEngine) on the pruned pattern."""
    from search import SearchEngine
    wd = Path(tempfile.mkdtemp())
    try:
        eng = SearchEngine(built['K'], built['nvars'], wd)
        import time
        res = eng.search(built['A'], built['B'], allowed=built['allowed'], kmax=kmax, deadline=time.monotonic() + budget)
        eng.close()
    finally:
        shutil.rmtree(wd, ignore_errors=True)
    bond = res.get('bond')
    if bond:
        res['bond_addresses'] = [built['ids'][i] for i in bond]
    return res
