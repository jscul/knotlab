# What the record holds on births that take a shared distinction: survey for PARTS-MEET-AGAIN-20261124-001

Written 2026-11-24 by a helper agent for the thread, before the study's freeze. Read-only survey of the repository at
HEAD `2c6a543b67`. Paths are relative to the repository root. "Line n" cites the file as it stands.
Every result cited below is **computed, scientific referee pending**, unless marked otherwise. Words: "shared" means
held by two or more knots, and the number of holders is given wherever it matters. The other thread's own word for the
move is "re-read"; it appears below only inside its record titles and quotations.

## 0. What the three laws are, in one line each

| Law | Source | Trigger | What is taken | Recorded as |
| --- | --- | --- | --- | --- |
| The A225 move | `research/THIRD-HOLDER-20261123-001B/preregistration.md` line 49 ("Class S") | none: a supplied setting birth | an observer's distinction that already has one or two holders; the birth gives it one more | assumption A225, a scaffold, "challenge: state it as a growth law" |
| Rule R | `research/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001A/preregistration.md` lines 45–47 | a live knot owes more than its loose distinctions | the short knot's own shared distinctions, one per unpaid birth | A230 (rule), A231 (conventions) |
| Rule Q | `research/ONE-PARENT-REREAD-20261123-001A/preregistration.md` lines 47–48 | every one-parent birth whose parent shares a distinction | one distinction its parent shares | A235 (rule), A236 (conventions) |

The A225 move is not a growth law. Rules R and Q are the record's two statements of it as a growth law. In both, the
distinction taken is a place of one of the birth's own parents. That one fact decides the main question of this study
(`the pre-registration`, "Settled by construction", arguments 1 to 3).

## 1. Rule R, exactly as run

**Wording** (`REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001A/preregistration.md` line 45): "Groups, demand and fresh counts
as in ordinary growth (the recorded operator on the present end). A live knot that owes more distinctions than it has
loose ones pays the rest with distinctions it shares, each of which gains a holder. A payment is never a distinction
that another parent of the same birth holds or pays. The round stalls only if some knot still cannot pay (a residual
stall)."

- **Trigger.** Shortness as in ordinary growth: a live knot in more groups than it holds loose distinctions.
- **Which births are paid with a shared distinction.** Births are made in the recorded order (groups of three or more,
  sorted; then pairs, sorted; then one-parent births); each parent hands out its loose distinctions in that order, "the
  last listed first", and once they are gone takes, for each further birth, a shared distinction (in that record's word,
  "pays")
  (`experiments/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001A/REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001A-E001_reread_law/deviations.md`,
  reading A1, lines 12–17; code `rlaw.py` lines 419–445). A short knot never makes a one-parent birth (it owes more
  than it holds), so all its paid births are joins.
- **Which shared distinction.** Convention O: the smallest name allowed (oldest); N: the largest (newest)
  (preregistration line 46; deviations A3, lines 24–26). "Shares" and "allowed" are read at the start of the round: a
  distinction with two or more holders then; not held then by another parent of the same birth; a different one for
  each of the knot's births in a round. Two different knots may pay the same shared distinction in one round
  (deviations A2, lines 18–23). On starts of at most 8 knots every allowed choice is enumerated for two rounds
  (preregistration line 46; deviations A11).
- **Fresh distinctions.** The ordinary count max(D, 3 − p, 1), with p parents; a paid input counts as one parent's input,
  so p is unchanged (preregistration line 47; `rlaw.py` lines 474–475).
- **The parity closing.** Replaced by elimination: "A parity birth receives no fresh distinction only when the parity of
  what it takes is implied by the old knots, tested by elimination" (preregistration line 47; deviations A6, lines 35–37:
  the GF(2) vector of what it takes lies in the row span of all knots of the stage before the round). The reason
  (preregistration, "Settled by construction", line 37): with a distinction held three times the sum of all knots no
  longer leaves the loose distinctions alone, so the shortcut "a sole birth that takes every loose distinction is implied"
  fails. Several births of one round may be implied.
- **Demand with three or more holders.** "Witnesses and demand under R are read from the full holdings: every knot
  holding a distinction that a birth holds witnesses that birth" (deviations A5, lines 30–34). In the lookahead every
  birth is provisionally live with one opening; every old knot holding a taken distinction witnesses the births that take
  it; births that take a common distinction witness each other (`rlaw.py` lines 480–494). No old knot persists into the
  lookahead, since under ordinary growth every loose distinction is spent each round.
- **Scope.** Run only with the ordinary count, the whole-round stall replaced by the payment and its residual stall.
  Never run with a ration (CAP-k, FLOOR0, FLOOR1, ONE-FEWER, RATION-k), a cancelling treatment, waiting, RELEASE/HOLD, or
  FILLERS: no file under `research/REREAD-BIRTHS-AND-MIXED-LAWS-*` or its experiments names any of them, and the ring
  study listed rule R only as "a candidate for a later swap" (`research/RING-IN-BALANCE-20261123-001A/preregistration.md`
  lines 58–59; `research/RING-IN-BALANCE-20261123-001C/preregistration.md` lines 58–59: "Not used here").

## 2. Rule Q, exactly as run

**Wording** (`ONE-PARENT-REREAD-20261123-001A/preregistration.md` line 47): "Groups, demand and stalls as in ordinary
growth, read from full holdings as in ticket A of the re-read epic. A one-parent birth takes its parent's loose
distinction and, when the parent shares a distinction at the start of the round, one such distinction, which gains a
holder; a parent that shares nothing gives an ordinary birth. A birth with i inputs gets max(D, 3 − i, 1) fresh
distinctions, where D is the lookahead demand computed from the holdings the round will leave, the new meetings of
re-reading births included."

- **Trigger.** Every one-parent birth whose parent holds, at the start of the round, a distinction with two or more
  holders. Joins never take one (deviations of the experiment
  `experiments/ONE-PARENT-REREAD-20261123-001A/ONE-PARENT-REREAD-20261123-001A-E001_one_parent_reread/deviations.md`,
  reading A3, lines 47–53). A shortage still stalls the whole round (reading A5, lines 62–66).
- **Which shared distinction.** O: the parent's smallest name; N: its largest. "Under a convention two births of one parent
  take the same distinction" (preregistration line 48; deviations A2, lines 40–46). In the census, every round-1 choice,
  each birth choosing independently (A14). Later rounds of a choice history use O (result line 92).
- **Fresh distinctions.** max(D, 3 − i, 1) with i the number of **inputs**, so a birth that takes a shared distinction
  gets max(D, 1) where an ordinary one-parent birth gets max(D, 2) (deviations A4, lines 54–61; `qlaw.py` lines 118–130).
  This is the single place where rule Q changes the count; it is why rule Q damps growth (result line 57).
- **Closing.** Under parity, elimination, as rule R (deviations A4).
- **Demand with three or more holders.** rlaw's lookahead: "the old holders of a re-read distinction witness the birth
  that took it (the new meetings)" (deviations A4; `qlaw.py` lines 20–24).
- **Scope.** Run with the ordinary count and STALL only. Never with a ration, a cancelling treatment, waiting, release or
  fillers (same search as for rule R).

## 3. The A225 move, exactly as run

- **Wording** (`THIRD-HOLDER-20261123-001B/preregistration.md` lines 48–49): "Class L. Each observer distinction has
  exactly one old holder, so the setting birth takes a loose distinction. Class S. An observer distinction may have one
  or two old holders; the setting birth gives it one more." The setting birth is a supplied not-all-equal knot on x1,
  x_{2+a} and one fresh distinction (`research/THIRD-HOLDER-20261123-001/advisor/question.md`).
- **Found** (`THIRD-HOLDER-20261123-001B/result.md` lines 8–11): with class S, seven knots of both knot laws, no old
  distinction held three times, give 19/9 with hidden settings; eight knots reach 20/9; none with six or fewer within the
  census; with class L nothing with at most three holders was found.
- **Not a growth law.** The birth is supplied, its parents are not defined, and nothing says when a birth takes a shared
  distinction. A225's own challenge: "State it as a growth law" (`scripts/track.py show A225`). Rules R and Q are the two
  answers on record. Its thread's note: "No recorded growth move gives a third holder to a value that is not already
  tied" (`research/THIRD-HOLDER-20261123-001/third_holder_moves.md` lines 48–50).

## 4. Meeting, met sets, groups and the knot test when a distinction has three or more holders

- **Meeting.** Two knots meet when they hold a common distinction, whatever its number of holders: in rlaw's present end a
  knot's witnessed set is every live knot that shares any distinction with it (`rlaw.py` lines 372–381;
  `qlaw.py` line 73 `shared_of`). So a distinction with m holders makes all m pairwise meet. This is the shared
  definitions' wording (`research/RING-IN-BALANCE-20261123-001/definitions.md` line 14) read for any number of holders.
- **Met set, common knot, joinable, groups.** Unchanged in form: the witnessed set of each knot (old or new), its
  inclusion-maximal versions, the recorded group rule (`rlaw.py` lines 139–150, an exact re-implementation of
  `end_operator._proposals`, checked against it on every round small enough: deviations B1). Neither study names parts of
  the live roster, components, or meeting again.
- **The knot test.** Neither rule-R nor rule-Q study ran the canonical K1–K3 test on the knots it grew. They ran:
  (a) extension, every allowed old word extends at every birth, by enumeration on stages of at most 22 distinctions
  (rule R: 0 of 18.7 billion words, `REREAD-...-001A/result.md` line 15; rule Q: 86.7 million, `ONE-PARENT-...-001A/result.md`
  line 72); and (b) the review-leads "operator test", planarity of the knot–distinction incidence graph, which "with three
  holders is a reading of the pattern only" (`REREAD-...-001A/result.md` lines 49–52; qlaw deviations A9). The two-holder
  engine's cut method (`engine.py` `parity_cut_test`) needs exactly two holders per shared distinction and was not used.
  The rank method of the shared definitions (rank H − rank H without the columns of a knot's places = 1) needs no such
  restriction and was not used either. The only K1–K3 run in this line is THIRD-HOLDER-A's, with `tools/knotlab` on each
  knot's own relation, every choice of contact place (`research/THIRD-HOLDER-20261123-001A/results_draft.md` line 22): a
  check of each knot's rule, not of the relation the whole structure induces on its places. Not-all-equal knots were
  never tested in the whole structure under either rule.

## 5. What was found, in the records' own numbers

### Rule R (`REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001A/result.md`; evidence: exact computation on named samples)

- Old words: none fails to extend (line 15).
- The seven recorded sources never have a short knot, so all 28 histories under R are the ordinary ones (line 19).
- Of 744 sparse draws that make no birth at round 1 under ordinary growth, 115 (O) and 98 (N) still make none; 588/605 (O)
  and 604/625 (N) are alive after 12 rounds (parity/not-all-equal); eighty stall under every allowed choice; most holders
  of a distinction 2/3/4 in 115/521/108 (O) and 98/549/97 (N) draws; never five (lines 22–34).
- **The rule acts at round 1 only** (lines 36–39): "Under ordinary growth a newborn is given as many fresh distinctions as
  the next round asks of it, so only a knot of the start can be short", with one exception over every allowed choice of
  two rounds (one draw, 3 of 192 choices, a short knot at round 2).
- The conventions give different births per round on 478 (parity) and 471 (not-all-equal) of 744 draws (line 41).
- After a payment, 482 (O) and 536 (N) sole births that take every loose distinction are not implied and go on; 17 and 21
  close (lines 45–47).
- Operator test fails at some stage for 582 of 629 (O) and 592 of 646 (N) growing starts (line 49).
- Two stalling set-ups: under R the two-sided stall's far-edit dependence goes; the parity closing's stays (P4 failed)
  (lines 54–59, 68–75).
- **"Re-reads in the wrong places"** (`REREAD-BIRTHS-AND-MIXED-LAWS-20261123-001/decision.md` lines 33–36): "Rule R
  re-reads only when a knot is short. The parts it repairs are far below 2 (largest hidden score 1.692), and the parts at
  2 have no short knot." Here a "part" is a connected piece of one of the 292 structures with a hidden excess, not a part
  of the live roster. Where it acts: knots of a start that owe more than they hold, at round 1. Where it never acts: any
  knot made by ordinary growth, and the 51 two-holder pieces that sit at exactly 2 (ticket C, `result.md` lines 30–34,
  58–60). It produced a hidden excess seven times, from three-holder pieces ordinary growth could not have made, the
  smallest under convention O only (ticket C lines 35–43).

### Rule Q (`ONE-PARENT-REREAD-20261123-001A/result.md`; evidence: exact computation, part of the mixed-arm null a sample)

- With every newborn not-all-equal, eight two-holder pieces go from exactly 2 to a hidden excess (61/30, 31/15) only when
  the two births of one parent take different shared distinctions; under either convention 0 of 10,348 histories gain
  (lines 29–31; table lines 24–27).
- On the 280 funded sparse draws, 12 rounds (table, lines 49–55): bounded/growing under not-all-equal 51/229 ordinary,
  257/23 (O), 264/16 (N); **largest number of holders of a distinction 2, 14, 6**; draws with a distinction held eight or
  more times 0, 239, 0; operator test fails 33, 114, 116; stalls after round 1: none.
- "Oldest-first builds one much-held distinction. A child's oldest shared distinction is the one its parent re-read, so
  along a chain of one-parent births one distinction gains a holder every round: a common hub, in the foundation's word.
  Newest-first stops at six holders, and no draw's largest number grows after round 3" (lines 59–61; settled by
  construction, preregistration line 39). "Bounded draws": "A re-reading birth gets one fresh distinction where an ordinary one-parent birth gets two, so most
  draws that grew without bound now make a bounded number of births each round" (lines 57–58).
- Parity closings move (P6 failed): 8 (O) and 5 (N) draws alive under ordinary growth close; 8 that close stay alive
  (lines 62–63, 80).
- Sources: three have no one-parent birth and are unchanged; the nine-knot source changes from round 2; two archived
  starts stop growing without bound (lines 64–66).

### Setting-as-re-read (`research/SETTING-AS-REREAD-20261123-001/decision.md` lines 14–38)

One round of rule Q on an 11-knot structure wired by hand makes exactly the two setting births; the setting is which
shared distinction each takes; 20/9, hidden; "Rule Q with not-all-equal newborns cannot grow them" (line 34). Nothing on
parts.

### Parts, components, meeting again

- None of the five other-thread studies mentions parts of the live roster, coming apart or meeting again.
- On this side of the record: under ordinary growth "the connected parts of the live roster neither come apart nor merge"
  (`research/GENERATORS-20261120-001/components.md` line 3, an argument by parentage; lesson 8.7 calls it proved). Under
  the added rules, "past the start the roster decides the round and parts act alone", "a new knot meets only its parents"
  (settled statements, `RING-IN-BALANCE-20261123-001A/preregistration.md` lines 93–99, an argument; true under the
  earlier laws only). Under ordinary growth two disjoint released packets "can meet directly only on the first step after
  simultaneous release" and, for a removed set of members that are not candidates of A, "every group containing an a ∈ A
  is unchanged ... its nonclosing fresh count agrees as well ... A whole-step stall, a change of the parity closing
  condition ... are different comparisons" (`research/GENERATORS-20261120-001/meeting.md` lines 5–17, argument). One
  shared distinction added by hand to a start lets two separate parts make a common birth later
  (`research/COPIES-AND-MEETINGS-20261120-001/start_edits.md` line 7: a prepared start, ordinary growth).
- The ring study's closing report: "Another thread's laws let a short knot pay with a shared distinction; under them parts
  could meet again, which these laws never allow" (`RING-IN-BALANCE-20261123-001/decision.md` line 105): a conjecture,
  never run.
- The global readers already in the record: STALL (any short knot stalls every part), and the parity closing exception,
  which reads every loose distinction of the structure ("One barred distinction anywhere switches the closing exception off
  everywhere", definitions lines 73–74). Under ordinary parity growth one extra loose distinction in one place can decide
  closing against growing in another (refereed, `publication/knotlab/INTUITIONS.md` lines 3710–3714, lesson 8.7); rule R keeps the closing's far-edit
  dependence (above).

## 6. Evidence class and referee status of what this study relies on

| Claim | Evidence class | Status |
| --- | --- | --- |
| Rule R's wording, conventions, elimination closing, lookahead (A230, A231) | frozen definitions; code read | scaffold; study referee pending |
| Rule R acts at round 1 only under ordinary growth | exact computation on 744 draws, every choice for two rounds | referee pending |
| Rule Q's wording, inputs-based fresh count, conventions (A235, A236) | frozen definitions; code read | scaffold; referee pending |
| Rule Q: 14 holders (O), 6 (N); bounded draws | exact computation on 280 draws | referee pending |
| The A225 move: 7-knot structure | exhaustive census for named classes | referee pending |
| Ordinary growth: parts never come apart or merge | argument by parentage | proved per lesson 8.7; GENERATORS refereed in part |
| Under the added rules parts act alone past the start | argument (settled statement) | not refereed |
| The ring that returns; the parts that copy themselves | exact computation, argument for every round | referee pending |

## 7. Did anyone run these rules with the rations and treatments of the ring and copying studies?

No. Rules R and Q ran only with the ordinary count (R with its residual stall in place of STALL; Q with STALL), on the
review-leads sparse draws, the seven recorded sources and pieces of the hidden-excess structures. The ring and copying
studies ran only the two-holder laws of the shared definitions; they name rule R as a later swap and never ran it. The
owner's belief is right.

## 8. Two consequences read off the record before any run (stated here, tested by the prototype and the drafts)

1. Under rule R with the ordinary count no later knot is short, so on the ring and the copier starts, which never stall
   at round 1, rule R with the ordinary count is ordinary growth. It acts there only as a treatment beside the rations
   (Part B item 1).
2. Both rules take a distinction that the birth's own parent holds. Every knot that holds it already meets that parent.
   So the new knot meets only knots that its parent meets. The pre-registration draft turns this into an argument with
   exact hypotheses (the seal argument).
