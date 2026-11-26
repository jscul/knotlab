# The advisor's answer (26 November 2026)

To [the question](advisor_question_2.md), asked before the two studies after the first checkpoint were run.

Nothing below was run; it is reasoning from the rules as you stated them.

**1. Not forced as stated; a local version probably is.**
- **What looks provable:** a far change travels only by toggling someone's shortness. With shortness fixed, one more loose distinction only adds an offshoot, which joins its parent's existing group and alters no one's owe or D (check the maximal-clique clause). A non-short member acts and leaves in its first round, so only waiting knots carry anything across rounds. That gives: every far hearing passes along a chain of knots that waited.
- **Where your rule can fail:** the last knot of the chain need not be A's own, and A need not be wholly short.
  - *Partial jam:* one own knot waits at the site while another branch of A grows.
  - *Mixed neighbour:* an own knot c that is not short shares a group with a mixed knot m (a join of A's and the link's lineage). If the change toggles m's shortness, the group {c, m} is cancelled or kept, and c makes an own offshoot instead of feeding a mixed join. A's own births then differ with no own knot short. This boundary renews each generation, since c's own offshoots are siblings of the join (c, m).
- **Verdict:** the rule is empirical and the test is not empty. The D point matters only through m.

**2. Three ways it is nearly vacuous.**
- **Forever-jammed receivers:** a jammed A makes no births, so any birth is a hearing and "hearing ends a jam" holds by definition. Prediction 2 has content only where A is not jammed for the whole baseline.
- **The "without or with" clause:** it doubles the rounds that satisfy the rule.
- **Receivers with no members:** they cannot hear anything.
- **What to report:** the denominator, meaning the number of (pair, law, round) cases where A has members, is not jammed in either growth, and a waiting chain from the change exists. If that is near zero, the test showed nothing.
- **A stronger statement:** per knot, every own birth that differs has a parent, or a group partner of a parent, that waited the round before. Also: the hearing round is the count of waiting knots between plus a constant.

**3. Predictions I expect to fail, and missing controls.**
- **Study 2 (1):** at risk from the mixed-neighbour case.
- **Study 2 (6):** confounded. Multiplying receivers reach 1,500 knots in a few rounds, so they are watched for fewer rounds. Report those as "not run", or compare at equal rounds.
- **Study 2 (4), first half:** by my arithmetic the two rations differ exactly when q = 1 and p ≥ 3, where the record gives 0 and the made one gives 1. They are identical on lines, where groups are pairs. They can differ for the ring and for starts with groups of three.
- **Study 2 (4), second half:** the cap bites only when D ≥ 4. A start with a knot in four groups could carry far.
- **Study 1 (4):** almost implied by item 1, so it carries little information.
- **Study 1 return detector:** in explosive growth, isomorphic five-member parts turn up by coincidence. Require the returned part to descend from the earlier part alone.
- **Missing controls:**
  - A stub at B for every receiver, to test that hearing does not depend on what B is.
  - A change of opposite sign, barring one loose distinction. Every change tested so far can only un-short, so nothing tests whether a jam can be sent.
  - d = 2 and d = 5 on a seeded sample, since the rule says "two or more" and the test has only d = 3.
  - A shared-distinction join in Study 2, because the meeting's extra distinction is itself a scaffold.

**4. Why FLOOR1 jams but does not thaw.** Under the one-fewer rations a short knot's shortfall, owe − h, is exactly 1, so one neighbour leaving cures it and the release propagates. FLOOR1 ignores D, so shortfalls of 2 or more occur, and one departure or one added distinction cures nothing. Check with a histogram of owe − h over the jammed roster: all 1 under the one-fewer rations, some ≥ 2 under FLOOR1. If FLOOR1 shows only 1s, this explanation is wrong.

**5. Closest known mechanism.** Threshold peeling, which the literature calls bootstrap percolation (equivalently k-core pruning with a threshold per vertex): a knot leaves once owe − h of its groups have dissolved. On the line every threshold is 1, which is an excitable medium with no recovery and gives your k + 3. Chip-firing is not it, since a departure lowers neighbours' demand and sends them nothing. Deadlock release is a fair gloss but not exact. It is an intuition, not evidence, and it covers only the jammed phase, not the births after.
- **Cheap identity:** take the jammed roster at round 2, compute the shortfalls and groups, and peel from the changed knot. That should predict the round each own knot first acts at d = 1..3, and the FLOOR1 stop.
- **Order test:** peeling is order-independent, so two changes in either order should free the same set.

**6. What sending again would need, and whether your test is fair.**
- **What the line needs:** to be re-armed, so the births of the pass must rebuild a chain of waiting knots with shortfall 1. In a fuse, neighbours are freed one after another, so their groups are cancelled and they make only offshoots. Offshoots share only with their parent, so the lineages come apart. Re-arming needs kept joins between neighbouring link lineages, which means both freed in the same round.
- **Structural check first:** after the pass, does any group hold knots of two link lineages, and does a chain of members sharing distinctions still run from the change to A's own? If not, "sent again" is decided without a run.
- **Fairness:** partly fair.
  - A second change at a spent knot puts it back on the roster. That is a new seed, not something B sent. Place it at a current member.
  - In the exploded once-changed growth, a hearing may come by local growth rather than along the line, so record the carrying chain.

**7. Words.** No new word is needed. Say "A's own roster is jammed", defined once as the record's word applied to the roster restricted to A's own members. For the partial case say "a waiting own knot". Do not let "jammed" cover it.
