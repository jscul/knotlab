# Why a chain of eight carries the step one layer up (proof sketch)

Chain knots K_i = (2i, 2i+1, 2i+2), i = 0..7, under not-all-equal. Call the shared distinctions at every second link the
**spine**: s = 2, 6, 10, 14 (shared by K0K1, K2K3, K4K5, K6K7). The pattern's six agreements, each with forbidden
value 1:

| Reading | Carrier | What it forces when it holds |
| --- | --- | --- |
| A0 | [3 = 4 = 5] | K1 = (2,3,4) and K2 = (4,5,6) each have two equal places, so 2 and 6 take the other value: **2 = 6** |
| C0 | [7 = 8 = 9] | K3, K4 likewise: **6 = 10** |
| A1 | [11 = 12 = 13] | K5, K6: **10 = 14** |
| C1 | [2 = 14] | **2 = 14** directly |
| B0 | [0 = 1 = 10] | K0 = (0,1,2): 2 takes the other value from 0 = 1 = 10: **2 ≠ 10** |
| B1 | [6 = 15 = 16] | K7 = (14,15,16): 14 takes the other value from 15 = 16 = 6: **6 ≠ 14** |

The rule used is one fact about not-all-equal: if two places of a three-place knot agree, the third takes the other
value. An agreement on a knot's two places therefore acts as a "not" on its third, and two such nots in a row act as an
equality.

The four clauses are four triangles on the spine:
- (A0, B0, C0): 2 = 6, 6 = 10 and 2 ≠ 10 cannot all hold.
- (A0, B1, C1): 2 = 6, 2 = 14 and 6 ≠ 14 cannot all hold.
- (A1, B0, C1): 10 = 14, 14 = 2 and 2 ≠ 10 cannot all hold.
- (A1, B1, C0): 10 = 14, 6 = 10 and 6 ≠ 14 cannot all hold.

So each clause is implied by the chain's own laws. It is implied on any stage that contains the chain, whatever else the
stage holds. The upper word "all three" (both A, some B, some C) is then excluded on every stage containing a chain of
eight. That part is **proved**. The other parts of the step (seven upper words, pairs free, no reading read at a knot or
at one lower bond) need the rest of the stage not to constrain more. They are computed (2,803 of 2,808).

**Why eight.** The relations needed are a cycle of four equalities (2 = 6 = 10 = 14 = 2) with two crossing inequalities
on four spine points. Each equality between consecutive spine points uses two knots. The two inequalities each use an end
knot's two own places with a far spine point. Four spine points two knots apart need eight knots.

**Intuition (a link, not evidence).** Read through agreements, not-all-equal turns into equalities and inequalities
between distinctions, that is, parity relations x + y = 0 or 1 on the spine. The step one layer up is a parity
contradiction around triangles of a four-point cycle: the second layer of not-all-equal speaks parity's first-layer
language. Cheapest test: a chain long enough to carry two such spines, searched for a step among the parity facts of
the spine (where parity's own family facts and their relation, lesson 12.3, would be the next layer).
