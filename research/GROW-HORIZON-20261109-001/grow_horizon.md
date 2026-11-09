# Distance and balls in the doubling network

Epic `GROW-HORIZON-20261109-001` (program foundations), 2026-11-09. Pre-registered in `preregistration.md` beside this note.

## The question

- **Where it comes from.** Backlog B49. `GROW-ALL-20261109-001` found the doubling law: a running tube that puts a band at every cut where
  one keeps every contact persistent finds every cut allowed, so every ring splits into a 2 × 2 block each lag. The coordinator gave B19's
  own question on it the go-ahead on 2026-11-09, with the horizon expectation pre-registered first.
- **The question.** While the network doubles, how far does each original ring's first row reach, in the original lattice's units, and
  how do the balls of rings a contact needs grow?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Doubling every lag isolates every ring.** Every contact is cut and reborn before any cell reads what it computed, so no ring ever hears another, and a contact needs only the two rings it lies on: while the network doubles every lag it reads no distance at all. | proved; checked to 96 × 96 rings | A |
| 2 | **Doubling every P lags makes a horizon.** From the 3 × 3 and 5 × 5 tubes at g = 2, an original ring's reach stays below 51/64, 3/4, 93/64, 113/64 and 155/64 original spacings for P = 2, 3, 4, 6 and 8, its growth halving at each doubling; no original ring hears it for P ≤ 4, the four nearest do for P = 6, the eight within distance 2 for P = 8. The same on both tubes. | computed, exact to four doublings | A |
| 3 | **Inside the horizon the balls fill in.** The contacts needing an original ring grow four- to tenfold per doubling, approaching fourfold, while the reach stops growing: the ball's extent is bounded and its count grows with the resolution, as an area does. | computed | A |
| 4 | **The expectations.** E1 held (proved); E2 held, the radius rising with P apart from parity (P = 3 below P = 2) and below P/g; E3 held on the odd tori and failed on the 4 × 4 control, whose unreached rings `LATTICE-NET-20261108-001A` had already found: the expectation was mine, not the record's. | against the pre-registration | A |

## Answer

The doubling network has a horizon, and at its fastest the horizon is zero. Doubling every lag, no ring ever hears another, so the plane
the law grows is a plane of declared rings that read no distance while growth goes on; distance appears only when growth stops.
Doubling every P lags, influence crosses contacts between doublings, but the rings between two original rings double faster than it
travels, so each original ring is heard only within a fixed radius in the original units, from below one spacing (P ≤ 4) to about 2.4
(P = 8), while the rings inside that radius multiply.

## Reading

**Interpretation, not a theorem.**
- **Growth outruns influence.** Influence crosses about one ring in 2g lags; doubling every P lags halves the spacing every P lags. A
  native law that grows space by refinement this fast confines every ring's influence to a neighbourhood fixed at its birth, and at the
  fastest rate to the ring itself. The resemblance to horizons in expanding models is a resemblance of counting, not a physics claim.
- **For G1.** The order-free law grows a plane, but a plane grown this way is causally a collection of patches: it reads the low
  dimension of its declared rings, not a connected distance, while it grows. A grown space that reads its own distance across time needs
  growth slow enough for influence to keep up, or growth that stops.
- **The balls read dimension two by resolution.** Inside a fixed comoving radius the contacts needing a ring multiply about fourfold per
  doubling, as the cells of a disc do when its grid is halved.

## Lag cutoffs and census-only claims

- **The theorem has no cutoff.** The horizon is read lag by lag to four doublings (three from 5 × 5); that the reach stays bounded at
  every later lag is the pattern of halving increments, not a proof.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| The theorem (1) | four tubes, two spacings, to 96 × 96 | pass (check 1) |
| The horizon (2) | the 5 × 5 tube beside the 3 × 3 | pass: the same radii within 5/64, one doubling fewer |

## Literature and provenance

- **Sources.** Light cones of additive automata (Martin, Odlyzko and Wolfram 1984); horizons in discrete models of uniform refinement.
- **Classification.** Known-with-delta: the counting is elementary; the delta is that the program's own growth law, chosen by its
  dynamics, isolates every ring at its natural rate.

## Workspace assumptions

- **Relied on.** A30, A32, A42 (confirmed), A44 (born cells open), A45 (declared rings).
- **Added.** None.

## Correction

`GROW-ALL-20261109-001`'s reading and report said that the doubling law "grows a plane while the network runs" and is "a uniform local
law that grows a plane of rings, every stage balanced". Its results stand, and it said that every contact is reborn each lag, but the
reading went beyond them: while it doubles every lag no ring hears another, so the plane is one of declared rings that reads no distance
until growth stops. Logged in `docs/CORRECTIONS.md` (2026-11-09, Not a block), with a correction section in its decision note.

## Ratio

Since the epic opened:
- **Substantive.** One proof (A) with four checks; the pre-registration; one correction of a reading.
- **Administrative.** This note and the closure.

## Pending the owner

- Nothing new.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — distance and balls in the doubling network | **Status:** Successful | A horizon, proved at zero radius for every-lag doubling and computed for every P lags |
| Local direction — a grown space that reads its own distance | Research directions | Doubling outruns influence; slower growth or a stop is needed |
| Broader exploration — G1 with G5 | Known alternatives | Why doubling keeps every stage balanced (B50); invertible substrate (B39); the horizon as a theorem |
| Long-term goal — G1 Space from a law (question 9) | Obstruction learned | The plane the law grows is causally disconnected while it grows fast; distance needs growth that influence can keep up with |

**Corrections:** one, Not a block: `GROW-ALL-20261109-001`'s plane reads no distance while it doubles every lag. **Goals:** a G1 and G5
checkpoint (obstruction learned), B49 marked taken. **Assumptions:** none added.

**Next step:** Research directions — selected: #1, as the coordinator asked (B50 next if B49 closed quickly).

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Why doubling keeps every stage balanced (B50) | 3/3 — Major | 2/3 — Testable | Pair the returns with the old lattice's translations and half-turns, which the whole history keeps → a proof at every lag, or the lag where it fails | Selected |
| 2 | The horizon as a theorem | 2/3 — Substantial | 2/3 — Testable | Bound the rings influence crosses between doublings by the time of flight (g·δ + 1) and sum the halving spacings → a proved radius for each P | Alternative · deferred |
| 3 | Growth slow enough to read distance | 2/3 — Substantial | 2/3 — Testable | Double only when influence has crossed the current spacing (P growing with the side) → a grown plane that reads its distance across time, or none | Alternative · deferred |
| 4 | Invertible substrate (B39) | 2/3 — Substantial | 3/3 — Ready | As before | Alternative · deferred |

**Recommendation.** Research directions, #1 as ordered; stop it at a proof or at the lag where balance fails.
