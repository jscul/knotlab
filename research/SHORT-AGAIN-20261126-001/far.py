"""far.py OUT [WORKERS]: the one pair that heard from afar on the bench (two seven-knot sources joined by a meeting,
with waiting), read with reach.py's changes at distances 1 to 8 and to 16 rounds, under every ration here and the
ordinary count, with waiting and, as a control, with retiring.  96 cases, each its own run under a memory cap of
8 GB and a stop at five minutes.  `far.py one D RATION TREATMENT` runs one."""
import sys, os, json, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
if sys.argv[1] == 'one':
    import reach
    r = reach.case('source', 'source', int(sys.argv[2]), sys.argv[3], sys.argv[4]); print(json.dumps(r))
else:
    from concurrent.futures import ThreadPoolExecutor
    PY = sys.executable; out = sys.argv[1]; workers = int(sys.argv[2]) if len(sys.argv) > 2 else 16
    jobs = [(d, ra, tr) for d in range(1, 9) for ra in ('ORD', 'JOIN-FEWER', 'BUSY-FEWER', 'ONE-FEWER', 'ODD-FEWER', 'THIRD-FEWER') for tr in ('CANCEL-WAIT', 'CANCEL-RETIRE')]
    def one(j):
        p = subprocess.run(['systemd-run', '--user', '--scope', '-q', '-p', 'MemoryMax=8G', '-p', 'MemorySwapMax=0', 'timeout', '300',
                            PY, '-B', os.path.join(HERE, 'far.py'), 'one', str(j[0]), j[1], j[2]], capture_output=True, text=True)
        try: return json.dumps(json.loads(p.stdout.strip().splitlines()[-1]))
        except Exception: return json.dumps({'job': list(j), 'not run': 'the clock' if p.returncode == 124 else 'return code %d' % p.returncode})
    with ThreadPoolExecutor(workers) as ex, open(out, 'w') as f:
        for line in ex.map(one, jobs): f.write(line + '\n'); f.flush()
    print(len(jobs), 'cases done')
