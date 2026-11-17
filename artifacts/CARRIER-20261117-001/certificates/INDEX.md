# Certificates of CARRIER-20261117-001's threshold runs

Packed on 2026-11-17 by `research/CARRIER-20261117-001/pack_certificates.py` from the gzip files the runs wrote to DIRECT-REACH's
`codex/certificates_carrier/` (79,393 certificates, 18.14 GB as gzip) into 15 zstd archives (2.09 GB). The originals were removed
after every member of every archive was read back and checked against its hash. They were this task's own files.

- One archive per threshold file (`research/CARRIER-20261117-001/threshold_*.json`, `threshold_deep_*.json`), holding the
  certificates it cites (the first file in sorted order owns a shared one), and `uncited` for the rest (the smoke run, and searches
  cut off by their budget).
- Members: `<digest>.cnf` and `<digest>.lrat` (raw), and `<digest>.json` (the record, with `proof_sha256` of the raw LRAT). The digest
  is the SHA-256 of the raw CNF.
- Which archive holds a certificate: `zcat index.tsv.gz | grep <digest>`. Per-archive sizes and hashes: `archives.json` and
  `<name>.index.json`.
- Extract: `mkdir -p out && zstd -dc --long=27 <name>.tar.zst | tar -x -C out`. Check a proof with the census's `lrat_check`, and that
  `sha256sum out/<digest>.cnf` equals the digest.
- The archives themselves are not tracked by git (`.gitignore`); the index files are.
