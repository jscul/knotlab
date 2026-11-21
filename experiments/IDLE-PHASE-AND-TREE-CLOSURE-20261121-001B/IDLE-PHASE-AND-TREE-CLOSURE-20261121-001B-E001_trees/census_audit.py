"""Join the counted Prüfer domain to all full physical trajectories without sampling."""

from argparse import ArgumentParser
from collections import Counter, defaultdict, deque
from fractions import Fraction
import gzip
import json
import os
import subprocess
import sys

from multiplicities import OUTPUT, ROOT, adjacency, colored_code, save
from literal_inputs import OLDER, local_data, physical
from end_operator import from_stars, step


def read(name):
    p=OUTPUT/name
    with (gzip.open(p,'rt') if p.suffix=='.gz' else p.open()) as f:
        return json.load(f)


def signature(law):
    history=[]
    for cut in law['cuts']:
        births=[(b['parents'],b['fresh']) for b in cut['births']]
        history.append([cut['after_holders'],cut['after_names'],local_data(births)])
    return {'termination':law['termination'],'age':law['age'],'arity':law['terminal_arity'],
            'positive':law['positive'],'history':history}


def check_end(case, law):
    expected=case['laws'][law]
    rows=case['founder_rows']
    end=from_stars(rows)
    name_count=len({x for row in rows for x in row})
    holder_count=len(rows)
    external=dict(enumerate(range(holder_count)))
    for age,c in enumerate(expected['cuts'],1):
        result=step(end,law)
        assert result.status=='extend' and age==c['age']
        assert (holder_count,name_count)==(c['before_holders'],c['before_names'])
        on_file=defaultdict(deque)
        for b in c['births']:
            key=(tuple(sorted(b['parents'])),b['fresh'],b['following_demand'])
            on_file[key].append(b['holder'])
        next_mapping={}
        for local,(parents,fresh,demand) in enumerate(zip(result.parents,result.fresh,result.demand,strict=True)):
            key=(tuple(sorted(external[v] for v in parents)),fresh,demand)
            assert on_file[key]
            next_mapping[local]=on_file[key].popleft()
        assert all(not values for values in on_file.values())
        holder_count+=len(result.parents)
        name_count+=sum(result.fresh)
        assert (holder_count,name_count)==(c['after_holders'],c['after_names'])
        assert (not result.end.opens)==c['whole_closed']
        external,end=next_mapping,result.end
    if expected['termination']=='stalled':
        result=step(end,law)
        assert result.status=='stall' and expected['age']==0
        return tuple(sorted((external[v],amount) for v,amount in result.shortages))
    if expected['termination']=='closed':
        assert not end.opens and expected['age']<=4
    else:
        assert end.opens and expected['age']==4
    return ()


def opening_shortages(case):
    """At a tree founder, the unique middle of a distance-two pair counts its demand exactly once."""
    n=case['n']; g=adjacency(n,case['edges']); flag=case['extra']
    private=[max(0,3-len(neighbors))+v for neighbors,v in zip(g,flag,strict=True)]
    live={h for h,quantity in enumerate(private) if quantity}
    watched=[sum(j in live for j in neighbors) for neighbors in g]
    needed={h:sum(watched[w]-1 for w in g[h]) for h in live}
    return tuple(sorted((h,needed[h]-private[h]) for h in live if needed[h]>private[h]))


def candidate_star(case):
    n=case['n']
    g=adjacency(n,case['edges'])
    centers=[i for i,nb in enumerate(g) if len(nb)==n-1]
    if len(centers)!=1:
        return None
    center=centers[0]; flags=case['extra']
    if flags[center] or n>5:
        return None
    return n-1,sum(flags)


def formula(n,q):
    if n==4:
        return (1-q)*(1-q**3)/4,3*q*q*(1-q)**2/4
    if n==5:
        return (1-q)*q**4/25,(1-q)*q**4/25
    return Fraction(0),Fraction(0)


def status_key(s):
    if s['termination']=='closed':
        return f"cut_{s['age']}_arity_{s['arity']}_odd_{'yes' if s['positive'] else 'no'}"
    return s['termination']


def fraction_record(value):
    if value is None:
        return None
    return [value.numerator,value.denominator]


def ratio(a,b):
    return a/b if b else None


def local_rule_check(arity,law,odd=False):
    allowed=[w for w in range(1<<arity) if (w.bit_count()%2==int(odd) if law=='parity' else 0<w<(1<<arity)-1)]
    names=[f'x{j}' for j in range(arity)]
    clauses=[' '.join(('-' if w>>j&1 else '')+name for j,name in enumerate(names))
             for w in range(1<<arity) if w not in allowed]
    command=[sys.executable,'-B','-m','knotlab','check','--cnf',';'.join(clauses),'--loops',*names[:-1],'--contact',names[-1],'--json']
    result=json.loads(subprocess.check_output(command,cwd=ROOT,env={**os.environ,'PYTHONPATH':str(ROOT/'tools')}))
    assert len(result['allowed'])==len(allowed)
    assert all(result[k] for k in ('binding','coexistence','loss_on_erasure','invisible_in_parts'))
    return {'arity':arity,'law':law,'single_odd':odd,'allowed_words':len(allowed),'K1_K2_K3':[True,True,True]}


def summarize(counts):
    n=counts['n']; data=counts['outcomes']; source_count=n**(n-2)
    out={}
    force_q=tuple(map(Fraction,('0','1/4','1/2','1')))
    for q in force_q:
        by_law={}
        for law, cells in data.items():
            masses=Counter()
            for cat, by_k in cells.items():
                masses[cat]=sum(int(v)*q**int(k)*(1-q)**(n-int(k))/source_count for k,v in by_k.items())
            assert sum(masses.values())==1
            closure=sum((v for k,v in masses.items() if k.startswith('cut_')),Fraction())
            positive=sum((v for k,v in masses.items() if k.endswith('_yes')),Fraction())
            if law=='parity':
                assert (closure,positive)==formula(n,q)
            else:
                assert closure==positive==0
            by_law[law]={'closing_probability':fraction_record(closure),'admitting_closure_probability':fraction_record(positive) if law=='parity' else None,
                          'conditional_admission':fraction_record(ratio(positive,closure)) if law=='parity' else None,
                          'stall':fraction_record(masses.get('stalled',Fraction())),'open':fraction_record(masses.get('open',Fraction())),
                          'by_age_arity_verdict':{k:fraction_record(v) for k,v in masses.items()}}
        out[str(q)]=by_law
    return out


def audit(sizes,use_full):
    all_reps=read('representatives.json.gz') if use_full else read(f'representatives_n{sizes[0]}.json.gz')
    reps=defaultdict(list)
    for c in all_reps:
        reps[c['n']].append(c)
    sample=read('archived_tree_replay.json.gz')['founders']
    whole={}
    for n in sizes:
        multiplicities=read(f'multiplicities_{n}.json.gz')
        expected={code:entry for tree in multiplicities['shapes'].values() for code,entry in tree['decorated'].items()}
        raw=read(f'literal_inputs_{n}.json.gz') if n<=5 else None
        counted=defaultdict(lambda:defaultdict(Counter))
        per_size=Counter()
        coverage=Counter()
        samples=[s for s in sample if s['n']==n]
        observed={}; named_stars=[]; cut_masses=defaultdict(Counter)
        for r in reps[n]:
            graph=adjacency(n,r['edges'])
            code,aut=colored_code(graph,r['extra'])
            assert code not in observed
            oracle=expected[code]; extra=sum(r['extra'])
            assert (aut,r['aut'],r['labelled'],r['mass'])==(oracle['symmetry'],aut,oracle['labelled'],oracle['quarter_mass_numerator'])
            if raw:
                assert raw['labelled_multiplicity'][code]==r['labelled']
            outcomes={law:signature(record) for law,record in r['laws'].items()}
            observed[code]=outcomes
            if raw:
                assert outcomes==raw['class_histories'][code]
            shortages=opening_shortages(r)
            cap=False
            for law,s in outcomes.items():
                assert check_end(r,law)==shortages
                assert bool(shortages)==(s['termination']=='stalled')
                key=status_key(s)
                counted[law][key][extra]+=r['labelled']
                per_size[law+'_'+key]+=r['mass']
                for age,cut in enumerate(r['laws'][law]['cuts'],1):
                    cut_masses[law][f'funded_age_{age}']+=r['mass']
                    cut_masses[law][f'births_age_{age}']+=r['mass']*len(cut['births'])
                cap |= bool(r['laws'][law]['would_cross_b251'])
                coverage[law+'_class_'+s['termination']]+=1
                if s['termination']=='closed':
                    star=candidate_star(r)
                    assert star
                    assert ((star[0]==3 and star[1]<=2) or star==(4,4)) and s['positive']==(star in ((3,2),(4,4)))
                    assert s['arity']>=3
            coverage['caps_either_law']+=cap
            if candidate_star(r):
                named_stars.append({'id':r['id'],'leaf_count_and_extras':candidate_star(r),
                                    'labelled':r['labelled'],'quarter_mass':r['mass'],'outcomes':outcomes})
        assert set(observed)==set(expected)
        assert sorted(r['id'] for r in reps[n])==sorted(set(r['id'] for r in reps[n]))
        for s in samples:
            assert s['laws']==observed[s['decoration_code']]
        # A second physical experiment with holder order and name order reversed at each size.
        # Check every closed representative, plus the first stalled and the first open one at that size when present.
        chosen={}
        for r in reps[n]:
            tag=r['laws']['parity']['termination']
            chosen.setdefault((tag,r['id'] if tag=='closed' else 0),r)
        renamings=[]
        for r in chosen.values():
            rows=r['founder_rows']
            width=len({name for row in rows for name in row})
            mapped=tuple(tuple(sorted(width-1-x for x in row)) for row in reversed(rows))
            assert {law:physical(mapped,law) for law in ('parity','nae')}=={law:signature(x) for law,x in r['laws'].items()}
            renamings.append(r['id'])
        for law in ('parity','nae'):
            assert sum(v for k,v in per_size.items() if k.startswith(law+'_'))==multiplicities['quarter_denominator']
        counts={'n':n,'decorated_classes':len(observed),'distinct_labelled_mask_pairs':multiplicities['labelled_trees_and_binary_masks'],
                'labelled_trees':multiplicities['distinct_labelled_prufer_words'],'quarter_denominator':multiplicities['quarter_denominator'],
                'outcomes':counted,'quarter_mass_by_law_and_outcome':per_size,'quarter_mass_cut_and_birth_totals':cut_masses,
                'class_outcomes':coverage,'relabelled_physical_case_ids':renamings,'matched_archive_draws':len(samples),
                'raw_all_labelled_inputs_replayed_at_both_laws':raw['raw_labelled_inputs'] if raw else None,'candidate_stars':named_stars}
        counts['probabilities_by_extra_weight']=summarize(counts)
        whole[n]=counts
    summary={}
    if list(sizes)==list(range(4,9)):
        for q in next(iter(whole.values()))['probabilities_by_extra_weight']:
            summary[q]={}
            for law in ['parity','nae']:
                keys=['closing_probability','stall','open']
                if law=='parity':
                    keys+=['admitting_closure_probability']
                qdata={}
                for k in keys:
                    value=sum(Fraction(*counts['probabilities_by_extra_weight'][q][law][k]) for counts in whole.values())/len(sizes)
                    qdata[k]=value
                qdata['conditional_admission']=ratio(qdata['admitting_closure_probability'],qdata['closing_probability']) if law=='parity' else None
                if law=='nae':
                    qdata['admitting_closure_probability']=None
                summary[q][law]={k:fraction_record(v) for k,v in qdata.items()}
    comparison={}
    local_checks=[]
    if summary:
        prior_path=ROOT/'artifacts'/OLDER/(OLDER+'-E001_closures')/'panels_summary.json'
        original=json.loads(prior_path.read_text())['T']['parity']['endpoints']['all_arities']
        parity_draws=[sample_draw['laws']['parity'] for sample_draw in sample]
        closed=sum(s['termination']=='closed' for s in parity_draws)
        admitted=sum(s['positive'] is True for s in parity_draws)
        for field,old_field,pair in (
            ('closing_probability','at_least_one_closure',(closed,len(sample))),
            ('admitting_closure_probability','at_least_one_admitting_closure',(admitted,len(sample))),
            ('conditional_admission','per_component_admission',(admitted,closed))):
            previous=original[old_field]
            exact=Fraction(*summary['1/4']['parity'][field])
            assert pair==(previous['numerator'],previous['denominator'])
            interval=previous['95pct']
            comparison[field]={'old_count':pair,'old_95pct_interval':interval,'exact':fraction_record(exact),
                               'exact_inside_old_interval': interval[0]<=exact<=interval[1]}
        arities=sorted({len(row) for case in all_reps for row in case['founder_rows']})
        terminal=sorted({case['laws']['parity']['terminal_arity'] for case in all_reps if case['laws']['parity']['termination']=='closed'})
        local_checks=[local_rule_check(arity,law) for arity in arities for law in ('parity','nae')]
        local_checks.extend(local_rule_check(arity,'parity',odd=True) for arity in terminal)
    return {'by_size':whole,'uniform_size_probabilities':summary,'previous_sample_comparison':comparison,'local_knot_checks':local_checks}


if __name__=='__main__':
    parser=ArgumentParser()
    parser.add_argument('--small-size',type=int)
    args=parser.parse_args()
    sizes=[args.small_size] if args.small_size else list(range(4,9))
    result=audit(sizes,args.small_size is None)
    filename=f'census_audit_{args.small_size}.json' if args.small_size else 'census_audit.json'
    save(filename,result)
    print('verified',sizes,result['uniform_size_probabilities'].get('1/4',''),flush=True)
