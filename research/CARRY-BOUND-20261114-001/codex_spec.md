# Codex specification: window certificates for the non-forgetting growers (CARRY-BOUND-20261114-001A)

You are computing, not designing. Follow this exactly. If anything is ambiguous or seems wrong, do not resolve it. Write the
question in `REPORT.md` under "Ambiguities", choose nothing silently, and skip only the affected part.

## Rules

- Work from the repository root `/home/jscul/p-vs-np-contact-first`. Write files **only** inside
  `experiments/CARRY-BOUND-20261114-001A/CARRY-BOUND-20261114-001A-E001_window/codex/` (CODEX below). Modify, move or delete no
  other file. Run no git command that changes anything.
- Use `.venv/bin/python -B`, at most 2 processes at a time and at most about 8 GB in total during your session. Touch no process
  you did not start.
- Use only repository material.
- **Use the shared runner** (`scripts/longrun.py`, read `docs/tooling/shared-runner.md`). Write the jobs, run the gates on their
  own families, `launch --prepare-only` and a 20-case smoke with `run --foreground --limit 20`, then stop. Do **not** launch the
  full runs; the thread does.

## Read first

`research/CARRY-BOUND-20261114-001/preregistration.md` (the object, the lemmas, the methods, the gates and predictions; it is
frozen, and this spec implements it). `research/CARRY-BOUND-20261114-001/advisor_review2_answer.md` (the review behind the repairs).

## Inputs (read-only; reuse, do not copy)

- **Population and verdicts.** `experiments/CENSUS-FORGET-20261114-001A/CENSUS-FORGET-20261114-001A-E001_forget_census/full/results.jsonl`
  (per family: `R_i` hex, `verdict`, `chain`, `c`, `r`, `semigroup`). The population is every record with `chain` false and
  `verdict` in {non-forgetting, capped}: 5,964 families. Weights: draw counts per key in
  `experiments/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/codex/draws.jsonl.gz`.
- **Scope.** The criteria of `research/CENSUS-FORGET-20261114-001/referee-R1/codex/target_inventory.py`: out of scope when another
  self-holding definition reachable from main or S has inlined own distinctions, or when another self-holding definition reachable
  from main or S can reach S (delayed S). Reimplement these two predicates in CODEX (they are short) and check them against that
  file's `target_inventory.json` counts where it reports them.
- **Strata.** `experiments/TIE-CYCLE-20261114-001A/TIE-CYCLE-20261114-001A-E001_ties/ties.py` (`classify_full(R_i)`: tie cycle,
  idempotent types) and FORGET-RULE's identity cycle (edges j → k when the k-th argument of a SELF call of S is port j; a directed
  cycle among ports 0 to 2). I = identity cycle; T = tie cycle without identity cycle; O = no tie cycle and some order-type idempotent
  only; X = the rest, including capped classifications.
- **The family machinery.** `experiments/FREE-TARGET-20261114-001A/FREE-TARGET-20261114-001A-E001_free_target/codex/` (`inputs.py`,
  `relations.py`: `per_call`, `compose`, `rectangular`, `semigroup`), which uses EVERY-RAY's `paths_dp.py` and the census's
  `reach_dp.py` (`Preparation`, `flat`, `Block`, the usual-limit relations `G`, main, S, entries).
- **Path DP.** `experiments/EVERY-RAY-20261113-001A/EVERY-RAY-20261113-001A-E001_min_over_paths/codex/paths_dp.py` and
  `run_paths.py`: the min over descending paths, members on the path, per depth, with its residue classification.
- **Direct search.** `research/FREE-TARGET-20261114-001/referee-R1/codex/direct_bonds.py` (unfolded CNF, usual-limit relations at
  the frontier, SAT projections), as used by `research/CENSUS-FORGET-20261114-001/referee-R1/codex/direct_other_targets.py`.

## Per family (window.py, one shared-runner case per family)

1. **Basics.** Living check (the usual limit of S and main nonempty). Recompute per-call relations with `relations.per_call` and
   compare with the census `R_i` (gate a). Scope, stratum, c, wrapper or not, weight.
2. **Start and steps.** Start: main's block with its S-call chosen (the diagonal on S's ports when main = S), giving the joint of
   main's ports with the top copy's ports, plus the identity partition (which top-copy ports are the same distinction as which main
   ports, and as each other). A step by SELF call i maps (J, partition) to (J · R_i, partition carried through call i's arguments:
   child port k is the same distinction as parent port j when the k-th argument is j; child ports with equal arguments are merged;
   an own distinction passed to a child port starts a new class not containing any main port). Depth convention as FREE-TARGET.
3. **Q_s iteration.** Q_0 = {start state}; Q_s = {step_i(q) : q ∈ Q_{s−1}, i}. Stop at the first s with Q_s equal to an earlier
   Q_t; record preperiod t and period s − t. Caps: at most 200,000 stored states in total and 2,000 levels; on a cap, the family is
   undecided for the window (record the cap).
4. **Window bond g(q).** For a state q = (J, partition), the window variables are main's ports and every distinction of the copy's
   flattened block (ports and own), with merged classes as one variable. Its allowed set is {(t, b) : (t, b|ports) ∈ J, b satisfies
   the block's knots and every call's usual-limit relation, SELF calls included}. g(q) is the least size of a minimal non-shattered
   set containing at least one port of main and at least one own distinction of the copy; ∞ if none up to size 6 (record "> 6").
   Also record, for the least bond, its members and whether it is a B bond (a carried port plus two pendant own distinctions in one
   knot), a widened-B bond (a carried port, an own distinction and a third member in one knot), a tie bond (no carried port, a main
   port tied to a copy port), or other.
5. **U(s).** U(s) = min over q ∈ Q_s of g(q), for s from 0 to the end of the first period. Classify: **bounded** (finite at every s
   in the repeating part; record max and the residues), **progressions** (finite on some residues of the repeating part only),
   **none** (∞ on every residue of the repeating part), **undecided** (cap).
6. **Theorem B, syntactic.** K = positions k with a knot {k, x, y}, x and y pendant (one constraint, no call argument in any
   definition). Carried sets R_s by the identity graph from the start (iterate to a repeat). B covers a residue when every R_s in the
   repeating part on that residue meets K. Gate b: B-covered residues have U ≤ 3.
7. **Readings for P3.** On each residue of the repeating part, whether some carried position shares a knot with an own distinction
   (the "knot-meeting" flag), and whether R_s is empty (no carried port of main).
8. **Lemma G (live quotient).** Dead positions by least fixed point across every definition: a position is dead when every
   occurrence of the port at that position, in its definition's block, is as an argument of a call at a dead position of the callee
   (a knot occurrence makes it live). A distinction is free when every position it occupies is dead. Reduce each R_i by projecting
   out the dead coordinates of S's ports (on both sides), then run `relations.semigroup` on the reduced relations (size 2^live).
   Certified when some r makes every r-product rectangular. Record r.
9. **Lemma G2 (trimmed gap).** For every context image A (the set of copy-port states in the second coordinate of J, over every
   state reached in steps 2 and 3) and every product M of r SELF relations (r = 1 to 8, from the length sets of
   `relations.semigroup`, capped as there), trim M to {(α, β) ∈ M : α ∈ A, β ∈ G_S} and test rectangularity. Certified with the least r
   for which every trimmed product is rectangular. Also on the live quotient (G2 after G's reduction). Record r.
10. **Verdict per family.** bounded (window), progressions, growing (G or G2), undecided. Gate e: never both bounded and growing.

## Gates (gates.py; write gates.json)

- (a) and (b) are recorded per case by `job_window.py` and checked over the whole population by `summarize.py` after the full
  run; check them now on the smoke and gate families only.
- (c) **Negative control.** The first 300 certified-forgetting families of the census results in sha256("CARRY:" + key) order: run
  steps 1 to 5 and 9; require U(s) ≥ 2 + ⌊s/r⌋ at every s computed (2 + ⌊(s − 1)/r⌋ for a wrapper main) and G2 certified.
- (d) **Brute force, separate code** (brute.py, sharing no window code): the first 50 in-scope stratum I families in the same order.
  For every word of length s ≤ 3, unfold the pattern explicitly to depth s + 1 (usual-limit relations at the leaves), enumerate its
  allowed states by SAT or direct enumeration, and project onto main's ports and the end copy's block distinctions. Compare with the
  window's allowed set for that word's state (after merging identical distinctions). Then re-verify 200 window bonds drawn with
  `random.Random(20261114)` from all families' recorded least bonds at s ≤ 3: non-shattered, every one-member deletion shattered.
- Synthetic controls: a family with a carried pendant knot (U = 3 at every depth); a family whose carried port sits only in
  port-only knots; an identity carriage with one dead coordinate (G must certify, the window must not bound through it); a forgetting
  family (G2 certifies).

## Sample (sample.py; after the census-wide run, from its results only)

- Path DP: every in-scope T, O and X family whose window verdict is not bounded, plus up to 30 per cell of in-scope I families whose
  window verdict is not bounded, cells = (period of R_s: 1, or more) × (knot-meeting on some unbounded residue: yes, no), in
  sha256("CARRY:" + key) order. Write `sample.json` before running anything on it.
- Direct search: the sampled families still not bounded after the path DP, up to 60 in the same order; s = 1 to 6, members within
  the unfolded pattern to depth s + 2, targets every covered copy at depth s; least bond up to size 6, else "> 6". Per family and
  depth record the value, or the cap.

## Jobs

- `job_window.py`: the census-wide steps 1 to 10, one case per family; per case at most 600 s and 3 GB.
- `job_paths.py`: EVERY-RAY's path DP on `sample.json`'s path list (reuse `run_paths.py`'s per-family entry point unchanged).
- `job_direct.py`: the direct search on `sample.json`'s direct list.
- `summarize.py`: P1 to P5 and every reported share by stratum, by count and by weight, Wilson intervals, the undecided cell and the
  sensitivity without it, the out-of-scope row, T family by family. Write `summary.json`.

## Report

`REPORT.md`: what was built, every gate's result, smoke timings and peak memory per case, the exact launch commands the thread
should run (prepare-only already done), and Ambiguities. Do not compute P1 to P5 on the population yourself; the thread reads them
once after the full run.
