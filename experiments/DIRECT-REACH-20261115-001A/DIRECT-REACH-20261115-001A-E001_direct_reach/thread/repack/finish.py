"""After repack_job.py (DIRECT-REACH-20261115-001, the thread's own, 2026-11-16): write the index of the certificate archives, check
that every certificate in codex/certificates/ is in exactly one verified archive, and, only with --remove, delete the originals of
certificates whose archive verified. Without --remove nothing is deleted."""
import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parents[1]
CERT = EXP / 'codex/certificates'
OUT = EXP / 'codex/certificate_archives'
sys.path.insert(0, str(EXP.parents[2] / 'scripts'))
from longrun import load_results  # noqa: E402

results = load_results(str(HERE / 'run'))
ok = {cid for cid, rec in results.items() if rec['status'] == 'ok'}
where, rows, total_archive, total_orig = {}, [], 0, 0
for idx in sorted(OUT.glob('*.index.json')):
    d = json.loads(idx.read_text())
    name = d['archive'][:-len('.tar.zst')]
    if name not in ok:
        continue
    for dg in d['digests']:
        if dg in where:
            raise SystemExit('certificate in two archives: ' + dg)
        where[dg] = d['archive']
    rows.append(d)
    total_archive += d['archive_bytes']
    total_orig += d['original_bytes']
on_disk = sorted(p.name[:-5] for p in CERT.glob('*.json'))
missing = [d for d in on_disk if d not in where]
print('archives', len(rows), 'certificates indexed', len(where), 'on disk', len(on_disk), 'not archived', len(missing))
print('original %.2f GB -> archives %.2f GB' % (total_orig / 1e9, total_archive / 1e9))
with gzip.open(OUT / 'index.tsv.gz', 'wt') as g:
    g.write('cnf_sha256\tarchive\n')
    for dg in sorted(where):
        g.write('%s\t%s\n' % (dg, where[dg]))
(OUT / 'archives.json').write_text(json.dumps([{k: v for k, v in d.items() if k != 'digests'} for d in rows], indent=1))
(OUT / 'INDEX.md').write_text(f"""# Certificate archives of DIRECT-REACH-20261115-001A

Repacked on 2026-11-16 at John's choice from `codex/certificates/` ({len(where)} certificates, {total_orig / 1e9:.2f} GB as gzip files)
into {len(rows)} zstd archives ({total_archive / 1e9:.2f} GB). Each certificate is named by the SHA-256 of its raw CNF and has three
members: `<digest>.cnf` and `<digest>.lrat` (raw, decompressed) and `<digest>.json` (its record, with `proof_sha256`, the SHA-256 of
the raw LRAT). A certificate lives in the archive of the first description, in sorted order of
`artifacts/DIRECT-REACH-20261115-001A/DIRECT-REACH-20261115-001A-E001_direct_reach/certificate_hashes.json.gz`, that cites it;
`uncited.tar.zst` holds those no description cites (gates and controls); pilot descriptions are `pilot_<case>.tar.zst`. Every member was
read back and checked against its hash before the archive was put in place (`../../thread/repack/repack_job.py`).

- Which archive holds a certificate: `zcat index.tsv.gz | grep <digest>` (columns: digest, archive).
- Extract one description: `mkdir -p out && zstd -dc --long=27 <case>.tar.zst | tar -x -C out`
- Extract one certificate: `zstd -dc --long=27 <archive> | tar -x -C out <digest>.cnf <digest>.lrat <digest>.json`
- Check a proof: `<cadical-checker> out/<digest>.cnf out/<digest>.lrat` (the census's `lrat_check`), and
  `sha256sum out/<digest>.cnf` equals `<digest>`.
- Per-archive sizes and hashes: `archives.json`.
""")
if '--remove' in sys.argv:
    if missing:
        raise SystemExit('refusing to remove: %d certificates are not in a verified archive' % len(missing))
    n = 0
    for dg in sorted(where):
        for suffix in ('.cnf.gz', '.lrat.gz', '.json'):
            p = CERT / (dg + suffix)
            if p.exists():
                p.unlink()
                n += 1
    print('removed', n, 'original files')
