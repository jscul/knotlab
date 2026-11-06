# The knot's amplitude on its spaces

Epic `THREEFOLD-AMPLITUDE-20261030-001`, 2026-10-30.

## The question

- **The owner's request (2026-10-30).** "Yes, let's continue on that." This approved the recommendation of
  `THREEFOLD-SURFACES-20261030-001`: prove that the knot's exactness factor λ(0) on a three-fold space is 5 per handle times a factor from
  planar glue, and identify that factor.
- **Setting.**
  - λ(0) is the number by which a gadget of the knot reproduces the knot: R = λ(0) · knot.
  - Through the duality of `SPACE-SELECTION-20261030-001C` it is a count of 2-colourings of the space's dual triple system H.
  - The space decomposes along tight 3-edge cuts into Fano atoms (Heawood graphs, each one handle of the surface) and glue (doubled squares,
    planar braces, trisums).
- **Scoping probe (not evidence).** λ(0) = 5^genus at every corner line on twelve spaces with doubled-square glue. The twisted cube, whose
  glue includes the planar cube, gives 2·5⁶.
- **Intuitions targeted:**
  - space from a law (question 9 of the knot intuition doc);
  - everything is relational: is the number a property of the whole space or of where it is opened?

**The evidence:**
- [Five per handle, Tutte's number per planar piece](../../proofs/THREEFOLD-AMPLITUDE-20261030-001A/THREEFOLD-AMPLITUDE-20261030-001A-P001_five_per_handle_tuttes_number_per_planar_piece/proof.md)
  (A, proof).
- [One amplitude for every non-colourable cubic system](../../proofs/THREEFOLD-AMPLITUDE-20261030-001C/THREEFOLD-AMPLITUDE-20261030-001C-P001_one_amplitude_for_every_non_colourable_cubic_system/proof.md)
  (C, proof; added during the epic, after a trisum probe).
- [The amplitude by computation](../../proofs/THREEFOLD-AMPLITUDE-20261030-001B/THREEFOLD-AMPLITUDE-20261030-001B-P001_the_amplitude_by_computation/proof.md)
  (B, exhaustive and exact computation).
- **Literature.**
  - Tutte's tree-trinity theorem (1948), in the Tutte-matching form presented by Mathews (arXiv 1702.03630).
  - Kálmán's hypertrees (arXiv 1103.1057).
  - Berman's determinant formula (1980).
  - Valiant's Holant theorem.
  - Two searches found no statement counting the colourings of a Kasteleyn-signed planar triple system, and none of corner independence.

## Outcome in one paragraph

**Yes, and the factor is Tutte's tree-trinity number. The amplitude is also one number for the whole space.**

- **The product formula (A).** λ(0) = (−1)^(n−1) · 5^(Fano atoms) · Π ρ(P) · 6^(trisums of three cubes).
  - **Planar glue.** ρ(P) is Tutte's tree-trinity number of each planar glue piece. For the omnitruncation of a planar map it is the number
    of spanning trees of the map; in general it is Kálmán's hypertree count.
  - **Doubled squares** contribute 1. So with doubled-square glue |λ(0)| = 5^genus.
  - **The mechanism.** The colouring count factors exactly across every tight cut, through a point lemma.
  - **Planar braces.** A Kasteleyn sign condition turns colourings into pointer systems, and a counting argument makes these exactly Tutte's
    matchings.
- **One amplitude (C).** For every connected cubic triple system that is not 2-colourable, the count is the same whichever line is removed.
  It is also the same for the transposed system (points and lines exchanged) whichever point is removed.
  - **Proof.** Place an Ising weight with couplings ±iπ/6, half the knot's angle, on the incidence graph. Summed over either side it becomes
    the not-all-equal constraint on the other. Counting one marked line in both orders makes each line's count the average of its points'
    counts, and vice versa. A maximum principle on the connected incidence graph then forces a single value.
  - **Consequence.** Every brace, planar or not, has one amplitude, and the product formula holds for every three-fold space.
- **Computation (B).**
  - Exhaustive on the census (2,652 classes up to 10 points).
  - The law at every corner of every space up to 22 points.
  - Planar glue: 13 omnitruncations, up to the dodecahedron (5,184,000 at all 60 lines), and 6 hypermaps.
  - Trisums of prisms: one amplitude, which depends on how they are glued. (2,3,3) gives 13 or 14, and (4,4,4) gives 36 or 52.

## What was proved

| Result | Content |
| --- | --- |
| A, Theorem 2 | λ(0) = (−1)^(n−1) A(H, L₀), with A the number of colourings of H − L₀ with L₀ fixed. |
| A, Lemma 3 | Point lemma: at a point of a non-colourable system, the colourings of the rest with one incidence complemented number A(H, ℓ_i). |
| A, Theorem 4 | Factorization across a tight cut: A(H, L) = a(B) · A(H′, L). |
| A, Proposition 5 | Heawood 5, doubled square 1, planar brace = Tutte matchings = ρ(P) (= τ(M) for Omni(M)), trisum of three cubes 6. |
| A, Theorem 6 | Product formula for spaces whose braces are of those types. |
| C, Lemma 2 | Two-way count: #col(H) + 6N_H(L) = 2Σ_p M_{Lp} N_{Hᵀ}(p) + R(L) for every cubic signed system; #col(H) = #col(Hᵀ). |
| C, Theorem 3 | One amplitude: A(H, L) = A(Hᵀ, p) for all lines L and points p, when H is connected and not colourable. |
| C, Lemma 4 | Signed dictionary: not colourable ⟺ Pfaffian, and then minimal. |
| C, Corollaries 5–6 | Product formula for every non-colourable cubic system; Tutte matchings independent of the outer triangle and its colour. |
| B | Census (2,652 classes), the law at every corner up to 22 points, omnitruncations, hypermaps, 44 + 6 trisums. |

## Reading

- **The knot's own number measures what it builds.**
  - Each handle of the surface (each Fano atom) contributes exactly 5.
  - Flat glue contributes a classical count of trees: the spanning trees of the map it is cut from, or Tutte's tree-trinity number in general.
  - The sign is the parity of the number of triangles.
- **The number belongs to the whole space.**
  - It does not depend on where the space is opened. It also does not depend on whether the space is read from its triangles or from its
    contacts.
  - That is the relational point: no contact is privileged.
- **A three-place phenomenon.** The two-way count works because, at half the knot's angle, summing out a vertex of degree three gives exactly
  not-all-equal. The same trick does not produce not-all-equal for four-place contacts.
- **What λ(0) does not tell.** It does not determine the genus alone: the 10-prism glue contributes 5 too. Non-planar glue (trisums)
  contributes a number that depends on how its pieces are glued, not only on the pieces.
- **Limits.**
  - λ(0) is treated on three-fold odd gadgets with distinct corner triangles.
  - The values of non-planar glue other than the trisum of three cubes are computed, not given in closed form.
  - The complex weight is a counting device.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — the knot's amplitude on three-fold spaces | **Status:** Successful | The owner's question is answered and extended. The planar factor is Tutte's tree-trinity number, and the amplitude is proved to be one number per space for every non-colourable cubic system. |
| Local direction — λ(0) on three-fold spaces | Practically complete | Open only for the values of non-planar glue (trisums), which depend on the gluing; a formula from boundary data of the pieces is possible but would be completion work. |
| Broader exploration — space from a law (question 9) | Known alternatives | The knot's spaces now have surfaces and numbers. Unmapped: whether the knot's own signs give its surface further structure (spin), spaces with boundary, mixed contact sizes. |
| Long-term goal — space from logic without a drawn space | Capability gained | The knot's quantitative output is a topological and relational invariant of the space it builds: 5 per handle, trees per flat piece, independent of the vantage point. |
| Next recommendation — the knot's spin structure | **Next step:** Continue, as a fresh epic. Does the knot's own (trivial) signing satisfy Kasteleyn's face condition on every minimal map of every three-fold space, so that each space carries a canonical spin structure on its surface? If so, find its Arf invariant per Fano atom, and whether λ(0) arises from the surface's 4^genus-term Pfaffian (Ising) expansion. Scratch evidence (not evidence of the claim): every face of the minimal maps up to 19 points has length 2 mod 4 (`THREEFOLD-SURFACES-20261030-001B`). | Ties the knot's signs to the topology it builds. A yes would make the surface a spin surface determined by logic; a no would locate where the knot's signs and its surface part ways. |
| Interest — that recommendation | **2/3 — Promising** | The face-length data are suggestive, and Kasteleyn structures on surfaces correspond to spin structures. Main uncertainty: the face condition may follow formally from Pfaffian-ness plus minimal genus, leaving little new meaning. |
| Execution — that next action | Deferred to the owner (fresh epic) | Done so far: this epic. First discriminator: test the face condition on the minimal maps of spaces with planar and trisum glue (twisted cube, 35-point trisum space). Stop if it fails there, or once the spin structure and its Arf invariant are identified. |

**Recommendation.** **Continue**, as a fresh epic: the knot's spin structure (2/3). Two alternatives were considered.
- **The trisum law and polynomial time (1/3).** Express a trisum's amplitude through boundary counts of its pieces. That would make λ(0)
  computable in polynomial time on every three-fold space, via the Robertson–Seymour–Thomas decomposition. It is completion-like.
- **A short note on the one-amplitude theorem (1/3).** A clean combinatorial statement about minimally non-2-colourable cubic hypergraphs.
  It needs a deeper literature check first. The owner asks for write-ups only for results of real magnitude.
