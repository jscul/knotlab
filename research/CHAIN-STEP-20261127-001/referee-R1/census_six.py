"""Count starts with a complete witness at round six under equal census weighting."""
import argparse
from collections import Counter
from functools import lru_cache
import gzip
from itertools import chain
import json
from pathlib import Path
from random import Random
from time import perf_counter

from failure_rule import ChainTables, chain_names, counted, off_chain
from other_bonds_determination import Stage, carried_pairs
from other_bonds_paired import (BASE_SEED, SAMPLE_COUNT, Source, ThirdIndices, examine_pair,
                                state_matrix, witness_columns)
from recount import advance, load_census, ordered_chains, supports_of

HERE = Path(__file__).resolve().parent


@lru_cache(maxsize=2)
def third_indices(size_class):
    return ThirdIndices(size_class)


def inspect(supports, chains, index, tables):
    # Search stops at the first certificate. Every rejected candidate fails a
    # necessary test, except when explicitly flagged as unresolved.
    source = Source(supports)
    general = Stage(supports)
    columns = witness_columns(supports, source.model, SAMPLE_COUNT, BASE_SEED + index)
    states = state_matrix(columns,SAMPLE_COUNT)
    indices = third_indices(((source.n+15)//16)*16)
    attempts = Counter()
    try:
        for ids in chains:
            attempts['chains_tried'] += 1
            label = chain_names(supports,ids)
            signature = tuple(cond for cond,_ in off_chain(supports,ids,label))
            properties = counted(tables.results(signature))
            if not properties['step_with_defining_bond_check_and_all_eight_needed']:
                attempts['failed_defining_or_deletion_test'] += 1
                continue
            good = True
            for pair in carried_pairs(supports,ids):
                _, bad = examine_pair(source,pair,columns,states,SAMPLE_COUNT,indices)
                if bad:
                    attempts['determining_bond_with_named_pair'] += 1
                    good = False
                    break
                for both in (False, True):
                    r = general.reducer(pair,both)
                    if r['determining_three_touching_bonds']:
                        attempts['other_determining_bond'] += 1
                        good = False
                        break
                    if r['two_touching_groups_left_to_examine']:
                        attempts['unresolved_alternative_cover'] += 1
                        good = False
                        break
                if not good:
                    break
            if good:
                return ids, attempts
        return None, attempts
    finally:
        source.solver.delete()
        general.solver.delete()


def run(pilot):
    census=load_census()
    sample=sorted(Random(27183).sample(range(len(census)),64)) if pilot else range(len(census))
    stem='census_six_pilot' if pilot else 'census_six'
    totals=Counter()
    unresolved=[]
    tables=ChainTables()
    begin=perf_counter()
    with gzip.open(HERE/(stem+'.jsonl.gz'),'wt') as output:
        for i in sample:
            totals['starts']+=1
            s=supports_of(census[i])
            for r in range(6):
                grown=advance(s)
                if grown.status!='funded':
                    break
                s=grown.supports
            else:
                totals['grew_through_six']+=1
                choices=ordered_chains(s)
                first=next(choices,None)
                if first is None:
                    continue
                totals['chain_positive']+=1
                cert,counts=inspect(s,chain([first],choices),i,tables)
                totals.update(counts)
                totals['certified_starts']+=cert is not None
                if cert is None and counts['unresolved_alternative_cover']:
                    unresolved.append(i)
                output.write(json.dumps({'census_entry':i,'witness_knot_ids':cert,'counts':counts})+'\n')
    out={'round':6,'unit':'one equal vote per census start, conditioning on growth as indicated',
         'test':'One chain needed, all eight laws individually needed in all three roles; each upper function varies at every eligible stage bond.',
         'totals':totals,'unresolved_starts':unresolved,'seconds':round(perf_counter()-begin,3)}
    (HERE/(stem+'.json')).write_text(json.dumps(out,indent=2)+'\n')
    print(out)

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--pilot',action='store_true')
    run(p.parse_args().pilot)
