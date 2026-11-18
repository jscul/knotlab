<!-- modelUsage: claude-fable-5-2 -->

**Verdict:** S1 and S3 hold (S3's proof needs a repair), S2's headline is false as worded, and the reading's "two" is an input of F, not a finding. Everything below is hand-derived from the rules as you stated them; I ran nothing.

## 1. S1–S3

**S1 is right, with a narrow scope.**
- It needs one more line: start junctions are dead after round 1, so a child of A and the junction B are never candidates through A.
- "No two have a common neighbour" means the neighbour graph of the start is a matching. So the scope is exactly lone knots and touching pairs sharing s ≥ 1 bits.
- The growth sees only l_J, the number of loose bits, never the size.

**S2 is right for two knots sharing one bit, but the summary sentence is false.** The correct statement in S1's scope is: one count c ≥ 2 survives iff every start junction has l_J ∈ {0, 1, c}.
- **l = 1 accepts every count.** Its lone offshoot is a fresh seed with c loose bits and grows N^c.
- **Counterexample, touching.** A 3-knot and a 4-knot sharing two bits (l = 1, 2) survive at c = 2. In general, sizes a < b sharing a−1 bits survive at c = b−a+1.
- **Counterexample, three knots.** A lone 3-knot plus two 4-knots sharing one bit (all l = 3) survive at c = 3.
- **c = 1 at l = 2 does not stall.** Each offshoot gets 1 bit, the join gets 1, then an endless chain of two-place junctions follows, all copies of h. So T2's "c = a−1 stalls at round 4" needs a ≥ 3. Either freeze "c ≥ 2 by the floor" explicitly or predict this survivor.
- **Stall round.** It is the minimum over pieces of r(l, c): 2 if c ≤ l−2; 4 if c = l−1 and l ≥ 3; 3 if c ≥ l+1 and l ≥ 2. I checked l = 2, c = 3 by hand: the join sits in 4 pair groups with 3 loose bits.

**S3's conclusion is right, but the stated proof is wrong.** The bit h is shared, not open, and a subset of equations containing A must also contain B.
- **Repair.** A subset S of old equations sums to its cut. If the cut equals the top's bits, S contains the top's parents, and so, by connectedness through h, the whole old component. That cut also contains the other piece's bits handed over in the same round, which are never empty.
- **General lemma.** A demand-0 junction is implied iff its bits are exactly all loose bits of its old component.
- **Same round (a = b).** Neither top is implied alone, though their sum is. Each gets 1 bit, each lone offshoot U gets 2, so your step stands. F never stops, since demand is ≥ 1 on every later junction.
- **Extra fact to freeze.** The top's fresh bit u satisfies u = h on every allowed state, on both sides. The closed 2^l block is a relay of h, and U is a three-place junction on (copy of h, v1, v2). So every one-bit touching start reduces to the 3–3 start.

**The "two" is F's floor term.** Surplus bits arise only from the terms 3−p and 1, that is only at demand ≤ 1. With floor m, U gets m−1 bits and the tail is N^(m−1). Your reading concedes this, but it should be said more strongly: the dimension two is put in by F, not found.

## 2. A reason for three?

I find none inside the growth.
- **Cheapness** restates the floor, as you say.
- **Bits hidden** never enters the rule.
- **Atomicity** enters only through F's 3−p term.
- **Size** is invisible to the rule; only l_J matters. That is the clean "nothing prefers either" statement.

**Presentation dependence is a fair reading, and it is stronger than you put it.**
- No hidden distinction is needed. Replacing {A, B} by {A, A+B} keeps the same variables and allowed states but changes the l's to 1 and b−1, hence the growth.
- Under F the contrast is sharper than under one count: the single 4-junction closes (2^4, finite), while its two-3-knot presentation grows two N^2 forever.
- The growth is therefore an invariant of the junction graph, not of the relation that K1–K3 tests.
- No canonical atomisation rescues it, since a 4-parity already splits three ways.
- State this as a limit of the study: "first knot size" is not well defined for the growth until a presentation is fixed.

## 3. Predictions to freeze

- **Q1.** Freeze the l ∈ {0, 1, c} criterion and the r(l, c) table. Add pairs sharing two bits and one three-knot start (3 apart, 4–4 touching). Include c = 1.
- **Q2.** Freeze exact junctions created per round, per piece:

  | Piece | Round r | Junctions created |
  |---|---|---|
  | l = 2 | every r | r + 1 |
  | l ≥ 3 | r ≤ l | C(l, r) |
  | l ≥ 3 | r = l + 1 | 1 |
  | l ≥ 3 | r ≥ l + 2 | r − l |

  Also freeze: top k = 1, U k = 2, and u_A = u_B = h on all allowed states.
- **Q3.** Survives at c = 2, and at c = 1 as the degenerate relay chain. Add the F contrast (closed against endless).
- **Q4.** Predict:
  1. A start closes iff the last demand-0 junction takes all loose bits of its component.
  2. Otherwise each unimplied demand-0 junction starts a tail: N^2 directly if p = 1, via one relay if p ≥ 2.
  3. Linear outcomes are strips N×{0,1}: a demand-1 offshoot whose partner has no axis of its own.
  4. Nothing cubic ever, because surplus needs demand ≤ 1. This is a mechanism, not yet a proof.

  Consistent with your pilot: the ring of four gives two unimplied joins (their sum is implied), hence two N^2 and 4 offshoots per round; the ring of three and the star close.
- **Control.** Rerun F with floor 2 and floor 4. I expect relay chains and N^3 tails respectively. That shows the two is the floor.

## 4. Literature

I did not search; this is from memory.
- **T1 and the cube filling** are the median-graph and CAT(0) cube complex picture: Sageev–Roller duality, and configurations of conflict-free event structures (Nielsen–Plotkin–Winskel).
- **The implied test** is the fact that the GF(2) incidence matrix of a graph has rank n minus the number of components.
- **Presentation dependence** is graphic-matroid non-uniqueness (Whitney 2-isomorphism).
- **S1–S3** I know of no source for; they are short corollaries of the above.