# Towers with nothing drawn: exploratory reading

Run: `.venv/bin/python -B experiments/LOGIC-AXIS-20261107-001C/LOGIC-AXIS-20261107-001C-E001_towers_with_nothing_drawn/run.py`
(2026-11-07, 4.9 s). Raw output: `result.json`.

**Gadgets that add no open ends keep the old knot, and the ruler never stretches.**
- **G0, corner triangle.** This is the 2026-10-20 parity refinement. Over levels 0–5:
  - the bond distance between the original corners stays 2;
  - coarse knots persist (1, 4 and 13 three-place knots beyond the explicit ones at levels 1–3);
  - one open bit is added per substitution, but as a closed cycle of knots, not an open end.
- **G6, corner triangle plus a middle knot (hubs).** Over levels 0–2 the bond distance stays 2, and
  extra three-place knots multiply (4, then 200).

**Gadgets that add open ends stretch the ruler by a level-independent factor.** An open end is a
distinction held by one knot, a dangling loop.

| Gadget | Bond distance a–b, levels 0.. | Fitted form | Copies | Dimension estimate |
| --- | --- | --- | --- | --- |
| G1 star, loop at each corner knot | 2, 4, 10, 28, 82, 244 | 3^k + 1 | 4 | log 4 / log 3 = 1.262 |
| G2 hexagon, loop on each edge knot | 2, 4, 10, 28, 82 | 3^k + 1 | 6 | log 6 / log 3 = 1.631 |
| G4 prism, loop at each outer knot | 2, 4, 13, 49, 193 | 3·4^(k−1) + 1 | 6 | log 6 / log 4 = 1.292 |

**How the numbers were checked.**
- **Two methods agree.** The minimum connected cut agrees with the exhaustive circuit search wherever
  both ran: G0 at levels 0–2, G1 at 0–2, G2 at 0–1, G4 at 0–1.
- **Control.** Without the connectivity constraint, the cut program returns 5 instead of 28 at G1
  level 3.
- **Bond balls.** On G2 at level 3, the open ends within bond distance r of leg a grow with a fitted
  exponent of about 1.7 between r = 6 and r = 30, beside log 6 / log 3 = 1.63.
- **G4's tower is not relation-defined.** It has three-place knots beyond the explicit ones (1 at
  level 1, 6 at level 2), so a relation-defined substitution would differ from the explicit one.
- **Open ends and open bits.** In the stretching gadgets every substitution adds three open ends
  and three open bits.

**Decision rule.** The rule is met: no open ends gives no stretch; open ends give a fixed stretch.
The open-end criterion and the tree formula are proved in `LOGIC-AXIS-20261107-001D`. The dimension
estimates stay exploratory: finite levels, and the gadget is chosen, like a drawing.
