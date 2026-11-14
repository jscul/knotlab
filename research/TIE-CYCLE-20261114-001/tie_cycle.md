# Is identity the whole story of forgetting

Epic `TIE-CYCLE-20261114-001` (`FORGET-RULE-20261114-001#1`; G17, with G1), 2026-11-14, at the coordinator's go-ahead. The thread's
work, reusing FREE-TARGET's per-call relations; the advisor consulted before the freeze. Pre-registered in two stages: a fresh split
(152856bab), then the rules and the held-out predictions (1f9e55b8c). The held-out half was then read once. The canonical K1–K3 test
is unchanged. **Referee pending.** The equivalence is about forgetting itself (rectangularity). Reading it as growth of the free bond
holds for depth-s targets in copies of S reached through S calls (`CENSUS-FORGET-20261114-001`).

## Words

A **tie**: in a product of per-call relations, an end port always equal or always opposite to a start port. A **tie cycle**: some
product with a self-tie (port j to port j). An **idempotent**: a product E with E·E = E. Its **core** is {x : (x, x) ∈ E}, preordered
by (x, y) ∈ E. A non-rectangular idempotent either **conserves a label** (incomparable core classes: a tie, a parity or a non-linear
label) or is a one-way **order** (comparable classes).

## The question

Rule N said a port handed to itself around a cycle of calls prevents forgetting. Is every way a family keeps its depth's memory a
tie, so that "no tie cycle" is exactly forgetting?

## The question in standard terms

For finite semigroups of complement-closed relations on {0,1}³ × {0,1}³, whether eventual rectangularity is characterised by the
absence of coordinate self-ties, and how non-rectangular idempotents divide into conserved labels and orders.

## Conclusions

| # | Conclusion | Kind | Prediction |
| --- | --- | --- | --- |
| 1 | **Forgetting is exactly: every idempotent is rectangular (Theorem I).** Rectangular relations form an ideal, and every long word has an idempotent factor, so the two are equivalent. It checks on every decided family of both halves (0 violations on 12,759). | proved; checked | H3 held |
| 2 | **A tie cycle prevents forgetting,** in a living family (*narrowed after FORGET-RULE's referee*, the same premise as rule N). An equality or inequality on one coordinate, with both values present, is never a product. No family with a tie cycle forgets (0 of 6,445 held out). Ties beyond identity are rare: a tie forced through knots, with no port passed unchanged, occurs in 5 training families and 1 held out. | proved | H1 held |
| 3 | **No tie cycle almost means forgetting, but not quite.** Without a tie cycle every chain forgets (2,097 of 2,097 held out; 2,126 of 2,126 in training). Among non-chains 838 of 883 forget (94.9%; Wilson 93.3% to 96.2%), so "no tie cycle ⟺ forgetting" is false. | computed | H2 held (the share in 91.5% to 95.5%) |
| 4 | **What remains is order, not identity.** Among non-chains with no tie cycle that do not forget, 44 of 45 held out (97.8%; training 52 of 55) have only order-type idempotents. The top's state class and the deep copy's are linked by a one-way ordering: the deep copy can only lie at or above the top's class, and no quantity is conserved. A parity without a tie occurs in 1 held-out family and in none in training. | computed | H4 held |
| 5 | **Ties settle capped cases.** 53 families the census left capped have a tie cycle (26 training, 27 held out), so they are non-forgetting. | proved per family | reported |

## Answer

Almost. A nested pattern keeps its depth's memory almost always by identity: a port value carried down unchanged, or, rarely, a
value tied equal or opposite through knots. Every chain without such a tie forgets. The only other way, in about one family in
twenty of the rest, is an order: the deep copy's ports cannot fall below a class fixed by the top, but nothing is carried. And one
equivalence is exact, as a theorem: a family forgets precisely when every repeated product of its calls is a product relation.

## Reading

**Interpretation, not a theorem.**
- **Two kinds of memory.** A pattern remembers its top at depth either by **carrying** something (identity, a tie, once a parity),
  which is a conserved label, or by **ordering** (the depth can only be on one side of the top), which carries nothing but still
  constrains. Carrying is the rule; ordering is the rare exception the tie test misses.
- **For counting inside.** Where a family forgets, its free bond grows to copies of S reached through S calls. Where it remembers by
  carrying, the carried value gives short bonds, as the carried ports of `TRUE-RATE-20261113-001` showed. Where it remembers by order,
  the bond's behaviour is open (B174).

## Lag cutoffs and census-only claims

The 12,772 census first-ray growers, split 6,321 training and 6,451 held out (salt `TIE:`); 13 with a semigroup cap. Theorem I and the
tie lemma are proved for every family; the near-equivalence and the residual's type are census facts.

## Review

**Referee pending.** The advisor model reviewed the plan cold before freezing (`advisor_review_answer.md`). It gave Theorem I's
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

One carried from FORGET-RULE's referee (`docs/CORRECTIONS.md`, 2026-11-14): **Narrowing.** The tie lemma, like rule N, needs a
living family; an unsatisfiable family has empty, rectangular relations. No census count changes.

## Data

`experiments/TIE-CYCLE-20261114-001A/TIE-CYCLE-20261114-001A-E001_ties/`: `ties.py` (closure, ties, parities, idempotent types),
`heldout.py` → `heldout.json` (both halves, by stratum).

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — tie cycles | **Status:** Successful (referee pending) | H1–H4 held; Theorem I proved; identity is almost, not entirely, the story |
| Local direction — counting inside | Continue | The order-type families are the one kind of memory without carrying |
| Broader exploration — G17 | Searching | Memory of depth classified into carrying and ordering |
| Long-term goal — G17 Typical and rare meeting patterns (with G1) | Capability gained | What a nested pattern remembers of its top, by kind |

**Corrections:** one Narrowing carried from FORGET-RULE's referee (a living family). **Goals:** a checkpoint for G17 and G1; no goal change. **Assumptions:** A79 used.
**Basket:** `B173` (2/3 Payoff, 2/3 Concreteness; next in line), `B174` (2/3, 2/3), `FORGET-RULE-20261114-001#2` (1/3, 2/3).

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Other recursive definitions as targets (B173) | 2/3 — Substantial | 2/3 — Testable | The two-kind semigroup on the 186 uncovered census families, with the gap argument for mixed stretches → which second-definition targets stay close to the top, and why | Selected · next in line (the coordinator's order) |
| 2 | What an order does to the free bond | 2/3 — Substantial | 2/3 — Testable | On the ~100 order-type families, the free bond per depth with depth-dependent paths (part of B174) → bounded or growing, and whether order behaves like carrying | Alternative · after #1 |

1. Payoff 2: removes a caveat from three closed studies, and the referee's counterexamples show it is real. Concreteness 2.
2. Payoff 2: the one kind of memory without carrying. Concreteness 2: small set; per-depth method needed.

**Recommendation.** Research directions, #1, as the coordinator set.
