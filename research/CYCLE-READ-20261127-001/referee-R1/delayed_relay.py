"""A cycle-class core that finishes one round beyond the study's horizon."""
import json
import random
from pathlib import Path
import sys
import time

from core import build_core
from reader import predict_core
from sample import make_start
sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'LOOK-ALIKE-20261126-001'))
from alike import grow


def fixture(length):
    blocks = [{0,1}, {0,2}, {1,2}, {0,3}, {1,3}]
    last = 2
    loose = [2,2,1,1]
    for i in range(4,4+length):
        blocks.append({last,i})
        loose[last] += 1
        loose.append(1)
        last = i
    return make_start(blocks, loose, random.Random(5187))


def check(length):
    start = time.perf_counter()
    s = fixture(length)
    horizon = build_core(s, max_rank=26)
    full = build_core(s, max_rank=35)
    p, = full.pieces
    result = dict(knots=len(s), cycle=p.cycle, chains=sum(p.chains.values()), twin=p.twin_rank,
                  cap25=horizon.pieces[0].stop, rank_sizes=[len(v) for v in p.ranks.values()],
                  terminal_round=max(p.ranks)-1, core_births=p.birth_count)
    for law in ('nae','parity'):
        g = grow(s,29,30000,law)
        pred, _ = predict_core(full,29,law)
        t=max(p.ranks)-2
        assert g['rows']==pred[:len(g['rows'])]
        result[law]=dict(end=g['end'], terminal=g['rows'][t]['sig0'],
                         following=[v['n'] for v in g['rows'][t+1:]])
    result['seconds']=round(time.perf_counter()-start,4)
    return result

if __name__=='__main__':
    print(json.dumps(check(int(sys.argv[1]))))
