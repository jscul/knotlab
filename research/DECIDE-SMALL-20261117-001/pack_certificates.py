"""Pack DECIDE-SMALL-20261117-001's ground-truth LRAT certificates (the thread's own, 2026-11-17) with CARRIER's packer
(research/CARRIER-20261117-001/pack_certificates.pack: tar of raw CNF, raw LRAT and record, zstd -12 --long=27, every member read back
and hash-checked before the archive is put in place, then the originals removed). One archive, ground_truth.tar.zst, in
artifacts/DECIDE-SMALL-20261117-001/certificates/ (not tracked), with its index files (tracked)."""
import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'research/CARRIER-20261117-001'))
import pack_certificates as pc  # noqa: E402

pc.CERT = ROOT / 'experiments/DIRECT-REACH-20261115-001A/DIRECT-REACH-20261115-001A-E001_direct_reach/codex/certificates_decide'
pc.OUT = ROOT / 'artifacts/DECIDE-SMALL-20261117-001/certificates'
pc.OUT.mkdir(parents=True, exist_ok=True)
(pc.OUT / '.gitignore').write_text('*.tar.zst\n*.tar.zst.tmp\n')
digests = sorted(p.name[:-5] for p in pc.CERT.glob('*.json'))
summary = pc.pack('ground_truth', digests)
with gzip.open(pc.OUT / 'index.tsv.gz', 'wt') as f:
    for d in digests:
        f.write('%s\tground_truth.tar.zst\n' % d)
(pc.OUT / 'archives.json').write_text(json.dumps(summary, indent=1))
print(summary)
