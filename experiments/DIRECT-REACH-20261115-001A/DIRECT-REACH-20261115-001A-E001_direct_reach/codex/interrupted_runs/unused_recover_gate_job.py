"""Verify one saved tie certificate, then rerun its four reach comparisons.

Tie verification reads only the original record, completed replay audit, and
cache. It uses no SAT solver, producer union-find, or new sampling. The ordinary
reach.query is used afterwards with its existing proof-retention adapter.
"""
from collections import defaultdict, deque
import copy
import gzip
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import time
import traceback

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from reuse import HERE, CENSUS, pattern, provenance, certificates as cert
from population import populations
from retention import ProofStore
from reach import query


DESCRIPTION = '57d2b6f04b592efbd9e5a32649dd70ab2361151f2dd20b37bf1bfd2bb0c1674c'
CASE_ID = 'reach-' + DESCRIPTION
EXPECTED_ORIGINAL_LINE_SHA256 = '45b0ea0cd95adfba49bfcf393e4d0338376d762e9e0195f6998aa72581cff0f5'
NVARS = 1023
CACHE = HERE / 'certificates'
ROW = ORIGINAL = AUDIT = ORIGIN = SOURCE_MANIFEST = WORK_ROOT = None


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _hash_file(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def _json_file(path):
    raw = path.read_bytes()
    return json.loads(raw), {'path': str(path.relative_to(HERE)),
                             'sha256': hashlib.sha256(raw).hexdigest()}


def _scan_records(path, selected=None):
    latest, digest, count = {}, hashlib.sha256(), 0
    with path.open('rb') as stream:
        for line in stream:
            _require(line.endswith(b'\n'), f'incomplete terminal JSONL line: {path.name}')
            digest.update(line)
            record = json.loads(line)
            count += 1
            _require(isinstance(record.get('case'), str), 'runner record has no case id')
            if selected is None or record['case'] == selected:
                latest[record['case']] = (record, hashlib.sha256(line).hexdigest())
    return latest, {'path': str(path.relative_to(HERE)), 'sha256': digest.hexdigest(),
                     'complete_lines': count}


def _terminal_state(directory):
    state, binding = _json_file(directory / 'state.json')
    _require(state.get('final') is True and state.get('complete') is True,
             f'{directory.name} is not a completed terminal run')
    return binding


def setup(params):
    global ROW, ORIGINAL, AUDIT, ORIGIN, SOURCE_MANIFEST, WORK_ROOT
    _require(not (set(params) - {'run_tag'}), 'unknown recovery parameter')
    tag = params.get('run_tag', 'saved-tie-recovery')
    _require(isinstance(tag, str) and re.fullmatch(r'[A-Za-z0-9_-]{1,64}', tag),
             'invalid recovery run tag')
    WORK_ROOT = HERE / 'recovery_work' / tag
    rows = [row for row in populations()['D'] if row['id'] == DESCRIPTION]
    _require(len(rows) == 1, 'description is not uniquely present in current D')
    ROW = rows[0]
    # This is population.py's compact normalized JSON serialization, not the
    # pre-addressed input_addr key normalizer, which has a different term type.
    key_raw = json.dumps(ROW['key'], separators=(',', ':'), ensure_ascii=True).encode('ascii')
    _require(hashlib.sha256(key_raw).hexdigest() == DESCRIPTION, 'current D key/id mismatch')
    _require(ROW['census']['union'] == 'alive'
             and [row['L_N'] for row in ROW['census']['levels']] == [2, 2, 2, 2],
             'selected census profile differs from the scoped constant-two case')

    bindings = {'original_state': _terminal_state(HERE / 'gates_run'),
                'audit_state': _terminal_state(HERE / 'certificate_audit')}
    old_rows, bindings['original_records'] = _scan_records(HERE / 'gates_run' / 'results.jsonl', CASE_ID)
    _require(CASE_ID in old_rows, 'original gate case is missing')
    ORIGINAL, original_line = old_rows[CASE_ID]
    _require(original_line == EXPECTED_ORIGINAL_LINE_SHA256, 'original complete JSON line changed')
    old = ORIGINAL.get('result', {})
    _require(ORIGINAL.get('status') == 'ok' and old.get('passed') is True
             and old.get('gate') == 'G-reach' and old.get('description') == DESCRIPTION,
             'original terminal record is not the expected successful G-reach case')
    if 'key' in old:
        _require(old['key'] == ROW['key'], 'original explicit key differs from current D')

    summary, bindings['audit_summary'] = _json_file(HERE / 'certificate_audit.json')
    audit_input, bindings['audit_input'] = _json_file(HERE / 'affected_certificates.json')
    hashes = audit_input.get('hashes') if isinstance(audit_input, dict) else audit_input
    _require(isinstance(hashes, list) and all(isinstance(h, str) and re.fullmatch('[0-9a-f]{64}', h) for h in hashes),
             'audit input hash roster is malformed')
    expected_hashes = set(hashes)
    _require(summary.get('passed') is True and summary.get('failed') == []
             and summary.get('runner_errors') == []
             and summary.get('records') == 'certificate_audit/results.jsonl',
             'completed certificate audit did not pass')
    audit_rows, bindings['audit_records'] = _scan_records(HERE / 'certificate_audit' / 'results.jsonl')
    checker_hash = _hash_file(cert.CHECKER)
    AUDIT = {}
    for audit_case, (record, line_hash) in sorted(audit_rows.items()):
        result = record.get('result', {})
        _require(record.get('status') == 'ok' and result.get('passed') is True
                 and result.get('failed_count') == 0, 'audit runner contains a failed terminal batch')
        _require(result.get('input', {}).get('sha256') == bindings['audit_input']['sha256'],
                 'audit replay used a different input roster')
        proofs = result.get('proofs', [])
        _require(result.get('certificate_count') == len(proofs)
                 and result.get('checker_passed_count') == len(proofs), 'audit batch counts disagree')
        for proof in proofs:
            digest = proof.get('cnf_sha256')
            _require(digest in expected_hashes and digest not in AUDIT, 'audit proof roster overlaps or differs')
            _require(proof.get('passed') is True and proof.get('checker_passed') is True
                     and proof.get('errors') == [], 'audit proof did not pass')
            checked = proof.get('checker', {})
            _require(checked.get('returncode') == 0 and checked.get('stdout', '').startswith('VERIFIED')
                     and checked.get('sha256') == checker_hash, 'audit checker binding is not valid')
            _require(proof.get('cnf_raw', {}).get('sha256') == digest
                     and proof.get('proof_raw', {}).get('sha256') == proof.get('expected_proof_sha256'),
                     'audit raw-hash binding is incomplete')
            AUDIT[digest] = {'proof': proof, 'record_line_sha256': line_hash, 'case': audit_case}
    _require(set(AUDIT) == expected_hashes and summary.get('checked') == len(AUDIT),
             'successful audit index does not cover its complete input roster')
    incidents = []
    for name in ('restart_collision.json', 'overlapping_gate_cases.json'):
        _require((HERE / name).is_file(), f'preserved engineering incident record is missing: {name}')
        incidents.append({'path': name, 'sha256': _hash_file(HERE / name)})
    ORIGIN = {'bindings': bindings, 'original_record_line_sha256': original_line,
              'original_case': CASE_ID, 'original_job_sha256': ORIGINAL.get('job_sha'),
              'original_finished_at': ORIGINAL.get('finished_at'),
              'original_elapsed_seconds': ORIGINAL.get('seconds'),
              'original_tie_elapsed_seconds': old['ties'].get('seconds'),
              'original_sampling_elapsed_seconds': old['ties'].get('sampling', {}).get('seconds'),
              'original_source_manifest': old.get('source_manifest'),
              'key_binding': 'current population compact-JSON SHA-256 and independently recomputed forbidden CNFs',
              'audit_passed_proofs': len(AUDIT),
              'earlier_resource_incident': {'status': 'preserved', 'records': incidents}}
    manifest = provenance()
    manifest['implementation']['recover_gate_job.py'] = _hash_file(HERE / 'recover_gate_job.py')
    manifest['implementation']['certificate_audit_job.py'] = _hash_file(HERE / 'certificate_audit_job.py')
    manifest['recovery_inputs'] = ORIGIN
    manifest_raw = (json.dumps(manifest, sort_keys=True, indent=2) + '\n').encode()
    SOURCE_MANIFEST = {'sha256': hashlib.sha256(manifest_raw).hexdigest(), 'inline': manifest}


def cases():
    _require(ROW is not None, 'setup(params) must precede cases()')
    yield CASE_ID, {'id': DESCRIPTION, 'original_record_line_sha256': ORIGIN['original_record_line_sha256']}


def _gzip_info(path):
    digest, size = hashlib.sha256(), 0
    with gzip.open(path, 'rb') as stream:
        while True:
            block = stream.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
            size += len(block)
    return {'sha256': digest.hexdigest(), 'bytes': size}


def _verify_cached(digest, original, verified, refutations):
    if digest in verified:
        return
    _require(digest in AUDIT, f'tie refutation lacks successful replay audit: {digest}')
    entry = AUDIT[digest]
    replay = entry['proof']
    metadata_path = CACHE / (digest + '.json')
    raw_metadata = metadata_path.read_bytes()
    metadata_hash = hashlib.sha256(raw_metadata).hexdigest()
    _require(metadata_hash == replay.get('metadata_sha256'), f'audited metadata changed: {digest}')
    metadata = json.loads(raw_metadata)
    _require(metadata.get('checked') is True and metadata.get('cnf_sha256') == digest,
             f'current refutation metadata is invalid: {digest}')
    cnf = _gzip_info(CACHE / (digest + '.cnf.gz'))
    proof = _gzip_info(CACHE / (digest + '.lrat.gz'))
    _require(cnf == replay['cnf_raw'] and proof == replay['proof_raw']
             and cnf['sha256'] == digest and proof['sha256'] == metadata.get('proof_sha256')
             and cnf['bytes'] == metadata.get('cnf_bytes') and proof['bytes'] == metadata.get('proof_bytes'),
             f'current gzip payload differs from successful audit/metadata: {digest}')
    _require(original.get('checked') is True and original.get('cnf_sha256') == digest
             and original.get('proof_sha256') == proof['sha256'],
             f'original pair proof binding differs from current audited artifact: {digest}')
    verified[digest] = {'cnf_sha256': digest, 'proof_sha256': proof['sha256'],
                        'cnf_bytes': cnf['bytes'], 'proof_bytes': proof['bytes'],
                        'metadata_sha256': metadata_hash, 'audit_case': entry['case'],
                        'audit_record_line_sha256': entry['record_line_sha256'],
                        'cnf_path': 'certificates/' + digest + '.cnf.gz',
                        'proof_path': 'certificates/' + digest + '.lrat.gz'}
    refutations[digest] = metadata


def _verify_ties(K, verified, refutations):
    started = time.monotonic()
    ties = ORIGINAL['result']['ties']
    _require(ties.get('verdict') == 'complete' and ties.get('nvars') == NVARS, 'original ties are incomplete')
    sampling = ties.get('sampling', {})
    packed = ties.get('state_pool', [])
    _require(sampling.get('random_phase_states') == 64 and len(packed) >= 64,
             'the recorded 64 initial states are not available')
    rows = [tuple(int(v) for v in row) for row in K]
    columns, state_bits = [0] * NVARS, []
    for index, value in enumerate(packed):
        _require(isinstance(value, str), 'packed state is not hex text')
        raw = bytes.fromhex(value)
        _require(len(raw) == 128 and not (raw[-1] & 128), 'packed N9 state has wrong length/padding')
        bits = int.from_bytes(raw, 'little')
        _require(all(not (((bits >> a) & 1) == ((bits >> b) & 1) == ((bits >> c) & 1))
                     for a, b, c in rows), f'stored state {index} violates the actual N9 pattern')
        state_bits.append(bits)
        for v in range(NVARS):
            columns[v] |= ((bits >> v) & 1) << index

    classes, class_signs, singletons = ties['classes'], ties['class_signs'], ties['singletons']
    _require(len(classes) == len(class_signs), 'stored class/sign counts differ')
    covered = list(singletons)
    _require(singletons == sorted(set(singletons)), 'stored singletons are not canonical')
    for members, signs in zip(classes, class_signs):
        _require(len(members) >= 2 and members == sorted(set(members))
                 and len(signs) == len(members) and signs[0] == 0
                 and all(type(sign) is int and sign in (0, 1) for sign in signs),
                 'stored class members/signs are malformed')
        covered.extend(members)
    _require(all(type(v) is int for v in covered) and sorted(covered) == list(range(NVARS)),
             'stored classes/singletons do not partition exactly 0..1022')

    prefix = hashlib.sha256()
    prefix.update(f'p cnf {NVARS} {2 * len(rows) + 2}\n'.encode())
    for row in rows:
        for sign in (1, -1):
            prefix.update((' '.join(str(sign * (v + 1)) for v in row) + ' 0\n').encode())
    adjacent = [[] for _ in range(NVARS)]
    confirmed = ties['confirmed_candidates']
    old_refs = ORIGINAL['result']['refutations']
    for candidate in confirmed:
        u, v, parity = candidate['u'], candidate['v'], candidate['parity']
        _require(type(u) is int and type(v) is int and 0 <= u < NVARS and 0 <= v < NVARS
                 and u != v and type(parity) is int and parity in (0, 1), 'malformed certified pair')
        _require(len(candidate['refutations']) == 2, 'certified pair does not have two refutations')
        for x in (0, 1):
            y = x ^ parity ^ 1
            units = [u + 1 if x else -u - 1, v + 1 if y else -v - 1]
            digest = prefix.copy()
            for literal in units:
                digest.update(f'{literal} 0\n'.encode())
            expected = digest.hexdigest()
            _require(candidate['refutations'][x] == expected and expected in old_refs,
                     'certified pair CNF digest does not bind the actual K and forbidden units')
            _verify_cached(expected, old_refs[expected], verified, refutations)
        adjacent[u].append((v, parity))
        adjacent[v].append((u, parity))

    # An independent adjacency/BFS construction, without the producer's UF.
    components, signs = [], [None] * NVARS
    for root in range(NVARS):
        if signs[root] is not None:
            continue
        signs[root], members, queue = 0, [], deque([root])
        while queue:
            u = queue.popleft()
            members.append(u)
            for v, parity in adjacent[u]:
                expected = signs[u] ^ parity
                if signs[v] is None:
                    signs[v] = expected
                    queue.append(v)
                else:
                    _require(signs[v] == expected, 'certified signed adjacency is inconsistent')
        components.append(sorted(members))
    actual_classes = [members for members in components if len(members) > 1]
    _require(actual_classes == classes
             and [[signs[v] for v in members] for members in actual_classes] == class_signs
             and [members[0] for members in components if len(members) == 1] == singletons,
             'independent signed components differ from stored classes/signs/singletons')
    _require(len(confirmed) == NVARS - len(components), 'confirmed pairs are not a spanning forest')
    _require(ties.get('forced_pair_count') == sum(len(members) * (len(members) - 1) // 2 for members in actual_classes),
             'stored forced-pair count differs from the independently verified classes')

    mask, signature_groups = (1 << len(packed)) - 1, defaultdict(list)
    for v, column in enumerate(columns):
        signature_groups[min(column, column ^ mask)].append(v)
    _require(sorted(signature_groups.values(), key=lambda group: group[0]) == components,
             'checked state signatures do not distinguish exactly the certified components')
    for members in components:
        for v in members:
            _require(columns[v] == (columns[members[0]] ^ (mask if signs[v] else 0)),
                     'checked state signature signs differ from certified pair signs')
    rejected = ties.get('rejected_candidates', [])
    for candidate in rejected:
        u, v, parity = candidate['u'], candidate['v'], candidate['proposed_parity']
        indices = candidate['counterstate_indices']
        _require(type(u) is int and type(v) is int and 0 <= u < NVARS and 0 <= v < NVARS
                 and type(parity) is int and parity in (0, 1) and len(indices) == 2,
                 'stored rejected candidate is malformed')
        for x, index in enumerate(indices):
            _require(type(index) is int and 64 <= index < len(state_bits), 'counterstate index is invalid')
            _require(((state_bits[index] >> u) & 1) == x
                     and ((state_bits[index] >> v) & 1) == (x ^ parity ^ 1),
                     'stored counterstate does not refute its proposed tie')
    _require(ties.get('sat_calls') == 64 + 2 * (len(confirmed) + len(rejected)),
             'stored sampling/candidate SAT-call counts disagree')
    summaries = []
    for top in (2, 3):
        for s in range(1, 7):
            indices = [i for i, members in enumerate(actual_classes)
                       if top in {(v + 1).bit_length() - 1 for v in members}
                       and top + s in {(v + 1).bit_length() - 1 for v in members}]
            summaries.append({'k0': top, 's': s, 'spanning': bool(indices), 'class_indices': indices})
    _require(ties.get('summaries') == summaries, 'stored spanning summaries differ from verified classes')
    evidence = {'passed': True, 'verification_seconds': time.monotonic() - started,
                'states_checked': len(packed), 'initial_states_recorded': 64,
                'certified_pairs': len(confirmed), 'refutations_checked': len(verified),
                'components': len(components), 'nontrivial_classes': len(actual_classes),
                'singleton_count': len(singletons), 'complete_signature_partition': True,
                'state_pool_sha256': hashlib.sha256(json.dumps(packed, separators=(',', ':')).encode()).hexdigest(),
                'method': 'all states checked; exact K+units hashes; audited raw proofs; signed adjacency/BFS; complete state-signature partition',
                'proof_bindings': verified, 'origin': ORIGIN}
    reused = copy.deepcopy(ties)
    reused.update(reuse_marker='reused, not resampled', original_elapsed_seconds=ties['seconds'],
                  elapsed_seconds_source='original gates_run computation', verification_seconds=evidence['verification_seconds'])
    return reused, summaries, evidence


def run(case_id, payload):
    _require(ROW is not None and case_id == CASE_ID and payload.get('id') == DESCRIPTION
             and payload.get('original_record_line_sha256') == EXPECTED_ORIGINAL_LINE_SHA256,
             'recovery case does not match the sole frozen original record')
    work = WORK_ROOT / case_id
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    started = time.monotonic()
    verified, tie_refs, store = {}, {}, None
    value = {'gate': 'G-reach', 'description': DESCRIPTION, 'passed': False,
             'comparisons': [], 'ties': {'verdict': 'not_verified'},
             'threshold_reach': None, 'source_manifest': SOURCE_MANIFEST,
             'origin': ORIGIN, 'original_elapsed_seconds': ORIGINAL.get('seconds')}
    try:
        for binding in ORIGIN['bindings'].values():
            _require(_hash_file(HERE / binding['path']) == binding['sha256'],
                     f'frozen recovery input changed: {binding["path"]}')
        K = pattern.pattern(ROW['key'], 9)
        reused, summaries, evidence = _verify_ties(K, verified, tie_refs)
        value.update(ties=reused, cached_verification=evidence)
        store = ProofStore(work, NVARS)
        reach = query(ROW['key'], work, store, 3, [1, 2, 3, 4], k_max=3, budget=300)
        value['threshold_reach'] = reach
        _require([row['s'] for row in reach['levels']] == [1, 2, 3, 4], 'fresh threshold query roster differs')
        for census, result in zip(ROW['census']['levels'], reach['levels']):
            s = census['s']
            _require(s == result['s'], 'fresh threshold and census query indices differ')
            spanning = next(row['spanning'] for row in summaries if row['k0'] == 3 and row['s'] == s)
            threshold = result['thresholds']['3']
            okay = (spanning == (census['L_N'] == 2) and threshold != 'undecided'
                    and (threshold == 'yes') == (census['L_N'] <= 3))
            value['comparisons'].append({'s': s, 'census_L_N': census['L_N'],
                                         'spanning_class': spanning, 'threshold': threshold,
                                         'fresh_L_N': result['L_N'], 'passed': okay})
        for digest, metadata in store.records.items():
            if digest in tie_refs:
                _require(tie_refs[digest]['proof_sha256'] == metadata['proof_sha256'],
                         'fresh query changed a verified tie proof binding')
        value['passed'] = all(row['passed'] for row in value['comparisons'])
    except Exception as exc:
        value['error'] = f'{type(exc).__name__}: {exc}'
        value['traceback'] = traceback.format_exc()
        if 'cached_verification' not in value:
            value['cached_verification'] = {'passed': False, 'refutations_checked': len(verified),
                                             'proof_bindings': verified, 'origin': ORIGIN}
    finally:
        value.update(refutations={**tie_refs, **(store.records if store is not None else {})},
                     incomplete_certifications=store.incomplete if store is not None else [],
                     external_certificate_seconds=store.external_seconds if store is not None else 0.0,
                     reused_external_certificate_seconds=store.reused_external_seconds if store is not None else 0.0,
                     seconds=time.monotonic() - started,
                     scope='finite saved-certificate verification and four fresh threshold queries; earlier resource incident preserved')
        if work.exists():
            shutil.rmtree(work)
    return value
