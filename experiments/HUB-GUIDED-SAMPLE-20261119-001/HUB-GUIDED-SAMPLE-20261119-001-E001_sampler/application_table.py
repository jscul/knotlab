"""Reconcile the fixed transfer samples with the exact birth corrections and available truths."""
from fractions import Fraction
from math import ceil,floor
from pathlib import Path
import argparse
import json


def read(path):
    return json.loads(path.read_text())


def fracstr(x):
    return [str(x.numerator),str(x.denominator)]


def mass(row):
    value=Fraction(*map(int,row['exact_initial_mass']))
    value*=Fraction(int(row['final_mass']),int(row['initial_rows']))
    den=int(row['resample_denominator'])
    for n in row['resample_numerators']:
        value*=Fraction(int(n),den)
    return value


def quantile(sorted_values,p):
    rank=p*(len(sorted_values)-1)
    i=floor(rank);j=ceil(rank)
    return sorted_values[i]+(rank-i)*(sorted_values[j]-sorted_values[i])


def numbers(values):
    vals=sorted(values)
    lo,hi=(quantile(vals,p) for p in [Fraction(1,40),Fraction(39,40)])
    return sum(vals,Fraction())/len(vals),lo,hi


def summarize(directory, obs):
    truth={1:read(directory/'pair_star01.json')['maximal_groups']-1400}
    value=read(directory/'near_block_02.json')['exact_count']['next_births']
    truth.update({s:value for s in [2,5,8]})
    truth.update({int(v['case'][-2:]):v['births'] for v in read(directory/'quotient_check.json')['targets']})
    targets=read(obs)['targets']
    corrections={q['stage']:q for q in read(directory/'pair_corrections.json')['targets']}
    report=[]
    for item in sorted(targets,key=lambda t:t['case']):
        if 'observations' not in item:continue
        i=int(item['case'][-2:]); age=item['age'];stage=f'start-{i:02}-age{age:02}'
        correction=corrections[stage]
        residual=None
        if i in (1,2,5,8):
            residual=0
        elif (path:=directory/f'literal_residual{i:02}.json').exists():
            residual=read(path)['residual_count']
        elif (path:=directory/f'cover_pairs{i:02}.json').exists():
            residual=read(path)['residual_pairs']
        values=[]
        for j,r in enumerate(item['observations']):
            assert int(r['seed'])==int(item['seed'])+j
            pair_reading=residual
            if residual is None:
                pair_reading=correction['easy_residual_pairs']+Fraction(correction['nontrivial_candidate_pairs']*correction['hits'][j],
                                                                       correction['samples_per_replicate'])
            values.append(mass(r)+correction['raw_maximum_to_birth_term']+pair_reading)
        assert len(values)==item['replicates_requested']==16
        ave,lo,hi=numbers(values)
        mid_offset=float(ave/truth[i]-1) if i in truth else None
        report.append(dict(case=item['case'],source_age=age,target_round=age+1,replicates=len(values),
                           reported_births=truth.get(i),exact_residual=residual,mean=float(ave),central95=[float(lo),float(hi)],
                           spread=float(hi/lo) if lo>0 else None,relative_mean_error=mid_offset,
                           exact_mean=fracstr(ave),individual_estimates=[fracstr(v) for v in values]))
    return report


def display(v):
    if v<1_000_000:return f'{v:,.0f}'
    return f'{v:.3g}'


def output(data):
    text='''# The other thirteen growing ends

Each row is a separate lawful history at its first unread round. The middle columns use one exact-weight prefix sampler, with 16 independent replicates of 128 particles per stage. Each run begins inside an exactly counted part formed from the largest block and up to fourteen outside neighborhood patterns in a second block. The mean uses every replicate. Spread is the empirical 97.5th percentile divided by the empirical 2.5th percentile, with linear interpolation. Each row gives equal weight to that stage’s replicates. No weighting across starts is implied.

| Start | Target round | Exact births | Sample mean | Observed error against exact | Empirical spread |
|---|---:|---:|---:|---:|---:|
'''
    for r in data:
        error='—' if r['relative_mean_error'] is None else f"{100*r['relative_mean_error']:+.1f}%"
        exact='open' if r['reported_births'] is None else f"{r['reported_births']:,}"
        spread='unresolved' if r['spread'] is None else f"{r['spread']:,.2f}×"
        text+=f"| {r['case']} | {r['target_round']} | {exact} | {display(r['mean'])} | {error} | {spread} |\n"
    return text+'''
Starts 02, 05 and 08 have isomorphic literal rosters and incoming parent sets. Their exact counts agree and the independent samples give three empirical checks on the same count. The pronounced spread on several other starts and the observed errors where totals are known limit the numerical reading of the open rows. The group-valued hub and disjoint branching methods were also applied to all thirteen, with separately recorded choice weights and run budgets. Conditional averages over completed capped runs have no claim to the unconditional expectation.

Start-14 was the largest input, with 162,336 live junctions. All sixteen original seeds finished. Its residual-pair correction uses 4,096 independent, uniformly drawn candidate pairs from outside the exact stratum, with zero hits. The exhaustive follow-up for this one correction was stopped when the requested precision and transfer runs completed. Using the full deterministic residual bracket puts the empirical spread between 437.9 million and 440.5 million. Every other target's residual-pair correction was exhausted. On starts 10 and 11, a different deterministic model counter also reproduced the exact raw counts. [Independent count on 10](../../artifacts/HUB-GUIDED-SAMPLE-20261119-001/HUB-GUIDED-SAMPLE-20261119-001-E001_sampler/exact_small10.json) · [Independent count on 11](../../artifacts/HUB-GUIDED-SAMPLE-20261119-001/HUB-GUIDED-SAMPLE-20261119-001-E001_sampler/exact_small11.json) · [Ganak's exact integer mode](https://github.com/meelgroup/ganak)

[Exact count on start-01](pair_star.md) · [Three dominant-block counts](near_block.md) · [Three exact smaller-roster counts](../../artifacts/HUB-GUIDED-SAMPLE-20261119-001/HUB-GUIDED-SAMPLE-20261119-001-E001_sampler/quotient_check.json) · [Transfer design and raw runs](prefix_targets.md) · [Group-valued sampling](hub.md) · [Independent branching totals](kernel.md)
'''


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('data',type=Path);p.add_argument('transfer',type=Path)
    p.add_argument('json',type=Path);p.add_argument('note',type=Path); args=p.parse_args()
    rows=summarize(args.data,args.transfer)
    assert len(rows)==13
    args.json.write_text(json.dumps(rows,indent=1)+'\n')
    args.note.write_text(output(rows))
