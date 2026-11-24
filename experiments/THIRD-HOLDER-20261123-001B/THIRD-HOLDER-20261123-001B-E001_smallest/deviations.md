# Deviations and readings: THIRD-HOLDER-20261123-001B-E001

Every definition of the frozen pre-registration (`research/THIRD-HOLDER-20261123-001B/preregistration.md`) is unchanged.
Where the note was open, or where a run could not be done as written, the reading taken is listed here. Nothing was tuned
after values were seen. Code is in this folder; outputs in
`artifacts/THIRD-HOLDER-20261123-001B/THIRD-HOLDER-20261123-001B-E001_smallest/`. Code reused from
`experiments/REVIEW-LEADS-20261123-001C/REVIEW-LEADS-20261123-001C-E001_present_words/` is copied, not imported, and marked
COPIED in `common.py` (evaluation, hiding test, exact score, symmetries, the C scoring kernel `chsh_kernel.c`).

1. **Census class.** A side: observer distinctions x1 x2 x3 (class L: exactly one old holder each; class S: one or two),
   one or two shared distinctions (exactly one holder on this side), 0 to 5 internal distinctions (one to three holders
   each, every one held), 1 to 4 knots of 3 or 4 places with law even, odd or not-all-equal, on distinct (members, law)
   pairs (as in ticket C: two knots may hold the same distinctions only with different laws). Every labelled structure is
   visited by the compiled enumerator `sides_enum.c` and its side table is deduplicated exactly. With the holder bound set to
   two the enumerator gives ticket C's listings exactly (same structure counts 7,023, 41,355, 4,501,281 and 27,947,475, and
   the same sets of tables, 596, 3,018, 8,647 and 51,596). In class S a side table is the same function as in class L (the
   observer still reads its distinction and the birth still takes it, whatever its number of old holders); the class only
   changes which sides are listed. A side with two shared distinctions needs at least two knots (five places).
2. **Five knots.** "5 knots if every run stays inside its bounds" was attempted where it could be done in runs under ten
   minutes and 12 GB: class L with two shared distinctions (2,279,242,395 labelled structures listed in 64 parts by the index
   of the first knot, `sides_parts.py`, merged into 2,403,586 tables; pairs in 67 runs). Not done: class S with 5 knots (its
   4-knot listing alone has 1,006,014,636 structures and 1,620,095 tables; with 5 knots the pairing would be several
   hundred times larger), and either class with one shared distinction (not needed: item 4, case K = 2, proves that no pair
   with one shared distinction has a hidden excess, at any size). So the class-L census is exhausted for sides of at most 5
   knots with two shared distinctions and at most 4 knots with one; the class-S census for sides of at most 4 knots.
3. **Pairs.** Every ordered pair of side tables of the same class and the same number of shared distinctions. Tables are
   divided by the gcd of their entries (as in ticket C) and reduced to one per orbit under the four row maps of a side (swap
   x2 and x3, flip the three old values; `pairlib.orbit_reps`): the old table of an image pair is an image of the old table
   under the 32 symmetries of the evaluation (copied from ticket C), so pairs of representatives stand for every ordered pair.
   Old tables are deduplicated up to those 32 symmetries. The counts in the result note give the pairs that were scored and
   the ordered pairs of projective tables that they stand for.
4. **The reduction (proved; checked).** For a side table T write p_b(T) = T^T W_b and M = T_A T_B^T. Alice's complete
   record hides Bob's setting iff T_A p_0(T_B) || T_A p_1(T_B) (and likewise for Bob), because M W_b = T_A p_b(T_B).
   (1) If p_0 || p_1 for both tables, the weight u_a(s) v_b(s)/N_ab of the shared value s does not depend on the settings, so
   the four record tables have one common local explanation (hidden value = the shared values): the pair is hidden and every
   score is at most 2. (2) If a table has rank 1, M has rank 1, the old words are a product and the score is at most 2.
   (3) Otherwise a hidden pair has a non-parallel side, say Bob's; for a pair with an allowed old word Alice's hiding holds
   iff the kernel of T_A meets the plane span(p_0(T_B), p_1(T_B)) (the multiplier is then automatically positive, since
   T_A p_b(T_B) are non-negative and non-zero). With one shared distinction (K = 2) the plane is everything, so T_A would have
   rank 1: no pair with one shared distinction has a hidden excess (the one-shared-distinction argument of ticket C, in
   another form). (4) If M has rank at most 2, its columns lie in a two-dimensional pointed cone spanned by two extreme
   columns, so M = A' B'^T with non-negative factors of two columns, and (1)-(3) with K = 2 give a score at most 2. So an
   excess needs both tables of rank at least 3 and the hiding side of rank exactly 3, its kernel a line k in
   span(p_0(T_B), p_1(T_B)). The test is exact: kernel lines and planes are primitive integer vectors (Pluecker
   coordinates), compared in integers. Only the pairs that (1), (2) and (4) do not exclude are combined and scored, in the
   orientation with the non-parallel side as Bob. Checks (`gates.py`, parts 3 and 3b): the hidden pairs counted by the
   reduction equal those found by combining every ordered pair (130,427, 691,311, 2,962,619, 6,970,674); on a test class that
   holds excess pairs (all class-S tables of at most 3 knots, the 4-knot tables of the census excess pairs and 3,000 drawn
   4-knot tables) every ordered pair gives the same 145 excess old tables, with the same scores and sizes, as the reduction;
   on both 20,000-table search pools both methods find none.
5. **Compiled evaluation (`pair_eval.c`).** Same arithmetic as ticket C's kernel; hiding decided in integers (128-bit
   products); old tables deduplicated by a 128-bit hash of their smallest image (a collision among the at most ~10^8 tables
   of a run has probability below 10^-20). A screen skips the full maximisation when the four largest |correlations| sum to
   less than 2 - 1e-9 (the score is at most that sum); such tables are counted as below 2. Every old table with float score
   at least 2 - 1e-9 is written out and decided exactly: if its float score is at most 2 + 1e-12 and the least common
   multiple L of its four correlation denominators is below 10^11, it is at most 2 (a value above 2 exceeds 2 by at least
   1/L > 10^-11, while the float error is below 10^-13); otherwise its exact best parity score is computed in fractions
   (`common.exact_best`). "Hidden" is exact throughout.
6. **Reduction.** Each of the 200 seeds (2026112320 to 2026112519, the same seeds for both starts) gives a permutation of the
   knots (`numpy.random.default_rng(seed).permutation`); passes through that order are repeated until a whole pass removes
   nothing, so each final structure is minimal (no single further removal keeps a hidden excess). A removal is kept only
   if the structure is still hidden with an exact score above 2 (side tables; their product is checked against full
   enumeration in row G). A removal that would leave an observer distinction with no old holder is not kept (the
   structure would leave its class, and the birth would take a distinction no knot holds); the note did not say this.
   Result: from both starts no single knot can be removed (every single removal of the 18-knot structure that keeps the
   observers held either loses the hiding or drops the score to 2; likewise for the pencil), so all 200 orders end at the
   start structure. Both were verified by full enumeration (`verify_reduced.py`).
7. **Seeded search.** "2,000,000 drawn sides per class" was read as 2,000,000 lawful sides (draws that cannot be completed
   are discarded and do not count: 3,549,265 attempts in class L, 3,254,426 in class S). One stream per class from
   `numpy.random.default_rng(2026112321)`; each draw chooses its number of shared distinctions (1 or 2), so each class gives
   two pools. The generator follows ticket C's `targeted.py` (mode "free"): k uniform in 2..9 knots, 3 or 4 places, laws
   uniform, at most 9 internal distinctions (one to three holders), class L observers one old holder, class S one or two.
   "Pools capped at 20,000 distinct tables" was read as the first 20,000 distinct non-empty tables in draw order. The caps
   were reached at draws 123,237 and 81,430 (class L, one and two shared distinctions) and 101,942 and 70,274 (class S); the
   later draws only add to the counts of distinct tables. Each pool was paired as in ticket C, every ordered pair (item 3),
   and also with the reduction (identical result, item 4).
8. **Extension beyond the cap (exploratory, not pre-registered).** Because the cap leaves most of the 2,000,000 draws unused,
   every distinct table of the draws with two shared distinctions (313,906 in class L, 369,435 in class S) was also paired
   with the reduction. Reported separately; it does not enter the predictions except as "found by search", stated as such.
9. **Size.** Knots of the old structure; extra holders are holders beyond two summed over old distinctions, counting the old
   holders on both sides (a shared distinction has two, so none extra). An observer distinction with two old holders counts
   none: the third holder it gets from the setting birth is not an old holder. Beside it the result note gives the number
   of observer distinctions with two old holders. "Smallest in class S" is taken over every structure of class S, which
   includes class L; every class-S structure found is strictly in class S (some observer distinction has two old holders).
10. **Runs stopped by the limit.** Five runs of the class-S census pairing (class pairs 3207 to 3312, about 2.1 x 10^8 pairs
    each) reached the ten-minute limit and were stopped; they wrote nothing. That range was repeated in 21 smaller runs
    (logs `*_runq*`); the merge checks that the runs used tile every class pair exactly once. The stopped runs' logs are kept
    as `*_killed_by_limit.log`. No other run was stopped.
11. **Parallel runs.** Up to eleven single-process runs, each under ten minutes and 12 GB, ran at once on the shared machine.
    The merge of the class-L 5-knot listing used about 10 GB.
12. **Row G, part 2.** The 100 drawn pairs with a third holder come from the 4-knot census lists (25 from each of class L
    and S with one and two shared distinctions, seed 20261123); in each pair at least one side's stored structure has an
    internal distinction with three holders. Every word of the four finished structures was enumerated with no side-table
    shortcut. In addition, 200 seeded-search tables were re-enumerated from their stored structures (part 2b).
13. **The 18-knot structure** has two distinctions with four holders; it lies outside the census's holder bound and enters
    only as a start of the reduction. Its distinctions were renamed apart (Alice's internal names and Bob's do not clash);
    knots unchanged.
14. **Class S, sides of at most 3 knots** was paired with an earlier version of `pairs.py` (the same reduction, with hiding
    sides of rank 2 or 3 and the hidden pairs counted); that class is contained in the 4-knot class, which was run with the
    final code.
15. **Development runs.** Timing trials (three-seed reductions, a 20,000-draw generator test, the first form of the class-S
    3-knot pairing) were made before the final runs; the trial reduction files were deleted before `verify_reduced.py` was
    run, and nothing from the trials is used.
16. **Scripts.** "One script lists sides, one pairs them, one reduces, one searches": `sides.py` lists (with the compiled
    `sides_enum.c`, and `sides_parts.py` to split the 5-knot listing); pairing has two front ends on the same reduction
    (`pairlib.py`): `pairs.py` (numpy, every ordered pair or the reduction with the hidden pairs counted; used for the
    classes small enough) and `pairs_c.py` with `pair_eval.c` (compiled, for the large classes and the search pools);
    `reduce.py` reduces and `verify_reduced.py` checks its finals by full enumeration; `search.py` draws the seeded sides.
    `gates.py` and `gates_mix.py` are row G; `report.py` collects the results and verifies the smallest structures.
