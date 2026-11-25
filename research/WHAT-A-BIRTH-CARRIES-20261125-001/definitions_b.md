# What a newborn's holdings must depend on for a made pattern to read which pattern it meets: definitions of the second ticket

Epic `WHAT-A-BIRTH-CARRIES-20261125-001` (its title keeps the word "read" in the owner's sense; the body does not use
it), ticket `WHAT-A-BIRTH-CARRIES-20261125-001B`. "BD2 n" below.

These definitions extend the following and change nothing in them except where marked "replaces":
- ticket A's ([definitions](definitions.md), "RD");
- the copier study's ticket A and B ([definitions](../MADE-COPIER-20261125-001/definitions.md), "D";
  [definitions_b](../MADE-COPIER-20261125-001/definitions_b.md), "DB");
- the fold study's ([definitions](../PARTS-MEET-AGAIN-20261124-001/definitions.md), "FD");
- the shared definitions ([definitions](../RING-IN-BALANCE-20261123-001/definitions.md), "SD").

They serve [the claim](claim_b.md) and [the pre-registration](../WHAT-A-BIRTH-CARRIES-20261125-001B/preregistration.md).
The data files sit with the pre-registration: `family.json`, `starts.json`, `renamings.json`, `gate_listing_b.txt`.
The canonical K1–K3 test is unchanged.

## 0. Words

Kept with their meanings: every word of RD 0, D 0 and FD 0.

Defined here, as phrases of words in use; no new noun:
- a law that uses no names; a sole candidate;
- the reader test;
- the values a rule can pass at one birth;
- the linking set; a linking distinction;
- a meeting only through made knots; an ancestral common knot made by births;
- the bars on Y;
- Whether through made knots; how many through made knots; Which at equal number;
- the input entries; m;
- lasts with the rest barred;
- the minimal laws among the listed laws.

**The law hands a count over** (RD 0) is extended. It also covers a count the law forms at one birth that fixes what
a later newborn holds, as the owing does under PARENT-OWING one round after the demand.

Not used:
- "reads", except in the owner's quoted sense;
- "meet again", except in the owner's words;
- "carries" or "carry";
- "gives parts off", which is SD's for a part that returns;
- "line", "beside", "crosses", "tells apart", and RD 0's barred words.

## 1. The round, the bounds, the knot test

1. **The round.** RD 1.1 (FD 2, RELEASE), with the rules of BD2 2. FD 2.4's one take per birth holds for every rule
   except J-EACH-PART (BD2 2.7).
2. **Bounds, by counts only:**
   - 7 rounds;
   - a run stops after the first round that leaves more than 1,500 knots, and that round is read;
   - the fold engine's guard stops a run without reading the round, at more than 20,000 candidate pairs (roster or
     demand roster), 20,000 groups, 20,000 births, 400,000 distinctions, 2,000,000 holder incidences or 200,000
     maximal cliques;
   - run P2 multiplies these limits by 10 and by 100, and keeps the knot bound;
   - each run records its peak counts;
   - no wall time enters a verdict.
3. **The knot test.** FD 7:
   - every knot of every run A at every round read, under the run's knot law;
   - barred runs (BD2 4.4) and lasting reruns (BD2 6.7) are tested only for pairs whose courses differ, at most 8 such
     pairs an item, the first in the registered order: pairs are ordered by s, then by the birth order of X's
     earliest member, then of Y's; the other barred runs are not knot-tested, and that is reported;
   - a differing pair whose barred run was not knot-tested is "undecided: knot test not run", never "found";
   - under not-all-equal only the knots born after round s are tested, at the run's last round read, by FD 7's birth
     method; a verdict there is fixed at birth for a birth that received a fresh distinction; the engine checks each
     birth after round s, and a run with one that received none is tested in full;
   - the runs of the ration controls (run P1) and of the unsymmetric ring (run U1) are tested in full;
   - under parity a tested barred run is tested in full at its last round read.
   - A case in a run with a failing knot is marked and does not count.

## 2. The rules

1. **Takes that use no names.** A birth takes **a sole candidate**: when its clause gives exactly one distinct
   eligible distinction, it takes that one; otherwise it takes nothing. Candidates are read on the structure at the
   start of the round (FD 2.4).
   - **MET-SOLE**: MET's two clauses (FD 3.3).
   - **STEPS1-SOLE**: the STEPS-1 offshoot clause. The candidates are the union, over the parent's parents, of their
     eligible distinctions not held by the parent; joins do not take.
   - **STEPS2-SOLE**: the STEPS-2 offshoot clause, the union over the knots two parent steps above the parent;
     joins do not take.
2. **PARENT-OWING** (on FLOOR1): an offshoot receives max(2, o) fresh distinctions.
   - o is the parent's owing (SD step 2): the number of the round's groups that contain the parent, counted before
     any is cancelled.
   - IMPLIED goes first: a birth whose inputs' parity lies in the span receives nothing (FD 2.8).
   - An offshoot that takes (p = 2) still receives max(2, o).
   - The rule covers every offshoot, including those RELEASE makes from distinctions that cancelled groups would
     have taken, and those of a short member under CANCEL-OFFSHOOT.
   - Every other birth receives as FLOOR1.
3. **PARENT-OWING-CAP3, PARENT-OWING-CAP4**: an offshoot receives min(max(2, o), k), k = 3 or 4, read as BD2 2.2.
4. **SHORT-BY** (a treatment, with FLOOR1 and CAP-3):
   - every group with a short member is cancelled;
   - a short member u that owes o(u) and holds h(u) makes min(h(u), o(u) − h(u)) offshoots, from its usable loose
     distinctions in birth order, and keeps the rest;
   - when o(u) − h(u) ≥ h(u) this is CANCEL-OFFSHOOT;
   - a keeper stays in the demand roster with what it keeps, and is a member in the next round;
   - whether it is short there is read afresh (SD step 2).
5. **Ration controls** (run P1; never in the search):
   - OFFSHOOT-TWO: an offshoot receives 2;
   - OFFSHOOT-THREE: an offshoot receives 3;
   - PARENT-OWING-1: an offshoot receives max(1, o). It can make offshoots of two places, against SD lines 12–13;
   - PARENT-OWING-PLAIN: an offshoot receives max(o, 3 − p, 1), the ordinary count with the parent's owing in place
     of the newborn's demand. It differs from PARENT-OWING only for a taking offshoot with o ≤ 1.
6. **The comparison 2 + (o mod 2)**: an offshoot receives 2 + (o mod 2). Run last, if the total allows.
7. **J-EACH-PART** (the positive control):
   - every offshoot also takes every eligible distinction held by a member of any part of the round's roster other
     than its parent's part;
   - parts are read at the start of the round;
   - FD 2.4 is amended for it alone: many takes at one birth;
   - 4 rounds, s ≤ 3.
8. **The owing is not PARENT-LOOSE (registered).**
   - PARENT-LOOSE hands a parent's h to its offshoot, the same quantity it sets, so a count is kept down a descent.
   - PARENT-OWING hands the parent's owing, which is formed anew from the round's groups each round and is not the
     quantity it sets (a usable loose count).
   - PARENT-LOOSE is not in this ticket.

## 3. The reader test, and the values a rule passes

A rule passes items 1 to 3; items 4 to 6 are reported (`family.json` holds the placement of every rule of every
law).
1. It is stated with no X, no Y, no descent, no part and no name.
2. It uses only values the recorded round already forms at the acting knot.
3. It applies at every birth of every start.
4. **With X alone**, read as the runs with every member of Y barred (A = ∅): the share of births at which the rule
   changes what the newborn holds or takes from what the recorded base law gives. Computed by run 1.
5. **The values it can pass at one birth.**
   - For a take: 2 (a sole candidate or nothing).
   - For a ration: the number of distinct fresh counts it can give one newborn of a given number of inputs.
   - For a treatment: the number of distinct acts on one short member.
   - The order is 1 < 2 < 3 < h(u) + 1 < unbounded. A law's value is the largest of its rules'.
6. A difference that one such value separates is credited to the law, never to a pattern.

The placements:
- J-EACH-PART fails item 1;
- every other rule passes items 1 to 3;
- FLOOR1, PARENT-OWING-CAP3 and the takes pass 2 values; CAP-3 and PARENT-OWING-CAP4 pass 3;
- ORD and PARENT-OWING are unbounded;
- SHORT-BY passes h(u) + 1;
- MET-SOLE, STEPS1-SOLE, STEPS2-SOLE, PARENT-OWING, its caps and SHORT-BY are new rules.

## 4. Class M

1. **Starts**: `starts.json`, in its registered order:
   - two-knot, made-3, three-knot, made-4, Ring(5, 3);
   - Ring(5, 3)+1 (Ring(5, 3) with knot 0 holding a fourth loose distinction: the ring without its rotation
     symmetry; the reflection through knot 0 remains, so X and Y may still be exchanged, BD2 6.8);
   - D2(5, 3), Ring(7, 3).
   - Each start is run on its registered numbering.
   - **The unsymmetric ring**, Ring(5, 3)+1+2 (`starts.json`, "extra"): Ring(5, 3) with knot 0 holding a fourth loose
     distinction and knot 1 a fourth and a fifth, so that no renaming maps the start onto itself. It is not in class
     M's search: it is run in run U1 only, under the two candidate laws of prediction B4. It was added at the freeze,
     on the advisor's last pass, and no scratch run was made on it.
2. **Pairs.**
   - For s = 1 to 4, every ordered pair (X, Y) of distinct parts of the roster after round s that are wholly apart
     (FD 1.6).
   - There is no cap on their number. This replaces FD 5.8's first eight parts and four pairs per round.
3. **Descent.**
   - D 2.6 on FD 4.2 with this s.
   - X's members are descended from X, and a knot made after round s is descended from X when it has a parent among
     X and its descendants.
   - Every other knot made at or before round s is from neither.
4. **The bars on Y**, per pair:
   - for each subset A of Y's members, run A from round s with every usable loose distinction of the members not in
     A barred;
   - A = Y is run A itself, and A = ∅ is FD 5.1's B(i);
   - for |Y| ≤ 4 every subset is run; for |Y| ≥ 5, only Y, ∅ and the |Y| subsets of size |Y| − 1;
   - the bars are a scaffold.

## 5. The meeting and the links (each read in each run separately)

1. **The meeting round** of a run for (X, Y): RD 3.4, read in that run.
2. **The linking set** at the meeting round t is the union of two sets of knots:
   - RD 3.5's set: knots made by round t − 1 whose met set, in round t's roster or demand roster, holds a knot of
     each descent;
   - **the suppliers of cross takes**: for each birth of round t with a parent of one descent that takes a
     distinction, every holder of that distinction of the other descent.
3. **A meeting with an empty linking set** (possible only where both parts' newborns meet with no older knot meeting
   both) has no linking knot. It is reported and never counted as a meeting only through made knots.
4. **A linking distinction** of a linking knot is a distinction of it held by a knot of either descent at round t.
   Each one is reported with the round its first holder was made and with its holders.
5. **A meeting only through made knots** (the strict form): the linking set is nonempty and every knot in it was made
   after round 0. FD 5.7's weaker class ("joinable through met sets with a common knot made after round 0") is
   reported with it.
6. **An ancestral common knot made by births** (FD 1.5 on the met members): a linking knot w made after round 0, with
   a knot u of X's descent and a knot v of Y's descent in w's met set at round t, such that w is a recorded ancestor
   of u and of v and not the parent of both. **The every-member form** (w a recorded ancestor of every member of X
   and of Y) is reported apart.

## 6. Readings

1. **B1-link**: the pair has a meeting only through made knots in run A.
2. **B1-ancestral**: B1-link, and one linking knot is an ancestral common knot made by births.
3. **B1-dependence: Whether through made knots.** B1-link, and the courses from X only (RD 3.1) of run A (A = Y) and
   of the run with A = ∅ differ through the last round both read.
   - Attribution (RD 4.3) is the condition. At the first round where the values used at X's births differ, the
     differing part must hold a knot from Y only: "through the meeting". It is accepted when the differing part
     holds at least one knot from Y only, whatever else it holds; a part holding only knots from neither or from both
     is not accepted.
   - The made linking knot is from neither, and a knot from both gives "a third part". Neither is accepted; both
     are reported.
   - **Differs, not attributed**: the courses differ and attribution is not accepted. No dependence through the
     meeting is then claimed.
   - Whether the run with A = ∅ has a meeting is reported. Where it has none, the result is worded "meets against
     does not meet".
4. **How many through made knots** (reported): subsets A, A′ with |A| ≠ |A′|, both nonempty, each with a meeting only
   through made knots in its own run, give different courses from X only. A subset whose run has no meeting is
   reported "no meeting".
5. **Which at equal number** (reported): |A| = |A′|, A ≠ A′, both with a meeting, and different courses. It is empty
   by symmetry where the structure after round s has a symmetry fixing X's members and every linking knot that maps
   A onto A′.
6. **The m reading** (reported), over the subsets of one pair:
   - P is their partition by the course from X only;
   - **the input entries** are the entries of RD 3.3, at the births of X's descent aligned by answers (RD 3.2), whose
     differing part between two subsets' runs is classed through the meeting;
   - m is the least number of input entries, at distinct births, whose joint value refines P;
   - **no difference**: P has one class; **handed in one value**: m = 1; **composed over several births**: m ≥ 2;
   - m and the births are reported;
   - "more than v classes", v the law's values at one birth, is reported as a consistency check: it implies m ≥ 2.
7. **Lasts with the rest barred** (reported, never part of a headline), for a pair whose courses first differ at
   round t_d:
   - both runs are rerun from round t_d with every member not from X only barred, to round t_d + 2 whatever the
     main bound, under the same knot bound;
   - it lasts when, in rounds t_d + 1 and t_d + 2, the rosters descended from X only are not the same (SD 29–30);
   - "undecided" if a rerun stops first.
   - The reruns get the knot test of BD2 1.3.
   - **Argued for the seen mechanism, not refereed**: a difference first in an offshoot's fresh count leaves, after
     the bars, a lone member whose offshoots in round t_d + 1 differ in number. So it lasts by implication.
8. **Is it the start's after all** (reported checks):
   - whether a start knot holds a linking distinction (BD2 5.4);
   - whether a start knot enters the linking set of any barred run;
   - whether the structure after round s has a symmetry that exchanges X and Y and fixes every linking knot,
     decided by an exact isomorphism search on that structure of at most 2,000,000 search nodes, and "undecided"
     beyond that count;
   - the link's ancestry back to the start, listed.
   - The honest phrase in every result is "the start supplies the ancestors; the knot and both parts are made".
9. **The Y-side knots** of the first differing demand (reported): the knots of Y's descent in the demand groups that
   differ, with their kind, parents and round.

## 7. Numberings

1. **DB 7** is the copier study's renaming statement: `definitions_b.md` of `MADE-COPIER-20261125-001`, section 7.
   With no taking rule, the run from a renamed start is, round by round, a renaming of the run.
2. **Lemma N** (b; argued, not refereed). Under a law of the search family, for every start and renaming σ, the run
   from σ of the start is, round by round, a renaming of the run, and every reading defined up to renaming is the
   same. Hypotheses:
   1. every choice by name is a choice among distinctions held by one knot alone (which usable loose distinction goes
      to which birth, and which ones SHORT-BY keeps), a permutation of them and so a renaming (DB 7);
   2. candidates and eligibility are sets, and "sole" counts distinct distinctions;
   3. every bound is a count;
   4. takes are read on the structure at the start of the round;
   5. readings forget names;
   6. the subsets A map with σ.
3. **Run N2.**
   - Renamings:
     - every numbering of made-3 (120) and of two-knot (30), up to the start's symmetries;
     - on each ring start, the reversal and 10 drawn renamings (`renamings.json`, seed `2026112508|<start>`).
   - Laws, fixed before the run: the candidate laws of prediction B4; the two fixed laws, MET-SOLE with
     FLOOR1/CANCEL-WAIT and with ORD/CANCEL-OFFSHOOT; and any other law that is minimal for a verdict after run 1a.
     Laws of runs 1b and 1c are not renamed.
   - Each pair is run with A = Y and A = ∅ only.
   - No knot test.
   - Compared:
     - the whole structure after every round, by its multiset of per-knot labels and a Weisfeiler–Leman invariant
       (4 iterations): "differs" refutes Lemma N, "equal" is "not refuted";
     - per run, the multiset over pairs of the verdicts of BD2 6.1 to 6.3, with each course from X only compared
       exactly by canonical form (RD 3.1).
   - A result says "verdicts and courses equal exactly; whole structures not distinguished by an invariant", never
     "identical".
   - The bars on the other subsets are not rerun in N2.
   - An exact whole-structure isomorphism test is not used: on a structure of 920 knots it ran past 4 minutes in the
     drafter's timing.

## 8. The minimal laws among the listed laws

- The cost of a law is the vector of:
  - holder steps looked at;
  - parent steps of the record;
  - a whole-roster look (yes or no);
  - its value at one birth (BD2 3 item 5, in the order given);
  - the number of new rules.
- Laws are compared component by component, a partial order.
- For each of the three verdicts (B1-link, B1-ancestral, B1-dependence), the minimal laws are the laws with the
  verdict that no other such law is below. They are reported as a set, "least among the listed laws".
- Every law of the search family is decided: "found", "none, every pair decided", or "none among n decided, m
  undecided".
- If run 1b or 1c is cut, "least among the listed laws" reads "least among the laws run".

## 9. Supplied by hand (scaffolds)

- every rule of BD2 2 and the controls;
- the starts, among them Ring(5, 3)+1 and the unsymmetric ring, and s;
- the bars on Y;
- every reading and its rounds;
- the order of the cost and of values;
- the bounds, the guard's numbers and multiples;
- the renamings and their seed.
