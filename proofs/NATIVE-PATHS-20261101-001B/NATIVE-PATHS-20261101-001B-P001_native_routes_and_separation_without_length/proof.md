# Routes in the knot's spaces: fixed by the space, carrying one bit at most

Status: Proved

Ticket `NATIVE-PATHS-20261101-001B`, 2026-11-01.

## Question

The epic asks whether network hubs can carry native paths and separation, the next gate after first emergence, on the knot's spaces. Its
first check: is a path defined through hubs fixed by the law, or chosen by an observer? Ticket A showed that the parts of a knot's space
meet in two ways:
- across 2-edge cuts as complementary two-place parity;
- across 3-edge cuts as a knot against a hub, up to signs.

This ticket asks four things:
- whether the routes these interfaces define are fixed;
- what a route carries;
- whether cutting routes separates;
- whether any length arises.

## Dependencies

- **`NATIVE-PATHS-20261101-001A`.**
  - The two-interface theorem: its items 2 and 3, the balance, and the four facts (a)–(d).
  - The library `paths_lib` (spaces, cuts, accepted relations).
- **`THREEFOLD-SPACES-20261030-001C`.** It enters through A. Its `cycles_lib` builds the cycles of Fano blocks with their units and
  connecting lines.

## Setting

- **Cuts.** These are as in A: nontrivial cuts, channels, ports, slots, and the shore relations R_X. Two cuts ∂(X) and ∂(Y) *cross*
  when X ∩ Y, X − Y, Y − X and the complement of X ∪ Y are all non-empty.
- **Shifts and proper splice cuts.** Let ∂(X) be a nontrivial 3-edge cut.
  - It is a *shift* when some vertex carries two of its edges.
  - It is a *proper splice cut* when no vertex does. It then has three distinct ports and three distinct slots.
- **Cycles of Fano blocks** (`THREEFOLD-SPACES-20261030-001C`). The cycle of k blocks has k units in cyclic order.
  - **Block i.** The Fano plane minus a line, on points 7i, …, 7i + 6. The removed line's three points are its ports.
  - **Connecting line i.** It joins two ports of block i to the third port of block i + 1.
  - **Unit i.** Block i together with connecting line i.
  - **Its two boundary incidences.** Its port is the point 7i + 2, which connecting line i − 1 reads. Its slot is connecting line i, which
    reads the port of unit i + 1.
  - **Junction i.** That incidence, between unit i's slot and unit i + 1's port.
  - **Arcs and routes.** An arc is a run of consecutive units. Between units a < b there are two routes:
    - the forward route through junctions a, …, b − 1;
    - the back route through junctions b, …, k − 1, 0, …, a − 1.

## Theorem

1. **The kinds of 3-edge cut.** Let ∂(X) be a nontrivial 3-edge cut of a knot's space, and suppose a vertex w ∈ X carries two of its edges.
   - Then Y = X − w is a shore of a nontrivial 2-edge cut, and ∂(X) is that cut with w moved across (a shift).
   - Y accepts equality or disequality on the 2-edge cut's channels (A, item 2). The shift is twisted (point side {v, v̄}, v ≠ 000)
     exactly when Y accepts disequality.
2. **Fixed by the space** (computed on the ten spaces of A).
   - The proper splice cuts are pairwise non-crossing, and none crosses a 2-edge cut.
   - Every crossing pair of nontrivial cuts involves a shift or two 2-edge cuts.
   - The decomposition into parts is unchanged under relabelling. Its parts are joined by 2-edge cuts (cycles of units) and by proper
     splice cuts (a tree), and the shifts are derived from the 2-edge cuts.
3. **What a route through atoms carries.** In a cycle of k Fano blocks:
   - Unit i accepts exactly disequality on (its port colour, its slot value). An arc of m units accepts exactly x + y = m (mod 2).
   - The two routes between units a < b carry parities b − a and k − (b − a).
   - For odd k these differ, and the closed cycle fails because both routes are present.
   - For even k they agree, and the cycle is colourable.
4. **What a route through a hub carries.** Across a proper splice cut, each side acts as one point or one line whatever it contains (A,
   item 3). So a route through a hub carries nothing about what lies beyond it.
   - Point sides of 7, 13 and 19 points in the chains, and of 7, 14 and 21 points elsewhere, all accept exactly two states.
5. **Separation.** Let J be a non-empty set of junctions of a cycle of k Fano blocks.
   - H with J's incidences cut is colourable.
   - For any two units, their port colours are unrelated (the full product) exactly when J meets both routes between them.
   - Otherwise they carry the parity of the route that J leaves intact.
6. **Counting.** Each Fano unit has exactly 5 colourings for each accepted pair, and none otherwise. An arc of m units has 5^m for each
   accepted pair.

## Proof

**Item 1.**
- **The third edge stays inside.** w's third edge goes into X. If it went to X̄, w would carry all three edges, and X would be {w} or
  disconnected.
- **The 2-edge cut.** So Y = X − w is connected, and ∂(Y) consists of w's third edge g and the remaining edge f of ∂(X).
  - Y has more than one vertex, since a single vertex has three boundary edges.
  - Its complement X̄ ∪ {w} is connected.
  - So ∂(Y) is a nontrivial 2-edge cut, and w has moved from its far shore into Y.
- **w a point.** Then w is a port of X, and X is the point side, so f's port lies in Y.
  - Y relates the colour of w (carried by g) to the colour of f's port by equality or by disequality.
  - So X accepts {(c, c, c ⊕ t)}, with t = 1 exactly for disequality.
- **w a line.** Then w is a slot of X, and X is the line side, so f's slot lies in Y.
  - Write s₁, s₂ for the values w reads on its cut edges and s₃ for f's value. X accepts (s₁, s₂, s₃) iff some colour y of g's port
    makes (y, s₁, s₂) not-all-equal with (y, s₃) accepted by Y.
  - For equality this is not-all-equal on (s₃, s₁, s₂), and the cut is plain.
  - For disequality it is not-all-equal on (s̄₃, s₁, s₂). The point side then accepts the complement, {001, 110} in this order, so the
    cut is twisted. ∎

**Item 2** is computed (checks 1–4).

**Item 3.**
- **One unit.** Fano is not colourable, so every colouring of block i makes its three ports equal, say c, and the port 7i + 2 has
  colour c. Connecting line i reads (c, c, y), which is proper iff y = c̄. Both pairs (0, 1) and (1, 0) occur, by complementation.
- **An arc.** In a cycle, junction i makes connecting line i read the port of unit i + 1. So along an arc the ports alternate, and the
  last slot reads x ⊕ m, where x is the first port colour.
- **Two routes.** The forward route forces port_b = port_a ⊕ (b − a), and the back route forces port_b = port_a ⊕ (k − (b − a)).
  - Both hold in the closed cycle, which is consistent iff k is even.
  - For even k, the alternating colours of the ports extend to every block by the unit's colourings. ∎

**Item 5.**
- **Colourable.** Cutting J splits the cycle into runs of consecutive units, each a path ending at a cut junction. By item 3, a run is
  colourable for either colour of its first port, and its last slot reads a free value. So the runs colour independently.
- **Both routes cut.** If J meets both routes between units a and b, every run containing a misses b, since such a run would contain a
  whole route. Runs are independent and complement-closed, so the two port colours range over the full product.
- **One route intact.** Otherwise a and b lie in one run, along the intact route. There the colour of a determines that of b by the
  route's parity, and both colours of a occur. ∎

**Item 6.**
- **One unit.** Colour the removed line's points c. Each of the other six lines meets that line in one point and has two of the four
  remaining points; the six lines give the six pairs.
  - A line fails iff both of its remaining points have colour c. So at most one of the four has colour c, which gives 1 + 4 = 5
    colourings.
- **An arc.** Junctions are single incidences, so an arc's count is the product of its units' counts along the forced port colours.
  Check 7 enumerates arcs of up to 3 units directly. ∎

## Checks

`check.py` (`result.json`, about 200 s):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved. | pass |
| 1 | Every nontrivial 3-edge cut of the ten spaces is proper or a shift of a 2-edge cut. Every proper point side accepts two states. | 16 proper, 160 shifts |
| 2 | The twist rule, on every shift. | 80 plain, 80 twisted |
| 3 | No two proper splice cuts cross, and none crosses a 2-edge cut. The test fires on shifts and on 2-edge cuts of the 5- and 7-cycles. | 0 crossings among proper cuts |
| 4 | The decomposition is unchanged under two random relabellings of three spaces. | 6/6 |
| 5 | Every arc of m units, in cycles of 3, 5 and 7 blocks, accepts exactly x + y = m (mod 2). | 68 arcs |
| 6 | Separation for every pair of units and every non-empty junction set, in cycles of 3, 5 and 7 blocks. The closed cycles fail. | 2998 cases |
| 7 | Unit counts (5, 5, 0, 0), and arcs of 1–3 units of the 5-cycle (5^m). | pass |
| 8 | Control: the even cycle of 4 blocks is colourable, and its routes agree for every pair of units. | pass |

**Notable rows.**
- **Check 3, the 7-cycle.** 35 crossing pairs of 2-edge cuts, 490 shift/2-edge-cut crossings and 1127 shift/shift crossings. These are
  the cycle's own cuts, which cross as the arcs of a cycle do.
- **Check 3, the twisted cube.** Its six proper cuts cross only shifts.
  - Three are plain: their point side is a 7-point Fano leaf.
  - Three are twisted: their point side holds a unit as well, which acts as a sign.

**Changes from the ticket's plan.** The plan expected tight cuts to cross in cyclic spaces, so that no tree would be canonical. The
crossing cuts are all shifts or cuts of one cycle, and the proper splice cuts stay laminar. So the plan's negative expectation is
refuted, and the routes are fixed in all ten spaces.

## Reading against the program's definitions

This section is interpretation, kept apart from the theorem.

- **Fixed by the space, not chosen.** The answer to the epic's first check is yes.
  - The parts, the cycles of units between them, and the tree of splice cuts are determined by the incidence graph. That graph is the
    declared substrate.
  - The law then fixes the relation each route carries.
- **Not native paths.** The program's path is a composition of complete contacts.
  - **A route through atoms.** It is a chain of two-place disequalities, so its relation is a bijection between its end channels. A
    two-place relation has no contact variable, so it cannot pass K1–K3 as a knot of two loops and a contact. In the owner's framing a
    2-clause never forms part of a loop or of topology.
  - **A route through a hub.** It passes equality on three channels. The owner has placed hubs in scope as a declared substrate, never
    counted as contact.
  - **So these routes are routes of the declared substrate.** The knot's contacts stay inside the parts: the line sides and the atoms.
- **Separation of the substrate.**
  - Item 5 has the shape of native separation: an intervention meets every route, the route relation is present before, and a product
    after.
  - But the routes are not native paths, so this is separation of the substrate, not native separation in the canonical sense.
  - It is also the separation one expects of a cycle; the content is that the law reproduces it exactly.
- **No length from relations.**
  - A route through atoms carries its length mod 2. A route through a hub carries nothing about what lies beyond it.
  - The count 5^m does carry the length. But it counts witnesses, which K1–K3 quantifies away; it is the amplitude multiplication of
    THREEFOLD-AMPLITUDE A, Theorem 4. Admitting a counted length would be a separate decision about measures, not a consequence of
    these relations.
- **The 2-versus-3 boundary.**
  - Across 2-edge cuts the parts meet pairwise. The atom projects each part's knots to a negation, and an odd cycle of negations is a
    2-CNF contradiction.
  - Across 3-edge cuts a knot meets a hub.
  - So in these spaces three-place emergence lives inside the parts, and everything joining the parts is pairwise or a hub.

## What this does not establish

- **Cuts of four or more edges.** These are unclassified. A 4-edge cut is balanced: two ports and two slots on each side. Two sides
  that both accept knots can fail together only as complementary parity cosets (KNOT-COMPOSE Lemma 3), here 4-place parity knots. Such
  a cut would be a hub-free meeting of knots, and it is the remaining candidate for a native path between parts.
- **Laminarity in general.** Item 2 is computed on ten spaces only.
- **Native extended distance.** None is constructed.

## Novelty

- **Classical.** The cactus structure of 2-edge cuts, the laminarity of tight cuts in splice decompositions, and the parity of cycles of
  negations (frustration) are classical graph and matching theory.
- **New here.**
  - The shift lemma and the twist rule.
  - The knot's-space instances.
  - The reading against the program's definitions of path, route and separation.
- **Folklore risk.** High for items 1–5 as graph facts. The contribution is the reading.
