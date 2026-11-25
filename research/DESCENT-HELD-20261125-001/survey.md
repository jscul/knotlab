# The order in a knot's own places: survey of the record

Epic `DESCENT-HELD-20261125-001` (sub-goal B328; assumptions A247, A228, A237; goals G5 with G18), 25 November 2026. Paths
are the repository's. Evidence classes: **proved** (with its referee standing), **computed** (with its range), **argued**
(not refereed), **reading**. The note: [note.md](note.md); the definitions: [definitions.md](definitions.md).

**What changed from the drafter's first survey:** the private paths (the epic's ticket file, line citations into the
register of assumptions) and every link into a scratch folder are removed; assumptions and the sub-goal are named by number;
the time-as-a-fold design's count argument, seen in scratch while in freeze, is no longer cited; the record's word
"generation" is quoted, and "parent steps" used otherwise; the drafter's assembly (section 3) is aligned with the note
(ten lone-knot cases; "has no renaming exchanging ..." in place of a third sense of "recovers"); and section 4 points to the
note instead of to scratch output.

## 1. What the question stands on

- **The owner's words and the thread's reading**: [owner_request.md](owner_request.md). The owner asked the thread to "work
  your way through all 4" of its top-valued directions; this epic is the fourth's untaken lead.
- **Sub-goal B328**: whether something a knot has by the growth law itself, in its own places or in how they are shared, can
  be one more than what its parents have, so that before and after is carried by distinctions and not by a stamp.
- **A247** (a scaffold): each knot carries a stamp written by whoever runs the growth, its "generation" counted in threes;
  nothing in the growth laws writes or uses a stamp. Its challenge names this epic.
- **A228** (an interpretation): the only before and after the structure itself carries is that a knot comes after its
  parents. **A237** (a scaffold): the part-round and birth-by-birth laws.
- **The guide, Chapter 9** (`publication/knotlab/INTUITIONS.md` lines 4040-4600): lesson 9.2, "What one knot's holdings
  give" (lines 4232-4239); lesson 9.3, the order not recovered from what is built and three values handed down (lines
  4306-4330), and "Open about the order" (lines 4349-4352).

## 2. The record, study by study

### 2.1 The least record (`LEAST-RECORD-20261124-001`; computed, scientific referee pending)

- **"Recovers the parents"**: a look within d holder steps, with a stamp shown; a rule of distance d recovers the parents on a
  population when no two looks within d are alike with one chosen place a parent place and the other not
  (`research/LEAST-RECORD-20261124-001A/preregistration.md` lines 32-62; the look,
  `research/PARENTS-FROM-HOLDERS-20261124-001A/preregistration.md` lines 37-49).
- **The result** (`research/LEAST-RECORD-20261124-001A/results.md` lines 9-15, 29, 45-56): the stamp counted in threes, written
  by each new knot from its parents' stamps, recovers every parent at one holder step under all four laws (RATION-3 with
  waiting; FLOOR1 with offshoots; FLOOR1 with retiring; ordinary growth), on complete rounds and half-built structures,
  wherever no start knot waits in a round in which a start knot it meets is a parent of a birth; "none of 34,243 births is an
  exception". Range: twenty pairs of start and law, to about 2,000 knots or twelve rounds, the half-built structures of twenty
  sampled orders, and sixteen runs under holding through six rounds.
- **Where it fails**: the start built so that a start knot waits while a knot it meets acts; there counting in fives works
  (`results.md` lines 71-75). **Under holding** "every birth's parents still had equal generations, in all 16 runs" (P9,
  which had leaned the other way, `results.md` line 37).
- **Settled there** (`preregistration.md` lines 130-146): the equal-steps sketch under RELEASE (lines 132-139; it uses RELEASE
  and who waits, not the ration); a stamp that is a function of what the look shows adds nothing (lines 142-144); recovered
  parents can stand in for the record in the guard (lines 145-146, not run).
- **What it is not**: "the order of descent cut down to three values, written by hand"
  (`research/LEAST-RECORD-20261124-001/decision.md` lines 31-33).
- **The census bears on it**: the note's history lines ([history_lines.md](history_lines.md)) give the counts on the census of
  3,348 starts (scratch, for the confirming run to check).

### 2.2 Parents from holders (`PARENTS-FROM-HOLDERS-20261124-001`; computed, one proof by hand confirmed, referee pending)

- **Half-built states can hide the parents completely** (`research/PARENTS-FROM-HOLDERS-20261124-001A/results.md` lines 43-47):
  places exchanged by a renaming of the whole structure under each of the four laws (115, 8, 49 and 12 at distance 6); the
  smallest has two knots, the lone four-place knot and its first offshoot; under FLOOR1 with offshoots the two-knot start
  after its first offshoot (`artifacts/PARENTS-FROM-HOLDERS-20261124-001A/PARENTS-FROM-HOLDERS-20261124-001A-E001_parents_from_holders/whole_pairs.json`).
- **Complete rounds**: a rule at distance 2 where a short knot retires; none of any fixed distance where it makes offshoots
  (proved by hand, confirmed to round 12); under RATION-3 with waiting and ordinary growth the least distance grows to 5 and 6
  (`results.md` lines 31-39). One finished structure of 16 knots keeps no trace of its order (line 39).

### 2.3 A round read locally (`LOCAL-ROUND-20261123-001`; computed, referee pending)

- One birth at a time under the guard of the one-birth-at-a-time study (the record's "brood guard") builds what the complete
  rounds build, given the record of parents (`research/LOCAL-ROUND-20261123-001/decision.md` lines 9-31); "Not shown: ... that
  the holders alone would do, with no record of parents" (line 43); every law fails at the second birth on the start-clause
  counterexample (line 58). Its `lr_core.own_round` is the reference of the confirming run's gate.

### 2.4 The guard under the cap and under holding (`GUARD-CAP-AND-HOLD-20261124-001`; computed, referee pending)

- Under holding a knot gives in more than one round, and a brood is not one round
  (`research/GUARD-CAP-AND-HOLD-20261124-001/decision.md` lines 9-24). This is why parents at different parent steps arise
  under holding where no knot waits (the note's witness W2).

### 2.5 What a reference is (`RING-IN-BALANCE-20261123-001`, ticket B; computed, referee pending)

- One law (ordinary growth) on one family (rings with a leftover distinction on every knot): r = f + 2p − 3 − 2e, e in {0, 1, 2},
  on 44,333 knots of six rings (`research/RING-IN-BALANCE-20261123-001B/results.md` line 25); settled by the cluster count, not
  a finding (`research/RING-IN-BALANCE-20261123-001B/preregistration.md` lines 86-91). The round is a function of f and p (and
  e); a look shows their sum, the number of places, not either alone.

### 2.6 The shared definitions (`research/RING-IN-BALANCE-20261123-001/definitions.md`)

- Every recorded ration is a function of p and D alone (lines 59-62); the closing exception uses the knot law and one barred
  distinction switches it off everywhere (lines 63-66, 72-74); which usable loose distinction goes to which birth is a renaming
  (lines 76-77); the record's "generation" is "not read from the structure" (lines 121-124); the knot test (lines 128-139);
  under parity every new knot that receives a fresh distinction passes
  (`research/RING-IN-BALANCE-20261123-001A/preregistration.md` lines 98-103), which the note qualifies at closing births.

### 2.7 Counts a pattern can carry, in another sense (`HOLD-COUNT-20261111-001`; proved, refereed)

- A drawn knot pattern's allowed states can count n distinctions mod m only when m is even and n odd, "never in threes, unless
  the outside fixes a value" (`docs/KNOT_INTUITION.md` lines 4389-4400). A different sense: a value the allowed states compute,
  not a count of a knot's own places.

### 2.8 Counts of fresh distinctions left to a rule (`FRESH-COUNT-20261118-001`; proved, refereed R1)

- Under the complete-round joining rule a count rule only places offshoots; each fresh distinction beyond the demand becomes
  an offshoot; "inherit a parent's count" is in its menu (`research/FRESH-COUNT-20261118-001/fresh_count.md` lines 24-30,
  55, 58). So the usable form of the count changes the growth by adding offshoots; the barred forms do not.

### 2.9 The literature's names (from memory, not checked)

- A phase clock of self-stabilizing unison (Couvreur, Francez and Gouda, 1992), cited by the least-record pre-registration
  (lines 23-28); proof-labelling schemes (Korman, Kutten and Peleg, 2010); the orientation of a graded order by its ranks
  counted in threes (folklore).

## 3. What the record settles about arm R (the drafter's assembly; argued, not refereed)

- **L1.** Under the four laws of the least-record study no quantity shown by the structure recovers the parents on the
  half-built structures of 2.2, at any distance: a shown quantity adds nothing to the look (2.1), and those structures have
  renamings exchanging a parent place with one that is not.
- **L2 (M1).** Under each recorded ration with the ten cases of the note, the lone start knot's first offshoot leaves a
  two-knot structure with such a renaming.
- **L3.** Under a ration of p and D alone, at a birth (not a closing birth) that repeats a parent's (p, D), the two numbers of
  places are equal.
- **L4.** Under a law in which a birth takes only usable loose distinctions, which of them it takes changes the structure only
  by a renaming (2.6), so the value cannot be carried by that choice.

## 4. Beyond the record

The note's two arguments and the scratch counts it quotes; the confirming run's
[pre-registration](../DESCENT-HELD-20261125-001A/preregistration.md) checks them.
