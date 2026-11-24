# Deviations and readings: THIRD-HOLDER-20261123-001A-E001

Every definition of the frozen pre-registration (`research/THIRD-HOLDER-20261123-001A/preregistration.md`) is unchanged.
Where the note was open, or where a run could not be done as written, the reading taken is listed here. Nothing was tuned
after values were seen.

1. **Code reused.** The 18 knots are copied from `research/REVIEW-LEADS-20261123-001/posthoc/three_holders_check.py`. The
   score (non-empty parities of each observer's record bits, the four sign patterns with one minus sign, absolute value),
   the hiding condition and the largest change follow `evaluate` in
   `docs/prompts/missed_leads_checks/finished_weighting_chsh.py` and `common.py` of `REVIEW-LEADS-20261123-001C-E001`; they
   are re-implemented in `common.py` here for k births, from joint tables of complete records. Row G also runs the starter's
   own `evaluate` on the old-word table.
2. **Canonical test.** The knot checker needs one place named as the contact. Each knot was tested with every choice of
   contact place (three per knot); every choice passes. The births and the copying knots are tested the same way.
3. **Full enumeration.** "Every knot tested on every assignment": the code evaluates every knot on every assignment of all
   distinctions (no early exit, no factorisation by side), 64 assignments per machine word with numpy bit operations; the
   record distinctions index the chunks. Two further checks were added that the note does not list: an engine self-test
   against a plain itertools enumeration on 200 seeded random structures (`selftest.py`), and an exhaustive backtracking
   search over the whole finished structure (each assignment is either listed or excluded by a knot that a partial
   assignment already violates; no factorisation by side).
4. **Parity births.** "Parity births in place of not-all-equal births" was run with even births and with odd births.
5. **Control weighting.** Each finished word of an old word with n lawful extensions has weight 1/n; computed in integers
   by scaling every weight by (2^k)^2.
6. **Value-keyed setting.** The functions are of the keyed observer's three old values (256). The change was computed for
   both observers keyed, both fixed settings of the other, and all ordered pairs of functions; the overall maximum and the
   attaining pairs are reported for each case. The normalized-per-setting reading was taken to weight the words of the
   finished structure at (a, b) by 1/Z_ab (Z_ab its number of allowed words) before pooling. Beside the pair maximum, the
   change relative to a fixed setting (a pair with a constant function) and the six functions keyed to one old value (the
   earlier study's policy test, pencil 1/9) are reported.
7. **Several births: the copies.** The old structure holds k loose copies of each of x1, x2, x3, y1, y2, y3 (the original
   and k - 1 copies, made by even or odd knots on the copying pairs a b, d e, p q, r t as in the original structure), for
   both settings; a setting's births take the copies of its two distinctions and leave the others loose. Extra holders
   (holders beyond two, summed over distinctions) were counted in the old structure and in each finished structure; the
   numbers agree because a birth only takes loose distinctions.
8. **Several births: enumeration.** k = 2 (36 distinctions, 2^36 assignments per finished structure) was enumerated in full
   for all four finished structures. Settings (0,0) ran as one run (221 s); the shared machine was then loaded by other
   sessions, a whole run would not have ended in ten minutes, and the other three were split into four runs each by the
   values of the record distinctions (`item_p3.py full 2 SA SB PART 4`), merged in the summary. Three whole runs of those
   structures that had been started were stopped by me before they ended and their partial output was deleted; nothing
   from them is used. k = 3 (44 distinctions, 2^44 assignments per finished structure, 256 times the k = 2 work, about 16
   hours per finished structure at the measured rate) does not fit; it was verified by side tables and by the exhaustive
   backtracking search over the whole structure, which agree exactly.
9. **Ceiling: the record.** Weight ratio rho = 2^k was read as k births per setting: the record is the three old values and
   k fresh ones, the fresh ones distributed as k not-all-equal births give them (every value when the chosen inputs are
   unequal, the single value 1 - x1 for each when they are equal), and the outcomes are the parities of all 3 + k record
   bits. Exact hiding of both complete records is the condition of item 1.
10. **Ceiling: the method.** With the ratios of the totals c = Z_00/Z_01 and c' = Z_00/Z_10 held as parameters, hiding is
    linear and the score with fixed outcomes is linear: a linear program in the 64 weights. The seeded optimisation (4,000
    starts per ratio, seeds 1,000,000 * rho + start) draws (log c, log c') uniformly in (-log rho, log rho) and a random
    outcome choice, alternates the linear program with a re-choice of the best outcomes, then moves (c, c') by Nelder-Mead
    (40 evaluations, two rounds) with re-choice. Exact re-verification: the ratios are rationalised, the linear program is
    re-solved, and its solution is re-derived exactly by Gaussian elimination in rationals on its support; the exact
    distribution is then evaluated with the same exact code as the structures. Runs were split into eight runs of 500
    starts per ratio. The first launch of twelve of them ended with an error when writing its output (a numpy boolean
    that the JSON writer refused); the bug was fixed and the same seeds were run again, giving the results used. Their
    logs are kept in `logs/failed_first_launch/`. Results at 2 whose float value exceeds the proved bound for their own
    ratios by up to 3.0e-8 occur only with a ratio at the end of its range, where both equal 2 up to the solver's
    tolerance; none exceeds it by 1e-7.
11. **Ceiling: a proof, added.** The pre-registration asked for exact solution where the problem is linear and seeded
    optimisation otherwise, and for a proof only if one could be given. A proof of the ceiling at every ratio was found
    (written out in the result note) and is reported as the result; the seeded optimisation and the linear programs are
    reported beside it as the pre-registered method. The proof uses a relaxation (hidden values grouped by weight type and
    outcome pair, any +-1 outcomes); a check of that relaxation by linear programs on 39 x 39 values of (c, c') per ratio
    (`item_p4.py relax`) agrees with the proved formula 2 + 2 T(c) T(c') to 1.5e-14.
12. **Development runs.** Before the scripts were fixed, inline trial runs (no files kept) timed the engine, tried the
    relaxation linear program on a set of (c, c') values (its maximum was the family's value at c = c' = 1 for each ratio,
    which suggested the proof), and timed 20 seeded starts per ratio. The seeded method was not changed after the timing
    trial. Runs were made from the experiment folder with `timeout 600 prlimit --as=12884901888`; several single-process
    runs ran at the same time on the shared machine.
