# Knots build exactly self-similar space in every dimension

Epic `SIMPLEX-GASKETS-20261029-001`, 2026-10-29.

## The question

- **The owner's request (2026-10-29).** "Yes, let's continue," on the recommendation of `SIGNED-GASKETS-20261029-001`. The tasks
  were:
  - prove exactness of the (d+1)-place standing wave on every level-k Sierpinski simplex in every dimension d;
  - decide when its factor is nonzero, and find for which (d, θ) its support is a knot;
  - compare with the program's three-dimensional obstruction (`HUB-DIMENSION-20261024-001`).
- **Setting.** SG^d_k is a d-simplex cut into k^d, keeping its C(k+d−1, d) up simplices. A (d+1)-bit law sits on each, glued at
  shared vertices, and R is the relation left on the d + 1 corners.
  - A law is exact when R = λw with λ ≠ 0.
  - Exactness at level k builds a tower: a finitely ramified self-similar space of similarity dimension log C(k+d−1, d)/log k, which
    tends to d.
- **Why it matters.** The previous epic built exact space of every dimension below 2 from a knot. The plane stayed out of reach, and
  three-manifolds had been found to show unsigned bits nothing but parity. Was 2 a limit of the mechanism or of the dimension?
- **Intuitions targeted:** space from logic without a drawn space; everything relational (harmonies as cancelling phases).

**The evidence:**
- [The standing wave reproduces itself on every Sierpinski simplex](../../proofs/SIMPLEX-GASKETS-20261029-001A/SIMPLEX-GASKETS-20261029-001A-P001_the_standing_wave_reproduces_itself_on_every_sierpinski_simplex/proof.md)
  (A, proof);
- [Signed laws on Sierpinski tetrahedra and the exceptional angles](../../proofs/SIMPLEX-GASKETS-20261029-001B/SIMPLEX-GASKETS-20261029-001B-P001_signed_laws_on_sierpinski_tetrahedra_and_the_exceptional_angles/proof.md)
  (B, proofs and exact census);
- scoping (scratch, not evidence): the first exact factors in dimensions 3 to 6, and the norms of the factor at angles π/q.

## Outcome in one paragraph

**A knot builds exactly self-similar space in every dimension.**
- **A (proved for every d and k).** The standing wave (−1)^(x₀) sin(θE)/sin θ reproduces itself on every Sierpinski simplex.
  - **The factor.** It is a monic integer polynomial in 2 cos θ, of degree d(#T − 1), equal to 2^N at θ = 0. At θ → 0 the wave
    becomes the linear law 1 + Σ s₀sᵢ, whose only surviving edge sets are the d edges of the big simplex.
  - **Where it vanishes.** Only at finitely many angles per level, and never at an angle jπ/q with q a power of an odd prime.
  - **Knots.** The Legendre member (−1)^(x₀)(E | 3) is an exact knot in every dimension d ≥ 2. In odd dimension every member is a
    knot: a continuous family of exact knots.
- **B.**
  - **The cosine wave.** It reproduces itself when the number of simplices is odd, and otherwise turns into the sine wave. This
    explains the period-4 family found in the plane.
  - **θ = π/4.** Both waves fail there at exactly the even levels, because the phases are frustrated along the edges between
    non-base corners.
  - **Parity** is exact at powers of 2 in every dimension. Odd parity is exact there only in even dimension.
  - **The census.** On Sierpinski tetrahedra (levels 2–5) and four-simplices (levels 2–3), the knots that reproduce themselves at every
    computed level are exactly standing waves. Everything else is tied to an arithmetic of k, or is sporadic.
  - **Exceptional angles.** The only rational ones are π/2 and π/4.
- **The comparison.** These spaces are finitely ramified and the laws are signed, so the three-manifold obstruction is untouched.

## What was proved

| Result | Content |
| --- | --- |
| A, Theorem 2 | For every d, k and every complex y, the corner relation of w^(y) = (−1)^(x₀) U_(E−1)(y/2) is λ_(d,k)(y) w^(y); at y = 2 cos θ this is the standing wave. |
| A, Theorem 3 and Lemma 4 | λ_(d,k) is monic in y, has integer coefficients, degree d(#T − 1) and that parity, λ(2) = 2^N; level 2: y^d (y² − 2)^(d(d−1)/2). The limit law's even edge sets are the empty set and the d axis paths. |
| A, Corollary 5 | Finitely many exceptional angles per level, none at odd prime-power angles; the Legendre factor ≡ (−1)^N (mod 3). |
| A, Proposition 6 and Corollary 7 | For d ≥ 2 and sin 2θ ≠ 0, the support is a knot iff d is odd or θ = jπ/q with q odd, q ≤ d + 1. Exact knots build towers of dimension → d in every d. |
| B, Theorem 1 | The cosine wave: exact iff #T is odd, else its corner relation is the sine wave. The parity twist maps sine to sine (odd d) or sine to cosine (even d). |
| B, Theorem 2 | θ = π/4 is exceptional for both waves at every even level, in every dimension d ≥ 2. |
| B, Lemma 3 and Theorem 4 | Complement and the non-base flip (odd k) preserve exactness. Parity is exact exactly at powers of 2, odd parity only in even dimension (Lucas). |
| B, Theorem 5 | Census: 75 of 3,280 laws (d = 3) and 75 of 29,524 (d = 4) are exact somewhere, with 13 and 8 knots. The families account for all but 6 and 2 sporadic knots, and the knots exact at every computed level are the standing waves. |
| B, Proposition 6 | The exact factors for d = 2 (k ≤ 8), 3 (k ≤ 5), 4 (k ≤ 3). Their rational exceptional angles are only π/2 and π/4; the rest are irrational, and their number grows with k. |

## Reading

- **Space from a law, in every dimension.**
  - In every dimension a knot reproduces itself exactly on the Sierpinski simplices of every level. So it builds finitely ramified
    self-similar spaces whose dimensions rise towards d.
  - Here is what is and is not drawn. The gluing is the Sierpinski substitution, chosen rather than derived. The law's contribution is
    that it is a fixed point of that substitution at every scale and in every dimension. Its corner relation at every level is the
    knot again.
- **Harmonies.**
  - The sine wave is two opposite phases that the edges hold in step. Exactness at every scale is the statement that the phases never
    mix.
  - The cosine wave keeps its form only when the number of simplices is odd. Otherwise it turns into the sine wave, which then
    persists. Under refinement the sine wave is the attractor.
  - The factor's arithmetic says the same: at θ = 0 the gasket sees only its own edges.
- **Three dimensions in the program.** The program now has three regimes.
  - On shared subdivision of the plane, no non-affine knot reproduces itself, even with signs (`SIGNED-SUBDIVISION-20261029-001`).
  - On triangulated three-manifolds under Pachner moves, unsigned and positive edge laws see only parity (`HUB-DIMENSION-20261024-001`,
    `TWIST-3D-20261025-001`).
  - On finitely ramified Sierpinski simplices, signed knots build space in every dimension (this epic).
  - So what blocks knots is coupling through shared faces, not dimension. Signs have not yet been tried on three-manifolds. Each of the
    program's three-dimensional notes names phases (twisted Dijkgraaf–Witten) as the missing ingredient.
- **Contact-first standing.**
  - The knot supports are symmetric, so K1–K3 holds whichever place is read as the contact.
  - The systems are finite gadgets, so the source-aware reading does not apply. The towers' infinite limits are not claimed.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — the standing-wave law in every dimension | **Status:** Successful | Proved for every d and k, with an integer factor that never vanishes at odd prime-power angles; knots in every dimension; the census in d = 3, 4 matches the families. Open: rational exceptional angles (B, Conjecture 7), uniqueness (B, Conjecture 8), the cosine factor at π/6. |
| Local direction — exact self-reproduction on finitely ramified Sierpinski simplices | Practically exhausted at the level of mechanisms | The persistent mechanisms are classified in d = 2, 3, 4: sine waves always, cosine waves at odd #T, parity at powers of 2, flips at odd k. What remains is completion. |
| Broader exploration — space from a law (question 9) | Known alternatives | Signed laws on spaces coupled through faces are untried in three dimensions; the plane is excluded even with signs. Each of `HUB-DIMENSION-20261024-001`, `TWIST-3D-20261025-001` and `PATTERN-3D-20261025-001` names phases as the missing ingredient. |
| Long-term goal — space from logic without a drawn space | Capability gained | Knots are fixed points of self-similar gluings in every dimension. But the gluing is chosen, the spaces are finitely ramified, and no manifold is built. |
| Next recommendation — interference in three dimensions | **Next step:** Continue, as a fresh epic. Run a census of signed bit laws on the edges of ordered triangulations under the 2–3 and 1–4 moves (`TWIST-3D-20261025-001A`'s setting, with weights in {−1, 0, 1} in place of counts). Decide whether signs let bits see more of a three-manifold than mod-2 cohomology, and whether anything beyond twisted Dijkgraaf–Witten (the cubic form of H¹(M; Z/2)) appears. | It answers the program's standing three-dimensional gap with the tool this line has made natural. A law beyond Dijkgraaf–Witten would be new. Finding exactly it would settle what interference adds in three dimensions. |
| Interest — that recommendation | **2/3 — Promising** | Three prior notes single out phases, and signed laws now build space in every dimension. Main uncertainty: the expected answer is classical (twisted Dijkgraaf–Witten). The novelty would lie in an exhaustive census and its contact-first reading. |
| Execution — that next action | Deferred to the owner (fresh epic) | Done so far: reading the three prior notes. Stop when the signed census for one bit per edge is complete, or if the ordered framework cannot carry signs consistently. |

**Recommendation.** **Continue**, as a fresh epic: interference in three dimensions (2/3). Two alternatives were considered.
- **Uniqueness of the standing wave (2/3).** Classify the real-weight laws exact on two consecutive levels. This is a characterization
  in the local line, but heavier algebra (polynomial systems of degree 7 in 6 to 8 unknowns).
- **Which other finitely ramified gluings the wave builds (1/3).** This is ill-posed without a native notion of dimension. Dangling
  decorations already make the mass dimension arbitrary.
