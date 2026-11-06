# Which knots reproduce themselves under shared subdivision of the triangular lattice

Status: Proved

Ticket `SHARED-SUBDIVISION-20261029-001A`, 2026-10-29.

## Standard statement

On the triangular-lattice torus of side m, put copies of a three-bit knot K on triangles:
- **S2.** On every up triangle, one coordinate order (34 rules).
- **S1.** On every triangle, one placement on up triangles and one on down triangles, from one class (88 rules).

Cut every triangle into k² triangles, the new vertices shared between neighbours. The result is the torus of side L = k·m, carrying the
same rule, and the coarse sites are the fine sites (k·i, k·j).
- **Set-level exact.** The fine solutions restricted to the coarse sites are exactly the coarse solutions.
- **Counted exact.** In addition, every coarse solution has the same number of fine extensions.

The census decides both for all 122 rules at scale 2 (tori of side 6 and 8) and scale 3 (side 9). It also records solution counts on
tori of side 2 to 11 and whether the solution sets on tori of side 3 to 6 are affine.

## Nearest known result

- **Parity on up triangles** is the triangular plaquette model of Newman and Moore (1999). Its zero-temperature states are
  Pascal's triangle mod 2, which is self-similar under rescaling by 2 (linear cellular automata: Willson; Allouche et al.). Its
  ground-state degeneracy depends on the torus size (Sfairopoulos et al., arXiv 2301.02826).
- **Parity on all triangles** has the zero-temperature states of the Baxter–Wu model: four on tori whose side is divisible by 3.
- **Not-all-equal on all triangles** is Wannier's triangular antiferromagnet at zero temperature, with positive entropy.
- **Exact real-space renormalization** on two-dimensional lattices is rare.
- **Not found.** A census of which hard constraint laws are exact under shared subdivision.
- **Classification.** No overlap found for the census (candidate local delta). The individual exact families are classical or
  elementary (ticket B).

## Theorem 1 (the census; computation)

Exact counts for all 122 rules (checks 2 to 4):
- **Scale 2 (tori of side 6 and 8).** Exactly 22 rules are exact, and on both tori. Set-level and counted exactness coincide:
  - S2: parity on up triangles, both parities (2);
  - S1: parity on all triangles (2), the two three-excluded classes (12 placement pairs), twisted not-all-equal (6 placement
    pairs).
- **Scale 3 (torus of side 9).** Exactly 6 rules are exact: the six twisted not-all-equal pairs. Both parity rules and the
  three-excluded rules fail at scale 3.
- **Every other rule fails at both scales.** Not-all-equal on all triangles (Wannier's antiferromagnet) is the clearest case: its
  fine solutions restrict to 21,510 forbidden coarse assignments on the 8-torus and 470 on the 9-torus.

## Theorem 2 (what the exact rules share; computation)

- **Affine.** Every exact rule has an affine solution set (a coset of a linear subspace) on the tori of side 3 to 6. Every other
  rule has a solution set that is not affine on some torus of side 3 to 6 (check 6). In this family, exact and affine coincide.
- **Zero entropy density.** Every exact rule has at most 2^L solutions on the L-torus for L = 2 to 11, so at most 0.091 bits per site
  at L = 11 (check 5). No rule with more than 0.1 bit per site is exact. The converse fails: some rules with low entropy are not
  exact.
- **Three families (check 7):**

| family | rules | solutions on the L-torus (L = 2..11) | exact at scale 2 | exact at scale 3 |
| --- | --- | --- | --- | --- |
| parity on up triangles | 2 | 1, 4, 1, 1, 16, 64, 1, 4, 1, 1 | yes | no |
| frozen: at most four solutions (parity and three-excluded on all triangles) | 2 + 12 | 1, 4, 1, 1, 4, 1, 1, 4, 1, 1 | yes, one extension each | no |
| line-constant (twisted not-all-equal on all triangles) | 6 | 2^L | yes, 2^(L/2) extensions | yes, 2^(2L/3) extensions |

Entropy per site at L = 11, largest over the placements of each class (check 5; bits):

| class (excluded) | S2 | S1 |
| --- | --- | --- |
| {000} or {111} | 0.860 | 0.822 |
| {001}, {011} (asymmetric atoms) | 0.773 | 0.721 |
| {001, 010}, {011, 101} | 0.642 | 0.588 |
| no lone one, no lone zero | 0.528 | 0.481 |
| x or (y ≠ z), both classes | 0.522 | 0.335 |
| twisted not-all-equal {001, 110} | 0.469 | 0.469 (six exact pairs 0.091) |
| not-all-equal {000, 111} | 0.464 | 0.464 |
| three excluded, both classes | 0.300 | 0.064 (twelve exact pairs 0) |
| parity, both classes | 0 | 0 |

## Method

- **The torus.** Rows of the L-torus are states of a transfer matrix T (2^L states). Coarse rows are the values at columns 0, k, 2k,
  and so on of every k-th row.
- **Counting extensions.** The number of fine extensions of a coarse assignment is the trace of a product of the matrices T^k
  restricted to the coarse values.
- **Exact arithmetic.** It is computed in floating point, for the support (all terms are nonnegative, so zero is exact), and modulo
  four primes below 2^18, where every product and sum stays below 2^53, so the residues are exact.
- **Validation.** Check 2 compares 854 sampled assignments, across all rules and tori, with an independent count in Python integers.
  All agree.
- **Solution counts and affineness.** Solution counts are traces of T^L. Affineness compares |S| with 2^rank(S − s₀) over the
  two-element field, on enumerated solution sets.

## Reading

- **On genuinely two-dimensional space, exact self-reproduction is rare and degenerate.**
  - Of 122 rules, 22 survive at scale 2 and 6 at scale 3.
  - All are affine and have zero entropy density.
  - Each is parity, behaves as parity on tori, or collapses into equality lines (ticket B).
- **Not-all-equal never reproduces itself.** Neither do any of the laws with positive entropy.
- **Exactness depends on the scale.** It is arithmetic, not geometric: parity's exactness at scale 2 does not survive scale 3.

## Checks

`check.py` (numpy) on `shared_lib.py`, with `result.json` (one row per rule):
- **0.** The dependency artifacts are bound by hash.
- **1.** 34 knots in 16 classes and 122 rules.
- **2.** The engine agrees with the independent exact count on 854 sampled coarse assignments.
- **3 and 4.** Exactness at scale 2 (6- and 8-tori) and scale 3 (9-torus) for every rule.
- **5.** Solution counts for L = 2 to 11 and entropy per site.
- **6.** Affineness on the 3- to 6-tori.
- **7.** The families of the exact rules.
- **8.** Controls:
  - not-all-equal gains forbidden coarse assignments at both scales;
  - no rule above 0.1 bit per site is exact.

## Provenance and novelty

| Result | Where it came from | Novelty |
| --- | --- | --- |
| Theorem 1 | Exact census of the program's knot classes under shared subdivision | Candidate local delta |
| Theorem 2 | The same census: affineness, solution counts | Candidate local delta; the families are classical (ticket B) |

## What this does not show

- **Larger tori.** Exactness on larger tori. Ticket B proves it for every torus in the parity and line-constant families.
- **Other substitutions.** Other subdivisions, other lattices, or rules mixing knot classes.
- **Why exact and affine coincide.** It is observed in this census, not proved.
