"""Bind the unique surviving cover, full word support and admissible history."""
from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from complete_older import forced_old_cover,histories
from role_options import signed_table,mono_triple
from select_target import OUT,read,save,advance


def genuine_source(rows,n):
    masks=[sum(1<<x for x in H) for H in rows]
    state_sets=[{w for w in range(1<<n) if all((w&k) not in (0,k) for j,k in enumerate(masks) if j!=i)} for i in range(len(rows))]
    state=set.intersection(*state_sets)
    assert state
    all_projections=[]
    for H in rows:
        projection={tuple(w>>j&1 for j in H) for w in state}
        assert len(projection)==2**len(H)-2
        all_projections.append(len(projection))
    assert all(s>state for s in state_sets)
    return state,all_projections,[len(sub-state) for sub in state_sets]


def run():
    selection=read(OUT/'selection.json')
    n=selection['reached_name_count']
    runs={}
    for weight in ('uniform','inherited'):
        branches=read(OUT/('role_branches_'+weight+'.json'))
        options=branches['possible_holders']
        rate=list(map(Fraction,read(OUT/(weight+'_rates.json'))))
        total,c=signed_table(n,rate)
        triples={frozenset(T) for T in combinations(range(n),3) if mono_triple(total,c,T)==0}
        one,=branches['priced_rosters']
        assignment,=one['assignments']
        chosen=assignment['current']
        old=assignment['old']
        details=dict(residual=assignment['residual'],previous_groups=assignment['known_preceding_groups'],previous_witness_obligations=assignment['remaining_spent_witness_obligations'])
        extras=list(forced_old_cover(n,options,chosen,old,details,triples))
        assert extras==[((6,7,8),)]
        all_rows=tuple(map(tuple,old))+extras[0]+tuple(tuple(options[j]['support']) for j in chosen)
        all_histories=histories(all_rows)
        assert len(all_histories)==1
        chain,=all_histories
        assert len(chain)==2
        source,current=chain
        assert set(current)==set(map(tuple,selection['physical_stage']))
        state,projections,erosions=genuine_source(source,9)
        _,after,births=advance(source,'nae')
        assert set(after)==set(current)
        price=Counter((int((w&1)==((w>>1)&1)),(15 if (w&1)==((w>>1)&1) else 16)*(15**4)) for w in state)
        assert sum(k[1]*s for k,s in price.items())==selection['uniform_word_count']
        physical_profile=sorted((sorted(tuple(row) for row in p),q) for p,q in selection['reference_named_roster'])
        assert physical_profile==sorted((sorted(tuple(row) for row in p),q) for p,q in one['profile'])
        runs[weight]=dict(observed_loose=assignment['loose'],current_holders=all_rows,
            completed_remaining_spent=extras[0],permitted_history_count=len(all_histories),
            only_original_rows=source,source_words=len(state),full_source_projections=projections,extra_words_on_source_erasure=erosions,
            classes_by_equal_inputs_extension_count={str(k):v for k,v in sorted(price.items())},positive_age_legal=True)
    save(OUT/'full_completion.json',runs)
    print({k:(len(v['observed_loose']),v['source_words'],v['permitted_history_count']) for k,v in runs.items()})
if __name__=='__main__':run()
