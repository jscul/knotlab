# What composing like cycles is good for: codes, constraint complexity and counting

Status: Proved

Ticket `CYCLE-UTILITY-20261021-001A`, 2026-10-21. It uses:
- `AFFINE-TOPS-20261021-001A-P001` ("the rectangularity proof"): Theorem 3 and
  Corollaries 5 and 6;
- `AFFINE-TOPS-20261021-001B-P001` ("the affine proof"): Theorems 1 and 3;
- `CYCLE-TOPS-20261021-001B-P001` ("the tops proof"): Corollary 3, ties are
  bijections of tops;
- `MATROID-CONVERSE-20261021-001B-P001`: the class 𝓡;
- `MALTSEV-CONVERSE-20261020-001B-P001` ("the converse proof"): Lemma 2, the
  selector hub;
- the definitions of `KNOT-CIRCUITS-20261020-001B-P001`.

It also cites four outside results:
- Pappus's theorem;
- the Taylor criterion for finite idempotent algebras;
- the CSP dichotomy theorem;
- the counting dichotomy of Dyer and Richerby.

The novelty scan behind this ticket is
`research/CYCLE-UTILITY-20261021-001/novelty_scan.md`.

## Standard statement

**This proof shows the following.**
1. **Codes** (Proposition 1).
   - **The criterion.** If the law of a relation composes like cycles, every
     matroid of its systems lies in 𝓡, with components over finite fields.
     So a code whose composition closure composes like cycles behaves like a
     linear code.
   - **The non-Pappus code fails.** Simonis and Ashikhmin's almost affine code
     over F₃² has uniform fibres and the non-Pappus matroid. Its law therefore
     fails elimination.
   - **The failing system** uses three copies of the code: an equivalence of
     the alphabet, defined by one copy, attached to two coordinates of
     another.
2. **Constraint complexity** (Proposition 2).
   - **With constants.** If a law still composes like cycles after all
     constants are added, its polymorphism algebra is Taylor. By the CSP
     dichotomy theorem, its constraint problem is solvable in polynomial time.
   - **With trivial tops,** a genuine Mal'tsev polymorphism exists.
   - **NP-hard laws fail.** One-in-three, not-all-equal and 3-colouring each
     give an explicit elimination failure.
3. **Counting is not covered** (Proposition 3). The lifted Z₃ law and K₄
   compose like cycles but are not balanced. So, by Dyer and Richerby, counting
   their solutions is #P-complete.
4. **Constants can destroy composing like cycles** (Proposition 4).
   - In parity beside J, and in K₄, fixing one variable to a value exposes a
     non-bijective tie inside a top class.
   - So the hypothesis of Proposition 2 is strictly stronger than composing
     like cycles.
   - Whether every law that composes like cycles has a polynomial-time
     constraint problem is open.

**The limits.** No claim about P versus NP is made. Propositions 2 and 4 are
about which laws are tractable, given the dichotomy theorem.

## Nearest known results

See the novelty scan for the full list. The ones used here:
- **Almost affine codes and entropic matroids.** [Abbe and
  Spirkl](https://arxiv.org/abs/1909.12175) reproduce Simonis and Ashikhmin's
  non-Pappus code as an example of a 9-entropic matroid that is not
  representable over any field.
- **Counting.** [Dyer and Richerby](https://arxiv.org/abs/1003.3879): the
  counting problem of a finite language is in FP when it is strongly balanced,
  and #P-complete otherwise.
- **The Taylor criterion.** A finite idempotent algebra has a Taylor term
  exactly when no two-element algebra of projections lies in HS(A), that is,
  among the quotients of its subalgebras (Bulatov; Szendrei). It is stated,
  for example, in [this survey of binary minimal
  clones](https://arxiv.org/abs/2301.12631).
- **The dichotomy theorem.** [Bulatov](https://arxiv.org/abs/1703.03021) and
  [Zhuk](https://arxiv.org/abs/1704.01914): for a finite structure with
  constants, the constraint problem is in P when the polymorphism algebra is
  Taylor, and NP-complete otherwise.

**Classification: corollaries and examples; new to the program.**
- Propositions 1 and 2 are short consequences of the affine-tops results
  combined with classical theorems.
- The explicit systems of Propositions 1 and 4 are computations.

## Proposition 1 (codes)

Let C be a relation whose law composes like cycles. Then every system of that
law, C included, has a matroid that is a direct sum of rank-one parallel
classes and matroids representable over finite fields.

Suppose also that:
- every coordinate of C ranges over the whole alphabet;
- C has a circuit of three or more variables, so the alphabet is a knot range;
- the alphabet carries no proper nontrivial pp-definable equivalence.

Then C is a coset of a module code M ⊗_D U over a finite field D.

*Proof.* The first statement is the affine proof's Theorem 3. For the second:
- **Trivial tops.** The tops are equality, so the top image is C itself.
- **A coset.** By that proof's Theorem 1, C is a coset of an R-submodule H.
- **The module code.** Its Theorem 3 gives H = M ⊗_D U. ∎

**The non-Pappus code.** Simonis and Ashikhmin's code is the row space, over
F₃, of a 6 × 9 matrix with entries in F₃² (reproduced by Abbe and Spirkl).
- **It is almost affine.** It has 729 codewords, and every projection has a
  power of 9 elements.
- **Its matroid is the non-Pappus matroid.** The rank-two triples are exactly
  the eight lines {1,2,3}, {4,5,6}, {1,5,7}, {1,6,8}, {2,4,7}, {2,6,9},
  {3,4,8} and {3,5,9}.
- **It is not representable.** By Pappus's theorem it is representable over
  no field, so it is not in 𝓡.
- **Its law fails elimination.** By Proposition 1, the law of this code does
  not compose like cycles, even though the code alone satisfies elimination.

The checks exhibit the failure.
- **Its only unary polymorphisms** are 0, the identity and negation.
- **The equivalence θ.** One copy of the code, with its nine coordinates
  identified into six variables (pattern 5,3,0,3,1,5,4,5,2, visible variables
  3 and 5), defines the equivalence θ: x − y ∈ ⟨(1,2)⟩ on the alphabet.
- **The failing system.** Take the coordinates c₁, c₂, c₄ and c₅ of a
  second copy, and attach w₁ and w₂ to c₁ and c₂ by θ.
  - Its circuits are {c₁,w₁}, {c₂,w₂}, {c₁,c₂,c₄,c₅}, {c₁,c₄,c₅,w₂} and
    {c₂,c₄,c₅,w₁}.
  - {c₁,w₁} and {c₁,c₄,c₅,w₂} share c₁, but {w₁,c₄,c₅,w₂} is free.
- **The mechanism is the top lemma failing.** Modulo θ the code becomes a
  ternary code. There, 171 sets change status, {1,2,4,5} first among them: it
  is free modulo θ but dependent in the code. In a law that composes like
  cycles a system and its blur have the same circuits; here they do not.

**What this gives coding theory.**
- **The gap.** A single code with uniform fibres can carry a matroid
  representable over no field. That is how 9-entropic matroids fail to be
  linear.
- **What closes it.** Closing the code under composition and keeping
  elimination brings back finite-field representability. Linear codes pass
  this test, since affine laws over a finite field compose like cycles.
- **The open question it does not settle.** For a prime p, it is open whether
  every p-entropic matroid is linear. In this language the question asks
  whether every such matroid is carried by a code that passes the test.

## Proposition 2 (constraint complexity)

Let Γ be a single-sorted law, and Γ⁺ the law with every constant added as a
unary relation. Suppose Γ⁺ composes like cycles.
- Then the algebra of polymorphisms of Γ⁺ has a Taylor term. By the CSP
  dichotomy theorem, the constraint problems of Γ⁺, and so of Γ, are solvable
  in polynomial time.
- **Trivial tops.** If every range of Γ has trivial top, Γ has a genuine
  Mal'tsev polymorphism, and Bulatov and Dalmau's Mal'tsev algorithm applies.
  This holds without the dichotomy theorem.

*Proof.* The polymorphisms of Γ⁺ fix every constant, so their algebra A is
idempotent. Suppose a two-element algebra of projections lies in HS(A): it is
U/θ, for a subuniverse U and a congruence θ on U.
1. **U is a range and θ is its top.** U and θ are invariant under all
   polymorphisms, hence pp-definable in Γ⁺ (the Galois connection for finite
   structures). So U is a range.
   - θ is a maximal proper equivalence on U, because U/θ has two elements.
   - Since Γ⁺ composes like cycles, U has a unique maximal proper pp-definable
     equivalence μ_U. So θ = μ_U.
2. **A relation that is not a bijection.** Let ρ be {(0,0), (0,1), (1,0)} on
   U/θ, and ρ̃ its preimage in U².
   - Every polymorphism acts on U/θ as a projection, so it preserves ρ̃.
     Hence ρ̃ is pp-definable.
   - Both variables of ρ̃ range over U, and ρ̃ is constrained, so it is a tie.
     Its top image is ρ, which is not a bijection.
3. **The contradiction.** By the tops proof's Corollary 3, the top image of
   every tie is a bijection.
   - So no such algebra exists, and A is Taylor by the Taylor criterion.
   - The dichotomy theorem then gives polynomial time for Γ⁺. Γ's problems are
     among Γ⁺'s.
4. **Trivial tops.** The rectangularity proof's Theorem 3 gives F with
   F(a,b,b) and a, and F(a,a,b) and b, in one top class of ⟨a, b⟩. When all
   tops are equality, F is a Mal'tsev polymorphism. ∎

**NP-hard laws fail elimination** (the checks build each system).
- **One-in-three.** R(x, e, h₁) ∧ R(z, e, h₂), with h₁ and h₂ hidden, has
  ties {x, e} and {z, e}, but {x, z} is free.
- **Not-all-equal.** Two copies sharing two variables fail at the shared
  selector, as in the converse proof's Lemma 2.
- **3-colouring.** x ≠ e ∧ e ≠ z: the ties {x, e} and {e, z} leave {x, z}
  free.

This is the contrapositive of Proposition 2's mechanism. These laws have
non-bijective ties already, without constants.

## Proposition 3 (counting is not covered)

The lifted Z₃ law and K₄ compose like cycles (census
`CYCLE-TOPS-20261021-001A-E001`), but their counting problems are #P-complete.

*Proof.* Let M(x, y) be the number of z with (x, y, z) in the relation.
- **The lifted law.** Its rows over x = 0, 1, 2, 3 are [1,2,1,1], [2,1,1,1],
  [1,1,2,2] and [1,1,2,2].
- **One block of rank two or more.** M is positive everywhere, so it forms a
  single block. The first two rows are not proportional, so the block's rank
  is above one.
- **K₄.** The same holds, with one entry lowered.
- **The conclusion.** The relations are not balanced, so the languages are not
  strongly balanced. By Dyer and Richerby, counting is #P-complete. ∎

**What it means.**
- **Top classes are uniform; values are not.** Composing like cycles makes the
  number of top-class completions uniform (the rectangularity proof's
  Lemma 1). The number of value completions is not, since classes have
  different sizes.
- **Contrast.** The Z₃ law itself has M constant, of rank one.

## Proposition 4 (constants can destroy composing like cycles)

Parity beside J and K₄ compose like cycles, but neither does once constants
are added.

*The systems.* The checks verify both by brute force.
- **Parity beside J.** Take J(x₀, x₁) ∧ J(x₂, x₀) ∧ (x₁ = 3) ∧ J(x₀, x₃), and
  show x₀, x₂ and x₃.
  - The allowed triples are 333, 334, 343, 344 and 433.
  - {x₀, x₂} and {x₀, x₃} are ties, both "not both 4", but {x₂, x₃} is free.
  - Inside the top class {3, 4} of the range {2, 3, 4}, pinning a value
    exposes a non-bijective relation.
- **K₄.** Take K₄(x₀, x₁, x₁) ∧ K₄(x₁, x₂, x₃) ∧ K₄(x₃, x₃, x₁) ∧ (x₂ = 2).
  This has ties {x₀, x₁} and {x₁, x₃}, both "not both 2" on the class {2, 3},
  while {x₀, x₃} is free.

**Sampling,** with constants in about a quarter of the atoms, finds failures
in K₄ and in parity beside J. It finds none in Z₃, parity and the full lift,
which keep x − y + z with constants.

**What it means.**
- **The top hides structure.** It hides structure inside its classes, and
  pinning values reveals it.
- **Proposition 2's hypothesis is strictly stronger** than composing like
  cycles.
- **The general question is open.** Does every law that composes like cycles
  have a polynomial-time constraint problem? The census laws do, for simple
  reasons: they contain a constant tuple, or their cores are affine. A proof
  would have to pass through cores rather than constants.

## What this does not show

- **General tractability.** Proposition 2 needs the law with constants to
  compose like cycles.
- **Counting at the level of tops.** Only the negative statement is proved.
- **The p-entropic question,** for primes p ≥ 5, is not addressed beyond the
  reformulation.
- **No claim about P versus NP.**
- **No protected structure.** No native recurrence, composed topology in the
  protected sense, path or distance is claimed.

## Checks

`check.py` writes `result.json` in about a second. All checks pass, and all
controls are rejected.

- **Proposition 1.**
  - The code is rebuilt from the matrix: 729 codewords, almost affine, the
    non-Pappus matroid.
  - The code alone satisfies elimination.
  - It has exactly three unary polymorphisms.
  - The one-copy system defines x − y ∈ ⟨(1,2)⟩, which has 27 pairs.
  - The failing system has 6,561 tuples, five circuits and two failures.
  - 171 sets change status modulo θ.
- **Proposition 2.**
  - One-in-three, not-all-equal and 3-colouring each give a failing system.
  - x − y + z preserves Z₃, parity and the GF(4) law with all constants
    added.
- **Proposition 3.** The counting matrices of the lifted law and K₄ are
  positive with two non-proportional rows. Z₃'s is constant.
- **Proposition 4.** Both explicit systems fail elimination. Over 150 sampled
  nontrivial systems per law, there are failures for parity beside J (3) and
  K₄ (1), and none for Z₃, parity and the full lift.
- **Controls,** each rejected:
  - "uniform fibres of one code force a law composing like cycles" (the
    non-Pappus code);
  - "composing like cycles makes counting tractable" (the lifted law);
  - "every law with a polynomial-time constraint problem composes like
    cycles" (x ≤ y);
  - "some NP-hard law composes like cycles" (the three hardness laws);
  - "adding constants preserves composing like cycles" (parity beside J, and
    K₄).
