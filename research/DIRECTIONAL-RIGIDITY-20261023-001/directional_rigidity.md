# Which contacts are rigid in direction

Epic `DIRECTIONAL-RIGIDITY-20261023-001`, closed 2026-10-24.

## The question

The owner approved the recommendation of `LINE-DETECTOR-20261023-001`: "directional rigidity".
- **The question.** Which contacts are all or nothing in direction?
  - At two literals, every contradiction runs along no class, one class, or every odd class.
  - Twelve of the 30 three-place tiling contacts are selective. What makes the other 18 rigid?
- **The plan.** Test the 18 with up to 16 classes and on larger tori, then compare the algebra (polymorphisms) of rigid and
  selective contacts.
- **The hope.** An algebraic criterion, as majority decides the two-literal side.

**The evidence:**
- [Contradiction patterns with more classes and larger tori](../../experiments/DIRECTIONAL-RIGIDITY-20261023-001A/DIRECTIONAL-RIGIDITY-20261023-001A-E001_rigidity/contract.json)
  (A, frozen confirmatory experiment, supported;
  [result](../../artifacts/DIRECTIONAL-RIGIDITY-20261023-001A/DIRECTIONAL-RIGIDITY-20261023-001A-E001_rigidity/result.json));
- [Stripes and walls, not algebra](../../proofs/DIRECTIONAL-RIGIDITY-20261023-001B/DIRECTIONAL-RIGIDITY-20261023-001B-P001_rigid_contacts/proof.md)
  (B, proof);
- **scoping (scratch, not evidence):** polymorphism enumeration, renaming classes, a wall analysis of placement 135 that
  reproduced its 3 × 3 counts before the theorem was written, and sampled tests of the wall-cycle rule for the contacts whose
  walls branch.

## Outcome in one paragraph

**Algebra does not decide rigidity at three places; the geometry of walls does.**
- **Algebra.** Every three-place tiling contact has only trivial polymorphisms: projections, plus constants when the constant
  patterns are doubly allowed. Worse for any algebraic criterion, renaming the places of one relation can turn a rigid contact
  into a selective one (135, 147 and 149 are one relation with its places renamed).
- **Walls.** Where a twist forces an assignment to change value, it leaves a wall. The four kinds are:
  - **Free stripes.** The doubly allowed patterns let whole stripes flip along an edge direction. Then contradictions can run only
    along that direction: along the diagonal class at most (8 contacts), or nowhere (2).
  - **Straight walls.** The walls are pinned by the coins and can never have their lone corner at one end of the diagonal edge.
    Then every wall is a straight diagonal staircase, so one wall serves every direction at once. Contradictions run along all odd
    classes or none, with an exact count (8 contacts).
  - **Bending walls.** The walls can turn at both ends of the diagonal edge, and these 12 contacts are selective.
- **Why bending walls select.** This was proved for the four whose walls are forced at every step (Theorem 7). A direction
  contradicts exactly when every wall that can wind around the torus would collide with its own copy on that cylinder. The rule
  reproduces all 262144 configurations of each on 3 × 3, in every twist and along 16 classes.

## How it was found

| Step | Result | Status |
| --- | --- | --- |
| Enumerate the ternary polymorphisms of all 54 tiling contacts | Two-literal: majority. Three-place: trivial, rigid and selective alike | Proved (B, Proposition 1(a)) |
| Group the 30 three-place relations under renaming of places | Five of the twelve groups mix rigid and selective members. The kind depends on which places sit at the ends of the diagonal edge | Proved (B, Proposition 1(b)) |
| Classify by doubly allowed patterns | Stripes along the diagonal for the "one-dimensional" group and two of the "never" group; stripes along rows and columns for the other two | Proved (B, Theorem 2) |
| Trace the walls of a rigid contact (135) | Forced into straight diagonal staircases. The coin condition along one staircase decides every direction at once. Predicted 23816 of 262144 consistent configurations on 3 × 3, matching the record | Proved (B, Theorem 3) |
| Trace the walls of a selective contact (147) | Walls turn at mirror-like squares. A wall blocks a cylinder when it collides with its own copy there | Scoping; then proved (B, Theorem 7) |
| Generalize to rotating walls on the honeycomb | First test missed some collisions (only first visits compared). Corrected, it matches every configuration of 54, 109, 147 and 151 on 3 × 3 | Proved (B, Theorem 7) |
| Test the wall-cycle rule on the eight contacts whose walls branch | Matches 240 random configurations of each on 3 × 3, 100 of four of them on 3 × 4, and 96 selective configurations located on purpose | Scoping (scratch); motivates the next step |
| Freeze predictions and test on more classes and larger tori | All seven predictions hold on all five tori; the exact counts match Theorem 3 | A, supported |

## What was measured (A, supported)

| Prediction | Outcome |
| --- | --- |
| P1: no even class contradicts (theorem) | Holds on every torus |
| P2: no two-literal placement is selective (theorem) | Holds: all 24 on 3 × 3 and 3 × 4 (every configuration), the 8 representatives on 4 × 4, 4 × 5 and 5 × 5 (sampled) |
| P3: the one-dimensional placements contradict only along the diagonal class (theorem, B) | Holds; where the diagonal class is not listed (3 × 4, 4 × 5) they never contradict |
| P4: every nonzero pattern of a saturated placement is every odd class (scoping; now Theorem 3) | Holds. The counts contradicting nowhere equal the formula: 23816 of 262144 (3 × 3), 2 of 16777216 (3 × 4), and the sampled counts agree within |z| ≤ 1.15 |
| P5: the never-contradicting placements never contradict (scoping; Theorem 2 for 127 and 223) | Holds, including placement 191 on 4 × 4 and 5 × 5 where the diagonal class is listed |
| P6: the selective representatives 54, 62, 109, 111 are selective on 4 × 5 and 5 × 5 | Holds (for example 514936 selective configurations of 109 in the 4 × 5 sample) |
| P7: three-place placements with single lines and global contradictions are selective | Holds on every torus: 26 such (placement, torus) pairs, all bending, all selective |

**The run.** 26225 s against a declared budget of 14400 s. The exhaustive 3 × 4 torus with 13 classes alone took 3.6 hours. The
budget was an underestimate from a dry run; the run was not changed or interrupted.

**Checks.**
- **Controls.** All passed: totals; on 3 × 3 and 3 × 4 the implied torus, cylinder, lone and cross counts equal the frozen record
  of `TRIPLE-SHIELD-20261023-001A-E001`; on 3 × 3 the two programs agree over their common classes.
- **The independent checker.** It recomputed the fitting twists, the controls and the verdict (supported, no problems). It
  certified 664 configurations along every listed class with its own PySAT encoding, none undetermined, 80 of them selective.

## What was proved (B)

| Result | Content |
| --- | --- |
| Proposition 0 | The 30 three-place tiling contacts fall into four kinds: h/v stripes (127, 223), diagonal stripes (91, 94, 123, 167, 173, 183, 191, 239), straight walls (45, 61, 101, 103, 135, 149, 157, 199), bending walls (the 12 selective). |
| Proposition 1 | All three-place contacts have only trivial polymorphisms; all two-literal ones have majority. Renaming places mixes kinds in five of twelve groups. |
| Theorem 2 | Diagonal stripes confine contradictions to the diagonal class; h/v stripes forbid them. |
| Theorem 3 | Straight walls: all odd classes for every configuration when the relative twist is odd on the diagonal class; otherwise all odd classes or none, with exactly 2^{2LM} − (2^{2l} − 2)^g configurations contradicting nowhere. |
| Proposition 4 | Certified selective configurations on 3 × 3 for all twelve bending contacts. |
| Corollary 5 | The 18 contacts with stripes or straight walls are rigid on every torus. A contact with both single lines and global contradictions has bending walls. |
| Theorem 7 | For bending contacts with no free place: a class contradicts exactly when every valid wall cycle with a transverse class has an overlap in ℤc + ℤe. |

## What this changes

- **In `LINE-DETECTOR-20261023-001`.** Its closing question was whether rigidity characterizes two-literal contacts or follows from
  an algebraic property that some three-place contacts share. The answer is neither.
  - Rigidity reaches beyond two literals: 18 three-place contacts are rigid.
  - It is not algebraic at three places: rigid and selective contacts share their polymorphisms, even their relation up to renaming.
  - What clause width decides is the mechanism. At two literals the doubly allowed tiling and majority force rigidity. At three
    places walls carry the direction, and their shape decides.
- **In the experiment's groups.** The scoping labels gain structural definitions. "Never contradicting" splits in two:
  - 127 and 223 have stripes in two directions and provably never contradict;
  - 191 and 239 have diagonal stripes, so they could contradict only along the diagonal class, and on the tori computed they do
    not.

## Assumptions in the workspace this challenges

| Assumption | Where it lives | Verdict |
| --- | --- | --- |
| An algebraic (polymorphism) criterion might separate rigid from selective contacts, as majority does at two literals | `LINE-DETECTOR-20261023-001` recommendation | **False.** All three-place contacts have trivial polymorphisms, and renaming places changes the kind. |
| The direction structure falls at clause width | `LINE-DETECTOR-20261023-001` decision note and D001 | **Refined.** The two-literal side is always rigid, but 18 three-place contacts are rigid too. Clause width decides the mechanism (algebra versus walls), not rigidity itself. |
| "Never contradicting" is one phenomenon | A's scoping groups | **Two mechanisms.** Stripes in two directions (proved) versus diagonal stripes with an empty diagonal (observed). |
| Rigid three-place contacts are degenerate exceptions | This epic's scoping | **Partly true.** Stripes are degenerate, since the doubly allowed patterns are not rigid. Straight walls are not: they have rigid doubly allowed tilings, like the selective ones. |

## Provenance and novelty

| Result | Where it came from | Novelty |
| --- | --- | --- |
| Trivial polymorphisms of three-place contacts | Enumeration plus Świerczkowski's lemma | Classical tools; the observation is the program's |
| Renaming places changes the kind | Enumeration | Elementary; it rules out every relational criterion |
| Stripes (Theorem 2) | Explicit doubly allowed assignments on cylinders | Elementary; in subshift terms, free stripes make a direction non-expansive (Boyle and Lind). Moderate folklore risk |
| Straight walls (Theorem 3) | Domain walls of a rigid ground state, pinned by the coins and forced straight by the allowed lone corners | Elementary argument, exact count new to the program; low to moderate folklore risk |
| Rotating walls (Theorem 7) | Walls as walks among fixed rotators (as in Lorentz lattice gases and mirror models), with blocking read from self-overlaps of torus cycles | New to the program; low folklore risk for the exact statement |

**Did the perspective do real work?** Yes. Asking what a contradiction "sees" in each direction led to walls, and walls gave both
the rigidity theorems and the selection mechanism. The proofs are elementary.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — which contacts are rigid in direction | **Successful** | All 30 three-place tiling contacts are classified: 18 provably rigid on every torus, 12 selective (certified on 3 × 3, seen on every torus computed). The algebraic hypothesis is refuted. An exact selection rule is proved for 4 of the 12. |
| Local direction — rigidity of three-place contacts | Practically exhausted for rigidity | What remains concerns the selective side: an exact rule for the eight contacts whose walls have choices, and selectivity on every torus. |
| Broader exploration — the two/three boundary in direction structure | Sharper picture | Two literals: rigidity from algebra. Three places: direction structure carried by walls, rigid exactly when walls are free stripes or straight. |
| Long-term goal — emergence at the two/three boundary | Capability gained | A contact distinguishes directions only through walls that turn and collide with their own copies, a geometric mechanism with no two-literal counterpart. Missing bridge: whether this mechanism is the general form of "seeing a direction". |
| Next recommendation — walls with choices | **Next step:** Continue with a fresh epic: "walls with choices". (1) An exact rule for the eight bending contacts with a free place (155, 159, 203, 215 and the flipped 62, 110, 111, 125), whose walls branch. (2) Prove that every bending contact is selective on every torus large enough. Alternatives: a short note on the classification (1/3); the 3/4 constant (1/3). | Would complete the classification into an equivalence: a three-place contact is selective exactly when its walls can turn. |
| Interest — walls with choices | **2/3 — Promising** | Theorem 7 matched every configuration of four contacts, and directed walls suggest that classes in the quadrant away from the walls' cone behave rigidly. Main uncertainty: branching walls may need a transfer-matrix rule rather than a clean statement. |
| Execution — walls with choices | Deferred to the owner | Bound: one epic; exact 3 × 3 and 3 × 4 histograms of the eight as the falsifiable gate. Stop if no rule reproduces them. |
