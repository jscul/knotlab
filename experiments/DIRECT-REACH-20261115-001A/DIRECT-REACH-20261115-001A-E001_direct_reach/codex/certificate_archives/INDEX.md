# Certificate archives of DIRECT-REACH-20261115-001A

Repacked on 2026-11-16 at John's choice from `codex/certificates/` (240509 certificates, 29.42 GB as gzip files)
into 135 zstd archives (8.99 GB). Each certificate is named by the SHA-256 of its raw CNF and has three
members: `<digest>.cnf` and `<digest>.lrat` (raw, decompressed) and `<digest>.json` (its record, with `proof_sha256`, the SHA-256 of
the raw LRAT). A certificate lives in the archive of the first description, in sorted order of
`artifacts/DIRECT-REACH-20261115-001A/DIRECT-REACH-20261115-001A-E001_direct_reach/certificate_hashes.json.gz`, that cites it;
`uncited.tar.zst` holds those no description cites (gates and controls); pilot descriptions are `pilot_<case>.tar.zst`. Every member was
read back and checked against its hash before the archive was put in place (`../../thread/repack/repack_job.py`).

- Which archive holds a certificate: `zcat index.tsv.gz | grep <digest>` (columns: digest, archive; on this machine only, not
  committed; the committed `certificate_hashes.json.gz` and the rule above give the same map).
- Extract one description: `mkdir -p out && zstd -dc --long=27 <case>.tar.zst | tar -x -C out`
- Extract one certificate: `zstd -dc --long=27 <archive> | tar -x -C out <digest>.cnf <digest>.lrat <digest>.json`
- Check a proof: `<cadical-checker> out/<digest>.cnf out/<digest>.lrat` (the census's `lrat_check`), and
  `sha256sum out/<digest>.cnf` equals `<digest>`.
- Per-archive sizes and hashes: `archives.json`.
