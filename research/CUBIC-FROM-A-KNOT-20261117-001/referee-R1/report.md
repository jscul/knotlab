# Referee report CUBIC-FROM-A-KNOT-R1 (fresh code, no Codex)

**Verdict: Confirmed, with framing fixes. No Block, no correction.**
- **What holds.** The mathematics is right, and every finite check reproduces in the referee's own code one or two sizes past:
  - the growth rule, written from the proof's text, gives the cubic orthant's incidence exactly through round 11 (364 junctions;
    the study replayed 220);
  - the boxes of side 2 to 5 have the stated counts, every junction's star is a K1–K3 knot, and the eight original states are kept
    exactly;
  - the new position bits are free;
  - the long-bond construction gives K1–K3 bonds in 200 of 200 random pairs.
- **What John's summary leaves out.** None of these points is an error in Codex's files.
  - **The cubic volume theorem is the program's own earlier result**, carried to the corner. The system is Tseitin's law (an even
    number of ones at every junction). LOGIC-AXIS's Proposition 3b proved r^D bond-ball growth for it on the full lattice Z^D on
    7 November.
  - **The "three" is put in by the law.** It has three fresh distinctions per join, groups of at most three, and simultaneous rounds.
    - With two fresh distinctions the same rule grows a quarter plane.
    - With four, it stalls after three rounds.
    - Without simultaneous rounds, trees are equally legal.
  - **"Three-dimensional" here is not CUBE-DOUBLING's "orders".** It is the growth exponent of bond balls, a different notion.
  - **The original cube is joined by design, and the law changes there.** The cheapest law would go on to four orders.
- **What it adds.** A concrete local rule that grows a three-dimensional base from one knot, read from inside by the program's own
  bond distance. Also a clean view of why the cut cubes could not do this: cut systems put their geometry into disagreement counts,
  while parity systems put it into bonds.

## What the system is (in John's terms first)

- **The junctions.** Each one says "an even number of my distinctions are 1". The distinctions are the links between neighbouring
  junctions on a cubic grid that has a corner and extends forever in three directions.
- **The allowed states.** They are the even subgraphs of the grid. In the literature this is the cycle space, or Tseitin's law with
  all charges zero.
- **Its knots.** They are exactly the minimal edge cuts of the grid. In graph theory these are also called *bonds*, so the
  program's word and graph theory's coincide here.
- **The distance.** Two links are close when a small cut contains both.

## What holds

- **The growth rule (`referee_cubic.py grow`).** The referee wrote the parallel policy from section 1 of the proof alone. It reads
  only which junctions share distinctions, which distinctions are loose, and the two common-neighbour tests.
  - From one ternary parity knot, round t's incidence (junctions and their bits) is isomorphic to the expected orthant layer
    I_t = {v ∈ ℕ³ : Σv ≤ t}. The check is a WL hash, then VF2.
  - That holds at every round through t = 11: 1, 4, 10, 20, …, 286, 364 junctions.
  - Each round uses the predicted groups, for instance 10 triples and 15 pairs at round 5.
- **The boxes (`boxes`).** By GF(2) ranks of the parity equations, sides 2 to 5 (125 junctions is one size past the study):

  | Side | Junctions | Shared bits | Loose bits | log₂ allowed states | log₂ rows of Y | Stars that are knots |
  | --- | --- | --- | --- | --- | --- | --- |
  | 2 | 8 | 12 | 12 | 16 | 11 | 8/8 |
  | 3 | 27 | 54 | 27 | 54 | 49 | 27/27 |
  | 4 | 64 | 144 | 48 | 128 | 123 | 64/64 |
  | 5 | 125 | 300 | 75 | 250 | 245 | 125/125 |

  - **The marked bits K.** No parity check falls on the eight marked bits at any side. So every one of their 256 tuples extends, and
    with the cut relation S imposed the marginal on K is exactly S's 8 rows. S itself equals the rows allowed by the literal
    betweenness knots of the 2 × 2 × 2 cube.
  - **Stars in Y.** In Y, each junction's star projects exactly to even parity, at sides 2 to 4: 99 of 99 stars, tested by
    enumeration and linear feasibility.
- **The position bits are free (claim 3).** No check falls on the set of one distinguished-direction bit per junction, at any side.
  So with S on K, the marginal is S times free choices at the 19, 56 and 117 new positions.
- **The long bonds (claim 2, upper side; `bonds`).** In a side-9 box, take 200 random pairs of edges and a shortest monotone path
  between their nearest endpoints. In all 200 cases the cut around the path is a K1–K3 bond: exactly one check on it, its full
  parity, and none on any part. Its size is at most 4d + 6.
- **The lower side.** 3,380 bonds were enumerated: every connected vertex set of up to 5 vertices with connected complement, near
  the corner and in the interior. None has anchors spread more than |F| − 1 apart in sup norm. This agrees with the proof's
  "dependencies are connected through squares".
- **The proof itself.**
  - **The finite constraint lemma.** Every valid check is a finite cut, built from a potential defined along monotone paths. This
    is the standard cut–cycle duality, correctly adapted to the corner.
  - **The upper bound.** The square-connectivity argument for the upper ball bound is right.
  - **The escape argument.** It is sound for the orthant's monotone paths, and it gives the lower bound. The study's 2,688-path
    audit agrees.
  - **The attached version.** The splitting at range three handles the non-linear S, and its bounds follow.

## 1. The cubic volume theorem is LOGIC-AXIS's, carried to the corner (Not a block)

- **What LOGIC-AXIS proved.** Proposition 3b of `LOGIC-AXIS-20261107-001A` treats the law "the edges at every vertex sum to 0" on
  ℤ^D. It proves |site(e) − site(f)|_∞ ≤ δ(e, f) ≤ (2D − 2)(d + 1) + 1, and bond balls between c·r^D and C·r^D (its Corollary).
- **What this study does.** The same law on the orthant ℕ³, with the corner and the boundary handled by the monotone-path escape
  argument. The proof's "Nearest known result" and the pre-registration cite LOGIC-AXIS for this.
- **The fix for John's summary.** "The proof shows … r³" should say that the volume part is LOGIC-AXIS's theorem, now on the
  corner. What is new is that the lattice is grown from one knot by a local rule, and attached to the original cube.

## 2. How much is supplied (the coordinator's question; Not a block, but the main framing point)

- **What the law supplies, and what each choice decides.**
  - **Three fresh distinctions per junction.** This is the number of directions.
    - With two fresh distinctions and groups of at most two, the referee's run of the same rule grows the quarter plane ℕ², exactly
      through round 14 (`grow`).
    - With four fresh distinctions and groups of at most three, it follows ℕ⁴ through round 3. At round 4 it has no legal parallel
      step: the four parents of (1, 1, 1, 1) would need a group of four (`grow4`).
    - So the dimension is a dial of the law, set by its arity and its group tests.
  - **The group tests.** "Pairwise common neighbour, and for triples no common neighbour of all three" are exactly the tests that
    pick out the parents of a cubic-lattice site.
  - **Simultaneous rounds.** The single-addition rule also admits trees. One example is a singleton junction on every loose bit,
    which grows exponentially. The proof and the note say this.
  - **The attachment.** The root corner, the distinguished direction and the value conventions are design choices. The note says so.
- **What is grown.** The incidence itself. From one knot, the rule builds ℕ³'s meeting pattern without coordinates.
- **So "we constructed a system with three-dimensional growth" is an existence result for a designed law**, as the note's Scope says.
  - It answers "is it possible?" with yes.
  - It does not show that logic selects three.
- **Against GRID-GROW's Block.**
  - **What was blocked there.** GRID-GROW's G5, "states name every placement", failed for betweenness bases: two placements had the
    same states.
  - **Here the analogue holds.** The parity part's states determine the junction graph up to isomorphism. This is Whitney's
    2-isomorphism theorem: each box's graph, with one extra vertex for the loose bits, is 3-connected (`whitney`, checked at sides
    2, 3 and 4).
  - **Recovering the junctions.** By Tutte's theorem, in a 3-connected graph the vertex stars are exactly the non-separating
    cocircuits. So the junctions themselves can be read from the states.
  - **What this settles.** It answers the note's open "full state recovery of the local constraint list" for the parity part, by
    known mathematics. It does not cover the attached betweenness bits.
- **Against CUBE-DOUBLING.**
  - **The law changes.** The bridge grows the original cube by betweenness steps, then changes law. Each parity step leaves four
    lifts per old row, far from A99's cheapest, under which the cube goes on to Q₄, Q₅, … and never stops at three orders.
  - **No conflict.** The two results are about different laws.

## 3. Is "three-dimensional" the same notion as CUBE-DOUBLING's "orders"? (No; Not a block)

- **CUBE-DOUBLING's orders.** They are the lattice dimension of a cut system: the fewest lines whose product holds the distinctions,
  read from the states' splits.
- **Here.** "Three-dimensional" is the growth exponent of bond-distance balls.
- **How the two notions come apart.**
  - On a cut cube Q_d there are d orders, but every pair is one three-place knot apart (Codex's own control: bond distance 2 for
    every pair at 8, 27 and 64 distinctions). So the cut cubes have no volume growth at all: a ball of radius 2 is everything.
  - The parity grid's states are not a cut system (the all-ones assignment is not allowed), so it has no orders in CUBE-DOUBLING's
    sense.
  - The eight original distinctions have three orders and are placed in the grid's three directions by the attachment's choice.
- **The fix.** "Three-dimensional" should name its notion where it is quoted: "bond balls grow as r³".

## 4. Is the distance legitimate, and does it agree with the others? (The coordinator's question; holds)

- **Legitimate.**
  - It is the canonical bond distance: the least size of a K1–K3 knot containing both, minus one, on the allowed states.
  - The knots are parity relations of unbounded size, up to about 4d + 6 at separation d. Each passes K1–K3, as the canonical test
    asks for parity.
  - Every distinction flips by a finite change at every state, so the source-aware reading is met.
- **Against steps apart.** It agrees up to constants, never exactly: δ lies between the sup-norm separation and 4d + 5. Steps apart
  in the grid is within a factor three of sup norm. So the ball exponent is exact, but the distance is only bi-Lipschitz to steps.
- **Against the disagreement count.**
  - **It reads nothing here.** Every pair of distinctions is free: no check on any pair at sides 2, 3 and 4, which is 276, 3,240 and
    18,336 pairs. So any two distinctions differ in exactly half the allowed states.
  - **The mirror of the cut box.** In Codex's cut box the disagreement count reads the coordinates (twice the step distance), and
    bond distance is 2 for every pair.
  - **Why.** This is cut–cycle duality. A cut system's *states* are cuts, so its geometry sits in which states separate two points.
    A cycle space's *checks* are cuts, so its geometry sits in which cuts contain two distinctions. That is a clean statement of
    when each of the program's two rulers can work.
- **Two-sided?** Yes, proved for every r ≥ 5, and r ≥ 33 with the cube attached:
  - 3·C(⌊(r − 5)/4⌋ + 3, 3) ≤ |B(e, r)| ≤ 3(2r + 1)³;
  - 3·C(⌊(r − 33)/4⌋ + 3, 3) ≤ |B_Y(e, r)| ≤ 3(6r + 1)³.

  The exponent 3 is exact. The constants are far apart: about r³/128 against 24 r³, or 648 r³ with the cube. No limit of |B|/r³ is
  claimed.

## 5. What the base carries when the position bits are free (the coordinator's question)

- **What it carries.** Its constraints and nothing else.
  - Every constraint on finitely many distinctions is the parity of a finite cut, by the finite constraint lemma.
  - A cut made only of position bits would need an infinite U, a union of whole layers. So every constraint uses join bits.
  - The information is which sets of distinctions are tied together (the bonds). It is not values at positions, and not pair
    counts.
- **Against A97.**
  - A97 reads information as distance "as its own law measures it (bond distance …)".
  - Here bond distance is the only one of the program's rulers that sees anything. The disagreement count is flat.
  - Whether the pairwise bond-distance table determines this base was not tested. A97's own challenge asks exactly that.
  - The states determine the graph (Whitney), and the graph determines the bond distances. Whether the converse holds is open.
- **Against DISTANCE-DIM.**
  - **Consistent.** DISTANCE-DIM found that the distance reads the dimension the meeting pattern already has.
  - **Here.** Bond distance reads the grown orthant up to constants. The dimension three is in the meeting pattern because the law's
    arity put it there (§2).
  - **So.** This is a three-dimensional case of "the distance reads the pattern's dimension". It is not a case of the distance
    creating dimension.

## 6. What is proved, what is computed, what is known

- **Proved by the study, and checked here.**
  - The parallel rule's output is ℕ³'s incidence at every round.
  - Bond balls are Θ(r³) at every distinction, with the cube attached as well.
  - The eight original states are kept exactly.
  - The position bits are free.
  - Every distinction has finite flips.
- **Computed.** The boxes of side 3 and 4, the 220-junction replay and the 2,688-path audit. The referee adds side 5, round 11, the
  200 tube bonds, the 3,380 enumerated bonds, and the two- and four-direction variants.
- **Known mathematics, cited once.**
  - **Tseitin's law and cut–cycle duality.** Tseitin's parity-at-every-vertex formulas (1968). Even subgraphs (the cycle space) and
    their checks (the cut space) are orthogonal complements (any graph theory text, for instance Diestel's *Graph Theory*, §1.9).
  - **Bonds.** Minimal cuts are the cocircuits of the cycle matroid (Oxley, *Matroid Theory*).
  - **Recovery.** Whitney's 2-isomorphism theorem (1933), and Tutte's non-separating cocircuits.
  - **Volume growth.** ℤ³ has cubic volume growth.
  - **The program's own.** LOGIC-AXIS Proposition 3b gives the r^D law on ℤ^D.
- **What the perspective adds.**
  - **The local rule.** It reads only which knots meet, and grows the cubic incidence from one knot.
  - **The bridge.** It joins the cut cube without losing a state.
  - **The duality reading.** Cut systems keep their geometry in disagreement counts, cycle spaces in bonds, which tells the program
    which ruler to use on which base.
  - **The dial.** The same rule grows two directions with two fresh distinctions.

## Fixes for the thread (listed for John and the coordinator; Codex's files not edited)

1. **The volume theorem.** In the summary, say it is LOGIC-AXIS's Tseitin-law result on the corner. **Not a block.**
2. **What sets the three.** Say what is supplied: three fresh distinctions, groups of at most three, simultaneous rounds and the
   attachment. Say that two fresh distinctions give two directions and that serial growth allows trees. **Not a block**, but it is
   the main point of framing.
3. **Naming the notion.** "Three-dimensional" should say "bond balls grow as r³", and should not be read as CUBE-DOUBLING's orders.
   **Not a block.**
4. **Optional.**
   - The note's open "full state recovery" is answered for the parity part by Whitney and Tutte.
   - The disagreement count is flat here, which is worth one line beside the cut-box control.

## How the work was split

- **The referee:**
  - read the note, the pre-registration, the proof, `cube_interface.md`, the results, and LOGIC-AXIS's proof;
  - checked the proof by hand;
  - wrote its own growth rule, isomorphism tests, GF(2) box algebra, Y-star feasibility, tube bonds, bond enumeration, the
    two- and four-direction variants and the connectivity check (`referee_cubic.py`).
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_cubic.py`**, with parts `grow`, `grow4`, `boxes`, `bonds` and `whitney`.
- **Outputs:** `referee_cubic_<part>.json`.

Reproduce, from `research/CUBIC-FROM-A-KNOT-20261117-001/referee-R1/`:

```sh
for P in grow grow4 boxes bonds whitney; do ../../../.venv/bin/python -B referee_cubic.py $P > referee_cubic_$P.json; done
```
