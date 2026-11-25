# DESCENT-HELD-20261125-001A-E001: the order in a knot's own places, the confirming run

A second program, written from the frozen texts without the drafter's scratch prototype: the pre-registration
(`research/DESCENT-HELD-20261125-001A/preregistration.md`), the note and its definitions (`research/DESCENT-HELD-20261125-001/`),
the shared definitions (`research/RING-IN-BALANCE-20261123-001/definitions.md`) and the data files beside the
pre-registration. Readings taken where the texts leave a choice, and the one place where a frozen statement is too broad,
are in [deviations.md](deviations.md).

Imported unchanged: `lr_core.py` (LOCAL-ROUND-20261123-001A: `compute_groups`, `start_stars`, `own_round` for the gate),
`cpcensus.py` (COPYING-PARTS-20261123-001A: the census), `knots.py` (PARTS-MEET-AGAIN-20261124-001A: `parity_test`,
`nae_decomposed`, `nae_direct`). Their sha256 are written into every output file.

| File | What |
| --- | --- |
| `dh_common.py` | paths, the three imports, data files, output |
| `dh_engine.py` | the complete round (SD steps 1-8) with the three forms of the ration (DH 3.2), runs, the place rule, conditions (a), (b′), (c), (d), an exact isomorphism test of structures |
| `dh_analysis.py` | reading a run: arm R (base law) and arm W (a count form), with the judgements of P3-P6 |
| `dh_census.py` | the census, kept flags, the two weightings, the six-knot sample's order, canonical forms of small structures |
| `part0.py` ... `part8.py` | the registered parts, in order |
| `sum_part1.py` | part 1's counts from its raw runs |
| `diag_joint.py` | after part 1: the joint stratum under three readings of a closing knot's places (deviations 30) |
| `summarize.py` | `summary.json` and `summary.md`: one row per prediction |

Run (each part under a 6 GB cap, at most 6 processes, 4 while the load is above 18):

```
ulimit -v 6291456
.venv/bin/python -B part0.py      # checks; then part1.py, sum_part1.py, part2.py ... part8.py, summarize.py
```

Outputs: `artifacts/DESCENT-HELD-20261125-001A/DESCENT-HELD-20261125-001A-E001_order_in_own_places/` (one file per
part, `part1_runs.json.gz` with every census run, `part8.json.gz`, `summary.json`, `summary.md`, `logs/`).

Words as in the frozen texts: "parent steps", "count in threes", "new knot", "the place rule is right on", "shown
within d". The ration writes the count and nothing else uses it; no pattern counts; nothing here is a clock.
