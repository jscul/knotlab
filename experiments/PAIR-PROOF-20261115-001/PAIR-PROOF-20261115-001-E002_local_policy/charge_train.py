"""Price the full model-fitting process, including Python startup, freeze writes and exit."""
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
OUT=ROOT/"artifacts"/HERE.parent.name/HERE.name


def main():
    cost=OUT/"training-cost.json"
    if cost.exists():
        raise FileExistsError(cost)
    wall=time.perf_counter_ns()
    complete=subprocess.run([sys.executable,"-B",str(HERE/"train.py")],cwd=ROOT)
    spent=resource.getrusage(resource.RUSAGE_CHILDREN)
    worker_cpu=round((spent.ru_utime+spent.ru_stime)*1e9)
    total=worker_cpu+time.process_time_ns()
    receipt=dict(cpu_ns=total,child_cpu_ns=worker_cpu,supervisor_ns_to_receipt=total-worker_cpu,
                 wall_ns=time.perf_counter_ns()-wall,returncode=complete.returncode)
    if complete.returncode:
        failed=OUT/"failed-fits.json"
        history=json.loads(failed.read_bytes()) if failed.exists() else []
        failed.write_text(json.dumps([*history,receipt],sort_keys=True)+"\n")
        raise SystemExit(complete.returncode)
    freeze=OUT/"freeze.json"
    receipt["freeze_sha256"]=hashlib.sha256(freeze.read_bytes()).hexdigest()
    receipt["model_sha256"]=json.loads(freeze.read_bytes())["model_sha256"]
    with cost.open("x") as stream:
        stream.write(json.dumps(receipt,sort_keys=True)+"\n")
    print("Charged training process CPU seconds",round(total/1e9,3),flush=True)


if __name__=="__main__":
    main()
