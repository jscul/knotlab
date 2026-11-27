The reading as coded should fail Y1 and Y2: I found two faults in `predict_nodes(cycles=True)`, each with a start in your structure files. Everything below is worked by hand from the code and the three structure files; nothing was run, and I opened no grown file, so the freeze is untouched. All claims are `unverified` except the code lines quoted.

## 1. Pieces with a cycle

**"A piece with a cycle never relays" is false as the code defines such a piece.** `order.py` 167 sets `relay = tree and nch == 0 and ...`. `tree` comes from `late.py` 112–114, which is a count on blocks and cells, not "the core never finishes". Two cells sharing two or more knots with no block through both, and two blocks sharing two knots, are counted as a cycle, but the round rule finishes on them with one last birth.

- **`cyc7_treeplus.jsonl` line 28 (draw 335), no chains.** The round-1 groups are {0,1,2,4,5,6} and {1,2,3,4,5}; one birth joins them in round 2 and the core ends. Under not-all-equal that birth gets max(0, 3 − 2, 1) = 1 fresh distinction and relays; the code predicts fresh 0 and nothing after. Expected miss at round 2 under not-all-equal, agreement under parity (one piece, so it closes).
- **`cyc6_uniform.jsonl` line 21 (index 13560), no chains.** The blocks are {1,4,5} and {2,4,5}, with a pendant point at knot 2. Births are 6, 6, 5, 3, 1 in rounds 1 to 5, and two of the round-3 births share two parents (twins with no chain). Expected miss at round 5 under not-all-equal, agreement under parity.

Both are misses with no chain, so Y2 fails too. The fix is to decide the relay by whether the core's layer empties with one last birth, not by `tree`. For a core that never finishes, "never relays" holds under both laws by this argument: every birth has a sibling, so no birth has zero groups (I did not re-open the engine's implied test).

**Chains are counted on a node's points with repeats merged.** `order.py` 126 lists chains per point of `points_of[n]`, and 131–133 take as chain parents every core parent whose points hold the base. On a core that never finishes, a birth whose set in the unrolled map holds two copies of a pendant point with a chain has two chains. Each of its chain births has two parents; the code gives one chain and one chain birth of three parents.

- **`cyc7_treeplus.jsonl` line 52 (draw 109).** The map has the ring 0–3–1–2–4, and knot 6 hangs on knot 1 with a pendant point carrying one chain. The first birth with two copies is the 10-point set p 6 1 2 4 0′ 3′ 1′ 6′ p′, born in round 9. The code predicts (2 parents, 4 fresh); the growth should give (2, 5). Expected miss at round 9 under both laws.
- In general the miss comes at round L + 2j + 2 or earlier, for a ring of L in the map and the chained knot j steps off it.

The core itself (round rule on nodes) I could not fault on a cycle. A set in the unrolled map cannot have twins; twins need cells or repeated blocks.

## 2. The twin explanation

**The decoupling argument is correct for the core's groups.** It is an induction on "a chain birth has at most one core parent", which the README compresses. I went through every mixed family: one chain birth; several at one core parent; a core group with chain births at two core parents; a single core birth with chain births. Only twins A, B sharing C, D, with chain births at C and D that share a parent, break it.

**Twins with the chain force a miss at the twins' own round.** The family {A, B, X, Y} has no common parent, so it merges or adds groups. In every case I went through, the group count of A, B or X changes, and all have two or more parents, so the fresh count changes. That matches rank 6 and round 6 on both known misses. A sharper prediction to freeze is "first differing round = least rank of such twins".

**Not complete for the whole reading.** The chain births themselves are computed, not proved. One gap is the same fault as in draw 109: a chain at a point that two parents of one core birth hold and no common parent of the two holds. In regions where births are plain sets it cannot happen; with cells I could not rule it out. A static flag for it in `twins.py` would tell you whether any unchained miss is this.

**A fault in the bucket labels.** `twins.py` 22–25 with `chained_only=False` (as `draw_twins` calls it) appends and breaks at the first shared pair of parents. Twins sharing three parents are labelled unchained when only a later pair has the chain. Take `any` over all pairs.

**Numbers.**

| Claim | My number |
| --- | --- |
| Every chained-twin start misses | 90% (the risks are a growth that stops before the twins' round, or signatures that happen to match) |
| Every unchained-twin start agrees, with the loop fixed | 75% |
| Every unchained-twin start agrees, as coded | 65% |

## 3. Y1 to Y3 and what a referee presses

| Prediction | As coded | Notes |
| --- | --- | --- |
| Y1 | 2% | About 50% with both faults fixed, or with chained never-finishing pieces reported as not predicted |
| Y2 | 3% | About 75% with the relay fixed |
| Y3 | 40% | Low confidence |

On Y3: draw 109 grows by about 1.32 a round, which I put at 10⁴ to 10⁵ core births by rank 25, under the cap. A map with two unfilled rings grows by about 2.4 a round and passes the cap near rank 16. The quadratic loop at `order.py` 28 will bind before the cap does, and the README has no rule for a core that is slow but under the cap.

A referee would press, in this order:

1. **The population.** It mixes cores that never finish with cores that finish. Stratify by whether the core finishes, and report each apart.
2. **Chains on a never-finishing core.** The two-copies fault above.
3. **Shared code and a supplied weighting in part 2.** The twin flags come from the predictor's own `NodePiece`, and `tree+sPP` is a scaffold chosen to make the kinds.
4. **Machine-dependent selection.** `graded.py` 145 uses a 5-second alarm, which also breaks the no-time-budget rule; use a count.
5. **The exclusion of earlier samples.** `graded.py` 224 skips rows without `sizes`, so the six-knot and census files are not excluded.
6. **The law asymmetry.** Relay misses show only under not-all-equal or with two or more pieces; a referee will read that as the signature of the relay rule.

The hivemind has one consultation entry and one standing fact (the `late.py` count is not "the core never finishes"), both marked `unverified`.
