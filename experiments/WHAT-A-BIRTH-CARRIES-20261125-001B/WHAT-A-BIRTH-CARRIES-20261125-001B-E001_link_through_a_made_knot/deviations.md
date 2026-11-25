# Deviations and readings, WHAT-A-BIRTH-CARRIES-20261125-001B-E001

Written by the engine's author, who has not seen the drafter's prototype, its outputs, or the `advisor/` and
`advisor_b/` folders of the epic. The frozen files are unchanged; their SHA-256 sums were checked against
`contract.json` before any code was written, and `common.check_frozen()` checks them at the start of every script.
Citations: SD line n, FD s.i, D s.i, DB s.i, RD s.i (ticket A), BD2 s.i (this ticket), PR (the pre-registration),
W n (ticket A's deviations). Each item gives the question, the reading taken and why, and the runs it affects. Items 1
to 30 were written before run G.

## The engine, the gate

1. **The round is written again** (`eng.py`), following ticket A's `wbc.py` step by step (which passed the same
   gate), because BD2 2 adds rules the fold engine does not have and RD 3.3 needs values it does not record. It is
   checked in run G against the fold engine `pm.py` (imported unchanged, read-only) on ticket A's 648 runs: the 12
   starts of RD 5.3 (`pm.STARS` and made-2 to made-6 as registered in ticket A's `numberings.json`), FLOOR1, CAP-3,
   ORD, the three recorded treatments, both knot laws, no taking rule, MET(OLDEST) and MET(NEWEST); 6 rounds, 800
   knots; compared as ticket A did (W 2): every knot's places in order, parents, round made, kind, bars, each birth's
   kind, parents, inputs, takes, D, p, f, implied flag and fresh names, groups, short members, closing, stop and the
   guard's round and limit. The guard's numbers are `pm.GUARD`; its checks are made in the fold engine's order (W 3).
2. **The gate listing (`gate_listing_b.txt`)** is compared line by line except its header lines, which name the law in
   the prototype's words (MET-ONE, STEPS1-ONE, BY-SHORTFALL; the file's first line translates them). The runs are
   grown under the registered bounds (7 rounds, 1,500 knots) and listed through the round the header gives. The knot
   test line is `knots.test_run` on the structures after rounds 0 to the last listed round; its count of verdicts is
   every knot at every round (39 = 3 + 6 + 11 + 19 in the first case), which is how the listing counts.
3. **Ticket A's four attribution records** are classed by ticket A's `wbc.record_attribution`, which uses
   `wbc.first_difference`, the function this engine's attribution calls (item 16): the gate checks the code used.
4. **Imports.** `eng.py` appends the fold folder and ticket A's folder to `sys.path` (both have a `common.py`; this
   folder's is imported first). Imported unchanged: `pm` (gate, guard numbers), `knots` (FD 7), `wbc` (the course's
   invariant and VF2 test, `align`, `first_difference`, `differing_part`, `classify_part`, `record_attribution`).

## The rules (BD2 2)

5. **The owing rations are "on FLOOR1"** (BD2 2.2): a join receives max(3 − p, 1). BD2 2.3, 2.5 and 2.6 give only an
   offshoot's count for PARENT-OWING-CAP3/4, the four ration controls and the comparison 2 + (o mod 2); a join
   receives as FLOOR1 under each of them too, the reading closest to BD2 2.2's "every other birth receives as FLOOR1".
6. **o** is the parent's owing of the round: the number of the round's groups containing the parent, counted before
   any is cancelled (BD2 2.2), for every offshoot (RELEASE's, CANCEL-OFFSHOOT's, SHORT-BY's). IMPLIED goes first.
7. **Sole candidate** (BD2 2.1): the clause's candidates are a set of distinct eligible distinctions read on the
   structure at the start of the round; exactly one is taken, otherwise none. MET-SOLE's join clause is MET's (FD 3.3,
   as `pm.take_candidates`); STEPS1-SOLE and STEPS2-SOLE use the knots exactly one and two parent steps above the
   parent (`pm`'s `level`), offshoots only.
8. **SHORT-BY** (BD2 2.4): a short member u makes n = min(h(u), o(u) − h(u)) offshoots; FD 2.1's hand-out gives them
   its first n usable loose distinctions in increasing name and it keeps the rest; its act is recorded as
   "short-by n keep h − n" (a value of RD 3.3 step 3). A keeper is in the demand roster with what it keeps (as a
   waiting member is) and is read afresh in the next round.
9. **J-EACH-PART** (BD2 2.7): every offshoot also takes every eligible distinction held by a member of a part of the
   round's roster (components of joinable at the start of the round) other than its parent's part. The text excludes
   nothing else, so a distinction its parent also holds is taken too when such a member holds it. Joins do not take.
   4 rounds, s = 1, 2, 3.
10. **Suppliers** (RD 3.3 item 5, W 6): every knot that supplies a candidate: for MET's clauses as ticket A; for
    STEPS-k the knots k parent steps above the parent that hold it; for J-EACH-PART the members of other parts that
    hold it.

## Pairs, bars, descent

11. **Pairs** (BD2 4.2): for s = 1 to 4 (J-EACH-PART 1 to 3), the parts of the roster after round s (components of
    joinable among the knots with a usable loose distinction), every ordered pair (X, Y), X ≠ Y, in different classes
    of FD 1.6. Registered order of pairs (BD2 1.3): by s, then the smallest knot of X (knots are named in birth
    order), then the smallest of Y. If run A stopped before round s, there are no pairs at s; if it stopped at round s,
    the pairs exist and have no round after s to read.
12. **Which pairs get the bars** (BD2 4.4). Every reading made on the bars (B1-dependence, how many, which at equal
    number, m, lasting, check (b)) is conditioned on a meeting, and B1-dependence on B1-link. The bars are therefore
    run for every Y of a pair that has a meeting in run A (all registered subsets: every subset for |Y| ≤ 4;
    otherwise Y, ∅ and the |Y| subsets of size |Y| − 1). Pairs with no meeting in run A are reported "no meeting" and
    get no barred run. The course with Y barred (A = ∅) is compared for every pair with a meeting (strict or not);
    the subsets' readings (how many, which, m), lasting, the checks and the knot test of barred runs are made for the
    pairs with a meeting only through made knots. A barred run is run A through round s, then the usable loose
    distinctions of Y's members not in A barred, then the same law, the same bounds.
13. **Descent** (BD2 4.3, D 2.6): X's and Y's members are descended from X and Y; a knot made after round s from the
    parts of its parents; everything else made by round s is from neither. Y's barred members stay Y's (W 7), so a
    take from them is a meeting. The meeting, the linking set and every descent are read separately in each run
    (BD2 5).

## What is read

14. **The course from X only** (RD 3.1) is ticket A's reduced form (W 10) with this ticket's s; X's members are labelled
    with round s, as RD 3.1 says ("its round (s for X's members)"), other knots with their round. Comparison is exact:
    first an explicit map by answers (the two runs' knots and distinctions matched by their answer keys; when labels
    and links agree under it, the courses are isomorphic); otherwise the invariant (different: not the same);
    otherwise VF2 (`wbc.same_course`). The first round at which they differ, t_d, is the least R such that the courses
    through R differ.
15. **The values used at X's births** (RD 3.3) are ticket A's entries (wbc `_analyse`), read with this pair's descent.
    Step 3 holds the treatment's act (SHORT-BY's count, item 8); step 7 holds (p, implied, f) and, under an owing
    ration, also o, the value the ration uses (Lemma A, corrected).
16. **Attribution** (RD 4.3, BD2 6.3) is ticket A's `wbc.first_difference` at the first round s + 1 … (last round both
    read) at which the values differ. Within a step, entries are in the order of "the run with the smaller a" (RD
    3.3): the run with A = ∅. The class in the other order is recorded beside it. Accepted when the differing part
    holds a knot from Y only (`wbc.classify_part`'s "through the meeting").
17. **The m reading** (BD2 6.6): P partitions the pair's subsets by their course through the last round all of the
    subsets' runs read. A position is (round, step, answers); a run without it gives "absent". An input entry is a
    position whose values differ between two subsets with a differing part (`wbc.differing_part`) classed through the
    meeting. "Joint value refines P": subsets with equal joint values have equal courses. m = 1 when one input entry
    refines P (whether it induces P exactly is reported); m = 2 is searched over pairs of input entries at distinct
    births (a birth: the knot key of the position; for a group its members from X only) when there are at most 400
    input entries; beyond that, or with no pair, m is reported as "≥ 2" or "≥ 3".
18. **The symmetry check** (BD2 6.8, item 3): "the structure" is SD's: knots holding distinctions, with the bars; the
    birth record is not part of it. Sought: a renaming of knots and distinctions onto itself exchanging X's members
    with Y's and fixing each linking knot that exists after round s (linking knots made after round s are listed
    apart). Exact search by individualisation and colour refinement on the disjoint union of the structure labelled
    both ways; a search node is one refinement call (the root or one individualisation); "undecided" past 2,000,000;
    a found map is checked link by link. Cached per (s, {X, Y}, linking knots), since (X, Y) and (Y, X) ask the same.
19. **The knot test** (BD2 1.3). Run A: `knots.test_run` on every structure after rounds 0 to the last read (parity:
    ranks and kernel on every knot; not-all-equal: the birth method on every knot, start knots directly, and the direct
    test of every knot of at most 12 places at every round, compared). Barred runs: only for pairs with a meeting
    only through made knots whose courses differ, the first 8 of an item in the registered order (item 11); for each,
    the run with A = ∅ and the two lasting reruns. Parity: in full at the last round read. Not-all-equal: every knot
    born after round s (reruns: after t_d) by FD 7's birth method alone, after checking that every such birth
    received a fresh distinction. Runs P1 and U1 ("tested in full"): every knot at every round read, as run A, for the
    same at most 8 pairs. Other subsets' runs are not knot-tested. A differing pair past the eighth is "undecided:
    knot test not run".
20. **Reader test item 4** (BD2 3): computed on the A = ∅ runs of pairs with a meeting only through made knots, over X's
    births (a parent from X only) after round s: the number at which the take took something, at which an owing
    ration gave another count than FLOOR1's max(3 − p, 1), and the short members from X only on which SHORT-BY acted
    otherwise than CANCEL-OFFSHOOT (kept something). Counts are summed per item and reported.
21. **Lasting** (BD2 6.7): each of the two runs (A = Y, A = ∅) is continued from its structure after round t_d with
    every usable loose distinction of every member not from X only barred, to round t_d + 2, the same knot bound.
    "The rosters descended from X only": the members from X only with h, k and the inclusion-maximal met sets among
    them (any knot a common knot). "The same" (SD 29–30) is decided exactly: different invariants (h, k multiset, sizes
    of maximal met sets, a WL hash of the member–met-set incidence) mean not the same; otherwise VF2. "Undecided" if a
    rerun stops before round t_d + 2.
22. **FD 5.7's weaker class** (BD2 5.5): some met set of round t's roster or demand roster holding a knot of each
    descent has a common knot made after round 0.
23. **The linking set** (BD2 5.2): RD 3.5's set (knots made by round t − 1 whose met set in round t's roster or demand
    roster holds a knot descended from X and one descended from Y; a knot from both counts as each) and, for each
    birth of round t that takes, the holders at the start of the round of what it took that are of the other descent
    (other than a descent of one of its parents). Each knot's FD 5.7 class as W 12; ancestors read from the parents in
    the structure after round t. A linking distinction (BD2 5.4) is a place of a linking knot with a holder of X's or
    Y's descent after round t, reported with its holders (knot, round, descent, kind) and the least round among its
    holders (the round its first holder was made).
24. **The ancestral reading** (BD2 5.6): a linking knot w made after round 0 and a met set of w (round t, either
    roster) holding u of X's descent and v of Y's descent with w a recorded ancestor of both and not the parent of
    both. Every-member form: w a recorded ancestor of every member of X and of Y.
25. **"Meets against does not meet"**: the run with A = ∅ has no meeting for the pair by its last round read.
26. **The Y-side knots of the first differing demand** (BD2 6.9): at the first step-6 entry (in the order of item 16)
    whose values differ, the partners from Y only or from both with no answer in the other run, from each run, with
    kind, parents and round.

## Verdicts and the minimal laws

27. **Per pair.** B1-link: a meeting only through made knots in run A. B1-ancestral: B1-link and a linking knot that is
    an ancestral common knot made by births. B1-dependence: B1-link, the courses differ, attribution accepted, no
    failing knot in run A and none in the run with A = ∅; a pair whose barred run was not knot-tested is "undecided:
    knot test not run". Failures in the lasting reruns are reported and are not a condition (BD2 6.3 names run A and
    the barred run).
28. **Per law.** Verdicts are decided per law and knot law, and a law "has" a verdict when it has it under at least one
    knot law; the minimal laws are given both ways. "found"; "none, every pair decided"; or "none among n decided, m
    undecided" (m pairs with B1-link whose dependence is undecided). The cost order is BD2 8 with family.json's costs:
    component-wise, a whole-roster look false < true, values 1 < 2 < 3 < h(u) + 1 < unbounded.
29. **C0.** The 290 items: 144 negative (no taking rule, the 9 recorded base laws, 8 starts, both knot laws, 7 rounds),
    144 positive (J-EACH-PART on the same, 4 rounds, s ≤ 3), and the planted case under both knot laws (family.json,
    "planted_ticket_A": made-4, ORD/CANCEL-RETIRE/MET(OLDEST); X and Y the two parts of round 1, s = 1, wholly apart;
    run A is a = 4, the barred run a = 1 with Y's member whose round-1 input is name 3 left usable, as ticket A's
    listing). The planted case passes when run A's meeting is classed "through a start knot".
30. **Process and cap.** At most 6 processes, 4 while the load is above 18 (`uptime` before each run); each process
    under a 6 GB address-space cap. The 70-minute cap counts from the start of run G. Before each run a sample of its
    items (every n-th, written only to the scratch folder) is timed. Items are run in the registered order through
    `imap`, so what is written is a prefix of whole items; a run is stopped at the deadline by terminating its own
    pool, and cuts are taken from the end of the registered order (M2, U1, 1c, P2, 1b).

## Written after run G, C0 and 1a passed, before P1

31. **"Tested in full" (BD2 1.3, runs P1 and U1)** is read as: every knot of the barred run and of the lasting reruns at
    every round read, for the same at most 8 pairs an item. Under parity, `knots.test_run` at every round. Under
    not-all-equal, start knots directly and every other knot by FD 7's birth method, whose verdict holds at every
    round from the knot's birth because every birth of these laws receives a fresh distinction (checked run by run;
    a run with a birth that received none would be tested by `knots.test_run` at every round). Run A is tested as in
    every run (item 19, with the direct check of the knots of at most 12 places at every round). Why: the timing
    sample of P1 (item 30) showed one rerun of PARENT-OWING-1/CANCEL-OFFSHOOT on Ring(7,3), not-all-equal, still in
    the direct check after 45 s, and the sample itself was stopped (its own processes) after 9 minutes; with the
    direct check at every round on every tested run, P1 would not fit the cap. Seen before this item was written: the
    sample's other items' sizes and times only (no verdict was read).
32. **The minimal laws after 1a, for N2** (BD2 7.3): B1-link and B1-ancestral: MET-SOLE with FLOOR1/CANCEL-WAIT (L02);
    B1-dependence: MET-SOLE with PARENT-OWING/CANCEL-OFFSHOOT (L10). Both are among the candidate laws of B4, so N2's
    laws are L02, L10 and the fixed law L07 (MET-SOLE with ORD/CANCEL-OFFSHOOT), under both knot laws.
33. **Run 1a differs from "Known before the runs", item 2** (written after 1a, no reading changed): under the nine
    recorded base laws with MET-SOLE this engine finds 328 meeting pairs (the prototype 640) and 176 pairs meeting only
    through made knots, all under FLOOR1/CANCEL-WAIT (88 per knot law: made-4 4, Ring(5,3) 20, Ring(5,3)+1 16, D2(5,3)
    20, Ring(7,3) 28); none on two-knot, made-3 or three-knot, and none under CAP-3/CANCEL-WAIT (the prototype: 312,
    216 under FLOOR1 on all 8 starts and 96 under CAP-3 on the ring starts; 32 in the every-member form, here 0). The
    growth itself was checked: the fold engine, with its candidate function wrapped at run time to keep only sole
    candidates (its file unchanged; a scratch script), gives the same structures on all 144 of these runs; and the
    meetings of one case (two-knot) were recounted by an independent scan of ancestry. Birth-by-birth listings of the
    differing cases are written to the outputs (`listing_*.txt`).

## Written after every registered run, from what the runs showed (no registered reading changed)

34. **A refinement of check (c), reported beside it.** The registered check (item 18) answered "yes" on every pair of
    the expected case, also on the unsymmetric ring, whose start has no renaming onto itself. So the renaming found is
    not a symmetry of the start: the structure after round s is read without the birth record and without marking
    start knots, and two sibling branches below the made linking knot can be exchanged. Reported beside the
    registered answer (never in place of it): the same search with every start knot also fixed
    (`check_c_fixing_start_knots.json`, `expected_listing.py`).
35. **U1 was run without a timing sample** (4 items; the pre-registration marks it "not timed"); it took 144 s on 4
    processes. P2 had no item: no run A, barred run, subset run or lasting rerun of 1a, P1 or 1b stopped at the guard
    (B5: P2 runs only where the guard stopped), so P2's two passes (x10, x100) ran 0 items.
36. **Run 1a's count of meeting pairs under the recorded rations** includes pairs that meet through a start knot at
    s = 1 or 2 (two-knot, made-4 and the ring starts, where the first parts of the growth meet again through a start
    knot one round later); see item 33 for the difference from the disclosed counts.
