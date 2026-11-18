# The surviving weave pair, with the twist fixed: pre-registration

Epic `WEAVE-PAIR-20261118-001`, 18 November 2026, by Claude, on the coordinator's queue. It is the first direction of
`WEAVE-MIX-20261117-001` after that study's referee. Goals G1 and G16; tests A97. Frozen before any read-out of ticket B. The
canonical K1–K3 test is unchanged.

## The question

`WEAVE-MIX-20261117-001` left one candidate pair on the weave: two 3 × 1 arrangements of not-all-equal-class knots, each with a
distinction meeting an odd number of inconsistent bonds. Its referee found them gapped to width 18 in both period parities, and
found that they are not gauge copies.

The questions here:
1. **The class.** With the twist around the cylinder set explicitly, both sectors computed, is the pair gapped (disordered)?
2. **The ruler.** Does its pair-count distance step outward from a start without skipping, the owner's premise on this pattern?
   For this class of knots the pair counts carry all the information (proved).
3. **One or two.** Are the two arrangements one, up to a symmetry of the weave?

## Ticket B: the computation

`experiments/WEAVE-PAIR-20261118-001B/WEAVE-PAIR-20261118-001B-E001_twist/`: `twistlib.py`, `run.py`, `checks.py`. It reads
`WEAVE-MIX-20261117-001B-E001`'s `mixlib.py` (closed) for the inconsistent bonds, pinned by hash. Six checks pass before this
freeze:
- the transfer applied one distinction at a time equals the dense one at widths 6, 9 and 12 in both sectors;
- the plain law reproduces `WEAVE-MIX`'s stored numbers;
- the symmetry tools work.

**The twist.** In the antiperiodic sector every knot crossing the seam reads column 0 flipped. The knots are closed under the global
flip, so there are no other sectors.

**Parts:**
- **W1.** For each of the weave's 12 point symmetries and each translation, does it carry arr1's inconsistent bonds onto arr2's?
- **W2.** Both arrangements, both sectors, flip-even and flip-odd, at widths 6 to 21 (Arnoldi from 15). Read:
  - states per distinction, the spin gap and the energy gap;
  - the free-energy splitting between the sectors;
  - the seam moved one column, as a check.
- **W3.** Exact correlations at width 12, both arrangements and sectors.
  - Along the transfer: C(r) for r = 1 to 30 at each column position. τ(r) = −log₃ |C(r)| is the pair-count distance's log.
  - Around: up to 6 columns.
  - Read: the slope of τ fitted on r = 10 to 30, and the local slopes.
  - Read: whether |C(r)| strictly decreases at single-row resolution, and whether its even-r and odd-r subsequences each strictly
    decrease. This **two-row tick** is declared now as an envelope reading.

## Predictions (frozen; the advisor's where marked)

| # | Prediction | Fails when |
| --- | --- | --- |
| Q1 | W1: arr2 is arr1 rotated by 180° (with a translation), up to a gauge: some point symmetry carries arr1's inconsistent bonds onto arr2's (advisor) | none does |
| Q2 | W2: arr1 and arr2 have the same spectra in the same sector when w/3 is even (6, 12, 18), and arr1 antiperiodic equals arr2 periodic when w/3 is odd (9, 15, 21), to 10⁻⁶ (advisor: the residual difference is one seam per period) | otherwise |
| Q3 | W2: gapped in both sectors: at widths 15, 18 and 21 the spin gap and the energy gap each agree within 5%, near 0.315 and 0.630 | otherwise |
| Q4 | W2: the free-energy splitting between the sectors shrinks at least threefold from width 12 to 21 (gapped: exponentially small) | it does not |
| Q5 | W3: the single-row ruler fails at positions 0 and 2 (|C| not strictly decreasing), and the two-row tick holds at every position in both sectors (advisor) | the two-row tick fails anywhere |
| Q6 | W3: the fitted slope of τ on r = 10 to 30 is within 10% of the width-12 spin gap at every position and sector | otherwise |

**What would count against it.**
- A gap that closes (Q3).
- A splitting that does not shrink (Q4): then the pair is critical or ordered, not disordered.
- A two-row tick that fails (Q5): then even the envelope ruler fails.

**What would be a positive for the owner's premise.** The distance, which carries the information, steps outward strictly. Here
the advisor expects that only at a two-row tick: an envelope ruler, a third envelope case after OR and hard hexagons. A strict
single-row ruler would be a real positive, and is not expected.

## Prior work

- `WEAVE-MIX-20261117-001` and its referee (the pair, its gaps to width 18, not gauge copies).
- `WEAVE-LAWS-20261117-001` (envelope rulers of OR and hard hexagons).

## Runs and stop rule

`run.py --part W1`, `W2`, `W3`, each its own process, then `--merge`. W2 at width 21 is expected to take tens of minutes and is
registered in `docs/LONG_RUNNING.md`. The study stops after its read-out, followed by A97 status, the decision note, the referee
hand-off and the report.

The advisor was consulted before this freeze. It:
- found the 180° rotation with a seam;
- confirmed that the twist has two sectors;
- predicted the gaps and the failure of the single-row ruler;
- asked for the frozen fit window, the two-row tick declared in advance, the splitting diagnostic and more Arnoldi eigenvalues.

All of these are in the design.
