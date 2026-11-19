"""Replay the static-to-growing witnesses and check two-hub orbits against literal cuts."""
from itertools import combinations
from pathlib import Path
import json
import subprocess
import tempfile
import networkx as nx
from low_delayed import production_law, verifier
from static_exact import patterns

def direct_orders():
    shapes=patterns(4)
    choices=[(2,2,2),(2,3,3),(3,2,2),(3,3,1),(4,2,3)]
    expected=[]
    for t,s,l in choices:
        edges=[(2+t+j,0 if j<s else 1,l) if a==0 else (2+t+j,1+a,1)
               for j in range(2*s) for a in range(t+1)]
        # Independent simple connected-subset test and literal named query oracle.
        graph=nx.Graph()
        graph.add_edges_from((u,v) for u,v,_ in edges)
        bonds=[]
        for mask in range(1,1<<(len(graph)-1)):
            subset={v for v in graph if mask & (1<<v)}
            if not nx.is_connected(graph.subgraph(subset)) or not nx.is_connected(graph.subgraph(set(graph)-subset)):
                continue
            crossing=sum(1<<i for i,(u,v,_) in enumerate(edges) if (u in subset)!=(v in subset))
            cost=sum(w for i,(_,_,w) in enumerate(edges) if crossing & (1<<i))
            bonds.append((cost,crossing))
        bonds.sort()
        phi=list(range(len(edges)))
        for a in range(t+1):
            z=s*(t+1)+a
            phi[a],phi[z]=phi[z],phi[a]
        first=0
        for k in range(1,5):
            for marks in combinations(range(len(edges)),k):
                m=sum(1<<i for i in marks);im=sum(1<<phi[i] for i in marks)
                if m==im: continue
                left=next((c for c,b in bonds if b&m==m),None)
                right=next((c for c,b in bonds if b&im==im),None)
                if left!=right: first=k;break
            if first: break
        expected.append(first)
    with tempfile.TemporaryDirectory(prefix='split-core-replay-') as tmp:
        exe=Path(tmp)/'test'
        subprocess.run(['c++','-O2','-std=c++20',str(Path(__file__).with_name('static_exact.cpp')),'-o',str(exe)],check=True)
        inputs=[str(len(shapes)),*(' '.join(map(str,[k,u,len(row),*row])) for k,u,row in shapes),
                *(' '.join(map(str,[t,s,l,1])) for t,s,l in choices)]
        data=subprocess.check_output([exe],input='\n'.join(inputs)+'\n',text=True)
    assert [int(x.split()[4]) for x in data.splitlines()]==expected
    return list(zip(choices,expected))

def replay(values):
    J,n,t,s,L,unit=values
    rows=[[] for _ in range(t+2+2*s)]
    labels=[]
    width=0
    for j in range(2*s):
        bysite=[]
        m=2+t+j
        for a in range(t+1):
            v=(0 if j<s else 1) if a==0 else a+1
            weight=L if a==0 else unit
            names=list(range(width,width+weight))
            rows[v].extend(names);rows[m].extend(names)
            bysite.append(names);width+=weight
        labels.append(bysite)
    phi=list(range(width))
    for x,y in zip(labels[0],labels[s]):
        for i,j in zip(x,y):
            phi[i]=j;phi[j]=i
    replaced=labels[1][1][0] # fixed, and disjoint from every hub spoke
    fixed_endpoint=2+t+1
    rows[fixed_endpoint].remove(replaced);rows[fixed_endpoint].append(width)
    rule=production_law()
    check=verifier()
    closed=rule.from_junctions(rows)
    old=check.Arrangement.parse(rows)
    summary=[]
    witness=[labels[j][0][0] for j in range(s)]
    image=[phi[v] for v in witness]
    for age in (1,2):
        assert closed.step(rule.gf2(rule.F.fewest),None)['new']
        new=check.Arrangement.parse(closed.bits_of)
        changes=check.round_replay(old,new)
        assert check.start_audit(new)['census_open_legal']
        assert all(phi[e]==e for row in new.live for e in new.stars[row] if e<width)
        if age==1:
            assert (len(new.stars),len(new.labels))==(J,n)
        hubword=set(rows[0]);mapped={phi[v] for v in hubword}
        cycle={labels[0][0][0],labels[1][0][0],labels[0][2][0],labels[1][2][0]}
        assert len(cycle & mapped)%2==1
        assert all(len(cycle & set(row))%2==0 for row in new.stars)
        # Any bond attaining sL through the image must be the image of the
        # entire hub word, because every one of these bundles crosses together.
        assert set(witness)<=hubword and set(image)<=mapped
        assert len(hubword)==s*L==len(mapped)
        summary.append([len(new.stars),len(new.labels),len(changes)])
        old=new
    return dict(parameters=[t,s,L,unit],ages_one_two=summary,marked_order=s,
                source_bond_size=s*L,image_exceeds_or_absent=True,
                four_name_cycle=sorted(cycle),split_names=[replaced,width])

def main():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('panels',nargs='+',type=Path)
    opts=parser.parse_args()
    winners=set()
    for panel in opts.panels:
        cases=json.loads(panel.read_text())['rows']
        for row in cases:
            for k in ('least_j_then_n','least_n_then_j'):
                if row[k] is not None:
                    if isinstance(row[k],dict):
                        d=row[k];case=(d['junctions'],d['distinctions'],d['anchors'],d['per_hub'],d['spoke_weight'],1)
                    else: case=tuple(row[k])
                    winners.add(case)
    output=dict(literal_cut_controls=direct_orders(),witnesses=[replay(c) for c in sorted(winners)])
    opts.output.write_text(json.dumps(output,indent=2)+'\n')
if __name__=='__main__':
    main()
