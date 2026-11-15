# Independent recomputation and critique: RULER-LEVEL-20261114-001

You are an independent referee's assistant. This is a proof epic with a census accounting. Check the proofs line by line and
recompute the census with **fresh code**.

## Rules for this task

- **Do not open, import or run:**
  - any `.py` under `research/RULER-LEVEL-20261114-001/exploratory/`, `proofs/RULER-LEVEL-20261114-001A/` or
    `experiments/LEVEL-REACH-20261114-001A/`, including the reach code's `pattern.py`.
- **You may read:**
  - `research/RULER-LEVEL-20261114-001/{ruler_level.md, advisor_question.md, advisor_answer.md}` and
    `exploratory/tree_plus_within.log`;
  - `proofs/RULER-LEVEL-20261114-001A/RULER-LEVEL-20261114-001A-P001_forest_ruler/{proof.md, result.json}`;
  - the proof of T1, `proofs/RANDOM-FATES-20261112-001B/RANDOM-FATES-20261112-001B-P001_no_cycle_and_four_consecutive/proof.md`;
  - LEVEL-REACH's note, specs and data: `research/LEVEL-REACH-20261114-001/`, and
    `artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/{results.jsonl.gz, records_slim.jsonl.gz}`.
- **Reuse the earlier referee code.** It is in `research/LEVEL-REACH-20261114-001/referee-R1/codex/`: `fresh_pattern.py`, the fresh
  pattern builder checked against the study's patterns; `fresh_search.py`, the exact least-bond search; and the `brute_audit/`
  tools.
- Write **only** inside `research/RULER-LEVEL-20261114-001/referee-R1/codex/`. No git commands that change state; no publishing.
- At most 4 processes and 12 GB; each command under about 20 minutes; the whole task under about 75 minutes. Use
  `/home/jscul/p-vs-np-contact-first/.venv/bin/python -B`. No network.
- Deliverable: `research/RULER-LEVEL-20261114-001/referee-R1/codex/codex_report.md`, plus scripts and JSON outputs there.

## Points to check (in order of value)

### 1. Theorem A** (proof.md)

1. **T1's hypotheses.** Check that T1 of RANDOM-FATES-001B covers this setting: a finite pattern, not necessarily connected, with
   addresses in one knot, deduplicated knots, and the least bond over all sets.
2. **The distance (the owner's point a).** Check the step "a knot spans at most one level step, so the distance is at least s" (T1's
   distance is the number of knots on the knot path), and that a descending chain gives distance exactly s.
3. **The statement's gap.** It covers "a descending chain" and "no path", but not an acyclic pattern with a path between the two
   levels and no descending chain. Is L = (least distance) + 2 the complete statement?
4. **Try to break it.** Run fresh exact search on random acyclic patterns of this object, including within-level knots, paths that go
   up before going down, and several components. Compare with min distance + 2.

### 2. Theorem A (the owner's point b)

Check every line:
- the three addresses of a knot are distinct, and distinct w give distinct knots;
- each address is the upper member of one knot and the lower member of one;
- the advisor's acyclicity argument: the deepest address on a cycle;
- no two knots share two distinctions;
- connectedness, and the existence of descending chains;
- that the words are automorphisms, which preserve length.

Then test it with fresh code on random tree-type descriptions at several N, including incidence-forest checks. Compute exact L on a
few at N = 6 to 7.

### 3. The census accounting (the owner's point c)

With the fresh builder, recompute on all 1,288 registered descriptions at N = 9:
- Berge acyclicity;
- descending-chain existence per s (k0 = 3, s = 1..4);
- path existence;
- Theorem A's form (exactly one distinct placement, of the tree type).

Cross-tabulate against LEVEL-REACH's outcomes, and reproduce the table in proof.md: 299, 170, 77, 158, 18, 106, 100, 73 and 287.
Reproduce the weights (394 of 605 ruler weight) and the 117.
- **Theory against census.** Say whether every acyclic outcome agrees with min distance + 2. Say whether "every direct, other,
  undecided and dead description is cyclic" is forced by the theorems (the leaf lemma gives a state; Theorem A** fixes the outcome)
  or is evidence.
- **"Two thirds of the census's rulers are explained by a theorem".** Is that fair? Acyclicity at N = 9 is a property of the
  truncation, and only Theorem A's form is acyclic at every depth. Give the shares by description and by weight at depth 9, and at
  every depth.

### 4. The six breaking cases

From `tree_plus_within.log`, recompute the six breaking cases ([2,2,2], [3,3,3], [3,3,4]×2, [3,4,4]×2) by fresh exact search, and check
the claim that each has a within-level knot holding two tree siblings. Say what "siblings" means here.

### 5. Known mathematics

From your own knowledge, flagged unverified, say how much of A and A** is known mathematics restated:
- the tree ruler;
- least implicate support on hypertrees;
- tree-structured CSPs and prime implicates of acyclic CNFs.

Say what, if anything, is new.

### 6. Wording

- "Exactly where the knots form no cycle" (the Answer). Is acyclicity necessary? There are 158 cyclic rulers.
- "Cycles break the ruler both ways".
- "Proved for every acyclic pattern".

## Report format (`codex_report.md`)

- A verdict line: Confirmed, Confirmed with fixes, or Refuted.
- One short section per point.
- Each fix marked Block, Narrowing or Not a block.
- The files you wrote.
