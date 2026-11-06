/-
The ring theorem: which knots remember a loop (ticket KNOT-LOOPS-20261019-001B).

A copy of a knot is a link: one witness distinction passed in, one passed out,
and some middle distinctions. For one value `m` of its middle distinctions, a
link allows some (witness in, witness out) pairs: its transfer at `m`. A ring
joins copies so that each passes its witness out to the next copy's witness
in. Once the witnesses are forgotten, the ring allows a pattern of middle
values when some witness assignment closes the loop.

Under the forgetting reading of K1–K3 a knot's excluded states contain no two
neighbours, states that differ in one distinction. For links with that
property:
* `transfer_cases`: each transfer is a permutation (identity or swap) or
  misses at most one pair;
* `ring_excludes_iff`: a ring excludes a pattern exactly when every transfer
  along it is a permutation and an odd number of them swap;
* `ring_one_flip`: two patterns that differ in one middle distinction are
  never both excluded, so a ring composes into a knot or into nothing;
* `all_permutations_iff_parity`: a link's transfers are all permutations
  exactly when it is a parity relation;
* `ring_memory`: a ring of `k ≥ 1` copies of one link excludes some pattern
  exactly when the link has a swap transfer and either `k` is odd or the link
  also has an identity transfer.
-/
namespace RingKernel

/-! ## Transfers and their composition -/

/-- Which (witness in, witness out) pairs are allowed. -/
abbrev Transfer := Bool → Bool → Bool

def idT : Transfer := fun a b => a == b
def swapT : Transfer := fun a b => a != b

/-- The identity or the swap of a bit. -/
def IsPerm (T : Transfer) : Prop := T = idT ∨ T = swapT

/-- Misses at most one pair. -/
def Thick (T : Transfer) : Prop :=
  ∀ a b c d, T a b = false → T c d = false → a = c ∧ b = d

/-- The transfers a knot link can have. -/
def KnotT (T : Transfer) : Prop := IsPerm T ∨ Thick T

/-- Whether a permutation transfer swaps. -/
def swapBit (T : Transfer) : Bool := T false true

/-- Relational composition along a list, first transfer first. -/
def comp : List Transfer → Transfer
  | [] => idT
  | T :: rest => fun a c => (T a false && comp rest false c) || (T a true && comp rest true c)

/-- Some witness assignment closes the loop. -/
def closes (L : List Transfer) : Bool := comp L false false || comp L true true

/-- The parity of the number of swaps. -/
def swaps : List Transfer → Bool
  | [] => false
  | T :: rest => swapBit T ^^ swaps rest

theorem comp_append (A B : List Transfer) (a c : Bool) :
    comp (A ++ B) a c = ((comp A a false && comp B false c) || (comp A a true && comp B true c)) := by
  induction A generalizing a with
  | nil => cases a <;> simp [comp, idT]
  | cons T A ih =>
    show ((T a false && comp (A ++ B) false c) || (T a true && comp (A ++ B) true c)) = _
    rw [ih false, ih true]
    simp only [comp]
    generalize T a false = t0
    generalize T a true = t1
    generalize comp A false false = p00
    generalize comp A false true = p01
    generalize comp A true false = p10
    generalize comp A true true = p11
    generalize comp B false c = q0
    generalize comp B true c = q1
    cases t0 <;> cases t1 <;> cases p00 <;> cases p01 <;> cases p10 <;> cases p11 <;>
      cases q0 <;> cases q1 <;> rfl

theorem closes_rotate (A B : List Transfer) : closes (A ++ B) = closes (B ++ A) := by
  simp only [closes, comp_append]
  generalize comp A false false = a00
  generalize comp A false true = a01
  generalize comp A true false = a10
  generalize comp A true true = a11
  generalize comp B false false = b00
  generalize comp B false true = b01
  generalize comp B true false = b10
  generalize comp B true true = b11
  cases a00 <;> cases a01 <;> cases a10 <;> cases a11 <;> cases b00 <;> cases b01 <;>
    cases b10 <;> cases b11 <;> rfl

theorem comp_perms (L : List Transfer) (h : ∀ T ∈ L, IsPerm T) :
    comp L = if swaps L then swapT else idT := by
  induction L with
  | nil => rfl
  | cons T L ih =>
    have hT := h T (List.mem_cons_self ..)
    have hL : ∀ U ∈ L, IsPerm U := fun U hU => h U (List.mem_cons_of_mem _ hU)
    funext a c
    simp only [comp, swaps]
    rw [ih hL]
    rcases hT with rfl | rfl <;> by_cases hs : swaps L = true <;> cases a <;> cases c <;>
      simp [hs, idT, swapT, swapBit]

theorem closes_perms (L : List Transfer) (h : ∀ T ∈ L, IsPerm T) : closes L = !swaps L := by
  rw [closes, comp_perms L h]
  cases swaps L <;> rfl

/-! ## A thick transfer always lets a loop close -/

def NoZeroCol (T : Transfer) : Prop := ∀ c, ∃ a, T a c = true

theorem knotT_noZeroCol (T : Transfer) (h : KnotT T) : NoZeroCol T := by
  intro c
  rcases h with (rfl | rfl) | ht
  · exact ⟨c, by cases c <;> rfl⟩
  · exact ⟨!c, by cases c <;> rfl⟩
  · cases h0 : T false c with
    | false =>
      cases h1 : T true c with
      | false => exact absurd (ht false c true c h0 h1).1 (by decide)
      | true => exact ⟨true, h1⟩
    | true => exact ⟨false, h0⟩

theorem comp_noZeroCol (L : List Transfer) (h : ∀ T ∈ L, NoZeroCol T) : NoZeroCol (comp L) := by
  induction L with
  | nil => intro c; exact ⟨c, by cases c <;> rfl⟩
  | cons T L ih =>
    intro c
    obtain ⟨b, hb⟩ := ih (fun U hU => h U (List.mem_cons_of_mem _ hU)) c
    obtain ⟨a, ha⟩ := h T (List.mem_cons_self ..) b
    refine ⟨a, ?_⟩
    simp only [comp]
    cases b <;> simp [ha, hb]

theorem closes_of_thick_head (T : Transfer) (R : List Transfer) (ht : Thick T)
    (hR : NoZeroCol (comp R)) : closes (T :: R) = true := by
  obtain ⟨y0, h0⟩ := hR false
  obtain ⟨y1, h1⟩ := hR true
  simp only [closes, comp]
  cases hT0 : T false y0 <;> cases hT1 : T true y1
  · exact absurd (ht false y0 true y1 hT0 hT1).1 (by decide)
  · cases y1 <;> simp [hT1, h1]
  · cases y0 <;> simp [hT0, h0]
  · cases y0 <;> simp [hT0, h0]

theorem closes_of_some_thick (L : List Transfer) (hk : ∀ T ∈ L, KnotT T) (T : Transfer)
    (hT : T ∈ L) (ht : Thick T) : closes L = true := by
  obtain ⟨A, B, rfl⟩ := List.append_of_mem hT
  rw [closes_rotate]
  show closes (T :: (B ++ A)) = true
  apply closes_of_thick_head T (B ++ A) ht
  apply comp_noZeroCol
  intro U hU
  apply knotT_noZeroCol U
  apply hk U
  simp only [List.mem_append, List.mem_cons] at hU ⊢
  rcases hU with h | h
  · exact Or.inr (Or.inr h)
  · exact Or.inl h

/-- (2) on lists of knot transfers. -/
theorem closes_false_iff (L : List Transfer) (hk : ∀ T ∈ L, KnotT T) :
    closes L = false ↔ (∀ T ∈ L, IsPerm T) ∧ swaps L = true := by
  constructor
  · intro hc
    have hp : ∀ T ∈ L, IsPerm T := by
      intro T hT
      rcases hk T hT with hp | ht
      · exact hp
      · have h := closes_of_some_thick L hk T hT ht
        rw [hc] at h
        cases h
    refine ⟨hp, ?_⟩
    have h := closes_perms L hp
    rw [hc] at h
    revert h
    cases swaps L <;> simp
  · rintro ⟨hp, hs⟩
    rw [closes_perms L hp, hs]
    rfl

/-! ## Links: knots with a witness in and a witness out -/

/-- Flip middle distinction `n`. -/
def flipAt : List Bool → Nat → List Bool
  | [], _ => []
  | b :: l, 0 => (!b) :: l
  | b :: l, n + 1 => b :: flipAt l n

def parity : List Bool → Bool
  | [] => false
  | b :: l => b ^^ parity l

theorem length_flipAt (l : List Bool) (n : Nat) : (flipAt l n).length = l.length := by
  induction l generalizing n with
  | nil => rfl
  | cons b l ih => cases n <;> simp [flipAt, ih]

/-- A link with `d` middle distinctions whose excluded states contain no two
neighbours (the forgetting reading of K1–K3; a knot when it excludes a state). -/
structure KnotLink (d : Nat) where
  allowed : Bool → List Bool → Bool → Bool
  sep_in : ∀ a m b, m.length = d → allowed a m b = false → allowed (!a) m b = false → False
  sep_out : ∀ a m b, m.length = d → allowed a m b = false → allowed a m (!b) = false → False
  sep_mid : ∀ a m b n, m.length = d → n < d → allowed a m b = false →
    allowed a (flipAt m n) b = false → False

def KnotLink.transfer {d : Nat} (L : KnotLink d) (m : List Bool) : Transfer :=
  fun a b => L.allowed a m b

/-- A transfer given by its four values. -/
def tbl (x00 x01 x10 x11 : Bool) : Transfer :=
  fun a b => if a then (if b then x11 else x10) else (if b then x01 else x00)

theorem tbl_eta (T : Transfer) : T = tbl (T false false) (T false true) (T true false) (T true true) := by
  funext a b
  cases a <;> cases b <;> rfl

theorem tbl_cases (x00 x01 x10 x11 : Bool)
    (h1 : ¬ (x00 = false ∧ x10 = false)) (h2 : ¬ (x01 = false ∧ x11 = false))
    (h3 : ¬ (x00 = false ∧ x01 = false)) (h4 : ¬ (x10 = false ∧ x11 = false)) :
    KnotT (tbl x00 x01 x10 x11) := by
  cases x00 <;> cases x01 <;> cases x10 <;> cases x11 <;> simp at h1 h2 h3 h4 <;>
    first
    | (left; left; funext a b; cases a <;> cases b <;> rfl)
    | (left; right; funext a b; cases a <;> cases b <;> rfl)
    | (right; intro a b c d ha hc; cases a <;> cases b <;> cases c <;> cases d <;> simp_all [tbl])

/-- (1) Each transfer of a knot link is a permutation or misses at most one pair. -/
theorem transfer_cases {d : Nat} (L : KnotLink d) (m : List Bool) (hm : m.length = d) :
    KnotT (L.transfer m) := by
  rw [tbl_eta (L.transfer m)]
  apply tbl_cases
  · rintro ⟨h0, h1⟩; exact L.sep_in false m false hm h0 h1
  · rintro ⟨h0, h1⟩; exact L.sep_in false m true hm h0 h1
  · rintro ⟨h0, h1⟩; exact L.sep_out false m false hm h0 h1
  · rintro ⟨h0, h1⟩; exact L.sep_out true m false hm h0 h1

/-- Neighbouring middle values with permutation transfers swap differently. -/
theorem perm_flip_differ {d : Nat} (L : KnotLink d) (m : List Bool) (hm : m.length = d)
    (n : Nat) (hn : n < d) (h1 : IsPerm (L.transfer m)) (h2 : IsPerm (L.transfer (flipAt m n))) :
    swapBit (L.transfer m) ≠ swapBit (L.transfer (flipAt m n)) := by
  rcases h1 with h1 | h1 <;> rcases h2 with h2 | h2
  · exfalso
    have e1 : L.allowed false m true = false := congrFun (congrFun h1 false) true
    have e2 : L.allowed false (flipAt m n) true = false := congrFun (congrFun h2 false) true
    exact L.sep_mid false m true n hm hn e1 e2
  · simp [swapBit, h1, h2, idT, swapT]
  · simp [swapBit, h1, h2, idT, swapT]
  · exfalso
    have e1 : L.allowed false m false = false := congrFun (congrFun h1 false) false
    have e2 : L.allowed false (flipAt m n) false = false := congrFun (congrFun h2 false) false
    exact L.sep_mid false m false n hm hn e1 e2

/-! ## Rings of copies -/

/-- A copy of a link with its middle values. -/
structure Copy where
  d : Nat
  link : KnotLink d
  mid : List Bool
  len : mid.length = d

def Copy.transfer (c : Copy) : Transfer := c.link.transfer c.mid

/-- The ring of these copies, in order, closes. -/
def ringCloses (cs : List Copy) : Bool := closes (cs.map Copy.transfer)

/-- (2) A ring excludes a pattern exactly when every transfer is a permutation and
an odd number of them swap. -/
theorem ring_excludes_iff (cs : List Copy) :
    ringCloses cs = false ↔ (∀ c ∈ cs, IsPerm c.transfer) ∧ swaps (cs.map Copy.transfer) = true := by
  have hk : ∀ T ∈ cs.map Copy.transfer, KnotT T := by
    intro T hT
    obtain ⟨c, _, rfl⟩ := List.mem_map.mp hT
    exact transfer_cases c.link c.mid c.len
  rw [ringCloses, closes_false_iff _ hk]
  constructor
  · rintro ⟨hp, hs⟩
    exact ⟨fun c hc => hp _ (List.mem_map.mpr ⟨c, hc, rfl⟩), hs⟩
  · rintro ⟨hp, hs⟩
    refine ⟨?_, hs⟩
    intro T hT
    obtain ⟨c, hc, rfl⟩ := List.mem_map.mp hT
    exact hp c hc

theorem swaps_append (A B : List Transfer) : swaps (A ++ B) = (swaps A ^^ swaps B) := by
  induction A with
  | nil => simp [swaps]
  | cons T A ih => simp [swaps, ih]

/-- The copy with middle distinction `n` flipped. -/
def Copy.flip (c : Copy) (n : Nat) : Copy :=
  ⟨c.d, c.link, flipAt c.mid n, by rw [length_flipAt, c.len]⟩

/-- (3) Two patterns that differ in one middle distinction are never both excluded:
the excluded patterns of a ring contain no two neighbours. -/
theorem ring_one_flip (A B : List Copy) (c : Copy) (n : Nat) (hn : n < c.d)
    (h1 : ringCloses (A ++ c :: B) = false) (h2 : ringCloses (A ++ c.flip n :: B) = false) : False := by
  rw [ring_excludes_iff] at h1 h2
  obtain ⟨p1, s1⟩ := h1
  obtain ⟨p2, s2⟩ := h2
  have hc : IsPerm c.transfer := p1 c (by simp)
  have hc' : IsPerm (c.flip n).transfer := p2 (c.flip n) (by simp)
  have hd := perm_flip_differ c.link c.mid c.len n hn hc hc'
  simp only [List.map_append, List.map_cons, swaps_append, swaps] at s1 s2
  change swapBit c.transfer ≠ swapBit (c.flip n).transfer at hd
  revert s1 s2 hd
  generalize swaps (A.map Copy.transfer) = p
  generalize swaps (B.map Copy.transfer) = q
  generalize swapBit c.transfer = u
  generalize swapBit (c.flip n).transfer = v
  cases p <;> cases q <;> cases u <;> cases v <;> simp

/-! ## Only parity keeps every middle value a permutation -/

theorem flip_parity_rule : ∀ (l : List Bool) (f : List Bool → Bool),
    (∀ l' n, l'.length = l.length → n < l'.length → f (flipAt l' n) = !f l') →
    f l = (f (List.replicate l.length false) ^^ parity l)
  | [], f, _ => by simp [parity]
  | b :: t, f, hf => by
    have hg : ∀ l' n, l'.length = t.length → n < l'.length →
        (fun s => f (false :: s)) (flipAt l' n) = !(fun s => f (false :: s)) l' := by
      intro l' n hl hn
      have h := hf (false :: l') (n + 1) (by simp [hl]) (by simp; omega)
      simpa [flipAt] using h
    have ih := flip_parity_rule t (fun s => f (false :: s)) hg
    simp only [List.length_cons, List.replicate, parity]
    cases b with
    | false => simpa using ih
    | true =>
      have h0 := hf (false :: t) 0 (by simp) (by simp)
      simp only [flipAt, Bool.not_false] at h0
      rw [h0, ih]
      cases f (false :: List.replicate t.length false) <;> cases parity t <;> rfl

theorem parity_flipAt (l : List Bool) (n : Nat) (h : n < l.length) : parity (flipAt l n) = !parity l := by
  induction l generalizing n with
  | nil => simp at h
  | cons b l ih =>
    cases n with
    | zero => simp only [flipAt, parity]; cases b <;> cases parity l <;> rfl
    | succ n =>
      simp only [flipAt, parity]
      rw [ih n (by simp at h; omega)]
      cases b <;> cases parity l <;> rfl

/-- A parity link: it allows a state exactly when the witnesses and middle values
have a fixed parity `c`. -/
def IsParityLink {d : Nat} (L : KnotLink d) : Prop :=
  ∃ c : Bool, ∀ a m b, m.length = d → L.allowed a m b = ((a ^^ b ^^ parity m) == c)

/-- (4) A knot link's transfers are all permutations exactly when it is a parity link. -/
theorem all_permutations_iff_parity {d : Nat} (L : KnotLink d) :
    (∀ m, m.length = d → IsPerm (L.transfer m)) ↔ IsParityLink L := by
  constructor
  · intro hp
    have rule : ∀ m, m.length = d → swapBit (L.transfer m) =
        (swapBit (L.transfer (List.replicate d false)) ^^ parity m) := by
      intro m hm
      have := flip_parity_rule m (fun l => swapBit (L.transfer l)) (by
        intro l' n hl hn
        have hl' : l'.length = d := by rw [hl, hm]
        have hd := perm_flip_differ L l' hl' n (by omega) (hp l' hl')
          (hp (flipAt l' n) (by rw [length_flipAt, hl']))
        revert hd
        cases swapBit (L.transfer l') <;> cases swapBit (L.transfer (flipAt l' n)) <;> simp)
      simpa [hm] using this
    refine ⟨swapBit (L.transfer (List.replicate d false)), ?_⟩
    intro a m b hm
    have hr := rule m hm
    rcases hp m hm with h | h
    · have hv : L.allowed a m b = (a == b) := congrFun (congrFun h a) b
      have hs : swapBit (L.transfer m) = false := by simp [swapBit, h, idT]
      rw [hv]
      rw [hs] at hr
      revert hr
      cases swapBit (L.transfer (List.replicate d false)) <;> cases parity m <;> cases a <;> cases b <;> simp
    · have hv : L.allowed a m b = (a != b) := congrFun (congrFun h a) b
      have hs : swapBit (L.transfer m) = true := by simp [swapBit, h, swapT]
      rw [hv]
      rw [hs] at hr
      revert hr
      cases swapBit (L.transfer (List.replicate d false)) <;> cases parity m <;> cases a <;> cases b <;> simp
  · rintro ⟨c, hc⟩ m hm
    cases hpm : (parity m == c)
    · right
      funext a b
      show L.allowed a m b = (a != b)
      rw [hc a m b hm]
      revert hpm
      cases parity m <;> cases c <;> cases a <;> cases b <;> simp
    · left
      funext a b
      show L.allowed a m b = (a == b)
      rw [hc a m b hm]
      revert hpm
      cases parity m <;> cases c <;> cases a <;> cases b <;> simp

/-! ## Which lengths of ring a link remembers -/

theorem swaps_replicate_swap (n : Nat) : swaps (List.replicate n swapT) = (n % 2 == 1) := by
  induction n with
  | zero => rfl
  | succ n ih =>
    simp only [List.replicate, swaps, ih]
    show (true ^^ (n % 2 == 1)) = ((n + 1) % 2 == 1)
    rcases Nat.mod_two_eq_zero_or_one n with h | h <;> simp [h, Nat.add_mod]

theorem swaps_replicate_id (n : Nat) : swaps (List.replicate n idT) = false := by
  induction n with
  | zero => rfl
  | succ n ih => simp only [List.replicate, swaps, ih]; rfl

theorem swaps_all_swap (L : List Transfer) (h : ∀ T ∈ L, T = swapT) :
    swaps L = (L.length % 2 == 1) := by
  have : L = List.replicate L.length swapT := List.eq_replicate_iff.mpr ⟨rfl, h⟩
  rw [this, swaps_replicate_swap, List.length_replicate]

/-- (5) A ring of `k ≥ 1` copies of one link excludes some pattern exactly when the
link has a swap transfer and either `k` is odd or it also has an identity transfer. -/
theorem ring_memory {d : Nat} (L : KnotLink d) (k : Nat) (hk : 0 < k) :
    (∃ ms : List (List Bool), ms.length = k ∧ (∀ m ∈ ms, m.length = d) ∧
        closes (ms.map L.transfer) = false) ↔
      ((∃ m, m.length = d ∧ L.transfer m = swapT) ∧
        (k % 2 = 1 ∨ ∃ m, m.length = d ∧ L.transfer m = idT)) := by
  have knotT_of : ∀ ms : List (List Bool), (∀ m ∈ ms, m.length = d) → ∀ T ∈ ms.map L.transfer, KnotT T := by
    intro ms hms T hT
    obtain ⟨m, hm, rfl⟩ := List.mem_map.mp hT
    exact transfer_cases L m (hms m hm)
  constructor
  · rintro ⟨ms, hlen, hms, hc⟩
    obtain ⟨hp, hs⟩ := (closes_false_iff _ (knotT_of ms hms)).mp hc
    by_cases hall : ∀ T ∈ ms.map L.transfer, T = swapT
    · -- every transfer swaps: the count is k, so k is odd
      have hk2 := swaps_all_swap _ hall
      rw [hs, List.length_map, hlen] at hk2
      obtain ⟨m, hm⟩ : ∃ m, m ∈ ms := by
        cases ms with
        | nil => simp at hlen; omega
        | cons m _ => exact ⟨m, List.mem_cons_self ..⟩
      refine ⟨⟨m, hms m hm, hall _ (List.mem_map.mpr ⟨m, hm, rfl⟩)⟩, Or.inl ?_⟩
      revert hk2
      rcases Nat.mod_two_eq_zero_or_one k with h | h <;> simp [h]
    · -- some transfer is the identity; an odd count needs a swap too
      have hid : ∃ m ∈ ms, L.transfer m = idT := by
        apply Classical.byContradiction
        intro hno
        apply hall
        intro T hT
        obtain ⟨m, hm, rfl⟩ := List.mem_map.mp hT
        rcases hp _ hT with h | h
        · exact absurd ⟨m, hm, h⟩ hno
        · exact h
      have hsw : ∃ m ∈ ms, L.transfer m = swapT := by
        apply Classical.byContradiction
        intro hno
        have hids : ∀ T ∈ ms.map L.transfer, T = idT := by
          intro T hT
          obtain ⟨m, hm, rfl⟩ := List.mem_map.mp hT
          rcases hp _ (List.mem_map.mpr ⟨m, hm, rfl⟩) with h | h
          · exact h
          · exact absurd ⟨m, hm, h⟩ hno
        have : ms.map L.transfer = List.replicate (ms.map L.transfer).length idT :=
          List.eq_replicate_iff.mpr ⟨rfl, hids⟩
        rw [this, swaps_replicate_id] at hs
        cases hs
      obtain ⟨ms_, hm_, hsw_⟩ := hsw
      obtain ⟨mi, hmi, hid_⟩ := hid
      exact ⟨⟨ms_, hms ms_ hm_, hsw_⟩, Or.inr ⟨mi, hms mi hmi, hid_⟩⟩
  · rintro ⟨⟨ms_, hls, hsw⟩, hodd | ⟨mi, hli, hid⟩⟩
    · refine ⟨List.replicate k ms_, by simp, ?_, ?_⟩
      · intro m hm; rw [List.eq_of_mem_replicate hm]; exact hls
      · rw [closes_perms]
        · rw [List.map_replicate, hsw, swaps_replicate_swap]; simp [hodd]
        · intro T hT
          rw [List.map_replicate, hsw] at hT
          exact Or.inr (List.eq_of_mem_replicate hT)
    · refine ⟨ms_ :: List.replicate (k - 1) mi, by simp; omega, ?_, ?_⟩
      · intro m hm
        rcases List.mem_cons.mp hm with h | h
        · rw [h]; exact hls
        · rw [List.eq_of_mem_replicate h]; exact hli
      · rw [closes_perms]
        · simp only [List.map_cons, List.map_replicate, hsw, hid, swaps, swaps_replicate_id]
          rfl
        · intro T hT
          simp only [List.map_cons, List.map_replicate, hsw, hid, List.mem_cons] at hT
          rcases hT with h | h
          · exact Or.inr h
          · exact Or.inl (List.eq_of_mem_replicate h)

/-! ## A parity link, written out -/

/-- The parity knot on witness in, one middle distinction and witness out. -/
def parity3 : KnotLink 1 where
  allowed a m b := (a ^^ b ^^ parity m) == true
  sep_in a m b _ h1 h2 := by revert h1 h2; cases a <;> cases b <;> cases parity m <;> simp
  sep_out a m b _ h1 h2 := by revert h1 h2; cases a <;> cases b <;> cases parity m <;> simp
  sep_mid a m b n hm hn h1 h2 := by
    have hp := parity_flipAt m n (by omega)
    revert h1 h2
    rw [hp]
    cases a <;> cases b <;> cases parity m <;> simp

theorem parity3_is_parity : IsParityLink parity3 := ⟨true, fun _ _ _ _ => rfl⟩

/-- Every ring of parity copies remembers its loop: at every length some pattern is excluded. -/
theorem parity3_every_length (k : Nat) (hk : 0 < k) :
    ∃ ms : List (List Bool), ms.length = k ∧ (∀ m ∈ ms, m.length = 1) ∧
      closes (ms.map parity3.transfer) = false := by
  apply (ring_memory parity3 k hk).mpr
  refine ⟨⟨[false], rfl, ?_⟩, Or.inr ⟨[true], rfl, ?_⟩⟩
  · funext a b; cases a <;> cases b <;> rfl
  · funext a b; cases a <;> cases b <;> rfl

end RingKernel
