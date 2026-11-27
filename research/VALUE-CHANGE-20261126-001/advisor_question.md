You are consulted read-only from the repository root. Read docs/ADVISOR_HIVEMIND.md first (your entry of today on
candidate commutation rules is there, now marked checked). Attack the design before I freeze it; counterexamples and
checks, not a verdict.

Epic VALUE-CHANGE-20261126-001 (research/VALUE-CHANGE-20261126-001/). Part A (done): your three checks (check1.py,
check2.py, check3.py and their outputs). Part B/C (not run): the coordinator's pick, "value against change" (all values
have joint values; a value and the read of a change that flips it do not). Read css.py and rings.py.

Setting. Under even parity the allowed words S form a linear space and the allowed changes are S itself. A value read
of z is Z^z; a change read of x is X^x. The "coherent counting state" is the equal superposition over S (stabiliser:
values S-perp, changes S); its value reads give the counts. For readers A, B (the rest the middle), e = rank of the
pairing x|A . z|A over the state's certainties on A + B (the ebit count of Fattal and others, 2004).

My argument (attack it): if no knot holds a distinction of A and one of B, every allowed change supported on A + B
splits into an allowed change on A and one on B (at each knot the change's distinctions lie all in A or all in B), so
the cross certainties are value reads only and e = 0: the reduced state is separable, whatever the readers read. With
a middle reader reading every middle change (and its record used to sort), e can be >= 1 (an allowed change runs from
one ring's loose distinction through the connecting chain to another's; the chain's cut is a cross value law). With the
middle read for values, e = 0 again.

Predictions I intend to freeze (rings.py 2: four joined-ring families of BUILT-BINDING's repro.rings_start, rounds 0-2):
1. e = 0 for every separated pair with the middle unread, and with the middle read for values (entailed if the argument
   holds; kept as a check).
2. With the middle read for changes, e >= 1 for every pair of rings in every family at round 0.
3. e <= 1 at every stage read (one cross value law per connecting chain), so no two-reader game of certainty with value,
   change and product reads; a CHSH excess needs a read that is not a product of values and changes (supplied).
4. Control (two adjacent knots of one ring, not separated): e = 1 with the middle unread.

Questions:
1. Is the separability argument right (CSS form; the factorisation at each knot; the quotient by local certainties)?
   Counterexample?
2. Is e the right quantity for "a table above the classical bound with Pauli reads" (e >= 2 for a game of certainty;
   e = 1 gives CHSH at most 2 with Pauli reads but 2*sqrt(2) with a rotated read)? Cite once if known.
3. Prediction 3: can growth (rounds 1-2) add cross value laws between two rings' lineages (births joining a ring's
   lineage with the middle)? Then e could reach 2. Which is more likely, and what is the cheapest discriminating case?
4. The conceptual question: what in the recorded structure performs or carries a read of a change (a knot whose law
   relates a before and after? a shared distinction between a parent and child? the growing end? the motion study's
   moves, the class changes, FREEDOM-CLOCKS' change read)? I intend to say: allowed changes exist as objects, but every
   recorded read is a function of one allowed word, and a change read needs the state to relate two words (coherence),
   which is supplied. Is anything in the record a function of two allowed words?
5. Is the "middle reader whose record sorts" a fair reading of separated readers (the literature's event-ready
   arrangement), or does it count as communication supplied?
