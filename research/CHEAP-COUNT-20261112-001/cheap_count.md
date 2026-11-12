# The cheapest counter

Epic `CHEAP-COUNT-20261112-001` (`TWO-BIT-ROWS-20261112-001` direction 2; G17, with G1), 2026-11-12, at the owner's go-ahead.
Pre-registered in commit 15f676529 before the registered run. The canonical K1–K3 test is unchanged. **Referee pending** (handed to
the referee thread).

## Words

As in the pre-registration: **fresh** (helper) distinctions, a **gadget** (NAE knots on four named and some fresh distinctions whose
allowed states on the named four are exactly their even parity), **generations** each one position longer, the reference R, the
additive rules 60, 90 and 150 (each new main distinction the parity of old ones, read against R where needed), and the **hopping**
rule (new i, old ⌊i/2⌋, old i, R).

## The question

What is the fewest NAE knots that make the parity a binary counter is built from, how fragile is the counter, how much weight does
counting get under short descriptions, and does a hopping version count?

## The question in standard terms

The minimum size of a primitive positive NAE₃ definition of 4-ary even parity with f auxiliaries; satisfiability by depth of the
additive triangles built from it; robustness to one changed constraint; a halving-reach variant.

## Conclusions

| # | Conclusion | Kind | Prediction |
| --- | --- | --- | --- |
| 1 | **A parity takes at least 10 NAE knots, and at least 3 helpers.** With 0, 1 or 2 fresh distinctions no gadget exists; with 3 the least is 12 knots (168 minimal gadgets, all enumerated); with 4, 5 or 6 it is 10. So the cheapest counter trades knots for distinctions: 12 knots and 4 distinctions per position, or 10 knots and 5. | exact (SAT, with unsatisfiability at every smaller size) | P1 held (plateau at 10) |
| 2 | **The counter counts, as known.** Built from the minimal gadget, rule 60's life is identical at every depth to 64 to the exact parity's, alive at depths 1–6, 11–14, 27–30 and 59–62 (the referee's bands and the next, 2^k − 5 to 2^k − 2); rules 90 and 150 count too; rule 102 dies at depth 3. | computed; counting by the known algebra | G passed |
| 3 | **Counting is astronomically rare under short descriptions.** The cheapest counting description takes about 104 to 106 bits (with 4 or 3 helpers per position); the 504 counting descriptions found (168 gadgets, three rules) weigh about 2^−97 together. | computed from the code | reported |
| 4 | **And fragile.** Of the 240 single-knot deletions and replacements of a minimal gadget, 3 (1.25%) still count, each a replacement that gives another minimal gadget; the rest are constant (169) or settle (68). | exact per mutant, frozen | P2 held |
| 5 | **The hopping version does not count.** With the old neighbour replaced by the old position at half the index, the growth lives to depth 11 (dead at 8 and 10) and is dead from 12 to 64. | computed, frozen | P3 failed |

## Answer

The cheapest NAE counter needs, at every position, a four-place parity built from at least 10 knots and at least 3 helper
distinctions, and it then counts depth in binary, exactly as the known additive rules do. Under a weighting by short descriptions
such a pattern has weight about 2^−97, and changing one knot almost always destroys it. The owner's hopping reach does not help: the
hopping version of the counter dies.

## Reading

**Interpretation, not a theorem.**
- **For the owner's "simple realities are more common".** Counting is possible but expensive: it needs a fine-tuned structure at
  every position, which a weighting by simplicity makes about 10^−29 likely. Patterns that count, and so could carry arithmetic, are
  among the rarest ones.
- **Distinctions per position.** With one or two distinctions per position and no helpers nothing counted (`ROW-NEST-20261112-001`,
  `TWO-BIT-ROWS-20261112-001`); this construction needs four or more. Whether three per position can count by another route is open.
- **Hopping.** Reaching back to half the index makes the additive rule die rather than count; nested reach is not a shortcut to
  counting here.

## Lag cutoffs and census-only claims

Gadget sizes exact for f ≤ 6 fresh distinctions; growths to depth 64; one minimal gadget (f = 3) used for the build and the mutants.
No claim about other routes to counting, other reaches, or depths beyond 64 except by the known algebra.

## Run note

The counter and mutant stages were first launched before the synthesis had finished (a waiting command that matched no unit) and
failed for want of its output; they were rerun unchanged once it existed. Nothing was looked at in between.

## Review

Referee pending (the referee thread). The advisor model reviewed the draft cold (`advisor_review_answer.md`): it made the counter a
wiring check, gave the infeasibility for f ≤ 2, and asked for the plateau check, the weight as the headline and single-knot
fragility.

## Literature and provenance

Known: the definability (Böhler, Reith, Schnoor and Vollmer 2005); additive automata counting in binary (Martin, Odlyzko and Wolfram
1984). Not found (a bounded check, the advisor's): exact primitive positive sizes for parity from NAE; gadget-optimality work
(Trevisan, Sorkin, Sudan and Williamson) concerns approximation gadgets. New: the m*(f) table, the counter's weight and fragility,
the hopping variant's failure. Classification: known-with-delta.

## Workspace assumptions

A79's kind of code used for the weighting.

## Ratio

Substantive: the synthesis, the growths and the mutants. Administrative: the pre-registration, this note, the closure.

## Corrections

None.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the cheapest counter | **Status:** Partially successful (referee pending) | P1, P2 held; P3 failed: the counter costs at least 10 knots and 3 helpers, weighs about 2^−97, and hopping does not count |
| Local direction — counting | Continue | Whether three distinctions per position can count is open |
| Broader exploration — G17 | Searching | Counting inside is in the basket |
| Long-term goal — G17 Typical and rare meeting patterns (with G1) | Capability gained | Counting is located among the rarest patterns |

**Corrections:** none. **Goals:** a checkpoint for G17 and G1 (capability gained); no goal change. **Assumptions:** none new.
**Basket:** `NEST-COUNT-20261112-001#1` (counting inside; 3/3 Payoff, 1/3 Concreteness), `PREFIX-END-20261112-001#2` (2/3, 3/3),
`LIFE-JUMPS-20261112-001#2` (2/3, 3/3), `LIMIT-ONLY-20261112-001#1` (2/3, 2/3), `NEST-READ-20261112-001#2` (2/3, 2/3).

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Counting with three distinctions per position | 2/3 — Substantial | 2/3 — Testable | Search for a counter whose helpers are shared between neighbouring positions (three distinctions per position), by SAT synthesis of the growth rule against a depth-indexed life pattern → a cheaper counter, or a proof that none exists in that class | Selected · awaiting go-ahead |
| 2 | Why the hopping counter dies | 1/3 — Minor | 3/3 — Ready | Read the hopping growth's forced values by depth → a mechanism | Alternative · deferred |

1. Payoff 2: it would set the threshold of distinctions per position for counting. Concreteness 2: the synthesis is new.
2. Payoff 1: a mechanism for one construction. Concreteness 3.

**Recommendation.** Research directions, #1, awaiting the go-ahead.
