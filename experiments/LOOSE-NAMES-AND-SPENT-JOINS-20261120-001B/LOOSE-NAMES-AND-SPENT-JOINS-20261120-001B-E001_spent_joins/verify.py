"""Independent one-name erasure, lookahead, and relabel checks on registered small cases."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
import json
from pathlib import Path
import random

import networkx as nx

import cases
import model


def erase_one(stars):
    table=defaultdict(list)
    for k, row in enumerate(stars):
        for bit in row:
            table[bit].append(k)
    live={row[0] for row in table.values() if len(row)==1}
    contact=nx.MultiGraph();contact.add_nodes_from(range(len(stars)))
    for bit, owners in table.items():
        if len(owners)==2:
            contact.add_edge(*owners,key=bit)
    family=[]
    for bit,owners in table.items():
        if len(owners)!=2 or not live.isdisjoint(owners):continue
        a,b=sorted(owners)
        l=tuple(sorted(set(contact[a])&live));r=tuple(sorted(set(contact[b])&live))
        if not l or not r:continue
        contact.remove_edge(a,b,key=bit)
        if not nx.has_path(contact,a,b):
            assert set(l).isdisjoint(r)
            family.append((bit,a,b,l,r))
        contact.add_edge(a,b,key=bit)
    return tuple(sorted(family))


def relabel(stars,seed):
    rng=random.Random(seed)
    ids=list(range(len(stars)));rng.shuffle(ids)
    bits=sorted({bit for row in stars for bit in row});images=list(bits);rng.shuffle(images)
    rename=dict(zip(bits,images,strict=True));new=[None]*len(stars)
    for k,row in enumerate(stars):new[ids[k]]=tuple(rename[b] for b in row)
    return tuple(new),{newid:oldid for oldid,newid in enumerate(ids)}


def check(stars,law,rule):
    physical=model.read(stars)
    witnesses=erase_one(stars)
    assert witnesses==tuple(sorted(model.separating_witnesses(physical)))
    detail=model.step(stars,law,rule)
    renamed,inverse=relabel(stars,20261120725)
    other=model.step(renamed,law,rule)
    assert detail.status==other.status
    if detail.status in ('stall','closed'):
        assert detail.stars==stars
        return {'status':detail.status,'witnesses':len(witnesses)}
    if detail.status!='extend':return {'status':detail.status,'witnesses':len(witnesses)}
    original=Counter((tuple(sorted(p)),len(f)) for p,f in zip(detail.parents,detail.fresh,strict=True))
    translated=Counter((tuple(sorted(inverse[k] for k in p)),len(f)) for p,f in zip(other.parents,other.fresh,strict=True))
    assert original==translated
    draws={d for row in detail.inputs for d in row}
    assert draws=={d for bits in physical.loose.values() for d in bits} and sum(len(g) for g in detail.inputs)==len(draws)
    nxt=erase_one(detail.stars)
    addition={tuple(sorted(set(l)|set(r))) for _,_,_,l,r in nxt} if rule=='spent' else set()
    assert addition==set(detail.next_added)
    if any(detail.fresh):
        q=model.read(detail.stars)
        old=cases.baseline.fixtures.multi_groups(*cases.baseline.fixtures.witnessed_end(q.graph,q.loose))
        true=Counter(v for g in set(old)|addition for v in g)
        assert tuple(true[len(stars)+i] for i in range(len(detail.fresh)))==detail.demand
    return {'status':detail.status,'witnesses':len(witnesses),'unique_spent_inputs':len(draws),'actual_newborns':len(detail.parents),'next_witnesses':len(nxt)}


def matrix_rank(stars):
    basis={}
    for row in stars:
        mask=sum(1<<v for v in row)
        while mask and mask.bit_length() in basis:
            mask^=basis[mask.bit_length()]
        if mask:
            basis[mask.bit_length()]=mask
    return len(basis)


def words_and_erasure(stars,law):
    if law=='parity':
        rank=matrix_rank(stars)
        local=[]
        for i,row in enumerate(stars):
            words=cases.baseline.fixtures.parity_words(stars,row)
            projections=cases.baseline.fixtures.expected_words('parity',len(row))
            assert words==projections
            local.append({'arity':len(row),'allowed':len(words),'essential':matrix_rank(stars[:i]+stars[i+1:])<rank})
        return local
    from pysat.solvers import Minisat22
    local=[]
    for i,row in enumerate(stars):
        with Minisat22() as solver:
            for j,other in enumerate(stars):
                if i!=j:
                    cases.baseline.fixtures.nae_add(solver,other)
            erased=solver.solve(assumptions=[-(d+1) for d in row])
            assert erased
            cases.baseline.fixtures.nae_add(solver,row)
            words=cases.baseline.fixtures.nae_words(solver,row)
            assert words==cases.baseline.fixtures.expected_words('nae',len(row))
            local.append({'arity':len(row),'allowed':len(words),'essential':erased})
    return local


def ablations():
    result={}
    for arity in (3,4):
        source=cases.baseline.path([arity,arity])
        for law in cases.LAWS:
            ordinary=model.step(source,law,'ordinary');first=model.step(source,law,'spent')
            current=first.stars
            witnesses=erase_one(current)
            assert len(witnesses)==1
            bit=witnesses[0][0]
            cells={}
            for label,suppressed in [('authorized',None),('suppressed_once',bit)]:
                step=model.step(current,law,'spent',suppress_name=suppressed)
                assert step.status=='extend'
                supplied=model.read(current).loose
                used=Counter(k for group in step.groups for k in group)
                cells[label]={'charges':[{'holder':k,'loose':len(bits),'groups':used[k],'residual':len(bits)-used[k]} for k,bits in supplied.items()],
                              'parents':step.parents,'prices':[len(g) for g in step.fresh],
                              'projections':words_and_erasure(step.stars,law)}
            assert cells['authorized']['parents']!=cells['suppressed_once']['parents']
            result[f'{law}_{arity}']={'identical_current_holdings':current,'source':source,'tested_name':bit,
              'ordinary_first_prices':[len(g) for g in ordinary.fresh], 'rival_first_prices':[len(g) for g in first.fresh], 'arms':cells}
    for law in cases.LAWS:
        src=cases.frames()['sole_parity'][0]
        first=model.step(src,law,'spent');second=model.step(first.stars,law,'spent')
        assert second.status=='extend' and len(second.parents)==1
        local=words_and_erasure(second.stars,law)
        before,after=matrix_rank(first.stars),matrix_rank(second.stars)
        if law=='parity':
            assert not second.fresh[0] and before==after and not local[-1]['essential']
        else:
            assert second.fresh[0] and local[-1]['essential']
        result[f'{law}_sole']={'old_rows':first.stars,'new_rows':second.stars[len(first.stars):], 'all_local':local,
            'old_and_new_row_rank':(before,after) if law=='parity' else None}
    return result

def run():
    result={}
    for name,(stars,r,s,depth) in cases.frames().items():
        small={}
        for law in cases.LAWS:
            small[law]={rule:check(stars,law,rule) for rule in cases.RULES}
        result[name]=small
    return {'controls':result,'suppressed_authorization_and_local_laws':ablations()}


if __name__=='__main__':
    cli=ArgumentParser();cli.add_argument('--out',type=Path,default=model.ROOT/'artifacts'/model.HERE.parent.name/model.HERE.name/'verify.json');args=cli.parse_args()
    result=run();args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(len(result['controls']),'original controls under independent erasure, recoding, and fresh-demand checks')
