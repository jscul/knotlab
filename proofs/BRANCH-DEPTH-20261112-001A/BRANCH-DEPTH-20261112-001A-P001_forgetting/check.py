#!/usr/bin/env python3
"""Focused finite checks; uniform arguments are proved in proof.md.

Only --write writes result.json in this owned family. No tracker or state
files are read or changed. NAE chain prefixes extend infinitely by choosing
successive port bits opposite, so their finite projections are exact here.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
from pathlib import Path
import subprocess
import sys

from pysat.solvers import Minisat22

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from knotlab.knots import check_knot
from knotlab.relations import Relation


def tuples(n):
    return list(itertools.product((0,1),repeat=n))


def project(rows,positions):
    return {tuple(row[i] for i in positions) for row in rows}


def free(rows,positions):
    return len(project(rows,positions))==1<<len(positions)


def is_bond(rows):
    n=len(next(iter(rows)))
    return 0<len(rows)<1<<n and all(free(rows,[i for i in range(n) if i!=d]) for d in range(n))


def minimal_supports(rows):
    n=len(next(iter(rows)))
    out=[]
    for size in range(1,n+1):
        for positions in itertools.combinations(range(n),size):
            if free(rows,positions):
                continue
            if all(free(rows,[p for p in positions if p!=drop]) for drop in positions):
                out.append(list(positions))
    return out


def cross_certificate(rows,u,v):
    union=sorted(set(u)|set(v))
    if not free(rows,u) or not free(rows,v) or free(rows,union):
        return None
    supports=minimal_supports(project(rows,union))
    selected=[union[i] for i in supports[0]]
    assert set(selected)&(set(u)-set(v))
    assert set(selected)&(set(v)-set(u))
    return {'support':selected,'kind':('canonical-knot-candidate' if len(selected)>=3
                                     else 'pair tie' if len(selected)==2 else 'unary constraint')}


def canonical(rows):
    n=len(next(iter(rows)))
    assert n>=3,'a singleton or pair tie is not a canonical knot'
    names=tuple(f'z{i}' for i in range(n))
    r=Relation(names,frozenset(tuple(map(bool,row)) for row in rows))
    report=check_knot(r,names[:-1],names[-1]).as_dict()
    assert report['is_knot']
    return report


def compose(a,b):
    return frozenset((x,z) for x,y in a for yy,z in b if y==yy)


def rectangle(r):
    if not r:
        return False
    left={a for a,b in r}
    right={b for a,b in r}
    return len(r)==len(left)*len(right)


def orbit_set(r,n):
    r=frozenset(r)
    current=r
    seen={}
    seq=[]
    while current not in seen:
        seen[current]=len(seq)+1
        seq.append(current)
        current=compose(current,r)
    return {'first_rectangular':next((i+1 for i,x in enumerate(seq) if rectangle(x)),None),
            'first_full':next((i+1 for i,x in enumerate(seq) if len(x)==n*n),None),
            'preperiod_start':seen[current],'distinct_powers':len(seq)}


def orbit_bits(r,n):
    base=tuple(sum(1<<b for a,b in r if a==i) for i in range(n))
    current=base
    seen={}
    seq=[]
    while current not in seen:
        seen[current]=len(seq)+1
        seq.append(current)
        nxt=[]
        for word in current:
            reach=0
            for i in range(n):
                if word>>i&1:
                    reach|=base[i]
            nxt.append(reach)
        current=tuple(nxt)
    rect=lambda a: bool(any(a)) and len({v for v in a if v})==1
    return {'first_rectangular':next((i+1 for i,x in enumerate(seq) if rect(x)),None),
            'first_full':next((i+1 for i,x in enumerate(seq) if all(v==(1<<n)-1 for v in x)),None),
            'preperiod_start':seen[current],'distinct_powers':len(seq)}


def matrix_checks():
    hist={}
    total=0
    for n in (1,2,3):
        all_pairs=list(itertools.product(range(n),repeat=2))
        for mask in range(1<<(n*n)):
            r=frozenset(p for i,p in enumerate(all_pairs) if mask>>i&1)
            a,b=orbit_set(r,n),orbit_bits(r,n)
            assert a==b,(n,mask,a,b)
            assert a['distinct_powers']<=1<<(n*n)
            key=str(a['first_rectangular'])
            hist[key]=hist.get(key,0)+1
            total+=1
    transient={(0,1),(1,2),(2,2)}
    t=orbit_set(transient,3)
    assert t['first_rectangular']==2 and t['first_full'] is None
    assert compose(transient,transient)==frozenset((x,2) for x in range(3))
    states=tuples(3)
    index={p:i for i,p in enumerate(states)}
    shift=frozenset((index[p],index[(p[2],p[0],x)]) for p in states for x in (0,1))
    accepted=orbit_set(shift,8)
    assert accepted['first_rectangular']==accepted['first_full']==3
    return {'relations_checked':total,'first_rectangular_histogram':hist,
            'nonfull_rectangular_control':t,'accepted_shift_register':accepted}


def occupancy_checks():
    cases=0
    tight=0
    for r in range(1,6):
        for s in range(1,15):
            for interior in itertools.product((0,1),repeat=s-1):
                occupied=[0]+[i+1 for i,b in enumerate(interior) if b]+[s]
                if all(b-a<=r for a,b in zip(occupied,occupied[1:])):
                    assert len(occupied)>=1+(s+r-1)//r
                    cases+=1
                    tight+=len(occupied)==1+(s+r-1)//r
    return {'admissible_occupancies':cases,'bound_attained':tight,
            'scope':'s<=14,r<=5; all-size counting proved in prose'}


def chain_relation(s):
    """Support order q0,z0,...,zs,qend, exact on the infinite NAE chain."""
    allowed=set()
    for pattern in tuples(s+3):
        current={pattern[0]}
        for z in pattern[1:-1]:
            current={b for a in current for b in (0,1) if len({a,b,z})>1}
        if pattern[-1] in current:
            allowed.add(pattern)
    return allowed


def chain_sat(s):
    q=list(range(1,s+3))
    zs=list(range(s+3,2*s+4))
    clauses=[]
    for a,b,z in zip(q,q[1:],zs):
        clauses.extend(([a,b,z],[-a,-b,-z]))
    # Three extra, entirely unobserved groups exercise the continuation.
    last=q[-1]
    next_id=2*s+4
    for _ in range(3):
        nxt,z=next_id,next_id+1
        next_id+=2
        clauses.extend(([last,nxt,z],[-last,-nxt,-z]))
        last=nxt
    support=[q[0],*zs,q[-1]]
    with Minisat22(bootstrap_with=clauses) as solver:
        return {p for p in tuples(len(support))
                if solver.solve(assumptions=[v if b else -v for v,b in zip(support,p)])}


def nae3():
    return {p for p in tuples(3) if len(set(p))>1}


def chain_and_control_checks():
    out=[]
    for s in range(9):
        a,b=chain_relation(s),chain_sat(s)
        assert a==b
        assert is_bond(a)
        excluded=[p for p in tuples(s+3) if p not in a]
        assert len(excluded)==2 and all(x!=y for x,y in zip(*excluded))
        out.append({'s':s,'size':s+3,'allowed':len(a),'excluded':excluded})
    reports=[{'s':s,'report':canonical(chain_relation(s))} for s in (0,1,3)]
    hstates=tuples(3)
    persistent={(p,q) for p in hstates for q in hstates if p[0]==q[0]}
    index={p:i for i,p in enumerate(hstates)}
    matrix={(index[p],index[q]) for p,q in persistent}
    assert orbit_set(matrix,8)['first_rectangular'] is None
    for p in hstates:
        for out_port in hstates:
            grow={z for z in (0,1) if len({p[1],out_port[1],z})>1}
            bounded={(u,z) for u,z in tuples(2) if len({p[0],u,z})>1}
            assert bool(grow) and bool(bounded)
    # The same physical h occurs in both tuples; all five actual bits are free.
    physical={(p[0],p[1],p[2],q[1],q[2]) for p,q in persistent}
    assert len(physical)==32 and not minimal_supports(physical)
    # Nontrivial local knots remain in the forgetting/no-endpoint example.
    bounded_report=canonical(nae3())
    local_product={(root,*local) for root in (0,1) for local in nae3()}
    product_bonds=minimal_supports(local_product)
    assert product_bonds==[[1,2,3]]
    # A full-joint projection with two non-free sides can mask coupling.
    mask={(*u,z) for u in tuples(4) if u not in ((0,0,0,0),(1,1,1,1))
          for z in (0,1) if (*u,z) not in ((0,0,1,1,0),(1,1,0,0,1))}
    assert len(mask)==26
    assert all(tuple(1-b for b in p) in mask for p in mask)
    assert len(project(mask,[0,1,2,3]))*len(project(mask,[4]))==28
    assert minimal_supports(mask)==[[0,1,2,3]]
    assert all(free(mask,[*c,4]) for k in range(4) for c in itertools.combinations(range(4),k))
    internal_report=canonical(project(mask,[0,1,2,3]))
    # General positive proposition may return a pair; keep it separately typed.
    pair={(0,0),(1,1)}
    assert free(pair,[0]) and free(pair,[1]) and minimal_supports(pair)==[[0,1]]
    positive=cross_certificate(chain_relation(1),[0,1],[2,3])
    overlapping=cross_certificate(nae3(),[0,1],[1,2])
    assert positive and len(positive['support'])==4
    assert overlapping and len(overlapping['support'])==3
    assert cross_certificate(physical,[0,1,2],[0,3,4]) is None
    assert cross_certificate(mask,[0,1,2,3],[4]) is None
    assert cross_certificate(pair,[0],[1])['kind']=='pair tie'
    return {'nae_chain_tables':out,'canonical_reports':reports,
            'persistent_matrix':orbit_set(matrix,8),
            'physical_identity_union_patterns':len(physical),
            'bounded_local_knot':bounded_report,
            'forgetting_without_endpoint':{'product_bonds':product_bonds,'root_index':0},
            'internally_constrained_counterexample':{'allowed':sorted(mask),'bonds':minimal_supports(mask),
                                                     'internal_knot_report':internal_report},
            'positive_cross_certificates':{'disjoint':positive,'overlapping':overlapping},
            'pair_control':{'allowed':sorted(pair),'bonds':[[0,1]],'kind':'pair tie, not a canonical knot'}}


def join_knots(a,b):
    return {(*p[:-1],*q[:-1]) for p in a for q in b if p[-1]==q[-1]}


def complement_knots(n):
    all_rows=tuples(n)
    pairs=[]
    for row in all_rows:
        opposite=tuple(1-b for b in row)
        if row<opposite:
            pairs.append((row,opposite))
    for mask in range(1<<len(pairs)):
        rows={r for i,pair in enumerate(pairs) if mask>>i&1 for r in pair}
        if rows and is_bond(rows):
            yield rows


def composition_checks():
    sources={n:list(complement_knots(n)) for n in (3,4)}
    count=0
    for n,m in itertools.product((3,4),repeat=2):
        for a in sources[n]:
            for b in sources[m]:
                joined=join_knots(a,b)
                assert is_bond(joined),(n,m,a,b)
                assert all(tuple(1-x for x in row) in joined for row in joined)
                count+=1
    # Without complement closure each relation can force only the same
    # shared value; choosing zero makes their join entirely free.
    atom=set(tuples(3))-{(1,1,1)}
    assert is_bond(atom)
    rejected=join_knots(atom,atom)
    assert len(rejected)==16 and not is_bond(rejected)
    return {'source_knots':{str(n):len(v) for n,v in sources.items()},'joins_checked':count,
            'noncomplement_control_rejects_binding':True,'atom_join_patterns':len(rejected)}


def neutral_link_checks():
    # Exact shift-register group p=(a,b,c), p'=(c,a,x), NAE(a,x,z).
    # link 0->2; carry 2->0. Phase is rotated so site s is a link.
    out=[]
    for s in range(11):
        next_id=4
        ports=[1,2,3]
        start=ports[0 if s%2==0 else 2]
        clauses=[]
        helpers=[]
        register=start
        for i in range(s+1):
            x=next_id;next_id+=1
            if i%2==s%2:
                z=next_id;next_id+=1
                assert ports[0]==register
                clauses.extend(([ports[0],x,z],[-ports[0],-x,-z]))
                helpers.append(z)
                register=x
            else:
                assert ports[2]==register
            ports=[ports[2],ports[0],x]
        assert register==x
        support=[start,*helpers,x]
        assert len(set(support))==len(support)
        with Minisat22(bootstrap_with=clauses) as solver:
            rows={p for p in tuples(len(support)) if solver.solve(
                assumptions=[v if b else -v for v,b in zip(support,p)])}
        assert is_bond(rows)
        assert len(support)<=s+3
        out.append({'s':s,'start_slot':0 if s%2==0 else 2,'links':len(helpers),
                    'support_size':len(support),'allowed':len(rows)})
    # Averaging a spectator away can hide failure of the required lifting.
    full_input_tables={}
    for a,t in tuples(2):
        full_input_tables[(a,t)]={(b,z) for b,z in tuples(2)
                                 if (a,b,z) in nae3() and (t==a or b==z)}
    averaged={(a,b,z) for (a,t),table in full_input_tables.items() for b,z in table}
    assert averaged==nae3()
    assert any(table!={(b,z) for b,z in tuples(2) if (a,b,z) in averaged}
               for (a,t),table in full_input_tables.items())
    return {'rotated_cycles':out,'spectator_averaging_rejected':True}


def cli_check():
    rows=chain_relation(1)
    names=['q0','z0','z1','q2']
    missing=[p for p in tuples(4) if p not in rows]
    cnf='; '.join(' '.join(('~' if b else '')+name for name,b in zip(names,p)) for p in missing)
    cmd=[sys.executable,'-B','-m','knotlab','check','--cnf',cnf,
         '--loops',*names[:-1],'--contact',names[-1],'--json']
    cp=subprocess.run(cmd,cwd=ROOT,env=dict(os.environ,PYTHONPATH=str(ROOT/'tools')),
                      text=True,capture_output=True,check=True)
    report=json.loads(cp.stdout)
    assert report['is_knot']
    return {'command':cmd,'report':report}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--write',action='store_true')
    args=ap.parse_args()
    checks={'finite_relations':matrix_checks(),'occupancy':occupancy_checks(),
            'controls':chain_and_control_checks(),'composition':composition_checks(),
            'neutral_link_cycles':neutral_link_checks(),'knotlab_cli':cli_check()}
    manifest=json.loads((HERE/'manifest.json').read_text())
    deps=[ROOT/'proofs/BONDS-AND-COUNT-20261112-001E/BONDS-AND-COUNT-20261112-001E-P001_branching_depth/proof.md',
          ROOT/'proofs/NEST-COUNT-20261112-001A/NEST-COUNT-20261112-001A-P001_finite_state/proof.md']
    result={'schema_version':3,'artifact_id':manifest['artifact_id'],'kind':'proof',
            'ticket':manifest['ticket'],'proof':manifest['proof'],'claim':manifest['claim'],
            'status':'passed','validation_level':'V1: hand proofs and same-task independent finite encodings',
            'uniform_claims':'argued-in-prose; finite checks are consistency checks',
            'checks':checks,'failures':[],
            'source_sha256':{n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in ('proof.md','check.py','manifest.json')},
            'dependency_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in deps}}
    if args.write:
        (HERE/'result.json').write_text(json.dumps(result,indent=1)+'\n')
    print(json.dumps({'status':'passed','relations':checks['finite_relations']['relations_checked'],
                      'composition_cases':checks['composition']['joins_checked'],
                      'occupancies':checks['occupancy']['admissible_occupancies'],'failures':[]},indent=1))


if __name__=='__main__':
    main()
