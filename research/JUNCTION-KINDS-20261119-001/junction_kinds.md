# A transfer between kinds of junction

Epic `JUNCTION-KINDS-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead after `BREAK-EDDIES-20261119-001`'s
referee verdict (taking `JUNCTION-MAP-20261119-001#1`). Goal G17. **Refereed:** report [R1](referee-R1/report.md), confirmed, no Block, one wording point folded in on 19 November (see
Referee). Its reading of the matching was narrowed
the same day by `NATIVE-SPINE-20261119-001` (see Corrections).

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `aceb33e8c` at 12:54 UTC after a pilot (disclosed).
- The run went through the shared runner (`JUNCTION-KINDS-B1`, `runs/junction-kinds`, 30 cases), all ok by 12:58 UTC.
- Code: [kindlib.py, spinelib.py, job.py, merge.py](../../experiments/JUNCTION-KINDS-20261119-001B/JUNCTION-KINDS-20261119-001B-E001_kinds/),
  with the pilot in `pilot/`.
- Results: [results.json](../../artifacts/JUNCTION-KINDS-20261119-001B/JUNCTION-KINDS-20261119-001B-E001_kinds/results.json).

**Words.** As in the pre-registration.
- A junction born in round t with p parents is shared 1/p to each.
- The **out-share** s(j) of a junction is the sum of those shares over its children.
- An **exact transfer** on a partition of the junctions is one in which every junction of a class sends the same total share into
  each class.
- An ancestor **at depth k** is reached by k parent steps. The **spine relation** joins each junction of round t to its ancestors at
  depths 2 and 3.

## The answer

**In the owner's terms.**
- **There is no exact transfer between kinds of junction** (along parents, each junction shared 1/p among its p parents; the
  qualifier added after referee R1). The direction's second stop case holds: the kinds never settle.
  - **Out-shares.** A junction's out-share takes more and more values as the growth goes on. In the last rounds, one round's
    junctions hold 26 to 185 distinct out-shares in the ten starts and 19 to 28 in the catalogue's eddies. In the first rounds they
    held 2 to 8 (J1, all 30 starts).
  - **Why that settles it.** In an exact transfer, every junction of one class has the same out-share, so finitely many classes
    give finitely many out-shares.
  - **The coarsest exact transfer.** Its classes per round also grow: 23 to 388 in the ten, 25 to 29 in the catalogue's (J2).
  - **The catalogue too.** This holds in the catalogue's eddies as well, where the cluster rule's cover gives an exact finite
    transfer. So the finite object behind a rational count is not a kind of junction. A junction is a growing cluster, and its
    parents count the points it can lose, which grow with it.
- **Ancestry is compatible with the count, no more (corrected the same day, a Narrowing).** In the ten starts c(t) = c(t − 2) +
  c(t − 3) from round 4, 5 or 6 on. The first version said "ancestry can carry the count", reading the matching below as the
  substitution's structure. But a degree-preserving shuffle of the relation has a perfect matching too (30 of 30,
  `NATIVE-SPINE-20261119-001`), and no pair is forced. So the matching shows only that the counts fit the ancestry's density.
  - **The matching.** At every round where it holds, each junction can be paired with a different ancestor two or three rounds
    back, using every junction of those two rounds exactly once: a perfect matching, 10 of 10, 21 to 23 rounds each.
  - **The tree it makes.** Every junction then has one partner two rounds later and one three rounds later, and every junction
    has one partner before it, as in the substitution a → b, b → c, c → ab, which counts c(t) = c(t − 2) + c(t − 3). Since a
    shuffled relation pairs off as well, this tree is one of very many and says little about the growth.
  - **The catalogue's eddies,** whose counts carry a constant part, match their own lags in the same way, saturating the smaller
    side at every round (5 of 5).
- **No local rule found picks that tree.** No set of up to three of the ten most frequent interval types makes the relation
  biregular, in any of the ten, even on the first half of the rounds (J4). An interval type is the shape of the parent chains
  between a junction and its ancestor.
  - The ancestors reached by one chain alone fall short too, matching 92 to 97% of a round in the last round.
- **What it means for the eddies.** A self-feeding loop of the break shapes is not a finite set of junction kinds. Its count
  fits its ancestry, but no rule tried picks a spine there, and none is forced (`NATIVE-SPINE-20261119-001`).

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| J1 | out-shares rise across the window's thirds in all 30 | **held** | 30 of 30 |
| J2 | sum-equitable kinds rise across the thirds in all 30 | **held** | 30 of 30 |
| J3 | T: perfect spine matching at every round from 4, with the recurrence holding; C: a matching saturating the smaller side | failed as scored | the matching is perfect at every round where the recurrence holds (10 of 10) and saturating in C (5 of 5); but in 4 of the ten the recurrence starts at round 5 or 6, not 4 |
| J4 | (risky) no native spine of interval types in T | **held** | 0 of 10 have a biregular set, even on the first half |
| J5 | T: d = 0 from round 4; Q: d nonzero and d(t) = −d(t − 2) − d(t − 3) from round 9 | failed as scored | T: d = 0 from round 4 in 6, from 5 or 6 in 4; Q: 14 of 15 hold from round 6 to 8; Q-045's counts carry a constant part (a factor x − 1, order 7), and its d's first differences satisfy the recurrence |

3 of 5 held as scored. Both failures are start rounds I fixed from one pilot start. A transient of one or two more rounds, and the
constant part that the divisibility test sets aside (the factor x − 1), moved them. Read from each start's own first recurrent
round, both hold (post hoc).

## Why it holds

- **No finite exact transfer (proved, short).** Let a partition's classes send shares M[k, l]. Then a junction of class l has
  out-share Σ_k M[k, l], the same for the whole class. So the out-shares take at most as many values as there are classes. J1
  measures the out-shares rising in every start.
- **Why out-shares grow.** A child with p parents gives each 1/p. In the cover's picture a junction is a cluster of points, its
  parents are the cluster with one removable point taken out, and its children add one point. As clusters grow, the numbers of
  their removable points and of their extensions grow, and so does the set of share sums. This is argued, not proved.
- **A finite transfer on average still exists.** Class totals can follow a fixed matrix without every junction doing so. The
  substitution a → b, b → c, c → ab has characteristic polynomial x³ − x − 1 and counts c(t) = c(t − 2) + c(t − 3). A perfect
  matching per round fits it into the ancestry, though a degree-preserving shuffle pairs off as well (corrected). A
  label like "rounds since the last whole turn" is not local, so a local partition cannot carry it, as the advisor said.

## Known results, and what this adds

- **Known, cited once.** Equitable partitions and their quotient matrices; substitutions and their matrices (the Padovan
  substitution); Hall's marriage theorem and Hopcroft–Karp matching.
- **What this adds.**
  - For the cheapest growth, a junction's kind, however refined, cannot carry an exact finite transfer, in the break-shape eddies
    and in the catalogue's alike.
  - The count of a break-shape eddy is compatible with its own ancestry: each round has a perfect matching with the two rounds
    its recurrence names. A degree-preserving shuffle has one too, so this is weak evidence (corrected).
  - No local interval type up to the size searched chooses that matching.

## Limitations

- 26 rounds (8,820 to 12,500 junctions in the last round) for the ten, 40 for the catalogue's. "Rises across the thirds" is
  evidence of unbounded growth, not a proof of it.
- The matching is found by Hopcroft–Karp, not by a native rule. J4 searched sets of up to 3 of the 10 most frequent interval
  types of the unfolded chain structure, a small family of local rules.
- The share 1/p is one convention. Any convention that splits a child's count among its parents gives an exact-transfer argument of
  the same form, but its out-shares were not measured.
- The y⁴(1 + y)² starts were used only as a count control; their own spine, at lags 4, 5 (twice) and 6, was not tested.

## Corrections

- **2026-11-19, Narrowing (overreading), found by `NATIVE-SPINE-20261119-001`.** "Ancestry carries the count … the substitution made
  of real parent chains" read the existence of a perfect matching as structure. A degree-preserving shuffle of the relation has one
  too (30 of 30), and no pair is forced. Logged in `docs/CORRECTIONS.md`. J3's verdict and every count stand.

## Referee

Report [R1](referee-R1/report.md), 19 November 2026, by the coordinator's background referee thread, with its own growth and an
independent matcher. No study code was run.
- **Confirmed.** All 30 starts reproduce; every recurrent round of the ten has a perfect matching by an independent matcher; J4 holds
  over every subset of interval types, not only up to three of the ten most frequent. The narrowing by `NATIVE-SPINE-20261119-001`
  is supported.
- **Folded in the same day (not a block)**, logged in `docs/CORRECTIONS.md`: the headline now carries its qualifier, an exact
  transfer along parents with 1/p shares, which the Limitations already stated.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2), before the freeze. Its answer stayed within its text.
- **What it gave, and held.** The out-share argument, which corrected my first reading: unbounded degree alone is not an
  obstruction. The cheapest discriminator, J1. The coarsest exact transfer, J2. The Padovan substitution as a finite transfer on
  average (checked: x³ − x − 1). The Hall test, J3, which holds where the recurrence does. The typed spine, J4, which found none.
  The Q control's d recurrence (checked: x⁶ − (x + 1)² = (x³ − x − 1)(x³ + x + 1)).
- **Where it was unsure, and what came of it.** It doubted that the break shapes' ancestry would have peelable turns at all.
  The matching exists, but no local type found picks it.
- **What I did not take.** Its catalogue spine with each eddy's own exponents as a biregular test, since those counts carry a
  constant part.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: a transfer between kinds of junction | **Status:** Partially successful (3 of 5 held as scored; the 2 misses are start rounds and hold post hoc; the stop rule's second case) | Out-shares and the coarsest exact transfer grow without settling in all 30 starts, the catalogue's included; ancestry carries c(t) = c(t − 2) + c(t − 3) as a perfect matching at every recurrent round; no local interval type picks it |
| Local direction: a finite object behind the break-shape eddies | Narrowed | Not a kind of junction; the ancestry is compatible with the count, but no spine is found or forced (corrected) |
| Broader exploration: what the cheapest growth builds | Known alternatives | Steady eddies are substitutions realised by parent chains; explosive starts remain unread |
| Long-term goal: G17 | Obstruction learned | Local kinds cannot carry the rare eddies' counts; their ancestry is only compatible with them (corrected) |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A native spine: a rule read from the growth that picks each junction's partner two or three rounds back, or a proof that no rule of bounded radius can (two junctions alike to radius r that must be paired differently) | 3/3 — the self-feeding loop as a substitution the growth itself carries | 2/3 — the matchings exist and the ten starts are grown | try the rules "newest ancestor by birth order", "most chains" and "fewest chains" on the ten → stop at a rule that is a perfect matching on every round, or at an indistinguishable pair | Selected · awaiting go-ahead |
| 2 | The y⁴(1 + y)² starts' spine: is c(t) = c(t − 4) + 2c(t − 5) + c(t − 6) carried by ancestry with two partners at lag 5, the (1 + y)² read as two ancestors? | 2/3 — whether W's factors are visible in the ancestry | 3/3 — the same code with multiplicities | Hall with multiplicity on the 15 → stop at the matchings, or a round where none exists | Alternative · proposed |
| 3 | The explosive kind (`BREAK-EDDIES-20261119-001#2`), with part U's 624 starts still rising at the memory limit | 2/3 | 2/3 | as there | Alternative · deferred |

## Final report as sent (2026-11-19 13:10 UTC)

**Correction first (Block, now folded in):** STATES-GROWTH's "the allowed states fix the knots on 93% of small not-all-equal stages" was wrong. Counting the states' minimal constraints of every size, the figure is 79.8%. My search had stopped one place above the largest knot, a bound read from the knots themselves, so it wasn't a states-only reading. The simplest counterexample, which I rechecked by brute force, is one knot after one round. It already holds a constraint that is not a knot. The parity half (Whitney's theorem) was confirmed, and MANY-VALUED's refined rule is the states-only growth that survives. Details are under Corrections below.

**Outcome of the transfer study:** No finite set of junction kinds can carry the count, but the growth's own ancestry can. 3 of 5 frozen predictions held as scored. The two misses are start rounds I fixed from one pilot start, and both hold read from each start's own first recurrent round. Closed, referee pending.

- **Kinds never settle.** Each junction passes a share of each child back to it. The total it receives, its out-share, takes more values every round: from 2–8 distinct values early to 19–185 late, in all 30 starts. In an exact transfer every junction of one kind has the same out-share, so no finite set of kinds works. The catalogue's eddies behave the same way, even though there the cover gives an exact finite transfer. A junction is a growing cluster.
- **Ancestry carries the count.** In the ten plastic-number eddies, c(t) = c(t − 2) + c(t − 3). At every round where that holds, each junction can be paired one to one with an ancestor two or three rounds back (10 of 10, 21 to 23 rounds each). So every junction gets one partner two rounds on and one three rounds on. That is the substitution a → b, b → c, c → ab, built from real parent chains.
- **No local rule found picks those pairs.** No set of up to three common chain shapes picks the partners consistently in any of the ten. Whether some native rule does is the next question.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: a transfer between kinds of junction | **Status:** Partially successful (3 of 5 held as scored; the 2 misses are start rounds; the stop rule's second case) | Out-shares and the coarsest exact transfer grow in all 30 starts; ancestry carries the recurrence as a perfect matching; no local chain type picks it |
| Local direction: a finite object behind the break-shape eddies | Narrowed | Not a kind of junction; a substitution in the ancestry, with no native rule found |
| Broader exploration: what the cheapest growth builds | Known alternatives | Steady eddies are substitutions carried by parent chains; explosive starts remain unread |
| Long-term goal: G17 | Obstruction learned | Local kinds can't carry the eddies' counts; their ancestry can |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A native spine: a rule read from the growth that picks each junction's partner, or a proof that no bounded-radius rule can | 3/3 | 2/3 | try "newest ancestor", "most chains", "fewest chains" on the ten → stop at a rule that matches every round, or two look-alike junctions that must be paired differently | Selected · awaiting go-ahead |
| 2 | The y⁴(1 + y)² starts' spine: is the (1 + y)² two ancestors at lag 5? | 2/3 | 3/3 | Hall's test with multiplicity on the 15 → stop at the matchings or a round with none | Alternative |
| 3 | The explosive kind, with part U's 624 still-rising starts | 2/3 | 2/3 | as in BREAK-EDDIES | Alternative · deferred |

**Corrections** (from referee verdicts folded since my last report; all logged in docs/CORRECTIONS.md and knotlab's HISTORY.md, commit 05a0fffef):
- **STATES-GROWTH, Block:** the 93% reading, as above. **Not blocks:**
  - "Saturated stages never collide" is now "no two saturated stages collide".
  - C1 is true by construction.
  - A108's reach line now reads 79.8%.
- **MANY-VALUED, not a block:** confirmed, and stronger than stated: uniqueness holds at all 1,031 points tested and 1,805 of 1,806 trajectories, counting constraints of every size. "Exactly one presentation" now carries its pool.
- **DROPPED-JUNCTION, Narrowing:** the sample figures were grown with a shortcut implied-parity test. It differs from the cheapest growth on 19 of the 360 re-chosen presentations the referee checked, none of them original or on an eddy. **Not blocks:** the 70 choices that leave a junction under three places are now named, and "growing" starts is reworded.
- **JUNCTION-MAP:** confirmed with nothing to fold, and marked refereed.

This study made no new corrections.

**Goals:** G17 checkpoint (obstruction learned). **Assumptions:** A108 history line (reach corrected; status Confirmed). **Basket:** `JUNCTION-MAP-20261119-001#1` taken, with its three duplicates. The basket's top open item is `ROUND-FREE-20261119-001#1` (3/3, 3/3). **Advisor:** Fable 5.2, before the freeze, staying within its text. It corrected my first reading, that unbounded degree alone rules out a transfer, and gave the out-share argument, the Hall test and the typed-spine test, all of which I adopted. It doubted the ancestry would carry the recurrence, and the matching shows it does.

**Referee hand-off.** The decision note is `research/JUNCTION-KINDS-20261119-001/junction_kinds.md`; the prior-work line is in the pre-registration (objects-gate passes). Please check:
- `spinelib.out_shares` and `sum_kinds`;
- one round's perfect matching with an independent matcher;
- the biregular search behind J4.
