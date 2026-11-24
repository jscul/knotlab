# A ring in balance: what stands, what a reference is, and where the round can go

Epic `RING-IN-BALANCE-20261123-001` (sub-goals B315, B318, B319 and the first half of B320; goals G18 with G5 and G17),
closed 2026-11-23, on the owner's go-ahead of that day. Three frozen studies, all computed, scientific referee pending.
[Shared definitions](definitions.md) · [ticket A: the ring on real knots](../RING-IN-BALANCE-20261123-001A/results.md) ·
[ticket B: what a reference is](../RING-IN-BALANCE-20261123-001B/results.md) ·
[ticket C: with no round supplied](../RING-IN-BALANCE-20261123-001C/results.md) · [referee hand-off](referee_handoff.md) ·
[advisor review before the freeze](advisor/README.md) · [the thread's checks](checks/)

## The answer

**The pilot's ring holds up.** Under two rules added by hand to the cheapest growth (a new knot receives at most three fresh
distinctions; a knot that cannot pay waits, and the others release what the cancelled joins would have taken as offshoots), a
ring of an odd number of knots, five or more, comes back to its start's roster every two rounds while the same two-knot part
comes apart from it n at a time. With a third rule the parts end and the roster is in balance. This was repeated on real
knots by code written from the frozen text alone, which agrees round by round with the pilot's two programs and with a second
independent engine.

1. **Every knot made is a knot.** Under parity this follows from an argument (a rule with a place of its own is the only
   constraint on its places) and was checked on 62,280 knots by two methods; under not-all-equal 1,848 knots pass through round
   6, with the same births as parity.
2. **Three is not special; waiting is.** Every cap from three to seven gives a returning ring, the ring's knots holding the cap
   each and the parts that come apart having 2, 5, 9, 14 and 20 knots. A fixed ration of three or four, or one fewer than
   asked, also does. Without waiting no ring returns; with the release swapped for holding, the ring jams for good; without
   offshoots nothing comes apart.
3. **A dead knot helps, modestly.** A dead knot is a common knot that is not a member of the live roster. In an exhaustive
   census of 86,032 starts of up to six knots, 227 have a part that returns giving parts off under the added rules and none
   under ordinary growth. With one or two dead knots a start returns more often than with none, four members suffice where five
   are needed without, and of matched pairs 70 return only with the knot dead against 42 only with it live. Returning stays
   under one start in a hundred, and no start with three or more dead knots returns.
4. **The ring is the knots that waited, but the pattern is not a set of lasting knots.** All 1,846 returns of a ring itself are
   made of knots that waited, the only knots under these laws that are members for two rounds. Half a period later the same
   pattern is made entirely of new knots.
5. **The round can belong to a part.** With the parts of the live roster taking their rounds one at a time in any order, the
   same structure is built (726 of 726 runs), and a knot's count of its own part's rounds is its round. How often the ring
   returns, counted in births, then depends on the order: under even-handed orders it slows as the parts it gave off pile up
   and keep growing, under largest-first it returns every 4n births and those parts are never served, and under the three added
   rules it holds steady.
6. **Inside a part the round is still supplied.** With one birth at a time and every knot reading again after each birth, the
   ring jams in every order (all 101,606,400 orders on the cycle of four) and never returns.
7. **One knot's holdings give its round only sometimes.** On rings with a leftover distinction on every knot, to within three
   values; with leftovers on some knots, or on the seven-knot generator, more loosely; on the bare ring, not at all.

**Not predicted.** Under rations that give a new knot only enough for three places, small parts copy themselves: a part of two
knots returns beside a copy of itself, with no knot waiting. Under one such law the members number five times the Fibonacci
numbers, in separate small parts. They came out of the table of swapped rules and are not yet studied.

## Predictions

Twenty-four were frozen, with three gates. All gates pass. Twenty predictions hold. Two fail: that a part returns giving
parts off under exactly the stated laws (ticket A, P8), and that everything that returns is made of knots that waited
(ticket B, P3); both fail on the small parts above, and P3 also on the ring's other phase. Two hold as meant and fail as
worded, because the wording did not say which part was meant (ticket A, P3; ticket C, P5).

## Scaffolds, and what survived their swaps

| Scaffold | Swapped for | Survived? |
| --- | --- | --- |
| The cap of three (A224) | caps of four to seven, fixed rations, one fewer | Yes: the ring returns under each; under two it returns giving nothing off. |
| Waiting (A224) | stall; the short knot makes offshoots; it retires | No: no ring returns. The result is about waiting. |
| The release rule (A224) | holding | No: the ring jams. |
| The fillers (A224) | their absence | The parts then grow instead of ending. No other rule that ends them is known. |
| Parity | not-all-equal | Yes. |
| The complete round (A104) | one part at a time, in seven orders | Yes: the same structure. |
| The complete round (A104) | one birth at a time, every knot reading again | No: the ring jams. |
| The ring as a start | cycles through dead knots built two ways; every start of up to six knots | Yes for the cycles; in the census 227 of 85,716 starts return. |
| The census's weighting (each start once) | not swapped | The shares are under that weighting only. |

So the result is about the added rules, as it says, and within them about waiting with release: it is not a property of
ordinary growth, in which no knot waits and no part comes apart. What it adds to the model is a worked case of a law under
which a fixed finite thing is made again and again by knots that pass the knot test, and a statement of how much of the
supplied round that law needs.

## What was supplied

Every rule beyond ordinary growth, the part-round law and its orders, the birth-by-birth law, the starts, the census's family
and weighting, the bounds, and the reading of a part of the live roster as a thing. The reader that says "the ring has
returned" is ours: nothing in the growth reads it.

## Limits

Everything is finite and computed: rings of 3 to 16 knots, starts of up to six knots with single meetings, 8 to 25 rounds,
at most 20,000 knots, 20 or 100 seeds. The statements for every odd ring and for every order of the parts are arguments, written
out for the referee and not refereed. Seven ordinary-law census runs blew up and were not completed. The advisor reviewed the
first design, not the part-round law. Ticket C's contract carries two stale descriptive fields from that first design.
