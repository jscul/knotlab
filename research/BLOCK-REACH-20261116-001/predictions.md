# BLOCK-REACH-20261116-001: predictions

Frozen 2026-11-16 20:45 UTC (the commit 169c0d53f; first stamped 21:00, later than the commit, corrected after the referee), after
the advisor's design review (`advisor_design_answer.md`) and before `run_census.py` was run. Seen
before freezing: the exploratory forgetting lengths at stable depth only, with a cap of six steps (`exploratory/forget_windows.py`;
half-rate r = 2 for 19 and 3 for 24; rulers 1 / 2 / 3 for 228 / 152 / 19; other 1 / 2 / 3 / none for 283 / 8 / 1 / 2; undecided 3 / none
for 6 / 2; direct none for 42), and the gate (`gate_forget.json`: 100 window relations equal SAT, no decided census value below the
bound). Not seen: the check at every remaining depth (r_all), the closure that decides "never forgets", the split of the rulers into
acyclic and cyclic, and the upper bounds from census bonds.

- **P1 (the shallow tail changes nothing).** For at least 40 of the 43 small-orbit half-rate descriptions, and at least 90% of the 399
  small-orbit rulers, the forgetting length at every remaining depth equals the exploratory stable one (r_all = r_stable).
- **P2 (never means never).** The closure confirms that the 42 direct descriptions and the 4 non-direct ones without an r within six
  steps never forget at any length.
- **P3 (cyclic rulers forget as fast).** Among the small-orbit rulers, the share with r = 1 among the cyclic ones is within 15
  percentage points of that among the acyclic ones.
- **P4 (upper bounds from depth 9).** For at least half of the decided (description, s) cells of the small-orbit rulers, the census's
  least bond at depth 9 has every member at level 9 − r0 or above (shallower), so its value bounds L_N(3, s) at every depth N ≥ 9.

Settled by construction, not findings: a window that forgets at length r forgets at every longer length; the bound never exceeds a
decided census value (the gate); direct descriptions cannot forget at stable depth with a bounded bond (a forgetting length forces
growth).
