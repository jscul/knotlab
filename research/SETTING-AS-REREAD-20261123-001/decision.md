# Both setting births as births the rule makes: decision

Epic `SETTING-AS-REREAD-20261123-001`, 2026-11-23, sub-goal B321. Taken up after the owner's clarification of the same
day: "'Nothing chooses' means that there isn't a 'simulator', it's random. But random can have any combination of
settings and starting positions. So no, nothing chooses, but yes, any possible configuration is testable and
applicable." One structure built by hand by the thread, checked first by the thread's own code, then, after a cold
review by the advisor model and a freeze, by a Claude Opus sub-agent's independent implementation. Referee pending.
[Referee hand-off](referee_handoff.md)

Words used below. Rule Q: a one-parent birth takes its parent's loose distinction and one distinction the parent
shares. A hidden excess is a four-correlation score above 2 with both complete records unchanged by the far choice,
every allowed word of a finished structure counted equally.

## What was found

| Record | Verdict | Finding |
| --- | --- | --- |
| [Ticket A](../SETTING-AS-REREAD-20261123-001A/result.md), an 11-knot structure whose two setting births the rule makes itself | Supported | One round of rule Q makes exactly two births, one per observer. With the setting read as which shared distinction each birth takes: four times 144 allowed words, both complete records hidden, score exactly 20/9. Bob's choice changes the two shared distinctions' distribution by 1/3; with the old words' distribution held fixed every score is exactly 2. No smaller part with exactly two births works |

## What it says

**The setting births no longer have to be added by hand.** A stated law makes them, and the setting is which shared
distinction each birth takes, a choice the law leaves open. This answers sub-goal B321 by a construction.

**It adds a statement and no number.** The birth the rule makes is the same knot the earlier studies added, so the
score is the third-holder epic's and sits on its ceiling.

**The excess is the weighting's.** Counting every allowed word of each finished structure equally makes the shared
values' distribution depend on Bob's choice. Held fixed, it gives exactly 2. In the literature's terms this is
measurement dependence, within its known bounds. Under the owner's picture, in which nothing chooses and any complete
configuration can occur, that weighting counts every complete configuration once and assumes no setting that is
independent of the values; that is a reading, recorded as an assumption, and no result.

**The hand moved to the structure.** The 11 knots are wired by hand, ties included. Rule Q with not-all-equal newborns
cannot grow them. Where ties could come from is sub-goal B322.

**What is still supplied.** The structure; the equal weighting; the observers and their records; the reading of an
open choice as a setting.

## Corrections

One, not a block: the thread had held this direction back because it "sits against" the owner's picture that nothing
chooses. The owner's picture puts no limit on which configurations are tested. Logged in `docs/CORRECTIONS.md`.

## Records

- Freeze commit `1dc9c6a58c`. Advisor question and answer: `advisor/`.
- The thread's exploratory scripts, written before the freeze: `thread_checks/`.
- The tracker rows of this epic were written without a commit, like those of the four epics before it.
- The open question about the weighting is recorded as sub-goal B324 and assumption A240.

## Final report as sent

Sent to the owner on 2026-11-24 07:30 UTC.

The independent check is done and it replicated every number. Both setting births can be births a stated law makes: on the 11-knot structure, one round of the rule makes exactly those two births, and the excess is hidden at exactly 20/9. The check also confirmed that the whole excess comes from the weighting, which leaves one question that only you can answer (below).

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — both setting births as births the rule makes (B321) | **Status:** Successful | A structure exists, checked by an independent implementation; what the claim does and does not contain is measured |
| Local direction — the setting as the law's open choice | Practically exhausted | One construction answers it; the number is the earlier one |
| Broader exploration — a hidden excess with less supplied | Known alternatives | The structure and the weighting are still supplied |
| G18 Comparing growth laws | Capability gained | The setting births are now inside a law |

- **Replication.** Round 1 makes two one-parent births, one per observer, each with one fresh distinction. With each birth taking one of two shared distinctions, the four finished structures have 144 allowed words each, both complete records are hidden, and the score is exactly 20/9 over all outcome functions. The fresh value is not needed in the outcome.
- **Only two of the three options matter.** The third shared distinction of each parent is forced opposite to the loose one, so a birth that takes it re-weights nothing.
- **Hidden means the four-value records.** Bob's choice changes the distribution of the two distinctions the sides share by 1/3. Alice's choice changes nothing Bob's knots hold. The dependence runs one way.
- **The excess is the weighting's.** With the old words' distribution held fixed at any one choice, every score is exactly 2.
- **No knot can be left out** while round 1 makes exactly the two births. If a third one-parent birth is allowed, a 10-knot part gives 55/27.
- **The signs are not tuned.** 128 of the 512 sign assignments of the parity knots give the same 20/9: exactly those that keep each observer's two options unequal.
- **What it does not show.** The structure is wired by hand and the rule cannot grow it. The number is the one we already had.

**The question for you.** Every hidden excess in this line comes from counting every allowed word of each finished structure equally. There are two natural countings, and they give different answers:
- **Every complete configuration once.** Settings and values are random together. This gives 20/9, because the shared values' distribution then depends on a setting.
- **A random start that then grows.** The values are random first and each old word's weight is divided among its completions. This gives at most 2, by argument, on every structure.

Your "it's random, any combination of settings and starting positions" sounds like the first. If that is what you mean, the 20/9 is a statement about your picture. If you mean the second, the line's excess is a property of a counting we chose.

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Which counting "it's random" means, and whether a growth law fixes it (B324) | 3/3 — Barrier | 2/3 — Testable | Your reading of the two countings above; then look for a counting that follows from a law → your reading, or a law that fixes it | Selected · awaiting go-ahead |
| 2 | Ties from growth: a birth after which two knots share two distinctions (B322) | 3/3 — Barrier | 1/3 — Idea | List such pairs in recorded histories under the rival laws → a birth rule that makes the tying pair, or none | Alternative · deferred |
| 3 | Check the line against the literature and write the five epics up as one note | 2/3 — Substantial | 3/3 — Ready | Compare with the bounds for measurement dependence and for selection → known, or a note | Alternative · deferred |
| 4 | Independent referee of today's five studies of re-read births and the eight studies before them | 2/3 — Substantial | 3/3 — Ready | Replay from the hand-offs → confirmed, or a failing case | Alternative · deferred |

1. The whole excess rides on the counting, so this decides what the line means. It waits for you because the reading is yours; I have recorded both countings so the work can start from either.
2. It would remove the hand-wired structure. No birth rule on record makes the tying pair.
3. In the literature's terms the line is a local model with measurement dependence and selection. Nobody here has checked the exact forms against published bounds.
4. All checks so far are mine or a sub-agent's working from my design.

**STOP** on B321's question: a structure exists, so the setting births need not be added by hand. What could reopen it: a smaller structure built another way, or one a law grows.

**Corrections:** One, not a block, logged in `docs/CORRECTIONS.md`: I held this direction back because it "sits against" your picture that nothing chooses. Your picture puts no limit on which configurations are tested.
**Goals:** Checkpoint row added; G18 gained a results line. B321 is taken and settled; B324 is a new sub-goal for the counting question; B322 stays open. No goal changed.
**Assumptions:** A239 records the reading of a law's open choice as a setting, with your words. A240 records the equal weighting of finished words as a reading of your picture, open to challenge.
**Scaffolds:** The 11-knot structure and its ties; the weighting; the reading of an open choice as a setting; the complete record. The weighting was tested with the old words' distribution held fixed, and the excess does not survive that.
**Basket:** B321 taken and settled. B322 and B324 open.

**Housekeeping.**
- Commits: `1dc9c6a58c` (freeze, with my exploratory scripts and the correction), `40ffe64ea8` (the epic, 23 files), `91ef641a34` (goals lines). Publication to knotlab succeeded.
- Not committed: the tracker rows of today's five epics on this line. The shared tracker files still hold other threads' pending rows; one integration commit remains your call.
- Sub-agent: Opus 5.5 at extra-high effort, working without my check scripts until its own numbers were written. Fable 5.2 reviewed the claim before the freeze and supplied most of the caveats above.
- The decision note is `research/SETTING-AS-REREAD-20261123-001/decision.md`.
