# Outcomes of random meeting patterns

Epic `RANDOM-FATES-20261112-001` (G17 Typical and rare meeting patterns, with G1 Space from a law and G7; program topology, group
spacing), 2026-11-12, from the owner's question of that night. Stage 1 pre-registered in commit 507421630 and stage 2 in commit
4902ca615, each before its registered run. The canonical K1–K3 test is unchanged. Referee: ticket B and stage 2 refereed in this
session; stage 1's census refereed by the referee thread (RANDOM-FATES-R1, **confirmed with fixes**, folded in below; five
corrections logged, one Narrowing and four Not a block). The five U300 runs with a minimal contradiction are still pending
(RANDOM-FATES-A2).

## Words

The guide's glossary (`publication/knotlab/INTUITIONS.md`): sample, weighting, outcome, ends, last base, tie class, minimal
contradiction, move, horizon, step ball, newest-w growth, bond, bond distance, steps apart, shortcut, faithful. In this note a
**stretch** is a run of consecutive distinctions in order of arrival, and "the law counts along newest-four growth" means that the
least bond grows with the distance in order of arrival. The stage-2 pre-registration says "line" for the order of arrival; read it
so.

## The question

- **Where it comes from.** The owner, 2026-11-12: nothing chooses a meeting pattern, every one exists and ours is one random
  sample; "some combinations should resolve to nothing, some can go for a while then die. Others will go on forever and create sets
  like the natural numbers"; and of the ones that end, "I get some inkling this is similar to limits", with measures "just relative
  to each other".
- **The question.** Under the not-all-equal law (NAE), grow meeting patterns by random processes (each one weighting of many, A71)
  and ask: (a) which outcomes occur, and how often; (b) what the law reads off the patterns that live; (c) what the bases look like
  on the way to their end: do the law's own quantities approach a limit, or jump?

## The question in standard terms

For random 3-uniform hypergraph processes under proper 2-colouring (positive NAE-3-SAT): the step at which the hypergraph stops
being 2-colourable; the minimal non-2-colourable subhypergraph then; for the 2-colourings before it, the backbone up to global flip
and the least non-shattered vertex set, with every proper subset shattered, containing two vertices at hypergraph distance d.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Outcomes depend on how the process closes.** Uniform knots on n distinctions always end, at 2.09 to 2.16 knots per distinction (median; n = 50 to 300), as known. Growth with new distinctions and closings anywhere is still a base after 2,000 moves in every run at q ≤ 0.2, in 45% at q = 0.3 and in none at q ≥ 0.35; growth along co-knotted pairs likewise (O global: all at q ≤ 0.1, 89% at 0.2, 6% at 0.3; O local: all, 71%, none). Newest-four growth never ends (proved); newest-five and newest-six growth end in 99 to 100% of runs at q ≥ 0.5 and in 8 to 15% at q = 0.3, and end with probability one for 0 < q < 1 (proved). No process "resolves to nothing" from its first knots: the least contradiction has seven knots (the Fano pattern), and within five consecutive distinctions ten. | computed, frozen (P4 held); proved (T3, T4) | A, B |
| 2 | **Uniform patterns read as rulers until near their end** (at n = 100 to 300; *corrected 2026-11-12 after the referee: at n = 50 three quarters of the life lies inside the end's stretch, and there 7 of 30 bases have ties and 11% of pairs three steps apart are rulers*). At half and three quarters of the knots at which they end, no base has a tie, and the least bond of two distinctions d steps apart has d + 2 members for 96 to 100% of the sampled pairs at n = 200 and 300 and d = 1, 2, 3 (P1 failed only at n = 100, three quarters, d = 3: 86%, with 13% shortcuts). Where no cycle of knots is near, this is the theorem: with no cycle of knots the law reads faithfully and bond distance is steps + 1 at every distance (T1, the alternating chain). | computed, frozen (P1 failed at one size); proved (T1) | A, B |
| 3 | **The end of a uniform pattern is a jump, consistent with a fixed length in knots.** The largest tie class holds about 1/n of the distinctions until about 20 knots before the end, then 25 to 34% ten knots before, 52 to 75% five before, and 87 to 90% at the last base, at every n from 50 to 300 (medians; P2 held in all three parts; the U300 readings come from 25 runs, runs 0 to 4 pending). *Corrected after the referee:* "the same at every size" is consistent, not pinned: the share shows no trend in n (Spearman −0.23 to 0.00) and each run's onset has the same spread at every n, but the bootstrap interval for the ratio of the n = 300 to n = 100 medians is 0.33 to 3.1 at k = 10 and 0.15 to 3.7 at k = 20, so a length growing slowly, such as √n, is not excluded. Ties then reach about 4 steps, which is the whole base. Shortcuts arrive with the ties: at 50 knots before the end 11 to 27% of pairs three steps apart have a least bond below 5, at 10 knots before 97 to 99%. A minimal contradiction holds 55, 73 and 86% of the knots at n = 50, 100 and 200 (P3 held; a constant share is known, these shares are new). | computed, frozen | A |
| 4 | **Growth that keeps adding distinctions ends without a final jump, at X(0.3), X(0.35) and O at 0.2 and 0.3** (*corrected after the referee: not at X(0.5), whose growths die young, at a median of 60 knots, so that 50 knots before the end is near their start; its median share rises from 0.30 at k = 50 to 0.75 at the last base*). At the last base of X and O growth the largest tie class holds at least 10% of the distinctions in 99% of the endings (P5c held), but it is already there 50 knots before the end: medians 0.35 and 0.43 at X(0.3) and X(0.35) at k = 50 against 0.38 and 0.46 at the last base, and 0.19 to 0.22 against 0.21 to 0.27 for O at q = 0.3, while uniform patterns have 0.3 to 2% at k = 50. After the run (exploratory, 10 growths per setting): over a whole life the largest tie class of X and O growth rises in jumps at random times and the growth goes on; uniform growth ties nothing until its last 5%. Their minimal contradictions are smaller and spread out: 71 to 90 knots over 160 to 218 distinctions for X, 17 to 23 knots over about 200 to 330 for O. | computed, frozen (k = 1 to 50); exploratory (whole lives) | A |
| 5 | **Endings among the newest distinctions are local.** Newest-five and newest-six growth end by a minimal contradiction of 10 to 12 knots within 5 to 10 consecutive distinctions (corrected from 4 to 10: an index span of 4 is five distinctions) (98%, P5a held), and the largest tie class at the last base has at most 40 distinctions in 99% of them (at most 48). It is not independent of age (P5b failed: Spearman 0.61), because the youngest endings, on 5 to 20 distinctions, tie nearly all of them. | computed, frozen | A |
| 6 | **Patterns that live with closings anywhere read as rulers with no finite growth rate.** At 2,000 moves, X at q ≤ 0.2 and O global at q ≤ 0.1: least bond d + 2 for 92 to 100% of pairs at d = 1, 2, 3, except O global (0.1) at d = 3 (90%, 7% shortcuts; P6 failed there); step balls grow 43 to 150 times from radius 1 to radius 3, so the law, which follows steps here, reads no finite dimension (the literature's locally tree-like patterns). Overlap does not spoil the ruler: in O growth a quarter of the co-knotted pairs lie in two or more knots and some pair in about 30. | computed, frozen (P6 failed at one setting) | A |
| 7 | **Newest-four growth: shortcuts locally, a count far away.** At 2,000 moves, 73% (q = 0.5) and 94% (q = 0.7) of pairs two and three steps apart have a shortcut, ties reach at most 8 steps, and step balls grow by about six per step (P7 held). Far apart (stage 2, exact): with rare closings no bond spans far distinctions, the growth falling into overlapping stretches no bond spans (even with no closings: at q = 0, 50% of pairs 64 apart and 0% of pairs 512 apart share a bond); as closings fill it in, the stretches lengthen (at q ≥ 0.7, 85 to 100% of pairs 512 apart share one). Within a stretch the least bond grows linearly with distance (Q2: the ratio of increments 1.64 to 2.44 against 2 for linear growth), at a rate that falls with q, from 0.31 per distinction at q = 0 to 0.024 at q = 0.9, while steps apart grow by 0.36 at every q. It follows the places where knots are missing (Spearman 0.83 and 0.70 with open windows at q = 0.7 and 0.9); the referee found, after the run, about one bond member per 8 to 10 knots missing from the windows between the pair, at every q (exploratory). In complete stretches each distinction is tied to the one four before it, a repetition with period four, and the count does not grow there. Q1 to Q4b held. | computed, frozen (P7; Q1–Q4b); exact; refereed; one count exploratory | A, C |
| 8 | **Controls.** The pattern with no cycle of knots gave least bond d + 2 for all 720 sampled pairs and no tie (C2); every last base ties its killing knot's three distinctions equal (C1, by definition); newest-four and O global (0) growth never ended (P4a, by proof). | computed | A |

## Answer

Uniform patterns away from their end (at n = 100 to 300), and X and O growth with rare closings, read as rulers: the law's distance
follows steps apart for nearly every pair, computed (the theorem for patterns with no cycle of knots says the same of those, and these
patterns are full of cycles). Not every living pattern is tie-free: most living X(0.2) bases carry a tie (21 of 30, a class of up to
77 distinctions), and living newest-four patterns carry ties in all 60 bases read and shortcuts for 73 to 94% of pairs two and three
steps apart. *(This paragraph corrected 2026-11-12 after the referee; it said "under every weighting tried, the patterns that live
read as rulers ... and nothing is tied".)* How they end depends on the weighting. Uniform knots end
suddenly: within about twenty knots, consistent with the same number at every size, the law ties about nine tenths of the base into one class, and
the last minimal contradiction holds most of the knots. Growth that keeps adding distinctions carries large tie classes for much
of its life, built up in jumps, and ends with no jump at the end; growth that touches only its newest distinctions ends locally,
through about ten knots. Only growth among the newest four never ends, by proof, and there the law counts: its distance grows in
proportion to distance along the growth, in a unit set by how many knots are missing, except where closings are so rare that no
bond spans far stretches.

## Reading

**Interpretation, not a theorem.**
- **The owner's three outcomes, as typical.** Under these weightings "resolves to nothing" is never typical for a growing pattern
  (a single knot, or a few, always allow states); "goes for a while then dies" is typical whenever closings are frequent; and "goes
  on forever" is typical only where closings are rare or every knot is kept among the newest four.
- **Limits.** For uniform knots the end is not a limit: the law's quantities stay small and then jump, over a fixed number of knots
  however large the pattern. For growth that keeps adding distinctions the largest tie class settles at a share of the base and
  stays there before the end, which is closer to the owner's limit, though the census measured only the last 50 knots and, after
  the run, ten growths per setting.
- **The natural numbers.** The process that goes on forever has an order of arrival, which the process supplies (A71). What the
  law adds is the count along it: the least bond grows by about one member for every 8 to 10 missing knots, not for every
  distinction (exploratory), so the law counts what is open, not what is there. Where every knot is present it does not count at
  all and repeats with period four. Read with the owner's words: the law's count is of gaps, and a full stretch is a harmony.
- **Space.** No weighting tried makes a low-dimensional space typical: living patterns with closings anywhere read with no finite
  growth rate, and the one that reads with growth rate one has its order supplied by the process.

## Lag cutoffs and census-only claims

- **Proved.** T1 to T4 and C1 (ticket B), for every finite pattern; T2 also for the integers.
- **Computed.** Everything else, under the named processes and sizes: uniform knots at n = 50 to 300 (U300: 55 of 60 runs; five
  pending, below), growth to 2,000 moves, stage 2 to 800 distinctions. Bond searches at d = 3 are lens-relative for their size-5
  part, and beyond 600 distinctions also for size 4 ("none" in the summary). Stage 2's undefined pairs are relative to the margin;
  the referee found none change with members anywhere.
- **Exploratory, after the run.** The whole-life tie trajectories (`life_ties.py`, `life_ties.json`) and the missing-knot count;
  both need frozen tests.

## Stress test and pending runs

- **Pending (stress test).** The five U300 runs with a minimal contradiction did not finish in the registered run's 4-hour cap; they
  run separately (`docs/LONG_RUNNING.md`, RANDOM-FATES-A2) and fold into the U300 summary when they finish. P3 rests on n = 100 and
  200 only, as registered. Until then `summary.json` comes from `summary_guarded.py`, the frozen summary with two lines changed (the
  path it runs from, and a guard for the missing U300 core statistics; corrected from "one line" after the referee); afterwards the unchanged `census.py --summary` is the record.
- **Deviation, disclosed.** The registered run stopped at its cap with 969 of 2,990 runs written; `resume_driver.py` ran the
  frozen `census.task` on the remaining runs unchanged.
- **One size past.** Stage 2 at 1,200 distinctions (the referee) changed no least bond; T1 checked exhaustively on every pattern
  with no cycle of knots up to 8 distinctions and on random ones to 13.

## Review

- **Ticket B** (a fresh referee with its own code): T1 proved with wording fixes (made), T2, T3, T4(a), T4(b) and C1 proved,
  T4(c) false as first stated and corrected (q = 1, and histories with fewer than five distinctions); see the proof's Review.
- **Stage 2** (a fresh referee with its own code, three independent exact methods): the programme is exact (0 mismatches on 60,932
  pairs of 1,260 patterns against brute force and on 2,040 window searches on the real bases; all 2,945 returned bonds are bonds,
  974 of them larger than the frozen SAT check covered); undefined pairs stay undefined with members anywhere; the frozen bases
  regenerate exactly; Q1 to Q4b recomputed and confirmed. Fragile points it named: Q1's median sits on its bound (128), Q2's
  eligible bases are exactly seven, and the frozen Spearman breaks ties by order (tie-corrected 0.84 and 0.67, still above 0.5). It
  traced the stretches no bond spans, found a local mechanism for one end of a stretch (a pair whose two later knots are the only
  link onward), and found the missing-knot count. Its code and outputs are in `referee_C/`; ticket B's in `referee_B/`.
- **Stage 1** (the referee thread, `referee-R1/report.md`, commit a595f196c): **confirmed with fixes**. All 2,985 growths regenerate
  exactly from their seeds with the referee's own code and another solver; every quoted number recomputes; 2,146 bases re-read with
  its own reader agree on every tie summary; least bonds with an uncapped lens change no verdict (P6 at X(0.2) d = 3 0.921 to 0.929,
  Og(0.1) still 0.896, P7a 75.2% and 94.2%, C2 720 of 720, P1 1,627 of 1,632 pairs exactly and the other 5 rulers or a bond of 5 the
  capped search missed); minimal contradictions match in distribution at n = 50 and 100 (n = 200 too slow to recheck); 100 fresh
  growths per setting agree within sampling error (single shares near a boundary carry about ±5 to 10 points: O global (0.3) gave 16%
  against 6%). Its fixes are made above and logged as five corrections; its follow-up (larger n or more runs, to tell a fixed length
  from slow growth) is direction 4 below.

## Literature and provenance

- **Known.** Thresholds and phases of random NAE-3-SAT and hypergraph bicolouring (clustering, condensation and the Kesten–Stigum
  bound at 1.5 knots per distinction; the one-step value 2.107 for the end, unstable at three places; Gabrié, Dani, Semerjian and
  Zdeborová 2017; Castellani, Napolano, Ricci-Tersenghi and Zecchina 2003); freezing and rigidity (Molloy and Restrepo; Ayre and
  Greenhill); minimal contradictions of constant share (the expansion argument, Chvátal and Szemerédi 1988); backbones that jump
  at the threshold (Monasson et al. 1999 for 3-SAT) and spines (Istrate, Boettcher and Percus 2005); m(3) = 7.
- **Not found** (bounded search, by the author and both referees): bond distance (least non-shattered sets through two vertices)
  on random patterns; the outcomes of the other growth processes; the length of a single uniform growth's last stretch in knots;
  bandwidth-3 2-colourability as a statement (elementary); the least-bond theorem on Berge-acyclic patterns (close to folklore on
  tree-structured constraints and prime implicates of acyclic formulas).
- **Classification.** Known-with-delta: the thresholds and the share of the end are classical; the readings, the end's fixed length
  in knots, the outcomes of growth, and the count along newest-four growth are the delta.

## Workspace assumptions

- **Added.** A71 (each random process is one weighting of many), A72 (a growing pattern ends when it allows no state).
- **Relied on.** A67 (faithfulness read on sets of at most three; bond distance reads larger sets), A15 and A73 (the owner's
  reading of realities, which the census does not test).

## Ratio

- **Substantive.** The census (2,985 runs), stage 2 (60 bases), ticket B's four theorems, two referee passes, the whole-life
  exploration.
- **Administrative.** Two pre-registrations, this note, the closure, one correction entry.

## Corrections

Six in all (`docs/CORRECTIONS.md`, 2026-11-12). Before the close: one, **Not a block** (`docs/CORRECTIONS.md`, 2026-11-12): the pre-registration said newest-five growth ends with probability one
for q > 0; it needs 0 < q < 1. From the referee (R1), after the close: one **Narrowing** (the Answer and the owner report said every
living pattern under every weighting reads as a ruler with nothing tied, and put the theorem for patterns with no cycle of knots
beside a computed claim; the report's "the count follows the missing knots" lacked its exploratory label) and four **Not a block**
(conclusion 2 needs n = 100 to 300; conclusion 3's fixed length is consistent, not pinned, with 87 to 90% and 25 U300 runs;
conclusion 4 holds at X(0.3), X(0.35) and O at 0.2 and 0.3, not X(0.5); the guarded summary differs in two lines, and newest-w cores
lie within 5 to 10 consecutive distinctions).

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — outcomes of random meeting patterns | **Status:** Successful (refereed, confirmed with fixes) | Outcomes by process measured; the uniform end a jump of fixed length; growth with new distinctions ending with no jump; newest-four counted |
| Local direction — random samples under NAE | Continue | Two exploratory findings (whole-life jumps, the missing-knot count) need frozen tests |
| Broader exploration — G17 typical and rare | Searching | Other laws and other weightings (shortest description first) untried |
| Long-term goal — G17 Typical and rare meeting patterns (with G1) | Capability gained | The owner's three outcomes now have frequencies under named weightings, and the end's limit question an answer for uniform knots |

Stage 1's census is the epic's largest evidence family and its referee is pending; a verdict that changes a conclusion will be a
correction. The local direction continues because the two strongest new readings came after the run.

**Corrections:** one, Not a block (newest-five growth ends for certain only when 0 < q < 1). **Goals:** a G17 checkpoint (capability
gained), with G1; no goal change. **Assumptions:** A71 and A72 added and used; A67 relied on. **Basket:** this epic's directions
below (#1 recorded as sub-goal B167); the knots-alone line's folding census (G17 with G1) runs beside it and reuses this census's library read-only.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Jumps over a whole life | 3/3 — Major | 3/3 — Ready | Freeze a census of the largest tie class at every 2% of life for X, O and uniform growth at two or three sizes → the jumps' sizes, timing and any signal before the end, or none | Selected · awaiting go-ahead |
| 2 | The count of missing knots | 2/3 — Substantial | 3/3 — Ready | Freeze the referee's count as a prediction on fresh newest-four bases and on newest-four patterns made otherwise → a fixed unit of about 0.11 members per missing knot, or a count that depends on the process | Alternative · deferred |
| 3 | Other weightings | 2/3 — Substantial | 1/3 — Stated | Define a shortest-description weighting on small patterns and compare outcomes with the growth weightings → a result that changes with the weighting, or one that does not | Alternative · deferred |
| 4 | Uniform ends at larger sizes | 1/3 — Modest | 2/3 — Testable | Tie classes only (no minimal contradiction) at n = 400 to 800, or more runs (the referee's follow-up) → the end's length in knots fixed, or growing like √n | Alternative · deferred |
| 5 | The other reading of "ends" | 2/3 — Substantial | 2/3 — Testable | Measure when new knots stop changing the tie classes and least bonds, against the time of no allowed state → the two readings agree or part | Alternative · awaiting the owner's answer |

1. **Jumps over a whole life.** Payoff 3: it answers the owner's question of what the patterns that "go for a while then die" look
   like on the way, and whether the law's quantities approach a limit, for the weighting where the census found no final jump.
   Concreteness 3: the census's processes, readers and seeds are frozen and the exploration's script exists; the exploration ran
   ten growths per setting only. Resource bound: tie classes only, about an hour on ten workers.
2. **Missing knots.** Payoff 2: a unit for the count along the one process that never ends. Concreteness 3: the exact programme and
   the formula are ready.
3. **Other weightings.** Payoff 2: tests A71 directly. Concreteness 1: the weighting is not yet defined.
4. **Larger uniform sizes.** Payoff 1: confirms a known-in-spirit jump. Concreteness 2: solver cost grows fast past 300.
5. **The other reading.** Payoff 2: the owner's second meaning of "die". Concreteness 2.

**Recommendation.** Research directions, #1, awaiting the coordinator's go-ahead; #2 is small enough to run beside it.

## Final report as sent

Sent to the owner on 2026-11-12 at 08:20 UTC, in the project thread:

> **Outcomes of random meeting patterns: done.** Here is what is typical under each random process. A pattern that lives reads as an exact ruler away from its end. A pattern of uniform knots ends in a sudden jump. Growth that keeps adding distinctions builds up its ties over its life. Growth among the four newest distinctions never ends, and along it the law counts.
>
> | Scope | Verdict | Why |
> | --- | --- | --- |
> | This attempt: outcomes of random meeting patterns | **Status:** Successful (census referee pending) | Outcomes measured by process. The uniform end is a jump of fixed length. Growth that adds distinctions has no final jump. Newest-four growth is counted |
> | Local direction: random samples under not-all-equal | Continue | The two strongest readings came after the run and need frozen tests |
> | Broader exploration: G17 typical and rare | Searching | Other laws and a shortest-description weighting are untried |
> | Long-term goal: G17 Typical and rare meeting patterns (with G1) | Capability gained | Your three outcomes now have frequencies under named weightings. The limit question has an answer for uniform knots |
>
> - **Living patterns are rulers.** Away from an end, two distinctions d steps apart share a least bond of d + 2. That is a theorem wherever knots form no cycle. There is no finite dimension, and heavy overlap doesn't spoil it.
> - **Uniform knots end in a jump, not a limit.** Nothing is tied until about 20 knots before the end. Then the law ties 87 to 89% of the base into one class, over the same number of knots at every size from 50 to 300.
> - **Growth that adds distinctions has no final jump.** Its tie classes rise in jumps during its life, and they already hold 20 to 45% of the base 50 knots before the end. That is the closest thing to your limit so far, but it rests on an exploratory run of only ten lives per process.
> - **"Goes on forever": only among the newest four, by proof.** The law counts along that growth, with a distance that grows in proportion. The count follows the missing knots. Where every knot is present, it repeats with period four. When closings are rare, no bond links distant stretches at all.
> - Frozen predictions: 4 of 7 held fully; P1, P5 and P6 failed in part. Stage 2's 5 of 5 held.
>
> **Next step:** Research directions. Selected: #1
>
> | # | Direction | Payoff | Concreteness | First step → stop when | Status |
> | --- | --- | --- | --- | --- | --- |
> | 1 | Jumps over a whole life | 3/3 Major | 3/3 Ready | Tie classes at every 2% of life for growth and uniform knots → limit or not | Selected · awaiting go-ahead |
> | 2 | The count of missing knots | 2/3 Substantial | 3/3 Ready | Freeze the unit of about 0.11 per missing knot → fixed, or depends on the process | Alternative · deferred |
> | 3 | Other weightings | 2/3 Substantial | 1/3 Stated | Shortest description first, on small patterns → results change or not | Alternative · deferred |
> | 4 | Uniform ends at larger sizes | 1/3 Modest | 2/3 Testable | Ties only at 400 to 800 → fixed length or not | Alternative · deferred |
> | 5 | The other meaning of "die" | 2/3 Substantial | 2/3 Testable | When new knots stop changing what the law reads → agrees with the end or not | Alternative · awaiting your answer |
>
> **Corrections:** one, Not a block. Newest-five growth ends for certain only when closings happen less than always.
> **Goals:** G17 checkpoint, capability gained, with G1 and G7. No goal change.
> **Assumptions:** A71 (each process is one weighting of many) and A72 (ends = no allowed state) were added and used.
> **Basket:** #1 is sub-goal B167. The folding census reuses this library read-only.
> **Pending:** the census referee, and five slow uniform runs (descriptive only). The advisor model designed stage 2's exact method and reviewed its predictions.

The advisor model (Fable 5.2) was consulted on analysis twice, under the owner's rule of 2026-11-12: for the exact method of stage 2
(its design is `bonddp.py`'s) and on stage 2's draft predictions before they were frozen; and once on wording (tie class, minimal
contradiction, move, horizon, step ball, newest-w growth).
