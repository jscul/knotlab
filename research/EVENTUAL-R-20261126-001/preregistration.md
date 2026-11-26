# Preregistration: rule R read off the whole structure (parts B and C)

Frozen before `part_b.py` is run on the sample and before `part_c.py` is run. Written 26 November 2026, after the
advisor's attack ([question](advisor_question.md), [answer](advisor_answer.md)), which found three of the first-drafted
predictions entailed by the engine or by construction (no closed component is touched after closing; with the whole's
R no law's sign differs between the knots read so far and the whole; CHSH at most 2 for products of values). They are
kept as checks, not predictions. Part A was run before this freeze, as the cheap direction the previous study named.

## Seen before freezing

The named starts: the ring of three closes with its knots commuting under R, forced odd, one round; the flip formula
held on its three changes; its one growing round has a unique commuting choice of its three open pairs, and the closing
round realises it; a reader signing by GF(2) is contradicted on its four knots' place sets. A 20-start timing pilot was
run on an earlier version of `part_b.py` and its output not read.

## What is run

`part_b.py 300 4`: census starts (forbid.py's census of 7,075 starts of three to five knots; 300 drawn uniformly with
seed 20261128; one vote per start), ordinary parity growth on the canonical engine for up to four rounds (and one more
round's funding test to tell growing from stalled or closed). `part_b.py 0 4 --named`. `part_c.py`.

## Predictions

1. Every sampled start still growing after round 4 has a settled failing knot pair by round 3 (the advisor's: two
   knots with no commuting place pair fail when both hold an odd number of places, and most births hold three).
2. Among sampled starts that close within four rounds, more than one third have every knot pair commuting under R.
3. The flip formula holds with no exception: every change of a knot pair's commutation between rounds is between two
   knots born in the earlier round, with an odd number of common children.
4. At growing rounds before a start's first settled failing pair, the next round realises a commuting choice of the
   open pairs in fewer than half of the cases (one vote per start and round).
5. On closers whose knots commute: where the forced sign is odd, the GF(2) reader is contradicted on at least one read
   set; where it is even, never, unless a knot cuts the pattern.
6. Part C: the three-reader value on the four-knot closure, readers (0,5), (1,4), (2,3), is 4, against 2 for a list of
   values. (Checks, entailed: the largest CHSH on the 21 census types with R1 is at most 2.)
7. Named start, two knots of four and three places sharing one: their pair commutes at round 0 and fails from round 1
   when a birth has both as parents (the advisor's small case).

## Scaffolds named

The round limit (four, plus a funding test), with pairs classed settled or open rather than read as failing; the
engine (canonical); the weighting of starts (uniform over the census, seed 20261128); R itself; the realisation of
values (A_i = X_i Z^{...}, no relations beyond R); the counting state (every knot even but the forced one).

## Deviation after the run (no change in any result)

`part_a.py` and `part_c.py` read the census rows from the previous study's `rule_census.jsonl`, an output that is not
kept in the record; they now recompute the same rows with `rule_census.analyse`. Part B's outputs are kept compressed
(`part_b_census.jsonl.gz`, `part_b_named.jsonl.gz`) and `tally.py` reads them so. Rerun: part A's, part C's and the
tally's outputs are identical (the timing lines once captured in `part_a_out.txt` are gone). `frozen.sha256` keeps the
hashes of the files as frozen.
