# Can a growth rule read its own dimension from distances?

Epic `FRESH-COUNT-20261118-001`, 18 November 2026, by Claude, on the coordinator's go-ahead. Goals G2 and G1; tests A97; the parity
counterpart of A101. **Referee pending.**

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `38de2f3dd` at 18:58 UTC. The census ran from 19:01
  UTC through the shared runner (`FRESH-COUNT-B1`, `runs/fresh-count-2`, 3,982 cases on 7 workers, all ok, finished 19:56 UTC).
- Proofs: [proof.md](../../proofs/FRESH-COUNT-20261118-001A/FRESH-COUNT-20261118-001A-P001_free_count/proof.md).
- Code: [freelib.py, ideals.py, bonds.py, job.py, merge.py, checks.py](../../experiments/FRESH-COUNT-20261118-001B/FRESH-COUNT-20261118-001B-E001_free_count/).
- Results: [results.json](../../artifacts/FRESH-COUNT-20261118-001B/FRESH-COUNT-20261118-001B-E001_free_count/results.json).

## The answer

**In the owner's terms.**
- **No rule here reads its dimension from the distances unless its start or its own text supplies the number. The joining rule
  adds nothing of its own: every chain of junctions with one parent starts from a fresh distinction that no join of the next round
  asks for, and the dimension comes from those chains.**
- **What the growth is.** Growing by the cubic study's joining rule, whatever the counts, always builds the same kind of object: the
  pattern of all "down-closed" sets of the junctions that have one parent, ordered by descent (proved; the literature's distributive
  lattice of ideals, Birkhoff). So a count rule has exactly one freedom: where to start a new junction with one parent (an
  **offshoot**). Each fresh distinction a junction takes beyond what the next round's joins ask for (its **demand**) becomes an
  offshoot. The policy completes everything else.
- **One count for every join is forced to the first knot's size.** If every join must take the same number of fresh distinctions
  and the growth must never stall, there is exactly one choice: the number of distinctions in the first knot (proved). Any other
  count stalls within four rounds: at round 2 if it is two or more short, at round 4 if it is one short, at round 3 if it is more.
  With the right count the growth is the a-fold counting pattern (the literature's orthant ℕ^a) and balls grow as r^a (proved for
  every a ≥ 3). The smallest knot has three distinctions, so a growth from the smallest knot with one count is three-dimensional.
  The three is the first knot's three places, not a number the rule is given.
- **The stall at four is the cap's.** The cubic study's rule takes groups of at most three. With that cap, and one count, only
  three survives (proved): four and more stall at round 4, because four junctions that should join as one are taken as four
  groups of three. Without the cap every size survives. So the stall at four does single out three, but only because the rule was
  told three.
- **The fewest counts close the first knot and stop.** Taking as few fresh distinctions as the next round asks for, with every junction a
  knot and no allowed state lost, closes one knot on a distinctions into the 2^a pattern (the literature's a-cube: eight junctions
  of three distinctions each from the smallest knot) and stops; its last junction adds nothing new (proved). From any other start
  the fewest counts keep exactly the chains of offshoots they are handed, which can be any number (proved).
- **Typical counts.** Counts chosen blindly almost always stall (1,997 of 2,000 runs by round 10; the three survivors are at the smallest knot with counts of one or two). Counts that cover the demand and add a surplus
  distinction at random never stall, and either close early or grow offshoots without limit, so no dimension is
  typical (1,600 runs: from the 2^3 pattern closing at round 3 in 141 of 200 runs at the lowest rate, to more than 300 new offshoots a round at the highest).

| Count rule | What it builds from one knot on a distinctions | Evidence |
| --- | --- | --- |
| one count c for every join | runs forever exactly when c = a: the a-fold counting pattern, balls r^a; else a stall at round 2, 4 or 3 | proved (T2, T5); replayed P1 |
| the same, groups of at most three | runs forever exactly when c = a = 3 | proved (T3); replayed P2 |
| fewest (the demand, knot floor, states kept) | the 2^a pattern, then stops | proved (T4); replayed P3 |
| fewest, from any hand-over | keeps the chains it is handed with demand 1, any number | proved (T4); replayed P7 |
| the demand plus one at every offshoot; inherit a parent's count | the a-fold counting pattern | proved (T1, T2); replayed P3 |
| as many fresh as old taken | stalls | computed P3 |
| blind, uniform on 1..K | stalls (1,997 of 2,000 by round 10) | computed P5 |
| the demand plus a random surplus | never stalls; closes or grows without a fixed number | proved (T1) and computed P6 |

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| G | nine gate checks | held | 9 of 9 pass |
| P1 | one count, groups of any size: survives exactly at c = a; stalls at rounds 2 / 4 / 3 | held | all 40 cells, a = 3..7 (the product's counts every round when c = a) |
| P2 | one count, groups of at most three: survives exactly at c = a = 3; c = a ≥ 4 stalls at round 4 | held | all 40 cells |
| P3 | the menu from one knot, a = 3..6 | held | fewest: the 2^a pattern, every junction a distinctions, no forced distinction; axis and inherit: the product; balance stalls (round 5 at a = 3, round 2 at a ≥ 4) |
| P4 | the descent-order check on every run that did not stall | held | 1,829 runs, no ideal built twice, none missing, every parent a lower cover |
| P5 | blind counts: at most 10% not stalled by round 10 | held | at most 3 of 200 in any cell (a = 3, K = 2); 0 in the other nine |
| P6 | random surplus: no stall, no forced distinction, unclosed share rising with q, median last-round offshoots ≥ 3 for q ≥ 0.2 | held | no stall and no forced distinction in 1,600 runs; not closed by round 10: 35, 65, 122, 187 of 200 at a = 3 and 30, 94, 182, 200 at a = 4; median offshoots in the last round 3 and 85 (a = 3), 9 and 335.5 (a = 4) at q = 0.2 and 0.4 |
| P7 | fewest after a hand-over keeps the chains of demand 1; the crossed start keeps a chains | held | 196 hand-overs (4 ended before it), every one constant; crossed starts a = 3..6: a offshoots in every round after round a |
| P8 | the reader: exact on one count; on the 2^a pattern exact but one round early; misreads on mixed counts | held | 9 of 9 uniform stages exact; 2^3 and 2^4: exact except the round before the last (all loose distinctions read as one junction); mixed: 47 misreads among 247 stages |
| P9 | capped = uncapped exactly when no group has four or more members | held | 11,698 rounds, the two policies differing in 3,209, always exactly where an uncapped group had four or more members |

All ten held (the gates and P1 to P9). P1 to P4, P7 and P9 replay theorems; P5, P6 and P8 are the census's own.

## What the census found

**Blind counts** (uniform on 1..K, floored; 200 runs per cell; the round of the stall):

| Seed | K = 2 | K = 3 | K = 4 | K = 5 | K = 6 |
| --- | --- | --- | --- | --- | --- |
| three distinctions | 197 stall (rounds 4 to 10), 3 survive | all stall (99 at round 3) | all stall (144 at round 3) | all stall (162 at round 3) | all stall (179 at round 3) |
| four distinctions | all stall at round 2 | all stall (197 at round 2) | all stall (188 at round 2) | all stall (168 at round 2) | all stall (161 at round 2) |

Twelve blind runs at the three-distinction seed put fresh distinctions on a junction whose parity was already implied, making a
distinction with one value in every state; no other rule did.

**Random surplus** (the demand plus one surplus distinction with probability q; 200 runs per cell, ten rounds, at most 2,500
junctions):

| Seed | q | Closed | Not closed | Median offshoots in the last round | Closed as the plain 2^a pattern |
| --- | --- | --- | --- | --- | --- |
| three | 0.05 | 165 | 35 | 1 | 141 |
| three | 0.1 | 135 | 65 | 2 | 97 |
| three | 0.2 | 78 | 122 | 3 | 52 |
| three | 0.4 | 13 | 187 | 85 | 8 |
| four | 0.05 | 170 | 30 | 1 | 108 |
| four | 0.1 | 106 | 94 | 2 | 38 |
| four | 0.2 | 18 | 182 | 9 | 9 |
| four | 0.4 | 0 | 200 | 335.5 | 0 |

A run either closes early, most often as the plain 2^a pattern when no surplus came in the first rounds, or its offshoots multiply:
the number made per round grows with the round, so no fixed dimension appears.

**Hand-overs to the fewest counts** (1 to 4 random-surplus rounds, then fewest for up to 25 rounds; 200 runs, 4 ended first):

| Chains handed over (offshoots with demand 1) | 0 | 1 | 2 | 3 |
| --- | --- | --- | --- | --- |
| Runs | 149 (148 closed, 1 still a large finite pattern at the cap) | 29 | 15 | 3 |

In all 196 the number of offshoots per round stayed exactly the number handed over. The crossed starts kept a chains for a = 3 to 6
(junctions per round 3, 4, 6, 9, 13, 18, 24, 31, 39, 48, 58 at a = 3, rising like t²/2, so the junctions up to round t grow like t³).

## What the rule is given, and what it reads

The coordinator asked for this, since the content of `TWO-PROBE-ALIGNMENT-20261118-001` turned out to sit there.

- **Given offline.** The parity law; the joining rule (common-neighbour tests); one count rule; the reader of
  `BOND-NEXT-JOIN-20261117-001`. The crossed start, which reads the round number, is a designed start and not a rule.
- **Read at run time.** The bond-distance table of the current distinctions, nothing else.
- **Actions.** Each round, one new junction per group the policy names, with a chosen number of fresh distinctions.
- **What distances can and cannot do here.** With one count the table determines every junction (proved, T6), so the uniform rule
  is distance-only. The table cannot supply the count: by T2 the count must be the first knot's size, which the table shows (the first
  knot is the one bond of its size at the start), so the rule copies a number from its start. Under the fewest counts the table even
  closes the 2^a pattern one round early: before the last junction, the last loose distinctions already form a knot, and the reader reads
  it as that junction (proved, P8). With mixed counts the threshold reader misreads (P8); whether the full table still determines the
  junctions is the companion question `VARIABLE-OUTPUT-READER-20261118-001` (planned, not this study's).

## Why it holds

- **The policy is the literature's cube condition.** Junctions of one round that pairwise share a parent, with no parent shared by all, are joined
  by one new junction: exactly how the down-closed sets of an order are completed (lower covers pairwise meeting, none common to all,
  have a join). So the grown pattern is the ideals of the descent order, and a junction's demand is the number of minimal offshoots
  outside it (T1).
- **A uniform count forces the chains.** Every junction of the a-fold pattern has exactly a ways up; the seed's a distinctions are
  the a bottoms of the chains, and a uniform count must equal a at the seed's children, or the pairs of children (round 2), the
  pairs' surplus (round 3) or the triples (round 4) run short (T2).
- **The fewest counts add only what the knot floor forces.** A junction with one parent needs two fresh distinctions to be a knot
  of three; if the next round asks for only one, the second is surplus and starts a chain that never ends; nowhere else does the
  fewest rule add surplus (T4). From one knot every offshoot is asked for at least two, so nothing is added and the 2^a pattern
  closes.

## Known results, and what this adds

Known, cited once: Birkhoff's representation of distributive lattices (finitary form, Stanley, *Enumerative Combinatorics* I,
Prop. 3.4.3); configurations of conflict-free prime event structures (Nielsen, Plotkin and Winskel 1981), whose events are the
offshoots; the cube condition of median graphs (Barthélemy and Constantin 1993; Chepoi 2000); order dimension of a distributive
lattice is the width of its join-irreducibles (Dilworth 1950); connectedness of minimal cuts when short cycles generate the cycle space
(Babson and Benjamini 1999; Timár 2013); Tseitin's law; in the program, `LOGIC-AXIS-20261107-001A` (r^D on ℤ^D),
`CUBIC-FROM-A-KNOT-20261117-001` and `BOND-NEXT-JOIN-20261117-001`. What this adds: the program's parity growth law is Birkhoff's
construction, so a count rule chooses only an order; one count is forced to the first knot's size; the cap of three is where the
earlier three came from; the fewest counts close one knot into the 2^a pattern and conserve chains; the reader proof for every
uniform count.

## Limitations

- **One policy.** All results are for the cubic study's complete-round joining policy. A serial rule never stalls and admits trees
  (the cubic study's own remark); nothing here constrains it.
- **Volume.** Bond balls are proved r^a only for the a-fold counting pattern. For other orders the census counts junctions by round,
  the meeting pattern's growth, not bond balls; breadth bounds that growth by t^breadth but can exceed its exponent.
- **The reader** is proved only for one count (T6). Mixed counts are the companion question.
- **The census** is bounded: seeds of three to seven distinctions, ten or fewer rounds (25 after a hand-over), 2,500 to 6,000
  junctions.

## Words

Adopted with the advisor for this study and proposed for the glossary: **offshoot** (a junction with one parent; the literature's
join-irreducible), **demand** (the number of next-round joins that take a distinction from a junction), **surplus distinctions**
(fresh distinctions beyond the demand), **descent order** and its **breadth** (the literature's width). Breadth is not the dimension.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2), before the freeze. It confirmed T1 to T3 and the 2^a construction; refuted the first form of
T4 ("eventually at most two offshoots per round") with the crossed start, which the thread had also found, and gave the constancy
theorem that replaced it; showed the reader proof does not extend past one count; found that the floored fewest rule could make a
distinction with one value in every state at an implied two-parent junction (the frozen rule gives no floor there); corrected
"breadth w gives t^w" to an upper bound; and gave the literature and the words. Its pointer to a "section 9.6" of the public text
saying four fresh distinctions stall at the fourth round was not found. It saw no distance-only criterion that picks a number.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: can a distance-only growth rule settle its dimension when the fresh count is free? | **Status:** Successful (a proved no, with the reason) | The grown pattern is always the down-closed sets of the descent order, so a count rule only places offshoots; one count is forced to the first knot's size; the stall at four is the cap of three; the fewest counts close one knot into the 2^a pattern; blind counts stall, random surplus fixes no dimension |
| Local direction: parity growth by the complete-round joining rule with a free count | Practically exhausted for this question | The count has no freedom left that could pick a number; what remains is the joining rule (A104) and the start (A105) |
| Broader exploration: where a growth's dimension comes from | Known alternatives | Betweenness (the two-order line): a cap, a price, the start, or one free step; parity (here): the first knot's size, or a cap |
| Long-term goal: G2 Dimension three (and G1 Space from a law) | Capability gained; obstruction learned | Three needs no number written into the rule, only one count and a three-place first knot; but no rule here reads a number that its start does not hold |

The attempt leaves open why a growth should begin with the smallest knot (A105) and whether a rule that adds one junction at a time
(A104's alternative) behaves differently. The three-manifold half of G2 is untouched.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Serial growth read from distances: a rule that adds one junction at a time and prefers joins to new offshoots, from one knot | 2/3 — tests A104 | 2/3 — the serial moves and the reader exist | compare its descent order with the complete round's on seeds of three to five → stop at a proof that it builds the same orders, or a seed where it builds another | Selected · awaiting go-ahead |
| 2 | Why the smallest knot first: a law-level reason (a price, or a competition between first knots of different sizes in one base) | 3/3 — would make three the law's own | 1/3 — no discriminator yet beyond Corollary 2.1 | state a competition of a three-place and a four-place first knot under one count → stop at a reason or a proof that nothing prefers either | Alternative · deferred |
| 3 | Bond balls on descent orders whose chains are tied (the ladder example) | 1/3 — closes the volume gap of the census | 3/3 — the finite constraint lemma applies | prove or refute "the ball exponent is the number of chains that are eventually untied" → stop at either | Alternative · deferred |
| 4 | A short note: the program's parity growth law is Birkhoff's construction | 1/3 — conversion | 3/3 | write T1 and T2 as a self-contained note → stop when checked | Alternative · deferred |

- **#1.** Payoff 2/3: the complete round is the one assumption every result here rests on (A104), and a serial rule that never
  builds trees would say whether the round itself carries a number. Concreteness 2/3: the cubic study's serial moves and the reader
  are in place; the open part is a natural serial preference. Its connection to G2: if a serial rule builds the same descent orders,
  the first knot's size is the whole story. Bound: one epic, seeds of three to five, twenty rounds.
- **#2.** Payoff 3/3: a reason in the law for the three-place first knot would make "three" a consequence of the law rather than
  of the start, which is G2's question. Concreteness 1/3: the only argument so far is cheapness (Corollary 2.1), which is the knot's
  floor of three places restated. Filed as a sub-goal.
- **#3.** Payoff 1/3: the census measured junctions by round, not bond balls, off the product. Concreteness 3/3.
- **#4.** Payoff 1/3, concreteness 3/3: conversion of an accepted result.
- The companion question whether the full table determines the junctions under mixed counts is
  `VARIABLE-OUTPUT-READER-20261118-001` (planned, in another scope), not a row here.

**Corrections:** none. Nothing published is contradicted: the cubic study's referee wrote that "the three is put in by the law";
this study adds that with one count the law has no other choice, given a three-place first knot.

**Goals:** G2 checkpoint (capability gained and obstruction learned: three from one count and a three-place first knot, no number
read from nothing); G1 checkpoint (the same, read for space from a law); no goal changed.

**Assumptions:** two new entries, A104 (parity growth is judged under the complete-round joining rule, scope) and A105 (a growth
starts from the smallest knot, working premise); A97 gains this study (status unchanged); A101 gains its parity counterpart
(status unchanged).

## Final report as sent (2026-11-18 19:58 UTC)

**Outcome:** No. Under the parity law, a growth rule that reads only bond distances cannot settle its own dimension; it can only copy the number from its start or its own text (proved, and replayed by a frozen census of 3,982 runs in which all ten predictions held). Closed, referee pending.

- **What the growth is.** Whatever the counts, the cubic study's joining rule builds one kind of object: the down-closed sets of the order in which its one-parent junctions descend (Birkhoff's construction). So a count rule decides only where to start new one-parent junctions.
- **One count is forced.** If every join takes the same number, it must equal the first knot's size, or the growth stalls by round 4. With it, balls grow as r to that power. A growth from the smallest knot, which has three places, is therefore three-dimensional: the three is the first knot's.
- **The stall at four** comes from the old rule's cap of three junctions per join. Without the cap, every size survives.
- **The fewest counts** close one knot into the 2^a pattern (eight junctions from a knot of three) and stop.
- **Typical counts:** blind counts stall (1,997 of 2,000 runs), and a random surplus never settles on a dimension.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: can a distance-only rule settle its dimension with the count free? | **Status:** Successful (a proved no, with the reason) | The pattern is the descent order's down-closed sets; one count is forced to the first knot's size; the cap of three made four stall; the fewest counts close the knot |
| Local direction: parity growth by the complete-round joining rule | Practically exhausted for this question | The count has no freedom left that could pick a number; what remains is the joining rule (A104) and the start (A105) |
| Broader exploration: where a growth's dimension comes from | Known alternatives | Betweenness: a cap, a price, the start or one free step; parity: the first knot's size or a cap |
| Long-term goal: G2 Dimension three (with G1) | Capability gained; obstruction learned | Three needs only one count and a three-place first knot, but no rule here reads a number its start does not hold |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Serial growth read from distances (one junction at a time, joins preferred) | 2/3 — tests A104 | 2/3 — moves and reader exist | compare its descent orders with the complete round's on seeds of three to five → stop at a proof they agree, or a seed where they differ | Selected · awaiting go-ahead |
| 2 | Why the smallest knot first: a reason in the law (a price, or competing first knots) | 3/3 — would make three the law's own | 1/3 — only cheapness so far | pose a three-place against a four-place first knot under one count → stop at a reason, or a proof nothing prefers either | Alternative · deferred (sub-goal) |
| 3 | Bond balls on descent orders with tied chains | 1/3 — closes the census's volume gap | 3/3 | prove or refute "exponent = chains eventually untied" → stop at either | Alternative · deferred |
| 4 | A short note: the parity growth law is Birkhoff's construction | 1/3 — conversion | 3/3 | write T1 and T2 self-contained → stop when checked | Alternative · deferred |

**Corrections:** none; the cubic study's referee wrote that the law puts the three in, and this adds that with one count it has no other choice. **Goals:** G2 checkpoint (capability gained), G1 checkpoint (obstruction learned); no goal changed. **Assumptions:** new A104 (the complete-round joining rule, scope) and A105 (a growth starts from the smallest knot, working premise); A97 and A101 gain this study, statuses unchanged. **Advisor:** Fable 5.2 before the freeze; it confirmed the main theorems, refuted my first guess that the fewest counts keep at most two chains (they keep whatever they are handed), and supplied the literature and the new words (offshoot, demand, surplus, descent order). **Overlap:** Codex's planned `VARIABLE-OUTPUT-READER-20261118-001` asks whether distances still identify the joins under mixed counts; I left that question to it.

Referee hand-off: the prior-work line is in the pre-registration (objects-gate passes). Decision note: `research/FRESH-COUNT-20261118-001/fresh_count.md`.
