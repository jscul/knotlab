"""Replay the seven frozen obligations on the exact same physical starts and questions."""
import json
import os
from pathlib import Path
import resource
import subprocess
import sys

for key in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"):
    os.environ[key]="1"
soft,hard=resource.getrlimit(resource.RLIMIT_AS)
limit=4*1024**3
resource.setrlimit(resource.RLIMIT_AS,(min(limit,soft) if soft>=0 else limit,hard))
from operations import HERE,ROOT,OUT,BASELINE,save,sha
import audits
import chains
import holdings
import tables


def motion(part):
    subprocess.run([sys.executable,"-B",str(HERE/"motion.py"),part],check=True,env=dict(os.environ,PYTHONHASHSEED="7"))


def main():
    pr=ROOT/"research"/HERE.parent.name/"preregistration.md"
    with (HERE/"contract.json").open() as source:
        assert json.load(source)["preregistration_sha256"]==sha(pr)
    motion("rings")
    tables.step3()
    tables.minimum_census()
    tables.step4_separated()
    chains.run()
    motion("maps")
    holdings.run_samples()
    tables.step6()
    tables.step7_counts()
    motion("phase")
    audits.run()
    archived=[BASELINE,holdings.ARCHIVE,holdings.PARTNER,
              ROOT/"research/MOTION-AT-EDDY-20261119-001/ring_state.md",
              ROOT/"research/MOTION-LAW-20261119-001/uniform_exchange.md",
              ROOT/"research/INTERFERENCE-20261029-001/interference.md",
              ROOT/"experiments/NAE-GROWTH-20261119-001B/NAE-GROWTH-20261119-001B-E001_nae/naelib.py",
              ROOT/"experiments/ENTANGLEMENT-READ-20261120-001B/ENTANGLEMENT-READ-20261120-001B-E001_separated_readings/exact_counts.py",
              holdings.OLD/"growth.py"]
    ring_family=ROOT/"experiments/MOTION-AT-EDDY-20261119-001/MOTION-AT-EDDY-20261119-001-E001_motion"
    old_motion=ROOT/"experiments/MOTION-LAW-20261119-001/MOTION-LAW-20261119-001-E001_rules"
    archived.extend(ring_family/n for n in ("inputs.json","holdout.json","motion_stage.py","b_updates.py","nearness.py"))
    archived.extend(old_motion/n for n in ("sources.py","permutation_controls.py","uniform_exchange.py","exchange.py"))
    archived.extend([ROOT/"artifacts/EDDY-WORLD-20261119-001/EDDY-WORLD-20261119-001-E001_world/stages.json",
                     ROOT/"experiments/EDDY-WORLD-20261119-001/EDDY-WORLD-20261119-001-E001_world/world_growth.py",
                     ROOT/"tools/knotlab/knots.py",ROOT/"tools/knotlab/relations.py",ROOT/"tools/knotlab/cli.py"])
    for module in tuple(sys.modules.values()):
        origin=getattr(module,"__file__",None)
        if origin:
            origin=Path(origin).resolve()
            if origin.suffix==".py" and any(origin.is_relative_to(ROOT/f) for f in ("experiments","proofs","tools")):
                archived.append(origin)
    paths=[pr,*HERE.glob("*.py"),HERE/"contract.json",HERE/"identity.json",*archived,
           *(p for p in OUT.glob("*.json") if p.name!="receipt.json")]
    import networkx,numpy,scipy
    save("receipt.json",dict(sha256={str(p.relative_to(ROOT)):sha(p) for p in paths},
         python=sys.version.split()[0],numpy=numpy.__version__,scipy=scipy.__version__,networkx=networkx.__version__,
         canonical="projected law types at widths three through eight plus the literal ring and motion preparations",
         independent_referee="pending"))


if __name__=="__main__":
    main()
