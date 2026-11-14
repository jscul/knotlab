# Independent recomputation and critique: READ-RULE-20261114-001

You are an independent referee's assistant. The study's census code was written by another coding agent, so your recomputation
must be **fresh code** from the notes and the mathematics.

## Rules for this task

- **Do not open or import any `.py` under** `experiments/READ-RULE-20261114-001B/` or `proofs/READ-RULE-20261114-001Z/`. You may
  read the following:
  - their data (JSON/JSONL, including `artifacts/READ-RULE-20261114-001B/.../census_run_results.jsonl.gz`) and the study Codex's
    `REPORT.md`;
  - `research/READ-RULE-20261114-001/{read_rule.md, preregistration.md, codex_spec.md, advisor_*.md}`;
  - the proofs `proofs/READ-RULE-20261114-001A/READ-RULE-20261114-001A-P001_read_rule/proof.md`;
  - CARRY-BOUND's note and data (`research/CARRY-BOUND-20261114-001/`,
    `experiments/CARRY-BOUND-20261114-001A/**/*.json*`);
  - the census records `artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/families.jsonl.gz`;
  - the earlier referee code under `research/CARRY-BOUND-20261114-001/referee-R1/codex/` (`grow_core.py`, `grow_search.py`: an exact
    relation-free bond search; `grow_global_exact.py`; `window_audit.py`; `scope_audit.py`) and
    `research/CENSUS-FORGET-20261114-001/referee-R1/codex/`. Reuse these.
- Write **only** inside `research/READ-RULE-20261114-001/referee-R1/codex/`. No git commands that change state; no publishing.
- At most 3 processes and 10 GB; each command under about 15 minutes; the whole task under about 75 minutes. Use
  `/home/jscul/p-vs-np-contact-first/.venv/bin/python -B`. No network.
- Deliverable: `research/READ-RULE-20261114-001/referee-R1/codex/codex_report.md`, plus scripts and JSON outputs there.

## Points to check (in order of value)

### 1. Attack the dichotomy hardest

This is the epic's strongest and newest claim (proof.md, "The dichotomy (pumping)"). Note that the pre-registration froze it only
under conditional rectangularity; the proof drops that hypothesis.

1. **The interface and indexing.** A member-free stretch is levels a+1..b, unoccupied. The product of per-call relations "from c_a
   to c_b" covers the blocks c_a..c_{b−1}, and c_a's block can hold members.
   - Say exactly which blocks the pumped product must cover, and which ports form the top and bottom interface. Can the off-by-one be
     repaired (for example, by taking the product over c_{a+1}..c_b)? Check that the factorisation across the stretch is then exact,
     including side subtrees of stretch copies, ports carried by identity (main ports and others), and members in c_a's block.
   - Check that the moved set is a bond (equal projection on every subset), that its target is an own distinction of a covered copy at
     depth s + Π reached through S calls, and that the wrapper offset is handled.
2. **Look for sublinear unbounded growth.** Try to break it on some residue.
   - Compute L(s) exactly, relation-free, with members anywhere and any covered target, for growers and slow-looking families as far
     as cheap, and look for any sequence inconsistent with "eventually bounded or ≥ s/(m+1) − 1".
   - Try to design a family by hand that would grow like √s, or put members at sparse levels.
   - If the proof is right this must fail. Say why each attempt fails, or report the counterexample in full.
3. **Explicit constants and thresholds.**
   - For a sample of families, compute m, the number of reachable states (per-call product, carry map), the period Π = m!, and the
     linear constant 1/(m+1).
   - Give the bounded branch's threshold explicitly. For example, any s with L(s) < s/(m+1) − 1 forces a long stretch; what does that
     give for s₀ and the bound?
   - Say whether "eventually" and "at least linear" are effective, and whether boundedness per residue is decidable or only
     semi-decidable from this proof.
4. **Is it known mathematics in kind?** No network; from your own knowledge, flagged as unverified. Compare it with:
   - pumping in finite monoids;
   - the ultimate periodicity of tropical (min-plus) matrix powers (cyclicity theorems);
   - sublinear growth in distance automata for max-over-words (as contrast: L is a min over targets).

   Say what is new here.

### 2. Theorem R's exception is exact, both directions

1. **By brute force over every context relation.** Over all complement-closed projections P on {p, x} and every tie status of z,
   check that the knot's W = {p, x, z} contains a bond holding p and x **iff** the exception fails.
2. **In the census.** Run the same check on the 9 exception families and a sample of 20 non-exception families, by direct exact search
   with no relation code.
3. **The quantifier.** The theorem needs one covered copy at depth s satisfying the hypothesis and avoiding the exception. Recount
   R's coverage of the bounded weight under that "some carried state" reading, against the 87.5% under the stricter one. Check that the
   9 exception families are all bounded at 3 by other bonds (Q1).

### 3. Theorem R1 and the counts

- Check its proof and its pendant condition: no other constraint, no call argument.
- Recount 469 of 5,067 window-bounded in-scope families (9.1% of the bounded weight). The study Codex's REPORT.md has 471 in scope on
  every residue; reconcile the two.

### 4. Q3's counterexample family

Verify L(s) = 2 at depths 1 to 6 in both variants by direct exact search. Check the explanation: "u ≠ a" ties the carried port to an
own distinction.

### 5. The study Codex's five ambiguities (REPORT.md)

Judge each, and say which reading the theorems need.

### 6. Wording

- **Per residue.** The Reading's "two speeds only" against per-residue (L may be bounded on one residue and linear on another).
- **Weak rate.** "Nothing grows slowly" against the possibly huge m, which makes the linear rate weak.
- **The frozen statement.** That the proved dichotomy differs from the frozen one.
- **"No family is known".**
- **Scope.** That every statement stays within covered targets (copies of S reached through S calls).

## Report format (`codex_report.md`)

- A verdict line: Confirmed, Confirmed with fixes, or Refuted.
- One short section per point.
- Each fix marked Block, Narrowing or Not a block.
- The files you wrote.
