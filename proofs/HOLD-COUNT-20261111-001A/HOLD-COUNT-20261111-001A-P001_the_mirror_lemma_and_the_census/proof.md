# The mirror lemma, refereed, and the census of counts

Status: Proved (the mirror lemma by hand, refereed by fresh code) with an exact census. Ticket A of
`research/HOLD-COUNT-20261111-001/preregistration.md`, frozen with the code in commit `29121e4e7` before any run.
`check.py --part export|tori|steered|summary|referee` reproduces each part; `after_run.py`, `after_run_classes.py` and
`referee_controls.py` are after the run and not frozen.

## 1. The mirror lemma (by hand; refereed)

**Setting.** A knot space whose floor states are closed under flipping every point: every space here, since each line is not-all-equal
on signed literals (theorem D of `IN-OUT-20261110-001`). The world holds n points; a reading is total when every held pattern occurs
among the floor states, an output point is decided when it has one value in every floor state with the same pattern, and decided points
hold the count mod m when their value is e(Σℓ_i mod m) for literals ℓ_i = x_i ⊕ ε_i and a map e that separates residues.

**Lemma.** Let n ≥ m − 1. A total reading of decided points that is a function e of the count mod m exists only if m is even and n is
odd, and then e sends the residues of c and n − c to complementary values. So no reading holds the count of three held points mod 3,
and the readings that hold it mod 4 are exactly the full adders: a point reading their parity and a point reading a majority of their
literals, each up to negation.

**Proof.** Theorem D gives F(¬p) = ¬F(p) for a decided total reading F. Flipping every held point sends the literal count c to n − c,
so e((n − c) mod m) = ¬e(c mod m) for c = 0..n. For odd m, c* = n · 2⁻¹ mod m is fixed by c ↦ n − c and is the count of some pattern
(n ≥ m − 1), so e(c*) = ¬e(c*); for even m and n, c = n/2 gives the same contradiction. For n = 3, m = 4, a bit b with b(3 − c) = ¬b(c)
is fixed by b(0), b(1): majority, parity, or a negation of either, and four residues need one of each. ∎

**Referee (`hold_referee.py`, fresh code, passed).** R1: the lemma's combinatorial core holds in all 90 cases n = 1..8, m = 2..6,
one to three output points (existence of a complementary code exactly when m is even and n odd; an injective one exactly when also
2^k ≥ m). R2: on all 32,424 classes of the 1,128 census spaces, the states satisfying every line, recomputed from the lines alone, are
closed under flipping every point, the lemma's only hypothesis. R3: the five least instances the census reports are confirmed from the
lines alone. **Controls (after the run, `referee_controls.py`):** a space with one point pinned is flagged by R2, and two corrupted
instances are rejected by R3, so the referee can fail. It is independent code by the same author, not an independent reviewer.

**Provenance.** The case m = 2 was in the program (backlog B149); the substance is classical (Post's self-dual functions; spin systems
without fields read only up to a global flip, so ground-state spin logic uses local fields: Whitfield, Faccin and Biamonte 2012).

## 2. The census (exact, frozen)

1,128 spaces read (all 281 lattice tori up to 20 points; 847 steered random spaces of 8 to 14 points and genus 1 to 3, 353 never reaching
their genus and skipped, as in `PARITY-NEEDS-20261111-001`), 32,424 classes, every triple of held points with and without each reference
point. Parts took 30 and 70 seconds; nothing was dropped.

| Reading of three held points | Triples (with references) | Spaces | Least space |
| --- | --- | --- | --- |
| parity, no reference | 804 | 20 | 8 points: torus (2, 0, 4) and four others |
| majority, no reference | 44,769 | 757 | 8 points |
| **full adder, no reference (P1)** | 200 | 13 | **8 points: the same five spaces as parity** |
| count mod 3, no reference (P0) | 0 | 0 | none |
| count mod 4, no reference | 200 (exactly the full adders, C2) | 13 | 8 points |
| parity, one reference | 216 | 3 | 18 points: tori (3, 0, 6), (6, 0, 3), (6, 3, 3) |
| **count mod 3, one reference (P2)** | 0 | 0 | **none** |
| count mod 4, one reference | 0 | 0 | none |

- **P0 holds** on every class, as the lemma requires.
- **P1: yes, at the smallest size.** The 8-point torus (2, 0, 4) in its class with 8 floor states, holding points 0, 1 and 4: point 5 is
  their parity and point 6 the negation of their majority, the two binary digits of their count; points 2, 3 and 7 read majorities of
  other literals. Every parity triple in a space of 8 or 12 points is a full adder; the 16- and 18-point tori count parity without one.
- **P2: no.** No space holds the count mod 3 with one reference point, nor mod 4; holding a fourth point at 0 makes readings rarer
  (parity with a reference only on three 18-point tori).
- **P3 and the measure criterion** cannot be evaluated: there is no instance of P2.
- **Controls.** C1: every space's numbers of total parity and total majority interfaces equal `PARITY-NEEDS-20261111-001`'s (no
  mismatch; the summary lists the 3-point torus (3, 1, 1) as read by one epic only because `PARITY-NEEDS` stored its empty tally as
  nothing; both count zero). C2: the mod-4 triples are exactly the full adders on every space.

## 3. Why a reference buys nothing here (computed after the run, exact on the census range)

A reading with a reference is a reading of four held points restricted to the reference's value. Over all 4,634,517 free four-point sets
(all 16 patterns occur), decided outputs depend on one held point (427,466, copies), three (15,593) or all four (6,857), never two (no
self-dual map has exactly two essential inputs). Those depending on all four fall into two classes under permuting and negating inputs
and output: the weighted majority [2a + b + c + d ≥ 3] (6,783) and maj(a, b, a ⊕ c ⊕ d) (74). A count mod 3 needs, at the reference's
value, a bit that is a function of the literal count equal at counts 0 and 3: exactly one, exactly two, or not-all-equal of the three
literals, all non-unate. A threshold function stays a threshold function, hence unate, when an input is fixed; and an exhaustive check
finds no restriction of either class, at any choice of reference, that is such a bit. So to count mod 3 a point would have to read
whether three held points are not all equal, the knot's own relation, and no space in the range reads it. (A first guess after the run,
that counting needs the held points to fix every point, was wrong: only 48 of the 804 parity triples do.)

## What this establishes

- Proved and refereed: a knot space with the not-all-equal law holds a count of n held points mod m only for even m and odd n.
- Exact, in the range: such a space writes the count of three held points in binary at 8 points, the least size at which it counts at
  all; one reference point does not let any space up to 20 points (or random spaces of 8 to 14 points, genus 1 to 3) count mod 3.
- Nothing here bears on P versus NP.
