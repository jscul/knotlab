"""Check retained encodings, hashes, paths and models without replaying proofs."""
import ast
import gzip
import hashlib
import json
from pathlib import Path
import resource
import fresh_certify as audit

resource.setrlimit(resource.RLIMIT_AS,(3*1024**3,3*1024**3))
HERE = Path(__file__).resolve().parent


def gzsha(path):
    digest = hashlib.sha256()
    count = 0
    with gzip.open(path,'rb') as stream:
        while block := stream.read(1024*1024):
            count += len(block)
            digest.update(block)
    return digest.hexdigest(),count


for path in HERE.glob('*.py'):
    ast.parse(path.read_text(),filename=str(path))
json_paths = list(HERE.glob('*.json'))
for path in json_paths:
    json.loads(path.read_text())
models = []
proofs = []
for path in sorted(HERE.glob('*.result.json')):
    value = json.loads(path.read_text())
    assert value['registered_pattern_hash_matches'] and value['registered_count_matches']
    if 'model_path' in value:
        model = gzip.decompress((HERE/value['model_path']).read_bytes()).decode().strip()
        assert audit.sha(model.encode())==value['assignment_sha256']
        _,triples,_,meta = audit.input_for(value['case'])
        checked = audit.verify_model(triples,model,1<<meta['n'])
        assert checked['valid']
        models.append({'case':value['case'],'checked_knots':len(triples)})
    if 'proof_path' in value:
        checked_sha,proof_bytes = gzsha(HERE/value['proof_path'])
        expected_sha = value.get('proof_uncompressed_sha256') or value['conversion']['drup_uncompressed_sha256']
        assert checked_sha==expected_sha
        cnf_sha,cnf_bytes = gzsha(HERE/value['cnf_path'])
        assert cnf_sha==value['certificate_cnf_sha256']
        entry = {'case':value['case'],'proof_bytes':proof_bytes,'cnf_bytes':cnf_bytes,
                 'mathematically_checked':value['certified']}
        if 'lrat_path' in value:
            lrat_sha,lrat_bytes = gzsha(HERE/value['lrat_path'])
            assert lrat_sha==value['conversion']['lrat_sha256']
            entry['lrat_bytes'] = lrat_bytes
        proofs.append(entry)
assert not list(HERE.glob('*.replay.cnf'))
result = {'status':'passed','json_files_parsed':len(json_paths),
          'python_files_parsed':len(list(HERE.glob('*.py'))),
          'retained_models_rechecked':models,'proof_and_cnf_archives_hash_checked':proofs,
          'scope':'Archive integrity and model rechecks; proof verdicts remain those of recorded independent RUP checks.'}
audit.dump(HERE/'artifact_validation.json',result)
print(json.dumps({'status':'passed','models':len(models),'proof_archives':len(proofs),
                  'json_files':len(json_paths)}),flush=True)
