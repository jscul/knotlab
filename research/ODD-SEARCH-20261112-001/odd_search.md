# The first odd harmony, or none

Epic `ODD-SEARCH-20261112-001` (`EVEN-PERIOD-20261112-001` direction 1, G8 with G1; program mathematics, group arithmetic), 2026-11-12,
at the coordinator's go-ahead. Pre-registered in [preregistration.md](preregistration.md), frozen in commit `be4f5a9d3` before the
search ran, with both outcomes as results. Proof family: `proofs/ODD-SEARCH-20261112-001A/`.

## Words

As in the guide's glossary and the pre-registration: harmony (A70), word, pattern, compatible, flippable, certificate, defect number.

## The question

`EVEN-PERIOD-20261112-001` proved that no not-all-equal harmony has an odd period up to 29, and that the rule at an odd period holds
exactly when every word of that period has a certificate (a compatible word with a value that can flip unseen). Is it true at every
odd period, or is there a first odd harmony?

## The answer

**There is an odd harmony, of period 61.**

- **The harmony (proved, refereed twice).** Forbid three equally spaced equal values with step 1, 2, 11 or 22, counted modulo 61: 12
  not-all-equal knot kinds of span up to 60. They allow exactly 122 repeating words, one of period 61 with its shifts and its mirror,
  no two of them differing in one place (the nearest are 11 places apart). So no value can flip unseen, and by lemma 4 every state the
  base allows repeats with period 61. It does not split. A SAT search on windows of 183, 400 and 1,000 distinctions finds no state that
  breaks the 61-repeat.
- **None smaller where the search was complete.** No word of period 31 or 37 lacks a certificate (all 740,777 and 26,760,404 words,
  sorted by defect number), so no harmony has period 31 or 37; with the earlier theorem, none has an odd period up to 29. Periods 33, 35
  and 39 to 59 are open; the targeted search at 41, 43 and 47 (small defect numbers) and the progression family at every prime from 31
  to 59 found none.
- **What pins it.** The steps are {±1, ±11} (11² = −1 modulo 61, the four fourth roots of 1) and twice them, and the word is unchanged,
  up to a shift, when positions are multiplied by 11 or −1. Its defect number is 11, beyond the small-defect search: the advisor's
  family of sets invariant under a multiplier subgroup found it, not the brute-force order.
- **The even rule narrowed.** "The law's numbers are even" (`HARMONY-ARITH-20261112-001`, `EVEN-PERIOD-20261112-001`) holds below 30
  and at 31 and 37, not in general. Logged as a Narrowing in `docs/CORRECTIONS.md`, as frozen.

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| A flippable residue is a compatible neighbour at one place; counterexamples may be taken closed; compatibility by difference counts; one defect never fails | proved by hand (lemmas 5 to 8; 6 to 8 from the advisor model, checked here) |
| An odd not-all-equal harmony of period 61 exists, unsplit, with 12 knot kinds | proved (lemma 4 and an exact enumeration); refereed by an independent session |
| No harmony has period 31 or 37 | exact, complete search, refereed by fresh code |
| None in the targeted ranges (41, 43, 47 at small defect numbers; the progression family to 59) | exact on those ranges only |
| The least odd period | open: 33, 35, or one of 39 to 61 |

## Against the pre-registration

S1 held (none at 31 or 37). **S2 failed**: the progression family at 61 has a counterexample, and it is a harmony. The frozen
consequence followed: verified by enumerating the compatible words and checking that none differ in one place, refereed by fresh code
and by an independent session (both passed), and the Narrowing logged. All parts ran inside their caps (the longest in under half an
hour). The parity route is measured, but not yet folded in: row ODD-SEARCH-A2 is **pending**.

## Review

The fresh-code referee (`odd_referee.py`) recomputed all 422 fully blocked words and 6,000 random words without the fast identity:
passed. The independent session (`independent_referee/report.md` in the proof family) rebuilt the 12 kinds, the 122 words and their
two orbits, found the smallest distance between them to be 11, judged the window argument airtight, and found no state breaking the
61-repeat on windows of 400 and 1,000: "the claim is correct".

## What it changes

- **For the owner's harmonies.** The knot law's repeats are mostly even, and the small ones are all even, but not all: at period 61 a
  repeat of odd length is held in place by a symmetry of the arithmetic modulo 61 (the four fourth roots of 1). Whether harmonies are
  even was a question about which symmetries a period allows, not a law of the knot.
- **For the count line.** The mirror still pairs and still forbids nothing, as proved; what forbade small odd periods was the room for
  an unseen flip, and at 61 a structured base leaves none.

## Assumptions

A70 used; status unchanged.

## Corrections

One, logged in `docs/CORRECTIONS.md`: **Narrowing**, "the knot law's harmonies are not all even: one has period 61" (on
`HARMONY-ARITH-20261112-001`'s reading and `EVEN-PERIOD-20261112-001`'s long-term verdict).

## In the owner's words

The knot law's repeating patterns are not all even after all. Up to length 29, and at 31 and 37, every one is; but at 61 there is a
pattern of odd length that the law holds completely still: twelve kinds of knot, each forbidding three equal values at equal
spacing, leave room for only one pattern and its mirror. What holds it is a symmetry of counting modulo 61, the four ways to take a
fourth root of 1.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the first odd harmony, or none | **Status:** Successful | an odd harmony of period 61 found and proved; none at 31 or 37 |
| Local direction — odd harmonies | Continue | the least odd period and why 61 are open |
| Broader exploration — the count line | Known alternatives | antiperiodicity, two shifts, signed knots |
| Long-term goal — G8 From spacing to arithmetic and sets | Obstruction learned | the law's numbers are not all even; a symmetry of the period decides |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The least odd harmony, and why 61 | 2/3 — Substantial | 2/3 — Testable | search sets invariant under a multiplier subgroup at every odd period 33 to 59, then explain the period-61 base algebraically → the least odd period and a construction, or 61 | Selected · awaiting go-ahead |
| 2 | Odd harmonies at other primes | 2/3 — Substantial | 2/3 — Testable | the same family (fourth roots of 1 and their doubles, and other subgroups) at primes p ≡ 1 mod 4 up to 200 → a family of odd harmonies, or 61 alone | Alternative · deferred |
| 3 | Why unsplit harmonies are antiperiodic, where they are | 1/3 — Incremental | 1/3 — Stated | characterise the even harmonies that are antiperiodic → a lemma | Alternative · deferred |

- **#1** settles "first" and asks what the arithmetic of 61 does; the targeted family found it in seconds.
- **#2** asks whether 61 is the start of a family, which would make odd harmonies a feature of the law's arithmetic rather than a
  rarity.

**Corrections:** one, Narrowing (the knot law's harmonies are not all even). **Goals:** G8 checkpoint (obstruction learned, with G1;
no goal change; its Open line answered "no"). **Assumptions:** A70 used, unchanged. **Basket:** #1 to #3 recorded. **Advisor:**
consulted twice before the freeze; it supplied lemmas 6 to 8 and the family that found the harmony.

## Final report as sent

Sent to the owner in the project thread on 2026-11-12 at about 05:53 UTC, verbatim:

> Done: there is an odd harmony, at period 61. The rule that the knot law's harmonies are even holds below 30 and at 31 and 37, but not in general. I've logged that as a Narrowing in the corrections log. The write-up is research/ODD-SEARCH-20261112-001/odd_search.md.
>
> • **The harmony (proved, refereed twice).** Twelve knot kinds forbid three equal values at equal spacing with step 1, 2, 11 or 22 (counted mod 61). They allow exactly 122 states: one word of period 61, its shifts and its mirror. No two of those differ in one place (the nearest are 11 apart), so nothing can flip unseen, and every allowed state repeats with period 61. The base doesn't split into independent parts. A fresh session rebuilt all of this from scratch and found nothing breaking the 61-repeat on windows up to 1,000 distinctions.
> • **What pins it.** The steps are the four fourth roots of 1 mod 61 (11 × 11 = −1) and their doubles. The word is unchanged, up to a shift, when positions are multiplied by 11. It came from the advisor's suggested family of symmetric step sets. The brute-force order wouldn't have reached it soon.
> • **Nothing smaller where the search was complete.** No harmony of odd period up to 29 (proved earlier), and none at 31 or 37 (every word checked). Periods 33, 35 and 39 to 59 are still open.
> • **What still stands.** Every count, lemma and theorem from the last two epics. The mirror still forbids nothing on its own.
>
> | Scope | Verdict | Why |
> | --- | --- | --- |
> | This attempt — the first odd harmony, or none | **Status:** Successful | an odd harmony of period 61 found and proved; none at 31 or 37 |
> | Local direction — odd harmonies | Continue | the least odd period and why 61 are open |
> | Broader exploration — the count line | Known alternatives | antiperiodicity, two shifts, signed knots |
> | Long-term goal — G8 From spacing to arithmetic and sets | Obstruction learned | the law's numbers are not all even; a symmetry of the period decides |
>
> **Next step:** Research directions — selected: #1
>
> | # | Direction | Payoff | Concreteness | First step → stop when | Status |
> | --- | --- | --- | --- | --- | --- |
> | 1 | The least odd harmony, and why 61 | 2/3 — Substantial | 2/3 — Testable | symmetric step sets at every odd period 33 to 59, then explain the 61 base → the least odd period and a construction | Selected · awaiting go-ahead |
> | 2 | Odd harmonies at other primes | 2/3 — Substantial | 2/3 — Testable | the same family at primes p ≡ 1 mod 4 up to 200 → a family, or 61 alone | Alternative · deferred |
> | 3 | Why unsplit harmonies are antiperiodic, where they are | 1/3 — Incremental | 1/3 — Stated | characterise the even ones → a lemma | Alternative · deferred |
>
> **Corrections:** one, Narrowing: the knot law's harmonies are not all even, since one has period 61. **Goals:** G8 checkpoint (obstruction learned), no goal change; its open question is answered "no". **Assumptions:** A70 used, unchanged. **Basket:** #1 to #3 recorded. **Advisor:** consulted twice before freezing. It supplied three of the lemmas and the family that found the harmony. One descriptive measurement, of the advisor's parity route, is still running in the background and will be folded in.
