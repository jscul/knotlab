# Referee report WEAVE-MIX-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block. "Inconclusive" is the fair headline.**
- **What holds.**
  - N1 to N4 are correct.
  - The referee's own transfer, split by the global flip, reproduces the stored spectra to every digit.
  - The twist diagnosis is right in substance. Every genuine difference between arrangements with the same inconsistent set appears only at widths with an odd number of
    column periods. One part of Q0's failure is not the twist: 3 × 1's "differences by 0.48" at width 6 come from a doubly degenerate
    top eigenvalue split by the 10⁻⁹ threshold.
  - The post hoc re-read is kept apart from the frozen verdicts, and labelled as post hoc.
- **What changes, about the four post hoc survivors.**
  - **The two 3 × 1 arrangements are genuinely gapped, one size past.** At widths 15 and 18 the spin gap is 0.314 to 0.316 and the
    energy gap 0.630, the same as at 12 in both period parities. Their correlations along the transfer axis decay.
    - But they are not gauge copies: their inconsistent sets differ. So "the same spectra (they look like gauge copies)" needs
      correcting. **Not a block.**
  - **The two 2 × 2 survivors are decoupled, not two-way disordered.**
    - One falls into independent bands of rows: its correlation along the transfer axis is exactly 0 from two rows on.
    - The other falls into independent strips of two columns: its states per distinction are 1.246504702770927 at every width from
      4 to 16, and its correlation around the cylinder is exactly 0 beyond one column.

    Neither is a candidate. **Narrowing.**
  - **The referee's own 2 × 2 law** (from `WEAVE-LAWS-R1`) is not gapped. Its spin gap falls to 0.143 at width 14 and 0.132 at 16.
    The referee's earlier "looks disordered" is withdrawn: a correction to the referee's report, erratum added there.
    **Correction (referee's own).**

## What holds

- **N1 to N4 (proved).**
  - **N1.** Each not-all-equal-class knot's three signs multiply to −1: for p = 000 all three are −1; otherwise one is −1 and two
    are +1. So the number of broken bonds is odd. Three broken bonds is exactly the excluded pair.
  - **N2** is the Moessner–Sondhi mapping, with the inconsistent bonds subdivided.
  - **N3** is the count of (knot, broken bond) pairs.
  - **N4.** The hexagon around a distinction has length 6 plus its number of inconsistent bonds, and a planar graph is bipartite
    exactly when every face is even.
- **The spectra reproduce.**
  - **The transfer.** It is the referee's strip transfer from `WEAVE-LAWS-R1`, multiplied over one row period. It is split into
    flip-even and flip-odd sectors.
  - **Above width 12.** A transfer applied one distinction at a time, with Arnoldi on symmetrised vectors. It equals the dense
    sectors at widths 6 and 12 to every digit.
  - **The agreement.** Survivor 0 at widths 6 and 12, the referee's 2 × 2 law at 6 and 12, and the other survivors' stored values
    all agree with the study to the last digit given.
- **The frozen record is kept.** The predictions table gives the frozen verdicts: Q0, Q1, Q3 and Q5 failed, Q2 held, Q4 "held as
  frozen". The re-reading is in its own paragraph and marked post hoc. `readout.py` separates the two parts, and the note's Position
  says "Inconclusive".
  - **Q5's threshold** was not frozen. The one used is stated, and its failures were critical on the re-reading. That is a gap in
    the protocol, carried honestly. **Not a block.**

## 1. The twist diagnosis (the owner's question)

The referee recomputed every group of arrangements that share an inconsistent set, in the 2 × 1 and 3 × 1 families, at widths 4,
6, 8 and 10 (2 × 1) and 6, 9 and 12 (3 × 1) (`referee_weavemix_twist.json`).
- **2 × 1.** 15 groups differ somewhere. 14 of them agree to every digit at the widths with an even number of column periods (4 and
  8) and differ at the odd ones (6 and 10). For example, plain NAE's group reads 0.1713, 0.2081 at widths 4 and 8 for all eight
  members, and 0.1987 or 0.1167 at width 6. The 15th group is frozen, with states per distinction 1, and differs only by
  numerical noise of order 10⁻⁵ at width 10.
- **3 × 1.** Every genuine difference is at width 9, an odd count; for example 0.1476 against 0.0997, equal at 6 and 12. The three
  groups flagged at a strict tolerance have members equal to six digits at every width: frozen or degenerate spectra.
- **What Q0's 3 × 1 deviation of 0.48 at width 6 is.** It is not a twist. Width 6 holds two periods.
  - The group ([e1 at 2], [e2 at 1]) has energy gaps of 9 × 10⁻⁹, 0.483 and 1.9 × 10⁻⁸ in its three members.
  - The top flip-even eigenvalue is doubly degenerate, and the 10⁻⁹ multiplicity threshold counts the partner in some members and
    skips it in others.
  - The 1 × 1 and 1 × 2 deviations of 10⁻⁸ are the same noise.
- **So.** Q0's genuine failures are 2 × 1's 14 groups, all by the twist. The rest of the deviations are a threshold artifact that a
  tolerance would have absorbed. The owner's single cause holds for the genuine part.

The mechanism is the one `WEAVE-LAWS-R1` found for the agreeing-signs law.
- A gauge relating two arrangements with the same inconsistent set may need two column periods. So a cylinder with an odd number
  of periods carries a seam.
- The frozen rule compared width 12 with 9 (or 10), whose number of periods has the other parity.
- For the triangular antiferromagnet, the twisted gap at width 9 (0.094) lies within 10% of the untwisted gap at 12 (0.102). That
  is enough for the rule to read "disordered". So Q1's failure, gauge copies of the critical law read as disordered, is explained.

Comparing widths with the same parity of periods (12 against 6, or against 8 for column period 2) is the right repair. It is post
hoc, and labelled so.

## 2. The four post hoc survivors (the owner's questions)

All values are the referee's (`referee_weavemix_gaps.json`, `_corr.json`, `_around.json`).

| Survivor | Widths read | Spin gap | Energy gap | States per distinction | Correlation along / around | Reading |
| --- | --- | --- | --- | --- | --- | --- |
| 3 × 1, survivor 0 | 6, 9, 12, 15, 18 | 0.342, 0.309, 0.317, 0.314, 0.316 | 0.658, 0.631, 0.630, 0.631, 0.630 | 1.2631 | 0.30 → 0.02 over 7 rows; about 0.08 at the farthest column (width 12) | gapped |
| 3 × 1, survivor 1 | 6, 9, 12, 15, 18 | 0.342, 0.323, 0.317, 0.316, 0.316 | 0.658, 0.633, 0.630, 0.630, 0.630 | 1.2631 | the same along; differs around | gapped |
| 2 × 2, survivor 2 | 4 to 16 | 9 to 10, or infinite | about 9 | 1.2465 | exactly 0 along from 2 rows; 0.65, 0.30, 0.25, 0.20, 0.15, 0.10 around | independent row bands |
| 2 × 2, survivor 3 | 4 to 16 | 0.4011 at every width | 0.8023 at every width | 1.246504702770927 at every width | decays along; exactly 0 around beyond one column | independent column strips |

- **The 3 × 1 pair is genuinely gapped.**
  - **The gaps settle.** One size past the study's width 12, both gaps settle to four digits, at 12, 15 and 18, in both parities of
    the period count. The two arrangements agree to ten digits at 18.
  - **Correlations decay.** Along the transfer axis they halve about every two rows.
  - **Around the cylinder** the width-12 correlation at the farthest column is still about 0.08. That fits a correlation length near
    three rows, but it was not followed to larger widths.
  - **They are not gauge copies.** Their inconsistent sets differ:
    - survivor 0: e1 at 1, e2 at 0, e2 at 2, e3 at 0;
    - survivor 1: e1 at 0, e2 at 0, e2 at 2, e3 at 1.

    Their correlations of distinction 0 around the cylinder differ in size (0.58 against 0.12 at one column), which no gauge does.
    Their equal spectra at even period counts suggest a symmetry of the weave relating them. So they are probably one candidate up
    to symmetry, not two.
  - **The best candidate.** On these readings, this arrangement is the best candidate yet for the premise's positive case on the
    weave: a periodic arrangement of knots whose pair counts carry the base, with a finite correlation length. It remains post hoc,
    and its pair-count ruler was not measured.
- **Survivor 2 decouples into bands.** Its gaps near 9, infinite at widths 14 and 16, and its zero correlation along the transfer
  axis from two rows on mean each two-row band is independent of the next. Within a band, the correlation around the cylinder
  falls linearly, as on a line. It is a stack of independent one-way strips, not a two-way disordered arrangement.
- **Survivor 3 decouples into strips.** Its states per distinction are identical to 15 digits at every width from 4 to 16, and its
  correlation around the cylinder is 0 to rounding beyond one column. The base is a product of independent two-column strips along
  the transfer axis. Its gap is a one-way chain's. The owner's guess ("decoupled rows") is right in kind; the decoupling is into
  column strips.
- **So of the four survivors, two are decoupled.** The note's "four arrangements still look disordered" should say "two, a 3 × 1
  pair related by a symmetry; the 2 × 2 two decouple into independent strips".

## 3. The referee's own 2 × 2 law, and the WEAVE-LAWS probes (the coordinator's question; correction)

- **The 2 × 2 law** has p3 on one up knot per 2 × 2 block. Its spin gap per row, at widths 4 to 16, is ∞, 0.315, 0.257, 0.240,
  0.233, 0.143 and 0.132. At width 14 its top flip-even pair is nearly degenerate (392.0 and 387.7), an energy gap of 0.005.
  - The values at 14 and 16 were rechecked with eight eigenvalues per sector.
  - The gap halves from 12 to 16, so the law is not gapped at these widths.
  - `WEAVE-LAWS-R1`'s "already looks disordered at widths up to 12" read a gap that had not settled.
  - **What was done.** The referee has added an erratum to its own report and withdraws the claim.
  - **What is needed.** A97's text, "one law on a 2 × 2 cell, that look disordered", needs that part removed, and the correction
    logged.
- **The random mix** (NAE with 10% signed knots, Lyapunov gap 0.20 at widths 9 to 15) is a different object, a base that is not
  periodic. WEAVE-MIX tested only periodic arrangements, so it neither confirms nor refutes the random-mix probe.
- **How the two studies now sit together.** The random mix and the 3 × 1 periodic pair are the two positive leads, both read through
  transfer gaps only.

## 4. Smaller points (Not a block)

- **The study's Q0 count.** By widths 4 to 10, the referee finds 15 groups in 2 × 1 and 11 in 3 × 1 that differ at a strict tolerance. Setting aside the 1 + 3 whose members agree to six digits, every difference is at an odd period count.
- **"Unresolved" is common (219).** This is fair at widths 12 and below. The 3 × 1 pair shows that widths 15 and 18 are cheap with a
  transfer applied one distinction at a time.

## Fixes for the thread (listed for the owner, not folded in)

1. **The survivors.**
   - Count two candidates (the 3 × 1 pair, probably one up to symmetry), not four.
   - Name the 2 × 2 two as decoupled: independent row bands; independent column strips.
   - Drop "they look like gauge copies": the 3 × 1 pair's inconsistent sets differ.

   **Narrowing.**
2. **The 3 × 1 pair one size past.** Record that its gaps hold at widths 15 and 18 (0.316 and 0.630). That supports the candidate.
   It is still post hoc and needs the frozen re-test the note proposes. **Not a block.**
3. **The referee's 2 × 2 law.** Record it as not gapped at widths 14 and 16. Remove "one law on a 2 × 2 cell, that look disordered"
   from A97's text, and log the correction to `WEAVE-LAWS-R1`. **Correction (the referee's own).**
4. **The twist.** Record that Q0's 3 × 1 deviation (0.48) and the 1 × 1 and 1 × 2 ones (10⁻⁸) are numerical: a degenerate top eigenvalue at the
   multiplicity threshold. Only 2 × 1's 14 groups are the twist. **Not a block.**

## How the work was split

- **The referee:**
  - read the note, the pre-registration, the proof, `mixlib.py`, `run.py`, `readout.py`, the results and the read-out;
  - checked N1 to N4 by hand;
  - wrote its own transfer split by the flip, a transfer applied one distinction at a time for widths to 18, gauge-group and
    correlation checks.
- **The study's code** was not run.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_weavemix.py`:**
  - parts `twist`, `gaps`, `corr` and `around`, with their `.json` outputs;
  - `gaps` holds the values behind the `WEAVE-LAWS-R1` erratum.

Reproduce, from `research/WEAVE-MIX-20261117-001/referee-R1/`:

```sh
for p in twist gaps corr around; do ../../../.venv/bin/python -B referee_weavemix.py $p > referee_weavemix_$p.json; done
```
