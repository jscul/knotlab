# A made clock and a part that reads it at each return: definitions

Epic `TIME-AS-FOLD-20261125-001`, ticket `TIME-AS-FOLD-20261125-001A`. These definitions extend
[the definitions of the study of parts that meet again](../PARTS-MEET-AGAIN-20261124-001/definitions.md) (**FD**, cited by
section) and, through them, [the shared definitions](../RING-IN-BALANCE-20261123-001/definitions.md) (**SD**, cited by
line), and change nothing in either. The claim they serve is [claim.md](claim.md); the runs are in
[the pre-registration](../TIME-AS-FOLD-20261125-001A/preregistration.md). The canonical K1–K3 test is unchanged.

## 0. Words

- **Kept with their meaning in FD and SD**: start, structure, place, loose, shared, live, dead, usable, barred, member,
  h(u), k(u), met set, common knot, joinable, part, past its start, the same, group, owing, short, waits, retires, join,
  offshoot, demand, ration, treatment, round, come apart, returns, gives parts off, ended, stopped (a roster with no
  member), jammed; take, eligible, the choice (OLDEST, NEWEST, IN-TURN, BY-COUNT), taking rule, parent step, ancestor,
  descendants, share nothing, wholly apart, one part again, course, trace, the paired test, run B(i), masked run, way (FD
  5.5's sense only), joint birth, kind (of a birth, FD 5.2).
- **Decided with the advisor for the guide's chapter on time**: clock and tick (a tick is the event, not a count of it;
  a supplied clock is given by whoever runs the growth, the round being one; a made clock is a pattern the growth builds in
  which a named event recurs, the study naming the event before it runs); return and period (the period is the count from
  one return to the next, always with its unit, here rounds); parent step and holder step (never a bare "step" as a unit,
  never "generation"); history (one whole course of a growth with nothing left undecided); priority (a rule choosing, from
  a named property of the ready births, which is made first) against choice of take; "a pattern that reads the clock at
  each return" until a **counting pattern** is earned (section 5.3); "the parts given off"; "a made count of returns". Not
  used: "counter", "tally", "told"; "clock" or "reader" for what counts a clock.
- **Reads** keeps the owner's sense only (A246): a part reads another when its course depends on whether the other is
  there. Rules, programs and studies "use", "look at" or "check".
- **New here**, each defined below: **series of returns**, **the second part**, **own knots** and **joint knots**, **Y
  barred after its r-th tick**, the runs **B(r)**, **B′(r)**, **Ball(r)**, **M(r)**, **the test with X barred**,
  **makes no further own knot** (with which of the three: ended, all members wait, closed), **numbering**, **shifts of
  the order of distinctions**, **MET's join clause alone**, **MET's offshoot clause alone**, **STEPS-k for offshoots of
  joins**, **STEPS-k for offshoots of offshoots**, **the laws of the count**, **cut short**, **unfinished**.
- **Not used**: "line" (the glossary keeps it for the owner's words and the literature's names; "X and its descendants",
  FD 4.2, serves); "dormant" (a part whose members all wait for ever is said in full); "keeps time with", "falls out of
  step", "yet"; "depth", "window", "shallower"; "the fold study" and its "fold engine" and "fold guard" (the owner's
  "fold" is another thing): "the study of parts that meet again", "its engine", "its guard".

## 1. The law, fixed before any pattern

1. **One complete round with taking**, exactly as FD 2 (order of births and names, eligibility, the take step, the choice,
   demand after the takes, the fresh count by distinct inputs, IMPLIED under parity).
2. **Primary laws**: L1 = STEPS-1 under COPY-LAW(t) = (FLOOR1, t, RELEASE); L2 = MET under CAP-3(t) = (CAP-3, t, RELEASE);
   t ∈ {CANCEL-RETIRE, CANCEL-OFFSHOOT, CANCEL-WAIT}. CAP-3(CANCEL-WAIT) is RING-LAW (SD lines 69–70). Each with OLDEST,
   NEWEST, IN-TURN and BY-COUNT.
3. **Other laws of the census**: the control (no taking rule); Q, MET, STEPS-1, STEPS-2, UP-TO-2 (FD 3.2, 3.3) under every
   base law; base laws RING-LAW, RING-LAW with FILLERS, COPY-LAW(t) for the three t, CAP-3(CANCEL-RETIRE),
   CAP-3(CANCEL-OFFSHOOT).
4. **The second arm, a family registered beforehand** (`rules.json` beside the pre-registration):
   - **MET's offshoot clause alone**: MET's offshoot clause; no join takes.
   - **MET's join clause alone**: MET's join clause; no offshoot takes. For a join MET's IN-TURN is OLDEST (FD 2.5), so
     this rule has three distinct choices. Chosen after the prototype's census; recorded as such.
   - **STEPS-k for offshoots of joins** (k = 1, 2, 3): STEPS-k's offshoot rule applied only to an offshoot whose parent has
     two or more parents in the birth record.
   - **STEPS-k for offshoots of offshoots** (k = 1, 2, 3): the same for an offshoot whose parent has exactly one parent.
     A fitted control, added by hand after the prototype's census: it spares exactly the ring's own offshoots, which are
     children of joins.
   - **Equivalences by construction**: STEPS-k applied to offshoots of start knots takes nothing (a start knot has no
     ancestor k parent steps above it), so the family by the kind of the parent has three members for each k, the third
     being STEPS-k itself; MET with neither clause is the control. (This holds for STEPS-k only; a split of MET's offshoot
     clause by the kind of the parent would not reduce so, and is not registered.)
   - **STEPS-k for k = 1 to 8** under RING-LAW on the ring starts (FD 3.3's STEPS-k taken for any k).
   - **Cost** of every rule: FD 3.3's vector (holder steps looked at, parent steps of the record, anything across the
     roster, what supplies the choice) and one component added here, **kinds of birth treated differently**: 1 when every
     birth is treated alike, 2 when joins and offshoots are treated differently (every rule of FD that takes, and MET's
     clauses alone), 3 when offshoots are also treated differently by the kind of their parent (STEPS-k for offshoots of
     joins or of offshoots). The number of the parent's parents lies within the first parent step, which STEPS-k already
     looks at, so these rules add only the new component.
5. **The choice of take** is a stated rule for the whole run. OLDEST, NEWEST and BY-COUNT use names (BY-COUNT counts its
   index from the oldest name); IN-TURN uses the order of births. So every choice depends on the numbering of the start
   (section 5.4).
6. **Knot laws**: not-all-equal and parity (IMPLIED); every run under both.
7. **The bounds, the guard and the limit.** Runs are grown through 18 rounds (the ladder of STEPS-k through 2k + 4
   rounds); a run is cut short after the first round that leaves more than 4,000 knots (6,000 for the ladder), that round
   kept. The guard of the study of parts that meet again cuts a run short, without keeping the round, when the round would
   have more than 20,000 joinable pairs (in the roster or in the demand roster), 20,000 groups, 20,000 births or 400,000
   distinctions, or a roster would need more than 2,000,000 holder incidences (members' places counted with their other
   holders) or 200,000 maximal cliques of the joinable relation. **Limit**: 600 seconds of process time for each run A
   and each test; a run or test that reaches it is **unfinished**, never a negative.
8. Nothing in this study changes a law for a pattern, adds a rule for counting, or places a knot after the start.

## 2. The made clock

1. **The named event**, fixed before any run: a return of a part of the live roster (SD lines 85–88), taken as follows.
2. **"Past its start"** is SD line 28's property of a roster (no member meets a member), applied here to a part: no member
   of the part meets a member. Under taking rules members that took one distinction meet directly, so the filter drops
   many-member parts for a reason unrelated to the start. **Every series is taken twice, with and without the filter**,
   and both are reported; the claim uses the series taken without it.
3. **First return.** For a part P of the roster after round s, its first return is the least round t > s at which some part
   Q of the roster after round t satisfies: every member of Q descends from P (through parents; a member of P that is
   still a member descends from itself); **Q has a member made after round s**; Q is the same as P (SD lines 29–30). SD's
   sameness carries h, k and the inclusion-maximal met sets; a direct meeting between two members that lies in no met set
   of two or more members is not carried, and is reported for each return. **Every qualifying Q at that round is
   recorded**; the series follows the one whose smallest member name is least (a convention that changes under renaming).
   Members that only waited, or a jam, make no return.
4. **A series of returns** is a part P₀ after a round t₀ and the chain of first returns P₁ at t₁, P₂ at t₂, …: t₁ the first
   return of P₀, t₂ the first return of P₁, and so on, until a part has no first return within the rounds grown. Its
   **ticks** are the returns at t₁, t₂, …; its **periods** are t_{r+1} − t_r, in rounds. A series is reported from the
   earliest t₀ whose part is not itself the first return of an earlier part.
5. **A made clock, Y**, is a series of returns whose parts have **two or more members**. A series of one-member parts is
   the glossary's endless chain, an order of knots each a parent of the next, and is reported apart; it is not a clock.
6. **Equal periods.** The claim needs four consecutive periods of one length after t_j; series with unequal periods are
   reported, and a period that is not the same as the others ends the stretch.
7. **The parts given off at the r-th tick**: the parts of the roster after round t_r, other than the qualifying parts of
   that tick, that have a member descended from P_{r−1}. A part given off that also has a member not descended from P_{r−1}
   is counted and labelled **mixed**. Y **gives parts off** at a tick when there is at least one. SD line 87 counts the
   other qualifying parts as given off; here they are copies, counted apart.
8. **The start's roster returns** (the reading 27 of the study of parts that meet again): the rounds t ≥ 1 at which some
   part is the same as the start's whole roster. Reported for the ring starts beside the series.
9. **The parts given off are Y's**: their knots, births and every count of them. They are a record of Y's ticks only if
   some made pattern's course depends on their number.

## 3. The second part

1. **X** is a part of the roster after a tick round t_j of Y (j ≥ 0), wholly apart from P_j at t_j (FD 1.6), with a member
   made after round 0. All such parts, in order of their smallest member name, at most 8 for each (Y, j).
2. **X and its descendants**: X and every knot made after round t_j with a parent among them (FD 4.2, taken from t_j).
   **Y's part and its descendants**: P_j and every knot made after t_j with a parent among them. A knot can be in both,
   through a joint birth.
3. **X's origin**: three facts, each yes or no and not exclusive: (a) X and P_j have a common part in their ancestry at
   some earlier round (they came apart, FD's reading); (b) X descends from a part given off by Y at an earlier tick (only
   for j ≥ 1); (c) X has members of mixed descent (one descended from Y's series before t_j and one not).
4. **Own knots and joint knots.** X's **own knots** are the knots made after t_j with a parent among X and its descendants
   and no parent among P_j and its descendants. **Joint knots** have a parent among each. Sense 5.1, its count and
   section 5.2 use own knots only; joint knots are counted and reported beside them. The trace of C-iii is FD 5.2's (it
   excludes joint births and includes their children).

## 4. Barring the made clock

1. **Y barred after its (j + r)-th tick**, run B(r), r = 1, 2, 3: run A through round t_{j+r}; then every usable loose
   distinction of the members of P_{j+r} that are **not** among X and its descendants is barred (FD 5.1); then the same
   law. X's own descendants are never barred; how many members of P_{j+r} descend from X is reported.
2. **B′(r)**: the same, barring instead the members of the parts given off at tick j + r (not among X and its
   descendants), and leaving the series. It separates reading the clock from reading what it gives off.
3. **Ball(r)**: when several parts qualify at t_{j+r} (a part that copies itself), every qualifying part is barred (not
   X's descendants). B(r) bars the series' part only.
4. **The masked run M(r)** is run A from round t_{j+r} + 1 in which no member among X and its descendants is joinable with
   a member among P_{j+r} and its descendants (FD 5.6); a knot among both is on both sides and is joinable with no member
   of either. A difference between A and B(r) goes **through a meeting** when X's trace in M(r) equals its trace in B(r).
   Masked runs are comparisons, not growths under the law. A difference that M(r) does not reproduce is reported as
   **unconfirmed** and never counts as through a meeting; the two kinds it could be are named (a knot of Y's acting as a
   common knot among X's own members, or making a distinction eligible for X's takes) without a further run.
5. **The test with X barred**: run A with every usable loose distinction of X's members barred at t_j; reported: Y's
   series of returns in that run, against run A's.
6. **Rounds grown and verdicts.** Runs are grown through 18 rounds. A verdict is given for each test (Y, j, X), bars run in
   the order r = 1, 2, 3. C-iii fails when, for some r, both runs are grown through round t_{j+r} + 2 periods and X's trace
   is equal through it; it holds when, for every r, X's trace differs within two periods of the bar, through a meeting (a
   difference seen is decided as seen). C fails when clause 1 fails in run A, or when, for some r, X makes an own knot in B(r) later than
   round t_{j+r} + 2 periods. C holds only when, for every r, both runs are grown through t_{j+r} + 4 periods. Every
   other test is undecided, never "no case".
7. **What the test tests**: whether X depends on Y's being there in each of three periods; not on returns as such.

## 5. The senses, the count and the numbering

1. **At a fixed ratio** (the thread's phrase): over the four periods from t_j to t_{j+4}, X's own knots in each period are
   one and the same number c > 0.
2. **Makes no further own knot**: in B(r), the least lag L, 0 ≤ L ≤ 2 periods, such that X and its descendants make no own
   knot in the rounds after t_{j+r} + L that are grown, with at least two periods grown after t_{j+r} + L and run A making
   own knots of X there. Which of the three is reported: **ended** (X and its descendants have no member), **all members
   wait** (every member is short under CANCEL-WAIT, or holds), or **closed** (their last births received no usable fresh
   distinction: FILLERS, or IMPLIED under parity).
3. **Counting pattern**: X passes C (claim, section 5). The count is X's own knots, taken in B(r) at run A's rounds: with
   e the own knots X makes in B(r) after t_{j+r} (one and the same for r = 1, 2, 3), the ticks since t_j are (their number
   − e) / c, shown for the three bars tested.
4. **Numbering.** A numbering of a start is an order of its distinctions (FD 2.1 names them in that order) together with
   an order of its knots (the order of its stars, which fixes the start knots' names). "Names reversed" in the study of
   parts that meet again reverses the distinctions only. **Registered numberings**: every numbering of a start of at most
   six distinctions (the two-knot start: 120 orders of its five distinctions × 2 orders of its knots = 240), run before any
   choice of take is enumerated; for every other start of n distinctions, the 4n numberings made of the n **shifts of the
   order of distinctions** (the order as given, started at each of its n places in turn, so that each distinction is once
   the least-named), each with the distinctions as given or reversed and the knots as given or reversed (the four
   numberings of the study of parts that meet again among them). Every choice uses names, and OLDEST and BY-COUNT use the
   least-named first, so the shifts put each distinction in that place once. The number of the registered numberings
   that differ up to the start's own symmetries is reported. A case **survives** a numbering when some (Y′, X′) in the run
   under that numbering meets the same sense. An enumerated choice of take (FD's ALL-CHOICES), if used, is bounded and
   each history so found is labelled **picked**; a picked history never earns "made".

## 6. Supplied or made: three questions, each with exclusive answers

1. **Who made Y and X**: both made by births after round 0 / one of them is a part of start knots as given / both are.
2. **What made the meeting** (for a difference through a meeting): knots the growth made link X's descendants and Y's
   (FD 5.7) / only start knots do / no meeting (a round-wide trigger: a stall, a residual stall, a parity closing).
3. **What fixed the takes**: a stated choice rule under which the case survives every numbering (starts of at most six
   distinctions) or the 4n and run 5b, the number run always stated / a stated rule under which it fails under some
   registered numbering (a case under a supplied numbering, with the condition on names stated where found) / a history
   picked.
"Made by the growth" is said only when the three answers are the first.

## 7. The knot test

As FD 7: parity by ranks and by kernel, the two agreeing on every knot; not-all-equal directly for knots of at most 12
places at every round and by the birth method for every knot where every birth receives a fresh distinction; every knot
of run A at every round grown, under the run's own knot law, for every registered run including every k of the ladder;
and every knot of every comparison run (B, B′, Ball, M, the test with X barred) at every round grown under parity (a birth
can receive nothing there) and at its last round under not-all-equal. A run with a failing knot is reported and does not
count toward the stop.

## 8. What is supplied by hand (scaffolds), and their swaps

Everything SD and FD list as supplied (SD lines 155–160, FD 8), and here: the choice of the primary laws by the cost
reading of the study of parts that meet again; the family of section 1.4 (new rules, two of them chosen after the
prototype's census); the named event and the study's check that a return has happened; "past its start" (swapped: taken
with and without); the least-name convention for the series (swapped: the greatest name); the series of returns; what is
counted as the parts given off; barring the series' part only (swapped: B′, Ball); the lag of two periods; four periods;
the bound of 8 second parts; the masked runs; the numberings; the bounds, the guard and the limit. Census swaps
registered: the fresh count by parents (the scaffold the count rests on); demand taken before the takes; the first-return
convention; "past its start". The study's check that a return has happened, and every count of ticks, are the study's:
nothing in the growth makes them.
