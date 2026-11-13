# Independent recomputation and critique: BOND-DEPTH-20261112-001

You are an independent referee's assistant working in this repository. Recompute key numbers of one closed study with **your own
code** where you can (you may import the study's `census.py` only to reuse its family loader and `dlang`, and say where you did),
and critique its claims. Be terse and exact.

## Rules for this task

- Write **only** inside `research/BOND-DEPTH-20261112-001/referee-R1/codex/`. Do not edit, move or delete anything else. No git
  commands that change state (no add, commit, stash, checkout, reset). Do not run any publishing script.
- Use `/home/jscul/p-vs-np-contact-first/.venv/bin/python` (it has `pysat` and `numpy`). Keep every single computation under about
  10 minutes and 8 GB, and the whole task under about 60 minutes of wall time; pick small samples where needed and say so.
- Deliverable: `research/BOND-DEPTH-20261112-001/referee-R1/codex/codex_report.md`, plus your scripts and their JSON outputs in
  the same folder.

## The study (read these)

- `research/BOND-DEPTH-20261112-001/preregistration.md` and `bond_depth.md` (conclusions).
- Code: `experiments/BOND-DEPTH-20261112-001A/BOND-DEPTH-20261112-001A-E001_spine_bonds/census.py` (`run_family` is the method;
  its repeat detector is at the end of `run_family`; `summarize` classifies) and `helper_after_start.py` (12 helper workers added
  mid-run, using `run_family` unchanged, records merged by family index).
- Data: `artifacts/BOND-DEPTH-20261112-001A/BOND-DEPTH-20261112-001A-E001_spine_bonds/{runs_merged.jsonl, raw/, validation.json,
  summary.json}`.

Setting, briefly: NAE (not-all-equal) knots on three distinct Boolean distinctions; one-definition nested families; along one ray
of copies, L(s) is the least size of a bond (minimal constrained set of distinctions) containing a top port and an own distinction
of the copy s levels down, found by a DP over blocks whose states are pairs (F, G) of families of interface-state masks with a cost.

## Claims and points to check

1. **The repeat detector.** A family is "bounded" when the normalised cost vector over states repeats with gain 0, and "growing"
   when it repeats with gain > 0; else "undetermined". Result: bounded 204, growing 0, undetermined 447. Read the code exactly:
   what is the normaliser `mn`, how does it behave across levels, and can the detector ever report "growing"? Is the "bounded"
   verdict sound when it is given? Can it miss eventually periodic L(s) (bounded or linear), and why?
2. **The 240 "rising steadily" and 163 "flat" undetermined families.** On a sample (say 20 of each, smallest state counts first),
   decide L(s) further or exactly. If you can, give an exact method for the eventual rate of L(s) (L is a fixed-length least-cost
   path in a finite state graph with a closing step), or else extend s well past 30 and say what the extended data show. Are the
   rising ones genuinely linear, and are the flat ones bounded?
3. **Validation.** Reproduce a part of `validation.json` independently (exhaustive ray search on a few families at s = 1..3) and
   the chain result L = steps + 2.
4. **The mid-run helpers.** Check from `raw/` that duplicate family records (same idx from an original worker and a helper) are
   identical, that merging by idx lost or changed nothing, and that the 11 unfinished families are reported as such.
5. **Settled by construction or by the class.** Which headlines follow from the definitions (for example the ray restriction making
   "bounded" transfer to the true bond but "growing" only an upper bound; endpoint minimisation over the three top ports and any own
   distinction at depth s)?
6. **Honest reporting.** Is P1's failure (bounded below half) reported honestly, and are "growing exactly 0" and "rising steadily"
   worded correctly given points 1 and 2?

## Report format (`codex_report.md`)

A verdict line (Confirmed / Confirmed with fixes / Refuted), then one short section per numbered point: what you recomputed, the
result, and any discrepancy. End with a list of fixes, each marked Block, Narrowing or Not a block, and a list of the files you
wrote.
