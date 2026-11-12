# Symmetric step sets that make a harmony

Status: Proved (three odd harmonies, of periods 61, 73 and 193, by lemma 4 of `EVEN-PERIOD-20261112-001` with exact enumeration),
with a frozen exact scan of two families, refereed twice. Ticket A of `research/ODD-FAMILY-20261112-001/preregistration.md`, frozen
with the code in commit `3cec8a886` before any run. `check.py --part scan|verify|counts|explain|summary|referee` reproduces each part.

Words, as in the pre-registration: harmony (A70), word, compatible, flippable, steps, makes a harmony, class (a word's rotations and
their flips), multiplier, stabiliser. Below, i denotes a fourth root of 1 modulo a prime p ≡ 1 mod 4 (i² ≡ −1), H = {±1, ±i}, and a
step written a + bi means the residue a + b·i mod p.

## 1. The tool

- **Lemma 4 at any odd n.** If S makes a harmony at an odd n (some compatible word, none with a flippable residue), every state of
  K_S repeats with a period dividing n. The proof of `EVEN-PERIOD-20261112-001` uses only that n consecutive positions hold every
  residue once, which needs n odd, not prime; the independent session rechecked it here and found no gap.

## 2. The scan (exact, frozen)

| Range | Values of n | Sets | With a compatible word | Make a harmony |
| --- | --- | --- | --- | --- |
| odd n from 33 to 59 | 14 (8 composite) | 5,964 | 4,965 | **0** |
| primes from 61 to 199 | 29 | 82,372 | 71,640 | **7**, at 61, 73 and 193 |

The sets are counted as the scan lists them (one per normalised union of cosets, and the doubled steps not already listed); the
referee's own count of the same families up to a multiplier is 31,104. Up to a multiplier, **exactly one set makes a harmony at each
of 61, 73 and 193**, and none anywhere else in range.

## 3. The three harmonies (proved; checked twice)

| n | Steps up to sign | As {steps}·H | Kinds | Compatible words | Classes | Least distance | Least period | Splits? |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 61 | 1, 2, 11, 22 | {1, 2}·H, i = 11 | 12 | 122 | 1 | 11 | 61 | no |
| 73 | 1, 2, 19, 27 | {1, 2}·H, i = 27 | 12 | 730 | 5 | 8 | 73 | no |
| 193 | 1, 2, 31, 54, 65, 81 | {1, 2, 4 + 3i}·H, i = 81 | 18 | 386 | 1 | 19 | 193 | no |

- **Each is a harmony.** No two compatible words differ in one place, so by lemma 4 every state of K_S repeats with period n; every
  word is non-constant and n is prime, so its least period is n. Checked directly: on a window of 3n distinctions (and of 4n by the
  referee, and of n + 1 by the independent session) no state has x_m ≠ x_(m+n).
- **None splits:** the kind (0, 1, 2) alone gives offsets of greatest common divisor 1.
- **73 is not one symmetric class.** Of its 5 classes only one is unchanged, up to a shift, by multiplying positions by i; the other
  four are permuted by it in one cycle. So a harmony needs neither a single class nor symmetric states.

## 4. The predictions (frozen; F1 to F5 and F7 the advisor's)

| Item | Prediction | Outcome |
| --- | --- | --- |
| F1 | none with at most two steps up to sign | **held** |
| F2 | every one is {±s, ±2s, ±t} or {±s, ±2s, ±t, ±2t} | **failed** at 193 (six steps up to sign) |
| F3 | none with a stabiliser of order 6 or more | **held**: every one has stabiliser exactly H |
| F4 | stabiliser of order 4: only H ∪ 2H or H ∪ 2⁻¹H | **failed** at 193 (three cosets of H) |
| F5 | H ∪ 2H: compatible words usually at 73 to 113, at most one or two further primes with a harmony; from 137 on, words exist and never a harmony | **held** beyond the pre-freeze 41 and 53: one further prime, 73; from 89 on more than 200,000 words and no harmony |
| F6 | none at an odd n from 33 to 59 | **held** (both families) |
| F7 | some set makes a harmony at a prime other than 61, among the doubled steps with t² ≠ −1 | **failed in part**: two other primes (73, 193), but no set with stabiliser {±1} |

## 5. The counts of H ∪ 2H

| p | 41 | 53 | 61 | 73 | 89 to 197 (12 primes) |
| --- | --- | --- | --- | --- | --- |
| Compatible words | 1,804 | 0 | 122 | 730 | over 200,000 at each |
| Classes, with a flippable residue | 22, all | — | 1, none | 5, none | — |
| Words fixed by every element of H | 0 | 0 | 2 | 2 | 0 to 1,286 (0 at 97) |

The advisor's mean-field rate (about 1.074^p words) is far off: 0 at 53, more than 200,000 at 89. Counts are irregular in p, and the
harmony property holds at 61 and 73 only.

## 6. One explanation attempt (frozen tests X1 to X5)

- **X1 (exact).** 11² ≡ −1 and 6 + 5·11 = 61, so x = a + 11b identifies Z_61 with pairs of integers modulo (61, 0) and (−11, 1), and
  S = {±1, ±2} ∪ 11·{±1, ±2}: a word is compatible exactly when, read along each of the two shifts (step 1 and step 11), it has no
  000, 111, 01010 or 10101. Checked on all 122 words. Along one shift such words grow as λⁿ, λ³ = λ² + 1 (λ ≈ 1.4656; checked).
- **X2.** At 61, 2 of the 122 words are fixed by every element of H (one class, centred at 0); at 73 also 2 of 730.
- **X3 (the advisor's difference-set test).** Not a difference set: in base-2 logarithms the 7 cosets of the lighter half give
  difference counts 2, 3 and 4.
- **X4.** Every set found has stabiliser exactly H, at primes ≡ 1 mod 4; none with stabiliser {±1}, none at a prime ≡ 3 mod 4 or a
  composite n.
- **X5 (descriptive).** Lifted to 305 = 5·61 with S' = {±1, ±2, ±t, ±2t}, t² ≡ −1 mod 305, the 61 word stays compatible with no
  flippable residue, but S' does not make a harmony at 305: other compatible words have one.
- **Verdict by rule: neither reading.** R2 (near threshold) needed a set with stabiliser {±1} (none) and R1 (the multiplier) needed a
  difference set (not one) and at most one class at most large primes (more than 200,000 words). What the tests do show: within the
  families every harmony has the fourth roots of 1 as its stabiliser, and that symmetry is not enough (H ∪ 2H fails at 14 of the 16
  primes 1 mod 4 from 41 to 197) and does not act by making the states symmetric (73).

## 7. The referees

- **Fresh code (`fam_referee.py`), passed.** Its own generation of both families up to a multiplier (31,104 sets), its own clauses
  and Glucose 4: the same sets make a harmony, at 61, 73 and 193 only; for every one, every compatible word enumerated and checked in
  plain Python, no two one place apart, no state breaking the n-repeat on a window of 4n; 30 flippable pairs per n checked in plain
  Python; the counts of H ∪ 2H agree to 73 (both over 20,000 words from 89).
- **An independent session (`independent_referee/report.md`), passed.** From scratch: the kinds (12 and 18), the counts and classes
  (730 in 5; 386 in 1), least distances 8 and 19, the window lemma sound, SAT on windows of 4n and n + 1 finds no state breaking the
  repeat, gcd 1, and no harmony from H ∪ 2H at 89 or 97. It noted that at 67 and 71 the steps {±1, ±2, ±3} allow no state at all,
  so they are vacuously a harmony under the bare definition; the definition used here requires a compatible word, which excludes them.

## 8. After the run (descriptive; the advisor's reading, checked here)

The advisor model was consulted after the run with the results (its answer is a colleague's view, not evidence); these parts were
checked here.

- **Along one shift there is always a free place (the advisor's lemma, checked to n = 23).** A word avoiding 000, 111, 01010 and
  10101 has a place whose flip keeps it so unless its runs read 2, 2, 2, … or 1, 1, 2, 1, 1, 2, …, which needs n divisible by 4. So
  at odd n the steps {±1, ±2} never make a harmony, and in a harmony containing them the places free under steps 1 and 2 are
  pinned by its other steps. Checked by
  enumeration for every odd n from 5 to 23.
- **The symmetric 61 word, by hand.** Assuming the word is unchanged by multiplying positions by 11, the advisor forced every value
  without branching; its word matches the symmetric word found here. It cannot flip: the places free along the first shift are
  ±{1, 6, 9, 12, 27} and 11 times them are ±{5, 8, 10, 11, 23}, disjoint, so each place is pinned along one of the two shifts
  (checked). A proof without enumeration would still need every compatible word to be symmetric about some place, which holds at 61
  (by enumeration) but fails at 73.
- **A rule to test later (the advisor's conjecture, fitted after the fact).** H ∪ 2H makes a harmony exactly when exactly two words
  are fixed by every fourth root of 1; on the 16 primes counted here that holds (two at 61 and 73 only). Its second conjecture: none
  from 89 on. Neither is tested here.
- **The nearest named property.** No two solutions one place apart is the property that locked constraint satisfaction problems have
  by construction (Zdeborová and Mézard, 2008, where solutions are pairwise at least two places apart); here it arises in a
  not-all-equal system, which is not locked, from the arithmetic of its steps. Pointer from the advisor; not yet read against this
  record.

## What this establishes

- Proved: odd not-all-equal harmonies of periods 73 and 193 exist, unsplit (with `ODD-SEARCH-20261112-001`'s 61, three).
- Exact, within the two frozen families: odd harmonies at 61, 73 and 193 only, for every odd n from 33 to 59 and prime from 61 to 199;
  each from steps closed under multiplying by a fourth root of 1.
- Not established: the least odd period of a harmony (still 61, or one of 33, 35, 39 to 59 outside these families); why the fourth
  roots matter; whether a harmony can have stabiliser {±1}.
