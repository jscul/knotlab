# Which growth is typical as starts of touching knots get larger?

Epic `SCALE-SHARE-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead for `CLUSTER-ALL-20261119-001#1`. Goal
G17. **Refereed:** report [R1](referee-R1/report.md), confirmed, no Block, with one Narrowing and one improved check, folded in
on 19 November (see Referee).

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `b5a3277d6` after a pilot and the advisor.
- Run: `SCALE-SHARE-B1`, `runs/scale-share`, 69 cases, all ok.
- Code: [scale.py, job.py, merge.py](../../experiments/SCALE-SHARE-20261119-001B/SCALE-SHARE-20261119-001B-E001_shares/).
- Results: [results.json](../../artifacts/SCALE-SHARE-20261119-001B/SCALE-SHARE-20261119-001B-E001_shares/results.json).

Classes are stated without rounds: a start stalls (some knot is asked for more joins than it has open distinctions), closes,
grows with a dimension equal to the largest number of endless chains feeding one piece of its map, or holds a ring and grows
exponentially (`CLUSTER-ALL-20261119-001`). Shares are over 8,000 Metropolis samples per knot count, uniform over labelled
descriptions (knots of three to five places, any multiplicities, connected), with distinct-arrangement shares by |Aut|/n!.

## The answer

**In the owner's terms.**
- **As starts get larger, almost all of them cannot start.** The share that stalls at once rises: 45% at five knots, 62% at seven,
  78% at ten, 89% at sixteen, 93% at twenty.
  - The advisor's reason, confirmed: among all ways to arrange many knots, most crowd each knot with shared distinctions. The open
    places per knot fall like √(5/n), from 1.2 at five knots to 0.6 at twenty, and some knot is then asked for more joins than it
    has.
  - This is a fact about counting arrangements, not about the rule.
- **Of those that do grow, two dimensions takes over.** Among growing starts, two-dimensional growth is 82% at five knots, 87% at
  seven, 93% at ten and 98% at twenty.
  - One-dimensional growth fades: 17% of growers at five knots, 2% at twenty.
  - Closing fades: 22% of non-stalled starts at five knots, 1.5% at twenty.
  - Three dimensions stays at about 0.3% of growers, and four occurred once in 8,000 at seven knots.
- **Rings stay rare, though cycles abound.** Exponential growth, a ring in the map, is at most 0.1% of growers at every size.
  This holds although the growing starts hold more and more cycles of knots: on average 3.8 at five knots and 22 at twenty. The
  referee regrew every ring the rule found. The seven-knot one is false (CLUSTER-ALL's second break): it grows 7, 8, 9, 10, 11,
  13, 15, …, not 7, 8, 13, 25, 54, …. So the seven-knot ring share is 0, not 0.01%. The other four (two at five knots, one each at
  six and twelve) are real, and "rings stay rare" holds more strongly.
- **The rule's scope holds.**
  - Out of scope (a first-round group of three overlapping another block in two knots): at most 0.4% of starts.
  - The six-knot break shape (overlapping sunflowers): one sample in 8,000 at six knots, and none at the other sizes in these
    samples. The referee's one-size-past spot checks found it at 12 knots. CLUSTER-ALL's second break shape (hyperedges forming a
    cycle of blocks) occurs once in the 64,000 samples, at seven knots, and at 16 knots in the spot checks.
  - Grown and compared with the rule: 998 of 998 non-stalled starts in scope at six, seven, eight, ten and twelve knots, plus 2
    out of scope.
- **So at scale the typical growing start is two-dimensional,** and the typical start of all is one that never begins. A
  three-dimensional or exponential start is rare at every size up to twenty.

| Knots | Stall | Closes | Dim 1 | Dim 2 | Dim 3 | Ring | Two-dim share of growers |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | 44.8% | 11.9% | 7.4% | 35.3% | 0.10% | 0.03% | 82% |
| 6 | 53.5% | 8.7% | 5.5% | 32.1% | 0.10% | 0.01% | 85% |
| 7 | 62.1% | 5.5% | 4.1% | 28.0% | 0.10% | 0.01% (false: 0) | 87% |
| 8 | 67.1% | 4.3% | 3.1% | 25.2% | 0.10% | 0 | 89% |
| 10 | 78.0% | 1.9% | 1.4% | 18.6% | 0.08% | 0 | 93% |
| 12 | 82.4% | 1.0% | 1.0% | 15.4% | 0.03% | 0.01% | 94% |
| 16 | 89.4% | 0.4% | 0.3% | 9.9% | 0.03% | 0 | 97% |
| 20 | 93.2% | 0.1% | 0.1% | 6.6% | 0 | 0 | 98% |

The table gives labelled shares. Distinct shares agree within 0.6 points, and their effective sample size is 7,067 to 7,912 of
8,000.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| P1 | open places per knot ≈ √(5/n), within a factor 1.5, for n ≥ 8 | held | 0.97, 0.88, 0.80, 0.69, 0.61 against 0.79, 0.71, 0.65, 0.56, 0.50 |
| P2 | stalls never fall from 7; non-stall in [0.12, 0.22] at 12, [0.06, 0.13] at 16, [0.03, 0.08] at 20 | held | 0.176, 0.106, 0.068 |
| P3 | −ln(non-stall)/n does not fall from 10 to 20 | **failed** | 0.151, 0.145, 0.140, 0.134: it falls slowly (each step within the 0.01 the scorer allowed, but 0.017 overall). The decay is close to geometric, not faster |
| P4 | closes, among non-stalled, lower at 16 than at 6 | held | 3.6% against 18.7% |
| P5 | dimension two most common; dim 2 : dim 1 in [2.5, 6]; dim 3 ≤ 2%; no dimension four | **failed** | Two is most common at every size. But the ratio rises past 6 from seven knots (6.9 to 50), and one four-dimensional start occurred at seven knots |
| P6 | rings at most 3% at every size | held | at most 0.03% |
| P7 | out of scope ≤ 2%, peaking at 7, 8 or 10 | **failed** | at most 0.41%, peaking at five knots |
| P8 | weightings converge | held | difference 0.006 at 20 |
| P9 | spot checks equal the rule | held | 998 of 998 in scope |
| P10 | break shape ≤ 5% of non-stalled | held | at most 0.03% |

Seven of ten held.

**The sampler's check.** At five knots the sample's labelled shares against the exact census give χ² = 4.3 on four classes. The
run's merge used stale reference shares (taken at the census's close with 200 large arrangements unread) and gave 10.3. The exact
labelled shares are stall 0.4402, closes 0.1212, dimension 1 0.0792 and dimension 2 0.3551 (referee R1). The samples are
autocorrelated, so this is agreement within sampling error.

## Known results, and what this adds

Cited once: Metropolis sampling of constrained multigraphs; random graphs with bounded degree are locally tree-like (sparse random
graph theory). What this adds: the typical growth of large starts of touching knots, read by the cluster rule. Stalls take over
for a counting reason; two dimensions takes over among growers; rings stay rare; the rule's scope holds to twenty knots.

## Limitations

- **Sampled, not enumerated.** Shares near 10⁻⁴ are not resolved: at twenty knots 8,000 samples hold about 540 non-stalled.
- **The rule is verified by growth** only through five knots exhaustively, and here on 998 spot checks at six to twelve. At 16
  and 20 knots the classes rest on the rule. The rule can report a false ring (CLUSTER-ALL's second break): the referee's regrowth
  of every ring and of all 43 samples of dimension 3 or more confirms all but the one at seven knots.
- **The measure is uniform over labelled descriptions** (A106 extended). The stall trend is mostly the measure's.

## Referee

Report [R1](referee-R1/report.md), 19 November 2026, by the coordinator's background referee thread: confirmed, no Block.
- **The sampler is uniform and irreducible.** This is argued for every n and checked exhaustively at 3, 4 and 5 knots. The
  referee's own fresh sampler gives non-stall shares 0.5591, 0.2306 and 0.0665 at 5, 10 and 20 knots, against 0.5516, 0.2205 and
  0.0680 here.
- **P3** is read as failed, with the scorer's pass disclosed, as reported.
- **Regenerated.** All 64 chains were regenerated, and their classes equal the record.
- **Folded in the same day**, logged in `docs/CORRECTIONS.md`:
  1. **Narrowing.** The seven-knot ring is false: it is CLUSTER-ALL's second break shape, and it grows two-dimensionally. The
     seven-knot ring share is 0. The scope sentence now names the second shape, and the six-knot shape found at 12 knots in the
     spot checks. The other four rings, and all 43 samples of dimension 3 or more, equal the referee's growth. No share moves
     beyond sampling error.
  2. **Not a block (an improved check).** `merge.py`'s five-knot reference shares were stale. With the exact labelled shares,
     χ² = 4.3, not 10.3.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2), before the freeze.
- It explained the stall trend as a counting effect (open places per knot ~ √(5/n)); that held.
- It gave eight of the predictions, of which five held. Its "faster than geometric", "ratio within 6" and "peak at 7–10" failed.
- It asked for dispersed chains, spot checks at ten and twelve knots, and effective sample sizes. All are done.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: typical growth at scale | **Status:** Successful (7 of 10 held) | Shares by knot count to twenty, both weightings: stalls take over, two dimensions takes over among growers, rings stay rare; the scope holds |
| Local direction: the cluster rule as a classifier | Continue | Verified by growth on 998 spot checks beyond the census; classifies a start in milliseconds |
| Broader exploration: what the cheapest growth builds | Known alternatives | At scale: mostly nothing (stall), and otherwise two-dimensional growth |
| Long-term goal: G17 | Capability gained | The typical and the rare, by knot count, for the first time beyond five knots |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Why cycles do not make rings: which cycles of knots give exponential growth, and why the growers' many cycles do not | 2/3 — explains why the exponential stays rare | 3/3 — the rule and the samples exist | classify the growers' cycles by length and surplus → stop at a rule for which cycles give rings, or a counterexample | Selected · awaiting go-ahead |
| 2 | Typical growth under a different measure (sizes free, or knots added one at a time): does two-dimensional stay typical when stalls do not dominate? | 2/3 — tests A106 at scale | 3/3 — swap the sampler | sample conditioned on no over-demand → stop at the shares | Alternative · deferred |
| 3 | Junctions as valid sets (`CLUSTER-ALL-20261119-001#2`) | 2/3 | 3/3 | as there | Alternative · deferred |

**Corrections:** none. **Goals:** G17 checkpoint (capability gained). **Assumptions:** A106 history line (the uniform labelled
measure, extended to twenty knots, makes stalls typical for a counting reason). **Basket:** `CLUSTER-ALL-20261119-001#1` taken.

## Final report as sent (2026-11-19 02:53 UTC)

**Outcome:** As starts of touching knots get larger, almost all of them cannot start, and of those that grow, two dimensions takes over. By the cluster rule, over 8,000 sampled arrangements at each size, the share that stalls at once rises from 45% (five knots) to 93% (twenty). Among growers, two-dimensional rises from 82% to 98%. Rings (exponential) stay at most 0.1% of growers. 7 of 10 frozen predictions held. Closed, referee pending.

- **Why stalls take over: counting, not the rule.** Most ways of arranging many knots crowd each knot with shared distinctions. Open places per knot fall like √(5/n), as the advisor predicted, from 1.2 to 0.6, so some knot is asked for more joins than it has.
- **What fades.** One-dimensional growth (17% to 2% of growers) and closing (22% to 1.5% of non-stalled). Three dimensions stays near 0.3% of growers, and four occurred once in 8,000.
- **Rings stay rare though cycles abound.** The growing starts hold 4 to 22 independent cycles of knots on average, yet almost none grows exponentially.
- **The rule's scope holds to twenty knots.** At most 0.4% of starts are out of scope. The six-knot break shape appeared once in 8,000 at six knots and never otherwise. Grown and compared with the rule, 998 of 998 non-stalled starts in scope at six to twelve knots matched every round.
- **Failed predictions:**
  - P3: the per-knot stall rate falls slowly instead of rising, so the decay is near geometric.
  - P5: the two-to-one-dimension ratio passes 6 from seven knots, and one four-dimensional start appeared.
  - P7: out of scope peaks at five knots, not seven to ten.
- **Sampler check.** The five-knot sample is near the exact census's shares (χ² ≈ 10 on 4 classes, with autocorrelated samples).

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: typical growth at scale | **Status:** Successful (7 of 10 held) | Shares by knot count to twenty, both weightings: stalls take over, two dimensions takes over among growers, rings stay rare; the scope holds |
| Local direction: the cluster rule as a classifier | Continue | Verified by growth on 998 spot checks beyond the census; milliseconds per start |
| Broader exploration: what the cheapest growth builds | Known alternatives | At scale: mostly nothing (stall), otherwise two-dimensional growth |
| Long-term goal: G17 | Capability gained | The typical and the rare by knot count, beyond five knots for the first time |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Why cycles do not make rings: which cycles of knots give exponential growth, and why the growers' many cycles do not | 2/3 — explains why the exponential stays rare | 3/3 — rule and samples exist | classify the growers' cycles by length and surplus → stop at a rule for which cycles give rings, or a counterexample | Selected · awaiting go-ahead |
| 2 | Typical growth under a measure where stalls don't dominate (sampling conditioned on no over-demand, or knots added one at a time) | 2/3 — tests A106 at scale | 3/3 — swap the sampler | sample → stop at the shares | Alternative · deferred |
| 3 | Junctions as valid sets (`CLUSTER-ALL-20261119-001#2`) | 2/3 | 3/3 | as there | Alternative · deferred |

**Corrections:** none. **Goals:** G17 checkpoint (capability gained). **Assumptions:** A106 history line (extended to twenty knots, the labelled measure makes stalls typical for a counting reason); no new entry. **Basket:** `CLUSTER-ALL-20261119-001#1` taken. **Advisor:** Fable 5.2, before the freeze. Its counting explanation of the stall trend held (P1, P2). It asked for dispersed chains, spot checks at ten and twelve knots, and effective sample sizes, all done. Three of its eight predictions failed (P3, P5, P7).

**Referee hand-off.** The decision note is `research/SCALE-SHARE-20261119-001/scale_share.md`, and the prior-work line is in the pre-registration (objects-gate passes). Please check:
- the sampler's uniformity (irreducibility under the moves);
- the scorer's stepwise reading of P3, which I report as failed overall.
