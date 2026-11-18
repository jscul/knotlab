# Referee report COPY-CLASS-R1 (fresh code, no Codex)

**Verdict: the facts are confirmed, but the post hoc rule is SEED's own clause restated. Block on one reading: "the far end knot
names the model" and the G1 capability built on it. The referee found an exact sign in its place.**
- **CRSWAP is confirmed on fresh seeds.** The referee used its own engine and 180 new starts. These include the lines of 14 and 16
  run to n = 34, past the study's sizes.
  - CRSWAP agrees with SEED on all 114,006 crossing-making extensions: 2,066 copy steps and 111,940 refused fills.
  - The proofs hold.
  - C1 holds on all 2,652,636 knot sets.
  - CR accepts none of the 2,066 copy steps.
  - Every copy step lies in COPY-READ's closure class (P5).
- **The agreement is trivial (the owner's question).** There are two reasons.
  1. **By construction on refused fills.** CRSWAP keeps SEED's clause (a) and searches a subset of SEED's candidates for clause (b).
     So it can accept only what SEED accepts. All 67,831 refused fills among the 68,547 "held out" agreements agree automatically.
  2. **On every copy step, CRSWAP's candidates are all the crossed splits.** Every crossed split separates the far end pair.
     - This holds on 2,066 of 2,066 copy steps on fresh seeds.
     - It also holds on 850 of 850 copy steps on the study's own engine, with its own seeds and code.
     - So CRSWAP is SEED's clause (b) word for word, and naming the far pair narrows nothing.
  - **CR's failure is the mirror image.** No crossed split separates the near pair: 2,066 of 2,066 copy steps. CR's candidate set
    was empty every time. It did not point at the wrong model; it pointed at nothing.
- **What is real instead (the referee's finding, exploratory).** One sign decides SEED's copy step exactly, with no comparison of
  crosser sets: **the far end pair is separated by every crossed split.**
  - It holds on all 2,066 copy steps and on none of the 111,940 refused fills on fresh seeds.
  - It holds on all 850 copy steps and none of the 84,352 refused fills on the study's own engine. That includes all 1,234
    clause-(b) refusals.
  - One half is proved here: the sign implies clause (a) (§2).
  - It still reads every crossed split, one bit each. So the obstruction for extent stands.
- **The wording and the scoring.**
  - "Named by the fill's own pairs" is not fair. The check reads a median of 91% of all splits, and at least 20%. **Narrowing
    (wording).**
  - P3 failed on its own terms, not from the swapped roles.
  - P4 was not measured, because its instrument was empty. **Not a block.**

## What holds

| Reading | Referee, fresh (180 starts) | Study's engine, all 135 starts (referee's cross-check) | Study |
| --- | --- | --- | --- |
| Crossing-making extensions; copy steps | 114,006; 2,066 | 85,202; 850 | 85,202; 850 |
| C1 on knot sets | 2,652,636 of 2,652,636 | not rerun | 2,056,136 of 2,056,136 |
| CR accepts | 0 copy steps, 0 refused | not rerun | 0 of 850, 0 refused |
| CRSWAP vs SEED | 2,066 of 2,066 accepted; 111,940 of 111,940 refused | not rerun | 850; 84,352 |
| Copy steps whose far pair is separated by every crossed split | **2,066 of 2,066** | **850 of 850** | not reported |
| Refused fills with that sign | **0 of 111,940** | **0 of 84,352** | not reported |
| Copy steps whose near pair is separated by some crossed split | 0 of 2,066 | not run | not reported |
| Refusals by clause (a); (b) mixed; (b) subset or superset | 108,242; 3,698; 0 | 83,118; 1,234 | 83,118; 1,234; 0 |
| Copy steps in COPY-READ's closure class (P5) | 2,066 of 2,066 | not rerun | 850 of 850 |
| Model's crossers / splits, median | 0.29 | not run | 0.27 |
| Gained-split readings with a model of two or more crossers | 2,660 of 3,438 | not run | 1,089 of 1,544 (post hoc) |

- **The referee's engine** (`referee_class.py`):
  - SEEDK from COPY-READ-R1: knot-local fills from MID-RULE-R1's `local_fills`, with no state limit.
  - Its own crossing graph, with r's quadrants.
  - SEED's two clauses, cross-checked against KNOT-SWITCH-R1's `seed_ok` (0 disagreements).
  - Fresh starts: every bracketing of 5, 6 and 7; the bracketings of 8 at indices 1, 4, 7, … (the study took 0, 3, 6, …); 30
    uniform random lines of 12 to n = 30; 30 of 14 and 15 of 16 to n = 34. Fresh seeds throughout.
- **The cross-check** (`referee_class_crosscheck.py`) imports the study's `classlib`, `run` and `posthoc`, read only. It shows that
  the finding is not an artifact of the referee's engine. Its counts match the study's exactly.

## 1. Is CRSWAP a real restatement, or trivial? (the owner's question)

**It is trivial.**
- **On refused fills.**
  - `posthoc.py` reads clause (a) on all new crossings, which is SEED's clause (a) itself.
  - It then seeks the model in `cand_swap ⊆ active`, while SEED seeks it in `active`.
  - So CRSWAP's acceptance implies SEED's, for every knot set. No false acceptance was possible.
- **On copy steps.**
  - In every copy step, every crossed split separates the far end pair. So `cand_swap == active`, and CRSWAP's search is SEED's.
  - A random candidate set of the same size would also pass every copy step, because it is the whole set.
  - On the referee's engine each copy step has exactly one knot set (one middle knot and two end knots, exactly one end pair
    touching the middle pair), so there was no choice among certificates either.
- **So the score proves less than it seems.**
  - "Agreed with SEED on all 68,547 extensions, held out" tests the engine, not the rule. The hold-out design is sound in form, but
    the rule it holds out is SEED's clause.
  - The note's reading, "the other end knot points at an existing split whose crossings it must copy exactly", is not supported.
    Every crossed split separates the far pair, models and non-models alike: up to 12 models per gained split, all of them crossed.
- **The roles the data do support.**
  - The gained split (the tail) separates the near pair and only it: 3,438 of 3,438 readings.
  - No crossed split separates the near pair: the tail attaches inside one cell of the crossed splits.
  - Every crossed split separates the far pair: the far pair spans everything that crosses.
- **Verdict. Block** on the reading "the far end knot names the model, so the copy step is named by the fill's own pairs". This is
  the G1 checkpoint's capability and the third role in "In the owner's terms".
- **What stands.** CRSWAP's agreement holds, as a fact. It is a restatement of SEED, not a localisation.

## 2. The exact sign, and half of a proof

**The sign.** A crossing-making fill is a copy step exactly when the far end pair of its knot set is separated by every crossed
split. The knot set is one middle knot and two end knots, with exactly one end pair touching the middle pair.
- **Computed:** exact on 114,006 fresh extensions and on all 85,202 of the study's. That is 2,916 copy steps and 196,292 refused
  fills, with no exception either way.
- **How it was found.** The referee saw it on the copy steps of four of its own starts. It then scored it, without change, on all 180
  fresh starts and on the study's 135. It is exploratory and should be frozen before it is used.

**Proved: the sign implies clause (a).**
- The far end knot is an end knot: B(p, q, r) or B(q, p, r), with r at an end. Wherever its pair differs, it gives r one fixed
  member's value, q's in the first case.
  - Case B(p, q, r): it forbids p = r ≠ q, so where p ≠ q, r = q.
  - The other case is symmetric.
- Take two crossed splits that both separate p from q. On the states of both, p ≠ q, so r falls on q's side of each.
- r's quadrant for the pair therefore contains q and was not empty, so the two splits do not come to cross.
- With the sign, no two crossed splits come to cross, and clause (a) holds. ∎

**Not proved.**
- That the sign implies clause (b), the copy itself.
- The converse: that a copy step has the sign, and that no crossed split separates the near pair.

**What it means.**
- SEED's copy step does not need a model search. It is decided by one bit per crossed split: does the split separate the far pair?
- In a full two-way grid the distinctions that every split separates are the two opposite extremes of both orders. So a copy step
  plausibly ties r beyond a corner of the grid.
  - This reading is an interpretation, not checked.
- The read still covers every crossed split, so the study's obstruction for extent stands, in a simpler form.

## 3. "Named by the fill's own pairs" (the owner's question)

**Not fair as written.**
- CRSWAP's candidates are every crossed split.
- The check reads the end pairs' splits, their crossers and the models' crossers. That is a median of 91% of all splits, with a
  minimum of 20% and a maximum of 100%:
  - 100% median on the bracketings of 5 to 8;
  - 91% on the lines of 12;
  - 87% on the lines of 14 and 16.
- The note's own caveat, "local in what it names, not bounded in what it reads", undersells this: what it names narrows nothing.
- **Fair wording.** "The copy step is decided by SEED's clause. Restricting the model to the far end pair's crossed splits changes
  nothing, because every crossed split separates the far pair. What decides the step is that separation (computed), and reading it
  takes every crossed split." **Narrowing (wording).**

## 4. The proofs C1 to C3

- **C1 holds, given MID-RULE's E1** (confirmed in MID-RULE-R1).
  - An end knot pins r only on states where its pair differs.
  - The two states realising a new crossing therefore lie on splits separating the two end pairs, one each.
  - Fresh: 2,652,636 of 2,652,636 knot sets.
- **C2 holds.**
- **C3 holds as proved.** A model's crossers are the whole other chain (N3).
  - Its last sentence goes further than the proof: "a rule that checks the copy exactly must see one whole order".
  - The proof shows what the model's crossers are. It does not show that every exact rule must read them.
  - The sign of §2 decides the step without comparing crosser sets, though it still reads every crossed split.
  - **Narrowing (wording):** "SEED's clause compares a whole order" is proved; "every exact rule must see one" is not.

## 5. The scoring of the failed predictions (the owner's question)

- **P1 failed, fairly.** The cause was not a swapped model, though. CR's candidate set was empty in every copy step, because no
  crossed split separates the near pair.
- **P3 failed on its own terms.**
  - Its clause-(b) part is measured against SEED's models among all crossed splits, independent of CR's roles.
  - Every clause-(b) refusal is mixed: 3,698 of 3,698 fresh, and 1,234 of 1,234 in the study.
  - So "P1, P3 and P4 turn on the same mistake" is wrong for P3.
- **P4 was not measured.**
  - It was read through CR's models, and CR's candidate set was empty on every copy step, so the instrument returned 0 by
    construction.
  - It should read "not scored as frozen (the instrument depended on CR)", not "failed".
  - The post hoc reading would favour it: 2,660 of 3,438 fresh readings have a model of two or more crossers.
  - The score becomes "2 of 4 scored predictions held; P4 unscored".
- **P2 is an engine check, as labelled.** CRANY is SEED's clause read on the end pairs' splits, which equal all splits' new
  crossings by C1.
- **Not a block.**

## Fixes for the thread (listed for the owner, not folded in)

1. **The answer, "In the owner's terms" and the G1 checkpoint.**
   - Withdraw "the rule names only the fill's own pairs and decides SEED's copy step" as a capability, along with "the other end knot
     points at an existing split whose crossings it must copy". CRSWAP is SEED's clause restated, because every crossed split
     separates the far pair (2,066 of 2,066 fresh; 850 of 850 in the study).
   - Keep the agreement as a fact.
   - Record the roles the data support: the tail separates the near pair; no crossed split does; every crossed split separates the
     far pair.
   - **Block (one reading).** One entry in `docs/CORRECTIONS.md`.
2. **CR's failure.** Explain it as an empty candidate set (no crossed split separates the near pair), not a swapped pointer.
   **Narrowing (wording).**
3. **"Named by the fill's own pairs" and C3's last sentence.** Use §3's and §4's wording. **Narrowing (wording).**
4. **The scoring.** P3 failed independently of the roles; P4 is unscored, not failed; "2 of 4 scored held". **Not a block.**
5. **The direction.** Direction 1 (freeze and prove CRSWAP) is moot as stated, since CRSWAP is SEED. Replace it with this: freeze the
   sign, "the far end pair is separated by every crossed split", and prove it equivalent to SEED's copy step. The half "sign ⇒
   clause (a)" is done (§2). Then ask whether the sign can be read from the betweenness among the move's distinctions (the copy
   class), which would bound what it reads. **Not a block; a lead.**

## How the work was split

- **The referee:**
  - read the note, the pre-registration, the proofs, `classlib.py`, `run.py`, `posthoc.py` and the read-outs, and checked C1 to C3
    by hand;
  - wrote `referee_class.py`: fresh starts and seeds on its own engine, with SEED, C1, CR, CRSWAP, CRNOT, CRBOTH, where every
    model lies, the candidate sets' sizes, the random-candidate control, the share of splits read, the refusal breakdown and the
    sign;
  - wrote `referee_class_crosscheck.py`, which runs the study's own engine on all its 135 starts;
  - proved "sign ⇒ clause (a)".
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_class.py`** and **`referee_class.json`**.
- **`referee_class_crosscheck.py`** and **`referee_class_crosscheck.json`**.

Reproduce, from `research/COPY-CLASS-20261118-001/referee-R1/`. The first command takes about 15 seconds on 16 workers, the second
about 5 minutes.

```sh
../../../.venv/bin/python -B referee_class.py > referee_class.json
../../../.venv/bin/python -B referee_class_crosscheck.py > referee_class_crosscheck.json
```
