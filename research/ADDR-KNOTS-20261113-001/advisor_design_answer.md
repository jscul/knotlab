**Headline: Class B as specified is settled by construction: every pattern lives at every level, so the census would report nothing.** I argued this by hand and did not run it.

## The hole in Class B

Substitute y = q1(x). The knots become {y, g y, h y} with g = q2 q1⁻¹ and h = q3 q1⁻¹, so the two knot rules are the same class. This is the closed out-neighbourhood hypergraph of the digraph with arcs y→gy and y→hy, which is the Seymour (1974) / Thomassen even-cycle setting.

- **Even cycle:** every permutation of level n induced by a binary tree automorphism has cycle lengths that are powers of 2. So any g-cycle of length ≥ 2 is an even directed cycle.
- **Colouring:** colour that cycle alternately. Each orbit is strongly connected, so give every other vertex the colour opposite to its next vertex on a shortest path to the cycle. Every vertex then has an out-neighbour of the other colour, so every knot is NAE.
- **Drop rule:** always alive.
- **Multiset rule:** dead at level n exactly when some word is fixed by both g and h. By your covering lemma the only possible fates are "dead up to level N, then alive" or "dead forever" (a common fixed ray). Neither is the owner's "lives a while then dies".
- **Orbit rule {x, ax, a²x}:** also always alive, since cycles of length 4 or more take the pattern 0011… and shorter ones are degenerate.

The counting reason is that one knot per word gives at most as many knots as distinctions, and Seymour's bound says a minimal non-2-colourable hypergraph needs at least as many edges as vertices. Death needs several knots per word, and then knot density becomes the main dial, which is a known kind of knob (the random NAE-3-SAT threshold is near 2.1 clauses per variable).

## 1. Lemma A

It is right for the single-member rule (u, p, q), assuming lists pass downward only and siblings do not see each other's enlistments. It is known in kind: this is the clique-width "join all of label i to label j" operation, and Courcelle–Makowsky–Rotics gives finite-state for MSO properties. Your direct argument is cleaner than routing through MSO.

Two additions:

- **Multi-member knots are near-trivial.** Knots on three list members die as soon as a list exceeds 4 members. Knots (u, u′, p) die once a list holds two 0s and two 1s, and before that they force p. Only the one-member rule is worth studying.
- **Rank, not distinguishability.** The sharper moral is that what matters is the number of distinct behaviours across the cut (cut-rank, or rank-width), not the cut's size. Courcelle–Oum (2007) proved Seese's conjecture for MSO with parity counting: decidable implies bounded clique-width. So Class A sits on the known decidable side of a known frontier.

## 2. The three-way split

It is a ladder, not a trichotomy, and it is not exhaustive.

- **(a)** is essentially Caucal's prefix-recognizable / VR-equational graphs, which have decidable MSO.
- **(b) and (c)** sit inside automatic structures, where the knot relation is accepted by a synchronous multi-tape automaton. A function computed by a transducer is a special case; a relation is more general. The grid lives here.
- **Outside both, non-flat, finitely described:**
  - Higher-order pushdown graphs and recursion schemes (Caucal hierarchy, Ong 2006) still have decidable MSO. But the finite-depth fate sequence need not be eventually periodic, because depth can be read at scales like 2^n. This is a real third behaviour: decidable but not periodic.
  - Hyperbolic and Baumslag–Solitar patterns (Kari 2007, Aubrun–Kari) have exponentially growing interfaces, are not plane-like, and have undecidable domino.
- **Growing-rank hyperedge replacement** with a uniform rule collapses to (a).

The umbrella conjecture you are circling is Ballier–Stein: domino is decidable iff the group is virtually free, which is the tree-like case.

## 3. Is Class B faithful?

Partly. Sections depending on the prefix does match "a part knows where it is". Two drifts:

- **No depth.** All distinctions are leaves, so there are no distinctions at inner depths. "Influence across depth" quietly becomes "influence across tree distance among leaves". Levels are separate patterns linked only by the covering map.
- **Lost continuity.** It abandons the macro language, so it loses the link to NEST-COUNT's weighting.

Repair: take all words of length ≤ n as distinctions, add vertical knots such as {w, w0, w1}, and place horizontal automaton knots at every level. Then a part really refers back to what contains it, and depth means depth.

Use {x, ax, bx} over a generator set, with at least two or three knots per word. Read degenerate triples as multiset NAE with fully fixed triples dropped; that keeps the covering lemma usable and avoids a rule-made artefact.

## 4. Settled by construction, and expected shares

Beyond the result above:

- Components are orbits, with sizes that are powers of 2.
- Any component containing a degenerate or repeated knot is alive under one knot per word.
- Activity class is a property of the automaton, not of the group or the pattern.

Rough guesses for s ≤ 3 by raw weight, from memory and unchecked:

| Class | Share |
|---|---|
| No trivially acting state, so exponential activity (Bartholdi's conjecture silent) | about 70% |
| Finite or virtually abelian group | 15–25% |
| Bounded, infinite and not ring-like | under 10% |

The 3-state classification has about 115 groups from 5,832 automata, and many are small. Expect the census mostly to re-read known structure. The interesting cells (bounded non-flat versus linear activity) will hold a handful of automata each, so treat them as case studies and not as shares.

## 5. What to freeze

1. **One knot per word, drop rule:** 100% alive at all levels. Any dead instance means a solver bug or an error in my argument. Check by brute force at s ≤ 2, n ≤ 6; this takes seconds and should come first.
2. **Multiset rule:** dead at level n iff a common fixed word exists. No SAT needed.
3. **Dense rule (k knots per word):** fate is predicted by density and component size, and activity class adds nothing after conditioning. This fails if, at matched density, bounded and unbounded automata differ in death rate beyond sampling noise.
4. **Bounded automata:** the fate sequence is eventually periodic with first death at a small level (say ≤ 6 for s ≤ 3). This fails on any later first death.

Cheapest honest discriminator: is there any automaton at s ≤ 3 with dense knots whose first death comes after level 8? If none exists, the class shows no depth-dependent phenomenon at census size, and you should say so.

## 6. Prior work (from memory, verify before citing)

- **Colouring:** Seymour 1974; Thomassen's even cycle problem (1985, 1992; k-regular k-uniform is 2-colourable for k ≥ 4, and Fano is the k = 3 exception); Robertson–Seymour–Thomas 1999. I know of nothing specifically on NAE on Schreier graphs.
- **Statistical models:** D'Angeli–Donno–Nagnibeda on Ising and dimers on Schreier graphs (Grigorchuk, Basilica, Hanoi); Ceccherini-Silberstein–Donno–Iacono on Tutte polynomials.
- **Domino:** Barbieri–Sablik 2016; Bartholdi–Salo on the lamplighter.
- **Random automata:** Godin's Dixon-type theorem for random Mealy automata; Akhavi–Klimann–Lombardy–Mairesse–Picantin on finiteness; Klimann 2013 on 2-letter invertible-reversible automata.
- **Undecidability:** Gillibert on finiteness and order problems; Bartholdi–Mitrofanov on the contracting case.

## 7. Ratings

| Option | Payoff | Concreteness |
|---|---|---|
| Class A | 1 | 3 |
| Class B as specified | 0 | 3 |
| Class B repaired (all depths, vertical knots, dense rule) | 2 | 2 |
| Higher-order schemes (decidable but not periodic) | 2 | 1 |

Class A is a clean negative that corrects the "interface size" reading to "interface rank". My preference is to publish Lemma A with the rank reading, record the even-cycle triviality as a by-construction result, and then run the repaired Class B only as case studies.
