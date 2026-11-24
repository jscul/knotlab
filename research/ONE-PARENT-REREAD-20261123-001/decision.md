# A law that re-reads where nothing is short: decision

Epic `ONE-PARENT-REREAD-20261123-001`, 2026-11-23, started at the close of `REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001`
under the owner's standing authorization (direction 1 of its report). One study, frozen after a cold review by the
advisor model and three lookups in existing records, implemented by a Claude Opus sub-agent and checked by the thread
with a separate engine. One exploratory probe by the thread. Every result is referee pending.
[Referee hand-off](referee_handoff.md)

Words used below. A hidden excess is a four-correlation score above 2 with both complete records unchanged by the far
setting, under supplied setting births and with every allowed word of the finished structure counted equally. A part is
a connected piece of one of the 292 structures with a hidden excess found by the third-holder epic's census.

## What was found

| Record | Verdict | Finding |
| --- | --- | --- |
| [Ticket A](../ONE-PARENT-REREAD-20261123-001A/result.md), rule Q: a one-parent birth also takes a distinction its parent shares | Supported; one prediction failed | With every newborn not-all-equal, eight parts with at most two holders go from exactly 2 to a hidden excess in one round (61/30, 31/15), only when the two births of one parent take different shared distinctions. With laws handed out, all 27 parts that one added knot lifts gain and no other part does. The rule damps growth and, oldest-first, builds one much-held distinction |
| [Probe](thread_checks/setting_as_reread_probe.py), both settings as births the rule makes | Exploratory null | In 161 of the recorded structures and 8,057 of their parts (those with at most 14 distinctions), 24,242 pairs of observers whose setting birth would be a rule-Q birth were scored; 19,665 are hidden and the largest hidden score is exactly 2 |

## What it says

**A stated law now grows a hidden excess with no law handed to any birth.** Under rule Q with every newborn
not-all-equal, the weight a part at exactly 2 lacks arrives in one round. This is the first time in the line that a
growth law, and no added knot, does it for a part with at most two holders.

**It hangs on a choice the rule leaves open.** The two births of one parent must take different shared distinctions.
Oldest-first and newest-first both give them the same one, and then nothing is gained. So the choice is a scaffold
that decides the result, as it was for rule R.

**It reaches only parts that already sit at 2.** Growth supplies no tie under this rule either. The 27 parts that gain
are the 27 that one added knot lifts; the other 24 at exactly 2 and the 5,710 below never pass their start.

**As a growth law it is a strong change.** Most sparse draws that grew without bound become bounded, the pattern of
holders fails the operator test far more often, and oldest-first makes one distinction held by a new knot every round,
a common hub in the foundation's word. Three of the seven recorded sources are untouched because they make no
one-parent birth.

**The settings are still supplied.** The probe found no structure on record in which both observers' setting births
could be births the rule makes and the excess stays hidden. That is a null on structures built for another purpose,
and no census.

**What is still supplied.** The parts, ties included; the observers and the setting births; the weighting; the choice
of which shared distinction a birth takes.

## Records

- Freeze commit `f3f5c9a1d1`. Advisor question and answer: `advisor/`.
- The thread's separate checks: `thread_checks/` (its own engine for rule Q, the comparison on the funded draws, the
  round-1 census on the 51 parts at exactly 2, and the exploratory probe).
- The tracker rows of this epic were written without a commit, like those of the three epics before it.

## Final report as sent

Sent to the owner on 2026-11-24 05:55 UTC.

The study I started at the last report is done. A stated growth law now grows a hidden excess with no law handed to any birth, from a part with at most two holders per distinction. It depends on one choice the law leaves open, and it reaches only parts that already sit at exactly 2. Referee pending.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — a law that re-reads where nothing is short | **Status:** Successful | With every newborn under one law, eight two-holder parts go from exactly 2 to a hidden excess in one round, and the law is classed on the draws and sources |
| Local direction — re-read births as a growth law | Practically exhausted | Two rules are classed; a re-read can supply the missing weight and cannot supply a tie |
| Broader exploration — a hidden excess with less supplied | Known alternatives | The setting births and the ties are still supplied; neither has been tested as a law |
| G18 Comparing growth laws | Capability gained | The first rival law that grows a hidden excess, with its cost to growth measured |

Rule Q: as ordinary growth, except that a one-parent birth takes, with its parent's loose distinction, one distinction its parent shares.

- **One law for every newborn is enough, in eight parts.** With every newborn not-all-equal, eight of the 27 parts that one added knot lifts gain a hidden excess at round 1: 61/30 in six and 31/15 in two. They keep it through round 3.
- **It hangs on which distinction each birth takes.** In every gaining part one knot makes two one-parent births. The gain needs them to take different shared distinctions. If both take the same one, the score stays at exactly 2, and both fixed conventions I ran (oldest-first, newest-first) give them the same one: 0 gains in 10,348 histories.
- **With laws handed out, all 27 parts gain.** One sibling not-all-equal and the other parity gives 109/54 or 55/27 under any choice. No part outside the 27 gains in either arm; for 1,377 parts that null rests on drawn law assignments.
- **Only parts already at 2 gain.** The other 24 parts at exactly 2 never pass 2, and the remaining 5,710 never pass 1.692. Growth supplies no tie under this rule either.
- **The rule changes growth strongly.** On the 280 funded sparse draws, 12 rounds:

| | Ordinary growth | Rule Q, oldest-first | Rule Q, newest-first |
| --- | ---: | ---: | ---: |
| Bounded / growing, not-all-equal | 51 / 229 | 257 / 23 | 264 / 16 |
| Largest number of holders of a distinction | 2 | 14 | 6 |
| Draws that fail the operator test | 33 | 114 | 116 |

- **Oldest-first builds one much-held distinction.** One distinction gains a holder every round along a chain of one-parent births. The foundation calls that a common hub.
- **Recorded sources.** Three of the seven make no one-parent birth and are unchanged. Two archived starts stop growing without bound.
- **One prediction failed.** Under parity, 8 draws (oldest-first) and 5 (newest-first) that stay alive under ordinary growth close under rule Q; 8 that close under ordinary growth stay alive.
- **Exploratory probe, outside the frozen design.** I asked whether both observers' setting births could themselves be births rule Q makes. On 161 recorded structures and 8,057 of their parts (those with at most 14 distinctions) I scored 24,242 such observer pairs; the largest hidden score is exactly 2. Those structures were built for another purpose, so this is a first look only.
- **Checks.** I wrote a separate engine for rule Q. It agrees with the study on all 280 funded draws under not-all-equal (about 3,300 rounds per convention), and on round 1 of all 51 parts at exactly 2 under every choice and law assignment. I also enumerated 40 later-stage gain tables word by word.

Still supplied: the parts, ties included; the observers and the setting births; the equal weighting of finished words; the choice of which shared distinction a birth takes.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Both settings as lawful births: the setting is which shared distinction a birth re-reads (B321) | 3/3 — Barrier | 2/3 — Testable | Run the third-holder census with one more class of side → a structure, or none at those sizes with the reason | Selected · awaiting go-ahead |
| 2 | Ties from growth: a birth after which two knots share two distinctions (B322) | 3/3 — Barrier | 1/3 — Idea | List such pairs in recorded histories under rule R and the rival laws → a birth rule that makes the tying pair, or none | Alternative · deferred |
| 3 | Check the ceiling and the counting argument against the literature and write up the four epics as one note | 2/3 — Substantial | 3/3 — Ready | Compare with the bounds for relaxed independence → known, or a note | Alternative · deferred |
| 4 | Independent referee of today's four studies of re-read births and the eight studies before them | 2/3 — Substantial | 3/3 — Ready | Replay from the hand-offs → confirmed, or a failing case | Alternative · deferred |

1. It would remove the supplied setting births, and rule Q gives the idea a home: which shared distinction a birth takes is a real open choice. The probe above and my mirrored pairs both came back empty, and there is a structural doubt: one observer's value is read by two not-all-equal knots, and a two-holder parity part hands a value on once. It waits for you for two reasons. It is a new objective, beyond the two directions you approved. And it reads an open choice of a law as an observer's setting, which sits against your picture that nothing chooses.
2. It would remove the largest supplied thing, the parts themselves. No birth rule on record makes the tying pair, so it is only an idea.
3. The line now has a clean statement across four epics (the ceiling, the smallest structure, weight and no tie, the re-read birth). Nobody here has checked the ceiling against the literature.
4. My checks are by the designer of the studies and are weaker than a fresh referee.

**STOP** on the question of the last two epics. The re-read move is stated as a law twice and classed, and what it can do is settled within these bounds: it supplies the weight a part at 2 lacks, and no tie. Another rule of this kind would meet the same limit. What could reopen it: a rule that fixes which distinction sibling births take, or a law whose births make ties.

**Corrections:** None new. The two from the last report stand.
**Goals:** Checkpoint row added; G18 gained a results line. No goal changed. B321 and B322 remain the open sub-goals.
**Assumptions:** A235 records rule Q; A236 records the open choice of which shared distinction a birth takes, on which the one-law result depends.
**Scaffolds:** The parts and their ties; the observers and setting births; the weighting; the choice of re-read distinction (two conventions and every round-1 choice were run, and the result differs between them); newborn laws in the mixed arm.
**Basket:** Direction 1 of the last report is taken and settled. B321 and B322 are open.

**Housekeeping.**
- Commits: `f3f5c9a1d1` (freeze), `787f22c804` (the epic, 92 files), `4fb5502e0e` (goals lines). Publication to knotlab succeeded.
- Not committed: the tracker rows of today's four epics on this line. The shared tracker files still hold other threads' pending rows; one integration commit remains your call.
- Sub-agent: Opus 5.5 at extra-high effort. Fable 5.2 reviewed the design before the freeze; its review moved the headline to one law for every newborn and sent me to three lookups that removed two foregone predictions.
- The decision note is `research/ONE-PARENT-REREAD-20261123-001/decision.md`.
