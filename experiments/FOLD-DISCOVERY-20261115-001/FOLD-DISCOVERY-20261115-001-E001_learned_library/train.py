"""Acquire a library from separate training programs. This entry point opens only the training split."""
import gzip
import json
from pathlib import Path
import sys
import time
from studyio import DATA,encoded,read,save_new,sha,verify_sources


def certify(item):
    if item is None:
        return 0
    dag=item['dag']
    for x in range(8):
        bits=[x>>j&1 for j in range(3)]+[0,1]
        for a,b in dag['gates']:
            if max(a,b)>=len(bits) or min(a,b)<0:
                raise ValueError('learned circuit has a forward operand')
            bits.append(1^(bits[a]&bits[b]))
        if bits[dag['output']]!=((item['truth']>>x)&1):
            raise ValueError('frozen physical fold disagrees with discovered semantic class')
    return 8*len(dag['gates'])


def train(out):
    design=read(out/'design.json')
    verify_sources(design['training_sources'])
    if sha(out/'train.json')!=design['inputs']['train.json'] or (out/'gate-freeze.json').exists():
        raise ValueError('unexpected training data or a finished acquisition')
    start,cpu_start=time.perf_counter_ns(),time.process_time_ns()
    from peel import PeelSolver
    import discover
    targets=read(out/'train.json')
    engines={}
    records=[]
    programs=[]
    for target in targets:
        t=time.perf_counter_ns()
        n=target['n']
        if n not in engines:
            engines[n]=PeelSolver(n,'primitive')
        engine=engines[n]
        before=engine.work_counters()
        try:
            result=engine.solve(target['truth'])
        except (ValueError,AssertionError,RuntimeError) as exc:
            after=engine.work_counters()
            result={'status':'error','error':f'{type(exc).__name__}: {exc}', 'expr':None,'truth':None,
                    'work':{k:v-before.get(k,0) for k,v in after.items()}}
        if result['status']=='exact':
            if result['truth']!=target['truth']:
                raise AssertionError('training circuit disagrees')
            encoded(result['circuit'])
            programs.append({'task_id':target['id'],'expr':result['expr']})
        records.append({'id':target['id'],'n':n,'elapsed_ns':time.perf_counter_ns()-t,'result':result})
    solve_end=time.perf_counter_ns()
    fit=discover.fit(programs)
    fit_end=time.perf_counter_ns()
    selected=fit['selected']
    entry={k:selected[k] for k in ('expr','truth','dag')} if selected is not None else None
    validation_nands=certify(entry)
    save_new(out/'entry.json',entry)
    verification_and_export_end=time.perf_counter_ns()
    cpu=time.process_time_ns()-cpu_start
    elapsed=verification_and_export_end-start
    # Evidence I/O is outside the deployed acquisition time. Emitting the executable checkpoint is paid.
    save_new(out/'candidates.json',fit)
    with gzip.open(out/'training.jsonl.gz','xb',compresslevel=1) as writer:
        for row in records:
            writer.write(encoded(row)+b'\n')
    receipt={'design_sha256':sha(out/'design.json'),'entry_sha256':sha(out/'entry.json'),
             'candidates_sha256':sha(out/'candidates.json'),'training_log_sha256':sha(out/'training.jsonl.gz'),
             'wall_ns':elapsed,'cpu_ns':cpu,'training_solve_and_setup_ns':solve_end-start,
             'fit_ns':fit_end-solve_end,'certificate_and_export_ns':verification_and_export_end-fit_end,
             'training_tasks':len(targets),'accepted_training_programs':len(programs),
             'failed_training_tasks':len(targets)-len(programs),'export_validation_scalar_nands':validation_nands,
             'frozen_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
    save_new(out/'gate-freeze.json',receipt)
    print(json.dumps({'receipt':receipt,'selected':selected},indent=2))

if __name__=='__main__':
    train(Path(sys.argv[1]).resolve() if len(sys.argv)>1 else DATA)
