"""Literal physical parent, state, and matched-delay checks for the three frozen rules."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations, product
import json
from pathlib import Path
import sys

import networkx as nx
from pysat.solvers import Minisat22

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GEN = ROOT / 'experiments/GENERATORS-20261120-001A/GENERATORS-20261120-001A-E001_generators'
CONE = ROOT / 'experiments/INFLUENCE-CONE-20261120-001A/INFLUENCE-CONE-20261120-001A-E001_cones'
sys.path.insert(0, str(GEN))
import fixtures
import periodic
import end_operator as ordinary
sys.path.insert(0, str(CONE))
import interventions
import guards

LAWS = ('nae', 'parity')
RULES = ('O', 'D', 'W')
CAP = 256


def tree(edges, arity):
    counts = Counter(p for pair in edges for p in pair)
    return fixtures.source_from(edges, [q-counts[p] for p, q in enumerate(arity)])


def path(arity):
    return tree(list(zip(range(len(arity)-1), range(1, len(arity)))), arity)


def extra(stars, at):
    rows = list(stars)
    rows[at] = (*rows[at], max(max(row) for row in rows)+1)
    return tuple(rows)


def multis(stars, rule):
    owners, graph, loose = fixtures.incidence(stars)
    witnesses, end_graph = fixtures.witnessed_end(graph, loose)
    before = fixtures.multi_groups(witnesses, end_graph)
    assert set(before) == set(ordinary.proposals(ordinary.from_stars(stars)))
    group_sets = [frozenset(g) for g in before]
    if rule == 'D':
        for a, b in graph.edges:
            if a in loose and b in loose and not any(a in row and b in row for row in group_sets):
                group_sets.append(frozenset((a, b)))
    elif rule == 'W':
        group_sets = []
        for group in before:
            choices = [w for w in loose if w not in group and all(graph.has_edge(w, v) for v in group)]
            group_sets.extend([frozenset((*group,w)) for w in choices] or [frozenset(group)])
    return sorted({tuple(sorted(row)) for row in group_sets}), loose


def literal_layer(stars, law, rule):
    groups, loose = multis(stars, rule)
    charges = Counter(p for group in groups for p in group)
    missing = {k:charges[k]-len(bits) for k,bits in loose.items() if charges[k]>len(bits)}
    record = {'groups':groups, 'charges':dict(charges), 'missing':missing}
    if not loose or missing:
        return stars, [], dict(record, status='stall' if missing else 'closed')
    parents = groups + [(k,) for k,bits in sorted(loose.items()) for _ in range(len(bits)-charges[k])]
    if len(parents)>CAP:
        return stars, [], dict(record, status='cap', minimum=len(parents))
    # The next witness of two new knots must be their shared old parent.
    demand, _ = ordinary._demands(parents)
    fresh = [0] if law=='parity' and len(parents)==1 else [max(1,3-len(g),d) for g,d in zip(parents,demand,strict=True)]
    next_bit=max(max(row) for row in stars)+1
    uses=Counter()
    born=[]
    new=list(stars)
    for family,count in zip(parents,fresh,strict=True):
        inputs=tuple(loose[k][uses[k]] for k in family)
        uses.update(family)
        private=tuple(range(next_bit,next_bit+count))
        next_bit+=count
        born.append(fixtures.Birth(len(new),family,inputs,private))
        new.append(inputs+private)
    assert all(uses[k]==len(bits) for k,bits in loose.items())
    physical,graph,new_loose=fixtures.incidence(new)
    for child in born:
        assert tuple(next(x for x in physical[b] if x!=child.knot) for b in child.inputs)==child.parents
        assert all(physical[b]==[child.knot] for b in child.fresh)
    assert all(not (a in new_loose and b in new_loose) for a,b in graph.edges)
    if rule=='O':
        plan=ordinary.step(ordinary.from_stars(stars),law,max_births=CAP)
        assert plan.status=='extend' and Counter(zip(plan.parents,plan.fresh))==Counter(zip(parents,fresh))
    return tuple(new),born,dict(record,status='extend',parents=parents,fresh=fresh)


def law_record(stars, law):
    fixtures.certify_source(stars, law)
    if law=='nae':
        for i,row in enumerate(stars):
            with Minisat22() as solver:
                for j,other in enumerate(stars):
                    if i!=j:
                        fixtures.nae_add(solver, other)
                assert solver.solve(assumptions=[-(b+1) for b in row])
    return {'full_local_projections':len(stars),'distinct_names':len(set.union(*map(set,stars)))}


def state_extension(old, new, law):
    """Compare all old words when affordable and verify every projection at small new arities."""
    bits=sorted(set.union(*map(set,old)))
    if len(bits)>13:
        return {'all_old_words':'extension proof', 'newborns':len(new)-len(old)}
    if law=='nae':
        with Minisat22() as solver:
            for row in new:
                fixtures.nae_add(solver,row)
            surviving=0
            for assignment in product((0,1),repeat=len(bits)):
                word=dict(zip(bits,assignment,strict=True))
                if all(len({word[b] for b in row})>1 for row in old):
                    assert solver.solve(assumptions=[b+1 if word[b] else -(b+1) for b in bits]);surviving+=1
    else:
        # The two powers of two agree iff every old solution has an extension.
        def rank(rows):
            piv={}
            for row in rows:
                x=sum(1<<b for b in row)
                while x and x.bit_length() in piv:
                    x^=piv[x.bit_length()]
                if x:
                    piv[x.bit_length()]=x
            return len(piv)
        q=len(set.union(*map(set,new)))-len(bits)
        rk=rank(old); kernel=q-rank([set(row)-set(bits) for row in new]); dimension=len(bits)+q-rank(new)
        assert dimension-kernel==len(bits)-rk
        surviving=1<<(len(bits)-rk)
    if new!=old and all(len(row)>=3 for row in new):
        fixtures.certify_source(new,law)
    return {'all_old_words':surviving,'newborns':len(new)-len(old)}


def witnessed_distance(stars,rule,left,right):
    groups,loose=multis(stars,rule)
    g=nx.Graph()
    g.add_nodes_from(loose)
    g.add_edges_from((a,b) for group in groups for a,b in combinations(group,2))
    if left not in g or right not in g:
        return 'inactive'
    return nx.shortest_path_length(g,left,right) if nx.has_path(g,left,right) else 'infinity'


def first_common(stars,law,rule,left,right,horizon):
    r,s={left},{right}; observations=[]
    for stage in range(1,horizon+1):
        stars,children,status=literal_layer(stars,law,rule)
        if status['status']!='extend':
            return {'observations':observations,'terminal':status['status']}
        r={b.knot for b in children if r.intersection(b.parents)}
        s={b.knot for b in children if s.intersection(b.parents)}
        observations.append({'stage':stage,'all_births':len(children),'R':len(r),'S':len(s),'both':len(r&s)})
        if r&s:
            break
    return {'observations':observations}


def paired_trace(stars,other,law,receiver,sender,depth,rule='O'):
    arms=[stars,other]
    previous=[{k:k for k in range(len(o))} for o in arms]
    rsets=[{receiver},{receiver}]; ssets=[{sender},{sender}]
    result=[]
    for stage in range(1,depth+1):
        cohorts=[]; rnext=[]; snext=[]; terminal=[]
        for i in range(2):
            arms[i],cohort,plan=literal_layer(arms[i],law,rule)
            cohorts.append(cohort);terminal.append(plan['status'])
            rnext.append({b.knot for b in cohort if rsets[i].intersection(b.parents)})
            snext.append({b.knot for b in cohort if ssets[i].intersection(b.parents)})
        if 'cap' in terminal:
            result.append({'stage':stage,'terminal':terminal});break
        local=[]; ids=[]
        for i,cohort in enumerate(cohorts):
            counts=Counter(); queried={}; label={}
            for b in cohort:
                ps=tuple(sorted(previous[i][p] for p in b.parents))
                key=(ps,counts[ps]);counts[ps]+=1;label[b.knot]=key
                if b.knot in rnext[i]:
                    queried[key]=len(b.fresh)
            local.append(queried);ids.append(label)
        # One common alphabet for recursively matched true-parent records.
        alphabet={g:k for k,g in enumerate(sorted(set(ids[0].values())|set(ids[1].values())))}
        previous=[{k:alphabet[v] for k,v in a.items()} for a in ids]
        L,R=local
        result.append({'stage':stage,'terminal':terminal,'receiver_births':[len(L),len(R)],'both':[len(rnext[i]&snext[i]) for i in range(2)],'fresh_rosters':[sorted(L.values()),sorted(R.values())],'unmatched':[len(L.keys()-R.keys()),len(R.keys()-L.keys())],'matched_changed_price':sorted((L[g],R[g]) for g in L.keys()&R.keys() if L[g]!=R[g]),'matched_births':len(L.keys()&R.keys())})
        rsets,ssets=rnext,snext
        if not any(cohorts):break
    return result


def tree_read(stars,r,s):
    _,graph,loose=fixtures.incidence(stars)
    cut=nx.shortest_path(graph,r,s);corr=Fraction(1);q=[len(stars[k]) for k in cut]
    for arity in q:corr*=Fraction(-1,2**(arity-1)-1)
    size=sum(q)-2*(len(cut)-1)
    # Independent connected-shore minimization on the actual finite tree.
    extremal=None;minimum=None
    if len(stars)<=18:
        other=set(graph)-set(cut)
        for i in range(len(other)+1):
            for group in combinations(other,i):
                shore=set(cut)|set(group)
                if not nx.is_connected(graph.subgraph(shore)):continue
                if any(not any(k in loose for k in comp) for comp in nx.connected_components(graph.subgraph(set(graph)-shore))):continue
                weight=sum(len(loose.get(k,())) for k in shore)+sum((u in shore)!=(v in shore) for u,v in graph.edges)
                if minimum is None or weight<minimum:minimum=weight;extremal=sorted(shore)
        assert minimum==size
    marks=[loose[r][0],loose[s][0]]
    allbits=max(max(row) for row in stars)+1
    raw=(1-corr)/2
    brute=None
    if allbits<=16:
        rows=[sum(1<<b for b in star) for star in stars]
        valid=[v for v in range(1<<allbits) if all(v&row not in (0,row) for row in rows)]
        unequal=sum(((v>>marks[0])^(v>>marks[1]))&1 for v in valid)
        assert Fraction(unequal,len(valid))==raw
        brute=[unequal,len(valid)]
    return {'path':cut,'arities':q,'marks':marks,'correlation':str(corr),'r':str(raw),'verified_nae_counts':brute,'bond_support_size':size,'bond_distance':size-1,'minimum_verified_shore':extremal}


def main():
    ap=ArgumentParser();ap.add_argument('--out',type=Path,default=ROOT/'artifacts'/HERE.parent.name/HERE.name/'built.json');args=ap.parse_args()
    live=path([6]*5)
    physical_edges=[(k,k+1) for k in range(4)]
    for v in (1,2,3):
        for j in range(4):physical_edges.append((v,5+(v-1)*4+j))
    spent=tree(physical_edges,[6]*17)
    short=path([3,4,3]); masked=path([3,3,4,3,3]);two=path([3,3]);three=path([3]*3)
    # A saturated ternary middle on a five-holder path cannot supply two witness groups.
    seven=fixtures.source_from([(0,1),(0,4),(1,4),(2,4),(2,6),(3,4),(3,5),(5,6),(0,1)],(3,0,3,3,3,2,2))
    names,frame=periodic.frame('meeting');twentyone=tuple(frame[i] for i in range(len(frame)))
    scenarios={'two':(two,0,1),'three':(three,0,1),'tree4_ternary':(path([3]*4),0,3),'tree5_ternary':(path([3]*5),0,4),'five_live':(live,0,4),'seventeen_spent':(spent,0,4),'seven_source':(seven,0,2),'separated_source':(twentyone,names.index('s'),names.index('t'))}
    result={'law_order':LAWS,'rules':RULES,'builds':{},'tree_readings':{},'edits':{},'global_and_structural_controls':{}}
    for tag,(stars,r,s) in scenarios.items():
        info={'initial_holdings':stars,'endpoints':[r,s],'laws':{}}
        for law in LAWS:
            row={'legal_start':law_record(stars,law),'rules':{}}
            for rule in RULES:
                grown,bs,plan=literal_layer(stars,law,rule)
                if tag in ('five_live','three','two','tree4_ternary','seventeen_spent'):
                    assert plan['status']!='cap'
                distance=witnessed_distance(stars,rule,r,s)
                horizon=2 if tag in ('five_live','seventeen_spent','two','three','seven_source','separated_source') else 1
                observed=first_common(stars,law,rule,r,s,horizon)
                if isinstance(distance,int) and distance<=horizon and plan['status']=='extend':
                    assert observed['observations'][-1]['both'] and observed['observations'][-1]['stage']==distance
                item={'plan':plan,'distance':distance,'actual_descent':observed,'word_extension':state_extension(stars,grown,law)}
                if plan['status']=='extend' and tag in ('two','three','five_live','seven_source','separated_source'):
                    ordinary_next=multis(grown,'O')[0]
                    assert ordinary_next==multis(grown,'D')[0]==multis(grown,'W')[0]
                    item['reached_ordinary_groups']=len(ordinary_next)
                row['rules'][rule]=item
            info['laws'][law]=row
        result['builds'][tag]=info
    for tag,(source,r,s) in {'near':(two,0,1),'ordinary_live':(live,0,4),'ordinary_spent':(spent,0,4),'unmasked':(short,0,2),'masked':(masked,1,3),'ternary':(three,0,2),'wider_middle':(path([3,7,3]),0,2),'longer_equal_rate':(masked,0,4)}.items():
        result['tree_readings'][tag]=tree_read(source,r,s)
    raw=result['tree_readings']; assert raw['masked']['r']==raw['unmasked']['r'] and raw['ordinary_live']['r']==raw['ordinary_spent']['r']
    assert raw['wider_middle']['r']==raw['longer_equal_rate']['r']=='284/567'
    assert [witnessed_distance(src,'O',0,len(src)-1) for src in (path([3,7,3]),masked)]==[1,2]
    assert raw['ordinary_live']['bond_distance']==raw['ordinary_spent']['bond_distance']==21
    for law in LAWS:
        nested=result['builds']
        assert all(nested['five_live']['laws'][law]['rules'][r]['distance']==2 for r in RULES)
        assert all(nested['seventeen_spent']['laws'][law]['rules'][r]['distance']=='infinity' for r in RULES)
        assert [nested['seven_source']['laws'][law]['rules'][r]['plan']['status'] for r in RULES]==['extend','stall','stall']
        assert all(nested['separated_source']['laws'][law]['rules'][r]['plan']==nested['separated_source']['laws'][law]['rules']['O']['plan'] for r in RULES)
        changes={}
        for tag,src,r,s,edited,depth in [('near',two,0,1,extra(two,1),4),('unmasked',short,0,2,extra(short,2),4),('masked',masked,1,3,extra(masked,3),5),('long',path([6]*7),0,6,extra(path([6]*7),6),4),('sham',short,0,2,short,4),('same_role',short,0,0,extra(short,0),2)]:
            changes[tag]=paired_trace(src,edited,law,r,s,depth)
        same=list(short);newbit=max(max(s) for s in same)+1
        for k in (1,2):same[k]+= (newbit,)
        assert law_record(same,law)
        changes['unchanged_end_holding_edit']=paired_trace(short,same,law,0,2,4)
        assert next(q['stage'] for q in changes['unmasked'] if q['matched_changed_price'])==1
        assert next(q['stage'] for q in changes['unmasked'] if any(q['unmatched']))==2
        assert not any(q['matched_changed_price'] for q in changes['masked'])
        assert [q['matched_births'] for q in changes['masked']]==[1,0,0,0,0]
        assert next(q['stage'] for q in changes['long'] if q.get('matched_changed_price'))==3
        assert next(q['stage'] for q in changes['long'] if any(q.get('unmatched',[])))==4
        assert all(not (any(q['unmatched']) or q['matched_changed_price']) for k in ('sham','near','unchanged_end_holding_edit') for q in changes[k]);result['edits'][law]=changes
        result.setdefault('rival_edit_readouts',{})[law]={}
        for rule,src,receiver,sender in [('D',two,0,1),('W',three,1,2)]:
            trace=paired_trace(src,extra(src,sender),law,receiver,sender,2,rule)
            assert trace[0]['both']==[1,1] and trace[0]['matched_changed_price']
            assert any(trace[1]['unmatched'])
            result['rival_edit_readouts'][law][rule]=trace
        result['global_and_structural_controls'][law]={'one_witness_d3':interventions.charged(1,law),'sole_birth':interventions.terminal(3,law)}
    result['global_and_structural_controls']['veto']=guards.funding_panel(7)
    args.out.parent.mkdir(exist_ok=True,parents=True);args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(f'{len(scenarios)} physical starts, {len(scenarios)*len(LAWS)*len(RULES)} rule/law comparisons, {len(result["edits"]["nae"])} paired edit controls per law -> {args.out}')


if __name__=='__main__':
    main()
