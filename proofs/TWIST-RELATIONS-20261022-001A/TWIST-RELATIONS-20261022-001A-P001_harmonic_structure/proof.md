# The harmonic structure of the twist sectors

Status: Proved

Ticket `TWIST-RELATIONS-20261022-001A`, 2026-10-22.

**What it uses:**
- from `NAE-INVARIANT-20261022-001A-P001`: the twisted model (the swap-reversed orientation of the double cover) and its topology;
- from `SC-TORUS-EXACT-20261022-001A-P001`: the cone theorem, and the exact twisted duality P(contractible) = P(cross).

## Standard statement

**Setting.**
- **The torus.** T_s = ℤ²/Λ_s with Λ_s = ⟨w1, w2⟩, w1 = (Lh, 0) and w2 = (s, Lv), where Lh, Lv ≥ 3 and s ∈ ℤ.
- **The orientation.** Uniform random.
- **The twist.** (a, b) ∈ {0, 1}² is the homomorphism p: Λ_s → ℤ/2 with p(w1) = a and p(w2) = b. The (a, b)-sector is the twisted model for p, or the orientation itself when p = 0.
- **The cone.** C_(a,b) is the cone of directed classes of the sector: {0}, a line or the plane in twisted sectors.
- **Contractibility.** P_ab(s) = P(C_(a,b) = {0}) on T_s.
- **Notation.** For fixed (Lh, Lv) write:
  - U = P00 + P01 and E = P00 − P01;
  - G = P10 + P11 and O = P10 − P11;
  - D = P00 − P10 − P01 + P11 = E − O.

1. **Basis covariance (pathwise).**
   - (a) **Shear by Lh.** T_{s+Lh} is the torus T_s with basis (w1, w1 + w2). For every orientation, its (a, b)-sector is the (a, a + b)-sector of T_s, with classes mapped by (x, y) ↦ (x + y, y).
   - (b) **The mirror.** The mirror (x, y) ↦ (−x, y) maps T_s onto T_{−s}. Every sector of an orientation corresponds to the same sector of the mirrored orientation, with classes mapped by (x, y) ↦ (−x, y). Two adjustments make this exact:
     - horizontal arrows are reversed, except on edges crossing the twist's seam;
     - the seam is then moved by a gauge transformation.
   - (c) **Half shear.** When 2s = Lh, mirroring exchanges the (1, 0)- and (1, 1)-sectors.
2. **Harmonic parity.**
   - **Periods.** U, E and G are even in s and periodic with period Lh. O is even in s and antiperiodic: O(s + Lh) = −O(s).
   - **Harmonics.** Over the period 2Lh:
     - U, E and G contain only the whole harmonics cos(2πks/Lh);
     - O contains only the half-integer harmonics cos((2k + 1)πs/Lh).
   - **Consequences.** O(Lh/2) = 0, D(s) = E(s) − O(s) and D(s + Lh) = E(s) + O(s).
3. **Why shear breaks additivity.**
   - **At half shear.** D(Lh/2) = P00 − P01: additivity holds there exactly when twisting along w2 leaves contractibility unchanged.
   - **In two bases.** Additivity in both bases (w1, w2) and (w1, w1 + w2) of the same torus forces E = O = 0.
   - **What additivity is.** Additivity in a basis says the Fourier coefficient Σ_p (−1)^{p(q)} P_p vanishes at the mod-2 class q of w1 + w2. It is a property of the class singled out by the basis, not of the torus.
4. **The duality equivalence.**
   - **The identity.** In every twisted sector, P(consistent) = 1 − P(contractible) − P(odd winding).
   - **Hence:** 1 − cons10 − cons01 + cons11 − P00 = −D + odd10 + odd01 − odd11.
   - **What this means.** The consistency relation observed on rectangles is equivalent to D = odd10 + odd01 − odd11. It is not a separate law.
5. **None of the measured large-size relations is a finite-size identity.** Exhaustive counts on the 3 × 3 torus:
   - D(0) = 2581/32768 ≠ 0;
   - E(1) = −15525/131072 ≠ E(0) = −4341/32768;
   - O(1) = −13013/131072 ≠ O(0) cos(π/3) = −3461/32768;
   - 1 − cons10 − cons01 + cons11 = 763/65536, while P00 = 5925/65536.

**Conjecture 6 (verified, not proved): odd lines.**
- **The identity.** Let c be a primitive class, and p, p′ the two nonzero twists with p(c) = p′(c) = 1. Then P(C_p = ℝc) = P(C_p′ = ℝc).
- **A stronger form, verified on the same tori.** For the twist odd on w1 and even on w2, P(C = ℝw1) does not depend on the shear s at all. By Theorem 1(a) this implies the identity for c = w1. (Corrected on 2026-10-22, before the epic closed: an earlier wording called the two forms equivalent, but relabeling links only s and s + Lh.) **This stronger form is refuted** by `TWIST-RELATIONS-20261022-001B-E001`. On 12 × 8 the probability falls from 0.000918 at shear 0 to 0.000861 at shear 6 (7.3 standard errors). Its exact equality on the smallest tori was a coincidence. The identity itself was accepted there.
- **Consequence.** odd10 + odd01 − odd11 = 2 Σ P(C_(1,0) = ℝc), summed over the classes c ≡ (1, 1) mod 2.
- **Evidence.**
  - Exact on 3 × 3 at shears 0 and 1 (check.py).
  - Exact on 4 × 3, 3 × 4 and 5 × 3, including sheared 4 × 3 (a scratch C enumeration).
  - Within a few parts in 10⁶ on eleven larger tori (scratch Monte Carlo).
  - The confirmatory test is `TWIST-RELATIONS-20261022-001B`.

## Nearest known result

- **Theorems 1–2.** These are the lattice, pathwise form of the modular covariance of twisted partition functions, Z_{a,b}(τ + 1) = Z_{a,a+b}(τ), standard for Z₂ orbifolds in conformal field theory. Expected; low novelty. What is specific here is the gauge bookkeeping for the swap-reversed double cover.
- **Theorem 4.** Elementary from the twisted duality.
- **Conjecture 6.** Not found in the literature. The twisted model itself comes from the previous epics.

## Theorem 1: basis covariance

**The sector depends only on the torus, the twist and the orientation.**
- **What it is.** The double cover is ℤ²/ker p; its orientation reverses on the sheet that the swap exchanges; its cone is a subset of ℝ².
- **What the basis does.** It only names the twist by (p(w1), p(w2)) and names classes by coordinates.

**(a) Shear by Lh.**
- **The same torus.** (s + Lh, Lv) = w1 + w2, so Λ_{s+Lh} = Λ_s, and the two tori have the same edges.
- **Labels.** In the basis (w1, w1 + w2), the twist labelled (a, b) has p(w2) = a + b, and the class x w1 + y(w1 + w2) is (x + y) w1 + y w2.
- **The construction itself is unchanged.**
  - The double cover gives the edge with period offset v the sheet change p(v).
  - Offsets differ between the two bases only on the edges that wrap vertically: (α − 1, 1) against (α, 1).
  - For the twist (a, b) in the new basis and (a, a + b) in the old, the sheet change is (α − 1)a + b ≡ αa + (a + b) (mod 2).
  - So the two double covers are the same digraph.

**(b) The mirror.**
- **The map.** M(x, y) = (−x, y) maps ℤ² to itself and Λ_s onto Λ_{−s}. M w1 = −w1, and M w2 is the second period of T_{−s}. It fixes every twist label and maps classes by (x, y) ↦ (−x, y).
- **Two bookkeeping effects in the double cover.**
  - **Lattice tails swap.** M exchanges the lattice tail and head of every horizontal edge. A lift's orientation is read at the sheet of its lattice tail, so for edges with sheet change 0 the image arrow is the reverse of the source bit. For seam-crossing edges (sheet change 1), the two lifts swap their tails' sheets and the bit is kept.
  - **The seam moves.** The image seam lies where M puts it, not where T_{−s} puts its own.
- **The gauge transformation.** Flip the sheets of a vertex set R, where R solves r(u) + r(w) = (old sheet change) + (new sheet change) on every edge; it exists because the two seams lie in the same twist class. This is an isomorphism of the double cover. In terms of base bits, it reverses the edges whose lattice tail lies in R.
- **Conclusion.** After these two steps the double covers are isomorphic, so kind, oddness and mapped class agree.

**(c) Half shear.**
- **The setting.** When 2s = Lh, T_{−s} = T_{s−Lh} is T_s with the basis (w1, w2 − w1).
- **Applying (a).** The (1, 0)-sector of T_{−s} is the (1, 1)-sector of T_s.
- **Composing with (b).** The (1, 0)-sector of an orientation equals the (1, 1)-sector of its mirrored, gauge-fixed image. ∎

## Theorem 2: harmonic parity

The maps of Theorem 1 are bijections of orientations, so they preserve the uniform law:
- P_(a,b)(s + Lh) = P_(a,a+b)(s);
- P_(a,b)(−s) = P_(a,b)(s).

**The four combinations.** The sectors (0, b) are fixed by the relabelling and (1, 0) ↔ (1, 1) are exchanged, so:
- E(s + Lh) = E(s) and U(s + Lh) = U(s);
- G(s + Lh) = G(s);
- O(s + Lh) = −O(s).

All four are even in s by the mirror.

**The harmonics.** A function on ℤ of period 2Lh is a finite sum of e^{iπks/Lh}.
- Period Lh removes the odd k, and antiperiod Lh removes the even k.
- Evenness turns each sum into cosines.

**The remaining statements.**
- O(Lh/2) = −O(−Lh/2) = −O(Lh/2), so O(Lh/2) = 0.
- D = E − O by definition, and the shift gives D(s + Lh) = E(s) + O(s). ∎

## Theorem 3: why shear breaks additivity

- **At half shear.** Since O(Lh/2) = 0, D(Lh/2) = E(Lh/2) = P00 − P01.
- **In two bases.** If D(s) = 0 and D(s + Lh) = 0, then E(s) − O(s) = 0 and E(s) + O(s) = 0, so E(s) = O(s) = 0.
- **The Fourier form.** It is the definition of the coefficient, with p(w1 + w2) = a + b. ∎

## Theorem 4: the duality equivalence

**The identity.** In a twisted sector:
- **Cone and topology.** The cone is {0}, a line or the plane: contractible, a winding in the class of the line, or cross.
- **Consistency.** The sector is consistent exactly when no cluster is odd: it is contractible or winds in an even class.
- **Duality.** P(contractible) = P(cross).
- **So:** P(consistent) = P(contractible) + P(even) = 1 − P(cross) − P(odd) = 1 − P(contractible) − P(odd).

**The relation.** Substituting this into 1 − cons10 − cons01 + cons11 − P00 gives −D + odd10 + odd01 − odd11. ∎

## Proposition 5: not finite-size identities

check.py enumerates all 2¹⁸ orientations of the 3 × 3 torus at shears 0 and 1. It obtains the exact values in Theorem 5 of the statement. At shear 1 on a torus of width 3, cos(π/3) = 1/2 exactly, so the first-harmonic law can be tested in exact arithmetic.

## Interpretation (not theorem)

- **Spin.** In a transfer-matrix reading along w2, the shear acts on the momentum of states on circles of length Lh:
  - E and U come from the untwisted circle, with whole momenta.
  - G and O come from the twisted circle. There, going once around applies the twist, so its twist-odd states carry half-integer momenta: "spin 1/2".
- **Additivity.** On rectangles, additivity says the twist-odd parts of the two circles carry equal weight at every aspect ratio. A shear dephases them, and half a turn kills O.
- **Measured shear dependence (scoping, not evidence).**
  - On squares, E is nearly constant and O ≈ O(0) cos(πs/L), so D(s) ≈ E(0)(1 − cos(πs/L)).
  - On the 2:1 torus sheared along its long side, higher harmonics appear. The law O = cos(πs/L) E fails there.
- **Conjecture 6 in words.** A contradiction carried by a single odd loop along c does not see how the transverse direction is glued.

## Check

`check.py` (standard library):
- **Pathwise covariance.** Theorem 1 (a), (b) and (c) on sampled orientations of six tori: 4 × 3 s = 1, 4 × 4 s = 2, 5 × 4 s = 2, 6 × 4 s = 3, 6 × 5 s = 1 and 5 × 5 s = −2. Kind, oddness and mapped class must agree in all four sectors.
- **Exhaustive 3 × 3 at shears 0 and 1:**
  - contractible and cross counts agree;
  - the identity of Theorem 4 holds exactly, and so does the relation derived from it;
  - the four large-size relations fail;
  - Conjecture 6 holds, as does shear independence of the odd horizontal line.
- **Controls (must give mismatches):** shearing without relabelling, and mirroring without reversing horizontal arrows.

## Scope

- Square-lattice tori with periods (Lh, 0) and (s, Lv), under uniform random orientations and their twisted double covers.
- Theorems 1, 4 and 5 are exact at every size. Theorems 2 and 3 are exact consequences.
- The large-size relations and Conjecture 6 are not proved here.
- No space or physics is claimed.
