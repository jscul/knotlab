"""Compare the necessary source laws of every qualifying alternating pattern in the 600 starts."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
from time import perf_counter

import networkx as nx

from witness_checks import CENSUS, columns, upper_values
from read_recount import calculate, stage_source

HERE=Path(__file__).resolve().parent
POSITIONS=((0,2,4),(0,3,5),(1,2,5),(1,3,4))


def as_pattern_graph(laws, pairs):
    g=nx.Graph()
    def node(kind, index):
        name=(kind,index)
        g.add_node(name,kind=kind)
        return name
    for i,law in enumerate(laws):
        loc=node('law',i)
        for d in law:
            g.add_edge(loc,node('distinction',d))
    chosen=[]
    for i,pair in enumerate(pairs):
        for j,(carrier,value) in enumerate(pair):
            loc=node('agreement '+str(value),2*i+j)
            chosen.append(loc)
            g.add_edge(loc,node('pair',i))
            for d in carrier:
                g.add_edge(loc,node('distinction',d))
    for i,t in enumerate(POSITIONS):
        for j in t:
            g.add_edge(node('clause',i),chosen[j])
    return g


def test_reduced(laws, pairs):
    names=sorted(set().union(*(set(law) for law in laws),
                             *(set(c) for p in pairs for c,_ in p)))
    table=dict(zip(names,columns(len(names))))
    universe=(1<<(1<<len(names)))-1
    def agreement(c):
        x=y=universe
        for d in c:
            x&=table[d]
            y&=~table[d]
        return x|y
    allowed=universe
    for law in laws:
        allowed &= ~agreement(law)
    cols=[agreement(c) if v else universe ^ agreement(c) for pair in pairs for c,v in pair]
    def split(values):
        cells=[allowed]
        for v in values:
            cells=[x for cell in cells for x in (cell&~v,cell&v)]
        return cells
    bond_cells=[split([cols[i] for i in t]) for t in POSITIONS]
    assert all([bool(x) for x in cells]==[True]*7+[False] for cells in bond_cells)
    upper=[]
    for role in range(3):
        u=upper_values(cols,role)
        assert [bool(x) for x in split(u)]==[True]*7+[False]
        assert all(any(cell&bit and cell&~bit for cell in cells) for cells in bond_cells for bit in u)
        upper.append((u[0]&u[1]&u[2]&allowed).bit_count())
    return {'distinctions_used_in_laws_or_readings':len(names),'source_states':allowed.bit_count(),
            'states_giving_111_by_role':upper}


def ordered_chain(laws):
    neighbours=[[j for j,other in enumerate(laws) if i!=j and set(law)&set(other)] for i,law in enumerate(laws)]
    assert sorted(map(len,neighbours))==[1,1,2,2,2,2,2,2]
    seq=[next(i for i in range(8) if len(neighbours[i])==1)]
    while len(seq)<8:
        options=[k for k in neighbours[seq[-1]] if k not in seq]
        assert len(options)==1
        seq.append(options[0])
    assert all(len(set(laws[a]) & set(laws[b]))==1 for a,b in zip(seq,seq[1:]))
    return seq



def eight_knot_choices(supports):
    triples={i:set(s) for i,s in enumerate(supports) if len(s)==3}
    def extend(path):
        if len(path)==8:
            if path[0]<path[-1]:
                yield tuple(sorted(path))
            return
        for i,s in triples.items():
            if i in path or len(triples[path[-1]] & s)!=1:
                continue
            if any(triples[j] & s for j in path[:-1]):
                continue
            yield from extend([*path,i])
    return {chain for i in triples for chain in extend([i])}


def chain_opportunities(pilot):
    census=json.loads(CENSUS.read_text())
    source_rows=[json.loads(line) for f in sorted((HERE.parent/'out').glob('four_*.jsonl'))
                 for line in f.read_text().splitlines()]
    histogram=Counter()
    eligible=[]
    for row in source_rows[:50] if pilot else source_rows:
        idx=int(row['start'].split()[1])
        for t,src in stage_source(census,idx):
            choices=eight_knot_choices(src)
            histogram[t,len(choices)]+=1
            if choices:
                eligible.append({'start':idx,'round':t,'eight_law_sets':sorted(choices)})
    previous=HERE.parents[1]/'UPPER-GROWN-20261127-001/referee-R1/upper_four_closed.json'
    closed=next(r['witness']['knots'] for r in json.loads(previous.read_text()) if 'witness' in r)
    controls={'earlier_four_knot_census_entry_420_round_two':sorted(eight_knot_choices(dict(stage_source(census,420))[2])),
              'earlier_closed_ten_knot_positive_on_15_distinctions':sorted(eight_knot_choices(closed))}
    return {'earlier_positive_controls':controls,'by_round_and_number_of_chains':[[t,num,count] for (t,num),count in sorted(histogram.items())],
            'stages_with_at_least_one_chain':eligible}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--pilot',action='store_true')
    args=p.parse_args()
    begin=perf_counter()
    # The same exact structural method supplied these rows at both sizes.
    read=[json.loads(line) for line in (HERE/'omitted_exact_pilot.jsonl').read_text().splitlines()]
    omitted=[json.loads(line) for line in (HERE/'omitted_stages.jsonl').read_text().splitlines()]
    results=[]
    reference=None
    for row in [next(r for r in read if r['start']==5260)]+[r for r in omitted if r['patterns']]:
        families=defaultdict(list)
        entries=[]
        for pattern in row['patterns'][:1] if args.pilot else row['patterns']:
            keys={tuple(sorted(r['initial_law_deletions']+r['birth_law_deletions'])) for r in pattern['qualifying_roles']}
            assert len(keys)==1 and len(pattern['qualifying_roles'])==3
            needed,=keys
            laws=[row['source_supports'][i] for i in needed]
            assert len(laws)==8 and all(len(k)==3 for k in laws)
            order=ordered_chain(laws)
            in_laws=set().union(*map(set,laws))
            assert len(in_laws)==17
            pairs=pattern['signed_pairs']
            short=[[(tuple(d for d in c if d in in_laws),v) for c,v in p] for p in pairs]
            extra=sorted(d for p in pairs for c,v in p for d in c if d not in in_laws)
            assert len(extra)<=1
            graph=as_pattern_graph(laws,short)
            if reference is None:
                reference=graph
            assert nx.is_isomorphic(reference,graph,node_match=lambda a,b:a['kind']==b['kind'])
            key=(needed,tuple(sorted(tuple(sorted((tuple(sorted(c)),v) for c,v in pair)) for pair in short)))
            families[key].append(extra)
            entries.append({'essential_source_laws':list(needed),'chain_order':[needed[j] for j in order],
                            'outside_distinction':extra,'eight_laws_on_reported_carriers':test_reduced(laws,pairs),
                            'eight_laws_on_shortened_carriers':test_reduced(laws,short)})
        for (needed,_),extras in families.items():
            if not args.pilot:
                remainder=set().union(*map(set,row['source_supports']))-set().union(*(set(row['source_supports'][j]) for j in needed))
                assert sorted(extras)==sorted([[]]+[[d] for d in remainder])
        results.append({'census_entry':row['start'],'round':row['round'],'patterns':len(entries),
                        'different_eight_law_choices':len({k[0] for k in families}),
                        'patterns_after_shortening_per_law_choice':len(families),'extensions_per_shortened_pattern':[len(v) for v in families.values()],
                        'patterns_by_number_of_outside_distinctions':dict(Counter(len(e['outside_distinction']) for e in entries)),
                        'same_reduced_pattern_up_to_renaming':True,'per_pattern':entries})
    def chain(k):
        # Consecutive knots share distinction 2*i+2. Every other place is loose.
        return [tuple(range(2*i,2*i+3)) for i in range(k)]
    controls=[]
    for size in ((7,) if args.pilot else (7,8)):
        control=calculate(chain(size),size,0)
        controls.append({'knots':size,'distinctions':2*size+1,'allowed':control['allowed'],
                         'single_word_bonds':control['single_word_bonds'],'patterns':control['patterns'],
                         'roles':control['relations read'],'qualifying_roles':control['proper and pairs free and not read at one lower bond']})
    fn='common_source_pilot.json' if args.pilot else 'common_source.json'
    (HERE/fn).write_text(json.dumps({'witness_sources':results,'bare_chain_controls':controls,'opportunities':chain_opportunities(args.pilot)},indent=2)+'\n')
    print(fn,[(r['census_entry'],r['patterns'],r['extensions_per_shortened_pattern']) for r in results],round(perf_counter()-begin,3))


if __name__=='__main__':
    main()
