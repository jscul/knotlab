# Independent recomputation and critique: WEIGHTS-20261112-001

You are an independent referee's assistant. Your recomputation must be **fresh code** from the notes and the mathematics, or the
earlier referees' code named below.

## Rules for this task

- **Do not open or import:**
  - `research/WEIGHTS-20261112-001/{completion.py, summary.py}`;
  - any `.py` under `experiments/WEIGHTS-20261112-001A/`, `experiments/SHIFT-COUNT-20261112-001A/` or
    `experiments/COMMON-FOLD-20261112-001A/`.
- **You may read:**
  - the data `artifacts/WEIGHTS-20261112-001A/WEIGHTS-20261112-001A-E001_two_shifts/{census.jsonl, calibration.jsonl,
    resume_census/results.jsonl}`. Each base record holds its kinds, diameters, class, stratum and the main arm's certified and
    forced directions.
  - `research/WEIGHTS-20261112-001/{two_shifts.md, preregistration.md, paused.md, completion.json, summary.json,
    partial_summary.json}`;
  - the definitions in `research/SHIFT-COUNT-20261112-001/{preregistration.md, shift_count.md}`,
    `research/FAR-BOUND-20261112-001/far_bound.md` and `research/COMMON-FOLD-20261112-001/common_fold.md`.
- **Reuse the earlier referee code.** It is in `research/SHIFT-COUNT-20261112-001/referee-R1/` (`ref_shiftcount.py`: forcing and
  certificates, tori and two-way eventually periodic states; `ref_137.py`: a completion of the same kind) and
  `research/COMMON-FOLD-20261112-001/referee-R1/`.
- Write **only** inside `research/WEIGHTS-20261112-001/referee-R1/codex/`. No git commands that change state; no publishing.
- **Keep the job modest.** Another long run is using most of the machine's cores: at most 2 processes and 6 GB; each command under
  about 15 minutes; the whole task under about 60 minutes. Use `/home/jscul/p-vs-np-contact-first/.venv/bin/python -B`. No network.
- Deliverable: `research/WEIGHTS-20261112-001/referee-R1/codex/codex_report.md`, plus scripts and JSON outputs there.

## Points to check (in order of value)

### 1. The four completion certificates

The certificates are in `completion.json`: β0/sample 38/r4, β1/18/r4, β1/28/r4 and β1/41/r3. Each claims that a pattern A with
values p forces its translate along k·d, certified by four-sided eventually periodic states: period P along, Q across, and two copies
of each tail block constrained equal.
- **Certify independently.** Check that the pattern is forced along k·d on the base (the base's kinds from the records), and that
  the certificate is sound.
- **Search for one yourself.** If you cannot reproduce a certificate, search for one in the same family yourself (as `ref_137.py`
  did).
- **Say what "certified" means here.** State the soundness argument for this certificate shape in one paragraph.

### 2. Spot-check the main arm's two-certified bases

Take about 10 bases across the three weightings and both strata, including some from the resumed run and some from before the
pause. For each:
- recompute the base's travelling class;
- independently certify both recorded directions.

Report any disagreement.

### 3. A light recount, from the raw JSONL with your own code

- **The prefix rule.** Recount the stopping indices (101, 55, 89) and the W1 counts: 39 of 40, 35 of 40 and 38 of 41 after
  completion, with Wilson intervals. Recount the old box at β = 2 (46 of 54) and the travelling rates (13.5%, 27%, 34%, 38%).
- **The alternative reading.** Recount the same with **all** completed samples in place of the prefix.
- **The dropped samples.** Report which samples were dropped before the pause, and their outcomes once rerun.

### 4. "Big knots travel less"

From the base records, tabulate the travelling rate by the base's largest kind diameter and by its mean diameter, within each β and
stratum, and by r. Say whether the rate falls with knot size inside a weighting, or whether the across-β comparison is confounded
by r or by the stratum's composition. Give Wilson intervals where counts are small.

### 5. Wording

- **The note's independence sentence.** "The three weightings share kinds and seeding". The seeds are
  random.Random(70000 + 1000·w + i) per weighting, so they differ, while the kind universe and the pipeline are shared.
- **"At 88 to 98%".**
- **"Two-way folding is typical ... under four declared weightings".**
- **The calibration.** W3 is undecided at 4 of 23.

## Report format (`codex_report.md`)

- A verdict line: Confirmed, Confirmed with fixes, or Refuted.
- One short section per point.
- Each fix marked Block, Narrowing or Not a block.
- The files you wrote.
