# The pinwheel grown outward by its own law: interpretation

Experiment `GROWTH-LAW-20261107-001B-E001` (exploratory), run 2026-11-07 under the frozen contract, 73 jobs in 985 s on 20
workers. Rows are in `rows.jsonl`, totals in `result.json`.

## Controls

- **Replays pass.** Growth that follows a genuine pinwheel patch (T_7 in its central tile's frame) reached 500 tiles in the bfs,
  random and finger orders. No genuine continuation was rejected, the move cache agreed with fresh computation throughout the bfs
  replay, and all three final patches embed and pass the radius-2 atlas (0 bad darts).
- **Even the genuine path branches.** On it, 32 of 125 moves (bfs), 31 of 104 (random) and 38 of 84 (finger) had more than one
  legal option. The collar law leaves the pinwheel's growth undecided at about a third of its moves.
- **Legality tests.** The genuine balls of the feasibility checks embed; flipped rectangles fail. So the tests are read.

## Primary observable

Runs that reached 500 tiles with no dead end, per order:

| Order | Runs | Reached 500 | Dead ends at (tiles) |
| --- | --- | --- | --- |
| bfs | 20 | 0 | 18, 33, 34, 41, 55, 77, 80, 97, 99, 101, 116, 132, 138, 154, 192, 205, 230, 241, 241, 304 |
| random | 20 | 0 | 48, 54, 59, 62, 64, 75, 82, 92, 96, 104, 105, 106, 111, 121, 146, 162, 167, 170, 197, 202 |
| finger | 20 | 0 | 46, 48, 53, 54, 59, 59, 59, 75, 78, 81, 101, 113, 120, 131, 135, 149, 175, 221, 243, 281 |
| forced | 10 | 4 | 137, 146, 176, 187, 254, 256 |

## Secondary observables

- **No grown patch is a pinwheel patch.** None of the 70 coin runs' final patches embeds. For the 66 dead ends this is forced: a
  pinwheel patch always has a legal move at every tile, which the replays confirm.
- **Collar-legal patches that are not pinwheel patches.** The four forced runs that reached 500 tiles are collar-legal at every
  tile, yet none embeds. The embedding fails already at level 1 or 2 of the hierarchy. Their interiors break the radius-2 atlas at
  32 to 120 of 214 to 268 darts. So the collar law, which looks one tile around each tile, admits large patches that the
  pinwheel's radius-2 law rejects.
- **How far growth gets.** At the end, the complete radius (every tile within it complete) was 0 to 4 in bfs, 0 or 1 in the
  random order and 0 in the finger order. Forced-first growth reached 1 to 3.
- **Choices.** The coin runs made 607 choices, 70 of them at the seed (54 options each). The other 537 had 2 options 310 times,
  3 options 105 times, and 4 to 10 options 122 times.

## Reading against the decision rule

- **The rule's cases.** Dead ends occurred in every order, and the four runs that avoided them did not stay pinwheel patches.
  So the contract's second and third cases both apply.
- **The finding.** Run as label-free outward growth in any of the four declared orders, with coins at its choices, the
  pinwheel's own collar law left the pinwheel's patches in all 70 runs. Mostly it got stuck within 300 tiles. Forced moves taken
  first sometimes carried it 500 tiles into a collar-legal region that is not the pinwheel.
- **Context.** This is what Dworkin and Shieh (Comm. Math. Phys. 168, 1995) prove must happen for any aperiodic protoset of the
  plane: it has deceptions of every order, patches that pass every local check of that size and extend to no tiling. Here the
  deceptions come at once, at the first few choices.

## Nonclaims

- **Finite runs.** No order is shown to fail always, and none is shown to succeed. The collar law is radius one in tiles, and the
  radius-2 atlas was only used to check the patches.
- **No forcing claim.** The four non-pinwheel patches are finite. They do not show that the collar law admits an infinite
  non-pinwheel tiling.
