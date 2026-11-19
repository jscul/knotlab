"""Pilot: each provisional break-shape eddy grown in its own child (6 GB address space, 900 s), to 40 rounds or 300,000
junctions, its counts printed after every round."""
import json, resource, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
HERE = Path(__file__).resolve().parent
LC = HERE.parents[2] / 'LOOP-CATALOGUE-20261119-001B/LOOP-CATALOGUE-20261119-001B-E001_catalogue'
CHILD = r'''
import json, sys
sys.path.insert(0, sys.argv[1])
import eddy as E
st = json.loads(sys.argv[2])
P = E.J.S.from_junctions(E.J.stars_from(st['sizes'], [tuple(x) for x in st['edges']]))
P.linalg = False
for _ in range(40):
    r = P.step(E.J.F.fewest, None)
    if r is None or r['new'] == 0:
        break
    print(json.dumps(P.counts_by_round()), flush=True)
    if len(P.bits_of) > 300000:
        break
'''
def one(st):
    lim = lambda: resource.setrlimit(resource.RLIMIT_AS, (6 * 2 ** 30, 6 * 2 ** 30))
    try:
        p = subprocess.run([sys.executable, '-B', '-c', CHILD, str(LC), json.dumps(st)], capture_output=True, text=True, timeout=900, preexec_fn=lim)
        lines, why = p.stdout.strip().splitlines(), ('ok' if p.returncode == 0 else 'limit')
    except subprocess.TimeoutExpired as ex:
        out = ex.stdout.decode() if isinstance(ex.stdout, bytes) else (ex.stdout or '')
        lines, why = out.strip().splitlines(), 'time'
    return dict(st, counts=json.loads(lines[-1]) if lines else None, stopped=why)
sts = json.loads((HERE / 'provisional.json').read_text())
with ThreadPoolExecutor(3) as ex:
    res = list(ex.map(one, sts))
(HERE / 'grown_long.json').write_text(json.dumps(res))
print('done', sum(r['counts'] is not None for r in res))
