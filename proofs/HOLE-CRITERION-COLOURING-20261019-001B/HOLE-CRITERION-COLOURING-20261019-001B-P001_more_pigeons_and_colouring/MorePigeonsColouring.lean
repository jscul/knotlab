/-
Braun's bound for more pigeons, and bit-colouring through a proper colouring
(ticket HOLE-CRITERION-COLOURING-20261019-001B).

Checked against Braun's formal development (GitHub repository math-research of
the account kbr-) at commit 8904bf09, whose replay and definitions were
audited in BPHP-RES-PARITY-AUDIT-20261019-001.

* `bitPHP_more_pigeons`: every refutation of the usual bit-PHP clause set with
  m pigeons and 2^ℓ holes has more than exp(4^ℓ/(8192 m ℓ²)) lines, for every
  m from 2^ℓ+1 up to about 4^ℓ/(16384 ℓ³). Braun's final calibration fixes
  m = 2^ℓ+1; the lemmas it calls take the number of pigeons as a parameter.
* `colouring_refutation_transfer`: a refutation of the bit encoding of
  2^ℓ-colouring a graph maps, line by line, to a refutation of bit-PHP with one
  pigeon per class of any proper colouring of the graph.
* `bitColouring_more_pigeons`: the two together.
* Witnesses against vacuity: the range of m is nonempty, both clause sets
  say what they should, and the complete graph gives bit-PHP itself.
-/
import claims.BitPHPExponential

namespace MorePigeonsColouring
noncomputable section
open MathResearch MathResearch.PolynomialCalculus

-- The same classical decidable equality the author's files use for clause sets.
local instance clauseDecidableEq {ν : Type} : DecidableEq ((ν → ZMod 2) →ᵃ[ZMod 2] ZMod 2) :=
  Classical.decEq _

/-! ## Bit-PHP with more pigeons -/

/-- Every refutation of bit-PHP with `m` pigeons and `2^ℓ` holes is long, for every `m` in the range. -/
theorem bitPHP_more_pigeons : ∀ ℓ ≥ 32, ∀ m : ℕ, 2^ℓ + 1 ≤ m → 8192*m*ℓ^2*(2*ℓ+5) ≤ (2^ℓ)^2 →
    ∀ {S : ℕ} (C : Fin S → FiniteParityClause (BitVar m ℓ))
    (_dag : AffineDAG (usualBitPHPInitials m ℓ) C) (finish : Fin S), C finish = ∅ →
    Real.exp ((((2^ℓ:ℕ):ℝ))^2/(8192*(m:ℝ)*(ℓ:ℝ)^2)) < (S:ℝ) := by
  intro ℓ hℓ m hm hroom S C dag finish hempty
  classical
  by_contra hnot
  let n : ℕ := 2^ℓ
  let x : ℝ := ((n:ℕ):ℝ)^2/(8192*(m:ℝ)*(ℓ:ℝ)^2)
  have hS : (S:ℝ) ≤ Real.exp x := le_of_not_gt hnot
  have hn1 : 1 ≤ n := Nat.one_le_two_pow
  have hnm : n + 1 ≤ m := hm
  have hm0 : 0 < m := by omega
  have hroom' : 32768*((2*ℓ+4)*ℓ^2) ≤ n := bitPHP_exponential_room ℓ hℓ
  have hℓℓ : 32*ℓ ≤ ℓ*ℓ := Nat.mul_le_mul_right _ hℓ
  have h64 : 64*ℓ ≤ n := by nlinarith
  -- Real-number bookkeeping.
  have hℓR : (32:ℝ) ≤ (ℓ:ℝ) := by exact_mod_cast hℓ
  have hnR : (1:ℝ) ≤ (n:ℝ) := by exact_mod_cast hn1
  have hmR : (1:ℝ) ≤ (m:ℝ) := by exact_mod_cast hm0
  have hden : (0:ℝ) < 8192*(m:ℝ)*(ℓ:ℝ)^2 := by positivity
  have hxmul : x*(8192*(m:ℝ)*(ℓ:ℝ)^2) = (n:ℝ)^2 := div_mul_cancel₀ _ hden.ne'
  have hroomR : (8192:ℝ)*(m:ℝ)*(ℓ:ℝ)^2*(2*(ℓ:ℝ)+5) ≤ (n:ℝ)^2 := by exact_mod_cast hroom
  have hx : 2*(ℓ:ℝ)+5 ≤ x := by
    rw [le_div_iff₀ hden]
    nlinarith
  have hx0 : 0 ≤ x := by linarith
  -- exp x ≥ 32 n².
  have he2 : (2:ℝ) ≤ Real.exp 1 := by
    have h := Real.add_one_le_exp (1:ℝ)
    linarith
  have hncast : (n:ℝ) = (2:ℝ)^ℓ := by
    simp only [n]
    push_cast
    ring
  have hexp : 32*(n:ℝ)^2 ≤ Real.exp x := by
    have hmono : Real.exp (((2*ℓ+5:ℕ):ℝ)) ≤ Real.exp x := by
      apply Real.exp_le_exp.mpr
      push_cast
      exact hx
    have hpow : (2:ℝ)^(2*ℓ+5) ≤ Real.exp 1^(2*ℓ+5) :=
      pow_le_pow_left₀ (by norm_num) he2 _
    rw [Real.exp_one_pow] at hpow
    have hring : (2:ℝ)^(2*ℓ+5) = 32*((2:ℝ)^ℓ)^2 := by ring
    rw [hncast, ← hring]
    exact hpow.trans hmono
  -- The number of pigeons is at most n².
  have hmn2 : m ≤ n^2 := by
    have h1 : 1 ≤ 8192*ℓ^2*(2*ℓ+5) := Nat.one_le_iff_ne_zero.mpr (by positivity)
    calc m = m*1 := (mul_one m).symm
      _ ≤ m*(8192*ℓ^2*(2*ℓ+5)) := Nat.mul_le_mul_left _ h1
      _ = 8192*m*ℓ^2*(2*ℓ+5) := by ring
      _ ≤ n^2 := hroom
  have hmn2R : (m:ℝ) ≤ (n:ℝ)^2 := by exact_mod_cast hmn2
  -- Inventory.
  let M : ℕ := 3*S + m.choose 2
  have hchoose : m.choose 2 ≤ m^2 := Nat.choose_le_pow m 2
  have hM : 1 ≤ M := by
    have h : 0 < m.choose 2 := Nat.choose_pos (by omega)
    omega
  have hMR : (M:ℝ) ≤ 3*Real.exp x + (m:ℝ)^2 := by
    have hc : ((m.choose 2:ℕ):ℝ) ≤ (m:ℝ)^2 := by exact_mod_cast hchoose
    simp only [M]
    push_cast
    linarith
  have hMpos : (0:ℝ) < 4*(M:ℝ) := by
    have : (1:ℝ) ≤ (M:ℝ) := by exact_mod_cast hM
    linarith
  have h4M : 4*(M:ℝ) ≤ Real.exp (2*x) := by
    rw [two_mul, Real.exp_add]
    have hn2 : (1:ℝ) ≤ (n:ℝ)^2 := one_le_pow₀ hnR
    have hm4 : (m:ℝ)^2 ≤ ((n:ℝ)^2)^2 := pow_le_pow_left₀ (by linarith) hmn2R 2
    nlinarith
  have hlog : Real.log (4*(M:ℝ)) ≤ 2*x := (Real.log_le_iff_le_exp hMpos).mpr h4M
  -- The kernel degree k = ⌊n/(32ℓ)⌋, as in Braun's calibration.
  let k : ℕ := n/(32*ℓ)
  have hqpos : 0 < 32*ℓ := by omega
  have hkmul : k*(32*ℓ) ≤ n := Nat.div_mul_le_self n (32*ℓ)
  have hkpos : 1 ≤ k := Nat.div_pos (by omega) hqpos
  have hkn : k ≤ n := Nat.div_le_self n (32*ℓ)
  have hkm : k ≤ m := by omega
  have hklt : n < (k+1)*(32*ℓ) := by
    have h1 := Nat.div_add_mod n (32*ℓ)
    have h2 := Nat.mod_lt n hqpos
    have h3 : (32*ℓ)*(n/(32*ℓ)) = k*(32*ℓ) := Nat.mul_comm _ _
    nlinarith
  have hnk : n ≤ 64*ℓ*k := by nlinarith
  have hnkR : (n:ℝ) ≤ 64*(ℓ:ℝ)*(k:ℝ) := by exact_mod_cast hnk
  have hsq : ((m:ℕ):ℝ)*Real.log (4*(M:ℝ)) ≤ (k:ℝ)^2 := by
    have hm0R : (0:ℝ) ≤ (m:ℝ) := Nat.cast_nonneg _
    have hstep : (m:ℝ)*Real.log (4*(M:ℝ)) ≤ (m:ℝ)*(2*x) := mul_le_mul_of_nonneg_left hlog hm0R
    have hmx : ((m:ℝ)*(2*x))*(4096*(ℓ:ℝ)^2) = (n:ℝ)^2 := by
      have : ((m:ℝ)*(2*x))*(4096*(ℓ:ℝ)^2) = x*(8192*(m:ℝ)*(ℓ:ℝ)^2) := by ring
      rw [this, hxmul]
    have hden2 : (0:ℝ) < 4096*(ℓ:ℝ)^2 := by positivity
    have hfin : (m:ℝ)*(2*x) ≤ (k:ℝ)^2 := by
      have hscaled : ((m:ℝ)*(2*x))*(4096*(ℓ:ℝ)^2) ≤ (k:ℝ)^2*(4096*(ℓ:ℝ)^2) := by
        rw [hmx]
        nlinarith [sq_nonneg ((ℓ:ℝ)*(k:ℝ))]
      exact le_of_mul_le_mul_right hscaled hden2
    exact hstep.trans hfin
  have hpack : 4*(k-1) < n := by
    have : 32*k ≤ n := by nlinarith
    omega
  have hB : 2*(k*((12*ℓ+1)+1))-1 ≤ n := by
    have : 2*(k*((12*ℓ+1)+1)) ≤ n := by nlinarith
    omega
  -- Transfer and exclusion, exactly as in Braun's proof, with m pigeons.
  obtain ⟨N,R,hN,_,_,_,hpc⟩ := usual_bitPHP_PC_transfer C dag finish hempty (3*ℓ) (by omega)
  let g : ∀ b : Fin N, {f // f ∈ R b} → AffineInputMap (BitVar m ℓ) :=
    fun _ i => i.val
  have hcount : Nat.card (ProperHighIndex g k) ≤ M := by
    apply le_trans ((proper_high_count_le_proper_count g k).trans ?_) hN
    rw [Nat.card_eq_fintype_card]
    calc
      Fintype.card (ProperBlockIndex g) ≤ Fintype.card (Fin N) := Fintype.card_subtype_le _
      _ = N := Fintype.card_fin _
  have hdegree : max (2*(3*ℓ)+ℓ) (4*(3*ℓ)+1) = 12*ℓ+1 := by omega
  rw [hdegree,registry_system_eq_ensFamily] at hpc
  exact affine_family_exclusion_of_square m ℓ M k (12*ℓ+1) hm0 (by omega) hM
    hkpos hkm hsq (by omega) hpack hB g hcount hpc

/-! ## Bit-colouring through a proper colouring -/

/-- A graph on `v` vertices: a symmetric adjacency relation without loops. -/
structure Graph (v : ℕ) where
  Adj : Fin v → Fin v → Prop
  symm : ∀ {u w : Fin v}, Adj u w → Adj w u
  loopless : ∀ u : Fin v, ¬ Adj u u

/-- The complete graph on `m` vertices. -/
def Graph.complete (m : ℕ) : Graph m where
  Adj u w := u ≠ w
  symm h := fun e => h e.symm
  loopless _ h := h rfl

/-- The bit encoding of colouring `G` with the `2^ℓ` labels: for every edge `u < w` and
every label `z`, the clause "`u` and `w` do not both carry `z`". -/
def bitColouringInitials {v : ℕ} (G : Graph v) (ℓ : ℕ) :
    Set (FiniteParityClause (BitVar v ℓ)) :=
  {C | ∃ u w : Fin v, u < w ∧ G.Adj u w ∧ ∃ z : BitLabel ℓ, C = usualCNFClause u w z}

/-- Read an assignment of the pigeon bits as one of the vertex bits: vertex `w` reads
the bits of its class `f w`. -/
def pullAssign {v m ℓ : ℕ} (f : Fin v → Fin m) :
    (BitVar m ℓ → ZMod 2) →ₗ[ZMod 2] (BitVar v ℓ → ZMod 2) where
  toFun y := fun p => y (f p.1, p.2)
  map_add' _ _ := rfl
  map_smul' _ _ := rfl

/-- An affine form in the vertex bits, read through `f`. -/
def pullForm {v m ℓ : ℕ} (f : Fin v → Fin m) (g : (BitVar v ℓ → ZMod 2) →ᵃ[ZMod 2] ZMod 2) :
    (BitVar m ℓ → ZMod 2) →ᵃ[ZMod 2] ZMod 2 :=
  g.comp (pullAssign f).toAffineMap

/-- A linear clause in the vertex bits, read through `f`. -/
def pullClause {v m ℓ : ℕ} (f : Fin v → Fin m) (C : FiniteParityClause (BitVar v ℓ)) :
    FiniteParityClause (BitVar m ℓ) :=
  C.image (pullForm f)

theorem holds_pull {v m ℓ : ℕ} (f : Fin v → Fin m) (C : FiniteParityClause (BitVar v ℓ))
    (y : BitVar m ℓ → ZMod 2) :
    clauseHolds (pullClause f C) y ↔ clauseHolds C (pullAssign f y) := by
  constructor
  · rintro ⟨g', hg', hy⟩
    obtain ⟨g, hg, rfl⟩ := Finset.mem_image.mp hg'
    exact ⟨g, hg, hy⟩
  · rintro ⟨g, hg, hy⟩
    exact ⟨pullForm f g, Finset.mem_image.mpr ⟨g, hg, rfl⟩, hy⟩

theorem pull_label {v m ℓ : ℕ} (f : Fin v → Fin m) (w : Fin v) (z : BitLabel ℓ) (t : Fin ℓ) :
    pullForm f (labelBitLiteral w z t) = labelBitLiteral (f w) z t := by
  ext y
  rfl

theorem pull_usual {v m ℓ : ℕ} (f : Fin v → Fin m) (u w : Fin v) (z : BitLabel ℓ) :
    pullClause f (usualCNFClause u w z) = usualCNFClause (f u) (f w) z := by
  ext g
  simp only [pullClause, usualCNFClause, Finset.mem_image, Finset.mem_union, Finset.mem_univ, true_and]
  constructor
  · rintro ⟨g0, (⟨t, rfl⟩ | ⟨t, rfl⟩), rfl⟩
    · exact Or.inl ⟨t, (pull_label f u z t).symm⟩
    · exact Or.inr ⟨t, (pull_label f w z t).symm⟩
  · rintro (⟨t, rfl⟩ | ⟨t, rfl⟩)
    · exact ⟨labelBitLiteral u z t, Or.inl ⟨t, rfl⟩, pull_label f u z t⟩
    · exact ⟨labelBitLiteral w z t, Or.inr ⟨t, rfl⟩, pull_label f w z t⟩

theorem usual_comm {m ℓ : ℕ} (a b : Fin m) (z : BitLabel ℓ) :
    usualCNFClause a b z = usualCNFClause b a z := by
  unfold usualCNFClause
  exact Finset.union_comm _ _

/-- An edge clause of `G`, read through a proper colouring, is a bit-PHP clause. -/
theorem initial_pull {v m ℓ : ℕ} (G : Graph v) (f : Fin v → Fin m)
    (hf : ∀ u w, G.Adj u w → f u ≠ f w) {C : FiniteParityClause (BitVar v ℓ)}
    (h : C ∈ bitColouringInitials G ℓ) : pullClause f C ∈ usualBitPHPInitials m ℓ := by
  obtain ⟨u, w, -, hadj, z, rfl⟩ := h
  rcases lt_or_gt_of_ne (hf u w hadj) with hlt | hgt
  · exact ⟨f u, f w, hlt, z, pull_usual f u w z⟩
  · exact ⟨f w, f u, hgt, z, (pull_usual f u w z).trans (usual_comm _ _ _)⟩

/-- A proper colouring with `m` classes maps a refutation of the bit-colouring clauses of
`G`, line by line, to a refutation of bit-PHP with `m` pigeons. -/
def transferDAG {v m ℓ S : ℕ} (G : Graph v) (f : Fin v → Fin m)
    (hf : ∀ u w, G.Adj u w → f u ≠ f w) {C : Fin S → FiniteParityClause (BitVar v ℓ)}
    (dag : AffineDAG (bitColouringInitials G ℓ) C) :
    AffineDAG (usualBitPHPInitials m ℓ) (fun i => pullClause f (C i)) where
  step i :=
    match dag.step i with
    | .initial h => .initial (initial_pull G f hf h)
    | .weaken a ha he => .weaken a ha (fun y hy =>
        (holds_pull f _ y).mpr (he _ ((holds_pull f _ y).mp hy)))
    | .resolve a b A B u ha hb hA hB hC => .binary a b ha hb (fun y h1 h2 => by
        rw [holds_pull] at h1 h2 ⊢
        obtain ⟨g, hg, hgx⟩ := h1
        obtain ⟨g', hg', hgx'⟩ := h2
        rw [hA, Finset.mem_insert] at hg
        rw [hB, Finset.mem_insert] at hg'
        rw [hC]
        rcases hg with rfl | hg
        · rcases hg' with rfl | hg'
          · simp [oppositeParity_apply, hgx] at hgx'
          · exact ⟨g', Finset.mem_union_right _ hg', hgx'⟩
        · exact ⟨g, Finset.mem_union_left _ hg, hgx⟩)
    | .binary a b ha hb hs => .binary a b ha hb (fun y h1 h2 =>
        (holds_pull f _ y).mpr (hs _ ((holds_pull f _ y).mp h1) ((holds_pull f _ y).mp h2)))

/-- The transfer keeps the number of lines and the empty final line. -/
theorem colouring_refutation_transfer {v m ℓ S : ℕ} (G : Graph v) (f : Fin v → Fin m)
    (hf : ∀ u w, G.Adj u w → f u ≠ f w) (C : Fin S → FiniteParityClause (BitVar v ℓ))
    (_dag : AffineDAG (bitColouringInitials G ℓ) C) (finish : Fin S) (hempty : C finish = ∅) :
    ∃ (C' : Fin S → FiniteParityClause (BitVar m ℓ)) (_ : AffineDAG (usualBitPHPInitials m ℓ) C'),
      C' finish = ∅ :=
  ⟨fun i => pullClause f (C i), transferDAG G f hf _dag, by simp [pullClause, hempty]⟩

/-- Every refutation of the bit encoding of `2^ℓ`-colouring `G` is long, whenever `G` has a
proper colouring with a number of classes `m` in the range of `bitPHP_more_pigeons`. -/
theorem bitColouring_more_pigeons : ∀ ℓ ≥ 32, ∀ {v : ℕ} (G : Graph v) (m : ℕ)
    (f : Fin v → Fin m), (∀ u w, G.Adj u w → f u ≠ f w) →
    2^ℓ + 1 ≤ m → 8192*m*ℓ^2*(2*ℓ+5) ≤ (2^ℓ)^2 →
    ∀ {S : ℕ} (C : Fin S → FiniteParityClause (BitVar v ℓ))
    (_dag : AffineDAG (bitColouringInitials G ℓ) C) (finish : Fin S), C finish = ∅ →
    Real.exp ((((2^ℓ:ℕ):ℝ))^2/(8192*(m:ℝ)*(ℓ:ℝ)^2)) < (S:ℝ) := by
  intro ℓ hℓ v G m f hf hm hroom S C dag finish hempty
  obtain ⟨C', dag', hempty'⟩ := colouring_refutation_transfer G f hf C dag finish hempty
  exact bitPHP_more_pigeons ℓ hℓ m hm hroom C' dag' finish hempty'

/-! ## Witnesses against vacuity -/

/-- The range of `m` is nonempty: it contains `2^32+1` at `ℓ = 32`. -/
theorem range_nonempty : 2^32 + 1 ≤ 2^32 + 1 ∧ 8192*(2^32+1)*32^2*(2*32+5) ≤ (2^32)^2 := by
  norm_num

/-- With more pigeons than labels, some bit-PHP clause is false at every assignment. -/
theorem usualBitPHP_unsat_more (ℓ m : ℕ) (hm : 2^ℓ < m) (x : BitVar m ℓ → ZMod 2) :
    ∃ C ∈ usualBitPHPInitials m ℓ, ¬ clauseHolds C x := by
  classical
  let f : Fin m → BitLabel ℓ := fun i t => x (i, t)
  have hcard : Fintype.card (BitLabel ℓ) < Fintype.card (Fin m) := by
    simpa [BitLabel, ZMod.card] using hm
  obtain ⟨i, i', hne, heq⟩ := Fintype.exists_ne_map_eq_of_card_lt f hcard
  have hrow : ∀ t, x (i', t) = f i t := fun t => by
    have := congrFun heq t
    simp only [f] at this
    simp only [f]
    exact this.symm
  rcases lt_or_gt_of_ne hne with h | h
  · refine ⟨usualCNFClause i i' (f i), ⟨i, i', h, f i, rfl⟩, ?_⟩
    rw [clause_not_holds, usual_CNF_zero_iff]
    exact ⟨fun t => rfl, hrow⟩
  · refine ⟨usualCNFClause i' i (f i), ⟨i', i, h, f i, rfl⟩, ?_⟩
    rw [clause_not_holds, usual_CNF_zero_iff]
    exact ⟨hrow, fun t => rfl⟩

/-- If `G` has no proper colouring with the `2^ℓ` labels, every assignment falsifies some
clause of its bit encoding. -/
theorem bitColouring_unsat {v : ℕ} (G : Graph v) (ℓ : ℕ)
    (hG : ∀ c : Fin v → BitLabel ℓ, ∃ u w, G.Adj u w ∧ c u = c w) (x : BitVar v ℓ → ZMod 2) :
    ∃ C ∈ bitColouringInitials G ℓ, ¬ clauseHolds C x := by
  obtain ⟨u, w, hadj, heq⟩ := hG (fun u t => x (u, t))
  have hrow : ∀ t, x (w, t) = x (u, t) := fun t => (congrFun heq t).symm
  have hne : u ≠ w := fun e => G.loopless u (e ▸ hadj)
  rcases lt_or_gt_of_ne hne with h | h
  · refine ⟨usualCNFClause u w (fun t => x (u, t)), ⟨u, w, h, hadj, _, rfl⟩, ?_⟩
    rw [clause_not_holds, usual_CNF_zero_iff]
    exact ⟨fun t => rfl, hrow⟩
  · refine ⟨usualCNFClause w u (fun t => x (u, t)), ⟨w, u, h, G.symm hadj, _, rfl⟩, ?_⟩
    rw [clause_not_holds, usual_CNF_zero_iff]
    exact ⟨hrow, fun t => rfl⟩

private theorem binary_ne (a b : ZMod 2) (h : a ≠ b) : a + b = 1 := by
  have key : ∀ a b : ZMod 2, a ≠ b → a + b = 1 := by decide
  exact key a b h

/-- A proper colouring with the `2^ℓ` labels satisfies every clause of the bit encoding. -/
theorem bitColouring_sat {v : ℕ} (G : Graph v) (ℓ : ℕ) (c : Fin v → BitLabel ℓ)
    (hc : ∀ u w, G.Adj u w → c u ≠ c w) :
    ∀ C ∈ bitColouringInitials G ℓ, clauseHolds C (fun p => c p.1 p.2) := by
  rintro C ⟨u, w, -, hadj, z, rfl⟩
  by_cases hu : c u = z
  · have hw : c w ≠ z := fun hw => hc u w hadj (hu.trans hw.symm)
    obtain ⟨t, ht⟩ := Function.ne_iff.mp hw
    exact ⟨labelBitLiteral w z t, Finset.mem_union_right _ (Finset.mem_image.mpr ⟨t, Finset.mem_univ _, rfl⟩),
      by simpa using binary_ne _ _ ht⟩
  · obtain ⟨t, ht⟩ := Function.ne_iff.mp hu
    exact ⟨labelBitLiteral u z t, Finset.mem_union_left _ (Finset.mem_image.mpr ⟨t, Finset.mem_univ _, rfl⟩),
      by simpa using binary_ne _ _ ht⟩

/-- The bit encoding of colouring the complete graph on `m` vertices is bit-PHP with `m` pigeons. -/
theorem complete_graph_is_bitPHP (m ℓ : ℕ) :
    bitColouringInitials (Graph.complete m) ℓ = usualBitPHPInitials m ℓ := by
  ext C
  constructor
  · rintro ⟨u, w, h, -, z, rfl⟩
    exact ⟨u, w, h, z, rfl⟩
  · rintro ⟨u, w, h, z, rfl⟩
    exact ⟨u, w, h, h.ne, z, rfl⟩

end
end MorePigeonsColouring
