# Layers through a naming knot

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): a knot space is a drawn knot pattern. Results are unchanged;
the earlier text is in git history.

Epic `NAME-LAYERS-20261110-001` (direction `NEST-ATOMS-20261110-001`#4, first raised as `RESIGN-STEER-20261107-001`#3; G15; program
learning), 2026-11-10, at the coordinator's go-ahead. Pre-registered in [preregistration.md](preregistration.md), frozen in commit
`6901b52a8` before any run. Proof family: `proofs/NAME-LAYERS-20261110-001A/`.

## The answer

Two readings of layers. A three-edge cut and a parity name each carry what the other cannot.

- **Proved by hand (claim D).** Through a cut, a lower level's contradiction becomes an upper-level constraint (the replaced line), so a
  point crosses levels: lower-level learning creates or removes the upper level's forced dissonance. Through a name it cannot: the lower
  level keeps its own unsatisfiable lines, the name offers nothing, and each level's forced dissonance stays at its level.
- **Computed.** On seven lower-level spaces and two frozen namings, the cut offered the line in every unsatisfiable class and the name
  offered nothing there (D and N1 held). My prediction that names carry nothing in satisfiable classes failed: they carry correlations that
  change with the lower level's class, in 41 of 69 readings, from a frozen pattern to a single excluded pattern.
- **So** the cut is a channel for contradictions and conjunctions (AND of class bits, `COMPOSITE-FN-20261110-001`), and the name is a
  channel for state correlations, including clauses, which no cut can offer because every knot gadget's relation is closed under
  complement.

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| D: a cut lifts a contradiction to a constraint; a name cannot carry it, and each level keeps its own | proved by hand |
| R_C and R_N in every class of the frozen spaces | exhaustive computation per class |
| Names carry class-dependent correlations, clauses included | computed (the pattern lists read post hoc) |

## Against the pre-registration

D and N1 held; N2 failed (names do carry correlations). The frozen naming rule left four of the seven spaces undefined for at least one
naming (too few points, or no free point off the next one's lines); no substitute was chosen. As the stop rule says, the epic records what
names carry and stops; other namings, other spaces and learning dynamics across names are not run.

## What it changes

- **For the owner's layers.** There are two ways for one level to speak to the next, and they say different things: a cut says whether
  everything inside holds together (one bit, conjunctive, able to carry a contradiction up), and a name says how states inside are
  correlated (any relation, unable to carry a contradiction). A network that uses both is the next thing to ask about.
- **For B109.** Composites compute only monotone functions, but names offer non-monotone relations such as single clauses, so mixed
  networks are not bound by that limit.

## Assumptions

Relied on: A20, A21, A46, A47, A49, A50, A52. None added or changed.

## Corrections

None.

## In the owner's words

Patterns can talk to the patterns above them in two ways. Sealed off behind three sides, a pattern tells the level above only whether
everything inside holds, and a contradiction inside becomes a rule outside. Named by parity, a pattern tells the level above how its parts
line up, and that can be any rule at all, but a contradiction inside stays inside.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — layers through a naming knot | **Status:** Successful | two readings: cuts carry contradictions and conjunctions, names carry correlations and clauses |
| Local direction — the layered memory | Practically complete for this phase | its channels are now both characterized |
| Broader exploration — learning program | New questions | mixed layers, native writing, inputs and outputs |
| Long-term goal — G15 Learning: a point in a learned knot pattern | Capability gained | the layer question has an answer: two channels |

**Next step:** Research directions — selected: #1 (for the coordinator to weigh against other lines)

The learning line has only incremental work left in this phase (B98, B105, B113, B115, B117). Three proposals for a next phase, new
questions the proved layered memory makes askable:

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A learned network that computes (next phase) | 3/3 — Breakthrough | 1/3 — Exploratory | combine cuts (AND of stored bits) with names (clauses on states) in one small network and ask which Boolean functions of the stored bits its top level can read → a complete basis from knots alone, or the class it is stuck in | Selected · awaiting go-ahead |
| 2 | Native writing (next phase) | 2/3 — Substantial | 2/3 — Testable | replace the targeted search, which is told the target configuration, by a learner that sees only its own dissonance and the address it is asked for, as `NATIVE-TARGET-20261110-001` did for resolutions → addresses written natively, or a reason they need an outside map | Alternative · deferred |
| 3 | Inputs and outputs (next phase) | 2/3 — Substantial | 1/3 — Exploratory | give the outer host input points held by the world and read the composites' roles as outputs; ask whether learning driven by examples writes a chosen input-output map → learning from examples in a drawn knot pattern (G16), or not | Alternative · deferred |
| 4 | Is every host critical (B115) | 1/3 — Incremental | 2/3 — Testable | as recorded | Alternative · deferred |
| 5 | A writing search that reads roles (B113) | 1/3 — Incremental | 3/3 — Ready | as recorded | Alternative · deferred |

- **#1** speaks to the owner's "it's like a computer": with cuts alone the layers only conjoin; names add clauses, and the question is
  whether together they reach every function. If it is not taken now it goes to the goals doc as a sub-goal.
- **#2** removes the last outside input from the learning picture.

**Corrections:** none. **Goals:** G15 checkpoint (capability gained); `NEST-ATOMS-20261110-001`#4 taken; next-phase proposals added (one
3/3 sub-goal, two backlog entries). **Assumptions:** none new or changed.
**Basket:** the learning line's basket is empty at payoff 2 or more once this epic takes its only item; the proposals above are new.

## Final report as sent

Sent to the owner in the project thread on 2026-11-10 (06:04 UTC), after the owner rested the project for the night: the answer (two
readings of layers), claim D, the census with N2's failure and the undefined namings, both tables above with the next-phase proposals
(sub-goal B118 selected, B119, B120) for the owner and the coordinator to weigh tomorrow, that no long-running check is pending, the
Corrections, Goals and Assumptions lines, and the Basket line.
