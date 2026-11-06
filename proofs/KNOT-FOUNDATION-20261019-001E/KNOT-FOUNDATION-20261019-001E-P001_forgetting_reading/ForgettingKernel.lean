/-
Knot kernel for the forgetting reading of erasure.

Two loops contribute open distinctions `a` and `b`, and `k` is the contact. A
relation is a Boolean predicate on `(a, b, k)`; witness variables are
existentially quantified away. Erasing a loop forgets it: its variable is no
longer constrained by anything.

K1 binding: the relation is constrained as a whole.
K2 loss on erasure: forgetting any one of `a`, `b`, `k` leaves the other two
unconstrained.
K3 coexistence: some state is allowed; it follows from K2.
-/
namespace ForgettingKernel

abbrev Rel3 := Bool → Bool → Bool → Bool

structure IsKnot (r : Rel3) : Prop where
  binding : ∃ a b k, r a b k = false
  forgetA : ∀ b k, ∃ a, r a b k = true
  forgetB : ∀ a k, ∃ b, r a b k = true
  forgetK : ∀ a b, ∃ k, r a b k = true

theorem coexistence {r : Rel3} (h : IsKnot r) : ∃ a b k, r a b k = true := by
  obtain ⟨k, hk⟩ := h.forgetK true true
  exact ⟨true, true, k, hk⟩

/-- The atom `¬a ∨ ¬b ∨ k`: the knot that excludes the fewest states. -/
def atom (a b k : Bool) : Bool := !a || !b || k

/-- Even parity: the knot that excludes the most states. -/
def parity (a b k : Bool) : Bool := !(a ^^ b ^^ k)

theorem atom_isKnot : IsKnot atom where
  binding := ⟨true, true, false, rfl⟩
  forgetA := fun b k => ⟨false, by cases b <;> cases k <;> rfl⟩
  forgetB := fun a k => ⟨false, by cases a <;> cases k <;> rfl⟩
  forgetK := fun a b => ⟨true, by cases a <;> cases b <;> rfl⟩

theorem parity_isKnot : IsKnot parity where
  binding := ⟨true, false, false, rfl⟩
  forgetA := fun b k => ⟨b ^^ k, by cases b <;> cases k <;> rfl⟩
  forgetB := fun a k => ⟨a ^^ k, by cases a <;> cases k <;> rfl⟩
  forgetK := fun a b => ⟨a ^^ b, by cases a <;> cases b <;> rfl⟩

/-- The common hub `(¬a ∨ k) ∧ (¬b ∨ k)`. -/
def hub (a b k : Bool) : Bool := (!a || k) && (!b || k)

/-- `(a ↔ b) ∧ (a → k)`, accepted by the earlier kernel's erasure condition. -/
def tied (a b k : Bool) : Bool := (a == b) && (!a || k)

theorem hub_not_knot : ¬ IsKnot hub := by
  intro h
  obtain ⟨a, ha⟩ := h.forgetA true false
  cases a <;> simp [hub] at ha

theorem tied_not_knot : ¬ IsKnot tied := by
  intro h
  obtain ⟨k, hk⟩ := h.forgetK true false
  cases k <;> simp [tied] at hk

/-! ## The absence reading is a special case -/

/-- The absence reading of K1–K3: a loop's variable is its presence. -/
structure AbsenceKnot (r : Rel3) : Prop where
  binding : ∃ k, r true true k = false
  erasureA : ∀ b k, r false b k = true
  erasureB : ∀ a k, r a false k = true
  coexistence : ∃ k, r true true k = true

theorem absence_knot_is_knot {r : Rel3} (h : AbsenceKnot r) : IsKnot r where
  binding := by
    obtain ⟨k, hk⟩ := h.binding
    exact ⟨true, true, k, hk⟩
  forgetA := fun b k => ⟨false, h.erasureA b k⟩
  forgetB := fun a k => ⟨false, h.erasureB a k⟩
  forgetK := fun a b => by
    cases a
    · exact ⟨false, h.erasureA b false⟩
    · cases b
      · exact ⟨false, h.erasureB true false⟩
      · exact h.coexistence

theorem parity_not_absence_knot : ¬ AbsenceKnot parity := by
  intro h
  have := h.erasureA true false
  simp [parity] at this

/-! ## A knot implies no clause narrower than its three variables -/

theorem no_clause_on_a_b {r : Rel3} (h : IsKnot r) (u v : Bool) :
    ¬ ∀ a b k, r a b k = true → (a = u ∨ b = v) := by
  intro implied
  obtain ⟨k, hk⟩ := h.forgetK (!u) (!v)
  rcases implied (!u) (!v) k hk with hu | hv
  · cases u <;> simp at hu
  · cases v <;> simp at hv

theorem no_clause_on_a_k {r : Rel3} (h : IsKnot r) (u v : Bool) :
    ¬ ∀ a b k, r a b k = true → (a = u ∨ k = v) := by
  intro implied
  obtain ⟨b, hb⟩ := h.forgetB (!u) (!v)
  rcases implied (!u) b (!v) hb with hu | hv
  · cases u <;> simp at hu
  · cases v <;> simp at hv

theorem no_clause_on_b_k {r : Rel3} (h : IsKnot r) (u v : Bool) :
    ¬ ∀ a b k, r a b k = true → (b = u ∨ k = v) := by
  intro implied
  obtain ⟨a, ha⟩ := h.forgetA (!u) (!v)
  rcases implied a (!u) (!v) ha with hu | hv
  · cases u <;> simp at hu
  · cases v <;> simp at hv

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

theorem tuple_eta (σ : TVar → Bool) : tuple (σ .a) (σ .b) (σ .k) = σ := by
  funext v
  cases v <;> rfl

/-- A majority-closed relation whose three pair shadows are unconstrained
allows every state: for a target state, take an allowed state agreeing with
it on each pair; their majority is the target. -/
theorem majority_with_free_pairs_is_full {r : Rel3}
    (hm : MajorityClosed (Sat r))
    (hab : ∀ a b, ∃ k, r a b k = true)
    (hak : ∀ a k, ∃ b, r a b k = true)
    (hbk : ∀ b k, ∃ a, r a b k = true) :
    ∀ a b k, r a b k = true := by
  intro a b k
  obtain ⟨k₁, h₁⟩ := hab a b
  obtain ⟨b₂, h₂⟩ := hak a k
  obtain ⟨a₃, h₃⟩ := hbk b k
  have hmaj := hm (tuple a b k₁) (tuple a b₂ k) (tuple a₃ b k) h₁ h₂ h₃
  have target : majorityAssign (tuple a b k₁) (tuple a b₂ k) (tuple a₃ b k) = tuple a b k := by
    funext v
    cases v <;> cases a <;> cases b <;> cases k <;> cases k₁ <;> cases b₂ <;> cases a₃ <;> rfl
  rw [target] at hmaj
  exact hmaj

/-- No 2-CNF, with any type of witness variables, defines a knot. -/
theorem no_two_cnf_defines_knot {A : Type} {r : Rel3} (h : IsKnot r)
    (f : CNF2 (Sum TVar A))
    (defines : ∀ visible, Projected f visible ↔ Sat r visible) : False := by
  have hm : MajorityClosed (Sat r) := by
    intro x y z hx hy hz
    apply (defines _).mp
    exact projected_majority f x y z ((defines x).mpr hx) ((defines y).mpr hy) ((defines z).mpr hz)
  have full := majority_with_free_pairs_is_full hm h.forgetK h.forgetB h.forgetA
  obtain ⟨a, b, k, hfalse⟩ := h.binding
  rw [full a b k] at hfalse
  exact Bool.noConfusion hfalse

/-! ## Naming partial matches keeps parity at three literals -/

/-- `ParityChain acc rest t`: each step names `w = acc xor l` with four clauses
of three literals, and the last name must equal `t`. -/
def ParityChain (acc : Bool) : List Bool → Bool → Prop
  | [], t => acc = t
  | l :: rest, t =>
      ∃ w, ((!w || acc || l) && (!w || !acc || !l) && (w || !acc || l) && (w || acc || !l)) = true ∧
        ParityChain w rest t

theorem parity_chain_defines_parity :
    ∀ (rest : List Bool) (acc t : Bool), ParityChain acc rest t ↔ rest.foldl (· ^^ ·) acc = t
  | [], acc, t => by simp [ParityChain]
  | l :: rest, acc, t => by
    have ih := parity_chain_defines_parity rest
    simp only [ParityChain, List.foldl]
    constructor
    · rintro ⟨w, hw, hrest⟩
      have : w = (acc ^^ l) := by
        cases w <;> cases acc <;> cases l <;> simp_all
      rw [← this]
      exact (ih w t).mp hrest
    · intro h
      refine ⟨acc ^^ l, by cases acc <;> cases l <;> rfl, ?_⟩
      exact (ih (acc ^^ l) t).mpr h

end ForgettingKernel
