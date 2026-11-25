# Independent check of the confirming run

Filed by the thread, 25 November 2026. The check was made by a helper that did not write the run's code; its report
follows as it wrote it, with three places it had left to fill completed by the thread from its finished output
(marked). Its scripts are beside this file, with the two absolute paths they used replaced by the words REPO_ROOT (this
repository) and CHECK_SCRATCH (the checker's working folder, not filed): set both to run them. Paths the report names
without a folder are these scripts or outputs in that working folder. Evidence class: a check of a computed result; referee pending.

---

# Check of TWO-COUNTINGS-20261125-001A (two countings of a structure's allowed states)

Checker: an independent helper; nothing written in the repository. Scripts and outputs are in this folder. "Mine" means
recomputed by the checker's own code (`mykt.py`, `mykt_np.py` for the knot test by projection; `myscore.py` for the
countings, the score over all two-valued functions and hiding; `mycanon.py` for the canonical command, with the
checker's own clause writer). The engine's code (`tc.py`, `knottest.py`, ...) was read only to learn data formats.
"Raw" means read from the run's raw JSON, not recomputed. "Implementer" means taken from the report or summary.md.

## 1. The knot test by my own means

My projection (`mykt.py`): every allowed state of the whole structure enumerated by an incremental join of the rules,
the induced relation of each rule read off, K1, K2, K3 tested in the forgetting reading (K2: forgetting any one place
leaves every assignment of the others). On all 33 structures of structures.json (0.2 s):

| Structure (structures.json) | Rules | Distinctions | Allowed states | Fail in the whole (mine) |
| --- | ---: | ---: | ---: | --- |
| eleven (start) | 11 | 16 | 64 | even(x1,x2,x3,c), even(y1,y2,y3,t): K2, each inducing {0011,0101,1010,1100} |
| eleven + settings 00, 01, 10, 11 | 13 | 18 | 144 each | the same two, K2 |
| ten A, ten B (start) | 10 | 16 | 128 | even(x1,x2,x3,c): K2 |
| smallest gain: part; + round 1 | 7; 9 | 12; 14 | 64; 160 | none |
| smallest gain finished 00, 01 | 11 | 16 | 576, 480 | nae(x1,x2,za): K2, inducing {010,011,100,101} |
| smallest gain finished 10, 11 | 11 | 16 | 432, 360 | none |
| seven (start); + settings (4) | 7; 9 | 12; 14 | 64; 144 | none |
| eight (start); + settings (4) | 8; 10 | 12; 14 | 32; 72 | even(y1,y2,y3,s1): K2 |
| nine, the pencil; + settings (4) | 9; 11 | 14; 16 | 64; 144 | none |
| eighteen (start); + settings (4) | 18; 20 | 26; 28 | 512; 1152 | none (projection only) |

No rule fails on its own anywhere. Canonical command (my own CNF, `--witnesses` every other distinction), 80 rules of
structures of at most 18 distinctions: all 19 rules that fail by projection (every failing rule of the 33) and 61
passing rules (all other rules of eleven + settings 00, smallest gain finished 10 and 01, seven + settings 00, nine +
settings 11, eight + settings 00). All 80 verdicts and allowed tables equal my projection; at most 2.3 s per check.

The finding's four statements:
1. **Confirmed** (mine, projection and canonical): the two four-place parity rules fail K2 in the start and in all four
   finished structures, inducing {0011,0101,1010,1100}; the other 9 rules and both setting knots pass.
2. **Confirmed** (mine, both methods): nae(x1,x2,za) fails K2 at a = 0 (b = 0, 1), inducing {010,011,100,101};
   at a = 1 every rule passes; the part and the part after the round pass.
3. **Confirmed** (mine): the 8-knot structure's even(y1,y2,y3,s1) fails K2 (both methods); the 7-knot and pencil 9-knot
   structures pass every rule (both methods); the 18-knot structure passes (my projection only, 26 and 28 distinctions).
4. **Confirmed** for the 33 and for all 3,255 distinct structures part 8 tested: no rule fails on its own (mine). The
   citations hold: THIRD-HOLDER-20261123-001A's `common.py` lines 355–368 build each knot's relation from its own
   clauses with no witness; REVIEW-LEADS-20261123-001C's `result.md` line 71 says "Each knot passes the canonical test on
   its own"; a search of the three other studies' folders finds no knot-test call.

All 3,255 distinct structures of part 8 (`allkt_np.py`): my projection equals part 8's projection in allowed-state
counts, every induced relation and every K1/K2/K3/own verdict (0 differences); 931 failing verdicts in 531 structures,
as summary.md says. The 2,560 structures of part 3 (512 sign assignments, start and four finished): recomputed (see P8).

## 2. The implementer's new results

(a) **Setting knots that take c or t. Partly confirmed (mine).** On the 11-knot structure's option pairs,
nae(x1,c,za) fails K2 wherever the first observer's setting takes c and nae(y1,t,zb) wherever the second's takes t
(both induce {010,011,100,101}). On the two 10-knot structures only nae(x1,c,za) fails; **nae(y1,t,zb) passes in
every 10-knot finished structure** (raw part 8 output agrees with me). The report's "in the 11-knot and 10-knot pairs,
nae(x1,c,za) and nae(y1,t,zb) fail" is wrong for the 10-knot pairs; summary.md's T02 row (11-knot only) is right.

(b) **10-knot finished structures. Confirmed (mine on the run's 48 grown finished structures, 19 distinctions):**
even(x1,x2,x3,c) fails K2 in all 48; even(y1,y2,y3,t) passes; nae(x1,c,za) also fails in the 16 where it occurs. I did
not regrow the rule-Q births myself; the structures are the run's (`pm.py`).

(c) **The rule-Q study's histories. Confirmed (mine, recomputed from the archive `census_gains_c_*.jsonl.gz`).**
- Round-1 histories of the 8 gaining parts (16, both round-1 choices): nae(x1,x2,za) fails at a = 0 in **8 of 16**
  (parts 104, 105, 109, 139, both choices); no other rule fails; the part and the part after the round pass in all 16.
- Histories with laws handed out (664 of 27 parts): the same setting knot fails at a = 0 in **272 of 664**; no other
  rule fails. In the other **392**, every rule of the start, the stage after the round and all four finished
  structures passes (my projection), at 109/54 (288), 55/27 (96), 31/15 (4) and 61/30 (4) from the finish; all 664
  hidden from the finish; all 664 at exactly 2, hidden, from the part and from after the round (mine).
- **The exact statement:** in the rule-Q study's census, the parts numbered 113 and 143 (its part identifiers), under
  either round-1 choice, score **61/30, hidden, counted from the finish**, and **2, hidden, counted from the part and
  from after the round**; every rule of the part, of the part after the round and of all four finished structures
  passes K1–K3 in the whole. Checked by my projection on all 16 finished structures and by the canonical command on all
  176 rules of them (16 and 17 distinctions; all pass; tables equal my projection). Parts 103 and 136 give 31/15 the
  same way (projection on all 16 finished structures; canonical on the 8 of choice [0,1], 88 rules, all pass).
  The structures (part = 7 rules; then the two rule-Q births of round 1; then the two setting knots of TD 4.1):
  - part 113: nae(x1,x2,s1), nae(x1,s2,Ah1), even(x2,x3,Ah2), odd(x3,Ah1,Ah2), even(y1,Bh1,Bh2), odd(s1,Bh1,Bh2),
    even(y1,y2,y3,s2) [12 distinctions]; births nae(y3,s2,f12), nae(y2,y1,f13) (choice [0,1]) or nae(y3,y1,f12),
    nae(y2,s2,f13) (choice [1,0]); setting knots nae(x1, x2 or x3, za), nae(y1, y2 or y3, zb); 11 rules, 16
    distinctions; allowed states 432, 360, 432, 360 (choice [0,1]).
  - part 143: the same first observer's side; second side even(y1,y2,y3,s2), odd(y1,Bh1,Bh2,Bh3),
    even(s1,Bh1,Bh2,Bh3) [13 distinctions]; births nae(y3,s2,f13), nae(y2,y1,f14) or nae(y3,y1,f13), nae(y2,s2,f14);
    11 rules, 17 distinctions; allowed states 864, 720, 864, 720.
  - The registered smallest gain is the census's part 104 (and 109, the same rule list) with renamed holders; its
    first observer's side forces x1 ≠ x2, part 113's does not. Part 113 has as many rules and distinctions as the
    registered smallest gain. In 113 and 143 every rule is a knot in the whole, so the 61/30 there compares knots.
  - Not checked by me canonically: the 392 passing laws-handed-out histories (my projection only; part 8 ran the
    canonical command on all four finished structures of 98 of them, none of 293, and some of 1).

(d) **Rule R and the 8/3 case.** 8/3 case **confirmed (mine)**: even(x2,h1,h2,h3) and even(y2,k1,k2,k3) fail K2 in
all four finished structures and in the start (x2 and y2 are forced to 1, so each induces {1001,1010,1100,1111});
nae(x1,x2,za) fails at a = 0 and nae(y1,y2,zb) at b = 0 (each induces {010,011,110}). Rule R: **confirmed (mine, all 214 histories by projection)**: three rules fail K2 in the whole in 33 of 214 histories (even(Bh1,Bh2,Bh3,Bh4), odd(y3,s2,Bh1), even(y2,s1,Bh1); two parts of that census, 27 and 6 histories); every rule passes in the other 181. [Filled by the thread from the checker's finished output file, after the checker was cut off by a usage limit.]

## 3. Predictions

| # | Verdict | Basis |
| --- | --- | --- |
| P1 | Held, confirmed from raw output and largely by my recount | Mine: Known 1–3 (all nine option pairs, the smallest gain, 7-, 8-, pencil 9-knot), Known 4 (P8), Known 5 and the 18-knot keyed setting (2/9 pooled from the finish, 0 from the start, both structures), the 10-knot 55/27 and 109/54 per history, the 18-knot 20/9 hidden with 512 and 1,152 states, the 8/3 case (8/3, change 1/6), all 680 rule-Q records (0 differences from the recorded value). All 214 rule-R records reproduced from the finish (mine) [filled by the thread, as above]. Every one of the 894 records equals the all-functions score (raw P1 fields), so P1 does not rest on the absolute-value reading of the parity score (R 16). |
| P2 | Held for the scores (mine); the hypothesis checks taken from the implementer | Mine: exactly 2, hidden, from every common stage before the settings on all registered setting tests I recomputed (nine option pairs, smallest gain from stages 0 and 1, 7, 8, 9, 18, 10-knot per history and pooled, 8/3, 680 rule-Q records from both stages, the 512 sign assignments). All 214 rule-R histories exactly 2, hidden, from the part and from after the round (mine) [filled by the thread, as above]. That every structure meets h0, h1′, h2, h3′, h4 rests on the engine's checker (not recomputed). |
| P3 | Held, confirmed by my recount | E1 20/9; E2 (order at index 11) 104/45, hidden; E3 7/3, second record changed by 1/6; E4 17/6, both by 1/3; E5 11/4, first by 1/4; E6 5/2, 1/4; E7 5/2, 1/4. |
| P4 | Held, confirmed by my recount on all 1,200 orders | In the class: 104, 92, 133, all at 2 and hidden; outside: 182/66/48, 182/75/51, 126/14/127; largest hidden outside 104/45 (orders 11, 147, 343, 357, 389, 395; and 38, 54, 109, 281, 299, 386) and 55/27 (63, 205). Identical to the run. One class order (smallest gain's list, index 279) loses no weight (raw: 132 of 133 lose some). |
| P6a | Held, from raw output (not regrown) | Renumberings of census starts 30, 82, 112, 120 grow finished structures with different numbers of knots (e.g. 39 against 25), which settles "some differs" without the hash method. |
| P6b | Held, from raw output only | 0 differing weightings; 356 compared by enumeration; 110 "same by the renaming of the whole history" rest on R 36's key equality, not a numeric comparison. |
| P7 | Held, confirmed by my recount on the run's grown structures | 55/27 per history from the finish, 2 hidden from the start per history and pooled (ν uniform). Pooled from the finish is also 2 (TD 3.5 and ν uniform): the pooled half does not tell the countings apart. |
| P8 | Held, confirmed by my recount | Both four-place rules fail K2 in the start and every finished structure of all 512; no other rule fails; 128 at 20/9 hidden = the 128 with both ties inequalities; from the finish 2 hidden ×256, 20/9 hidden ×128, 194/91 not hidden ×64, 23/10 not hidden ×64; from the start 2 hidden ×512. |
| P9 | Held, from raw output only; vacuous | 194 distinct tables under renaming, so no two types share a table; the prediction cannot fail when no table is shared. Not recomputed. |

Nothing I found changes a registered verdict.

## 4. The lemma's verdicts

All 1,816 part-2 verdicts are "hypotheses met and at most 2 (exactly 2 over all two-valued functions), both records
hidden" (raw; the scores recomputed by me where listed under P2). Examples (P3): every one scores above 2 or changes a
record (mine). The hypotheses the checks find failing (raw): E3 h2; E4 h1′, h2, h3′ (TD 8.2 lists h3′); E5 h3′, h4
(TD lists h4); E6, E7 h4; E2 not computed (R 25: an order's knots between the two setting knots lie outside the lemma's
form, so no common stage before both exists). For E4 and E5 the extra failures follow from the frozen definitions
themselves (a z held by both setting knots breaks h1′'s third clause and h3′ together; a later knot holding za and zb
breaks h3′'s second clause), not from a reading. Consequence: P3 itself is about the score or a changed record and holds
for all seven. What the examples were for ("one example per hypothesis", PR "What a result would show") is met only
for h2 (E3) and h4's record clause (E6, E7): no example breaks h1′ alone, h3′ alone or h4's first clause alone, and
for E2 the break is untested. So the examples do not show that h1′ or h3′ is needed on its own.

## 5. Deviations flagged (of 42)

- **R 16 (parity score with an absolute value)**: chosen after a timing probe showed the record's 127/63 against the
  signed 29/18. It widened P1's criterion to "equals the all-functions score or the absolute parity score". It does not
  decide P1: all 894 records equal the all-functions score. TD 4.4 has no absolute value; the records' scores do.
- **R 17 (10-knot settings)**: TD 4.1's y2 option is not eligible on start A (nor y3 on B). The pair used, (x2,x3)
  against (y3,t) or (y2,t), is the record's own 55/27 pair (SETTING-AS-REREAD-20261123-001A `results_draft.md`
  line 81), so not a choice made toward P7.
- **R 25 (E2's index)**: "order 11" read as list index 11; index 10 scores 2, hidden, and would fail P3. Index 11 is
  the order Known 6 and 7 give as 104/45, so the disclosed numbers fix it. Written before part 4.
- **R 36/R 37 (part 7)**: written after probes whose results bore on P6a (disclosed). P6a does not need them (knot
  counts differ). R 36 calls the key comparison exact; it identifies a new distinction only by its maker's key, so equal
  key multisets are not a proof of the same history where two makers share a key. 110 P6b rows rest on it.
- **Undeclared code change**: `tc.py` and `lemma.py` were last modified at 01:41:59, 36 s after part 1's gates were
  written (01:41:23) and after the early knot test (01:39:24); the gates were not rerun. Presumably R 16's absolute form
  (a profile of the probe is dated 01:40:41). My recounts agree with every number I checked.
- **R 19**: T07's "20 of the 27" replaced by the pre-registration's "all 27": follows the frozen order of authority.
- deviations.md is not under version control and was last written at 02:43:22, after the report; the "written before
  the part" claims cannot be checked by date.

## 6. The cut

Part 8's canonical command: 671 of 3,255 distinct structures checked (7,406 rule verdicts, 171 of them copied from the
early run), all agreeing with projection. Not checked canonically: 1,046 cut (all finished structures of the
laws-handed-out histories of the rule-Q study, last in build order; 11,506 rule verdicts; 128 of these structures have
a failing rule); 1,075 over 20 distinctions (rule R's and the 18-knot structures, by registration); 463 never registered
for it (starts and after-round stages of the records, part 4's structures); part 3's 2,560 (projection only). My
projection agrees with part 8's on all of these. summary.md line 299 says "the canonical command on 7406 knots of this
run and 171 of the early run": the raw total is 7,406 including the 171 (7,235 new). Nothing else claims more than the
cut allows.

## 7. Words and claims in summary.md and README.md (they become public; not fixed)

summary.md:
- 7, 13, 14, 19, 20, 252, 256, 264, 266: "11-knot", "10-knot", "8-knot" structures, each holding rules that fail in the
  whole (the names count rules; "knot" only after the test).
- 299: "7406 knots" counts rules, failing ones among them, and overstates the total by 171 (section 6); 696 "knot
  verdicts".
- 258 (T07): knot column "fails: nae(x1,x2,za) (K2)" for all 680 histories; it fails in 280, and every rule passes in
  the other 400. Says more than the run shows.
- 261 (T10): knot column "[canonical: agrees / not run (more than 20 distinctions ...)]": report.py line 422 selects
  structures whose names start with "eight", which takes in the 18-knot ones. The 8-knot structures are all canonical.
- 198: "Every order in the class loses weight at some knot": 132 of 133 in the smallest gain's list (raw "losing weight
  at some knot": 132; order 279 loses none; my recount agrees); the sentence prints the count of "equally".
- 177: the "Weight kept per setting pair" column holds the weight lost for that row (61/64, 29/32; raw "weight lost").
- 161–163, 693–695: "ONE-PARENT-REREAD", "REREAD-BIRTHS rule R" without saying what they are; 293: "STATE-DISTANCE,
  LOOSE-NAMES, NEWEST-KNOTS" (copied from table.json) likewise; 17, 206–221: "census 30" and other start numbers
  without saying they are census_index.json entries; 25, 299 and the P rows: "R 16", "R 38", "part 2" etc. without
  saying what they are.
- 271 (T20): "CHSH" unmarked (the literature's name; first use).
- No "random", "typical", "rare", "likely"; no counting attributed to the owner; the working choice is not mentioned,
  so not presented as a result; no physics words beyond the disclaimer.
README.md: no problem found (it says "A rule is called a knot only once it has passed the knot test in the whole
structure").

## 8. What I could not check

The hypothesis checks h0–h4 (taken from the engine); P9 (not recomputed: needs the type archive's elimination); part 7's
growth and part 9's engine check (not rerun; read from raw); the rule-Q births of the 10-knot starts (I used the run's
grown structures); the canonical command on structures over 18 distinctions.
