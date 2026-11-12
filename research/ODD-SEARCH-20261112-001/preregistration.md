# Pre-registration: the first odd harmony, or none

Epic `ODD-SEARCH-20261112-001` (`EVEN-PERIOD-20261112-001` direction 1, G8 with G1; program mathematics, group arithmetic), written on
2026-11-12 before the search runs, at the coordinator's go-ahead under the owner's standing mandate. Code frozen with this file in
`proofs/ODD-SEARCH-20261112-001A/ODD-SEARCH-20261112-001A-P001_pattern_sets/` (`odd_lib.py`, `check.py`, `odd_referee.py`). The
canonical K1–K3 test is unchanged.

## Words

As in `EVEN-PERIOD-20261112-001`: harmony (A70), word, compatible, flippable, certificate. A **pattern** is a set of three residues
{0, a, b} modulo an odd p up to translation; a word c is compatible with a set P of patterns when it is non-constant on every
translate of every pattern of P. D(d) is the number of residues x with c[x] ≠ c[x + d]. The **defect number** of c is p − max D(d),
the number of doubled letters c[x] = c[x + 1] after a multiplier makes the difference 1 the one that changes most often.

## The question

`EVEN-PERIOD-20261112-001` proved that no not-all-equal harmony has a state of odd period up to 29, and that the statement at an odd
period p is equivalent to: every word of period p has a certificate. Is it true at every odd period, or is there a first odd harmony?

## Both outcomes are results (frozen)

- **A general construction of certificates is a theorem**: no not-all-equal harmony along one shift has an odd period.
- **A first odd harmony overturns "the law's numbers are even" past 29.** It would be a correction of kind **Narrowing**, logged in
  `docs/CORRECTIONS.md` and reported: the published lines that say the knot law's harmonies are even (the intuition entries of
  `HARMONY-ARITH-20261112-001` and `EVEN-PERIOD-20261112-001`, the G8 lines of the goals document) would be narrowed to periods below the
  first odd harmony, which is not a block of the theory under test.
- **Neither, in range, is evidence only.**

## Tools, before the freeze (proved by hand or from the advisor, and disclosed)

The advisor model (Fable 5.2) was consulted cold twice before this freeze (the rule since 2026-11-12). Its suggestions below were
checked here.

- **Lemma 5 (one flip is a neighbour).** For odd p, a residue r of a compatible word c is flippable exactly when c with residue r
  flipped is also compatible (every triple has three distinct residues). So a word has a certificate exactly when its compatible set
  holds two words that differ in one place.
- **Lemma 6 (closure; the advisor's).** If a set P is a counterexample (some compatible word, none with a flippable residue), so is
  the set of all patterns any of its compatible words satisfies: it has fewer compatible words and stricter flips. So the search may
  run over words, with P the word's own patterns, and is exhaustive at a period when it covers every word.
- **Lemma 7 (compatibility by differences; the advisor's identity).** Over the p translates of {0, a, b}, a constant triple has no
  differing pair and any other has exactly two, so c is compatible with {0, a, b} exactly when D(a) + D(b) + D(b − a) = 2p, its
  largest possible value. Checked against 58,396 direct tests on `EVEN-PERIOD-20261112-001`'s data: no disagreement.
- **Consequences used.** A word with a compatible pattern has 3·max D ≥ 2p, so its defect number is at most p/3. At a prime p every
  word is the image under a multiplier of a word whose difference 1 changes most often, so enumerating every word of each odd defect
  number k ≤ p/3, normalised that way, covers every word with a pattern.
- **Lemma 8 (one defect is never a counterexample; the advisor's).** A word with defect number 1 is a multiplier image of an interval
  word 1^n 0^(p−n), n ≤ (p − 1)/2, whose D(d) = 2 min(|d|, n); lengthening the interval by one never lowers a D(d), so every compatible
  pattern stays compatible and the two words differ in one place.
- **The parity route (the advisor's, not a proof).** Compatible words are closed under flipping every value, and a word and its flip
  have weights of different parity because p is odd. If they are joined by steps of one or two changed places through compatible words,
  some step changes one place, which is a certificate (lemma 5).

## The search (frozen; exact)

- **Complete at p = 31 and 37** (prime): every word of every odd defect number up to p/3 (k ≤ 9 at 31, k ≤ 11 at 37), one per
  rotation class of its doubled letters, normalised; its patterns by lemma 7; whether it has a flippable residue; for a fully blocked
  word, the two SAT calls of `odd_lib.test_set` (is there a compatible word with residue 0 flippable).
- **Targeted, partial:** p = 41 and 43 with k ≤ 9, p = 47 with k ≤ 7 (small defect numbers first, as the advisor advised); and the
  advisor's family of progression patterns {0, a, 2a} with steps {1} ∪ A, |A| = 1 to 3, at every prime p from 31 to 61, tested by
  the same two SAT calls on the set itself.
- **Measured, not predicted:** for every fully blocked word, whether it reaches its flip through compatible words by steps of one or
  two changed places (the parity route), with the compatible set enumerated up to 200,000 words.
- **Caps, set now.** Each part 4 hours and 16 GB by its systemd unit; registered as long-running. A part over its cap is reported as
  dropped and its range as unsearched.

## Predictions and failure criteria

- **S1.** No counterexample at p = 31 or 37 (complete). Predicted: none, weakly (the advisor rates counterexamples plausible in the
  30s). If one is found, the first odd harmony is the base of all kinds of span less than p that its word satisfies (lemma 4 of
  `EVEN-PERIOD-20261112-001`); it is then verified by enumerating that base's compatible words and checking that no two differ in one
  place, refereed, and the Narrowing above is logged.
- **S2.** No counterexample in the targeted ranges. Predicted: none, weakly. These ranges are not complete, so none found there is
  not a theorem.
- **Control.** The same two SAT calls flag the five even harmony words (01, 0011, 000111, 00001111, 00101101) with their own residue
  pairs as counterexample-type (a compatible word, none with a flippable residue), and flag no word of odd period up to 29; checked
  before the freeze on the five and on every pattern set of up to three patterns at odd periods 5 to 21 (none flagged).
- **Answer by rule.** S1, S2, the measured route, the proof attempt. Stop there; report and hold.

**Referee.** Fresh code (`odd_referee.py`): every fully blocked word's patterns and blocking recomputed directly, every certificate
checked, a sample of words at p = 31 and 37 recomputed without the fast identity; and an independent fresh session, as for
`EVEN-PERIOD-20261112-001`.

Known mathematics, checked before the freeze: as for `EVEN-PERIOD-20261112-001`, and colourings of cyclic groups avoiding monochromatic
three-term progressions with given steps (van der Waerden-type questions on Z_p), the nearest literature to the progression family.

Assumptions in force: A70. Nothing here bears on P versus NP.
