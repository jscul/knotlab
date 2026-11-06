# Emergence is countable exactly when it is topological

Status: Proved

Ticket `NATIVE-COUNTING-20261024-001A`, 2026-10-24.

**What it uses:**
- from `SURFACE-GLUING-20261024-001` (closed):
  - the criterion for topological gluing, that two glued copies are symmetric in their four legs;
  - the four topological knots;
  - their identification as the fusion rules of the abelian and Fibonacci theories;
- from `NATIVE-HARDNESS-20261024-001` (closed): native networks are edge problems, with each variable in two constraints, and they
  are decided in polynomial time;
- external theorems, cited as hypotheses and not admitted as local evidence:
  - **(B)** Backens, *A complete dichotomy for complex-valued Holant^c*, ICALP 2018 (arXiv:1704.05798), Theorem 15. Holant^c(F) is
    #P-hard unless:
    - F is tractable for Holant*, that is F ⊆ ⟨T⟩, F ⊆ ⟨O∘E⟩ for a complex orthogonal O, F ⊆ ⟨K∘E⟩, or F ⊆ ⟨K∘M⟩ or ⟨KX∘M⟩;
    - F ⊆ S∘A for a matrix S taking the equality and the pins to affine functions;
    - or F ⊆ L.
  - **(CHL)** Cai, Huang and Lu, *From Holant to #CSP and back* (2012); Cai, Lu and Xia (2009): the same dichotomy for symmetric
    signatures.

## Standard statement

**Setting.**
- **Counting native networks.** A native network has knots, internal edges each shared by two knots, and legs, pinned or unpinned.
  Its count is the number of assignments to the internal edges and unpinned legs satisfying every knot. Networks whose only unary
  constraints are pins are the instances of Holant^c with the knot as the only other constraint.
- **Symmetric signatures and gluing.** A symmetric signature is written [f₀, f₁, f₂, f₃], with f_k its value on inputs with k ones.
  Two copies glued along one edge give g(a, b, c, d) = Σₑ f(a, b, e) f(e, c, d).

**Theorem 1 (the gluing criterion is the Fibonacci recurrence).** For a complex symmetric signature, these are equivalent:
- (a) g is symmetric in its four legs, the criterion for topological gluing;
- (b) f₀ f₂ + f₁ f₃ = f₁² + f₂²;
- (c) f is a generalized Fibonacci gate (f₂ = m f₁ + f₀ and f₃ = m f₂ + f₁ for some m), or f = [a, 0, 0, b].

Among the 34 knots, exactly four satisfy them: the two parity knots (m = 0) and the two "no lone value" knots (m = 1 for no lone one,
m = −1 for no lone zero).

**Theorem 2 (the topological knots count in polynomial time).**
- **Two cubes.** Each topological knot is λ₀ v₀^⊗3 + λ₁ v₁^⊗3 with v₀ and v₁ orthonormal:
  - even parity: v = (1, ±1)/√2 and λ = √2, √2;
  - odd parity: the same vectors, with λ = √2, −√2;
  - no lone one: v_j = (S₀ⱼ, S₁ⱼ) and λ_j = 1/S₀ⱼ, with S = (1/D)[[1, φ], [φ, −1]] and D² = 2 + φ;
  - no lone zero: the same with the two values exchanged.
- **The count.** For a connected native network with n knots,
  count = Σⱼ λⱼⁿ ∏ over legs uⱼ(leg),
  where uⱼ is vⱼ(a) for a leg pinned to a, and vⱼ(0) + vⱼ(1) for an unpinned leg.
- **Closed forms.** With all L legs pinned and genus g = (n − L)/2 + 1:
  - the even parity knot gives 2^g if the pins have an even total, and 0 otherwise;
  - the odd parity knot gives 2^g if the pin total has the parity of n;
  - the no-lone-one knot gives D^(2g−2) (φ^t + (−1)^t φ^(2−2g−t)), with t the number of pins equal to 1.
- So these counts are computed in polynomial time.

**Theorem 3 (the other 30 knots, given B).** Each of the other 30 knots lies in none of the tractable families of (B). So, given (B),
counting their native networks with pins is #P-hard. For the three symmetric ones (not-all-equal, the three-place clause and its
complement), (CHL) gives the same.

**Corollary 4 (emergence is countable exactly when it is topological).** Among the 34 knots:
- counting native networks is polynomial exactly for the four knots that see only the surface;
- for every other knot it is #P-hard, given (B), even though deciding is polynomial for every knot (`NATIVE-HARDNESS-20261024-001C`).

**Reading.**
- **What is easy and what is not.** The emergent information of a native network is the logarithm of its count. It is easy to know
  exactly when the law is topological, and hard otherwise.
- **The same objects twice.** Holographic algorithms with Fibonacci gates and two-dimensional topological field theories are the same
  objects here. A symmetric knot sees only the surface exactly when its algebra is diagonalized by an orthogonal change of basis.

## Nearest known result

- **Fibonacci gates.** Cai, Lu and Xia, *Holographic algorithms by Fibonacci gates* (Linear Algebra Appl. 2013): generalized Fibonacci
  gates are tractable on general graphs. Cai, Guo and Williams (arXiv:1307.7430): they are product type after a holographic
  transformation, and [1, 0, 1, 1], the no-lone-one knot, is their standard example.
- **Topological field theories.** Two-dimensional topological field theories are commutative Frobenius algebras (Dijkgraaf; Abrams
  1996), and their counts are Verlinde dimensions.
- **The local contribution** is the identification. The gluing criterion of `SURFACE-GLUING-20261024-001A` is exactly the
  Fibonacci-gate recurrence, and the knots that see only the surface are exactly the knots whose native counting is tractable. Novelty:
  `candidate-local-delta`; folklore risk high, since experts may know the equivalence in another language.

## Proof

### Theorem 1

- **The four-leg function.** By symmetry of f, g(a, b, c, d) = G(a + b, c + d) with G(s, t) = f_s f_t + f_{s+1} f_{t+1}.
- **The one condition.** G is symmetric, and g is invariant under exchanging a with b, c with d, and the pair (a, b) with (c, d). So g
  is symmetric in all four legs exactly when it is also invariant under exchanging b and c.
  - With total weight 0, 1, 3 or 4, that exchange preserves the pair of weights {a + b, c + d}.
  - With total weight 2, it can turn (2, 0) into (1, 1).
  - So the only condition is G(2, 0) = G(1, 1), which is f₀ f₂ + f₁ f₃ = f₁² + f₂². This gives (a) ⟺ (b).
- **(b) ⟺ (c).**
  - If f₁ ≠ 0, put m = (f₂ − f₀)/f₁. Then (b) reads f₁ f₃ = f₁² + f₂ m f₁, that is f₃ = m f₂ + f₁.
  - If f₁ = 0, (b) reads f₂(f₀ − f₂) = 0. Either f₂ = 0, so f = [a, 0, 0, b]; or f₂ = f₀ ≠ 0, which is a gate with m = f₃/f₀.
- **The knots.** Asymmetric knots are not symmetric signatures, and among the seven symmetric knots the check finds exactly four. ∎

### Theorem 2

- **The decompositions.** The check verifies that each decomposition reproduces the knot and that the vectors are orthonormal. For
  no lone one this is the Verlinde formula N_abc = Σⱼ S_aj S_bj S_cj / S₀ⱼ.
- **The count.** The count is the full contraction of the network's tensors. Insert the decompositions.
  - An internal edge between knots carrying the terms j and j′ contributes Σₐ vⱼ(a) vⱼ′(a) = δⱼⱼ′.
  - In a connected network every knot therefore carries the same j.
  - Each knot contributes λⱼ, and each leg its value uⱼ.
- **Parity, closed form.** For even parity with all legs pinned,
  Σ over s = ± of 2^(n/2) 2^(−L/2) s^(Σ a) = 2^((n−L)/2) (1 + (−1)^(Σ a)).
  This is 2^g when the pin total is even. Odd parity is the same with λ₁ = −√2.
- **No lone one, closed form.**
  - With t pins equal to 1, Σⱼ S₀ⱼ^(−n) S₀ⱼ^(L−t) S₁ⱼ^t = D^(n−L)(φ^t + (−1)^t φ^(L−n−t)).
  - Since 3n = 2E + L and g = E − n + 1, n − L = 2g − 2.
- **Time.** The genus and the pin counts are read off in linear time, and the formula is exact arithmetic in Q(√5). ∎

### Theorem 3

Each family test is finite:
- **Products.** A ternary product of unary and binary functions factors across one variable, so some 2 × 4 unfolding has rank one.
- **Generalized equalities after a transformation.** A ternary signature in ⟨O∘E⟩ or ⟨K∘E⟩ that does not factor is
  α a₁⊗a₂⊗a₃ + β b₁⊗b₂⊗b₃.
  - Every factor pair {aᵢ, bᵢ} spans the same two lines.
  - These two lines are orthogonal and non-isotropic (O), or the two isotropic lines spanned by (1, i) and (1, −i) (K).
  - In each mode the lines are read off as the perpendiculars of the roots of the binary quadratic det(contraction with φ) = 0. A
    repeated or vanishing quadratic means the signature is not of this kind.
- **Weight at most one.** Membership in ⟨K∘M⟩ and ⟨KX∘M⟩ is tested by applying K⁻¹ or (KX)⁻¹ and checking that the result vanishes
  on inputs of weight two or more.
- **S∘A.** The rows of S must be affine unary vectors, so they are proportional to one of (1, 0), (0, 1), (1, ±1) or (1, ±i). The
  ratio of the two row scales is fixed by requiring SᵀS to be one of finitely many binary patterns. The check tests a superset of
  these S: every pattern with entries in {0, ±1, ±i}, which is 768 matrices. Then (S⁻¹)^⊗3 f must be affine.
- **L.** A 0/1 signature in L has affine support. Knots other than parity have 5, 6 or 7 allowed tuples, so their support is not
  affine.

The check runs these tests on all 34 knots. Exactly the four topological knots pass one, the orthogonal generalized equalities, and
the two parity knots also pass S∘A. The other 30 pass none, and (B) gives #P-hardness. ∎

## Checks

`check.py` uses the standard library only (seed 20261024), with complex floating point (tolerance 10⁻⁹) for the family tests and
exact Q(√5) arithmetic for the closed forms. It confirms:
- **Theorem 1** on all 625 symmetric signatures with entries in {−2, …, 2}: four-leg symmetry, the equation and the gate condition
  agree everywhere; the knots satisfying it are exactly the four.
- **Theorem 2** on 366 random connected native networks with up to 7 knots, pinned and unpinned legs and up to 13 internal edges: the
  formula equals the brute-force count every time, and the closed forms agree on every network with all legs pinned.
- **Theorem 3:** 4 knots in some family and 30 in none.

**Controls.**
- **Each family test can say yes.** Each accepts a constructed member: a product, a rotated generalized equality, K applied to a
  generalized equality, K applied to a weight-at-most-one function, an S-transformed parity function, and a point mass (local affine).
- **Each family test can say no.** All reject a random complex tensor.
- **The count formula is not loose.** Replacing λⱼⁿ by λⱼ^(n+1) disagrees with the brute-force counts.

## What this does not show

- **Local proofs of (B) and (CHL).** Theorem 3 is conditional on them.
- **Other counting questions.** Counting with hubs, approximate counting, and laws mixing knots: gates with different m do not combine
  tractably in general.
- **Networks without pins.** These can be easier: ticket B treats the closed worlds of not-all-equal.
