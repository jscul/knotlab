# Ticket C (RING-IN-BALANCE-20261123-001C): readings, ambiguities and deviations

Written by the helper agent that built the engine from the frozen text. It was written before the registered runs of C1,
C2 and C3. Development runs were made earlier with the same code: seed 0 of each C1 configuration and of each C2
configuration, to check the code and estimate run times, and the whole C3 search, which takes under a second. Every item
below is a reading of the frozen text, not a change to it. The code follows these readings, and where a second reading is
possible the summary reports the result under both.

## The structure and the roster

1. **A knot does not meet itself.** A met set is "the set of members that one knot of the structure meets". I read
   "meet" as sharing a distinction with another knot, so the common knot is never in its own met set, even when it is a
   member. Under this reading D2(n, 3) and Ring(5, 3) give n pair groups in round 1 (2n births), which matches the
   disclosed hand trace ("generation 0 makes its ten births").
2. **Dead** (for the DEAD rule): a knot that holds no loose distinction, usable or barred ("A knot is live while it
   holds a loose distinction and dead otherwise"). Under RATION-3 with waiting nothing is barred, so this is the same as
   "not a member".
3. **Which distinction a birth takes.** The lowest-numbered usable loose distinction of the parent. The definitions say
   this makes no difference up to renaming.

## The part-round law (C0, C1)

4. **Demand in a part move.** "Steps 1 to 8 applied to the members of that part alone": the demand roster of a part
   move holds the part's new knots and its waiting members only. The other parts' members are not added. At every move
   the engine checks that no knot meets both the moving part's demand roster and a member of another part. If one did,
   adding them would change the demand, and the engine raises `PartInteraction`. The check also runs before step 1. If
   it never fires, the two readings agree on every move that was run.
5. **ALL-IN-TURN.** A sweep moves, once each, the parts that would make a birth at the start of the sweep, in order of
   their least knot number. Parts made during a sweep wait for the next sweep. Since the parts do not interact, the
   order inside a sweep does not change what is built (checked against the complete rounds).
6. **Own time in P2.** A waiting member's own time keeps growing after its birth, so "the knots of own time at most R"
   is ambiguous for a knot that waited. I read it as **own time at birth**. The P2 comparison colours each knot by its
   own time at birth (part-round run) and by its round of birth (complete rounds). A colour-preserving isomorphism
   therefore also checks "each knot's own time is its round there". Under the other reading (own time now), a knot that
   waited past R would be dropped and the check would fail on purpose. I take this to be unintended.
7. **Detecting returns under the part-round law.** Each part made by a move is compared, by hash and then by an exact
   isomorphism test of its members (coloured by h and k) and its inclusion-maximal met sets, with every ancestor part
   that is past its start. The first match found, in run order, fixes the part that returns, Y0: it is the matching
   ancestor with the least own time. After that, the k-th return is the first part made that descends from the
   (k−1)-th return and is the same as it. Afterwards the run checks, over every match it found, that Y0 has the least
   s and the first return the least t (`least_s_t` against `chain_s_t`), and that no descendant of a return with a
   smaller own time was the same (`returns_not_least_t`). A part that is never made in a run cannot be searched; for
   example, under LARGEST the parts that came apart never move. The other matches a run finds (the ring's other phase
   returning, for instance) are counted as `off_chain_detections`. They are not returns of the part that returns.
8. **"The moves and the births since the return before" for the first return** are counted from the creation of Y0:
   the start for D2(n, 3), and the end of the first move for Ring(5, 3), where Y0 is the part made by that move (the
   start of the ring is not past its start). P4 and P6 use returns 2 to 12 only, so they do not depend on this.
9. **P5's n (ambiguity that changes the verdict on Ring(5, 3)).** P5 says "exactly 4n at every return (n the number
   of members of the part that returns)". On D2(n, 3) the part that returns is the start's part, with n members. On
   Ring(5, 3), with the least s first, the part that returns is the part after the first round. It has 10 members (5
   joins and 5 offshoots, own time 1), and its period makes 20 = 4 × 5 births. So under the literal text P5 expects 40
   on the ring and fails there; with n read as the start's n it expects 20. I found this by hand before the runs, and
   the development run of seed 0 shows it. The verdict line gives P5 under the literal reading and, separately, with n
   the start's n. I did not choose between them.
10. **P4 and P6 means.** "A mean over seeds under the named priority's weighting": seeds weigh equally. For each seed,
    its births between returns are averaged over returns 2 to 6 and over returns 7 to 12; the two numbers are then
    averaged over seeds, and the ratio is taken. A seed that reaches fewer than 12 returns (P3's bound of 20,000 knots)
    counts with the returns it reached, and a seed with none in a window is left out of that window. The pooled mean
    over every (seed, return) is given too, along with the number of seeds that reached 12 returns.
11. **Bounds.** 12 returns, 4,000 moves or 20,000 knots, start knots included. They are checked before each move, so
    the last move can pass 20,000 knots.
12. **Seeds in C1.** Every priority but ALL-IN-TURN makes a random choice (UNIFORM and BY-MEMBERS by definition, the
    others to break ties uniformly), so each has seeds 0 to 19 and ALL-IN-TURN has one run: 3 × 2 × (6 × 20 + 1) = 726.
13. **Random choices.** Each choice is uniform (or, for BY-MEMBERS, proportional) over a list in a fixed order: parts by
    least knot number, moves in the order the engine registers them. The generator is Python's `random.Random`, seeded
    by the first 8 bytes of SHA-256 of (run identity, start, law or rule, priority or order, seed). So a rerun, even in
    another process with another string-hash seed, gives the same result (checked in `selfcheck_determinism.json`).

## The birth-by-birth law (C0 G(b), C2, C3)

14. **Jams.** The condition "no move of generation g or less is available and some member of generation g or less is
    short" is tested before every move and at the end. For each g, the first moment it holds is recorded with the
    number of joins and offshoots of generation g made by then. Under BY-GENERATION the run goes on after a jam with the
    moves of higher generation, up to 600 moves or 4,000 knots.
15. **P1's terms.** "A join of generation 1" is a join move whose generation (the greatest generation of its parents)
    is 1; it makes a knot of generation 2. "Jams at generation 1 after exactly 2n moves of generation 1, all of them
    offshoots" is read as: when the jam at generation 1 first holds, 2n offshoot moves and no join move of generation 1
    have been made. "No join of generation 1 ever made" is checked over the whole run. A jam at generation 0 is reported
    separately, as an observation; it is not among P1's fail conditions.
16. **C2's "a part that is the same as the start's roster, past its start and made of knots not in the start".** Every
    part the engine rebuilds after a move is checked. A candidate must have the start roster's number of members, none
    of them a start knot, no member meeting a member, and the same h and k and inclusion-maximal met sets as the start's
    roster. Met sets are read under the run's own rule for both the part and the start. Under DEAD, Ring(n, 3) has no
    dead knot at its start, so its start roster has no met set and no connected part of n members can equal it. For DEAD
    runs the summary also gives the comparison with the start's roster read under ANY.
17. **PRESENT-ORD.** This is used only in G(b), under ANY. While d is read, the new knot is counted as a member and
    treated as live, so it is not a dead common knot.
18. **G(b).** "The ordinary present-state law of ROUND-FREE" is run as PRESENT-ORD, FIRST-COME, ANY and UNIFORM on the
    starts [[0,1,2],[0,3,4]] (two three-place knots sharing one distinction) and [[0,1,2,3]] (a lone four-place knot),
    with seeds 0 to 39 and up to 300 moves. "Stop" means the roster has no member. No knot bound is applied.
19. **C3.** The search covers all orders of the moves of least generation while that generation is 0 or 1, that is,
    BY-GENERATION with every tie rule and every choice among the moves. A state ends the search when no move of
    generation 1 or less is left. States are memoised by the colour-refinement hash, then an exact isomorphism test, of
    the incidence graph of knots and distinctions, with knots coloured by generation and distinctions by barred or not.
    A non-start knot shares distinctions only with its parents (lower generation) and its children (higher), so this
    graph fixes parents, open groups, h and every move, and the future of a state depends on it alone. The number of
    orders reaching each end is counted through the memo. An extra search under ANY, which is not registered, is
    reported separately.

## Sameness tests

20. "A colour-refinement hash ... confirmed by an exact isomorphism test": different hashes are taken as "not the
    same", since refinement is an isomorphism invariant and equal graphs get equal hashes. When the hashes are equal, a
    colour-preserving bijection is searched for, and it counts only after every edge has been verified. The search is
    graded first (knots level by level through the knots of lower level they meet), then a general backtracking search
    on the graph with twin vertices collapsed, and finally networkx's VF2. `iso_stats` in the results counts which
    method decided.

## Noticed after the registered runs

22. **The contract and the pre-registration disagree in their prose.** `contract.json` in this directory was frozen
    with the pre-registration, and its two SHA-256 hashes match the pre-registration and definitions I worked from.
    But its `resource_budget` speaks of "the grid of 19,200 runs through the shared runner", and its
    `primary_observable` of "whether each run builds the same to depths 1, 2 and 3 as the complete rounds". The
    pre-registration's run table has 726 runs (C1), 4,800 runs (C2) and one search (C3), and P2 compares the knots of
    own time at most R. I followed the pre-registration's table, which the task names as the frozen design. I left the
    contract unchanged. I saw this only after C1 to C3 had run, so it is recorded here afterwards, not before.

## Not run

23. The K1–K3 knot test is not run by ticket C, since none of C0 to C3 asks for it. Not-all-equal, the record's
    eight-knot clock and the fillers under the birth-by-birth law are left out, as the pre-registration says.
