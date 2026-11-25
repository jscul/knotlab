# TWO-COUNTINGS-20261125-001A-E001: two countings side by side

The engine of ticket `TWO-COUNTINGS-20261125-001A`, written from the frozen texts (pre-registration, definitions "TD",
claim, knot-test finding, data files) by a helper who did not see the drafter's prototype. Readings taken where the
texts leave a choice: `deviations.md`, each written before the part it affects. Results are referee pending. Every
weighting is supplied; "counting from the finish" counts each allowed state of the finished structure once, "counting
from the start" counts each allowed state of the start once and divides an old state's weight equally among its
completions at each birth. A rule is called a knot only once it has passed the knot test in the whole structure.

## Files

| File | What |
| --- | --- |
| `tc.py` | Structures, histories (stage-by-stage enumeration of allowed states and completions, numpy int64 states), the countings from every stage, lost weight and renormalising, record tables, the score over all two-valued functions and over parities (TD 4.4, exact), hiding, the knot test by projection (`knotlab.knots.check_knot`) and the canonical command |
| `lemma.py` | Setting tests: the four setting pairs' histories, every counting of the family (from each common stage, the two mixed stages, the finish), pooled rows, the hypotheses h0, h1′, h2, h3′, h4 and the lost-weight rule in checkable form (TD 9), the three-way verdict |
| `specs.py` | The registered setting tests built from `structures.json` and TD 4.1 |
| `knottest.py` | Projection and canonical checks of lists of structures |
| `orders.py` | Construction orders (TD 8.1) and C5's class |
| `part1_gates.py` | Part 1: brute force against the engine; the score's methods against each other; Known 1–3 |
| `part8_early.py` | Part 8, early: the 11-knot, 8-knot and smallest-gain structures, projection and canonical, and the finding's statements |
| `part2_lemma.py` | Part 2: every registered lemma test (the 10-knot rounds by the fold study's `pm.py`, unchanged) |
| `part3_signs.py` | Part 3: the 512 sign assignments, both countings, and their knot test by projection |
| `part4_examples.py` | Part 4: E0–E7 |
| `part5_p9.py` | Part 5: P9 on the 194 not-all-equal types |
| `part6_orders.py` | Part 6: the 1,200 construction orders |
| `part7_grow.py` | Part 7: grow again under the 4n renumberings |
| `part8_rest.py` | Part 8, the remainder: projection on every structure of parts 2–4, the canonical command up to the cut |
| `finding_check.py` | The knot-test finding's per-structure table checked against part 8 |
| `part9_engine.py` | Part 9: the engine check of TD 7.3's agreement rule |
| `report.py` | `summary.json` and `summary.md` from the parts' raw files |

Outputs: `artifacts/TWO-COUNTINGS-20261125-001A/TWO-COUNTINGS-20261125-001A-E001_two_countings/` (one JSON file per part,
`summary.json`, `summary.md`).

## How to rerun

From this folder, with the repository's `.venv`: `python -B part1_gates.py`, `python -B part8_early.py 4`,
`python -B part2_lemma.py 4`, `python -B part3_signs.py 4`, `python -B part4_examples.py`, `python -B part5_p9.py 4`,
`python -B part6_orders.py 4`, `python -B part7_grow.py 4`, `python -B part8_rest.py 4`, `python -B part9_engine.py 4`,
`python -B report.py` (the argument is the number of processes; every process caps its memory at 6 GB). The canonical
command is run as `PYTHONPATH=tools python3 -B -m knotlab check --cnf ... --loops ... --contact ... --witnesses ...
--json` from the repository root (with the `.venv` interpreter).

## Imported unchanged

`tools/knotlab` (the canonical checker and `check_knot`); `experiments/PARTS-MEET-AGAIN-20261124-001A/.../pm.py` (the
fold study's growth engine, for the 10-knot rounds, part 7 and part 9).
