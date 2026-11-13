"""Separate scalar/SAT verification of the aggregate shortcut.

Only aggregate_* outputs are written. The original receipt and its files are
checked for immutability. No producer semantic functions are imported.
"""
from __future__ import annotations

import gzip
import hashlib
import itertools as it
import json
from pathlib import Path

import verify as V

OUT=V.OUT
ROOT=V.ROOT


def main():
    witness=json.loads((OUT/'aggregate_witness.json').read_text())
    coverage=json.loads((OUT/'aggregate_coverage.json').read_text())
    old_receipt=OUT/'receipt.json'
    old_hash=hashlib.sha256(old_receipt.read_bytes()).hexdigest()
    assert old_hash==coverage['summary']['old_receipt_sha256']
    old=json.loads(old_receipt.read_text())
    for name,digest in old['files'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    source=witness['source']
    source_file=ROOT/source['file']
    with gzip.open(source_file,'rt') as stream:
        row=json.loads(next(line for n,line in enumerate(stream,1) if n==source['line']))
    assert row['limit_only'] and row['defs'][0]==source['definition']
    definition=row['defs'][0]
    assert not any(cl=='SELF' and set(args)=={0,1,2} for cl,args in definition[2])
    greatest,history=V.gfp(definition)
    assert greatest==V.ALL
    current=V.NAE;orbit=[];depth_relations=[]
    while current not in orbit:
        orbit.append(current);current=V.apply(definition,current);depth_relations.append(current)
    first_dead=next((n for n,relation in enumerate(depth_relations,1) if not relation),None)
    assert first_dead==source['first_dead']==4
    result=dict(source=source,source_sha256=hashlib.sha256(source_file.read_bytes()).hexdigest(),
                gfp=[list(x) for x in sorted(greatest)],first_finite_death=first_dead,
                validation_level='V1-separate-algorithm-same-task',
                source_label='finite-flip source not assessed',old_receipt_sha256=old_hash,
                original_receipt_and_all_recorded_files_unchanged=True)
    reconstructed={}
    for label in ('ray','branch'):
        cut=witness[label+'_cut']
        names,factors=V.construct(definition,{tuple(p) for p in cut['expanded_paths']})
        rows=V.enumerate_states(names,factors)
        sat_rows=V.sat_states(names,factors)
        assert rows==sat_rows
        numeric=sorted(sum(r[name]<<j for j,name in enumerate(cut['names'])) for r in rows)
        assert numeric==witness[label+'_allowed_assignments']
        reconstructed[label]=rows
        result[label+'_model_count']=len(rows)
        result[label+'_incidence']=V.forest_certificate(names,factors)
    assert result['ray_incidence']['is_forest']
    ray_names=witness['ray_cut']['names']
    assert V.project(reconstructed['branch'],ray_names)==V.project(reconstructed['ray'],ray_names)
    result['branch_projection_equals_ray']=True
    target=[ray_names[x] for x in witness['ray_cut']['target']]
    pairs=list(it.product(('a','b','c'),target))
    seen=set();exclusions=[]
    for size in (2,3):
        for first,second in pairs:
            for extra in it.combinations([x for x in ray_names if x not in (first,second)],size-2):
                support=tuple(sorted((first,second,*extra)))
                if support in seen:continue
                seen.add(support)
                table=V.project(reconstructed['ray'],support)
                assert len(table)==1 << size,(support,table)
                completions={''.join(map(str,values)):next(r for r in reconstructed['ray']
                             if tuple(r[x] for x in support)==values) for values in table}
                exclusions.append(dict(variables=list(support),allowed=[''.join(map(str,t)) for t in table],
                                       completion_for_each_allowed_state=completions))
    assert len(exclusions)==len(witness['ray_small_supports'])==39
    result['all_eligible_pairs']=[list(p) for p in pairs]
    result['all_cheaper_ray_supports']=exclusions
    result['cheaper_ray_support_counts']={str(n):sum(len(s)==n for s in seen) for n in (2,3)}
    ray_cert=V.projected_certificate(reconstructed['ray'],witness['ray_minimum_witness'])
    side_cert=V.projected_certificate(reconstructed['branch'],witness['unrestricted_support'])
    assert len(ray_cert['variables'])==4 and len(ray_cert['allowed'])==14
    assert len(side_cert['variables'])==3 and len(side_cert['allowed'])==6
    assert any(set(pair)<=set(side_cert['variables']) for pair in pairs)
    for first,second in pairs:
        assert len(V.project(reconstructed['branch'],[first,second]))==4
    V.knotlab_cli(ray_cert,'aggregate_ray')
    V.knotlab_cli(side_cert,'aggregate_side')
    # Recheck the earlier control using this verifier without rewriting it.
    control_names=['a','b','c','d','x']
    factors=[(('a','b','x'),V.NAE),(('x','c','d'),V.NAE)]
    control_rows=V.enumerate_states(control_names,factors)
    assert control_rows==V.sat_states(control_names,factors)
    control=V.projected_certificate(control_rows,['a','b','c','d'])
    assert len(control['allowed'])==14
    V.knotlab_cli(control,'aggregate_control')
    result.update(ray_bond=ray_cert,unrestricted_bond=side_cert,
                  exact_aggregate_minima=dict(ray=4,unrestricted=3),
                  side_free_control_model_count=len(control_rows),
                  checks=['all 512 ray assignments: scalar = SAT = producer',
                          'all 2048 branch assignments: scalar = SAT = producer',
                          '39 cheaper ray supports across all six endpoint pairs are full',
                          'all single-deletion tables full',
                          'knotlab K1-K3 for both bonds and the side-free control'])
    (OUT/'aggregate_verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k in ('first_finite_death','ray_model_count','branch_model_count',
                                                          'cheaper_ray_support_counts','exact_aggregate_minima',
                                                          'original_receipt_and_all_recorded_files_unchanged')},indent=2))


if __name__=='__main__':main()
