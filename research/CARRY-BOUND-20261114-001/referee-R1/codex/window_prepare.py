"""Select permitted JSON evidence without opening producer Python."""
import gzip
import hashlib
import json
import resource
from pathlib import Path

resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))
ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
BASE = ROOT / 'artifacts/CARRY-BOUND-20261114-001A/CARRY-BOUND-20261114-001A-E001_window'
DIGEST = BASE / 'window_digest.jsonl.gz'
FULL = ROOT / 'experiments/CARRY-BOUND-20261114-001A/CARRY-BOUND-20261114-001A-E001_window/codex/window_full/results.jsonl'
CENSUS = ROOT / 'artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/families.jsonl.gz'
PREFIXES = [
    'e35d907e41c9', '277e4af88ffd',
    'ce444059ece1', '432127c418b0',
    '0d0a849308d9', '4a89d24d95e9',
    '0274a8f97ce5', '17f842211d02',
    '7aac0c3bf98b', '3b96dcc4045a',
    '3e479a23fc49', '4c743f6f3c29', '6840b65fda90',
    '43d056083445', 'd2942bac0424',
    '057b385094fd',
]

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1024**2), b''):
            h.update(b)
    return h.hexdigest()

def thin_certificate(cert):
    window = cert['window']
    return {k: cert[k] for k in ('key', 'verdict', 'caps', 'scope', 'wrapper', 'depth', 'R_i', 'stratum', 'preparation')} | {
        'window': {k: window[k] for k in ('complete', 'verdict', 'preperiod', 'period', 'repeat_at',
                                           'maximum', 'levels', 'starts', 'residues')} | {
            'state_bonds': [{k: state[k] for k in ('J', 'partition', 'g')}
                            for state in window['state_bonds']]}}

def main():
    compact = [json.loads(line) for line in gzip.open(DIGEST, 'rt')]
    chosen = [r for r in compact if r['key_sha256'][:12] in PREFIXES]
    assert len(chosen) == len(PREFIXES) == 16
    assert all(r['in_scope'] and r['window_complete'] and r['window_verdict'] == 'bounded' for r in chosen)
    assert sum(r['verdict'] == 'bounded' for r in chosen) == 15
    keys = {r['key'] for r in chosen}
    certs = {}
    full_h = hashlib.sha256()
    with FULL.open('rb') as f:
        for line in f:
            full_h.update(line)
            row = json.loads(line)
            if row['case'] in keys:
                certs[row['case']] = thin_certificate(row['result'])
    census = {}
    with gzip.open(CENSUS, 'rt') as f:
        for line in f:
            row = json.loads(line)
            if row['key'] in keys:
                census[row['key']] = row
    assert keys == set(certs) == set(census)
    records = []
    for r in sorted(chosen, key=lambda r: PREFIXES.index(r['key_sha256'][:12])):
        cert = certs[r['key']]
        records.append({'digest': r, 'census': census[r['key']], 'certificate': cert})
    out = {'records': records, 'sources': {
        str(DIGEST.relative_to(ROOT)): digest(DIGEST),
        str(FULL.relative_to(ROOT)): full_h.hexdigest(),
        str(CENSUS.relative_to(ROOT)): digest(CENSUS),
    }, 'forbidden_python_opened_or_imported': False}
    target = HERE / 'window_inputs.json'
    target.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({'selected': len(records), 'output_bytes': target.stat().st_size,
                      'cells': [(r['digest']['key_sha256'][:12], r['digest']['stratum'],
                                 r['digest']['preperiod'], r['digest']['period']) for r in records]}))

if __name__ == '__main__':
    main()
