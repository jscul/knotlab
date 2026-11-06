# Dimension three through hubs

Epic `HUB-DIMENSION-20261024-001`, closed 2026-10-24.

## The question

The owner asked to continue both directions recommended at the close of `SURFACE-GLUING-20261024-001` and
`NATIVE-HARDNESS-20261024-001`. This epic took the space direction.
- **What was known.** Native gluing builds surfaces.
- **The question.** What do bits see of a three-manifold once distinctions sit on the edges of a triangulation, each shared by every
  triangle around its edge, which makes them hubs?
- **Intuitions this epic targets:** space from logic without a drawn space; everything relational (the Fibonacci harmonies).

**The evidence:**
- [Bits see a three-manifold only through its mod-2 cohomology](../../proofs/HUB-DIMENSION-20261024-001A/HUB-DIMENSION-20261024-001A-P001_bits_see_mod2_cohomology/proof.md)
  (A, proof);
- [The Fibonacci rule needs a negative weight in three dimensions](../../proofs/HUB-DIMENSION-20261024-001B/HUB-DIMENSION-20261024-001B-P001_fibonacci_needs_a_sign/proof.md)
  (B, proof);
- [bounded scan](scan.md) (Pachner moves, Dijkgraaf–Witten, Turaev–Viro, sign problems, the one-tetrahedron census);
- **scoping (scratch, not evidence):**
  - the first census on simplicial spheres, which stalled when six vertices filled every edge;
  - the Gröbner basis of the weighted Fibonacci identities;
  - the one-tetrahedron enumeration.

## Outcome in one paragraph

**Dimension three is not native, and bits see it only faintly.**
- **Native networks are blind (A).** A native network of a triangulation, with bits on faces each shared by two tetrahedra, is only
  the dual graph with slots. The sphere and L(4,1) have one-tetrahedron triangulations with the same native network.
- **With hubs, bits see only mod-2 cohomology (A).** Put the bits on edges, which are shared by every triangle around them. Among all
  32,768 symmetric laws (one rule per triangle, one per tetrahedron), the laws whose counts survive the 2–3 and 1–4 moves are four
  trivial ones and three parity ones.
  - Parity counts flat connections: |H¹(M; Z/2)| · 2^(V−1).
  - Every other law breaks on explicit moves.
  - So no bit law of this kind separates the sphere from L(5,2), and everything it sees is already in the two-dimensional skeleton.
- **Fibonacci needs a negative weight (B).** The Fibonacci rule sees surfaces exactly (`SURFACE-GLUING-20261024-001`). To see a
  three-manifold in Turaev–Viro form it needs real weights, and the move identities force the all-τ tetrahedron weight to be
  −(W₉ t₂)² < 0. No count of hidden witnesses supplies that. An exact solution exists, with edge weight φ and vertex weight 1/D².

## How it was found

| Step | Result | Status |
| --- | --- | --- |
| Local census of symmetric edge laws under the two moves | 5,703 of 32,768 masks pass, reducing to seven laws: trivial or parity | Proved (A, Theorem 1) |
| Global test on simplicial spheres | Six vertices already fill every edge, so 2–3 moves stop; switched to singular triangulations | Scoping |
| Moves on singular triangulations from the one-tetrahedron sphere, L(4,1) and L(5,2) | 65 sampled moves keep validity and H₁; every passing law keeps its ratios and every failing law breaks | Proved (A, Proposition 4) |
| Parity against cohomology | count = |H¹| 2^(V−1) on all 65 triangulations | Proved (A, Theorem 3) |
| One-tetrahedron census | The sphere, L(4,1), L(5,2), as in Burton's census; the sphere and L(4,1) share a face pairing | Proved (A, Proposition 5) |
| Weighted Fibonacci identities | 19 polynomial identities; a negative all-τ weight is forced by three of them; exact solution in Q(√5) | Proved (B) |

## What was proved

| Result | Content |
| --- | --- |
| A, Theorem 1 and Corollary 2 | The symmetric edge laws satisfying the move identities are all 0, all 1, all equal, free, even parity, odd parity, and even or odd; their normalized counts are constants or |H¹(M; Z/2)| up to a factor. |
| A, Theorem 3 | The even-parity count is |H¹(M; Z/2)| 2^(V−1) (flat connections). |
| A, Proposition 4 | Every other law that is ever allowed breaks on explicit sampled moves. |
| A, Proposition 5 and Corollary 6 | Native networks see only the dual graph; bits see dimension three only through hubs and then only through mod-2 first cohomology. |
| B, Theorem 1 and Corollary 2 | Fibonacci weights of full support force d² = d + 1 and W₁₀ = −(W₉ t₂)² < 0: not a witness count. |

## What this changes

- **Space from logic stops at two dimensions natively.**
  - Native gluing builds surfaces. Dimension three needs hubs, the non-native sharing that also carries NP-hardness
    (`NATIVE-HARDNESS-20261024-001`).
  - Even with hubs, bits see only the mod-2 first cohomology, which the two-dimensional skeleton already determines.
- **The two/three boundary, revisited.** Two places give lines, and three places give surfaces. With bits, three places shared three
  ways (hubs) still give no genuinely three-dimensional invariant.
- **The relational intuition has a limit at counting.**
  - **In two dimensions** the Fibonacci incommensurables (5 ± √5)/2 cancel into integer counts.
  - **In three dimensions** they need a negative weight, so counting alone does not make them cancel.
  - **What is missing** is signed combination (interference), not more counting.

## Assumptions in the workspace this challenges

| Assumption | Where it lives | Verdict |
| --- | --- | --- |
| Hubs would supply dimension three | This epic's own framing, from `SURFACE-GLUING-20261024-001` | **Refined.** Hubs are necessary but give only mod-2 first cohomology for bit laws. |
| A law that sees surfaces exactly will see three-manifolds with suitable weights | The recommendation closing `SURFACE-GLUING-20261024-001` | **False for counts.** The Fibonacci rule needs a negative weight. |
| Space recognized, not created (`KNOT-SPACE-20261020-001`) | Earlier epics | **Unchanged in dimension three.** Bits on hubs recognize a cohomology group of a manifold they do not create. |

## Provenance and novelty

| Result | Where it came from | Novelty |
| --- | --- | --- |
| A, Theorem 3 and Corollary 2 | Cellular cohomology; Dijkgraaf–Witten for the two-element group | Classical |
| A, Theorem 1 and Proposition 4 | Finite census and sampled certificates | `candidate-local-delta`; no census found |
| A, Proposition 5 | Elementary; Burton's census | Classical facts, new reading |
| B | Three move identities | Known phenomenon (Fibonacci sign problem, F-matrix entry −1/φ); elementary certificate is `candidate-local-delta` |

**Did the perspective do real work?** Partly.
- **What it supplied.** The question, whether native or hub sharing builds dimension three, and the choice of laws (bits with symmetric
  local rules) came from the program.
- **What is classical.** The answers are classical facts: Dijkgraaf–Witten, Turaev–Viro, sign problems. The census and the certificate
  make them exact for the program's laws.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: dimension three through hubs | **Status:** Successful (an obstruction) | Native networks are blind to three dimensions; bit laws on hubs see only mod-2 first cohomology; the Fibonacci rule needs a negative weight. |
| Local direction: Boolean laws on triangulations | Practically exhausted | The symmetric census is complete; larger label sets leave the Boolean thesis, and weighted laws are not counts. |
| Broader exploration: topology program | Known alternatives | Native space is two-dimensional topology; geometry and higher dimension are absent at the Boolean base. Signed combination is the one ingredient the evidence names as missing. |
| Long-term goal: space from logic (question 9) | Obstruction learned | Dimension three is not native, and bits see only mod-2 cohomology of it. |
| Next recommendation: signed witnesses | **Next step:** Research directions | A bounded scan of whether signed witness counts are natural for the program (for example, witnesses weighted by the parity of a hidden bit), what they buy in three dimensions (Turaev–Viro), and what they cost in complexity. Classically these are differences of counts, as in GapP. |
| Interest: that search | **1/3: exploratory** | The evidence points at signs as the missing ingredient, but whether signs can be native is unclear; it may leave the program's counting view. |
| Execution | Deferred to the owner | Bound: one bounded scan; stop if signs cannot be read as native relations. |

**Alternative:** a full pivot away from space toward "patterns of patterns" (1/3). Native composition was already shown never to
create memory (`SURFACE-GLUING-20261024-001B`), which limits it.
