# What lies beyond rejection: the whole-round response, and weights that cancel

Epic `BEYOND-REJECTION-20261126-001`, under G18, at the coordinator's pick after
[`FORBID-EDITS-20261126-001`](../FORBID-EDITS-20261126-001/decision.md) (a join that forbids, with free local edits,
acts as a local rejection). That study left two routes to a table beyond the classical bound: a joint response that
does not signal, or weights that can cancel. Part A tests the first on the one joint response the record has; part B
scopes the second. A check by the thread; computed; referee pending.

## A. The whole-round response under every sender policy ([`lp.py`](lp.py))

The earlier edit study's preparation (`WHOLE-STAGE-SETTINGS-20261120-001`, its 56-knot construction): four
preparations (u, v), each reader's three terminal values, carried to the other end through correspondences whose net
interchange is the identity unless u = v = 1 (then a cycle of the three values) under parity; any values under
not-all-equal, where every combination is allowed. A free address x (y) funds the whole round exactly when x = u and
y = v, otherwise it stalls; a reader reads 1 when its round is funded and its first terminal is 1. Its complete record:
its preparation bit, its three terminals, whether its round was funded (the newborns add fair values that change
nothing here). The weighting is free: any nonnegative weighting of the preparation's allowed states, so on these
records any distribution on the allowed (u, v, terminals). Exact linear programs:

1. **Calibration.** The uniform weighting gives correlations (1, 1, 1, 3/4) and CHSH 9/4, the earlier result.
2. **Fixed addresses, every complete record unchanged by the far address.** The largest CHSH is **7/3** under parity
   (the twelve worlds with one terminal value 1, equally weighted) and **5/2** under not-all-equal's support. Above the
   earlier 9/4, so 9/4 was not the most this response gives; 5/2 is the ceiling of any response that stalls three
   trials in four (each stalled trial reads 00).
3. **Every sender policy.** Let the sender choose its address from its own visible record. The receiver's record must
   then not depend on the sender's choice, which is the same as: the receiver's record jointly with the sender's visible
   record does not depend on the sender's address. **No weighting satisfies this** under either knot law: the sender
   sees its own shortage, and supplying it or not changes whether the receiver's round is funded. If the shortage is
   hidden from the sender (a policy reads only its terminals), the only weightings left fix every terminal, and CHSH is
   exactly 2.

*Expected, worked out by hand before the program was written:* 7/3, 5/2, no weighting, and 2. All four held.

So the whole-round response, the one joint response the record has, gives no excess that survives a free sender: the
earlier study's proof (a common distribution follows when no policy signals) holds on its own preparation with the
weighting chosen freely. Prior work: `WHOLE-STAGE-SETTINGS-20261120-001A-P001` (the proof); this adds the exact
optimum under fixed addresses and the check that no weighting escapes it.

**With signed weights ([`lp_signed.py`](lp_signed.py), the advisor's number).** Drop nonnegativity from the weighting,
keeping every observable probability nonnegative (the joint distribution of the two complete records in each address
pair): with the sender seeing its shortage, no signed weighting satisfies policy no-signalling at all; with the shortage
hidden, the largest CHSH is still exactly 2 (no signed weighting reaches 2.001), under either knot law. No amount of
cancellation rescues the whole-round response against a free sender.

**Not shown.** Other joint responses (a contact between readers was read in the forbidding study's addendum: no excess);
records with more content than the three terminals (they can only add constraints); not-all-equal's actual completion
counts (the weighting is free, so they do not enter).

## B. Where the recorded model makes something cancel (a scoping note)

The coordinator's question: list every place the recorded model already produces something that cancels; for each, does
it arise from growth or from a choice of ours, and could it weight whole configurations (a signed weight on each allowed
state)? Reviewed with the advisor ([question](advisor_question.md), [answer](advisor_answer.md)). One fact frames it:
every table in which far settings change nothing is the marginal of some signed weighting of joint assignments
(Abramsky and Brandenburger, *New Journal of Physics* 13, 113036, 2011), the literature's PR box included. So signs can
always give an excess; the only question is whether a sign the model already makes does.

| # | Where | What cancels | Growth or our choice | Weights whole configurations? |
|---|---|---|---|---|
| 1 | The parity knot rule | Adding parity equations cancels shared distinctions in pairs; growth uses it (a birth gets no fresh distinction where its inputs already imply the law; `GROWTH-SIGN-LAW-20261125-001`, the three-copy circuit) | Growth (the knot law) | No: it decides which states are allowed and weights none |
| 2 | Two passes of a shared distinction | x + x = 0 in a sum of characters; a knot's character (−1)^(sum of its places) is +1 on every allowed state | The knot law | Only trivially: constant on allowed states |
| 3 | The signed knot law +--- on 000, 011, 101, 110 (`INTERFERENCE-20261029-001`; i^(weight) on even words) | The two fillings of the three-copy circuit cancel (1 − 1 = 0); every three-bit knot is a signed sum of pair functions over one hidden bit; with phase-sensitive reads it gives every three-reader probability (`WEIGHTED-KNOT-FOUR-SETTINGS-20261125-001`) | A choice: the signed witness reading is the owner's working reading, the sign law is chosen, and growth selects neither (`GROWTH-SIGN-LAW-20261125-001`) | Yes, but used two ways: as an amplitude (squared at a value read, every phase vanishes and the unsigned table returns) or as a weight summed directly (a reading no record adopts) |
| 4 | The reversal sign (−1)^C(k,2) (`REORDER-CONFIRM-20261126-001`) | The round's own order (every parent before any child) gives a word of weight k that sign under the swap rule | The order is the round's own; the swap rule is added (A275) | It is a pairwise sign, ∏ over pairs (−1)^(x_i x_j); on words of fixed parity it is a product of per-reader phases (diag(1, i)), so on one knot it is a local adjustment; on structures whose words vary in parity it is not |
| 5 | The exchange sign of crossing lifetimes (the literature's Wick sign; `REORDER-SIGN-20261126-001`) | Two occupied parents whose lifetimes cross cost −1 | The schedule is supplied (A279 weights schedules equally); the line stopped | Yes, truly pairwise, but no rule of the model selects a schedule that carries the contradiction |
| 6 | Orientation signs of matching counts (the literature's Pfaffian or Kasteleyn signs; the native scan of 31 October, its Pfaffian graphs) | Signed weights on matchings that make a determinant count them | The orientation is ours | Yes; the same mechanism as row 5, with the orientation supplied |
| 7 | Not-all-equal's completion matrix K = [[3,2],[2,3]] | Its antisymmetric mode (1, −1) carries the correlation along a chain | The knot law | No: K is positive; the mode is a signed direction of a nonnegative weighting |
| 8 | Complement symmetry and antiperiods (the odd harmonies) | States come in complementary pairs; an antiperiod returns a pattern flipped | The knot law | A two-valued character, which complement-symmetric weightings give weight zero |
| 9 | Basis changes (holographic transforms; the native scan's y-basis, x² = −1/3) | Signatures with signs after a change of basis | Our choice of basis | Only in the transformed frame |
| 10 | Counting identities (point splitting; inclusion–exclusion over knots) | Signed sums of counts | Arithmetic | They weight different structures, not the states of one |
| 11 | A knot's co-information (parity: −1 bit on every allowed word; not-all-equal: log2(8/9)) | The knot's interaction term is negative | The knot law | A logarithm of ratios of a nonnegative weighting, not a weight |
| 12 | The whole-round response with signed weights (part A) | — | — | Allowed any signs, it still gives no excess against a free sender |

**The note: none exists in the recorded laws.** Every cancellation the recorded model makes by itself (rows 1, 2, 7, 8,
11) weights no configuration, or weights them all alike. Every signed weight on whole configurations in the record is a
choice of ours: the sign law and its reading (3), the swap rule (4), the schedule (5), the orientation (6), the basis
(9). The one sign the round itself orders (4) is a product of per-reader phases on words of fixed parity, so it changes
no table there. And the one joint response the growth makes (part A) stays classical against a free sender even with
signs. So a quantum table needs a sign the model does not yet make; the earlier stop of the reordering line (reopen
only on a growth rule that forces the carrying class of schedules) is where a native sign would have to come from.

### The frozen confirmation test (not run)

Frozen with the advisor as a cheap confirmation of the note, not as a candidate; run only on the coordinator's word.
`forbid.py`'s census starts, edits, readers and one round, unchanged; exact arithmetic over Gaussian integers; the
signed weight of each allowed state summed directly (a reading of its own, to be registered when run):

| Variant | Weight on each allowed state |
|---|---|
| V1 | (−1)^(shared distinctions holding 1) |
| V2 | V1 × i^(loose distinctions holding 1) (the signed law of row 3) |
| V3 | V1 × the reversal sign of row 4 |

Gates per placement, in order: G0 all four normalizers nonzero; G1 every entry real and nonnegative; G2 the four
normalizers equal (a failure is recorded as signed local rejection, not a hit); G3 every complete record unchanged by
far settings; G4 CHSH above 2. A hit passes all five. Controls: the unsigned weight reproduces the census's counts
exactly; a hand-built signed PR weighting passes G0 to G4. **Prediction (the advisor's, about 85% confident; mine the
same):** zero hits in all three variants; parity structures fail G0 or reduce to the unsigned table, not-all-equal
structures mostly fail G1 and the rest are classical or fail G2. Any hit would be "the supplied sign under a supplied
reading", with the sign law, the direct-sum reading and the reader set each named as a scaffold.
