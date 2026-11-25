# Ticket B: changes after the advisor's cold review (one line per item)

Review: `carries_b_advisor/answer.md`. The new scratch runs are `proto/b2_checks.py` (parts 1 and 2), `time_b2b.py`
and `time_wl.py`, with outputs in `outB2/`. "Applied" means applied in b2_claim.md, b2_definitions.md,
b2_preregistration.md and b2_data/.

## 1. B1, the claim
- **Split into link, ancestral and dependence, each with its own minimal laws:** applied (claim; BD2 6.1–6.3, 8).
- **"Which" renamed "How many through made knots":** applied as a reported reading (BD2 6.4).
  - **Not applied as the registered dependence reading. The scratch shows it is undefined on the seen case.**
  - The one-member runs have no meeting at all (part 2: on four starts, both knot laws, every singleton subset gives
    no meeting). "How many" needs a meeting in both runs.
  - So the registered dependence is "Whether through made knots": Y usable against Y barred, with attribution as the
    condition.
  - This follows the advisor's own item 6 ("the meeting in the one-member run") against its item 1. Question 1 for
    the last pass.
- **Which at equal number:** added as a reported reading. It is empty on the seen case, because the one-member runs
  have no meeting; the symmetry clause is in BD2 6.5. Applied.
- **Owner sentence 2:** corrected. Made links do form under the recorded rations (312 pairs, part 1). Applied.
- **The headline is the made link with the count in the same sentence:** applied (pre-registration, "Expected").
- **"Under FLOOR1 the round-5 demand fixes nothing the join holds":** right. "Hands a count over" is extended to the
  owing one round later (BD2 0). Applied.
- **The Y-side knot in the extra demand group:** run in part 2. It is Y's round-5 join of its two members, made only
  when both are usable. Reported as BD2 6.9; disclosed as item 4.

## 2. "Only through made knots"
- **The strict form, with the empty case defined:** applied (BD2 5.2, 5.3, 5.5).
  - The suppliers of cross takes are counted as links.
  - A meeting with an empty linking set is excluded and reported.
  - Part 1 saw no meeting with an empty RD 3.5 set.
- **FD 5.7's weaker class:** reported. Applied.
- **Ancestral aligned with FD 1.5 on the met members** ("not the parent of both" restored); the every-member form is
  reported apart (BD2 5.6). Applied.
  - Part 1: 312 of 312 strict meetings are ancestral in the FD 1.5 form, 32 in the every-member form.
- **"First" qualified:** applied. The fold study's results say a made ancestral common knot "appears only under the
  control law", so "first in the record" is said only for laws that use no names and do not look at parts.
- **The four checks of "the start's after all":** registered as reported checks (BD2 6.8). Applied.
  - Part 1 and part 2: no start knot holds a linking distinction.
- **"The start supplies the ancestors; the knot and both parts are made":** used. Applied.

## 3. PARENT-OWING
- **Its difference from PARENT-LOOSE:** stated as a registered item (BD2 2.8). Applied.
- **The plain form max(o, 3 − p, 1):** registered as a control (BD2 2.5).
  - Part 2: it gives the case on all four starts, both knot laws. Applied.
- **PARENT-OWING-1 makes two-place offshoots:** right (max(1, o) with o = 1). It is a control only. Applied.
- **PARENT-OWING-CAP3 and PARENT-OWING-CAP4:** added to the search. Applied.
  - Part 2: CAP3 gives no pair meeting only through made knots after rounds 3 and 4.
  - CAP4 gives such pairs with one class, so the case vanishes, as the advisor argued.
- **The mod-2 comparison:** run last (M2). Part 2 saw no strict pair. Applied.
- **Reader-test item 4 for every law:** added to `family.json`, computed by run 1 on the runs with Y barred
  (BD2 3 item 4). Applied.

## 4. B2, composed
- **The m reading** replaces RD 4.4's on class M's subsets, reported (BD2 6.6). "At least three classes" is dropped.
  Applied.
- **The first draft's "two classes, so it cannot be composed":** a bad inference, as the advisor says. Logged in the
  disclosure (item 5).
- **Class C:** cut. **The composed claim:** a later ticket with a two-by-two class and a planted composed case.
  Applied.

## 5. The family, the order, "least"
- **The order on values,** with a law's value taken as its largest rule's: applied (BD2 3 item 5).
- **MET-SOLE "new_rule: false" was wrong:** fixed. `new_rules` now counts each new rule of a law. Applied.
- **OFFSHOOT-TWO and PARENT-OWING-1** were in the search in the first `family.json`; that was wrong. Moved to the
  controls. Applied.
- **Item 5 for treatments:** defined as the number of distinct acts on one short member. Applied.
- **Q-SOLE:** not added, as the thread decided. "Least among the listed laws" is used throughout.
- **The 18 marked comparisons:** cut, except mod-2. **STEPS2-SOLE:** runs last (1c). Applied.

## 6. Controls and catches
- **A start without the ring's symmetry:** Ring(5, 3)+1, chosen over the seven-knot generator. It removes the rotation
  symmetry while keeping the mechanism of the seen case, so a result there reads directly against it. The generator
  differs in too many ways at once.
  - Registered with no prediction, as decided. Part 2 has since seen the core case there; disclosed, and question 2
    for the last pass.
  - Its X and Y are still two-member parts of one form, so the sentences say "two like parts".
- **"Whether both":** used. Applied.
- **Lasting:** reruns to t_d + 2 whatever the main bound. Argued as implied for the seen mechanism and taken out of
  the headline (BD2 6.7). Applied.
- **The guard:** P2 runs only where the guard stopped at × 1, with peak counts recorded. Applied.
- **The constant-3 control:** added (OFFSHOOT-THREE). Part 2: no strict pair. Applied.
- **The meeting in the one-member run:** checked. There is none (see section 1).

## 7. Numberings
- **Lemma N with its six hypotheses,** marked (b): applied (BD2 7.2).
- **"DB 7":** defined; it is section 7 of the copier study's `definitions_b.md`. **"4n numberings":** removed.
  Applied.
- **N2 as registered by the advisor, with no knot test:** applied.
  - Every numbering of made-3 and two-knot (120 and 30).
  - On each ring start, the reversal and 10 drawn renamings instead of 30.
  - **Not applied as worded:** the whole-structure comparison is by an invariant ("not refuted"), not an exact
    canonical form. The exact test of two 920-knot structures ran past 4 minutes (`time_b2b.py`), while the invariant
    takes 0.04 s.
  - Every verdict and every course from X only is still compared exactly. Question 3.

## 8. Definitions
- **Each hole closed as a numbered definition:** applied.
  - descent (BD2 4.3);
  - meeting and links per run (BD2 5.1–5.4);
  - the bars' cap, per pair, |Y| ≤ 4 (BD2 4.4), which removes the "32 subsets" disagreement;
  - every ordered pair, against FD 5.8 (BD2 4.2);
  - attribution with a made link (BD2 6.3);
  - lasting (BD2 6.7);
  - PARENT-OWING's four points (BD2 2.2);
  - SHORT-BY's three points (BD2 2.4);
  - STEPS1-SOLE over the union (BD2 2.1);
  - J-EACH-PART (BD2 2.7);
  - the gate listing's provenance (header added to `gate_listing_b.txt`).

## 9. Sizes
- **The order of items inside runs** (law, then start small first, then parity before not-all-equal): applied.
- **One total cap of 70 minutes,** with the order of cuts: applied.
- **The knot test in barred runs:**
  - under not-all-equal, knots born after round s only; parity tests in full;
  - limited to pairs with a course difference, at most 8 an item, from the timing of 1.1 s a barred run (question 4).
  - Applied.
- **The estimate:** about 34 minutes at the measured rates.

## 10. Predictions
- **Re-marked as asked:** applied.
  - B0 is (b), and B5 is (b), true by construction.
  - B1 is split into a core (a) and details (c); attribution and m are (c).
  - B1″ is (a), now on 8 starts at the registered bounds (part 1).
  - B4 is (a); the negative control is (b).
  - "A third class" fails nothing.

## 11. Words
- **Owner sentence 1:** no longer uses "carries" or "meet again". Applied.
- **"Gives parts off", "Which through made knots", "in every numbering", bare "least", "it did not happen" and bare
  "first":** removed or qualified. Applied.
- **The title's "read":** said once, as the owner's word. Applied.

## 12. Sentences for the owner
- **The advisor's sentences:** adapted (pre-registration).
  - "Three ring starts" becomes "four ring starts" (Ring(5, 3)+1 added).
  - "Meet" becomes "come to share one knot" in sentence 1.
  - The recorded-ration links are counted (312).
  - Applied.

## 13. Required and optional
- **Required 1 to 11:** applied in order, except as noted under 1 (the registered dependence form) and 7 (the
  invariant comparison).
- **Optional:**
  - the plain form and the constant 3: applied (controls);
  - mod-2: applied (run last);
  - Q-SOLE: not added;
  - "removing symmetric pairs": not applied. Every ordered pair is kept, and the symmetry check is reported per pair
    (BD2 6.8).
