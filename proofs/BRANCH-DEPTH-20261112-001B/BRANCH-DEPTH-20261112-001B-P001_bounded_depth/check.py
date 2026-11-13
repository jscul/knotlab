"""Exact checks for a different actual branching limit-only family.

No active sibling proof or external mutable data is read. --write-result
writes only this proof family's result.json.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import itertools as it
import json
import os
from pathlib import Path
import subprocess
import sys

from pysat.card import CardEnc
from pysat.solvers import Solver

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SOURCE=ROOT/'artifacts/LIMIT-ONLY-20261112-001A/LIMIT-ONLY-20261112-001A-E001_limit_only/sample_2.jsonl.gz'
TOP=set(it.product((0,1),repeat=3))
NAE=TOP-{(0,0,0),(1,1,1)}
MAIN=[3,2,[['SELF',[3,0,2]],['SELF',[4,2,1]],['SELF',[1,4,3]],['K',[0,2,4]]]]
CONTROL=[3,2,[['SELF',[3,4,2]],['SELF',[1,3,2]],['SELF',[1,4,2]],['K',[0,4,3]],['SELF',[1,0,3]]]]


def read_source(line,expected):
    with gzip.open(SOURCE,'rt') as stream:
        row=json.loads(next(text for n,text in enumerate(stream,1) if n==line))
    assert row['defs']==[expected]
    assert not any(cl=='SELF' and set(args)=={0,1,2} for cl,args in expected[2])
    return row


def image(definition,previous):
    allowed=set()
    for assignment in it.product((0,1),repeat=5):
        if all(tuple(assignment[j] for j in args) in (NAE if callee=='K' else previous)
               for callee,args in definition[2]):
            allowed.add(assignment[:3])
    return allowed


def orbits(definition):
    current=TOP;greatest_steps=[]
    while True:
        greatest_steps.append(sorted(current))
        updated=image(definition,current)
        if updated==current:break
        assert updated<current
        current=updated
    greatest=current
    current=NAE;seen=[];finite=[]
    while current not in seen:
        seen.append(current)
        current=image(definition,current)
        finite.append(current)
    first_dead=next((j for j,relation in enumerate(finite,1) if not relation),None)
    assert greatest==TOP and first_dead==4
    return dict(greatest=sorted(greatest),greatest_steps=greatest_steps,
                first_finite_death=first_dead,finite_relation_sizes=list(map(len,finite)),
                finite_relations=[sorted(r) for r in finite])


def ray(definition,depth):
    greatest=orbits(definition)['greatest']
    a,b,c=0,1,2;next_id=3;knots=[];copies=[];frontiers=[]
    for level in range(depth+1):
        x,y=next_id,next_id+1;next_id+=2
        environment=[a,b,c,x,y];copies.append(tuple(environment))
        first=None
        for callee,args in definition[2]:
            actual=tuple(environment[j] for j in args)
            if callee=='K':knots.append(actual)
            elif first is None:first=actual
            else:frontiers.append(actual)
        assert first is not None
        a,b,c=first
    frontiers.append((a,b,c))
    # Every frontier gets exactly the independently computed port summary.
    assert set(map(tuple,greatest))==TOP
    return next_id,knots,copies,frontiers


def cnf(knots):
    return [clause for triple in knots for clause in ([j+1 for j in triple],[-j-1 for j in triple])]


def table_scalar(n,knots,support):
    out=set();models=0
    for assignment in it.product((0,1),repeat=n):
        if all(len({assignment[j] for j in knot})==2 for knot in knots):
            models+=1;out.add(tuple(assignment[j] for j in support))
    return out,models


def table_sat(solver,support):
    return {values for values in it.product((0,1),repeat=len(support))
            if solver.solve(assumptions=[j+1 if bit else -j-1 for j,bit in zip(support,values)])}


def canonical_check(allowed,label):
    names=['c','x','y'];excluded=TOP-set(allowed)
    clauses=[' '.join(('~' if value else '')+name for name,value in zip(names,row))
             for row in sorted(excluded)]
    command=[sys.executable,'-B','-m','knotlab','check','--cnf','; '.join(clauses) or 'c ~c',
             '--loops','c','x','--contact','y','--json']
    report=json.loads(subprocess.check_output(command,cwd=ROOT,text=True,
                      env={**os.environ,'PYTHONPATH':str(ROOT/'tools')}))
    assert report['is_knot']==bool(excluded)
    return dict(label=label,command=command,report=report)


def verify_main():
    scalar=[];pair_checks=0;top_target_checks=0;deletions=0;canonical=[]
    for depth in range(1,13):
        n,knots,copies,frontiers=ray(MAIN,depth)
        # Reconstruct the stated formula from actual substitutions.
        assert copies[1][:3]==(copies[0][3],0,2)
        for i in range(2,depth+1):assert copies[i][:3]==(copies[i-1][3],copies[i-2][3],2)
        support=(2,copies[depth-1][3],copies[depth][4])
        targets=copies[depth][3:]
        with Solver(name='g4',bootstrap_with=cnf(knots)) as solver:
            allowed=table_sat(solver,support)
            assert allowed==NAE
            for dropped in range(3):
                keep=support[:dropped]+support[dropped+1:]
                assert table_sat(solver,keep)==set(it.product((0,1),repeat=2));deletions+=1
            for top,target in it.product(range(3),targets):
                assert table_sat(solver,(top,target))==set(it.product((0,1),repeat=2));pair_checks+=1
            for target in targets:
                assert table_sat(solver,(0,1,2,target))==set(it.product((0,1),repeat=4));top_target_checks+=1
        if depth<=4:
            got,models=table_scalar(n,knots,support)
            assert got==NAE and models==8*3**(depth+1)
            for target in targets:
                got,_=table_scalar(n,knots,(0,1,2,target))
                assert len(got)==16
            scalar.append(dict(depth=depth,variables=n,models=models,frontier_calls=len(frontiers)))
        if depth in (1,2,5,12):canonical.append(canonical_check(allowed,f'depth {depth}'))
    canonical.append(canonical_check(TOP,'negative: full relation'))
    return dict(depths=list(range(1,13)),all_eligible_pair_tables=pair_checks,
                full_top_triple_plus_target_tables=top_target_checks,
                single_deletion_tables=deletions,scalar=scalar,canonical=canonical)


def verify_control():
    calls=[args for cl,args in CONTROL[2] if cl=='SELF']
    local=[args for cl,args in CONTROL[2] if cl=='K']
    assert all(2 not in args for args in local)
    assert all(2 not in args or args.index(2)==2 for args in calls)
    checked=0
    for depth in range(1,7):
        n,knots,copies,_=ray(CONTROL,depth)
        assert all(copy[2]==2 for copy in copies)
        assert all(2 not in knot for knot in knots)
        with Solver(name='g4',bootstrap_with=cnf(knots)) as solver:
            for bits in it.product((0,1),repeat=2):
                for target in copies[-1][3:]:
                    assert solver.solve(assumptions=[3 if bits[0] else -3,
                                                    target+1 if bits[1] else -target-1])
                    checked+=1
    return dict(third_port_retained=True,ignored_by_every_literal=True,
                third_port_only_passed_as_third_or_dropped=True,pair_checks=checked,
                no_bond_with_top_c='argued-in-prose: exact free product factor')


def verify_finite_flip_control():
    checked=[]
    for depth in range(1,13):
        n,knots,copies,_=ray(MAIN,depth)
        background=[0]*n;background[2]=1
        assert all(len({background[v] for v in knot})==2 for knot in knots)
        pairs=[tuple(v for v in knot if v!=2) for knot in knots]
        assert len({v for pair in pairs for v in pair})==2*len(pairs)
        changes=sorted(v+1 for pair in pairs for v in pair)
        cardinality=CardEnc.atmost(lits=changes,bound=len(pairs)-1,top_id=n)
        with Solver(name='g4',bootstrap_with=cnf(knots)+cardinality.clauses+[[-3]]) as solver:
            assert not solver.solve()
        # One private flip per local knot suffices for this finite ray.
        new=list(background);new[2]=0
        for pair in pairs:new[pair[0]]=1
        assert all(len({new[v] for v in knot})==2 for knot in knots)
        checked.append(dict(depth=depth,required_private_changes=len(pairs)))
    return checked


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write-result',action='store_true');args=parser.parse_args()
    main_row=read_source(25697,MAIN);control_row=read_source(16375,CONTROL)
    main_orbit=orbits(MAIN);control_orbit=orbits(CONTROL)
    assert main_row['first_dead']==main_orbit['first_finite_death']
    assert control_row['first_dead']==control_orbit['first_finite_death']
    result=dict(artifact_id='BRANCH-DEPTH-20261112-001B-P001',status='Proved',
                claim='For every s>=1, L(s)=3, over all three top ports, both depth-s own distinctions on the first SELF branch, and arbitrary finite supports throughout the infinite family.',
                all_depth_authority='argued-in-prose: explicit TOP extension, exact NAE projection, and all eligible pairs free',
                main_source=dict(file=str(SOURCE.relative_to(ROOT)),line=25697,definition=MAIN),
                control_source=dict(file=str(SOURCE.relative_to(ROOT)),line=16375,definition=CONTROL),
                source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                main_orbit=main_orbit,control_orbit=control_orbit,
                checks=verify_main(),retained_but_unused_control=verify_control(),
                finite_flip_negative_control=verify_finite_flip_control(),
                finite_flip_conclusion='At an explicitly extended allowed state, c requires infinitely many private changes; no universal native-at-a-solution claim.',
                validation=dict(level='V1-separate-algorithm-same-task',
                                methods=['symbolic extension proof','scalar assignment enumeration','PySAT Glucose4','knotlab CLI'],
                                external_review=False,trusted_kernel=False),
                novelty='field-level novelty not assessed',source_contribution=1,
                nonclaims=['no corpus frequency','no arithmetic counting','no general family classification',
                           'no positive native-at-infinity conclusion','no exact minimum for every individual endpoint pair'])
    bindings=[
        ROOT/'proofs/BONDS-AND-COUNT-20261112-001E/BONDS-AND-COUNT-20261112-001E-P001_branching_depth/manifest.json',
        ROOT/'proofs/BONDS-AND-COUNT-20261112-001E/BONDS-AND-COUNT-20261112-001E-P001_branching_depth/proof.md',
        ROOT/'research/NEST-COUNT-20261112-001/nest_count.md',
        ROOT/'research/LIMIT-ONLY-20261112-001/referee-R1/report.md',
        HERE/'proof.md',HERE/'check.py']
    result['dependency_and_check_bindings']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                                            for p in bindings}
    if args.write_result:(HERE/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status='passed',main_first_death=main_orbit['first_finite_death'],
                          control_first_death=control_orbit['first_finite_death'],
                          main_gfp_size=len(main_orbit['greatest']),control_gfp_size=len(control_orbit['greatest']),
                          pair_tables=result['checks']['all_eligible_pair_tables'],
                          top_target_tables=result['checks']['full_top_triple_plus_target_tables'],
                          scalar=result['checks']['scalar'],
                          control_pair_checks=result['retained_but_unused_control']['pair_checks'],
                          finite_flip_depths=len(result['finite_flip_negative_control'])),indent=2))


if __name__=='__main__':main()
