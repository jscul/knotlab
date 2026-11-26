# Preregistration: rule R over the closed census (part E)

Frozen before `rule_census.py` is run over the census. Written 26 November 2026; revised after the advisor's reading, before the run.

## What is run

`rule_census.py` over every type of the 20 November census (`FOUR-READINGS-20261120-001A`, `census.json`: 173 closed,
twice-held, simple, connected patterns with at least three places per holder and at most seven holders), the eight-knot
closure of three-label subsets, and the three patterns of `parts.py`. **Rule R:** the values of two distinctions commute
exactly when some knot holds both. Per pattern:

- **R1:** under R, do the knots' operators (each the product of its places' operators) commute pairwise?
- **R2:** if so, the parity R forces on the sum of the knots' signs. With every older knot even, that is the closing
  sign, by the identity checked in `values_commute.py` (the product of all knots' operators is (−1)^c, c the non-commuting
  pairs whose two occurrences interleave in the closing sum).
- **R3:** with any choice of which unheld pairs fail to commute (pairs held by a common knot always commute) and every
  knot pair commuting, is an odd sum attainable? (Exact, GF(2).)

Two weightings, both named: one vote per type, and one vote per labelled pattern (the census's `labelled` count).

## Seen before freezing (code checks, not predictions)

The four-knot closure (every two of four knots share one distinction): R1 yes, R2 odd, R3 odd attainable. The five-knot
closure: R1 yes, R2 odd. The eight-knot closure: R1 no, R3 odd attainable. These came from `values_commute.py` and a
check that `rule_census.analyse` agrees with it.

## Revised after the advisor (before the run)

The advisor read the design ([question](advisor_question.md), [answer](advisor_answer.md)) and found three things, taken
here: the first prediction 3 below was entailed, not a test (R3's constraints are the swaps of two knots in the order of
the closing sum, so an odd sum is attainable exactly on patterns that are not outerplanar, and no simple pattern with
three places per holder is outerplanar); R1 is not the marker of where part counting overshoots; and R changes at a
birth. Its by-hand derivations are now predictions to check. The first-written predictions are kept, struck where
replaced.

## Predictions (frozen)

1. Under one vote per type, R1 holds at fewer than half of the 173 types (my guess; the advisor could not count it).
   **Added:** `rule_census.py`'s R1 agrees on all 173 types with the advisor's closed form (knots that share:
   (d_u − 1)(d_v − 1) ≡ t; knots that do not: d_u·d_v ≡ t, mod 2, t their common neighbours).
2. ~~Where R1 holds, R2 is odd at some type other than the four- and five-knot ones, and even at some type.~~ **Replaced
   by the advisor's derivation:** R1 with R2 odd at K6, K7 and K1,3,3 (the literature's names for every two of six,
   every two of seven, and one knot meeting all of two groups of three that meet each other across); R1 with R2 even at
   K3,4 (two groups of three and four, every cross pair meeting), which is nonplanar, so its stored witness is
   signed-identity positive while R forces the even sum there.
3. ~~R3 holds at every one of the 173 types.~~ (Entailed.) **Replaced:** R3 holds exactly where the pattern is not
   outerplanar: at all 173 types and the eight-knot closure, and fails at the outerplanar controls (rings of three, four
   and five knots with each meeting doubled, a ring of four with each meeting tripled) and at the two-reader pattern.
4. The two-reader pattern of `parts.py`: R1 fails and R3 fails. The three-reader pattern and the nine-distinction square:
   R1 holds and R2 is odd.
5. **Added:** planar exactly at the 58 types without a signed-identity reading (Arkhipov's criterion against the stored
   verdicts).
6. **Added (shuffle test):** where R1 holds, R2 is unchanged under 20 seeded relabellings of knots, distinctions and the
   order of places (seed 20261127).
7. **Added:** under R no knot of the four-knot closure commutes with every value (the reading needs a state), and every
   knot of the five-knot closure does (each knot a signed identity).
8. **Added (part counting against the state):** two four-knot closures sharing one knot: R1 holds; reading the shared
   knot's six places, part counting allows 32 words and the stabilised state 16.

## What would change the reading

- If R1 fails at every reached type but the four- and five-knot ones, R is a rule for those two closures only.
- If prediction 3 fails on a control, the outerplanar account of where an odd sum is attainable is wrong.
- If prediction 8 fails, part counting and the state's counts agree even where a product of knots lies in the read set.

## Scaffolds named

The census's restriction (simple sharing, at most seven holders, three places per holder); the word order of the
closing sum (knot by knot, places in index order; the parity is order-free when R1 holds); R itself, beside the current
rule (every pair commutes) and the free choice of R3.
