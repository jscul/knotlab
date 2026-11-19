# Advisor answer: JUNCTION-KINDS before the freeze

## 1. Is the reading right?

It is half right. The conclusion, that kinds of junction are the wrong carrier, is probably correct. The argument, that unbounded degrees make a finite transfer impossible, is not valid as stated.

**Unbounded degree is not an obstruction.** If every round-t junction had t children with t parents each, every share would be 1/t, the out-share would be 1, and one class with M = (1) would be exact. What matters is how many distinct share profiles occur.

**Counts alone can never refute a finite transfer.** A sequence with c(t) = c(t − 2) + c(t − 3) is carried by the three-letter substitution a → b, b → c, c → ab, whose matrix has characteristic polynomial x³ − x − 1. So a three-class partition with N(t+1) = M N(t), M ≥ 0, exists whenever the start values fit. Any impossibility claim has to be about which partitions count as native, and about the 1/p share convention.

**The strongest true statement I can give** is for exact per-junction transfers:

- Let s(j) = Σ over children of 1/p(child) be the out-share of j. If every junction of class l sends total share M_kl into class k, then s(j) = Σ_k M_kl is constant on each class.
- So if s takes unboundedly many values over the rounds, no finite partition has an exact per-junction share transfer.
- The partitions that do have one are exactly those refining the coarsest sum-equitable partition, where you refine by the total share sent into each class.

**Your pilot fact 3 does not yet settle this.** It refines by the multiset of (kind, 1/p), which is finer than the transfer needs. Two children at share 1/2 and one child at share 1 into the same class are the same for M. Rerun the refinement with sums, or just count distinct s values.

**A coarse partition can still work on average.** N(t+1) = M N(t) only needs class totals to follow M, and refinement cannot detect that. Your "one class per residue" idea lands here, with two caveats:

- A junction spans many turns of the loop, so it has no residue; only its ends do.
- Classes by end type are finite in the cover model. Their counts obey a recurrence reaching back two and three rounds, because a turn adds 2 or 3 points. That is not a one-round M.

A one-round M needs classes like the letters a, b, c above, meaning "rounds since the last whole turn". That label is not local; it is induced by a spine. So a working coarse partition and candidate (c) are the same object.

**A guess, not checked:** parent counts grow linearly because each turn's optional spare is a removable point, so p ≈ ends + spares. If so, s(j) does take unboundedly many values and your reading holds for exact transfers.

## 2. What should replace kinds of junction?

I recommend (c), defined through (a), with (b) only as bookkeeping.

**Why (c).** In the cover model, W = y²(1 + y) says one turn adds 2 points, or 3 with its spare. Peeling the last turn at one end of a cluster leaves a connected cluster of round t − 2 or t − 3. That cluster is an ancestor, since the points come off one at a time from the end. This is the recurrence as a bijection, and it uses only the parent relation.

**Why it needs (a).** "Which end" is a choice. Two fixes:

- Count ended junctions, the pairs (junction, end). The peel map on these needs no choice.
- Or show that one end is natively marked.

**Checkable definition.**

- Let A₂(j) and A₃(j) be the ancestors of j exactly 2 and 3 parent steps up.
- For each such ancestor a, record the type of the interval [a, j] in the ancestor order: the junctions between them and their parent relations, up to isomorphism.
- A spine is a set T of interval types such that "a is a T-ancestor of j" is biregular with one constant e between round t and rounds t − 2 and t − 3 together. I expect e = 1 or 2.
- The ends of j are then its T-ancestors, read from parents alone.

**Why not (b) alone.** Kinds of loose bit inherit the unboundedness of fact 1: body bits multiply with size. They help only in telling end bits from body bits.

**Where I am unsure.** In the break shapes the cover model is wrong, so the ancestor order may not have peelable turns at all. The recurrence could hold through a cancellation, with no bijection along ancestors.

## 3. Frozen test

1. **Out-shares are unbounded.** In all ten starts and all five catalogue eddies, the number of distinct s(j) values strictly increases across successive thirds of the window. Falsified if it plateaus; then compute the sum-equitable partition, and kinds revive.
2. **Sum-refinement grows too.** Classes per round of the coarsest sum-equitable partition grow in both families. Falsified by a plateau.
3. **Hall test (risky).** For every round t past the transient in each of the ten starts, take the two-sided relation between round t and rounds t − 2 and t − 3 together, with a pair related when one is an ancestor of the other at exactly that depth. It has a perfect matching. Falsified by one Hall violation, which kills every ancestor-based spine at once.
4. **Canonical spine (riskiest).** One fixed set T of interval types, chosen on the first half of the window, makes the relation biregular with constant e on the second half, in all ten starts.
5. **Controls separate.** Let d(t) = c(t) − c(t − 2) − c(t − 3).
   - Ten starts: d = 0.
   - y⁴(1 + y)² starts: d ≠ 0, with d(t) = −d(t − 2) − d(t − 3), alternating in sign and growing about ×1.21 a round. The Hall test fails there by count. If d = 0 instead, that W was not minimal and the start belongs with the ten.
   - Catalogue eddies: run predictions 3 and 4 with each eddy's own W exponents. The cover model guarantees they pass, so a failure means a bug in the ancestor reading.

**Cheapest discriminator:** the distinct out-share count in prediction 1. It is one pass with no refinement and decides whether kinds are dead. For the spine, the cheapest is the Hall test in prediction 3: one matching per round, with no interval types chosen by anyone.