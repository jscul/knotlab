# Searching words of odd period for one without a certificate

Status: Proved (lemmas 5 to 8 by hand; the period-61 harmony by lemma 4 of `EVEN-PERIOD-20261112-001` with an exact check), with an
exact search, refereed. Ticket A of `research/ODD-SEARCH-20261112-001/preregistration.md`, frozen with the code in commit `be4f5a9d3`
before any run. `check.py --part p31|p37|targeted|ap|route|summary|referee` reproduces each part.

Words, as in the pre-registration: harmony (A70), word, pattern, compatible, flippable, certificate, D(d), defect number.

## 1. Tools (by hand; three from the advisor model, checked here)

- **Lemma 5.** For odd p a residue of a compatible word is flippable exactly when flipping it leaves a compatible word.
- **Lemma 6 (the advisor's).** A counterexample set may be taken closed under the patterns of its compatible words, so a search over
  words, each with its own patterns, is exhaustive at a period it covers.
- **Lemma 7 (the advisor's).** c is compatible with {0, a, b} exactly when D(a) + D(b) + D(b − a) = 2p. Checked on 58,396 cases with no
  disagreement before the freeze, and the fast autocorrelation code agrees with the direct code on every word at periods 17 and 19.
- **Lemma 8 (the advisor's).** A word of defect number 1 is never a counterexample (an interval word grows by one place).

Proofs are in the pre-registration.

## 2. The search (exact, frozen)

| Range | Words | With a pattern | Fully blocked (u not its own certificate) | Without any certificate |
| --- | --- | --- | --- | --- |
| p = 31, every defect number (complete) | 740,777 | 59,198 | 21 | 0 |
| p = 37, every defect number (complete) | 26,760,404 | 887,583 | 93 | 0 |
| p = 41 and 43, defect number at most 9; p = 47, at most 7 (partial) | see `result.json` | | 308 | 0 |
| progression patterns {0, s, 2s}, steps {1} ∪ A, \|A\| ≤ 3, every prime 31 to 59 | 11,911 sets | 9,890 satisfiable | — | 0 |
| the same family at p = 61 | 4,089 sets | 3,608 satisfiable | — | **2** |

- **S1 holds:** no word of period 31 or 37 lacks a certificate, so (lemma 4 of `EVEN-PERIOD-20261112-001`) no not-all-equal harmony
  has a state of period 31 or 37.
- **S2 fails:** two progression sets at p = 61, steps {1, 2, 11, 22} and {1, 11, 25, 30}, have compatible words but none with a
  flippable residue. They are one set up to the multiplier 30.

## 3. An odd harmony of period 61 (proved; checked twice)

Let K be the 12 knot kinds (0, a, b), b < 61, whose residues form a translate of {0, s, 2s} or {0, −s, −2s} mod 61 with s in
{1, 2, 11, 22}: they forbid three equally spaced equal values with those steps. (The steps are the multiplier subgroup {±1, ±11},
11² = −1 mod 61, and twice it.)

- **Its periodic states.** Exactly 122 words of period 61 are compatible: two orbits of 61, swapped by flipping every value. No two
  differ in one place (the smallest distance is 11, by the independent referee).
- **It is a harmony.** By lemma 4 of `EVEN-PERIOD-20261112-001`, a state of K that does not repeat with period 61 would give two
  compatible words differing in one place, and there are none. So every state K allows repeats with period 61, which is odd. Checked
  directly: on a window of 183 distinctions with every knot inside it, no state has x_j ≠ x_{j+61} in the middle (SAT), and the
  independent referee found the same on windows of 400 and 1,000.
- **It does not split:** the kind (0, 1, 2) alone gives offsets of greatest common divisor 1.
- **Its word** is unchanged, up to a shift, by multiplying positions by 11 or by −1; it has 32 ones; its largest difference count is
  D(2) = 50, so its defect number is 11, beyond the targeted word search, which is why the progression family found it first.

So "the not-all-equal law's harmonies are even" fails: true for every odd period up to 29 (proved) and at 31 and 37 (complete
search), false at 61. Periods 33, 35 and 39 to 59 are not settled.

## 4. The parity route (measured after the run)

Not a proof route as stated. Measured before closing on `EVEN-PERIOD-20261112-001`'s words that need another word's certificate
(descriptive): every one at periods 17 to 21 reaches its flip by steps of one or two places, but 22 of the 66 at period 23 do not;
each of those 22 still has, among its 138 compatible words (48 components of the step graph), a component holding a word and its
flip, which gives a certificate by parity. The period-61 harmony has no such component: its 122 words are at least 11 places apart.
The frozen measurement on this epic's 422 fully blocked words is long-running (row ODD-SEARCH-A2; **pending**) and will be folded in.

## 5. The referees

- **Fresh code (`odd_referee.py`), passed.** All 422 fully blocked words recomputed directly (patterns, every residue blocked,
  certificate valid); 3,000 random words at each of 31 and 37 recomputed without the fast identity, each with a pattern its own
  certificate or listed.
- **An independent session (`independent_referee/report.md`), passed.** From scratch: the 12 kinds; 122 compatible words in two
  orbits swapped by the flip; no two at distance 1 (smallest 11); the window argument airtight; SAT on windows of 400 and 1,000 finds
  no state breaking the 61-repeat; offsets of gcd 1. Verdict: the claim is correct.

## What this establishes

- Proved: an odd not-all-equal harmony exists, of period 61, unsplit, with 12 knot kinds.
- Exact: none of period 31 or 37; with `EVEN-PERIOD-20261112-001`, none of odd period up to 29.
- Open: the least odd period of a harmony (between 30 and 61, not 31 or 37); periods 33, 35, 39 to 59.
