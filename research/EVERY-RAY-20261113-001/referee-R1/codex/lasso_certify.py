"""Fresh EVERY-RAY referee: capped exact cost vectors along a single lasso.

No producing code is imported. A cost cap is exact for bounded reachability:
costs never decrease, so deleting states above the cap cannot lose a certificate.
Each vector contains ALL non-rejected DP states of cost <= cap, not just one
minimum or a selected zero cycle. Repeating (phase,T,vector) proves all future
residues. The certificate is eventual; any early missing bonds are explicit.
"""
import argparse, collections, hashlib, itertools, json, resource, signal, time
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
DATA = ROOT / 'experiments/EVERY-RAY-20261113-001A/EVERY-RAY-20261113-001A-E001_min_over_paths/codex/sample'
INF = 10**9

def bits(x):
    while x:
        b=x & -x; yield b.bit_length()-1; x-=b

def selected_value(x, vs):
    return sum(((x>>v)&1)<<j for j,v in enumerate(vs))

def read_rows():
    rows={}
    for name in ('G.jsonl','N.jsonl','B.jsonl','B_resume.jsonl','phase2.jsonl'):
        for line in (DATA/name).open():
            r=json.loads(line)
            if r.get('key'): rows[r['key']]=r
    return rows

def relations(defs):
    """Usual limit, from TOP by greatest fixed point, independently enumerated."""
    ds=[]
    for k,l,cs in defs:
        cs=[(c,tuple(a)) for c,a in cs]
        if any(c=='SELF' and sorted(a)==[0,1,2] for c,a in cs):
            cs=cs+[('K',(0,1,2))]
        ds.append((k,l,cs))
    prev=[(1<<(1<<k))-1 for k,l,cs in ds]
    for iteration in range(100):
        nxt=[]
        for i,(k,l,cs) in enumerate(ds):
            rel=0
            for a in range(1<<(k+l)):
                ok=True
                for c,vs in cs:
                    r=126 if c=='K' else prev[i] if c=='SELF' else nxt[c]
                    if not (r>>selected_value(a,vs))&1:ok=False;break
                if ok:rel|=1<<(a&((1<<k)-1))
            nxt.append(rel)
        if nxt==prev:return ds,nxt,iteration+1
        assert all(b&a==b for a,b in zip(prev,nxt))
        prev=nxt
    raise RuntimeError('GFP did not settle')

class Block:
    def __init__(self,k,n,terms,calls,g):
        self.k=k;self.n=n;self.terms=terms;self.calls=calls;self.g=g
        allstates=[]
        for x in range(1<<n):
            if all((r>>selected_value(x,a))&1 for a,r in terms):allstates.append(x)
        self.allowed={}
        for choice in range(-1,len(calls)):
            self.allowed[choice]=tuple(x for x in allstates if all(j==choice or ((g>>selected_value(x,a))&1) for j,a in enumerate(calls)))

def prepare(defs):
    ds,rels,niter=relations(defs)
    selfset={i for i,d in enumerate(ds) if any(c=='SELF' for c,a in d[2])}
    reachable=set()
    def visit(i):
        if i in reachable:return
        reachable.add(i)
        for c,a in ds[i][2]:
            if isinstance(c,int):visit(c)
    visit(len(ds)-1)
    def first_self(i):
        if i in selfset:return i
        for c,a in ds[i][2]:
            if isinstance(c,int):
                found=first_self(c)
                if found is not None:return found
        return None
    S=first_self(len(ds)-1)
    assert S is not None
    def block(root):
        k,l,cs=ds[root];n=k;terms=[];calls=[]
        def expand(i,actual):
            nonlocal n
            kk,ll,cc=ds[i];env=list(actual)+list(range(n,n+ll));n+=ll
            for c,a in cc:
                av=tuple(env[v] for v in a)
                if c=='K':terms.append((av,126))
                elif c=='SELF':
                    if i==S:calls.append(av)
                    else:terms.append((av,rels[i]))
                elif c==S:calls.append(av)
                elif c in selfset:terms.append((av,rels[c]))
                else:expand(c,av)
        expand(root,range(k))
        return Block(k,n,terms,calls,rels[S])
    return S,block(len(ds)-1),block(S),rels,niter

class DP:
    def __init__(self,defs,cap):
        self.S,self.main,self.mid,self.rels,self.gfp_iterations=prepare(defs)
        self.cap=cap
        self.states=[];self.ids={}
        self.metrics=collections.Counter()
        self._edges={};self._close={};self._transforms={};self._apply={}
        self.tabs={}
        for ismain,b in ((True,self.main),(False,self.mid)):
            pools=[tuple(bits(w)) for w in range(1<<b.n) if (w&((1<<b.k)-1))] if ismain else [tuple(j for j in range(3,b.n) if (w>>(j-3))&1) for w in range(1<<(b.n-3))]
            for choice in range(len(b.calls)):
                self.tabs[ismain,choice]=[(len(W),self.make_tabs(b,choice,W,ismain)) for W in pools if len(W)<cap]
        self.endtabs=[(len(W),self.make_tabs(self.mid,-1,W,False)) for w in range(1,1<<(self.mid.n-3)) if len(W:=tuple(j for j in range(3,self.mid.n) if (w>>(j-3))&1))<=cap]

    def make_tabs(self,b,choice,W,start):
        rows=[[0]*8 for _ in range(1<<len(W))]
        for x in b.allowed[choice]:
            a=selected_value(x,W);incoming=0 if start else x&7
            out=0 if choice==-1 else selected_value(x,b.calls[choice])
            rows[a][incoming]|=1<<out
        full=set(tuple(v) for v in rows)
        forgot=set()
        for j in range(len(W)):
            for a in range(1<<len(W)):
                if not (a>>j)&1:
                    forgot.add(tuple(x|y for x,y in zip(rows[a],rows[a|(1<<j)])))
        return tuple(sorted(full)),tuple(sorted(forgot))

    def transform(self,T):
        if T not in self._transforms:
            image=[0]*256
            for r in range(1,256):
                low=r & -r;image[r]=image[r-low]|T[low.bit_length()-1]
            self._transforms[T]=tuple(1<<v for v in image)
        return self._transforms[T]

    def apply(self,F,T):
        key=(F,T)
        if key not in self._apply:
            z=0;lookup=self.transform(T)
            for r in bits(F):z|=lookup[r]
            self._apply[key]=z
        return self._apply[key]

    def advance(self,st,tabs):
        F,G=st;full,forgot=tabs
        nF=nG=0
        for T in full:
            nF|=self.apply(F,T);nG|=self.apply(G,T)
        for T in forgot:nG|=self.apply(F,T)
        if nG&1:return None # a forgotten assignment already impossible forever
        return nF,nG

    def intern(self,st):
        if st not in self.ids:self.ids[st]=len(self.states);self.states.append(st)
        return self.ids[st]

    def start(self,e):
        vec={}
        for c,tabs in self.tabs[True,e]:
            ns=self.advance((2,0),tabs)
            if ns is not None:
                v=self.intern(ns);vec[v]=min(vec.get(v,INF),c)
        return vec

    def edges(self,v,i):
        key=(v,i)
        if key not in self._edges:
            out={}
            for c,tabs in self.tabs[False,i]:
                ns=self.advance(self.states[v],tabs)
                if ns is not None:
                    j=self.intern(ns);out[j]=min(out.get(j,INF),c)
            self._edges[key]=tuple(out.items())
        return self._edges[key]

    def step(self,vec,i):
        out={}
        for v,c in vec.items():
            for j,w in self.edges(v,i):
                z=c+w
                if z<self.cap and z<out.get(j,INF):out[j]=z
        return out

    def close(self,v):
        if v not in self._close:
            best=INF
            for c,tabs in self.endtabs:
                if c>=best:continue
                ns=self.advance(self.states[v],tabs)
                if ns is not None and (ns[0]&1):best=c
            self._close[v]=best
        return self._close[v]

    def value(self,vec):
        return min((c+self.close(v) for v,c in vec.items()),default=INF)

    def signature(self,vec):return tuple(sorted(vec.items()))
    def certificate_vector(self,vec):
        return [[str(self.states[v][0]),str(self.states[v][1]),c] for v,c in sorted(vec.items(),key=lambda p:self.states[p[0]])]

def transport(T,args):return sum(1<<j for j,a in enumerate(args) if a<3 and (T>>a)&1)

def test_lasso(dp,e,prefix,period,max_steps=100):
    vec=dp.start(e);T=sum(1<<j for j,a in enumerate(dp.main.calls[e]) if a<dp.main.k)
    values=[];masks=[];seen={};history=[]
    for depth in range(1,max_steps+1):
        val=dp.value(vec);values.append(val if val<INF else None);masks.append(T)
        if depth-1>=len(prefix):
            phase=(depth-1-len(prefix))%len(period)
            sig=(phase,T,dp.signature(vec))
            if sig in seen:
                old=seen[sig]
                if T==0 and all(x is not None and x<=dp.cap for x in values[old-1:depth-1]):
                    return dict(certified=True,entry=e,prefix=list(prefix),period=list(period),repeat_from_depth=old,repeat_at_depth=depth,repeat_length=depth-old,cap=dp.cap,eventual_bound=max(values[old-1:depth-1]),values=values,top_port_masks=masks,all_depths_have_bond=all(x is not None for x in values),all_depth_bound=max((x for x in values if x is not None),default=None) if all(x is not None for x in values) else None,vector=dp.certificate_vector(vec),residue_values=values[old-1:depth-1],vector_states=len(vec))
                return None
            seen[sig]=depth
        i=prefix[depth-1] if depth-1<len(prefix) else period[(depth-1-len(prefix))%len(period)]
        vec=dp.step(vec,i);T=transport(T,dp.mid.calls[i])
        if not vec:return None
        if len(dp.states)>100000:raise RuntimeError('state cap')
    return None

def candidate_words(c):
    # The periodic choice and entry are found here, never read from row witnesses.
    for p in range(1,5):
        for w in itertools.product(range(c),repeat=p):
            if p>1 and len(set(w))==1:continue
            if any(p%d==0 and w==w[:d]*(p//d) for d in range(1,p)):continue
            yield w

def find(row,seconds=35):
    start=time.monotonic();defs=json.loads(row['key'])
    # A row's bound sets a search budget only. It is never used as evidence.
    cap=max(7,min(12,int((row.get('uncarried_result') or {}).get('uniform_cost_bound') or 9)+2))
    dp=DP(defs,cap)
    assert dp.S==row['S'] and dp.main.n==row['main_block_size'] and dp.mid.n==row['s_block_size'],(dp.S,dp.main.n,dp.mid.n)
    attempted=0
    for prefixlen in range(3):
        for prefix in itertools.product(range(len(dp.mid.calls)),repeat=prefixlen):
            for word in candidate_words(len(dp.mid.calls)):
                for e in range(len(dp.main.calls)):
                    attempted+=1
                    cert=test_lasso(dp,e,prefix,word)
                    if cert:
                        cert.update(key=row['key'],mixed_path_needed=row.get('mixed_path_needed'),row_uncarried_class=row.get('class_path_uncarried'),row_bound=(row.get('uncarried_result') or {}).get('uniform_cost_bound'),independent_S=dp.S,main_calls=dp.main.calls,self_calls=dp.mid.calls,main_size=dp.main.n,s_size=dp.mid.n,attempted=attempted,dp_states=len(dp.states),seconds=round(time.monotonic()-start,4),gfp_iterations=dp.gfp_iterations)
                        return cert
                    if time.monotonic()-start>seconds:raise TimeoutError('family search budget')
    return dict(key=row['key'],certified=False,reason='candidate word envelope exhausted',attempted=attempted,dp_states=len(dp.states),seconds=round(time.monotonic()-start,4),mixed_path_needed=row.get('mixed_path_needed'),row_uncarried_class=row.get('class_path_uncarried'))

def controls():
    # Known NAE chain: top-to-depth-s minimal non-shattered set needs s+3.
    defs=[[3,3,[['K',[0,1,3]],['SELF',[3,4,5]]]]]
    dp=DP(defs,10);v=dp.start(0);got=[]
    for s in range(1,5):got.append(dp.value(v));v=dp.step(v,0)
    assert got==[4,5,6,7],got
    assert test_lasso(dp,0,(),(0,),max_steps=20) is None
    return dict(negative_growing_chain=got,negative_lasso_rejected=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,default=204);ap.add_argument('--seconds',type=float,default=35);ap.add_argument('--output',default='lasso_results.jsonl');ap.add_argument('--offset',type=int,default=0);args=ap.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(4*1024**3,4*1024**3))
    print(json.dumps({'controls':controls()}),flush=True)
    rows=[r for r in read_rows().values() if r.get('first_ray_class')=='grows' and r.get('class_path')=='bounded' and r.get('symmetry_inequivalent')]
    rows.sort(key=lambda r:(not r.get('mixed_path_needed'),r['main_block_size']+r['s_block_size'],r['key']))
    done=set()
    dest=OUT/args.output
    if dest.exists():
        for line in dest.open():done.add(json.loads(line)['key'])
    total=0;success=0
    with dest.open('a') as f:
        for row in rows[args.offset:args.offset+args.limit]:
            if row['key'] in done:continue
            t=time.monotonic()
            try:r=find(row,args.seconds)
            except (TimeoutError,MemoryError,RuntimeError,AssertionError) as ex:r=dict(key=row['key'],certified=False,reason=str(ex),mixed_path_needed=row.get('mixed_path_needed'),row_uncarried_class=row.get('class_path_uncarried'),seconds=round(time.monotonic()-t,3))
            r['row_order']=rows.index(row)
            f.write(json.dumps(r)+'\n');f.flush();total+=1;success+=r['certified']
            print(json.dumps({k:r.get(k) for k in ('row_order','certified','entry','prefix','period','eventual_bound','all_depth_bound','reason','seconds','attempted')}),flush=True)
    print(json.dumps(dict(new_rows=total,new_certificates=success)),flush=True)

if __name__=='__main__':main()
