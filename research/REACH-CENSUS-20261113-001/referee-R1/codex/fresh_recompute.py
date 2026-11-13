"""Independent REACH referee reconstruction from the frozen spec and mathematics.

No producer module is loaded. Family definitions are decoded from the allowed data.
The sole reused scientific routine is the explicitly allowed earlier referee's exact
residue test. Everything else, including limits, inlining, block maps, graph, SCCs,
Karp, and direct SAT projection tests, is implemented here afresh.

Run with the workspace .venv/bin/python -B. One process, <=6 GiB address space,
per-case alarm, no subprocesses. All writes are beside this file.
"""
from __future__ import annotations
import argparse
from collections import Counter, deque
from fractions import Fraction
from functools import lru_cache
import gzip
import hashlib
import importlib.util
import itertools
import json
import math
from pathlib import Path
import random
import resource
import signal
import time
import numpy as np
from pysat.solvers import Solver

ROOT = Path('/home/jscul/p-vs-np-contact-first')
HERE = Path(__file__).resolve().parent
DATA = ROOT / 'artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census'
INF = 10**9

def rows(name):
    with gzip.open(DATA / name, 'rt') as f:
        return [json.loads(line) for line in f]

def save(name, obj):
    p = (HERE / name).resolve()
    assert p.is_relative_to(HERE)
    p.write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n')

def members(mask):
    while mask:
        b = mask & -mask
        yield b.bit_length()-1
        mask ^= b

def powerset(seq, minimum=0):
    return (c for n in range(minimum, len(seq)+1) for c in itertools.combinations(seq,n))

def state_code(a, args):
    return sum(((a >> x) & 1) << i for i,x in enumerate(args))

def usual_and_limit(defs):
    """Existential relations, descending from TOP; no imported census helpers."""
    usual = []
    for k,l,calls in defs:
        c = [(t, tuple(a)) for t,a in calls]
        if any(t == 'SELF' and sorted(a) == [0,1,2] for t,a in c):
            c.append(('K',(0,1,2)))
        usual.append((k,l,c))
    holding = {i for i,d in enumerate(usual) if any(t == 'SELF' for t,a in d[2])}
    G = {i:255 for i in holding}
    history = [dict(G)]
    while True:
        rels = []
        for i,(k,l,calls) in enumerate(usual):
            r = 0
            for a in range(1 << (k+l)):
                for t,args in calls:
                    q = state_code(a,args)
                    relation = 126 if t == 'K' else G[i] if t == 'SELF' else rels[t]
                    if not ((relation >> q) & 1):
                        break
                else:
                    r |= 1 << (a & ((1<<k)-1))
            rels.append(r)
        new = {i:rels[i] for i in holding}
        assert all(new[i] & ~G[i] == 0 for i in holding)
        if new == G:
            return usual, holding, G, bool(rels[-1]), history
        G = new
        history.append(dict(G))

def inline_body(defs, holding, i):
    """Depth-first expansion; allocate every callee's locals fresh in call order."""
    k,l,_ = defs[i]
    next_id = k+l
    calls = []
    def expand(j, env):
        nonlocal next_id
        for t, args in defs[j][2]:
            mapped = tuple(env[a] for a in args)
            if t == 'K':
                calls.append(('K', mapped))
            elif t == 'SELF':
                calls.append((j, mapped))
            elif t in holding:
                calls.append((t, mapped))
            else:
                ck,cl,_ = defs[t]
                assert len(mapped) == ck
                fresh = tuple(range(next_id,next_id+cl))
                next_id += cl
                expand(t, mapped+fresh)
    expand(i,tuple(range(k+l)))
    return k,next_id,tuple(calls)

class Pattern:
    def __init__(self, key, ray='first'):
        self.key,self.ray = key,ray
        self.defs = json.loads(key)
        self.usual,self.holding,self.G,self.alive,self.limit_history = usual_and_limit(self.defs)
        self.main_id = len(self.defs)-1
        self.main = inline_body(self.usual,self.holding,self.main_id)
        candidates = [(j,t) for j,(t,a) in enumerate(self.main[2]) if t != 'K']
        self.S = self.main_id if self.main_id in self.holding else candidates[0][1] if candidates else None
        self.body = inline_body(self.usual,self.holding,self.S) if self.S is not None else None
        if self.S is not None:
            entries = [j for j,(t,a) in enumerate(self.main[2]) if t == self.S]
            rays = [j for j,(t,a) in enumerate(self.body[2]) if t == self.S]
            self.entry = entries[0 if ray == 'first' else -1]
            self.ray_call = rays[0 if ray == 'first' else -1]

    def settled(self):
        if not self.alive: return 'S1 limit dead'
        if self.S is None: return 'S2 no copy'
        if self.body[1] == 3: return 'S3 no own distinctions'
        used = set(self.body[2][self.ray_call][1])
        for j,(t,a) in enumerate(self.body[2]):
            if t == 'K' or (j != self.ray_call and self.G[t] != 255):
                used.update(a)
        if not used.intersection(range(3,self.body[1])): return 'S4 free own distinctions'
        return None

    def allowed(self, body, omitted):
        k,V,calls = body
        ans = []
        for a in range(1<<V):
            if all(j == omitted or ((126 if t == 'K' else self.G[t]) >> state_code(a,args)) & 1
                   for j,(t,args) in enumerate(calls)):
                ans.append(a)
        return ans

    def cnf(self, depth):
        """Direct syntax expansion, independent of block truth tables and DP.

        Only the chosen ray is expanded. Other holding calls become their exact
        greatest-fixed-point clauses. Locals introduced by inlining stay members
        of this ray's pool; side branch interiors never enter the member pool.
        """
        clauses=[]
        # This expansion deliberately does not use self.main, self.body,
        # inline_body(), or the DP's entry/ray indices. A stack walks original
        # syntax and allocates each invocation's locals when encountered.
        k=self.usual[-1][0]
        total=k
        ports=tuple(range(k))
        top=set(ports)
        created=[]
        direct_S=None
        for level in range(depth+1):
            owner=len(self.usual)-1 if level==0 else direct_S
            old_total=total
            l=self.usual[owner][1]
            env=ports+tuple(range(total,total+l)); total+=l
            stack=[(owner,env,iter(self.usual[owner][2]))]
            events=[]
            while stack:
                j,env,it=stack[-1]
                try: t,args=next(it)
                except StopIteration: stack.pop(); continue
                actual=tuple(env[x] for x in args)
                if t=='SELF': events.append((j,actual))
                elif t=='K' or t in self.holding: events.append((t,actual))
                else:
                    l=self.usual[t][1]
                    subenv=actual+tuple(range(total,total+l)); total+=l
                    stack.append((t,subenv,iter(self.usual[t][2])))
            if level==0:
                direct_S=owner if owner in self.holding else next(t for t,a in events if t!='K')
                assert direct_S==self.S
            eligible=[j for j,(t,a) in enumerate(events) if t==direct_S]
            chosen=eligible[0 if self.ray=='first' else -1]
            local=tuple(range(old_total,total))
            created.append((tuple(range(k))+local) if level==0 else local)
            nxt=None
            for j,(t,actual) in enumerate(events):
                if j==chosen:
                    nxt=actual
                    if level<depth: continue
                rel=126 if t=='K' else self.G[t]
                for q in range(1<<len(actual)):
                    if not ((rel>>q)&1):
                        clauses.append([-(v+1) if (q>>i)&1 else v+1 for i,v in enumerate(actual)])
            ports=nxt
        return clauses,total,top,set(created[-1]),set(itertools.chain.from_iterable(created))

class Block:
    def __init__(self, allowed, output):
        self.a=np.array(allowed,dtype=np.int64)
        self.port=self.a & 7
        self.out=np.zeros(len(self.a),dtype=np.int64) if output is None else sum(((self.a>>x)&1)<<i for i,x in enumerate(output))
        self.cache={}

    def maps(self,W):
        W=tuple(W)
        if W not in self.cache:
            alpha=np.zeros(len(self.a),dtype=np.int64)
            for i,w in enumerate(W): alpha |= ((self.a>>w)&1)<<i
            T=np.zeros((1<<len(W),8),dtype=np.uint16)
            np.bitwise_or.at(T,(alpha,self.port),1<<self.out)
            self.cache[W]=tuple(dict.fromkeys(tuple(map(int,row)) for row in T))
        return self.cache[W]

def encode_set(xs):
    out=0
    for x in xs: out |= 1<<x
    return out

@lru_cache(maxsize=50000)
def image_table(T):
    a=[0]*256
    for i in range(1,256):
        b=i & -i
        a[i]=a[i^b] | T[b.bit_length()-1]
    return bytes(a)

class Action:
    def __init__(self,block,W):
        self.cost=len(W)
        self.full=tuple(image_table(T) for T in block.maps(W))
        self.forgot=tuple(dict.fromkeys(image_table(T) for i in range(len(W))
                              for T in block.maps(W[:i]+W[i+1:])))
        self.cache={}
    def apply(self,st):
        if st in self.cache: return self.cache[st]
        F,G=st
        nf=encode_set(T[r] for r in members(F) for T in self.full)
        ng=encode_set(itertools.chain((T[r] for r in members(G) for T in self.full),
                                      (T[r] for r in members(F) for T in self.forgot)))
        result=(nf,ng)
        self.cache[st]=result
        return result

class DynamicProgram:
    def __init__(self,p):
        self.p=p
        k,V,calls=p.main
        _,SV,scalls=p.body
        begin=Block(p.allowed(p.main,p.entry),calls[p.entry][1])
        middle=Block(p.allowed(p.body,p.ray_call),scalls[p.ray_call][1])
        ending=Block(p.allowed(p.body,None),None)
        self.starts={}
        # Direct no-incoming-interface calculation, independent of any 3-port
        # assumption on main. The 8-state incoming masks are used only below it.
        for W in powerset(tuple(range(V)),1):
            if not any(w<k for w in W): continue
            full=encode_set(int(np.bitwise_or.reduce(T)) for T in begin.maps(W))
            forgot=encode_set(int(np.bitwise_or.reduce(T)) for i in range(len(W))
                              for T in begin.maps(W[:i]+W[i+1:]))
            st=(full,forgot)
            self.starts[st]=min(self.starts.get(st,INF),len(W))
        loc=tuple(range(3,SV))
        self.middle=[Action(middle,W) for W in powerset(loc)]
        self.ending=[Action(ending,W) for W in powerset(loc,1)]
    @lru_cache(maxsize=None)
    def close(self,st):
        if st[1]&1: return INF
        for a in self.ending:
            F,G=a.apply(st)
            if F&1 and not G&1: return a.cost
        return INF
    def layers(self,n):
        layer=dict(self.starts); result=[]
        for _ in range(n):
            result.append(min(INF,min((c+self.close(st) for st,c in layer.items()),default=INF)))
            nxt={}
            for st,c in layer.items():
                for a in self.middle:
                    ns=a.apply(st)
                    nxt[ns]=min(nxt.get(ns,INF),c+a.cost)
            layer=nxt
        return result

def graph_of(dp,cap=100000):
    states=list(dp.starts); ids={s:i for i,s in enumerate(states)}
    starts={ids[s]:c for s,c in dp.starts.items()}
    graph=[]; close=[]
    cursor=0
    while cursor<len(states):
        st=states[cursor]; arcs=[]
        for a in dp.middle:
            ns=a.apply(st)
            if ns not in ids:
                if len(states)>=cap: raise RuntimeError('referee graph node cap')
                ids[ns]=len(states); states.append(ns)
            arcs.append((ids[ns],a.cost))
        graph.append(arcs); close.append(dp.close(st)); cursor+=1
    return graph,close,starts

def productive_scc(graph,close):
    reverse=[[] for _ in graph]
    for u,arcs in enumerate(graph):
        for v,w in arcs: reverse[v].append(u)
    good={i for i,c in enumerate(close) if c<INF}; q=deque(good)
    while q:
        for u in reverse[q.popleft()]:
            if u not in good: good.add(u); q.append(u)
    seen=set(); order=[]
    for root in sorted(good):
        if root in seen: continue
        seen.add(root); stack=[(root,iter(graph[root]))]
        while stack:
            u,it=stack[-1]
            try: v,_=next(it)
            except StopIteration: order.append(u); stack.pop(); continue
            if v in good and v not in seen: seen.add(v); stack.append((v,iter(graph[v])))
    seen=set(); comps=[]
    for root in reversed(order):
        if root in seen: continue
        todo=[root]; seen.add(root); c=[]
        while todo:
            u=todo.pop(); c.append(u)
            for v in reverse[u]:
                if v in good and v not in seen: seen.add(v); todo.append(v)
        comps.append(c)
    return good,comps

def minimum_mean(graph,c):
    index={u:i for i,u in enumerate(c)}; n=len(c)
    arcs=[(index[u],index[v],w) for u in c for v,w in graph[u] if v in index]
    if n==1: return min((Fraction(w) for u,v,w in arcs if u==v),default=None)
    D=[[0]*n]
    for _ in range(n):
        row=[10**18]*n
        for u,v,w in arcs: row[v]=min(row[v],D[-1][u]+w)
        D.append(row)
    return min(max(Fraction(D[n][v]-D[j][v],n-j) for j in range(n)) for v in range(n))

def zero_cycles(graph):
    successor=[]
    for arcs in graph:
        zero=[v for v,w in arcs if w==0]
        assert len(zero)==1
        successor.append(zero[0])
    seen=set(); cycles=[]
    for root in range(len(graph)):
        if root in seen: continue
        pos={}; trace=[]; u=root
        while u not in seen and u not in pos:
            pos[u]=len(trace); trace.append(u); u=successor[u]
        if u in pos: cycles.append(trace[pos[u]:])
        seen.update(trace)
    return cycles

def residue_function():
    path=ROOT/'research/PROVED-RATE-20261113-001/referee-R1/codex/recompute.py'
    s=importlib.util.spec_from_file_location('allowed_prior_referee',path)
    module=importlib.util.module_from_spec(s); s.loader.exec_module(module)
    return module.exact_eventual_bound

def classify(dp):
    graph,close,starts=graph_of(dp)
    good,comps=productive_scc(graph,close)
    cyclic=[c for c in comps if len(c)>1 or any(v==c[0] for v,w in graph[c[0]])]
    rate=min((minimum_mean(graph,c) for c in cyclic),default=None)
    cycles=zero_cycles(graph)
    exact=residue_function()(graph,close,starts,good,cycles)
    if not good: label='none at any depth'
    elif not cyclic: label='lost at large depths'
    elif exact['eventually_bounded']: label='bounded'
    elif rate is not None and rate>0: label='grows'
    elif exact['eventually_bounded'] is None: label='unresolved'
    else: label='mixed by residue'
    layer=starts; values=[]
    for _ in range(30):
        values.append(min(INF,min((c+close[u] for u,c in layer.items()),default=INF)))
        nxt={}
        for u,c in layer.items():
            for v,w in graph[u]: nxt[v]=min(nxt.get(v,INF),c+w)
        layer=nxt
    return dict(nodes=len(graph),complete=True,trimmed_nodes=len(good),
                **{'class':label,'lambda':str(rate) if rate is not None else None},
                exact=exact,L_ray=values)

def direct_sat(p,depth,maxsize=7):
    clauses,n,top,last,pool=p.cnf(depth)
    started=time.monotonic(); tests=0
    # Factor the CNF into independent variable components. No minimal nonfree
    # set can straddle independent factors; isolated variables enter no bond.
    parent=list(range(n))
    def root(v):
        while parent[v]!=v: parent[v]=parent[parent[v]]; v=parent[v]
        return v
    for clause in clauses:
        vs=[abs(x)-1 for x in clause]
        for v in vs[1:]: parent[root(v)]=root(vs[0])
    active=set(abs(x)-1 for c in clauses for x in c)
    components={}
    for v in sorted(pool & active): components.setdefault(root(v),[]).append(v)
    relevant=[vs for vs in components.values() if top.intersection(vs) and last.intersection(vs)]
    known_nonfree=[]
    with Solver(name='cadical153',bootstrap_with=clauses) as solver:
        if not solver.solve(): return dict(status='dead',n=n)
        @lru_cache(maxsize=None)
        def free(W):
            nonlocal tests
            tests+=1
            # Global bit complement is a symmetry (independently verified below),
            # hence testing representatives with W's first member zero suffices.
            for a in range(1<<max(0,len(W)-1)):
                assignments=[-(W[0]+1)] if W else []
                assignments += [v+1 if (a>>(i-1))&1 else -(v+1) for i,v in enumerate(W) if i]
                if not solver.solve(assumptions=assignments): return False
            return True
        # Check the symmetry used to halve projection queries at the clause level.
        cs={tuple(sorted(c)) for c in clauses}
        assert all(tuple(sorted(-x for x in c)) in cs for c in clauses)
        for size in range(1,maxsize+1):
            for vs in relevant:
                for W in itertools.combinations(vs,size):
                    mask=sum(1<<v for v in W)
                    if any(mask & b == b for b in known_nonfree): continue
                    if free(W): continue
                    assert all(free(W[:j]+W[j+1:]) for j in range(size))
                    known_nonfree.append(mask)
                    if top.intersection(W) and last.intersection(W):
                        return dict(status='exact',value=size,witness=list(W),n=n,clauses=len(clauses),
                                    candidates=tests,seconds=time.monotonic()-started)
    # If every component is small, all possible bonds were searched, not just <=7.
    exhaustive=not relevant or max(map(len,relevant))<=maxsize
    return dict(status='exact' if exhaustive else 'lower_bound',value=INF if exhaustive else None,
                lower_bound=maxsize+1,n=n,clauses=len(clauses),candidates=tests,
                components=list(map(len,relevant)),seconds=time.monotonic()-started)

def choose(records):
    usable=[r for r in records if r.get('complete') and not r['class'].startswith('S')]
    chosen={}
    def add(r,reason): chosen.setdefault(r['key'],dict(record=r,reasons=[]))['reasons'].append(reason)
    for label in ['bounded','grows','lost at large depths','none at any depth','mixed by residue']:
        for multi in [False,True]:
            a=sorted((r for r in usable if r['class']==label and (r.get('n_defs',0)>1)==multi),
                     key=lambda r:(r['nodes'],r['key']))
            for r in a[:3 if label!='mixed by residue' else 8]: add(r,f'class:{label}:multi={multi}')
    for field in ['main_block_size','s_block_size']:
        for size in [10,11,12]:
            for label in ['bounded','grows','lost at large depths','none at any depth','mixed by residue']:
                a=sorted((r for r in usable if r.get('n_defs',0)>1 and r.get(field)==size and r['class']==label),
                         key=lambda r:(r['nodes'],r['key']))
                if a: add(a[0],f'large:{field}={size}:{label}')
    # Explicit non-self-holding main and wide-port start cases, not only main=S.
    a=sorted((r for r in usable if r.get('n_defs',0)>1 and r.get('k_main',3)>3),key=lambda r:(r['nodes'],r['key']))
    for r in a[:4]: add(r,'wide main / entry')
    return list(chosen.values())

def timeout(signum,frame): raise TimeoutError('per-case referee resource ceiling')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('mode',choices=['select','primary','alternative','controls'])
    ap.add_argument('--limit',type=int); ap.add_argument('--offset',type=int,default=0)
    ap.add_argument('--seconds',type=int,default=90); ap.add_argument('--output')
    args=ap.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(6*1024**3,6*1024**3))
    signal.signal(signal.SIGALRM,timeout)
    if args.mode=='controls':
        checks=[]
        for graph,expected in [([[(0,2)]],Fraction(2)),([[(1,0)],[(0,1)]],Fraction(1,2)),([[(0,0)]],Fraction(0))]:
            got=minimum_mean(graph,list(range(len(graph)))); assert got==expected
            checks.append(dict(kind='karp',got=str(got),expected=str(expected)))
        exact=residue_function()
        graph=[[(0,0)]]; r=exact(graph,[2],{0:1},{0},[[0]])
        assert r['eventually_bounded'] and r['uniform_cost_bound']==3
        checks.append(dict(kind='positive residue',result=r))
        graph=[[(1,0)],[(0,0)]]; r=exact(graph,[2,INF],{0:1},{0,1},[[0,1]])
        assert r['eventually_bounded'] is False and r['missing_residues']==[1]
        checks.append(dict(kind='negative residue',result=r))
        save('controls.json',checks); print('controls passed'); return
    records=rows('families.jsonl.gz'); selected=choose(records)
    if args.mode=='select':
        save('selection.json',[dict(key=x['record']['key'],reasons=x['reasons'],
               reported={k:x['record'].get(k) for k in ['class','nodes','main_block_size','s_block_size','n_defs']}) for x in selected])
        print('selected',len(selected)); return
    if args.mode=='alternative':
        alt=rows('alt_growing664_families.jsonl.gz')
        chosen=[]
        for bound in [3,4,5]:
            a=sorted((r for r in alt if r['class']=='bounded' and r['uniform_cost_bound']==bound),key=lambda r:(r['nodes'],r['key']))
            # All five-member cases and several of the others; include late onsets.
            take=a[:5] if bound!=5 else a
            if a: take+=sorted(a,key=lambda r:(-r['onset_depth'],r['nodes']))[:2]
            chosen+=take
        seen=set(); selected=[]
        for r in chosen:
            if r['key'] not in seen: selected.append(dict(record=r,reasons=['last-call bound stratum'])); seen.add(r['key'])
    selected=selected[args.offset:args.offset+args.limit if args.limit else None]
    output=args.output or args.mode+'_results.jsonl'
    pth=(HERE/output).resolve(); assert pth.is_relative_to(HERE)
    with pth.open('x') as stream:
        for i,x in enumerate(selected):
            r=x['record']; t=time.monotonic(); out=dict(key=r['key'],reasons=x['reasons'],index=i,
                         reported={k:r.get(k) for k in ['class','nodes','lambda','L_ray','main_block_size','s_block_size','S','period','missing_residues','uniform_cost_bound','onset_depth']},errors=[])
            signal.alarm(args.seconds)
            try:
                p=Pattern(r['key'],'last' if args.mode=='alternative' else 'first')
                out['structure']=dict(n_defs=len(p.defs),main_size=p.main[1],main_ports=p.main[0],S=p.S,
                           s_size=p.body[1],entry=p.entry,ray_call=p.ray_call,G=p.G,main_calls=p.main[2],ray_calls=p.body[2])
                assert p.settled() is None
                for f,v in [('main_block_size',p.main[1]),('s_block_size',p.body[1]),('S',p.S)]:
                    if r.get(f)!=v: out['errors'].append(dict(field=f,ours=v,study=r.get(f)))
                dp=DynamicProgram(p)
                out['dp_small']=dp.layers(3)
                if out['dp_small']!=r['L_ray'][:3]: out['errors'].append(dict(field='L_ray(1..3)',ours=out['dp_small'],study=r['L_ray'][:3]))
                out['direct_sat']=[]
                for depth in [1,2,3]:
                    sat=direct_sat(p,depth,maxsize=min(7,r['L_ray'][depth-1]) if r['L_ray'][depth-1]<INF else 7)
                    sat['depth']=depth
                    predicted=out['dp_small'][depth-1]
                    sat['agreement']=sat['value']==predicted if sat['status']=='exact' else predicted>=sat['lower_bound']
                    out['direct_sat'].append(sat)
                    if not sat['agreement']: out['errors'].append(dict(field='direct_sat',depth=depth,result=sat,dp=predicted))
                out['class_recompute']=classify(dp)
                fresh=out['class_recompute']
                for f in ['class','nodes','L_ray']:
                    if fresh[f]!=r[f]: out['errors'].append(dict(field=f,ours=fresh[f],study=r[f]))
                if (Fraction(fresh['lambda']) if fresh['lambda'] is not None else None)!=(Fraction(r['lambda']) if r['lambda'] is not None else None):
                    out['errors'].append(dict(field='lambda',ours=fresh['lambda'],study=r['lambda']))
                for f,g in [('eventually_bounded','eventually_bounded'),('period','period'),('missing_residues','missing_residues')]:
                    if fresh['exact'].get(f)!=r.get(g): out['errors'].append(dict(field=f,ours=fresh['exact'].get(f),study=r.get(g)))
                out['status']='done'
            except (TimeoutError,MemoryError,RuntimeError) as e:
                out['status']='resource_failure'; out['exception']=repr(e)
            finally:
                signal.alarm(0)
                DynamicProgram.close.cache_clear(); image_table.cache_clear()
            out['seconds']=time.monotonic()-t
            out['peak_rss_kib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            stream.write(json.dumps(out,sort_keys=True)+'\n'); stream.flush()
            print(json.dumps(dict(index=i,status=out['status'],seconds=round(out['seconds'],2),errors=out['errors'],
                                  sizes=out.get('structure',{}).get('main_size'),reported_class=r['class'])),flush=True)

if __name__=='__main__': main()
