"""Match the two independent populations and price ledgers, then certify the registered endpoints."""
from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import gzip
import json

from catalog import OUT, Catalog, components_of, cuts, initial_read
from meeting_comparisons import check_local, deletions, ending_words, named_control
from survivors import describe, physical_ends, survivor_certificate


LAWS = ('parity','nae')
UNITS = ('types','labelled','distinct_mass','tree_mass')


def save_gzip(path,obj):
    with path.open('wb') as f, gzip.GzipFile(fileobj=f,mode='wb',filename='',mtime=0) as z:
        z.write((json.dumps(obj,sort_keys=True,separators=(',',':'))+'\n').encode())


def fraction(a,b):
    return str(Fraction(a,b)) if b else None


def match_physical(row, law):
    raw=row['laws'][law]
    fate,trace,sizes,unused=cuts(row['founder_rows'],law)
    assert fate==raw['termination'] and len(trace)==raw['age']
    observed=physical_ends(row['founder_rows'],raw)
    stages=[describe(end) for end in observed]
    assert [len(t['live_components']) for t in stages]==sizes
    for s,x in zip(stages,raw['end_by_age'],strict=True):
        assert tuple(map(tuple,x['effective_witness_subsets']))==s['witness_subsets']
        assert tuple(map(tuple,x['live_components']))==s['live_components']
        assert [(h,len(v)) for h,v in x['openings']]==s['loose_counts']
    for turn,cut in zip(trace,raw['cuts'],strict=True):
        compressed=Counter((len(p),f,d) for p,f,d in zip(turn.parents,turn.fresh,turn.demand,strict=True))
        physical=Counter((len(b['parents']),b['fresh'],b['following_demand']) for b in cut['births'])
        assert compressed==physical
    first_separate=next((t for t,count in enumerate(sizes) if count>1),None)
    assert first_separate==raw['first_separated_age']
    return fate,sizes


def four_rank(row):
    law=row['laws']['parity']
    w=len({x for r in row['founder_rows'] for x in r})
    return (law['final_holders'],law['final_width'],law['age'],law['terminal_arity'],w,
            sum(row['extra']),tuple(map(tuple,row['edges'])),tuple(row['extra']))


def legal_fixed_supply(typ):
    e=typ['edges']
    d=Counter(i for pair in e for i in pair)
    private=[max(0,3-d[i])+v for i,v in enumerate(typ['flags'])]
    return [edge for edge,orbit in deletions(e,typ['flags']) if all(d[i]+private[i]>=4 for i in edge)]


def run():
    catalog=Catalog()
    archive=OUT/'physical_population.json.gz'
    cases=json.load(gzip.open(archive,'rt'))
    assert len(cases)==len(catalog.types)
    evidence={}
    measure=defaultdict(Counter)
    coverage=Counter()
    per_shape=defaultdict(Counter)
    other_examples={}
    late={}
    local_arities=set()
    found={}
    for row in cases:
        key=catalog.classify(row['edges'],row['extra'])
        assert key not in evidence
        typ=catalog.types[key]
        assert row['labelled']==typ['labelled'] and row['aut']==typ['aut'] and row['tau']==typ['tau']
        assert row['mass_distinct']==typ['mass_distinct'] and row['mass_edited']==typ['mass_histories']
        assert all(row['eligible'][l] for l in LAWS)
        assert tuple(map(tuple,row['edges']))==typ['edges'] and tuple(row['extra'])==typ['flags']
        local_arities.update(map(len,row['founder_rows']))
        weights=(1,typ['labelled'],typ['mass_distinct'],typ['mass_histories'])
        f0=initial_read(6,typ['edges'],typ['flags'])
        evidence[key]={'weights':dict(zip(UNITS,weights,strict=True)),'laws':{}}
        for l in LAWS:
            raw=row['laws'][l]
            fate,c=match_physical(row,l)
            assert (fate=='stalled')==bool(f0['shortages'])
            if fate=='stalled':
                assert dict(raw['stall']['shortages'])==f0['shortages']
            else:
                got=Counter(tuple(b['parents']) for b in raw['cuts'][0]['births'])
                assert got==Counter(f0['funded_parents'])
            outcome='admitting_closure' if raw['positive'] else 'refusing_closure' if fate=='closed' else fate
            for u,weight in zip(UNITS,weights,strict=True):
                measure[(l,u)][outcome]+=weight
                if fate=='closed':
                    measure[(l,u,'closing_by_age_arity')][f"{raw['age']}/{raw['terminal_arity']}"]+=weight
                elif fate=='stalled':
                    measure[(l,u,'stall_by_attempted_age')][raw['stall']['attempted_age']]+=weight
                first=raw['first_separated_age']
                measure[(l,u,'first_multiple_live_groups')]['never_observed' if first is None else first]+=weight
                measure[(l,u,'live_group_transition')][f"{c[0]}/{c[-1]}/{fate}"]+=weight
            coverage[l+'_births']+=sum(len(z['births']) for z in raw['cuts'])
            coverage[l+'_cuts']+=len(raw['cuts'])
            evidence[key]['laws'][l]={'fate':fate,'first_multiple_groups':raw['first_separated_age'],'groups_through_stop':c}
        if row['laws']['parity']['termination']=='closed': found[key]=row
        if row['laws']['parity']['termination']=='open' and evidence[key]['laws']['parity']['groups_through_stop'][-1]==1:
            late[key]=row
        for feature,test in [('repeated_witness',any(len(p['witnesses'])>1 for p in f0['witnessed_pairs'])),
                             ('maximal_unheld_group',bool(f0['unheld_maximal_groups']))]:
            if test and not f0['shortages'] and feature not in other_examples:
                other_examples[feature]={'class':key,'first_cut':f0}
        per_shape[str(typ['edges'])][row['laws']['parity']['termination']]+=1

    assert set(evidence)==set(catalog.types)
    ranking=sorted(found,key=lambda k:four_rank(found[k]))
    ranks={label:next((k for k in ranking if label=='ordinary' or found[k]['laws']['parity']['positive']),None)
           for label in ('ordinary','odd_admitting')}
    numeric_ties={x:[k for k in ranking if (x=='ordinary' or found[k]['laws']['parity']['positive']) and
                  four_rank(found[k])[:6]==four_rank(found[target])[:6]] if target else [] for x,target in ranks.items()}
    primary_targets=set(k for k in ranks.values() if k is not None)
    if not primary_targets:
        primary_targets={min(late) if late else min(k for k,v in evidence.items() if v['laws']['parity']['fate']=='open')}
    comparisons={k:named_control(catalog.types[k]) for k in sorted(primary_targets)}
    # A descriptive lawful equal-supply deletion can still be available on an open
    # source, even if keeping the positive source's supplies violates minimum arity.
    extra_control=None
    if not any(legal_fixed_supply(catalog.types[k]) for k in primary_targets):
        target=sorted(primary_targets)[0]
        source=catalog.types[target]
        viable=[k for k in late if catalog.types[k]['edges']==source['edges'] and legal_fixed_supply(catalog.types[k])]
        if viable:
            selected=min(viable,key=lambda k:(sum(a!=b for a,b in zip(source['flags'],catalog.types[k]['flags'],strict=True)),k))
            extra_control={'class':selected,'comparison':named_control(catalog.types[selected])}
    signed={k:ending_words(c['founder']) for k,c in comparisons.items() if c['founder']['laws']['parity']['termination']=='closed'}
    for k in found:
        local_arities.add(found[k]['laws']['parity']['terminal_arity'])
    certs={law:{a:check_local(a,law) for a in sorted(local_arities)} for law in LAWS}
    controls={'four_cut_rank':ranks,'ties_on_numeric_rank':numeric_ties,'ranked_sources':comparisons,'physical_last_words':signed,
              'equal_private_supply_supplementary_control':extra_control,'ordinary_first_found_examples':other_examples}
    save_gzip(OUT/'matched_and_signed.json.gz',controls)
    (OUT/'local_knot_checks.json').write_text(json.dumps(certs,indent=2)+'\n')
    save_gzip(OUT/'all_funding_and_components.json.gz',evidence)

    # Direct physical certificate at an earlier *observed* cut. Never advance a new
    # founder beyond its fourth cut.
    third=None
    if ranks['ordinary']:
        v=found[ranks['ordinary']]
        third=physical_ends(v['founder_rows'],v['laws']['parity'])[-2]
    survivors={}
    for k,row in sorted(late.items()):
        survivors[k]=survivor_certificate(row,row['laws']['parity'],third)
        survivors[k]['multiplicities']=evidence[k]['weights']
        survivors[k]['nae_groups']=evidence[k]['laws']['nae']['groups_through_stop']
        if survivors[k]['fate']=='later_closure_implied_by_observed_end':
            survivors[k]['matched_four_step_class']=ranks['ordinary']
    nae_survivors={}
    for row in cases:
        k=catalog.classify(row['edges'],row['extra'])
        raw=row['laws']['nae']
        if raw['termination']=='open' and raw['live_groups_at_four']==1:
            nae_survivors[k]={'source_rows':row['founder_rows'],'ends':list(map(describe,physical_ends(row['founder_rows'],raw))),
                'paid_parents_and_fresh':[[[b['parents'],b['fresh']] for b in cut['births']] for cut in raw['cuts']],
                'fate':'every paid NAE birth receives at least one fresh name','multiplicities':evidence[k]['weights']}
    save_gzip(OUT/'connected_survivors.json.gz',{'parity':survivors,'nae':nae_survivors})
    details={}
    for l in LAWS:
        details[l]={}
        for u in UNITS:
            cells=measure[(l,u)]
            den=sum(cells.values())
            closed=cells['admitting_closure']+cells['refusing_closure']
            details[l][u]={'source_denominator':den,'eligible_mass':den,'unresolved_mass':0,'stalled':cells['stalled'],
               'open_after_four':cells['open'],'whole_closure':closed,'closure_probability':fraction(closed,den),
               'odd_admission_joint':cells['admitting_closure'] if l=='parity' else None,
               'odd_admission_joint_probability':fraction(cells['admitting_closure'],den) if l=='parity' else None,
               'odd_admission_given_closure':fraction(cells['admitting_closure'],closed) if l=='parity' else None,
               'closed_by_cut_and_terminal_arity':measure[(l,u,'closing_by_age_arity')],
               'stalled_by_attempted_cut':measure[(l,u,'stall_by_attempted_age')],
               'first_multiple_groups':measure[(l,u,'first_multiple_live_groups')],
               'initial_and_terminal_live_group_counts':measure[(l,u,'live_group_transition')]}
    output={'physical_population_sha256':sha256(archive.read_bytes()).hexdigest(),'labelled_catalog_sha256':sha256((OUT/'labelled_orbits.json').read_bytes()).hexdigest(),
            'numeric_funding':details,'type_count':len(catalog.types),'funded_cuts_and_births':coverage,'primary_minima':ranks,
            'survivor_verdict':{k:v['fate'] for k,v in survivors.items()},'per_meeting_pattern':per_shape}
    output['all_age_ordinary_by_proof']={}
    for u in UNITS:
        actual=details['parity'][u]['whole_closure']
        inferred=sum(s['multiplicities'][u] for s in survivors.values() if s['fate']=='later_closure_implied_by_observed_end')
        assert all(s['fate']!='later_fate_unresolved' for s in survivors.values())
        ordinary=actual+inferred
        den=details['parity'][u]['source_denominator']
        output['all_age_ordinary_by_proof'][u]={'primary_through_four':actual,'predicted_only_from_matching_ends':inferred,
            'total_ordinary_closure_mass':ordinary,'ordinary_probability':fraction(ordinary,den),
            'lower_all_age_odd_given_closure':fraction(actual,ordinary),'upper_all_age_odd_given_closure':'1',
            'signed_status':'All actually observed closures admitted. Later odd readings unmeasured.'}
    output['nae_connected_open_at_four']=sorted(nae_survivors)
    (OUT/'exact_results.json').write_text(json.dumps(output,indent=2)+'\n')
    print('registered ordinary:',ranks,'per-law primary',[(l,details[l]['types']['whole_closure']) for l in LAWS])
    print('surviving connected:',Counter(z['fate'] for z in survivors.values()))


if __name__=='__main__':
    run()
