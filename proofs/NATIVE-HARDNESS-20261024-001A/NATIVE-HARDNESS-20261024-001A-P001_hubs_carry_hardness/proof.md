# Hubs carry hardness

Status: Proved

Ticket `NATIVE-HARDNESS-20261024-001A`, 2026-10-24.

**What it uses:**
- the canonical guardrail of `AGENTS.md`: a distinction tied independently into several relations is a common hub, not one touch;
- from `NATIVE-NETWORK-20261021-001` (closed): two knots sharing a distinction compose by quantifying it away;
- from `BASE-THREE-20261021-001` (closed): the regimes of laws on bits, and that NP-hardness needs transmission and memory;
- external theorems, cited as hypotheses and not admitted as local evidence (`docs/EXTERNAL_EVIDENCE_POLICY.md`):
  - **(KKR)** Kazda, Kolmogorov and Rolinek, *Even delta-matroids and the complexity of planar Boolean CSPs*, ACM Trans.
    Algorithms (2019), arXiv:1602.03124, Theorem 11: an edge constraint problem whose constraints come from an efficiently
    coverable class of delta-matroids is solvable in polynomial time;
  - **(F)** Feder, *Fanout limitations on constraint systems*, Theoret. Comput. Sci. 255 (2001), as stated in KKR Theorem 7: if Γ
    contains the constants, CSP(Γ) is NP-hard and some relation of Γ is not a delta-matroid, then the edge problem over Γ is
    NP-hard;
  - **(GF)** the general factor problem (Lovász 1972; Cornuéjols 1988): it is polynomial when every allowed degree set has gaps of
    length at most one, and NP-complete when the degree set {0, 3} occurs, together with {1};
  - **(S)** Schaefer's theorem: with constants, CSP(Γ) for a Boolean language Γ is polynomial when every relation is affine,
    every one is Horn, every one is dual-Horn, or every one is bijunctive; otherwise it is NP-complete.

## Standard statement

**Setting.**
- **Edge problems.** An *edge constraint problem* over a set Γ of Boolean relations is a constraint satisfaction instance in which
  every variable occurs in exactly two constraints.
- **Knots.** A *knot* is a relation on three bits in which every pair of variables is unconstrained, other than the full cube. There
  are 34 knots.
- **Networks.** A *network* of knots is an instance whose constraints are knots, possibly with some variables pinned to 0 or 1.
  - It is *hub-free* if every variable occurs in at most two knots.
  - A *hub* is a variable occurring in three or more.

**Theorem 1 (census).**
- **The knots.** All 34 knots are delta-matroids. Exactly the two parity knots are even. All 34 are coverable in the sense of KKR
  (Definitions 9 and 10).
- **All three-place delta-matroids.** All 155 nonempty delta-matroids on three variables are coverable, and so are the unary
  relations: the constants and the free relation {0, 1}.
- **The hub relation.** All-equal on three variables, {000, 111}, is not a delta-matroid. As a degree set it is {0, 3}, with a gap of
  length two.
- **Schaefer classes.** Two knots are affine (the parity knots), eight are Horn, eight are dual-Horn and none is bijunctive. The other
  16, not-all-equal among them, are NP-hard with constants.
- **Symmetric knots.** For the seven symmetric knots, the allowed numbers of ones are {0, 2}, {1, 3}, {0, 1, 3}, {0, 2, 3}, {0, 1, 2},
  {1, 2, 3} and {1, 2}, each with gaps of length at most one.

**Theorem 2 (reductions).**
- **(a) Hub-free networks are edge problems.** Give each variable that occurs in one knot the unary free constraint, and replace each
  pinned variable by a unary constant constraint. The result is an edge constraint problem over the knots, the constants and the free
  relation, with the same solutions on the original variables.
- **(b) A hub is all-equal.** A network with hubs is equisatisfiable with an edge problem over the knots, the constants, the free
  relation and all-equal: split each variable into one copy per occurrence and join the copies by all-equal relations and
  equalities. Conversely, any edge problem with all-equal constraints is a network with hubs.

**Corollary 3 (hardness lives in hubs; conditional on the cited theorems).**
- **(a) Hub-free networks are easy, given KKR.** Every hub-free network of knots with pinned variables is decidable in polynomial
  time. By Theorems 1 and 2(a) it is an edge problem over a finite set of coverable delta-matroids. A finite set is efficiently
  coverable, since each M_α can be tabulated.
- **(b) Hubs make them hard, given F and S.** For each of the 16 knots outside the Schaefer classes, networks with hubs are
  NP-complete. By Theorem 2(b) they are edge problems over a language containing the constants and all-equal, which is not a
  delta-matroid, and with all-equal the knot's problem is NP-hard by S.
- **(c) The symmetric case, given GF.** For the five symmetric knots that are not parity, a hub-free network on a multigraph is a
  general factor problem whose degree sets have gaps of length at most one, hence polynomial. A hub is the degree set {0, 3}, the case
  shown NP-complete by Lovász.

For the parity knots, networks with hubs remain easy (affine, Gaussian elimination). For the 16 Horn and dual-Horn knots they are
easy too (S). So hubs are necessary for hardness, and with the 16 remaining knots they suffice.

## Nearest known result

- **Corollary 3.** It applies KKR, Feder, the general factor theorems and Schaefer's theorem directly. Its content is classical; the
  program's contribution is the census and the reading. Folklore risk: high for the complexity statements.
- **Theorem 1.** "Every delta-matroid on three variables is coverable" is a finite computation. It may be implicit in the cited
  literature, where the coverable classes include local and compact delta-matroids. A non-coverable example on four variables is used
  as a control. Novelty: `candidate-local-delta`.

## Proof

### Theorem 1

These are finite checks on three variables, made by `check.py` from the definitions.
- The exchange axiom is tested on every pair of tuples.
- For coverability, the even delta-matroids on three variables are enumerated. For each α the check finds one containing everything
  reachable from α and satisfying condition (3).
- The Schaefer classes are closure under ∧, ∨, majority and x ⊕ y ⊕ z.
- The hub relation fails exchange at A = 000, B = 111, x = the first variable: neither 100, 110 nor 101 is in the relation. ∎

### Theorem 2

- **(a)** In a hub-free network every variable occurs in one or two knots. The unary constraints bring every count to exactly two
  without changing the solutions on shared variables.
- **(b)** Replacing a variable that occurs k times by k copies joined by all-equal chains preserves solutions. A variable shared by
  three knots then becomes three copies, each in its knot and in one all-equal relation.
- **The converse.** An all-equal relation in an edge problem merges its three variables into one variable occurring in three other
  constraints, which is a hub.
- **Random check.** The check confirms equisatisfiability on 300 random networks. ∎

### Corollary 3

- **(a)** By Theorem 2(a) and KKR Theorem 11, since every relation used is coverable (Theorem 1) and the set is finite.
- **(b)** By Theorem 2(b) and F, since all-equal is not a delta-matroid and the knot is NP-hard with constants by S.
- **(c)** In a hub-free network of a symmetric knot, each knot is a vertex whose incident edges are its three variables. A knot allows
  exactly a set W of numbers of ones among them. Pins and free legs shift or restrict W without creating a gap of length two. GF then
  applies; the hub is {0, 3}. ∎

## Checks

`check.py` uses the standard library only (seed 20261024). It confirms:
- the census of Theorem 1, including all 155 three-place delta-matroids;
- the reductions of Theorem 2 on 300 random networks.

**Controls.**
- The non-coverable four-place delta-matroid {0000, 0001, 0010, 0110, 0111, 1010, 1011, 1100, 1101}, located by an exhaustive scan,
  is rejected.
- The hub relation fails exchange.
- Without condition (3) of coverability, the non-coverable example would pass.

## What this does not show

- **Local proofs of the cited theorems.** Corollary 3 is conditional on them.
- **Resolution complexity.** Proof complexity is ticket B; algorithmic tractability says nothing about it.
- **Networks of relations on more than three variables.** Composites of knots stay coverable by KKR's closure under gadgets, but
  relations on four or more variables outside that closure need not be coverable.
