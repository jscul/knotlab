# Hubs and memory: where native hardness lives

Epic `NATIVE-HARDNESS-20261024-001`, closed 2026-10-24.

## The question

The owner asked for "the complexity side of the thesis" alongside the space epic.
- **The thesis** reads the two/three boundary as emergence. Earlier work separated emergence from hardness: Horn and affine knots
  are easy (`BASE-THREE-20261021-001`).
- **This epic** asked where hardness lives in networks of knots:
  - in native, hub-free networks, where each distinction joins two knots;
  - or in hubs, where a distinction joins three.
- **Intuitions this epic targets:** the complexity side of the thesis, and the two/three boundary.

**The evidence:**
- [Hubs carry hardness](../../proofs/NATIVE-HARDNESS-20261024-001A/NATIVE-HARDNESS-20261024-001A-P001_hubs_carry_hardness/proof.md)
  (A, proof; complexity corollaries conditional on cited theorems);
- [Only parity makes native contradictions hard](../../proofs/NATIVE-HARDNESS-20261024-001B/NATIVE-HARDNESS-20261024-001B-P001_only_parity_is_hard/proof.md)
  (B, proof; size corollary conditional on Ben-Sasson and Wigderson);
- [Native contradictions are linear](../../proofs/NATIVE-HARDNESS-20261024-001C/NATIVE-HARDNESS-20261024-001C-P001_native_contradictions_are_linear/proof.md)
  (C, proof; no external theorem);
- [bounded scan](scan.md) (edge constraint problems, delta-matroids, general factors);
- **scoping (scratch, not evidence):**
  - a resolution-width probe whose first version was flawed (too many pins made every contradiction local);
  - a census of 81,600 random closed networks with up to 96 knots. Each parity knot gave about 50% unsatisfiable networks at every
    size; the 32 other knots gave none, out of 76,800.
  - searches for unsatisfiable networks with cycles;
  - a first run of C's procedure against a solver, with PySAT, on 40,000 networks.

## Outcome in one paragraph

**Native networks of every law are polynomial, and every native contradiction is a parity contradiction. Hubs are needed for
NP-hardness, and parity for hardness to refute.**
- **The half rule (C).** In an unsatisfiable native network, a knot whose removal keeps the network connected allows exactly half the
  states of its edges, and the rest allows exactly the other half.
  - The reason is a count: the rest of a connected network always allows at least half, and so does every face of a knot.
  - So a knot allowing more than half can never be the place of a contradiction unless it cuts the network.
- **Native contradictions are linear (C).** Cut at its bridges, with the forced values pinned, every native contradiction is a set of
  unsatisfiable parity systems: parity knots and wires.
  - This gives a polynomial procedure for every law: peeling, the tree of bridges, the half rule, and Gaussian elimination.
  - It makes ticket A's tractability unconditional; A had relied on Kazda, Kolmogorov and Rolinek.
- **Resolution (B).**
  - **Without parity knots,** native contradictions are necklaces of odd wire rings. They are refuted with derived clauses of at most
    two literals, in linear size.
  - **With a parity knot,** contradictions spread over the whole network. On cubic expanders they need width Ω(n) and, given
    Ben-Sasson and Wigderson, size 2^Ω(n); the classical Tseitin case.
- **Hubs (A).** A hub is the all-equal relation on three places, which is not a delta-matroid. With hubs, the 16 knots outside
  Schaefer's classes become NP-complete, given Feder and Schaefer.

## How it was found

| Step | Result | Status |
| --- | --- | --- |
| Census the 34 knots as delta-matroids; encode hub-free networks and hubs | All knots are coverable delta-matroids; a hub is all-equal, degree set {0, 3} | Proved (A); complexity conditional on cited theorems |
| Hypothesis for B: non-parity native networks have bounded resolution width | — | Planned |
| Notice that Ben-Sasson and Wigderson's Tseitin argument uses only two facts | Flip repair, which is the knot axiom K2, and two occurrences per variable, which is hub-freeness. So every unsatisfiable native network needs width at least the balanced boundary of its graph. | Proved (B, Theorem 5). The question became which laws have unsatisfiable networks on expanding graphs. |
| Census of random closed networks | Parity about 50% unsatisfiable at every size; no other knot ever | Scoping |
| A counting argument | A surrounded non-parity knot allows at least 5 of 8 states and the rest at least 4, so they meet: non-parity contradictions are cacti, refuted narrowly | Proved (B, Theorems 2 and 4) |
| Generalize the count to every knot that does not cut the network | The half rule; every native contradiction is linear; a polynomial procedure | Proved (C) |

## What was proved

| Result | Content |
| --- | --- |
| A, Theorem 1 | All 34 knots are coverable delta-matroids, the two parity knots even; all 155 nonempty three-place delta-matroids are coverable; all-equal is not a delta-matroid. |
| A, Corollary 3 (conditional) | Hubs make the 16 non-Schaefer knots NP-complete (Feder, Schaefer); the symmetric case is the general factor problem with degree set {0, 3} at hubs. |
| B, Theorem 2 and Corollary 3 | In an unsatisfiable native network every surrounded knot is parity, with the complementary rest; without parity knots, contradictions are cacti of odd wire cycles. |
| B, Theorem 4 | Unsatisfiable cactus networks have refutations with derived clauses of at most two literals, of linear size. |
| B, Theorem 5 and Corollary 6 | Every unsatisfiable native network needs width at least the balanced edge boundary; parity networks on cubic expanders need width Ω(n) and, given Ben-Sasson and Wigderson, size 2^Ω(n). |
| C, Theorems 1 and 2 | The half rule; every native contradiction, cut at its bridges, is a set of unsatisfiable parity systems. |
| C, Corollary 3 | Native networks of every law are decided in polynomial time, without external theorems. |

## What this changes

- **Three in two directions.** NP-hardness needs three places per relation and three relations per place.
  - Native logic has the first but not the second, and it is polynomial.
  - Two-place relations have the second without the first: two-literal reasoning is polynomial with any reuse.
  - This is the knot-level form of Tovey's theorem: three-literal clauses with each variable in at most two clauses are easy, and with
    three they are NP-complete (Tovey 1984).
  - A hub is the all-equal relation, maximally constrained in pairs, the opposite of a knot. Hardness needs a knot and a hub together.
- **Inside native logic, the only contradiction is memory's.**
  - Without parity, a three-place law's contradictions are two-place ones, odd rings of wires assembled by forced values. They are
    refuted using only clauses of two literals beyond the knots' own.
  - Parity is the only knot whose contradictions live in the whole surface. It is also the knot that counts handles
    (`SURFACE-GLUING-20261024-001`).
- **The thesis, on the complexity side.**
  - The two/three boundary of places is crossed natively only by parity, for proofs in resolution.
  - It is crossed by every NP-hard knot once hubs are allowed.
  - Emergence alone does not create NP-hardness; non-native sharing does.

## Assumptions in the workspace this challenges

| Assumption | Where it lives | Verdict |
| --- | --- | --- |
| Hardness needs hubs | This epic's title and A | **Refined.** True for NP-hardness (conditional on Feder and Schaefer). For resolution, native parity networks are already exponentially hard; native networks of other laws are not. |
| Hub-free tractability of the knots needs Kazda, Kolmogorov and Rolinek | A, Corollary 3(a) | **Superseded.** C proves it from a two-line count. |
| Non-parity native networks have bounded resolution width | B's planning hypothesis | **Confirmed in a sharper form:** derived clauses of two literals and linear size suffice. The route went through the opposite expectation, that the Tseitin argument made every knot hard. |
| Emergence and hardness are unrelated (Horn and affine knots are easy) | `BASE-THREE-20261021-001` | **Refined.** Natively, every contradiction is a parity contradiction. Memory is the only native source of contradiction and the only native source of resolution hardness, although it is algorithmically easy. |

## Provenance and novelty

| Result | Where it came from | Novelty |
| --- | --- | --- |
| A, census | Finite checks | `candidate-local-delta`; may be implicit in the delta-matroid literature |
| A, complexity corollaries | Kazda–Kolmogorov–Rolinek, Feder, Schaefer, Lovász, Cornuéjols | Classical, applied; the knot-level analogue of Tovey (1984) |
| B, Theorems 2–4 | A count on allowed states; the closure of SURFACE-GLUING B | `candidate-local-delta`, folklore risk medium. The single-clause case is classical (minimally unsatisfiable formulas with two occurrences per variable are trees). |
| B, Theorem 5 | Ben-Sasson and Wigderson's argument, with K2 as flip repair | Folklore; risk high |
| C, half rule and linear contradictions | The same count, applied to every knot that does not cut the network | `candidate-local-delta`, folklore risk medium |
| C, procedure | Dynamic programming over bridges | Standard |

**Did the perspective do real work?** Yes.
- **The knot axiom K2 is exactly the hypothesis of the Tseitin lower bound,** and the hub guardrail is exactly its other hypothesis.
- **The co-independence closure** from the space epic turned the half rule into a two-line count.
- **The reading "three in two directions"** comes from the program's distinction between a knot and a common hub.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: where native hardness lives | **Status:** Successful | Native networks are polynomial and their contradictions linear (C); resolution hardness natively exactly with parity (B); NP-hardness with hubs (A, conditional). |
| Local direction: deciding native networks | Practically exhausted | Decision and refutation are classified for every law of three-place knots. |
| Broader exploration: complexity program | Known alternatives | Counting, which is the measure of emergence, is unexamined natively; hubs are classified only through cited theorems. |
| Long-term goal: the complexity side of the thesis | Capability gained | A precise reading: emergence needs three places, NP-hardness needs also three uses per place, and the only native contradictions are memory's. |
| Next recommendation: counting what emerges natively | **Next step:** Continue, with a fresh epic | Deciding a native network is easy, but counting its witnesses, the emergent information, may not be. The topological knots count trivially (2^g; Verlinde dimensions). First discriminator: classify native counting for the seven symmetric knots through the published dichotomy for three-regular Holant problems, confirm on small networks, and test whether not-all-equal counting is hard in general but easy on planar networks. |
| Interest: that recommendation | **2/3 — Promising** | A sharp thesis-level question (is emergence hard to count while contradiction is easy?) tying emergence, surfaces and complexity. Main uncertainty: published dichotomies probably settle it, leaving mostly the reading. |
| Execution | Deferred to the owner | Bound: one epic; stop if every knot's native counting is affine or topological. |

**Alternatives:**
- native logic of every arity, extending the half rule to relations on four or more places (1/3: likely straightforward);
- a note on the half rule and native contradictions (1/3: modest magnitude, folklore risk medium).
