Verdict: **Confirmed with fixes.**

Fresh recomputation supports the checked first-ray results and the headline
arithmetic. The broad reading of first-ray growth as a ray-independent count of
depth is blocked. The implementation prohibited in the brief was never opened
or imported. No Git state was changed and nothing was published. This audit
writes only in this referee directory; it does not amend the studies themselves.

## 1. Multi-definition path and large blocks

**Not a block — checked computations agree.** `fresh_recompute.py` independently
implements the usual-limit fixed point, depth-first inlining with fresh own
distinctions, S, the entry and ray calls, side-limit relations, and the block DP.
The SAT path separately expands the original definition syntax with a stack;
it does not use the DP's flattened bodies, selected call indices, or tables.
It tests constrained projections and every single-member deletion, restricting
members to the ray's distinctions, including own distinctions created by inlining.

The first-ray sample has 49 families, **37 with several definitions**, including
seven with a block of size 12, and blocks of sizes 10 and 11. Some have a
non-self-holding main with more than three ports. At s=1,2,3, all 147 SAT checks
agree: 141 give exact minima or exact absence; six establish only “no bond of
size at most 7”, consistent with the larger/absent DP values. Among the
multi-definition cases, 107 of 111 checks are exact. Truncations have up to
39 distinctions. Nineteen additional full-assignment enumeration controls agree.
Selection is class/size-stratified and favors small graphs; it estimates no share.

**Narrowing — G3 is incomplete.** G1 covers one-definition families; G2's wrapper
does not test arbitrary inlining. G3's 139 completed families give useful evidence,
but its 11 unfinished largest families leave a size-dependent gap. They do not
justify “all frozen gates passed” or full validation of large multi-definition
blocks. My additional checks materially improve that coverage, but do not identify
and finish those exact 11 families or reproduce their deeper tests.

## 2. Classes

**Not a block.** All 49 fresh complete graphs reproduce the stored class, node
count, exact minimum cycle mean, residue verdict/period/missing residues, and
L_ray(1..30): 1,470 depth values without a mismatch. The classes are bounded 9,
grows 9, lost 9, none 14, mixed 8. Both one- and multi-definition cases are
included wherever that class exists; all eight mixed families have several
definitions and all eight were checked. Growth uses a positive exact cycle mean
on a complete graph, not finite-depth fitting. Boundedness uses the explicitly
permitted prior referee's exact residue routine; all other mathematics is fresh
code. Synthetic positive/negative residue and fractional-cycle controls pass.

## 3. Crash and recovery

**Narrowing — resume, with aggregate stability only.** Contrary to the question's
“reran from scratch”, `run_info.json` records 110,262 resumed records and 14,310
new records. The logs and partial-summary missing-key list agree with that split.
The retained prefix represents 206,980 draws; the suffix adds 16,281.

Recomputing the prefix from the final rows matches every available partial-summary
comparison: 1,830 count/band comparisons and 366 rate/bound/onset histogram
comparisons, zero mismatches. This supports “no aggregate change detected”. The
prepatch per-family rows and a before/after implementation pair are unavailable
in the permitted evidence. Compensating per-key changes, or changes in individual
L_ray, graph, or residue fields, cannot be excluded. An unconditional “no family's
result changed” is not independently established by these archives.

## 4. Weights, counts, and Conclusions 2–4

**Not a block — arithmetic reproduced.** Replaying the eight permitted sampler
seeds gives exactly 223,261 draws and 124,572 distinct keys. A retained draw gets
one vote; repeated keys retain their multiplicity. These are Monte Carlo shares
under the capped description sampling, with no second weighting by 2^-bits.
Distinct-family counts describe a different denominator. The original stored-draw
bits/fates gate G0 was not independently rechecked against its separate archive.

| Quantity | Recomputed draws / denominator | Share |
| --- | --- | --- |
| S2 + S3, no depth | 130,379 / 223,261 | 58.3976% |
| S1 + S4, no bond by construction | 6,780 / 223,261 | 3.0368% |
| No eligible ray bond at large depths, including no-depth cases | 178,182–178,995 / 223,261 | 79.8088–80.1730% |
| Bounded, all draws | 30,979 / 223,261 | 13.8757% certified |
| Grows, all draws | 13,279 / 223,261 | 5.9477% certified |
| Forever, computed: none / bounded / grows | 40,046 / 30,431 / 13,002, each over 85,240 | 46.9803% / 35.7004% / 15.2534% |
| Limit-only, computed: none / bounded / grows | 7 / 548 / 277, each over 862 | 0.8121% / 63.5731% / 32.1346% |

P1 is 30,431–31,226 / 44,236 = **68.7924–70.5896%**, with bootstrap interval
[68.3422,71.0295]%. P2's growth interval is [15.0047,16.4395]%. P3's conservative
difference is 15.9485 percentage points, bootstrap lower quantile 12.7529 points.
Independent draw bootstraps reproduce the reported endpoints; P1–P3 survive.
Across the final summary, 2,145 count/band comparisons and 429 histogram comparisons
agree. Full tables, including distinct-family counts, are in `weights_crash.json`.

**Narrowing — wording and denominators.** “Only because their bonds exist” is
too strong: conditional growth bands still differ, 29.3924–31.1895% versus
32.8588–34.9941%. Say the large gap is mainly associated with absence, without a
causal claim. The Reading's roughly 6% of draw weight cannot be multiplied by
297/645 from a uniform sample of eligible distinct families to estimate weight
growing on both rays. Also qualify “mixed below 0.01%” as **classified** weight:
8 draws are 0.00358%, but the unresolved-inclusive upper band is 0.36773%.

## 5. Construction versus measured class; one-sided bounds

**Not a block.** S1–S4's implications follow from the definitions; their shares
are measured properties of these sampled descriptions. Finite-state eventual
behavior and the graph-class implications are method facts. Neither forces the
approximately 70/30 bounded/grows split or its similarity across fate cells.

P1 legitimately rests on a conservative lower bound on the bounded share: even
counting every unresolved draw against bounded leaves its lower interval above
one half. Bounded ray size supplies an upper bound on unrestricted least-bond
size. First-ray growth or absence supplies no corresponding lower bound for
unrestricted bonds; the 70/30 split must retain its ray and conditioning.

**Narrowing — two overstatements.** “Nothing below the top three distinctions”
should mean no new eligible own-distinction endpoint at increasing ray depth;
main may have more ports and finite own distinctions. Conclusion 5's “settles at”
should read “has a certified upper bound of”. The residue routine's cost and onset
are sufficient certificates, not optimal values or minimal onsets. For example,
family-row 262 has bound 5/onset 3 while all 30 recorded minima are 3; a stress-test
row alternates 2 and 3. No claim of eventual constancy follows from boundedness.

## 6. Ray dependence and the correction's severity

**Not a block — the 131 upper bounds are independently certified.** The stress
file has 224 rows: bounded 131, grows 87, lost 2, none 1, unresolved 3. A stratified
16-family last-ray sample reproduces all 48 SAT minima at s=1..3. Fifteen full
graphs and exact residue tests agree; one hits my 100,000-node referee cap, retained
as a resource failure. A separate fresh positive test then certifies **all 131**
bounded cases: it retains only paths within each reported cost bound and detects
an exact repeat of the entire cost layer, checking every accepting residue on
that repeat. Bounds are 3 for 96 cases, 4 for 32, and 5 for 3. Its sufficient
onsets range from 1 to 21; they need not equal the earlier certificates' 1–11.
This also handles the six bounded cases whose full study graphs are incomplete.

**Block — against the broad published depth/counting reading.** The phrases
“the law's reach measures depth there, as on a ruler” (PROVED-RATE, Reading) and
“counting inside … appears in more than a third” (BOND-DEPTH, Answer), if read as
ray-independent growth with copy depth, are contradicted by these 131 cases.
The least bond to some eligible copy at that depth is bounded above by five,
despite first-ray growth. Dependent claims using the broader inference must stop.

**Narrowing — the replacement; Not a block — the equations.** Both earlier notes
also explicitly restrict their technical statements to a ray and leave other
bonds open. Those equations, rates, and first-ray finite values stand. “Narrowing”
describes replacing the broad reading by the restricted one, but should not be
the sole verdict against the broad reading itself. This does not refute either
numerical study. Even “distance to one copy” needs the qualification that bond
members are restricted to the chosen ray; its unrestricted least bond may be smaller.

## 7. Unresolved

**Not a block.** Exactly 813 draws/keys are unresolved: 746 over the block cap,
38 timeouts, 27 incomplete capped graphs, and two worker exits without results.
They remain outside every substantive class numerator and inside the appropriate
computed denominator. For class count C, unresolved U and computed total N, bands
are [C/N,(C+U)/N]; P1 uses its separately registered conditional denominator.
The cells contain U=795/85,240 (0.9327%) and 18/862 (2.0882%), respectively,
both below the 5% undecided threshold. No unresolved row carries a positive
bounded certificate. Thus none is silently counted as grows, bounded, or absent.

## Files and reproduction

Primary scripts: `fresh_recompute.py`, `bounded_certificate.py`, `verify_referee.py`,
`weights_crash.py`. Retained JSON evidence: `selection.json`, `controls.json`,
`fresh_primary.jsonl`, `fresh_alternative.jsonl`,
`alternative_positive_certificates.json`, `all131_positive_certificates.json`,
`verification_summary.json`, `weights_crash.json`, `claims_review.json`, and
`scratch_cleanup.json`.
Supporting reviews: `weights_crash_notes.md`, `claims_review.md`; this report is
`codex_report.md`. Input/source hashes, sample keys, resource failures, exact
values, and certificates are retained in those outputs. Earlier redundant probe
outputs were task-owned scratch and were removed; existing brief files were preserved.

Exact final computation commands, from the repository root (fresh output names
are required when repeating the two write-once JSONL runs):

```bash
/home/jscul/p-vs-np-contact-first/.venv/bin/python -B research/REACH-CENSUS-20261113-001/referee-R1/codex/fresh_recompute.py controls
/home/jscul/p-vs-np-contact-first/.venv/bin/python -B research/REACH-CENSUS-20261113-001/referee-R1/codex/fresh_recompute.py select
/home/jscul/p-vs-np-contact-first/.venv/bin/python -B research/REACH-CENSUS-20261113-001/referee-R1/codex/fresh_recompute.py primary --seconds 12 --output fresh_primary.jsonl
/home/jscul/p-vs-np-contact-first/.venv/bin/python -B research/REACH-CENSUS-20261113-001/referee-R1/codex/fresh_recompute.py alternative --seconds 25 --output fresh_alternative.jsonl
/home/jscul/p-vs-np-contact-first/.venv/bin/python -B research/REACH-CENSUS-20261113-001/referee-R1/codex/bounded_certificate.py
/home/jscul/p-vs-np-contact-first/.venv/bin/python -B research/REACH-CENSUS-20261113-001/referee-R1/codex/bounded_certificate.py --all
/home/jscul/p-vs-np-contact-first/.venv/bin/python -B research/REACH-CENSUS-20261113-001/referee-R1/codex/verify_referee.py
/home/jscul/p-vs-np-contact-first/.venv/bin/python -B research/REACH-CENSUS-20261113-001/referee-R1/codex/weights_crash.py
```

No process pools were used: at most three audit lanes, each with one computation
process. The heaviest recorded process peak is below 0.75 GiB; the draw/initial
bootstrap audit took 173 seconds, and the primary/alternative graph samples took
about 19/17 seconds. All commands stayed within the requested time and memory
limits. These are bounded checks and positive certificates, not a fresh full census.
