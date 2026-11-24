# Can ordinary growth with both laws reach the structures with a hidden excess?: result

Ticket `REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B` (direction 2 of the third-holder epic; G18 with G17), 2026-11-23.
Computed, with one counting argument; scientific referee pending.
[Pre-registration](preregistration.md) · [full tables and commands](results_draft.md) ·
[deviations](../../experiments/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B-E001_reach/deviations.md)

**Ordinary growth changes how much each old word counts and never which old words are allowed. So it cannot make the
seven-knot structure from any part of it, and it does finish a structure with a hidden excess when the start already
has the structure's allowed words. Every start it finished that way holds a distinction with three holders, which
ordinary growth never makes.** A hidden excess is a four-correlation score above 2 with both complete records
unchanged by the far setting, under the supplied setting births and with every allowed word of the finished structure
counted equally.

## What was run

The 292 structures with a hidden excess found by the third-holder epic's census were the targets. For each, every
connected proper part that holds all six observer distinctions was a start (49,961 starts). Each start was grown by the
recorded ordinary operator for up to 3 rounds or until it passed 20 distinctions, with every assignment of a law to
every newborn (2.03 million tables with even parity or not-all-equal; 15.6 million with odd parity allowed too).

## The counting argument

A birth with a fresh distinction forbids no old word: whatever the values it takes, some value of the fresh
distinction completes it. A parity birth with f fresh distinctions gives every old word the same number of completions.
A not-all-equal birth gives 2^f completions when the distinctions it takes are not all equal and 2^f − 1 when they are.
So a birth changes the old words' counts only when it is not-all-equal and has two or more parents, and then by the
ratio 2^f : 2^f − 1 (2 to 1 with one fresh distinction). Computed beside it: the set of allowed observer words changed
in 0 of 17.6 million grown tables.

## What happened

**The seven-knot structure is not reached.** It has 19 starts. Each allows 24, 36 or 48 observer words against the
structure's 16, and growth keeps that set. Six of its seven knots hold no distinction of their own, and its two pairs of
parity knots that share two distinctions can only be founders, so no left-out knot can be born.

**Growth does finish other targets.** In 34 histories a start with no hidden excess gains one at round 1. The smallest:

- Start, 7 knots, 11 distinctions: Alice nae(x1,x2,s1), nae(x1,x3,s2), even(x2,h1,h2), odd(x3,h1,h2); Bob
  even(y1,y3,k), odd(y2,s2,k), odd(y3,s1,k). Hidden, score exactly 2. Bob's y1 and y2 are loose; k has three holders.
- Round 1 makes one birth on y1 and y2 with one fresh distinction. Not-all-equal, it gives **55/27**, hidden; even
  parity leaves the score at 2.

In 10 of the 34 the grown stage is an 8-knot target itself; 20 more targets are grown exactly from starts that already
had a hidden excess. The scores gained run from 2059/1029 to 55/27.

**Every one of the 34 starts has a distinction with three holders.** Among the 12,147 starts with at most two holders
per distinction, 74 already contain a structure with a hidden excess and none of the others gains one: 5,248 of them
grew, through 1.46 million tables (10.1 million with odd parity allowed), and the largest hidden score they reach is
exactly 2. Ten of those starts have the target's allowed words and score exactly 2, and stay there: the knot they lack
is nae(y3,k1,k2,k3), which takes three distinctions that already have two holders. That is a birth ordinary growth
does not make.

**An open search found nothing new.** Over every grown stage of at most 16 distinctions, with observers taken wherever
two exactly tied pairs exist that no knot joins (85,090 choices; 153,102 with odd parity allowed), four grown stages
give 20/9 and in each the start already did with the same observers. In the first two stages of the 280 funded sparse
draws of the review-leads epic no such observer choice exists at all.

## Predictions

| # | Verdict | Evidence |
| --- | --- | --- |
| G | Passed | 292 of 292 targets reproduce their recorded score, hidden; projected tables agree with word-by-word enumeration on 100 of 100 drawn stages; allowed observer words never shrink |
| P1 | Held | 19 starts of the seven-knot structure, none with its allowed words |
| P2 | Failed | Trivially, 630 starts already contain a structure with a hidden excess. In substance, 34 histories gain one by growth |
| P3 | Failed by inheritance only | 4 grown stages (6 with odd parity allowed) give 20/9, each already at its start |

**The thread's own check** (separate enumeration, sharing only the recorded scorer): the smallest start gives exactly
2 and its round-1 stage 55/27, both hidden; 254 of 254 new-excess tables on stages of at most 22 distinctions give the
recorded table and exact score; the 19 seven-knot starts and their word counts were rebuilt from the knot list; 400
drawn two-holder starts regrown with the review-leads epic's wrapper make the same births; the smallest tied-pair
structure gives 20/9 at its start and after the round. The count of holders in the 34 starts and the split of the
starts by holders are the thread's, made after the results were seen.

## What this is about

About the recorded ordinary operator on parts of the listed structures, for 3 rounds, with these supplied: the targets
and their observers; the setting births, which take distinctions that are already shared; the law of each newborn;
the equal weighting of finished words. Two more scaffolds bear on the 34 histories. The recorded operator accepts at
most two holders, so a start with a three-holder distinction was grown with every two of its holders meeting. And which
of a founder's loose distinctions a birth takes follows the recorded wrapper; in 7 of the 34 the table could see that
choice and other placements were not tried.

One statement of the pre-registration's "settled by construction" was false: a newborn's parity sign is a renaming of
its fresh distinction only until a later birth takes that distinction. The frozen two-law version was run as written
and a three-law version beside it; every verdict is the same.
[Correction](../../docs/CORRECTIONS.md)

**Verdict.** The wall is now stated in one line: ordinary growth supplies weight and no tie. A hidden excess needs
both. Every one of the 292 targets has two parity knots that share two distinctions, and such a pair can only be
founders. The starts that growth finished kept those pairs, held a distinction with three holders besides, and lacked
only the weight: one not-all-equal birth with two parents, which ordinary growth makes freely. What would let growth
make a tie is a birth that takes a shared distinction, the subject of this epic's other study.
