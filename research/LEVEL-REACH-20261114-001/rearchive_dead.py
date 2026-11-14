"""After LEVEL-REACH-R1 (Block 2): re-solve the dead union patterns of the registered run, keep each CNF and LRAT proof
(gzip, named by the CNF's SHA-256) and record the hashes. Uses the reach code's pattern builder and LEVEL-RETURN's certifier."""
import sys, os, json, gzip, shutil
sys.path.insert(0, 'scripts')
sys.path.insert(0, 'experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex')
KEEP = os.path.abspath('experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex/certificates/union_dead')
os.environ['CERT_KEEP_DIR'] = KEEP
sys.path.insert(0, 'experiments/LEVEL-RETURN-20261113-001A/LEVEL-RETURN-20261113-001A-E001_certified_levels')
from longrun import load_results
from pattern import pattern
import certify
R = load_results('experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex/registered')
dead = [v['result'] for v in R.values() if v.get('status') == 'ok' and v['result']['union']['verdict'] == 'dead']
out = []
wd = os.path.abspath('research/LEVEL-REACH-20261114-001/work_dead')
for r in dead:
    shutil.rmtree(wd, ignore_errors=True); os.makedirs(wd)
    K = pattern(r['key'], 9)
    import numpy as np
    c = certify.certify(np.asarray(K, dtype=np.int64).reshape(-1, 3), (1 << 10) - 1, wd, 1800)
    out.append(dict(case=r['case'], verdict=c['verdict'], certificate=c['certificate']))
    print(r['case'][:12], c['verdict'], c['certificate'][:120], flush=True)
shutil.rmtree(wd, ignore_errors=True)
json.dump(out, open('artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/union_dead_certificates.json', 'w'), indent=1)
print(len(out), sum(o['verdict'] == 'dead' for o in out))
