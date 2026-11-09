# Which lattices compose everywhere

Epic `LATTICE-REACH-20261109-001` (program foundations), 2026-11-09.

## The question

- **Where it comes from.** `LATTICE-NET-20261108-001A` proved that on the n × n square torus every contact needs every ring exactly when
  n is odd, and found rectangular tori that fail only when a side is even. `HONEY-REACH-20261109-001` found the honeycomb obstruction: the
  ring pinned by the turn of order 3. Backlog B21 asked which tori of the three lattices compose everywhere; the coordinator selected it on
  2026-11-09.
- **The question.** On tori of every shape of the square, triangular and honeycomb lattices, when does every contact need every ring?
  Stop at a characterisation, or at the first family no rule tried explains.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Digon faces stop composition.** A torus has a digon face exactly when its lattice holds (1, ±1) (square) or a unit (honeycomb), never on the triangular lattice; then a one-step factor of the walk polynomial vanishes and every contact needs at most a handful of rings (4 and 6 in every case read). | proved | A |
| 2 | **One power covers almost everything on odd square tori.** On every square torus of odd index without digons, L^(2^r − 1) is 1 off the symmetric difference of the two diagonal subgroups. | proved | A |
| 3 | **Odd index: composition reaches everywhere but at digons and the pinned ring.** At odd index 3 to 151, a square torus composes everywhere exactly when it has no digon, every triangular torus does, and a honeycomb torus does exactly when it has no digon and is not the n × n torus with 3 ∤ n, except one torus of index 63 (three lattices, one per mirror). | computed, 20,910 tori | A, stress test |
| 4 | **Even index has no simple rule.** To index 48, 89%, 84% and 68% of the square, triangular and honeycomb tori without digons compose everywhere, and neither the lattice modulo 16, nor the 2-part of the torus's group, nor its mirror symmetries decide which. | computed | A |

## Answer

At odd index the answer is nearly complete: composition reaches everywhere on every torus of the three lattices except where it has a
digon face, which kills a factor of the walk polynomial, and on the honeycomb n × n tori whose side 3 does not divide, where the turn of
order 3 pins a ring; one honeycomb torus of index 63 is the only other exception to index 151. At even index the walk counts fold under
doubling, and whether composition reaches everywhere is not decided by any of the lattice invariants tried. The stop rule's second
outcome holds for even index.

## Reading

**Interpretation, not a theorem.**
- **Obstructions are local or symmetric.** A digon is a local defect: two rings meet twice in a row and their walks cancel at once. The
  pinned ring is a global symmetry. At odd index those are all there is, apart from one sporadic torus.
- **The prime 2 is special.** Squaring is additive over GF(2), so doubling the lattice is what powers of the walk polynomial see, and at
  even index the parity of sums over the 2-torsion decides reach at every scale. The square torus's antipode is the simplest case.
- **Given, not grown.** The tori are given, not grown from a law.

## Lag cutoffs and census-only claims

- **No lag cutoff.** Reach follows rows of walk counts until the next lies in the span of the earlier ones.
- **Census-only.** Conclusions 3 and 4: every lattice of odd index to 151 (index 81 in the ticket's check, the rest in the stress test)
  and of even index to 48.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| The odd-index rule (3) | every lattice of odd index 83 to 151 (checked to 81), the three lattices | pass: 4,939, 4,904 and 5,009 tori, no exception |

The script is `stress_test.py` beside this note, its output `stress_test.json`; it ran in 99 seconds.

## Literature and provenance

- **Sources.** Linear cellular automata over GF(2) on finite abelian groups (Martin, Odlyzko and Wolfram 1984); the Frobenius map on group
  algebras of abelian groups of even order; `LATTICE-NET-20261108-001A` and `HONEY-REACH-20261109-001A` for the n × n tori.
- **Classification.** Known-with-delta.

## Workspace assumptions

- **Relied on.** A30 (two-time knots), A32 (binding), A37 (composition at recurring lags).
- **Added.** None.
- **Scope.** Tori of every shape of the three regular lattices of rule-60 rings with equally spaced law-(12, 12) contacts.

## Ratio

Since the epic opened:
- **Substantive.** One proof (A) with five checks, one stress test.
- **Administrative.** This note and the closure.

## Correction (2026-11-09)

- **A doubled pair, not a face.** What Theorem 1 calls a digon face, two contacts consecutive on both rings they share, is not a face:
  every face of these tori keeps the lattice's size. Read it as a doubled pair, the same order on both rings (`REROUTE-20261109-001A`;
  `docs/CORRECTIONS.md`). Wording only; every result stands.

## Pending the owner

- None new.
- Carried: whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`; the SELECTION-NOTE erratum;
  superseding `KNOT-COMPOSE-20261101-001-D001`.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — which lattices compose everywhere | **Status:** Partially successful | Odd index is characterised (computed, with its obstructions proved); even index has no rule by the invariants tried |
| Local direction — where composition reaches | Research directions | The odd-index positive half and the even-index mechanism are open |
| Broader exploration — G5 | Known alternatives | Rescue on maps of higher genus (B27, selected by the coordinator); B20, B22 |
| Long-term goal — G5 Dynamics (question 4) | Obstruction learned | Composition across a flat network fails only at digons and pinned rings at odd index; at even index the 2-adic folding of walk counts decides, with no rule found |

**Corrections:** none. **Goals:** a G5 checkpoint (obstruction learned); B21 taken; backlog B29 to B31 added. **Assumptions:** none
added or changed.

- **What the attempt leaves open.** A proof that odd-index tori without digons compose everywhere; the rule at even index; why the index-63
  honeycomb torus fails.
- **The missing bridge to the program's composed topology.** As before: networks whose lattice a law grows.

**Next step:** Research directions — selected: rescue on maps of higher genus (B27), by the coordinator on 2026-11-09, in this thread.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Rescue on maps of higher genus (B27, G5) | 2/3 — Substantial | 2/3 — Testable | Look for short closed walks with a unique fastest way in the 141 on-time maps against the 565 late ones → the same mechanism, or a different one | Selected · this thread |
| 2 | Odd-index full reach proved (G5) | 1/3 — Minor | 2/3 — Testable | Extend Theorem 2 with the other contact kind and the other powers, as `LATTICE-NET-20261108-001A` did for A ∩ B = 0 → a proof for square tori, or the case it cannot close | Alternative · deferred |
| 3 | The even-index mechanism (G5) | 2/3 — Substantial | 1/3 — Stated | Write reach on G through the tower of doublings G → 2G → 4G … and the 2-torsion fibres → a rule, or the first torus it misreads | Alternative · deferred |
| 4 | The index-63 honeycomb torus (G5) | 1/3 — Minor | 2/3 — Testable | Split GF(2)[Z_63] by its 7- and 9-parts and find where the six missed rings cancel → the mechanism, or none | Alternative · deferred |

**Recommendation.** Research directions, selected #1 at the coordinator's instruction; #2 to #4 go to the backlog as B29 to B31.

## Final report as sent

Sent to the owner on 2026-11-09 at 20:18 UTC and copied here verbatim.

Which lattices compose everywhere (B21) is closed and published (LATTICE-REACH-20261109-001). At odd index it is nearly characterised; at even index no simple rule exists among the invariants I tried.
- **Digon faces stop composition (proved).** If the lattice holds (1,±1) on the square or a unit on the honeycomb, two rings meet at two contacts in a row. Their walks cancel at once, a factor of the walk polynomial vanishes, and every contact needs at most a handful of rings (4 and 6 in every case read). The triangular lattice has no such tori.
- **At odd index nothing else does, nearly (computed, 20,910 tori to index 151).** Every triangular torus composes everywhere, and so does every square one without a digon. Every honeycomb one without a digon does too, except the n × n tori whose side 3 doesn't divide (the pinned ring from the honeycomb epic) and one sporadic torus of index 63, where each contact misses 6 of 126 rings.
- **One power covers almost everything on odd square tori (proved):** L^(2^r−1) is 1 off the symmetric difference of the two diagonal subgroups. That generalises the n × n proof's key step but doesn't close every shape alone.
- **At even index there is no rule by the lattice mod 16, the torus group's 2-part, or its mirrors (computed to index 48).** 89%, 84% and 68% of square, triangular and honeycomb tori compose everywhere. Squaring the walk polynomial doubles the lattice, and at even index doubling folds the torus onto half of itself.

| Scope | Verdict | Why |
|---|---|---|
| This attempt: which lattices compose everywhere | Partially successful | Odd index characterised (computed, obstructions proved); even index has no rule by the invariants tried |
| Local direction: where composition reaches | Research directions | The odd-index positive half and the even-index mechanism are open |
| Broader exploration: G5 | Known alternatives | Rescue on higher-genus maps (B27, selected); B20, B22 |
| Long-term goal: G5 Dynamics | Obstruction learned | At odd index composition fails only at digons and pinned rings; at even index the prime 2 decides |

| # | Direction | Payoff | Concreteness | First step → stop |
|---|---|---|---|---|
| 1 | Rescue on higher-genus maps (B27) | 2/3 | 2/3 | Short closed walks with a unique fastest way in the 141 on-time maps vs the 565 late ones → same mechanism, or another |
| 2 | Prove odd-index full reach (B29) | 1/3 | 2/3 | Extend the 2^r−1 power with the other contact kind → proof for square tori, or the case it can't close |
| 3 | The even-index mechanism (B30) | 2/3 | 1/3 | Write reach through the tower of doublings and the 2-torsion fibres → a rule, or a misread torus |
| 4 | The index-63 honeycomb torus (B31) | 1/3 | 2/3 | Split GF(2)[Z_63] into its 7- and 9-parts → where the missed rings cancel |

**Corrections:** none. **Goals:** a G5 checkpoint (obstruction learned); B21 marked taken; B27 selected; B29 to B31 added to the backlog. **Assumptions:** none added or changed.

Commits on main: f05c2c422 (the epic) and 398feab75 (goals doc and knot intuition entry). I staged only my own hunks this time. The stress test, one size past to odd index 151, passed in 99 seconds. Starting B27 now.
