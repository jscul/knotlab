# Counted length is a measure on the knot's spaces

Status: Proved

Ticket `SELECT-COUNT-20261101-001B`, 2026-11-01.

## Question

- **Where we started.** NATIVE-PATHS B found that relations along the routes of a knot's space carry little:
  - a route through atoms carries only its length mod 2;
  - a route through a hub carries nothing.
- **What did carry the length.** The number of witnesses: an arc of m Fano units has 5^m colourings per accepted pair. These are the
  colourings that K1–K3 quantifies away.
- **The request.** The owner asked for this count to be worked out as a measure.
- **The questions here.**
  - Is the count a measure, that is, additive over the parts of a space?
  - What does it measure?
  - How does it relate to the routes' relations?
  - How does it read against the program's definitions?

## Dependencies

- **`NATIVE-PATHS-20261101-001A`.** The side relations across nontrivial 2- and 3-edge cuts: equality against disequality, and an
  antipodal pair against its complement.
- **`NATIVE-PATHS-20261101-001B`.** The units and arcs of the cycles of Fano blocks.
- **`THREEFOLD-AMPLITUDE-20261030-001A`.**
  - The amplitude A(H, L), half the number of colourings of H − L, and Theorem 2: A is the same at every line (*one amplitude*).
  - Lemma 3 (the point lemma).
  - Theorem 4 (factorization across tight cuts, for the Pfaffian pieces with their signs).
  - Five per Fano atom, and Tutte's tree-trinity number per planar glue piece.
- **`THREEFOLD-SURFACES-20261030-001A`.** Theorem 6: the genus of a space is its number of Fano atoms when the other braces are
  planar.

## Definitions

- **Amplitude.** For a knot's space H, A(H) is half the number of colourings of H minus any one line. It is independent of the line.
- **Side counts.** For a nontrivial cut ∂(X) and an assignment w of values to its channels, N_X(w) is the number of colourings of X's
  points that are proper on X's lines. Ports take their channel's value, and slots read theirs.
- **Counted length.** The counted length of a side is ℓ(X) = log a(X), where a(X) is its count on accepted assignments; item 1
  shows this is well defined. The counted length of H is ℓ(H) = log A(H).

## Theorem

Let H be a knot's space.

1. **Uniform sides.** Across every nontrivial 2- or 3-edge cut ∂(X), N_X takes one value a(X) > 0 on X's accepted assignments, and 0
   on the others.
2. **Factorization.** a(X) · a(X̄) = A(H). So counted length is additive across every such cut: ℓ(H) = ℓ(X) + ℓ(X̄).
   - Iterated over the decomposition into parts, ℓ(H) is the sum of the parts' counted lengths: a measure on the decomposition.
   - Across splice cuts the iteration is THREEFOLD-AMPLITUDE's Theorem 4. Across 2-edge cuts it is item 2 here.
3. **Values.** ℓ is log 5 per Fano block, plus the logarithm of the glue's tree-trinity number. For example, the twisted cube's is
   6 log 5 + log 2.
4. **Routes.** An arc of m Fano units has 5^m colourings for each accepted pair, so its counted length is m log 5. Relations keep only
   m mod 2.
5. **Rings.** Cut one incidence from each of several knot's spaces, giving units, and join the units in a ring.
   - Every unit accepts exactly a negation.
   - The ring fails iff it has an odd number of units.
   - An odd ring's amplitude is the product of the units' amplitudes; an even ring has twice that product as colourings.
6. **What it respects.** A is unchanged by transposition, which exchanges points and lines, and so knot sides and hub sides. It is
   unchanged by isomorphism. It is *not* unchanged when a part is replaced by a relationally equal one: a Fano unit and a 13-point unit
   both accept exactly a negation, with counts 5 and 25.

## Proof

**The twist identity.** For an incidence (p, ℓ) of H, the colourings of H with that incidence read exchanged are exactly the colourings
of H − ℓ.
- **From H − ℓ to the twisted space.** In a colouring of H − ℓ, the line ℓ is not proper (else H would be colourable), so it reads
  three equal values. Exchanging p's reading makes it proper, and the other lines are unchanged.
- **Back.** A colouring with the twist is proper on every line except possibly ℓ with its true reading, so it colours H − ℓ.
- **The count.** So the twisted space has 2A(H, ℓ) = 2A(H) colourings, by one amplitude. This is the counting form of the point lemma.

**Items 1 and 2.**
- **Twisting a channel.** Let the cut have channels e₁, …, e_k with k = 2 or 3, and twist the incidence of e_i. A colouring of the
  twisted space is a colouring of each side, with X seeing an assignment w and X̄ seeing w ⊕ e_i. So 2A(H) = Σ_w N_X(w) N_X̄(w ⊕ e_i).
- **Complements.** Complementing every colour preserves not-all-equal, so N_X(w̄) = N_X(w), and the same holds for X̄.
- **k = 2.** The sides accept equality and disequality (NATIVE-PATHS A).
  - Each side's two accepted assignments are complements, so each side's count is one value.
  - Both assignments w accepted by X have w ⊕ e_i accepted by X̄. So 2A(H) = 2 a(X) a(X̄).
- **k = 3.** The point side accepts {v, v̄}, with one count a(X) by complementation. The line side accepts the six assignments v ⊕ e_j
  and their complements.
  - The identity gives 2A(H) = 2 a(X) N_X̄(v ⊕ e_i) for each i.
  - So N_X̄(v ⊕ e_i) = A(H)/a(X) for i = 1, 2, 3, and the same holds for the complements: one value a(X̄) on all six, with a(X) a(X̄) =
    A(H).
- **Positivity.** A(H) > 0, because H is minimally non-colourable. So both counts are positive. ∎

**Item 3.**
- **One Fano plane.** Colour the points of the removed line c. Each other line meets it once and holds a pair of the four remaining
  points, and the six lines give all six pairs. A line fails iff its pair is all c. So at most one remaining point has colour c, which
  gives 5 colourings for each c, and A(Fano) = 5.
- **Splice trees and cycles of blocks.** Item 2 multiplies these along their cuts.
- **In general.** THREEFOLD-AMPLITUDE gives 5 per Fano atom, times Tutte's tree-trinity number per planar glue piece. For the twisted
  cube this is 2 · 5⁶ = 31250, as computed. ∎

**Item 4** is NATIVE-PATHS B, item 6, here checked for every arc of the 3-, 5- and 7-cycles.

**Item 5.**
- **Each unit.** By the atom lemma each unit accepts exactly a negation. By the twist identity it has A(H_i) colourings per accepted
  pair.
- **Colourability.** The ports alternate around the ring, so it closes consistently iff the number of units is even.
- **An even ring.** Choose the first port's colour (2 ways) and each unit's interior independently, which gives 2 ∏ A(H_i).
- **An odd ring.** Its 2-edge cuts separate the units, so item 2 multiplies their amplitudes. The ring is again a connected cubic system
  that fails, and its amplitude is the same at every line (check 4). ∎

**Item 6.**
- **Transposition.** THREEFOLD-AMPLITUDE shows that the amplitude equals the transpose's; it is checked here on all ten spaces.
- **Isomorphism.** This is trivial.
- **Relational replacement.** Check 6 exhibits two relationally equal units with different counts. ∎

## Checks

`check.py` (`result.json`, about 175 s). `count_lib.py` counts colourings exactly by variable elimination.

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved. | pass |
| 1 | One amplitude at every line of the ten spaces: Fano 5; chains 5^k; star 5⁴; cycles of k blocks 5^k; twisted cube 2 · 5⁶; the 3-cycle spliced into Fano 5⁴. The counter agrees with brute force on three spaces. | pass |
| 2 | Uniform sides and a(X) a(X̄) = A(H) at every nontrivial 2- and 3-edge cut of the ten spaces. | 216 cuts |
| 3 | Every arc of m units of the 3-, 5- and 7-cycles has 5^m per accepted pair. | 68 arcs |
| 4 | Seven rings of units cut from Fano, the 13-point splice, the 3-cycle and the twisted cube, with 2 to 5 units. Units are negations; odd rings fail with amplitude equal to the product at every line; even rings have twice the product as colourings. | 7/7 |
| 5 | Transposes and random relabellings keep the amplitude. | 10/10 |
| 6 | Controls (below). | pass |

**Notable rows.**
- **The twisted cube (check 2).** Every cut leaves the glue's factor 2 on the large side. The smaller side holds one or two Fano units,
  with counted length log 5 or 2 log 5.
- **The odd five-unit ring (check 4)** has amplitude 2,441,406,250 = 31250 · 125 · 25 · 5 · 5.

**The controls.**
- Two disjoint Fano planes fail, but every line's amplitude is 0, so there is no counted length without minimality.
- A colourable even cycle still multiplies its counts.
- Two relationally equal units have different counts.

## Reading

This section is interpretation, kept apart from the theorem.

- **What counted length measures.** It is the logarithm of the number of ways a part's inside can be arranged, given what its channels
  show: what the relation hides. In these spaces it is log 5 per Fano block, and THREEFOLD-SURFACES makes each Fano atom one handle of
  the space's surface. So counted length counts the handles a part contains, plus the glue's spanning-tree number. The handles and the
  glue contribute incommensurable amounts (log 5 against log 2), so there is no common unit across kinds of piece.
- **Counting sees what relations hide.**
  - Along atoms, the relation keeps m mod 2, and the count keeps m.
  - Across a hub, the relation sees the far side as one point or one line, while the count sees its whole amplitude.
  - In rings the two are independent: the relation counts the parts (their parity decides failure), and the count counts what is
    inside them.
- **A measure with canonical weights.**
  - Counted length is positive, additive over cuts and fixed by the law and the substrate.
  - Earlier route values in the program were noncanonical because the weights had to be chosen. Counted length is a law-intrinsic
    source of such weights.
  - It does not distinguish knot sides from hub sides, since transposition preserves it.
- **Against the program's definitions.**
  - The routes it measures are routes of the declared substrate, not native paths (NATIVE-PATHS B and C). So it is *counted length*,
    a measure, and not native extended distance.
  - It leaves K1–K3 untouched, since it counts the witnesses that K1–K3 quantifies away.
  - Admitting it as a native magnitude would change the canonical doctrine. That remains the owner's decision.

## What this does not establish

- **Native extended distance.** None is constructed.
- **Counted length off the knot's spaces.** Counts exist on any system, but uniform sides and the factorization use the knot's failure
  and its minimality (the controls).
- **A metric on parts.** Taking the shorter route's counted length gives a weighted cycle or tree metric. That is standard, and is not
  claimed as a doctrine-level metric.

## Novelty

- **Ours.** The amplitude, the point lemma, one amplitude, the factorization over tight cuts, five per handle and handles from Fano
  atoms (THREEFOLD-AMPLITUDE, THREEFOLD-SURFACES).
- **New here.**
  - The factorization across 2-edge cuts.
  - Uniform sides on both kinds of cut, from the twist identity.
  - The rings.
  - The reading as counted length.
- **Classical background.** Exact counting by variable elimination.
- **Folklore risk.** Moderate.
