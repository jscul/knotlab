"""Generate closed meeting patterns and run the exact signed-box search serially."""

import argparse
import collections
import itertools
import json
from pathlib import Path
import subprocess
import time

import networkx as nx


HERE = Path(__file__).resolve().parent
ORIGINAL = HERE.parent
PREVIOUS = ORIGINAL.parent / 'RING-BOND-20261127-001' / 'referee-R1'


def canonical_classes(patterns):
    buckets = collections.defaultdict(list)
    for n, links in patterns:
        graph = nx.Graph()
        graph.add_nodes_from(range(n))
        for u, v in links:
            if graph.has_edge(u, v):
                graph[u][v]['multiplicity'] += 1
            else:
                graph.add_edge(u, v, multiplicity=1)
        key = tuple(sorted((graph.has_edge(v,v), tuple(sorted(
            k['multiplicity'] for k in graph[v].values()))) for v in graph))
        match = nx.isomorphism.categorical_edge_match('multiplicity',1)
        if any(nx.is_isomorphic(old, graph, edge_match=match) for old in buckets[key]):
            continue
        buckets[key].append(graph)
        yield n, tuple(sorted(tuple(sorted(link)) for link in links))


def multigraphs():
    # A repeated pair has two external ends, which may belong to one knot.
    # Removing the pair and reconnecting those ends creates an ordinary
    # distinction or a self-meeting in the temporary reduced pattern.
    # A self-meeting holder is removed with its only neighbour in the same way.
    patterns = [(2,((0,1),)*3),(2,((0,0),(0,1),(1,1)))]
    for n in (4,6,8,10):
        def candidates():
            if n <= 8:
                for line in (ORIGINAL / 'out' / f'cubic_{n}.jsonl').read_text().splitlines():
                    yield n, json.loads(line)['links']
            for _, links in patterns:
                for index, (x,y) in enumerate(links):
                    keep = links[:index] + links[index+1:]
                    u, v = n-2, n-1
                    yield n, keep+((x,u),(u,v),(u,v),(v,y))
                    yield n, keep+((x,u),(u,y),(u,v),(v,v))
        patterns = list(canonical_classes(candidates()))
        for m, links in patterns:
            if len(set(links)) < len(links) and all(a!=b for a,b in links):
                yield m, links


def quartic_atlas(n):
    # Each set of distinct holder pairs occurs once in the atlas. Try each
    # positive multiplicity that still allows degree four at every holder.
    for graph in nx.graph_atlas_g():
        if len(graph) != n or not nx.is_connected(graph) or max(dict(graph.degree()).values()) > 4:
            continue
        links = sorted(graph.edges())
        residual = [4-graph.degree(p) for p in graph]
        def complete(pos, chosen):
            if pos == len(links):
                if not any(residual):
                    yield n, tuple(chosen)
                return
            a,b = links[pos]
            for extra in range(min(residual[a],residual[b])+1):
                residual[a] -= extra
                residual[b] -= extra
                if all(r == 0 or any(p in e for e in links[pos+1:])
                       for p, r in enumerate(residual)):
                    yield from complete(pos+1, chosen + [(a,b)]*(extra+1))
                residual[a] += extra
                residual[b] += extra
        yield from canonical_classes(complete(0, []))


def quartic_eight():
    from arity_contract import canonical
    n=8
    # The exceptional pattern has a triple meeting at every holder.
    special=[(v,v+1) for v in range(0,n,2) for _ in range(3)]
    special.extend((v,(v+1)%n) for v in range(1,n,2))
    seen={canonical(n,special)}
    yield n,special
    for _,links in quartic_atlas(n-1):
        for i,j in itertools.combinations(range(len(links)),2):
            new=[p for k,p in enumerate(links) if k not in (i,j)]
            new.extend((v,n-1) for v in links[i]+links[j])
            key=canonical(n,new)
            if key in seen: continue
            seen.add(key)
            yield n,new


def supports(n, links):
    return [[i for i,pair in enumerate(links) if v in pair] for v in range(n)]


def built_cases():
    # Pair carriers give a readable construction at four places. The twelve
    # cross-group pairs are the source laws; each carrier meets four knots.
    groups = ((0,1),(2,3),(4,5))
    rows = [[2*a,2*a+1,2*b,2*b+1] for g,h in itertools.combinations(groups,2)
            for a,b in itertools.product(g,h)]
    yield 'four-place twelve, each raw distinction has four holders', rows, None
    # A simple four-place system plus selected patterns with repeated meetings.
    for n in (7,8,9,10):
        for steps in ((1,1),(1,2),(1,3)):
            links = sorted(tuple(sorted((v,(v+k)%n))) for v in range(n) for k in steps)
            yield f'four-place cyclic choices {steps}, {n} knots', supports(n,links), links


def engine(binary, rows):
    masks = [sum(1<<i for i in row) for row in rows]
    n = max(max(row) for row in rows)+1
    request = ' '.join(map(str,[n,len(rows),*masks]))
    raw = subprocess.check_output([binary], input=request, text=True)
    fields = list(map(int,raw.split()))
    states, reads, triples, clauses, boxes = fields[:5]
    witness = [[i for i in range(n) if mask>>i&1] for mask in fields[5::2]]
    return dict(states=states, unread_carriers=reads, eligible_triples=triples,
                single_clause_triples=clauses, boxes=boxes,
                witness=list(zip(witness,fields[6::2])))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--group',choices=['pilot','cubic','four','built'],required=True)
    parser.add_argument('--size', type=int, default=6)
    parser.add_argument('--limit', type=int)
    parser.add_argument('--binary', type=Path, required=True)
    args=parser.parse_args()
    if args.group=='pilot':
        witness = json.loads((PREVIOUS/'layer_witness.json').read_text())['source_knots_not_all_equal']
        # The first, cheap case also tests detection without giving a box to the search.
        cases=iter([next(built_cases()), ('archived twelve-knot positive control',witness,None)])
    elif args.group=='built':
        cases = (c for c in built_cases() if len(c[1])==args.size)
    else:
        choices = multigraphs() if args.group=='cubic' else (
            quartic_eight() if args.size==8 else quartic_atlas(args.size))
        cases = ((args.group,supports(n,links),links) for n,links in choices if n==args.size)
    for kind,rows,links in itertools.islice(cases,args.limit):
        start = time.perf_counter()
        result = engine(args.binary.resolve(), rows)
        print(json.dumps(dict(kind=kind,knots=len(rows),links=links,
                              seconds=round(time.perf_counter()-start, 4),**result)),flush=True)


if __name__=='__main__':
    main()
