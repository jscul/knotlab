# Lane B: approximate counting (Rowell's part (a))

Ticket `NEXT-DIRECTION-SCAN-20261026-001B`, 2026-10-26. A bounded scouting pass (documentation, no theorem activated). The
scouting agent's harness refused to write this file, so the top-level task wrote it from the agent's final report and reran
its seven scripts in a temporary mirror of the repository (see "Replay" below).

## Question

For the solvable groups already shown exactly #P-hard on knots (UT₃(F₄) ⋊ C₃; H(F_p) ⋊ C_r with a hard pair; S₄), are the
reductions approximation-preserving from a #BIS-hard problem? If not, is there a precise obstruction, or evidence for an
FPRAS (Rowell's Conjecture 3.2(a))?

## Findings

Labels: **[proved]** with an argument; **[computed]** by the scripts here; **[literature]**; **[inference]**.

1. **UT₃(F₄) ⋊ C₃: #BIS ≤_AP H_K(G)** [proved, given `TRIPLE-PRODUCT-20261026-001A` Thm. 1(c,d), `…001D` Lemma 6 and
   Construction 7 (reissued as `CORRECTIONS-20261026-001A/D`), and Goldberg–Jerrum Thm. 1].
   - |Hom(π₁ S³₃(K_Γ), G)| = 1 + 128·4^(4m)·Z_Γ(64, 15), and the knot group adds 63.
   - The Frobenius automorphism makes the ψ and ψ² sectors equal, so no sector is left unsteered.
   - One query (δ = ε/2), then subtracting the known constant, is an AP-reduction from Tutte(64, 15) on arbitrary
     multigraphs. The same holds for closed manifolds with H₁ = Z/3.
   - [computed] On the end-to-end knots, N(ψ) = N(ψ²) = 326656 and 45162496; |Hom| divided by the steered term is
     1 + 5.8e−12 and 1 + 7e−16.
2. **Heisenberg groups.**
   - [proved] The recipe as written (`COPRIME-CLASS2-20261026-001D` §3, pure leaves) is exact but not approximation-preserving.
     For a hard pair the ψ⁻¹ sector is never a permutation of (α, β, γ), so pure leaves leave it at its maximum (c₋₁ = c₁,
     and the dimensions agree by duality). Hence |Hom|/(steered term) ≥ 1 + (Q(1 + v)/(Q + v))^(rank Γ).
   - [computed] Had the leaves been pure, that ratio would be 301.2 (p = 7 digon) and 76.3 (p = 5 triangles).
   - [computed] D's own computed knots (bundle leaves found by search) already steer ψ and ψ⁻¹ identically: equal kernel
     counts, identical leaf ranks, 0 steering-law mismatches in sector −1; the ratio is 2.000000 (r = 3) and 2.00001 (r = 4).
   - [sketch] Two-sided leaves (unprojected twist-knot loops nonzero on both W_ζ and W_ζ⁻¹, balanced bands, per-vertex
     rescaling) would give |Hom| = 1 + 2c₁𝒩_gadget + (an exact, negligible term) for r ∈ {3, 4}, hence #BIS ≤_AP. General r:
     open.
3. **The hardness theorems apply** [computed]. Every Potts point produced has Q > 2 (64, p³, p², 12), so Goldberg–Jerrum
   applies to the UT₃ and Heisenberg reductions, which accept arbitrary graphs. Galanis–Štefankovič–Vigoda–Yang Thm. 2 also
   applies on bipartite graphs of maximum degree Δ ≥ 4 (UT₃: B = 16 > B_o(64, 4) = 8.94; patterns 1 and 3) or Δ ≥ 5
   (patterns 2 and 4).
4. **S₄ (also GL(2,3), 2O): no verdict, but a precise obstruction.**
   - Links: the restricted count is exactly 2⁻ⁿ4ᵐ Z(G; 12, 1/2), but G is planar, and no #BIS-hardness of planar ferromagnetic
     Potts was found [literature].
   - Knots: the reduction interpolates, so it is not approximation-preserving. On the hardness family |Hom| = 4 + R + 2T with
     R = 2·4^N [proved; brute force on 3₁ and the granny knot]; R/T ≤ 0.45, falling to about 1e−6 [computed], so |Hom| ≡_AP T
     there.
   - [proved; checked to 10 edges, 744 classes] Every tripled series-parallel gadget has interaction R + xI + yN with
     x ≥ 1 ≥ |y|: equal states are never penalized, so planar colouring hardness (Guo–Zhang, q ≥ 4) cannot enter through these
     gadgets.
   - Closed manifolds with H₁ = Z/2: 3C₂(K) + C₂(K#3₁) = 16 + 12T has only positive terms, so T ≤_AP C₂, and the closed
     counts inherit T's open status.
5. **Kernel-count gadgets are ferromagnetic** [proved; computed on random B]. w(u) = #{P : B(u, P) = 0} has Fourier transform
   Σ_P |K_P| [ξ ⊥ K_P] ≥ 0, so the induced interactions are positive semidefinite. [inference] The cohomological route can give
   only #BIS-type evidence, never NP-hardness of approximation.
6. **Non-solvable groups** [inference from Kuperberg–Samperton 2021 Thm. 1.1 and Cor. 1.2; they do not state it; not verified
   here]. For A₅, whose 3-cycle class is the unique largest, their knots would have |Hom(π_K, A₅)| = 60 + 120·#Q with deciding
   #Q > 0 NP-complete, so part (a) would fail for A₅ unless NP = RP.
7. **Controls** [computed]. Ising (Q = 2) lies outside Goldberg–Jerrum and GSVY and has an FPRAS (Jerrum–Sinclair); no
   reduction here reaches Q = 2. Nilpotent targets: |Hom(π_K, G)| = |G| for H(F₃), H(F₅) and UT₃(F₄) on 3₁, 4₁, 5₂ and
   3₁ # 3₁; the knot-group trivial sector is p³ in every Heisenberg run.

**Not claimed.** #BIS-hardness is evidence, not proof, that no FPRAS exists. There is no NP-hardness of approximation for any
solvable G, and nothing about P versus NP.

## Evidence

`heis_sectors`, `heis_inverse_sector`, `potts_points`, `s4_knots`, `ut3_and_controls`, `ferro_check` and `s4_gadget_region`
(`.py`, `.json`, `.log`) in this directory. Standard library only (they import `tp_lib.py` and `cp_lib.py` read-only); each
runs in under three minutes. The proof sketches for findings 2, 4 and 5 are in the docstrings of `potts_points.py`,
`s4_gadget_region.py` and `ferro_check.py`.

## Replay

The top-level task copied the seven scripts into a temporary mirror of the repository (the proof libraries linked read-only)
and reran them: all exit 0 (heis_sectors 173 s, heis_inverse_sector 84 s, ut3_and_controls 11 s, the others under 3 s), and
every regenerated `.json` equals the lane's file once timing fields are removed.

## Literature

- Goldberg–Jerrum, J. ACM 2012, [arXiv:1002.0986](https://arxiv.org/abs/1002.0986): "Theorem 1. Suppose that q > 2 and γ > 0
  are efficiently approximable. Then #BIS ≤AP Tutte(q, γ)."
- Galanis–Štefankovič–Vigoda–Yang, SICOMP 2016, [arXiv:1311.4839](https://arxiv.org/abs/1311.4839), Thm. 2: "For all q ≥ 3,
  all ∆ ≥ 3 … for any B > Bo, #BIS ≤AP #BipFerroPotts(q, B, ∆)", with B_o = (q − 2)/((q − 1)^(1−2/Δ) − 1).
- Goldberg–Jerrum on planar graphs, [arXiv:0907.1724](https://arxiv.org/abs/0907.1724): the ferromagnetic region is not
  covered.
- Guo–Zhang, [arXiv:2608.06172](https://arxiv.org/abs/2608.06172) (August 2026, unrefereed): "for any constant q ≥ 4,
  approximately counting q-colourings in planar graphs is NP-hard."
- Rowell, [arXiv:0803.1258](https://arxiv.org/abs/0803.1258) §3.3.5: an FPRAS "is widely believed" to exist.
- Rowell–Wang, [arXiv:1705.06206](https://arxiv.org/abs/1705.06206): weakly integral categories are suggested to give link
  invariants approximable in polynomial time.
- Krovi–Russell, [arXiv:1210.1550](https://arxiv.org/abs/1210.1550): multiplicative approximation of A_m-coloured plat
  closures is SBP-complete (Thm. 4); their classical algorithm is additive only.
- Kuperberg–Samperton, [arXiv:1707.03811](https://arxiv.org/abs/1707.03811) and [arXiv:1907.05981](https://arxiv.org/abs/1907.05981).
- Nothing was found on approximate counting for solvable targets.

## Gaps

- Heisenberg groups need the two-sided rewrite and a sector analysis for general r.
- S₄ is planar, and its gadget region is ferromagnetic in the equal-state channel.
- Upper bounds (≤_AP #BIS) are open, even for Potts.

## Cheapest next discriminator: an S₄ tangle scan (at most a day)

- Compute the colouring tensors of knot-preserving 2-tangles outside the tripled series-parallel class (1- and 2-crossing
  twists, rational tangles, up to about 8 crossings).
- **Gate.** One tangle that suppresses equal states (outside x ≥ 1 ≥ |y|) would open an AP-reduction from planar
  q-colourings (Guo–Zhang) or from planar antiferromagnetic 3-state Potts, and part (a) would fail for S₄ unless NP = RP. If
  no such tangle exists within the bound, stop.

## Assessment

- **Interest: 1/3 (Exploratory)** as a standalone epic. The main result (finding 1) is already a corollary. The main
  uncertainty is whether S₄ tangles outside the series-parallel class escape the ferromagnetic region; if they do, this
  becomes Hot.
- **Recommendation: against a standalone epic.** Fold finding 1 into the Rowell note (done: Proposition "approximation is
  #BIS-hard" for UT₃(F₄) ⋊ C₃), note finding 2's obstruction, keep finding 6 flagged as an inference, and keep the S₄ tangle
  scan as an optional bounded ticket.
