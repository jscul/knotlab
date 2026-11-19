# Can the distances version of the one-round extension be proved? Pre-registration

Epic `PROVE-B-20261119-001` (`HUNT-SHORTEN-20261119-001#1`, the coordinator's go-ahead; A97, A108, G1), 2026-11-19. Frozen before
the hunt. The canonical K1–K3 test is unchanged.

## The question

Claim B: a table isometry that keeps what the round reads extends to an isometry of the next round's tables. It held on 1,746,752
census self-symmetries (holder-breaking ones included) and 36,060 carried-pair matchings, but is unproved. Prove it in the form a
proof reaches. Say what stays unproved. Hunt the smallest configuration where the proof stalls.

## Prior work in the program

`python3 -B scripts/track.py objects "prove the table version of the one-round extension split formula offshoots counterexample" --until 2026-11-19 --exclude PROVE-B-20261119-001`

- `HUNT-SHORTEN-20261119-001`: bridging joins made by hand, the self-pairs (the direct predecessor).
- `EXTEND-ROUND-20261119-001`: Lemma A, Claim B\*, Claim B.
- `CREATED-PAIR-20261119-001`: the growing end.
- `PLUS-ONE-20261118-001`: how offshoot chains combine under the same law (a relative: what offshoots do in a round).
Also `PARENT-RULE-20261119-001` (Theorems 1 to 3).

## What the proof reaches (ticket A, [proof.md](../../proofs/PROVE-B-20261119-001A/PROVE-B-20261119-001A-P001_split/proof.md))

- **Lemma C, the split formula (proved).** Bonds of the next junction graph are families of disjoint, non-adjacent old bonds,
  glued by new junctions. A bond's size is the old cut's size plus, for each new junction inside, f + (parents outside) −
  (parents inside).
- **Lemma O (proved).** Offshoots never change the least bond through two old distinctions. Rounds of offshoots only extend any
  isometry that keeps the loose distinctions per live junction. HUNT-SHORTEN's H1 becomes a theorem.
- **Proposition X (the advisor's construction, checked before the freeze).** A 7-junction connected arrangement has a table
  symmetry that swaps two distinctions of one junction lying in different holder classes. It keeps the round's reading and does
  not extend: after the law's round, T′(p₁, p₂) = 2 against T′(q₁, p₂) = 3. **So Claim B is false for arrangements in general.**
  The arrangement is a start whose live junctions share two distinctions with a parent, which no reached stage allows. Claim B
  for reached stages stays open.
- **The stall.** For reached stages a proof needs a tie lemma (proof, Section 4), and that lemma is not proved. Proposition X
  names the configuration to hunt:
  - a junction with no loose distinction whose distinctions split evenly between two holders;
  - a holder-class-breaking table symmetry;
  - a tie between its star and a bond holding a full parent set with k > f.
  In reached stages the split needs start knots that share two or more distinctions.

## The hunt (ticket B)

`reached_job.py` on the shared runner:
- **Starts.** Every start of 3 knots (shared multiplicities 1 to 4) or 4 knots (1 to 3), with 0 to 3 loose distinctions per knot,
  legal, one per orbit: 35,735 starts.
- **Rounds.** Each is grown by the census's law for up to three rounds, while stages keep at most 14 junctions.
- **The test.** For every open stage of round ≥ 1, every table symmetry is taken, one per coset of holder-class permutations,
  holder-breaking ones included, enforced inside VF2 (cap 20,000). Those that carry the equations are skipped. For those that keep
  the reading, the extension is checked entry by entry on the next stage.

`control.py`: Proposition X's arrangement through the same test.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| P0 | Control: every reading-keeping, equation-breaking symmetry of Proposition X's arrangement fails to extend (seen: 32 of 32) | one extends |
| P1 | No counterexample to Claim B in any reached stage of the hunt (mine 65%; the advisor's 60% for all reached stages) | one fails |

Reported:
- the numbers of stages and symmetries, carrying, keeping and breaking holder classes;
- capped and late stages;
- the smallest failing stage if P1 fails.

## Advisor

Fable 5.2 ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md)) was consulted on the proof itself.
- **What it confirmed.** Lemma C, with the refinement to families of bonds, and Lemma O with offshoot stripping.
- **What it built.** Proposition X.
- **What it named.** The tie lemma, and the reached-stage hunt target. It asked that the double edges between a live junction and
  its parent be replaced by start-knot sharing.
- **Its bets.** Claim B true for all reached stages 60%, for all connected arrangements 10%.
- **Design-stage check (disclosed).** Proposition X was verified by computation before this freeze, and the hunt was
  smoke-tested on its smallest case (261 starts, 804 symmetries, all extending).

## Runs and stop rule

`reached_job.py` (312 cases, 8 workers, 16G cap), then `control.py`. One run each; then stop.
