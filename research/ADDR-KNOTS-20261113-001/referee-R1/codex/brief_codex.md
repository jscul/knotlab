# Independent recomputation and critique: ADDR-KNOTS-20261113-001

You are an independent referee's assistant. The study's census code was written by a coding agent from a frozen spec, so your
recomputation must be **fresh code written from the spec and the mathematics**.

## Rules for this task

- **Do not open or import anything under** `experiments/ADDR-KNOTS-20261113-001A/ADDR-KNOTS-20261113-001A-E001_addressed_census/codex/`
  (the study's implementation) or `research/ADDR-KNOTS-20261113-001/recheck_returns.py` (the thread's recheck). You may read
  `research/ADDR-KNOTS-20261113-001/{codex_spec.md, codex_spec_addendum.md, preregistration.md, addr_knots.md, returns_recheck.json}`,
  the proof `proofs/ADDR-KNOTS-20261113-001B/ADDR-KNOTS-20261113-001B-P001_growing_interfaces/proof.md`, and the records
  `artifacts/ADDR-KNOTS-20261113-001A/ADDR-KNOTS-20261113-001A-E001_addressed_census/{keys.jsonl.gz, draws.jsonl.gz, summary.md,
  summary_compact.json}`.
- Write **only** inside `research/ADDR-KNOTS-20261113-001/referee-R1/codex/`. No git commands that change state; no publishing.
- At most 3 processes and 10 GB; each command under about 15 minutes; the whole task under about 60 minutes. Use
  `/home/jscul/p-vs-np-contact-first/.venv/bin/python -B`. No network.
- Deliverable: `research/ADDR-KNOTS-20261113-001/referee-R1/codex/codex_report.md`, plus scripts and JSON outputs there.

## Points to check (in order of value)

1. **Certified returns.** The 48 descriptions that die at a level and live at a later one (the records' fates/first deaths; the
   keys are in `returns_recheck.json`), and above all the **7 that alternate with level parity**. With your own pattern builder
   (from the spec: addresses, automaton maps, words applying r first then q, placements, level-n knots on distinct triples), and
   your own NAE CNF (two clauses per knot), recompute alive/dead at each level 1..12. For every **alive** level, verify a satisfying
   assignment directly against every knot. For every **dead** level, produce an unsatisfiability **certificate** and check it
   independently: for example a DRUP/DRAT proof from a pysat solver with proof logging, checked by a reverse-unit-propagation checker
   you write yourself (or another exact method, such as exhaustive search over a symmetry-reduced space, where small enough). Do all
   7 alternating ones at every dead level; then as many of the other 41 as time allows, smallest first. Report each certified
   verdict and any failure.
2. **Fresh pattern check on a sample.** For about 30 records of different automaton sizes and placement counts, compare your level
   patterns' knot counts and the pattern hash defined in the spec (if you can reproduce its serialization) with `keys.jsonl.gz`, and
   your fate with the record's.
3. **The relative classes.** For about 20 sampled patterns of each class (bounded, polynomial, exponential, finitary), compute the
   activity class of the relative maps g_j g_i⁻¹ yourself (product automata with inverses, minimised or not; activity = growth of
   the number of non-identity sections per level) and compare with the record's class. Say whether the study's gate checks the
   class or only the action.
4. **Joining counts.** For a few patterns of each class, count the joining knots per level (knots whose three addresses do not all
   share the last k letters, as the note defines tail classes) and compare with `join_n`.
5. **Wording.** Does any sentence call something typical, common or rare beyond "within level 12" and "under this weighting"? Is
   "bounded joining is rare" right at about 8% of weight and patterns?

## Report format (`codex_report.md`)

A verdict line (Confirmed / Confirmed with fixes / Refuted), one short section per point, fixes each marked Block, Narrowing or Not a
block, and the files you wrote.
