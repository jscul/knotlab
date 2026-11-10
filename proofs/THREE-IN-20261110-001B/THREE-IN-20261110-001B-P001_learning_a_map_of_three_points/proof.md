# Learning a map of three held points

Status: Proved (computed, frozen). `check.py` (about 32 minutes, four interfaces in parallel), ticket B of
`research/THREE-IN-20261110-001/preregistration.md`, frozen in stage 1 (commit `f3dff17a6`) after the census and before any learning run.

## The test

At one interface per test space (the first in census order where a total map occurs), the credit learner of
`CREDIT-PIN-20261110-001B` with the sturdier probe of `STURDY-PROBE-20261110-001A` extended to three inputs learned, in turn, the census's
single-input map, then parity `01101001` and majority `00010111`, which the census proves impossible there.

## Results

| Space | Single-input map | Parity | Majority | Probe steps |
| --- | --- | --- | --- | --- |
| S1 (K_3, three thin leaves) | `10101010` learned and held (806,400 steps) | not stopped | not stopped | 689,925,434 |
| S2 (K_3, three Fano leaves) | `10101010` learned and held (706,400 steps) | not stopped | not stopped | 373,736,436 |
| S3 (two-level, thin) | `00001111` not stopped | not stopped | not stopped | 131,922,214 |
| S4 (two-level, Fano) | `00001111` not stopped | not stopped | not stopped | 128,371,341 |

- **Mark I held:** parity and majority never stopped (8 of 8); the learner, with the sturdier probe, never accepted a map the census
  rules out.
- **Mark L3 failed:** the single-input map was learned and held at 2 of 4. On S3 and S4 it occurs in only 12 of 256 classes at that
  interface (a frozen pair), and the learner did not find one in 4,000,000 steps.
- At the end of the parity and majority runs the maps were gates in two of the inputs (for example `1uu01uu0`) or never decided: unate,
  as the census says every map here is.
