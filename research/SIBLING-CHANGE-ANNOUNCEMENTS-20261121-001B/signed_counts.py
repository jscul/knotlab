"""Paid-word amplitudes for a preassigned sibling basis and all four erasure signs."""
from pathlib import Path
from collections import Counter
from itertools import product
from functools import cache
from fractions import Fraction as F

A=Path(__file__).resolve().parent
ROOT=A.parents[1]
NAMES=list(range(4))
WORDS=tuple(product((0,1),repeat=4))
TRIPLES=tuple(product((0,1),repeat=3))
ZERO=(0,0,0)


def legal(bits,law):
    return min(bits)!=max(bits) if law=='nae' else sum(bits)%2==0


def allowed_old(r,law):
    return tuple(int(legal(s,law) and all(legal((s[i+1],*r[3*i:3*i+3]),law) for i in range(3))) for s in WORDS)


@cache
def chars(vec):
    return tuple(sum((-1)**(h&s).bit_count()*v for s,v in enumerate(vec)) for h in range(16))


@cache
def forms(path):
    a,b=chars(path[:8]+(0,)*8),chars((0,)*8+path[8:])
    return tuple((i*i,i*j,j*j) for i,j in zip(a,b,strict=True))


def build_records(law,basis):
    old=[allowed_old(r,law) for r in product((0,1),repeat=9)]
    if basis=='nine_z':
        path=old
    elif basis=='mixed':
        path=[tuple(a+(-1)**b*c for a,c in zip(old[2*u],old[2*u+1],strict=True)) for u in range(256) for b in (0,1)]
    else:
        raise ValueError(basis)
    return tuple(zip(*(forms(p) for p in path),strict=True))


def add(x,y):
    return tuple(a+b for a,b in zip(x,y,strict=True))


def multiply(a,g):
    return tuple(a*v for v in g)


def sum_forms(seq):
    out=[0,0,0]
    for x in seq:
        for i in range(3):out[i]+=x[i]
    return tuple(out)


@cache
def score(law,g,c):
    p,t,q=g if c==0 else (g[2],g[1],g[0])
    if law=='nae':
        w=7*p+12*t+7*q
        two_v=p+t-4*q
    else:
        w=4*(p+q)
        two_v=-7*p+10*t-5*q
    return w,14*two_v-w


@cache
def matrix(law,g):
    f0,f1=[tuple(int(legal((s,*x),law)) for x in TRIPLES) for s in (0,1)]
    p,t,q=g
    return tuple(tuple((p*a+t*b)*aa+(t*a+q*b)*bb for aa,bb in zip(f0,f1,strict=True)) for a,b in zip(f0,f1,strict=True))


@cache
def signed_table(law,g):
    mat=matrix(law,g);pool=[]
    for s in range(8):
        moments=[sum((-1)**(x&j&(7^s)).bit_count()*mat[x][x^(s&j)] for x in range(8)) for j in range(8)]
        pool.append(tuple(sum((-1)**(a&j).bit_count()*moments[j] for j in range(8))/F(8) for a in range(8)))
    return tuple(pool)


def keys_for(cube,bits=15,ports=tuple(range(16))):
    # Integer h uses the same increasing physical bit names as the signed basis.
    parts={}
    for h in ports:
        group=h&bits
        if group not in parts:
            parts[group]=list(cube[h])
        else:
            parts[group]=[add(a,b) for a,b in zip(parts[group],cube[h],strict=True)]
    return {512*h+k:g for h,block in sorted(parts.items()) for k,g in enumerate(block)}


def select(source,mask):
    return sum_forms(multiply(v,source[k]) for k,v in mask.items() if v)
