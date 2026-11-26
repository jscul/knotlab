# Referee brief EVENTUAL-R-20261126-001-R1

For an independent referee, at the owner's standing request; keep it lean (under an hour of compute; cut a longer check
to a seeded sample and report the rest as not run). You are refereeing the study `EVENTUAL-R-20261126-001` (rule R,
two values commute exactly when some knot of the whole structure holds both, read off the whole fixed structure),
closed 26 November. Read its decision, README and preregistration, register entries A295 and A297 in
`docs/ASSUMPTIONS.md`, the previous study `NO-WHOLE-STATE-20261126-001` (refereed), and `AGENTS.md` ("Canonical
foundation", "Research discipline", "Guardrails").

**Order of work.** Rebuild independently, with code you write:
1. Part A: on the 21 census types where R makes the knots commute, every subset of every maximal read set: the closed
   part rule against the state the signed knots fix (it should differ only at the cut-knot type), and GF(2)-signed
   products of knots (contradictions at every odd-forced type).
2. Part B: settling (pairs settle when either distinction is held twice), the flip formula (a knot pair's commutation
   changes between rounds only for two knots born in the earlier round, by the parity of their common children), and the
   count of 290 of 300 sampled starts on which some two knots' operators fail to commute for good. Check the engine
   lines cited (`rival_growth.py` 71 and 81) and whether a stalled structure is rightly treated as the whole.
3. Part C: the three-reader value 4 on the four-knot closure; whether "CHSH at most 2 for the counting state with values
   that are products of distinctions' values" is true (it was argued, not computed beyond single distinctions); whether
   "the tables are contextuality, not separated readers" is right.
4. Whether "what R contradicts is the knots' own laws" and "consistent with earlier readings" are worded within their
   evidence, and whether the frozen prediction that failed (2) is reported as failed.
Say what you did not reach.

## Your job

Write `research/EVENTUAL-R-20261126-001/referee-R1/report.md`: first line after the title, the verdict (**Confirmed**, **Confirmed with
fixes** or **Refuted**, and whether there is a **Block**); what holds, with your counts and whether rebuilt or read; the
fixes, each with its verdict (Block, Narrowing, Not a block), the exact sentence and file, and the evidence; what was not
run; how it was checked. Use code you write yourself in that folder.

## Rules

- **Where you write.** Only inside `research/EVENTUAL-R-20261126-001/referee-R1/`. Edit no other file. Do not
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
