# Takes that reach further: a second probe of "more than a count"

Sub-goal B335, 25 November 2026. [The first probe](../two_by_two/README.md) found that under the take of a sole
candidate a made part meets only the other branches of the knot it descends from, so its course can tell how many of
them are there and nothing else. The owner asked for the next direction: a law without names under which parts of
different descent come to meet. **This is a probe by the thread, not a frozen study.** Nothing was registered
beforehand; each program states at its head what was expected before its first run.

Programs (run `make_engine.py` first; it writes the engine into this folder): [the engine's seven added rules](make_engine.py) ·
[the scan and the four runs](scan2.py) · [its driver](drive2.py) · [the links, and whether they are the start's](links.py) ·
[one case birth by birth](detail.py) · [the renumbering check](renumber.py) · [every take recomputed from the rule's words](check_take.py) ·
[tallies](summ2.py), [of links](summ_links.py), [driver](drive_links.py).
Outputs: [ring starts](rings.jsonl.gz) · [small census starts, five rules](census_wide.jsonl.gz) ·
[small census starts, two rules](census_near.jsonl.gz) · [five-knot starts](census_five_m2many.jsonl.gz) ·
links on [rings](links_rings.jsonl.gz), [small census](links_census.jsonl.gz), [five-knot](links_five.jsonl.gz) ·
[rings with unequal knots](links_ringk.jsonl.gz) ([driver](drive_ringk.py)) ·
[renumbering](renumber.jsonl.gz) · [rule check](check_take.jsonl.gz).

> **Block on one reading, 26 November 2026 (referee report R1;** [the report](../../referee-R1/report.md)**).** Finding 2
> below, and the report as sent, say that under the take of the candidate with the most holders "the linking knots are
> made knots that are an ancestor of neither part", and so that parts of different descent meet through made knots.
> That is false of the knots that meet. The probe used ticket B's class "ancestral common knot", which leaves out a
> knot that is a direct parent of both meeting knots. In all 1,250 first meetings with no start-held linking
> distinction, under each knot law, the made linking knot is a direct parent of both knots that meet, each child
> holding a different distinction of it. These are two children of one made knot: branches of one knot, as in the
> first probe. **"Parts of different descent meet through made knots" is withdrawn.** What stands: the counts of the
> barred courses (three classes by the number barred, a least of two entries at distinct births, on 1,120 four-run
> tests) and both registered tickets.
>
> Narrowings from the same report:
> - The 15 and 90 of 3,285 settings with a take count only rounds after the first; with round 1, 1,965 of 3,285 for
>   each rule. The 120 meetings under each take-every rule are 60 unordered meetings.
> - For "two copies of one count" read: three classes by the number barred, and a least of two entries, with their
>   places saved only for the 18 earlier ring tests.
> - For "one value in every census test" read: one entry in 76 responsive tests, 51 unchanged; 54 of 127 census tests
>   reached a common round seven.
> - That a first part still meets a second part when the other is barred was not established.

## What the record already had

The study of parts that meet again ([its decision](../../../PARTS-MEET-AGAIN-20261124-001/decision.md), closed the same
day) found that laws which reach further do rejoin parts, 180 times through a knot the growth made; that every such
law needed a supplied way of choosing which distinction is taken, by name; and that what crosses is "whether the other
part is there", never "what the other part is". This probe adds a way of choosing that uses no name, two second parts
in place of one, a sorting of the ways a course can depend on two second parts, and ticket B's question of whether a
link is the start's after all.

## The rules tried

A birth may take a shared distinction that no parent of it holds. Two things were varied, and no rule uses a name or
looks at parts.

- **How far it draws from.** Near: the knots a parent meets, as in the take of a sole candidate. Further: those knots
  and the knots they meet.
- **Which one it takes.** The sole candidate, when exactly one is on offer; every candidate; the candidate with the
  fewest holders, when exactly one has the fewest; the candidate with the most holders, when exactly one has the most.

That is eight rules, seven of them new. Each was run with five rations (just enough for three places, the cap of
three, the ordinary count, the owing ration and its plain form) and short knots retiring, making offshoots or
waiting: fifteen laws a rule, not-all-equal, 7 rounds, parts chosen after rounds 1 to 4. Starts: ticket B's five ring
starts and the 219 census starts of three and four knots; then, for the one rule that gave something, the 250 census
starts of five knots, which were not looked at while the probe was built, and every ring of five to seven knots with
unequal knots (246 rings: five knots holding 2 to 5 loose distinctions each, six holding 2 to 4, seven holding 2 or
3, one for each class under turning and reversing). 27,345 runs in the sweeps and 492 on the rings.

## What was found

1. **Six of the seven new rules give nothing new.**
   - Drawing from further and taking a sole candidate: with more on offer there is almost never exactly one. Births
     take in 15 of 3,285 census runs, and no two parts that were wholly apart meet.
   - Drawing from further and taking the one with the fewest holders: births take in 90 runs; no part meets two others.
   - Taking every candidate, near or further: about a third of the runs are stopped by the guard, the only meetings
     of parts wholly apart run through start knots (120 under each), and no part meets two others through made knots.
   - Drawing from near and choosing by a count, fewest or most: as under the take of a sole candidate. With the
     fewest, 2,020 first parts with 8,649 pairs of second parts, every pair alike. With the most, 565 first parts,
     2,872 pairs alike and 4 not alike, and on those four the first part's course does not change.
2. **One rule makes parts of different descent meet: draw from further and take the candidate with the most holders.**
   On the small census starts 37 first parts meet two or more others only through made knots, with 99 pairs of second
   parts not alike and 6 alike; on the five-knot starts 114 first parts, 269 pairs not alike and 24 alike; on the ring
   starts 30 first parts under one law. The linking knots are made knots that are an ancestor of neither part, which
   the take of a sole candidate never gave. Parts now also first meet later than the round after they separate.
3. **Where the link is wholly the growth's, the course tells how many, through two births, and never which.** Under
   the cap of three with offshoots, on 123 of the 136 rings of five knots, 1,120 tests have second parts that are not
   alike, linking knots made after the start, and no start knot holding a distinction through which they meet. In
   every one the first part's course is the same whichever second part is barred, different with neither barred, and
   different again with both; and it takes two values at two births to tell the cases apart. In the case read birth
   by birth, each second part adds one to the demand of a different join of the first part's descent in round 5: 2
   with it there and 1 without. This is the first verdict "composed over several births" in ticket B's reading, and
   what it holds is two copies of one count. The course as read does not tell the two births apart, on rings with
   no symmetry as on the others. The thread expected otherwise before the run and was wrong. Rings of six and seven
   knots give no part that meets two others this way, and the other law that responds gives none on any ring.
4. **On the census starts every link runs through a distinction a start knot holds.** All 127 tests there. The rule
   piles holders onto whichever distinction already has the most, and on these starts that is one of the start's own.
   Counted by knots these are meetings only through made knots; by ticket B's own question they are the start's.
5. **Through such links the course depends on the two second parts in six ways.**

   | The course from the first part only | Small census (37 tests) | Five-knot (90 tests) |
   | --- | --- | --- |
   | does not change | 14 | 37 |
   | tells how many are barred | 16 | 12 |
   | changes only with both barred | 1 | 10 |
   | changes with exactly one barred, and with both barred is as with neither | 0 | 26 |
   | follows the first to arrive: one alone matters, the other only once it is gone | 6 | 1 |
   | changes with one of the two only | 0 | 2 |
   | is different in all four cases | 0 | 2 |

   In 11 tests on 5 starts it differs with which second part is barred. One value at one birth separates the cases
   in every census test.
6. **In the cases read birth by birth these are presence, a count and order of arrival.** On a start of four knots
   (the cap of three with offshoots), the first part's own line runs until it joins a second part. One second part
   would join it in round 5 and the other in round 6. So its line ends in round 5 with the first there, in round 6
   with only the second there, and not at all with neither: three courses, and "which" is which came first. On a
   start of five knots (short knots retiring), where all four courses differ, one second part changes how many fresh
   distinctions three of the first part's births receive in round 4 (3 with it there, 1 without), and with the other
   barred the first part's own line has three more births in round 5. The other ways were not read birth by birth.
   **What these runs cannot say** is whether any course responds to what a second part is, as against where and when
   it arrives: no test holds the place fixed and changes the form. Where the link is wholly the growth's, two second
   parts that are not alike are not told apart.

## How it was checked

- **The engine** is ticket B's with five replacements, listed in `make_engine.py`. With the take of a sole candidate it
  gives the same knots, parts, first parts and pairs as ticket B's own engine on 73 of 73 ring runs compared.
- **Every take recomputed** from the rule's words, from the places of the knots at the start of each round and with
  none of the engine's code: 7,105 of 7,105 births the same, on 30 runs (the 15 ring and small census starts with a
  test, under the two laws that respond).
- **Renumbering**: those 30 runs repeated under 8 seeded renumberings of knots and distinctions each: knots, parts,
  first meetings, pairs and the outcome of every test the same in 240 of 240.
- **Starts not seen beforehand**: the five-knot starts were run once, after the rule and the readings were fixed.
  They show the same picture: parts of different descent meet, every link through a distinction a start knot holds.
  The rings with unequal knots were run once as well, with the expectation written first; it failed.
- **The knot test** on the four runs of two cases (one census, one ring): 1,073 and 2,759 verdicts, none failing.

## Not run, and limits

- **A probe.** No pre-registration, no referee, one program for the course; the thread wrote the rules, the scan and
  the checks.
- **Not run**: 148 of the 27,345 runs passed their time limit (30 or 60 seconds): 71 under the near rule that
  chooses the fewest, 39 under the fruitful rule, 30 under the further rule that takes every candidate, 8 others.
  3,778 runs were stopped by the engine's guard and 178 by its knot bound, and are read as far as they went. None of
  these is a negative.
- **Tested with four runs**: one pair for each first part, and at most 12 a run in the sweeps; the links were then
  read with every eligible first part tested.
- **The course from the first part only** counts knots that also descend from a third part.
- **One family of rules**, seven members, three of the ten listed rations left out, parity not run, the knot test on
  two cases only.
- **The fruitful rule seeks the most-held distinction.** A distinction with many holders is a common hub, and a hub
  is not a contact. The ring cases have no start knot on the linking distinction; whether their links are hubs in
  that sense was not examined.
- **Finite**: 7 rounds, starts of three to five knots, and rings of five to seven.
- Nothing here is about living things, minds or physics.

## Report as sent (2026-11-25, about 22:20 UTC)

**Direction 1, run with rules that do reach further: parts of different descent can be made to meet through knots the growth made, under a rule that uses no names. Where that link is wholly the growth's, the first part's course still tells only how many second parts are there, never which.** This was a second probe of my own, not a registered study.

First the correction. The rule I named for this direction, "a take within one holder step", reaches less far than the rule already in use, so it could never have done this. I ran the direction with rules that draw from one step further out. It is logged (Not a block).

What the runs show:

- **Seven new taking rules, none using a name; six give nothing new.** I varied how far a birth draws from (the knots its parent meets, or also the knots those meet) and which candidate it takes (the only one, all, the one with fewest holders, the one with most). Six of the seven either almost never take, or pile everything through the start, or behave like the old rule.
- **One works: draw from further and take the candidate with the most holders, when exactly one has the most.** Under it a first part meets second parts that are not branches of its own knot, through made knots that are an ancestor of neither.
- **Through links that are wholly the growth's: how many, through two births, never which.** On 123 rings of five knots with unequal knots, 1,120 tests: the course is the same whichever second part is barred. It does take two values at two births to tell the cases apart, which is new, but they are two copies of one count. I expected rings with no symmetry to show "which", wrote that down first, and was wrong.
- **On the census starts, "which" does appear, but through the start.** In 11 of 127 tests the course differs with which second part is barred. Every one of those links runs through a distinction a start knot holds. In the cases I read birth by birth the cause is which second part arrives first, or a count at one birth and a join at another.
- **Whether anything responds to what a second part is stays open.** No test holds the place fixed and changes the form. The study of parts that meet again had already found, with one second part, that what crosses is whether the other part is there; this agrees with it.

Checks: the engine is ticket B's with five recorded changes and reproduces it on 73 of 73 runs; every take was recomputed from the rule's words (7,105 of 7,105 births); renumbering changes nothing (240 of 240); the five-knot starts and the rings were run once, after the rule was fixed. Not run: 148 of 27,837 runs passed their time limit, and the knot test was run on two cases only.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the second probe of sub-goal B335: takes that reach further | **Status:** Partially successful | Parts of different descent meet through made knots under a rule without names; a course that differs with which second part is barred shows only through a distinction the start holds. |
| Local direction — more than a count by changing the taking rule | Practically exhausted | Seven rules; under the one that works, 1,120 of 1,120 tests through the growth's own links tell how many. |
| Broader exploration — the owner's fold of emergence | Known alternatives | A test that fixes the place and changes the form; the third property; the copier study, whose third ticket has reported. |
| Long-term goal — G15 Learning: a point in a learned knot pattern, with G18 Comparing growth laws | Capability gained | A rule without names under which made parts of different descent meet, and a first course that needs two values at two births. What crosses is still presence and counts. |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A test that fixes the place and changes the form: the same first part, with a second part of one form or another in the same place | 3/3 — it is the question the fold asks | 1/3 — no start or rule in hand gives it | Design pairs of starts that swap two forms between two places, as a registered study with an advisor's review → a course that follows the form, or one that follows the place on every pair | Selected · awaiting go-ahead |
| 2 | Are the links under the new rule contacts or common hubs? | 2/3 — the rule seeks the most-held distinction, and a hub is not a contact | 2/3 — the knot test exists; the hub reading of a link must be written | Read the linking distinctions of the 1,120 ring tests for their holders → links that pass as contacts, or hubs throughout | Alternative · deferred |
| 3 | The third property on a case in hand: does a part whose course changed make a part of its own that it otherwise would not? | 2/3 — completes the owner's three properties on one case | 3/3 — the cases and the four runs exist | Read the parts made from the first part only in the four runs to round 9 → a part form in one run and not another, or the same forms | Alternative · deferred |

Direction 1 moves G15's open question directly, and its weakness is that nobody has yet shown such a pair of starts exists; it needs a design, not another sweep, so it waits for your word. Direction 2 guards the one positive against being the wrong kind of link. Direction 3 is cheap and finishes the picture on what we have.

**STOP** for changing the taking rule. Settled, for what was read: a rule without names can make parts of different descent meet, and through the growth's own links only a count crosses, at as many births as there are second parts. Open: whether a course can follow the form of what it meets. What would reopen this line: a rule that reaches as far without seeking the most-held distinction.

**Corrections:** one, logged (Not a block): the rule first named for this direction reaches less far than the one in use. One expectation written before a run failed (rings with no symmetry would show "which"); that is a result.
**Goals:** no checkpoint row (no study closed). B335 carries both probes; its concreteness is re-rated 1/3.
**Assumptions:** one scaffold entered, A257 (a birth may take the most-held distinction within two holder steps of knots). A244 (a law is not a reader) is borne out again.
**Scaffolds:** added: seven taking rules, one of them entered as A257. Swapped: how far a birth draws from, which candidate it takes, the ration (five), the treatment of short knots (three), the starts (rings, census starts of three to five knots, 246 rings with unequal knots). What survived: how many, through the growth's own links. What did not: any "which", which appears only where a start knot holds the linking distinction.
**Basket:** direction 1 is recorded on B335; directions 2 and 3 are in this report only.
