"""One longer RUP replay of the retained hard-cell proof, no re-solving."""
import gzip
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import time
import fresh_certify as audit

resource.setrlimit(resource.RLIMIT_AS,(3*1024**3,3*1024**3))
HERE = Path(__file__).resolve().parent
prefix = '91c75673c09d9046-L14.cadical212.b3000000'
result_path = HERE/(prefix+'.result.json')
result = json.loads(result_path.read_text())
scratch = HERE/(prefix+'.replay.cnf')
with gzip.open(HERE/result['cnf_path'],'rb') as source:
    scratch.write_bytes(source.read())
assert hashlib.sha256(scratch.read_bytes()).hexdigest()==result['certificate_cnf_sha256']
command = [str(HERE/'check_rup_fast'),str(scratch),str(HERE/result['proof_path'])]
start = time.monotonic()
try:
    process = subprocess.run(command,capture_output=True,text=True,timeout=600)
    try:
        checked = json.loads(process.stdout)
    except json.JSONDecodeError:
        checked = {'valid':False,'reason':process.stderr.strip()}
    checked['exit_code'] = process.returncode
except subprocess.TimeoutExpired:
    checked = {'valid':False,'reason':'checker timeout','timeout_seconds':600}
checked['seconds'] = time.monotonic()-start
result.setdefault('earlier_proof_checks',[]).append(result['proof_check'])
result['proof_check'] = checked
result['certified'] = checked['valid']
result['verdict'] = 'dead' if checked['valid'] else 'undecided'
result['long_replay_seconds'] = checked['seconds']
result['certification_rule'] = 'A valid independently checked RUP refutation suffices; no native solver exit-status assertion is used.'
audit.dump(result_path,result)
scratch.unlink()
print(json.dumps({'case':result['case'],'certified':result['certified'],
                  'proof_check':checked}),flush=True)
