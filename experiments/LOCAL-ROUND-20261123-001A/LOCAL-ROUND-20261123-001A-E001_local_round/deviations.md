# Readings and deviations, LOCAL-ROUND-20261123-001A-E001

Written by the engine's author (a helper agent that has not seen the drafter's prototype or its outputs) before the
registered runs of items 2 to 5. Before this file was written, the gate (item 1) had passed, and development runs had been
made on D2(4,3) under (RATION-3, CANCEL-WAIT) through round 1, the pre-registration's suggested first discriminator,
to check the code. Those runs are rerun by the registered scripts. The SHA-256 sums of the three frozen texts and of the
reference engine were checked against `contract.json` before any code was written, and they matched. `lr_reference.py` checks the engine's sum again on every
import. No definition, prediction or earlier study's file was changed. Each item is a place where the text left a
choice. It gives the reading taken and why, and the reading closest to the letter was preferred. "LR" is
`research/LOCAL-ROUND-20261123-001/definitions.md`, "the definitions" the shared definitions.

## How a run is represented (not a reading; stated so the referee can check it)

1. **A run's knots are named by their images under m.** While every birth and barring has matched, the run's structure
   is, up to renaming of distinctions, the sub-structure of the reference made of the image set I (start knots
   included), with the images in Bar barred (LR section 4, "Memo key"). Each image fixes its parents, its fresh count and
   whether it is barred, and which loose distinction of a parent a child took is exchangeable. So a state is the memo key
   (I, Bar), stored as one integer, and a mismatching birth ends its order. Every law reads only this structure:
   - the written parent relation;
   - children (the reference children that lie in I);
   - h0;
   - usable and barred counts (usable = h0 less children in I, or 0 if barred);
   - which start knots meet;
   - holder steps, which cross parent-child meetings and start-knot meetings.

   No law reads a round of birth. Only the comparison reads it, for the cutoff and the outcome tests.
2. **A brood's plan is memoised by the brood's knot set.** Every child in I of a brood parent lies in the brood (LR
   1.4), so the brood's roster at birth is a function of its knot set alone.

## Readings

3. **A knot does not meet itself.** A met set never contains its common knot, even when the common knot is a member. This is
   the reading of tickets A (D2) and C (item 1) of the earlier study; the gate confirms it against the reference.
4. **All-short (LR 2.1, step 5).** The test is applied to every roster of the sequence, the first one included ("a part of
   any roster"), and only under CANCEL-WAIT, since it is part of step 5, which is CANCEL-WAIT only. Under CANCEL-RETIRE
   a part all of whose members are short retires. Under CANCEL-OFFSHOOT its members make their offshoots.
5. **ORD's D in a plan (LR 2.1, step 4)** is computed among the births of the roster in which they are planned. Under
   STALL, the only treatment used with ORD, there is one such roster.
6. **The cutoff for barrings.** LR section 4 limits births to those within round r and says nothing of barrings. A
   barring of x is made only when m(x) was born by round r. *Why:* the outcome tests ("every image of m born by round r
   that retires in the reference is barred") look only at knots born by round r. A barring of a later knot could not be
   tested against a reference run only to round R, just as "a mismatch at a birth whose parent was born after round r is
   not tested". Under CANCEL-WAIT and STALL there are no barrings, so only the FLOOR1 rows depend on this.
7. **Barrings are made all at once.** After every birth, and at the start, every barring allowed in the present state is
   made together. The state is read again, and this repeats until none is allowed. Each barring is tested for a match.
   A mismatch at a barring ends the order with the births made so far. *Why:* "made as soon as it is allowed, before the
   next birth" (LR 2.4.4). Barring two knots read short at the same moment one at a time, with a re-read in between,
   would add an order that the text does not name. This matters for R0 and R3L only. Under the brood laws and the control,
   barring a retiring knot (which has no children) changes no other reading.
8. **An allowed birth is a parent set with its fresh count.** A member with several remaining offshoots offers one
   allowed birth (u,) at a time. The sampled and x-last orders choose uniformly among the distinct allowed parent sets.
   The every-order search counts orders as sequences of parent sets. *Why:* the definitions name a birth by its parent
   set (LR 2.4.1), and offshoots of one member are exchangeable up to renaming. No law here allows one parent set with
   two fresh counts. The search checks this and raises an error if it happens.
9. **Remaining births under R1, R2, R3.** These are the remaining births (LR 2.3) of the plan read by the birth's knots,
   which all read one roster: the start roster, or one brood. Each knot of B must also hold a usable loose distinction
   (LR 2.4.1). A brood that is not all-weaned is read with the children its parents have so far (LR, R1 item 1).
10. **The guards on start knots.** A start knot is weaned and has no parents, so it has no brood-mates. A start-roster
    birth or barring therefore passes the guard of R1, R2 and R3.
11. **Stall.** Under STALL, if the start roster's plan stalls, nothing is allowed (LR 2.4.5). A brood's roster at birth
    whose plan stalls allows nothing from that brood (LR 2.4.5, second bullet). This never happened: see P12.
12. **R3L.**
    - The present roster is read with every knot as a common knot (ANY).
    - An untouched part's plan uses the waiters' recursion, since LR 2.1 includes it.
    - In a touched part, "its remaining births" are those of the plans its members read (LR 2.2) whose parent set holds a
      member of the part. Such a parent set lies wholly in the part, because its knots share a common knot.
    - R3L under (ORD, STALL) is run and reported without a prediction.
13. **T(d).**
    - W is the set of knots within holder-step distance d of B in the present structure.
    - **The candidates.** I read "every remaining join of the reading around one of its members" with "its" as the join's:
      a join G is a candidate when G is a remaining join of the reading around some member u of G. Each member alone is
      also a candidate. Each candidate is then tested in the reading around its own parent set, as the text says.
    - **The guard.** No parent in W of a knot of the brood within d is a member.
    - Holdings are h0, read exactly at the boundary.
14. **The control.**
    - Depth is found breadth-first from the start knots in the present structure.
    - **Holdings at k ≥ 1.** A layer knot's holding is its places less its number of neighbours of depth k − 1, since a
      non-start knot shares exactly one distinction with each neighbour.
    - **Made births.** The layer's children are the knots of depth k + 1, each with its depth-k neighbours as its parents,
      and they are subtracted by parent set.
    - **Barrings.** A layer member whose status is "retires" is barred with no further guard.
    - The layer at k = 0 is the start roster, with holdings h0.
15. **R0.**
    - **CANCEL-RETIRE.** All members read short at one moment retire together (item 7).
    - **CANCEL-OFFSHOOT.** A short member has an offshoot move, one parent set as in item 8, while it holds a usable
      distinction, and it has no join move.
    - **ORD.** R0 is PRESENT-ORD with FIRST-COME. Its d is read on the present roster after the take: each parent's
      holding drops by one (a parent that gave its last usable distinction is no longer a member), and the new knot
      counts as a member before it receives anything. Every knot is a common knot, the new knot included, and the new
      knot meets its parents.
16. **The closing bit (LR 2.4.3).** It fires when, after the take, no loose distinction (usable or barred) is left in the
    structure. The birth then receives none and is matched against a reference knot with fresh count 0. Every firing is
    counted, together with whether the matched reference knot received none. A birth that does not fire but has a
    reference closing knot as its only candidate shows up as a mismatch; the listing names that candidate's fresh count.
17. **Sampled and x-last orders.**
    - Seeds use Python's `random.Random(seed)`, and each choice is `randrange` over the allowed parent sets sorted by
      their tuples of images.
    - An x-last order runs for every reference knot that exists by round 1 (born in round 0 or 1), dead start knots
      included, each with `Random(0)`. This gives the counts named in the pre-registration (20 on D2(5,3), 15 on
      Ring(5,3), 32 on the cycle of eight with three extra dead knots).
18. **Every order.**
    - The breadth-first search over memo keys is not stopped at its first mismatch, which ends its own branch. It goes on
      until no order is left, until the key cap, or until a time budget, so that counts of matching, mismatching and
      underbuilding orders are complete where it finishes.
    - The least number of births to a mismatch is exact when it is found at level n + 1 after levels 0 to n were expanded
      in full. It is exact even if the budget ends the search during level n + 1.
    - "Keys" counts distinct memo keys over all levels, the start included.
    - "Every order searched to N births" means that every state reachable with N births has been generated.
19. **Time budgets.** These come on top of the registered key caps: 420 s for each search of the first table, and 300 s
    for T(d) and for item 4 and its extra. A search that reaches either one is reported unfinished, with its depth. The
    pre-registration allows this ("reported as finished or not"), and the task fixes about three hours for the study.
20. **The last round R.** R is the least round t ≥ r that meets LR's condition. Rounds after a stop make nothing. Under
    (FLOOR1, CANCEL-RETIRE) the seven-knot generator's growth stops at round 2, so R = 3 for the cutoff of round 3.
21. **The gate's rounds.** For each start and law the gate checks rounds 1 to max(5, R), with R the largest last round
    of the cutoffs registered for that pair. It checks fewer where the growth stops: 4 rounds for the lone four-place
    knot, and 2 for the seven-knot generator under CANCEL-RETIRE.
22. **Ring(5,3) under (RATION-3, CANCEL-WAIT)** is run at both of its cutoffs, rounds 1 and 2, with all three kinds of
    order, since item 3 asks for every kind "for every start, law and cutoff". The same holds for the cutoffs 2, 3 and 4
    of the FLOOR1 rows.
23. **P4 at n = 6.** R3L on D2(6,3) through round 1 is not a row of the first table, but P4 predicts its least order
    (16). It is run as an extra, with the orders of item 3 and the cap of item 4, so that P4 has a verdict for n = 6.
24. **Groups of three or more.** The flag covers every roster whose plan a law reads:
    - the start roster;
    - each brood's roster at birth, complete or partial;
    - each waiters' roster;
    - R3L's untouched parts;
    - R0's present roster;
    - the control's layer roster;
    - T(d)'s rosters within W.

    ORD's demand rosters (LR 2.1, step 4) are not counted.
25. **P12** is checked on every brood's roster at birth that is read, complete or partial, at its first level (the roster
    itself, not a waiters' roster). A member there is short when it owes more groups than its holding h0.
26. **Numbering in listings.** Run knots are numbered as in the start's star list, and births from the first free number
    in the order they are made, as the pre-registration numbers them. Each row also gives the reference knot (image) it
    matches.
27. **"A waiter's surplus offshoot" (P3).** I read this as follows: the first mismatch is an offshoot (u,); u's image waits
    in at least one reference round; and the reference's offshoots of m(u) with that fresh count are already all images.

## Noticed after the registered runs (written after them; no code or reading was changed because of them)

28. **Extended searches.** On 67 rows the every-order search ended unfinished: at a registered key cap, or at the time
    budget of item 19, which is this engine's own and not the pre-registration's. Eight of these were rerun in the
    background with a 1,500 s budget, toward the registered cap of ten million keys: R3 on the cycle of eight with three
    extra dead knots (P14); R1, R2, R3 and the control on Ring(5,3) under (ORD, STALL) through round 2 (P7, P9); the
    control and R1 on the two-knot start under (FLOOR1, CANCEL-OFFSHOOT) through round 4; and R1 on the three-knot start
    there. Their outputs are `runs/<run>__long.json` and the registered outputs are left as they were. The summary uses
    an extended search where one exists and prints the registered line beside it. The command lines are in
    `logs/long_runs_commands.txt`.
29. **Key counts.** The prototype's key counts need not agree with this engine's (pre-registration). In fact they agree
    exactly on every finished search under CANCEL-WAIT, STALL and CANCEL-OFFSHOOT that was compared, and for the
    control under every treatment, with one exception: the control on the cycle of eight gives 8,207 keys, disclosed
    8,206. By hand that start gives 2^13 = 8,192 states of the start's 13 births, plus 15 states of the offshoots of
    members 3's and 7's offshoots, start key included. They differ for the brood laws under (FLOOR1, CANCEL-RETIRE):
    on the two-knot start R1 400 against 517 and R2 324 against 357 (round 2), and R1 12,321 against 17,403 and R2
    11,881 against 16,435 (round 3); on the three-knot start R1 109 against 128 and R2 107 against 124 (round 2), and R1
    409 against 528 and R2 331 against 364 (round 3). The verdict is the same in every case. A scratch test outside the
    registered runs found the following:
    - Making each barring a separate step that can be interleaved with births gives larger counts (841 on the two-knot
      start).
    - Storing the key just after a birth as well as the key after its barrings gives 520 and 360, near but not equal to
      the disclosed counts.

    So the difference lies in when the prototype made barrings under the brood laws; this was not confirmed. The control's barrings,
    which agree, are guarded by the layer alone.
30. **Disclosed least orders that were found, not exact.** Under T(2) and T(3) on D2(n, 3) and on the cycle of eight,
    the prototype's least numbers were found in sampled orders. This engine's breadth-first search gives smaller exact
    least numbers:
    - 7 for T(2) on every start;
    - 11 for T(3) on D2(8,3);
    - 20 found for T(3) on D2(12,3), where the every-order search reaches only 8 births.

    Similarly, R1 on D2(4,3) through round 3 has least 7 (exact), where the prototype found 9 in 40 sampled orders. None
    of these changes a verdict, since P11 asks for the least d with no mismatch. Listings are in `listings/difference_*.json`.
31. **x-last counts.** Each x-last order is a single order drawn with seed 0, so counts depend on the generator and on
    the enumeration of allowed births (items 8 and 17). R1 differs in 20 of 20 x-last orders on D2(5,3) (disclosed 19
    of 20) and in 15 of 15 on Ring(5,3) (disclosed 7 of 15). Every such mismatch is a waiter's surplus offshoot (item 27).
    Listings are in `listings/xlast_*.json`.
32. **The advisor's account of R2 on the cycle of eight** (pre-registration, "R2 on the cycle of eight with three extra
    dead knots") was traced with this engine (`listings/C8X3_R2_the_advisors_order_...json`, field `trace`). It holds
    with one difference of detail. With member 3's offshoot not yet made, the joins of members 2 and 3 and of members 3
    and 4 already read as not short in the brood's roster at birth itself, not in their second reading. The join of
    members 0 and 1 then acts in the third roster together with the joins (1,5) and (5,6). The join of the joins (0,1)
    and (1,5) is planned there, and the reference has no such knot.
33. **The key cap is checked when a breadth-first level is complete.** A search can therefore pass its cap by up to one
    level. Examples: 1,761,884 keys against the cap of one million (R1 on D2(4,3) through round 3), and 14,599,220
    against ten million (R3 on the cycle of eight, extended). The depth reported is always that of a complete level.
