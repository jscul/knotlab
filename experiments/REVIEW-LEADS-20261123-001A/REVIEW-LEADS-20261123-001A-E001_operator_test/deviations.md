# Deviations, readings and limits (REVIEW-LEADS-20261123-001A-E001)

Nothing in the pre-registration's "Definitions (frozen)" or "Predictions (frozen)" was changed. Everything below is either a reading
taken where the note could be read two ways (the most literal one), a limit applied under the ten-minute and 12 GB rule, or a
shortcut that cannot change a verdict (and is checked). Source files read, none changed, are named in `lib.py`.

## Readings taken (the most literal)

1. **"The three archived explosive starts"** = archived starts 00, 04 and 13 of the cap-seven archive (`named_archive_starts` in
   `artifacts/HEAVY-GROWTH-20261119-001/.../sources_audit.json`; draws 91 of the six-knot cap-7-06, 110 of cap-7-06 and 55 of cap-7-07).
   They are the three `archived_burst` starts of the six-rule study (`FOUR-READINGS-20261120-001A .../growth.py`, `ordinary()`), the study the
   note builds on. Another reading (the 16-start archive, or the two hosts of `FOUR-READINGS-20261120-001D .../explosive.py`) was not used.
2. **"The five-founder clock"** = the `five_odd` source of `CALIBRATIONS-CLOCKS-AND-WIDER-KNOTS-20261120-001B .../phase_clocks.py`
   (five knots sharing in a closed loop, with 2,1,1,1,3 shared distinctions between neighbours and two loose distinctions each). **"The 21-knot structure with two clocks"** =
   `periodic.frame('meeting')` of `GENERATORS-20261120-001A` (21 knots, 60 distinctions; its gate counts are checked in `gates.py`).
   **"The nine-knot drawn source"** = the smallest sampled positive of `READS-HOLDERS-SOURCES-20261120-001C/proof.md` (ten pairs, loose
   5,2,4,3,3,4,3,3,2; 9 knots, 39 distinctions). **"The seven-knot source"** = `small_periodic.physical` links with loose 3,0,3,3,3,2,2.
3. **Growth stops at a cap by not taking the step**: "to 20,000 knots" (P2, P1) and "to 5,000 knots" (P3) mean that a parent step whose
   births would take the structure above the cap is not taken (`end_operator.step(..., max_births=cap - knots)` returns `cap`). The outcome
   is recorded as `cap`. In P2 this stopped five sources before 16 steps (nine-knot source 8,911 knots after 8 steps; 21-knot structure 13,486
   after 8; seven-knot 19,614 after 13; archived 04 2,081 after 8; archived 13 1,368 after 6); in P3 no draw reached the cap.
4. **P3 draws**: one `random.Random(2026112301)` is used in order over arms 0, 1, 2, 3 with 256 draws each: size `randint(4, 8)`, a
   Pruefer word, one coin per knot (chance 1/4 of one more loose distinction), then `sample(missing pairs, arm)` for the extra meetings; each
   knot gets `max(3, degree)` places plus its coin. The arms are independent draws (not nested). Both laws use the same draws. The sampler
   follows `READS-HOLDERS-SOURCES-20261120-001C survey.draw_specs` and `GENERATORS-20261120-001A sample.source_draws`.
5. **Rewired comparison details the note leaves open**: the birth order inside a step is the engine's (multi-parent births in sorted order,
   then one-parent births); a birth's eligible parents are the knots that hold a loose distinction at the moment it is made (a knot that has
   given its last loose distinction drops out); knots born in the same step become eligible at the next step; the loose distinction a parent
   gives is its last in the list (the loose distinctions of one knot are interchangeable). Each replica uses `random.Random(seed)` with
   seeds 2026112310 to 2026112317, re-seeded for every start (so a replica's draws are reproducible per start in any chunk).
6. **First failing step and the median** (P3): a start or rewiring with no failing stage within the horizon is coded +infinity; the median of the
   eight rewiring values is the mean of the 4th and 5th smallest. Prediction P3 is judged on this primary reading, pooled over all P3 starts
   (both laws, four arms); per-law and per-arm shares are tabulated. Two sensitivity codings are reported beside it (lower median; no failure
   coded as the last reached stage + 1).
7. **Growth kind**: `stalled` = the engine stalled, or the history has no birth at all (no live knot at the source: the K4-like sources with no
   loose distinction); `bounded` = births per step never above the largest of the first four steps; `growing` otherwise. A history that
   closes counts as bounded or growing by the same rule. The outcome (stall / closed / horizon / cap) is tabulated beside it.
8. **P2 pair of stages** is searched over all reached stages of P1, P2 and P3 pooled, and also within each population.
9. **Closed parity part, "admits"**: the recorded independent solver `pauli_solution` (`FOUR-READINGS-20261120-001A .../census.py`) is run
   with each single odd knot in turn (up to 40 knots) and the part admits when one succeeds. No assignment ever exists with one odd knot when
   every distinction has two holders (the knots sum to zero), so only the operator reading is computed. The part is judged against T on its own
   incidence pattern. Closed parity parts are looked for in the parity-law histories only (a not-all-equal history is not a parity part);
   a part is counted once, at the stage where it is first met.
10. **Knot-side check** (gate G, last clause), read as follows. Change-answer words: a single-mark change question on every distinction of the structure
    (all answer words, so every sub-collection follows by marginals). Recorded counting rule: `words.counts_table` of the recorded
    code (`FREEDOM-CLOCKS-AND-BIRTHS-20261120-001A .../words.py`), whose value is the Fourier form of C(T,U) of `counting.md` section 1.
    For more than ten distinctions `counts_table` needs 4^m operations; the same rule is then evaluated as `Shat(a)^2 / (2^m |S|)` (a
    Walsh-Hadamard transform), asserted equal to `counts_table` on the two small structures (4 and 10 distinctions). Knot side: all 2^n sets of
    knots with equal weight, each distinction read as the parity of its drawn holders. Exact fractions; all answer words compared.
    Five structures: two split three-place knots ((0,1,2) and (0,1,3)); the five-knot closure of the closing-sign study (holdings
    {1,6,7,8},{2,3,4,8},{0,3,6,9},{4,5,7,9},{0,1,2,5}); three closed parts met in P3 chosen by the rule fixed in `knotside.py` before they
    were read (first three non-isomorphic closed parts with at most 14 distinctions, in the order arm 0..3, file order). They were met in the
    P3 parity files, so that part of gate G ran after P3 (the rest of G ran first, and P1 to P3 were started only after G1 to G3 and the first two
    structures passed).
11. **Both laws on P2**: the not-all-equal history is the parity history when no step has exactly one birth (the engine's only difference between the
    laws); census_p2.py then writes the not-all-equal lines from the shared history (flag `history_shared_with_parity`). `p2_law_check.py`
    runs the not-all-equal law for the first five steps of every P2 source and finds the same stars, births and outcomes. P3 runs both laws separately.

## Limits applied (ten minutes, 12 GB)

- Each run is one foreground process under `timeout 600 prlimit --as=12884901888`. Several runs (up to eight) were started together in one shell
  command and waited for; none shared a process or a file. No run hit a limit: the wall-clock budgets inside the scripts (330 s per P2 growth, 25 s per
  P3 growth) were never reached, no history has outcome `time`. The slowest run was archived start 13 (396 s with seven runs in parallel).
- P3 was run as eight runs (law x arm), each of 256 draws; every run finished within 25 s.
- Removal bounds: the upper bound is computed only at the first failing stage of a history (not at later failing stages), after pruning pendant nodes
  (loose distinctions and knots with one link cannot lie on a forbidden sub-pattern; they are removed before the routine is called, which
  does not change planarity). Caps: 160 links in the pruned pattern and 80 removals for P3, 600 links and 300 removals for P1 and P2, 20 s (P3) or
  40 s (P2) per bound. All 66 failing P3 histories and all P2 and P1 first failing stages were within the caps.

## Shortcuts that cannot change a verdict (checked)

- T is `networkx.check_planarity` of the incidence pattern. Before calling it, a pattern with more links than 2V - 4 (V nodes) is reported as failing,
  by Euler's bound for a simple bipartite pattern. `gates.py` (S2) compares the shortcut with the routine on all 173 recorded patterns, all 20 benchmark
  patterns and 995 engine stages: no disagreement. Every first failing stage of a parity history in P2 and P3 (40) also carries a Kuratowski certificate
  (the routine's counterexample is a K5 or K3,3 subdivision) and the stage before it an embedding satisfying Euler's formula (`verify.py`, V1b).
- The growth driver `lib.grow` calls the recorded `end_operator.step` and builds the births the way `GENERATORS-20261120-001A fixtures.literal_turn`
  does; it reproduces the recorded birth counts of archived starts 00, 04 and 13 and agrees with the other recorded engine (`naelib`, freelib presentation)
  on counts per parent step in 80 of 80 P3 draw-and-law pairs (gate S3). A stage is the first n knots in birth order, with the distinctions they hold (a stage never shows a link made
  by a later birth).

## Findings about the note's own definitions (reported, not repaired)

- **Gate G, mutant clause.** "A mutant that unlinks the second holder of every shared distinction passes everything" holds for the 173 recorded patterns, every
  P1 pattern in which a distinction has at most two holders (cubic, pinwheel, polygonal control: 16 of 16 in the gate's depth list) and 13 of 13 engine stages. It does **not** hold
  literally for the bounded-bond windows 2 to 4, where a distinction has up to six holders and unlinking only the second leaves the others (window 1 passes;
  windows 2, 3, 4 still fail). The clause is true only where every distinction has at most two holders; this is a flaw of the wording, not of the code, and the gate
  is recorded as passed for the patterns with at most two holders and failed literally for the bounded-bond windows.
- **Lower removal bound.** `max(0, P - (3K - 6))` counts distinct pairs of knots that share a distinction. It bounds the removal of shared distinctions from
  below only when each distinction has two holders (a removal then deletes at most one pair). For the bounded-bond windows, a distinction of six holders is 15
  pairs, and the recorded lower bound exceeds the upper bound (window 2: lower 41, upper 5). Reported as computed.
- In every P3 and P2 history the lower bound is 0 (pairs never exceed 3K - 6 at the first failing stage), so it carries no information there.

## Not done

- The upper removal bound at stages after the first failing one (not required by a prediction).
- The brute-force minor search on incidence patterns with distinctions of three or more holders covers 61 small random patterns and the K3,3 case, not every
  such pattern with at most six knots (their incidence patterns have more than ten nodes; the exhaustive search is exponential in the node count). The simple
  sharing patterns (distinctions of two holders) are covered exhaustively: every simple graph on 1 to 6 knots (and 7), and every recorded pattern.
- The note's `Scaffolds` record and the epic ledger are the thread's.
