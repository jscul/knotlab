"""Decode unrestricted-arity branches from pair correlations; replay finite examples exactly."""
from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path
import sys

import networkx as nx

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
OUT=ROOT/'artifacts'/HERE.parent.name/HERE.name
OLD='READS-HOLDERS-SOURCES-20261120-001B'
sys.path.insert(0,str(ROOT/'experiments'/OLD/(OLD+'-E001_irredundant')))
from controls import allowed, deletions, lawful, next_stage
from model import growth, nae_counts, nae_separator, width


def read_definition(rows,with_core):
    total,counts=nae_counts(rows)
    n=width(rows)
    corr={(i,j):Fraction(total-2*v,total) for (i,j),v in counts.items()}
    def c(i,j):
        return corr[tuple(sorted((i,j)))]
    assert all(abs(v)<1 for v in corr.values())
    # All triples that are mixed have a total of two disagreements per word.
    core=tuple(s for s in combinations(range(n),3) if with_core and
               sum(counts[p] for p in combinations(s,2))==2*total)
    core_names={i for h in core for i in h}
    core_graph=nx.Graph()
    for h in core:
        core_graph.add_edges_from(combinations(h,2))
    core_components=[sorted(v) for v in nx.connected_components(core_graph)]
    component_of={i:k for k,part in enumerate(core_components) for i in part}
    graph=nx.Graph()
    graph.add_nodes_from(range(n))
    for a,b in combinations(range(n),2):
        if a in core_names and component_of[a]==component_of.get(b):
            continue
        if not any(c(a,b)==c(a,x)*c(x,b) for x in range(n) if x not in (a,b)):
            graph.add_edge(a,b)
    outer=sorted(tuple(sorted(h)) for h in nx.find_cliques(graph) if len(h)>=3)
    constraints=tuple(sorted(set(core)|set(outer)))
    assert nae_separator(rows,constraints) is None
    assert nae_separator(constraints,rows) is None
    return {'names':n,'states':total,'core_names':sorted(core_names),'core_components':core_components,'core_triples':core,
            'branch_holders':outer,'recovered_exact_relation':True,
            'recovered_physical_rows':set(map(frozenset,rows))==set(map(frozenset,constraints)),
            'correlation_range':[str(min(corr.values())),str(max(corr.values()))]}


def reached_test(rows,with_core):
    assert lawful(rows,'nae') and all(deletions(rows,'nae')[0])
    first,stage,births=next_stage(rows,'nae')
    assert first=='births'
    second,next_births=growth(stage,'nae')
    report=read_definition(stage,with_core)
    report.update(source_rows=rows,source_width=width(rows),first_count=len(births),
                  next_status=second,next_count=len(next_births),stage_arities=sorted(map(len,stage)))
    return report


def signs_report():
    controls=[]
    for q in (4,5):
        # Two of the wide holder's bit names, 0 and 1, belong to a cycle.
        # Name 2 joins the two other ternaries. The remaining names are loose.
        rows=((0,1,*range(3,q+1)),(0,2,q+1),(2,1,q+2))
        assert lawful(rows,'nae') and all(deletions(rows,'nae')[0])
        states=allowed(rows,'nae')
        total,pairs=nae_counts(rows)
        assert len(states)==total
        value=lambda i,j:Fraction(total-2*pairs[tuple(sorted((i,j)))],total)
        controls.append({'rows':rows,'width':width(rows),'words':total,'coheld_01':str(value(0,1)),
                         'other_product':str(value(0,2)*value(2,1))})
    return controls


def private_moments():
    output=[]
    for q in (3,4):
        # Every test includes an external variable attached through bit zero.
        rows=(tuple(range(q)),(0,q,q+1))
        words=allowed(rows,'nae')
        private=1
        others=[i for i in rows[0] if i!=private]
        outside=q
        def moment(inds):
            return Fraction(sum(1 if sum(x>>i&1 for i in inds)%2==0 else -1 for x in words),len(words))
        linear=sum(moment((j,outside)) for j in others)
        higher=moment((*others,outside)) if q==4 else 0
        calc=-(linear+higher)/(1<<(q-2))
        assert calc==moment((private,outside))
        output.append({'arity':q,'rows':rows,'outside':outside,'private':private,
                       'actual':str(calc),'lower_order_contribution':str(-linear/(1<<(q-2))),
                       'higher_order_contribution':str(-higher/Fraction(1<<(q-2)))})
    return output


def main():
    report={'one_holder_arbitrary_arity':{},'cyclic_ternary_core_and_wider_branches':{}}
    for k in range(3,10):
        row=reached_test((tuple(range(k)),),False)
        assert row['names']==k*k and row['next_count']==k*(k-1)//2
        report['one_holder_arbitrary_arity'][str(k)]=row
    for h in (4,5,7,9):
        # 0 is the core's only connection to the wider root. The last
        # two ternaries share 3 and 4, so the core has a repeated meeting.
        core=((0,1,2),(1,3,4),(2,3,4))
        source=(*core,(0,*range(5,h+5)))
        row=reached_test(source,True)
        assert row['names']==5+h*h and row['next_count']==h*(h-1)//2 and row['recovered_physical_rows']
        report['cyclic_ternary_core_and_wider_branches'][str(h)]=row
    report['separate_cyclic_ternary_parts_joined_by_one_wide_holder']={}
    for number in (2,3):
        h=4
        cores=[tuple(5*i+j for j in r) for i in range(number) for r in ((0,1,2),(1,3,4),(2,3,4))]
        central=(*[5*i for i in range(number)],*range(5*number,5*number+h))
        source=(*cores,central)
        row=reached_test(source,True)
        assert len(row['core_components'])==number and row['recovered_physical_rows'] and row['next_count']==6
        report['separate_cyclic_ternary_parts_joined_by_one_wide_holder'][str(number)]=row
    report['cyclic_sign_test']=signs_report()
    report['private_conditional_mean']=private_moments()
    triangle=((0,1,3),(0,2,4),(1,2,5))
    first,stage,births=next_stage(triangle,'nae')
    assert first=='births' and len(births)==1
    report['reached_wide_knot_with_private_distinction_and_three_inputs']={
        'source':triangle,'first_stage':stage,'births':births,'next_count':len(growth(stage,'nae')[1]),
        'states':nae_counts(stage)[0]}
    (OUT/'tree_reading.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['cyclic_sign_test'],report['private_conditional_mean'])


if __name__=='__main__':
    main()
