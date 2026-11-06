# Lane A: hardness for general coprime class-2 groups

Ticket `NEXT-DIRECTION-SCAN-20261026-001A`, 2026-10-26. A bounded scouting pass (documentation, no theorem activated). The
scouting agent's harness refused to write this file, so the top-level task wrote it from the agent's final report and reran
its five scripts in a temporary mirror of the repository (see "Replay").

## Question

Is counting maps π₁(M) → G #P-hard with bounded first homology for every group of class (K) with a hard pair, not only for
the Heisenberg groups of `COPRIME-CLASS2-20261026-001D`? Sub-questions:
1. the Bulatov–Grohe route;
2. several commutator components on one character triple;
3. the diagonal (Bockstein) terms at p = 2;
4. extension fields.

## Findings

Labels: **[proved]** with an argument in the scripts' docstrings; **[computed]**; **[sketch]**; **[literature]**.

1. **One tensor carries every component** [proved; computed].
   - Put U_s = B_s ⊕ A*_{s⁻¹}, so that each eigenspace carries its cocycle part and its test part together.
   - Φ(b + φ, b′ + φ′, b″ + φ″) = φ″κ(b, b′) + φκ(b′, b″) + φ′κ(b″, b) is an alternating, C_r-invariant 3-form on B ⊕ A*.
   - The count over ψ is p^(−#tests) Σ e_p(T contracted with Φ).
   - A hard pair exists exactly when Φ is nonzero on three nontrivial characters.
2. **The count is a Bulatov–Grohe partition function** [proved; computed].
   - Gadgets: distinct characters use the diagonal Σ_e (x_u − x_v) ⊗ y_e ⊗ t_e; the multiset {s, s, s⁻²} uses D's pattern-2
     gadget; {s, s, s} uses D's alternating 3-form.
   - Then N_ψ = λⁿ μᵐ Σ_{X : V(Γ) → U_{s₁}} Π_e w(X_u − X_v), with w(δ) = |U₃| p^(dim U₂ − rank K(δ)) and K the restriction of
     Φ to the triple.
   - The matrix W[x, y] = w(x − y) is positive, and it has rank one exactly when K = 0.
   - Checked on 199 cases over 15 groups and every ψ_k: full enumeration (up to p¹⁰ cocycles) equals this form, and a hard pair
     occurs exactly when some block is not of rank one. It reproduces D's 46101601, 3240625 and 25925 (positive control); with
     αβ = 1 or a trivial-character slot every block has rank one (negative controls).
3. **Hardness for p odd and r | p − 1** [sketch]. Hard pairs force p ≥ 5.
   - D's twist-knot bases and pure-leaf construction do not depend on G.
   - |Hom| = Σ_k C_k Z_k(Γ), a sum of block partition functions with vertex weights. For connected Γ this is the partition
     function of a block-diagonal matrix, so the sectors need not be isolated one by one: when the hard blocks share C_k,
     Goldberg–Grohe–Jerrum–Thurley Lemma 6.4 applies directly, and Bulatov–Grohe gives #P-hardness.
   - With `COPRIME-CLASS2-20261026-001C` this would be the dichotomy for class (K) with F_p-rational characters, already on
     r-surgeries of knots.
4. **Components mix, harmlessly** [computed]. Pure leaves isolate a character multiset, not one component.
   - On D's pattern-2 knot, the group mix(5) ([e₁, e₂] → A_{ζ²}, [e₁, f] → A_{ζ³}, |G| = 12500) gives 22578125, the
     Bulatov–Grohe value for a three-level weight (3125/625/125) that is not a Potts weight. Isolating each component would give
     84013203125 instead.
   - On B's pattern-1 knots (p = 7, r = 6), the free class-2 group on three generators gives 938791 and 49735 from actual cup
     products, equal to the counts predicted from the steered tensor.
   - D's patterns 2 and 4 are one case: the same knot gives both 3240625 and 25925.
5. **p = 2 diagonals** [invariance proved; criterion sketched; computed].
   - In characteristic 2 Borromean moves add forms with zero diagonal, so a ↦ T(a, a, ·) is invariant under them.
   - That map is a Frobenius-twisted Teichmüller Bockstein; for a cyclic module it vanishes exactly when Δ_K(χ̃) ≡ 0 mod 4.
   - At q = 4 this holds in all 23 one-dimensional cases: the diagonal is zero for 4₁, 7₂ and T(3, 4), and for twist knots K_m
     exactly when m ≡ 1 mod 4.
   - With zero diagonal the squaring map does not matter: UT₃(F₄), an isomorphic control and an anisotropic-squaring group all
     give 5056 = Z(64, 15) on K₂. With a diagonal term the counts differ (2212 against 316).
   - Mod 2, twist knots only see cube roots of unity, so r ≥ 5 needs knots with Δ ≡ Φ_r mod 4 (Seifert's construction).
6. **Extension fields** [sketch]. F_p-rational leaves live on whole Frobenius orbits. When the orbits line up, the weights
   become p^(d − rank_{F_p}(Tr ∘ K(δ))), still nonconstant exactly when K ≠ 0. A hand computation at p = 3, r = 4 gives
   Potts(81, 2), or Potts(81, 8) for the full H(F₉).

## Evidence

In this directory, each with a `*_result.json` and most with a `.log`; all checks report ok:
- `bg_route.py`: the algebraic layer (numpy).
- `knot_mixing.py`: D's pattern-2 knot with a mixed group.
- `knot_pattern1.py`: B's pattern-1 knots.
- `bockstein_q4.py`: the q = 4 diagonal criterion (sympy).
- `gf4_check.py`: the squaring-map check (standard library).

## Replay

The top-level task copied the five scripts into a temporary mirror of the repository (proof libraries linked read-only) and
reran them with the workspace's `.venv` Python: all exit 0 (bg_route 23 s, knot_pattern1 15 s, knot_mixing 11 s, the others
2 s), and every regenerated `*_result.json` equals the lane's file once timing fields are removed.

## Literature

- Bulatov–Grohe, Theoret. Comput. Sci. 348 (2005), [report](https://cs.ox.ac.uk/techreports/oucl/rr-04-04.html): "the problem
  is in polynomial time if the adjacency matrix of H has row rank 1, and #P-complete otherwise".
- Goldberg–Grohe–Jerrum–Thurley, [arXiv:0804.1932](https://arxiv.org/abs/0804.1932), Lemma 6.4: "If abs(A) contains a block of
  row rank at least 2 then EVAL(A, D, O) is #P-hard"; it needs D non-singular with non-negative integer entries, and input
  graphs may have loops and multiple edges.
- Seifert (1935), as quoted by Kammeyer, [arXiv:1607.03824](https://arxiv.org/abs/1607.03824): "the Alexander module of
  Seifert's K^∆ is actually cyclic".
- Two searches found no earlier result. Folklore risk is high for finding 1 and medium for finding 3.

## Gaps

1. The ψ_k isolation step and the size bookkeeping are not written out.
2. No end-to-end pattern-1 gadget knot has been built.
3. Knot groups are not covered when some κ_{1,σ} ≠ 0, because then H¹(X; F_p) couples V_σ with V_{σ⁻¹}.
4. For p = 2 and r ≥ 5, explicit zero-diagonal knots are still needed, with T₀ = 0 on the triples where Φ is nonzero.
5. Frobenius-stable triples such as {χ, χ^p, χ^{p²}} are not analysed.
6. The diagonal criterion must be applied per cyclic summand; applied to the whole module it fails for 8₁₈ and 3₁ # 4₁.

## Cheapest next discriminator (about a day)

Build the projector construction of `COPRIME-CLASS2-20261026-001D` §3 for pattern 1 (p = 7, r = 6) on K₂ and on the digon,
and count maps to the free class-2 group on three generators. The predicted N_ψ are 133 and 2737; a mismatch would show that
pattern 1 cannot be realized this way.

## Assessment

- **Interest: 2/3 (Promising).** The hard-pair criterion does not change; the gain is that it would hold for a class of
  groups instead of a family, with Bulatov–Grohe replacing the Potts gadgets.
- **Recommendation: for, bounded.** Prove the p-odd, prime-field dichotomy for class (K) (optionally with q = 4, r = 3),
  as a short epic gated on the discriminator above. Against pursuing p = 2 with r ≥ 5, or Frobenius-stable triples, now.
