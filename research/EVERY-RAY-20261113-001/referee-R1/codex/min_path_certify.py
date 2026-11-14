"""Independent per-depth minimum check using the fresh referee DP.

This differs deliberately from a single lasso: each node's cost may use a
different call word. It certifies forall depth exists path, not the reverse.
"""
import argparse, gzip, hashlib, json, resource, signal, time
from pathlib import Path
from lasso_certify import DP, INF, OUT, read_rows, transport

class FamilyTimeout(Exception):pass
def timeout(sig,frame):raise FamilyTimeout('per-family wall cap')

def run(row,seconds=40):
    start=time.monotonic()
    ub=(row.get('uncarried_result') or {}).get('uniform_cost_bound')
    cap=max(7,int(ub or 7))
    dp=DP(json.loads(row['key']),cap)
    assert (dp.S,dp.main.n,dp.mid.n)==(row['S'],row['main_block_size'],row['s_block_size'])
    layer={}
    for e,a in enumerate(dp.main.calls):
        T=sum(1<<j for j,v in enumerate(a) if v<dp.main.k)
        for v,c in dp.start(e).items():layer[v,T]=min(layer.get((v,T),INF),c)
    seen={};plain=[];unc=[];mismatch=[]
    for s in range(1,151):
        z=min((c+dp.close(v) for (v,T),c in layer.items()),default=INF)
        u=min((c+dp.close(v) for (v,T),c in layer.items() if T==0),default=INF)
        plain.append(z if z<=cap else None);unc.append(u if u<=cap else None)
        for label,val,field in [('plain',z,'L_path'),('uncarried',u,'L_path_uncarried')]:
            if s<=len(row.get(field,[])):
                expected=row[field][s-1]
                if (expected<=cap and expected!=val) or (val<=cap and expected!=val):mismatch.append(dict(depth=s,which=label,value=val,expected=expected))
        sig=tuple(sorted((v,T,c) for (v,T),c in layer.items()))
        if sig in seen:
            begin=seen[sig]
            tail=unc[begin-1:s-1]
            serial=sorted([[str(dp.states[v][0]),str(dp.states[v][1]),T,c] for (v,T),c in layer.items()])
            return dict(key=row['key'],complete=True,cap=cap,repeat_from_depth=begin,repeat_at_depth=s,period=s-begin,certified_uncarried_bounded=all(x is not None for x in tail),eventual_uncarried_bound=max(tail) if all(x is not None for x in tail) else None,plain=plain,uncarried=unc,residue_values=tail,vector_sha256=hashlib.sha256(json.dumps(serial,separators=(',',':')).encode()).hexdigest(),vector=serial,vector_states=len(layer),dp_states=len(dp.states),comparisons=min(s,len(row.get('L_path',[]))),mismatches=mismatch,seconds=round(time.monotonic()-start,3),row_uncarried_class=row.get('class_path_uncarried'))
        seen[sig]=s
        nl={}
        for (v,T),c in layer.items():
            for i,a in enumerate(dp.mid.calls):
                U=transport(T,a)
                for w,d in dp.edges(v,i):
                    cost=c+d
                    if cost<cap and cost<nl.get((w,U),INF):nl[w,U]=cost
        layer=nl
        if time.monotonic()-start>seconds:raise FamilyTimeout('per-family wall cap')
        if len(dp.states)>100000:raise RuntimeError('state cap')
    return dict(key=row['key'],complete=False,reason='150 layers without repeat',plain=plain,uncarried=unc,mismatches=mismatch)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--only-unfound',action='store_true');ap.add_argument('--seconds',type=int,default=40);ap.add_argument('--output',default='min_path_results.jsonl.gz');ap.add_argument('--limit',type=int,default=204);args=ap.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(4*1024**3,4*1024**3))
    signal.signal(signal.SIGALRM,timeout)
    rows=[r for r in read_rows().values() if r.get('first_ray_class')=='grows' and r.get('class_path')=='bounded' and r.get('symmetry_inequivalent')]
    rows.sort(key=lambda r:(not r.get('mixed_path_needed'),r['main_block_size']+r['s_block_size'],r['key']))
    if args.only_unfound:
        certs={r['key'] for line in (OUT/'lasso_results.jsonl').open() if (r:=json.loads(line))['certified']}
        rows=[r for r in rows if r['key'] not in certs]
    dest=OUT/args.output;done=set()
    opener=lambda mode:gzip.open(dest,mode+'t') if dest.suffix=='.gz' else dest.open(mode)
    if dest.exists():
        with opener('r') as f:done={json.loads(line)['key'] for line in f}
    with opener('a') as f:
        for row in rows[:args.limit]:
            if row['key'] in done:continue
            t=time.monotonic();signal.alarm(args.seconds)
            try:r=run(row,args.seconds)
            except (FamilyTimeout,MemoryError,RuntimeError,AssertionError) as ex:r=dict(key=row['key'],complete=False,reason=str(ex),seconds=round(time.monotonic()-t,3))
            finally:signal.alarm(0)
            f.write(json.dumps(r)+'\n');f.flush()
            print(json.dumps({k:r.get(k) for k in ['complete','certified_uncarried_bounded','eventual_uncarried_bound','period','vector_states','dp_states','seconds','reason','mismatches']}),flush=True)
if __name__=='__main__':main()
