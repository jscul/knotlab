# Does the law's reach grow along every descending path: pre-registration

Epic `EVERY-RAY-20261113-001` (`REACH-CENSUS-20261113-001` direction 1, reframed; G17, with G1), 2026-11-13, at the coordinator's
go-ahead. Computed by Codex from `codex_spec.md`, run by the thread. Frozen before any result was seen. The canonical K1–K3 test is
unchanged. Law: not-all-equal on three-place knots.

## The question

`REACH-CENSUS-20261113-001` found the least bond along one chosen ray (the first SELF call at each level) grows in about 30% of the
families with a persisting bond, and a stress test found 131 of 224 one-definition growers bounded along the last-call ray. So growth
along one ray is not growth with depth. Reading every descending path of copies: for how many families is the reach bounded along
**some** path, and does any family grow along **every** path (so that depth is genuinely a bond distance, with nothing chosen)?

## In standard terms

The minimum, over all descending chains of self-substitutions, of the least root-to-depth-s minimal non-shattered set, in the
satisfying assignments of an iterated hyperedge-replacement NAE family, decided per family by the minimum cycle mean of a min-plus
graph whose step is a minimum over which self-call continues.

## The object and its bounds (frozen in the spec)

L_path(s): the least bond over all descending paths, members on the chosen copies' own distinctions. The census ray DP with the
middle step a minimum over which SELF call of S continues. Bounds, settled: **L_any ≤ L_path ≤ L_ray** and **L_any ≤ L_true**, where
L_any is the free-target, members-anywhere bond (the deferred follow-on), L_ray the census first ray, L_true the TRUE-RATE bond to
the first-ray copy with members anywhere. So **L_path bounded ⇒ L_any bounded** (decisive for L_any's boundedness only; it says
nothing about λ_true, since a different copy at depth s may be near while the first-ray copy stays far). **L_path grows** means
grows along every path with members on it — an upper-bound reading of "counts depth", and only on an uncapped (complete) graph.

## Settled by construction (stated, not tested)

- **One self-call, one path.** A family whose S has one SELF call (c = 1) has one ray: L_path = L_ray, already in the census. Among
  families with a persisting first-ray bond, 16,895 of about 42,000 distinct have c = 1 (5,803 of the growers). The question is
  non-empty only for c ≥ 2.
- **Path-independent settled classes.** S1 (dead limit), S2 (no copy) and S3 (no own distinctions of S) hold on every path. S4 is
  **not** path-independent and is recomputed over all paths (an own distinction may be free against the first call but constrained
  against another).
- **Trivial equalities.** If two SELF calls are duplicates or images of each other under a port symmetry of S, they give the same
  ray, so L_path = L_ray with no new content; a grower over paths counts as genuine only when its calls are inequivalent.
- **L_path ≤ L_ray** at every depth (the min includes the first ray): a gate, not a prediction.

## Reporting and words

By count (exact) and by A79 draw weight (bands and a 95% bootstrap over draws), among families with a persisting bond on some path,
split by first-ray class and by c. "Bounded along some path" is **decisive for L_any's boundedness only**. "Grows along every path"
is an upper-bound reading and is asserted only on complete graphs; a capped, timed-out or over-block family is unresolved, never a
grower. Finite readings are "within depth N".

## Predictions (frozen)

The advisor model reviewed the design cold (`advisor_review_answer.md`); its points are adopted: the "decisive" wording is
L_any-only; the population includes families with a bond on a non-first path; pass-through calls are stratified; the caps never make
a grower; P3 moved to the gates; P2 restated for symmetry-inequivalent calls; P1 given a threshold and evaluated outside the 224;
the mixed-path count added; the brute force flattens the unfolding; panel depth is preperiod plus period.

| # | Prediction | Fails when |
| --- | --- | --- |
| P1 | **First-ray growth is usually defeated by another path.** Among c ≥ 2 families that grow along the first ray, L_path is bounded in at least 75% by count, and a majority by weight; evaluated both on all of them and **excluding the 224 one-definition growers** (where 131/224 is already known). | below 75% by count, or not a weight majority, on the set excluding the 224 |
| P2 | **Some family grows along every path.** At least one c ≥ 2 family with symmetry-inequivalent SELF calls has λ_path > 0 on a complete graph. The count is reported; one-self-call growers trivially grow along their one ray and are reported separately. | none |
| P3 | **A bond appears only off the first ray for some family.** At least one family with no first-ray bond (census class none or lost) has a persisting bond over paths. | none |
| — | Reported: over-paths classes by cell; λ_path; the mixed-path count; pass-through-cycle count; symmetry-inequivalent growers; unresolved by c; the count newly bounded over paths. | — |

## Gates

G-reg (c = 1 reproduces the census graph, λ, class — a regression check, not validation). G-last (L_path ≤ the last-call and
first-call rays on the 224, recomputed here). G-brute (an independent flattened-unfolding brute force with `knotlab check`,
reproducing L_path to preperiod-plus-period on a 120-family stratified panel, ≥20 with c ≥ 3). G-node (the three DP-soundness cases).
Any G-last, G-brute or G-node failure invalidates the run.

## Stop rule

One Codex hand-off (code, gates, smoke); one full run launched by the thread (registered in `docs/LONG_RUNNING.md`); its frozen
summary; a referee hand-off; report. The free-target, members-anywhere L_any is the deferred follow-on (a sub-goal), bounded above
by both L_path and TRUE-RATE's λ_true.

## Clarification before any result (2026-11-13, while Codex builds; no result seen)

`TRUE-RATE-20261113-001` found that 99 of the census's 131 last-call-bounded families carry a top port down that ray by identity, so
the bond's top member is a port of every copy and the bond is local at each depth (A81, under challenge). `BRANCH-DEPTH-20261112-001`
had seen the same case on the first branch. A bounded verdict is therefore split, computed in the reading by the thread on Codex's DP
(not a change to the frozen classes or predictions):

- **Port maps.** A SELF call with arguments (a_0, a_1, a_2) maps the child's port j to the parent's port a_j when a_j is a port.
  Along a path, T_s ⊆ {0, 1, 2} is the set of C_s's port positions that hold a port of main: T_0 = {0, 1, 2} when main is S (for
  main ≠ S, T_1 is the positions where the entry call passes a port of main), and T_{k+1} = {j : a_j ∈ T_k} for the call chosen.
  The path is **carried** at depth s when T_s is not empty, **uncarried** when it is empty (and then it stays empty).
- **The split.** The min-over-paths DP with the node extended by T (eight values), accepting at depth s only with T_s empty, gives
  L_path^unc(s). A family bounded over paths is **bounded, uncarried** when L_path^unc is eventually bounded (the exact residue test
  on the extended graph), otherwise **bounded, carried only**. The census's first-ray classes are split the same way along the first
  ray.
- **Reading.** P1 is reported as frozen, and next to it on uncarried boundedness. Only uncarried boundedness says the reach is
  genuinely short: a carried bond never crosses depth. Still open: one of main's own distinctions carried down by identity forever
  could also keep a bond local. It is not tested here and is stated as a limitation.

## Second clarification, after Codex's first hand-off (2026-11-13; gate results seen, no class share)

Codex's first hand-off (`handoff1_snapshot/`) built the DP and flagged eight ambiguities. Its G-last gate failed in 6 of 82 families,
at depth 1 or 2: L_path exceeded the last-call ray. The cause was a flaw in my spec. "Start block unchanged" fixed the first step to
main's first call, so the minimum did not run over every path. The fix and answers to all eight ambiguities are frozen in
`codex_spec_addendum.md`:
- the start chooses the entry too;
- G-brute enumerates every path's ray CNF, with stated depths and endpoints;
- fixed-index rays are (entry, call) pairs;
- equivalent calls are duplicates or images under a port permutation that fixes the block's allowed states;
- the population and its bootstrap over the whole archive are fixed;
- the carried T-extension is to be built by Codex.

The predictions and classes are unchanged. G-last's earlier failures are kept as evidence of the flaw.

## Third clarification: a frozen sample in place of the census (2026-11-13, no class share seen)

Codex's second hand-off (`codex_spec_addendum.md`) built the free start and the carried extension. It was stopped by its time cap at
204 of 300 smoke families, before G-brute. It flagged two more gaps: G-reg against the free start, and G-brute's ordering. Timing:
mean 58 s per family, with 15% of families stopped by the 300 s cap, so the 32,315 eligible families would take days. The advisor
reviewed the replacement design cold (`advisor_review_answer_2.md`); its points are adopted.

- **Strata** (`sample_paths.py`, one `Random(20261114)` stream over sorted keys), by the census's first-ray class:
  - **G**, 300 first-ray growers (6,925 eligible, excluding the 224 one-definition growers, which run in full as G-last).
  - **N**, 200 first-ray none-or-lost families (6,469).
  - **B**, 100 first-ray bounded families (18,281). They are bounded over paths by construction (L_path ≤ L_ray), so only
    their carried split is open, and it is reported as description only.
- **Phase 2.** Every G and N family left unresolved by a cap is run again at 1,000 s and 1,000,000 nodes. Families stopped by
  memory stay unresolved.
- **Estimates.** Count shares are sample proportions, with Wilson 95% intervals. Weight shares weight each sampled family by its
  draws; they are near the count shares here (6,989 draws on 6,925 growers). Unresolved families count against a class (low) and
  for it (high). The 5% undecided rule is dropped, because the bands already carry the unresolved.
- **P1, the verdict reading.** The count share of bounded-over-paths among sampled G families with at least two inequivalent SELF
  calls. Families whose calls are all equivalent grow by construction (L_path = L_ray), so they are reported separately.
  - **Holds** if the low band's Wilson lower end is at least 75%.
  - **Fails** if the high band's Wilson upper end is below 75%.
  - Otherwise **undecided**.
  - The weight majority, the uncarried reading and G-last's 224 are reported beside it, not as the verdict.
- **P2, P3.** These are existence claims, confirmed by any sampled instance; they cannot be refuted by a sample. "Not found" bounds
  the share below about 1.5% at n = 200. P3 is existential over paths: a family is a hit when some path keeps a bond at large
  depths (a bondless path enters the minimum as INF), and a cap does not block a hit.
- **Uncarried.** L_path^unc ≥ L_path, so uncarried-bounded implies bounded. "None at any depth" on the uncarried graph includes
  families with no uncarried path at all.
- **Gates.**
  - G-reg is judged on families with one SELF call and one entry, where the free start changes nothing.
  - G-last runs on all 224.
  - G-brute's panel is the completed 300-family smoke ordered by largest block, then the sum of block sizes (`max_then_sum`).
  - The completed smoke, a uniform sample of eligible families, is reported as description only.

## Deviation before G-brute (2026-11-13 22:4x UTC, before any brute-force result)

The smoke could not be finished: the runner rightly refused to add rows from the timer-patched code to rows from the code before
the patch. G-brute's panel source is therefore a 300-row composite of the frozen sample, the first 150 of stratum G and the first
150 of stratum N in selection order (`codex/sample/brute_panel_source.jsonl`). Codex's `run_brute.py` chooses the panel from it as
frozen (`max_then_sum`). G-reg is judged as clarified, on families with one SELF call and one entry.
