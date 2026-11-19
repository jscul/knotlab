# Does one cluster rule predict every growth of touching knots?

Epic `CLUSTER-ALL-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead for `RING-PAIR-20261119-001#1`. Goals
G17 and G2. **Referee pending.**

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `31617b54c` at 02:21 UTC after a pilot on every
  census arrangement of up to four knots (disclosed).
- The test ran from 02:22 UTC through the shared runner (`CLUSTER-ALL-B1`, `runs/cluster-all`, 557 cases on 6 workers, all ok by
  02:25 UTC).
- Code: [clusters.py, job.py, merge.py, checks.py](../../experiments/CLUSTER-ALL-20261119-001B/CLUSTER-ALL-20261119-001B-E001_census/),
  with the pilot and its history in `pilot/`. The post hoc readings are `dimension.py` and `posthoc_dimension.py`.
- Results: [results.json](../../artifacts/CLUSTER-ALL-20261119-001B/CLUSTER-ALL-20261119-001B-E001_census/results.json) and
  [posthoc_dimension.json](../../artifacts/CLUSTER-ALL-20261119-001B/CLUSTER-ALL-20261119-001B-E001_census/posthoc_dimension.json).

"Growth" counts junctions by round. Words as in `RING-PAIR-20261119-001`: the candidate map, the unrolled map, a cluster. Two new
words:
- an **endless chain** is a run of offshoots, each given one distinction beyond its demand by the floor of three places;
- a **relay** is the extra offshoot a finished piece of the map gets when the rest of the start still holds loose distinctions
  (`FIRST-KNOT-20261118-001`'s word).

## The answer

**In the owner's terms.**
- **Nearly one rule for every start.** Draw which knots can join which, unroll it, and add the floor's endless chains. The
  junctions of each round are then the map's clusters of that size.
  - Set down before growing, this gave every round of all 24,383 five-knot census arrangements in its scope (99.5% of the five-knot
    census): every stall, every close and every growth, exponential rings included.
  - It gave every round of 137 of them regrown to 45 rounds.
  - It gave 1,989 of the 1,991 six-knot samples in its scope, and 9 of the 11 hand-built falsifiers in its scope.
- **Where it breaks, one size past.** Two first-round sunflowers that share two knots, with knots of their own on both sides, make
  a piece of the map shaped like four points with one pair unlinked. There one cluster of four carries two junctions at once,
  each made from a different set of three earlier junctions, and the rule counts one. This needs six knots, which is why the
  five-knot census never met it. Two six-knot samples and both of the advisor's overlapping-sunflower falsifiers hit it (P2 and P3
  failed).
- **What the rule says about the census's dimensions** (read after the test, on the whole census).
  - Every growth that does not stall is one of these:
    - it closes;
    - it is fed by endless chains, and its dimension (junctions by round) is the largest number of chains feeding one piece of the
      map;
    - it holds a ring, and it grows exponentially.
  - A knot with two open distinctions left after its first-round joins feeds one chain, a knot with one left feeds two, and a
    finished piece that must go on because the rest of the start still holds loose distinctions feeds two through its relay. A bare
    ring is itself one chain once unrolled.
  - This reproduces the census's measured dimension in all 15,261 polynomial growths in scope, from 0 to 4 (3,623 close, 2,032
    one-dimensional, 9,559 two, 40 three, 7 four), and its 13 fast rings as exponential.
  - So two is typical because a relay, or two knots with one chain each, is the commonest way for a piece to keep growing. Three
    and four need three or four chains on one piece: `FIRST-KNOT-20261118-001`'s mutually touching knots.
- **Rules within rules.** Each piece's count is the same recursion as for two rings: a knot, then for each further block "skip it
  or enter it", with chains as the simplest endless entries. The growth class is then read off the map without growing anything.

| Part | Starts | In scope | Equal to the rule, every round | Verdict |
| --- | --- | --- | --- | --- |
| pilot (fitting): census, up to four knots | 1,939 | 1,901 | 1,901 | — |
| T1: census, five knots | 24,502 | 24,383 | 24,383 | P1 held |
| T5: every 100th of T1 not stalling, to 45 rounds | 137 | 137 | 137 | P4 held |
| T3: random six-knot arrangements | 2,000 | 1,991 | 1,989 | **P2 failed** (2) |
| T4: the advisor's falsifiers | 12 | 11 | 9 | **P3 failed** (2, both overlapping sunflowers) |
| T2 (consistency check): JOIN-GROWTH's recorded starts | 136 grown | 134 | 134 | — |

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| G | gate checks | held | the pilot replays (1,901 equal, 38 out of scope); hand cases; both mutants differ; RING-PAIR's 17 fresh starts agree |
| P1 | every in-scope five-knot census arrangement equals the rule | **held** | 24,383 of 24,383: 10,695 stall, 3,194 close, 10,494 grow (2 to the junction cap); 119 out of scope |
| P2 | every in-scope six-knot sample equals the rule | **failed** | 1,989 of 1,991; the two misses differ from round 3, both with two sunflowers sharing two knots |
| P3 | every in-scope falsifier equals the rule | **failed** | 9 of 11: two triangles sharing one or two knots, a ring of six, the unequal ring of five, two relays, the triangles, the ring of seven and three touching five-place knots all hold; the overlapping sunflowers miss |
| P4 | 45 rounds | **held** | 137 of 137 |

Three of five held, counting G.

## Why it breaks there

In the overlapping-sunflower falsifier, knot w1 touches a, b, c and knot w2 touches b, c, e:
- **Round 1.** The candidate pairs are ab, ac, bc, be, ce. There is no ae, because a and e have no common neighbour.
- **Round 2.** Four junctions form, one on each of the clusters abc, bce, abe and ace.
- **Round 3.** Among those four, abe and ace share no parent. The joining rule's maximal valid sets are then two triples,
  {abc, bce, abe} and {abc, bce, ace}. Both have the union abce, so two junctions sit on one cluster, and the rule counts one.
- **Checked.** The grown round 3 holds two junctions with ancestors {a, b, c, e}, each with three parents.

The advisor's argument for "one junction per cluster" needs every same-size subset of a block present. A block with a missing pair
breaks that. Blocks that are full simplices, or merged simplices whose clusters are all present, keep it.

## Known results, and what this adds

As `RING-PAIR-20261119-001`, cited once there.

What this adds:
- the rule covers the floor's chains, relays, merged sunflowers and first-round groups of three;
- it predicts every round of the whole five-knot census and 99.9% one size past;
- it explains the census's dimensions as chain counts;
- the first counterexample, with its mechanism.

## Limitations

- Computed, not proved.
- The chain-count reading of the dimension is post hoc: it was read on the census after the test. The rule's own long-horizon class
  (to round 160) is what was compared with the census's measured dimension.
- Out of scope: a first-round group of three sharing two knots with another block (119 of the five-knot census). Wrong outside its
  scope: blocks with a missing pair (from six knots).
- One policy (A104); sizes as the census gives them (A106) or bare (A107).

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2), before the freeze.
- It explained the 38 out-of-scope starts and proposed a set-level rule for them. That rule was not frozen; it is direction #1.
- It asked for the scope fraction before the freeze, the scope fixed by hash, T2 marked as a consistency check, the six-knot
  sample reported by class and a horizon check. All are done.
- It gave the relay's hyperedge correction.
- It proposed the falsifiers. Its "partly overlapping simplices; the pair bc arises twice" found the break.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: one cluster rule for every growth of touching knots | **Status:** Partially successful | Exact on every in-scope arrangement through five knots (26,284 with the pilot) and 99.9% at six; first break found, with its mechanism (a cluster carrying two junctions) |
| Local direction: an exact model of the cheapest parity growth | Continue | The break is understood: junctions are valid sets, which equal clusters only when a block's same-size sets are all present |
| Broader exploration: what the cheapest growth builds | Known alternatives | Close; polynomial, of dimension equal to the number of endless chains feeding one piece; or exponential, through a ring |
| Long-term goal: G17 Typical and rare meeting patterns (with G2) | Capability gained | The census's typical two and rare three and four are explained as chain counts, and the growth class is read from the map without growing |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Typical growth at scale: classify, by the rule alone, every arrangement of six and seven knots and large random ones | 3/3 — whether exponential growth (a ring) becomes typical as starts grow, and which dimension is typical: G17's question at sizes no growth can reach | 3/3 — the rule classifies an arrangement in milliseconds; the scope is 99.5% | census six and seven knots by the rule, sample larger ones, and spot-check with growth → stop at the shares of close, each dimension and exponential as the knot count rises, or at a size where the scope collapses | Selected · awaiting go-ahead |
| 2 | Junctions as valid sets: the advisor's set-level rule inside blocks with a missing pair | 2/3 — closes the break | 3/3 — the mechanism and four failing starts | freeze the set-level rule on the blocks, test on the two six-knot misses, the falsifiers and a fresh six-knot sample → stop at all equal, or the next break | Alternative · deferred |
| 3 | Prove the identification (`RING-PAIR-20261119-001#2`) | 3/3 | 2/3 | as there | Alternative · deferred |

- **#1.** Payoff 3/3: G17 asks what is typical and what is rare; the census stopped at five knots because growing is slow. The rule
  makes the class a property of the map, so six, seven and larger starts can be classified exactly where it applies, with growth
  as a spot check. Concreteness 3/3: the code exists and runs in milliseconds. Bound: one epic.
- **#2** ties with #1 on concreteness and is independent; it could run in parallel.

**Corrections:** none to published claims. **Goals:** G17 checkpoint (capability gained) and G2 checkpoint (the census's three
and four dimensions explained as three or four chains on one piece; not forced). **Assumptions:** none new. **Basket:** B196,
`FRESH-COUNT-20261118-001#1`, B202, `PLUS-ONE-20261118-001#1`, `JOIN-GROWTH-20261118-001#2` and `#3`, `RING-PAIR-20261119-001#2`
and `#3`; none taken.
