"""Run all frozen obligations in scientific order and bind every numerical result."""
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys

for k in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS"):
    os.environ[k]="1"
soft,hard=resource.getrlimit(resource.RLIMIT_AS);budget=4*1024**3
resource.setrlimit(resource.RLIMIT_AS,(min(soft,budget) if soft>=0 else budget,hard))

from completions import HERE,ROOT,OUT,PRIOR
from three import save
import fixed
import panel
import separation
import verify_evidence


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    research=ROOT/"research"/HERE.parent.name;pr=research/"preregistration.md"
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    assert json.loads((HERE/"contract.json").read_bytes())["preregistration_sha256"]==digest(pr)
    fixed.step2();fixed.step3()
    subprocess.run([sys.executable,"-B",str(HERE/"holders.py")],check=True)
    panel.run();separation.run();verify_evidence.run()
    from holdings import ARCHIVE,PARTNER
    deps=[pr,research/"advisor_receipt.json",HERE/"contract.json",HERE/"identity.json",*HERE.glob("*.py"),ARCHIVE,PARTNER,
          ROOT/"research/READS-HOLDERS-SOURCES-20261120-001/decision.md",
          ROOT/"research/READS-HOLDERS-SOURCES-20261120-001A/details.md",ROOT/"research/READS-HOLDERS-SOURCES-20261120-001B/results.md",
          ROOT/"experiments/ORDINARY-DYNAMICS-20261120-001A/ORDINARY-DYNAMICS-20261120-001A-E001_ordinary/end_operator.py",
          ROOT/"tools/knotlab/knots.py",ROOT/"tools/knotlab/cli.py",ROOT/"tools/knotlab/relations.py",
          *(p for p in OUT.glob("*.json") if p.name!="receipt.json")]
    for m in tuple(sys.modules.values()):
        f=getattr(m,"__file__",None)
        if f:
            p=Path(f).resolve()
            if p.suffix==".py" and any(p.is_relative_to(ROOT/d) for d in ("experiments","proofs","tools")):
                deps.append(p)
    import numpy,scipy,networkx,sympy
    save("receipt.json",dict(sha256={str(p.relative_to(ROOT)):digest(p) for p in deps},python=sys.version.split()[0],
          libraries={k.__name__:k.__version__ for k in (numpy,scipy,networkx,sympy)},referee="pending"))


if __name__=="__main__":main()
