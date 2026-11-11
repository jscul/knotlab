# Back toward native emergence: the decision

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): a knot space is a three-regular contradiction. Results are unchanged;
the earlier text is in git history.

Epic `NEXT-DIRECTION-SCAN-20261031-001`, closed 2026-10-31. Program: portfolio.

## The request

The counting arc ended with the note `COUNT-NOTE-20261031-001`. The owner approved its recommendation ("Yes, please continue"): run a short,
scoped scan back toward native emergence and pick one direction. The three candidates were:
- (a) does a native law favour the knot's signs or the twist-free Fano plane;
- (b) the Ising reading, with the knot's class as its free-fermion point;
- (c) counting one line short of Seymour's bound.

Each lane got one cheap discriminator and ran as a documentation ticket. Every lane's script was rerun in a temporary mirror of the
repository, and every output was identical apart from timing.

## What the lanes found

| Lane | Question | Finding | Interest |
| --- | --- | --- | --- |
| A (`…001A`) | Does single-flip descent toward fewer colourings reach the knot's sign class? | On the knot's own spaces (Fano and two 13-point Fano splices, girth 6), it does from every class. Every Pfaffian graph with 4-cycles has traps: cube 4, prisms 1, trisums 6 and 3, truncated octahedron 14. The dynamics is imposed, not native. | 1/3 |
| B (`…001B`) | Is the knot's class a free fermion at every coupling x, or only at the counting point x² = −1/3? | Single pages: free at every x (a two-parameter family closed under junctions, and Theorem 4's similitude at every x). Depth two: closed branches leave the family by a defect divisible by 3x² + 1. Junctions of two deep branches break the matchgate identity in 5 of 6 pairs, and the factors shared by all five are exactly x, x ± 1, x² + 1, 3x² + 1: the affine couplings and the counting point. One pair (two truncated-octahedron branches) keeps it. Checked against brute force at depths one and two. | 3/3 |
| C (`…001C`) | Is there a counting question one line short of the bound beyond Theorem 1? | Counting is #P-hard there, even for connected Seymour-sparse systems of degree at most 3, by point splitting: #col(H0) = 2 #col(H1) − #col(H2). Only the knot's subclass is known to be easy. | 1/3 |
| Check (top-level, `basis_check.py`) | Is lane B's failure an artifact of the y-basis? | No. For a generic coupling, the only invertible holographic transformations that keep both the point and the line signatures parity-definite (necessary for matchgates) are diagonal or antidiagonal. Under those the matchgate identity is multiplied by a nonzero constant. | — |

## The pick: lane B, a coupling dichotomy in the knot's class

**The question.** On non-colourable cubic triple systems carrying the knot's signs, is the three-body Ising model #P-hard at every coupling
except the counting point x² = −1/3 and the affine couplings x = 0, ±1, ±i?

**Why this one.**
- **It is native.** Nothing is imposed but the coupling. The space's Pfaffian signs decide at which law counting stays planar, and the scan
  finds that they choose the knot's own law, not-all-equal. Lane A's selection, by contrast, needed an imposed dynamics.
- **It ties the arc to the owner's intuition.** The two/three boundary is emergence, and the knot is where it happens. A positive answer
  would say that on the knot's contradictions the knot's law is the only non-trivial law that counts easily: the signs and the law fit only each
  other.
- **Its evidence is concrete.** The pattern is exact algebra (common factors, not numerics), cross-checked by brute force and controlled
  by generic matchgates and by the basis check.
- **Its first discriminator is cheap and decisive.** A deep-branch junction that breaks the identity is a non-matchgate signature *inside*
  the knot's class. Test whether planar gadgets around it interpolate to a crossing, as the cube-junction ladder of `PLAIN-BRACE-20261031-001A`
  did at the counting point.

**What would change the pick.**
- A tractable route at a generic coupling, beyond matchgates: an affine or product-type structure, or bounded genus on the instances
  that matter.
- More special families, like the truncated-octahedron pair, that keep the identity at every coupling.
- A published statement.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — the three-lane scan back toward native emergence | **Status:** Successful | Each lane returned a decision-ready discriminator, every replay reproduced its outputs, and one direction stands out. |
| Local direction — the counting arc's mechanisms | Continue through lane B; A and C retired as standalone epics | Lane A's funnel and lane C's hardness are recorded. Neither carries native content worth an epic. |
| Broader exploration — the two/three boundary | Known alternatives | Lane A's funnel on Fano spaces (1/3), the colourable side of H − L (1/3), approximate counting (not assessed here), expert review of the note (the owner's decision). |
| Long-term goal — the two/three boundary as emergence | Capability gained (computed evidence, not a theorem) | On the knot's contradictions, the knot's signs keep counting planar only at the knot's own law, on every tested depth-two tree but one. The missing bridge is hardness at the other couplings. |
| Next recommendation — a coupling dichotomy in the knot's class | **Next step:** Continue. Open a fresh epic asking whether the three-body Ising model with the knot's signs is #P-hard at every coupling except x² = −1/3 and x = 0, ±1, ±i. | First discriminator: interpolate a crossing from a deep-branch junction inside the knot's class. Stop if a tractable route appears at a generic coupling, if special families keep the identity in general, or if a published statement is found. |
| Interest — that recommendation | **3/3 — Hot** | The evidence is exact and cross-checked, and the payoff is a native selection theorem: the space's signs select the knot's law. Main uncertainty: the hardness step inside the knot's class, and special families like the truncated-octahedron pair. |
| Execution — that action | Planned; awaits the owner | A fresh epic that depends on this closure. Its first ticket is the crossing discriminator; a second would state the depth-two defect (the factor 3x² + 1) as a lemma. |
