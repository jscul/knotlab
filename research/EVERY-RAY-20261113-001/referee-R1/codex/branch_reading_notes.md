# Independent branch, arithmetic, provenance and wording audit

Scope: EVERY-RAY-20261113-001, referee R1, branch/reading lane. Fresh standard-library implementation in
`branch_reading_check.py`; full machine evidence and input SHA-256 values in `branch_reading_results.json`.
No EVERY-RAY producer Python was read or imported; no network, Git mutation, ticket mutation, or publication.
Only the three assigned referee files were written. The final computation took about 1.6 seconds and used
one Python process at a time. An initial launch failed at Python parse time, before computation, and was
corrected; subsequent bounded reruns were explicitly authorized by the lead.

**Verdict:** preserve the finite-depth minimum results and main frozen sample verdict, but correct the
uncarried uncertainty and several construction/reading claims before accepting the report as written.
This lane does not independently validate the producer DP or prove its infinite-path interpretation.

## Block

1. **One path at all depths is stronger than the measured minimum.** The frozen object gives, at each
   sufficiently large finite depth, some path and some bond of uniformly bounded size. The Answer's
   “some descending path ... at every depth” and its later reference to “that path” interchange
   `for every depth, there exists a path` with `there exists one path, for every depth`.
   The saved residue certificate alone does not justify that interchange. The main lane is checking
   coherent repeating-path witnesses separately. An eventual certificate also needs its finite prefix
   checked before it supports an all-positive-depth numerical bound.

2. **Unresolved uncarried results are called carried-only.** Among the 204 bounded, inequivalent-call G
   families, the actual uncarried classes are **200 bounded, 3 none, 1 unresolved**. The fourth purported
   carried-only family is a timeout with a positive plain bounded certificate and unresolved uncarried
   result. Its key is
   `[[3,0,[["K",[1,0,2]],["SELF",[0,2,1]],["K",[2,1,0]]]],[3,0,[["K",[2,0,1]]]],[4,0,[[0,[1,2,0]],[0,[2,0,3]]]],[3,2,[[1,[1,0,3]],["SELF",[1,3,2]],["SELF",[3,2,0]]]]]`.
   Therefore the secondary uncarried band has **27 unresolved**, not 26: **200/296 to 227/296**,
   or **67.568%–76.689%**, with Wilson envelope **62.039%–81.145%**. The reported upper share
   76.351% and upper Wilson 80.835% omit this uncertainty.
   B similarly has **55 uncarried bounded, 15 no uncarried bond, 30 unresolved**; five of the reported
   20 carried-only rows actually have unresolved uncarried results. Its reported 25 unresolved is five
   too few. The spec's “otherwise carried only” label follows its prescribed else-case but is not a
   proof of “only.” These errors do not change the main P1 verdict.

3. **Local equivalent calls do not force the first-ray result.** All four sampled G families whose calls
   form one local symmetry class are bounded over paths although their archived first-ray class grows.
   Independent exhaustive allowed-state permutation checks reproduce all four equivalence classes.
   A simple example is
   `[[3,2,[["SELF",[3,0,1]],["K",[4,2,1]],["SELF",[3,0,2]]]]]`:
   exchanging ports 1 and 2 preserves the flat relation and exchanges the calls, yet the results differ.
   Thus the preregistration's “equivalent ⇒ L_path=L_ray” and “grow by construction” claims are false
   for its frozen equivalence definition. Keep the frozen exclusion as a stated estimand; remove its
   construction-based justification. One of the four even has `mixed_path_needed=true`.

4. **The numerical bound sentence is unsupported by the saved certificates.** Among those 204 G
   families, `uniform_cost_bound` has distribution
   **2:1, 3:97, 4:63, 5:27, 6:9, 7:2, 8:1, 9:3, 14:1**.
   The report says 3–9, with 100 at 3. One family has bond value 2 throughout all 30 recorded depths and
   certificate bound 2. Another has certificate bound 14, onset 6, although its recorded values are all
   3. A certificate bound need not be tight; a smaller eventual bound needs its own evidence. Replacing
   the saved certificate by the largest or final value seen through depth 30 would not prove that bound.

## Narrowing

5. **G-reg is a revised-domain pass.** Of 500 one-SELF-call rows, independent expansion of ordinary
   calls finds **486 with one entry** and 14 with several entries. All 486 one-entry graphs agree.
   Exactly **9** graphs differ; each has 2 or 3 entries, and all 500 class and lambda pairs agree.
   The other five multientry rows happen to have equal graphs. Original spec/prereg required equality
   for c=1; A1 freed main's entry but still claimed c=1 was unchanged; the third clarification narrowed
   the gate after gate results, before class shares. Preserve that chronology and the nine failures.
   Also correct “one SELF call ⇒ one path”: **one SELF call and one entry** is the valid domain.
   The sample has c≥2, so this does not invalidate its selected rows.

6. **State the sampled population in claims about prevalence.** The random selections reconstruct
   exactly, in sequence, from `Random(20261114)` and the archived class pools:
   G **300/6,701 after excluding 224 from 6,925**, N **200/6,469**, B **100/18,281**.
   There are no duplicate, missing, or extra selected rows. Statements such as “usually,” “about seven
   in ten,” or decline with call count need an explicit sample/population qualifier. The four-or-more
   call cells are small and differently capped; the recorded resolved shares need not imply a general
   structural monotonic law. A c=1 family can be bounded or bondless; it is not automatically a grower.
   My direct archived-S SELF count gives 32,314 total eligible records rather than the draft's 32,315;
   this auxiliary one-record discrepancy does not affect any of the three exactly reconstructed pools.

7. **Phase 2 certified three additional G bounded cases.** There are 29 rerun rows, 28 G and 1 N.
   Three G classes change unresolved→bounded. Two reach `status=done`; the third remains a timeout but
   has the positive bounded certificate expressly allowed by the spec. “Resolved 2 of 29” is true only
   for completed statuses, not for bounded scientific verdicts. The report should distinguish these.

8. **No successful same-input old/new replay is supplied.** Metadata assign G/N/B/phase2 to
   `paths_dp.py` hash `a9cd74a7…`; B_resume and gates use `164661c7…`. B contains 25 keys and
   B_resume the complementary 75. Their disjointness proves coverage, not semantic equivalence of
   the two code versions. The 29 phase-2 overlaps retain the old hash. Across every overlap in the six
   allowed sample files, a broad set of mathematical fields has **zero resolved-versus-resolved
   conflicts**. Differences are cap-limited partial information and the three positive resolutions.
   Source-level verification that the patch changes only timeout handling remains outside this lane.

9. **Branch mapping is partial and the proposed inequality is not valid.** From the prior 664-member
   definition inventory I independently recomputed usual-limit G, first finite death, own/call counts,
   and the first-ray port transition, including the child's G restriction. All 664 signatures match:
   **640 uniquely, 24 with two candidate source rows**. This signature encodes the first-ray transition
   and the listed summaries, not the full call list; even a unique match is structural corroboration,
   not a raw source-identity proof. No positional zip was used. Of the 600 sample
   families, 477 have one definition, but only **2** exactly occur in that earlier inventory. Both are
   B, currently DP unresolved, and have BRANCH outcomes exactly-three / eventually-exactly-four.
   Thus the sample supplies no matched BRANCH-linear contradiction.

   All 224 G-last definitions and reported idx values match the earlier inventory exactly; 218 have
   unique port signatures. All collision candidates agree on the outcome. At distinct-family level
   the mapped outcomes are **65 linear, 143 linear-lower-bound-only, 10 exactly-three, 6 larger-size
   unresolved**. These are the G-last subset, not BRANCH's full totals 69/154. The 664 exact inventory
   definitions are all distinct; equal port signatures must not be mistaken for duplicate definitions. Of the
   65 linear mapped families, 53 have fully finite G-last L_path prefixes, which remain finite-depth
   evidence; G-last deliberately gives no eventual path class. Across the full earlier inventory,
   the 69 structurally matched linear labels have archived ray classes 65 grows, 2 lost (idx 547/761),
   and 2 unresolved (idx 692/1018). Loss of a path-restricted bond does not exclude a members-anywhere
   bond to that same target, so these labels are compatible as well.

   The raw source-file/line→definition archive is not an allowed input. This signature bridge
   corroborates but does not independently reconstruct that raw identity link. More importantly,
   **L_true≤L_path is not generally valid**: L_true fixes the first-ray target while L_path minimizes
   over target copies. The valid frozen bounds are **L_any≤L_true** and
   **L_any≤L_path≤L_ray**. BRANCH-linear fixed-target results and a bounded different-target path
   would therefore be compatible. A same-target restricted-path comparison is needed for the former
   inequality. Do not treat absence of a contradiction in this limited overlap as a broad validation.

## Not a block

10. **Main count verdict and existence numerators reproduce.** Final G classes are 208 bounded,
    66 grows, 26 unresolved; excluding four equivalent-call families gives **204/296 to 230/296**,
    **68.919%–77.703%**, with Wilson envelope **63.432%–82.072%**. P1 remains **undecided**.
    N has 20 bounded, 13 grows, 165 none, 1 lost, 1 unresolved. P3 gives **33/200 to 34/200**,
    **16.5%–17.0%**, with Wilson envelope **11.997%–22.816%**. A single ordinary Wilson interval for
    33/200 ends at 22.266%; call the wider reported interval the unresolved-aware envelope.
    All **79** reported inequivalent G/N growers have complete graphs. G's growth rates reproduce:
    30 at 1, 24 at 1/2, 9 at 1/3, 3 at 2. The 50 mixed flags each list all fixed entry/call pairs,
    with no unresolved or bounded pair, so their saved certificates are internally consistent.
    These are arithmetic/provenance checks, not an independent proof of those graph certificates.

11. **Weight summaries are unaudited here.** The allowed sample rows, selection, and family census
    contain no per-family draw counts. The draw archive is outside the whitelist. No weight summary
    was recomputed or certified by this lane.

Recommended report wording: “In this frozen sample, the minimum bond over finite paths is eventually
bounded for 204 of 296 first-ray growers with inequivalent calls, with 26 unresolved. The count result
does not decide the registered 75% threshold. Of those 204, 200 have certified bounded uncarried
finite-path minima, three have no uncarried bond, and one has unresolved uncarried status. A single
infinite path realizing a uniform bound requires a separate witness.”
