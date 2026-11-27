# Referee hand-off: RING-BOND-20261127-001

The design and predictions were frozen in commit 8df7206b94 (`README.md`, `frozen.sha256`). Results are in `out/`, the
tallies in `out/tally.json`, and the reading in `decision.md`. Post-hoc checks, not frozen, are in `post/`.

## Claims, evidence class and where

| Claim | Class | Where |
| --- | --- | --- |
| Every renaming of the start's three knots maps the stage onto itself at rounds 0 to 5; bonds map to bonds; the three round-1 bonds with every law essential form one orbit; relabelled starts grow isomorphic stages through round 5 | computed; with the growth rule, proved for this ring (later births hold no start distinction) | `symmetry.py`, `out/symmetry.json` |
| Under the stage's full symmetry (48 at round 3) no bond at rounds 1 to 3 is fixed | computed, post hoc | `post/` (command in `decision.md`) |
| The three opposite pairs read three-valued against the birth's fresh distinction take 16 of 27 triples (19 without the birth's law); every law essential; every pair takes all nine; unchanged by every renaming | computed | `out/symmetry.json`, "P1.4 three-valued" |
| The knot checker passes each round-1 bond's clause in every contact role; the birth's law is essential in all nine round-1 bonds | computed | `out/ring.json` |
| The collapse rule agrees with the bond search on every bond checked | computed | `collapse.py`, `out/collapse.json` |
| Ring counts: bonds 0, 9, 411, 9,121, 44,483 at rounds 0 to 4; with every law essential 0, 3, 144, 234, 0; the round-3 ones all three carriers of three missing 111 | computed | `out/ring.json` |
| Bonds of the round before are kept, except 14 of 9,121 at round 4, each holding a pair that a round-4 birth holds | computed (the cause post hoc) | `out/ring.json`, `post/p44_and_lost.txt` |
| Bonds need no ring and no growth: a chain of three three-place knots holds 16 | computed, post hoc | `decision.md` |
| No bond of the layer above on the clusters read; on every disjoint-carrier cluster of round 2 the bonds together present their readings' joint image | computed (the second part post hoc) | `layer2.py`, `out/layer2_*.json`, `post/l2_extra.py`, `post/l2_extra.json` |
| Census sample (1,000 held-out starts, holders ≤ 4): the not-all-equal and parity tallies | computed | `census_bonds.py`, `out/census_*.jsonl`, `tally.py`, `out/tally.json` |
| Under parity every bond is a consequence of sums of laws read through agreements | proved (linearity), checked by the six-distinction sums | `README.md`, "Proved"; `out/tally.json` |

## Points to press

1. **The definition of a bond.** It uses agreement readings on carriers of two or three distinctions, says "read at a
   knot" for a function of that knot's values, and in the local search takes connected holders with the carriers in
   their distinctions. Do the round-0 census bonds survive a stricter reading (for example, no carrier holding two places
   of one knot)? The advisor says the earlier referee's carrier (0,4,6) holds two places of the birth.
2. **Padding.** Full-search bonds whose carriers take in distinctions of inessential knots were excluded from the local
   search. Is any reported count inflated by readings padded with nearly free distinctions?
3. **The layer above.** Only 24 disjoint-carrier clusters exist at round 2 (6 of three bonds), and none at round 1. The
   "none" there could hardly have failed. Find a larger or different construction in which bonds bind again, or show
   that none exists in a stated class.
4. **Selection.** The symmetry argument covers the ring only. On sampled starts with no symmetry, does anything in the
   growth (the births' parents and inputs, the next round) pick some bonds out of the many?
5. **Parity shapes.** The advisor's shape rule failed. Is the "consequence of sums of laws" statement more than the
   linearity of the allowed states, and what does it add?
6. **Earlier work.** Search the record for relations among agreements or equalities (for example the two kinds of
   readings in `OVERLAP-READ`, or `THREE-READERS-AND-GROWTH-20261120-001B`).
