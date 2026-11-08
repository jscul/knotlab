# A cut separates a path; a cycle of rings needs two

Status: Proved by hand from `RECUR-PROOF-20261108-001`'s lemmas. The finite claims are checked in `check.py`.

Ticket `SEPARATE-20261108-001A`, 2026-11-08.

## Standard statement

- **Networks of rings.** Rings of s ≥ 4 cells, each on rule 60 or 102, joined by contacts: a contact is a cell of two rings and
  updates by a self-blind law that adds the neighbours it reads (`net_lib.py`). A contact's **partner** on a ring is the neighbour
  that reads it back. All verdicts are read from row sequences of M^T (`NATIVE-PATH-20261108-001A`, Theorem 2).
- **Cutting a contact.** The contact is frozen: its law becomes c ← c, so it reads nothing. This is the intervention.
- **Needing a ring.** A contact needs ring X at lag T when its value at lag T depends on X's own first-row cells.
- **Native separation** (`docs/COMMON_VERBIAGE.md`). An intervention that meets every native route between two recurrence sets,
  with reachability before it and a complete account of the routes after it that proves their absence.

**Theorem 1 (a cut separates a path).** Take a path of n ≥ 3 rings of `RECUR-PROOF-20261108-001B`: rule 60 or 102 on each ring,
every middle ring's contacts two apart, c_1 reading its partners and each later contact both neighbours on its first ring and its
partner on its second. Before any cut, the last contact needs R_0 exactly at the lags with C(T − (n − 1), e) odd, infinitely many.
After cutting any one contact c_i, the last contact needs R_0 at no lag, and every other contact still binds both of its rings at
every lag. So cutting any contact is a native separation of R_0 from R_(n−1) across time.

**Theorem 2 (a cycle of four rings needs two cuts).** Close four rings R_0, R_1, R_2, R_3 into a cycle with two routes from R_0 to
R_2: contacts c01 (cell 0 of R_0 and of R_1) and c03 (cell k0 of R_0, cell 0 of R_3) read their partners on both rings, and c12
(cell k1 of R_1, cell 0 of R_2) and c32 (cell k3 of R_3, cell k2 of R_2) read both neighbours on R_1 or R_3 and their partner on R_2,
with every k ∈ {2, s − 2}. After mirroring every rule-102 ring:
1. every contact binds both of its rings at every lag;
2. c12 needs R_0 exactly when C(T − 2, k1 − 1) is odd, and c32 exactly when C(T − 2, k3 − 1) is odd;
3. cutting c01 leaves c12 needing R_0 at no lag and c32 exactly as before, and cutting c03 does the same the other way round;
4. cutting both separates R_0 from R_2.

So one cut does not separate R_0 from R_2 and two cuts, one on each route, do: the least separating cut has the size of the number
of routes.

**Remark (routes come from the laws).** Orient the same four contacts round the cycle instead, each reading both neighbours on the
ring before it and its partner on the next. Then R_2 needs R_0 only through c01, and one cut separates (computed, check 4).

## Nearest known result

- **Menger's theorem.** In a graph, the least number of vertices whose removal separates two sets equals the greatest number of
  disjoint paths between them. Theorems 1 and 2 are instances of it on the reads graph of a path and of a cycle of rings.
- **Classification.** Known-with-delta. The delta is the reading across time: a route is a chain of reads whose count at lag T fixes
  a contact's dependence, and its presence is given exactly by `RECUR-PROOF-20261108-001`'s binomial coefficients.

## Lemma A (routes)

A cell's value at lag T depends on a first-row cell x exactly when the number of walks of length T from the cell to x in the reads
graph (an edge from each cell to every cell it reads) is odd. In particular, if no walk of length T leads from the cell to any cell
of ring X, the cell does not need X at lag T.

*Proof.* The entry (M^T)_(c,x) counts the walks of length T from c to x, mod 2. ∎

## Lemma B (cuts)

After a contact c is cut, c reads only itself, so every walk that enters c stays at c. Walks that avoid entering c are unchanged.

*Proof.* The cut replaces c's reads by the single loop at c. ∎

## Proof of Theorem 1

Mirror to rule 60 everywhere (`RECUR-PROOF-20261108-001A`, Lemma 2).
- **Before the cut.** `RECUR-PROOF-20261108-001B` gives the lags: C(T − (n − 1), e) odd, a periodic set with infinitely many lags.
- **The only route.** Split the path at c_i: the upstream part is R_0, …, R_(i−1) with c_1, …, c_(i−1); the downstream part is
  R_i, …, R_(n−1) with c_(i+1), …, c_(n−1). A downstream cell reads only cells of its own ring, its ring's contacts and, for a
  contact, the cells of its two rings. So the only downstream reads of upstream cells are c_i's reads on R_(i−1). After the cut c_i
  reads only itself, and by Lemma B no walk from the last contact reaches R_0's cells. By Lemma A, it needs R_0 at no lag.
- **The other contacts.** A contact other than c_i keeps its two partners, and its inputs still come from before it, so by
  `RECUR-PROOF-20261108-001A`'s Lemma 1 it binds both of its rings at every lag. ∎

## Proof of Theorem 2

Mirror to rule 60 everywhere.
- **Part 1.** c01 and c03 read only their partners, so each is a closed loop (Lemma 1). c12 reads its partner on R_1, its partner
  on R_2 and the chain on R_1 that starts at c01's partner; that chain never depends on c12's partners. So Lemma 1 applies, and in the
  same way to c32.
- **Part 2.** The walks from c12 to R_0's cells all pass through c01: R_2's partner of c12 reads only c12 and itself, R_1's cells
  read only R_1's cells and its contacts, and of those only c01 reads R_0, through its partner R_0[1]. Along this route, as in
  `RECUR-PROOF-20261108-001B` with three rings, R_0[1](0) has coefficient C(T − 2, k1 − 1) in c12. The same holds for c32 through
  c03, with k3.
- **Parts 3 and 4.** Cutting c01 removes every walk from c12 to R_0 (Lemma B), and no walk from c32 to R_0 passes through c01, so
  c32's lags are unchanged. The same holds for c03. Cutting both removes every walk from R_2's contacts to R_0's cells. ∎

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependency artifacts bound by hash; upstream statuses | pass |
| 1 | `net_lib` agrees with `path_lib` on 500 random linear paths, and its full-state-space reading with its row sequences on small networks | pass |
| 2 | Theorem 1 for n = 3 to 8 rings at ring sizes 4 to 14, every choice of positions, each contact cut, and on 300 random mirrored paths | pass |
| 3 | Theorem 2 at ring sizes 4 to 24, all 16 choices of positions, every cut of one or both route contacts, and on 300 random mirrored cycles | pass |
| 4 | The remark: with the contacts oriented round the cycle, cutting c01 separates R_0 from R_2, at ring sizes 4 to 16 | pass |
| 5 | Full state spaces: Theorem 1 for three rings at sizes 4 and 5 and four rings at size 4, and Theorem 2 at sizes 4 and 5, every cut | pass |

## Nonclaims

- **These families only:** rings on rule 60 or 102 with contacts two apart, and the laws stated.
- **No distance.** Separation here is relational: no length, path count used as a magnitude, or metric is formed.
- **Two-time knots only** (A30); composition is read under A37.
