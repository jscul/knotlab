# Deviations, readings and limits: SETTING-AS-REREAD-20261123-001A-E001

Nothing in "Definitions (frozen)", "Predictions (frozen)" or "Runs and stop rule" of
`research/SETTING-AS-REREAD-20261123-001A/preregistration.md` (sha256 2fe6c510...0cd9, as in `contract.json`) is
changed. Section A was written after the code and before any run of it (the self-test included); it lists every place
where the note leaves a choice and the reading taken, the most literal one available. Section B is added during and
after the runs and lists limits met and anything found after values were seen.

Recorded code is imported by path and never edited; its sha256 is asserted at every import of `both_settings.py`:
`qlaw.py` of ONE-PARENT-REREAD-20261123-001A-E001 (457abaa5...7942) and through it `rlaw.py` of
REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001A-E001 (29aa3d91...d8f8), the review-leads `lib.py` (c2bfbfd8...b821) and the
recorded `end_operator.py`; the recorded scorer `docs/prompts/missed_leads_checks/finished_weighting_chsh.py`
(ec55774a...4194), executed up to its section 1. Nothing under `research/SETTING-AS-REREAD-20261123-001/thread_checks/`
or `research/ONE-PARENT-REREAD-20261123-001/thread_checks/` was read or used before every number of this study was on
disk.

## A. Readings fixed before the runs

1. **Engine of record.** `qlaw.QGrowth` with law `nae` (every newborn not-all-equal, so no birth is implied and every
   birth has at least one fresh distinction), `reread=True`, `bound_next=False` (the lookahead demand computed in
   full), one round planned with `plan(max_births=None, choice=...)`; `rlaw.USE_C` is False (set by `qlaw` at import,
   asserted). The engine reads only holdings, so the laws of the old knots do not enter round 1. Beside it,
   `plan_round1` in `both_settings.py` is a second planner written here from the definitions of `end_operator.py`
   (witnessed sets, maximal groups, pairs, shortages, lookahead) and of rule Q (`qlaw` and its deviations A2 to A4); it
   is compared with QGrowth on every round 1 this study plans (all choices), and every structure is built from its
   plan only after the two agree. Row G is judged on both: QGrowth against the recorded driver on whole histories, and
   `plan_round1` against `end_operator.step` on round 1 (see A16).
2. **Names.** Distinctions are numbered by first appearance along the eleven knots as written in the note
   (x1 x2 x3 c s1 s2 h1 h2 y1 y2 y3 t m1 m2 k1 k2 = 0..15). The numbering matters only for conventions O and N (the
   smallest or largest number; reported, never used: every choice is enumerated) and for which loose distinction a
   parent with two or more hands to which birth (last listed first, as rlaw and lib.grow), which can matter only in (e).
3. **Options.** The distinctions the live knot holds that have two or more holders when round 1 starts (rule Q, qlaw
   reading A2). An option pair is an unordered pair; inside a pair, setting 0 is the option first in the note's order
   (x2, x3, c; y2, y3, t). The scores and hiding do not depend on this labelling.
4. **Stage-1 structure.** The eleven old knots and the births round 1 makes under the choice, each newborn
   not-all-equal over its inputs and its fresh distinctions. The fresh distinction of the birth on x1 is named zA, that
   of the birth on y1 zB (zA2, ... if a birth had more than one; other births' fresh distinctions n<i>_<j>).
5. **Weighting and enumeration.** Every allowed word of the stage-1 structure (all its distinctions, 18 in the full
   structure) counts 1. Every one of the 2^n words is tested against every knot (numpy, exact integers). It is
   asserted that the allowed old words (the 16 old distinctions) are exactly those of the old structure in every
   stage-1 structure (a birth with a fresh distinction forbids no old word).
6. **Records.** Alice's complete record for an option pair (o0, o1): (x1, o0, o1, zA), the same four distinctions
   under both her settings; Bob's (y1, p0, p1, zB). In (d): (x1, x2, x3, c, zA) and (y1, y2, y3, t, zB). Record values
   are coded big-endian in that order; nothing depends on the coding.
7. **Hidden.** For each of an observer's choices, the counts of its complete record under every far choice are
   proportional (exact integer cross-multiplication). Both observers hidden = both complete records unchanged by the
   far choice. The largest change (total variation, exact) is reported beside.
8. **Scores.** The four-correlation value is the largest, over the four placements of the minus sign and over the
   response functions, of |E(0,0) + E(0,1) + E(1,0) + E(1,1) - 2 E(k)|, with E(a,b) the mean of A_a(record) B_b(record)
   under the uniform weighting of the allowed words of structure (a, b); each observer has one function per setting.
   (i) every +-1-valued function of the complete record (constants included); (ii) the parity of a non-empty set of
   the record's four values (15 per setting and observer, as the recorded scorer does) - primary; the same with the
   constant outcome (empty set) allowed is reported beside as `score_ii_with_constant`, not judged; (iii) every
   +-1-valued function of the record's three old values (the record with its fresh value summed out). In (d) (ii) has
   31 non-empty sets and (iii) four old values.
9. **Exact maximisation for (i) and (iii).** With all four tables scaled to the common denominator L (the least
   common multiple of the four totals), the value is an integer over L. The side with fewer generators is enumerated:
   generators are the record values with a non-zero column (Bob) or row (Alice) of the two tables of one setting,
   and generators positively proportional to each other are merged (the value, after the other side's best response,
   is a sum of absolute values of linear forms, convex in the enumerated side's signs, so its largest value has equal
   signs on positively proportional generators). Every sign assignment of the merged generators is enumerated (one sign
   fixed: negating every function leaves the value), the other side answers best by the sum of absolute values,
   in int64 when 4L < 2^62 and in Python integers otherwise. The argmax functions are re-evaluated in Fractions from the
   tables and must give the same value (asserted). Beside it, `chsh_functions_brute` does what the brief describes with
   no merging: every pair of Alice's functions on the record values that occur, Bob's best response, the four
   placements; it is run on every test where Alice has at most 22 occurring record values in total, and must agree
   (asserted). The scoring code is first run by `--part selftest` on objects that are not this study's: 150 drawn
   tables of one- and two-bit records against the definition itself (every function on both sides; every parity on
   both sides, with and without the constant), 40 drawn three-bit tables merged against unmerged, a non-local box
   (value 4), and the recorded scorer's own four-type example against `evaluate(M)`. Seed 2026112399.
10. **Check (c), dependence.** "(s1, s2) depends on Bob's choice and not on Alice's" (P2) is read: for every one of
    Bob's choices the distribution of (s1, s2) is the same under Alice's two choices, and for some one of Alice's
    choices it differs between Bob's two. Whether it differs for both of Alice's choices is reported beside. "The joint
    distribution of every distinction held by each observer's own knots, with its fresh one": Alice, x1 x2 x3 c s1 s2
    h1 h2 zA; Bob, y1 y2 y3 t m1 m2 s1 k1 k2 s2 zB (s1 and s2 are held by knots of both). It depends on the far choice
    when for some own choice the two far choices give different distributions; the change (total variation) is
    reported for each own choice.
11. **Check (c), the old words' distribution held fixed.** Reference: one of the four choices (a*, b*) of the pair
    (x2, x3) against (y2, y3). An old word w (an assignment of the 16 old distinctions allowed by the eleven old knots)
    has, in the stage-1 structure (a*, b*), weight n*(w) = the number of its completions there (allowed stage-1 words
    whose old part is w; counted from the enumeration, not from a formula). Under each choice (a, b) every allowed
    stage-1 word u of structure (a, b) with old part w gets weight n*(w) / n_ab(w), n_ab(w) the number of completions
    of w in structure (a, b): each old word keeps its reference weight in total, divided equally among its completions
    under the choice at hand. Weights are kept as the integers 4 n*(w) / n_ab(w) (divisibility and the totals are
    asserted). Hidden and the three scores are then computed exactly as in (b) from these weighted tables, for each of
    the four references. Beside, not judged: the old structure's own weighting (every allowed old word weight 1) as a
    fifth reference.
12. **Check (d).** The nine stage-1 structures (x2, x3, c) by (y2, y3, t). Hidden for a choice of Alice's: her
    five-value record has one distribution under all three of Bob's choices; reported for every one of the nine
    choices and for each observer. "The largest score over its two-by-two sub-tests": the nine sub-tests made of two of
    Alice's three choices and two of Bob's, each scored as in (b) on the five-value records; score (i) is the score
    asked for, (ii) and (iii) beside; the largest is reported over all nine and over the hidden ones.
13. **Check (e), leaving knots out.** A left-out knot is removed; a distinction no remaining knot holds is gone; the
    others keep their names. "Round 1 of rule Q still makes exactly two one-parent births on x1 and y1 with at least
    two options each" is read strictly (primary, judged for P4): round 1 extends (no shortage), makes exactly two births
    in all, both one-parent, one taking x1 and the other y1, and each of these parents shares at least two distinctions
    when the round starts. Beside, not judged (loose reading): one-parent births taking x1 and y1 with at least two
    options each exist, other births allowed; for those, (b) is computed with every other birth not-all-equal and
    every choice of every other re-reading birth enumerated, held the same across the four stage-1 structures of a test.
    Structures in which x1 or y1 is held by no knot fail at once. If a birth on x1 or y1 got more than one fresh
    distinction, its record would hold all of them. Where the conditions hold, (b) is run on every pair of option pairs
    the structure has (C(nA, 2) C(nB, 2)); a hidden excess there is a test with both records hidden and score (i) above 2.
14. **Check (f).** The nine parity knots are, in the note's order, even(x1,x2,x3,c), even(x2,h1,h2), odd(x3,h1,h2),
    even(y1,y2,y3,t), even(t,m1,m2), even(s1,m1,m2), even(y2,k1,k2), odd(y3,k1,k2), odd(s2,k1,k2); assignment number
    sum 2^j over the odd ones (j their place in that list); the note's structure is one of the 512 (flagged). The two
    old not-all-equal knots and the newborns are unchanged; round 1 reads holdings only, so its births are those of (a)
    for every assignment. For each assignment the pair (x2, x3) against (y2, y3) is evaluated as in (b). An assignment
    whose stage-1 structures have no allowed word in one of them has no score and is counted apart. "A hidden excess":
    both records hidden and score (i) above 2 (primary); the counts with (ii) and with (iii) are reported beside.
15. **Verdicts** apply the "Fails when" column literally. P1 "any differs": the two births each one-parent with one
    fresh distinction; three options each; for (x2, x3) against (y2, y3) each of the four stage-1 structures has 144
    allowed words, both records hidden, score (i) exactly 20/9; each of the other eight pairs hidden with score (i)
    equal to 19/9 or to 37/18. P2: no score (i), (ii) or (iii) above 2 under any of the four references (A11), and the
    pattern of A10. P3: every complete record of (d) unchanged by every far choice. P4: no structure of (e) meeting the
    strict reading has a test with a hidden excess. P5: score (iii) equals score (i) for (x2, x3) against (y2, y3).
16. **Row G.** (1) QGrowth with re-reading off (`qlaw.run_ab(stars, 'nae', 'O', reread=False, bound_next=False)`)
    against the recorded driver `lib.grow(stars, 'nae', 12, 5000)` on the funded draws of `lib.p3_draws()` (seed
    2026112301; funded: the recorded history neither stalls nor lacks a birth, as ONE-PARENT-REREAD's ticket A; 280
    expected): stars, knots per stage and outcome equal on every one, and 280 draws compared. Beside, on round 1 of the
    same draws: `plan_round1` with re-reading off against `end_operator.step` (status, parents, fresh counts, lookahead
    demand) and against QGrowth, and with re-reading on (conventions O and N) against QGrowth (status, parents, inputs,
    fresh, demand). G fails if any of these differs. (2) The recorded scorer `evaluate(M)`, M the 8x8 counts of the old
    structure's allowed words by (x1, o0, o1) and (y1, p0, p1) from this study's enumeration, for each of the nine
    pairs: its float score against this study's exact score (ii) (difference below 1e-9) and its hidden flag against
    this study's hidden; G fails if any differs. The recorded scorer is never used outside row G.
17. **Runs.** Every run as `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 timeout 600 prlimit
    --as=12884901888 .venv/bin/python -B <script> ...` from the repository root, at most four at once, output to
    `artifacts/SETTING-AS-REREAD-20261123-001A/SETTING-AS-REREAD-20261123-001A-E001_both_settings/` (JSON per part,
    `logs/<part>.log`). (f) may be split into slices of the 512 by `--lo/--hi`.

## B. Limits and findings during the runs

1. **Runs, in order.** `selftest` (passed), then `g_draws` and `main` together, then `e` (stopped, item 2) and `f`
   together, then `e` again (item 2), then `main` again (item 4), then `report.py`; each under five seconds and under
   250 MB. Statuses: `logs/runs.log`; output: `logs/<part>.log` (the stopped run of (e) in `logs/e_first_run_stopped.log`,
   the first run of `main` in `logs/main_first_run.log` and `main_first_run.json`).
5. **Compared after every number was on disk:** the thread's exploratory script
   `research/SETTING-AS-REREAD-20261123-001/thread_checks/eleven_knot_both_settings.py` was read and run once (it
   writes nothing). Its round 1 (two births, x1 with x2 and y1 with y2 under its convention, one fresh distinction
   each), its options, and for all nine pairs its word counts, hiding, score and the dependence of every distinction
   of each observer's knots on the far choice (Alice's depends, Bob's does not) are the same as this study's. Nothing
   in this study was changed after the comparison.
2. **The first run of (e) stopped** (assertion: a structure with more than 24 distinctions) at the structure without
   knots 1 and 6, which meets only the loose reading of A13 (six births in round 1, three of them with two fresh
   distinctions). The strict reading never has more than 18 distinctions. Its printed lines, and a listing of round 1
   of every structure of (e) made afterwards by a command that wrote nothing (the same functions), were seen before the
   rerun: the strict reading holds for exactly two structures, without knots 2 and 10 and without knots 3 and 4, and
   the loose reading for eight more; nothing of (b) had been computed for a strict structure. Change, to the
   computation only and only for the loose reading: `joint_summing_others` sums out the fresh distinctions of every
   birth other than those on x1 and y1 exactly (each is held by its newborn alone: a not-all-equal newborn whose other
   members are all equal has 2^f - 1 completions, else 2^f), and wherever such a stage-1 structure has at most 22
   distinctions the full word-by-word enumeration is also made and must give the same table (asserted). Structures
   with only the two births are enumerated word by word as before. No definition changed.
3. **A third reading of (e), added after the listing of item 2** and reported beside, not judged: round 1 makes
   exactly two one-parent births, on x1 and y1 with at least two options each, joint births allowed (`two_one_parent`).
   It is nearer the note's words ("exactly two one-parent births") than the loose reading of A13, which also admits a
   third one-parent birth. (Corrected before hand-off: a first draft of this item said the listing showed no joint
   birth beside exactly two one-parent births on x1 and y1. That misread the listing. In four structures, those
   without knots 1 and 8, 1 and 9, 2 and 8, and 2 and 9, a joint birth of Bob's live knot with knot 7 or 10 stands
   beside them, so this reading picks out six structures: the two of the strict reading and these four. None of the
   six has a hidden excess.)
4. **Added to `main` after its values were seen, beside (c), not judged:** for each observer, whether the joint
   distribution of its own distinctions without s1 and s2 (Alice: x1 x2 x3 c h1 h2 zA; Bob: y1 y2 y3 t m1 m2 k1 k2 zB)
   depends on the far choice (`own_without_s1_s2`). Asked because (c) found that Alice's own distinctions depend on
   Bob's choice while her complete record does not; it says whether the dependence is carried by the two shared
   distinctions alone. `main` was rerun for it; every other key of `main.json` was compared with the first run's file
   (kept as `main_first_run.json`) and is identical.
