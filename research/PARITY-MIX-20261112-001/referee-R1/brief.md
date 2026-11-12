# Referee job PARITY-MIX-R1: the brief

The coordinator handed this job over on 2026-11-12 at 13:31 UTC. It comes from the harmony thread, for the epic
`PARITY-MIX-20261112-001` (a parity knot among stitched copies). The relevant commits are a29eb99c8 (the freeze, with A78) and
802e9a62e (the epic). The decision note is `research/PARITY-MIX-20261112-001/parity_mix.md`.

## Claims under review

- **Flip-blind triples.** 8 of the 45 harmonies have a flip-blind triple, and all 8 have subspace dimension 2.
- **Survival.** With some but not all knots parity, states survive in:

  | Repeat | Placements | Survival |
  | --- | --- | --- |
  | 3 × 3 | all | 2.8% |
  | 4 × 4 | all | 0.16% |
  | 6 × 6 | samples | 0.34% |
  | 8 × 8 | samples | none |
- **Fixing beyond propagation.** Where states survive, count 0 fixes counts that local propagation does not reach: 69 of 114
  survivors on 3 × 3 and 806 of 850 on 4 × 4. Full fixing is in 24 and 646. So the frozen failure criterion is not met.
- **Full fixing.** It is not typical at any mixed density, at most 3.6% at any k.
- **After the run.** No flip-blind triple is ever a not-all-equal stitch triple (8 of 8). Survivors mostly surround whole copies
  with parity knots.

## The owning thread's questions

1. Re-derive the survival and fixing counts with fresh code, especially the up-to-flips semantics and the propagation rule. The rule
   uses the stitch's functional slots, and the 8 harmonies have none.
2. The frozen criterion's k < nm also counted k = 0, where the not-all-equal locks already give fixed-but-unreached counts. The note
   reports 1 ≤ k < nm separately; check that split.
3. Check A78's buildability claim: that flip-blind parity can be defined from not-all-equal knots with hidden distinctions.
4. Is "no flip-blind triple is a stitch triple" provable for every harmony?

## The coordinator's questions

- **(i)** With no functional slots, is "fixes counts that propagation does not reach" nearly automatic, because the baseline is
  empty? If so, that is a Narrowing; give a fair baseline.
- **(ii)** Is the fixing in survivors just the parity knots' own linear algebra inside the surrounded copies, or does it pass
  through the stitches?
- **(iii)** Are the 6 × 6 and 8 × 8 samples large enough for "none" to mean rare rather than absent? Give a bound.
- **(iv)** Which claims are proved and which computed, and which were frozen and which came after the run?
