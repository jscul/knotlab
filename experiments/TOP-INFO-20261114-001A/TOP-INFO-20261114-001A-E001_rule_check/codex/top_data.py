"""Read-only sources and exact selections for the frozen TOP census."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import sys
import time
sys.dont_write_bytecode = True
for _name in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[_name] = '1'
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CARRY = ROOT / 'experiments/CARRY-BOUND-20261114-001A/CARRY-BOUND-20261114-001A-E001_window/codex'
READ = ROOT / 'experiments/READ-RULE-20261114-001B/READ-RULE-20261114-001B-E001_coverage/codex'
for directory in (HERE, CARRY):
    if str(directory) not in sys.path:
        sys.path.append(str(directory))
import inputs
import window
coverage = inputs.module('top_read_coverage', READ / 'coverage.py')


def dump(name, value):
    path = (HERE / name).resolve()
    if not path.is_relative_to(HERE):
        raise ValueError('write outside TOP CODEX forbidden')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')


def top_order(key):
    return hashlib.sha256(('TOP:' + key).encode()).hexdigest()


def load_raw(row):
    return coverage.read_raw(row)['result']


def frozen_file(path, *, sha256=True):
    stat = path.stat()
    item = dict(path=str(path.relative_to(ROOT)), bytes=stat.st_size, mtime_ns=stat.st_mtime_ns)
    if sha256:
        item['sha256'] = inputs.digest(path)
    return item


def build_catalog():
    start = time.monotonic()
    index = json.loads((READ / 'source_index.json').read_text())
    source = ROOT / index['source']
    stat = source.stat()
    if (stat.st_size, stat.st_mtime_ns) != (index['size'], index['mtime_ns']):
        raise ValueError('CARRY source changed since READ streaming index')
    read = json.loads((READ / 'results.json').read_text())
    families = {r['key']: r for r in read['families']}
    paths = {}
    with (CARRY / 'paths_full/results.jsonl').open() as stream:
        for line in stream:
            rec = json.loads(line)
            p = rec.get('result') or {}
            paths[rec['case']] = dict(status=rec['status'], path_class=p.get('class'),
                eventually_bounded=p.get('eventually_bounded'), complete=p.get('complete'),
                period=p.get('period'), uniform_cost_bound=p.get('uniform_cost_bound'),
                missing_residues=p.get('missing_residues'))
    exceptions = {r['key'] for r in json.loads((READ / 'summary.json').read_text())['Q1']['exception_only_families']}
    rows = []
    for indexed in index['rows']:
        row = dict(indexed)
        old = families[row['key']]
        if (old['verdict'], old['in_scope'], old['stratum'], old['weight']) != (row['verdict'], row['in_scope'], row['stratum'], row['weight']):
            raise ValueError('READ metadata and source index disagree')
        p = paths.get(row['key'])
        verdict = ('bounded_window' if row['verdict'] == 'bounded' else
                   'bounded_path_DP' if p and p['status'] == 'ok' and p['path_class'] == 'bounded' else
                   row['verdict'])
        r = old['R']
        residues = [dict(residue=a['residue'], s_mod_period=a['s_mod_period'],
                        Q_residues=a['Q_residues'], U=a['U'], applies=a['any_state_survives'],
                        exception_only=a['killed_in_every_carried_Q']) for a in r.get('residues', [])]
        if not residues:
            carried = old['carried']
            for phase, mask in enumerate(carried['masks'][carried['preperiod']:]):
                possible = any(mask >> k & 1 for k, x, z in old['candidates'])
                residues.append(dict(residue=phase, s_mod_period=(carried['preperiod']+phase)%carried['period'],
                    Q_residues=[], U=[], applies=None if possible else False, exception_only=None))
        known_absent = all(a['applies'] is False for a in residues)
        flags = [a['applies'] for a in residues]
        row.update(final_verdict=verdict, bounded=verdict.startswith('bounded_'), path_DP=p,
                   key_sha256=old['key_sha256'], exception_family=row['key'] in exceptions,
                   R=dict(complete=all(f is not None for f in flags),
                          every_residue=False if False in flags else None if None in flags else True,
                          some_residue=True if True in flags else None if None in flags else False,
                          residues=residues, carried_preperiod=old['carried']['preperiod'],
                          carried_period=old['carried']['period'],
                          Q_preperiod=r.get('Q_preperiod'), Q_period=r.get('Q_period'),
                          basis='some repeating state carrying the candidate position and failing the exception'))
        rows.append(row)
    bounded = sorted((r['key'] for r in rows if r['bounded']), key=top_order)[:200]
    selected = {r['key'] for r in rows if not r['bounded']} | set(bounded)
    census = inputs.load_records()
    forgetting = sorted((k for k, r in census.items() if r['verdict'] == 'certified'), key=top_order)[:100]
    if len(bounded) != 200 or len(forgetting) != 100:
        raise ValueError('control selection too small')
    result = dict(schema_version=1, scope_id='TOP-INFO-20261114-001A',
        rows=rows, selected_two_block=sorted(selected, key=top_order), bounded_controls=bounded,
        forgetting_controls=[dict(key=k, r=census[k]['r']) for k in forgetting],
        brute_control_selection=None,
        brute_selection_ambiguity='Which 30 census families and selection rule are intended for the brute-force gate? Only the 200 bounded and 100 forgetting selections are specified; no official brute sample is chosen.',
        source_index=dict(path=str((READ / 'source_index.json').relative_to(ROOT)),
                          source=str(source.relative_to(ROOT)), bytes=stat.st_size, mtime_ns=stat.st_mtime_ns,
                          sha256=index['sha256'], hash_basis='reused READ streamed SHA-256 with matching size and mtime'),
        sources=[frozen_file(p) for p in [READ / 'results.json', READ / 'summary.json', READ / 'source_index.json',
                    READ / 'coverage.py', CARRY / 'paths_full/results.jsonl', CARRY / 'summary.json',
                    ROOT / 'research/TOP-INFO-20261114-001/preregistration.md',
                    ROOT / 'research/TOP-INFO-20261114-001/advisor_review_answer.md',
                    ROOT / 'research/TOP-INFO-20261114-001/codex_spec.md']],
        seconds=time.monotonic()-start)
    dump('catalog.json', result)
    return result


if __name__ == '__main__':
    from collections import Counter
    cat = build_catalog()
    print(json.dumps(dict(families=len(cat['rows']), counts=dict(Counter(('in:' if r['in_scope'] else 'out:')+r['final_verdict'] for r in cat['rows'])),
        two_block=len(cat['selected_two_block']), bounded_controls=len(cat['bounded_controls']),
        forgetting_controls=len(cat['forgetting_controls']), seconds=cat['seconds']), indent=2))
