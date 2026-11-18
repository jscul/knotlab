# Referee report MEET-GROW-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.**
- **What holds.**
  - The computations are sound.
  - The referee's own engine (MEET-ORDERS-R1's, without digests) recomputes P1 exactly for every pair of presentations of five and
    six distinctions, to n0 + 4. All 9 pairs are carried, each by both isomorphisms of their meeting patterns. The two-order chances
    differ within every pair.
  - The labelled counts follow the pattern (P3).
  - The digest method, `canonical_pattern` and the automorphism comparison are correct.
- **What changes.** "The meeting pattern grows on its own" says more than P1 and P4 show.
  - Within one presentation, bases with the same pair graph give different laws for the next pair graph from the third new
    distinction on. At six this is 6 of 18 pair graphs at n0 + 2 and 170 of 218 at n0 + 3.
  - So the pair graph is not a process of its own: the states steer its next step.
  - What is shown is that the joint growth looks the same wherever the pattern sits along the line.

  The study's own pre-registration discloses the state dependence. The headline, the owner's-terms paragraph and the A97 line drop it.
  **Narrowing.**

## What holds

- **The digest method (the owner's point 1).**
  - **How the digest is made.** Each level's distribution of the co-knotted pairs G is relabelled by α ∘ φ (φ to the canonical
    pattern, α one of its automorphisms; new distinctions fixed). It is written as the sorted repr of (G, exact fraction) pairs, and
    hashed (24 hex characters of sha256, 96 bits). A false equality would need a collision, which is negligible at this scale.
  - **How carrying is scored.** `first_uncarried` requires the same α at every level (one isomorphism for all levels), and so does
    `profile_carried`.
  - **Why every isomorphism is covered.** φ_b⁻¹ ∘ α ∘ φ_a runs over every isomorphism between the two patterns as α runs over the
    automorphisms.
  - **The G4 gate's reach.** It compares digests with a direct comparison on all ten pairs of five. At five every pair has one
    pattern and is carried, so G4 tests agreement when carried but not the discrimination between patterns.
  - **The referee's check needs no digests.** It compares exact fractions directly.
- **`canonical_pattern` (job.py).** The least relabelled sorted knot list over all n0! renamings, and the automorphisms of that form
  by exhaustive search. It is correct, and it is exact for n0 ≤ 9.
- **The profile digest (P4; the owner's point 3).**
  - **What it encodes.** For each labelled base it records the cheapest cost and, for each cheapest knot set, the pairs it adds,
    relabelled and sorted. So it carries each option's effect on the pairs.
  - **What it leaves out.** Each option's effect on the states.
  - **So P4's "state by state" means:** the joint law of (pair graph, the options' effects on the pairs) is carried. That is what the
    note says.
- **A fresh recomputation (the owner's point 4; `referee_grow.py`).** The referee's labelled KF3 engine ran every presentation of
  five and six to n0 + 4 (one per mirror pair: 3 and 7) and compared the exact distributions of G within each meeting pattern, under
  every isomorphism found by brute force.

  | n0 | Presentations | Meeting patterns | Pairs within a pattern | Carried at every level | Two orders differ |
  | --- | --- | --- | --- | --- | --- |
  | 5 | 3 | 1 | 3 | 3 (each by both isomorphisms) | 3 |
  | 6 | 7 | 3 (3, 3, 1) | 6 | 6 (each by both isomorphisms) | 6 |

  - The labelled counts are equal within each pattern and differ between them: six gives 13,368 and 13,364 for the two
    three-member patterns, and 16,272 for the single one at n = 10. Five gives 6,752 at n = 9.
  - These equal the study's values (P3).
- **Prior work (the owner's point 5).**
  - The in-program line is accurate: MEET-ORDERS is the source, and STATE-RULES is a relative.
  - "None found outside" fits what the referee found for MEET-ORDERS. Triangulations and rotations are classical. A growth law for
    co-knotted pairs under betweenness extensions is not in the literature that the referee searched.

## 1. "The meeting pattern grows on its own" (the coordinator's question; Narrowing)

- **The test.** Within one presentation, at each level, the referee grouped the labelled bases by their pair graph G. It asked
  whether every base with the same G has the same option profile, and the same law of the next pair graph.
- **The result, the same for every presentation of a size:**

  | n0 | Level | Pair graphs | With bases whose next-pair-graph laws differ |
  | --- | --- | --- | --- |
  | 5 | n0, n0 + 1 | 1, 3 | 0, 0 |
  | 5 | n0 + 2 | 10 | 4 |
  | 5 | n0 + 3 | 120 | 98 |
  | 6 | n0, n0 + 1 | 1, 4 | 0, 0 |
  | 6 | n0 + 2 | 18 | 6 |
  | 6 | n0 + 3 | 218 | 170 (180 of 228 in the single pattern) |

- **What this means.**
  - Through the second new distinction the pair graph does decide its own next step. That is MEET-ORDERS's Lemmas A and B.
  - From the third on, it does not. Bases with the same pairs but different states grow different pairs. So the pair graph is not a
    Markov process of its own, and the states steer it.
  - The study disclosed this in its pre-registration ("the correspondence is not one of pair graphs alone"; 510 pair graphs for five
    to n0 + 3).
- **What P1 and P4 do show.** The joint growth, states and pairs together, has the same pair law and the same option effects
  wherever the meeting pattern sits along the line. Some map of states, perhaps the advisor's twist, carries one placement onto
  another.
- **Fair plain-language readings:**
  - "the meeting pattern grows by the same law wherever it sits along the line";
  - "where the pattern sits does not change how its pairs grow, only how many orders they carry".
- **Readings that overstate:**
  - the headline's "grows on its own";
  - "a process of its own" (owner's terms);
  - A97's "the pairs grow by a law of the meeting pattern alone, while the states decide only the number of orders".

  The states also decide which pairs come next, in a way the placement does not change.

## 2. How this squares with MEET-ORDERS-R1's "12 patterns, 8 signatures" (the coordinator's question)

- **Consistent.**
  - MEET-ORDERS-R1 compared coarse signatures: labelled-base counts and mass by largest odd set. At n0 = 8 those do not separate all
    12 meeting patterns.
  - P2 compares the pair-graph laws themselves up to renaming, a finer invariant, which does separate them. The note says so in its
    Limitations.
  - Both agree that the pattern decides its own signature: 12 of 12 patterns uniform there, and P1 here.
- **Not rechecked.** P2 was not recomputed by the referee, since it needs canonical forms of pair graphs at every level.
- **Two points about P2's starting level.**
  - It differs trivially there: a bracketing's pair graph is a maximal outerplanar graph, whose triangles are its knots.
  - Its "every level" runs to n0 + 3, not beyond.

## 3. Scope (the owner's least sure; Not a block)

- **Beyond the depths computed.** Nothing here goes past the study's depths. The referee's checks sit inside them: five and six to
  n0 + 4.
- **The fewest-knot scope.** A100 is material for the orders (MEET-ORDERS-R1: one redundant knot changes the second-step chance in
  21 of 21 cases). For the pairs' law across placements it is untested here too.
- **"Computed, not proved".** The note marks it so. The mechanism (the twist) is the advisor's.

## Fixes for the thread (listed for the owner, not folded in)

1. **The headline and its quotes.** Replace "the meeting pattern grows on its own" and "the states decide only the number of orders"
   with "grows by the same law wherever it sits; the states steer which pairs come next, the same way in every placement". Do this
   in the note, the A97 line and the intuition entry if it repeats it. **Narrowing.**
2. **Record the state dependence in the note.** From n0 + 2, pair graphs with state-dependent next steps: 6 of 18 at six, 170 of 218
   at n0 + 3. **Not a block.**
3. **G4's reach.** It checks agreement on carried pairs only. A cross-pattern direct comparison would test the other side.
   **Not a block.**

## How the work was split

- **The referee:**
  - read the note, the pre-registration, `job.py` (`canonical_pattern`, the digests, the profiles), `merge.py`, `checks.py` (G4)
    and the results;
  - wrote its own comparison of exact pair-graph distributions under brute-force pattern isomorphisms, and the state-dependence
    tests (`referee_grow.py`), on its MEET-ORDERS-R1 engine.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_grow.py`** (the parts `run` and `merge`).
- **`referee_grow_5_4.json` and `referee_grow_6_4.json`:** the merged comparisons. The per-presentation distributions are
  regenerated by `run`, not kept.

Reproduce, from `research/MEET-GROW-20261118-001/referee-R1/`:

```sh
for j in 0 1 2 3 4 5 6; do ../../../.venv/bin/python -B referee_grow.py run 6 4 $j; done
for j in 0 1 2; do ../../../.venv/bin/python -B referee_grow.py run 5 4 $j; done
../../../.venv/bin/python -B referee_grow.py merge 6 4 > referee_grow_6_4.json
../../../.venv/bin/python -B referee_grow.py merge 5 4 > referee_grow_5_4.json
```
