# Native paths across time

Epic `NATIVE-PATH-20261108-001` (program foundations), 2026-11-08.

## The question

- **Where it comes from.** It is the selected next step of `AFFINE-WIRE-20261108-001`, which found persistent native networks of
  two contacts across time on affine substrates. The coordinator relayed the go-ahead on 2026-11-08 with instructions:
  - search restricted families first, reusing the rule-150 wire and the 430 carrying chains;
  - register any sweep over about ten minutes in `docs/LONG_RUNNING.md`;
  - park the other directions in the backlog.
- **The question.** A native path is a path of four rings A, B, C and D, joined by three shared contacts c1, c2 and c3, in which:
  - every contact binds its own two rings at every lag;
  - the last contact binds the end rings A and D at every lag from the light-cone lag on.

  This is the first composed topology across time: two compositions in a row.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The light cone of a path.** The last contact cannot depend on the first ring before lag d_1 + … + d_(n−2) + 1, the distances between the contacts of the middle rings plus one. | proved; computed on 400 four-ring and, one size past, 300 five-ring paths with arbitrary rules | A |
| 2 | **Affine paths reduce to row sequences.** Every verdict of an affine path is decided exactly by the contacts' row sequences of M^T. | proved; checked against full state spaces on 800 paths | A |
| 3 | **No native path in two restricted families.** Rule 150 on all four rings with every law: 900,000 paths. The 430 carrying chains extended by one end ring: 96,840 paths. 762 keep all three contacts persistent, and none binds its end rings. The middle contact often carries the first ring at every lag (302 of the 762); the loss happens across the second middle ring. | exploratory search (H1 fails) | B |
| 4 | **A shift as the second middle ring keeps no contact.** Of 3,059,280 paths whose second middle ring is a shift, none keeps all three contacts persistent. A shift uses up its own first row within one turn and then holds only its contacts' pasts. | exploratory search (H1 fails) | C |

## Answer

In the families searched, no native path exists. The second middle ring must do two things at once:
- keep its own first row, so that both of its contacts keep binding it;
- carry the first ring's influence from one contact to the other without cancelling it.

The additive rules of ticket B keep their first row but cancel the influence on the way. The shift of ticket C carries without
cancelling but loses its first row. The absence is for these three families only. A broader sweep is the next step, and a wider
run of the first family (rule 150, one size past) is pending.

## Reading

**Interpretation, not a theorem.**
- **For the program's composed topology.** One contact passes the gate across time (`PROCESS-CONTACT-20261108-001`,
  `SHARED-CONTACT-20261108-001`), and two contacts compose persistently on affine substrates (`AFFINE-WIRE-20261108-001`). A path
  of three contacts, the first adjacency beyond a single composition, has not been found.
- **A tension.** A middle ring between two contacts must both remember and transmit. The rings tested do one or the other. This
  is a candidate obstruction, not a theorem.
- **The lesson applied.** An absence found in restricted families names its families (`docs/CORRECTIONS.md`, 2026-11-08).

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| The light cone (A), four-ring paths | 300 five-ring paths with arbitrary elementary rules, full state spaces (`stress_quick.json`) | pass: no dependence before the light cone |
| No native path with rule 150 everywhere (B) | end rings to 6 cells, middle rings to 8: NATIVE-PATH-S1 in `docs/LONG_RUNNING.md` (`stress_wide.json`) | stress test pending |

## Literature and provenance

- **Sources.** Light cones of automata on graphs, and linear recurring sequences over GF(2).
- **Classification.**
  - **Ticket A.** Known-with-delta: elementary.
  - **Tickets B and C.** New as far as found: searches for native paths across time.

## Workspace assumptions

- **Relied on.** A30, A32, A34.
- **Scope.** Linear rules, contact laws by their linear parts, the declared families and sizes.

## Ratio

Since the epic opened:
- **Substantive.** Three evidence families: A (a proof), B and C (exploratory searches, both negative in their families).
- **Administrative.** This note and the closure.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — native paths of four rings | **Status:** Negative evidence | None in three restricted families, about 4.06 million paths |
| Local direction — paths across time | Research directions | A second middle ring must remember and transmit; no tested ring does both |
| Broader exploration — G5 with G1 | Known alternatives | A broad sweep of mixed paths; designing the middle ring algebraically; backlog B9–B11 |
| Long-term goal — G5 Dynamics (question 4) | Obstruction learned | Two contacts compose across time, and paths of three have not been found |

**Corrections:** none. **Goals:** a G5 checkpoint (obstruction learned). **Assumptions:** none added.

- **What the attempt leaves open.**
  - Paths with mixed rules on all four rings and all laws: the broad family, which was not searched.
  - A middle ring designed to keep its first row while it transmits.
- **The missing bridge to the program's composed topology.** A path of contacts, each composing with the next, at every lag.

**Next step:** Research directions — the main hypothesis failed in the restricted families, so the next step is a bounded search,
not a continuation of these families.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A broad sweep of mixed four-ring paths (G5, with G1) | 2/3 — Substantial | 3/3 — Ready | Every linear rule on each ring, sizes 3/4/4/3 to 4/5/5/4, all laws, registered as long-running → a native path, or none in the family | Alternative · deferred |
| 2 | A middle ring designed to remember and transmit (G5) | 3/3 — Major | 1/3 — Stated | From the row algebra: a middle-ring rule and contact laws whose own first row never leaves both contacts while the first ring's part never cancels → a construction, or a proof that the two conflict | Alternative · deferred |
| 3 | The pulse law of affine chains (backlog B9) | 2/3 — Substantial | 2/3 — Testable | Parked | Backlog |
| 4 | Persistent composition on nonlinear substrates (backlog B10) | 2/3 — Substantial | 1/3 — Stated | Parked | Backlog |

**Recommendation.** Research directions. Run direction 1 as a registered long-running sweep. If it finds no native path, try
direction 2 once. If that also fails, pause the process line and reassess G5 against question 4, which the line has answered for
one process, one contact and two contacts.
