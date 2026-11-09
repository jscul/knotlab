# Large networks persistent without flips

Epic `REROUTE-20261109-001` (program foundations), 2026-11-09.

## The question

- **Where it comes from.** `FLIP-RULE-20261109-001` found that a contact can persist without a flip, an automorphism of the map fixing
  it and exchanging its rings, on small maps, and read the smallest non-degenerate example, six contacts on genus 2, as parity that
  comes out even with no symmetry. Backlog B42 asked whether large networks keep every contact persistent that way and whether any reads
  its distance plainly as a plane; B43 asked why the parity comes out even. The coordinator selected B42 on 2026-11-09, to be opened
  with B43 as a short bounded step.
- **The question.** What pairs the closed walks of the six-contact example, if anything? Are there growing, non-degenerate networks
  whose every contact persists with few or no flips, and does any of them read its distance plainly, as a line or as a plane?

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The six-contact example is paired by doubled pairs.** Two of its contacts send both their darts to one next contact; every closed walk at the example's contact passes one, and exchanging the dart there pairs the walks. | exact reading | A |
| 2 | **Two pairings and a criterion.** Doubled pairs and automorphisms of the contact graph that exchange a contact's arcs make it persist; and a contact persists exactly when deleting it keeps det(I + tN) over GF(2), N the contact graph mod 2: the cycle families through it are even in number at every size. | proved | A |
| 3 | **Pairings explain everything to six contacts, and not beyond.** On every non-degenerate map of up to six contacts each persistent contact that sends and hears has a flip, a doubled pair or a contact-graph flip; from seven contacts most have none of them (5,438 of 8,992 sampled at seven). | computed | A |
| 4 | **Re-routing keeps persistence.** Exchanging, at any set of contacts, which ring each arriving ring continues on (Chmutov's partial duality) keeps every arc of the contact graph, so every contact's persistence; the maps with a given contact graph are exactly its 2^E re-routings. At law-(12, 12) contacts the cellular automaton itself is unchanged. | proved; the automaton checked cell by cell | B |
| 5 | **Large networks persistent without flips are generic.** Every random re-routing of the square, triangular and honeycomb tori read (60, n = 6 to 16) is non-degenerate, keeps every contact persistent and has no flip at any contact, with genus 15 to 189. | exploratory census, pre-registered | C |
| 6 | **Lines read their distance plainly.** Re-routing a torus at one direction class (two on the honeycomb) turns its rings into 2n lines, whose ring graph is a cycle; every contact persists and every ring has a closest contact reached by exactly one shortest route, at every size. | proved (square), computed to n = 28 (triangular, honeycomb) | B, stress test |
| 7 | **Small rings never do.** On the square contact graph a ring inside a box of side 2^k − 2 is late on any torus with no lattice vector shorter than 2^(k+3), so an on-time re-routing of the n × n torus (n ≥ 64) has at most 64n rings, each of at least n/8 − 4 contacts. Every random re-routing read is late, and every ring of at most 12 contacts on tori of n ≥ 12 is late for some target, on all three lattices. | proved (square); census | B, C |

## Answer

The six-contact example is paired, not arithmetic: two doubled pairs cancel its walks. Up to six contacts every case is a pairing;
from seven, parity without a pairing found is the rule. Large networks persistent without flips are everywhere: every re-routing of a
lattice torus keeps every contact persistent and a random one has no symmetry at all. The reason is that at law-(12, 12) contacts a
contact reads one cell of each ring and feeds both, so the automaton does not say which way a ring continues; re-routing changes only
which corners the description calls one ring. Persistence belongs to the automaton. Reading distance plainly belongs to the rings: the
square torus's automaton is late read as a plane of small rings and on time read as lines, and on the square contact graph no grouping
into small rings reads plainly. A plane read plainly is still not found; what reads plainly is a line again.

## Reading

**Interpretation, not a theorem.**
- **Rings are a description at symmetric contacts.** A law-(12, 12) contact is a cell that reads its left neighbour on each ring and is
  read by both; nothing in the law pairs an incoming corner with an outgoing one. That is why persistence never needed a flip, a symmetry
  of the rings: it is a property of the corners and contacts. The network's rings are part of its declaration, not of its law (A45).
- **What the plain reading reads.** "A contact needs ring X" groups cells into X. Grouped into staircase lines, the square automaton
  reads its distance plainly, by the single fastest way straight across to each line, as tubes do; grouped into small rings it cannot.
  So "a plane needs freezing" (A41) is a fact about planes of small rings; whether it is a fact about the automaton is A45's question.
- **Lines are isolated.** Not one face toggle of a line network keeps it a network: the plain groupings found are rigid under local
  re-routing.

## Lag cutoffs and census-only claims

- **No lag cutoff.** Return parities to length E + 1, exact; distances and route counts exact.
- **Census-only.** Conclusion 3 (exhaustive to six contacts, normalised by the first dart, sampled from seven to ten), conclusion 5, the
  triangular and honeycomb parts of conclusions 6 and 7. The automaton check of conclusion 4 is a post-hoc reading
  (`same_automaton.py` beside this note: 24 of 24 tori and re-routings, the same rows cell by cell).

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| Triangular and honeycomb lines on time with single fastest ways (6) | n = 21 to 28 (checked to 20) | pass: 48 networks |
| Small rings late on every lattice (7, H3) | random re-routings of the three n = 20 tori, four seeds (read to 16) | pass: 4,058 of 4,058 |

The script is `stress_test.py` beside this note, its output `stress_test.json`; it ran in 49 seconds.

## Literature and provenance

- **Sources.** Chmutov, *Generalized duality for graphs on surfaces and the signed Bollobás–Riordan polynomial* (J. Combin. Theory B,
  2009), for partial duality; Ellis-Monaghan and Moffatt, *Graphs on Surfaces* (2013), for partial duals sharing their medial graph,
  which is our contact graph with the orientation's directions; transition systems of 4-regular digraphs (Kotzig, Las Vergnas);
  Lucas's theorem; Cramer's rule and the cycle-cover expansion of a determinant over GF(2). `LOOP-NET-20261108-001A`, Theorems 2 and 3;
  `RESCUE-MAP-20261109-001A` for the single fastest way.
- **Classification.** Known-with-delta: re-routing as partial duality, and the determinant criterion. New as far as found for the
  readings: persistence without flips as re-routing, lines that read plainly, and small rings late on the square contact graph.

## Workspace assumptions

- **Relied on.** A30 (two-time knots), A32 (binding), A41 (distance across time read through freezes), A42 (each network read as fixed).
- **Added.** A45, rings are read as declared: at a law-(12, 12) contact the automaton does not say which way a ring continues, so
  every ring-level reading is a reading of the declared rings.
- **Changed.** A41 keeps its status; its history records that the same automaton reads plainly when grouped into lines, and that on the
  square contact graph only groupings into O(n) long rings do.
- **Scope.** Networks of rule-60 rings with equally spaced law-(12, 12) contacts: maps to ten contacts (A), re-routings of the square,
  triangular and honeycomb tori (B, C).

## Ratio

Since the epic opened:
- **Substantive.** Two proofs (A, B), one pre-registered census (C), one stress test, one post-hoc reading of the automaton.
- **Administrative.** This note, the closure, and two corrections to earlier records.

## Corrections made

- **`FLIP-RULE-20261109-001`, Narrowing.** "Small maps persist by arithmetic, with no symmetry pairing them": up to six contacts they
  persist by pairings (doubled pairs or contact-graph symmetries); with no pairing found only from seven.
- **`LATTICE-REACH-20261109-001`, Not a block.** Its "digon face" is no face but a doubled pair; wording only.

Both are logged in `docs/CORRECTIONS.md` and knotlab `HISTORY.md` (commit 8291ad565).

## Pending the owner

- None new.
- Carried: whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`; the SELECTION-NOTE erratum;
  superseding `KNOT-COMPOSE-20261101-001-D001`.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — B43, then large networks persistent without flips (B42) | **Status:** Successful | A pairing for the example; persistent flipless networks are generic (re-routings); only lines read plainly, and small rings never do on the square |
| Local direction — persistence and the plain reading | Research directions | Persistence is the automaton's and the plain reading the rings'; which grouping, if any, is native is open |
| Broader exploration — G1 with G5 | Known alternatives | The even-index mechanism (B30); the cone's parity laws (B44); B28 |
| Long-term goal — G1 Space from a law (question 9) | Obstruction learned | The dimension the plain reading sees is set by how rings are declared, and on the square automaton only lines read plainly |

**Corrections:** two, made and published (above). **Goals:** a G1 and G5 checkpoint (obstruction learned); B42 and B43 taken; backlog
B45 to B48 added. **Assumptions:** A45 added; A41's history extended, status unchanged.

- **What the attempt leaves open.** Whether ring-level readings can be made native (contact laws that tell their rings apart); whether a
  grouping of the square automaton into long rings can read plainly with a two-dimensional ring graph; Theorem 3 on the triangular and
  honeycomb automata; a pairing for the cases from seven contacts.
- **The missing bridge to the program's composed topology.** A plane read plainly: here, a grouping of a plane's automaton into rings
  that is native and reads its distance without freezing.

**Next step:** Research directions — none selected, for the coordinator.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Rings the law can see (A45, G1 with G5) | 3/3 — Major | 2/3 — Testable | Give contacts laws that read their two rings differently, so the automaton fixes how a ring continues; read which re-routings of the square torus then stay persistent and which read plainly → native rings and their reading, or a proof that persistence needs symmetric laws | Alternative · deferred |
| 2 | A plane of long rings (G1) | 2/3 — Substantial | 1/3 — Stated | Search groupings of the square automaton into O(n) long rings in two directions, by moves that keep every contact on two rings, for one that is on time with ring balls growing like r² → one, or a proof that on-time groupings have a one-dimensional ring graph | Alternative · deferred |
| 3 | Small rings late on every lattice (G5) | 1/3 — Minor | 3/3 — Ready | Prove Theorem 3 for the triangular and honeycomb contact graphs with Lucas's theorem for multinomials → the proof, or the lattice where the even box fails | Alternative · deferred |
| 4 | A pairing from seven contacts (G5) | 1/3 — Minor | 1/3 — Stated | Read the cycle families of the seven-contact cases with no pairing found, for an involution on families → a pairing, or none | Alternative · deferred |

1. **Rings the law can see.** Payoff 3: it decides whether the program's ring-level readings of space (needs, plain first need, freeze
   lengths, ring balls) are native at all; Concreteness 2: the laws and the networks exist, and the census code carries over.
2. **A plane of long rings.** Payoff 2: Theorem 3 leaves this door open on the square automaton; Concreteness 1: no candidate yet, and
   line networks are rigid under face toggles.
3. **Small rings on every lattice.** Payoff 1: it extends a proved obstruction; Concreteness 3: the census already supports it.
4. **A pairing from seven.** Payoff 1; Concreteness 1: Theorem 1 says what must cancel, not how.

**Recommendation.** Research directions, none selected; directions 1 to 4 go to the backlog as B45 to B48 for the coordinator to choose.

## Final report as sent

Sent to the owner on 2026-11-09 at 22:55 UTC and copied here verbatim.

B43 and B42 are closed and published (REROUTE-20261109-001), along with two corrections.
- **B43, why the parity comes out even (proved).** The six-contact example isn't bare arithmetic. Two of its contacts send both their arcs to the same next contact, every closed walk passes one, and switching the arc there pairs the walks. Up to six contacts, every non-degenerate case is that kind of pairing or a symmetry of the contact graph. From seven contacts most cases are neither, and what remains is a parity of cycle families: the contact persists exactly when deleting it leaves det(I + tN) over GF(2) unchanged.
- **B42, large networks persistent without flips (proved, plus a pre-registered census).** They're everywhere. Re-routing a network at any set of contacts, which means swapping which ring continues where (the partial duality of maps), keeps every contact persistent. All 60 random re-routings of the square, triangular and honeycomb tori that I read are non-degenerate, with no flip at any contact. The reason is bigger than the census. At law (12, 12) a contact reads one cell from each ring and both rings read it, so the automaton never says which way a ring continues. Every re-routing is literally the same cellular automaton (checked cell by cell); only the grouping of its cells into rings changes.
- **The plain reading (proved for the square).** Grouped into lines, the tori's automata read their distance plainly at every size, by single fastest ways, and their ring graph is a cycle. On the square contact graph, a small ring is always late for some target, so any grouping that reads plainly has at most 64n rings on the n × n torus. A plane of small rings still needs freezing, and what reads plainly is a line again.

| Scope | Verdict | Why |
|---|---|---|
| This attempt: B43, then B42 | Successful | A pairing for the example; persistent flipless networks are generic; only lines read plainly |
| Local direction: persistence and the plain reading | Research directions | Persistence belongs to the automaton, the plain reading to the rings; which grouping is native is open |
| Broader exploration: G1 with G5 | Known alternatives | The even-index mechanism (B30); the cone's parity laws (B44); B28 |
| Long-term goal: G1 Space from a law | Obstruction learned | The dimension the plain reading sees depends on how rings are declared; on the square only lines read plainly |

| # | Direction | Payoff | Concreteness | First step → stop |
|---|---|---|---|---|
| 1 | Rings the law can see (B45) | 3/3 | 2/3 | Contact laws that tell their two rings apart, rerun on the square torus and its lines → native rings, or proof that persistence needs symmetric laws |
| 2 | A plane of long rings (B46) | 2/3 | 1/3 | Groupings into O(n) long rings in two directions, on time with r² ring balls → one, or proof the ring graph must be 1D |
| 3 | Small rings late on every lattice (B47) | 1/3 | 3/3 | Lucas for multinomials on the triangular and honeycomb contact graphs → proof, or the failing lattice |
| 4 | A pairing from seven contacts (B48) | 1/3 | 1/3 | An involution on the cycle families of the unpaired cases → a pairing, or none |

**Corrections:** two, both published in 8291ad565 and logged in docs/CORRECTIONS.md and knotlab HISTORY.md.
- FLIP-RULE-20261109-001's "small maps persist by bare arithmetic, with no symmetry pairing them" is a **Narrowing**: up to six contacts it's pairings, and parity with no pairing found starts at seven.
- LATTICE-REACH-20261109-001's "digon face" is no face but a doubled pair. **Not a block:** wording only, with a pending qualification on its discovery record.

**Goals:** a G1 and G5 checkpoint (obstruction learned); B42 and B43 marked taken; B45 to B48 added to the backlog. **Assumptions:** A45 added: rings are read as declared. At symmetric contacts the law doesn't fix the rings, so every ring-level reading, "a plane needs freezing" included, is a reading of the declared rings. A41's history is extended; its status is unchanged.

Commits on main: 8291ad565 (pre-registration, tickets A and B, the corrections), 20fa5b248 (the epic) and 082eb6ce9 (shared docs). I staged only my own hunks. The stress test, one size past, passed in 49 seconds, and nothing is running. No direction is selected; your call. If I were picking, I'd take direction 1, because it decides whether ring-level readings of space are native at all.
