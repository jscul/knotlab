# Can nested patterns count?

Epic `NEST-COUNT-20261112-001` (`WITNESS-COUNT-20261112-001` direction 2; G17, with G1), 2026-11-12, agreed by the owner after he
asked how Gödel's work relates to ours. Pre-registered in commit d008757c0; one statement amended before the proof. The canonical
K1–K3 test is unchanged. **Referee pending** (handed to the referee thread).

## The question

Can the nested patterns of the A79 language count, and is whether they live decided by a procedure that always ends? If not, what
is the smallest extension in which living becomes undecidable and a counter can be built?

## The question in standard terms

For satisfiability of iterated hyperedge-replacement NAE instances with bounded interfaces: decidability and eventual periodicity
in depth, at finite depths and in the limit; expressiveness of NAE on distinct variables; and satisfiability of translation-invariant
NAE instances on Z².

## Conclusions

| # | Conclusion | Kind | Prediction |
| --- | --- | --- | --- |
| 1 | **Every nested pattern of the language is finite-state.** The self-holding definitions' relations at depth t follow a fixed map on at most 16^s values (s self-holding definitions), so whether the depth-t pattern lives is eventually periodic, with preperiod plus period at most 16^s; whether the bottomless pattern lives is decided by a greatest fixed point in at most 4s steps, and the usual limit is the bottomless pattern with the knot on the ports of each definition that passes its own ends to itself. Every question of life is decided by a procedure that always ends. | proved (known in kind) | T1 |
| 2 | **No counter in a top window.** What the depth-t pattern allows on any fixed window of top levels is a function of the relations a fixed number of levels down, so it reads depth only modulo the period. Under the A79 weighting no description counts its depth from the top. | proved | T2 |
| 3 | **NAE alone can say everything symmetric.** Four knots on distinct distinctions force two distinctions unequal, two such gadgets force them equal, and with these every relation closed under complement is a pattern of NAE knots (Böhler, Reith, Schnoor and Vollmer 2005). Checked on all 16 such relations on three distinctions. | proved; checked | P3a, P3b |
| 4 | **On the plane, life is undecidable.** For translation-invariant patterns on Z², whether the infinite pattern lives is undecidable: a tile set tiles the plane iff its NAE encoding lives (Berger 1966; known in this form, Freedman 1998). Checked on 300 random tile sets on small tori (201 tile, 99 do not; the encoding agrees and decodes). With a seed, counters and Turing machines follow (Wang 1961). | proved (known); checked | P3c |

## Answer

Nested patterns of our language cannot count, and whether they live is always decidable: each self-holding knot's inside is seen
from outside only through what it allows on its three ends, which can be one of 16 things, so the fate in depth repeats with a
period, and the top of a pattern can tell depth only modulo that period. The law itself is not what stops counting: NAE knots can
express every relation closed under complement, and on a plane-like pattern, where a part meets the rest along a boundary that grows
with it, whether the pattern lives is undecidable and counters can be built. What separates the two is the size of the interface.

## Reading

**Interpretation, not a theorem.**
- **The owner's Gödel question.** Gödel's compactness explains why the limit-only patterns live (`LIMIT-ONLY-20261112-001`).
  Incompleteness needs a system that can count; our nested patterns cannot, from their ends, because each nested knot meets its
  outside in three distinctions. A pattern can reach undecidable questions only when its parts meet along interfaces that grow, as
  on the plane.
- **Counting inside.** T2 is about windows at the top. Inside a pattern, the law's bonds between the top and a deep level can still
  grow with depth, as bond distance does on a ruler; that would be counting in the knots-alone sense, and is not decided here.

## Literature and provenance

Known: compactness (Gödel 1930); bounded-interface hierarchical graphs (Lengauer and Wanke 1988), hyperedge-replacement grammars and
MSO (Courcelle), MSO on infinite trees (Rabin 1969); Kleene iteration; the co-clone bases (Böhler, Reith, Schnoor and Vollmer 2005);
the domino problem (Wang 1961, Berger 1966), k-SAT on groups (Freedman 1998); substitution tilings with local rules (Robinson 1971,
Mozes 1989), as analogy. New in form: the statements for this language and the gadgets on distinct distinctions. Classification:
known (the mathematics), with delta (its application here).

## Workspace assumptions

A79 used (the language).

## Ratio

Substantive: the proofs and their finite checks. Administrative: the pre-registration, this note, the closure.

## Corrections

One, to the pre-registration before the proof (`docs/CORRECTIONS.md`, Not a block): the usual-limit description keeps the
pass-through calls.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — can nested patterns count? | **Status:** Successful (referee pending) | T1, T2, P3 proved: this language cannot count from its ends; growing interfaces can |
| Local direction — counting | Continue | Counting inside (bonds against depth) is the open half |
| Broader exploration — G17 | Searching | Where the extra witnesses sit is in the basket |
| Long-term goal — G1 Space from a law (with G17) | Capability gained | The interface size is what separates decidable nesting from undecidable, plane-like patterns |

**Corrections:** one, Not a block. **Goals:** a checkpoint for G17 and G1 (capability gained); no goal change. **Assumptions:** A79
used. **Basket:** `WITNESS-COUNT-20261112-001#1` (2/3 Payoff, 3/3 Concreteness), `PREFIX-END-20261112-001#2` (2/3, 3/3),
`LIFE-JUMPS-20261112-001#2` (2/3, 3/3), `LIMIT-ONLY-20261112-001#1` (2/3, 2/3), `NEST-READ-20261112-001#2` (2/3, 2/3).

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Counting inside | 3/3 — Breakthrough-scale if yes | 2/3 — Testable | In living nested families, the least bond between a top distinction and one s levels down, exactly (by the definitions' relations, not a cap), against s → bonds that grow without bound with s (the law counts depth inside, though not from the ends), or a bound | Selected · awaiting go-ahead |
| 2 | Growing interfaces in the language | 2/3 — Substantial | 2/3 — Testable | Add a definition whose calls pass one more distinction per depth and find the smallest such description that lives only by counting → a counter in a nested form, or none | Alternative · deferred |

1. Payoff 3 if bonds grow without bound: the law would count depth inside a pattern that cannot count from its ends. Concreteness 2:
   an exact method for bonds across many levels is not yet written (NEST-READ capped bonds at five).
2. Payoff 2: the nested door to undecidability. Concreteness 2: the language change is small; the counter is a construction.

**Recommendation.** Research directions, #1, awaiting the go-ahead.
