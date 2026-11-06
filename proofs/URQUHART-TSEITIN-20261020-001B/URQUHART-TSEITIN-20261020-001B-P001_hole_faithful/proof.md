# Re-querying and proof size for Tseitin formulas: Urquhart's conjecture, the read-2 barrier, and hole-faithful refutations

Status: Proved

Theorems 1 and 4, Corollaries 2 and 6, and Propositions 3 and 5 are proved
below. Urquhart's conjecture itself is not resolved.

Ticket `URQUHART-TSEITIN-20261020-001B`, 2026-10-20. It builds on:
- `CELL-SIZE-20261020-001B-P001` and `GENERAL-SIZE-20261020-001B-P001`, for the
  cases where the conjecture holds;
- `SOS-SIZE-20261020-001B-P001`, for the carving bound on resolution width.

## Background

- **The conjecture.** Urquhart's conjecture says that regular resolution
  polynomially simulates resolution on Tseitin formulas. Itsykson, Riazanov
  and Smirnov list it as open in their SAT 2022 talk.
- **Regular resolution.** The same authors prove that regular refutations need
  size 2^{Ω(tw)}, up to a polynomial factor.
- **The width version.** Galesi, Talebanfard and Torán (SAT 2018; ACM ToCT
  2020) characterize resolution width, variable space and depth for Tseitin
  formulas by a cops-and-robber game. The game can be played monotonically, so
  these measures equal their regular-resolution values. For size, nothing of
  the kind is known.

## Setting

- **The formula.** G = (V, E) is connected, and c is a charge with odd total.
  T(G, c) is in the clause encoding. A clause is identified with the partial
  assignment β_C that falsifies it, and Q_C is its set of variables (edges).
- **Critical assignments and holes.** A *critical assignment* violates exactly
  one vertex constraint; that vertex is its *hole*.
- **The region of a clause.** C is *consistent* if, under β_C, exactly one
  component of G − Q_C has boundary parity different from its charge. That
  component is the *region* K_C. Every critical assignment that falsifies C
  has its hole in K_C.
- **Walks.** A refutation's derived clauses each come from two premises. The
  *walk* of an assignment α starts at the empty clause and repeatedly moves to
  the premise α falsifies, until it reaches an axiom.
- **Steps and forgetting.** A *step* goes from a clause D to its premise P on
  the pivot x. The variables of D missing from P are *forgotten* at the step.
  The *region after reading x* is the odd component of G − (Q_D ∪ {x}) under
  β_D extended by P's value of x.
- **Free dimension.** fd(Q) is the dimension of the cycle space of G projected
  onto Q, which equals |Q| − (number of components of G − Q) + 1.

## Statements

**Theorem 1 (the conjecture is the open problem).** Let 𝒢 be a family of
connected graphs of maximum degree at most Δ, each with an odd charge. Then
regular resolution polynomially simulates resolution on these Tseitin
formulas if and only if, for some c > 0, every resolution refutation of
T(G, c) on G ∈ 𝒢 has size at least 2^{c·tw(G)}/n^c.

**Corollary 2 (where it holds).** Urquhart's conjecture holds on the following
bounded-degree families:
- graphs with cell systems of bounded parameters and |U| ≤ ε·tw;
- graphs excluding a fixed minor, planar graphs included;
- graphs with tw ≥ εn;
- graphs with a compact topological minor of nearly full treewidth, in the
  sense of `GENERAL-SIZE-20261020-001B-P001`.

**Proposition 3 (the read-2 barrier).** Let the charge have even total.
- A deterministic branching program of size 2m + 2 computes T(G, c) and reads
  each variable at most twice on every path.
- Itsykson et al. prove their regular bound by turning a regular refutation
  into a read-once branching program and bounding that program's size.
- Once a variable may be read twice, programs of size O(m) exist. So
  branching-program size alone cannot prove Urquhart's conjecture.

**Theorem 4 (hole-faithful refutations).** Call a refutation *hole-faithful*
if, at every step between consistent clauses, no forgotten variable is an edge
touching the region after reading the pivot.

Let G be 2-edge-connected, and let W ⊆ V be a set of w ≥ 2 vertices with
|δ(X)| ≥ min(|X ∩ W|, |W ∖ X|) for every X ⊆ V. Then for 0 < ε < 1/4, every
hole-faithful refutation of T(G, c) has at least (1 − 4ε)·2^{εw/2} clauses.

Graphs of treewidth t contain such sets with w = Ω(t), since well-linked sets
(Reed) qualify: vertex-disjoint paths are edge-disjoint. So hole-faithful
refutations need size 2^{Ω(tw)}.

**Proposition 5 (the standard refutations are hole-faithful).** Every
Davis–Putnam refutation (variable elimination in any order) of a Tseitin
formula is regular and hole-faithful. Eliminating along an optimal
elimination order of the line graph gives one with 2^{O(Δ·tw)}·m clauses. So
for bounded degree, hole-faithful size is 2^{Θ(tw)} up to polynomial factors.

**Corollary 6 (what a smaller refutation must do).** A refutation of size
2^{o(tw)} on bounded-degree graphs, if one exists, must do both of the
following:
- re-read some variable on some path (by Itsykson et al.);
- take a step that forgets a variable at the hole's region, either by
  recontaminating (dropping a boundary edge) or by dropping a chord
  (Theorem 4).

## Proofs

### Theorem 1

- **The two bounds on regular resolution.** Itsykson, Riazanov and Smirnov give
  Reg(G) ≥ 2^{c₁·tw}/n^{c₁}. Proposition 5 gives Reg(G) ≤ 2^{c₂·tw}·n^{c₂}.
  The formula's size is poly(n), and S ≤ Reg.
- **(⇐)** If S ≥ 2^{c·tw}/n^c, then Reg ≤ (S·n^c)^{c₂/c}·n^{c₂}.
- **(⇒)** If Reg ≤ (S·n)^a, then S ≥ Reg^{1/a}/n ≥ 2^{c₁·tw/a}/n^{c₁/a + 1}. ∎

### Corollary 2

Each family has general-resolution size 2^{Ω(tw)}:
- **Cell systems:** Theorem 1 of `CELL-SIZE-20261020-001B-P001`, with the
  tangle of order cvw ≥ (tw + 1)/6;
- **Excluded minors:** Corollary 6 there;
- **tw ≥ εn:** size–width (Ben-Sasson–Wigderson);
- **Compact minors:** the compact case of Theorem 3 of
  `GENERAL-SIZE-20261020-001B-P001`.

Theorem 1 then applies. ∎

### Proposition 3

Check the vertices one after another. For each vertex v, a two-state chain
reads the edges of E(v) and tracks their parity. A wrong parity leads to the
rejecting sink; otherwise the next vertex starts.
- Every edge lies in two stars, so it is read at most twice on any path.
- The program has 2m + 2 nodes.

Applied to the satisfiable formulas that Itsykson et al. obtain, programs of
this size exist as soon as two reads are allowed. ∎

### Theorem 4

Draw the hole h uniformly from W, then draw α uniformly among the critical
assignments with hole h. Fix a hole-faithful refutation and write μ(K) for
|K ∩ W|/w.

**Lemma P (the hole stays uniform).** Let C be a clause on a walk, and condition
on the walk's path up to C. Then h is uniform on K_C ∩ W.

*Proof.*
- The path is determined by α's values on R, the variables read along it.
- By faithfulness, every variable in R ∖ Q_C was forgotten at a step where it
  did not touch the region after reading. Regions never grow, because a
  faithful step leaves the region after reading unchanged. So that variable
  does not touch K_C either.
- Hence K_C is a whole component of G − R.
- For h, h′ ∈ K_C, adding a path from h to h′ inside K_C maps critical
  assignments with hole h to those with hole h′. It fixes every value on R. ∎

**Lemma F (no skipping).** Along the walk, μ(K) starts at 1 and ends at 1/w.
Let τ be the first clause with μ(K) ≤ 1/2. Then Pr[μ(K_τ) < ε] ≤ 4ε.

*Proof.*
- The region shrinks at τ only because the pivot splits K_{τ−1} into two parts.
- Given the path, Lemma P puts h in each part with probability
  μ(part)/μ(K_{τ−1}).
- μ(K_{τ−1}) > 1/2, and at most two parts have μ below ε. So the conditional
  probability is at most 2ε/(1/2). ∎

**Lemma B (balanced clauses are rarely falsified).** If ε ≤ μ(K_C) ≤ 1/2, then
Pr[α falsifies C] ≤ 2^{−εw/2}.

*Proof.*
- **Many boundary edges.** By the linkage of W, |δ(K_C)| ≥ εw.
- **Large free dimension.** Q_C ⊇ δ(K_C), and fd is monotone in its argument.
  G − δ(K_C) consists of K_C plus components of G − K_C. G is 2-edge-connected,
  so each of those has at least two boundary edges, and there are at most
  |δ(K_C)|/2 of them. So fd(Q_C) ≥ |δ(K_C)|/2.
- **The probability.** Given any hole, α restricted to Q_C is uniform on a
  coset of size 2^{fd(Q_C)}. ∎

**Conclusion.**
- By Lemma F, with probability at least 1 − 4ε the walk passes through a clause
  with μ(K) ∈ [ε, 1/2].
- The walk passes through a clause only if α falsifies it.
- A union bound with Lemma B over such clauses gives at least
  (1 − 4ε)·2^{εw/2} of them. ∎

### Proposition 5

On Tseitin formulas, Davis–Putnam elimination is edge contraction.

- **The invariant.** At every stage the clauses are grouped by super-vertex: a
  set S of vertices connected by eliminated edges. S has its boundary δ(S) and
  its uneliminated internal edges L_S, the self-loops. S's clauses exclude
  exactly the assignments of δ(S) ∪ L_S with the wrong parity for S.
- **Merging.** Eliminating an edge x between S₁ and S₂ produces exactly S's
  clauses, for S = S₁ ∪ S₂.
  - For each wrong-parity assignment, exactly one pair of premises resolves to
    exclude it. Pairs that disagree on another shared edge are tautological
    and are dropped.
  - Eliminating a self-loop just removes it.
- **Regions.** A consistent clause of S has region S. S is connected through
  eliminated edges, none of which are clause variables, and its parity is
  wrong by construction.
- **Faithfulness.**
  - At a merge step, reading x leaves the hole in the part S_j of wrong parity.
    That is the region after reading, and P is S_j's clause.
  - The forgotten variables are boundary edges of S at the other part and that
    part's self-loops. None touches S_j.
  - At a self-loop step nothing is forgotten.
- **Regularity.** Pivots on a path from the root follow the elimination order
  backwards, so each appears at most once.
- **Size.** The variables of a Davis–Putnam clause created when eliminating x
  are neighbours of x in the induced graph of the elimination order on the
  primal graph, which here is the line graph L(G).
  - Along an optimal order, every clause has at most
    tw(L(G)) + 1 ≤ Δ·(tw(G) + 1) variables. (Replace each vertex of a bag by
    its incident edges.)
  - Each stage then creates at most 2^{Δ(tw+1)} clauses, over m stages. ∎

### Corollary 6

- **Regular refutations** need 2^{Ω(tw)} (Itsykson, Riazanov and Smirnov).
- **Hole-faithful refutations** need 2^{Ω(tw)} (Theorem 4).
- **Non-faithful steps bias the hole.** The checks show that a single
  non-faithful step already makes the hole's posterior non-uniform on the
  clause's region, at many nodes. Lemma P's argument then fails: the walk knows
  more about the hole than its clause states, and the next split can skip the
  balanced scale. ∎

## Checks

`check.py` runs in about 1 s on K₄, the prism, K₃,₃, the cube, the Wagner
graph, the 3 × 3 grid and the Petersen graph.

| Check | Result |
| --- | --- |
| Carving refutations (43–219 clauses) and three Davis–Putnam refutations per graph (47–407 clauses): validity | every derived clause is the non-tautological resolvent of its premises |
| Hole-faithfulness, at every step between consistent clauses | no violations |
| Every critical assignment walked: regions never grow; the hole is uniform given each walk prefix, and at each node | holds for every refutation |
| Fraction of walks through each clause, against (\|K_C\|/n)·2^{−fd} | within the bound everywhere |
| Control: the second step forgets a variable at the hole's region, with every needed clause derived by lifted Davis–Putnam elimination | one faithfulness violation; the hole becomes non-uniform at 40 of 215 walk prefixes (prism), 96 of 527 (cube), 63 of 249 (3 × 3 grid) and 248 of 1,359 (Petersen) |
| Read-2 programs for an even charge | correct on all assignments, at most 2 reads per variable, size 2m + 2 |

## What this does and does not show

- **Not shown.** Urquhart's conjecture, and general-resolution 2^{Ω(tw)}.
  Theorem 1 shows they are the same problem for bounded degree, and the
  remaining families are those of `GENERAL-SIZE-20261020-001B-P001`'s barrier.
- **Theorem 4 against the regular bound.** Hole-faithful refutations need not
  be regular: they may re-read variables away from the hole's region. Regular
  refutations need not be hole-faithful. The two lower bounds cover different
  classes, and both contain the Davis–Putnam refutations.
- **The hole picture's diagnosis.** A refutation beats 2^{tw} only if its walks
  carry information about the hole that their clauses no longer state, and it
  can use that information only by reading variables again. The graph-searching
  analogue is recontamination. Monotonicity theorems say that recontamination
  does not help the number of searchers; whether it helps the number of
  positions is exactly what is open.

## Novelty

- **Method.** The argument is Haken's counting method in Urquhart's
  probabilistic form, run with a hole drawn from a well-linked set and a
  faithfulness condition in place of expansion.
- **Search.** A targeted search on 2026-10-20 found:
  - Urquhart's conjecture listed as open;
  - the monotone cops-and-robber characterization of width, space and depth;
  - no lower bound for a class defined like hole-faithful refutations.
- **Folklore.** Theorem 1, Corollary 2 and Proposition 3 are short
  consequences of known results, and may be folklore.
- **Review.** No human expert has reviewed this.
