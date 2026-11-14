# Referee report READ-RULE-R1 (Codex-assisted, fresh code)

**Verdict: Confirmed with fixes, with one Block on the converse.**

**What stands.**
- **The theorems.** R, R1, Claim 1′ and the per-residue dichotomy are confirmed. The dichotomy's proof needs two repairs, neither of
  which needs rectangularity.
- **The census figures.** They reproduce, with R's coverage correctly 87.6%.

**The Block.**
- **What the note says.** The converse ("growth needs every carried value unread") is open, with no known exception.
- **What Codex found.** A family whose carried values are read, in the note's own sense, at every copy, yet whose bond grows as
  L(d) = d + 2.
- **What remains true.** The converse with "read without the exception" is not open. It follows from Theorem R and the dichotomy, so
  that half of the rule is now a theorem.

**How the work was split.** The background referee thread owns the verdict.
- **The referee.**
  - Checked the objects gate, which returns `ok`.
  - Checked the isolation boundary: the study's Python appears in the run log only in file listings.
  - Brute-forced R's exception over all 7 living projections.
  - Read the pumping proof and found the indexing slip at the stretch's top before Codex reported.
  - Independently recomputed Codex's converse counterexample by brute force (`referee_converse_check.py`: L(d) = 3, 4, 5, 6 at d = 1
    to 4, with witnesses).
  - Derived that the effective converse follows from R and the dichotomy.
- **Codex.** The Codex command-line tool, at the owner's choice of model and effort, recomputed from fresh code in about 25 minutes.
  It found the second proof defect and the converse counterexample.
- **Advisor.** The advisor model was not consulted.

## 1. The dichotomy (Codex; the referee on the proof)

**Two defects, both repairable. Not a block.**

1. **Interfaces.** The member-free stretch is levels a+1..b, but the product "from c_a to c_b" covers the blocks c_a..c_{b−1}, and
   c_a's block can hold members.
   - **The repair.** Take the product over the blocks c_{a+1}..c_b, with top interface the ports of c_{a+1} and bottom interface the
     ports of c_{b+1}, and keep c_a's block in the upper context.
   - **Why it is exact.** Side subtrees enter by their exact usual-limit port relations. The carry map of all top ports, including
     non-main identities, is preserved. The moved set has equal projections on every subset, so it is a bond.
   - **The moved target.** It is an own distinction of a covered copy at depth s + Π, and the wrapper offset is fixed.
2. **Counting.** A member must be counted at the one copy that holds it as its own, not at every block where it sits as a carried
   port. Read literally, one main port occupies every level, and the inequality fails: Codex built a 3-bond at depth 20 with m = 2.
   - **The corrected bound.** With n = d − δ and t occupied levels, n ≤ (m+1)t + m and t ≤ |W| − 2. This is slightly stronger than
     the note's d/(m+1) − 1.

**No sublinear growth was found.**
- **Global minima.** Two growers give 6, 7, 8, 9 at depths 7, 8, 10 and 12, and the wrapper gives 6, 6 at depths 7 and 8. These are
  global by the two-blank separation argument from CARRY-BOUND-R1.
- **Hand designs.** Square-number and exponentially sparse member levels, stalls, delays and side subtrees all fail, each for the
  reason the proof gives: a long empty stretch eventually appears and pumps to a bound.

**Constants.** m counts reachable pairs of a per-call product and a carry map, including the empty word.

| Family | m | Π = m! | Linear constant |
| --- | --- | --- | --- |
| `a43ab6412097` | 5 | 120 | 1/6 |
| `bc22e10bb149` | 3 | 6 | 1/4 |
| `e35d907e41c9` | 596 | 596! | 1/597 |
| `432127c418b0` (wrapper) | 29,359 | 29359! | 1/29,360 |

Eleven samples in all are in `codex/pumping_results.json`.

**Effectivity.** **Narrowing.**
- **What the proof gives.**
  - The monoid, the period and the constant are effective.
  - A long-gap witness at depth d₀ gives the threshold d₀ and the bound C = |W|. Any bond with |W| < d₀/(m+1) − 1 forces such a gap.
  - Boundedness per residue is semi-decidable.
- **What it does not give.** A decision procedure, a finite growth test, an advance bound on the onset, or ultimate periodicity of
  L. The pre-registration's "decided by a finite local state" is not proved.

**Known in kind.** **Not a block.** This is from memory, without a network check.
- **What is classical.** Pumping in a finite monoid; and tropical cyclicity gives eventual affine periodicity, but only once a problem
  is cast as additive costs, which bond size is not.
- **What is new.** The identity-sensitive factorisation and the allocation count.
- **Why the minimum matters.** For a maximum over words, sublinear growth is possible. Codex gives a distance automaton with √N
  growth. L is a minimum over targets.

## 2. Theorem R (the referee and Codex)

**The exception is exact in both directions, locally.**
- **Exhaustive check.** The 7 nonempty complement-closed projections on {p, x, z} inside NAE were tested, by the referee and by Codex
  separately. W contains a bond through p and x exactly when the exception fails, and exactly 2 of the 7 projections are
  exceptions.
- **Relation-free.** A CNF audit of all 9 exception families and 20 non-exception families (919 states, 1,996 readings) agrees.
- **Q1.** All 9 exception families have deletion-checked 3-bonds in every repeating phase.

**Narrowing:** the exception says when the triple W fails to give a bond. It is not a criterion for L > 3.

**The quantifier.** The theorem needs some eligible carried state with a surviving reading in every repeating phase.

| R's coverage of the window-bounded in-scope weight | Families of 5,067 | Weight of 5,129 |
| --- | --- | --- |
| stricter, every eligible state | 4,479 | 87.46% |
| correct, some state per phase | 4,484 | 87.56% |

- **The five extra families.** They resolve the study Codex's five quantifier ambiguities. 9 exception-only families remain, and 68
  capped cases are unknown, not 73.
- **The published 87.5%.** It is a valid lower bound. **Not a block:** report 87.6%.

## 3. Theorem R1 (Codex)

**The proof is sound**, and the syntax check keeps finite helper-call arguments.

**469 against 471.** 471 in-scope families are R1-covered on every residue, and 469 of them are in the 5,067 window-bounded
denominator. That is 469/5,129 = 9.14% of the bounded weight. The other two (`d5ac8dc038ae968e`, `ce083ff8262fab67`) are capped
undecided families that R1's syntax bounds anyway. **Not a block:** state both denominators.

## 4. Q3 (Codex)

**L(s) = 2 at depths 1 to 6 is confirmed** in both variants. The tie {a, u} gives projection {01, 10}, and both variants enforce
u ≠ a. The same two-member argument works at every depth. **Not a block.**

## 5. The five ambiguities (Codex)

| # | Judgment |
| --- | --- |
| 1 | Some carried state per phase. **Not a block.** |
| 2 | Exception-only means every eligible reading in every carried state is killed. This settles 5 cases. **Not a block.** |
| 3 | 90 is the window-stage count, and 83 the count after the path rescues. Label the stage. **Not a block.** |
| 4 | Keep the one capped family capped. Q2 is far below 90% either way. **Not a block.** |
| 5 | No predicate was given for "the counterexample's shape", so no census count follows. **Narrowing.** |

## 6. The converse, and the rest of the wording

### The syntactic converse is false

This is the Block. The family (Codex's, from `codex/growth_hand_read_exception_argument.md`):

    S(a, b, c), own x, w:  NAE(a, x, b), NAE(c, x, w), SELF(a, b, x)
    main(p, q, r), own e, f, g:  NAE(p, q, e), NAE(p, q, f), NAE(p, q, g), NAE(e, f, g), S(p, q, r)

**How it works.**
- **The wrapper.** It forces p ≠ q, with distinct arguments in every call.
- **The carried ports.** p and q are carried by identity to every copy, and read there by NAE(p, x_i, q) with x_i own.
- **The exception.** With p ≠ q that knot is always satisfied: z = q is tied opposite to p, and {p, x} is free.
- **What is left.** A chain NAE(r, x_0, w_0), NAE(x_0, x_1, w_1), ... with pendant w's.

**The bond.** L(d) = d + 2 at every absolute depth d ≥ 1, with witness {r, w_0, ..., w_{d−1}, x_{d−1}}.
- **Lower bound.** Leaving out any w_j erases its constraint and separates r from the target.
- **Computed.** Codex's direct search gives 3 to 8 at depths 1 to 6 in both variants. The referee's own brute force gives 3, 4, 5, 6
  at depths 1 to 4.

**The verdict.** The note's statements need to change:
- conclusion 7, "No family is known whose bond grows while a carried value is effectively read";
- the Answer, "the converse ... is open, with no known exception";
- the Reading, "keeps its top within reach exactly where a knot puts a carried value next to something of the deep copy's own".

All three fail for "read" as the note's Words define it, which is also CARRY-BOUND's sense of live. **Block** (on the converse as
stated).

### The effective converse is proved

The proof is the referee's.
1. On a residue, suppose that at infinitely many depths some carried value is read by a knot that avoids the exception.
2. Then Theorem R gives L ≤ 3 at those depths.
3. By the dichotomy, L is then bounded on that residue, since linear growth would contradict step 2.
4. So growth on a residue forces every reading at every large depth on it to be exceptional or absent.

**What follows.**
- **The open question is gone.** The converse is open in neither sense: false read syntactically, a theorem read effectively.
- **Next-steps direction #2 needs restating.** It searches for "a carried value read with the exception avoided yet unbounded", which
  this argument shows cannot exist.

**Narrowing.**

### The rest of the wording

1. **"Two speeds only" and "nothing grows slowly".** Write: "on each residue modulo a computable period, L is eventually bounded or
   has a positive linear lower bound". Residues may differ, and m can be very large, so the rate can be weak. **Narrowing.**
2. **"The dichotomy gives a finite growth test"** (direction #2's concreteness). It gives none; only semi-decision of boundedness.
   **Narrowing.**
3. **The proved and the frozen dichotomy.** The proved one is a post-registration generalisation that drops conditional
   rectangularity, and the note says so. Its "finite local state" decision clause is not proved. **Not a block:** keep the two
   distinct.
4. **Scope.** Everything concerns own targets of S copies reached through S calls. **Not a block.**

## Fixes for the thread

1. **Replace the open converse** with the two facts: the syntactic converse is false (this family), and the effective converse is
   proved (R + the dichotomy). Fix conclusion 7, the Answer and the Reading, and restate direction #2. **Block** (on the converse as
   stated).
2. **Write the two repairs into the dichotomy's proof:** the interfaces over the blocks c_{a+1}..c_b, and counting at the allocating
   copy. **Not a block.**
3. **Per residue.** Say "per residue, eventually bounded or a positive linear lower bound", say that the rate can be weak, and drop
   the finite growth test. **Narrowing.**
4. **R's coverage.** Report 87.6% under the some-state reading, with 87.5% as the stricter one; and 68 capped unknowns. **Not a
   block.**
5. **R's exception is local to W.** Say so. **Narrowing.**
6. **R1's two denominators** (469/5,067 bounded and 471 in scope). **Not a block.**
7. **The other wording.** Ambiguity 5 and the frozen-versus-proved note. **Narrowing / Not a block.**

## Files

- **Codex's work, in `codex/`.**
  - `codex_report.md`, `pumping_proof_audit.md` and `pumping_results.json`;
  - the `coverage_*` and `growth_*` scripts and data, including the new family `growth_hand_read_exception_*`;
  - `q3_*` and `referee_manifest.json`.
- **The referee's own check.** `referee_converse_check.py` and `.txt`.
- **Kept out of git.** `codex/coverage_results.jsonl` (16 MB) stays on disk; its hash is in `large_file_hashes.json`.
