"""Which cycles of knots feed themselves (LOOP-CATALOGUE-20261119-001B).

The candidate map and its blocks are CLUSTER-ALL's (clusters.analyse): for every knot, the live knots sharing a distinction with it
form a simplex; simplices sharing two knots merge into one block; a first-round group of three or more (a hyperedge) is its own
block.  The block graph has a point for each live knot and each block, a line for each knot of a block.  A loop is a cycle of the
block graph.
- **The eddy rule.**  A start feeds itself (grows exponentially) exactly when some piece of the block graph has a cycle and is
  not bare.  Bare: the piece is one cycle whose ordinary blocks are pairs, none of its knots has a spare (an offshoot beyond its
  first-round demand), and a knot off the cycle occurs only as the third knot of a hyperedge (taken all or nothing).  A piece with a
  cycle in which two hyperedges meet at a knot is outside the rule (CLUSTER-ALL's second break).
- **growth_class** reads the class from a real growth, with no rule: closed, stall, quasi-polynomial of dimension d (the d-th
  differences at some lag of at most 12 vanish on the last 16 rounds), or exponential (not quasi-polynomial and still rising, or
  past the junction cap while rising by at least 10% a round)."""
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'experiments/CLUSTER-ALL-20261119-001B/CLUSTER-ALL-20261119-001B-E001_census'))
import clusters as Cl  # noqa: E402
J = Cl.J


def pieces(A, skip_hyper=False):
    """Pieces of the block graph: [(knots, block indices, cycle rank, bare, hyperedges meeting at a knot)]."""
    live, blocks, bedges, pend = A['live'], A['blocks'], A['bedges'], A['pend']
    use = [i for i, B in enumerate(blocks) if not (skip_hyper and bedges[i] is None)]
    parent = {('k', k): ('k', k) for k in live}
    parent.update({('b', i): ('b', i) for i in use})

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for i in use:
        for z in blocks[i]:
            a, b = find(('k', z)), find(('b', i))
            if a != b:
                parent[a] = b
    comp = defaultdict(lambda: ([], []))
    for k in live:
        comp[find(('k', k))][0].append(k)
    for i in use:
        comp[find(('b', i))][1].append(i)
    out = []
    for ks, bs in comp.values():
        lines = sum(len(blocks[i]) for i in bs)
        rank = lines - len(ks) - len(bs) + 1
        deg = defaultdict(int)
        hdeg = defaultdict(int)
        for i in bs:
            for z in blocks[i]:
                deg[z] += 1
                if bedges[i] is None:
                    hdeg[z] += 1
        # bare: one cycle; every ordinary block a pair; no pendants; a knot off the cycle only as the third knot of a hyperedge,
        # which is taken all or nothing and so adds no choice
        bare = (rank == 1 and not any(pend[k] for k in ks)
                and all(len(blocks[i]) == 2 for i in bs if bedges[i] is not None)
                and all(deg[k] == 2 or (deg[k] == 1 and hdeg[k] == 1) for k in ks))
        meet = any(v >= 2 for v in hdeg.values())
        out.append((sorted(ks), sorted(bs), rank, bare, meet))
    return out


def eddy(sizes, edges):
    """'stall'; 'out' (outside the cluster rule's scope); True (feeds itself: a reliable piece with a cycle that is not bare);
    'unreliable' (no such piece, but a piece with a cycle holds one of the cluster rule's known breaks, so growth must decide);
    or False."""
    A = Cl.analyse(sizes, edges)
    if not A['scope']:
        return 'out'
    if A['stall']:
        return 'stall'
    bad = broken_blocks(A)
    unsure = False
    for ks, bs, r, bare, meet in pieces(A):
        if r < 1:
            continue
        if meet or any(i in bad for i in bs):
            unsure = True
        elif not bare:
            return True
    return 'unreliable' if unsure else False


def broken_blocks(A):
    """Merged blocks with a missing pair: the cluster rule's first break (CLUSTER-ALL)."""
    return {i for i, B in enumerate(A['blocks'])
            if A['bedges'][i] is not None and len(A['bedges'][i]) < len(B) * (len(B) - 1) // 2}


def exact(A):
    """True when no known break of the cluster rule occurs anywhere, so its series is expected to equal the growth."""
    return not broken_blocks(A) and not any(meet and r >= 1 for _, _, r, _, meet in pieces(A))


def loops(sizes, edges):
    """The pieces with a cycle, described: knots, blocks, cycle rank, bare; and the hyperedge-only cycles."""
    A = Cl.analyse(sizes, edges)
    if not A['scope'] or A['stall']:
        return None
    with_h = pieces(A, skip_hyper=False)
    without = pieces(A, skip_hyper=True)
    return {'rank_with_hyperedges': sum(p[2] for p in with_h), 'rank_without': sum(p[2] for p in without),
            'pieces': [{'knots': ks, 'blocks': [list(A['blocks'][i]) for i in bs], 'rank': r, 'bare': bare, 'hyperedges_meet': m}
                       for ks, bs, r, bare, m in with_h if r >= 1], 'hyperedges': A['hyper']}


def growth_class(sizes, edges, rounds=40, maxj=300000, tmax=180.0):
    g = J.grow(sizes, edges, rounds=rounds, maxj=maxj, tmax=tmax)
    c, out = g['counts'], g['outcome']
    if out in ('stall', 'closed'):
        return out, c
    W = 16
    if len(c) >= W + 8:
        for k in range(1, 7):
            for p in range(1, 13):
                d = list(c)
                for _ in range(k):
                    d = [d[i + p] - d[i] for i in range(len(d) - p)]
                if len(d) >= W and all(x == 0 for x in d[-W:]):
                    return f'dim{k}', c
    if out in ('cap', 'time'):
        return ('exp' if len(c) >= 3 and c[-1] >= 1.1 * c[-2] else 'unsettled'), c
    if len(c) >= 12 and c[-1] > c[-6] > c[-11]:
        return 'exp?', c
    return 'unsettled', c


def _analyse_all():
    """clusters.analyse without its scope cut: the same blocks for every start, with 'scope' still reporting the cut."""
    import inspect
    src = inspect.getsource(Cl.analyse)
    cut = "            return {'scope': False, 'why': 'a round-1 group of three sharing two knots with another block'}\n"
    assert src.count(cut) == 1
    src = src.replace("def analyse(", "def analyse_all(").replace(cut, "            out_of_scope = True\n")
    src = src.replace("    nh = len(blocks)\n", "    nh = len(blocks)\n") 
    src = src.replace("    ls = set(live)\n", "    ls = set(live)\n    out_of_scope = False\n", 1)
    src = src.replace("    return {'scope': True, 'stall': False,", "    return {'scope': not out_of_scope, 'stall': False,")
    ns = dict(Cl.__dict__)
    exec(compile(src, Cl.__file__, 'exec'), ns)
    return ns['analyse_all']


analyse_all = _analyse_all()


def loop_rank_any(sizes, edges):
    """The block graph's cycle rank outside the cluster rule's scope too, after merging every two blocks (hyperedges included)
    that share two knots, so that only cycles through distinct blocks count (None on a stall)."""
    A = analyse_all(sizes, edges)
    if A.get('stall'):
        return None
    bl = [set(B) for B in A['blocks']]
    merged = True
    while merged:
        merged = False
        for i in range(len(bl)):
            for j in range(i + 1, len(bl)):
                if len(bl[i] & bl[j]) >= 2:
                    bl[i] |= bl.pop(j)
                    merged = True
                    break
            if merged:
                break
    pts = {z for B in bl for z in B}
    return sum(len(B) for B in bl) - len(pts) - len(bl) + _components(bl)


def _components(bl):
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for i, B in enumerate(bl):
        for z in B:
            a, b = find(('b', i)), find(('k', z))
            if a != b:
                parent[a] = b
    return len({find(x) for x in list(parent)})
