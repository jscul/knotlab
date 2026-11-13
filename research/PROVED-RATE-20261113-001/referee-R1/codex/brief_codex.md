# Independent recomputation and critique: PROVED-RATE-20261113-001

You are an independent referee's assistant. The study's code was itself written by a coding agent from a frozen spec, so your
recomputation must be **fresh code written from the spec and the mathematics**, not from the study's implementation.

## Rules for this task

- **Do not open or import anything under** `experiments/PROVED-RATE-20261113-001A/PROVED-RATE-20261113-001A-E001_cycle_mean/codex/`
  (the study's implementation and its logs). You may read the spec, the notes, BOND-DEPTH's `census.py` (whose DP the spec
  refactors) and the result files named below.
- Write **only** inside `research/PROVED-RATE-20261113-001/referee-R1/codex/`. Do not edit, move or delete anything else. No git
  commands that change state; no publishing script.
- Use `/home/jscul/p-vs-np-contact-first/.venv/bin/python -B`. Keep each computation under about 10 minutes and 8 GB, at most 4
  processes, and the whole task under about 60 minutes; choose samples by smallest node count where needed and say so.
- Deliverable: `research/PROVED-RATE-20261113-001/referee-R1/codex/codex_report.md`, plus your scripts and JSON outputs there.

## The study (read these)

- `research/PROVED-RATE-20261113-001/codex_spec.md` (the frozen spec), `preregistration.md`, `proved_rate.md` (conclusions).
- DP source: `experiments/BOND-DEPTH-20261112-001A/BOND-DEPTH-20261112-001A-E001_spine_bonds/census.py` (`run_family`,
  `families_one_def`).
- Results: `artifacts/PROVED-RATE-20261113-001A/PROVED-RATE-20261113-001A-E001_cycle_mean/{rates_all.jsonl, summary.json}` and
  `experiments/PROVED-RATE-20261113-001A/PROVED-RATE-20261113-001A-E001_cycle_mean/merge_and_summarize.py` (the owner's merge).

## Points to check

1. **Fresh recomputation.** For a sample of complete families (say the 40 smallest by node count, plus 10 from each of: λ > 0,
   bounded_all, zero-mean without bounded_all, λ None), build the reachable graph of the DP yourself, trim it (reachable from a
   start node and co-reachable to a node with finite closing), compute the minimum cycle mean exactly (Karp per strongly connected
   component, or another exact method), and `bounded_all` as the spec defines it. Compare with `rates_all.jsonl` field by field.
2. **The lower bound.** Does L_ray(s) ≥ λ(s − |V|) follow on a complete graph, and with which |V| (all nodes or trimmed)? Does
   λ > 0 imply linear growth of L_ray, and is λ exactly liminf L_ray(s)/s?
3. **bounded_all.** Prove or refute that it implies L_ray bounded at every large depth. Is it also necessary? For the 46
   "flat" families that are zero-mean but not bounded_all (and a sample of the other zero-mean-only families), decide exactly
   whether L_ray(s) is bounded for every large s (for example by working per residue of the length modulo the gcd of zero-mean
   cycle lengths, or by another exact method), and report how many are.
4. **Capped graphs.** What does a λ computed on an incomplete (capped) graph prove, if anything?
5. **Run history.** Check that `rates_all.jsonl` has each of the 664 families once, that the three batches (508, 92, 64; the second
   ended in an out-of-memory stop) merge without loss or duplication, and that the summary's counts follow from the rows.
6. **Wording.** Is growth worded only as a property of ray bonds (an upper bound on the true least bond), and boundedness as
   transferring? Is anything presented as found that is settled by construction?

## Report format (`codex_report.md`)

A verdict line (Confirmed / Confirmed with fixes / Refuted), then one short section per point, then fixes each marked Block,
Narrowing or Not a block, then the files you wrote.
