# Deviations, readings and limits (REVIEW-LEADS-20261123-001G-E001)

Nothing in the pre-registration's "Definitions (frozen)", "Predictions (frozen)" or "Runs and stop rule" was changed.
Everything below is a reading taken where the note could be read two ways, a resource limit, a shortcut that cannot change
a result (and is checked), or a sensitivity line reported beside the frozen reading. Source files read, none changed: ticket
A's `lib.py` (imported) and the reads-holders-sources study's `edits.py`, `survey.py`, `rates.py` (imported) and its
`edits.json`, `draws.jsonl`, `certificates.json`.

## Readings taken

1. **Q1 verdicts.** The recorded verdict of each of the 53 edits is `recurrence_including_residual_proof` at horizon 32 in
   `edits.json` (the frozen reader together with the later parent-map proof for the edits adding 1–2 and 1–3). It equals the
   horizon-16 value for every edit and law. Counts: yes 16, no 33, unknown 4 under each law (gate). The 33 "proved not"
   are as recorded: 16 loose deletions and three additions that stall, two additions with a repeating bounded roster
   (0–2, 0–3), three additions that close under parity and keep at most one cycle per part under not-all-equal (2–3,
   4–5, 4–6), six legal shared deletions, and three **illegal** shared deletions (0–1 twice, 1–4: knot 1 left with two
   places, below the study's three-place floor). Ticket A's engine does not test legality, so the illegal three are grown
   like every other start; they stay in the 33 as recorded and are flagged (`legal: false`). P2 is also reported without them.
2. **Q2 verdicts.** The recorded verdict of each draw is the event `underlying_indefinite_recurrence` of the study's own
   `rates.events` (any part proved positive: proved source; otherwise an unbounded part left open: unresolved; otherwise
   proved not). Counts 5 / 14 / 173 under each law and at both horizons. The note's "the rest not certified" is proved not
   plus unresolved (187).
3. **"Not proved sources"** (P3 and the fixed reading) = proved not + undecided (Q1) + unresolved (Q2).
4. **Horizon.** As in ticket A: a parent step whose births would take the structure above 5,000 knots is not taken (outcome
   `cap`).
5. **Knot identity between an edited start and the unedited source** (Q1, "uses only knots that the unedited source also has
   at that step"): by parentage. A founder is its index; a birth is its parent step, the identities of its parents, and its
   rank among the births of that step with the same parents in the engine's order. A birth whose parents include a knot with
   no counterpart, or a group the edit's meeting creates, has no counterpart. The unedited source is `original_supports`
   of `edits.json` grown under the same law, horizon and cap (another labelling of the distinctions of ticket A's
   seven-knot source; same history and first failing step, gate).
6. **"The first failing stage's forbidden sub-pattern"** = the one `networkx.check_planarity(..., counterexample=True)`
   returns on the stage's pattern after pendant nodes are pruned (its 2-core), the convention of ticket A's upper removal
   bound. The routine returns one sub-pattern among possibly several, so a routine-free reading is reported beside it:
   whether the inherited knots alone, with every distinction they hold, already fail. That holds exactly when some forbidden
   sub-pattern uses only inherited knots. Whether the returned sub-pattern contains the edit's own distinction
   (distinction 25 of the additions) is also recorded.
7. **Breaking birth.** From the last passing stage, the next step's births are added one at a time in the engine's order
   (the order of `lib.grow`'s `stars`) and the stage is tested after each. The code would switch to bisection above 300 births
   in that step (failing is monotone in the prefix, so the birth is the same). It never did: all 452 breaking steps had at most
   27 births. For each found birth the code checks that the prefix ending with it fails, the prefix before it passes, and the
   number of its distinctions shared with earlier knots equals its recorded number of parents.
8. **Both laws.** Q1: both laws grown separately for every start, and the histories compared. Q2: when the parity history has
   no step with exactly one birth and did not close, the engine's only law clause (`implied`) cannot act, so the not-all-equal
   history is the parity history. Its first three steps were grown directly under not-all-equal and compared, and all 181
   agreed. The 11 others were grown separately.
9. **Medians.** Medians of the values; for an even count, the mean of the middle two. A start with no failing stage within the
   horizon would be coded +infinity, but no funded start in either group passes, so the coding never acts.
10. **P3 and the fixed reading** are judged under each law separately. The two laws give identical numbers.
11. **Independent sources.** The note counts six (the 16 edits as one family, and five draws). Two of the five draws, draw 25
    with two and with three extra meetings, come from one tree (`results.md` of the earlier study: "One underlying tree
    contributes to both arms"). Counted by tree there are five. One draw (draw 60, two extra meetings) is the nine-knot drawn
    source ticket A read before the freeze.

## Limits applied (ten minutes, 12 GB)

- **Per-growth wall-clock limit of 240 s** (`lib.grow` `time_limit`, outcome `time`), fixed before any start of Q1 or Q2 was
  read. Each history it stopped keeps the stages before the stop. Under each law it stopped 32 histories: Q1-29 and Q1-30 (the
  edits adding 1–2 and 1–3) after 10 steps, and 30 Q2 draws after 4 to 10 steps. All 32 had already failed at step 1, and
  failing is monotone in the step, so the test's verdict within the horizon cannot change. Growth kind changes for two of them
  (next item). The step at which a growth stops on time depends on machine load (up to 20 runs ran at once), so a rerun can
  reach a different number of steps for these 32. Their first failing steps come before the stop and cannot change.
- **Growth kind with a short history.** Ticket A's `growth_kind` calls a history bounded when births never exceed the most of
  its first four steps, so any history with four or fewer steps is bounded. Three Q2 histories (all unresolved) stopped
  within four steps: Q2-x3-78 and Q2-x3-16 on time, Q2-x3-95 by the cap. Their births per step were 21, 32, 54, 141;
  26, 52, 103, 224; and 27, 60, 132, 374. The code calls them bounded and the frozen tables use that. A **sensitivity line
  added after these three were seen**, and used for no verdict, reads them as growing. All three fail, so P3 and the
  reading do not change (185 of 185).
- The forbidden sub-pattern had a 60 s limit; it was computed for the 34 Q1 first failures (at most 53 knots) and never neared it.
- Each run: one foreground process under `timeout 600 prlimit --as=12884901888`. The largest run took 240.3 s wall-clock and
  603 MB resident. The Q1 chunk with starts 28 to 41 reached its 250 s start deadline after start 29, and starts 30 to 41 ran
  as three further runs. No run hit `timeout` or the memory cap.

## Runs before the final code (seen, outputs deleted)

- A trial of `read_test.py` on Q1 starts 0 to 2 and Q2 start 0, with an earlier version that grew both laws separately for
  every start. Seen: first failing step 1 for Q1-00, Q1-02 and Q2-x2-00; Q1-01 stalls. Q2-x2-00 took 2 × 240 s. After this
  trial the Q2 not-all-equal history was shared under the engine's clause (item 8), to halve the run time. No definition,
  bar or limit was changed. The trial files were deleted, and the final runs regenerated these starts.

## Checks that are not gate clauses (all passed)

- Q1 regenerated by the study's `edit_population` and `Edit.applied`: 53 of 53 equal to `edits.json`. Q2 regenerated by its
  `survey.draw_specs` and the supply formula of `survey.source`: 192 of 192 equal to `draws.jsonl`. The five proved draws
  equal `certificates.json` holdings (5 of 5).
- `lib.grow`'s births per step equal the earlier study's recorded rosters wherever both exist. Q1 `trace` planned births:
  109 of 109 ages under parity, 115 of 115 under not-all-equal. Q2 per-age widths (one-part draws): 670 of 670 and 695 of 695.
- The gate sources were read with and without the Euler shortcut at the first failing stage and the stage before it: same
  verdicts.

## Not done

- Whether the returned forbidden sub-pattern, with its distinctions, is itself a sub-pattern of the unedited stage's own
  pattern (only knot identity was compared, as the note asks, plus the edit-distinction flag).
- The upper removal bound and loop rank at first failure (not asked by this note).
