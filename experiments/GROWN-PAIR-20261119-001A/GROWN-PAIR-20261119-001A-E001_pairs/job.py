"""Shared-runner job for GROWN-PAIR-20261119-001A-E001: the exact full bond-distance table of every census stage of at most
MAXJ junctions (rounds 0-8 under the cheapest counts, as CENSUS-READ's passes), with a canonical hash of the table up to renaming
and a canonical hash of the arrangement.  Shards of 100 arrangements in the census's sorted order.

The table hash: Weisfeiler-Leman on the complete graph of distinctions, edges labelled by distance (equal tables up to renaming give
equal hashes; unequal hashes mean non-isomorphic tables).  The arrangement hash: Weisfeiler-Leman on the incidence graph
(junctions, distinctions, loose distinctions marked).  Exact tables and stars are kept so that pairs can be checked exactly."""
import json
import sys
import zlib
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CENSUS = ROOT / 'experiments/CENSUS-READ-20261118-001A/CENSUS-READ-20261118-001A-E001_census'
sys.setrecursionlimit(100000)
sys.path.insert(0, str(CENSUS))
import importlib.util  # noqa: E402
_spec = importlib.util.spec_from_file_location('census_job', CENSUS / 'job.py')
CJ = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = CJ
_spec.loader.exec_module(CJ)
import exact_table_v2 as X  # noqa: E402
R, S, F, A = CJ.R, CJ.S, CJ.F, CJ.A
SHARD = 100
MAXJ = 14
_ARR = None


def setup(params):
    global _ARR, MAXJ
    MAXJ = int(params.get('maxj', MAXJ))
    _ARR = CJ.load()


def cases():
    data = _ARR if _ARR is not None else CJ.load()
    for s in range(0, len(data), SHARD):
        yield f'census-{s // SHARD:04d}', {'lo': s, 'hi': min(len(data), s + SHARD)}


def table_hash(table, labels):
    g = nx.Graph()
    g.add_nodes_from(labels)
    for (a, b), d in table.items():
        g.add_edge(a, b, d=str(d))
    return nx.weisfeiler_lehman_graph_hash(g, edge_attr='d', iterations=4)


def arrangement_hash(stars):
    own = R.owners(stars)
    g = nx.Graph()
    for j, s in enumerate(stars):
        g.add_node(('j', j), k='j')
        for b in s:
            g.add_node(('b', b), k='loose' if len(own[b]) == 1 else 'shared')
            g.add_edge(('j', j), ('b', b))
    return nx.weisfeiler_lehman_graph_hash(g, node_attr='k', iterations=4)


def stage_record(stars):
    stars = [frozenset(s) for s in stars]
    labels = sorted(R.owners(stars))
    N = len(labels)
    table = X.exact_table(stars, N)
    own = R.owners(stars)
    from collections import Counter
    shared = Counter(tuple(sorted(js)) for js in own.values() if len(js) == 2)
    return {'junctions': len(stars), 'distinctions': N, 'max_shared': max(shared.values()) if shared else 0,
            'loose': sum(1 for js in own.values() if len(js) == 1),
            'table_hash': table_hash(table, labels), 'arrangement_hash': arrangement_hash(stars),
            'distance_histogram': sorted(Counter(table.values()).items()),
            'stars': [sorted(s) for s in stars]}


def run(case_id, p):
    data = _ARR if _ARR is not None else CJ.load()
    out = []
    for i in range(p['lo'], p['hi']):
        key = data[i]
        P = S.from_junctions(A.stars_of(key))
        for r in range(CJ.RMAX + 1):
            if len(P.bits_of) > MAXJ:
                break
            rec = stage_record(P.bits_of)
            rec.update({'index': i, 'key': [list(key[0]), list(key[1])], 'round': r})
            out.append(rec)
            if r == CJ.RMAX:
                break
            res = P.step(S.gf2(F.fewest), None)
            if res is None or res['new'] == 0:
                break
    return {'stages': out}
