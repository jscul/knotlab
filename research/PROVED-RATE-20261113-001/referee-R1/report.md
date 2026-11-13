# Referee report PROVED-RATE-R1 (lean, Codex-assisted, fresh code)

**Verdict: Confirmed with fixes: two Narrowing, one Not a block.**
- **Every recomputed field agrees.** That holds on 95 families rebuilt from fresh code, which never read the study's implementation.
- **The proofs are sound.** The lower bound L_ray(s) ≥ λ(s − t) holds, and λ = liminf L_ray(s)/s.
- **The run history checks out.** 508 + 92 + 64 = 664 rows, disjoint and identical to the merged file.
- **The every-depth test is only sufficient.** All 46 "flat" families it failed are in fact bounded at every depth, and so are 10
  more zero-mean-only families. So at least 361 families are bounded, not 305.

**How the work was split.** The background referee thread owns the verdict.
- **Codex.** The Codex command-line tool, at the owner's choice of model and effort, recomputed from fresh code written from the
  spec. It was barred from the study's own implementation folder, and its run log shows that folder was never opened. It took about
  9 minutes and wrote only in `codex/`, starting with `codex/codex_report.md`.
- **The referee.**
  - Checked the proofs.
  - Compared the rates with BOND-DEPTH-R1's depth-512 sample.
  - Audited the three batches (`ref_history.py`), which Codex could not open under its rule.
- **Advisor.** The advisor model was not consulted.

## 1. Recomputation (Codex)

**The sample.** 95 complete families: the 40 smallest, the 10 smallest of each class, and all 46 disputed "flat" families.
- **Codex's code.** It wrote its own bitset DP, trimming, SCCs and exact rational Karp. It imported only the family list.
- **The match.** 2,375 field comparisons across 25 fields all agree, and 1,885 recorded depth values all match.
- **Controls.** Codex ran 210 synthetic graphs against explicit cycle enumeration, plus direct-set controls for the block
  operations.

**Against my depth-512 sample (BOND-DEPTH-R1).** The 20 "rising" families there have λ = 1 (13), 1/2 (6) and 2 (1) in
`rates_all.jsonl`, exactly the rates certified then.

## 2. The proofs (the referee, with Codex's write-up in `codex/math_review.md`)

**The lower bound holds.** Take an accepting depth-s walk of s − 1 middle steps inside the trimmed graph (t nodes).
- **Every node counts.** Every node on such a walk is reachable and co-reachable, so the walk lies in the trimmed graph.
- **Cutting cycles.** Removing cycles leaves a simple walk of at most t − 1 steps. Each removed cycle costs at least λ times its
  length, and every cost is nonnegative.
- **So** L_ray(s) ≥ λ(s − t). The trimmed count is the sharper |V|.

**λ is exactly liminf L_ray(s)/s.** Repeating a minimum-mean cycle between fixed entry and exit walks gives the matching upper bound
along a progression of depths. That is also why rates per residue are a separate question, as the note says.

**Karp on the trimmed graph is right.** Restricting to reachable and co-reachable nodes is exactly the set that accepting walks can
use. The minimum over strongly connected components of their minimum cycle means is λ.

**bounded_all is sufficient, but only for every sufficiently large depth.** Go from a reachable node into an empty-W cycle (cost 0)
whose every node closes. Then every large depth has a closing of bounded cost.
- **Not necessary.** In family 130 the cycle's states close only through a fixed positive-cost exit.
- **An exact test (Codex).** Take P, the least common multiple of the zero-cycle lengths. Track the walk length modulo P, flag a
  visit to a zero cycle, and check every residue. Codex proves both directions.
- **What it finds.** All 46 "flat" families that fail bounded_all are bounded at every depth s ≥ 1, at 4 or less. So are the ten
  smallest of the other zero-mean-only families.
- **So the count is at least 361:** the original 305 plus these 56.

**A capped graph proves no growth.** On a subgraph, λ_H ≥ λ_full, so a positive partial λ is no lower bound.
- **What still transfers.** Positive witnesses do: a zero cycle or a closing empty-W cycle found on a capped graph is genuine.
- **The census is right here.** It counts only complete graphs for λ > 0 (226; the single partial 1/3 is excluded).
- **One small gain.** Its 4 partial bounded_all are valid certificates too, giving 309.

## 3. The run history (the referee)

The three batches (508, 92 and 64) hold 664 rows, all distinct. Every row equals its row in `rates_all.jsonl` in every scientific
field, and no family is missing. The second batch's log ends at 92 of 156, consistent with the out-of-memory stop. The last one ends
at 64 of 64. This closes the provenance gap Codex flagged, which came from my own rule barring it from those files.

## 4. Wording and construction

**The ray wording is correct.** L_true(s) ≤ L_ray(s), so ray growth is an upper bound only and boundedness transfers. The note says
both.

**Small wording fixes.**
- Write "no ray bond at large depths" for λ None, not "vanishes". Two families never have one and ten lose it.
- The rates run from 1/7 to 2 per level, not "one to six levels".
- For the 26 rising families with λ = 0: λ = 0 alone does not mean eventually constant, though five of the 26 were proved
  eventually constant at 4 in BOND-DEPTH-R1.

**Settled by construction.** Finite state, nonnegative costs, zero cycles being empty-W cycles, and the min-cycle-mean implications.
The rates and counts per family are the substance.

**Prior work.** The statement (Karp 1978; Cohen, Dubois, Quadrat and Viot 1983; Heidergott, Olsder and van der Woude 2006) is
adequate.

## Fixes for the thread

1. **Boundedness.**
   - Say that bounded_all is sufficient for every sufficiently large depth and not necessary.
   - Report at least 361 families bounded: 305 plus the 46 "flat" and 10 other zero-mean families certified exactly, with bounds of
     4 or less.
   - Drop "bounded only along a progression" for the 46.
   - P3 still fails as frozen, since it tested the predicate.

   **Narrowing.**
2. **Growth and absence.**
   - Give growth as a ray-only linear lower bound with an additive constant, and the rate as the liminf.
   - Write "no ray bond at large depths" for λ None.
   - Give rates as 1/7 to 2.
   - Do not infer eventual constancy from λ = 0.

   **Narrowing.**
3. **Presentation.** Keep 644 of 653 (records with values) apart from 655 of 664 (all). The partial bounded_all could raise 305 to
   309. **Not a block.**

## Files

- **`codex/`.** Codex's brief and report, `recompute.py`, `controls.py`, `math_review.md`, `history_audit.py` and the JSON outputs.
- **Referee.** `ref_history.py` and `result_history.json`.
