# Advisor answer for `THIRD-LAYER-20261126-001`

The step does not repeat by itself. I think ordinary growth gives a connected start exactly one second-layer knot, so there is no cycle at layer 2 and no third layer made by growth. Everything below is by hand with no run, and is `unverified` unless I say a line was read.

**Read:** the hivemind, `BUILT-BINDING` README, decision, referee report and argument note, `repro.py`, `built.py`, and `fastlib.py` lines 12–22 (the candidate rule).

## The main claim: two kinds of fact, and one second-layer knot

**Families.** `fastlib.candidates` (lines 12–22, read) makes two live knots candidates only through a common neighbour `w`; `w` may hold no loose distinction. Call the classes of live start knots under chains of candidates *families*. A birth shares distinctions only with its parents and children, so no birth should have ancestors in two families (`unverified`; check on the birth records).

**Claim T (two kinds).** Let f be a parity on the start's allowed states, and ℓ_A the parity of family A's loose distinctions.

- **Lasting.** If f is a sum of some ℓ_A (mod laws), the least change flipping f at round t is at least 2(t + 1) plus the shared distinctions on a route between two families.
  - Reason: summing the laws of A's lineage shows a change odd on ℓ_A uses an odd number of that lineage's newest loose distinctions, and it must do the same in a second family.
- **Bounded.** Otherwise f is odd on a change with an even number of loose distinctions in every family.
  - Such changes are spanned by closed start changes, pairs at one knot, and `loose_a, x(a,w), x(w,b), loose_b` for candidates a, b.
  - Each of these stays a stage change of fixed size at every round (the last closes through the common child).
  - So the least flipping size is bounded by a number the start fixes.

**Corollary (one knot).** A sum of start laws supported on loose distinctions has equal coefficients across every shared distinction, so it is all the laws of a connected part or none. This is premise 3 of the referee's argument note (read). So the ℓ_A of a connected start obey exactly one relation, the sum of all its laws.

**Agreement with the record** (as written in the hivemind and the referee report; I did not recompute any of it):

| Recorded | What T gives |
| --- | --- |
| Even rings: each carrier splits into two unread facts; six or eight facts take all 32 or 128 even tuples | Alternate ring knots are two families (p and p + 2 share p + 1); one relation |
| Joined rings of four keep 2, 3, 4 whole-held facts (9, 13, 17 knots) | If each joining knot touches one knot per ring: 3, 4, 5 families, minus one |
| Odd rings' label capped by n; even rings' class "fixed by loose values" | An odd ring is one family (ℓ ≡ 0) and its label is bounded; an even ring's is ℓ |
| Least flipping change 5, 7, 9, 11 | p + 2t |
| A loose distinction at a detour's middle knot frees all 2^R | It is a new family, so the one relation now includes it |

**Checks that could break T:**
- Least flipping size of each ℓ_A on rounds 0 to 6: is it p + 2t exactly?
- For fixed k, the number of class facts under changes of at most k should be constant in t once 2t + p > k.
- No class fact outside the span of the ℓ_A should have a least flipping size that grows past round 1.
- A start where one knot has live neighbours in two rings: those two families must merge and one fact must disappear.

## Question 1: the smallest start

**With loose-parity facts, none can exist.** By the corollary, a ring cannot sit in two groups: its dead-knot sets cannot cancel, because the only law-sum supported on loose distinctions is the sum of everything. That is the difficulty you hit by hand.

**With facts on shared distinctions, your overlap route gives no shared fact.**
- Take ring e with dead knots a_e, c_e attached to two hubs V and W (pairs J, K sharing v, as in `built.py`).
- The flows g_{e,V} = t^V + u^V and g_{e,W} are separate facts, with z_e = g_{e,V} + g_{e,W}.
- z_e is the ring's own loose parity, so the ring is a second-layer knot of three places whose loose distinction is z_e, not a shared fact.
- The resulting layer-2 pattern has a loose distinction at every ring, and its weight-4 elements (z_e, g, g′, z_e′) span all of C2, so there is no layer-3 fact.

**A candidate that does carry one is closed and does not grow.**
- Take a pattern G whose least loops have six links and do not span its loops. Example: four knots in a ring twice over, joined by four rungs, every ring link subdivided once (16 knots, 20 links, four loops of six, ring loops of eight).
- Double every knot V into J_V, K_V sharing v_V.
- Make every link e = (V, W) a bundle: t_e between J_V and J_W, u_e between K_V and K_W.
- This gives 32 knots and 56 distinctions, none loose.

Predictions for it:
- The shortest change through each distinction is the loop of four (t_e, v_V, u_e, v_W).
- Layer-2 facts: z_e = t_e + u_e, 20 of them, each unread at one knot.
- C2 is G's loop space (5 values); the layer-2 knots are 16 (8 of three facts, 8 of two).
- C2's shortest elements are the four loops of six.
- Layer-3 fact: z_e + z_e′ for one upper and one lower ring link of the same segment, flipped only by a ring loop of eight.

In the stage's own terms this is three sizes of closed change: 4, 6 and 8. I did not search exhaustively for a smaller one.

## Question 2: controls

For claim T:
- **Removes a fact:** one knot with live neighbours in two families.
- **Frees the tuple:** a loose distinction at any knot outside the chosen families.
- **Kills it:** reading changes of at most p + 2t; or a rule that lets two lineages share a child.

For the closed candidate:
- **Removes layer 2 locally:** delete one v_V.
- **Removes layer 3:** make G's ring loops six.
- **Kills layer 3:** read changes of at most eight.
- **Frees:** two loose distinctions at one J_V.

## Question 3: the collapse argument and your definition

- **The collapse is right.** A layer-3 fact pulls back to a class fact that is also even on the lifts of the layer-2 small changes.
- **A layer number is not a property of a fact.** Any grouping of knots gives a quotient start (bundles between groups as distinctions, each group's law-sum as its law). The same parity is layer 2 for one grouping and layer 3 for a finer one.
- **Your definition depends on the chosen family.** The referee found two valid families on even rings. With the families' parities, C2 is the even-weight code, its pairs span it, and there is no layer-3 fact on any start.
- **What is native** is the least size of a change flipping a fact, round by round. Claim T says growth sorts facts into two kinds only, so it makes one separation, not a tower.

**An attack on the built bindings themselves.** On the 32 ring families, take e_rs, the parity of one connecting knot's two attachment distinctions.
- It should be a class fact whenever z_r is, and it is read by that single knot.
- The e's should take every tuple, with z_r the sum of ring r's e's.
- The recorded rule is then "each e counted twice".
- e_rs should stop growing at the closed loop through all three links (12 for split with double links), while z_r keeps growing.

Check with `repro.analyse`, using each connecting knot's attachments as carriers. This suggests a stricter test of whole-held: not in the span of class facts read at single knots. The 14-knot start should pass it (I found no single-knot class fact at J, a_i or b_i).

**The honest stop**, as I would word it: ordinary growth's own facts are the families' loose parities, bound by the one law that is the sum of all the start's laws; any further layer is in the start's closed changes, built in, and growth leaves it as it was. Only the forbidding cuts add relations among family parities (referee fix 4: seven constraints at round 1 on the six-knot-ring arity-floor starts). That is the one place a second layer with several knots made by a growth rule could be looked for.

## Question 4: proofs already in the record, and the conjecture

- **Argument note** (pairs and loops of four): class facts are start parities. Its premise 3 is the component lemma that gives the one relation.
- **Closing law:** the one second-layer knot is the law growth reads when it closes; one family means ℓ ≡ 0.
- **Projection lemma:** start representatives.
- **Lemma R and the birth identification** (standing fact "What the growth reads"): no birth across families.
- **Reach bound** (`INFLUENCE-CONE`): the 2t lower bound.
- **`RELAY-IDENT`:** its "pieces" may be these families; check the definition before using the word.

**Conjecture.** For a funded ordinary parity growth from a connected start with families A_1 … A_m: for every k there is a T of about k/2 such that for t ≥ T the class facts under changes of at most k are the span of the ℓ_A (m − 1 values, one relation) plus the start parities even on the closed start changes of at most k and on the candidate loops. The second part does not depend on t.

A referee would press first on rounds where a birth gets one fresh distinction and has no sibling, on the shortest-change reading (ties), and on whether "no birth across families" survives capped groups.

The hivemind has one new entry (`unverified`); nothing else was touched. The file had changed on disk since I read it, and the edit applied cleanly under the marker.