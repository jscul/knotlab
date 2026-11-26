# What differs between two orders of filling in (a note after the referee)

At the coordinator's request, after referee R1's third Block ("admission order can change the intermediate view"). Read
from the referee's own witnesses ([`referee-R1/challenge.json`](referee-R1/challenge.json),
[`referee-R1/weighted_example.json`](referee-R1/weighted_example.json)); nothing new was computed.

**What differs: only whether the part being computed stalls.** On the 14-knot start (reader U1, not-all-equal), 64
regions hold the reader's knots within t + 1 steps; 60 grow and give exactly the full growth's view, and the other 4
stall in round 1 and give no view at all ("regions by end and comparison": 60 grow and agree, 4 stall and differ). The 180
of 720 orders "with a differing prefix" are the orders that pass through one of those four regions on the way. No order
reads a birth in another round, and no order records a different birth, a different kind of birth or different parents:
each intermediate reading is either the full view or nothing.

**Why a part stalls.** On the 25-knot start, the reader's part within two steps holds A, B, C and V but not X. In the
whole start A, B and C join X in one group of four and each joins V in a pair, owing two distinctions each, which they
hold. Without X the group of four is gone, A, B, C and V lie in one holder's block, every pair among them counts as a
group of its own, and A, B and C each owe three and hold two: they are short, and a short knot stops the whole growth
(lesson 8.1). Adding X restores the group and the view. So which order fills in X relative to the knots it groups decides
whether some intermediate part is short.

**Bookkeeping, not something a reader holds.** The difference belongs to the outside computation, which grows a part of
the start as if it were the whole: the model grows the whole start once, with no admission order, and in it no knot is
short. Inside the model no reader can see or hold which order an outside computation used. The difference is two-valued
only in the trivial sense (the part grows or stalls), carries no natural sign, and disappears once the part's knots are
funded as in the whole. It is not a case of the order of looking changing what is seen in the model: it is the earlier
theorem's funding premise failing for a cut part.
