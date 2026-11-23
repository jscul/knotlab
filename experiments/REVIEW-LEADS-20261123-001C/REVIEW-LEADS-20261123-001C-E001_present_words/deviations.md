# Deviations and readings: REVIEW-LEADS-20261123-001C-E001

Every definition of the frozen pre-registration (`research/REVIEW-LEADS-20261123-001C/preregistration.md`) is unchanged. Where
the note was open, or where a run could not be done as written, the reading taken is listed here. Nothing was tuned after values
were seen; the one method added after a pre-registered method returned only the value 2 is item 9, and is labelled exploratory.

1. **Four knots need more than three internal distinctions.** A side with k knots of arity 3 or 4 has at least 3k holder places,
   while a side with a cut of c, I internal distinctions, three observer distinctions and at most two holders per internal
   distinction has at most 3 + c + 2I places. With I <= 3 and c <= 2 that is at most 11 places, so four knots (at least 12
   places) are impossible. The pre-registered class "at most 3 knots, at most 3 internal distinctions" is therefore the census
   class and is **exhausted** (every side listed, every ordered pair combined). The "4 knots if a run stays within bounds"
   option was read as **at most 4 knots and at most 5 internal distinctions** (a four-knot side needs at least 4 internal
   distinctions; 5 was taken as the smallest bound that also keeps all earlier sides). That extended class was also listed in full
   (cut 1: 4,501,281 lawful structures, 8,647 tables; cut 2: 27,947,475 structures, 51,596 tables, listing 211 s) and all its
   pairs were combined (cut 2 in 12 row blocks, each under 4 minutes wall time on the shared machine), so it is exhausted too; it is not "partial".
2. **Allocation class flag.** A table is flagged if some structure that makes it has x2 and x3 held by one knot and x1 by a
   different knot. The evaluation depends on the table only, so a pair is "in the allocation class" when both tables are flagged.
   (The note does not say how to flag a table made by several structures.)
3. **Deduplication and symmetry.** (a) Side tables are listed once per exact table and counted that way. (b) For pairing, each
   table is divided by the gcd of its entries (the score, the hiding and the control value are unchanged by scaling a side), and a
   projective table is flagged if any exact table giving it is. (c) Pairs are reduced to unique old tables M up to scaling and the
   32 symmetries of the evaluation (swap x2 and x3 on a side, flip every old value of a side, exchange the observers); the symmetry
   was checked numerically on 700 tables (300 random, 400 hidden) in `gates_a.log`, and the census of both cut sizes was run both on all
   ordered projective pairs and on symmetry classes: identical numbers of unique old tables, hidden tables, tables reaching 2,
   tables above 2 and identical maxima (`sym_equivalence_check.json`). The census was run on **all ordered pairs of
   projective tables**; the extended class and the targeted search were run on **unordered pairs of symmetry classes of tables**
   (tables identified under the four row maps of a side), which stand for every ordered pair of projective tables by the
   symmetries. Pair counts are given in the result note for both.
4. **Knots on the same set of distinctions.** Two knots may hold the same set of distinctions only with different laws (an
   identical repeated knot adds nothing to a table). Disconnected knots (all places internal) are included; they only scale a table.
5. **"Hidden" and the score.** Hiding is decided in integers (equal, after scaling, of the old-record vectors M W0, M W1 and of
   M^T W0, M^T W1, which is the stated condition because the lawful-value count is positive). Scores are in 64-bit floats with a
   tolerance of 1e-9; every hidden table that reaches 2 within the tolerance was re-evaluated in exact rational arithmetic (the
   float screen picks every outcome choice within 1e-7 of the float best; each is evaluated with Fractions). Pairs with no allowed
   old word (M = 0) have no finished word and are not evaluated; their number is stated.
6. **Control weighting** was evaluated for every unique M of every run (the control column of each summary), not only on the
   gate sample.
7. **Extra tests.** "Best over all two-valued functions" was run by alternating optimization from the 225 parity starts and 200
   random starts, for the four sign patterns, as written. As an extension (not pre-registered) it was also run on every
   saved hidden table with parity score at least 1: all of cut 1 and 52,002 of the 55,112 distinct tables of cut 2 (the
   remaining 3,110 have the lowest parity scores; all 14,774 that reach 2 were done first). The linear-programming test is a
   residual minimization (zero iff a common local explanation exists), over deterministic strategies on the lawful records of
   each setting; it was run on the best ten by (general value, parity score) and on 40 more spread over the hidden tables that
   reach 2. "Best ten" is ambiguous when all reach 2; the ranking above was fixed before running.
8. **Reference, pre-registered method.** The 2,000 seeded starts were run as written (local optimization, SLSQP with exact
   gradients, over side tables TA, TB with 4 cut values, hidden ratios and the exact hiding equations). Its one reading: the
   hiding equations are imposed on the old table M = TA TB^T (M (W0 - lam W1) = 0 and (W0 - mu W1)^T M = 0 for some positive lam,
   mu), not on the factors, because hiding forced on the factors alone gives a common weighting of the cut values and so
   a local model (score at most 2 by construction). The outcome choice (masks and sign pattern) is re-chosen at the current table
   and held fixed for the next local optimization, up to five rounds.
9. **Reference, added method (exploratory).** The 2,000 random starts returned no feasible table above 2 (largest 2.0000000863 at
   constraint violation 1.1e-9, a feasibility slop). The note's own four-type table (20/9) is not found from random starts
   because the tables above 2 form a thin set. A second method was added and reported separately: for fixed hiding ratios
   (lam, mu) the hidden old tables form a polytope on which the score is a convex function, so its maximum is at a vertex; vertices
   were sampled by linear programs with random objectives on a grid of 30 x 30 ratios (600 programs per point) and on finer
   11 x 11 grids around the six best points (800 per point). This is a search, not a proof of a maximum. It places no restriction
   on the number of cut values; the 20/9 table is shown to need a cut of two (rank-4 factorization) and is the best found.
10. **Targeted search.** "Sides of up to 6 knots in the allocation class": k drawn uniformly from 2 to 6, arities and laws
    uniformly, the number of internal distinctions at most 9 (so at most 14 distinctions, for a table by brute force), holder
    counts respected exactly, x2 and x3 placed in one knot and x1 in another. Each pool was capped at 14,000 distinct tables
    (reached in 1 to 2 minutes of drawing, well under the allowance), then combined as in the census. Because the allocation class
    is exchangeable in x2 and x3 (result note), the same search was repeated **without** the allocation condition as an extension.
    Pair evaluation was split into 6 row blocks per pool to stay inside the memory limit. Two earlier attempts at this pairing were
    discarded and repeated on the same pools: the first ran out of memory at the 12 GB cap, the second stored old tables as 16-bit
    integers, which overflow for tables with large counts (entries above 32,767 appear when a table has 9 internal distinctions;
    the census and the extended class have entries below 4,096 and were not affected); entries are now 32-bit.
    A second pass of draws with other seeds (pools capped at 20,000 tables) was run in the same way and is reported with the first.
11. **Gate on 200 random pairs.** 100 pairs per cut size, half of them with both sides drawn from the allocation-class tables,
    drawn from the census class, each compared (joint record counts of all four finished structures, 16 x 16 integers) with the
    side-table product, and the old-word table compared with brute force.
12. **Not done, by the stop rule.** No hidden pair exceeded 2, so the full-structure write-out, the brute-force enumeration of a
    positive structure, its local-explanation test and the keyed-setting policy test on a lawful structure were not run. As a
    side check of the same code, the policy test was run on the (not lawful) reference table.
13. **A C kernel.** The batch score (15^4 outcome choices, four sign patterns) is also implemented in C (`chsh_kernel.c`, compiled
    to the artifacts directory) because the numpy version is about 18 times slower; it agrees with the numpy version to the last bit on
    random tables (checked in gates_a.py) and the numpy version agrees with the starter's `evaluate` on 1,500 random tables.
14. **Parallel runs.** Several single-process runs (each under ten minutes and 12 GB, one thread) were run at the same time on the
    shared machine; no run needed more than one process.
15. **Development runs.** Exploratory development runs (timing, gradient checks, small trials of the reference optimizers and of the
    vertex search, an independent itertools re-enumeration of small side classes) were made from throwaway scripts outside the
    experiment directory, some without the `prlimit` wrapper; they are small and their results are not used except where a retained
    script reproduces them (`reference_vertices.py`, `reference_fine.py`, `reference_slop_check.py`, `sides.py`). One early launch of the
    random-start and vertex runs without a thread limit oversubscribed the machine; those processes were stopped and the runs were
    restarted with one thread each. Nothing from the stopped runs is used.
