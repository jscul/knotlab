# Which spaces the harmony builds

Epic `SPACE-SELECTION-20261030-001`, 2026-10-30.

## The question

- **The owner's request (2026-10-30).** "Yes, let's continue," on the recommendation of `WAVE-UNIQUENESS-20261029-001`.
  - Reverse the question of the previous epics: fix the law (the standing wave, and signed not-all-equal in particular) and ask on which
    gluings of triangles it reproduces itself.
  - Test the conjectured criterion "sector locking plus odd flip parity".
  - Find the growth exponents of the towers.
- **Setting.**
  - A *gadget*: n triangles glued at vertices, corners A, B, C each in one triangle (in roles a, b, c), inner vertices in at least two
    triangles.
  - The law is *exact* when the corner relation is a nonzero multiple of the law. An exact gadget builds a finitely ramified tower by
    substituting itself into its own triangles.
- **Intuitions targeted:**
  - space from logic without a drawn space: the law selecting its gluings;
  - everything relational: harmonies as cancelling phases;
  - the two/three boundary.

**The evidence:**
- [The gadget criterion](../../proofs/SPACE-SELECTION-20261030-001A/SPACE-SELECTION-20261030-001A-P001_the_gadget_criterion/proof.md)
  (A, proof). Its Theorem 5 is corrected by C.
- [Census of small gadgets](../../proofs/SPACE-SELECTION-20261030-001B/SPACE-SELECTION-20261030-001B-P001_census_of_small_gadgets/proof.md)
  (B, proof, all 74,650 gadgets with at most five triangles).
- [Three-fold contacts and the Fano gadget](../../proofs/SPACE-SELECTION-20261030-001C/SPACE-SELECTION-20261030-001C-P001_three_fold_contacts_and_the_fano_gadget/proof.md)
  (C, proof, with the erratum for A).
- Scoping (scratch, not evidence):
  - Random labelled gadgets with six to eight triangles, 1,500 to 4,000 per size. Their counterexamples were re-verified exactly and
    entered B.
  - Random 3-regular triple systems with 7 to 15 points (about 25,000).

## Outcome in one paragraph

**The harmony selects gluings by interference, not by a local rule, and it selects neither one space nor one growth exponent. Inside the
gluing, the two/three boundary returns.**
- **The criterion.**
  - The standing wave is exact on a gadget iff six signed sums over phase assignments cancel (A).
  - The conjectured "locking plus odd flip parity" is refuted: flip parity is always odd, and locking is sufficient but not necessary.
  - Phase locking and mirror cancellation explain every exact gadget up to five triangles. Six and seven triangles need algebraic
    cancellation.
- **The census (B).**
  - The harmony is exact on 14, 172 and 5,694 gadgets with 3, 4 and 5 triangles. The knot is exact on 14, 206 and 8,584; 3,082 of the
    8,584 are its own.
  - Special angles proliferate: π/4, π/6, π/8, cos 2θ = −1/3, and others.
  - Growth rates are certified algebraic integers. Tadpoles make the exponents unbounded.
- **Interference and three-fold contacts (C).**
  - Without signs, a not-all-equal law needs at least seven triangles to rebuild itself, and seven suffice. With signs, three suffice.
  - At the knot angle, a contact of three triangles with odd base count is itself a not-all-equal knot on their phases. A gluing made only
    of such contacts is the unsigned problem on its dual configuration. The knot then needs seven triangles, and at seven the only spaces
    (with distinct corner triangles) are the 64 Fano gadgets, on which the signed and the plain knot both reproduce themselves.

## What was proved

| Result | Content |
| --- | --- |
| A, Theorems 1-2 | Base incidences sum to n − 1, so flip parity is automatic. The wave is exact iff six mixed sector sums vanish. Either exact for all q outside the roots of a monic λ of degree n − 1, or for at most n values of q. |
| A, Theorem 3 | Locking and balanced cancellation suffice. Neither is necessary: a 4-triangle twin gadget, and algebraic cases at 6 and 7 triangles. The conjectured criterion is refuted. |
| A, Theorems 4, 6 | Exact gadgets compose under substitution. Tadpoles keep exactness and corner chains, so exponents are unbounded. |
| A, Proposition 7 | At the knot angle a three-fold contact with odd base count acts on phases as the not-all-equal knot. |
| A, Theorem 5 | **Superseded by C, Theorem 1.** The claim overlooks n = 1, and the proof uses the wrong hypergraph. |
| B | Complete census to five triangles (counts, mechanisms, knot, special values, cosine and plain pencils, certified growth) and exact examples where the small-size coincidences end. |
| C, Theorem 1 | No nonnegative not-all-equal law is exact for 2 ≤ n ≤ 6 (property B and a forcing lemma). The bound is sharp at 7. |
| C, Theorem 2, Corollary 3, Proposition 4 | Duality at the knot angle for three-fold odd gluings. At least 7 triangles are needed, and at 7 with distinct corner triangles exactly the 64 Fano gadgets, exact for both knots. |

## Scoping beyond the census (not evidence)

- **Labelled random gadgets.** The three pencil parameters below are exact on these numbers of samples.

  | Triangles, class | Knot (q = 0) | Quarter wave (q = 1) | Sixth wave (q = 2) | Generic |
  | --- | ---: | ---: | ---: | ---: |
  | 6, linear | 358 | 312 | 177 | 122 |
  | 7, linear | 171 | 216 | 105 | 74 |
  | 8, linear | 59 | 147 | 19 | 11 |

  - The knot's lead at five triangles does not last: the quarter wave, which is not a knot, overtakes it in these samples.
  - Generic (harmony-wide) exactness thins out fastest.
- **Random 3-regular triple systems.**
  - Of about 25,000 connected samples with 7 to 15 points, the only ones that are not 2-colourable have 7 points: the Fano plane.
  - If every connected 3-regular triple system other than the Fano plane is 2-colourable, C's duality makes the Fano gadgets the knot's
    only three-fold odd spaces, at every size. This plausibly follows from the theory of minimally non-2-colourable hypergraphs (Seymour;
    Thomassen; Robertson–Seymour–Thomas on even cycles). It is not checked here.
- **The Fano towers.** They have corner growth 3, so exponent log 7 / log 3 ≈ 1.77.

## Reading

- **Interference is the selection mechanism.**
  - A gluing carries the harmony when the mixed phase assignments cancel. Contacts that lock phases make this happen locally; mirror pairs
    of assignments, and from six triangles genuine identities between products, make it happen globally.
  - The space the law builds is therefore defined by a cancellation, which is the program's "harmony" in exact form.
- **No space and no dimension are forced.** Thousands of gluings already at five triangles, closure under substitution, tadpoles and
  unbounded exponents show that the law does not draw a space by itself. The gluing still has to come from somewhere.
- **The two/three boundary, inside the gluing.**
  - Two-fold contacts transmit phase (an equality), and interference lets three triangles suffice.
  - Three-fold contacts with odd base count are themselves not-all-equal knots on phases, and positivity returns: the knot then needs the
    Fano plane, the smallest configuration that is not 2-colourable.
  - So the knot's space made only of knots is the Fano plane. Being self-dual, it reads the same with triangles and contacts exchanged.
- **The error.** Ticket A's interference bound was stated for "fewer than seven" and proved with the wrong hypergraph. The bound survives
  for 2 ≤ n ≤ 6, now with a correct proof and shown sharp, and A's record is kept with an erratum.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — which spaces the harmony builds | **Status:** Successful | Criterion proved and the conjectured one refuted. Census complete to five triangles with certified growth. Corrected interference bound, sharp at seven. Duality for three-fold contacts and the Fano gadgets. One error found and corrected inside the epic. |
| Local direction — gadget censuses for the wave pencil | Practically exhausted | More sizes would add counts, not mechanisms. The coincidences of small sizes end at six or seven triangles, and from there cancellations are algebraic. |
| Broader exploration — space from a law (question 9) | Known alternatives | The three-fold (phase-knot) side has a concrete classical bridge: 2-colourings of 3-regular triple systems and minimally non-2-colourable square hypergraphs. Mixed gluings (two-fold locks plus three-fold knots) are unmapped. |
| Long-term goal — space from logic without a drawn space | Capability gained | The law selects gluings by cancellation but does not draw one. At the level of contacts the knot reappears, and the gluing made only of knots is forced to be the Fano plane. |
| Next recommendation — the knot's three-fold spaces | **Next step:** Continue, as a fresh epic. Prove that the Fano gadgets are the knot's only three-fold odd spaces at every size: check the literature on 2-colourings of 3-regular triple systems, and prove or cite that every connected one other than the Fano plane is 2-colourable. Then classify mixed gluings, two-fold phase locks with three-fold phase knots, up to six triangles. | If true, the knot's space made only of knots is unique: the Fano plane, self-dual. That would be the closest the program has come to a space the law draws by itself. |
| Interest — that recommendation | **2/3 — Promising** | Concrete: duality, an exact criterion, and about 25,000 random samples with no exception. Main uncertainty: the uniqueness may be a known classical theorem, in which case the new content is the duality and the reading. The mixed case may not admit a clean structure. |
| Execution — that next action | Deferred to the owner (fresh epic) | Done so far: duality, Fano gadgets, the probe. Stop when three-fold odd gluings are classified at every size (proof or exact citation) and mixed gluings up to six triangles are classified or shown to need algebraic cancellation. |

**Recommendation.** **Continue**, as a fresh epic: the knot's three-fold spaces (2/3). Three alternatives were considered.
- **The census at six triangles (1/3).** Completion work. Sampling already shows the patterns.
- **A write-up of the standing wave on finitely ramified gluings (1/3).** It would gather `SIGNED-GASKETS`, `SIMPLEX-GASKETS`,
  `WAVE-UNIQUENESS`, `SIGNED-3D` and this epic. Deferred until the three-fold classification settles whether the Fano statement is new.
- **The quarter wave (1/3).** It overtakes the knot at seven and eight triangles in samples, but it is not a knot.
