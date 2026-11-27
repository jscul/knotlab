Read docs/ADVISOR_HIVEMIND.md first and follow its rules. When you have answered, add one entry for this consultation under its consultations marker, and a standing fact only if you checked it in the record.

Study: CYCLE-READ-20261127-001, before the freeze. Read research/CYCLE-READ-20261127-001/README.md (the design and predictions Y1-Y3, and parts 2 and 3), research/GRADED-ORDER-20261126-001/README.md from "The order lemma and a reading for the exception" on (the node reading, the held-out test, the decoupling argument and the twin explanation of its two misses), and the code research/GRADED-ORDER-20261126-001/order.py (NodePiece, predict_nodes with cycles=True), twins.py and graded.py (draw_twins, sample_start with the 'tree+sPP' weighting).

Counterexamples and checks, not verdicts:
1. On a piece with a cycle, is building the core's births by the round rule to rank 25 and counting chains by late.py's binomial terms right? Find a start with a cycle where it must fail (for example where chain births and core births interact through the cycle, or where the decoupling argument's hypothesis fails in a new way on a cycle). Is "a piece with a cycle never relays" right under both laws?
2. The twin test: the explanation says the node reading fails exactly on starts with twin core births sharing two parents C, D and a chain based at a point of a common parent of C and D. Is the decoupling argument in GRADED-ORDER's README correct, and complete (could chain births change core groups in another way, or could chained twins fail to cause a miss)? Your number for "every chained-twin start misses" and "every unchained-twin start agrees".
3. Your numbers for Y1-Y3, and what a referee would press first.
Keep it short.
