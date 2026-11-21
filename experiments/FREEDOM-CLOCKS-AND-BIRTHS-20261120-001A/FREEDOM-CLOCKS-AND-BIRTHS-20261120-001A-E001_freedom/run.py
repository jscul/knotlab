"""Reproduce the six frozen freedom-rule steps and bind their exact input and output records."""
import gzip
import json
import os
from pathlib import Path
import resource
import subprocess
import sys

for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[k]='1'
soft,hard=resource.getrlimit(resource.RLIMIT_AS);limit=4*1024**3
resource.setrlimit(resource.RLIMIT_AS,(min(soft,limit) if soft>=0 else limit,hard))
from words import HERE,ROOT,OUT,save,sha
import calibrations
import histories
import native_events
import freedom_validation


def main():
    research=ROOT/'research'/HERE.parent.name;freeze=research/'preregistration.md'
    assert json.loads((HERE/'contract.json').read_text())['preregistration_sha256']==sha(freeze)
    calibrations.first();calibrations.combined()
    subprocess.run([sys.executable,'-B',str(HERE/'archive_replay.py')],check=True)
    calibrations.rivals();native_events.run();histories.run();freedom_validation.run()
    previous='READS-HOLDERS-SOURCES-20261120-001A';old='THREE-READERS-AND-GROWTH-20261120-001A'
    files={freeze,research/'advisor_receipt.json',HERE/'identity.json',HERE/'contract.json',*HERE.glob('*.py'),
           *(p for p in OUT.iterdir() if p.name!='receipt.json'),ROOT/'research'/previous/'motion.md',
           ROOT/'research'/old/'readings.md',ROOT/'research'/old/'holders.md',
           next((ROOT/'artifacts'/previous).glob('*/motion.json')),
           ROOT/'research/BOND-CLOSURE-20261120-001/criterion.md',ROOT/'research/BOND-CLOSURE-20261120-001/eight_inputs.md',
           ROOT/'research/ORDINARY-DYNAMICS-20261120-001/end_operator.md',
           ROOT/'research/STATE-FEEDS-GROWTH-20261119-001/decision.md',
           ROOT/'research/MOTION-AT-EDDY-20261119-001/b_updates.md',ROOT/'research/MOTION-LAW-20261119-001/what_is_forced.md',
           ROOT/'research/FOUR-READINGS-20261120-001A/supplemental_stress_freeze.md',
           ROOT/'proofs/WALL-READ-20261119-001A/WALL-READ-20261119-001A-P001_partnered/proof.md'}
    for epic in ('READS-HOLDERS-SOURCES-20261120-001','THREE-READERS-AND-GROWTH-20261120-001'):
        files.add(ROOT/'research'/epic/'decision.md')
    from holdings import ARCHIVE,PARTNER
    files.update((ARCHIVE,PARTNER))
    archive=json.loads(gzip.decompress((OUT/'archive_replay.json.gz').read_bytes()))
    for name,h in archive['inputs'].items():
        source=ROOT/name;assert sha(source)==h;files.add(source)
    for m in tuple(sys.modules.values()):
        f=getattr(m,'__file__',None)
        if f:
            p=Path(f).resolve()
            if p.suffix=='.py' and any(p.is_relative_to(ROOT/d) for d in ('experiments','tools','proofs')):files.add(p)
    files.update((ROOT/'tools/knotlab').glob('*.py'))
    import motion_stage,sources
    from holdings import J
    files.update((motion_stage.STAGES,motion_stage.INPUTS,sources.PRIOR/'holdout.json',
                  Path(motion_stage.growth_engine().__file__),Path(J.__file__)))
    import numpy,scipy,networkx
    save('receipt.json',dict(sha256={str(p.relative_to(ROOT)):sha(p) for p in files},python=sys.version.split()[0],
          libraries={m.__name__:m.__version__ for m in (numpy,scipy,networkx)},referee='pending'))


if __name__=='__main__':main()
