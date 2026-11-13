# How the law's reach typically behaves across nested patterns

Epic `REACH-CENSUS-20261113-001` (`BOND-DEPTH-20261112-001` direction 2; G17, with G1), 2026-11-13, the coordinator's choice under
the owner's standing instruction; computed by Codex from a frozen spec. Pre-registered in commit 5605bec51, with clarifications of
Codex's flagged ambiguities in 3e7c1e0ef, both before any census result was seen. The canonical K1–K3 test is unchanged.
Refereed by the referee thread with Codex (REACH-CENSUS-R1, `referee-R1/report.md`, commit d4cbc40ff): **confirmed with fixes**, folded
in below; six corrections logged (five Narrowing, one Not a block), one of them the thread's own after the referee.

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
| 1 | **The method is exact where checked.** The replayed draws match the stored ones (G0, 0 mismatches); on the one-definition families the new code reproduces the earlier graphs, rates, every-depth tests, ray bonds at 13,598 depths and the referee's 95 exact tests (G1, 0 mismatches; at the census caps 644 of 664 comparable, all agree); a family wrapped under a new main shifts by one depth (G2, 618 of 618 under the clarified long-run class); an independent brute force over the ray's states agrees at all 1,071 depths of 139 of the 150 panel families, 65 of them with several definitions, with no disagreement; the other 11, its largest cases, did not finish within its 5-hour cap (G3, folded in after the close); every family that lives at every depth has a living usual limit (G4). *After the referee:* its fresh recomputation agrees on 49 families (147 satisfiability checks at s = 1 to 3, classes, cycle means, residue verdicts and L_ray to depth 30), 37 with several definitions and seven with blocks of 12; so large several-definition blocks are validated only at shallow depth. | computed | G0–G2 and G4 passed; G3 on 139 of 150; large several-definition blocks checked only at shallow depth |
| 2 | **Most nested weight has no depth to read: 58.4%.** Main reaches no copy (5.8%) or the ray definition has no own distinctions after inlining (52.6%), so no eligible endpoint lies at increasing depth. Another 3.0% has no ray bond by construction (a dead limit 0.7%, own distinctions in no constraint 2.4%). These follow from the definitions and the code, not from the law. | proved (one-line arguments) | stated |
| 3 | **Absence is typical by weight, bounded reach is typical where a bond persists.** Of all weight: no ray bond at large depths 79.8% (to 80.2%); bounded 13.9%; grows 5.9%; mixed by residue below 0.01% of the classified weight (its band reaches 0.37%); unresolved 0.4%. Among the computed draws that live at every depth (38.2% of the weight), none at any depth 47.0%, bounded 35.7% [35.4, 36.9], grows 15.3% [15.0, 16.4], lost at large depths 1.1%, unresolved 0.9%. Where a ray bond persists, bounded is 68.8% to 70.6% [68.3, 71.0]. *After the referee (the thread's own split, `carried_split.json`; **unrefereed, a short referee check R2 pending**):* 82% of the bounded weight is **carried**: the first ray passes a top port into every copy by identity, so its bond is local at each depth and does not cross depth. On uncarried persisting bonds, growth is 63% to 68% and bounded 32% to 37% (families that live at every depth; 59% to 64% and 37% to 41% in the limit-only cell). | exact per family, census | P1 held as frozen (mostly carried), P2 held |
| 4 | **Families alive only in the limit grow about twice as often, mostly because their bonds exist.** Among their computed draws (862): bounded 63.6% [60.3, 68.9], grows 32.1% [29.0, 37.5], none 0.8%, unresolved 2.1%; grows minus the forever cell's is 15.9 points (draws, unresolved against), bootstrap 2.5% quantile 12.8. *After the run (exploratory):* where a ray bond persists, growth is 29.4% to 31.2% in families that live at every depth and 32.9% to 35.0% in the limit-only cell, close but still apart; most of the gap is the 47% of forever families with no ray bond at any depth. | exact per family, census | P3 held |
| 5 | **The rates and bounds are few.** Growth at 1 (6,211 draws), 1/2 (5,594), 1/3 (789), 2 (345), 2/3, 1/6, 1/4 and 14 rarer rates from 1/7 to 3 members per level; bounded reach has a certified upper bound of 3 members (80% of bounded weight), 4 (17%), 2, 5 or 6, from an onset depth of 1 to 12 (a bound, not always the least value). | exact per family | reported |
| 6 | **The class depends on which ray is read.** On a frozen sample of 3,000 families with a second ray (the last-call ray), the class agrees on 75.4%. Growth is the least stable: 314 of 645 families growing along the first ray are bounded along the last-call ray, 297 grow on both. *After the referee:* in 283 of the 314 the last-call ray carries a top port by identity; only 31 are bounded without one. | exact per family, sample | reported |
| 7 | **Stress test: some families proved to grow are bounded along another ray.** On all 224 one-definition limit-only families whose ray bond provably grows along the first ray and whose graph is complete at the census caps (`PROVED-RATE-20261113-001`'s 226 less 2 now unresolved), the last-call ray is bounded in 131 (58%), at 3 members (96), 4 (32) or 5 (3) from an onset depth of 1 to 11, with a ray bond at every depth to 30; it grows in 87, is lost in 2, absent in 1, unresolved in 3. *Reworded after the referee (Narrowing):* in 99 of the 131 the last-call ray carries a top port by identity (77 as a fixed point, 22 through a cycle of ports), so its bounded bond is local at each depth and reach should not be read from it. In at least 32 of the 224 another ray reaches depth s with at most five members without carrying a top port, so growth along the first ray is not growth with depth there. | exact per family (exact residue test; carried split by the referee and the thread) | correction (Narrowing) |

## Answer

Under the description weighting, a nested pattern typically gives the law no reach to measure: in 58% of the weight no eligible
endpoint lies at increasing depth, and in another 21% no ray bond joins the top to deep copies. Where a ray bond persists along the
first ray, it is bounded in about 70%, but mostly because the ray carries a top port into every copy, so the bond is local at each
depth. Set those aside and the picture turns: on uncarried bonds the reach grows linearly, mostly at one or one half member per level,
in about two thirds, and is genuinely short in one third, in families that live at every depth and in those alive only in the limit
alike (this carried split of the first-ray classes is the thread's own, made after the referee's pass; R2 pending). Growth along the first ray is mostly not undone by another ray: in at least 32 of the 224 families where it was proved,
another ray reaches depth s within five members without carrying a top port, and in 99 more it does so only by carrying one.
*(Rewritten after the referee.)*

## Reading

**Interpretation, not a theorem.**
- **Counting inside is uncommon by weight but usual where a genuine bond exists.** Along a chosen ray the reach lengthens in about
  6% of the weight. Among the bonds that do cross depth (uncarried), lengthening is the majority, and it survives the second ray
  read in about 95% of the sampled growers once carried ports are set aside. Whether it survives every path of copies is
  `EVERY-RAY-20261113-001`'s question.
- **For the owner's nested parts.** Where the larger pattern holds the smaller ones close, it usually does so by sharing a top
  distinction with every copy, not by a short chain of constraint. Where no distinction is shared, each level usually adds to the
  distance, as a count would. *(Rewritten after the referee; the carried split it rests on awaits R2.)*

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
  after about 2.5 hours; I fixed it in place (marked in `reach_dp.py`) and resumed: the 110,262 rows computed before the patch were
  kept and the other 14,310 computed after it. The patch changes only how the timer is disarmed. The referee checked that the
  prefix's summary, recomputed from the final rows, equals the unread partial summary in all 1,830 counts and bands, so no result
  changed in aggregate; the per-family pre-patch rows cannot be compared. (My hand-off note to the referee said "reran from scratch";
  that was wrong.) Its brute force is slow on
  the largest panel families (up to 47 minutes each); G3 checked 139 of 150 within its 5-hour cap, all agreeing.
- **Saved.** All algorithmic, validation and summary code was Codex's; my part was the design, the settled classes, the
  clarifications, the launch, the stress test and the reading.

## Review

**REACH-CENSUS-R1** (the referee thread with Codex, fresh code that never read the study's folder): the computations reproduce,
including the several-definition path at shallow depth, the classes on 49 families, every headline share from a replay of the
223,261 draws and certificates for all 131 last-call bounds. Its fixes are made above: the ray correction reworded for the carried
ports (99 local by identity, 32 genuine; also found by `TRUE-RATE-20261113-001`, A81), large several-definition blocks validated only
at shallow depth, four small overstatements, and the crash a resume. Two more points needed no change: the shares are of draws and
worded consistently, and the 813 unresolved are handled as registered (inside the bands, below the 5% undecided level). The 70/30
split is not settled by construction. After the referee the thread split the census's own first-ray classes by carried ports
(`carried_split.py`), which narrows the Answer's reading of boundedness. The advisor model reviewed the design cold before freezing
(`advisor_review_answer.md`); all its points were adopted.

## Literature and provenance

Known: Karp's minimum cycle mean (1978); min-plus eventual periodicity (Cohen, Dubois, Quadrat and Viot 1983; Heidergott, Olsder and
van der Woude 2006); compactness; the exact residue test is the PROVED-RATE referee's. Ours: the settled classes (one-line, by
construction), the inlined ray for several definitions, and the shares. Classification: known-with-delta.

## Workspace assumptions

A71, A79 used; A80 added (the first-call ray), under challenge from conclusions 6 and 7 (restated after the referee); A81 (a bond may start from a carried port, `TRUE-RATE-20261113-001`) bears on conclusions 3, 6 and 7.

## Ratio

Substantive: the census of 124,572 families, the alternative-ray sample and the stress test. Administrative: the spec, the
clarifications, the crash recovery, this note.

## Corrections

Seven in `docs/CORRECTIONS.md` (2026-11-13). At the close, one from the stress test (**Narrowing**: the "ruler" readings of
`PROVED-RATE-20261113-001` and `BOND-DEPTH-20261112-001`). After the referee, five Narrowing and one Not a block:
- **Narrowing.** That correction was mostly an identity artefact. 99 of its 131 are local by a carried top port and 32 are genuine.
  It is reworded in place in both notes; it stays a Narrowing on condition that the ruler reading is never used without the ray and
  carried-port qualifiers.
- **Narrowing.** Bounded reach where a bond persists is mostly a carried top port (82% of bounded weight). This one is the thread's
  own, found after the referee's pass and **unrefereed** (R2 pending).
- **Narrowing.** Large several-definition blocks are validated only at shallow depth.
- **Narrowing.** "Only because their bonds exist": the conditional bands still differ.
- **Narrowing.** Three wordings: mixed below 0.01% is of classified weight, "settles at 3" is a certified upper bound, and "nothing
  below the top three distinctions" means no eligible endpoint at increasing depth.
- **Not a block.** The crash was a resume, and no result changed in aggregate only.

Every proved rate and bound stands.

## Data

Run outputs, compressed: `artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/` (`families.jsonl.gz`,
one record per distinct family; `alt_families.jsonl.gz`, the 3,000 on the last-call ray; `alt_growing664_families.jsonl.gz`, the
stress test; `gate664.jsonl.gz`; `summary.json`; the run logs, including the crashed first part). Code, gates and smoke outputs:
`experiments/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/codex/` (Codex's) and its parent folder (the
thread's `g3_panel.py` and `alt_growing664.py`). The summary is `summarize.py DIR --quantile-convention linear
--bootstrap-stream-policy shared --p1-bootstrap-frame computed --p3-bootstrap-frame independent-cells` on the decompressed records.
The conditional growth shares and the unique-ray split in conclusions 4 and 6 were computed after the run from these records; the
carried-port split (conclusions 3, 6, 7) by `carried_split.py` after the referee, into `carried_split.json` (it reproduces the
referee's 99/32 on the 224).

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the reach census | **Status:** Successful (refereed, confirmed with fixes) | P1, P2, P3 held (P1 mostly by carried ports); gates passed with large blocks checked only at shallow depth |
| Local direction — counting inside | Continue | On uncarried bonds growth is the majority and mostly survives a second ray; every path decides it (`EVERY-RAY-20261113-001`) |
| Broader exploration — G17 | Searching | Typical shares under one weighting are known; other weightings are untested |
| Long-term goal — G17 Typical and rare meeting patterns (with G1) | Capability gained | The typical reach of nested patterns under the description weighting is located, and mostly settled by construction |

**Corrections:** seven (above): six Narrowing, one Not a block. **Goals:** a checkpoint for G17 and G1 (capability gained); no goal change.
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
