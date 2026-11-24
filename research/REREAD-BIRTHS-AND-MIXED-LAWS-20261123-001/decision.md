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
most stay at 2 ([script](thread_checks/one_parent_reread_exploratory_v2.py)). None of the 292 structures has, on both
sides, the pattern that would make the setting birth itself such a birth (one knot holding the observer's loose
distinction and both of its shared ones); 15 have it on one side.

**What is still supplied.** The parts; the observers and the setting births; the weighting; the law given to each
newborn; rule R's choice of which shared distinction is paid.

## Corrections

One, not a block: the pre-registration of ticket B stated as settled that a newborn's parity sign is a renaming of its
fresh distinction. It is one only until a later birth takes that distinction. Both versions were run; every verdict is
the same. Logged in `docs/CORRECTIONS.md`.

Second, not a block: the first exploratory script took a distinction of another knot as the parent's second shared
distinction in four of the ten parts. Redone with the parent's own, the sentence above stands as written; with both
births not-all-equal 34 of the 40 cases stay at 2, and the six that pass 2 (31/15 and 61/30, in three parts) are those
in which the two births take different distinctions. Logged in `docs/CORRECTIONS.md`.

## Records

- Freeze commits `43762c5b04` (tickets A and B) and `1cff0bbd6b` (ticket C). Advisor questions and answers: `advisor/`.
- The thread's separate checks: `thread_checks/` (enumeration of the reachability results, round 1 of rule R, extension
  under rule R, the added-knot census on a sample, the checks of ticket C, and the exploratory variant).
- The tracker rows of this epic were written without a commit, like those of the two epics before it.
- The untaken major directions are recorded as sub-goals B321 and B322. The successor study was frozen at `f3f5c9a1d1` (epic `ONE-PARENT-REREAD-20261123-001`).

## Final report as sent

Sent to the owner on 2026-11-24 05:10 UTC.

Directions 1 and 2 are both done, with one follow-up study that joins them. Growth can add weight to a structure but never a tie, and the one birth a hidden excess still needs is now identified exactly. The law I wrote for direction 1 turned out to re-read in the wrong places, so I have frozen and started a second law. All three studies are referee pending.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — re-read births, and both laws in growth | **Status:** Successful | Both questions are answered within their bounds, and the missing birth is pinned down |
| Local direction — rule R, a short knot pays with a shared distinction | Retire | It is lawful, but it acts only on a start and never on a part that sits at 2 |
| Broader exploration — laws that re-read | Known alternatives | A birth that re-reads where nothing is short lifts parts in an exploratory check; it is now under test as a law |
| G18 Comparing growth laws | Narrowed | Any law that keeps every old word supplies weight and no tie |

Two terms: a hidden excess is a four-correlation score above 2 with both complete records unchanged by the far setting. A part is a connected piece of one of the 292 structures with a hidden excess from the third-holder census.

- **Direction 2, ordinary growth with both laws: the seven-knot structure cannot be grown from any part of itself.** A birth with a fresh distinction forbids no old word, so growth changes how much each old word counts and never which are allowed (argument, and 0 changes in 17.6 million tables). Each of the structure's 19 parts allows 24 to 48 observer words against its 16.
- **Ordinary growth does finish other structures.** In 34 histories a part gains a hidden excess after one round. The smallest sits at exactly 2 with 7 knots and reaches 55/27 after one not-all-equal birth on two loose distinctions. Every one of those 34 parts already holds a distinction with three holders, which ordinary growth never makes. None of the 12,147 parts with at most two holders gains.
- **Direction 1, the re-read move as a law.** Rule R: a knot that owes more loose distinctions than it holds pays the rest with shared ones.
  - It forbids no old word (0 of 18.7 billion).
  - It lets 629 to 646 of the 744 sparse draws that stall at once grow, and gives distinctions a third and fourth holder, never a fifth.
  - It acts at round 1 only and never in the seven recorded sources, because ordinary growth leaves no later knot short.
  - Which shared distinction is paid matters: the two conventions I ran differ on 471 to 478 of the 744 draws.
- **The follow-up: rule R does not lift a two-holder part.** No two-holder part gains in 146,044 histories; the largest hidden score is 1.692. Part of that null rests on drawn choices and is a sample. The parts the rule repairs are far below 2, and the parts at 2 have no short knot.
- **Rule R did produce a hidden excess by a lawful birth, seven times.** All seven parts hold a distinction three times and sit at exactly 2. In the smallest (10 knots) a short knot pays with the distinction it shares with the other side, and the newborn lifts the score to 127/63. Made even parity, the same birth leaves 2.
- **The missing birth.** I tried every single added not-all-equal knot with a fresh distinction on the 12,073 two-holder parts with no hidden excess (31.4 million sets).
  - 27 parts gain, all among the 51 that sit at exactly 2.
  - Every knot that works takes one loose distinction and one to three shared ones.
  - None works on loose distinctions alone (0 of 2.05 million).
  - The least takes a knot's loose distinction and one of that same knot's shared distinctions.
  - Neither rule makes any of them.
- **Four predictions failed.**
  - Ordinary growth does lift some parts (the 34 above).
  - A search with observers placed elsewhere found four grown stages with a hidden excess, each already present in its start.
  - Under rule R the parity closing keeps its dependence on a far edit; only the stall's goes.
  - My pace test asked for a distance the sample does not contain.
- **Checks.** I verified each study with separate code: my own enumeration of words, my own round 1 of rule R on all 16,720 histories involved, and my own census of added knots on 425 parts. All agree. They share the recorded scorer and group rule with the studies.

Still supplied: the parts, which already contain the ties; the observers and the setting births; the equal weighting of finished words; the law given to each newborn; rule R's choice of which distinction to pay.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A law that re-reads where nothing is short: a one-parent birth also takes a distinction its parent shares | 3/3 — Barrier | 3/3 — Ready | Frozen at `f3f5c9a1d1`, with one law for every newborn as the headline → the law is classed on the sparse draws and the census of parts is done | Selected · started |
| 2 | Both settings as lawful births: the setting is which shared distinction a birth re-reads (B321) | 3/3 — Barrier | 2/3 — Testable | Run the third-holder census with one more class of side → a structure, or none at those sizes with the reason | Alternative · deferred |
| 3 | Ties from growth: a birth after which two knots share two distinctions (B322) | 3/3 — Barrier | 1/3 — Idea | List such pairs in recorded histories under rule R and the rival laws → a birth rule that makes the tying pair, or none | Alternative · deferred |
| 4 | Check the ceiling and the counting argument against the literature and write them up | 2/3 — Substantial | 3/3 — Ready | Compare with the bounds for relaxed independence → known, or a note | Alternative · deferred |
| 5 | Independent referee of these three studies and the eight before them | 2/3 — Substantial | 3/3 — Ready | Replay from the hand-offs → confirmed, or a failing case | Alternative · deferred |

1. It would be the first hidden excess grown by a stated law from a part with two holders. In an exploratory check all ten parts I tried reach 55/27 or 109/54 when one of two sibling births is not-all-equal and the other parity. With both not-all-equal only 6 of 40 cases pass 2, which is why the frozen headline is one law for every newborn. Main doubt: the recorded sources make one-parent births at round 1 only, so this law too may act on little beyond a start.
2. It would remove the supplied setting births. Of the 292 structures, 15 have the needed pattern on one side and none on both; pairs I made by mirroring those sides all change the far record.
3. It would remove the largest supplied thing, the parts themselves. No birth rule on record makes the tying pair, so this is only an idea.
4. The ceiling is of the kind the literature has for relaxed measurement independence. Nobody here has checked whether this exact form is published.
5. My checks are by the designer of the studies and are weaker than a fresh referee.

**GO** on direction 1. The last result says where the re-read must happen (where nothing is short) and what it must take (a loose distinction with a shared one of the same knot). If parts gain with one law for every newborn, a hidden excess is grown without handing any birth its law. If they gain only with mixed laws, that scaffold stays. The study stops when the law is classed on the draws and the census of parts is done.

**Corrections:** Two, both not a block, logged in `docs/CORRECTIONS.md`.
- My frozen design for direction 2 called a newborn's parity sign a renaming. It is one only until a later birth takes its fresh distinction. Both versions were run and every verdict is the same.
- My first exploratory script took a distinction of another knot in four of the ten parts. Redone, the statement I gave you stands; the count with both births not-all-equal is 34 of 40 at 2, not 30.

**Goals:** Checkpoint row added; G18 gained a results line. Two sub-goals recorded for the untaken major directions, B321 and B322. No goal changed.
**Assumptions:** A230 to A234 record the scaffolds: rule R; its choice of which distinction to pay; parts as starts with a law for each newborn; the reading of a start that holds a distinction three times; the single added knot.
**Scaffolds:** The parts and their ties; the observers and setting births; the weighting; newborn laws; rule R and its two conventions. None was tested under a different choice except the newborn laws (two against three) and the convention (two, and every choice on small cases).
**Basket:** Directions 1 and 2 of the third-holder epic are taken and settled. B232 (several laws present at once) is marked taken; B321 and B322 are new.

**Housekeeping.**
- Commits: `43762c5b04` and `1cff0bbd6b` (freezes), `c627e42317` (the epic, 527 files), `46a4c74a9f` (goals lines and the first correction), `f3f5c9a1d1` (freeze of the new study). Publication to knotlab succeeded for the epic.
- Not committed: this epic's tracker rows (A230 to A234, B321, B322, three objects rows), like those of the two epics before it. The shared tracker files still hold other threads' pending rows; one integration commit remains your call.
- Sub-agents: Opus 5.5 at extra-high effort for all three studies and for the new one. Fable 5.2 reviewed each design before its freeze.
- The decision note is `research/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001/decision.md`.
