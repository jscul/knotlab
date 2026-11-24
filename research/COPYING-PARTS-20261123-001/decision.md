# Parts that copy themselves: what stands

Epic `COPYING-PARTS-20261123-001` (direction 1 of `RING-IN-BALANCE-20261123-001`; goals G18 with G17), closed 2026-11-23.
One frozen study, computed, scientific referee pending. [Ticket A: result](../COPYING-PARTS-20261123-001A/results.md) ·
[pre-registration](../COPYING-PARTS-20261123-001A/preregistration.md) · [referee hand-off](referee_handoff.md) ·
[advisor review before the freeze](advisor/README.md) · [the thread's side checks](checks/)

## The answer

The owner asked whether the growth has structures that make other structures, like cells that reproduce. Under rules added by
hand it does, in the simplest form found so far.

1. **The copier.** Two knots that hold two usable loose distinctions each and can join through one knot. Under three rations
   that give a new knot just enough for three places, they join; the join receives one distinction where two will be asked of
   it, so it is short and its joins are cancelled; and each of the two offshoots releases two offshoots of its own. One part
   has become two of the same.
2. **How fast.** By what the short join then does. It retires: the copies double every two rounds. It makes an offshoot: one
   more copy a round later, and the count grows by the golden ratio a round (on the ring of five, five times the Fibonacci
   numbers). It waits: one more copy two rounds later, and the counts from one copier are the Pell numbers.
3. **Every knot is a knot on the small starts**, under parity (by argument and 57,171 verdicts) and under not-all-equal
   (19,113 verdicts). Under the ration that always gives a fresh distinction no knot fails in any of 3,344 starts of up to five
   knots; under the two rations that can give a join of three parents nothing, knots do fail, exactly in the rounds where that
   happens.
4. **It is common under these laws.** A part copies itself in 85 to 97 of every hundred starts of up to five knots, each start
   counted once, depending on the treatment.
5. **What it needs.** A join that receives less than it is asked, offshoots that receive more than they are asked, and a
   treatment that cancels the short join's groups. It needs neither waiting nor the release rule. With the ordinary count, a
   cap of two or three, or a fixed ration of two, nothing copies in this way; a fixed ration of three has a larger copier of
   five knots that copies itself every round, and a fixed ration of four has parts of seven and nine that turn into one another.
6. **What stops it.** The fillers rule stops everything within three rounds. Removing offshoots stops it at once.

Ten predictions and a gate were frozen. Nine predictions and the gate hold. One hand prediction holds for two treatments and
fails for the third: with knots holding instead of releasing, and the short join waiting, nothing copies and the growth jams.

## Scaffolds, and what survived their swaps

| Scaffold | Swapped for | Survived? |
| --- | --- | --- |
| The ration (A224) | FLOOR0, FLOOR1, ONE-FEWER give the same copier; the ordinary count, caps and a fixed two give none; a fixed three and four give other copiers | The two-knot copier is specific to a ration that gives a join one. |
| The treatment (A224) | retiring, offshoots, waiting | Yes: all three copy, at three different rates. |
| The release rule (A224) | holding | Yes with retiring and offshoots; no with waiting. |
| Offshoots | none | No. |
| The fillers | added | No: everything stops. |
| Parity | not-all-equal | Yes on the small starts. |
| The start | two small starts, the ring of five, 3,344 starts of up to five knots | Yes: common under that census's weighting. |
| The complete round (A104) | not swapped | By the earlier study's argument the copies act alone, so rounds part by part would give the same; not run here. |

This is a result about rations and treatments added by hand, not about ordinary growth, under which a join receives what it is
asked and no part comes apart.

## What it does not show

The copies never meet again, so they cannot combine or read one another: the laws rule it out. Nothing reads the count of
copies; the one who runs the growth counts them. No claim is made about living things.

## Limits

Finite and computed: three named starts to 20,000 knots, 3,344 starts for ten rounds. The recurrences for every round are an
argument, written out for the referee. The census counts are lower bounds. One engine; the thread's side checks use the
pilot's program, which has no distinctions in it, and agree on every count compared.

## Final report as sent (2026-11-24 07:11 UTC)

The study of the parts that copy themselves is closed, referee pending, and the next one has started. The copier is real, small and common under these laws: two knots become two pairs of knots every two rounds, and every knot made passes the knot test.

**What stands** (computed on real knots with the earlier study's engine; 9 of 10 predictions hold and one holds in part; my side checks with the pilot's program agree on every count compared):

- **The copier.** Two knots that each hold two usable loose distinctions and can join through one knot. They join; their join receives one distinction where two will be asked of it, so it cannot pay and its joins are cancelled; each of their two offshoots then makes two offshoots of its own. One part has become two of the same.
- **Three rates, set by what the short join does.** If it gives up, the copies double every two rounds. If it makes an offshoot, one more copy follows a round later and the count grows by the golden ratio a round; on the ring of five the counts are five times the Fibonacci numbers. If it waits, the counts from one copier are the Pell numbers: 1, 2, 5, 12, 29, 70, 169.
- **Every knot is a knot.** On the small starts all 57,171 parity checks and 19,113 not-all-equal checks pass. Under the simplest ration, where a new knot gets enough for three places and never nothing, no knot fails in any of 3,344 starts of up to five knots.
- **It is common under these laws.** A part copies itself in 85 to 97 of every hundred of those starts, each counted once, depending on what the short join does.
- **What it needs and what stops it.** It needs a join that receives less than it is asked, with offshoots that receive more than they are asked. It needs neither waiting nor the release rule. Under the ordinary count, a cap of two or three, or a fixed ration of two, nothing copies. A fixed ration of three has a different copier, five knots that copy themselves every round. The fillers rule stops everything within three rounds.
- **What it is not.** The copies never meet again, so nothing combines and nothing reads: it is a population with a fixed rule of descent, not a machine. And none of it is ordinary growth.
- **The one failure.** The advisor's hand prediction for knots that hold instead of releasing held for two treatments and failed for the third: with waiting, nothing copies and the growth jams.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the frozen study of the parts that copy themselves | **Status:** Successful | The gate and nine predictions hold; the tenth fails for one of three treatments; three counting rules confirmed to 20,000 knots and by a second program. |
| Local direction — rations and treatments added by hand | Continue | The simplest ration gives knots that always pass the knot test and reads nothing of the round to come, which makes it the natural law for the next question. |
| Broader exploration — growth laws compared | Known alternatives | Laws under which parts can meet again exist in another thread's work; nothing here can combine or read. |
| Long-term goal — G18 Comparing growth laws, with G17 | Capability gained | The first parts in the record that make copies of themselves out of knots that pass the knot test, with their rates known. |

**Next step:** Research directions — selected: #1.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A round read locally: can births be made one at a time, each knot reading a few steps of what is built, and still build what the rounds build? | 3/3 — would remove the last supplied round, for the ring that returns and perhaps for ordinary growth | 2/3 — I have a candidate rule (a knot reads when its parents are spent), but Codex's guarded rule of 20 November may already cover part of it | Read what that rule establishes; then every order of births on the cycle of four → stop at a law that matches the rounds in every order, or a proof that each law of a stated family does not | Selected · started |
| 2 | The simplest ration as a law of its own: what it grows besides copies | 2/3 — a growth law with no lookahead whose knots always pass the knot test | 3/3 — the engine and a census exist | Kinds of growth and rates on the census → stop at a table by kind, or a start that breaks the knot test | Alternative · deferred |
| 3 | A made pattern that reads another, your fold of emergence | 3/3 — the first reader nobody supplies | 1/3 — needs a law under which parts meet again | Try the other thread's law on the ring and on the copier → stop at one part whose course depends on another, or a reason it cannot | Alternative · deferred |
| 4 | Proofs of what is argued or computed in the two studies | 2/3 — turns computed rules into theorems | 3/3 — short arguments from one proved theorem | Write them out → stop at proofs or a counterexample | Alternative · deferred |

**GO on #1.** The evidence: this study reached its stop with a verdict on every prediction; the remaining open question of the line is the round inside a part; and the simplest ration found here needs no lookahead, so the question can now be asked cleanly. The new study is open and its first step, reading the record's guarded rule so as not to repeat it, is running.

**Corrections:** none.
**Goals:** one checkpoint row (G18, G17: capability gained); no goal changed. Sub-goal B323 is taken by the new study.
**Assumptions:** no new entry; a history line on A224 (the added rules). Still uncommitted in the tracker with the earlier pending entries.
**Scaffolds:** the ration, the treatment, the release rule, the offshoots, the fillers, the knot law and the start were each swapped. The copier survives a swap of the treatment (three rates), of the knot law and of the start; it is specific to rations that give a join one distinction; the fillers stop it. The complete round was not swapped here.
**Basket:** direction #1 taken (B323); B317 (3/3, 1/3) and B316 (2/3, 3/3) deferred; direction #2 new (2/3, 3/3).

Lesson 8.7's paragraph on these parts is updated on the guide and on prespatial.org.
