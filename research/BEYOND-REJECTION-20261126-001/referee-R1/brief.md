# Referee brief BEYOND-REJECTION-R1

For an independent referee, at the owner's standing request; keep it lean (well under an hour of compute). You are
refereeing one closed study of this repository: `BEYOND-REJECTION-20261126-001`. Its claims and files are in
`research/BEYOND-REJECTION-20261126-001/referee_handoff.md`; read it, `decision.md`, `README.md`, the advisor's answer,
the register entry A290 in `docs/ASSUMPTIONS.md`, the earlier construction it models
(`experiments/WHOLE-STAGE-SETTINGS-20261120-001C/`, its `result.md`, and the proof in
`proofs/WHOLE-STAGE-SETTINGS-20261120-001A/`), the records cited in the scoping table, and `AGENTS.md` ("Canonical
foundation", "Research discipline", "Guardrails").

**Order of work.** Part A first: check that the record-level model matches the earlier construction (the terminal
correspondences, the funding rule, what each reader's complete record holds), rebuild the programs with your own code,
and check the policy equivalence. Then part B: check each row of the table against its cited record, and look for a
native sign that could weight configurations that the table missed. Say what you did not reach. Citations given from
memory (Abramsky and Brandenburger 2011): check what you can.

## Your job

Write `research/BEYOND-REJECTION-20261126-001/referee-R1/report.md`: first line after the title, the verdict
(**Confirmed**, **Confirmed with fixes** or **Refuted**, and whether there is a **Block**); what holds, with your counts
and whether rebuilt or read; the fixes, each with its verdict (Block, Narrowing, Not a block), the exact sentence and
file, and the evidence; what was not run; how it was checked. Use code you write yourself in that folder.

## Rules

- **Where you write.** Only inside `research/BEYOND-REJECTION-20261126-001/referee-R1/`. Edit no other file. Do not
  commit, stage, stash, reset, switch branches or push. Other sessions are working in this checkout: do not stop
  any process you did not start, and stop your own only by process number.
- **Compute.** The machine is shared. Use at most 8 worker processes and 16 GB in all. Time a small part at the
  exact configuration before any run. A run finishes in about an hour, two at the outside: cut a longer one to a
  stated prefix or to a sample with a stated seed, and report what was not run as "not run". Use the repository's
  `.venv/bin/python`.
- **Independence.** The study was drafted and closed by another agent. A refutation is as welcome as a
  confirmation; do not soften a finding, and do not invent one.
- **Words.** Use the glossary's words: distinction, knot, shared distinction, loose distinction, sample, weighting.
  Say "knot". Do not name the program's own objects by words from a space of two or three dimensions. Never call
  anything typical, rare or likely without naming its weighting. Do not use a study label or a start number without
  saying what it is.
- **No names of AI models, agents or tool versions** in any file you write.
- **Publication hold.** If anything you find would amount to an efficient general method for SAT, factoring or
  breaking cryptography, write nothing about it in the repository and say so in your final message only.
- **No claims** about physics, minds, living things, time or space from this work.

When the report is written, end with a final message of at most fifteen lines: the verdict, each fix with its
verdict in one line, and what was not run.
