# A knot is a betweenness: the disagreement count determines every not-all-equal base

Status: Proved

Ticket `DISTANCE-ORDER-20261117-001A`, 17 November 2026, by Claude. Epic `DISTANCE-ORDER-20261117-001`. The proofs are below.
`check.py` checks every statement exhaustively at small sizes; that is a check, not the proof.

## Words

- **Base.** A set R of allowed joint states of n distinctions, each state a choice of 0 or 1 for every distinction. N is the number
  of allowed states.
- **Not-all-equal base.** The set of states that are not all equal on each of a given set of triples, its knots.
- **Disagreement count.** For two distinctions u and v,

  d(u, v) = the number of allowed states in which u and v take different values,

  and d/N is the **disagreement rate**. In the literature's words this is the Hamming distance between columns u and v of the states
  written as an N by n table. It is a count across the allowed states, not an extended or metric distance in the program's sense,
  which the foundation allows only after native paths and separation are built. It obeys the triangle inequality. It is 0 on two
  distinctions tied equal.
- **Between.** c lies between a and b when d(a, b) = d(a, c) + d(c, b), which is the literature's metric betweenness (Menger 1928).
  It is strict when d(a, c) and d(c, b) are both positive.
- **Flip.** The flip ā of a is the same distinction read with its two values exchanged, so d(u, ā) = N − d(u, a).
- **Steps apart.** Two distinctions are s steps apart when the shortest row of distinctions joining them, each consecutive pair in
  a common knot, has s links.

## Statements

1. **Betweenness is a three-place constraint.** For any base and distinctions a, b, c, c lies between a and b if and only if no
   allowed state has a = b ≠ c.
2. **A not-all-equal knot is a sum.** d(a, b) + d(b, c) + d(c, a) ≤ 2N, with equality if and only if every allowed state is not all
   equal on a, b, c. This is statement 1 for ā lying between b and c.
3. **The disagreement count determines the base.**
   - (a) Given N, the table of disagreement counts determines every base defined by complement-closed constraints on at most three
     distinctions. These are ties (u = v, u ≠ v) and the three-place knots that exclude one pair of opposite joint states;
     not-all-equal is the pair 000/111.
   - (b) The table alone determines every nonempty not-all-equal base on n ≥ 4 distinctions.
   - (c) At n = 3 the table alone does not determine the base. One knot (6 states) and no knot (8 states) both have every count
     equal to 4.
4. **Pairs see exactly three places.**
   - A parity knot on three distinctions leaves every pair taking each of its four joint values equally often. So on four
     distinctions, parity on abc and parity on abd have the same N, 8, and the same table, every entry 4, and allow different states.
   - Three-place parity is not complement-closed. The witness inside the complement-closed class is four-place parity on five
     distinctions: a + b + c + d even and a + b + c + e even have N = 16 and every count 8, and allow different states.
5. **A line made of betweenness.** On distinctions 0, …, n − 1, the count is additive along the order, d(i, k) = d(i, j) + d(j, k)
   for all i < j < k, if and only if every allowed state is a threshold, 0…01…1 or 1…10…0. If every threshold is allowed, then
   d(i, j) = 2|i − j|. Each condition "j lies between i and k" is a three-place knot (K1 to K3) excluding 010 and 101 on (i, j, k).
   It is a not-all-equal knot with j read flipped, not a plain one. When every threshold of both kinds is allowed, the base's
   projection on (i, j, k) is exactly that knot. *Narrowed after the review of what the premise reopens, 17 November 2026: with only
   one kind of threshold, as on the chain of implications x → y → z, the projection also excludes 100 and 110, its pairs are not
   free, and it is no knot; there d(i, j) = |i − j|, a line from two-place rules alone.*
6. **Order costs states.** Take a chain o, v1, …, vk, each strictly between o and the next. Then every allowed state is a
   threshold along the chain, so the base allows at most 2(k + 1) joint values on its k + 1 distinctions, out of 2^(k+1).
7. **On knot trees the rate reads steps apart.** Take a not-all-equal pattern with no cycle of knots: its knots can be listed so
   that each shares at most one distinction with all the knots before it. Two distinctions s steps apart have disagreement rate
   (1 − (−1/3)^s)/2, and rate 1/2 if no row joins them. So τ(u, v) = −log₃ |1 − 2 d(u, v)/N| equals steps apart. It is additive along
   every shortest row, and it is built from unit steps.

## Proofs

**1.** Fix one allowed state, and write [·] for 1 if true and 0 if not. Then [a ≠ b] ≤ [a ≠ c] + [c ≠ b]:
- if a ≠ b, then c differs from exactly one of them, and both sides are 1;
- if a = b = c, both sides are 0;
- if a = b ≠ c, the left side is 0 and the right side is 2.

Summing over the allowed states gives d(a, b) ≤ d(a, c) + d(c, b). Equality holds exactly when no allowed state has a = b ≠ c. ∎

**2.** In one state, the number of unequal pairs among a, b and c is 0 if all three are equal and 2 otherwise. Summing over the
allowed states, d(a, b) + d(b, c) + d(c, a) = 2 × (the number of allowed states not all equal on a, b, c) ≤ 2N. Equality holds
exactly when every allowed state is not all equal on them. For the flip, d(b, ā) + d(ā, c) = 2N − d(a, b) − d(a, c), so "ā lies
between b and c" is the same equality. ∎

**3(a).** A constraint holds on the base when every allowed state satisfies it. Each constraint of the kinds named is read from the
table and N:
- u = v holds iff d(u, v) = 0, and u ≠ v holds iff d(u, v) = N;
- "exclude 000 and 111 on a, b, c" holds iff the three counts sum to 2N (statement 2);
- "exclude 001 and 110 on (a, b, c)", that is no state with a = b ≠ c, holds iff d(a, b) = d(a, c) + d(c, b) (statement 1). The
  pairs 010/101 and 100/011 are the same statement with the roles exchanged.

Let a base be defined by a set S of such constraints, and take every such constraint that holds on it. The states satisfying all of
them form the base: those constraints include S, so the set is no larger than the base, and the base satisfies each of them, so it
is no smaller. Two bases with the same table and the same N hold the same constraints, so they are equal. ∎

**3(b).** Let R be a nonempty not-all-equal base on n ≥ 4 distinctions. By 3(a) it is enough to read N from the table.
- If R allows every state, every count is 2^(n−1).
- Otherwise some knot holds on R, so by statement 2 the largest sum of three counts, M, equals 2N, and N = M/2.
- No other base has every count 2^(n−1). If one did, every triple would sum to M = 3 × 2^(n−1) = 2N, so every triple would be a
  knot of R, and N = 3 × 2^(n−2). For n ≥ 5 no state is not all equal on every triple, since among five distinctions three take the
  same value. For n = 4 the only such states are the six with two 1s, and 6 ≠ 12.

The decoder is therefore: if every count is 2^(n−1), R is full; otherwise R is cut out by the triples whose counts sum to the
largest value. ∎

**3(c).** One knot on three distinctions allows the six states other than 000 and 111, and in them each pair differs in 4. All
eight states also give each pair 4. ∎

**4.** Under parity on a, b, c, the value of c is the sum of a and b mod 2. So each value of (a, b) has exactly one completion in c,
and by symmetry the same holds for (a, c) and (b, c). A pair with a distinction outside the knot meets no constraint from it. Every
pair therefore differs in half of the 8 states in both bases, and 0111 is allowed by the first and not the second. The four-place
case is the same argument: every pair, and every triple, among a, b, c, d takes all its joint values equally often under a + b +
c + d even. Flipping all five values keeps both relations, since 4 is even, and 01111 is allowed by the first and not the second. ∎

**5.** By statement 1, additivity at (i, j, k) says that no allowed state has x_i = x_k ≠ x_j. A state with no such triple is
monotone along the order, since a value that changes twice gives such a triple, and a monotone state has none.

If every threshold is allowed, there are 2n of them: n + 1 of each kind, with the two constant states counted once. For i < j,
x_i ≠ x_j in exactly the j − i thresholds of each kind whose step falls between i and j, so d(i, j) = 2(j − i).

The constraint excluding 010 and 101 on (i, j, k) is a knot:
- it excludes something (K1);
- every pair of the three still takes all four joint values (K2): for (i, j), 00 occurs in 000, 01 in 011, 10 in 100 and 11 in 111,
  and the other pairs are alike;
- it allows states (K3). ∎

**6.** Write v0 = o. For i < j < l, the chain gives d(o, v_l) = d(o, v_i) + d(v_i, v_j) + d(v_j, v_l): add the equalities that
define the chain, and use the triangle inequality in the other direction for the steps it skips. So v_j lies between v_i and v_l.
By statement 1 no allowed state has v_i = v_l ≠ v_j, so every state is monotone along the chain, as in statement 5. There are 2(k +
1) monotone patterns on k + 1 places. ∎

**7.** Induction on the knots, in the listed order. With one knot the base allows its six states, uniformly as a set: each pair
differs in 4 of them, rate 2/3 = (1 − (−1/3))/2.

Add a knot (x, y, z) that meets the earlier ones in at most the one distinction x; y and z are new. For each earlier state there
are exactly three completions on (y, z) (six if x is also new, the case of a separate piece; corrected after the referee from "four"), so every earlier state keeps the same
weight.
- In ±1 terms, among the three completions with x given, y equals x once and differs twice, so the mean of s_y given s_x is
  −s_x/3, and the same holds for z. The pair (y, z) is equal in one of the three completions, so the mean of s_y s_z is −1/3.
- For an earlier distinction u, the mean of s_u s_y over the allowed states is −1/3 times the mean of s_u s_x, since y depends on
  the earlier distinctions only through x.
- The steps apart of u and y are those of u and x plus one, since every row from u to y passes through x.

So the correlation 1 − 2d/N of two distinctions s steps apart is (−1/3)^s, by induction. When x is new the new piece is independent
of the old, and the correlation is 0: rate 1/2, no row. Then τ = −log₃ |(−1/3)^s| = s. ∎

*Added at the close, 17 November 2026.* Among such bases, steps apart also determines the knots, and so the base. Three
distinctions that pairwise share a knot lie in one knot. Otherwise, of the knots that hold the three pairs, the last one listed would
share two distinctions with the knots before it. So the knots are the triples whose pairs are all one step apart. ∎

## What it means

- **The census, explained.** The referee of `DISTANCE-INFO-20261117-001` found that the disagreement table determined every
  not-all-equal base through six distinctions. Statement 3 proves it for every size, and for every base defined by
  complement-closed constraints on at most three places once N is given. The reason is that "not all equal" on three distinctions is
  itself a sum of pairwise disagreements. The law is pairwise, and statement 4 shows that pairs see no further.
- **The dual of a known result.** `OVERLAP-READ-20261111-001` proved that the law reads pair counts: a not-all-equal base depends
  only on how many knots lie on each pair of distinctions. Statement 3 reads the same fact from the other side: the pair counts of
  the allowed states give back the base.
- **What it needs.** The table determines the base only among bases of the known law. It is not the claim that pair counts determine
  a set of states in general, which is false: see statement 4, and the bits a knot hides from pairs (`EMERGENCE-BITS-20261021-001`).
- **The smallest emergent unit.** On one knot of three distinctions, statement 3(c) shows that the table alone cannot tell the knot
  from no knot. It can once N is known, or once the counts are read as rates: 2/3 against 1/2.
- **Where order lives.** By statement 1, "c lies between a and b" is exactly a three-place constraint. It is a knot where its three
  pairs are free. On a base closed under flipping all values and with no tie, every strict betweenness is a knot, since a
  complement-closed pair that is not free is a tie. Elsewhere it can follow from two-place rules: on the chain of implications x →
  y → z, which has no knot, the counts are 1, 1 and 2 (narrowed 17 November 2026). By statement 6 it is paid for in states: a chain of k + 1 distinctions leaves only
  2(k + 1) of their 2^(k+1) joint values. A line with nothing skipped (statement 5) is the base whose knots say that each
  distinction lies between its neighbours, and it has only 2n states.
- **Steps apart, read from the states.** By statement 7, on knot trees the log of the correlation reads steps apart exactly. That is
  a quantity read from the allowed states alone, built from unit steps, with nothing skipped. On knot trees bond distance is steps
  apart plus one (`RANDOM-FATES-20261112-001`, proved), so there the states' pair counts and the bonds give the same ruler.
- **Parity.** Statement 4 answers A97's second test. The full bit a parity knot hides is seen by no pairwise count, so it is not a
  pairwise distance.

## Provenance

- **Statements 1 and 2** are elementary. In the cut-polytope literature they say which of the four triangle facets of a triple are
  tight, one for each pair of opposite joint states (Deza and Laurent 1997). That "not all equal" on three values has degree two in
  ±1 values, (3 − x_a x_b − x_b x_c − x_c x_a)/4, is standard in the Fourier analysis of constraint problems.
- **Statement 3** has no source I know in this form, and the advisor knows none either. It is likely folklore: a nonnegative
  degree-two violation count has mean zero over a base exactly when it vanishes on it, the second-moment reading behind
  degree-two Sherali–Adams and sum-of-squares arguments (added after the referee). The complement-closed relations of 3(a) sit
  in the co-clone IN₂ (Böhler, Reith, Schnoor and Vollmer 2005). A co-clone also allows hidden distinctions, and four-place parity
  is in IN₂, so 3(a) covers plain conjunctions of the named constraints, not the whole co-clone.
- **Statement 4** is the standard fact that parity is pairwise independent.
- **Statement 5** is the classical picture of a line as a sum of nested cuts (Hamming and cut metrics; Deza and Laurent 1997).
- **Statement 6** is local. It is elementary from statement 1.
- **Statement 7** is the binary symmetric Markov model on a tree. The log transform is the literature's additive tree metric for
  such models, the Cavender–Farris–Neyman distance of phylogenetics, −½ ln(1 − 2p) (Neyman 1971, Farris 1973, Cavender 1978), here
  with base three and the sign of the correlation dropped. The process is the broadcast process on a tree with flip probability
  2/3 (Evans, Kenyon, Peres and Schulman 2000; added after the referee).
- **Advisor.** The advisor model was consulted before the freeze. It confirmed statements 1 to 5 by hand. It gave the four-place
  parity witness of statement 4 and the bound behind statement 6, and it proposed the log transform of statement 7.
