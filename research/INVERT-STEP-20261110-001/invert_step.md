# Growth on an invertible substrate

Epic `INVERT-STEP-20261110-001` (program foundations), 2026-11-10.

## The question

- **Where it comes from.** Backlog B39. A band inserted while a network of rule-60 rings runs breaks most knots across time of the
  rings it reaches (`GROW-RUN-20261109-001`), and reading from the insertion row does not rescue them, because no row after the first
  is open (`REBASE-KNOTS-20261109-001`). On a substrate with an invertible step every row would be open. The coordinator gave B39 the
  go-ahead on 2026-11-10, after `GROW-STOP-20261110-001`.
- **The question.** Is there a ring rule and contact law with an invertible step and persistent contacts, on which growth while
  running could be read natively? Is the lapse of knots rule 60's forgetting, or growth itself?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Persistence needs forgetting.** On a finite network under any deterministic law, an injective step has finite order p, and at every lag kp every contact is its own first value, which neither ring decides: no contact persists. | proved | A |
| 2 | **Only beginnings are open, everywhere.** In any finite network with a persistent contact no row after the first is open, whatever the rule and contact law. | proved | A |
| 3 | **No such substrate.** Of 256 linear substrates (8 ring rules, 32 contact laws), first and second order, on five tubes, every invertible one fails by lag 25 (first order) or 336 (second order); the 32 to 52 per tube that persist all forget. | checked; the persistent ones computed | A |
| 4 | **No conflict with `DOUBLE-BALANCE-20261109-001A`.** Its invertible map is a ring's own cells' evolution while every contact is reborn, not the network's step; the step there is rule 60's, which forgets. | proved; checked | A |

## Answer

No finite substrate has both. An invertible step permutes the finite set of states, so it returns every state to itself, and at that
lag each contact holds only its own first value, bound to neither ring. A contact can keep its knots across time only if the law loses
information, and wherever a contact persists, every row after the first has lost some freedom, so only beginnings are open. The lapse
of knots under growth while running is therefore not a defect of rule 60 that another substrate would remove: the forgetting that
breaks them is what any persistent contact on a finite network needs. Growth keeps knots by giving the network new beginnings, as the
doubling law does, not by reading a later row.

## Reading

**Interpretation, not a theorem.**
- **An arrow from persistence.** A finite world whose contacts keep their knots across time has an irreversible law: persistence of
  binding singles out a direction of the process, the one in which information is lost. This is a statement about the program's
  logic, not about physics.
- **The two invertibilities.** Inside a ring, invertibility is what lets an isolated ring carry its born cells to its contacts intact
  (the transfer lemma); across the whole network, it is what the contacts cannot have. Doubling every lag has both: each ring's own
  cells evolve invertibly, and each contact's first value is discarded at its rebirth.
- **The forgetting can be small.** A listening contact between rings with invertible rules loses only its own first value and
  persists; the shared contacts read here lose at least two dimensions.

## Lag cutoffs and census-only claims

- **The theorem has no cutoff.** Check 3's persistence is read through a full cycle of every state; nothing is undecided.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| No invertible substrate persists (1, 3) | 5 × 4 at g = 2 and 3 × 4 at g = 3, beside the three census tubes | pass (checks 1 and 2) |

## Literature and provenance

- **Sources.** A permutation of a finite set has finite order; on finite configurations injective and surjective agree, as in the
  Garden-of-Eden theorem (Moore 1962; Myhill 1963); reversible and second-order cellular automata (Fredkin; Toffoli and Margolus 1990).
- **Classification.** Known-with-delta: the mathematics is elementary; the delta is that it settles B39 for every finite substrate
  and turns `REBASE-KNOTS-20261109-001`'s "only beginnings are open" into a theorem for every rule and law.

## Workspace assumptions

- **Relied on.** A30 (two-time knots from the first row), A32 (binding; the contact's first value belongs to neither ring), A45.
- **Added.** None.

## Ratio

- **Substantive.** One proof (A) with five checks. **Administrative.** This note and the closure.

## Pending the owner

- Nothing new.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — an invertible substrate | **Status:** Successful | Proved that none exists on a finite network: persistence needs forgetting |
| Local direction — growth while running | Research directions | The lapse cannot be removed by changing substrate; growth keeps knots by new beginnings |
| Broader exploration — G1 with G5 | Known alternatives | The proof pair B55 and B64; shaped growth that stops (B65); a reversible substrate that never stops growing |
| Long-term goal — G5 Dynamics (question 4) | Obstruction learned | A process keeps its contacts' knots across time only if its law forgets |

**Corrections:** none. **Goals:** a G1 and G5 checkpoint (obstruction learned), B39 marked taken, backlog B66 added. **Assumptions:**
none.

**Next step:** Research directions.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Why odd spacings keep balance (B55) | 2/3 — Substantial | 2/3 — Testable | As recorded | Alternative · deferred |
| 2 | Why crossing breaks balance (B64) | 2/3 — Substantial | 2/3 — Testable | As recorded | Alternative · deferred |
| 3 | Shaped growth that stops (B65) | 2/3 — Substantial | 2/3 — Testable | As recorded | Alternative · deferred |
| 4 | A reversible substrate that never stops growing (B66) | 2/3 — Substantial | 2/3 — Testable | Run the doubling law on second-order rule 60, which the theorem leaves open because the network is never fixed, and read binding while it grows → contacts bound at every lag while growth lasts, or the lag where binding fails | Alternative · deferred |

1. **B55.** Payoff 2: half of a theorem that would make the exclusion between knots and distance while growing exact. Concreteness 2.
2. **B64.** The other half. Payoff 2, Concreteness 2.
3. **B65.** Payoff 2: growth that chooses a shape, then reads it. Concreteness 2: the GROW-STOP check extends to partial doubling.
4. **B66.** Payoff 2: the mirror of `GROW-STOP-20261110-001`, knots kept only while growing. Concreteness 2: second-order doubling
   has to be written.

**Recommendation.** Research directions: #1 and #2 together, as the proof pair for the exclusion, since growth then reading is now
the positive result and the exclusion is the open half.
