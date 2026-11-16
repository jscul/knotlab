"""Read-only cache-binding recovery audit, in batches of 100 certificates.

The shared runner retains results. Only this job's audit_work/<case>/ scratch
is created or removed. Original cache files are opened for reading only.
No CNF or proof is generated: gzip payloads are replayed by the existing checker.
"""
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from reuse import HERE, certificates as cert
import retention


INPUT = HERE / 'affected_certificates.json'
CACHE = HERE / 'certificates'
BATCH_SIZE = 100
HASHES = None
INPUT_INFO = None
CHECKER_INFO = None
IMPLEMENTATION = None


def _is_hash(value):
    return (isinstance(value, str) and len(value) == 64
            and all(character in '0123456789abcdef' for character in value))


def _file_hash(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def setup(params):
    """Load a fixed hash roster before the runner forks its workers."""
    global HASHES, INPUT_INFO, CHECKER_INFO, IMPLEMENTATION
    if params:
        raise ValueError('certificate audit has no configurable parameters')
    raw = INPUT.read_bytes()
    document = json.loads(raw)
    hashes = document.get('hashes') if isinstance(document, dict) else document
    if not isinstance(hashes, list) or not hashes or not all(_is_hash(value) for value in hashes):
        raise ValueError('affected_certificates.json must contain a nonempty list of lowercase CNF SHA-256 hashes')
    HASHES = sorted(set(hashes))
    INPUT_INFO = {'path': str(INPUT.relative_to(HERE)),
                  'sha256': hashlib.sha256(raw).hexdigest(),
                  'listed_hashes': len(hashes), 'unique_hashes': len(HASHES)}
    CHECKER_INFO = {'path': str(cert.CHECKER), 'sha256': _file_hash(cert.CHECKER)}
    IMPLEMENTATION = {name: _file_hash(HERE / name)
                      for name in ('certificate_audit_job.py', 'retention.py', 'reuse.py')}


def cases():
    if HASHES is None:
        raise RuntimeError('setup(params) must precede cases()')
    for start in range(0, len(HASHES), BATCH_SIZE):
        case_id = INPUT_INFO['sha256'] + f'-{start // BATCH_SIZE:05d}'
        yield case_id, {'id': case_id, 'input_sha256': INPUT_INFO['sha256'],
                        'hashes': HASHES[start:start + BATCH_SIZE]}


def _inflate(source, target):
    """Stream the unchanged gzip payload to owned scratch and hash raw bytes."""
    digest, size = hashlib.sha256(), 0
    with gzip.open(source, 'rb') as compressed, target.open('wb') as output:
        while True:
            block = compressed.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
            size += len(block)
            output.write(block)
    return {'sha256': digest.hexdigest(), 'bytes': size}


def _audit_one(digest, batch_work):
    started = time.monotonic()
    cnf_gzip = CACHE / (digest + '.cnf.gz')
    proof_gzip = CACHE / (digest + '.lrat.gz')
    metadata_path = CACHE / (digest + '.json')
    result = {'cnf_sha256': digest,
              'cnf_gzip_path': str(cnf_gzip.relative_to(HERE)),
              'proof_gzip_path': str(proof_gzip.relative_to(HERE)),
              'metadata_path': str(metadata_path.relative_to(HERE)),
              'checker': {'path': CHECKER_INFO['path'],
                          'sha256': CHECKER_INFO['sha256'], 'attempted': False},
              'passed': False, 'checker_passed': False, 'errors': []}
    work = batch_work / digest
    work.mkdir()
    try:
        metadata = None
        try:
            raw_metadata = metadata_path.read_bytes()
            result['metadata_sha256'] = hashlib.sha256(raw_metadata).hexdigest()
            metadata = json.loads(raw_metadata)
            if not isinstance(metadata, dict):
                raise ValueError('certificate metadata is not an object')
            expected_proof = metadata.get('proof_sha256')
            result['expected_proof_sha256'] = expected_proof
            if metadata.get('cnf_sha256') != digest:
                result['errors'].append('metadata CNF SHA-256 disagrees with cache filename')
            if metadata.get('checked') is not True:
                result['errors'].append('metadata does not mark the certificate checked')
            if not _is_hash(expected_proof):
                result['errors'].append('metadata proof SHA-256 is missing or malformed')
        except Exception as exc:
            result['errors'].append(f'metadata: {type(exc).__name__}: {exc}')

        cnf, proof = work / 'input.cnf', work / 'input.lrat'
        complete = True
        for label, source, target in (('cnf', cnf_gzip, cnf), ('proof', proof_gzip, proof)):
            try:
                result[label + '_raw'] = _inflate(source, target)
            except Exception as exc:
                complete = False
                result['errors'].append(f'{label} decompression: {type(exc).__name__}: {exc}')
        if 'cnf_raw' in result and result['cnf_raw']['sha256'] != digest:
            result['errors'].append('raw CNF SHA-256 disagrees with cache filename')
        if isinstance(metadata, dict):
            if 'proof_raw' in result and result['proof_raw']['sha256'] != metadata.get('proof_sha256'):
                result['errors'].append('raw LRAT SHA-256 disagrees with metadata')
            for label, key in (('cnf', 'cnf_bytes'), ('proof', 'proof_bytes')):
                if label + '_raw' in result and key in metadata and result[label + '_raw']['bytes'] != metadata[key]:
                    result['errors'].append(f'raw {label} byte count disagrees with metadata')

        # A hash disagreement is retained as a failed audit even if this actual
        # pair passes replay. The checker helps distinguish those two failures.
        if complete:
            wait_started = time.monotonic()
            try:
                with retention.external_slot():
                    result['external_slot_wait_seconds'] = time.monotonic() - wait_started
                    check_started = time.monotonic()
                    command = [str(cert.CHECKER), str(cnf), str(proof)]
                    result['checker']['attempted'] = True
                    checked = subprocess.run(command, capture_output=True, text=True)
                    result['checker'] = {'path': CHECKER_INFO['path'],
                                         'sha256': CHECKER_INFO['sha256'],
                                         'attempted': True,
                                         'returncode': checked.returncode,
                                         'stdout': checked.stdout, 'stderr': checked.stderr,
                                         'seconds': time.monotonic() - check_started}
                result['checker_passed'] = checked.returncode == 0 and checked.stdout.startswith('VERIFIED')
                if not result['checker_passed']:
                    result['errors'].append('LRAT checker rejected the decompressed CNF/proof pair')
            except Exception as exc:
                result['errors'].append(f'checker: {type(exc).__name__}: {exc}')
        else:
            result['checker_skipped'] = 'gzip input missing or not fully decompressed'
        result['passed'] = not result['errors'] and result['checker_passed']
        return result
    finally:
        result['seconds'] = time.monotonic() - started
        shutil.rmtree(work)


def run(case_id, payload):
    if HASHES is None:
        raise RuntimeError('setup(params) must precede run()')
    expected_ids = {INPUT_INFO['sha256'] + f'-{index:05d}'
                    for index in range((len(HASHES) + BATCH_SIZE - 1) // BATCH_SIZE)}
    if (case_id not in expected_ids or payload.get('id') != case_id
            or payload.get('input_sha256') != INPUT_INFO['sha256']):
        raise ValueError('case id must belong to the loaded audit input')
    index = int(case_id.rsplit('-', 1)[1])
    expected_hashes = HASHES[index * BATCH_SIZE:(index + 1) * BATCH_SIZE]
    if payload.get('hashes') != expected_hashes:
        raise ValueError('case payload differs from the frozen sorted hash batch')
    work = HERE / 'audit_work' / case_id
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    started = time.monotonic()
    try:
        proofs = [_audit_one(digest, work) for digest in expected_hashes]
        return {'case': case_id, 'passed': all(item['passed'] for item in proofs),
                'certificate_count': len(proofs),
                'checker_passed_count': sum(item['checker_passed'] for item in proofs),
                'failed_count': sum(not item['passed'] for item in proofs),
                'proofs': proofs, 'input': INPUT_INFO, 'checker': CHECKER_INFO,
                'implementation_sha256': IMPLEMENTATION,
                'seconds': time.monotonic() - started,
                'scope': 'cache hashes and independent LRAT replay only; cache files unchanged'}
    finally:
        shutil.rmtree(work)
