import sys, time, json
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import scalelib as L
for n in [int(a) for a in sys.argv[1].split(',')]:
    t=time.time()
    samp = L.SC.chain(n, int(sys.argv[2]), 99)
    cls=Counter(); dims=Counter(); rule_cmp=Counter()
    for sizes, M in samp:
        c, D = L.theorem_class(sizes, M)
        cls[c]+=1
        if c=='in':
            dims[L.label(D)]+=1
            rule_cmp[(L.label(D)==L.SC.classify(sizes, M))]+=1
    ns=sum(v for k,v in cls.items() if k!='stall')
    print(n, dict(cls), 'in-class share of non-stalling %.3f'%(cls['in']/ns if ns else 0), dict(dims), 'agree with cluster rule', dict(rule_cmp), f'{time.time()-t:.0f}s', flush=True)
