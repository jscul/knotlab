"""Pack CARRIER-20261117-001's LRAT certificates (the thread's own, 2026-11-17). The threshold runs wrote them, gzip-compressed, to
DIRECT-REACH's codex/certificates_carrier/ (threshold.py, threshold_deep.py). This packs them as DIRECT-REACH's repack did
(experiments/DIRECT-REACH-20261115-001A/.../thread/repack/repack_job.py, refereed format): one zstd archive per pattern, holding the
certificates its threshold files cite (the first file in sorted order that cites one owns it), and 'uncited' for the rest (the smoke
and searches cut off by their budget). Members are <digest>.cnf and <digest>.lrat (decompressed) and <digest>.json (the record, with
proof_sha256 of the raw LRAT). Every member is read back and checked against its hash before the archive is put in place, and the
originals of a checked archive are then removed (they are this task's own files).
Archives: artifacts/CARRIER-20261117-001/certificates/<name>.tar.zst (not tracked) with <name>.index.json and index.tsv.gz (tracked).
Extract: zstd -dc --long=27 <name>.tar.zst | tar -x -C <dir>."""
import gzip
import hashlib
import io
import json
import os
import subprocess
import sys
import tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CERT = ROOT / 'experiments/DIRECT-REACH-20261115-001A/DIRECT-REACH-20261115-001A-E001_direct_reach/codex/certificates_carrier'
OUT = ROOT / 'artifacts/CARRIER-20261117-001/certificates'


def sha_stream(f):
    h = hashlib.sha256()
    while True:
        b = f.read(1 << 20)
        if not b:
            return h.hexdigest()
        h.update(b)


def pack(name, digests):
    final, tmp = OUT / (name + '.tar.zst'), OUT / (name + '.tar.zst.tmp')
    z = subprocess.Popen(['zstd', '-12', '--long=27', '-T4', '-q', '-f', '-o', str(tmp)], stdin=subprocess.PIPE)
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
    expect = {}
    for d in digests:
        rec_bytes = (CERT / (d + '.json')).read_bytes()
        expect[d + '.cnf'] = d
        expect[d + '.lrat'] = json.loads(rec_bytes)['proof_sha256']
        expect[d + '.json'] = hashlib.sha256(rec_bytes).hexdigest()
    seen, raw = {}, 0
    dz = subprocess.Popen(['zstd', '-dc', '--long=27', '-q', str(tmp)], stdout=subprocess.PIPE)
    with tarfile.open(fileobj=dz.stdout, mode='r|') as tar:
        for m in tar:
            seen[m.name] = sha_stream(tar.extractfile(m))
            raw += m.size
    if dz.wait():
        raise RuntimeError('zstd -d failed')
    bad = [k for k, v in expect.items() if seen.get(k) != v]
    extra = sorted(set(seen) - set(expect))
    if bad or extra:
        raise RuntimeError('%s: %d bad, %d extra; first %s' % (name, len(bad), len(extra), (bad + extra)[:3]))
    os.replace(tmp, final)
    gz_bytes = sum((CERT / (d + s)).stat().st_size for d in digests for s in ('.cnf.gz', '.lrat.gz', '.json'))
    with open(final, 'rb') as f:
        archive_sha = sha_stream(f)
    index = dict(archive=final.name, archive_sha256=archive_sha, archive_bytes=final.stat().st_size, original_bytes=gz_bytes,
                 raw_bytes=raw, certificates=len(digests), members_checked=len(seen), digests=digests)
    (OUT / (name + '.index.json')).write_text(json.dumps(index))
    for d in digests:
        for s in ('.cnf.gz', '.lrat.gz', '.json'):
            (CERT / (d + s)).unlink()
    index.pop('digests')
    return index


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / '.gitignore').write_text('*.tar.zst\n*.tar.zst.tmp\n')
    have = sorted(p.name[:-5] for p in CERT.glob('*.json'))
    owner = {}
    for f in sorted(HERE.glob('threshold_*.json')):
        d = json.load(open(f))
        name = f.stem
        for dg in d.get('refutations', []):
            owner.setdefault(dg, name)
    groups = {}
    for dg in have:
        groups.setdefault(owner.get(dg, 'uncited'), []).append(dg)
    missing = sorted(set(owner) - set(have))
    summary = {}
    for name in sorted(groups):
        summary[name] = pack(name, groups[name])
        print(name, summary[name], flush=True)
    with gzip.open(OUT / 'index.tsv.gz', 'wt') as f:
        for name in sorted(groups):
            for dg in groups[name]:
                f.write('%s\t%s.tar.zst\n' % (dg, name))
    total = dict(archives=len(summary), certificates=sum(v['certificates'] for v in summary.values()),
                 archive_bytes=sum(v['archive_bytes'] for v in summary.values()),
                 original_bytes=sum(v['original_bytes'] for v in summary.values()),
                 cited_not_found=missing, per_archive=summary)
    (OUT / 'archives.json').write_text(json.dumps(total, indent=1))
    print({k: v for k, v in total.items() if k != 'per_archive'})
    if missing:
        sys.exit('cited certificates not found: %d' % len(missing))
