# The floor's endless chains as pendant chains of the cover

Epic `CHAIN-IDENT-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead for `RING-IDENT-20261119-001#2`. Goal
G17. **Referee pending.**

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
