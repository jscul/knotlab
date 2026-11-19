# Do pair and three-way distances force the allowed states of what the law grows? Pre-registration

Epic `THREE-RIGID-20261119-001` (`PROVE-B-20261119-001#1`, the coordinator's go-ahead; A97, A108, G1), 2026-11-19. Frozen before
the run. The canonical K1–K3 test is unchanged.

## The question

Claim B is false (PROVE-B): pair distances plus the growing end do not carry one round. But every failing swap breaks three-way
readings, the smallest bond holding three given distinctions, less one. In PROVE-B's sample, none of 164,052 reading-keeping,
equation-breaking symmetries keeps them.

**R3 (three-way rigidity) on reached stages:** every symmetry of the bond-distance table that keeps every three-way reading
carries the equation space onto itself. With Claim B\* (EXTEND-ROUND, proved) that gives pair plus three-way distances plus the
growing end carrying what grows, every round. Hunt a counterexample first; then try to prove R3.

## Prior work in the program

`python3 -B scripts/track.py objects "three-way rigidity table symmetry keeping three-way readings carries the equations" --until 2026-11-19 --exclude THREE-RIGID-20261119-001`

- `PROVE-B-20261119-001`: Claim B refuted; the three-way observation.
- `TRIPLE-GROWN-20261119-001`: three-way readings separate every collision found; three-distinction bonds never span the
  equations there.
- `THREE-WAY-20261119-001`: the readings.

## A lemma (the advisor's, recorded)

**Lemma.** If the bonds of at most three distinctions span the equations, any symmetry keeping pair and three-way readings carries
the equations.

*Proof sketch.*
- A triple reads 2 exactly when it is itself a bond, and a pair reads 1 exactly when it is a bond.
- So the symmetry maps the small bonds onto small bonds, and a spanning set onto a spanning set.

TRIPLE-GROWN found the three-distinction bonds never span on its pairs, so the lemma will rarely settle a stage here. The hunt
records, for each stage, whether it is spanned (settled) or has a deficit (where a counterexample must live).

## Method

`rigid_job.py` on the shared runner. Stages of round ≥ 1 with at most 14 junctions come from three populations:
- **census:** every census start, at most five knots, rounds 1 to 8;
- **small:** PROVE-B's 35,735 starts of 3 or 4 knots sharing up to 4 (or 3) distinctions, rounds 1 to 3;
- **meet7:** every legal meet-once 7-junction start (417,297), round 1. This is where Codex's meet-once failure lives.

For each stage, every table symmetry is taken, one per holder-class coset, holder-breaking ones included. VF2 is restricted by
each distinction's multiset of three-way readings, which is sound; the cap is 20,000. Each symmetry is tested for keeping every
three-way reading and for carrying the equations. A three-way-keeping one that breaks the equations is a counterexample to R3. If
it also keeps the round's reading, its extension is checked (Claim B3). `control.py` runs Proposition X and Codex's two cases.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| Q0 | Control: in the three known failures every reading-keeping, equation-breaking symmetry breaks three-way readings (seen) | one keeps them |
| Q1 | No counterexample to R3 in any of the three populations (mine 85%; the advisor's 85% with four-place generators present) | one |
| Q2 | Hence no Claim B3 failure (pair plus three-way plus reading) | one |

Reported: stages spanned or with a deficit, symmetries enumerated, capped and late.

## Advisor

Fable 5.2 before the freeze ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md)). Taken:
- the lemma;
- the rank-deficit discriminator;
- the warning that a spanned population would make the hunt a replay rather than evidence.

Its bets: R3 on this hunt 85%, with four-place junctions present; for all reached stages 60%; for all connected arrangements 20%.
It expects a counterexample in graphs where every bond has four or more distinctions.

## Runs and stop rule

`rigid_job.py` (663 cases, 8 workers, 16 GB cap) and `control.py`, once each; then stop.
