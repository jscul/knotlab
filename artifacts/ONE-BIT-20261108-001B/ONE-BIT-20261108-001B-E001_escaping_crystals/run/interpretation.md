# Interpretation: crystals that escape the one-bit decorations

Experiment `ONE-BIT-20261108-001B-E001` (exploratory, non-promotable; contract in
`experiments/ONE-BIT-20261108-001B/ONE-BIT-20261108-001B-E001_escaping_crystals/contract.json`). The run took 632 seconds and was
listed in `docs/LONG_RUNNING.md` as ONE-BIT-B1 once it passed ten minutes.

## Controls

All five held (`result.json`): the rhombus lattice and a period-4 brick plane pass the filter after one cut, the plain rectangle
lattice is set aside, every small-torus plane that `COLLAR-PLANE-20261108-001C` found legal is kept at its first legal level, and
the decoration 10001 / 01100, known to admit a period-4 brick crystal, is admitted.

## The filter (`filter.json`)

- **96,416 planes, 5,376 collar types.** 82 types lie in the level-one law, and 54 more cut into it.
- **Legal after one cut: 32 planes** (4 on each of the 2 × 4 and 4 × 2 tori, 24 on the 4 × 4 torus): the rhombus lattice and the
  period-4 brick rows, as before.
- **Legal after two cuts: 176 planes** (8, 8 and 160). The 160 on the 4 × 4 torus were never tested before; they include mixed
  tilings with dominoes in both directions.
- **11 distinct planes** by their multisets of collar types.

## The labelled tests (`rows.jsonl`)

- **Seven of the eight open decorations escape.** Each is admitted, with a periodic labelling on a torus of index 1, by a crystal
  legal after two cuts on the 4 × 4 torus. One plane does most of the work: a mixed domino tiling, with horizontal dominoes at
  (0, 0), (3, 1), (2, 2) and (1, 3) and vertical ones at (2, 0), (3, 3), (1, 1) and (0, 2), diagonals 0 1 1 0 1 1 0 0. Cut two to
  four times, it admits six of the seven (and the control); a variant with diagonals 1 0 0 1 0 0 1 1 admits two.
- **One does not.** s(0) = 1 0 1 0 1, s(1) = 0 0 1 1 0, with its relabelling 1 1 0 0 1 / 0 1 0 1 0, is admitted by none of the 11
  planes within two levels past their first legal cut.

## Reading

- **One bit per tile, as a decorated substitution, fails in 1,022 of 1,024 cases.** Every failure is a crystal with a periodic
  labelling, so by Lemma 2 of `ROUND-PRICE-20261108-001A` the decoration's law of any radius admits a periodic plane.
- **The last candidate** excludes every crystal tried: the rhombus lattice, two brick families, and the eleven domino-torus planes.
  Its parent labels are forced, but the joint consistency test (`ONE-BIT-20261108-001A`) leaves off-law parent collars, so whether it
  forces the pinwheel is open.
- **A new kind of crystal.** The mixed tiling that defeats most decorations is legal only after two cuts. A wider census of
  periodic planes legal after two or three cuts is the cheapest way to try the last candidate further.
