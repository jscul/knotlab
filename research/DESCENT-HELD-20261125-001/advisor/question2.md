You are the design advisor for a pre-registered computational study in a research program on "knot growth". This is the LAST pass before the freeze on a small study: a checked note with one confirming run, on whether the structure itself can hold the order of descent that births made one at a time need. You reviewed its first drafts cold and said "Do not freeze as drafted. Redesign smaller", ten required. You do not remember that review; the drafter's account of what it changed, item by item, is part (5) below. You have no tools; everything is below: (1) my questions; (2) the note, second version; (3) the definitions, second version; (4) the pre-registration of the one confirming run, second version; (5) the drafter's account of the changes; (6) the drafter's report to me; (7) the proposed history lines for the earlier study this corrects; (8) that earlier study's result note (the least record); (9) the shared definitions ("SD"), with line numbers.

Your first review's main points: the ration that counts in threes does not remove the supplied record, it moves it into the law ("shown in the structure's places; written by the law; relative to a start supplied flat"); with the added distinctions barred it is the earlier stamp written in distinctions that do nothing; and a restart lemma (yours, then unchecked): if a structure reached after a birth is itself an allowed start, no function of the structure recovers the parents on a population holding both.

Since then the drafter checked the lemma by a search (176 reached structures under eight laws on six small starts: 173 are allowed starts; within one start's own history 148 have a recoverable order, and none stays recoverable once the restart is in the population), found that 515 of the 3,348 starts of the record's own census are structures reached from a smaller census start, and found that the condition under which the earlier study's three-valued record fails (a birth whose parents are at different numbers of parent steps from the start) occurs on 510 of 3,348 census starts under that study's waiting law and on 48 to 462 under its four holding laws, where that study's published summary says "the one place it fails is the start built so" and found none in sixteen holding runs.

The standard is unchanged: every added rule, weighting and hand-built start a scaffold with its swap; supplied or made said plainly; a rule that counts is not a pattern that counts; nothing called typical, rare or likely without its weighting; no claim about physical time; words from the glossary, one word for one meaning ("parent steps" for the earlier record's "generation", quoted once). The owner's standing rule on compute: spend it in proportion to what a result is worth; this study's one run is sized at about 25 minutes.

## What I need from you (answer under these numbers; short lines; no preamble)

1. **The restart lemma as now written**, with the definition of an allowed start the drafter added (knots of at least three places, one or two holders per distinction, no barred distinction) and its stated limit (a round that reads only the present structure; laws that read the record of parents do not continue a restart the way they continue the run). Is the statement right and as strong as it can honestly be? Is "the lemma's force is about populations: a positive result must name a class of starts that no reached structure belongs to" the right consequence, and does the fact that 515 of the census's 3,348 starts are reached structures change what the earlier studies' "recovers the parents on every structure reached" can mean? Is anything about the search's coverage (26 of 48 cases of law and start finished) worded beyond what was run?
2. **H1 as strengthened** ("parent steps agree counted in threes" in place of "equal parent steps"; the place rule is right on a run exactly when that holds, given the start's meeting knots agree and counts never change). Right? And H3 with the list of what does change.
3. **The earlier study** (part 8) and the proposed history lines (part 7). Is "a narrowing, not a block: the published sentence 'the one place it fails is the start built so' is true of the study's twenty registered pairs, not of the laws" the right verdict and wording, once the confirming run checks the counts? What exactly should the corrected sentence of the earlier study say, in one or two sentences? Does the holding result (48 to 462 starts) change that study's failed prediction about holding into something else?
4. **The one confirming run**: is its content right and enough for a helper who has not seen the prototype (the gate, the hand case and the planted error; the lone-knot renamings; the named starts under the three forms of the ration; the census strata under both weightings; the restart control; two rings with descent and the period formula; the counts of item 3; the knot test)? Anything to cut as not worth its minutes; anything a claim needs that is missing? Is each prediction marked honestly?
5. **Anything still wrong**: a definition that cannot be implemented from the text; "recovers" used in two senses; a sentence that says the growth makes the order, or that a pattern counts; a word that breaks the rules (the drafter was asked to use "parent steps", "count in threes", "new knot", "value" for the stamp only, and the law names NEXT3-PLACES (usable), NEXT3-PLACES (barred), NEXT3-BARRED, NEXT5-BARRED).
6. **The sentences for the owner** at the end of the drafter's report: correct as written? Rewrite any that is not.
7. **Verdict.** Freeze as it is; freeze with listed sentence-level fixes that the thread can apply; or another round. Required fixes in order of importance, then optional.



# (2) The note, second version

# The order births one at a time need, in a knot's own places: a note of two arguments (second version)

Epic `DESCENT-HELD-20261125-001` (sub-goal B328; assumptions A247, A228, A237; goals G5 with G18). Second version,
2026-11-25, after the advisor's cold review of the first drafts (`study/descent_advisor/answer.md`); the first versions are
kept beside this file. Definitions: `definitions_v2.md` ("DH2"), which builds on the shared definitions ("SD",
`research/RING-IN-BALANCE-20261123-001/definitions.md`), the parents-from-holders pre-registration ("PH") and the
least-record pre-registration ("LQ"). No claim is made about physical time, physics, living things or minds.

**Everything in this note was seen in the drafter's scratch runs before it was written.** The two arguments are the note's
content; one confirming run (`preregistration_v2.md`) checks them with a second program.

## The question, and the verdict line

The owner's direction, as the thread put it to him: "a count of descent held by the structure itself, which would remove
the last supplied record" (`research/DESCENT-HELD-20261125-001/owner_request.md`). The record it means is the stamp of
A247: each new knot's parent steps from the start counted in threes, written by whoever runs the growth (the least-record
study's word is "generation").

**Verdict:** *shown in the structure's places; written by the law; relative to a start supplied flat.* The supplied record
is moved into the law, not removed. This note does not say the order is held by the structure; the owner's question keeps
its own words.

## Argument 1. The restart lemma (argued, not refereed)

**Hypotheses.**
- (R1) A law L that makes births, with any ration, treatment, release rule, extras, number of holders or taking rule.
- (R2) A class 𝒮 of allowed starts, stated in terms of what a start may carry (DH2 1.2: for this program's two-holder
  laws, knots of at least three places, one or two holders per distinction, no barred distinction).
- (R3) A start S0 in 𝒮 and a structure T reached from S0 under L after at least one birth, with T itself in 𝒮.
- (R4) A population Π of (structure, record of parents) that holds both (T, its record from S0) and (T, as a start: no
  parents).

**Conclusion.** No function of the structure, at any distance, names the parent places correctly on every member of Π. The
place of T's last new knot to its parent is a parent place in the first member and a place between two start knots in the
second; any function of the structure gives the same answer at both.

**For complete rounds, more.** Where the round reads only the present structure (SD's round does: groups, owing, shortness,
births, demand and the fresh count use usable loose distinctions, met sets and counts, and never the record or the round
number; SD lines 34-77 and `research/RING-IN-BALANCE-20261123-001A/preregistration.md` lines 92-93), the growth from T as a
start equals the growth from S0 after T, round by round. So every later structure is also held twice, and the conclusion
holds on the whole population of structures reached from both.

**Its smallest instance, M1.** Under each recorded ration with the values of a below, the lone start knot of a places makes
a offshoots in round 1, each with demand a − 1. If the ration gives the first offshoot a − 1 fresh distinctions, the
structure after that one birth has two knots of a places, each with one shared and a − 1 usable loose places. It is an
allowed start, and it is also its own instance of a two-knot symmetry: exchanging the two knots and their loose
distinctions, the shared distinction fixed, is a renaming that exchanges the offshoot's place to its parent with the start
knot's place to its child. Cases: ORD, a = 3, 4, 5; CAP-3, a = 3, 4; RATION-3, a = 4; RATION-4, a = 5; FLOOR1, FLOOR0 and
ONE-FEWER, a = 3; under any treatment and release rule (round 1 has no group) and with or without FILLERS (there f = D, so
nothing is barred); not under NO-OFFSHOOT, which makes no birth. For a = 3 the structure is the named two-knot start
`[[0,1,2],[0,3,4]]` of the record, reached under ORD, CAP-3, FLOOR1, FLOOR0 and ONE-FEWER.

**Population.** M1 is about one start per ration. It refutes any one function meant to name the parents on every structure
reached from every allowed start under those rations. It says nothing about a population confined to the histories of one
start.

**The drafter's check of the lemma (scratch, `w3_restart.py`).** The conclusion has no counterexample once both members are
in the population: it needs only that a new knot has a parent. What can fail is hypothesis (R3). So the check asked, for
eight laws and six small starts, on the structures after complete rounds 1 to 3 (at most 60 knots) and on the half-built
structures of the start and a prefix of round 1's new knots (at most 12 knots): is the structure an allowed start, and is its
order recoverable within its own start's history alone (no renaming of the whole structure exchanges a parent place with a
place that is not one)? Results are in `changes_v2.md`, item "the restart lemma" (26 of 48 cases finished before the drafter cut the run; 176
structures). In short: reached structures are
allowed starts except where the law has barred a distinction (retiring, FILLERS) or made a knot of fewer than three places
(the closing exception); most reached structures that are allowed starts have an order recoverable within their own
history; and the restart grows exactly as the continuation. So the lemma is about populations that include restarts, and a
positive result must name a class of starts that no reached structure belongs to.

**The record's own population holds restarts.** Of the 3,348 census starts of up to five knots, 515 are themselves
structures reached, after one or more of round 1's births, from a census start of at most four knots under some recorded
law (145 to 234 by law; scratch, `w6_census_restart.py`, isomorphism with marks). So on the census's histories taken
together, by argument 1, no function of the structure names every parent place.

**Where "allowed start" needs a statement.** SD says what a start is (lines 11-18) but not, in so many words, that a start
may not carry a barred distinction; "a loose distinction is usable unless the law has barred it" (line 17) reads that way.
Every positive result here rests on such a statement: condition (a) below, or "a start has no barred place".

**Narrowed with it.**
- **L3.** Under a ration that is a function of the new knot's number of parents p and demand D alone, at a birth that is not
  a closing birth and whose (p, D) equals that of a parent that is not a start knot, the two knots have equal numbers of
  places; no rule on the two counts can then answer differently from the two sides of the place between them. Argued; its
  scope is each such birth.
- **M2.** On the census of starts of up to five knots (each start counted once up to isomorphism; 3,348 whose start knots
  pass the parity test), under each of ten recorded laws, grown through 8 rounds or 3,000 knots: every start that reaches a
  knot at three parent steps has some birth whose number of places is not one more, counted in threes, than some parent's.
  Seen, not argued. The threshold "three parent steps" was chosen after the scratch run.
- **Withdrawn:** "every ration of p and D alone". A ration with F(1, a − 1) ≠ a − 1 for every a escapes M1, and L3 then
  speaks only of births that repeat a parent's (p, D).

## Argument 2. Counting places in threes, written by the ration (H1 with H3; argued, not refereed)

**The laws (arm W).** On a base law B (SD's form, two holders, no taking rule, RELEASE or HOLD), a new knot x with parents
y_1, ..., y_p and base count F receives s more fresh distinctions, s the least of 0, 1, 2 that makes x's count one more,
counted in threes, than its parents' common count (DH2 3.2):
- **NEXT3-PLACES (usable):** the count is the number of places; the s distinctions are usable.
- **NEXT3-PLACES (barred):** the count is the number of places; the s distinctions are barred at birth.
- **NEXT3-BARRED:** the count is the number of barred places; the s distinctions are barred at birth.

**The place rule** at a shared place of x whose other holder is y: "a parent place" exactly when y's count is one less than
x's, counted in threes. It uses the two holders' counts: shown within 1.

**H1. Hypotheses.** (a) Every two start knots that meet have the same count in threes (for NEXT3-BARRED this is the
convention that a start has no barred place); (b′) every birth's parents are at numbers of parent steps that agree counted
in threes; (c) no knot's count changes after its birth (a start knot's: after the start) by a number not divisible by 3.
**Conclusion:** within each connected piece of the start, every knot's count is the piece's common start count plus its
parent steps, counted in threes, and the place rule is right at every shared place of every structure of the run, and of
every parent-closed part of one (DH2 4.3). **And conversely**, given (a) and (c), if (b′) fails at some birth, the first
such birth has parents of different counts, and the place rule is wrong at one at least of its places to its parents. So,
given (a) and (c), the place rule is right everywhere on a run exactly when (b′) holds.

*Argument.* Induction on births in order of rounds. Before the first birth all knots of a piece have one count c (by (a),
pieces being connected through meetings). If every earlier knot has count c + parent steps and a birth's parents agree in
parent steps counted in threes, they have one count, and the ration makes the new knot's count one more, which is c plus its
parent steps, counted in threes (its parent steps are one more than the greatest of its parents', which agrees with each
counted in threes). By (c) counts keep this value. At a shared place the holders are parent and child (count one apart in
the right direction) or two start knots (equal). The rule's verdict at a place uses only the two holders' counts, fixed at
birth, so it is the same in every structure that holds both. For the converse, the first birth whose parents' parent steps
disagree counted in threes has parents of two different counts, and the new knot's count is one more than at most one of
them.

*What holds (b′) up.* Equal parent steps (LQ's sketch, under RELEASE: every knot acts in at most one round, so a common knot
of two members is a parent of both or a start knot meeting a start knot; the leak is a start knot that waits while one it
meets acts) is sufficient. It is not true on the census (history lines): under the four waiting bases parents at different
parent steps occur on 510, 510, 510 and 223 of 3,348 starts; under holding with retiring or offshoots on 368 and 462. (b′)
is decided from the record; no knot can check it.

*(c) exactly.* Only retiring changes a count after birth here (it bars a knot's usable loose places). For NEXT3-BARRED, a
knot that retires with h more barred places keeps its count in threes if h ≡ 0; if h ≡ 1 its places to its parents are
wrong from both sides; if h ≡ 2, from its own side only (for a retired start knot, its places to other start knots: from its
own side if h ≡ 1, from the other side if h ≡ 2). Seen to give exactly the wrong places on 16 runs (FLOOR1 with retiring,
with RELEASE and HOLD, 8 named starts each); h ≡ 0 did not occur there. The place-count forms have (c) under every law here.

**Population.** H1 is about every run, under every law of arm W, from a start that meets (a), on which (b′) and (c) hold;
the census strata (`preregistration_v2.md`) count the starts that do. By argument 1 no reached structure meets (a): its last
new knot and its parent have counts one apart.

**H3. With the s distinctions barred, no birth changes (argued, not refereed).** A barred distinction is never taken and
never counted in h (SD lines 17-18, 22-24, 67). Groups, owing, shortness, births, demand and the base count read only usable
distinctions and met sets, so under both barred forms every birth, its parents and its round are the base law's, through
the base law's closing round under parity. The one place a barred distinction acts is the closing exception: one barred
distinction anywhere switches it off (SD lines 72-74), so from the first s > 0 on it is off for the rest of the run, and
where the base law closes the barred form goes on. Under NEXT3-BARRED the first birth from a start with no barred place leaves a
barred distinction (s = 1 without FILLERS; a barred filler or s with it), so the exception never applies. Seen: births equal on every scratch run except the lone four-place knot under ORD and
CAP-3, where the base law closes at round 4 under parity.

**So the barred forms are the stamp of A247 written in barred distinctions.** Without FILLERS NEXT3-BARRED's write rule is
the stamp's rule word for word (one more than the parents', counted in threes; a start knot is 0, here as "a start has no
barred place"), and H3 is the proof that it factors out of the growth.

**What does change under the barred forms** (none of it is the count doing anything; no knot uses the comparison):
- A knot with a barred added place stays live for good.
- Under parity such a knot never constrains its shared places against one another, and under not-all-equal its loose place
  satisfies it; so the allowed states change. Seen (scratch, 12 named starts × 7 bases, 8 rounds or 3,000 knots): the share of
  new knots with s > 0 is 0.62 overall under NEXT3-PLACES (barred) and 0.78 under NEXT3-BARRED, 0.25 to 1 by run;
  `preregistration_v2.md` registers it as the cost.
- The closing exception is off from the first s > 0.
- SD's sameness counts barred loose places (k, line 29), so returns, periods and census kinds change. A part that returns
  with period T, its members q parent steps on at each return, returns with its barred marks every T · 3 / gcd(3, q)
  rounds. Seen with descent checked on the rings of five and seven knots under the two and the three added rules: T = 2,
  q = 1, period 6 under both barred forms. What the members show is parent steps counted in threes, which equals the
  number of returns only because each return is one parent step on. The ration wrote it and nothing uses it. (A note for the
  count-of-returns study: any annotation in barred places changes periods as SD reads them.)

**The usable form** belongs in the price list: its added distinctions become offshoots (`FRESH-COUNT-20261118-001`: a count
rule only places offshoots), so the births differ from the base law's; no knot uses the comparison. With FILLERS it bars
the added distinctions whenever F + s > D and then equals the barred form at those births.

**Knot test.** An added loose place cannot make a knot fail under either knot law (it satisfies its knot, and constrains no
other); so every new knot passes wherever it would under the base law, and the confirming run's knot test is a check of the
code. Seen: 51,063 knots in 162 scratch runs pass under both knot laws.

**Numberings.** Argued for every numbering (every step uses counts and met sets; which usable loose distinction goes to
which birth is a renaming, SD lines 76-77; s uses counts only). No difference was found in 89,910 scratch runs (every
numbering of four starts of at most six distinctions, and the 4n and 200 registered numberings of five others, 4 rounds).

## The three tests in place of reading the law's text

For a law and a stated class of starts, each answer exhaustive:

1. **Inputs.** Does some input of the ration determine the parents' counts that the place rule compares? *Written*: yes
   (arm W: the parents' numbers of places or of barred places are inputs). *Not written*: no input does (every recorded
   ration: p and D only).
2. **Factoring.** Delete the rule (s = 0 always). *Factors*: births, parents and rounds are the same with and without it
   (the barred forms, H3, up to the closing exception). *Does not factor*: they differ (the usable form). *No rule*: the law
   has none to delete (the recorded laws).
3. **Restart.** *Closed*: some structure reached from the class is itself in the class; then by argument 1 nothing the
   structure shows names the parents on the population holding both. *Not closed*: no reached structure is in the class
   (condition (a) under the place-count forms; "a start has no barred place" under NEXT3-BARRED).

The order would be **made**, in the only sense this note admits, if inputs is *not written*, the start class is *not
closed* and stated without the count, and some function of the look within a fixed d names every parent place on every
structure reached from that class, on runs several parent steps past the start, one round past. No law here does that:
the recorded laws answer *not written* and, with the record's starts, *closed*; arm W answers *written*.
With nothing supplied about starts (every allowed start admitted), "made" is closed by argument 1, once it is
refereed: every class that admits all allowed starts is closed under restart wherever a reached structure carries no mark a
start may not carry.

**What stays open,** parked as an idea and not designed: from a start class fixed without the count (lone knots, say),
whether some ration with no parent count among its inputs shows the order at a fixed distance (the advisor's smallest
search: the seven recorded rations each plus one and plus two fresh, four treatments, lone starts of 3 to 5 places, PH's
search at d ≤ 3).

## For the owner (the advisor's sentences, adjusted to what is true)

- Under the recorded laws nothing the structure shows gives the order. A lone knot and its first offshoot are exchanged by
  a renaming. More generally, a structure reached by a birth can itself be handed in as a start, and then the same places
  have no parents.
- If we write a ration that uses the parents' place counts and adds 0, 1 or 2 distinctions, each new knot's count is one
  more, counted in threes, and a knot can compare counts across one shared distinction. This is the stamp of A247 moved into
  the law. With the added distinctions barred, no birth changes, which is what shows it is a stamp.
- It works only from a start whose meeting knots already agree (133 of 3,348 census starts of up to five knots, each counted
  once up to isomorphism; 804 of 82,372 at six knots), or by the convention that a start has no barred place. It works only
  where parents are equally many parent steps from the start, counted in threes; parents at different parent steps occur on
  510 of 3,348 census starts under the waiting law of the least-record study, and on 48 to 462 under the holding laws.
- So the supplied record is moved, not removed. The order is relative to a start supplied flat. No pattern counts; nothing
  uses the count; nothing here is a clock.
- All of this was seen in scratch before the claim was written. The confirming run checks it with a second program; it
  tests little that the arguments do not already give.


# (3) The definitions, second version

# The order in a knot's own places: definitions, second version ("DH2")

Epic `DESCENT-HELD-20261125-001`. Replaces `definitions_draft.md` (kept). Builds on the shared definitions ("SD",
`research/RING-IN-BALANCE-20261123-001/definitions.md`, cited by line), the parents-from-holders pre-registration ("PH",
`research/PARENTS-FROM-HOLDERS-20261124-001A/preregistration.md`), the least-record pre-registration ("LQ",
`research/LEAST-RECORD-20261124-001A/preregistration.md`) and the fold study's knot test ("FD 7",
`research/PARTS-MEET-AGAIN-20261124-001/definitions.md` lines 265-289). Nothing in them is changed. The canonical K1-K3 test
is unchanged. Every term is decided by a program from a run's structures and its record.

## 0. Words

0.1 SD's words (lines 9-77): structure, place, holder, loose, shared, usable, barred, start, start knot, member, met set,
common knot, joinable, part, group, owing, short, join, offshoot, demand D, ration, treatment, release rule, extras,
closing exception, round. **New knot** is SD's word for a knot a birth makes. Two holders per distinction; no taking rule.

0.2 PH's and LQ's words: look within d, alike, confusable pair, parent place, not a parent place (a child place, or a place
between two start knots), holder step, holder-step distance, stamp, half-built structure, the condition (LQ line 170-172).
"Mark": loose and usable, loose and barred, or shared.

0.3 **Parent steps** of a knot: 0 for a start knot; one more than the greatest of its parents' for a new knot. It is the
least-record study's "generation" (SD line 121; LQ line 37), quoted here once. It is computed from the record of parents.

0.4 **Count in threes**: a number's remainder on division by 3; "one more, counted in threes" means a difference of 1 modulo
3. "Mod" appears only inside formulas.

0.5 **Value** is kept for the stamp of A247 (a number written on a knot by whoever runs the growth). What this study puts in a
knot's places is its **count** (DH2 2.1).

0.6 Words not used: "held" for this study's result (it has four senses already: knots hold distinctions, HOLD, HOLD-COUNT's
counts, a prediction that holds); "generation" outside the quotation of 0.3; "reads" for anything but the owner's sense;
"made" for knots ("new knot").

## 1. Runs, starts and their record

1.1 **A run** is one start grown under one law and one knot law in complete rounds (SD steps 1-8), through R rounds or until
the first round after which the structure has more than N knots, or until a round makes no birth or stalls (SD lines 81-84).
**Every run names its knot law** (parity or not-all-equal): it decides the closing exception (SD lines 63-66) and the knot
test. Census runs are made under both knot laws; the two differ only from a closing birth on, and runs where they differ are
reported.

1.2 **An allowed start**: a finite structure of knots, each of at least three places, each distinction with one or two
holders, no distinction barred (the reading of SD lines 11-18: a loose distinction is usable unless the law has barred it, so
before any birth none is barred). Census starts are also connected with at least one live knot. A structure reached by a
birth **is an allowed start** when it meets this definition with its marks as they are.

1.3 **The record of parents** is written by each birth (A242), with its round. It is the answer checked against; no law here
takes it as an input, and no look shows it.

1.4 **The order of new knots** is the engine's (SD steps 4 and 5: groups in sorted order, then offshoots by member). It names
knots for the record only. A verdict that depends on it (such as "the first failing birth" of a round, with its kind) is
reported as the round and the multiset of the births in question.

## 2. A knot's counts

2.1 Fixed at a knot's birth (for a start knot, at the start): its number of places n; for a new knot its number of parents
p, its demand D, its fresh distinctions f, so n = p + f; its number of places barred at birth z (FILLERS, and DH2 3.2's
barred added distinctions; 0 for a start knot).

2.2 **Changing later**: the number of barred places b, which is z at birth and grows only when the knot retires
(CANCEL-RETIRE bars its usable loose places, SD lines 47-48), for start knots and new knots alike; and its numbers of loose
and shared places, which change with later births.

2.3 **Shown within d**: a function of a knot's look within d holder steps (PH lines 37-42) that is unchanged by every
renaming of knots and distinctions. n and b are shown within 0; the other holder's n and b within 1. p, f, D and parent
steps are not shown in general; written on a knot they are stamps. "Shown within d" is always written with its d, and a
claim that a function names the parents always names its population, the function being one function for the whole
population.

## 3. The laws

3.1 **Arm R, the recorded laws**: `laws.json`, "recorded" (ten laws with RELEASE) and "holding" (four with HOLD), each with
what it adds by hand (A104, A224). Every ration there is a function of (p, D) alone (SD lines 59-62). NO-OFFSHOOT is not used.

3.2 **Arm W, the laws that write the count.** For a base law B and a count form, B with SD step 7 changed as follows and
nothing else. For a new knot x with parents y_1..y_p:
  1. **The base count** F = F_B(p, D); at a closing birth (parity, SD lines 63-66) F = 0, except as in step 5.
  2. **The parents' counts** κ(y_i), read at the moment of the birth: for NEXT3-PLACES the number of places n(y_i); for
     NEXT3-BARRED the number of barred places b(y_i); counted in threes.
  3. **The target.** If every κ(y_i) is one count c, the target is c + 1 (mod 3). Otherwise x is **a birth whose parents
     differ**, counted. Registered rule: no target, s = 0. Swap: if the parents' counts are exactly two, c and c + 1
     (mod 3), the target is c + 2 (one more than the greater); otherwise no target.
  4. **The added count** s: the least of 0, 1, 2 that makes x's count the target: p + F + s for NEXT3-PLACES; z_F + s for
     NEXT3-BARRED, z_F being the number of F's distinctions FILLERS bars (0 without FILLERS).
  5. **A would-be closing birth with s > 0** (a birth that takes every loose distinction, whose count would miss the target
     with F = 0): it receives F_B(p, D) computed as if no closing exception applied, and s is recomputed on that F; the
     structure then does not close. (This keeps every new knot at three places or more, SD lines 12-13.) Swap: no added
     count at a would-be closing birth (s = 0 there, the closing as SD).
  6. **Usable or barred.** NEXT3-PLACES (usable): x receives F + s fresh distinctions, FILLERS (if in B) applying to all
     F + s (min(F + s, D) usable, the rest barred). NEXT3-PLACES (barred) and NEXT3-BARRED: x receives F as B gives them
     (FILLERS applying to these F) and s more, barred at birth.
  What each adds by hand: the parents' counts as inputs of the ration, the counting in threes, the target, the added
  distinctions and where they go.

3.3 **NEXT5-BARRED** (a stated variant, not a law the study registers): counts in fives; the target is one more than the
parent count c for which every other parent count w has c − w in {0, 1, 2} (mod 5); the place rule reads "one or two less,
counted in fives". It is the least-record study's counting in fives (LQ results line 71-75), moved here; a greatest difference
of d parent steps needs counting in 2d + 1 (LQ results line 75).

3.4 **The brief's literal wording** (the fresh count one more, counted in threes, than the parent's) is not a law of this
study: the place rule would compare n while the law writes f, and n(x) − n(y) ≡ p(x) − p(y) + 1, so it is wrong at
the place of every offshoot of a start knot to its parent, from the offshoot's side. Stated in one sentence in the note.

## 4. The place rule and the two meanings of "recovers"

4.1 **The place rule** for a count form: at a shared place a of knot x whose other holder is y, the prediction is "a parent
place" exactly when κ(y) is one less than κ(x), counted in threes; otherwise "not a parent place". It uses κ(x) and κ(y):
shown within 1.

4.2 **"The place rule is right on"** a structure: at every shared place the prediction is the place's kind. On a run: on the
structure after every round.

4.3 **"Recovers the parents"**, kept in LQ's sense only (arm R): a population has no confusable pair at distance d (PH lines
45-49); a renaming of a whole structure that exchanges a parent place with a place that is not one is a confusable pair at
every d.

4.4 **A parent-closed part** of a run's structure after round t: a set of its knots holding every start knot and, with each
knot, its parents. It is taken as a construction: each knot with all its places as at the end of round t; a distinction with
one holder in the part loose there; barred marks as at the end of round t (a knot that retires bars its places in the round
it would have acted, so a part made of knots of earlier rounds carries those marks only from that round's end). It is not a
half-built structure of a run made one birth at a time (under ORD such a structure does not have D yet); LQ's half-built
structures are such parts, up to renaming of distinctions, wherever the one-birth-at-a-time run matched the rounds (the
matching statement of `LOCAL-ROUND-20261123-001A`'s laws module, "the run's structure is ... the sub-structure of the
reference made of the image set I"). The place rule's verdict at a place uses only the two holders' counts, so it is the
same on every part that holds both, where (c) holds.

4.5 **The conditions on a run**, each decided from the run:
  - (a) **The start's counts agree**: every two start knots that meet have the same count in threes. For NEXT3-BARRED it holds
    by 1.2 (no start knot has a barred place).
  - (b′) **Parent steps agree in threes**: every birth's parents have numbers of parent steps that agree counted in threes.
    Reported beside it: (b) every birth's parents have equal parent steps; and LQ's condition (a start knot waits in a round
    in which a start knot it meets is a parent of a birth), which is sufficient for (b) under RELEASE and not necessary.
  - (c) **Fixed counts**: no knot's count changes after its birth (a start knot's, after the start) by a number not divisible
    by 3.

4.6 **The greatest difference** of a run: the greatest, over births and their parents, of the new knot's parent steps less the
parent's (1 where (b) holds). Reported by start and by round.

## 5. Arm R

5.1 **The lone-knot structure** of a ration F and a number a ≥ 3 with F(1, a − 1) = a − 1: the start of one knot of a places,
and the structure after its first offshoot in DH2 1.4's order.

5.2 **The renaming that exchanges them**: a one-to-one renaming of the knots and distinctions of that structure, keeping
every mark and which places are one distinction, that exchanges the two knots and their loose distinctions and fixes the
shared distinction; it carries the offshoot's place to its parent onto the start knot's place to its child. Found by search
over every renaming and checked place by place.

5.3 **The census verdict on places** for a law and a start (M2): grown round by round, "fails at round r" (with the multiset of
the failing births' kinds) at the first round with a birth whose n is not one more, counted in threes, than some parent's;
"holds through R", "holds on a finished structure" or "holds, cut at N knots" otherwise. **Reaches three parent steps**: some
knot of the run has parent steps 3 or more (a threshold chosen after the scratch run).

5.4 **The restart control**: the structure after round t of a run, handed in as a start (its record of parents dropped), grown
under the same law for k more rounds; compared with the run's structure after round t + k by an exact test of isomorphism
of knots and distinctions with marks; and the place rule of arm W applied to the restarted structure.

## 6. Growth compared

6.1 Births by round, knots, how the run ended (SD lines 81-93).

6.2 **Same births**: for every round through the last both runs reached, the list of each new knot's parents in DH2 1.4's
order is the same under B and under B with a count form.

6.3 **The cost**: the share of new knots with s > 0, and the mean of s.

6.4 **Returns with barred marks**: SD lines 85-88, sameness as SD line 29 with k counting every barred loose distinction;
for the first return found (least s, then least t), its period T and the change q of parent steps between the part's
members and the returned part's members. **The period formula**: under a barred count form, the least period with barred
marks is T · 3 / gcd(3, q).

## 7. The knot test

Every start knot and every new knot of the run's last structure, under the run's knot law: parity by FD 7's ranks and kernel
methods, which must agree; not-all-equal by FD 7's decomposed method (`nae_decomposed` of the fold study's `knots.py`, exact,
with no hypothesis on fresh distinctions). **One bound**: the knot test is made on structures of at most 3,000 knots (every
structure the runs make); the direct not-all-equal method is used as a check of the code only, on knots of at most 7 places in
structures of at most 150 knots. A census start with a start knot that fails under the run's knot law is set aside for that
knot law (under parity 32 of 3,380 starts at five knots or fewer and 284 of 82,656 at six; none under not-all-equal at five
knots or fewer, scratch).

## 8. Numberings

8.1 A numbering of a start: an order of its knots and of its distinctions. Every numbering when the start has at most six
distinctions; else the 4n (the n shifts of the order of distinctions, each as given or reversed, knots as given or reversed)
and the registered 200 of `numberings_registered.json`.

8.2 The test: an exact isomorphism test (knots and distinctions with marks) between the run's last structure under a numbering
and under the numbering as given, on the starts of at most six distinctions; elsewhere the signature (births by round; the
multiset of (round of birth, parent steps, p, n, z, s, number of children, b) over knots; the place rule's counts by kind).
"Argued for every numbering; no difference found in N runs" is the only sentence a result may say.

## 9. The census and its weightings

9.1 The census of `COPYING-PARTS-20261123-001A` (`cpcensus.py`, read-only): connected graphs of networkx's atlas on 1 to 5
vertices (and 6 for condition (a) and the sample of 9.3), a loose count 0 to 3 on each knot with degree plus loose count at
least 3 and at least one live knot, each kept once up to the graph's automorphisms; one shared distinction per edge. 3,380
starts on 1 to 5 knots; 82,656 on 6.

9.2 **The census weighting**: each start counted once. **The labelled weighting** (the swap): each start weighted n!/|Aut|,
|Aut| the number of the graph's automorphisms that keep every loose count, that is, each numbering of the knots counted once.
The strata are unchanged by renaming, so the labelled shares are a reweighting of the same runs.

9.3 **The six-knot sample** for (b′): 3,000 starts of the 82,372 kept under parity, taken in the order of
`random.Random('DESCENT-HELD-20261125-001|six|v2')`'s shuffle of the census order; a prefix of that order is itself a sample.

## 10. Scaffolds and their swaps

The count form (places or barred places); where the added distinctions go (usable or barred); counting in threes (fives as the
stated variant of 3.3); the rule at a birth whose parents differ (none; one more than the greater of two); the closing reading
(3.2 step 5; its swap); the base laws; the starts and the two weightings; the bounds R and N; complete rounds (one birth at a
time is not run).


# (4) The pre-registration of the confirming run, second version

# The order in a knot's own places: one confirming run. Pre-registration, second version

Ticket `DESCENT-HELD-20261125-001A` of epic `DESCENT-HELD-20261125-001` (sub-goal B328; assumptions A247, A228, A237; goals
G5 with G18). **Second draft, 2026-11-25, after the advisor's cold review; not frozen.** It replaces
`preregistration_draft.md` (kept). The study's result is the note `note_v2.md` (two arguments, each argued, not refereed);
this run checks the note with a second program. **Every prediction below was written after the drafter's scratch runs,
which saw each of them.** The code will be written by a helper who has not seen the prototype, from this text, `note_v2.md`,
`definitions_v2.md` ("DH2"), the shared definitions ("SD"), and the data files `laws.json`, `starts.json`,
`numberings_registered.json`. It imports read-only `lr_core.py` of `LOCAL-ROUND-20261123-001A` (`compute_groups`,
`start_stars`, `own_round`), `cpcensus.py` of `COPYING-PARTS-20261123-001A`, and `knots.py` of `PARTS-MEET-AGAIN-20261124-001A`
(`parity_test`, `nae_decomposed`, `nae_direct`). The canonical K1-K3 test is unchanged. No claim about physical time,
physics, living things or minds.

## The question

The owner's words (24 November 2026, Pacific time): "Could you work your way through all 4 of these? You can work in
parallel." The direction taken, as the thread put it to him: "a count of descent held by the structure itself, which would
remove the last supplied record." The note's answer: *shown in the structure's places; written by the law; relative to a
start supplied flat.* This run asks only whether a second program finds what the note argues and the scratch runs saw.

## Prior work in the program

As in `preregistration_draft.md`, "Prior work in the program" (six searches with `--until 2026-11-25 --exclude
DESCENT-HELD-20261125-001`; the epics of their top three rows: `LEAST-RECORD-20261124-001`,
`TWO-KNOTS-ONE-DECISION-20261121-001`, `CALIBRATIONS-CLOCKS-AND-WIDER-KNOTS-20261120-001`, `SEQUENTIAL-WALL-20261116-001`,
`WALL-READ-20261119-001`, `MERGE-BURST-20261119-001`, `PARENTS-FROM-HOLDERS-20261124-001`, `ONE-PARENT-REREAD-20261123-001`,
`MEET-ORDERS-20261118-001`, `PARTS-MEET-AGAIN-20261124-001`, `MEET-GROW-20261118-001`,
`QUIET-RETURNS-AND-SIGNAL-FRACTIONS-20261122-001`, `RING-IN-BALANCE-20261123-001`, `GROWTH-STATISTICS-20261121-001`,
`DOUBLE-IDENT-20261119-001`). Used: `LEAST-RECORD-20261124-001`, `PARENTS-FROM-HOLDERS-20261124-001`,
`RING-IN-BALANCE-20261123-001`, `FRESH-COUNT-20261118-001`, `LOCAL-ROUND-20261123-001`, `GUARD-CAP-AND-HOLD-20261124-001`.

## Prior work outside the program

From memory, not checked: graded orders and their ranks, oriented locally by the rank counted in threes (folklore); phase
clocks of self-stabilizing unison (Couvreur, Francez and Gouda, 1992); proof-labelling schemes (Korman, Kutten and Peleg,
2010); views in anonymous networks (Angluin, 1980). What the note adds: that in these growth laws the count is in the
structure only where a ration is written to put it there, from a start supplied flat, and that a structure reached by a
birth can be handed in as a start.

## Known before the run

All of it: see `note_v2.md` and `preregistration_draft.md`, "Known before the runs", and `changes_v2.md`. The scratch
prototype (`de.py` and the scripts of the scratch folder, with `out/`) is unreviewed and is not this run's engine.

## Settled by construction (the note's arguments; argued, not refereed)

Argument 1 (the restart lemma, with M1, L3 and M2 narrowed) and argument 2 (H1 with its converse, and H3), as stated in
`note_v2.md`. The knot test (an added loose place cannot make a knot fail) and the numbering argument, as stated there.

## What is supplied

SD's list (lines 155-160) for the base laws; the count forms, counting in threes, the target, the added distinctions and
where they go; the rule for a birth whose parents differ and its swap; the closing reading and its swap; the starts (named
and the census), both weightings, the six-knot sample's seed; the bounds. The record of parents is the answer checked
against.

## What the run would and would not show

- **It would show** that a second program, written from this text, finds the arguments' conclusions on the populations
  named, and the census strata counted.
- **It would not show** anything the arguments do not give, beyond those counts; nothing about laws with three or more
  holders, about births made one at a time, or about time; and nothing that reads the count.

## Starts and files

`starts.json` (14 named starts); the census (DH2 9.1: 3,380 starts on 1 to 5 knots; 82,656 on 6); `laws.json`;
`numberings_registered.json`.

## The run, in its registered order

One process may do several parts; parts run in this order, and within a part starts in their file or census order and laws
in `laws.json` order, so that a cut leaves a prefix. Rates are the drafter's scratch rates on this machine (one process).

| Part | What | Items | Seconds per item (scratch) | Wall time, 6 processes |
| --- | --- | --- | --- | --- |
| 0a | Gate: with no count form, the engine's round equals `lr_core.own_round` (names included) on the twenty pairs of `LOCAL-ROUND-20261123-001A`'s `gate.json`, 8 rounds or 3,000 knots | 20 runs | about 1 | under 1 minute |
| 0b | The hand case (below) | 1 | — | seconds |
| 0c | The planted error (below), on the named starts under each base and both barred forms | 14 × 11 × 2 | under 0.1 | under 1 minute |
| 0d | Numberings: exact isomorphism test on the four named starts of at most six distinctions, every numbering, 5 bases × 3 forms, 4 rounds | 4,590 × 15 | under 0.01 | about 1 minute |
| 1 | M1: the lone-knot structures (DH2 5.1) of `laws.json`'s 11 cases; the renaming searched under the base and the three count forms | 44 | under 0.1 | seconds |
| 2 | The named starts: 14 starts × 11 bases (seven with RELEASE, four with HOLD) × (base, NEXT3-PLACES usable, NEXT3-PLACES barred, NEXT3-BARRED) × both knot laws; 8 rounds or 3,000 knots; for each run the conditions (a), (b′), (c), the place rule's right and wrong places by kind, births by round, same births (DH2 6.2), the cost (6.3) | 1,232 runs | 0.05 | under 1 minute |
| 3 | The census strata: (a) on all 3,380 + 82,656 starts (no growth); (b′), (b), LQ's condition and the greatest difference by round (DH2 4.6) on the 3,380 starts under the 14 laws of `laws.json` (recorded and holding) and both knot laws; the place rule under the three count forms on the seven RELEASE bases, parity; the six-knot sample (DH2 9.3) for (b′) under the four waiting bases; every share under both weightings | 3,380 × (28 + 21) and 3,000 × 4 | 0.3 per start for the 28, 0.5 for the 21; 0.03 per sample start | about 10 minutes |
| 4 | M2 on the census: the ten recorded laws, DH2 5.3, stopping at the first failing round | 3,380 × 10 | 0.01 | under 1 minute |
| 5 | The restart control (DH2 5.4): eight laws (`laws.json`'s first seven and H-R3W) × six small starts (lone three- and four-place knots, the two-knot and three-knot starts, the ring of five, the cycle through doubled dead knots of four members), t = 1, 2, 3, k = 2, structures of at most 1,500 knots; and the arm-W count forms' reached structures after round 1 handed in as starts, with the place rule applied; and the census starts (of up to five knots) that are isomorphic, marks kept, to a structure reached after one or more of round 1's births from a census start of at most four knots under a recorded law | 144 + 6 × 11; 223 × 10 | about 1; under 0.01 | under 3 minutes |
| 6 | Two rings with descent: the rings of five and seven knots with three loose on each, under the two and the three added rules, base and both barred forms, 14 rounds, returns searched as DH2 6.4 | 12 | about 2 | under 1 minute |
| 7 | The knot test (DH2 7) on the last structure of every run of part 2, and of part 6 | 1,244 | 0.6 on average, 25 at most | about 4 minutes |

Total about 25 minutes on 6 processes, well under the hour. **Limit:** a part not finished in 30 minutes is cut to its
prefix and reported as such.

**The hand case (0b).** The two-knot start `[[0,1,2],[0,3,4]]` under (FLOOR1, CANCEL-OFFSHOOT), NEXT3-PLACES (usable),
parity. Round 1: no met set has two members, so the four loose distinctions make four offshoots; each has p = 1, F = 2, its
parent's count 3 ≡ 0, target 1, s = 1, four places. Round 2: two groups, the two offshoots of each start knot; each join has
p = 2, F = 1, parents' count 4 ≡ 1, target 2, s = 2, five places; each of the four offshoots has two usable loose places left
and makes two offshoots, each with p = 1, F = 2, target 2, s = 2, five places. New knots: 4, then 10. Under NEXT3-PLACES
(barred) the same new knots with the s distinctions barred; under NEXT3-BARRED round 1 has s = 1 barred on each offshoot and
round 2 s = 1 on each new knot.

**The planted error (0c).** After a run, one barred loose distinction is added to the first new knot x of round 2 (DH2 1.4's
order). The place rule must then be wrong exactly at: x's places to its parents, from both sides; and x's places to its
children, from the children's side. Everywhere else unchanged.

## Predictions (every one written after the scratch runs)

Marks: **check** = a check of the code (true by an argument of the note or by construction); **replication** = the scratch
count, at the same bounds, which a correct second program must reproduce; **reported** = no prediction.

| # | Prediction | Mark | Fails when |
| --- | --- | --- | --- |
| C0 | 0a, 0b, 0c, 0d hold as stated. | check | any fails |
| P1 | M1: in all 11 lone-knot cases the renaming exists under the base law, and under none of the three count forms. | check (argument 1) | a case otherwise |
| P2 | M2: under each of the ten recorded laws, every census start that reaches three parent steps has a birth whose number of places is not one more, counted in threes, than some parent's (3,348 starts kept under parity). | replication | one such start without it |
| P3 | H1: in every run of part 2 and part 3 where (a), (b′) and (c) hold, the place rule is right on every structure of the run. | check (argument 2) | a wrong place in such a run |
| P4 | H1's converse: in every run where (a) and (c) hold and (b′) fails, the place rule is wrong at some place. | check (argument 2) | such a run with none |
| P5 | Under the count forms in place counts, every run from a start where (a) fails has a wrong place at a place between two start knots. | check | such a run without one |
| P6 | Under NEXT3-BARRED with CANCEL-RETIRE (RELEASE or HOLD), the wrong places are exactly those of the note's "(c) exactly": for a knot that retires with h more barred places, h ≢ 0, its places to its parents from its own side, and from the parent's side when h ≡ 1; for a retired start knot its places to start knots, from its own side if h ≡ 1, the other side if h ≡ 2; on runs where (a) and (b′) hold. | check | a wrong place outside the set, or one inside it right |
| P7 | H3: under both barred forms, births, parents and rounds equal the base law's in every run of part 2, through the base law's last round under not-all-equal and through its closing round under parity. | check | a difference |
| P8 | The restart control: wherever the structure after round t is an allowed start, its growth as a start for 2 rounds is isomorphic to the run's structure after round t + 2; and the place rule applied to a reached arm-W structure handed in as a start is wrong at every old parent place from the new knot's side and right from the parent's side. | check (argument 1) | a difference, or a place otherwise |
| P8b | The census holds restarts: 515 of the 3,348 kept census starts are reached structures of census starts of at most four knots under some recorded law (145 to 234 by law). | replication | another count |
| P9 | The rings of part 6: the first return has period T = 2 and q = 1 under the base law; under both barred forms, with barred marks, period T · 3 / gcd(3, q) = 6. | check (given the formula) | another period |
| P10 | The knot test: every knot of part 7 passes under its run's knot law; the two parity methods agree; the decomposed not-all-equal test agrees with the direct one where both are made. | check | a failing or disputed knot |
| P11 | The census strata, census weighting: (a) on 133 of 3,348 starts of up to five knots and 804 of 82,372 of six; (b′) fails on 510, 510, 510 and 223 starts under the four waiting bases (RATION-3, CAP-3, CAP-3 with FILLERS, FLOOR1, each with waiting) and on 48, 48, 368, 462 under the four holding laws, under both knot laws; on 0 under FLOOR1 with offshoots, FLOOR1 with retiring and ordinary growth. | replication | another count |
| P12 | The usable form (the price): births by round, knots and how the run ended, against the base law. | reported | — |
| P13 | The cost under the barred forms: the share of new knots with s > 0 and the mean of s, by run. | reported | — |
| P14 | The table of the greatest difference (DH2 4.6) by start and by round; seen in scratch up to 3, so no fixed count in fives or sevens is known to be enough. | reported | — |
| P15 | The labelled shares of P11's strata. | reported, no direction predicted | — |
| P16 | The swaps (the rule for a birth whose parents differ; the closing reading): the place rule's wrong places by kind under each. | reported | — |

Counting in twos, the negative control: not run here; the least-record study's P6 already shows parent steps counted in twos
leaving confusable pairs at every distance in the finished structure of 16 knots (its results, line 34).

## Stop rule

Stop when parts 0 to 7 have their verdicts or their stated prefixes. The result reports each prediction as it is, with the
note's two arguments as the study's content and the run as their check.

## Considered and not registered

- **The guard of the one-birth-at-a-time study with the parents taken from the place rule** (the first draft's run 6, and
  the least-record study's deferred direction 3). Under the barred forms the births are the base law's and the parents the
  place rule gives are the record's, so the guard's inputs are identical by H3 and H1: the run tests plumbing, and cannot
  fail without a planted negative. Left to that deferred direction.
- **The two exception requests** of the first draft (every order of births for that guard; the census of six knots grown in
  full): not asked. Condition (a) at six knots needs no growth and is in part 3; (b′) at six knots is the seeded sample.
- **The search for a ration with no parent count among its inputs** that shows the order at a fixed distance from lone
  starts: parked as an idea, in one sentence in the note; not designed.
- **The brief's literal wording** (the fresh count one more): a sentence in the definitions (DH2 3.4); not a law here.

## Words

"Shown within d", always with its d; "count in threes" ("mod" in formulas only); "parent steps" (the record's
"generation", quoted once, DH2 0.3); "new knot"; "value" kept for the stamp; arms R (recorded) and W (writes); the law names
NEXT3-PLACES (usable), NEXT3-PLACES (barred), NEXT3-BARRED and the stated variant NEXT5-BARRED; "the guard of the
one-birth-at-a-time study" (the record's "brood guard", cited once here). Not used: "held by the structure" for this result,
"residue", "counter", "layer", "congruent", "inherit".


# (5) The drafter's account of the changes

# Changes from the first drafts to the second versions, item by item of the advisor's answer

`study/descent_advisor/answer.md`, sections 1 to 14. "Applied" means applied as worded; otherwise the change or the reason
is given. Files: `note_v2.md`, `definitions_v2.md` (DH2), `preregistration_v2.md` (PR2), `history_lines.md`.

## 1. Is (H) an answer or a price?

- It is a price; moved, not removed. **Applied** (note: verdict line; owner sentences).
- The verdict line "shown in the structure's places; written by the law; relative to a start supplied flat". **Applied**.
  "Held by the structure" is used for this result nowhere; the owner's question keeps it in quotation.
- Reading the law's text is too weak; V1 not exhaustive. **Applied**: V1-V3 replaced by the inputs, factoring and restart
  tests, each with exhaustive answers (note, "The three tests"). The advisor's example ration (as many fresh as the parent
  has places, plus one) answers "written" under the inputs test.
- What "made" would require (four items). **Applied** (note).

## 2. BARRED-MOD3

- It is the stamp of A247 in unary in distinctions no birth takes; say so; H3 is its proof. **Applied** ("the stamp of A247
  written in barred distinctions").
- Its write rule without FILLERS is the stamp's word for word. **Applied.**
- It moves condition (a) into "a start has no barred place"; V3 (b) is supplied. **Applied** (DH2 1.2 states it; note).
- "Do nothing" is false outside births; list what changes. **Applied** (live for good; allowed states under parity and
  not-all-equal; the closing exception; SD's sameness and periods), with the cost measured in scratch (share of new knots
  with s > 0: 0.62 under NEXT3-PLACES (barred), 0.78 under NEXT3-BARRED). One wording changed: the advisor wrote "Under
  BARRED-MOD3 the first birth has s = 1"; that holds without FILLERS; with FILLERS the first birth leaves a barred filler or
  s, so the conclusion (the exception never applies) stands.
- The knot test is true by construction for these forms. **Applied** (PR2 P10, a check of the code).
- USABLE is the price, not the count doing something. **Applied.**
- Neither form at the centre; the value is used only in run 6. **Applied** (the note's content is the two arguments).

## 3. M1, the reason

- Sound; exclude NO-OFFSHOOT. **Applied.**
- DH 5.2 "to itself": the distinction is fixed, the places exchanged. **Applied** (DH2 5.2).
- DH 5.1 "the least a" against 11 cases. **Applied** (DH2 5.1: "a number a with F(1, a − 1) = a − 1").
- Scope one start per ration; "every ration of p and D alone" too wide. **Applied**: withdrawn (note).
- The restart lemma. **Applied with a statement of "allowed start"** (DH2 1.2) and with the drafter's own check (below).
- The two-knot named start as an instance. **Applied**; confirmed in scratch: it is the lone three-place knot after its first
  offshoot under ORD, CAP-3, FLOOR1, FLOOR0 and ONE-FEWER.
- Every positive result must name a class not closed under restart; (a) is that class. **Applied.**
- L3 stronger. **Applied.**
- "A later stage breaks the symmetry" true within one known start; what refutes "from then on". **Applied**, and quantified by
  the check below.
- A registered family (one exchanging renaming per round on a start that is not a lone knot). **Not applied**: the
  parents-from-holders record already has such pairs at later rounds (115 on the two-knot start under FLOOR1 with offshoots,
  49 on the ring of five under RATION-3 with waiting, its `whole_pairs.json`), and the note cites them; a new registered
  family would cost an engine part for a statement the record holds. Left to the advisor.

### The restart lemma: the drafter's check, as the coordinator asked

- **Can the conclusion fail?** No, once both members are in the population: it needs only that a structure reached by a
  birth has a parent place (its last new knot's), which is a place between two start knots when the same structure is a
  start. A counterexample can only be to hypothesis (R3), "a reached structure is an allowed start".
- **The search** (`w3_restart.py`, eight laws, six small starts; structures after complete rounds 1 to 3 of at most 40 knots,
  and the half-built structures of the start and a prefix of round 1's new knots of at most 12 knots). Results in
  `out/w3_all.txt`. The run was cut at 20 minutes by the drafter (its renaming search is slow on the symmetric 40-knot
  structures): 26 of the 48 cases of law and start finished, 176 structures. Findings:
  - 173 of the 176 are allowed starts; the 3 that are not carry a barred distinction (FLOOR1 with retiring). By the
    definitions the other ways to fail are FILLERS barring and the closing exception (a knot of fewer than three places).
  - **Most reached structures that are allowed starts have an order recoverable within their own start's history**: no
    renaming of the whole structure exchanges a parent place with a place that is not one, on 148 of the 173 (the other 25
    have such a renaming, among them the lone-knot structures of M1 that were in range). So the lemma is about
    populations that include restarts; on the population of one start's histories alone it says nothing, and the record's
    other results (the parents-from-holders study's growing least distance) carry that case.
  - The restart grows as the continuation (same signature) in 68 of 68 tests (structure after round t handed in as a
    start, 2 more rounds, against round t + 2).
  - **The coordinator's question** ("a recorded law and a reached structure that is an allowed start but whose reaching
    history is recoverable from the structure") has many positive instances inside one start's history, and none once the
    restart is admitted to the population; they do not refute the lemma, they show its population-relative force.
  - **The census holds restarts.** 515 of the 3,348 census starts are themselves reached, after one or more of round 1's
    births, from a census start of at most four knots under some recorded law (145 to 234 by law; `w6_census_restart.py`).
    So the lemma bites on the record's own population.
- **Where "allowed start" needs a statement.** SD lines 11-18 define a start but say only implicitly that a start carries no
  barred distinction ("a loose distinction is usable unless the law has barred it"). Every positive result rests on such a
  statement: condition (a), or "a start has no barred place". Laws with three or more holders would also need to say whether
  a start may hold a distinction three times.
- **One thing the advisor's statement leaves implicit**: its extension to every later structure needs a round that reads only
  the present structure (SD's does). Laws that read the record of parents (the fold study's STEPS-k, the guard of the
  one-birth-at-a-time study) do not continue a restart as they continue the run; the lemma about the one structure still
  holds there.

## 4. L3, H1, H3, H5, H6

- L3: exclude closing births. **Applied.**
- M2: reword; disclose "reaches a knot of generation 3" as chosen after scratch. **Applied** ("three parent steps").
- H1 true as a conditional under RELEASE and HOLD; one c per connected piece; (b) sufficient not necessary; (b) is a sketch
  under RELEASE and an observation on 16 runs under HOLD; (b) decided from the record. **Applied, and strengthened**: (b′)
  "parent steps agree counted in threes" replaces (b), with an exact converse (given (a) and (c), the place rule is right on a
  run exactly when (b′) holds). **And a finding**: the observation under HOLD does not extend to the census: parents at
  different parent steps on 48, 48, 368 and 462 of 3,348 starts under the four holding laws (history lines).
- (c) counted in threes, with the exact effect of h. **Applied**; the effect checked exactly on 16 runs (`w5_retire.py`:
  predicted and actual wrong places equal on every run; h ≡ 0 did not occur).
- H3's three notes (the exception off from the first s > 0; births match through the base's closing round; SD's kinds
  differ). **Applied.**
- DH 3.2 step 5 defect (a two-place knot). **Applied** as the advisor wrote it (F_B as if no closing, s recomputed), with
  the old reading kept as the swap.
- H5 sound; run 4 a check of the code. **Applied.**
- The not-all-equal bound stated three ways. **Applied**: one bound for the test (every structure the runs make, at most
  3,000 knots, by the fold study's exact decomposed method); the direct method only as a check of the code (knots of at most
  7 places in structures of at most 150 knots).
- H6: "first failing birth" depends on the order of joins. **Applied** (round and multiset).

## 5. The start's values

- The honest statement (works from a start that already agrees; supplied). **Applied.**
- 133 of 3,348 with its family and weighting and the counts by size. **Applied**; and (a) exactly at six knots: 804 of
  82,372 kept (scratch, seconds), labelled share 0.5% (1.7% at up to five knots).
- Counting in fives is the least-record result moved; not a law. **Applied** (DH2 3.3, a stated variant).
- The table of the greatest difference by start and round. **Applied** (PR2 part 3, P14); scratch: a greatest difference of 3 seen
  under every waiting law with RELEASE except ORD with waiting, and under three of the four holding laws.
- The history line on the 510 starts. **Applied** (`history_lines.md`), widened to the holding laws.
- The discrepancy (1,753 against 1,243). **Resolved**: the first fives run left out the three added rules; with them,
  1,727 of 1,753.

## 6. H7

- A sentence and one cheap check, not a ticket. **Applied** (PR2 part 6).
- The period formula 2 × 3 / gcd(3, q). **Applied** as T · 3 / gcd(3, q); seen with descent checked on the rings of five
  and seven under the two and three added rules (T = 2, q = 1, period 6 under both barred forms).
- The honest sentence. **Applied**, nearly word for word.
- The note for the count-of-returns study. **Applied.**

## 7. What is left open

- Three or more holders is not the one place left; the restart lemma covers them. **Applied.**
- "Made" with nothing supplied closed by argument once refereed. **Applied** (note).
- What stays open is relative; the smallest honest search; value low, park it. **Applied**: one parked sentence, not designed.

## 8. Sizes

- Ask for neither exception. **Applied.**
- Run 6 tests plumbing. **Applied**: not registered; considered and left to the least-record study's deferred direction 3.
- Six-knot census: (a) exact, (b) a seeded sample of about 3,000. **Applied** (scratch: 493 of 3,000 under the study's
  waiting law).

## 9. Weighting and numberings

- The labelled weighting as the swap, as a reweighting, no direction predicted. **Applied.**
- "Argued for every numbering; no difference found in N runs". **Applied**, N = 89,910.
- An exact isomorphism test on the small starts. **Applied** (PR2 0d).
- The miscount ("five starts"). **Applied**: four starts of at most six distinctions and five others.

## 10. The definitions

- Two meanings of "recovers". **Applied** (DH2 4.2, 4.3).
- Name the population every time. **Applied.**
- "Shown within d" unchanged by renaming. **Applied.**
- The parent-closed part (a construction; which of the least-record study's half-built structures are such parts; marks as
  of when). **Applied.**
- The knot law of each run; the 32 set aside under parity. **Applied**: every run names its knot law; the 32 are set aside
  under parity only; none fails under not-all-equal.
- Parents that differ: the swap replaced by "c and c + 1 give c + 2". **Applied.**
- FRESH-MOD3 a sentence. **Applied** (DH2 3.4); P4 removed.
- H2 has no defined set. **Applied**: H2 removed; replaced by the converse of H1 (P4), the start-place prediction (P5) and the
  exact set under retiring (P6).
- Smaller defects (DH 2.2 garbled; (c) for start knots; "inherit that difference"; USABLE with FILLERS). **Applied.**

## 11. The predictions

- True by construction marked as checks; replications marked. **Applied** (PR2 marks).
- Undecidable H2 and P16. **Applied** (H2 removed; P16 reported).
- P8 and P10 over-pinned. **Applied**: P8 is now PR2's P6 (the exact set); P10 is now PR2's P12, reported with no
  prediction (the price).
- New by run: HOLD bases, swaps, rings 13 and 15, run 6. **Applied with one change**: HOLD bases and swaps are in; two rings
  with descent (as the coordinator's list says), not 13 and 15; run 6 not registered.
- Missing items: the restart control (PR2 part 5, P8); the population of each claim; the knot test on the census structures
  (stated as argued, tested on parts 2 and 6); the cost (P13); counting in twos (a sentence); "written after scratch".
  **Applied.**

## 12. Words

- All applied: "shown within d" with its d; "count in threes"; "parent steps" with the record's "generation" quoted once;
  "value" for the stamp only; "new knot"; arms R and W; NEXT3-PLACES (usable), NEXT3-PLACES (barred), NEXT3-BARRED,
  NEXT5-BARRED; "the guard of the one-birth-at-a-time study". The breaches listed are gone from the second versions (searched:
  "generation" appears only in quotation; "counter", "layer", "congruent", "inherit", "came out", "one side of every" do
  not appear).

## 13 and 14

- The owner sentences. **Applied, adjusted**: the 510 is "under the waiting law of the least-record study" (it is 510 under
  three of the four waiting bases and 223 under FLOOR1 with waiting), and the holding counts are added.
- The verdict (redesign smaller: a checked note with one confirming run). **Applied.**

## Anything in the advisor's answer found wrong

- Nothing material. Two small points: the first birth under BARRED-MOD3 has s = 1 only without FILLERS (section 2; the
  conclusion stands); and the advisor's (b)-under-HOLD "observation on 16 runs" is right as stated but does not extend: the
  census shows it fails (section 4 above). The restart lemma's conclusion is right; its force is population-relative, which
  the advisor's section 3 implies ("on a population holding both") and the check makes explicit.


# (6) The drafter's report

## Report: descent study, second version (checked note plus one confirming run)

The rewrite is done as you asked, and checking it turned up two things you should know first:
- **Holding is not as safe as the least-record study says.** Under its four holding laws, parents at different numbers of parent steps occur on 48, 48, 368 and 462 of 3,348 census starts. Its own sixteen holding runs had none, and my engine also gives none on those sixteen. It belongs in the same history line as the 510.
- **The census itself holds restarts.** 515 of the 3,348 census starts are themselves structures reached from a smaller census start under some recorded law. So the restart lemma applies to the record's own population.

Everything was written only in my scratch folder, nothing in the repository, and none of my processes is still running.

**Files.** All are in `/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/7d6e7b9e-634d-564b-a5b8-21bd756b246b/scratchpad/descent_survey/`, and the first versions are kept:
- `note_v2.md`
- `definitions_v2.md`
- `preregistration_v2.md`
- `history_lines.md`
- `changes_v2.md`
- the new scripts `w1_census.py` to `w6_census_restart.py`, with outputs in `out/`

The confirming run is sized at about 25 minutes on 6 processes, from measured rates. A part not finished in 30 minutes is cut to its prefix.

**Advisor items not applied as worded:**
- **Registered family of renamings (section 3).** I did not register one exchanging renaming per round on a non-lone start. The parents-from-holders record already has such pairs at later rounds: 115 on the two-knot start, 49 on the ring of five. The note cites them.
- **Rings 13 and 15 (section 11).** Not registered; your item 7 asks for two rings with descent, and those two are in.
- **(b) under holding.** The advisor calls it "an observation on 16 runs", which is right as stated. Applied with the stronger census result above.
- **H1, strengthened.** "Parent steps agree counted in threes" replaces "equal parent steps". Given that the start's meeting knots agree and counts never change, the place rule is right on a run exactly when that holds.
- **Wording I corrected.** The advisor wrote "first birth has s = 1" (s is the number of added distinctions). That is true only without the extra FILLERS; with it, the first birth leaves a barred filler or the added distinction, so the conclusion stands.
- **Nothing material in the advisor's answer was found wrong.**

**My check of the restart lemma:**
- **The conclusion cannot fail** once both the reached structure and its restart are in the population. A counterexample can only be to the hypothesis that a reached structure is an allowed start.
- **"Allowed start" needs a statement**, which I added (definitions, 1.2): knots of at least three places, one or two holders per distinction, no barred distinction. The shared definitions imply the last point but never say it.
- **The search** covered eight laws and six small starts. It was cut at 20 minutes, with 26 of 48 cases of law and start finished and 176 reached structures tested:
  - 173 of the 176 are allowed starts. The 3 that are not carry a barred distinction (FLOOR1 with retiring).
  - Growing a restart gave the same signature as continuing the original run in 68 of 68 tests.
  - **Your counterexample question has many positive cases, but none refutes the lemma.** 148 of the 173 allowed starts have an order recoverable within their own start's history alone. None stays recoverable once the restart is in the population.
  - **The lemma's force is about populations.** A positive result must name a class of starts that no reached structure belongs to.
- **The census holds restarts.** 515 of the 3,348 census starts are reached structures, after one or more of round 1's births, of a census start of at most four knots: 145 to 234 by law. This is registered as prediction P8b.
- **One limit.** Extending the lemma to every later structure needs a round that reads only the present structure, as the shared definitions' round does. Laws that read the record of parents do not continue a restart the way they continue the run.

**Resolved counts for item 5.** All are from scratch runs, for the confirming run to check (P11).
- **Definition.** On the census, 3,348 starts of up to five knots, each counted once up to isomorphism, kept where every start knot passes the parity test. Grown in complete rounds through 8 rounds or 3,000 knots. A start is counted when some new knot has two parents at different numbers of parent steps.
- **Same counts under both knot laws.**

| Law | Starts counted (of 3,348) |
| --- | --- |
| RATION-3, waiting (the least-record study's law) | 510 (19.3% labelled) |
| CAP-3, waiting | 510 |
| CAP-3, waiting, FILLERS | 510 |
| FLOOR1, waiting | 223 |
| FLOOR1 offshoots; FLOOR1 retiring; ordinary growth | 0 |
| The four holding laws | 48, 48, 368, 462 |

- **The discrepancy.** The four waiting bases are 1,753 runs. My earlier 1,243 left out CAP-3 with FILLERS. Counting in fives is right on 1,727 of the 1,753; the other 26 have a parent three parent steps above a child.
- **Six knots, seeded sample of 3,000:** 493 counted.
- **Proposed reading:** a Narrowing, not a Block. The published sentence "the one place it fails is the start built so" is true of the study's twenty registered pairs, not of the laws.

**Section 13's sentences for the owner, adjusted:**
- "Under the recorded laws nothing the structure shows gives the order. A lone knot and its first offshoot are exchanged by a renaming. More generally, a structure reached by a birth can itself be handed in as a start, and then the same places have no parents. 515 of 3,348 census starts are such structures."
- "If we write a ration that uses the parents' place counts and adds 0, 1 or 2 distinctions, each new knot's count is one more, counted in threes, and a knot can compare counts across one shared distinction. This is the stamp of A247 moved into the law. With the added distinctions barred, no birth changes, which is what shows it is a stamp."
- "It works only from a start whose meeting knots already agree, or by the convention that a start has no barred place. That is 133 of 3,348 census starts of up to five knots, each once up to isomorphism, and 804 of 82,372 at six knots. It works only where parents are equally many parent steps from the start, counted in threes. That fails on 510 of 3,348 census starts under the least-record study's waiting law, and on 48 to 462 under the holding laws."
- "So the supplied record is moved, not removed. The order is relative to a start supplied flat. No pattern counts; nothing uses the count; nothing here is a clock."
- "All of this was seen in scratch before the claim was written. The confirming run checks it with a second program and tests little the arguments do not already give."

**Not registered, as you asked:** the guard of the one-birth-at-a-time study using recovered parents (it only tests plumbing, since its inputs are identical by construction), and both exception requests. The search for a ration that shows the order without using parent counts is parked in one sentence in the note.

# (7) The proposed history lines

# Proposed history lines: the least-record study and assumption A247 (second version, 2026-11-25)

Proposed by the design helper of `DESCENT-HELD-20261125-001`; nothing is entered in the repository. **Every count here is
from the helper's scratch prototype and is to be checked by the confirming run (`preregistration_v2.md`, part 3, P11)
before anything is entered or corrected.** The prototype's round was checked equal, names included, to
`lr_core.own_round` of `LOCAL-ROUND-20261123-001A` on that study's twenty pairs through 8 rounds, and it reproduces the
least-record study's sixteen holding runs (0 births with parents at different parent steps).

## What the least-record record says

- `research/LEAST-RECORD-20261124-001A/results.md` line 12-13: "The one place it fails is the start built so that a start
  knot waits while a knot it meets acts; there five values are enough." Line 30 (P2): the condition "fails on one registered
  start only, the one built to break it". Line 37 (P9): "Under holding every birth's parents still had equal generations, in
  all 16 runs through six rounds".
- Its decision (`research/LEAST-RECORD-20261124-001/decision.md` line 20-21, 24): "Where it fails: On the one start built
  so ..."; "Under holding it still worked on the sixteen runs tried".
- The guide, lesson 9.3 (`publication/knotlab/INTUITIONS.md` lines 4319-4330): "on the one start built so that a start knot
  waits while a knot it meets makes its births, it fails, and five values repair it there."
- A247 (`docs/ASSUMPTIONS.md` line 5322): "a start in which a start knot waits while a knot it meets acts (the stamp fails on
  the one such start tried, and counting in fives works there)".

Each statement is true of the populations it names (twenty registered pairs; sixteen holding runs). Read as statements about
the laws, they are too narrow, as below.

## The count, defined exactly

- **Starts.** The census of `COPYING-PARTS-20261123-001A` (`cpcensus.py`, imported read-only): every connected graph of
  networkx's atlas on 1 to 5 vertices; a loose count 0 to 3 on each knot with degree plus loose count at least 3 and at least
  one live knot; each kept once up to the graph's automorphisms; one shared distinction per edge. 3,380 starts; **3,348 kept**,
  those whose start knots all pass the parity knot test (both methods of `knots.py`); under not-all-equal none fails.
- **Laws.** SD's complete round (`research/RING-IN-BALANCE-20261123-001/definitions.md` steps 1-8), two holders, no taking
  rule, with RELEASE unless HOLD is named: (RATION-3, CANCEL-WAIT), the least-record study's waiting law; (CAP-3,
  CANCEL-WAIT), the two added rules; (CAP-3, CANCEL-WAIT, FILLERS), the three added rules; (FLOOR1, CANCEL-WAIT); and,
  reported beside them, (ORD, CANCEL-WAIT), (ONE-FEWER, CANCEL-WAIT), (RATION-4, CANCEL-WAIT), and the four holding laws of
  `GUARD-CAP-AND-HOLD-20261124-001` (CAP-3 or RATION-3 with waiting, FLOOR1 with retiring or with offshoots, each with HOLD).
  Each under parity and under not-all-equal (the knot law sets the closing exception only).
- **Bounds.** Grown through 8 rounds, or until the first round after which the structure has more than 3,000 knots, or until
  a round makes no birth or stalls.
- **The count.** A start is counted under a law when **some new knot of the run has two parents whose parent steps differ**
  (parent steps: 0 for a start knot, one more than the greatest of the parents' for a new knot; the least-record study's
  "generation"). Equivalently, the three-valued stamp of A247, written one more than the parents' and read by "a parent is
  exactly one less, counted in threes", is wrong at some place of the run.
- **Weighting.** The census weighting: each start counted once (up to isomorphism). The labelled weighting (each numbering
  of the knots counted once, weight n!/|Aut|) is given beside.

## The counts (scratch; identical under parity and not-all-equal)

| Law | Starts counted (of 3,348) | Labelled share | First round it happens | Greatest difference (parent steps, child less parent) | Counting in fives right on |
| --- | --- | --- | --- | --- | --- |
| RATION-3, waiting (the study's law) | **510** | 19.3% | round 2: 69, 3: 426, 4: 14, 5: 1 | 2 on 501, 3 on 9 | 501 |
| CAP-3, waiting | 510 | 19.3% | as above | 2 on 502, 3 on 8 | 502 |
| CAP-3, waiting, FILLERS | 510 | 19.3% | as above | 2 on 502, 3 on 8 | 502 |
| FLOOR1, waiting | 223 | 7.9% | 2: 64, 3: 150, 4: 9 | 2 on 222, 3 on 1 | 222 |
| ORD, waiting | 155 | 5.8% | 2: 86, 3: 46, 4: 19, 5: 4 | 2 on 155 | not run |
| ONE-FEWER, waiting | 351 | 12.9% | 2: 64, 3: 166, 4: 99, 5: 20, 6: 2 | 2 on 346, 3 on 5 | not run |
| RATION-4, waiting | 400 | 15.1% | 2: 75, 3: 300, 4: 20, 5: 5 | 2 on 377, 3 on 23 | not run |
| CAP-3, waiting, HOLD | 48 | 1.5% | 2: 48 | 2 on 44, 3 on 4 | not run |
| RATION-3, waiting, HOLD | 48 | 1.5% | 2: 48 | 2 on 48 | not run |
| FLOOR1, retiring, HOLD | 368 | 12.8% | 2: 314, 3: 53, 4: 1 | 2 on 303, 3 on 65 | not run |
| FLOOR1, offshoots, HOLD | 462 | 16.4% | 2: 427, 3: 35 | 2 on 417, 3 on 45 | not run |
| FLOOR1 offshoots; FLOOR1 retiring; ORD with STALL (RELEASE; parity) | 0 | 0 | — | — | — |

- **By size**, under the study's law: 21 of the 197 four-knot starts and 489 of the 3,128 five-knot starts; none of three
  knots or fewer.
- **The least-record study's condition** (a start knot waits in a round in which a start knot it meets is a parent of a
  birth) fails on 1,474 starts under each RELEASE waiting law; every counted start is among them. Under the two holding laws
  without waiting it never fails, yet 368 and 462 starts are counted: there a knot gives in more than one round, and the
  advisor's equal-steps sketch, which assumes RELEASE, does not apply.
- **Six knots** (scratch, a sample of 3,000 of the 82,372 six-knot starts kept under parity, in the order of
  `random.Random('DESCENT-HELD-20261125-001|six|v2')`'s shuffle of the census order): counted on 493 under each of the three
  laws with CAP-3 or RATION-3 and waiting, and 184 under FLOOR1 with waiting.
- **Counting in fives** ("a parent is one or two less, counted in fives", the stamp written one more than the cyclically
  greatest parent's): right on every place on 1,727 of the 1,753 counted runs under the four waiting bases; the other 26
  have a parent three parent steps above a child, where fives cannot work (the least-record study's own rule: count in
  2d + 1 for a greatest difference d).

## The discrepancy the advisor found, resolved

The first draft said counting in fives repairs "1,225 of 1,243 such runs". The four waiting bases give 510 + 510 + 510 + 223
= **1,753** counted runs. The 1,243 left out the three added rules (CAP-3, waiting, FILLERS): the first fives run covered
RATION-3, CAP-3 and FLOOR1 with waiting only (510 + 510 + 223 = 1,243, right on 501 + 502 + 222 = 1,225). The added run of
the three added rules gives 502 of 510. **Corrected figure: 1,727 of 1,753.**

## Proposed history lines

**On `LEAST-RECORD-20261124-001` (its result and decision), for its next reading and its referee:**

> 2026-11-25 · Narrowed, not a block (proposed by `DESCENT-HELD-20261125-001`, scratch, to be confirmed by its run). The
> result's "the one place it fails is the start built so" is true of the twenty registered pairs. On the census of 3,348
> starts of up to five knots (each counted once up to isomorphism), grown through 8 rounds or 3,000 knots, parents at
> different parent steps occur on 510 starts under the study's waiting law (RATION-3 with waiting), and so the three-valued
> stamp is wrong somewhere there; counting in fives is right on 501 of them; the other 9 need sevens. Under the study's
> three laws without waiting it occurs on none. Under holding, "parents still had equal generations" is true of the sixteen
> runs tried; on the census it fails on 48 to 462 starts by holding law (368 and 462 where no knot waits: holding lets a
> knot give in more than one round). Verdict: narrowing of P2's and P9's reach, not of what was run.


**On A247, history:**

> 2026-11-25 · `DESCENT-HELD-20261125-001` (scratch, to be confirmed): the stamp's failure is not one built start. Under
> the waiting law of the study that adopted it, parents at different parent steps occur on 510 of 3,348 census starts of up
> to five knots (each once up to isomorphism; 19% with each numbering of the knots counted once), from round 2; under the
> laws without waiting on none; under holding on 48 to 462. Counting in fives is right on 1,727 of 1,753 such runs under
> the four waiting laws tried; a greatest difference of three parent steps is seen, so no fixed count is known to be
> enough. The same study found the stamp can be written in barred distinctions with no birth changed (its note, argument
> 2). Status unchanged.

**Correction-log question for the thread:** whether the summary sentence on knotlab and the guide's lesson 9.3 ("on the one
start built so ... it fails") need a Narrowing entry in `docs/CORRECTIONS.md` once the confirming run reproduces the count.
The helper's reading: yes, a Narrowing (the published sentence names the only failure; the census has many), not a Block
(the stamp's result on its registered population stands).


# (8) The earlier study: its result note

# How little has to be written for a knot to find its parents? Result

Ticket `LEAST-RECORD-20261124-001A` (sub-goal B325 after its first step; goals G5 with G18), 2026-11-25. Computed with the
earlier search's program, extended by its author from the frozen text; scientific referee pending.
[Pre-registration](preregistration.md) ·
[code and its recorded readings](../../experiments/LEAST-RECORD-20261124-001A/LEAST-RECORD-20261124-001A-E001_least_record/deviations.md) ·
[the thread's own check](../LEAST-RECORD-20261124-001/checks/thread_checks.txt)

**Three values are enough. If every new knot writes one of three values, one step on from its parents' value, any knot
can tell its parents from its children by comparing values with the knots it meets, looking one step and no further. This
held on every structure reached, half-built ones included, under all four laws, and under holding on the structures tried.
No stamp of two values that was tried does the same under every law. The one place it fails is the start built so that a
start knot waits while a knot it meets acts; there five values are enough. The stamp is written by hand, and it is itself
the order of descent cut down to three values: the result says how small the record can be, not that the growth supplies
it.**

## What was done

A **stamp** is one value written on each knot. Ten stamps were tried, from two values to the full generation, each added
to what a knot sees within d holder steps, and the earlier search was rerun: are there still two places, one leading to a
parent and one not, that look alike? A knot's **generation** is 0 for a start knot and one more than its parents' for a
new knot.

## Verdicts

| # | Verdict | What was found |
| --- | --- | --- |
| Checks | Hold | The earlier checks still pass with no stamp; a stamp that is the same everywhere changes nothing; a hand-built structure of five knots comes out as stated; a stamp changed four steps away is unseen at distances 1 to 3 and seen from 4, 60 times of 60. |
| P1 | Holds | Wherever no start knot waits in a round in which a start knot it meets acts, every birth's parents have equal generations: none of 34,243 births is an exception. With the generation counted in threes shown, the rule "the other holder is a parent exactly when its stamp is one less" gives every place of both populations under all four laws (for example 807,124 of 807,124 under a fixed three with waiting). |
| P2 | Holds | That condition fails on one registered start only, the one built to break it. There a round-2 knot has parents of generations 0, 1, 1 and 1, and the rule reads its place to the start knot wrong from both sides. |
| P3 | Holds (a check) | The full generation gives every place everywhere. |
| P4 | Holds (a check) | "Has no usable loose place" changes nothing: every look already shows it. |
| P5 | Holds | "Has made a birth" leaves a start knot and a new offshoot hanging off the same knot exactly alike, at every distance, and changes nothing on the complete rounds of the proved case. |
| P6 | Holds | The generation counted in twos leaves look-alike pairs at every distance in the finished structure of 16 knots, and at distances 1 to 5 at round 12 where a short knot makes offshoots. |
| P7 | Reported | The table below. |
| P8 | Reported: none | No stamp of two values in the table recovers the parents under every law. Two do under one law only. |
| P9 | **Fails** | Under holding every birth's parents still had equal generations, in all 16 runs through six rounds, and the three-valued rule gave every place. The advisor had leaned the other way. |

## The table of costs

The least distance at which a rule recovers every parent, on both populations together, where the condition of P1 holds.
"None" means look-alike pairs remain, or the only distances without them are ones where every look reaches a start knot or
a member, which is not counted.

| Stamp | Values | Who writes it | Short knot makes offshoots | Short knot retires | Fixed three, waiting | Ordinary growth |
| --- | --- | --- | --- | --- | --- | --- |
| Nothing | 1 | — | none | none | none | none |
| Has no usable loose place | 2 | nobody: it is visible | none | none | none | none |
| Has made a birth | 2 | the birth, on an old knot | none | none | none | none |
| Has two or more parents | 2 | the new knot, from its own birth | none | none | none | none |
| Is a start knot | 2 | comes with the start | none | 2 | none | none |
| Generation counted in twos | 2 | the new knot, from its parents' stamps | none | 2 | none | none |
| **Generation counted in threes** | **3** | **the new knot, from its parents' stamps** | **1** | **1** | **1** | **1** |
| Has made a birth, and is a start knot | 4 | both | none | 2 | none | none |
| The number of its parents | grows with the law | the new knot, from its own birth | 2 | 2 | none | none |
| The full generation | grows with the growth | the new knot, from its parents' stamps | 1 | 1 | 1 | 1 |

- **The three-valued stamp is the only small one that works everywhere**, and it works at the least distance there is. The
  places it was checked on are not all near the start or the live roster: between 38,910 and 95,112 of them, by law, see
  neither.
- **A new knot can write it knowing only its parents' stamps.** No old knot is rewritten and nothing about the start has
  to be known beyond "a start knot is 0".
- **The number of a knot's parents** is enough at two steps on structures built by complete rounds under the two laws with
  "just enough for three places", but not on every half-built structure, and not under the other two laws.
- **Smallest failures.** With nothing written, or with any of the first three two-valued stamps: two knots, a knot and
  its first offshoot (or three, with a second start knot). With the generation counted in twos: the finished structure of
  16 knots.

## Where it fails, and what works there

On the start built so that a start knot waits while the knots it meets act, that start knot later joins knots one
generation younger. The join's parents have generations 0 and 1, its own is 2, and "one less, counted in threes" reads its
place to the start knot as leading to a child. The greatest difference between a child's generation and a parent's is 2
there, so counting in fives works, with the rule "a parent is one or two less". In general a count modulo one more than
twice the greatest such difference works at one step.

## What this does and does not show

- **It shows how small the record can be.** The earlier study needed, for each shared place, which holder was the parent.
  One of three values per knot carries the same, wherever the knots that join were made together.
- **It does not show that the growth supplies the stamp.** Someone writes it. And the stamp is not something other than
  the order of births: it is that order, cut down to three values.
- **It does not show that two values cannot work.** The five two-valued stamps tried do not. A cleverer one, read over a
  longer distance, is not ruled out.
- **By construction, not run:** a guard that recovers the parents exactly can stand in for the written record in the
  one-birth-at-a-time laws and decide the same. That was not run as its own test.

## Deviations and limits

- **A count that added nothing (the thread's and the advisor's design).** The second guard count, for looks holding no
  place between two start knots, always equals the first: a look with no start knot cannot hold such a place. The engine's
  author reported a variant beside it.
- **One law under holding could not count.** Under a fixed three with waiting and holding, every look reaches a start knot
  or a member at every distance, so no rule there is counted, although the full generation's rule is right on every place.
- **P9 was a lean, not a prediction with an argument.** On other starts or longer runs under holding, parents of unequal
  generations may still occur; none did here.
- **The 28 readings** of the engine's author are recorded with the code. The condition is read as: a start knot waits in a
  round in which a start knot it meets is a parent of a birth.
- **Six processes took 10 to 25 minutes**, within their memory caps (long-running row `LEASTREC-RUNS`).
- **Everything is finite:** the structures of the earlier search (twenty starts and laws, to about 2,000 knots or twelve
  rounds, and the half-built structures of twenty sampled orders), and sixteen runs under holding to six rounds.
- **Evidence class:** exact computation; an argument for why parents have equal generations (a proof sketch by the
  advisor, in the pre-registration); the thread's own check of the rule on ten grown structures.
- **Scaffolds:** every stamp is supplied, and so is who writes it. Ten were tried; the result is the table.


# (9) The shared definitions (SD), with line numbers

     1	# A ring in balance: definitions shared by the three studies
     2	
     3	Epic `RING-IN-BALANCE-20261123-001`, 2026-11-23. Frozen with the three pre-registrations, before any of the study's code is
     4	written. Tickets A, B and C cite this file and add only what is their own. The canonical K1–K3 test is unchanged. Words are the
     5	glossary's (Intuitions guide). The growth records' "junction" is a knot and their "growing end" is the live roster. Their
     6	"witness" is here a **common knot**, their "witnessed set" a **met set** and their "adjacent" **joinable**, because the glossary
     7	keeps witness for a helper variable and graph theory uses adjacent for what the program calls meeting.
     8	
     9	## Structure
    10	
    11	- A **structure** is a finite set of knots, each holding a set of distinctions, its **places**. A distinction has one or two
    12	  **holders**. It is **loose** with one holder and **shared** with two. Every knot of a start has at least three places, and so
    13	  has every new knot except one that receives no fresh distinction (below).
    14	- Two knots **meet** when they share a distinction. A knot is **live** while it holds a loose distinction and **dead** otherwise.
    15	- A **start** is a structure given before any birth, written as its list of knots, each a list of distinction numbers (the
    16	  records' stars).
    17	- A loose distinction is **usable** unless the law has **barred** it: a barred distinction stays loose and is never taken by any
    18	  birth. (The Intuitions guide and the site call a barred distinction "never used".)
    19	
    20	## The live roster
    21	
    22	- The **members** of the live roster are the knots holding at least one usable loose distinction. Write h(u) for the number of
    23	  usable loose distinctions member u holds and k(u) for the number of barred ones. A knot holding only barred distinctions is
    24	  live and is not a member.
    25	- A **met set** is the set of members that one knot of the structure meets, when it has at least two members. That knot is a
    26	  **common knot** of those members; it may be dead or itself a member. Two knots with the same met set count once.
    27	- Two members are **joinable** when some met set contains both. A **part** of the live roster is a connected component of the
    28	  relation joinable. The roster is **past its start** when no member meets a member (the records' positive age).
    29	- Two rosters, or two parts, are **the same** when a one-to-one renaming of members carries h, k and the family of
    30	  inclusion-maximal met sets of one onto the other.
    31	
    32	## One complete round
    33	
    34	A **law** is a knot law (parity or not-all-equal), a ration, a treatment and optional extras. One round, on real knots:
    35	
    36	1. **Groups.** First take every inclusion-maximal set of at least three pairwise joinable members that is contained in no
    37	   single met set. Then take every joinable pair that is contained in none of the sets just taken. These are the groups
    38	   ([ORDINARY-DYNAMICS-20261120-001](../ORDINARY-DYNAMICS-20261120-001/end_operator.md), "The operator on the present end", step 1).
    39	2. **Owing.** Member u owes one usable loose distinction to each group containing it. It is **short** when it owes more than
    40	   h(u). Shortness is read once, here, for the whole round.
    41	3. **Treatment of a short member.**
    42	   - STALL: if any member is short, no birth is made and the growth has stalled.
    43	   - CANCEL-OFFSHOOT: every group containing a short member is cancelled; the short member makes an offshoot from each of its
    44	     usable loose distinctions.
    45	   - CANCEL-WAIT: every group containing a short member is cancelled; the short member **waits**: it makes nothing and keeps
    46	     everything it holds.
    47	   - CANCEL-RETIRE: every group containing a short member is cancelled; the short member **retires**: it makes nothing now or
    48	     later, and its loose distinctions are barred.
    49	4. **Joins.** Each group that is kept makes one new knot, a **join**, whose parents are its members; it takes one usable loose
    50	   distinction from each.
    51	5. **Offshoots and the release rule.** A member that is not short, after paying its kept groups, makes one new knot of one
    52	   parent, an **offshoot**, from each usable loose distinction it has left. RELEASE (the default): this includes the
    53	   distinctions that its cancelled groups would have taken. HOLD: it keeps those and makes offshoots only from the rest. With
    54	   the extra NO-OFFSHOOT it makes no offshoot, and the distinctions an offshoot would have taken are barred.
    55	6. **Demand.** Count every new knot as a member holding one usable loose distinction, whatever it will receive, and keep every
    56	   old member that still holds a usable loose distinction after steps 3 to 5 (one that waits; under HOLD, one that keeps what
    57	   its cancelled groups would have taken) with what it holds. Form the groups of that roster as in step 1. The **demand** D of
    58	   a new knot is the number of those groups that contain it.
    59	7. **Fresh distinctions (the ration).** A new knot with p parents and demand D receives f fresh distinctions, each loose and held
    60	   by it alone. With q = max(D, 3 − p, 1), the ordinary count:
    61	   - ORD: f = q. CAP-k: f = min(q, k). RATION-k: f = max(k, 3 − p).
    62	   - ONE-FEWER: f = min(q, max(3 − p, 0, q − 1)). FLOOR0: f = max(3 − p, 0). FLOOR1: f = max(3 − p, 1).
    63	   - **Closing exception** (parity only, every ration): a new knot that takes every loose distinction of the structure receives
    64	     none; it may then have fewer than three places. It is then the round's only birth, nothing is barred and no old member
    65	     keeps anything. Under not-all-equal there is no exception
    66	     ([NAE-GROWTH-20261119-001](../NAE-GROWTH-20261119-001/nae_growth.md): the growth reads the knot law in this one place).
    67	8. **Extra FILLERS.** Of a new knot's f fresh distinctions, min(f, D) are usable and the rest are barred.
    68	
    69	The records' ordinary growth, the cheapest growth of lesson 8.1, is the law (ORD, STALL). **The two added rules** are the law
    70	(CAP-3, CANCEL-WAIT with RELEASE). **The three added rules** are (CAP-3, CANCEL-WAIT with RELEASE, FILLERS). They were added by
    71	hand (assumption A224, a scaffold); RELEASE is part of what was added. The pilot's program counted a short member by all its
    72	loose distinctions; the two readings agree, because a member holding a barred distinction owes exactly its usable count in
    73	the one round it acts. One barred distinction anywhere switches the closing exception off everywhere, since the exception needs
    74	a birth that takes every loose distinction there is.
    75	
    76	A distinction taken by a new knot becomes shared between its old holder and the new knot. Which of a member's usable loose
    77	distinctions goes to which birth makes no difference up to renaming.
    78	
    79	## Kinds of outcome under complete rounds
    80	
    81	A run is one start grown under one law through a stated number of rounds, or until a stated number of knots. After each round:
    82	
    83	- The growth has **stopped** when the roster has no member, **stalled** (STALL only) when a member is short, and **jammed** when
    84	  the roster has members and the round makes no birth.
    85	- A part Y of the roster after round s, past its start, **returns** at round t > s when the members after round t that descend
    86	  from Y (through parents; a waiting member descends from itself) include a part that is the same as Y. The other parts those
    87	  descendants form have **come apart** from Y, and Y **gives parts off** when there is at least one. Returns are searched with
    88	  the least s first and then the least t, and t − s is the period.
    89	- The roster is **in balance** from round s with period T when at least one birth is made in every round and the whole roster
    90	  after round t + T is the same as the whole roster after round t for every t ≥ s in the run. The structure still grows.
    91	- A part has **ended** when none of the knots descending from it is a member. It may still hold barred distinctions.
    92	- For a census a run is given one kind, the first that applies: stalled; jammed; stopped; a part returns giving parts off; a
    93	  part returns giving none off; grows to the bound with no return found.
    94	
    95	## One part at a time, and one birth at a time
    96	
    97	- **Part-round law.** A move is one complete round of one part: steps 1 to 8 applied to the members of that part alone, the
    98	  other parts left as they are (the closing exception as stated: only for a birth that takes every loose distinction of the
    99	  whole structure). The **own time** of a start knot is 0; a new knot's is one more than its parents'; and a member that
   100	  waits through a move of its part gains one. So a member's own time is the number of moves its line of descent has taken
   101	  part in. A **priority** chooses the part that moves next among the parts that would make a birth:
   102	  - ALL-IN-TURN: every part once, then again; this is the complete round.
   103	  - UNIFORM: each part with equal chance.
   104	  - BY-MEMBERS: each part with chance in proportion to its number of members.
   105	  - LARGEST: a part with the most members; SMALLEST: one with the fewest; ties uniform.
   106	  - MOST-LOOSE: a part whose members hold the most usable loose distinctions in all; ties uniform.
   107	  - LEAST-TIME: a part whose members have the least own time; ties uniform. This priority reads the history, not the structure.
   108	- **Birth-by-birth law** (the present-state reading of [ROUND-FREE-20261119-001](../ROUND-FREE-20261119-001/round_free.md), with
   109	  waiting). A move is one birth, and everything is read again after every move.
   110	  1. Form the groups of the present roster as in step 1, with every knot allowed as a common knot (ANY) or only dead knots
   111	     (DEAD). A group is **open** when no knot already made has all of its members among its parents.
   112	  2. A member is short when it is in more open groups than h(u); a short member makes nothing. Under FIRST-COME, used only to
   113	     check the engine against the record, no member counts as short.
   114	  3. Every open group with no short member is a join move. A member that is not short and holds more usable loose distinctions
   115	     than the number of open groups without a short member that contain it has an offshoot move. (Under FIRST-COME: every open
   116	     group is a join move, and a member has an offshoot move when h(u) exceeds the number of open groups containing it.)
   117	  4. The new knot receives max(3, 3 − p) fresh distinctions (RATION-3), or max(d, 3 − p, 1) (PRESENT-ORD), where d is the number
   118	     of open groups containing it immediately after its birth, the new knot counted as a member before it receives anything.
   119	     Closing exception, parity only: a move that takes every loose distinction of the structure, with d = 0 where d is read,
   120	     receives none.
   121	  5. Start knots have **generation** 0 and a new knot has generation one more than the greatest generation of its parents; a
   122	     move's generation is the greatest generation of its parents. The next move is chosen uniformly among all moves (UNIFORM)
   123	     or among the moves of least generation (BY-GENERATION), with joins first, offshoots first, or uniformly among those. The
   124	     generation is the simulator's record of who was made from whom; it is not read from the structure.
   125	  - A birth-by-birth run has **jammed at generation g** when no move of generation g or less is available and some member of
   126	    generation g or less is short.
   127	
   128	## The knot test
   129	
   130	- **Parity.** Each knot is the rule that its places have even parity. A knot with place set S passes K1–K3 in the whole
   131	  structure when the allowed states of the structure, restricted to S, are exactly the even assignments of S. Two methods are
   132	  run and must agree on every knot. Ranks: with H the matrix over the field of two elements with one row for each knot, the
   133	  rank of H less the rank of H with the columns of S removed is one (the records' test, ORDINARY-DYNAMICS, `rulers.py`). Cut:
   134	  in the graph with one vertex for each knot and one for the outside, an edge between the two holders of each shared
   135	  distinction and an edge to the outside for each loose one, deleting the knot leaves the rest connected (the knot is not a cut
   136	  vertex; the allowed states are the graph's cycle space).
   137	- **Not-all-equal.** Each knot is the rule that its places are not all equal. A knot passes when the assignments of S that
   138	  extend to an allowed state of the whole structure are exactly the assignments that are not constant, decided by a SAT solver
   139	  for each of the 2^|S| assignments (the records' test, ORDINARY-DYNAMICS, `source_cert.py`).
   140	- **Extension.** A round, or a move, extends when every allowed state of the structure before it is the restriction of an
   141	  allowed state after it.
   142	
   143	## Named starts
   144	
   145	- **Ring(n, a).** Knots 0 to n − 1. Knot i shares one distinction with knot i + 1 (mod n) and holds a loose distinctions.
   146	  Ring(5, 3) is the start of the golden-ratio eddy.
   147	- **Cycle through dead knots, doubled, D2(n, a).** Members 0 to n − 1, each holding a loose distinctions, and dead knots
   148	  w_0 to w_{n−1}; w_i shares two distinctions with member i and two with member i + 1 (mod n), so w_i has four places and its
   149	  met set is {i, i + 1}.
   150	- **Cycle through dead knots that meet one another, DW(n, a).** As D2 with single meetings: w_i shares one distinction with
   151	  member i, one with member i + 1, one with w_{i−1} and one with w_{i+1}.
   152	- **The seven-knot generator.** Stars [0,1,2,9,10,11], [0,1,3], [4,5,12,13,14], [6,7,15,16,17], [2,3,4,6,18,19,20], [7,8,21,22],
   153	  [5,8,23,24] ([GENERATORS-20261120-001](../GENERATORS-20261120-001/source.md)).
   154	
   155	## What is supplied by hand
   156	
   157	The complete round (assumption A104); every ration other than ORD, every treatment other than STALL, the release rule and both
   158	extras (A224); the part-round law, the birth-by-birth laws and every priority; the starts; the reading of a part as a thing (as
   159	in A125); the bounds on rounds, moves and knots; and each weighting named where a share is given. Each study says which of
   160	these it swaps.
