# Independent recomputation and critique: TRUE-BOND-20261113-001

You are an independent referee's assistant. The study's code was written by a coding agent from a frozen spec, so your
recomputation must be **fresh code written from the spec and the mathematics**.

## Rules for this task

- **Do not open or import anything under** `experiments/TRUE-BOND-20261113-001A/TRUE-BOND-20261113-001A-E001_side_branches/codex/`
  (the study's implementation, logs and partial outputs). You may read the spec, the notes, BOND-DEPTH's `census.py`, and the result
  file `artifacts/TRUE-BOND-20261113-001A/TRUE-BOND-20261113-001A-E001_side_branches/true_rates_all.jsonl` (+ `summary.json`).
- Write **only** inside `research/TRUE-BOND-20261113-001/referee-R1/codex/`. No git commands that change state; no publishing.
- The machine is shared with another heavy computation: use **at most 2 processes and 6 GB**, keep each command under about
  10 minutes, and the whole task under about 45 minutes. Use `/home/jscul/p-vs-np-contact-first/.venv/bin/python -B`.
- Deliverable: `research/TRUE-BOND-20261113-001/referee-R1/codex/codex_report.md`, plus scripts and JSON outputs there.

## The study (read these)

- `research/TRUE-BOND-20261113-001/codex_spec.md` (the frozen spec: objects, the summary DP, the generic side table as a least
  fixed point with cost cap L_ray(s) − 2), `preregistration.md`, `true_bond.md` (conclusions).

## Points to check

1. **Fresh recomputation of L(s).** For about 8 small families of the study set (smallest by number of own distinctions and SELF
   calls; include family 911) and s = 1, 2, 3: compute the least bond containing a port of C_0 and an own distinction of C_s by
   **direct satisfiability** on truncations of the infinite pattern to depth s + h (SELF calls below replaced by "arguments in G"),
   for h = 1, 2, 3 (as far as cheap), with members allowed anywhere in the truncation. Report how the value changes with h and compare
   it with the `L` field of `true_rates_all.jsonl` (which comes from the fixed-point side table, i.e. no depth limit on members).
2. **The objects.** Is the fixed-point side table the right object for the spec's L(s) (bonds with members at any depth)? Is the
   validation's "uniform-depth truncation" (side tables of height D − j at C_j, D = s + h) the right finite object to compare with
   brute force? Does the cost cap L_ray(s) − 2 hide any bond of size at most L_ray(s)?
3. **Settled by construction.** Is "side branches never lengthen the bond" (L ≤ L_ray) settled by the definitions?
4. **Selection.** From `true_rates_all.jsonl`, compare the families that reached depth 12 (and depth ≥ 8) with the rest: how many in
   each group have any shortening (L < L_ray at some reached depth)? What do "growth survives in 37/37" and "all 75 reaching depth
   ≥ 8 grow" say about shortened families specifically?
5. **The runs.** Count statuses (done, timeout, memory, incomplete ray, error), say what the 2 errors are (from the rows), and check
   that each of the 226 families appears once.
6. **Wording.** Is anything worded as holding at all depths or as typical, beyond the depths reached?

## Report format (`codex_report.md`)

A verdict line (Confirmed / Confirmed with fixes / Refuted), one short section per point, fixes each marked Block, Narrowing or Not a
block, and the files you wrote.
