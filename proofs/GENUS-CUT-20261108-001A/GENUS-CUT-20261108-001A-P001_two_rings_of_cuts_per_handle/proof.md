# Two rings of cuts per handle keep one piece

Status: Proved by hand. The finite claims are checked exactly in `check.py`.

Ticket `GENUS-CUT-20261108-001A`, 2026-11-08.

## Standard statement

- **Networks.** Rule-60 rings joined by contacts with law (12, 12), consecutive contacts on a ring at least two cells apart
  (`LOOP-NET-20261108-001A`). The positions give a rotation system on the ring graph G (rings as vertices, contacts as edges), which
  embeds G cellularly in a closed orientable surface S of genus g: always orientable, since every ring runs one way.
- **Cuts and pieces.** Cutting a set C of contacts freezes them (A38). Afterwards say that ring X **meets** ring Y when an uncut contact
  on X needs Y at some lag. The **pieces** of the cut network are the classes of rings linked by chains of meetings; the network is in
  **one piece** when there is one class. Two sets of rings are separated exactly when no uncut contact on either side needs a ring on
  the other, the native separation of `SEPARATE-20261108-001A`.
- **Rings of cuts.** The dual graph G* has a vertex for each face of the embedding and a dual edge e* for each contact e, joining the
  faces on its two sides. A **ring of cuts** is a cycle of G*; cutting it freezes the contacts whose dual edges it uses. A family of rings
  of cuts is **independent** when no nonempty part of it adds up to zero mod 2, and its **number** is the dimension of the cycle space
  Z1(C*) of the dual edges of the contacts it cuts.

**Theorem 1 (the pieces are read exactly).** After any set C of contacts is cut, the pieces of the network are the vertex sets of the
components of G − C, the ring graph without the cut contacts. Every uncut contact needs both of its rings from lag 1, and no contact
needs a ring in another component.

**Theorem 2 (two rings of cuts per handle).** A set C of cut contacts leaves the network in one piece exactly when Z1(C*) meets the
boundaries of G* only in zero, that is when its rings of cuts are independent in the homology H1(S; Z2) of the surface. Since
H1(S; Z2) has dimension 2g, at most 2g independent rings of cuts keep the network in one piece; some 2g do; and any set of cut contacts
carrying more than 2g independent rings of cuts separates it. The most rings of cuts that keep one piece is two per handle.

**Corollary (the torus and genus 2).** On a torus of rings, a ring of cuts round it in each direction together keeps it in one piece,
and a third independent ring of cuts separates it. On a genus-2 network four rings of cuts can keep it in one piece and five never do.
Among genus-2 networks, the regular network of 16 rings with three contacts each (its rotations from GL(2,3)) has every contact
persistent at every lag at every size, by `LOOP-NET-20261108-001A`, Theorem 3.

## Nearest known result

- **Graphs on surfaces.** That a graph cellularly embedded in a surface of genus g stays connected after removing the edges crossed by a
  family of closed curves exactly when the curves are independent in H1(S; Z2), so that at most 2g of them can be cut, is classical
  (cut graphs and tree–cotree decompositions: Mohar and Thomassen, *Graphs on Surfaces*; Eppstein 2003).
- **Classification.** Known-with-delta. The delta is reading it natively: the pieces defined by which contacts need which rings, after
  freezing contacts, are the topological pieces, so the network's surface genus is read across time by cutting.

## Proof of Theorem 1

- **Adjacency is needed at once.** An uncut contact c reads the last cells of its two in-corners, one on each of its rings, so its value
  at lag 1 is the sum of those two cells' first values. So c needs both of its rings at lag 1, and the two rings it joins meet.
- **Needs follow walks of uncut contacts.** By `LOOP-NET-20261108-001A`, Theorem 1, a cell of ring X's corner into contact d appears in
  c's value only through D_cd = Σ_k (K^k)_cd, a sum over walks from d to c. A cut contact reads nothing, so no arc enters it and no walk
  passes through it; and the cells of a corner ending at a cut contact are read by that contact alone. So if c needs X, some walk of
  uncut contacts runs from a contact of X to c. Consecutive contacts on a walk share a ring, and an uncut contact joins two rings of one
  component of G − C, so every ring along the walk, X among them, lies in c's component.

So meeting links the two rings of every uncut contact and never links two components: the pieces are the components. ∎

## Proof of Theorem 2

For a set R of rings, δ(R) is the set of contacts joining a ring of R to a ring outside it. In the cellular chain complex of the
cellularly embedded dual G*, the faces of G* are the rings, and the boundary of the faces of R is δ(R)* (a contact with both rings in R
is counted twice and cancels). Over Z2 the boundary of a set of faces of a closed connected surface vanishes only for no faces or all of
them.
- **One piece exactly when injective.** G − C is disconnected exactly when δ(R) ⊆ C for some nonempty proper set R, that is when C*
  contains the boundary δ(R)* ≠ 0 of a set of faces of G*. A nonzero boundary contained in C* is a cycle of C* that is zero in H1(S; Z2),
  and conversely every such cycle is the boundary of a nonempty proper set of faces. So, with Theorem 1, the network stays in one piece
  exactly when Z1(C*) → H1(S; Z2) is injective.
- **At most 2g.** H1(S; Z2) = Z1(G*)/B1(G*) has dimension 2g, so an injective Z1(C*) has dimension at most 2g, and a cut carrying more
  than 2g independent rings of cuts separates.
- **Some 2g.** Take a spanning tree T of G, a spanning tree T* of G* on dual edges of contacts outside T, and the 2g contacts X left over
  (Euler's formula: |E| − (|V| − 1) − (|F| − 1) = 2g). Cutting the fundamental cycles of X in T* ∪ X leaves T uncut, so G − C is
  connected: 2g rings of cuts, one piece. ∎

## Proof of the corollary

The torus has g = 1 and genus-2 networks g = 2. On the n × n square torus, the contacts h(n − 1, j) and v(i, n − 1) are a ring of cuts
round it in each direction; they meet at one face, their union carries two independent rings of cuts, and G − C is the n × n grid,
connected. A further ring of cuts, such as the contacts h(⌊n/2⌋ − 1, j), adds a third and separates. The 16-ring network is the regular
map {8,3} of genus 2 (orientation-preserving automorphisms GL(2,3), transitive on darts), so Theorem 3 of `LOOP-NET-20261108-001A`
applies with equally spaced contacts. ∎

## Remarks

- **One piece is not full reach.** After a ring of cuts round the n × n torus in each direction, every uncut contact still needs every
  ring for n = 3 to 17 except n = 8 and n = 16, where some contacts on a diagonal never need three rings in the far corner (check 4,
  computed). Before the cut, even sides never reached the antipode (`LATTICE-NET-20261108-001A`); cutting the handle removes that
  cancellation. Heavier cuts, such as tree–cotree systems, keep one piece but rarely keep full reach.
- **Genus-2 lattices of any size.** Double covers of the n × n torus lattice, cross-glued along a slit, are genus-2 lattices of every
  size; the theorems hold on them, but some of their contacts have odd return counts and so do not persist through their witnesses.
- **Not a metric.** Counting rings of cuts counts independent cycles; no length or distance is formed.

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependencies bound by hash | pass |
| 1 | The networks and their genus: square tori (genus 1), the GL(2,3) networks (genus 2 and 6), double covers of the torus lattice (genus 2) | pass: 14 networks |
| 2 | Theorem 1 on random cut sets: native pieces equal the components of the ring graph without the cut contacts | pass: 504 cut sets |
| 3 | Theorem 2: tree–cotree systems give 2g rings of cuts and one piece; adding a further ring of cuts, and random cut sets, give one piece exactly when the cut's dual cycle space injects into homology | pass: 784 families; the most is 2, 4 and 12 at genus 1, 2 and 6 |
| 4 | The torus cut both ways, n = 3 to 17: one piece, and two pieces with a second ring round it; computed: uncut contacts still needing every ring | pass; every uncut contact needs every ring except at n = 8 (108 of 112) and n = 16 (468 of 480) |
| 5 | The genus-2 GL(2,3) networks: a flip at every contact, every return count even, the witnesses holding at every lag (exact), every contact needing every ring | pass |
| 6 | Cell level, exact: the rings each uncut contact needs, read from rows of M^T with the cuts, equal the walk-count reading (tori cut both ways, tree–cotree cuts on genus-2 networks) | pass |

## Nonclaims

- **Networks with law (12, 12)** on rule-60 rings; the pieces use only needs at some lag, and full reach is a separate, computed matter.
- **No distance.**
- **Two-time knots only** (A30).
