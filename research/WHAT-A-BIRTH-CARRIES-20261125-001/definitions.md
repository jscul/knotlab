# What a newborn's holdings must depend on for a made pattern to read which pattern it meets: definitions

Epic `WHAT-A-BIRTH-CARRIES-20261125-001`, ticket `WHAT-A-BIRTH-CARRIES-20261125-001A`. "RD n" below. These definitions
extend three others and change nothing in them except where said (RD 3.4):
- the copier study's ("D", [definitions](../MADE-COPIER-20261125-001/definitions.md));
- the fold study's ("FD", [definitions](../PARTS-MEET-AGAIN-20261124-001/definitions.md));
- the shared definitions ("SD", [definitions](../RING-IN-BALANCE-20261123-001/definitions.md)).

They serve [the claim](claim.md) and [the pre-registration](../WHAT-A-BIRTH-CARRIES-20261125-001A/preregistration.md).
The data files sit with the pre-registration:
- `numberings.json`;
- `gate_listing.txt`;
- `attribution_records.json`.

The canonical K1–K3 test is unchanged.

## 0. Words

Kept from D 0, FD 0 and SD with their meanings.

**Defined here**, as phrases of words in use; no new noun:
- the course from X only;
- the values used at X's births;
- answers (D 7.8's rule);
- the meeting round (this ticket's);
- the same meeting;
- the linking knots;
- the set of courses;
- the compared prefix;
- the number of distinct courses over the class;
- handed in one value; composed over several births; no difference;
- through the meeting; a third part; round-wide; unclassified;
- needs the second pattern's members usable;
- follows a; follows h.

**Whether** and **Which** are the guide's pair: whether the other is there, and which it is.

**Meet, in its three senses.** "Two knots meet" is SD's: they hold a common distinction. "One part again" is FD 4.3's
meeting of parts. **The meeting round** of this ticket is RD 3.4's. Each is named where it matters.

**The law hands a count over** when a count the law forms at a birth (here the demand) fixes what the newborn holds.
It is not D 3.4's "hand on", which is a tie between a fresh distinction and a place.

**Not used**:
- "line", "side by side", "beside", "crosses", "tells apart", "carry" or "carries";
- the banned words of the thread's studies.

## 1. The law

1. **The round**: one complete round as FD 2 exactly:
   - FD 2.1: the order of births and names;
   - FD 2.2: eligibility;
   - FD 2.4: step 5′, one take per birth;
   - FD 2.6: demand after the takes;
   - FD 2.7: the fresh count by distinct inputs;
   - FD 2.8: IMPLIED under parity;
   - RELEASE.
2. **The ration ORD**: f = max(D, 3 − p, 1) (SD step 7), with p the number of distinct inputs and D the demand.
3. **The treatment**: CANCEL-RETIRE (SD step 3). CANCEL-OFFSHOOT and CANCEL-WAIT are used in run 1b only.
4. **The taking rule MET** (FD 3.3, both clauses):
   - with **OLDEST** (FD 2.5: the candidate with the smallest name);
   - and, as its swap, **NEWEST** (the largest).
   - Both use names.
5. **Knot laws**: parity with IMPLIED, and not-all-equal; every run under both.
6. **Bounds, by counts only**:
   - 4 rounds;
   - a run stops after the first round that leaves more than 800 knots; that round is read;
   - the fold engine's guard (`pm.GUARD`) stops a run, without reading the round, when the round would have more than
     20,000 candidate pairs (in the roster or the demand roster), 20,000 groups, 20,000 births, 400,000 distinctions,
     2,000,000 holder incidences or 200,000 maximal cliques;
   - a stop never alters a completed round, and no wall time enters any verdict.

## 2. Starts, numberings, patterns

1. **The start made-h** = `[[0,1,2],[0,3,…,2+h]]`:
   - h = 3 and 4 in run 1, and h = 5 and 6 in run 2.
   - **X**: the two round-1 offshoots of the start knot with three places.
   - **Y_h**: the h round-1 offshoots of the start knot with h + 1 places (**Y's start knot**).
   - **e**: the start's shared distinction.
   - s = 1.
2. **A numbering** writes the start with names 0 … h + 2 for its distinctions and its two knots in an order.
   - Its distinctions are named in the order of their labels (FD 2.1).
   - **The start's symmetries** permute the two loose distinctions of X's start knot, and the h loose distinctions of
     Y's.
   - A symmetry maps a named start onto itself, so the registered list holds one numbering per orbit:
     (h + 3)!/h! = 120, 210, 336, 504 for h = 3 … 6, the order of the two knots included (`numberings.json`,
     "made_class").
   - **The registered numbering** is made-h as written.
3. **The class Y_h^a**, a = 0 … h, on made-h:
   - After round 1, every usable loose distinction is barred for each Y member whose round-1 input is not among the a
     listed names; the other a members are left usable.
   - The bars are a scaffold, added by hand.
   - Every marked numbering is listed: an entry of "made_class" (its **underlying numbering**) with one set of a names.
     That gives (h + 3)!/(a!·(h − a)!) entries: 120, 360, 360, 120 for h = 3, and 210, 840, 1,260, 840, 210 for h = 4
     ("class_h_by_a").
   - Y_h^h is Y_h.
   - **What "which second pattern" means here**: how many of Y's members a hand-placed bar left usable.
4. **Descent**: D 2.6 exactly (from X only, from Y only, from both, from neither).

## 3. What is read

1. **The course from X only**, after round s through round R, is a labelled structure.
   - **Its knots**: the knots from X only, X's members included, each labelled with:
     - its round (s for X's members);
     - its kind;
     - its number of places;
     - for each round from its birth (or s) to R, its usable and its barred loose counts.
   - **Its distinctions**: every distinction such a knot holds, each labelled with:
     - its origin: existing after round s; fresh of a knot from X only; or fresh of any other knot;
     - its barred flag at round R.
   - **Its links**: knot–distinction incidence, and parent arcs between its knots.
   - **All names are forgotten.**
   - **Its canonical form** is the isomorphism class of this labelled structure, decided exactly: by a complete
     canonical labelling of the labelled graph (the literature's canonical labelling, as computed by nauty or
     bliss), or by an exact isomorphism test (the literature's VF2) within classes of an invariant that sorts them
     first. A hash or invariant alone never decides equality. The engine states which it uses.
   - FD's trace and the count of joint births are reported with every course.
2. **Answers** (D 7.8's rule, used to align two runs under one underlying numbering):
   - a birth answers another when they are of the same round and kind, their parents answer one another, and, for
     offshoots, they have the same index in the order of that parent's offshoots of the round;
   - start knots answer by their order in the start's list;
   - start distinctions answer by name;
   - fresh distinctions of answering births answer in order.
   - A knot with no answer in the other run is **unanswered**.
3. **The values used at X's births** in round t, in **step-major** order: all entries of step 1, then of step 2, and so
   on. Within a step, entries for groups are in FD 2.1's group order and entries for births are in FD 2.1's birth
   order, both read in run A (the run with the smaller a). Each entry is compared with the entry of the answering
   group, member or birth in run B.
   1. Step 1: each group holding a member from X only. Compared: its size, and the multiset of its members' descents.
   2. Step 2: each member from X only. Compared: its owing, and whether it is short.
   3. Step 3: the treatment's act on it.
   4. Step 4 and 5: each birth with a parent from X only. Compared: its kind, the answers of its parents, and its
      loose inputs.
   5. Step 5′: its take. Compared:
      - its candidates, each with **the knot that supplies it**: for a join, a common knot of its parents holding it;
        for an offshoot, a knot its parent meets holding it;
      - what it took.
   6. Step 6: its demand D. Compared: the number, and the multiset of the descents of the members of its demand
      groups. Descent only; their kinds are not compared, since the law does not use them at X's birth.
   7. Step 7: p, the implied flag (parity), and f.
   8. Round-wide entries: a stall or a closing, and whether the guard stopped round t, and on which limit.
4. **The meeting round** of a run replaces D 2.3 for this ticket. It is the first round t > s with any of:
   - a group, or a demand group, holding a knot descended from X and a knot descended from Y (a knot from both counts
     as each);
   - a take, by a birth with a parent of one descent, of a distinction with a holder of the other.
5. **The linking knots** of a meeting round:
   - the set of knots made at or before the round before it, whose met set, in that round's roster or demand roster,
     holds both a knot descended from X and one descended from Y. Newborns of the meeting round are left out: a newborn
     holding a shared distinction meets every other holder, and counting them would make the set differ whenever the
     number of births differs;
   - each is given its FD 5.7 class: an ancestral common knot; a knot the growth made that is no ancestor of both; or a
     start knot that is no recorded ancestor of both (**through a start knot**).
6. **The same meeting** (a reported reading; the claim's condition is only the same meeting round), for the runs of a
   pair under one underlying numbering, requires all of:
   - the same meeting round;
   - the same set of linking knots, by answers;
   - the same births of X up to that round, by answers.
   The demand and the fresh count of X's births of the meeting round itself are excluded. Different meeting rounds are
   reported with the gap.

## 4. Verdicts

1. **The pairs.** For a and b on made-h, the pairs are every a-marked entry with every b-marked entry on one
   underlying numbering: (ν, A, B), with ν an entry of "made_class" and A, B sets of a and of b names. The per-numbering
   conditions (RD 4.3 to 4.5) are read on every such pair and counted per class.
2. **The set of courses and disjointness.**
   - C(h, a) is the set of canonical forms of the courses from X only, through **the compared prefix**, over every
     entry of Y_h^a.
   - For a pair of cells, the compared prefix is the longest prefix of rounds that every run of both cells reached; it
     must be round 2 or later, and it is stated with the verdict.
   - **Disjoint**: no canonical form lies in both sets. **Not disjoint**: one does. **Undecided**: some run read fewer
     than 2 rounds after s.
   - Disjointness at every shorter prefix down to round 2 is reported too.
   - No entry of one cell is paired with an entry of another for disjointness.
3. **Attribution**, for one pair (ν, A, B) whose courses differ:
   - take the first round where the values used at X's births differ, the first differing entry in RD 3.3's order, and
     its differing part (the members, candidates or partners in one run with no answer in the other);
   - replace each differing candidate by the knot that supplies it;
   - class the resulting knots:
     - **through the meeting**: one of them is from Y only;
     - **a third part**: none is from Y only, and one is from both or from neither (marked "a start knot" when all are
       start knots);
     - **round-wide**: the entry is an implied flag, a stall or closing, or the guard's stop (supplied, FD 5.7);
     - **unclassified**: anything else, for instance a differing part all from X only, or empty. It fails the
       condition.
4. **Handed in one value / composed over several births / no difference**, at fixed h and one underlying numbering
   ν, over a = 1 … h, with each a read on every a-marked entry over ν:
   - let P be the partition of those entries by the course from X only through the compared prefix;
   - **no difference** when P has one class;
   - **handed in one value** when one entry of RD 3.3 (one position by answers, one round within the prefix) induces P
     exactly;
   - **composed over several births** otherwise.
   - Where the inducing entry is a count (D, owing, p or f), the verdict adds: the law hands a count over.
5. **Follows a; follows h** (descriptions only, no cause named):
   - **follows a** at fixed h: C(h, a) and C(h, b) are disjoint;
   - **follows h** at fixed a: C(3, a) and C(4, a) are disjoint, a = 0 … 3.
6. **Needs the second pattern's members usable** (a reported reading): C(h, a) and C(h, 0) are disjoint.
7. **The number of distinct courses over the class**: |C(h, 1) ∪ … ∪ C(h, h)|, and, per underlying numbering, the
   number of classes of P.

## 5. Controls and checks

1. **Negative control**: no taking rule, on the same class and bounds; a law that uses no names.
   - One run per entry for h = 3, and one per cell for h = 4.
   - X and Y never meet (FD argument 1), so one course over the whole class is expected.
   - It tests that the canonical form leaks no name or knot number, and it shows any IMPLIED closing or guard stop.
   - It exercises no attribution.
2. **Planted control**: CAP-3/CANCEL-RETIRE with MET taking every candidate.
   - FD 2.4 is amended for this control only: a birth takes every candidate of the MET clause.
   - It is a marked comparison, not a member of the search, and uses no names.
   - Registered numbering, a = 0, made-5 against made-6, with the start knots and distinctions answering by order and
     name.
   - **Criterion**: the first difference of the course from X only is at round 3, and its first differing entry is X's
     round-3 joins' candidates. The extra candidate is supplied by Y's start knot, so it is classed **a third part (a
     start knot)**.
3. **Gate**:
   - The engine equals the fold engine with no taking rule, MET(OLDEST) and MET(NEWEST) on 648 runs:
     - 12 starts (the fold engine's seven named starts and made-2 to made-6) × 3 rations (FLOOR1, CAP-3, ORD) × 3 treatments × 2
       knot laws × 3 takes;
     - 6 rounds, 800 knots.
   - It reproduces `gate_listing.txt` birth by birth.
   - Its attribution returns the expected class on each of the four records of `attribution_records.json`.
   - 100 pairs of numberings related by a symmetry give identical runs. This check is nearly empty: such numberings are
     the same named start, so it tests only the order of the places listed inside a knot.
4. **The knot test**: FD 7, on every knot of every run at every round read, under the run's knot law. A case with a
   failing knot is marked and does not count.

## 6. Supplied by hand (scaffolds)

- ORD, RETIRE and RELEASE (A224, A104);
- MET (A245), and its choice by names (A231, A236);
- the starts;
- the bars that make Y_h^a;
- X, s, and the compared prefix;
- the course from X only and its canonical form;
- the values used at X's births and their order;
- answers;
- the attribution classes;
- the controls;
- the bounds and the guard's numbers.
