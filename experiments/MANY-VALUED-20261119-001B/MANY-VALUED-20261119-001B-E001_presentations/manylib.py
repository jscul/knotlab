"""All presentations of the same allowed states (MANY-VALUED-20261119-001B).

At a stage where the states-only growth is undefined (STATES-GROWTH-20261119-001), the presentations of its allowed states are the
sets Q of junction supports, drawn from M(S) (the minimal not-all-equal constraints) and the stage's own junctions, such that
Q is admissible (every member of at least three places, every distinction in at most two members, every distinction held),
irredundant (no member's removal leaves the states unchanged) and allows exactly the stage's states.  Each is grown by the cheapest
growth under not-all-equal for a few rounds."""
import itertools
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'experiments/STATES-GROWTH-20261119-001B/STATES-GROWTH-20261119-001B-E001_states'))
import statelib as SL  # noqa: E402
sys.path.insert(0, str(ROOT / 'experiments/NAE-GROWTH-20261119-001B/NAE-GROWTH-20261119-001B-E001_nae'))
import bondlib as B  # noqa: E402
import naelib as N  # noqa: E402


def presentations(stars, n=None, cap=20, pool='stage'):
    """pool 'M': candidates are M(S) only (states-only); pool 'stage': M(S) and the stage's own junctions (reads the stage)."""
    n = n or 1 + max(b for s in stars for b in s)
    st = B.states(n, stars, 'nae')
    target = sorted(st.tolist())
    M = SL.nae_core(n, st, kmax=max(len(x) for x in stars) + 1)
    cand = sorted(set(M) | ({tuple(sorted(x)) for x in stars} if pool == 'stage' else set()))
    if len(cand) > cap:
        return None, len(cand)
    found = []
    for r in range(1, len(cand) + 1):
        for Q in itertools.combinations(cand, r):
            held = {}
            for S in Q:
                for b in S:
                    held[b] = held.get(b, 0) + 1
            if len(held) < n or max(held.values()) > 2 or min(len(S) for S in Q) < 3:
                continue
            sq = B.states(n, [list(x) for x in Q], 'nae')
            if len(sq) != len(st) or sorted(sq.tolist()) != target:
                continue
            if any(len(B.states(n, [list(x) for x in Q if x != y], 'nae')) == len(st) for y in Q):
                continue
            found.append([list(x) for x in Q])
    return found, len(cand)


def grow(stars, rounds=3):
    P = N.S.from_junctions([list(x) for x in stars])
    P.linalg = False
    counts = []
    for _ in range(rounds):
        r = P.step(N.nae_rule(N.F.fewest), None)
        if r is None:
            counts.append('stall')
            break
        counts.append(r['new'])
        if r['new'] == 0:
            break
    return counts


def iso_classes(pres):
    """Presentations up to renaming of distinctions (the same structure): any renaming carrying one onto the other also carries
    the allowed states onto themselves, since both present them."""
    import networkx as nx
    nm = nx.algorithms.isomorphism.categorical_node_match('kind', None)
    graphs, classes = [], []
    for p in pres:
        G = nx.Graph()
        for j, S in enumerate(p):
            G.add_node(('j', j), kind='j')
            for b in S:
                G.add_node(('b', b), kind='b')
                G.add_edge(('j', j), ('b', b))
        for i, H in enumerate(graphs):
            if nx.is_isomorphic(G, H, node_match=nm):
                classes[i].append(p)
                break
        else:
            graphs.append(G)
            classes.append([p])
    return classes
