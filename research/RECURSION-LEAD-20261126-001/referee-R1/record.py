"""Reconcile the archived score, the freeze, and the earlier records."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import sys
from time import perf_counter

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = HERE.parents[2]
FREEZE = '1bae2cbd80'
CLOSURE = '10e4f22f26'


def file_at(commit, name):
    path = (STUDY/name).relative_to(ROOT)
    return subprocess.check_output(['git', 'show', f'{commit}:{path}'], cwd=ROOT)


def tracker(*args):
    return subprocess.run([sys.executable, '-B', 'scripts/track.py', *args],
                          cwd=ROOT, text=True, capture_output=True)


def json_rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def raw_score(pilot):
    rec, tower, paths, orbit_details = Counter(), Counter(), Counter(), Counter()
    breaks, returns, reaches_two = [], [], []
    for sample in ['census', 'heldout']:
        rows = json_rows(STUDY/f'recur_{sample}.jsonl')
        for r in (rows[:24] if pilot else rows):
            name = r['start']
            pinned, free = r['pinned exchange'], r['free exchange']
            rec[f'{sample} / pinned / {pinned}'] += 1
            rec[f'{sample} / R2 free / {free}'] += 1
            if pinned == 'lawful':
                path = r['orbit']
                paths[f'{sample} / '+ ' -> '.join(path)] += 1
                if r['returns']:
                    returns.append([sample, name, r['knots'], r['loose']])
                    ring = r['one ring'] and r['knots'] >= 5 and r['knots'] != 6 and set(r['loose']) == {2}
                    verdict = 'a ring as predicted' if ring else 'BREAK'
                    rec[f'{sample} / R1 returns / {verdict}'] += 1
                    if not ring:
                        breaks.append(['R1',sample,name])
                eligible = r['most shared distinctions at a knot'] > 2
                label = 'BREAK' if eligible else 'at most two shared at every knot'
                rec[f'{sample} / R3 lawful pinned / {label}'] += 1
                if eligible:
                    breaks.append(['R3',sample,name])
                    if path[0].startswith('a new start'):
                        size = int(path[0].split('(')[1].split()[0])
                        relation = 'more' if size > r['knots'] else 'equal' if size == r['knots'] else 'fewer'
                        orbit_details[f'first exchange has {relation} knots'] += 1
                    orbit_details[f'{len(path)} recorded outcomes, {sum(s.startswith("a new start") for s in path)} new starts'] += 1
            if free == 'lawful':
                breaks.append(['R2',sample,name])
    for sample in ['census','multi','rings']:
        rows = json_rows(STUDY/f'tower_{sample}.jsonl')
        for r in (rows[:2] if pilot else rows):
            for stage in r['rounds']:
                key = f"{sample} / round {stage['round']} / "
                if 'end' in stage:
                    tower[key + stage['end'].partition(':')[0]] += 1
                    continue
                for reading in ['SHORT','UPTO5']:
                    bits = stage[reading]['whole-held']
                    tower[key+f'{reading} / whole-held {bits}'] += 1
                    if bits >= 2:
                        obs = [sample,r['start'],stage['round'],reading,bits]
                        reaches_two.append(obs)
                        breaks.append(['T1',*obs])
    recomputed = {'recursion':rec, 'orbits of lawful pinned exchanges':paths, 'returners':returns,
                  'tower':tower, 'tower steps':reaches_two, 'breaks':breaks}
    published = json.loads((STUDY/'score.json').read_text())
    agreement = {k: recomputed[k] == v for k,v in published.items()}
    if not pilot:
        assert all(agreement.values()) and published.keys() == recomputed.keys()
    return {'score_fields_agree_full':agreement if not pilot else None,
            'recursion':rec, 'pinned_iteration':paths, 'branched_lawful_pinned':orbit_details,
            'tower':tower, 'prediction_failures':dict(Counter(f[0] for f in breaks))}


def main():
    parse = argparse.ArgumentParser()
    parse.add_argument('--pilot',action='store_true')
    parse.add_argument('--output',type=Path)
    args = parse.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(1 << 30,1 << 30))
    start = perf_counter()
    tables = raw_score(args.pilot)
    before = file_at(FREEZE, 'README.md')
    after = file_at(CLOSURE, 'README.md')
    assert after.startswith(before)
    required = ['README.md','tower2.py','recur.py']
    data = [f'{name}.jsonl' for name in ('recur_census','recur_heldout','tower_census','tower_multi','tower_rings')]
    tables['freeze'] = {'frozen_commit':FREEZE,'outputs_commit':CLOSURE,
                        'frozen_prose_unchanged_prefix':True,
                        'frozen_code_unchanged_at_results':{p:file_at(FREEZE,p)==file_at(CLOSURE,p) for p in required[1:]},
                        'archive_sha256':{p:hashlib.sha256(file_at(CLOSURE,p)).hexdigest() for p in data},
                        'archive_bytes_equal_closed_commit':all(file_at(CLOSURE,p)==(STUDY/p).read_bytes() for p in data)}
    result = tracker('objects-gate',str(STUDY.relative_to(ROOT)/'README.md'))
    tables['prior_work_gate'] = {'exit':result.returncode,'message':(result.stdout+result.stderr).strip()}
    queries = ['shortest changes exchanged pattern ring pins returns',
               'whole-held class single knot labels layers',
               'growth implied parity forbidding fresh count old states']
    prior = {}
    for q in (queries[:1] if args.pilot else queries):
        res = tracker('objects',q,'--until','2026-11-26','--exclude',STUDY.name,'--limit','3','--json')
        res.check_returncode()
        hits = json.loads(res.stdout)
        prior[q] = {k:[x['record'] for x in hits[k]] for k in ('index','other_epics')}
    tables['prior_search_records'] = prior
    # Outside the frozen study: a single not-all-equal support has six states.
    # A change that preserves the whole allowed set is defined without parity.
    nae = set(range(1,7))
    tables['one_not_all_equal_support'] = {
        'allowed_states':sorted(nae),
        'changes_preserving_every_state':[
            change for change in range(8) if {word ^ change for word in nae} == nae],
        'smallest_nonzero_change_somewhere':min((a ^ b).bit_count() for a in nae for b in nae if a != b),
    }
    tables['seconds'] = round(perf_counter()-start,4)
    if args.output:
        args.output.write_text(json.dumps(tables,indent=2)+'\n')
    print(tables['score_fields_agree_full'],tables['branched_lawful_pinned'],tables['seconds'])


if __name__ == '__main__':
    main()
