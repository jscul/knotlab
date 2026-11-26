**Short version:** I found no error in (A)–(E) or (G), but I could not check (F), C5 has a sign-convention trap, and the verdict misses that the sign is a local phase gate on each reader.

## 1. Correctness

- **(A)** Correct, and it is an operator identity: the O_iO_j term lives only on n_i = n_j = 1, where the E terms vanish.
- **(B) criterion** Correct, including even n. Sharpness for all even T forces every derivative q(x+t)+q(x) to be affine with linear part x·t (since x·t^c = x·t on even words). For even n, the all-ones word is the radical of the dot form, q is linear there, and X^n = (-1)^{q(1)} is sharp.
- **Non-character clause** It is redundant: once the polar form is the dot product, c(T) = (-1)^{q(t)} cannot be a character for n ≥ 3. Say so, or it looks like a second condition.
- **(B) cyclic shifts** Correct. The polar form of d vanishes on the even code iff the adjacency matrix is u1ᵀ+1uᵀ, i.e. a cut. Transitivity of inversion sets then forces S to be a prefix or suffix. The residual sign is |x∩S|, i.e. Z_S, so "moved readers" may equally be the unmoved ones.
- **(C)** Correct, but only for real X/Z readings (see section 3).
- **(D)** The counts check: graphs mod cuts give 8 forms, 24/4 = 6 classes are reached, and 6 × 8 = 48.
- **(D) sign convention** The n = 3 rule only matches the recorded FIFO result if "ascending creator basis" already puts h = -1 on weight-2 words for the uniform ascending start. Under the opposite convention the rule flips to its complement. Freeze the convention and one anchor row; the count 48 is convention-blind, so freeze which 48.
- **(E) sign rules** The algebra is right, but the b-term is linear, not nothing: it is Z on a subset and relabels X outcomes. State that "equivalent" means up to relabelling, or fixed-label exactness will appear to fail.
- **(E) phases** For θ ≠ 0, π a swap sign is not well defined, because swapping twice gives e^{2iθ}. You are really defining s^{#inversions}; say so. I reproduce (cos θ − 1)/2 and the cos θ < 1/3 threshold.
- **(F)** I could not derive this, because "record" is not defined in what you sent. I do confirm F2 with K as written maps the pair state to the antisymmetric one, so that reader is killed. The prefix criterion also follows from (B), given −X = Z X Z.
- **(G)** Correct. The coherent sum is the identity Σ sgn = 0 over S_k for k ≥ 2, and with any order register it reduces to the mixture.

## 2. Theorems versus tests

- **Cannot fail except by a bug:** the G gate identity, C1 (everything is defined in the abstract CAR algebra), C2, the coherent part of C7, and the sign-rule half of C6. Label these as engine checks.
- **C3 is one-sided as written.** Run all n! orders at n = 5 and 6 (120 and 720) and assert that exactly n carry, including the odd-T cells.
- **Most informative if it failed:** C3 at n = 5 and 6, then C8 (the least derived), then the identity of the 48 in C5.
- **Shared-convention risk:** your engine and your derivation share conventions, so have the referee's code run C3 and C5.

## 3. The verdict

**The sign is a local gate.** On even words (-1)^{C(|x|,2)} = i^{|x|}, which is diag(1,i) applied to every reader. The positive state is (|+…+> + |−…−>)/√2, an ordinary GHZ state that carries the full contradiction under Y/Z readings. Consequences:

- (C) and every "no contradiction" mean "none with real X/Z readers".
- The θ-family is all one local-unitary orbit.
- Swapping g'_x for g_x in the flip (i·g_x g_y is Hermitian) is a reader convention on a par with (F). I expect it to move the contradiction to depth-first and other non-cyclic orders; add it to C8.
- The verdict should say that order matters only relative to a fixed real reader convention.

**The round structure is also an ordering.** It is a breadth-first schedule, so "the model's own contribution" is not order-free.

**A fairer test (new C9): general interleaved schedules.** Take any sequence of the 2n events with each creation before its own birth. For an occupied pair, disjoint and nested intervals cost nothing and crossing intervals cost −1. Prediction: the schedule carries iff its crossing graph equals K_n up to a cut. This reproduces what you have:

- FIFO: all pairs cross.
- Reversed order: all pairs nested, so nothing.
- Cyclic shift: K_n minus a cut.
- Depth-first: empty graph.

Weight over all (2n)!/2^n schedules and report the carrying fraction. That number, not n/n!, answers "model versus ordering".

**Other things to say:**

- Joint weighting over (σ, π) adds nothing, since only σ⁻¹π enters. State it as a theorem.
- FIFO is a candidate native rule that needs no second supplied order. Depth-first is another, and they disagree; the verdict should admit this.
- "Unique among sign rules" covers only the 8 symmetric, holding-dependent pair rules.
- n/n! presumes a uniform measure over orders.
- The second round is untested, so the claims are for one round.

## 4. Literature

I know no source stating the cyclic-class result itself. The pieces are:

- **Quadratic-form phases on a code:** Dehaene and De Moor (2003) on stabilizer states over GF(2); Hein, Eisert and Briegel on graph states.
- **Graphs modulo cuts:** this is Seidel switching, i.e. two-graphs (Seidel; Cameron). It is the right name for your (D) count, 2^{C(n-1,2)} = 8 classes at n = 4.
- **Inversion and crossing graphs:** permutation graphs and circle graphs (chord diagrams).
- **Non-character as obstruction:** Mermin (1990); Abramsky and Brandenburger; Okay, Roberts, Bartlett and Raussendorf (2017).
- **Reversal sign and fermion parity:** Clifford reversion (Lounesto); Bravyi and Kitaev on fermionic computation.
- **Graded cyclicity:** cite the supertrace only as an analogy.
