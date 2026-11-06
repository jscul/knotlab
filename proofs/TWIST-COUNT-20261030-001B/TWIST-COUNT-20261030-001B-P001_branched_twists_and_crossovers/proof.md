# Branched twists: a junction crosses wires softly, never sharply

Status: Proved

Ticket `TWIST-COUNT-20261030-001B`, 2026-10-30.

**What it uses:**
- **`TWIST-COUNT-20261030-001A`:**
  - the setting: signings, branch tensors, junctions and the Hadamard basis;
  - Lemma 2: branch tensors are even, and planar pages are matchgates;
  - Theorem 4: a junction with an untwisted closed branch is a similitude of the matchgate identity;
  - Proposition 7: junctions of two twisted pages can leave the matchgate class.
- **`SEYMOUR-COUNT-20261030-001B`:** trisum trees.
- **External, not replayed:** the role of crossovers in planar Holant and #CSP dichotomies (Valiant; Cai, Lu and Xia; Guo and Williams). A
  problem that is tractable on planar graphs and hard on general graphs becomes hard on planar graphs as soon as a crossover is realizable.
  It is context only and is not used in a proof here.

## Why this ticket exists

Ticket A showed that counting stays polynomial unless some trisum square has twisted branches on all three sides. There the junction leaves
the matchgate class.

The cheapest route to hardness is a *crossover*: a junction that passes two wires across each other. With it, any non-planar instance could
be drawn in the plane and its crossings replaced by junctions. This ticket asks whether a junction can be one.

## Standard statement

**Setting** (as in ticket A).
- **Branch tensors.** At a square S = (c0, c1, c2, c3), the closed branches Q and R have nonnegative tensors F_Q, F_R (colouring counts).
  The arguments are the colours x0, x2 of the square's points and the colours of c1's and c3's neighbours in the branch.
- **The junction** W(x0, z1, x2, z3) on the host's legs:
  - it sums F_Q F_R over the branches' arguments;
  - it requires the square lines c1 and c3 to see not-all-equal values from (host, Q, R), with incidence signs s1 and s3.
- **Slices.** A *slice* fixes (x0, x2), and Q(q1, q3), R(r1, r3) denote the branch tensors on it.
  - Q_row(a) = Σ_b Q(a, b) and Q_col(b) = Σ_a Q(a, b).
  - |Q| is the slice total.
- **Crossovers.**
  - A *crossover* is [x0 = x2 ⊕ a][z1 = z3 ⊕ b], for some a, b. It passes the point colour from c0 to c2, and the host's colour from c1's
    neighbour to c3's, independently.
  - In the Hadamard basis it is [y0 = y2][y1 = y3]: only the four *straight* entries 0000, 0101, 1010, 1111 are nonzero, and all are equal.
  - A junction is *crossover-type* when its four *turning* entries (1100, 0110, 0011, 1001) vanish.
  - Its straight entries (a, b, c, d) then describe how it crosses. d = 0 is an *exclusive crossing*: one wire or the other, not both.

**Results.**
- **Lemma 1 (the junction on a slice).** With zero incidence signs,

  W(z1, z3) = |Q||R| − Q_row(z1) R_row(z1) − Q_col(z3) R_col(z3) + Q(z1, z3) R(z1, z3).

  Incidence signs act as complementation of the corresponding legs.
- **Theorem 2 (the square's lines carry no hard wire).** Let F_Q, F_R be nonnegative, with any signs. Suppose that on some slice W vanishes on
  every host pair (z1, z3) outside one parity class z1 ⊕ z3 = c.
  - Then W is nonzero on that slice for at most one value of z1.
  - Consequently no junction is a crossover: a crossover is nonzero on the slice x0 = x2 ⊕ a for both values of z1.
  - The square's points can carry a hard wire: a branch forcing x0 = x2 gives W = 0 off x0 = x2, with both colours alive.
- **Proposition 3 (soft crossings exist).** Over all pairs of sign classes of the truncated octahedron page (1786 distinct tensors) and all
  incidence signs:
  - 256 junctions are crossover-type, off the matchgate class, with all four straight entries nonzero;
  - for example (40000, −1112, 3336, −192), with MGI = −11,389,632;
  - none is an exact crossover, and none has a rank-1 straight part (ad = bc, two independent soft wires).

  Cube, 6- and 8-prism and Omni(K₂,₃) pages give crossover-type junctions only with a zero double entry, exclusive crossings.
- **Control.** If a branch tensor may be negative, a junction can be an exact crossover. Nonnegativity is what Theorem 2 uses.

## Nearest known result

- **Crossovers and dichotomies.** In planar Holant and #CSP dichotomies a realizable crossover makes a planar-tractable problem hard. The
  tractable planar classes are exactly those without one (matchgate-transformable signatures).
- **What is new here** (no overlap found, candidate local delta):
  - the knot's junction can never be a sharp crossover, because its lines are not-all-equal constraints and the counts are nonnegative;
  - it can be a soft one.

## Proof of Lemma 1

- With zero signs, NAE(z, q, r) = 1 − [q = z][r = z].
- Multiplying the two lines' factors and summing F_Q F_R over (q1, q3, r1, r3) gives the four terms.
- A sign on an incidence replaces that argument by its complement, which is the complement on the corresponding leg. ∎

## Proof of Theorem 2

- **Absorbing signs.** Primed variables absorb the signs (leg complements keep the tensors nonnegative). It suffices to treat zero signs and
  the class c = 0; c = 1 is the same with (v, v̄) in place of (v, v).
- **The hypothesis term by term.** W(0, 1) = W(1, 0) = 0 is a sum of nonnegative terms F_Q(q) F_R(r)[NAE(z1, q1, r1)][NAE(z3, q3, r3)]. So
  every pair (q, r) in supp Q × supp R makes one of the two factors vanish in both cases:
  - (q1 = r1 = 0 or q3 = r3 = 1);
  - and (q1 = r1 = 1 or q3 = r3 = 0).
- **Diagonal support.** The only consistent combinations are q1 = r1 = q3 = r3 = 0 and q1 = r1 = q3 = r3 = 1. So every pair in the product
  of supports is constant, (v, v, v, v).
- **One value.** A product of supports contains pairs mixing any of its points. So supp Q and supp R are the single point (v, v), with one
  common v (if either is empty, W vanishes on the slice).
- **The conclusion.** Then W(z, z) = [z ≠ v]² Q(v, v) R(v, v) is nonzero only for z = v̄.
- **No crossover.** A crossover needs both W(x0, z, x0 ⊕ a, z ⊕ b) to be nonzero for z = 0, 1 on the slice, which this excludes. ∎

## Proof of Proposition 3

- **Enumeration (check, section 3).**
  - Distinct tensors of all 2048 gauge-fixed sign classes of the truncated octahedron page: 1786.
  - All ordered pairs of them, and all 16 sign choices on the incidences of Q and R (host signs are leg complements).
  - The Hadamard junction is computed through its bilinear coefficient tensor, and the crossover-type junctions with a nonzero double entry
    are listed.
- **The exhibited example**, recomputed exactly from the two page tensors and the signs: turning entries 0, straight entries
  (40000, −1112, 3336, −192), MGI = 40000·(−192) − 0 + 3336·(−1112) − 0 = −11,389,632.
- **Other pages.** For the cube, the 6- and 8-prisms and Omni(K₂,₃) the same enumeration finds only zero double entries. ∎

## What the computation checks

`check.py` (a few seconds):
- **1, Lemma 1** on 300 random tensors and sign choices.
- **2, Theorem 2.**
  - 20,000 random sparse nonnegative junctions: 2448 slices are confined to one parity class, and every one has a single value of z1.
  - None of the 13,120 junctions of cube and 6-prism pages (all pairs, all signs) is a crossover.
- **3, Proposition 3.** All five page types, counted by kind, with the exact example.
- **4, controls.**
  - A junction with a signed branch is an exact crossover.
  - A branch forcing x0 = x2 makes the square's points carry a hard wire.

## Reading

- **Lines cannot carry wires; points can.**
  - A not-all-equal line forbids only one pattern. So to force a relation between the host's two line-neighbours, the other two sides must
    pin their own values, and that pins the host too.
  - The square's points, being shared colours, can carry a wire across the face.
  - So the knot's junction can never cross two wires sharply.
- **But it can cross them softly.**
  - With twists on all three sides, the junction lets both wires through at once with a small weight: double entry −192 against 40000.
  - That is a genuinely non-planar crossing, outside the matchgate class.
- **What remains.** Hardness theorems usually sharpen such soft gadgets by interpolation: repeat them and solve for the sharp crossover.
  Whether that works here is the open question. It needs the gadget's weights to be multiplicatively independent (a lattice condition) and a
  hard non-planar source problem.

## Nonclaims

- **Hardness.** No hardness theorem is proved. Soft crossings make the interpolation route plausible but not established.
- **Positivity beyond one junction.** Theorem 2 concerns a single junction. Networks of junctions are not covered.
- **Completeness.** Only five page types were enumerated. Larger pages may give rank-1 or other crossings.
