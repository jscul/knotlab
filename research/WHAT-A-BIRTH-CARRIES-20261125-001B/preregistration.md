# What a newborn's holdings must depend on for a made pattern to read which pattern it meets: pre-registration of the second ticket

Ticket `WHAT-A-BIRTH-CARRIES-20261125-001B` of epic `WHAT-A-BIRTH-CARRIES-20261125-001` (sub-goal B331; goals G15 with
G18; assumptions A223, A241, A244, A245, A248).
- With [the claim](../WHAT-A-BIRTH-CARRIES-20261125-001/claim_b.md) and
  [the definitions](../WHAT-A-BIRTH-CARRIES-20261125-001/definitions_b.md) ("BD2").
- Data files with this text: `family.json`, `starts.json`, `renamings.json`, `gate_listing_b.txt`.
- The code will be written by a helper who has not seen the drafter's prototype.
- The canonical K1–K3 test is unchanged. No claim is made about living things, minds, physics or time.

## The question

Ticket A ([result](../WHAT-A-BIRTH-CARRIES-20261125-001A/results.md)) found one count handed through a start knot.
This ticket asks three things:
- whether two parts the growth made meet only through knots the growth made;
- whether one such knot is a knot both descend from;
- whether one part's course then depends on the other through it.

Each is asked under which of the listed laws, with what each adds by hand. The owner's premise stands: a law is not a
reader (A244).

## In standard terms

In the literature's words: in a synchronous hypergraph-rewriting system with label-free rules, do two components
reconnect only through hyperedges created after the start, one of them an ancestor of both? Does the continuation of
one then depend on the other's activity through that contact?

## Prior work in the program

Searches, run read-only on 25 November, each with `--until 2026-11-25 --exclude WHAT-A-BIRTH-CARRIES-20261125-001`:

`python3 -B scripts/track.py objects "a part's course depends on which second part it meets, not only whether it is there" --until 2026-11-25 --exclude WHAT-A-BIRTH-CARRIES-20261125-001`

`python3 -B scripts/track.py objects "parts that came apart meet again through a knot the growth made, an ancestral common knot made by births" --until 2026-11-25 --exclude WHAT-A-BIRTH-CARRIES-20261125-001`

`python3 -B scripts/track.py objects "a difference composed over several births, not one value at one birth" --until 2026-11-25 --exclude WHAT-A-BIRTH-CARRIES-20261125-001`

Top three rows:
1. `PARTS-MEET-AGAIN-20261124-001/2`, `PARTS-MEET-AGAIN-20261124-001/1`, `READ-ORIGIN-20261120-001/4`.
2. `PARTS-MEET-AGAIN-20261124-001/2`, `PARTS-MEET-AGAIN-20261124-001/1`, `RING-IN-BALANCE-20261123-001/7`.
3. `GUARD-CAP-AND-HOLD-20261124-001/1`, `QUIET-RETURNS-AND-SIGNAL-FRACTIONS-20261122-001/1`,
   `IDLE-PHASE-AND-TREE-CLOSURE-20261121-001/6` (relatives in words only).

Found by reading, in the fold study's results ([results](../PARTS-MEET-AGAIN-20261124-001A/results.md)):
- links through knots the growth made exist under choices by names (180 of 216 cases);
- its ancestral common knot is "always a start knot", and one the growth made "appears only under the control law"
  that looks for the other part.

So what would be new here is a made ancestral link under laws that use no names and do not look at parts.

The epics of the top three rows of each search: `PARTS-MEET-AGAIN-20261124-001`, `READ-ORIGIN-20261120-001`, `RING-IN-BALANCE-20261123-001`, `GUARD-CAP-AND-HOLD-20261124-001`, `QUIET-RETURNS-AND-SIGNAL-FRACTIONS-20261122-001`, `IDLE-PHASE-AND-TREE-CLOSURE-20261121-001`.

## Prior work outside the program (from memory, not checked)

A take of a unique candidate is the deterministic, label-free form of an embedding step in graph rewriting.

## Known before the runs (disclosed; the drafter's unreviewed prototype, not the study's engine)

1. **Recorded rations, takes of a sole candidate** (5 starts, 6 rounds, 800 knots, 270 runs, the prototype's first
   reading of a link):
   - MET-SOLE: 280 meeting pairs, 84 only through made knots;
   - STEPS1-SOLE and STEPS2-SOLE: no meeting;
   - named comparisons, MET(OLDEST) and STEPS-2(OLDEST): 668 meetings, none only through made knots.
2. **The same at the registered bounds and readings (BD2 5)** (a second scratch script): MET-SOLE with the 9 recorded
   rations and treatments, 8 starts, 7 rounds, 1,500 knots, both knot laws, 144 runs.
   - 640 meeting pairs. **312 met strictly through made knots, all under CANCEL-WAIT**: 216 under FLOOR1 on all 8
     starts, 96 under CAP-3 on the four ring starts.
   - Every one of the 312 is an ancestral common knot made by births in the FD 1.5 form; 32 are also in the
     every-member form.
   - None has a linking distinction held by a start knot.
   - No meeting had an empty RD 3.5 set.
   - **In none did the course from X only differ with Y barred.**
   - No knot failed. Max 77 s a run.
3. **New rules, takes of a sole candidate** (5 starts, 6 rounds, 510 runs): 18 pairs under MET-SOLE with a made link
   and a course difference, all on Ring(5, 3) under FLOOR1/CANCEL-OFFSHOOT with PARENT-OWING (both knot laws) or
   PARENT-OWING-1 (parity).
4. **The B1-dependence case and its controls** (the same scratch script): MET-SOLE, CANCEL-OFFSHOOT; Ring(5, 3),
   D2(5, 3), Ring(7, 3), Ring(5, 3)+1; 7 rounds; pairs after rounds 3 and 4, up to 4 per run.
   - **PARENT-OWING and PARENT-OWING-PLAIN, on all four starts, both knot laws:**
     - pairs of two-member parts meet at round 5, strictly through one knot made in round 2;
     - that knot is ancestral in both forms, and no start knot holds a linking distinction;
     - the bars give two classes, {none, either one member} against {both};
     - **the one-member runs have no meeting at all**;
     - at round 5, X's join has demand 7 against 6 (10 against 9 on Ring(5, 3)+1); the Y-side newborn in the extra
       demand group is Y's join of its two members, made only when both are usable;
     - no knot fails.
   - **PARENT-OWING-1**: the same under parity. Under not-all-equal there are 32 to 56 failing verdicts a run.
   - **OFFSHOOT-TWO, OFFSHOOT-THREE, PARENT-OWING-CAP3 and the mod-2 comparison**: no pair met only through made knots
     after rounds 3 and 4.
   - **PARENT-OWING-CAP4**: such pairs, with one class (no difference).
5. **At 8 rounds** (a third scratch script; Ring(5, 3), D2(5, 3), both knot laws):
   - the first differing used value is at round 5 and the course differs from round 6;
   - with the rest barred from round 6, the rosters from X only differ at rounds 7 and 8;
   - the guard × 10 and × 100 give the same, since the guard was never reached;
   - 100 renumbered runs of Ring(5, 3) gave identical per-round profiles, a coarse check.
   - The first draft's "two classes, so it cannot be composed" was a bad inference; it holds only because one entry
     induces P.
6. **Controls probed:**
   - J-EACH-PART (40 runs, 4 rounds): 404 pairs with meetings only through made knots; 374 with a course difference,
     354 of them with no failing knot.
   - No taking rule (40 runs): no meeting.
7. **Timings**, host load 18 to 27:
   - **the registered item** (a timing script; 154 items, 11 laws × 2 knot laws × 7 starts, with every pair, the bars
     and the lasting reruns, but no knot test in barred runs):
     - mean 4.5 s, median 0.15 s, max 80 s;
     - not-all-equal mean 6.5 s, 61% of it the knot test; parity mean 2.5 s;
     - items with bars: mean 15 s, max 80 s;
   - **one barred run's knot test** (not-all-equal, knots born after round 4, last round): 1.0 to 1.1 s on about 890
     knots;
   - **an exact whole-structure isomorphism test** of two 920-knot structures did not finish in 4 minutes;
   - **the invariant of BD2 7.3**: 0.04 s a structure.

## Settled by argument (not refereed)

The lemmas of the claim (b). FD argument 1 for the negative control.

## What is supplied

- every rule of BD2 2 and the controls;
- the starts, Ring(5, 3)+1 and the unsymmetric ring among them;
- s;
- the bars on Y;
- the readings;
- the bounds and the guard's numbers;
- the renamings.

## What a result would and would not show

It would show:
- whether, under a listed law that uses no names, two parts the growth made meet through a knot the growth made that
  both descend from;
- whether one part's course then depends on the other through it;
- the least listed laws for each.

It would not show a fold of emergence (A223: a pattern the rules make, whose making depends on another pattern, and
which makes a pattern of its own). Where one value at one birth separates the cases, the law handed a count over.

**Result sentences, for each outcome:**
- **Expected** (used only when attribution is accepted and m = 1). "Under FLOOR1 and CAP-3 with short knots waiting,
  and a take of a sole candidate (a rule added by hand), a law that uses no names, two like parts made by the growth
  meet only through one knot made in round 1 or 2 that both descend from. The start supplies the ancestors; the knot
  and both parts are made. There the course from X only does not change with Y barred. Under a different treatment
  (short knots make offshoots), no such link forms unless a second rule is added by hand, PARENT-OWING; with it the
  parts link and the course changes by one count: whether both of Y's two members are usable, so that Y's join is
  made, which is also whether the parts meet at all. That join adds one to the demand of X's join at the meeting
  round, then one to the owing whose offshoots receive it. Handed in one value, not composed. Verdicts and courses
  equal exactly on N renamings; 7 rounds; the listed laws only."
- **Differs, not attributed.** "The course changes with Y barred, but the first differing value holds no knot from Y
  only; no dependence through the meeting is claimed."
- **Link not found.** "Among n laws decided, none; m undecided. A241 stands as recorded: every knot both descend from
  is still a start knot, except under the fold study's control law."
- **Link found, dependence not.** As the first sentence of the expected outcome, then "and under no listed law did the
  course change with the other part barred".
- **A third class, or m ≥ 2.** Name the law, the start and the bars, and say it is the one result here worth designing
  on.

**The owner's sentences, for the expected outcome:**
1. "Two like parts the growth made, on four ring starts, come to share one knot the growth itself made in round 1
   or 2, which both descend from; no start knot links them, and the rule that does it, taking a distinction only when
   it is the only one, uses no names."
2. "Such links already form under the rations we had, in 312 pairs of the scratch runs, all with short knots waiting.
   There one part's course does not change with the other; for it to change we added one rule by hand, an offshoot
   receiving at least two fresh distinctions, and otherwise as many as its parent had joins asked of it."
3. (Used only when attribution is accepted and m = 1.) "What then passes is one count, whether both of the other
   part's two members are usable so that they join, which is also whether the parts meet at all: the law handed a
   count over at a meeting that a made knot links, no pattern read anything, and nothing was composed over several
   births."

## Runs

Six processes, four while the load is above 18.

**Order inside every run**: law (in `family.json` order), then start (in `starts.json` order, small first), then
parity before not-all-equal.

**One cap for the whole ticket: 70 minutes of wall time.** If a timing overruns, the run in progress is stopped at a
whole item. Everything not reached is reported "not run", never as a negative. Cuts are made from the end of this
order: the mod-2 comparison first, then the unsymmetric ring, then 1c, then P2, then 1b. If 1b or 1c is cut, "least
among the listed laws" reads "least among the laws run".

| # | Run | Items | Measured per item | Wall time on 6 processes |
| --- | --- | --- | --- | --- |
| G | the gate: ticket A's 648 runs against the fold engine; `gate_listing_b.txt` reproduced; ticket A's 4 attribution records | 650 | < 0.5 s (ticket A: 196 s on 4 processes) | < 4 min |
| C0 | negative (no taking rule) and positive (J-EACH-PART, 4 rounds) on 8 starts × 9 base laws × 2 knot laws; the planted case | 290 | ≤ 0.5 s | < 2 min |
| 1a | MET-SOLE, its 20 laws × 8 starts × 2 knot laws, with every pair, the bars, the lasting reruns, and the barred runs' knot test on pairs with a course difference (at most 8 pairs an item) | 320 | 4.5 s mean, 80 s max; ≈ 35 s more on about 16 items with cases | ≈ 6 min |
| P1 | the ration controls (4 rules × 4 ring starts × 3 treatments × 2 knot laws) | 96 | ≈ 10 s (47 s max seen) | ≈ 3 min |
| N2 | renamings (BD2 7.3) for the candidate laws of B4, the two fixed laws and any other law minimal after 1a, ≈ 6 laws × 2 knot laws; each pair with A = Y and A = ∅ only | ≈ 3,500 | ≈ 0.1 s (small starts) and 3 to 15 s (rings, with the barred runs) | 5 to 15 min |
| 1b | STEPS1-SOLE, its 20 laws × 8 × 2 | 320 | as 1a | ≈ 4 min |
| P2 | the guard × 10 and × 100, only on items the guard stopped at × 1 | ≤ 60 × 2 | ≈ 15 s (estimate) | ≈ 5 min |
| 1c | STEPS2-SOLE, its 20 laws × 8 × 2 | 320 | as 1a | ≈ 4 min |
| U1 | the unsymmetric ring under the two candidate laws of B4, both knot laws, with every pair, the bars and the knot test in full | 4 | not timed (a ring item with bars: 15 s mean, 80 s max) | ≈ 2 min |
| M2 | 2 + (o mod 2) on the 4 ring starts × 3 treatments × 2 knot laws | 24 | ≈ 5 s | < 1 min |

**Total about 34 to 46 minutes at the measured rates**, under the 70-minute cap, which leaves room for a doubling of
the knot test under load as at ticket A.

**Cut:**
- the 18 marked comparisons, except the mod-2 one;
- class C;
- the composed claim (a later ticket, with a two-by-two class and a planted composed case);
- sampled takes;
- Q-SOLE.

## Predictions

Legend:
- **(a)** seen in the drafter's prototype (a replication);
- **(b)** by argument;
- **(c)** reported, no prediction.

| # | Prediction | Fails when |
| --- | --- | --- |
| B0 (b) | Lemma N: no renamed run of N2 differs in its invariant or verdicts; the gate passes. | one differs |
| B1-link (a) | Under MET-SOLE with FLOOR1/CANCEL-WAIT, and with CAP-3/CANCEL-WAIT, pairs meet only through made knots on all 8 starts under FLOOR1, and on the four ring starts under CAP-3 (seen: 312 pairs, 7 rounds). | none does |
| B1-ancestral (a) | Under the same laws such meetings are ancestral in the FD 1.5 form. | none is |
| B1-dep, recorded (a, 8 starts and 7 rounds, MET-SOLE only) | Under the recorded rations with MET-SOLE no course from X only differs with Y barred across a meeting only through made knots. | one does |
| B1-dep, core (a) | Under MET-SOLE/FLOOR1/CANCEL-OFFSHOOT/PARENT-OWING, both knot laws, on Ring(5, 3), D2(5, 3) and Ring(7, 3): a pair with a made ancestral link whose course from X only differs with Y barred, every tested knot passing. | no such pair, or a knot fails |
| B1-dep, details (c) | The round (seen 6), the classes of the bars (seen two), attribution and m (never run), the Y-side knots, and lasting (seen at 8 rounds, not as registered). A third class does not fail any prediction. | — |
| P1 (a) | PARENT-OWING-PLAIN gives the core case. PARENT-OWING-1 gives it under parity, with failing knots under not-all-equal. OFFSHOOT-TWO, OFFSHOOT-THREE and CAP3 give no pair meeting only through made knots after rounds 3 and 4. CAP4 gives such pairs and no difference. | otherwise |
| Ring(5, 3)+1 (a) | A replication: the core case is seen there too (item 4). The start was chosen before the scratch run; the prediction was not. | no such pair, or a knot fails |
| The unsymmetric ring (c) | Reported with no prediction; no scratch run was made on it. | — |
| C0 (b and a) | Negative: no meeting (b). Positive: found by B1-link and B1-dependence (a). Planted: "through a start knot" (a). | otherwise |
| B4 (a for the link and for the difference; c for attribution, never run) | The candidate minimal laws among the listed: for B1-link and B1-ancestral, MET-SOLE with FLOOR1/CANCEL-WAIT; for B1-dependence, MET-SOLE with PARENT-OWING/CANCEL-OFFSHOOT, if attribution is accepted there. | another law is minimal |
| B5 (b) | Where the guard is not reached, P2's runs are identical by construction; P2 runs only where it stopped. | — |
| How many, Which at equal number, m (c) | Reported. On the seen case the one-member runs have no meeting, so "how many" is undefined there, and Which at equal number is empty. | — |

## Stop rule

Stop when every registered run within the cap is done and each of the three verdicts is decided for every law
reached, with the minimal laws among the listed laws reported as a set. Disagreements with the disclosed prototype are
replayed birth by birth. Deviations are recorded before the affected run.

## Words

Phrases of words in use, defined in BD2 0. "Reads" is not used for any pattern. "Meet again" and "gives parts off" are
not used. "In every numbering" is not said: "the law uses no names; checked on N renamings". "Least" always reads
"least among the listed laws". "First" always reads "first in the record".

## What the advisor's passes changed

Two passes ([the record](../WHAT-A-BIRTH-CARRIES-20261125-001/advisor_b/README.md)).

- **The first pass, on the first drafts**: "freeze after the listed changes". The made link became the whole ticket,
  split into three verdicts (the link, ancestral, the dependence), each with its own minimal laws; a difference
  composed over several births became a later ticket and is here only the m reading; the strict form of "only through
  made knots" was defined with its empty case; the ancestral reading was aligned with the fold study's; four checks of
  whether the link is the start's after all were registered; two bounded owing rations joined the search and two
  rules left it for the controls; the renaming lemma got its hypotheses; lasting was taken out of the headline as
  implied; one total cap and the order of items were registered.
- **Not applied as advised, with the evidence**: the registered dependence is "Whether" (Y usable against Y barred),
  not "How many", because in every scratch run that keeps one of Y's two members usable there is no meeting at all;
  whole structures under renamings are compared by an invariant, because an exact test did not finish in 4 minutes on
  920 knots; the start that breaks the ring's rotation is the ring with one knot holding four.
- **The last pass, on the revised texts**: "not yet; freeze once these are written in; all are wording". Written in
  by the thread: the knot test's premise for barred runs (fixed at birth only for a birth that received a fresh
  distinction) and the order and standing of the at most 8 tested pairs; what attribution accepts, and the outcome
  "differs, not attributed"; "meets against does not meet" where the barred run has no meeting; the laws and bars of
  the renaming run fixed before it; a node count for the symmetry search; the cut rule for "least"; six sentences
  that said more than the runs can; Ring(5, 3)+1 re-marked as a replication; and the unsymmetric ring added with no
  prediction and no scratch run. The advisor found none of its earlier advice wrongly rejected.
