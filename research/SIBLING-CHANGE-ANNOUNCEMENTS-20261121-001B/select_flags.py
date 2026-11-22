"""Exact labelled selection with one pooled surplus constraint. Weights and 28 times surplus are integer."""
from array import array
from collections import defaultdict
from fractions import Fraction as F
from hashlib import sha256
from math import gcd
from functools import reduce
import sys


def rates(records,method):
    assert all(int(w)==w and int(d)==d for w,d in records.values())
    records={k:(int(w),int(d)) for k,(w,d) in records.items()}
    good={};losses=defaultdict(list); credit=0
    for key,(w,d) in sorted(records.items()):
        if w and d>=0:
            good[key]=1
            credit+=d
        elif w:
            losses[w,-d].append(key)
    if method=='randomized':
        # Ratio is w/(-28d) in the scaled convention of this routine.
        ranked=sorted(((-F(w,k),lab,k) for (w,k),labs in losses.items() for lab in labs))
        left=credit; mu=F(0)
        for ratio,i,k in ranked:
            f=min(F(1),F(left,k))
            if f:good[i]=f
            left-=f*k
            if f<1:mu=-ratio;break
        bound=sum(max(0,w+mu*d) for w,d in records.values())
        cert={'mu_for_28_times_surplus':mu,'lower_equals_upper_raw':bound,
              'sum_of_all_positive_scaled_surplus':credit,'unused_scaled_surplus':left,
              'boundary_positive_weight_records':sum(w>0 and w+mu*d==0 for w,d in records.values())}
    elif method=='deterministic':
        # Group identical score/cost items. Each binary chunk is still exchangeable over its concrete labels.
        divisor=reduce(gcd,[k for w,k in losses] or [1])
        B=credit//divisor
        best=[-1]*(B+1);best[0]=0
        flags=[];updates=[]
        for (w,k),ids in sorted(losses.items(),key=lambda t:(t[0][1],-t[0][0],t[1][0])):
            p=k//divisor
            num=min(len(ids),B//p)
            start=0; part=1
            while num:
                q=min(num,part); num-=q;part*=2
                cost=q*p
                changes=bytearray(B+1)
                # Descending cost visits each optional chunk just once.
                for total in range(B,cost-1,-1):
                    previous=best[total-cost]
                    if previous>=0 and previous+q*w>best[total]:
                        best[total]=previous+q*w
                        changes[total]=1
                flags.append(changes)
                updates.append((cost,ids[start:start+q]))
                start+=q
        state=best.index(max(best));end=state
        for (k,ids),flags0 in zip(reversed(updates),reversed(flags),strict=True):
            if flags0[state]:
                good.update(dict.fromkeys(ids,1));state-=k
        assert state==0
        base=sum(records[i][0] for i,(_,d) in records.items() if d>=0)
        bound=base+int(max(best))
        digest_values=array('q',best)
        assert digest_values.itemsize==8
        if sys.byteorder!='little':digest_values.byteswap()
        cert={'scale':'d in this certificate is 28 times the unnormalized excess','starting_scaled_surplus':credit,
              'gcd_of_negative_costs':divisor,'capacity_in_gcd_units':B,'used_capacity_in_gcd_units':end,
              'binary_0_1_chunks_evaluated':len(updates),'best_revenue_from_negative_records':int(max(best)),
              'terminal_dp_digest_little_endian_int64':sha256(digest_values.tobytes()).hexdigest(),
              'negative_item_types_weight_scaled_cost_multiplicity':[[w,k,len(ids)] for (w,k),ids in sorted(losses.items())],
              'lower_equals_upper_raw':bound}
    else:
        raise ValueError(method)
    w=sum(p*records[i][0] for i,p in good.items())
    scaled=sum(p*records[i][1] for i,p in good.items())
    assert w==bound and scaled>=0
    return {'mask':dict(sorted(good.items())),'weight':w,'scaled_surplus':scaled,'I':(w+scaled)/F(28*w) if w else None,'certificate':cert}
