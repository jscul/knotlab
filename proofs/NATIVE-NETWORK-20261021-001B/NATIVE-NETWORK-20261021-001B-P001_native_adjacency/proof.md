# Adjacency, routes and separation from allowed states

Status: Proved

Ticket `NATIVE-NETWORK-20261021-001B`, 2026-10-21. It uses:
- `NATIVE-NETWORK-20261021-001A-P001` ("the gate audit");
- the definitions of `KNOT-CIRCUITS-20261020-001B-P001`: a law that composes
  like cycles has, in every system, free sets forming a matroid;
- `CYCLE-TOPS-20261021-001B-P001`, Theorem 2 ("the top lemma"), with the Latin
  and affine structure of tops (`THOMSEN-KNOTS-20261021-001A-P001`, Theorem 2;
  `AFFINE-TOPS-20261021-001B-P001`, Theorem 1);
- `KNOT-SPACE-20261020-001B-P001`: a 3-connected graphic matroid returns its
  graph (Whitney).

It also cites, as classical:
- **matroid connectivity:** "equal, or on a common circuit" is an equivalence
  relation, and a matroid is the direct sum of its classes (Whitney 1935);
- **deletion and contraction** for linear codes (puncturing and shortening);
- **the Galois connection** between polymorphisms and pp-definable relations.

The program's terms are those of `docs/COMMON_VERBIAGE.md`: intrinsic
adjacency, path, native route, native separation, minimal contact-distance.

## Definitions, all read from allowed states

- **The declared substrate.** It is a system S of a law that composes like
  cycles. Its visible distinctions are V, and M is the matroid of its free
  sets.
- **Contacts and ties.**
  - A contact is a circuit of three or more distinctions. Its projection is a
    knot: K1–K3, read with any one of its distinctions as the contact.
  - A tie is a circuit of two. It is a bijection of tops, not a contact.
- **Routes.**
  - A route from x to y is a sequence of circuits C₁, …, C_k with x ∈ C₁ and
    y ∈ C_k, consecutive circuits sharing a distinction.
  - x reaches y when some route joins them. A direct route is a single
    circuit containing both.
- **Bond distance.**
  - s(x, y) is the least size of a circuit containing x and y.
  - The bond distance is δ(x, y) = s(x, y) − 1. Also δ(x, x) = 0, and δ is ∞
    when no circuit contains both.
- **Contact adjacency.** δ(x, y) = 2. Then x and y are two of the three
  distinctions of one atomic contact, which is the minimal contact-distance of
  the protected thesis. A tie gives δ = 1, which is collapse, not contact.
- **Interventions.** Erasing Z forgets the distinctions in Z. Pinning Z fixes
  their values.
- **Native separation of x and y.** Before the intervention x reaches y. After
  it, the intervention has dissolved every route, and the intervened
  substrate's complete set of circuits has none joining them.

## Standard statement

1. **Routes compose into contacts** (Theorem 1). In every declared substrate
   of a law composing like cycles, a route from x to y yields one circuit,
   inside the union of the route's circuits, containing x and y.
   - So reachability is the matroid's connectivity: an equivalence relation
     whose classes are its components.
   - Two not-all-three knots sharing a distinction give a route whose ends lie
     on no common circuit.
2. **Bond distance** (Theorem 2).
   - **It is an extended metric.** δ(x, z) ≤ δ(x, y) + δ(y, z), and it is
     finite exactly within components. The not-all-three pair violates the
     inequality.
   - **Chains.** In a chain of k atoms {e_{i−1}, ℓ_i, e_i}, the circuits are
     exactly the runs {e_i, ℓ_{i+1}, …, ℓ_j, e_j}. So δ(e_i, e_j) = j − i + 1:
     the bond distance grows by one per atom.
3. **Erasing composes, pinning separates** (Theorem 3), in affine laws over
   finite fields. Erasing Z leaves M∖Z. Pinning leaves M/Z, read with
   single-valued distinctions as free. In a chain:
   - erasing the shared distinctions composes the ends into one contact;
   - erasing a private loop separates the ends;
   - pinning a shared distinction separates the ends and ties its two
     neighbours in each atom;
   - pinning a private loop ties its two neighbours, and shortens the
     end-to-end bond by one.
4. **The drawing is not recovered** (Theorem 4). Three parity contacts in a
   triangle have the matroid of K₄. Its 24 automorphisms move every distinction
   to every other, and carry the drawn contact {A, B, k₁} to {k₁, k₂, k₃}, the
   knot that the loop A → B → C → A leaves among the three contacts.
5. **The law fixes no substrate** (Theorem 5). The 3-net of Z_p pp-defines
   every linear subspace, so its substrates realize every F_p-representable
   matroid without loops:
   - in parity, the Fano plane, which is not graphic;
   - in the 3-net of Z₃, U(2, 4), which is not binary.
6. **The answer to the owner's question** (Corollary 6).
   - **What the allowed states fix.** Those of a declared substrate fix contact
     adjacency, routes, native separation and a bond distance, with no drawing.
   - **What they do not fix.** They do not recover the drawing. The law fixes
     none of them until a substrate is declared.

## Nearest known results

- **Connectivity and components of matroids** (Whitney 1935; Tutte). A
  circuit-size measure between two elements is elementary once they are in
  place.
- **Puncturing and shortening.** A linear code punctured at a coordinate has
  the deleted matroid; shortened, the contracted one.
- **Whitney's theorem** on 3-connected graphs. It is used through the space
  epic.
- **The program's earlier corpus.**
  - **Under the earlier contact gate,** Proofs 0022–0027 formed native
    reachability, components, disconnection and route-cut separation, and
    Proof 0051 a valuation metric. There a route was a successor trace.
  - **The space note** (`KNOT-FOUNDATION-20261019-001`, ticket D) found bond
    size growing by one per atom along chains of atoms. Theorem 2 proves this
    for every law that composes like cycles, and adds the triangle inequality.

**Classification: elementary matroid theory; new to the program.** New are
the reading and these facts:
- routes compose into contacts;
- bond distance is a metric wherever composition holds, and fails in a hub;
- erasing and pinning act differently on shared and private distinctions;
- the drawing is not recoverable.

## Theorem 1 (routes compose into contacts)

*Proof.*
1. **The union is connected.** Let C₁, …, C_k be a route, and N the
   restriction of M to their union.
   - A circuit is connected, and lies inside one part of any direct-sum
     decomposition.
   - Consecutive circuits share a distinction, so all the Cᵢ lie in one part
     of any decomposition of N. That part is everything.
   - So N is connected.
2. **One circuit through both ends.** In a connected matroid every two elements
   lie on a common circuit (Whitney). So some circuit of N, inside the union,
   contains x and y.
3. **Reachability is connectivity.** Applied to all routes, this gives the
   statement about reachability.
4. **The not-all-three pair.** Its circuits are {x₁, x₂, e} and {y₁, y₂, e}.
   No circuit contains x₁ and y₁, so the route x₁ – e – y₁ does not compose. ∎

**What changes in the program's picture.** Under the canonical knot test, a
path of contacts is itself a contact: forgetting the shared distinctions
composes it into one knot (the gate audit, Theorem 1(b)). What survives of
the path's length is the size of that knot. The earlier corpus, by contrast,
kept routes as traces.

## Theorem 2 (bond distance)

*Proof of the metric.*
1. **Easy properties.** δ is symmetric, δ(x, x) = 0, and δ(x, y) ≥ 1 for
   x ≠ y.
2. **The triangle inequality.** Let C₁ ∋ x, y and C₂ ∋ y, z be least circuits.
   By Theorem 1, a circuit inside C₁ ∪ C₂ contains x and z. It has at most
   |C₁| + |C₂| − 1 elements, so δ(x, z) ≤ δ(x, y) + δ(y, z).
3. **Finiteness.** δ is finite exactly when x and y lie in one component.
4. **The not-all-three pair.** δ(x₁, e) = δ(e, y₁) = 2, but
   δ(x₁, y₁) = ∞. ∎

*Proof for chains.* Let the atoms be knots K_i on (e_{i−1}, ℓ_i, e_i). Each
shared e_i has the same range in K_i and K_{i+1}.
1. **The top image.** Blurring commutes with the chain: apply the argument of
   the gate audit, Theorem 1(b), atom by atom.
   - Atom i's top image is ē_i = α_i ē_{i−1} + β_i ℓ̄_i + c_i, with α_i and β_i
     group isomorphisms.
2. **Relabelling.** Put ψ₀ = id and ψ_i = ψ_{i−1} ∘ α_i⁻¹. Relabel
   e′_i = ψ_i(ē_i) and ℓ′_i = ψ_i(β_i ℓ̄_i + c_i).
   - These are bijections of each top, so free sets do not change.
   - The chain becomes e′_i = e′_{i−1} + ℓ′_i over one group A.
3. **The fan.** Take a center o, rim vertices p₀, …, p_k, spokes e_i = (o, p_i)
   and rim edges ℓ_i = (p_{i−1}, p_i).
   - The edge values f(head) − f(tail) of potentials f: V → A are exactly the
     solutions of e′_i = e′_{i−1} + ℓ′_i: put f(o) = 0 and f(p_i) = e′_i.
   - So the free sets are the forests of the fan, and the circuits are its
     cycles.
4. **The cycles of the fan.** A cycle meets the rim path in a segment, and must
   pass through o using two spokes. So the cycles are exactly the runs.
5. **The top lemma** makes these the chain's circuits. Hence
   δ(e_i, e_j) = |run| − 1 = j − i + 1. ∎

## Theorem 3 (erasing composes, pinning separates)

Let the law be affine over a finite field: every relation is an affine
subspace. Then pinning keeps the law composing like cycles (the gate audit,
(f)).

*Proof.*
1. **Erasing Z** projects S onto V − Z without changing the ranges of the
   remaining distinctions. A set of them is free in the projection exactly
   when it is free in S. So the free sets are those of M∖Z, and its circuits
   are the circuits of M that avoid Z. This holds in any law.
2. **Pinning z.** S is a coset w + L. Pinning z to an allowed value leaves
   w′ + L₀, where L₀ = {l ∈ L : l_z = 0}.
   - Read on L₀, this is shortening, whose matroid is the contraction M/z. Its
     circuits are the minimal nonempty traces C − z of circuits C of M.
   - **Loops become free.** A one-element trace {y} is a loop of M/z. In the
     pinned substrate y has a single value, and the range-relative convention
     makes it free. So the circuits of the pinned substrate are the minimal
     traces with two or more elements.
   - **In the program's terms,** pinning z freezes every distinction tied to z:
     those lose their open distinctions.
3. **Chains,** through the fan of Theorem 2.
   - **Erasing the spokes e₁, …, e_{k−1}** leaves one cycle,
     o, p₀, …, p_k, o. So the ends lie on the single contact
     {e₀, ℓ₁, …, ℓ_k, e_k}.
   - **Erasing a rim edge ℓ_i** destroys every cycle through both end spokes.
     The only such cycle is the full run, and it contains ℓ_i.
   - **Pinning a spoke e_i** merges o with p_i, which becomes a cut vertex. So
     the ends fall into different blocks, and e_{i−1} ∥ ℓ_i and ℓ_{i+1} ∥ e_{i+1}
     become parallel: ties.
   - **Pinning a rim edge ℓ_i** merges p_{i−1} with p_i. So e_{i−1} ∥ e_i, and
     the full run loses ℓ_i: δ(e₀, e_k) drops from k + 1 to k.
4. **Native separation.** Erasing a private loop, or pinning a shared
   distinction, is a native separation of the chain's ends.
   - **Before:** the ends were joined by the full run.
   - **Every route is dissolved.** A route from e₀ to e_k must use a run that
     crosses the cut, since the runs on either side share no distinction.
     - When ℓ_i is erased, every crossing run contains ℓ_i.
     - When e_i is pinned, every crossing run either contains e_i or is no
       longer minimal once e_i is fixed. It contains the shorter trace that
       ends at e_i.
   - **After:** the complete circuits of the intervened substrate join them by
     none.
   - **The other two interventions are not separations.** Erasing a shared
     distinction composes. Pinning a private loop collapses, tying its two
     neighbours. ∎

**Duality.** Deletion and contraction exchange under matroid duality. In the
program's terms:
- **Shared distinction:** forgetting it composes the contacts through it, and
  fixing it cuts them.
- **Private loop:** the roles swap.

## Theorem 4 (the drawing is not recovered)

Take loops A, B and C, with parity contacts k₁ on (A, B), k₂ on (B, C) and
k₃ on (C, A).
- **Every notion above comes from allowed states.** Contacts, routes, bond
  distance and separations are defined from allowed states. So two
  presentations with the same allowed states give the same ones.
- **The triangle's matroid is that of K₄.**
  - Its circuits are the four triangles {A, B, k₁}, {B, C, k₂}, {C, A, k₃} and
    {k₁, k₂, k₃}, and three 4-cycles.
  - Label A, B and C as the spokes from an apex 4, and k₁, k₂ and k₃ as the
    outer triangle on 1, 2, 3.
- **Its 24 automorphisms are transitive.** They are the symmetries of K₄. One
  of them exchanges the apex with a vertex of the outer triangle. It carries the
  drawn contact {A, B, k₁} onto {k₁, k₂, k₃}.
- **So the drawing is lost.** Which circuits were drawn as contacts and which
  arise from the loop, and which distinctions were drawn as loops and which as
  contacts, are not properties of the allowed states.
- **What the allowed states return.** The space epic's recovery gives K₄, with
  an apex the drawing does not show. ∎

## Theorem 5 (the law fixes no substrate)

Let p be prime. The 3-net of Z_p is the law {z = x + y}; for p = 2 it is
parity.

*Proof.*
1. **The polymorphisms are linear.** A polymorphism preserves the graph of
   addition, so it is additive, and over F_p additive maps are linear.
   Conversely, every linear map Σ cᵢxᵢ preserves the relation.
2. **So every linear subspace is pp-definable.** By the Galois connection, the
   pp-definable relations are the relations invariant under all linear maps:
   the linear subspaces.
3. **Realizing a matroid.** For a matroid represented over F_p by a matrix
   with no zero column, the row space is a substrate. Its free sets are the
   independent sets of the columns.
4. **The two examples.**
   - **The Fano plane.** It has rank 3, seven elements and no 2-circuits. It is
     connected, so a graph realizing it could be taken connected. That graph
     would need four vertices and seven edges with no parallel pair, and K₄
     has only six. So it is not graphic.
   - **U(2, 4).** Its 3-circuits {a, b, c} and {a, b, d} have symmetric
     difference {c, d}, which contains no circuit. So it is not binary. ∎

**What this means.** A law composing like cycles fixes how adjacency, routes,
separation and bond distance behave, by Theorems 1–3. It does not fix which
ones occur:
- Parity's substrates include adjacency structures of the Fano plane, which no
  graph has.
- Every graph's cycle matroid occurs too.
- Question 9, a law that selects its own substrate, is untouched.

## Corollary 6 (the answer to the owner's question)

**Within a declared substrate of a law composing like cycles,** the allowed
states, with no drawing, fix:
- contact adjacency;
- routes, which compose into contacts;
- native separation, by erasing private loops or pinning shared distinctions;
- an extended bond distance.

**What they do not fix:** the drawing, meaning which contacts were written,
which distinctions are loops, and the drawn graph.

**What the law does not fix:** the substrate.
- **The guardrail's prerequisites are met.** Contact-supported adjacency,
  native paths and native separation are constructed in the declared
  substrate. That is the precondition for an extended distance.
- **The bond distance is that candidate.**
  - It is relative to the declared substrate.
  - It is computed from bond sizes, not from values.
  - It is a metric where composition holds.

## What this does not show

- **No space created by a law.** The substrate is declared.
- **The bond distance is no geometry.** It brings no coordinate, dimension,
  continuum or embedding, and it is not the program's minimal contact-distance
  (that is one atomic contact, δ = 2).
- **Theorem 3 is limited.** It is proved for affine laws over finite fields.
  For other laws that compose like cycles with constants, pinning was not
  analysed.
- **No physical claim.**

## Checks

`check.py` writes `result.json` in about three seconds. All checks pass, and
all six controls are rejected.

- **Theorems 1 and 2, random systems.** 40 random systems each were sampled
  from 13 laws: the eleven census laws, the 3-net of Z₃, and x + y + z = 0 over
  F₅. In all 469 nonempty systems:
  - every one of the 2,043 pairs joined by a route lies on a common circuit;
  - the bond distance satisfies the triangle inequality;
  - its finite classes are the route classes.

  The not-all-three pair fails both.
- **Theorem 2, chains.** Eight laws were tested:
  - parity, Z₃, the 3-net of Z₃, the lift, K₄, the 3-net of Z₄, z = 2x + y over
    F₅, and the K₆ lift;
  - with k from 1 to 4 atoms (to 3 on five and seven values).

  In every chain the circuits are exactly the runs, and δ(e_i, e_j) = j − i + 1.
- **Theorem 3.**
  - **Erasure and pinning.** Random systems were drawn of affine laws over F₂,
    F₃ and F₅, 50 each.
    - Erasing a variable leaves exactly the circuits avoiding it, in 150 of
      150 systems.
    - Pinning it leaves exactly the minimal traces with two or more elements,
      in 454 of 454 pinned systems.
  - **A chain of four atoms** in each of the three laws: all four statements
    hold, for every pinned value.
- **Theorem 4.** The triangle network's seven circuits form M(K₄). Its 24
  automorphisms are transitive, and one carries {A, B, k₁} to {k₁, k₂, k₃}.
- **Theorem 5.**
  - **Parity.** It realizes the Fano plane: 14 circuits, 7 lines, rank 3, no
    ties.
  - **The 3-net of Z₃.** It realizes U(2, 4): four 3-circuits.
- **Controls,** each rejected:
  - "routes compose in every substrate";
  - "bond size minus one is a metric in every substrate";
  - "erasing a chain's shared distinctions separates its ends";
  - "pinning a private loop separates a chain's ends";
  - "allowed states tell drawn contacts from a loop's knot";
  - "the parity law fixes a graph".
