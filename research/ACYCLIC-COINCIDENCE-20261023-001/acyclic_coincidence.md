# Equal acyclic counts without isomorphism

Epic `ACYCLIC-COINCIDENCE-20261023-001`, closed 2026-10-23.

## The question

The owner approved this as a short side route with a strict stop rule: "find the identity, or show it's a one-off
coincidence".
- **What was left open.** `TWIST-MAP-20261023-001` explained every exact twist relation on its genus-2 surfaces skeleton by
  skeleton, except six on L(3,1,3,1).
- **What was odd about them.** On 48 skeletons of those six relations, the two twists' shrunken signed graphs have the same number
  of acyclic orientations (for example 54 and 54). Yet they are neither isomorphic nor Tutte-equivalent (for example 20 and 21
  bases).
- **The lead.** The owner's framing pointed to Zaslavsky: the number of acyclic orientations of a signed graph is a value of its
  chromatic polynomial.

**The evidence:**
- [The path-sign move](../../proofs/ACYCLIC-COINCIDENCE-20261023-001A/ACYCLIC-COINCIDENCE-20261023-001A-P001_path_sign_move/proof.md)
  (A, proof, with a standard-library check of all 48 skeletons);
- the residue itself, read from the artifact of `TWIST-MAP-20261023-001B-E001`;
- **scoping (scratch, not evidence):** three short scripts, described below.

## Outcome in one paragraph

**The identity exists, and it is elementary.**
- **The move.** Take a path through vertices of degree 2 whose two ends are also joined directly by a positive and a negative link.
  Flipping the path's sign changes nothing that counts colourings: not the chromatic polynomial, not T(x, 0), and so not the
  number of acyclic orientations. It does change the Tutte polynomial.
- **Why.** The doubled link forces the ends' colours to differ in both senses, c(a) ≠ ±c(b). A path's sign only decides
  whether c(a) = ±c(b) is excluded, which is already ruled out.
- **The residue.** In each of the 48 skeletons, one such flip turns one twist's shrunken graph into a graph whose frame matroid
  is isomorphic to the other's.
- **The consequence.** The genus-2 twist map has no unexplained residue. Every exact relation found there holds skeleton by
  skeleton through walls, symmetries, isomorphic pieces, or isomorphic pieces after this move.

## How it was found

| Step | Result | Status |
| --- | --- | --- |
| Hypothesis 1: the graphs differ only in parallel copies, which T(x, 0) ignores | False: all 96 shrunken graphs are already simple | Scoping |
| Compare T(x, 0) as a polynomial, not just at x = 2 | Equal in all 48 pairs: an identity of chromatic polynomials, not a coincidence of one value | Scoping; proved for all 48 by the check |
| Look at the differences | Each pair differs by the sign of one edge into a vertex of degree 2, on a path between two points already joined by links of both signs | Scoping |
| Colouring argument | A path's sign is invisible when its ends are forced apart in both senses (Lemma 1, Theorem 2) | Proved |
| Canonical form (set each such path's sign to +) | Explains 41 of 48; the other 7 differ by a switching at an end, which moves the flip onto another path | Scoping |
| Search over flips, up to frame-matroid isomorphism (which ignores switching) | One flip explains all 48 | Proved by the check |

## Assumptions in the workspace this challenges

| Assumption | Where it lives | Verdict |
| --- | --- | --- |
| The six relations rest on equal acyclic counts with no structure behind them | `TWIST-MAP-20261023-001` decision note ("measured, not explained") | **False.** They come from equal chromatic polynomials, caused by one local move. |
| Isomorphic reduced pieces are the right notion of "same piece" for counts | `TWIST-MAP-20261023-001A-P001`, Theorem 2 | **Too strict for the acyclic factor.** It is a function of the chromatic polynomial, and the path-sign move keeps that without keeping the matroid. |
| Series edges outside clusters cannot be merged | `TWIST-MAP-20261023-001A-P001`, Corollary 1 (merges only parallel edges outside) | **Correct in general**, since series merging changes T(x, 0). But next to a doubled link a series path's sign drops out. |
| The coincidence might be a one-off of the value at λ = −1 | The ticket's own stop rule | **False.** The whole polynomial agrees. |

## Provenance and novelty

| Result | Where it came from | Novelty |
| --- | --- | --- |
| Lemma 1 (colourings along a path) | Switching plus the walk count in a complete graph | Textbook |
| Theorem 2 (the path-sign move, with the closed form χ_G = χ_H ((λ − 1)^k − (−1)^k)/λ) | The colouring view of Zaslavsky's chromatic polynomial | A gluing along the doubled edge ±K₂, the signed analogue of the classical clique-cutset formula. High folklore risk. Not found stated in a short search (Greaves, Syatriadi and Utomo, arXiv:2407.00883, build co-chromatic signed graphs that are not switching isomorphic by other means; a 2026 abstract by de Vera studies clique cut sets for zero-free equivalence) |
| All 48 residual skeletons explained; the genus-2 map has no residue | The check, on the recorded residue | A recorded computation; new to the program |

**Did the perspective do real work?** Little. The mathematics is classical colouring theory. The program's picture adds only a
reading: two points joined by both signs form the smallest odd loop, and that loop hides the sign of every parallel path from the
acyclic count. This is the same shape as the lone-loop shield of `LOOP-SHIELD-20261023-001`, at the scale of one digon and only
for the acyclic factor. It is an interpretation, not a theorem about shielding.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — the identity behind the six residual relations | **Successful** | The stop rule's first branch is met: an identity (the path-sign move) explains all 48 skeletons, by proof and an exhaustive check. |
| Local direction — exact twist relations of the two-literal model on genus 2 | Practically exhausted; retire | Every relation found is now explained skeleton by skeleton. Further surfaces would re-map known mechanisms. |
| Broader exploration — twisted worlds | Moving to three places | The main route, `TRIPLE-SHIELD-20261023-001`, is testing whether shielding survives at three places (frozen exhaustive counts running). |
| Long-term goal — emergence at the two-literal/three-literal boundary | Capability gained (small) | The two-literal side's exact relations are now fully local on genus 2. The missing bridge is whether any exact relation survives at three places. |
| Next recommendation — dual pairs for three-place lines | **Next step:** Full pivot from this side route to the main route, `TRIPLE-SHIELD-20261023-001`, already under way. Retained: the path-sign move and the complete genus-2 map. Reopen this line if a three-place relation turns on acyclic or chromatic counts. | The side question is settled; its refinements lose to the thesis-boundary test. |
| Interest — that next step | **2/3 — Promising** | Lines at three places run along odd classes, as two-literal loops do (proved). Scoping on 3 × 3 shows dual pairs unequal at three places unless a symmetry relates them, so the likely answer is negative, and informative. |
| Execution — that next step | Started | The frozen experiment `TRIPLE-SHIELD-20261023-001A-E001` is running (exhaustive counts on four tori, about an hour); the proof ticket B follows its result. |
