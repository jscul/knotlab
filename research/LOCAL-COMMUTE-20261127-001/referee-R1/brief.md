# Referee brief LOCAL-COMMUTE-R1

For an independent referee. You are refereeing one closed study of this repository: `LOCAL-COMMUTE-20261127-001`. It
declares which distinctions' binary observables fail to commute, each pair decided at the end of the round in which the
later of its two distinctions is born and never revised (the birth rule: a pair may fail only if no knot holds both and one
member is already held twice then), and gives each implied birth the sign forced by the cost of reordering its checks. On
all 7,075 census starts grown up to four rounds by ordinary parity growth, it claims: every grown structure keeps a state
under the birth rule; every closure is a single implied birth that closes the whole structure; whole choices (read off
the finished structure, the earlier no-whole-state study's R3) attain an odd close exactly at the 1,187 closures that are
not outerplanar; birth choices attain it at 1,177 of them, losing it at 10 round-2 closures on two-place closing knots; the
natural birth rule loses its state on 4,941 of 5,086 growing starts; choosing round by round never reaches a round without
a consistent choice; and the sign is a free half-and-half choice at every closure where odd is attainable.

**Your main task is to break these claims**: rebuild the growth bookkeeping, the decidable pairs, the commuting conditions
and the interleaving cost with your own code; check the arguments A1–A6 of the README (A6 is the reviewer's lemma, argued
by hand and not proved in the record); look for a closure where the birth rule's restriction is mis-stated (a pair
forbidden that should be allowed, or the reverse); and check whether the headline ("the choice, not growth, selects the
sign") says more than the counts.

## Your job

1. **Read the hand-off.** `research/LOCAL-COMMUTE-20261127-001/decision.md` states each claim; the design, arguments,
   frozen predictions, review and results are in `README.md`; the code is `local_commute.py` and the post hoc
   `posthoc_losses.py`; the outputs are `summary.json`, `gates.json`, `results.jsonl`, `past.jsonl` and
   `posthoc_losses.json`. Read what they link: `research/NO-WHOLE-STATE-20261126-001/rule_census.py` (`analyse`, the whole
   choices) and README part E; `research/EVENTUAL-R-20261126-001/README.md` part B (rule R, pairs settling); the engine
   `research/FORBID-EDITS-20261126-001/forbid.py` and
   `experiments/FORBIDDING-JOIN-20261120-001B/FORBIDDING-JOIN-20261120-001B-E001_free_readings/rival_growth.py`. The
   advisor was unavailable; an independent reviewer checked the design by hand before the freeze. Read `AGENTS.md`
   ("Canonical foundation", "Research discipline", "Guardrails") and the glossary at the end of
   `publication/knotlab/INTUITIONS.md` first.
2. **Recount.** Check every listed claim with code you write yourself in this folder. Do not import `local_commute.py` or
   `posthoc_losses.py`; you may call the archived engine through `forbid.grown` and `forbid.starts`. In particular:
   - the decidable pairs (same-round pairs both loose at birth are forbidden; check the held-twice condition directly);
   - A1 on every structure, and A3 at every closure (one implied birth, closing the whole);
   - the whole choices against outerplanarity at all 1,819 closures, and the birth choices at all of them, by your own
     GF(2) elimination;
   - the 10 lost closures and the post hoc description (two-place closing knots, the forbidden pairs born at round 0);
   - the natural birth rule's first round without a state, on all starts;
   - the round-by-round random rule: no dead end, and the share of odd closes where odd is attainable;
   - A6 on the 26 closures it covers: construct its witness and check it, rather than only the rank test.
3. **Press.** Take the points above and in the hand-off, then look for what neither lists:
   - a prediction judged kindly, or a threshold or reading changed after results were seen (compare the freeze commit
     `89433903f1` with the closing one);
   - a claim stated beyond the census, the four-round cap or the 40-knot cut (25 starts not run);
   - "a state is kept on every grown structure": does it rest only on the classical choice, and is that said;
   - "half the choices close odd": is it uniform over the birth choices or over the round-by-round process, and does the
     latter sample the former uniformly;
   - a control that could not have failed;
   - a headline, summary, notebook entry (`docs/KNOT_INTUITION.md`), goals row or assumption entry (A314) that says more
     than the tables do;
   - earlier work in the program that already has the result: rerun `python3 -B scripts/track.py objects-gate
     research/LOCAL-COMMUTE-20261127-001/README.md`, one objects search of your own in other words, and a full-text search
     of the records.
4. **Report.** Write `research/LOCAL-COMMUTE-20261127-001/referee-R1/report.md`:
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

- **Where you write.** Only inside `research/LOCAL-COMMUTE-20261127-001/referee-R1/`. Edit no other file. Do not commit,
  stage, stash, reset, switch branches or push. Other sessions are working in this checkout. Do not stop any process
  you did not start, and stop your own only by process number.
- **Compute.** The machine is shared. Use at most 4 worker processes and 8 GB in all, and set `OMP_NUM_THREADS=1` for
  every numpy process. The study's own run took under two minutes. Use the repository's `.venv/bin/python`.
- **Independence.** Another agent drafted and closed the study. A refutation is as welcome as a confirmation. Do not
  soften a finding, and do not invent one.
- **Words.** Use the glossary's words: distinction, knot, shared distinction, loose distinction, sample, weighting.
  Say "knot". Do not name the program's own objects by words from a space of two or three dimensions. Never call
  anything typical, rare or likely without naming its weighting. Do not use a study label or a start number without
  saying what it is.
- **No names of AI models, agents or tool versions** in any file you write.
- **Publication hold.** If anything you find would amount to an efficient general method for SAT, factoring or
  breaking cryptography, write nothing about it in the repository and say so in your final message only.
- **No claims** about physics, minds, living things, time or space from this work.
