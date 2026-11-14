"""Exhaustive finite-cost lasso search after the short-word search.

A closed reachable capped-vector graph with no safe cycle rules out every
infinite path eventually bounded BY THIS CAP. It does not rule out larger caps.
"""
import argparse, collections, gzip, json, resource, signal, time
from lasso_certify import DP,INF,OUT,read_rows,transport,test_lasso

class StopSearch(Exception):pass
def alarm(sig,frame):raise StopSearch('wall cap')

def find_cycle(adj,good):
    color={};parent={}
    for root in good:
        if color.get(root):continue
        color[root]=1;stack=[(root,iter(adj[root]))]
        while stack:
            v,it=stack[-1]
            try:w,i=next(it)
            except StopIteration:color[v]=2;stack.pop();continue
            if w not in good:continue
            if color.get(w)==1:
                rev=[i];u=v
                while u!=w:
                    p,j=parent[u];rev.append(j);u=p
                return w,tuple(reversed(rev))
            if not color.get(w):
                parent[w]=(v,i);color[w]=1;stack.append((w,iter(adj[w])))
    return None

def search(row,cap,maxnodes,require_all_depths=False):
    t=time.monotonic();dp=DP(json.loads(row['key']),cap)
    vectors=[];ids={};parents=[];entries=[];adj=[];good=set();q=collections.deque()
    def node(vec,T,parent,entry):
        sig=(T,dp.signature(vec))
        if sig not in ids:
            ids[sig]=len(vectors);vectors.append((vec,T));parents.append(parent);entries.append(entry);adj.append([]);q.append(ids[sig])
        return ids[sig]
    for e,a in enumerate(dp.main.calls):
        T=sum(1<<j for j,v in enumerate(a) if v<dp.main.k)
        node(dp.start(e),T,None,e)
    complete=True;reason=None
    try:
        while q:
            v=q.popleft();vec,T=vectors[v]
            val=dp.value(vec)
            if T==0 and val<=cap:good.add(v)
            if require_all_depths and val>cap:continue
            for i,a in enumerate(dp.mid.calls):
                nv=dp.step(vec,i);U=transport(T,a)
                w=node(nv,U,(v,i),entries[v]);adj[v].append((w,i))
            if len(vectors)>maxnodes:raise StopSearch('vector node cap')
    except (StopSearch,MemoryError) as ex:complete=False;reason=str(ex)
    cyc=find_cycle(adj,good)
    ans=dict(key=row['key'],cap=cap,complete=complete,reason=reason,vector_nodes=len(vectors),expanded=len(vectors)-len(q),safe_nodes=len(good),safe_cycle=bool(cyc),dp_states=len(dp.states),seconds=round(time.monotonic()-t,3),mixed_path_needed=row.get('mixed_path_needed'),row_uncarried_class=row.get('class_path_uncarried'),require_all_depths=require_all_depths)
    if cyc:
        v,word=cyc;path=[];u=v
        while parents[u] is not None:
            p,i=parents[u];path.append(i);u=p
        prefix=tuple(reversed(path));e=entries[v]
        cert=test_lasso(dp,e,prefix,word,max_steps=len(prefix)+3*len(word)+5)
        assert cert is not None
        if require_all_depths:assert cert['all_depths_have_bond'] and cert['all_depth_bound']<=cap
        cert['key']=row['key'];cert['search']='finite vector automaton';ans['certificate']=cert
    elif complete:
        # Small graph sufficient for replay; save full content, including all
        # costs and edge labels, so that a negative finite-cap result is concrete.
        ans['graph']=[dict(T=T,costs=dp.certificate_vector(vec),edges=adj[v],safe=v in good) for v,(vec,T) in enumerate(vectors)]
    return ans

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cap',type=int,default=7);ap.add_argument('--seconds',type=int,default=40);ap.add_argument('--maxnodes',type=int,default=5000);args=ap.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(4*1024**3,4*1024**3));signal.signal(signal.SIGALRM,alarm)
    found={r['key'] for line in (OUT/'lasso_results.jsonl').open() if (r:=json.loads(line))['certified']}
    rows=[r for r in read_rows().values() if r.get('first_ray_class')=='grows' and r.get('class_path')=='bounded' and r.get('symmetry_inequivalent') and r['key'] not in found]
    rows.sort(key=lambda r:(not r.get('mixed_path_needed'),r['main_block_size']+r['s_block_size'],r['key']))
    with gzip.open(OUT/'lasso_automaton_results.jsonl.gz','wt') as f:
        for row in rows:
            signal.alarm(args.seconds);t=time.monotonic()
            try:ans=search(row,args.cap,args.maxnodes)
            except (StopSearch,MemoryError) as ex:ans=dict(key=row['key'],cap=args.cap,complete=False,reason=str(ex),seconds=round(time.monotonic()-t,3))
            finally:signal.alarm(0)
            f.write(json.dumps(ans)+'\n');f.flush();print(json.dumps({k:v for k,v in ans.items() if k not in ['key','certificate','graph']}),flush=True)
if __name__=='__main__':main()
