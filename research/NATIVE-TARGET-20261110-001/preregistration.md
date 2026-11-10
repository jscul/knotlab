# Pre-registration: a native target for learning

Epic `NATIVE-TARGET-20261110-001` (backlog B61, G15), written on 2026-11-10 before any native rule is run, at the coordinator's
go-ahead. Only a construction fact was looked at first: on every thin torus tested, every line and every face constrains three
consecutive slices of the chain of `COUNT-SURFACES-20261107-001A` theorem 5.3.

## The setting

The class-forced tori and least states of `LEARN-HANDLES-20261109-001A`: the two Fano tori and the 57 thin tori of even index up to 40
points, a Kasteleyn law in the class no state satisfies, and a state x with one violated line l0 and one face w0 of deg 3. The learner of
A26 holds x fixed. After the split at l0 (one sign change), each learning step moves a hole along one of the three lines at it, and a hole
that enters a face of deg ≥ 2 is absorbed. In `LEARN-HANDLES-20261109-001` the rule that resolved every start was told the graph distance
to w0 by the experimenter. That distance is the outside input B61 asks to remove.

## What counts as supplied by the law and the state (frozen)

A signal is **native** when it is computed from the current law s and the fixed state x alone: from their dissonance (violated lines,
⌊deg/2⌋ at each face, even faces), from the states the law allows, or from the learner's own possible moves. A signal is **outside** when it
uses a metric or coordinates of the triangulation, or a target that the experimenter names. No native rule is told which face is w0; it
can recognise an over-agreeing face only by its deg, as dissonance it sees. (A47 records this reading.)

## The rules

- **R0, random.** Uniform among the three moves. The baseline.
- **R1, R2, R3, sight of radius r.** The learner looks at every sequence of at most r of its own moves from the present configuration. If
  one ends by entering a face of deg ≥ 2, it takes the first move of a shortest such sequence; otherwise a random move, never straight
  back unless forced. Native and local.
- **R4, the most states.** For each move, N is the number of states y that have the same dissonance as x under the law after the move:
  the same violated lines and the same ⌊deg/2⌋ at every face. The rule takes a move with the largest N, ties at random, never straight
  back unless forced. Native and global: A27 weighed by the state's own dissonance.
- **R5.** R4 with sight of radius 1: a move that absorbs is taken when there is one.
- **R6, control.** As R4 with the smallest N.
- **R7, reference.** `LEARN-HANDLES-20261109-001`'s rule with the outside distance.

Budgets: 50 V² steps for R0 to R3 and R7, 20 V for R4 to R6. Starts: for R0 to R3 and R7 those of `LEARN-HANDLES-20261109-001A` check 5
(every least state up to 200 per torus, on all 59 tori, with its seeded split); for R4 to R6, 50 of those starts on each of the two Fano
tori and the 19 thin tori torus(N, 1, 1), N = 4 to 40 even. N is counted exactly: by enumeration up to 20 points, and on thin tori by a
transfer matrix along the chain, checked against enumeration up to 20 points.

## Expectations, frozen

- **F1 (sight).** R1 to R3 resolve every start, with mean steps below R0's on every torus of at least 10 points, falling as r grows.
- **F2 (entropic attraction).** Same charges repel on the sphere (`RESIGN-STEER-20261107-001`); a hole and w0 have opposite charges, so
  they should attract: N grows as a hole nears w0. Then R4, or R5 if R4 hesitates to absorb, resolves every start, with mean steps below
  R0's on every torus of at least 10 points. Diagnostic: along R0's walks, N against the hole's graph distance to w0, measured by the
  experimenter and given to no rule; expected to fall with distance on average.
- **F3 (control).** R6 is slower than R0, or fails on some start.

## What would count against them, and the answer to B61

R4 and R5 stalling on some start within 20 V, or N not falling with distance, counts against F2: the entropic signal would not steer, and
the answer would rest on sight alone. R6 doing as well as R4 counts against F2 too. A sight rule failing a start counts against F1.

B61's stop rule: **yes** if a native rule resolves every start and beats R0's mean on every torus of at least 10 points, naming which;
**no** if none does.
