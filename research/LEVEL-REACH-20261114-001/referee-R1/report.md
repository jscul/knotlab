# Referee report LEVEL-REACH-R1 (Codex-assisted, fresh code)

**Verdict: Confirmed with fixes, with two Blocks.**

**What stands.**
- **The census values.** Every sampled depth-9 least bond survives a fresh exact recomputation, with zero disagreements in 112
  cells. A brute-force panel one size up agrees, and depths 10 and 11 change none of the 124 decided cells.
- **Q0 is stronger than claimed.** It holds on both readings of the undecided cell.

**The two Blocks.**
- **"L is non-increasing in N" is false.** The pre-registration and the note give it as settled by construction ("deeper levels can
  only lower a bond"). Two registered descriptions break it, and I verified one myself.
- **Not every refutation was kept.** The 23 dead-union refutations are not retained, although the pre-registration says every one is
  kept.

**What else needs fixing.**
- **Q3's wording.** "All 2,894 least bonds found lie within levels ≤ their target" is false for 26 of them. Q3's failure rule ("needs
  a member below") is not met for any of the 2,894.
- **Composition.** Adjacent-level joining alone does not compose into a ruler. The proof epic must not assume it, nor monotonicity.

**How the work was split.** The background referee thread owns the verdict.
- **The referee.**
  - Checked the objects gate, which returns `ok`.
  - Checked the isolation boundary: the only study file named in Codex's log is quoted from my own brief.
  - Recomputed the outcome rule and tightened bounds from the full records (`referee_bounds.py`, `.json`).
  - Found Q3's 26 bonds that reach below the target, and that the 3 cases with an undecided L_target have overshoot 0.
  - Read the thread's budget and filter additions in `job.py`.
  - Independently checked a monotonicity counterexample from the stored knot lists, by SAT (`referee_monotonicity_check.py`), and
    the composition counterexample by truth table (`referee_composition_check.txt`).
- **Codex.** The Codex command-line tool, at the owner's choice of model and effort, ran fresh code for about 40 minutes.
  - It ran the exact search, the larger brute force, the depth checks, the certificate replay and the recount.
  - It found the monotonicity counterexamples, the composition example and the missing union-death certificates.
- **Advisor.** The advisor model was not consulted.

## 1. Optimality (Codex)

**The fresh search.** It compiles the existence of a completing state into a circuit by quantifier elimination. A cardinality-bounded
SAT query then finds forbidden supports, and each candidate's minimality is checked on every assignment of every maximal proper
subset. A final audit confirmed that all 56,971 blocked subsets miss a required level.

**The sample.** 12 chained, 8 direct, 6 other and 4 undecided descriptions, plus 2 Q3 cases.
- **The decided cells.** All 112 depth-9 cells agree exactly, with **zero disagreements**. That includes all 12 cells where the ruler
  gives L(4) = 6, each excluding every smaller bond, and all 9 "> 10" cells, exhausted through size 10.
- **The undecided profiles.** They stay unresolved, with fresh lower bounds L(s) ≥ 3 and L(4) ≥ 4.

**A larger brute force.** 29 descriptions at N = 4 (through size 7) and N = 5 (through size 4): 4.3 million crossing supports and 6.4
million SAT projections. All 62 decided queries agree with the fresh search.

**Deeper levels.** For 12 chained, 2 [3,3,3,3] and 2 [3,3,4,4] descriptions at N = 10 and N = 11, all 124 decided cells equal their
N = 9 values. 4 cells timed out.

**The certificates.** Of 184 retained CNF/LRAT pairs, every CNF was rebuilt and matches, and every proof checks with the earlier
referee's hint-free RUP checker (3,619 additions). 3,236 witness states and 4,028 proper-subset assignments check. "> 10" rests on
exhaustion, which was reproduced in the 9 sampled cells.

**Not a block** for the sampled values. **Narrowing:** this is sampled finite validation, and the search's UNSAT answers are
replayable, not LRAT-certified lower bounds.

## 2. Block: monotonicity in N is false

**Where it is claimed.**
- The pre-registration, under "Settled by construction": "L is non-increasing in N (more knots, fewer states), so 'chained' and
  'growing' are readings to depth 9, and bounded readings are upper bounds that deeper levels can only lower".
- The note's Words: "deeper levels can only lower a bond".

**Why it fails.** More knots keep a set non-full, but they can make a proper subset non-full too. That destroys the old bond's
minimality, and the smaller bond inside it may miss the top or the target.

**Counterexamples** (registered descriptions).
- **`162021bb…`** (k0 = 1, s = 2). L = 3 at N = 3, with bond [1, 7, 9]. At N = 4, no bond of size ≤ 3 holds both levels.
  - **The referee's check.** From the stored knot lists (33 and 81 knots; the N = 3 knots are contained in the N = 4 ones), by SAT
    projections over every support of size 2 and 3: the same result.
- **`a0ce47179bf2…`** (W_R draw 1185, at the study's k0 = 3, s = 1). L₄(1) = 3, with bond [7, 15, 16]. L₅(1) > 4, exhausted through
  size 4.
  - **Its depth-9 reading.** Its profile at depth 9 is [> 10, > 10, > 10, > 10].
  - **At top level 2.** The same key goes from L = 3 to no crossing bond at all.

**What is unaffected.** The census values as **depth-9 readings**. In the depth panel, N = 10 and 11 changed no decided value.

**What changes.**
- "Bounded readings are upper bounds that deeper levels can only lower" has no basis.
- G-mono cannot support the lemma. It also ran 49 of 50 keys: the 50th failed on memory four times, which the note discloses.
- The downstream proof epic must not use N-monotonicity.

**Block** (on the settled-by-construction lemma).

## 3. Block: the union-death certificates were not kept

**What the pre-registration says.** "Every refutation's CNF and LRAT proof, gzip-compressed, named by the CNF's SHA-256" (a standing
rule after LEVEL-RETURN-R1).

**What the records hold.** All 23 dead-union records lack a CNF hash, a proof hash or a retained name. Their textual
"checked" assertions bind no retrievable proof.

**The fresh check.** Codex rebuilt 3 weighted dead cases, refuted them with Glucose4, and checked the new DRUP proofs by hint-free RUP.
That does not repair the 23 records.

**The weight is small.** These are 11 of 1,423 W_R draws.

**Block** (on the evidence claim for the dead unions).

## 4. The outcome rule and the frozen verdicts (the referee; Codex recounted)

**The recount.** It reproduces every label and weight exactly (`referee_bounds.json`, `codex/outcomes/independent_summary.json`).

**The undecided cell, tightened.** An undecided profile is counted toward the ruler's (or direct's) upper bound only if its decided
levels allow it.
- **The ruler.** 126 of the 150 undecided weight could still be the ruler.
- **Direct.** 91 could still be direct.
- **No union is undecided** in W_R.

| Quantity | As reported | Tightened |
| --- | --- | --- |
| Q0 none / alive | 36.8–47.4% | **36.76% exactly** (an undecided level is always connected) |
| Q0 chained / alive | 42.8–53.5% | 42.85–51.77% |
| Q0 direct / alive | 5.0–15.7% | **5.03–11.47%** |
| Q1 ruler / 893 | 67.7–84.5% | 67.75–81.86% |
| Q2 direct / 893 | 8.0–24.7% | 7.95–18.14% |

**The verdicts.**
- **Q0 holds on both readings**: none ≥ 25% and direct ≤ 15% at the tightened bounds. That is an upgrade from "held on the point
  reading". **Not a block.**
- **Q1 and Q2 are not refuted**, under their one-sided frozen failure rules. But neither is established: the ruler's lower bound is
  below 70%, and direct's upper bound is above 10%.
  - **Q1's denominator.** Its 893 include 13 "> 10" draws and 150 undecided ones, for which a bond at every s is not shown.

  **Narrowing:** write "not refuted" with the bands, not "held".
- **The "none" label.** It means no join, or disconnected at some s. A connected pattern can still have no crossing bond (section 6),
  so 36.76% is the share of the label, not of all patterns with no bond. **Narrowing.**

**"Direct" (owner's point d).** Constant over s = 1..4, including 3, is faithful to the frozen words "one constant value ≥ 3". But it
is not "bounded".
- **The evidence.** The profiles [3,3,4,4] (45 weight) and [3,3,3,4] (3) show slow growth, so a constant 3 over four values cannot be
  told apart from growth at rate ≤ 1/4.
- **The fix.** Write "constant over s = 1..4 at depth 9". Drop "binds every level read with a fixed number of distinctions" and
  "depth costs nothing" as asymptotic statements. **Narrowing.**

**"Other" (4.7%).** By weight:
- 45 are the **half-rate ruler** [3,3,4,4];
- 13 are "> 10" profiles (10 of them [3, > 10, > 10, > 10]);
- the rest are scattered.

**Narrowing:** name the half-rate profile; it is a reach type of its own.

**Q3.** Of the 2,894 least bonds found, 26 (in 16 descriptions) have a member deeper than their target, up to 5 levels deeper.
- **The equal-size alternatives.** Every one has an equal-size alternative within the target's levels. That is shown by L_target =
  L_N in 2,891 cases, and in the 3 whose L_target search ran out of time by the found bond itself, which has overshoot 0 there.
- **What follows.** The note's "All 2,894 least bonds found lie within levels ≤ their target" is false. Q3's failure rule, "any found
  bond **needs** a member below its target", is not met, so Q3 holds on its frozen rule.

**Narrowing:** write "every least bond has an equal-size alternative within its target's levels; 26 found ones reach below it". This
is a correction of a published sentence.

**Q4 failed by the frozen bootstrap, but the verdict is sensitive.** The point difference reproduces (27.3% against 4.6%).
- **The frozen bootstrap.** A fresh 100,000-replicate version of it gives [−6.6, 40.0] percentage points.
- **A joint resampling.** Seven canonical automata occur in both classes, and resampling them jointly gives [0.24, 39.6].

That variant is post hoc and is not promoted. **Narrowing:** say the verdict depends on how the shared automata are resampled.

**Q5 reproduces.** The exponential class's intervals were omitted. They are 9.9–16.1% direct and 68.4–76.6% ruler, ignoring
clustering and censoring. **Not a block.**

## 5. The thread's additions (owner's point c; the referee and Codex)

**The budget.** It is a parameter, and the registered run used 300 s per (key, s), as frozen (every record says 300). A stale comment
in `job.py` says "the registered run sets 150". The budget is shared at each s by L_N, L_target and the per-target searches, with L_N
first. **Not a block.**

**The population filter** (W_R index < 2000; E_R bounded or polynomial). It is frozen in the pre-registration and applied correctly:
1,288 descriptions, and 1,423 accepted W_R draws once rejections are taken out. **Not a block.**

**The rest.** Certificate retention, memoisation caps and the presence encoding can change timing, the witnesses chosen and undecided
outcomes, but not a value the exact search decides. The retention gap is section 3. **Not a block.**

## 6. Composition, and what the proof epic must assume

**The claim.** The pre-registration ("Knots joining only adjacent levels compose into a chain of s + 2 wherever they compose") and the
note's Reading ("Knots join only adjacent levels, so a chain of joining knots composes into a bond of s + 2").

**Why it does not hold in general.** Take NAE(a, u, v) and NAE(u, v, b), with levels {a}, {u, v}, {b}.
- **The states.** The pattern has 10 allowed states, and its only bonds are the two knots, {a, u, v} and {u, v, b}.
- **The bond.** No bond holds both a and b, even though knots join adjacent levels and the pattern is connected. The referee checked
  this by truth table.

**Narrowing** for the note's Reading. For the proof epic, it must state an explicit composition (overlap) hypothesis, prove its lower
bound independently, and drop N-monotonicity as a premise.

## 7. Wording

1. **"In about half of the living patterns ... the ruler".** The ruler is 42.85–51.77% of the alive weight. Write "two fifths to a
   half". **Narrowing.**
2. **"The typical reach across levels is a ruler"** (the goals row). Among draws with a bond at every s it is 67.75–81.86%. Among all
   alive draws it is the most common outcome (42.85–51.77%, against none at 36.76%), not a majority. Write "the most common reach".
   **Narrowing.**
3. **"To depth 9': deeper levels can only lower a bond".** Remove it (section 2). **Block** (with section 2).

## Fixes for the thread

1. **Remove N-monotonicity** from the pre-registration's settled list as published, and from the note. Read every census value as
   depth 9 only. Tell the proof epic not to use it. **Block.**
2. **The 23 dead-union refutations.** Regenerate and retain them with hashes, or say they are not archived. **Block** (on the evidence
   claim).
3. **Correct Q3's sentence:** equal-size in-target alternatives exist, and 26 found bonds reach below. **Narrowing.**
4. **Q1 and Q2:** "not refuted" with the tightened bands. **Q0** holds on both readings. "None" is a label at 36.76%. **Narrowing /
   Not a block.**
5. **"Direct"** is constant over s = 1..4 at depth 9, not "bounded". Name the half-rate profile [3,3,4,4]. **Narrowing.**
6. **The Q4 sensitivity**, and the composition hypothesis for the proof epic. **Narrowing.**
7. **The wording in section 7.** **Narrowing.**

## Files

- **The referee's.** `referee_bounds.py` and `.json`; `referee_monotonicity_check.py` and `.json`; `referee_composition_check.txt`.
- **Codex's, in `codex/`.**
  - `codex_report.md`, `fresh_pattern.py`, `fresh_search.py`, `run_fresh.py` and `audit_summary.json`;
  - `brute_audit/` (the larger brute force and the counterexamples), `cert_audit/` (the certificate replay and the depth panel) and
    `outcomes/` (the recount, `q3_membership.json`, `monotonicity.json` and the Q4 clusters);
  - `dead_recomputation.json` and `validation_manifest.json`.
- **Kept out of git.** `codex/outcomes/direct_pair_audit.json` (2.5 MB) stays on disk; its hash is in `large_file_hashes.json`.
