# Pre-registration: inputs and outputs

Epic `IN-OUT-20261110-001` (backlog B120, G15, with G16), written on 2026-11-10 before any run on the test spaces, at the coordinator's
go-ahead. The interface, the learner, what counts as learned and each failure are frozen here, with the code in
`proofs/IN-OUT-20261110-001A/IN-OUT-20261110-001A-P001_inputs_and_outputs/` (`io_lib.py`, `check.py`), committed with this file.

## The question

The layered memory has no interface. With points held by the world as inputs and a point read as the output, which maps can a knot
space compute, and can a learner that sees only its own dissonance learn a chosen one from examples, a non-monotone one included?

## The interface (frozen; assumption A58)

An interface is the three outer points of an atom or a composite, on the line it replaced. The world holds the first two (inputs a, b)
at a pattern; the third is the output. At the floor (W = |χ|: every line satisfied and no even face) the output is **decided** at a
pattern when every floor state with those inputs gives it the same value, **undecided** ("u") when both occur, and the pattern is
**excluded** ("x") when no floor state has those inputs. A map is the four readings at inputs 00, 01, 10, 11; for example `1uu0` reads 1
at 00, undecided at 01 and 10, and 0 at 11.

Why not read a composite's role as the output, as B120 first said: a role depends on the law alone, so held inputs cannot change it,
and by theorem M of `NOT-INSIDE-20261110-001` readings of roles are monotone. Why not read only decided values: as theorem D below
shows, a total map of two inputs can only copy or negate one of them.

## Proved before any run (by hand)

- **Theorem D (self-duality).** Flipping every point leaves every literal's equalities unchanged (each literal flips), so no line's
  violation and no corner's agreement changes, and W is unchanged. Hence floor states with inputs x and output v correspond to floor
  states with ¬x and ¬v, and every map satisfies f(¬x) = ¬f(x) (with ¬u = u, ¬x = x). So no map is constant, and as total maps of two
  inputs only a, b, ¬a, ¬b exist: AND, OR and XOR are impossible, and `0001` (AND) can never be learned.
- **Lemma G (frame).** A gauge flip at a point (its three signs, with its state) leaves every literal unchanged, so it changes the map
  only by negating the input or output at that point; a line complement changes nothing. So within a class the maps are one map up to
  negating the inputs and the output.
- **Lemma C (credit).** The map at a composite's interface depends on the law inside the composite only through its relation on its
  sides, which is the line when every atom inside acts and lets everything through otherwise (`NEST-ATOMS-20261110-001`'s theorem). So
  until every atom inside acts, every example reads the same as if none did: the examples carry no information about which inner atom
  to change.

## Not blind

Developed on the dev spaces only (the outer host K_2 with two composites C(2, thin) or C(2, Fano)). There, an acting leaf read on its
sides computed a gate in 63 of 64 of its acting classes and transparent leaves read `uuuu` in 189 of 192; theorem D and lemma G held on
every class. A learner limited to a fixed attention radius never reached Fano leaves or composites; with attention that widens, dev
leaf targets were all learned and held (8 of 8), thin composites 7 of 8, a Fano composite none, and `0001` never stopped (4 of 4).
No run has touched S1 to S4.

## What the learner may use (frozen in `io_lib.py`)

Its own dissonance (violated lines, agreeing corners, W and the change in W of its moves), the floor |χ|, the interface points (where the
world touches it) and the examples: the world holds the inputs and, as a teacher, the output asked for. **It is not the native writer of
`NATIVE-WRITE-20261110-001` and uses no address:** it is never told which atoms exist, where they are, their roles or classes, a target
signing, or a solver's answer. No outside map enters.

- **Probe.** For each example, on a copy, walks of 4,000 state-only Metropolis steps (temperature 0.7) with points held: an example asking
  value y at inputs x passes when the floor is reached with (x, y) held and not with (x, 1 − y); an example asking "u" passes when the
  floor is reached with both. Like the native writer's probe it can be fooled one way only: a wrong value that is reachable but not
  reached. Its reliability is computed, not proved (backlog B130 is the analogue).
- **Attention.** Sign changes are allowed only on attention lines: the lines through the interface points, widened by one step (to the
  lines through any of their points) after every 40 failed probes, up to four steps.
- **Moves.** A state flip of a random point (probability 1/2) or a sign change at a random A21 site on an attention line, accepted by the
  Metropolis rule on W at temperature 2.0 when it touches an attention line and 0.7 otherwise, never above floor + 4.
- **Stop.** Every 200 steps at the floor it probes, and stops when no example fails. Budget 4,000,000 steps per target.

## The test (ticket A)

- **Census (exact).** At every interface of S1 to S4 (14 leaves, 4 composites), the map in every class, theorem D and lemma G checked on
  every class.
- **Learning.** At each of the 18 interfaces, from the space's start (first class with no atom acting, relaxed by M1), the targets in
  turn: `1uu0` (the NOT gate: when the inputs agree the output is forced to their negation), `u10u` (decided exactly when the inputs
  differ, an XOR pattern), `uuuu` (off), `0uu1` (the copy gate), and the impossible `0001`. Learner seed 3000 + k for the k-th interface
  (S1's leaves, S2's, S3's leaves then composites, S4's). After each stop one random outermost-host point off the interface is flipped,
  M1 runs to the floor, and the map is read again.
- **Outcomes, each counted on its own:** learned and held; learned, not held; inexact stop (stopped with another map); not stopped,
  never reached (the map is still `uuuu`: the input never reached a handle); not stopped with another map.

## Marks (decisive, one line each)

- **L:** learning from examples holds at a single atom's interface iff at least 90% of the 56 leaf writes (four targets at 14 leaves)
  are learned and held.
- **C:** it holds at a composite's interface iff at least 90% of the 16 composite writes are learned and held.
- **A:** `0001` never stops (18 of 18), as theorem D requires.
- **R:** inexact stops are counted on their own; predicted 0.
- **K:** the median steps to turn a gate on (targets `1uu0` and `0uu1`, stopped writes) at composites is at least four times that at leaves
  (lemma C: two inner atoms must both act, found by trial).
- **Census:** theorem D and lemma G hold on every class.

## Predictions

L holds; C fails (composites need both inner atoms to act and the examples cannot say which; Fano composites were never reached on dev);
A holds; R: 0; K holds; the census holds. The non-monotone targets `1uu0` and `u10u` are learned at leaves: the inputs are held values,
a frame the world supplies, so theorem M (about stored classes) does not bind them.

## Stop rule (one epic)

One frozen test. Whatever C gives is the answer for this learner at composites; a learner that reaches deeper handles is a new
pre-registration.

Assumptions in force: A20, A21, A46, A47, A49, A50 (its temperature alternative while learning), A52, and A58 (added with this file).
The test is expected to take under ten minutes.
