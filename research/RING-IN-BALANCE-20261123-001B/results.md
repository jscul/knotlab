# What a reference is: result

Ticket `RING-IN-BALANCE-20261123-001B` (sub-goal B318; G18 with G17 and G15), 2026-11-23. Computed with ticket A's engine;
scientific referee pending. [Pre-registration](preregistration.md) ·
[shared definitions](../RING-IN-BALANCE-20261123-001/definitions.md) ·
[code and its recorded readings](../../experiments/RING-IN-BALANCE-20261123-001B/RING-IN-BALANCE-20261123-001B-E001_reference/deviations.md) ·
[the thread's spot checks](../RING-IN-BALANCE-20261123-001/checks/spot_checks.txt)

**A dead knot does make it easier for a part to return and give parts off, in each way it was tested, though returning stays
uncommon among small starts. The ring itself is always made of the knots that waited; but the prediction that everything that
returns is made of such knots failed, because the same pattern half a period later is made entirely of new knots, and because
under other laws small parts return with no waiting at all. What one knot holds gives the round it was made in only on rings
where every knot keeps a leftover distinction, and there only to within three values.**

## Verdicts

| # | Verdict | What was found |
| --- | --- | --- |
| G | Holds | Ticket A's gate passed. All 34 named starts pass the parity knot test (and, reported, the not-all-equal test). The two ways of building a cycle through dead knots give the same roster at every round (387 comparisons). Under the ordinary law no part gives parts off and no knot is a member for two rounds, in 49 named runs and 85,716 census runs. |
| P1 | Holds | A cycle through dead knots returns every two rounds giving n two-member parts off for every n from 4 to 12, built either way. The cycle of three never returns. |
| P2 | Holds | No start of four or fewer knots with every knot live has a part that returns giving parts off. Among the 1,593 such starts of five knots exactly one does: the ring of five with three loose distinctions on each knot (one of 39 starts on the five-cycle). |
| P3 | **Fails, on both sentences** | Under laws with waiting, 13,561 returns that give parts off have a returning part that did not wait. Under laws without waiting, 24,595 returns give parts off, in 24 of ticket A's runs. But every return of a ring itself, 1,846 in all, is made of knots that waited. See below. |
| P4 | Holds | 107 census starts with fewer than five members have a part that returns giving parts off: 10 of five knots with one dead knot and 97 of six knots with two. All have exactly four members; none with three or fewer does. |
| P5 | Holds | Of 30,390 matched pairs at six knots, 70 return only with the knot dead and 42 only with it holding one loose distinction; none returns both ways. |
| P6 | Holds | (a) All 44,333 knots on six rings with a leftover on every knot satisfy r = f + 2p − 3 − 2e, and for the 12,187 whose stretch is shorter than the ring e read from the line of descent is the same number; the spread of rounds among knots of equal p and f is exactly 4. (b) On the bare ring every knot has p = 2 and f = 2. With the leftover removed from one knot the spread reaches 5 to 6 by round 12, and from every second knot 9 to 10. |
| P7 | Holds | On the seven-knot generator through round 9 (1,420 knots) no knot holds fewer fresh distinctions than (t + 9)/5; the least are 3, 3, 3, 3, 4, 4, 4, 5, 5. Among knots of equal p and f the rounds spread by at most 5. |

## The census

Every connected pattern of single meetings on 3 to 6 knots, every loose count from 0 to 3, each start once up to isomorphism:
86,032 starts. The knot test sets 316 aside, all with three or more dead knots. Seven runs under the ordinary law could not be
completed (below). Starts with a part that returns giving parts off, under the two added rules:

| Knots | Dead knots | Starts that pass the knot test | Return giving parts off | Share |
| --- | --- | --- | --- | --- |
| 3 or 4 | any | 216 | 0 | 0 |
| 5 | 0 | 1,593 | 1 | 0.06% |
| 5 | 1 | 1,027 | 10 | 0.97% |
| 5 | 2 or 3 | 508 | 0 | 0 |
| 6 | 0 | 28,508 | 49 | 0.17% |
| 6 | 1 | 30,390 | 70 | 0.23% |
| 6 | 2 | 16,691 | 97 | 0.58% |
| 6 | 3 or 4 | 6,783 | 0 | 0 |

Each start counts once; the shares are under that weighting and no other. The same 227 starts return under the three added
rules, and none under the ordinary law. Under the two added rules the rest grow with no return found (57,110), return giving
nothing off (16,681), jam (7,860) or stop (3,838); under the three, most stop (63,252) or jam (21,825). In every one of the 227
the part that returns is a cycle of met pairs whose members hold three each; the small parts that copy themselves, found in
ticket A under other rations, do not occur in the census.

- **Smallest with every knot live:** the ring of five.
- **Smallest with a dead knot:** five knots, four members. Stars [0,6,7,8], [0,1,2,3,9], [1,4,5], [2,4,10,11,12],
  [3,5,13,14,15]; the third knot is dead. Its ring has six members, more than the start has, and first returns from round 3 at
  round 5. The thread's own program gives the same: a cycle of six holding three each after rounds 3, 5, 7 and 9.
- **A start need not be a ring to make one.** The next smallest with every knot live are trees of six knots, which make a ring
  of six that returns.

## What this says about the owner's anchors

- **A dead knot is a common knot that is not a member.** In a start with every knot live, each knot has to be both a member
  and the common knot of the members it meets, which is why a cycle of n joinable pairs is a ring only for odd n. A dead knot
  lifts that. On every count above the starts with one or two dead knots return more often than the starts with none, and with
  a dead knot four members are enough where five are needed without.
- **It is a modest effect, and too many dead knots end it.** Returning stays under one start in a hundred at every size, the
  matched pairs split 70 to 42, and no start with three or more dead knots returns.
- **What lasts.** A ring that returns is, at the rounds where it has n members, exactly the knots that waited: the only knots
  under these laws that are members for two rounds. Half a period later the same pattern has 2n members, all new. So the pattern
  is not a set of lasting knots; it passes through one. And lasting is not needed for returning in general: under rations that
  give only enough for three places, small parts return and copy themselves with no knot waiting (ticket A).

## Why P3 failed

P3 said that every member of a part that returns giving parts off waited, and that no part does so without waiting.

- The first half fails by the definition of a return. The part of 2n members after an odd round comes back two rounds later,
  and it is made of that round's new knots. In the census the same happens for 887 returns of parts of 8, 10 or 12 members. The
  prediction was written with only the ring's phase of n members in mind.
- The second half fails on the small parts of ticket A's swap table (FLOOR0, FLOOR1 and ONE-FEWER with a short knot making
  offshoots or retiring) and on parts of seven and nine members under RATION-4.
- What stands: all 1,846 returns of a ring itself, in the named families, the swap table and the census, are made of knots that
  waited, and no ring returns under a law without waiting.

## Deviations and limits

- **Seven ordinary-law runs were not completed.** Three dense patterns of six knots with nearly every knot holding three grow
  so fast that the engine's demand step cannot finish: in one, a single new knot is asked for by 62,682 groups when the
  structure has 376 knots. They were rerun alone under 10 to 12 GB and 18 to 20 minutes and recorded as not completed, with
  their six to eight completed rounds, in which none stalls, stops or returns. All runs under the added rules completed, so P2
  to P5 lose nothing. That ordinary growth blows up on such starts is expected (assumption A110).
- **The census went through the shared runner.** Three of its 432 blocks ran out of memory there and were completed outside it,
  after the same script had reproduced five finished blocks record for record.
- Readings recorded by the code's author before the runs
  ([deviations](../../experiments/RING-IN-BALANCE-20261123-001B/RING-IN-BALANCE-20261123-001B-E001_reference/deviations.md)):
  which returns P3 covers, how P5's pairs are matched, how e is read from a knot's line of descent, and that "no knot is a
  member for two rounds" is checked over rounds that do not stall (52,474 ordinary census runs stall in round 1).
- Everything is finite: starts of up to six knots with single meetings, 10 rounds, 1,500 knots. A dead knot there has to meet
  three knots, so the cycles through dead knots of P1, whose dead knots meet two members, are not in the census.
- Evidence class: exhaustive census for the stated family and exact computation; the statement about starts with every knot
  live is an observation.
- Scaffolds: the way a cycle through dead knots is built was swapped (two ways, same result). The census's weighting was not
  swapped.
