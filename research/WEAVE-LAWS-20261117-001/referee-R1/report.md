# Referee report WEAVE-LAWS-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.**
- **What holds.**
  - L1, L2 and L3 are correct, and the sign-consistency test is right.
  - Every frozen number recomputes with the referee's own code.
  - The disagreeing-sign laws are frozen exactly: the spectral radius of each one's live transfer is exactly 1 at every width
    from 3 to 12 (one of them: exactly 2 on two live rows). The Arnoldi values above 1 are numerical artifacts.
  - The post-freeze amendment changed only numerical method.
- **What changes.**
  - *"The pairwise laws are critical or frozen" holds more widely than tested,* for all 16 laws that put one not-all-equal-class
    knot on every up knot and one on every down knot. But probes one size past find two cases that look disordered:
    - **NAE with a sparse random mix of the three signed knots;**
    - **one periodic law on a 2 × 2 cell.**

    Every knot in both is pairwise, so their pair counts carry them. So the premise's positive case on the weave probably exists,
    among non-uniform bases and laws on larger cells. The G1 and G16 checkpoint, "obstruction learned", holds for laws with one
    knot per orientation only.
  - *P7's open question is settled.* λ₁ is the mode a single distinction feels. The miss is a period-three oscillation. But that
    oscillation also means the ruler laws' pair-count deviation does not shrink step by step along an axis. So "the distances that
    do step outward" holds as an envelope only.

## What holds

- **Order.** The freeze, `9b4346001`, is at 19:41:53 UTC. The amendment, `266f96fde`, is at 19:44:28, and the run went from
  19:44:28 to 19:47:43. `lawlib.py` and `run.py` hash to the amendment's recorded values, unchanged since.
- **L1 (proved).** The referee computed the Fourier degree of all 34 knots' allowed sets. Degree at most two holds exactly for the
  knots that exclude one complementary pair. There are 4 of them, not 8 (see 6).
- **L2 (proved; the owner's item 1).**
  - **The bond kinds are mapped correctly.** For up knot places (1,2), (1,3), (2,3), they are e1, e2, e3; for the down knot, e3,
    e2, e1.
  - **The ferromagnetic bonds** (those where p differs) are:

    | Knot | Up knot | Down knot |
    | --- | --- | --- |
    | NAE | none | none |
    | p1 | e1, e2 | e2, e3 |
    | p2 | e1, e3 | e1, e3 |
    | p3 | e2, e3 | e1, e2 |

    So 4 of the 16 up/down pairs are consistent: (NAE, NAE), (p2, p2), (p1, p3) and (p3, p1). Of the study's six, NAE and the
    place-2-odd law are consistent, as it says.
  - **The holonomy, at every width.** The place-2-odd law's gauge flips every other column (g = i mod 2), so it needs an even
    width.
    - Its row spectrum equals NAE's to every digit at widths 4, 6, 8, 10 and 12.
    - It differs at every odd width, 3, 5, 7, 9 and 11, not only at 9. Its top eigenvalue is doubled at 3 and 9.
    - The torus counts agree: 14 against NAE's 42 at L = 3, and 263,640 for both at L = 6.

    The other two consistent pairs behave as their gauges predict:
    - (p3 up, p1 down) has g = j mod 2, a twist along the transfer axis, and its spectrum equals NAE's at every width;
    - (p1 up, p3 down) has g = i + j mod 2, and is twisted at odd widths.
  - **Pair counts carry every base of the class, signed knots included.** Take a knot excluding {p, p̄} on (a, b, c). Each triple
    state outside {p, p̄} mismatches p's pair pattern on exactly two pairs, and each state inside mismatches on none. So the number
    of states of a relation inside {p, p̄} is N − ½ Σ over the three pairs of the number of states that mismatch on that pair. Each
    term is a pair count d or N − d.

    N and the pair counts therefore say which signed knots a relation satisfies. A base's relation is the conjunction of the knots
    it satisfies. This re-derives statement 3(a) of `DISTANCE-ORDER-20261117-001A`, which already covers the signed knots
    (001/110, 010/101 and 100/011, through its statement 1), so L1's last sentence needs no extension. *Corrected by the referee
    after the first commit:* an earlier wording said 3(a) was proved for plain NAE only.
- **L3 (proved).**
  - **Hard hexagons.** States per distinction are 1.39549 at widths 8 to 12. The torus counts are 23, 202, 4,217 and 162,315, and,
    one size past, 12,329,634 at L = 7.
  - **Parity.** It is frozen exactly: spectral radius 1 at every width, with torus counts 4, 1, 1, 4, 1 at L = 3 to 7.
- **The twelve laws recompute.** The referee wrote its own transfer. Each value below matches the study:
  - **NAE.** States per distinction 1.38565 at width 12; gaps 0.1987, 0.1351 and 0.1021.
  - **The agreeing-signs law.** Gap 0.0936 at width 9, with a doubled top eigenvalue.
  - **OR.** States per distinction 1.76736; gap 1.1192 at width 12.
  - **Hard hexagons.** Gap 0.8586 at width 12.
  - **Distance-two, place 2 odd.** States per distinction 1.2566 and gap 0.0514 at width 12, with the same erratic gaps at smaller
    widths.
  - **OR's torus counts** are 178, 8,951, 1,524,541 and 801,919,016, and, one size past, 1,314,679,218,273 at L = 7.
  - **P1, one size past.** A product transfer that reproduces the dense spectrum to 10⁻¹³ at widths 6 and 9 gives NAE's
    gap × width as 1.230 at width 15, within 0.008 of 1.238.
- **The census recomputes.**
  - OR has 16, 1,024 and 1,048,576 relations, with 16, 1,024 and 995,085 keys. At six distinctions there are 44,521 colliding
    groups.
  - Not-exactly-two has no collision at four distinctions (12 relations) and 227 relations with 217 keys at five.
  - Parity has 16 relations with 13 keys at four.
  - The distance-two class, in any place order, has 1,118 relations with 1,097 keys at four.

## 1. The frozen readings are exact (the owner's items 2 and 4; Not a block)

**The test.** A 0/1 matrix restricted to its live rows (rows on an endless path) has spectral radius exactly 1 when every
strongly connected part is a single cycle. It has radius above 1 when some part is not. The referee applied this test exactly
(`referee_laws.py`, `frozen_exact`).

| Law | Live transfer, widths 3 to 12 | Spectral radius |
| --- | --- | --- |
| signed NAE, place 1 odd; place 3 odd | every row may follow itself; every other move is one-way (35,108 such moves at width 12) | exactly 1 |
| NAE up, place 3 odd down | single cycles up to 2 × width long, joined by one-way moves; no torus state at odd L | exactly 1 |
| NAE up, place 1 odd down | **no state on any odd-width cylinder**; at even widths two live rows with all four moves | exactly 2 |
| distance-two, places 1 or 3 odd | single cycles joined by one-way moves | exactly 1 |

- **The Arnoldi values above 1 are artifacts.** These are 1.0002 to 1.0007 per distinction at widths 11 and 12 for the uniform
  laws, and 1.0015 and 1.0010 for distance-two at 12.
  - The dense values came out exactly 1 because LAPACK's balancing isolates triangular structure. For the two uniform laws the
    live transfer is triangular with ones on its diagonal.
  - Arnoldi does not isolate it.
  - P6 holds. It now stands on an exact test at widths 3 to 12, not only on a prediction informed by the L = 6 counts. The study
    disclosed that those counts were seen before the freeze.
- **"Each row fixes the next exactly" is not what happens** for the two uniform laws. A row has several possible successors (14
  moves among 8 rows at width 3). What is exact:
  - on a torus every row equals the next, so the torus states are the 2^L states constant along the axis across rows;
  - on an open cylinder the rows change only a bounded number of times, so counts grow polynomially in the length.
- **NAE up, place 1 odd down** has states per distinction 2^(1/width): 1.0595 at width 12, not the table's 1.000. It tends to 1,
  so it is frozen by the rule, but it carries one free bit per row. It has no state at all at odd widths.

## 2. "The pairwise laws are critical or frozen": right for every law with one knot per orientation, but a sparse mix looks disordered (the owner's item 3; Narrowing)

**All 16 such laws** (`referee_scope.py`, `.json`):

| Pairs (up knot, down knot) | Consistent | On the weave, widths 3 to 12 |
| --- | --- | --- |
| (NAE, NAE), (p3, p1) | yes | NAE's spectrum at every width: critical (L2) |
| (p2, p2), (p1, p3) | yes | NAE's spectrum at even widths, twisted at odd: critical (L2) |
| (NAE, p2), (NAE, p3), (p1, NAE), (p1, p1), (p2, NAE), (p2, p1), (p3, p2), (p3, p3) | no | spectral radius exactly 1: frozen |
| (p1, p2), (p2, p3) | no | two live rows, λ₀ = 2: per distinction 2^(1/width) → 1 |
| (NAE, p1), (p3, NAE) | no | the same at even widths; no state at odd widths |

So the bullet holds for all 16, not only the six tested. Ten of the 16 were untested, two of them consistent and eight not.

**A base, not a law: NAE with a density ε of signed knots** (`referee_mix.py`, `.json`, `_runs.jsonl`, `_long.jsonl`).
- **The setup.** Each knot is NAE, or with probability ε one of p1, p2 or p3. The base is read on the cylinder through the
  product of row transfers, one distinction at a time. That gives states per distinction from the top Lyapunov exponent, and the
  gap from the first two exponents.
- **Checks.**
  - At ε = 0 it reproduces NAE's dense spectrum to 10⁻¹³ at widths 6 and 9.
  - At width 6 its exact count equals the strip product's on the same draws.
  - A random gauge of NAE gives NAE's counts exactly at widths 4 to 9.

Gap per row, in log base 3, with two seeds and 600 rows (500 after a burn-in of 100):

| ε | width 6 | 9 | 12 | 15 | gap × width at 15 | states per distinction at 15 |
| --- | --- | --- | --- | --- | --- | --- |
| 0 (NAE) | 0.199 | 0.135 | 0.102 | 0.082 | 1.23 | 1.384 |
| 0.01 | 0.195, 0.196 | 0.136, 0.139 | 0.103, 0.102 | 0.084, 0.086 | 1.26, 1.29 | 1.374 |
| 0.03 | 0.207, 0.205 | 0.144, 0.140 | 0.114, 0.115 | 0.094, 0.101 | 1.40, 1.52 | 1.355 |
| **0.1** | 0.250, 0.228 | **0.196, 0.203** | **0.209, 0.203** | **0.199, 0.201** | **2.99, 3.02** | **1.302** |
| 0.3 | no state after 73 and 173 rows | 0.202; no state after 230 | no state after 43 and 165 | no state after 416 and 242 | — | — |

- **At ε = 0.1 the gap levels off near 0.20 from width 9 to 15,** about five rows of correlation length. By the study's own frozen
  rule (changes by less than 10% from 9 to 12, above 0.05) that is **disordered**. The base keeps 1.30 states per distinction.
  - At 0.03 the gap × width is still climbing (1.24 to 1.52). This looks like a crossover with a correlation length beyond these
    widths.
  - At 0.01 it is close to NAE's.
  - All twelve runs at ε = 0.1 and 0.03 survive 5,000 rows (widths 6 and 9, three fresh seeds), with gaps of 0.243 to 0.249 at
    width 6 and 0.209 to 0.215 at 9.
  - A uniform mix of the four knots dies within 3 to 40 rows at every width from 4 to 9 (18 of 18 runs).
- **What this shows and does not.**
  - *It is a probe.* It uses Lyapunov exponents, two or three seeds and widths up to 15, and it measures a gap, not the pair-count
    ruler itself.
  - *The endless random base may be contradictory.* If some finite patch of these knots has no state, an endless independent mix
    contains one somewhere almost surely, and then has no state at all. At ε = 0.3 cylinders die within a few hundred rows. Whether
    they die by a local patch or by a contradiction around the cylinder was not separated.
  - *A periodic mix avoids that question,* since it is a law on a larger cell. A first probe with one signed up knot per 2 × 2 or
    3 × 3 cell (`referee_periodic.py`, `.json`) is mixed:
    - placing p3 every 2 × 2 cell (one knot in eight) gives gaps per row of 0.315, 0.315, 0.257, 0.240 and 0.233 at widths 4
      to 12. That is gap × width 1.26 to 2.79, levelling off within 10% from width 8 to 12, with 1.249 states per distinction.
      It looks disordered;
    - p1 and p2 there (identical to each other), and every 3 × 3 placement, have gaps falling with width at widths up to 10 or
      9.

    **So one periodic law on a 2 × 2 cell, all of whose knots are pairwise, already looks disordered at widths up to 12.** It is a
    probe at small widths, not a classification.
- **What follows for the study.**
  - The headline, "no *tested* knot law", stands.
  - The bullet "The pairwise laws are critical or frozen" should read "every law that puts one not-all-equal-class knot on all up
    knots and one on all down knots (all 16) is critical or frozen".
  - The Position line "Obstruction learned: on the weave, information and order sit in different laws' counts", the G1 and G16
    checkpoint, and A97's narrowing hold for such laws.
  - The probe suggests they do not hold for bases, nor for laws on a 2 × 2 cell. Direction 1 ("Can a non-uniform arrangement of pairwise knots on the weave be
    disordered?") looks likely to succeed. It is now the concrete candidate for the premise's positive case on the weave. The
    referee recommends the coordinator weigh raising it. The decision is the program's.

## 3. P7 and the rulers (the coordinator's question; Narrowing of the owner's-terms sentence)

- **The gap's mode is the one a single distinction feels** (`referee_laws.json`, `single_distinction_modes`). The referee wrote the
  single distinction's correlation along the transfer axis as Σ_k a_k (λ_k/λ₀)^r, with left and right eigenvectors.
  - For OR, λ₁ is a complex pair, of phase ±2π/3 at widths 6 and 9 and ±0.7π at 10.
  - It is the first coupled mode, with the largest amplitude (0.16, 0.11 and 0.10).
  - So the correlation decays asymptotically at exactly the gap's rate. The study left this open; the answer is yes.
  - P7's miss comes from the oscillation and from nearly degenerate modes (OR's next ones decay at 1.157 and 1.18), read from two
    points. P7 stays failed by its frozen rule, and OR is disordered.
  - Hard hexagons are the same: λ₁ is a complex pair (±0.8π at width 10) and is the first coupled mode.
- **But the oscillation means the pair-count deviation does not shrink step by step.**
  - *OR, at widths 9 and 10.* C(r) is −0.129, −0.0067, +0.0063, −0.0012, −2 × 10⁻⁵, +6 × 10⁻⁵ for r = 1 to 6. So |C(3)| ≈ |C(2)|
    and |C(6)| > |C(5)|.
  - *Hard hexagons.* |C(3)| > |C(2)| and |C(7)| > |C(6)|.
  - *What this changes.* A distance read as −log|C(r)| along an axis grows linearly only as an envelope, and at small r it ranks a
    farther distinction as nearer. The answer's sentence "the distances that do step outward carry only part of the information"
    needs "in envelope". Otherwise it needs a reading that removes the period-three oscillation.
  - *NAE's own correlations* oscillate with period three as well (Stephenson). That was already handled through nearness levels in
    `DISTANCE-DIM-20261117-001`.

## 4. P2 in the headline (the coordinator's question; Not a block)

- **The failure is carried honestly** in the predictions table and its paragraph. The criticality claim rests on L2 (proved),
  not on the measurement.
- **Two fixes of wording.**
  - The twist applies at every odd width, not "at width 9".
  - The answer's bullet quotes gap × width 1.192, 1.216 and 1.225 for both NAE and the agreeing-signs law. Those are NAE's. The
    agreeing-signs law reads 0.84 at width 9, and equals NAE at even widths.

## 5. The amendment (the coordinator's question; Not a block)

- **What it changed.** It touched only `lawlib.py`'s numerical method:
  - trimming to the live part;
  - dense eigenvalues up to 1,024 live rows instead of up to width 9;
  - a ones starting vector for Arnoldi, with a dense fallback;
  - the same starting vector for the correlation.

  It also added the contract's amendment record. The classification rules, predictions and headline rule live in the
  pre-registration and are untouched. No read-out rule changed.
- **Bookkeeping.**
  - The record's "at" is 19:47Z. That is after its own commit (19:44:28Z) and after the run started (19:44:28Z); it should read
    19:44Z.
  - `run.py`'s docstring still says "dense eigenvalues to 9, sparse Arnoldi at 10 to 12".

## 6. Smaller points (Not a block)

- **L1's count.** "Zero exactly for the 8 that exclude one complementary pair" should say 4. The cube has 4 complementary pairs;
  the 8 literal patterns pair up.
- **L2's proof wording.** "Forbids exactly the states in which all three bonds are satisfied" should say *violated*. Under the
  stated signs, p itself violates all three bonds. The allowed states violate exactly one, the frustrated triangle's ground
  states.
- **`check.py`'s docstring** claims "a direct gauge search on small tori (L = 3, 6)". The check compares L = 6 counts with NAE's
  only. At L = 3 the agreeing-signs law has 14 states against NAE's 42, the odd twist.
- **Distance-two, place 2 odd.** It is reproduced, and "unclassified" is fair.

## Fixes for the thread (listed for the owner, not folded in)

1. **Scope the pairwise bullet and the checkpoint.**
   - Say "every law with one not-all-equal-class knot on all up knots and one on all down knots (all 16)". The referee checked the
     ten untested pairs.
   - Scope "obstruction learned" (Position, the G1 and G16 checkpoint, A97's narrowing) to such laws.
   - Record that, on the referee's probes, a sparse random mix of signed knots into NAE looks disordered, and so does one periodic
     law on a 2 × 2 cell (p3 at one up knot per cell). So direction 1 is the live candidate for the premise's positive case.

   **Narrowing.**
2. **P7.**
   - Record that λ₁ is the mode a single distinction feels and that the miss is the period-three oscillation.
   - Qualify "the distances that do step outward" for OR and hard hexagons as holding in envelope.

   **Narrowing.**
3. **The frozen laws.**
   - Say the frozen readings are exact (spectral radius exactly 1; exactly 2 on two live rows for NAE up, place 1 odd down).
   - Replace "each row fixes the next exactly" with "on a torus every row equals the next".
   - Correct NAE up, place 1 odd down to 1.0595 at width 12, and add that it has no state at odd widths.

   **Not a block.**
4. **P2's wording.** Every odd width, and NAE's numbers. **Not a block.**
5. **Small slips.** L1's count (4), L2's "violated", `check.py`'s docstring, the amendment's time and `run.py`'s docstring.
   **Not a block.**

## How the work was split

- **The referee:**
  - read the pre-registration, the proof, `check.py`, `lawlib.py`, `run.py`, the results, the amendment's diff and the note;
  - checked L1 to L3 by hand;
  - wrote its own transfer matrices, exact frozen test, spectral-amplitude analysis, census, the 16-pair scan, and the mixed and
    periodic probes.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_laws.py` and `.json`:**
  - L1;
  - the twelve laws at widths 3 to 12, with the exact frozen test and torus counts to L = 7;
  - the agreeing-signs law against NAE at every width;
  - the single distinction's modes for OR and hard hexagons;
  - the census.
- **`referee_scope.py` and `.json`:**
  - all 16 orientation pairs;
  - uniform random mixes;
  - the gauge control.
- **`referee_mix.py` and `.json`, `_runs.jsonl`, `_long.jsonl`:** NAE with a density ε of signed knots, the product transfer and
  its checks, and the 5,000-row survival runs.
- **`referee_periodic.py` and `.json`:** one signed up knot per 2 × 2 or 3 × 3 cell.

Reproduce, from the repository root, inside `research/WEAVE-LAWS-20261117-001/referee-R1/`:

```sh
../../../.venv/bin/python -B referee_laws.py > referee_laws.json
../../../.venv/bin/python -B referee_scope.py > referee_scope.json
../../../.venv/bin/python -B referee_mix.py > referee_mix.json 2> referee_mix_runs.jsonl
../../../.venv/bin/python -B referee_mix.py --long > referee_mix_long.jsonl
../../../.venv/bin/python -B referee_periodic.py > referee_periodic.json
```
