# Paths through mixed middle rings

Epic `PATH-HYBRID-20261108-001` (program foundations), 2026-11-08.

## The question

- **Where it comes from.** `NATIVE-PATH-20261108-001` found no native path of four rings in three restricted families. It
  recommended a broad sweep of mixed paths, then a middle ring designed to remember and transmit. The coordinator relayed the
  go-ahead on 2026-11-08 with instructions:
  - run the sweep in the background, registered as long-running;
  - meanwhile make the second direction concrete with middle rings that are not uniform within the ring, some cells shifting and
    some additive, or a ring with one extra cell acting as a buffer;
  - if the sweep returns first with a positive, fold it in and characterise it.
- **The question.** Is there a native path? Four rings A, B, C and D are joined by contacts c1, c2 and c3. The path is native when
  every contact binds its own two rings at every lag and c3 binds the end rings A and D at every lag from the light-cone lag on.
  - **Ticket A.** One linear rule on each ring, any laws.
  - **Ticket B.** A hybrid second middle ring, whose cells run different linear rules.
  - **Ticket C.** What makes the hybrid paths work.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Native paths exist with one rule per ring.** Of 20,480,000 paths (every linear rule on each ring, every law at each contact, shapes 3/4/4/3 and 3/5/5/3), 17,192 keep all three contacts and 16 are native. All 16 are one construction: 3-cell shift end rings (rule 170 or 240), 5-cell rule-150 middle rings with their contacts two apart, c1 and c3 reading both neighbours on both rings, and c2 reading one cell on each middle ring, the one on the short arc toward that ring's other contact. | exploratory search (H1 holds); every verdict exact; the ten smallest verified on full state spaces | A |
| 2 | **How the construction works.** From lag 3 on, an end contact's input from its shift ring is its own value two and three lags back, so the end ring and its contact form a feedback shift register with polynomial x³ + x + 1, which never forgets. With rule 150 on the end rings the same paths keep none of their contacts: a 3-cell rule-150 ring's two cells are equal from lag 1 on, and the contact reads their sum. At every lag from 5 to 10 the smallest path's last contact has one knot, of 8 to 10 places, meeting all four rings. | computed exactly on all 16 (`uniform_paths.json`); canonical check by the generic enumerator and knotlab (`stress_test.json`) | A |
| 3 | **Hybrid middle rings give many more.** Of 3,175,200 paths with a hybrid second middle ring, 18,592 keep all three contacts and 1,120 are native, each binding all four rings at its last contact. | exploratory search (H1 holds); every verdict exact; the ten smallest verified on full state spaces | B |
| 4 | **What a hybrid ring does.** Each of the 1,120 needs its hybrid ring: no uniform linear ring in its place keeps it native. The last contact's eventual support keeps two or three of the hybrid ring's own cells. The smallest's knot through c3 meets all four rings at lags 5 to 10. | exploratory; canonical check by the generic enumerator and knotlab | C |
| 5 | **They exist only at particular sizes.** None of 11,600 larger versions of the uniform construction is native, and 10,912 of them keep no contact at all. The larger versions have end rings to 5 cells and middle rings to 7, with every position and every one-sided law at c2. None of 512 five-ring versions is native. One more cell on ring D keeps 928 of the 1,120 hybrid paths native, and one more cell on ring A or ring B keeps none. Every native path found has contact row periods of at most 12, while 99% of the larger uniform versions have longer ones, up to 131,071. | stress test, exact; 448 larger versions undecided within 200,000 lags (`stress_test.json`, `periods.json`) | A, B |

## Answer

Native paths across time exist. Four rings joined by three contacts can have every contact binding its two rings at every lag
while the last contact binds the end rings at every lag once the first ring can reach it. This is the first composed topology of
three contacts across time.
- **With one rule per ring** there is a single construction of 16 paths:
  - shift end rings, which remember through their contacts;
  - rule-150 middle rings, which carry;
  - a middle contact that relays along the short arcs.
- **With hybrid middle rings** there are 70 times as many in a smaller family.

NATIVE-PATH's candidate obstruction does not hold, since rule 150 does both jobs as a middle ring; the diagnosis is corrected.

The paths found are tied to their sizes. The uniform construction fails at every larger size tested and with a fifth ring, and the
hybrid paths survive growth only at the far end. Transport, which the network gate requires, is the open problem.

## Reading

**Interpretation, not a theorem.**
- **For the program's composed topology.** Rings A and D share no contact, yet the last contact needs both their pasts at every
  lag. In the program's vocabulary this is an indirect loop-relative position across time, through two intermediate recurrences and
  three complete contacts, at these sizes. It creates no direct contact between A and D, and no coordinate, length, separation or
  metric.
- **The gate's other items.**
  - Recoding by constants changes nothing, by the affine reduction.
  - Transport fails for the uniform construction and is partial for the hybrid paths.
  - Restrictions are untested.

  So each contact passes the gate and the path composes, but the paths are not yet a native network under the gate's transport
  clause.
- **Why sizes matter (a heuristic).** In an affine path a contact binds a ring at every lag when its row of M^T meets the ring's
  first-row cells at every phase of its eventual cycle. Every native path found has a short cycle. Growing a ring usually lengthens
  the cycle to hundreds or thousands of lags, and then some phase misses a ring. Every contact feeds back into every ring, so even
  c1's persistence depends on the far end: growing one end ring breaks all three contacts in most larger versions.
- **A fixed row does not help by itself.** The 128 hybrid paths whose contacts' rows settle on fixed rows, parities the path
  conserves, survive one more cell on ring D at the same rate as the others (112 of 128), and one more cell on ring A or ring B not
  at all.
- **Inhomogeneous rings.** Counting ticket B's hybrid paths as native takes a law declared cell by cell as a native substrate (A36,
  added). The existence of native paths does not rest on it, since ticket A's rings are uniform.
- **The recurring family.** Again the affine one: rule 150, shifts and parity contacts.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| Native paths with one rule per ring (A) | the construction with end rings of 3 to 5 cells and middle rings of 5 to 7, every position with the contacts at least two apart, every one-sided c2 law, both shift directions: 11,600 paths (`stress_test.json`) | none native: 10,912 keep no contact, 240 keep one, 448 undecided within 200,000 lags |
| The same, one ring longer (A) | five rings, shift / 150 / 150 / 150 / shift on 3/5/5/5/3 cells, every position (2 or 3) and every one-sided law at the two inner contacts: 512 paths | none native: 416 keep no contact |
| The smallest path's knot (A) | the generic enumerator at lags 5 to 10, and knotlab check on the parity of the last contact's eventual support | pass: one knot meeting all four rings at each lag; knotlab confirms a knot |
| Hybrid native paths (B) | one more cell on ring A, ring B or ring D, each with its ring's rule (`periods.json`); one more hybrid-ring cell (ticket C) | partial: ring D keeps 928 of 1,120, rings A and B keep none; one more hybrid-ring cell keeps some variant native for 704 |

The existence claims of tickets A and B are for the declared sizes and stand. The stress test shows that they do not transport,
and every summary of them says so.

## Correction

`NATIVE-PATH-20261108-001` read its negative searches as a tension: a second middle ring must keep its own first row and carry the
first ring's influence, and "the additive rules keep the first row but cancel the influence". Ticket A shows rule 150 doing both,
and the same paths with rule 150 on their end rings fail at the end rings (`uniform_paths.json`). Logged in `docs/CORRECTIONS.md`
as not a block, with a correction section in that epic's decision note.

## Correction (2026-11-08, after PATH-GROWTH-20261108-001)

Logged in `docs/CORRECTIONS.md`.
- **Narrowing.** The answer's "with one rule per ring there is a single construction of 16 paths" holds for ticket A's two shapes.
  Native paths with one rule per ring also sit at 5/6/6/5, 4/7/7/5 and, with rule 150 on every ring, at end rings of 6 cells.
- **Not a block.** The heuristic under "Why sizes matter" holds for the construction's larger versions only. Persistent paths of
  other families keep short cycles at every size and still do not compose.

## Literature and provenance

- **Sources.**
  - Linear feedback shift registers: x³ + x + 1 is primitive over GF(2), of period 7 (Golomb, *Shift Register Sequences*, 1967).
  - Additive automata on rings (Martin, Odlyzko and Wolfram 1984).
  - Networks of intersecting Boolean automata cycles. Alcolei, Perrot and Sené characterise the asynchronous dynamics of xor-cycle
    chains and xor-flowers (arXiv:1510.05452, 2015), and Demongeot, Noual, Sené and coauthors study double-cycles.
- **Nearest known.** Xor-cycle chains are chains of cycles joined at shared automata that combine their inputs by XOR, close to
  this substrate. That work describes transition graphs under asynchronous updating, not whether a shared node's value needs both
  cycles' initial states at every lag.
- **Classification.**
  - **Tickets A, B and C.** New as far as found: native paths across time and their constructions.
  - **The end-ring mechanism.** Known-with-delta: elementary.
- **Where the question came from.** `NATIVE-PATH-20261108-001`'s directions, relayed by the coordinator.

## Workspace assumptions

- **Relied on.** A30 (two-time knots), A32 (binding), A34 (composition at every lag, here for a path's last contact).
- **Added.** A36: a law declared cell by cell is a native substrate.
- **Scope.** Linear rules, contact laws by their linear parts, the declared families and sizes.

## Ratio

Since the epic opened:
- **Substantive.** Three evidence families changed conclusions: A (the sweep, its characterisation and its stress test), B (the
  hybrid search) and C (its characterisation). One correction to an earlier reading.
- **Administrative.** This note, the closure and a renumbering of three backlog entries.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — native paths of four rings | **Status:** Successful | 16 with one rule per ring and 1,120 with hybrid middle rings, verified; the earlier tension does not hold |
| Local direction — paths across time | Continue | The paths are tied to their sizes, and transport is the gate's next item |
| Broader exploration — G5 with G1 | Known alternatives | Native separation and cycles of rings; the gate's restrictions; nonlinear paths; backlog B9 to B11 |
| Long-term goal — G5 Dynamics (question 4) | Capability gained | The first composed topology of three contacts across time exists, at particular sizes |

**Corrections:** one, not a block (NATIVE-PATH's diagnosis). **Goals:** a G5 checkpoint (capability gained). **Assumptions:** A36
added.

- **What the attempt leaves open.**
  - Transport: a native path that stays native as its rings grow, or as rings are added.
  - The gate's restrictions.
  - Separation and cycles of rings, the steps after paths.
- **The missing bridge to the program's composed topology.** Native paths that survive the admitted transports, so that a network
  of them is native rather than tied to one size.

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Native paths that survive growth (G5, with G1) | 3/3 — Major | 2/3 — Testable | Search families parametrised by size, each ring's rule and each law fixed while the rings grow together, for one native at every size from 3 to 9 cells per ring; and look for a certificate of every-lag binding that does not depend on ring sizes → a family native at every tested size, or evidence that every-lag binding in affine paths is tied to particular sizes, which would put A34 under challenge | Selected · not started |
| 2 | Native separation and cycles of rings (G5, with G1) | 3/3 — Major | 2/3 — Testable | Cut a found path's middle contact or ring and prove that no route remains; then search four rings in a cycle for contacts bound along both routes → native separation across time, or its obstruction | Alternative · deferred |
| 3 | The gate's restrictions for paths (G5) | 2/3 — Substantial | 2/3 — Testable | Restrict a found path to admitted subsystems and recheck every binding → which restrictions keep it native | Alternative · deferred |
| 4 | Nonlinear native paths (backlog B10) | 2/3 — Substantial | 1/3 — Stated | Parked | Backlog |

1. **Native paths that survive growth.**
   - **Payoff 3.** Transport is what separates a native network from a coincidence of sizes. A family native at every size would
     make composed topology across time robust, and a proof that none exists would answer the gate's transport clause negatively.
   - **Concreteness 2.** The row-sequence reduction decides each size exactly, and the families are small. The certificate is not yet
     known.
   - **Uncertainty.** Whether any family escapes the long cycles of larger rings.
2. **Native separation and cycles of rings.**
   - **Payoff 3.** Separation comes after paths in the program's order: adjacency, paths, separation, then distance. A cycle of rings
     is the first topology with two routes.
   - **Concreteness 2.** The cut is cheap to test on the found paths; the cycle search reuses the path code.
   - **Uncertainty.** Separation built on paths that do not transport may not survive the next size either.
3. **Restrictions.** The gate's remaining item; cheap on the found paths.
4. **Nonlinear native paths.** No method beyond search yet.

**Recommendation.** Continue with direction 1. If no family stays native at every tested size, record that every-lag binding in
affine paths is tied to particular sizes, reassess A34 against the intermittent reading, and take direction 2 on the found paths.
