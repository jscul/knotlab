import sys
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import eddy as E, sampler as S
for n in (6, 8, 10, 12):
    fr, nb, cnt = [], [], 0
    for s in range(n * 1000000, n * 1000000 + 20000):
        sz, e = S.sample(n, s)
        A = E.Cl.analyse(sz, e)
        if not A['scope'] or A['stall'] or not A['live']:
            continue
        cnt += 1
        big = max((len(B) for B in A['blocks']), default=0)
        fr.append(big / len(A['live']))
        nb.append(len(A['blocks']))
    fr.sort()
    print(n, cnt, 'largest block / live knots: median', round(fr[len(fr)//2], 2), 'mean', round(sum(fr)/len(fr), 2), 'mean blocks', round(sum(nb)/len(nb), 2), flush=True)
