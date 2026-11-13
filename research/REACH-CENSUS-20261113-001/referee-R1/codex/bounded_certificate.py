"""Fresh finite positive certificates, retaining only paths of cost <= B.

Each layer maps a summary state to its least cost, discarding costs above B.
An exactly repeated layer recurs forever. If every closing value on that repeat
is finite and <=B, it proves eventual boundedness, even without a complete full
graph. Nonnegative costs make this cost truncation sound. States whose
one-forgotten family already contains the empty mask can never accept and are
discarded. This is a separate positive certificate, not a negative decision.
"""
from collections import Counter
import argparse
import json
import resource
import signal
import time
import fresh_recompute as R

def certify(p,bound,limit=500):
    dp=R.DynamicProgram(p)
    layer={st:c for st,c in dp.starts.items() if c<bound and not st[1]&1}
    seen={}; values=[]
    for depth in range(1,limit+1):
        code=frozenset(layer.items())
        if code in seen:
            onset=seen[code]
            tail=values[onset-1:]
            good=bool(tail) and all(x<=bound for x in tail)
            return dict(certified=good,uniform_cost_bound=bound,onset_depth=onset,
                        period=depth-onset,L_ray_capped=values,
                        repeated_layer_size=len(layer),reason='exact layer repeat')
        seen[code]=depth
        value=min((c+dp.close(st) for st,c in layer.items()),default=R.INF)
        values.append(value if value<=bound else R.INF)
        nxt={}
        for st,c in layer.items():
            for action in dp.middle:
                cost=c+action.cost
                if cost>=bound: continue  # closing selects >=1 member
                ns=action.apply(st)
                if ns[1]&1: continue
                if cost<nxt.get(ns,R.INF): nxt[ns]=cost
        layer=nxt
    return dict(certified=False,reason='layer repeat not reached',L_ray_capped=values)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--all',action='store_true',help='all 131 reported bounded stress-test families')
    args=ap.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(6*1024**3,6*1024**3))
    signal.signal(signal.SIGALRM,R.timeout)
    selected=[json.loads(x) for x in (R.HERE/'fresh_alternative.jsonl').read_text().splitlines()]
    if args.all:
        selected=[dict(key=r['key'],reported=dict(uniform_cost_bound=r['uniform_cost_bound']))
                  for r in R.rows('alt_growing664_families.jsonl.gz') if r['class']=='bounded']
    results=[]
    for r in selected:
        signal.alarm(5 if args.all else 20); started=time.monotonic()
        out=dict(key=r['key'],reported_bound=r['reported']['uniform_cost_bound'])
        try:
            p=R.Pattern(r['key'],'last')
            out.update(certify(p,r['reported']['uniform_cost_bound']))
            out['status']='done'
        except (MemoryError,TimeoutError,RuntimeError) as e:
            out.update(status='resource_failure',error=repr(e))
        finally:
            signal.alarm(0); R.DynamicProgram.close.cache_clear(); R.image_table.cache_clear()
        out['seconds']=time.monotonic()-started
        out['peak_rss_kib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        results.append(out)
        print(json.dumps({k:out.get(k) for k in ['status','certified','uniform_cost_bound','onset_depth','period','seconds']}),flush=True)
    R.save('all131_positive_certificates.json' if args.all else 'alternative_positive_certificates.json',results)

if __name__=='__main__': main()
