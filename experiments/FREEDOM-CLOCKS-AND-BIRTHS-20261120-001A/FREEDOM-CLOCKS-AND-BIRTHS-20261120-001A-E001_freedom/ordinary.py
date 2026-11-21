"""Physical ordinary growth and finite integer counts used by the freedom study."""
from collections import Counter
from fractions import Fraction as F
from importlib import util
from itertools import product
from math import gcd
from pathlib import Path
import sys
from words import ROOT,pm


def experiment(ticket):
    return next((ROOT/'experiments'/ticket).glob('*-E001_*'))


previous=experiment('THREE-READERS-AND-GROWTH-20261120-001A')
sys.path.insert(0,str(previous))
from completions import gram,nea_contraction
from holdings import J,certify,hosted
from growth import observe,rule_for
from exact_counts import NotAllEqualSupport,Parity
from three import rows_for,singleton
from certificates import hall


def module_at(name,path):
    spec=util.spec_from_file_location(name,path);module=util.module_from_spec(spec)
    sys.modules[name]=module;spec.loader.exec_module(module);return module


end=module_at('freedom_end_operator',experiment('ORDINARY-DYNAMICS-20261120-001A')/'end_operator.py')


def advance(stars,law,cap=True):
    plan=end.step(end.from_stars(stars),law,48 if cap else None)
    if plan.status=='cap':return dict(status='censored growth',reason='more than 48 births',lower=plan.planned_births_lower),None
    if plan.status=='closed':return dict(status='already closed'),None
    if plan.status=='extend' and cap and (len(stars)+len(plan.parents)>180 or 1+max(map(max,stars))+sum(plan.fresh)>600):
        return dict(status='censored growth',reason='stage size',knots=len(stars)+len(plan.parents),
                    distinctions=1+max(map(max,stars))+sum(plan.fresh)),None
    stage=J.S.from_junctions(stars)
    result=observe(stage,law,rule_for(law))
    if plan.status=='stall':
        assert result['status']=='stall';return dict(status='stall',shortages=result['shortages']),None
    assert result['status'] in ('grown','closed')
    owner={}
    for h,row in enumerate(stars):
        for b in row:owner.setdefault(b,[]).append(h)
    for birth in result['new']:
        inherited=[b for b in birth['places'] if b in owner]
        assert all(len(owner[b])==1 for b in inherited)
        birth['parent_names']=sorted(owner[b][0] for b in inherited)
        assert len(inherited)==birth['parents'] and len(birth['places'])-len(inherited)==birth['fresh']
    native=Counter((tuple(v['parent_names']),v['fresh']) for v in result['new'])
    independent=Counter((tuple(sorted(parents)),fresh) for parents,fresh in zip(plan.parents,plan.fresh))
    assert native==independent
    return result,[list(s) for s in stage.bits_of]


def elimination_width(stars,marks):
    """Follow the existing contraction's exact scope order without allocating a tensor."""
    marks=set(marks);owners={};border=set()
    for k,s in enumerate(stars):
        inside=any(b in marks for b in s);outside=any(b not in marks for b in s)
        if inside and outside:border.add(k)
        for b in s:
            if b not in marks:owners.setdefault(b,[]).append(k)
    live={h for row in owners.values() for h in row}
    scopes=[{h} for h in live]+[set(row) for row in owners.values() if len(row)>1]
    remaining=live-border;largest=max([len(border),1])
    while remaining:
        nbr={v:{v} for v in remaining}
        for sc in scopes:
            for v in sc&remaining:nbr[v].update(sc)
        v=min(remaining,key=lambda v:(len(nbr[v]),v));joined=nbr[v]
        largest=max(largest,len(joined));scopes=[s for s in scopes if v not in s]+[joined-{v}];remaining.remove(v)
    return largest


def raw_moments(g):
    den=sum(int(g[x,x]) for x in range(8))
    def read(t,z):return F(sum(pm(x&z)*int(g[x,x^t]) for x in range(8)),den)
    return den,[read(7,0),read(1,6),read(2,5),read(4,3)]


def three_count_rows(g):
    n=sum(int(g[x,x]) for x in range(8))
    result=[]
    for questions in product((0,1),repeat=3):
        reads=sum(q<<i for i,q in enumerate(questions))
        moments=[]
        for subset in range(8):
            t=subset & (7^reads);z=subset&reads
            moments.append(sum(pm(x&z)*int(g[x,x^t]) for x in range(8)))
        counts=[sum(pm(a&subset)*m for subset,m in enumerate(moments)) for a in range(8)]
        den=8*n;common=gcd(den,*counts)
        assert min(counts)>=0 and sum(counts)==den
        result.append(dict(settings=list(questions),numerators=[c//common for c in counts],denominator=den//common))
    return result
