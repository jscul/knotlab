# Rows that grow by one

Epic `ROW-NEST-20261112-001` (`NEST-COUNT-20261112-001` direction 2; G17, with G1), 2026-11-12, at the coordinator's go-ahead.
Pre-registered in commit 47e0312fe before the registered run. The canonical K1–K3 test is unchanged. Refereed by the referee thread
(ROW-NEST-R1, `referee-R1/report.md`, commit 3d4c50d4c): **confirmed with fixes**, folded in below; three corrections logged (one
Narrowing, two Not a block).

## Words

As in the pre-registration: a **row rule** (knots between a row and the next, one longer, at relative positions within one step),
the **closing row** (knots on consecutive triples of the bottom row), **alive(t)**, the **first-row relation** T_t, and the classes
**constant**, **eventually constant**, **harmony** (eventually periodic with period at least 2) and **unexplained within 40**.

## The question

With one more distinction passed per depth, the smallest escape from the finite-state theorem, do NAE patterns count (life or the
first row depending on depth without a period), make harmonies (with a period), or neither, and how common is each under short
descriptions?

## The question in standard terms

For NAE window-1 rules on a growing triangle closed at the bottom: whether satisfiability and the projection onto the first row are
eventually periodic in the depth, and with what period, for depths up to 40.

## Conclusions

| # | Conclusion | Kind | Prediction |
| --- | --- | --- | --- |
| 1 | **No rule counts.** Of the 1,024 rules, none has life or a first-row relation unexplained within depth 40. | exhaustive, depth ≤ 40, census frozen | Q2 held |
| 2 | **No rule makes a harmony either.** Life is constant in 910 rules and eventually constant in 114; the first-row relation is constant in 787 and eventually constant in 237. Nothing depends on depth with a period. | exhaustive, depth ≤ 40 | Q3 failed |
| 3 | **Everything settles at once.** The first-row relation last differs from the depth before at depth 2 (186 rules), 3 (43) or 4 (8), and never later (*corrected after the referee: the census's counts were by the earlier depth of each change*). Given at least one knot, 96% of the weight has constant life and 92% a constant first row. | exhaustive, depth ≤ 40 | reported |
| 4 | **Death comes from density.** No rule with four knots or fewer is dead at depth 40; 126 rules with five or more are (7% of the weight given at least one knot), all dead from early on. | exhaustive, depth ≤ 40 | reported |

## Answer

Passing one more distinction per depth is not enough for these rules to count, or even to keep time: with one distinction per
position, knots reaching one step, no fresh distinctions and the ends of each generation left free, every rule's life and every first
row settle within four depths. *After the referee:* that null result is a property of the class. With fresh distinctions (a four-place
parity, which NAE defines) and the ends read against one reference distinction, rules 60, 90 and 150 count: rule 60 lives at depths
1 to 6, 11 to 14 and 27 to 30, reading depth in binary, the known additive-automaton mechanism (Martin, Odlyzko and Wolfram 1984;
Lucas's theorem). Either widening alone counts nothing.

## Reading

**Interpretation, not a theorem.**
- **For the owner's harmonies.** A harmony would be a pattern whose life comes and goes with depth's residue; none appears in this
  class. *(The reason first given here, that one bit per site has no room to carry a signal, is refuted inside the class by the
  referee: mask 148, three knots, makes every interior new distinction the complement of the majority of the three above it, a
  deterministic map between generations; it does not count because such threshold maps settle to fixed points or period two, Goles
  and Olivos 1980. What the class lacks is fresh distinctions and constrained ends.)*
- **Where counting lives.** The domino problem shows growing interfaces can count once local rules are rich enough; the frontier is
  how much richer than one NAE bit per site, and how rare such rules are under short descriptions.

## Lag cutoffs and census-only claims

All 1,024 window-1 rules, first row of three, depths 1 to 40. Nothing is claimed beyond depth 40, for wider windows, or for more
distinctions per site.

## Review

**ROW-NEST-R1** (the referee thread, confirmed with fixes): all 1,024 rules reproduce exactly at every depth; the construction and
classifier are as frozen; the null result is by the class's definition (Narrowing above); the 512 rules containing the knot on old
i − 1, i, i + 1 are monotone by construction; the last-change depths were counted one early. The advisor model reviewed the draft cold (`advisor_review_answer.md`): it showed the draft's
observable monotone and its counting test vacuous without a closing row, which the design then added, and asked for weights given at
least one knot.

## Literature and provenance

Known: space-time diagrams of cellular automata; the seeded domino problem (Wang 1961), the domino problem (Berger 1966). Not found:
the census of NAE window-1 row rules. Classification: known-with-delta.

## Workspace assumptions

A79's kind of code used for the weighting.

## Ratio

Substantive: the exhaustive census. Administrative: the pre-registration, this note, the closure.

## Corrections

Three, from the referee (`docs/CORRECTIONS.md`, 2026-11-12): **Narrowing**, the null is by the class's definition and the stated
reason is refuted; **Not a block**, half the rules are monotone by construction; **Not a block**, last-change depths one early.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — rows that grow by one | **Status:** Partially successful (refereed, confirmed with fixes) | Q2 held, Q3 failed: no counting, no harmonies, everything settles by depth 3 |
| Local direction — counting | Continue | The frontier is how rich a local rule must be |
| Broader exploration — G17 | Searching | Counting inside and the extra witnesses are in the basket |
| Long-term goal — G1 Space from a law (with G17) | Capability gained | One NAE bit per site cannot carry a signal down growing rows |

**Corrections:** none. **Goals:** a checkpoint for G17 and G1 (capability gained); no goal change. **Assumptions:** none new.
**Basket:** `NEST-COUNT-20261112-001#1` (counting inside; 3/3 Payoff, 1/3 Concreteness until an exact multi-level bond method
exists), `WITNESS-COUNT-20261112-001#1` (2/3, 3/3), `PREFIX-END-20261112-001#2` (2/3, 3/3), `LIFE-JUMPS-20261112-001#2` (2/3, 3/3),
`LIMIT-ONLY-20261112-001#1` (2/3, 2/3), `NEST-READ-20261112-001#2` (2/3, 2/3).

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Two distinctions per site | 3/3 — Breakthrough-scale if counting appears | 2/3 — Testable | Sample row rules on two distinctions per site (knots among the ten relative distinctions) by short descriptions, read life and the first rows to depth 40 → the fewest knots that make a harmony or a counter, and their weight, or none | Selected · awaiting go-ahead |
| 2 | Where the extra witnesses sit | 2/3 — Substantial | 3/3 — Ready | As in `WITNESS-COUNT-20261112-001` | Alternative · deferred |

1. Payoff 3 if a counter appears: the smallest NAE pattern that counts, and how rare it is. Concreteness 2: the census is a small
   change; the rule space must be sampled, not enumerated (2^120 rules).
2. Payoff 2, Concreteness 3, as recorded.

**Recommendation.** Research directions, #1, awaiting the go-ahead.
