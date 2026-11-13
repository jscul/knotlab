# Codex specification: knots placed by address maps (ADDR-KNOTS-20261113-001A)

You are computing, not designing. Follow this exactly. If anything is ambiguous or seems wrong, do not resolve it: write the
question in `REPORT.md` under "Ambiguities", choose nothing silently, and skip only the affected part.

## Rules

- Work from the repository root `/home/jscul/p-vs-np-contact-first`. Write files **only** inside
  `experiments/ADDR-KNOTS-20261113-001A/ADDR-KNOTS-20261113-001A-E001_addressed_census/codex/` (CODEX below). Modify, move or delete
  no other file. Run no git command that changes anything.
- Use `.venv/bin/python -B` (numpy and python-sat are installed). At most **4 processes** at a time; keep total memory under about
  8 GB. Other studies share the machine. Touch no process you did not start.
- Repository material only; no network. You may read
  `proofs/ADDR-KNOTS-20261113-001B/ADDR-KNOTS-20261113-001B-P001_growing_interfaces/` (`proof.md`, `check.py`),
  `research/ADDR-KNOTS-20261113-001/preregistration.md`, and the `gamma` function in
  `experiments/SHORT-DESC-20261112-001A/SHORT-DESC-20261112-001A-E001_description_census/dlang.py`. Do not read
  `research/ADDR-KNOTS-20261113-001/exploratory/`.
- **Do not run the full job.** Write the code, run the validation gates and the smoke run below, and stop. The full run is launched
  by the thread from your runner, so it must be resumable and independent of your session.

## Objects

- **Addresses.** Level n is the set of binary words of length n, stored as integers 0 .. 2ⁿ − 1 with the **first letter the most
  significant bit**. "Dropping the last letter" is `x >> 1`; "the last letter" is `x & 1`.
- **Automaton.** s state maps 0 .. s − 1; map q has a swap bit `sw[q]` and successors `d0[q]`, `d1[q]`. Applied to an address it reads
  letters from the first: at each letter b it outputs `b ^ sw[q]` and continues with `d0[q]` if b = 0, else `d1[q]`.
- **Words.** The identity `()`, the words of length 1 `(q,)`, and of length 2 `(q, r)`, which applies **r first, then q**. The word
  list W_s is in exactly this order: `()`, then `(0,)` .. `(s−1,)`, then `(q, r)` in lexicographic order of (q, r). |W_s| = 1 + s + s².
- **Placement.** An unordered triple of three distinct words of W_s, stored as the sorted triple of their indices in W_s.
- **Description.** (s, sw, d0, d1, placements), a list of r placements (repeats allowed). Its **key** is (s, sw, d0, d1, the sorted
  set of distinct placements); equal keys are one distinct description, computed once.
- **Level-n pattern.** For every placement (w₁, w₂, w₃) and every address x of length n, the triple (w₁(x), w₂(x), w₃(x)), kept when
  the three are distinct, as a sorted triple; the pattern is the set of kept triples (deduplicated over placements and addresses).
- **Pattern hash.** SHA-1 over the twelve level patterns (each as a C-contiguous int64 array of sorted rows, in lexicographic row
  order, with its level). Keys with equal hashes are one **distinct pattern** in the summary.
- **Automaton class.** The lexicographically least (sw, d0, d1) over the 2·s! transforms: renaming the maps by a permutation π
  (sw′[π q] = sw[q], d0′[π q] = π(d0[q]), d1′[π q] = π(d1[q])), optionally followed by swapping the letters (exchange d0 and d1).
  Stored as a string with s.

## The weighting and the two populations

Fair coins, as in dlang.py's `gamma` (re-implement it; do not import dlang). Each W draw i uses its own `random.Random(f"{seed}-{i}")`.
Bits: gamma counts its bits; a uniform choice among k options costs log₂ k bits (fractional).

1. s = gamma; if s > 5, the draw is **rejected (s)**: record it with its bits and stop.
2. For q = 0 .. s − 1: `sw[q]` one fair bit (1 bit); `d0[q]` uniform in range(s); `d1[q]` uniform in range(s) (log₂ s bits each).
3. r = gamma; if r > 8, **rejected (r)**. For each of r placements: a uniform index into the list of all 3-subsets of
   range(|W_s|) in `itertools.combinations` order (log₂ C(|W_s|, 3) bits). For s = 1, |W_1| = 3 and the only placement costs 0 bits.
4. Total bits = the sum. Sampling by these coins samples descriptions by weight 2^−bits.

- **Population W:** draws i = 0 .. 39,999 with seed `20261113`.
- **Population E:** every automaton with s = 3 in the order `for sw in product((0,1), repeat=3): for d0 in product(range(3),
  repeat=3): for d1 in product(range(3), repeat=3)` (index a = 0 .. 5,831), with 3 placement lists each (j = 0, 1, 2); then every
  automaton with s = 2 in the same order (a = 0 .. 63), with 30 lists each (j = 0 .. 29). List (s, a, j) uses
  `random.Random(f"20261114-{s}-{a}-{j}")`: r = 1 + gamma, capped at 9 (if 1 + gamma > 9, r = 9 and `r_capped: true`), then r
  placements as in step 3. Record its bits as in the weighting (reference only; E is not weighted).

## Settled flags (per key)

- `single_placement`: the key has one distinct placement.
- `first_letter_settled`: in every distinct placement the three words' root swaps (the XOR of the swap bits of the word's maps; 0
  for `()`) are not all equal.
- `s1`: s = 1.

## Activity (exact)

**Letter class** (secondary): over the state maps U occurring in the key's placements.
**Relative class** (primary): over every distinct placement and every ordered pair i ≠ j of its words, the relative map
h = wⱼ wᵢ⁻¹ (apply wᵢ⁻¹ first, then wⱼ), as a product automaton (below); the key's relative class is the largest class over all of them
(finitary < bounded < polynomial, by degree < exponential).

**Product automaton.** An item is (q, +1) (map q) or (q, −1) (its inverse); a product is a tuple of items applied right to left (the
rightmost first). Reading letter b, an item (q, +1) outputs b ^ sw[q] and becomes (d_b[q], +1); an item (q, −1) reading c outputs
c ^ sw[q] and becomes (d_{c ^ sw[q]}[q], −1). A product reads b with its rightmost item, passes each output to the next item to the
left, outputs the leftmost item's output, and becomes the tuple of the items' successors. Its swap is the XOR of its items' swap
bits. Build the states reachable from the start tuple under both letters. For the letter class use the automaton's own maps.

**Class of a start state** (the same procedure for both):
1. A state is **trivial** when no state reachable from it (including itself) has swap 1.
2. The graph on the non-trivial states reachable from the start: an edge to each successor that is non-trivial (two parallel edges
   when both successors are the same non-trivial state).
3. Strongly connected components; a component is **cyclic** if it holds at least one edge (a self-loop counts).
4. If some cyclic component has more edges than vertices (parallel edges counted): **exponential**. Otherwise every cyclic component
   is one simple cycle. No cyclic component (or no non-trivial state): **finitary**. Else degree d = (the largest number of cyclic
   components on one path of the component graph) − 1: d = 0 **bounded**, d ≥ 1 **polynomial** of degree d.

## Per key, per level n = 1 .. 12

- `knots_n`: the size of the level-n pattern; `join_n`: its knots holding an address ending in 0 and one ending in 1.
- `verdict_n`: alive (1), dead (0), or undecided (null). Empty pattern: alive. Otherwise a SAT instance on variables 1 .. 2ⁿ
  (variable x + 1 for address x): for each knot (a, b, c) the clauses [a+1, b+1, c+1] and [−a−1, −b−1, −c−1]; plus the unit clause
  [m+1] for m the smallest address in any knot (complement symmetry). Solver: pysat `Cadical195`, conflict budget **2,000,000** via
  `conf_budget` then `solve_limited`; None is undecided. Record conflicts used if exposed (else null) and wall time. Phase hint: if
  level n − 1 was alive with model M, set phases so that address x takes M's value at x >> 1.
- **Compute every level 1 .. 12, also after a death.**

## Per-key derived fields

- `fate`: F0 if no level has a knot. Else, over the levels with knots in order: F1 if the first is dead; F2 if some level is alive and
  a later one dead; F3 if every one is alive; **FU** if a null leaves the class open (e.g. alive to 11, null at 12; or null at the
  first level with knots). A null after a determined F1 or F2 keeps the class and sets `undecided_after: true`. `return: true` when
  some level is dead and a later one alive.
- `first_death` (the first dead level or null) and `null_before_death: true` when a null precedes it.
- `rho_max` = max over n of knots_n / 2ⁿ; `rho12` = knots_12 / 4096.
- `letter_class`, `letter_degree`, `rel_class`, `rel_degree`, `automaton_class`, `pattern_hash`, the settled flags.
- `join_growth` from (join_10, join_11, join_12): "constant" if equal; "grows" if join_12 ≥ 1.15·join_11, join_11 ≥ 1.15·join_10
  and join_12 > 0; else "other".

## Output layout (resumable)

- `CODEX/addr.py`: the library. `CODEX/reference.py`: the independent plain implementations used by the gates.
- `CODEX/run_census.py --workers K --out DIR`: builds both draw lists deterministically, writes `DIR/draws.jsonl.gz` (per draw:
  population, index or (s, a, j), rejected cause or key, bits, r_capped), then processes distinct keys with K worker processes,
  appending one JSON line per finished key to `DIR/keys/worker-<k>.jsonl` (all fields above, per-level arrays), flushing after each
  line. On restart it reads every finished key and skips it. Memory per worker under 1.5 GB. Order keys so that every worker gets a
  mix (e.g. shuffled with a fixed seed).
- `CODEX/summarize.py DIR`: writes `DIR/summary.json` and `DIR/summary.md` with exactly the pre-registration's tables ("Measures",
  "Predictions and failure criteria", "Matched-density design"): fate shares raw, given s ≥ 2, given s ≥ 3 and given each density
  bin, by count (distinct patterns) and by weight (W's draws; rejected draws excluded and counted); the weight settled by
  construction (s = 1, single placement, first-letter settled); first-death histograms and death-by-level curves by relative class;
  the matched-density cells on E (settled excluded; and included), each with arm sizes, automaton-class counts, undecided counts,
  Δ, the 95% and Bonferroni cluster-bootstrap intervals (2,000 resamples of automaton classes within each arm, percentile, seed
  20261115), the verdict with undecided as dead and as alive, and the combined verdict; the same on W by weight (bootstrap over draws)
  as a secondary; the logistic sensitivity fit (death ~ relative class + bin, cluster-robust by automaton class; if statsmodels is not
  installed, write the design matrix and skip the fit, saying so); each prediction's verdict by its frozen criterion; and the
  measured join growth against the relative class.

## Validation gates (run all; write `CODEX/validation.json` and report in `REPORT.md`)

- **V-act:** 200 random automata (s ≤ 5): for every word of W_s, the vectorised action on all addresses of length ≤ 8 equals the
  plain recursive one in `reference.py`.
- **V-rel:** 200 random (automaton, placement) pairs: each relative map's product automaton acts on all addresses of length ≤ 8 as
  the composition of the actions, with the inverse computed by inverting the permutation.
- **V-sat:** 1,000 random (key, level ≤ 4) instances agree with brute force over all 2ⁿ assignments; 300 instances at levels 9 and 10
  from E (stratified to include dense ones): Cadical195 and Glucose4, both with budget 2,000,000, agree whenever both decide; and
  `conf_budget(10)` on Cadical195 returns None on at least one instance that the full budget decides.
- **V-B0:** run a copy of the proof note's `check.py` placed in CODEX (so it writes its result there) and report its printed line; and
  every smoke key that is `single_placement` or `first_letter_settled` is F3.
- **V-act-class:** 500 random automata (s ≤ 5, U = all maps): θ_n = max over q in U of the number of addresses of length n that hand q
  a non-trivial map, n = 1 .. 160 (exact integers). Finitary ⇔ θ_160 = 0; exponential ⇔ θ_160 ≥ 1000 · θ_80 (and θ_80 > 0);
  bounded ⇔ not finitary and max(θ_81..160) ≤ max(θ_1..80); polynomial otherwise. Any disagreement with the exact letter class fails.
- **V-code:** over W's 40,000 draws (sampling only), the frequencies of s and of r (among draws not rejected for s) agree with
  P(n) = 2^−(2⌊log₂ n⌋+1) by a chi-square test at 0.01, cells with expected count ≥ 5.
- **V-resume:** the smoke run, killed after about half its keys finish and restarted, gives the same records (wall times aside) as an
  uninterrupted run of the same keys.

## Smoke run

300 keys, stratified with seed 20261116: 100 from E with s = 3 and r ≥ 4, 100 uniformly from E, 100 uniformly from W's keys with
s ≥ 2. Run with 4 workers. Report: wall time per key (mean, max, by level), undecided count, the fates, and an estimate of the full
run's time at 8 workers. Then stop.

## REPORT.md

What you wrote, how to launch the full run (exact command), every gate's result, the smoke timings, any binding limitation (conflict
counts, phases), and "Ambiguities" (empty if none).
