"""Exact classical-word optimizers for the frozen acceptance constraint."""
from dataclasses import dataclass
from fractions import Fraction as F
from itertools import groupby
from math import lcm


@dataclass(frozen=True)
class Atom:
    label: str
    # (original nine-bit index, conditional probability of this observation given that word).
    preimage: tuple
    w: F
    v: F


def observations(w, v, view):
    groups = {}
    for i in range(512):
        s = f'{i:09b}'
        if view == 'full':
            keys = [(s,F(1))]
        elif view == 'eight':
            keys = [(s[:-1],F(1))]
        elif view == 'symmetric':
            triple_counts = sorted(s[j:j+3].count('1') for j in (0,3,6))
            keys = [(''.join(map(str,triple_counts)),F(1))]
        elif view == 'independent_tenth_bit':
            keys = [(s+'0',F(1,2)),(s+'1',F(1,2))]
        elif view == 'no_read':
            keys = [('empty observation',F(1))]
        else:
            raise ValueError(view)
        for k,p in keys:
            groups.setdefault(k,[]).append((i,p))
    return [Atom(key,tuple(pairs),sum(p*w[i] for i,p in pairs),sum(p*v[i] for i,p in pairs))
            for key,pairs in sorted(groups.items())]


def named_rule(atoms, choices):
    out = [F(0)]*512
    for item in atoms:
        for i,p in item.preimage:
            out[i] += choices.get(item.label,F(0))*p
    assert all(0<=x<=1 for x in out)
    return out


def optimize(w, v, delta, view, randomized):
    atoms=observations(w,v,view)
    d={a.label:a.v-delta*a.w for a in atoms}
    good=[a for a in atoms if a.w and d[a.label]>=0]
    bad=[a for a in atoms if a.w and d[a.label]<0]
    budget=sum((d[a.label] for a in good),F(0))
    choice={a.label:F(1) for a in good}
    if randomized:
        order=sorted(bad,key=lambda a:(-a.w/(-d[a.label]),a.label))
        left=budget
        cutoff=F(0)
        for a in order:
            price=-d[a.label]
            f=min(F(1),left/price)
            choice[a.label]=f
            left-=f*price
            if f<1:
                cutoff=a.w/price
                break
        cap=sum(max(F(0),a.w+cutoff*d[a.label]) for a in atoms)
        cert={'method':'continuous upper certificate: sum max(0,w+lambda*(v-delta*w))',
              'multiplier':cutoff,'upper_bound_w':cap,'positive_surplus':budget,
              'unused_surplus':left,
              'boundary_labels':[a.label for a in atoms if a.w and a.w+cutoff*d[a.label]==0],
              'strictly_positive_dual_support':[a.label for a in atoms if a.w and a.w+cutoff*d[a.label]>0]}
    else:
        # Choosing every nonnegative-surplus, positive-weight observation is dominant.
        den=lcm(*(x.denominator for x in d.values()))
        cap=int(den*budget)
        best={0:(F(0),())}
        for a in bad:
            cost=int(-den*d[a.label])
            if cost>cap:
                continue
            old=list(best.items())
            for used,(score,labels) in old:
                k=used+cost
                if k>cap:
                    continue
                cand=(score+a.w,labels+(a.label,))
                prev=best.get(k)
                if prev is None or cand[0]>prev[0] or (cand[0]==prev[0] and cand[1]<prev[1]):
                    best[k]=cand
        extra, chosen = min(best.values(),key=lambda row:(-row[0],row[1]))
        choice.update((s,F(1)) for s in chosen)
        cap_w=sum(a.w for a in good)+extra
        cert={'method':'exact 0/1 recurrence on total negative surplus cost, nonnegative offers dominant',
              'surplus_integer_scale':den,'capacity':cap,
              'least_negative_cost':min((int(-den*d[a.label]) for a in bad),default=None),
              'feasible_budget_states':{k:{'maximum_extra_weight':value,'chosen':labs}
                                        for k,(value,labs) in sorted(best.items())},
              'dominant_labels':[a.label for a in good],'upper_bound_w':cap_w}
    f=named_rule(atoms,choice)
    value=sum(p*q for p,q in zip(f,w))
    score=sum(p*q for p,q in zip(f,v))
    assert score>=delta*value and value==cert['upper_bound_w']
    return {'view':view,'randomized':randomized,'target':delta,'available_label_count':len(atoms),
            'eligible_population_weight':sum(w),'mask':f,'attained_weight':value,
            'raw_witness':score,'conditional_I':score/value if value else None,
            'optimum_certificate':cert,'positive_observation_acceptance':{k:v for k,v in sorted(choice.items()) if v}}
