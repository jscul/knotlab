/-
Competition kernel: which knots competing rules on pairs can make.

A state of `m` distinctions is a function `Fin m → Bool`, and a relation
`r : State m → Bool` says which states a system allows. Under the forgetting
reading of K1–K3, `r` is a knot when it excludes some state and forgetting any
one coordinate leaves the rest unconstrained: of any state and its neighbour
across that coordinate, at least one is allowed.

A pairwise energy is a finite sum of integer terms, each depending on at most
two coordinates. Its least set is the set of states where it is smallest. A
system of rules on pairs has two readings:
* strict: the allowed states break no rule;
* competition: the allowed states break the fewest rules, the least set of the
  violation count, which is a pairwise energy.

Main results:
* `slice_vanishes`: the alternating sum of a pairwise energy over any
  three-coordinate slice is zero.
* `no_knot_on_four_distinct` and `no_knot_beyond_three`: on four or more
  distinctions no knot is the least set of a pairwise energy.
* `three_variable_classification`: on three distinctions a knot is the least
  set of a pairwise energy exactly when it is a not-all-equal relation, which
  excludes one state and its opposite. The frustrated triangle realizes it.
* `strict_pairwise_no_knot`: under the strict reading, rules on pairs never
  allow exactly a knot on three or more distinctions.
* `competition_pairwise_no_knot`: under the competition reading, they never do
  on four or more.
* `readings_agree_when_satisfiable`: the readings agree whenever some state
  breaks no rule.
* `gadget_projection`: with one hidden variable per excluded state, ten
  two-literal clauses each make every relation on three distinctions with an
  allowed state the projection of a least set (Garey, Johnson and Stockmeyer
  1976).
* Frustrated and weighted triangles, checked by evaluation.
-/
namespace CompetitionKernel

/-! ## States, flips and knots -/

abbrev State (m : Nat) := Fin m → Bool

/-- Flip coordinate `i`. -/
def toggle {m : Nat} (x : State m) (i : Fin m) : State m := fun j => x j ^^ decide (j = i)

theorem toggle_ne {m : Nat} (x : State m) {i p : Fin m} (h : p ≠ i) : toggle x i p = x p := by
  simp [toggle, h]

theorem toggle_comm {m : Nat} (x : State m) (a b : Fin m) :
    toggle (toggle x a) b = toggle (toggle x b) a := by
  funext j
  simp only [toggle]
  generalize x j = u
  generalize decide (j = a) = v
  generalize decide (j = b) = w
  cases u <;> cases v <;> cases w <;> rfl

/-- K1–K3 under the forgetting reading. -/
structure IsKnot {m : Nat} (r : State m → Bool) : Prop where
  binding : ∃ x, r x = false
  forget : ∀ (i : Fin m) (x : State m), r x = true ∨ r (toggle x i) = true

theorem neighbour_allowed {m : Nat} {r : State m → Bool} (hk : IsKnot r) {e : State m}
    (he : r e = false) (i : Fin m) : r (toggle e i) = true := by
  rcases hk.forget i e with h | h
  · rw [he] at h
    cases h
  · exact h

/-! ## Pairwise energies -/

/-- A term that depends on at most the coordinates `p` and `q`. -/
structure Term (m : Nat) where
  p : Fin m
  q : Fin m
  f : State m → Int
  depends : ∀ x y : State m, x p = y p → x q = y q → f x = f y

def energy {m : Nat} : List (Term m) → State m → Int
  | [], _ => 0
  | t :: ts, x => t.f x + energy ts x

/-- `r` is exactly the set of states where `E` is smallest. -/
def LeastSet {m : Nat} (E : State m → Int) (r : State m → Bool) : Prop :=
  ∀ x, r x = true ↔ ∀ y, E x ≤ E y

/-- The alternating sum of `E` over the slice through `x` on `i`, `j` and `k`. -/
def slice {m : Nat} (E : State m → Int) (x : State m) (i j k : Fin m) : Int :=
  E x - E (toggle x i) - E (toggle x j) - E (toggle x k)
    + E (toggle (toggle x i) j) + E (toggle (toggle x i) k) + E (toggle (toggle x j) k)
    - E (toggle (toggle (toggle x i) j) k)

theorem term_toggle {m : Nat} (t : Term m) {k : Fin m} (hp : k ≠ t.p) (hq : k ≠ t.q)
    (y : State m) : t.f (toggle y k) = t.f y :=
  t.depends _ _ (toggle_ne y (Ne.symm hp)) (toggle_ne y (Ne.symm hq))

/-- Three distinct coordinates cannot all lie in a set of two. -/
theorem one_outside {m : Nat} {i j k p q : Fin m} (hij : i ≠ j) (hik : i ≠ k) (hjk : j ≠ k) :
    (k ≠ p ∧ k ≠ q) ∨ (j ≠ p ∧ j ≠ q) ∨ (i ≠ p ∧ i ≠ q) := by
  by_cases hk1 : k = p
  · subst hk1
    by_cases hj2 : j = q
    · subst hj2
      exact Or.inr (Or.inr ⟨hik, hij⟩)
    · exact Or.inr (Or.inl ⟨hjk, hj2⟩)
  · by_cases hk2 : k = q
    · subst hk2
      by_cases hj1 : j = p
      · subst hj1
        exact Or.inr (Or.inr ⟨hij, hik⟩)
      · exact Or.inr (Or.inl ⟨hj1, hjk⟩)
    · exact Or.inl ⟨hk1, hk2⟩

theorem term_slice {m : Nat} (t : Term m) (x : State m) {i j k : Fin m}
    (hij : i ≠ j) (hik : i ≠ k) (hjk : j ≠ k) : slice t.f x i j k = 0 := by
  rcases one_outside (p := t.p) (q := t.q) hij hik hjk with ⟨hp, hq⟩ | ⟨hp, hq⟩ | ⟨hp, hq⟩
  · have h1 := term_toggle t hp hq x
    have h2 := term_toggle t hp hq (toggle x i)
    have h3 := term_toggle t hp hq (toggle x j)
    have h4 := term_toggle t hp hq (toggle (toggle x i) j)
    simp only [slice]
    omega
  · have h1 := term_toggle t hp hq x
    have h2 := term_toggle t hp hq (toggle x i)
    have h3 := term_toggle t hp hq (toggle x k)
    have h4 := term_toggle t hp hq (toggle (toggle x i) k)
    have c1 := congrArg t.f (toggle_comm x j k)
    have c2 := congrArg t.f (toggle_comm (toggle x i) j k)
    simp only [slice]
    omega
  · have h1 := term_toggle t hp hq x
    have h2 := term_toggle t hp hq (toggle x j)
    have h3 := term_toggle t hp hq (toggle x k)
    have h4 := term_toggle t hp hq (toggle (toggle x j) k)
    have c1 := congrArg t.f (toggle_comm x i j)
    have c2 := congrArg t.f (toggle_comm x i k)
    have c3 : t.f (toggle (toggle (toggle x i) j) k) = t.f (toggle (toggle (toggle x j) k) i) := by
      rw [toggle_comm x i j, toggle_comm (toggle x j) i k]
    simp only [slice]
    omega

/-- On every three-coordinate slice, a pairwise energy has alternating sum zero. -/
theorem slice_vanishes {m : Nat} (terms : List (Term m)) (x : State m) {i j k : Fin m}
    (hij : i ≠ j) (hik : i ≠ k) (hjk : j ≠ k) : slice (energy terms) x i j k = 0 := by
  induction terms with
  | nil => simp [slice, energy]
  | cons t ts ih =>
    have ht := term_slice t x hij hik hjk
    simp only [slice, energy] at ht ih ⊢
    omega

/-! ## A least-set knot excludes the opposite corner of every slice -/

theorem levels {m : Nat} {E : State m → Int} {r : State m → Bool}
    (hl : LeastSet E r) {x0 : State m} (h0 : r x0 = true) :
    (∀ x, r x = true → E x = E x0) ∧ (∀ x, r x = false → E x0 < E x) := by
  constructor
  · intro x hx
    have a := (hl x).mp hx x0
    have b := (hl x0).mp h0 x
    omega
  · intro x hx
    by_cases hlt : E x0 < E x
    · exact hlt
    · exfalso
      have least : ∀ y, E x ≤ E y := fun y => by
        have := (hl x0).mp h0 y
        omega
      have := (hl x).mpr least
      rw [hx] at this
      cases this

theorem above_min {m : Nat} {E : State m → Int} {r : State m → Bool} {c : Int}
    (ha : ∀ x, r x = true → E x = c) (hx : ∀ x, r x = false → c < E x) (z : State m) :
    c ≤ E z := by
  cases h : r z
  · have := hx z h
    omega
  · have := ha z h
    omega

theorem opposite_in_slice {m : Nat} {E : State m → Int} {r : State m → Bool} {c : Int}
    (ha : ∀ x, r x = true → E x = c) (hx : ∀ x, r x = false → c < E x)
    {e : State m} {i j k : Fin m} (he : r e = false)
    (hi : r (toggle e i) = true) (hj : r (toggle e j) = true) (hk : r (toggle e k) = true)
    (hs : slice E e i j k = 0) :
    r (toggle (toggle (toggle e i) j) k) = false := by
  cases h : r (toggle (toggle (toggle e i) j) k)
  · rfl
  · exfalso
    have h0 := hx e he
    have h1 := ha _ hi
    have h2 := ha _ hj
    have h3 := ha _ hk
    have h4 := above_min ha hx (toggle (toggle e i) j)
    have h5 := above_min ha hx (toggle (toggle e i) k)
    have h6 := above_min ha hx (toggle (toggle e j) k)
    have h7 := ha _ h
    simp only [slice] at hs
    omega

/-! ## No knot on four or more distinctions -/

theorem six_flips {m : Nat} (e : State m) (i j k l : Fin m) :
    toggle (toggle (toggle (toggle (toggle (toggle e i) j) k) i) j) l = toggle (toggle e k) l := by
  funext z
  simp only [toggle]
  generalize e z = u
  generalize decide (z = i) = a
  generalize decide (z = j) = b
  generalize decide (z = k) = c
  generalize decide (z = l) = d
  cases u <;> cases a <;> cases b <;> cases c <;> cases d <;> rfl

theorem no_knot_on_four_distinct {m : Nat} {r : State m → Bool} (hk : IsKnot r)
    (terms : List (Term m)) (hl : LeastSet (energy terms) r)
    {i j k l : Fin m} (hij : i ≠ j) (hik : i ≠ k) (hil : i ≠ l)
    (hjk : j ≠ k) (hjl : j ≠ l) (hkl : k ≠ l) : False := by
  obtain ⟨e, he⟩ := hk.binding
  obtain ⟨ha, hx⟩ := levels hl (neighbour_allowed hk he i)
  -- The slice through `e` on `i, j, k` excludes `e` with all three flipped.
  have s1 := opposite_in_slice ha hx he (neighbour_allowed hk he i) (neighbour_allowed hk he j)
    (neighbour_allowed hk he k) (slice_vanishes terms e hij hik hjk)
  -- The slice through that state on `i, j, l` excludes `e` with `k` and `l` flipped.
  have s2 := opposite_in_slice ha hx s1 (neighbour_allowed hk s1 i) (neighbour_allowed hk s1 j)
    (neighbour_allowed hk s1 l) (slice_vanishes terms _ hij hil hjl)
  rw [six_flips] at s2
  -- The slice through `e` on `k, l, i` now has two excluded states of the same parity.
  have hs := slice_vanishes terms e hkl (Ne.symm hik) (Ne.symm hil)
  simp only [slice] at hs
  have c0 := hx e he
  have c1 := ha _ (neighbour_allowed hk he k)
  have c2 := ha _ (neighbour_allowed hk he l)
  have c3 := ha _ (neighbour_allowed hk he i)
  have c4 := hx _ s2
  have c5 := above_min ha hx (toggle (toggle e k) i)
  have c6 := above_min ha hx (toggle (toggle e l) i)
  have c7 := ha _ (neighbour_allowed hk s2 i)
  omega

/-- On four or more distinctions, no knot is the least set of a pairwise energy. -/
theorem no_knot_beyond_three {m : Nat} (hm : 4 ≤ m) {r : State m → Bool} (hk : IsKnot r)
    (terms : List (Term m)) (hl : LeastSet (energy terms) r) : False :=
  no_knot_on_four_distinct (i := ⟨0, by omega⟩) (j := ⟨1, by omega⟩) (k := ⟨2, by omega⟩)
    (l := ⟨3, by omega⟩) hk terms hl
    (fun h => by cases h) (fun h => by cases h) (fun h => by cases h)
    (fun h => by cases h) (fun h => by cases h) (fun h => by cases h)

/-! ## Three distinctions -/

def antipode {m : Nat} (x : State m) : State m := fun j => !x j

def i0 : Fin 3 := ⟨0, by decide⟩
def i1 : Fin 3 := ⟨1, by decide⟩
def i2 : Fin 3 := ⟨2, by decide⟩

theorem ext3 {x y : State 3} (h0 : x i0 = y i0) (h1 : x i1 = y i1) (h2 : x i2 = y i2) : x = y := by
  funext z
  match z with
  | ⟨0, _⟩ => exact h0
  | ⟨1, _⟩ => exact h1
  | ⟨2, _⟩ => exact h2

theorem toggle_val {m : Nat} (x : State m) (i j : Fin m) :
    toggle x i j = (x j ^^ decide (j = i)) := rfl

/-- Not all of `x` agrees with `e` and not all of it disagrees: the not-all-equal
relation that excludes `e` and its opposite. -/
def nae (e : State 3) (x : State 3) : Bool :=
  !(((x i0 ^^ e i0) == (x i1 ^^ e i1)) && ((x i1 ^^ e i1) == (x i2 ^^ e i2)))

theorem three_flips_is_antipode (e : State 3) :
    toggle (toggle (toggle e i0) i1) i2 = antipode e := by
  apply ext3 <;> simp [toggle_val, antipode, i0, i1, i2]

theorem xor_eq_true {a b : Bool} (h : (a ^^ b) = true) : a = !b := by
  cases a <;> cases b <;> simp_all

theorem xor_eq_false {a b : Bool} (h : (a ^^ b) = false) : a = b := by
  cases a <;> cases b <;> simp_all

theorem fin3_cases (i : Fin 3) : i = i0 ∨ i = i1 ∨ i = i2 := by
  match i with
  | ⟨0, _⟩ => exact Or.inl rfl
  | ⟨1, _⟩ => exact Or.inr (Or.inl rfl)
  | ⟨2, _⟩ => exact Or.inr (Or.inr rfl)

theorem toggle_same {m : Nat} (x : State m) (i : Fin m) : toggle x i i = !x i := by
  simp [toggle_val]

/-- Every state of the 3-cube is `e`, its opposite, or a neighbour of one of them. -/
theorem cube_cover (e x : State 3) :
    nae e x = false ∧ (x = e ∨ x = antipode e) ∨
      nae e x = true ∧ ∃ i, x = toggle e i ∨ x = toggle (antipode e) i := by
  have d01 : i0 ≠ i1 := by decide
  have d02 : i0 ≠ i2 := by decide
  have d12 : i1 ≠ i2 := by decide
  rcases Bool.eq_false_or_eq_true (x i0 ^^ e i0) with h0 | h0 <;>
  rcases Bool.eq_false_or_eq_true (x i1 ^^ e i1) with h1 | h1 <;>
  rcases Bool.eq_false_or_eq_true (x i2 ^^ e i2) with h2 | h2
  · -- all three differ from `e`: the opposite state
    refine Or.inl ⟨by simp [nae, h0, h1, h2], Or.inr (ext3 ?_ ?_ ?_)⟩
    · exact xor_eq_true h0
    · exact xor_eq_true h1
    · exact xor_eq_true h2
  · refine Or.inr ⟨by simp [nae, h0, h1, h2], i2, Or.inr (ext3 ?_ ?_ ?_)⟩
    · rw [toggle_ne _ d02]; exact xor_eq_true h0
    · rw [toggle_ne _ d12]; exact xor_eq_true h1
    · rw [toggle_same]; simp only [antipode, Bool.not_not]; exact xor_eq_false h2
  · refine Or.inr ⟨by simp [nae, h0, h1, h2], i1, Or.inr (ext3 ?_ ?_ ?_)⟩
    · rw [toggle_ne _ d01]; exact xor_eq_true h0
    · rw [toggle_same]; simp only [antipode, Bool.not_not]; exact xor_eq_false h1
    · rw [toggle_ne _ (Ne.symm d12)]; exact xor_eq_true h2
  · refine Or.inr ⟨by simp [nae, h0, h1, h2], i0, Or.inl (ext3 ?_ ?_ ?_)⟩
    · rw [toggle_same]; exact xor_eq_true h0
    · rw [toggle_ne _ (Ne.symm d01)]; exact xor_eq_false h1
    · rw [toggle_ne _ (Ne.symm d02)]; exact xor_eq_false h2
  · refine Or.inr ⟨by simp [nae, h0, h1, h2], i0, Or.inr (ext3 ?_ ?_ ?_)⟩
    · rw [toggle_same]; simp only [antipode, Bool.not_not]; exact xor_eq_false h0
    · rw [toggle_ne _ (Ne.symm d01)]; exact xor_eq_true h1
    · rw [toggle_ne _ (Ne.symm d02)]; exact xor_eq_true h2
  · refine Or.inr ⟨by simp [nae, h0, h1, h2], i1, Or.inl (ext3 ?_ ?_ ?_)⟩
    · rw [toggle_ne _ d01]; exact xor_eq_false h0
    · rw [toggle_same]; exact xor_eq_true h1
    · rw [toggle_ne _ (Ne.symm d12)]; exact xor_eq_false h2
  · refine Or.inr ⟨by simp [nae, h0, h1, h2], i2, Or.inl (ext3 ?_ ?_ ?_)⟩
    · rw [toggle_ne _ d02]; exact xor_eq_false h0
    · rw [toggle_ne _ d12]; exact xor_eq_false h1
    · rw [toggle_same]; exact xor_eq_true h2
  · refine Or.inl ⟨by simp [nae, h0, h1, h2], Or.inl (ext3 ?_ ?_ ?_)⟩
    · exact xor_eq_false h0
    · exact xor_eq_false h1
    · exact xor_eq_false h2

/-- A knot on three distinctions that excludes a state and its opposite is the
not-all-equal relation around them. -/
theorem knot_is_nae {r : State 3 → Bool} (hk : IsKnot r) {e : State 3}
    (he : r e = false) (hn : r (antipode e) = false) : ∀ x, r x = nae e x := by
  intro x
  rcases cube_cover e x with ⟨hv, hx | hx⟩ | ⟨hv, i, hx | hx⟩
  · rw [hv, hx, he]
  · rw [hv, hx, hn]
  · rw [hv, hx, neighbour_allowed hk he i]
  · rw [hv, hx, neighbour_allowed hk hn i]

/-- The frustrated triangle around `e`: each pair should disagree relative to `e`. -/
def disagree (e : State 3) (a b : Fin 3) : Term 3 where
  p := a
  q := b
  f := fun x => bif (x a ^^ e a) == (x b ^^ e b) then 1 else 0
  depends := fun x y hp hq => by simp only [hp, hq]

def frustrated (e : State 3) : List (Term 3) := [disagree e i0 i1, disagree e i0 i2, disagree e i1 i2]

theorem frustrated_energy (e x : State 3) :
    energy (frustrated e) x = bif nae e x then 1 else 3 := by
  simp only [frustrated, energy, disagree, nae]
  generalize (x i0 ^^ e i0) = a
  generalize (x i1 ^^ e i1) = b
  generalize (x i2 ^^ e i2) = c
  cases a <;> cases b <;> cases c <;> rfl

theorem frustrated_least (e : State 3) : LeastSet (energy (frustrated e)) (nae e) := by
  have hy : nae e (toggle e i0) = true := by
    simp [nae, toggle_val, i0, i1, i2]
  intro x
  rw [frustrated_energy]
  constructor
  · intro hx y
    rw [frustrated_energy, hx]
    cases nae e y <;> decide
  · intro least
    have := least (toggle e i0)
    rw [frustrated_energy, hy] at this
    cases h : nae e x
    · rw [h] at this
      exact absurd this (by decide)
    · rfl

theorem nae_is_knot (e : State 3) : IsKnot (nae e) where
  binding := ⟨e, by simp [nae]⟩
  forget := fun i x => by
    rcases fin3_cases i with rfl | rfl | rfl <;>
    simp only [nae, toggle_val] <;>
    generalize x i0 = a0 <;> generalize x i1 = a1 <;> generalize x i2 = a2 <;>
    generalize e i0 = b0 <;> generalize e i1 = b1 <;> generalize e i2 = b2 <;>
    cases a0 <;> cases a1 <;> cases a2 <;> cases b0 <;> cases b1 <;> cases b2 <;> decide

/-- On three distinctions, a knot is the least set of a pairwise energy exactly
when it is the not-all-equal relation around some state, excluding that state
and its opposite. -/
theorem three_variable_classification {r : State 3 → Bool} (hk : IsKnot r) :
    (∃ terms : List (Term 3), LeastSet (energy terms) r) ↔ ∃ e, ∀ x, r x = nae e x := by
  constructor
  · rintro ⟨terms, hl⟩
    obtain ⟨e, he⟩ := hk.binding
    obtain ⟨ha, hx⟩ := levels hl (neighbour_allowed hk he i0)
    have s := opposite_in_slice ha hx he (neighbour_allowed hk he i0) (neighbour_allowed hk he i1)
      (neighbour_allowed hk he i2) (slice_vanishes terms e (by decide) (by decide) (by decide))
    rw [three_flips_is_antipode] at s
    exact ⟨e, knot_is_nae hk he s⟩
  · rintro ⟨e, he⟩
    refine ⟨frustrated e, fun x => ?_⟩
    rw [he x]
    exact frustrated_least e x

/-! ## The strict reading -/

/-- A rule on the pair `p, q`: it holds exactly when `g (x p) (x q)`. -/
structure PairRule (m : Nat) where
  p : Fin m
  q : Fin m
  g : Bool → Bool → Bool

def holds {m : Nat} (rule : PairRule m) (x : State m) : Bool := rule.g (x rule.p) (x rule.q)

def allHold {m : Nat} (rules : List (PairRule m)) (x : State m) : Bool :=
  rules.all (fun rule => holds rule x)

theorem third_coordinate {m : Nat} (hm : 3 ≤ m) (p q : Fin m) : ∃ s : Fin m, s ≠ p ∧ s ≠ q := by
  rcases one_outside (i := (⟨0, by omega⟩ : Fin m)) (j := ⟨1, by omega⟩) (k := ⟨2, by omega⟩)
    (p := p) (q := q) (fun h => by cases h) (fun h => by cases h) (fun h => by cases h)
    with h | h | h
  · exact ⟨_, h⟩
  · exact ⟨_, h⟩
  · exact ⟨_, h⟩

/-- On three or more distinctions, every pair is free in a knot. -/
theorem free_pairs {m : Nat} (hm : 3 ≤ m) {r : State m → Bool} (hk : IsKnot r)
    {p q : Fin m} (hpq : p ≠ q) (u v : Bool) : ∃ x, r x = true ∧ x p = u ∧ x q = v := by
  obtain ⟨s, hsp, hsq⟩ := third_coordinate hm p q
  let base : State m := fun j => if j = p then u else if j = q then v else false
  have bp : base p = u := by simp [base]
  have bq : base q = v := by simp [base, Ne.symm hpq]
  rcases hk.forget s base with h | h
  · exact ⟨base, h, bp, bq⟩
  · refine ⟨toggle base s, h, ?_, ?_⟩
    · rw [toggle_ne base (Ne.symm hsp)]; exact bp
    · rw [toggle_ne base (Ne.symm hsq)]; exact bq

/-- Under the strict reading, rules on pairs never allow exactly a knot on three or
more distinctions: every pair is free among the allowed states, so every rule
holds at every pair of values, and nothing is excluded. -/
theorem strict_pairwise_no_knot {m : Nat} (hm : 3 ≤ m) (rules : List (PairRule m))
    (hk : IsKnot (allHold rules)) : False := by
  obtain ⟨y, hy⟩ := hk.binding
  have : allHold rules y = true := by
    simp only [allHold, List.all_eq_true]
    intro rule hr
    by_cases hpq : rule.p = rule.q
    · obtain ⟨s, hs, -⟩ := third_coordinate hm rule.p rule.p
      obtain ⟨x, hx, hxp, -⟩ := free_pairs hm hk (Ne.symm hs) (y rule.p) false
      have hall := List.all_eq_true.mp hx rule hr
      simp only [holds] at hall ⊢
      rw [← hpq, hxp] at hall
      rw [← hpq]
      exact hall
    · obtain ⟨x, hx, hxp, hxq⟩ := free_pairs hm hk hpq (y rule.p) (y rule.q)
      have hall := List.all_eq_true.mp hx rule hr
      simp only [holds] at hall ⊢
      rw [hxp, hxq] at hall
      exact hall
  rw [hy] at this
  cases this

/-- Breaking a rule on a pair costs one: a term on that pair. -/
def violation {m : Nat} (rule : PairRule m) : Term m where
  p := rule.p
  q := rule.q
  f := fun x => bif holds rule x then 0 else 1
  depends := fun x y hp hq => by simp only [holds, hp, hq]

/-- Under the competition reading, rules on four or more distinctions never allow
exactly a knot. -/
theorem competition_pairwise_no_knot {m : Nat} (hm : 4 ≤ m) (rules : List (PairRule m))
    {r : State m → Bool} (hk : IsKnot r) (hl : LeastSet (energy (rules.map violation)) r) : False :=
  no_knot_beyond_three hm hk _ hl

/-! ## The readings agree when some state breaks no rule -/

def broken {S : Type} : List (S → Bool) → S → Nat
  | [], _ => 0
  | rule :: rules, x => (if rule x then 0 else 1) + broken rules x

theorem readings_agree_when_satisfiable {S : Type} (rules : List (S → Bool))
    (h : ∃ x0, broken rules x0 = 0) :
    ∀ x, broken rules x = 0 ↔ ∀ y, broken rules x ≤ broken rules y := by
  obtain ⟨x0, h0⟩ := h
  intro x
  constructor
  · intro hx y
    omega
  · intro least
    have := least x0
    omega

/-! ## Hidden variables: every relation on three distinctions -/

abbrev Triple := Bool × Bool × Bool

/-- Clauses broken by one gadget with literals `l0, l1, l2` and hidden `w`:
`l0, l1, l2, w, ¬l0 ∨ ¬l1, ¬l1 ∨ ¬l2, ¬l0 ∨ ¬l2, l0 ∨ ¬w, l1 ∨ ¬w, l2 ∨ ¬w`. -/
def gadget (l0 l1 l2 w : Bool) : Nat :=
  (if l0 then 0 else 1) + (if l1 then 0 else 1) + (if l2 then 0 else 1) + (if w then 0 else 1)
    + (if l0 && l1 then 1 else 0) + (if l1 && l2 then 1 else 0) + (if l0 && l2 then 1 else 0)
    + (if !l0 && w then 1 else 0) + (if !l1 && w then 1 else 0) + (if !l2 && w then 1 else 0)

theorem gadget_bound : ∀ l0 l1 l2 w : Bool,
    3 + (if l0 || l1 || l2 then 0 else 1) ≤ gadget l0 l1 l2 w := by decide

theorem gadget_best : ∀ l0 l1 l2 : Bool,
    ∃ w, gadget l0 l1 l2 w = 3 + (if l0 || l1 || l2 then 0 else 1) := by decide

/-- The gadget for excluded state `b` reads its literals as "differs from `b`". -/
def gadgetAt (b x : Triple) (w : Bool) : Nat :=
  gadget (x.1 != b.1) (x.2.1 != b.2.1) (x.2.2 != b.2.2) w

theorem differs_somewhere (b x : Triple) :
    ((x.1 != b.1) || (x.2.1 != b.2.1) || (x.2.2 != b.2.2)) = !(decide (x = b)) := by
  obtain ⟨b1, b2, b3⟩ := b
  obtain ⟨x1, x2, x3⟩ := x
  cases b1 <;> cases b2 <;> cases b3 <;> cases x1 <;> cases x2 <;> cases x3 <;> decide

def total : List Triple → List Bool → Triple → Nat
  | b :: bs, w :: ws, x => gadgetAt b x w + total bs ws x
  | _, _, _ => 0

def hits : List Triple → Triple → Nat
  | [], _ => 0
  | b :: bs, x => (if x = b then 1 else 0) + hits bs x

theorem total_bound : ∀ (bs : List Triple) (ws : List Bool) (x : Triple),
    ws.length = bs.length → 3 * bs.length + hits bs x ≤ total bs ws x
  | [], [], _, _ => by simp [total, hits]
  | [], _ :: _, _, h => by simp at h
  | _ :: _, [], _, h => by simp at h
  | b :: bs, w :: ws, x, h => by
    have ih := total_bound bs ws x (by simpa using h)
    have g := gadget_bound (x.1 != b.1) (x.2.1 != b.2.1) (x.2.2 != b.2.2) w
    rw [differs_somewhere] at g
    simp only [total, hits, gadgetAt, List.length_cons]
    by_cases hb : x = b
    · subst hb
      simp at g ⊢
      omega
    · simp [hb] at g ⊢
      omega

theorem total_best : ∀ (bs : List Triple) (x : Triple),
    ∃ ws : List Bool, ws.length = bs.length ∧ total bs ws x = 3 * bs.length + hits bs x
  | [], x => ⟨[], rfl, by simp [total, hits]⟩
  | b :: bs, x => by
    obtain ⟨ws, hl, ht⟩ := total_best bs x
    obtain ⟨w, hw⟩ := gadget_best (x.1 != b.1) (x.2.1 != b.2.1) (x.2.2 != b.2.2)
    rw [differs_somewhere] at hw
    refine ⟨w :: ws, by simp [hl], ?_⟩
    simp only [total, hits, gadgetAt, List.length_cons, ht]
    by_cases hb : x = b <;> simp [hb] at hw ⊢ <;> omega

/-- A visible state belongs to the projection of the least set when some hidden
assignment makes it least among all states and assignments. -/
def ProjectedLeast (bs : List Triple) (x : Triple) : Prop :=
  ∃ ws : List Bool, ws.length = bs.length ∧
    ∀ (x' : Triple) (ws' : List Bool), ws'.length = bs.length → total bs ws x ≤ total bs ws' x'

theorem gadget_projection (bs : List Triple) (h : ∃ x0, hits bs x0 = 0) :
    ∀ x, ProjectedLeast bs x ↔ hits bs x = 0 := by
  obtain ⟨x0, h0⟩ := h
  intro x
  constructor
  · rintro ⟨ws, hl, least⟩
    obtain ⟨ws0, hl0, ht0⟩ := total_best bs x0
    have a := least x0 ws0 hl0
    have b := total_bound bs ws x hl
    omega
  · intro hx
    obtain ⟨ws, hl, ht⟩ := total_best bs x
    refine ⟨ws, hl, fun x' ws' hl' => ?_⟩
    have := total_bound bs ws' x' hl'
    omega

def cube : List Triple :=
  [(false, false, false), (false, false, true), (false, true, false), (false, true, true),
   (true, false, false), (true, false, true), (true, true, false), (true, true, true)]

theorem hits_cube : ∀ x : Triple, hits cube x = 1 := by
  intro x
  obtain ⟨a, b, c⟩ := x
  cases a <;> cases b <;> cases c <;> decide

theorem hits_filter (f : Triple → Bool) (x : Triple) :
    ∀ l : List Triple, hits (l.filter f) x = if f x then hits l x else 0
  | [] => by simp [hits]
  | b :: bs => by
    have ih := hits_filter f x bs
    by_cases hb : x = b
    · subst hb
      cases hf : f x <;> simp [List.filter, hits, hf, ih]
    · cases hf : f b <;> simp [List.filter, hits, hf, hb, ih]

/-- The excluded states of a relation on three distinctions. -/
def excludedOf (r : Triple → Bool) : List Triple := cube.filter (fun x => !r x)

theorem hits_excluded (r : Triple → Bool) (x : Triple) :
    hits (excludedOf r) x = if r x then 0 else 1 := by
  rw [excludedOf, hits_filter, hits_cube]
  cases r x <;> rfl

/-- Every relation on three distinctions with an allowed state, every knot among
them, is the projection of the least set of two-literal clauses with hidden
variables. -/
theorem every_relation_by_gadgets (r : Triple → Bool) (h : ∃ x0, r x0 = true) :
    ∀ x, ProjectedLeast (excludedOf r) x ↔ r x = true := by
  obtain ⟨x0, h0⟩ := h
  have hx0 : hits (excludedOf r) x0 = 0 := by rw [hits_excluded, h0]; rfl
  intro x
  rw [gadget_projection _ ⟨x0, hx0⟩ x, hits_excluded]
  cases r x <;> simp

/-! ## Triangles, checked by evaluation -/

/-- Number of broken preferences on a triangle: `differ01` says whether the pair
`0, 1` should differ (otherwise agree), and so on; `w01` weights that pair. -/
def triangleEnergy (differ01 differ02 differ12 : Bool) (w01 : Nat) (x : Triple) : Nat :=
  w01 * (if (x.1 != x.2.1) == differ01 then 0 else 1)
    + (if (x.1 != x.2.2) == differ02 then 0 else 1)
    + (if (x.2.1 != x.2.2) == differ12 then 0 else 1)

def leastOf (E : Triple → Nat) (x : Triple) : Bool := cube.all (fun y => decide (E x ≤ E y))

def strictOf (E : Triple → Nat) (x : Triple) : Bool := E x == 0

/-- K1–K3 on three distinctions, as a computation. -/
def isKnot3 (r : Triple → Bool) : Bool :=
  cube.any (fun x => !r x) &&
    cube.all (fun x => r x || r (!x.1, x.2.1, x.2.2)) &&
    cube.all (fun x => r x || r (x.1, !x.2.1, x.2.2)) &&
    cube.all (fun x => r x || r (x.1, x.2.1, !x.2.2))

def notAllEqual (x : Triple) : Bool := !((x.1 == x.2.1) && (x.2.1 == x.2.2))

/-- All three pairs should differ: nothing breaks no rule, and the six states
that break exactly one form the not-all-equal knot. -/
theorem frustrated_triangle :
    cube.all (fun x => !strictOf (triangleEnergy true true true 1) x) = true ∧
    cube.all (fun x => leastOf (triangleEnergy true true true 1) x == notAllEqual x) = true ∧
    isKnot3 (leastOf (triangleEnergy true true true 1)) = true := by decide

/-- A triangle whose preferences can all hold has a least set that is not a knot;
one with an odd number of "differ"s has a knot. -/
theorem triangles_knot_iff_frustrated : ∀ d01 d02 d12 : Bool,
    isKnot3 (leastOf (triangleEnergy d01 d02 d12 1)) = (d01 ^^ d02 ^^ d12) := by decide

/-- Weighting one preference twice breaks the knot: competition depends on the
weights, not only on which rules there are. -/
theorem weighted_triangle_not_knot :
    isKnot3 (leastOf (triangleEnergy true true true 2)) = false := by decide

end CompetitionKernel
