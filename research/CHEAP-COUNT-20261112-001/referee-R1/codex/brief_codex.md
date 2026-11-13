# Independent recomputation and critique: CHEAP-COUNT-20261112-001

You are an independent referee's assistant working in this repository. Your job: recompute the key numbers of one closed study
with **your own code** (do not import or call the study's `census.py`), and critique its claims. Be terse and exact.

## Rules for this task

- Write **only** inside `research/CHEAP-COUNT-20261112-001/referee-R1/codex/`. Do not edit, move or delete anything else. Do not
  run git commands that change state (no add, commit, stash, checkout, reset). Do not run any publishing script.
- Use `/home/jscul/p-vs-np-contact-first/.venv/bin/python` (it has `pysat`). Keep every single computation under about 10 minutes
  and 8 GB; if something would take longer, do a smaller version and say so.
- Your final deliverable is `research/CHEAP-COUNT-20261112-001/referee-R1/codex/codex_report.md` plus the scripts you wrote and
  their outputs (JSON) in the same folder.

## The study (read these)

- `research/CHEAP-COUNT-20261112-001/preregistration.md` (frozen predictions G, P1, P2, P3) and `cheap_count.md` (conclusions).
- Code (read only): `experiments/CHEAP-COUNT-20261112-001A/CHEAP-COUNT-20261112-001A-E001_cheapest_counter/census.py`.
- Data: `artifacts/CHEAP-COUNT-20261112-001A/CHEAP-COUNT-20261112-001A-E001_cheapest_counter/{s1.json, s2.json, s3_*.jsonl, summary.json}`.

Setting, briefly: a knot is NAE (not-all-equal) on three distinct Boolean variables. A gadget is a set of knots on 4 named
variables plus f fresh (existential) variables whose projection onto the named four is exactly their even parity. Knots on three
named variables are excluded. The counter: rows of length 3 + r; each new position's variable is tied by a 4-place even parity to
old neighbours (rule 60: new i, old i−1, old i, R; rule 90: new i, old i−1, old i+1, R; rule 150: new i, old i−1, old i, old i+1;
rule 102: new i, old i, old i+1, R; hop: new i, old floor(i/2), old i, R), missing old positions read as the single reference
variable R; the last row is closed by NAE on consecutive triples; alive(t) = the depth-t system is satisfiable.

## Claims to check

1. **S1, least gadget size m*(f).** No gadget for f = 0, 1, 2; m*(3) = 12; m*(4) = m*(5) = m*(6) = 10. Recompute with your own
   encoding, including the unsatisfiability one below each least size. Verify the f = 3 minimal gadgets number exactly 168 (as
   labelled sets of knots) by your own enumeration, and say what the count is up to relabelling the fresh variables and permuting
   the named ones.
2. **Scope of "a parity takes at least 10 NAE knots".** The note states this without restriction on f, but the search stopped at
   f = 6. Decide whether it holds for every f, and if a bound on the useful number of fresh variables is needed, derive it and check
   the remaining cases.
3. **S2.** Rebuild the rule-60 growth (exact parity clauses, and with one f = 3 minimal gadget per position, handling the slot
   collisions at row ends, where two slots are the same variable) and compare alive(t) for t = 1..64 with `s2.json`: rule 60 alive
   at 1–6, 11–14, 27–30, 59–62. Also rules 90, 150, 102 and hop from exact clauses (to 64 if cheap, else 40).
4. **Weight arithmetic.** Recompute the description bits (105.6 for h = 3 helpers and m = 12; 103.6 for h = 4, m = 10) and the
   log2 weight of the 504 counting descriptions (about −97) from the formula in `summarize()`; say whether the formula describes the
   counter's description correctly and whether 504 is a count, a lower bound or neither.
5. **S3 fragility.** 240 single-knot deletions/replacements of the first minimal gadget: 3 keep parity, 169 constant, 68
   eventually constant. Check the count of 240, the 3, and which parts of this are settled by the minimality itself.
6. **Settled by construction or known.** For each conclusion of `cheap_count.md`, say whether it is new, known (give the standard
   reference if you know it), or settled by the definitions.
7. **Honest reporting.** Is the P3 failure (hop does not count) reported honestly? Are rules 90 and 150 described accurately
   ("count too" against "unexplained within 64")?

## Report format (`codex_report.md`)

A verdict line (Confirmed / Confirmed with fixes / Refuted), then one short section per numbered claim: what you recomputed, the
result, and any discrepancy. End with a list of fixes, each marked Block, Narrowing or Not a block, and a list of the files you
wrote.
