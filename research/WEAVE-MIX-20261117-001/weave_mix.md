# Can a mixed arrangement of not-all-equal knots on the weave be disordered?

Epic `WEAVE-MIX-20261117-001`, 17 November 2026, by Claude, on the coordinator's go-ahead (the first direction of
`WEAVE-LAWS-20261117-001`). Goals G1 and G16; tests A97. Refereed: report [R1](referee-R1/report.md), confirmed with fixes, no
Block, folded in on 17 November (see Referee). Pre-registration: [preregistration.md](preregistration.md),
frozen in commit `35348250b` at 20:02:19 UTC; the run went from 20:02:34 to 21:24:47 UTC (82 minutes; registered at about 45).
Proof: [proof.md](../../proofs/WEAVE-MIX-20261117-001A/WEAVE-MIX-20261117-001A-P001_broken_bonds/proof.md). Code:
[mixlib.py, run.py and readout.py](../../experiments/WEAVE-MIX-20261117-001B/WEAVE-MIX-20261117-001B-E001_mixes/). Results:
[results.json and readout.json](../../artifacts/WEAVE-MIX-20261117-001B/WEAVE-MIX-20261117-001B-E001_mixes/).

## The answer

**Not settled. The frozen reading broke on the twist around the cylinder, so most of its "disordered" verdicts are artifacts.
Read again post hoc, two arrangements are gapped one size past, both with a distinction that meets an odd number of inconsistent
bonds; none with every count even reads disordered.** *Narrowed after the referee: of the four post hoc survivors, the two in the
2 × 2 family fall apart into independent pieces and are not candidates.*
- **What broke.** The frozen rule compared width 12 with the next smaller width (9, or 10 for column period 2). Its number of column
  periods has the other parity, and arrangements with the same inconsistent bonds differ by the twist around the cylinder (their
  holonomy), which changes with that parity. The knot-law study's referee had already found this twist at odd widths for the
  agreeing-signs law. So:
  - two arrangements with the same inconsistent bonds can have different spectra (up to 1.12 in log base 3 per row; Q0 failed);
  - gauge copies of the critical law were labelled disordered (Q1 failed);
  - 19 arrangements in which every distinction meets an even number of inconsistent bonds were labelled disordered (Q3 failed).
- **Read again with widths of the same parity** (post hoc, labelled: width 12 against 6, or against 8 for column period 2; frozen
  thresholds otherwise). Of the 69 arrangements the frozen rule called disordered, 51 read as critical, 14 as unresolved, and
  4 as disordered:
  - **two in the 3 × 1 family**, with the same spectra: 1.263 states per distinction, gaps 0.34, 0.31, 0.32 (spin) and 0.66,
    0.63, 0.63 (energy) per row at widths 6, 9 and 12. The correlations decay, from 0.30 at one row to 0.02 at seven. *After the
    referee:* they are not gauge copies, since their inconsistent bonds differ (probably one arrangement up to a symmetry of the
    weave). One size past, at widths 15 and 18, the spin gap is 0.314 to 0.316 and the energy gap 0.630 in both period parities.
    They are the one candidate, still post hoc, and their pair-count distance was not measured.
  - **two in the 2 × 2 family**, which the referee found decoupled. One falls into independent bands of two rows (the gaps are
    about 9, and the correlation along the transfer is exactly zero from two rows on). The other falls into independent strips
    of two columns (1.246504702770927 states per distinction at every width from 4 to 16, and no correlation around the cylinder
    beyond one column). Neither is a candidate.
  - No arrangement with every count even reads as disordered, as the bipartite picture expects.
- **The referee's 2 × 2 law** (index 3 on one up knot per 2 × 2 block, plain not-all-equal elsewhere) is unresolved under both
  rules. Its spin gap is 0.32, 0.26, 0.24 and 0.23 at widths 6 to 12, still drifting, and its energy gap is erratic. The referee
  has since withdrawn it as a disordered-looking case: at widths 14 and 16 the gap falls to 0.143 and 0.132.

In the owner's terms: knots whose bases are determined by their pair counts may still give the weave a distance that carries the
information and steps outward from a start. The 3 × 1 pair is the periodic candidate, and the referee's random 10% mix of signed
knots, which this study did not test, is the other lead. This study does not show it, because its frozen test
could not tell the twist from disorder.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| Q0 | Same inconsistent set, same spectrum at width 6 (to 10⁻⁹) | **failed** | 20 groups differ: in 2 × 1 by up to 1.12 (the twist); in 3 × 1 by 0.48, and in 1 × 1 and 1 × 2 by about 10⁻⁸ or by an infinite against a finite gap (a doubly degenerate top eigenvalue, split by the 10⁻⁹ threshold; the referee) |
| Q1 | Every arrangement with no inconsistent bond is critical | **failed** | 10 of 26 read disordered and 4 unresolved; post hoc all read critical except 8 unresolved in 2 × 1 |
| Q2 | More than two inconsistent bonds per cell: empty | held | 29 of 29 empty |
| Q3 | No all-even arrangement is disordered | **failed** | 19 read disordered; post hoc none |
| Q4 | Some arrangement with an odd count is disordered | held as frozen | 50 read disordered; post hoc 4 remain, 2 of them decoupled (the referee) |
| Q5 | Every disordered arrangement's correlations decay | **failed** | 64 of 69 decay; 5 do not, all critical post hoc |

Q5 needed a threshold that the pre-registration did not fix. The read-out counts a correlation as not decaying when its value at
the farthest distance is above 0.01 and above half its value at the first distance. Two of six predictions held. The four
failures come from the twist, except part of Q0's: at width 6 a doubly degenerate top eigenvalue was counted in some members of a
group and not others (the referee).

## What the knot picture explained

- **Only the inconsistent bonds and the twist matter.** The gauge leaves every distinction free to be read flipped, so an
  arrangement is fixed by which bonds its two knots read differently, and by the twist around the cylinder. The prediction kept
  the first and forgot the second.
- **Odd counts are where disorder can live.** With every count even, the matching graph is bipartite (N4): a liquid or frozen
  phase, never gapped. Every surviving candidate has an odd count, which is where Fendley, Moessner and Sondhi found gapped
  dimers on the triangular lattice.

Known mathematics, labelled: the gauge (Mattis; Toulouse), dimer phases (Kasteleyn; Kenyon, Okounkov and Sheffield), the
triangular-lattice dimer liquid (Fendley, Moessner and Sondhi 2002), and twisted boundary conditions as a torus sector.

## What it means for A97

No change in status. The narrowing from `WEAVE-LAWS-20261117-001` stays scoped to the 16 laws with one knot per orientation. The
mixed arrangements are open, with candidates: two 3 × 1 arrangements look disordered under the same-parity reading, whose pair
counts would then carry the information and give a ruler on the weave. A test that sets the twist explicitly would settle them.

## Limitations

- The frozen classification is the result of record, and it is unreliable for the reason given. The re-reading is post hoc.
- Widths reach 12 only. A correlation length above about 10 cannot be resolved, so "unresolved" is common (219 arrangements).
- The 3 × 1, 1 × 3 and 2 × 2 families are samples of 150 each.
- Pair counts carry the information for this class of knots (proved). Whether the candidates' counts form a ruler was not
  measured directly.

## Reproduce

```sh
cd experiments/WEAVE-MIX-20261117-001B/WEAVE-MIX-20261117-001B-E001_mixes
../../../.venv/bin/python -B run.py        # about 82 minutes on 24 cores
../../../.venv/bin/python -B readout.py    # frozen verdicts and the labelled re-reading
```

## Advisor

Consulted before the freeze. It confirmed N1 and N2, and gave the contraction picture, N4, the "only I matters" count, Q3 and
Q4, the two-gap reading, and the warning about long correlation lengths and rigid sublattices. Its "only I matters" left out the
twist, which is Q0's failure. It was not consulted after the read-out.

## Referee

Report [R1](referee-R1/report.md), 17 November 2026, by a background referee thread with fresh code and no Codex: confirmed with
fixes, no Block; "inconclusive" is the fair headline. N1 to N4 hold, and the referee's own transfer reproduces the stored spectra
to every digit. The twist diagnosis is right for every genuine difference: arrangements with the same inconsistent bonds agree to
every digit at widths with an even number of column periods and differ only at odd ones. The post hoc re-read is kept apart and
labelled. Folded in the same day, each item logged in `docs/CORRECTIONS.md` and knotlab's `HISTORY.md`:
1. **Narrowing.** The two 2 × 2 survivors are decoupled, into bands of two rows and strips of two columns. They are not
   candidates, so the four post hoc survivors are two, the 3 × 1 pair.
2. **Not a block.** The 3 × 1 pair is not a pair of gauge copies: their inconsistent bonds differ. They are genuinely gapped one
   size past (spin gap 0.314 to 0.316, energy gap 0.630 at widths 12, 15 and 18, in both period parities).
3. **Not a block.** Part of Q0's failure is not the twist: the 0.48 in 3 × 1 and the 10⁻⁸ deviations come from a doubly
   degenerate top flip-even eigenvalue, which the 10⁻⁹ multiplicity threshold counted in some members and not others.
4. **Not a block.** Q5's threshold was not frozen; the one used is stated.
5. **The referee's own erratum.** Its 2 × 2 law from `WEAVE-LAWS-R1` is not gapped (folded in separately, `198bbae02`).

The random 10% mix of signed knots from `WEAVE-LAWS-R1`, a base that is not periodic, stands as the other lead. A frozen test of the
3 × 1 pair with the twist fixed and the ruler measured is filed as the first direction, not started.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: a disordered mixed arrangement on the weave | **Status:** Inconclusive (refereed) | The frozen reading broke on the twist (2 of 6 predictions held); post hoc, one candidate pair with odd counts, gapped one size past; none with all counts even |
| Local direction: pair-count distances on the weave | Promising | The 3 × 1 pair is gapped to width 18 with decaying correlations; the random 10% mix is the other lead |
| Broader exploration: a law whose information and ruler coincide | Unexplored | Whether such an arrangement can be grown, rather than given |
| Long-term goal: G1 and G16 | No change | No arrangement shown disordered |

**Next step:** Research directions. None is selected; the first starts on the coordinator's go-ahead.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Settle the 3 × 1 pair with the twist fixed: every twist sector at even and odd widths, and its pair-count distance measured as a ruler | 2/3 | 3/3 | Freeze the pair with sectors fixed → stop at a class and a ruler reading | Alternative (filed by the coordinator, not started) |
| 2 | The full 2 × 2 and 3 × 1 families (65,536 and 4,096), read with the same-parity rule frozen in advance | 2/3 | 2/3 | A frozen re-run with the corrected rule → stop at the fraction disordered | Alternative |
| 3 | Grow a candidate: whether a state-reading rule reaches a disordered arrangement on the weave | 2/3 | 1/3 | Join the state-rules line once it reads out → stop at a rule or an obstruction | Alternative |

**Corrections:** none. Q0's failure is a failed prediction, not a correction to a recorded claim. One more "pairwise" in A97's text,
in the sense "determined by its pair counts", was fixed at this close; it belongs to the word correction already logged for
`KNOT-ORDER-20261117-001`.

**Goals:** a G1 and G16 checkpoint (no change); no goal changed.

**Assumptions:** A97 unchanged, with the mixed case open and candidates named; no new entry.

**Basket:** read; nothing taken.
