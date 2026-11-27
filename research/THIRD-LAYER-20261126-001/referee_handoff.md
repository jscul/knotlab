# Referee hand-off: THIRD-LAYER-20261126-001

The note is [README.md](README.md) (frozen section committed at `965e73547a` before the frozen runs); the decision is
[decision.md](decision.md); the scores are [score.json](score.json) from [score.py](score.py); the conjecture is
[conjecture.md](conjecture.md); the recursion note is [recursion_note.md](recursion_note.md).

| # | Claim | Evidence class | Code | Data |
| --- | --- | --- | --- | --- |
| 1 | T1: no birth has parents descended from two start families | computed, frozen | `twokinds.py` (`families`, lineage in `run`) | `frozen_*.jsonl` |
| 2 | T2 and the one relation: on a connected start the families' facts obey exactly one relation, the sum of all its laws | proved (component lemma, conjecture.md (ii)); computed, frozen | `twokinds.py` | `frozen_*.jsonl` |
| 3 | T3: the least change flipping a family's fact grows by at least two distinctions a round | computed, frozen | `minflip.py`, `twokinds.py` | `frozen_*.jsonl` |
| 4 | T4: at the scale of five, the class-fact count is equal at rounds 3 and 4 and contains every family's fact | computed, frozen | `twokinds.py` (`labels_dim`) | `frozen_*.jsonl` |
| 5 | At round 4 and the scale one below the families' flip, the bound facts are held by no part on 10 of 12 three-ring families read | computed, read (no prediction) | `scale.py`, `scale_read.py` | `frozen_scale_read.jsonl` |
| 6 | At small scale the ring and sampled bindings are sums of single-knot facts (the narrowing logged today) | computed, before the freeze | `jointly.py`, `jointly_examples.py` | `jointly_explore.jsonl`, `jointly_examples.jsonl` |
| 7 | The conclusion: one second-layer knot per connected start, so the binding step does not repeat under ordinary growth | argument from 2 with 1, 3, 4 | conjecture.md | as above |

**Points to press.**
- Whether "families" are the right objects: does any class fact that lasts lie outside the span of the families'
  facts (claim T (iii) and (iv) were tested only through T3 on the families and T4's count)?
- Whether the conclusion in 7 follows: could two relations among lasting facts arise from facts other than the
  families' (for example lineages that split during growth), or could second-layer knots share a fact without two
  relations among lasting facts?
- `minflip.least`: the solver's least flipping change, its cap of 40, and the scale read's local facts.
- Scaffolds: register entry A299 (families and the scale of a small change); the census sample (seed 20261215).
