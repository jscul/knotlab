# Re-read births and mixed laws: decision

Epic `REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001`, 2026-11-23, on the owner's go-ahead for directions 1 and 2 of
`THIRD-HOLDER-20261123-001`. Three studies, each frozen after a cold review by the advisor model, implemented by Claude
Opus sub-agents and checked by the thread with separate code. The third study is the arm the second one's
pre-registration left for after the first. Every result is referee pending. [Referee hand-off](referee_handoff.md)

Words used below. A hidden excess is a four-correlation score above 2 with both complete records unchanged by the far
setting, under supplied setting births and with every allowed word of the finished structure counted equally. A start
is a connected part of one of the 292 structures with a hidden excess found by the third-holder epic's census.

## What was found

| Record | Verdict | Finding |
| --- | --- | --- |
| [Ticket A](../REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001A/result.md), the re-reading move as a law | Supported; two predictions failed | Rule R: a knot that owes more loose distinctions than it holds pays the rest with shared ones. It forbids no old word, lets 629 to 646 of the 744 sparse draws that stall at once grow, and reaches four holders. It acts at round 1 only and never in a recorded source, because ordinary growth leaves no later knot short. It removes the two-sided stall's dependence on a far edit and leaves the parity closing's |
| [Ticket B](../REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001B/result.md), ordinary growth from parts, both laws | Supported; two predictions failed | Ordinary growth changes how much each old word counts and never which are allowed. The seven-knot structure is reached from none of its 19 parts. In 34 histories a part gains a hidden excess after one round; every such part holds a distinction with three holders. No part with at most two holders gains one |
| [Ticket C](../REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001C/result.md), the same census under rule R, and one added knot | Supported | Under rule R no two-holder part gains (partly a sample); seven three-holder parts gain through a birth that took a shared distinction. One added not-all-equal knot with a fresh distinction lifts 27 of the 51 two-holder parts that sit at exactly 2; every such knot takes one loose distinction and one to three shared ones, and neither rule makes any of them |

## What it says

**Growth supplies weight and no tie.** A birth with a fresh distinction forbids no old word, under ordinary growth and
under rule R alike. A not-all-equal birth with two or more inputs counts old words unequally, two to one with one fresh
distinction. A hidden excess needs both the right allowed words and the right weight. Every one of the 292 structures
has two parity knots that share two distinctions, and under ordinary growth such a pair can only be founders, so
ordinary growth makes none of them whole.

**The missing weight is one re-read birth.** A part that already has the allowed words and sits at exactly 2 gains a
hidden excess from one not-all-equal birth that takes a loose distinction together with a shared one. On loose
distinctions alone no birth does it for a two-holder part (0 of 2.05 million sets). The least such birth takes a
knot's loose distinction and one of that knot's shared distinctions.

**The law as first worded re-reads in the wrong places.** Rule R re-reads only when a knot is short. The parts it
repairs are far below 2 (largest hidden score 1.692), and the parts at 2 have no short knot. It did produce a hidden
excess by a lawful birth seven times, each from a part ordinary growth could not have made and under one of its two
conventions.

**Exploratory, outside the frozen designs.** On the ten parts seen before ticket C's freeze, a variant in which each
one-parent birth also takes one shared distinction of its parent lifts every one of them to 55/27 or 109/54 when
exactly one of the two sibling births is not-all-equal; with both parity nothing changes and with both not-all-equal
most stay at 2 ([script](thread_checks/one_parent_reread_exploratory.py)). None of the 292 structures has, on both
sides, the pattern that would make the setting birth itself such a birth (one knot holding the observer's loose
distinction and both of its shared ones); 15 have it on one side.

**What is still supplied.** The parts; the observers and the setting births; the weighting; the law given to each
newborn; rule R's choice of which shared distinction is paid.

## Corrections

One, not a block: the pre-registration of ticket B stated as settled that a newborn's parity sign is a renaming of its
fresh distinction. It is one only until a later birth takes that distinction. Both versions were run; every verdict is
the same. Logged in `docs/CORRECTIONS.md`.

## Records

- Freeze commits `43762c5b04` (tickets A and B) and `1cff0bbd6b` (ticket C). Advisor questions and answers: `advisor/`.
- The thread's separate checks: `thread_checks/` (enumeration of the reachability results, round 1 of rule R, extension
  under rule R, the added-knot census on a sample, the checks of ticket C, and the exploratory variant).
- The tracker rows of this epic were written without a commit, like those of the two epics before it.
