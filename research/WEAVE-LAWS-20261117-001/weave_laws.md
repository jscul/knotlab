# Which knot laws on the weave give a ruler from their counts

Epic `WEAVE-LAWS-20261117-001`, 17 November 2026, by Claude, on the coordinator's go-ahead. Goals G1 and G16; tests A97. Referee
pending. Pre-registration: [preregistration.md](preregistration.md), frozen in commit `9b4346001` at 19:41:53 UTC. The first run
crashed at once with no output (an eigenvalue routine failed on a degenerate matrix). The fix was recorded in the contract before
any read-out (`266f96fde`), and the run went from 19:44:28 to 19:47:43 UTC. Proof:
[proof.md](../../proofs/WEAVE-LAWS-20261117-001A/WEAVE-LAWS-20261117-001A-P001_law_classes/proof.md). Code:
[lawlib.py and run.py](../../experiments/WEAVE-LAWS-20261117-001B/WEAVE-LAWS-20261117-001B-E001_gaps/). Results:
[results.json](../../artifacts/WEAVE-LAWS-20261117-001B/WEAVE-LAWS-20261117-001B-E001_gaps/results.json).

## The answer

**On the weave, no tested knot law has a distance read from pair counts that both carries all its information and is a ruler.**
"Carries the information" is about the family of all bases of a law. "Ruler" is about one base, the weave's meeting pattern.
- **The pairwise laws are critical or frozen.** Only the not-all-equal class of knots is pairwise: its pair counts carry all of a
  base's information (proved, L1; the census confirms it through six distinctions). On the weave:
  - plain not-all-equal, and its signed copies whose signs agree on every pair, are gauge copies of the triangular
    antiferromagnet and critical (proved, L2; measured, gap × width 1.192, 1.216, 1.225 toward the conformal 1.238);
  - the four signed laws whose signs disagree are frozen: their rows lock (for two of them each row fixes the next exactly), so
    the states per distinction tend to 1.
  Neither kind gives a ruler.
- **The laws that give a ruler are not pairwise.** OR (some 1 on every knot) and "not exactly two ones" are disordered. The second
  is hard hexagons at activity one (L3), with 1.39549 states per distinction, Baxter's constant. Their transfer gaps settle at
  1.12 and 0.86 per row, so their counts' log grows linearly with distance. But their pair counts do not determine their bases:
  OR's first collide at six distinctions (44,521 colliding groups among 1,048,576 relations), and "not exactly two"'s at five.
  Their information needs counts of three.
- **Parity is frozen** (4 states or 1; L3).
- **The distance-two class** is frozen in two place orientations. In the third it has positive entropy and an erratic gap,
  unclassified at these widths. Its pair counts collide already at four distinctions.

In the owner's terms: on this meeting pattern, the distance that carries a law's information does not step outward from a start
without skipping, and the distances that do step outward carry only part of the information.

| Law | Class | Information pairwise? | On the weave | States per distinction (width 12) | Gap per row (widths 6, 9, 12) |
| --- | --- | --- | --- | --- | --- |
| NAE | complementary pair | yes (proved; census 16, 1,023, 97,248 injective) | critical (known; gauge copy) | 1.3857 | 0.199, 0.135, 0.102 (× width 1.19, 1.22, 1.23) |
| signed NAE, signs agreeing (place 2 odd) | complementary pair | yes | critical (L2): the same spectrum as NAE at widths 6 and 12; a doubled top eigenvalue at width 9 | 1.3857 | 0.199, 0.094, 0.102 |
| signed NAE, signs disagreeing (four laws) | complementary pair | yes | frozen: per distinction → 1 | 1.000 | — |
| OR | one excluded state | no (first collision at n = 6) | disordered | 1.76736 | 1.119, 1.119, 1.119 |
| not exactly two (hard hexagons) | three of one parity | no (first collision at n = 5) | disordered (known) | 1.39549 | 0.882, 0.859, 0.859 |
| parity | four | no (collision at n = 4) | frozen | 1 | — |
| distance-two, places 1 or 3 odd | distance-two pair | no (collision at n = 4) | frozen | 1.000 | — |
| distance-two, place 2 odd | distance-two pair | no | positive entropy, gap erratic (0.19 to 0.05): unclassified | 1.257 | 0.192, 0.257, 0.051 |

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| P1 | NAE gap × width toward 1.238, within 0.03 at 12 | held | 1.192, 1.216, 1.225 (0.013 short) |
| P2 | signed NAE with agreeing signs: critical by the frozen rule | **failed** | at widths 6 and 12 identical to NAE; at width 9 the top eigenvalue is doubled and the gap is 0.094, so "the gap falls with width" fails from 9 to 12 |
| P3 | hard hexagons disordered, per distinction within 0.001 of 1.39549 | held | 1.39549; gap 0.86, settled |
| P4 | OR disordered | held | gap 1.12, settled from width 4 |
| P5 | parity frozen | held | 1 at every width |
| P6 | the four laws with disagreeing signs frozen or ordered | held | per distinction 1 (dense spectra to width 10; the Arnoldi values 1.0002 to 1.0007 at widths 11 and 12 are in line with 1) |
| P7 | each disordered law's direct correlation decays at the gap's rate within 10% | **failed** for OR | hard hexagons 0.871 against 0.859 (1.4%); OR 1.285 against 1.119 (15%) |
| P8 | census: NAE one key per relation at 4, 5, 6; parity collides at 4; OR one key at 4 and 5, first collision at 6 | held | as predicted (OR: 16, 1,024, then 995,085 keys for 1,048,576 relations) |

6 of 8 held.

**The two failures.**
- **P2** failed on a torus sector, not a different law. L2 makes the agreeing-signs law a gauge copy up to the two twists around
  the torus. At widths 6 and 12 its spectrum equals NAE's to every digit. At width 9 the twist puts it in another sector, and its
  doubled top eigenvalue gives a smaller gap. The frozen rule asked the gap to fall at every step; on the endless weave the law is
  critical by proof.
- **P7** failed for OR. OR's correlations are tiny beyond two rows (−0.13, −0.007, 0.006, −0.001, −2 × 10⁻⁵, 6 × 10⁻⁵), and they
  change sign irregularly. A rate read from r = 6 to 12 is dominated by that oscillation. It is faster than the gap, not slower,
  so OR is disordered either way. Whether λ₁'s mode is the one a single distinction feels is left open.

**Not predicted.**
- "Not exactly two" collides at five distinctions.
- The distance-two class collides at four, has two frozen orientations, and one unclassified.
- OR knot sets give pairwise different relations through six distinctions: 2^4, 2^10 and 2^20 of them.

## What it means for A97

A97 asks whether the distance that carries a base's information is also the one that orders it. On the weave, among the twelve
laws tested, the answer is no.
- The law whose information is pairwise is critical or frozen there, so its counts set no scale.
- The laws with a scale keep part of their information in counts of three.

This is a narrowing of where the reading could hold on this meeting pattern, not a test of other patterns. A97 stays under
challenge. The open question now has two forms:
- whether a non-uniform arrangement of pairwise knots on the weave can be disordered;
- whether knots alone, on some meeting pattern, build an order among their distinctions (the owner's knots-first answer).

## What the knot picture explained

Being pairwise and having a scale pull in opposite directions here.
- **Pairwise means frustrated or frozen.** A knot is pairwise only if it excludes a complementary pair. On the weave that makes
  every knot a frustrated triangle. With agreeing signs, the frustration is the triangular antiferromagnet's, which is critical.
  With disagreeing signs, no consistent bond signs exist, and the rows lock.
- **Scale needs counts of three.** The knots that give a scale exclude states of one parity, so they are not complementary pairs.
  Their information then lives partly in counts of three.

Known mathematics, labelled:
- the triangular antiferromagnet and its conformal data (Wannier; Stephenson; Blöte and Hilhorst; Nienhuis, Hilhorst and Blöte;
  Cardy);
- hard hexagons (Baxter);
- frustration and gauge (Mattis; Toulouse; Fradkin, Huberman and Shenker);
- Fourier degree.

Local:
- the classification of the 34 knots by degree;
- the census;
- OR's and the distance-two class's behaviour on the weave;
- the frozen rows of the disagreeing-sign laws.

## Limitations

- Uniform laws and two up/down mixes only, at widths up to 12, on one meeting pattern.
- The Arnoldi values at widths 11 and 12 for frozen laws are slightly above 1, against exact 1 from dense spectra below.
- P7's rate for OR is read from two noisy points.
- The distance-two orientation with positive entropy is unclassified at these widths.
- "Ruler" is read through the transfer gap along one axis; no outline or roundness was measured (B195).

## Reproduce

```sh
.venv/bin/python -B proofs/WEAVE-LAWS-20261117-001A/WEAVE-LAWS-20261117-001A-P001_law_classes/check.py
.venv/bin/python -B experiments/WEAVE-LAWS-20261117-001B/WEAVE-LAWS-20261117-001B-E001_gaps/run.py
```

## Advisor

Consulted once before the freeze. It:
- corrected L2: the draft claimed every not-all-equal-class weave is critical, and assignments with disagreeing signs are not
  covered;
- gave the three-way classification and the direct-correlation check;
- gave the conformal value 1.238 and the census predictions (OR's Pasch collision at six, parity at four).

Not consulted after the read-out.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: which knot laws on the weave give a ruler | **Status:** Successful (referee pending) | Pairwise laws: critical (agreeing signs) or frozen (disagreeing); ruler laws (OR, hard hexagons) not pairwise; 6 of 8 held |
| Local direction: one distance that carries the information and steps outward | Unresolved on the weave | Not among uniform laws; non-uniform pairwise arrangements untested |
| Broader exploration: which meeting patterns and laws do both | Unexplored | Off-critical pairwise patterns exist elsewhere (the chain grid of `DISTANCE-DIM-20261117-001`) |
| Long-term goal: G1 and G16 | Obstruction learned | On the weave, information and order sit in different laws' counts |

**Next step:** Research directions. None is selected; the first starts on the coordinator's go-ahead.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Can a non-uniform arrangement of pairwise knots on the weave be disordered? Random and periodic mixes of the four signed not-all-equal knots per triangle | 2/3, the premise's positive case on the weave if yes | 3/3, the same transfer code with position-dependent laws | Freeze a classification of periodic mixes up to period 3 → stop at the first disordered one, or at a proof that mixed signs lock rows | Alternative |
| 2 | Can knots alone build an order among their distinctions (the owner's knots-first answer), for example through distinctions that knots force or settle? | 3/3 | 1/3 | Look for knot patterns whose settled distinctions carry exact betweenness → stop at a pattern or an obstruction | Alternative |
| 3 | B195, outlines of the disordered laws' rulers (OR, hard hexagons) | 1/3 | 3/3 | Queued for its own owner | Queued elsewhere |

**Corrections:** none.

**Goals:** a G1 and G16 checkpoint (obstruction learned); no goal changed.

**Assumptions:** A97 stays Under challenge, narrowed on the weave; no new entry.

**Basket:** read; B195 is the outline question and is left to its owner.
