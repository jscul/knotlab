# Referee reports RING-GROWTH-001-R1 and RING-FORMULA-001-R1 (fresh code, no Codex)

**Verdict on both: confirmed. No Block.**
- Every count, recurrence and rate the two studies state reproduces with the referee's own growth engine.
- The general formula has **no exception** among the 13 census rings, nor on the 14 further rings the referee grew. Five of those are odd
  rings RING-FORMULA did not grow, and two go past it: a seven-place knot, and a ring of six-place knots.
- **The step the studies flag as an outline (step 3, groups in the unrolled product) holds.** The referee found a short exact route
  for it, given in RING-GROWTH section 2. With that route written in, the growth is the model is proved for every odd ring of at least five knots, not only
  outlined.
- The fixes are wording and one sharper constant. They are listed at the end of each part for the owner and are not folded in.

# Part 1: RING-GROWTH-20261118-001

## 1. What is proved, and what is model plus check

| Claim | Status |
| --- | --- |
| Proposition 1: in the model, c(t) = Σ_v C(m(v), t − h(v)) and c(t) = c(t − 5) + c(t − 6) | **Proved; checks by hand.** Pascal's rule on the shift (0, 5), which raises m by one. The recurrence holds from t = 6 counting round 0 (the study's ticket B also finds 6) |
| Proposition 2, step 1 (the fewest rule gives exactly the demand) | **Checks by hand.** For p ≥ 1 and d ≥ 2, max(d, 3 − p, 1) = d. The offshoot has p = 1, d = 2 |
| Step 2 (candidates are one direction apart over a common lower element) | **Checks by hand.** After round 1 a live junction's only neighbours are its parents, since its children do not exist yet. So a common neighbour is a common lower cover |
| Step 3 (groups are the lower covers of one element) | **Holds; re-derived exactly by the referee** (section 2). The proof's wording "a product of the quadrant order with a cube over each position" is not literally right (fix 2) |
| Step 4 (no group wraps the ring) | **Checks by hand.** A wrapping path needs 2n = 10 position steps, and lift steps do not move the position. A group spans at most six |
| The model is the growth, computed | **The referee's check.** Grown and model patterns have equal counts and equal joint histograms of (parents, fresh) in **every round 1 to 53** (41,501 junctions). The study checked isomorphism at rounds 8 to 20 and histograms to 22 |

## 2. Step 3, written exactly

The model's junctions form a set M = {(v, S): h(v) ≥ 0, S ⊆ L(v)}, where L(v) is the set of lifts below v. M sits inside the lattice
ℤ² × (finite sets of lifts), ordered by both coordinates and by inclusion. That ambient lattice is distributive, and its rank
h(v) + |S| is modular. Three facts suffice:
- **M is closed under joins.** If S ⊆ L(v) and S' ⊆ L(v'), then S ∪ S' ⊆ L(v ∨ v'), because L is monotone.
- **Candidates have their meet in M.** If x ≠ y at rank t share a lower cover u in M, then u = x ∧ y in the ambient lattice, since u ≤ x ∧ y < x.
- **Sunflower or co-star, from modularity alone.** Take x₁, x₂, x₃ at rank t, pairwise meeting at rank t − 1. Suppose x₁ ∧ x₂ ≠ x₁ ∧ x₃.
  - Then (x₁ ∧ x₂) ∨ (x₁ ∧ x₃) = x₁, so x₁ ≤ x₂ ∨ x₃.
  - Every pairwise join has rank t + 1, so all three joins are one element w, and w ∈ M.
  - Otherwise all three meets are one lower cover: a sunflower, which is invalid.
  - **In the co-star case the three have no common neighbour.** A common one would be a common lower cover, at rank t − 1 below
    x₁ ∧ x₂ ∧ x₃, which has rank t − 2.

Every two lower covers of a w in M share a lower cover in M except when w is a round-1 position junction. These are the three meets:
- (v − e_a − e_b, S), using L(v − e_a − e_b) = L(v − e_a) ∩ L(v − e_b), when h(v) ≥ 2;
- (v − e_a, S ∖ k);
- (v, S ∖ {k, k'}).

So the maximal valid sets are exactly the lower-cover sets of the elements with three or more lower covers. The uncovered pairs are
those of the elements with exactly two. **The one exception is round 1.** There the ring knots are candidates through the ring
adjacency, not a lower cover, and section 1 of the proof handles it: n odd and at least 5 gives pairs two apart and no triple.

Nothing here uses j = 1 or the positions of the spares. Only the monotonicity of L and L(v ∧ v') = L(v) ∩ L(v') are used, and both hold
for any set of spares. This is the step RING-FORMULA borrows (Part 2).

## 3. The general formula on the 13 census rings

**The census's faster-than-power rings are its 13 exponential arrangements** (TOUCH-CENSUS-R1). All are rings of five knots. Four of
them have a knot sharing two distinctions with a neighbour, so they are not clean rings. For each one the referee counted the spare
distinctions as j = Σ (size − shared distinctions − 2), grew it, and tested c(t) = Σ_i C(j, i) c(t − n − i) on every round after the
first in which the recurrence can be stated (`referee_ring_formula.json`, `referee_ring_formula_high_j.json`).

| j | Rings | Predicted rate | Measured last ratio | Rounds grown | Recurrence holds from round (to the last) |
| --- | --- | --- | --- | --- | --- |
| 1 | 4 (three with double shares) | 1.1347 | 1.1332 | 53 | 7 |
| 2 | 4 (two with double shares) | 1.2628 | 1.264 to 1.274 | 31 | 8 |
| 3 | 3 (one with double shares) | 1.3854 | 1.385 | 24 | 9 |
| 4 | 1 | 1.5036 | 1.50 | 19 | 10 |
| 5 | 1 | 1.6180 | 1.6180 | 17 | 11 |

- **No exception.** Each recurrence holds from round n + j + 1 when rounds are counted from 1, or from n + j counting round 0. That is
  the first round it can be stated, so there is no transient beyond the minimum.
- **A double share uses up a spare.** For example, five five-place knots with two double shares grow exactly like four four-place
  knots and one five-place knot.

## 4. Other ring lengths

| Ring | Study's claim | Referee |
| --- | --- | --- |
| 4 knots, one five-place | one more junction each round | yes, 59 rounds |
| 6 knots, one five-place | per-round counts quadratic | yes: second difference 1, 51 rounds |
| 7 knots, one five-place (R1) | c(t) = c(t − 7) + c(t − 8) | yes, 59 rounds |
| 8 knots, one five-place (R2) | g = c − 4, g(t) = g(t − 4) + g(t − 5) | yes, 44 rounds |
| **10 knots, one five-place (one size past)** | (two cylinders of circumference 5, one inert, by RING-FORMULA section 4) | **yes**: g = c − 5 follows g(t) = g(t − 5) + g(t − 6) from round 7. Predicted in `even_rings.py` before the run |
| **12 knots, one five-place** | none | g = c − 6 follows g(t) = g(t − 6) + g(t − 7) from round 8. This was found after the run, not predicted |

## Fixes for RING-GROWTH (listed for the owner, not folded in)

1. **The decision note's bullet "The rule for every clean ring … checked here for n = 5, 7 and 8".** The formula x^(n + j) =
   (1 + x)^j is for odd n ≥ 5. The ring of eight does not follow it with n = 8: that would give rate 1.0757, the root of
   x⁹ = 1 + x. It follows it with n/2 = 4, on the one of its two cylinders that holds the spare, giving 1.1673, the root of x⁵ = x + 1.
   The study's own table row and proof section 4 say this correctly. **Narrowing (wording).**
2. **Step 3's "a product of the quadrant order with a cube over each position".** The cube's dimension m(v) changes with v, and
   positions stop at height 0, so M is a join-closed subset, not a product. Replace the phrase with section 2's argument. Proposition 2
   can then be called proved rather than proved in outline. **Not a block.**
3. **Optional.** The Limitations line "checked exactly to round 20" can add the referee's histogram agreement through round 53.

# Part 2: RING-FORMULA-20261118-001

## 5. The outline step: the grown pattern is the model with j spares

- **Proved at the same level as RING-GROWTH, and exactly once section 2 is written in.** Section 2 uses nothing about j.
- **The round-0 argument is unchanged.** It needs only n odd and at least 5.
- **A knot with q spares makes q one-parent offshoots in round 1.** Each has demand 2 + q − 1 = q + 1, and the fewest rule gives
  max(q + 1, 2, 1) = q + 1. Their combinations then fill in at later rounds. The histograms show this as the shapes (1, 3) for a six-place knot
  and (1, 4) for a seven-place knot, as the model says.
- **The study checked counts only, to round 13.** Its 17 rings' model counts equal their grown counts there. Its result.json says so,
  but proof section 1 points to "§4" for the check, and the check is in the Verification section.
- **The referee compared the full joint histogram of (parents, fresh) per round** on nine rings, with the model written from proof
  section 1. The table is `referee_ring_general.json`:

| Ring | n | j | Rounds compared | Junctions | Histograms equal every round | Recurrence from round (to the last) |
| --- | --- | --- | --- | --- | --- | --- |
| 5,5,4,4,4 (adjacent spares) | 5 | 2 | 31 | 46,272 | yes | 8 |
| 6,4,4,4,4 | 5 | 2 | 31 | 50,136 | yes | 8 |
| 6,4,6,4,4 | 5 | 4 | 18 | 46,948 | yes | 10 |
| 5,5,5,5,5 | 5 | 5 | 16 | 54,720 | yes | 11 (and 5F(t + 2) every round) |
| 6,4,5,4,4,5,4 | 7 | 4 | 22 | 48,133 | yes | 12 |
| 5,4,4,5,4,4,5,4,4 | 9 | 3 | 33 | 47,775 | yes | 13 |
| 5 then ten 4s | 11 | 1 | 88 | 42,405 | yes | 13 |
| **7,4,4,4,4 (past the study: a seven-place knot)** | 5 | 3 | 22 | 44,929 | yes | 9 |
| **6,6,6,6,6 (past the study: two spares at every knot)** | 5 | 10 | 10 | 55,155 | yes | too few rounds for this recurrence; the shorter one below holds |

## 6. Proposition 2: the recurrence and its transient

- **Checks by hand, with a sharper constant.** The transient is exactly T₀ = n + j.
  - At height below n each spare has at most one lift below v, because the interval of admissible k has length h/n < 1. So m(v) ≤ j
    there.
  - The low positions therefore contribute only for t ≤ n − 1 + j.
  - Every position of height at least n is the shift by (0, n) of a position of height at least 0.
- **The data agree.** The study's ticket B finds the recurrence from round n + j in all 17 rows. The referee's grown counts start at
  the first possible round in every ring.
- **Two small slips in the proof.**
  - "Raising b by n raises it by exactly one once it is nonnegative, which holds for every spare when h(v) ≥ n − 1": it holds at every
    h(v) ≥ 0.
  - "Summing over positions of height at least 2n − 1" should read "at least n".
- **The root argument is right:** f is increasing and f(1) = −j log 2 < 0.

## 7. Proposition 3, and one size past it

- **Proposition 3 checks by hand:** Σ_k C(t + 1 − k, k) = F(t + 2).
- **Computed:** n F(t + 2) in every round for n = 5 (16 rounds) and n = 9 (15 rounds, below).
- **One size past: q spares at every knot.** The same proof gives m(v) = q(h + 1), so c(t) = n Σ_h C(q(h + 1), t − h).
  - Its generating function is n(1 + x)^q / (1 − x(1 + x)^q), and the rate is the root of x^(q + 1) = (1 + x)^q.
  - **For q = 2 (five six-place knots)** the grown counts are 15, 30, 65, 140, 300, 645, 1,385, 2,975, 6,390, 13,725 in rounds 1 to 10.
    Exactly as given, with c(t) = c(t − 1) + 2c(t − 2) + c(t − 3) and rate 2.1479.
  - **This agrees with the general formula,** because x³ − (1 + x)² divides x¹⁵ − (1 + x)¹⁰.
  - **Offered as an addition, not a correction.**

## 8. Odd rings the study did not grow (the coordinator's request)

Five rings, all different from the study's 17 (`referee_ring_new_rings.json`):

| Ring | n | j | Rounds | Predicted rate | Last ratio | Formula |
| --- | --- | --- | --- | --- | --- | --- |
| 5 then ten 4s | 11 | 1 | 88 | 1.0622 | 1.0571 (not yet settled) | exact from round 13 to 88 (76 terms) |
| 5,4,4,5,4,4,5,4,4 | 9 | 3 | 33 | 1.2207 | 1.2219 | exact from round 13 (21 terms) |
| 6,4,5,4,4,5,4 | 7 | 4 | 22 | 1.3682 | 1.4024 (not yet settled) | exact from round 12 (11 terms) |
| 6,4,6,4,4 | 5 | 4 | 18 | 1.5036 | 1.4704 (not yet settled) | exact from round 10 (9 terms) |
| nine 5s | 9 | 9 | 15 | 1.618 | 1.618 | 9 F(t + 2) in every round; consistent, since x² − x − 1 divides x¹⁸ − (1 + x)⁹ |

The last-round ratio settles slowly. That is why the study scored its rates on the model to round 80, which the referee
did not repeat; the exact recurrence is the real test.

## 9. Section 4 (rings of three, four, six and even length)

- **Rings of four and six:** as stated (Part 1, section 4).
- **Even n ≥ 8, which the study marks "not proved":** consistent at 8, 10 and 12.
- **Three four-place knots:** per-round counts quadratic, so total growth cubic: three-dimensional, as stated.
- **Outside the claim:** three knots with one five-place knot grow by four junctions a round, which is two-dimensional. The spare
  lowers the dimension there.

## Fixes for RING-FORMULA (listed for the owner, not folded in)

1. **The transient.** State T₀ = n + j, with the bound m(v) ≤ j below height n, in place of "at most about 3n + j". Correct the two
   slips in section 6. **Not a block.**
2. **The outline step.** Cite section 2's argument in place of "written at the level of the predecessor's lemma". Point the check to
   the Verification section, not "§4", and say it compares counts to round 13. The referee's histograms extend it to nine rings through
   10 to 88 rounds. **Not a block.**

## How the work was split

- **The referee:**
  - read both proofs, both decision notes and RING-FORMULA's ticket-B results;
  - wrote `referee_ring.py` and four companion scripts on the referee's FIRST-KNOT-R1 growth engine and TOUCH-CENSUS-R1 census code:
    - `referee_ring.py`: the model check and the census formula;
    - `high_j.py`: the j = 3 to 5 census rings;
    - `new_rings.py`: the unseen odd rings;
    - `general_model.py`: histograms with several spares;
    - `even_rings.py`: rings of 3, 10 and 12.
- **Study code** was not imported. The census keys were read from `runs/touch-census/results.jsonl` and the referee's TOUCH-CENSUS
  file of the 100 arrangements the run had not read.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files and reproduction

Run from `research/RING-GROWTH-20261118-001/referee-R1/`. Wall times on this machine: model a few minutes, formula 27 min (one process),
high_j 8 min, new_rings 4 min, general 3 min, even 1 min.

```sh
../../../.venv/bin/python -B referee_ring.py model > referee_ring_model.json
../../../.venv/bin/python -B referee_ring.py formula > referee_ring_formula.json
../../../.venv/bin/python -B high_j.py > referee_ring_formula_high_j.json
../../../.venv/bin/python -B new_rings.py > referee_ring_new_rings.json
../../../.venv/bin/python -B general_model.py > referee_ring_general.json
../../../.venv/bin/python -B even_rings.py > referee_ring_even.json
```
