# Knots between processes: two rings joined by one contact

Epic `PROCESS-CONTACT-20261108-001` (program foundations), 2026-11-08.

## The question

- **Where it comes from.** It is the selected next step of `TIME-KNOTS-20261107-001`, which read one process as its space-time law:
  its knots with its first row are its minimal decisive sets. The program's first emergence is a knot between two loops through
  one contact. With loops as processes, the question is which contacts bind two changing loops, so that the contact's future needs
  both loops' pasts. The step started at once under the standing mandate.
- **Two models.**
  - **Listening.** Two rings, each running an elementary cellular automaton, and one contact cell c that reads one cell of each
    ring (and possibly itself) but feeds nothing back.
  - **Shared.** The contact is a cell of both rings, as the contact gate's shared identity asks, so each ring feeds the other
    through it. A non-contact cell updates by its ring's rule, and the contact combines the two rings' proposals by a two-input
    law.
- **The test.** The contact *binds both rings at lag T* when every minimally decisive set of c(T) over the joint first row meets
  both rings. It *persists* when it binds at every lag.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Binding is two-sided essentiality and loss under erasure, read across time.** The contact binds both rings exactly when neither ring's first row with the contact's own first value decides c(T), and exactly when forgetting either ring leaves c(T) free. A binding contact has knots through c(T) and no ties. | proved; computed on 15,360 maps against the generic enumerator | A |
| 2 | **A listening contact sees each ring only through its contact histories.** Two pairs of rings that can show the same histories at their contact cells are bound by the same laws. | proved; computed on 135,168 maps | A |
| 3 | **A listening contact binds exactly when it is a parity.** A memoryless contact binds both rings exactly when it is XOR or XNOR of two contact cells that still depend on their first rows. Its knots join one decisive set of each ring, so a knot between processes is one knot or tie of each ring joined through the contact. With memory, binding from the first step still needs one of the four parities, though binding can begin later through what the rings cannot show (38 non-parity laws at 3 + 4 cells, 40 at 4 + 5). | proved; computed, exact at every lag | A |
| 4 | **Linear rings keep the binding unless they forget.** Between linear or affine rings the parity contact binds at every lag exactly when neither ring polynomial is nilpotent modulo X^m − 1. That fails only for rules 0 and 255 on every ring, and for rules 60, 102 and 90 and their negations on rings of 2^k cells, after 2^k, 2^k and 2^(k−1) steps. | proved (the nilpotency is known); computed | A |
| 5 | **Sharing the contact costs persistence.** Of 128,128 shared configurations, each exact at every lag, 44 bind both rings at every lag, all with a parity combiner. Sharing breaks 13,068 of the 13,104 parity bindings that a listening contact keeps forever, and rescues 8: a rule-60 ring of 4 cells forgets alone but keeps binding when it shares the contact. At lag 1 the contact binds exactly when the combiner is a parity and neither rule is canalizing at its centre. Otherwise the contact's own first value fixes a ring's proposal. Binding usually decays, most often after one step, and 53 non-parity configurations bind from some lag on. | exploratory experiment; one size past, the same pattern | B |

## Answer

- **A listening contact.** It binds two processes, two-sided and lost when either is erased, exactly when it is a parity. It
  persists exactly while both processes remember their first rows at the contact. This is the static first-emergence knot read
  across time: one knot or tie of each process, joined through a parity into one knot.
- **A shared contact.** A contact that is part of both processes, as shared identity asks, feeds each process the other's past and
  its own. At lag 1, when a rule is canalizing at its centre, the contact's own past alone settles a proposal. At later lags one
  ring's side usually comes to steer the contact. Binding at every lag remains, always with a parity combiner, in 44 of 128,128
  configurations, at sizes that vary by rule.

## Reading

**Interpretation, not a theorem.**
- **For the contact gate.** Read across time the gate splits. A listening contact passes two-sided essentiality, loss under erasure
  and persistence (while both rings remember), but it is part of neither loop. A shared contact is part of both loops, but it rarely
  persists at these sizes. Few contacts pass every item together: the 44 of the census and the 55 one size past.
- **An XOR of fixed values is a classifier.** The doctrine says so because its inputs are not open. A ring that forgets fixes its
  contact value, and then the parity contact stops binding, exactly where ticket A's Theorem 5 says linear rings forget.
- **Persistence grows with the rings.** At rings of one rule each, parity configurations persist in 2, 13, 4, 13 and 21 of 176 at
  3 + 4, 4 + 4, 4 + 5, 5 + 6 and 6 + 7 cells. Three more at 6 + 7 bound at every one of 4,096 lags without their maps repeating.
  Whether shared binding becomes typical on large rings is open.
- **In line with double-cycles.** Networks of two Boolean automata cycles that share one automaton have exponentially fewer
  attractors than isolated cycles (Demongeot, Melliti, Noual, Regnault and Sené). That is the same direction as the census: a shared
  node makes the joint dynamics forget more of where it started.

## Stress test

One size past each computed claim (`stress_test.py` here, with `ticket_a.json`, `larger.json` and `recheck.json`). Each reuses the
tickets' own code.

| Claim | One size past | Result |
| --- | --- | --- |
| Theorem 3 on rings alike to 5 + 5 cells, T ≤ 8 (A) | 6 + 6 cells, T ≤ 10 | pass: 14,080 maps, no mismatch |
| With memory: the four lag-1 laws; 38 later-binding laws at 3 + 4 (A) | 4 + 5 cells, exact at every lag | pass: the same four laws; 40 later-binding laws |
| The census at four sizes alike and 3 + 4 mixed (B) | 6 + 7 alike (16 combiners), 4 + 5 mixed (8 combiners): 62,656 configurations | the lag-1 criterion holds on all; sharing breaks 13,565 of 13,618 listening-persistent bindings and rescues 2; 55 bind at every lag; 41 non-parity bind from some lag on; 48 undecided within 4,096 lags |
| The census rows (B) | recheck by direct simulation and minimally decisive sets, 500 rows, lags ≤ 6 | pass: 500 of 500 |

## Literature and provenance

- **Sources.**
  - **Canalizing functions** (Kauffman, 1969). Every two-input function except XOR and XNOR is canalizing.
  - **Composition of certificates** of Boolean functions, classical (for example Tal, 2013).
  - **Additive automata on rings.** Martin, Odlyzko and Wolfram (1984) treat them through polynomials modulo X^m − 1, including
    the nilpotency of rule 90 on rings of 2^k cells.
  - **Boolean automata double-cycles.** Two cycles of Boolean automata that share one automaton. Demongeot, Noual and Sené studied
    their dynamics and attractors, and Melliti, Noual, Regnault, Sené and Sobieraj characterized the asynchronous case
    (arXiv 1310.5747). A 2022 chapter by Demongeot, Melliti, Noual, Regnault and Sené (arXiv 2204.10686) reviews them: double-cycles
    have exponentially fewer attractors than isolated cycles.
- **Classification.**
  - **Ticket A.** Known-with-delta. The delta is the reading of the contact gate across time: binding as two-sided essentiality
    and loss under erasure, parity as its exact condition, and nilpotency as its end.
  - **Ticket B.** New as far as found: a census of shared contacts between elementary-automaton rings by binding and persistence.
    The double-cycle literature studies attractors of cycles whose arcs copy or negate, a different model and observable, with a
    finding in the same direction.
- **Where the ideas came from.** The question follows the owner's question 4 and the program's first emergence.

## Workspace assumptions

- **Relied on.** A3 (verdicts from allowed states), A6 (erasure is forgetting), A30 (a process's memory is read from its two-time
  knots).
- **Taken by default.**
  - **A31.** A shared contact combines its two rings' proposals by a two-input law. The contact laws that read their four ring
    neighbours without the rings' rules are not covered.
  - **A32.** Two-sided essentiality across time means that every minimally decisive set of the contact's future meets both rings.
    Theorem 1 shows that this is also loss under erasure.

## Ratio

Since the epic opened:
- **Substantive.** Two evidence families changed conclusions: A (a proof) and B (an exploratory census). The stress test also
  counts, since it found that persistence grows with ring size.
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
| This attempt — which contacts bind two processes | **Status:** Successful | Listening: exactly the parities, while both rings remember; shared: rarely persistent |
| Local direction — contacts between processes | Continue | Which shared contacts persist is open, and persistence grows with ring size |
| Broader exploration — G5 lines | Known alternatives | Shared contacts that do not read themselves; the whole-law reading (A30) |
| Long-term goal — G5 Dynamics (question 4) | Capability gained | The contact gate reads across time, and shared identity costs persistence |

**Corrections:** none. **Goals:** a G5 checkpoint (capability gained). **Assumptions:** A31 and A32 added.

- **What the attempt leaves open.**
  - Whether shared binding becomes typical as the rings grow.
  - Whether a shared contact that does not feed its own value back persists more often.
  - Which knots the whole space-time law has between the two rings (A30's alternative).
- **The missing bridge to the program's first emergence.** A contact that is part of both loops and still binds them at every lag,
  for every size of a family of rings.

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Shared contacts that do not read themselves (G5, A31) | 2/3 — Substantial | 3/3 — Ready | Contact laws u(a_{m−1}, a_1) + v(b_{n−1}, b_1) on the census's rings, exact at every lag → whether removing the contact's own past restores persistence | Selected · not started |
| 2 | Shared binding as rings grow (G5) | 2/3 — Substantial | 3/3 — Ready | The census alike at 7 + 8 and 8 + 9 cells with a lag cap → the trend of persistence with size | Alternative · deferred |
| 3 | The whole-law reading for two rings (A30) | 2/3 — Substantial | 2/3 — Testable | Knots of the shared space-time law joining both rings in windows → knots that the two-time reading misses | Alternative · deferred |
| 4 | Learning a rule from its knots (G16) | 2/3 — Substantial | 1/3 — Stated | Carried from `TIME-KNOTS-20261107-001` | Alternative · deferred |

1. **Shared contacts that do not read themselves.**
   - **Payoff 2.** At lag 1 the shared contact fails exactly when its own past fixes a proposal. A contact whose update ignores its
     own value but whose rings still read it is part of both loops. If such contacts persist, shared identity and persistence are
     compatible, and the gate passes across time.
   - **Concreteness 3.** The census code runs with a new contact family.
   - **Uncertainty.** Later failures come from one ring's side steering the contact, which the contact's own past may not cause.
2. **Shared binding as rings grow.**
   - **Payoff 2.** It would tell whether the census's rarity is a small-size effect.
   - **Concreteness 3.** Ready, with a lag cap for maps that do not repeat.
3. **The whole-law reading.**
   - **Payoff 2.** It would show whether the shared rings are knotted to each other through the contact's history even where c(T)
     does not bind.
   - **Concreteness 2.** Window computations, as in the correction of 2026-11-08.
4. **Learning a rule from its knots.** Carried, unchanged.

## Final report as sent

Sent to the owner on 2026-11-08 at 08:22 UTC and copied here verbatim.

Knots between processes is closed and published. I joined two rings (each a cellular automaton) by one contact cell. A contact that only listens to both rings binds them exactly when it is a parity (XOR) of two ring cells that still remember their start. "Binds" means every set of past cells deciding it touches both rings, which turns out to be the same as being lost when either ring is erased. The binding lasts as long as both rings remember. A contact that is a cell of both rings, as the gate's shared identity asks, feeds them back, and then only 44 of 128,128 configurations stay bound at every lag. [Decision note](https://github.com/jscul/knotlab/blob/main/research/PROCESS-CONTACT-20261108-001/process_contact.md)

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt | Successful | Listening contacts: exactly the parities; shared contacts: rarely persistent |
| Local direction | Continue | Which shared contacts persist is open; persistence grows with ring size |
| G5 Dynamics (question 4) | Capability gained | The contact gate reads across time, and shared identity costs persistence |

**Next step:** Continue, with #1 started.

| # | Direction | Payoff | Concreteness | Status |
| --- | --- | --- | --- | --- |
| 1 | Shared contacts that don't read their own value | 2/3 | 3/3 | Started |
| 2 | Shared binding as rings grow | 2/3 | 3/3 | Folded into #1 |
| 3 | Whole-law knots between the rings (A30) | 2/3 | 2/3 | Deferred |
| 4 | Learning a rule from its knots (G16) | 2/3 | 1/3 | Deferred |

**Corrections:** none. The nearest prior work is Boolean automata "double-cycles", two cycles sharing one node, which also lose dynamical variety. It is cited.
**Goals:** a G5 checkpoint.
**Assumptions:** A31 added (a shared contact combines its two rings' proposals), now under challenge by #1. A32 added (two-sided essentiality across time means binding).
