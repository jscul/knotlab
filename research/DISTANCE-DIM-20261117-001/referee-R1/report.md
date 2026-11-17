# Referee report DISTANCE-DIM-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.**
- **What holds.**
  - D1 to D5 are correct.
  - Every frozen number recomputes with the referee's own code, the failed K3 included.
  - With correlations made exactly symmetric, K3's degrees 8 and 2 and its levels hold at all three sizes, so the tie explanation
    is right. The frozen verdict correctly stays failed.
- **What the data single out, said plainly.** Neither half shows that the distance premise produces two dimensions.
  - *The implication half* is a classical round trip. The allowed states are the up-sets of a drawn order, that is, the open sets of
    its Alexandrov topology. Reading the order back is reading the specialization order. The dimension is the drawn order's.
  - *The knot half* reads a growth exponent of one particular nearness graph on bases that are themselves drawn two-dimensional. A
    different order-only test gives a different graph.

  Three published summaries can be read as "the premise gives x and y on knots". The note itself is careful.

## What holds

- **Order.** The freeze, `c04c4a400`, is at 19:23:49 UTC; the run went from 19:24:00 to 19:26:07.
- **D1 (proved).** Both directions of the proof check out. If w is above neither u nor v, the up-set ↑u ∪ ↑v separates; if w is
  below neither, the complement of ↓u ∪ ↓v does. The four cases leave only u ≤ w ≤ v or the reverse.
- **D2 (proved).** As stated.
- **D3 (proved; the owner's item 1).**
  - **The hypothesis does its job.** "Every comparable pair in a chain of three" is what makes betweenness see every comparable pair.
  - **The propagation is right.** For comparable pairs {x, w} and {w, y}:
    - if x and y are comparable, the triple's middle fixes the second orientation from the first;
    - if they are incomparable (known, since comparability is read), w is above both or below both.

    Connectedness links all pairs.
  - **The referee's own run of this propagation** rebuilds P or its reverse on all seven orders that satisfy the hypothesis
    (`referee_dims.py`, `.json`).
  - **One point to add.** The dimension does not need D3. By D2 each pair's states show whether it is ordered, with no hypothesis,
    and order dimension depends only on the comparability graph (Gallai; Trotter, Moore and Sumner).
    - So bare S_3's dimension, 3, is also read from its states, through pairs.
    - The referee's exhaustive search of its 48 linear extensions finds no 2-realizer and finds a 3-realizer.
    - "Bare S_3 reads nothing" is true of the betweenness route only.
- **The implication bases recompute.** The referee built each order's up-sets itself. All eight hold:
  - betweenness equals the interval triples;
  - a missing joint pattern equals comparability.

  The other checks:
  - **Comparability from betweenness** is exact on the seven, and absent on bare S_3.
  - **Dimension.** It is 1 on the chain, and 2 on the four two-way orders (coordinate realizers verified). It is 3 on 3 × 3 × 3
    (coordinate realizer; it contains 2³) and on S_3 with bottom and top (no 2-realizer among 48 extensions).
  - **The counts** of states are 13, 70, 924, 120, 226, 980, 20 and 18.
- **D4 and D5 (proved).**
  - **D4.** The full-support argument is right: a private distinction is forced when its ends agree and free when they differ.
  - **D5.** Summing out the privates gives weights 1 and 2, tanh K = −1/3, above the critical point. Onsager's 1/ξ = ln 3 − ln 2.
- **The chain grid** (the owner's items 3 and 4). The referee wrote its own float row transfer for the grid and derived the private
  correlations from the conditional mean −(s_u + s_v)/2.
  - **The tie mechanism is confirmed.** Mirror-image entries of the raw floats differ by 1.7 to 2.8 × 10⁻¹⁶. That is enough to
    flip a strict comparison between exactly tied quantities, as the note explains.
  - **With exact symmetry,** reading each correlation as a function of the displacement's class under the torus's eight symmetries,
    the gap degrees are 8 at a grid start and 2 at either kind of private start. The levels are exactly K3's frozen values at L = 8,
    10 and 12. At L = 12 they are 1, 8, 20, 32, 44, 56, 66, 64, 52, ….
  - **The transfer gaps,** from a symmetrized row matrix, are 0.37638, 0.37191 and 0.37020, as published, tending to 0.3691.
- **The weave.**
  - **The levels** of the relative-neighbourhood graph are 1, 12, 23 / 1, 12, 30, 38 / 1, 12, 30, 48, 53, as K4 predicted.
  - **The transfer gaps** are 0.1987, 0.1351 and 0.1021, with gap × width 1.192, 1.216 and 1.225, as published.
- **Post hoc labels.** The note and the objects row label K3's 8 and 2 at L = 10 and 12 as post hoc. K1's weave case is labelled as
  well. The goals and intuition entries do not mention them.

## 1. Known mathematics: the implication half is a classical round trip (Not a block, but it changes how it reads)

- **What the allowed states are.** They are the up-sets of P, that is, the open sets of P's Alexandrov topology.
- **What reading the order back is.** "u is below v" is "every open set containing u contains v", D2's missing pattern, which is
  the specialization order of that topology (Alexandrov 1937). Equivalently, Birkhoff's duality between finite orders and finite
  distributive lattices gives P back from its lattice of up-sets.
- **Where the dimension comes from.** The order dimension then follows from Dushnik and Miller, with comparability invariance
  (Gallai; Trotter, Moore and Sumner).
- **What is the study's own.** D1, that the disagreement count's betweenness is exactly the interval, is a folklore-level addition
  (Glivenko; Pitcher and Smiley).

So "the states give back the order and its dimension" restates Alexandrov and Birkhoff for a drawn order. The note names Birkhoff
in a list but presents the result as the answer under implications. Name the specialization order as what is read.
- **This is worth putting to John.** He said "distance is topological". Under implications, the allowed states literally are a
  topology, and the order with nothing skipped is its specialization order. That is a clean, known way his words come true, and it
  is known mathematics, not a finding.

## 2. "Order dimension read from the states" and "two dimensions on knots" (Narrowing, wording; the owner's item 2 and the coordinator's question)

- **Under implications.** The order and its dimension are put in by the drawn order and read back. The note says so: "The grid is
  still drawn. The states read its dimension; they do not choose it."
  - Two summaries drop the caveat: the intuition entry ("its number of independent orders: 1 on a chain, 2 on a grid, 3 on a
    three-way grid") and A97's challenge text.
  - The goals line keeps it ("on a drawn grid").
- **Under knots.** The weave and the chain grid are themselves drawn two-dimensional, and the thread one-dimensional. The nearness
  graph is local in that drawing: the knot-neighbours plus, on the weave, same-class second neighbours. So its balls grow like the
  drawing, quadratically on the two tori and linearly on the thread. The growth exponent reads the drawn dimension, exactly as on
  the implication side.
  - *Three summaries can be read as "the distance premise gives two dimensions on knots".* They are the intuition entry and A97's
    text ("levels from a start grow in two dimensions on the weave and the chain grid"), and the goals line ("a two-dimensional
    growth of nearness levels").
  - *The knot half does not show that.* Say beside each: "on bases drawn two-dimensional; the growth reads the drawn dimension, as
    the thread's linear growth and the tree's exponential growth do".

## 3. The order-only reading depends on its test (Narrowing; the coordinator's question)

The referee read the weave's τ (float transfer, L = 6, 9 and 12) with two other order-only tests besides the study's relative
neighbourhood:

| Test | Neighbours of a start | Reach | Levels at L = 12 |
| --- | --- | --- | --- |
| relative neighbourhood (the study's): nothing nearer to both | 12: six knot-neighbours, six same-class second neighbours | all | 1, 12, 30, 48, 53 |
| the six nearest by τ | 6: the six same-class second neighbours | one class only: 12 of 36, 27 of 81, 48 of 144 | 1, 6, 12, 18, 11 |
| the unit ball, τ ≤ 1 | 17, 32, 36 at L = 6, 9, 12 (grows with L) | all | 1, 36, 95, 12 |

- **Under a nearest-neighbour reading the weave does have six neighbours, but they are the wrong six.** That graph splits the weave
  into its three classes, each a two-dimensional lattice of its own.
- **The unit ball is not local at all.**
- **So degree 12 belongs to the relative-neighbourhood test.** Quadratic growth survives in the two local readings.
- **No order-only reading tried gives an order,** let alone two independent orders. What they give is a graph and its growth
  exponent.
- **A fair wording.** "Under the relative-neighbourhood test, the nearness graph has degree 12..."

## 4. The weave's criticality (the owner's item 5; Not a block)

- **Three widths alone would only suggest it.** But the zero-temperature triangular antiferromagnet's criticality is known exactly:
  spin correlations decay as r^(−1/2) with period three (Stephenson 1964 and 1970), and the model is a Gaussian height model at its
  critical coupling (Blöte and Hilhorst 1982; Nienhuis, Hilhorst and Blöte 1984).
- **The measurement matches the conformal prediction.** With the spin's scaling dimension x = 1/4, conformal finite-size scaling on
  a strip with rows √3/2 apart gives gap × width → π√3 x / ln 3 = 1.238 in base 3. The measured 1.192, 1.216 and 1.225 approach it.
- **So "critical" is known mathematics, and the study's numbers agree with it.** Cite it rather than resting on three widths.

## 5. Smaller points (Not a block)

- **The table's row for bare S_3.** "Order from the states: nothing" should say "nothing through betweenness". Its pairs give the
  order and dimension 3.
- **"An order, not a ruler" (counts 3 and 6 on 3 × 3).** It is correctly stated.
- **Words.** "Nearness" and "growth dimension" are clear. "Ruler" for a linear distance along an axis is the program's word.

## Fixes for the thread (listed for the owner, not folded in)

1. **What the dimension summaries read.**
   - Say that the implication half reads a drawn order back through its Alexandrov topology (specialization order; Birkhoff).
   - Add "drawn" beside "2 on a grid" in the intuition entry and A97.
   - Add "on bases drawn two-dimensional; the growth reads the drawn dimension" beside "levels grow in two dimensions" in the
     intuition entry, A97 and the goals line.

   **Narrowing.**
2. **The test behind degree 12.** Scope the degree-12 result to the relative-neighbourhood test, and report that a nearest-neighbour
   reading gives the six same-class neighbours in three separate classes. **Narrowing.**
3. **Known results.** Cite the weave's known criticality and the 1.238 limit, name the specialization order, and correct bare S_3's
   row. **Not a block.**

## How the work was split

- **The referee:**
  - read the proof, the pre-registration, the note, `dimlib.py`'s chain grid and the published summaries;
  - checked D1 to D5 by hand;
  - wrote its own up-set enumeration, D3 propagation and realizer search, and its own chain-grid and weave transfer matrices with
    exact symmetry;
  - recomputed every frozen value;
  - ran two further order-only tests.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- `referee_dims.py` and `.json`:
  - the implication half;
  - the chain grid (symmetrized gap graph, levels, transfer gaps);
  - the weave (relative-neighbourhood levels, the nearest-six and unit-ball readings, transfer gaps).
