"""Validate the delivered referee record; optionally replay every chosen lasso.

No producer code is imported. Inputs are exact allowed data paths and our
fresh scripts. This is a replay/integrity check, not external replication.
"""
import argparse,ast,copy,datetime,gzip,hashlib,json,resource,time
from pathlib import Path
from lasso_certify import DP,OUT,ROOT,controls,test_lasso

def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def chosen():
    out={}
    for line in (OUT/'lasso_results.jsonl').open():
        r=json.loads(line)
        if r['certified']:out[r['key']]=r
    for name in ['lasso_improvements.json','lasso_higher_cap.json']:
        for r in json.loads((OUT/name).read_text()):
            if r.get('certificate'):out[r['key']]=r['certificate']
    return out

def replay(c):
    dp=DP(json.loads(c['key']),c['cap'])
    got=test_lasso(dp,c['entry'],tuple(c['prefix']),tuple(c['period']),max_steps=c['repeat_at_depth']+5)
    assert got is not None
    for k in ['entry','prefix','period','repeat_from_depth','repeat_at_depth','repeat_length','cap','eventual_bound','values','top_port_masks','all_depths_have_bond','all_depth_bound','vector','residue_values','vector_states']:
        assert got[k]==c[k],(c['key'],k)
    return got

def provenance():
    b=json.loads((OUT/'branch_reading_results.json').read_text())
    inputs=dict(b['input_sha256'])
    names=['codex_spec.md','codex_spec_addendum.md','every_ray.md','preregistration.md']
    for name in names:
        p=ROOT/'research/EVERY-RAY-20261113-001'/name
        inputs.setdefault(str(p.relative_to(ROOT)),sha(p))
    for pattern in [ROOT/'experiments/SHORT-DESC-20261112-001A/SHORT-DESC-20261112-001A-E001_description_census/dlang.py',ROOT/'experiments/LIMIT-STATE-20261112-001A/LIMIT-STATE-20261112-001A-E001_limit_states/census.py',ROOT/'experiments/BOND-DEPTH-20261112-001A/BOND-DEPTH-20261112-001A-E001_spine_bonds/census.py']:
        inputs[str(pattern.relative_to(ROOT))]=sha(pattern)
    outputs={p.name:sha(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.name not in ['brief_codex.md','codex_last_message.md','provenance.json','validation_results.json']}
    data=dict(scope='EVERY-RAY-20261113-001 / referee-R1/codex',start_utc='2026-11-13T23:37:45Z',artifact_freeze_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),python='/home/jscul/p-vs-np-contact-first/.venv/bin/python -B',offline=True,max_concurrent_python_computations=3,path_address_space_limit_bytes=4*1024**3,input_sha256=inputs,output_sha256=outputs,read_boundary='No EVERY-RAY or REACH producing Python; no raw LIMIT-ONLY archive; allowed source modules and data plus fresh referee code only.',writes='Only this referee folder; existing brief and last-message files left untouched.',commands=[
    'lasso_certify.py --limit 5 --seconds 20',
    'lasso_certify.py --limit 50 --seconds 12',
    'lasso_certify.py --offset 50 --limit 154 --seconds 12',
    'lasso_certify.py --offset 165 --limit 39 --seconds 12',
    'min_path_certify.py --only-unfound --seconds 40',
    'min_path_certify.py --seconds 20',
    'lasso_automaton.py --cap 7 --seconds 30 --maxnodes 3000',
    'compact_evidence.py',
    'improve_lassos.py',
    'higher_cap_lassos.py',
    'summarize_referee.py',
    'direct_brute.py --depth 4',
    'direct_brute.py --fixtures --depth 5',
    'direct_brute.py --lassos --depth 4',
    'branch_reading_check.py',
    'validate_referee.py --freeze --replay-lassos'
    ],recorded_implementation_repairs=[
    'Initial independent S selection used largest reachable selfholding index; row165 metadata exposed it. Replaced with first selfholding in main expansion call order. Existing completed rows already matched S and sizes. Resumed row165 onward.',
    'First summary launch failed on an optional mixed flag with value null; retained raw flag and used bool only for the count.',
    'Reading lane initial launch failed at parse time; fixed before computation.',
    'Large referee-only outputs were losslessly compressed; receipts bind the exact uncompressed bytes.'
    ])
    (OUT/'provenance.json').write_text(json.dumps(data,indent=2)+'\n')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--freeze',action='store_true');ap.add_argument('--replay-lassos',action='store_true');args=ap.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(4*1024**3,4*1024**3))
    t=time.monotonic()
    if args.freeze:provenance()
    p=json.loads((OUT/'provenance.json').read_text())
    for name,h in p['input_sha256'].items():assert sha(ROOT/name)==h,('input changed',name)
    for name,h in p['output_sha256'].items():assert sha(OUT/name)==h,('output changed',name)
    for file in OUT.glob('*.py'):ast.parse(file.read_text(),filename=str(file))
    for r in json.loads((OUT/'compression_receipt.json').read_text()):
        with gzip.open(OUT/r['file'],'rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==r['uncompressed_sha256']
    s=json.loads((OUT/'recomputation_summary.json').read_text());inv=json.loads((OUT/'family_certificates.json').read_text())
    assert len(inv)==s['total_families']==204
    assert sum(x['single_lasso_certified'] for x in inv)==s['single_lasso_certificates']==188
    assert sum(x.get('all_depths_have_bond',False) for x in inv)==s['strict_all_positive_depth_lassos']==185
    assert sum(x['per_depth_uncarried_certified'] for x in inv)==s['per_depth_combined_certificates']==201
    assert not s['censored_mismatches']
    d=json.loads((OUT/'direct_brute_results.json').read_text())
    assert d['summary']['families']==18 and d['summary']['complete_depth_cells']==71
    assert d['summary']['mismatches']==d['summary']['uncarried_mismatches']==0
    b=json.loads((OUT/'branch_reading_results.json').read_text());assert not b['errors']
    control=controls()
    certificates=chosen();replayed=0
    if args.replay_lassos:
        for c in certificates.values():
            replay(c);replayed+=1
            if replayed%25==0:print(json.dumps(dict(lassos_replayed=replayed)),flush=True)
    first=next(iter(certificates.values()));bad=copy.deepcopy(first);bad['residue_values'][0]+=1
    rejected=False
    try:replay(bad)
    except AssertionError:rejected=True
    assert rejected
    result=dict(passed=True,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),seconds=round(time.monotonic()-t,3),inputs_hashed=len(p['input_sha256']),outputs_hashed=len(p['output_sha256']),all_python_parsed=True,compression_roundtrips=True,lassos_available=len(certificates),lassos_replayed=replayed,mutated_residue_rejected=rejected,growing_chain_control=control,summary_consistent=True,direct_enumeration_mismatches=0,reading_integrity_errors=b['errors'])
    (OUT/'validation_results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)
if __name__=='__main__':main()
