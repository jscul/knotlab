# Composition and separation across a lattice of rings

Epic `LATTICE-NET-20261108-001` (program foundations), 2026-11-08.

## The question

- **Where it comes from.** `LOOP-NET-20261108-001` proved that lattices of rings on a torus keep every contact persistent at every
  size. The coordinator relayed its direction 1 on 2026-11-08: on the square torus, find which contacts each contact needs and when,
  then test whether a ring of cuts separates it, and stop at a theorem or at the size where composition stops reaching.
- **The question.** In a lattice of persistent contacts, does influence reach across the whole torus, and do rings of cuts separate it
  the way closed curves separate a surface?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Composition is the four-neighbour sum.** Two steps from a contact land on the four neighbouring contacts of its kind, one walk each, so influence spreads by the powers of L = x + 1/x + y + 1/y = (x + y)(1 + 1/xy) over GF(2). A contact needs a ring exactly when an odd number of walks of some length k lead from one of the ring's contacts to it. It first needs the ring at lag g·k + 1, and then at infinitely many lags, eventually periodically. | proved | A |
| 2 | **On odd tori composition reaches every ring.** Every power of L vanishes on the two diagonals except at the origin, and L^(2^r − 1) is 1 at every point off them; the rings on the diagonals are reached through the other kind of contact. So every contact needs every ring. | proved; checked exactly to side 21 | A |
| 3 | **On even tori it never reaches the antipode.** The routes round the torus in opposite directions pair up and cancel, so a contact never needs the ring halfway round in both directions. When the side is a power of two the feedback is finite. | proved; checked exactly to side 20 | A |
| 4 | **A ring of cuts separates when it bounds.** Cutting the contacts round any set of rings leaves no route across: a native separation, since on odd tori every contact needed every ring before the cut. One ring of cuts round the torus does not separate, because influence still goes round the other way, by a single walk; two such rings do. | proved; checked exactly to side 12 and at cell level | A |
| 5 | **The antipode is a symmetry effect, not a range.** On rectangular tori a ring that some contact never needs appears only on some shapes: 4 × 4, 4 × 8, 4 × 12, 6 × 6, 8 × 8, 8 × 12 and 10 × 10 of 52 checked, never with an odd side. A cut can even add reach: after one ring of cuts round the 4 × 4 torus, 24 of the 28 uncut contacts need every ring. | computed | A, checks 8 and 11 |

## Answer

The stop rule's two outcomes both occur. For every odd side there is a theorem: composition reaches every ring. Composition stops
reaching at every even side, first at side 4, where no contact ever needs the ring antipodal to it. Native separation across the lattice
behaves as on a surface: a ring of cuts that bounds separates, one that goes round the torus once does not, and two do.

## Reading

**Interpretation, not a theorem.**
- **Separation sees the handle.** Adjacency, native paths and separation now hold on a two-dimensional lattice of persistent contacts,
  and separation shows something paths and loops could not: a ring of cuts round the torus leaves it in one piece. Native separation
  across time tells a torus from a disc.
- **Why the parity of the side matters.** Influence spreading round the torus meets itself. On an even square torus the two ways to the
  antipode are mirror images and cancel mod 2. This is `LOOP-NET-20261108-001`'s pairing of returns, now acting on the influence between
  two contacts.
- **First lags are lags.** The first lag g·k + 1 at which a ring is needed counts steps; it is not offered as a distance, which waits on
  the owner's ruling on counted length.
- **Given, not grown.** The lattice is given, not grown from a law, so this is not G1's space from a law.

## Lag cutoffs and census-only claims

- **This epic used no census and no lag cutoff.** Every reading follows walk counts until the next row lies in the span of the earlier
  ones, powers of L until they repeat, or rows of M^T until they repeat.
- **Earlier claims that rest on a lag cutoff, marked census-only.** `LOOP-NET-20261108-001B`'s 500 placements persistent to lag 300 and
  `LOOP-ANY-20261108-001B`'s 11,322 unbalanced loops persistent to lag 400 are undecided beyond those lags. `LOOP-NET-20261108-001A`'s
  check 9 records networks persistent to lag 600 that first miss a ring at lags 630 to 1,143, and a scratch diagnosis at spacing 15 found
  one at lag 154,468, not recorded in a check.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| Odd tori reach every ring (2) | sides 23 and 25 for the powers of L, 15 and 17 for the contacts | pass |
| Even tori never reach the antipode (3) | sides 22 and 24 for the powers of L, 18 and 20 for the contacts | pass |
| A bounding ring of cuts separates (4) | blocks of 2, 5 and 8 rings a side on the 10 × 10 and 11 × 11 tori | pass |
| One ring of cuts round the torus does not separate; two do (4) | one at sides 13 and 14, two at sides 11 and 12 | pass |

## Literature and provenance

- **Sources.** Additive cellular automata read through polynomials over GF(2) modulo x^n − 1 (Martin, Odlyzko and Wolfram 1984); Lucas'
  theorem; Menger's theorem; closed curves that bound and that do not on a surface.
- **Classification.** Known-with-delta. The delta is composition and native separation across time on a lattice of rings, decided by
  the parity of the torus's side, with separation that fails for a ring of cuts that does not bound.

## Workspace assumptions

- **Relied on.** A30 (two-time knots), A32 (binding), A37 (composition at recurring lags), A38 (a cut freezes a contact).
- **Scope.** Square tori of rule-60 rings with equally spaced law-(12, 12) contacts.

## Ratio

Since the epic opened:
- **Substantive.** One proof (A) with twelve checks.
- **Administrative.** This note and the closure.

## Pending the owner

- **Counted length as a native magnitude**, which gates distance across time; put to the owner by the coordinator. The first lags
  g·k + 1 are the counts such a distance would use if the owner rules counted length native.
- Carried: whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`; the SELECTION-NOTE erratum;
  superseding `KNOT-COMPOSE-20261101-001-D001`.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — composition and separation across a lattice | **Status:** Successful | A theorem for odd sides; composition stops reaching at every even side; rings of cuts separate when they bound |
| Local direction — composed topology across time | Research directions | The order up to separation holds on the lattice; distance is next and waits on the owner |
| Broader exploration — G5 with G1 | Known alternatives | Genus read by cuts; other lattices and rectangular tori; the rule-90 mechanism (B13); restrictions (B14) |
| Long-term goal — G5 Dynamics (question 4) | Capability gained | Native paths and separation across a two-dimensional lattice of persistent contacts, with separation that sees the torus's handle |

**Corrections:** none. **Goals:** a G5 checkpoint (capability gained). **Assumptions:** none added.

- **What the attempt leaves open.**
  - How many rings of cuts can be made without separating, and whether that count reads the genus of the surface the rings form.
  - Which rectangular tori, and which triangular and honeycomb lattices, leave rings unreached, and why.
- **The missing bridge to the program's composed topology.** Distance across time, which waits on the owner, and a native reading of
  the surface's genus.

**Next step:** Research directions — the epic's question is answered; what comes next is a choice between reading genus by cuts and
mapping the shapes where composition reaches, while distance waits on the owner.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Genus read by rings of cuts (G5, with G1) | 3/3 — Major | 2/3 — Testable | On the odd square torus, cut a ring of cuts round it in each direction together and test whether the torus stays in one piece; then build a genus-2 lattice of rings with even returns and find the most rings of cuts that leave it in one piece → that count is 2 per handle, or the first surface where it is not | Alternative · deferred |
| 2 | Which lattices compose everywhere (G5) | 2/3 — Substantial | 3/3 — Ready | Extend the reach computation to rectangular, triangular and honeycomb tori and prove the rule behind 4 × 8 and 6 × 6 against 4 × 6 → a criterion, or the first exception | Alternative · deferred |
| 3 | Distance across time | 3/3 — Major | 1/3 — Stated | Waits on the owner's ruling on counted length | Alternative · deferred |
| 4 | The rule-90 mechanism (backlog B13) | 2/3 — Substantial | 2/3 — Testable | Parked | Backlog |

1. **Genus by cuts.**
   - **Payoff 3.** A count of cuts that leave the network in one piece would be a native, across-time reading of the surface's genus.
   - **Concreteness 2.** The cut machinery and the exact reach computation carry over; genus-2 networks of rings need a regular map with
     even returns.
   - **Uncertainty.** Whether cancellation on a cut network ever disconnects influence that the surface keeps connected.
2. **Which lattices.** Narrower; it explains where the antipode gap appears.
3. **Distance.** Waits on the owner.
4. **Rule 90.** Parked as B13.

**Recommendation.** Research directions, leaning to direction 1. The process line has run sixteen epics today, so pausing it until the
owner rules on distance is also reasonable; the lattice results stand as a complete stage.

## Final report as sent

Sent to the owner on 2026-11-08 at 15:42 UTC and copied here verbatim.

**The lattice of rings is done, and both outcomes of the stop rule occur.** Epic and docs are committed and published (ac0909bf2, 13081492b).

- **Which contacts and when (proved).** Influence spreads by powers of the four-neighbour sum x + 1/x + y + 1/y over GF(2). A contact needs a ring exactly when an odd number of walks lead from that ring to it. The first such lag is g·k + 1, and the need then recurs.
- **Odd sides reach everywhere, even sides never the antipode (proved).** On an odd torus every contact needs every ring. On an even torus the two ways round to the ring halfway across cancel, so no contact ever needs it. The smallest such size is 4. On rectangular tori the gap appears only on some shapes (computed), so it comes from symmetry, not from limited reach.
- **Rings of cuts (proved).** Cutting round any block of rings separates it, which is native separation on odd tori. One ring of cuts round the torus does not separate, because influence goes round the other way, and two rings do. So separation tells a torus from a disc.
- **Lag cutoffs.** This epic used no census and no cutoff; every reading is exact. The note marks the earlier census-only claims: the lag-300 and lag-400 counts, and the late misses up to lag 154,468.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: lattice of rings | Successful | Theorem for odd sides; composition stops reaching at every even side; cuts separate when they bound |
| Local direction: composed topology across time | Research directions | Order up to separation holds on the lattice; distance is next and waits on John |
| Broader exploration: G5 with G1 | Known alternatives | Genus read by cuts; which lattices compose everywhere; B13, B14 |
| Long-term goal: G5 Dynamics | Capability gained | Native paths and separation across a 2D lattice, and separation that sees the torus's handle |

**Next step:** Research directions, leaning to #1.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Genus read by rings of cuts | 3/3 | 2/3 | Cut round the torus in both directions together and test whether it stays in one piece; then a genus-2 lattice → the most cuts that keep one piece is 2 per handle, or the first surface where it isn't | Deferred |
| 2 | Which lattices compose everywhere | 2/3 | 3/3 | Prove the rule behind 4×8 and 6×6 failing while 4×6 doesn't; triangular and honeycomb | Deferred |
| 3 | Distance across time | 3/3 | 1/3 | Waits on John's ruling on counted length | Deferred |
| 4 | Rule-90 mechanism (B13) | 2/3 | 2/3 | Parked | Backlog |

**Corrections:** none. **Goals:** G5 checkpoint (capability gained). **Assumptions:** none added.

This is the line's sixteenth epic today, so pausing until John rules on distance is reasonable too.
