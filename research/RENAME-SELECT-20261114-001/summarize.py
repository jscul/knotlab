"""Read the fixed-panel runner output and compute blind and operational totals."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from statistics import mean
import sys

from problems import audit as audit_tasks

TICKET = 'RENAME-SELECT-20261114-001'
ROOT = Path(__file__).resolve().parents[2]
FAMILY = TICKET + '-E001_selector'
BASE = ROOT / 'artifacts' / TICKET / FAMILY
LANGUAGES = ('raw', 'reuse')
BLIND = ('shortest', 'fitted', 'always')
DEPLOY = ('shortest', 'fitted', 'direct')
SEEDS = (101, 211, 307)


def total_cost(runs):
    costs = Counter()
    checks = Counter()
    for r in runs:
        costs.update(r['cost']['components'])
        checks.update(r['cost']['checking'])
    won = sum(r['correct_return'] for r in runs)
    total = sum(costs.values())
    seconds = sum(r['wall_seconds'] for r in runs)
    return {'episodes': len(runs), 'returns': won, 'exhausted_without_return': len(runs)-won,
            'proposals': sum(r['proposals'] for r in runs), 'units': total,
            'units_per_correct_including_failures': total/won if won else None,
            'seconds_all': seconds, 'seconds_per_correct_including_failures': seconds/won if won else None,
            'cost_components': dict(costs), 'checker_actions': dict(checks),
            'certification_attempts': sum(len(r['requests']) for r in runs),
            'crossing_used_in_returns': sum(r['correct_return'] and r['returned']['macro_calls'] > 0 for r in runs),
            'failed_units': sum(r['cost']['work_units'] for r in runs if not r['correct_return'])}


def blind_summary(arms):
    output = {'episodes': len(arms), 'nonempty_bank': sum(bool(r['blind']['bank_count']) for r in arms),
              'oracle_available': sum(r['assessment']['n_exact_in_pool']>0 for r in arms)}
    for mode in BLIND:
        scores = [r['assessment']['scores'][mode] for r in arms]
        accuracy = [v['held_correct'] for v in scores if v['held_correct'] is not None]
        conditional = [v for v in scores if v['eligible_pairs']]
        output[mode] = {'exact': sum(v['exact'] for v in scores), 'held_correct_total': sum(accuracy),
                        'held_seen_if_a_program_returned': 9*len(accuracy),
                        'contrast_episodes': len(conditional),
                        'mean_pair_win_fraction_per_eligible_episode': mean(v['correct_pair_choices']/v['eligible_pairs'] for v in conditional) if conditional else None,
                        'pooled_pair_wins': sum(v['correct_pair_choices'] for v in conditional),
                        'pooled_eligible_pairs': sum(v['eligible_pairs'] for v in conditional)}
    tally = Counter()
    for arm in arms:
        v = arm['assessment']['scores']
        tally['both_exact' if v['shortest']['exact'] and v['fitted']['exact'] else
              'fitted_only' if v['fitted']['exact'] else 'shortest_only' if v['shortest']['exact'] else 'neither_exact'] += 1
    output['paired_blind_exact'] = dict(tally)
    return output


def summarize(path):
    raw = [json.loads(line) for line in path.read_text().splitlines() if line]
    if len(raw)!=30 or any(row['status']!='ok' for row in raw):
        raise ValueError('Expected thirty successful runner cases')
    rows = sorted((entry['result'] for entry in raw),key=lambda v:(v['task'],v['seed']))
    panel = audit_tasks()
    ids = [p['id'] for p in panel['tasks']]
    if {(v['task'],v['seed']) for v in rows} != {(t,s) for t in ids for s in SEEDS}:
        raise ValueError('A paired seed or task is missing')
    grouped = [(r['task'], r['seed'], lang, r['arms'][lang]) for r in rows for lang in LANGUAGES]
    bytask = {}
    example = None
    failures = []
    for entry in panel['tasks']:
        task = entry['id']
        given = [arm for t,_,_,arm in grouped if t==task]
        fit = given[0]['blind']['models']['fitted']
        if not all(arm['blind']['models']['fitted']==fit for arm in given):
            raise ValueError('The same training labels led to different rule fits')
        bytask[task] = {'definition':entry['definition'], 'true_group_size':entry['stabilizer_order'],
                        'fitted_renamings_with_identity':len(fit['accepted'])+1,
                        'correct_inferred_group':set(map(tuple,fit['accepted']))|{(0,1,2)}==set(map(tuple,entry['full_stabilizer'])),
                        'voted_cells':len(fit['margins']), **blind_summary(given)}
    for t,seed,lang,arm in grouped:
        blind=arm['blind']; sc=arm['assessment']['scores']
        if example is None and sc['fitted']['exact'] and not sc['shortest']['exact']:
            example={'id':t,'seed':seed,'language':lang,'shortest':blind['choices']['shortest'],
                     'fitted':blind['choices']['fitted'],'scores':{m:sc[m]['held_correct'] for m in BLIND}}
        for m in DEPLOY:
            outcome=arm['deployed'][m]
            if not outcome['correct_return']:
                failures.append([t,seed,lang,m])
    comparison={}
    acq=json.loads((path.parent/'acquisition.json').read_text())
    acq_units=acq['equivalent_literal_gates_over_nine_original_inputs']
    acq_sec=acq['median_forward_reacquisition_seconds']
    for mode in DEPLOY:
        comp={lang:total_cost([row['arms'][lang]['deployed'][mode] for row in rows]) for lang in LANGUAGES}
        matched=[row for row in rows if all(row['arms'][lang]['deployed'][mode]['correct_return'] for lang in LANGUAGES)]
        comp['same_successes']={lang:total_cost([r['arms'][lang]['deployed'][mode] for r in matched]) for lang in LANGUAGES}
        first,second=comp['raw'],comp['reuse']
        comp['matched_outcomes']={key:sum((bool(r['arms']['raw']['deployed'][mode]['correct_return']),bool(r['arms']['reuse']['deployed'][mode]['correct_return']))==bits for r in rows)
                                  for key,bits in [('both',(True,True)),('raw_only',(True,False)),('reuse_only',(False,True)),('neither',(False,False))]}
        comp['paired_reuse_cheaper_on_shared_successes']=sum(r['arms']['reuse']['deployed'][mode]['cost']['work_units']<r['arms']['raw']['deployed'][mode]['cost']['work_units'] for r in matched)
        comp['amortized_reuse_units_per_return_lower_bound']=(second['units']+acq_units)/second['returns'] if second['returns'] else None
        comp['amortized_reuse_seconds_per_return']=(second['seconds_all']+acq_sec)/second['returns'] if second['returns'] else None
        comparison[mode]=comp
    twin=panel['twin']
    pairs={(r['task'],r['seed']):r for r in rows}
    nident=0
    for s in SEEDS:
        for lang in LANGUAGES:
            left=pairs[twin['invariant_id'],s]['arms'][lang]['blind']
            right=pairs[twin['sensitive_id'],s]['arms'][lang]['blind']
            for k in ('bank_sha256','choices','training_observations','models','blind_commitment'):
                if left[k]!=right[k]:
                    raise ValueError(f'twin leak at {s}, {lang}, {k}')
            nident+=1
    return {'schema_version':1,'artifact_id':TICKET+'-E001','ticket':TICKET,'kind':'experiment','evidence_stage':'exploratory',
            'status':'Completed mixed-symmetry task panel and independently timed certified returns',
            'report':'research/'+TICKET+'/selection.md','contract':'experiments/'+TICKET+'/'+FAMILY+'/contract.json',
            'raw_sha256':sha256(path.read_bytes()).hexdigest(),'problem_controls':panel,
            'blind_overall':blind_summary([a for *_,a in grouped]),'blind_by_task':bytask,
            'blind_by_language':{l:blind_summary([a for _,_,lang,a in grouped if l==lang]) for l in LANGUAGES},
            'blind_by_group_order':{n:blind_summary([a for t,_,_,a in grouped if bytask[t]['true_group_size']==n]) for n in (1,2,3,6)},
            'twins_identical_banks_choices_and_votes':nident,'example':example,
            'certified_by_selector':comparison,'failed_cases':failures,'acquisition':acq,
            'per_task_certified':{t:{m:{l:total_cost([a['deployed'][m] for task,_,lang,a in grouped if (task,lang)==(t,l)]) for l in LANGUAGES} for m in DEPLOY} for t in ids},
            'per_seed_certified':{s:{m:{l:total_cost([a['deployed'][m] for _,seed,lang,a in grouped if (seed,lang)==(s,l)]) for l in LANGUAGES} for m in DEPLOY} for s in SEEDS}}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--raw',type=Path,default=BASE/'results.jsonl')
    p.add_argument('--out',type=Path)
    args=p.parse_args()
    d=summarize(args.raw)
    if args.out:
        args.out.write_text(json.dumps(d,indent=2)+'\n')
    else:
        print(json.dumps(d['blind_overall'],indent=2))
