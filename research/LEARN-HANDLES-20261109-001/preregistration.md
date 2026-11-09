# Pre-registration: learning in handles

Epic `LEARN-HANDLES-20261109-001` (backlog B6, G15 with G4), written on 2026-11-09 before any learning walk on a torus is run, after the
owner asked whether the learning line had been left. Only constructions were looked at first: the list of thin tori of even index up to
40 points (57 lattices) and the satisfiable classes of the two Fano tori, both already in `COUNT-SURFACES-20261107-001A`.

## The setting

The knot spaces on lattice tori T(L) of `COUNT-SURFACES-20261107-001A`: every face has degree 6, the all-zero signing has no even face,
and the four sign classes are the twists. The **class-forced** laws are the classes no state satisfies (theorem 5 there): the untwisted
class of the two Fano tori, and the one missing class of each thin torus of even index up to 40 points. Degenerate tori, whose lines
repeat a point, are left out. In such a law the count forces nothing (violated lines − E = 0 in every state), yet no state satisfies
every line, so every state also over-agrees somewhere: its dissonance is a pair of opposite charges.

The learner is the one of `RESIGN-STEER-20261107-001` (A26): the state x holds still, and each step changes one sign, on a side of a
violated line or on a side with an end at an even face. The dissonance is **resolved** when no line is violated, no face over-agrees and
no face is even.

## Expectations, frozen

- **E1 (least states).** Every class-forced law has states with exactly one violated line l0, and in each of them exactly one face w0
  has all three corners agreeing. Proved for the face from the count; computed for the line (all states up to 20 points, SAT beyond).
- **E2 (learning resolves the pair, and must wind).** From every least state learning resolves the dissonance: one re-signing at l0
  splits it into two holes (even faces with no agreeing corner), and moving each hole along lines that agree where it goes, until both
  have entered w0, ends at a perfect matching of the lines with the faces. Every perfect matching is reachable, so every other class is
  reached. The sign change of every resolving walk is a cycle of T whose homology class is not zero: the law ends in another class with
  no even face. Expected to be proved by hand from theorems 2 and 4 of `COUNT-SURFACES-20261107-001A`, and checked by replaying walks
  as sign changes from every least state up to 20 points and from up to 200 sampled ones beyond, into every other class, with the
  change's holonomy equal to the difference of classes.
- **E3 (the sphere is different).** On a sphere the forced dissonance can be moved into the law but never resolved: it stays as two
  even faces (`RESIGN-STEER-20261107-001`). On a class-forced torus resolution leaves nothing local, and the only trace of learning is
  the class. Proved from the count.
- **E4 (cost).** A resolving walk needs at least as many re-signings as the shortest cycle of T in the class change it makes (proved,
  since its sign change is such a cycle). Computed, exploratory: the cheapest walk found into each class, against that systole.
  Expectation: within a few re-signings of the systole for the cheapest least states, growing with the separation of l0 and w0
  for the others.
- **E5 (a local rule, exploratory).** The rule sees only the three lines at a hole, where each agrees, and the graph distance to w0
  supplied from outside (A26), and never steps straight back; it moves the nearer hole into w0, then the other. Expectation: it
  resolves from most least states, and where it fails the second hole circles because the short way into w0 would close a loop that
  does not wind. Unbiased random moves resolve with probability 1, since the moves are reversible and resolution is reachable; their
  mean number of steps is recorded.
- **S (the sphere's local rule, one size past).** `RESIGN-STEER-20261107-001B`'s no-reversal rule, 300 random targets each, on K_14
  and K_16 (budget 40 m) and on the non-octahedral test spheres of `steer_lib` (two tubes, three grown spheres, four branched double
  covers; budget 20 ⌈√V⌉), failures rerun with ten times the budget. Expectation: at least 95% reached on each, as on K_2 to K_12.

## What would count against them

A class-forced law whose least states have two violated lines (against E1); a least state with no resolving walk, a resolving walk
whose change does not wind, or another class not reached (against E2, and against theorem 4 unless the check is wrong); a walk cheaper
than its systole (impossible, so a bug); a local rule that resolves everywhere at every size (winding would then be free locally) or
nowhere beyond the Fano tori (against E5); a sphere where the no-reversal rule reaches fewer than 95% of its targets (against S, and a
narrowing of the published "a local rule suffices" line, to be logged as a correction).
