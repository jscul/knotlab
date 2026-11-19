import json, sys, glob
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import eddy as E, sampler as S
for f in sorted(glob.glob(str(HERE / 'random_*_*000000.json'))):
    n = int(f.split('_')[-2])
    for r in json.load(open(f)):
        if r.get('growth') and r['rule'] == 'False' and r['rule_with_h'] == 'True':
            sz, e = S.sample(n, r['seed'])
            A = E.Cl.analyse(sz, e)
            hyp = [list(B) for i, B in enumerate(A['blocks']) if A['bedges'][i] is None]
            other = [list(B) for i, B in enumerate(A['blocks']) if A['bedges'][i] is not None]
            pr = E.Cl.series(sz, e, 20)
            print(n, r['seed'], r['growth'], 'grown', r['counts'][:14], 'rule', pr[:14] if isinstance(pr, list) else pr)
            print('    blocks', other, 'hyper', hyp, 'pend', {k: v for k, v in A['pend'].items() if v})
