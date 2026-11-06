/-!
# What permutation contact remembers (HOLES-COHOMOLOGY-20261019-001B-P001)

A loop passes a witness through a list of transfers and closes when the
witness comes back to itself. With permutation contact each transfer is the
graph of a map, and a loop closes exactly when the composed map has a fixed
point (`loop_rule`).

A bouquet is a family of loops that share one base witness. Each loop has a
selector: unselected, its holonomy is the identity; selected, it is `h i`.
Forgetting every witness leaves a relation on the selectors (`bouquet_rule`).
Its shape, the sets of selectors on which it allows every pattern, is the
nerve of the holonomies' fixed-point sets (`shape_is_nerve`). On a minimal
non-face it excludes exactly one pattern, every loop selected
(`minimal_nonface_excludes_only_all`), so a minimal non-face of three or more
loops is a knot under the forgetting reading: K1, K2 and K3
(`minimal_nonface_is_knot`). Two loops form a tie, three or more a knot among
loops.

Free contact, where a holonomy that fixes one value fixes all, never binds two
loops (`free_contact_binds_nothing`). A knot among `k` loops needs at least
`k + 1` witness values (`knot_needs_more_values`), and the star transpositions
on `k + 1` values are one (`star_is_knot`). Every simplicial complex is the
nerve of the fixed-point sets of some involutions
(`every_complex_is_a_nerve`).

Core Lean 4 only; no Mathlib.
-/

namespace LoopNerve

/-! ## Loops -/

/-- A witness passes along a list of transfers from `a` to `b`. -/
def Path {W : Type} : List (W → W → Prop) → W → W → Prop
  | [], a, b => a = b
  | T :: rest, a, b => ∃ m, T a m ∧ Path rest m b

/-- A loop closes when some witness value returns to itself. -/
def Closes {W : Type} (Ts : List (W → W → Prop)) : Prop := ∃ a, Path Ts a a

/-- Apply a list of maps in order. -/
def run {W : Type} : List (W → W) → W → W
  | [], a => a
  | f :: rest, a => run rest (f a)

/-- Permutation contact: the witness out is the image of the witness in. -/
def graphOf {W : Type} (f : W → W) : W → W → Prop := fun a b => b = f a

theorem path_graph {W : Type} (fs : List (W → W)) (a b : W) :
    Path (fs.map graphOf) a b ↔ b = run fs a := by
  induction fs generalizing a with
  | nil => simp only [List.map_nil, Path, run]; exact eq_comm
  | cons f rest ih =>
    simp only [List.map_cons, Path, run, graphOf]
    constructor
    · rintro ⟨m, hm, h⟩
      subst hm
      exact (ih _).1 h
    · intro h
      exact ⟨f a, rfl, (ih _).2 h⟩

/-- (1a) A loop of permutation contact closes exactly when the composed map has a fixed point. -/
theorem loop_rule {W : Type} (fs : List (W → W)) :
    Closes (fs.map graphOf) ↔ ∃ a, run fs a = a := by
  constructor
  · rintro ⟨a, h⟩
    exact ⟨a, ((path_graph fs a a).1 h).symm⟩
  · rintro ⟨a, h⟩
    exact ⟨a, (path_graph fs a a).2 h.symm⟩

/-! ## Bouquets and selectors -/

/-- Loops sharing one base witness; loop `i` passes it through `loop i (s i)`. -/
def Bouquet {ι W : Type} (loop : ι → Bool → List (W → W)) (s : ι → Bool) : Prop :=
  ∃ u, ∀ i, Path ((loop i (s i)).map graphOf) u u

/-- The composite on selectors, written with holonomies. -/
def Sel {ι W : Type} (h : ι → W → W) (s : ι → Bool) : Prop :=
  ∃ u, ∀ i, s i = true → h i u = u

/-- (1b) If unselected loops have identity holonomy and selected ones `h i`, the bouquet allows a
selector pattern exactly when the selected holonomies share a fixed point. -/
theorem bouquet_rule {ι W : Type} (loop : ι → Bool → List (W → W)) (h : ι → W → W)
    (hoff : ∀ i a, run (loop i false) a = a) (hon : ∀ i a, run (loop i true) a = h i a)
    (s : ι → Bool) : Bouquet loop s ↔ Sel h s := by
  constructor
  · rintro ⟨u, hu⟩
    refine ⟨u, fun i hi => ?_⟩
    have e := (path_graph _ u u).1 (hu i)
    rw [hi, hon] at e
    exact e.symm
  · rintro ⟨u, hu⟩
    refine ⟨u, fun i => (path_graph _ u u).2 ?_⟩
    cases hs : s i with
    | false => rw [hoff]
    | true => rw [hon, hu i hs]

/-! ## Shapes are nerves -/

/-- The selectors in `S` are free: every pattern on them extends to an allowed pattern. -/
def Free {ι W : Type} (h : ι → W → W) (S : ι → Prop) : Prop :=
  ∀ t : ι → Bool, ∃ s, (∀ i, S i → s i = t i) ∧ Sel h s

/-- `S` is a face of the nerve: the holonomies of the loops in `S` share a fixed point. -/
def Face {ι W : Type} (h : ι → W → W) (S : ι → Prop) : Prop :=
  ∃ u, ∀ i, S i → h i u = u

/-- (2a) The shape of the selector composite is the nerve of the fixed-point sets. -/
theorem shape_is_nerve {ι W : Type} (h : ι → W → W) (S : ι → Prop) : Free h S ↔ Face h S := by
  classical
  constructor
  · intro hf
    obtain ⟨s, hs, u, hu⟩ := hf (fun _ => true)
    exact ⟨u, fun i hi => hu i (hs i hi)⟩
  · rintro ⟨u, hu⟩ t
    refine ⟨fun i => if S i then t i else false, fun i hi => by simp [hi], u, fun i hi => ?_⟩
    by_cases hS : S i
    · exact hu i hS
    · simp [hS] at hi

/-- No fixed point is shared by the loops of `S`, but one is shared once any one loop is left out. -/
def MinimalNonFace {ι W : Type} (h : ι → W → W) (S : ι → Prop) : Prop :=
  ¬ Face h S ∧ ∀ j, S j → Face h (fun i => S i ∧ i ≠ j)

/-- The selector composite seen on `S`: the patterns on `S` that extend to an allowed pattern. -/
def Proj {ι W : Type} (h : ι → W → W) (S : ι → Prop) (t : ι → Bool) : Prop :=
  ∃ s, (∀ i, S i → s i = t i) ∧ Sel h s

/-- (2b) On a minimal non-face exactly one pattern is excluded: every loop of `S` selected. -/
theorem minimal_nonface_excludes_only_all {ι W : Type} (h : ι → W → W) (S : ι → Prop)
    (hm : MinimalNonFace h S) (t : ι → Bool) : Proj h S t ↔ ¬ ∀ i, S i → t i = true := by
  classical
  constructor
  · rintro ⟨s, hs, u, hu⟩ hall
    exact hm.1 ⟨u, fun i hi => hu i ((hs i hi).trans (hall i hi))⟩
  · intro hnot
    have hex : ∃ j, S j ∧ t j = false := by
      apply Classical.byContradiction
      intro hno
      apply hnot
      intro i hi
      cases ht : t i with
      | true => rfl
      | false => exact absurd ⟨i, hi, ht⟩ hno
    obtain ⟨j, hj, htj⟩ := hex
    obtain ⟨u, hu⟩ := hm.2 j hj
    refine ⟨fun i => if S i then t i else false, fun i hi => by simp [hi], u, fun i hi => ?_⟩
    by_cases hS : S i
    · have hti : t i = true := by simpa [hS] using hi
      have hij : i ≠ j := fun e => by
        rw [e, htj] at hti
        cases hti
      exact hu i ⟨hS, hij⟩
    · simp [hS] at hi

/-- (2c) With at least one witness value, a minimal non-face read as a relation on its selectors is
a knot under the forgetting reading: constrained as a whole (K1), unconstrained once any one of its
loops is forgotten (K2), and some state allowed (K3). With two loops this is a tie, with three or
more a knot among loops. -/
theorem minimal_nonface_is_knot {ι W : Type} (h : ι → W → W) (S : ι → Prop) (w : W)
    (hm : MinimalNonFace h S) :
    (∃ t, ¬ Proj h S t) ∧ (∀ j, S j → Free h (fun i => S i ∧ i ≠ j)) ∧ (∃ t, Proj h S t) := by
  refine ⟨⟨fun _ => true, fun hp => ?_⟩, fun j hj => (shape_is_nerve h _).2 (hm.2 j hj),
    ⟨fun _ => false, ?_⟩⟩
  · exact ((minimal_nonface_excludes_only_all h S hm _).1 hp) (fun _ _ => rfl)
  · refine (minimal_nonface_excludes_only_all h S hm _).2 (fun hall => ?_)
    apply hm.1
    refine ⟨w, fun i hi => ?_⟩
    cases hall i hi

/-! ## Free contact binds nothing -/

/-- A holonomy acts freely when fixing one value means fixing every value. -/
def ActsFreely {W : Type} (f : W → W) : Prop := ∀ u, f u = u → ∀ v, f v = v

/-- (3) Under free contact a minimal non-face has at most one loop: no ties, no knots among loops. -/
theorem free_contact_binds_nothing {ι W : Type} (h : ι → W → W) (hfree : ∀ i, ActsFreely (h i))
    (S : ι → Prop) (hm : MinimalNonFace h S) : ∀ i j, S i → S j → i = j := by
  intro i j hi hj
  apply Classical.byContradiction
  intro hij
  obtain ⟨u, hu⟩ := hm.2 i hi
  obtain ⟨v, hv⟩ := hm.2 j hj
  apply hm.1
  refine ⟨u, fun l hl => ?_⟩
  by_cases hli : l = i
  · have hlj : l ≠ j := fun e => hij (hli.symm.trans e)
    exact hfree l v (hv l ⟨hl, hlj⟩) u
  · exact hu l ⟨hl, hli⟩

/-! ## A knot among `k` loops needs `k + 1` values -/

theorem nodup_length_le : ∀ (n : Nat) (l : List Nat), l.Nodup → (∀ x ∈ l, x < n) → l.length ≤ n
  | 0, [], _, _ => Nat.le_refl 0
  | 0, x :: _, _, hb => absurd (hb x (List.mem_cons_self ..)) (Nat.not_lt_zero x)
  | n + 1, l, hnd, hb => by
    have hb' : ∀ x ∈ l.erase n, x < n := by
      intro x hx
      have hx' := (List.Nodup.mem_erase_iff hnd).1 hx
      have := hb x hx'.2
      omega
    have ih := nodup_length_le n (l.erase n) (List.Nodup.erase n hnd) hb'
    rw [List.length_erase] at ih
    split at ih <;> omega

/-- The values `f (m - 1), ..., f 0`. -/
def vals (f : Nat → Nat) : Nat → List Nat
  | 0 => []
  | m + 1 => f m :: vals f m

theorem mem_vals (f : Nat → Nat) (x : Nat) : ∀ m, x ∈ vals f m ↔ ∃ i, i < m ∧ f i = x
  | 0 => by simp [vals]
  | m + 1 => by
    rw [vals, List.mem_cons, mem_vals f x m]
    constructor
    · rintro (e | ⟨i, hi, hfi⟩)
      · exact ⟨m, Nat.lt_succ_self m, e.symm⟩
      · exact ⟨i, Nat.lt_succ_of_lt hi, hfi⟩
    · rintro ⟨i, hi, hfi⟩
      by_cases him : i = m
      · subst him
        exact Or.inl hfi.symm
      · exact Or.inr ⟨i, by omega, hfi⟩

theorem length_vals (f : Nat → Nat) : ∀ m, (vals f m).length = m
  | 0 => rfl
  | m + 1 => by simp [vals, length_vals f m]

theorem nodup_vals (f : Nat → Nat) (m : Nat) (hinj : ∀ i j, i < m → j < m → f i = f j → i = j) :
    (vals f m).Nodup := by
  induction m with
  | zero => simp [vals]
  | succ m ih =>
    rw [vals, List.nodup_cons]
    refine ⟨fun hmem => ?_, ih (fun i j hi hj e => hinj i j (by omega) (by omega) e)⟩
    obtain ⟨i, hi, hfi⟩ := (mem_vals f (f m) m).1 hmem
    have := hinj i m (by omega) (by omega) hfi
    omega

/-- Pigeonhole: `m` distinct values below `n` need `m ≤ n`. -/
theorem pigeonhole (f : Nat → Nat) (m n : Nat) (hb : ∀ i, i < m → f i < n)
    (hinj : ∀ i j, i < m → j < m → f i = f j → i = j) : m ≤ n := by
  have hl := nodup_length_le n (vals f m) (nodup_vals f m hinj) (fun x hx => by
    obtain ⟨i, hi, rfl⟩ := (mem_vals f x m).1 hx
    exact hb i hi)
  rwa [length_vals] at hl

/-- `k` loops on `n` values form a knot among loops: every `k - 1` of them share a fixed point, and
all `k` do not. For `k = 2` this is a tie. -/
def KnotAmong {k n : Nat} (h : Fin k → Fin n → Fin n) : Prop :=
  ¬ Face h (fun _ => True) ∧ ∀ j, Face h (fun i => i ≠ j)

/-- (4a) A knot among `k ≥ 1` loops of permutation contact needs at least `k + 1` witness values. -/
theorem knot_needs_more_values {k n : Nat} (hk : 1 ≤ k) (h : Fin k → Fin n → Fin n)
    (hinj : ∀ i a b, h i a = h i b → a = b) (hknot : KnotAmong h) : k + 1 ≤ n := by
  classical
  have hp : ∀ j : Fin k, ∃ p : Fin n, (∀ i, i ≠ j → h i p = p) ∧ h j p ≠ p := by
    intro j
    obtain ⟨p, hp⟩ := hknot.2 j
    refine ⟨p, hp, fun hj => hknot.1 ⟨p, fun i _ => ?_⟩⟩
    by_cases hij : i = j
    · rw [hij]
      exact hj
    · exact hp i hij
  let p : Fin k → Fin n := fun j => Classical.choose (hp j)
  have hpfix : ∀ i j, i ≠ j → h i (p j) = p j := fun i j hij => (Classical.choose_spec (hp j)).1 i hij
  have hpmove : ∀ j, h j (p j) ≠ p j := fun j => (Classical.choose_spec (hp j)).2
  have hpinj : ∀ i j, p i = p j → i = j := by
    intro i j e
    apply Classical.byContradiction
    intro hij
    have h1 := hpfix j i (fun e' => hij e'.symm)
    rw [e] at h1
    exact hpmove j h1
  let j0 : Fin k := ⟨0, hk⟩
  let q : Fin n := h j0 (p j0)
  have hq : ∀ j, q ≠ p j := by
    intro j e
    by_cases hj : j = j0
    · rw [hj] at e
      exact hpmove j0 e
    · have h1 := hpfix j0 j (fun e' => hj e'.symm)
      have h2 : h j0 (p j0) = h j0 (p j) := by
        rw [h1]
        exact e
      exact hj (hpinj _ _ (hinj _ _ _ h2)).symm
  let f : Nat → Nat := fun i => if hi : 0 < i ∧ i ≤ k then (p ⟨i - 1, by omega⟩).val else q.val
  have hb : ∀ i, i < k + 1 → f i < n := by
    intro i _
    simp only [f]
    split
    · exact (p _).isLt
    · exact q.isLt
  have hf : ∀ i j, i < k + 1 → j < k + 1 → f i = f j → i = j := by
    intro i j hi hj e
    simp only [f] at e
    split at e <;> split at e
    · next h1 h2 =>
      have := hpinj _ _ (Fin.ext e)
      simp only [Fin.mk.injEq] at this
      omega
    · next h1 h2 => exact absurd (Fin.ext e.symm) (hq _)
    · next h1 h2 => exact absurd (Fin.ext e) (hq _)
    · next h1 h2 => omega
  exact pigeonhole f (k + 1) n hb hf

/-- The star transposition exchanging `j` with the last value `k`, on `k + 1` values. -/
def star (k : Nat) (j : Fin k) (x : Fin (k + 1)) : Fin (k + 1) :=
  if x.val = j.val then ⟨k, Nat.lt_succ_self k⟩
  else if x.val = k then ⟨j.val, Nat.lt_succ_of_lt j.isLt⟩
  else x

theorem star_val (k : Nat) (j : Fin k) (x : Fin (k + 1)) :
    (star k j x).val = if x.val = j.val then k else if x.val = k then j.val else x.val := by
  unfold star
  have hkj : ¬ k = j.val := by have := j.isLt; omega
  by_cases h1 : x.val = j.val
  · simp [h1]
  · by_cases h2 : x.val = k
    · simp [h2, hkj]
    · simp [h1, h2]

theorem star_star (k : Nat) (j : Fin k) (x : Fin (k + 1)) : star k j (star k j x) = x := by
  apply Fin.ext
  rw [star_val, star_val]
  have hkj : ¬ k = j.val := by have := j.isLt; omega
  by_cases h1 : x.val = j.val
  · simp [h1, hkj]
  · by_cases h2 : x.val = k
    · simp [h2]
    · simp [h1, h2]

theorem star_injective (k : Nat) (j : Fin k) (a b : Fin (k + 1)) (e : star k j a = star k j b) :
    a = b := by
  rw [← star_star k j a, ← star_star k j b, e]

/-- (4b) The star transpositions on `k + 1` values are a knot among `k ≥ 1` loops. -/
theorem star_is_knot (k : Nat) (hk : 1 ≤ k) : KnotAmong (star k) := by
  constructor
  · rintro ⟨u, hu⟩
    by_cases hu' : u.val < k
    · have e := congrArg Fin.val (hu ⟨u.val, hu'⟩ trivial)
      rw [star_val] at e
      simp only [if_true] at e
      omega
    · have e := congrArg Fin.val (hu ⟨0, hk⟩ trivial)
      rw [star_val] at e
      have hu2 : u.val = k := by
        have := u.isLt
        omega
      have hk0 : ¬ k = 0 := by omega
      simp only [hu2, hk0, if_false, if_true] at e
      omega
  · intro j
    refine ⟨⟨j.val, Nat.lt_succ_of_lt j.isLt⟩, fun i hij => ?_⟩
    apply Fin.ext
    rw [star_val]
    have hne : j.val ≠ i.val := fun e => hij (Fin.ext e).symm
    have hlt : j.val ≠ k := Nat.ne_of_lt j.isLt
    simp only [hne, hlt, if_false]

/-- Three loops cannot form a knot among loops on three witness values, and four values suffice:
the star transpositions (03), (13), (23). -/
theorem three_loops_need_four_values (h : Fin 3 → Fin 3 → Fin 3) (hinj : ∀ i a b, h i a = h i b → a = b) :
    ¬ KnotAmong h :=
  fun hknot => absurd (knot_needs_more_values (by decide) h hinj hknot) (by decide)

theorem four_values_knot_three_loops : KnotAmong (star 3) := star_is_knot 3 (by decide)

/-- With two witness values no two loops tie. -/
theorem boolean_contact_never_ties (h : Fin 2 → Fin 2 → Fin 2) (hinj : ∀ i a b, h i a = h i b → a = b) :
    ¬ KnotAmong h :=
  fun hknot => absurd (knot_needs_more_values (by decide) h hinj hknot) (by decide)

/-! ## Every complex is a nerve -/

/-- A family of sets of loops, given as selector patterns, closed under taking subsets. -/
def DownClosed {ι : Type} (N : (ι → Bool) → Prop) : Prop :=
  ∀ F G : ι → Bool, N F → (∀ i, G i = true → F i = true) → N G

/-- On the values (face, tag), loop `i` fixes the faces of `N` that contain `i` and flips the tag of
everything else. -/
def flip {ι : Type} (N : (ι → Bool) → Prop) [DecidablePred N] (i : ι) (x : (ι → Bool) × Bool) :
    (ι → Bool) × Bool :=
  if N x.1 ∧ x.1 i = true then x else (x.1, !x.2)

theorem flip_involutive {ι : Type} (N : (ι → Bool) → Prop) [DecidablePred N] (i : ι)
    (x : (ι → Bool) × Bool) : flip N i (flip N i x) = x := by
  unfold flip
  by_cases hc : N x.1 ∧ x.1 i = true
  · simp [hc]
  · simp [hc]

/-- (5) Every simplicial complex (a down-closed family containing the empty set) is the nerve of the
fixed-point sets of a family of involutions: a set of loops shares a fixed point exactly when it is
a face. With `shape_is_nerve`, every complex is the shape of a bouquet of loops. -/
theorem every_complex_is_a_nerve {ι : Type} (N : (ι → Bool) → Prop) [DecidablePred N]
    (hdown : DownClosed N) (hempty : N (fun _ => false)) (S : ι → Bool) :
    Face (fun i => flip N i) (fun i => S i = true) ↔ N S := by
  classical
  constructor
  · rintro ⟨⟨F, b⟩, hu⟩
    by_cases hne : ∃ i, S i = true
    · obtain ⟨i, hi⟩ := hne
      have hfix := hu i hi
      have hNF : N F := by
        unfold flip at hfix
        by_cases hc : N F ∧ F i = true
        · exact hc.1
        · simp [hc] at hfix
      refine hdown F S hNF (fun j hj => ?_)
      have hfj := hu j hj
      unfold flip at hfj
      by_cases hc : N F ∧ F j = true
      · exact hc.2
      · simp [hc] at hfj
    · have hS : S = fun _ => false := by
        funext i
        cases hsi : S i with
        | false => rfl
        | true => exact absurd ⟨i, hsi⟩ hne
      rw [hS]
      exact hempty
  · intro hS
    refine ⟨(S, true), fun i hi => ?_⟩
    unfold flip
    simp [hS, hi]

end LoopNerve
