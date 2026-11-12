**Main flaw: in loose families most of this is settled by a finite computation.** If every SELF relation at G is free, imposing G at the bottom imposes nothing. A call's possible end-states then depend only on its parent's, through the definition body. That gives a map on subsets of the 8 states, per definition and call site, which you can iterate exactly along call paths.

- **Forced/possible:** these shares are eventually periodic in the call path by construction, so they cannot show regularity. The iteration also replaces the SAT sampling and the T+2 cap.
- **Sampling:** "no forced call" is a claim about all calls, so a 64-call sample cannot establish it in branching families.
- **P3:** this is mostly settled, as you suspect. Chains satisfy it by the lemma, so exclude them. Elsewhere, "forced at T implies forced deeper" is a one-step property of the body (ports all-equal ⇒ inner call all-equal) that holds at all depths or none, so T+1 and T+2 are not independent evidence.
- **P1:** the census (94% of relations free) nearly settles it, and the unit differs (relations there, families here). "Loose" tests only that the bottom imposes nothing. The stronger reading, that the interior is unconstrained, is already refuted by the lemma.
- **P2:** when the lemma demands only some call, no forced call is the default expectation. The "half" threshold is arbitrary and neither outcome separates regular from free.
- **Gate:** this is the lemma restated, so label it a code check. Also pin the index, since the lemma says level t-1 and the design lists depth t.
- **Range:** confirm T..T+2 lies inside the census's verified dead range, and that G is the joint fixed point over all definitions.

**What would answer the question:** the joint structure, since the marginals are regular automatically. Project onto the per-call all-equal indicators and enumerate the minimal all-equal sets per depth. Three cheap measures:

1. **Single ray:** can the all-equal calls lie on one path, each witness at t+1 a child of the witness at t, or must they move between branches?
2. **Independence:** is the set of achievable (depth-t set, depth-t+1 set) pairs a full product or a strict subset?
3. **Count:** does the number of minimal sets per depth stay bounded (rigid) or grow with branching (free)?

Report non-loose families separately, since there the bottom also constrains.
