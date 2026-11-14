"""Repair a sample of the independently unretrievable union-death evidence.

Fresh NAE formulas, a different SAT producer (Glucose4), and the old referee's
hint-free RUP checker. This does not repair the study's original retention.
"""
import gzip
import hashlib
import importlib.util
import json
import resource
import sys
import time
from pathlib import Path
from pysat.solvers import Solver
from fresh_pattern import build, cnf

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
spec = importlib.util.spec_from_file_location('old_referee_rup',ROOT/'research/ADDR-KNOTS-20261113-001/referee-R1/codex/check_rup.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def main():
    resource.setrlimit(resource.RLIMIT_AS,(3<<30,3<<30))
    out = HERE/'dead_refutations'
    out.mkdir(exist_ok=True)
    data = ROOT/'artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/records_slim.jsonl.gz'
    records = [json.loads(l) for l in gzip.open(data,'rt')]
    dead = sorted((r for r in records if r['union']=='dead'),key=lambda r:r['case'])
    selected = [r for r in dead if any(m['family']=='W_R' and m['index']<2000 for m in r['memberships'])][:3]
    result = []
    for r in selected:
        start = time.monotonic()
        knots = build(r['key'],9)
        formula = cnf(knots)
        with Solver(name='glucose4',bootstrap_with=formula,with_proof=True) as solver:
            solver.conf_budget(100000)
            answer = solver.solve_limited()
            proof = solver.get_proof() if answer is False else None
        row = {'case':r['case'],'key':r['key'],'solver':'glucose4','N':9,'conflict_budget':100000,
               'result':'dead' if answer is False else ('alive' if answer else 'undecided')}
        if proof is not None:
            raw = f'p cnf 1023 {len(formula)}\n' + ''.join(' '.join(map(str,c))+' 0\n' for c in formula)
            drup = '\n'.join(proof)+'\n'
            row['check'] = mod.RUPChecker(formula,1023).check(proof)
            assert row['check']['valid'], row
            digest = hashlib.sha256(raw.encode()).hexdigest()
            for ext,text in [('cnf',raw),('drup',drup)]:
                path = out/(digest+'.'+ext+'.gz')
                with gzip.open(path,'wt') as f:
                    f.write(text)
                row[ext+'_path'] = str(path.relative_to(HERE))
                row[ext+'_sha256_uncompressed'] = hashlib.sha256(text.encode()).hexdigest()
        row['seconds'] = time.monotonic()-start
        result.append(row)
        print(json.dumps({'case':r['case'][:16],'result':row['result'],'RUP':row.get('check'),
                          'seconds':row['seconds']}),flush=True)
    summary = {'scope':'three deterministic weighted-dead keys; original study union certificates still unbound',
               'results':result,'peak_rss_MiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024}
    (HERE/'dead_recomputation.json').write_text(json.dumps(summary,indent=2)+'\n')


if __name__=='__main__':
    main()
