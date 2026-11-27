# A growth-made four-clause step on open census stages

Both rival laws produce the four-clause step on census entry 5,246, a start with four three-place knots and one six-place knot. The decisive birth occurs in round four. The three preceding rounds match ordinary growth. In the fourth, each cut retains only one of the two fresh distinctions that ordinary growth assigns to the birth with inputs 13 and 15. This is the only birth changed in either history through that round. [Histories, readings and state counts](open_four_changed.json)

The cut stage has twelve knots, 22 distinctions and five loose distinctions. In order A0, A1, B0, B1, C0, C1, the six readings test agreement on these disjoint carriers.

```
(0,1,5)  (11,12,14)  (2,8,9)  (7,13)  (3,4,10)  (6,15,17)
```

Of the 4,194,304 raw assignments, 173,430 satisfy the twelve source laws. They realize 39 six-reading words. Each of A0 B0 C0, A0 B1 C1, A1 B0 C1 and A1 B1 C0 realizes exactly 000 through 110. The upper readings are “both A”, “either B” and “either C”. If both A readings are 1, every choice of a 1 from B and a 1 from C meets a forbidden triple. All seven other upper words occur. Each carrier member changes its reading under a single allowed bit change. Each lower reading varies at a fixed value of each individual source knot. Each upper reading varies at a fixed value of each chosen lower triple. In the four-clause conjunction, deleting each clause restores 111.

Removing the shortened birth's law, while keeping the carrier distinctions available, restores 468 upper-111 assignments. Under ordinary growth on the same parent stage, substituting the wider law gives 468 upper-111 assignments for the identical six readings. The other two births from that round restore zero upon individual deletion. The census start has ten distinctions, too few for these six disjoint carriers or any six disjoint pairs. The difference in the fourth round establishes dependence on the shortened birth, including its allotment of fresh distinctions.

A second check used census entry 420, the four-knot start with one four-place knot and three three-place knots from the earlier ordinary-growth study. Both rivals keep all the ordinary allotments through round two. The resulting open ten-knot stage has 18 distinctions, five loose, 17,928 allowed states, 39 six-reading words and seven upper words. Its six birth laws separately restore 10, 36, 36, 36, 36 and 36 upper-111 assignments on deletion. This transfers the previously chosen reading to both rivals. [Earlier four-clause specimen](../../UPPER-GROWN-20261127-001/referee-R1/upper_sample.json) · [Independent projected-state check](open_four_transfer.json)

## Search scope

Eight of the ten laws on the second example suffice together for all four lower clauses and the upper exclusion. In order 8, 5, 2, 0, 4, 7, 6 and 9, consecutive three-place laws share one distinction and all other pairs are disjoint. These eight laws alone have 17 distinctions, 13,122 allowed states and the same 39 lower words. Each of the eight laws is essential to 111. The search tried both orders of every eligible sequence of eight such laws and all choices for the two indistinguishable carrier positions at either end, stopping on the first verified witness.

Among the open stages through round six with 17 to 22 distinctions and a freshly shortened birth in the latest round, there are 1,440 stage occurrences under the one-fewer cut and 1,410 under the arity-floor cut. The search ordered each roster by increasing distinctions, knots, census entry and round. The first witness in each roster was the round-four stage described above, visited at position 1,426 or 1,396 respectively. These are occurrence counts in a targeted search. Other four-clause arrangements and their frequency across the census were not run. The same source sequence is absent from all 48 one-fewer and 144 arity-floor open occurrences at or after the two rivals first give different support histories. Those differences begin in round one on 48 starts. [Comparison of the rival histories](open_four_histories.json)

Run from the repository root, one command at a time. Each direct calculation checks all raw assignments on the named stage. The canonical checker is run on the resulting seven-word relation. The first one-law replay took 0.05 seconds. The 100-start shortened-birth pilot took 0.06 seconds, and the complete search took 13.70 seconds, peaking at 102,084 KiB. [Timing of the one-law check](open_four_pilot.json) · [Timing of the open-stage search](open_four_changed_pilot.json)

```sh
ulimit -v 1966080
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ref=research/CLOSED-BY-CUTS-20261127-001/referee-R1
.venv/bin/python -B "$ref/open_four.py" --task transfer --law one_fewer --output "$ref/open_four_pilot.json"
.venv/bin/python -B "$ref/open_four.py" --task transfer --output "$ref/open_four_transfer.json"
.venv/bin/python -B "$ref/open_four.py" --task changed --start-limit 100 --candidate-limit 50 --output "$ref/open_four_changed_pilot.json"
.venv/bin/python -B "$ref/open_four.py" --task changed --output "$ref/open_four_changed.json"
.venv/bin/python -B "$ref/open_four_histories.py" --start-limit 100 --output "$ref/open_four_histories_pilot.json"
.venv/bin/python -B "$ref/open_four_histories.py" --output "$ref/open_four_histories.json"
```
