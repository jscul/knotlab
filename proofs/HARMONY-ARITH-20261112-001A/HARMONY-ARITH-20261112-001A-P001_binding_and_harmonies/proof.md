# Stitching harmonies, and the harmonies the law makes

Status: Proved (lemma S and proposition M by hand) with an exact census, refereed by fresh code. Ticket A of
`research/HARMONY-ARITH-20261112-001/preregistration.md`, frozen with the code in commit `c423659f4` before any run. `check.py --part
harmonies|stitches|summary|referee` reproduces each part; `referee_controls.py` is after the run.

Words, as in the pre-registration and the guide's glossary: a **harmony** (the owner's word, read as A70) is a periodic base along one
shift all of whose allowed states repeat, the literature's finite subshift; the **period** of a state is the least shift returning it
to itself; an **orbit** (the literature's word) is a repeating state with all its shifts; a **stitch** is a knot of one fixed kind at
every shift holding distinctions of two harmonies; two harmonies **overlap** at s when a_i and b_{i+s} are one shared distinction;
the **offset** of two orbits of periods p and q is the shift between their states modulo gcd(p, q) (literature: relative phase); a
state is **antiperiodic** when flipping every value equals shifting by half its period. The bases have one distinction per shift and
knots of one to three kinds (0, a, b), span W = the largest b.

## 1. Settled by definition, for any law

**Lemma S.** For harmonies A and B stitched with stitches of one kind or overlapping, under any law: (a) every allowed state restricts
to states of A and B; (b) so it repeats, with period the least common multiple of theirs; (c) with no stitch, the pairs drawn from
orbits of periods p and q form gcd(p, q) orbits, one per offset, each of period lcm(p, q); (d) stitches and overlaps keep or remove
each offset whole; (e) so no state of the stitched base drawn from orbits of periods p and q has period |p − q| or p mod q. The proof
is in the pre-registration (immediate, and the Chinese remainder theorem for (c)).

**Proposition M.** Under not-all-equal, for antiperiodic orbits of periods p and q, flipping every value acts on offsets by adding
(q − p)/2 modulo gcd(p, q): the identity when p and q carry the same power of 2, and otherwise a pairing, so that the number of offsets
a stitch or overlap keeps is even. The proof is in the pre-registration.

## 2. The harmonies the law makes (exact; H1 to H3)

Every pattern of one to three knot kinds with span 2 to 10 (15,225 per law), under four laws:

| Law | Harmonies | Periods found | Antiperiodic states |
| --- | --- | --- | --- |
| not-all-equal | 5,539 | 2, 4, 6, …, 20, 24 and 80: only even | 10,374 of 10,424; every state of every harmony whose offsets have gcd 1 |
| odd parity (control) | 15,225 (every pattern) | 1, 3, 6, 7, 9, 12, 14, 15, 21, 30, 31, 42, 62, 63, 73, 93, 127, 217, 465, 511, 889, 1023 | none |
| exactly one (control) | 299 | 3, 6, 9, 12, 15: only multiples of 3 | none |
| clause (control) | 0 | — | — |

- **H1 holds:** no not-all-equal harmony state has an odd period at spans 7 to 10 (nor at 2 to 6, scoped).
- **H2 holds:** in every not-all-equal harmony whose knot offsets have gcd 1, every state is antiperiodic. The 50 states that are not
  lie in 16 harmonies whose offsets share a factor (2 in 15, 3 in 1), which split into independent parts.
- **H3 holds:** odd parity has odd periods at every span (its periods are those of linear recurrences over two values, many of the
  form 2^k − 1); exactly one has only multiples of 3; the clause law, which always allows all ones and more, has no harmony.
- **Typical, not supplied.** About a third of the not-all-equal patterns are harmonies at every span from 5 on (2,605 of 7,419 at span
  10); the commonest periods are 2 and 4, and long ones are rare. Period 80 occurs in two patterns, both with all offsets even: each splits
  into two independent halves whose states have periods 16 and 20 in full positions, and 80 = lcm(16, 20), lemma S inside one base.

- **Stress test one size past (after the run, `stress_test.py`).** Spans 11 and 12 under not-all-equal: 32,746 more patterns,
  9,120 harmonies and 22,510 states; no odd period (periods 2 to 24, 40 and 48), and no connected harmony with a state that is not
  antiperiodic (the 156 at span 12 lie in split patterns).

No proof of H1 or H2 was found: the even-period rule is exact on every pattern to span 12, not a theorem at every span.

## 3. What stitches read (exact; M, R1, R2, the control)

The 11 not-all-equal orbits found at spans 2 to 6 (periods 2 to 12) and the 29 odd parity orbits, every ordered pair, with 48 stitch
kinds and 4 overlaps of offsets 0 to 3: 6,292 not-all-equal cases and 43,732 odd parity ones.

- **M holds** in all 2,496 cases it covers: the kept offsets come in mirror pairs whenever the two periods carry different powers of 2.
- **Control law:** 16 odd parity cases with periods of different powers of 2 keep an odd number of offsets, so the pairing belongs to
  the mirror, not to the counting.
- **R1 holds:** in 616 cells (one stitch kind, one pair of periods) different orbits of the same periods keep different numbers of
  offsets: the stitches read the orbits' words, not only their periods.
- **R2 holds:** no stitch kind or overlap allows a stitched state exactly when one period divides the other.
- **Seen after the run.** Not-all-equal stitches keep 15 to 39% of offsets on average, overlaps 1 to 8%; 4,432 of the 6,292 cases keep
  none and 616 keep all.

## 4. The referee: passed

R1 recomputed all 11,046 patterns at spans 2 to 8 under not-all-equal, odd parity and exactly one from the window graph as a 0/1
matrix (a harmony when its core is a permutation matrix), with the same verdicts and periods. R2 recomputed all 50,024 stitches and
overlaps over every shift, not only offsets: the surviving shifts form whole offsets (lemma S (d)) and equal the census's. R3: every
surviving stitched state has period lcm(p, q). Controls after the run (`referee_controls.py`): an altered census period and a removed
offset are each caught. It is independent code by the same author, not an independent reviewer.

## Scope and limits

- The law is the plain not-all-equal law, with no negated literals. With signed knots the mirror and M stand, but the even-period rule
  need not: a gauge that flips every other distinction turns the period-2 state into a constant one.
- Bases with one distinction per shift and up to three knot kinds of span at most 10; stitches of one kind, offsets 0 to 3, between
  orbits found at spans up to 6. Nothing here bears on P versus NP.
