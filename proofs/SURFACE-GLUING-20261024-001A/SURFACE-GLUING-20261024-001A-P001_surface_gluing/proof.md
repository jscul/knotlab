# Native gluing builds surfaces, and four knots see only the surface

Status: Proved

Ticket `SURFACE-GLUING-20261024-001A`, 2026-10-24.

**What it uses:**
- from `NATIVE-NETWORK-20261021-001` (closed): two knots sharing a distinction compose into one knot by quantifying it away;
- from `EMERGENCE-BITS-20261021-001` (closed): a network with hidden joints holds at most one bit per independent loop, and only parity
  fills every loop. This is used only for comparison;
- the canonical guardrail of `AGENTS.md`: a distinction tied independently into several relations is a common hub, not a touch;
- classical background, cited and not used as a proof step: two-dimensional topological field theories correspond to commutative
  Frobenius algebras (Abrams 1996; Kock 2004).

## Standard statement

**Setting.**
- **Relations.** Take a Boolean relation R on three variables.
  - It is *symmetric* if permuting its variables preserves it. A symmetric R is fixed by its set W ⊆ {0, 1, 2, 3} of allowed numbers
    of ones.
  - It is a *knot* when every pair of variables is unconstrained and R is not the full cube. There are 34 knots.
- **Networks.** A *hub-free network* of K copies of R identifies some variables of the copies in pairs: each identified pair is a
  shared variable, and every variable of a copy is either paired with exactly one other variable or left open (a *leg*). The copies
  with the pairings form a connected multigraph in which every node has degree three, counting a loop twice and a leg once. The
  multigraph may have loops and multiple edges.
- **Glued results.** The *glued result* of a network is the set of assignments to its b legs that extend to the shared variables so
  that every copy holds. The *witness count* of a leg assignment is its number of extensions.
- **Topological gluing.** Gluing R is *topological* if the glued result of every connected network depends only on its numbers of
  copies and legs and is symmetric in the legs. It is *topological with counts* if the same holds for witness counts.

**Theorem 1 (surfaces).**
- **(a) Three places give surfaces.** Glue one pair of pants (a sphere with three holes) per copy along the shared variables.
  - A connected hub-free network of K copies with b legs then becomes a compact connected orientable surface with Euler
    characteristic −K and b boundary circles.
  - Its genus g = (K − b + 2)/2 equals the cycle rank of the multigraph.
- **(b) Two places give lines and loops.** A hub-free network of two-variable relations is a disjoint union of paths and cycles.
- **(c) A hub is not a surface point.** At a variable shared by three copies, three sheets meet along one circle.

**Theorem 2 (a local criterion).** Gluing a symmetric three-place relation is topological exactly when two copies glued along one
variable give a result symmetric in its four legs. The same holds with witness counts in place of results.

**Theorem 3 (which symmetric relations see only the surface).** Among the 16 symmetric three-place relations, gluing is topological
with counts exactly for:
- the empty relation and the full cube;
- the constants "all 0" and "all 1";
- all-equal;
- the two parity relations, "even number of ones" and "odd number of ones";
- the two "no lone value" relations: W = {0, 1, 3}, no lone 0, and W = {0, 2, 3}, no lone 1.

As relations, though not with counts, the two frozen relations W = {0, 1, 2} ("not all ones") and W = {1, 2, 3} ("not all zeros") also
glue topologically. The remaining five do not glue topologically: W = {1}, {2}, {0, 1}, {2, 3}, and not-all-equal {1, 2}. For a
connected network with K copies, b legs and genus g:
- **Parity with total κ.** A leg assignment β is allowed exactly when its number of ones is congruent to Kκ modulo 2, and each allowed
  β has 2^g witnesses. So every handle doubles the witnesses: one hidden bit per handle.
- **No lone 0.** On a sphere (g = 0), β is allowed exactly when it does not have exactly one 0. On any surface with a handle, every β is
  allowed. The witness counts form a two-dimensional theory with handle matrix H = [[3, 1], [1, 2]] in the basis (0, 1).
  - A closed surface of genus g has tr H^(g−1) witness assignments: 5, 15, 50, … for g = 2, 3, 4.
  - The eigenvalues of H are (5 ± √5)/2, and their ratio is the square of the golden ratio.
  - No lone 1 is the same with 0 and 1 exchanged.
- **Frozen.** Once two copies are glued, every β is allowed: set every shared variable to 0 (for "not all ones") or 1 (for "not all
  zeros"). The witness counts depend on more than the surface.
- **All-equal.** Only the two constant leg assignments are allowed, each with one witness, or two witnesses in all when b = 0.

**Corollary 4 (the knots).** Of the 34 knots:
- 27 are not symmetric, so already a single copy is not invariant under the homeomorphisms of a pair of pants;
- the seven symmetric ones are the two parity knots, the two no-lone knots, the two frozen knots and not-all-equal.

So exactly four knots glue topologically with counts. Only the parity knots carry information through every surface: their leg
relation is never full, and their handles are hidden bits. The no-lone knots see only whether the surface is a sphere, and count
handles through H. The frozen knots forget once two copies meet, and not-all-equal depends on the arrangement. All-equal, the hub,
glues topologically but is not a knot.

## Nearest known result

- **Theorem 1.** Classical: pants decompositions and their dual cubic graphs (Hatcher and Thurston 1980).
- **Theorem 2.** Its proof is generalized associativity for trees followed by closing handles. That is the elementary half of the
  classical theorem that two-dimensional topological field theories are commutative Frobenius algebras (Abrams 1996). Frobenius
  objects in the category of relations are classified (Heunen, Contreras and Cattaneo 2013, groupoids; Mehta and Zhang 2020). The
  parity case is mod-2 homology of surfaces.
- **Theorem 3 and Corollary 4.** New to the program: the census of Boolean three-place relations and knots under topological gluing,
  and the golden-ratio handle of the no-lone knots. Novelty: `candidate-local-delta`. A Frobenius-object census on a two-element set
  may exist in the literature; this was not found in a bounded scan (`research/SURFACE-GLUING-20261024-001/scan.md`).

## Proof

### Theorem 1

- **(a)** A pair of pants has Euler characteristic −1, and gluing along circles leaves the Euler characteristic additive. So the
  surface has χ = −K. Its boundary circles are the legs. Gluings can be chosen orientation-reversing, which makes the surface
  orientable, and it is connected exactly when the multigraph is.
  - From χ = 2 − 2g − b we get g = (K − b + 2)/2.
  - The multigraph has (3K − b)/2 edges, so its cycle rank is (3K − b)/2 − K + 1 = (K − b)/2 + 1 = g.
- **(b)** A two-variable relation contributes degree two to the multigraph, so every node has degree at most two.
- **(c)** Three pants glued along one circle meet in three sheets. No neighbourhood of a point of that circle is a disc. ∎

### Theorem 2

Work over the Boolean semiring for glued results and over the natural numbers for witness counts. The result of a network is the
contraction of copies of R, as a tensor, over its shared variables.

- **(⇒)** Two copies glued along one variable form a network. Permuting its legs gives a network with the same numbers of copies
  and legs.
- **(⇐) Trees.** Let T_1 = R, and let T_k be T_{k−1} with one further copy attached to its last leg. By induction on k, T_k is
  symmetric in its k + 2 legs and equals the result of every tree-shaped network of k copies.
  - **The induction step.** By the induction hypothesis T_{k−1} is the result of any tree of k − 1 copies, so it can be written with
    any two chosen legs, x and e, on one copy f.
  - Attaching a copy at e therefore contracts two copies, f and the new one, along e. That contraction is the four-leg result, which
    is symmetric by assumption. So T_k is symmetric in x and the two new legs.
  - Together with the symmetry of T_{k−1}, T_k is fully symmetric.
  - A tree of k copies has a leaf copy, and removing it shows that the tree's result is T_k.
- **(⇐) Handles.** A connected network has a spanning tree of copies. The g shared variables outside the tree become 2g extra legs of
  that tree, and the network's result contracts them in pairs. By the symmetry of T_K, the result depends only on g and b, and it is
  symmetric in the remaining legs. ∎

### Theorem 3

- **Parity.** The copies give K linear equations over GF(2).
  - Their sum is Kκ = (number of ones on the legs) + 2 · (shared variables), so a leg assignment is allowed only if its ones are
    congruent to Kκ.
  - The equations on the shared variables have the incidence matrix of a connected multigraph, of rank K − 1. Every allowed
    assignment therefore has 2^(edges − K + 1) = 2^g extensions.
- **No lone 0.** Write Z for the set of variables equal to 0. The relation says |Z| ≠ 1 on each copy.
  - **Gluing one shared variable.** Glue relations "|Z(X, e)| ≠ 1" and "|Z(Y, e)| ≠ 1" along e.
    - The value e = 0 needs Z(X) and Z(Y) nonempty.
    - The value e = 1 needs |Z(X)| ≠ 1 and |Z(Y)| ≠ 1.
    - Either case holds exactly when |Z(X ∪ Y)| ≠ 1. So trees keep "no lone 0" on their legs.
  - **A handle.** Gluing two legs of the same network to each other: e = 0 adds two to |Z| and always succeeds. So every handle makes
    the relation full.
  - **Counts.** The four-leg count criterion holds by the check, so the counts are topological (Theorem 2). A closed surface of genus
    g is a ring of g − 1 two-holed tori. Each torus contributes the matrix of witness counts on its two legs, which is H, so the count
    is tr H^(g−1).
  - **No lone 1** follows by exchanging 0 and 1.
- **Frozen.** In a connected network with K ≥ 2, every copy has a shared variable, and the stated constant on the shared variables
  satisfies every copy. The check gives two networks of genus 1 with two legs whose count profiles differ.
- **All-equal.** Connectivity forces every variable equal.
- **The rest.** For the remaining five, two glued copies give a result that is not symmetric in its four legs. For not-all-equal the
  excluded assignments are 0011 and 1100, with legs 1–2 on one copy and 3–4 on the other. By Theorem 2 they do not glue
  topologically. ∎

### Corollary 4

A homeomorphism of a pair of pants can permute its three boundary circles arbitrarily. So topological gluing requires a single copy
to be symmetric, which excludes the 27 asymmetric knots. The census of the 34 knots finds seven symmetric ones, with allowed weights
{0, 2}, {1, 3}, {0, 1, 3}, {0, 2, 3}, {0, 1, 2}, {1, 2, 3} and {1, 2}. Theorem 3 sorts them as stated. ∎

## Checks

`check.py` uses the standard library only. It enumerates every connected hub-free network with up to six copies, up to isomorphism:
2, 5, 7, 22, 43 and 141 shapes for one to six copies. Over these it confirms:
- the census of Theorem 3, as relations and with counts, for all 16 symmetric relations;
- that the four-leg criterion of Theorem 2 agrees with the census in every case;
- the parity formula on every network;
- the no-lone formulas, including the closed counts 5, 15 and 50 for genus 2, 3 and 4;
- that the frozen relations are full once glued, with a certificate that their counts are not topological;
- the all-equal formula;
- the knot census: 34 knots, 27 not symmetric, seven symmetric.

**Controls.**
- **A hub fits no surface.** Three parity copies sharing one variable, each with two legs, would need genus −1/2. Their result allows
  16 of the 64 leg assignments, not the 32 of a single parity constraint.
- **One copy is not enough.** A criterion using one copy instead of two would accept not-all-equal.
- **Two places.** Among symmetric two-variable relations, only equality, the constants and the full relation give a path result
  independent of the path's length.

## What this does not show

- **Gluing along more than one variable at once.** Only gluing along single variables is covered. Cells of dimension three would need
  gluing along whole sets of variables, and that is not studied here.
- **Topological gluing with roles.** Asymmetric knots might glue topologically if their places had roles, for example a contact place
  glued only to contact places. That is not studied.
- **Which surface occurs.** No surface is selected: every network exists, and the theorems say what each law makes of each network.
