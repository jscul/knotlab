# Arithmetic of harmonies without a zero

Epic `HARMONY-ARITH-20261112-001` (backlog B163, G8 with G1; program mathematics, group arithmetic), 2026-11-12, at the owner's word.
Pre-registered in [preregistration.md](preregistration.md), frozen in commit `c423659f4` before the census ran. Proof family:
`proofs/HARMONY-ARITH-20261112-001A/`.

## Words

As in the guide's glossary and the pre-registration: harmony (the owner's word, read as A70: a periodic base along one shift all of
whose allowed states repeat, the literature's finite subshift), the period of a state, orbit, antiperiodic, stitch, overlap and offset.
"Stitch" and "offset" are new, chosen with the advisor model (Fable 5.2) and added to the glossary with this epic.

## The question

The owner asked what subtraction and division of logical harmonies are. A running total needs a zero the not-all-equal law cannot
make; this route never asks for one. Stitch a harmony of period p to one of period q: which periods do the stitched states have, does
the law read divisibility, is there a native difference (a beat), and what is forced by the law rather than by definition?

## The answer

**Stitching multiplies and the shared divisor counts; nothing subtracts; and the knot law's own harmonies are even.**

- **By definition, for any law (proved).** Every stitched state pairs a state of each harmony, so it repeats with the least common
  multiple of their periods. The pairs from two orbits fall into gcd(p, q) offsets, and a stitch keeps or removes each offset whole.
  No stitched state has period |p − q| or p mod q: there is no native beat, only readings made from a stitched state, which are
  classifiers of values.
- **The law makes only even periods (exact, to span 12).** Every not-all-equal harmony among 47,971 patterns of one to three knot
  kinds and span 2 to 12 has states of even period only: 2, 4, …, 24, with 40, 48 and 80 among the rare long ones. In every one whose
  knot offsets have greatest common divisor 1, every state flips under half its period. The control laws make other numbers: odd
  parity periods of linear recurrences (1, 3, 7, 15, 31, …), the exactly-one law only multiples of 3, the clause law no harmony.
- **The mirror reads a power of 2 (proved; 2,496 cases).** Under not-all-equal, flipping every value pairs the offsets of two
  antiperiodic harmonies exactly when their periods carry different powers of 2, so the kept offsets then come in pairs. That is a
  yes-or-no fact about p and q the law reads by itself. Odd parity, with no mirror, keeps odd numbers of offsets in 16 such cases.
- **Divisibility is not read (exact).** No stitch kind or overlap allows a stitched state exactly when one period divides the other,
  and in 616 cells two orbits with the same periods keep different numbers of offsets: what a stitch reads is the orbits' words.

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| Stitched states repeat with period lcm(p, q); gcd(p, q) offsets, each kept or removed whole; no beat | proved by hand (lemma S) |
| Under not-all-equal the mirror pairs the offsets of antiperiodic harmonies iff p and q carry different powers of 2 | proved by hand (proposition M); 2,496 cases, no exception |
| Not-all-equal harmonies have only even periods | exact on every pattern to span 10 (frozen), and to span 12 (stress test); not proved |
| Connected not-all-equal harmonies are antiperiodic in every state | exact on the same range; not proved |
| Odd parity has odd periods; exactly one has multiples of 3; the clause law no harmony | exact on the same range to span 10 |
| No stitch kind reads divisibility; stitches read words, not only periods | exact on 6,292 not-all-equal cases |

## Against the pre-registration

Every frozen prediction held: H1, H2, H3a, H3b, M, R1, R2 and the control. Both census parts finished in under a minute, far inside
their caps. The referee (fresh code) agreed on all 11,046 patterns it recomputed and all 50,024 stitches and overlaps, and every
surviving stitched state had period lcm(p, q); its negative controls caught an altered period and a removed offset. The scoping run at
spans 2 to 6 is disclosed in the pre-registration. After the run: a stress test one size past, spans 11 and 12 (32,746 more
patterns, 9,120 harmonies), found no odd period and no connected harmony with a state that is not antiperiodic; and the offsets a
not-all-equal stitch keeps form a single coset of a subgroup in only 412 of 1,244 proper cases.

## What it changes

- **For the owner's question.** Without a zero there is still arithmetic between harmonies: putting two together multiplies their
  periods into the least common multiple, and their common divisor is the number of ways they can be offset, each offset kept or
  removed whole. That is division read as "how many ways one fits against the other". Subtraction does not appear: no beat is ever a
  harmony of the stitched base.
- **For the count line.** The mirror that limited counting to even moduli (`HOLD-COUNT-20261111-001`) reappears: the knot law's own
  harmonies come only in even periods, each flipping under half its period, and the law reads whether two periods carry the same power
  of 2. The knot's arithmetic is two-sided from the start.
- **Typical, not supplied.** About a third of the patterns at each span are harmonies; most have period 2 or 4.

## Assumptions

A70 (a harmony is a periodic base whose allowed states all repeat) added and used; status unchanged. Relied on: none other.

## Corrections

None.

## In the owner's words

Two harmonies put together repeat at their least common multiple, and the number of ways they can sit against each other is their
common divisor. There is no difference between them that comes out as a new harmony. The knot law's own harmonies all come in even
periods, each one flipping into its mirror image half a period on, and the mirror tells two harmonies apart by their powers of 2. The
knot's numbers are even from the start.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — arithmetic of harmonies without a zero (B163) | **Status:** Successful | lcm, offsets, no beat proved; even periods exact to span 12; the mirror reads powers of 2 |
| Local direction — harmonies along one shift | Continue | the even-period rule is exact but unproved |
| Broader exploration — the count line and periodic bases | Known alternatives | two shifts, signed knots, a harmony read as a finite repeat |
| Long-term goal — G8 From spacing to arithmetic and sets | Capability gained | least common multiple and offsets native; the law's numbers even |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Prove the even-period rule | 2/3 — Substantial | 2/3 — Testable | from the transfer graph and the mirror, show every connected harmony state flips under half its period → a theorem, or a harmony past span 12 with an odd period | Selected · awaiting go-ahead |
| 2 | Harmonies along two shifts | 2/3 — Substantial | 2/3 — Testable | harmonies of two-shift patterns, their period lattices, and stitching as lattice intersection → the two-shift arithmetic, or none | Alternative · deferred |
| 3 | Signed knots and the twist | 1/3 — Incremental | 3/3 — Ready | the census with negated literals → an even rule up to a gauge, or odd periods | Alternative · deferred |
| 4 | A harmony read as a finite repeat (challenge A70) | 1/3 — Incremental | 3/3 — Ready | rerun the stitching questions on finite repeats of period p → the same arithmetic, or A70 carries the result | Alternative · deferred |

- **#1** would turn "the knot law's numbers are even" into a theorem; the data is exact to span 12 and the exceptions in split
  patterns are explained, but no route through the transfer graph's core is in hand.
- **#2** is where division of lattices would appear; the two-shift census tools exist (`PERIODIC-READ-20261111-001`).
- **#3** and **#4** are cheap checks of the result's reach.

**Corrections:** none. **Goals:** G8 checkpoint (capability gained, with G1; no goal change). **Assumptions:** A70 added (Assumed),
used here. **Basket:** #1 to #4 recorded; B163 taken.
