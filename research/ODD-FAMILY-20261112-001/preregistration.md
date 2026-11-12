# Pre-registration: which odd periods the knot law makes, and why 61

Epic `ODD-FAMILY-20261112-001` (`ODD-SEARCH-20261112-001` directions 1 and 2 taken together, G8 with G1; program mathematics, group
arithmetic), written on 2026-11-12 before the scan runs, at the coordinator's go-ahead under the owner's standing mandate. Code
frozen with this file in `proofs/ODD-FAMILY-20261112-001A/ODD-FAMILY-20261112-001A-P001_symmetric_steps/` (`fam_lib.py`, `check.py`,
`fam_referee.py`). The canonical K1–K3 test is unchanged.

## Words

As in `ODD-SEARCH-20261112-001`: harmony (A70), word, pattern, compatible, flippable. For an odd n and a set S of nonzero residues
closed under negation (its **steps**), a word of period n is compatible with S when it is not constant on any progression
{x, x + s, x + 2s} with s in S (the literature's 2-colouring of Z_n with no monochromatic progression of those steps). S **makes a
harmony at n** when some word is compatible with S and no compatible word has a flippable residue. Then the base K_S of all knot kinds
(0, a, b), b < n, whose residues form a translate of {0, s, 2s} with s in S, is a harmony all of whose states repeat with a period
dividing n: this is lemma 4 of `EVEN-PERIOD-20261112-001`, whose window argument uses only that n is odd (each n consecutive positions
hold every residue once), not that n is prime. A **class** of words is a word's n rotations and their flips. A **multiplier** is a
unit u of Z_n acting by x ↦ ux; the **stabiliser** of S is the set of multipliers with uS = S, and S is a union of cosets of a
subgroup H exactly when H lies in it.

## The question

`ODD-SEARCH-20261112-001` found the first known odd harmony: steps S = {±1, ±2, ±11, ±22} at 61, where {±1, ±11} = H is the group of
fourth roots of 1 modulo 61 and S = H ∪ 2H. Which numbers does the knot law make as periods of harmonies, and what decides it? Bounded
here to: (1) symmetric step sets at every odd n from 33 to 59 and the same family at every prime from 61 to 199; (2) one attempt to
explain why 61 works. No full classification is sought.

## The families (frozen)

- **Cosets.** For every subgroup H of the units containing −1 (each ⟨u, −1⟩), every union of one, two or three cosets tH (t any
  nonzero residue; for composite n, t may be a non-unit), a union containing a unit coset normalised by a multiplier to contain H.
- **Doubled steps (the advisor's).** S = {±1, ±2, ±t} and S = {±1, ±2, ±t, ±2t} for every t.
- **Range.** Every odd n from 33 to 59 (prime and composite) and every prime from 61 to 199. For each set, the two SAT calls of
  `ODD-SEARCH-20261112-001`'s `odd_lib.test_set` (is there a compatible word; is there one with residue 0 flippable).
- **Every set found to make a harmony** is verified: every compatible word enumerated (up to 10⁶), none differing from another in
  one place; the least periods of its words; a direct check on a window of 3n distinctions with every knot inside it that no state has
  x_m ≠ x_(m+n) in the middle; the greatest common divisor of its offsets (1: the harmony does not split).
- **Counts.** For H ∪ 2H (H the fourth roots of 1) at every prime p ≡ 1 mod 4 from 41 to 199: the number of compatible words and
  classes (capped at 200,000 words), the number of classes with a flippable residue, and the number of words fixed by every fourth root
  of 1.
- **Caps.** Each part 2 hours and 16 GB by its systemd unit, registered as long-running if it passes ten minutes. A part over its cap
  is reported as dropped, its range as unsearched.

At the primes from 31 to 59, `ODD-SEARCH-20261112-001` already tested every set of at most four steps up to sign (its progression
family) and none made a harmony. The new ground below 61 is the composite n (33, 35, 39, 45, 49, 51, 55, 57) and unions with more
steps.

## Predictions and failure criteria (frozen)

The advisor model (Fable 5.2) was consulted cold before this freeze (the rule since 2026-11-12); F1 to F5 and F7 are its predictions,
recorded as its, and F6 is this epic's.

- **F1.** No set with at most two steps up to sign makes a harmony.
- **F2.** Every set found is {±s, ±2s, ±t} or {±s, ±2s, ±t, ±2t} for some s and t (up to a multiplier, {±1, ±2, ±t} or
  {±1, ±2, ±t, ±2t}).
- **F3.** None has a stabiliser of order 6 or more (the analogue of H ∪ 2H with |H| = 6 is predicted too constrained).
- **F4.** A set whose stabiliser has order 4 makes a harmony only when it is H ∪ 2H or H ∪ 2⁻¹H, up to a multiplier.
- **F5.** For H ∪ 2H, classes number about 1.074^p/(2p): at 73 to 113 compatible words usually exist, with at most one or two further
  primes where it makes a harmony; at every prime from 137 on, compatible words exist and it never makes a harmony. **Seen before the
  freeze** while testing `count_orbits` (so not tests): at 41, 1,804 words in 22 classes, every class with a flippable residue (the
  advisor had predicted none at 41: its estimate is already off there); at 53, no compatible word; at 61, one class of 122 words.
- **F6.** No set of either family makes a harmony at an odd n from 33 to 59. Predicted weakly: if one does, the least known odd period
  of a harmony falls below 61.
- **F7.** Some set makes a harmony at a prime other than 61 below 200, among the doubled steps with t² ≠ −1. Predicted weakly (the
  advisor's reading below).
- **Control.** At 61 the scan finds H ∪ 2H (known), and nothing at 31 or 37 is re-tested (settled by `ODD-SEARCH-20261112-001`).

## One explanation attempt for 61 (frozen tests)

Two readings, each with what it predicts:

- **R1, the multiplier.** The symmetry x ↦ 11x (11² = −1) is what pins the word: sets that make a harmony have stabilisers larger
  than {±1}; H ∪ 2H has compatible words at isolated primes only, in one class or none; the 61 word's cosets of H form a difference set
  (the advisor's cheap algebraic test: the 7 cosets of its lighter half, in base-2 logarithms, a (15, 7, 3) difference set in Z_15).
- **R2, near threshold (the advisor's).** Since 6 + 5·11 = 61 and 11² = −1, the residues mod 61 are the pairs of integers (a, b) ↦
  a + 11b modulo (6, 5) and (−11, 1), and S = H ∪ 2H is the progression law with steps 1 and 2 read **along two shifts**: along each
  shift a compatible word has no 000, 111, 01010 or 10101 (in the literature, a two-dimensional shift of finite type whose periods
  form the ideal (6 + 5i) of the Gaussian integers). Words along one shift then grow as λ^n with λ³ = λ² + 1 (λ ≈ 1.4656), and the
  mean-field count (λ²/2)^n ≈ 1.074^n sits just above 1: making a harmony is a near-threshold accident, the symmetry its consequence
  (a single class must be fixed by the stabiliser), not its cause. It predicts sets with stabiliser {±1} that make harmonies (F7),
  counts of H ∪ 2H growing with p, and no difference set.
- **Tests.** X1: the reading along two shifts, checked on the 61 words. X2: the words fixed by every fourth root of 1, at 61 and at
  every count prime. X3: the difference-set test on both halves of the fixed 61 word. X4: from the scan, any set that makes a harmony
  with stabiliser {±1}, and the stabiliser of every set found. X5 (descriptive): the 61 word lifted to 305 = 5·61 with
  S' = {±1, ±2, ±t, ±2t}, t² ≡ −1 mod 305, t ≡ ±11 mod 61: whether it stays compatible with no flippable residue (the advisor's
  inheritance), and whether S' makes a harmony at 305.
- **Verdict by rule.** R2 is supported if X4 finds a set with stabiliser {±1}, X3 fails, and H ∪ 2H has more than one class at every
  count prime from 137 to 197 (or passes the cap); R1 is supported if every set found has a stabiliser of order 4 or more, X3 holds,
  and H ∪ 2H has at most one class at most count primes from 137 on. Otherwise neither is decided. Either way the explanation is a
  reading, not a theorem, unless a proof follows.

## Referees

Fresh code (`fam_referee.py`): its own generation of both families up to a multiplier, its own clauses, another SAT solver
(Glucose 4); it recomputes the whole scan and must find the same sets, up to a multiplier; for every set found it enumerates the
compatible words, checks them in plain Python, finds no two one place apart, and checks a window of 4n; it recounts H ∪ 2H at the
primes up to 113. And an independent fresh session, as for `ODD-SEARCH-20261112-001`.

## Known mathematics, checked before the freeze

A bounded search on 2026-11-12 found no statement of this property (a progression law on Z_n whose compatible words have no
flippable residue). Nearest: colourings of Z_n avoiding monochromatic progressions of every step (arXiv 2509.14595, 1107.2888);
progressions whose step is restricted to a set (Landman and Robertson, *Ramsey Theory on the Integers*; Brown, Graham and Landman,
1999); colourings constant on cosets of a multiplicative subgroup, used for van der Waerden lower bounds (Rabung, 1979; Herwig, Heule,
van Lambalgen and van Maaren, 2007, "cyclic zippers"); periodic points of shifts of finite type and their involutions (Manada and
Kashyap, arXiv 0801.1060; Adler, Kitchens and Marcus; Boyle and Krieger); frozen variables of random not-all-equal SAT (Achlioptas
and Ricci-Tersenghi; Ding, Sly and Sun); uniquely 2-colourable hypergraphs. A novelty claim, if any, will say "not found in a bounded
search".

Assumptions in force: A70. Nothing here bears on P versus NP.

**Answer by rule.** F1 to F7, the counts, X1 to X5 and the verdict; stop there, report and hold.
