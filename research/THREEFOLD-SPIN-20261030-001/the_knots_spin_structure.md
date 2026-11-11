# The knot's spin structure

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): a three-fold space is a three-regular contradiction; a Fano atom is a Fano piece. Results are unchanged;
the earlier text is in git history.

Epic `THREEFOLD-SPIN-20261030-001`, 2026-10-30.

## The question

- **The owner's request (2026-10-30).** "Yes, let's continue." This approved the recommendation of `THREEFOLD-AMPLITUDE-20261030-001`:
  - Do the knot's own signs satisfy Kasteleyn's face condition on every minimal map of every three-regular contradiction?
  - If so, each space carries a spin structure on its surface. Find its Arf invariant per Fano piece.
- **Setting.**
  - The knot's three-regular contradiction H has a triangle–contact incidence graph B(H). Its minimal maps are the least-genus surfaces carrying it,
    one handle per Fano piece (`THREEFOLD-SURFACES-20261030-001`).
  - The knot's signs on B(H) are trivial, and they are Pfaffian.
  - Kasteleyn's condition on a face of length 2l asks for l − 1 negated edges mod 2. For trivial signs this means every face has length
    2 mod 4.
  - Cimasoni and Reshetikhin attach to a Kasteleyn orientation and a perfect matching a spin structure: a quadratic form on the surface's
    homology.
- **Intuitions targeted:**
  - the law equipping the space it builds with structure;
  - the two/three boundary.

**The evidence:**
- [Kasteleyn faces and even spin structures](../../proofs/THREEFOLD-SPIN-20261030-001A/THREEFOLD-SPIN-20261030-001A-P001_kasteleyn_faces_and_even_spin_structures/proof.md)
  (A, proof).
- [The spin structure by computation](../../proofs/THREEFOLD-SPIN-20261030-001B/THREEFOLD-SPIN-20261030-001B-P001_the_spin_structure_by_computation/proof.md)
  (B, exhaustive and exact computation).
- **Literature.**
  - Cimasoni–Reshetikhin, *Dimers on surface graphs and spin structures. I* (arXiv math-ph/0608070); its Theorem 4.1, Proposition 4.2
    and the sign identity in the proof of Theorem 5.1 were read and used.
  - Johnson (spin structures as quadratic forms); Kasteleyn; Galluccio–Loebl and Tesler (4^g Pfaffians).
  - Zhang–Zhang (faces of plane elementary bipartite graphs are nice cycles).

## Outcome in one paragraph

**Yes. The knot's own signs are a Kasteleyn structure on its own surface, and the spin structures it induces are even, handle by handle.**

- **Every face of every minimal map has length 2 mod 4 (A, proved for planar glue).**
  - The proof is a splice lemma. Across a tight three-edge cut, a genus-additive gluing has exactly three crossing faces, each made of one
    face from each side, so face parities add.
  - Fano pieces (seven hexagons on the torus), doubled squares and planar braces all satisfy the condition.
  - Trisum glue, the non-planar kind, satisfies it on every one of its minimal maps (B).
- **The spin structures are even (A).**
  - Because the signs are Pfaffian, each perfect matching gives a spin structure whose quadratic form vanishes on every difference of
    matchings, so its Arf invariant does not depend on the matching.
  - The form splits over the Fano pieces. On each atom the matching differences span the torus's homology, which forces Arf 0.
- **The matchings induce exactly the spin structures that are even on every handle.**
  - On the Fano torus the 24 matchings induce the three even spin structures, 8 each, and never the odd one.
  - A space with h atoms gets exactly 3^h spin structures (A proves "at most"; B confirms "exactly" up to 22 points): 9 of the 10 even
    ones at genus 2, 27 of 36 at genus 3.
- **The knot's class is singled out.** On the Heawood torus the four Kasteleyn classes have determinants 24, 8, 8, 8 in absolute value. Only
  the knot's own class counts the 24 matchings.
- **Evenness belongs to the minimal surface (B).** On larger surfaces carrying the same signs, odd spin structures do appear: about 1–2% of
  Kasteleyn maps, and only from genus 3 on.

## What was proved

| Result | Content |
| --- | --- |
| A, Lemma 1 | Face splice: three crossing faces, one face from each side; three distinct faces at every vertex preserved; Kasteleyn parity carried over. |
| A, Theorem 2 | Every face of every minimal map of a space with planar glue has length 2 mod 4: the knot's signs are Kasteleyn. |
| A, Proposition 3 | For a Pfaffian Kasteleyn signing, the form vanishes on matching differences and its Arf invariant does not depend on the matching. |
| A, Theorem 4 | The form splits over atoms; each atom has Arf 0; every induced spin structure is even, and even on every handle (at most 3^h of them). |
| A, Proposition 5 | Fano torus: the matchings induce exactly the three even spin structures, 8 each. |
| B | All spaces up to 22 points: exactly 3^h classes, Arf 0. Trisum glue: Kasteleyn and even. Heawood determinants 24, 8, 8, 8. Odd spin structures only on non-minimal maps of genus ≥ 3. |

## Reading

- **The law equips its space.**
  - The knot builds its space from atoms, which become handles, and the glue stays flat (earlier epics).
  - Now its own signs turn out to be exactly the extra structure a surface needs to carry spinors: a Kasteleyn structure, giving a spin
    structure for each perfect matching.
- **Even on every handle.** Each handle carries only the three even spin structures of the torus, never the odd one. Since the Arf invariant
  is the spin bordism class, every knot surface with any of its induced spin structures bounds a spin 3-manifold.
- **The two/three boundary.** The three-place atom carries the handle and its even spin structures. The two-place glue is flat, carries no
  homology and so carries no spin choice.
- **Limits.**
  - This is the spin geometry of an incidence graph on its least-genus surface, through the dimer correspondence. It is not a physical
    spin, and not a native contact topology in the K1–K3 sense.
  - Non-planar glue is treated by computation only.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — the knot's spin structure | **Status:** Successful | Yes, and more: Kasteleyn on every minimal map (proved for planar glue), even spin structures, handle-even, 3^h of them, odd only on non-minimal maps. |
| Local direction — spin structures of three-regular contradictions | Practically complete | Open: a proof for non-planar glue in general, and why odd spin structures need genus ≥ 3 on non-minimal maps. Both are completion-like. |
| Broader exploration — space from a law (question 9) | Known alternatives | The knot's surface now carries atoms, handles, an amplitude (5 per handle, tree counts for flat glue) and an even spin structure. These two numbers have not yet been connected. |
| Long-term goal — space from logic without a drawn space | Capability gained | The law's own signs supply the surface's spin structure. That is a second piece of structure determined by logic on the surface it builds. |
| Next recommendation — the knot's amplitude as a spin sum | **Next step:** Continue, as a fresh epic. The amplitude A(H, L) is an Ising partition function at half the knot's angle on B(H) − L (`THREEFOLD-AMPLITUDE-20261030-001C`). On a surface such a function is a signed sum over the 4^g spin structures of Pfaffians (Kac–Ward, Cimasoni). Which spin structures contribute at the knot's coupling? Does 5 per handle come from the three even spin structures alone, with the odd one cancelling? | Would connect the knot's two numbers, its amplitude and its spin structure, and explain 5 per handle topologically. |
| Interest — that recommendation | **2/3 — Promising** | The ingredients are all in place (the Ising form of the amplitude, the even spin structures, the Fisher dimer correspondence). Main uncertainty: the Pfaffians at complex coupling may not separate cleanly by spin structure. |
| Execution — that next action | Deferred to the owner (fresh epic) | Done so far: this epic. First discriminator: the four Fisher-dimer Pfaffians of the Heawood torus minus a line, at the knot's coupling. Stop if no spin structure is singled out there. |

**Recommendation.** **Continue**, as a fresh epic: the knot's amplitude as a spin sum (2/3). Two alternatives were considered.
- **A filling chosen by the knot (1/3).** The surface bounds spin 3-manifolds. Does the knot single out a handlebody? The matchings weight the
  three even spin structures equally (8, 8, 8), which suggests no preferred filling.
- **A write-up of the three-fold line (1/3).** Five epics form a coherent story: spaces, grammar, surfaces, amplitude, spin. The owner asks
  for write-ups only for results of real magnitude.
