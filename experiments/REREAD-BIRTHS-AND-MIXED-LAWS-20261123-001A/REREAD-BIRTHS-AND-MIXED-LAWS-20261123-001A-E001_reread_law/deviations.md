# Deviations, readings and limits (REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001A-E001)

Nothing in the pre-registration's "Definitions (frozen)", "Predictions (frozen)" or "Runs and stop rule" was changed.
Section A was written before any code was run; it lists every place where the note leaves a choice and the reading
taken. Section B, added during the runs, lists limits met and anything found after values were seen. Recorded code is
read, never changed: `end_operator.py` of `ORDINARY-DYNAMICS-20261120-001A` (groups, lookahead, the ordinary step) and
`lib.py` of `REVIEW-LEADS-20261123-001A` (sources, draws, ordinary driver, operator test, growth kind), both imported
by path from `rlaw.py`; `edits.py` of `WHOLE-STAGE-SETTINGS-20261120-001B` (the two set-ups of test (d)), imported.

## A. Readings fixed before the first run

1. **Which births a short knot pays with a shared distinction.** Births are made in the recorded engine's order
   (groups of three or more in sorted order, then pairs, then one-parent births). Each parent hands out its loose
   distinctions in that order, the last listed first, exactly as `lib.grow` does; once its loose distinctions are
   gone it pays each further birth with a shared distinction chosen by the convention. In the enumeration of every
   allowed choice, both the set of births a short knot pays with shared distinctions and the distinction paid to each
   are enumerated (loose distinctions of one knot are interchangeable and are not permuted).
2. **"Shares", "allowed", read at the start of the round.** A knot pays with a distinction it holds that has two or
   more holders when the round starts (its own loose distinctions handed out earlier in the same round do not count).
   A payment is not held, at the start of the round, by another parent of the same birth (a parent can only pay what
   it holds, so "or pays" adds nothing). A knot pays different distinctions to its different births in one round, as
   it owes one distinct distinction to each group. Two different knots may pay the same shared distinction to two
   different births in one round; the rule does not forbid it.
3. **Oldest and newest** are the smallest and largest name. Names grow with creation (at the start: meetings first,
   then each knot's loose distinctions; at each round fresh names in birth order), so the smallest name is the oldest;
   distinctions of the start, all of one age, are ordered by name.
4. **Residual stall.** Under a convention: some short knot finds no allowed distinction for one of its births; the
   round does not happen and the history ends there. The enumeration of all choices (test (c)) says whether some other
   choice would have paid.
5. **Witnesses and demand under R** are read from the full holdings: every knot holding a distinction that a birth
   holds witnesses that birth (under ordinary growth these are exactly its parents). The lookahead takes every birth
   as provisionally live with one opening, and each knot's witnessed set (old knot or birth) is the set of births it
   shares a distinction with; groups and demand are then the recorded `proposals`. The next end is read the same way
   from the holdings after the round. On a round with no payment both equal the recorded child rosters (gate G).
6. **Closing under R.** Under parity a birth receives no fresh distinction exactly when the GF(2) vector of the
   distinctions it takes lies in the row span of the stars of all knots of the stage before the round (every knot of
   even parity). Several births of one round may be implied; the history closes when no live knot remains.
7. **The laws.** Parity: every knot has even parity (as in the recorded counting code, `FORBIDDING-JOIN-20261120-001B`
   `counts.py`). Not-all-equal: the values of a knot's distinctions are not all equal.
8. **Horizons.** (b): 16 rounds or 20,000 knots, the horizons of the review-leads ticket A for these sources. (c), (e):
   12 rounds or 5,000 knots. As recorded, a round that would take the structure above the cap is not taken. No
   wall-clock limit inside any script.
9. **Growth kind.** The recorded `growth_kind` reads any stall outcome as stalled. Under R a residual stall may come
   after rounds of births, so both that value and the kind from births per round (stalled only with no birth at all;
   bounded: births per round never above the largest of the first four rounds; growing otherwise) are reported.
10. **(c) "stall at once".** No birth in round 1. Counted two ways: residual stall at round 1; and the 13 starts with
    no loose distinction anywhere (no live knot), which make no birth under either rule. P2's "some ... still stall"
    is judged on residual stalls at round 1; "fewer than half" on every start of the 744 without a birth in round 1.
    Both counts are given, per law and convention.
11. **(c) enumeration.** Every draw has at most 8 knots, so all 1,024 per law are enumerated: every allowed choice at
    round 1 and, on each resulting structure, every allowed choice at round 2. The numbers of births per round
    across all choices, whether every choice stalls, and where the two conventions fall are reported.
12. **(d) set-ups and readings.** The smallest two-sided stall is `S_cycle_five` (five knots, 13 distinctions) and the
    smallest parity closing is `C_binary` (three knots, six distinctions, the ordinary implied two-parent birth), both
    from `WHOLE-STAGE-SETTINGS-20261120-001B/.../edits.py`, with its edits (setting 1 adds the optional loose
    distinction at the reader's holder) and its readings (`responses`: S, whether the reader's mark gains a second
    holder; C, Alice whether a zero-fresh birth takes her mark, Bob whether his optional distinction gains a holder).
    Weights on the start: uniform over the allowed words of the unedited start, the added distinction carried at zero
    under parity and fair under not-all-equal, each word splitting its mass equally among its extensions. Outcomes do
    not depend on values, so every cell is a point mass; denominators are reported. C is a parity closing, so P4 is
    judged with the parity law for C and with both laws for S; not-all-equal on C is reported beside it. Own-edit
    dependence of a side: its outcome differs between its two own settings at some far setting; far-edit dependence:
    it differs between the two far settings at some own setting. The four-correlation value (CHSH in the literature's
    name) is the recorded one: the largest of the eight sign choices with an odd number of minus signs, beside the
    signed E00 + E01 + E10 - E11. Under R the conventions and every allowed choice are all run. A supplementary row,
    not judged, runs `C_ternary` (six knots, 11 distinctions).
13. **(e) pace.** The 200 draws are the first 200 in the order of `p3_draws` (arm 0 to 3, draw 0 to 255) whose first
    round funds under ordinary growth (the same draws under both laws). One `random.Random(2026112330)` draws, in that
    order, the edited knot with `randrange(n)` over all knots of the start; the added loose distinction takes the next
    free name. Distance: steps in the start's sharing graph (two knots adjacent when they share a distinction) from the
    edited knot; a later knot takes the least distance of its founder ancestors (ancestry through parents). Births are
    matched as in the influence-cone study: an original knot r is (0, r), a birth is (1, sorted identities of its
    parents); a birth is unchanged when the other history has a birth of the same identity, the same number of fresh
    distinctions and (under R) the same payments (for each parent: loose, or the identities of the round-start holders
    of the shared distinction it paid), counted with multiplicity; the changed births are the multiset differences in
    both directions, each with its distance in its own history. Rounds after a cap in either history are not
    compared; after a stall or closing in one history every birth of the other is changed. Ordinary growth and R with
    both conventions, both laws. P5's bound is judged on pairs in which neither history has a residual stall in the
    compared rounds.
14. **(a) extension.** Covered: every round t to t+1 of every R history of tests (c) (both conventions and every
    enumerated choice), (d) and (e) whose stage t has at most 22 distinctions. Every assignment of stage t is
    enumerated and the allowed words kept; for each birth of round t+1 every assignment of its fresh distinctions is
    enumerated; a word extends when every birth has an assignment satisfying its law (fresh distinctions of different
    births are disjoint, so this is exact). Cross-check: full enumeration of stage t+1 where it has at most 24
    distinctions, with the projection of its allowed words onto stage t compared with the allowed words of stage t.
15. **Gate G.** Under ordinary growth the closings met are the parity closings of the 280 funded draws and the C
    set-ups at setting 00; the elimination test is compared with the shortcut (implied exactly when the birth is the
    round's only birth) on every birth of every ordinary history of the gate, not only at closings. "R reproduces
    ordinary growth" is checked as equal stars, knots per stage and outcome against `lib.grow`, and, round by round,
    equal groups, parents, demand and fresh counts against the recorded `end_operator.step` on the same end.

## B. Limits and findings during the runs

1. **The recorded group search is too slow for R's growth; an exact re-implementation is used.** Under R the starts
   that used to stall grow fast (a round of 1,553 births with 15 to 30 parents each was met by round 8), and the
   recorded pivot search (`end_operator._maximal_groups`) took minutes to hours on single rounds. `rlaw.Groups` computes
   the same groups in the same order by an exact route: knots with the same witnessed sets are interchangeable (true
   twins: every maximal group holds all or none of them); a knot in only one witnessed set is in no unheld group; the
   maximal unheld groups of the rest are found by a Bron-Kerbosch search with pivot on bit sets, pruned exactly as the
   recorded search is; uncovered pairs are counted per class. The search runs in C (`bk.c`, built into
   `artifacts/.../build/bk.so` on first use, deleted at the end, see PRUNED.md) above 64 candidate classes and in
   Python below; both are the same algorithm. Checks: every round of every history of tests (b), (c) and of the gate
   with at most 400 groups and 400 births is also run by the recorded code and compared (groups, maximal witnessed
   sets, lookahead demand, and with no short knot the whole round); the C and Python searches are compared on every
   end and lookahead of R (convention O) on all draws up to 400 candidate classes (gate part f). No difference was found.
2. **Next-round cap found by a count (exact for the cap; fresh counts of that last round are lower bounds).** When
   every birth of a round is live in the next round (fresh distinctions are loose), the lookahead's groups are exactly
   the next round's groups. If the lookahead search finds more maximal unheld groups than the room left under the
   5,000-knot cap, the recorded rule will not take the next round (`_proposals` raises its cap first), so the search
   stops there; the round is taken with fresh counts max(3 - p, 1) (or 0 if implied), flagged `fresh_lower_bound`, and
   the history ends with a cap (or at the horizon if it was round 12). With an implied birth the next end on the live
   births is counted instead. Births per round, holders, residual stalls, growth kind and the operator test (fresh
   distinctions are pendant in the knot-distinction pattern and cannot change its verdict) do not depend on these fresh
   counts; test (a) skips such rounds; test (e) does not compare from such a round on. In test (c) it ended 26 (O) and
   22 (N) of the 744 histories per law (24 and 21 caps, 2 and 1 at the horizon), with 35,267 and 28,080 births. Test (b)
   runs with the shortcut off (`bound_next=False`), so its last rounds are exact. Gate part f verifies the shortcut by a
   full lookahead (up to 200,000 maximal groups), exact fresh counts and the next end built from the holdings; see the
   draft for how many were verified and how many have lookaheads beyond 200,000 groups.
3. **A fault in my prefix helper, repaired, runs repeated.** `small_prefix` first returned nothing for a history whose
   every stage had at most 22 distinctions, so short histories (closings, early stalls) were missing from test (a).
   After the repair, tests (c) and (e) were rerun: their rows are identical to the first runs (4,096 and 1,200 rows,
   apart from the timing field), and only the stored prefixes changed.
4. **Test (b) was run twice.** The first R runs predate item 2; they were rerun with the final code and the shortcut
   off. Both sets are identical to the recorded driver.
5. **Gate part f, first form, ran out of memory.** Its first verification of item 2 recomputed the last lookahead with no
   limit and asked for a 16 GB buffer; it was replaced by the limited verification of item 2 before any value of it was
   used. The parity runs of arms 0 and 1 were split into chunks of 32, 8 and finally one draw to stay under ten
   minutes. Two single-draw runs (parity, arm 0 draw 50 and arm 1 draw 156) still exceeded ten minutes and wrote
   nothing; they are not verified under parity (their histories, identical under not-all-equal, were verified there).
   `tables.md` therefore counts 50 shortcut histories in gate f; with these two there are 52.
10. **Sole births under R.** On 1,018 rounds with no short knot (all under parity, all after a payment in round 1) the
    fresh counts differ from the recorded operator's: each is a round's only birth, which the recorded shortcut would
    close and the replaced closing test (elimination) does not find implied. This is the replaced test acting as
    frozen, not a fault; gate part c confirms elimination by enumeration on every parity birth of rounds 1 and 2 whose
    stage has at most 20 distinctions (5,635 births), and test (a) confirms that every such birth extends every word.
6. **Scouting.** To find the cost of R before the study runs, R (convention O) was run on the stalled draws with a
   per-history clock guard in /tmp; these were not study runs, gave no reported value and are deleted.
7. **Test (e) cannot meet P5's ordinary clause on this sample.** The 200 funded draws have 4 to 8 knots (96 have 4); the
   largest distance from the edited knot in any of their starts is 5, so no birth can be beyond distance 6. Reported
   as the prediction's failure ("no such draw exists"), with this reason.
8. **Test (a) on the enumerated choices** counts rounds, births and words; a round whose stage has more than 22
   distinctions is not covered (798,642 such rounds in the enumeration are not covered).
9. **Growth kinds.** The recorded function and the births-based kind agree on every R history here, because no residual
   stall came after round 1.
