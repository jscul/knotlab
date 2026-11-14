# Counterexample execution notes

Scope: READ-RULE task 4, following the frozen preregistration and Codex specification. This module uses repository material only and starts no child processes. The coordinator owns scheduling and the final `counterexample.json` and `REPORT.md`.

`counterexample.variant_rows()` supplies both exact census-format keys. Variant a has three own distinctions `u,x,w`; variant b has those and the three own distinctions of the four-constraint positive inequality gadget. Both have one definition, `main = S = 0`, and the prescribed `SELF(a,u,x)`. The gadget calls are transcribed exactly from `gadget_control.gadget`, whose source has top-level computation and a write, so it is not imported.

The execution interface is `run_window(variant)` and `run_direct(variant,s)`. The former invokes unchanged CARRY `window.run_family(..., include_growth=True)`; the latter invokes unchanged CARRY `direct.run_case(...)`. `cases()` and `run(case_id,payload)` expose these independent cells to a shared-runner adapter. No runner, timeout loop, resume loop, search extension, or output writer is implemented here. `q3_from_results(records)` computes a three-valued prediction from observed results only.

## Ambiguities and limits identified before execution

- **Exact direct values above six:** CARRY `direct.py` fixes `MAX_SIZE = 6` and its public `run_case` has no parameter for changing that. How are the preregistered exact values 7, 8 and 9 at a's depths 4, 5 and 6 to be measured using this unchanged entry point? Pending an explicit amendment, run the supported search at every required depth but leave any exact value above six unresolved. A completed `> 6` exclusion is not an exact minimum or a growth result.
- **Repeated arguments:** variant a is outside the census input grammar, as specified. Run its exact raw family through the original entry points; if rejected, retain the failure and continue independent supported cells. Do not replace the prescribed family or alter a parser.

Direct results retain the original evidence qualification: all unfolded distinctions through absolute depth `s+2`, with usual-limit relations at the frontier; finite-reading upper bounds only. These experiments do not discharge proof obligations.

## Scheduled execution

The coordinator first scheduled both window/growth cells and direct depth 1 for each variant, then scheduled the remaining direct depths 2–6. Both invocations used one `.venv/bin/python -B` process, with no child processes. Raw results, timing, memory and source hashes are retained in the separately authorized `counterexample_probe.json` and `counterexample_full_raw.json`.

## Observed result

**Q3 fails in both prescribed variants.** Both original window computations completed with `U(0)=U(1)=U(2)=2`, preperiod 2 and period 1; hence their repeating value is 2. Both received the original `bounded` verdict. Every original growth test (`G`, `G2`, `G2_live`) returned `certified=false`.

| Variant | Direct L(1) | L(2) | L(3) | L(4) | L(5) | L(6) |
| --- | --- | --- | --- | --- | --- | --- |
| a, repeated argument | 2 | 2 | 2 | 2 | 2 | 2 |
| b, positive gadget | 2 | 2 | 2 | 2 | 2 | 2 |

All twelve direct rows have `status=exact_minimum`, and all twelve independently checked CNF projections have `is_bond=true`, `every_deletion_full=true`, and allowed pair states `[1,2]`. Each witness contains top port `a` and own distinction `u` of the target copy at the requested depth (`raw_owner.own_index=0`). Thus the reported pair is opposite in every allowed state. The prescribed target set includes `u`; omitting it to seek the advisor's proposed larger bond would change the task.

The initial four-cell probe took 0.082905 seconds, peak process RSS 42,920 KiB. The ten remaining direct cells took 0.073271 seconds, peak process RSS 41,760 KiB in that second process. The first direct measurement arrived 0.079206 seconds after the initial probe began; dominant work before it was necessary support (input construction and original-module loading). The observed failure closes Q3's finite test; no larger search or shared-runner job is needed for these cells. The size-six capacity limit did not leave any observed direct minimum unresolved, because every observed minimum was two.

The repeated-argument family was accepted by both original entry points. No prescribed cell was skipped, capped, timed out or replaced. These observations contradict the advisor's hand-derived count and the preregistered Q3 expectation; they do not by themselves establish or refute a different converse statement or discharge a proof obligation. The coordinator owns reporting the discrepancy in `REPORT.md` and to the owner.
