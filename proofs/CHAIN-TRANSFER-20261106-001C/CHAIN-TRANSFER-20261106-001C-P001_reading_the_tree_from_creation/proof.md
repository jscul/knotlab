# Reading the tree from creation

Status: Proved (by hand from ticket A and the block lemma; checked on every Fano tree of at most five atoms, on random trees, and on an
exact creation map)

Ticket `CHAIN-TRANSFER-20261106-001C`, 2026-11-06.

## Question

- **Background.** By ticket A and the block lemma, creation on a Fano tree is fixed by its tree:
  - lines of one atom create at each other;
  - a line receives creation from another atom exactly when it touches its atom's cut toward that atom.
- **The source rule fails.** Ticket B refutes it at six atoms.
- **The question.** Can the tree, its atoms and the direction of every cut, still be read from creation alone by a short rule?

## Dependencies

- **`CHAIN-TRANSFER-20261106-001B`.** Its trees (`tree_lib.py`), its counterexamples and their exact creation maps.
- **`CHAIN-TRANSFER-20261106-001A`.** The touching rule at every distance.
- **`TWO-BIT-SCREEN-20261105-001B`.** The block lemma.

## Setting

Let S be a Fano tree. For an atom X:
- **Its lines.** L(X) is its set of lines.
- **Its cuts.** At each cut, X either emits (it lost a line there) or receives (it lost a point p there).
- **Facing.** For another atom A, the cut of X facing A is X's cut on the tree path toward A.

For atoms A and X, the **footprint** F(A → X) is the set of lines of X at which the lines of A create.

**Condition N.** Every atom X satisfies three things:
- **(N1)** X keeps a line.
- **(N2)** For each point p that X lost at a receiving cut, some line of X avoids p.
- **(N3)** For two such points, the lines of X through them are different sets.

**Every Fano tree whose atoms have at most four cuts satisfies N.**
- Breaking (N1) means losing all seven lines.
- Breaking (N2) means losing the four lines off p, and p itself.
- Breaking (N3) means losing the four lines through exactly one of two points, and both points.
- Each of these needs at least five lost elements.

## The rule

1. **Twins.** Two lines are twins when each creates at the other and they create at the same other lines. The twin classes are the
   atoms.
2. **Footprints.**
   - **Grouping.** For each atom X, group the other atoms by their footprint on X.
   - **The cuts.** Every footprint that is a proper subset of L(X) marks one cut where X receives. The atoms carrying that footprint are
     those beyond the cut.
3. **The tree.**
   - **Splits.** Each cut is read once, from its receiver, as a split: the receiver, and the atoms beyond.
   - **Edges.** The cut joins the receiver to the one atom beyond that no other split separates from it.
   - **Direction.** The cut runs from that atom, which emits, to the receiver.

## Theorem

**For every Fano tree that satisfies condition N, the rule returns its atoms and its cuts, each with its direction.** So native creation
recovers the directed handle tree of every Fano tree whose atoms have at most four cuts.

*Proof.*

- **Footprints are read from the tree.** Let a be a line of atom A, and X another atom.
  - By the touching rule, a creates at the lines of X that touch X's cut facing A, and at no others.
  - So F(A → X) is the same for every line of A, and equals:
    - L(X), when X emits at that cut;
    - X's lines through p, when X receives there at the point p.
  - By the block lemma, out(a) = (L(A) minus a) together with F(A → X) over all X ≠ A.
- **Lines of one atom are twins.**
  - Two lines a, a' of A create at each other.
  - Both sets, out(a) minus a' and out(a') minus a, equal (L(A) minus a, a') together with the same footprints.
- **Lines of different atoms are not.** Suppose a in A and z in Z, with A ≠ Z, are twins.
  - **On L(A).** out(a) meets L(A) in L(A) minus a, and out(z) meets it in F(Z → A).
    - Since z creates at a, a lies in F(Z → A), so F(Z → A) = L(A).
    - By (N1) and (N2), A emits at its cut facing Z.
  - **On L(Z).** Likewise Z emits at its cut facing A.
  - **Not neighbours.** A cut has one emitter, so A and Z are not neighbours.
  - **The next atom.** Let X be the next atom from A toward Z.
    - A emits at their cut, so X receives there, at a point p. So F(A → X) is X's lines through p, a proper subset by (N2).
    - The cut of X facing Z is a different one.
      - If X emits there, F(Z → X) = L(X).
      - If X receives there, at a point p' ≠ p, F(Z → X) is X's lines through p', different by (N3).
    - Either way out(a) and out(z) differ on L(X), which holds neither a nor z.
  - **So** a and z are not twins, a contradiction.
- **The cuts.** Fix X.
  - **Which footprints.** A footprint on X that is a proper subset of L(X) comes from a receiving cut of X, by (N2). Distinct receiving
    cuts give distinct footprints, by (N3).
  - **Which atoms.** The atoms showing it are exactly those beyond that cut.
  - **Once each.** Every cut has exactly one receiver, so every cut is read exactly once, with its far side.
- **The tree.** A tree is determined by the splits of its edges. The atom beyond a cut adjacent to its receiver is the one that no other
  split separates from the receiver, and it is the cut's emitter. ∎

## Where condition N fails

The rule loses the tree there (check 4):
- **An atom that lost all its lines.** It has no lines, so nothing can be read of it as lines.
- **A lost point whose four lines off it are all lost.** Its footprint is all of its atom's lines, as an emitting cut's is.
- **Two lost points with the same surviving lines.** They give one footprint for two cuts.

On random trees with many atoms hanging from two, condition N often fails. Wherever it held, in 1,550 of 2,000 random trees, the rule
recovered the tree. It recovered none of the other 450 (check 2).

## Beyond Fano trees (computed)

BRACE-TREE C's 111 fresh spaces, with exact creation maps (check 5):
- **Fano trees.** In all 17, each atom is exactly one twin class, as the theorem says.
- **With plane glue (93 spaces, 333 atoms).** The rule does not extend as stated:
  - 168 atoms are exactly one twin class;
  - for 155, a glue line joins the atom's class;
  - 10 split into three twin pairs. Through glue, their lines are reached differently.
  - No twin class ever mixes two atoms.
- **On the same spaces the source rule counted every atom** (BRACE-TREE C). Each rule fails where the other holds: the source rule on large
  Fano trees, twins through plane glue.

## How this answers the source rule

- **Twins and footprints use creation alone.** They need no quiet part and no blocks.
- **They read the direction of every cut.**
- **They hold where the source rule fails.** On ticket B's six-atom counterexample, the rule recovers the tree from the exact creation map
  (check 3).

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Every tree of at most five atoms: condition N holds; atoms and directed tree recovered | 100,830 of 100,830 |
| 2 | 2,000 random trees of 6 to 30 atoms, with random lost elements and permutations (half with many atoms hanging from two) | N holds in 1,550, all recovered; none of the 450 others |
| 3 | The exact creation map of ticket B's six-atom counterexample | atoms and directed tree recovered |
| 4 | Three trees violating N | the rule does not recover them |
| 5 | Computed: BRACE-TREE C's 111 fresh spaces, exact creation maps | 17 Fano trees: 67 of 67 atoms exact; 93 spaces with plane glue, 333 atoms: 168 exact, 155 plus one glue line, 10 split into three pairs; no class mixes two atoms |

## What this does not establish

- **Trees violating condition N.** Whether some other rule reads them is open. An atom with no lines cannot be read as lines at all.
- **Spaces with plane glue or non-Fano handles.** Check 5 shows that the rule does not extend to plane glue as stated.
- **Other far sides.**

## Novelty

- **New here.** The twin and footprint rule, and its proof.
- **Classical ingredient.** That a tree is determined by its edge splits (Buneman).
