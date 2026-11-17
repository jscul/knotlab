# MODE-BOND-20261117-001: predictions

Frozen at the commit that adds this file, after the advisor's check (`advisor/design_answer.md`), before any computation of Part A on
the patterns or the controls. Seen before:
- TWO-ENDS's results (as narrowed by its referee), CARRIER's, and both referee reports;
- the advisor's expectation: no gadget at about 70–75%, type 5 less certain at about 60%, and a gadget, if any, of type III with
  side-child members and 8 or 9 members.

`mode_bond.py` (the pruned search of the first draft) was written and not run.

- **P1 (the 5 patterns).** No gadget at a level-3 type for any of the 5 patterns, for single crossings. Prediction: 70%.
- **P2 (the controls).** For each of the 5 bounded controls the test finds a gadget, since their stem and block carriers cross long
  stretches of non-product composites. Prediction: 90%. A control with no gadget would mean the test misses carriers, and it would
  be repaired before P1 is read.
- **P3 (paired crossings).** Paired crossings add no gadget for the 5 patterns. Prediction: 80%.
- **P4 (size, if a gadget appears).** Its bond has 8 or 9 members and uses a decoration on a side child (the advisor's guess).

If P1 and P3 hold, and the lemma covers more crossings, the 5 patterns grow linearly (conditional on TWO-ENDS's theorems). If P1
fails and Part B confirms the bond, they are bounded.
