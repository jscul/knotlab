# Referee report RING-PAIR-001-R1 (fresh code, no Codex)

**Verdict: confirmed. No Block.**
- **The cover model checks three independent ways.**
  - **The block recursion with the dissymmetry count is the orbit count.** It equals the referee's rooted count divided by the
    cluster size, which is valid because the deck group acts freely on finite sets of a tree.
  - **Both equal a brute-force enumeration** of connected sets in the explicitly built cover.
- **The model equals the growth.** It reproduces every recorded round of all 17 fresh starts and of the five two-ring joins of
  JOIN-GROWTH.
- **It also equals the referee's own growth of the 5–9 join, one round past every recorded horizon** (round 17).
  The referee's own growth of four fresh starts (F01, F10, F14, F16) is queued behind the JOIN-GROWTH runs. It is marked pending
  and will be folded in.
- **The scope conditions,** recomputed by the referee, classify all 20 starts as the study does.
- **The exponent is settled: −5/2.**
  - In the exact count the local exponent is −1.42 at round 16, where the growth ends.
  - It reaches −2.00 at 50 and −2.46 at 700.
  - So the referee's earlier read of −3/2 from growth near round 17 was pre-asymptotic, and the study's Narrowing of
    JOIN-GROWTH is right.
- **The amendments are clean.**

## 1. Is the block recursion with the dissymmetry count the orbit count? (the owner's first point)

**The referee's model** (`referee_pair.py`) is written from the study's statement of it, not from `covermodel.py`.
- **The candidate complex.** A block on N(w) for every knot w with at least two neighbours, plus a pendant block for each surplus
  distinction.
- **The recursion.** U(B, z) = y Π over the other blocks B′ at z of Π_{w ∈ B′, w ≠ z} (1 + U(B′, w)).

It is counted three ways:

| Count | How | Result |
| --- | --- | --- |
| Rooted | Σ_x R_x over base vertices, then the coefficient of y^(t+1) divided by t + 1. Each orbit of a set of size s is met s times, because a nontrivial deck transformation fixes no finite set of a tree | an integer at every term |
| Dissymmetry | Σ_x R_x − Σ_B Σ_{S ⊆ B, \|S\| ≥ 2} (\|S\| − 1) Π_{v ∈ S} U(B, v). This holds because vertices − incidences + blocks = 1 on a finite subtree | **equal to the rooted count on all 40 terms**, on all 5 two-ring joins and all 17 fresh starts |
| Brute force | Redelmeier enumeration of connected vertex sets containing a root lift, in the cover built lazily as non-backtracking walks of the vertex–block incidence graph | **equal to the rooted series** for sizes 1 to 10 (5–9) and 1 to 8 (5–5–K, 5–7, 7–7, 5–5–P1) |

So `covermodel.py`'s count, which is the dissymmetry formula with surplus-only singletons removed, is the orbit count, and gate G4
(the rooted identity) is a genuine independent check. The referee did not run `covermodel.py`; its formula is the one tested here.

## 2. The model against the growth

| Starts | Growth compared | Model equals it on every round |
| --- | --- | --- |
| 17 fresh starts (F01 to F17) | the study's recorded counts, 11 to 26 rounds each (main run and memory rerun) | **17 of 17** |
| Five two-ring joins of JOIN-GROWTH (5–5–K, 5–5–P1, 5–7–D, 7–7–D, 5–9–D) | JOIN-GROWTH's recorded counts | **5 of 5** |
| 5–9–D, one round past every recorded horizon | **the referee's own growth**, rounds 0 to 17 (692,761 junctions; JOIN-GROWTH-R1's lean engine) | **yes, including round 17 (344,740)** |
| four fresh starts (F01, F10, F14, F16), the referee's own growth | *pending* | *pending* |

## 3. The scope conditions (the owner's second point)

The referee recomputed the four conditions from the start alone (`scope`):
- **round-1 candidates** are knots with a common neighbour;
- **a round-1 group of three** is three pairwise candidates with no common neighbour;
- **demand** is the number of round-1 groups containing a knot;
- **shared** is the knot's degree.

**The 17 fresh starts** pass all four: every knot has shared + demand of at least 3; surplus sits only on knots of demand at least
2; no round-1 group has three or more; and no two knots have two common neighbours.

**The three out-of-scope starts** (X01 to X03) fail on a round-1 group of three, as the study says.

**One caveat, as the note itself says.** The advisor's reading of the last two conditions, that the knot–distinction graph has no
cycle of three, four or six, is recorded, not tested. The scope conditions are sufficient where checked, not shown necessary.

## 4. The exponent (the coordinator's question, settled)

The referee computed 400 to 700 terms of the exact orbit count with its own code, in floating point scaled by the rate; the
floating series agrees with the exact integers on terms 1 to 28. Local exponents come from three consecutive terms
(`referee_pair_exponent_*.json`).

| t | 5–9–D | 5–7–D | 7–7–D | 5–5–K | 5–5–P1 |
| --- | --- | --- | --- | --- | --- |
| 16 | −1.42 | −1.44 | −1.50 | −1.53 | −1.56 |
| 50 | −2.00 | −2.06 | −2.01 | −2.13 | −2.09 |
| 100 | −2.23 | −2.26 | −2.23 | −2.30 | −2.28 |
| 200 | −2.36 | −2.38 | −2.36 | −2.40 | −2.39 |
| 499 (5–9: 699) | −2.46 | −2.45 | −2.44 | −2.46 | −2.45 |

- **The limit is −5/2.** The local exponents climb steadily toward −5/2 with a correction of order 1/t. This is the unrooted
  lattice-animal exponent on a tree-like map, the rooted −3/2 divided by one more power of t.
- **The growth cannot show it.** At the rounds growth can reach (16 to 17), the local exponent is −1.4 to −1.6. That explains both
  JOIN-GROWTH's −3/2 fit and the referee's own early read.
- **The rates.** With α = −5/2 from the last two terms: 2.868 (5–5–K), 2.427 (5–5–P1), 2.382 (5–7), 2.241 (5–9) and 2.186 (7–7).
  These fall within the study's 2.19 to 2.87.

## 5. The two amendments (the owner's third point)

- **The scorer import fix (01:47 UTC).**
  - merge.py had imported JOIN-GROWTH's `job.py`, through the same module name on the path, and scored nothing. It now loads this
    family's `job.py` by path.
  - The comparison itself is done inside each case: `job.run` stores `equal` and `first_difference`. The fix cannot have changed
    any case's result.
- **The memory rerun (01:48 UTC).**
  - Exactly the three cases that failed on memory were rerun (F06, F07, F17), by `job_mem.py` with the same cases, the same
    `job.run` and the same caps, at 7 GB.
  - All three stopped on the frozen junction cap (637,700, 750,141 and 763,527) within 178 to 329 s.
  - merge.py takes a rerun record only where the main record is not ok.
- **Both are clean.**

## 6. What the study claims, and how far it is shown

- **Computed, not proved.** The identification of the growth with the clusters is checked on every grown round, not proved; the note
  says so. The asymptotic exponent and the rates are properties of the cluster count. The referee confirms them for that count; it
  does not and cannot confirm them from growth alone.
- **Known mathematics,** cited correctly: lattice animals on the Bethe lattice (θ = 5/2) and positive algebraic systems.

## Corrections for the owner (listed, not folded in)

None for RING-PAIR. It already narrows JOIN-GROWTH's t^(−3/2), and the referee's JOIN-GROWTH report lists the same. The referee's
own earlier thread line ("favours the t^(−3/2) reading") is replaced by section 4.

## How the work was split

- **The referee:**
  - read `ring_pair.md`, the pre-registration, `covermodel.py`'s docstring and formulas, `job.py`, `job_mem.py`, `merge.py` and
    `contract.json`;
  - wrote `referee_pair.py` (the rooted and dissymmetry counts, the brute force, the scope test, the exponent) and
    `regrow_fresh.py` (its own growth of fresh starts).
- **The fresh starts' edge lists** were copied as data. No study code was run.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
