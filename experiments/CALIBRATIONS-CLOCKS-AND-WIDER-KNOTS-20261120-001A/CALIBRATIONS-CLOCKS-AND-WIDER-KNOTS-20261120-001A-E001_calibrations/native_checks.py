"""Reconstruct refused attempts, actual growth filtering, and weighted marked sources."""
from collections import Counter, defaultdict
from functools import cache
from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations
import json
from random import Random
import sys
from study_io import allowed, failed, family, load_module, plus, write

FREEDOM = 'FREEDOM-CLOCKS-AND-BIRTHS-20261120-001A'
FOUR = 'FORBIDDING-JOIN-20261120-001C'
sys.path.insert(0,str(family(FREEDOM)))
from ordinary import J, advance, certify, elimination_width, gram, hosted, nea_contraction
import networkx as nx
from scipy.stats import beta
from pysat.solvers import Minisat22


def rng(label, size, index, purpose):
    tag=f'202611209643|{label}|{size}|{index}|{purpose}'
    return Random(int.from_bytes(sha256(tag.encode()).digest(),'big'))


def generate(label, n, i):
    rand=rng(label,n,i,'source'); word=[rand.randrange(n) for _ in range(n-2)]
    structure=nx.from_prufer_sequence(word); extra=None
    if label=='extra':
        extra=rand.choice([p for p in combinations(range(n),2) if not structure.has_edge(*p)])
        structure.add_edge(*extra)
    meetings=sorted(tuple(sorted(p)) for p in structure.edges)
    stars=J.stars_from([max(3,structure.degree(h)) for h in range(n)],meetings)
    return stars,dict(prufer=word,extra=extra)


def subset_keys(affected):
    return [frozenset(row) for k in range(len(affected)+1) for row in combinations(affected,k)]


@cache
def measured(stars, bit, law):
    held=tuple(h for h,row in enumerate(stars) if bit in row)
    assert len(held) in (1,2)
    width=elimination_width(stars,[bit]) if law=='nae' else 0
    if width>10:
        return dict(censored_width=width)
    g=gram(stars,[bit],law);n=int(g[0,0]+g[1,1]);m=int(g[0,1]+g[1,0]); assert n>0
    choices=subset_keys(held)
    if law=='parity':
        by_failure={key:int(key==frozenset(held))*n for key in choices}
    else:
        # A changed mark remains legal at h exactly when the other marks of h already contain both values.
        no_fail={}
        for key in choices:
            residual=[tuple(b for b in row if b!=bit or h not in key) for h,row in enumerate(stars)]
            check_width=elimination_width(residual,[])
            if check_width>10:return dict(censored_width=check_width)
            unused=not any(bit in row for row in residual)
            no_fail[key]=(2 if unused else 1)*int(nea_contraction(residual,[])[0,0])
        assert no_fail[frozenset()]==n and no_fail[frozenset(held)]==m
        by_failure={}
        for key in choices:
            survivors=frozenset(held)-key
            by_failure[key]=sum((-1)**len(sub)*no_fail[survivors|sub] for sub in subset_keys(sorted(key)))
    assert by_failure[frozenset()]==m and sum(by_failure.values())==n and min(by_failure.values())>=0
    if 1+max(map(max,stars))<=12:
        ordinary=allowed(stars,law)
        literal=Counter(frozenset(failed(s ^ (1<<bit),stars,law)) for s in ordinary)
        assert all(literal[k]==v for k,v in by_failure.items()) and len(ordinary)==n
    return dict(held=held,allowed=n,paired=m,full_pairs=m//2,singleton_pairs=n-m,
                actual_moving=str(F(m,n)),calibrated_plus=plus(n,m),guarded_spectral_plus='1',
                permitted_plus_illegal=str(F(n-m,2*(n+m))),permitted_minus_illegal='1/2' if m<n else None,
                permitted_all_illegal=str(F(n-m,2*n)),physical_gram=list(map(int,g.flat)),
                failed_original_rules=[[sorted(k),by_failure[k]] for k in choices],elimination_width=width)


def frozen(stars):
    return tuple(tuple(sorted(row)) for row in stars)


def stress():
    cases=[];votes=[];groups=defaultdict(list)
    def add(label,n,i,stars,origin,host=False):
        for law in ('parity','nae'):
            assert all(certify(stars,law))
            event,new=advance(stars,law);stages=[frozen(stars)]+([frozen(new)] if new is not None else [])
            key=f'{label}/{n}/{i}/{law}'
            projections=[list(certify(stage,law)) for stage in stages]
            cases.append(dict(key=key,law=law,label=label,size=n,origin=origin,stages=stages,event=event,
                              complete_local_law_by_holder=projections))
            for j in (range(16) if host else [i]):
                h=rng(label,n,j,'holder').randrange(n);b=rng(label,n,j,'bit').choice(sorted(stars[h]))
                obs=[measured(stage,b,law) for stage in stages]
                votes.append(dict(case=key,placement=j,knot=h,bit=b,observations=obs))
                for age in (0,1):
                    cell=obs[age] if age<len(obs) else None
                    groups[label,n,law,age].append((cell,event['status']))
    for label in ('tree','extra'):
        for n in range(4,9):
            for i in range(12):
                stars,origin=generate(label,n,i);add(label,n,i,stars,origin)
    for label,stars in hosted().items():add(label,len(stars),0,stars,dict(fixed_host=True),True)
    summaries=[]
    for (label,n,law,age),v in sorted(groups.items()):
        reached=[s for s,e in v if s is not None];exact=[s for s in reached if 'paired' in s]
        partial=sum(0<s['paired']<s['allowed'] for s in exact);count=len(exact)
        interval=None if not count else [float(beta.ppf(.025,partial,count-partial+1)) if partial else 0.,
            float(beta.ppf(.975,partial+1,count-partial)) if partial!=count else 1.]
        values=[F(s['paired'],s['allowed']) for s in exact]
        summaries.append(dict(label=label,size=n,law=law,age=age,drawn=len(v),reached=len(reached),exact=count,
            partial=partial,ci_95=interval,mean_free=str(sum(values)/count) if count else None,
            zero=sum(not val for val in values),full=sum(val==1 for val in values),
            minimum=str(min(values)) if values else None,maximum=str(max(values)) if values else None,
            stage_unavailable=Counter(e for s,e in v if s is None),width_censored=len(reached)-count))
    verdicts={}
    motion=load_module('calibration_local_projection_gate',family('READS-HOLDERS-SOURCES-20261120-001A')/'motion.py')
    for size in sorted({len(row) for case in cases for stage in case['stages'] for row in stage}):
        for law in ('parity','nae'):
            patterns=tuple(sorted(allowed([list(range(size))],law)))
            verdict=motion.knot_check(size,patterns)
            assert verdict['is_knot']
            verdicts[f'{law}/{size}']=verdict
    write('fresh_sources.json.gz',dict(seed=202611209643,source_runs=cases,placements=votes,canonical_local_laws=verdicts))
    write('source_summary.json',summaries)
    return dict(source_law_runs=len(cases),marked_law_draws=len(votes),exact_stages=sum(r['exact'] for r in summaries),sample_summary_rows=len(summaries))


def clauses(stars, law):
    cnf=[]
    for row in stars:
        if law=='nae':
            cnf += [[b+1 for b in row],[-b-1 for b in row]]
        else:
            for pattern in range(1<<len(row)):
                if pattern.bit_count()%2:
                    cnf.append([-(b+1) if pattern>>i&1 else b+1 for i,b in enumerate(row)])
    return cnf


def filter_records():
    mod=load_module('calibration_old_growth_checks',family(FOUR)/'growth_checks.py')
    archive=json.loads((family(FOUR,'artifacts')/'growth_checks.json').read_text())['arms']
    records=[]
    for name in ('four_0','four_1'):
        for law in ('parity','nae'):
            for rival in ('ordinary','one_fewer','floor'):
                prior=archive[name][law][rival]; rows=mod.specimens()[name][0]; histories=[]
                for age in (1,2):
                    following,receipt=mod.advance(law,rival,rows)
                    assert following==frozen(prior['stages'][age]['supports'])
                    old=sorted(allowed(rows,law));universe=sorted({b for row in rows for b in row})
                    refused=[];witnesses=[]
                    with Minisat22(bootstrap_with=clauses(following,law)) as oracle:
                        for word in old:
                            pins=[(b+1)*(1 if word>>b&1 else -1) for b in universe]
                            if not oracle.solve(assumptions=pins):
                                refused.append(word);continue
                            if len(witnesses)<2:
                                full=sum(1<<(lit-1) for lit in oracle.get_model() if lit>0)
                                assert not failed(full,following,law);witnesses.append([word,full])
                    assert len(old)-len(refused)==receipt['surviving_old']==prior['rounds'][age-1]['surviving_old']
                    histories.append(dict(age=age,old_knots=rows,following_knots=following,old_count=len(old),
                        retained=len(old)-len(refused),all_refused_words=refused,lift_examples=witnesses,
                        births=receipt['births'],first_refused_breaks=[failed(refused[0],rows,law),
                            [v['id'] for v in receipt['births'] if v['f']==0 and failed(refused[0],[v['spent']],law)]] if refused else None))
                    rows=following
                records.append(dict(source=name,law=law,rule=rival,rounds=histories))
    return records


def native():
    prior=json.loads((family(FREEDOM,'artifacts')/'ordinary_events.json').read_text());swaps={}
    for law in ('parity','nae'):
        stars=[[0,1,2],[0,3,4,5]]; words=allowed(stars,law); pairs=[]
        for w in sorted(words):
            x=((w>>1)^(w>>2))&1; target=w^(6*x)
            assert target in words;pairs.append([w,target])
        assert pairs==prior['archived_swap'][law]['attempts']
        swaps[law]=dict(ordered_lifts=pairs,old=len(words),moving=sum(a!=b for a,b in pairs),outside=0)
    marked=family('READS-HOLDERS-SOURCES-20261120-001A')
    motion=load_module('calibration_motion_archive',marked/'motion.py');guard=motion.directed_guard()
    assert guard==prior['guard']; record=guard['idling_collision']
    stage=motion.motion_stage.load_stage('R31',1); import b_updates
    board=b_updates.Board(stage)
    h=board.supports.index(motion.mask(record['named_event']));w=motion.mask(record['enabled_state']);y=motion.mask(record['image_and_disabled_state'])
    assert h in board.actions(w) and h not in board.actions(y) and w^board.supports[h]==y
    assert stage.allowed_change(record['named_event']) and stage.allowed_change(motion.bits(w)) and stage.allowed_change(motion.bits(y))
    minimum={}
    for mark in record['named_event']:
        witness=stage.minimum_response(mark,pinned_loose=False)
        assert witness.minimum_size==len(record['named_event']);minimum[mark]=witness.minimum_size
    filters=filter_records();write('ordinary_refusals.json.gz',dict(swap=swaps,guard=guard,enabled_event=h,
        named_least_size_by_mark=minimum,rule_filter=filters))
    return dict(swap_moving={k:[r['moving'],r['old']] for k,r in swaps.items()},guard_event=h,new_filter_transitions=sum(len(r['rounds']) for r in filters))
