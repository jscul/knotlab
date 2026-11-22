"""Contract one fixed sibling change at a reached first four-place birth."""
from collections import Counter
from fractions import Fraction as F
from functools import cache
from itertools import product

B3=tuple(product((0,1),repeat=3))
B4=tuple(product((0,1),repeat=4))
B8=tuple(product((0,1),repeat=8))
ZERO=(0,0,0)


def integer(bits):
    return sum(b<<(len(bits)-1-i) for i,b in enumerate(bits))


def lawful(bits,law):
    return sum(bits)%2==0 if law=='parity' else min(bits)!=max(bits)


@cache
def focal(law):
    return tuple(tuple(int(lawful((b,*x),law)) for x in B3) for b in (0,1))


def plus(*forms):
    return tuple(sum(v) for v in zip(*forms,strict=True))


def times(w,form):
    return tuple(w*i for i in form)


def outer(a,b):
    return (a*a,a*b,b*b)


@cache
def matrix(law,form):
    u,v=focal(law); p,g,q=form
    return tuple(tuple(p*u[x]*u[y]+g*(u[x]*v[y]+v[x]*u[y])+q*v[x]*v[y] for y in range(8)) for x in range(8))


@cache
def table(law,form):
    gram=matrix(law,form)
    out=[]
    for s in range(8):
        moments=[sum((-1)**(i&j&(7^s)).bit_count()*gram[i][i^(s&j)] for i in range(8)) for j in range(8)]
        out.append(tuple(sum((-1)**(a&j).bit_count()*moments[j] for j in range(8))/F(8) for a in range(8)))
    return tuple(out)


@cache
def quantities(law,form,c):
    t=table(law,form)
    w=sum(t[0])
    v=(sum(t[7][a] for a in range(8) if a.bit_count()>=2)-t[0][7*c]
       -sum(t[s][a] for s in (1,2,4) for a in range(8) if a&s and a&(7^s)!=(7*c)&(7^s)))
    if law=='nae':
        p,g,q=form if c==0 else tuple(reversed(form))
        assert w==7*p+12*g+7*q and 2*v==p+g-4*q
    return w,v


def chars(values):
    return tuple(sum((-1)**(h&s).bit_count()*v for s,v in enumerate(values)) for h in range(16))


def birth_rows(law,j=8):
    """The two possible ordinary completions can have overlapping paid histories."""
    rows=[]
    for u in B8:
        legs=[]
        for t in (0,1):
            r=(*u[:j],t,*u[j:])
            # Old focal orientation and allowed sibling triples jointly determine each path.
            paid=[int(lawful(s,law) and all(lawful((s[k+1],*r[3*k:3*k+3]),law) for k in range(3))) for s in B4]
            legs.append(paid)
        for b in (0,1):
            k=[left+(-1)**b*right for left,right in zip(*legs,strict=True)]
            d=(sum(x*x for x in k[:8]),0,sum(x*x for x in k[8:]))
            s0,s1=chars(k[:8]+[0]*8),chars([0]*8+k[8:])
            q=tuple(outer(y,z) for y,z in zip(s0,s1,strict=True))
            tagged_d=(sum(sum(x*x for x in pair[:8]) for pair in legs),0,
                      sum(sum(x*x for x in pair[8:]) for pair in legs))
            tags=[]
            for left in legs:
                s0t,s1t=chars(left[:8]+[0]*8),chars([0]*8+left[8:])
                tags.append([outer(y,z) for y,z in zip(s0t,s1t,strict=True)])
            qt=tuple(plus(v,w) for v,w in zip(*tags,strict=True))
            assert plus(*q)==times(16,d) and plus(*qt)==times(16,tagged_d)
            rows.append({'retained':d,'clean':q[0],'h':q,'sibling_tag_retained':tagged_d,'sibling_tag_h':qt,
                         'paid_path_amplitudes':k})
        assert plus(rows[-1]['retained'],rows[-2]['retained'])==times(2,tagged_d)
        assert all(plus(x,y)==times(2,z) for x,y,z in zip(rows[-1]['h'],rows[-2]['h'],qt,strict=True))
    return rows


def form_at(row,field,h=0):
    return row[field][h] if field in ('h','sibling_tag_h') else row[field]


def select(rows,mask,field,h=0):
    c=Counter()
    for r,f in zip(rows,mask,strict=True):
        if f: c[form_at(r,field,h)]+=f
    return tuple(sum(v*coef[k] for coef,v in c.items()) for k in range(3))


def zerolabel(i):
    return f'{i//2:08b}/{"-" if i%2 else "+"}'


def histogram(law,rows,mode,c=0):
    counts=Counter((quantities(law,r[mode],c),r[mode]) for r in rows)
    return [{'count':n,'weight':w,'wI':v,'form':f} for ((w,v),f),n in sorted(counts.items())]
