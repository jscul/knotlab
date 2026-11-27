"""Recheck the predecessor's completed rows and its held seven-knot growth sample."""
import argparse
from collections import Counter
import json
from pathlib import Path
import resource
import time
from core import build_core
from reader import predict_core
from replay import score

OLD=Path(__file__).resolve().parents[2]/'GRADED-ORDER-20261126-001'
def rows(p):
    return [json.loads(l) for l in p.read_text().splitlines()]
def check(lo,hi):
    out=[]
    for source in ('fresh7_grow','fresh7_treeplus','held_grow','held_treeplus','held8_treeplus','replays'):
        g={law:rows(OLD/f'grown_{source}_{law}.jsonl') for law in ('nae','parity')}
        old={law:rows(OLD/f'nodesg_{source}_{law}.jsonl') for law in g}
        for i in range(lo,min(hi,len(g['nae']))):
            t=time.perf_counter()
            x=g['nae'][i]
            assert x['stars']==g['parity'][i]['stars']
            row=dict(source=source, line=i+1)
            if any('error' in old[law][i] for law in g):
                row['old_cap']=True
            else:
                c=build_core(x['stars'],max_rank=130)
                row['twin_round']=min((p.twin_rank-1 for p in c.pieces if p.twin),default=None)
                for law in g:
                    pred,why=predict_core(c,24,law)
                    got=score(g[law][i],pred) if pred is not None else why
                    row[law]=got
                    row[law+'_stored']=old[law][i]['node reading'] or 'agrees'
            row['seconds']=round(time.perf_counter()-t,4)
            out.append(row)
    return out

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('lo',type=int)
    ap.add_argument('hi',type=int)
    args=ap.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(1400<<20,1400<<20))
    for r in check(args.lo,args.hi):
        print(json.dumps(r))
