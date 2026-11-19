"""Amendment (logged in contract.json): part U's shards that exceeded memory, rerun with each start grown in its own child
process, limited to 3 GB of address space and 90 s, which prints its counts after every round.  A child stopped by the limit is
recorded as 'over limit' with the counts it finished; otherwise the class is eddy.growth_class's rule applied to its counts.
Same starts and caps as job.py's part U (30 rounds, 5,000 junctions).  `--param only=<id>,...` selects the shards."""
import importlib.util
import json
import resource
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location('loop_catalogue_job', HERE / 'job.py')
job = importlib.util.module_from_spec(_spec)
sys.modules['loop_catalogue_job'] = job
_spec.loader.exec_module(job)
E = job.E

CHILD = r'''
import json, sys
sys.path.insert(0, sys.argv[1])
import eddy as E
st = json.loads(sys.argv[2])
P = E.J.S.from_junctions(E.J.stars_from(st['sizes'], [tuple(x) for x in st['edges']]))
P.linalg = False
out = 'alive'
for _ in range(30):
    r = P.step(E.J.F.fewest, None)
    if r is None:
        out = 'stall'; break
    if r['new'] == 0:
        out = 'closed'; break
    print(json.dumps({'counts': P.counts_by_round(), 'outcome': 'alive'}), flush=True)
    if len(P.bits_of) > 5000:
        out = 'cap'; break
print(json.dumps({'counts': P.counts_by_round(), 'outcome': out}), flush=True)
'''

ONLY = None


def setup(params):
    global ONLY
    ONLY = set(params.get('only', '').split(','))


def cases():
    for cid, pay in job.cases():
        if ONLY is None or cid in ONLY:
            yield cid, pay


def classify(c, out):
    if out in ('stall', 'closed'):
        return out
    W = 16
    if len(c) >= W + 8:
        for k in range(1, 7):
            for p in range(1, 13):
                d = list(c)
                for _ in range(k):
                    d = [d[i + p] - d[i] for i in range(len(d) - p)]
                if len(d) >= W and all(x == 0 for x in d[-W:]):
                    return f'dim{k}'
    if out == 'cap':
        return 'exp' if len(c) >= 3 and c[-1] >= 1.1 * c[-2] else 'unsettled'
    if len(c) >= 12 and c[-1] > c[-6] > c[-11]:
        return 'exp?'
    return 'unsettled'


def grow_isolated(st):
    def limit():
        resource.setrlimit(resource.RLIMIT_AS, (3 * 2 ** 30, 3 * 2 ** 30))
    try:
        p = subprocess.run([sys.executable, '-B', '-c', CHILD, str(HERE), json.dumps(st)], capture_output=True, text=True,
                           timeout=90, preexec_fn=limit)
        lines, killed = p.stdout.strip().splitlines(), p.returncode != 0
    except subprocess.TimeoutExpired as ex:
        lines, killed = (ex.stdout or b'').decode().strip().splitlines() if isinstance(ex.stdout, bytes) else (ex.stdout or '').strip().splitlines(), True
    last = json.loads(lines[-1]) if lines else {'counts': [len(st['sizes'])], 'outcome': 'alive'}
    if killed:
        return 'over limit', last['counts']
    return classify(last['counts'], last['outcome']), last['counts']


def run(case_id, payload):
    out = []
    for st in payload['starts']:
        sz, e = st['sizes'], [tuple(x) for x in st['edges']]
        A = E.analyse_all(sz, e)
        P = E.pieces(A)
        cls, c = grow_isolated(st)
        out.append(dict(st, growth=cls, counts=c[:30], meet=any(p[4] and p[2] >= 1 for p in P),
                        broken=bool(E.broken_blocks(A)), scope=A['scope']))
    return {'starts': out}
