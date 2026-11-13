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
