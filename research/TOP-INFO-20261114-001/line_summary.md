# Counting inside nested patterns: the line's closing summary

2026-11-14. The nested fixed-interface line, from the census of first-ray growth (`REACH-CENSUS-20261113-001`) to the whole-rule
study (`TOP-INFO-20261114-001`). Every epic named here is refereed and folded in. The coordinator wrapped the line up at that point.
CARRY-BOUND's direct-search readings are folded in: the 28 sampled undecided families stay flat at 2 or 3 up to depth 5, so the
undecided look bounded (a reading, not a proof). TOP-INFO's brute-force gate was still running when this was written.

## The question

A nested pattern is a recursive NAE definition unfolded without end (the usual limit). Does the law count depth inside it with
nothing chosen? That is: does the least bond from the top to a copy at depth s, with members anywhere, grow with s, or stay bounded?
And what decides which?

## What is proved

| Result | Where |
| --- | --- |
| **The gap argument.** If every product of r per-call port relations is a product relation (forgetting), every bond to a covered copy at depth s has at least 2 + ⌊s/r⌋ members (one level fewer for a wrapper main). | `FREE-TARGET-20261114-001` |
| **Theorem I (classical).** A family forgets exactly when every idempotent of its product semigroup is a product relation. | `TIE-CYCLE-20261114-001` |
| **Rules N and A.** An identity cycle (or a tie cycle) prevents forgetting in a living family; separation after guarded peeling implies it. | `FORGET-RULE-20261114-001`, `TIE-CYCLE-20261114-001` |
| **Exact windows.** The projection onto main's ports (or main's whole block) and the target copy's block is exact, so window bonds bound the reach; the bound is eventually periodic and computed exactly. | `CARRY-BOUND-20261114-001`, `TOP-INFO-20261114-001` |
| **Unread carrying.** If, after deleting the coordinates no knot reads, the relations forget, the bond grows. | `CARRY-BOUND-20261114-001` |
| **Theorem R.** A carried top port read by a knot with an own distinction of the target copy gives a bond of at most 3, unless a tie splits that knot. With a pendant third member there is no exception (R1). | `READ-RULE-20261114-001` |
| **The dichotomy.** Per residue of the depth, the bond is eventually bounded or has a positive linear lower bound, possibly very weak. Nothing grows sublinearly. | `READ-RULE-20261114-001` |
| **The effective converse.** A reading outside R's exception at infinitely many depths of a residue bounds the bond there. Read syntactically, the converse is false. | `READ-RULE-20261114-001` (its referee) |
| **Bond-pinning (P′).** Shattered sets of main's ports and the target copy's own distinctions that are jointly constrained contain a bond of their total size. | `TOP-INFO-20261114-001` |
| **Localisation.** Every bounded case has some least bond within a window at the top and at the target, computable once the bound is known. | `TOP-INFO-20261114-001` |

## What is computed (the census, by draws)

The census's first-ray growth is 13,279 draws:
- **Grows, proved: 58.0%** (7,697 draws). Chains, forgetting non-chains, and the 634 draws whose carried values are unread.
- **Bounded, proved: 39.7%** (5,276 draws). It splits as follows, by family:
  - 88.4% by an effective reading;
  - 10.3% by pinning;
  - 1.3% a residue that neither explains on every residue.
- **Undecided: 2.3%** (306 draws). Of these, 72 families are in scope, 46 are outside it, and 188 draws lie outside CENSUS-FORGET's
  covered targets.

The first ray overstates growth. In 40% of the first-ray growth weight, a path that changes with the depth finds a short bond at every
large depth.

## What it means (interpretation)

The law counts depth exactly where the deep copy holds no usable information about the top. A carried value that some knot reads,
or a one-way order that pins the deep copy's own distinctions, keeps the top within a few members. A value carried but unread, or
read only where a tie splits the knot, leaves the bond to grow.

## What is open

| # | Open item | Payoff | Concreteness | Backlog |
| --- | --- | --- | --- | --- |
| 1 | Why a one-way order bounds the bond: 78 of the 93 order families are pinned, the other 15 are not | 2/3 | 2/3 | B177 |
| 2 | Decide boundedness: an a priori bound on the least bounded value | 2/3 | 1/3 | B179 |
| 3 | The 72 undecided in-scope families (almost all capped windows) | 1/3 | 2/3 | B178 |
| 4 | Pinning with main's whole block, on the 65 unexplained families (covers at least 3) | 1/3 | 3/3 | B176 |
| 5 | Other recursive definitions as targets (largely answered by the referees' counterexamples) | 1/3 | 2/3 | B173 |

## Lessons

These are kept in `docs/CORRECTIONS.md`:
- A certificate's target type is part of its claim.
- Write a rule's guards as the code applies them.
- A sort read on a relation's core is a label, not a classification.
- Kept is not read.
- An exception local to one knot can hold at every copy.
- A residue of what two tests miss is not a mechanism until its members are looked at.
