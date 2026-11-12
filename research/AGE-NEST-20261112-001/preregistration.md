# What the expanding growth's degrees do not carry: pre-registration

Epic `AGE-NEST-20261112-001` (`OLD-CORE-20261112-001` direction 1; G17, with G7), 2026-11-12, at the coordinator's go-ahead. Frozen
before the registered run. The canonical K1–K3 test is unchanged. Words as in `OLD-CORE-20261112-001`: the dying core is the knots
among the oldest k* distinctions, k* the least at which they allow no state; a knot's **youngest** distinction is its last to arrive.

## The question

In growth with closings anywhere (X), patterns with the dying core's degrees never end (`OLD-CORE-20261112-001`, referee pending).
What structure beyond degrees carries the end? The weighting is the process X(q) (A71).

## In standard terms

For the first non-2-colourable prefix of a grown 3-uniform hypergraph, which ensemble of resamples, from degree-preserving to
history-preserving, keeps it non-2-colourable?

## What is settled by definition (checks, not tests)

- **Keeping the pair counts reproduces the end** (`OVERLAP-READ-20261111-001`'s lemma: not-all-equal's states depend only on how many
  knots lie on each pair). So a pair-count resample is not a test. Its freedom is the patterns with the same pair counts, which is
  non-empty exactly where the core holds a trade; the smallest is the Pasch configuration (four knots replaced by the complementary
  four), and larger trades exist. Control Q0 applies one Pasch trade where one exists and checks that no state is allowed.
- Each rung keeps k* distinctions and the core's number of knots. R2 keeps every count of knots among the oldest j distinctions, by
  construction. FULL redraws under the growth's own rule with the core's schedule kept, so it measures how much the schedule decides
  the end, not a mechanism (the advisor's reading).

## Design (frozen; `census.py`)

OLD-CORE's X(0.25), X(0.3) and X(0.35) endings regenerated from its seeds, the pilot's twelve excluded. Twenty resamples per rung per
core: **SW** degrees kept (a switch chain); **R2** degrees and every knot's youngest distinction kept (the same chain restricted to
the two older members); **R2p** youngest kept, the other two redrawn among older distinctions; **FULL** the growth's rule with the
schedule kept. For each: the share that allow no state, and the share identical to the core in pair counts. **Fairness:** both
chains choose a pair of knots and one member of each uniformly and count rejections as steps, so they are symmetric and uniform on
their components; on five degree sequences (one regular, four uneven like the cores) every simple pattern is enumerated and the
exact transition matrices are checked: symmetric, and connected within the classes each chain must preserve (computed before the
freeze: all pass).

## Predictions (frozen)

The advisor model reviewed a draft cold. It showed that the draft's comparison of FULL with SW was not nested (FULL drops degrees,
SW drops the schedule), proposed R2 as the nested rung (degrees plus each knot's youngest, keeping the oldest-j counts), asked for
paired per-core tests, the share of forced resamples, X(0.25) as report-only, and the pilot cores held out.

| # | Prediction | Fails when |
| --- | --- | --- |
| N1 | **Degrees miss it (replicated with a fair chain).** In X(0.3) and X(0.35) the median over cores of the SW share that end is at most 0.1. | either above |
| N2 | **The nesting carries it.** In X(0.3) and X(0.35) the median R2 share is at least 0.2, and among cores where the two differ, R2's share exceeds SW's in at least 70%. | either part, either setting |
| N3 | Reported: R2p and FULL, the shares identical in pair counts, X(0.25). | — |
| Q0 | Control: every Pasch trade applied keeps the pair counts and allows no state. | a bug |

## Pilot (disclosed)

Twelve OLD-CORE endings (scratchpad; held out): switch-chain shares 0 to 0.1; redrawn closings with births kept about 0.4; redrawn
births with closings kept about 0.25; Pasch trades 0 to 3 per core. A smoke test of the frozen code on one held-in core (X(0.3)
run 5): SW 0, R2 0.9, R2p 0.55, FULL 0.8.

## Stop rule and runtime

One run, its summary, a hand-off to the referee thread, report. About fifteen minutes on eight workers.
