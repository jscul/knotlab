# Two countings of a structure's allowed states, side by side: result

Ticket `TWO-COUNTINGS-20261125-001A` of the study of two countings (sub-goal B324; assumptions A240, A71, A73, A110,
A185, A239; goals G17 with G18), 2026-11-25. Computed by an engine written from the frozen texts by a helper that had
not seen the drafter's prototype, then checked by a second helper that recounted the raw results with code of its own
(its own enumeration of allowed states, knot test, countings and score, and its own runs of the canonical command).
Evidence class of everything here: **computed, bounded, referee pending.**
[Pre-registration](preregistration.md) · [claim](../TWO-COUNTINGS-20261125-001/claim.md) ·
[definitions](../TWO-COUNTINGS-20261125-001/definitions.md) ·
[knot-test finding](../TWO-COUNTINGS-20261125-001/knot_test_finding.md) · [table](../TWO-COUNTINGS-20261125-001/table.json) ·
[code and its recorded readings](../../experiments/TWO-COUNTINGS-20261125-001A/TWO-COUNTINGS-20261125-001A-E001_two_countings/deviations.md)

**Counted from a common stage before the setting knots, every registered setting test scores exactly 2 with both
records hidden, as the lemma says: the 11-rule structure's nine option pairs, the smallest gain of the rule-Q line, the
7-knot, 8-rule, pencil 9-knot and 18-knot structures, the two 10-rule structures per history and pooled, the 8/3 case,
and all 894 grown records of the rule-Q and rule-R lines. Every registered score above 2 on the settings line is a
score under counting from the finish, and every one was reproduced (the whole-stage 9/4, the same under both countings,
and the two- and three-birth settings were not rerun). No run decides between the two countings: the excess is
what the thread's working choice (counting from the finish, reversible) produces, not evidence for it. The knot test in
the whole structure confirms the finding on all 33 registered structures (the 11-rule structure's two four-place
parity rules, the 8-rule structure's even(y1,y2,y3,s1) and the smallest gain's first setting knot at a = 0 are not
knots there; no rule fails on its own). Beyond the finding: in the rule-Q study's census, two parts of seven rules give
the hidden 61/30 under counting from the finish with every rule a knot in the whole, so the line's smallest gaining
part does not need a rule that fails; and a setting knot that takes c or t is not a knot in the 11-rule structure.**

The words used: a **counting** is our rule for a weighting of states, never made by the growth. **Counting from the
finish**: each allowed state of the finished structure counts once. **Counting from the start**: each allowed state of
the start counts once, and at each birth an old state's weight is divided equally among its completions; **counting
from stage s** does the same from a stage common to the histories compared. **The first observer** and **the second
observer** are each a supplied list of distinctions (their records are (x1,x2,x3,za) and (y1,y2,y3,zb)); nothing
observes. The **score** is the four-correlation score E00 + E01 + E10 − E11 (the literature's CHSH score, from Clauser,
Horne, Shimony and Holt), maximized over every pair of two-valued outcome functions of each observer's own record and
own setting; a record is **hidden** when the other observer's setting changes its distribution by exactly 0. A
**rule** is a parity or not-all-equal constraint as the records wrote it; it is called a **knot** only once it has
passed K1–K3 in the whole structure (its induced relation, every other distinction quantified away, constrained as a
whole, every part free, some state allowed). Structures are named by the records' names with "rule" where some of
their rules fail: the 11-rule structure is the record's "11-knot structure" (11 rules, 9 knots in the whole), the
8-rule and 10-rule structures likewise. **Rule Q** (A235): a one-parent birth also takes a distinction its parent
shares. **Rule R** (A230): a short knot pays the rest with shared distinctions.

## Verdicts

Nine predictions were frozen (P6 in two parts). All hold. The checker's recount agrees with the engine on every number
it recomputed; where it took a number from the raw output only, the row says so.

| # | Prediction (short) | Verdict | Numbers |
| --- | --- | --- | --- |
| P1 | Counting from the finish reproduces every recorded number | Holds | The 11-rule structure: 20/9 hidden on (x2,x3) against (y2,y3), 19/9 or 37/18 on the other eight option pairs, the second observer's setting moves (s1,s2) by 1/3; smallest gain 61/30; 7-knot 19/9, 8-rule 20/9, pencil 9-knot 20/9; 18-knot 20/9 with 512 start states and 1,152 per finished structure; 10-rule structures 55/27 per history (109/54 for the pairs with c); 8/3 not hidden (change 1/6); keyed settings 2/9 between two keyings (pooled); 128 of 512 sign assignments at 20/9; all 894 grown records (680 of the rule-Q line, 214 of rule R). Recounted by the checker: all of it the 214 rule-R records were recounted by the checker too, each reproduced from the finish. Every record equals the score over all two-valued functions, so the verdict does not rest on reading 16 (below). |
| P2 | Every structure meeting h0–h4 scores at most 2 (exactly 2 over all two-valued functions), both records hidden; the unmeasured structures meet them | Holds | 1,816 verdicts, all "hypotheses met, exactly 2, hidden"; the 512 sign assignments all exactly 2, hidden, from the start. The checker recounted the scores (exactly 2, hidden, on every one it recomputed); the hypothesis checks are the engine's. |
| P3 | Each example E1–E7 scores above 2 or changes a record | Holds | E1 20/9 hidden; E2 104/45 hidden; E3 7/3, second record changed by 1/6; E4 17/6, both by 1/3; E5 11/4, first by 1/4; E6 5/2, first by 1/4; E7 5/2, first by 1/4. Recounted: identical. |
| P4 | Every construction order in which both setting knots bring only their own fresh distinction scores 2, hidden | Holds | 104 of the registered 400, 92 of the new 400, 133 of the smallest gain's 400: all at 2, hidden. Recounted on all 1,200: identical. |
| P6a | Under Q-OLDEST or Q-NEWEST some renumbered start grows a different finished structure | Holds | Smallest gain's part: 34 of 48 renumberings differ under each; seven of the ten five-knot census starts: 45 to 58 of their 52 to 64 renumberings differ; the other three (entries 59, 125 and 146 of census_index.json, which make no birth in three rounds) none. From the raw output: renumberings of census starts 30, 82, 112 and 120 grow different numbers of knots (39 against 25 for start 30). |
| P6b | Where the finished structures are the same, counting from the start gives the same weighting carried back | Holds | 0 weightings differ; 356 compared by enumeration, 110 by the renaming of the whole history (not compared numerically). From the raw output only. |
| P7 | The 10-rule structures' 55/27 becomes 2 counted from the start, per history and pooled | Holds | Per history 55/27 from the finish, 2 hidden from the start; pooled 2 from the start. Pooled from the finish the score is also 2 (each history and state once, and with ν uniform). Recounted on the run's grown structures: identical. |
| P8 | The 11-rule structure's two four-place rules fail K2 in all 512 sign assignments; the 128 at 20/9 are those whose ties are inequalities | Holds | Both fail K2 in the start and every finished structure of all 512, and no other rule fails; the 128 hidden at 20/9 are exactly the 128 with x2 ≠ x3 and y2 ≠ y3. From the finish: 2 hidden ×256, 20/9 hidden ×128, 194/91 not hidden ×64, 23/10 not hidden ×64; from the start 2 hidden ×512. Recounted: identical. |
| P9 | The counting-from-the-start pair tables decide the next birth count on all 194 not-all-equal types | Holds, with nothing to decide | The 194 tables are distinct under renaming, so no two types share one. From the raw output only. |

The engine checks hold: brute force equals the engine (37 gates); the agreement rule of TD 7.3 on the 100 census starts
and six laws through 3 rounds: under parity no growth parted, under not-all-equal every growth with a birth parted by
round 3 except 2 under RING-LAW, 0 mismatches with direct counting, 0 undecided (raw output).

## The knot test in the whole

| Structure (structures.json) | Rules | Distinctions | Rules that fail in the whole (K2 each) | Method |
| --- | ---: | ---: | --- | --- |
| 11-rule start; + setting knots (00, 01, 10, 11) | 11; 13 | 16; 18 | even(x1,x2,x3,c), even(y1,y2,y3,t), each inducing {0011, 0101, 1010, 1100} | projection and canonical |
| 10-rule starts A and B | 10 | 16 | even(x1,x2,x3,c) | projection and canonical |
| smallest gain: part; + rule-Q round 1 | 7; 9 | 12; 14 | none | projection and canonical |
| smallest gain finished, a = 0 (b = 0, 1) | 11 | 16 | nae(x1,x2,za), inducing {010, 011, 100, 101} | projection and canonical |
| smallest gain finished, a = 1 | 11 | 16 | none | projection and canonical |
| 7-knot start; + setting knots | 7; 9 | 12; 14 | none | projection and canonical |
| 8-rule start; + setting knots | 8; 10 | 12; 14 | even(y1,y2,y3,s1) | projection and canonical |
| pencil 9-knot start; + setting knots | 9; 11 | 14; 16 | none | projection and canonical |
| 18-knot start; + setting knots | 18; 20 | 26; 28 | none | projection only |

No rule fails on its own, here or in any of the 3,255 distinct structures tested. The engine's projection and canonical
command agree on all 287 rules of these structures of at most 20 distinctions; the checker's own projection agrees on
every rule of all 3,255 structures, and its own canonical runs on 80 rules of the 33 (all 19 failing ones and 61
passing) agree.

The finding's four statements are confirmed as written. Beyond them, on the structures the run built:

- **Setting knots that take c or t.** In the 11-rule structure the first observer's setting knot nae(x1,c,za) and the
  second's nae(y1,t,zb) fail K2 wherever they occur (each induces {010,011,100,101}): x1 and c are always opposite
  there, as are y1 and t. So the record's 19/9 and 37/18 compare knots with rules that are not knots. In the 10-rule
  structures nae(x1,c,za) fails and nae(y1,t,zb) passes.
- **The 10-rule finished structures** (the 55/27 row, three rule-Q births made by the run): even(x1,x2,x3,c) fails K2
  in all 48; even(y1,y2,y3,t) passes.
- **The rule-Q study's census** (two-holder parts grown one round under rule Q, its 8 gaining parts with every
  round-1 choice and its 27 parts with laws handed out to the newborns): the first setting knot nae(x1,x2,za) fails K2
  at a = 0 in 8 of the 16 histories of the gaining parts and in 272 of the 664 histories with laws handed out; no other
  rule fails. In the other 400 histories every rule of the part, of the stage after the round and of all four finished
  structures passes in the whole, and the hidden scores from the finish are 109/54 (288), 55/27 (96), 61/30 (8) and
  31/15 (8). (Histories with laws handed out in which both newborns are not-all-equal repeat the gaining parts'
  histories, so the 61/30 and 31/15 counts hold each structure twice.)
- **A hidden 61/30 on knots alone.** The census's parts 113 and 143 (its identifiers), under either round-1 choice,
  score 61/30 with both records hidden under counting from the finish, and 2, hidden, from the part and from after the
  round. Every rule of their finished structures passes in the whole: projection on all 16, the canonical command on
  all 176 rules (the checker's run). Part 113 is nae(x1,x2,s1), nae(x1,s2,Ah1), even(x2,x3,Ah2), odd(x3,Ah1,Ah2),
  even(y1,Bh1,Bh2), odd(s1,Bh1,Bh2), even(y1,y2,y3,s2) (12 distinctions); rule Q's round adds nae(y3,s2,f12) and
  nae(y2,y1,f13) (or, with the other choice, nae(y3,y1,f12) and nae(y2,s2,f13)); the setting knots are nae(x1, x2 or x3,
  za) and nae(y1, y2 or y3, zb); 11 rules and 16 distinctions in all, as many as the registered smallest gain. Part 143
  has the same first observer's side and, for the second, even(y1,y2,y3,s2), odd(y1,Bh1,Bh2,Bh3), even(s1,Bh1,Bh2,Bh3)
  (17 distinctions finished). The registered smallest gain is the census's part 104 renamed: its first observer's side,
  even(x1,h1,h2) with odd(x2,h1,h2), forces x1 ≠ x2, so its setting knot at a = 0 constrains nothing; part 113's side
  ties no two of x1, x2, x3. Parts 103 and 136 give 31/15 the same way. This bears on the later ticket the finding
  named ("the smallest gain among structures whose every rule is a knot in the whole"): among the census's 8 gaining
  parts, one whose every rule is a knot has the registered winner's size and its 61/30.
- **Rule R's parts** (the 214 grown records of the rule-R line, REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001): in 33 of the
  214 histories, of two parts of that census, three rules fail K2 in the whole, in the part, after the round and in
  all four finished structures: even(Bh1,Bh2,Bh3,Bh4), odd(y3,s2,Bh1) and even(y2,s1,Bh1). In the other 181 every
  rule passes. Recounted by the checker's projection on all 214 (these structures have more than 20 distinctions, so
  not by the canonical command); every recorded score is reproduced from the finish, hidden, and every history scores
  exactly 2, hidden, from the part and from after the round.
- **The 8/3 case** (the review-leads census's unhidden 8/3, REVIEW-LEADS-20261123-001C): x2 and y2 are forced to 1, so
  even(x2,h1,h2,h3) and even(y2,k1,k2,k3) fail K2 in the start and every finished structure, and nae(x1,x2,za) at a = 0
  and nae(y1,y2,zb) at b = 0 fail too (each induces {010, 011, 110}).

The registered reversal reading "every structure of the line whose excess holds under counting from the finish has a
rule that fails in the whole" is tested and not met, now on the 7-knot, pencil 9-knot and 18-knot structures (the last
by projection only), on parts 113 and 143, and on 392 histories with laws handed out (projection; the canonical command
ran on all four finished structures of 98 of them).

## The lemma: hypotheses and examples

The hypotheses (TD 9), for the four setting pairs' histories and a common stage s before the first setting knot:
**h0** the stages up to s are the same in all four and the counting starts at or before s; **h1′** every place of a
setting knot but its fresh distinctions is held at s, and what it brings fresh is the same for both of that observer's
settings and held by no knot of the other's; **h2** every old state has a completion at the setting stage, or, when
weight is lost and renormalised, the lost-weight rule; **h3′** the two observers' fresh sets are disjoint and no later
knot holds fresh distinctions of both; **h4** no later stage loses weight except by the lost-weight rule, and each record
holds only distinctions held at s and its own setting's fresh ones. **Lost-weight rule**: whether a state is lost
depends on its part at s alone (checked as: the same old states keep all their weight under all four setting pairs).
Under these the score is at most 2 over any class of outcome functions and exactly 2 over all two-valued ones.

| Example | Built to break | Hypotheses the checks find failing | Score, changes (first / second record) | What it shows |
| --- | --- | --- | --- | --- |
| E0 | none | none | 2; 0 / 0 | the lemma's case |
| E1 | the premise (counting from the finish) | (no common start) | 20/9; 0 / 0 | the excess needs the finish |
| E2 | h1′, and h4's first clause | not computed (an order's knots between the two setting knots lie outside the lemma's form) | 104/45; 0 / 0 (weight kept 1/36 to 5/288) | an excess from nothing in a supplied order; which hypothesis it breaks is untested |
| E3 | h2 | h2 | 7/3; 0 / 1/6 | breaking h2 alone allows both |
| E4 | h3′ | h1′, h2, h3′ | 17/6; 1/3 / 1/3 | a shared fresh z breaks h1′ and h3′ together by their definitions |
| E5 | h4, first clause | h3′, h4 | 11/4; 1/4 / 0 | the later knot holds za and zb, so h3′ fails too |
| E6 | h4, record clause | h4 | 5/2; 1/4 / 0 | breaking the record clause alone allows a changed record |
| E7 | h4, record clause | h4 | 5/2; 1/4 / 0 | the same, with no weight lost |

So P3 holds for every example, but "one example per hypothesis" is met only for h2 and h4's record clause: no example
breaks h1′, h3′ or h4's first clause alone, and the examples do not show that h1′ or h3′ is needed on its own. Two other
candidates for h2, nae(x1, x2 or x3, h1 or h2) with nothing fresh, fail h2 and score 2, hidden (beside, not judged).
The order at list index 10 (the eleventh counting from 1) scores 2, hidden; E2 is the order at index 11, the one the
pre-registration's disclosed numbers give as 104/45.

Keyed settings (the first observer's setting a function g of its old values): from the start the second record changes
by 0 between any two g; from the finish, pooled, by 2/9 (both the 11-rule and 18-knot structures; 1/9 against a constant
g).

## Construction orders

Each order builds the structure knot by knot from nothing, each rule bringing as fresh the distinctions no earlier
rule holds, counted from the start renormalised. The orders are supplied, drawn by a seeded shuffle.

| List | Orders | In the class (both setting knots bring only their own fresh distinction) | In it: 2, hidden | Outside: 2, hidden | Outside: above 2, hidden | Outside: above 2, not hidden | Largest hidden outside |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 11-rule structure, registered | 400 | 104 | 104 | 182 | 66 | 48 | 104/45 (6 orders) |
| 11-rule structure, new | 400 | 92 | 92 | 182 | 75 | 51 | 104/45 (6 orders) |
| smallest gain | 400 | 133 | 133 | 126 | 14 | 127 | 55/27 (2 orders) |

Every order in the class loses weight equally across the four setting pairs, and all but one lose some (order 279 of
the smallest gain's list loses none). Some supplied orders put a
hidden score above 2 back under counting from the start, so counting from the start on a hand-built structure depends
on the start and birth record we supply.

## The table of the record's statements

Of the table's 44 rows, 15 were recomputed and 29 copied from the table (not recomputed). Changed (from the finish →
from the start, both hidden unless said): T01 20/9 → 2; T02 19/9 or 37/18 → 2; T03 (s1,s2) moved by 1/3 → 0; T04 128
of 512 above 2 → 0; T05 the 10-rule structures 55/27 per history → 2 (pooled 2 under both); T06 smallest gain 61/30 → 2;
T07 the other gaining parts and the parts with laws handed out 109/54, 61/30, 55/27, 31/15 → 2; T09 7-knot 19/9 → 2;
T10 8-rule 20/9 → 2; T11 pencil 9-knot 20/9 → 2; T13 18-knot 20/9 → 2; T15 a keyed setting moves the other record by
2/9 → 0; T17 the 8/3 case, not hidden → 2, hidden; T18 rule R's seven values (127/63, 5293/2646, 6175/3087, 109/54, 1135/567, 973/486, 11162/5535) → 2. Unchanged: T36 (the
pair tables decide the next birth count on 194 of 194 types). Newly filled where the table said "to compute": T05,
T07, T17, T18. The knot column: "all" for T09, T11 and T13 (the last by projection only); a failing rule for T01–T07,
T10, T15 (its 11-rule half), T17 and T18, in T07 for 280 of its 680 histories only.

## What this shows and does not show

- **No run decides between the countings.** Both are run on every structure; the excess above 2 appears only under
  counting from the finish, because the lemma's hypotheses hold (by the engine's checks) on every grown history from a
  stage before the setting knots. That is what the working choice produces. It is not evidence for the choice, which stays the thread's,
  reversible, and untested here (A240); nothing here is the owner's counting.
- **Supplied in every case**: the two countings and the family from a common stage; uniform weight on a start's states;
  equal division at a birth (its swap is the other counting); the hand-built structures taken as their own starts (the
  11-rule, 8-rule, 7-knot, pencil 9-knot and 18-knot structures, the 8/3 case); the 1,200 construction orders, drawn by
  a seeded shuffle; ν uniform over histories in pooled rows (swapped for each history and state once: the same verdicts);
  the settings, observers, records and outcome classes as each earlier study froze them, including the option pairs of
  the 10-rule structures (the record's own); the laws and the 100 census starts. Each verdict is about these as much as
  about the growth.
- **What the cut leaves unchecked by the canonical command**: 1,046 distinct finished structures of the histories with
  laws handed out (cut at 20 minutes; 128 of them hold a failing rule), the 1,075 structures over 20 distinctions (rule
  R's and the 18-knot's, by registration), 463 structures never registered for it (starts, stages after the round and
  the examples' structures) and part 3's 2,560 sign-assignment structures. Two independent projections agree on all of
  them.
- **The 61/30 on knots alone is a statement about two hand-chosen settings** on two parts of one census: it shows that
  a failing rule is not needed for the line's smallest excess, not that rule Q's growth makes excesses of knots under
  counting from the start (it does not: every grown history scores 2 there).
- **Not shown**: which counting is right; anything about the owner's picture beyond his answers; anything about physics.
  Everything is finite: 33 hand-built structures, 894 grown records of two earlier censuses, 1,200 orders, 11 starts
  grown three rounds, 194 types, 100 census starts.

## Deviations that matter

- **The parity score's absolute value** (reading 16): TD 4.4 has none, the records' scores have one; the reading was
  taken after a timing probe on one rule-R record showed it. No verdict rests on it: every recorded number equals the
  score over all two-valued functions.
- **The 10-rule structures' settings** (reading 17): TD 4.1's option y2 (or y3) is not eligible there; the pair used is
  the record's own 55/27 pair.
- **E2's index** (reading 25): the order at index 11, fixed by the disclosed numbers; index 10 would score 2, hidden.
- **Grow again** (readings 36 and 37, written after probes that bore on P6a, disclosed): structures compared by a key of
  each history, then a hash, then a 5 s search. P6a does not need them (different numbers of knots). 110 rows of P6b
  rest on the key, which identifies a made distinction only by its maker's key.
- **Code edited after the gates**: the engine's main modules were last changed 36 s after the gates were written, not
  named in the deviations (presumably reading 16's absolute form); the gates were not rerun. The checker's recount agrees
  with every number it recomputed.
- The deviations file is not under version control; the dates of its entries cannot be checked.
