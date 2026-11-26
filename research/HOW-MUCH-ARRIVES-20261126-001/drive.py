"""drive.py OUT [WORKERS]: every job of amount.py (setting A; under not-all-equal, and the marks, moves and round-2
made marks again under parity) and of between.py (setting B), each its own run under a memory cap of 4 GB and a
clock of 30 minutes, written one JSON line each as they finish."""
import sys, os, json, subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
out = sys.argv[1]; workers = int(sys.argv[2]) if len(sys.argv) > 2 else 6
A = [json.loads(l) for l in subprocess.run([PY, '-B', os.path.join(HERE, 'amount.py'), 'list'], capture_output=True, text=True).stdout.splitlines()]
jobs = [('amount.py', ['one', json.dumps(j)]) for j in A]
jobs += [('amount.py', ['one', json.dumps(dict(j, **{'knot law': 'parity'}))]) for j in A
         if j['change'] in ('mark', 'move') or (j['change'] == 'made' and j['round'] == 2)]
jobs += [('between.py', ['b1', str(d), law]) for d in range(1, 9) for law in ('REC-ONE-FEWER', 'ORD')]
jobs += [('between.py', ['b2', str(d), law]) for d in range(2, 6) for law in ('CAP-3', 'ORD')]
def one(job):
    prog, args = job
    p = subprocess.run(['systemd-run', '--user', '--scope', '-q', '-p', 'MemoryMax=4G', '-p', 'MemorySwapMax=0', 'timeout', '1800',
                        PY, '-B', os.path.join(HERE, prog)] + args, capture_output=True, text=True)
    try: return json.dumps(json.loads(p.stdout.strip().splitlines()[-1]))
    except Exception: return json.dumps({'job': [prog] + args, 'not run': 'the clock' if p.returncode == 124 else 'return code %d' % p.returncode, 'err': p.stderr[-400:]})
with ThreadPoolExecutor(workers) as ex, open(out, 'w') as f:
    futs = [ex.submit(one, j) for j in jobs]
    for k, fu in enumerate(as_completed(futs)):
        f.write(fu.result() + '\n'); f.flush()
print(len(jobs), 'jobs done')
