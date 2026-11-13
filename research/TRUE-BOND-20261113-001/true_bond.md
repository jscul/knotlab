# Does growth survive side branches?

Epic `TRUE-BOND-20261113-001` (`PROVED-RATE-20261113-001` direction 1; G17, with G1), 2026-11-13, at the coordinator's go-ahead.
Pre-registered with the Codex spec in commit 3709fddce before the code was written. The canonical K1–K3 test is unchanged.
**Referee pending** (handed to the referee thread).

## Words

As in the pre-registration: L(s), the least bond between a top port and an own distinction of the depth-s ray copy with members
anywhere; L_ray(s), the same along the ray only; the deficit D(s) = L_ray(s) − L(s). All readings are exact at the depths each family
reached within its limit of 1,100 seconds (the "reached depth").

## The question

Along the ray the least bond provably grows in 226 families. Once side branches may carry members of the bond, does it still grow?

## The question in standard terms

The least minimal non-shattered set through a root vertex and a depth-s vertex, over all vertices of an infinite iterated
hyperedge-replacement NAE instance, against the same along one derivation ray, for s ≤ 12.

## Conclusions

| # | Conclusion | Kind | Prediction |
| --- | --- | --- | --- |
| 1 | **The method is exact where checked.** With the depth convention settled (Codex flagged it; the thread chose the uniform truncation), the DP's bond counts by size equal direct satisfiability counts in all 33 cases (sizes through each exhausted bound, h = 2 and 3), including a family where a side branch shortens the bond (911: 3 against 4); the F-for-G mutant fails; side branches forced to G reproduce L_ray (168 of 168). | computed | G passed (after the thread settled the ambiguity) |
| 2 | **Side branches shorten the reach in at least 62 of 226 families (27%),** within the depths reached: by one member (44 families), two (9) or three (9); never lengthen it. | exact at the depths reached | P1 failed (at most 20% registered) |
| 3 | **Growth survives wherever it was read deep enough.** All 37 families that reached depth 12 have L(12) > L(6), and all 75 that reached depth 8 or more grow from depth 4 to their last. In a few the deficit itself grows (0, 1, 1, 2, 2, 3, 3 in four families: a side branch lowers the rate, from one member per level to one per two, without stopping the growth). | exact at the depths reached | P3 held on the 37 reached; not decided for the rest |
| 4 | **Most families did not reach depth 12.** 163 hit the time limit, 18 the memory limit, 6 had an incomplete ray reference, 2 errors; the reached depths were 5 or less in 112. P2 could be read on only 2 shortened families (both D(12) − D(6) = 0). | stated | P2 not decided |

## Answer

Allowing side branches does shorten the law's reach in more than a quarter of these families, by one to three members, and in a few
it lowers the rate of growth; but wherever the computation got deep enough, the reach still grows with depth. So the growth found along
the ray is not an artefact of leaving out side branches, in every family where this could be checked; for most families the depths
reached were too small to say.

## Reading

**Interpretation, not a theorem.** Side branches give the law extra routes near each level, so a bond can use a shortcut through a
branch hanging off the ray, but no route skips a level (the construction's own fact), so the reach still lengthens as depth grows.

## Lag cutoffs and census-only claims

The 226 families with provably growing ray bonds; s ≤ 12; exact values only at reached depths (1,100 seconds per family, 2.5 GB per
worker). No rate is claimed (the cost cap depends on s). Run note: the thread's first launcher skipped the last 32 families (its list
lacked a final newline); they were run afterwards with the same code (`thread_launcher_part6.sh`); all 226 have records.

## The Codex hand-off (for the owner)

- **Quality.** Codex wrote exact, carefully checked code, with independent satisfiability checks, a working mutant test and runner
  tests (killed and stuck workers, resume), and it found the shortening case the spec asked for.
- **Friction.** It flagged one real ambiguity in the spec (how deep the side branches reach in the small check cases) and left the
  gate open rather than guess; I settled it and ran the comparison myself (`thread_settled_validation.py`, 33 of 33). This time it did
  not run the long job, as planned, so nothing was lost to its session ending. My own launcher bug cost an extra 50 minutes.
- **Saved.** All the algorithmic and validation code was Codex's; my part was the spec, one settlement, the launch and the reading.

## Review

Referee pending (the referee thread). The advisor model reviewed the design cold (`advisor_review_answer.md`): it confirmed the
method's exactness, dropped an unsound rate step, and gave the pruning, the validation design and the discriminating predictions.

## Literature and provenance

Known: minimal non-shattered sets (Sauer–Shelah; Pajor), ∃∀ dynamic programming on bounded treewidth (Chen; Pan and Vardi), least
fixed points of superior functions (Knuth 1977). Not found: whether side branches shorten the law's reach in nested NAE patterns.
Classification: known-with-delta.

## Workspace assumptions

A79 used.

## Ratio

Substantive: the exact true bonds at the depths reached. Administrative: the spec, the settlement, the launches, this note.

## Corrections

None.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — does growth survive side branches? | **Status:** Partially successful (referee pending) | G passed; P1 failed (27% shortened); P3 held where read; most families not read to depth 12 |
| Local direction — counting inside | Continue | A faster method would read all families deep enough |
| Broader exploration — G17 | Searching | The full census and per-residue rates stay proposed |
| Long-term goal — G17 Typical and rare meeting patterns (with G1) | Capability gained | The law's reach grows with side branches allowed, where checked |

**Corrections:** none. **Goals:** a checkpoint for G17 and G1 (capability gained); no goal change. **Assumptions:** A79 used.
**Basket:** `PROVED-RATE-20261113-001#2` (rates per residue; 1/3 Payoff, 3/3 Concreteness), `CHEAP-COUNT-20261112-001#1` (2/3, 2/3),
`PREFIX-END-20261112-001#2` (2/3, 3/3), `LIFE-JUMPS-20261112-001#2` (2/3, 3/3), `LIMIT-ONLY-20261112-001#1` (2/3, 2/3).

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A per-level side-cost bound | 3/3 — Breakthrough-scale if it gives proved true rates | 2/3 — Testable | Prove that a side branch can save at most a fixed number of members per level, which caps the generic table independently of s and makes a minimum cycle mean sound → proved true rates for all 226, or a counter-example | Selected · awaiting go-ahead |
| 2 | Deeper reading of the slow families | 2/3 — Substantial | 3/3 — Ready | The same code with a longer limit on the 189 families not read to depth 12 → growth confirmed or a family where it stops | Alternative · deferred |

1. Payoff 3: proved growth of the true bond would show the law counts inside nested patterns. Concreteness 2: the bound is plausible
   (no level skipping) but not proved.
2. Payoff 2, Concreteness 3: compute only.

**Recommendation.** Research directions, #1, awaiting the go-ahead.
