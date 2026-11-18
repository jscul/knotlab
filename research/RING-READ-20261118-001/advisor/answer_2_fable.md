I have not run anything; this is reasoning from your frozen facts only.

**(1) g = 3 is not enough; let g grow with s.**
- Two junctions share at most one distinction, so each shared distinction cancels in the sum.
- A chain of k junctions of size 3 has support k + 2, so six of them fit under support 8.
- A closed ring of k such junctions has support k. No triangle only forces k ≥ 4, so up to eight fit.
- The two end distinctions of a chain of four lie in no sum of three, so g = 3 leaves that pair standing at stage 8.
- Your own diagnosis says "three or more", and g = 3 covers only "three".

Use g = s, or better a closure: keep adding a touching known junction while the running support stays ≤ s + 2. The slack is needed because a ring's partial sums overshoot by one or two before closing.

**(2) Yes, keeping junctions can poison later stages, in three ways.**
- **Protection:** the "one known junction contains both" exception shields a wrong junction's pairs for good.
- **Wrong sums:** a wrong junction enters the sums and can prune true pairs.
- **Span:** a true junction lying in the span of known ones that include a wrong one is refused.

Nothing in R3 retracts a junction before the final repair. Two cheap guards:
- Stamp each junction with its stage, and let R2's repair drop junctions as well as add them.
- Refuse any new clique sharing two distinctions with a known junction. That uses a frozen fact as a filter, so declare it.

Two further holes:
- **Swallowing:** one surviving spurious pair beside a true junction makes the maximal clique larger than the junction, so the true one is missed. Test sub-cliques too.
- **Order:** new cliques at a stage are tested against known ones only, not against each other, so the result can depend on order.

**(3) I would bet against "R3 alone exact at every round 10–20".**
- **Rounds 10–14:** the three spurious cliques are not parity consequences, so the span test passes them. They are removed only if their pairs happen to lie in small sum supports, which nothing guarantees.
- **Rounds 15–20:** g = 3 leaves long-chain pairs standing, so some of the 104–148 spurious cliques should survive, or swallow true junctions.

The second most likely to fail is "one survivor after repair" at rounds 15–20, if the residue is more than the repair can handle or a kept wrong junction blocks the legal repair. The regrown-round and horizon predictions I expect to hold wherever the repair succeeds.