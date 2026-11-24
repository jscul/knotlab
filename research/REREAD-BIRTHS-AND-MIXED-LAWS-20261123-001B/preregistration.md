# Can ordinary growth with both laws reach the structures with a hidden excess?: pre-registration

Ticket `REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B` of epic `REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001` (direction 2 of `THIRD-HOLDER-20261123-001`; G18), 2026-11-23. Frozen before the study's code is written or run. Code by a Claude Opus sub-agent from this note; analysis and verdict by the thread. The canonical K1–K3 test is unchanged.

## The question

The smallest structure with a hidden excess has seven knots, mixes parity and not-all-equal knots and has no distinction held three times. Can ordinary growth, with a law given to each knot, make such a structure from a part of it, or make any structure that has a hidden excess once the setting birth is supplied?

## In standard terms

Whether a layered, solution-preserving growth process can produce a constraint network whose projected relation on six designated variables equals a given one; and a search of the grown networks for projected relations that admit a CHSH value above 2 under exact no-signalling with a supplied post-selecting constraint.

## Prior work in the program

`python3 -B scripts/track.py objects "ordinary growth reaching a prescribed structure from a proper founder subset" --until 2026-11-23 --exclude REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001`

`python3 -B scripts/track.py objects "reachability of a constraint network by a layered growth process" --until 2026-11-23 --exclude REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001`

`python3 -B scripts/track.py objects "structures with a hidden excess found by the census of the third-holder epic" --until 2026-11-23 --exclude REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001`

`BOND-CLOSURE-20261120-001` — a relative: which inputs make a parity closing implied; used here for the closing rule under re-reading.
`KNOT-RATION-GAME-20261121-001` — unrelated object.
`REVIEW-LEADS-20261123-001` — a relative: its audit showed that no ordinary event gives a knot a distinction or repairs a shortage, its ticket A read the operator test on the same sparse draws, and its both-laws ticket imposed two laws on every knot, which is not the mixing studied here.
`MEET-GROW-20261118-001` — unrelated object.
`THIRD-HOLDER-20261123-001` — the source of both studies: the move (a birth that takes a distinction already held twice) and the structures with a hidden excess whose reachability is asked here.
`SIBLING-ANNOUNCEMENTS-AND-RECEIVER-BIRTHS-20261121-001` — unrelated object.

Seen before this freeze: nothing under this rule or this census. The results of the third-holder study are known.

## Prior work outside the program

None found.

## Settled by construction (stated, not tested)

Under ordinary growth every allowed word extends, so the set of allowed words on distinctions that already exist never shrinks: growth cannot add an exact tie among existing distinctions, and can only change how many completions a word has (under not-all-equal births). A newborn takes one distinction from each parent, so two knots that share two distinctions were both founders. Every loose distinction is spent every round. A newborn has a fresh distinction, so its parity sign is a renaming of that distinction: a newborn's law is parity or not-all-equal, two choices.

## What is supplied

The targets; the founder sets; the law given to each newborn (every assignment enumerated); the setting births, which are supplied and take distinctions that may already be shared; the restriction of the open search to observers with an exactly tied pair. Each is a scaffold and is recorded as one at close.

## Definitions (frozen)

- **Targets.** The seven-knot structure of the third-holder study, the 9-knot structure written before its freeze, and every structure in that study's list of structures with a hidden excess, each with its six observer distinctions and its table of old allowed words.
- **Founder starts.** For a target, every connected proper subset of its knots that between them hold all six observer distinctions, with the target's laws and signs; a distinction whose other holder is left out is loose in the start. Subsets that are not connected, or lack an observer distinction, are counted and not grown.
- **Growth.** Ordinary growth by the recorded operator, structure as under not-all-equal whenever some knot is not-all-equal (no closing) and as under parity otherwise, for 3 rounds or until a stage passes 20 distinctions. Every assignment of parity or not-all-equal to the newborns is enumerated (at most 4,096 per history; beyond that, 4,096 drawn by seed 2026112340).
- **T1, reaching a target.** At each stage, the table of allowed words on the target's six observer distinctions after forgetting every other distinction: (i) has the same support as the target's; (ii) is proportional to it; (iii) gives a hidden excess when the supplied setting births are added.
- **T2, any grown stage.** For every stage of at most 16 distinctions met in T1, and for the first two stages of the 280 funded sparse draws of the review-leads epic's ticket A that fit that size under both laws and under every law assignment as above: every choice of Alice's x1, x2, x3 and Bob's y1, y2, y3 in which x2 and x3 are exactly tied (always equal or always unequal), y2 and y3 likewise, and no knot holds distinctions of both observers; the supplied setting births added; hidden excess or not.
- **Weighting, records, hidden, score.** As in the third-holder study.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| G | Checks of the code: each target taken whole gives its recorded score, hidden; the projected table of a stage agrees with brute-force enumeration on 100 drawn stages; support never shrinks along any history. | any fails |
| P1 | No proper founder start of the seven-knot structure reaches its table in support. | one does: it is reported in full with its law assignment |
| P2 | No proper founder start of any target gives a hidden excess at any stage. | one does |
| P3 | No grown stage examined in T2 gives a hidden excess. | one does: the smallest is reported in full |

## Runs and stop rule

One script builds the targets and founder starts, one grows and tests T1, one runs T2. The study stops when every target and every draw in the bounds is done. It reports the counts of founder starts grown and skipped, of stages and law assignments tested, and of observer choices in T2, and the reason each seven-knot founder start fails. Every run stays under ten minutes and under 12 GB; work is split into runs and nothing is stopped by the clock. Nothing is tuned after values are seen; a changed definition is reported with both versions. Deviations go in `deviations.md` in the experiment family. Results are referee pending.

**Advisor.** Claude Fable 5.2 reviewed both designs cold before this freeze (`research/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001/advisor/question.md`, `answer.json`). Its strongest objections here: the result was foregone as first designed: equality of holder patterns fails for trivial reasons, and 'the largest part reachable' is always all but one knot. Changes: reaching a target now means reaching its table of allowed words on the six observer distinctions after forgetting the rest, every newborn's law is enumerated as a declared scaffold, and an open search of grown stages (T2) was added. The advisor also asked for the same census under the re-reading law of ticket A; that is left for after ticket A, since it needs its engine.
