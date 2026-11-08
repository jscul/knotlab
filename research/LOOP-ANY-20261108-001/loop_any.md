# Balanced loops of any number of rings

Epic `LOOP-ANY-20261108-001` (program foundations), 2026-11-08.

## The question

- **Where it comes from.** `LOOP-PROOF-20261108-001` proved that in four-ring loops the feedback returning round the loop cancels
  when the contacts' positions sum to 2s. The coordinator relayed its direction 1 on 2026-11-08: find when the feedback cancels in an
  r-ring loop and check r = 5 to 8 at sizes 4 to 16, stopping with a theorem for every r or the first r with no persistent balanced
  loop.
- **The question.** For which loops of r rings does every contact keep binding both of its rings at every lag?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The feedback is a polynomial in a shift.** For any number of rings, C = S + KC with K = z(A + cA^(−1)): A is the weighted cyclic shift of the chains, and c = a^(s−2) is a scalar, since going back and forth across any ring costs the same. | proved | A |
| 2 | **Balance cancels every return.** When the positions sum to rs/2, every diagonal entry of (I − K)^(−1) is 1. The returns to a contact pair up as C(m, j) with C(m, m − j) and cancel mod 2, and the central binomials are even. | proved | A |
| 3 | **So balanced loops persist for every number of rings.** Every contact binds both of its rings at every lag at every ring size, through the ends of the two chains it reads. The antipodal loops, every contact halfway round, persist for every number of rings and every even size. | proved; checked on 1,266 loops of 2 to 10 rings and on full state spaces | A |
| 4 | **The feedback is finite only for powers of two.** It is a finite sum, with K^(r/2) = 0, exactly when r is a power of two and the loop is balanced. For other r it never ends, though its diagonal still vanishes. | proved; checked by exact rational functions | A |
| 5 | **Balance is sufficient, not necessary.** Of 65,472 loops of 5 to 8 rings at sizes 4 to 16, all 5,354 balanced ones persist to lag 400 through the witnesses, and so do 11,322 unbalanced ones, through other cells. | exploratory census | B |

## Answer

The stop rule's first outcome holds: a theorem for every number of rings. A loop of r rings whose contacts' positions sum to rs/2
keeps every contact binding both of its rings at every lag, at every ring size. Influence returns round it, and the returns to each
contact cancel. For four or eight rings, or any power of two, the feedback even dies out after r/2 steps. For other numbers it goes on
forever, but its returns still cancel. Unbalanced loops can persist too, by another mechanism the proof does not cover.

## Reading

**Interpretation, not a theorem.**
- **Why balance works.** Crossing a ring forward and back costs a^(s−2) whichever ring it is, so the feedback is a shift plus a
  multiple of its inverse. A return to a contact winds t times one way or the other, and balance makes the two ways weigh the same, so
  they cancel in pairs.
- **For composed topology across time.** Closed routes of contacts of every length now hold at every size, by proof. The cycle side of
  composed topology across time is complete for these loops: paths, separation, and loops of any length.
- **Powers of two.** That finiteness picks out powers of two is the characteristic-2 signature again: squaring is linear there, so
  only loops of length 2^p let the feedback square away.
- **Not a metric.** Nothing here is a length or a distance.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| Balanced loops persist (3) | 2 to 8 rings at sizes 4 to 20 (random balanced and antipodal positions), and antipodal loops of 2 to 10 rings | pass: 1,266 loops, every lag to 300 |
| Every balanced loop of 5 to 8 rings (5) | 5,354 balanced loops at sizes 4 to 16 | pass: all persist to lag 400 |

## Literature and provenance

- **Sources.** Generating functions over GF(2); the binomial theorem in characteristic 2; Lucas' theorem.
- **Classification.** Ticket A: known-with-delta. Ticket B: new as far as found, a census of persistent loops of contacts.

## Workspace assumptions

- **Relied on.** A30 (two-time knots), A32 (binding), A37 (composition at recurring lags).
- **Scope.** Rule-60 rings (rule 102 by mirror symmetry), laws (12, 12) and (6, 6) under condition W.

## Ratio

Since the epic opened:
- **Substantive.** One proof (A) and one census (B).
- **Administrative.** This note and the closure.

## Pending the owner

- **Counted length as a native magnitude**, which gates distance across time; put to the owner by the coordinator.
- Carried: whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`; the SELECTION-NOTE erratum;
  superseding `KNOT-COMPOSE-20261101-001-D001`.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — loops of any number of rings | **Status:** Successful | A theorem for every r; the census agrees for r = 5 to 8 |
| Local direction — composed topology across time | Research directions | Single loops are done; what comes next, loops that share rings or the unbalanced mechanism, is a choice |
| Broader exploration — G5 with G1 | Known alternatives | The rule-90 mechanism (B13); restrictions (B14); distance, once the owner rules |
| Long-term goal — G5 Dynamics (question 4) | Capability gained | Closed routes of contacts of every length hold at every size, by proof |

**Corrections:** none. **Goals:** a G5 checkpoint (capability gained). **Assumptions:** none added.

- **What the attempt leaves open.**
  - Rings with three or more contacts, so that loops share rings: the first structure with more than one independent loop.
  - The mechanism behind the 11,322 unbalanced loops that persist.
- **The missing bridge to the program's composed topology.** Networks of loops, and then a lattice of rings, which would bring G1's
  space-from-a-law question into time.

**Next step:** Research directions — the epic's question is answered for every r, and the next structure is a choice between widening
to networks of loops and deepening the single loop.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Networks of loops: rings with three or more contacts (G5, with G1) | 3/3 — Major | 2/3 — Testable | Give one ring a third contact so that two loops share it; extend the generating functions to the network and find the balance condition for each loop → persistence of every contact at every size, or the obstruction where loops meet | Alternative · deferred |
| 2 | Why unbalanced loops persist (G5) | 2/3 — Substantial | 2/3 — Testable | Classify the 11,322 unbalanced persistent loops by which cells witness each contact; prove the commonest mechanism → a second sufficient condition, or loops that fail past lag 400 | Alternative · deferred |
| 3 | The rule-90 mechanism (backlog B13) | 2/3 — Substantial | 2/3 — Testable | Parked | Backlog |
| 4 | Distance across time | 3/3 — Major | 1/3 — Stated | Waits on the owner's ruling on counted length | Alternative · deferred |

1. **Networks of loops.**
   - **Payoff 3.** Two loops sharing a ring are the first structure with more than one independent cycle, and a lattice of rings would
     be space across time.
   - **Concreteness 2.** The generating functions extend; how two balance conditions interact at a shared ring is the open part.
   - **Uncertainty.** Whether a ring with three contacts still lets each contact keep its witnesses.
2. **Unbalanced loops.** Narrower; it deepens the single loop.
3. **The rule-90 mechanism.** Parked as B13.
4. **Distance.** Waits on the owner.

**Recommendation.** Research directions, leaning to direction 1. The process line has run fourteen epics today, so if the coordinator
prefers to pause it until the owner rules on distance, the single-loop results stand as a complete stage.
