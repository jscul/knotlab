# The cheapest counter

Epic `CHEAP-COUNT-20261112-001` (`TWO-BIT-ROWS-20261112-001` direction 2; G17, with G1), 2026-11-12, at the owner's go-ahead.
Pre-registered in commit 15f676529 before the registered run. The canonical K1–K3 test is unchanged. Refereed by the referee thread
with Codex (CHEAP-COUNT-R1, `referee-R1/report.md`, commit 327daf56a): **confirmed with fixes**, folded in below; seven corrections
logged (**one Block**, three Narrowing, three Not a block).

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
| 1 | **A parity takes at least 10 NAE knots, and at least 3 helpers.** With 0, 1 or 2 fresh distinctions no gadget exists; with 3 the least is 12 knots (168 minimal gadgets, all enumerated); with 4, 5 or 6 it is 10. So the cheapest counter built on such a gadget trades knots for distinctions: 12 knots and 4 distinctions per position, or 10 knots and 5. *After the referee: the ten-knot bound holds for every number of helpers, not only up to 6: a helper in a single knot can be dropped with that knot, so a minimal gadget has 4 + 2f ≤ 3m, and m ≤ 9 forces f ≤ 11; reduced searches at f = 7 to 11 are all unsatisfiable. The 168 minimal gadgets at f = 3 fall into three classes (24, 72 and 72; 28 classes up to relabelling helpers).* | exact (SAT, with unsatisfiability at every smaller size) | P1 held (plateau at 10) |
| 2 | **The counter counts, as known.** Built from the minimal gadget, rule 60's life is identical at every depth to 64 to the exact parity's, alive at depths 1–6, 11–14, 27–30 and 59–62 (the referee's bands and the next, 2^k − 5 to 2^k − 2); rules 90 and 150 are unexplained within depth 64 (*worded as finite after the referee; "count too" read beyond the depths run*); rule 102 dies at depth 3. | computed; counting by the known algebra for rule 60 | G passed |
| 3 | ~~**Counting is astronomically rare under short descriptions.**~~ *Withdrawn after the referee (Block):* the cheapest counting descriptions found in this template take about 104 to 106 bits (with 4 or 3 helpers per position), counting the frozen decoder's conventions (one global reference, the ends read against it, the closing generation, the equality copies) at no cost; the 504 found weigh about 2^−97 together, which is a lower bound on the mass of counting, not an upper bound, so it says nothing about how rare counting is. | computed from the code | reported |
| 4 | **And fragile.** Of the 240 single-knot deletions and replacements of a minimal gadget, 3 (1.25%) still count, each a replacement that gives another minimal gadget; the rest are constant (169) or settle (68), within depth 64. *After the referee: that every deletion fails follows from minimality; what is measured is the three replacements and the growth classes, which are readings to depth 64.* | exact per mutant, frozen | P2 held |
| 5 | **The hopping version is dead from depth 12 to 64.** With the old neighbour replaced by the old position at half the index, the growth lives to depth 11 (dead at 8 and 10) and is dead from 12 to 64 (*worded as finite after the referee*). | computed, frozen | P3 failed |

## Answer

A counter built on a four-place parity needs, at every position, a parity of at least 10 knots and at least 3 helper distinctions
(for any number of helpers), and it then counts depth in binary, exactly as the known additive rules do. The cheapest such
descriptions found take about 104 to 106 bits under the frozen code; that is not a measure of how rare counting is, since other
counters may exist. Changing one knot almost always breaks it within depth 64, and the hopping version is dead from depth 12 to 64.
*(Corrected after the referee: the rarity claim is withdrawn, the scope is counters built on a parity gadget, and the finite readings
are stated as finite.)*

## Reading

**Interpretation, not a theorem.**
- **For the owner's "simple realities are more common".** Counting by this route is possible but expensive: it needs a fine-tuned
  structure at every position, about a hundred bits of description. Whether counting as such is rare needs an upper bound on all
  counting descriptions, which this study does not give. *(The "about 10^−29 likely" first written here is withdrawn.)*
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

**CHEAP-COUNT-R1** (the referee thread with Codex, confirmed with fixes): every number reproduces; the enumeration at f = 3 is
complete; the ten-knot bound holds for every f; the rarity headline is a Block; the finite readings and the parity scope are
narrowed. The advisor model reviewed the draft cold (`advisor_review_answer.md`): it made the counter a
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

Seven, from the referee (`docs/CORRECTIONS.md`, 2026-11-13): **Block**, the rarity claim; **Narrowing**, the parity scope; **Narrowing**,
finite verdicts as finite; **Narrowing**, the decoder conventions the bits assume; **Not a block**, the bound for every f; **Not a
block**, the gadget classes; **Not a block**, deletions failing by minimality.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the cheapest counter | **Status:** Partially successful (refereed, confirmed with fixes; one Block) | P1, P2 held; P3 failed: a parity-built counter costs at least 10 knots and 3 helpers; rarity not shown |
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
