dict_keys(['claude-fable-5-2'])
I ran nothing here; everything below is argument for you to check. The main result is that P3 looks provable from incidence alone, which makes NAE close to a degenerate arm.

## 1. Law-blind except at implied junctions

Yes, and it holds for every law that passes K2, not only NAE.

- **Keep clause.** "A junction with at least one fresh bit removes no old state" says the projection onto the old places is full. K2 gives that directly. Since the count max(d, 3 − p, 1) is at least 1, the keep clause never binds, and a knot law can only enter through "implied".
- **NAE on k bits.** It passes K1–K3 for every k ≥ 2. K1: all-equal is excluded. K2: any assignment of k − 1 bits extends, by setting the last bit against one of them. K3 is clear.
- **What changes with k.** It hides log2(2^k / (2^k − 2)) bits, which tends to 0, where parity hides one bit at every size. So "every junction is a knot" survives, but the many-place junctions are nearly empty knots. Say that in the record.

## 2. Can an NAE junction be implied?

Your argument is not valid as stated: loose bits are not jointly free just because each junction has one.

**A case.** Take the lone knot Q = (e1, e2, e3) after one round, with P_i = (e_i, b_i, b_i'). A six-place junction J on all six loose bits is NAE-implied: all b equal to 0 forces every e_i = 1, which violates Q. Your pilot avoids it only because the policy joins those bits in threes.

**Two exact lemmas.**
- **Swallow.** If J's old bits contain every place of an old junction, J is implied.
- **Two spare places.** Suppose every bit lies in at most two junctions and every junction has at least 3 places. If every parent keeps at least two places outside J, then J is not implied.

**Proof of the second.**
1. Delete J's bits and read what is left as a multigraph H: junctions are points, shared bits are lines, and remaining loose bits are pendant lines.
2. The classical lemma: a connected multigraph that is not an odd cycle has a 2-colouring of its lines in which every point of degree ≥ 2 sees both colours. Colour each component of H this way.
3. A component that is an odd cycle consists only of parents, since each of its junctions lost a place to J. Colour it all 1.
4. Set J's bits to 0. Non-parents see both colours, and parents see a 1 next to their 0. So an allowed state has J's old bits all equal.

Please check the cited lemma; I recall it from the Euler-tour proofs of edge-colouring theorems, not from a source in front of me.

**Consequence.** If, as you say, a new junction takes its old bits from different parents, each parent gives one place and keeps at least two. P3 is then a theorem, not a prediction. The census checks only its hypotheses:
- each bit lies in at most two junctions;
- every junction has at least 3 places;
- no parent gives a junction more than (places − 2) bits.

Log the minimum over parents of places outside J for every new junction. If it is always ≥ 2, the SAT calls are redundant; keep them as the independent check.

**Stronger form, same proof.** Any set S of bits that leaves every junction at least two places outside S is jointly free under NAE. NAE correlation only starts when some junction is taken to within one place.

## 3. The closed form

Probably exact, but freeze it as its own prediction and do not fold it into P2.

- **What is already forced.** In a connected start, parity implies exactly one junction, at the last round T. A span element supported on loose bits is a sum of whole components, so the top is the only one.
- **P1 caveat.** If any census arrangement is disconnected, one component can close while another grows, and P1 as worded misfiles it. Check for this.
- **The tail.** Under NAE the top gets one fresh bit and is then the only junction with a loose bit. The tail is the growth from that seed. It is universal only if candidates and lookahead never read back into the closed body.
- **Unit test.** Grow a single junction with one loose bit and confirm 1, 2, 3, 4, …. Then predict NAE − parity = y^(T+1)/(1 − y)^2 for every closing start.
- **One thing to explain.** Counts of 1, 2, 3, 4 are linear growth, which "two endless chains" would not give. Something in the tail branches. Say what before the freeze.

## 4. Bond distance

"Who joins whom" is identical by construction, so that sentence carries no information. I do not have the exact bond-distance definition in front of me, so I cannot say what the tables would show.

The sharp statement available without tables is the stronger form in section 2: under NAE, bits are jointly free until a junction is taken to within one place. A brute-force check of that lemma on small presentations (the ring of five, the two-ring join) is cheap and worth freezing as a control. I would not compute NAE bond tables unless the record is going to claim something about NAE bond distance.

## 5. A second arm

**One-in-three and majority are not knot arms.** Both fail K2: forget one place of one-in-three and (1,1) is still excluded; forget one place of the majority law and (0,0) is still excluded. They also break the keep clause, since no number of fresh bits rescues an old state with two ones. That makes them hub laws under a different policy.

**Among knot laws, parity is the special one.** It is the only law where implication is systematic, because it is linear. For any other K2 law, implication needs a near-swallow.

**A candidate.** Symmetric knot laws are exactly those whose forbidden counts are non-empty and contain no two consecutive numbers. "Number of ones not divisible by 3" is a uniform family at every size. It runs through the same SAT check, and I would predict it matches NAE. It is a cheap second arm, but it would confirm the same theorem again.

**Recommendation.** Run the NAE freeze as the check of a theorem (P3 proved, P1 and P2 following), with the tail form as the one real prediction. State the result as: loops keep branching under every knot law, and laws differ only in which closures become relays. If the coordinator wants a law that changes the branching itself, that needs a non-knot law and a changed keep clause. I would make that a separate ticket, not a second arm.
