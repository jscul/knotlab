"""Follow each original physical reader through six rounds, preserving every unresolved age."""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations
from math import gcd
from random import Random
import gzip
import json
import networkx as nx
from scipy.stats import beta
from words import OUT,save,three_score
from ordinary import J,advance,certify,elimination_width,gram,hall,hosted,raw_moments,singleton,three_count_rows
from three import full_certificate,specs


def rng(label,n,i,purpose):
    word=f'202611207319|{label}|{n}|{i}|{purpose}'
    return Random(int.from_bytes(sha256(word.encode()).digest(),'big'))


def fresh(label,n,i):
    rand=rng(label,n,i,'source');p=[rand.randrange(n) for _ in range(n-2)]
    g=nx.from_prufer_sequence(p);extra=None
    if label=='extra':
        extra=rand.choice([pair for pair in combinations(range(n),2) if not g.has_edge(*pair)]);g.add_edge(*extra)
    meetings=sorted(tuple(sorted(row)) for row in g.edges)
    return J.stars_from([max(3,g.degree(h)) for h in range(n)],meetings),dict(prufer=p,extra=extra)


def check(scores,complete):
    first=scores[0];present=[F(s) for s in scores if s is not None];start=F(first) if first is not None else None
    raw=[(F(a),F(b)) for a,b in zip(scores,scores[1:]) if a is not None and b is not None]
    fade=any(a>2>=b for a,b in raw);gain=any(a<=2<b for a,b in raw)
    values=[None if x is None else F(x) for x in scores]
    before=[];history_return=False;value_return=False
    for val in values:
        if val is None:continue
        if val>2 and any(a>2 and any(b<=2 for b in before[j+1:]) for j,a in enumerate(before)):
            history_return=True
        if any(a==val and any(b!=val for b in before[j+1:]) for j,a in enumerate(before)):value_return=True
        before.append(val)
    return dict(source_violation=None if start is None else start>2,complete=complete,fade_seen=fade,up_cross_seen=gain,
                return_seen=history_return,exact_score_return=value_return,
                gain_from_nonviolating=start is not None and start<=2 and any(v>2 for v in present),
                persistent=bool(complete and start is not None and start>2 and min(present)>2),
                increase=sum(a<b for a,b in raw),decrease=sum(a>b for a,b in raw),equal=sum(a==b for a,b in raw),
                reached_comparable_transitions=len(raw))


def ci(k,n):
    if not n:return None
    return [0 if not k else float(beta.ppf(.025,k,n-k+1)), 1 if k==n else float(beta.ppf(.975,k+1,n-k))]


def run():
    cases=[];registry={};votes=[];qs=singleton(3)
    def one(stars,marks,law):
        width=elimination_width(stars,marks) if law=='nae' else 0
        if width>10:return dict(censored_width=width)
        g=gram(stars,marks,law);values=list(map(int,g.flat));mult=gcd(*values);norm=[v//mult for v in values]
        rid=law+'-'+sha256(str(norm).encode()).hexdigest()[:20]
        if rid not in registry:
            den,m=raw_moments(g);rows=three_count_rows(g)
            if law=='parity':status=True;cuts=None;assert three_score(m)==0
            elif norm[0]==norm[-1]==0:
                certificate=hall(rows);status=certificate['local'];cuts=certificate['hall']
            else:status=full_certificate(rows,specs(qs))['local'];cuts=None
            registry[rid]=dict(gram=norm,rows=rows,moments=list(map(str,m)),M=str(three_score(m)),common=status,comparisons=cuts)
        return dict(table=rid,physical_unit=mult,elimination_width=width)
    def follow(label,n,index,source,origin,mode):
        case_id=f'{label}/{n}/{index}'
        for law in ('parity','nae'):
            assert all(certify(source,law));stages=[source];outcomes=[];stop='horizon'
            for age in range(6):
                outcome,next_stars=advance(stages[-1],law);outcomes.append(outcome)
                if next_stars is None:stop=outcome['status'];break
                stages.append(next_stars)
                if outcome['status']=='closed':stop='already closed';break
            case=dict(id=case_id,label=label,n=n,index=index,law=law,mode=mode,origin=origin,stages=stages,outcomes=outcomes,stop=stop)
            cases.append(case);cache={}
            def add(role,trial,anchor,age):
                if anchor is None:
                    votes.append(dict(case=case_id,law=law,role=role,trial=trial,ineligible=True));return
                holder,marks=anchor;measured=[]
                for j,frame in enumerate(stages[age:],age):
                    key=j,tuple(marks)
                    if key not in cache:cache[key]=one(frame,marks,law)
                    measured.append(cache[key])
                scores=[registry[r['table']]['M'] if 'table' in r else None for r in measured]
                complete=stop!='censored growth' and None not in scores
                votes.append(dict(case=case_id,law=law,role=role,trial=trial,anchor_age=age,holder=holder,marks=marks,
                                  records=measured,history=check(scores,complete)))
            if mode=='built':add('built',0,(0,source[0][:3]),0);continue
            for trial in (range(8) if mode=='host' else [index]):
                eligible=[j for j,s in enumerate(source) if len(s)==3];r=rng(label,n,trial,'mark')
                h=r.choice(eligible) if eligible else None
                add('source ternary',trial,None if h is None else (h,sorted(source[h])),0)
                if mode=='host' and h is None:
                    h=r.choice(list(range(len(source))));mark=rng(label,n,trial,'wide').choice(list(combinations(sorted(source[h]),3)))
                    add('wider source',trial,(h,list(mark)),0)
                if mode=='host':
                    born=[j for j in range(len(source),len(stages[1])) if len(stages[1][j])==3] if len(stages)>1 else []
                    h=rng(label,n,trial,'first').choice(born) if born else None
                    add('first newborn ternary',trial,None if h is None else (h,sorted(stages[1][h])),1)
    built={'single3':[[0,1,2]],'single4':[[0,1,2,3]],'three_mutual':[[0,1,3],[0,2,4],[1,2,5]],
           'three_arms':[[0,1,2],[0,3,4],[1,5,6],[2,7,8]]}
    for label,stars in built.items():follow(label,len(stars),0,stars,dict(built=True),'built')
    for label in ('tree','extra'):
        for n in range(4,9):
            for i in range(12):
                s,origin=fresh(label,n,i);follow(label,n,i,s,origin,'draw')
    for label,stars in hosted().items():follow(label,len(stars),0,stars,dict(fixed_explosive_host=True),'host')
    result=dict(seed=202611207319,cases=cases,tables=registry,votes=votes)
    (OUT/'histories.json.gz').write_bytes(gzip.compress((json.dumps(result,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0))
    describe(result)


def describe(raw):
    cases={(c['id'],c['law']):c for c in raw['cases']};groups={}
    for vote in raw['votes']:
        c=cases[vote['case'],vote['law']]
        for n in ([0,c['n']] if c['mode']=='draw' else [c['n']]):
            k=(c['label'],n,c['law'],vote['role']);groups.setdefault(k,[]).append((vote,c))
    summaries=[]
    for (label,n,law,role),row in groups.items():
        eligible=[(v,c) for v,c in row if not v.get('ineligible')];alln=len(eligible);ages=[]
        for age in range(7):
            vals=[];stopped=[];censored=0;reached=0
            for v,c in eligible:
                j=age-v['anchor_age']
                if j<0:continue
                if j<len(v['records']):
                    reached+=1;r=v['records'][j]
                    if 'table' in r:vals.append(raw['tables'][r['table']])
                    else:censored+=1
                elif c['stop'] in ('stall','already closed'):
                    r=v['records'][-1]
                    if 'table' in r:stopped.append(raw['tables'][r['table']])
            scores=[F(t['M']) for t in vals];pos=sum(s>2 for s in scores)
            ages.append(dict(age=age,reached=reached,exact=len(vals),censored_counting=censored,score_above_two=pos,
                             no_common=sum(not t['common'] for t in vals),min=str(min(scores)) if scores else None,
                             max=str(max(scores)) if scores else None,terminal_carried=len(stopped),
                             carried_above_two=sum(F(s['M'])>2 for s in stopped),interval=ci(pos,len(vals)) if n else None))
        counter=Counter();stops=Counter()
        for v,c in eligible:
            stops[c['stop']]+=1;h=v['history']
            for k,val in h.items():
                if val:counter[k]+=int(val)
            if h['complete'] and h['source_violation']:counter['fully_observed_initial_violations']+=1
            if h['complete'] and h['fade_seen']:counter['fully_observed_fades']+=1
        ev={k:[sum(bool(v['history'][k]) for v,c in eligible),sum(bool(v['history'][k]) or not v['history']['complete'] for v,c in eligible)]
            for k in ('fade_seen','return_seen','gain_from_nonviolating','exact_score_return')}
        summaries.append(dict(label=label,n=n,law=law,role=role,draws=len(row),eligible=alln,ages=ages,events=counter,
                              stop=stops,all_draw_event_bounds=ev))
    save('history_summary.json',summaries)
