"""Shared-runner job for MEET-ONCE-20261119-001A-E001: every grown census stage of 15 to 40 junctions in which no two junctions share
two distinctions (rounds 1-8, cheapest counts, complete rounds), with its table exact up to H = 8 (pooled above), a
Weisfeiler-Leman hash of that table (complete graph on distinctions, edges labelled; an isomorphism invariant, and since the pooled
table is a function of the full one, equal full tables give equal pooled hashes; H = 8 for every stage, so that the pooling
does not depend on the arrangement), and an arrangement hash.  Shards of 100
arrangements in the census's sorted order."""
import sys
from collections import Counter
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CENSUS = ROOT / 'experiments/CENSUS-READ-20261118-001A/CENSUS-READ-20261118-001A-E001_census'
sys.setrecursionlimit(100000)
sys.path.insert(0, str(CENSUS))
import importlib.util  # noqa: E402
_spec = importlib.util.spec_from_file_location('census_job_meet', CENSUS / 'job.py')
CJ = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = CJ
_spec.loader.exec_module(CJ)
import exact_table_v2 as X  # noqa: E402
R, S, F, A = CJ.R, CJ.S, CJ.F, CJ.A
SHARD = 100
LO, HI = 15, 40
HPOOL = 8
_ARR = None


def setup(params):
    global _ARR
    _ARR = CJ.load()


def cases():
    data = _ARR if _ARR is not None else CJ.load()
    for s in range(0, len(data), SHARD):
        yield f'census-{s // SHARD:04d}', {'lo': s, 'hi': min(len(data), s + SHARD)}


def hashes(stars, table):
    labels = sorted(R.owners(stars))
    g = nx.Graph()
    g.add_nodes_from(labels)
    for (a, b), d in table.items():
        g.add_edge(a, b, d=str(d))
    th = nx.weisfeiler_lehman_graph_hash(g, edge_attr='d', iterations=4)
    own = R.owners(stars)
    h = nx.Graph()
    for j, s in enumerate(stars):
        h.add_node(('j', j), k='j')
        for b in s:
            h.add_node(('b', b), k='loose' if len(own[b]) == 1 else 'shared')
            h.add_edge(('j', j), ('b', b))
    ah = nx.weisfeiler_lehman_graph_hash(h, node_attr='k', iterations=4)
    return th, ah


def run(case_id, p):
    data = _ARR if _ARR is not None else CJ.load()
    out = []
    for i in range(p['lo'], p['hi']):
        key = data[i]
        P = S.from_junctions(A.stars_of(key))
        for r in range(CJ.RMAX + 1):
            n = len(P.bits_of)
            if n > HI:
                break
            stars = [frozenset(b) for b in P.bits_of]
            own = R.owners(stars)
            shared = Counter(tuple(sorted(js)) for js in own.values() if len(js) == 2)
            if r >= 1 and n >= LO and (max(shared.values()) if shared else 0) < 2:
                K = max(map(len, stars))
                table = X.exact_table(stars, HPOOL)
                th, ah = hashes(stars, table)
                out.append({'index': i, 'key': [list(key[0]), list(key[1])], 'round': r, 'junctions': n,
                            'distinctions': len(own), 'largest': K, 'pooled_table_hash': th, 'arrangement_hash': ah,
                            'stars': [sorted(s) for s in stars]})
            if r == CJ.RMAX:
                break
            res = P.step(S.gf2(F.fewest), None)
            if res is None or res['new'] == 0:
                break
    return {'stages': out}
