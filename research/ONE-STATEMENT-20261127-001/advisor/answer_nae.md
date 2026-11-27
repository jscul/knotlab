**The short answer:** I expect no second layer under not-all-equal beyond the first layer composed with itself, and one short run can refute that. Everything below is by hand with no run, so `unverified`, unless marked "read".

**The premise has moved.** `ONE-STATEMENT-20261127-001/referee-R1/report.md` is in the tree: Refuted, two Blocks (read).
- The census is complete: 7,074 of 7,075 starts have one presentation.
- "The states choose the knots" holds only where every knot is essential and every knot's own states all occur. That is the all-size theorem of `THREE-READERS-AND-GROWTH-20261120-001B/classification.md` (referee pending there).
- Outside that class, the referee's ten-knot start has two family partitions.

## Three lemmas the answers rest on

- **F, forcing is everything.** With at most two holders and three or more places, fixed values extend to an allowed state exactly when forcing reaches no all-equal knot. Forcing means: a knot with every place but one fixed and equal sets the last to the other value. This is the step at `classification.md` 11–13, stated generally.
- **G, gluing.** Two knots sharing one distinction x, with x hidden, are one not-all-equal knot on the remaining places with one side reversed: only "A all v, B all the other value" is missing. Check: two three-place knots have 18 states and 14 of 16 patterns.
- **R, rings erase.** Take a connected part and the distinctions exactly one of its knots holds.
  - With no ring and no double meeting, exactly two patterns are missing there: values alternating with the number of steps between holders. No proper part implies this.
  - With a ring or a double meeting, every pattern occurs.

## 1. The three candidates

- **(a) A function every small change keeps: none.**
  - In every state at least (distinctions − knots) distinctions can change alone, because a knot blocks at most one place.
  - The record has one class on all 208 structures read (`nae_sample.jsonl`, `nae_rings.jsonl`, read).
  - Prediction: one class under single changes alone on every census start.
- **(b) A relation among separately carried functions: yes, one per ring-free connected part (lemma R).**
  - This is not-all-equal's "sum of laws", and it is a function of the states with no basis to choose.
  - It gives no layer number: any grouping of knots into ring-free parts is again a presentation, as with parity's quotient.
  - `STATES-GROWTH`'s M(S) lists only relations with no place reversed (its lines 15–16, read), so its 79.8% undercounts them.
  - A trap: "the number of ring knots whose two ring distinctions differ is even" holds for every assignment, allowed or not. It is an identity, not a law.
- **(c) Properties of the allowed set.**
  - Tied pairs: none; every pair takes four values (from F). Predicted 0 on every census start.
  - Under the equal weighting of allowed states, the mean product of two distinctions is a sum over routes of −1/(2^(a−1) − 1) per knot of a places, normalised by the rings.
  - This reproduces `SIGNED-COUNT`'s −15/41, −33/95 and −3/13 (its README table, read).
  - On a start with no ring, functions unchanged by flipping every value, carried on disjoint sets of knots, are exactly independent.
  - So under that weighting the whole holds one bit, the flip of every value, and each knot between two parts weakens their link by its factor.
  - `nae_carriers.py` asks only which tuples occur. A ring of four with one loose distinction per knot should have even ring parity in 50 of its 82 states.

## 2. Smallest starts

- **Census size:** the chain (0,1,2), (2,3,4), (4,5,6).
  - It has 54 states and three composed relations.
  - The one on the loose set misses only (0,1,3,5,6) = (v,v,v̄,v,v).
  - Each grouped fact there is read by one knot.
- **Facts carried by two knots each (T7):** (0,1,2), (0,3,6), (1,4,7), (2,5,8), (3,9,10), (4,11,12), (5,13,14).
  - It should have 4,374 states.
  - Fact g_i sits on {6+i, 9+2i, 10+2i}: + at (1,0,0), − at (0,1,1), 0 otherwise.

## 3. Candidate second-layer knot and what refutes it

The candidate on T7: (g_0, g_1, g_2) is never (+,+,+) or (−,−,−). Predicted: 25 of 27 triples occur, every pair takes 9 of 9, and the loose set shows 510 of 512 patterns.

- **Refutes lemma G:** any other count on the loose set.
- **Refutes my reason in 4:** rename 11 as 9, so the knots are (3,9,10) and (4,9,12) and a ring of five closes. All 128 patterns of the seven loose distinctions should occur. A missing pattern means a ring carries a relation.
- **Growth:**
  - T7 should stall in round 1, since each of (0,3,6), (1,4,7), (2,5,8) lies in two groups with one loose distinction.
  - With 15, 16, 17 added to those three knots it should have 55,566 states, show 4,094 of 4,096 loose patterns, and show every loose pattern after one round.
  - I did not open the engine; this rests on the hivemind's standing facts.
- **Why it is not a new layer even if all this holds:** it is (0,1,2)'s own law read through relays. Whenever g_i is nonzero it fixes distinction i.

## 4. Strongest reason for no second layer

- A parity knot passes a value on from any place. A not-all-equal knot passes one on only when all its other places are fixed and equal.
- So every exact relation is a composition over a ring-free part, and a ring erases it. This is the reverse of parity, where rings carry the facts.
- Two-parent births close rings, since the parents already share a neighbour. So nothing should bind the loose set after the first such birth.
- Prediction on the census: the loose set shows 2^m − 2 patterns on tree-shaped starts, 2^m on the others, and 2^m on every start after one round. Parity shows 2^(m−1) always.
- A referee will press lemma F first, then whether composition counts as "held by the whole".

## 5. Census start 959

- **It is the record's Pasch pattern** (read): `OVERLAP-READ-20261111-001` conclusion 2, `STATES-GROWTH` A1, `MANY-VALUED`, and the 20 November theorem. The study's own files do not cite it.
- **What is different about it:**
  - Its distinctions fall into three pairs no knot holds together: {0,5}, {1,4}, {2,3}.
  - The 18 states are exactly "some pair 00 and some pair 11".
  - All eight triples taking one from each pair are relations; the knots are four of them and the second presentation is the other four.
  - Exchanging the members of one pair swaps the two presentations.
  - Each second knot is a first knot read through the other three: 3, 4, 5 all v forces 0, 1, 2 all v̄.
- **Is it the only kind?**
  - Within the theorem's class, yes, by the record's proof.
  - Outside it, the referee's kind: a redundant law laid on a composed relation with no place reversed. So the relations of 1(b) are exactly the room for a second presentation.
  - A knot with a spare place (`MANY-VALUED`'s (1,2,4,5,6)) is a third candidate. The loose mark removes that example, and I built no other.

**Not opened:** the growth engine, `knots.py`, `recovery_argument.md`.

**Hivemind:** one consultation entry and one standing fact (the prior classification and 959) added to `docs/ADVISOR_HIVEMIND.md`, both dated 2026-11-27 to match the log; nothing else touched.