# Referee report PIN-RULE-R1: the pinning theorem

**Verdict: Confirmed with fixes.** The theorem, its restatement of "spare" and the harmony corollary all hold. I checked the proof line
by line and proved the theorem again by a different argument, a majority over the three copies plus Hall's condition, in
`../../SUBST-NEST-20261112-001/referee-R1/report.md`, section 2. One claim is false as stated: section 3's "pins never vary under any
block triples closed under reordering". With the diagonal, a pattern that holds an opposite tie of its own pins two copies unequal.
The fix narrows the claim to the block's knots in every order, where the theorem already gives equality for every pattern.

Referee: the background referee thread, 2026-11-12. It used its own code (`ref_pin_checks.py` here, and `ref_subst.py` in the
SUBST-NEST referee folder). It did not import `subst_lib.py` or the epic's `check.py`. Validation: V2. The advisor model was
consulted once, on the referee's own proof, which it found correct.

## 1. The claims

**(1) The theorem holds.**
- **The proof's steps.** With a_p = 0 and b_p = 1, the four between-copy knots it names do exclude c_u = c_w = 0 (b would be constant
  on {p, u, w}) and c_u = c_w = 1 (a would be constant). So c, which already holds both values on every knot that avoids p, is a
  spare witness. The other pairs of copies follow by reordering, which uses all six orders.
- **A distinction in no knot of B** is spare: every state survives flipping it. So the theorem says nothing about it, and N6 frees it.
  It is handled correctly.
- **Repeated distinctions of P** are excluded by the definition, since knots hold three distinct distinctions. If one were allowed,
  two copies would coincide and the argument would still go through by reorder-closure. That case is outside the definitions, and
  nothing rests on it.
- **The computed side.** In my own census, a part is pinned exactly when it is not spare in all 870 living tests of the 87 blocks.
  The whole tie relation has the closed form given in the SUBST-NEST referee report. Pins on one part are equalities, and pins
  across parts carry the block's relation.

**(2) The restatement holds, both ways in a line each.**
- A spare witness u gives two states, u with p = 0 and u with p = 1.
- Conversely, if t and t with p flipped are both states, every knot through p has its other two members unequal in t. So t without
  p is a witness.

**(3) The harmony corollary matches the earlier definitions; it is not a look-alike.**
- The cyclic block's states are exactly ODD-FAMILY's compatible words: words on Z_n that are non-constant on every {x, x + s, x + 2s}.
- Spare means flippable, by (2) and ODD-SEARCH's lemma 5.
- ODD-FAMILY defines "S makes a harmony at n" as "some compatible word, none with a flippable residue".
- So the corollary is (2) plus definitions, and holds for a living block. The proof's section 5 says "when compatible words exist".
  The decision note's bullet drops that condition (fix 2).

**(4) "Pins never vary" is false as stated for the diagonal.**
- **The counterexample.** P is the Fano plane less the knot {2, 4, 5}, which forces 2 = 4 = 5, plus the knot {2, 4, 7}, which then
  forces 7 ≠ 2. The block is K4, all four knots on four distinctions. Under the diagonal, (2, p) and (7, p) are tied unequal for every
  p (`result_pin_checks.json`): a pin that is an inequality.
- **Where the argument breaks.** "Three pairwise inequalities in a knot are impossible" treats the forced relation as symmetric in
  the copies. That holds for one knot of P on its own. In a larger P, the pattern's own ties break the symmetry, so ties between
  copies need not be symmetric and need not be equalities.
- **Where the claim does hold.** With the block's knots in every order the claim holds for every P, by the theorem itself: the same
  example gives equality there. With patterns that hold no ties of their own, the diagonal pins nothing, which is how
  SUBST-NEST's S1 was tested. So "with the diagonal nothing is pinned" in the sceptic paragraph also needs "for patterns with no ties
  of their own".

## 2. The account of what is built in

The account is fair. Two additions would make it complete.
- **The reach is automatic.** The frozen "influence growing with the pattern" criterion of SUBST-NEST, and the measured tie extent,
  follow from connectivity once one knot pins. That is the "wire" in the account, and it is worth saying that the measurement
  therefore tests nothing beyond the local pin.
- **Novelty.** The advisor notes that the ingredients are standard: a majority over three solutions with Hall's theorem, and a
  single-flip freedom close to the free and frozen variables of the random-CSP literature (whitening). Novelty is unverified, and
  the folklore risk is real.

## 3. Fixes for the thread

1. **Section 3 and the decision note's "Pins never vary (proved)".** Narrow both to: with the block's knots in every order, for every
   pattern. Under the diagonal, pins between copies are the pattern's own ties, inequalities included, and none when the pattern holds
   no ties. The sceptic line "with the diagonal nothing is pinned" needs "for patterns with no ties of their own". **Narrowing**
   (Overreading). Not a block for the theorem.
2. **The decision note's harmony bullet** needs "for a living block", or "when compatible words exist", as the proof has it.
   **Not a block** (wording).
