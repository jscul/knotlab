# Is the sign the cost of reordering? Pre-registration

Ticket `REORDER-SIGN-20261126-001` (direction 1 of the owner's selection on 25 November, "take on direction 1"; goals G5 Dynamics
and G9 Witnesses), 26 November 2026. Frozen before the code is written. Code by this thread (Claude). The canonical K1–K3 test is
unchanged. The idea is the intuition "the sign as the cost of reordering" from the comparison of the program's signed records,
kept apart from evidence until this test.

## The question

The three-detector experiment of `WEIGHTED-KNOT-FOUR-SETTINGS-20261125-001` needs one supplied ingredient beyond the parity knot on
a, b, c (allowed words 000, 011, 101, 110): the signs `+---`, with the ordinary reading Z and the real flip reading X held fixed.
On the even words those signs are exactly the sign of listing the three distinctions in reverse order when swapping two
distinctions that both hold 1 costs −1. The growth law already leaves the commit order of a round's children free: every order
gives the same holdings after matching names (`GROWTH-SIGN-LAW-20261125-001`, `INFLUENCE-CONE-20261120-001`).

Add one rule and nothing else. **Swap rule S_s:** list distinctions in order of creation (old ones in their index order, then
each child's fresh distinctions in commit order); a listing's weight relative to a reference listing is s raised to the number of
pairs of distinctions that both hold 1 and whose relative order differs. s = −1 is the rule under test; s = +1 is the control.
Do the growth's own reorderings, under S_−1, supply the sign the experiment needs, with nothing supplied but the free settings?

## In standard terms

S_−1 is the fermionic mode-ordering sign (Jordan–Wigner). A swap of two adjacent occupied modes is SWAP·CZ, so S_−1 is the same
as "one CZ per crossing" and this design cannot tell exchange statistics from that. The test asks whether a GHZ contradiction with
real Pauli Z and X readings arises from the relative mode order of a growth round and its readers.

## The primary observable

Relabelling-proof GHZ score. For a signed preparation ψ on n readers and each nonempty set T of readers of even size, take the
correlation c(T) = ⟨X_T Z_rest⟩ with the two real readings held fixed. The preparation carries the **full contradiction** when every
c(T) is ±1 and T ↦ c(T) is not a character of T (no assignment of local ±1 answers fits). At n = 3 this is the product
P = ⟨ZZZ⟩⟨XXZ⟩⟨XZX⟩⟨ZXX⟩ = −1, where any list of local answers gives +1. Flipping the outcomes of one reader's X multiplies c by
a character, so the verdict is unchanged by real relabellings. Complex local phases are not relabellings here: diag(1,−i) turns X
into Y, and "signed preparation with X" and "positive preparation with Y" are one resource.

## Prior work in the program

`python3 -B scripts/track.py objects "sign of reordering births commit order exchange" --until 2026-11-26 --exclude REORDER-SIGN-20261126-001 --limit 3`

`python3 -B scripts/track.py objects "fermion exchange sign antisymmetric order of creation Jordan-Wigner" --until 2026-11-26 --exclude REORDER-SIGN-20261126-001 --limit 3`

`python3 -B scripts/track.py objects "funded children of a parity knot committed in any order" --until 2026-11-26 --exclude REORDER-SIGN-20261126-001 --limit 3`

`python3 -B scripts/track.py objects "order serial births one at a time" --until 2026-11-26 --exclude REORDER-SIGN-20261126-001 --limit 3`

`python3 -B scripts/track.py objects "births in opposite orders recomputed counts" --until 2026-11-26 --exclude REORDER-SIGN-20261126-001 --limit 3`

`python3 -B scripts/track.py objects "Mermin product real readings signed parity knot relabelling" --until 2026-11-26 --exclude REORDER-SIGN-20261126-001 --limit 3`

- `WEIGHTED-KNOT-FOUR-SETTINGS-20261125-001` — same object: the signed preparation, its real readers and the 64-cell target. This study asks where its signs could come from.
- `GROWTH-SIGN-LAW-20261125-001` — same population: the growth fixtures and the forward/reverse commit-order control. It showed ordinary growth carries any sign pattern unchanged; this study adds a rule that makes order carry a sign.
- `GROWN-OPPOSITE-READS-20261125-001` — the four-place cyclic starts and the production growth routine, reused unchanged.
- `FOUR-SETTINGS-PARITY-20261125-001` — the four-setting benchmark and the local ceiling 3/4.
- `INFLUENCE-CONE-20261120-001` — a relative: 5,040 and 120 supplied orders agree within their preparations, so a round's commit order is free under the ordinary law.
- `ROUND-FREE-20261119-001`, `LOCAL-ROUND-20261123-001`, `FRESH-DEMAND-20261120-001`, `GENERATORS-20261120-001` and `TICK-BIRTHS-AND-SCARCITY-20261121-001` — relatives: serial rules that recompute after each birth do depend on order (different counts by the fourth event). That is a different object, a change of outcome, not a reordering of one outcome; it is out of scope here.
- `REVIEW-LEADS-20261123-001` — the Bell ceiling with one shared distinction; its order counts of donor payments are unrelated to signs.
- `IDLE-PHASE-AND-TREE-CLOSURE-20261121-001` — a relative: an exchange of whole allowed words, whose compensated phase is fixed at z² = i (roots ±exp(iπ/4)) once a coherent reference is supplied. Not the exchange of two distinctions tested here.
- `ERASURE-AND-CLOSING-SIGNS-20261121-001` — a relative: signed permutations with value readout give zero phase contrast; a supplied coherent law gives a sign-sensitive keeper.
- `TWO-KNOTS-ONE-DECISION-20261121-001`, `TWO-READERS-ONE-SURVIVING-SIGN-20261121-001` and `SPLIT-KNOT-METER-AND-CLOSING-TRIPLE-20261121-001` — relatives on reading a joint sign; each needs a supplied coherent meter or reference.
- `JOINT-BRAID-READS-20261114-001`, `GROWTH-STATISTICS-20261121-001`, `FEEDER-PAYOFF-REVERSAL-20261121-001` and `THREE-SIBLING-PAID-EVENT-20261122-001` — unrelated (matched on "order", "commit", "exchange" or "children" only).
- `INTERFERENCE-20261029-001`, `SIGNED-JOINTNESS-001` and `KNOT-LOOPS-20261019-001` — relatives: signs let two-place pieces build every three-distinction knot; signed returns and contact phases are invariant under local rephasing but supplied; a ring of knots excludes a word exactly when an odd number of its transfers swap.

## Prior work outside the program

The swap sign is Jordan and Wigner's (1928). Mermin (1990) gives the n-reader contradiction; real amplitudes suffice (McKague,
Mosca and Gisin 2009). The removability criterion below is the polar form of a quadratic form restricted to a code (Dehaene and De
Moor 2003; Van den Nest, Dehaene and De Moor 2004); weight/2 mod 2 is linear on an even code exactly when the code is
self-orthogonal (MacWilliams and Sloane). Real-reading stabilizer fragments are noncontextual (Delfosse, Allard Guerin, Bian and
Raussendorf 2015); the toy model differs from stabilizer theory by this sign (Spekkens 2007; Pusey 2012). Mode-ordering ambiguity
and parity superselection: Wick, Wightman and Wigner (1952); Bravyi and Kitaev (2002); Friis, Lee and Bruschi (2013). A coherent
sum over orders is the literature's quantum switch (Chiribella et al. 2013). What the program would add is the link to its own
growth: whether its free commit order supplies the sign.

## Settled by construction (stated, not tested)

- **L1.** For even k, (−1)^(k(k−1)/2) = (−i)^k. On even words the full-reversal sign is diag(1,−i) at every reader, so the
  reversal-signed n-distinction parity knot with Z and X has the same table as the positive one with Z and Y, for every n.
- **L2.** Under S_−1 a commit order π of a round's children gives each grown word the sign (−1)^q, q = Σ over pairs of children
  inverted by π of p_i·p_j, where p_i is the parity of child i's fresh distinctions (equal, for a parity child, to the XOR of its
  inherited distinctions). q depends only on the old word. (−1)^q is undone by real relabellings exactly when its polar form
  vanishes on the allowed words.
- **L3.** On the three-distinction knot the six orders give the six patterns ++++, +++-, +-++, ++--, +--+, +--- (minus signs =
  inversions); ++-+ and +-+- come from no order. Odd orders give P = −1; even orders give mixed correlations 0.
- **L4.** A coherent equal-weight sum over all commit orders (reading R2) vanishes on every word where two or more children have
  odd fresh parity: Σ over S_m of the sign is 0 for m ≥ 2. On the ternary only 000 survives.
- Squared weights are supplied (A144). They are only exercised where magnitudes are equal.

## Readings of "nothing chooses an order"

- **R1** orders recorded and known to the readers, with the readers' reference listing supplied;
- **R1b** orders recorded but unknown to the readers (equal weight over the orders the growth allows);
- **R2** orders not recorded (coherent equal-weight sum);
- **R3** the readers' records are children born in the same round as the preparation, listed by the same rule;
- **JW** the swap rule applied to the readings as well (each changed reading carries its ordering string).

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Gate. A direct count of inverted occupied pairs over the full listing equals the block formula of L2 on every grown word, order and fixture. The real benchmark reproduces the 64-cell target for `+---` with X and `++++` with Y. A mutant using s = +1 in place of −1 must fail the target. | any fails |
| P1 | L1 and the full contradiction for the reversal sign hold exactly for n = 3 to 8. | any n fails |
| P2 | At n = 4 and 5 (one parity knot, all n! orders), the full contradiction appears exactly for the n orders that reverse a prefix and the complementary suffix separately, and the invariant is the polar form, not the parity of the order: at n = 4 the full reversal (even) carries it and a single swap (odd) does not. At n = 6 (720 orders) the same count n holds. | another order carries it, one of these does not, or parity predicts it |
| P3 | Growth fixtures under S_−1 (one ternary and its three children; the three-ternary ring; three, five and seven four-place knots in cyclic order; two ternaries sharing two distinctions). On the ternary, the grown preparation read by block readers (each reader holds its old distinction and its child's fresh pair, logical Z = Z_x, logical X = X_x·X_y) carries P = −1 exactly for the three odd orders relative to the production listing, and the table matches the 64-cell target up to real relabelling. The three-ternary ring carries no sign (its only child has no fresh distinctions). For the rings, record which orders give a nonvanishing polar form; no prediction on counts. | the ternary result differs |
| P4 | R1b: averaged over the orders the round allows, with the readers not told the order, no fixture's GHZ score exceeds the local bound (ternary: Mermin score 4/3 over the odd orders, 7/6 over all six, against 2). | any average exceeds the local bound |
| P5 | R2: the coherent sum leaves exactly the words with at most one odd child; on the ternary only the blank word, so the knot is lost. The other one-dimensional weighting of orders (by the sign of the order) also loses it. Under s = +1 the knot survives with no signs. | any differs |
| P6 | R3: when the readers' records are born in the same round and listed by the same rule, the relative order is the identity and every order gives the positive class (mixed correlations 0). | a contradiction appears |
| P7 | JW: with the rule applied to the readings too, the 64-cell table is the same for every commit order (order is gauge), and it is the positive class's. | tables differ across orders |

Verdict rule. **Success** only if a full contradiction follows from the growth's own reorderings and S_−1 with nothing else supplied
but the free settings, under some reading other than R1. Otherwise the result is the name of what must still be supplied. The
expected answer, written before the run: a specific relative inversion between the preparation's commit order and the readers'
listing, of the prefix/suffix kind, which is the phase reference again in the form of an order.

## Runs and stop rule

Exact integer arithmetic in one Python process: at most 720 orders and 2^6 words per order for the knot census, and the
production growth routine on fixtures up to seven knots (at most 5,040 commit orders of 2^15 grown words in rank form). The first
small case is timed before the rest; the expected total is under a minute. No long-running row. Stop after the gate, P1–P7 and the
scaffold variations below.

Scaffolds varied: the reference listing (production order, its reverse, and every order for the ternary); s = +1 against −1; the
block readers against reading the old distinction alone (which decoheres to the dephased table, 5/8); outcome relabellings.

The advisor model was consulted on the design before freezing (served as `claude-fable-5-2` through the `claude-fable-5-1` alias,
since this host's CLI rejects the explicit 5-2 name). It found that the first design could only confirm its prediction, gave the
n = 4 counterexample to the parity reading and the prefix/suffix criterion, proposed R1b, R3 and JW as the decisive
falsifiers, and supplied the literature above. A peer session on the meeting-studies line suggested the relabelling-proof product
and the list of inverted pairs. Both reviews are colleagues' views; the run checks them.
