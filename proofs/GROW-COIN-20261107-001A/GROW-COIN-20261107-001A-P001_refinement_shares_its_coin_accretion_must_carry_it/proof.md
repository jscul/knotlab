# Refinement shares its coin, accretion must carry it

Status: Proved by hand. The finite claims (subdivisions, ring growths, the census of choice patterns, the decision windows, the
random runs) are checked by computation with controls.

Ticket `GROW-COIN-20261107-001A`, 2026-11-07.

## Standard statement

**Setting.** Spheres are the two-kind knot spheres of `SPHERE-GROWTH-20261107-001A`: two-coloured triangulations whose co-lines have
two or three points (T-degree 4 or 6). K_m is the octahedral knot sphere. A static law without hidden states cannot single out the
K_m, and one hidden bit per incidence can (`SPHERE-GROWTH-20261107-001A`). Here the question is whether a *growing* law can do without
that bit. As in the canonical test, no scheduler supplies an input: a growth result belongs to a law only if it holds in every
growth order.

**Two ways to grow.**
- **Refinement.** A step replaces every triangle by its j² subdivision (j = 2 or 3). The points on an edge are shared by the edge's
  two triangles.
- **Accretion.** Triangles are added at the boundary of a disc. An ADD puts a triangle on one boundary edge with a new vertex; a CAP
  puts one on two consecutive boundary edges, closing their common vertex at degree 4 or 6.
  - **Ring accretion** around a corner c grows the disc one annulus at a time. Every ring vertex is completed to degree 6, except
    that a convex turn (a ring vertex with two triangles so far) may be made a corner, of degree 4.
  - **Single-strip accretion** builds one annulus at a time, triangle by triangle in angular order.

**Theorem 1 (refinement keeps the shape).**
- Subdividing every triangle of K_m into j² gives K_{jm}.
- A partial refinement is not a closed surface, so in every order a refinement step covers the whole sphere.
- Refinement maps the capped tube T(m, L, τ) to T(jm, jL, jτ). It scales whatever it is given and never places a corner.
- So from the octahedron it grows exactly the K_{2^a 3^b}, with no labels. Its one shared decision, to refine again, is shared by the
  edges themselves.

**Theorem 2 (ring accretion).** Making the four turns of ring m corners, and no others, gives K_m. Ring accretion around a corner
of K_m produces K_m only that way.

**Theorem 3 (decisions taken one turn at a time are not enough).** With each turn decided on its own, ring accretion also closes into
non-round two-kind spheres.
- Every choice pattern up to 100 triangles closes into 38 distinct spheres. Three are round (K_1, K_2, K_3), and they come only from
  the uniform patterns.
- With an independent coin at every turn, 12 of 400 runs closed non-round, up to 646 triangles; one closed round.

**Theorem 4 (the coin must be carried).**
- In single-strip accretion, take the radius-w window at which a turn is decided. It is the same at the equator's turns as at the
  turns of every earlier ring of index at least w + 1 (checked for w ≤ 5).
- So a label-free rule of radius w cannot tie the four equator turns together. By Theorem 3, decisions taken one turn at a time also
  close into non-round spheres.
- One bit kept for one lap does tie them: set it at the first turn of the chosen lap, and make every turn of that lap a corner. By
  Theorem 2 this grows exactly the K_m, one size per choice of lap.
- That bit is history kept by the growth process, not part of the sphere. Under the canonical test it is a hidden witness, like the
  seam bits.

**Remark (a rule read off one order).** Take the radius-5 window law of the single-strip order: every window and move it uses for
K_1 to K_10. Run in random orders, it closed only K_1 and K_2 (69 of 200 runs) and was stuck otherwise. A rule read off one order is
not a law that grows in every order. Small closures are round because the window then sees the whole ring; this is no evidence about
large sizes.

## Nearest known result

- **Decorations and local rules.**
  - Levitov (*Local rules for quasicrystals*, CMP 1988) separates strong and weak local rules, with and without decorations.
    Undecorated rules characterize a family by its patches of some radius only for special parameters.
  - Mozes (1989), Goodman-Strauss (*Annals of Mathematics* 1998) and Fernique–Ollinger (*Combinatorial substitutions and sofic
    tilings*, 2010) show that substitution tilings are sofic: local rules with decorations define them, though rules without do not.
  - In these terms `SPHERE-GROWTH-20261107-001A` says that the round knot spheres are sofic, with one bit, but not of finite type.
- **Growth.**
  - Onoda, Steinhardt, DiVincenzo and Socolar (*Growing perfect quasicrystals*, PRL 1988) grow perfect Penrose tilings by local
    vertex rules from a seed with one defect. Local rules alone stall at dead surfaces without non-local information (Dworkin and
    Shieh 2016).
  - Capsids assemble by local rules in which subunits switch between conformations, which are labels (Berger, Shor, Tucker-Kellogg
    and King, PNAS 1994).
  - In algorithmic self-assembly, n × n squares need Θ(log n / log log n) tile types (Rothemund–Winfree 2000; Adleman et al. 2001).
    A constant tile set builds sizes only through a shared global parameter, such as tile concentrations: approximately (Kao and
    Schweller, ICALP 2008) or exactly with high probability (Doty, *Randomized self-assembly for exact shapes*, 2010).
- **Refinement.** Uniform subdivision of polyhedral spheres is the Goldberg–Coxeter construction (here with parameters (j, 0)).
- **Classification.** Known-with-delta. New as far as found: the refinement/accretion contrast for the knot spheres, the census of
  lopsided closures, and the decision-window identity.

## Proof of Theorem 1

- **K_m to K_{jm}.** Each face of K_m is an equilateral lattice triangle of side m, and its j² subdivision is the lattice triangle of
  side jm. The corners keep degree 4, every new vertex has degree 6, and the octahedral gluing is kept, so the result is K_{jm}.
- **All or nothing.** Suppose a triangle is subdivided and its neighbour across an edge is not. Then the subdivided edge's inner points
  and short edges lie in one triangle only, so the result is not a closed surface. The same holds for neighbours subdivided with
  different j. A closed two-kind sphere therefore arises only when every triangle has been subdivided alike, whatever the order.
- **Tube to tube.** Subdivision scales the lattice cylinder and its two caps by j, giving T(jm, jL, jτ).
- **No new corner.** Old vertices keep their degrees and new ones have degree 6, so the corners are exactly the seed's. ∎

## Proof of Theorem 2

- **K_m's rings.** Around a corner c of K_m the ring at distance d < m is a closed curve with four convex turns, on the four seams
  leaving c. At distance m those four turns are corners, the other corners of K_m except the one opposite c. Beyond, the rings shrink
  to that opposite corner.
- **Completion is unique.** Given which turns become corners, the next annulus is determined: each ring vertex receives exactly the
  triangles that bring it to its target degree.
- **Hence uniform choices give K_m,** by induction on rings.
- **Conversely,** if ring accretion around c closes into K_m, its corners at distance m from c are the four turns of ring m, and K_m
  has no corner nearer to c. So the pattern is uniform. ∎

## Proof of Theorem 3

The census and the random runs are the computations of checks 3 and 4. The non-round closures are two-kind spheres: valid closed
triangulations of the sphere with degrees 4 and 6, not isomorphic to any K_m. ∎

## Proof of Theorem 4

- **The decision window.** Within an annulus the triangles at a turn T go on in a forced order. Just before T is decided, T has three
  triangles and its left boundary neighbour, the newest outer vertex, has two. The window then reads (3, …, 3, 2, 3, 3, …, 3), as long
  as the straight runs on both sides are longer than w. That holds at every ring of index at least w + 1.
- **Same window, two decisions.** In K_m's growth the three equator turns decided within the lap become corners, while every earlier
  ring's turns, deciding in the same window, stay flat. A label-free rule sees only the window, and possibly a coin. So it cannot make
  the equator turns corners exactly when the first one was, except by chance.
- **One bit for one lap.** A walker that keeps one bit through a lap makes the four turns agree, which gives exactly K_m by Theorem 2.
  The bit is not in the sphere: it is history supplied by the process. ∎

## Checks

`check.py`, with `growth_lib.py`, runs in about a quarter of a minute and reproduces `result.json`.

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependency artifacts bound by hash; upstream proofs Proved | pass |
| 1 | K_m subdivided into j² is K_{jm} (m ≤ 4, j = 2, 3); two tubes refine to tubes, not round; one triangle refined alone is no closed surface | pass |
| 2 | Uniform ring accretion closes into K_m (m ≤ 6) | pass |
| 3 | Every choice pattern up to 100 triangles: 109 closed runs, 38 distinct spheres, 3 round, all from uniform patterns | pass |
| 4 | Independent coins: 12 of 400 runs closed non-round (up to 646 triangles), 1 round, 386 stuck | pass |
| 5 | Decision windows: the equator turns' window equals the window at which earlier turns go flat, w ≤ 5 and m = w + 2 .. w + 5; at m = w = 3 they differ | pass |
| 6 | The window law of one order in random orders: 69 of 200 runs closed (K_1, K_2), the rest stuck | pass |

## What this does not establish

- **No theorem for every label-free accretion law.** Theorems 3 and 4 cover ring accretion and its single-strip order. A law with
  other moves might store the coin in the shape of its growing edge. Since a law must grow correctly in every order, and an order can
  separate the four turns, this seems unlikely, but it is not proved.
- **Refinement reaches only the sizes 2^a 3^b** from the octahedron, and only because the seed is already round.
- **No hardness claim** beyond `SPHERE-GROWTH-20261107-001A`.
