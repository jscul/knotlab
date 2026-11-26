# Referee brief SHORT-AGAIN-R1

For an independent referee, at the owner's standing request. You are refereeing one closed study of this repository:
`SHORT-AGAIN-20261126-001`, "a ration under which a knot is short again where two patterns join: does one then hear
the other from afar". It was closed at commit `b72f027d6e`; all its results are computed and marked "referee
pending". Its register entries are A277, A278 and A224 in `docs/ASSUMPTIONS.md`, and its correction is the newest
entry of `docs/CORRECTIONS.md` about it ("Heard from afar: without the change ...").

**Order of work.** The switch under the cap of three first (JAM.md, "The one receiver that hears under the cap"),
since it is the result most is built on next; then the weaker rule about waiting own knots and its denominator;
then the correction (that the unchanged two-source growth makes nothing after round 1); then the ring line; then
the rest. If time is short, a complete check of the switch and the rule is worth more than a thin pass over
everything; say plainly what you did not reach.

**Points beyond the hand-off's.**
- Write your own growth from the record's definitions (the ordinary count, the cap, the one-fewer rations made and
  recorded, the treatments of a short knot, the meeting and the shared distinction as joins, the link knots, the
  stub, a change of either sign) and regrow a sample of cases with a stated seed; compare every round's counts with
  the recorded runs (`*.jsonl.gz`). The engine the study used is `experiments/WHAT-A-BIRTH-CARRIES-20261125-001B/
  WHAT-A-BIRTH-CARRIES-20261125-001B-E001_link_through_a_made_knot/eng.py` with
  `research/TWO-PATTERNS-20261126-001/bench/bench.py`; where you fall back on it, say so and say what you checked it
  against.
- The switch: is "leaves the first way at round 2d + 1" a property of the receiver reading the far end, or of a
  count that any change near the line would move? Check that the 28 "never" senders are read to round 16, that the
  split by the sender's site (two loose distinctions) is exact, and the stated route (the receiver's partners owed
  four and given three). Search the program's earlier records for a receiver that switches (`python3 -B
  scripts/track.py objects` with the words "switch", "cap", "demand four", "cone").
- The weaker rule: in how many hearing rounds could it have failed, that is, rounds in which the unchanged growth
  has no waiting own knot? If almost every round of every receiver has one, say that the rule is near-empty.
- The correction: confirm from `far.jsonl.gz` that the unchanged growths make nothing after round 1, and judge
  whether the note's notice now says what the record shows, no more.
- "What passes is one number" (RING_LINE.md): check the restart rounds and "the same numbers after" on all 21 starts.
- Scaffolds: the meeting, the link knots, the change, the stub, the strict reading of own knots (A277); the made
  rations (A278) and the record's; the cap (A224). For each result, say whether it survives a different choice of
  each scaffold it depends on, so whether it is about the model or about the scaffold. If a cheap swap is feasible
  (another join, another site, a cap of five), run it on a small sample and report it.

## Your job

1. **Read the hand-off.** `research/SHORT-AGAIN-20261126-001/referee_handoff.md` lists each claim, where its code and
   data are, and what to press. Read what it links: `decision.md`, `README.md`, `RING_LINE.md`, `JAM.md`, `AGAIN.md`,
   `report_1.md`, `owner_request.md`, the advisor's two answers. Read `AGENTS.md` ("Canonical foundation", "Research
   discipline", "Guardrails") and the glossary at the end of `publication/knotlab/INTUITIONS.md` first.
2. **Recount.** Check every listed claim against the raw outputs with code you write yourself in this folder. Do not
   import the author's reading or analysis modules.
3. **Press.** Take the points above and the hand-off's, then look for what they do not list:
   - a prediction judged kindly, or a threshold or reading changed after results were seen (the jam study's rule was
     stated from the far table and six trial pairs; its weaker form was added after the full pass showed the strict
     one failing, and AGAIN.md had no written expectation);
   - a count on a sample, a prefix or the author's own picked cases stated as general;
   - a "none", "every" or "exactly" claim that almost nothing could have contradicted (count the cases that could have);
   - a control that could not have failed;
   - a difference that a simpler reading explains (a count, the first round, a numbering, a name);
   - a headline, summary, goals row or register line that says more than the tables do;
   - earlier work in the program that already has the result.
4. **Report.** Write `research/SHORT-AGAIN-20261126-001/referee-R1/report.md`:
   - first line after the title, the verdict: **Confirmed**, **Confirmed with fixes** or **Refuted**, and whether
     there is a **Block**;
   - **What holds**, claim by claim, each with the count you obtained and whether you rebuilt it or only read it;
   - **The fixes**, each with its verdict (**Block**: what the study stood on is false; **Narrowing**: true only in a
     smaller scope or for another reason; **Not a block**: wording or credit), the exact sentence and file to change,
     and the evidence;
   - **Scaffolds**: per result, model or scaffold, and what you swapped;
   - **What was not run**, never as a negative;
   - **How it was checked**: your files, and the commands that rerun them.
   Keep the report to what a reader needs to act on it. Put tables of counts in JSON files beside it.

## Rules

- **Where you write.** Only inside `research/SHORT-AGAIN-20261126-001/referee-R1/`. Edit no other file. Do not
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
