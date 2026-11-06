# Fano atoms are handles

Status: Proved

Ticket `THREEFOLD-SURFACES-20261030-001A`, 2026-10-30.

**What it uses:**
- `THREEFOLD-GRAMMAR-20261030-001A`: the tight-cut decomposition of the incidence graph B(H) of a three-fold space.
  - Its pieces are cubic, and every tight cut splices its two contractions.
  - Its braces are Heawood graphs, doubled squares, planar braces, or trisums of smaller Pfaffian braces.
  - Every leaf is a Heawood graph (a Fano plane minus a point or a line).
- `THREEFOLD-SPACES-20261030-001A` (library) and, for the reading, the duality of `SPACE-SELECTION-20261030-001C`.
- Classical facts, not replayed:
  - orientable cellular embeddings correspond to rotation systems, with genus from Euler's formula (Heffter–Edmonds);
  - genus does not increase under taking minors;
  - homeomorphic graphs have equal genus;
  - the genus of a disconnected graph is the sum over its components (Battle, Harary, Kodama and Youngs 1962);
  - a 3-connected planar graph has one planar embedding up to mirroring (Whitney).

## Why this ticket exists

The owner asked whether each three-fold space of the knot defines a closed surface whose genus equals its number of Fano atoms. A yes would
be the first place the knot determines a canonical topological object rather than a combinatorial class.

Scoping found two things:
- genus is not additive over 3-edge cuts in general (K₃,₃ spliced with K₃,₃ has genus 1);
- on all eight spaces up to 22 points it equals the number of Heawood braces.

This ticket proves why: a Fano atom keeps its handle when one of its vertices is deleted, and that is exactly what additivity needs.

## Standard statement

**Setting.**
- **Rotation systems.** A rotation system ρ of a graph (parallel edges allowed) gives every vertex a cyclic order of its edge-ends.
  - Faces are the orbits of the tracing map: arrive at a vertex along an edge, then leave along the next edge in the cyclic order.
  - For a connected graph, g(ρ) = 1 − (V − E + F)/2.
  - The genus γ(G) is the least g(ρ).
  - The mirror ρ̄ reverses every cyclic order and has the same faces reversed.
- **Splices.**
  - Let A have a vertex x of degree three and R a vertex y of degree three, and let σ match the three edge-ends at x with those at y.
  - The splice A ⊙ R deletes x and y and joins the matched ends.
  - Every tight cut of B(H) is such a splice of its two contractions.
- **Transitions.** For a rotation system ρ of G = A ⊙ R, number the cut edges 1, 2, 3.
  - τ ∈ S₃ sends i to the cut edge through which the face entering A's side through i first leaves.
  - π is defined the same way on R's side.
  - For cyclic orders r of the cut edges at x and r̃ at y, ρ_A^r and ρ_R^r̃ are the rotation systems induced on A and R.
  - cyc counts the cycles of a permutation.
- **Rigid.** A is *rigid at x* when γ(A − x) = γ(A). Then also γ(A − e) = γ(A) for each edge e at x.

**Results.**
- **Lemma 1 (face-tracing identity).** 2(g(ρ) − g(ρ_A^r) − g(ρ_R^r̃)) = cyc(r∘τ) + cyc(r̃∘π) − cyc(π∘τ) − 3 =: D(r, r̃).
- **Lemma 2 (the table, exhaustive over S₃).**
  - (a) D(r, r⁻¹) ≤ 0 for all τ, π and both 3-cycles r, the inverse taken through σ.
  - (b) max D ≥ 0 whenever τ or π is a 3-cycle.
  - (c) max D ≥ −4, with equality only for τ = π = id.
  - (d) max D = −2 only when both τ and π fix a cut edge.
  - (e) For 3-cycles τ and π, max D = 0 if π = τ⁻¹, and max D = 2 otherwise.
- **Lemma 3 (a face that turns back costs a handle).** If τ fixes a cut edge and that edge is not a bridge of A, then g(ρ_A^r) ≥ γ(A − x) + 1
  for both r.
- **Theorem 4 (splice lemma).** γ(A ⊙ R) ≤ γ(A) + γ(R) always. If A is rigid at x and the edges at x are not bridges, then
  γ(A ⊙ R) = γ(A) + γ(R) for every connected R and every matching σ.
- **Theorem 5 (minimal maps of a splice).** Suppose A is rigid at x and R is rigid at y, with no bridges at x or y. Then:
  - the minimum-genus rotation systems of A ⊙ R are exactly the gluings of minimum-genus systems of A and R whose rotations at x and y
    are compatible (inverse through σ);
  - their number is N(A)·N(R)/2, where N counts minimum-genus rotation systems.
- **Theorem 6 (genus formula).** Let G be the incidence graph of a three-fold space. Suppose every non-planar brace B of a tight-cut
  decomposition satisfies γ(B − v) = γ(B) at every vertex. Then γ(G) = Σ γ(B) over the braces.
  - The Heawood graph satisfies this, so if every other brace is planar, γ(G) is the number of Heawood braces: one handle per Fano atom.
  - The trisum of three cubes satisfies it too, with genus 1.
- **Theorem 7 (minimal maps of three-fold spaces).** Suppose every brace other than the Heawood graphs is planar. Then both sides of every
  tight cut are rigid. So every minimum-genus embedding of G is a compatible connected sum of Heawood maps (one per Fano atom) and planar
  maps of the glue, and their number is Π_B N(B) / 2^(number of tight cuts).
  - Here N(Heawood) = 16, N(doubled square) = 4, and N(3-connected planar brace) = 2.
  - With one, two and three atoms and no glue this gives 16, 128 and 1024.
- **Proposition 8 (the Fano plane's surface).**
  - The Heawood graph has exactly 16 torus rotation systems, all with seven hexagonal faces.
  - They form one orbit under its 336 automorphisms and mirroring, eight per handedness, so the Heawood map is chiral.
  - Any two faces share exactly one edge, so the dual is K₇ on the torus.
  - The dual's 14 triangles are the seven points and the seven lines of the Fano plane. The faces around the points form a Fano plane on
    the seven faces, and so do the faces around the lines.

## Nearest known result

- **Additivity of genus.**
  - It holds over blocks (Battle–Harary–Kodama–Youngs 1962).
  - It holds within one over 2-amalgamations (Decker–Glover–Huneke 1981; Stahl 1980).
  - Alpert (1973) treats amalgamations of complete graphs.
  - A bounded search found no statement for splices along three edges with the vertex-deletion hypothesis.
- **Method.** The face-permutation bookkeeping is in the spirit of Stahl's permutation-partition pairs.
- **The Heawood map and K₇ on the torus** are classical (Heawood 1890; the seven-vertex torus of Möbius and Császár).
- **Classification.**
  - Theorem 4 and Theorem 5: no overlap found (candidate local delta). Folklore risk is moderate, because the proof is short and uses
    standard tools.
  - Theorems 6–7 and the knot reading are new here.

## Proof of Lemma 1

**Counting faces.**
- Every face of G lies inside one side, or alternates between the sides through cut edges.
- The alternating faces correspond to the cycles of π∘τ:
  - a face entering A's side through i next crosses back through τ(i);
  - it then re-enters A's side through π(τ(i)).
- In ρ_A^r, R's side is replaced by x. A face leaving through cut edge j re-enters through r(j), so the faces through x correspond to the
  cycles of r∘τ. Likewise, the faces of ρ_R^r̃ through y correspond to the cycles of r̃∘π.
- The faces inside one side are shared. So F(ρ_A^r) + F(ρ_R^r̃) − F(ρ) = cyc(r∘τ) + cyc(r̃∘π) − cyc(π∘τ).

**Euler bookkeeping.**
- V = V_A + V_R − 2 and E = E_A + E_R − 3.
- So 2(g − g_A − g_R) = (F_A + F_R − F) − 3. ∎

## Proof of Lemma 2

Exhaustive over τ, π ∈ S₃ and the 3-cycles r, r̃ (72 and 144 cases). The values of max D are −4 once, −2 nine times, 0 24 times and
2 twice. ∎

## Proof of Lemma 3

- Suppose τ fixes cut edge i. Then the face entering A's side through i also leaves through i.
- In ρ_A^r this face traverses the edge between x and the end of i in both directions, whatever r is.
- Deleting a non-bridge traversed twice by one face splits that face: F rises by one and E falls by one.
- So the genus falls by one, and g(ρ_A^r) − 1 ≥ γ(A − e) ≥ γ(A − x). ∎

## Proof of Theorem 4

**Upper bound.**
- Take minimum-genus systems ρ_A and ρ_R, mirroring ρ_R if needed so that its rotation at y is the inverse of ρ_A's at x through σ.
- Glue them: on G, keep their rotations away from x and y.
- The induced systems of the glued ρ are ρ_A and ρ_R themselves. So by Lemmas 1 and 2(a), g(ρ) ≤ γ(A) + γ(R).

**Lower bound.** Let ρ be a minimum-genus system of G with transitions τ and π, and choose r and r̃ maximizing D.
- **τ or π a 3-cycle.** D ≥ 0 by Lemma 2(b), so γ(G) ≥ γ(A) + γ(R).
- **Otherwise, and not both the identity.** Then D ≥ −2 (Lemma 2(c)). τ fixes an edge, so Lemma 3 and rigidity give
  g(ρ_A^r) ≥ γ(A) + 1. So γ(G) ≥ γ(A) + 1 + γ(R) − 1.
- **τ = π = id.**
  - Each crossing face traverses one cut edge in both directions and nothing else across the cut.
  - Delete the three cut edges. The first two each split a face and lower the genus by one. The third splits a face and disconnects G,
    leaving the total genus unchanged.
  - So the two sides A − x and R − y carry a rotation system of total genus γ(G) − 2. By Battle–Harary–Kodama–Youngs,
    γ(G) − 2 ≥ γ(A − x) + γ(R − y).
  - Now γ(A − x) = γ(A) by rigidity, and γ(R − y) ≥ γ(R) − 2, because re-inserting a vertex of degree three costs at most two handles
    (one tube for each of its second and third edges).
  - So γ(G) ≥ γ(A) + γ(R). ∎

## Proof of Theorem 5

**Every minimal system is a standard gluing.** Let ρ be of minimum genus γ(A) + γ(R).
- **τ is a 3-cycle.** Suppose τ fixed an edge.
  - If π is a 3-cycle, then max D = 0 and Lemma 3 gives γ(G) ≥ γ(A) + 1 + γ(R).
  - If π also fixes an edge and τ = π = id fails, then Lemma 3 on both sides gives γ(G) ≥ γ(A) + γ(R) + 1.
  - If τ = π = id, then γ(G) ≥ 2 + γ(A − x) + γ(R − y) = γ(A) + γ(R) + 2.

  Each case contradicts minimality.
- **π is a 3-cycle,** by symmetry.
- **π = τ⁻¹.** Otherwise max D = 2 and γ(G) ≥ γ(A) + γ(R) + 1 (Lemma 2(e)).
- **The induced systems are minimal and compatible.** With r = τ⁻¹ and r̃ = τ (the maximizers, D = 0), the induced systems have genera
  summing to γ(A) + γ(R). So both are minimum-genus, and their rotations at x and y are inverse.

**Every compatible gluing is minimal.** Such a gluing has genus at most γ(A) + γ(R) by the upper-bound construction, hence exactly that.

**The correspondence is a bijection.**
- The rotation at x of a minimal ρ_A must be τ⁻¹.
- Otherwise it would be τ, with one face through x instead of three, and one more handle.

**The count.** Mirroring is a fixed-point-free involution on R's minimum-genus systems that swaps the two rotations at y. So exactly half
of them are compatible with any given ρ_A. ∎

## Proof of Theorem 6

Peel leaves of the decomposition tree, one at a time; each leaf L is spliced to the rest R along its tight cut.
- **A planar leaf.**
  - γ(G) ≥ γ(R), because R arises from G by contracting the connected shore L − x.
  - γ(G) ≤ γ(L) + γ(R) = γ(R) by Theorem 4.
- **A non-planar leaf** satisfying the hypothesis at its contracted vertex adds exactly γ(L) (Theorem 4). Braces have no bridges.
- **The last brace** contributes its own genus.
- **Why the Heawood graph satisfies the hypothesis.** It has genus 1, and so does every vertex-deleted subgraph. Such a subgraph has
  13 vertices, 18 edges and girth 6, so a planar embedding would need 7 faces of length at least 6, which is 42 > 36 edge-sides.
- **The trisum of three cubes** has genus 1 and keeps it under every vertex deletion (computed). ∎

## Proof of Theorem 7

Theorem 5 needs both sides of each tight cut to be rigid.
- **Each side holds an atom.** Each side of a tight cut contains at least one leaf of the decomposition tree, hence a Heawood atom.
- **The side's genus.** Let S be one side's contraction, with contracted vertex z. Its genus is its number of atoms (Theorem 6).
- **S − z keeps that genus.**
  - S − z is the shore's induced subgraph.
  - It still contains each atom of its side as a splice piece, or, for an atom containing z, as a Heawood graph minus a vertex (genus 1).
  - Peeling the atoms by Theorem 4 (the rest may have vertices of degree two) shows γ(S − z) ≥ number of atoms = γ(S).
- **Applying Theorem 5 at every cut** gives the structure and the count. N(Heawood) = 16 (Proposition 8); the doubled square has 4 planar
  systems (computed); a 3-connected planar brace has 2 (Whitney). ∎

## Proof of Proposition 8

- **All faces are hexagons.** A genus-1 system of the Heawood graph has F = E − V = 7 faces. Their lengths sum to 42, and each length is
  at least 6, so all seven are hexagons.
- **The rest is computed:**
  - the 16 systems;
  - the single orbit under automorphisms and mirroring;
  - the 8 images of one map under automorphisms alone (so the map is chiral);
  - every two faces sharing exactly one edge (so the dual is the simple graph K₇);
  - the face triples around the points (and around the lines) covering every pair of faces exactly once. ∎

## What the computation checks

`check.py` (about 15 seconds):
- the permutation table;
- the identity of Lemma 1 on 1200 random cases (three splices, four choices of rotations at the cut);
- the Heawood graph's genus, rigidity, torus maps, orbit, chirality and dual;
- the splice lemma for the Heawood graph spliced into seven graphs with two matchings each, and its failure for K₃,₃;
- all 128 minimum-genus systems of the 13-point space, each a standard gluing of two Heawood maps, with faces 8 hexagons and 3 decagons;
- the genus formula on the 7-, 13-, 19-, 21-, 22- and 43-point spaces (genus 1, 2, 3, 3, 3, 6);
- the trisum of three cubes and the doubled square;
- controls.

## Reading

- **A canonical surface.** The incidence graph of the knot's three-fold space is the graph of its triangles and contacts. Its least genus
  is the number of Fano atoms.
  - Each atom is a handle, and the glue (planar in the main case) adds none.
  - The surface is determined up to homeomorphism by the space itself, not chosen.
- **The minimal maps.**
  - Every minimal map is assembled from copies of one map, the Heawood map on the torus, joined along the glue.
  - Each copy can be glued in with either handedness and at a few positions, so a space has finitely many minimal maps up to symmetry:
    1 for the Fano plane, 2 for the 13-point space, 3 to 6 for the 19-point spaces (ticket B).
- **The Fano space is the seven-vertex torus.** Read dually, its minimal map is the seven-vertex triangulation of the torus.
  - The triangles come in two colours, like a checkerboard: the seven points of the Fano plane and its seven lines.
  - In the knot's gadget these are its seven triangles and its seven contacts, the corner line counted as a contact.
- **The two/three boundary, once more.** The three-place atom carries the topology (a handle). The two-place glue is planar.

## Nonclaims

- **Non-orientable genus** and embeddings above the minimum genus are not treated.
- **Non-planar glue.** The formula with non-planar glue is proved only for braces that keep their genus under vertex deletion. The trisum
  of three cubes is checked; no general statement about trisums is claimed.
- **This is the topology of an incidence graph.** It is a canonical invariant of the knot's space. It is not a native contact topology in
  the K1–K3 sense, and not a metric.
