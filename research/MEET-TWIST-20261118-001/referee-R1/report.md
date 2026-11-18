# Referee report MEET-TWIST-R1 (fresh code, no Codex)

**Verdict: Confirmed. No Block.**
- **What holds.** Theorem 2 is proved. The referee checked Lemma 1 (including h = g), all five rows of Lemma 2 and its inverse, the
  parity form of zero-cost options, the irredundancy point, the induction and the corollary's reflections, line by line.
- **A fresh test that does not use Lemma 2's table.**
  - **The test.** The referee's own engine compared the exact joint law of (the new distinctions' odd sets, the co-knotted pairs)
    before and after one move of the ends' pair.
  - **The result.** It is carried at every level for every bracketing of 5 (to n0 + 4), 6 (to n0 + 4) and 7 (to n0 + 3): 263 of 263
    levels. The labelled counts are equal throughout.
  - **The orders.** The chance of two orders changes under the move for 4 of 5, 10 of 14 and 24 of 42 bracketings, as the theorem
    says it may.
- **What to add.** Wording on the range.
  - "For every n" means every line length, through the steps before the first added state.
  - That range is finite for each line: at most 2^(n0−1) distinctions.
  - From the line of five it lasts at least to n0 + 5.
  - The theorem says nothing after a state is added.

## What holds

- **The parity form (the owner's point 2).**
  - **Why r has a value at every state.** A zero-cost option pins every state. On the constant states only β knots pin (u = v
    there), and they set r = u, so r is 0 on (g, 0).
  - **Why r respects complements.** Every pin reads r = u or r = v.
  - **Why the odd set is unique.** So r is ε ⊕ φ(h) with φ(g) = 0, and φ's changes along the runs give its odd set up to the one
    distinction that lies in no run. The odd-size convention fixes that one.
  - **What KF3 adds to that.** Since KF3 never adds a copy, every E_uv is nonempty and D_g(u, v) is nonempty.
- **Lemma 1, including h = g (the owner's point 3).**
  - For h ∉ {g, g⁺}, run_g(h) = {w} ∪ run_{g⁺}(h).
  - At h = g⁺ the runs are {w} and ∅.
  - At h = g, run_{g⁺}(g) is every distinction but w, which meets an even E in |E| − [w ∈ E] ≡ [w ∈ E] distinctions.
  - All three give π_{g⁺} = π_g ⊕ [w ∈ E].
- **Lemma 2, row by row (the owner's point 1).**
  - **w ∉ E_uv.** A and D are unchanged.
    - *β → β.* β pins A_g, which holds g⁺ (π_g(E_uv, g⁺) = 0). Rightness there gives w ∉ O_r △ O_u, so the condition survives the
      move.
    - *γ_v → γ_v or γ_u.* It keeps its steps D. If w ∈ O_r △ O_v the condition flips to "r ≠ v on D". That is "r = u on D", and it
      is consistent: π_{g⁺}(O_r △ O_u) = 1 ⊕ 1 = 0 on D. The γ_u row is symmetric.
  - **w ∈ E_uv.** A and D swap.
    - *β → γ_u or γ_v.* β's steps A_g become D_{g⁺}. Its condition there reads r = u, or r = v when w ∈ O_r △ O_u, since
      π_{g⁺}(O_r △ O_v) = 1 ⊕ 1 = 0.
    - *γ → β.* A right γ_v pins D_g ∋ g⁺, which forces w ∉ O_r △ O_v. On D_g = A_{g⁺}, r = v = u, which is β. The same holds for γ_u.
    - *One to one.* γ_u and γ_v cannot both be right, since they pin the nonempty D_g to different values.
  - **The inverse.** It uses g as the witness step: π_{g⁺}(F, g) = [w ∈ F], and g lies in A_{g⁺} or D_{g⁺} as w ∉ or ∈ E_uv. Read
    backwards, the table undoes itself in every case. For instance, γ_v → γ_u → γ_v uses w ∈ O_r △ O_v ⟺ w ∈ O_r △ O_u when
    w ∉ E_uv.
- **The induction.**
  - The image of an option uses the same pairs and pins the same steps. So it is compatible, covers every step, is irredundant,
    adds no state and makes the same O_r.
  - Two knots of one option never map to one image, by injectivity on each pair.
  - KF3 weighs knot sets uniformly, and the map is a bijection of knot sets.
- **"Irredundant" (the owner's least sure).** It equals "judged on states". In KF3's code, and in the referee's, a set is redundant
  when dropping a knot leaves the union of pins (pin0, pin1) unchanged, that is the same states with the same values. For a zero-cost
  option all pins are values of one function, so this is the proof's "the others already pin every state it pins".
- **The corollary and reflections (the owner's point 4).**
  - **One cycle.** The pair graph of a triangulation is maximal outerplanar and has one Hamiltonian cycle, the polygon. So a
    renaming between two presentations with one meeting pattern maps the cycle to itself by a rotation or a reflection.
  - **Reflections.** Reversing the direction replaces a run by its complement. With odd sets of odd size, that sends (h, ε) to
    (h, 1 − ε) and keeps every odd set, so a reflection is harmless.
  - **The rest.** Single mark moves, composed, reach every marked side.
- **The fresh test (`referee_twist.py law`; the owner's point 5).**
  - **How it works.**
    - The move of the ends' pair from {m, 0} to {0, 1} is built as a new line, 1, 2, …, m, 0, with the same knots.
    - The referee's assertion checks that this new line is a presentation.
    - The new line is run separately, then renamed back.
    - The exact law of (odd sets in order, co-knotted pairs) is compared with the original's at every level.

  | n0 | Bracketings | Depth | Levels carried | Added states | Two-order chance changed by the move |
  | --- | --- | --- | --- | --- | --- |
  | 5 | 5 | n0 + 4 | 25 / 25 | 0 | 4 of 5 |
  | 6 | 14 | n0 + 4 | 70 / 70 | 0 | 10 of 14 |
  | 7 | 42 | n0 + 3 | 168 / 168 | 0 | 24 of 42 |

  This tests Theorem 2's statement directly, not Lemma 2's table, so it is independent of the frozen check (T1 to T3).

## 1. "For every n", and after a state is added (the coordinator's question; Not a block, wording)

- **What is earned.** The proof does not rest on the check. So "for every n" is earned in this sense: for every line length, and
  for every number of new distinctions up to the first one that adds a state.
- **That range is finite for each line.**
  - While no state is added, the splits are the line's n0 − 1. Every zero-cost step fills an unoccupied orientation of them
    (CUBE-DOUBLING's L1, which holds for any knot rule).
  - So at most 2^(n0−1) distinctions can exist before a state must be added: 16 for the line of five.
  - Knot-locality may end it sooner.
  - From the line of five, one bracketing runs with no added state through n = 10, which is n0 + 5 and 334,834 labelled bases. So
    for five the range is somewhere from n0 + 6 to 2^(n0−1).
- **After a state is added, the theorem says nothing.**
  - The parity description fails, since states no longer extend uniquely, and so does the coupling.
  - Whether the law is carried there is the study's direction #2, untested.
  - The check never reached such a step, as T3 records.
- **The fix.** Where "for every n" is quoted (the note, the intuition entry's "for every size", the goals row), keep "until a step
  adds a state". Add "which, on a line of n0, comes by 2^(n0−1) distinctions".

## 2. Smaller points (Not a block)

- **The orders.** The move changes the two-order chance in most bracketings. Where it does not, the bracketing is symmetric under
  that move. This fits "the cut decides the number of orders".
- **The mutant control.** Without role changes it fails on 18 states of five, a fair control for the table.

## 3. Prior work (the owner's point 6, per John's folklore direction)

- **Known, cited once.**
  - Triangulations of a polygon and their dihedral symmetry: moving the marked side is rotating the polygon, which re-roots the
    corresponding binary tree.
  - The unique Hamiltonian cycle of a maximal outerplanar graph.
  - Parity over GF(2).
  - The line's states are the cycle's two-arc bipartitions with one arc end at the mark. That is why every mark shares one index set
    (h, ε).
- **Not found.** A statement that a growth rule like KF3 is invariant under moving the marked side, while the number of orders is
  not. The preregistered "Nothing found for KF3" stands.
- **What the perspective adds.** The knots of a line form a ring, and the growth reads only the ring. Where the line's ends are cut
  decides only how the grown knots line up into orders.

## Fixes for the thread (listed for the owner, not folded in)

1. **The range.** Keep "until a step adds a state" wherever "for every n" or "every size" appears, and add that on a line of n0 this
   comes by 2^(n0−1) distinctions (at least n0 + 6 for five). Say that nothing is claimed after it. **Not a block.**

## How the work was split

- **The referee:**
  - read the note, the pre-registration, the proof and `job.py` (the twist's state map and Lemma 2's table, used only for reading);
  - checked every lemma by hand;
  - wrote its own law comparison under a mark move and the first-added-state search (`referee_twist.py`), on its MEET-ORDERS-R1
    engine.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_twist.py`.**
- **`referee_twist_law_5_4.json`, `_6_4.json` and `_7_3.json`.**
- **`referee_twist_beyond.json`:** the line of five to n = 10, stopped there.

Reproduce, from `research/MEET-TWIST-20261118-001/referee-R1/`:

```sh
../../../.venv/bin/python -B referee_twist.py law 5 4
../../../.venv/bin/python -B referee_twist.py law 6 4
../../../.venv/bin/python -B referee_twist.py law 7 3
```
