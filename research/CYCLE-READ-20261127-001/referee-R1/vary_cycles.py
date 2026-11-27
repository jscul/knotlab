"""Change the operational bounds on the originally excluded cycle-class starts."""
import argparse
import json
from pathlib import Path
import resource
import signal
import time
from core import build_core
from replay import lines, score
from reader import predict_core

def expire(*_):
    raise TimeoutError()

def entries():
    root=Path(__file__).resolve().parent
    records=[json.loads(r) for path in (root/'replay-pilot.jsonl',root/'replay.jsonl')
             for r in path.read_text().splitlines()]
    for group in ('cyc6_uniform','cyc7_treeplus','cyc7_grow'):
        starts=lines(group+'.jsonl')
        laws={law:lines(f'grown_{group}_{law}.jsonl.gz') for law in ('nae','parity')}
        for r in records:
            if r['group']==group and (r['nae']['actual'] in ('excluded','growth not run')
                                      or any(p['core']=='rank limit' for p in r['pcs'])):
                i=r['line']-1
                yield group,r['key'],starts[i]['stars'],{law:g[i] for law,g in laws.items()}

def compare(stars, laws):
    core=build_core(stars, max_rank=51, max_births=20_000, group_work=5_000_000)
    result={'pieces':[[p.stop,p.birth_count,max(p.ranks)-1,p.twin_rank-1 if p.twin else None]
                      for p in core.pieces]}
    for law,g in laws.items():
        if g['end']=='not run (time limit)':
            result[law]='growth not run'
            continue
        pred,why=predict_core(core,24,law)
        result[law]=score(g,pred) if pred is not None else why
    return result

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('lo',type=int)
    ap.add_argument('hi',type=int)
    args=ap.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(1800<<20,1800<<20))
    signal.signal(signal.SIGALRM,expire)
    for i,(group,key,s,g) in enumerate(entries()):
        if not args.lo<=i<=args.hi:
            continue
        start=time.perf_counter()
        signal.setitimer(signal.ITIMER_REAL,3)
        try:
            row=compare(s,g)
        except (TimeoutError,MemoryError) as e:
            row={'cut':type(e).__name__}
        finally:
            signal.setitimer(signal.ITIMER_REAL,0)
        print(json.dumps(dict(group=group,key=key,seconds=round(time.perf_counter()-start,4),**row)),flush=True)
