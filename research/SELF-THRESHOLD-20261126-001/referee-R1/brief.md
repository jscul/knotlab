# Referee brief SELF-THRESHOLD-R1

For an independent referee, at the owner's standing request; keep it lean (under an hour of compute). You are
refereeing one closed study of this repository: `SELF-THRESHOLD-20261126-001`, and a recheck made beside it. Its
claims and files are in `research/SELF-THRESHOLD-20261126-001/referee_handoff.md`; read it, `decision.md`, `README.md`,
the advisor's answer, the register entry A285 in `docs/ASSUMPTIONS.md`, the previous study's referee report
(`research/HOLD-BACK-20261126-001/referee-R1/report.md`, which already tested one threshold of this kind on four pairs),
and `AGENTS.md` ("Canonical foundation", "Research discipline", "Guardrails").

**Order of work.** Claims 1 and 2 first: regrow, with your own code, a seeded sample of the 28 linked pairs and of the
census pairs under HALF, PLACES and the cap of three; check that HALF's allocations equal the cap's on hearing
histories and that the deciding birth for PLACES is the one stated. Then test the reading (claim 3) where you can, for
instance on a history with a birth owed five or more before a hearing. Then claim 4 on a sample. Say what you did not
reach.

## Your job

Write `research/SELF-THRESHOLD-20261126-001/referee-R1/report.md`: first line after the title, the verdict
(**Confirmed**, **Confirmed with fixes** or **Refuted**, and whether there is a **Block**); what holds, with your counts
and whether rebuilt or read; the fixes, each with its verdict (Block, Narrowing, Not a block), the exact sentence and
file, and the evidence; what was not run; how it was checked. Use code you write yourself in that folder.

## Rules

- **Where you write.** Only inside `research/SELF-THRESHOLD-20261126-001/referee-R1/`. Edit no other file. Do not
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
