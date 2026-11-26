# Referee brief SIDE-SIGN-R1

You are refereeing one study of this repository, `SIDE-SIGN-20261126-001`, at the owner's standing request. Keep it
lean: well under two hours of compute in all.

## The question

Take meeting patterns made by ordinary growth (the canonical engine: `research/FORBID-EDITS-20261126-001/forbid.py`,
arm 'ordinary', and the starts in its `starts.json`) that have a renaming of order two moving a knot (a swap). With no
added rule:

1. Do the allowed states sort into those the swap leaves unchanged and those it turns into their complement, and is that
   sort a two-valued label the pattern carries?
2. Are there patterns where going round a chain of knots returns with the swap's two sides exchanged, so that no
   renaming removes it, and what of it can a state read?
3. Can a sign built from a swap weight whole configurations so that two completions of one reading cancel, giving two
   readers (each choosing which of two distinctions to read) a table above CHSH 2 that passes these gates: G0 every
   normalizer nonzero, G1 every entry nonnegative, G2 equal normalizers across setting pairs, G3 no signalling, G4 CHSH
   above 2? Which parts of any such sign and reading does the model make, and which are supplied?
4. Under parity, where the allowed states fall into classes joined by the shortest changes through each distinction
   (`research/READS-HOLDERS-SOURCES-20261120-001A/motion.md`), does a swap keep the classes, exchange them, or give them a
   relative sign?

## Steps

1. **Answer it yourself first**, with your own code in your folder (never import the study's modules; you may import
   the growth engine through `forbid.py` as the study did, or build your own and compare). Rebuild on a stated sample of
   the census (a seed, and at least the starts 3097 and those at indices 0 to 99), on the rings of four, five and six knots
   with two loose distinctions each (rounds 0 and 1), and on any other pattern you judge a better test, including one
   blow-up start. State every weighting and reading you use as a choice.
2. **Then read the study**: `research/SIDE-SIGN-20261126-001/README.md` (design, arguments A1 to A5, frozen predictions,
   and the results section added after the run), `decision.md`, the code (`sides.py`, `named.py`, `controls.py`,
   `tally.py`), its outputs (`census_tally.md`, `named_*.jsonl`, `census_hits.json`), register entry A292 in
   `docs/ASSUMPTIONS.md`, and the advisor's answer. Compare with your answers: every count you rebuilt, every argument
   (check each step), every prediction's verdict, and the reading of what is supplied.
3. **Press hardest on** whether any table reported above 2 is right and what it rests on, whether a native sign was
   missed, and whether the claims about what the model makes and what is supplied hold.

## Stop

Stop when you can give a verdict. Write `research/SIDE-SIGN-20261126-001/referee-R1/report.md`: the first line after the
title is the verdict (**Confirmed**, **Confirmed with fixes** or **Refuted**, and whether there is a **Block**); then what
holds, with your counts and whether rebuilt or read; the fixes, each with its verdict (Block, Narrowing, Not a block), the
exact sentence and file, and the evidence; what was not run; how it was checked.

## Rules

- **Where you write.** Only inside `research/SIDE-SIGN-20261126-001/referee-R1/`. Edit no other file. Do not commit,
  stage, stash, reset, switch branches or push. Other sessions are working in this checkout: do not stop any process
  you did not start, and stop your own only by process number.
- **Compute.** The machine is shared. Use at most 8 worker processes and 16 GB in all. Time a small part at the exact
  configuration before any run. A run finishes in about an hour: cut a longer one to a stated prefix or to a sample with
  a stated seed, and report what was not run as "not run". Use the repository's `.venv/bin/python`.
- **Independence.** The study was drafted by another agent. A refutation is as welcome as a confirmation; do not soften
  a finding, and do not invent one.
- **Words.** Use the glossary's words (`publication/knotlab/INTUITIONS.md`, Glossary): distinction, knot, shared
  distinction, loose distinction, sample, weighting. Say "knot". Do not name the program's own objects by words from a
  space of two or three dimensions. Never call anything typical, rare or likely without naming its weighting. Do not use a
  study label or a start number without saying what it is.
- **No names of AI models, agents or tool versions** in any file you write.
- **Publication hold.** If anything you find would amount to an efficient general method for SAT, factoring or breaking
  cryptography, write nothing about it in the repository and say so in your final message only.
