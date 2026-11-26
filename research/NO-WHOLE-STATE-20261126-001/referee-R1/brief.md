# Referee brief NO-WHOLE-STATE-20261126-001-R1

For an independent referee, at the owner's standing request; keep it lean (under an hour of compute; cut a longer check
to a seeded sample and report the rest as not run). You are refereeing the study `NO-WHOLE-STATE-20261126-001`
(patterns read part by part, and values that need not commute), closed 26 November. Read its decision, README and
preregistration, register entries A126, A294 and A295 in `docs/ASSUMPTIONS.md`, and `AGENTS.md` ("Canonical
foundation", "Research discipline", "Guardrails"). Its prior work, `FOUR-READINGS-20261120-001A` (refereed: confirmed
with fixes) and `ERASURE-AND-CLOSING-SIGNS-20261121-001B` (its own referee is running), may be read but is not yours.

**Order of work.** Rebuild independently, with code you write:
1. The fixture (part C): ordinary parity growth from the ring of three knots (0,1,2), (1,3,4), (3,0,5) closes in one
   round onto (2,4,5) with no fresh distinction; with the closing sign odd, all 64 probabilities of the three readers'
   part tables equal the three-reader target and the overlaps agree; the control.
2. The reordering identity (part D): the sum of the knots' signs equals the number of non-commuting interleaved pairs,
   mod 2, at the 115 stored operator witnesses of the prior study; at the four-knot closure rule R (two values commute
   exactly when some knot holds both) makes the knots commute and forces the closing value odd.
3. The census (part E): R1, R2, R3 over the 173 stored types, the table's counts under both weightings (one vote per
   type, one per labelled pattern), the claim that an odd sum is attainable exactly at non-outerplanar patterns, and the
   32-against-16 word count on two four-knot closures sharing one knot.
4. The arguments (parts F and G): that part counting alone reaches CHSH 4 on the two-reader pattern; that R changes at a
   birth (three values pairwise non-commuting under R joined by one knot have no parity); whether "R is not native"
   and "the bound needs a whole of another kind" are worded within their evidence.
5. The correction the study logs (the advisor's "entailed at the rest"), and whether any claim of novelty is made where
   the literature already has the result (Mermin 1990; Arkhipov 2012; Gottesman 1998; Popescu–Rohrlich 1994).
Say what you did not reach.

## Your job

Write `research/NO-WHOLE-STATE-20261126-001/referee-R1/report.md`: first line after the title, the verdict (**Confirmed**, **Confirmed with
fixes** or **Refuted**, and whether there is a **Block**); what holds, with your counts and whether rebuilt or read; the
fixes, each with its verdict (Block, Narrowing, Not a block), the exact sentence and file, and the evidence; what was not
run; how it was checked. Use code you write yourself in that folder.

## Rules

- **Where you write.** Only inside `research/NO-WHOLE-STATE-20261126-001/referee-R1/`. Edit no other file. Do not
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
