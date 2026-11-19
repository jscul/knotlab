['claude-fable-5-2']
**I can't confirm your reading, and I'd hold the freeze.** The pilot isn't reproducible from what is on disk, and the one pilot script I could run fails its own controls against the committed growth.

## What I checked

All of this is against the committed growth (`eddies.py` at HEAD, copied to `/tmp/jm_adv/head/`). I wrote nothing in the repository.

- **The pilot's imports are missing.** `q1_growth`, `q4_blocktree` and `q9_misses.json` are not in the workspace or `/tmp`, so I stubbed the imports. The 36 starts I used are the committed `misses.json`.
- **`pilot_junction_map2.py` disappeared.** It was listed when I started and was gone by 11:49 UTC, so pilot results 2 to 4 have no runnable source and I did not test them.
- **`eddies.py` was changed under me.** The working copy was rewritten at 11:47:31 UTC, uncommitted and not by me. The changed copy gives 4, 7, 11, 19 on the smallest start where HEAD gives 4, 7, 16, 31. I left it alone; anything run against it after 11:47 is suspect.
- **`pilot_cut_lifted.py` does not give result 1.** It differs from the growth at round 1 on all 36, not round 2 (smallest start: 4, 13, 28 against 4, 7, 16). It also fails both controls: two touching knots give 2, 4, 6 against 2, 3, 5, and the chain of three gives 3, 7, 11 against 3, 5, 9.
- **`stage` and `grow_live` in `pilot_junction_map.py` are not the growth.** They agree for two rounds, then go linear: the chain of three gives 3, 5, 9, 13, 17 against 3, 5, 9, 16, 26. So that presentation fails at its second round on any start, with or without an overlap.
- **The "22 against 16" figure.** I could not reproduce the 22. The committed `unrolled_counts` equals the growth at round 2 on all 36 (16 = 16 on the smallest) and first differs at round 3 (34 against 31).

## Question 1: the reading

Not established. Result 2's pattern (right for one round, wrong at the next, on all 36) is what a faulty stage presentation would produce on its own, so it cannot support the reading yet.

Here is what the growth does on the smallest of the 36 (k0 in all three groups; k1, k2, k3 in two each), traced from the committed run:

- **Round 1.** It makes three junctions: A on (k0, k1, k2), B on (k0, k1, k3), C on (k0, k2, k3). Each joins its members by two-knot places only, nine in all. A and B share two members and share no place.
- **Round 2.** The junctions are exactly those nine pairs. The three new knots around A share one new place, and likewise around B and C.
- **Consequence.** In the stage-1 presentation the "loop of length two" between the blocks of A and B is a ring of four knots, A, k0, B, k1, joined by two-knot places. The stage is three such rings sharing sides, through k0.

In rounds 1 and 2 no new knot lies on an original group of three. If that holds throughout, those groups are inert in the stage, and the identification you want is the ordinary one for a ring, where going round returns to the same knot. I have not derived which cluster pairs the unrolled map double-counts.

## Question 2: a corrected count

I have none to offer. The traced structure suggests applying the eddy rule to the three rings of four sharing sides, rather than repairing the block overlap, but I did not compute that weight.

There is also something I could not reconcile. The committed growth's knot count grows by these factors at round 22:

| Start | Factor at round 22 | Recorded rate |
|---|---|---|
| Smallest of the 36 | about 1.4928, steady to four places | 1.3247 |
| Chain of three | about 1.469, still falling slowly | 1.3247 |
| Ring of five with a spare | about 1.475, still falling slowly | 1.2599 |

The first figure is not close to the plastic number. Either "rate" is defined differently from the growth factor of the count, or this needs a stress test before more is built on W = y² (1 + y).

## Question 3: J1 to J3

Not yet. Before any freeze:

1. **Restore a runnable pilot.** Take the growth from the committed `eddies.py` and find out who changed the working copy.
2. **Gate every stage.** The stage presentation must equal the continued growth for 8 rounds on every start and every s, controls included, before any map is compared with it.
3. **Reword J1.** As written it predicts the failure the faulty presentation produces unaided. Define "holds an overlap" over places that a live or later knot lies on, not over the inert original groups.
4. **Re-derive J3.** Use a cut-lifted map that first passes two touching knots and the chain of three.
5. **Add a rate check.** Fit each start's rate from the growth itself at 20 or more rounds, next to its W.

Scratch scripts and outputs are in `/tmp/jm_adv/` (`real.py`, `trace_head.py`, `out5.txt` to `out8.txt`).
