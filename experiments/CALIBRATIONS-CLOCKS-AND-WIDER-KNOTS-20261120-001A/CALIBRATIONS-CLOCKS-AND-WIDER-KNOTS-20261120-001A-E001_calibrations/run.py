"""Run the fixed preparations, forks, continuations and ordinary snapshots, in order."""
import argparse
import gzip
import json
import os
from pathlib import Path
import resource
import subprocess
import sys

for setting in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[setting]='1'
soft, hard = resource.getrlimit(resource.RLIMIT_AS)
cap = 4 * 1024**3
resource.setrlimit(resource.RLIMIT_AS, (cap if soft==resource.RLIM_INFINITY else min(soft,cap),hard))
import study_io
from study_io import HERE, ROOT, OUT, RESEARCH, digest, write


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true',help='Verify all stored evidence without changing it.')
    args=parser.parse_args();study_io.VERIFY_ONLY=args.check
    inputs=set(HERE.glob('*.py')) | {HERE/'contract.json', HERE/'identity.json', RESEARCH/'preregistration.md',RESEARCH/'advisor_receipt.json'}
    observed=set()
    def audit(event, data):
        if event=='open' and isinstance(data[0],str) and isinstance(data[1],str) and data[1].startswith('r'):
            observed.add(data[0])
    sys.addaudithook(audit)
    from preparations import principles, instruments
    from effects import run as compressed_effects
    from native_checks import native, stress
    result={}
    result['step_two']=dict(principles())
    command=[sys.executable,'-B',str(HERE/'games.py')]
    if args.check:command.append('--check')
    games=json.loads(subprocess.check_output(command,text=True))
    result['step_three_game_replays']=games['archive_counts']
    result['step_three_compressed_joint_measurements']=compressed_effects()
    result['step_four']=dict(instruments())
    result['step_five_native']=native();result['step_five_sample']=stress()
    with gzip.open(OUT/'games.json.gz','rt') as handle:
        inputs.update(ROOT/path for path in json.load(handle)['inputs'])
    for name in sorted(observed):
        path=Path(name)
        if path.suffix not in ('.py','.json','.gz','.md','.txt','.cnf'):continue
        path=path.resolve()
        if not path.is_relative_to(ROOT) or path.is_relative_to(OUT):continue
        if path.relative_to(ROOT).parts[0] in ('experiments','proofs','artifacts','research','tools') and path.exists():
            inputs.add(path)
    # Files served by the bytecode cache were still program inputs. The source digest is portable.
    for mod in list(sys.modules.values()):
        name=getattr(mod,'__file__',None)
        if not isinstance(name,str):continue
        path=Path(name).resolve()
        if path.suffix=='.py' and path.is_relative_to(ROOT) and path.relative_to(ROOT).parts[0] in ('experiments','proofs','tools'):
            inputs.add(path)
    numeric=['principles.json.gz','games.json.gz','compressed_effects.json','posteriors.json.gz','posteriors_named.json.gz',
             'ordinary_refusals.json.gz','fresh_sources.json.gz','source_summary.json']
    receipt=dict(schema_version=1,experiment=HERE.name,stage='exploratory',referee='pending',
        counted=result,inputs_sha256={str(p.relative_to(ROOT)):digest(p) for p in sorted(inputs)},
        outputs_sha256={n:digest(OUT/n) for n in numeric},python=f'{sys.version_info.major}.{sys.version_info.minor}',
        resource_cap_bytes=cap,numerical_threads=1)
    write('receipt.json',receipt)
    print(json.dumps(dict(verified=args.check,result=result,receipt_sha256=digest(OUT/'receipt.json')),sort_keys=True))

if __name__=='__main__':
    main()
