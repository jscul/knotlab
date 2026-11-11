# Pre-registration: parity of five held points

Epic `PARITY-FIVE-20261111-001` (backlog B149, G15 with G16; program learning), written on 2026-11-11 at the coordinator's go-ahead,
before any search for a five-input parity map. The search space, the exact method, what counts as found, as none and as a bound, the caps,
and the learning stage are frozen here with the code in
`proofs/PARITY-FIVE-20261111-001A/PARITY-FIVE-20261111-001A-P001_parity_of_five_held_points/` (`five_lib.py`, `check.py`). Nothing is
tuned after a result is read.

## The question

`PARITY-NEEDS-20261111-001` found that one handle is enough to count three held points: the 8-point lattice torus (2, 0, 4), in its most
constrained class, forces a fourth point to the sum mod 2 of three held ones, and `LEARN-PARITY-20261111-001` showed the unchanged learner
learns and holds that map. Does one handle count further? Is there a lattice torus on which five held points force a sixth to their sum mod
2, and if so, does the same learner learn it?

## What is known before the search

Each item is marked proved, conditional, expected or background, and none of them settles the question.

- **Proved here (theorem D, `IN-OUT-20261110-001`).** Every map of held points is self-dual, f(not x) = not f(x), because the floor states
  are closed under flipping every point. Parity of an even number of held points is not self-dual, so it never occurs. After three inputs,
  five is the next case. This is why B149 asks for five, not four.
- **Proved here, by one line (restriction).** In a five-input parity map, holding two of the inputs at fixed values leaves the parity of
  the other three, or its negation, on the same space and class. So a five-input parity space also computes three-input parity, and every
  obstacle to three-input parity is an obstacle to five-input parity.
- **Conditional (from `PARITY-NEEDS-20261111-001`).** Genus 0 cannot carry a parity gadget whose terminals lie on one face unless P = NP:
  planar NAE-3SAT is polynomial (Moret 1988, through planar max-cut: Orlova and Dorfman 1972, Hadlock 1975), and three four-point parity
  gates sharing a local reference make a crossover (after Lichtenstein 1982). By the restriction, the same holds for five inputs. The least
  genus is therefore at least 1 here too, under the same condition.
- **Proved here, by counting.** Five-input parity at a set of six points needs at least 2^5 = 32 floor states in the class, and the floor
  states' projection onto the six points is then exactly the even-weight or the odd-weight code of length 6. The 8-point torus (2, 0, 4)
  has at most 24 floor states in any class, so it cannot carry it.
- **Expected, not proved (composition).** Parity is associative, so a three-input gadget whose output feeds an input of a second gives
  five-input parity. In this program's gluing (an atom grown at a line, `nest_lib.grow_leaf`) genus adds, so composition suggests that
  genus 2 suffices. Whether the host passes the first atom's output on as the second atom's input is not proved; stage 1c checks it exactly.
- **Background (not used in any claim).** Max-cut is polynomial on graphs of any fixed genus (Galluccio, Loebl and Vondrák 2001; the
  cost grows as 4^g), and Moret's route from NAE-3SAT to max-cut is local, so I expect NAE-3SAT of fixed genus to be polynomial too (not
  checked). Either way it does not bound how many inputs one handle can count: a gadget of fixed genus is consistent with it, and a
  reduction that used one gadget per crossing would have unbounded genus. The crossing-number route gives no bound either
  that I know of: a torus embeds K_7 (Heawood), so one handle can absorb many crossings of a drawing. I know of no published result that
  bounds the arity of parity a genus-1 NAE gadget can carry, or that constructs one beyond three inputs. In weighted counting the picture
  differs: the symmetric parity signatures [1, 0, 1, 0, ...] of every arity are planar matchgate signatures (Valiant 2002, and the
  characterization of symmetric matchgate signatures that followed). That is a statement about weighted perfect matchings, not about solution sets, and is noted only as a contrast.

## The search space (frozen)

- **Stage 1a (search):** every simple, non-degenerate lattice torus with 3 to 24 points (`SL.hnf_sublattices`, as in
  `PARITY-NEEDS-20261111-001`): 421 tori. Every class of each (4 per torus).
- **Stage 1b (extra), only if stage 1a finds no five-input set:** the 342 lattice tori with 25 to 32 points, every class.
- **Stage 1c (composed), always:** the knot sphere K_2 with the torus (2, 0, 4), less a point, grown as an atom at each of its two lines: 30
  points, genus 2, 16 classes. Reported; it bears on composition and on genus, not on the genus-1 question.

## The exact method (frozen)

For each space and class, the floor states (every line satisfied under a Kasteleyn law) are listed by SAT with blocking clauses. A set T of
points carries a parity map of |T| - 1 held inputs exactly when (i) its indicator is a parity check of the floor states, that is, it is
orthogonal over F2 to every difference x - x0 of floor states, and (ii) the floor states' projection onto |T| - 1 of its points has all
2^(|T| - 1) patterns. Then holding those points at any values forces the last to their sum mod 2 plus a constant, and no other map is
possible there. By symmetry, (ii) for the first |T| - 1 points is (ii) for any |T| - 1 of them. Every set of size 4 (three inputs) and 6
(five inputs) is checked. This is exhaustive and exact for each space it finishes; no sampling.

Checks of the method, run before freezing (the harness part, `result_harness.json`, no five-input search):

- **V1:** the five-input harness, run with three held inputs on `LEARN-PARITY-20261111-001`'s torus T1 at seed 9000, reproduced that epic's
  first T1 run exactly, step for step (the learner is unchanged). It took 104 seconds.
- **V2:** the method finds three-input parity on the torus (2, 0, 4) in class 3 only, at the sets (0, 1, 4, 5) and (2, 3, 6, 7), as before.
- **V3 (in stage 1a):** the lattice tori up to 20 points with a three-input parity set must be exactly `PARITY-NEEDS-20261111-001`'s 16.
  If V3 fails, the five-input result of stage 1a is not reported as found or none until the difference is explained.

A feasibility timing, also before freezing, listed the floor states of two 24-point tori (counts only, no parity read): about 4,000 per
class, under half a second per torus.

## What counts as found, none, and a bound

- **Found (exact).** A six-point set passing (i) and (ii) in some class of some space: that space computes five-input parity, exhaustively
  checked. Reported with its torus, class, set and constant.
- **None in a space (exact).** Every class of that space finished and no six-point set passes. Exact for that space only.
- **Not found in the range.** No lattice torus up to 24 (or 32) points has one. This is a statement about lattice tori in that range, not a
  bound: not a proof that genus 1 cannot count five, and not a lower bound on genus. If the search shows a pattern, it is recorded as a
  conjecture, not a theorem.
- **Dropped.** A space over 600 seconds, or a class over 200,000 floor states, is dropped by rule, counted and named. A dropped space or
  class is undecided, never none.

## Stage 2: learning, only if a five-input parity space exists (frozen)

- **Space.** The space with the fewest points that has a five-input set (a lattice torus before the composed space at equal size); its
  first class with one, and its first set in sorted order. The first five points of the set are held, the sixth is read.
- **The learner, unchanged.** `CREDIT-PIN-20261110-001B`'s credit learner with `THREE-IN-20261110-001B`'s sturdier probe extended to every
  input pattern of five held points, otherwise unchanged (positive checks one 4,000-step clamped walk; each negative check four
  25,000-step walks, three from fresh states), through `LEARN-PARITY-20261111-001A`'s harness. V1 shows the extension changes nothing for
  three inputs. Start: the base Kasteleyn law (no class added) at the solver's first satisfying state, relaxed by M1.
- **Runs.** Ten runs, learner seed 9100 + k, budget 8,000,000 steps per target. Targets in turn: five-input parity, its negation, parity
  again (32 examples each). After each stop one random point off the interface (in the composed space, a point of the host sphere) is
  flipped, M1 runs to the floor, and the map is read again by SAT. 90 minutes per run; a run over it is dropped by rule and counts as not
  learned.

## Marks (decisive, one line each)

- **F (exact):** some lattice torus with at most 24 points computes five-input parity (stage 1a).
- **P5 (computed):** if F holds, or stage 1b or 1c finds one, five-input parity (the first target) is learned and held in at least 8 of 10
  runs (the same pass mark as `LEARN-PARITY-20261111-001`).
- Reported: V1 to V3, every five-input space and class, the composed space's result, dropped spaces, the other targets, inexact stops and
  steps. No mark is settled by its own definition: F is computed exhaustively, and P5 is a set of runs.

## Predictions

Low confidence. F holds, on a torus of 12 to 16 points, in its most constrained class, as three-input parity did; the composed space
computes five-input parity too; P5 holds with slower learning than for three inputs (32 examples instead of 8). If F fails, I expect stage
1b to fail as well, and the composed space to be the first five-input parity space found.

## Caps and long runs

Stage 1a is expected to take under ten minutes. Each part runs under `systemd-run` with MemoryMax 24G and no swap: stage 1a capped at 30
minutes, 1b at 60, 1c at 30, stage 2 at 120. Any part expected to exceed ten minutes is registered in `docs/LONG_RUNNING.md` before it
starts; stage 2, if it runs, is registered.

## Stop

A five-input parity space, learned or with a clear statement of what stops the learner; or the exact statement that none exists in the
range and what the composed space shows. Then report and hold.

Assumptions in force: A20, A21, A46, A47, A49, A50, A52, A58.
