# Twists in three dimensions

Epic `TWIST-3D-20261025-001`, closed 2026-10-25.

## The question

The owner asked to pivot to the recommendation made at the close of `LOOP-HUB-20261025-001`.
- **What was known.**
  - Symmetric edge-bit laws see a closed three-manifold only through |H¹(M; Z/2)|, and the Fibonacci rule needs a negative weight
    (`HUB-DIMENSION-20261024-001`).
  - The six open knots are the Fibonacci knot with a twist, which is a signed reflection in the Fibonacci basis
    (`NATIVE-APPROX-20261024-001B`).
- **The question.** Do twists let bits see more of three dimensions, or let positive weights replace the sign?
- **Intuitions this epic targets:** space comes from logic, now in three dimensions; it also bears on the sign shared with the
  complexity side.

**The evidence:**
- [Twists add nothing to counting laws in three dimensions](../../proofs/TWIST-3D-20261025-001A/TWIST-3D-20261025-001A-P001_twists_add_nothing_to_counting/proof.md)
  (A, proof; exhaustive census);
- [The sign survives the twist](../../proofs/TWIST-3D-20261025-001B/TWIST-3D-20261025-001B-P001_the_sign_survives_the_twist/proof.md)
  (B, proof; exhaustive support classification and an exact gauge computation);
- [bounded scan](scan.md);
- **scoping (scratch, not evidence):**
  - the SAT census;
  - the first evaluations on triangulations, where a bug in the vertex-link test was found and fixed before the census was
    formalized;
  - positive-weight least squares, where a residual that vanishes as all weights shrink was replaced by a scale-free one;
  - numerical solutions on the parity sector.

## Outcome in one paragraph

**Twists add nothing, and the sign survives them.**
- **Counting laws (A).** On ordered triangulations, each triangle can read its three edges in vertex order, so any triangle rule can
  be used, the twisted Fibonacci knots included, with tetrahedron rules that may even depend on orientation.
  - Exactly 354 laws survive the ordered 2–3 and 1–4 moves over all 255 triangle rules. They are the same seven symmetric laws as
    before, wherever the triangle rule contains what they need.
  - None uses an asymmetric part of its rule, and none uses orientation.
  - Each twisted Fibonacci knot keeps just one constant law and its one parity law.
- **Positive weights (B).** In Turaev–Viro form the Fibonacci and twisted Fibonacci supports always contain an identity with positive
  terms on one side only. So positive weights cannot have full support.
  - Every positive weighting lives on constants or on the parity class.
  - On the parity class the weights are pure gauge, and the state sum is |H¹(M; Z/2)|/2.
- **Conclusion.** With one bit per edge, counting sees three-dimensional space only through its mod-2 first cohomology, twisted or not,
  and seeing more needs signs.

## How it was found

| Step | Result | Status |
| --- | --- | --- |
| SAT census of ordered laws | 354 laws, all among the seven symmetric ones | Scratch |
| Evaluate them on triangulations by homology | All are functions of \|H¹(M; Z/2)\| | Scratch; confirmed in A |
| Exact census with unit propagation, standard library | Same 354; orientation never matters | Proved (A) |
| Positive full support | One-sided identities for all eight non-windable knots | Proved (B, Theorem 1) |
| Positive supports | Constants, parity class, parity class with one constant | Proved (B, Theorem 2) |
| The parity class | The logarithmic 2–3 system is exactly the gauge span | Proved (B, Theorem 3) |

## What was proved

| Result | Content |
| --- | --- |
| A, Theorem 1 | Ordered counting laws invariant under ordered moves are exactly the seven symmetric laws inside each triangle rule: 354 laws, never orientation-dependent. |
| A, Corollaries 2 and 3 | Invariant counts are 1, 2, \|H¹\|/2 or \|H¹\|; each twisted knot carries one constant law and one parity law. |
| B, Theorems 1 and 2 | No positive full support; positive supports are constants, the parity class, or (no-lone knots) the parity class with one constant. |
| B, Theorem 3 and Corollary 4 | On the parity class positive weights are gauge; every positive state sum is 1, 2, \|H¹\|/2 or \|H¹\|/2 + 1. |

## What this changes

- **Three dimensions are closed for bits.**
  - Native face bits are blind (`HUB-DIMENSION-20261024-001A`).
  - Edge bits see only mod-2 cohomology: with symmetric rules (`HUB-DIMENSION-20261024-001A`), with twisted or ordered rules, with
    orientation-dependent rules, and with positive weights (this epic).
- **The sign is the boundary, in both lines.**
  - In the complexity line the six open knots are where Fibonacci meets a twist.
  - In the space line the twist cannot supply the sign that Fibonacci needs in three dimensions.
  - In both, everything unsigned is settled.
- **Seeing more needs bigger distinctions.**
  - Counts with labels from a finite group G see homomorphisms π₁(M) → G (Dijkgraaf–Witten, untwisted). That is far more than mod-2
    cohomology for large or non-abelian G, and it is still a count.
  - Bits cannot form such groups, but patterns of bits can. Three-dimensional space from counting therefore needs patterns of patterns.

## Assumptions in the workspace this challenges

| Assumption | Where it lives | Verdict |
| --- | --- | --- |
| A twist, a native sign in the Fibonacci basis, might stand in for Fibonacci's negative weight | The recommendation behind this epic | **False.** Positive weights cannot use it: the twisted supports force one-sided identities. |
| Orientation or vertex order might give bits more three-dimensional information | Implicit in ordered state sums | **False for one bit per edge.** No surviving law depends on either. |
| Seeing more three-dimensional topology requires signs | The reading of `HUB-DIMENSION-20261024-001B` | **Refined.** It requires signs for bits. With larger labels, counting with finite groups already sees more. |

## Provenance and novelty

| Result | Where it came from | Novelty |
| --- | --- | --- |
| A | Exhaustive census of ordered Boolean laws | `candidate-local-delta`; folklore risk low to medium |
| B, Theorems 1 and 2 | One-sided identities, support enumeration | `candidate-local-delta`; folklore risk medium |
| B, Theorem 3 | Logarithmic linear algebra and gauges | The classical fact that positive real cocycles of finite groups are trivial, in local form |

**Did the perspective do real work?** Partly.
- **What it supplied.** The question joins two of the program's own threads: the twisted knots of the complexity line, and the
  Fibonacci sign of the space line.
- **What is negative.** The answer is a clean negative that closes the bit-level route to three dimensions.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: twists in three dimensions | **Status:** Successful (negative) | Twisted and ordered laws, and positive weights, see only mod-2 cohomology; the stop condition was met and then proved. |
| Local direction: bits on triangulations | Practically exhausted | Every bit-level variant tried (face bits, symmetric edge laws, ordered and twisted laws, orientation, positive weights) is settled. |
| Broader exploration: space from logic | Known alternatives | Composite labels; signed state sums, which are not counts. |
| Long-term goal: space comes from logic | Capability gained | Surfaces come natively (two dimensions); three-manifolds through bits only up to mod-2 cohomology. The lever left is the size of the distinctions. |
| Next recommendation: patterns of patterns in three dimensions | **Next step:** Continue, with a fresh epic | See below. |
| Interest: that recommendation | **2/3: promising** | It ties two intuitions, patterns of patterns and space from logic, by asking how much composite structure is needed to see which topology. Main uncertainty: the answer may be exactly the classical group counts. |
| Execution | Deferred to the owner | Bound: one epic; stop if only group laws survive (then counting sees exactly homomorphism counts). |

**The next step in more detail.**
- **The question.** Which counting laws with composite labels (three or four states per edge, built from bits) survive the ordered
  moves, and what do they see?
- **The first discriminator.** A census of function-type laws, where the third edge of each ordered triangle is a function of the
  other two, over all magmas of orders 3 and 4 up to isomorphism, under the ordered 2–3 and 1–4 identities.
  - Prediction to test: only groups survive, and their counts see H¹(M; Z/3), H¹(M; Z/4) and H¹(M; Z/2)².
  - A surviving non-group structure would be a discovery.
- **The reading.** Seeing mod-3 information, for example telling the three-sphere from L(3,1), which bits cannot, requires a distinction
  made of patterns of bits.

**Alternatives:**
- **A note on Boolean state sums in three dimensions (1/3).** It would collect `HUB-DIMENSION-20261024-001` and this epic. Magnitude
  moderate.
- **Signed counts as a native resource (1/3).** What do differences of witness counts buy, and at what cost?
- **Back to the complexity side (1/3).** The arm inequality's global proof.
