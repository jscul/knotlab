# Solver record

Experiment evidence for `COUNT-NOTE-20261107-001B`; not part of the proof.

- `export_spheres.py` writes `spheres.json` (k = 2..8) from `count_lib.signed_space(octa_dual(k))`.
- `cp_scout.py` runs Exact, a cutting-planes solver (`pip install exact`).
- `xor_scout.py` runs CryptoMiniSat with native XOR constraints (`pip install pycryptosat`).
- `cdcl_scout.py` runs CaDiCaL through python-sat (the repository's .venv).

The scripts were run from a scratch directory on 2026-11-07, with the outputs recorded in `solver_runs.json`. `check.py` reads that
file; it does not rerun the solvers.

The CaDiCaL script originally used a conflict budget, and that first run was lost: its output was piped and the run reached its
background time limit. The script here is the second version, with a 600 s timer. CaDiCaL did not honour the interrupt, so its k = 7
run was stopped by hand at 2476 s.
