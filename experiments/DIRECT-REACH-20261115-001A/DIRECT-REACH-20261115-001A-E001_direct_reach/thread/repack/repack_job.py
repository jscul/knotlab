"""Repack codex/certificates/ into one zstd archive per description (DIRECT-REACH-20261115-001, the thread's own, 2026-11-16, at
John's choice "Repack now"). Shared-runner job: one case per archive. Nothing is removed here.

Each certificate (digest = SHA-256 of the raw CNF) has three files: <digest>.cnf.gz, <digest>.lrat.gz and <digest>.json (its record,
with proof_sha256 of the raw LRAT). It goes to the archive of the first description, in sorted order of the committed
artifacts/.../certificate_hashes.json.gz, that cites it; certificates no description cites (gates, controls) go to 'uncited'. An
archive is a tar of <digest>.cnf, <digest>.lrat (both decompressed) and <digest>.json, compressed with zstd -12 --long=27. After writing,
the archive is read back and every member is checked: the CNF's SHA-256 equals its digest, the LRAT's equals proof_sha256, the record's
bytes equal the original file's; the archive is renamed into place only if every assigned certificate is present and checked.
Extract one description: zstd -dc --long=27 <archive> | tar -x -C <dir>."""
import gzip
import hashlib
import io
import json
import os
import subprocess
import tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parents[1]
CERT = EXP / 'codex/certificates'
OUT = EXP / 'codex/certificate_archives'
ROOT = EXP.parents[2]
HASHES = ROOT / 'artifacts/DIRECT-REACH-20261115-001A/DIRECT-REACH-20261115-001A-E001_direct_reach/certificate_hashes.json.gz'
ASSIGN = {}


def archive_name(key):
    return key.replace(':', '_')


def setup(params):
    global ASSIGN
    cited = json.load(gzip.open(HASHES, 'rt'))
    owner = {}
    for key in sorted(cited):
        for cnf, *_ in cited[key]:
            owner.setdefault(cnf, archive_name(key))
    digests = sorted(p.name[:-5] for p in CERT.glob('*.json'))
    ASSIGN = {}
    for d in digests:
        ASSIGN.setdefault(owner.get(d, 'uncited'), []).append(d)
    OUT.mkdir(exist_ok=True)
    (OUT / 'assignment.json').write_text(json.dumps({k: len(v) for k, v in sorted(ASSIGN.items())}, indent=1))


def cases():
    for name in sorted(ASSIGN):
        yield name, {'digests': ASSIGN[name]}


def sha_stream(f):
    h = hashlib.sha256()
    while True:
        b = f.read(1 << 20)
        if not b:
            return h.hexdigest()
        h.update(b)


def run(name, payload):
    digests = payload['digests']
    final = OUT / (name + '.tar.zst')
    tmp = OUT / (name + '.tar.zst.tmp')
    if final.exists():
        tmp = None
    else:
        z = subprocess.Popen(['zstd', '-12', '--long=27', '-T2', '-q', '-f', '-o', str(tmp)], stdin=subprocess.PIPE)
        with tarfile.open(fileobj=z.stdin, mode='w|') as tar:
            for d in digests:
                rec_bytes = (CERT / (d + '.json')).read_bytes()
                rec = json.loads(rec_bytes)
                for suffix, member, size in (('.cnf.gz', d + '.cnf', rec['cnf_bytes']), ('.lrat.gz', d + '.lrat', rec['proof_bytes'])):
                    info = tarfile.TarInfo(member)
                    info.size = size
                    with gzip.open(CERT / (d + suffix), 'rb') as src:
                        tar.addfile(info, src)
                info = tarfile.TarInfo(d + '.json')
                info.size = len(rec_bytes)
                tar.addfile(info, io.BytesIO(rec_bytes))
        z.stdin.close()
        if z.wait():
            raise RuntimeError('zstd failed')
    # read back and check every member
    path = tmp or final
    seen = {}
    expect = {}
    for d in digests:
        rec_bytes = (CERT / (d + '.json')).read_bytes()
        rec = json.loads(rec_bytes)
        expect[d + '.cnf'] = d
        expect[d + '.lrat'] = rec['proof_sha256']
        expect[d + '.json'] = hashlib.sha256(rec_bytes).hexdigest()
    dz = subprocess.Popen(['zstd', '-dc', '--long=27', '-q', str(path)], stdout=subprocess.PIPE)
    raw = 0
    with tarfile.open(fileobj=dz.stdout, mode='r|') as tar:
        for m in tar:
            f = tar.extractfile(m)
            seen[m.name] = sha_stream(f)
            raw += m.size
    if dz.wait():
        raise RuntimeError('zstd -d failed')
    bad = [k for k, v in expect.items() if seen.get(k) != v]
    extra = sorted(set(seen) - set(expect))
    if bad or extra:
        raise RuntimeError('verification failed: %d bad, %d extra; first %s' % (len(bad), len(extra), (bad + extra)[:3]))
    if tmp is not None:
        os.replace(tmp, final)
    gz_bytes = sum((CERT / (d + s)).stat().st_size for d in digests for s in ('.cnf.gz', '.lrat.gz', '.json'))
    with open(final, 'rb') as f:
        archive_sha = sha_stream(f)
    index = dict(archive=final.name, archive_sha256=archive_sha, archive_bytes=final.stat().st_size, original_bytes=gz_bytes,
                 raw_bytes=raw, certificates=len(digests), members_checked=len(seen), digests=digests)
    (OUT / (name + '.index.json')).write_text(json.dumps(index))
    index.pop('digests')
    return index
