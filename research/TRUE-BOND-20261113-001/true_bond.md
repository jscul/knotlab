# Does growth survive side branches?

Epic `TRUE-BOND-20261113-001` (`PROVED-RATE-20261113-001` direction 1; G17, with G1), 2026-11-13, at the coordinator's go-ahead.
Pre-registered with the Codex spec in commit 3709fddce before the code was written. The canonical K1–K3 test is unchanged.
Refereed by the referee thread (TRUE-BOND-R1, `referee-R1/report.md`, commit 0e741e63d): **confirmed with fixes**; six corrections
logged (**one Block**, two Narrowing, three Not a block).

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
| 3 | ~~**Growth survives wherever it was read deep enough.**~~ *Corrected after the referee (Block and Narrowing):* all 37 families that reached depth 12 have L(12) > L(6), and all 75 that reached depth 8 or more grow, but these are mostly families where side branches change nothing (only 2 of the 37 and 9 of the 75 are shortened; shortening makes the computation slower, so the deep-read set is biased), and the shortened ones grow by about one member over six to eight levels. In four families (269, 302, 642, 908) the true bond is **flat at 3 through depth 7** while the ray bond rises to 6: no growth is observed there, the strongest evidence against growth surviving. ~~"a side branch lowers the rate … without stopping the growth"~~ is withdrawn. | exact at the depths reached | P3 undecided on its registered denominator |
| 4 | **Most families did not reach depth 12.** 163 hit the time limit, 18 the memory limit, 6 had an incomplete ray reference, 2 errors; the reached depths were 5 or less in 112. P2 could be read on only 2 shortened families (both D(12) − D(6) = 0). | stated | P2 not decided |

## Answer

Allowing side branches shortens the law's reach in more than a quarter of these families, by one to three members. Where the
computation got deep, the reach still grows, but those are mostly families where side branches change nothing; in four families the
true bond stays at 3 to depth 7 while the ray bond doubles, so side branches may make the reach bounded there. Whether growth survives
side branches is therefore open, with four candidate counter-examples. *(Corrected after the referee.)*

## Reading

**Interpretation, not a theorem.** Side branches give the law extra routes near each level, so a bond can use a shortcut through a
branch hanging off the ray. No route skips a level (the construction's own fact), but that does not make the reach lengthen: the four
flat families show that side branches can carry the constraint down at no cost per level. *(The inference first written here is
withdrawn after the referee.)*

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

**TRUE-BOND-R1** (the referee thread with Codex): the object is right (the closed side table is the true bond with members at any
depth; the uniform truncation only in the finite gate); the cost cap hides nothing; a fresh satisfiability recomputation gives all 48
minima at h ≥ 2 equal to the recorded L; "never lengthens" is a consistency check (L ≤ L_ray by construction). Families 248 and 1288
failed with a SystemError in the bond search (cause not recorded). The advisor model reviewed the design cold (`advisor_review_answer.md`): it confirmed the
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

Six, from the referee (`docs/CORRECTIONS.md`, 2026-11-13): **Block**, the growing-deficit sentence (the four families are flat, not
slower); **Narrowing**, the deep-read set is biased and P3 undecided; **Narrowing**, the Reading's inference; **Not a block**, two
SystemErrors; **Not a block**, roster and P1 as reported; **Not a block**, the gate stands.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — does growth survive side branches? | **Status:** Partially successful (refereed, one Block) | G passed; P1 failed (27% shortened); P3 undecided; four candidate counter-examples |
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
