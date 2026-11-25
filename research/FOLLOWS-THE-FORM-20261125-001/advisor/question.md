# Review before a freeze: does what a part makes follow the form of what it is attached to?

You are reviewing the design of a small registered study before it is frozen. Be a hard referee. I want to know what
is wrong or missing, not encouragement.

Context in one paragraph. The program grows structures of "knots" (rules over distinctions; think hyperedges over
variables) in complete rounds under a fixed, deterministic law: each round every live knot gives its unshared
("loose") distinctions to births (joins of knots that meet, and offshoots), and each birth receives some fresh
distinctions by a count rule (a "ration"); some laws add a "taking rule" by which a birth also takes one shared
distinction from a nearby knot. Earlier studies asked whether one made pattern's course depends on another pattern it
meets, and found only "a count handed over" or "whether the other is there"; they varied presence (by barring the
second pattern), never its form. A probe by the drafter then built starts from a first seed, one link distinction
and a second seed, held the first seed and the link's place fixed, swapped the second seed through families of
forms, and read what the first seed's own descent makes (its births round by round). It found many classes, later
separation, and different fates (the first seed's line ends, idles or grows). The study below registers that: exact
replication of what the probe saw by an independently written program, and predictions on first seeds and second
seeds nothing has grown.

What I ask of you:
1. Verdict: "Freeze", "Freeze after the listed changes", or "Not yet", with a numbered list of required changes.
2. Is the central claim worded within what the design can show? In particular "follows the form", "by more than what
   happens at the first contact" (C2) and "through knots the growth made".
3. Confounds I have missed. For example: is C2's inference from "start knots act in round 1 only" to "the later
   difference reached the first seed's descent through made knots" sound? Could the late separations be nothing but
   a round-1 difference taking time to show in the reading? Does that matter for the claim as worded?
4. Are the predictions falsifiable and their thresholds sensible, given what was seen? Any that cannot fail, or that
   can fail for an uninteresting reason?
5. Controls: what negative or positive control is missing? Is the reading FF 5 fully specified for an independent
   implementer? Any ambiguity in FF 2, FF 6 or FF 9?
6. Anything in the wording that claims more than the evidence class (computed, bounded, built starts).

Keep the answer under about 900 words. The three texts follow in full.

---


# TEXT 1: the claim

# Claim: on built starts, what a part makes follows the form of what it is attached to

Epic `FOLLOWS-THE-FORM-20261125-001`, ticket A. Frozen with [the definitions](definitions.md) and
[the pre-registration](../FOLLOWS-THE-FORM-20261125-001A/preregistration.md). Evidence class sought: computed,
bounded, by a program written from these texts; referee pending.

## The setting

A start is built from a **first seed**, one **link** distinction and a **second seed** (FF 2). The first seed and the
knot of it that holds the link are held fixed while the second seed runs over a family of forms. The start is grown
under one law, and **what the first seed's own descent makes** is read (FF 4, FF 5): its births round by round.

## The claim

- **C1. It follows the form.** With the first seed and the place of the link fixed, what the first seed's descent
  makes differs between second seeds of different form: in every study of the fresh material the forms fall into two
  or more classes, and in at least nine studies in ten into three or more.
- **C2. By more than what happens at the first contact.** Under the laws where a start knot is a member of the
  roster in round 1 only (short knots retiring or making offshoots), some pairs of forms are first told apart in
  round 2 or later. Those differences reached the first seed's descent through knots the growth made.
- **C3. It differs in kind.** Across second seeds, the first seed's own line ends, holds steady or grows.
- **C4. It does not read the whole form.** With no taking rule it tells apart two chains that differ two or more
  steps from the link knot in at most one pair in ten. With the take of a sole candidate it tells a chain of four
  knots from one of five in at least 15 pairs in a hundred, under the ordinary count and under the cap of three with
  short knots waiting.

Each part is registered as predictions with a "Fails when" entry in the pre-registration, some on material the
drafter's probe ran (replications, to be reproduced exactly) and some on first seeds and second seeds nothing has
grown (the fresh material).

## What is supplied

Everything but the growth: the starts, built by hand (assumption A258); the choice of first seeds, of the place of the
link and of the families of second seeds; the laws, among them the take of a sole candidate, a rule added by hand
(A255); the reading; the bounds. **The meeting of the two seeds is supplied**: they share a start distinction.

## What the claim is not

- Not a claim about two parts the growth made that meet through a knot the growth made. That is the fold of emergence
  the owner asks for (A223), and it stays open.
- Not a claim that a pattern reads anything in a fuller sense, or that the first part makes use of what it follows.
- No weighting is named, so nothing is called typical, rare or likely. The fresh family is a seeded sample of a
  written list, each form once.
- Nothing about living things, minds, physics or time.

---

# TEXT 2: the definitions

# Definitions (FF)

Epic `FOLLOWS-THE-FORM-20261125-001`. Frozen with [the claim](claim.md) and
[the pre-registration](../FOLLOWS-THE-FORM-20261125-001A/preregistration.md). Items are cited as FF n.

## FF 0. Words

Glossary words (distinction, knot, loose, shared, roster, round, birth, join, offshoot, part) are used as in the
guide's glossary and in the definitions of `WHAT-A-BIRTH-CARRIES-20261125-001` (its `definitions_b.md`, "BD2"), which
this study takes over for the growth. A **seed** is a small set of knots written out by hand. A **chain** is a seed
whose knots are in a row, each sharing one distinction with the next. A **ring** is a chain whose last knot also
shares one distinction with its first. Names such as `path`, `star3` and `ring` in the data file are labels only;
`star3` is a knot that shares one distinction with each of three others.

## FF 1. The growth

- The growth is BD2's, with no change: complete rounds, release, the rations FLOOR1 ("just enough for three places"),
  CAP-3 (the cap of three) and ORD (the ordinary count); short knots treated by CANCEL-RETIRE, CANCEL-OFFSHOOT or
  CANCEL-WAIT; the taking rule either none or the take of a sole candidate (BD2 2.1, MET-SOLE); the knot law
  not-all-equal or parity. A **law** here is (ration, treatment, take); with the knot law there are 18 laws under each
  knot law.
- **The engine of record** for the growth is ticket B's (`eng.py` of
  `experiments/WHAT-A-BIRTH-CARRIES-20261125-001B/...`), unchanged and read-only.
- **Bounds.** A run is grown for R_max rounds: 9, or 10 for the chains (FF 3). It stops after the first round that
  leaves more than 3,000 knots; that round is read. The engine's guard limits are ticket B's; a round the guard stops
  is not read. A run is **read through** the last round it completed.

## FF 2. Seeds and starts

- A seed is a list of knots, each a list of the seed's own distinction names 0, 1, 2, ... A first seed names one of
  its knots, the **site**; a second seed names one of its knots, **at**.
- **The start** of a first seed F and a second seed S: F's knots first, with F's own names; then one new name, the
  **link**, equal to the number of F's names; then S's knots, each of S's names raised by the number of F's names
  plus one. The link is appended to the place list of F's site knot and of S's `at` knot.
- **The bare start** of F is F alone with the link appended to its site knot, where it is a loose distinction.
- Every knot of every start has three or more places. The seeds are in `seeds.json`, as explicit knots.
- Three starts written out, for checking (first seeds and second seeds by their names in `seeds.json`):
  - B with `one:2`: `[[0, 1, 2, 6], [0, 3, 4, 5], [7, 8, 6]]`
  - D with `two:1,2`: `[[0, 2, 3, 8], [0, 1, 4], [1, 5, 6, 7], [9, 10, 8], [9, 11, 12]]`
  - the bare start of A: `[[0, 1, 2, 3]]`

## FF 3. Families

Four families of second seeds, in `seeds.json`: `mixed` (50), `chains` (62: every chain of one to five knots with 2 or
3 loose distinctions a knot, held at its first knot), `second` (37) and `fresh` (60). The first three were grown by
the drafter's probe. `fresh` is a sample of 60, drawn with Python's `random.Random(20261125).sample`, of a written
list of 207 forms: every chain of one to four knots held at any knot, every knot with three partners held at that
knot or at a partner, and every ring of three or four knots, with 0 to 3 loose distinctions a knot, every knot of
three or more places, one for each class under the seed's own renamings that keep the held knot, and none equal to a
form of the other three families. Fifteen first seeds, A to O: A to E and F to J were grown by the probe; K to O were
not.

## FF 4. Descent

A start knot of the first seed is **of the first**; a start knot of the second seed is **of the second**. A knot made
by a birth is of the first if a parent is, and of the second if a parent is; it may be both. **The first seed's own
descent** is the knots that are of the first and not of the second. A distinction taken by a birth does not change
its descent.

## FF 5. What it makes

For a run read through round R, and each round t from 1 to R: the multiset, over the births of round t that are in
the first seed's own descent, of the entries

    (kind, number of parents, number of places, f, number of takes)

where kind is join or offshoot, the number of places is the length of the newborn's place list once its fresh
distinctions are added, f is the number of fresh distinctions it received, and the number of takes is the number of
distinctions it took. **What the first seed's descent makes through round R** is the sequence of these multisets for
t = 1, ..., R. Nothing in it is a name.

## FF 6. Studies, classes, told apart

- A **study** is one knot law, one law, one first seed and one family: its runs are the bare start and one start for
  each second seed of the family.
- **R\*** of a study is the last round that every one of its runs was read through.
- Two runs of a study are in one **class** when what the first seed's descent makes through R\* is the same in both.
  The **classes among the forms** leave the bare start out.
- Two second seeds are **told apart** when they are in different classes.
- **First told apart.** For two second seeds a and b of a study, let r be the smaller of the rounds their runs were
  read through, and L the last round any run of the study was read through. If what the first seed's descent makes
  differs through some round up to r, they are *first told apart in* the least such round. Otherwise, if r = L,
  *never*; otherwise *not read further*.

## FF 7. Fate

For a run read through four or more rounds, let x be the numbers of births in the first seed's own descent in the
last three rounds read. The first seed's line **ends** if all three are 0; else is **steady** if all three are equal;
else **grows** if they strictly increase; else **shrinks** if they strictly decrease; else **other**. A run read
through fewer than four rounds is **not read**.

## FF 8. Start knots in the roster

A knot is a **member** of round t's roster when it holds a usable loose distinction at the start of round t (held by
it alone and not barred). A start knot **acts in round 1 only** in a run when it is a member of no roster after
round 1.

## FF 9. Depth, on the chains

In a study of the family `chains`: a **pair at depth i** is two chains of one length whose loose counts are the same
except at the knot i steps from the held knot, where one has 2 and the other 3. A **pair of lengths n and n + 1** is a
chain of n knots and the chain of n + 1 knots that begins with it. For one law, pairs are pooled over the first seeds
of the run; a pair is told apart as in FF 6, within its own study.

## FF 10. Renumbering

A renumbering of a start permutes its distinction names, shuffles the place list of every knot and shuffles the order
of its knots, keeping note of which knots are the first seed's. What the first seed's descent makes must not change.

## FF 11. Supplied by hand (scaffolds)

The built starts and the choice of seeds, sites and families (A258); the take of a sole candidate (A255); the bounds
of FF 1; the reading of FF 5; the thresholds in the predictions. Swapped within the study: the first seed (fifteen),
the family (four), the ration, the treatment of short knots, the taking rule (none or one), the knot law.

---

# TEXT 3: the pre-registration

# Pre-registration: the place held fixed, the form changed

Ticket `FOLLOWS-THE-FORM-20261125-001A` (sub-goal B335; assumptions A223, A244, A255 and A258; goals G15 with G18),
25 November 2026. Frozen with [the claim](../FOLLOWS-THE-FORM-20261125-001/claim.md),
[the definitions](../FOLLOWS-THE-FORM-20261125-001/definitions.md) (FF) and two data files: [the seeds](seeds.json)
and [what the drafter's probe saw](disclosed.json). The engine is to be written from these texts by a helper that has
not seen the drafter's probe programs.

## The question

On a start built from a first seed, one link distinction and a second seed, with the first seed and the place of the
link held fixed: does what the first seed's own descent makes differ with the form of the second seed? By more than
what happens at the first contact? In kind? How far into the second seed does it see?

## In standard terms

The sensitivity of one subsystem's trajectory to the structure of a neighbouring subsystem, in a deterministic
growing system of constraints (a growing hypergraph), with the coupling site held fixed. The literature's names, from
memory: information transfer between patterns; signalling in growth models; in cellular automata, one pattern
"reading" another.

## Prior work in the program

Searches, run read-only on 25 November, each with `--until 2026-11-25 --exclude FOLLOWS-THE-FORM-20261125-001`:

`python3 -B scripts/track.py objects "what the descent of one part of a built start makes depends on the form of the other part attached at a fixed place" --until 2026-11-25 --exclude FOLLOWS-THE-FORM-20261125-001`

`python3 -B scripts/track.py objects "a second seed substituted at a fixed link; classes of second seeds by what the first seed's own births are" --until 2026-11-25 --exclude FOLLOWS-THE-FORM-20261125-001`

`python3 -B scripts/track.py objects "how many knots deep into an attached chain a part's own births depend" --until 2026-11-25 --exclude FOLLOWS-THE-FORM-20261125-001`

Top three rows:
1. `PARTS-MEET-AGAIN-20261124-001`, `READ-ORIGIN-20261120-001`, `SETTING-AS-REREAD-20261123-001`.
2. `SIBLING-ANNOUNCEMENTS-AND-RECEIVER-BIRTHS-20261121-001`, `PARTS-MEET-AGAIN-20261124-001`, `PLUS-ONE-20261118-001`.
3. `SUBST-NEST-20261112-001`, `CAP-CHAINS-20261119-001`, `PARTS-MEET-AGAIN-20261124-001`.

What they hold for this question:
- `PARTS-MEET-AGAIN-20261124-001`: one part's course differs with another part stopped, under laws that reach
  further; what crosses is whether the other part is there; "none depends on what the other part is". It varied
  presence, never form.
- `WHAT-A-BIRTH-CARRIES-20261125-001` (the direct predecessor, not in the top rows): the first pattern's first join
  receives two fresh distinctions and one more for each birth the second pattern makes that round; courses separate
  exactly where that count differs. Its second pattern varied only by which members a bar left usable. Its three
  probes of sub-goal B335 are the drafter's own; the third is what this study registers.
- `CAP-CHAINS-20261119-001` and `PLUS-ONE-20261118-001`: chains of offshoots under the cheapest parity growth. They
  describe what a chain grows into, not what a neighbour's descent makes of it.
- The other four are relatives in words only (marks on original knots; a structure for two setting births; a paid
  orientation in the learning line; substitution of blocks into knot patterns).

No record substitutes one form for another at a fixed place.

## Prior work outside the program (from memory, not checked)

Sensitivity to initial structure is the ordinary condition of deterministic growth systems, and nothing here is
claimed as new mathematics. What this adds is the measurement in this model: which features of an attached form a
part's own births depend on, under which laws, and how far in.

## Known before the runs (disclosed; the drafter's unreviewed probe, not the study's engine)

The probe is `research/WHAT-A-BIRTH-CARRIES-20261125-001/checks/form_at_a_fixed_place/`. It used ticket B's engine
and a reading the drafter wrote. Everything it saw is in `disclosed.json`, in this study's terms: for each of its
270 studies under not-all-equal (families `mixed` and `chains` with first seeds A to E, family `second` with first
seeds F to J; 18 laws each) R\* and the classes, and the tables of first told apart, of fates and of depth.

- Classes among the forms: 3 to 22 on `mixed`; 2 to 30 on `second`. The bare start is a class of its own in all 270.
- First told apart, pairs of forms on `mixed` (18,375 a row): with no taking rule, in round 1 for 9,837 to 10,962,
  in round 2 or later for 1,096 (retiring), 1,096 (offshoots) and 3,047 (waiting); with the take of a sole candidate
  726, 772 and 3,115 in round 2 or later.
- Start knots: under retiring and offshoots, a member in round 1 only, in 3,000 runs read to 6 rounds.
- Fates on `mixed`, no taking rule, ordinary count, retiring, 255 runs: 75 end, 67 steady, 113 grow.
- Depth on `chains` (first seeds A to E): with no taking rule, pairs at depth 2 or more told apart in at most 4 of 140
  (4 of 80 at depth 4, under the cap of three with waiting); lengths 3 and 4 in 0 of 80 except 16 of 80 under FLOOR1
  with waiting; 4 and 5 in at most 4 of 160. With the take of a sole candidate, lengths 4 and 5 in 48, 48 and 80 of
  160 under the ordinary count and 98 of 160 under the cap of three with waiting.
- Checks the probe made: renumbering on 150 runs (450 of 450 the same); the knot test on those runs (103,934
  verdicts, none failing).
- **The family `second` was itself a repeat**: fixed with three predictions before it was run; two held and one
  failed in one study of 90 (three or more classes everywhere: one study gives two).
- **Expectations of the drafter that failed**: that with no taking rule nothing would be told apart after round 1;
  that where short knots wait a change at every depth would be seen, later for deeper knots.
- **Not run by anything**: first seeds K to O; the family `fresh`; parity.

## Settled by argument (not refereed)

Under CANCEL-RETIRE and CANCEL-OFFSHOOT a start knot acts in round 1 only. In round 1 every member either retires,
which bars its usable loose distinctions, or gives each of them to a birth, which makes it shared. A knot never
gains a loose distinction, a barred distinction stays barred and a holder never lets go. So no start knot is a member
after round 1. PR4 checks it.

## What is supplied

The starts and every choice in them (A258); the laws, the take of a sole candidate among them (A255); the reading
FF 5; the bounds FF 1; the thresholds below; the seed of the sample. The meeting of the two seeds is supplied.

## What a result would and would not show

- **If C1 to C3 hold on the fresh material**: on built starts, what a part makes depends on the form of what it is
  attached to, beyond the first contact and in kind. It would not show this for parts the growth made, and it would
  not say what decides the classes.
- **If C1 fails** (the fresh forms fall into fewer classes than predicted): the probe's finding was particular to its
  seeds.
- **If C2 fails**: the dependence is one event at the first contact, as the earlier tickets found for a count.
- **If the replication rows fail** while the fresh rows hold: the drafter's reading and the engine's differ, and the
  study reports the engine's, with the first differing study.
- **A positive is a statement about built starts under the listed laws.** No weighting is named.

## Runs

One cap for the whole ticket: **60 minutes of wall time on at most 8 processes**, each under a memory cap of 6 GB.
Before each run a small part is timed and the whole worked out. If the estimate passes the cap, the run is cut to a
prefix of its registered order (first seeds in alphabetical order, laws in the order of FF 1 with no taking rule
first, second seeds in the order of the data file), the cut is recorded before the run, and what is not run is
reported as not run. Estimates from the probe, on ticket B's engine: 0.08 to 0.4 seconds a run.

| Run | What | Runs | Estimate (8 processes) |
| --- | --- | --- | --- |
| R0 | **Gate.** The three starts of FF 2 reproduced. A second growth of a seeded sample of 400 runs of R1 and R2 (seed 1): for laws with no taking rule, by the engine of `PARTS-MEET-AGAIN-20261124-001A`, same structure after every round up to renaming; for the take of a sole candidate, every take recomputed from the rule's words from the places at the start of its round. | 400 | 2 min |
| R1 | **Replication**, not-all-equal: `mixed` and `chains` with first seeds A to E, `second` with F to J, 18 laws. | 13,680 | 8 min |
| R2 | **Fresh**, not-all-equal: `fresh` with first seeds K to O, 18 laws. | 5,490 | 4 min |
| R3 | **Depth, fresh first seeds**, not-all-equal: `chains` with K to O, 18 laws. | 5,670 | 5 min |
| R4 | **The knot law swapped**: R2 under parity. | 5,490 | 4 min |
| R5 | **Controls.** Renumbering (FF 10): a seeded sample of 200 runs of R2 (seed 2), three renumberings each (seeds 3, 4, 5). The knot test, every knot of every round, by ticket B's routine: a seeded sample of 200 runs of R2 and 100 of R4 (seed 6). | 900 | 6 min |

Cut order if the cap is near: R5's knot test to half, then R4, then R3. R0, R1 and R2 are not cut.

The drafter's probe program is run on the fresh material only after the engine's outputs are in, as a second count.

## Predictions

"Seen" means seen in the drafter's probe. Replication rows are exact; a single differing study fails them.

| # | Prediction | Kind | Fails when |
| --- | --- | --- | --- |
| G | R0: the three starts are as written; every sampled run has the same structure under the second growth, or every take is as the rule says | gate | any start differs, or any sampled run differs. A failed gate stops the ticket. |
| PR1 | R1: in each of the 270 studies R\* and the classes equal `disclosed.json` | replication, seen | any study differs |
| PR2 | R1: the tables of first told apart, for `mixed` and for `second`, equal `disclosed.json` | replication, seen | any cell differs |
| PR3 | R1: the depth table for `chains` equals `disclosed.json` | replication, seen | any cell differs |
| PR4 | R1: under the 12 laws with retiring or offshoots, in every run of `mixed` and `second`, every start knot acts in round 1 only | by argument; seen to 6 rounds | any start knot is a member after round 1 |
| PR5 | R1: the tables of fates, for `mixed` and for `second`, equal `disclosed.json` | replication, seen | any cell differs |
| PN1 | R2: in each of the 90 studies the bare start is a class of its own | seen on other material (270 of 270) | some form shares the bare start's class |
| PN2 | R2: the classes among the forms number two or more in all 90 studies and three or more in at least 81 | seen on other material (90 of 90, and 89 of 90) | a study with one class, or more than 9 studies with fewer than three |
| PN3 | R2: in each of the four rows with retiring or offshoots (with and without the take), at least 100 of the 26,550 pairs of forms are first told apart in round 2 or later | seen on other material (200 to 1,096) | a row with fewer than 100 |
| PN4 | R2: in each of the six rows (take or none, by treatment) between 45% and 95% of the pairs of forms are told apart at R\* | seen on other material (59% to 85%) | a row outside that range |
| PN5 | R2: in at least 45 of the 90 studies the forms show two or more of the fates ends, steady, grows | seen on other material (71 of 90) | fewer than 45 |
| PN6 | R4: under parity, the classes among the forms number three or more in at least 60 of the 90 studies | open: no scratch run, the drafter's guess | fewer than 60 |
| PD1 | R3: with no taking rule, for each of the 9 laws: pairs at each depth of 2 or more are told apart in at most 10%; lengths 3 and 4 in at most 30%; lengths 4 and 5 in at most 15% | seen with other first seeds (at most 5%, 20% and 2.5%) | any law and cell above its bound |
| PD2 | R3: with the take of a sole candidate, under the ordinary count (three treatments) and under the cap of three with waiting: lengths 4 and 5 are told apart in at least 15% of the pairs | seen with other first seeds (30% to 61%) | any of the four laws below 15% |
| PD3 | R3: under each of the 18 laws, a chain of one knot is told apart from the chain of two that begins with it in all 20 pairs | seen with other first seeds (20 of 20) | any pair not told apart |
| C1 | R5: what the first seed's descent makes is the same under every renumbering | by the laws using no names; seen (450 of 450) | any renumbered run differs |
| C2 | R5: under not-all-equal no knot fails the knot test in the sampled runs. Under parity the count of failing knots is reported, with no prediction | seen under not-all-equal (none in 150 runs) | a failing knot under not-all-equal |

How the claim is judged: C1 by PN1 and PN2; C2 by PN3 with PR4; C3 by PN5; C4 by PD1 and PD2. A study whose sampled
runs hold a failing knot under not-all-equal is listed apart and does not count toward PN2 to PN5.

## Stop rule

Stop when every registered run within the cap is done and every prediction is judged, holds or fails, or is reported
as not run. No run is added after its outcome is seen.

## Words

First seed, second seed, link, site, bare start, what it makes, class, told apart, fate: as in FF. "Ring" and "chain"
are the record's words for seeds whose knots share distinctions in a closed or an open row; no claim about space is
made with them.

## What the advisor's pass changed

(Written at the freeze.)
