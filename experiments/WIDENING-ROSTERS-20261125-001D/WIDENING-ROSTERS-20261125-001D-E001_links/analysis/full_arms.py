"""Project both exclusive holder supports together with their actual shared distinction."""

from collections import Counter, defaultdict, deque
import gzip
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from time import monotonic

from pysat.solvers import Solver


def incidence_core(rules, kept):
    """A variable private to one surviving rule can always satisfy that rule."""
    at = defaultdict(set)
    for i, row in enumerate(rules):
        for var in row:
            at[var].add(i)
    queue = deque(var for var, uses in at.items() if var not in kept and len(uses)==1)
    live = set(range(len(rules)))
    while queue:
        var = queue.popleft()
        if len(at[var]) != 1:
            continue
        rule = next(iter(at[var]))
        live.remove(rule)
        for other in rules[rule]:
            at[other].remove(rule)
            if other not in kept and len(at[other])==1:
                queue.append(other)
    return [rules[i] for i in sorted(live)]


def parity_shadow(rules, variables):
    """Eliminate all non-observed variables before producing the local parity checks."""
    kept = set(variables)
    columns = list(variables) + sorted({v for row in rules for v in row} - kept)
    pos = {v:i for i,v in enumerate(columns)}
    pivots = {}
    for row in rules:
        support = sum(1 << pos[v] for v in row)
        while support:
            pivot = support.bit_length()-1
            if pivot not in pivots:
                pivots[pivot]=support
                break
            support ^= pivots[pivot]
    return [mask for i,mask in pivots.items() if i < len(variables)]


def cnf(rules, parity):
    fresh = 2+max((v for rule in rules for v in rule), default=-1)
    clauses = []
    for rule in rules:
        row = [v+1 for v in rule]
        if not parity:
            clauses.extend((row,[-x for x in row]))
            continue
        acc = row[0]
        for other in row[1:-1]:
            out, fresh = fresh, fresh+1
            clauses.extend(([acc,other,-out],[acc,-other,out],[-acc,other,out],[-acc,-other,-out]))
            acc = out
        clauses.extend(([-acc,row[-1]],[acc,-row[-1]]))
    return clauses


def projected(rules,variables,parity):
    kept = set(variables)
    core = incidence_core(rules,kept)
    pos = {v:i for i,v in enumerate(variables)}
    if parity:
        masks = parity_shadow(core,variables)
        return {x for x in range(1<<len(variables))
                if all((x & mask).bit_count()%2==0 for mask in masks)}
    if all(set(row)<=kept for row in core):
        supports = [sum(1<<pos[v] for v in row) for row in core]
        return {x for x in range(1<<len(variables))
                if all(0 < (x & mask) < mask for mask in supports)}
    # Encode the small residual in its original variable names.
    with Solver(name='minisat22',bootstrap_with=cnf(core,False)) as solver:
        return {word for word in range(1<<len(variables)) if solver.solve(
            assumptions=[v+1 if word & (1<<i) else -v-1 for i,v in enumerate(variables)])}


def independent_projection(rules, variables, parity):
    """Independent raw, unpeeled whole-stage check with a distinct solver."""
    # Assignments of every whole-stage knot are invariant under complement for NAE.
    # For parity with mixed arities the complementary assignment need not be valid.
    with Solver(name='cadical195',bootstrap_with=cnf(rules,parity)) as solver:
        rows = set()
        for values in product([False, True],repeat=len(variables)-(0 if parity else 1)):
            bit_values = values if parity else (False,)+values
            pins = [v+1 if bit else -v-1 for v,bit in zip(variables,bit_values)]
            if solver.solve(assumptions=pins):
                word=sum(1<<i for i,b in enumerate(bit_values) if b)
                rows.add(word)
                if not parity: rows.add(word ^ ((1<<len(variables))-1))
        return rows


def factor(rows,al,bl):
    left_mask, right_mask = (1<<al)-1,(1<<bl)-1
    fibers=[]
    for c in [0,1]:
        pairs={(x&left_mask,(x>>al)&right_mask) for x in rows if x>>(al+bl)==c}
        a,b={i for i,_ in pairs},{j for _,j in pairs}
        missing=next(((i,j) for i in sorted(a) for j in sorted(b) if (i,j) not in pairs),None)
        fibers.append((pairs,a,b,missing))
    rectangle=all(len(p)==len(a)*len(b) for p,a,b,_ in fibers)
    c_count=sum(bool(p) for p,_,_,_ in fibers)
    a_count=len(fibers[0][1] | fibers[1][1]);b_count=len(fibers[0][2] | fibers[1][2])
    proper_a=sum(len(z[1]) for z in fibers)<a_count*c_count
    proper_b=sum(len(z[2]) for z in fibers)<b_count*c_count
    return dict(rows=len(rows),table_sha256=sha256(json.dumps(sorted(rows),separators=(',',':')).encode()).hexdigest(),
                conditional_product=rectangle,proper_a=proper_a,proper_b=proper_b,
                fibers=[dict(c=c,joint=len(p),a=len(a),b=len(b),missing=missing) for c,(p,a,b,missing) in enumerate(fibers)])


def stream(path,digest):
    h=sha256()
    with gzip.open(path,'rb') as fp:
        for line in fp:
            h.update(line)
            yield json.loads(line)
    if h.hexdigest()!=digest: raise ValueError(f'Wrong decompressed digest: {path}')


def examine(record, root):
    started=monotonic()
    stages=list(stream(root/record['support_file'],record['support_sha256']))
    by_t={s['round']:s for s in stages}
    initial=by_t[0]['distinctions']
    choice={}
    for ev in stream(root/record['events_file'],record['events_sha256']):
        for route in ev['routes']:
            for c in route['contacts']:
                key=(route['route'],'start-held' if c<initial else 'made')
                coords=(ev['s'],ev['t'],tuple(ev['X']),tuple(ev['Y']),route['w'],route['u'],route['v'],c)
                if key not in choice or coords<choice[key]:
                    choice[key]=coords
    result=[]
    for (route,origin),coords in sorted(choice.items()):
        s,t,X,Y,w,u,v,c=coords
        supports=[k for j in range(t+1) for k in by_t[j]['supports']]
        left=sorted(set(supports[u])-set(supports[v])); right=sorted(set(supports[v])-set(supports[u]))
        assert c in supports[u] and c in supports[v]
        variables=left+right+[c]
        details=dict(route=route,origin=origin,s=s,t=t,X=X,Y=Y,w=w,u=u,v=v,c=c,A=left,B=right,width=len(variables))
        if not left or not right:
            details['status']='empty arm'
        elif len(variables)>14:
            details['status']='not run: first representative exceeds registered width'
        else:
            parity=record['kl']=='parity'
            a=projected(supports,variables,parity)
            b=independent_projection(supports,variables,parity)
            if a!=b: raise ValueError(f'Independent tables differ on {coords}')
            details.update(status='checked',**factor(a,len(left),len(right)))
        result.append(details)
    return dict(case=record['case'],kl=record['kl'],representatives=result,seconds=round(monotonic()-started,4))


def setup(params):
    global primary_dir, selected
    primary_dir=Path(params['primary']).resolve()
    casefile=Path(__file__).resolve().parents[1]/'cases.json'
    order={x['id']:i for i,x in enumerate(json.loads(casefile.read_text()))}
    raw=[json.loads(line) for line in Path(params['manifest']).read_text().splitlines()]
    selected=sorted((r for r in raw if r['rule']=='MOST'),key=lambda r:(order[r['case']],r['kl']))
    if 'limit' in params: selected=selected[:int(params['limit'])]


def cases():
    for record in selected:
        yield f"{record['case']}-{record['kl']}",record


def run(case_id,payload):
    return examine(payload,primary_dir)
