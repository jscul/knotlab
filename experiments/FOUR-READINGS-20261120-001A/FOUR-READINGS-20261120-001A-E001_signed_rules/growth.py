"""Replay the ordinary forward rule from every puncture and from the frozen cohorts."""
from collections import Counter, defaultdict
from itertools import combinations
from random import Random
import json
import sys

import networkx as nx

from census import ROOT, OUT, closure_candidates, pauli_solution, save

GROWTH=ROOT/'experiments/NAE-GROWTH-20261119-001B/NAE-GROWTH-20261119-001B-E001_nae'
COUNTS=ROOT/'experiments/ENTANGLEMENT-READ-20261120-001B/ENTANGLEMENT-READ-20261120-001B-E001_separated_readings'
sys.path.insert(0,str(GROWTH))
sys.path.insert(0,str(COUNTS))
import naelib
from exact_counts import Parity, NotAllEqualSupport

J=naelib.J
ARCHIVE=ROOT/'artifacts/HEAVY-GROWTH-20261119-001/HEAVY-GROWTH-20261119-001-E001_checks/sources_audit.json'


def holding(ends):
    return [[i for i,p in enumerate(ends) if u in p] for u in range(1+max(map(max,ends)))]


def observe(stage, law, rule, retain=True):
    old_n=len(stage.bits_of)
    live=[j for j in stage.live if stage.loose(j)]
    if not live:
        return {'status':'already_closed'}
    groups=stage.groups_among(live)
    demands=Counter(j for group in groups for j in group)
    loose={j:len(stage.loose(j)) for j in live}
    predicted=len(groups)+sum(loose[j]-demands[j] for j in live)
    if not any(demands[j]>loose[j] for j in live) and old_n+predicted>400:
        return dict(status='cap', old_holders=old_n,predicted_births=predicted,old_distinctions=stage.nbits)
    step=stage.step(rule,None)
    if step is None:
        return dict(status='stall',shortages={j:demands[j]-loose[j] for j in live if demands[j]>loose[j]})
    new_ids=range(old_n,len(stage.bits_of))
    new=[dict(holder=j,places=stage.bits_of[j],fresh=stage.fresh[j],parents=stage.parents[j],
              demand=stage.demand_at_birth[j]) for j in new_ids]
    if stage.nbits>2000:
        status='cap'
    else:
        status='grown' if stage.live else 'closed'
    row=dict(status=status,births=len(new),holders=len(stage.bits_of),distinctions=stage.nbits,
             loose=sum(len(v)==1 for v in stage.owner.values()))
    if retain: row['new']=new
    if status=='closed':
        assert law=='parity' and len(new)==1 and new[0]['fresh']==0
        ends=[tuple(pair) for bit,pair in sorted(stage.owner.items())]
        graph=nx.Graph(ends)
        row['terminal_arity']=len(new[0]['places'])
        row['operator_after_one_supplied_odd']=not nx.check_planarity(graph)[0]
    return row


def certify(stars,law):
    if law=='parity':
        oracle=Parity(stars)
        return [oracle.certificate(s)['eligible'] for s in stars]
    with NotAllEqualSupport(stars) as oracle:
        return [oracle.certificate(s)['eligible'] for s in stars]


def rule_for(law):
    return (naelib.parity_rule if law=='parity' else naelib.nae_rule)(J.F.fewest)


def puncture(ends,u):
    stars=holding(ends)
    parents=[i for i,pair in enumerate(ends) if u in pair]
    pre=[s for i,s in enumerate(stars) if i!=u]
    live=J.S.from_junctions(pre)
    connected=nx.is_connected(nx.Graph(dict(enumerate(live.nbr))))
    laws=certify(pre,'parity')
    actual=None
    if connected and all(laws):
        actual=observe(live,'parity',rule_for('parity'))
    recovered=bool(actual and actual['status']=='closed' and (live.bits_of[-1] and set(live.bits_of[-1])==set(parents)))
    return dict(last=u,source_connected=connected,source_full_knots=laws,restored=recovered,step=actual)


def source(name, stars, family, steps, provenance):
    row=dict(name=name,family=family,stars=stars,provenance=provenance,laws={})
    for law in ('parity','nae'):
        checks=certify(stars,law)
        stages=[]
        if all(checks):
            stage=J.S.from_junctions(stars)
            rule=rule_for(law)
            for _ in range(steps):
                stages.append(observe(stage,law,rule))
                if stages[-1]['status']!='grown':
                    break
        row['laws'][law]=dict(source_full_knots=checks, stages=stages)
    return row


def subset_sources():
    for k in (3,4,5):
        for single in (True,False):
            for extra in (0,1):
                if single:
                    # A spare on the future spent first knot cannot remain loose through its first
                    # round. From a single holder, this comparator is literally a (k+1)-place source.
                    sizes=[k+extra];meetings=[]
                else:
                    sizes=[k+extra]+[k]*k;meetings=[(0,i) for i in range(1,k+1)]
                steps=k+extra if single else k-1
                yield source(f'subsets_{k}_'+(f'single_spare_{extra}' if single else f'leaves_spare_{extra}'),
                             J.stars_from(sizes,meetings),'built_subset',steps,
                             dict(k=k,extra_at_spent=extra,initial_single=single))


def ordinary():
    rng=Random(202611200131)
    for n in (4,5,6):
        for replicate in range(4):
            word=[rng.randrange(n) for _ in range(n-2)]
            graph=nx.from_prufer_sequence(word)
            meetings=sorted(tuple(sorted(p)) for p in graph.edges)
            extra=[rng.randrange(4)==0 for j in range(n)]
            sizes=[max(3,graph.degree(j))+extra[j] for j in range(n)]
            yield source(f'tree_{n}_{replicate}',J.stars_from(sizes,meetings),'uniform_tree',3,
                         dict(prufer=word,extras=extra,words=n**(n-2),replicate=replicate))
    archive=json.loads(ARCHIVE.read_text())['named_archive_starts']
    for name in ['start-00','start-04','start-13']:
        r=archive[name]
        yield source(name,J.stars_from(r['sizes'],r['meetings']),'archived_burst',3,dict(archive_id=name))


def special():
    all5=list(combinations(range(5),2))
    six=list(nx.complete_bipartite_graph(3,3).edges())
    three=[(0,j) for j in (1,2,3)]
    for j,(a,b) in enumerate(((1,2),(2,3),(1,3))):
        w=4+j
        three.extend([(w,a),(w,b),(w,7+j),(7+j,10),(7+j,11)])
    def split(ends):
        a,b=ends[0]; last=1+max(map(max,ends))
        return [*ends[1:],(a,last),(last,b)]
    return [('all5',all5,0),('six',six,0),('all_ternary',three,0),
            ('all5_nonfinal_double',[*all5,(1,2)],0),('all5_final_double',[*all5,(0,1)],0),
            ('all5_split',split(all5),5),('six_split',split(six),6)]


def run():
    rows=json.loads((OUT/'census.json').read_text())
    inverse=[]
    for r in rows:
        ends=r['sharing']
        trials=[puncture(ends,u) for u in range(r['n'])]
        assert [t['last'] for t in trials if t['restored']]==r['restored_last_holders']
        inverse.append(dict(atlas=r['atlas'],punctures=trials))
    save('all_punctures.json',inverse)
    specimens=[]
    for name,ends,last in special():
        p=puncture(ends,last)
        ops=pauli_solution(ends,{0})
        g=nx.Graph(ends)
        assert (ops is not None) == (not nx.check_planarity(g)[0])
        pre=[s for i,s in enumerate(holding(ends)) if i!=last]
        cases=source(name,pre,'built_final',1,'One specified physical rule removed')
        cases.update(ends=ends, last=last, puncture=p, paulis=ops)
        specimens.append(cases)
    save('minimum_controls.json',specimens)
    samples=list(subset_sources())+list(ordinary())
    for row in samples:
        for law,entry in row['laws'].items():
            assert all(entry['source_full_knots'])
        if row['family']=='built_subset' and (row['provenance']['initial_single'] or not row['provenance']['extra_at_spent']):
            k=row['provenance']['k']+row['provenance']['extra_at_spent']
            stage=row['laws']['parity']['stages'][-1]
            assert stage['holders']==2**k and stage['distinctions']==k*2**(k-1) and stage['status']=='closed'
            assert stage['operator_after_one_supplied_odd']==(k>=4)
            stage_stars=row['stars']+[birth['places'] for step in row['laws']['parity']['stages'] for birth in step['new']]
            owners=defaultdict(list)
            for j,s in enumerate(stage_stars):
                for h in s: owners[h].append(j)
            measured=nx.Graph(tuple(p) for p in owners.values())
            assert nx.is_isomorphic(measured,nx.hypercube_graph(k))
    save('growth_histories.json',samples)
    rates=Counter()
    for row in samples:
        for law,r in row['laws'].items():
            key=(row['family'],law,r['stages'][-1]['status'])
            rates[key]+=1
    print('census',Counter((r['n'],r['operator'],bool(r['restored_last_holders'])) for r in rows))
    print('histories',rates)
    print('control',[(s['name'],s['puncture']['restored']) for s in specimens])


if __name__=='__main__':
    run()
