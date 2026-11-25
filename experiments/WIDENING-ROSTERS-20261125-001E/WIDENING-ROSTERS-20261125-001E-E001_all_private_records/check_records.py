"""Exact product and proper-arm tests on actual physical holder records."""
from collections import defaultdict, deque
from functools import lru_cache
from hashlib import sha256
from itertools import chain
from pathlib import Path
import gzip
import json

from pysat.solvers import Solver


def rank(vectors):
    basis={}
    for v in vectors:
        while v:
            p=v.bit_length()-1
            if p not in basis:
                basis[p]=v
                break
            v ^= basis[p]
    return len(basis)


class EvenStage:
    def __init__(self,rules):
        pivots={}
        universe=set(chain.from_iterable(rules))
        for row in rules:
            v=sum(1<<x for x in row)
            while v:
                p=v.bit_length()-1
                if p not in pivots:
                    pivots[p]=v
                    break
                v ^= pivots[p]
        self.coordinates={}
        next_free=0
        for x in sorted(universe):
            if x not in pivots:
                self.coordinates[x]=1<<next_free
                next_free+=1
            else:
                q=pivots[x] ^ (1<<x)
                value=0
                while q:
                    bit=q & -q
                    value ^= self.coordinates[bit.bit_length()-1]
                    q ^= bit
                self.coordinates[x]=value

    @lru_cache(maxsize=30000)
    def dimension(self,coords):
        return rank(self.coordinates[x] for x in coords)

    def check(self,a,b,c):
        contact=frozenset([c])
        dimension=self.dimension
        dc=dimension(contact)
        da,db=dimension(a),dimension(b)
        dac,dbc=dimension(a|contact),dimension(b|contact)
        dab=dimension(a|b|contact)
        return dab==dac+dbc-dc,dac<da+dc,dbc<db+dc


def minimal_clauses(clauses):
    small=[]
    for clause in sorted(set(clauses),key=lambda c:(len(c),tuple(sorted(c)))):
        if not any(p<=clause for p in small):
            small.append(clause)
    return set(small)


class NotAllEqualStage:
    def __init__(self,rules):
        self.rules=list(map(frozenset,rules))
        at=defaultdict(list)
        for j,row in enumerate(rules):
            for v in row:
                at[v].append(j)
        self.at=dict(at)
        self.degrees={v:len(js) for v,js in at.items()}
        self.initial=[v for v,js in at.items() if len(js)==1]
        pos=[[v+1 for v in row] for row in rules]
        self.solver=Solver(name='cadical195',bootstrap_with=[c for p in pos for c in (p,[-v for v in p])])
        assert self.solver.solve()

    @lru_cache(maxsize=5000)
    def projection(self,keep):
        # A private hidden place can satisfy its sole surviving constraint for any other choices.
        live=set(range(len(self.rules)))
        degree=self.degrees.copy()
        q=deque(v for v in self.initial if v not in keep)
        while q:
            v=q.popleft()
            if degree[v]!=1:
                continue
            j=next(j for j in self.at[v] if j in live)
            live.remove(j)
            for w in self.rules[j]:
                degree[w]-=1
                if degree[w]==1 and w not in keep:
                    q.append(w)
        clauses=set()
        hidden=set()
        for j in live:
            row=self.rules[j]
            p=frozenset(x+1 for x in row)
            clauses.update([p,frozenset(-x for x in p)])
            hidden.update(x+1 for x in row if x not in keep)
        # Existential Boolean elimination by resolution, discarding only tautologies or subsumed clauses.
        while hidden:
            incidence=defaultdict(lambda:[0,0])
            for clause in clauses:
                for lit in clause:
                    if abs(lit) in hidden:
                        incidence[abs(lit)][lit<0]+=1
            if not incidence:
                break
            var=min(incidence,key=lambda v:(incidence[v][0]*incidence[v][1],v))
            hidden.remove(var)
            pos=[p for p in clauses if var in p]; neg=[p for p in clauses if -var in p]
            if len(pos)*len(neg)>100000 or len(clauses)>10000:
                raise OverflowError('exact resolution budget')
            clauses.difference_update(pos,neg)
            for p in pos:
                for n in neg:
                    r=(p|n)-{var,-var}
                    if not any(-lit in r for lit in r):
                        clauses.add(r)
            clauses=minimal_clauses(clauses)
        return tuple(clauses)

    @lru_cache(maxsize=30000)
    def proper(self,arm,c):
        # A proper attachment permits some arm at one c and forbids it at the other.
        for clause in self.projection(arm | {c}):
            for lit in clause:
                if abs(lit)==c+1:
                    pins=[-x for x in clause if x!=lit]+[lit]
                    if self.solver.solve(assumptions=pins):
                        return True
        return False

    def check(self,a,b,c):
        product=True
        for clause in self.projection(a|b|{c}):
            left=[-lit for lit in clause if abs(lit)-1 in a]
            right=[-lit for lit in clause if abs(lit)-1 in b]
            if not left or not right:
                continue
            for contact in (c+1,-c-1):
                if contact in clause:
                    continue
                if self.solver.solve(assumptions=[contact]+left) and self.solver.solve(assumptions=[contact]+right):
                    product=False
                    break
            if not product:
                break
        return product,self.proper(a,c),self.proper(b,c)


def setup(params):
    global root, grouped, timing
    root=Path(params['inputs'])
    grouped=defaultdict(list)
    for line in (root/'requests.jsonl').read_text().splitlines():
        r=json.loads(line);grouped[r['law'],r['system']].append(r)
    timing=params.get('timing','no')=='yes'


def cases():
    by_key=sorted(grouped)
    if timing:
        # Cover the widest distinct records, largest systems, largest batches, and first ordinary systems under both laws.
        keys=set()
        for law in ('nae','parity'):
            population=[k for k in by_key if k[0]==law]
            for criterion in (lambda k:max(r['width'] for r in grouped[k]), lambda k:grouped[k][0]['knots'],lambda k:len(grouped[k])):
                keys.update(sorted(population,key=criterion,reverse=True)[:2])
            keys.add(population[0])
        by_key=sorted(keys)
    for law,system in by_key:
        yield law+'-'+system, (law,system)


def run(case_id,payload):
    law,system=payload
    data=gzip.decompress((root/'systems'/(system+'.json.gz')).read_bytes())
    assert sha256(data).hexdigest()==system
    rules=json.loads(data)
    checker=EvenStage(rules) if law=='parity' else NotAllEqualStage(rules)
    judgements=[]
    population=grouped[law,system]
    if timing and len(population)>64:
        ordered=sorted(population,key=lambda r:(r['width'],r['u'],r['v'],r['c']))
        population=[ordered[i*(len(ordered)-1)//63] for i in range(64)]
    for r in population:
        u,v,c=r['u'],r['v'],r['c']
        x,y=frozenset(rules[u]),frozenset(rules[v])
        a,b=x-y,y-x
        if not a or not b:
            result='empty-arm'
        else:
            try:
                cp,pa,pb=checker.check(a,b,c)
                result=''.join('1' if q else '0' for q in (cp,pa,pb))
            except OverflowError:
                result='undecided'
        judgements.append([u,v,c,result,r['count']])
    if law=='nae':
        checker.solver.delete()
        checker.projection.cache_clear();checker.proper.cache_clear()
    else:
        checker.dimension.cache_clear()
    return {'law':law,'system':system,'total_requests':len(grouped[law,system]),'rows':judgements}
