# Referee report CARRY-BOUND-R1 (Codex-assisted, fresh code)

**Verdict: Confirmed with fixes. No Block.**

**What holds.**
- **Lemma G.** It survives a direct attempt to break it, including a carried value that is constrained above and unread below.
- **Lemma W.** It is exact, with identities merged before members are counted.
- **The counts and shares.** All 632 growth certificates, the scope flags, and the 58.0 / 39.6 / 2.4 split reproduce.
- **The two undecided-by-rule families.** The frozen rule handles them correctly.
- **The two logged corrections.** Their verdicts are right.

**The fixes.**
- **The 6-member search cap.** A window reading of ">6" was taken as "unbounded", but Codex found bonds of size 7 in 8 sampled
  states.
- **Wording.** The bound "at most four" and "every depth" are stated past their evidence.
- **The wrapper shift.** It is missing from the note's growth formula.
- **The cap's other effects.** These are Narrowings in the note's wording, not in its results.

**How the work was split.** The background referee thread owns the verdict.
- **The referee.**
  - Checked the objects gate, which returns `ok`.
  - Checked the isolation boundary: the run log shows no reads of the study's Python.
  - Brute-forced the two-blank separation step of Codex's own closure argument. Two consecutive blanks let all 16 boundary assignments
    extend; one blank does not.
  - Read Lemma G's written proof against Codex's objection, and checked the note's wording line by line.
- **Codex.** The Codex command-line tool, at the owner's choice of model and effort, recomputed from fresh code within the
  75-minute budget.
- **Advisor.** The advisor model was not consulted.

## 1. Lemma G (Codex; the referee on the proof text)

**Global exact minima in 8 of the smallest growers.** For the five with main S and three with a wrapper main, Codex found the
following, with no relation code and members anywhere, at depths 1 to 6.

| Main | L(1), ..., L(6) | Lemma G's lower bound |
| --- | --- | --- |
| S (r = 4) | 3, 4, 4, 5, 5, 6 | 2, 2, 2, 3, 3, 3 |
| wrapper (r = 4) | 3, 3, 4, 4, 5, 5 | 2, 2, 2, 2, 3, 3 |

**Why the minima are global, not only finite-prefix.**
- **The setting.** These families reduce to consecutive-triple NAE chains that meet only at main's ports.
- **The separation step.** Two consecutive unselected own variables separate a chain's projection.
- **The consequence.** A bond of size k containing a main port has every member at depth at most 2k − 3, plus one for a wrapper, so
  the searched prefix contains every smaller bond.
- **Independent check.** The referee checked the separation step by brute force: all 16 boundary assignments extend across two
  blanks; across one blank they do not, which matches Codex's failing control.

**Wider tests.** Codex ran 14 growers in all, including r = 1, 2, 3 and two-call branching.
- **The cells.** 119 of 126 cells are exact finite-prefix minima, and 7 timeouts are preserved. Every positive bond was rechecked
  with a second SAT solver.
- **The result.** No cell violates G.
- **The certificates.** Fresh per-call relations and least liveness reproduce all 632 certificates: r = 1 in 318, 2 in 163, 3 in 55
  and 4 in 96.

**The proof text has a gap that can be filled.**
- **The gap.** The pre-registration argues from "a distinction that lies in no constraint". But a dead position's value need not be
  globally free: a wrapper above can constrain it in main.
- **The sound argument.**
  1. A dead position is unread in its copy's whole subtree.
  2. Keep the upper constraints and values.
  3. Delete only the unread occurrences from the stretch's interface. The lower formula does not depend on them.
  4. Rectangularity then factors the bond's projection into upper and lower parts, which contradicts minimality.
- **Controls.** The matched constrained-above control passes. Freeing the upper value globally is rejected, as it should be.

**Not a block:** write this lifting step into the proof.

## 2. Lemma W (Codex)

**The sample.** 15 bounded families plus one frozen-undecided case. It covers bounds 2, 3 and 4, main S and wrapper mains, the
order label, and all five tie families.
- **The checks.** 21,805 state values and every first-repeat parameter reproduce, with 191 concrete SAT bond checks and 63,872
  whole-window assignment comparisons.
- **The direct readings.** These cover lengths 1, 2, 3 and 6 and every residue of the repeating part, on both selected-path and
  all-S-copy unfoldings.

**Why W is exact.**
- **The interface.** The target subtree meets its context only through its ports, and decreasing usual limits are exact infinite
  projections.
- **Identity merging.** Root and target identities must be merged before members are counted. A repeated-port control rejects a
  spurious two-position "bond", which after merging is one free identity.

**Not a block.**

**The cap.** ">6" means "no bond of at most six found", not unbounded.
- **The evidence.** Eight sampled states recorded ">6" have directly verified bonds of size 7. One is `7aac0c3bf98b` on the word
  [0,0,1,1,0,0]: its only forbidden assignments are a complementary pair, and every deletion is shattered.
- **What survives.** These families stay bounded through other words, so the positive bounds stand.
- **What changes.** The note's "the window leaves unbounded" (conclusion 4) is a censored reading. **Narrowing.**

**The threshold.** A state set repeating at word length μ with period p proves the bound for every word length n ≥ μ.
- **Absolute depth.** It is d = n for main S, and d = n + 1 for a wrapper.
- **Sufficient, not earliest.** The tie family `3e479a23fc49` has μ = 36 and p = 4, but its bound 2 already holds from n = 5.
- **The note's "at most 36 levels".** It is consistent with the data.

**Narrowing:** give the threshold as μ per family with the wrapper shift, and call it sufficient, not earliest.

## 3. Scope (Codex)

**The flags.** The structural predicates match all 5,964 scope flags and the 657 earlier inventory rows.
- **In scope.** 5,789 families (weight 5,853).
- **Excluded, 175 families.**
  - 167 have only other recursive own distinctions.
  - 4 have only a delayed S.
  - 4 have both.
- **Reachability.** It starts from main and from S, which is CENSUS-FORGET-R1's covered-target scope.

**The split reproduces.**

| Census first-ray growth | Draw weight | Share of 13,279 |
| --- | --- | --- |
| grows | 7,063 + 634 = 7,697 | 57.96% |
| bounded | 5,129 window + 7 path + 129 out-of-scope upper bounds = 5,265 | 39.65% |
| undecided | 83 + 46 + 188 = 317 | 2.39% |

- **Out-of-scope families.** Counting them as bounded is valid, because an upper bound to a covered target bounds L. The reverse
  inference (a lower bound) would not be.
- **The weights.** They are inherited from the permitted digest and the earlier referee, then independently summed.

**Not a block.**

## 4. The two complete-window families left undecided (Codex)

| Family | Main | μ | p | Window bound | Absolute threshold |
| --- | --- | --- | --- | --- | --- |
| `432127c418b0` | wrapper | 19 | 12 | 3 | 20 |
| `981fdc202826` | wrapper | 14 | 4 | 3 | 15 |

**The frozen rule is applied correctly.** It counts a capped length-set family as undecided in P1 to P4 and not growing in P5.
Their upper certificates are still valid mathematics. **Not a block.**

**The path rescues need a separate statement.**
- **The case.** Two of the seven path rescues (`b47bcba2eb6c`, `530dbea3fe7b`) have exact bound-4 certificates from depth 6, but
  inherited caps and a timed-out further row.
- **How the counts move.**
  - A strict complete-row reading gives 5,072 bounded, 632 growing and 85 undecided.
  - The advertised policy gives 5,074 / 632 / 83.
  - Admitting every valid upper certificate gives 5,076 / 632 / 81.
- **The headline is unchanged.**

**Narrowing:** say that completed path certificates are admitted separately from the frozen window classification.

## 5. The two logged corrections (Codex)

- **TIE-CYCLE's carrying reading** (Narrowing): the verdict is right. Carrying by identity alone does not bound the bond, since all
  632 growers carry only unread values. The surviving reading needs a read value, with a certificate. The converse for arbitrary
  families is still a proposed theorem.
- **The pre-registration's fixed point in G** (Not a block): the verdict is right for the amended study.
  - **The defect.** Least-dead iteration started empty cannot find a self-carried unread position.
  - **The repair.** The addendum replaces it with least liveness, seeded by knots, and takes the complement.
  - **The timing.** The repair came after the disclosed 20-case smoke and before the full run, as the addendum says.

## 6. Wording (Codex; checked against `carry_bound.md` by the referee)

1. **"Every depth".** Answer, line 47, and Reading, line 61, should say "every sufficiently large depth", with μ and the wrapper
   shift. **Narrowing.**
2. **"At most four".** Lines 47 and 63 should say this only for window certificates.
   - The path rescues `ad4255ad1474` and `992270e6afcd` give bounds of 5. That does not show that L ever exceeds 4.
   - The order label's 55 / 36 split counts certificate sizes of the 91 window cases (56 and 37 with the two path additions), not
     exact values of L.

   **Narrowing.**
3. **Conclusion 6's 2 + ⌊s/r⌋.** It needs the wrapper shift, 2 + ⌊(d − 1)/r⌋, for its 101 wrapper families, as the
   pre-registration already states. **Narrowing.**
4. **"5,964 exact window decisions"** (Review, line 93). Say 5,964 attempted, of which 72 are incomplete, with the six-member search
   cap. **Narrowing.**
5. **The population (line 27).** Describe it as "non-forgetting or capped first-ray growers". The 66 inherited census caps do not
   establish a non-rectangular idempotent. **Narrowing.**
6. **"Proved per family".** This is defensible for a checked finite certificate together with the symbolic lemma (W or G), which
   together give every sufficiently large depth. The shares are computed census facts, and the direct search's finite readings never
   prove growth. **Not a block.**

## Fixes for the thread

1. **Write Lemma G's lifting step** (section 1). **Not a block.**
2. **Read ">6" as no bond of at most six found** in conclusion 4 and wherever the window "leaves unbounded". **Narrowing.**
3. **Give the threshold** as μ per family, with the wrapper shift, called sufficient. **Narrowing.**
4. **Separate path-certificate admission** from the frozen window classification, giving the 5,072 / 5,074 / 5,076 alternatives.
   **Narrowing.**
5. **Fix the wording** in items 1 to 5 of section 6. **Narrowing.**

## Files

`codex/`: Codex's report (`codex_report.md`), proof review (`grow_proof_review.md`), and the window, scope and grow audits with their
scripts and data. `referee_manifest.json` holds the hashes. `codex/window_inputs.json` (6 MB) stays on disk; it can be regenerated by
`codex/window_prepare.py`, and its hash is in `large_file_hashes.json`.
