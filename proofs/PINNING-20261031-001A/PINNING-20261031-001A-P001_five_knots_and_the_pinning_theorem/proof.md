# Five knots and the pinning theorem

Status: Proved

Ticket `PINNING-20261031-001A`, 2026-10-31.

## Dependencies

- **`MUTUAL-SELECTION-20261031-001`.** Lanes A–C: the symmetric laws, Tovey's census, and the Fibonacci pinning reduction that the pinning
  theorem generalizes.
- **External, not replayed.**
  - Schaefer's dichotomy (1978).
  - Tovey (1984): every 3-CNF in which every clause has three distinct variables and every variable occurs at most three times is
    satisfiable. A cubic bipartite graph has a perfect matching, so each clause owns a variable.

## Setting

- **Relations and laws.** A relation is a set R ⊆ {0,1}³. A *signed law* is the class of R under flips and permutations of the three
  places. A *cubic system* over a law has lines that are ordered triples of distinct points, each carrying a relation of the law, and every
  point lies on exactly three lines. A *plain* system uses only permutations of R, without flips.
- **Knots.** R is a *knot* when it passes K1–K3 on three places: R ≠ ∅, R ≠ {0,1}³, and every two-place projection of R is full.
- **Pieces.** A *piece* has internal points, each on three of its lines, and three *ports* a, b, c, each on one of its lines. It *accepts*
  the port values that extend to a satisfying assignment of the internal points.
  - A *pinning piece* accepts exactly a face {x : x_i = c}.
  - A *full piece* accepts everything.

## Lemma 1 (five knots)

The 34 knot relations fall into exactly five classes under flips and permutations:

| Class | Relations | Size of R |
| --- | --- | --- |
| parity (affine) | 2 | 4 |
| Fibonacci (no-lone) | 8 | 5 |
| not-all-equal | 4 | 6 |
| x ∨ (y ≠ z) | 12 | 6 |
| clause | 8 | 7 |

*Proof.* R must have |R| ≥ 4. Its complement must contain no full fibre (two states differing in one place).
- |R| = 4 makes R a Latin square, a parity coset.
- |R| = 5 makes the complement three independent vertices of the cube, which lie in one parity class: the no-lone class.
- |R| = 6 makes the complement two vertices at distance 3 (not-all-equal) or at distance 2 (x ∨ (y ≠ z)).
- |R| = 7 is the clause. ∎ (Enumerated in check 1.)

## Lemma 2 (plain systems)

- **Statement.** Not-all-equal is the only knot relation that excludes both 000 and 111. So on plain cubic systems every other knot is
  satisfied by a constant colouring, and not-all-equal is the only knot that can fail.
- **Proof.**
  - If 000, 111 ∉ R, the full projection onto any two places needs the pair value (0,0) from a state of weight 1, and (1,1) from a state of
    weight 2.
  - Over the three pairs of places this forces all six states of weight 1 and 2, so R is not-all-equal.
  - Permuting places does not move 000 or 111. ∎ (Check 2.)

## Lemma 3 (no preferred value, no pinning)

- **Statement.**
  1. If every relation of a law is unchanged by flipping all three places, every piece accepts a set closed under flipping all three
     ports. Such a law cannot pin.
  2. Among the knots, the relations unchanged by this flip are exactly the four signed not-all-equal relations.
- **Proof.**
  1. Flipping every point of a solution gives a solution. A face is not closed under the flip.
  2. A relation closed under the flip is a union of antipodal pairs. Three pairs give signed not-all-equal. One pair, two pairs or four
     pairs miss a projection or are full. ∎ (Checks 3 and 7.)

## Theorem 4 (the pinning theorem)

- **Statement.** Let L be a signed law with:
  1. a pinning piece, pinning port i to value c;
  2. a relation S ∈ L and a place j such that S with place j fixed to some value is equality or disequality on its other two places;
  3. a full piece.

  Then the satisfiability of arbitrary instances over L (any number of occurrences per variable) reduces in polynomial time to
  satisfiability on simple cubic systems over L. In particular, if L is not Schaefer-tractable, deciding L on cubic systems is
  NP-complete.
- **Proof.**
  1. **Copies.** Replace a variable with d occurrences by d copies, each carrying one occurrence. Join consecutive copies by a line of S
     whose place j holds a pinned point.
     - Flip that incidence so the point is seen at the fixing value; for disequality, also flip one copy's incidence.
     - The copies are then forced equal.
  2. **Pinned points.** Each pinning piece supplies one pinned port with two free incidences. Its two other ports are free, and they are
     solvable whatever the pinned value is, since the piece accepts a whole face.
  3. **Padding.** Spare incidences come from chain ends, free ports and unused pinned incidences. Give each point a demand equal to its
     number of spare incidences.
     - The total demand is divisible by 3, because 3·#points − 3·#lines is.
     - Add fresh points of demand 3 until no demand exceeds total/3.
     - Then repeatedly take the three points of largest remaining demand and join them by a full piece.
     - The bound max ≤ total/3 is preserved: if the maximum equals total/3, at most three points attain it, and all of them are taken. So
       the procedure ends with every point on exactly three lines.
  4. **Correctness.** Full pieces impose nothing; pinning pieces fix only their pinned ports; copies are equal. Solvability is preserved.
     The lines are distinct and have distinct points; the size is polynomial. ∎
- **Checked (check 5).** Generic code, on 60 random Fibonacci instances, 24 of them unsolvable. The systems are cubic and simple, of up to
  182 lines.

## Proposition 5 (Schaefer status)

Only the parity law is tractable with unbounded occurrences (affine). The other four classes are closed under none of Schaefer's
operations, so they are NP-complete (check 4).

## Proposition 6 (the clause cannot pin)

- **Statement.** The clause law has no pinning piece.
- **Proof.**
  - Suppose a piece P pins port a to c. Flip the sign of a's incidence in a copy P′, so that P′ pins its port to ¬c.
  - Identify the two pinned ports into one point p, which then has degree 2. Add a clause line through p and two fresh points, and pad
    every spare incidence with full clause pieces; three clause lines sharing two internal points always accept.
  - The result is a cubic system of three-literal clauses in which p must equal both c and ¬c. It is unsatisfiable, against Tovey. ∎
- **Checked (check 6).** A full clause piece exists, 300 of 300 random cubic clause systems are satisfiable, and the search finds no
  pinning piece with up to four internal points.

## Observation 7 (one skeleton pins every pinning law)

The same skeleton pins the Fibonacci law and parity (check 5 and the controls): four internal points, the lines (0,1,2), (0,1,3), (0,2,3),
and the tails (1,2,a) and (3,b,c). With its own signs it also pins x ∨ (y ≠ z), as ticket B records. Not-all-equal and the clause cannot use
it, for the reasons of Lemma 3 and Proposition 6.

## Controls (check 8)

- Exactly-one also excludes both constants but is not a knot, so the knot hypothesis is what Lemma 2 uses.
- Parity pins, yet it stays polynomial (affine).
- Replacing the equality link by a clause line decouples the copies and loses solvability on 16 of 40 instances.

## Consequences used later

- **Plain systems.** Only not-all-equal can fail.
- **Signed systems.**
  - Parity fails, but is polynomial.
  - Not-all-equal cannot pin, and is polynomial (Pfaffian; Seymour, Robertson–Seymour–Thomas).
  - The clause cannot pin and never fails.
  - The Fibonacci law pins and is NP-complete on cubic systems.
  - x ∨ (y ≠ z) is ticket B.

## Novelty

- **Classical.** Schaefer, Tovey, and the bounded-occurrence literature (Feder; Dalmau and Ford).
- **No overlap found yet.** The five-class census of three-place knots, the no-preferred-value lemma, and the pinning theorem in this
  exactly-three form. The literature check comes at closure.
