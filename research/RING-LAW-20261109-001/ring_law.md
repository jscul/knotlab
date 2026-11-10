# Rings the law can see

Epic `RING-LAW-20261109-001` (program foundations), 2026-11-09 to 2026-11-10.

## The question

- **Where it comes from.** `REROUTE-20261109-001` found that at law-(12, 12) contacts every re-routing of a network is the same cellular
  automaton, so its rings are read as declared, assumption A45, and recorded the challenge as backlog B45: give contacts laws that read
  their two rings differently, and see whether persistence, binding and the plain reading survive. The coordinator selected B45 on
  2026-11-09.
- **The question.** Which contact laws make the rings native, and what do the tori and their line networks keep under them?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Which laws see the rings.** Of the 256 self-blind laws u(l, r) + v(l, r), exactly the 32 affine laws that read both arriving cells alike are blind to re-routing, (12, 12) among them; the other 224 see the routing. An affine law sees only by cutting a ring, so a law under which both rings pass and the routing is seen is nonlinear (128 laws). Under an affine law binding is needing. | proved | A |
| 2 | **On the tori, native rings do not bind.** On none of the nine tori (square, triangular, honeycomb; n = 4, 5, 6) does a law that sees the routing bind both rings at every lag read (A32); only the 12 blind affine laws bind. | computed (pre-registered, exact) | B |
| 3 | **On the square lines, 32 laws bind.** On the square line networks of n = 4 and 5 the same 32 seeing laws bind both rings to lag 6: one ring's table is the parity of its two neighbours, the other's one of the eight nonlinear tables. On the triangular and honeycomb lines none does. | computed (pre-registered, exact) | B |
| 4 | **The plain reading survives.** Under the eight symmetric nonlinear laws every contact of all 18 networks needs both its rings at every lag to 64, and every network reads its distance on time, tori included, where law (12, 12) is late. | computed (pre-registered, exact) | B |

## Answer

Rings can be made native: 224 of the 256 contact laws fix how each ring continues through a contact, and under the nonlinear ones the
tori read their distance plainly, on time, where the blind law (12, 12) was late. But on a torus that costs binding: no law that tells
the rings apart keeps both rings bound, while on the square line networks 32 such laws still bind to lag 6. A plane read plainly with
rings of its own is not a bound one.

## Reading

**Interpretation, not a theorem.**
- **Seeing a ring and holding it are different jobs.** A law that sees its rings treats their arriving cells differently, and on every
  torus read some assignment of the other cells then makes a contact independent of one of its rings within a few lags. Why the square
  line networks escape this for 32 laws, a parity on one ring and a nonlinear table on the other, is open (direction 2).

## Lag cutoffs and census-only claims

- **Lag cutoffs.** Binding of nonlinear laws read to lag 6, needing to lag 64; neither at every lag.
- **Census-only.** Conclusions 2 to 4 hold on the 18 networks read (binding on the line networks of n = 4 and 5 only). E001 was stopped as
  too slow with no result; E002 was killed for memory after 3,562 of 4,002 readings and finished by resume.py with the same code
  (RING-LAW-B2, RING-LAW-B3, signed off by the coordinator).

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| The 32 laws bind on square lines (3) | square 6 × 6 lines, to lag 6 (read to 5) | pass: all 32 bind to lag 6 |
| No seeing law binds on a torus (2) | square 7 × 7 torus, the 128 nonlinear passing laws and the 32 (read to 6) | pass: none of the 128 binds |
| Needing and on time under the eight nonlinear laws (4) | square 7 × 7 torus and lines (read to 6) | pass: every contact needs both rings to lag 64, none late (98 and 28 pairs per law) |

The script is `stress_test.py` beside this note, its output `stress_test.json`; registered before launch as RING-LAW-S1, it ran from
2026-11-10 05:23 to 09:13 UTC (3.8 hours, 6 workers, 5.3 GB peak) and passed. Folded in on 2026-11-10; the conclusions stand as
stated.

## Literature and provenance

- **Sources.** Chmutov's partial duality (for re-routing, via `REROUTE-20261109-001`); algebraic normal forms of Boolean functions;
  A31, A32 and A45 of the register.
- **Classification.** New as far as found, as readings of these networks.

## Workspace assumptions

- **Relied on.** A31 (the self-blind family), A32 (binding), A45 (rings as declared).
- **Changed.** A45 confirmed: (12, 12) is blind, so its ring-level readings are declarations; native rings need seeing laws, which on
  tori cost binding.

## Ratio

Since the epic opened:
- **Substantive.** One proof (A), one census (B, E002) after a stopped one (E001), one stress test.
- **Administrative.** The resume after the out-of-memory stop, this note and the closure.

## Pending the owner

- None new.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — rings the law can see | **Status:** Successful | Native rings exist; on tori they cost binding, on square lines 32 laws keep it to lag 6 |
| Local direction — native rings | Research directions | Binding past lag 6 on the square lines, and why only square |
| Broader exploration — G1 | Known alternatives | The reach line's open rows |
| Long-term goal — G1 Space from a law, with G5 | Obstruction learned | A plane read plainly with native rings is not bound on the tori read |

**Corrections:** none. **Goals:** a G1 checkpoint (obstruction learned, with G5); B45 taken. **Assumptions:** A45 confirmed.

- **What the attempt leaves open.** Binding of the 32 laws at every lag; tori larger than 6 × 6 and other lattices' lines.

**Next step:** Research directions — none selected, for the coordinator.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Do the 32 square-line laws bind at every lag? (G1) | 2/3 — Substantial | 3/3 — Ready | Read their binding on the square 4 × 4 and 5 × 5 lines to lag 12 with the census code, and look for an invariant (the parity ring's linear part) that holds at every lag → a proof of binding at every lag, or the lag where it fails | Alternative · deferred |
| 2 | Why the square lines and not the triangular or honeycomb ones? (G1) | 2/3 — Substantial | 2/3 — Testable | Compare how often two rings of each line network meet per period and where the 32 laws fail on the triangular lines → the meeting count that decides binding, or none | Alternative · deferred |

1. **Binding at every lag.** Payoff 2: native rings that stay bound would make ring-level readings native on the square lines.
   Concreteness 3: the census code reads it directly.
2. **Why square.** Payoff 2: it would say which geometry lets a law see its rings and hold them. Concreteness 2.

**Recommendation.** Research directions, none selected, for the coordinator.

## Final report as sent

B45 is closed and published: rings can be native, but on a torus that costs binding. Exactly 32 of the 256 self-blind contact laws are blind to how rings run through a contact, (12, 12) among them, so the other 224 make the rings the automaton's own (proved). Under the eight nonlinear laws, every torus and line network needs both rings to lag 64 and reads its distance on time, including the tori where (12, 12) was late. But no torus keeps both rings bound under a law that sees them. On the square line networks, 32 laws (a parity on one ring, a nonlinear table on the other) bind to lag 6. A45 is now confirmed: the earlier ring readings were declarations. The stress test one size past is running and registered as pending (RING-LAW-S1). One slip along the way: my A45 history line went in oldest-first, which failed one publication run for about a minute. It's fixed and published.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: rings the law can see | Successful | Native rings exist; on tori they cost binding, square lines keep it to lag 6 |
| Local direction: native rings | Research directions | Binding past lag 6, and why only the square lines |
| Broader exploration: G1 | Known alternatives | The reach line's open rows |
| Long-term goal: G5, with G1 | Obstruction learned | A torus read plainly with rings of its own is not bound |

**Next step:** Research directions, none selected.

| # | Direction | Payoff | Concreteness | First step → stop when |
| --- | --- | --- | --- | --- |
| 1 | Do the 32 square-line laws bind at every lag? | 2/3 | 3/3 | Read binding to lag 12 and look for an invariant → a proof at every lag, or the lag where it fails |
| 2 | Why the square lines and not the others? | 2/3 | 2/3 | Compare how rings meet per period and where the laws fail → the deciding count, or none |

**Corrections:** none. **Goals:** a G5/G1 checkpoint; B45 taken. **Assumptions:** A45 confirmed.
**Basket:** RING-LAW-20261109-001#1 (2/3, 3/3), B13 (2/3, 2/3), RING-LAW-20261109-001#2 (2/3, 2/3); none taken, since this thread moves to B114 at your go-ahead.
