# Referee brief BUILT-BINDING-R1

For an independent referee. You are refereeing one closed study of this repository: `BUILT-BINDING-20261126-001`. It
reproduces the bindings that the referee of `BINDING-20261126-001` found (three or more facts that no single knot reads,
each carried on its own, obeying one parity rule after ordinary parity growth), and reports them in four parts:
(a) such bindings exist on hand-built ring starts (and on one sampled ten-knot start under one reading of a small
change); (b) their relation is the start's own sum of knot laws, already true of the facts' start representatives;
(c) **what growth contributes**: before growth the representatives were functions of the start's values that no single
knot reads but, depending on the reading, not facts kept by every small change; after growth they are such facts, each
held only by a whole carrier of new distinctions, so growth turns a first-layer relation into a relation among
whole-held facts; (d) under the two forbidding cuts one birth's law makes a relation the start lacked. It adds an
argument (premises checked on every birth record, a spanning set checked by rank) that ordinary growth never makes a
relation among class facts.

**Your main task is to break (c)**, and with it the argument. Try, for instance:
- that the "before growth" status is misread: the representatives were already class facts, or were read at single
  knots, under some reading the study uses, or a different representative changes the verdict;
- that after growth the facts are read by a single knot, or are not kept by some small change, under either reading;
- that the carriers are not "held only by whole carriers" in any sense that matters (for example that the lineage rule
  picks carriers the growth does not distinguish), or that the relation among the new carriers is not the start's;
- that the argument fails: a broken premise (no birth takes two distinctions of one parent; any two live knots with a
  common neighbour share a birth next round; a birth with no fresh distinction is alone in its structure and its
  parents hold one loose distinction each) at larger starts or later rounds, a stage where the pairs and loops of four
  do not span the changes that keep the start's values, or a gap in the proof sketch itself;
- a relation made by ordinary growth among class facts anywhere, on built or sampled starts;
- for (d), that the cut's relation is something other than one birth's law, or that it is not new.

## Your job

1. **Read the hand-off.** `research/BUILT-BINDING-20261126-001/referee_handoff.md` lists each claim, its evidence class,
   where its code and data are, and the points the author asks a referee to press. Read what it links, including the
   advisor's answer (`advisor/answer.md`) and the earlier referee's report
   (`research/BINDING-20261126-001/referee-R1/report.md`). Read `AGENTS.md` ("Canonical foundation", "Research
   discipline", "Guardrails") and the glossary at the end of `publication/knotlab/INTUITIONS.md` first.
2. **Recount.** Check every listed claim against the raw outputs with code you write yourself in this folder. Do not
   import the author's reading or analysis modules. For the growth itself, write your own from the frozen
   definitions where that is feasible and compare it with recorded runs on a sample; where you reuse a shared growth
   engine, say so in the report and say what you checked it against.
3. **Press.** Take the points above and in the hand-off, then look for what neither lists:
   - a prediction judged kindly, or a threshold or reading changed after results were seen;
   - a count on a sample, a prefix or the author's own picked cases stated as general;
   - a "none", "every" or "is a function of" claim that almost nothing could have contradicted (count the cases that
     could have);
   - a control that could not have failed;
   - a difference that a simpler reading explains;
   - a headline, summary, guide passage or goals row that says more than the tables do;
   - earlier work in the program that already has the result: search with `python3 -B scripts/track.py objects`.
4. **Report.** Write `research/BUILT-BINDING-20261126-001/referee-R1/report.md`:
   - first line after the title, the verdict: **Confirmed**, **Confirmed with fixes** or **Refuted**, and whether
     there is a **Block**;
   - **What holds**, claim by claim, each with the count you obtained;
   - **The fixes**, each with its verdict (**Block**: what the study stood on is false; **Narrowing**: true only in a
     smaller scope or for another reason; **Not a block**: wording or credit), the exact sentence and file to change,
     and the evidence;
   - **What was not run**, never as a negative;
   - **How it was checked**: your files, and the commands that rerun them.
   Keep the report to what a reader needs to act on it. Put tables of counts in JSON files beside it.

## Rules

- **Where you write.** Only inside `research/BUILT-BINDING-20261126-001/referee-R1/`. Edit no other file. Do not commit,
  stage, stash, reset, switch branches or push. Other sessions are working in this checkout: do not stop any process
  you did not start, and stop your own only by process number.
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
