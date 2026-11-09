# Full reach on honeycomb tori

Epic `HONEY-REACH-20261109-001` (program foundations), 2026-11-09.

## The question

- **Where it comes from.** `DISTANCE-20261108-001` computed that on honeycomb tori of side 3 to 13 every ring needs every ring exactly
  on sides 3, 6, 9 and 12, unlike the square torus, where the side's parity decides (`LATTICE-NET-20261108-001A`). Its direction 2 was
  parked as backlog B18 (Payoff 2/3, Concreteness 3/3); the coordinator relayed it on 2026-11-09.
- **The question.** Does a honeycomb torus of rule-60 rings with equally spaced contacts have full reach exactly when 3 divides its
  side, and why? Stop at a theorem, or at the first side that breaks the pattern.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Composition is the six-neighbour sum.** Three steps between contacts of one kind multiply by M = (1 + x)(1 + y/x)(1 + 1/y), the sum of the six neighbours on the triangular lattice of rings of one kind, over GF(2). A ring never needs another exactly when every power of M vanishes on a window of seven points (a ring of the same kind) or six (the other kind). | proved | A |
| 2 | **Powers vanish on the mirrors.** Every power of M vanishes on the three mirror lines through a ring, because the reflections pair up the walks. | proved | A |
| 3 | **When 3 does not divide the side, full reach fails.** The turn of 120° about a ring fixes exactly one ring of the other kind, and that ring's whole window lies on the mirrors: it never needs the first ring, nor the first ring it. | proved | A |
| 4 | **The mirrors pin nothing else.** From side 7 on, the mirror lines contain no window of a ring of the same kind, and contain one of the other kind only when 3 does not divide the side, and only the turn-fixed ring's. | proved | A |
| 5 | **When 3 divides the side, full reach holds.** Every ring needs every ring on every side from 3 to 300 divisible by 3. | computed | A, stress test |
| 6 | **How many rings miss a ring.** When 3 does not divide n, each ring is never needed by exactly 2(N − 1)(N − 2) + 1 rings, with N = 2^(v + 1) and v the power of 2 in n (N = 2^(v − 1) when n is a power of two): one on odd sides, 13 at side 8 and twice an odd side, 85, 421, 1,861, 7,813 as v grows. | computed, sides 3 to 300 | A, stress test |

## Answer

Half by proof, half by computation. When 3 does not divide the side, composition never reaches every ring, by proof, for every side:
the ring of the other kind that the turn of order 3 fixes is reached by walks that cancel in pairs across the three mirrors. When 3
divides the side the turn fixes no ring of the other kind, the mirrors pin nothing (proved from side 7), and every ring needs every ring
on every side checked, to 300. The pattern computed on sides 3 to 13 holds to side 300, with an exact count of the rings missed.

## Reading

**Interpretation, not a theorem.**
- **What blocks reach is a symmetry of the source.** On the square torus the ring never reached is the antipode, which the half-turn
  about the source fixes, and it exists when the side is even. On the honeycomb torus it is the ring the turn of order 3 fixes, and it
  exists when 3 does not divide the side. In both, a ring pinned by a rotation about the source lies on its mirrors, and the routes into
  it cancel. The lattice's rotation order sets which sides fail.
- **Powers of two deepen the gap.** Even sides lose more rings, and the loss grows with the power of 2 in the side but not with its odd
  part, as on the square torus. The parity of the walk counts carries the 2-adic structure.
- **Given, not grown.** The lattice is given, not grown from a law.

## Lag cutoffs and census-only claims

- **No lag cutoff.** Every reading follows powers of M, walk counts or rows of M^T until the next lies in the span of the earlier ones.
- **Census-only.** Full reach when 3 divides the side (sides to 300); the count of rings missed (sides to 300); that the points no power
  reaches are exactly the mirror lines on odd sides (to 299). The last fails on some even sides, divisible by 3 or not (66 is the first
  divisible by 3); full reach holds there all the same, so the even sides keep full reach for a reason not found here.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| Mirror lines (2), turn-fixed ring (3) | sides 201 to 300 (checked to 200) | pass |
| Full reach when 3 divides n (5) | sides 201 to 300 (checked to 200) | pass |
| The count formula (6) | sides 201 to 300 (checked to 200), including 224 (7,813) and 256 (32,005) | pass |
| Contact level, every pair of rings | sides 17 to 20 (checked to 16) | pass |
| Cell level | sides 8 and 9 (checked to 7) | pass |

The script is `stress_test.py` beside this note, its output `stress_test.json`; it ran in 162 seconds.

## Literature and provenance

- **Sources.** Additive cellular automata read through polynomials over GF(2) (Martin, Odlyzko and Wolfram 1984); parity of lattice
  walks and the pairing of walks by an involution without fixed points; the honeycomb's medial graph, the kagome lattice; the rotation
  centres of the honeycomb.
- **Classification.** Known-with-delta. The pairing argument is classical. The delta is composition across time on the honeycomb torus of
  rings, with the obstruction located at the ring the turn of order 3 pins, matching the square torus's antipode.

## Workspace assumptions

- **Relied on.** A30 (two-time knots), A32 (binding), A37 (composition at recurring lags).
- **Added.** None. The definition of a ring needing a ring (one of its contacts needs it) is `DISTANCE-20261108-001B`'s.
- **Scope.** Honeycomb tori of rule-60 rings with equally spaced law-(12, 12) contacts.

## Ratio

Since the epic opened:
- **Substantive.** One proof (A) with ten checks, one stress test.
- **Administrative.** This note and the closure.

## Pending the owner

- None new.
- Carried: whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`; the SELECTION-NOTE erratum;
  superseding `KNOT-COMPOSE-20261101-001-D001`.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — full reach on honeycomb tori | **Status:** Partially successful | The failing sides are proved and explained; full reach when 3 divides the side is computed to 300, not proved |
| Local direction — where composition reaches | Research directions | Square and honeycomb tori are mapped; the triangular and rectangular tori and the proof of the computed half remain |
| Broader exploration — G5 | Known alternatives | Which finite maps rescue late rings (queued by the coordinator); B19 to B23 |
| Long-term goal — G5 Dynamics (question 4) | Capability gained | Where composition fails to reach on a lattice of persistent contacts is read off the lattice's rotations |

**Corrections:** none. **Goals:** a G5 checkpoint (capability gained); backlog B18 taken. **Assumptions:** none added or changed.

- **What the attempt leaves open.** A proof that full reach holds when 3 divides the side; why the count of missed rings is
  2(N − 1)(N − 2) + 1; which triangular and rectangular tori reach everywhere.
- **The missing bridge to the program's composed topology.** As before: a network whose lattice a law grows, so that where influence
  reaches is read from a law, not from a given lattice.

**Next step:** Research directions — the coordinator's queued epic on which finite maps rescue late rings comes next, in this thread.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Which lattices compose everywhere (B21, G5) | 2/3 — Substantial | 3/3 — Ready | Run this epic's reduction on triangular tori (rotation order 6) and rectangular ones → a rule by the lattice's rotations, or the first exception | Alternative · deferred |
| 2 | Full reach when 3 divides the side, proved (G5) | 1/3 — Minor | 2/3 — Testable | On odd sides, show that the points no power of M reaches are exactly the mirror lines, through the eigenvalues of M over GF(2) → a proof on odd sides, or the first odd side with extra points | Alternative · deferred |
| 3 | The count of missed rings (G5) | 1/3 — Minor | 2/3 — Testable | Derive 2(N − 1)(N − 2) + 1 from the halving map that carries side 2n to side n → the formula proved, or its first failure | Alternative · deferred |

1. **Which lattices.** Payoff 2: a rule that reads where composition fails from the lattice's rotation order would cover all three
   regular lattices; Concreteness 3: the reduction to windows and mirrors carries over directly. Main uncertainty: triangular rings have
   six contacts, so the windows are larger and the mirrors may pin more.
2. **The proof.** Payoff 1: it would turn a computed half into a theorem without changing the picture; Concreteness 2: the reduction is
   exact, but the extra points on even sides show the number theory is not trivial.
3. **The count.** Payoff 1: a sharpening; Concreteness 2: the halving map is exact, the recursion is not yet closed.

**Recommendation.** Research directions, none selected here; the thread moves to the coordinator's queued epic (which finite maps
rescue late rings). Reassess direction 1 when that epic closes.

## Final report as sent

Sent to the owner on 2026-11-09 at 19:33 UTC and copied here verbatim.

Full reach on honeycomb tori is settled in one direction by proof and in the other by computation, and it's published (HONEY-REACH-20261109-001):
- **When 3 doesn't divide the side, full reach always fails (proved, every side).** Influence spreads by the six-neighbour sum, and every power of it vanishes on the three mirror lines through a ring, because each mirror pairs the walks up. The 120° turn about a ring fixes exactly one ring of the other kind, and everything that would let influence into that ring lies on the mirrors. So that ring never needs the first one, and the first never needs it.
- **When 3 divides the side, full reach holds on every side checked, to 300 (computed).** The turn then fixes no ring of the other kind, and from side 7 on the mirrors pin no other ring (proved).
- **How many rings are missed (computed, to 300):** one per ring on odd sides, and otherwise exactly 2(N − 1)(N − 2) + 1, with N = 2^(v+1) and v the power of 2 in the side. That gives 13, 85, 421 and so on, whatever the odd part.

This explains the census: the obstruction is a ring pinned by a rotation of the source. On the square torus it's the antipode (half-turn, even sides); here it's the turn of order 3.

| Scope | Verdict | Why |
|---|---|---|
| This attempt: full reach on honeycomb tori | Partially successful | The failing sides are proved and explained; full reach when 3 divides the side is computed to 300, not proved |
| Local direction: where composition reaches | Research directions | Square and honeycomb tori are mapped; triangular and rectangular tori, and the proof of the computed half, remain |
| Broader exploration: G5 | Known alternatives | Which finite maps rescue late rings (queued next); B19 to B23 |
| Long-term goal: G5 Dynamics | Capability gained | Where composition fails to reach on a lattice of persistent contacts is read off the lattice's rotations |

| # | Direction | Payoff | Concreteness | First step → stop |
|---|---|---|---|---|
| 1 | Which lattices compose everywhere (B21) | 2/3 | 3/3 | Run the same reduction to mirrors on triangular and rectangular tori → a rule from the lattice's rotations, or the first exception |
| 2 | Prove full reach when 3 divides the side | 1/3 | 2/3 | On odd sides, show that the points no power reaches are exactly the mirror lines → a proof, or the first odd side with extra points |
| 3 | Prove the count of missed rings | 1/3 | 2/3 | Derive 2(N − 1)(N − 2) + 1 from the halving map from side 2n to side n → proved, or its first failure |

**Corrections:** none; the census claims of DISTANCE-20261108-001 (one ring missed on sides 4, 5, 7, 11 and 13, thirteen on 8 and 10) all hold. **Goals:** a G5 checkpoint (capability gained), and B18 is marked taken. **Assumptions:** none added or changed.

Commits on main: 38ab37ebd (the epic) and 62988d3ae (goals doc and knot intuition entry), both publishing automatically. No long-running checks: the stress test, one size past to side 300, took 162 seconds. Next I'm starting the rescued-maps epic, beginning with today's thin-tori correction.
