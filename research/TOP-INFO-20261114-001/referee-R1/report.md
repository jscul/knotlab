# Referee report TOP-INFO-R1 (Codex-assisted, fresh code)

**Verdict: Confirmed with fixes, with one Block on the "middle members" mechanism.**

**What stands.**
- **The three theorems.** Theorem P′, the two-block window bound and localisation stand. Localisation needs proof repairs and an
  exact, weaker meaning of "local".
- **The counts.** They reproduce once the denominator is fixed.

**The Block.** The 65 families that neither condition explains are not shown to need members between the top and the target.
- **The counterexamples.** At least three of them (`fea4933ecaf1`, `fd60333c5872`, `5ceea39607cb`) have eventual bonds made only
  of main's block and the target copy.
- **The referee's check.** I confirmed one by my own unfolding.

**How the work was split.** The background referee thread owns the verdict.
- **The referee.**
  - Checked the objects gate, which returns `ok`.
  - Checked the isolation boundary: the run log names the study's Python only inside the study Codex's REPORT.md text.
  - Brute-forced the advisor's hiding relation.
  - Traced the 2-family gap in the split.
  - Independently recomputed the Block's main counterexample (`referee_toponly_check.py`), unfolding `fea4933ecaf1` from its census
    key and solving with SAT.
- **Codex.** The Codex command-line tool, at the owner's choice of model and effort, recomputed from fresh code in about 40 minutes.
- **Advisor.** The advisor model was not consulted.

## 1. Localisation (Codex; the referee on the meaning)

The proof's steps hold with these repairs, none of which changes the statement's form (`codex/localisation_audit.md`).

**Not a block:** write these into the proof.
- **Counting.** Members are counted at their allocating copy, which gives at most C + 1 member-free stretches. The stretch products
  run over the unoccupied blocks, with the interfaces moved accordingly.
- **State equality.** It must keep the relative product and the carry map of every input port, including identities owned by an
  ancestor.
- **Restoring depth.** Use a short loop of length ℓ ≤ m that can be pumped, so that ℓ divides Π = m!. A deleted loop that is only
  divisible by Π is not enough.
- **Side subtrees.** Occupancy must be applied recursively: a level is protected when it holds a member or an off-path branch that
  holds one. Otherwise a cut can delete another member, which was the referee's concern. With that, the bound C·(m+1) from the
  branch point holds.
- **The onset.** As written, the argument needs s > max(N, H), where N is where L ≤ C starts and H = (C+1)·m·(Π+1) + C. A backward
  normalisation, keeping a short loop that can be pumped, gives the advertised s > H. The bound B = C·m·(Π+1) is right.

**"Local", exactly.** If L ≤ C eventually on a residue, then at every s > H on it **some** least bond has:
- its occupied levels within B of the root or of the target;
- its side members within C·(m+1) levels of where their subtree branches off.

**It is not every least bond.** A synthetic family with m = 6, Π = 720, C = 3 and H = 17,307 has, at s = 17,308, one least bond with
a member 23 levels below the target, beyond C·(m+1) = 21, and also a local one. The raw CNF and every subset projection were checked.

**What the bound costs and adds.** B is computable only **given C**, which the theorem does not supply. With m about 29,000 it is
impractical. The lemma adds a normal form for witnesses: semi-decision of boundedness already followed from the dichotomy, per
READ-RULE-R1.

**Narrowing:** "a computable number of levels" needs "given the bound C". The Answer's "every bounded case shows up in a bounded
window at the top and at the target" holds for **some** least bond, with a window that depends on C.

## 2. Theorem P′ and pinning (Codex; the referee on the hiding relation)

**P′ is correct.** A minimal non-full subset of T ∪ D cannot lie in either shattered side, so it meets both. **Not a block.**

**The census quantifier.** It asks for some word state in each repeating phase, which gives every large depth. The wrapper's
absolute residues take the +1 shift. **Not a block.**

**The recount.** The fresh reconstruction matches 757 families: all 632 growers, all 93 order families and 32 identity families, with
26,431 word states. T1 has no violation.

**The hiding relation.**
- **The advisor's relation.** Verified by the referee and by Codex: correlated, no bond holding x, and not bond-pinned. Codex also
  checked the equivalence on all 255 complement-closed four-distinction relations.
- **Hiding does occur.** At the level of word states, order family `aab77be157e5` has 24 plainly pinned but only 22 bond-pinned
  states. Its two hidden words have 220 joint states against 224 for the product of the marginals, and no cross bond, confirmed by
  CNF.
- **What still holds.** The family and residue flags agree.

**Narrowing:** withdraw "so the advisor's hiding relation does not occur"; say hiding occurs in word states but does not change any
family's flag.

## 3. The two-block window (Codex)

**It is exact**, provided three conditions hold:
- main's whole block is kept;
- other calls take their exact usual limits;
- identities are merged, including main's own distinctions passed down as arguments. Dropping that merge gives a wrong window.

**Not a block.**

**The start convention.** For main = S, depth 0 keeps one copy, and a nonempty word starts with the call-specific Start′ followed by
the remaining factors. A wrapper starts directly and adds one level. **Narrowing** (the proof's generic sentence).

**The 9 new bounds.** All 9 reproduce, all of them wrapper families with U₂ ≤ 4 on every eventual phase and thresholds 4 to 8.
- **The checks.** 45 raw-CNF bonds, 18 explicit branching unfoldings and 778,752 assignment comparisons, with wrong-identity and
  wrong-start controls.
- **The limit.** These are upper bounds, not exact L = 4. The study's 30-family brute-force gate was not reproduced.

## 4. The counts (Codex; the referee traced the gap)

| CARRY-BOUND admission policy | Bounded | Growing | Undecided |
| --- | --- | --- | --- |
| strict complete rows | 5,072 | 632 | 85 |
| advertised (with the path rescues) | 5,074 | 632 | 83 |
| every valid upper certificate | 5,076 | 632 | 81 |
| after TOP-INFO's 9 two-block certificates | **5,085** | **632** | **72** |

**The 2-family gap.** 4,484 + 523 + 65 = 5,072, which is exactly the strict population. In the advertised 5,074, two path-rescued
families (`b47bcba2eb6c`, `530dbea3fe7b`) have unavailable R and pinning flags because of inherited caps. **Narrowing:** count them as
a fourth category, "unavailable".

**The two R-bounded families** (`432127c418b0`, `981fdc202826`).
- **The certificate.** Their surviving readings are verified on all 12 and 4 phases, so R bounds them directly; the dichotomy is not
  needed.
- **What it changes.** They already had complete CARRY-BOUND window certificates of 3, so this adopts CARRY-BOUND's full-admission
  count of 5,076. It gives a second proof, not new bounds.
- **The final weights.** 5,147 / 634 / 72, which sum to 5,853. **Not a block.**

**The rest reproduces.**
- 588 = 93 + 9 + 486. The 486 are 477 identity, 4 X and 5 T.
- The overlap of R and bond-pinning is 3,515.
- **The 523 bond-pinned without R** are 436 identity, 78 order, 4 X and 5 T families.
- The 15 order families failing T2 are listed in `codex/counts_results.json`.

## 5. The Block: "middle members"

**What the note says.** Conclusion 3: "Their bonds use members between the top and the target". The Answer: "In 1.3% the bond needs
members between the top and the target".

**The counterexamples.** Codex's complete finite-state certificates give bonds using only main's block and the target copy.

| Family | Absolute threshold | Bound on every phase | Allocations |
| --- | --- | --- | --- |
| `fea4933ecaf1` (order) | 4 | 3, globally least | main and target only |
| `fd60333c5872` | 9 | 3 | main and target only |
| `5ceea39607cb` (order) | 12 | 4 | main and target only |

**The referee's check of `fea4933ecaf1`.** I unfolded it from its census key to truncation depths 4, 6, 8 and 10, with unconstrained
leaves: a relaxation whose projections decrease to the usual limit. I then took the target copy on S-call word [1,1,1] at absolute
depth 4.
- **The bond.** {main port 1, main's own distinction 8, the target's own distinction at position 4 (or 6)} is non-shattered, with 6
  of 8 states, and every pair is full, at every truncation depth.
- **Why P′ misses it.** One top member is main's **own** distinction, the argument it passes to S, not a port.

**What follows.**
- **The 65 are a residue, not a mechanism.** They are the families the two tested conditions do not explain on every residue.
- **What to state instead.** "65 families not explained on every residue by reading or bond-pinning". Interior members appear in
  some least bonds at small depths (for example `b192b55035ef`, near the target), which says nothing against localisation's
  enormous B.
- **A natural next condition.** P′ with T drawn from main's whole block, which the two-block window already contains, would cover at
  least these three.

**Block** (on the mechanism claim).

## 6. Wording (Codex; checked against `top_info.md` by the referee)

1. **"The rule is false, in both directions"** (conclusion 1).
   - **For the rule as asked**, with readings outside the exception, only one direction fails: bounded without an effective reading
     (588 families). The other direction is the theorem stated in the same cell.
   - **The growing family** reads only inside the exception, so it refutes the syntactic rule, not this one.

   **Narrowing.**
2. **"Pinning ... with nothing carried, as in the order families (another 10%)".** The 523 are mostly identity families (436), and
   pinning does not require nothing to be carried. **Narrowing.**
3. **The shares.** Give families or weight, not both mixed.
   - **By family:** 88.37% / 10.31% / 1.28%, plus 0.04% unavailable.
   - **By weight:** 87.44% / 11.25% / 1.27%, plus 0.04% unavailable.

   **Narrowing.**
4. **"Information, not carrying".** It stays interpretation. A bounded bond can use main's own distinction while main's ports and the
   target's own distinctions are uncorrelated (section 5). **Narrowing.**
5. **Scope.** Everything concerns covered targets: own distinctions of S copies reached through S calls. **Not a block.**

## Fixes for the thread

1. **Replace "middle members"** by "65 families not explained on every residue by reading or bond-pinning", citing the three top-only
   families. Consider a top-block form of P′. **Block** (on the mechanism claim).
2. **Write the localisation repairs** (section 1) into the proof. **Not a block.**
3. **State "local" exactly:** some least bond, a window computable given C, and not every least bond. **Narrowing.**
4. **Withdraw "hiding does not occur"**: it occurs in word states without changing family flags. **Narrowing.**
5. **The two-block start convention** (section 3). **Narrowing.**
6. **The denominator.** 4,484 + 523 + 65 = 5,072 (strict), with 2 unavailable in the advertised 5,074; the 2 R families adopt
   CARRY-BOUND's 5,076; final 5,085 / 632 / 72. **Narrowing.**
7. **The wording in section 6, items 1 to 4.** **Narrowing.**

## Files

- **Codex's work, in `codex/`.**
  - `codex_report.md`, `localisation_audit.md`, `pinning_window_audit.md` and `middle_audit.md`;
  - the scripts and data listed there, with `referee_validation.json` for the hashes.
- **The referee's own check.** `referee_toponly_check.py` and `.txt`.
