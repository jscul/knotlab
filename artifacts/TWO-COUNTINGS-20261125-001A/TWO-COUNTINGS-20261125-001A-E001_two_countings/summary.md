# Two countings of a structure’s allowed states, side by side: results of TWO-COUNTINGS-20261125-001A-E001

Computed by an engine written from the frozen texts, independent of the drafter’s prototype. Referee pending. Every weighting here is supplied. "Counting from the finish": each allowed state of the finished structure counts once. "Counting from the start": each allowed state of the start counts once, and at each birth an old state’s weight is divided equally among its completions. A rule is called a knot only once it has passed the knot test in the whole structure. Readings taken: `deviations.md` of the experiment folder. No claim is made about physics, physical space or time, living things or minds.

**Notes added after an independent check** (the checker's report is in the study's folder under `checks/`; the result note of the ticket carries the checked numbers). Names such as "11-knot", "10-knot" and "8-knot" below are the earlier studies' names for their structures and count rules: some of those rules are not knots in the whole structure (the section on the knot test says which). In the table, T07's knot column applies to 280 of its 680 histories; in the other 400 every rule passes. T10's structures were all checked by the canonical command; the "not run" in its column belongs to the 18-knot structures. The canonical command ran on 7,406 rules in all, 171 of them in the early run, failing rules among them. One of the 133 class orders of the smallest gain loses no weight (132 lose some). In the examples' table the column headed "Weight kept" gives the weight lost. The four-correlation score is the literature's CHSH form of a Bell inequality, named here once.

## Gates (part 1)

37 checks, 0 failed. Brute force equals the engine on the 11-knot and smallest-gain structures (allowed states, completions, counting from the start); the score’s merged method equals the unmerged one and an enumeration of both sides’ functions; the parity score equals a direct enumeration; Known 1–3 reproduced.

## Predictions

| # | Prediction | Verdict | Numbers |
| --- | --- | --- | --- |
| P1 | Counting from the finish reproduces every recorded number of parts 2 and 3 | held | Known 1-3 (part 1 gates): yes; 894 records of part 2 (ONE-PARENT-REREAD 680, rule R 214): the recorded finish value: yes; the 10-knot 55/27 per history (and 109/54 for the pairs with c): yes; the 18-knot 20/9 hidden, 1,152 allowed states per finished structure, 512 start states: yes; the 8/3 case: 8/3, not hidden, largest record change 1/6: yes; the 18-knot keyed setting: 2/9 between two keyings, 1/9 against a fixed setting (finish, pooled): yes; Known 4: 128 of 512 sign assignments at 20/9 hidden (finish): yes; Known 5: the 11-knot keyed setting, up to 2/9 from the finish (pooled), 0 from the start: yes |
| P2 | Every structure of parts 2 and 3 that meets the hypotheses scores at most 2 for both outcome classes (exactly 2 over all two-valued functions) with both records hidden; the unmeasured structures meet them | held | 1816 lemma verdicts in part 2 (every counting from a common stage before the settings, every structure, variant and record): {'hypotheses met and at most 2 (exactly 2 over all two-valued functions), both records hidden': 1816}; part 3: all 512 at exactly 2, hidden, from the start; pooled 10-knot rows from the start at 2, hidden: True |
| P3 | Each example E1-E7 gives a score above 2 or a record changed by the other’s setting | held | E1 20/9 (changes 0, 0); E2 104/45 (changes 0, 0); E3 7/3 (changes 0, 1/6); E4 17/6 (changes 1/3, 1/3); E5 11/4 (changes 1/4, 0); E6 5/2 (changes 1/4, 0); E7 5/2 (changes 1/4, 0) |
| P4 | Every order in C5’s class scores 2 and is hidden | held | eleven_registered_400: 104 in the class, 104 at 2 hidden; eleven_new_400: 92 in the class, 92 at 2 hidden; smallest_gain_400: 133 in the class, 133 at 2 hidden |
| P6a | Under Q-OLDEST or Q-NEWEST some renumbered start grows a different finished structure | held | smallest gain: part: Q-OLDEST 34 of 48 different, Q-NEWEST 34 of 48 different; census 30: Q-OLDEST 53 of 60 different, Q-NEWEST 53 of 60 different; census 59: Q-OLDEST 0 of 52 different, Q-NEWEST 0 of 52 different; census 82: Q-OLDEST 57 of 64 different, Q-NEWEST 57 of 64 different; census 84: Q-OLDEST 55 of 64 different, Q-NEWEST 55 of 64 different; census 105: Q-OLDEST 46 of 56 different, Q-NEWEST 46 of 56 different; census 112: Q-OLDEST 51 of 60 different, Q-NEWEST 51 of 60 different; census 114: Q-OLDEST 45 of 52 different, Q-NEWEST 45 of 52 different; census 120: Q-OLDEST 58 of 64 different, Q-NEWEST 58 of 64 different; census 125: Q-OLDEST 0 of 52 different, Q-NEWEST 0 of 52 different; census 146: Q-OLDEST 0 of 60 different, Q-NEWEST 0 of 60 different |
| P6b | Where the finished structures are the same, counting from the start gives the same weighting carried back; where they differ, "no comparison" | held | 0 weightings differ on the same structure; 356 same by enumeration, 110 same by the renaming of the whole history (too large to enumerate), 0 not decided |
| P7 | The 10-knot 55/27 becomes 2 counted from the start, per history and pooled | held | {"ten A x2-x3/y3-t": {"per history, from the start": ["2", "2"], "per history, hidden": [true, true], "pooled, from the start": "2", "per history, from the finish": ["55/27", "55/27"], "pooled from the finish (TD 3.5)": "2", "pooled from the finish (nu uniform)": "2"}, "ten B x2-x3/y2-t": {"per history, from the start": ["2", "2"], "per history, hidden": [true, true], "pooled, from the start": "2", "per history, from the finish": ["55/27", "55/27"], "pooled from the finish (TD 3.5)": "2", "pooled from the finish (nu uniform)": "2"}} |
| P8 | The two four-place rules of the 11-knot structure fail K2 in all 512 sign assignments, and the 128 at 20/9 are exactly those whose ties are inequalities | held | K2 fails for both in all 512 (start and the four finished structures each): True; 128 at 20/9 = the 128 with both ties inequalities: True; no other rule fails in any of the 512: True; finish values {"('2', True)": 256, "('20/9', True)": 128, "('194/91', False)": 64, "('23/10', False)": 64} |
| P9 | The counting-from-the-start pair tables decide the next birth count on all 194 not-all-equal types | held | 194 types (183 connected, 11 disconnected); 194 distinct tables under renaming; groups sharing a table: named 0, under renaming 0; gates (finish pair counts and totals equal the archive; start tables equal enumeration up to width 20): True |

## The lemma (C2): each registered structure and example

Scores over all two-valued functions; "par" the signed parity score, "|par|" its absolute form (R 16). Hidden: both records unchanged by the other’s setting. Verdict for counting from a common stage before the settings.

| Structure | Variant | Counting | Score | par | abs par | Hidden (changes) | Hypotheses failing | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| eleven x2-x3/y2-y3 | only | from the start | 2 | 2 | 2 | yes (0, 0) |  | hypotheses met and at most 2 (exactly 2 over all two-valued functions), both records hidden |
| eleven x2-x3/y2-y3 | only | from the finish | 20/9 | 20/9 | 20/9 | yes (0, 0) |  | (no verdict: the finish breaks the premise) |
| eleven x2-x3/y2-y3 | only | mixed stage (the first observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| eleven x2-x3/y2-y3 | only | mixed stage (the second observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| eleven x2-x3/y2-t | only | from the start | 2 | 2 | 2 | yes (0, 0) |  | hypotheses met and at most 2 (exactly 2 over all two-valued functions), both records hidden |
| eleven x2-x3/y2-t | only | from the finish | 19/9 | 19/9 | 19/9 | yes (0, 0) |  | (no verdict: the finish breaks the premise) |
| eleven x2-x3/y2-t | only | mixed stage (the first observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| eleven x2-x3/y2-t | only | mixed stage (the second observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| eleven x2-x3/y3-t | only | from the start | 2 | 2 | 2 | yes (0, 0) |  | hypotheses met and at most 2 (exactly 2 over all two-valued functions), both records hidden |
| eleven x2-x3/y3-t | only | from the finish | 19/9 | 19/9 | 19/9 | yes (0, 0) |  | (no verdict: the finish breaks the premise) |
| eleven x2-x3/y3-t | only | mixed stage (the first observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| eleven x2-x3/y3-t | only | mixed stage (the second observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| eleven x2-c/y2-y3 | only | from the start | 2 | 2 | 2 | yes (0, 0) |  | hypotheses met and at most 2 (exactly 2 over all two-valued functions), both records hidden |
| eleven x2-c/y2-y3 | only | from the finish | 19/9 | 19/9 | 19/9 | yes (0, 0) |  | (no verdict: the finish breaks the premise) |
| eleven x2-c/y2-y3 | only | mixed stage (the first observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| eleven x2-c/y2-y3 | only | mixed stage (the second observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| eleven x2-c/y2-t | only | from the start | 2 | 2 | 2 | yes (0, 0) |  | hypotheses met and at most 2 (exactly 2 over all two-valued functions), both records hidden |
| eleven x2-c/y2-t | only | from the finish | 37/18 | 37/18 | 37/18 | yes (0, 0) |  | (no verdict: the finish breaks the premise) |
| eleven x2-c/y2-t | only | mixed stage (the first observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| eleven x2-c/y2-t | only | mixed stage (the second observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| eleven x2-c/y3-t | only | from the start | 2 | 2 | 2 | yes (0, 0) |  | hypotheses met and at most 2 (exactly 2 over all two-valued functions), both records hidden |
| eleven x2-c/y3-t | only | from the finish | 37/18 | 37/18 | 37/18 | yes (0, 0) |  | (no verdict: the finish breaks the premise) |
| eleven x2-c/y3-t | only | mixed stage (the first observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| eleven x2-c/y3-t | only | mixed stage (the second observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| eleven x3-c/y2-y3 | only | from the start | 2 | 2 | 2 | yes (0, 0) |  | hypotheses met and at most 2 (exactly 2 over all two-valued functions), both records hidden |
| eleven x3-c/y2-y3 | only | from the finish | 19/9 | 19/9 | 19/9 | yes (0, 0) |  | (no verdict: the finish breaks the premise) |
| eleven x3-c/y2-y3 | only | mixed stage (the first observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| eleven x3-c/y2-y3 | only | mixed stage (the second observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| eleven x3-c/y2-t | only | from the start | 2 | 2 | 2 | yes (0, 0) |  | hypotheses met and at most 2 (exactly 2 over all two-valued functions), both records hidden |
| eleven x3-c/y2-t | only | from the finish | 37/18 | 37/18 | 37/18 | yes (0, 0) |  | (no verdict: the finish breaks the premise) |
| eleven x3-c/y2-t | only | mixed stage (the first observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| eleven x3-c/y2-t | only | mixed stage (the second observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| eleven x3-c/y3-t | only | from the start | 2 | 2 | 2 | yes (0, 0) |  | hypotheses met and at most 2 (exactly 2 over all two-valued functions), both records hidden |
| eleven x3-c/y3-t | only | from the finish | 37/18 | 37/18 | 37/18 | yes (0, 0) |  | (no verdict: the finish breaks the premise) |
| eleven x3-c/y3-t | only | mixed stage (the first observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| eleven x3-c/y3-t | only | mixed stage (the second observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| smallest gain | only | from the start | 2 | 2 | 2 | yes (0, 0) |  | hypotheses met and at most 2 (exactly 2 over all two-valued functions), both records hidden |
| smallest gain | only | from stage 1 | 2 | 2 | 2 | yes (0, 0) |  | hypotheses met and at most 2 (exactly 2 over all two-valued functions), both records hidden |
| smallest gain | only | from the finish | 61/30 | 61/30 | 61/30 | yes (0, 0) |  | (no verdict: the finish breaks the premise) |
| smallest gain | only | mixed stage (the first observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| smallest gain | only | mixed stage (the second observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| seven | only | from the start | 2 | 2 | 2 | yes (0, 0) |  | hypotheses met and at most 2 (exactly 2 over all two-valued functions), both records hidden |
| seven | only | from the finish | 19/9 | 19/9 | 19/9 | yes (0, 0) |  | (no verdict: the finish breaks the premise) |
| seven | only | mixed stage (the first observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| seven | only | mixed stage (the second observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| eight | only | from the start | 2 | 2 | 2 | yes (0, 0) |  | hypotheses met and at most 2 (exactly 2 over all two-valued functions), both records hidden |
| eight | only | from the finish | 20/9 | 20/9 | 20/9 | yes (0, 0) |  | (no verdict: the finish breaks the premise) |
| eight | only | mixed stage (the first observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| eight | only | mixed stage (the second observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| nine | only | from the start | 2 | 2 | 2 | yes (0, 0) |  | hypotheses met and at most 2 (exactly 2 over all two-valued functions), both records hidden |
| nine | only | from the finish | 20/9 | 20/9 | 20/9 | yes (0, 0) |  | (no verdict: the finish breaks the premise) |
| nine | only | mixed stage (the first observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| nine | only | mixed stage (the second observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| eighteen | only | from the start | 2 | 2 | 2 | yes (0, 0) |  | hypotheses met and at most 2 (exactly 2 over all two-valued functions), both records hidden |
| eighteen | only | from the finish | 20/9 | 20/9 | 20/9 | yes (0, 0) |  | (no verdict: the finish breaks the premise) |
| eighteen | only | mixed stage (the first observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| eighteen | only | mixed stage (the second observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| ten A x2-x3/y3-t | third birth takes t | from the start | 2 | 2 | 2 | yes (0, 0) |  | hypotheses met and at most 2 (exactly 2 over all two-valued functions), both records hidden |
| ten A x2-x3/y3-t | third birth takes t | from the finish | 55/27 | 55/27 | 55/27 | yes (0, 0) |  | (no verdict: the finish breaks the premise) |
| ten A x2-x3/y3-t | third birth takes t | mixed stage (the first observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| ten A x2-x3/y3-t | third birth takes t | mixed stage (the second observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| ten A x2-x3/y3-t | third birth takes y3 | from the start | 2 | 2 | 2 | yes (0, 0) |  | hypotheses met and at most 2 (exactly 2 over all two-valued functions), both records hidden |
| ten A x2-x3/y3-t | third birth takes y3 | from the finish | 55/27 | 55/27 | 55/27 | yes (0, 0) |  | (no verdict: the finish breaks the premise) |
| ten A x2-x3/y3-t | third birth takes y3 | mixed stage (the first observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| ten A x2-x3/y3-t | third birth takes y3 | mixed stage (the second observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| ten A x2-x3/y3-t | pooled | from the start, pooled (nu uniform over histories) | 2 | 2 | 2 | yes (0, 0) |  |  |
| ten A x2-x3/y3-t | pooled | from the finish, pooled (each history and state once, TD 3.5) | 2 | 2 | 2 | yes (0, 0) |  |  |
| ten A x2-x3/y3-t | pooled | from the finish, nu uniform over histories | 2 | 2 | 2 | yes (0, 0) |  |  |
| ten A x2-c/y3-t | third birth takes t | from the start | 2 | 2 | 2 | yes (0, 0) |  | hypotheses met and at most 2 (exactly 2 over all two-valued functions), both records hidden |
| ten A x2-c/y3-t | third birth takes t | from the finish | 109/54 | 109/54 | 109/54 | yes (0, 0) |  | (no verdict: the finish breaks the premise) |
| ten A x2-c/y3-t | third birth takes t | mixed stage (the first observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| ten A x2-c/y3-t | third birth takes t | mixed stage (the second observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| ten A x2-c/y3-t | third birth takes y3 | from the start | 2 | 2 | 2 | yes (0, 0) |  | hypotheses met and at most 2 (exactly 2 over all two-valued functions), both records hidden |
| ten A x2-c/y3-t | third birth takes y3 | from the finish | 109/54 | 109/54 | 109/54 | yes (0, 0) |  | (no verdict: the finish breaks the premise) |
| ten A x2-c/y3-t | third birth takes y3 | mixed stage (the first observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| ten A x2-c/y3-t | third birth takes y3 | mixed stage (the second observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| ten A x2-c/y3-t | pooled | from the start, pooled (nu uniform over histories) | 2 | 2 | 2 | yes (0, 0) |  |  |
| ten A x2-c/y3-t | pooled | from the finish, pooled (each history and state once, TD 3.5) | 2 | 2 | 2 | yes (0, 0) |  |  |
| ten A x2-c/y3-t | pooled | from the finish, nu uniform over histories | 2 | 2 | 2 | yes (0, 0) |  |  |
| ten A x3-c/y3-t | third birth takes t | from the start | 2 | 2 | 2 | yes (0, 0) |  | hypotheses met and at most 2 (exactly 2 over all two-valued functions), both records hidden |
| ten A x3-c/y3-t | third birth takes t | from the finish | 109/54 | 109/54 | 109/54 | yes (0, 0) |  | (no verdict: the finish breaks the premise) |
| ten A x3-c/y3-t | third birth takes t | mixed stage (the first observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| ten A x3-c/y3-t | third birth takes t | mixed stage (the second observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| ten A x3-c/y3-t | third birth takes y3 | from the start | 2 | 2 | 2 | yes (0, 0) |  | hypotheses met and at most 2 (exactly 2 over all two-valued functions), both records hidden |
| ten A x3-c/y3-t | third birth takes y3 | from the finish | 109/54 | 109/54 | 109/54 | yes (0, 0) |  | (no verdict: the finish breaks the premise) |
| ten A x3-c/y3-t | third birth takes y3 | mixed stage (the first observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| ten A x3-c/y3-t | third birth takes y3 | mixed stage (the second observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| ten A x3-c/y3-t | pooled | from the start, pooled (nu uniform over histories) | 2 | 2 | 2 | yes (0, 0) |  |  |
| ten A x3-c/y3-t | pooled | from the finish, pooled (each history and state once, TD 3.5) | 2 | 2 | 2 | yes (0, 0) |  |  |
| ten A x3-c/y3-t | pooled | from the finish, nu uniform over histories | 2 | 2 | 2 | yes (0, 0) |  |  |
| ten B x2-x3/y2-t | third birth takes t | from the start | 2 | 2 | 2 | yes (0, 0) |  | hypotheses met and at most 2 (exactly 2 over all two-valued functions), both records hidden |
| ten B x2-x3/y2-t | third birth takes t | from the finish | 55/27 | 55/27 | 55/27 | yes (0, 0) |  | (no verdict: the finish breaks the premise) |
| ten B x2-x3/y2-t | third birth takes t | mixed stage (the first observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| ten B x2-x3/y2-t | third birth takes t | mixed stage (the second observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| ten B x2-x3/y2-t | third birth takes y2 | from the start | 2 | 2 | 2 | yes (0, 0) |  | hypotheses met and at most 2 (exactly 2 over all two-valued functions), both records hidden |
| ten B x2-x3/y2-t | third birth takes y2 | from the finish | 55/27 | 55/27 | 55/27 | yes (0, 0) |  | (no verdict: the finish breaks the premise) |
| ten B x2-x3/y2-t | third birth takes y2 | mixed stage (the first observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| ten B x2-x3/y2-t | third birth takes y2 | mixed stage (the second observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| ten B x2-x3/y2-t | pooled | from the start, pooled (nu uniform over histories) | 2 | 2 | 2 | yes (0, 0) |  |  |
| ten B x2-x3/y2-t | pooled | from the finish, pooled (each history and state once, TD 3.5) | 2 | 2 | 2 | yes (0, 0) |  |  |
| ten B x2-x3/y2-t | pooled | from the finish, nu uniform over histories | 2 | 2 | 2 | yes (0, 0) |  |  |
| ten B x2-c/y2-t | third birth takes t | from the start | 2 | 2 | 2 | yes (0, 0) |  | hypotheses met and at most 2 (exactly 2 over all two-valued functions), both records hidden |
| ten B x2-c/y2-t | third birth takes t | from the finish | 109/54 | 109/54 | 109/54 | yes (0, 0) |  | (no verdict: the finish breaks the premise) |
| ten B x2-c/y2-t | third birth takes t | mixed stage (the first observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| ten B x2-c/y2-t | third birth takes t | mixed stage (the second observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| ten B x2-c/y2-t | third birth takes y2 | from the start | 2 | 2 | 2 | yes (0, 0) |  | hypotheses met and at most 2 (exactly 2 over all two-valued functions), both records hidden |
| ten B x2-c/y2-t | third birth takes y2 | from the finish | 109/54 | 109/54 | 109/54 | yes (0, 0) |  | (no verdict: the finish breaks the premise) |
| ten B x2-c/y2-t | third birth takes y2 | mixed stage (the first observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| ten B x2-c/y2-t | third birth takes y2 | mixed stage (the second observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| ten B x2-c/y2-t | pooled | from the start, pooled (nu uniform over histories) | 2 | 2 | 2 | yes (0, 0) |  |  |
| ten B x2-c/y2-t | pooled | from the finish, pooled (each history and state once, TD 3.5) | 2 | 2 | 2 | yes (0, 0) |  |  |
| ten B x2-c/y2-t | pooled | from the finish, nu uniform over histories | 2 | 2 | 2 | yes (0, 0) |  |  |
| ten B x3-c/y2-t | third birth takes t | from the start | 2 | 2 | 2 | yes (0, 0) |  | hypotheses met and at most 2 (exactly 2 over all two-valued functions), both records hidden |
| ten B x3-c/y2-t | third birth takes t | from the finish | 109/54 | 109/54 | 109/54 | yes (0, 0) |  | (no verdict: the finish breaks the premise) |
| ten B x3-c/y2-t | third birth takes t | mixed stage (the first observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| ten B x3-c/y2-t | third birth takes t | mixed stage (the second observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| ten B x3-c/y2-t | third birth takes y2 | from the start | 2 | 2 | 2 | yes (0, 0) |  | hypotheses met and at most 2 (exactly 2 over all two-valued functions), both records hidden |
| ten B x3-c/y2-t | third birth takes y2 | from the finish | 109/54 | 109/54 | 109/54 | yes (0, 0) |  | (no verdict: the finish breaks the premise) |
| ten B x3-c/y2-t | third birth takes y2 | mixed stage (the first observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| ten B x3-c/y2-t | third birth takes y2 | mixed stage (the second observer first) | 2 | 2 | 2 | yes (0, 0) |  | (no verdict: the mixed stage is not common) |
| ten B x3-c/y2-t | pooled | from the start, pooled (nu uniform over histories) | 2 | 2 | 2 | yes (0, 0) |  |  |
| ten B x3-c/y2-t | pooled | from the finish, pooled (each history and state once, TD 3.5) | 2 | 2 | 2 | yes (0, 0) |  |  |
| ten B x3-c/y2-t | pooled | from the finish, nu uniform over histories | 2 | 2 | 2 | yes (0, 0) |  |  |
| eight-thirds case | only | from the start | 2 | 2 | 2 | yes (0, 0) |  | hypotheses met and at most 2 (exactly 2 over all two-valued functions), both records hidden |
| eight-thirds case | only | from the finish | 8/3 | 8/3 | 8/3 | no (1/6, 1/6) |  | (no verdict: the finish breaks the premise) |
| eight-thirds case | only | mixed stage (the first observer first) | 7/3 | 7/3 | 7/3 | no (0, 1/6) |  | (no verdict: the mixed stage is not common) |
| eight-thirds case | only | mixed stage (the second observer first) | 7/3 | 7/3 | 7/3 | no (1/6, 0) |  | (no verdict: the mixed stage is not common) |

**The records of part 2** (each one history; counting from the part, from after the round, from the finish, and the two mixed stages):

| Source | Records | From the start | From stage 1 | From the finish (= the record’s number in every record) | Mixed stages | Verdicts |
| --- | ---: | --- | --- | --- | --- | --- |
| ONE-PARENT-REREAD uniform | 16 | 2 ×16 | 2 ×16 | 61/30 ×12, 31/15 ×4 | 2 ×16; 2 ×16 | {'hypotheses met and at most 2 (exactly 2 over ': 32} |
| ONE-PARENT-REREAD mixed | 664 | 2 ×664 | 2 ×664 | 109/54 ×552, 55/27 ×96, 61/30 ×12, 31/15 ×4 | 2 ×664; 2 ×664 | {'hypotheses met and at most 2 (exactly 2 over ': 1328} |
| REREAD-BIRTHS rule R | 214 | 2 ×214 | 2 ×214 | 127/63 ×56, 5293/2646 ×54, 6175/3087 ×36, 109/54 ×35, 1135/567 ×27, 973/486 ×5, 11162/5535 ×1 | 2 ×214; 2 ×214 | {'hypotheses met and at most 2 (exactly 2 over ': 428} |

**The examples (part 4)**, counted from the start (E1 from the finish; E2 from nothing, renormalised):

| Example | Breaks (TD 8.2) | Score | par | Change of the first / second record | Weight kept per setting pair | Hypotheses found failing | P3 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E0 | none | 2 | 2 | 0 / 0 | {"(0, 0)": "1", "(0, 1)": "1", "(1, 0)": "1", "(1, 1)": "1"} | none | 2 and hidden |
| E1 | the premise (no start before the settings) | 20/9 | 20/9 | 0 / 0 | {"(0, 0)": "1", "(0, 1)": "1", "(1, 0)": "1", "(1, 1)": "1"} | none | above 2 or changed |
| E2 | h1′, and h4's first clause as a consequence | 104/45 | 104/45 | 0 / 0 | lost: {"(0, 0)": "35/36", "(0, 1)": "71/72", "(1, 0)": "139/144", "(1, 1)": "283/288"} | not computed (R 25) | above 2 or changed |
| E3 | h2 (renormalised) | 7/3 | 7/3 | 0 / 1/6 | {"(0, 0)": "3/4", "(0, 1)": "3/4", "(1, 0)": "1/2", "(1, 1)": "1/2"} | h2 | above 2 or changed |
| E4 | h3′ | 17/6 | 17/6 | 1/3 / 1/3 | {"(0, 0)": "3/4", "(0, 1)": "1", "(1, 0)": "3/4", "(1, 1)": "3/4"} | h1′, h2, h3′ | above 2 or changed |
| E5 | h4, first clause (renormalised) | 11/4 | 5/2 | 1/4 / 0 | {"(0, 0)": "1/2", "(0, 1)": "1/2", "(1, 0)": "1/2", "(1, 1)": "1/2"} | h3′, h4 | above 2 or changed |
| E6 | h4, record clause | 5/2 | 5/2 | 1/4 / 0 | {"(0, 0)": "1", "(0, 1)": "1", "(1, 0)": "1", "(1, 1)": "1"} | h4 | above 2 or changed |
| E7 | h4, record clause | 5/2 | 5/2 | 1/4 / 0 | {"(0, 0)": "1", "(0, 1)": "1", "(1, 0)": "1", "(1, 1)": "1"} | h4 | above 2 or changed |
| E2 read as the 11th order (index 10), beside, not judged | (beside) | 2 |  |  /  | {"(0, 0)": "61/64", "(0, 1)": "29/32", "(1, 0)": "61/64", "(1, 1)": "29/32"} |  |  |
| other h2 candidate nae(x1, x2 or x3, h1), beside (Known 7), not judged | (beside) | 2 |  | 0 / 0 | {"(0, 0)": "3/4", "(0, 1)": "3/4", "(1, 0)": "3/4", "(1, 1)": "3/4"} | h2 |  |
| other h2 candidate nae(x1, x2 or x3, h2), beside (Known 7), not judged | (beside) | 2 |  | 0 / 0 | {"(0, 0)": "3/4", "(0, 1)": "3/4", "(1, 0)": "3/4", "(1, 1)": "3/4"} | h2 |  |

**Keyed settings** (the first observer keyed, TD 4.5): the largest change of the second record between two functions g (and against a constant function):

| Structure | Second observer fixed at | From the start | From the finish, pooled | Against a constant (start / finish) |
| --- | --- | --- | --- | --- |
| eleven (16 functions g) | 0 | 0 | 2/9 | 0 / 1/9 |
| eleven (16 functions g) | 1 | 0 | 2/9 | 0 / 1/9 |
| eighteen (256 functions g) | 0 | 0 | 2/9 | 0 / 1/9 |
| eighteen (256 functions g) | 1 | 0 | 2/9 | 0 / 1/9 |

## Construction orders (part 6)

| List | Orders | In C5’s class | In the class: at 2, hidden | Outside: at 2, hidden | Outside: above 2, hidden | Outside: above 2, not hidden | Largest hidden outside |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| eleven_registered_400 | 400 | 104 | 104 | 182 | 66 | 48 | 104/45 (orders [11, 147, 343, 357, 389, 395]) |
| eleven_new_400 | 400 | 92 | 92 | 182 | 75 | 51 | 104/45 (orders [38, 54, 109, 281, 299, 386]) |
| smallest_gain_400 | 400 | 133 | 133 | 126 | 14 | 127 | 55/27 (orders [63, 205]) |

Every order in the class loses weight at some knot and loses it equally across the four setting pairs (eleven_registered_400 104 of 104, eleven_new_400 92 of 92, smallest_gain_400 133 of 133).

## Grow again (part 7)

| Start | Law | Renumberings | Different finished structure | Same: weighting compared by enumeration (same) | Same: by the renaming of the whole history | Weighting differs |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| smallest gain: part | Q-OLDEST | 48 | 34 | 14 | 0 | 0 |
| smallest gain: part | Q-NEWEST | 48 | 34 | 14 | 0 | 0 |
| census 30 | Q-OLDEST | 60 | 53 | 0 | 7 | 0 |
| census 30 | Q-NEWEST | 60 | 53 | 0 | 7 | 0 |
| census 59 | Q-OLDEST | 52 | 0 | 52 | 0 | 0 |
| census 59 | Q-NEWEST | 52 | 0 | 52 | 0 | 0 |
| census 82 | Q-OLDEST | 64 | 57 | 0 | 7 | 0 |
| census 82 | Q-NEWEST | 64 | 57 | 0 | 7 | 0 |
| census 84 | Q-OLDEST | 64 | 55 | 0 | 9 | 0 |
| census 84 | Q-NEWEST | 64 | 55 | 0 | 9 | 0 |
| census 105 | Q-OLDEST | 56 | 46 | 0 | 10 | 0 |
| census 105 | Q-NEWEST | 56 | 46 | 0 | 10 | 0 |
| census 112 | Q-OLDEST | 60 | 51 | 0 | 9 | 0 |
| census 112 | Q-NEWEST | 60 | 51 | 0 | 9 | 0 |
| census 114 | Q-OLDEST | 52 | 45 | 0 | 7 | 0 |
| census 114 | Q-NEWEST | 52 | 45 | 0 | 7 | 0 |
| census 120 | Q-OLDEST | 64 | 58 | 0 | 6 | 0 |
| census 120 | Q-NEWEST | 64 | 58 | 0 | 6 | 0 |
| census 125 | Q-OLDEST | 52 | 0 | 52 | 0 | 0 |
| census 125 | Q-NEWEST | 52 | 0 | 52 | 0 | 0 |
| census 146 | Q-OLDEST | 60 | 0 | 60 | 0 | 0 |
| census 146 | Q-NEWEST | 60 | 0 | 60 | 0 | 0 |

## P9 (part 5) and the engine check (part 9)

P9: 194 types, 194 distinct counting-from-the-start pair tables under renaming, so no two types share a table and the tables decide the next birth count (and status) on all 194. Gates: the finish pair counts and totals equal the archive’s on every type; the start tables equal enumeration on every type of at most 20 names.

Engine check (TD 7.3 on the 100 census starts, 3 rounds): first round whose product varies, by law and knot law.

| Law / knot law | Growths | Made a birth | First parting at round | Not parted | Undecided | Rounds checked directly | Rule against direct: mismatches |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| ORDINARY / parity | 100 | 60 | {} | 60 | 0 | 149 | 0 |
| ORDINARY / nae | 100 | 60 | {'1': 59, '2': 1} | 0 | 0 | 149 | 0 |
| Q-OLDEST / parity | 100 | 60 | {} | 60 | 0 | 161 | 0 |
| Q-OLDEST / nae | 100 | 60 | {'1': 60} | 0 | 0 | 161 | 0 |
| Q-NEWEST / parity | 100 | 60 | {} | 60 | 0 | 151 | 0 |
| Q-NEWEST / nae | 100 | 60 | {'1': 60} | 0 | 0 | 151 | 0 |
| RING-LAW / parity | 100 | 99 | {} | 99 | 0 | 53 | 0 |
| RING-LAW / nae | 100 | 99 | {'1': 79, '2': 17, '3': 1} | 2 | 0 | 53 | 0 |
| COPY-LAW(CANCEL-RETIRE) / parity | 100 | 99 | {} | 99 | 0 | 79 | 0 |
| COPY-LAW(CANCEL-RETIRE) / nae | 100 | 99 | {'1': 79, '2': 20} | 0 | 0 | 79 | 0 |
| COPY-LAW(CANCEL-RETIRE)+MET(OLDEST) / parity | 100 | 99 | {} | 99 | 0 | 252 | 0 |
| COPY-LAW(CANCEL-RETIRE)+MET(OLDEST) / nae | 100 | 99 | {'1': 99} | 0 | 0 | 252 | 0 |

## The table of the record’s statements (C1)

| Row | Statement | From the finish | From the start | Verdict here | Verdict in table.json | Knots in the whole (here) | Source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T01 | hidden score, options (x2,x3) against (y2,y3), 11-knot structure | 20/9 hidden | 2 hidden | changed by 2/9 | changed by 2/9 | fails: even(x1,x2,x3,c) (K2); even(y1,y2,y3,t) (K2) [canonical: agrees] | recomputed here |
| T02 | the other eight option pairs | 19/9 or 37/18 hidden | 2 hidden (all eight) | changed by 1/9 or 1/18 | changed by 1/9 or 1/18 | fails: even(x1,x2,x3,c) (K2); even(y1,y2,y3,t) (K2); nae(x1,c,za) (K2); nae(y1,t,zb) (K2) [canonical: agrees] | recomputed here |
| T03 | the second observer's choice moves (s1,s2) | TV 1/3 | 0 | changed by 1/3 | changed by 1/3 | fails: even(x1,x2,x3,c) (K2); even(y1,y2,y3,t) (K2) [canonical: agrees] | recomputed here |
| T04 | 128 of 512 sign assignments give the hidden 20/9 | 128 of 512 at 20/9 (hidden) | 0 of 512 above 2; 512 at 2, hidden | changed: 128 to 0 | changed: 128 to 0 | fails (the two four-place rules, K2, in all 512; projection) | recomputed here |
| T05 | two 10-knot structures with three one-parent births | 55/27 hidden per history; pooled 2 (TD 3.5) and 2 (nu uniform) | 2 hidden, per history and pooled | changed by 1/27 (per history) | to compute in the ticket (part 2) | fails: even(x1,x2,x3,c) (K2) [canonical: agrees]; the starts: fails: even(x1,x2,x3,c) (K2) [canonical: agrees] | recomputed here |
| T06 | smallest gain: part, one rule-Q round, setting births | 61/30 hidden | 2 hidden (from the part), 2 hidden (after round 1) | changed by 1/30 | changed by 1/30 | fails: nae(x1,x2,za) (K2) [canonical: agrees] | recomputed here |
| T07 | the other 7 gaining parts (61/30 or 31/15) and the 27 parts with laws handed out (109/54, 55/27) | 109/54, 61/30, 55/27, 31/15 hidden (680 records reproduced) | 2 hidden in all 680 (from the part and after the round) | changed by 1/54, 1/30, 1/27, 1/15 | to compute in the ticket (part 2) | fails: nae(x1,x2,za) (K2) [canonical check not run (cut) / canonical: agrees] | recomputed here |
| T08 | negative: the remaining 5,710 parts never pass 1.692 (parity outcomes) | ≤ 1.692 | ≤ 2 by the lemma (parity outcomes: at most 2) | bound by argument only | bound by argument only | not tested | from table.json (not recomputed here) |
| T09 | smallest structure: 7 knots | 19/9 hidden | 2 hidden | changed by 1/9 | changed by 1/9 | all [canonical: agrees] | recomputed here |
| T10 | 8 knots | 20/9 hidden | 2 hidden | changed by 2/9 | changed by 2/9 | fails: even(y1,y2,y3,s1) (K2) [canonical: agrees / not run (more than 20 distinctions; projection only, as registered)] | recomputed here |
| T11 | the pencil 9-knot structure | 20/9 hidden | 2 hidden | changed by 2/9 | changed by 2/9 | all [canonical: agrees] | recomputed here |
| T12 | negative and search winner: none with 6 or fewer knots; 7 is the minimum (census under counting from the finish) | minimum 7 knots | no structure of any size has a hidden excess under the lemma's hypotheses: the search has no winner | changed: the question is empty | changed: the question is empty | all | from table.json (not recomputed here) |
| T13 | 18-knot structure, one birth per setting | 20/9 hidden | 2 hidden (recomputed) | changed by 2/9 | changed by 2/9 | all [not run (more than 20 distinctions; projection only, as registered)] | recomputed here |
| T14 | two and three births per setting | 68/25, 260/81 hidden | 2 (record control, results_draft.md:83) | changed by 18/25, 98/81 (the record's control; recomputed in part 2 for k = 1 only) | changed by 18/25, 98/81 (the record's control; recomputed in part 2 for k = 1 only) | not tested | from table.json (not recomputed here) |
| T15 | a keyed setting changes the other record | 2/9 between keyings (pooled), 18-knot and 11-knot | 0 (both structures) | changed by 2/9 | changed by 2/9 | all [not run (more than 20 distinctions; projection only, as registered)]; 11-knot: fails: even(x1,x2,x3,c) (K2); even(y1,y2,y3,t) (K2) [canonical: agrees] | recomputed here |
| T16 | the ceiling 4(1+ρ²)/(1+ρ)² | the formula | 2 (ρ = 1) | consistent | consistent | not applicable (no settings-line structure) | from table.json (not recomputed here) |
| T17 | census of two-holder sides: largest hidden 2; 8/3 unhidden | the 8/3 case: 8/3, not hidden (change 1/6) | the 8/3 case: 2, hidden | changed: 8/3 not hidden to 2 hidden (the census rows not recomputed) | to compute in the ticket (part 2) | fails: even(x2,h1,h2,h3) (K2); even(y2,k1,k2,k3) (K2); nae(x1,x2,za) (K2); nae(y1,y2,zb) (K2) [canonical: agrees] | recomputed here |
| T18 | rule R: seven three-holder parts gain (smallest 10 knots) | 6175/3087, 5293/2646, 1135/567, 973/486, 127/63, 11162/5535, 109/54 hidden (214 records reproduced) | 2 hidden in all 214 (from the start and after the round) | changed by 1/3087, 1/2646, 1/567, 1/486, 1/63, 92/5535, 1/54 | to compute in the ticket (part 2) | fails: even(Bh1,Bh2,Bh3,Bh4) (K2); even(y2,s1,Bh1) (K2); odd(y3,s2,Bh1) (K2) [not run (more than 20 distinctions; projection only, as registered)] | recomputed here |
| T19 | 34 round-1 gains (smallest 7 knots: 2 to 55/27) | 55/27 | to compute | not recomputed (not registered in part 2; at most 2 by the lemma where its hypotheses hold) | not recomputed (not registered in part 2; at most 2 by the lemma where its hypotheses hold) | not tested | from table.json (not recomputed here) |
| T20 | parity CHSH from all-or-none funding, both complete records hidden | 9/4 (parity: the same) | 9/4 (its primary weighting, preregistration.md:21) | outside both countings (its cause is all-or-none funding; the same under both) | outside both countings (its cause is all-or-none funding; the same under both) | not tested | from table.json (not recomputed here) |
| T21 | smallest NAE closing control | TV 12/689 at the first observer's low setting | 0 | changed by 12/689 | changed by 12/689 | not applicable (no settings-line structure) | from table.json (not recomputed here) |
| T22 | NAE version of the funding construction | not computed | about 1.500001965, hidden | not recomputed (the finish value needs counts over about 7.5e23 states; low worth, near 1.5) | not recomputed (the finish value needs counts over about 7.5e23 states; low worth, near 1.5) | not tested | from table.json (not recomputed here) |
| T23 | hidden-address construction | parity: the same (theorem); NAE not computed | parity 9/4, TV 1/4; NAE about 1.50000193 | parity unchanged; NAE not recomputed | parity unchanged; NAE not recomputed | not tested | from table.json (not recomputed here) |
| T24 | panel maxima, four readings | NAE uniform stage 122/285, 22/19, 163/410, 2; lifted start 4/9, 32/27, 146/273, 2; parity 0,1,0,1 under both | see record | changed as recorded | changed as recorded | not applicable (no settings-line structure) | from table.json (not recomputed here) |
| T25 | old-mark distributions moved by growth | 221/233 NAE under counting 1; 0/233 under counting 2; 0/233 parity | see record | changed as recorded | changed as recorded | not applicable (no settings-line structure) | from table.json (not recomputed here) |
| T26 | central pair at two, three, four meetings | 234/635 to 351/953; 3064/8057 to 1533/4031; 38682/102203 to 58059/153401 (counting 1); unchanged (counting 2) | see record | changed as recorded | changed as recorded | not applicable (no settings-line structure) | from table.json (not recomputed here) |
| T27 | all 378 pair rates of a reached stage | 1109423/1936070 against 172/343 at the old inputs | see record | changed as recorded | changed as recorded | not applicable (no settings-line structure) | from table.json (not recomputed here) |
| T28 | disagreement rates of 406 named pairs | 416/801 against 78/155 (366 of 406 differ) | see record | changed as recorded | changed as recorded | not applicable (no settings-line structure) | from table.json (not recomputed here) |
| T29 | rates on a 601,181,310-word stage | 462 of 465 differ; 136 of 136 old pairs kept only by counting 2 | see record | changed as recorded | changed as recorded | not applicable (no settings-line structure) | from table.json (not recomputed here) |
| T30 | a distant birth changes matched newborns | 1486832/2981835 against 3962383/7946541 (counting 1); equal under counting 2 | see record | changed as recorded | changed as recorded | not applicable (no settings-line structure) | from table.json (not recomputed here) |
| T31 | best guess of the focal orientation |  | see record | changed as recorded | changed as recorded | not applicable (no settings-line structure) | from table.json (not recomputed here) |
| T32 | a supplied two-offer writer |  | see record | unchanged (equal) | unchanged (equal) | not applicable (no settings-line structure) | from table.json (not recomputed here) |
| T33 | completed fresh-only records | to compute | 67/588, 37/336, 789/1568, 5/784 | not recomputed (no registered definition) | not recomputed (no registered definition) | not applicable (no settings-line structure) | from table.json (not recomputed here) |
| T34 | a later zero payment | to compute | 1/3 to 1/2; 1/4 | not recomputed (no registered definition) | not recomputed (no registered definition) | not applicable (no settings-line structure) | from table.json (not recomputed here) |
| T35 | receipt rates | to compute | 1/64; 0.409%; 51.70 to 52.64%; 68.96% | not recomputed (no registered definition) | not recomputed (no registered definition) | not applicable (no settings-line structure) | from table.json (not recomputed here) |
| T36 | the disagreement table of a reached stage decides the next birth count (194 of 194 NAE types); a rate with no weighting word ("fraction of complete allowed words") | 194 of 194 (the record) | 194 of 194: no two types share a table | unchanged | to compute in the ticket (P9, part 5) | not applicable (no settings-line structure) | recomputed here |
| T37 | tables from observations | 2,166 tables from 2,245 NAE observations; parity 67/114 | to compute | not recomputed (no registered definition) | not recomputed (no registered definition) | not applicable (no settings-line structure) | from table.json (not recomputed here) |
| T38 | first children of the lone four-place NAE knot | 1/2; 1/4802; 12/7 | the same: one-parent births, every old state 7^4 completions | unchanged by argument | unchanged by argument | not applicable (no settings-line structure) | from table.json (not recomputed here) |
| T39 | violating ternaries at the first funded stage (trees 65/134, extra meeting 27/70); flagged by the classification as a weighting of states inside an amplitude row | 65/134, 27/70 | to compute | not recomputed (no registered definition) | not recomputed (no registered definition) | not applicable (no settings-line structure) | from table.json (not recomputed here) |
| T40 | weightings of meeting patterns | no weighting of states | no weighting of states | unchanged | unchanged | not applicable (no settings-line structure) | from table.json (not recomputed here) |
| T41 | a history is one allowed state; every later update forced | one completion per start | the same | unchanged (they coincide when every start has one completion) | unchanged (they coincide when every start has one completion) | not applicable (no settings-line structure) | from table.json (not recomputed here) |
| T42 | "disagreement rate": a share of the allowed states (a rate with no weighting word) | by definition | differs on grown NAE structures (rows of STATE-DISTANCE, LOOSE-NAMES, NEWEST-KNOTS above) | the definition is counting from the finish | the definition is counting from the finish | not applicable (no settings-line structure) | from table.json (not recomputed here) |
| T43 | disagreement counts of grown structures and whether they decide the allowed states | counts (support) | counts (support) | unchanged: counts, not rates | unchanged: counts, not rates | not applicable (no settings-line structure) | from table.json (not recomputed here) |
| T44 | chances from squared amplitudes of coherent preparations | not a counting of states | not a counting of states | outside both countings | outside both countings | not applicable | from table.json (not recomputed here) |

## The knot test in the whole: the 33 registered structures

Projection on 3255 distinct structures; the canonical command on 7406 knots of this run and 171 of the early run (agreement with projection: every knot; disagreements 0; errors 0); 1046 structures cut from the canonical check (R 38).

| Structure | Knots | Distinctions | Rule | Relation induced in the whole | K1 | K2 | K3 | In the whole | On its own | Canonical |
| --- | ---: | ---: | --- | --- | --- | --- | --- | --- | --- | --- |
| eleven (start) | 11 | 16 | even(x1,x2,x3,c) | 0011 0101 1010 1100 | True | False | True | fails | passes | agrees |
| eleven (start) | 11 | 16 | nae(c,x2,s1) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| eleven (start) | 11 | 16 | nae(c,x3,s2) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| eleven (start) | 11 | 16 | even(x2,h1,h2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| eleven (start) | 11 | 16 | odd(x3,h1,h2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| eleven (start) | 11 | 16 | even(y1,y2,y3,t) | 0011 0101 1010 1100 | True | False | True | fails | passes | agrees |
| eleven (start) | 11 | 16 | even(t,m1,m2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| eleven (start) | 11 | 16 | even(s1,m1,m2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| eleven (start) | 11 | 16 | even(y2,k1,k2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| eleven (start) | 11 | 16 | odd(y3,k1,k2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| eleven (start) | 11 | 16 | odd(s2,k1,k2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| smallest gain: part | 7 | 12 | nae(x1,x3,s1) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| smallest gain: part | 7 | 12 | even(x1,h1,h2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| smallest gain: part | 7 | 12 | nae(x2,x3,s2) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| smallest gain: part | 7 | 12 | odd(x2,h1,h2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| smallest gain: part | 7 | 12 | even(y1,k1,k2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| smallest gain: part | 7 | 12 | odd(s1,k1,k2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| smallest gain: part | 7 | 12 | even(y1,y2,y3,s2) | 0000 0011 0101 0110 1001 1010 1100 1111 | True | True | True | passes | passes | agrees |
| smallest gain: part + rule-Q round 1 | 9 | 14 | nae(x1,x3,s1) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| smallest gain: part + rule-Q round 1 | 9 | 14 | even(x1,h1,h2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| smallest gain: part + rule-Q round 1 | 9 | 14 | nae(x2,x3,s2) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| smallest gain: part + rule-Q round 1 | 9 | 14 | odd(x2,h1,h2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| smallest gain: part + rule-Q round 1 | 9 | 14 | even(y1,k1,k2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| smallest gain: part + rule-Q round 1 | 9 | 14 | odd(s1,k1,k2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| smallest gain: part + rule-Q round 1 | 9 | 14 | even(y1,y2,y3,s2) | 0000 0011 0101 0110 1001 1010 1100 1111 | True | True | True | passes | passes | agrees |
| smallest gain: part + rule-Q round 1 | 9 | 14 | nae(y3,s2,f) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| smallest gain: part + rule-Q round 1 | 9 | 14 | nae(y2,y1,g) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| seven (start) | 7 | 12 | nae(x1,x2,s1) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| seven (start) | 7 | 12 | nae(x1,x3,s2) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| seven (start) | 7 | 12 | even(x2,Ah1,Ah2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| seven (start) | 7 | 12 | odd(x3,Ah1,Ah2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| seven (start) | 7 | 12 | even(y2,Bh1,Bh2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| seven (start) | 7 | 12 | odd(s1,Bh1,Bh2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| seven (start) | 7 | 12 | odd(y1,y2,y3,s2) | 0001 0010 0100 0111 1000 1011 1101 1110 | True | True | True | passes | passes | agrees |
| eight (start) | 8 | 12 | nae(x1,x2,s1) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| eight (start) | 8 | 12 | nae(x1,x3,s2) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| eight (start) | 8 | 12 | even(x2,Ah1,Ah2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| eight (start) | 8 | 12 | odd(x3,Ah1,Ah2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| eight (start) | 8 | 12 | even(y2,Bh1,Bh2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| eight (start) | 8 | 12 | odd(y3,Bh1,Bh2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| eight (start) | 8 | 12 | odd(s2,Bh1,Bh2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| eight (start) | 8 | 12 | even(y1,y2,y3,s1) | 0011 0101 1010 1100 | True | False | True | fails | passes | agrees |
| nine, the pencil (start) | 9 | 14 | nae(x1,x2,n2) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| nine, the pencil (start) | 9 | 14 | nae(x1,x3,n1) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| nine, the pencil (start) | 9 | 14 | even(x2,d,e) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| nine, the pencil (start) | 9 | 14 | odd(x3,d,e) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| nine, the pencil (start) | 9 | 14 | even(y1,p,q) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| nine, the pencil (start) | 9 | 14 | odd(n1,p,q) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| nine, the pencil (start) | 9 | 14 | even(y2,r,t) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| nine, the pencil (start) | 9 | 14 | odd(n2,r,t) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| nine, the pencil (start) | 9 | 14 | odd(y3,r,t) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| ten A: eleven less even(y2,k1,k2) (start) | 10 | 16 | even(x1,x2,x3,c) | 0011 0101 1010 1100 | True | False | True | fails | passes | agrees |
| ten A: eleven less even(y2,k1,k2) (start) | 10 | 16 | nae(c,x2,s1) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| ten A: eleven less even(y2,k1,k2) (start) | 10 | 16 | nae(c,x3,s2) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| ten A: eleven less even(y2,k1,k2) (start) | 10 | 16 | even(x2,h1,h2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| ten A: eleven less even(y2,k1,k2) (start) | 10 | 16 | odd(x3,h1,h2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| ten A: eleven less even(y2,k1,k2) (start) | 10 | 16 | even(y1,y2,y3,t) | 0000 0011 0101 0110 1001 1010 1100 1111 | True | True | True | passes | passes | agrees |
| ten A: eleven less even(y2,k1,k2) (start) | 10 | 16 | even(t,m1,m2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| ten A: eleven less even(y2,k1,k2) (start) | 10 | 16 | even(s1,m1,m2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| ten A: eleven less even(y2,k1,k2) (start) | 10 | 16 | odd(y3,k1,k2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| ten A: eleven less even(y2,k1,k2) (start) | 10 | 16 | odd(s2,k1,k2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| ten B: eleven less odd(y3,k1,k2) (start) | 10 | 16 | even(x1,x2,x3,c) | 0011 0101 1010 1100 | True | False | True | fails | passes | agrees |
| ten B: eleven less odd(y3,k1,k2) (start) | 10 | 16 | nae(c,x2,s1) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| ten B: eleven less odd(y3,k1,k2) (start) | 10 | 16 | nae(c,x3,s2) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| ten B: eleven less odd(y3,k1,k2) (start) | 10 | 16 | even(x2,h1,h2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| ten B: eleven less odd(y3,k1,k2) (start) | 10 | 16 | odd(x3,h1,h2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| ten B: eleven less odd(y3,k1,k2) (start) | 10 | 16 | even(y1,y2,y3,t) | 0000 0011 0101 0110 1001 1010 1100 1111 | True | True | True | passes | passes | agrees |
| ten B: eleven less odd(y3,k1,k2) (start) | 10 | 16 | even(t,m1,m2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| ten B: eleven less odd(y3,k1,k2) (start) | 10 | 16 | even(s1,m1,m2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| ten B: eleven less odd(y3,k1,k2) (start) | 10 | 16 | even(y2,k1,k2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| ten B: eleven less odd(y3,k1,k2) (start) | 10 | 16 | odd(s2,k1,k2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| eighteen (start) | 18 | 26 | even(x1,a,b) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen (start) | 18 | 26 | even(c1,a,b) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen (start) | 18 | 26 | even(k1,a,b) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen (start) | 18 | 26 | even(x2,d,e) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen (start) | 18 | 26 | odd(x3,d,e) | 001 010 100 111 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen (start) | 18 | 26 | even(c2,d,e) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen (start) | 18 | 26 | odd(c3,d,e) | 001 010 100 111 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen (start) | 18 | 26 | nae(c1,c2,n2) | 001 010 011 100 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen (start) | 18 | 26 | nae(k1,c3,n1) | 001 010 011 100 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen (start) | 18 | 26 | even(n2,g,h) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen (start) | 18 | 26 | odd(s2,g,h) | 001 010 100 111 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen (start) | 18 | 26 | even(n1,u,v) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen (start) | 18 | 26 | odd(s1,u,v) | 001 010 100 111 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen (start) | 18 | 26 | even(y1,p,q) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen (start) | 18 | 26 | even(s1,p,q) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen (start) | 18 | 26 | even(y2,r,t) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen (start) | 18 | 26 | even(s2,r,t) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen (start) | 18 | 26 | odd(y3,r,t) | 001 010 100 111 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eleven + settings 00 | 13 | 18 | even(x1,x2,x3,c) | 0011 0101 1010 1100 | True | False | True | fails | passes | agrees |
| eleven + settings 00 | 13 | 18 | nae(c,x2,s1) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| eleven + settings 00 | 13 | 18 | nae(c,x3,s2) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| eleven + settings 00 | 13 | 18 | even(x2,h1,h2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| eleven + settings 00 | 13 | 18 | odd(x3,h1,h2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| eleven + settings 00 | 13 | 18 | even(y1,y2,y3,t) | 0011 0101 1010 1100 | True | False | True | fails | passes | agrees |
| eleven + settings 00 | 13 | 18 | even(t,m1,m2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| eleven + settings 00 | 13 | 18 | even(s1,m1,m2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| eleven + settings 00 | 13 | 18 | even(y2,k1,k2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| eleven + settings 00 | 13 | 18 | odd(y3,k1,k2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| eleven + settings 00 | 13 | 18 | odd(s2,k1,k2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| eleven + settings 00 | 13 | 18 | nae(x1,x2,za) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| eleven + settings 00 | 13 | 18 | nae(y1,y2,zb) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| smallest gain finished 00 | 11 | 16 | nae(x1,x3,s1) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| smallest gain finished 00 | 11 | 16 | even(x1,h1,h2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| smallest gain finished 00 | 11 | 16 | nae(x2,x3,s2) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| smallest gain finished 00 | 11 | 16 | odd(x2,h1,h2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| smallest gain finished 00 | 11 | 16 | even(y1,k1,k2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| smallest gain finished 00 | 11 | 16 | odd(s1,k1,k2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| smallest gain finished 00 | 11 | 16 | even(y1,y2,y3,s2) | 0000 0011 0101 0110 1001 1010 1100 1111 | True | True | True | passes | passes | agrees |
| smallest gain finished 00 | 11 | 16 | nae(y3,s2,f) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| smallest gain finished 00 | 11 | 16 | nae(y2,y1,g) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| smallest gain finished 00 | 11 | 16 | nae(x1,x2,za) | 010 011 100 101 | True | False | True | fails | passes | agrees |
| smallest gain finished 00 | 11 | 16 | nae(y1,y2,zb) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| seven + settings 00 | 9 | 14 | nae(x1,x2,s1) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| seven + settings 00 | 9 | 14 | nae(x1,x3,s2) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| seven + settings 00 | 9 | 14 | even(x2,Ah1,Ah2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| seven + settings 00 | 9 | 14 | odd(x3,Ah1,Ah2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| seven + settings 00 | 9 | 14 | even(y2,Bh1,Bh2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| seven + settings 00 | 9 | 14 | odd(s1,Bh1,Bh2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| seven + settings 00 | 9 | 14 | odd(y1,y2,y3,s2) | 0001 0010 0100 0111 1000 1011 1101 1110 | True | True | True | passes | passes | agrees |
| seven + settings 00 | 9 | 14 | nae(x1,x2,za) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| seven + settings 00 | 9 | 14 | nae(y1,y2,zb) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| eight + settings 00 | 10 | 14 | nae(x1,x2,s1) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| eight + settings 00 | 10 | 14 | nae(x1,x3,s2) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| eight + settings 00 | 10 | 14 | even(x2,Ah1,Ah2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| eight + settings 00 | 10 | 14 | odd(x3,Ah1,Ah2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| eight + settings 00 | 10 | 14 | even(y2,Bh1,Bh2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| eight + settings 00 | 10 | 14 | odd(y3,Bh1,Bh2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| eight + settings 00 | 10 | 14 | odd(s2,Bh1,Bh2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| eight + settings 00 | 10 | 14 | even(y1,y2,y3,s1) | 0011 0101 1010 1100 | True | False | True | fails | passes | agrees |
| eight + settings 00 | 10 | 14 | nae(x1,x2,za) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| eight + settings 00 | 10 | 14 | nae(y1,y2,zb) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| nine + settings 00 | 11 | 16 | nae(x1,x2,n2) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| nine + settings 00 | 11 | 16 | nae(x1,x3,n1) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| nine + settings 00 | 11 | 16 | even(x2,d,e) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| nine + settings 00 | 11 | 16 | odd(x3,d,e) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| nine + settings 00 | 11 | 16 | even(y1,p,q) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| nine + settings 00 | 11 | 16 | odd(n1,p,q) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| nine + settings 00 | 11 | 16 | even(y2,r,t) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| nine + settings 00 | 11 | 16 | odd(n2,r,t) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| nine + settings 00 | 11 | 16 | odd(y3,r,t) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| nine + settings 00 | 11 | 16 | nae(x1,x2,za) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| nine + settings 00 | 11 | 16 | nae(y1,y2,zb) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| eighteen + settings 00 | 20 | 28 | even(x1,a,b) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 00 | 20 | 28 | even(c1,a,b) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 00 | 20 | 28 | even(k1,a,b) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 00 | 20 | 28 | even(x2,d,e) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 00 | 20 | 28 | odd(x3,d,e) | 001 010 100 111 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 00 | 20 | 28 | even(c2,d,e) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 00 | 20 | 28 | odd(c3,d,e) | 001 010 100 111 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 00 | 20 | 28 | nae(c1,c2,n2) | 001 010 011 100 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 00 | 20 | 28 | nae(k1,c3,n1) | 001 010 011 100 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 00 | 20 | 28 | even(n2,g,h) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 00 | 20 | 28 | odd(s2,g,h) | 001 010 100 111 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 00 | 20 | 28 | even(n1,u,v) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 00 | 20 | 28 | odd(s1,u,v) | 001 010 100 111 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 00 | 20 | 28 | even(y1,p,q) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 00 | 20 | 28 | even(s1,p,q) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 00 | 20 | 28 | even(y2,r,t) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 00 | 20 | 28 | even(s2,r,t) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 00 | 20 | 28 | odd(y3,r,t) | 001 010 100 111 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 00 | 20 | 28 | nae(x1,x2,za) | 001 010 011 100 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 00 | 20 | 28 | nae(y1,y2,zb) | 001 010 011 100 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eleven + settings 01 | 13 | 18 | even(x1,x2,x3,c) | 0011 0101 1010 1100 | True | False | True | fails | passes | agrees |
| eleven + settings 01 | 13 | 18 | nae(c,x2,s1) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| eleven + settings 01 | 13 | 18 | nae(c,x3,s2) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| eleven + settings 01 | 13 | 18 | even(x2,h1,h2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| eleven + settings 01 | 13 | 18 | odd(x3,h1,h2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| eleven + settings 01 | 13 | 18 | even(y1,y2,y3,t) | 0011 0101 1010 1100 | True | False | True | fails | passes | agrees |
| eleven + settings 01 | 13 | 18 | even(t,m1,m2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| eleven + settings 01 | 13 | 18 | even(s1,m1,m2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| eleven + settings 01 | 13 | 18 | even(y2,k1,k2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| eleven + settings 01 | 13 | 18 | odd(y3,k1,k2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| eleven + settings 01 | 13 | 18 | odd(s2,k1,k2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| eleven + settings 01 | 13 | 18 | nae(x1,x2,za) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| eleven + settings 01 | 13 | 18 | nae(y1,y3,zb) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| smallest gain finished 01 | 11 | 16 | nae(x1,x3,s1) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| smallest gain finished 01 | 11 | 16 | even(x1,h1,h2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| smallest gain finished 01 | 11 | 16 | nae(x2,x3,s2) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| smallest gain finished 01 | 11 | 16 | odd(x2,h1,h2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| smallest gain finished 01 | 11 | 16 | even(y1,k1,k2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| smallest gain finished 01 | 11 | 16 | odd(s1,k1,k2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| smallest gain finished 01 | 11 | 16 | even(y1,y2,y3,s2) | 0000 0011 0101 0110 1001 1010 1100 1111 | True | True | True | passes | passes | agrees |
| smallest gain finished 01 | 11 | 16 | nae(y3,s2,f) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| smallest gain finished 01 | 11 | 16 | nae(y2,y1,g) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| smallest gain finished 01 | 11 | 16 | nae(x1,x2,za) | 010 011 100 101 | True | False | True | fails | passes | agrees |
| smallest gain finished 01 | 11 | 16 | nae(y1,y3,zb) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| seven + settings 01 | 9 | 14 | nae(x1,x2,s1) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| seven + settings 01 | 9 | 14 | nae(x1,x3,s2) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| seven + settings 01 | 9 | 14 | even(x2,Ah1,Ah2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| seven + settings 01 | 9 | 14 | odd(x3,Ah1,Ah2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| seven + settings 01 | 9 | 14 | even(y2,Bh1,Bh2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| seven + settings 01 | 9 | 14 | odd(s1,Bh1,Bh2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| seven + settings 01 | 9 | 14 | odd(y1,y2,y3,s2) | 0001 0010 0100 0111 1000 1011 1101 1110 | True | True | True | passes | passes | agrees |
| seven + settings 01 | 9 | 14 | nae(x1,x2,za) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| seven + settings 01 | 9 | 14 | nae(y1,y3,zb) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| eight + settings 01 | 10 | 14 | nae(x1,x2,s1) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| eight + settings 01 | 10 | 14 | nae(x1,x3,s2) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| eight + settings 01 | 10 | 14 | even(x2,Ah1,Ah2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| eight + settings 01 | 10 | 14 | odd(x3,Ah1,Ah2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| eight + settings 01 | 10 | 14 | even(y2,Bh1,Bh2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| eight + settings 01 | 10 | 14 | odd(y3,Bh1,Bh2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| eight + settings 01 | 10 | 14 | odd(s2,Bh1,Bh2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| eight + settings 01 | 10 | 14 | even(y1,y2,y3,s1) | 0011 0101 1010 1100 | True | False | True | fails | passes | agrees |
| eight + settings 01 | 10 | 14 | nae(x1,x2,za) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| eight + settings 01 | 10 | 14 | nae(y1,y3,zb) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| nine + settings 01 | 11 | 16 | nae(x1,x2,n2) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| nine + settings 01 | 11 | 16 | nae(x1,x3,n1) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| nine + settings 01 | 11 | 16 | even(x2,d,e) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| nine + settings 01 | 11 | 16 | odd(x3,d,e) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| nine + settings 01 | 11 | 16 | even(y1,p,q) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| nine + settings 01 | 11 | 16 | odd(n1,p,q) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| nine + settings 01 | 11 | 16 | even(y2,r,t) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| nine + settings 01 | 11 | 16 | odd(n2,r,t) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| nine + settings 01 | 11 | 16 | odd(y3,r,t) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| nine + settings 01 | 11 | 16 | nae(x1,x2,za) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| nine + settings 01 | 11 | 16 | nae(y1,y3,zb) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| eighteen + settings 01 | 20 | 28 | even(x1,a,b) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 01 | 20 | 28 | even(c1,a,b) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 01 | 20 | 28 | even(k1,a,b) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 01 | 20 | 28 | even(x2,d,e) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 01 | 20 | 28 | odd(x3,d,e) | 001 010 100 111 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 01 | 20 | 28 | even(c2,d,e) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 01 | 20 | 28 | odd(c3,d,e) | 001 010 100 111 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 01 | 20 | 28 | nae(c1,c2,n2) | 001 010 011 100 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 01 | 20 | 28 | nae(k1,c3,n1) | 001 010 011 100 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 01 | 20 | 28 | even(n2,g,h) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 01 | 20 | 28 | odd(s2,g,h) | 001 010 100 111 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 01 | 20 | 28 | even(n1,u,v) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 01 | 20 | 28 | odd(s1,u,v) | 001 010 100 111 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 01 | 20 | 28 | even(y1,p,q) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 01 | 20 | 28 | even(s1,p,q) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 01 | 20 | 28 | even(y2,r,t) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 01 | 20 | 28 | even(s2,r,t) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 01 | 20 | 28 | odd(y3,r,t) | 001 010 100 111 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 01 | 20 | 28 | nae(x1,x2,za) | 001 010 011 100 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 01 | 20 | 28 | nae(y1,y3,zb) | 001 010 011 100 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eleven + settings 10 | 13 | 18 | even(x1,x2,x3,c) | 0011 0101 1010 1100 | True | False | True | fails | passes | agrees |
| eleven + settings 10 | 13 | 18 | nae(c,x2,s1) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| eleven + settings 10 | 13 | 18 | nae(c,x3,s2) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| eleven + settings 10 | 13 | 18 | even(x2,h1,h2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| eleven + settings 10 | 13 | 18 | odd(x3,h1,h2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| eleven + settings 10 | 13 | 18 | even(y1,y2,y3,t) | 0011 0101 1010 1100 | True | False | True | fails | passes | agrees |
| eleven + settings 10 | 13 | 18 | even(t,m1,m2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| eleven + settings 10 | 13 | 18 | even(s1,m1,m2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| eleven + settings 10 | 13 | 18 | even(y2,k1,k2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| eleven + settings 10 | 13 | 18 | odd(y3,k1,k2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| eleven + settings 10 | 13 | 18 | odd(s2,k1,k2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| eleven + settings 10 | 13 | 18 | nae(x1,x3,za) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| eleven + settings 10 | 13 | 18 | nae(y1,y2,zb) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| smallest gain finished 10 | 11 | 16 | nae(x1,x3,s1) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| smallest gain finished 10 | 11 | 16 | even(x1,h1,h2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| smallest gain finished 10 | 11 | 16 | nae(x2,x3,s2) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| smallest gain finished 10 | 11 | 16 | odd(x2,h1,h2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| smallest gain finished 10 | 11 | 16 | even(y1,k1,k2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| smallest gain finished 10 | 11 | 16 | odd(s1,k1,k2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| smallest gain finished 10 | 11 | 16 | even(y1,y2,y3,s2) | 0000 0011 0101 0110 1001 1010 1100 1111 | True | True | True | passes | passes | agrees |
| smallest gain finished 10 | 11 | 16 | nae(y3,s2,f) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| smallest gain finished 10 | 11 | 16 | nae(y2,y1,g) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| smallest gain finished 10 | 11 | 16 | nae(x1,x3,za) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| smallest gain finished 10 | 11 | 16 | nae(y1,y2,zb) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| seven + settings 10 | 9 | 14 | nae(x1,x2,s1) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| seven + settings 10 | 9 | 14 | nae(x1,x3,s2) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| seven + settings 10 | 9 | 14 | even(x2,Ah1,Ah2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| seven + settings 10 | 9 | 14 | odd(x3,Ah1,Ah2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| seven + settings 10 | 9 | 14 | even(y2,Bh1,Bh2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| seven + settings 10 | 9 | 14 | odd(s1,Bh1,Bh2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| seven + settings 10 | 9 | 14 | odd(y1,y2,y3,s2) | 0001 0010 0100 0111 1000 1011 1101 1110 | True | True | True | passes | passes | agrees |
| seven + settings 10 | 9 | 14 | nae(x1,x3,za) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| seven + settings 10 | 9 | 14 | nae(y1,y2,zb) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| eight + settings 10 | 10 | 14 | nae(x1,x2,s1) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| eight + settings 10 | 10 | 14 | nae(x1,x3,s2) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| eight + settings 10 | 10 | 14 | even(x2,Ah1,Ah2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| eight + settings 10 | 10 | 14 | odd(x3,Ah1,Ah2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| eight + settings 10 | 10 | 14 | even(y2,Bh1,Bh2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| eight + settings 10 | 10 | 14 | odd(y3,Bh1,Bh2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| eight + settings 10 | 10 | 14 | odd(s2,Bh1,Bh2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| eight + settings 10 | 10 | 14 | even(y1,y2,y3,s1) | 0011 0101 1010 1100 | True | False | True | fails | passes | agrees |
| eight + settings 10 | 10 | 14 | nae(x1,x3,za) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| eight + settings 10 | 10 | 14 | nae(y1,y2,zb) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| nine + settings 10 | 11 | 16 | nae(x1,x2,n2) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| nine + settings 10 | 11 | 16 | nae(x1,x3,n1) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| nine + settings 10 | 11 | 16 | even(x2,d,e) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| nine + settings 10 | 11 | 16 | odd(x3,d,e) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| nine + settings 10 | 11 | 16 | even(y1,p,q) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| nine + settings 10 | 11 | 16 | odd(n1,p,q) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| nine + settings 10 | 11 | 16 | even(y2,r,t) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| nine + settings 10 | 11 | 16 | odd(n2,r,t) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| nine + settings 10 | 11 | 16 | odd(y3,r,t) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| nine + settings 10 | 11 | 16 | nae(x1,x3,za) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| nine + settings 10 | 11 | 16 | nae(y1,y2,zb) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| eighteen + settings 10 | 20 | 28 | even(x1,a,b) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 10 | 20 | 28 | even(c1,a,b) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 10 | 20 | 28 | even(k1,a,b) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 10 | 20 | 28 | even(x2,d,e) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 10 | 20 | 28 | odd(x3,d,e) | 001 010 100 111 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 10 | 20 | 28 | even(c2,d,e) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 10 | 20 | 28 | odd(c3,d,e) | 001 010 100 111 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 10 | 20 | 28 | nae(c1,c2,n2) | 001 010 011 100 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 10 | 20 | 28 | nae(k1,c3,n1) | 001 010 011 100 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 10 | 20 | 28 | even(n2,g,h) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 10 | 20 | 28 | odd(s2,g,h) | 001 010 100 111 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 10 | 20 | 28 | even(n1,u,v) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 10 | 20 | 28 | odd(s1,u,v) | 001 010 100 111 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 10 | 20 | 28 | even(y1,p,q) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 10 | 20 | 28 | even(s1,p,q) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 10 | 20 | 28 | even(y2,r,t) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 10 | 20 | 28 | even(s2,r,t) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 10 | 20 | 28 | odd(y3,r,t) | 001 010 100 111 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 10 | 20 | 28 | nae(x1,x3,za) | 001 010 011 100 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 10 | 20 | 28 | nae(y1,y2,zb) | 001 010 011 100 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eleven + settings 11 | 13 | 18 | even(x1,x2,x3,c) | 0011 0101 1010 1100 | True | False | True | fails | passes | agrees |
| eleven + settings 11 | 13 | 18 | nae(c,x2,s1) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| eleven + settings 11 | 13 | 18 | nae(c,x3,s2) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| eleven + settings 11 | 13 | 18 | even(x2,h1,h2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| eleven + settings 11 | 13 | 18 | odd(x3,h1,h2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| eleven + settings 11 | 13 | 18 | even(y1,y2,y3,t) | 0011 0101 1010 1100 | True | False | True | fails | passes | agrees |
| eleven + settings 11 | 13 | 18 | even(t,m1,m2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| eleven + settings 11 | 13 | 18 | even(s1,m1,m2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| eleven + settings 11 | 13 | 18 | even(y2,k1,k2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| eleven + settings 11 | 13 | 18 | odd(y3,k1,k2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| eleven + settings 11 | 13 | 18 | odd(s2,k1,k2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| eleven + settings 11 | 13 | 18 | nae(x1,x3,za) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| eleven + settings 11 | 13 | 18 | nae(y1,y3,zb) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| smallest gain finished 11 | 11 | 16 | nae(x1,x3,s1) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| smallest gain finished 11 | 11 | 16 | even(x1,h1,h2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| smallest gain finished 11 | 11 | 16 | nae(x2,x3,s2) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| smallest gain finished 11 | 11 | 16 | odd(x2,h1,h2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| smallest gain finished 11 | 11 | 16 | even(y1,k1,k2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| smallest gain finished 11 | 11 | 16 | odd(s1,k1,k2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| smallest gain finished 11 | 11 | 16 | even(y1,y2,y3,s2) | 0000 0011 0101 0110 1001 1010 1100 1111 | True | True | True | passes | passes | agrees |
| smallest gain finished 11 | 11 | 16 | nae(y3,s2,f) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| smallest gain finished 11 | 11 | 16 | nae(y2,y1,g) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| smallest gain finished 11 | 11 | 16 | nae(x1,x3,za) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| smallest gain finished 11 | 11 | 16 | nae(y1,y3,zb) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| seven + settings 11 | 9 | 14 | nae(x1,x2,s1) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| seven + settings 11 | 9 | 14 | nae(x1,x3,s2) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| seven + settings 11 | 9 | 14 | even(x2,Ah1,Ah2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| seven + settings 11 | 9 | 14 | odd(x3,Ah1,Ah2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| seven + settings 11 | 9 | 14 | even(y2,Bh1,Bh2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| seven + settings 11 | 9 | 14 | odd(s1,Bh1,Bh2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| seven + settings 11 | 9 | 14 | odd(y1,y2,y3,s2) | 0001 0010 0100 0111 1000 1011 1101 1110 | True | True | True | passes | passes | agrees |
| seven + settings 11 | 9 | 14 | nae(x1,x3,za) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| seven + settings 11 | 9 | 14 | nae(y1,y3,zb) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| eight + settings 11 | 10 | 14 | nae(x1,x2,s1) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| eight + settings 11 | 10 | 14 | nae(x1,x3,s2) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| eight + settings 11 | 10 | 14 | even(x2,Ah1,Ah2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| eight + settings 11 | 10 | 14 | odd(x3,Ah1,Ah2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| eight + settings 11 | 10 | 14 | even(y2,Bh1,Bh2) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| eight + settings 11 | 10 | 14 | odd(y3,Bh1,Bh2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| eight + settings 11 | 10 | 14 | odd(s2,Bh1,Bh2) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| eight + settings 11 | 10 | 14 | even(y1,y2,y3,s1) | 0011 0101 1010 1100 | True | False | True | fails | passes | agrees |
| eight + settings 11 | 10 | 14 | nae(x1,x3,za) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| eight + settings 11 | 10 | 14 | nae(y1,y3,zb) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| nine + settings 11 | 11 | 16 | nae(x1,x2,n2) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| nine + settings 11 | 11 | 16 | nae(x1,x3,n1) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| nine + settings 11 | 11 | 16 | even(x2,d,e) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| nine + settings 11 | 11 | 16 | odd(x3,d,e) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| nine + settings 11 | 11 | 16 | even(y1,p,q) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| nine + settings 11 | 11 | 16 | odd(n1,p,q) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| nine + settings 11 | 11 | 16 | even(y2,r,t) | 000 011 101 110 | True | True | True | passes | passes | agrees |
| nine + settings 11 | 11 | 16 | odd(n2,r,t) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| nine + settings 11 | 11 | 16 | odd(y3,r,t) | 001 010 100 111 | True | True | True | passes | passes | agrees |
| nine + settings 11 | 11 | 16 | nae(x1,x3,za) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| nine + settings 11 | 11 | 16 | nae(y1,y3,zb) | 001 010 011 100 101 110 | True | True | True | passes | passes | agrees |
| eighteen + settings 11 | 20 | 28 | even(x1,a,b) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 11 | 20 | 28 | even(c1,a,b) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 11 | 20 | 28 | even(k1,a,b) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 11 | 20 | 28 | even(x2,d,e) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 11 | 20 | 28 | odd(x3,d,e) | 001 010 100 111 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 11 | 20 | 28 | even(c2,d,e) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 11 | 20 | 28 | odd(c3,d,e) | 001 010 100 111 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 11 | 20 | 28 | nae(c1,c2,n2) | 001 010 011 100 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 11 | 20 | 28 | nae(k1,c3,n1) | 001 010 011 100 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 11 | 20 | 28 | even(n2,g,h) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 11 | 20 | 28 | odd(s2,g,h) | 001 010 100 111 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 11 | 20 | 28 | even(n1,u,v) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 11 | 20 | 28 | odd(s1,u,v) | 001 010 100 111 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 11 | 20 | 28 | even(y1,p,q) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 11 | 20 | 28 | even(s1,p,q) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 11 | 20 | 28 | even(y2,r,t) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 11 | 20 | 28 | even(s2,r,t) | 000 011 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 11 | 20 | 28 | odd(y3,r,t) | 001 010 100 111 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 11 | 20 | 28 | nae(x1,x3,za) | 001 010 011 100 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |
| eighteen + settings 11 | 20 | 28 | nae(y1,y3,zb) | 001 010 011 100 101 110 | True | True | True | passes | passes | not run (more than 20 distinctions; projection only, as registered) |

**Beyond the 33: part 2’s histories.** Rules that fail in the whole in the finished structures of part 2’s records (projection; the canonical check where run agreed on every knot):

| Source | Histories | With a rule failing in some finished structure | Rules failing (finished structures) | Scores from the finish of the histories whose every rule passes | Canonical |
| --- | ---: | ---: | --- | --- | --- |
| ONE-PARENT-REREAD uniform | 16 | 8 | nae(x1,x2,za) at (0, 0) ×8; nae(x1,x2,za) at (0, 1) ×8 | 31/15 ×4, 61/30 ×4 | canonical: agrees ×64 |
| ONE-PARENT-REREAD mixed | 664 | 272 | nae(x1,x2,za) at (0, 0) ×272; nae(x1,x2,za) at (0, 1) ×272 | 109/54 ×288, 55/27 ×96, 31/15 ×4, 61/30 ×4 | canonical check not run (cut) ×1558; canonical: agrees ×1098 |
| REREAD-BIRTHS rule R | 214 | 33 | even(Bh1,Bh2,Bh3,Bh4) at (0, 0) ×33; even(Bh1,Bh2,Bh3,Bh4) at (0, 1) ×33; even(Bh1,Bh2,Bh3,Bh4) at (1, 0) ×33; even(Bh1,Bh2,Bh3,Bh4) at (1, 1) ×33; even(y2,s1,Bh1) at (0, 0) ×33; even(y2,s1,Bh1) at (0, 1) ×33; even(y2,s1,Bh1) at (1, 0) ×33; even(y2,s1,Bh1) at (1, 1) ×33; odd(y3,s2,Bh1) at (0, 0) ×33; odd(y3,s2,Bh1) at (0, 1) ×33; odd(y3,s2,Bh1) at (1, 0) ×33; odd(y3,s2,Bh1) at (1, 1) ×33 | 5293/2646 ×54, 127/63 ×50, 6175/3087 ×36, 1135/567 ×27, 109/54 ×8, 973/486 ×5, 11162/5535 ×1 | not run (more than 20 distinctions; projection only, as registered) ×856 |

All 3255 distinct structures of parts 2–4 and structures.json: 42568 knot verdicts, 931 fail in the whole, 0 fail on their own. Part 3’s 2,560 structures: the two four-place rules fail K2 in every one, no other rule fails.

Failing rules by source and rule (structures counted): part 2 nae(x1,x2,za) ×302; part 2 even(Bh1,Bh2,Bh3,Bh4) ×132; part 2 odd(y3,s2,Bh1) ×132; part 2 even(y2,s1,Bh1) ×132; part 2 (the stage after the round) even(Bh1,Bh2,Bh3,Bh4) ×33; part 2 (the stage after the round) odd(y3,s2,Bh1) ×33; part 2 (the stage after the round) even(y2,s1,Bh1) ×33; part 2 even(x1,x2,x3,c) ×29; part 4 even(x1,x2,x3,c) ×16; part 4 even(y1,y2,y3,t) ×16; part 2 nae(x1,c,za) ×11; structures.json even(x1,x2,x3,c) ×7; part 4 nae(c,x2,s1) ×7; part 4 nae(c,x3,s2) ×6; structures.json even(y1,y2,y3,t) ×5; structures.json even(y1,y2,y3,s1) ×5; part 2 even(y1,y2,y3,t) ×5; part 2 even(x2,h1,h2,h3) ×4; part 2 even(y2,k1,k2,k3) ×4; part 2 nae(y1,t,zb) ×3; structures.json nae(x1,x2,za) ×2; part 2 nae(y1,y2,zb) ×2; part 2 (the start) even(Bh1,Bh2,Bh3,Bh4) ×2; part 2 (the start) odd(y3,s2,Bh1) ×2; part 2 (the start) even(y2,s1,Bh1) ×2; part 4 nae(x1,x2,s1) ×2; part 4 nae(x1,x3,s1) ×2; part 2 (the start) even(x2,h1,h2,h3) ×1; part 2 (the start) even(y2,k1,k2,k3) ×1


## Wall times (s)

{"part 1": 18.5, "part 8 early": 15.8, "part 2": 298.2, "part 3": 15.5, "part 4": 0.9, "part 5": 52.6, "part 6": 13.9, "part 7": 11.4, "part 8 remainder": 1190.0, "part 9": 406.5}
