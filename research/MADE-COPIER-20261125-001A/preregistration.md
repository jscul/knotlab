# A made pattern that, on meeting a second pattern, leaves two of the second? Pre-registration

Ticket `MADE-COPIER-20261125-001A` of epic `MADE-COPIER-20261125-001` (lead B327; assumptions A244 and A248, with A223,
A241, A245, A246; goals G15 with G17 and G18). The code will be written by a helper agent that has not seen the
drafter's prototype, from this text ("P"), [the definitions](../MADE-COPIER-20261125-001/definitions.md) ("D"),
[the claim](../MADE-COPIER-20261125-001/claim.md), [the owner's arm](../MADE-COPIER-20261125-001/owner_arm.md), [the fold
study's definitions](../PARTS-MEET-AGAIN-20261124-001/definitions.md) ("FD"), [the shared
definitions](../RING-IN-BALANCE-20261123-001/definitions.md) ("SD") and the data files of this folder
([starts.json](starts.json), [take_lists.json](take_lists.json), [record_structures.json](record_structures.json)). The
engine will extend the fold study's engine
(`experiments/PARTS-MEET-AGAIN-20261124-001A/PARTS-MEET-AGAIN-20261124-001A-E001_meet_again/pm.py`) without editing it.
The canonical K1–K3 test is unchanged. Versions 1 and 2 of this text are filed in the advisor folder as sent; where a
reading changed, the change is said where it is made. No claim is made about living things, minds, physics or time.

**Frozen on 2026-11-25 (UTC; the evening of 24 November 2026, Pacific time), after the advisor's three passes and before
the study's code is written.** The owner's later idea of the same evening, "What if instead of 'copying', we consume and
output 2?" ([his request](../MADE-COPIER-20261125-001/owner_request.md)), is not part of this text. It is taken up in a
second ticket of the same study, with its own claim and its own pre-registration. Here, two parts the same as the second
pattern count for the claim only when their members descend from the first pattern alone (D 5.1); parts whose members
descend from both patterns are reported by descent and are not counted.

## The question

The owner, 24 November 2026: "copying would not be a law. Laws are for how the knots interact. A copy function, like
other functions, would be a logical structure that has a meeting pattern with other things. And we would need to prove
that the copy/paste pattern can be generalized." And: "Keep two things apart in everything written about this: a law is
the rule the growth follows (which knots join, what a new knot receives, what a short knot does); a copier is a pattern
the growth makes. What we have so far makes more of itself and takes no input. What I am asking for meets another
pattern and leaves two of it." The question, in his words: "under the cheapest law the fold study finds that lets parts
meet, is there a made pattern that, on meeting a second pattern, leaves two of the second?"

His steps, in order: "1. State the claim before testing it. For which class of patterns should the copier work, and what
counts as 'two of it': the same form, the same built structure, or the same values? Say which of these is claimed. 2.
Check the record first. In particular the other thread's note that a chain of parity knots hands a value on only once,
so that sending one value to two places needs a distinction with a third holder. Confirm or correct that from the
record, and say what it implies for pasting a value under parity and under not-all-equal. 3. The first test: let the
existing two-knot part that copies itself meet one other small pattern, and see whether anything of the second pattern
appears twice afterwards. Use the fold study's paired test: with and without the second pattern. 4. Generalize or bound
it. Either an argument that the copier works for the whole stated class, or the smallest pattern it fails on and why."

His stop: "Stop at a pattern that leaves two of what it met, with the class it works for, or at a reason no made pattern
can under that law."

His inkling of 24 November 2026 (Pacific time; the record's tickets carry 25 November, its date in UTC), A248, kept apart
from the evidence and registered as its own arm: "I want to take on the copier too. But mind you, I have an inkling about
this one. Like the interesting fact here is that it's actually impossible to generalize a 'copier' for all logic
structures. It might be the case that some logic models are able to over-write the instructions of the copier and break
out."

The claim, stated before any test, is [the claim](../MADE-COPIER-20261125-001/claim.md); the record on handing a value on
is [the survey](../MADE-COPIER-20261125-001/survey.md).

**The law is fixed first** (claim, section 1): MET under both COPY-LAW(t) (the fold study's name for (FLOOR1, t,
RELEASE), not a law of copying) and CAP-3(t), each primary; STEPS-1 as the second taking rule; STEPS-2 for the arm of
parts that came apart; the form arm under CAP-3(t) and FBP(t) (FLOOR1 with the fresh count by parents); four stated
choice rules fixed before the runs, on a registered naming. The copier is a pattern grown under that law.

**What is tested** (claim, section 5): C(r, b) in values, per rule r and base law b, with X made and with X a start
pattern; CF(r, b) in form under the form arm's laws; each predicted to fail. Settled by argument and checked: the
ration's doing (no part with a member holding two is made after the start's own offshoots under COPY-LAW(t), copied or
not) and, from a tie-free start, no made distinction ever tied under not-all-equal.

## In standard terms

In the literature's words, not the program's: a synchronous hypergraph-rewriting system in which each new hyperedge
attaches to degree-one vertices of earlier ones and, under the laws used here, to one vertex of higher degree; every
hyperedge carries a constraint, a parity equation over the field of two elements or a not-all-equal condition. The form
reading is isomorphism of a labelled component of a derived graph; the built-structure reading an induced labelled
sub-hypergraph isomorphism; the values reading is **fan-out** (the circuit literature's word): two new variables equal,
in every solution, to a given old one. Under parity a new equation with one new variable sets it to the sum of its old
variables, so fan-out is linear algebra over the row space. Under not-all-equal, when every new constraint has a new
variable of its own, every old solution extends, and from a system with no forced equalities none is ever created.

## Prior work in the program

Searches, each with `--until 2026-11-25 --exclude MADE-COPIER-20261125-001`:

`python3 -B scripts/track.py objects "a made pattern that meets another pattern and leaves two of it, a copier that takes an input" --until 2026-11-25 --exclude MADE-COPIER-20261125-001`

`python3 -B scripts/track.py objects "a value handed on to two places, a distinction with a third holder, distinctions tied under parity and not-all-equal" --until 2026-11-25 --exclude MADE-COPIER-20261125-001`

`python3 -B scripts/track.py objects "a part that copies itself under a law in which a birth takes a distinction held by a knot its parent meets" --until 2026-11-25 --exclude MADE-COPIER-20261125-001`

What they return (run read-only by the drafter on 2026-11-24), one line each, in the order returned:

- First search.
  - `PARTS-MEET-AGAIN-20261124-001/2` — the same law: one part's course differs with another stopped under MET and the
    ancestor-taking laws; "none depends on what the other part is". The law and the paired test used here.
  - `LAST-DISTINCTION-AND-PRIVATE-PULSES-20261121-001/1` — a relative: a last loose distinction shared between a clock
    and an outside expense, in a prepared ordinary start. Not used.
  - `PARTS-MEET-AGAIN-20261124-001/1` — the same study: under rules Q and R parts never meet again, and "from round 1
    these rules undo both objects".
  - `OVERLAP-READ-20261111-001/4`, `RING-IN-BALANCE-20261123-001/4`, `NEVER-NEST-20261118-001/1`,
    `FIVE-PRODUCT-GUARDED-REUSE-20261115-001/1` — unrelated objects.
- Second search.
  - `THIRD-HOLDER-20261123-001/2` — a relative: the smallest structure with a hidden excess needs a birth that takes a
    distinction already held twice. Its note is the note the owner names; surveyed.
  - `REVIEW-LEADS-20261123-001/4` — a relative: two-holder structures cap the score at 2; three or four holders reach 20/9.
  - `SPLIT-KNOT-METER-AND-CLOSING-TRIPLE-20261121-001/4` — a relative, not used.
  - `UNREAD-COMPANION-AND-ORDER-FREE-WEIGHTING-20261121-001/4` — a relative: a not-all-equal birth changes an old pair's
    weight; a weighting, not a tie (the limit stated in "What a result would and would not show").
  - `PAYMENT-HISTORY-AND-FIRST-WRITE-20261122-001/1` — a relative: with two holders every fresh reference extends.
  - `READS-HOLDERS-SOURCES-20261120-001/2` — **used**: with not-all-equal and at most two holders every distinction can
    change alone, so nothing is tied (details line 89; survey 1.2).
  - `KNOT-COUNTS-AND-ONE-EXTRA-MEETING-20261121-001/1` — unrelated.
- Third search.
  - `PARTS-MEET-AGAIN-20261124-001/1`, `/2` — as above.
  - `ONE-PARENT-REREAD-20261123-001/1` — the same kind of law (rule Q) on other objects.
  - `COPYING-PARTS-20261123-001/3` — the same object: the census of the part that copies itself; FLOOR1 needed.
  - `SETTING-AS-REREAD-20261123-001/1` — a relative: one round of rule Q makes two setting births.
  - `GENERATORS-20261120-001/4`, `COPIES-AND-MEETINGS-20261120-001/6` — relatives (survey, section 3).

The epics of the rows in the top three of each search: `LAST-DISTINCTION-AND-PRIVATE-PULSES-20261121-001`,
`ONE-PARENT-REREAD-20261123-001`, `PARTS-MEET-AGAIN-20261124-001`, `REVIEW-LEADS-20261123-001`,
`SPLIT-KNOT-METER-AND-CLOSING-TRIPLE-20261121-001`, `THIRD-HOLDER-20261123-001`.

## Prior work outside the program

Each from memory, the literature's, not checked:
- **Fan-out** in Boolean circuits; read-once formulas are those without it.
- **The duplicator** of interaction nets (Lafont, 1990): copying as an agent with its own rule, that is, a law; the
  owner's premise excludes exactly that.
- **Von Neumann's universal constructor** (1966) copies a description given as an input; **Langton's loops** (1984)
  copy themselves and take none, like the part on record.
- **Linear algebra over the field of two elements**: two variables are equal in every solution exactly when their sum is
  in the row space; for a graph's cycle space, when they form a two-edge cut.
- **Two-colouring of hypergraphs**: every hypergraph with edges of three or more vertices and vertices in at most two
  edges is two-colourable (an Euler-tour argument, cited in the record); the Fano plane is the smallest three-uniform
  one that is not.

What this would add: whether a pattern made under a stated growth law, on a structure every piece of which passes the
canonical knot test, can fan out a value or leave two of a part it met; under which knot law; for which second
patterns; and how much of it is the choice's and the numbering's. Not searched further.

## Known before the runs (disclosed)

The drafter wrote a scratch prototype (in its scratch folder: version 1 `cp.py`, `s1_selfcopy.py` to `s9h_tables.py`;
version 2 `v2_common.py`, `v2_run.py`, `v2_swaps.py`, `v2_every.py`, `v2_reader.py`, `v2_smallest.py`, `v2_checks1.py`;
version 3 `v3_arm.py`, `v3_checks.py`, `v3_record.py`, `v3_starts.py`; unreviewed; not the study's engine; its author
does not write the study's code). It imports the fold study's engine read-only and adds the readings. Everything it showed
is listed here or in [the owner's arm](../MADE-COPIER-20261125-001/owner_arm.md), section C. "Seen" means seen in the
prototype. Results of versions 1 and 2 that version 3 replaces are marked so.

**What the gate cannot test.** The prototype, like the study's engine, uses the fold engine's growth code; an equality of
the engine's runs with the fold engine's (P0) therefore tests nothing new. What is written afresh, and must be tested,
is the readings: ties, the sameness of parts with their descents, renamings of Y's knots, descents, B_X, X alone, Y
alone, the replacement and third-pattern runs, the renamings of the start, the take lists, the arm's readings.

**Record checks for the owner's step 2** (survey 1.1, 1.2), on [record_structures.json](record_structures.json). Parity,
two holders: no violation of the cut statements in 3,659 drawn connected structures and 14,459 parts; not-all-equal, two
holders: no tie in 80,811 labelled and 3,690 drawn structures; the Fano piece ties three places, all shared, every knot
passing; the counterexample to "any start" checked: the join's fresh distinction is tied to 7.

**S4 and its exceptions, checked** (`s8_check_s4.py`, `v2_checks1.py`). Over 1,008 runs (version 1) and then over the
fold study's starts and the designs under RELEASE and HOLD with MET, STEPS-1 and STEPS-2 (every choice rule, three
treatments, both knot laws, 6 rounds): every birth received one fresh distinction (or none, implied, under parity) except
offshoots of start knots (two or one) and, under STEPS-2, offshoots of knots whose parents are all start knots (two); no
other exception under HOLD. A two-place knot left by an implied birth passes and has its two places tied (S7's repair).

**The part that copies itself under the taking laws** (version 1, s1). Over 315 runs (the three starts of run 1,
COPY-LAW(t) and CAP-3(t), no taking rule, Q, MET, STEPS-1, STEPS-2, UP-TO-2, four choices, 8 rounds): no part the same
as the two-knot part in the roster after any round t ≥ 3 under any taking rule; with no taking rule the counts of starts.json ("counts for
P3"), which follow the record's recurrences under COPY-LAW(t) (2, 4, 8, 16 under retiring on the two-knot start) and
give no part copying itself under CAP-3(t). With the fresh count by parents, one further round of copying in 3 of 180
runs.

**Designs** ([starts.json](starts.json), "designs"; D 2.2): made-2 to made-6, made-2 with the names of X and Y exchanged
(`made-2-exchanged`), and ystart-<kind> for the six kinds, e the label 1000 (named last).

**The first test under the stated rules** (`v2_run.py`, 1,584 runs: made-2 to made-6 and the six designs with Y present
from round 0 × the nine base laws × MET and STEPS-1 × four rules × both knot laws, 6 rounds, at most 500 knots; run A,
B(i), B_X, X alone and the replacement runs read across designs).
- **Values, parity.** One run of 792: ystart-three-222, COPY-LAW(CANCEL-OFFSHOOT), MET(NEWEST): after round 6 two usable
  loose made distinctions descended from X only (names 52, 53), tied to Y's place 16 (one holder after round 0, seven at
  round 6). B(i): two again, tied to another place of Y (34, 35 and 10; 10 has two holders after round 0, five at round
  6): "does not need Y's births". B_X: no two descended from Y only. Both are later taken, by different births (52 in
  rounds 7 and 8 by two offshoots, 53 by five), and stay tied through round 8 (two users). Lost under every renaming n1
  to n4. No other run, and no made design, has two made by X.
- **Values, not-all-equal.** No tie involving a made distinction in any of the 792 runs.
- **The second pattern handing on its own value**: 9 parity runs, the same with X barred.
- **C(r, b) by rule**: for X a start pattern, C(NEWEST, COPY-LAW(CANCEL-OFFSHOOT)) holds for 1 of 5 members before the
  renamings and for none after; every other rule and base law, 0. For X made, 0 of 4 under every rule and base law.
- **Form: census, under parity.** Runs of the form arm's laws (CAP-3(t) and FBP(t), MET and STEPS-1) under parity
  with at least one part the same as the member's Y after round s, in the runs of that member's family, its control
  included: made family (made-2 to made-6, 240 runs), made-3 47, made-4 13, made-5 6, made-6 11; family with Y present
  from round 0 (288 runs), one-2 31, one-3 1, three-222 38, two-23 0, two-33 0 (dropped). **By descent from X only** (at
  least one such part with every member descended from X only): made-3 46, made-4 13, made-5 6, made-6 11; one-2 2,
  one-3 0, three-222 3. Under not-all-equal every form reading equals the one under parity, run by run (528 of 528
  pairs), so the counts are the same. So X's descendants do make one part the same as each member of the made class,
  and of one-2 and three-222; whether they make two is what CF asks. (Version 2 counted pairs of a run and a round;
  version 3 gave the sums over both knot laws, 94, 26, 12, 22 and 62, 2, 76, with numbers of runs, 192 and 240, that
  were neither.)
- **Form: two parts the same as Y, every member descended from X only**: besides the control made-2, three cases, all on
  made-4 under FBP(CANCEL-OFFSHOOT): MET(BY-COUNT), STEPS-1(BY-COUNT), STEPS-1(NEWEST), each under both knot laws.
  - MET(BY-COUNT), the one case of CF's law: two at round 5. B(i) gives the same two and X's course is the same with Y
    barred, so the case needs Y's knots, not Y's births; X alone has none (its course differs from X alone at round 2).
    With made-3, made-5 or made-6 as the second pattern, no two of the new Y; and in those runs the parts the same as made-4's Y
    number 0, 1 and 1 (fewer than two). Renamings: survives n4, lost under n1 and n3. Honestly: **one case that is there
    with this Y and not in X alone, not a copier for any other member, lost under renaming.**
  - STEPS-1(BY-COUNT) and STEPS-1(NEWEST): X alone makes the same two, and so do the replacement runs: X's own course.
- **Built structure**: no renaming of Y's knots among the made knots in any run.
- **The fourth mark on the replacement runs** (X's renamed trace with Y against with Y′, same X, law, rule and naming):
  differs in 164 of 864 made-X pairs and 203 of 1,440 start-X pairs; under MET, CAP-3(t) 56 of 144 and 116 of 240, FBP(t)
  22 of 144 and 76 of 240, COPY-LAW(t) 6 of 144 and 11 of 240. So, unlike the fold study's 16 pairs, X's course here
  depends on what Y is in 367 of 2,304 pairs; that is not what fails.
- **Knots**: under not-all-equal no failure (154,399 verdicts); under parity 4 failing verdicts, in one run (made-2,
  CAP-3(CANCEL-WAIT), MET(NEWEST): the fold study's two joins of twelve parents at round 5); no method disagreement.

**Swaps on the form arm's negatives** (`v2_swaps.py`, 6,336 runs). The form arm's six base laws × the 11 designs × MET
and STEPS-1 × four rules × both knot laws, under each of n1, n3, n4, the order of births reversed, demand before the
takes, HOLD: no case beyond the three made-4 cases and the controls. MET(BY-COUNT) on made-4 survives n4 and demand
before the takes, and is lost under n1, n3, the order of births reversed and HOLD. 8 runs had a round whose roster hit
the fold engine's guard; those rounds were not read.

**The controls of the readings** (`v2_reader.py`; D 3.6). With no taking rule on the two-knot start, the form reading
and the built-structure reading in counting mode count, at every round from 2 to 7, exactly N(t) (retiring 0, 4, 0, 8,
0, 16; offshoots 0, 4, 2, 8, 8, 18; waiting 0, 4, 0, 10, 0, 24). A part the same as Y and a renaming of Y's knots placed
by hand after round 3 are each found (one more) on made-3, made-4, ystart-one-3 and ystart-two-23.

**The smallest second pattern the values case fails on, in the registered class** (members first, then places: one
member holding two; that it is the smallest follows from P6, since the case holds for no other member). Under the case's
law, in round 3 each of the three takes of births descended from X only takes the eligible distinction with the largest
name. With three members holding two (the case) that distinction is one of X's own round-1 fresh distinctions (22 or
23), and Y's place 16 keeps its value at two loose places by round 6. With one member holding two, Y's member makes two
offshoots named after X's, so **all three takes of round 3 take Y's fresh distinction 17**, and **after round 6 X's three
usable loose made distinctions are tied to three different start distinctions (e, 7 and 5)**: one each, never two of one.

**Every choice, the F1 control** (`v2_every.py`). Parity, MET, made-2 to made-6 and the six designs with Y present from
round 0 × COPY-LAW(t) and CAP-3(t), rounds s + 1 to s + 4. Under COPY-LAW with retiring and with waiting every history is
read (4 to 144 per design: the growth stops) and none has two. Under CAP-3 with retiring and waiting, read in full where
there are at most 60,000 (the one-member designs, 9 histories) and otherwise drawn, 5,000 per design and law in the
prototype (the registered number is 20,000): none. Under COPY-LAW with offshoots (5,000 drawn): **every design has
histories with two**: made-3 4, made-4 34, made-5 30, made-6 25; one-2 26, one-3 10, two-23 13, two-33 11, three-222 4;
the controls made-2 57 and two-22 23; in 9 of these 237 histories some knot fails (made-2 4, made-4 1, made-5 3, one-3
1), marked. Under CAP-3 with offshoots none, but on made-4, made-5 and made-6 the fold engine's guard stopped 4,867,
5,000 and 5,000 of the drawn histories before round s + 4, so those three are not read there. The first three histories
with two per design and law (33, every knot passing) are registered in [take_lists.json](take_lists.json) and replay
exactly; in all 35 values cases (the 33 lists, the stated-rule case and its B(i)), v has one holder (21) or two (14)
after round s and 2 to 11 at the round seen (three or more in 24), and the structure read has at least six distinctions
with three or more holders. Read: the knot law allows a value of each second pattern of the class at two loose places
made by X; the choice decides whether it is there. (Version 1's counts under the take-by-take weighting, 3,000 histories
per design, are kept as disclosed in version 1.)

**The third-pattern starts** (`v3_checks.py`). All 60 (each kind of Y with each of the five other kinds of Z, named
before and after Y): e has three holders, and at round 0 no tie and no frozen distinction under either knot law.

**The owner's arm** (`v3_arm.py`, `v3_checks.py`; on the registered naming only, e last, with made-2-exchanged: 1,728
runs; run O: 1,034 runs). All listed in [the owner's arm](../MADE-COPIER-20261125-001/owner_arm.md), section C; the
counts PO3 to PO7 compare against are repeated in the predictions. Version 2's arm counts, over two namings of e, are
replaced.

**The not-all-equal weighting, left out.** "No made distinction is ever tied" is not "nothing of v reaches f": for a
birth NAE(a, b, f) with (a, b) uniform, f differs from a in 4 of the 6 allowed states. That is a weighting, and the study
does not measure it.

**Not run by the drafter:** the masked runs on the values case; the strong form of the built-structure reading (no
renaming to compare); every choice under STEPS-1 and STEPS-2; the arm of parts that came apart under the version-2
readings (version 1's 213 pairs: none with a made distinction of X tied to a place of Y, none with two parts the same as
Y); anything past round 8.

## Settled by construction (stated, not tested)

Arguments for the referee; the runs check them. Checked by the advisor in a first form and repaired as it asked; the
form given here has been checked by the drafter's runs only.

1. **S1, ties are decided at birth.** Under a law in which every birth of a round either receives a fresh distinction
   (a row with a column of its own) or, under parity with IMPLIED, adds a row already in the span, every allowed state
   before the round extends, whether or not any knot passes and however many births take one shared distinction; and no
   state after it restricts to a state not allowed before it. So the allowed states restricted to the distinctions
   existing after round t are the same after every later round. Excluded: LITERAL, FLOOR0, ONE-FEWER.
2. **S2, not-all-equal.** Every birth with a fresh distinction: a fresh distinction f of a birth u is tied to another
   distinction exactly when u has one fresh distinction and u's inputs are all tied equal before its round; f is then
   tied unequal to each input. Otherwise there are two allowed states differing only in f. By induction with S1, **from a
   start with no tie, no made distinction is ever tied to another**, under any taking rule and choice, whether or not
   knots pass. From a start with a tie it can be (the Fano counterexample, disclosed).
3. **S3, parity.** Under IMPLIED, a birth with two or more fresh distinctions hands nothing on; a birth u with one fresh
   distinction f has f tied to v exactly when the sum over the field of two elements of u's inputs and v lies in the span
   of the rules before u's round, zero included; if v is an input, u fails the knot test, so a passing maker never holds
   v; the same-round case needs v's maker to have one fresh distinction too, and is never needed for the values reading.
4. **S4, one fresh distinction.** Under FLOOR1 with the fresh count by distinct inputs: a join has two or more inputs
   and receives one. An offshoot of a parent q that is not a start knot: q holds exactly one place of its own parent g
   (the distinction d it took; its take is by rule not held by g, and a join's other inputs were loose elsewhere); if g is
   not a start knot, the distinction g took from its own parent is shared, not held by q, and eligible; if g is a start
   knot, g acted in the round it made q and, under RELEASE, spent every other loose place, so they are shared; under HOLD
   a start knot that keeps something was in a group and so has a shared place; under CANCEL-WAIT g made q, so it was not
   waiting; a knot holding barred distinctions has no children. So under MET (the parent meets g) and STEPS-1 (g is one
   parent step from q; several parents give a union that is not empty) the offshoot takes and receives one. Under STEPS-2
   the same holds one parent step later (an offshoot of q takes whenever q has an ancestor two parent steps away). FLOOR1
   never gives more than two. **Consequence, by maker**: under COPY-LAW(t) with
   MET or STEPS-1, every knot made by a birth other than an offshoot of a start knot holds **at most one** loose
   distinction (none when its birth is implied), so no part with a member holding two is made by such births, copied or
   not; the part that copies itself stops copying. It is the ration's doing; the form arm therefore runs under CAP-3(t)
   and FBP(t), where S4 does not hold.
5. **No renaming of Y's knots under COPY-LAW(t)** (P5's second clause): every member of Y holds two or more loose places,
   so its image under a renaming is a made knot holding two or more loose places, an offshoot of a start knot by S4; that
   offshoot's inputs keep their old holder, the start knot, which is outside every set of made knots (holders never
   decrease, FD 1.1); but every holder of a place of a member of Y is one of Y's knots. So the renaming fails on that
   place.
6. **S5, S6** (record facts; survey 1.1, 1.2): parity with at most two holders, ties are two-element cuts; not-all-equal
   with at most two holders, every distinction can change alone. **The owner's step 2, in two sentences**: with at most
   two holders, two loose distinctions tied to each other are the only loose distinctions of their connected structure,
   so two usable loose places for one value, in a connected structure that has any other loose distinction (usable or
   barred), need a distinction with a third holder (with no other, four knots suffice: {f1, a, b}, {a, b, v}, {v, c,
   d}, {c, d, f2} tie f1, v and f2, every knot passing); under not-all-equal nothing is tied
   with at most two holders, and growth from a tie-free start never ties a made distinction (S2). The registered designs
   have at most two holders, so they are tie-free and S2 applies; the third-pattern starts are not covered by S6 and are
   tie-free at round 0 by computation (run G).
7. **S7.** A passing knot with three or more places has no two of its own places tied (a two-place knot left by an
   implied birth has both places tied and passes).
8. **The arm's B1** ([the owner's arm](../MADE-COPIER-20261125-001/owner_arm.md), B1): under the hypotheses of S1, from
   round s on, **nothing changes a place, or a relation among distinctions that exist; what changes is the holders of
   shared distinctions and, through the course, which loose distinctions are taken or barred.** A distinction of X is
   barred only when a member of X and its descendants retires, or by the paired runs' barring; a usable loose distinction
   of a member of X is taken only by a birth with a parent among X's members (a loose distinction is never eligible, FD
   2.2), joint births included. Outside the hypotheses (FLOOR0, ONE-FEWER) a birth descended from Y only can change the
   relation on X's distinctions (run O).
9. **The arm's B2**: at the level of the rule, MET and the joining rule refer to no descent. With every choice read in
   full it is a proof that on a start with a renaming exchanging X and Y the counts of X's and Y's states are unchanged
   when X and Y are exchanged: a renaming carries histories onto histories one to one. With drawn histories only the
   weighting is carried, not the counts. A stated rule is carried along only by renamings that keep the order of names.
10. **The arm's B3, on the parts by descent**: if every member of each of two parts the same as Y is descended from X
    only and X meets condition 2 of D 5.1, then the counts of parts the same as Y′ differ between the replacement runs
    with Y and with Y′, at the round at which the run with Y′ has two (fewer than two against at least two), so the parts
    by descent (D 5.3) differ. True by definition, when both runs reached that round. On the renamed trace a difference
    can be missed at the last round read (the trace restricts each met set to X and its descendants, so a part wholly of
    X's descendants and the restricted remainder of a mixed part look the same, and a birth of Y in that round can take a
    place of X's common knot). Nothing like it holds
    for values: the same takes up to renaming can be tied to places of different second patterns; a take from Y is seen
    in the one case, and is not proved necessary.
11. **Checks, true by construction**: a tie is never a knot; under parity an offshoot never fails the knot test (it has at
    most two inputs, and its verdict is fixed at birth by S1).

## What is supplied

Everything the fold study's definitions supply (FD 8), and here: the designs and their starts; the classes; the
registered naming and the four renamings; the three readings and their bounds; the descents; B_X, X alone, Y alone, the
replacement and third-pattern runs; the take-by-take weighting and its seeds; the take lists; the bounds; the structures
of the controls of the readings. **The choice is supplied in every case**, and with it the numbering it uses.

## What a result would and would not show

- **Verdicts, three questions** (D 5.2): who made the two; what fixed the takes; where X and the linking knot come
  from. "Made" only when all three are the growth's.
- **The disclosed values case, in one sentence**: supplied: a start pattern, joined to the second pattern through a
  start distinction, under a rule that picks by the start's numbering, comes to hold one value of one second pattern at
  two loose places, and it is gone when the start is renamed or the second pattern changed; only the births that carry
  the value are made.
- **A positive for C(r, b)** would show one value of each registered second pattern at two loose places, under parity,
  one rule and one numbering (and its renamings). It would not show two of the pattern, a class beyond the registered
  forms, a made X on the designs with Y present from round 0, or anything under not-all-equal.
- **The expected result** shows what COPY-LAW(t) can make (the ration's doing); that not-all-equal growth from a tie-free
  start ties nothing; that under parity a value is tied at two loose places in every design under some history (seen under
  COPY-LAW(CANCEL-OFFSHOOT) only), and
  that which history is the choice's; and, in the form arm, a negative bounded by its census, its controls of the
  readings and its swaps. **The form arm has no every-choice control**: its negative says that four stated rules and
  their swaps do not leave two of the class, not that the law does not allow it. It does not show that no made pattern
  can leave two of what it meets under parity, anything past the bounds, or dependence under a weighting.
- **For values under parity the expected result reaches neither arm of the owner's stop**: no pattern with the class it
  works for, and no reason no made pattern can (S2 is for not-all-equal, S4 for one ration). The study then reports:
  the arguments and what they close; the form arm's bounded negative; the one values case with its verdicts; the F1
  control with its take lists (the knot law allows it; the choice decides it); and that the question under parity is
  not decided.
- **The plain sentence for the owner** (the advisor's, fitted): "Under the law we fixed, the ration gives every later
  knot at most one loose distinction, so the part that copied itself stops and no part of that kind is made again; that
  is the ration's doing and says nothing yet about leaving two parts the same as a second pattern. Under not-all-equal no made distinction is ever tied
  to another. Under parity a value of a second pattern can be tied at two loose places, but in every case found the
  choice we supplied put it there: it happens under one rule, for one pattern, numbered one way. We have neither a
  copier nor a reason there cannot be one." With the form arm: "Under the cap of three and under the other count of
  fresh distinctions, where parts like the second pattern are made again, nothing we grew made two of what it met,
  except in one case that is there with that second pattern and not with the first pattern alone, is no copier for any
  other, and is gone when the start is renamed." On the inkling: the owner's arm, section D.

## Starts and files

- [starts.json](starts.json): the naming convention; the designs (stars, X, Y, s); X alone and Y alone; the renamings n1
  to n4 per design as exact label maps; the third-pattern knots for each kind, named before Y and named after Y; the fold study's starts
  used (two-knot, three-knot, three-knot-larger, Ring(5, 3)); the pair starts; the counts of P3 (parts the same as the
  two-knot part after rounds 0 to 8, no taking rule, parity, the fold engine).
- [take_lists.json](take_lists.json): its format is stated in the file (one list per round from s + 1, the distinction
  picked by each take in the order the round asks; v, the two and their descents, the holders of v).
- [record_structures.json](record_structures.json): run R's structures: the parity structures with their four drawn
  parts each, the not-all-equal structures, and the structures built by hand; the 80,811 labelled structures are every
  structure of one to three knots of three or four places in which each place is loose or shared with exactly one other
  knot, no knot holding a distinction twice, enumerated by pairing places.

## Runs

Both knot laws in every run unless the table says otherwise. RELEASE unless stated. **Bounds**: rounds as in the table; a run stops after the first round
past 500 knots (read; its roster read where the fold engine's guard allows, otherwise reported "not read"); the fold
study's guard. **Knot tests**: every knot of run A at every round read, of every comparison run at its last round read,
of every replayed history at every round, of every drawn history with two at every round.

| Run | Starts | Laws | Rounds | Readings |
| --- | --- | --- | --- | --- |
| G | the fold study's starts; 600 drawn small structures with any number of holders (`random.Random('2026112505')`: 2 to 7 knots of 3 to 5 places over 4 to 11 distinctions, unused distinctions dropped; the draw's procedure is the engine's own, recorded with its seed in the result note: P0 needs agreement, not these 600); the structures of the controls of the readings (D 3.6); the 60 third-pattern starts | no readings: MET, STEPS-1 under COPY-LAW(t) and CAP-3(t); the readings on the drawn structures; COPY-LAW(t) with no taking rule on the two-knot start; (CAP-3, CANCEL-OFFSHOOT, RELEASE) with MET(OLDEST), parity, before the placing by hand | 6; 7 for the controls of the readings on the two-knot start; 3 before the placing by hand | P0; ties against brute force on every drawn structure; sameness and renamings of Y's knots against brute force on drawn structures with a stated pattern (a part of the roster of the drawn structure after one round under COPY-LAW(CANCEL-OFFSHOOT) with MET(OLDEST), parity, and its knots) and stated candidates (every knot made in that round); the controls of the readings (P14); tie classes at round 0 of the third-pattern starts (P2) |
| R | record_structures.json | none | none | the record check for the owner's step 2 (P4) |
| 1 | two-knot, three-knot, Ring(5, 3) | COPY-LAW(t), CAP-3(t); no taking rule, Q, MET, STEPS-1, STEPS-2 × four rules; FBP(t) | 8 | N(t) per round; the fresh count of every birth (P1, P3) |
| 2 | made-2 to made-6, made-2-exchanged, ystart-<kind>; X alone; Y alone | the nine base laws; MET and STEPS-1 × four rules | 6 (8 for the two-users reading on a case) | runs A, B(i), B_X, M, M′, M_Y, M′_Y, X alone, Y alone; the three readings by descent at every round; the replacement runs; the fourth mark; the owner's arm (D 7.1 to 7.7, 7.10); verdicts |
| 3 | the pairs of the pair starts (D 4.8) | COPY-LAW(t), CAP-3(t); STEPS-2, MET and STEPS-1 × four rules | 7 | as run 2 without the replacement runs, X alone, Y alone and reading (iii); in run 5 its cases are swapped under n1 and n4 only (n4 drawn with the pair start's name), unless starts.json lists more |
| 4 | made-2 to made-6; ystart-<kind> | parity (and, on made-2, not-all-equal); COPY-LAW(t), CAP-3(t); MET with every choice (D 2.7); the registered take lists replayed | s + 1 to s + 4 | whether some history has two of a place of Y made by X, every knot passing; the counts under the take-by-take weighting of histories with two loose made distinctions tied to one place, by who made them and whose place it is (P9); on made-2, under both knot laws, the counts of (X's state, Y's state) at round s + 4 (PO8) |
| 5 | every case of runs 2 to 4; every run of the form arm | each case: the other rules, the other base laws, n1 to n4, the order of births reversed, demand before the takes, HOLD, STEPS-1 for MET and back, the knot law; on every values case of the designs with Y present from round 0, reading (iv) (D 7.8); the form arm: n1, n3, n4, order reversed, demand before the takes, HOLD | as the case's run | whether the case survives, with its verdicts; reading (iv); the form arm's counts under each swap |
| 6 | every not-all-equal run of runs 1 to 5 | as run | as run | every tie class containing a made distinction (P2) |
| O | made-2 to made-6; ystart-<kind> | FLOOR0 and ONE-FEWER × three treatments; MET and STEPS-1 × four rules; at most 300 knots | 5 | changed by births descended from Y only (D 7.9); the knot test at that round (PO2); under not-all-equal, every tie class containing a made distinction (reported) |

## Predictions

Marked: (a) seen in the drafter's scratch runs and predicted; (b) a hand prediction not run; (c) reported, with no
prediction; **check**: true by construction; **replication**: a count seen in the prototype that an independent engine
is expected to reproduce, where **a miss is a finding about the engines, not about the claim**, replayed birth by birth.
No clause is registered that the registered runs cannot decide.

| # | Prediction | Fails when |
| --- | --- | --- |
| P0 (check) | The gate: with no readings the engine's runs equal the fold engine's (shared growth code: this tests only the wiring); the tie classes agree with brute force on the 600 drawn structures; sameness and renamings of Y's knots agree with brute force on the stated drawn cases. | any differs |
| P1 (check; S4) | Under COPY-LAW(t) with MET or STEPS-1 (not FBP(t)), every birth other than an offshoot of a start knot receives exactly one fresh distinction, or none under parity when implied; under STEPS-2, the same except also offshoots of knots whose parents are all start knots. | another count |
| P2 (check; S2) | Under not-all-equal, in every run and history under the nine base laws (run O apart, where S2's hypothesis fails; its tie classes are reported), no tie class contains a made distinction; and the 60 third-pattern starts have no tie at round 0 under either knot law (S6 does not cover them). | one does |
| P3 (a) | Run 1: under COPY-LAW(t) and CAP-3(t), with Q, MET, STEPS-1, STEPS-2, no part the same as the two-knot part in the roster after any round t ≥ 3 (the two-knot start's round-1 pair and STEPS-2's round-2 copies are the only ones). With no taking rule, the counts of starts.json ("counts for P3"), round by round. | one exists, or a count differs |
| P4 (check; the owner's step 2) | The record check on record_structures.json: the cut statements for parity with two holders, no tie for not-all-equal with two holders, the Fano piece's tie, and the counterexample to "any start". | any fails |
| P5 (check; S4 and item 5) | Under COPY-LAW(t) with MET or STEPS-1, every part the same as a member of 𝒴_made or 𝒴_start that contains a member made after round s has as its made members offshoots of start knots (seen: under STEPS-1 on ystart-one-3, Y's own three round-1 offshoots); and no renaming of Y's knots is among the made knots. | otherwise |
| P6 (a) | Values, stated rules, made-2 to made-6 and the six designs with Y present from round 0: exactly one design, law and rule has two usable loose made distinctions tied to one place of Y made by X: ystart-three-222, COPY-LAW(CANCEL-OFFSHOOT), MET(NEWEST), parity; the two descended from X only, tied to a place of one of Y's members. (Names in the replay listing: 52, 53, 16.) (made-2-exchanged: reported.) | another design, law or rule has such two, or this one has none |
| P7a (a) | P6's case survives demand before the takes and HOLD. | it does not |
| P7b (a) | P6's case is lost under each of the other three rules. | it survives one |
| P7c (a) | P6's case is lost under each of the renamings n1 to n4; so it does not hold "under a stated rule". | it survives every one |
| P7d (c) | P6's case under the other base laws, FBP(t), STEPS-1: reported (seen: lost under each). | not applicable |
| P8a (a) | The registered take lists replayed: each gives the two of take_lists.json, at its round, every knot passing. | a take list does not |
| P8b (c) | Every choice: which designs have a history with such two, under each base law, with the counts under the take-by-take weighting (seen under COPY-LAW(CANCEL-OFFSHOOT) for every design in 5,000 draws; none under CAP-3(t), where three designs are mostly stopped by the guard). | not applicable |
| P9 (c) | Under the take-by-take weighting (20,000 histories per design, COPY-LAW(CANCEL-OFFSHOOT)), the histories with two loose made distinctions tied to a place of Y, made by X, and those tied to a place of X: reported per design and pooled. | not applicable |
| P10 (a) | The knot test, in runs 1 to 5: under not-all-equal no knot fails; under parity knots fail only at joins (seen: two joins of twelve parents, CAP-3(CANCEL-WAIT), MET(NEWEST); under every choice, joins with three or four inputs and one fresh distinction); offshoots never fail (check); the two parity methods always agree; every case counted passes. Run O's knots are PO2's. | a knot fails elsewhere, or methods disagree |
| P11 (a) | C(r, b) fails for each of the four rules and each base law, X made and X a start pattern (seen: one member of 𝒴_start under NEWEST and COPY-LAW(CANCEL-OFFSHOOT), lost under renaming; none of 𝒴_made). | C(r, b) holds for some r and b |
| P12 (a) | CF(r, b) fails for each rule and base law, under MET (seen: one case, made-4 under FBP(CANCEL-OFFSHOOT) with MET(BY-COUNT): there with this Y and not in X alone, not a copier for any other member, lost under renaming). Under STEPS-1, reported (seen: two cases that are X's own course). | CF(r, b) holds for some r and b |
| P13 (a) | The form classes by the engine's census: its laws make parts the same as made-3, made-4, made-5, made-6 in the made family, and as one-2, one-3 and three-222 in the other, never as two-23 or two-33 there, which are dropped. The census by descent from X only is reported. | otherwise |
| P14 (check) | The controls of the readings (D 3.6): on the two-knot start with no taking rule the form reading and the built-structure reading in counting mode equal N(t) at every round 2 to 7 under the three treatments; the part and the knots placed by hand are each found, one more. | either fails |
| P16 (check; B3) | Any form case made by X only that meets condition 2 shows the fourth mark on the parts by descent on its replacement runs (true by definition). | one does not |
| P17 (c) | The fourth mark on the replacement runs, on the renamed trace and on the parts by descent: reported (seen on the trace: 164 of 864 made-X pairs, 203 of 1,440 start-X pairs). | not applicable |
| P18 (c) | X alone: X's course with Y never there against run A, on the traces renamed by first appearance: reported (seen: differs in every MET run, because the shared distinction 0 or e is barred in X alone; under STEPS-1 in 216 of 432 made runs and in none with Y present from round 0). | not applicable |
| P19 (c) | The second pattern handing on its own value, and Y returning: reported (seen: 9 parity runs, the same with X barred). | not applicable |
| P20 (a) | The smallest second pattern in the registered class that P6's case fails on, members first, then places, is one member holding two (this follows from P6). Its two clauses: in round 3 all three takes of births descended from X only take Y's fresh distinction (17); after round 6 X's three usable loose made distinctions are tied to three different start distinctions (e, 7 and 5). | another smallest, or a clause fails |
| PO1 (check; B1) | Under COPY-LAW(t), CAP-3(t) and FBP(t), in every run, the allowed states restricted to the whole set of distinctions held by X and its descendants after a round are the same after every later round (parity: the rank of the set's columns over a basis; not-all-equal: the number of assignments that extend, by a solver, over the whole set when it has at most 12 distinctions, otherwise the 12 with the smallest names, reported so); and no birth without a parent among X's members takes a usable loose distinction of X. | either fails |
| PO2 (a; B1's edge) | Run O: in every run in which the relation on D0 is changed by births descended from Y only (D 7.9), some knot fails the knot test at that round (seen: 68 runs, all under parity and STEPS-1, every one with a failing knot). | such a change with every knot passing |
| PO3 (replication) | The courses (D 7.4), as in the owner's arm, C.1: X's course differs with Y barred in 652 of 1,728 runs, 560 through a meeting; Y's with X barred in 457, 357; and by family and base law as in its table (made-3 to made-6: COPY-LAW 24 (24), CAP-3 96 (96), FBP 72 (72); five members with Y present from round 0: 10 (0), 120 (90), 108 (78); made-2 and made-2-exchanged: 28 (24), 72 (72), 72 (68); two-22: 2 (0), 24 (18), 24 (18)). On run 2's designs without made-2-exchanged this gives, per base law, 50, 276 and 240 of 528 (version 2's P15). | a count differs |
| PO4 (replication) | Takes against the course (D 7.5): of X's 560 differences through a meeting, no take either way in 370, the first take in the same round in 60, after it in 126, strictly before it in 4; of Y's 357: 240, 40, 62, 15. | a count differs |
| PO5 (replication) | Reading (ii) has exactly these 3 runs: made-4, CAP-3(CANCEL-OFFSHOOT), MET(BY-COUNT), parity (T = 5, run A's next round stopped by the guard; X ends at round 4 by an implied join; not by round 5 with Y barred, where it ends at round 6; through a meeting); ystart-two-22, CAP-3(CANCEL-RETIRE), MET(IN-TURN), parity and not-all-equal (X ends at round 3, its members retiring; not with Y barred; through a meeting). | another case, none, or a listed one differs |
| PO6 (replication) | The reverse of reading (ii) has exactly these 9 runs, all through a meeting: made-3, CAP-3(CANCEL-RETIRE), MET(NEWEST) and MET(BY-COUNT), both knot laws (Y ends at round 4); ystart-three-222, CAP-3(CANCEL-RETIRE), MET(OLDEST) and MET(IN-TURN), both knot laws (Y ends at round 3); ystart-one-2, COPY-LAW(CANCEL-OFFSHOOT), MET(NEWEST), parity (Y ends at round 2). | otherwise |
| PO7 (a; B2) | The control with Y the same as X: on made-2 and on made-2-exchanged, X and Y end in the same round in every run; takes in one direction only exactly under MET(NEWEST) with offshoots (X from Y, under each base law) and FBP(CANCEL-OFFSHOOT) with MET(BY-COUNT) (Y from X), both knot laws, the same in both namings. | otherwise |
| PO8 (check where every history is read; replication under offshoots; B2) | Run 4 on made-2, both knot laws: where every history is read (retiring, waiting), the counts of (X's state, Y's state) at round s + 4 are unchanged when X and Y are exchanged. Under offshoots, the drawn counts are reported with their exchange (seen in version 1: equal in 2,000 draws per law). | where every history is read, they change |
| PO9 (c) | Reading (iii) and its reverse (D 7.7): reported (seen: 70 runs and 8, owner's arm C.3). | not applicable |
| PO10 (c) | Reading (iv) (D 7.8) on every values case of the designs with Y present from round 0: reported (seen: on the stated-rule case it holds for each of the 5 kinds of Z named before Y and for none named after; on the 18 take-list cases for none, the list not applying in 26 of 180 runs). | not applicable |
| **POA (the owner's, A248)** | The owner's inkling, in his words: "it's actually impossible to generalize a 'copier' for all logic structures. It might be the case that some logic models are able to over-write the instructions of the copier and break out." (i) C(r, b) and CF(r, b) fail for every r and b (P11, P12): **overturned** for a registered class by one first pattern, law and rule that is a copier for it; **only supported** by failures, since the classes are finite and "all logic structures" is not; reported in two parts, no copier at all, or a copier for some members of the class and not all (both defined in the owner's arm, A). Readings (ii) to (iv) (PO5, PO6, PO9, PO10) are reported and are never called support for his second sentence. The plain sentence for each outcome is in the owner's arm, section D. Seen: (i) no copier at all. | (i) a copier for a whole registered class |

A result that fails is reported as it is. P1, P2, P5, P16, PO1 and PO8 check arguments on finitely many runs; the result
note states the arguments for the referee.

## Runs and stop rule

- One engine is written from this text, the definitions and the data files, extending the fold engine. It passes P0 and
  P14 before any other run; the take lists are replayed (P8a) before run 4's draws.
- **Stop, in the owner's words**: "Stop at a pattern that leaves two of what it met, with the class it works for, or at
  a reason no made pattern can under that law."
- **As read here**: stop when, for each reading and each knot law, under MET with both base laws (and STEPS-1, STEPS-2),
  there is either a first pattern with the class for which it is a copier (D 5.1) and its three verdicts, or a reason no
  made pattern can (S2 for not-all-equal; S4 for COPY-LAW(t) in form and built structure), or, where neither is reached
  (values under parity; form under the form arm's laws), the bounded report listed under "What a result would and would
  not show"; and every registered run has been made and every prediction has a verdict.
- **Disagreements** with the disclosed prototype are replayed birth by birth (parents, inputs, holders of each input,
  fresh count, tie classes, descents); the listing decides, and the disagreement is reported as a finding.
- **Resources.** Each run is expected to take under ten minutes and 8 GB on one process; anything longer goes through the
  shared runner with a row in the long-running index.
- **Deviations** are recorded in `deviations.md` in the experiment family before the affected run.

## What the advisor's passes changed

Three passes by the advisor model, each on the whole text as it then stood; the questions and answers are in
[the advisor folder](../MADE-COPIER-20261125-001/advisor/README.md).

- **First pass: "freeze after listed changes".** Both rations became primary under the taking rule; reading two parts the
  same as the second pattern got an arm of its own under the base laws where the one-fresh-distinction argument fails;
  both "cannot hold" statements were reworded (the ration's doing; "tied", from a start with no tie); "fewer than two
  with the second pattern barred" stopped being a condition for values; the claim was stated once for each rule fixed
  beforehand, apart for a made and a start first pattern, and predicted to fail; verdicts became three questions; no new
  noun was kept. The drafter's account: `advisor/changes_after_first_pass.md`.
- **Second pass: "do not freeze yet".** The owner's arm was registered with its runs and listings; his inkling's second
  reading was renamed neutrally and is never called support, and two sharper readings were added; "ended" became the
  shared definitions' own; the statement that nothing a pattern holds is changed was corrected; the base law was fixed
  for a whole class; the classes were set by family; everything the engine's author needs was written into the
  definitions and the data files. The drafter's account: `advisor/changes_after_second_pass.md`.
- **Third pass: "freeze", with sentence-level fixes**, all applied: the scope of two checks, rounds for three conditions,
  a definition of "a copier for some members and not all", a corrected sentence for the owner's step 2, the plain
  sentences for the owner, and words. The drafter's account: `advisor/changes_after_third_pass.md`.

