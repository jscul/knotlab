# Independent recomputation and critique: FREE-TARGET-20261114-001 (the proof is the main object)

You are an independent referee's assistant. The study's code was written by a coding agent from a frozen spec, so your
recomputation must be **fresh code written from the spec and the mathematics**. Work at full care: the headline is a proved lower
bound that the owner will rely on.

## Rules for this task

- **Do not open or import any `.py` file under** `experiments/FREE-TARGET-20261114-001A/FREE-TARGET-20261114-001A-E001_free_target/codex/`.
  You may read its JSON/JSONL data (`gates.json`, `gate_relations.jsonl`, `population.json`, `full/`, `smoke/`), and
  `research/FREE-TARGET-20261114-001/{free_target.md, preregistration.md, codex_spec.md, advisor_review_answer.md}`, the EVERY-RAY
  sample rows `experiments/EVERY-RAY-20261113-001A/EVERY-RAY-20261113-001A-E001_min_over_paths/codex/sample/*.jsonl` (data only), the
  census records `artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/families.jsonl.gz` and
  `.../codex/draws.jsonl.gz` under `experiments/REACH-CENSUS-20261113-001A/`, and the input modules the spec names (dlang,
  LIMIT-STATE's census).
- Write **only** inside `research/FREE-TARGET-20261114-001/referee-R1/codex/`. No git commands that change state; no publishing.
- At most 3 processes and 10 GB; each command under about 15 minutes; the whole task under about 75 minutes. Use
  `/home/jscul/p-vs-np-contact-first/.venv/bin/python -B`. No network.
- Deliverable: `research/FREE-TARGET-20261114-001/referee-R1/codex/codex_report.md`, plus scripts and JSON outputs there.

## Points to check (in order of value)

1. **Try to break the lower bound directly.** For at least 8 of the 43 certified families (smallest blocks first, and at least two
   with r ≥ 4), compute **exactly, with no relation or semigroup code**, the least bond containing a port of main and an own
   distinction of **any** copy at depth s, with members **anywhere** (side copies included), for s = 1..5 or as far as cheap: build
   the tree of all copies to depth s + h (h = 1, 2), replace every SELF call below that by its limit relation G, and search sets by
   size with direct satisfiability (constrained, and every one-forgotten subset unconstrained). Report the values against
   2 + ⌊s/r⌋ (they must be at least that) and against the recorded L_path (they must be at most that), and how they change with h.
2. **The gap argument, as mathematics.** Check its premises for a free target with members anywhere: (a) copies share distinctions
   only through call arguments, and G is the exact limit projection; (b) each R_i projects out the copy's own distinctions and every
   other call's subtree, including calls to other self-holding definitions in several-definition families; (c) the 8×8 port
   relation, composed, is exactly the projection a stretch needs, so that no finer relation tracking shared identity is needed. Say
   precisely what the argument covers when main ≠ S, or when targets could be copies of other self-holding definitions, and how many
   of the 43 have several definitions.
3. **Rectangularity, fresh.** Re-derive R_i for each SELF call of the 43 and of the 23 unresolved yourself, and decide the semigroup
   exactly (the least r with every length-r product rectangular, or a recurring non-rectangular product). Compare with the records.
4. **Claim (iii), added at the close.** One-definition families with one SELF call and no other self-holding call: show that
   L_any = L_ray (members anywhere, any target copy), and recount from the census records the 5,190 distinct families and 5,633 draws
   of such growers, and the stated 2.5% of all nested weight and 42% of the first-ray growth weight. Is the claim labelled as added
   at the close? Is it a restatement of something the program already had (single chains of copies as rulers)?
5. **The unresolved and the wording.** The bounded search tests one eventually periodic path only, so per-depth boundedness along
   paths that change with the depth is untested (EVERY-RAY's referee found such a family). Check that the 21 unresolved are not
   described as anything stronger, that "counts depth" is worded as a proved linear lower bound with existence from L_path, that
   "about 3% of all weight" (if present) does not combine a census count with a sample share, and that nothing is called typical or
   rare beyond the sample.

## Report format (`codex_report.md`)

A verdict line (Confirmed / Confirmed with fixes / Refuted), one short section per point, fixes each marked Block, Narrowing or Not a
block, and the files you wrote.
