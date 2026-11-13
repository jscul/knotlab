# Referee report TRUE-RATE-R1 (lean, Codex-assisted, fresh code)

**Verdict: Confirmed with fixes: three Narrowing, three Not a block.**
- **What reproduces.** With fresh code, the certificate's ten bonds, the carried counts, the mapping to BRANCH-DEPTH (664 of 664
  identical rules) and three of the 24 exact rates all reproduce.
- **The shift argument is sound,** so L(s) ≤ 3 at every depth is proved in the ten.
- **The fixes are wording.**
  - Cycles of ports change which top port is carried.
  - "112 uncarried" is a syntactic test.
  - BRANCH-DEPTH had classified 76 of the 226 outright, not 220.
  - The missed prior work is a Narrowing against TRUE-BOND, not a Block.
- **My own earlier slip.** It also corrects my TRUE-BOND-R1 report (section 5).

**How the work was split.** The background referee thread owns the verdict.
- **Codex.** The Codex command-line tool, at the owner's choice of model and effort, recomputed from fresh code, barred from the
  study's own folder (not opened). It took about 13 minutes, one process at a time, and wrote only in `codex/`, starting with
  `codex/codex_report.md`.
- **The referee.**
  - Checked the certificate's argument independently.
  - Judged the classes.
  - Checks its own earlier report.
- **Advisor.** The advisor model was not consulted.

## 1. The certificate (steps 1–4)

**The referee's reading.**
- **Steps 1–2.** The copies form a tree glued at ports, and a carried port appears in a connected chain of ray copies. So the rest
  of the pattern meets subtree(C_s) only through C_s's ports. Its projection there is R_s, with R_0 all eight states and
  R_{s+1} = F(R_s) for one fixed map F. The other calls are read as the bottomless relation G, exact at the fixed point.
- **Step 3.** If R_1 = R_0 = all, then F(all) = all and every R_s is all eight. Subtree(C_s) then has, under the shift, the
  allowed states of the whole pattern.
- **Step 4.** A size-3 bond in subtree(C_1), holding a port of C_1 that is a top port, an own distinction of C_1 and a side-copy
  member, therefore shifts to a bond at every depth. So L(s) ≤ 3 for all s ≥ 1, and the lower bound of 3 comes from TRUE-BOND's
  values where reached.

**Codex, fresh.** In all ten, and in all 20 carried families, G and R_1 are all eight states. Direct satisfiability on the subtree
to depth 3 finds each bond, given with its slots, own distinction and side path.
- **Each bond is a knot.** It has exactly the six NAE states with all pair projections full, and `knotlab check` accepts it under
  K1 to K3.
- **Each is stable.** It is unchanged with boundaries at depths 2 and 4.

**Narrowing: cycles change which port.** When the port is carried through a cycle of positions, C_s.port[p] = C_0.port[f^s(p)]. The
shifted bond still holds *a* top port, as L(s) requires, but not the same one at every depth. All ten certificates use fixed points,
and all 20 carried families have only singleton cycles, so no conclusion changes. The wording should allow for cycles; the census has
50 two-cycles.

## 2. The carried-port test and counts (Codex)

**The test.** A cycle in the partial map j ↦ a_j on slots 0 to 2, with controls for cycles of length 2 and 3, chains into a local,
and tails into a cycle.

**The counts reproduce exactly.**
- 20 carried of the 226.
- 320 carried of BRANCH-DEPTH's 432 bounded rules. All 320 are at exactly 3, and the 112 uncarried are 73 at 3 and 39 eventually at
  4.
- All 154 conditional rules and 65 of the 69 linear rules are uncarried.

**Narrowing: what "uncarried" rules out.** It excludes the syntactic identity carry only, not carrying enforced through constraints.
"Where a bounded reach is real" should say so.

## 3. The mapping to BRANCH-DEPTH (Codex)

**The same rules.** The archive order and definitions were rebuilt independently, and the usual-limit filter leaves the same 664
families.
- **Everything matches.** Definition keys, allowed port relations and first-call transition relations all agree with BRANCH-DEPTH's
  records, and the source hashes agree.
- **The offset.** The +1 converts zero-based enumeration to one-based lines. Offsets 0 and +2 recover no rule.

**The outcomes on the 226 reproduce:** 66 linear, 144 with a linear lower bound if a bond exists, 10 exactly three and 6 unresolved.

**Narrowing: the Answer's "largely answered".** BRANCH-DEPTH classified 76 outright (66 + 10). In the 144 only a conditional lower
bound was proved, and existence was still open. Say "76 classified outright, and 144 with a proved conditional lower bound", not an
implied 220.

## 4. The 24 closed families (Codex)

Codex reimplemented the uncapped summaries, ray graphs, trimming and exact cycle means for three families:

| Family | λ_true | L(s), proved |
| --- | --- | --- |
| 105 | 1/3 | 3 + floor(s/3) |
| 429 | 1 | s + 3 |
| 874 | 2 | 2s + 3 |

All three equal λ_ray, with exact cost-vector repeats from depth 1, and all 36 reference cells match. The other 21 rest on the
study's records and argument. **Not a block.**

## 5. Prior work, and a correction to my own report

**Against TRUE-BOND: Narrowing, not Block.** BRANCH-DEPTH's earlier note allows arbitrary side support.
- **What changes.** TRUE-BOND's novelty, its "open", and its framing of the four flat families: those are among BRANCH-DEPTH's ten
  already certified at exactly three.
- **What stands.** TRUE-BOND's computed minima and its shortening census are untouched. Exact true rates were not given before.
- **When it would be a Block.** Only a universal claim that ray growth forces true growth, which the ten refute. TRUE-BOND does not
  make that claim after its R1 corrections.

**My own TRUE-BOND-R1 report.**
- **The search I missed.** Like the study, it missed BRANCH-DEPTH's prior result.
- **The framing I used.** It called the four flat families (269, 302, 642, 908) "the strongest evidence in the run against 'growth
  survives'".
- **Why that needs qualifying.** All four carry a top port, and their size-3 bonds are local by identity. They show that the bond
  definition admits an identity shortcut (A81), not that the law's reach across depth stops.
- **What to do.** The coordinator should log this as a correction to the TRUE-BOND-R1 wording (Narrowing). I do not edit the logs
  myself.

## Fixes for the thread

1. **Cycles.** Say "a top port at every depth, which under a cycle of positions need not be the same one". **Narrowing.**
2. **"Where a bounded reach is real".** Qualify the 112 uncarried as free of the syntactic identity carry only. **Narrowing.**
3. **BRANCH-DEPTH's prior result.** Give it as 76 classified outright and 144 with a conditional lower bound, not "largely answered"
   for 220. **Narrowing.**
4. **The 24.** Keep them, noting that 3 were independently recomputed. **Not a block.**
5. **TRUE-BOND's missed prior work.** Keep it as a Narrowing. **Not a block** as a reclassification.
6. **Log the correction to TRUE-BOND-R1's wording** about the four flat families (carried, local by identity). **Not a block.**

## Files

`codex/`: Codex's brief and report, `certificate_audit.py`, `mapping_audit.py`, `rate_recompute.py`, `validate_audit.py` and their
JSON.
