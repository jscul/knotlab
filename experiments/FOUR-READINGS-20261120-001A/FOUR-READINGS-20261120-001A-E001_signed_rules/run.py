"""Ordered, deterministic replay of the five questions. Use the repository's .venv."""
import hashlib
import os
from pathlib import Path
import resource
import time

os.environ['OPENBLAS_NUM_THREADS']='1'
budget=4*1024**3
soft,hard=resource.getrlimit(resource.RLIMIT_AS)
resource.setrlimit(resource.RLIMIT_AS,(min(budget,soft) if soft>=0 else budget,hard))

import census
import controls
import games
import growth


def main():
    start=time.monotonic()
    stages=[]
    def run(label,function,*args):
        local=time.monotonic()
        outcome=function(*args)
        stages.append(dict(step=label,elapsed_seconds=round(time.monotonic()-local,4)))
        return outcome
    six=run('2. Six rules and the complete two-reader records',games.run_six)
    run('3. Small sharing census and operator witnesses',census.run)
    run('4. Ordinary growth, inverse closures, and both-law controls',growth.run)
    run('5. Negative comparison, promised/independent settings',games.run_comparison,*six)
    run('Certificate, sign, and marker replay',controls.main)
    digest=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
    frozen=census.ROOT/'research'/census.HERE.parent.name/'preregistration.md'
    meta=dict(design_sha256=digest(frozen),contract_sha256=digest(census.HERE/'contract.json'),
              stages=stages,elapsed_seconds=round(time.monotonic()-start,4),
              peak_kib=max(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                           resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss),
              python_version=os.sys.version.split()[0],networkx_version=census.nx.__version__,
              output_sha256={p.name:digest(p) for p in sorted(census.OUT.glob('*.json'))
                             if p.name not in ('receipt.json','supplemental_stress.json')})
    census.save('receipt.json',meta)
    print('Completed ordered replay in',meta['elapsed_seconds'],'seconds at',meta['peak_kib'],'KiB peak')


if __name__=='__main__':
    main()
