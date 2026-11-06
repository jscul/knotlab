/-
Relational knot kernel.

Two loops have presence variables `a` and `b` (true when the loop is present,
false when it is erased), and `k` is the contact. A relation is a Boolean
predicate on `(a, b, k)`; witness variables are existentially quantified away.
No executor supplies an input: a loop's own presence enters a constraint only
as a literal.

K1 binding: with both loops present, some contact value is excluded.
K2 loss on erasure: with either loop absent, nothing is excluded.
K3 coexistence: both loops can be present together.
-/
namespace KnotKernel

abbrev Rel3 := Bool → Bool → Bool → Bool

structure IsKnot (r : Rel3) : Prop where
  binding : ∃ k, r true true k = false
  erasureA : ∀ b k, r false b k = true
  erasureB : ∀ a k, r a false k = true
  coexistence : ∃ k, r true true k = true

/-- The atom `¬a ∨ ¬b ∨ k`: both loops present require the contact. -/
def atom (a b k : Bool) : Bool := !a || !b || k

/-- The same atom with the other contact value counted as made. -/
def atomNeg (a b k : Bool) : Bool := !a || !b || !k

theorem atom_isKnot : IsKnot atom :=
  ⟨⟨false, rfl⟩, by decide, by decide, ⟨true, rfl⟩⟩

theorem atomNeg_isKnot : IsKnot atomNeg :=
  ⟨⟨true, rfl⟩, by decide, by decide, ⟨false, rfl⟩⟩

/-- The two-loop knot is unique up to which contact value counts as made. -/
theorem knot_unique (r : Rel3) : IsKnot r ↔ (r = atom ∨ r = atomNeg) := by
  constructor
  · intro h
    obtain ⟨k₁, hk₁⟩ := h.binding
    obtain ⟨k₃, hk₃⟩ := h.coexistence
    have hA := h.erasureA
    have hB := h.erasureB
    cases h1 : r true true true <;> cases h0 : r true true false
    · cases k₃ <;> simp_all
    · right
      funext a b k
      cases a <;> cases b <;> cases k <;> simp_all [atomNeg]
    · left
      funext a b k
      cases a <;> cases b <;> cases k <;> simp_all [atom]
    · cases k₁ <;> simp_all
  · rintro (rfl | rfl)
    · exact atom_isKnot
    · exact atomNeg_isKnot

/-- Every two-variable shadow of a knot is unconstrained. -/
theorem knot_shadow_ab {r : Rel3} (h : IsKnot r) (a b : Bool) : ∃ k, r a b k = true := by
  cases a
  · exact ⟨false, h.erasureA b false⟩
  · cases b
    · exact ⟨false, h.erasureB true false⟩
    · exact h.coexistence

theorem knot_shadow_ak {r : Rel3} (h : IsKnot r) (a k : Bool) : ∃ b, r a b k = true :=
  ⟨false, h.erasureB a k⟩

theorem knot_shadow_bk {r : Rel3} (h : IsKnot r) (b k : Bool) : ∃ a, r a b k = true :=
  ⟨false, h.erasureA b k⟩

/-! ## Pairwise relations cannot define a knot -/

def majority (x y z : Bool) : Bool := (x && y) || (x && z) || (y && z)

def majorityAssign {V : Type} (x y z : V → Bool) : V → Bool :=
  fun v => majority (x v) (y v) (z v)

def MajorityClosed {V : Type} (r : (V → Bool) → Prop) : Prop :=
  ∀ x y z, r x → r y → r z → r (majorityAssign x y z)

structure Literal (V : Type) where
  atom : V
  positive : Bool

structure Clause2 (V : Type) where
  left : Literal V
  right : Literal V

abbrev CNF2 (V : Type) := List (Clause2 V)

def evalLiteral {V : Type} (σ : V → Bool) (l : Literal V) : Bool :=
  if l.positive then σ l.atom else !(σ l.atom)

def evalClause {V : Type} (σ : V → Bool) (c : Clause2 V) : Bool :=
  evalLiteral σ c.left || evalLiteral σ c.right

def Satisfies {V : Type} (f : CNF2 V) (σ : V → Bool) : Prop :=
  ∀ c, c ∈ f → evalClause σ c = true

theorem literal_majority {V : Type} (x y z : V → Bool) (l : Literal V) :
    evalLiteral (majorityAssign x y z) l =
      majority (evalLiteral x l) (evalLiteral y l) (evalLiteral z l) := by
  cases l with
  | mk atom positive =>
    cases hx : x atom <;> cases hy : y atom <;> cases hz : z atom <;>
      cases positive <;> simp [evalLiteral, majorityAssign, majority, hx, hy, hz]

theorem clause_majority {V : Type} (x y z : V → Bool) (c : Clause2 V)
    (hx : evalClause x c = true) (hy : evalClause y c = true)
    (hz : evalClause z c = true) :
    evalClause (majorityAssign x y z) c = true := by
  cases c with
  | mk left right =>
    simp only [evalClause]
    rw [literal_majority, literal_majority]
    simp only [evalClause] at hx hy hz
    generalize evalLiteral x left = xl at hx
    generalize evalLiteral y left = yl at hy
    generalize evalLiteral z left = zl at hz
    generalize evalLiteral x right = xr at hx
    generalize evalLiteral y right = yr at hy
    generalize evalLiteral z right = zr at hz
    cases xl <;> cases yl <;> cases zl <;> cases xr <;> cases yr <;> cases zr <;>
      simp [majority] at hx hy hz ⊢

theorem cnf_majority {V : Type} (f : CNF2 V) : MajorityClosed (Satisfies f) := by
  intro x y z hx hy hz c hc
  exact clause_majority x y z c (hx c hc) (hy c hc) (hz c hc)

def merge {V A : Type} (visible : V → Bool) (aux : A → Bool) : Sum V A → Bool
  | .inl v => visible v
  | .inr a => aux a

/-- What a 2-CNF over visible and witness variables allows once the witnesses
are quantified away. -/
def Projected {V A : Type} (f : CNF2 (Sum V A)) (visible : V → Bool) : Prop :=
  ∃ aux : A → Bool, Satisfies f (merge visible aux)

theorem projected_majority {V A : Type} (f : CNF2 (Sum V A)) :
    MajorityClosed (Projected f) := by
  intro x y z hx hy hz
  rcases hx with ⟨ax, hax⟩
  rcases hy with ⟨ay, hay⟩
  rcases hz with ⟨az, haz⟩
  refine ⟨majorityAssign ax ay az, ?_⟩
  have h := cnf_majority f (merge x ax) (merge y ay) (merge z az) hax hay haz
  have heq : majorityAssign (merge x ax) (merge y ay) (merge z az) =
      merge (majorityAssign x y z) (majorityAssign ax ay az) := by
    funext q
    cases q <;> rfl
  rw [heq] at h
  exact h

inductive TVar where | a | b | k deriving DecidableEq, Repr

def Sat (r : Rel3) (σ : TVar → Bool) : Prop := r (σ .a) (σ .b) (σ .k) = true

def tuple (a b k : Bool) : TVar → Bool
  | .a => a
  | .b => b
  | .k => k

/-- No knot is majority-closed: one loop erased, the other loop erased, and
both present give, by majority, both present with the excluded contact. -/
theorem knot_not_majority_closed {r : Rel3} (h : IsKnot r) : ¬ MajorityClosed (Sat r) := by
  intro hm
  rcases (knot_unique r).mp h with rfl | rfl
  · have bad := hm (tuple true false false) (tuple false true false) (tuple true true true)
      (by simp [Sat, tuple, atom]) (by simp [Sat, tuple, atom]) (by simp [Sat, tuple, atom])
    simp [Sat, tuple, atom, majorityAssign, majority] at bad
  · have bad := hm (tuple true false true) (tuple false true true) (tuple true true false)
      (by simp [Sat, tuple, atomNeg]) (by simp [Sat, tuple, atomNeg])
      (by simp [Sat, tuple, atomNeg])
    simp [Sat, tuple, atomNeg, majorityAssign, majority] at bad

/-- No 2-CNF, with any type of witness variables, defines a knot. -/
theorem no_two_cnf_defines_knot {A : Type} {r : Rel3} (h : IsKnot r)
    (f : CNF2 (Sum TVar A))
    (defines : ∀ visible, Projected f visible ↔ Sat r visible) : False := by
  apply knot_not_majority_closed h
  intro x y z hx hy hz
  apply (defines _).mp
  exact projected_majority f x y z ((defines x).mpr hx) ((defines y).mpr hy) ((defines z).mpr hz)

/-! ## Three-literal clauses bind any number of loops -/

/-- `Chain acc loops k`: the presence `acc` (the first loop, or the witness that
the loops so far are all present) is joined with the next loop by a clause of
exactly three literals, through a fresh witness, until the last clause
`¬acc ∨ ¬last ∨ k` names the contact. -/
def Chain (acc : Bool) : List Bool → Bool → Prop
  | [], k => (!acc || k) = true
  | [l], k => (!acc || !l || k) = true
  | l :: l' :: rest, k => ∃ w, (!acc || !l || w) = true ∧ Chain w (l' :: rest) k

/-- The chain allows exactly the states of the knot of all its loops: every
loop present requires the contact, and nothing else is constrained. -/
theorem chain_defines_knot :
    ∀ (rest : List Bool) (acc k : Bool),
      Chain acc rest k ↔ ((acc && rest.all id) = true → k = true)
  | [], acc, k => by cases acc <;> cases k <;> simp [Chain]
  | [l], acc, k => by cases acc <;> cases l <;> cases k <;> simp [Chain]
  | l :: l' :: rest, acc, k => by
    have ih := chain_defines_knot (l' :: rest)
    simp only [Chain]
    constructor
    · rintro ⟨w, h₁, h₂⟩ hall
      have hw : w = true := by
        cases acc <;> cases l <;> cases w <;> simp_all
      exact (ih w k).mp h₂ (by cases acc <;> cases l <;> simp_all)
    · intro h
      refine ⟨acc && l, by cases acc <;> cases l <;> rfl, ?_⟩
      apply (ih (acc && l) k).mpr
      intro hall
      apply h
      cases acc <;> cases l <;> simp_all

/-! ## The earlier kernel's erasure condition -/

/-- Erasure as stated by CONTACT-FORMAL-KERNEL-001A: once a loop is erased the
relation ignores the contact. -/
def OldErasureLoss (r : Rel3) : Prop :=
  (∀ b k₁ k₂, r false b k₁ = r false b k₂) ∧ (∀ a k₁ k₂, r a false k₁ = r a false k₂)

def Factors (r : Rel3) : Prop :=
  ∃ fA fB : Bool → Bool → Bool, ∀ a b k, r a b k = (fA a k && fB b k)

/-- `(a ↔ b) ∧ (a → k)`. -/
def tied (a b k : Bool) : Bool := (a == b) && (!a || k)

theorem tied_passes_old_conditions :
    tied true true true = true ∧ tied true true false = false ∧
      ¬ Factors tied ∧ OldErasureLoss tied := by
  refine ⟨rfl, rfl, ?_, ?_⟩
  · rintro ⟨fA, fB, h⟩
    have h111 := h true true true
    have h001 := h false false true
    have h101 := h true false true
    simp [tied] at h111 h001 h101
    simp_all
  · constructor <;> intro x k₁ k₂ <;> cases x <;> cases k₁ <;> cases k₂ <;> rfl

/-- The earlier kernel's role-swap persistence also holds for `tied`. -/
theorem tied_role_swap (a b k : Bool) : tied a b k = tied b a k := by
  cases a <;> cases b <;> cases k <;> rfl

def lit (v : TVar) (positive : Bool) : Literal TVar := ⟨v, positive⟩

/-- The clauses `¬a ∨ b`, `a ∨ ¬b` and `¬a ∨ k`. -/
def tiedCNF : CNF2 TVar :=
  [⟨lit .a false, lit .b true⟩, ⟨lit .a true, lit .b false⟩, ⟨lit .a false, lit .k true⟩]

theorem tied_is_two_cnf (σ : TVar → Bool) : Satisfies tiedCNF σ ↔ Sat tied σ := by
  cases ha : σ .a <;> cases hb : σ .b <;> cases hk : σ .k <;>
    simp [Satisfies, tiedCNF, evalClause, evalLiteral, lit, Sat, tied, ha, hb, hk]

theorem tied_not_knot : ¬ IsKnot tied := by
  intro h
  have := h.erasureA true false
  simp [tied] at this

/-! ## Checking a guard only while its loop runs -/

/-- Cross-wired 2-clause guards read relationally: A's guard `¬b ∨ k` and B's
guard `¬a ∨ k` both always hold. This is a common hub. -/
def crossRelational (a b k : Bool) : Bool := (!b || k) && (!a || k)

/-- A guard that is checked only while its loop runs holds when the loop is absent. -/
def whileRunning (present guard : Bool) : Bool := !present || guard

def crossGated (a b k : Bool) : Bool := whileRunning a (!b || k) && whileRunning b (!a || k)

theorem cross_relational_not_knot : ¬ IsKnot crossRelational := by
  intro h
  have := h.erasureB true false
  simp [crossRelational] at this

/-- Gating adds the loop's own presence as a literal, which turns each
2-clause guard into the three-literal atom. -/
theorem cross_gated_eq_atom : crossGated = atom := by
  funext a b k
  cases a <;> cases b <;> cases k <;> rfl

theorem cross_gated_isKnot : IsKnot crossGated := by
  rw [cross_gated_eq_atom]
  exact atom_isKnot

end KnotKernel
