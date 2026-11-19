# Which dimensions does the cheapest growth give across arrangements of touching knots?

Epic `TOUCH-CENSUS-20261118-001`, 18 November 2026, by Claude, on the coordinator's go-ahead for `FIRST-KNOT-20261118-001`'s
direction 3. Goals G17, G2 and G1. **Refereed:** report [R1](referee-R1/report.md), confirmed with fixes, no Block, folded in on 18 November
(see Referee). The referee grew the 100 arrangements the run had not read, and the run's last shard then finished (23:55 UTC, after two
timeouts): its own merge of all 26,441 ([results_complete.json](../../artifacts/TOUCH-CENSUS-20261118-001B/TOUCH-CENSUS-20261118-001B-E001_arrangements/results_complete.json))
equals the referee's complete census in every row. The tables below are the **complete census**; the study's 26,241 at the close
are given in the Referee section.

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `86694ace0` at 20:36 UTC; the census ran from 20:37
  UTC through the shared runner (`TOUCH-CENSUS-B1`, `runs/touch-census`), with one amendment at 21:06 UTC (the rerun of unsettled
  arrangements capped at 12,000 junctions, 40 rounds or 600 seconds, recorded in the contract) after six shards had run 22 minutes.
- Lemmas: [proof.md](../../proofs/TOUCH-CENSUS-20261118-001A/TOUCH-CENSUS-20261118-001A-P001_chains/proof.md).
- Code: [arrlib.py, job.py, merge.py, checks.py](../../experiments/TOUCH-CENSUS-20261118-001B/TOUCH-CENSUS-20261118-001B-E001_arrangements/).
- Results: [results.json](../../artifacts/TOUCH-CENSUS-20261118-001B/TOUCH-CENSUS-20261118-001B-E001_arrangements/results.json).

"Dimension" here counts junctions by round: the junctions up to round t grow like t^d (the referee's narrowing of
`FIRST-KNOT-20261118-001`). Bond balls are proved only for the d-fold counting pattern.

## The answer

**In the owner's terms.**
- **Nothing chooses how first knots are arranged, so we counted every small arrangement:** every connected way of letting up to five
  parity knots of three to five places share distinctions, each arrangement counted once (26,441; 26,241 read so far).
- **What is typical.** About two in five arrangements cannot start at all: some knot is asked for more joins at once than it has
  open distinctions. About one in seven closes. Of those that grow, about four in five grow two-dimensionally, and almost all the
  rest along a single strip (one-dimensional). This holds under both ways of counting (each arrangement once, or by how many
  labelled descriptions it has) and at four and at five knots.
- **What is rare.** Three-dimensional growth: 40 arrangements (0.15%). Four-dimensional: 7 (0.03%), all of them growing exactly as
  four mutually touching knots do. Growth faster than any power: 13 arrangements (0.05%), rings of five knots with some five-place
  knots, whose junctions per round multiply by a fixed base between about 1.13 and 1.62 every round (four of them follow exact
  recurrences: x⁶ = x + 1 with base 1.135, x⁵ = x⁴ − x² + x + 1 with base 1.263, and Fibonacci with base 1.618 for the ring of five
  five-place knots; computed, not proved; the ring of one five-place knot is proved in `RING-GROWTH-20261118-001`).
- **So the cheapest growth has a typical dimension, two, without being told any number.** It is typical, not forced: three and four
  occur, rarely, and exactly where the arrangement holds three or four chains of junctions born together.
- **The rule mostly predicts the dimension.** The dimension is the largest set of chains born together with one common partner in
  98.7% of growing arrangements. It misses in two ways: in 145 arrangements chains born separately combine, and the dimension is then
  exactly one more than the largest set every time; and rings of five knots grow without any chain, one-dimensionally when all five
  have four places and faster than any power when some have five.

| Outcome | Distinct arrangements | Share | By labelled count |
| --- | --- | --- | --- |
| cannot start (round-1 stall) | 11,010 | 41.6% | 43.7% |
| closes | 3,726 | 14.1% | 12.4% |
| one-dimensional | 2,081 | 7.9% | 8.1% |
| two-dimensional | 9,564 | 36.2% | 35.7% |
| three-dimensional | 40 | 0.15% | 0.09% |
| four-dimensional | 7 | 0.03% | 0.005% |
| faster than any power (rings of five) | 13 | 0.05% | 0.03% |

Complete census (the referee's table, and the run's own once its last shard finished; labelled total 2,626,697). Two-dimensional among growing arrangements:
81.7% by distinct count, 81.4% by labelled count; at six knots (the referee's sample of 1,200, one size past) 85.1% and 84.5%. A
reading of 5 or 6 by the frozen reader is not a dimension: it means "not polynomial" (two equal fifth differences in a seven-round
window), and it fired only on exponential rings.

By number of knots (distinct, complete): two knots, 17 of 22 grow, all two-dimensionally; three, 71 of 154 two-dimensional, 28
one-dimensional, 2 three-dimensional; four, 852 of 1,760 two-dimensional, 192 one-, 5 three-, 2 four-dimensional, 315 stalls; five
(24,502), 8,624 two-dimensional, 1,861 one-, 33 three-, 5 four-dimensional, 13 faster, 10,695 stalls.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| G | three gate checks | held | 3 of 3 |
| P1a | birthless growth is one-dimensional | **failed** | 9 birthless growths: 2 rings of five four-place knots (one-dimensional, 5 junctions a round), 7 rings of five with five-place knots growing faster than any power |
| P1b | with a birth, dimension = the largest class | **failed** | held in 11,476 of 11,621; in all 145 exceptions the dimension is the largest class plus one (141 times 2 from single births, 4 times 3 from a class of two and single births) |
| P2 | two most common among growing; three or more under 2% | held | 0.18% by distinct count, 0.09% by labelled count |
| P3 | nothing above four, nothing unsettled after the rerun, exactly one arrangement of dimension 4 | **failed** | 7 arrangements of dimension 4, each growing exactly as four mutually touching five-place knots; the faster-than-power rings were read as "6" (meaning not polynomial) or left unsettled |
| P4 | every stall in round 1 | held | 10,906 of 10,906 |
| P5 | stall share rising with knots to over 40% at five; two-dimensional share rising, one-dimensional falling | **failed** | stall shares 0, 0, 18%, 44% (no rise from two to three knots); two-dimensional share 100%, 70%, 81%, 82% |
| P6 | no distinction with one value in every state | **failed as stated** | 1,746 of the 26,241 arrangements (1,749 of 26,341, and of all 26,441) already force a distinction in their start (a part of the arrangement whose cut is one distinction); the growth never adds one (number corrected after the referee) |

Three of eight held (G, P2, P4). The failures are on the record; two of them (P1b's "plus one" and the faster growths) are the study's
most informative findings.

## Why it holds, and what is proved

- **Stalls only at the start** (Lemma 1, proved): the fewest counts always cover the next round's demand, so only the given start
  knots can fall short, in round 1.
- **Where growth comes from** (Lemma 2, proved): extra distinctions are given only at one-parent junctions asked for at most one join,
  and through a relay; such junctions start chains that never end.
- **The rule's proved cases** (from `FIRST-KNOT-20261118-001`): a sibling pair of chains grows two-dimensionally, m chains sharing the
  group of m mutually touching knots grow m-dimensionally.
- **Not proved**: the "plus one" when separately born chains combine, and the faster-than-power rings.

## Known results, and what this adds

Known: enumeration of small multigraphs up to isomorphism; the predecessors' Birkhoff picture. What this adds: the first census of
what the cheapest parity growth does over all small arrangements of first knots, with two-dimensional growth typical, three and four
rare, and a mechanism (chains born together) that predicts nearly every case.

## Limitations

- The census stops at five knots of three to five places, and weights arrangements uniformly or by labelled count (A106).
- "Dimension" counts junctions by round; bond balls are not measured.
- The frozen dimension reader looked at the last seven rounds only; it read three exponential-looking rings as "6".
- None pending: the run's last shard finished on 18 November at 23:55 UTC and agrees with the referee's complete census.
- One joining rule (A104).

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2), before the freeze. It proposed splitting the rule, predicted that rings of five four-place
knots grow without a chain (right: one-dimensionally), and that linked partners might combine (right: always plus one); its tighter
2% bound held; it predicted "no birth after round 2" (not frozen; births came up to round 11, through relays).

## Referee

Report [R1](referee-R1/report.md), 18 November 2026, by the coordinator's background referee thread with fresh code: confirmed with
fixes, no Block. Counting confirmed by Burnside's lemma (3, 22, 154, 1,760, 24,502) and the labelled weights; two-dimensional growth
typical under both weights, in the complete census and one size past at six knots; the fast rings real (grown to 60,000 junctions);
1,686 of 1,686 sampled readings agree at 45 rounds. Folded in the same day, logged in `docs/CORRECTIONS.md` and knotlab's
`HISTORY.md`:
1. **Narrowing (the unread block).** The 200 arrangements unread at the close were the last, largest five-knot arrangements, not a
   random sample, and they held the exotic growth: the complete census has 40 three-dimensional arrangements (not 36) and 13
   faster-than-power rings (not 7). At the close the study had read 26,241: stall 10,906, closes 3,705, one-dimensional 2,068,
   two-dimensional 9,512, three-dimensional 36, four-dimensional 7, faster 7.
2. **Narrowing (the fast rings' bases).** 1.13 to 1.62, not "about 1.25 to 1.4"; a reading of 6 means "not polynomial".
3. **Narrowing (number).** 1,746 arrangements force a distinction in their start, not 1,713.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: which dimensions are typical and rare across small arrangements of touching knots? | **Status:** Successful (census; 3 of 8 predictions held) | Two-dimensional growth is typical (about four in five growing arrangements, under both weights, at four and five knots, and at six by the referee); three and four are rare (0.18%); the chain rule predicts 98.7% |
| Local direction: what the start's arrangement decides | Continue | Two exceptions to the rule are sharp and testable: separately born chains add one, and rings of five grow without chains, sometimes faster than any power |
| Broader exploration: where dimension comes from | Known alternatives | A cap, a price, the start's open distinctions, or (here) the typical arrangement |
| Long-term goal: G17 Typical and rare meeting patterns (with G2) | Capability gained | The first typical dimension of cheapest parity growth over unchosen arrangements: two; three is rare, not forced |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Rings of five knots that grow faster than any power under the cheapest counts, with no chain born | 2/3 — growth the chain lemma did not expect | 3/3 — seven arrangements, all rings | prove the per-round ratio for the ring of four four-place and one five-place knot → stop at a proof of exponential growth, or a polynomial | Selected · awaiting go-ahead |
| 2 | The "plus one": when separately born chains combine | 2/3 — would make the rule exact | 3/3 — 145 cases, all plus one | state when two births' partners are linked, freeze "dimension = largest class + 1 then", test on six knots → stop at a proof or a counterexample | Alternative · deferred |
| 3 | Serial growth read from distances (`FRESH-COUNT-20261118-001#1`) | 2/3 — tests A104 | 2/3 | as before | Alternative · deferred |
| 4 | B202, a growth whose dimension belongs to the relation | 3/3 | 1/3 | as before | Alternative · deferred (sub-goal) |

- **#1.** Payoff 2/3: under the fewest counts, extra distinctions come only from chains (Lemma 2), yet these rings grow faster than
  any power with none; if it is exponential, the cheapest growth can branch like a tree with no surplus at all. Concreteness 3/3:
  seven small arrangements, one ring of five knots in each. Bound: one epic, rings of five to seven knots.
- **#2.** Payoff 2/3, concreteness 3/3: one more clause would make the rule predict every polynomial case in the census.
- **#3, #4** as in the earlier reports; the coordinator asked to keep both.

**Corrections:** none to published claims (P6's wording was this study's own prediction, failed before publication).

**Goals:** G17 checkpoint (capability gained: two-dimensional growth typical over unchosen arrangements, three and four rare); G2
checkpoint (obstruction learned: three is rare, not forced); no goal changed.

**Assumptions:** new A106 (arrangements are weighted uniformly over distinct arrangements, or by labelled count, of up to five knots
of three to five places; a measure).

**Basket:** B196, `FRESH-COUNT-20261118-001#1`, B202; none taken, #1 here awaits go-ahead.

## Final report as sent (2026-11-18 21:45 UTC)

*As sent, on the 26,241 arrangements read at the close; the complete census and two corrected numbers are in Referee.*

**Outcome:** Over every small arrangement of touching first knots, the cheapest growth is typically two-dimensional. Three and four dimensions are rare, and nothing forces a number. The census covered 26,241 of the 26,441 distinct arrangements of up to five knots of three to five places; two slow shards of 100 are still running and will be folded in. 3 of 8 frozen predictions held. Closed, referee pending.

- **Typical.** About two in five arrangements cannot start: some knot is asked for more joins than it has open distinctions. About one in seven closes. Of those that grow, about four in five grow two-dimensionally and most of the rest along one strip. This holds counting each arrangement once or by labelled count, and at four and at five knots.
- **Rare.** Three dimensions: 36 arrangements (0.14%). Four: 7, all growing exactly as four mutually touching knots do. Faster than any power: 7 rings of five knots containing five-place knots, multiplying by about 1.3 a round (computed, not proved). "Dimension" here counts junctions by round, not bond balls.
- **The rule.** "The dimension is the largest set of chains born together" held in 98.7% of growing arrangements. In all 145 misses it was exactly one more. Rings of five knots grow with no chain at all: one-dimensionally when all have four places, faster when some have five.
- **Failed predictions:** the rule as frozen (both parts), "exactly one four-dimensional arrangement", the trends by knot count, and "no forced distinction". On the last, 1,746 arrangements (corrected from 1,713 after the referee) already force one in their start; the growth never adds one.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: which dimensions are typical and rare across small arrangements of touching knots? | **Status:** Successful (census; 3 of 8 predictions held) | Two-dimensional growth is typical (about four in five growing arrangements); three and four are rare (0.16%); the chain rule predicts 98.7% |
| Local direction: what the start's arrangement decides | Continue | Two sharp exceptions: chains born apart add one; rings of five grow without chains, sometimes faster than any power |
| Broader exploration: where dimension comes from | Known alternatives | A cap, a price, the start's open distinctions, or (here) the typical arrangement |
| Long-term goal: G17 Typical and rare meeting patterns (with G2) | Capability gained | Two is the typical dimension of cheapest parity growth over unchosen arrangements; three is rare, not forced |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Rings of five knots that grow faster than any power with no chain born | 2/3 — growth the chain lemma did not expect | 3/3 — seven small rings | prove the per-round ratio for the ring of four four-place and one five-place knot → stop at a proof of exponential growth, or a polynomial | Selected · awaiting go-ahead |
| 2 | The "plus one" when separately born chains combine | 2/3 — would make the rule exact | 3/3 — 145 cases | state when partners are linked, freeze "largest class + 1", test on six knots → stop at a proof or counterexample | Alternative · deferred |
| 3 | Serial growth read from distances (`FRESH-COUNT-20261118-001#1`) | 2/3 — tests A104 | 2/3 | as before | Alternative · deferred |
| 4 | B202, a growth whose dimension belongs to the relation | 3/3 | 1/3 | as before | Alternative · deferred (sub-goal) |

**Corrections:** none. **Goals:** G17 checkpoint (capability gained), G2 checkpoint (obstruction learned: three is rare, not forced). **Assumptions:** new A106 (the arrangement weights and cutoffs, a measure). **Basket:** B196, `FRESH-COUNT-20261118-001#1`, B202; none taken. **Advisor:** Fable 5.2 before the freeze. It foresaw the rings that grow without chains and the possibility that separate chains combine; both turned up. **Amendment:** the rerun of unsettled arrangements was capped at 21:06 UTC (logged in the contract).

Referee hand-off: the prior-work line is in the pre-registration (objects-gate passes). The decision note is `research/TOUCH-CENSUS-20261118-001/touch_census.md`.
