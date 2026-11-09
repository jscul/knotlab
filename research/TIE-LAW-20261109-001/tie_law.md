# The first tie of shortest routes

Epic `TIE-LAW-20261109-001` (program foundations), 2026-11-09.

## The question

- **Where it comes from.** `PLAIN-TIME-20261108-001B` computed that in the contact graph of a regular tiling of type (m, f), m contacts
  per ring and f per face, the first contact reached by two shortest routes comes at τ = L − L/m − L/f + 1, L = lcm(m, f), on every
  cover it read (39 for the first late ring, 10 for the tie). The coordinator's argument gave the tie's mechanism: two routes round a
  disc, with k ring cells and j face cells inside, have equal length only if km = jf. Why no tie comes earlier was open (its direction 1);
  the coordinator assigned it to this thread on 2026-11-09.
- **The question.** Prove the tie law, stated in standard graph and GF(2) terms so that an outsider can check it. Stop with a proof of
  both bounds, or with the part proved and the gap stated.

## The law in standard terms

Let T be the regular tessellation {f, m} of the Euclidean or hyperbolic plane (f-gonal faces, m at each vertex, 1/m + 1/f ≤ 1/2), and D
its directed medial graph: one vertex per edge of T, one arc per corner (vertex, face) of T, from the corner's edge to the next edge about
its vertex, always turning the same way. Every vertex of D has two arcs in and two out; the arcs about a vertex form a directed m-cycle,
those about a face a directed f-cycle. The tie law: the least length of two different shortest routes with the same ends is
τ(m, f) = lcm(m, f) − lcm/m − lcm/f + 1. Over GF(2), with A the adjacency matrix of D: (A^d)[x, y] = 1 for every y at distance d < τ,
and some y at distance τ has (A^τ)[x, y] = 0.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **A Gauss–Bonnet count for two routes.** For two routes with common ends that meet nowhere else, the disc between them on the first one's left satisfies km = I + d_P, jf = I + d_Q and n = k + j − 2 − p_F − q_V; for equal lengths d = K(1 − 1/m − 1/f) + 1 − n with K = km = jf a common multiple of m and f. | proved | A |
| 2 | **One run per cell.** A shortest route runs along each cell of the disc on its side at most once. | proved | A |
| 3 | **Run bounds.** A shortest route goes at most ⌊m(f − 1)/f⌋ arcs about one ring and ⌊f(m − 1)/m⌋ about one face; both are attained. | proved; attainment computed | A |
| 4 | **No tie before τ.** On every regular tessellation, Euclidean or hyperbolic, two different shortest routes with the same ends have length at least τ: every contact within τ − 1 has a single shortest route. | proved | A |
| 5 | **The tie at τ when m = f.** Every closed route has length at least min(m, f), so when m = f the first tie is exactly at τ = m − 1, the long way round a ring against the long way round a face. | proved | A |
| 6 | **The tie at τ elsewhere.** The first tie is at τ, two contacts of two routes each, on 42 hyperbolic covers (two primes each) and on four larger covers of the stress test (τ up to 24); every pair of shortest routes read is thin, at length c(τ − 1) + 1. | computed | A, stress test |

## Answer

The half that was open is proved: no tie comes before τ, on every regular tessellation. The proof counts the disc between two tied
routes. Its corners and arcs give d = K(1 − 1/m − 1/f) + 1 − n, where K = km = jf is a common multiple of m and f and n the number of
vertices inside. Two facts about shortest routes, that one never runs along the same cell twice and that its runs are short, show that
n counts the cells the routes never touch. Such a cell needs a ring of neighbours all inside the disc, which a disc of size L cannot hold
and a larger disc pays for in length. So a tie needs K ≥ L and has length at least τ. That a tie does come at τ is proved when m = f and
computed everywhere else read.

## Reading

**Interpretation, not a theorem.**
- **Thin bigons.** The first tie's two routes enclose a single row of cells, a caterpillar of rings along one route and faces along
  the other, with no vertex inside (proved for the discs of size L; every pair read is thin): the directed version of the thin
  bigons of small-cancellation theory.
- **Why lcm.** The disc's ring corners and face corners must balance, km = jf, so the smallest tie spans L corners of each kind; that is
  where the plain first need first hides a ring (`PLAIN-TIME-20261108-001B`).
- **Nothing here is a length beyond counted route length**, the program's native magnitude (A40).

## Lag cutoffs and census-only claims

- **No lag cutoff.** Route counts are exact on balls read in PSL(2, p).
- **Census-only.** Conclusion 6 (attainment for m ≠ f), and attainment of the run bounds.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| Attainment at τ (42 covers, balls to two million contacts) | (8, 12), (6, 10), (5, 7), (4, 9), (6, 7), balls to τ of up to 30 million | pass where read: the first tie at τ = 20, 23, 24 and 24 on the first four; (6, 7), τ = 30, was read only to radius 25 under the cap, with no tie there, as Theorem 2 requires (TIE-LAW-S1, `docs/LONG_RUNNING.md`) |
| No tie before τ | proved for every type; check 1 runs the case analysis for every type with m, f ≤ 40 | pass |

The script is `stress_test.py` beside this note, with `stress_test.json` and `stress_test_log.txt`.

## Literature and provenance

- **Sources.** Combinatorial Gauss–Bonnet for 4-valent plane complexes; thin bigons in C(p)–T(q) small-cancellation complexes (Lyndon
  and Schupp; Strebel); triangle groups and their geodesics. The routes here are directed and the cells are directed cycles, so none of
  these results applies as it stands.
- **The coordinator's sandbox (relayed 2026-11-08 to `PLAIN-TIME-20261108-001`).** The tie's mechanism, km = jf ≥ L for a tie; it is
  the first relation of Theorem 1, which adds the length formula and n.
- **Classification.** New as far as found for the question asked.

## Workspace assumptions

- **Relied on.** A40 (counted length is native), A41 (distance across time is read through freezes), as `PLAIN-TIME-20261108-001`.
- **Added.** None.
- **Scope.** Regular tessellations given, not grown; the covers read in PSL(2, p).

## Ratio

Since the epic opened:
- **Substantive.** Ticket A (three theorems and two lemmas, five checks) and the stress test.
- **Administrative.** This note and the closure.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the tie law | **Status:** Partially successful | The open half is proved for every tiling; attainment proved for m = f, computed elsewhere |
| Local direction — the plain first need | Continue | Attainment for m ≠ f, and the ring-level law (τ + 1 and τ + 2), are concrete next steps |
| Broader exploration — G5 with G1 | Known alternatives | The full-reach collapse (selected next), backlog B22 to B31 |
| Long-term goal — G5 Dynamics (question 4) | Capability gained | The horizon of distance without freezing is now a theorem from below on every tiling |

**Corrections:** none. **Goals:** a G5 checkpoint (capability gained). **Assumptions:** none added.

- **What the attempt leaves open.** That the caterpillar's two routes are shortest when m ≠ f; and the first late ring at τ + 1 or τ + 2.

**Next step:** Continue — selected: #2, the full-reach collapse, at the coordinator's instruction.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Attainment of the tie when m ≠ f | 1/3 — Incremental | 2/3 — Testable | Show the caterpillar's routes minus their last arc are shortest, by induction along the routes → a proof, or a cover where they are not | Alternative · deferred |
| 2 | The collapse at every power of two (`FULL-REACH-PROOF-20261108-001`'s #1) | 2/3 — Substantial | 2/3 — Testable | The Smith form of the cut-line matrix at 4, 8, 16 → a proof, or a power of two where it fails | Selected · started |
| 3 | The first late ring at τ + 1 or τ + 2 | 1/3 — Incremental | 2/3 — Testable | The rings next to a thin tie's endpoints → why the extra step for triangular faces | Alternative · deferred |

1. **Attainment.** Payoff 1: it completes a law whose open half is now proved; Concreteness 2: if the two routes minus their last arcs
   are shortest, the tie follows at once, and the induction needs a distance bound along the route.
2. **The collapse.** Payoff 2: it would prove why powers of two fail full reach; Concreteness 2: the matrix is explicit. Selected by the
   coordinator on 2026-11-09 as the next step after this epic.
3. **The ring law.** Payoff 1: a sharpening; Concreteness 2: thin ties give the local picture.

**Recommendation.** Continue with the full-reach collapse (#2).

## Final report as sent

Sent to the owner on 2026-11-09 at 21:10 UTC and copied here verbatim.

The tie law's open half is now proved, and the epic is published. On every regular tiling, flat or curved, no contact is reached by two shortest routes before distance τ = lcm(m,f) − lcm/m − lcm/f + 1. So the plain first need reads every closer contact on time. The proof counts the disc between two tied routes. A shortest route runs along each cell beside it only once, and never for too long. Together those force a tie to span at least lcm(m,f) corners of each kind. That a tie does come at τ is proved when m = f. For other tilings it's computed: on 42 covers, plus 4 larger ones in the stress test.

| Scope | Verdict | Why |
|---|---|---|
| This attempt: the tie law | **Status:** Partially successful | No tie before τ proved on every tiling; the tie at τ proved for m = f, computed elsewhere |
| Local direction: the plain first need | Continue | Attainment for m ≠ f, and the law for rings (τ+1, τ+2) |
| Broader exploration: G5 with G1 | Known alternatives | The full-reach collapse (next), backlog B22–B31 |
| Long-term goal: G5 Dynamics | Capability gained | The horizon of distance without freezing is now a theorem from below |

**Next step:** Continue, selected #2 (the coordinator's go-ahead).

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
|---|---|---|---|---|---|
| 1 | The tie at τ when m ≠ f | 1/3 | 2/3 | Show both routes minus their last arc are shortest → a proof, or a cover where they aren't | Alternative · deferred |
| 2 | Full-reach collapse at every power of two | 2/3 | 2/3 | Smith form of the cut-line matrix at 4, 8, 16 → a proof, or a power of two where it fails | Selected · started |
| 3 | The first late ring at τ+1 or τ+2 | 1/3 | 2/3 | The rings beside a thin tie's ends → why triangular faces add a step | Alternative · deferred |

**Corrections:** none. **Goals:** G5 checkpoint (capability gained). **Assumptions:** none added. Both stress tests are folded in. The tie-law one (TIE-LAW-S1) needs the coordinator's sign-off; FULL-REACH-PROOF-S1 already has it. Commits 3982d13c5, 4f286a296 and aa7ab1c7a. I'm starting the Smith-form work now.
