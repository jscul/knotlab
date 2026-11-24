### Row G

| check | compared | equal |
| --- | --- | --- |
| QGrowth, re-reading off, against the recorded driver lib.grow (stars, knots per stage, outcome; 12 rounds, 5,000 knots) | 280 funded draws (arm 0: 69, arm 1: 29, arm 2: 69, arm 3: 113), 3360 rounds | 280 |
| this study's planner, re-reading off, against end_operator.step, round 1 (status, parents, fresh, demand) | 280 | 280 |
| this study's planner against QGrowth, round 1, re-reading off / on with convention O / on with convention N | 280 each | 280 / 280 / 280 (re-reading births at round 1: 598 under O, 598 under N) |

| Alice pair | Bob pair | recorded scorer, score | this study, score (ii) | recorded scorer, hidden | this study, hidden | agree |
| --- | --- | --- | --- | --- | --- | --- |
| x2, x3 | y2, y3 | 2.222222222222 | 20/9 | yes | yes | yes |
| x2, x3 | y2, t | 2.111111111111 | 19/9 | yes | yes | yes |
| x2, x3 | y3, t | 2.111111111111 | 19/9 | yes | yes | yes |
| x2, c | y2, y3 | 2.111111111111 | 19/9 | yes | yes | yes |
| x2, c | y2, t | 2.055555555556 | 37/18 | yes | yes | yes |
| x2, c | y3, t | 2.055555555556 | 37/18 | yes | yes | yes |
| x3, c | y2, y3 | 2.111111111111 | 19/9 | yes | yes | yes |
| x3, c | y2, t | 2.055555555556 | 37/18 | yes | yes | yes |
| x3, c | y3, t | 2.055555555556 | 37/18 | yes | yes | yes |

Self-test of the scoring code (objects that are not this study's): 150 drawn tables of one- and two-bit records, score (i) merged = unmerged = every function on both sides, score (ii) = every parity on both sides with and without the constant; 40 drawn three-bit tables, merged = unmerged; a non-local box gives 4; the recorded scorer's own four-type example gives 20/9 by score (ii), as `evaluate(M)` does, and 20/9 by score (i).

### (a) Round 1 of rule Q on the 11-knot structure

Live knots (knot: openings): {'0': 1, '5': 1} (knot 0 = even(x1,x2,x3,c), knot 5 = even(y1,y2,y3,t)); groups of two or more live knots: none; births: 2, of which one-parent: 2.

| birth | parent | loose distinction taken | options (shared distinctions of the parent) |
| --- | --- | --- | --- |
| 0 | even(x1,x2,x3,c) | x1 | x2, x3, c |
| 1 | even(y1,y2,y3,t) | y1 | y2, y3, t |

| choice (Alice, Bob) | birth on x1 takes | birth on y1 takes | lookahead demand | fresh distinctions | QGrowth = this planner |
| --- | --- | --- | --- | --- | --- |
| x2, y2 | x1, x2 | y1, y2 | 0, 0 | 1, 1 | yes |
| x2, y3 | x1, x2 | y1, y3 | 0, 0 | 1, 1 | yes |
| x2, t | x1, x2 | y1, t | 0, 0 | 1, 1 | yes |
| x3, y2 | x1, x3 | y1, y2 | 0, 0 | 1, 1 | yes |
| x3, y3 | x1, x3 | y1, y3 | 0, 0 | 1, 1 | yes |
| x3, t | x1, x3 | y1, t | 0, 0 | 1, 1 | yes |
| c, y2 | x1, c | y1, y2 | 0, 0 | 1, 1 | yes |
| c, y3 | x1, c | y1, y3 | 0, 0 | 1, 1 | yes |
| c, t | x1, c | y1, t | 0, 0 | 1, 1 | yes |

Convention O (smallest number, deviations A2) would take x2, y2; convention N c, t. Old structure: 64 allowed words over 16 distinctions.

| stage-1 structure (Alice, Bob) | newborns | allowed words | completions per old word (completions: old words) |
| --- | --- | --- | --- |
| c, t | nae(x1,c,zA); nae(y1,t,zB) | 256 | 4: 64 |
| c, y2 | nae(x1,c,zA); nae(y1,y2,zB) | 192 | 2: 32, 4: 32 |
| c, y3 | nae(x1,c,zA); nae(y1,y3,zB) | 192 | 2: 32, 4: 32 |
| x2, t | nae(x1,x2,zA); nae(y1,t,zB) | 192 | 2: 32, 4: 32 |
| x2, y2 | nae(x1,x2,zA); nae(y1,y2,zB) | 144 | 1: 16, 2: 32, 4: 16 |
| x2, y3 | nae(x1,x2,zA); nae(y1,y3,zB) | 144 | 1: 16, 2: 32, 4: 16 |
| x3, t | nae(x1,x3,zA); nae(y1,t,zB) | 192 | 2: 32, 4: 32 |
| x3, y2 | nae(x1,x3,zA); nae(y1,y2,zB) | 144 | 1: 16, 2: 32, 4: 16 |
| x3, y3 | nae(x1,x3,zA); nae(y1,y3,zB) | 144 | 1: 16, 2: 32, 4: 16 |

### (b) All nine pairs of option pairs

| Alice pair (o0, o1) | Bob pair (p0, p1) | allowed words (o0p0, o0p1, o1p0, o1p1) | Alice hidden (largest change) | Bob hidden (largest change) | score (i) | score (ii) (with the constant) | score (iii) | hidden excess |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| x2, x3 | y2, y3 | 144, 144, 144, 144 | yes (0) | yes (0) | 20/9 | 20/9 (20/9) | 20/9 | yes |
| x2, x3 | y2, t | 144, 192, 144, 192 | yes (0) | yes (0) | 19/9 | 19/9 (19/9) | 19/9 | yes |
| x2, x3 | y3, t | 144, 192, 144, 192 | yes (0) | yes (0) | 19/9 | 19/9 (19/9) | 19/9 | yes |
| x2, c | y2, y3 | 144, 144, 192, 192 | yes (0) | yes (0) | 19/9 | 19/9 (19/9) | 19/9 | yes |
| x2, c | y2, t | 144, 192, 192, 256 | yes (0) | yes (0) | 37/18 | 37/18 (37/18) | 37/18 | yes |
| x2, c | y3, t | 144, 192, 192, 256 | yes (0) | yes (0) | 37/18 | 37/18 (37/18) | 37/18 | yes |
| x3, c | y2, y3 | 144, 144, 192, 192 | yes (0) | yes (0) | 19/9 | 19/9 (19/9) | 19/9 | yes |
| x3, c | y2, t | 144, 192, 192, 256 | yes (0) | yes (0) | 37/18 | 37/18 (37/18) | 37/18 | yes |
| x3, c | y3, t | 144, 192, 192, 256 | yes (0) | yes (0) | 37/18 | 37/18 (37/18) | 37/18 | yes |

For (x2, x3) against (y2, y3) the value 20/9 is reached with the minus sign on E(0,0); the four correlations are E(0,0) = -5/9, E(0,1) = 5/9, E(1,0) = 5/9, E(1,1) = 5/9; response functions found by enumerating Bob ([4, 4] merged generators per setting), re-evaluated in fractions; the unmerged enumeration of Alice's functions gives 20/9.

### (c) The pair (x2, x3) against (y2, y3): what depends on the far choice

| choice (Alice, Bob) | P(s1 s2 = 00) | 01 | 10 | 11 |
| --- | --- | --- | --- | --- |
| x2, y2 | 1/6 | 1/3 | 1/3 | 1/6 |
| x2, y3 | 1/3 | 1/6 | 1/6 | 1/3 |
| x3, y2 | 1/6 | 1/3 | 1/3 | 1/6 |
| x3, y3 | 1/3 | 1/6 | 1/6 | 1/3 |

(s1, s2) the same under Alice's two choices, for Bob's choice y2 / y3: yes / yes. The same under Bob's two choices, for Alice's choice x2 / x3: no / no.

| observer | distinctions | own choice | unchanged by the far choice | change (total variation) |
| --- | --- | --- | --- | --- |
| Alice | held by its own knots, with its fresh one: x1 x2 x3 c s1 s2 h1 h2 zA | x2 | no | 1/3 |
| Alice | held by its own knots, with its fresh one: x1 x2 x3 c s1 s2 h1 h2 zA | x3 | no | 1/3 |
| Bob | held by its own knots, with its fresh one: y1 y2 y3 t m1 m2 s1 k1 k2 s2 zB | y2 | yes | 0 |
| Bob | held by its own knots, with its fresh one: y1 y2 y3 t m1 m2 s1 k1 k2 s2 zB | y3 | yes | 0 |
| Alice | the same without s1 and s2 (beside, deviations B4): x1 x2 x3 c h1 h2 zA | x2 | yes | 0 |
| Alice | the same without s1 and s2 (beside, deviations B4): x1 x2 x3 c h1 h2 zA | x3 | yes | 0 |
| Bob | the same without s1 and s2 (beside, deviations B4): y1 y2 y3 t m1 m2 k1 k2 zB | y2 | yes | 0 |
| Bob | the same without s1 and s2 (beside, deviations B4): y1 y2 y3 t m1 m2 k1 k2 zB | y3 | yes | 0 |

Old words' distribution held fixed (deviations A11): reference weight of an old word = its number of completions in the reference structure, divided equally among its completions under each choice.

| reference | weighted totals (00, 01, 10, 11; weights x4) | Alice hidden | Bob hidden | score (i) | score (ii) (with the constant) | score (iii) |
| --- | --- | --- | --- | --- | --- | --- |
| old structure (beside) | 256, 256, 256, 256 | yes | yes | 2 | 2 (2) | 2 |
| x2, y2 | 576, 576, 576, 576 | yes | yes | 2 | 2 (2) | 2 |
| x2, y3 | 576, 576, 576, 576 | yes | yes | 2 | 2 (2) | 2 |
| x3, y2 | 576, 576, 576, 576 | yes | yes | 2 | 2 (2) | 2 |
| x3, y3 | 576, 576, 576, 576 | yes | yes | 2 | 2 (2) | 2 |

### (d) Three options each

| Alice choice | Bob choice | allowed words | Alice's five-value record the same for all three of Bob's choices | Bob's the same for all three of Alice's |
| --- | --- | --- | --- | --- |
| c | t | 256 | yes | yes |
| c | y2 | 192 | yes | yes |
| c | y3 | 192 | yes | yes |
| x2 | t | 192 | yes | yes |
| x2 | y2 | 144 | yes | yes |
| x2 | y3 | 144 | yes | yes |
| x3 | t | 192 | yes | yes |
| x3 | y2 | 144 | yes | yes |
| x3 | y3 | 144 | yes | yes |

Two-by-two sub-tests on the five-value records (x1, x2, x3, c, zA) and (y1, y2, y3, t, zB):

| Alice pair (o0, o1) | Bob pair (p0, p1) | allowed words (o0p0, o0p1, o1p0, o1p1) | Alice hidden (largest change) | Bob hidden (largest change) | score (i) | score (ii) (with the constant) | score (iii) | hidden excess |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| x2, x3 | y2, y3 | 144, 144, 144, 144 | yes (0) | yes (0) | 20/9 | 20/9 (20/9) | 20/9 | yes |
| x2, x3 | y2, t | 144, 192, 144, 192 | yes (0) | yes (0) | 19/9 | 19/9 (19/9) | 19/9 | yes |
| x2, x3 | y3, t | 144, 192, 144, 192 | yes (0) | yes (0) | 19/9 | 19/9 (19/9) | 19/9 | yes |
| x2, c | y2, y3 | 144, 144, 192, 192 | yes (0) | yes (0) | 19/9 | 19/9 (19/9) | 19/9 | yes |
| x2, c | y2, t | 144, 192, 192, 256 | yes (0) | yes (0) | 37/18 | 37/18 (37/18) | 37/18 | yes |
| x2, c | y3, t | 144, 192, 192, 256 | yes (0) | yes (0) | 37/18 | 37/18 (37/18) | 37/18 | yes |
| x3, c | y2, y3 | 144, 144, 192, 192 | yes (0) | yes (0) | 19/9 | 19/9 (19/9) | 19/9 | yes |
| x3, c | y2, t | 144, 192, 192, 256 | yes (0) | yes (0) | 37/18 | 37/18 (37/18) | 37/18 | yes |
| x3, c | y3, t | 144, 192, 192, 256 | yes (0) | yes (0) | 37/18 | 37/18 (37/18) | 37/18 | yes |

Largest score (i) over the nine sub-tests: 20/9 (over the hidden ones: 20/9).

### (e) One or two knots left out (66 structures)

Knots: 0 even(x1,x2,x3,c), 1 nae(c,x2,s1), 2 nae(c,x3,s2), 3 even(x2,h1,h2), 4 odd(x3,h1,h2), 5 even(y1,y2,y3,t), 6 even(t,m1,m2), 7 even(s1,m1,m2), 8 even(y2,k1,k2), 9 odd(y3,k1,k2), 10 odd(s2,k1,k2).

| left out | round 1 | births (parent knots: taken distinctions; fresh) | options on x1 / y1 | strict (judged) | two one-parent, joint allowed (beside) | loose (beside) | hidden excess | largest hidden score (i) | engines agree |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | x1 or y1 held by no knot |  |  | no | no | no |  |  |  |
| 1 | extend | 5+7: y1 s1 (1); 0: x1 x2 (1) | x2, x3, c / - | no | no | no |  |  | yes |
| 2 | extend | 5+10: y1 s2 (1); 0: x1 x2 (1) | x2, x3, c / - | no | no | no |  |  | yes |
| 3 | extend | 0+4: x1 h2 (1); 4: h1 x3 (1); 5: y1 y2 (1) | - / y2, y3, t | no | no | no |  |  | yes |
| 4 | extend | 0+3: x1 h2 (1); 3: h1 x2 (1); 5: y1 y2 (1) | - / y2, y3, t | no | no | no |  |  | yes |
| 5 | x1 or y1 held by no knot |  |  | no | no | no |  |  |  |
| 6 | extend | 0+7: x1 m2 (1); 5: t y2 (1); 5: y1 y2 (1); 7: m1 s1 (1) | - / y2, y3 | no | no | no |  |  | yes |
| 7 | extend | 0+1: x1 s1 (1); 5: y1 y2 (2); 6: m2 t (2); 6: m1 t (2) | - / y2, y3, t | no | no | no |  |  | yes |
| 8 | extend | 0: x1 x2 (1); 5: y2 y3 (1); 5: y1 y3 (1) | x2, x3, c / y3, t | no | no | yes | yes | 55/27 | yes |
| 9 | extend | 0: x1 x2 (1); 5: y3 y2 (1); 5: y1 y2 (1) | x2, x3, c / y2, t | no | no | yes | yes | 55/27 | yes |
| 10 | extend | 0+2: x1 s2 (1); 5: y1 y2 (1) | - / y2, y3, t | no | no | no |  |  | yes |
| 0, 1 | x1 or y1 held by no knot |  |  | no | no | no |  |  |  |
| 0, 2 | x1 or y1 held by no knot |  |  | no | no | no |  |  |  |
| 0, 3 | x1 or y1 held by no knot |  |  | no | no | no |  |  |  |
| 0, 4 | x1 or y1 held by no knot |  |  | no | no | no |  |  |  |
| 0, 5 | x1 or y1 held by no knot |  |  | no | no | no |  |  |  |
| 0, 6 | x1 or y1 held by no knot |  |  | no | no | no |  |  |  |
| 0, 7 | x1 or y1 held by no knot |  |  | no | no | no |  |  |  |
| 0, 8 | x1 or y1 held by no knot |  |  | no | no | no |  |  |  |
| 0, 9 | x1 or y1 held by no knot |  |  | no | no | no |  |  |  |
| 0, 10 | x1 or y1 held by no knot |  |  | no | no | no |  |  |  |
| 1, 2 | stall | shortage: knot 3 short by 1 |  | no | no | no |  |  | yes |
| 1, 3 | extend | 0+4: x2 h2 (2); 5+7: y1 s1 (1); 0: x1 x3 (2); 4: h1 x3 (2) | x3, c / - | no | no | no |  |  | yes |
| 1, 4 | extend | 5+7: y1 s1 (1); 0: x1 x2 (2); 3: h2 x2 (2); 3: h1 x2 (2) | x2, x3, c / - | no | no | no |  |  | yes |
| 1, 5 | x1 or y1 held by no knot |  |  | no | no | no |  |  |  |
| 1, 6 | extend | 0: x1 x2 (1); 5: t y2 (1); 5: y1 y2 (1); 7: m2 (2); 7: m1 (2); 7: s1 (2) | x2, x3, c / y2, y3 | no | no | yes | no | 2 | yes |
| 1, 7 | extend | 0: x1 x2 (1); 5: y1 y2 (2); 6: m2 t (2); 6: m1 t (2) | x2, x3, c / y2, y3, t | no | no | yes | no | 0 | yes |
| 1, 8 | extend | 5+7: y2 s1 (1); 0: x1 x2 (1); 5: y1 y3 (1) | x2, x3, c / y3, t | no | yes | yes | no | 2 | yes |
| 1, 9 | extend | 5+7: y3 s1 (1); 0: x1 x2 (1); 5: y1 y2 (1) | x2, x3, c / y2, t | no | yes | yes | no | 2 | yes |
| 1, 10 | extend | 0+2: x1 s2 (1); 5+7: y1 s1 (1) | - / - | no | no | no |  |  | yes |
| 2, 3 | extend | 5+10: y1 s2 (1); 0: x1 x2 (2); 4: h2 x3 (2); 4: h1 x3 (2) | x2, x3, c / - | no | no | no |  |  | yes |
| 2, 4 | extend | 0+3: x3 h2 (2); 5+10: y1 s2 (1); 0: x1 x2 (2); 3: h1 x2 (2) | x2, c / - | no | no | no |  |  | yes |
| 2, 5 | x1 or y1 held by no knot |  |  | no | no | no |  |  |  |
| 2, 6 | extend | 0+7: x1 m2 (1); 5+10: t s2 (1); 5: y1 y2 (1); 7: m1 s1 (1) | - / y2, y3 | no | no | no |  |  | yes |
| 2, 7 | extend | 0+1: x1 s1 (1); 5+10: y1 s2 (2); 6: m2 t (2); 6: m1 t (2) | - / - | no | no | no |  |  | yes |
| 2, 8 | extend | 5+10: y2 s2 (1); 0: x1 x2 (1); 5: y1 y3 (1) | x2, x3, c / y3, t | no | yes | yes | no | 2 | yes |
| 2, 9 | extend | 5+10: y3 s2 (1); 0: x1 x2 (1); 5: y1 y2 (1) | x2, x3, c / y2, t | no | yes | yes | no | 2 | yes |
| 2, 10 | extend | 0: x1 x2 (1); 5: y1 y2 (1) | x2, x3, c / y2, y3, t | yes | yes | yes | no | 2 | yes |
| 3, 4 | extend | 0: x1 x2 (1); 5: y1 y2 (1) | x2, x3, c / y2, y3, t | yes | yes | yes | no | 0 | yes |
| 3, 5 | x1 or y1 held by no knot |  |  | no | no | no |  |  |  |
| 3, 6 | stall | shortage: knot 0 short by 1 |  | no | no | no |  |  | yes |
| 3, 7 | stall | shortage: knot 0 short by 1; knot 1 short by 1 |  | no | no | no |  |  | yes |
| 3, 8 | extend | 0+4: x1 h2 (1); 4: h1 x3 (1); 5: y2 y3 (1); 5: y1 y3 (1) | - / y3, t | no | no | no |  |  | yes |
| 3, 9 | extend | 0+4: x1 h2 (1); 4: h1 x3 (1); 5: y3 y2 (1); 5: y1 y2 (1) | - / y2, t | no | no | no |  |  | yes |
| 3, 10 | extend | 0+2+4: x1 s2 h2 (1); 4: h1 x3 (1); 5: y1 y2 (1) | - / y2, y3, t | no | no | no |  |  | yes |
| 4, 5 | x1 or y1 held by no knot |  |  | no | no | no |  |  |  |
| 4, 6 | stall | shortage: knot 0 short by 1 |  | no | no | no |  |  | yes |
| 4, 7 | extend | 0+1+3: x1 s1 h2 (1); 3: h1 x2 (1); 5: y1 y2 (2); 6: m2 t (2); 6: m1 t (2) | - / y2, y3, t | no | no | no |  |  | yes |
| 4, 8 | extend | 0+3: x1 h2 (1); 3: h1 x2 (1); 5: y2 y3 (1); 5: y1 y3 (1) | - / y3, t | no | no | no |  |  | yes |
| 4, 9 | extend | 0+3: x1 h2 (1); 3: h1 x2 (1); 5: y3 y2 (1); 5: y1 y2 (1) | - / y2, t | no | no | no |  |  | yes |
| 4, 10 | stall | shortage: knot 0 short by 1; knot 2 short by 1 |  | no | no | no |  |  | yes |
| 5, 6 | x1 or y1 held by no knot |  |  | no | no | no |  |  |  |
| 5, 7 | x1 or y1 held by no knot |  |  | no | no | no |  |  |  |
| 5, 8 | x1 or y1 held by no knot |  |  | no | no | no |  |  |  |
| 5, 9 | x1 or y1 held by no knot |  |  | no | no | no |  |  |  |
| 5, 10 | x1 or y1 held by no knot |  |  | no | no | no |  |  |  |
| 6, 7 | extend | 0+1: x1 s1 (1); 5: t y2 (1); 5: y1 y2 (1) | - / y2, y3 | no | no | no |  |  | yes |
| 6, 8 | extend | 0+7: x1 m2 (1); 5: t y3 (2); 5: y2 y3 (2); 5: y1 y3 (2); 7: m1 s1 (1) | - / y3 | no | no | no |  |  | yes |
| 6, 9 | extend | 0+7: x1 m2 (1); 5: t y2 (2); 5: y3 y2 (2); 5: y1 y2 (2); 7: m1 s1 (1) | - / y2 | no | no | no |  |  | yes |
| 6, 10 | stall | shortage: knot 0 short by 1; knot 2 short by 1 |  | no | no | no |  |  | yes |
| 7, 8 | extend | 0+1: x1 s1 (1); 5: y2 y3 (3); 5: y1 y3 (3); 6: m2 t (3); 6: m1 t (3) | - / y3, t | no | no | no |  |  | yes |
| 7, 9 | extend | 0+1: x1 s1 (1); 5: y3 y2 (3); 5: y1 y2 (3); 6: m2 t (3); 6: m1 t (3) | - / y2, t | no | no | no |  |  | yes |
| 7, 10 | extend | 0+1+2: x1 s1 s2 (1); 5: y1 y2 (2); 6: m2 t (2); 6: m1 t (2) | - / y2, y3, t | no | no | no |  |  | yes |
| 8, 9 | extend | 0+10: x1 k2 (1); 5: y3 t (2); 5: y2 t (2); 5: y1 t (2); 10: k1 s2 (1) | - / t | no | no | no |  |  | yes |
| 8, 10 | extend | 0+2: x1 s2 (1); 5: y2 y3 (3); 5: y1 y3 (3); 9: k2 y3 (3); 9: k1 y3 (3) | - / y3, t | no | no | no |  |  | yes |
| 9, 10 | extend | 0+2: x1 s2 (1); 5: y3 y2 (3); 5: y1 y2 (3); 8: k2 y2 (3); 8: k1 y2 (3) | - / y2, t | no | no | no |  |  | yes |

(e) without knots 8 (even(y2,k1,k2)), loose reading only (beside, not judged); tables: {'summed out, checked against full enumeration': 24}:

| other births' choices | Alice pair (o0, o1) | Bob pair (p0, p1) | allowed words (o0p0, o0p1, o1p0, o1p1) | Alice hidden (largest change) | Bob hidden (largest change) | score (i) | score (ii) (with the constant) | score (iii) | hidden excess |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| birth 1: y3 | x2, x3 | y3, t | 432, 480, 432, 480 | yes (0) | yes (0) | 55/27 | 55/27 (55/27) | 55/27 | yes |
| birth 1: y3 | x2, c | y3, t | 432, 480, 576, 640 | yes (0) | yes (0) | 109/54 | 109/54 (109/54) | 109/54 | yes |
| birth 1: y3 | x3, c | y3, t | 432, 480, 576, 640 | yes (0) | yes (0) | 109/54 | 109/54 (109/54) | 109/54 | yes |
| birth 1: t | x2, x3 | y3, t | 480, 432, 480, 432 | yes (0) | yes (0) | 55/27 | 55/27 (55/27) | 55/27 | yes |
| birth 1: t | x2, c | y3, t | 480, 432, 640, 576 | yes (0) | yes (0) | 109/54 | 109/54 (109/54) | 109/54 | yes |
| birth 1: t | x3, c | y3, t | 480, 432, 640, 576 | yes (0) | yes (0) | 109/54 | 109/54 (109/54) | 109/54 | yes |

(e) without knots 9 (odd(y3,k1,k2)), loose reading only (beside, not judged); tables: {'summed out, checked against full enumeration': 24}:

| other births' choices | Alice pair (o0, o1) | Bob pair (p0, p1) | allowed words (o0p0, o0p1, o1p0, o1p1) | Alice hidden (largest change) | Bob hidden (largest change) | score (i) | score (ii) (with the constant) | score (iii) | hidden excess |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| birth 1: y2 | x2, x3 | y2, t | 432, 480, 432, 480 | yes (0) | yes (0) | 55/27 | 55/27 (55/27) | 55/27 | yes |
| birth 1: y2 | x2, c | y2, t | 432, 480, 576, 640 | yes (0) | yes (0) | 109/54 | 109/54 (109/54) | 109/54 | yes |
| birth 1: y2 | x3, c | y2, t | 432, 480, 576, 640 | yes (0) | yes (0) | 109/54 | 109/54 (109/54) | 109/54 | yes |
| birth 1: t | x2, x3 | y2, t | 480, 432, 480, 432 | yes (0) | yes (0) | 55/27 | 55/27 (55/27) | 55/27 | yes |
| birth 1: t | x2, c | y2, t | 480, 432, 640, 576 | yes (0) | yes (0) | 109/54 | 109/54 (109/54) | 109/54 | yes |
| birth 1: t | x3, c | y2, t | 480, 432, 640, 576 | yes (0) | yes (0) | 109/54 | 109/54 (109/54) | 109/54 | yes |

(e) without knots 1, 6 (nae(c,x2,s1); even(t,m1,m2)), loose reading only (beside, not judged); tables: {'summed out': 24}:

| other births' choices | Alice pair (o0, o1) | Bob pair (p0, p1) | allowed words (o0p0, o0p1, o1p0, o1p1) | Alice hidden (largest change) | Bob hidden (largest change) | score (i) | score (ii) (with the constant) | score (iii) | hidden excess |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| birth 1: y2 | x2, x3 | y2, y3 | 17280, 21600, 13824, 17280 | yes (0) | yes (0) | 2 | 2 (2) | 2 | no |
| birth 1: y2 | x2, c | y2, y3 | 17280, 21600, 20736, 25920 | yes (0) | yes (0) | 2 | 2 (2) | 2 | no |
| birth 1: y2 | x3, c | y2, y3 | 13824, 17280, 20736, 25920 | yes (0) | yes (0) | 2 | 2 (2) | 2 | no |
| birth 1: y3 | x2, x3 | y2, y3 | 21600, 17280, 17280, 13824 | yes (0) | yes (0) | 2 | 2 (2) | 2 | no |
| birth 1: y3 | x2, c | y2, y3 | 21600, 17280, 25920, 20736 | yes (0) | yes (0) | 2 | 2 (2) | 2 | no |
| birth 1: y3 | x3, c | y2, y3 | 17280, 13824, 25920, 20736 | yes (0) | yes (0) | 2 | 2 (2) | 2 | no |

(e) without knots 1, 7 (nae(c,x2,s1); even(s1,m1,m2)), loose reading only (beside, not judged); tables: {'summed out, checked against full enumeration': 36}:

| other births' choices | Alice pair (o0, o1) | Bob pair (p0, p1) | allowed words (o0p0, o0p1, o1p0, o1p1) | Alice hidden (largest change) | Bob hidden (largest change) | score (i) | score (ii) (with the constant) | score (iii) | hidden excess |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| birth 2: t, birth 3: t | x2, x3 | y2, y3 | 6860, 6860, 5488, 5488 | no (1/686) | yes (0) | 687/343 | 687/343 (687/343) | 687/343 | no |
| birth 2: t, birth 3: t | x2, x3 | y2, t | 6860, 7840, 5488, 6272 | no (1/1372) | yes (0) | 1373/686 | 1373/686 (1373/686) | 1373/686 | no |
| birth 2: t, birth 3: t | x2, x3 | y3, t | 6860, 7840, 5488, 6272 | no (1/1372) | yes (0) | 1373/686 | 1373/686 (1373/686) | 1373/686 | no |
| birth 2: t, birth 3: t | x2, c | y2, y3 | 6860, 6860, 8232, 8232 | no (1/1029) | yes (0) | 2060/1029 | 2060/1029 (2060/1029) | 2060/1029 | no |
| birth 2: t, birth 3: t | x2, c | y2, t | 6860, 7840, 8232, 9408 | no (1/2058) | yes (0) | 2059/1029 | 2059/1029 (2059/1029) | 2059/1029 | no |
| birth 2: t, birth 3: t | x2, c | y3, t | 6860, 7840, 8232, 9408 | no (1/2058) | yes (0) | 2059/1029 | 2059/1029 (2059/1029) | 2059/1029 | no |
| birth 2: t, birth 3: t | x3, c | y2, y3 | 5488, 5488, 8232, 8232 | no (1/686) | yes (0) | 687/343 | 687/343 (687/343) | 687/343 | no |
| birth 2: t, birth 3: t | x3, c | y2, t | 5488, 6272, 8232, 9408 | no (1/1372) | yes (0) | 1373/686 | 1373/686 (1373/686) | 1373/686 | no |
| birth 2: t, birth 3: t | x3, c | y3, t | 5488, 6272, 8232, 9408 | no (1/1372) | yes (0) | 1373/686 | 1373/686 (1373/686) | 1373/686 | no |

(e) without knots 1, 8 (nae(c,x2,s1); even(y2,k1,k2)), loose reading only (beside, not judged); tables: {'summed out, checked against full enumeration': 12}:

| other births' choices | Alice pair (o0, o1) | Bob pair (p0, p1) | allowed words (o0p0, o0p1, o1p0, o1p1) | Alice hidden (largest change) | Bob hidden (largest change) | score (i) | score (ii) (with the constant) | score (iii) | hidden excess |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| - | x2, x3 | y3, t | 800, 720, 640, 576 | yes (0) | yes (0) | 2 | 6/5 (2) | 2 | no |
| - | x2, c | y3, t | 800, 720, 960, 864 | yes (0) | yes (0) | 2 | 6/5 (2) | 2 | no |
| - | x3, c | y3, t | 640, 576, 960, 864 | yes (0) | yes (0) | 2 | 6/5 (2) | 2 | no |

(e) without knots 1, 9 (nae(c,x2,s1); odd(y3,k1,k2)), loose reading only (beside, not judged); tables: {'summed out, checked against full enumeration': 12}:

| other births' choices | Alice pair (o0, o1) | Bob pair (p0, p1) | allowed words (o0p0, o0p1, o1p0, o1p1) | Alice hidden (largest change) | Bob hidden (largest change) | score (i) | score (ii) (with the constant) | score (iii) | hidden excess |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| - | x2, x3 | y2, t | 800, 720, 640, 576 | yes (0) | yes (0) | 2 | 6/5 (2) | 2 | no |
| - | x2, c | y2, t | 800, 720, 960, 864 | yes (0) | yes (0) | 2 | 6/5 (2) | 2 | no |
| - | x3, c | y2, t | 640, 576, 960, 864 | yes (0) | yes (0) | 2 | 6/5 (2) | 2 | no |

(e) without knots 2, 8 (nae(c,x3,s2); even(y2,k1,k2)), loose reading only (beside, not judged); tables: {'summed out, checked against full enumeration': 12}:

| other births' choices | Alice pair (o0, o1) | Bob pair (p0, p1) | allowed words (o0p0, o0p1, o1p0, o1p1) | Alice hidden (largest change) | Bob hidden (largest change) | score (i) | score (ii) (with the constant) | score (iii) | hidden excess |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| - | x2, x3 | y3, t | 576, 640, 720, 800 | yes (0) | yes (0) | 2 | 6/5 (2) | 2 | no |
| - | x2, c | y3, t | 576, 640, 864, 960 | yes (0) | yes (0) | 2 | 6/5 (2) | 2 | no |
| - | x3, c | y3, t | 720, 800, 864, 960 | yes (0) | yes (0) | 2 | 6/5 (2) | 2 | no |

(e) without knots 2, 9 (nae(c,x3,s2); odd(y3,k1,k2)), loose reading only (beside, not judged); tables: {'summed out, checked against full enumeration': 12}:

| other births' choices | Alice pair (o0, o1) | Bob pair (p0, p1) | allowed words (o0p0, o0p1, o1p0, o1p1) | Alice hidden (largest change) | Bob hidden (largest change) | score (i) | score (ii) (with the constant) | score (iii) | hidden excess |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| - | x2, x3 | y2, t | 576, 512, 720, 640 | yes (0) | yes (0) | 2 | 1 (2) | 2 | no |
| - | x2, c | y2, t | 576, 512, 864, 768 | yes (0) | yes (0) | 2 | 1 (2) | 2 | no |
| - | x3, c | y2, t | 720, 640, 864, 768 | yes (0) | yes (0) | 2 | 1 (2) | 2 | no |

(e) without knots 2, 10 (nae(c,x3,s2); odd(s2,k1,k2)), strict reading (judged); tables: {'enumerated': 36}:

| other births' choices | Alice pair (o0, o1) | Bob pair (p0, p1) | allowed words (o0p0, o0p1, o1p0, o1p1) | Alice hidden (largest change) | Bob hidden (largest change) | score (i) | score (ii) (with the constant) | score (iii) | hidden excess |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| - | x2, x3 | y2, y3 | 192, 192, 240, 240 | yes (0) | yes (0) | 2 | 2 (2) | 2 | no |
| - | x2, x3 | y2, t | 192, 256, 240, 320 | yes (0) | yes (0) | 2 | 2 (2) | 2 | no |
| - | x2, x3 | y3, t | 192, 256, 240, 320 | yes (0) | yes (0) | 2 | 2 (2) | 2 | no |
| - | x2, c | y2, y3 | 192, 192, 288, 288 | yes (0) | yes (0) | 2 | 2 (2) | 2 | no |
| - | x2, c | y2, t | 192, 256, 288, 384 | yes (0) | yes (0) | 2 | 2 (2) | 2 | no |
| - | x2, c | y3, t | 192, 256, 288, 384 | yes (0) | yes (0) | 2 | 2 (2) | 2 | no |
| - | x3, c | y2, y3 | 240, 240, 288, 288 | yes (0) | yes (0) | 2 | 2 (2) | 2 | no |
| - | x3, c | y2, t | 240, 320, 288, 384 | yes (0) | yes (0) | 2 | 2 (2) | 2 | no |
| - | x3, c | y3, t | 240, 320, 288, 384 | yes (0) | yes (0) | 2 | 2 (2) | 2 | no |

(e) without knots 3, 4 (even(x2,h1,h2); odd(x3,h1,h2)), strict reading (judged); tables: {'enumerated': 36}:

| other births' choices | Alice pair (o0, o1) | Bob pair (p0, p1) | allowed words (o0p0, o0p1, o1p0, o1p1) | Alice hidden (largest change) | Bob hidden (largest change) | score (i) | score (ii) (with the constant) | score (iii) | hidden excess |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| - | x2, x3 | y2, y3 | 176, 184, 176, 184 | no (21/506) | yes (0) | 527/253 | 14/11 (524/253) | 527/253 | no |
| - | x2, x3 | y2, t | 176, 240, 176, 240 | no (7/330) | yes (0) | 337/165 | 14/11 (112/55) | 337/165 | no |
| - | x2, x3 | y3, t | 184, 240, 184, 240 | no (7/345) | yes (0) | 704/345 | 6/5 (234/115) | 704/345 | no |
| - | x2, c | y2, y3 | 176, 184, 152, 160 | no (9/190) | no (1/209) | 199/95 | 30398/24035 (524/253) | 199/95 | no |
| - | x2, c | y2, t | 176, 240, 152, 208 | no (6/247) | no (1/195) | 4403/2145 | 17236/13585 (112/55) | 4403/2145 | no |
| - | x2, c | y3, t | 184, 240, 160, 208 | no (3/130) | no (1/195) | 707/345 | 11263/8970 (234/115) | 707/345 | no |
| - | x3, c | y2, y3 | 176, 184, 152, 160 | no (9/190) | no (1/209) | 199/95 | 30398/24035 (524/253) | 199/95 | no |
| - | x3, c | y2, t | 176, 240, 152, 208 | no (6/247) | no (1/195) | 4403/2145 | 17236/13585 (112/55) | 4403/2145 | no |
| - | x3, c | y3, t | 184, 240, 160, 208 | no (3/130) | no (1/195) | 707/345 | 11263/8970 (234/115) | 707/345 | no |

### (f) Every even/odd assignment of the nine parity knots (pair (x2, x3) against (y2, y3))

Assignments: 512; with no allowed word in some stage-1 structure: 0; with a hidden excess by score (i): 128 (by (ii): 128, by (iii): 128). The note's structure is assignment 388.

| x2 and x3 forced to differ (laws of even(x2,h1,h2), odd(x3,h1,h2) differ) | y2 and y3 forced to differ (laws of even(y2,k1,k2), odd(y3,k1,k2) differ) | assignments | Alice hidden | Bob hidden | score (i) | score (ii) | score (iii) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| yes | yes | 128 | yes | yes | 20/9 | 20/9 | 20/9 |
| yes | no | 128 | yes | yes | 2 | 2 | 2 |
| no | yes | 64 | no | yes | 194/91 | 194/91 | 194/91 |
| no | yes | 64 | no | yes | 23/10 | 23/10 | 23/10 |
| no | no | 128 | yes | yes | 2 | 2 | 2 |

Every assignment (laws in the order of deviations A14, e = even, o = odd; allowed words of the four stage-1 structures x2y2, x2y3, x3y2, x3y3; Alice hidden; Bob hidden; scores (i), (ii), (iii); hidden excess):

```text
  0 eeeeeeeee 208/208/208/208 A:h B:h 2 2 2 
  1 oeeeeeeee 128/128/128/128 A:h B:h 2 2 2 
  2 eoeeeeeee 144/144/144/144 A:h B:h 2 2 2 
  3 ooeeeeeee 144/144/144/144 A:h B:h 2 2 2 
  4 eeoeeeeee 144/144/144/144 A:h B:h 2 2 2 
  5 oeoeeeeee 144/144/144/144 A:h B:h 2 2 2 
  6 eooeeeeee 208/208/208/208 A:h B:h 2 2 2 
  7 oooeeeeee 128/128/128/128 A:h B:h 2 2 2 
  8 eeeoeeeee 224/224/224/224 A:h B:h 2 2 2 
  9 oeeoeeeee 160/160/160/160 A:h B:h 2 2 2 
 10 eoeoeeeee 144/144/144/144 A:h B:h 2 2 2 
 11 ooeoeeeee 144/144/144/144 A:h B:h 2 2 2 
 12 eeooeeeee 144/144/144/144 A:h B:h 2 2 2 
 13 oeooeeeee 144/144/144/144 A:h B:h 2 2 2 
 14 eoooeeeee 224/224/224/224 A:h B:h 2 2 2 
 15 ooooeeeee 160/160/160/160 A:h B:h 2 2 2 
 16 eeeeoeeee 224/224/224/224 A:h B:h 2 2 2 
 17 oeeeoeeee 160/160/160/160 A:h B:h 2 2 2 
 18 eoeeoeeee 144/144/144/144 A:h B:h 2 2 2 
 19 ooeeoeeee 144/144/144/144 A:h B:h 2 2 2 
 20 eeoeoeeee 144/144/144/144 A:h B:h 2 2 2 
 21 oeoeoeeee 144/144/144/144 A:h B:h 2 2 2 
 22 eooeoeeee 224/224/224/224 A:h B:h 2 2 2 
 23 oooeoeeee 160/160/160/160 A:h B:h 2 2 2 
 24 eeeooeeee 208/208/208/208 A:h B:h 2 2 2 
 25 oeeooeeee 128/128/128/128 A:h B:h 2 2 2 
 26 eoeooeeee 144/144/144/144 A:h B:h 2 2 2 
 27 ooeooeeee 144/144/144/144 A:h B:h 2 2 2 
 28 eeoooeeee 144/144/144/144 A:h B:h 2 2 2 
 29 oeoooeeee 144/144/144/144 A:h B:h 2 2 2 
 30 eooooeeee 208/208/208/208 A:h B:h 2 2 2 
 31 oooooeeee 128/128/128/128 A:h B:h 2 2 2 
 32 eeeeeoeee 224/224/224/224 A:h B:h 2 2 2 
 33 oeeeeoeee 160/160/160/160 A:h B:h 2 2 2 
 34 eoeeeoeee 144/144/144/144 A:h B:h 2 2 2 
 35 ooeeeoeee 144/144/144/144 A:h B:h 2 2 2 
 36 eeoeeoeee 144/144/144/144 A:h B:h 2 2 2 
 37 oeoeeoeee 144/144/144/144 A:h B:h 2 2 2 
 38 eooeeoeee 224/224/224/224 A:h B:h 2 2 2 
 39 oooeeoeee 160/160/160/160 A:h B:h 2 2 2 
 40 eeeoeoeee 208/208/208/208 A:h B:h 2 2 2 
 41 oeeoeoeee 128/128/128/128 A:h B:h 2 2 2 
 42 eoeoeoeee 144/144/144/144 A:h B:h 2 2 2 
 43 ooeoeoeee 144/144/144/144 A:h B:h 2 2 2 
 44 eeooeoeee 144/144/144/144 A:h B:h 2 2 2 
 45 oeooeoeee 144/144/144/144 A:h B:h 2 2 2 
 46 eoooeoeee 208/208/208/208 A:h B:h 2 2 2 
 47 ooooeoeee 128/128/128/128 A:h B:h 2 2 2 
 48 eeeeooeee 208/208/208/208 A:h B:h 2 2 2 
 49 oeeeooeee 128/128/128/128 A:h B:h 2 2 2 
 50 eoeeooeee 144/144/144/144 A:h B:h 2 2 2 
 51 ooeeooeee 144/144/144/144 A:h B:h 2 2 2 
 52 eeoeooeee 144/144/144/144 A:h B:h 2 2 2 
 53 oeoeooeee 144/144/144/144 A:h B:h 2 2 2 
 54 eooeooeee 208/208/208/208 A:h B:h 2 2 2 
 55 oooeooeee 128/128/128/128 A:h B:h 2 2 2 
 56 eeeoooeee 224/224/224/224 A:h B:h 2 2 2 
 57 oeeoooeee 160/160/160/160 A:h B:h 2 2 2 
 58 eoeoooeee 144/144/144/144 A:h B:h 2 2 2 
 59 ooeoooeee 144/144/144/144 A:h B:h 2 2 2 
 60 eeooooeee 144/144/144/144 A:h B:h 2 2 2 
 61 oeooooeee 144/144/144/144 A:h B:h 2 2 2 
 62 eoooooeee 224/224/224/224 A:h B:h 2 2 2 
 63 ooooooeee 160/160/160/160 A:h B:h 2 2 2 
 64 eeeeeeoee 208/224/208/224 A:- B:h 194/91 194/91 194/91 
 65 oeeeeeoee 128/160/128/160 A:- B:h 23/10 23/10 23/10 
 66 eoeeeeoee 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
 67 ooeeeeoee 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
 68 eeoeeeoee 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
 69 oeoeeeoee 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
 70 eooeeeoee 208/224/208/224 A:- B:h 194/91 194/91 194/91 
 71 oooeeeoee 128/160/128/160 A:- B:h 23/10 23/10 23/10 
 72 eeeoeeoee 224/208/224/208 A:- B:h 194/91 194/91 194/91 
 73 oeeoeeoee 160/128/160/128 A:- B:h 23/10 23/10 23/10 
 74 eoeoeeoee 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
 75 ooeoeeoee 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
 76 eeooeeoee 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
 77 oeooeeoee 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
 78 eoooeeoee 224/208/224/208 A:- B:h 194/91 194/91 194/91 
 79 ooooeeoee 160/128/160/128 A:- B:h 23/10 23/10 23/10 
 80 eeeeoeoee 224/208/224/208 A:- B:h 194/91 194/91 194/91 
 81 oeeeoeoee 160/128/160/128 A:- B:h 23/10 23/10 23/10 
 82 eoeeoeoee 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
 83 ooeeoeoee 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
 84 eeoeoeoee 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
 85 oeoeoeoee 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
 86 eooeoeoee 224/208/224/208 A:- B:h 194/91 194/91 194/91 
 87 oooeoeoee 160/128/160/128 A:- B:h 23/10 23/10 23/10 
 88 eeeooeoee 208/224/208/224 A:- B:h 194/91 194/91 194/91 
 89 oeeooeoee 128/160/128/160 A:- B:h 23/10 23/10 23/10 
 90 eoeooeoee 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
 91 ooeooeoee 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
 92 eeoooeoee 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
 93 oeoooeoee 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
 94 eooooeoee 208/224/208/224 A:- B:h 194/91 194/91 194/91 
 95 oooooeoee 128/160/128/160 A:- B:h 23/10 23/10 23/10 
 96 eeeeeooee 224/208/224/208 A:- B:h 194/91 194/91 194/91 
 97 oeeeeooee 160/128/160/128 A:- B:h 23/10 23/10 23/10 
 98 eoeeeooee 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
 99 ooeeeooee 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
100 eeoeeooee 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
101 oeoeeooee 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
102 eooeeooee 224/208/224/208 A:- B:h 194/91 194/91 194/91 
103 oooeeooee 160/128/160/128 A:- B:h 23/10 23/10 23/10 
104 eeeoeooee 208/224/208/224 A:- B:h 194/91 194/91 194/91 
105 oeeoeooee 128/160/128/160 A:- B:h 23/10 23/10 23/10 
106 eoeoeooee 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
107 ooeoeooee 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
108 eeooeooee 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
109 oeooeooee 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
110 eoooeooee 208/224/208/224 A:- B:h 194/91 194/91 194/91 
111 ooooeooee 128/160/128/160 A:- B:h 23/10 23/10 23/10 
112 eeeeoooee 208/224/208/224 A:- B:h 194/91 194/91 194/91 
113 oeeeoooee 128/160/128/160 A:- B:h 23/10 23/10 23/10 
114 eoeeoooee 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
115 ooeeoooee 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
116 eeoeoooee 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
117 oeoeoooee 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
118 eooeoooee 208/224/208/224 A:- B:h 194/91 194/91 194/91 
119 oooeoooee 128/160/128/160 A:- B:h 23/10 23/10 23/10 
120 eeeooooee 224/208/224/208 A:- B:h 194/91 194/91 194/91 
121 oeeooooee 160/128/160/128 A:- B:h 23/10 23/10 23/10 
122 eoeooooee 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
123 ooeooooee 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
124 eeoooooee 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
125 oeoooooee 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
126 eooooooee 224/208/224/208 A:- B:h 194/91 194/91 194/91 
127 oooooooee 160/128/160/128 A:- B:h 23/10 23/10 23/10 
128 eeeeeeeoe 224/208/224/208 A:- B:h 194/91 194/91 194/91 
129 oeeeeeeoe 160/128/160/128 A:- B:h 23/10 23/10 23/10 
130 eoeeeeeoe 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
131 ooeeeeeoe 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
132 eeoeeeeoe 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
133 oeoeeeeoe 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
134 eooeeeeoe 224/208/224/208 A:- B:h 194/91 194/91 194/91 
135 oooeeeeoe 160/128/160/128 A:- B:h 23/10 23/10 23/10 
136 eeeoeeeoe 208/224/208/224 A:- B:h 194/91 194/91 194/91 
137 oeeoeeeoe 128/160/128/160 A:- B:h 23/10 23/10 23/10 
138 eoeoeeeoe 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
139 ooeoeeeoe 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
140 eeooeeeoe 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
141 oeooeeeoe 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
142 eoooeeeoe 208/224/208/224 A:- B:h 194/91 194/91 194/91 
143 ooooeeeoe 128/160/128/160 A:- B:h 23/10 23/10 23/10 
144 eeeeoeeoe 208/224/208/224 A:- B:h 194/91 194/91 194/91 
145 oeeeoeeoe 128/160/128/160 A:- B:h 23/10 23/10 23/10 
146 eoeeoeeoe 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
147 ooeeoeeoe 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
148 eeoeoeeoe 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
149 oeoeoeeoe 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
150 eooeoeeoe 208/224/208/224 A:- B:h 194/91 194/91 194/91 
151 oooeoeeoe 128/160/128/160 A:- B:h 23/10 23/10 23/10 
152 eeeooeeoe 224/208/224/208 A:- B:h 194/91 194/91 194/91 
153 oeeooeeoe 160/128/160/128 A:- B:h 23/10 23/10 23/10 
154 eoeooeeoe 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
155 ooeooeeoe 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
156 eeoooeeoe 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
157 oeoooeeoe 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
158 eooooeeoe 224/208/224/208 A:- B:h 194/91 194/91 194/91 
159 oooooeeoe 160/128/160/128 A:- B:h 23/10 23/10 23/10 
160 eeeeeoeoe 208/224/208/224 A:- B:h 194/91 194/91 194/91 
161 oeeeeoeoe 128/160/128/160 A:- B:h 23/10 23/10 23/10 
162 eoeeeoeoe 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
163 ooeeeoeoe 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
164 eeoeeoeoe 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
165 oeoeeoeoe 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
166 eooeeoeoe 208/224/208/224 A:- B:h 194/91 194/91 194/91 
167 oooeeoeoe 128/160/128/160 A:- B:h 23/10 23/10 23/10 
168 eeeoeoeoe 224/208/224/208 A:- B:h 194/91 194/91 194/91 
169 oeeoeoeoe 160/128/160/128 A:- B:h 23/10 23/10 23/10 
170 eoeoeoeoe 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
171 ooeoeoeoe 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
172 eeooeoeoe 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
173 oeooeoeoe 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
174 eoooeoeoe 224/208/224/208 A:- B:h 194/91 194/91 194/91 
175 ooooeoeoe 160/128/160/128 A:- B:h 23/10 23/10 23/10 
176 eeeeooeoe 224/208/224/208 A:- B:h 194/91 194/91 194/91 
177 oeeeooeoe 160/128/160/128 A:- B:h 23/10 23/10 23/10 
178 eoeeooeoe 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
179 ooeeooeoe 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
180 eeoeooeoe 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
181 oeoeooeoe 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
182 eooeooeoe 224/208/224/208 A:- B:h 194/91 194/91 194/91 
183 oooeooeoe 160/128/160/128 A:- B:h 23/10 23/10 23/10 
184 eeeoooeoe 208/224/208/224 A:- B:h 194/91 194/91 194/91 
185 oeeoooeoe 128/160/128/160 A:- B:h 23/10 23/10 23/10 
186 eoeoooeoe 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
187 ooeoooeoe 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
188 eeooooeoe 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
189 oeooooeoe 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
190 eoooooeoe 208/224/208/224 A:- B:h 194/91 194/91 194/91 
191 ooooooeoe 128/160/128/160 A:- B:h 23/10 23/10 23/10 
192 eeeeeeooe 224/224/224/224 A:h B:h 2 2 2 
193 oeeeeeooe 160/160/160/160 A:h B:h 2 2 2 
194 eoeeeeooe 144/144/144/144 A:h B:h 2 2 2 
195 ooeeeeooe 144/144/144/144 A:h B:h 2 2 2 
196 eeoeeeooe 144/144/144/144 A:h B:h 2 2 2 
197 oeoeeeooe 144/144/144/144 A:h B:h 2 2 2 
198 eooeeeooe 224/224/224/224 A:h B:h 2 2 2 
199 oooeeeooe 160/160/160/160 A:h B:h 2 2 2 
200 eeeoeeooe 208/208/208/208 A:h B:h 2 2 2 
201 oeeoeeooe 128/128/128/128 A:h B:h 2 2 2 
202 eoeoeeooe 144/144/144/144 A:h B:h 2 2 2 
203 ooeoeeooe 144/144/144/144 A:h B:h 2 2 2 
204 eeooeeooe 144/144/144/144 A:h B:h 2 2 2 
205 oeooeeooe 144/144/144/144 A:h B:h 2 2 2 
206 eoooeeooe 208/208/208/208 A:h B:h 2 2 2 
207 ooooeeooe 128/128/128/128 A:h B:h 2 2 2 
208 eeeeoeooe 208/208/208/208 A:h B:h 2 2 2 
209 oeeeoeooe 128/128/128/128 A:h B:h 2 2 2 
210 eoeeoeooe 144/144/144/144 A:h B:h 2 2 2 
211 ooeeoeooe 144/144/144/144 A:h B:h 2 2 2 
212 eeoeoeooe 144/144/144/144 A:h B:h 2 2 2 
213 oeoeoeooe 144/144/144/144 A:h B:h 2 2 2 
214 eooeoeooe 208/208/208/208 A:h B:h 2 2 2 
215 oooeoeooe 128/128/128/128 A:h B:h 2 2 2 
216 eeeooeooe 224/224/224/224 A:h B:h 2 2 2 
217 oeeooeooe 160/160/160/160 A:h B:h 2 2 2 
218 eoeooeooe 144/144/144/144 A:h B:h 2 2 2 
219 ooeooeooe 144/144/144/144 A:h B:h 2 2 2 
220 eeoooeooe 144/144/144/144 A:h B:h 2 2 2 
221 oeoooeooe 144/144/144/144 A:h B:h 2 2 2 
222 eooooeooe 224/224/224/224 A:h B:h 2 2 2 
223 oooooeooe 160/160/160/160 A:h B:h 2 2 2 
224 eeeeeoooe 208/208/208/208 A:h B:h 2 2 2 
225 oeeeeoooe 128/128/128/128 A:h B:h 2 2 2 
226 eoeeeoooe 144/144/144/144 A:h B:h 2 2 2 
227 ooeeeoooe 144/144/144/144 A:h B:h 2 2 2 
228 eeoeeoooe 144/144/144/144 A:h B:h 2 2 2 
229 oeoeeoooe 144/144/144/144 A:h B:h 2 2 2 
230 eooeeoooe 208/208/208/208 A:h B:h 2 2 2 
231 oooeeoooe 128/128/128/128 A:h B:h 2 2 2 
232 eeeoeoooe 224/224/224/224 A:h B:h 2 2 2 
233 oeeoeoooe 160/160/160/160 A:h B:h 2 2 2 
234 eoeoeoooe 144/144/144/144 A:h B:h 2 2 2 
235 ooeoeoooe 144/144/144/144 A:h B:h 2 2 2 
236 eeooeoooe 144/144/144/144 A:h B:h 2 2 2 
237 oeooeoooe 144/144/144/144 A:h B:h 2 2 2 
238 eoooeoooe 224/224/224/224 A:h B:h 2 2 2 
239 ooooeoooe 160/160/160/160 A:h B:h 2 2 2 
240 eeeeooooe 224/224/224/224 A:h B:h 2 2 2 
241 oeeeooooe 160/160/160/160 A:h B:h 2 2 2 
242 eoeeooooe 144/144/144/144 A:h B:h 2 2 2 
243 ooeeooooe 144/144/144/144 A:h B:h 2 2 2 
244 eeoeooooe 144/144/144/144 A:h B:h 2 2 2 
245 oeoeooooe 144/144/144/144 A:h B:h 2 2 2 
246 eooeooooe 224/224/224/224 A:h B:h 2 2 2 
247 oooeooooe 160/160/160/160 A:h B:h 2 2 2 
248 eeeoooooe 208/208/208/208 A:h B:h 2 2 2 
249 oeeoooooe 128/128/128/128 A:h B:h 2 2 2 
250 eoeoooooe 144/144/144/144 A:h B:h 2 2 2 
251 ooeoooooe 144/144/144/144 A:h B:h 2 2 2 
252 eeooooooe 144/144/144/144 A:h B:h 2 2 2 
253 oeooooooe 144/144/144/144 A:h B:h 2 2 2 
254 eoooooooe 208/208/208/208 A:h B:h 2 2 2 
255 ooooooooe 128/128/128/128 A:h B:h 2 2 2 
256 eeeeeeeeo 224/224/224/224 A:h B:h 2 2 2 
257 oeeeeeeeo 160/160/160/160 A:h B:h 2 2 2 
258 eoeeeeeeo 144/144/144/144 A:h B:h 2 2 2 
259 ooeeeeeeo 144/144/144/144 A:h B:h 2 2 2 
260 eeoeeeeeo 144/144/144/144 A:h B:h 2 2 2 
261 oeoeeeeeo 144/144/144/144 A:h B:h 2 2 2 
262 eooeeeeeo 224/224/224/224 A:h B:h 2 2 2 
263 oooeeeeeo 160/160/160/160 A:h B:h 2 2 2 
264 eeeoeeeeo 208/208/208/208 A:h B:h 2 2 2 
265 oeeoeeeeo 128/128/128/128 A:h B:h 2 2 2 
266 eoeoeeeeo 144/144/144/144 A:h B:h 2 2 2 
267 ooeoeeeeo 144/144/144/144 A:h B:h 2 2 2 
268 eeooeeeeo 144/144/144/144 A:h B:h 2 2 2 
269 oeooeeeeo 144/144/144/144 A:h B:h 2 2 2 
270 eoooeeeeo 208/208/208/208 A:h B:h 2 2 2 
271 ooooeeeeo 128/128/128/128 A:h B:h 2 2 2 
272 eeeeoeeeo 208/208/208/208 A:h B:h 2 2 2 
273 oeeeoeeeo 128/128/128/128 A:h B:h 2 2 2 
274 eoeeoeeeo 144/144/144/144 A:h B:h 2 2 2 
275 ooeeoeeeo 144/144/144/144 A:h B:h 2 2 2 
276 eeoeoeeeo 144/144/144/144 A:h B:h 2 2 2 
277 oeoeoeeeo 144/144/144/144 A:h B:h 2 2 2 
278 eooeoeeeo 208/208/208/208 A:h B:h 2 2 2 
279 oooeoeeeo 128/128/128/128 A:h B:h 2 2 2 
280 eeeooeeeo 224/224/224/224 A:h B:h 2 2 2 
281 oeeooeeeo 160/160/160/160 A:h B:h 2 2 2 
282 eoeooeeeo 144/144/144/144 A:h B:h 2 2 2 
283 ooeooeeeo 144/144/144/144 A:h B:h 2 2 2 
284 eeoooeeeo 144/144/144/144 A:h B:h 2 2 2 
285 oeoooeeeo 144/144/144/144 A:h B:h 2 2 2 
286 eooooeeeo 224/224/224/224 A:h B:h 2 2 2 
287 oooooeeeo 160/160/160/160 A:h B:h 2 2 2 
288 eeeeeoeeo 208/208/208/208 A:h B:h 2 2 2 
289 oeeeeoeeo 128/128/128/128 A:h B:h 2 2 2 
290 eoeeeoeeo 144/144/144/144 A:h B:h 2 2 2 
291 ooeeeoeeo 144/144/144/144 A:h B:h 2 2 2 
292 eeoeeoeeo 144/144/144/144 A:h B:h 2 2 2 
293 oeoeeoeeo 144/144/144/144 A:h B:h 2 2 2 
294 eooeeoeeo 208/208/208/208 A:h B:h 2 2 2 
295 oooeeoeeo 128/128/128/128 A:h B:h 2 2 2 
296 eeeoeoeeo 224/224/224/224 A:h B:h 2 2 2 
297 oeeoeoeeo 160/160/160/160 A:h B:h 2 2 2 
298 eoeoeoeeo 144/144/144/144 A:h B:h 2 2 2 
299 ooeoeoeeo 144/144/144/144 A:h B:h 2 2 2 
300 eeooeoeeo 144/144/144/144 A:h B:h 2 2 2 
301 oeooeoeeo 144/144/144/144 A:h B:h 2 2 2 
302 eoooeoeeo 224/224/224/224 A:h B:h 2 2 2 
303 ooooeoeeo 160/160/160/160 A:h B:h 2 2 2 
304 eeeeooeeo 224/224/224/224 A:h B:h 2 2 2 
305 oeeeooeeo 160/160/160/160 A:h B:h 2 2 2 
306 eoeeooeeo 144/144/144/144 A:h B:h 2 2 2 
307 ooeeooeeo 144/144/144/144 A:h B:h 2 2 2 
308 eeoeooeeo 144/144/144/144 A:h B:h 2 2 2 
309 oeoeooeeo 144/144/144/144 A:h B:h 2 2 2 
310 eooeooeeo 224/224/224/224 A:h B:h 2 2 2 
311 oooeooeeo 160/160/160/160 A:h B:h 2 2 2 
312 eeeoooeeo 208/208/208/208 A:h B:h 2 2 2 
313 oeeoooeeo 128/128/128/128 A:h B:h 2 2 2 
314 eoeoooeeo 144/144/144/144 A:h B:h 2 2 2 
315 ooeoooeeo 144/144/144/144 A:h B:h 2 2 2 
316 eeooooeeo 144/144/144/144 A:h B:h 2 2 2 
317 oeooooeeo 144/144/144/144 A:h B:h 2 2 2 
318 eoooooeeo 208/208/208/208 A:h B:h 2 2 2 
319 ooooooeeo 128/128/128/128 A:h B:h 2 2 2 
320 eeeeeeoeo 224/208/224/208 A:- B:h 194/91 194/91 194/91 
321 oeeeeeoeo 160/128/160/128 A:- B:h 23/10 23/10 23/10 
322 eoeeeeoeo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
323 ooeeeeoeo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
324 eeoeeeoeo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
325 oeoeeeoeo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
326 eooeeeoeo 224/208/224/208 A:- B:h 194/91 194/91 194/91 
327 oooeeeoeo 160/128/160/128 A:- B:h 23/10 23/10 23/10 
328 eeeoeeoeo 208/224/208/224 A:- B:h 194/91 194/91 194/91 
329 oeeoeeoeo 128/160/128/160 A:- B:h 23/10 23/10 23/10 
330 eoeoeeoeo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
331 ooeoeeoeo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
332 eeooeeoeo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
333 oeooeeoeo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
334 eoooeeoeo 208/224/208/224 A:- B:h 194/91 194/91 194/91 
335 ooooeeoeo 128/160/128/160 A:- B:h 23/10 23/10 23/10 
336 eeeeoeoeo 208/224/208/224 A:- B:h 194/91 194/91 194/91 
337 oeeeoeoeo 128/160/128/160 A:- B:h 23/10 23/10 23/10 
338 eoeeoeoeo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
339 ooeeoeoeo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
340 eeoeoeoeo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
341 oeoeoeoeo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
342 eooeoeoeo 208/224/208/224 A:- B:h 194/91 194/91 194/91 
343 oooeoeoeo 128/160/128/160 A:- B:h 23/10 23/10 23/10 
344 eeeooeoeo 224/208/224/208 A:- B:h 194/91 194/91 194/91 
345 oeeooeoeo 160/128/160/128 A:- B:h 23/10 23/10 23/10 
346 eoeooeoeo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
347 ooeooeoeo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
348 eeoooeoeo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
349 oeoooeoeo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
350 eooooeoeo 224/208/224/208 A:- B:h 194/91 194/91 194/91 
351 oooooeoeo 160/128/160/128 A:- B:h 23/10 23/10 23/10 
352 eeeeeooeo 208/224/208/224 A:- B:h 194/91 194/91 194/91 
353 oeeeeooeo 128/160/128/160 A:- B:h 23/10 23/10 23/10 
354 eoeeeooeo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
355 ooeeeooeo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
356 eeoeeooeo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
357 oeoeeooeo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
358 eooeeooeo 208/224/208/224 A:- B:h 194/91 194/91 194/91 
359 oooeeooeo 128/160/128/160 A:- B:h 23/10 23/10 23/10 
360 eeeoeooeo 224/208/224/208 A:- B:h 194/91 194/91 194/91 
361 oeeoeooeo 160/128/160/128 A:- B:h 23/10 23/10 23/10 
362 eoeoeooeo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
363 ooeoeooeo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
364 eeooeooeo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
365 oeooeooeo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
366 eoooeooeo 224/208/224/208 A:- B:h 194/91 194/91 194/91 
367 ooooeooeo 160/128/160/128 A:- B:h 23/10 23/10 23/10 
368 eeeeoooeo 224/208/224/208 A:- B:h 194/91 194/91 194/91 
369 oeeeoooeo 160/128/160/128 A:- B:h 23/10 23/10 23/10 
370 eoeeoooeo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
371 ooeeoooeo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
372 eeoeoooeo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
373 oeoeoooeo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
374 eooeoooeo 224/208/224/208 A:- B:h 194/91 194/91 194/91 
375 oooeoooeo 160/128/160/128 A:- B:h 23/10 23/10 23/10 
376 eeeooooeo 208/224/208/224 A:- B:h 194/91 194/91 194/91 
377 oeeooooeo 128/160/128/160 A:- B:h 23/10 23/10 23/10 
378 eoeooooeo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
379 ooeooooeo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
380 eeoooooeo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
381 oeoooooeo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
382 eooooooeo 208/224/208/224 A:- B:h 194/91 194/91 194/91 
383 oooooooeo 128/160/128/160 A:- B:h 23/10 23/10 23/10 
384 eeeeeeeoo 208/224/208/224 A:- B:h 194/91 194/91 194/91 
385 oeeeeeeoo 128/160/128/160 A:- B:h 23/10 23/10 23/10 
386 eoeeeeeoo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
387 ooeeeeeoo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
388 eeoeeeeoo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS (note)
389 oeoeeeeoo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
390 eooeeeeoo 208/224/208/224 A:- B:h 194/91 194/91 194/91 
391 oooeeeeoo 128/160/128/160 A:- B:h 23/10 23/10 23/10 
392 eeeoeeeoo 224/208/224/208 A:- B:h 194/91 194/91 194/91 
393 oeeoeeeoo 160/128/160/128 A:- B:h 23/10 23/10 23/10 
394 eoeoeeeoo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
395 ooeoeeeoo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
396 eeooeeeoo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
397 oeooeeeoo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
398 eoooeeeoo 224/208/224/208 A:- B:h 194/91 194/91 194/91 
399 ooooeeeoo 160/128/160/128 A:- B:h 23/10 23/10 23/10 
400 eeeeoeeoo 224/208/224/208 A:- B:h 194/91 194/91 194/91 
401 oeeeoeeoo 160/128/160/128 A:- B:h 23/10 23/10 23/10 
402 eoeeoeeoo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
403 ooeeoeeoo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
404 eeoeoeeoo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
405 oeoeoeeoo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
406 eooeoeeoo 224/208/224/208 A:- B:h 194/91 194/91 194/91 
407 oooeoeeoo 160/128/160/128 A:- B:h 23/10 23/10 23/10 
408 eeeooeeoo 208/224/208/224 A:- B:h 194/91 194/91 194/91 
409 oeeooeeoo 128/160/128/160 A:- B:h 23/10 23/10 23/10 
410 eoeooeeoo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
411 ooeooeeoo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
412 eeoooeeoo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
413 oeoooeeoo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
414 eooooeeoo 208/224/208/224 A:- B:h 194/91 194/91 194/91 
415 oooooeeoo 128/160/128/160 A:- B:h 23/10 23/10 23/10 
416 eeeeeoeoo 224/208/224/208 A:- B:h 194/91 194/91 194/91 
417 oeeeeoeoo 160/128/160/128 A:- B:h 23/10 23/10 23/10 
418 eoeeeoeoo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
419 ooeeeoeoo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
420 eeoeeoeoo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
421 oeoeeoeoo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
422 eooeeoeoo 224/208/224/208 A:- B:h 194/91 194/91 194/91 
423 oooeeoeoo 160/128/160/128 A:- B:h 23/10 23/10 23/10 
424 eeeoeoeoo 208/224/208/224 A:- B:h 194/91 194/91 194/91 
425 oeeoeoeoo 128/160/128/160 A:- B:h 23/10 23/10 23/10 
426 eoeoeoeoo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
427 ooeoeoeoo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
428 eeooeoeoo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
429 oeooeoeoo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
430 eoooeoeoo 208/224/208/224 A:- B:h 194/91 194/91 194/91 
431 ooooeoeoo 128/160/128/160 A:- B:h 23/10 23/10 23/10 
432 eeeeooeoo 208/224/208/224 A:- B:h 194/91 194/91 194/91 
433 oeeeooeoo 128/160/128/160 A:- B:h 23/10 23/10 23/10 
434 eoeeooeoo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
435 ooeeooeoo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
436 eeoeooeoo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
437 oeoeooeoo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
438 eooeooeoo 208/224/208/224 A:- B:h 194/91 194/91 194/91 
439 oooeooeoo 128/160/128/160 A:- B:h 23/10 23/10 23/10 
440 eeeoooeoo 224/208/224/208 A:- B:h 194/91 194/91 194/91 
441 oeeoooeoo 160/128/160/128 A:- B:h 23/10 23/10 23/10 
442 eoeoooeoo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
443 ooeoooeoo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
444 eeooooeoo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
445 oeooooeoo 144/144/144/144 A:h B:h 20/9 20/9 20/9 EXCESS
446 eoooooeoo 224/208/224/208 A:- B:h 194/91 194/91 194/91 
447 ooooooeoo 160/128/160/128 A:- B:h 23/10 23/10 23/10 
448 eeeeeeooo 208/208/208/208 A:h B:h 2 2 2 
449 oeeeeeooo 128/128/128/128 A:h B:h 2 2 2 
450 eoeeeeooo 144/144/144/144 A:h B:h 2 2 2 
451 ooeeeeooo 144/144/144/144 A:h B:h 2 2 2 
452 eeoeeeooo 144/144/144/144 A:h B:h 2 2 2 
453 oeoeeeooo 144/144/144/144 A:h B:h 2 2 2 
454 eooeeeooo 208/208/208/208 A:h B:h 2 2 2 
455 oooeeeooo 128/128/128/128 A:h B:h 2 2 2 
456 eeeoeeooo 224/224/224/224 A:h B:h 2 2 2 
457 oeeoeeooo 160/160/160/160 A:h B:h 2 2 2 
458 eoeoeeooo 144/144/144/144 A:h B:h 2 2 2 
459 ooeoeeooo 144/144/144/144 A:h B:h 2 2 2 
460 eeooeeooo 144/144/144/144 A:h B:h 2 2 2 
461 oeooeeooo 144/144/144/144 A:h B:h 2 2 2 
462 eoooeeooo 224/224/224/224 A:h B:h 2 2 2 
463 ooooeeooo 160/160/160/160 A:h B:h 2 2 2 
464 eeeeoeooo 224/224/224/224 A:h B:h 2 2 2 
465 oeeeoeooo 160/160/160/160 A:h B:h 2 2 2 
466 eoeeoeooo 144/144/144/144 A:h B:h 2 2 2 
467 ooeeoeooo 144/144/144/144 A:h B:h 2 2 2 
468 eeoeoeooo 144/144/144/144 A:h B:h 2 2 2 
469 oeoeoeooo 144/144/144/144 A:h B:h 2 2 2 
470 eooeoeooo 224/224/224/224 A:h B:h 2 2 2 
471 oooeoeooo 160/160/160/160 A:h B:h 2 2 2 
472 eeeooeooo 208/208/208/208 A:h B:h 2 2 2 
473 oeeooeooo 128/128/128/128 A:h B:h 2 2 2 
474 eoeooeooo 144/144/144/144 A:h B:h 2 2 2 
475 ooeooeooo 144/144/144/144 A:h B:h 2 2 2 
476 eeoooeooo 144/144/144/144 A:h B:h 2 2 2 
477 oeoooeooo 144/144/144/144 A:h B:h 2 2 2 
478 eooooeooo 208/208/208/208 A:h B:h 2 2 2 
479 oooooeooo 128/128/128/128 A:h B:h 2 2 2 
480 eeeeeoooo 224/224/224/224 A:h B:h 2 2 2 
481 oeeeeoooo 160/160/160/160 A:h B:h 2 2 2 
482 eoeeeoooo 144/144/144/144 A:h B:h 2 2 2 
483 ooeeeoooo 144/144/144/144 A:h B:h 2 2 2 
484 eeoeeoooo 144/144/144/144 A:h B:h 2 2 2 
485 oeoeeoooo 144/144/144/144 A:h B:h 2 2 2 
486 eooeeoooo 224/224/224/224 A:h B:h 2 2 2 
487 oooeeoooo 160/160/160/160 A:h B:h 2 2 2 
488 eeeoeoooo 208/208/208/208 A:h B:h 2 2 2 
489 oeeoeoooo 128/128/128/128 A:h B:h 2 2 2 
490 eoeoeoooo 144/144/144/144 A:h B:h 2 2 2 
491 ooeoeoooo 144/144/144/144 A:h B:h 2 2 2 
492 eeooeoooo 144/144/144/144 A:h B:h 2 2 2 
493 oeooeoooo 144/144/144/144 A:h B:h 2 2 2 
494 eoooeoooo 208/208/208/208 A:h B:h 2 2 2 
495 ooooeoooo 128/128/128/128 A:h B:h 2 2 2 
496 eeeeooooo 208/208/208/208 A:h B:h 2 2 2 
497 oeeeooooo 128/128/128/128 A:h B:h 2 2 2 
498 eoeeooooo 144/144/144/144 A:h B:h 2 2 2 
499 ooeeooooo 144/144/144/144 A:h B:h 2 2 2 
500 eeoeooooo 144/144/144/144 A:h B:h 2 2 2 
501 oeoeooooo 144/144/144/144 A:h B:h 2 2 2 
502 eooeooooo 208/208/208/208 A:h B:h 2 2 2 
503 oooeooooo 128/128/128/128 A:h B:h 2 2 2 
504 eeeoooooo 224/224/224/224 A:h B:h 2 2 2 
505 oeeoooooo 160/160/160/160 A:h B:h 2 2 2 
506 eoeoooooo 144/144/144/144 A:h B:h 2 2 2 
507 ooeoooooo 144/144/144/144 A:h B:h 2 2 2 
508 eeooooooo 144/144/144/144 A:h B:h 2 2 2 
509 oeooooooo 144/144/144/144 A:h B:h 2 2 2 
510 eoooooooo 224/224/224/224 A:h B:h 2 2 2 
511 ooooooooo 160/160/160/160 A:h B:h 2 2 2 
```

