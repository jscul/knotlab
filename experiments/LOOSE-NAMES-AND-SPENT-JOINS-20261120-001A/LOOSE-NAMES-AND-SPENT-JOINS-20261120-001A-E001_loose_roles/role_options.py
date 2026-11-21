"""Generate necessary age-free live-holder options from an indexed NAE table."""
from collections import Counter, defaultdict
from itertools import combinations, product
from math import lcm
from fractions import Fraction


def signed_table(n, rates):
    d=lcm(*(x.denominator for x in rates))
    c=[[d if i==j else 0 for j in range(n)] for i in range(n)]
    for (x,y),r in zip(combinations(range(n),2),rates,strict=True):
        c[x][y]=c[y][x]=d-2*r.numerator*(d//r.denominator)
    return d,c


def mono_triple(total,c,T):
    a,b,d=T
    return total+c[a][b]+c[a][d]+c[b][d]  # four times the probability times total.


def analyze(n,rates):
    total,c=signed_table(n,rates)
    names=set(range(n))
    forbidden=[frozenset(t) for t in combinations(range(n),3) if mono_triple(total,c,t)==0]
    equality=[]
    reasons=[]
    options={}
    for x in range(n):
        low=min(c[x])
        S=tuple(i for i in range(n) if i!=x and c[x][i]==low)
        H=frozenset((x,*S))
        F=tuple(sorted(y for y in H if y==x or all(c[x][z]==c[y][z] for z in names-{x,y})))
        U=tuple(sorted(H-set(F)))
        q,p=len(F),len(U)
        result=[]
        if low>=0 or len(S)<2: result.append('minimum/arity')
        if len(S)==2 and total+c[S[0]][S[1]]!=-2*low:
            result.append('all other two constant')
        if len(S)==3 and mono_triple(total,c,S)!=-4*low:
            result.append('all other three constant')
        if len(S)>3 and any(mono_triple(total,c,T)<=-4*low for T in combinations(S,3)):
            result.append('proper triple has strictly more constant mass')
        if not p: result.append('no inherited input')
        if any(t<H for t in forbidden):result.append('proper physical projection has forced triple')
        if p and q<max(1,3-p):result.append('arity/fresh floor')
        if {z for z in names-H if abs(c[x][z])>-low}:result.append('absolute minimum magnitude')
        if p in (1,2,3):
            if p==1: const=4*total
            elif p==2: const=2*(total+c[U[0]][U[1]])
            else:const=mono_triple(total,c,U)
            if const!=-4*((1<<q)-1)*low:result.append('conditional constant-input mass')
        if p in (1,2):
            # The mixed-versus-constant mean of the common input sign is
            # exactly the average of one or two input signs.
            if any(p*((1<<q)-1)*c[x][z]!=-sum(c[u][z] for u in U) for z in names-set(F)):
                result.append('unary/binary conditional row')
        if len(S)==3:
            for y in names-H:
                fourth=-4*c[x][y]-sum(c[u][y] for u in S)
                ij=tuple(combinations((*S,y),2))
                if any(total+sum(s[i]*s[j]*c[h][k] for (h,k),(i,j) in zip(ij,combinations(range(4),2)))+
                       s[0]*s[1]*s[2]*s[3]*fourth<0 for s in product((-1,1),repeat=4)):
                    result.append('inferred four-name atom negative')
                    break
        reasons.append(dict(name=x,minimum=low,support=sorted(H),fresh=F,inputs=U,exclusions=result))
        if not result:
            options[(tuple(sorted(H)),F)]=dict(support=tuple(sorted(H)),fresh=F,inputs=U)
    return total,c,forbidden,reasons,list(options.values())


def selections(options):
    def walk(at,occupied,picked):
        if picked:yield tuple(picked)
        for j in range(at,len(options)):
            opt=options[j];row=set(opt['support'])
            if not occupied & row:
                yield from walk(j+1,occupied|row,(*picked,j))
    yield from walk(0,set(),())


def derive_old_bounds(total,c,forced,options,indices,weight):
    N=set(range(len(c)))
    loose=set(x for k in indices for x in options[k]['fresh'])
    live_rows=[set(options[k]['support']) for k in indices]
    active_inputs={x:k for k in indices for x in options[k]['inputs']}
    role={}
    for x,k in active_inputs.items():
        opt=options[k]
        f=opt['fresh'][0]
        if weight=='uniform':
            values={z:c[x][z]-c[f][z] for z in N-{f,x}}
        else:
            values={z:c[x][z] for z in N-loose-{x}}
        low=min(values.values())
        maximum=sorted(z for z,v in values.items() if v==low and z not in loose and z not in opt['support'])
        if low>=0 or len(maximum)<2:return {}
        R=set()
        # A preceding holder may have had repeated source meetings, in which
        # case some exterior names can also minimize its measured row.
        for m in range(2,len(maximum)+1):
            for cs in combinations(maximum,m):
                H=frozenset((x,*cs))
                if any(t<H for t in forced):continue
                if len(H)==3 and H not in forced:continue
                if any(len(row & H)>1 for row in live_rows):continue
                R.add(H)
        if not R:return {}
        role[x]=R
    return role


def parent_covers(role):
    valid={}
    all_inputs=set(role)
    for x,R in role.items():
        valid[x]={K for K in R if all(K in role[y] for y in K&all_inputs)}
    if any(not R for R in valid.values()):return
    def walk(residual,ids,depth):
        if not residual:
            yield tuple(sorted((tuple(sorted(row)) for row in ids)))
            return
        x=min(residual,key=lambda y:(len(valid[y]),y))
        for K in sorted(valid[x],key=lambda row:(len(row),tuple(sorted(row)))):
            if not (K&all_inputs)<=residual:continue
            if any(depth[z]>=2 for z in K):continue
            depth.update(K)
            yield from walk(residual-K,(*ids,K),depth)
            depth.subtract(K)
    yield from walk(all_inputs,(),Counter())
