/-
Witnesses against vacuity for MathResearch.bitPHP_exponential
(audit BPHP-RES-PARITY-AUDIT-20261019-001B).

The main theorem quantifies over every AffineDAG refutation of
usualBitPHPInitials (2^ℓ+1) ℓ. It would hold vacuously if no such refutation
could exist. This file checks, against the author's own definitions, that:

* the formal clause set is unsatisfiable for every ℓ (pigeonhole), so no
  assignment can block a refutation;
* the formal proof system admits an explicit refutation of the smallest
  instance, ℓ = 1 with three pigeons and two holes, built from the usual
  resolution rule and two-premise semantic steps.
-/
import claims.BitPHPExponential

namespace AuditWitnesses
noncomputable section
open MathResearch MathResearch.PolynomialCalculus

-- The same classical decidable equality the author's files use for clause sets.
local instance auditClauseDecidableEq {ν : Type} : DecidableEq ((ν → ZMod 2) →ᵃ[ZMod 2] ZMod 2) :=
  Classical.decEq _

/-- Some usual bit-PHP clause is false at every assignment. -/
theorem usualBitPHP_unsat (ℓ : ℕ) (x : BitVar (2^ℓ+1) ℓ → ZMod 2) :
    ∃ C ∈ usualBitPHPInitials (2^ℓ+1) ℓ, ¬ clauseHolds C x := by
  classical
  let f : Fin (2^ℓ+1) → BitLabel ℓ := fun i t => x (i, t)
  have hcard : Fintype.card (BitLabel ℓ) < Fintype.card (Fin (2^ℓ+1)) := by
    simp [BitLabel, ZMod.card]
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

/-- No assignment satisfies every usual bit-PHP clause. -/
theorem usualBitPHP_no_model (ℓ : ℕ) :
    ¬ ∃ x : BitVar (2^ℓ+1) ℓ → ZMod 2, ∀ C ∈ usualBitPHPInitials (2^ℓ+1) ℓ, clauseHolds C x := by
  rintro ⟨x, hx⟩
  obtain ⟨C, hC, hnot⟩ := usualBitPHP_unsat ℓ x
  exact hnot (hx C hC)

/-! ## An explicit refutation for ℓ = 1: three pigeons, two holes -/

abbrev V := BitVar 3 1

def zero : BitLabel 1 := fun _ => 0
def one : BitLabel 1 := fun _ => 1

theorem holds_usual (i i' : Fin 3) (z : BitLabel 1) (x : V → ZMod 2) :
    clauseHolds (usualCNFClause i i' z) x ↔ (x (i,0) + z 0 = 1 ∨ x (i',0) + z 0 = 1) := by
  classical
  constructor
  · rintro ⟨g, hg, hgx⟩
    rcases Finset.mem_union.mp hg with hg | hg
    · obtain ⟨t, -, rfl⟩ := Finset.mem_image.mp hg
      have ht : t = 0 := Subsingleton.elim t 0
      subst ht
      exact Or.inl (by simpa using hgx)
    · obtain ⟨t, -, rfl⟩ := Finset.mem_image.mp hg
      have ht : t = 0 := Subsingleton.elim t 0
      subst ht
      exact Or.inr (by simpa using hgx)
  · rintro (h | h)
    · exact ⟨labelBitLiteral i z 0,
        Finset.mem_union_left _ (Finset.mem_image.mpr ⟨0, Finset.mem_univ _, rfl⟩), by simpa using h⟩
    · exact ⟨labelBitLiteral i' z 0,
        Finset.mem_union_right _ (Finset.mem_image.mpr ⟨0, Finset.mem_univ _, rfl⟩), by simpa using h⟩

/-- The single-literal clause "pigeons i and i' differ". -/
def differ (i i' : Fin 3) : FiniteParityClause V := insert (pairBitLiteral i i' 0) ∅

/-- The single-literal clause "pigeons 1 and 2 agree". -/
def agree12 : FiniteParityClause V := insert (oppositeParity (pairBitLiteral (1 : Fin 3) 2 0)) ∅

theorem holds_differ (i i' : Fin 3) (x : V → ZMod 2) :
    clauseHolds (differ i i') x ↔ x (i,0) + x (i',0) = 1 := by
  classical
  simp [differ, clauseHolds]

theorem holds_agree12 (x : V → ZMod 2) :
    clauseHolds agree12 x ↔ 1 - (x (1,0) + x (2,0)) = 1 := by
  classical
  simp [agree12, clauseHolds]

/-- Two clauses about one pair imply that the pair differs. -/
theorem merge_sound (i i' : Fin 3) (x : V → ZMod 2) :
    clauseHolds (usualCNFClause i i' zero) x → clauseHolds (usualCNFClause i i' one) x →
      clauseHolds (differ i i') x := by
  rw [holds_usual, holds_usual, holds_differ]
  simp only [zero, one]
  generalize x (i,0) = a
  generalize x (i',0) = b
  fin_cases a <;> fin_cases b <;> decide

theorem agree_sound (x : V → ZMod 2) :
    clauseHolds (differ 0 1) x → clauseHolds (differ 0 2) x → clauseHolds agree12 x := by
  rw [holds_differ, holds_differ, holds_agree12]
  generalize x (0,0) = a
  generalize x (1,0) = b
  generalize x (2,0) = c
  fin_cases a <;> fin_cases b <;> fin_cases c <;> decide

/-- The refutation, line by line. -/
def lines : Fin 11 → FiniteParityClause V :=
  ![usualCNFClause 0 1 zero, usualCNFClause 0 1 one, differ 0 1,
    usualCNFClause 0 2 zero, usualCNFClause 0 2 one, differ 0 2,
    agree12,
    usualCNFClause 1 2 zero, usualCNFClause 1 2 one, differ 1 2,
    ∅]

theorem mem_initials (i i' : Fin 3) (h : i < i') (z : BitLabel 1) :
    usualCNFClause i i' z ∈ usualBitPHPInitials 3 1 := ⟨i, i', h, z, rfl⟩

/-- Each line is an initial clause, a two-premise semantic step, or resolution. -/
def stepAt : (i : Fin 11) → AffineDAGStep (usualBitPHPInitials 3 1) lines i
  | ⟨0, _⟩ => .initial (mem_initials 0 1 (by decide) zero)
  | ⟨1, _⟩ => .initial (mem_initials 0 1 (by decide) one)
  | ⟨2, _⟩ => .binary 0 1 (by simp [Fin.lt_def]) (by simp [Fin.lt_def]) (merge_sound 0 1)
  | ⟨3, _⟩ => .initial (mem_initials 0 2 (by decide) zero)
  | ⟨4, _⟩ => .initial (mem_initials 0 2 (by decide) one)
  | ⟨5, _⟩ => .binary 3 4 (by simp [Fin.lt_def]) (by simp [Fin.lt_def]) (merge_sound 0 2)
  | ⟨6, _⟩ => .binary 2 5 (by simp [Fin.lt_def]) (by simp [Fin.lt_def]) agree_sound
  | ⟨7, _⟩ => .initial (mem_initials 1 2 (by decide) zero)
  | ⟨8, _⟩ => .initial (mem_initials 1 2 (by decide) one)
  | ⟨9, _⟩ => .binary 7 8 (by simp [Fin.lt_def]) (by simp [Fin.lt_def]) (merge_sound 1 2)
  | ⟨10, _⟩ => .resolve 9 6 ∅ ∅ (pairBitLiteral (1 : Fin 3) 2 0)
      (by simp [Fin.lt_def]) (by simp [Fin.lt_def]) rfl rfl (Finset.empty_union ∅).symm
  | ⟨n + 11, h⟩ => absurd h (by omega)

def refutation : AffineDAG (usualBitPHPInitials 3 1) lines where
  step := stepAt

/-- The formal system refutes the smallest bit-PHP instance with eleven nodes. -/
theorem smallest_instance_refuted :
    ∃ (S : ℕ) (C : Fin S → FiniteParityClause V) (_ : AffineDAG (usualBitPHPInitials 3 1) C)
      (finish : Fin S), C finish = ∅ :=
  ⟨11, lines, refutation, 10, rfl⟩

end
end AuditWitnesses
