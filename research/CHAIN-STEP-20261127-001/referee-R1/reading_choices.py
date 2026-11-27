"""Test the freedom to enlarge the two-place carrier on a fixed grown chain."""
import argparse
import gzip
import json
from pathlib import Path
from time import perf_counter

from other_bonds_determination import Stage as DeterminationStage
from other_bonds_paired import (BASE_SEED, SAMPLE_COUNT, Source, ThirdIndices, examine_pair,
                                state_matrix, witness_columns)
from stage_readings import (DEFINING, EXPECTED_UPPER, determines_an_upper, locality_of_triple,
                            mapped_carriers, projection, stage_solver, upper_images)

HERE = Path(__file__).resolve().parent


def run(row, limit):
    supports = row['supports']
    chain = row['checked_chains'][0]
    fixed = mapped_carriers(supports,chain)
    shorter = fixed[-1]
    extras = sorted({d for k in supports for d in k} - {d for c in fixed for d in c})
    assert len(shorter) == 2
    accepted = []
    semantic_classes = []
    all_bond_passes = []
    unresolved = []
    source = Source(supports)
    general = DeterminationStage(supports)
    cols = witness_columns(supports,source.model,SAMPLE_COUNT,BASE_SEED)
    states = state_matrix(cols,SAMPLE_COUNT)
    indices = ThirdIndices(source.n)
    pair_cache = {}

    def all_bond_verdict(pair):
        pair = tuple(sorted(pair))
        if pair not in pair_cache:
            _, bad = examine_pair(source,pair,cols,states,SAMPLE_COUNT,indices)
            if bad:
                verdict = 'read at a bond'
            else:
                cases = [general.reducer(pair,b) for b in (False,True)]
                if any(c['determining_three_touching_bonds'] for c in cases):
                    verdict = 'read at a bond'
                elif any(c['two_touching_groups_left_to_examine'] for c in cases):
                    verdict = 'unresolved'
                else:
                    verdict = 'varies at every bond'
            pair_cache[pair] = verdict
        return pair_cache[pair]
    with stage_solver(supports) as stage:
        orig = stage.agreement(shorter)
        for d in extras[:limit]:
            cs = fixed[:-1] + (tuple(sorted((*shorter,d))),)
            readings = tuple(map(stage.agreement,cs))
            witnesses = stage.observed(readings)
            if not all(projection(witnesses,t) == EXPECTED_UPPER for t in DEFINING):
                continue
            if any(im != EXPECTED_UPPER for im in upper_images(witnesses)):
                continue
            if stage.read_at_any_knot(readings,witnesses)['determining_knot_and_reading']:
                continue
            if any(determines_an_upper(locality_of_triple(witnesses,t)) for t in DEFINING):
                continue
            all_upper = stage.upper_111(readings)
            if not all(stage.solve([u],omit={law}) for u in all_upper for law in chain):
                continue
            long_reading = readings[-1]
            assert stage.solve([orig,-long_reading])
            accepted.append(d)
            verdicts = [all_bond_verdict(cs[2*i:2*i+2]) for i in range(3)]
            if all(v == 'varies at every bond' for v in verdicts):
                all_bond_passes.append(d)
            elif 'unresolved' in verdicts and 'read at a bond' not in verdicts:
                unresolved.append(d)
            for group in semantic_classes:
                _, rep = group[0]
                if not stage.solve([rep,-long_reading]) and not stage.solve([-rep,long_reading]):
                    group.append((d,long_reading))
                    break
            else:
                semantic_classes.append([(d,long_reading)])
    source.solver.delete()
    general.solver.delete()
    return {'all_stage_bond_passing_additions':all_bond_passes,'all_stage_bond_unresolved':unresolved,
            'census_entry':row['start'],'round':row['round'],'chain_knot_indices':chain,'canonical_carriers':fixed,
            'outside_distinctions':len(extras),'tried':len(extras[:limit]),
            'passing_additions':accepted,'different_extended_readings':len(semantic_classes),
            'equal_reading_classes':[[d for d,_ in g] for g in semantic_classes],
            'gate':'Whole-stage lower and upper images, locality at every source knot and each defining bond, every chain law needed. Each changed reading differs from the original on a stage state.'}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--pilot',action='store_true')
    args=p.parse_args()
    begin=perf_counter()
    with gzip.open(HERE/'stages.jsonl.gz','rt') as f:
        rows=[r for line in f if (r:=json.loads(line))['checked_chains'] and r['round']==2]
    results=[run(row,1 if args.pilot else None) for row in (rows[:1] if args.pilot else rows)]
    out={'selection':'first checked chain on each positive round-two stage','rows':results,'seconds':perf_counter()-begin}
    (HERE/('choices_pilot.json' if args.pilot else 'choices.json')).write_text(json.dumps(out,indent=2)+'\n')
    print([(r['census_entry'],r['tried'],r['different_extended_readings']) for r in results],out['seconds'])
