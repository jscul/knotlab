"""Bind the public task design, fit the decision on training data only, and freeze it."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import pickle
import statistics
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TICKET = HERE.parent.name
NOTES = ROOT / 'research' / TICKET
DATA = ROOT / 'artifacts' / TICKET / HERE.name
PREVIOUS = ROOT / 'artifacts/FOLD-REUSE-20261115-001/FOLD-REUSE-20261115-001-E001_second_learner'
FOLD_SHA = '271dbaaab837a5ad91962c12ec421385adf44cb82358698a6bd1bd7576dab907'
COST_SHA = '81b68acce193e96cba29dfe8e6e27c15172c385310cab4ff63b722eaa442a00b'
sys.path.insert(0, str(NOTES))
sys.path.insert(0, str(HERE))
import stream
from gate import checkpoint_sha256, fit
from lesson import run_task
from search import PRIMITIVE_RELATIVE, SearchBackend


def encode(value):
    return json.dumps(value, separators=(',', ':'), sort_keys=True, allow_nan=False).encode()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_json(path, value):
    path.write_bytes(encode(value) + b'\n')


def new_json(path, value):
    with path.open('xb') as target:
        target.write(encode(value) + b'\n')


def read_json(path):
    return json.loads(path.read_bytes())


def fold():
    raw = (PREVIOUS / 'fold.json').read_bytes()
    if hashlib.sha256(raw).hexdigest() != FOLD_SHA:
        raise ValueError('source fold changed')
    return json.loads(raw)


def basis_check():
    receipt = read_json(DATA / 'design.json')
    for key, expected in receipt['sources'].items():
        if digest(ROOT / key) != expected:
            raise ValueError(f'frozen source changed: {key}')
    return receipt


def bind():
    files = [HERE / s for s in ('search.py', 'lesson.py', 'gate.py', 'study.py', 'job.py', 'contract.json', 'identity.json')]
    files += [NOTES / 'stream.py', NOTES / 'preregistration.md', ROOT / PRIMITIVE_RELATIVE,
              PREVIOUS / 'fold.json', PREVIOUS / 'source_cost.json']
    if digest(PREVIOUS / 'source_cost.json') != COST_SHA or digest(PREVIOUS / 'fold.json') != FOLD_SHA:
        raise ValueError('source receipt changed')
    design = {'sources': {str(p.relative_to(ROOT)): digest(p) for p in files},
              'splits': {s: digest(DATA / (s + '.bin')) for s in ('train','held')},
              'ordered_targets': stream.ORDERED_TRUTH_SHA256,
              'bound_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
    new_json(DATA / 'design.json', design)


def save_backend(name, backend):
    path = DATA / (name + '.pickle.gz')
    with gzip.open(path, 'xb', compresslevel=1) as writer:
        pickle.dump(backend, writer, protocol=pickle.HIGHEST_PROTOCOL)
    return {'name': path.name, 'sha256': digest(path), 'bytes': path.stat().st_size,
            'cache': backend.ledger()['cache']}


def train():
    basis = basis_check()
    if (DATA / 'gate-freeze.json').exists():
        raise ValueError('a gate is already frozen')
    wall0, cpu0 = time.perf_counter_ns(), time.process_time_ns()
    train_path = DATA / 'train.bin'
    if digest(train_path) != basis['splits']['train']:
        raise ValueError('training split changed')
    tasks = list(stream.load_split(train_path, 'train'))
    amounts = [[[], []] for _ in tasks]
    modes = ('median','always')
    paid = []
    first_signal = None
    for repeat in range(3):
        backends = (SearchBackend(), SearchBackend(fold_dag=fold()))
        for i, target in enumerate(tasks):
            for a in ((0,1) if (repeat + i) % 2 == 0 else (1,0)):
                result = run_task(backends[a], target, stream.ROW_ORDER, modes[a])
                if result['proposal_truths'][-1] != target:
                    raise AssertionError('training program failed')
                amounts[i][a].append(result['cpu_ns'])
            if first_signal is None:
                first_signal = time.perf_counter_ns()-wall0
        paid.append([b.ledger() for b in backends])
    records = []
    for t, (default, probe) in zip(tasks, amounts):
        prefix = [(x,(t >> x) & 1) for x in stream.ROW_ORDER[:8]]
        records.append({'prefix': prefix, 'median_cost':statistics.median(default),
                        'fold_cost':statistics.median(probe)})
    checkpoint = fit(records[64:])
    if checkpoint['sha256'] != checkpoint_sha256(checkpoint):
        raise ValueError('checkpoint digest failed before export')
    new_json(DATA / 'gate.json', checkpoint)
    # Retaining the learned worker and its on-demand public cache is part of its bill.
    snapshots = {'gated': save_backend('training-fold-cache', backends[1])}
    paid_wall = time.perf_counter_ns() - wall0
    paid_cpu = time.process_time_ns() - cpu0
    # Grant the comparator's measured-training cache in a separate favorable control.
    snapshots['median'] = save_backend('training-median-cache', backends[0])
    train_log = DATA / 'training.json.gz'
    with gzip.open(train_log, 'xb', compresslevel=1) as writer:
        writer.write(encode({'cpu_ns':amounts, 'warmup_count':64,'passes':3,
                             'mode_order':modes,'counts_per_pass':paid}))
    freeze = {'design_sha256':digest(DATA / 'design.json'), 'training_targets':len(tasks),
              'training_rows_used_for_fit':len(records)-64, 'paid_training_wall_ns':paid_wall,
              'paid_training_cpu_ns':paid_cpu, 'first_training_pair_wall_ns':first_signal,
              'training_log_sha256':digest(train_log), 'gate_file_sha256':digest(DATA / 'gate.json'),
              'snapshots':snapshots, 'frozen_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
    new_json(DATA / 'gate-freeze.json', freeze)
    print(json.dumps({'gate':checkpoint,'training_seconds':paid_wall/1e9,
                      'cache_bytes':snapshots['gated']['bytes']},indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('bind','train'))
    command = parser.parse_args().command
    (bind if command == 'bind' else train)()
