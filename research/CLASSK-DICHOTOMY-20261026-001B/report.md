# Sector counts on explicit gadget surgeries, all three patterns

Ticket `CLASSK-DICHOTOMY-20261026-001B`, 2026-10-27. Experiment `CLASSK-DICHOTOMY-20261026-001B-E001` (frozen contract, run once to
completion). **Verdict: supported.**

## The question

`CLASSK-DICHOTOMY-20261026-001A` (Theorem A) predicts every sector count of every class-(K) group from the gadget model alone. The
open step was realization: does the construction of `COPRIME-CLASS2-20261026-001D` §3 produce manifolds with exactly the gadget's
twisted cohomology and cup products, for all three slot patterns and on the knot exteriors? `PATTERN1-CHECKPOINT-20261026-001`
had built only pattern 1 at p = 7, r = 6, for one group and two sectors.

## What was built

**Eight surgeries**, by the projector construction:

| Fixture | Base summands | Components | Crossings |
| --- | --- | --- | --- |
| P1-K2, characters (ζ, ζ², ζ³) at p = 7, r = 6 | 3₁, 3₁, 6₁, 5₂ | 7 | 1,761 |
| P1-digon | 3₁ × 2, 6₁ × 2, 5₂ × 2 | 13 | 4,124 |
| P1-K2 ⊔ K2 | 3₁ × 4, (6₁, 5₂) × 2 | 13 | 3,622 |
| P2-K2, characters (ζ, ζ, ζ⁴) | 3₁ × 3, 6₁ | 7 | 1,768 |
| P2-digon | 3₁ × 4, 6₁ × 2 | 13 | 4,114 |
| P3-K2, characters (ζ², ζ², ζ²) | 6₁ × 4 | 7 | 2,216 |
| P3-digon | 6₁ × 6 | 13 | 5,324 |
| P2-K2 at p = 5, r = 4, characters (2, 2, 4) | 6₁ × 3, 4₁ | 7 | 589 |

The construction:
- eigenprojector combs with literal multiplicities r⁻¹χ^{−j} mod p;
- bands winding j times in direction −1;
- balanced band sums above the diagram;
- disk-framed leaves;
- each Y-graph as surgery on its six-component link.

**Test groups.** At (7, 6):
- free class 2 on (3, 2, 6);
- two hard sectors (3, 2, 6, 4, 5), where [e₅, e₄] is seen by ψ⁵;
- commutators involving the trivial character (1, 3, 2, 6);
- free class 2 on (3, 3, 4);
- pattern 2 with a trivial character;
- free class 2 on three coordinates of character 2;
- Heisenberg (2, 2);
- pattern 3 with a trivial character.

At (5, 4): two Heisenberg groups, free class 2 on (2, 2, 4), and a variant with a trivial character. Six pattern-3 pairs were
excluded by size before the freeze.

**Measured.** Every twisted H¹, every cup-product class, and the kernel count of every sector ψ^k for every group. This was done
on the closed r-surgery and on the knot exterior (knot framing relator dropped, trivial character included).

## Results

- **Manifolds.** Every closed surgery has H₁ = Z/r with ψ well defined and onto. The clasper-only surgery has trivial H₁.
  Dimensions are as predicted, for example (2, 1, 1, 1, 2) for P1-K2 and (0, 6, 0, 6, 0) for P3-digon. Each knot exterior adds
  H¹(X; F_p) = F_p.
- **Purity.** On the four K₂ fixtures every leaf functional is nonzero exactly on its slot character.
- **Counts.** All 108 group-by-fixture comparisons equal the frozen predictions in every sector (6 at p = 7, 4 at p = 5), closed
  and knot. Examples:

| Fixture, group | Closed ψ⁰…ψ⁵ | Knot exterior ψ⁰…ψ⁵ |
| --- | --- | --- |
| P1-K2, two hard sectors | 1, 45619, 2401, 343, 2401, 218491 | 16807, 45619, 2695, 16807, 2695, 218491 |
| P1-K2, trivial-character commutators | 1, 133, 49, 49, 49, 2401 | 2401, 211, 133, 2401, 133, 2695 |
| P3-digon, Heisenberg (2, 2) | 1, 46101601, 13841287201, 1, 46101601, 13841287201 | (as predicted) |
| P2-K2 at p = 5, Heisenberg (2, 4) | 1, 145, 5, 625 | (as predicted) |

- **The checkpoint values.** 133 (ψ¹) and 2401 (ψ⁵) on P1-K2 are reproduced.
- **Machinery controls**, rerun first, all pass:
  - dimensions equal cp_lib's at (7, 6) and (5, 4);
  - 138 and 48 maps to S₃ for the Borromean rings;
  - the counting path equals cp_lib's Heisenberg counts per sector;
  - the counting path, times |Z¹(A)| |B¹(B)|, equals direct lifting counts for two non-Heisenberg groups;
  - the u-pairing of single twist-knot exteriors equals the pre-registered calibration;
  - the winding calibration holds at p = 5.

## What it shows

**Realization.** The construction realizes the gadget tensors of all three slot patterns at two (p, r). The structure of the knot
exteriors is as stated, which is what the knot-group corollary uses:
- the u-pairing is unchanged by the moves;
- it is block-diagonal over the summands.

**What the predictions encode.** Each one came from the gadget model through Theorem A, or through the model extended by u. None
came from the fixtures.

**Knot groups differ from closed manifolds exactly as predicted.** With trivial-character commutators, ψ¹ gives 211 on the knot
group against 133 on the closed surgery.

## Process notes

- **Restarts.** The run was killed twice by session restarts (KeyboardInterrupt) after it had completed P1-K2. Both partial logs are
  kept: `run_log_interrupted_by_container_restart.txt` and `_2.txt`.
- **The completed run.** It was launched unchanged as its own systemd user unit and finished in 3,058 s, inside the 14,400 s budget.
  Its P1-K2 rows equal those seen before the interruptions.
- **Scoping before the freeze**, disclosed in the contract:
  - geometry of every fixture;
  - the machinery controls (one test-geometry repair at p = 5);
  - the pipeline on P1-K2 for the checkpoint's published values only;
  - the u-pairing calibration.

## Limits

- Eight small fixtures at two (p, r). Correctness on every graph rests on the proof of `COPRIME-CLASS2-20261026-001D` §3.
- The Y-graph surgery is computed through its six-component link, validated in the checkpoint, not reproved.
- Predictions and measurements share ticket A's bilinear counter, but not their inputs. V7 and V8 check the measurement path
  against independent counts.
- No external review.
