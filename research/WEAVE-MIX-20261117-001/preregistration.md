# Can a mixed arrangement of not-all-equal knots on the weave be disordered? Pre-registration

Epic `WEAVE-MIX-20261117-001`, 17 November 2026, by Claude, on the coordinator's go-ahead (the first direction of
`WEAVE-LAWS-20261117-001`). Goals G1 and G16; tests A97. Frozen before any read-out of ticket B. The canonical K1–K3 test is
unchanged.

## The question

Only the not-all-equal class of knots is pairwise: a base built from them is determined by its pair counts and N
(`DISTANCE-ORDER-20261117-001A`, statement 3(a); `WEAVE-LAWS-20261117-001A`, L1). On the six-regular weave, every arrangement
whose signs agree is critical (a gauge copy of the triangular antiferromagnet). The four uniform arrangements with disagreeing
signs that were tested are frozen. So the question is whether some non-uniform periodic arrangement of the four
not-all-equal-class knots is disordered. If one is, its pair-count distance both carries the information and is a ruler on the
weave's meeting pattern: in the owner's terms, a distance that carries the information and steps outward from a start without
skipping.

As before, a ruler found here reads how the knots meet in this one sample. It does not show a law adding or choosing a dimension.

## Ticket A: the proof (written before this freeze)

`proofs/WEAVE-MIX-20261117-001A/WEAVE-MIX-20261117-001A-P001_broken_bonds/proof.md`, checked by its `check.py`.
- **N1.** Each knot has exactly one bond broken in its own signs.
- **N2.** States up to the global flip are perfect matchings of the honeycomb with every inconsistent bond subdivided, in the
  torus sector that closes up.
- **N3.** Per cell, 2 = 2u + i. More than two inconsistent bonds per cell empties the base, and period one gives i = 0 or 2.
- **N4.** The matching graph is bipartite iff every distinction meets an even number of inconsistent bonds.

## Bases and readings (ticket B)

**Bases.** Every arrangement with column and row periods (1, 1), (2, 1) or (1, 2): 16, 256 and 256 arrangements. Then 150 random
ones, with seeds sha256 "WM:pc×pr", for each of (3, 1), (1, 3) and (2, 2).

**For each arrangement:**
- its inconsistent set I, the count per cell, and whether every distinction meets an even number of bonds of I;
- per-row transfer spectra split by the global flip, at widths 6, 9, 12 (column period 1 or 3) or 6, 8, 10, 12 (column period
  2): states per distinction, the spin gap (top flip-even against top flip-odd) and the energy gap (top against second
  flip-even), in log base 3 per row.

**Classification at width 12.**

| Class | Rule |
| --- | --- |
| empty | no state |
| frozen | states per distinction below 1.01 |
| ordered | spin gap below 0.01 with energy gap above 0.05 |
| disordered | both gaps above 0.05 and each within 10% of its value at the next smaller width |
| critical | spin gap smaller at 12 than at 6, and spin gap × width at 12 within 15% of its value at 6 |
| unresolved | otherwise: a correlation length too long for these widths, or anything else |

**For each disordered arrangement:** the connected correlation of distinctions 0, 1 and 2 of a row with the same distinction r
rows away, on the infinite cylinder of width 12 (rounded down to the column period). This checks every sublattice: a rigid
sublattice would show as a non-decaying correlation.

## Predictions (frozen; the advisor's analysis, checked where it could be)

| # | Prediction | Fails when |
| --- | --- | --- |
| Q0 | Arrangements with the same inconsistent set have the same spectrum at width 6, to 10⁻⁹ (the gauge) | a larger deviation |
| Q1 | Every arrangement with I empty is critical | any is not |
| Q2 | Every arrangement with more than two inconsistent bonds per cell is empty (N3) | any has states |
| Q3 | No arrangement in which every distinction meets an even number of inconsistent bonds is disordered (the matching graph is bipartite: liquid or frozen expected) | one is disordered |
| Q4 | At least one arrangement with a distinction meeting an odd number of inconsistent bonds is disordered (a non-bipartite matching graph, expected to be a Z₂ liquid with exponential decay, as Fendley, Moessner and Sondhi found for triangular-lattice dimers) | none is, among all six families |
| Q5 | Every disordered arrangement's direct correlations decay at all three positions (no rigid sublattice) | a non-decaying one |

**What each outcome would mean, stated before running.**
- **Q4 and Q5 hold.** A non-uniform arrangement of the pairwise knots is disordered on the weave. Its pair counts carry all its
  information (proved for the class), and its counts' log grows linearly with distance. That is the premise's positive case on
  this meeting pattern. It would also say what it takes: knots whose signs disagree on an odd number of bonds at some
  distinction.
- **Q4 fails.** Among these small periods, the pairwise knots on the weave are critical, frozen, ordered or unresolved. Information
  and a scale then stay apart on this pattern, at least at small periods.
- **Q3 fails.** A bipartite matching graph can be gaseous at uniform weight here, which would be notable in itself (Kenyon,
  Okounkov and Sheffield's gaseous phase).

## Prior work in the program

`python3 -B scripts/track.py objects "mixed signed not-all-equal knots weave disordered matchings" --until 2026-11-17 --exclude WEAVE-MIX-20261117-001`

- `WEAVE-LAWS-20261117-001`: uniform laws on the weave (the predecessor).
- `DISTANCE-DIM-20261117-001`: the off-critical chain grid gives a ruler.
- `DISTANCE-ORDER-20261117-001`: the pair table determines not-all-equal-class bases.
- `KNOTS-ALONE-20261111-001`: a relative (not-all-equal on regular two-fold weaves, read through bond distance).
- `PARITY-MIX-20261112-001`: unrelated (parity placements among stitched copies; matched on "mixed").

## Prior work outside the program

- **Frustration and dimers:** Wannier; Blöte and Hilhorst; Moessner and Sondhi.
- **Dimer phases:** Kasteleyn; Kenyon, Okounkov and Sheffield 2006; Fendley, Moessner and Sondhi 2002.
- **Gauge:** Mattis; Toulouse.

## Runs and stop rule

One script, `run.py`, one process. It is expected to take about 45 minutes, so it is registered in `docs/LONG_RUNNING.md` and run
in the background. The study stops after its read-out, followed by A97 status, the decision note, the referee hand-off and the
report.

The advisor model was consulted before this freeze. It confirmed N1 and N2 and gave:
- the contraction picture;
- the bipartite criterion N4 and the "only I matters" count;
- the predictions Q3 and Q4;
- the two-gap reading;
- the warning that a correlation length above about 10 cannot be resolved at these widths (hence "unresolved"), and that rigid
  sublattices must be checked.
