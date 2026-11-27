# Does the step one layer up need a closed system?

`CUT-BOXES-20261127-001`. Background from `UPPER-GROWN-20261127-001`:
- Boxes (six agreements whose eight triples are clauses, binding three agreements of agreements) occur on 49 of the 85
  closed twelve-knot three-place systems, with every knot needed.
- They occur on none of the 2,416 grown stages read.
- A connected grown stage has no closed part. A closed part holds each of its distinctions twice, so no other knot meets
  it, and growth always leaves loose distinctions.

**The argument to test.** Suppose a knot holds a distinction that no other knot of a box's holders holds, and no carrier
reads it. Then that knot can satisfy its law there, so its law is never needed.

In each of the 49 systems, cut one link. A seeded draw (`cut.py`) picks one distinction; it stays with one of its two
knots, and the other knot gets a new distinction of its own. The result is an open system of twelve knots and nineteen
distinctions, two of them loose. It is searched in full for boxes.

## Frozen predictions

- C1. No cut system has a box. The two cut knots each hold a loose distinction, and at most one of those two can lie in
  a carrier: the new distinction cannot, since the boxes before the cut never read it. So at least one cut knot is never
  needed, and every box needed all twelve. A new box on fewer knots would be a box on an open system of at most eleven
  constraining knots, which the closed census never showed.
- C2. The cut systems still have bonds (the lower layer survives openness).

**Scaffolds:** those of A309 (the box form), and the seeded choice of the cut link, one per system. **Advisor:** not
consulted (usage limit). **Compute:** about 1 to 2 minutes a system, in 8 chunks, with a 6G memory cap and a 30-minute
stop.
