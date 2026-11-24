# With no round supplied: result

Ticket `RING-IN-BALANCE-20261123-001C` (sub-goals B319 and B320; G5 with G18 and G17), 2026-11-23. Computed with code written
from the frozen text alone, independent of ticket A's engine; scientific referee pending.
[Pre-registration](preregistration.md) · [shared definitions](../RING-IN-BALANCE-20261123-001/definitions.md) ·
[code and its recorded readings](../../experiments/RING-IN-BALANCE-20261123-001C/RING-IN-BALANCE-20261123-001C-E001_no_round/deviations.md) ·
[the two engines compared](../RING-IN-BALANCE-20261123-001/checks/compare_engines.txt)

**The round for the whole growth is not needed: when the parts of the live roster take their rounds one at a time, in any
order, the same structure is built, and each knot's own count of its part's rounds is its round. What the order does change
is how often the ring returns, counted in births: under even-handed orders the ring returns ever more slowly as the parts it
has given off pile up, unless those parts end; under an order that serves the largest part first it returns every 4n births
and the parts it gave off never move. The round inside a part is still needed: with one birth at a time and every knot
reading again after each birth, the ring jams in every order and never returns.**

## Verdicts

| # | Verdict | What was found |
| --- | --- | --- |
| G | Holds | (a) Two engines written independently, this ticket's part-round law taking every part in turn and ticket A's complete rounds, agree on members, parts, loose counts, met sets, births and fresh counts for rounds 1 to 8 on the ring of five and the cycles of four and five through dead knots, under the two and the three added rules. (b) The record's order effect comes out: two three-place knots sharing a distinction stop in 12 of 40 seeds and go on in 28 (the record's referee: 12 of 40); a lone four-place knot goes on in 37 of 40. (c) The sameness test accepts 25 of 25 renamed copies and rejects 50 of 50 copies with one distinction moved. |
| P1 | Holds | One birth at a time, least generation first, every tie rule, either rule for common knots, on the four cycles through dead knots: all 2,400 runs jam at generation 1 after exactly 2n offshoots and no join. Every order on the cycle of four: 101,606,400 orders pass through 71 distinct structures to one end, jammed. |
| P2 | Holds (a check of an argument) | In all 726 part-round runs the knots of own time at most R are the same structure as R complete rounds build, R from 2 to 25, up to 6,960 knots, by exact isomorphism with rounds as colours. |
| P3 | Holds | 688 runs reach 12 returns; 38 meet the bound of 20,000 knots first, after 6 to 11 returns (all under the two added rules, 37 with the order by members). None stops returning otherwise. |
| P4 | Holds | Under the two added rules the births between returns grow under all four even-handed orders: late returns (7 to 12) against early ones (2 to 6) by 3.8 to 4.6 times with each part equally likely, 4.8 to 5.4 with every part in turn, 4.6 to 5.2 with the least own time first, and 12 to 14 with chance by members (where only 3 to 11 of 20 seeds reach 12 returns). |
| P5 | Holds as meant; fails as worded on the ring | With the largest part first, or the part holding most, the parts that came apart never move in any run, and the births between returns are exactly 16, 20 and 20 on the cycle of four, the cycle of five and the ring of five: 4n for n the knots of the start. As worded, n is the members of the part that returns, which on the ring is read as the part of ten after round 1, giving 40. |
| P6 | Holds | Under the three added rules the births between returns do not grow under any order: every ratio is between 0.997 and 1.044, most exactly 1. |
| R | Reported | Smallest part first, two added rules: the births between returns stay flat at about 177, 327 and 326 (ratios 1.02 to 1.04): each part that came apart moves until it is larger than the ring and then never again. One birth at a time, uniformly: a join of generation 1 is made in 79 to 96 of 100 seeds on the cycles, a jam follows in 94 to 100, and in no seed of any start does a part the same as the start's roster appear. The rings at their start jam at generation 0 under either rule for common knots. |

Across all 4,800 runs with one birth at a time, no part the same as the start's roster ever appears.

## What this says about time, in the program's terms

- **A count of rounds can belong to a part.** Past the start a part acts alone, so nothing has to step every part at once.
  Each part can take its rounds whenever it is served, and a knot's own time, the number of rounds its line of descent has
  taken part in, is exactly its round under complete rounds. This is argued in the pre-registration and checked here on 726
  runs; the argument is for the referee.
- **How often depends on the order, and on what else is there.** Births are counted by the one who runs the growth; nothing in
  the growth counts them. Under orders that serve every part alike, a ring that keeps giving off parts that keep growing
  returns ever more slowly in births. Under the three added rules, where the parts end, it returns at a steady 4n to 5n
  births (16 to 25 here). Under an order that always serves the largest part, the ring returns every 4n births and the small parts are never
  served at all: parts with nothing asked of them cost nothing. Each of these orders reads only the present roster (how many
  members a part has, or how much they hold), except the one by least own time, which reads the history.
- **Inside a part the round is still supplied.** The birth-by-birth law lets every knot read again after each birth. Then an
  offshoot that is entitled to release three distinctions has released two when its own shortage is read again, and it stops;
  the joins it would have freed stay short for ever. That is the whole jam, and it does not depend on the order. So under these
  laws the members of one part have to read together. Whether a law exists in which they need not is open.

## Deviations and limits

- **A stale contract text (the thread's error).** The contract of this ticket carries the hashes of the frozen
  pre-registration and definitions, but two of its descriptive fields still describe the first design (a grid of 19,200 runs
  and sameness to depths 1 to 3). The pre-registration is what was run. The contract is left as frozen.
- **Readings recorded by the code's author** ([deviations](../../experiments/RING-IN-BALANCE-20261123-001C/RING-IN-BALANCE-20261123-001C-E001_no_round/deviations.md)):
  own time at most R is read as own time at birth, since a waiting member's own time goes on growing; P5's n, as above;
  a part's demand roster holds only that part, with a check at every move that no knot meets it and another part, which never
  fired.
- The part-round law was not reviewed by the advisor before the freeze; the advisor's review of the first design is what
  found the jam by hand.
- Left out, as the pre-registration says: the record's eight-knot clock and its attachments, not-all-equal, and any law in
  which the members of a part read at different moments other than the birth-by-birth law.
- Everything is finite: three starts for the part-round law, 12 returns, 20 seeds; six starts, 600 moves and 100 seeds for one
  birth at a time; every order only for the cycle of four. Every mean is over seeds under the named order's own weighting.
- Evidence class: exact computation; the order-independence of what is built is an argument checked on 726 runs.
- Scaffolds: this ticket swapped the complete round (A104) for the part-round law, and what ticket A found survives it; for
  the birth-by-birth law it does not. The part-round law, its orders and the birth-by-birth law are themselves supplied.
