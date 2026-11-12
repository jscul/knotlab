# A native grade for rigidity

Epic `NATIVE-GRADE-20261112-001` (sub-goal B160, G15 with G16; program learning; the challenge of A68 and A69), 2026-11-12, at the
coordinator's go-ahead. Pre-registered in [preregistration.md](preregistration.md), frozen in commit `7999dd625` before any learning run.
Proof family: `proofs/NATIVE-GRADE-20261112-001A/`.

## The answer

**A graded, value-free rule of the knots partly replaces the supplied rigidity: on the undrawn base it keeps the count at the first target
in 8 of 10 runs (19 of 30 writes), on one copy in 6 of 10, where by its construction it gives no rigidity.**

- **The rule.** The learner rests where the law's sums around all its shortest cyclic sequences of knots and distinctions are equal,
  whatever the value, and is charged 2 for each sequence that would have to change. No value is chosen by us, so A69 is not needed on these
  two bases. The learner's own repair is free to re-sign.
- **The undrawn base, U (computed, frozen).** Found the count 10 of 10; held it 8 of 10 at the first target, which passes the frozen mark,
  and 19 of 30 across the three targets. Most of U's places lie on two or more shortest sequences, so re-signing one costs more than it
  mends.
- **One copy, J1 (computed, frozen).** Found 10 of 10; held 6 of 10, 17 of 30: still drifts, as predicted. No place on J1 lies on two
  shortest sequences, so the rule gives it no rigidity by construction.
- **A narrowing of LAW-RIGIDITY (exact).** On the next two bases of the frozen undrawn search, every rule fixing the shortest sums leaves 8
  laws at rest and none counts. The shortest-sum rest set worked on U by U's own structure; it is not a general native source.
- **How much of LAW-RIGIDITY's stage 2 was settled by definition.** On U, with 2 laws at rest and a repair that could not change a law,
  finding and keeping were nearly settled, and the disturbance never tested a move to the other law; the runs show only that the learner
  left the plain law quickly. On one copy, the learner found the count no faster than random draws among the laws at rest. Here too: on
  J1 it took a median of 244.5 probes where random draws among the 64 laws at rest would need 16. The examples are not steering the search.

## What is known, and what is proved and computed

| Claim | Evidence class |
| --- | --- |
| A law is a Z2 gauge field; its sums around cyclic sequences are the literature's frustration; learned couplings made stiff by a plaquette term | known: Toulouse 1977; Fradkin, Huberman and Shenker 1978; the gauged neural network of Kemuriyama, Matsui and Sakakibara (cond-mat/0203136) |
| "All shortest sums equal" leaves a counting law at rest on J1 (4 of 64) and U (1 of 2); on U(7, 9) and U(8, 10) no shortest-sum rule does | exhaustive |
| No place on J1 lies on two shortest sequences; 18 of U's 24 do | exhaustive |
| With the graded rule and a free repair: U held 8 of 10 at the first target (19 of 30 writes); J1 6 of 10 (17 of 30) | computed, frozen |
| The learner finds no faster than random draws among laws at rest | computed (probe counts against the exact rest-set sizes) |

## Against the pre-registration

- P(U) passed at the first target, as predicted; across all writes U held 19 of 30, which the pre-registration did not mark.
- P(J1) failed, and J1 still drifts, as predicted.
- By the frozen rule A69 is Overturned for these two bases (the value-free rule leaves a counting law at rest on both, exact). A68 was to
  be Overturned for U if P(U) passed and Confirmed if U drifted. P(U) passed, but J1 still needs a supplied rigidity and U holds only 19 of
  30 writes, so the evidence splits by base; A68 is returned to **Assumed**, with that recorded.

## What it changes

- **Rigidity can come from the knots where places are shared by enough shortest sequences.** The count of sequences through a place sets
  the cost of re-signing it, and that count is a property of the base.
- **The rest set is the open problem.** It finds the count, but no rule fixing the shortest sums contains a counting law on two of three
  undrawn bases, and within a rest set the learner searches no better than at random. B161 asks whether any rule of the knots chooses the
  rest set well on every base.

## Assumptions

A69 **Overturned** for J1 and U (replaced by the value-free rule). A68 returned to **Assumed** (U passes the first-target mark with a native
grade, 19 of 30 writes; J1 drifts without A68). Relied on: A20, A21, A46, A47, A49, A50, A52, A58, A66.

## Corrections

One, Narrowing: `LAW-RIGIDITY-20261112-001`'s reading that a rule read from the knots can supply the rest set holds on U only; on the next two
bases of the frozen search it leaves no counting law at rest.

## In the owner's words

Give the learner a rule that only asks the sums of its signs around the shortest cyclic sequences of knots to agree with one another, no
value chosen, and it finds the count on both patterns. It keeps it where most of its signs sit on two or more of those sequences, and loses
it where each sits on one or none. On two other small patterns, though, the rule leaves no counting rule to settle on at all.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: a native grade for rigidity (B160) | **Status:** Partially successful | U holds at the first target (8 of 10; 19 of 30 writes); J1 drifts; no chosen value needed |
| Local direction: native rest sets and rigidity from shortest sums | Practically exhausted | the rest set fails to contain the count on two of three undrawn bases |
| Broader exploration: learning program | Known alternatives | which sequences to fix (B161), rigidity from longer sequences (B162), the tie (B157), seven (B154), two histories (B159) |
| Long-term goal: G15 Learning: a point in a learned knot pattern | Capability gained | a count kept by a rule of the knots alone on a base no drawing fits, at the first target |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Which cyclic sequences to fix (B161) | 3/3 — Major | 2/3 — Testable | an exact census on J1, U, U(7, 9) and U(8, 10) of rules of the knots over cyclic sequences of up to three knots, defined before the census → a rule that leaves a counting law at rest on all four, or none in the family | Selected · awaiting go-ahead |
| 2 | Rigidity from longer sequences (B162) | 2/3 — Substantial | 3/3 — Ready | GE with sequences of up to three knots charged, on J1 and U, frozen → J1 held in 8 of 10, or still drifts | Alternative · deferred |
| 3 | A tie in place of the shared distinction (B157) | 2/3 — Substantial | 3/3 — Ready | as recorded | Alternative · deferred |
| 4 | The count of seven (B154) | 2/3 — Substantial | 3/3 — Ready | as recorded | Alternative · deferred |
| 5 | Two histories (B159) | 2/3 — Substantial | 2/3 — Testable | as recorded | Alternative · deferred |

- **#1:** payoff now 3/3, because the rest set is what lets the learner find a count, and whether the knots can choose it on every base
  decides whether learning on the owner's bases needs anything supplied; concreteness 2/3, the census is exact and small but the family of
  rules must be defined before it. Resource bound: an exact census of four bases.
- **#2:** payoff 2/3, it would give J1 rigidity natively; concreteness 3/3, one change to this epic's engine.
- **#3 to #5:** as recorded.

**Corrections:** one, Narrowing (LAW-RIGIDITY's native rest set works on U only, of three undrawn bases).
**Goals:** G15 checkpoint (capability gained, with G16); sub-goal B160 taken; B161's payoff raised to 3/3; B162 added.
**Assumptions:** A69 Overturned for J1 and U; A68 returned to Assumed.
**Basket:** B161 (selected, awaiting a go-ahead), B162, B157, B154, B159, B155, B156, B150, B151, B130.
