"""Shared-runner job for GROW-SMALL-20261119-001A-E001.  Every legal meet-once arrangement of 2 to 7 junctions of
PARENT-RULE-20261119-001B part S (503,039, the same enumeration and order) taken as a start and grown by complete rounds under the
census's law (cheapest counts, elimination over GF(2)), rounds 1 and 2; a stall ends a start.  For every stage: its round, junction
and distinction counts, whether junctions still meet at most once, a Weisfeiler-Leman hash of its table read exactly up to
distance 8 and pooled beyond (exact_table_v2, as in MEET-ONCE), whether some pair reads beyond 8, a hash of the arrangement, and its
self-grown depth (peel, regrow one round, compare; repeated while it gives the arrangement back; at most 4).  Stages are regrown
from their start and round for the pairing, so no stars are stored.  Control: every 500th start is also grown from a relabelled
copy (junctions and distinctions permuted), and its stages must be isomorphic.  Cases: the static job's cases."""
import itertools
import random
import sys
from collections import Counter
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PR = ROOT / 'experiments/PARENT-RULE-20261119-001B/PARENT-RULE-20261119-001B-E001_parent'
sys.path.insert(0, str(PR))
import census_job as C  # noqa: E402  (the census's law and exact_table_v2)
import plib as L  # noqa: E402
import static_job as SJ  # noqa: E402
ROUNDS = 2
HPOOL = 8


def setup(params):
    SJ.atlas()


def cases():
    yield from SJ.cases()


def grow(stars, rounds=ROUNDS):
    """The stages of rounds 1..rounds, as lists of frozensets; a stall or nothing to add ends the list."""
    P = C.S.from_junctions([sorted(s) for s in stars])
    out = []
    for r in range(1, rounds + 1):
        res = P.step(C.S.gf2(C.F.fewest), None)
        if res is None or res['new'] == 0:
            break
        out.append([frozenset(b) for b in P.bits_of])
    return out


def same_arrangement(a, b):
    """Isomorphism of arrangements, with cheap invariants first (VF2 alone can be slow on near-misses)."""
    if len(a) != len(b) or sorted(map(len, a)) != sorted(map(len, b)):
        return False
    ga, gb = L.incidence(a), L.incidence(b)
    if nx.weisfeiler_lehman_graph_hash(ga, node_attr='k', iterations=4) != nx.weisfeiler_lehman_graph_hash(gb, node_attr='k', iterations=4):
        return False
    return L.arrangement_iso(a, b)


def self_grown_depth(stars, cap=4):
    d, cur = 0, stars
    while d < cap:
        if not L.live_set(cur):
            break
        base = L.peel(cur)
        if not base:
            break
        again = grow(base, 1)
        if not again or not same_arrangement(again[0], cur):
            break
        d += 1
        cur = base
    return d


def relabelled(stars, seed):
    rng = random.Random(seed)
    labels = sorted(L.owners(stars))
    new = labels[:]
    rng.shuffle(new)
    m = dict(zip(labels, new))
    out = [frozenset(m[b] for b in s) for s in stars]
    rng.shuffle(out)
    return out


def hashes(stars, table):
    labels = sorted(L.owners(stars))
    g = nx.Graph()
    g.add_nodes_from(labels)
    for (a, b), d in table.items():
        g.add_edge(a, b, d=str(d))
    th = nx.weisfeiler_lehman_graph_hash(g, edge_attr='d', iterations=4)
    ah = nx.weisfeiler_lehman_graph_hash(L.incidence(stars), node_attr='k', iterations=4)
    return th, ah


def run(case_id, p):
    G = dict(SJ.atlas())
    out, c = [], Counter()
    for gi in p['graphs']:
        g = nx.convert_node_labels_to_integers(G[gi])
        n = g.number_of_nodes()
        auts = [tuple(m[i] for i in range(n)) for m in nx.algorithms.isomorphism.GraphMatcher(g, g).isomorphisms_iter()]
        for ell in itertools.product(range(SJ.lmax(n) + 1), repeat=n):
            if any(tuple(ell[s[i]] for i in range(n)) < ell for s in auts):
                continue
            if not SJ.legal(g, ell):
                continue
            c['starts'] += 1
            start = SJ.arrangement(g, ell)
            stages = grow(start)
            c[f'reached_round_{len(stages)}_n{n}'] += 1
            if c['starts'] % 500 == 0:
                other = grow(relabelled(start, c['starts']))
                c['label_control'] += 1
                if len(other) != len(stages) or any(not same_arrangement(a, b) for a, b in zip(stages, other)):
                    c['label_control_mismatch'] += 1
            for r, stars in enumerate(stages, 1):
                ms = L.max_shared(stars)
                tab = C.X.exact_table(stars, HPOOL)
                th, ah = hashes(stars, tab)
                beyond = any(v == HPOOL + 1 for v in tab.values())
                out.append([n, gi, ''.join(map(str, ell)), r, len(stars), len(L.owners(stars)), ms, th, ah,
                            'closed' if not L.live_set(stars) else 'open', self_grown_depth(stars), beyond])
    return {'rows': out, 'counts': dict(c),
            'fields': ['n', 'atlas', 'loose', 'round', 'junctions', 'distinctions', 'max_shared', 'table_hash', 'arrangement_hash', 'kind',
                       'depth', 'beyond_8']}
