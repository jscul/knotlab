# Referee brief TRANSFER-TABLES-20261126-001-R1

For an independent referee, at the owner's standing request; keep it lean (under an hour of compute). You are refereeing
`TRANSFER-TABLES-20261126-001` (tables under the ring-to-end study's transfer law for readers whom no listed law joins),
closed 26 November. Read its decision, README, preregistration, `tables.py` and `whole_knots.py`, the factoring study's
referee R2 (section 2), the transfer law (`experiments/RING-TO-END-20261119-001/RING-TO-END-20261119-001-E001_transfer/
transfer.py`), and `AGENTS.md`.

**Order of work.** Rebuild independently: the 13 reached states and 30 splits; that value reads never exceed CHSH 2
and never signal; on the coherent version the negativities, the largest CHSH with any reads (1 + √2 and 2.2159) and
with the model's reads (exactly 2: try hard to beat it with signed Pauli products on the readers' distinctions); the
controls; and that every split is joined by a knot in the whole of the reached states. Try to break "no table exceeds
the classical limit with the model's reads" and "nothing signals", and say whether the excess with rotated reads is a
table above the classical limit that the model makes, or one supplied. Say what you did not reach.

## Your job

Write `research/TRANSFER-TABLES-20261126-001/referee-R1/report.md`: first line after the title, the verdict (**Confirmed**, **Confirmed with
fixes** or **Refuted**, and whether there is a **Block**); what holds, with your counts and whether rebuilt or read; the
fixes, each with its verdict (Block, Narrowing, Not a block), the exact sentence and file, and the evidence; what was not
run; how it was checked. Use code you write yourself in that folder.

## Rules

- **Where you write.** Only inside `research/TRANSFER-TABLES-20261126-001/referee-R1/`. Edit no other file. Do not
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
