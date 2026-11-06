# Native contradictions are linear

Status: Proved

Ticket `NATIVE-HARDNESS-20261024-001C`, 2026-10-24.

**What it uses:**
- from `NATIVE-HARDNESS-20261024-001B-P001`:
  - the networks, their graphs and their encoding;
  - Lemma 1: peeling of unpinned legs, and opposite forced values on the two sides of each bridge of an unsatisfiable network;
- from `SURFACE-GLUING-20261024-001B-P001`, through B:
  - Lemmas 2 and 3: hub-free gluing, self-gluing and pinning keep excluded tuples pairwise non-adjacent;
  - Lemma 4: such a relation on d ≥ 1 places allows at least half of the 2^d tuples, and exactly half only when it is a parity class;
- the knot axiom K2.

No external theorem is used.

## Standard statement

**Setting.**
- **Networks.** As in ticket B, except that a network may also have unpinned legs and several connected pieces. Networks have no loops.
- **Faces and cut knots.**
  - The *face* of a knot is its relation with pinned values substituted, on its internal edges. A face is co-independent.
  - A knot is a *cut knot* if removing it disconnects its piece of the network.
- **Parity relations and systems.**
  - A *parity relation on d places* is one parity class of {0, 1}^d: a constant (d = 1), a wire (d = 2) or a parity knot (d = 3).
  - A closed network whose faces are all parity relations is a *system of parity equations*. It is satisfiable exactly when the
    corresponding linear equations over the field with two elements are consistent.

**Theorem 1 (half rule).** Let N be an unsatisfiable connected closed network with at least two knots, and v a knot that is not a cut
knot. Then v's face is a parity relation, and the rest of N allows exactly the complementary parity relation on v's internal edges.

**Theorem 2 (native contradictions are linear).** Let N be an unsatisfiable connected closed network, and C a 2-edge-connected
component of its graph (possibly a single knot). Pin every bridge leaving C to the value forced on it by its far side. The resulting
network N_C is an unsatisfiable system of parity equations.

**Corollary 3 (polynomial time for every law).**
- The procedure given in the proof decides every native network in polynomial time: peel unpinned legs; then, along the tree of
  bridges, either some knot allows more than half of the states of its edges inside its component, or Gaussian elimination decides.
- So native networks of every set of knots, with pins, are decidable in polynomial time, without external theorems.
- Ticket A's tractability statement, Corollary 3(a), was conditional on Kazda, Kolmogorov and Rolinek. It therefore holds
  unconditionally.

**Reading.**
- **The rest leaves half open.** The rest of a connected network always allows at least half of the states of a knot's edges. So a
  knot allowing more than half, and not cutting the network, can never be the place of a contradiction.
- **Every native contradiction is a parity contradiction.** It consists of forced values carried across bridges, and odd systems of
  parity equations inside the blocks.
- **Laws without parity knots.** They contribute only constants and wires, which is why their contradictions are necklaces of odd
  rings (ticket B, Corollary 3).
- **Hardness.** Parity systems are solved by Gaussian elimination, so native networks are polynomial, and NP-hardness needs hubs
  (ticket A, conditional on Feder and Schaefer). For resolution, a parity system on a large block is a Tseitin formula (ticket B).

## Nearest known result

- **Kazda, Kolmogorov and Rolinek.** Their Theorem 11 makes edge problems over coverable delta-matroids polynomial; ticket A applied it
  to the knots.
  - Corollary 3 gives a self-contained route for the knots, a special class: relations whose excluded tuples are pairwise
    non-adjacent.
  - The half rule is a short counting argument. No statement of it was found in the bounded scans of this epic.
  - Novelty: `candidate-local-delta`. Folklore risk medium: the area is well studied, and the rule may be known in another form.
- **The procedure.** Dynamic programming over the 2-edge-connected components and bridges is standard.

## Proof

### Theorem 1

- **Number of edges.** Let d be the number of internal edges of v. Since N is connected with at least two knots, 1 ≤ d ≤ 3.
- **The face.** v's face F is co-independent on d places, so it allows at least 2^(d−1) tuples (SURFACE-GLUING B, Lemma 4).
- **The rest.** N − v is connected, and v's edges are its legs. Build N − v by gluing knots in a connected order, self-gluing extra
  shared edges and pinning pins. So the set Q of values it allows on v's edges is co-independent (Lemmas 2 and 3), and it also allows
  at least 2^(d−1) tuples.
- **The count.** N is unsatisfiable exactly when F and Q are disjoint, which forces |F| + |Q| ≤ 2^d.
  - So both allow exactly half, and they are complementary.
  - By the equality case of Lemma 4, both are parity relations. ∎

### Theorem 2

- **N_C is unsatisfiable.** A solution of N_C would extend across every bridge, since each far side allows its forced value
  (ticket B, Lemma 1).
- **No cut knots.** N_C is connected and closed, and its graph is C: 2-edge-connected, with degrees at most three. In such a graph no
  knot is a cut knot. A cut knot of degree at most three would have a bridge among its edges, because some component of the rest
  receives exactly one of them.
- **A single knot.** If C is a single knot, N_C is that knot with every slot pinned, and its pinned tuple is excluded.
- **Otherwise.** By Theorem 1 every face of N_C is a parity relation, so N_C is an unsatisfiable system of parity equations. ∎

### Corollary 3

**The procedure.**
1. **Peel.** While some knot has an unpinned leg, remove it; its other internal edges become unpinned legs. By ticket B's Lemma 1, the
   network is satisfiable exactly when the remaining closed pieces are.
2. **Bridge trees.** In each remaining piece, find the bridges and the 2-edge-connected components. They form a tree; root it at any
   component.
3. **Values allowed across a bridge.** For a bridge f whose far side from the root is the component D, let S(f) be the set of values
   of f allowed by the part beyond f. Compute S(g) first for the bridges g below D. S(g) is never empty, by peeling.
   - **Some S(g) has both values.** Then S(f) = {0, 1}. A knot of D has an unconstrained slot, so D with f pinned is satisfiable by
     peeling, and the parts below extend.
   - **Otherwise.** Pin each g to its value, pin f to the value tested, and decide D with these pins. D with pins is connected,
     closed and without cut knots.
     - If some knot of D allows more than half of the states of its edges inside D, it is satisfiable (Theorem 1, contrapositive).
     - Otherwise every face allows exactly half, so it is a parity relation (Lemma 4), and Gaussian elimination decides.
4. **Root.** A piece is satisfiable exactly when its root component, with the bridges below it pinned, passes the same test. The
   network is satisfiable exactly when every piece is.

**Correctness.**
- Every part below a bridge allows exactly the values in S, and it is joined to the rest only through that bridge. So the solutions of
  the parts combine.
- Step 3 decides each component exactly, by Lemma 1 and Theorem 1.

**Time.** Each component is decided at most three times, once per tested value of its parent bridge and once at the root, and each
decision is polynomial. ∎

## Checks

`check.py` uses the standard library only (seed 20261024), with its own solver. It confirms:
- **Theorem 1 and Theorem 2.** In 600 random unsatisfiable connected closed networks with two to ten knots, mixing parity and other
  knots:
  - all 2,021 knots whose removal keeps the network connected have a parity face, with the complementary relation as the rest's;
  - all 1,778 2-edge-connected components, with forced bridge values pinned, have only parity faces and are unsatisfiable systems of
    parity equations.
- **Corollary 3.** On 20,000 random networks of mixed laws (2,603 of them unsatisfiable), with pinned and unpinned legs, connected or
  not, the procedure agrees with the solver everywhere.

**Controls.**
- **Hub-freeness is needed.** With hubs, not-all-equal on all ten triples of five places is unsatisfiable, although every knot's
  removal keeps the network connected and every knot allows six of eight states.
- **Cut knots are exempt.** A cut knot allowing six of eight states sits in an unsatisfiable network (three pendant knots force the
  excluded tuple).
- **Each step does work.** The procedure without its Gaussian step disagrees with the solver on 1,258 networks, and the procedure with
  the half rule reversed on 8,613.

## What this does not show

- **Networks with hubs.** Ticket A's conditional NP-completeness covers them; nothing here applies to them.
- **Counting.** Counting solutions of native networks, the witness counts behind emergence, is not addressed.
- **Loops.** A knot with a loop is outside the statements as written. Its two loop slots carry one variable.
