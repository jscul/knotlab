"""Read the frozen study's receipts and compare cumulative wall costs at every prefix."""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
from itertools import accumulate
import json
from pathlib import Path
import statistics
import struct

NOTES = Path(__file__).resolve().parent
ROOT = NOTES.parents[1]
TICKET = NOTES.name
OUT = ROOT/'artifacts'/TICKET/(TICKET+'-E001_gated_stream')
PREVIOUS = ROOT/'artifacts/FOLD-REUSE-20261115-001/FOLD-REUSE-20261115-001-E001_second_learner'
N = 32768
from stream import ROW_ORDER, grading_rows, split_summary


def get(path):
    return json.loads(path.read_bytes())


def trace(arm):
    with gzip.open(OUT/f'trace-{arm}.jsonl.gz','rt') as reader:
        keys = json.loads(next(reader))
        for line in reader:
            yield dict(zip(keys, json.loads(line), strict=True))


def crossings(difference):
    positive_prefix = difference[1:]
    first = next((k for k, value in enumerate(positive_prefix,1) if value <= 0), None)
    last_loss = next((k for k in range(len(difference)-1,0,-1) if difference[k] > 0),0)
    reversals = [k for k in range(2,len(difference)) if difference[k-1] <= 0 < difference[k]]
    closest = min(range(1,len(difference)),key=difference.__getitem__)
    return {'first_break_even':first,'sustained_from':last_loss+1 if last_loss < len(positive_prefix) else None,
            'reversals':reversals,'closest_prefix':closest,'lowest_gap_ns':difference[closest],
            'end_gap_ns':difference[-1]}


def summarize():
    rows = [json.loads(line) for line in (OUT/'results.jsonl').read_text().splitlines()]
    if len(rows) != 12 or any(r['status'] != 'ok' for r in rows):
        raise ValueError('incomplete method streams')
    freeze = get(OUT/'gate-freeze.json')
    source = round(get(PREVIOUS/'source_cost.json')['original_acquisition_wall_s']*1e9)
    acquisition = {'gated-warm':source+freeze['paid_training_wall_ns'],
                   'gated-cold':source+freeze['paid_training_wall_ns'],'always':source}
    summaries, curves = {}, {}
    for runner in rows:
        trial = runner['result']
        arm, rep = trial['arm'],trial['repeat']
        timing = (OUT/trial['times']).read_bytes()
        if len(timing) != N*16 or hashlib.sha256(timing).hexdigest()!=trial['times_sha256']:
            raise ValueError(f'invalid timing rows for {arm}/{rep}')
        wall, cpu = zip(*struct.iter_unpack('<QQ',timing))
        setup_ns = trial['setup_wall_ns']
        curve = list(accumulate(wall, initial=acquisition.get(arm,0)+setup_ns))
        curves.setdefault(arm,{})[rep]=curve
        entry = summaries.setdefault(arm,{'upfront_ns':acquisition.get(arm,0),'runs':[],'trace_hash':trial['trace_hash'],
                                          'stats':trial['stats']})
        if trial['trace_hash'] != entry['trace_hash'] or trial['stats'] != entry['stats']:
            raise ValueError('choices or certificates changed between timing repeats')
        new,old = (trial[key]['counters'] for key in ('growth_after','growth_before'))
        entry['runs'].append(dict(repeat=rep, setup_ns=setup_ns, total_ns=curve[-1],
                                  downstream_ns=curve[-1]-acquisition.get(arm,0), cpu_ns=trial['setup_cpu_ns']+sum(cpu),
                                  physical_builds=new['physical_programs_compiled']-old['physical_programs_compiled'],
                                  physical_hits=new['materialization_cache_hits']-old['materialization_cache_hits'],
                                  physical_packed_NANDs=new['validation_packed_NANDs']-old['validation_packed_NANDs']))
    for arm, entry in summaries.items():
        runs = entry['runs']
        entry['median_total_ns']=statistics.median([r['total_ns'] for r in runs])
        entry['median_downstream_ns']=entry['median_total_ns']-entry['upfront_ns']
    mid = {arm:[statistics.median(xs) for xs in zip(*[reps[r] for r in sorted(reps)],strict=True)]
           for arm,reps in curves.items()}
    differences = {arm:[x-y for x,y in zip(mid[arm],mid['median'])] for arm in ('gated-warm','gated-cold')}
    for arm, dif in differences.items():
        case = summaries[arm]
        case['comparison']=crossings(dif)
        case['paired_repeats']=[crossings([x-y for x,y in zip(curves[arm][r],curves['median'][r])]) for r in range(3)]
    with gzip.open(OUT/'training.json.gz') as reader:
        costs = json.load(reader)['cpu_ns']
    fit = [(statistics.median(x),statistics.median(y)) for x,y in costs[64:]]
    training = {'paid_training_ns':freeze['paid_training_wall_ns'], 'source_ns':source,'first_pair_ns':freeze['first_training_pair_wall_ns'],
                'fitting_rules':len(fit),'fold_cheaper_rules':sum(y<x for x,y in fit),
                'hindsight_possible_saving_ns':sum(max(x-y,0) for x,y in fit),
                'checkpoint':get(OUT/'gate.json')}
    conditions = Counter()
    prefix_cases = defaultdict(dict)
    prefix_sizes = Counter()
    for i,(base, probe, gated, test) in enumerate(zip(trace('median'),trace('always'),trace('gated-warm'),grading_rows('held'),strict=True)):
        target = test['truth']
        for k in ('prefix_labels','teacher_mismatch_mask','teacher_rows'):
            if len({row[k] for row in (base,probe,gated)}) != 1:
                raise AssertionError('teacher feedback differs')
        if any(row['proposal_truths'][-1] != target for row in (base,probe,gated)):
            raise AssertionError('incorrect terminal submission')
        base_first, probe_first = base['proposal_truths'][0],probe['proposal_truths'][0]
        signature = base['prefix_labels']
        prefix_sizes[signature] += 1
        if base_first != probe_first:
            if base_first == target:
                prefix_cases[signature]['median'] = (i + 1, target)
            if probe_first == target:
                prefix_cases[signature]['fold'] = (i + 1, target)
        conditions['tasks'] += 1
        conditions['same_first_truth'] += base_first == probe_first
        conditions['both_first_exact'] += base_first == probe_first == target
        conditions['fold_only_first_exact'] += base_first != target and probe_first == target
        conditions['median_only_first_exact'] += base_first == target and probe_first != target
        conditions['different_from_default_gate_trajectory'] += base['proposal_truths'] != gated['proposal_truths']
        conditions['fold_possible'] += test['foldable']
        conditions['fewer_checks_with_unconditional_fold'] += probe['verifier_calls'] < base['verifier_calls']
        conditions['more_checks_with_unconditional_fold'] += probe['verifier_calls'] > base['verifier_calls']
    ambiguous = [(key, group) for key, group in prefix_cases.items() if len(group) == 2]
    witness = None
    if ambiguous:
        key, group = min(ambiguous, key=lambda item: max(row[0] for row in item[1].values()))
        plain, probe = group['median'], group['fold']
        distinguish = next(x for x in ROW_ORDER if ((plain[1] ^ probe[1]) >> x) & 1)
        witness = {'prefix_in_order':[(x, (key >> pos) & 1) for pos,x in enumerate(ROW_ORDER[:8])],
                   'median_first_exact_rule':plain[0], 'fold_first_exact_rule':probe[0],
                   'first_public_row_separating_them':distinguish, 'answer_median_rule':(plain[1] >> distinguish) & 1,
                   'answer_fold_rule':(probe[1] >> distinguish) & 1}
    prefix_ambiguity = {'observed_prefixes':len(prefix_sizes),'opposite_first_winners_prefixes':len(ambiguous),
                        'example':witness,'use':'post-evaluation diagnostic, no change to the frozen gate'}
    result={'study':TICKET,'training':training,'train_split':split_summary('train'),'held_split':split_summary('held'),
            'arms':summaries,'paired_choices':dict(conditions), 'prefix_ambiguity':prefix_ambiguity,'correct_rule_input_pairs_per_arm':N*64}
    return result, differences


def plot(differences):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter
    fig, ax = plt.subplots(figsize=(7.4,3.35),layout='constrained')
    colors={'gated-warm':'#006566','gated-cold':'#81513f'}
    for arm, label in [('gated-warm','Kept training cache'),('gated-cold','Started with empty cache')]:
        ax.plot([v/1e9 for v in differences[arm]],color=colors[arm],lw=1.8,label=label)
    ax.axhline(0,color='#323a39',lw=0.9)
    ax.set(xlim=(0,N),xlabel='Fresh rules completed',ylabel='Additional total time (seconds)')
    ax.set_ylim(bottom=min(-1.2,min(min(items) for items in differences.values())/1e9-0.5))
    ax.set_xticks([0,8192,16384,24576,32768])
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, pos:f'{x:,.0f}'))
    ax.spines[['top','right']].set_visible(False)
    ax.grid(axis='y',alpha=.18)
    ax.legend(loc='center left',frameon=False)
    ax.set_title('Cost above ordinary median search',loc='left',weight='bold')
    fig.savefig(OUT/'cumulative-cost.png',dpi=165)
    plt.close(fig)


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plot',action='store_true')
    args=p.parse_args()
    result, differences = summarize()
    (OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    if args.plot:
        plot(differences)
    print(json.dumps({'primary':result['arms']['gated-warm']['comparison'],
                      'endpoints':{k:v['median_total_ns'] for k,v in result['arms'].items()},
                      'paired_choices':result['paired_choices']},indent=2))
