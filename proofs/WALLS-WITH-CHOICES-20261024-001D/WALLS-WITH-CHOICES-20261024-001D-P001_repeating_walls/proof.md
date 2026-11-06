# Good walls that repeat themselves

Status: Proved

Ticket `WALLS-WITH-CHOICES-20261024-001D`, 2026-10-24.

**What it uses:**
- from `WALLS-WITH-CHOICES-20261024-001A-P001`: the wall graph, the overlap set D(C), Lemma 2 (cyclic covers) and Theorem 1
  (periodic walls decide every direction), with the shared machinery of its check;
- from `WALLS-WITH-CHOICES-20261024-001B-E001` (frozen confirmatory experiment, refuted): the counts of configurations on which
  simple cycles misjudge a class.

## Standard statement

### Setting

- **The placement.** 159, one of the four bending contacts whose walls turn both ways and have a free place (111, 125, 159, 215).
- **The torus and the configurations.** The 3 × 4 torus in twist 11, in the placement's own terms (the convention of the frozen
  record). A configuration x gives the triangle of type t (0 up, 1 down) on square (i, j) the coin of bit 2(jL + i) + t of x.
- **Walks.** As in `WALLS-WITH-CHOICES-20261024-001A-P001`, a closed walk C of the wall graph *passes the criterion* for an odd
  class c when det(c, e(C)) ≠ 0 and D(C) ∩ (ℤc + ℤe(C)) = ∅.
  - A wall state is a triangle, an entry edge and a left value.
  - A closed walk that visits no wall state twice is a simple cycle, up to its starting point. Neither the class nor the overlap
    set depends on the starting point.

**Proposition 1 (good walls must repeat a state).** Take placement 159 on the 3 × 4 torus in twist 11 and the three pairs below of
a configuration and an odd class.

| Configuration | Class c | Fewest sheets of a cover with an assignment | Simple cycles | crossing the cylinder | passing the criterion |
| --- | --- | --- | --- | --- | --- |
| 7860857 | (2, 1) | 3 | 692 | 516 | 0 |
| 7985754 | (0, 1) | 3 | 244 | 198 | 0 |
| 6433130 | (1, 2) | 5 | 374 | 306 | 0 |

- **(a) An assignment.** For each pair the cylinder along c has an assignment.
- **(b) No good simple cycle.** No simple cycle of the wall graph passes the criterion.
- **(c) Repetition is forced.** So, by Theorem 1, some closed walk passes the criterion, and every closed walk that passes it
  visits some wall state more than once.
- **(d) An explicit good wall.** For each pair the crossing wall of a cover assignment is such a walk:

| Configuration | Length | Class e | det(c, e) | Wall states visited twice | Torus triangles visited twice |
| --- | --- | --- | --- | --- | --- |
| 7860857 | 46 | (3, 3) | 3 | 7 | 15 |
| 7985754 | 44 | (−3, −3) | 3 | 2 | 16 |
| 6433130 | 38 | (−3, −1) | 5 | 2 | 13 |

**Corollary 2 (simple cycles are not enough).** For the honeycomb contacts with a free place, deciding a class by simple cycles of
the wall graph is incomplete: it can report a contradiction where the cylinder has an assignment. It never errs the other way,
since by Theorem 1 (⇐) a good simple cycle yields an assignment.
- By ticket B, on 3 × 4 the contradiction histograms of each of 111, 125, 159 and 215 differ from the frozen ones by 240, 744
  and 4656 configurations in three of its four twists, 5640 in all. B compared histograms, so these are lower bounds on the
  number of misjudged configurations. The witnesses here come from 159's twist 11, where the difference is 4656.
- On 3 × 3, and for the other eight bending contacts on 3 × 4, simple cycles judge every configuration right (ticket B).

**Remark 3 (why a good wall can repeat a state).** Cut a good closed walk C at a repeated state into two closed walks C₁ and C₂.
- Their classes add: e(C) = e(C₁) + e(C₂).
- Their overlaps come from those of C: each is ±d or ±(e(C) − d) for some d ∈ D(C).
- But each piece is tested against its own lattice ℤc + ℤe(Cᵢ), of index |det(c, e(Cᵢ))| in ℤ², not against ℤc + ℤe(C). So an
  overlap that C may keep can fall into a piece's lattice, and the piece is then not simple on the cylinder.
- Cutting at every repeated state splits a closed walk into simple cycles. In the witnesses each simple cycle alone either
  does not cross the cylinder or is not simple there, by (b); only a combination of them passes.

## Nearest known result

- **The phenomenon.** Cycles of a finite graph that must avoid their own translates in a covering space need not be simple. That
  is generic for self-avoidance on a quotient; nothing here is surprising beyond the specific witnesses. Low novelty.
- **The witnesses.** They are new to the program and located by computation. They are certified below.

## Proof

**(a)** The check builds the cyclic cover of the cylinder along c with m sheets, for m = 1, 2, …, as in Lemma 2. The program's own
complete solver finds no assignment for m below the listed number. It finds one at that number, and the check verifies it clause by
clause.

**(b)** The check enumerates every simple cycle of the wall graph, each once from its smallest state, with no cap. It finds that
none has det(c, e) ≠ 0 together with no overlap in ℤc + ℤe.

**(c)** By (a) and Theorem 1, some closed walk passes the criterion. A closed walk that visits no wall state twice is a simple cycle
up to its starting point, and its class and overlap set do not depend on that point. So by (b) every closed walk that passes visits
some wall state twice.

**(d)** Follow the cut edges of the assignment of (a) on the cover. The check takes a wall that meets the loop of class c an odd
number of times; the proof of Theorem 1 (⇒) says one exists.
- **Its moves.** Projected to the torus, it is a closed walk of the wall graph whose moves are valid with its constant left value.
- **The criterion.** Its class e has det(c, e) equal to the number of sheets, and it has no overlap in ℤc + ℤe.
- **The repeated states.** It visits the listed numbers of wall states twice.
- **A rebuilt assignment.** The construction of Theorem 1 (⇐), applied to this walk alone, builds an assignment of the cylinder,
  and the check confirms that it passes every triangle of a window. ∎

**Corollary 2.** The first statement is Proposition 1. The second is Theorem 1 (⇐). The counts are half the differences of the
histograms in ticket B's frozen result: a misjudged configuration moves from its true pattern to one with more contradicting
classes, so it changes two entries by one each. ∎

## Checks

`check.py` uses the standard library only and the shared machinery of `WALLS-WITH-CHOICES-20261024-001A-P001`'s check. It
confirms (a)–(d) for the three witnesses, with the numbers in the tables.

**Control.** For placement 147, whose walls have no choices, on 3 × 3 (twist 01, configuration 30817, class (1, 1)), the
crossing wall of a cover assignment visits no wall state twice and passes the criterion. There the closed walks are the cycles of
a partial permutation, so a good wall is always simple.

## What this does not show

- **Larger tori.** Whether the share of misjudged configurations grows or shrinks on larger tori.
- **Bounds.** Any bound on how often a good wall must repeat a state, on the length of a good walk, or on the number of sheets.
- **Polynomial decidability.** Whether deciding a class is polynomial for these contacts. Ruling out simple cycles rules out one
  search, not every polynomial method.
- **Selectivity.** Whether the four contacts are selective on every large torus. Remark 4 of
  `WALLS-WITH-CHOICES-20261024-001C-P001` leaves that open.
- **Anything beyond the declared lattices.** Nothing about other triangulations, space or physics.
