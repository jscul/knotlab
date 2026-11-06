# Only parity makes native contradictions hard

Status: Proved

Ticket `NATIVE-HARDNESS-20261024-001B`, 2026-10-24.

**What it uses:**
- from `SURFACE-GLUING-20261024-001B-P001`:
  - Lemmas 2 and 3: hub-free gluing, self-gluing and pinning keep excluded tuples pairwise non-adjacent ("co-independent");
  - Lemma 4: such a relation on n ≥ 1 variables excludes at most half the tuples, exactly half only when it is parity;
  - Theorem 5: a parity face of dimension three or more needs a parity knot;
- from `NATIVE-HARDNESS-20261024-001A-P001`: hub-free networks are edge problems, and they are polynomial given Kazda, Kolmogorov and
  Rolinek;
- the knot axiom K2: forgetting any one variable leaves the rest unconstrained. Equivalently, changing one variable of an excluded tuple
  always gives an allowed tuple ("flip repair");
- external theorems, cited as background or hypotheses and not admitted as local evidence (`docs/EXTERNAL_EVIDENCE_POLICY.md`):
  - **(BSW)** Ben-Sasson and Wigderson, *Short proofs are narrow — resolution made simple*, J. ACM 48 (2001). A resolution refutation
    of size S, of a formula with N variables and clauses of at most w₀ literals, contains a clause of width at most
    w₀ + O(√(N log S)). So a required width w forces size exp(Ω((w − w₀)²/N)).
  - **(U)** Urquhart, *Hard examples for resolution*, J. ACM 34 (1987): Tseitin formulas on suitable graphs need exponential
    resolution size.
  - **(X)** Cubic expanders exist, for example random cubic graphs (Bollobás 1988): there are a constant h > 0 and cubic graphs on
    every even number n of vertices with |∂H| ≥ h·|H| whenever |H| ≤ n/2.

## Standard statement

**Setting.**
- **Networks.** A *network* is a finite set of knots (the 34 relations on three bits with every pair of places unconstrained) whose
  slots are paired into *internal edges* or left as *legs*.
  - A network is *closed* if every leg is pinned to 0 or 1.
  - It is *hub-free* by construction, since every variable lies in at most two knots.
  - Its *graph* G has the knots as vertices and the internal edges as edges, possibly with parallel edges.
  - A loop, an edge with both ends at one knot, is a cycle of length one; the statements and proofs include it, and the checks cover
    networks without loops.
- **Encoding.** A network is encoded by one clause per excluded tuple of each knot, with pinned values substituted. Its variables are
  the internal edges, and its clauses have at most three literals.
- **Surrounded knots and cacti.**
  - A knot is *surrounded* if its three slots carry three distinct internal edges, none of them a bridge of G.
  - G is a *cactus* if every knot has at most two non-bridge edges. Equivalently, every block of G is a cycle or a single bridge.
- **Wires.** A *wire* is a parity relation on two places: *equal* (excluding 01 and 10) or *unequal* (excluding 00 and 11).
  - A cycle of G is an *odd wire cycle* if, once each knot's third slot is set to the value forced on it, every knot's face on its two
    cycle slots is a wire, and an odd number of these wires are unequal.
  - The value forced on a third slot comes from its pin, or from the part of the network beyond the bridge it carries.
- **Boundary.** For a set H of knots, ∂H is the set of internal edges with exactly one end in H. The *balanced edge boundary* of G
  is b(G) = min{|∂H| : n/3 ≤ |H| < 2n/3}, for n knots.

**Lemma 1 (peeling).**
- A connected network with an unpinned leg is satisfiable.
- So an unsatisfiable connected closed network is minimally unsatisfiable at the level of knots.
- In such a network, the part beyond each bridge allows exactly one value of the bridge, and the two sides force opposite values.

**Theorem 2 (surrounded knots).** In an unsatisfiable connected closed network, every surrounded knot is a parity knot, and the rest
of the network allows exactly the complementary parity class on its three edges. In particular, the rest contains a parity knot.

**Corollary 3 (necklaces).** If a network has no parity knot and is unsatisfiable, connected and closed, then it is a cactus and every
cycle in it is an odd wire cycle.

**Theorem 4 (narrow refutations).**
- Every unsatisfiable connected closed cactus network has a resolution refutation in which every derived clause has at most two
  literals. The number of resolution steps is linear in the number of knots.
- So for a law without parity knots, resolution limited to clauses of three literals decides its native networks in polynomial time.

**Theorem 5 (wide refutations).** Let N be an unsatisfiable connected closed network with n ≥ 2 knots on a graph G. Every resolution
refutation of N contains a clause with at least b(G) literals.

**Corollary 6 (dichotomy).** Let a law be a set of knots, used with pins.
- **No parity knot.** Every unsatisfiable native network of the law has a refutation whose derived clauses have at most two
  literals, with a linear number of steps.
- **A parity knot.** Cut one edge of a connected cubic graph into two legs and pin them to different values. The network of that knot
  is then unsatisfiable.
  - On cubic expanders (X), its refutations need width at least h·n/3 − 1 (Theorem 5).
  - Given (BSW), they need size 2^Ω(n).

**Reading.**
- **The counting behind Theorem 2.** A non-parity knot allows at least five of its eight states. The rest of a connected network
  allows at least four of them. So they always meet, unless the knot is parity, allows exactly four, and the rest allows exactly the
  other four.
- **Without memory, contradictions are two-place.** Every native contradiction of a law without memory is a necklace: odd rings of
  two-place wires, tied together by trees of forced values. Its refutation never needs a clause of more than two literals beyond the
  knots' own.
- **With memory, contradictions are global.** Only parity knots, the knots with memory, make contradictions spread over the whole
  surface of the network. Those are exactly the knots whose gluing counts handles (`SURFACE-GLUING-20261024-001A`).

## Nearest known result

- **Theorem 5.** It is the width lower bound of Ben-Sasson and Wigderson for Tseitin formulas.
  - Their proof uses two facts: every variable occurs in two constraints, and flipping one variable repairs a violated constraint.
    Here these are hub-freeness and K2.
  - The extension to every constraint with flip repair is folklore; folklore risk high. It is proved below for completeness.
- **Corollary 3 and Theorem 4.**
  - For knots that are single clauses, the statement reduces to a classical one. Minimally unsatisfiable formulas in which every
    variable occurs at most twice are trees of clauses, with deficiency one (Davydov, Davydova and Kleine Büning 1998).
  - The counting in Theorem 2 is elementary.
  - No statement for general co-independent constraints was found in the bounded scans of this epic. Novelty: `candidate-local-delta`,
    folklore risk medium.
  - Theorem 4 gives an unconditional polynomial-time route for laws without parity knots. Ticket A obtained polynomial time for all
    knots only conditionally, from Kazda, Kolmogorov and Rolinek.
- **Corollary 6.** Hardness of Tseitin formulas is classical (U, BSW). The program's contribution is the dichotomy: among native
  networks, hardness for resolution occurs exactly with parity.

## Proof

### Lemma 1

- **Peeling.** Take a knot with an unpinned leg. By K2, every assignment of its other two slots extends to an allowed tuple.
  - Remove the knot. Its other internal edges become unpinned legs of their other knots.
  - In a connected network this removes every knot in some order.
  - Assign values in the reverse order, choosing each knot's unpinned leg last.
- **Minimal unsatisfiability.** Removing any set of knots from a connected network leaves every remaining component with an unpinned
  leg, so the rest is satisfiable.
- **Bridges.** Let f be a bridge. Each side is a connected network with the single unpinned leg f.
  - The values of f allowed by a side form a nonempty co-independent relation on one variable (SURFACE-GLUING B, Lemmas 2 and 3):
    {0}, {1} or {0, 1}.
  - If one side allowed both values, take a solution of the other side, which exists by peeling, and extend it across f. The network
    would then be satisfiable.
  - So both sides allow a single value, and since the network is unsatisfiable, the two values differ. ∎

### Theorem 2

- **The rest is connected.** Let A be surrounded, with edges e₁, e₂, e₃. Suppose N − A were disconnected. Some component would contain
  exactly one of A's edges, and that edge would be a bridge. So N − A is connected.
- **The relation Q.** In N − A, the edges e₁, e₂, e₃ are legs, each in exactly one knot.
  - Let Q be the set of values of (e₁, e₂, e₃) allowed by N − A. N is unsatisfiable exactly when Q and A are disjoint.
  - Build N − A by adding knots in a connected order: glue each new knot along one shared edge, and self-glue the rest of its shared
    edges. Pins are pinning.
  - So Q is co-independent on three variables (SURFACE-GLUING B, Lemmas 2 and 3). By Lemma 4 there, Q allows at least four tuples, and
    exactly four only for a parity relation.
- **The count.**
  - A knot that is not parity excludes at most three tuples (Lemma 4 again), so it allows at least five.
  - Then |A| + |Q| ≥ 9 > 8, and A meets Q.
  - So A is a parity knot with |A| = 4, and Q is the complementary class.
  - That makes Q a parity face of dimension three of N − A, which needs a parity knot in N − A (SURFACE-GLUING B, Theorem 5). ∎

### Corollary 3

- **Cactus.**
  - By Theorem 2, a network without parity knots has no surrounded knot. Every knot with three distinct internal edges has a bridge
    among them.
  - A knot with a pinned slot has at most two internal edges. A knot with a loop has its third slot pinned or on a bridge.
  - So every knot has at most two non-bridge edges, and every bridgeless block, being connected with all degrees at most two, is a
    cycle.
- **Odd wire cycles.** Let C be a cycle and e an edge of C. Cut e into two unpinned legs e′ and e″. Let B be the set of values of
  (e′, e″) allowed by N − e.
  - **B is the unequal wire.** Since N is unsatisfiable, B excludes 00 and 11. B is nonempty and co-independent, so it is exactly the
    unequal wire.
  - **The path.** In N − e, the rest of C is a path from e′ to e″ through all knots of C. Each knot's third slot is pinned, or carries
    a bridge whose far side forces a constant by Lemma 1; that side is the same in N − e.
  - **Composition.** So B is the composition, along the path, of the knots' faces on their two cycle slots, each taken with the third
    slot at its forced value.
  - **Every face is a wire.** Each face is co-independent on two places: full, a single excluded pair, or a wire. By Lemma 2 of
    SURFACE-GLUING B, composing with a relation that excludes at most one pair leaves at most one excluded pair. Since B excludes two,
    every face is a wire.
  - **Odd parity.** The parities of the wires add up to the parity of B, so an odd number of them are unequal. ∎

### Theorem 4

**Claim.** Let T be a connected cactus network with one unpinned leg f, in which f is allowed exactly one value c. Then resolution
derives the unit clause asserting f = c from T's clauses, with every derived clause of at most two literals, in a number of steps at
most a constant times the number of knots of T.

Two facts about resolution are used:
- Any resolvent of two clauses on the same three variables has at most two literals, or is a tautology.
- Resolution derives every implied clause on three variables (completeness for prime implicates), and every implied two-literal clause
  from clauses of at most two literals.

Let k be the knot holding f. The claim is proved by induction on the number of knots.

- **(a) The other two slots of k are pinned or carry bridges g and h.**
  - The part beyond g is a connected cactus network with the one leg g. By Lemma 1's argument, it allows one value or both.
  - If it allowed both: by K2, k's projection onto (f, h) is full. T would then allow both values of f, which is impossible. The same
    holds for h.
  - By induction, derive the units on g and h. Resolving them against k's clauses gives clauses on f alone; since T forces f = c, one
    of them is the unit f = c.
- **(b) k lies on a cycle C of T, with cycle slots g and h.**
  - **Constants on the third slots.** Each other knot of C has its third slot pinned or on a bridge. As in (a), the part beyond that
    bridge forces a constant; otherwise the composition around C would be full, and by K2, T would allow both values of f.
  - **Faces.** By induction, derive those units. Resolving each knot's clauses against its unit leaves clauses of at most two literals
    describing its face.
  - **Around the cycle.** Resolving along the path from g to h derives the two-literal clauses of the composed relation on (g, h), with
    a constant number of steps per knot.
  - **The unit.** Resolve k's clauses against these. All clauses involved are on the three variables f, g and h. So every resolvent
    has at most two literals, and the implied unit f = c is derived.
- **Closed networks.** Let N be an unsatisfiable connected closed cactus network.
  - **N has a bridge.** By Lemma 1, the two sides force opposite values on it. The claim derives both units, and one more resolution
    gives the empty clause.
  - **N is a single knot with every slot pinned.** Its encoding already contains the empty clause.
  - **Otherwise, N is a single cycle** whose knots have their third slots pinned. Its faces are clauses of at most two literals, and
    resolution among them derives the empty clause.

**Size.** Each knot enters a constant number of steps, so the refutation has linear size.

**Decision.** Let the law have no parity knot. An unsatisfiable native network is then a cactus (Corollary 3), with a refutation using
clauses of at most three literals. Saturating resolution at three literals produces polynomially many clauses, and it finds the empty
clause exactly when the network is unsatisfiable. ∎

### Theorem 5

- **The measure μ.** For a clause C, let μ(C) be the least number of knots whose clauses imply C.
  - A clause of a knot has μ = 1.
  - The empty clause has μ = n, since every proper set of knots is satisfiable (Lemma 1).
  - A resolvent has μ at most the sum of its premises' μ.
- **A balanced clause.**
  - Walk from the empty clause toward the premise of larger μ while μ ≥ 2n/3.
  - Each step at least halves μ, and axioms have μ = 1 < 2n/3. So the walk stops at a clause C with n/3 ≤ μ(C) < 2n/3.
- **Every boundary edge occurs in C.** Let H be a set of μ(C) knots implying C. Let e ∈ ∂H, with end v in H and end u outside H, and
  suppose e does not occur in C.
  - **An assignment that violates only v.** By minimality, some assignment α satisfies the knots of H other than v and falsifies C.
    Since H implies C, α violates v.
  - **Flip e.** v's tuple changes in one place. No two excluded tuples of v's pinned face are adjacent (K2, kept by pinning), so v
    becomes satisfied.
  - **Nothing else changes.** No other knot of H contains e, because its other end u lies outside H and the network is hub-free. C
    still fails, since e does not occur in it.
  - **Contradiction.** So H does not imply C.
- **Conclusion.** Every edge of ∂H occurs in C, and |C| ≥ |∂H| ≥ b(G). ∎

### Corollary 6

- **No parity knot.** By Corollary 3 and Theorem 4.
- **A parity knot P.** Cut one edge of a connected cubic graph on n vertices (n even) into two legs pinned to different values.
  - **Unsatisfiable.** Sum the slot totals over all knots. Each internal edge counts twice and each leg once, so the sum is odd.
  - If P is even, every knot's total is even, and the sum is even.
  - If P is odd, the sum has the parity of n, which is even.
  - Either way the network is unsatisfiable.
- **The width.** If the graph has edge expansion h (X), then for n/3 ≤ |H| < 2n/3 we have |∂H| ≥ h·min(|H|, n − |H|) ≥ h·n/3. Cutting
  one edge lowers this by at most one. Theorem 5 gives width at least h·n/3 − 1.
- **The size.** By (BSW) with N = 3n/2 − 1 variables and w₀ = 3, the size is exp(Ω(n)). ∎

## Checks

`check.py` uses the standard library only (seed 20261024), with its own solver and resolution saturation bounded by the number of
literals in derived clauses. It confirms:
- **Counting.** Every non-parity knot allows at least five tuples. The 35 nonempty co-independent relations on three variables (the
  34 knots and the full cube) allow at least four, and exactly four only for the two parity relations.
- **Theorem 2.**
  - In 20,000 random connected closed networks with up to ten knots, mixing parity and non-parity knots, 1,157 are unsatisfiable.
  - All 1,590 surrounded knots in them are parity knots, with the complementary class as the rest's relation.
  - Every rest relation is co-independent.
- **Corollary 3 and Theorem 4.**
  - In 100,000 random networks of non-parity knots with up to eleven knots, 452 are unsatisfiable. All 452 are cacti, have only odd
    wire cycles, are minimal at the knot level, and are refuted with derived clauses of at most two literals.
  - The constructed necklaces have one, two and three odd rings, of the knot excluding 000 and 110 (3, 7 and 11 knots). They pass the
    same tests.
- **Theorem 5.**
  - All 236 unsatisfiable random networks of any knots tested are minimal at the knot level.
  - With one odd and the other knots even parity on the Petersen graph, the cube graph and the complete bipartite graph on three and
    three vertices, the networks are unsatisfiable and minimal, with balanced edge boundaries 5, 4 and 4. Saturation with derived
    clauses of fewer literals than the boundary finds no refutation.
- **Corollary 6.** On the Petersen and cube graphs with one edge cut into two pinned legs, the network of either parity knot is
  unsatisfiable exactly when the pins differ.

**Controls.**
- **Connectivity is needed.** A non-parity knot whose three edges are bridges is unsatisfiable when its pendant knots force the
  excluded tuple 000; the rest allows a single tuple.
- **Hub-freeness is needed.** With hubs, not-all-equal on all ten triples of five variables is unsatisfiable, and the rest of any one
  triple allows only 000 and 111. That is fewer than four, so the counting of Theorem 2 fails.
- **The count is sharp.** Parity knots do occur surrounded in unsatisfiable networks (all 1,590 cases above).
- **Parity is not narrow.** The three parity networks are not refuted with derived clauses of at most two literals.

## What this does not show

- **Laws mixing parity and non-parity knots.** Theorem 2 still applies to them, but their polynomial-time solvability rests on the
  conditional result of ticket A.
- **Stronger proof systems.** Algebraic reasoning over the field with two elements refutes parity networks easily, by Gaussian
  elimination. The hardness here is for resolution.
- **Networks with hubs.** Their NP-hardness is ticket A's conditional result. Their resolution complexity is not studied here.
