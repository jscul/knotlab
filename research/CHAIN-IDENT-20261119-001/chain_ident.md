# The floor's endless chains as pendant chains of the cover

Epic `CHAIN-IDENT-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead for `RING-IDENT-20261119-001#2`. Goal
G17. **Refereed:** report [R1](referee-R1/report.md), confirmed line by line, no Block; one correction to the validation count
(not a block) and four wording points folded into the proof on 19 November (see Referee).

**Record.**
- **The proof:** [proof.md](../../proofs/CHAIN-IDENT-20261119-001A/CHAIN-IDENT-20261119-001A-P001_chains/proof.md) (ticket A).
- **Its machine check:** [machine_check.py](../../proofs/CHAIN-IDENT-20261119-001A/CHAIN-IDENT-20261119-001A-P001_chains/machine_check.py),
  with its output in [machine_check.json](../../proofs/CHAIN-IDENT-20261119-001A/CHAIN-IDENT-20261119-001A-P001_chains/machine_check.json).
- **The advisor:** it checked the statement and the case table before the freeze ([question](advisor/question_1.md),
  [answer](advisor/answer_1_fable.md)).

## The answer

**In the owner's terms.**
- **The floor's chains are part of the map, so the theorem extends.** When a knot takes a distinction from the floor, its leftover
  open distinctions make offshoots in round 1. In the extended map they are points hung on the knot itself.
  - If the knot has three or more open distinctions, the point is a dead end.
  - If it has two, an endless chain hangs from the point.
  - If it has one, two chains hang from it.

  With those chains added, round t's junctions are again exactly the clusters of t + 1 points of the unrolled map:
  - a junction's parents are the points its cluster can lose;
  - its open distinctions are the points just outside;
  - the junctions with one parent are the clusters that run out along a chain.
- **Why the floor fits exactly.** The floor gives a one-parent junction two fresh distinctions where its demand is lower. Along a
  chain that demand is always one, and the extra distinction is exactly the next point of the chain. Every case of the count checks,
  and the advisor confirmed the table.
- **The dimension becomes a theorem.** When the knots' graph is a tree and no piece of the map finishes early (no relay), the
  number of junctions per round is eventually a polynomial of degree R − 1. Here R is the largest number of chains in one piece.
  - In a bare tree, a chain comes from each leaf hanging from a knot of degree 2, so R counts those leaves in one parity class.
  - Dimension two then means two such leaves at even distance, or the two smallest trees.
  - The path of four knots, whose two such leaves are at odd distance, is constant at 4.
- **What stays open.** Relays: a piece with no cycle and no chain finishes while others go on, and the floor then starts a chain
  from its top. That is the next direction, `RING-IDENT-20261119-001#1`. Why two is the census's typical dimension is a fact about
  which trees occur, not proved here.

## Referee

Report [R1](referee-R1/report.md), 19 November 2026, by the coordinator's background referee thread, read line by line, with its own
growth and cluster enumeration. No study code was run.
- **Confirmed.** Theorems 1 and 2 and Corollary 3. Its own check found 81 of 81 in the class to seven knots and 47 of 47 at eight, and
  Theorem 2 held on all 66 trees in the class to round 20. The pair and the paths of three, four and five were regrown as stated.
- **Folded in.**
  - **The relay control, corrected (not a block).** 115 of 137 differ, not 137: the check counted a non-live knot twice. The 22
    stars close by implication, exactly as their clusters do, so (S5⁺) can be weakened to "every live component is infinite, or
    there is only one".
  - **Wording points.** The path of three's leaves each carry a ray, so both classes have R = 2. Case 3's two loose distinctions are
    named for open = 1, k = 1. The program's implied rule is cited. The check's (S6) is noted as not part of the proof.

## Known results, and what this adds

- **Known, cited once.** RING-IDENT's ingredients; compositions of integers.
- **What this adds.**
  - The cheapest growth with the floor equals the clusters of a deck-invariant extended map, with the chains hung on the knots'
    offshoot points.
  - The growth's dimension is a theorem on trees without relays, with its leading coefficient.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: the floor's chains in the cover | **Status:** Successful (proved; the step the advisor feared was not invariant is invariant) | The chains hang from the knots' offshoot points; every case of the count checks; 81 of 81 starts agree |
| Local direction: an exact model of the cheapest parity growth | Continue | Proved now with the floor; relays and round-1 groups of three remain |
| Broader exploration: what the cheapest growth builds | Known alternatives | Clusters of an extended cover: polynomial on trees (degree = chains − 1), rational or algebraic with cycles |
| Long-term goal: G17 | Capability gained | The census's dimensions, typical two included, follow from the map for trees without relays |

**Next step:** Research directions — none selected yet (awaiting the coordinator)

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Relays (`RING-IDENT-20261119-001#1`): a finished piece's top gets a chain; prove the count with that chain added at the top | 3/3 — with it, every tree start of the census is a theorem | 3/3 — the mechanism and examples are known | state the relay's chain as a ray hung at the top cluster, check on the path of five and the spider → stop at a proof, or the first relay that is not one ray | Alternative · next in the basket |
| 2 | Which trees give which dimension: count bare trees by their largest number of degree-2-hung leaves in one parity class, against CLUSTER-ALL's census shares | 2/3 — explains why two is typical | 3/3 — the census exists | tally the census's trees by R → stop at the share of two, compared with the measured share | Alternative · proposed |
| 3 | First-round groups of three (`RING-IDENT-20261119-001#3`) | 2/3 | 1/3 | as there | Alternative · deferred |

## Final report as sent (2026-11-19 14:04 UTC)

**Outcome:** The theorem extends to starts that take distinctions from the floor, and the growth's dimension becomes a theorem for tree-shaped starts. The step the advisor feared would not be invariant turns out to be invariant: the floor's endless chains hang from points attached to the knots themselves, so they are part of the map of joins. Closed, referee pending.

- **The chains in the map.** A knot's leftover open distinctions make points hung on that knot.
  - With three or more open distinctions, the point is a dead end.
  - With two, one endless chain hangs from it.
  - With one, two chains hang from it.
- **The theorem with chains.** With the chains added, round t's junctions are again exactly the clusters of t + 1 points. The one-parent junctions are the clusters that run out along a chain, and the floor's extra distinction is always the chain's next point. Every case of the count checks, and the advisor confirmed the table.
- **The dimension.** Take a start whose knot graph is a tree, and in which no piece of the map finishes early (no relay). Then the number of junctions per round is eventually a polynomial of degree R − 1, where R is the largest number of chains in one piece. In a bare tree, each leaf hanging from a knot of degree 2 gives one chain. So dimension two means two such leaves at even distance, or one of the two smallest trees. The path of four knots, whose two such leaves are at odd distance, stays constant at 4.
- **The check.** All 81 starts of up to seven knots in the class agree, round by round. All 137 starts with a relay differ, as they should. The advisor's predicted counts all hold: the path of three gives 2t + 2, a single pair of knots gives 2(t + 1), and the path of four gives a constant 4.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: the floor's chains in the cover | **Status:** Successful (proved) | The chains hang from the knots' own offshoot points; every case checks; 81 of 81 starts agree |
| Local direction: an exact model of the cheapest parity growth | Continue | Proved with the floor; relays and first-round groups of three remain |
| Broader exploration: what the cheapest growth builds | Known alternatives | On trees, polynomial of degree chains − 1; with cycles, rational or algebraic |
| Long-term goal: G17 | Capability gained | The census's dimensions follow from the map for trees without relays |

**Next step:** Research directions — none selected yet (awaiting the coordinator)

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Relays: add a chain at a finished piece's top and prove the count | 3/3 — every tree start of the census becomes a theorem | 3/3 | the path of five and the spider first → stop at a proof, or a relay that is not one chain | Alternative · next in the basket |
| 2 | Which trees give which dimension, against CLUSTER-ALL's census shares | 2/3 — why two is typical | 3/3 | tally the census's trees by R → stop at the share of two | Alternative · proposed |
| 3 | First-round groups of three | 2/3 | 1/3 | as in RING-IDENT | Alternative · deferred |

**Corrections:** none new. **Goals:** G17 checkpoint (capability gained). **Assumptions:** none changed. **Basket:** `RING-IDENT-20261119-001#2` taken, and #1 (relays) stays next. **Advisor:** Fable 5.2, before the freeze, staying within its text. It confirmed the case table and the description of the one-parent clusters. It replaced my "at least two live knots" condition with the right one (at least two loose distinctions per piece, which holds automatically here), named the relay as what the class excludes, and fixed the corollary's coefficient and hypothesis. Its four predictions all held.

**Referee hand-off.** The proof is `proofs/CHAIN-IDENT-20261119-001A/CHAIN-IDENT-20261119-001A-P001_chains/proof.md`, and the decision note is `research/CHAIN-IDENT-20261119-001/chain_ident.md`. Please check:
- the fresh table and the implied cases;
- Lemma 0.5 (one-parent clusters);
- Theorem 2's count;
- `machine_check.py`'s extended complex.
