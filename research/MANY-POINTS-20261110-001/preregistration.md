# Pre-registration: many points at once

Epic `MANY-POINTS-20261110-001` (backlog B3, G15 stretch goal), written on 2026-11-10 before any run, at the coordinator's go-ahead,
which lifted the hold on B3 now that the two-level space has a proved rule (`NEST-ATOMS-20261110-001`).

## The question

The owner asked for the learning picture "parallelized". In the program's terms (B3): several points of dissonance in one knot space,
updated with no scheduler choosing an order. Do they move independently, or do they meet, cancel or bind? And where can units of the
floor dissonance sit together?

## The space

Space (b) of `NEST-ATOMS-20261110-001`: the outer host K_2 with two composites C(2, leaf) at L0 and L1, for the Fano and the thin (2,1,2)
leaves. Leaves 0 and 1 are in composite C1 (at L0), 2 and 3 in C2 (at L1). Genus 4, so the floor is 3 units; every face is odd, and a face
with a agreeing corners holds (a − 1)/2 units. Regions: R1 and R2 are the faces at C1's and C2's triangles, R0 the other faces. A point is
**outer** if it is a point of the outer host, otherwise in C1 or C2.

## Ticket A: where units can sit together (by hand, then exact by SAT over every state)

**From the theorem** (lemma U of `NEST-ATOMS-20261110-001A` and the floor count), at the floor, with u_r the units in R_r:
u_1 ≥ 1 + [C1 acts], u_2 ≥ 1 + [C2 acts], u_0 ≥ 0, and u_0 + u_1 + u_2 = 3. So:
- **A1 (proved).** No region holds three units, and the two composites never act together at the floor. If C1 acts, (u_0, u_1, u_2) =
  (0, 2, 1); if C2 acts, (0, 1, 2); if neither acts, one of (1, 1, 1), (0, 2, 1), (0, 1, 2).
- **A2 (predicted).** In every one of the 256 classes, every distribution A1 allows there is realized by some floor state.
- **A3 (proved).** Where a composite acts, its two units sit one in each of its leaves' regions and none on its sphere part.
- **A4 (recorded, no prediction).** Where a composite holds two units without acting, where they sit.

The check decides, in every class, each distribution by SAT (every line satisfied, the units of each region fixed by cardinality
constraints), and A3 and A4 by SAT on leaf regions. **Failure:** a distribution A1 excludes being realized (the theorem or the code is
wrong).

## Ticket B: two points at once (computed)

- **Floors.** For each leaf type, the four configurations written by `ADDRESS-SEQ-20261110-001A`'s frozen targeted search from
  `NEST-ATOMS-20261110-001C`'s start toward A1 = {0, 1, 2}, A2 = {0, 2, 3}, A4 = {0, 1, 3} and A3 = {1, 2, 3}, each search from that
  start.
- **A point** is a disturbance: one state point flipped at a floor. **Two points** are two such flips, p and q.
- **Pairs.** Four categories: both in different composites; both in the same composite; both outer; one outer and one in a composite.
  For each floor, 40 unordered pairs per category, sampled uniformly with random.Random(3): 1,280 pairs in all.
- **The rule D**, deterministic: among the learner's moves (`LEARN-RISE-20261110-001A`'s state flips and learning steps at A26 sites),
  take one that lowers the dissonance weight W most, the first listed on ties, until the floor or until no move lowers W (stuck), at most
  60 moves. D_p is its move sequence from the floor with p flipped.
- **Measures.** The interaction I = ΔW(p, q) − ΔW(p) − ΔW(q), each ΔW the rise of W above the floor. The **grid** of D_p and D_q: the
  configuration after i moves of D_p and j of D_q from the floor with both flipped, for all i and j; every interleaving of the two
  sequences is a path through it, so "in every order" means every grid step is a legal move (a flip, or a learning step at a site that is
  a dissonance there) that does not raise W. The **end** is the grid's far corner.
- **Classes.** A pair with D_p or D_q stuck is **single-stuck** and set aside. Otherwise: **cancel** if I < 0; **bind** if I > 0;
  **independent** if I = 0, D_p and D_q share no move, every grid step is legal and does not raise W, and the end is at the floor with
  the floor's acting leaves; **meet** otherwise.
- **Memory.** From the floor with both flipped, and from the floor with p alone flipped, the learner M1 runs once each
  (random.Random(3) after the sampling). An address is held when the acting leaves at M1's end are the floor's.
- **Predictions.** B1: at least 90% of different-composite pairs are independent. B2: the independent share is higher for different
  composites than for the same composite and than for outer pairs. B3: in every category the address is held after two points at least
  0.9 times as often as after one.
- **Failure.** Fewer than 50% of different-composite pairs independent, or a held ratio below 0.5 in some category.
- **Stop.** If every category is at least 90% independent, the points move independently under this rule, and B3's question is answered
  that way for it.

## Ticket C: writing with more addresses (computed, a re-test of `NEST-ATOMS-20261110-001C`)

That ticket's procedure unchanged (frozen search, one random outer-host flip, M1), on space (b) and on the same space with the outer host
K_3 (composites at K_3's L0 and its farthest line), for each leaf type; the targets A1, A2, A4, A3 cycled six times (24 writes per space
and leaf type, 96 in all), random.Random(105).
- **Primary,** as frozen there: held when the acting leaves after the return equal the target. **Expected:** at least 95% held for each
  leaf type over both spaces. **Failure:** a write not reached, or under 80% held for a leaf type.
- **Secondary:** the share of exact writes (acting leaves after the write equal the target), and the held share among exact writes.

## Runs

Each check is expected to take under ten minutes; one expected to take longer is registered in `docs/LONG_RUNNING.md` before it is
launched. Assumptions in force: A20, A21, A46, A47, A49, A50, A52.
