# Readings and deviations, PARENTS-FROM-HOLDERS-20261124-001A-E001

Written by the code's author (a helper agent) from the frozen pre-registration
(`research/PARENTS-FROM-HOLDERS-20261124-001A/preregistration.md`, SHA-256 `55a86f08...ab8`, checked against
`contract.json` before any code was written), the shared definitions (`research/RING-IN-BALANCE-20261123-001/definitions.md`,
SHA-256 `e7c001a4...648`, checked) and sections 1.1 and 4 of the one-birth-at-a-time study's definitions ("LR"). No frozen
text, earlier engine or earlier artifact was changed. The reference engine is imported unchanged through the earlier study's
`lr_reference.py`, which checks its SHA-256 sum (`2c6eac56...671`) on every import.

Before this file was written, only scratch measurements were made (in the session scratchpad, not in the repository): the
sizes of the P2 structures, the sizes of their biconnected blocks, counts of depth-d unfoldings (item 21) per law, and a
replay of R3's sampled orders against the stored results of the earlier study (all 27 runs matched their stored outcome
and birth count for seeds 0 to 19). No look was compared and no verdict was computed before this file.

Items 1 to 24 were written before run 1. Items added later say before which run they were written.

## Populations

1. **P1, the reference rounds.** "The reference structure after each complete round up to the last round it compared" is
   read as rounds 1 to `rounds_checked` of the earlier study's `gate.json` (the last round its gate compared): 5 for 18
   pairs, 2 for (GEN7, FLOOR1, CANCEL-RETIRE), whose growth stops at round 2, and 4 for (LONE-FOUR, ORD, STALL), which stops
   at round 4. The start (round 0) is not included: it is not the structure after a complete round, and it has no parent
   place.
2. **P1, the serial structures.** "For the law R3 at each cutoff" is read as every registered run of the law R3 in the
   earlier study: its 13 table rows at each of their cutoffs (22 runs) and its 5 item-4 rows, which run R3 at cutoff 3 on
   pairs of `gate.json` (27 runs in all). Each run's reference is rebuilt with that study's `RefData`, its law with
   `make_law(ref, 'R3')`, and seeds 0 to 19 are replayed with its `Runner.run_order` and the same uniform chooser
   (`random.Random(seed)`, `A[rng.randrange(len(A))]`) as its `sampled`. The replay is checked against the stored outcome
   and number of births of every seed; a difference stops the study.
3. **"The structure after every birth"** is the state after that birth and after the barrings made before the next birth
   (barrings are made as soon as they are allowed, LR 2.4.4); this is the state from which the next birth is chosen. The
   state before the first birth is not in the population. It is kept only as an unseen link for identity certificates
   (item 17).
4. **The structure of a state.** While every birth has matched, the run's structure is the sub-structure of the reference
   on the image set I, with the knots of Bar barred (the earlier study's `lr_laws.py`, docstring, and its deviations item
   1): a distinction is shared when both its reference holders lie in I, and a loose distinction is barred exactly when its
   holder is in Bar. Knots and distinctions keep their reference numbers.
5. **A mismatching birth.** Every order of (SCC, RATION-3, CANCEL-WAIT) at cutoff 1 ends in a birth that matches no
   reference knot. The structure after that birth is built as the structure before it plus one new knot that takes one
   usable loose distinction from each of its parents (the lowest-numbered, which makes no difference up to renaming) and
   receives the fresh count the law gave it, all usable. Its parents are its parent set. The order ends there.
6. **Duplicate states.** Within one run, states with the same image set and barred set are the same structure and are
   counted once. P1's reference rounds are the same structures as P2's first rounds (same engine, same start, same law)
   and are not duplicated when P1 and P2 are pooled.
7. **P2.** Each of the twenty pairs is grown by the reference engine round by round. The last round is the first round
   after which the structure has more than 2,000 knots (that round is included), or round 12. Where the growth stops
   earlier (no member left: GEN7 under (FLOOR1, CANCEL-RETIRE) after round 2, LONE-FOUR under (ORD, STALL) after round 4),
   later rounds would repeat the same structure and are not added. No pair stalls or jams within its bound.

## The look

8. **Chosen places** are the shared places of every knot: a pair (x, a) with a a distinction held by x and by one other
   knot y. Loose places are not chosen; the kinds are defined for shared places only.
9. **Kinds.** P (parent place): y is a parent of x. C (child place): x is a parent of y. S: x and y are both start knots.
   A shared place of any other kind stops the study. "Not a parent place" is C or S. A class of looks is **mixed** when it
   holds a P place and a C or S place. Classes holding C and S but no P are counted separately and are not the question.
   The kind is read from the record of parents only.
10. **The full look** is a coloured graph. Its knots are those at holder-step distance at most d from x. Each place of each
    such knot is a distinction marked U (loose, usable), B (loose, barred) or S (shared). A shared distinction both of
    whose holders are in the look is one distinction with two holders, whatever their distances (so one shared by two
    knots both at distance d is one distinction, the first choice of the text). A shared distinction whose other holder
    is farther than d has one holder in the look and is marked S only. Two such distinctions leading to one unseen knot
    are two separate one-holder distinctions (the second choice). x and a are marked. Distances are computed in the
    structure; they equal the distances inside the look, since every shortest path to a knot within d stays within d.
11. **The first coarser look** (C1) is the full look with U and B merged into one mark L (loose).
12. **The second coarser look** (C2), "with knots only as live or dead and their numbers of places", is read as: each knot
    of the look carries only whether it is live (holds a loose distinction, usable or barred; definitions line 14) and its
    number of places; the shared distinctions both of whose holders are in the look are shown as before; loose
    distinctions and shared distinctions whose other holder is outside are not shown one by one. For a knot inside the
    rim this keeps the number of loose places (places less shared ones); at the rim it keeps only whether the knot has a
    loose place. Each coarser look is a function of the full look, so alike full looks are alike coarser looks.
13. **Alike.** Two looks are alike when a one-to-one renaming of knots and of distinctions of the look carries one onto
    the other with x to x, a to a, every mark kept (for C2, every knot's live bit and number of places kept), and every
    distinction onto a distinction with the images of its holders.
14. **The compressed form used for the search.** The search works on the knots of a look, with each knot coloured by
    (is x, number of U, number of B, number of one-holder S) for the full look ((is x, number of L, number of one-holder
    S) for C1; (is x, live, number of places) for C2) and each pair of knots that share distinctions in the look joined
    by one edge labelled (number of shared distinctions, whether a is among them). A renaming of looks gives a renaming
    of compressed forms, and conversely a renaming of compressed forms extends to a renaming of looks (distinctions with
    the same mark at one knot, and shared distinctions between the same two knots other than a, are interchangeable). The
    extension is built explicitly (in increasing distinction number within each set) and checked place by place before
    any pair is reported alike in an output file.

## Certificates both ways

15. **Told apart.** Two looks are reported not alike only when one of these differs, each computed on the extracted look
    or, for item 21, provably a function of it: (i) the depth-d unfolding of item 21; (ii) the canonical colour refinement
    of the compressed look with x marked (number of rounds to stability and the multiset of final colours, colours named
    by interned signatures); (iii) a joint refinement of the two looks' disjoint union that leaves some colour class with
    unequal numbers of knots from the two looks; or (iv) the exhaustive individualization-refinement search of item 16,
    which finds no renaming. A hash is never used: every invariant is an interned tuple, so equal identifiers mean equal
    values.
16. **The search for a renaming** is individualization and refinement on the disjoint union of the two compressed looks:
    refine to the coarsest equitable partition; if a class is unbalanced there is no renaming; if every class holds one
    knot from each look the pairing is the renaming; otherwise take the first class with more than two knots, fix one of
    its knots from the first look and try, one by one, every knot of the second look in that class. Every renaming maps
    the fixed knot to one of those, so the search is exhaustive: it reports "not alike" only when every branch fails.
17. **Alike, certified.** Two places are put in one class only by a chain of these certificates, each a renaming that is
    checked: (i) a renaming found by item 16 and checked place by place; (ii) an automorphism of a whole structure (item
    20), checked place by place on the whole structure, which restricts to a renaming of the looks at every distance and
    for every kind of look; (iii) the identity, when the look of a place in a structure is literally the same (same knots,
    same distinctions, same marks) as its look in the next structure of the same lineage (the next round, or the next
    state of the same order); this is certified by the rule that no knot within distance d of x changed (item 18); (iv)
    a renaming of the looks at distance d + 1, restricted to distance d (the look at d is a function of the look at
    d + 1); (v) a renaming of the full looks, for the coarser looks.
18. **Identity across a step.** Between two consecutive structures of a lineage, the changed knots are the new knots and
    the old knots whose places changed (a loose place taken or barred). The look of (x, a) at distance d is unchanged when
    every changed knot is farther than d from x in the later structure: then no knot within d changed, no new knot is
    within d (a new knot meets only changed knots), and no distance up to d changed.
19. **Pairs reported** are always written with an explicit renaming of the two looks, found by item 16 directly between
    the two places and checked place by place by a separate routine, even when the class was certified by a chain.
20. **Automorphisms of a whole structure from the record.** For a reference structure, candidate automorphisms are built
    from the record: every automorphism of the start's compressed form (found by exhaustive search) and every exchange of
    two knots born in the same round with the same parents and the same numbers of places and barred places, each
    extended round by round by sending a knot with parents Q to an unused knot of its round with parents σ(Q) and the same
    numbers. Each candidate is checked place by place on the whole structure and is used only if it passes (a failure is
    reported). They are used only to put places in one class, never to tell places apart. Serial structures are not given
    such automorphisms; their places are compared by items 16 and 18 only.
21. **The depth-d unfolding.** For a chosen place (x, a) and distance d: x's marks and, for each shared place p of x
    (with a marked), the unfolding of depth d − 1 of the other holder of p entered through p; the unfolding of depth k of
    a knot z entered through e is z's marks and the multiset of the unfoldings of depth k − 1 of the other holders of z's
    shared places other than e (non-backtracking walks); depth 0 is z's marks alone. Marks are (U, B, S counts) for the
    full look, (L, S) for C1, (live, number of places) for C2. It is computed for every place at once on the structure,
    but it is a function of the look: a walk of length at most d from x visits only knots within d, a knot reached after
    t < d steps is within d − 1 so all its shared places lead into the look, and a knot reached after d steps contributes
    only its marks, which the look shows. It is used to group places before the search; places with different unfoldings
    are told apart by it.

## Reports

22. **Groups of a pair.** "On one knot or within one structure": both places in one structure. "Across two rounds of one
    start": two structures of the same start and law (two rounds, a round and a serial state, or two serial states). "Across
    two starts". A mixed class is put in the first group that it contains a pair of.
23. **Populations of a verdict.** Classes are computed once per law, kind of look and distance on all the structures of
    that law (P1 and P2 pooled), since being alike does not depend on the population; each population's numbers are the
    restriction. Reported: P1, P2, P1 and P2 pooled, and P2 by round (the structures after round t of every start of the
    law). The stop rule's "no confusable pair on P1 and P2" is read on the pooled population, which also holds pairs
    across the two.
24. **The guard count** is the number of chosen places whose look at d holds no start knot and no member (a knot with a
    usable loose distinction), computed from the distances to the nearest start knot and the nearest member. It is
    reported per law, distance and P2 round, for P1's reference rounds per round, and for P1's serial structures per run.
25. **Run 4's choice.** A place's farness is the least of the distance from its knot to the nearest start knot and to the
    nearest member. A pair's farness is the smaller of its two places' farness; the pair of greatest farness is written
    out, ties broken by the larger sum of the two farness values, then by the larger structure, then by the lowest
    numbers. Its least separating distance is searched from d + 1 to 10.
26. **Run 4's pair followed from round to round** is a pair within one structure (the advisor's pair for (FLOOR1,
    CANCEL-OFFSHOOT)); for the other laws, the confusable pair within one P2 structure at the greatest distance, chosen by
    item 25, followed in that start's later rounds (the same two knots and distinctions exist in every later round).
27. **Run 5** asks whether some automorphism of a whole final P2 structure (at most 2,000 knots) carries a parent place to
    a place that is not one (P8's wording; a child place is a special case). The unfoldings of item 21 are computed on the
    whole structure to the depth at which their partition of places stops refining (from then on it never changes);
    places with different unfoldings are told apart for whole-structure renamings (the whole structure is then the look);
    any remaining pair of kinds P and C or S with equal unfoldings is decided by item 16 on the whole structure.
28. **Check (b)'s places.** On the two-knot start under (FLOOR1, CANCEL-OFFSHOOT, RELEASE): A is start knot 0, a1 the
    lower-numbered of A's two offshoots born in round 1, a2 the other, j the knot whose parents are exactly {a1, a2}. The
    two places are a1's place shared with A (kind P) and a1's place shared with j (kind C). For R = 4 to 9 the full looks
    are compared at d = 1 to R + 1; the check passes when they are alike exactly for d ≤ R − 2.
29. **Check (c)'s plant.** On a copy of a structure, one loose place of a knot y at holder-step distance exactly 4 from x
    has its mark changed (usable to barred, or barred to usable). The full looks of (x, a) in the original and the copy are
    compared at d = 1 to 6; the check passes when they are alike for d = 1, 2, 3 and not alike for d = 4, 5, 6. It is run
    on 60 plants drawn on P2 structures of every law.
30. **Check (a)'s draw.** 200 looks of at most 8 knots: 80 from the populations (structures of every law after rounds 1
    to 3, d from 1 to 3, the full and the coarser looks), 60 from random small structures, 30 renamed copies of drawn
    looks (knots and distinctions renumbered at random, so alike pairs with different numbers occur), 30 made by changing
    one detail of a drawn look (a mark at the rim, or a distinction shared by two rim knots made into two one-holder
    shared distinctions, which tests the first choice of the text). Every two different looks of the same kind of look are
    compared by the code (items 14 and 16, then the place-by-place check) and by trying every renaming of knots (x fixed)
    with, for each, the test that the distinctions can be matched (equal multisets of mark, images of holders and whether
    the distinction is a), which shares no code with the search. Five hand-built pairs with a known answer test the two
    choices of the text and the coarser look C1. The check passes when the code and the trial of every renaming agree on
    every pair and every hand-built pair gets its known answer.
31. **Written after a first run of run 1, before any other run.** The first run of run 1 passed all three checks, with
    check (a) drawn as 100 population looks, 60 random and 40 changed looks, compared in 6,771 pairs, 0 disagreements;
    but its 265 alike pairs included the 200 pairs of a look with itself, so only 65 alike pairs were of two different
    looks. Check (a) was then strengthened as item 30 says (renamed copies, no look compared with itself) and run 1 run
    again; the registered result is the second run. The first run's checks.json is kept in the session scratchpad only.

## Written after run 1 and before runs 2 to 6

Development runs of the class computation were made on (FLOOR1, CANCEL-RETIRE) with outputs in the session scratchpad,
to check the code; the registered runs are made afresh by `pfh_run.py`.

32. **Unfoldings computed on the look.** For every place that takes part in a comparison, the unfolding of item 21 and the
    colours of the knots of its look (item 35) are computed again on the extracted look alone (`pfh_views.in_look`) and
    checked to equal the values computed on the whole structure; a difference stops the run. The same check is made on
    1,000 places drawn at random for every kind of look and distance, so that the values used to tell untested places
    apart are checked on a sample too. The counts are written to every output file (`in_look_checked`,
    `in_look_sampled`).
33. **Identical labelled looks of serial states.** Every structure of one start and law (P2's rounds and the serial
    states) is a sub-structure of that start's P2 lineage, with the same numbers of knots and distinctions; this is checked
    for every serial reference (`serial_prefix_checks`). For serial states, the look of (x, a) within d is determined by
    x, a, the knots within d, which of their reference neighbours are present and which of them are barred; two places with
    the same such key have literally the same look (identity renaming). Structures after a mismatching birth (item 5) take
    no part in this.
34. **Whole serial states.** Serial states of one run with the same invariant (numbers of knots and places, and the
    multiset of whole-structure unfoldings at the depth where they stop refining) are compared by the search of item 16 on
    their whole compressed forms; a renaming found is completed to distinctions and checked place by place, and then every
    place of one is linked to its image in the other. Within each state that is not a copy of an earlier one, places with
    equal whole-structure unfoldings are compared by the search on the whole state with the two places marked, and each
    automorphism found (checked place by place) links every place to its image. These links hold at every distance and for
    every kind of look.
35. **How two looks are compared.** Each knot of a look is coloured by its compressed colour, its distance from x and its
    unfolding of depth d minus that distance, entered from no side (a function of the look by the argument of item 21,
    and computed on the look, item 32). If the multisets of colours differ, the looks are not alike. Otherwise a renaming
    is first sought by matching outwards from x, pairing neighbours with the same colour and edge label in increasing order;
    the result is checked edge by edge and then place by place. If that fails, the colour refinements of the two looks are
    compared (item 15 (ii)), and if they are equal the exhaustive search of item 16 decides. Within a group of places with
    equal unfoldings, each component of the certificates of item 17 is compared with the representatives of the classes
    already found, so every two classes reported are told apart by one of the quantities of item 15.
36. **Order of the computation.** Classes are computed for the full look at d = 6, 5, ..., 1, then C1 and then C2 in the
    same order; the classes of (C1, d) start from those of (full, d) and of (C1, d + 1), and (C2, d) from (C1, d) and
    (C2, d + 1) (item 17 (iv), (v)). Every carried link is checked to join places with equal unfoldings.

## Written after runs 2 to 5 of three laws (F1R, F1O, R3W), before the additions below were run

37. **An addition to run 5 (not registered).** Run 5 is registered for final P2 structures of at most 2,000 knots. Because
    each P2 lineage stops at the first round after which it has more than 2,000 knots, this tests only 8 of the 20 final
    structures (none under RATION-3). As an addition, clearly marked as such in `whole_extra.json`, the same test is made on
    the last round of each lineage with at most 2,000 knots. It does not change any registered verdict.
38. **Run 6 where no rule exists on P1 and P2.** On every law finished so far P1's serial states hold confusable pairs at
    every distance (most within one structure, exchanged by a renaming of the whole small structure), so no law has a rule
    "on P1 and P2" and run 6, read literally, applies to none. It is made, as an addition, where a rule exists on P2 alone:
    for (FLOOR1, CANCEL-RETIRE) at distance 2 (a stated rule, checked against every place of P2, P1's reference rounds and
    P1's serial states); for a law whose least distance on P2 has a guard count of zero, the table is reported by its size
    only, with that count, since it is a property of these small structures (pre-registration, "The count that guards
    against an artifact").
39. **An addition to run 4 (not registered): pairs exchanged by a whole structure.** For each law, every mixed class of
    the full look at d = 6 that holds a parent place and another place in one structure is tested once: is there a
    renaming of that whole structure (search of item 16 on the whole structure with the two places marked, then checked
    place by place) carrying one onto the other? Such a pair is one that no look of any distance tells apart in that
    structure. Written to `whole_pairs.json`.
40. **An addition to run 4 for ORD (not registered).** Under (ORD, STALL) the pair chosen by item 26 lies in the final
    structure of LONE-FOUR (the growth has stopped there after round 4), so it exists in a single round and cannot be
    followed. As an addition, the pair written out by run 4 at the greatest distance outside that lineage (d = 5, on the
    two-knot start, round 12) is followed through every P2 round in which both places exist, up to d = 10. Written to
    `followed_extra.json`.

## Written after all runs: what was run, and what in the frozen text could not be followed as written

41. **Runs.** Run 1 (checks) passed on its second run (item 31). Runs 2 to 5 were each run once per law by `pfh_run.py`,
    four processes at once, each under an 8 GB address-space cap set in the script, and all finished within their stated
    bounds: F1R 52 s, F1O 4 min 28 s, R3W 10 min 05 s, ORD 15 min 19 s (wall clock; peak resident memory 0.7, 2.1, 4.7 and
    5.5 GB). The two longer than about ten minutes were run in the background; their command lines, from this folder:
    `/home/jscul/p-vs-np-contact-first/.venv/bin/python -B pfh_run.py --law R3W` and the same with `--law ORD`. They are
    not entered in `docs/LONG_RUNNING.md` by this helper (no tracker scripts were run). The knot test (3 s), run 6 and the
    additions of items 37, 39 and 40 ran in under ten minutes each. No bound was shrunk.
42. **Places in the frozen text that could not be followed literally** (each also stated in the report):
    - Run 5 is bounded to final P2 structures of at most 2,000 knots, while P2 stops at the first round after which a
      structure has more than 2,000 knots; so 12 of the 20 final structures are excluded by construction, including
      every RATION-3 one (item 37 adds the last round under the bound).
    - Run 6 applies "where a rule exists at some distance on P1 and P2"; no law has one, because P1's serial states hold
      confusable pairs at every distance, almost all of them exchanged by a renaming of a whole small structure (item 39).
      Run 6 was made on P2 alone where a rule exists (item 38).
    - The stop rule's second branch follows one pair; a fixed pair's least separating distance is bounded by its distance
      to the start knots, so only a pair placed symmetrically about the start (the advisor's kind) can show growth
      without limit; under RATION-3 the followed pair grows by one per round from round 6 to round 10 and stays at 5 at
      round 11, while the least distance with no confusable pair, round by round, keeps growing. Both are reported.
    - P8's wording ("a place that is not one") and run 5's ("a child place") differ; the test is the wider one, and its
      only positive case carries a parent place onto a child place, so both readings fail together.
