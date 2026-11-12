# Which odd periods the knot law makes, and why 61

Epic `ODD-FAMILY-20261112-001` (`ODD-SEARCH-20261112-001` directions 1 and 2 taken together, G8 with G1; program mathematics, group
arithmetic), 2026-11-12, at the coordinator's go-ahead. Pre-registered in [preregistration.md](preregistration.md), frozen in commit
`3cec8a886` before the scan ran. Proof family: `proofs/ODD-FAMILY-20261112-001A/`.

## Words

As in the guide's glossary and the pre-registration: harmony (A70), word, compatible, flippable, steps, makes a harmony, class (a
word's rotations and their flips), multiplier, stabiliser.

## The question

`ODD-SEARCH-20261112-001` found the first known odd harmony, at period 61, from steps closed under multiplying by a fourth root of 1.
Which numbers does the knot law make as periods of harmonies, and what decides it? Bounded by the coordinator: symmetric step sets at
every odd period from 33 to 59 and the same family at every prime up to 200, then one attempt to explain why 61 works; no full
classification.

## The answer

**Three odd periods in range, 61, 73 and 193; none below 61 in these families; what decides it is not known.**

- **Two new odd harmonies (proved, refereed twice).** At 73 the steps 1, 2, 27 and 54 (with their negatives; 27² ≡ −1) make a harmony
  of 12 knot kinds whose 730 states fall into five classes. At 193 the steps 1, 2, 31, 54, 65 and 81 (in Gaussian notation
  {1, 2, 4 + 3i} times the fourth roots of 1, i = 81) make one of 18 kinds with 386 states in one class. In both, no two states differ
  in one place, so every state repeats (lemma 4 of `EVEN-PERIOD-20261112-001`, which needs only that the period is odd); neither
  splits.
- **Nothing else in range (exact, in the two frozen families).** 88,336 step sets at 43 values of n: unions of one to three cosets
  of every multiplier group containing −1, and the steps {±1, ±2, ±t} and {±1, ±2, ±t, ±2t}. Up to a multiplier exactly one set
  makes a harmony at each of 61, 73 and 193, and none does at any odd n from 33 to 59 (composite or prime), at any prime ≡ 3 mod 4,
  or at any other prime to 199.
- **What they share.** Every set found has stabiliser exactly the fourth roots of 1, so every period found is a prime ≡ 1 mod 4.
  None was found with stabiliser {±1} or with a larger stabiliser.
- **What that does not explain.** The same steps H ∪ 2H fail at 14 of the 16 primes ≡ 1 mod 4 from 41 to 197. At 73 four of the
  five classes are moved by the multiplier, so the states need not be symmetric. Neither frozen explanation passed its test (below).

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| Lemma 4 of `EVEN-PERIOD-20261112-001` holds at every odd n, prime or not | proved by hand (rechecked by the independent session) |
| Odd harmonies of periods 73 and 193 exist, unsplit | proved (lemma 4 and an exact enumeration); refereed by fresh code and an independent session |
| In the two families, harmonies only at 61, 73 and 193 (odd n 33 to 59, primes 61 to 199), each with stabiliser the fourth roots of 1 | exact on those families and ranges; the fresh-code referee recomputed all 31,104 sets up to a multiplier |
| The least odd period of a harmony | open: 61, or one of 33, 35, 39 to 59 outside these families |
| Why the fourth roots of 1, and which primes | not known; the advisor's rule (exactly two symmetric words) fits all 16 primes counted, after the fact |

## Against the pre-registration

| Item | Outcome |
| --- | --- |
| F1 none with at most two steps up to sign (the advisor's) | held |
| F2 every set {±s, ±2s, ±t(, ±2t)} (the advisor's) | **failed** at 193 |
| F3 no stabiliser of order 6 or more (the advisor's) | held |
| F4 stabiliser of order 4: only H ∪ 2H or H ∪ 2⁻¹H (the advisor's) | **failed** at 193 (three cosets) |
| F5 H ∪ 2H counts (the advisor's) | held beyond the pre-freeze 41 and 53: one further harmony prime, 73; from 89 on, over 200,000 words and no harmony; the rate 1.074^p is far off |
| F6 none at odd n 33 to 59 (this epic's) | held |
| F7 another prime, among doubled steps with t² ≠ −1 (the advisor's) | **failed in part**: two other primes, but none with stabiliser {±1} |
| Verdict rule for the explanation | **neither reading**: R2 needed a set with stabiliser {±1} (none), R1 a difference set (not one) and at most one class at large primes (over 200,000 words) |

The counts at 41, 53 and 61 were seen before the freeze while testing the code, and were disclosed then. All parts ran inside their
caps (the scan in under four minutes of processor time). No frozen prediction was changed.

## Review

The fresh-code referee (`fam_referee.py`: its own family generation up to a multiplier, its own clauses, Glucose 4) recomputed all
31,104 sets and found the same harmonies; it enumerated every compatible word of each, found none one place apart and no state
breaking the repeat on windows of 4n, checked 30 flippable pairs per n in plain Python, and recounted H ∪ 2H to 73: passed. The
independent session (`independent_referee/report.md` in the proof family) rebuilt the kinds (12 and 18), the counts and classes (730
in five; 386 in one), the least distances (8 and 19), judged the window lemma sound, found no state breaking the repeat on windows of
4n and of n + 1, and confirmed that H ∪ 2H makes no harmony at 89 or 97. Its one remark: at 67 and 71 the steps {±1, ±2, ±3} allow no
state at all, a vacuous harmony under the bare definition, which this record's definition (a compatible word must exist) excludes.

## The explanation attempt

- **Read along two shifts (exact).** Since 11² ≡ −1 and 6 + 5·11 = 61, the residues mod 61 are pairs of integers (a, b) ↦ a + 11b, and
  H ∪ 2H is the progression law with steps 1 and 2 along each of two shifts: along each, a compatible word has no 000, 111, 01010 or
  10101 (in the literature, a two-dimensional shift of finite type with periods the ideal (6 + 5i) of the Gaussian integers).
- **The multiplier reading (R1) failed its test.** The 61 word's cosets are not a difference set, and H ∪ 2H has many classes at the
  large primes.
- **The advisor's near-threshold reading (R2) failed its test.** No set with stabiliser {±1} makes a harmony in range, and the counts
  are irregular: none at 53, one class at 61, five at 73, over 200,000 words at 89.
- **After the run (descriptive, from the advisor, checked here).** Along one shift alone a word of odd length always has a free place
  (checked to 23), so the other steps must pin those places. The symmetric 61 word is forced by hand and pinned because the places free
  along one shift and their multiples by 11 are disjoint; a proof without enumeration would also need every state to be symmetric,
  which fails at 73. A rule fitted after the fact: H ∪ 2H makes a harmony exactly when exactly two words are fixed by every fourth root
  of 1 (true on all 16 primes counted). The nearest named property is that of locked constraint satisfaction problems (Zdeborová and
  Mézard, 2008), whose solutions are never one place apart; there it holds by construction, here it comes from the steps' arithmetic.

## What it changes

- **For the owner's harmonies.** The knot law's odd repeats are not one accident: in range they come at 61, 73 and 193, each from
  steps closed under multiplying by a fourth root of 1. Their symmetry is shared but is not shown to be the cause, so the earlier
  reading that the symmetry holds them in place is narrowed (below).
- **For the count line.** The three are, read along two shifts, harmonies of a two-shift law with steps 1 and 2, which joins this line
  to `HARMONY-ARITH-20261112-001`'s direction on harmonies along two shifts.

## Assumptions

A70 used; status unchanged.

## Corrections

One, logged in `docs/CORRECTIONS.md`: **Not a block**, "the fourth roots of 1 are not shown to hold the odd harmony in place"
(`ODD-SEARCH-20261112-001`'s reading of its period-61 harmony; Overreading). Its decision note, the notebook and the goals document
carry the narrowed reading.

## In the owner's words

The knot law makes repeating patterns of odd length at 61, 73 and 193, and at no other odd length up to 199 in the families searched,
none below 61. All three come from steps that stay the same when every position is multiplied by a fourth root of 1. But the same kind
of steps fails at most other primes, and at 73 most of the patterns are not symmetric themselves, so the symmetry is something they
share, not yet the reason they hold still.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — which odd periods the knot law makes, and why 61 | **Status:** Partially successful | two new odd harmonies (73, 193) proved and the families searched to 199; the explanation failed both frozen tests |
| Local direction — odd harmonies | Continue | whether the fourth roots are necessary is one cheap search away |
| Broader exploration — the count line | Known alternatives | harmonies along two shifts (joined), antiperiodicity |
| Long-term goal — G8 From spacing to arithmetic and sets | Capability gained | the law's odd periods found so far are primes 1 mod 4 carrying a fourth root of 1 |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A harmony without the fourth roots | 2/3 — Substantial | 3/3 — Ready | every step set with trivial stabiliser of five steps up to sign at the primes 61 to 89, and a sample of six → one, or the symmetry is necessary in range | Selected · awaiting go-ahead |
| 2 | Which primes, for H ∪ 2H | 2/3 — Substantial | 3/3 — Ready | the advisor's rule (exactly two symmetric words) and "none from 89 on" at every prime 1 mod 4 to 1000, one SAT query each → a rule, or its first failure | Alternative · deferred |
| 3 | The least odd period | 2/3 — Substantial | 2/3 — Testable | a complete word search at 33, 35 and 39 (composite periods need a new normalisation) → a smaller odd harmony, or 61 stands lower down | Alternative · deferred |
| 4 | A proof for 61 without enumeration | 1/3 — Incremental | 2/3 — Testable | the advisor's forcing from a free place 0 along both shifts, case by case → a hand-checkable proof | Alternative · deferred |

- **#1** decides whether "every odd harmony carries a fourth root of 1" is the law's or the families': the advisor bets on a sampling
  artefact, the data so far say necessary.
- **#2** would say exactly which primes the main family makes, the closest thing to "what decides it" for one family.
- **#3** settles "first"; the families found nothing below 61, but they are not complete.

**Corrections:** one, Not a block (the fourth roots of 1 are not shown to hold the odd harmony in place). **Goals:** G8 checkpoint
(capability gained, with G1; no goal change). **Assumptions:** A70 used, unchanged. **Basket:** #1 to #4 recorded; the arithmetic
line's basket held six untaken rows at payoff 2 (OWN-RELATION #1, HARMONY-ARITH #2, HOLD-COUNT #4, OWN-RELATION #2 and #4,
EVEN-PERIOD #2), none ahead of #1; HARMONY-ARITH #2 (harmonies along two shifts) now has this epic's three examples. **Advisor:**
consulted before the freeze (predictions F1 to F5 and F7, the doubled-step family and the reading along two shifts) and once after
the run (the lemma along one shift, the hand forcing at 61, the fitted rule, the pointer to locked problems), each checked here.

## Final report as sent

Sent to the owner in the project thread on 2026-11-12 at about 06:27 UTC, verbatim:

> Done. In the families I searched, the knot law's odd harmony periods up to 199 are 61, 73 and 193. None of them is below 61. What decides which primes is still open. The write-up is research/ODD-FAMILY-20261112-001/odd_family.md.
>
> • **Two new odd harmonies (proved, refereed twice).** At 73, the steps 1, 2, 27 and 54 allow 730 states (five repeating words, with their shifts and mirrors). At 193, six steps allow 386 states (one word). In both, no two states differ in one place, so every state repeats. Neither splits.
> • **Nothing else in range (exact).** I tested 88,336 step sets at every odd period from 33 to 59 and every prime up to 199. The fresh-code referee recomputed all of them independently and got the same answer.
> • **What they share.** In all three, the steps are unchanged when every position is multiplied by a fourth root of 1. So each period is a prime that is 1 more than a multiple of 4.
> • **That doesn't explain it.** The same steps fail at 14 of the 16 such primes from 41 to 197. At 73, four of the five words aren't symmetric themselves. Both explanations I froze before the run failed their tests. That includes the advisor's near-threshold count, which was far off: 0 states at 53, but over 200,000 at 89.
>
> | Scope | Verdict | Why |
> | --- | --- | --- |
> | This attempt — which odd periods the knot law makes, and why 61 | **Status:** Partially successful | 73 and 193 found and proved, families searched to 199; the explanation failed both frozen tests |
> | Local direction — odd harmonies | Continue | one cheap search decides whether the fourth roots are necessary |
> | Broader exploration — the count line | Known alternatives | harmonies along two shifts (now with three examples), antiperiodicity |
> | Long-term goal — G8 From spacing to arithmetic and sets | Capability gained | the law's odd periods found so far are primes 1 mod 4 carrying a fourth root of 1 |
>
> **Next step:** Research directions — selected: #1
>
> | # | Direction | Payoff | Concreteness | First step → stop when | Status |
> | --- | --- | --- | --- | --- | --- |
> | 1 | A harmony without the fourth roots | 2/3 — Substantial | 3/3 — Ready | every five-step set with no symmetry beyond ±1 at the primes 61 to 89, plus a sample of six-step sets → one, or the symmetry is necessary in range | Selected · awaiting go-ahead |
> | 2 | Which primes, for H ∪ 2H | 2/3 — Substantial | 3/3 — Ready | test the advisor's rule (exactly two symmetric words) at every prime 1 mod 4 up to 1000 → a rule, or its first failure | Alternative · deferred |
> | 3 | The least odd period | 2/3 — Substantial | 2/3 — Testable | complete word search at 33, 35 and 39 → a smaller odd harmony, or 61 stands | Alternative · deferred |
> | 4 | A proof for 61 without enumeration | 1/3 — Incremental | 2/3 — Testable | the advisor's hand forcing, case by case → a checkable proof | Alternative · deferred |
>
> **Corrections:** one, Not a block. The last epic said the fourth-root symmetry "holds" the 61 harmony in place, which is more than the evidence shows. It's narrowed and logged in docs/CORRECTIONS.md. **Goals:** G8 checkpoint (capability gained), no goal change. **Assumptions:** A70 used, unchanged. **Basket:** #1 to #4 recorded; nothing in the line's basket ranks above #1. **Advisor:** consulted before the freeze (most of the predictions) and after the run, where it hand-derived the 61 word and fitted the rule in #2. I checked both. The route measurement from the last epic is still running, and I'll fold it in when it lands.
