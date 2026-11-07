# Atoms see only the port relation

Status: Proved (an exhaustive finite check extending GLUE-READ A's, on top of ticket A)

Ticket `ATOM-ONE-20261107-001B`, 2026-11-07.

## Question

- **What ticket A gives.** A Fano atom with any line removed sends the free relation through each of its cuts. So any port relation
  that a removal in atom A causes at another atom's cut is the same whichever line of A is removed.
- **What is left.** The deep points of A's side do depend on the removed line. Can they change what a line of another Fano atom
  receives?

## Dependencies

- **`ATOM-ONE-20261107-001A`.** Transparency. Also step 1 of its proof: a Fano atom with its closed sides is the Fano plane, up to flips.
- **`GLUE-READ-20261106-001A`.** The receiving-cut law for a closed atom. Its bound feeds every deep relation of the removal's side at
  once (`port_lib.py`).
- **`CHAIN-TRANSFER-20261106-001A`.** The local engine (`transfer_lib.py`): creation at a line as an OR over local configurations, each
  given as a mask (PENDANT-LINE A).

## Setting

- **The atom and its cut.** B is a Fano atom of a knot space, b a line of B, and C the cut of B facing a removal.
- **The port relation.** R is the relation the removal's side shows on C.
- **B's own verdict.** It uses masks from B's own points and channels only. By ticket A this is GLUE-READ A's closed atom: B with each
  closed side replaced by the relation it shows, which is that of its lost element up to flips.
- **Three kinds of further point.**
  - **B's points and channels.**
  - **Deep points of the removal's side.** Their relations with C's channels are compatible with R.
  - **Deep points behind B's other elements.**
    - **Behind a line.** Its closed side accepts exactly not-all-equal, so a deep point's relation with its channels is compatible with
      that.
    - **Behind a point.** Its side accepts one antipodal pair, so a deep point there is a copy of the point or free.
- **A mixed pair.** A deep point of the removal's side together with a deep point behind another element.

## Theorem 1 (deep points of the removal's side)

**Feed at once:**
- every single and pair relation of the removal's side compatible with R (GLUE-READ A's bound);
- every mixed pair, the deep point behind another element ranging over every relation its side allows.

**Then whether creation occurs at b is B's own verdict.** For every port relation, closed atom and line this holds in all 5,880
non-degenerate cases of the 8,190 letters (check 2).

**Far sides change only in one place.** They change only at a receiving atom's cut lines, when R is one of six relations (504 cases,
check 2). Those are the six with six patterns that keep both constants, or four patterns with two ports opposite. Mixed pairs add nothing
beyond GLUE-READ A's bound.

## Theorem 2 (free passes through)

**A closed Fano atom passes a free relation unchanged.** Open one element of the Fano plane, a line removed or a point split into free
copies. Then every other element's three variables are free: 182 of 182 (check 1). The removed-line half is ticket A's freeness.

## Corollary (a Fano atom acts as one)

Let A and B be different Fano atoms of a knot space, b a line of B, and a and a′ lines of A.
1. **Creation.** a creates at b exactly when a′ does.
2. **Far sides.** a and a′ give b the same far-side vector, except possibly at one kind of line. That line is a cut line of B where B
   receives (lost a point) at the cut facing A, and the port relation there has six patterns.
   - **Only three such relations.** Of the six relations, only the three that keep the constant patterns can occur at a receiving cut.
     The point side's closed relation is one antipodal pair, and a removal only enlarges it.
3. **Atoms only between.** If only Fano atoms lie between A and B in the decomposition, a and a′ give every line of B the same far-side
   vector. That covers every Fano tree.

*Proof.*

1. **The port relation at C is the same for a and a′.**
   - Split the removal's side at A's cut toward B.
   - By ticket A, A's part sends the free relation there for either line.
   - The rest of the removal's side contains neither line, so it turns that same input into the same relation R on C.
2. **Masks that use only B's side are the same for a and a′.** These masks use B's points and channels and the points behind B's other
   cuts. They depend only on B's side and R.
3. **Every other mask contains a deep point of the removal's side.** Its relation with b's points is that point's relation with C's
   channels, joined through B's side. B's other sides enter only through their channels, and their deep points through relations their
   exact relations allow. So it is one of the masks fed in Theorem 1.
4. **These masks add nothing outside the exception.** By Theorem 1, together they create only where B's own verdict does. They add far
   sides only in the exception. B's own masks are among those of step 2, so step 2's masks decide everything else.
5. **Atoms only between.** By ticket A and Theorem 2, R is then free, which is not one of the six. ∎

## What the bound cannot do (check 3)

- **The test.** Deep points behind B's own other elements are bounded the same way: every relation their sides allow, alone, in pairs and
  with B's points, and no deep point of the removal's side.
- **They can add creation.** With one slot order, 56 of 980 cases change: intact lines with a free or not-all-equal port relation. Far
  sides change in 728 of 980.
- **So bounding cannot settle more.** It cannot show that every real atom gives exactly its closed verdict. Whether real sides ever
  present such relations is a question for ticket C.
- **Acts-as-one is untouched.** These points lie on B's side and do not depend on which line of A was removed.

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Free passes through a closed atom | 182 of 182 |
| 2 | Deep points of the removal's side and mixed pairs, all 8,190 letters | creation: 5,880 of 5,880 unchanged; far sides: only the 504 exception cases, as in GLUE-READ A |
| 3 | Deep points behind B's other elements alone (one slot order) | creation changes in 56 of 980 cases; far sides in 728 |

## Reading

- **What an atom can tell about a distant handle.**
  - Through its port relation it learns everything the handle's removal changes there, and that relation is the same for every line
    of the handle.
  - Deeper points of the handle's side carry more, but an atom's lines can read it only at one place: a receiving cut line whose
    relation has six patterns.
- **Atoms are blind to depth, made precise.**
  - GLUE-READ's reading was that atoms are blind to depth and plane glue is not.
  - This corollary proves it for whether creation occurs. It also proves it far side by far side, except one finite place.
- **Why glue lines differ.** Glue lines are not closed Fano atoms. Their sides are not exact elements, so the theorem says nothing
  about them, and FAR-READ A found atoms acting as one there in only 452 of 731 cases.
- **Doctrine.** The far sides are the creation map's four census far sides. Creation is an OR over local configurations at the gluing
  line (PENDANT-LINE A).

## What this does not establish

- **The exception.** It is left to computation (ticket C).
- **Exactness of the closed verdict in real spaces.** Check 3 shows bounding cannot give it. Ticket C measures it.
- **Non-Fano handles, and lines of glue.**

## Novelty

- **New here.** Theorem 1's extension to mixed pairs, Theorem 2, and the corollary.
- **Method.** Bounding an OR over local configurations by feeding every compatible relation at once is GLUE-READ A's.
