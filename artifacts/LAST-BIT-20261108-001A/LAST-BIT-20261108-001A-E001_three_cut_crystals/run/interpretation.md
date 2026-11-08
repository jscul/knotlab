# Interpretation: crystals legal only after three cuts

Experiment `LAST-BIT-20261108-001A-E001` (exploratory, non-promotable; contract in
`experiments/LAST-BIT-20261108-001A/LAST-BIT-20261108-001A-E001_three_cut_crystals/contract.json`). The run took 985 seconds and was
listed in `docs/LONG_RUNNING.md` as LAST-BIT-A1.

## Controls

All three held: classes 1 and 2 reproduce `ONE-BIT-20261108-001B`'s 32 planes legal after one cut and 176 after two; the plain
rectangle lattice gets class 0; and the decoration 10001 / 01100 is admitted by the mixed 4 x 4 plane, so the labelled test can
answer yes.

## Result

- **No collar type is of class 3.** Of the 5,376 collar types of the 96,416 domino-torus planes, 82 are of class 1 (in the level-one
  law), 54 of class 2 (their children are), and none of class 3: a type whose children are not all in the level-one law never has
  all its grandchildren in it either.
- **So there is no crystal here legal only after three cuts**, and nothing new to test with the last decoration, s = 10101 / 00110.
  Within this family the crystal search for it is exhausted: every plane legal after some number of cuts up to three is legal after
  one or two, and those were all tested in `ONE-BIT-20261108-001B`.

## Reading

- **The family stops at two cuts.** Whatever buries a domino crystal's seams does so within two cuts, or not within three.
- **The next crystals must come from elsewhere:** larger tori, or tilings not made of 1 x 2 rectangles.
