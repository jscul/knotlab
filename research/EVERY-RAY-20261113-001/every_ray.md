# Does the law's reach grow along every descending path

Epic `EVERY-RAY-20261113-001` (`REACH-CENSUS-20261113-001` direction 1, reframed; G17, with G1), 2026-11-13, at the coordinator's
go-ahead. Code by Codex in two hand-offs, run by the thread on a frozen stratified sample. Pre-registered in efea48eec, with
clarifications in 5e003342c (the carried split), b90bd7ff3 (the start step and eight ambiguities), 1bb68cfab (the sample) and the
G-brute deviation, all before any class share was seen. The canonical K1–K3 test is unchanged. Refereed by the referee thread with
Codex (EVERY-RAY-R1, `referee-R1/report.md`, commit 180fcc5d3): **confirmed with fixes**. The per-depth result and P1 to P3 stand.
Four sentences were false (Block on each sentence) and three statements are narrowed; all are folded in below and logged.

## Words

A **descending path** chooses, at every level, which SELF call of the ray definition S makes the next copy (the start chooses
main's entry too). **L_path(s)**: the least bond over all descending paths between a port of main and an own distinction of the
depth-s copy, members on the path's own distinctions, side calls by their limit relations. **Uncarried**: along the path no top port
is a port of the depth-s copy (A81); L_path^unc counts only such paths. **Bounded over paths**: L_path eventually bounded (exact
residue test). Strata are the census's first-ray classes: **G** first-ray growers, **N** first-ray none or lost, **B** first-ray
bounded, all with two or more SELF calls.

## The question

Along the first ray the bond grows in about 30% of the families with a persisting bond (`REACH-CENSUS-20261113-001`). Is that growth
with depth, or the choice of ray? For how many is the reach bounded along **some** path, and does any family grow along **every**
path?

## The question in standard terms

The minimum over all descending chains of self-substitutions of the least root-to-depth-s minimal non-shattered set, in an iterated
hyperedge-replacement NAE family, decided per family by a min-plus graph whose step is a minimum over which self-call continues.

## Conclusions

| # | Conclusion | Kind | Prediction |
| --- | --- | --- | --- |
| 1 | **The method is exact where checked.** G-last: on all 224 one-definition first-ray growers L_path ≤ both the first-call and the last-call ray at every recorded depth, 181 checked with no failure (43 stopped by caps), including the 7 that failed under the first spec's fixed start. G-reg: on 491 of 500 one-self-call families the graph equals the census's; the other 9 have two or three entries, where the free start rightly changes the graph, with class and λ unchanged. G-node: the three soundness cases agree. G-brute (independent per-path enumeration, no DP code): no disagreement at any of the 462 depths compared completely in 98 of 120 panel families (45,668 paths enumerated; 19 more finished with some paths over 22 distinctions, 3 stopped by its one-hour budget); the panel came from the sample (classes bounded 45, grows 12, none 51, unresolved 12; 48 with three or more SELF calls), and only 22 had several definitions, short of the 40 asked. | computed | G-last, G-reg (as clarified), G-node passed; G-brute no disagreement, several-definition quota short |
| 2 | **First-ray growth is mostly undone, depth by depth.** Of 296 sampled first-ray growers with inequivalent SELF calls, 204 are bounded over paths **per depth**: for each sufficiently large depth, some finite path, possibly depending on the depth, has a short bond (68.9%, to 77.7% with the 26 unresolved; Wilson 63.4% to 82.1%). *Corrected after the referee:* 200 of the 204 are bounded without a carried top port, 3 have no uncarried bond, and 1 was unresolved (now certified uncarried by the referee, 201 of 204), so the uncarried band is 200/296 to 227/296 (Wilson 62.0% to 81.1%). A single infinite path with a bounded uncarried bond (a lasso: entry, prefix, repeated call word) is certified in 188 families, 185 of them at every depth; in 13 none was found. In 50 of the 204 no fixed entry-and-call ray is bounded (37 of these have a certified lasso). The plain certified bounds (`uniform_cost_bound`) run from 2 to 14 members, 97 at 3; the referee's exact per-depth uncarried bounds are 3 (26), 4 (169) and 5 (6). The 4 families with only equivalent calls are all bounded. | exact per family, sample | P1 undecided (75% inside the band) |
| 3 | **Some families grow along every path, in the per-depth sense.** The per-depth minimum over all paths grows (proved per family on complete graphs) in 66 of the 300 growers (λ_path 1, 1/2, 1/3 or 2 members per level), 62 of them on uncarried paths too; 79 symmetry-inequivalent growers in G and N. In this sample, more SELF calls, fewer of them: among resolved families 31% grow at two calls, 27% at three, none at four, 15% at five or more. | exact per family, sample | P2 held |
| 4 | **A bond appears off the first ray.** 33 of 200 first-ray none-or-lost families (16.5%; Wilson 12.0% to 22.8%) have a persisting bond over paths: 20 bounded, 13 growing. | exact per family, sample | P3 held |
| 5 | **Bounded first-ray families are mostly bounded without a carried port over paths.** Of the 100 sampled, 55 bounded uncarried, 15 only through a carried port, 30 unresolved on the uncarried graph (description only; *corrected after the referee*: 20 had been written for 15 carried-only plus 5 unresolved). | exact per family, sample | reported |

## Answer

Growth of the law's least bond along one chosen ray is mostly a choice of ray. In this sample, among the families whose bond grows
along the first ray and that have a real choice of path, about seven in ten have, **for each sufficiently large depth, some finite
path (possibly depending on the depth) whose bond to that depth is short**, and in all but a handful without a top distinction
carried into the copies. In 188 of these one infinite path does it at once (a certified lasso); the per-depth minimum does not imply
this in general (the referee's family `[[3,2,[["K",[1,3,4]],["SELF",[2,0,4]],["SELF",[0,3,4]]]]]` has a per-depth minimum of 3 to 4,
while every single infinite path's bond grows). About a fifth to three tenths of the sample still grow per depth over every path,
mostly at one or one half member per level, fewer as the number of self-calls rises. The
registered threshold (three quarters) lies inside the uncertainty band, so the frozen prediction is undecided. And bonds the first
ray misses exist on other paths in about a sixth of the families with none there.

## Reading

**Interpretation, not a theorem.**
- **Depth is usually not a bond distance along copies.** Where a pattern can descend in more than one way, at each depth some way
  usually reaches it through a fixed handful of distinctions (in this sample; the way may change with the depth). The law counts depth along every path only in a minority of these families,
  and in families with one self-call, where there is only one path.
- **What remains open.** L_path keeps the bond's members on one path. The bond with members anywhere and any target copy, L_any
  (B172), is at most L_path, so every bounded verdict here holds for it; whether the growers here still grow there is open, as is
  whether side branches shorten them (`TRUE-RATE-20261113-001`).

## Lag cutoffs and census-only claims

A frozen stratified sample of the 32,315 eligible families (two or more SELF calls, not S1–S3): G 300 of 6,925 (excluding the 224
one-definition growers), N 200 of 6,469, B 100 of 18,281 (`Random(20261114)`). Blocks of at most 12 distinctions, 300,000 nodes,
300 s and 3 GB per family; a second phase at 1,000 s and 1,000,000 nodes resolved 2 of 29 capped G and N families (most stopped by
memory). No census-wide shares; no claim about members off the path, side branches, or other weightings. Prevalence statements are
about this frozen sample. *After the referee:* the timer patch's equivalence is uncontradicted but not tested by these data (B and
B_resume are disjoint, and the phase-2 overlaps ran one DP version).

## The hand-off to Codex (for the owner)

- **Quality.** Codex wrote the min-over-paths DP, the carried extension, the symmetry test, the runner, the gates and an independent
  per-path brute force, reusing the census code, and checked them with synthetic controls. Across two hand-offs it flagged ten
  ambiguities rather than guessing; one was a real flaw in my spec (the start step was fixed, so the minimum did not run over every
  path), which its own G-last gate exposed.
- **Friction.** Both hand-offs ran out of session time on long validations; I stopped the first and resumed from the second's code.
  The new DP is slow (mean 58 s per family, 15% capped), so I replaced the census-wide run with a frozen sample. A timer race (an
  alarm escaping the timeout handler) crashed one stratum at 25 of 100; I fixed it in place (marked in `paths_dp.py`) and the
  runner kept the code versions apart. The 3 GB memory stop, not the time cap, limited the second phase.
- **Saved.** All algorithmic and validation code was Codex's; my part was the spec and its three clarifications, the sampling
  design, the runs, the patch and the reading.

## Review

**EVERY-RAY-R1** (the referee thread with Codex, fresh code that opened none of the study's Python): the per-depth result reproduces.
It certified 201 of 204 bounded families uncarried (12,180 comparisons, no disagreement) and 188 single-path lassos. It checked the DP on
18 more several-definition families by direct enumeration (no disagreement) and found the bands and G-reg sound. It also found four false
sentences and three statements to narrow, all fixed above. Its note on bounds: L_true ≤ L_path does not hold in general, since the
targets differ. The advisor model reviewed the design twice cold
(`advisor_review_answer.md`, `advisor_review_answer_2.md`); all its points were adopted.

## Literature and provenance

Known: Karp's minimum cycle mean (1978); min-plus eventual periodicity; the exact residue test (PROVED-RATE's referee). The members-
anywhere bond to a **fixed** first-branch target was read by `BRANCH-DEPTH-20261112-001`, `TRUE-BOND-20261113-001` and
`TRUE-RATE-20261113-001`; the carried artefact is A81. Not found in the records: the minimum over descending paths. Ours: that object,
its DP, and the shares. Classification: known-with-delta.

## Workspace assumptions

A79 used; A80 (the first-call ray) overturned for growth by conclusion 2; A81 used.

## Ratio

Substantive: the sample of 600 families and the gates. Administrative: two hand-offs, three clarifications, the sampling redesign,
the crash recovery, this note.

## Corrections

*Corrected after the referee:* not none. Logged in `docs/CORRECTIONS.md` (2026-11-13): four **Block** entries, one per false sentence
(the single-path reading of the Answer; the carried-only labels; the bounds sentence; the pre-registration's justification that
equivalent calls give L_path = L_ray), none touching P1 to P3 or the per-depth minima; and three **Narrowing** (REACH-CENSUS's
"another ray seldom contradicts first-ray growth", now naming the last-call ray and citing this result; the timer patch's
equivalence untested; sample and depth qualifiers on prevalence and on "grow along every path"). Before the referee: A80 is overturned
for growth, but every published growth claim resting on it (`BOND-DEPTH-20261112-001`,
`PROVED-RATE-20261113-001`, `REACH-CENSUS-20261113-001`, and the first-ray targets of `TRUE-BOND-20261113-001` and
`TRUE-RATE-20261113-001`) is already stated along the first ray, with the ray and carried-port qualifiers in place, so none is wrong
as stated.

## Data

`experiments/EVERY-RAY-20261113-001A/EVERY-RAY-20261113-001A-E001_min_over_paths/`: `codex/` (Codex's code, gates in
`codex/gates_full/`, the sample's rows in `codex/sample/`), the thread's `sample_paths.py`, `sample_B_resume.py`, `read_sample.py`
and `sample_reading.json`, and the first hand-off's snapshot.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — every descending path | **Status:** Partially successful (refereed, confirmed with fixes) | P2, P3 held; P1 undecided (69% to 78% bounded against a 75% threshold); gates passed, the brute force with no disagreement |
| Local direction — counting inside | Narrowed | First-ray growth is mostly a choice of path; a minority grows along every path |
| Broader exploration — G17 | Searching | Whether the remaining growers count depth with members anywhere is open (B172) |
| Long-term goal — G17 Typical and rare meeting patterns (with G1) | Capability gained | The law's reach across paths of copies is measured on a frozen sample |

**Corrections:** seven (four Block on sentences, three Narrowing; above). **Goals:** a checkpoint for G17 and G1 (capability gained); no goal change. **Assumptions:** A80 overturned
for growth; A79, A81 used. **Basket:** `BOND-BALLS-20261111-001#2` (2/3 Payoff, 3/3 Concreteness), `LIFE-JUMPS-20261112-001#2`
(2/3, 3/3), `PREFIX-END-20261112-001#2` (2/3, 3/3), `TRUE-BOND-20261113-001#2` (2/3, 3/3), `B172` (3/3, 2/3).

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The every-path growers with members anywhere | 3/3 — Breakthrough-scale if any still grows | 2/3 — Testable | On the 66 sampled growers over paths, the least bond to any copy at depth s with members anywhere (B172's L_any, the side-summary table of `TRUE-RATE-20261113-001` combined with the min over paths) → whether any nested pattern has a growing L_any, or none | Selected · awaiting go-ahead |
| 2 | What makes a pattern grow along every path | 2/3 — Substantial | 2/3 — Testable | From the 66 and the bounded ones, a rule in the SELF calls' port maps and own distinctions (the share falls with the number of calls) → a rule stated and checked on a fresh sample, or none | Alternative · after #1 |
| 3 | Why limit-only patterns more often have a bond | 2/3 — Substantial | 2/3 — Testable | Compare the call structure of limit-only and forever families with no ray bond at any depth → a structural reason, or none | Alternative · deferred |
| 4 | Decide P1 | 1/3 — Minor | 3/3 — Ready | Rerun the 26 unresolved growers with a larger memory cap → P1 holds or fails | Alternative · deferred |

1. Payoff 3: if a pattern's bond still grows with members anywhere and any target, the law counts depth inside it with nothing chosen; if none does, counting inside along copies is ruled out here. Concreteness 2: both DPs exist, their combination does not.
2. Payoff 2: what makes a pattern count. Concreteness 2: needs a rule to state.
3. Payoff 2: the census's limit-only cell differs mainly in having bonds at all. Concreteness 2.
4. Payoff 1: a threshold. Concreteness 3: the code runs as is.

**Recommendation.** Research directions, #1, awaiting the go-ahead.
