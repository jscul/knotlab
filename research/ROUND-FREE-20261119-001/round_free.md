# What does the growth build when joins come one at a time, without rounds?

Epic `ROUND-FREE-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead (the round-free test promised to the
owner; `FRESH-COUNT-20261118-001#1`, serial growth testing A104). Goal G17. **Referee pending.**

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `d2ff4b4d8` after a three-order pilot and the
  advisor.
- Runs: `runs/round-free` (328 cases, all ok).
- Code: [serial.py, job.py, merge.py, parts.py, partc.py](../../experiments/ROUND-FREE-20261119-001B/ROUND-FREE-20261119-001B-E001_serial/).
- Results: [results.json](../../artifacts/ROUND-FREE-20261119-001B/ROUND-FREE-20261119-001B-E001_serial/results.json) and
  [partc.json](../../artifacts/ROUND-FREE-20261119-001B/ROUND-FREE-20261119-001B-E001_serial/partc.json).

No law here reads a junction's rank or size; there is no inside clock. "Size" is how many points of the unrolled candidate map a
junction spans (`RING-PAIR-20261119-001`).

## The answer

**In the owner's terms.**
- **Without rounds, what gets built depends on the order, unless the joining reads the map.**
  - We tried two laws that look only at what has been built so far, making one join at a time in random orders. They build
    different things in different orders, and always less than the rounds.
  - The order can even decide whether a growth lives. Two touching three-place knots grow forever under rounds; in 4 of 20 random
    orders they died, and in 16 they kept growing.
  - A lone four-place knot, which closes under rounds, kept growing in 19 of 20 random orders.
- **Why.** The cheapest counts need to know, when a junction is made, how many joins will later take a distinction from it. Its
  partners may not exist yet. The rounds supply that by making all partners at once. That is the work the outside tick was doing.
- **The law that needs no rounds.** Make a junction for a cluster of the map as soon as all its parent junctions exist; nothing
  else is a move.
  - It is order-free: every order reaches the same structure. Making one junction never blocks another, so the result is the same
    whatever comes first (argued, the advisor's argument).
  - It needs no clock. The only before-and-after is that a junction comes after its parents. Junctions of different sizes are
    made in any order.
  - It reads the map instead of a clock. The map says, in advance, which junctions will join which.
- **The ratios survive, read by size instead of by round.**
  - The golden ratio of the ring of five five-place knots, the 1.1347 of the ring with one spare, and the 2.6075 of two joined
    rings are ratios between the numbers of junctions spanning k and k + 1 points.
  - Every junction's round was its size less one all along, so the rounds were counting size. This holds wherever the cluster
    rule holds: RING-PAIR and CLUSTER-ALL.
- **Parts do not grow at their own speeds; the growth lives in the joint.**
  - Counted by size, each part alone keeps exactly its stand-alone growth. Each bare ring of five keeps five junctions per size,
    a ring of seven seven. The spare-distinction ring keeps 5, 6, 7, 8, 9, 10, 11, 13, ..., its own 1.1347 growth.
  - Everything else spans the joint: 97 to 99.9% of the junctions of size 10 or more.
  - So "faster in one place" is said without rounds as: the joined part holds almost all the junctions of each size, while each
    part on its own holds only its own.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| P1 | naive laws build at least two different structures in 20 orders, on every growing start and schedule | **failed** | 12 of 14. Joins first on two touching three-place knots and on a chain of three built one structure in all 20 orders, and in every order it dies after 8 junctions where the rounds grow forever. Order-free there, but wrong. |
| P2 | no naive order reproduces the rounds' ranks 0 to 3 on any growing start | held | 0 of 280 orders |
| P3 | the two touching three-place knots die in some uniform order and pass 400 junctions in another | held | 4 die, 16 pass 400 |
| P4 | in three new joins, parts alone do not grow exponentially, and over 90% of clusters span two or more parts from size 10 | **failed** (first clause) | The share holds in all three (0.968 to 0.999 at size 10). But the ring with a spare keeps its own exponential growth alone (5, 6, 7, ..., 24): each part alone keeps exactly its stand-alone growth, which for that ring is exponential. |

Two of four held. Both failures sharpen the answer: an order-free naive law can be wrong in the same way in every order, and parts
keep their stand-alone growth rather than none.

## Known results, and what this adds

Cited once:
- confluence and step semantics of asynchronous rules: Mazurkiewicz traces; event structures (Nielsen, Plotkin and Winskel 1981);
- the cubic study's remark that asynchronous moves admit trees (`CUBIC-FROM-A-KNOT-20261117-001`).

What this adds:
- for the cheapest parity growth, the measured failure of present-state serial laws;
- an order-free law, read from the cluster map;
- the round shown to be the cluster's size less one;
- part shares by size, with each part keeping its stand-alone growth.

## Limitations

- The naive laws are two schedules of one present-state law. The advisor's three-cause repair test was not run (direction #2).
- The impossibility of any present-state law is a template without a witness pair.
- The closure law's order-independence is argued, not run on the growth.
- Part C counts come from the cluster map (computed by brute force on the cover to size 13), not from serial growth.
- One policy (A104 is now challenged here, not overturned: the rounds' role is identified).

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2), before the freeze.
- It gave the closure law and its order-independence argument.
- It named three causes of order dependence, the impossibility template, and the wording "size counts what a junction spans, not
  when it is made".
- It advised against a random-order point prediction (Pólya urns), so none was frozen.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: what the growth builds without rounds | **Status:** Partially successful (2 of 4 held) | Present-state serial laws are order-dependent, or uniformly wrong, and can decide survival; the order-free law reads the map; ratios and part shares are round-free by size |
| Local direction: A104 (the complete round) | Under challenge | The round does one job: telling a new junction how many partners it will have. The cluster map does that job without a tick |
| Broader exploration: what the cheapest growth builds | Known alternatives | The same structure can be stated with no rounds (clusters by size) |
| Long-term goal: G17 | Capability gained | Growth statements that never mention a round: counts and shares by size |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Typical growth at scale by the rule alone (`CLUSTER-ALL-20261119-001#1`) | 3/3 | 3/3 | as there | Selected · awaiting go-ahead |
| 2 | The three-cause repair test: remove each present-state reading from the naive law | 2/3 — names exactly what a round-free local law must know | 3/3 — the law and runs exist | run the seven repair combinations on the same starts → stop at the smallest repair that restores order-independence and the rounds' result | Alternative · deferred |
| 3 | A witness pair for the impossibility (two starts alike near a junction, one with a late partner) | 2/3 — makes "no local law without the map" a theorem | 2/3 | build the pair for the touching knots → stop at a proof, or a local law that escapes it | Alternative · deferred |

**Corrections:** none. **Goals:** G17 checkpoint (capability gained). **Assumptions:** A104 moves to Under challenge, with a history
line (the round's role identified; the cluster map replaces it in scope). **Basket:** `FRESH-COUNT-20261118-001#1` taken here.
