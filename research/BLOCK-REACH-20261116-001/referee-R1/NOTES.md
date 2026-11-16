# Referee R1 — BLOCK-REACH-20261116-001, fresh-code recheck

2026-11-16.
- **My own code.** My block DP and SAT oracle from the DIRECT-REACH referee (`research/DIRECT-REACH-20261115-001/referee-R1/`:
  `referee_pattern.py`, `referee_blocks.py`, `referee_check_s5.py`) are imported read-only. They were validated there against
  explicit addresses and SAT.
- **Study code.** Read, never called: `forget.py`, `run_census.py`, `gate_forget.py`, `gate_upper.py` and
  `exploratory/forget_windows.py`, for definitions only.
- **Data read as claims.** `census_forget.json` (the study's), and the census records for keys and bonds.
- **Untouched.** `NOTES_reading.md`.
- **Machine.** The load was 26 to 50 throughout.

## Summary

| Item | Verdict |
| --- | --- |
| 1. Forgetting length | **Matches.** r_stable, r_all and r₀ equal on all 786, including the 7 with r₀ = 1 and the 46 that never forget |
| 2. Rectangularity against SAT (owner's (b)) | **Matches.** 360 windows at N = 12 and 120 at N = 11 equal SAT; rectangular wherever r ≥ the claimed r |
| 3. Lemma U | **Matches.** 132 depth-9 bonds of 40 descriptions have equal projections at N = 9, 12 and 13, and are bonds at all three |
| 4. Bound against exact values | **Matches.** 45 distinct rulers with r = 1 (21 acyclic, 24 cyclic) and all 43 half-rate at N = 11: no bond below 1 + ⌈s/r⌉ for s ≤ 3. The half-rate upgrade L = 3 at s = 1, 2 holds at N = 12 for all 43 |
| Theorem F's Case 2 (owner's (a)) | **Holds** on reading; the exhaustive searches in item 4 cover bonds of both cases |

Nothing differs. The interface index in the proof's Case 1 is the one-line wording slip already noted in `NOTES_reading.md`.

## 1. Forgetting length — Matches

`referee_forget.py` → `referee_forget.json` (the sample) and `referee_forget_all786.json` (all 786; 4 s).

My implementation, written from Theorem F's statement:
- **The step from type t to child ci at remaining depth ρ** = my `Blocks.down(t, ci, F_ρ, identity on all 2^m)`.
  - The parent is restricted by every knot placed at the orbit, including its own-level knots.
  - Every other child orbit lies in F_ρ.
  - The path child is unrestricted.
- **Windows.** Sets of (end type, composed relation) over every start type and path. The first step is at ρ = r − 1 … r₀ + r − 1,
  and the steps run ρ, ρ − 1, …, ≥ 0.
- **r_all** = the least r with every window rectangular or empty.
- **r_stable** = a closure at F_{r₀} that stops at the first repeat ("never").

Results:
- **Sample** (as asked): all 7 descriptions with r₀ = 1, all 46 that never forget, and 120 others stratified by census name (seed
  20261116). **173 of 173 equal** (r_stable, r_all, r₀).
- **All 786** (cheap, so done too): **786 of 786 equal.**
- **The Corollary F table reproduces from my r values.**
  - Acyclic rulers: 197 / 47 / 1.
  - Cyclic rulers: 31 / 105 / 18.
  - Half-rate: 19 / 24.
  - Other: 5 / 8 / 1, plus 2 never.
  - Undecided: 6, plus 2 never.
  - No bond: 278 with r = 1.
  - Direct: 42 never.
- **P3's split:** 31 of 154 cyclic against 197 of 245 acyclic.
- **No census value is below the bound** (my r, every decided depth-9 cell).
- **Gaps to the census values.** Rulers: 1,083 cells with gap 1, 323 with gap 2, 190 with gap 3. Half-rate: 148 with gap 1, 24 with
  gap 2.

## 2. The block step against SAT (owner's (b)) — Matches

`referee_window_sat.py` → `referee_window_sat_N11.json` (120 windows, 30 descriptions) and `referee_window_sat_N12.json` (360
windows, 60 descriptions; 7 s).

**Method.**
- Take a random explicit path of orbits from the root (my types mapped to explicit addresses), a random top level j and
  r ∈ {1, 2, 3, the claimed r}.
- **Mine:** compose r of my steps at ρ = N − level − 1.
- **SAT:** the projection onto (O_j, O_{j+r}) of every knot of P_N (my builder) placed at an address under O_j (O_j included) and not
  under O_{j+r} (O_{j+r} excluded). Every assignment of the two orbits is decided by SAT.

The sample includes every description with r₀ = 1 (42 windows). 39 windows end at level N, so their last step is at ρ = 0. The
sub-patterns hold up to 17,920 knots (median 336); 24 windows have none.

**Results.**
- **All 480 windows equal SAT.**
- **All 212 windows at N = 12 with r ≥ the claimed r_all are rectangular in the SAT projection.**
- Of the 82 windows with r < the claimed r, 59 are not rectangular, so the claimed r is not loose.
- **Control for (b).** I restricted the bottom orbit by its own subtree (z ∈ F_{N−j−r}). This changes the relation in 12 of 360
  windows, and in none of those 12 does the restricted relation equal SAT.
  - So the window sub-pattern is exactly the unrestricted step. The bottom orbit's own knots and subtree belong to the next group,
    as the splicing lemma's groups require.
- **The splice itself.** σ_L supplies O_in. The window state w supplies the window's variables, O_out included. σ_R supplies the
  rest; its knots touch the window only at O_out. Rectangularity over all assignments gives (σ_L(O_in), σ_R(O_out)) ∈ R, so the
  splice is sound.

## 3. Lemma U — Matches

`referee_lemmaU.py` → `referee_lemmaU.json` (merged from `_a`/`_b`; 12 s of solving).

**Sample.** 40 descriptions: the 5 with r₀ = 1 that have a counted bond, and 35 drawn round-robin across census names (9 direct, 9
ruler, 8 other, 7 half-rate, 7 undecided).

**Method.**
- The bonds are every census depth-9 least bond counted in `upper_every_depth`. Its members are the record's
  `levels[s−1]['bond']`, as `run_census.py` reads them.
- That gives 132 bonds: sizes 2 (12), 3 (62), 4 (35), 5 (14) and 6 (9), with deepest members at level 4 to 8.
- For each, the projection of P_N (my builder) onto the members is computed exactly by SAT at **N = 9, 12 and 13**: every pattern
  with the first member 0, plus its complement.

**Results.**
- **All 132 projections are equal across the three depths.**
- **Every set is a bond at all three** (constrained, and every proper subset free).
- **All members lie at level ≤ 9 − r₀.**
- **Size equals the census L₉ in every case.**

## 4. Bound against exact values — Matches

`referee_bound.py` → `referee_bound_{a,b,c}.json` (20 descriptions), `referee_bound_big_{a,b}.json` (larger sample) and
`referee_upgrade.json` / `referee_upgrade_all43.json`.

**Bound, N = 11.**
- **Method.**
  - Exact ties from level 3 to every deeper level (backbone).
  - An exhaustive search for three-member bonds meeting levels 3 and 6: every {x at level 3, y at level 6, z any}, 2.1M sets. Sets
    seen with all 8 patterns in the models are excluded; the rest are decided by SAT.
  - Members may lie anywhere, so this covers bonds of Theorem F's Case 1 and Case 2.
- **Rulers with r = 1 (5 acyclic, 5 cyclic).**
  - No tie at s = 1, 2, 3, and no three-member bond at s = 3.
  - So the exact least bond is ≥ 3 at s = 1, 2 and ≥ 4 at s = 3. The bound is 2, 3 and 4, and the census L₉ is 3, 4 and 5.
  - **Bound respected; tight at s = 2 and 3 as far as this search goes.**
- **Half-rate (10; r = 2 for 5, r = 3 for 5).**
  - No tie at s ≤ 3, and no three-member bond at s = 3. So the least bond is ≥ 3, 3 and 4, against bounds of at most 3.
  - L₁₁(3, 3) ≥ 4 equals the census value, above the theorem's bound.
- **Larger sample (`referee_bound_big_a/b.json`, 95 s + 202 s).** 43 rulers with r = 1 (21 acyclic, 22 cyclic) and all 43
  half-rate (r = 2 for 19, r = 3 for 24). Every one has no tie at s ≤ 3 and no three-member bond at s = 3. The least bond is ≥ 3,
  3 and 4 against the bound; no description falls below it.

**Upgrade (L_N(3, s) = 3 at s = 1, 2 for the 43 half-rate ones), at N = 12.**
- **Method.**
  - No tie from level 3 to levels 4 and 5 (exact backbone).
  - The census's depth-9 three-member bond for that s is still constrained (6 of 8 patterns) with every pair free, and meets
    levels 3 and 3 + s.
- **15 of 15 sampled hold, and all 43 hold** (`referee_upgrade_all43.json`, 211 s). In every one, s = 1 and s = 2 have no tie,
  and the census bond has 6 of 8 patterns with every pair free at N = 12.
- **The argument for every N ≥ 9 is sound.**
  - L ≥ 3: Theorem W shows no tie at any depth (DIRECT-REACH, my recheck there).
  - L ≤ 3: Lemma U applies to the bond (within level 9 − r₀).

## Theorem F's Case 2 (owner's (a)) — Holds

Read against the splicing argument above:
- **Where u and v sit.** u lies in a side subtree of the first step from O_b, so in group 1. v lies in group k + s − b.
- **The count.** Every window counted (groups 2 … k + s − b − 1) has u on its left and v on its right. That gives
  |B| ≥ 2 + ⌊(k + s − b − 2)/r⌋ ≥ 2 + ⌊(s − 1)/r⌋, since k − b ≥ 1.
- **Depths.** The windows use only descending steps along v's path, at remaining depths ≥ N − k − s.

No gap. Item 4's exhaustive searches put z and y anywhere, including outside u's orbit's subtree, and found no bond below the bound.

## Runtime notes

Most runs took seconds. The larger item-4 runs took 95 to 211 s each. The SAT oracle reaches N = 11 for item 4's exhaustive searches, N = 12 for the upgrade and the windows, and N = 13 for Lemma U.
