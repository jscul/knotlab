# Which knot laws on the weave give a ruler from their counts

Epic `WEAVE-LAWS-20261117-001`, 17 November 2026, by Claude, on the coordinator's go-ahead. Goals G1 and G16; tests A97.
Refereed: report [R1](referee-R1/report.md), confirmed with fixes, no Block, folded in on 17 November (see Referee). Pre-registration: [preregistration.md](preregistration.md), frozen in commit `9b4346001` at 19:41:53 UTC. The first run
crashed at once with no output (an eigenvalue routine failed on a degenerate matrix). The fix was recorded in the contract before
any read-out (`266f96fde`; the contract's amendment time 19:47Z should read 19:44Z), and the run went from 19:44:28 to 19:47:43 UTC. Proof:
[proof.md](../../proofs/WEAVE-LAWS-20261117-001A/WEAVE-LAWS-20261117-001A-P001_law_classes/proof.md). Code:
[lawlib.py and run.py](../../experiments/WEAVE-LAWS-20261117-001B/WEAVE-LAWS-20261117-001B-E001_gaps/). Results:
[results.json](../../artifacts/WEAVE-LAWS-20261117-001B/WEAVE-LAWS-20261117-001B-E001_gaps/results.json).

## The answer

**On the weave, no tested knot law has a distance read from pair counts that both carries all its information and is a ruler.**
"Carries the information" is about the family of all bases of a law. "Ruler" is about one base, the weave's meeting pattern.
- **The laws determined by their pair counts that put one knot on every up knot and one on every down knot are critical or
  frozen.** *Scoped after the
  referee: all 16 such laws are, but a sparse mix of signed knots looks disordered (see Referee). The referee's 2 × 2 law, once
  said to look disordered too, was withdrawn by the referee on 17 November: one size past, its gap keeps falling.* Only the not-all-equal class of knots gives bases determined by their pair counts: they carry all of a
  base's information (proved, L1; the census confirms it through six distinctions). On the weave:
  - plain not-all-equal, and its signed copies whose signs agree on every pair, are gauge copies of the triangular
    antiferromagnet and critical (proved, L2; measured, gap × width 1.192, 1.216, 1.225 toward the conformal 1.238);
  - the signed laws whose signs disagree are frozen: their live transfer is a union of single cycles, with spectral radius exactly
    1, except NAE up with place 1 odd down, which has exactly 2 on two live rows (1.0595 per distinction at width 12, and no state
    at odd widths); all tend to 1 per distinction (the referee's exact test; the Arnoldi values above 1 were artifacts).
  Neither kind gives a ruler.
- **The laws that give a ruler are not determined by their pair counts.** OR (some 1 on every knot) and "not exactly two ones" are disordered. The second
  is hard hexagons at activity one (L3), with 1.39549 states per distinction, Baxter's constant. Their transfer gaps settle at
  1.12 and 0.86 per row, so their counts' log grows linearly with distance. But their pair counts do not determine their bases:
  OR's first collide at six distinctions (44,521 colliding groups among 1,048,576 relations), and "not exactly two"'s at five.
  Their information needs counts of three. Their counts' log grows linearly only in envelope: the gap's mode is a complex pair
  at phase 2π/3, so |C(r)| oscillates with period three (referee).
- **Parity is frozen** (4 states or 1; L3).
- **The distance-two class** is frozen in two place orientations. In the third it has positive entropy and an erratic gap,
  unclassified at these widths. Its pair counts collide already at four distinctions.

In the owner's terms: on this meeting pattern, the distance that carries a law's information does not step outward from a start
without skipping, and the distances that do step outward carry only part of the information.

| Law | Class | Determined by pair counts? | On the weave | States per distinction (width 12) | Gap per row (widths 6, 9, 12) |
| --- | --- | --- | --- | --- | --- |
| NAE | complementary pair | yes (proved; census 16, 1,023, 97,248 injective) | critical (known; gauge copy) | 1.3857 | 0.199, 0.135, 0.102 (× width 1.19, 1.22, 1.23) |
| signed NAE, signs agreeing (place 2 odd) | complementary pair | yes | critical (L2): the same spectrum as NAE at every even width, twisted at every odd width (gauge i mod 2) | 1.3857 | 0.199, 0.094, 0.102 |
| signed NAE, signs disagreeing (four laws) | complementary pair | yes | frozen: per distinction → 1 | 1.000 (NAE up, place 1 odd down: 1.0595, exact 2 on two rows) | — |
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
- The law whose bases are determined by their pair counts is critical or frozen there, so its counts set no scale.
- The laws with a scale keep part of their information in counts of three.

This is a narrowing of where the reading could hold on this meeting pattern, not a test of other patterns. A97 stays under
challenge. The open question now has two forms:
- whether a non-uniform arrangement of not-all-equal-class knots on the weave can be disordered;
- whether knots alone, on some meeting pattern, build an order among their distinctions (the owner's knots-first answer).

## What the knot picture explained

Being determined by pair counts and having a scale pull in opposite directions here.
- **Determined by pair counts means frustrated or frozen.** A knot's bases are determined by pair counts only if it excludes a
  complementary pair. On the weave that makes
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

## Referee

Report [R1](referee-R1/report.md), 17 November 2026, by a background referee thread with fresh code and no Codex: confirmed with
fixes, no Block. L1 to L3 hold; every frozen number recomputes; the amendment changed only the numerical method. Folded in the same
day, each item logged in `docs/CORRECTIONS.md` and knotlab's `HISTORY.md`:
1. **Narrowing.** "The pairwise laws are critical or frozen" holds for all 16 laws with one not-all-equal-class knot on every up
   knot and one on every down knot, 10 of which were untested here. It does not hold beyond them, on the referee's probes:
   - NAE with a random 10% of signed knots levels off at a gap near 0.20 per row from width 9 to 15, with 1.30 states per
     distinction, over 5,000 rows;
   - one periodic law, p3 at one up knot in every 2 × 2 cell, has gaps 0.257, 0.240 and 0.233 at widths 8, 10 and 12.
     *Withdrawn by the referee (17 November, during `WEAVE-MIX-R1`): at widths 14 and 16 the spin gap falls to 0.143 and 0.132,
     so this law is unresolved and looks critical or long-range, not disordered.*
   The random mix looks disordered with every knot in the not-all-equal class. They are probes: Lyapunov exponents, few seeds and small widths. An endless
   independent random mix may be contradictory somewhere; the periodic law avoids that. So "obstruction learned", A97's narrowing
   and the goals checkpoint hold for one-knot-per-orientation laws only. `WEAVE-MIX-20261117-001` is the test.
2. **Narrowing.** The gap's mode is a complex pair at phase 2π/3, the mode a single distinction feels. P7's miss is a period-three
   oscillation, which makes |C(r)| non-monotone for OR and hard hexagons. "The distances that do step outward" holds in envelope
   only.
3. **Not a block.** The disagreeing-sign laws' readings now rest on the referee's exact test: every strongly connected part of the
   live transfer is a single cycle, so the spectral radius is 1. The exception is NAE up with place 1 odd down: 2 on two live rows,
   1.0595 per distinction at width 12, and no state at odd widths. "Each row fixes the next exactly" was wrong: on a torus every
   row equals the next.
4. **Not a block.** P2's twist is at every odd width (gauge i mod 2), not only at 9.
5. **Not a block.** Small slips:
   - L1's count is 4 knots, not 8;
   - L2's proof should say "violated", not "satisfied";
   - `check.py`'s docstring claimed a gauge search it does not do;
   - `run.py`'s docstring is stale;
   - the amendment's time is 19:44Z.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: which knot laws on the weave give a ruler | **Status:** Successful (refereed) | Laws determined by pair counts: critical (agreeing signs) or frozen (disagreeing); ruler laws (OR, hard hexagons) not; 6 of 8 held |
| Local direction: one distance that carries the information and steps outward | Promising | Not among one-knot-per-orientation laws; the referee's probes find candidates among mixed arrangements |
| Broader exploration: which meeting patterns and laws do both | Unexplored | Off-critical not-all-equal-class patterns exist elsewhere (the chain grid of `DISTANCE-DIM-20261117-001`) |
| Long-term goal: G1 and G16 | Obstruction learned, for one-knot-per-orientation laws | For such laws, information and order sit in different laws' counts; a sparse mix and a 2 × 2 periodic law look disordered (referee), which `WEAVE-MIX-20261117-001` tests |

**Next step:** Research directions. None is selected; the first starts on the coordinator's go-ahead.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Can a non-uniform arrangement of not-all-equal-class knots on the weave be disordered? Random and periodic mixes of the four signed not-all-equal knots per triangle | 2/3, the premise's positive case on the weave if yes | 3/3, the same transfer code with position-dependent laws | Freeze a classification of periodic mixes up to period 3 → stop at the first disordered one, or at a proof that mixed signs lock rows | Alternative |
| 2 | Can knots alone build an order among their distinctions (the owner's knots-first answer), for example through distinctions that knots force or settle? | 3/3 | 1/3 | Look for knot patterns whose settled distinctions carry exact betweenness → stop at a pattern or an obstruction | Alternative |
| 3 | B195, outlines of the disordered laws' rulers (OR, hard hexagons) | 1/3 | 3/3 | Queued for its own owner | Queued elsewhere |

**Corrections:** none.

**Goals:** a G1 and G16 checkpoint (obstruction learned); no goal changed.

**Assumptions:** A97 stays Under challenge, narrowed on the weave; no new entry.

**Basket:** read; B195 is the outline question and is left to its owner.
