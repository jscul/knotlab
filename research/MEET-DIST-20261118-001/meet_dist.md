# Is the knots' nesting a distance?

Epic `MEET-DIST-20261118-001`, 18 November 2026, by Claude, on the coordinator's go-ahead. It takes sub-goal B198
(`MEET-TWIST-20261118-001`'s selected direction). Goal G16; tests A97 directly. Refereed: report [R1](referee-R1/report.md), every number confirmed, one Block on a
reading, folded in on 18 November (see Referee).

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `5df037bcd` at about 04:23 UTC on 18 November. The
  run (long run MEET-DIST-B1, 315 cases on the shared runner) ended at 04:27 UTC, 315 of 315 ok.
- Code: [job.py, checks.py, merge.py and melib.py](../../experiments/MEET-DIST-20261118-001B/MEET-DIST-20261118-001B-E001_tables/).
- Results: [results.json](../../artifacts/MEET-DIST-20261118-001B/MEET-DIST-20261118-001B-E001_tables/results.json).

## The answer

- **One grown base's distances, read without the distinctions' names, carry part of the nesting; with the names, all of it at
  five** (computed, exact; *corrected after the referee*, see Referee: this headline first said the nesting becomes a distance
  "never all" and that "the rest is lost, not hidden", which is false). Every presentation of a line has the line's states, hence the same
  disagreement counts (the setting, `MEET-ORDERS-20261118-001` Lemma 0, not a finding). Under KF3 one grown base's table of
  disagreement counts, read up to renaming (without names), carries this share of the information about the bare bracketing
  (mutual information over entropy, prior uniform over labelled presentations):

  | Line of | k = 1 | k = 2 | k = 3 | k = 4 |
  | --- | --- | --- | --- | --- |
  | 5 | **0.63** | 0.60 | 0.39 | 0.22 |
  | 6 | 0.45 | **0.65** | 0.63 | 0.53 |
  | 7 | 0.37 | 0.57 | **0.62** | 0.58 |
  | 8 | 0.30 | 0.51 | 0.58 | |
  | 9 | 0.26 | 0.45 | 0.53 | |

  Unnamed, the share rises and, for five, six and seven, peaks (at k = 1, 2, 3) and falls; for eight and nine it is still rising
  at k = 3, the last computed. The peaks are about 0.6 to 0.7 depending on the prior (under a prior uniform over bare bracketings
  0.70 at five and 0.69 at six, the referee). **Named** (the line's distinctions known, and the new ones in the order they came),
  the same grown base carries all of it at five from k = 2 (1.0 at k = 2, 3, 4) and 0.83 and 0.91 at six (k = 2, 3), still rising;
  naming only the line's distinctions gives 0.70 and 0.71 at six (the referee's recomputation).
- **Unnamed, the growth reads less than revealing the knots directly.** Revealing the same number of knots directly, as fills chosen at random with no growth
  (the advisor's bag-of-knots null), carries the whole of it by k = n0 − 3 (1.0 at five from k = 2, at six from k = 3, at seven at
  k = 4). KF3's grown tables carry less than the null at every k ≥ 2 (D4). The growth reveals the knots it fills and, in the same
  steps, makes them confusable up to renaming: later fills are fills of re-bracketed triples. Named, they are not confused.
- **In law the nesting is fully readable from k = 1** (D1, D2): the law of the grown distances determines the nesting from the
  first new distinction; the shares above are one sample's. Different bare bracketings give different laws of grown tables from
  the first new distinction, and every two presentations that are not mirror images from the second. At k = 1 some presentations
  with one bare bracketing tie (1, 2, 17 and 41 pairs at six to nine), as the advisor predicted from mirrored self-mirror regions.
- **The labels matter.** The unlabelled multiset of the table's entries carries less than the full table from k = 2 (D5): from
  0.12 to 0.42 of the information, against 0.40 to 0.65 for the full table.
- **And the distance between grown distinctions is not the nesting** (by hand, before the run). Two fill points' disagreement
  count measures steps along the line between the distinctions their triples do not share, not how far apart the knots nest: 4
  for the end placement's knots (0,1,2) and (0,2,3), 6 for the middle placement's (0,1,2) and (0,2,4), though each pair shares a
  pair of distinctions.
- **Distance and states are the same here** (DISTANCE-ORDER's statement 3(a), checked): for these bases the table with the state
  count determines the allowed states, named or unnamed. So the share the unnamed table misses is carried by the names, which
  distinctions are the line's and in what order the new ones came: with them one grown base holds all of it at five and 0.91 at
  six. *Corrected after the referee (Block on this reading):* this bullet first said "the share not carried is not held in some
  other form; the growth does not keep it", which is false. The share measures what a reader loses by not knowing which
  distinction is which, not what the growth loses.

**In the owner's terms.**
- Every presentation of a line has the same distances, so before growth no distance can tell how the knots nest.
- After growth, one grown base's distances, read as plain numbers on unnamed distinctions, tell part of it, about half to two
  thirds. Knowing which distinction is which, above all the order in which the new ones came, tells all of it on the line of five.
  That order is history, not a distance.
- Read over many growths (the law), the distances tell the nesting completely from the first new distinction.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| G | 4 gate checks pass | held | table classes = state classes on five and six to n0 + 3 |
| D1 | In law, different bare bracketings differ from k = 1 (5 to 9) | held | no equal pair at any k ≥ 1 |
| D2 | In law, non-mirror presentations differ from k = 2 (5 to 9) | held | no equal pair at k ≥ 2; at k = 1, 1, 2, 17, 41 ties within one bare bracketing (six to nine) |
| D3 | The share is largest at k = 1 or 2 and smaller at the last k, every n0 | **failed** | holds for five and six; seven peaks at k = 3; eight and nine still rise at k = 3, the last computed |
| D4 | KF3 below the bag-of-knots null at every k ≥ 2 where it exists | held | every n0 and k |
| D5 | The unlabelled multiset below the full table from k = 2 | held | every n0 and k |

4 of 5 held. D3 failed by timing, not direction: the peak moves later as the line grows (about n0 − 4 new distinctions), and the
fall is seen for five, six and seven.

## What it means for A97 and the goals

- **A97** stays under challenge. *Corrected after the referee:* one grown base's unnamed distances carry about 0.4 to 0.7 of
  how the knots nest; the distances together with the distinctions' names carry all of it at five, and the names that matter most
  are the order of growth, which is history, not distance. In law the distances carry all of it from the first new distinction.
  Whether the order of growth can itself be read from the grown base without names (from its distances or from how its grown
  knots meet) is the open question.
- **G16:** capability gained. The information a grown base's distances carry about how the knots nest, measured exactly against a
  null and an ablation.

## Limitations

- Fewest-knot presentations, KF3, up to k = 4 (three for eight and nine); the long-growth fade is seen for five to seven only.
- One prior (uniform over labelled presentations of one labelling); shares, not naming chances, are the headline because chains
  dominate that prior.
- The disagreement count is the one distance read (A98's reading).

## Reproduce

```sh
cd experiments/MEET-DIST-20261118-001B/MEET-DIST-20261118-001B-E001_tables
../../../.venv/bin/python -B checks.py
cd ../../..
.venv/bin/python -B scripts/longrun.py launch experiments/MEET-DIST-20261118-001B/MEET-DIST-20261118-001B-E001_tables/job.py \
  --out <dir> --unit <name> --workers 12 --case-mem 1G
.venv/bin/python -B experiments/MEET-DIST-20261118-001B/MEET-DIST-20261118-001B-E001_tables/merge.py <dir>
```

## Advisor

Consulted once before the freeze. It reproduced the hand count at five, showed that the first D2 (from k = 1) was false at six,
judged the rising and threshold predictions unlikely, and argued that the design tested memory of the presentation rather than
nesting as a distance. Its sharper tests became the bag-of-knots null (D4), the multiset ablation (D5) and the literal test
settled by hand. Not consulted after the read-out.

## Referee

Report [R1](referee-R1/report.md), 18 November 2026, by a background referee thread with its own engine (a WL hash with VF2 for
table classes, every bracketing so no mirror bookkeeping): every share recomputes to four digits (five to k = 4, six to k = 3),
with the null, the multiset ablation and the in-law separation; the code (information share, prior, null fill points, multiset key,
canonical form) is right. Folded in the same day, each logged in `docs/CORRECTIONS.md` and knotlab's `HISTORY.md`:
1. **Block (on a reading; every number stands).** "The rest is lost, not hidden: the growth does not keep it" is false. Read with
   the distinctions' names kept, one grown base carries all of the information about the bare bracketing at five from k = 2 and
   0.83 and 0.91 at six (k = 2, 3); naming only the line's distinctions gives 0.70 and 0.71. The missing share sits in the names,
   mostly in the order of growth. Corrected in the headline, the bullets, the owner's terms, A97, the intuition entry and the goals
   row. No work depended on the false reading.
2. **Narrowing.** The share is one grown base, read without names, under the labelled prior; in law the tables carry all of it from
   k = 1.
3. **Narrowing.** "Then growth blurs it" holds for the unnamed reading and for five to seven only; named, the share rises; for
   eight and nine the unnamed share was still rising at k = 3, so "peaks near n0 − 4", "never all" and "at most two thirds" are not
   shown there.
4. **Not a block.** The peaks depend on the prior (0.70 and 0.69 under a prior uniform over bare bracketings).
5. **Not a block.** "No distance holds the nesting before growth" is the setting (all presentations have the line's states), not a
   finding; now presented as such.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: is the knots' nesting a distance | **Status:** Successful (refereed R1: numbers confirmed, one Block on a reading) | Exact: one grown base's unnamed distances carry about 0.4 to 0.7; named, all of it at five; in law all from k = 1; 4 of 5 held |
| Local direction: how knots meet as information under KF3 | Continue | The fade's long-run limit and which part of the table carries it are open |
| Broader exploration: A97 on other growths and readings | Searching | One rule, one distance reading |
| Long-term goal: G16 Learning the rules behind what a system allows | Capability gained | A measured transfer of knot information into distance |

**Next step:** Research directions — selected: #1 (regraded after the referee)

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Where the missing share lives: can the order of growth be read from one grown base without names, from its distances or from how its grown knots meet (the co-knotted pairs)? | 3/3 | 3/3 | Exact shares, unnamed, for the table with the grown pairs, and named variants, five to seven → stop when the unnamed reading reaches the named share, or at the part that stays outside | Selected · started (coordinator's go-ahead) |
| 2 | Long growth: the unnamed and named shares to k = 20, sampled | 2/3 | 3/3 | Sample six and seven → a rate or a floor | Alternative · deferred |
| 3 | Which block of the table carries the nesting | 2/3 | 3/3 | Shares per block, exact → the carrying block | Alternative · deferred |
| 4 | Prove the k = 1 value | 1/3 | 3/3 | Formula, checked 5 to 9 → proof | Alternative · deferred |

- **#1.** Payoff: after the Block, A97's question on this line is whether the order of growth, which carries the share the unnamed
  distances miss, is itself readable from the grown base (then the knots' meeting carries it, or the distances do) or genuinely
  outside. Concreteness: the exact runs exist; the grown pairs are tracked by the engine.
- **#2, #3, #4** as before.

**Corrections:** five from the referee (one Block on the reading "lost, not hidden", two Narrowings, two Not a block), all
logged; see Referee.

**Goals:** a G16 checkpoint (capability gained); no goal changed.

**Assumptions:** A97 under challenge, with this finding added; A100 gains this study among what rests on it; no new entry.

**Basket:** read; B198 taken by this epic.

## Final report as sent

Posted in the project thread at about 04:31 UTC on 18 November 2026 (the tables are those of the Position section above, with the
directions shortened):

> **Fourth study done (referee pending): the knots' nesting is a distance only in part, and only after growth.** Every
> presentation of a line has the same disagreement counts, so at the start no distance holds how the knots nest. Growth writes part
> of it in. One grown base's counts carry at most about two thirds of the information (0.63, 0.65, 0.62 for lines of five, six and
> seven), best after about n0 − 4 new distinctions, and then growth blurs it again. Revealing the knots directly carries all of it,
> and the unlabelled list of counts carries less. Here the counts determine the states, so the missing share is lost, not hidden in
> some other form. 4 of 5 predictions held; the one miss was timing: the peak comes later for longer lines.
>
> Corrections: none. Goals: G16 checkpoint. Assumptions: A97 under challenge, with this measurement added.
