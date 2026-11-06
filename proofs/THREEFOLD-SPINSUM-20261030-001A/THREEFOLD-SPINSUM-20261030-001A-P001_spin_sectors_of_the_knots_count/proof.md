# Spin sectors of the knot's count

Status: Proved

Ticket `THREEFOLD-SPINSUM-20261030-001A`, 2026-10-30.

**What it uses:**
- **`THREEFOLD-AMPLITUDE-20261030-001C`:**
  - Lemma 2(a): summing the weight Ω(s) = Π exp((iπ/6) s_w s_p) over spins, lines first, gives (√3)^n #col(H);
  - Lemma 4: a connected cubic signed system is non-colourable iff its signing is Pfaffian.
- **`THREEFOLD-AMPLITUDE-20261030-001A`, Lemma 1:** Pfaffian signings of a matching covered bipartite graph form one switching class.
- **`THREEFOLD-SPIN-20261030-001A`:**
  - the knot's signs are Kasteleyn on every minimal map with planar glue;
  - the Cimasoni–Reshetikhin form q_ref;
  - perfect-matching differences and their classes.
- **`THREEFOLD-SPACES-20261030-001A`, Theorem 1:** the knot's spaces are not 2-colourable.
- **External context, not used as input:** the Arf invariant formula for even subgraphs on surfaces (Kac–Ward, Fisher, Cimasoni,
  Loebl–Masbaum). The form needed here is proved directly.

## Why this ticket exists

The owner approved the question: the knot's amplitude is an Ising count at half the knot's angle, and on a surface such a count is a signed
sum over spin structures. Does 5 per handle come from the even spin structures alone, with the odd one cancelling? This ticket gives the
sum exactly and answers no.

## Standard statement

**Setting.**
- **The space.** H is a three-fold space with n points, and B its incidence graph on a minimal map of genus g; L is a contact (a line).
- **Even subgraphs.** For a graph G, either B or B − L, ℰ(G) is its set of even subgraphs. Each χ has a class [χ] ∈ H₁(Σ; Z₂).
- **The knot's coupling** is x = i/√3. The weight is x^{|χ|} = (−1/3)^{|χ|/2}, since bipartite even subgraphs have even size.
- **Spin structures.** A spin structure is a quadratic form q on H₁(Σ; Z₂) refining the intersection form; there are 4^g, of which
  2^{g−1}(2^g + 1) are even.
- **Sector values.**
  - N_q(B) = (3/2)^n Σ_{χ∈ℰ(B)} (−1)^{q([χ])} x^{|χ|};
  - N_q(B − L) = 2 (3/2)^{n−1} Σ_{χ∈ℰ(B−L)} (−1)^{q([χ])} x^{|χ|}.

**Results.**
- **Lemma 1 (high-temperature form).**
  - #col(H) = (3/2)^n Σ_{χ∈ℰ(B)} x^{|χ|};
  - #col(H − L) = 2 (3/2)^{n−1} Σ_{χ∈ℰ(B−L)} x^{|χ|} = 2A(H, L).
- **Lemma 2 (Arf average).** For every class α, Σ_q (−1)^{Arf(q) + q(α)} = 2^g, the sum running over all 4^g spin structures.
- **Theorem 3 (spin sum).**
  - #col(H) = 2^{−g} Σ_q (−1)^{Arf(q)} N_q(B), and #col(H − L) = 2^{−g} Σ_q (−1)^{Arf(q)} N_q(B − L).
  - Since H is not 2-colourable, its even and odd sectors balance: Σ_{q even} N_q(B) = Σ_{q odd} N_q(B).
- **Proposition 4 (the knot's sign class).** The Kasteleyn sign classes of a minimal map are the knot's signing twisted by the 4^g classes of
  H¹(Σ; Z₂). The knot's own is the only one that is not 2-colourable.
- **Proposition 5 (the Fano torus).** On all 16 maps and for all 7 contacts the sectors are:
  - 8, 8, 8 (even) and 24 (odd) for the closed space;
  - 16, 16, 16 (even) and 28 (odd) with one contact opened.

  The three even spin structures are exactly the knot's own (those induced by its perfect matchings). So
  2A = 10 = (3·16 − 28)/2: the even sectors alone would give 24, and the odd sector does not vanish.
- **Proposition 6 (genus 2).** On the 13-point space the 4 × 4 matrices of sector values, indexed by the spin structures of the two handles,
  have rank 4, both closed and with a contact opened in either atom. So the sectors do not factor over handles, although the amplitude
  does (25 = 5 · 5).

## Nearest known result

- **The Arf invariant formula.** Writing the generating function of even subgraphs of a surface graph as a signed sum over spin
  structures is classical:
  - Kac–Ward and Fisher, through Pfaffians;
  - Cimasoni's generalized Kac–Ward formula;
  - Loebl and Masbaum's Arf invariant formula.

  Theorem 3 is an instance, proved directly here.
- **What is new here** (no overlap found, candidate local delta):
  - reading non-colourability as the balance of spin sectors;
  - the uniqueness of the knot's non-colourable sign class;
  - the sector values, and the failure of factorization.

## Proof of Lemma 1

- **Expanding the weight.** Since exp(iθ s s′) = cos θ (1 + i tan θ s s′) for s, s′ = ±1, the sum Σ_s Ω(s) over all spins of a graph with
  V vertices and E edges equals

  (cos θ)^E 2^V Σ_{χ∈ℰ} (i tan θ)^{|χ|}.

  Expanding the product over edges, a spin summed over gives 0 for every edge set with an odd vertex.
- **The constants.** At θ = π/6, i tan θ = x and cos θ = √3/2.
- **The closed space.** For B (V = 2n, E = 3n), summing the lines first gives (√3)^n #col(H) (`THREEFOLD-AMPLITUDE-20261030-001C`,
  Lemma 2(a)). Comparing the two gives #col(H) = (3/2)^n Σ x^{|χ|}.
- **One contact opened.** For B − L (V = 2n − 1, E = 3n − 3), the n − 1 remaining lines summed out give √3 times not-all-equal each, and the
  points stay free spins. So the sum is (√3)^{n−1} #col(H − L), and comparing gives #col(H − L) = 2 (3/2)^{n−1} Σ x^{|χ|}. ∎

## Proof of Lemma 2

- **One form gives all.** Fix one spin structure q₀. Every spin structure is q₀ + (a · −) for a unique a ∈ H₁, by Poincaré duality.
- **Two facts.**
  - Arf(q₀ + a·−) = Arf(q₀) + q₀(a): substitute x ↦ x + a in the Gauss sum.
  - q₀(a) + a·α = q₀(a + α) + q₀(α).
- **The sum.** Hence

  Σ_a (−1)^{Arf(q₀) + q₀(a) + q₀(α) + a·α} = (−1)^{Arf(q₀)} Σ_a (−1)^{q₀(a+α)} = (−1)^{Arf(q₀)} (−1)^{Arf(q₀)} 2^g = 2^g. ∎

## Proof of Theorem 3

- **The spin sum.** Group the even subgraphs by class: Σ_χ x^{|χ|} = Σ_α E_α. By Lemma 2,

  2^{−g} Σ_q (−1)^{Arf(q)} Σ_α (−1)^{q(α)} E_α = Σ_α E_α.

  Lemma 1 turns both sides into the colouring counts.
- **The balance.** H is not 2-colourable, so the closed sum is 0, which is the balance of even and odd sectors. ∎

## Proof of Proposition 4

- **The Kasteleyn classes.**
  - A cocycle c of the map meets every face boundary evenly, so the twist σ + c satisfies the face condition whenever σ does.
  - Conversely, the face condition is affine in the signing, with the cocycles as its linear part.
  - So the Kasteleyn signings are σ + (cocycles). Up to switching, they correspond to H¹(Σ; Z₂).
- **Which twist is Pfaffian.** Pfaffian signings form one switching class. So σ + c is Pfaffian iff c is a switching (a cut), iff [c] = 0.
- **Colourability.** By the signed dictionary, a connected cubic signed system is non-colourable iff its signing is Pfaffian. Every nonzero
  twist is therefore 2-colourable, and the knot's is not. ∎

## Proofs of Propositions 5 and 6

Both are exact finite computations in `check.py`.
- **The Fano values.** On every map and contact the sector values are as stated. The induced spin structures are identified through the
  intersection form, recovered from q_ref.
- **The genus-2 matrices.**
  - The two handles' homology is spanned by the classes of even subgraphs inside the two shores of the tight cut, 4 classes each.
  - A spin structure is determined by its restrictions to the two handles.
  - The resulting 4 × 4 matrices of N values have rank 4. A factorization N = X(q₁)Y(q₂) would have rank 1. ∎

## What the computation checks

`check.py` (a few seconds):
- **Theorem 3:** 112 Fano and 8 genus-2 identities with a contact opened, plus the closed ones, against colouring counts computed
  independently.
- **Proposition 4:** all 16 Fano maps and 4 maps of the 13-point space; every nonzero twist is Kasteleyn and 2-colourable, 108 twists in
  all.
- **Propositions 5 and 6** exactly.
- **Controls:**
  - at the real coupling x = 1/2 the sectors do not balance;
  - pairing classes by coordinates instead of the intersection form mislabels the knot's spin structures. This was a trap in the scoping
    probe.

## Reading

- **The answer is no.** On the Fano torus the knot's amplitude takes contributions from every spin structure.
  - Its three even spin structures give 16 each, and the odd one 28, so 2 · 5 = (3 · 16 − 28)/2.
  - The odd sector does not cancel, and the even sectors alone would give 12, not 5.
- **The spin decomposition does not localize the handles.** At genus 2 the sectors do not factor over the two handles, though the amplitude
  is exactly 5 · 5. "Five per handle" is a property of the total, which factors through the point lemma across cuts, not of spin sectors.
- **What the spin picture does say.**
  - The knot's contradiction is a cancellation between spin sectors. In the closed Fano space the odd sector, 24, cancels the three even
    ones, 8 each.
  - Opening a contact unbalances them by twice the amplitude.
  - Of the 4^g sign classes the surface admits, the knot's is the only one that cannot be 2-coloured; every twist of it can.
  - This is the relational reading: the contradiction is a balance of the whole, not a local defect.

## Nonclaims

- Sector values are given for the Fano space and the 13-point space only. No general formula for them is claimed.
- The identification of sector values with Pfaffians (Kac–Ward, Fisher) is classical context, not used.
- Non-planar glue is not treated here.
