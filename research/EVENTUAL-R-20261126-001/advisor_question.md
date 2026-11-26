You are consulted read-only from the repository root. Read docs/ADVISOR_HIVEMIND.md first (your entry of today on rule R
is there). Attack the design; I want counterexamples and checks, not a verdict.

Epic EVENTUAL-R-20261126-001 (research/EVENTUAL-R-20261126-001/). The coordinator's framing: the owner's confirmed
layer reading is that nothing changes over time; rounds are a reading outward of one fixed unlimited structure ("time
doesn't have ticks"). So test R in that form: two distinctions have a joint value exactly when some knot of the whole
structure ever holds both. Is it determined at a closed component, consistent with every finite reading made before the
closing knot is read, and does a reader reading outward ever get a record contradicted by a later layer? Then the bound:
under R with one state, do reached patterns stay at or below the quantum limit, and is 4 excluded?

Code (read it): ops.py (values as signed Paulis, A_i = X_i Z^{j<i anti}; laws on a read set = products of knots whose
leftover lies inside it, signed by the operator product; signs: every knot even but the last of each closed component,
which takes the forced sign); part_a.py (ALREADY RUN, part_a_out.txt: on the 21 census types with R1, 3,789 read sets;
the operator-signed product rule equals an independent enumeration of the group on all; the closed part rule differs
only on 15 read sets, all at the type with a cut knot; GF(2)-signed products differ on 104, at every odd-closing type
and at the cut-knot type); part_b.py (NOT yet run beyond a 20-start timing pilot whose output I did not read, and the
named starts, whose output I did read: ring of three and four mutually meeting knots: forced odd, B3 all same, B4 "stage
knots do not commute"; three- and four-label subset closures: R1 fails); part_c.py (not run).

Questions:
1. Is "the whole's R" well defined for an open structure that grows without end? Co-held is a property that becomes true
   at a finite stage and may never be refuted; knot-pair commutation under R can flip parity as more pairs become
   co-held. So R1 for an open component is provisional. Is my truncation at the last grown round (exact for closed
   components) the right scaffold, and what would a second choice be (e.g. more rounds, and counting how often R1 at
   round T is overturned at round T+1)?
2. B2 checks that no later knot holds a closed component's distinctions. Is it an engine property (births take loose
   distinctions only), so that R on a closed component is fixed at closing? Where in the engine?
3. B3 formalises "a record contradicted by a later layer" as a law's sign differing between the knots read so far and
   the whole, under the whole's R and signs. Is that the right formalisation? I expect zero sign differences wherever the
   whole has a state, by construction. Is there a reading I am missing in which a later layer does contradict an earlier
   record (e.g. R1 holding at T and failing at T+1, or a component whose knots commute only after a later layer)?
4. B4: a reader using only R read off what it has read. On the fixture its knots do not commute before closing. Is that a
   contradiction of a record or only the absence of a state?
5. Part C: my argument that the counting state (the one the signed knots fix, uniform on each read set's allowed words)
   never exceeds CHSH 2 with single-distinction observables (if three of the four pair products are laws the fourth is
   too, and a PR-signed set would put −1 in the group). Check it; is it true for products of places as observables too?
   With any state in the code space Tsirelson's 2*sqrt(2) holds (commuting observables). Anything that would let 4
   through?
6. Predictions I intend to freeze (sampled census starts, seed 20261128, 300 starts, four rounds): B1 closed components
   whose knots commute are under one third of closed components; B2 zero; B3 zero sign differences and zero
   contradictions, and "more laws later" at least once; B4 stage knots often fail to commute, and where they commute
   some read set differs; C largest CHSH exactly 2. Which are entailed (move them out), which wrong, which cheaper test
   discriminates better?
7. Exact link (intuition): is "commute iff some knot of the whole holds both" a known construction (the advisor named
   symplectic polar spaces; anything on commutation fixed by a completed structure, e.g. the Kochen–Specker contexts of
   a hypergraph)?
