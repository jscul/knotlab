"""Recompute exact weights and test every generating observational symmetry."""
from fractions import Fraction
from itertools import combinations
import json
import sys
from select_target import OUT, PREV, ROOT, OLD, save

sys.path.insert(0,str(ROOT/'experiments'/OLD/PREV.name))
from explosive_rates import nae_rates
from explosive_symmetry import table_moves,profile_move,inverse
from census_weighted import canonical_weighted

def target():
    d=json.loads((OUT/'selection.json').read_text())
    rows=d['physical_stage'];n=d['reached_name_count']
    stage=dict(rows=rows,width=n,limits=d['holder_cut_limits'])
    profile=d['reference_named_roster']
    loose=d['actual_loose']
    out={}
    sheet={}
    for name in ('uniform','inherited'):
        total,counts=nae_rates(stage,name)
        rates=[Fraction(counts[p],total) for p in combinations(range(n),2)]
        if name=='uniform':
            assert rates==[Fraction(k,d['uniform_word_count']) for k in d['uniform_disagreements']]
        tab=canonical_weighted(n,total,counts)
        generators,order=table_moves(tab.key)
        assert order==tab.automorphisms
        base=profile_move(profile,inverse(tab.order))
        available={inverse(tab.order)[x] for x in loose}
        sheet[name]=rates
        out[name]=dict(canonical_group_order=order,generators=len(generators),
            group_fixes_priced_roster=all(profile_move(base,g)==base for g in generators),
            group_fixes_loose_roles=all({g[x] for x in available}==available for g in generators),
            word_mass_scale=total,distinct_rates=len(set(rates)))
        save(OUT/(name+'_rates.json'),list(map(str,rates)))
    out['entries_changing_under_weight']=sum(x!=y for x,y in zip(*sheet.values(),strict=True))
    out['max_weight_difference']=str(max(abs(x-y) for x,y in zip(*sheet.values(),strict=True)))
    save(OUT/'target_symmetries.json',out)
    print(out)
if __name__=='__main__':target()
