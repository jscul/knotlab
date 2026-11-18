# Pilot (fitting, before the freeze)

Scripts from the thread's scratch area, kept as run (they import the FIRST-KNOT start library; `gen.py` and `bare.py` used the
engine of `../fastlib.py` once it existed). `results.json` holds the last record of every pilot run: `long/*` (40 to 60 rounds or
500,000 junctions, fast engine), `g_*` and `out_*` (the first runs, freelib's engine, stopped early). Conventions: `keep` gives each
knot shared + round-1 demand + its part's own surplus; `consume` lets the join use a joined knot's surplus first; `b_*` runs use the
bare convention of the census. The provisional read sent to the owner on 2026-11-18 at 23:13 UTC came from the `out_*` and `g_*`
runs.
