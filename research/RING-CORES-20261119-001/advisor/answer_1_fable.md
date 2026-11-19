**Verdict:** steps 1–4 check out from the text, with one gap in the S3 argument and two wording fixes to the headline. I could not check the class definition itself, only what you state here.

## 1. Steps

- **Shape.** Right. d_c = 2 + ℓ_{c−1} + ℓ_{c+1} and deg_c = 2 + ℓ_c give your inequality, and the forced open counts follow. No ray arises, since every pendant sits on a knot with open ≥ 3.
- **Leaf through an outside block.** No. A leaf lies in exactly one block, and no block holds two leaves. If both line points of its block are outside, the leaf reaches only its own spares, which is your second kind. "Edges meeting [i,j]" must include the two boundary edges, j − i + 2 edges in all; W's product over all n edges per period confirms you count it that way.
- **Reading of a 3-point block.** This assumes the block is one cell (points x_k, x_{k+1} and the leaf mutually joined, with no cycle of its own). If the engine unrolled it as a 3-cycle, the cover would differ. The leaf pilots matching says it does not.
- **Even L.** Right, with one thing to state outright: a leaf of c_i decorates the piece of the opposite parity to i, while a spare on c_j decorates the piece of j's own parity. So C10 with a leaf and a spare has two cases:
  - same piece (i and j of opposite parity): W = z^5(1+z)^2, rate 1.2628;
  - different pieces (same parity): each has W = z^5(1+z), rate 1.1347 (x^6 = x + 1).

  This is a sharp test of the assignment; check which case your pilot ran.
- **ρ.** Right. W has non-negative coefficients, W(0) = 0, W(1) > 1 and W′ > 0, so there is one simple root in (0, 1). On |z| = ρ, |W(z)| = 1 forces z^n and z^{n+1} to have the same argument, so z = ρ. The numerator is a nonzero polynomial with non-negative coefficients, so it does not cancel the root. The bare case does cancel, to nz/(1 − z), as you say.
- **Orbit count.** Fine: clusters are finite, so stabilisers are trivial and "leftmost point in a fundamental domain" counts each orbit once.

## 2. Class

- **Cycles.** The only cycle is the ring, so L ∉ {3, 4, 6} suffices. Candidate triples among core knots need 6 ≡ 0 mod L, so they are excluded.
- **Gap in S3.** A leafed core knot c_i has three neighbours (c_{i−1}, c_{i+1} and the leaf), which are pairwise candidates with a common neighbour. Your dichotomy "6-cycle or common neighbour" lands in its second branch here and does not exclude it. This is also exactly the "first-round group of three" on your outside list.

  Either S3 allows a common-neighbour triple when p_c ≥ deg_c + d_c, which is how the refereed C7 with a leaf must pass, or the leafed rings need a separate line. Say explicitly which; I cannot tell from this text.

## 3. Predictions

The rate depends only on n, A and the b's per piece, never on positions.

| Start | Equation | Rate |
|---|---|---|
| C5, two spares | x^7 = (x + 1)^2 | ≈ 1.2628 |
| C7, leaf b = 1, one spare | x^10 = (x + 1)(x^2 + x + 1) | ≈ 1.2377 |
| C9, three leaves b = 0 | x^12 = (x + 1)^3, i.e. x^4 = x + 1 | ≈ 1.2207 |
| C14, one spare | x^8 = x + 1 on the spare's piece; the other piece is bare, +7 per round | ≈ 1.0970 |

- **C5:** adjacency of the two spares is irrelevant to the rate.
- **C14:** same rate as C7 with a leaf, but not the same counts.

## 4. Headline

Your outside list is right as far as I can see. I would add starts with p_k < deg_k + d_k, if the class excludes them. Three fixes to the wording:

- **Say "every knot live".** The claim is only for all-live starts.
- **"Exactly" needs star cores.** You cite the tree dimension theorem for path cores only. Cite or prove the star case too; it should follow because an acyclic K̄ gives an acyclic map, but that rests on what the relay and rays do, which I cannot check here.
- **W is per piece.** For even L there are two W's and the rate is the larger root; one piece can be bare while the start still grows. Also "piece" now means both a component and a factor of W; call the three "factors".

Suggested wording: "Within the cap, in the class, with every knot live, a start grows exponentially exactly when its core is a ring carrying a leaf or a spare; each piece's round-weight is a product of three kinds of factor."
