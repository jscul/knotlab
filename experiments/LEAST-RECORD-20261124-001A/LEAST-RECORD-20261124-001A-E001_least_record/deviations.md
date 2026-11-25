# Readings and deviations, LEAST-RECORD-20261124-001A-E001

Written by the code's author (the helper agent who wrote the earlier study's program) from the frozen pre-registration
(`research/LEAST-RECORD-20261124-001A/preregistration.md`, SHA-256 `fba75f53...929a`), the earlier pre-registration
(`55a86f08...ab8`) and the shared definitions (`e7c001a4...648`), all checked against `contract.json` before any code was
written and again by every script. The holding study's pre-registration (`research/GUARD-CAP-AND-HOLD-20261124-001A`) was
read for P3's four laws. No frozen text and no file of the earlier study was changed. "The earlier deviations" are
`experiments/PARENTS-FROM-HOLDERS-20261124-001A/.../deviations.md`; their items 1-42 hold here unless changed below.

Before this file was written, only the condition and the P3 lineages were computed once (a smoke test of two new
functions; see item 6), nothing about looks or stamps.

Items 1 to 20 were written before run 1. Items added later say before which run they were written.

## The program

1. **One program.** The earlier study's modules (commit `307b3bbe63`) are copied into this folder and extended there:
   `pfh_common` (paths, sums, the laws with holding), `pfh_struct` (stamps, generations, children), `pfh_look` (a look
   shows the stamp of every knot it shows; a renaming must keep stamps), `pfh_views` (the unfoldings include stamps),
   `pfh_auto` (whole-structure maps keep stamps), `pfh_pop` (round records kept, the condition, P3), `pfh_classes` (one
   stamp at a time), `pfh_report` (tables split by the condition, guard counts, the smallest pair). The earlier folder is
   not touched.
2. **The full look only.** The text asks for the classes of looks with each stamp shown; it does not name the earlier
   study's two coarser looks, so they are not computed (they remain in the code, used only by check (a)).

## Stamps

3. **Stamps are written from the record of the structure in which they are shown.** HAS-CHILD: the knot has at least one
   child in that structure (so in a half-built structure it is set at the parent's first birth). JOIN and PARENT-COUNT:
   the knot's parents. START-KNOT: the knot has no parents. HAS-CHILD with START-KNOT: the pair, as one value of four.
   NOT-MEMBER: the knot has no usable loose place now. The generation: 0 for a start knot, otherwise one more than the
   greatest generation of its parents, computed in the structure itself (parents are always present with their child).
   A generation stamp is the generation, or the generation modulo 2, 3 or m.
4. **Where a birth's parents have unequal generations** the stamp is still the true generation (as the text says); every
   such birth is counted and listed by run 3.
5. **The knot made at a mismatching birth** (the earlier deviations, item 5; the start-clause counterexample only) has the
   generation one more than its parents' greatest and is counted by run 3 as a birth the complete rounds do not make.

## The condition

6. **The condition is computed from the complete rounds of a start's lineage** (the P2 lineage for P1 and P2, the P3
   lineage for P3): it fails when, in some round, a start knot is on the engine's record of knots that wait (CANCEL-WAIT;
   `rec['waiting']`) while a start knot that shares a distinction with it acts, a knot acting in a round when it is a parent
   of a birth of that round. Start knots meet only through the start's own distinctions. The condition of a start holds
   for every structure of that start: its rounds and its serial states. A smoke test of this function, run before this
   file, found it failing on the start-clause counterexample alone, in round 1 (knot 0 waits while knots 1, 2 and 3 act);
   it is run again by the registered scripts.
7. **Every result is split by the condition.** Each population (P1, P1's reference rounds, P1's serial states, P2, P2 by
   round, P1 and P2 pooled, P3, P3 by round) is reported whole and restricted to the starts where the condition holds
   ("| holds") and where it fails ("| fails").

## P3

8. **P3** is every one of the four laws with holding of the holding study's run 4 ((CAP-3, CANCEL-WAIT, HOLD),
   (RATION-3, CANCEL-WAIT, HOLD), (FLOOR1, CANCEL-RETIRE, HOLD), (FLOOR1, CANCEL-OFFSHOOT, HOLD)) on each of D2(4, 3),
   Ring(5, 3), the two-knot and the three-knot starts: sixteen lineages, including (RATION-3, CANCEL-WAIT, HOLD) on the
   two small starts, which the holding study's disclosed table did not run but which its run 4 and this text name. Each
   is grown by the reference engine with `release='HOLD'`; the structure after each of rounds 1 to 6 is kept; a lineage
   ends at the first round that changes nothing (no birth and no barring: every later round is then the same), and that
   round is not added again. A round with no birth in which knots retire changes the structure and is kept.
9. **P3's classes** are computed per law with holding on its four starts (structures under different laws are not
   compared), with the stamps NONE, GENERATION-MOD-3 and GENERATION (run 7).

## Guard counts and the least distance

10. **The two guard counts.** The first: chosen places whose look within d holds no start knot and no member (the
    earlier study's count). The second, as registered: among those, the ones whose look holds no place shared by two start
    knots. **This second count always equals the first**: a look holds a place only of a knot it shows, and a place shared
    by two start knots is held only by start knots, so a look with no start knot holds no such place. It is computed as
    written and reported, and the text is said to be wrong here. Reported beside it, as a reading of what the advisor asked
    for ("for GEN-2, also require no place shared by two start knots in the look"), is a third count: chosen places whose
    look within d holds no member and no place shared by two start knots (start knots allowed).
11. **A rule that counts.** With a stamp shown, a population has a rule at distance d when it has no confusable pair at d;
    it counts only when the first guard count there is not zero, and for GENERATION-MOD-2 only when the second is not zero
    (the same, item 10). The least distance with no confusable pair and the least distance with a rule that counts are both
    reported, overall and by round; for GENERATION-MOD-2 the least distance with a rule that counts under the third count
    is reported as well.
12. **By round** means P2's structures after round t of the starts of the law, P1's reference rounds likewise, and P3's.

## Runs

13. **Run 1, check (a).** The earlier study's check program, copied, is run unchanged with every stamp NONE: its draw of
    200 looks (all three kinds of look), the advisor's pair with its threshold, and 60 planted marks. As an addition, the
    same comparison of the code against the trial of every renaming is made on 200 looks drawn with stamps shown
    (HAS-CHILD, START-KNOT, JOIN, GENERATION-MOD-2, GENERATION-MOD-3 and GENERATION), the trial requiring every stamp kept.
14. **Run 1, check (b).** The stamp CONSTANT (7 on every knot) and NONE are computed independently on every structure of
    (FLOOR1, CANCEL-RETIRE) and of (FLOOR1, CANCEL-OFFSHOOT); the check passes when the classes are the same partition of
    the chosen places at every distance from 1 to 6. As an addition, the classes of NONE are compared with the earlier
    study's published tables of the full look for those two laws (places by kind, classes, mixed classes and their groups,
    guard counts, for P1, P2 and pooled).
15. **Run 1, check (c).** The five-knot structure of the text, with a1 and a2 offshoots of A and J their join, B a start
    knot: generations 0, 0, 1, 1, 2, and the kinds of its eight chosen places: (A, A-B) and (B, A-B) between start knots;
    (A, A-a1), (A, A-a2) child places; (a1, A-a1), (a2, A-a2) parent places; (a1, a1-J), (a2, a2-J) child places;
    (J, a1-J), (J, a2-J) parent places. (Ten places: the text's "every shared place".)
16. **Run 1, check (d).** On a copy of a structure, the stamp of one knot at holder-step distance exactly 4 from x is
    changed (to another value of the same stamp); the looks of (x, a) in the original and the copy are compared at d = 1
    to 6; the check passes when they are alike for d = 1, 2, 3 and not alike for d = 4, 5, 6. 60 plants, on P2 structures
    of every law, with the stamps GENERATION-MOD-3, GENERATION-MOD-2, HAS-CHILD and START-KNOT in turn.
17. **Run 3.** A birth is a knot with parents. For each start and law, every knot of the last structure of its lineage
    (which holds every knot of P1's reference rounds and serial references, item 33 of the earlier deviations) is a birth
    of P1 and P2; P3 likewise; the knots made at mismatching births are counted separately. For each birth: whether its
    parents have equal generations, and the greatest difference between its generation and a parent's. Births with
    unequal parents are listed with their round, parents and generations.
18. **Run 4.** The rules are checked against every chosen place of the populations named, read from the look at distance
    1 (stamps of x and of the other holder only): GENERATION-MOD-3, "the other holder is a parent exactly when its stamp is
    one less, modulo 3"; GENERATION, "exactly when its stamp is smaller"; GENERATION-MOD-m with m = 2 Delta + 1 (run 6),
    "exactly when x's stamp less the other holder's, modulo m, is between 1 and Delta". Any other stamp with a rule that
    counts gets its rule stated and checked in the same way.
19. **Run 5.** For each stamp and law, in P1 and P2 pooled where the condition holds, where it fails, and in P3: at the
    largest distance from 1 to 6 with a confusable pair, the pair whose structures have the fewest knots (then the lowest
    numbers), with an explicit renaming checked place by place and whether a renaming of the whole structure exchanges the
    two places.
20. **Order and inheritance.** Each process computes, for one law, a chain of stamps in which each later stamp is a
    function of the first: (GENERATION, GENERATION-MOD-3, GENERATION-MOD-2, and GENERATION-MOD-m where run 3 gives m),
    (PARENT-COUNT, JOIN), (HAS-CHILD with START-KNOT, HAS-CHILD, START-KNOT), (NONE), (NOT-MEMBER); a renaming that keeps
    the first stamp keeps the later ones, so the classes of the first carry over (the earlier deviations, item 17 (iv)
    and (v)), each carried link being checked to join places with equal unfoldings. NOT-MEMBER and NONE are computed
    independently of each other, since P4 compares them.

## Written after run 1, before run 3

21. **Run 1** was started three times. The first two stopped on errors in the new code before any check had a result
    (the generation required knots to be numbered parents first, which the renamed copies of check (a) are not; and a
    misnamed variable in `pfh_views.marks_of`); both were fixed (the generation is now computed by recursion over the
    parents, whatever the numbering) and the third run is the registered one. All four checks passed.

## Written after run 3, before runs 2, 5, 6 and 7

22. **Run 6's modulus.** Run 3 found the greatest difference on the start-clause counterexample to be 2 (one birth, knot
    16 of round 2, parents 0, 7, 8, 9 of generations 0, 1, 1, 1), so the stamp of run 6 is GENERATION-MOD-5. It is
    computed for every structure of (RATION-3, CANCEL-WAIT) in the chain of GENERATION, and reported where the condition
    fails (and, for completeness, where it holds).
23. **Processes.** One process per law and chain (item 20) for P1 and P2, and one per law with holding for P3 (the chain
    GENERATION, GENERATION-MOD-3, then NONE, the last carried over from GENERATION, which is valid since NONE is a
    function of every stamp); at most six at once, each under an 8 GB address-space cap set in the script. Each writes, for
    each stamp, one JSON per population (P1, P2, P1 and P2 pooled; P3), its smallest pairs (run 5), and its class table to
    the session scratchpad for the comparisons of P4 and P5.

## Written while runs 2, 5, 6 and 7 were running, before run 4

24. **Run 4's rules for other stamps.** A rule that counts on P1 and P2 where the condition holds was seen in a development
    run (scratchpad only) for START-KNOT and HAS-CHILD with START-KNOT under (FLOOR1, CANCEL-RETIRE) at distance 2. The
    rule stated for them is the earlier study's rule for that law (its run 6), with its first test (a start knot read from
    its number of places) replaced by the stamp, and a second test added: if the other holder is a start knot and x is not,
    the place is a parent place. It is checked against every chosen place like the others; any other stamp and law with a
    rule that counts in the registered runs is listed by the summary with its table size, and a statement is added only
    where one can be stated and checked.
25. **"No confusable pair" and "the stated rule".** Under GENERATION-MOD-3 the start-clause counterexample may have no
    confusable pair at distance 1 although the stated rule ("one less, modulo 3") gets a place wrong there: the look at
    distance 1 shows more than the two stamps. Both are reported: P2's clause about the modulo-3 rule is judged on the stated
    rule.

## Written after run 4's first pass, before its second (the stated rules for other stamps)

26. **Rules that count for stamps other than the generations** (registered runs, P1 and P2 where the condition holds,
    distance 2): START-KNOT, HAS-CHILD with START-KNOT, PARENT-COUNT and GENERATION-MOD-2 under (FLOOR1, CANCEL-RETIRE),
    and PARENT-COUNT under (FLOOR1, CANCEL-OFFSHOOT). For each, the rule is first of all the table of looks at distance 2
    (every class holds places of one kind; its number of classes is reported). A shorter statement was sought (by hand,
    and by an induced decision tree over plain features of the look, in the scratchpad) and two were found and checked
    against every chosen place: item 24's rule for the start-knot stamps, and for PARENT-COUNT the decision list of
    `lrec_rules.rule_floor1_parent_count`. Both reproduce every place of P2 and of P1's reference rounds, and fail on part
    of P1's serial states, where a knot can hold a loose place after its first birth; no shorter statement covering the
    half-built structures was found, and none is claimed. For GENERATION-MOD-2 under (FLOOR1, CANCEL-RETIRE) no shorter
    statement was found.

## Written after all runs

27. **Runs.** Run 1 passed (item 21). Run 3, run 4 and the summary each took under a minute. Runs 2, 5, 6 and 7 were made
    once, by `lrec_run_all.py --jobs 6` (25 min of wall clock in all), 24 processes, each under an 8 GB cap, all with exit
    status 0; peak resident memory at most 3.7 GB. Six took longer than about ten minutes (wall clock): ORD chain H 25 min 04 s,
    ORD chain G 18 min 01 s, ORD chain P 15 min 07 s, R3W chain G 15 min 01 s, R3W chain H 10 min 28 s, ORD chain M
    10 min 27 s; each was started from this folder as
    `/home/jscul/p-vs-np-contact-first/.venv/bin/python -B lrec_run.py --law <law> --chain <chain>`. They are not entered
    in `docs/LONG_RUNNING.md` by this helper. No bound was shrunk.
28. **What in the frozen text could not be followed as written.** (i) The second guard count equals the first by
    construction (item 10); it is reported, equal to the first in every one of 12,822 rows, and a variant is reported
    beside it. (ii) "On every structure of every start where the condition holds" (P8) and the stop rule's "where the
    condition holds" are read on P1 and P2 pooled; by law, since structures under different laws are not compared.
    (iii) P3 under (RATION-3, CANCEL-WAIT, HOLD) has both guard counts zero at every distance, so no stamp, GENERATION
    included, can have a rule that counts there, although GENERATION's rule is right on every place (P3's check).
