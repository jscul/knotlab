"""Frozen endpoint and repeat-word survey. Scorer labels never select an orientation."""
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
import argparse
import json
import random
import sys

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREVIOUS = ROOT / 'experiments/FOUR-READINGS-20261120-001D/FOUR-READINGS-20261120-001D-E001_unbuilt_sources'
sys.path.insert(0, str(PREVIOUS))
import panel as prior

end, fix = prior.end, prior.fix
OUT = ROOT / 'artifacts' / HERE.parent.name / HERE.name
H, CAP = 32, 128


def cycword(word):
    w = tuple(word)
    variants = (w,w[::-1])
    return min(k[i:]+k[:i] for k in variants for i in range(len(k)))


def orbit(graph, point):
    """Rooted isomorphism tests avoid enumerating every permutation of symmetric leaves."""
    left = graph.copy()
    nx.set_node_attributes(left, {p:int(p==point) for p in left}, 'marked')
    nm = nx.algorithms.isomorphism.categorical_node_match(['color','marked'],[None,0])
    result = set()
    for p in graph:
        if graph.nodes[p].get('color') != graph.nodes[point].get('color'):
            continue
        right = graph.copy()
        nx.set_node_attributes(right, {v:int(v==p) for v in right}, 'marked')
        if nx.is_isomorphic(left,right,node_match=nm):
            result.add(p)
    return result


def classify(state, raw_rows, groups):
    roles = nx.Graph()
    roles.add_nodes_from(((0,v),{'color':('live',state.opens[v])}) for v in state.opens)
    counts = Counter()
    for w, block in raw_rows:
        if len(block) < 2:
            continue
        roles.add_node((1,w),color=('witness',len(block)))
        roles.add_edges_from(((0,v),(1,w)) for v in block)
        counts.update(combinations(sorted(block),2))
    assert nx.is_connected(roles)
    multi = max(counts.values(),default=0) > 1
    triple = any(len(g) >= 3 for g in groups)
    rank = roles.number_of_edges()-len(roles)+1
    return roles, {'rank':rank,'duplicate':multi,'unheld':triple,
                   'identified':not (multi or triple) and sum(state.opens.values())>=2}


def return_words(roles, physical, age):
    max_period = (H-age+1)//2
    if max_period < 8:
        return [],False
    if len(roles)>48 or sum(v[0]==0 for v in roles)>20:
        return [],True
    cycles=list(nx.simple_cycles(roles,length_bound=2*(max_period-4)))
    returns=defaultdict(set)
    for cy in cycles:
        if len(cy) < 8:
            continue
        for c in (cy,cy[::-1]):
            for j,r in enumerate(c):
                if r[0]==0:
                    seq = c[j:]+c[:j]
                    pts=tuple(v for typ,v in seq[::2])
                    returns[r[1]].add((pts,seq[1][1],seq[-1][1]))
    marks = {}
    def marker_set(m):
        if m not in marks:
            if physical is not None:
                marks[m]=orbit(physical,m)
            else:
                marks[m]={v for typ,v in orbit(roles,(0,m))}
        return marks[m]
    best=None
    candidates=[]
    for ret in returns.values():
        for a,first,last in sorted(ret):
            for b,start,finish in sorted(ret):
                score=len(a)+len(b),len(a)
                if score[0] > max_period or (best is not None and score>best):
                    continue
                if last==start or finish==first:
                    continue
                both=set(a)|set(b)
                good=[m for m in set(b)-set(a) if marker_set(m)<=both]
                if not good:
                    continue
                if best!=score:
                    best=score
                    candidates=[]
                # All admissible marks are returned, not one index chosen to fix a symmetry.
                candidates.append({'a':a,'b':b,'marks':[sorted(marker_set(m)) for m in sorted(good)]})
    return candidates,False


def is_source(word, marks):
    doubled=set()
    for r in range(1,len(word)//2+1):
        for i in range(len(word)-2*r+1):
            v=word[i:i+r]
            if v==word[i+r:i+2*r]:
                doubled.update(v)
    return any(m not in doubled for m in marks)


def phase_rows(word,size):
    p=len(word)
    long=word*((size+p-1)//p+1)
    return [long[i:i+size] for i in range(p)]


def packet_windows(candidates, anchor_age):
    unique={}
    checks=set()
    for c in candidates:
        a,b=tuple(c['a']),tuple(c['b'])
        for k in range(1,H+1):
            word=a*k+b
            p=len(word); launch=anchor_age+2*p-1
            if launch>H:
                break
            key=cycword(word)
            if key in unique:
                continue
            marks=c['marks'][0] # Each admissible orbit works; the family is identical.
            for n in (2*p-1,2*p,2*p+1):
                check=(key,tuple(marks),n)
                if check in checks:
                    continue
                checks.add(check)
                windows=phase_rows(word,n)
                assert len({min(w,w[::-1]) for w in windows})==p
                assert all(is_source(w,marks)==(n<2*p) for w in windows)
                parents={min(w,w[::-1]) for w in phase_rows(word,n-1)}
                assert all(min(w[:-1],w[:-1][::-1]) in parents and min(w[1:],w[1:][::-1]) in parents for w in windows)
            unique[key]={'age':launch,'width':p,'parents_per_member':2,'k':k,'word':key,
                         'a':a,'b':b,'marker_orbit':marks}
    return sorted(unique.values(),key=lambda x:(x['age'],x['word']))


def groups_rows(state):
    try:
        groups=end._proposals(state,CAP)
    except end._Cap:
        return None
    return groups


def advance(state, grants, law, single):
    """Cap the next cohort including its proposed lookahead, before dense expansion."""
    paid=Counter(p for g in grants for p in g)
    assert all(state.opens[v]>=paid[v] for v in paid)
    parents=grants+tuple((v,) for v,h in state.opens.items() for _ in range(h-paid[v]))
    if len(parents)>CAP:
        return None,{'kind':'current_births','lower':len(parents)}
    rows=defaultdict(list)
    for child,ps in enumerate(parents):
        for p in ps:
            rows[p].append(child)
    if len(parents)==1 and single and law=='parity':
        return (parents,None,[],None),None
    raw=[(v,tuple(row)) for v,row in rows.items() if len(row)>=2]
    # Every proposed group counts at least once toward the following cohort's births.
    possible=end.End(dict.fromkeys(range(len(parents)),1),[r for _,r in raw])
    nxt_groups=groups_rows(possible)
    if nxt_groups is None:
        return None,{'kind':'following_groups','lower':CAP+1,'known_current_parents':len(parents)}
    demand=Counter(v for group in nxt_groups for v in group)
    opens={i:max(demand[i],1,3-len(p)) for i,p in enumerate(parents)}
    return (parents,end.End(opens,[r for _,r in raw]),raw,nxt_groups),None


def inspect_component(state, raw, grants, law, single, physical, original_readable, lean):
    receipts=[]
    persists={}
    pure={}
    candidates_seen=[]
    families=[]
    positive=False
    broad_no=False
    cap=None
    closed=False
    unreadable_candidate=False
    end_proof=False
    for age in range(H+1):
        graph=prior.graph_of(state)
        tips,stable=prior.path_features(state,graph)
        roles,gate=classify(state,raw,grants)
        if age and stable:
            for tag in pure.values():
                if persists[tag]['read'] and persists[tag]['certified'] is None:
                    persists[tag]['certified']=age
        if stable or gate['identified'] and gate['rank']<=1:
            broad_no=True
        if lean and age==0 and gate['identified'] and gate['rank']:
            core=nx.k_core(roles,2)
            assert all(roles.degree(v)==2 for v in core) and gate['rank']==1
        receipts.append({'age':age,'width':len(graph),'stable_path':stable,**gate})
        if gate['identified'] and gate['rank']>=2 and not positive and not broad_no:
            pairs,too_wide=return_words(roles,physical if age==0 else None,age)
            if pairs:
                candidates_seen.append({'age':age,'pairs':pairs,'readable':original_readable})
                if original_readable:
                    packets=packet_windows(pairs,age)
                    assert packets
                    positive=True;families.extend(packets)
                else:
                    unreadable_candidate=True
            unreadable_candidate |= too_wide
        if age==H:
            break
        if len(state.opens)==0:
            closed=True; broad_no=True; break
        # A stable path only grows by its two continuing endpoints and pair births.
        # If the source itself is stable, take its first full step to count newly launched tips.
        if age and stable:
            if all(v['certified'] is not None or not v['read'] for v in persists.values()):
                break
        # With a certified returning part, no later cut is scanned for additional
        # templates. Check endpoint observations until the numerical cap if necessary.
        result,cap=advance(state,grants,law,single)
        if cap:
            cap['before_age']=age+1
            break
        parents,nxt,raw,grants=result
        if nxt is None:
            closed=True; broad_no=True
            break
        new_tips,_=prior.path_features(nxt,prior.graph_of(nxt))
        nq={}
        for v,ps in enumerate(parents):
            if len(ps)==1 and ps[0] in pure:
                tag=pure[ps[0]]
                nq[v]=tag
                if v not in new_tips: persists[tag]['read']=False
            elif v in new_tips:
                assert len(ps)==1
                tag=len(persists);nq[v]=tag
                persists[tag]={'launch':age+1,'parent':ps[0],'read':True,'certified':None}
        assert set(pure.values())<=set(nq.values())
        pure=nq
        state=nxt
    assert not (positive and broad_no), (receipts,candidates_seen)
    # The necessary condition is a component condition; no component can receive a
    # release from another one after the starting cut.
    return {'cuts':receipts,'cap':cap,'closed':closed,'bounded':broad_no,'positive':positive,
            'structural_candidates':candidates_seen,'unreadable_or_large_candidate':unreadable_candidate,
            'periodic_packets':families,'tip_records':list(persists.values()),'end_only_periodic_proved':end_proof}


def draw_specs():
    for size_group,run_count,limits,seed,meet_seed in [('4-8',512,(4,8),20261120311,20261120312),
                                                       ('9-12',256,(9,12),20261120314,20261120315)]:
        rng=random.Random(seed); extra_rng=random.Random(meet_seed)
        for i in range(run_count):
            n=rng.randint(*limits); word=[rng.randrange(n) for _ in range(n-2)]
            base=nx.from_prufer_sequence(word)
            coins=[int(rng.randrange(4)==0) for _ in range(n)]
            missing=[p for p in combinations(range(n),2) if not base.has_edge(*p)]
            extra_rng.shuffle(missing)
            for extra in (2,3):
                if len(missing)<extra: raise AssertionError(n)
                g=base.copy();g.add_edges_from(missing[:extra])
                edges=sorted(tuple(sorted(p)) for p in g.edges)
                for supply in (('original','funded_sensitivity') if i<96 else ('original',)):
                    yield {'size_group':size_group,'draw':i,'n':n,'word':word,'coins':coins,'extra':extra,
                           'extra_meetings':missing[:extra],'edges':edges,'supply':supply}


def source(spec):
    g=nx.Graph();g.add_nodes_from(range(spec['n']));g.add_edges_from(spec['edges'])
    n=spec['n']; funded_all=spec['supply']=='funded_sensitivity'
    if funded_all:
        raw=[tuple(g[w]) for w in g]
        all_live=end.End(dict.fromkeys(range(n),1),raw)
        demand=Counter(v for group in end.proposals(all_live) for v in group)
        h=[max(2,3-g.degree(v),demand[v])+spec['coins'][v] for v in g]
    else:
        h=[max(0,3-g.degree(v))+spec['coins'][v] for v in g]
    stars=fix.source_from(spec['edges'],h)
    legal={q:True for q in ('parity','nae')} if funded_all else {q:prior.legality(stars)[q]['lawful'] for q in ('parity','nae')}
    physical=g.copy()
    nx.set_node_attributes(physical,{v:('physical',h[v]) for v in g},'color')
    active={v for v in g if h[v]}
    readable=any(v in active and u in active for v,u in g.edges)
    raw=[(w,tuple(sorted(set(g[w])&active))) for w in g]
    state=end.from_stars(stars)
    original_groups=end.proposals(state)
    paid=Counter(v for gr in original_groups for v in gr)
    funded=bool(active) and all(h[v]>=paid[v] for v in active)
    parts=list(nx.connected_components(prior.graph_of(state)))
    laws={}
    for law in ('parity','nae'):
        if law=='nae' and funded and len(parts)>1 and legal['nae']==legal['parity']:
            laws[law]=laws['parity'];continue
        entries=[]
        if legal[law] and funded:
            for comp in parts:
                rv=[(w,tuple(p for p in row if p in comp)) for w,row in raw]
                gr=tuple(group for group in original_groups if group[0] in comp)
                sub=end.restricted(state,comp)
                rr=inspect_component(sub,rv,gr,law,len(parts)==1,physical,readable,not funded_all)
                rr['root_holders']=sorted(comp)
                entries.append(rr)
        laws[law]={'legal':legal[law],'funded':legal[law] and funded,'parts':entries}
    return {**spec,'loose':h,'distinctions':sum(h)+len(spec['edges']),'recoverable_original':readable,
            'shortages':{v:paid[v]-h[v] for v in active if paid[v]>h[v]},'laws':laws}


def main():
    cli=argparse.ArgumentParser();cli.add_argument('--output',type=Path,default=OUT/'draws.jsonl')
    cli.add_argument('--limit',type=int);cli.add_argument('--skip',type=int,default=0)
    args=cli.parse_args()
    with args.output.open('w') as out:
        for i,spec in enumerate(draw_specs()):
            if i<args.skip: continue
            if args.limit is not None and i>=args.skip+args.limit: break
            print(json.dumps(source(spec),separators=(',',':')),file=out,flush=True)


if __name__=='__main__': main()
