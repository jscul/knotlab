# MODE-BOND-20261117-001: design

Epic `MODE-BOND-20261117-001` takes direction #1 of `TWO-ENDS-20261117-001` at the coordinator's go-ahead (2026-11-17 22:40 UTC).
It serves G17, with G1. The advisor checked the plan before the freeze (`advisor/design_question.md`, `advisor/design_answer.md`);
its changes are marked (advisor). Every claim here that uses Theorem D or G is conditional on `TWO-ENDS-20261117-001`, refereed and
confirmed with fixes. Claims that use Theorem N are conditional also on its repaired step 3, which has not been re-refereed.

## The patterns

The 13 mutants of 8db5da810c00 are 5 distinct patterns (CARRIER-R1). This study runs one representative of each:
- −73 (the same as −79, −84, −94, −106);
- −76 (as −86, −92);
- −81 (as −97, −103);
- −89;
- −100.

Controls are the 5 bounded patterns among CARRIER's 12: bace53f8f952-58, -111 and -147, ca1efb37ad88-361 (as the other seven of its
group), and ca1efb37ad88-835.

## The question

For these patterns F[r] is every assignment of every four-address orbit, at every r. On the periodic part of the saturated composite
automaton, every composite is a product except one along the self-similar type (one per parity). That composite T has two parts
(TWO-ENDS-R1):
- **the all-equal link:** an all-equal upper orbit forces an all-equal lower one, alternating with each step;
- **the split link:** a split lower orbit (0011 or 1100) forces a split upper one.

What the lower side of a bond can impose on the upper orbit x through T is one of four conditions:
- x split (C_P);
- x not all equal (C_PO);
- x not all-ones (C_¬Z1);
- x not all-zeros (C_¬Z0).

Each is realisable by members at the lower orbit. The advisor's third incompatibility type, where the upper side forces only "x
constant" and two unequal addresses sit below, is the condition C_PO read from above.

A bond across a long member-free window (no special orbit, at least five levels, saturated) must cross it along such a line, since
every other crossing is a product (Theorem G's argument). Its member at level 3 must matter.

## Part A: the decorated test (exact, finite)

- **Decorations (advisor).** Decorations are what members above the window can do to an orbit's state.
  - Members in the orbit itself fix some of its addresses: a subcube of its states.
  - Members in a child's subtree restrict the child's state to an induced set.
  - The family 𝓜′(t) of realisable restrictions of a type-t orbit is a fixpoint over types: subcubes intersected with the sets
    induced by the children's families through the orbit's block.
- **Backward closure.** Start at a self-similar orbit x, the top of the long crossing, with (C ∩ cube, cube) for each condition C
  and each subcube of x. Step to the parent with every decoration of the parent (a subcube) and of its other child (a set in 𝓜′).
  Each step maps the pair (M₁, M₂) to the sets of parent states from which some state of M₁, or of M₂, is reachable. Close over all
  types and lengths. Pairs(t) is the set reached at a type-t orbit.
- **Gadget.** A pair (M₁, M₂) in Pairs(t), for a type t found at level 3, with ∅ ≠ M₁ ≠ M₂. Then fixing the level-3 orbit's
  addresses to a state in M₂ ∖ M₁, with the decorations and the lower members, is impossible, while a state in M₁ is possible. The
  top member is then needed.
- **Joint crossings.** A bond may cross a window along several such lines. The test is extended to two crossings below one branch
  point by closing profiles (condition pairs to masks). A lemma covers more: if no orbit's compatible set depends on its crossings'
  conditions, nested crossings add nothing. The note says how far this reaches.
- **Reading, conditional as stated above.**
  - **If no gadget exists at a level-3 type, for single and paired crossings, and the lemma covers the rest:** no bond has a long
    member-free window, so L ≥ (⌊n/W₀⌋ + 3)/2 with W₀ = 6, linear growth (Theorem G's count).
  - **If a gadget exists:** its decorations give an explicit set of bounded size. It is checked as a bond of the real pattern by SAT,
    and then bounds L at every s of its parity from its depth on, by the same composite at every longer length (Lemma S).
- **Gates.** The families 𝓜′ and the backward steps are checked against SAT on the actual pattern at depth 8:
  - the induced restriction of a decorated subtree;
  - the projection of a decorated path onto its top orbit and its condition.

## Part B: confirmation

For a gadget found, the bond is mapped to addresses (the top orbit at level 3, the decorations, the lower orbit at distance 6 or 7
below x) and checked by SAT on the depth-N pattern, N = level(v) + 1, at two lengths of the window of each parity.

## Stop rule

Close when Part A is computed and gated on the 5 patterns and the 5 controls, and Part B has confirmed any gadget. If the joint
crossings are not settled, the note says which case stays open.
