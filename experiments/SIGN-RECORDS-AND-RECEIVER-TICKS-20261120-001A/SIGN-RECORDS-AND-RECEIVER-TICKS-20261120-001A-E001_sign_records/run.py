"""Regenerate or check the registered finite experiment and source-bound evidence receipt."""
import argparse
from fractions import Fraction as F
import gzip
import json
import os
from pathlib import Path
import resource
import subprocess
import sys

for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[name]='1'
soft, hard=resource.getrlimit(resource.RLIMIT_AS)
cap=4*(1024**3)
resource.setrlimit(resource.RLIMIT_AS,(cap if soft==resource.RLIM_INFINITY else min(soft,cap),hard))
from physical_histories import HERE, OUT, ROOT, RESEARCH, digest, run as physical, save
from signed_comparisons import run as signed


def read(name):
    path=OUT/name
    if name.endswith('.gz'):
        with gzip.open(path,'rt') as source:return json.load(source)
    return json.loads(path.read_text())


def audit_outputs():
    record=read('physical_histories.json.gz');cross=read('signed_comparisons.json');old=read('archived_events.json.gz')
    # Rebuild expected physical endpoints from the two logical preparation maps, independent of the gate simulator.
    def logical(word,orientation):return tuple((word>>(i+orientation))&1 for i in (0,2,4,6))
    checked=0;false_sign_claims=0
    for key,case in record['histories'].items():
        orientation,random,copy,reset,ready,reader=key.split('/')
        orientation,random,copy,reset,ready=map(int,(orientation,random,copy,reset,ready))
        for arm,paths in enumerate(case['literal_histories']):
            for path in paths:
                d,m,w,r=logical(path['states'][0],orientation);assert (w,r)==(0,ready)
                expected_w=m if copy else 0;expected_m=0 if reset else m^arm
                assert logical(path['states'][case['cut']],orientation)==(d,expected_m,expected_w,ready)
                expected_r=ready^expected_m^(expected_w if reader=='PV' else 0)
                assert logical(path['states'][-1],orientation)==(d,expected_m,expected_w,expected_r)
                checked+=1
    signed_rows=cross['crossed_sign_and_history'];assert len(signed_rows)==4
    for history in record['programs']:
        trials=[r for r in signed_rows if r['history']==history]
        assert {r['quantum_plus'] for r in trials}=={'0','1'} and len({r['ordinary_detector_fired'] for r in trials})==1
        false_sign_claims+=sum(r['fixed_sign_unoccupied']!=r['quantum_plus'] for r in trials)
    for sign in (1,-1):
        trials=[r for r in signed_rows if r['input_sign']==sign]
        assert len({r['quantum_plus'] for r in trials})==1 and len({r['ordinary_detector_fired'] for r in trials})==2
    assert false_sign_claims==2
    # The four-state code can pass every allowed one-read covariance test while failing the sign cross above.
    group=record['covariance']['independent_signed_four_state_comparison'];identity=next(row for row in group if not row['physical_operations'])
    calibrated=[t['word_one_and_change_minus'] for t in identity['checks']]
    assert calibrated==[['1/2','0'],['1/2','1'],['0','1/2'],['1','1/2']]
    effects=cross['effects']; assert effects['imaginary_projector']['contrast']=='0' and effects['tilted_real_projector']['contrast']=='4/5'
    for r in effects.values():
        assert F(r['contrast'])**2<=F(r['square_of_sharp_absolute_contrast_bound'])
    assert all(v['complete_paths']==55050240 for v in old['summary']['switch_loaded_directions'])
    return dict(physical_program_endpoints_checked=checked,independent_covariance_ordinary_chances=sum(2*len(r['checks']) for r in group),
                colliding_predictions_for_scorer_claim=false_sign_claims,signed_effects_checked=len(effects))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true',help='Compare every byte of existing outputs without writing.')
    args=parser.parse_args();check=args.check
    science=dict(physical=physical(check),signed=signed(check))
    cmd=[sys.executable,'-B',str(HERE/'archived_events.py')]
    if check:cmd.append('--check')
    subprocess.run(cmd,stdout=subprocess.PIPE,check=True)
    old=read('archived_events.json.gz');science['native']=old['summary'];science['cross_checks']=audit_outputs()
    files={HERE/'contract.json',HERE/'identity.json',RESEARCH/'preregistration.md',RESEARCH/'design_for_review.md',
           RESEARCH/'review_candidate_v2.md',RESEARCH/'design_reviews.md',*HERE.glob('*.py')}
    # The canonical checker ran as a subprocess. Include its local package sources without any cache files.
    files.update((ROOT/'tools'/'knotlab').glob('*.py'))
    for name,h in old['sources'].items():
        p=ROOT/name;assert digest(p)==h;files.add(p)
    data=['physical_histories.json.gz','archived_events.json.gz','signed_comparisons.json']
    receipt=dict(schema_version=1,ticket=HERE.parent.name,experiment=HERE.name,evidence_stage='exploratory',referee='pending',result=science,
                 inputs={str(p.relative_to(ROOT)):digest(p) for p in sorted(files)},outputs={n:digest(OUT/n) for n in data},
                 resource_cap_bytes=cap,numerical_threads=1)
    save('receipt.json',receipt,check)
    print(json.dumps(dict(verified=check,receipt_sha256=digest(OUT/'receipt.json'),outputs=receipt['outputs'],independent_checks=science['cross_checks']),sort_keys=True))

if __name__=='__main__':main()
