# The advisor's answer to the coordinator on next directions (claude-fable-5-2, extra-high effort); direction 3 is this study

**Read this first: the state you gave me is out of date in three places.** [read]

- **"At most one two-valued fact held by the whole" is Blocked.** The layers referee built a connected nine-knot start that gains two independent facts in one ordinary round, found a sampled ten-knot one, and built starts keeping three and four (`research/LAYERS-20261126-001/referee-R1/report.md` lines 4, 16, 18). It is logged at `docs/CORRECTIONS.md` line 230.
- **The recursion study has a referee report its decision does not show.** `research/RECURSION-LEAD-20261126-001/referee-R1/report.md` is "Refuted", with a Block on the one-fact claim, while `decision.md` line 5 still said "referee pending" and item 1 was unchanged when I read it. Fix 3 of the report: two recorded rival cuts can make a pin collectively (census entry 1590), so "which no recorded law does" is false as worded.
- **The scoping study on signed counts is closed and refereed.** The mixture identity is confirmed; "only squared readings cancel" is Blocked (`research/SIGNED-COUNT-20261126-001/referee-R1/report.md` lines 2, 18–22).

A study on binding (`research/BINDING-20261126-001/`) was frozen and running while I read; direction 1 bears on it directly.

Nothing below was run. "By hand" means my argument, `unverified`; "read" means I opened the file at the place cited.

## (1) Three directions

| # | Direction | Payoff | Concreteness |
| --- | --- | --- | --- |
| 1 | A next-layer parity knot made by the knots' laws, and closing as the growth's own reading of it | 3/3 | 3/3 |
| 2 | Finish and prove the reading of ordinary growth from the start's map | 3/3 | 3/3 for the test, 1/3 for the proof |
| 3 | One statement that classes every recorded excess | 2/3 | 3/3 |

### Direction 1: a knot on whole-held facts

**A built start to test (by hand): 14 knots, 31 distinctions.**
- Three rings i = 1, 2, 3 of four knots a_i, b_i, c_i, d_i in that order.
- b_i and d_i hold two loose distinctions each.
- a_i holds none, and one more shared distinction t_i with a joining knot J.
- c_i holds none, and one more shared distinction u_i with a second joining knot K.
- J holds t_1, t_2, t_3 and v; K holds u_1, u_2, u_3 and v; neither holds a loose distinction.

**Predictions (by hand).**
1. The laws of the eight knots without loose distinctions sum to the parity of all twelve ring distinctions, so z_1 + z_2 + z_3 is forced. Each z_i is free alone: it equals the parity of the loose distinctions of b_i and d_i, up to a constant.
2. The shortest change through each distinction has size two, four or five, and each is even on every ring:
   - two: the two loose distinctions of one knot;
   - four: two ring distinctions at a_i or c_i with one loose at each of b_i and d_i, or the whole ring;
   - five: t_i, v, u_i and two ring distinctions through b_i or d_i.
3. The least change odd on a ring has six distinctions (t_i, t_j, and one ring distinction and one loose in each of two rings).
4. So there are four classes with labels z_1, z_2, and z_3 is bound to them. No single knot reads any z_i, and no single-knot parity is a label, so both bits survive the quotient by single-knot reads. The same holds under "every change of at most five".

This is an element of the binding study's space B that splits into three carriers, which is exactly what its frozen prediction says does not occur (`BINDING-20261126-001/README.md` lines 27–30, 50–51). Its frozen sets stop at eight knots, and I could not make a smaller one: the alternation needs even rings, and a ring of two is read by one knot. A "none" from that run is therefore not about the model, which is the lesson logged today at `CORRECTIONS.md` lines 245–246.

**The same thing with no move rule.**
- The sum of all knot laws leaves only the loose distinctions; the recursion referee uses this (its report, line 17).
- Where live parts are joined only through knots without loose distinctions, that sum is one parity law whose places are the parts' loose parities (by hand).
- The growth already reads it: a finished piece's top is not implied while another piece grows, and a lone piece closes (`RELAY-IDENT`, confirmed; `research/DOUBLE-IDENT-20261119-001/line_summary.md` line 68).
- One far loose distinction turns a birth of three places with no fresh distinction into one of four places with one, at route lengths 4, 5 and 9, under parity only (`research/INFLUENCE-CONE-20261120-001/guards.md` lines 3, 20–25; referee pending).

**First step.** Run `binding.py` and `forced.py` on the built start at rounds 0 to 3 under both readings. Then, on a start with three live parts, test K1–K3 on the relation among the parts' parities with the canonical checker, with no value defined as a sum. Test whether a part's top is implied exactly when the others hold no loose distinction, with not-all-equal as the control.

**Stop.** Any of predictions 1 to 4 fails (report which). Or all hold and closing follows the binding; then freeze it as a second-layer knot and referee it. The next question is whether growth ever makes such a set of knots from a start without one. Round 2 is the first round it could, and the binding note has B growing through born knots on start 7-239 (lines 38–40).

### Direction 2: the reading from the start's map

**What the record has.**
- 705 of 706 uniform six-knot starts agree in every round, and the study's own swap audit says the agreement is about the model (`research/LATE-VIEWS-20261126-001/decision.md` lines 10–17, 56–59; refereed).
- A graded-order reading found afterwards fixes the 40 failures; it is post hoc and untested (lines 22–25).
- The reading that was refuted (a view on demand) was run instead of this one.

**Why it serves the aims.**
- It is the route to simulating.
- It is the only handle on dimension outside the proved class; inside that class three never occurs in the samples read (`line_summary.md` line 70, read, not rechecked).

**First step.** Freeze the graded-order reading. Test it on fresh seven-knot starts in the stratum where cells share a knot, on the two unexplained starts, and on the eight-knot built start that missed.

**Stop.** A miss (find the exception, which gives the statement to prove), or none (write the statement and hand it for proof).

### Direction 3: one statement for the quantum question

**The statement to write.** For laws that read no values, every table is one of three kinds:
- (a) separate responses with each setting birth multiplying an old word's weight by its number of completions, which is a local model with partial rejection;
- (b) a response depending on both settings (a shared birth or a whole-round event), which signals once the sender may condition on what it sees;
- (c) a supplied order, sign or reading.

**What supports it.**
- The forbidding referee already notes that a rejection representation can come from positive completion counts (`research/FORBID-EDITS-20261126-001/decision.md` lines 16–18).
- The third-holder ceiling 4(1 + ρ²)/(1 + ρ)² is 2 at ρ = 1, 20/9 at ρ = 2 and tends to 4 (by hand, from the formula at `research/THIRD-HOLDER-20261123-001/decision.md` line 52). Those are the values with no reweighting, with a three-place not-all-equal birth's one or two completions, and with outright rejection.

**First step.** Class every row of the two-countings table and the 9/4, 7/3, 5/2, 104/45 and 61/30 cases.

**Stop.** All are classed (the quantum line then stops on the recorded laws with its reason in one place), or one fits none, and that row is the lead.

## (2) How each fails, and a quick check

**Direction 1.** A referee will say it is the sum of the laws, and that the binding belongs to the start: growth gives old carriers no new relations (binding note, item 1). Three controls on the built start separate a law-made binding from bookkeeping:
- Remove v. The shortest change through t_i then crosses rings, and the labels should vanish.
- Give J one loose distinction. The binding should vanish and leave three free bits.
- Run the "at most five" reading. The referee's own witnesses keep no facts under it (binding note, lines 41–42), and this start should.

Under the shortest-change rule I also expect the labels to merge at any round where one ring's part holds exactly one loose distinction (by hand).

**Direction 2.** The reading may not be a function of the start's valid sets where parity's closing enters, since closing is decided by the whole presentation. Pieces with a cycle are not predicted at all (`LATE-VIEWS` decision, line 27), and every start today's class studies care about has one. Quick check: work the two unexplained starts and the eight-knot miss by hand before freezing; if the graded order does not fix the eight-knot start, it fails with size.

**Direction 3.** The third-holder proof may not be the rejection argument: I read the formula, not the proof. The 9/4 parity tables are also hidden under both countings with fixed addresses, so they fall under (b) only through the register's definition of a free sender. If fixed addresses count as settings, the record already holds an excess without signalling that has no quantum realization. Quick check: read the proof's hypotheses against the forbidding argument, and state the sender definition in the statement.

## (3) Lines to stop

- **Every search for a sign or a sum over histories:**
  - `FOLD-SIGN` direction 1;
  - `BEYOND-REJECTION` directions 1 and 2 (its inventory was Blocked, so the frozen test confirms a note that no longer stands);
  - `TWO-CLASS-SIGN` direction 1;
  - `SECOND-CHECK` direction 2;
  - `SIDE-SIGN` directions 1 and 2 (tests of supplied readings);
  - `SIGNED-COUNT` direction 1.
- **Forbidding:** `FORBID-EDITS` directions 3 and 4, and `CONTACT-FORBID` direction 2.
- **The exchange:**
  - `RECURSION-LEAD` direction 1. Its referee replayed the free exchange under both rival cuts on all 5,528 funded starts and found no return (report, line 29).
  - `RECURSION-LEAD` direction 2. The referee gives the pins (line 17).
- **`LAYERS` directions 2 and 3.** The referee gave the split and a simpler test for 2 (report, line 32); 3 was run.
- **`BOTH-LONG` direction 1.** The layers referee answered it: the ring labels take all four joint values.

Keep the local direction of `LAYERS` (now "Continue"), `LATE-VIEWS`, and the owner's `TWO-PATTERNS`.

## (4) What today's studies overlooked

- **The squared-weight chances are already counts.** They equal counts of pairs of ordinary words with no negative weight; what is supplied is the read of a change and its calibration (`research/FREEDOM-CLOCKS-AND-BIRTHS-20261120-001A/results.md` lines 3, 15, 19, 21; referee pending). None of today's nine sign and forbidding studies cites it (grep of their top-level notes). So "the missing piece is a sum with cancelling weights" should read "a reader's question about a change".
- **Closing as a whole-presentation event.** No class, tower or exchange study cites `RELAY-IDENT`, `INFLUENCE-CONE` or `GENERATORS` (grep of eleven notes and decisions: zero).
- **A recursion lead under ordinary growth.** A released product that is itself a source is proved under both laws (`research/GENERATORS-20261120-001/nested.md` lines 9–11), and the sub-goal on emitting the same finite thing has waited since 20 November. Its caveat is its own: the second level depends on the observer's two-scale test.
- **The same law at every layer.** Composition is answered: two parity knots sharing a distinction compose into a knot (`docs/RESEARCH_GOALS.md` lines 1960–1965). That is the one form of recursion the record can already state.
- **Parity only.** Every class, tower, exchange and binding study today is under parity. Under not-all-equal moves were searched to size four within two holder steps. The literature's names for the question are clustering of solution spaces and frozen variables.

## Hivemind and limits

I added one consultation entry and two standing facts (closing decided by the whole presentation; chances as pair counts), both marked `unverified` as read at the cited lines.

Not checked:
- The growth engine itself. The rule for spare loose distinctions I took from `guards.md`.
- That a distinction never has more than two holders. I read it as a lawfulness test in the recursion referee's report, not in the code.
- The third-holder proof.
