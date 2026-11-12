# Travelling ladders across the fold

Status: Proved (refereed)

Ticket `ACROSS-FOLD-20261112-001A`, 2026-11-12. The frozen statement ("Theorem L", rows 2 to 8) is in
`research/ACROSS-FOLD-20261112-001/preregistration.md`. During the work the advisor model, asked about the lower bound, sketched the
flip form and the core lemma below; I checked and completed the argument, and it proves Theorem L for every row, together with two
statements the pre-registration left to the census (Theorems C and D). These are stated here as found after freezing.

## Standard statement

Base 16 in the sheared frame is the 3-uniform hypergraph on Z² with the edges {z, z+(0,1), z+(1,0)} and {z, z+(0,2), z+(1,2)}; a
state is a proper 2-colouring; a finite set is free when every colouring of it extends to a state, and a bond when it is not free and
every proper subset is. Write (x, r) for column x, row r. For y ≥ 2 let L_y = {0, 1, 2, 4, 6, …, y} (y even) or {−1, 0, 1, 3, 5, …, y}
(y odd), as rows of column 0; |L_y| = ⌊(y+1)/2⌋ + 2.

- **Theorem L.** For every y ≥ 2 and every k ≥ ⌊(y+1)/2⌋ + 1, L_y ∪ {(k, y)} is a bond of size ⌊(y+1)/2⌋ + 3.
- **Theorem C.** If A is a set of rows of column 0 containing 0, y ≥ 2, |A| ≤ k and A ∪ {(k, y)} is a bond, then
  |A| ≥ ⌊(y+1)/2⌋ + 2. So for k ≥ ⌊(y+1)/2⌋ + 1 the ladder is the least bond of this form; for y ∈ {0, 1} the least has size 4.
- **Theorem D.** If y ≤ −3 and |A| ≤ k, no set A of rows of column 0 containing 0 makes A ∪ {(k, y)} a bond.

In the program's words (the glossary's unlengthened shift, along-count and across-count, heddle): the law's bond distance from the
origin to the distinction k along and y across is at most ⌊(y+1)/2⌋ + 2 at every k ≥ ⌊(y+1)/2⌋ + 1, and exactly that among bonds
made of one along-count and one distinction further along; such bonds never reach three or more fewer across. Bonds over two
along-counts do reach that way, at the same sizes (computed; `research/ACROSS-FOLD-20261112-001/across_fold.md`), so Theorem D is
about the family, not the law.

## Proof

**The column rule** (FOLD, check C1 there). Columns c, d (maps Z → {0, 1}) are consecutive exactly when, for every r, c(r) = c(r+1)
implies d(r) ≠ c(r), and c(r) = c(r+2) implies d(r+2) ≠ c(r).

**Flip form.** Put p_x(r) = c_x(r) + x (mod 2). A row s of column x is *pinned* when c_x(s) = c_x(s+1) or c_x(s−2) = c_x(s),
equivalently p_x(s) = p_x(s+1) or p_x(s−2) = p_x(s). The column rule says exactly: at a pinned row, d(s) = ¬c_x(s), that is,
p_{x+1}(s) = p_x(s); at a row that is not pinned, d(s) is free. So p_{x+1} is p_x with any set of unpinned rows flipped. Flipping
nothing (d = ¬c) is always allowed, so every column has a successor and a predecessor (its complement), and every state of finitely
many columns extends to a state of the base. In particular every pattern on one column is free.

**The core.** For a pattern a on a finite set A of rows of column 0, a subset T of A is *self-supporting* for a when every r in T has
r+1 in T or r−2 in T with the same value under a. The union of self-supporting sets is self-supporting; let core(a) be the largest.

**Lemma 1 (core rows never flip).** In every state with c_0 = a on A, p_x(r) = a(r) for every r in core(a) and every x ≥ 0. By
induction on x: if every core row keeps its value in column x, each has a neighbour (r+1 or r−2) in the core with the same value, so
it is pinned, and keeps its value in column x+1.

**Lemma 2 (everything else can flip).** Let y be in A but not in core(a), v = a(y). Let Q be the smallest set containing y+1 and y−2
such that whenever s in Q ∩ A has a(s) = v, also s+1 and s−2 are in Q. Choose c_0 outside A so that p_0 = ¬v on Q \ A, and arbitrary
elsewhere. Let F = {y} ∪ {s in Q ∩ A : a(s) = v}. Repeatedly, in one column at a time, flip one row s of F that still has value v and
whose two neighbours s+1 and s−2 currently have value ¬v (it is then unpinned), and nothing else. Every neighbour of a row of F lies in
Q, and a row of Q has value ¬v unless it is an unflipped row of F, so a flipped row is never needed again and nothing else changes. If
the process stops before y is flipped, the unflipped rows U of F all have value v and each has a neighbour of value v, necessarily in
U: U is self-supporting, lies in A and contains y, so y is in core(a), a contradiction. Hence y can be flipped by column |F| ≤ |A|, and
then left alone; and y can also never be flipped. So for every k ≥ |A| both values of (k, y) occur. A row y outside A takes both values
at column k as well (choose c_0(y) freely and flip nothing).

**Corollary.** For k ≥ |A|, a pattern a on A (in column 0) forces the value at (k, y) exactly when y is in core(a), and then the value
is a(y) + k. Since patterns on A alone are free, A ∪ {(k, y)} is constrained exactly when some a has y in core(a).

**Lemma 3 (a bottom triple and no long gaps).** Let T be self-supporting for a with least row m: m needs m+1 (m−2 is
below m), and m+1 needs m+2 (m−1 is below m); so m, m+1, m+2 are in T, with one value. If T is a *minimal* self-supporting set
containing y, it is monochromatic (supports join equal values, and the closure of y under supports is self-supporting) and has no two
consecutive rows g, g+1 missing between its least and greatest rows: otherwise the rows above the gap are supported only from above
the gap (a row r ≥ g+2 is supported by r+1 or by r−2 ≥ g, so by r−2 ≥ g+2), and the rows below only from below (r ≤ g−1 is supported
by r−2 or by r+1 ≤ g, so by r+1 ≤ g−1), and the half containing y alone is self-supporting.

**Proof of Theorem L.** The all-equal pattern on L_y is self-supporting (every row of the bottom triple has a neighbour above it or two
below it in the triple; each rung r has r − 2), so L_y ∪ {(k, y)} is constrained at every k ≥ 1 (Lemma 1). For minimality: without
(k, y) the set is one column, free; without (0, y), the row y is outside the set and (k, y) is unforced. Without a row of the bottom
triple, the set has no three consecutive rows (the rungs are two apart), so by Lemma 3 no subset is self-supporting for any pattern.
Without a rung r < y, a self-supporting set containing y would contain a minimal one, whose least row starts the only triple (at most
0 < r) and whose greatest row is at least y > r; but the rows r−1, r, r+1 are all missing, against Lemma 3. So no pattern on the part
has y in its core, and since the part's column-0 rows number ⌊(y+1)/2⌋ + 1 ≤ k, the Corollary makes every part free. ∎

**Proof of Theorem C.** Let A ∪ {(k, y)} be a bond with |A| ≤ k. By the Corollary some pattern a has y in core(a); let T be a minimal
self-supporting subset of core(a) containing y. If some row r of A were not in T, the part without (0, r) would still be constrained
(T, a|T and the Corollary, with k ≥ |A| − 1), so A = T. Then 0 is in T, so its least row m is at most 0; its greatest row is at least
y; it has the bottom triple and no two consecutive missing rows above it. Rows m+3 to y therefore hold at least ⌈(y − m − 2)/2⌉ ≥
⌈(y − 2)/2⌉ rows of T, and |A| ≥ 3 + ⌈(y − 2)/2⌉ = ⌊(y+1)/2⌋ + 2. For y ∈ {0, 1}, |A| ≥ 3 by the bottom triple. If instead |A| > k ≥
⌊(y+1)/2⌋ + 1, then |A| ≥ ⌊(y+1)/2⌋ + 2 anyway. ∎

**Proof of Theorem D.** With T as above, generate T from y by adding to each row its support, preferring r−2 when it is in T; this
closure is self-supporting and inside T, so it is T. No row of it exceeds y+2: a row r ≤ y adds r−2 or r+1 ≤ y+1; the row y+1 adds y−1
or y+2; the row y+2 adds y, which is in T. For y ≤ −3 every row of T is at most −1, so 0 is not in T = A: no bond. ∎

**Nearer columns.** For k < |A| Lemma 2 may not have room to flip, and other sets are constrained: a run of rows two apart without a
triple loses its least row at each column (rows −1, 1, 3, 5 all equal force row 5 three columns on), so for y ≥ 5 and
3 ≤ k ≤ ⌊(y+1)/2⌋ a proper part of L_y ∪ {(k, y)} is constrained (check C2 lists them).

## Nearest known result

The forcing mechanism is FOLD's, and the nearest precedent is Ledrappier's three-dot shift and its non-mixing shapes (Kitchens and
Schmidt), whose proofs use the group structure that not-all-equal lacks. The core is the stable set of a constrained flip dynamics,
the kind studied in bootstrap percolation and kinetically constrained models; the advisor named that fit, and I did not find this
statement there. Classification: known-with-delta for the mechanism, the core lemma not found.

## Checks

`check.py` (result in `result.json`): C1 the ladder's forcing; C2 freeness of every proper part for every k (exact transfer graphs of
period up to 11), y = 2 to 8, which agrees with Theorem L's threshold and lists the failing nearer k; C3 every rung needed; C4 the core
lemma itself, exhaustively on row sets within rows −2 to 5 of size up to 5, every pattern, every y in the set, at k = |A| and |A| + 2
(30,048 cases: core rows never take the opposite value in a periodic state, and every other row takes both). C3 certifies its five
sets free with periodic states (it first used a window alone, which cannot show freeness; the referee caught it). Ticket B's census
and its soundness audit agree with Theorems C and D on every target they cover.

## Review

An independent referee (a fresh agent, its own code in the original frame) checked every step of the proof and found no gap, agreed
on 600 random instances of the lemma, and confirmed Theorem L's thresholds and nearer failures exactly; it asked for the two trivial
parts to be stated (they are) and for C3 to certify freeness (it does).
