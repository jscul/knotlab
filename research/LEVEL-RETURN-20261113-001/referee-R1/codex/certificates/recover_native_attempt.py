"""Preserve the attempt whose first checker timeout interrupted JSON writing."""
from pathlib import Path
import gzip
import hashlib
import json
import resource
import fresh_certify as audit
import native_refute as native

resource.setrlimit(resource.RLIMIT_AS,(3*1024**3,3*1024**3))
HERE = Path(__file__).resolve().parent
case = '91c75673c09d9046-L14'
prefix = case+'.cadical212.b3000000'
_,triples,clauses,meta = audit.input_for(case)
cnf = HERE/(prefix+'.cnf')
lrat = HERE/(prefix+'.lrat')
drup = HERE/(prefix+'.drup.gz')
drup_sha = hashlib.sha256()
additions = empty = 0
with gzip.open(drup,'rb') as stream:
    for line in stream:
        drup_sha.update(line)
        additions += 1
        empty += line.strip()==b'0'
lrat_sha = hashlib.sha256()
lrat_lines = deletions = 0
with lrat.open('rb') as stream:
    for line in stream:
        lrat_sha.update(line)
        lrat_lines += 1
        header = line.split(maxsplit=2)
        deletions += len(header)>1 and header[1]==b'd'
result = {**meta, 'solver':'cadical212', 'solver_version':'2.1.2',
          'solver_binary_sha256':audit.sha(native.BINARY.read_bytes()),
          'conflict_budget':3000000, 'solver_seconds_limit':300,
          'solver_exit_code':None,
          'disclosure':'Native stdout/exit status was held in memory and lost when the first 180s checker timeout raised; preserved proof bytes and conversion are audited here. No UNSAT verdict is inferred from solver output.',
          'complement_symmetry_unit':1, 'complement_invariance_checked':True,
          'certificate_cnf_sha256':audit.sha(cnf.read_bytes()),
          'conversion':{'lrat_lines':lrat_lines,'additions':additions,
                        'deletions_discarded':deletions,'empty_additions':empty,
                        'lrat_sha256':lrat_sha.hexdigest(),
                        'drup_uncompressed_sha256':drup_sha.hexdigest(),
                        'hints_consumed_by_checker':False},
          'proof_check':{'valid':False,'reason':'checker timeout','timeout_seconds':180},
          'verdict':'undecided','certified':False,'agrees_with_registered_decided':True,
          'seconds':None,
          'proof_path':drup.name, 'cnf_path':cnf.name+'.gz','lrat_path':lrat.name+'.gz'}
for path in (cnf,lrat):
    with path.open('rb') as source,gzip.open(str(path)+'.gz','wb',compresslevel=6) as destination:
        while chunk := source.read(1024*1024):
            destination.write(chunk)
    path.unlink()
audit.dump(HERE/(prefix+'.result.json'),result)
print(json.dumps({'additions':additions,'empty_additions':empty,
                  'lrat_lines':lrat_lines,'deletions':deletions,
                  'lrat_compressed_bytes':(HERE/(lrat.name+'.gz')).stat().st_size,
                  'status':'not certified: checker timeout'}),flush=True)
