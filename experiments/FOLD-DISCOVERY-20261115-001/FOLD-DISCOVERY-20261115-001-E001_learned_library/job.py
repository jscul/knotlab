"""Run one fresh worker per held stream, including library loading and all verifications."""
import gzip
import hashlib
import json
from pathlib import Path
import sys
import time

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from studyio import DATA,FIRST_OUT,encoded,read,sha,verify_sources

ARMS=('primitive','learned','flat','given')


def setup(params):
    global OUT,TEST
    if set(params)-{'data_dir'}:
        raise ValueError('unexpected parameters')
    OUT=Path(params.get('data_dir',DATA)).resolve()
    design=read(OUT/'design.json')
    receipt=read(OUT/'gate-freeze.json')
    verify_sources(design['training_sources'])
    verify_sources(design['evaluation_sources'])
    if sha(OUT/'design.json')!=receipt['design_sha256'] or sha(OUT/'entry.json')!=receipt['entry_sha256']:
        raise ValueError('learned library freeze changed')
    if sha(OUT/'held.json')!=design['inputs']['held.json']:
        raise ValueError('held truth tables changed')
    TEST=read(OUT/'held.json')
    if any(set(t)!={'id','n','truth'} for t in TEST):
        raise ValueError('private attributes in test input')


def cases():
    for repeat in range(5):
        caches=('warm','cold') if repeat%2==0 else ('cold','warm')
        for cache in caches:
            offset=(repeat+int(cache=='cold'))%len(ARMS)
            for arm in ARMS[offset:]+ARMS[:offset]:
                yield f'{cache}-{repeat}-{arm}',{'cache':cache,'repeat':repeat,'arm':arm}


def run(case_id,payload):
    arm, cache, repeat=payload['arm'],payload['cache'],payload['repeat']
    if case_id!=f'{cache}-{repeat}-{arm}':
        raise ValueError('unexpected case')
    start,cpu_start=time.perf_counter_ns(),time.process_time_ns()
    entry=dag=None
    if arm=='primitive':
        from peel import PeelSolver
        def construct(n):
            return PeelSolver(n,'primitive')
    else:
        from library_solver import LibrarySolver
        if arm=='given':
            dag=read(FIRST_OUT/'fold.json')
            # Only this separately supplied, uncharged reference reads the old fold.
            truth=sum(((((x&1)&((x>>1)&1))^((x>>2)&1))<<x) for x in range(8))
            entry={'truth':truth,'expr':['XOR',['AND',['input',0],['input',1]],['input',2]]}
        else:
            entry=read(OUT/'entry.json')
            dag=entry['dag'] if arm=='learned' and entry is not None else None
        def construct(n):
            return LibrarySolver(n,'flat' if arm=='flat' else 'named',entry,dag)
    setup_wall=time.perf_counter_ns()-start
    setup_cpu=time.process_time_ns()-cpu_start
    engines={}
    rows=[]
    for task in TEST:
        start,cpu=time.perf_counter_ns(),time.process_time_ns()
        n=task['n']
        fresh=cache=='cold' or n not in engines
        if fresh:
            engines[n]=construct(n)
        engine=engines[n]
        init_ns=time.perf_counter_ns()-start
        before=engine.work_counters()
        try:
            result=engine.solve(task['truth'])
        except (AssertionError,RuntimeError,ValueError) as exc:
            after=engine.work_counters()
            result={'status':'error','error':f'{type(exc).__name__}: {exc}','truth':None,'expr':None,'circuit':None,
                    'work':{k:v-before.get(k,0) for k,v in after.items()},'timing':{},'unassigned_failure_time':True}
        output=result.get('circuit')
        output_bytes=len(encoded(output)) if output is not None else 0
        cpu_ns=time.process_time_ns()-cpu
        wall=time.perf_counter_ns()-start
        rows.append({'id':task['id'],'n':n,'setup_work':before if fresh else {},'init_ns':init_ns,
                     'cpu_ns':cpu_ns,'wall_ns':wall,'return_bytes':output_bytes,'result':result})
    path=OUT/(case_id+'.jsonl.gz')
    with gzip.open(path,'wb',compresslevel=1) as writer:
        for row in rows:
            writer.write(encoded(row)+b'\n')
    return {'arm':arm,'cache':cache,'repeat':repeat,'startup_ns':setup_wall,'startup_cpu_ns':setup_cpu,
            'tasks':len(rows),'file':path.name,'sha256':sha(path)}

