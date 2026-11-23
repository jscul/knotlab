# Deviations, readings taken and what was left out

Experiment `REVIEW-LEADS-20261123-001D-E001`. The preregistration (`research/REVIEW-LEADS-20261123-001D/preregistration.md`,
frozen at a078a4f959) is unedited. Every item below is a reading taken where it was silent, a narrowing forced by a gate,
or something not done. Nothing was tuned after outcome values were read except where an item says so.

## Left out

1. **Four of the five sources have no recorded tick inside the horizon.** Ordinary growth alone (`gate1.json`):
   the seven-knot source makes 8, 12, 19, 32, 56, 101, 185 births at steps 1 to 7 (413 cumulative at step 7); the
   nine-knot drawn source 15, 30, 63, 142, 338 (588 at step 5); the 21-knot structure 12, 24, 56, 143, 378 (613 at
   step 5). Their first recorded ticks are at parent steps 15, 17 and 31 (the 24-step clock 47), taken from
   `research/GENERATORS-20261120-001/source.md`, `research/READS-HOLDERS-SOURCES-20261120-001C/results.md` and
   `research/FREEDOM-CLOCKS-AND-BIRTHS-20261120-001/decision.md`. The horizon (400 births or 12 completed parent steps)
   ends before any of them. Gate G therefore fails for these four by horizon, not by a shared donor, and no joint start
   uses them. Only the scarcity clock (the eight-knot ring with one spare) has a recorded tick inside the horizon, at
   steps 6 and 10. All five joint starts join two copies of it.
2. **Outside spends are not branched.** Branching is at the shared donor. Births elsewhere that are not roles of a
   registered tick are never written before the ticks are classified, so a later outside birth that takes a donor's last
   distinction (the mechanism of `LAST-DISTINCTION-AND-PRIVATE-PULSES-20261121-001A`) is outside this study. At the
   starts used, every proposal enabled through the donor at the start is a plan proposal, so nothing is missed at the
   contested births themselves.
3. **No pair of the sources named in the preregistration other than the scarcity clock with itself.** See item 1.

## Gate G, as it came out (`gate1.json`, `gate2.json`)

4. **Gate 1 passes for ordinary growth and the guarded rule, and in part for the recompute rule.** The ring alone
   makes ticks at steps 6 and 10 under ordinary growth (births 70 and 151 at those cuts, equal to the scarcity receipt for
   the bare ring and both attachments), at births 56 and 128 under the guarded rule with the tick first inside its step,
   and under the recompute rule its first tick (a 20-birth completion found by search, replayed through the archived
   `apply` under both laws). The recompute rule does **not** reproduce a second tick alone: from the original ring the
   search is undecided at 20,000 states (a separate 600-second scratch search was also undecided); from the 63-knot stage
   it is exhausted at 193 states with no firing order among births that are roles of the tick. Under the `joins_first`
   pool the original ring's first tick is not reproduced alone either (exhausted at 745 states). Consequences, fixed in
   the addendum before any joint growth: the completion search is run for the first registered tick of each source only;
   a second tick receives only the loss test and is reported `open` when no certificate exists; `joins_first` results for
   a start with the original ring as a source show `open` where `unrestricted` shows `made`, and the loss counts are not
   affected.
5. **Gate 2 passes for all five starts at s = 0**: every role of each source's recorded history through the latest
   registered tick age is written at the same step as alone, the ticks are made at the recorded steps (S1: 6 and 10 for
   both sources; S2: 1 and 5; T1: X 6 and 10, Y 1 and 5; T2: X 1 and 5, Y 1; T3: as T1), the first three steps agree with
   the archived `literal_turn`, and the first tick of each source is found under the recompute rule. The joint fresh counts
   exceed the alone counts for many roles (the merged donor gives its children more demand), which never removes a tick.

## Construction readings

6. **Staggering.** Under ordinary growth every live knot pays all its loose distinctions in the one parent step after its
   birth, so two sources sharing one knot always ask it in the same parent step of the joint growth. A start whose first
   asks differ in the joint growth does not exist for a shared knot (stated, not tested). "Staggered" is therefore defined
   in the sources' own recorded histories: the donor's birth depth + 1 (step 1 for an original, 6 for the first parent
   of tick 6, 10 for the first parent of tick 10). The sources are placed in the joint start at those cuts (the original
   ring, the 63-knot stage, the 135-knot stage). All five starts ask the donor at joint step 1.
7. **Donors.** R0: ring knot 4 (the one opposite the marked original; two proposals, both needed for ticks 6 and 10).
   R0m: ring knot 0 (the marked original; two pair proposals and one unary, all needed). R5: knot 57, the first parent of
   tick 6 (three proposals: the tick, a pair needed for tick 10, and a triple needed for neither). R9: knot 126, the first
   parent of tick 10 (four proposals, one needed). The second parent of each tick was not tried.
8. **Shortfall.** s = 1 removes one loose distinction of the second source's part of the merged donor. The merged donor
   otherwise holds both supports in full.
9. **S1 changes a definition, both versions are reported.** Merging two original ring donors makes the merged knot a
   common witness of its neighbours on both sides, so four cross pairs become proposals and ordinary growth stalls at
   step 1 with shortages (knot, missing) (3, 2), (5, 2), (11, 2), (12, 2) (the unfunded merge; `construction_addendum.json`).
   S1 is run with exactly those shortages repaired by extra loose slots at the four neighbours, as the scarcity study's
   attachment does at a host's neighbours. Merging at a stage knot whose neighbours on one side are all spent creates no
   cross pair, so S2, T1, T2, T3 need no repair. This is the first missing construction for original-donor merges: the
   smallest example is two copies of the eight-knot ring joined at knots 4 and 4.
10. **Contested birth.** Primary reading: a birth is contested when the shared donor has more enabled multi-parent
    proposals than loose distinctions, and every such proposal is a branch (this contains the preregistered case, one loose
    distinction needed by two proposals, and does not let an index order assign the earlier slots). The literal reading,
    branching only when the donor has one loose distinction left and two or more proposals need it, with the proposals
    before that written in ascending order of their parent lists, was **added after the primary results were read**
    and is reported separately (`grow_strict_*.json`). It decides by labelling: the source whose knots have the lower numbers
    receives its slots first and the later source loses.
11. **Counting.** Choice sequences are counted exactly with equal states merged (T2: 5,040 sequences, 2,520 distinct
    leaves, the largest). No start exceeds 20,000 distinct leaves, so no sampling by seed 2026112304 was used.
12. **Outcome of a tick** at a leaf: `made` if a depth-first search (20,000 states) over births that are roles of its
    ancestry finds a firing completion or the birth is already written; `lost` if after a fair continuation at the donor
    (every enabled multi-parent proposal through it written in ascending order, then offered unary births) a required parent
    holds no loose distinction or a larger common child excludes a required pair; otherwise `open`. A stalled step is
    `stalled`, not `lost`.
13. **Certificate root cause.** After reading the guarded output of T3 at s = 1 the certificate selection in
    `lib.State.lost` was changed to report the root reason (a direct exhaustion, or the reason of the lost ancestor) first.
    Statuses are unchanged: the tally text of every `grow.py` run before and after the change is identical.
14. **Guarded rule.** A funded step is written one birth at a time with the births that are roles of a registered tick
    first; an unfunded step stalls as a whole and nothing after it is written. Second ticks of the original ring and
    of the stage that need more than 400 births are reported `not reached within the caps`; they are not counted as
    kept or lost.
15. **Laws.** The engine counts loose distinctions and neighbours and is the same for parity and not-all-equal. Both
    laws were checked on: every start's star projections (`certify_source`); the alone completions (archived `apply`);
    the contest trees and leaves of all five starts (parity and not-all-equal for the `unrestricted` pool, parity for
    `joins_first`). Leaves above 200 per run (S2: 360, T2: 2,520) were checked on a seeded sample of 200; the contest trees were
    compared in full.

## Disclosure

16. Before the addendum was written, one ordinary growth of the repaired S1-type merge was run in a scratch script
    outside the experiment folder (births per step 22, 36, 59, 101, 176, 320, 595 through step 7). No other joint start
    was grown and no serial rule was run on a joint start before the addendum was hashed (`construction_addendum.sha256`).
17. Advisor not consulted: the preregistration records its review; no new word was needed.
