# Two distinctions per position

Epic `TWO-BIT-ROWS-20261112-001` (`ROW-NEST-20261112-001` direction 1; G17, with G1), 2026-11-12, at the coordinator's go-ahead.
Pre-registered in commit 902871068 before the registered run. The canonical K1–K3 test is unchanged. Refereed by the referee thread
(TWO-BIT-ROWS-R1, `referee-R1/report.md`, commit 9a98e4cc0): **confirmed with fixes**, folded in below; three corrections logged (one
Narrowing, two Not a block). Read deeper in `LATE-HOP-20261112-001`.

## Words

As in the pre-registration: **generations** growing by one position, two distinctions per position, a **rule** of knots on relative
distinctions, **flat** reach (neighbouring positions) and **hopping** reach (old position ⌊i/2⌋, non-neighbouring), the **closed**
last generation, the first generation's relation, and the classes **constant**, **eventually constant**, **harmony**, **unexplained
within 40**. `ROW-NEST-20261112-001`'s referee showed that a class without fresh distinctions and with free ends cannot show the known
additive counters; this class has the same two limits.

## The question

With two distinctions per position, what is the fewest knots that make life or the first generation depend on depth with a period (a
harmony) or without one within depth 40, how rare is each under short descriptions, and does hopping reach differ from flat?

## The question in standard terms

For NAE rules on growing generations of two-variable positions, with neighbour or halving reach and a closed last generation:
whether satisfiability and the projection onto the first generation are eventually periodic in depth up to 40.

## Conclusions

| # | Conclusion | Kind | Prediction |
| --- | --- | --- | --- |
| 1 | **Harmonies appear, and hopping makes them cheaply.** With hopping reach two knots suffice: two of the 1,596 hopping rules with one or two knots make the first generation's relation alternate with period 2 from depth 1 (for example: old position i's first distinction, old ⌊i/2⌋'s second and new i's second in one knot; old i's second, old ⌊i/2⌋'s first and new i's first in the other). Flat reach needs ten knots (2 of 4,000 drawn rules; none of the 7,260 with one or two). Weight given to harmonies: 0.12% hopping, 0.011% flat. Periods seen: 2 (22 rules), 3 (1). *After the referee: the two-knot hopping harmonies come from position 0, whose half is itself, so the rule reads one old position through both reaches and its two knots make position 0 a bit that flips every generation; dropping only the knots at position 0 removes both and 16 of the 21 hopping harmonies. Without that self-reading position hopping needs 6 knots against flat's 10, and its weight falls to about 0.028% against 0.011%, roughly 2.5 times, not 11.* | exhaustive for one or two knots; drawn above | P1 held |
| 2 | **Five hopping rules are unexplained within depth 40, none flat.** By the frozen rule this fails P2. *Read after the run:* every one changes late and then holds: three die at depth 21 or 31 and stay dead, one's first-generation relation changes at depths 2, 21 or 31 and then stays, and one settles into period 2 from depth 35. *Corrected after the referee and `LATE-HOP-20261112-001`: that last one alternates only at depths 35 to 37 and dies at 41; all five settle, by depth 41.* They are long transients or late harmonies, which the classifier (a period holding from depth 20 or earlier) cannot see; none is shown to count. | drawn, census frozen; inspected after the run | P2 failed (as frozen) |
| 3 | **Most rules settle at once.** Given the drawn rules, 77% (flat) and 81% (hopping) have constant life; a quarter (flat) and a third (hopping) are dead at depth 40, all early. | drawn | reported |

## Answer

Two distinctions per position are enough to keep time: harmonies appear, where life or what the first generation allows alternates
with depth. They are rare under short descriptions, and hopping reach, where a new position meets the old one at half its index,
makes them with two knots and ten times more often than neighbouring reach, which needs ten knots. *(After the referee: the two-knot
case is the self-reading position 0; without it, six knots and about 2.5 times. Harmonies already exist in the nested language with
three-distinction ends, 264 of `LIMIT-ONLY-20261112-001`'s 223,261 families having relations that cycle with period 2 to 4, so
keeping time is not what two distinctions add.)* Nothing in this class was shown to
count: the five rules the classifier could not explain change late and then hold. Counting in this kind of growth is known to need
fresh distinctions and constrained ends (additive rules), which this class, like the last, does not have.

## Reading

**Interpretation, not a theorem.**
- **For the owner's picture.** Hopping reach, a new part's knots meeting a part far back at half its position, makes harmonies
  somewhat more cheaply than neighbouring reach (six knots against ten, once the self-reading position is set aside); the cheapest
  case first reported was that self-reading position, not far reach (the referee's).
- **Late changes.** Changes at depths 21, 31 and 35, after long quiet stretches, are what a hop to half the index could produce as
  the generations' length passes new halvings; whether they continue to count is not decided at depth 40.

## Lag cutoffs and census-only claims

All rules with one or two knots (7,260 flat, 1,596 hopping) and 4,000 drawn per variant with three to thirty knots; depths 1 to 40;
first generation of two positions. No claim beyond depth 40, for wider reach, fresh distinctions or constrained ends.

## Review

**TWO-BIT-ROWS-R1** (the referee thread, confirmed with fixes): all 1,596 hopping rules with one or two knots, the two harmonies and
the five late rules reproduce; the construction matches the pre-registration; its fixes are made above. No advisor review this time: the design reused `ROW-NEST-20261112-001`'s reviewed classifier
and closing generation (stated in the pre-registration).

## Literature and provenance

Known: additive cellular automata count in binary (Martin, Odlyzko and Wolfram 1984), threshold maps settle (Goles and Olivos 1980),
the domino problem. Not found: the fewest NAE knots that make a harmony in growing generations, flat against hopping. Classification:
known-with-delta.

## Workspace assumptions

A79's kind of code used for the weighting.

## Ratio

Substantive: the census of 16,856 rules. Administrative: the pre-registration, this note, the closure.

## Corrections

Three, from the referee (`docs/CORRECTIONS.md`, 2026-11-12): **Narrowing**, the two-knot hopping harmony is the halving map's fixed
point at position 0, not far reach; **Not a block**, one late rule was misread after the run; **Not a block**, harmonies already exist
with three-distinction ends.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — two distinctions per position | **Status:** Partially successful (refereed, confirmed with fixes) | P1 held; P2 failed as frozen, by five late changes not shown to count |
| Local direction — keeping time | Continue | The late hopping rules need deeper reading; the cheapest counter with fresh distinctions is unbuilt |
| Broader exploration — G17 | Paused | The owner asked to pause after this study for the referee verdicts |
| Long-term goal — G1 Space from a law (with G17) | Capability gained | Hopping reach keeps time with two knots |

**Corrections:** none. **Goals:** a checkpoint for G17 and G1 (capability gained); no goal change. **Assumptions:** none new.
**Basket:** `NEST-COUNT-20261112-001#1` (counting inside; 3/3 Payoff, 1/3 Concreteness), `WITNESS-COUNT-20261112-001#1` (2/3, 3/3),
`PREFIX-END-20261112-001#2` (2/3, 3/3), `LIFE-JUMPS-20261112-001#2` (2/3, 3/3), `LIMIT-ONLY-20261112-001#1` (2/3, 2/3),
`NEST-READ-20261112-001#2` (2/3, 2/3).

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The late hopping rules, deeper | 3/3 — Breakthrough-scale if they count | 3/3 — Ready | Read the five rules, and every hopping rule with a change after depth 15, to depth 200 → changes at depths tied to the generations' halvings (counting by hops), or settling | Selected · awaiting go-ahead |
| 2 | The cheapest counter | 2/3 — Substantial | 2/3 — Testable | The fewest NAE knots, with fresh distinctions, that build an additive rule and a closed boundary, and that description's weight (`ROW-NEST-20261112-001`'s referee) → a count of knots and a weight | Alternative · deferred |

1. Payoff 3 if they count: counting by hops, with a handful of knots, is the owner's nested picture keeping a number. Concreteness 3:
   the census runs as is with a larger depth.
2. Payoff 2: the known mechanism's price under short descriptions. Concreteness 2: the gadget construction is mapped, not built.

**Recommendation.** Research directions, #1, awaiting the go-ahead; paused for the referee verdicts first.
