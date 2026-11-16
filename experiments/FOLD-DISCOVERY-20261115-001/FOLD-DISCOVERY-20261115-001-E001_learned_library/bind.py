"""Write the two design-bound splits without fitting a candidate or running a solver."""
import json
import sys
import time
from studyio import DATA,FIRST_EXP,FIRST_NOTES,FIRST_OUT,HERE,NOTES,ROOT,read,save_new,sha

def bind(out):
    sys.path.insert(0,str(NOTES))
    sys.path.insert(0,str(FIRST_NOTES))
    import training_tasks
    import tasks
    out.mkdir(parents=True,exist_ok=True)
    if (out/'design.json').exists():
        raise ValueError('design already sealed')
    train=list(training_tasks.training_tasks())
    held=list(tasks.stage2_tasks())
    if len(train)!=24 or len(held)!=24 or any(set(r)!= {'id','n','truth'} for r in train+held):
        raise ValueError('invalid discovery or evaluation inputs')
    if {r['n'] for r in train}!={4,6,8} or {r['n'] for r in held}!={5,7,9}:
        raise ValueError('input arities are not separated')
    if len({(r['n'],r['truth']) for r in train+held})!=48:
        raise ValueError('repeated target across discovery and transfer')
    # Preserve the sequence reserved during phase one, with its own public order.
    save_new(out/'train.json',train)
    save_new(out/'held.json',held)
    save_new(out/'grading.json',tasks.grading('stage2'))
    if not read(FIRST_OUT/'result.json')['gate']['discover']:
        raise ValueError('supplied fold did not qualify for discovery')
    shared=[HERE/'studyio.py',FIRST_EXP/'peel.py',FIRST_EXP/'solver.py']
    fit_sources=shared+[HERE/'train.py',HERE/'discover.py',NOTES/'training_tasks.py']
    evaluation_sources=[HERE/'library_solver.py',HERE/'job.py',HERE/'bind.py',HERE/'contract.json',
                        HERE/'identity.json',NOTES/'preregistration.md',NOTES/'assess.py',FIRST_NOTES/'tasks.py',
                        FIRST_OUT/'fold.json',FIRST_OUT/'result.json',FIRST_OUT/'freeze.json',
                        ROOT/'artifacts/FOLD-REUSE-20261115-001/FOLD-REUSE-20261115-001-E001_second_learner/panel.json']
    old=ROOT/'artifacts/FOLD-GATE-20261115-001/FOLD-GATE-20261115-001-E001_gated_stream'
    evaluation_sources.extend([old/'train.bin',old/'held.bin'])
    data_digests={name:sha(out/name) for name in ('train.json','held.json','grading.json')}
    fingerprint=lambda items: {str(p.relative_to(ROOT)):sha(p) for p in items}
    save_new(out/'design.json',{'training_sources':fingerprint(fit_sources),'evaluation_sources':fingerprint(evaluation_sources),
                                'inputs':data_digests,'bound_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())})
    print(json.dumps(data_digests,indent=2))

if __name__=='__main__':
    from pathlib import Path
    bind(Path(sys.argv[1]).resolve() if len(sys.argv)>1 else DATA)
