# Which loops of knots feed themselves? A catalogue

Epic `LOOP-CATALOGUE-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead (taking
`SCALE-SHARE-20261119-001#1`). Goal G17. **Refereed:** report [R1](referee-R1/report.md), confirmed with one Narrowing, no Block,
folded in on 19 November (see Referee). **Part U is pending (stress test running, see Record).**

The owner's idea behind it, in his words: "loops of logic, then like eddies in a river that are shared across the universe
essentially there are 'core-libs' kind of processing" (18 November, Pacific time). It is recorded as his direction, not a result,
in THEORY.md and as A109.

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `f7e8519bf` at 05:17 UTC after a pilot
  (disclosed).
- The run went from 05:18 to 06:52 UTC through the shared runner (`LOOP-CATALOGUE-B1`, `runs/loop-catalogue`, 206 cases on 6
  workers). 179 finished; 27 shards of part U went over the memory cap.
- Those 27 are being rerun with every start isolated in a 3 GB, 90 s child process (`LOOP-CATALOGUE-B3`,
  `runs/loop-catalogue-iso`, contract amendments of 06:53 and 06:57 UTC). Part U below reads 440 of its 1,520 starts. **Stress
  test pending** for the rest. The first memory rerun (B2, 5 GB per case) also went over and was stopped.
- Gates: G1–G6 pass ([checks_output.json](../../experiments/LOOP-CATALOGUE-20261119-001B/LOOP-CATALOGUE-20261119-001B-E001_catalogue/checks_output.json)).
- Code: [eddy.py, loopweight.py, catalogue.py, equation.py, sampler.py, job.py, merge.py, posthoc.py](../../experiments/LOOP-CATALOGUE-20261119-001B/LOOP-CATALOGUE-20261119-001B-E001_catalogue/),
  with the pilot in `pilot/`.
- Results: [results_prelim.json](../../artifacts/LOOP-CATALOGUE-20261119-001B/LOOP-CATALOGUE-20261119-001B-E001_catalogue/results_prelim.json)
  (part U partial) and [posthoc.json](../../artifacts/LOOP-CATALOGUE-20261119-001B/LOOP-CATALOGUE-20261119-001B-E001_catalogue/posthoc.json).

**Words.** As in `CLUSTER-ALL-20261119-001`: the candidate map, its blocks, the unrolled map, a cluster. Further words:
- a **loop** is a cycle of the block graph, whose points are knots and blocks;
- a **live** knot still holds an open distinction;
- a start is an **eddy** when its growth is exponential;
- going once round a loop has a **round-weight** W(y), which sums y^(knots taken) over the ways round;
- a loop is **bare** when there is only one way round;
- a **minimal eddy** stops feeding itself when any one spare place or any one knot is removed;
- its **interface** is what joining something to one of its knots does to its rate.

## The answer

**In the owner's terms.**
- **An eddy is a loop of open knots with at least two ways round.**
  - Draw which knots can join which (the candidate map). A start feeds itself exactly when that map holds a loop that the
    growth can go round, and the loop offers a choice somewhere: a spare place, a hanging knot, or a bigger block.
  - A loop with one way round only circulates. The bare ring of five makes 5 junctions every round, forever.
  - Read before growing, this picked every eddy of the touch census (the 13 rings).
  - Set down before growing, on 864,000 fresh arrangements of 5 to 20 knots (516,731 of which do not stall), it called 49
    eddies. All 49 grow exponentially, each exactly as the rule says round by round, and none of the 1,433 non-eddies grown does.
- **Why the many cycles of large starts do not feed.** A loop has to join through open knots, and in large starts almost every
  knot is full: only 14 to 27% of a grower's knots are live (6 to 14 knots, random starts).
  - Growers hold 3.9 (six knots) to 30 (fourteen knots) chordless cycles of knots each, but only 0.015 to 0.43% of those cycles
    are all open.
  - Short cycles never unroll. Three knots in a ring are joined in one go, four make a pair with two common neighbours, and six
    make two groups of three.
  - So only about one grower in 3,800 to 9,000 has a loop at all.
- **The rate is fixed by the round-weight.** Going once round a loop multiplies the count by W(y), so the rate ρ solves
  W(1/ρ) = 1. W is a product of a few pieces:
  - y for each knot on the loop;
  - a factor for each block passed;
  - a factor (1 + U) for whatever hangs off it.
  - The smallest eddies have exactly two ways round, W = y^L (1 + y), so ρ is the real root above 1 of x^(L+1) = x + 1.
- **The catalogue, where the rule holds: one family.** Every minimal eddy up to eight knots that the rule can read is a ring with
  one extra choice. The run grew every one and confirmed it, and each grows identically under not-all-equal:

| Round-weight W | Realized by (minimal starts, up to eight knots) | Ratio: the root of | Ratio |
| --- | --- | --- | --- |
| y^4 (1 + y) | the ring of eight with one spare (its knots join two apart, so it holds two loops of four) | x^5 = x + 1 | 1.1673 |
| y^5 (1 + y) | the ring of five with one spare; the ring of five with a lone knot hung on it | x^6 = x + 1 | 1.1347 |
| y^7 (1 + y) | the ring of seven with one spare; the ring of seven with a lone knot hung on it | x^8 = x + 1 | 1.0970 |

  The same family continues past eight knots. Rings of 9 to 13 with one spare grow at the roots of x^(L+1) = x + 1, with L = n
  for odd n and n/2 for even n: 1.0758, 1.1347, 1.0622, 1.1128, 1.0527.
- **Interfaces: joined parts multiply the round-weight.** On these loops, measured by growth and matching W exactly:

| Joined at a knot of the loop | W is multiplied by |
| --- | --- |
| a spare place | 1 + y |
| a lone knot | 1 + y |
| a lone knot with one spare | 1 + y + y^2 |
| a hanging path of two knots (its far knot carries the floor's endless chain) | (1 + y)/(1 − y) |
| on a side knot instead of the loop, the same pieces nested | e.g. (1 + y + y^2)/(1 + y) for a spare on a hung knot |
| a second loop (the ring of five with a spare) | the count becomes algebraic, with a rate of 2.32 to 2.81, above both |

  The one exception: an even ring holds two separate loops, and a part joined to one of them leaves the other's rate. The start
  then grows at the faster of the two, so the rate need not rise (5 cases on the ring of eight).
- **Is the catalogue finite? Unbounded in number, few in kind, where the rule holds.**
  - There is one minimal eddy per loop length at least. The rates are infinitely many and fall towards 1 as the loop grows.
  - All of them are built from one short list: the loop's knots, the blocks passed, what hangs off, and the joint between two
    loops. These compose by multiplying round-weights and by putting one loop's count inside another's.
  - That is the owner's "core-libs" made exact: a handful of pieces, each acting the same way wherever it sits.
- **Where the rule breaks, more eddies hide.** The cluster rule has two known breaks: overlapping groups of three, and groups of
  three meeting at a knot.
  - On the 440 such starts grown so far (part U, the rest pending), 122 grow exponentially. Among them is the six-knot theta (the
    literature's name for a cycle with a second path across it: the ring of five plus a knot touching two of its knots), growing past 2,000 junctions a round by round 18.
  - 30 of the 122 look minimal, at six to eight knots, with ratios from about 1.13 to explosive. Their minimality is provisional
    until all of part U is read.
  - So "few in kind" holds where the rule holds. The break shapes add self-feeding loops that nothing here describes yet, and they
    are where the next work is.
  - **Part U is not every start the rule cannot decide** (referee R1). The search counted a start outside the rule's scope with no
    loop through distinct blocks as no eddy, without growing it. The referee's exhaustive search to six knots (3,693 starts) found
    one such start that is a minimal eddy: two triangles of knots joined by one shared distinction, with one spare. It grows 6, 7,
    9, 10, 12, 13, 16, 19, 22, 25, 29, 35, 41, 47, … and reaches 1,646 at round 36 (ratio about 1.16). It is in neither the
    catalogue nor part U. Two more such shapes exceed 3 GB in their first rounds, class unknown: two triangles joined by two shared
    distinctions, and the three-regular six-knot graph, both with spares.
  - In random starts of 3 to 5 places the second break shape never fed (42 of 42). Among the catalogue's larger knots, 33 of the
    349 with that shape did.
- **The same under not-all-equal.** Every catalogue entry grows identically under both laws for 12 rounds, as
  `NAE-GROWTH-20261119-001`'s theorem says for any start that never closes.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| G | gates | held | the census's 13 picked exactly; W's rates for four known starts; growth classes; sampler; minimality; 11,117 graphs |
| E1 | rule-eddies are exponential, and the exact ones equal the rule | **held** | 49 of 49, all exact and equal round by round |
| E2 | rule non-eddies are not exponential | **held** | 0 of 1,433 |
| E3 | meeting hyperedges in random starts are not exponential | **held** | 0 of 42 |
| E4 | descriptive thresholds (live share < 0.3; all-live cycles < 2%; loops < 0.1%) | failed | held on the random starts (live 0.14–0.27; all-live 0.02–0.43%; loops 0.011–0.027%); on SCALE-SHARE's chains the live share is 0.25–0.55 and at five and six knots 5.8% and 2.1% of cycles are all-live |
| C1 | catalogue entries exponential, equal to the rule, equal under not-all-equal | **held** | 5 of 5 |
| C2 | W's root equals the rule's rate | failed as scored | 59 of 71; the 12 others had W truncated at 30 terms, cutting an endless chain's series, and all 12 agree to 10^(−5) at 120 terms (post hoc) |
| C3 | minimal one-loop eddies have W(1) = 2 | **held** | 4 of 4 (the ring of eight, with two loops, is read by R2) |
| C4 | no two-loop catalogue entry to eight knots | **held** | all five rational |
| I1 | interface starts equal their rule series | **held** | 105 of 105 |
| I2 | the interface factors at a loop knot | failed as scored | 42 of 64; the scorer kept the advisor's (1 + y)^2 for the path where the pre-registration says (1 + y)/(1 − y), and its on_loop flag also marked 8 hung side knots (knots in a loop block but off the cycle) as loop knots; those 8 carry the nested factors the product law gives. Re-scored at the true loop knots, 56 of 56 agree (post hoc) |
| I3 | every interface raises the rate; ring joins algebraic | failed | 100 of 105 raised; the 5 others sit on the other loop of the ring of eight and leave its rate; all 21 ring joins algebraic |
| R1 | rings with one spare follow W; bare rings constant | failed as scored | 9 of 12; for the even rings W was not computed (two loops), and their rates equal the predicted roots (post hoc) |
| R2 | the ring of eight's placements | **held** | 1.1673 and 1.3247 (the plastic number), as the advisor predicted |
| U1 | meeting hyperedges in the undecided starts are not exponential | failed (preliminary) | 33 of 349 are exponential (part U partial) |

8 of 14 held as scored. Of the six failures, three are the instrument's: W's truncation, the scorer's factor table and its
loop-knot test, and W left uncomputed for two loops. Each holds once corrected post hoc: the fixed scorer is `merge_fixed.py`
(a logged amendment of 07:04 UTC), and its output, beside the frozen verdicts, is
[results_fixed.json](../../artifacts/LOOP-CATALOGUE-20261119-001B/LOOP-CATALOGUE-20261119-001B-E001_catalogue/results_fixed.json). Three are real: E4's thresholds do not
carry to SCALE-SHARE's measure; a part joined to one loop of an even ring does not raise the start's rate; and meeting hyperedges
can feed.

## Why it holds

These statements are about the cover model, the cluster rule's picture of the growth (`RING-PAIR-20261119-001`). They are argued,
not proved in a proof record, and they hold where the rule does. The run checks them on every start it grows.
- **No loop, no eddy.** A piece of the block graph with no loop has finitely many clusters. Its growth closes, or keeps growing
  only through the floor's endless chains, which give polynomial growth (`CLUSTER-ALL-20261119-001`).
- **One loop: the round-weight decides.** Unroll the loop. The piece becomes an endless periodic chain of copies of the loop's
  blocks, with finite trees hanging from it.
  - A cluster either stays inside less than one round of the chain, or crosses k full rounds. A cluster crossing k rounds is
    counted by W^k times its two ends.
  - Summing over k gives a rational count P(y) + Q(y)/(1 − W(y)).
  - If W is a single power of y, the count per round is constant.
  - Otherwise W(1) ≥ 2, and the count grows like C ρ^t, with W(1/ρ) = 1.
  - This is the transfer argument for periodic structures, standard for rational generating functions.
- **The pieces of W** (the advisor's statement, checked by C2):
  - each knot on the loop gives y, times what hangs from it;
  - each block passed gives a transit: a simplex of k knots (1 + y)^(k − 2), a group of three or more all-or-nothing;
  - each side entry gives (1 + U), with U = y Π(1 + U′) over what hangs from it:
    - a spare and a lone hung knot give U = y;
    - a knot with two open places and one join gets the floor's endless chain, U = y/(1 − y).
- **Two loops: branching.** With two independent loops the unrolled map branches at every joint, and the count is algebraic,
  growing like C ρ^t t^(−5/2) (`RING-PAIR-20261119-001`).
- **The smallest eddies.** One choice beyond the single way round gives W = y^L (1 + y), whose rate is the root of
  x^(L+1) − x − 1. That trinomial is irreducible for every L (Selmer 1956), so each loop length has its own rate.
- **Why an even ring's two loops do not help each other.** The ring of 2m knots joins two apart, so its candidate map is two
  separate loops of m: evens and odds.
  - A spare on knot 0 enters knot 0's own loop.
  - A knot hung on knot 0 enters the other loop, through knot 0's simplex.
  - Each loop grows by its own W, and the start by the faster (R2).

## Known results, and what this adds

- **Known, cited once.** Transfer matrices and rational generating functions for periodic structures. The trinomials
  x^n − x − 1 and their irreducibility (Selmer, *Math. Scand.* 4, 1956); their real roots (x^5 = x + 1 gives 1.1673, and
  x^3 = x + 1 gives the plastic number, the smallest Pisot number). Lattice animals on tree-like maps (Fisher and Essam 1961), as
  cited in `RING-PAIR-20261119-001`. The ring formula, the menus F_s and the product law (`RING-FORMULA-20261118-001`,
  `JOIN-GROWTH-20261118-001`).
- **What this adds.**
  - Which cycles of knots feed themselves, as one rule tested on 864,000 fresh starts.
  - Why large starts' cycles do not: their knots are full.
  - The round-weight as the single quantity that sets every one-loop rate, with its pieces measured as interfaces.
  - The exhaustive list of minimal eddies to eight knots inside the rule's domain: one Selmer family.
  - The finding that the rule's break shapes hide further eddies.

## Limitations

- **The theory is argued, not proved,** and it holds where the cluster rule does. The rule itself is computed, with two known
  breaks.
- **Part U is partial:** 440 of 1,520 starts. The 30 growth-minimal entries rely on reductions, 93 of whose statuses are not yet
  known. Classes come from at most 30 rounds or 5,000 junctions, and "exp?" means not quasi-polynomial at any lag up to 12 and
  still rising.
- **Scope of the search:** simple knot graphs (each pair of knots shares at most one distinction), bare sizes plus at most two
  spares, up to eight knots. Starts outside the rule's scope with no loop through distinct blocks were counted as no eddy without
  growing them. At six knots that misses one minimal eddy (referee R1).
- **"Every minimal eddy that the rule can read is a ring with one extra choice"** stays true as worded. But the catalogue together
  with part U is not every minimal eddy to eight knots.
- **One policy (A104)** and the bare-size convention (A107). E4's thresholds were set from the pilot, and they hold only on its
  sampler's measure.

## Referee

Report [R1](referee-R1/report.md), 19 November 2026, by the coordinator's background referee thread: confirmed with one Narrowing,
no Block.
- **Confirmed.**
  - The transfer argument, P + Q/(1 − W).
  - W against growth on all 122 starts: all 74 with a recorded W annihilate exactly, 18 of them needing the endless chain's tail
    c·y^m/(1 − y).
  - The post hoc rescorings: C2; I2, 56 of 56 at true loop knots; R1.
  - The rates are all roots of x^(L+1) = x + 1 and depend on the loop length L, not the number of knots. The ring of eight acts as
    two loops of four, and the rings of ten and twelve give L = 5 and 6. Rings of four and six feed nothing.
  - Minimality: all 37 one-step reductions are quasi-polynomial.
  - E1 and E2: all 49 regrown and exponential, none of 184 sampled non-eddies.
  - Part U: 32 of 34 regrown in full, and the theta and one eight-knot start equal to rounds 18 and 7. The 1,080 pending were not
    checked.
- **Folded in the same day**, logged in `docs/CORRECTIONS.md` and knotlab's `HISTORY.md`: **Narrowing (completeness).** Part U is
  not every start the rule cannot decide. A minimal eddy outside both lists exists at six knots, two triangles joined by one shared
  distinction with one spare, and two more shapes are unknown (The answer, Limitations). The on_loop wording is fixed (the I2 row).
  The three shapes go to `BREAK-EDDIES-20261119-001`.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2), before the freeze.
- **What held.** The round-weight form, the theorem by transfer, W(1) = 2 for minimal eddies, no two-loop entry to eight knots, and
  the even ring's placement check (R2, exact). It also corrected my theta equation.
- **What failed.** Its finite-path factor (1 + y)^2: under bare sizes the far knot carries an endless chain, (1 + y)/(1 − y). This
  was caught in the smoke run and frozen correctly, but the scorer kept the advisor's form.
- **Not tested.** Its mechanism for meeting hyperedges, that a loop knot needs an open distinction left after round 1. Part U's 33
  exponential cases are where to test it.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: which loops feed themselves, and their catalogue | **Status:** Partially successful (8 of 14 held as scored; 3 more hold post hoc) | The eddy rule held on 864,000 fresh starts with no miss. Inside the rule's domain, the catalogue to eight knots is one family with exact interfaces. The break shapes hide more eddies |
| Local direction: the cluster rule as the catalogue's instrument | Continue | Exact where it holds; its two break shapes are where the uncatalogued eddies are |
| Broader exploration: what the cheapest growth builds | Known alternatives | The self-feeding part is loops with choices, rated by a round-weight |
| Long-term goal: G17 | Capability gained | The rare (eddies) explained: a loop of open knots with two ways round, rare because large starts' knots are full |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The eddies in the break shapes: what the growth does where groups of three meet or overlap, and their round-weights | 3/3 — the catalogue's missing part, and the cluster rule's two open breaks at once | 2/3 — part U's 122 exponential starts and the theta to start from | grow the theta and the 30 provisional minimal entries 40 rounds, read their recurrences, and test the advisor's open-distinction mechanism → stop at a round-weight for them, or a shape whose count no finite model fits | Selected · awaiting go-ahead |
| 2 | A growth that reads only the allowed states (`NAE-GROWTH-20261119-001#1`, A108) | 3/3 | 2/3 | as there | Alternative · deferred |
| 3 | The catalogue under larger knots (sizes past bare, three or more spares) and multigraph shares | 2/3 — whether new families appear beyond the Selmer one in the rule's domain | 3/3 — the same search | widen the search → stop at a second family, or none to eight knots | Alternative · deferred |

## Final report as sent (2026-11-19 07:03 UTC)

**Outcome:** A loop of knots feeds itself when it runs through open knots and offers at least two ways round. With one way round it only circulates, as the bare ring of five does at 5 junctions a round forever. Set down before growing, this rule picked 49 self-feeding starts among 864,000 fresh arrangements. All 49 grow exponentially, exactly as predicted round by round, and none of the 1,433 others grown does. Up to eight knots, wherever the rule holds, the self-feeding loops form one small family with exact "interfaces". Where the rule breaks, more of them hide. 8 of 14 frozen predictions held as scored, and 3 more hold once scorer slips are fixed. Closed, referee pending; one part is still running.

- **Why large starts' many cycles don't feed.** A loop has to join through knots that still have an open place. In large starts only 14 to 27% of knots do, so of their 4 to 30 cycles each, only 0.015 to 0.43% are fully open. About one grower in 3,800 to 9,000 has a loop at all.
- **The rate comes from one number per loop.** Going once round multiplies the count by the loop's round-weight W, so the rate solves W = 1.
- **The catalogue, eddies up to eight knots.** All are rings with one extra choice (a spare place, or a hung knot): the rings of five, seven and eight. Each grows at the root of x^(L+1) = x + 1: 1.1347, 1.0970 and 1.1673. Each is identical under not-all-equal. Rings to thirteen continue the family.
- **Interfaces: joined parts multiply W.** A spare or a lone knot multiplies it by 1 + y, a knot with a spare by 1 + y + y², and a hanging path of two by (1 + y)/(1 − y). A second loop turns the count algebraic, at 2.3 to 2.8. On an even ring the two halves are separate loops and don't help each other.
- **Finite?** Unbounded in number (one per loop length, with rates falling towards 1), but few in kind. Every one is built from the same handful of pieces. That is your "core-libs" made exact, though only where the rule holds.
- **Where the rule breaks** (groups of three that meet or overlap), 122 of the 440 starts grown so far feed themselves, including a six-knot theta. Nothing here describes them yet. The rest of that part is still running in the background (marked pending).
- **Real failures:** a part joined to one half of an even ring doesn't raise the rate; groups of three meeting at a knot can feed after all; and a descriptive threshold didn't carry to the other sampler.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: which loops feed themselves, and their catalogue | **Status:** Partially successful (8 of 14 held as scored; 3 more post hoc) | The rule held on 864,000 fresh starts with no miss; one family with exact interfaces where the rule holds; break shapes hide more |
| Local direction: the cluster rule as the catalogue's instrument | Continue | Exact where it holds; its two break shapes are where the uncatalogued eddies are |
| Broader exploration: what the cheapest growth builds | Known alternatives | The self-feeding part is loops with choices, rated by a round-weight |
| Long-term goal: G17 | Capability gained | The rare explained: two ways round through open knots, rare because large starts' knots are full |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The eddies in the break shapes: what the growth does where groups of three meet or overlap, and their round-weights | 3/3 — the catalogue's missing part and the cluster rule's two open breaks at once | 2/3 — 122 exponential starts and the theta to start from | grow the theta and the 30 provisional minimal ones 40 rounds and read their recurrences → stop at a round-weight for them, or a shape no finite model fits | Selected · awaiting go-ahead |
| 2 | A growth that reads only the allowed states (A108) | 3/3 | 2/3 | as in NAE-GROWTH | Alternative · deferred |
| 3 | The catalogue with larger knots and doubled shares | 2/3 — whether a second family appears where the rule holds | 3/3 | widen the search → stop at a second family, or none | Alternative · deferred |

**Corrections:** none for this study. Separately, I folded in the referees' corrections to CLUSTER-ALL (a second break; false rings possible, Narrowing), NAE-GROWTH (99 → 100, Not a block), SCALE-SHARE (the seven-knot ring was false, Narrowing; χ² 4.3) and JOIN-GROWTH (26 tests, not 27, Narrowing). All are logged in docs/CORRECTIONS.md. **Goals:** G17 checkpoint (capability gained). **Assumptions:** A109 added, under challenge (your eddies / core-libs idea in your words, as your direction), with a first history line; also a THEORY.md reading. **Basket:** `SCALE-SHARE-20261119-001#1` taken. **Advisor:** Fable 5.2, before the freeze. It gave the round-weight form, W(1) = 2, no two-loop entry to eight knots and the even-ring placements (all held), and corrected my theta equation. Its hanging-path factor was wrong.

**Referee hand-off.** The decision note is `research/LOOP-CATALOGUE-20261119-001/loop_catalogue.md`; the prior-work line is in the pre-registration (objects-gate passes). Please check:
- the transfer argument for one loop (rate = root of W = 1);
- `loopweight.py`'s W against the rule's series;
- the three post hoc rescorings (C2, I2, R1);
- the minimal-eddy search's reductions;
- part U's 33 exponential starts with meeting groups of three.
