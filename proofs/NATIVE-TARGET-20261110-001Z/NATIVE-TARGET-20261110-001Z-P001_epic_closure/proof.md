# Closure of a native target for learning

Status: Proved

Ticket `NATIVE-TARGET-20261110-001Z`, 2026-11-10.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/NATIVE-TARGET-20261110-001/native_target.md`; the pre-registration is
  `research/NATIVE-TARGET-20261110-001/preregistration.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | On the class-forced tori (two Fano, 57 thin up to 40 points), a learner that sees its own moves one to three ahead resolves every run and beats random moves on every torus of at least 10 points (at 40 points 12.9 steps at radius 3, against 64.4). | computed (exploratory) | A |
| 2 | A learner that keeps the most states sharing the state's dissonance resolves every run and beats random moves on every such torus (at 40 points 19.3, or 17.9 with sight 1); the count is 2 far from the over-agreeing face and grows near it, unevenly at contact. One size past, to 46 points, the same. | known-with-delta; computed (exploratory) | A |
| 3 | The control that keeps the fewest such states never resolves on the Fano tori and on the thin tori is no better than random. | computed (exploratory) | A |

## Answer

Yes: the outside distance can be replaced by native signals, the learner's sight of its own moves and the count of states that share
the state's dissonance, at about twice its cost.

## Recommendation

**Continue, awaiting the coordinator's go-ahead:** learning that grows a handle (sub-goal B60), now concrete: splice a Fano atom at the
knot sphere's violated line and learn. The decision note gives the two tables.
