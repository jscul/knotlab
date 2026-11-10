# Pre-registration: weakly aperiodic laws under Leibniz's rule

Epic `WEAK-APER-20261110-001` (`LEIBNIZ-BOARDS-20261110-001` direction 2, G1; program topology, group `spacing`), written on
2026-11-10 before any run, at the owner's go-ahead ("Yes, let's do that").

## The question

Under Leibniz's rule, the dichotomy W says that an infinite board always brings the tree. It holds for every law with a finite board
that uses a free choice (Lemma A) and for every deterministic law. The only place it can fail is a law with free choices but no
usable finite board, and above all a weakly aperiodic law, which has solutions but no finite board at all. Do such laws still have a
solution with trivial stabilizer?

## Known before the run (disclosed)

- **The horofunction law is weakly aperiodic.** Its law is {(1, 0, 3)}: one neighbour one level lower, three one level higher.
  Counting edges between levels on a finite board gives three upward ends per place against one downward, so no finite board
  exists. Busemann functions of ends fixed by no nontrivial element are free solutions, so W holds for it.
- **The controls.** The horofunction law classifies as WA-L2, the empty law as E, the full law as A.

## Frozen

- **Ticket B's census.** Its family (the 32,768 level laws on three values), classes, certificates and predictions are in its contract
  (`experiments/WEAK-APER-20261110-001B/WEAK-APER-20261110-001B-E001_level_laws_on_three_values/contract.json`). C1: no law is
  undecided. C2: the horofunction law is WA-L2 without L1.
- **Ticket A's targets.** The balance criterion, Lemma A″, L1, L2, and W in general or its gap.
- **Stop rule, one epic.** The census runs once. Every undecided law is examined by hand, and W is proved, refuted, or left with its
  gap stated.
