# What the law reads along a nested pattern's levels

Epic `NEST-READ-20261112-001` (`SHORT-DESC-20261112-001` direction 1; G17, with G7), 2026-11-12, at the coordinator's go-ahead.
Pre-registered in commit c3467c1df before the registered run. The canonical K1–K3 test is unchanged. **Referee pending** (handed to
the referee thread).

## Words

As in the pre-registration: the two variants (**through the knot**: an inner pattern shares distinctions with the outside only
through the knot that holds it; **direct**: it also shares others), **constraining** and **monotone** families (whether a
self-holding definition allows on its ports less than its holding knot), **tied** families, a distinction's **level**, the least
bond L, steps apart d, a **tie-free shortcut** (3 ≤ L ≤ 5, L < d + 2). The weighting is SHORT-DESC's description code, conditioned
on the selection (A79, A71).

## The question

In a pattern where a knot holds its definition's pattern inside itself, level below level, does the law bond a top distinction to
distinctions many levels down through a few others, and does that grow, hold or die with level, in both variants of the owner's
open question?

## The question in standard terms

For satisfiable positive NAE-3-SAT instances from iterated hyperedge replacement: the least minimal non-shattered set (up to 5)
through a root vertex and a vertex created at replacement depth s, against hypergraph distance and s.

## Conclusions

| # | Conclusion | Kind | Prediction |
| --- | --- | --- | --- |
| 1 | **Control.** No pair in a pattern without a cycle of knots breaks L = d + 2 within five. | computed | gate passed |
| 2 | **Monotone families mostly follow the steps, but not entirely.** In monotone families with a cycle, 93% of pairs one to three steps apart are bonded within five, and 11.3% of pairs four or more apart, above the registered 10%. | computed, frozen | P2 failed (far share) |
| 3 | **Constraining families reach beyond the steps twice as often.** Tie-free shortcuts: 20% of pairs against 10% in monotone families with a cycle (difference 0.100, 0.066 to 0.131). Through the knot, 45% of pairs four or more steps apart are bonded within five (46% at five steps and 37% at six), where uniform patterns of the same size have none at five or six. | computed, frozen | P3 held |
| 4 | **Influence holds with level.** Against a uniform pattern at the same steps apart, the share of tie-free bonds within five neither grows nor dies with level in constraining families (mean slope −0.001 per level, −0.005 to 0.003). The raw share falls (from 0.70 at level 1 to 0.52 to 0.58 at levels 8 to 11, through the knot), because steps apart grow. Every level read, up to 11, keeps a top distinction bonded within five to about half or more of its sampled distinctions. | computed, frozen | P4 held (hold) |
| 5 | **Through the knot, influence passes as ties; directly, it passes by nearness.** Through the knot, 35% of constraining families tie ports of their definition and 17% of pairs are tied, at every level read; directly, almost none (2 families). Sharing directly keeps deep distinctions within about two steps of the top, so at levels 4 and deeper 0.21 more pairs (0.15 to 0.26) are tie-free bonded within five than through the knot; at the same steps apart (four), through the knot more pairs are bonded within five (0.55 against 0.37). | computed, frozen | reported |
| 6 | **Nested patterns are bonded less at short range than uniform ones.** One to three steps apart, 84 to 94% against 98 to 99%, as SHORT-DESC found them less tied. | computed, frozen | reported |

## Answer

Yes: in a nested pattern a top distinction stays bonded through at most three others to distinctions at every level read, down to
eleven, and this holds with level once distance is accounted for. Where the inside constrains its ends more than a knot does, the
law reaches beyond what the steps allow twice as often as where it does not. Through the knot that reach is carried mostly by ties,
which the self-holding definition repeats at every level. Sharing directly gives more bonds deep down, but by keeping deep
distinctions near the top, not by reaching past the steps.

## Reading

**Interpretation, not a theorem.**
- **The owner's (a).** Influence passes between levels non-locally: through a few others, a top distinction meets the eleventh
  level about as often as its steps would predict at the first, and in constraining families often past its steps. Within what was
  read it holds; it neither grows nor dies.
- **The owner's (b).** The two variants pass influence differently. Through the knot, the inner pattern acts on the outside only
  through what it allows at the knot's three distinctions, and when that is a tie the tie repeats at every level. Directly, the inner
  pattern is near the outside, so it is bonded by nearness. Both carry influence down; only the first carries it past the steps.
- **Settled against measured.** Steps apart are set by the substitution; ties forced by a tied definition are counted apart; what is
  measured is the tie-free reach beyond steps and its level trend against a uniform pattern at the same steps apart.

## Lag cutoffs and census-only claims

Computed on 960 constraining and 480 monotone families (8 workers per variant), each read at the largest depth with at most 60
distinctions; the selection keeps slow-growing, mostly chain-like families with levels to 11 (keep rates: through the knot 480 of
6,061 constraining and 240 of 1,813 monotone families tried, directly 480 of 4,701 and 240 of 1,298; most others had fewer
than four levels). Bonds exact up to five members. No claim
past level 11 or for fast-growing families.

## Review

Referee pending (the referee thread). The advisor model reviewed the design cold before freezing (`advisor_review_answer.md`): it
showed that ties alone could pass the draft's tests, that the cap restated the control on patterns without cycles, and that level and
steps apart are confounded; the tie-free shortcut, the cyclic-only P2, the excess slope and the band rule are its.

## Literature and provenance

Known in kind: hierarchical instances and their port relations (Lengauer and Wanke 1988); correlations along hierarchical lattices
under renormalization (Berker and Ostlund 1979); bonds as least non-shattered sets (`RANDOM-FATES-20261112-001`). Not found in a
bounded search: how far influence passes between levels of self-substituting NAE patterns. Classification: known-with-delta.

## Workspace assumptions

A71, A79 used, unchanged.

## Ratio

Substantive: the census of 1,440 families and 23,618 pairs. Administrative: the pre-registration, this note, the closure.

## Corrections

None.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — what the law reads along a nested pattern's levels | **Status:** Partially successful (referee pending) | P3, P4 held; P2 failed narrowly (11.3% against 10%) |
| Local direction — influence across levels | Continue | Ties carry it through the knot; whether it holds at every depth is exact for tied definitions and open for the rest |
| Broader exploration — G17 | Searching | Patterns alive only in the limit are in the basket |
| Long-term goal — G17 Typical and rare meeting patterns (with G7) | Capability gained | Influence passes between levels of a logic fractal and holds with level |

**Corrections:** none. **Goals:** a G17 checkpoint (capability gained, with G7); no goal change. **Assumptions:** A71, A79 used.
**Basket:** `SHORT-DESC-20261112-001#2` (patterns alive only in the limit), `OLD-CORE-20261112-001#2`, `LIFE-JUMPS-20261112-001#2`.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Patterns alive only in the limit | 2/3 — Substantial | 3/3 — Ready | Characterize the families that die at a finite depth while their limit lives by their relation maps, and test the rule on fresh families → a rule, or none | Selected · awaiting go-ahead |
| 2 | Untied reach at every depth | 2/3 — Substantial | 2/3 — Testable | For untied constraining definitions, follow the least bond to depth s exactly by the definition's relation on its ports and one level's distinctions → a bound that holds at every depth, or a depth where it fails | Alternative · deferred |

1. Payoff 2: the exact form of the owner's "similar to limits". Concreteness 3: the relation maps are computed.
2. Payoff 2: it would turn "holds within eleven levels" into a statement at every depth. Concreteness 2: the exact method is not
   yet written.

**Recommendation.** Research directions, #1, awaiting the go-ahead.
