# The node reading's two exceptions: what stands

> **Referee report R1, 27 November 2026: confirmed with fixes — Block on the sentence that every accepted `grow` start
> is in the class, and on the classifier as a complete inventory** ([the report](referee-R1/report.md)). All 67 twin
> starts and the three failed-lift starts reproduce, and every draw count of the table reproduces on all 30,000 draws.
> - **Block: not every `grow` start.** The table shows 774 of 775 accepted `grow` draws certified in the class; an accepted
>   seven-knot `grow` start of the graded-order study (held-out draw 257587) has chained twins. Read "every accepted start
>   drawn here", not every accepted start.
> - **Block: the classifier kept one piece.** At a tie between two pieces failing in the same round it kept the first;
>   a 54-knot start with one piece of each kind lost a mechanism. Repaired (`shapes.py` keeps every piece at the earliest
>   round); the counts above are unchanged.
> - **Narrowings.** A twin family can have three or four lifts, and a split can have one shortening and three lifts, or
>   three families; "N3 never fails alone" and the lift-split count are for completed cores: of the 3,166 `tree+` draws
>   left unresolved by the caps, 1,363 already violate a class condition on the checked prefix, 876 of them N2 alone, so
>   failed lifts are frequent among large cores and rare only among the cores that finish here. Seven-knot `tree+`
>   distinct starts are 227 and the rank-limited ones 12 (one hash collision). Read this record with these changes.

Epic `TWO-EXCEPTIONS-20261127-001` (G17 with G1; after `CHAIN-COUNT-20261127-001` and its referee), closed 27 November
2026. Computed, structure only; referee pending. [The note](README.md)

## What stands

1. **Two families break the reading, and nothing else seen (computed).** On all 67 sample starts with chained twins the
   first failure of the extended-node lemma is a twin family; on all three of the referees' failed-lift starts it is a
   lift split; every other start checked agrees through round 10.
2. **How often a start is outside the proved class (computed, named weightings).** Under `grow` every accepted start drawn
   at seven to eleven knots is in the class (one is over the cap; R1: not every accepted `grow` start). Under `tree+` the class holds 90% of accepted draws at
   seven knots falling to 67% at eleven; chained twins are under 3% at every size, failed lifts alone 2 draws in 15,000,
   and the rest are cores too large to check (up to 30%) or unfinished cycle cores (2% or less).

**Not shown.** A reading of the two families (the objective's second part, not attempted: births after them are not
pairs of a core node and chain lengths); what the cores over the cap are.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — classify and count the exceptions | **Status:** Successful (first part); second part not attempted | Every failure seen starts at one of the two named families; their frequency is measured under two weightings |
| Local direction — reading a growth from its start | Continue | The exceptions are a few percent under `tree+`; the size of the core is the larger limit |
| Broader exploration — what a local reader keeps of a start | Capability gained | Which starts the theorem covers is now measured by size |
| Long-term goal — G17 with G1 | Capability gained | Under `grow` every accepted start checked is read by the theorem |

**Next step:** Continue — #1 starts now in this thread

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | What the cores over the cap are: finishing, repeating or growing without bound | 2/3 — answers how often a core is unending, which the cap cannot | 3/3 — the cycle referee's finishing and repeating certificates exist | Run completion and repetition certificates on the capped starts of the counts above → each class counted, the rest unresolved | Selected |
| 2 | A structure for births after a twin family or a lift split | 3/3 — reads the last exceptions | 1/3 — no candidate structure yet | Build the births with the round rule on extended nodes past the first failure; look for a core-like object per chain support → a reading, or the reason none exists | Proposed |
| 3 | Decide whether N1 and N2 imply N3 | 2/3 | 2/3 — the referee's triple test | Prove the triple test, or build a start that fails it | Proposed |
| 4 | Chains on cores that never finish | 2/3 | 2/3 — the unrolled map's copies | As in `CYCLE-READ-20261127-001` | Proposed |

**Corrections:** one entry after R1 (two Blocks, two Narrowings, one Not a block).
**Goals:** checkpoint row added (G17 with G1; capability gained).
**Assumptions:** none new; the counts reuse the caps of A307 and the two weightings of `WEIGHTINGS-20261119-001B`.
**Scaffolds:** the caps (5,000 families, 250,000 pairs), rank 25, round 10 for the lemma, the seed. The caps decide which
starts are checked, not the class of a checked start; the percentages are of accepted draws under each named weighting.
**Advisor:** not consulted (its usage limit was reached earlier in the session).
