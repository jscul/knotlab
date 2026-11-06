# Relations among the twist sectors

Epic `TWIST-RELATIONS-20261022-001`, closed 2026-10-23.

## The question

The previous epic found that one exact-looking value (half a bit) was not exact. It also found a relation that held: on rectangular tori the four twist sectors "add up". The owner framed the next step as relations, not values: "everything is relational", and harmonies are relations in which incomplete quantities cancel. The approved epic was to prove the additivity, or to map the shapes on which it holds and explain why.

**The evidence:**
- [The harmonic structure of the twist sectors](../../proofs/TWIST-RELATIONS-20261022-001A/TWIST-RELATIONS-20261022-001A-P001_harmonic_structure/proof.md) (A, proof);
- [The twist relations across shapes](../../experiments/TWIST-RELATIONS-20261022-001B/TWIST-RELATIONS-20261022-001B-E001_relations_map/contract.json) (B, confirmatory experiment; [result](../../artifacts/TWIST-RELATIONS-20261022-001B/TWIST-RELATIONS-20261022-001B-E001_relations_map/result.json));
- **Scoping (scratch, not evidence):** exhaustive enumeration of every orientation of the 3 × 3, 4 × 3, 3 × 4 and 5 × 3 tori at every shear, and 48–96 million-sample runs on eleven further tori.

**Notation.**
- **The torus.** It has periods w1 = (Lh, 0) and w2 = (s, Lv), where s is the shear.
- **Sectors.** Sector (a, b) is the twist with value a on w1 and b on w2.
- **The four probabilities.** P_ab = P(all strong components contractible) in sector (a, b).
- **The combinations.**
  - E = P00 − P01: the effect of twisting w2 when w1 is untwisted.
  - O = P10 − P11: the same effect when w1 is twisted.
  - D = E − O: the second difference. "Additivity" is D = 0.

## Outcome in one paragraph

**Proved (A).**
- **The exact skeleton.** Relabeling the basis turns E and O into two "harmonics" of different kinds. E repeats under a full shear and carries only whole harmonics. O changes sign and carries only half-integer harmonics. Its "spin" is ½, and it vanishes exactly at half shear.
- **What follows.** Additivity can hold only where the two agree. It is a statement about an orthogonal basis, not about the torus. Shear dephases it. At half shear it would need the twist to have no effect at all.

**Found and confirmed (B): an exact relation.** For every class c:
- **The relation.** The probability that a twisted sector's strong components wind along c, and nothing else, is the same for the two twists that make c odd.
- **The evidence.** It is exact on every small torus enumerated, and confirmed to about 10⁻⁵ on eight new tori.
- **In the knot's terms.** A contradiction carried by one odd loop along c does not care how the transverse direction is twisted.

**Refuted (B).** A stronger form, that this probability does not depend on the shear at all, was exact on the smallest tori and fails on 12 × 8 (7.3 standard errors).

**Mapped (B).**
- **Rectangles.** Additivity holds on rectangles of aspect 1, 3/2, 2 and 3, and on the rotated square in its own orthogonal basis.
- **Squares under shear.** D(s) = D(0) + E(0)(1 − cos πs/L) to 0.001: a single half-integer harmonic.

## The exact skeleton (proved in A)

**Basis covariance, pathwise.**
- **Shear by Lh.** This is the same torus in the basis (w1, w1 + w2). Sector (a, b) becomes (a, a + b), orientation by orientation.
- **The mirror.** It maps shear s to −s, and each sector to itself, once the twisted seam is moved by a gauge transformation.
- **A bookkeeping detail.** The mirror swaps the ends of horizontal edges, and a lift's sheet is read at its tail. So a horizontal arrow is reversed only where its edge does not cross the seam.

**Harmonic parity.**
- **Periodic parts.** E, P00 + P01 and P10 + P11 are periodic in the shear with period Lh, and even.
- **The antiperiodic part.** O is antiperiodic, O(s + Lh) = −O(s), and even.
- **In Fourier terms.** Over the period 2Lh, the first three carry only cos(2πks/Lh), and O only cos((2k + 1)πs/Lh).
- **Consequences.** O(Lh/2) = 0, D = E − O, and D(s + Lh) = E + O.

**Why shear breaks additivity.**
- **At half shear.** D = P00 − P01, the whole effect of the second twist.
- **In two bases.** Additivity in both bases of the same torus forces both effects to vanish.
- **What additivity is.** It singles out the mod-2 class of w1 + w2, so it is a property of a basis.

**One law, not two.** In twisted sectors P(consistent) = 1 − P(contractible) − P(odd winding), exactly. So the earlier "consistency relation" (1 − cons10 − cons01 + cons11 = P00) is equivalent to D = odd10 + odd01 − odd11. It is not a separate law.

**Nothing measured is exact at finite size.** On the 3 × 3 torus:
- D = 2581/32768;
- E differs between shears 0 and 1;
- O at shear 1 is not O(0)/2;
- the consistency relation gives 763/65536 against 5925/65536.

## The exact relation found: odd lines

**The identity.** Let c be a primitive class. The two nonzero twists p, p′ that are odd on c give P(cone of sector p = the line ℝc) = P(cone of sector p′ = ℝc).

**Evidence.**

| Where | Result |
| --- | --- |
| 3 × 3, 4 × 3, 3 × 4, 5 × 3, all shears (exhaustive, scratch; 3 × 3 also in A's check) | Exact: for example 19200 = 19200 and 232320 = 232320 orientations on 4 × 3 with shear 1; 97848000 = 97848000 on 5 × 3 |
| Eleven scoping tori up to 32 × 32, 48–96 million samples | Every difference within 2.3 standard errors; resolved to a few parts in 10⁶ |
| **B, pre-registered: 8 new tori** (7 × 5 to 24 × 24, three sheared) | **Accepted:** 24 tests, max \|z\| 2.63, resolved to about 10⁻⁵ |
| B, the 18 larger rows (descriptive) | Pooled differences within 1.8 standard errors; two single tests near 3.1 out of 54 |

**What it means.**
- **A contradiction loop is blind to the transverse twist.** In a fair not-all-equal world, inconsistency happens when a strong component wraps an odd cycle. The identity says: the chance that the only thing wrong is a single odd loop along c depends on c's own parity, not on whether the other direction is twisted.
- **Consequence.** odd10 + odd01 − odd11 = twice the odd lines in diagonal classes. Exactly zero on the small tori, where no diagonal odd loops occur; positive on large tori, where they do.

**How far a proof got (scratch).**
- **The bijection.** Move the second twist's seam by a gauge transformation to a row where nothing crosses it.
- **Where it works.** It is an exact bijection on tori of height 3: every configuration has exactly one such row, which also explains why the two events overlap in exactly a third.
- **Where it fails.** From height 4 on, some configurations have no straight such row. A proof needs seams that follow the dual barrier, and moving a seam through a dual band rewires the band. The identity stays a conjecture.

**The stronger form is refuted.**
- **The claim.** For the twist odd on w1 and even on w2, the odd horizontal line does not depend on the shear.
- **Small tori.** It held exactly: 19200 at all three shears of 4 × 3.
- **12 × 8.** It fails: 0.000918, 0.000913, 0.000866, 0.000861 at shears 0, 2, 4, 6 (z = −0.65, −6.65, −7.31).
- **A lesson about tiny tori.** Exact equalities there can be coincidences, which is why the identity itself was tested again on new tori.

## The large-size relations (B)

**Rectangle additivity: accepted.**
- **Aspect 1.** Previous epic: 0.0008 ± 0.0005.
- **Other aspects.** Two-size extrapolation in B:

  | Aspect | D_inf |
  | --- | --- |
  | 3/2 | 0.0025 ± 0.0014 |
  | 2 | 0.0004 ± 0.0012 |
  | 3 | 0.0005 ± 0.0010 |

- **What kind of relation.** It holds at large size only; on squares D decays like 1/L.

**The rotated square: accepted at 2.5 standard errors.**
- **The torus.** Periods (L, 0) and (L/2, L/2): a square turned 45°.
- **In its orthogonal basis.** The relation gives 0.0043 ± 0.0017, extrapolated. It is not yet decaying between the two sizes (0.0035, then 0.0039), so it is weaker evidence.
- **In the axis basis.** The same torus gives −0.2715. Additivity is a relation of the orthogonal frame, as the skeleton predicts.

**Shear harmonics (descriptive).**
- **Squares, 64 × 64.**
  - **E.** −0.1342, −0.1345, −0.1326, −0.1337, −0.1327 at shears 0, 8, 16, 24, 32: shear-independent.
  - **O.** −0.1363, −0.1270, −0.0961, −0.0537, −0.0005, against O(0) cos(πs/64) = −0.1363, −0.1260, −0.0964, −0.0522, 0.
  - **The law.** D(s) = D(0) + E(0)(1 − cos(πs/64)) to 0.001. In the language of the skeleton, the square carries one whole harmonic and one half-integer harmonic, in phase at zero shear.
- **The 2:1 torus, 128 × 64, sheared along its long side.**
  - **E.** It moves by 0.016.
  - **O.** −0.2843, −0.2740, −0.2261, −0.1321, −0.0014, against a single harmonic's −0.2843, −0.2627, −0.2010, −0.1088, 0.
  - **What that shows.** Higher harmonics appear when the torus is short in the transfer direction.
  - **A rejected law.** O = cos(πs/L) E, a "spin splitting" in which each twist-odd state splits into two states shifted by ±½, failed by 22 standard errors in scoping.

## Interpretation (not theorem)

- **Additivity as a harmony.**
  - **The two parts.** The four twist sectors split into a part that sees whole turns of a shear and a part that sees half turns.
  - **On a rectangle.** The two twist-odd parts are equal: the "harmonies" are in phase.
  - **Under shear.** Shear detunes them by half a turn, and half a shear silences the half-turn part completely.
  - **In the owner's words.** A relation between two incommensurable quantities: neither number is known, but their difference vanishes exactly where the geometry is symmetric.
- **The odd-line identity as a harmony in the strict sense.**
  - **It holds at finite size,** on every torus small enough to count exactly.
  - **What it relates.** Two quantities whose values nobody can compute (the probability of a lone odd contradiction loop under two different twists).
- **Spectral reading.** In a transfer-matrix picture, additivity on every rectangle says that the twist-odd states of the twisted and untwisted circles carry equal weight at every aspect ratio. That is a degeneracy of the scaling limit. Nothing here proves it.

## Assumptions in the workspace this challenges

| Assumption | Where it lives | Verdict |
| --- | --- | --- |
| Sector additivity might be an exact law | The previous epic's recommendation and this epic's plan | **No.** It is a large-size relation in an orthogonal basis, false at finite size (3 × 3) and broken by shear for a proved reason. |
| The consistency relation is a second law | Scoping in this epic | **No.** It is equivalent to D = odd10 + odd01 − odd11 by an exact duality identity. |
| Exact equalities on the smallest tori are evidence of exact laws | This epic's own scoping | **Half right.** The odd-line identity survived new tori; the shear-independent form, equally exact on small tori, failed at 12 × 8. |
| The odd-line identity and shear independence are the same statement | `TWIST-RELATIONS-20261022-001A-P001` as first written | **Corrected** before closure: relabeling links only s and s + Lh. The stronger form is now refuted. |
| A single half-integer harmonic describes every shear | Scoping on squares | **Only on squares.** On the 2:1 torus higher harmonics appear, and the spin-splitting law fails by 22 standard errors. |

## Provenance and novelty

| Result | Where it came from | Novelty |
| --- | --- | --- |
| Basis covariance and harmonic parity of the twist sectors | Modular covariance of twisted sectors (standard for Z₂ orbifolds), made pathwise for the swap-reversed double cover | Low (expected); the gauge bookkeeping is specific |
| Additivity is a relation of the orthogonal basis; the half-shear obstruction | The parity structure | New to the program; elementary |
| The odd-line identity | Exhaustive small-torus counts, then a pre-registered test | Not found in the literature; a conjecture with strong evidence |
| The refuted shear-independent form | The same counts, then the pre-registered test | A recorded negative |

**Did the relational lens do real work?** Yes.
- **What it changed.** Asking for relations rather than values led to the odd-line identity: an exact statement between two unknown numbers, found while looking at what cancels.
- **What it did not do.** It did not make additivity exact. Additivity turned out to be a symmetry-of-the-frame relation, not a law of the model.

**Ratio since the last checkpoint.**
- 2 artifacts are substantive: the proof and the experiment.
- 2 are administrative: this note and the ledger.

## Recommendation

| Option | What it would do | Interest |
| --- | --- | --- |
| **1. Prove the odd-line identity** (recommended) | **First,** the exact count on the 4 × 4 torus at every shear: 2³² orientations, about half an hour on all cores. It is a decisive check at a new size. **Then** one bounded proof attempt: a configuration-dependent seam bijection whose seam follows the dual barrier, generalizing the height-3 proof. | 2/3 |
| 2. A bounded search for the program's next barrier question | Over the lower bound, space from a law (question 9) and dynamics (question 4), as recommended after the previous epic | 1/3 |
| 3. Pursue additivity itself | It is a scaling-limit degeneracy with no theory to supply it | 1/3 |

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — relations among the twist sectors | **Partially successful** | The exact skeleton is proved. Additivity is mapped and explained as an orthogonal-frame relation that shear dephases. An exact relation, the odd-line identity, is found and confirmed. Its stronger form is refuted. |
| Local direction — exact relations of the twisted model | Continue | One exact candidate survives a pre-registered test and has a partial proof (height 3). |
| Broader exploration — critical emergence of single fair contacts | Practically complete, plus one exact relation | Reduction, class, duality, harmonic structure and an exact loop identity. Open: the lower bound and the scaling-limit degeneracy behind additivity. |
| Long-term goal — emergence from logic | Capability gained | A first exact relation between unknown emergence quantities: a contradiction loop's probability is blind to the transverse twist. |
| Next recommendation — prove the odd-line identity | **Next step:** Continue. A fresh epic: the 4 × 4 exact count, then one bounded proof attempt via barrier-following seams. | A proof would turn the first exact "harmony" of the knot's emergence into a theorem. A failure at 4 × 4 would end it cheaply. |
| Interest — that next step | **2/3 — Promising** | An exact identity is supported at 10⁻⁵ on 8 new tori and proved for height 3. The main uncertainty is that its stronger sibling looked just as exact on small tori and failed. |
| Execution — that next step | Deferred to the owner | Bound: one epic. Stop if 4 × 4 breaks it, or if one proof attempt finds no bijection. |
