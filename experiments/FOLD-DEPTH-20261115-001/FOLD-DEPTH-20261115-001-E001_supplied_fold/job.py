"""Shared-runner job. Each case is one method on the entire bound stream."""
import gzip
import hashlib
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TICKET = HERE.parent.name
DEFAULT_OUT = ROOT / 'artifacts' / TICKET / HERE.name
sys.path.insert(0, str(HERE))
ARMS = ('primitive','named','flat','peel-primitive','peel-named','peel-flat')


def encode(obj):
    return json.dumps(obj, sort_keys=True, separators=(',',':'), allow_nan=False).encode()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def setup(params):
    global OUT, PUBLIC, DAG
    if set(params) - {'data_dir'}:
        raise ValueError('unexpected job parameters')
    OUT = Path(params.get('data_dir', DEFAULT_OUT)).resolve()
    bound = json.loads((OUT/'freeze.json').read_bytes())
    for name, expected in bound['sources'].items():
        if sha(ROOT/name) != expected:
            raise ValueError(f'changed study source {name}')
    for name, expected in bound['inputs'].items():
        if sha(OUT/name) != expected:
            raise ValueError(f'changed bound input {name}')
    PUBLIC = json.loads((OUT/'public.json').read_bytes())
    DAG = json.loads((OUT/'fold.json').read_bytes())
    if any(set(item) != {'id','n','truth'} for item in PUBLIC):
        raise ValueError('public tasks may expose only an opaque receipt ID, arity and table')


def cases():
    for repeat in range(5):
        for arm in ARMS[repeat%len(ARMS):] + ARMS[:repeat%len(ARMS)]:
            yield f'cold-{repeat}-{arm}', {'cache':'cold','repeat':repeat,'arm':arm}
    for arm in ARMS:
        yield f'warm-0-{arm}', {'cache':'warm','repeat':0,'arm':arm}


def run(case_id, payload):
    from solver import Solver
    from peel import PeelSolver
    arm, cache = payload['arm'], payload['cache']
    if case_id != f"{cache}-{payload['repeat']}-{arm}":
        raise ValueError('invalid case')
    engine_type = PeelSolver if arm.startswith('peel-') else Solver
    role = arm.removeprefix('peel-')
    engines = {}
    receipts = []
    for task in PUBLIC:
        start, cpu = time.perf_counter_ns(), time.process_time_ns()
        n = task['n']
        new_instance = cache=='cold' or n not in engines
        if new_instance:
            engines[n] = engine_type(n=n, arm=role, fold_dag=DAG if role=='named' else None)
        created = time.perf_counter_ns() - start
        # The solver has no access to the study receipt ID, stratum, source AST, or match.
        backend = engines[n]
        before = backend.work_counters()
        try:
            result = backend.solve(task['truth'])
        except (AssertionError, ValueError, RuntimeError) as exc:
            # Preserve paid costs and move on to the next target. A failed run
            # can never establish equal correctness or trigger discovery.
            after = backend.work_counters()
            result = {'status':'error','error':f'{type(exc).__name__}: {exc}',
                      'work':{k:v-before.get(k,0) for k,v in after.items()},
                      'expr':None,'truth':None,'circuit':None,'expanded_NANDs':0,
                      'timing':{'search_cpu_ns':0,'search_seconds':0,'build_seconds':0,
                                'verification_seconds':0},'unassigned_failure_time':True}
        returned = result.get('circuit')
        payload_bytes = len(encode(returned)) if returned is not None else 0
        total_cpu = time.process_time_ns()-cpu
        total_wall = time.perf_counter_ns()-start
        receipts.append({'id':task['id'],'n':n,'setup_wall_ns':created,
                         'setup_work':before if new_instance else {},
                         'return_bytes':payload_bytes,'wall_ns':total_wall,'cpu_ns':total_cpu,
                         'result':result})
    file = OUT/f'{case_id}.jsonl.gz'
    with gzip.open(file,'wb',compresslevel=1) as writer:
        for receipt in receipts:
            writer.write(encode(receipt)+b'\n')
    return {'arm':arm,'repeat':payload['repeat'],'cache':cache,'tasks':len(receipts),
            'file':file.name,'sha256':sha(file),'stream_total_ns':sum(r['wall_ns'] for r in receipts)}
