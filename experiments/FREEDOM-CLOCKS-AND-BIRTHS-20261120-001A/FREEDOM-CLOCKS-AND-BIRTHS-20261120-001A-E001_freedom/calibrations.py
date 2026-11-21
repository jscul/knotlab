"""Finite checks of ordinary/disjoint and compatible combined questions and competing rules."""
from collections import Counter
from fractions import Fraction as F
from itertools import combinations,product
from words import Question as Q,bits,compact,counts_table,disjoint_fibres,invert,op_moment,path_counts,pm,projector_reference,save,states,totals


def marginal(rows,indices):
    counts=[F(0) for _ in range(1<<len(indices))]
    for y,p in enumerate(rows):counts[compact(y,indices)]+=p
    return counts


def first():
    audits=[]
    for n in (1,2,3):
        full=(1<<n)-1;events=Counter()
        for raw in range(1,1<<(1<<n)):
            S=set(bits(raw));subtables={}
            for choice in product(range(3),repeat=n):
                T=[i for i,v in enumerate(choice) if v==1];U=[i for i,v in enumerate(choice) if v==2]
                questions=[Q(1<<i) for i in T]+[Q(read=1<<i) for i in U]
                law=counts_table(S,questions);fibres=disjoint_fibres(S,T,U)
                ref=projector_reference(S,n,questions)
                assert law==fibres==ref and min(law)>=0 and sum(law)==1
                subtables[choice]=(T+U,law);events['tables']+=1;events['probabilities']+=len(law)
            for choice,(seq,law) in subtables.items():
                for j in seq:
                    smaller=list(choice);smaller[j]=0
                    targetseq,expected=subtables[tuple(smaller)]
                    assert marginal(law,[seq.index(k) for k in targetseq])==expected
                    events['marginal_equalities']+=1
            events['supports']+=1
        audits.append(dict(n=n,counts=events))
    cases={}
    for label,h,law in [('ternary_parity',[[0,1,2]],'parity'),('ternary_nae',[[0,1,2]],'nae'),('meeting_nae',[[0,1,2],[2,3,4]],'nae'),('split_parity',[[0,1,2],[3,4,5]],'parity')]:
        S=states(h,law);n=max(map(max,h))+1;checks=[]
        for ch in product(range(3),repeat=n):
            t=sum(1<<i for i,v in enumerate(ch) if v==1);u=sum(1<<i for i,v in enumerate(ch) if v==2)
            numerator=sum(pm(u&x) for x in S if x^t in S)
            expected=projector_reference(S,n,[Q(t,u)])
            assert F(numerator,len(S))==expected[0]-expected[1]
            checks.append([t,u,numerator])
        cases[label]=dict(stars=h,law=law,allowed=len(S),moments=checks)
    assert sum(len(e['moments']) for e in cases.values())==1026
    contrasts={}
    for law in ('parity','nae'):
        S=states([[0,1,2]],law);erased=[sorted({compact(x,[j for j in range(3) if j!=i]) for x in S}) for i in range(3)]
        contrasts[law]=dict(words=sorted(S),erased=erased,free_words=[sorted(x for x in S if x^t in S) for t in range(8)],
                            plus_chance_by_mask=[str((1+op_moment(S,Q(t)))/2) for t in range(8)])
    save('single_questions.json',dict(exhaustive=audits,physical_cases=cases,K2_and_freedom=contrasts))


def combined():
    checks=[]
    for n in (1,2):
        prospective=[Q(t,z,s) for t in range(1<<n) for z in range(1<<n) for s in (False,True)]
        valid=[q for q in prospective if q.two_answers()];records=Counter()
        for a,b in product(prospective,repeat=2):
            fused=a.after(b)
            for x in range(1<<n):
                y,r=b.on(x);w,s=a.on(y);assert fused.on(x)==(w,r*s)
                records['ordered_actions']+=1
        for pair in product(valid,repeat=2):
            if not pair[0].compatible(pair[1]):
                try:totals(pair)
                except ValueError:records['incompatible_pairs_rejected']+=1;continue
                raise AssertionError('incompatible product accepted')
            for support in range(1,1<<(1<<n)):
                S=set(bits(support));law=counts_table(S,pair)
                assert law==projector_reference(S,n,pair)==path_counts(S,pair)
                assert min(law)>=0 and sum(law)==1
                assert marginal(law,[0])==counts_table(S,pair[:1]) and marginal(law,[1])==counts_table(S,pair[1:])
                records['full_tables']+=1;records['probabilities']+=4
        checks.append(dict(n=n,checks=records))
    save('combined_checks.json',checks)


def rivals():
    out={}
    for n,law in ((3,'parity'),(3,'nae'),(4,'nae')):
        S=states([range(n)],law);all_ones=(1<<n)-1
        D={t for t in range(1<<n) if all(x^t in S for x in S)}
        orbit=lambda x:min(x^d for d in D)
        reps=sorted(set(map(orbit,S)))
        sign=lambda x:-1 if len(reps)>1 and orbit(x)==orbit(1) else 1
        classes={'unsigned':lambda x,y:1,'orbit_dephased':lambda x,y:int(orbit(x)==orbit(y)),
                 'orbit_signed':lambda x,y:sign(x)*sign(y),'unrestricted_sign':lambda x,y:pm((x^y)&1)}
        rival_data={}
        for model,weight in classes.items():
            mom=lambda t,z:F(sum(pm(x&z)*weight(x,x^t) for x in S if x^t in S),len(S))
            certain=[t for t in sorted(D) if mom(t,0)==1];tables={};failures=[]
            for choice in product(range(3),repeat=n):
                names=[j for j,c in enumerate(choice) if c];tset=sum(1<<i for i,v in enumerate(choice) if v==1)
                zset=sum(1<<i for i,v in enumerate(choice) if v==2)
                integrals=[]
                for mask in range(1<<len(names)):
                    real_mask=sum(1<<names[j] for j in bits(mask));integrals.append(mom(tset&real_mask,zset&real_mask))
                rows=invert(integrals);assert all(v>=0 for v in rows) and sum(rows)==1
                if not tset:
                    direct=Counter(compact(x,names) for x in S)
                    assert rows==[F(direct[y],len(S)) for y in range(len(rows))]
                for j in names:
                    shorter=list(choice);shorter[j]=0;expected=tables[tuple(shorter)]
                    assert marginal(rows,[i for i,b in enumerate(names) if b!=j])==expected
                tables[choice]=rows
            # Elementary real combined questions in every single-mark pair of commuting signed queries share
            # the operator identities because every component is an ordinary real preparation.
            valid=[Q(t,z) for t in range(1<<n) for z in range(1<<n) if pm(t&z)==1]
            checks=0
            for a,b in product(valid,repeat=2):
                if not a.compatible(b):continue
                c=a.after(b)
                e=[F(1),mom(a.flip,a.read),mom(b.flip,b.read),(-1 if c.negative else 1)*mom(c.flip,c.read)]
                joint=invert(e);assert min(joint)>=0 and sum(joint)==1
                assert e[1]==joint[0]+joint[2]-joint[1]-joint[3]
                assert e[2]==joint[0]+joint[1]-joint[2]-joint[3]
                assert e[3]==joint[0]+joint[3]-joint[1]-joint[2];checks+=1
            for t in range(1,1<<n):
                seen=set();pair_data=[]
                for x in sorted(S):
                    r=min(x,x^t)
                    if r in seen:continue
                    seen.add(r);part=sorted(S&{x,x^t})
                    if len(part)==2:
                        val=weight(*part)
                        if val!=1:failures.append([t,part,val])
                    else:val=0
                    pair_data.append((len(part),val))
                assert mom(t,0)==sum(F(nw*val,len(S)) for nw,val in pair_data)
            change=[mom(1<<i,0) for i in range(n)]
            modelrow=dict(matching_global_free=certain,all_global_free=certain==sorted(D),single_means=list(map(str,change)),
                          all_flip_mean=str(mom(all_ones,0)),full_tables=len(tables),compatible_ordered_pairs=checks,
                          conditional_full_pairs_failing=len(failures),first_failed_pair=next(iter(failures),None))
            if n==3:modelrow['M']=str(mom(7,0)-sum(mom(1<<i,7^(1<<i)) for i in range(3)))
            rival_data[model]=modelrow
        naming=[]
        for v in range(1<<n):
            for overall in (1,-1):
                if all(sign(x)==overall*pm(v&x) for x in S):naming.append([v,overall])
        out[f'{law}{n}']=dict(words=sorted(S),free_group=sorted(D),orbits=[sorted(x for x in S if orbit(x)==r) for r in reps],
                              character_renamings_of_orbit_sign=naming,models=rival_data)
    S=states([[0,1,2]],'nae');chosen={1,6};amp={x:2 if x in chosen else 1 for x in S};norm=sum(v*v for v in amp.values())
    reweighted=[str(F(sum(amp[x]*amp[x^t] for x in S if x^t in S),norm)) for t in range(8)]
    def one_mark(preparations):
        xx=yy=zz=den=0
        for a,b in preparations:
            pair=complex(a).conjugate()*b;xx+=2*int(pair.real);yy+=2*int(pair.imag)
            aa=int((a.conjugate()*a).real);bb=int((b.conjugate()*b).real);zz+=aa-bb;den+=aa+bb
        return {k:str(F(v,den)) for k,v in (('X',xx),('Y',yy),('Z',zz))}
    orbits={min(x,x^7) for x in S}
    invariant_rates=sorted({F(sum(1 for x in S if min(x,x^7) in selected),len(S))
                            for r in range(len(orbits)+1) for selected in combinations(orbits,r)})
    assert F(5,6) not in invariant_rates
    out['weight_and_phase_controls']=dict(positive_nonuniform=dict(masses={str(x):w*w for x,w in amp.items()},change_means=reweighted),
                complement_invariant_deterministic_rates=list(map(str,invariant_rates)),
                unrestricted_one_bit={k:one_mark(preps) for k,preps in {
                    '+real':[(1,1)],'+imaginary':[(1,1j)],'-imaginary':[(1,-1j)],'diagonal':[(1,0),(0,1)]}.items()},
                singleton_without_fairness=dict(ordinary=1,full_pairs_vacuous=True,always_yes=1,calibrated_plus='1/2'))
    assert out['nae3']['models']['orbit_dephased']['M']=='1' and out['nae4']['character_renamings_of_orbit_sign']==[]
    save('rivals.json',out)
