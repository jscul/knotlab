# Hub-free gadgets cannot create parity

Status: Proved

Ticket `SURFACE-GLUING-20261024-001B`, 2026-10-24.

**What it uses:**
- from `SURFACE-GLUING-20261024-001A-P001`: hub-free gluing, and parity as the only knot that glues topologically at every genus;
- the canonical guardrail of `AGENTS.md`: a variable tied into three or more relations is a hub;
- background on the hypercube, proved inline: a connected regular bipartite graph has exactly its two colour classes as maximum
  independent sets.

## Standard statement

**Setting.**
- **Co-independent relations.** A Boolean relation S on n variables is *co-independent* when no two tuples outside S differ in
  exactly one place. The *excluded set* is Z = {0, 1}^n \ S.
- **Knots.** On three variables, the co-independent relations other than the full cube are exactly the 34 knots.
- **Hub-free operations.**
  - *Gluing*: identify one variable of each of two relations and quantify it away.
  - *Self-gluing*: identify two variables of one relation and quantify them away.
  - *Pinning*: fix one variable to 0 or 1.
- **Faces.** A *face* of S is the relation obtained by pinning some of its variables. A *parity face of dimension d* is a face on d
  variables that is a parity relation, with total fixed modulo 2.

**Lemma 1.** S is co-independent exactly when forgetting any one variable leaves the other n − 1 unconstrained.

**Lemma 2 (exact gluing).** Let M(x, e) and N(y, e) be co-independent, and let Z_M^v = {x : (x, v) ∉ M}, and likewise Z_N^v. Then the
glued relation C(x, y) = ∃e M(x, e) ∧ N(y, e) is co-independent, and

  |Z_C| = |Z_M^0| · |Z_N^1| + |Z_M^1| · |Z_N^0|.

**Lemma 3.**
- Self-gluing and pinning keep co-independence.
- The operations commute with taking faces: a face of a result is the result of the corresponding faces.

**Lemma 4.** A co-independent relation on n ≥ 1 variables excludes at most 2^(n−1) tuples. Equality holds exactly for the two parity
relations.

**Theorem 5 (no parity without hubs).** Suppose co-independent relations M and N have no parity face of dimension three or more.
Then neither does any relation obtained from them by gluing, self-gluing or pinning. So the hub-free closure of any family of such
relations contains no parity relation on three or more variables.

**Corollary 6.**
- **Hub-free gadgets.** Of the 34 knots, only the two parity knots build a parity relation on three or more variables by hub-free
  gadgets with pins. This stays true for laws combining several non-parity knots.
- **With hubs.** Not-all-equal and pins define three-variable parity.

**Reading.** In density terms the glued excluded fraction is a₀b₁ + a₁b₀, where a_v and b_v are the excluded fractions of the halves
e = v. Each is at most ½, so hub-free gluing can only dilute exclusion, unless every piece is already parity. Memory, which is
parity, is never created without hubs; a law has it natively only if it starts with it.

## Nearest known result

- **Lemmas 1 to 4.** Elementary. A co-independent relation is the complement of a binary code of minimum distance at least two.
- **Theorem 5.**
  - It is a fan-out-two expressibility obstruction, in the spirit of Feder's fan-out limitations. Feder's delta-matroid closure does
    not give it, since parity is itself a delta-matroid; the density identity does.
  - With hubs the obstruction disappears: not-all-equal with constants pp-defines every relation, and the check builds parity
    explicitly.
  - Novelty: `candidate-local-delta`. No statement of this form was found in the bounded scans of this epic.

## Proof

### Lemma 1

- **Excluded neighbours give a missing projection.** If two excluded tuples differ only at variable i, forgetting i loses their common
  projection.
- **A missing projection gives excluded neighbours.** If a projection p on n − 1 variables is missing, both extensions of p are
  excluded, and they differ in one place. ∎

### Lemma 2

- **The count.** (x, y) is excluded exactly when both values of e fail: (x, 0) ∈ Z_M or (y, 0) ∈ Z_N, and (x, 1) ∈ Z_M or (y, 1) ∈ Z_N.
  - Co-independence forbids (x, 0) and (x, 1) both excluded from M, and likewise (y, 0) and (y, 1) from N.
  - So exactly one of two disjoint cases holds: (x, 0) ∈ Z_M and (y, 1) ∈ Z_N, or (x, 1) ∈ Z_M and (y, 0) ∈ Z_N. Counting the two
    cases gives the formula.
- **Co-independence of the result.** Take two excluded tuples that differ in one x-place.
  - If both are in the same case, two neighbouring tuples are excluded from M.
  - If they are in opposite cases, (y, 0) and (y, 1) are both excluded from N.
  - The y-places are symmetric. ∎

### Lemma 3

- **Self-gluing.** A tuple is excluded after self-gluing exactly when it is excluded with both values 00 and 11 inserted at the glued
  pair. Two neighbouring excluded results would give two neighbouring excluded tuples with 00 inserted.
- **Pinning.** A subcube of an independent set is independent.
- **Faces.** Pinning variables commutes with identifying and quantifying other variables. ∎

### Lemma 4

- **The hypercube.** It is connected, bipartite and regular, with the two parity classes as colour classes.
- **Maximum independent sets.** In a connected d-regular bipartite graph with classes A and B, Hall's condition holds with strict
  inequality |N(X)| > |X| for every proper nonempty X ⊂ A.
  - An independent set I satisfies |I| ≤ |I ∩ A| + |B| − |N(I ∩ A)| ≤ |B|.
  - Equality forces I ∩ A to be empty or all of A, so I = B or I = A.
- **The relations.** An excluded set of size 2^(n−1) is therefore a parity class, and its complement is a parity relation. ∎

### Theorem 5

All relations involved are co-independent (Lemmas 2 and 3). It suffices to treat one operation at a time.

- **Gluing.** Let F be a face of dimension d ≥ 3 of C, pinning some x- and y-places. By Lemma 3, F is the gluing of the matching faces
  M_F and N_F, which keep e. Suppose F is parity, so its excluded fraction is ½ (Lemma 4). By Lemma 2, ½ = a₀b₁ + a₁b₀.
  - **(i) Both pieces keep another variable besides e.** Every half has dimension at least one, so every a_v and b_v is at most ½
    (Lemma 4), and all four must equal ½.
    - The halves of M_F are then parity classes. They are disjoint by co-independence, so M_F is a parity relation. So is N_F.
    - Their dimensions add up to d + 2 ≥ 5, so one of them has dimension at least three. That is a parity face of dimension three or
      more of M or N.
  - **(ii) M_F has e as its only variable.** M_F is then empty, the full relation {0, 1}, or a constant.
    - If M_F is empty or full, F is empty or the projection of N_F forgetting e, which is full by Lemma 1. Neither is parity.
    - If M_F is a constant, F is a face of N of dimension d ≥ 3.
    - N_F is symmetric.
- **Self-gluing.** Let F be a face of dimension d ≥ 3 of the result. Its excluded set is contained in that of the face of M with 00
  at the glued pair, a face of dimension d. So its excluded fraction is at most ½, and equality makes that face of M a parity face of
  dimension d ≥ 3.
- **Pinning.** A face of a pinned relation is a face of the original. ∎

### Corollary 6

- **The knots.** A knot is co-independent, and its only face of dimension three is itself, which is parity only for the parity knots.
  Apply Theorem 5 to any family of non-parity knots.
- **With hubs.** The explicit construction:
  - u ≠ ū is NAE(u, ū, 0) ∧ NAE(u, ū, 1);
  - OR(a, b, c) is ∃w NAE(a, b, w) ∧ NAE(w, c̄, 1);
  - the four clauses excluding the odd tuples give even parity on x, y, z.
  
  Several variables then occur three or more times. ∎

## Checks

`check.py` uses the standard library only (seed 20261024). It confirms:
- **Lemmas 2 and 3** on 400 random glued pairs and 200 self-glued and pinned relations;
- **Lemma 4** exhaustively on up to four variables;
- **Theorem 5** on 300 random pairs without parity faces of dimension three or more;
- **Corollary 6** through the hub-free closure of every knot, with intermediate relations of at most five variables:
  - closure sizes are 8, 10, 15, 19, 28, 30, 54 and 149 by knot orbit;
  - the closure of all 32 non-parity knots together has 279 relations and no parity face of dimension three or more;
  - the parity knots reach parity on three, four and five variables.

**Controls.**
- **A parity face is enough.** A four-variable co-independent relation that is not parity but has a parity face reaches parity by one
  pin.
- **Hubs suffice.** The hub construction gives even parity.
- **The formula is sharp.** A same-side mutation of the gluing count, |Z_M^0||Z_N^0| + |Z_M^1||Z_N^1|, disagrees with the true
  excluded count.

## What this does not show

- **Relations that are not co-independent.** Theorem 5 assumes co-independence; exactly-one, for example, is not co-independent.
- **Hardness of hub-free networks.** Theorem 5 shows that parity cannot be built natively. Whether native networks of non-parity
  knots are easy for resolution is ticket B of `NATIVE-HARDNESS-20261024-001`.
