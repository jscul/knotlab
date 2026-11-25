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
