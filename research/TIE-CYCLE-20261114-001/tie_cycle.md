# Is identity the whole story of forgetting

Epic `TIE-CYCLE-20261114-001` (`FORGET-RULE-20261114-001#1`; G17, with G1), 2026-11-14, at the coordinator's go-ahead. The thread's
work, reusing FREE-TARGET's per-call relations; the advisor consulted before the freeze. Pre-registered in two stages: a fresh split
(152856bab), then the rules and the held-out predictions (1f9e55b8c). The held-out half was then read once. The canonical K1–K3 test
is unchanged. Refereed by the referee thread with Codex (TIE-CYCLE-R1, `referee-R1/report.md`, commit 46889db02): **confirmed with
fixes, one Block on the order and label prose**. Theorem I, the tie lemma and H1 to H4 stand; the residual's description is narrowed
below. The equivalence is about forgetting itself (rectangularity). Reading it as growth of the free bond
holds for depth-s targets in copies of S reached through S calls (`CENSUS-FORGET-20261114-001`).

## Words

A **tie**: in a product of per-call relations, an end port always equal or always opposite to a start port. A **tie cycle**: some
product with a self-tie (port j to port j). An **idempotent**: a product E with E·E = E. Its **core** is {x : (x, x) ∈ E}, preordered
by (x, y) ∈ E. The study sorted non-rectangular idempotents by their core: incomparable core classes were read as a conserved
**label** (a tie, a parity or a non-linear label), one-way comparable classes as an **order**. *Corrected after the referee:* this is a
census label read on the core, not a dichotomy. Explicit complement-closed relations refute it in general, a core label need not
hold between a word's ends, and one idempotent can have an order and a conserved parity at once.

## The question

Rule N said a port handed to itself around a cycle of calls prevents forgetting. Is every way a family keeps its depth's memory a
tie, so that "no tie cycle" is exactly forgetting?

## The question in standard terms

For finite semigroups of complement-closed relations on {0,1}³ × {0,1}³, whether eventual rectangularity is characterised by the
absence of coordinate self-ties, and how non-rectangular idempotents divide into conserved labels and orders.

## Conclusions

| # | Conclusion | Kind | Prediction |
| --- | --- | --- | --- |
| 1 | **Forgetting is exactly: every idempotent is rectangular (Theorem I).** Rectangular relations form an ideal, and every long word has an idempotent factor, so the two are equivalent. It is the classical Rees-quotient fact (for a nonempty ideal I, S/I is nilpotent iff every idempotent lies in I). *Narrowed after the referee:* so H3's 0 violations on 12,759 decided families are a consequence of the theorem and a code check, not a prediction; the referee matched all 6,931 non-forgetting families against independent idempotent witnesses. | proved (classical); checked | H3 (a code check) |
| 2 | **A tie cycle prevents forgetting,** in a living family (*narrowed after FORGET-RULE's referee*, the same premise as rule N). An equality or inequality on one coordinate, with both values present, is never a product. The living premise holds here: every generator is serial on a nonempty support, so no word is empty. No family with a tie cycle forgets (*corrected after the referee*: 0 of 3,471 tied families held out; the earlier "0 of 6,445" counted every decided family). Ties beyond identity are rare: a tie forced through knots, with no identity cycle, occurs in 5 training families and 1 held out; some of them pass a port to another position, so "no port passed unchanged" is read narrowly. | proved | H1 held |
| 3 | **No tie cycle almost means forgetting, but not quite.** Without a tie cycle every chain forgets (2,097 of 2,097 held out; 2,126 of 2,126 in training). Among non-chains 838 of 883 forget (94.9%; Wilson 93.3% to 96.2%), so "no tie cycle ⟺ forgetting" is false. | computed | H2 held (the share in 91.5% to 95.5%) |
| 4 | **Most of what remains has only one-way core comparabilities.** Among non-chains with no tie cycle that do not forget, 44 of 45 held out (97.8%; training 52 of 55) have only idempotents whose core classes are comparable one way. *Corrected after the referee (Block on the prose):* ~~no quantity is conserved~~. The held-out family 4f5934b2e118 has a single such idempotent (word [1,1]) that also conserves start[0] ⊕ start[2] = end[0] ⊕ end[2]. It is the one tie-free parity, and it was counted inside the 44. So "an order and nothing carried" holds in 43 of 45 held out (training 52 of 55). | computed | H4 held (as frozen, under either reading) |
| 5 | **Ties settle capped cases.** *Corrected after the referee:* all 66 families the census left capped have identity cycles, so all are non-forgetting. The study's 53 left out 13 recorded as a semigroup cap. | proved per family | reported |

## Answer

Almost. A nested pattern keeps its depth's memory almost always by identity: a port value carried down unchanged (98.5% of the
non-forgetting families have an identity cycle), or, rarely, a value tied equal or opposite through knots. Every chain without such
a tie forgets. *Corrected after the referee:* ~~The only other way, in about one family in twenty of the rest, is an order, and
nothing is carried.~~ Most of the rest, about one family in twenty, have only one-way core comparabilities: the deep copy's ports
cannot fall below a class fixed by the top. A conserved parity can coexist with such an order (one held-out family), and a label read
on the core need not hold between the ends. And one equivalence is exact, as a classical theorem: a family forgets precisely when
every repeated product of its calls is a product relation.

## Reading

**Interpretation, not a theorem.**
- **Carrying and ordering.** A pattern remembers its top at depth mostly by **carrying** something (identity, a tie), and in a few
  families by **ordering** (the depth can only be on one side of the top). *Narrowed after the referee:* these are two census
  descriptions, not an exhaustive pair; one family orders and carries a parity at once.
- **For counting inside.** Where a family forgets, its free bond grows to copies of S reached through S calls. Where it remembers by
  carrying, the carried value gives short bonds, as the carried ports of `TRUE-RATE-20261113-001` showed, *when some knot reads it*
  (narrowed after `CARRY-BOUND-20261114-001`: in 632 families every carried value is unread, and the bond grows). Where it remembers by order,
  the bond's behaviour is open (B174). *Narrowed after the referee:* non-forgetting proves neither a bounded bond nor the absence of
  growth, and any growth reading keeps the covered-target scope.

## Lag cutoffs and census-only claims

The 12,772 census first-ray growers, split 6,321 training and 6,451 held out (salt `TIE:`); 13 with a semigroup cap. Theorem I and the
tie lemma are proved for every family; the near-equivalence and the residual's type are census facts, and the residual's type is
a label read on the core.

## Review

**TIE-CYCLE-R1**: confirmed with fixes, one Block on the order and label prose. Codex recomputed all 12,772 families and 26,243
relations, the ties and the 159 residual idempotents with a second set-based check. The advisor model reviewed the plan cold before freezing (`advisor_review_answer.md`). It gave Theorem I's
reduction and the classification of idempotents into labels and orders, and it caught that my first count left out 33 capped
families. It also tightened H2's band and replaced a descriptive H4 with a falsifiable one. All of this was adopted.

## Literature and provenance

Known: idempotents in finite semigroups (the pumping argument is classical, as in Simon's factorisation forests); rectangular
relations as an ideal. Ours: the classification's use for nested NAE families, and the census split into carrying and ordering.
Classification: known-with-delta.

## Workspace assumptions

A79 used.

## Ratio

Substantive: Theorem I and the held-out test on 6,451 families. Administrative: the two freezes, this note.

## Corrections

From the referee (`docs/CORRECTIONS.md`, 2026-11-14):
- **Block.** The residual's prose: "an order, nothing carried" holds in 43 of 45 held out, not 44, and the label/order sort is a
  census label read on the core, not a dichotomy.
- **Narrowing.** H3 is a consequence of the classical Theorem I and a code check.
- **Narrowing.** The capped families (all 66 have identity cycles) and the tied denominator (0 of 3,471); ties beyond identity read
  narrowly.
- **Narrowing.** Any growth reading keeps the covered-target scope.

Found later by `CARRY-BOUND-20261114-001`: **Narrowing.** A carried value gives short bonds only when some knot reads it.

Carried from FORGET-RULE's referee and confirmed by this one: **Narrowing.** The tie lemma, like rule N, needs a living family. No
census count changes.

## Data

`experiments/TIE-CYCLE-20261114-001A/TIE-CYCLE-20261114-001A-E001_ties/`: `ties.py` (closure, ties, parities, idempotent types),
`heldout.py` → `heldout.json` (both halves, by stratum).

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — tie cycles | **Status:** Successful (refereed, confirmed with fixes) | H1–H4 held; Theorem I proved (classical); identity is almost, not entirely, the story |
| Local direction — counting inside | Continue | The order-type families are the one kind of memory without carrying |
| Broader exploration — G17 | Searching | Memory of depth classified into carrying and ordering |
| Long-term goal — G17 Typical and rare meeting patterns (with G1) | Capability gained | What a nested pattern remembers of its top, by kind |

**Corrections:** five: from the referee one Block (the residual's prose) and three Narrowing; one Narrowing carried from FORGET-RULE's referee (a living family). **Goals:** a checkpoint for G17 and G1; no goal change. **Assumptions:** A79 used.
**Basket:** `B173` (2/3 Payoff, 2/3 Concreteness; next in line), `B174` (2/3, 2/3), `FORGET-RULE-20261114-001#2` (1/3, 2/3).

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Other recursive definitions as targets (B173) | 2/3 — Substantial | 2/3 — Testable | The two-kind semigroup on the 186 uncovered census families, with the gap argument for mixed stretches → which second-definition targets stay close to the top, and why | Selected · next in line (the coordinator's order) |
| 2 | What an order does to the free bond | 2/3 — Substantial | 2/3 — Testable | On the ~100 order-type families, the free bond per depth with depth-dependent paths (part of B174) → bounded or growing, and whether order behaves like carrying | Alternative · after #1 |

1. Payoff 2: removes a caveat from three closed studies, and the referee's counterexamples show it is real. Concreteness 2.
2. Payoff 2: the one kind of memory without carrying. Concreteness 2: small set; per-depth method needed.

**Recommendation.** Research directions, #1, as the coordinator set.
