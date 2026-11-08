# Circles from logic

Epic `LOGIC-CIRCLE-20261107-001` (program topology), 2026-11-07.

## The question

- **The approval.** The owner said "Yes, let's continue." to `OPEN-END-GROWTH-20261107-001`'s recommendation. They had corrected
  its framing: no law chooses anything. The question is whether round spaces exist among logical spaces, perhaps only as
  large-scale trends, and whether roundness differs in kind from polygons.
- **The owner's intuition.** "Some polygons are kind of like harmonies where the logical CNF collapses to a 3 side 'thing' … other
  shapes can resolve to something more like a ratio that continues … lines are shapes, but shapes are a unique subset of shapes."
- **Question served.** Question 9 (space from a law).
- **Terms.**
  - **A circle** is a bond ball: the distinctions whose least shared knot with a fixed distinction has at most a given size, read
    from allowed states.
  - **Its π** is Gołąb's: half the circle's perimeter measured with the circle's own distance. A round circle has
    π = 3.14159…; every plane has π between 3 and 4, with 3 only for hexagons and 4 only for parallelograms.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Periodic laws have polygonal circles with rational π.** For a parity law on a doubly periodic plane graph, bond distance is twice the graph distance of the plane dual up to a constant. So the circle is half the dual's velocity polygon, with rational vertices, and its π is a ratio of whole numbers. | proved | A |
| 2 | **Only two regular circles.** By Niven's theorem, the only regular (up to linear maps) circles of periodic laws are parallelograms (π = 4) and hexagons (π = 3), exactly Gołąb's two extremes. No periodic law has a round circle. | proved | A |
| 3 | **Laws on lines approach the circle as Archimedes did.** With a parity knot at each crossing of a line arrangement, bond distance is twice the number of separating lines, plus O(1). With n equally spaced directions the circle is a regular 2n-gon with π = 2n sin(π/2n) (odd n) or 2n tan(π/2n) (even n): Archimedes' inscribed and circumscribed polygons. These values are irrational for n ≥ 4, and such arrangements are periodic only for n = 2, 3. The Penrose pentagrid law has π = 5/φ (φ the golden ratio). | proved | A |
| 4 | **The 19 laws on Archimedean and Laves tilings.** Their π lie in {3, 10/3, 16/5, 7/2, 11/3, 4}. Ten have π = 3 (regular hexagons up to linear maps) and two have π = 4. The roundest are two dodecagons with π = 16/5. | computed exactly | A |
| 5 | **Exact distance with random diagonals.** In ℤ² with one random diagonal per square, graph distance is \|dx\| + \|dy\| minus the longest strictly increasing chain of correctly oriented squares. | proved | B |
| 6 | **Coins bend the circle.** Split each four-place knot of the square law into two three-place knots by a coin. The circle becomes a square with elliptic corners, and with fair coins the corners are exact quarter circles. π = 3.44120 at p = 1/2; p = 0 or 1 gives the honeycomb law's hexagon. The flat sides never round off. | proved, citing Seppäläinen 1997 | B |
| 7 | **Isotropic randomness makes it round.** The parity law on a Poisson-Voronoi tessellation, all of whose knots are three-place, has an exactly round circle. | proved, citing Kingman and Vahidi-Asl–Wierman | B |
| 8 | **Measured.** Square and honeycomb controls reproduce their polygons. Split laws approach their curved squares. The Voronoi law's anisotropy falls to 1.05 at radius 60. The uniform random planar law of four-place knots is not a plane: bond distance grows like n^0.28 (Brownian map n^0.25). | exploratory experiment | C |

## Answer

- **Round spaces exist among logical spaces, but no periodic law and no coin-split lattice law makes one.** By family:

| Law | Circle | π |
| --- | --- | --- |
| periodic | polygon, finitely many sides | rational |
| aperiodic order (Penrose) | polygon | irrational: 5/φ |
| lattice with coins | curved corners (exact circular arcs for fair coins) but flat lattice sides, at every scale | 3.44120 for fair coins |
| isotropic randomness (Poisson points) | exactly round | 3.14159… |
| uniform randomness with nothing drawn (random planar maps) | no plane at all: a space of dimension 4, the same in every direction | none |

- **Roundness differs from polygons in kind**, in three ways:
  - **Number.** A periodic law's π is rational; the round circle's is transcendental.
  - **Directions.** A polygon needs finitely many directions; laws on lines reach the circle only as their number of directions goes
    to infinity.
  - **Source.** Curvature appears with chance, and full roundness needs a source with no preferred direction.

## Literature and provenance

- **Ticket A.**
  - **Sources.** Velocity polygons of periodic graphs and the no-go theorem for isotropic periodic graphs (Fritz 2013, crediting Eon
    and Kotani–Sunada); periodic metrics (Burago); Gołąb (1932); self-circumferences of regular polygons (Martini and coauthors 2019;
    Wolansky 2026); pentagrids (de Bruijn 1981); Niven (1956).
  - **Folklore risk.** High for the polygons themselves. Moderate for the bond-distance reductions, the rationality of π and the
    Niven route to the two regular circles.
- **Ticket B.**
  - **Sources.** Strictly increasing chains in a Bernoulli lattice (Seppäläinen 1997, cited and not re-proved); a different
    exactly-solved shape (Seppäläinen 1998); round shapes on Voronoi and Delaunay graphs by isotropy (Vahidi-Asl and Wierman 1990,
    1992; Howard–Newman; Pimentel).
  - **Not found.** The exact distance formula, the reduction of least cycles to it, the circular corners at fair coins and π(p).
- **Ticket C.** The Brownian map (Chassaing–Schaeffer 2004; Le Gall 2013; Miermont 2013). The experiment replays these in terms of
  bond distance.
- **Where the ideas came from.**
  - **The program.** The question and the bond-distance reading.
  - **The owner's picture.** The harmony and continuing-ratio reading.
  - **Classical shape theory.** The polygon and isotropy arguments.

## Reading

**Interpretation, not a theorem.**
- **Harmonies.**
  - A periodic law's circle closes after finitely many sides, and its π is a ratio of whole numbers, whose continued fraction stops.
    Musical harmonies are ratios of the same kind.
  - The hexagonal planes have π = 3: the circumference is exactly three diameters, the least any plane allows. Their circles come
    from three directions, as in the honeycomb law, made only of three-place knots. This may be what the owner's "3 side thing"
    points at, though knot size alone does not decide it: the law of three-place knots on 4.8.8 has π = 4.
- **A ratio that continues.**
  - The round circle's π = [3; 7, 15, 1, 292, …] never stops.
  - Laws on n directions of lines reach it only as n grows, through Archimedes' polygons: alternately above and below, with
    irrational ratios from n = 4 on.
  - Aperiodic order gives the golden ratio, whose continued fraction [1; 1, 1, …] is the slowest to settle, yet its circle still
    closes after ten sides.
  - Coins bend the corners; only a source with no preferred direction rounds the whole circle.
- **Lines are shapes.**
  - **What the circles are made of.** Every circle here is assembled from lines: polygons from straight segments only. The coin
    law's circle uses straight segments along the lattice and arcs that are graphs of functions such as y = ½ + √(¼ − (x − ½)²).
  - **Distance is measured by closed shapes.** Bond distance is the size of the least knot, a closed boundary, through two points.
- **A caution.** π alone does not detect roundness. The coin law's π passes 3.14159 near p = 0.021, where its circle is a hexagon
  with slightly rounded corners.

## Workspace assumptions challenged

- **"Random laws may give roundness as a large-scale trend."** This was the open-end growth epic's expectation. It is false for
  lattice randomness: coins give an exact curved square at every scale, and the lattice's flat sides never round off. Roundness came
  only from an isotropic input.
- **"π measures roundness."** It does not; see the caution above.

## Wording correction

- **What was wrong.** On 2026-11-07 the owner rejected agency language: "Where is this agency coming from? Why is it assumed that
  there needs to be a 'choice'?" Four passages used it:
  - `research/LOGIC-AXIS-20261107-001/logic_axis.md` lines 53, 122 and 125 ("a law that selects its own dimension", "no tested law
    chooses its dimension");
  - `research/OPEN-END-GROWTH-20261107-001/open_end_growth.md` line 103 ("a single law that selects its own dimension");
  - `docs/KNOT_INTUITION.md` ("What is still chosen … No tested law selects its own").
- **The right reading.** Is a dimension derived from a rule that does not mention it, or written into the construction (a gadget, a
  product, a drawing)?
- **What changes.** The closed notes stay as published. The intuition-doc sentence is reworded with this epic's entry.

## Ratio

Since the epic opened:
- **Substantive.** Three evidence families changed conclusions: A and B (proofs) and C (an exploratory experiment).
- **Administrative.** This note and the closure.

## Pending the owner

- **Carried from `LOGIC-AXIS-20261107-001`.** Whether a native knot must also be natively bound
  (`research/LOGIC-AXIS-20261107-001/canonical_correction_request.md`).
- **Carried from earlier epics.**
  - Whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`.
  - The SELECTION-NOTE erratum.
  - Superseding `KNOT-COMPOSE-20261101-001-D001`.
  - Counted length as a native magnitude.

## Next steps

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt — circles from logic | **Status:** Successful | Five families classified: periodic (rational polygons), aperiodic grids (irrational polygons), lattice laws with coins (curved squares), isotropic random laws (round), uniform random laws (no plane). Unresolved: whether a law with no coins and no drawn plane can have a curved or round circle. |
| Local direction — shapes of periodic and lattice-random laws | Practically exhausted | Periodic laws are settled by theorem, and coins on a lattice by an exact shape. More lattice randomness changes constants, not kind; whether any lattice first-passage shape is exactly round is open even classically. |
| Broader exploration — question 9 | Line, plane and circles mapped | The number line is grown natively and the plane is a product of lines. Circles are polygons for periodic laws and round only with isotropic input. Unmapped: deterministic laws with infinitely many directions. |
| Long-term goal — space from logic | Capability gained; obstruction learned | Round space exists among logical spaces, but periodic and coin-split lattice logic does not produce it; it needs a source with no preferred direction. |
| Next recommendation — round without coins: the pinwheel law | **Next step:** Continue, as a fresh epic. Conway and Radin's pinwheel tilings are generated by one substitution rule and forced by local matching rules (Radin 1994). Their tiles turn through the irrational angle arctan(1/2), so orientations are uniformly distributed, and the tiling system is uniquely ergodic. Does the parity law on the pinwheel tiling have an exactly round circle, with no coins and no Poisson points? First discriminator: build the tiling to 5^7 tiles and measure anisotropy against radius. A round circle tends to 1; a 2n-gon stalls at 1/cos(π/2n). Then attempt the proof by unique ergodicity and rotation invariance, as in ticket B's Theorem 5. | It would answer the owner's "ratio that continues" directly: one irrational angle, applied again and again, in place of chance. |
| Interest — that recommendation | **2/3 — Promising** | The rotation-invariance argument looks robust. Main uncertainty: whether a rule with a built-in irrational angle counts as nothing drawn. Novelty risk: the round large-scale geometry of pinwheel tilings may already be known in the aperiodic-order literature. |
| Execution — that action | Deferred to the owner | **Not started.** **Stop when** the pinwheel law's anisotropy at 5^7 tiles either falls toward 1 (then prove it) or stalls (record the polygon or the obstruction). **Alternatives:** the harmonic spectrum, which rational values of π periodic laws realize (1/3); the exact taxicab formula for the logical Cartesian plane (1/3). |
