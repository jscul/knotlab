# How the law's reach typically behaves across nested patterns

Epic `REACH-CENSUS-20261113-001` (`BOND-DEPTH-20261112-001` direction 2; G17, with G1), 2026-11-13, the coordinator's choice under
the owner's standing instruction; computed by Codex from a frozen spec. Pre-registered in commit 5605bec51, with clarifications of
Codex's flagged ambiguities in 3e7c1e0ef, both before any census result was seen. The canonical K1–K3 test is unchanged.
**Referee pending.**

## Words

As in the pre-registration. The **ray**: main's first call to the ray definition S, then S's first SELF call, repeatedly, after
every definition that does not hold itself is inlined; the copies along it are C_0 = main, C_1, C_2, …. **L_ray(s)**: the least bond
among the ray's own distinctions containing a port of main and an own distinction of C_s, in the states of the usual limit, with
every other self-holding call read by its limit relation. **By weight**: the share of the 223,261 draws (a Monte Carlo estimate of
the description weighting, A79). **Among distinct families**: exact counts of the 124,572 distinct families drawn, which overweights
heavy families and describes the sampled set. A band [low, high] counts unresolved families against a class and for it; intervals
are 95% bootstraps over draws. **Typical** means the interval's lower end is above 1/2, **common** that it is at least 5%, **rare**
that its upper end is below 1%.

## The question

Along one ray, the least bond provably grows in 226 of the 664 one-definition families alive only in the limit and is bounded in at
least 361 (`PROVED-RATE-20261113-001`). That cell is 0.3% of the weight. Across all nested draws, which reach is typical: growing with
depth, bounded, or absent? Does it differ between families that live at every depth, die with a dead limit, and live only in the
limit?

## The question in standard terms

For iterated hyperedge-replacement NAE instances sampled with probability 2^−length from a straight-line grammar: the share whose
least root-to-depth-s minimal non-shattered set along one derivation ray grows linearly, stays bounded or does not exist, decided per
family by the minimum cycle mean and an exact residue test on a finite min-plus state graph.

## Conclusions

| # | Conclusion | Kind | Prediction |
| --- | --- | --- | --- |
| 1 | **The method is exact where checked.** The replayed draws match the stored ones (G0, 0 mismatches); on the one-definition families the new code reproduces the earlier graphs, rates, every-depth tests, ray bonds at 13,598 depths and the referee's 95 exact tests (G1, 0 mismatches; at the census caps 644 of 664 comparable, all agree); a family wrapped under a new main shifts by one depth (G2, 618 of 618 under the clarified long-run class); an independent brute force over the ray's states agrees at all 1,071 depths of 139 of the 150 panel families, 65 of them with several definitions, with no disagreement; the other 11, its largest cases, did not finish within its 5-hour cap (G3, folded in after the close); every family that lives at every depth has a living usual limit (G4). | computed | gates passed (G3 on 139 of 150) |
| 2 | **Most nested weight has no depth to read: 58.4%.** Main reaches no copy (5.8%) or the ray definition has no own distinctions after inlining (52.6%), so every copy lives on the distinctions above it. Another 3.0% has no ray bond by construction (a dead limit 0.7%, own distinctions in no constraint 2.4%). These follow from the definitions and the code, not from the law. | proved (one-line arguments) | stated |
| 3 | **Absence is typical by weight, bounded reach is typical where a bond persists.** Of all weight: no ray bond at large depths 79.8% (to 80.2%); bounded 13.9%; grows 5.9%; mixed by residue below 0.01%; unresolved 0.4%. Among the computed draws that live at every depth (38.2% of the weight), none at any depth 47.0%, bounded 35.7% [35.4, 36.9], grows 15.3% [15.0, 16.4], lost at large depths 1.1%, unresolved 0.9%. Where a ray bond persists, bounded is 68.8% to 70.6% [68.3, 71.0]. | exact per family, census | P1 held, P2 held |
| 4 | **Families alive only in the limit grow about twice as often, but only because their bonds exist.** Among their computed draws (862): bounded 63.6% [60.3, 68.9], grows 32.1% [29.0, 37.5], none 0.8%, unresolved 2.1%; grows minus the forever cell's is 15.9 points (draws, unresolved against), bootstrap 2.5% quantile 12.8. *After the run (exploratory):* where a ray bond persists, growth is 29.4% to 31.2% in families that live at every depth and 32.9% to 35.0% in the limit-only cell, nearly the same; the gap is the 47% of forever families with no ray bond at any depth. | exact per family, census | P3 held |
| 5 | **The rates and bounds are few.** Growth at 1 (6,211 draws), 1/2 (5,594), 1/3 (789), 2 (345), 2/3, 1/6, 1/4 and 14 rarer rates from 1/7 to 3 members per level; bounded reach settles at 3 members (80% of bounded weight), 4 (17%), 2, 5 or 6, from depth 1 to 12. | exact per family | reported |
| 6 | **The class depends on which ray is read.** On a frozen sample of 3,000 families with a second ray (the last-call ray), the class agrees on 75.4%. Growth is the least stable: 314 of 645 families growing along the first ray are bounded along the last-call ray, 297 grow on both. | exact per family, sample | reported |
| 7 | **Stress test: most families proved to grow are bounded along another ray.** On all 224 one-definition limit-only families whose ray bond provably grows along the first ray and whose graph is complete at the census caps (`PROVED-RATE-20261113-001`'s 226 less 2 now unresolved), the last-call ray is bounded in 131 (58%), at 3 members (96), 4 (32) or 5 (3) from an onset depth of 1 to 11, with a ray bond at every depth to 30; it grows in 87, is lost in 2, absent in 1, unresolved in 3. A ray bond is a true bond, so in those 131 some copy at depth s is tied to the top by at most 5 members at every depth past the onset: the growth proved along the first ray is the distance to one copy, not to the depth. | exact per family (exact residue test) | correction (Narrowing) |

## Answer

Under the description weighting, a nested pattern typically gives the law no reach to measure: in 58% of the weight there is
nothing below the top three distinctions, and in another 21% no ray bond joins the top to deep copies. Where a ray bond does persist,
it is typically bounded, at three or four members, in about 70%, and grows linearly, mostly at one or one half member per level, in
about 30%; this holds both for families that live at every depth and for those alive only in the limit, which differ mainly in
having bonds at all. And the growth is a property of the ray read, not of depth: in most of the families where it was proved, the
copies at the same depth along another ray are reached by three to five members at every depth.

## Reading

**Interpretation, not a theorem.**
- **Counting inside is rare and target-bound.** The law counts depth inside a nested pattern only where every way down lengthens.
  Along a chosen ray it lengthens in about 6% of the weight; along both rays read, in about half of that among families that have
  two. A deep copy is usually tied to the top by a short bond through some other copy at its depth.
- **For the owner's nested parts.** The larger pattern typically holds the smaller ones close, or not at all: either a few
  distinctions tie the top to every depth, or the copies are free of the top.

## Lag cutoffs and census-only claims

The 223,261 draws of the main variant (caps: 6 definitions, 6 ports, 6 own distinctions, 12 calls); the first-call ray (the
last-call ray on 3,000 families and on the 224 growing limit-only ones); blocks of at most 12 distinctions, 300,000 graph nodes,
300 seconds per family. Unresolved: 813 draws (746 over the block size, 38 timeouts, 27 capped graphs, 2 lost to a crash). No claim
about other rays, about bonds through side branches, or about other weightings.

## The hand-off to Codex (for the owner)

- **Quality.** Codex wrote the replay, the inlined DP, the runner, the summary and an independent brute force in 35 minutes, and
  checked them carefully: G0, G1 and G4 passed first time, the runner was tested on timeouts, memory stops and interrupted output.
  It flagged eight ambiguities instead of guessing; one (G2) was a real flaw in my gate, the others reporting conventions I had left
  open. The class-only G2 mismatches it reported were exactly that flaw.
- **Friction.** One timer race in its runner (an alarm firing as it was disarmed) killed the full run at 110,262 of 124,572 families
  after about 2.5 hours; I fixed it in place (marked in `reach_dp.py`, no result changed) and resumed. Its brute force is slow on
  the largest panel families (up to 47 minutes each); G3 checked 139 of 150 within its 5-hour cap, all agreeing.
- **Saved.** All algorithmic, validation and summary code was Codex's; my part was the design, the settled classes, the
  clarifications, the launch, the stress test and the reading.

## Review

**Referee pending** (the coordinator's background referee thread). The advisor model reviewed the design cold before freezing
(`advisor_review_answer.md`): the no-depth share is definitional, P3 was not blind on the limit-only side, the conditional share's
denominator, "mixed by residue", the ray convention as a robustness check, and deeper gates; all adopted.

## Literature and provenance

Known: Karp's minimum cycle mean (1978); min-plus eventual periodicity (Cohen, Dubois, Quadrat and Viot 1983; Heidergott, Olsder and
van der Woude 2006); compactness; the exact residue test is the PROVED-RATE referee's. Ours: the settled classes (one-line, by
construction), the inlined ray for several definitions, and the shares. Classification: known-with-delta.

## Workspace assumptions

A71, A79 used; A80 added (the first-call ray), under challenge from conclusions 6 and 7.

## Ratio

Substantive: the census of 124,572 families, the alternative-ray sample and the stress test. Administrative: the spec, the
clarifications, the crash recovery, this note.

## Corrections

One, from this epic's stress test (`docs/CORRECTIONS.md`, 2026-11-13): **Narrowing**. The readings of `PROVED-RATE-20261113-001`
("the law's reach measures depth there, as on a ruler") and `BOND-DEPTH-20261112-001` ("counting inside … appears in more than a
third of the families read") took growth along the first ray for growth with depth; in 131 of the 224 a copy at the same depth on the
last-call ray is tied to the top by at most 5 members. Every proved rate and bound stands.

## Data

Run outputs, compressed: `artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/` (`families.jsonl.gz`,
one record per distinct family; `alt_families.jsonl.gz`, the 3,000 on the last-call ray; `alt_growing664_families.jsonl.gz`, the
stress test; `gate664.jsonl.gz`; `summary.json`; the run logs, including the crashed first part). Code, gates and smoke outputs:
`experiments/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/codex/` (Codex's) and its parent folder (the
thread's `g3_panel.py` and `alt_growing664.py`). The summary is `summarize.py DIR --quantile-convention linear
--bootstrap-stream-policy shared --p1-bootstrap-frame computed --p3-bootstrap-frame independent-cells` on the decompressed records.
The conditional growth shares and the unique-ray split in conclusions 4 and 6 were computed after the run from these records.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the reach census | **Status:** Successful (referee pending) | P1, P2, P3 held; G0–G2 and G4 passed, G3 on 139 of 150 with no disagreement |
| Local direction — counting inside | Continue | Growth is bound to the ray read; the reach to a whole depth decides counting |
| Broader exploration — G17 | Searching | Typical shares under one weighting are known; other weightings are untested |
| Long-term goal — G17 Typical and rare meeting patterns (with G1) | Capability gained | The typical reach of nested patterns under the description weighting is located, and mostly settled by construction |

**Corrections:** one, Narrowing (above). **Goals:** a checkpoint for G17 and G1 (capability gained); no goal change.
**Assumptions:** A79 and A71 used; A80 added, under challenge (the first-call ray).
**Basket:** `BOND-BALLS-20261111-001#2` (2/3 Payoff, 3/3 Concreteness), `LIFE-JUMPS-20261112-001#2` (2/3, 3/3),
`PREFIX-END-20261112-001#2` (2/3, 3/3), `TRUE-BOND-20261113-001#2` (2/3, 3/3), `BRANCH-DEPTH-20261112-001#2` (2/3, 2/3).

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The reach to a whole depth | 3/3 — Breakthrough-scale if growth survives | 3/3 — Ready | Let the DP choose which SELF call continues at every level (the union of the middle maps), so L(s) is the least bond to any copy at depth s along any path of copies; Karp and the exact test on the union graph, on the 224 and on the census's growing families → which still grow | Selected · awaiting go-ahead (a Codex hand-off) |
| 2 | Which families grow along every ray | 2/3 — Substantial | 2/3 — Testable | From the families of #1 that still grow, a rule in the definition's calls (how the ray call's arguments leave the ports) → a rule stated and checked, or none | Alternative · after #1 |
| 3 | Another weighting | 1/3 — Minor | 3/3 — Ready | Rerun the census on the wide variant or under shortest descriptions (A79's challenge) → whether the shares move | Alternative · deferred |

1. Payoff 3: if growth survives the least over every path of copies, the law counts depth inside these patterns with no ray chosen;
   if it does not, counting inside along copies is ruled out for the whole census. Concreteness 3: the change to Codex's DP is a
   union of maps it already builds.
2. Payoff 2: it would say what makes a pattern count. Concreteness 2: needs #1's survivors.
3. Payoff 1: a robustness check of the weighting. Concreteness 3: the code runs as is.

**Recommendation.** Research directions, #1, awaiting the go-ahead.
