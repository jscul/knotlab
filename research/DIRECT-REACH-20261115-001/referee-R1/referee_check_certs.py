"""Referee R1, item (e): spot-check of refutation certificates against the committed hashes.

20 entries of artifacts/DIRECT-REACH-20261115-001A/*/certificate_hashes.json.gz (description -> [cnf sha256, lrat sha256, label,
verdict]), drawn at random (seed 20261116) over 10 archives of at most ~300 MB raw (2 per archive), located with index.tsv.gz,
extracted (only those members) into a scratch folder under referee-R1, re-hashed (sha256 of the raw .cnf and .lrat as stored in
the archive; the record's proof_sha256 too), then the scratch copies are deleted. Writes referee_certs.json."""
import gzip
import hashlib
import json
import random
import shutil
import subprocess
from pathlib import Path

ROOT = Path('/home/jscul/p-vs-np-contact-first')
ARCH = ROOT / 'experiments/DIRECT-REACH-20261115-001A/DIRECT-REACH-20261115-001A-E001_direct_reach/codex/certificate_archives'
HASHES = ROOT / 'artifacts/DIRECT-REACH-20261115-001A/DIRECT-REACH-20261115-001A-E001_direct_reach/certificate_hashes.json.gz'
HERE = ROOT / 'research/DIRECT-REACH-20261115-001/referee-R1'
SCR = HERE / 'scratch_certs'


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


rng = random.Random(20261116)
H = json.load(gzip.open(HASHES))
where = {}
with gzip.open(ARCH / 'index.tsv.gz', 'rt') as f:
    next(f)
    for line in f:
        d, a = line.split()
        where[d] = a
sizes = {r['archive']: r['raw_bytes'] for r in json.load(open(ARCH / 'archives.json'))}
# entries grouped by archive
by_arch = {}
for case, rows in H.items():
    for row in rows:
        a = where.get(row[0])
        if a is not None:
            by_arch.setdefault(a, []).append((case, row))
small = sorted(a for a in by_arch if sizes.get(a, 1 << 62) <= 300_000_000 and a != 'uncited.tar.zst')
pick_arch = rng.sample(small, 10)
picks = []
for a in pick_arch:
    for case, row in rng.sample(by_arch[a], 2):
        picks.append((a, case, row))
out = []
SCR.mkdir(exist_ok=True)
try:
    for a in pick_arch:
        mine = [p for p in picks if p[0] == a]
        members = [m for _, _, row in mine for m in (row[0] + '.cnf', row[0] + '.lrat', row[0] + '.json')]
        dest = SCR / a.replace('.tar.zst', '')
        dest.mkdir(exist_ok=True)
        zs = subprocess.Popen(['zstd', '-dc', '--long=27', str(ARCH / a)], stdout=subprocess.PIPE)
        tr = subprocess.run(['tar', '-x', '-C', str(dest)] + members, stdin=zs.stdout, capture_output=True)
        zs.wait()
        for _, case, row in mine:
            d = row[0]
            cnf, lrat, rec = dest / (d + '.cnf'), dest / (d + '.lrat'), dest / (d + '.json')
            r = dict(archive=a, case=case, digest=d, lrat_sha256_committed=row[1], label=row[2], verdict=row[3],
                     extracted=cnf.exists() and lrat.exists() and rec.exists(), tar_stderr=tr.stderr.decode()[:200])
            if r['extracted']:
                r['cnf_ok'] = sha(cnf) == d
                r['lrat_ok'] = sha(lrat) == row[1]
                j = json.load(open(rec))
                r['record_proof_sha256_ok'] = j.get('proof_sha256') == row[1]
            out.append(r)
            print(r, flush=True)
finally:
    shutil.rmtree(SCR, ignore_errors=True)
summary = dict(checked=len(out), archives=len(pick_arch), all_ok=all(r.get('cnf_ok') and r.get('lrat_ok') for r in out),
               scratch_deleted=not SCR.exists())
json.dump(dict(summary=summary, entries=out), open(HERE / 'referee_certs.json', 'w'), indent=1)
print(summary)
