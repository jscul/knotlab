# Referee report KNOT-CAP-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.**
- **What holds.**
  - T1 to T4 are proofs, and the two tight caps stop exactly at the 2 × 2 pattern.
  - The referee's own exact code, which shares nothing with `caplib.py` or `rules.py`, reproduces the key exact values:
    - the six-starts' numbers of orders are identical through n = 9, with two orders 51/140 at n = 8 and 9409/339822 at n = 9 from
      both; the first difference is at n = 10 (two orders 0.0027098 against 0.0017223, exact, from 22,724 and 22,720 labelled bases);
    - the five-starts give 5/12 against 11/18 at n = 7, and 173/6552 against 233/2457 at n = 8.
  - The owner's claim about the line of five holds: every three-knot presentation has a distinction in all three knots.
  - The exact erasure distances are exact values, not sampling, so the floor does not explain them.
- **What changes.**
  - *"Correspond class for class" overstates what was shown.* The (states, knots) class probabilities agree as multisets, and the
    order distributions agree exactly. But the two starts have 14 against 15 classes of states at n = 8, and their coarse features
    differ at n = 9 (distance 0.0023). **Not a block, wording.**
  - *The five-start pair covers two of three cases.* The shared distinction sits at an end, next to an end, or in the middle
    (labelled presentations 120, 120 and 60). The study tested end against middle only. **Not a block.**
  - *"Fading imprint" is half the story.* For the five-starts the distance fades with the knots kept as well: 0.65, 0.47, 0.40 kept
    against 0.65, 0.46, 0.30 erased. So most of the fade there is the growth, not the forgetting. Only for the six-starts does
    erasure make the difference (kept 0.68, 0.72; erased 0.66, 0.52, 0.41). **Narrowing.**
  - *Under a degree cap the knots matter by construction.* The fan's hub starts in four knots and the non-fan's busiest distinction in
    three, and a degree cap reads exactly that. The 181 against 95 at c = 5 shows the cap acting on the meeting pattern; it is not
    separate evidence of what the states lack. **Not a block, wording.**
  - *The correction to STATE-RULES is scoped correctly.* The second positive case, the five-starts uncapped, is genuine and exact.
    Two record points remain: the note says "Corrections: none" while `docs/CORRECTIONS.md` logs it as a Narrowing, and the scoped
    STATE-RULES sentence should add that even the six-starts differ slightly from n = 10. **Not a block.**

## What holds

- **T1 (proved).**
  - The fill F(a, c, b) is the unique zero-cost extension of the line of three (STATE-RULES S4), and also its unique realisation
    with at most three knots. The middle knot must be B(a, p, b), the L interval on split 1 forces B(c, a, p), and the R interval on
    split 2 forces B(c, b, p).
  - So the degrees after the step are (3, 3, 3, 3), and any new knot puts two old distinctions at four.
- **T2 (proved).** After F, each of the six pairs lies in exactly two of the four knots: (a, c), (a, b), (c, b), (a, p), (b, p) and
  (c, p), checked one by one.
- **Fresh check of T1 and T2** (`referee_cap.py`, item 1). From one knot, under the degree cap 3 and under the pair cap 2, each with
  and without knot-locality: the 2 × 2 pattern at n = 4 with probability 1, then every move is blocked (all mass stalled before
  n = 5).
- **T3 (proved).** The degree sum is 3K ≤ c·n, and K ≥ 1 + (n − 3) + 2f. At n = 16 the bound is f ≤ 3, 6 and 9 for c = 4, 5 and 6.
- **T4 (proved).** A rule that reads only the states, renamed at random, acts as one Markov kernel on classes of states, whichever
  start the states came from. Total variation does not increase under a kernel. The exact erasure curves are non-increasing, as
  T4 requires.
- **The matched starts, exactly** (item 2). The referee propagated exact rational distributions over labelled (states, knots) bases
  under KF3: fewest states over knot-local moves, uniform over irredundant knot sets.

  | Starts | n | Two orders (each start) | λ distributions | Coarse features, distance |
  | --- | --- | --- | --- | --- |
  | fan6, nonfan6 | 7 | 1, 1 | equal | 0 |
  | fan6, nonfan6 | 8 | 51/140, 51/140 | equal | 0 |
  | fan6, nonfan6 | 9 | 9409/339822, 9409/339822 | equal | 0.0023 |
  | fan5, mid5 | 7 | 5/12, 11/18 | differ | 0.417 |
  | fan5, mid5 | 8 | 173/6552, 233/2457 | differ | 0.378 |

  The labelled bases number 1, 4, 24 and 536 from each six-start at n = 6 to 9. All values equal the study's to the last digit.
- **The five-start pair** (item 3). There are 300 labelled sets of three betweenness knots on five distinctions whose base is a
  line. Every one has exactly one distinction in all three knots, which confirms the owner's point. That distinction sits at an end
  in 120, next to an end in 120 and in the middle in 60: per order of the line, two fans, two hubs next to an end, one middle hub.

## 1. "Correspond class for class" (the owner's first check; Not a block)

- **What the study checked.** Through n = 9, its K2 compares the sorted list of class probabilities ("sorted_probabilities_equal"),
  and the two-order and λ distributions. Both match.
- **What is exact.** The referee's exact rational run confirms that the order distributions are identical through n = 9.
- **Why "class for class" is too strong.** The classes of states are not in correspondence: there are 14 against 15 at n = 8 and 52
  against 57 at n = 9, and their coarse features (N, splits, crossings) differ by 0.0023 at n = 9.
- **A fair line.** "Through n = 9 the two starts give the same multiset of class probabilities and identical distributions of the
  number of orders (exact). Their classes of states differ throughout from n = 7."
- **The first difference at n = 10** (0.0027 against 0.0017 two orders): confirmed exactly by the referee: two orders 143556687457/52977325484160 ≈ 0.0027098 against 34829826271/20222527469760 ≈ 0.0017223, with λ = 3 at 0.67585 against 0.67724 (`referee_cap_n10.json`).

## 2. The erasure curves: fade or floor? (the coordinator's question; Narrowing)

- **Exact values, not the floor.** The exact distances after erasure are computed from exact distributions, so no sampling floor
  enters:
  - six-starts: 0.779, 0.655, 0.522, 0.414 at n = 8 to 11;
  - five-starts: 0.651, 0.461, 0.302, 0.202.
- **The sampled values do meet the floor.**
  - For the six-starts the floor rises from 0.21 at n = 9 to 0.52, 0.74, 0.88 and 0.95 at 10 to 13. The sampled distance (0.70 to
    0.96) is then mostly floor: it reads 0.715 at n = 10 against an exact 0.522. From n = 12 the permutation tests are near 0.7.
    The note says this ("swamped from n = 11 on").
  - For the five-starts the classes stay few (4 to 38) and the floor stays low (0.03 to 0.1). Their sampled curve 0.65, 0.45, 0.30,
    0.19, 0.16, 0.09, 0.06 is real, reaching the floor near n = 14.
- **But the kept control matters.** The study's no-erasure control, KF3 continuing with its knots, exact:

  | Starts | n = 8 | 9 | 10 | 11 |
  | --- | --- | --- | --- | --- |
  | six, knots erased | 0.779 | 0.655 | 0.522 | 0.414 |
  | six, knots kept | 0.779 | 0.677 | 0.724 | — |
  | five, knots erased | 0.651 | 0.461 | 0.302 | 0.202 |
  | five, knots kept | 0.651 | 0.470 | 0.399 | — |

  For the six-starts, erasure is what makes the difference fade; with the knots kept it stays near 0.7. For the five-starts the
  difference fades with or without the knots. At n = 9 the two are almost equal (0.470 and 0.461), and erasure only speeds the fade
  by n = 10.
- **A fair line.** "After erasure the states' difference fades (exact). For the six-starts that is the forgetting, since with the
  knots kept it stays near 0.7. For the five-starts most of the fade happens with the knots kept too." The note gives the kept
  control only for the six-starts.

## 3. The correction to STATE-RULES (the coordinator's question)

- **The logged Narrowing is right and well scoped.**
  - The five-starts give an exact uncapped case where how the knots meet changes the number of orders (5/12 against 11/18 at
    n = 7). The referee's exact run reproduces it.
  - The six-start finding (the referee's own 1,000 runs in `STATE-RULES-R1`) stays as scoped there: "for these two starts".
- **Two record points.**
  - *The six-starts themselves differ slightly from n = 10.* The scoped STATE-RULES sentence says "exactly equal through n = 9". It
    should add "with a tiny difference from n = 10" (two orders 0.0027 against 0.0017 at n = 10, exact). The 1,000 runs could not see a difference of that size.
  - *The note and the log disagree.* KNOT-CAP's note says "Corrections: none … extended, not contradicted", while its close commit
    logs a Narrowing in `docs/CORRECTIONS.md`. One of the two should change; the log's reading (a Narrowing of the earlier general
    sentence) is the accurate one.

## 4. Smaller points (Not a block)

- **The cap at c = 5.** Its effect on the six-starts is the cap reading the degree profile: the fan's hub is already in four knots.
- **"Logic's cheapest continuation and its tightest local limits meet at two orders, and nothing grows past them."** That is true as
  a stop: the caps end the growth at the 2 × 2 pattern. They do not grow two orders. The note's Position says so ("the tight caps
  stop, the loose ones run on").
- **The predictions.** C2, C3, C5, C6 and C9 failed and are carried honestly, with the advisor's role named.

## Fixes for the thread (listed for the owner, not folded in)

1. **The erasure reading.** Give the kept control for both pairs, and say that for the five-starts the difference fades with the
   knots kept as well. **Narrowing.**
2. **Wording.**
   - "Same multiset of class probabilities and identical order distributions through n = 9" for "correspond class for class".
   - Name the third five-start (hub next to an end) as untested.
   - Say the c = 5 effect is the degree cap reading the hubs.

   **Not a block.**
3. **The record.**
   - Make the note's Corrections line match the logged Narrowing.
   - Add the n = 10 difference to the scoped STATE-RULES sentence.

   **Not a block.**

## How the work was split

- **The referee:**
  - read the note, the pre-registration, the proof, `caplib.py`, `run.py` and the results (K2, K4);
  - checked T1 to T4 by hand;
  - wrote its own move enumeration (irredundant knot sets, knot-locality, both caps), exact rational propagation, orders, and the
    enumeration of the line of five's presentations (`referee_cap.py`, `referee_cap_n10.py`).
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_cap.py` and `.json`:**
  - 1, the tight caps;
  - 2, the matched starts, exact (six to n = 9, five to n = 8);
  - 3, the presentations of the line of five.
- **`referee_cap_n10.py` and `.json`:** the six-starts at n = 10, exact.

Reproduce, from `research/KNOT-CAP-20261117-001/referee-R1/`:

```sh
../../../.venv/bin/python -B referee_cap.py > referee_cap.json
../../../.venv/bin/python -B referee_cap_n10.py > referee_cap_n10.json
```
