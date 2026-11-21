"""Exhaust the necessary current and preceding role assignments for one named table."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction
from math import isqrt
from pathlib import Path
import json
from select_target import OUT, save
from role_options import analyze, selections, derive_old_bounds, parent_covers
from previous_cut import evaluate


def run(n,rates,weight,word_limit):
    unit,c,ternary,fates,options=analyze(n,rates)
    counts=Counter()
    samples=[]
    final_exclusions=[]
    roster=defaultdict(list)
    for ids in selections(options):
        counts['pairwise disjoint candidate packs']+=1
        bounds=derive_old_bounds(unit,c,ternary,options,ids,weight)
        if not bounds:
            counts['missing prior holder']+=1;continue
        placements=0
        for previous in parent_covers(bounds):
            placements+=1
            reason,d=evaluate(n,options,ids,previous)
            counts[reason]+=1
            if reason=='too few old shared slots for required witnesses':
                final_exclusions.append(dict(current=list(ids),earlier=previous))
            if reason!='viable':continue
            loose=tuple(sorted(x for k in ids for x in options[k]['fresh']))
            key=tuple((p,f) for p,f in d['roster'])
            info=dict(current=list(ids),loose=loose,old=previous,residual=d['residual'],
                      known_preceding_groups=d['previous_groups'],remaining_spent_witness_obligations=d['previous_witness_obligations'])
            roster[key].append(info)
            if len(samples)<word_limit:samples.append(info)
        if not placements:counts['inconsistent prior assignments']+=1
    return dict(weight=weight,width=n,den=unit,candidate_details=fates,possible_holders=options,
                scope='Necessary tests on all named positive-age NAE rivals. Surviving assignments could still be infeasible.',
                counts=dict(counts),final_witness_exclusions=final_exclusions,priced_rosters=[dict(profile=k,assignments=v) for k,v in roster.items()],samples=samples)

def main():
    parser = ArgumentParser()
    parser.add_argument('weight', choices=['uniform', 'inherited'])
    parser.add_argument('--rates', type=Path)
    args = parser.parse_args()
    table_path = args.rates or OUT / f'{args.weight}_rates.json'
    rates = list(map(Fraction, json.loads(table_path.read_text())))
    width = (1 + isqrt(1 + 8 * len(rates))) // 2
    if width * (width - 1) // 2 != len(rates):
        raise ValueError('Expected one exact fraction for each unordered named pair.')
    result = run(width, rates, args.weight, 4)
    save(OUT / f'role_branches_{args.weight}.json', result)
    print(len(result['possible_holders']), result['counts'], len(result['priced_rosters']))


if __name__ == '__main__':
    main()
