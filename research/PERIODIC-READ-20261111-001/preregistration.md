# Infinite bases with periodic overlap: pre-registration

Epic `PERIODIC-READ-20261111-001` (`OVERLAP-READ-20261111-001` directions 1 and 2; G1, question 9; program topology, group
spacing), 2026-11-11, at the coordinator's go-ahead under the owner's standing mandate. Frozen before any registered run. The
canonical K1–K3 test is unchanged. What such bases compute belongs to the learning line.

## Words

As in the guide's glossary (`publication/knotlab/INTUITIONS.md`): knot, distinction, shared distinction, **meeting pattern** (which
knots share which distinctions), **knot pattern** (the knots with their rules and their meeting pattern), **base** (a knot pattern
with a state), co-knotted pair, two-fold weave, hollow triple, bond, bond distance, world (an allowed state). From
`OVERLAP-READ-20261111-001`: a **tied pair**, a **frozen** distinction, an **unnamed hollow triple**, and a base read **faithfully**.
New here, by construction and counts:
- A **periodic knot pattern** repeats under every shift by an integer vector z of Z^d (d = 1 or 2): it has k kinds of distinction,
  one distinction (v, z) of each kind v at each shift z, and finitely many kinds of knot, each naming three (kind, shift) pairs, with
  one knot of each kind at each shift. Nothing limits how many knots lie on a pair. It is infinite: its distinctions are all (v, z).
  (Literature: a periodic 3-uniform hypergraph, the lift of a finite one by integer voltages.)
- A **finite repeat** is the pattern taken modulo a sublattice of Z^d: a finite knot pattern whose states are exactly the periodic
  states of the infinite one with that period. (Literature: a periodic quotient.)
- The **window** of radius R is the finite knot pattern of the distinctions with shifts in [−R, R]^d and the knots inside it.
- The **unit** at shift z is its k distinctions.

## The question

Which infinite bases with a periodic meeting pattern does the not-all-equal law (NAE) read faithfully, with how much overlap, and what
does an infinite base show that its finite repeats do not? Beside it: what are the global hollow triples of `OVERLAP-READ-20261111-001`?

## What is settled by definition, and what the infinite base adds

- **A pattern on a finite set S extends to a state of the infinite base** if it extends in some finite repeat in which S stays
  distinct (a periodic state lifts), and does not if it fails in some window (compactness); between the two it is unsettled. Every
  verdict below says whether it is settled.
- **Along one shift (d = 1) the reading is exact by a finite computation.** The pattern is a one-dimensional shift of finite type
  (literature), and a window of radius R > max|z in S| + 2^(k·span) + span decides it: past S, a path through the de Bruijn graph
  longer than its nodes repeats a node and can be continued for ever. So the one-shift family F1 checks the code, not a question.
- **Along two shifts (d = 2) the reading is only bounded.** Whether such a repeating rule has any state is undecidable in general
  (Berger 1966, for two-dimensional shifts of finite type), and states may never repeat. A third bound helps: a pattern repeating in
  one shift only (period m in one coordinate, infinite in the other) is again exact along the other by the same window argument, and
  its states are states of the infinite base.
- **What the infinite base shows that its finite repeats do not.** (1) States with a junction between two repeating regimes
  (literature: a domain wall): some value patterns occur only there, never in a finite repeat. (2) No short unfilled cycles: a finite
  repeat's short cycles can bind sets the infinite base leaves free, as six-regular one-pair weaves of small edge-width (literature)
  did. (3) Source labels: a distinction is native at a state when some change of finitely many distinctions flips it, which only an
  infinite base can fail. (4) Balls that grow without end.

## Disclosed before freezing

Pilots outside the registered run, code in the scratchpad:
- **F1 (one shift):** 181 patterns, every reading settled; 73 read faithfully, 23 of them with a pair in three or four knots; six read
  faithfully at infinity although none of their finite repeats (n = 3 to 15) is; 72 of 77 faithful patterns native at their first
  periodic state.
- **F2 (two shifts) with at most two knot kinds:** 127 patterns. With windows of radius 6 and finite repeats of index up to 30 only
  13 settled, and radius 9 with index 48 settled none of 40 more; one unsettled triple turned out to be realized only in patterns
  repeating in one shift, a junction state. Adding those repeats (period 2 and 3) settled 87: 78 read faithfully (55 with pairs in
  at most two knots, among them the endless six-regular weave, literature: the triangular lattice; 19 with every pair in one; 4 with
  a pair in three), 9 not, 40 still unsettled. It took 694 s on 8 workers on a loaded machine.
- **Global hollow triples:** in 8 of `OVERLAP-READ-20261111-001`'s 98 global bases, a greedy forcing set is one class of the source
  weave's knots, with at most two knots of the other class and the swapped-in knots.

## Families and readings (frozen; `contract.json`)

- **F1:** d = 1, one or two kinds of distinction, one to three kinds of knot, shifts in {0, 1, 2}; connected; up to relabelling and
  reversal (181). Window radius 24 (exact), finite repeats n = 2 to 15.
- **F2:** d = 2, one kind of distinction, one to three kinds of knot with shifts in {−1, 0, 1}²; connected; up to the eight
  symmetries of Z² (2,247): every pattern with one or two knot kinds (127) and a sample of 500 of the 2,120 with three (seed
  20261120). Window radius 6; finite repeats by every sublattice of index 3 to 30; patterns repeating in one shift with period 2 or 3
  in either coordinate, exact along the other.
- **Readings:** states; the faithful reading on sets meeting the unit at the origin within graph distance 2, stopping at the first
  settled violation (faithful, not faithful, or unsettled); knots on each pair. For each pattern read faithfully: whether some finite
  repeat (F1: n = 3 to 15; F2: index 9 to 30) is itself read faithfully as a finite base; the source labels at its first periodic state
  (each kind's distinction at the origin flipped by a change of the distinctions within shift 3); and, in place of the ruler (bond
  distance is undefined between some pairs of overlapping bases), whether each pair two steps apart lies in a bond of four with two
  distinctions next to one of them, the ruler's first step.

## Predictions

- **P1 (one shift is exact).** Every F1 reading with states is settled. A failure is a bug.
- **P2 (more overlap at infinity).** Some F2 pattern with a pair in four or more knots is read faithfully, settled. The pilot found
  pairs in three with two knot kinds, and F1 pairs in four. Failure: none in the three-kind sample, so in two shifts periodic overlap
  above three is not read faithfully in the family.
- **P3 (the infinite base shows more).** Some F2 pattern read faithfully at infinity has no finite repeat of index 9 to 30 read
  faithfully (F1 had six such in the pilot).
- **P4 (the ruler's first step).** In every F2 pattern read faithfully, every pair two steps apart lies in a bond of four. Failure: a
  pattern with such a pair in none, the infinite form of the unbonded pairs of `OVERLAP-READ-20261111-001`.
- **Measured, not predicted:** the share unsettled; source labels; patterns whose verdict needs the one-shift repeats.

## The global hollow triples (ticket B)

- **Lemma (two classes).** If the knots of a finite pattern split into two classes, every co-knotted pair in exactly one knot of each,
  then the two classes and their union have the same states (`OVERLAP-READ-20261111-001B`'s L5: same pair counts, same states). So
  each knot of one class is forced by the other class alone. The six-regular one-pair weaves split so.
- **G1.** In each of the 98 global bases, every added set forced only by the whole base is a knot of the source weave that the swaps
  removed. **G2.** Where every removed source knot lies in one class, the other class's knots force each of them. Measured: for the
  rest, whether the other class's remaining knots with the swapped-in knots force them. Mutation: a random set of as many knots does
  not force them.

## Decision rules

- **P2 holds:** an infinite base with a pair in four knots is read natively in two shifts; its ruler and balls are the next step.
  **P2 fails:** in the family, two-shift periodic overlap is read faithfully only up to three knots per pair.
- **P3 holds:** the infinite base is a different object from its finite repeats, as the owner's base realities are meant to be.
- **P4 fails:** unbonded pairs persist at infinity; the ruler needs more than overlap there.
- **G1 and G2 hold:** the global hollow triples are the two-class lemma at work, a removed knot held by the other class.

## Prior work (bounded search, 2026-11-11)

- **Known.** Shifts of finite type, the de Bruijn graph, decidability and periodic points in one dimension (Lind and Marcus, *An
  Introduction to Symbolic Dynamics and Coding*, 1995); undecidability of emptiness and aperiodic states in two (Berger 1966;
  Robinson 1971); domain walls in statistical physics; the two-class lemma is an instance of trades (Hedayat and Li 1979) and of the
  triangle gadget behind NAE-3SAT to maximum cut.
- **Not found.** A census of the not-all-equal law on periodic hypergraphs, or of which periodic overlaps it reads faithfully.

## Stop rule

One registered run of each ticket, the lemma proved, one referee pass; report and hold.

## Runtime

About an hour on 8 workers on the shared machine; registered in `docs/LONG_RUNNING.md`; `systemd-run --user -p MemoryMax=16G -p
MemorySwapMax=0`. Ticket B's check takes a few minutes.
