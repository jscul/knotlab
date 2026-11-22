"""Independent check by private-bank counts and the number of ones in G's new word."""
from collections import Counter, defaultdict
from fractions import Fraction as F
from itertools import product
from math import comb
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'SUCCESSOR-RECEIPT-20261122-001'))
import weigh_successor as previous


def receiver_law(law, h, q, width):
    """Return probabilities of each weight class; words in a class are equally likely."""
    if law == 'parity':
        return {k:F(comb(width,k),2**(width-1)) for k in range(width+1) if (h+q+k)%2==0}
    equal = h==q
    return {k:F(comb(width,k)-int(equal and k==h*width), 2**width-int(equal)) for k in range(width+1)}


def chance_paid_one(case, intention, n):
    """Condition on n ones, before seeing any labeled K value or the future G word."""
    before=F(n,3)
    majority=int(n>=2)
    if case in ('blind','pair_swap','random_unlike'):
        return before
    if case=='cross_pair':
        return F(majority) if intention else before
    if case=='subset_writer':
        return F(majority) if intention==majority else before
    if case=='address_writer':
        return F(intention) if n in (1,2) else before
    if case=='ready_pair':
        return F(intention)
    raise ValueError(case)


def report(law):
    data=previous.source_data()
    births,_,_,_,_,h,k,g,hbit,_,_,extra,_=previous.reconstruct(data,law)
    old=dict(zip(data['original_name_order'], map(int,data['common_original_words'][law]),strict=True))
    width=len(g.fresh)
    assert len(k.fresh)==3
    # Use only older inputs of K and H's paid value/background. Then sum by K bank count.
    background=[extra,*[v for v in h.fresh if v!=hbit]]
    targets=tuple([*k.paid,hbit,*background])
    before,_=previous.distribution(law,births,old,targets,{})
    by_group=defaultdict(Counter)
    for record, prior in before.items():
        incoming=record[:len(k.paid)]
        hvalue=record[len(k.paid)]
        calibrated=not any(record[len(k.paid)+1:])
        allowed={n:comb(3,n) for n in range(4) if (
            (sum(incoming)+n)%2==0 if law=='parity' else 0<sum(incoming)+n<len(incoming)+3)}
        denom=sum(allowed.values())
        for n,number in allowed.items():
            mass=prior*number/denom
            by_group['all'][(hvalue,n)]+=mass
            if calibrated: by_group['H_zero_background'][(hvalue,n)]+=mass
    assert sum(by_group['all'].values())==1
    result={}
    for cohort,table in by_group.items():
        base=sum(table.values())
        group={}
        for case in ('blind','pair_swap','random_unlike','cross_pair','subset_writer','address_writer','ready_pair'):
            reads={r:[Counter(),Counter()] for r in ('fresh_only','fresh_plus_h')}
            totals=[Counter(),Counter()]
            for (hvalue,n), mass in table.items():
                if case=='ready_pair':
                    # One specified oriented 01 inside a three-bit bank. It occurs on one of three assignments at n=1 or 2.
                    mass *= F(1,3) if n in (1,2) else 0
                if not mass: continue
                for m in (0,1):
                    p=chance_paid_one(case,m,n)
                    for q,weight in ((0,1-p),(1,p)):
                        if not weight: continue
                        totals[m]['paid_'+str(q)]+=mass*weight
                        for count,obs in receiver_law(law,hvalue,q,width).items():
                            if not obs: continue
                            value=mass*weight*obs
                            reads['fresh_only'][m][str(count)]+=value
                            reads['fresh_plus_h'][m][str(count)+'|'+str(hvalue)]+=value
            population=sum(totals[0].values())
            assert population==sum(totals[1].values())
            group[case]={'population':str(population),'paid_one':[str(row['paid_1']/population) for row in totals]}
            for typ,arms in reads.items():
                left,right=arms
                keys=set(left)|set(right)
                correct=sum(max(left[k],right[k]) for k in keys)/(2*population)
                certain=sum(left[k]+right[k] for k in keys if min(left[k],right[k])==0)/(2*population)
                assert sum(left.values())==sum(right.values())==population
                group[case][typ]={'accuracy':str(correct),'certifying_mass':str(certain)}
        full=sum(w for (hvalue,n),w in table.items() if n in (1,2))
        assert F(group['ready_pair']['population'])==full/3
        for cs in ('blind','random_unlike','pair_swap'):
            assert F(group[cs]['fresh_only']['accuracy'])==F(group[cs]['fresh_plus_h']['accuracy'])==F(1,2)
        result[cohort]={'population':str(base),'private_bank_mixed':str(full/base),'designated_pair_mixed':str(2*full/(3*base)),'cases':group}
    return result


if __name__=='__main__':
    answers={law:report(law) for law in ('parity','nae')}
    (HERE/'by_count.json').write_text(json.dumps(answers,indent=2)+'\n')
    for law,res in answers.items():
        r=res['all']
        print(law,r['private_bank_mixed'],r['designated_pair_mixed'])
        for name,row in r['cases'].items():
            print(name,row['paid_one'],{k:(row[k]['accuracy'],row[k]['certifying_mass']) for k in ('fresh_only','fresh_plus_h')})
