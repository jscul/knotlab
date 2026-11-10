# Maps of held inputs and learning them from examples

Status: Proved (theorem D and lemmas G and C by hand) with exact and computed checks. `check.py` (about six minutes, interfaces in
parallel), ticket A of `research/IN-OUT-20261110-001/preregistration.md`, frozen with the code in commit `6d6434df1` before any run on
the test spaces.

## The interface

The world holds two outer points of an atom or composite (inputs a, b); the third is the output, read at the floor (every line satisfied,
no even face) as decided (one value in every floor state), undecided (u) or excluded (x). A map lists the readings at inputs 00, 01, 10,
11 (A58).

## Proved by hand

**Theorem D (self-duality).** Flipping every point flips every literal, so no line's violation and no corner's agreement changes and W is
unchanged. Floor states with inputs x and output v therefore match those with ¬x and ¬v, and every map satisfies f(¬x) = ¬f(x) (¬u = u,
¬x = x). Hence no map is constant, and a total map of two inputs is one of a, b, ¬a, ¬b: AND, OR and XOR are impossible. ∎

**Lemma G (frame).** A gauge flip at a point flips its three signs together with its state, so every literal is unchanged: the map read
under the flipped law at inputs x equals the old map at x with that point's input (or the output) negated. A line complement changes
nothing. So the maps of one class are one map up to negating inputs and output. ∎

**Lemma C (credit).** Floor states restricted to everything outside a group depend on the group only through its relation on its three
sides (the group's own lines touch the rest only there). By `NEST-ATOMS-20261110-001`'s theorem a composite's relation is its line when
every atom inside acts and lets everything through otherwise. So the map at a composite's interface depends on its inner atoms only
through the AND of their acting bits: until all act, every example reads exactly as if none did. ∎

## Computed

**Check 1 (exact, every class).** At the 18 interfaces of S1 to S4 (14 leaves, 4 composites, 3,456 interface-classes), theorem D and
lemma G hold on every class (each map self-dual; each of the three gauge flips transforms it as lemma G says). An acting group computes
a gate (one of `1uu0`, `0uu1`, `u10u`, `u01u`: the output forced exactly when the held sides agree, or exactly when they differ, in the
frame) in 582 of 608 acting leaf-classes and 60 of 64 acting composite-classes; the rest are classes with no floor state at all (18)
and, where two atoms of S1 or S2 share faces, the total map `1010` (the output is ¬b; 12). A transparent group reads `uuuu` in 1,746 of
1,824 leaf-classes and 900 of 960 composite-classes; the rest are gates made by a neighbouring acting atom (36) or input patterns the
host excludes.

**Check 2 (the frozen test).** At each interface the targets in turn, then the impossible `0001`:

| Target | Leaves (14) | Composites (4) |
| --- | --- | --- |
| `1uu0` (NOT gate) | 13 learned and held, 1 inexact | 3 never reached, 1 inexact |
| `u10u` (XOR pattern) | 13 learned and held, 1 inexact | 3 never reached, 1 inexact |
| `uuuu` (off) | 14 learned and held | 1 learned and held, 3 never reached |
| `0uu1` (copy gate) | 13 learned and held, 1 inexact | 3 never reached, 1 inexact |
| `0001` (impossible by D) | 14 never stopped | 4 never stopped |

- Leaves: 53 of 56 learned and held (94.6%). Median 62,600 steps to turn a gate on (`1uu0`, `0uu1`); switching between gates of one acting
  atom (a frame change) is cheaper (median 8,400 steps for `u10u` after `1uu0`).
- Composites: 1 of 16 learned and held, the "off" target. Three composites never reached a gate in 4,000,000 steps; after that failure
  the learner was left above its floor, where it never probes and so never widens its attention, and every later target failed the same
  way (0 probes). The fourth composite (S4's second) stopped three times believing a gate was formed when its map was still `uuuu`.
- Inexact stops: 6, all at S4 (Fano atoms, 90 points), all reading `uuuu`: three at one leaf and three at one composite. In each, a wrong
  output value was reachable at the floor but the probe's 4,000-step walk with it held did not reach it.

## Against the pre-registration

L held (53 of 56; mark 90%), C failed as predicted (1 of 16), A held (18 of 18 never stopped), K held as frozen (composite median
2,024,900 steps against 62,600 at leaves, but the only composite stops with those targets were inexact), and the census held. **R failed:**
6 inexact stops against a prediction of 0.

## What it says

Held inputs give the memory a frame from outside, so it computes maps that are not monotone in its inputs: a single acting atom is a
gate (the NOT gate `1uu0`: when the inputs agree the output is forced to their negation), and a learner that sees only its own dissonance
under the world's clamps learns any of these gates at a leaf's interface from four examples, and switches them off. Every map is
self-dual, so no knot space computes AND, OR or XOR of two held inputs. Learning stops at depth: through a composite the examples see only
the AND of the inner atoms, the learner gets no signal until all act, and it did not find them in its budget. Its probe, a clamped walk,
is also weaker than the native writer's: on the largest space it was fooled six times.
