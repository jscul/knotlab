# The late hopping rules, read deeper

Epic `LATE-HOP-20261112-001` (`TWO-BIT-ROWS-20261112-001` direction 1; G17, with G1), 2026-11-12, at the coordinator's go-ahead.
Pre-registered in commit 935b83962 before the registered run. The canonical K1–K3 test is unchanged. Refereed by the referee thread
(LATE-HOP-R1, `referee-R1/report.md`, commit 8b61b48d3): **confirmed with two wording fixes**, folded in below (both Not a block). Read together with `TWO-BIT-ROWS-20261112-001`'s referee report (folded into that record the same day).

## The question

Do the five hopping rules that changed late, and the other late rules, settle, keep a period, or keep changing to depth 200, and are
late changes tied to where the last generation's length passes a power of two?

## The question in standard terms

For 35 NAE rules on growing generations (two variables per position): eventual periodicity of satisfiability and of the projection
onto the first generation up to depth 200.

## Conclusions

| # | Conclusion | Kind | Prediction |
| --- | --- | --- | --- |
| 1 | **The five settle.** Three die at depth 21 or 31 and stay dead; one dies at 41 (after its first-generation relation alternates at depths 35 to 40, *corrected after the referee*) and stays dead; one's first-generation relation changes at 31 and then holds. | exact, depth ≤ 200, frozen | L1 held |
| 2 | **Nothing keeps changing except by alternating.** All 35 rules are, by depth 200, constant, eventually constant (the latest from depth 47, rule 28's death after changes every three depths), or alternating with period 2 (20 hopping and 2 flat harmonies). No other period and no unexplained sequence occurs. | exact, depth ≤ 200, frozen | reported |
| 3 | **L2 fails, for a reason built into it.** Its frozen statement asked every change after depth 40 to sit near a power-of-two length; the period-2 harmonies change at every depth, so it fails on them. Apart from the alternations, the changes after 40 are rule 9's death at 41 and rule 28's: its first-generation relation changes in pairs every three depths from 17 (17, 18, 20, 21, …, 41, 42, 44, 45) until it dies at 47, none at a power-of-two length. *(Corrected after the referee: "one rule's settling at 47" was a death at 47 after a period-3 run of changes.)* | exact, frozen | L2 failed |

## Answer

The late hopping rules are long transients, not counters: each settles, at the latest by depth 47, and nothing to depth 200 changes
except harmonies that alternate every depth. With `TWO-BIT-ROWS-20261112-001`'s referee: those harmonies mostly come from the one
position that reads itself through the hop (position 0, whose half is itself), and without it hopping needs six knots for a harmony
against flat reach's ten, about 2.5 times more common, not 11; and harmonies already exist in the nested language with three-
distinction ends. So two distinctions per position add neither counting nor, by themselves, keeping time.

## Reading

**Interpretation, not a theorem.** Hopping reach changes how cheaply a pattern keeps time, a little; it does not make the law count.
Counting in these growths is the known additive mechanism (`ROW-NEST-20261112-001`'s referee), which needs fresh distinctions and
constrained ends.

## Lag cutoffs and census-only claims

35 frozen rules, depths 1 to 200. No claim beyond 200 or for other rules.

## Review

**LATE-HOP-R1** (the referee thread, confirmed): two wording fixes, made above. No advisor review: the readings and classes are TWO-BIT-ROWS's, with longer bounds.

## Literature and provenance

Known: long transients and settling of local rules (threshold maps, Goles and Olivos 1980). Classification: known-with-delta.

## Workspace assumptions

None new.

## Ratio

Substantive: the deep read. Administrative: the pre-registration, this note, the closure.

## Corrections

Two from the referee (`docs/CORRECTIONS.md`, Not a block): rule 28's changes after 40 were undercounted, and rule 9 alternates at
depths 35 to 40; the same "35 to 37" in `TWO-BIT-ROWS-20261112-001`'s note and its correction entry is fixed there.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the late hopping rules, deeper | **Status:** Partially successful (refereed, confirmed) | L1 held; L2 failed as stated, on the harmonies: long transients, not counters |
| Local direction — keeping time and counting | Practically exhausted at this richness | Two distinctions per position add neither; counting needs fresh distinctions and constrained ends (known) |
| Broader exploration — G17 | Paused | The coordinator will take stock with the owner |
| Long-term goal — G1 Space from a law (with G17) | Capability gained | Where these growths can and cannot count is mapped |

**Corrections:** none here. **Goals:** a checkpoint for G17 and G1 (capability gained); no goal change. **Assumptions:** none new.
**Basket:** `TWO-BIT-ROWS-20261112-001#2` (the cheapest counter; 2/3 Payoff, 2/3 Concreteness), `NEST-COUNT-20261112-001#1` (counting
inside; 3/3, 1/3), `PREFIX-END-20261112-001#2` (2/3, 3/3), `LIFE-JUMPS-20261112-001#2` (2/3, 3/3), `LIMIT-ONLY-20261112-001#1`
(2/3, 2/3), `NEST-READ-20261112-001#2` (2/3, 2/3).

**Next step:** Research directions — none selected; paused for the owner.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The cheapest counter | 2/3 — Substantial | 2/3 — Testable | The fewest NAE knots, with fresh distinctions, that build an additive rule and a closed boundary, and its weight → a count of knots and a weight | Awaiting the owner |
| 2 | Counting inside | 3/3 — Breakthrough-scale if bonds grow without bound in typical families | 1/3 — Exploratory | An exact least-bond method across levels → typical growth of bonds with depth, or a bound | Awaiting the owner |

**Recommendation.** Pause, as asked; when work resumes, #1 is the cheaper and more concrete.
