Verdict: **Confirmed with fixes**.

Lemma G survived the attempted falsification, including values constrained
above and unread below. Lemma W's projection argument is sound with identity
merges. The reported scope and census arithmetic reproduce. Required fixes
concern censored window searches, eventual-depth wording, and the distinction
between frozen classifications and mathematical certificates. **No Block
found.** This is an independent implementation by AI referees, not human
review or external replication.

## 1. Lemma G: direct attempts to break it

I selected the eight smallest growers by S-block size, call count, definition
count, r and key, then added r=1,2,3 and branching cases. The search reuses only
the permitted earlier referee's exact SAT bond search; the unfolding and
limit computation are fresh. No per-call relation, composition, semigroup,
window or path code supplies a direct-search answer.

The following are **global exact minima**, with support members anywhere,
at absolute depths d=1,...,6:

| Family SHA prefix | Main | r | L(1),...,L(6) | Claimed lower bounds |
| --- | --- | ---: | --- | --- |
| `a43ab6412097` | S | 4 | 3,4,4,5,5,6 | 2,2,2,3,3,3 |
| `b3b48fb04a11` | S | 4 | 3,4,4,5,5,6 | 2,2,2,3,3,3 |
| `46540117e841` | S | 4 | 3,4,4,5,5,6 | 2,2,2,3,3,3 |
| `7cab1d17e3b9` | S | 4 | 3,4,4,5,5,6 | 2,2,2,3,3,3 |
| `c75c4e97f3a2` | S | 4 | 3,4,4,5,5,6 | 2,2,2,3,3,3 |
| `4dc882a6a1d7` | wrapper | 4 | 3,3,4,4,5,5 | 2,2,2,2,3,3 |
| `a430c16bc410` | wrapper | 4 | 3,3,4,4,5,5 | 2,2,2,2,3,3 |
| `83a64950aded` | wrapper | 4 | 3,3,4,4,5,5 | 2,2,2,2,3,3 |

These families reduce to consecutive-triple NAE chains meeting only at
main's ports. Two consecutive unselected own variables separate a chain's
projection: all 16 assignments to the four boundary variables extend across
the two blanks. A bond of size k containing a main port therefore has every
member at depth at most 2k−3, plus one for wrappers. Every hypothetical bond
smaller than the displayed SAT witness lies inside the searched prefix.
This independent support-radius argument closes the finite-search limitation
for all 48 cells **without using Lemma G or its r**. A one-blank control fails
as required. Detailed proof and machine shape checks are in
`grow_proof_review.md` and `grow_global_exact.json`.

Additional relation-free searches covered 14 growers altogether, including
r=1,2,3 and two-call branching. There were 126 cells: 119 exact finite-prefix
minima and seven preserved timeouts. All 119 positive bonds were reverified
with a second SAT solver, including non-shattering and every deletion's
shattering. No completed cell violated G. The additional families' finite
minima are not promoted to global minima. Larger prefixes through d+6
reproduced every displayed minimum.

Separately, fresh SAT-derived per-call relations and least-liveness iteration
reproduced **all 632** live quotients and their least rectangular lengths:
318 at r=1, 163 at r=2, 55 at r=3, 96 at r=4.

**Not a block — make the deletion proof explicit.** A dead *position* is
unread in that copy's entire subtree; the value occupying it need not be
globally free. The wrappers above constrain such values in main. Keep those
upper constraints and values in the context, deleting only unread occurrences
from the stretch's interface. The lower formula does not depend on them.
Rectangularity then gives a product of the upper and lower projections,
contradicting bond minimality across a member-free stretch. This lifting and
factorisation step is sound; the opening observation about a globally free
variable does not by itself justify it. The matched constrained-above control
passes, while globally freeing the upper variable is rejected.

## 2. Lemma W: sample certificates, thresholds and merges

The independent panel has 15 final bounded families plus one complete-window
but frozen-undecided case. It covers bounds 2,3,4, main=S and wrappers, I/O
labels and all five T families. All 21,805 sampled state values and exact
first-repeat parameters reproduce. There are 191 concrete SAT bond checks
and 63,872 whole-window assignment comparisons, including the size-7 checks
below. See
`window_audit.md` for the family-by-family bounds, preperiods, periods and
absolute thresholds, and `window_results.jsonl` for explicit supports,
words and SAT checks. Direct checks include lengths 1,2,3,6 and every residue
of the first repeating part; both selected-path and all-S-copy unfoldings
are used. Fresh state-set iteration agrees with the certificates.

W is exact because the target subtree meets its context only through its
ports, and decreasing usual limits are exact infinite-subtree projections.
Composition gives the context; attaching the target block and child limits
gives precisely the window projection. Merge root/target and target/target
identities before counting support members. The repeated-port negative
control rejects the spurious two-position equality bond: after merging it
is one free identity. Semantic equality between distinct variables must
remain a possible genuine size-2 bond.

**Narrowing — “>6” is not infinity or exact uncensored g.** This is a concrete
defect in the prose, not just a hypothetical limitation. Eight sampled
states recorded “>6” have directly verified size-7 bonds. For example,
`7aac0c3bf98b`, SELF-label word `[0,0,1,1,0,0]`, has
J=`0x7ffffffffffffffe`, partition `[0,1,2,3,4,5]`, and bond labels
`[0,1,2,3,5,6,7]`. Its only forbidden assignments are 31 and 96, with bits
ordered by those labels; every deletion is shattered. These families still
have U≤3 or U≤4 through other words. Thus positive bounds survive, while
“the window leaves unbounded” must become “the window finds no bond of size
at most six”. See `window_censor_probe.json`.

**Narrowing — specify the threshold.** A repeated state set at word length
μ with period p proves coverage for every word length n≥μ, all p residues
included. Absolute target depth is d=n for main=S and d=n+1 for wrappers.
This is a sufficient certificate threshold, not necessarily the earliest
one: tie `3e479a23fc49` has μ=36, p=4, while its bound 2 already holds from
n=5. The reported maximum sufficient absolute threshold 36 is consistent
with the data; the maximizing family is not a wrapper.

## 3. Scope and the 58.0 / 39.6 / 2.4 split

The independent structural predicates match **all 5,964 scope flags** and
all 657 earlier inventory rows. There are **5,789 in-scope families**, weight
5,853. The 175 excluded families comprise 167 with other recursive own
distinctions only, four with delayed S only, and four with both. Reachability
must start from main **and** S. Covered targets are own distinctions of S
copies reached through S calls; the lower bound does not cover other types
or delayed ancestry.

| Census first-ray-growth outcome | Draw weight | Share of 13,279 |
| --- | ---: | ---: |
| Growing | 7,063 earlier + 634 here = 7,697 | 57.9637% |
| Bounded | 5,129 in-scope window + 7 path + 129 excluded upper certificates = 5,265 | 39.6491% |
| Undecided | 83 in scope + 46 excluded here + 188 earlier exclusions = 317 | 2.3872% |

**Not a block.** This reproduces 58.0/39.6/2.4. An upper bound to a covered
target remains an upper bound when more targets are allowed; the reverse
lower-bound inference fails. The split is a weighted census fact, not a
theorem about all families. Raw draw multiplicities were outside the assigned
inputs: weights are inherited from the permitted digest and earlier referee,
then independently summed and reconciled. The seven path admissions require
the classification distinction in point 4.

## 4. Two complete-window families left undecided by rule

| Family SHA prefix | Main | μ | p | Window bound | Absolute certificate threshold |
| --- | --- | ---: | ---: | ---: | ---: |
| `432127c418b0` | wrapper | 19 | 12 | 3 | 20 |
| `981fdc202826` | wrapper | 14 | 4 | 3 | 15 |

Both have inherited census length-set caps and a capped product search.
**Not a block:** the frozen rule explicitly counts a capped length-set family
as undecided in P1–P4 and not growing in P5. Their conservative trial
classification is correct. A failed growth test does not invalidate their
complete mathematical upper certificates.

**Narrowing — separate trial classifications from later certificate
admission.** The advertised seven path rescues include `b47bcba2eb6c` and
`530dbea3fe7b`, which retain primary exact bound-4 certificates from depth 6
but have inherited caps and incomplete further analysis; the first whole
row is marked timeout. P1–P5 are window-only and unaffected. The final report
must explicitly say it admits completed primary path certificates separately
from the frozen window classification. A strict complete-row reading gives
5,072 bounded / 632 growing / 85 undecided in scope; the advertised rescue
policy gives 5,074 / 632 / 83. Counting every valid primary upper certificate,
including both capped complete windows, would instead give 5,076 / 632 / 81.
The 58.0/39.6/2.4 rounded headline is unchanged under these alternatives.
This audit inspects the seven path records, not the path-DP implementation.

## 5. The two reported corrections

**Narrowing — TIE-CYCLE's carrying reading:** correct. Carrying by identity
alone does not bound the bond. All 632 growers' eventual carried positions
are unread. The surviving reading needs a value read by constraints, with
the stated window or other certificate; the converse for arbitrary families
is still a proposed theorem.

**Not a block — the original fixed point in G:** correct for the amended
study. Least-dead iteration started empty cannot discover a self-carried
unread position. The addendum correctly replaces it with least liveness,
seeded by knots and propagated through calls, and takes the complement.
This is a substantive rule repair. It followed the disclosed 20-case smoke
and preceded the full population run; it was not made before every result.
The current rule and all 632 certificates pass this audit.

These verdicts check the correction descriptions in the permitted note and
addendum. I did not inspect the global correction log, which was outside the
specified scientific inputs. The new censoring correction in point 2 is
recorded here; no outside file was edited.

## 6. Wording and evidence class

The remaining required edits are **Narrowing**:

- Replace unrestricted “every depth” in the answer and reading with “every
  sufficiently large depth”, accompanied by μ and the wrapper shift.
- Restrict “at most four” to the window-certified cases. Path rescues
  `ad4255ad1474` and `992270e6afcd` supply bounds of 5, not proofs of ≤4.
  They do not prove L ever exceeds 4 either.
- The order-label tally 55 size-3 / 36 size-4 describes 91 window cases.
  Including its two path additions gives 56 certificates of ≤3 and 37 of
  ≤4. Call these bounds or certificate sizes, not exact L values.
- Qualify G's formula for its 101 wrappers: `2+floor((d−1)/r)` rather than
  `2+floor(d/r)` at absolute depth d.
- Replace “5,964 exact window decisions” with attempted families and actual
  completions: 72 windows are incomplete. Retain the six-member search cap.
- Describe the population as “non-forgetting or capped first-ray growers”.
  The 66 inherited census caps do not establish a non-rectangular idempotent.
- “Proved per family” is defensible for a checked finite certificate **plus
  the relevant symbolic lemma**, yielding all sufficiently large depths.
  Census shares are computed; finite direct readings alone do not prove
  growth. Keep the read-carry and order interpretations within their checked
  scope, and the proposed general theorem separate from current results.

## Files written and validation

All paths below are inside this referee directory. No forbidden study Python
was opened or imported, no network was used, and no Git state or publication
was changed. Each lane used one computational process, at most three in
parallel; imposed address-space limits totaled under 10 GB. Direct cells
used 15–30-second budgets, preserving timeouts; the longest command was well
under 15 minutes. The grow searches totaled about 198 seconds of cell time,
with peak RSS under 0.9 GiB. The work completed inside the 75-minute budget.

- This report: `codex_report.md`.
- Grow scripts: `grow_core.py`, `grow_search.py`, `grow_lemma_audit.py`,
  `grow_global_exact.py`, `grow_validate.py`; proof review:
  `grow_proof_review.md`.
- Grow data: `grow_sample.json`, `grow_inputs.json`, `grow_controls.json`,
  `grow_smoke.jsonl`, `grow_results.jsonl`, `grow_halo6.jsonl`,
  `grow_branching.jsonl`, `grow_lemma_audit.json`, `grow_global_exact.json`,
  `grow_validation.json`.
- Window scripts/data/report: `window_prepare.py`, `window_audit.py`,
  `window_censor_probe.py`, `window_contract.md`, `window_inputs.json`,
  `window_results.json`, `window_results.jsonl`, `window_censor_probe.json`, `window_manifest.json`,
  `window_audit.md`.
- Scope scripts/data/review: `scope_audit.py`, `scope_audit.json`,
  `scope_audit.md`, `scope_global_review.md`.
- Overall hashes and JSON/source checks: `referee_manifest.json`, produced
  by `referee_finalize.py`.

Validation is V2: fresh same-task implementations and alternate SAT checks,
with permitted reuse of earlier referee code. The symbolic global-minimum
closure received a separate AI review; it is not external replication.
