# Under the forbidding cuts, does growth close a stage that carries the step one layer up?

`CLOSED-BY-CUTS-20261127-001`. The background:
- Boxes are the step one layer up: six agreements whose eight triples are clauses, binding three agreements of
  agreements.
- They occur on 49 of the 85 closed twelve-knot three-place systems and none smaller (`UPPER-GROWN-20261127-001`).
- One cut removes every one of them (`CUT-BOXES-20261127-001`).
- Ordinary growth never closes a connected stage.
- The rival laws recorded beside it, A129 (a join may receive one fewer fresh distinction) and A130 (only the fresh
  distinctions its arity requires), can close one.

`closed.py` grows every census start under each rival law for at most six rounds. On each stage that becomes closed
after at least one round, it runs the full search for boxes, recording whether a birth's law is needed.

## Explored before freezing

On 150 census starts (seed 11), both laws agreed:
- 1 start closes after growth: a stage of 8 knots and 14 distinctions, after round 2;
- 4 are closed at the start;
- 125 stall;
- 20 are still funded at round 6.

## Frozen predictions

- K1. Under each law, at most 2% of census starts close after growth.
- K2. No stage closed by growth has twelve or more knots. That is fewer than twelve knots, so going by the closed
  census, no box.
- K3. Therefore no box, and no box needing a birth, under either law.

**Scaffolds:** the two rival laws (register A129 and A130), the six-round limit, and the box form (A309).
**Advisor:** not consulted (usage limit).
**Compute:** growth is fast, and only closed stages are searched. The run is 8 chunks per law, with a 6G memory cap and
a 30-minute stop.
