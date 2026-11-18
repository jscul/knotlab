# Certificates of DECIDE-SMALL-20261117-001's ground-truth check

Packed on 2026-11-18 by `research/DECIDE-SMALL-20261117-001/pack_certificates.py` (CARRIER's packer): 22,183 LRAT certificates of the
census's certified search (5.02 GB as gzip; 51.1 GB raw) in one zstd archive, `ground_truth.tar.zst` (1.49 GB). Every member was read
back and hash-checked before the archive was put in place, and the originals (this task's own) were then removed.
- Members: `<digest>.cnf` and `<digest>.lrat` (raw) and `<digest>.json` (the record, with `proof_sha256` of the raw LRAT).
- Extract: `mkdir -p out && zstd -dc --long=27 ground_truth.tar.zst | tar -x -C out`; check with the census's `lrat_check`.
- The archive is not tracked by git; `ground_truth.index.json`, `index.tsv.gz` and `archives.json` are.
