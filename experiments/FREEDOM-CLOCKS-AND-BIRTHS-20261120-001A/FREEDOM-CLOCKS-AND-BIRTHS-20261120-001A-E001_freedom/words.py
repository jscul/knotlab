"""Exact answer probabilities made from pairs of unsigned ordinary words."""
from collections import Counter,defaultdict
from dataclasses import dataclass
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import hashlib
import json
import os

for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
OUT=ROOT/'artifacts'/HERE.parent.name/HERE.name
OUT.mkdir(parents=True,exist_ok=True)


def save(name,obj):
    (OUT/name).write_text(json.dumps(obj,sort_keys=True,separators=(',',':'))+'\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bits(mask):
    return [i for i in range(mask.bit_length()) if mask>>i & 1]


def compact(x,marks):
    return sum(((x>>i)&1)<<j for j,i in enumerate(marks))


def pm(x):
    return -1 if x.bit_count()%2 else 1


def states(stars,law):
    masks=[sum(1<<i for i in h) for h in stars];n=max(map(max,stars))+1
    if law=='parity':return frozenset(x for x in range(1<<n) if all(pm(x & v)==1 for v in masks))
    return frozenset(x for x in range(1<<n) if all((x & v) not in (0,v) for v in masks))


@dataclass(frozen=True)
class Question:
    flip:int=0
    read:int=0
    negative:bool=False

    def on(self,x):
        return x ^ self.flip,(-1 if self.negative else 1)*pm(self.read & x)

    def after(self,earlier):
        return Question(self.flip^earlier.flip,self.read^earlier.read,
                        self.negative^earlier.negative^bool((self.read&earlier.flip).bit_count()%2))

    def two_answers(self):
        return pm(self.flip&self.read)==1

    def compatible(self,other):
        return self.after(other)==other.after(self)


def op_moment(S,op):
    vote=[op.on(x) for x in S];return F(sum(sign for y,sign in vote if y in S),len(S))


def totals(questions):
    for i,q in enumerate(questions):
        if not q.two_answers() or any(not q.compatible(other) for other in questions[:i]):
            raise ValueError('simultaneous binary queries must be commuting involutions')
    ops=[Question()]
    for q in questions:ops+= [q.after(old) for old in ops]
    return ops


def invert(moments):
    terms=len(moments)
    return [sum(pm(out & mask)*v for mask,v in enumerate(moments))/terms for out in range(terms)]


def counts_table(S,questions):
    return invert([op_moment(S,op) for op in totals(questions)])


def path_counts(S,questions):
    """For each endpoint count agreeing and opposing paths, then square the imbalance."""
    ops=totals(questions);terms=len(ops);rows=[]
    for out in range(terms):
        count=defaultdict(lambda:[0,0])
        for subset,op in enumerate(ops):
            for x in S:
                y,s=op.on(x);count[y][int(pm(out&subset)*s<0)]+=1
        rows.append(F(sum((a-b)**2 for a,b in count.values()),terms**2*len(S)))
    return rows


def projector_reference(S,n,questions):
    """Independent unnormalized application of each I +/- O on an ordinary word array."""
    active=[[int(x in S) for x in range(1<<n)]]
    for q in questions:
        moved=[]
        for f in active:
            v=[0]*len(f)
            for x,w in enumerate(f):
                y,s=q.on(x);v[y]=s*w
            moved.append(v)
        active=[[a+s*b for a,b in zip(row,shifted)] for s in (1,-1) for row,shifted in zip(active,moved)]
    return [F(sum(w*w for w in f),len(S)*4**len(questions)) for f in active]


def disjoint_fibres(S,flips,reads):
    """Distribution on (ordinary bits, change signs) by positive/negative word counts."""
    fmask=sum(1<<i for i in flips);sections=defaultdict(list)
    for x in S:sections[x & ~fmask].append(compact(x,flips))
    result=Counter();norm=(1<<len(flips))*len(S)
    for h,words in sections.items():
        z=compact(h,reads)
        for out in range(1<<len(flips)):
            plus=sum(pm(out&x)==1 for x in words);minus=len(words)-plus
            result[z<<len(flips)|out]+=(plus-minus)**2
    return [F(result[x],norm) for x in range(1<<(len(flips)+len(reads)))]


def three_score(m):
    return m[0]-sum(m[1:])
