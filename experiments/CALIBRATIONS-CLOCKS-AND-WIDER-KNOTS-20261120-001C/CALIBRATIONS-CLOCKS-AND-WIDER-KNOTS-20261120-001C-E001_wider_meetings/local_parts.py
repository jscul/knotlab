"""Pair-only decomposition and exact locally identifiable not-all-equal parts."""
from collections import Counter, defaultdict
from functools import cache
import gzip
from itertools import combinations
import json
from pathlib import Path
import sys

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / 'artifacts' / HERE.parent.name / HERE.name
PREVIOUS = 'FREEDOM-CLOCKS-AND-BIRTHS-20261120-001C'
sys.path.insert(0, str(ROOT / 'experiments' / PREVIOUS / (PREVIOUS+'-E001_pair_births')))
from census_rates import canonical_pair_table
from census_reached import count_pairs, mask_of, width
from controls import deletions, lawful
from model import nae_separator


def archive():
    smaller = 'READS-HOLDERS-SOURCES-20261120-001B'
    larger = 'THREE-READERS-AND-GROWTH-20261120-001B'
    first = ROOT/'artifacts'/smaller/(smaller+'-E001_irredundant')/'census_cases.json.gz'
    second = ROOT/'artifacts'/larger/(larger+'-E001_state_recovery')/'census_cases.json.gz'
    with gzip.open(first,'rt') as f:
        all_widths = json.load(f)
    with gzip.open(second,'rt') as f:
        all_widths['10'] = json.load(f)
    return all_widths


def local_rows(rows, names):
    place = {name:i for i,name in enumerate(names)}
    return tuple(sorted(tuple(sorted(place[x] for x in row)) for row in rows))


def physical_parts(rows):
    g = nx.Graph()
    for h in rows:
        g.add_nodes_from(h)
        g.add_edges_from(combinations(h,2))
    parts = sorted((tuple(sorted(c)) for c in nx.biconnected_components(g)))
    owner = {}
    for part, names in enumerate(parts):
        for u,v in combinations(names,2):
            if g.has_edge(u,v):
                owner[u,v] = part
    scopes = [[] for _ in parts]
    for h in rows:
        if len(h)<2:
            raise ValueError('A single-place rule is outside the structural theorem.')
        which = owner[tuple(sorted(h[:2]))]
        assert set(h)<=set(parts[which])
        scopes[which].append(h)
    return [(names,local_rows(holdings,names)) for names,holdings in zip(parts,scopes,strict=True)]


def measured_pairs(n, total, counts):
    """Signed numerators share one denominator. A strict test works with integers."""
    signed = [[0]*n for _ in range(n)]
    for (i,j),d in counts.items():
        signed[i][j] = signed[j][i] = total-2*d
    graph = nx.Graph()
    graph.add_nodes_from(range(n))
    triples = []
    for a,b,c in combinations(range(n),3):
        if signed[a][b]+signed[a][c]+signed[b][c] == -total:
            triples.append((a,b,c))
            graph.add_edges_from(((a,b),(a,c),(b,c)))
    for a,b in combinations(range(n),2):
        magnitude = abs(signed[a][b])*total
        if all(magnitude > abs(signed[a][z]*signed[z][b]) for z in range(n) if z!=a and z!=b):
            graph.add_edge(a,b)
    return graph, triples, signed


def frozen(v):
    return tuple(map(frozen,v)) if isinstance(v,list) else v


@cache
def profile(rows):
    total, counts = count_pairs(rows,'nae')
    value = canonical_pair_table(width(rows),total,counts)
    return value, total, counts


def make_catalogue():
    entries = {}
    diagnostics = {}
    all_widths = archive()
    for n in range(3,11):
        states = all_widths[str(n)]['nae']
        grouped = defaultdict(list)
        for state in states:
            # Each archive row is one complete word-set orbit; the sole
            # exceptional (closed) six-name ambiguity is internal to its orbit.
            rows = tuple(map(tuple,state['presentations'][0]['supports']))
            value,total,counts = profile(rows)
            grouped[value.key].append((rows,value,state['state_automorphisms'],total,counts))
        tally = Counter(all_state_types=len(states), rate_types=len(grouped))
        for key, items in grouped.items():
            if len(items)>1:
                tally['distinct_state_type_ambiguities']+=1
                continue
            rows,value,state_aut,total,counts=items[0]
            if value.automorphisms!=state_aut:
                tally['extra_naming_symmetries']+=1
                continue
            tally['unique_named_observations']+=1
            if len(physical_parts(rows))!=1:
                continue
            graph,_,_ = measured_pairs(n,total,counts)
            if not nx.is_biconnected(graph):
                tally['unique_indivisible_not_measured_as_one_part']+=1
                continue
            to_canonical={old:i for i,old in enumerate(value.order)}
            canonical = tuple(sorted(tuple(sorted(to_canonical[x] for x in r)) for r in rows))
            entries[key] = canonical
            tally['accepted_physical_parts']+=1
            if not (len(rows)<=2 or all(len(h)==3 for h in rows)):
                tally['new_over_analytic_parts']+=1
        diagnostics[n]=dict(tally)
    return entries,diagnostics


def save_catalogue():
    entries,diagnostics=make_catalogue()
    data={'bounds':diagnostics,'entries':[(k,v) for k,v in sorted(entries.items())]}
    (OUT/'local_catalogue.json.gz').write_bytes(gzip.compress(json.dumps(data,separators=(',',':')).encode(),mtime=0))
    print(json.dumps(diagnostics), flush=True)


def load_catalogue():
    with gzip.open(OUT/'local_catalogue.json.gz','rt') as f:
        v=json.load(f)
    return {frozen(key):frozen(rows) for key,rows in v['entries']}


def legal_nae(rows):
    return min(map(len,rows))>=3 and lawful(rows,'nae') and all(deletions(rows,'nae')[0])


def normalization(names, signed, total):
    counts={(i,j):(total-signed[a][b])//2 for i,a in enumerate(names) for j,b in enumerate(names) if i<j}
    return canonical_pair_table(len(names),total,counts)


def decode(n,total,counts,library,additional_reader=None):
    graph,triples,signed=measured_pairs(n,total,counts)
    result=[]
    for part in nx.biconnected_components(graph):
        names=tuple(sorted(part))
        assert len(names)>=3
        if len(names)<=10:
            local=normalization(names,signed,total)
            if local.key in library:
                order=[names[i] for i in local.order]
                result.extend(tuple(sorted(order[i] for i in h)) for h in library[local.key])
                continue
        mixed=[row for row in triples if set(row)<=part]
        if mixed and set().union(*map(set,mixed))==part:
            result.extend(mixed)
            continue
        positive=nx.Graph()
        positive.add_edges_from((a,b) for a,b in combinations(names,2) if signed[a][b]>0)
        if not positive:
            result.append(names)
            continue
        if nx.is_connected(positive) and nx.is_bipartite(positive):
            a,b=map(set,nx.bipartite.sets(positive))
            if all(positive.has_edge(x,y) for x in a for y in b):
                common=set(names)-a-b
                assert len(common)>=2
                result.extend((tuple(sorted(a|common)),tuple(sorted(b|common))))
                continue
        assert additional_reader is not None
        result.extend(additional_reader(names,signed,total))
    return tuple(sorted(set(result)))


def member(rows,library,check_legality=False):
    if any(len(r)<3 for r in rows):
        return {'old':False,'analytic':False,'library':False,'reason':'rule below three places'}
    parts=physical_parts(rows)
    old=analytic=with_library=True
    for _,local in parts:
        # A stage under parity receives a structural classification for the
        # NAE law only if every component is legal under that law as well.
        all_three=all(len(h)==3 for h in local)
        previous=len(local)==1 or all_three
        elementary=previous or len(local)==2
        old &= previous
        analytic &= elementary
        if not elementary:
            if width(local)>10:
                with_library=False
            else:
                with_library &= profile(local)[0].key in library
    if with_library and check_legality and not all(legal_part(local) for _,local in parts):
        return {'old':False,'analytic':False,'library':False,'reason':'NAE gate fails'}
    return {'old':old,'analytic':analytic,'library':with_library,'reason':'structural test'}


@cache
def legal_part(rows):
    # The all-ternary and small cases use literal local projection gates.
    # A single large rule is tautologically full and essential on this part.
    if len(rows)==1:
        return len(rows[0])>=3
    if len(rows)==2:
        a,b=map(set,rows)
        return bool(a-b and b-a)
    return legal_nae(rows)


if __name__=='__main__':
    save_catalogue()
