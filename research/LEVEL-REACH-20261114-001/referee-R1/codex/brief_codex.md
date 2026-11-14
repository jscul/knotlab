# Independent recomputation and critique: LEVEL-REACH-20261114-001

You are an independent referee's assistant. The study's search was written by another coding agent and extended by the research
thread, so your recomputation must be **fresh code** from the specification and the mathematics. A proof epic ("least bond = level +
2 for chained patterns") builds on this census, so **attack the optimality claims hardest**.

## Rules for this task

- **Do not open, import or run any `.py` or `.c` under** `experiments/LEVEL-REACH-20261114-001A/`, nor
  `research/LEVEL-REACH-20261114-001/summarize.py`.
- **You may read:**
  - the data: `artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/{results.jsonl.gz,
    records_slim.jsonl.gz, summary.json, raw_hashes.json}`;
  - the JSON gate and provenance files under `experiments/LEVEL-REACH-20261114-001A/.../codex/` (`g_*.json`, `*provenance*.json`,
    `mono_gate/results.jsonl`, `mono_*retry*/results.jsonl`, `mono_selection.json`);
  - the kept certificates `.../codex/certificates/` (gzip CNF and LRAT, named by the CNF's SHA-256);
  - `research/LEVEL-REACH-20261114-001/{level_reach.md, preregistration.md, design.md, codex_spec.md, codex_spec_addendum.md,
    advisor_*.md, summary.json}`;
  - ADDR-KNOTS's spec `research/ADDR-KNOTS-20261113-001/codex_spec.md`.
- **Reuse the earlier referee code.** It is in `research/ADDR-KNOTS-20261113-001/referee-R1/codex/` (`fresh_patterns.py`, the
  checkers `check_rup.py`, `fast_certificates.py`) and `research/LEVEL-RETURN-20261113-001/referee-R1/codex/` (`automata/`,
  `rigidity_*.py`).
- Write **only** inside `research/LEVEL-REACH-20261114-001/referee-R1/codex/`. No git commands that change state; no publishing.
- **The machine is free.** Use at most 4 processes and 12 GB; each command under about 20 minutes; the whole task under about 90
  minutes. Use `/home/jscul/p-vs-np-contact-first/.venv/bin/python -B` (numpy, python-sat). No network.
- Deliverable: `research/LEVEL-REACH-20261114-001/referee-R1/codex/codex_report.md`, plus scripts and JSON outputs there.

## The object

The study's object, from `codex_spec.md`:
- **Distinctions.** Addresses of length 0..9, with id 2^n − 1 + x.
- **Terms.** (w, a) send x to w(x) or w(x)·a.
- **Knots.** A placement is three terms. At every address where all three images have length ≤ 9 and are distinct, they form an
  NAE knot.
- **The reach.** L_N(s) is the least bond (minimal non-shattered set) holding an address of level 3 and one of level 3 + s, with
  members anywhere in levels 0..9, for s = 1..4; "> 10" means proved that no bond of size ≤ 10 exists.

## Points to check (in order of value)

### 1. Optimality, freshly

Write your own exact least-bond search, using a method different from the study's implicit hitting set if you can. For example:
- enumerate forbidden partial assignments by size, with SAT and blocking, among supports in the connected component;
- or a MaxSAT/QBF-style formulation, with the minimality of the support checked separately.

Build the pattern yourself from the key with fresh code (ADDR-KNOTS-R1's `fresh_patterns.py` may help). Then recompute L_N(s) on a
stratified sample:
- about 12 **chained** descriptions (ruler 3, 4, 5, 6), including s = 4, where "no bond of size ≤ 5" is the key lower bound;
- about 8 **direct** ones: [3,3,3,3] and [2,2,2,2];
- about 6 **other**, including [3,3,4,4] and some "> 10";
- about 4 **undecided** ones.

Report every disagreement in full. Say how your search proves optimality.

### 2. Beyond G-brute's tiny patterns

G-brute used N = 3, k0 = 1, S = 2 (15 distinctions). Run an exhaustive cross-check one size up or more, for example N = 4 or 5 with
k0 = 2 and S = 2, on random descriptions. Compare a brute force over supports (with SAT projections, or state enumeration where it
is small) against your search, and against the study's numbers where the study's population gives them.

### 3. Depth sensitivity of the ruler

L is non-increasing in N, so "chained" is a reading to depth 9.
- **Deeper levels.** For about 10 chained descriptions, recompute L(s) at N = 10 and N = 11, for s = 3 and 4 especially (the margin
  below the target is only 2 levels at s = 4). Does the ruler survive?
- **The other profiles.** Do the same for [3,3,3,3] and [3,3,4,4] profiles.
- **G-mono.** Check its 49 of 50 keys (from the gate data): which key did not finish, and was any L_10 < L_9?

### 4. The certificates

On a sample of the kept certificates:
- rebuild the CNF from the description yourself, and check that it equals the stored CNF up to clause order;
- check the LRAT proof with an independent hint-free RUP checker (ADDR-KNOTS-R1's);
- check the recorded witness states for every maximal proper subset of the bond.

For "> 10" claims, say what proves them.

### 5. The outcome rule and the frozen verdicts

Recompute from the full records, with your own code:
- the outcome classes (no join, dead, no bond, direct = constant over s = 1..4, chained = s + 2, other, undecided);
- the weights (multiplicity among W_R draws with index < 2000);
- Q0 to Q5.

Then judge:
- **(a) "direct".** Is "constant over s = 1..4, including L = 3" a fair operationalisation of the frozen "direct (L bounded: ...)"?
  The profiles [3,3,4,4] (45 weight) and [3,3,3,4] exist, so is a constant 3 over four values distinguishable from slow growth?
- **(b) The undecided bands.** Is "held" a fair reading of Q0, Q1 and Q2 given them? Tighten the bounds by counting an undecided
  profile toward the ruler (or direct) upper bound only if its decided levels are compatible with it, and report the tightened bounds.
- **(c) "None".** Is its share actually decided? Undecided levels are connected.
- **(d) The other class.** Describe its composition.

### 6. The thread's additions to Codex's code

From the provenance JSON files only (not the code), say what changed: the budget and population parameters, certificate retention,
memoisation, presence encoding. Say whether each could change a decided result, or only timing and undecided outcomes.

## Report format (`codex_report.md`)

- A verdict line: Confirmed, Confirmed with fixes, or Refuted.
- One short section per point.
- Each fix marked Block, Narrowing or Not a block.
- The files you wrote.
