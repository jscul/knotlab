Verdict: **Confirmed with fixes.**

P′ and the two-block bound survive independent recomputation. Existential
localisation survives with explicit proof repairs supplied here. There is
a **Block on the claimed necessity of middle members**: concrete residual
families have eventual bonds using only main and target allocations.

## 1. Localisation and actual bond locations

**Not a block — proof repairs required.** The step-by-step reconstruction is
[localisation_audit.md](localisation_audit.md). Its conclusions are:

- Allocating-copy occupancy gives at most C+1 member-free stretches. Counting
  a carried occurrence repeatedly would be wrong. Products must include the
  unoccupied source blocks, with the interfaces moved accordingly.
- With the empty prefix, K=m(Π+1) levels suffice for Π+1 equal typed states
  and two equal depth residues. Equality must preserve the relative product
  and **every input port's carry map**, including ancestor-own identities.
  The resulting equality of the entire selected relation preserves every
  subset projection and bond minimality.
- Restore depth using a **short stable-prefix loop** of length ell≤m, so
  ell divides Π=m!. An arbitrary deleted loop divisible by Π is insufficient
  to restore every required multiple of Π.
- In side subtrees, apply occupancy recursively: protect a level holding a
  member **or an off-path selected branch**. Otherwise a cut can delete a
  different member. Typed states keep the cut words legal. Charging these
  protected levels to distinct members gives C(m+1) from the branch anchor.
- B=Cm(Π+1) has no missing additive C. Use absolute depth s=n+delta,
  delta=0 for main=S and 1 for wrappers. The written argument directly needs
  s>max(N,H), where L≤C starts at N and H=(C+1)m(Π+1)+C. The supplied
  backward normalisation, retaining a short pumpable loop, proves the
  stronger advertised onset s>H.

**Narrowing — exact meaning of local.** Eventually L≤C on one Π-residue
implies that every s>H in that residue has **some least bond** of size≤C
with the stated root/target windows and side bounds. Its word and lower
allocated identities may change. B is computable **given C and the required
typed state count m**; C is not supplied by this theorem. The Answer's
existential bounded-window claim is defensible after these repairs;
“a computable number of levels” needs that qualification. At m≈29,000,
the factorial bound is also impractical. This adds a witness normal form;
positive semidecision already followed from the repaired dichotomy.
Decidability remains unproved.

The relation-free panel covers all **65** residual families, with **192
recorded cells**, chiefly absolute depths 3,4,6: **159 globally exact
size-three minima** and **27 exact prefix size-four minima** (one obtained
by combining a completed lower exclusion with an alternative witness).
Size four is not promoted to a global minimum. Actual IDs, allocation
depths, target-relative levels and side addresses are retained in the JSON.
For example, `b192b55035ef` has least value 3 with allocations [0,s−1,s]
at s=2,3,4,6; these are strictly intermediate allocations, near the target.
The chosen primary witnesses have no side members; this is not an exclusion
of other witnesses. See [middle_audit.md](middle_audit.md).

**Block — the 65 do not require strict-middle allocations.** Independent
complete finite-state certificates give:

| Residual family | Absolute threshold | All-phase bound | Allocation locations |
| --- | ---: | ---: | --- |
| `fea4933ecaf1` | 4 | 3, globally least | main and target only |
| `fd60333c5872` | 9 | 3 | main and target only |
| `5ceea39607cb` | 12 | 4 | main and target only |

For `fea4933ecaf1`, a depth-4 bond has IDs [1,8,22], allocated at [0,0,4].
Thus “neither condition on every residue” does not establish a third
mechanism. Small-depth interior positions do not refute the enormous B.

**Narrowing — some, not every, least bond.** A separate synthetic family
has m=6, Π=720, C=3, H=17,307. At s=17,308 it has a least three-member
bond with a member **23 levels below the target**, beyond C(m+1)=21,
and also a local least bond. Its raw CNF and all subset projections were
checked. This refutes universal localisation of least bonds, while leaving
the actual existential theorem intact. No depth was found where all least
bonds violate the repaired theorem.

## 2. P′, pinning, residues and hiding

**Not a block.** The P′ proof is correct: a minimal non-full subset of
shattered T∪D cannot lie entirely in either shattered side, so it meets
both and has size≤|T|+|D|. Coverage only enters the definition of L(s).

The census correctly asks for **some word state in each repeating Q phase**,
not every word. Periodic repetition then gives every sufficiently large
depth directly. Alternatively, infinitely many bounded-size witnesses on
**each relevant Π-residue** rule out that residue's linear arm by the
dichotomy. One successful subphase of an unspecified coarser residue is
insufficient. Wrapper absolute residues require the +1 shift.

Fresh reconstruction matches **757 families / 26,431 repeating word states /
1,045 phases**: all 632 growers, all 93 order families, and 32 identity
families. T1 has zero plain or bond-pinning violations. The advisor's
26-state hiding relation is correlated and has no x-containing bond;
all 255 nonempty complement-closed four-distinction relations also pass
the independent shattered-side/cross-bond equivalence check.

**Narrowing — flags versus word states.** Family/residue plain and bond
flags agree in the sample and in the supplied full-population flags. But
order family `aab77be157e5` has **24 plainly pinned versus 22 bond-pinned
word states** in its repeating 28-state Q set. The two hidden words have
220 joint states versus 8×28=224 marginal-product states and no cross
bond, confirmed by explicit CNF and all support projections. This is the
generic hiding phenomenon, not the advisor's literal five-variable
example. The inference “so hiding does not occur” must be withdrawn.
Details: [pinning_window_audit.md](pinning_window_audit.md).

## 3. The two-block projection

**Not a block.** The displayed projection is exact when the context retains
main's entire block, other calls have their exact usual limits, and actual
identities are merged. This includes main-own distinctions passed down as
arguments; forgetting that identity gives an incorrect window.

**Narrowing — start convention.** For main=S, depth zero retains one copy,
not two. For nonempty w=i₁…iₛ, use the call-specific whole-main Start′ᵢ₁
followed by Rᵢ₂…Rᵢₛ. A wrapper uses a direct-entry start followed by s
factors and has absolute depth s+1. The proof's generic composition/context
sentence needs this qualification; the producer REPORT acknowledges it.

All **nine** new bounds independently reproduce, each with **U₂≤4** on
every eventual phase. All nine are wrappers; certificate thresholds range
from absolute depth 4 to 8. The lane report lists every identifier, period
and threshold. Validation includes **45 raw-CNF bonds** across early depths
and two complete eventual periods, **18 explicit branching unfoldings**,
and **778,752 assignment comparisons**, plus wrong-identity and wrong-start
controls. These establish upper bounds, not exact global L=4. The official
30-family gate was not reproduced in full by this review.

## 4. Counts and certificate admission

**Narrowing — the denominator and two unavailable flags.** The independent
data recount gives:

| CARRY admission policy | Bounded | Growing | Undecided |
| --- | ---: | ---: | ---: |
| Strict complete rows | 5,072 | 632 | 85 |
| Advertised primary path admissions | 5,074 | 632 | 83 |
| Every valid primary upper certificate | 5,076 | 632 | 81 |
| After TOP's nine new two-block certificates | **5,085** | **632** | **72** |

The split 4,484+523+65=5,072 is exactly the strict population. In the
advertised 5,074, `b47bcba2eb6c` and `530dbea3fe7b` have admitted path upper
certificates but **unavailable** R/pinning flags. They must be a fourth
category, not counted among known negatives. READ-R1's 4,484/5,067 used
only the original window-bounded denominator; the five complete path
additions do not change its numerator. All **5,717** earlier complete
referee R flags match TOP.

**Not a block — the two R families.** `432127c418b0` and `981fdc202826`
have independently verified surviving readings on all 12 and 4 Q phases,
respectively. R therefore bounds them (the dichotomy is unnecessary for
this stronger every-phase certificate). They already had complete CARRY
window bound-3 certificates, from absolute thresholds 20 and 15. Their
admission adopts CARRY's **5,076 full-certificate count**; it supplies an
alternative proof, not two previously unknown mathematical bounds. From
the advertised frozen classification, nine new certificates plus these
two admissions explain the eleven status changes. Final draw weights are
5,147 / 634 / 72, summing to the in-scope weight 5,853.

Other requested counts reproduce: **588=93+9+486**; the 486 others are
477 I +4 X +5 T. The old R/pinning overlap is **3,515** (3,517 after the
two full-certificate admissions). The **523** pinning-only families are
**436 I +78 O +4 X +5 T**. All 93 O flags were independently recomputed:
78 pass every phase, **15 fail T2**; their complete identifiers are in
`counts_results.json` and `pinning_window_results_summary.json`.

## 5. Wording fixes

- **Narrowing:** replace “another 10%, with nothing carried, as in the order
  families” with the actual pinning-only composition. Most are identity
  families, and pinning does not require the absence of carrying.
- **Narrowing:** using the advertised old denominator, the family shares are
  **88.37% / 10.31% / 1.28%**, plus 0.039% unavailable. Draw-weight shares
  are **87.44% / 11.25% / 1.27%**, plus 0.039% unavailable. Do not mix them.
- **Block for the mechanism claim:** replace “their bonds need/use middle
  members” as a classification with **“65 families not explained on every
  residue by the two tested sufficient conditions.”** The counterexamples
  above invalidate the claimed necessity.
- **Narrowing:** “information, not carrying” remains interpretation, not a
  characterised invariant. A bounded bond can involve main's own allocation
  while main ports and target-own distinctions are uncorrelated. Also,
  “false in both directions” must distinguish raw syntactic reading from
  effective R: effective R's sufficient direction survives.
- **Narrowing:** every L(s), growth claim and population count here concerns
  **covered S targets reached through S calls**, with admitted direct wrapper
  entries. No classification of all recursive target types follows.

## Files written and validation limits

Everything written is in this directory. No forbidden TOP study Python was
opened/imported, no network was used, and no Git mutation, lifecycle edit
or publication was made. Earlier permitted referee code was reused,
including its disclosed transitive exact SAT-search helper. Computations
used one solver process per lane, at most three lanes; address-space caps
totalled below 10 GB. No command reached 15 minutes. The work finished
within 75 minutes.

The deep `2cbac5d97e3f` cell was interrupted in two owned runs after soft
timeouts overran inside solver/search work. All completed records survive;
four primary timeouts, two copy-count skips, that interrupted cell and two
unstarted deep cells remain explicit. No resource limit is negative
mathematical evidence. See `middle_interruption.json` and `middle_summary.json`.

- Main report: `codex_report.md`; supporting reports: `localisation_audit.md`,
  `pinning_window_audit.md`, `middle_audit.md`.
- Scripts: `counts_audit.py`, `localisation_checks.py`, `middle_bonds.py`,
  `middle_bonds_soft_timeout.py` (preserved original version),
  `middle_word_audit.py`, `middle_summarize.py`, `pinning_window_core.py`,
  `pinning_window_audit.py`, `referee_validate.py`.
- Counts/proof data: `counts_results.json`, `localisation_checks.json`.
- Bond data: `middle_inputs.json`, `middle_controls.json`,
  `middle_solver_controls.json`, `middle_interruption.json`,
  `middle_smoke.jsonl`, `middle_panel.jsonl`, `middle_panel2.jsonl` through
  `middle_panel5.jsonl`, `middle_remaining.jsonl`,
  `middle_remaining_small.jsonl`, `middle_word_results.jsonl`, their
  accompanying `*_inputs.json`, and `middle_summary.json`.
- Pinning/window data: `pinning_window_results_{controls,growers,orders,
  identities,hiding,twoblock,toponly,Rrescues,summary}.json`, plus the
  `{growers,orders,identities,twoblock}.jsonl` records.
- Final file inventory, hashes and artifact checks: `referee_validation.json`.

The mathematical reconstructions are independent same-task AI referee work,
not external replication or formal-kernel proofs. Computational replay is
V2 with permitted older referee algorithms; the fresh finite localisation
controls are V1. Finite checks supplement the symbolic arguments.
