"""One sequential, caching learner per complete held stream and timing repeat."""
import gzip
import hashlib
import json
from pathlib import Path
import pickle
import struct
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TICKET = HERE.parent.name
DATA = ROOT / 'artifacts' / TICKET / HERE.name
sys.path.insert(0, str(ROOT / 'research' / TICKET))
sys.path.insert(0, str(HERE))
TIMES = struct.Struct('<QQ')
TRACE_KEYS = ('prefix_labels', 'teacher_mismatch_mask', 'teacher_rows', 'try_fold', 'used_fold',
              'proposal_stages', 'proposal_truths', 'verifier_calls', 'verifier_packed_checks',
              'verifier_rows', 'adaptive_feedback', 'accepted_stage', 'physical_sha256')
CORE = ('median', 'gated-warm', 'gated-cold')


def compact(value):
    return json.dumps(value, separators=(',', ':'), allow_nan=False).encode()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def get_json(path):
    return json.loads(path.read_bytes())


def setup(params):
    from stream import load_split, ROW_ORDER
    global FREEZE, TASKS, ORDER
    if params:
        raise ValueError('the held study has no variable scientific parameters')
    FREEZE = get_json(DATA / 'gate-freeze.json')
    design = get_json(DATA / 'design.json')
    if sha(DATA / 'design.json') != FREEZE['design_sha256']:
        raise ValueError('gate freeze lacks the bound pretraining design')
    for path, expected in design['sources'].items():
        if sha(ROOT / path) != expected:
            raise ValueError(f'changed bound source {path}')
    if sha(DATA / 'held.bin') != design['splits']['held']:
        raise ValueError('held split changed')
    if sha(DATA / 'gate.json') != FREEZE['gate_file_sha256']:
        raise ValueError('gate changed before opening held stream')
    TASKS = tuple(load_split(DATA / 'held.bin', 'held'))
    ORDER = ROW_ORDER


def cases():
    for repeat in range(3):
        for mode in CORE[repeat:] + CORE[:repeat]:
            yield f'{repeat}-{mode}', [repeat, mode]
    for mode in ('always', 'median-warm', 'adaptive'):
        yield f'0-{mode}', [0, mode]


def run(case_id, payload):
    repeat, arm = payload
    if case_id != f'{repeat}-{arm}':
        raise ValueError('invalid case identity')
    started, start_cpu = time.perf_counter_ns(), time.process_time_ns()
    from lesson import run_task
    from gate import checkpoint_sha256
    from search import SearchBackend
    mode = arm.split('-')[0]
    checkpoint = None
    if mode == 'gated':
        checkpoint = get_json(DATA / 'gate.json')
        if checkpoint['sha256'] != checkpoint_sha256(checkpoint):
            raise ValueError('changed checkpoint')
    if arm.endswith('-warm'):
        metadata = FREEZE['snapshots'][mode]
        path = DATA / metadata['name']
        if sha(path) != metadata['sha256']:
            raise ValueError('cache snapshot differs from frozen receipt')
        with gzip.open(path, 'rb') as reader:
            backend = pickle.load(reader)
    elif mode in ('always', 'gated'):
        from study import fold
        backend = SearchBackend(fold_dag=fold())
    else:
        backend = SearchBackend()
    setup_wall_ns = time.perf_counter_ns() - started
    setup_cpu_ns = time.process_time_ns() - start_cpu
    initial = backend.ledger()
    timings = bytearray()
    receipts = hashlib.sha256()
    detail = (DATA / f'trace-{arm}.jsonl.gz') if repeat == 0 else None
    writer = gzip.open(detail.with_suffix('.partial'), 'wb', compresslevel=1) if detail else None
    if writer:
        writer.write(compact(TRACE_KEYS)+b'\n')
    programs = {}
    stats = dict(tasks=0, try_fold=0, used_fold=0, first_exact=0, final_fold=0,
                 verifier_calls=0, verifier_packed_checks=0, verifier_rows=0, teacher_rows=0,
                 proposals=0, expanded_NANDs_returned=0)
    try:
        for target in TASKS:
            row = run_task(backend, target, ORDER, mode, checkpoint)
            if row['proposal_truths'][-1] != target:
                raise AssertionError('learner returned an incorrect program')
            timings += TIMES.pack(row['elapsed_ns'], row['cpu_ns'])
            program = row['accepted_program']
            token = program['physical_sha256']
            row['physical_sha256'] = token
            receipt = compact([row[k] for k in TRACE_KEYS]) + b'\n'
            receipts.update(receipt)
            if writer:
                writer.write(receipt)
                if token not in programs:
                    programs[token] = program
            stats['tasks'] += 1
            for key in ('try_fold','used_fold','verifier_calls','verifier_packed_checks','verifier_rows','teacher_rows'):
                stats[key] += row[key]
            stats['first_exact'] += (row['proposal_truths'][0] == target)
            stats['final_fold'] += bool(program['macro_uses'])
            stats['proposals'] += len(row['proposal_truths'])
            stats['expanded_NANDs_returned'] += program['expanded_NANDs']
    finally:
        if writer:
            writer.close()
    if detail:
        detail.with_suffix('.partial').replace(detail)
        manifest = DATA / f'programs-{arm}.jsonl.gz'
        with gzip.open(manifest, 'wb', compresslevel=1) as dest:
            for item in programs.values():
                dest.write(compact(item)+b'\n')
    times = DATA / f'times-{case_id}.bin'
    times.write_bytes(timings)
    return {'arm':arm,'repeat':repeat,'setup_wall_ns':setup_wall_ns,'setup_cpu_ns':setup_cpu_ns,
            'times':times.name,'times_sha256':sha(times),'trace_hash':receipts.hexdigest(),
            'first_run_trace': detail.name if detail else None, 'trace_keys': TRACE_KEYS,
            'program_manifest':manifest.name if detail else None, 'growth_before':initial,
            'growth_after':backend.ledger(), 'stats':stats}
