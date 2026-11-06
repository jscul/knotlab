# Three-fold contacts: the knot on phases, the Fano gadget, and the corrected interference bound

Status: Proved

Ticket `SPACE-SELECTION-20261030-001C`, 2026-10-30.

**What it uses:**
- `SPACE-SELECTION-20261030-001A`:
  - the gadgets and pencils;
  - the sector expansion (Lemma 1) and the knot on sectors (Proposition 7);
  - the exhaustive fact that the 7-edge non-2-colourable 3-graphs on 7 points are the Fano planes (check 6);
  - the library `gadget_lib.py`.
- `SPACE-SELECTION-20261030-001B`: plain not-all-equal is exact on no gadget with 2 ≤ n ≤ 5.
- Classical: m(3) = 7, i.e. every 3-graph with at most six edges is 2-colourable (property B), with the Fano plane as the extremal example.

## Erratum for ticket A, Theorem 5

`SPACE-SELECTION-20261030-001A-P001` (closed) states that no nonnegative not-all-equal law is exact on a gadget with fewer than 7 triangles.
Its proof reduces R(0, 0, 0) = 0 to "G ∪ {ABC} is not 2-colourable". Three things are wrong:
- **The claim** overlooks the one-triangle gadget, on which every law is exact.
- **The reduction.** It is the wrong hypergraph. R(0, 0, 0) counts proper colourings with A = B = C = 0, so it vanishes iff G with A, B, C
  merged into one vertex is not 2-colourable. "G ∪ {ABC} not 2-colourable" says instead that every proper colouring has A = B = C.
- **A missing case.** Gadgets with two corners in one triangle are not covered.

Theorem 1 below is the corrected statement. It keeps the bound, now for 2 ≤ n ≤ 6, and shows it is sharp. The other results of ticket A are
unaffected. The check exhibits the n = 1 counterexample and confirms the correct identity on every gadget with n ≤ 4.

## Standard statement

**Setting.**
- **Gadgets** as in ticket A. A *contact* is an inner vertex. Its *base count* is its number of base incidences.
- **Three-fold gadgets.** A gadget is *three-fold odd* when every contact lies in exactly three triangles and has an odd base count.
- **The dual configuration G\*.**
  - Its points are the triangles and its lines are the contacts, each a triple of triangles.
  - A *phase assignment* σ ∈ {±1}^triangles is proper when no line is monochromatic.
  - N\*(ε) counts the proper assignments with corner-triangle phases ε = (σ_TA, σ_TB, σ_TC).

**Results.**
- **Theorem 1 (the corrected interference bound).** Let W be a law with nonnegative values and support not-all-equal.
  - For 2 ≤ n ≤ 6, W is exact on no gadget with n triangles.
  - The bound is sharp: plain not-all-equal is exact on the Fano gadgets (Proposition 4), which have 7 triangles.
  - The one-triangle gadget is exact for every law.
- **Lemma (forcing).** No 2-colourable 3-graph with at most five edges forces two of its vertices to be equal in all its proper 2-colourings.
  Six edges can: the Fano plane minus a line forces its three points equal.
- **Theorem 2 (duality at the knot angle).** Let G be three-fold odd.
  - Every contact then has exactly one base incidence.
  - At ζ = e^(iπ/3) the sector sums of ticket A, Lemma 1, are

    Z(ε) = (−i√3)^(n−1) · ε_A ε_B ε_C · N\*(ε).
  - So signed not-all-equal is exact on G iff G\* is 2-colourable and every proper phase assignment gives the three corner triangles the
    same phase.
  - With distinct corner triangles, the second condition says that G\* ∪ {T_A T_B T_C} is not 2-colourable.
- **Corollary 3 (seven triangles, and the Fano plane).**
  - A three-fold odd gadget on which the knot is exact has at least 7 triangles.
  - With distinct corner triangles and exactly 7, G\* ∪ {T_A T_B T_C} is a Fano plane.
  - These *Fano gadgets* are the Fano plane read as a gluing: triangles at its points, contacts at six of its lines, and corner triangles at
    the seventh line, with one base incidence per contact. Up to isomorphism there are 64.
- **Proposition 4 (the Fano gadgets).** All 64 Fano gadgets are:
  - linear;
  - exact for signed not-all-equal with λ(0) = 5;
  - exact for plain not-all-equal;
  - not generic for the standing wave.
- **Outside the theorem.** With contacts of even base count the duality fails, and small three-fold gluings can still be exact.
  - 60 of the 2,389 three-fold gadgets with at most five triangles are exact at the knot.
  - 1,216 of the 2,592 role patterns of the Fano gluing are exact at the knot; the 64 Fano gadgets are among them.
  - No three-fold odd gadget with at most five triangles (282 of them) is exact at the knot.

## Nearest known result

- **Property B.** m(3) = 7 and the Fano plane are classical. Hypergraph 2-colouring is the not-all-equal problem with positive literals.
- **In the repository.** `HUB-SURVIVORS-20261029-001` rebuilt plain not-all-equal on a punctured Fano plane with hub variables. The Fano
  gadget is a gluing without hubs on which both the plain and the signed knot reproduce themselves.
- **Classification.**
  - Theorem 1 is a short consequence of property B plus an exhaustive lemma.
  - Theorem 2, Corollary 3 and Proposition 4: no overlap found (candidate local delta).

## Proof of the forcing lemma

- **Pruning.** Suppose H is 2-colourable and forces u = v. Let w ≠ u, v be a vertex of degree one, in the edge e.
  - Removing w and e does not change the set of proper colourings of the remaining vertices. A colouring of H − e extends to w: e is
    proper already, or w can take the colour its two partners lack.
  - So the pruned graph is still 2-colourable and still forces u = v.
- **Size.** After pruning, every vertex other than u, v has degree at least two, and u, v have degree at least one (a free vertex is not
  forced). With k ≤ 5 edges, 3k ≥ 2(|V| − 2) + 2, so |V| ≤ 8.
- **Exhaustion.** The check enumerates every set of at most five triples on 8 labelled points (3.8 million at five). Each set is tested
  against all 128 colourings with one point fixed. None is 2-colourable with a forced pair.
- **Six edges.** Fano minus a line is 2-colourable, and every proper colouring makes the removed line monochromatic. ∎

## Proof of Theorem 1

- **Setup.** Exactness needs R(0, 0, 0) = λW(0, 0, 0) = 0 and λ ≠ 0. Since R ≥ 0 and W > 0 on not-all-equal states, λ > 0 and G has
  proper colourings.
- **The reduction.** R(0, 0, 0) is a sum of nonnegative terms over the proper colourings with A = B = C = 0, so it vanishes iff there is no
  such colouring. By complement symmetry, it vanishes iff no proper colouring has A = B = C.
- **Distinct corner triangles.** Merge A, B and C into one vertex O. Every triangle still has three distinct vertices, and the proper
  colourings of the merged 3-graph G_O are those of G with A = B = C. So G_O, with n edges, is not 2-colourable, and n ≥ m(3) = 7.
- **Two corners in one triangle T = {X, Y, x}.**
  - With X = Y = 0, T forces x = 1.
  - So R(0, 0, 0) = 0 iff no proper colouring of H = G − T has the third corner Z = 0 and x = 1. By complement symmetry, iff every proper
    colouring of H has Z = x.
  - H is 2-colourable because G is, it has n − 1 edges, and Z, x are vertices of H.
  - By the forcing lemma, n − 1 ≥ 6.
- **All three corners in one triangle.** Then that triangle has no inner slot, so connectivity forces n = 1.
- **Sharpness.** Proposition 4. ∎

## Proof of Theorem 2

- **One base each.** The base counts sum to n − 1 (ticket A, Theorem 1). There are n − 1 contacts, since 3(n − 1) inner slots are grouped
  in triples. Each count is odd, hence at least one, so each equals one.
- **The factors.** At ζ = e^(iπ/3) a three-fold contact of odd base count has factor f_v = −i√3 · σ_t σ_t′ σ_t″ · NAE(σ_t, σ_t′, σ_t″)
  (ticket A, Proposition 7).
- **The signs.**
  - Hence Z(ε) = (−i√3)^(n−1) Σ_σ (Π_t σ_t) Π_t σ_t^(d_t) Π_v NAE_v, where d_t is the number of contacts of triangle t, i.e. 3 minus its
    corners.
  - The sign Π_t σ_t^(1 + d_t) = Π_t σ_t^(c_t), with c_t the number of corners of t, equals ε_A ε_B ε_C. This holds also when two corners
    share a triangle, since then their phases agree.
- **Exactness.** By ticket A, Theorem 2, exactness means:
  - the mixed Z(ε) vanish, i.e. N\*(ε) = 0 for every mixed ε;
  - Z(+++) ≠ 0, i.e. N\*(+++) > 0. By complement symmetry and the first condition this is equivalent to G\* being 2-colourable.
- **The corner line.** With distinct corner triangles, "every proper assignment gives the corners equal phases" is "adding the corner line
  leaves no proper assignment". ∎

## Proof of Corollary 3 and Proposition 4

- **The bound.** G\* has n points and n − 1 lines.
  - With distinct corner triangles, G\* ∪ {T_A T_B T_C} is a non-2-colourable 3-graph with n edges, so n ≥ 7.
  - If two corner triangles coincide, G\* forces the phases of the shared triangle and the third corner triangle to be equal, so by the
    forcing lemma n − 1 ≥ 6.
- **Seven triangles.** At n = 7 with distinct corner triangles, G\* ∪ {T_A T_B T_C} has 7 edges on 7 points and is not 2-colourable, so it
  is a Fano plane (ticket A, check 6). G\* is the Fano plane minus a line, which is 2-colourable.
- **The 64 gadgets.**
  - The gadget is determined by which corner sits at each point of the corner line and by roles with one base incidence per contact.
  - The check generates every such choice and finds 64 isomorphism classes.
  - It confirms for each: Theorem 2's identity in Z[ζ₆], exactness for both knots, linearity, and that the standing wave is not generic.
- **Why plain not-all-equal is exact.**
  - Merging the corners gives the Fano plane, read dually: contacts and the merged corner are its points, triangles its lines. That is not
    2-colourable, so R(0, 0, 0) = 0.
  - The three not-all-equal corner patterns receive equal positive counts, by the symmetries of the Fano plane fixing the merged point.
- **Shared corner triangles at n = 7** are not classified here. ∎

## What the computation checks

`check.py` (about a minute):
- **The erratum.** The one-triangle counterexample. The correct identity for R_plain(0, 0, 0) on every gadget with n ≤ 4, and the one
  gadget where A's reduction disagrees.
- **Theorem 1.** The forcing lemma (exhaustive on 8 points, up to five edges). Fano minus a line forces equality. Ticket B's census shows
  plain not-all-equal exact on no gadget with 2 ≤ n ≤ 5.
- **Theorem 2.** The duality identity exactly in Z[ζ₆], for all 282 three-fold odd gadgets with n ≤ 5 and the 64 Fano gadgets. The
  equivalence of knot exactness with the dual criterion on all of them, and that none with n ≤ 5 is exact.
- **Proposition 4**, together with the count over all 2,592 role patterns of the Fano gluing.
- **Controls:**
  - the identity fails when a contact has even base count;
  - a three-fold odd 7-triangle gadget whose dual plus the corner line is 2-colourable is not exact;
  - the Fano plane is not 2-colourable, and Fano minus a line is.

## Reading

- **The two/three boundary reappears inside the gluing.**
  - A contact of two triangles with one base incidence locks their phases: an equality, a two-place relation. Phases propagate, signs
    interfere, and the knot reproduces itself on three triangles (the Sierpinski gadget).
  - A contact of three triangles with odd base count is itself a not-all-equal knot on their phases. A gluing made only of such contacts
    turns the signed problem into the unsigned one on the dual configuration, where nothing cancels.
- **The Fano plane is where interference and positivity meet.** Like the unsigned knot, the signed knot then needs seven triangles and the
  Fano plane, and on the Fano gadget both knots reproduce themselves.
- **The corrected bound is a statement about positivity, now proved and sharp.** Without signs a not-all-equal law needs at least seven
  triangles to rebuild itself, and seven suffice.

## Nonclaims

- **Even base counts.** Gluings with three-fold contacts of even base count are outside Theorem 2. Many of them are exact at the knot, and
  they are not classified.
- **Shared corners.** Three-fold odd gadgets with shared corner triangles at n = 7 are not classified.
- **Classical input.** m(3) = 7 is a classical input, not replayed here. Ticket A's check replays only the small-vertex cases and the 7-point
  enumeration.
