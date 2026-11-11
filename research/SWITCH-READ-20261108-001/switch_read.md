# Does native creation see only the switching class?

Words (2026-11-11). Reworded under the owner's language rule (Intuitions guide, Glossary): a Fano atom is a Fano piece. Results are unchanged;
the earlier text is in git history.

Epic `SWITCH-READ-20261108-001` (program topology), 2026-11-08.

## The question

- **Where it came from.** TRISUM-READ's one failed frozen statement came from a symmetry of seed 5's native map that moves an atom to
  another incidence while keeping the signing's switching class. Its report parked the conjecture as backlog B5: the native creation
  map depends on the signing of the glue only through its switching class.
- **The go-ahead.** The coordinator took B5 up under the owner's standing mandate for autonomous research (2026-11-08).
- **The test.** HANDLE-COUNT A's generator returns different minimal signings, and so different placements of the atoms, under
  different hash seeds. Compare the native maps of two placements of one glue in one switching class.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **The placements.** Under hash seeds 0 to 23 each of the 17 glues comes out the same, with Pfaffian and minimal signings in one switching class. Eleven glues get two or three placements that are not isomorphic as spaces, 25 in all. | computed | A |
| 2 | **No: the whole map sees the placement.** In all five pairs mapped (38 to 56 points), the two native maps are not isomorphic, neither with the glue's lines fixed nor under any bijection. | computed | A |
| 3 | **Yes for the glue block.** In all five pairs, removing a glue line and gluing at a glue line gives the same vector in both placements, entry by entry. | computed | A |
| 4 | **The difference is in atom removals.** Removing a glue line creates at the atom lines with the same multiset of vectors in both placements; removing a line of an atom creates differently at glue lines. | computed | A |
| 5 | **TRISUM-READ's reading transfers.** Its frozen statements P1 to P7 hold on all five alternative placements. | computed | A |
| 6 | **One size past (stress test).** With the nine other placements (56 to 60 points), all 17 pairs on 11 glues behave as in conclusions 2 to 4. P1 to P7 hold on 13 of the 14 alternative placements; on seed 11's second, P1 fails through a symmetry of the glue that moves an atom, as on TRISUM-READ's seed 5. | computed | stress test |

## Answer

- **Native creation splits in two.** Creation among glue lines sees only the switching class of the signing, which is what Pfaffian
  counting sees. Creation that starts by removing a line of an atom reads where that atom sits.
- **So the conjecture is false as stated and true for the glue.** TRISUM-READ's seed 5 was a symmetric case: there a symmetry of the
  glue moves the atom, so even the atom removals cannot tell the two places apart.

## Reading

- **Why atom removals see more.** An intact Fano piece acts on the glue as one negated incidence (ATOM-ONE), and switching-equivalent
  signings give the glue the same solutions up to complementing points, which the creation test does not see. Removing a line of an
  atom makes it transparent and frees its incidence, and which incidence is freed is what the placement records. This is a reading
  from earlier results, not yet a proof.
- **For the junction reading.** TRISUM-READ's junction signature lives in the glue block, so it depends only on the switching class.
  Its atom reading uses atom removals but still held on every alternative placement.
- **For counting.** The part of native creation that sees only switching classes is the glue's, the same data that decides Pfaffian
  counting on these spaces. Whether the two agree beyond that is open.
- **Doctrine.** Everything here is invariant under relabeling lines and re-listing their points.

## Literature

- **Classical.** Switching classes of signed graphs (Zaslavsky). Pfaffian signings of a matching-covered bipartite graph form one
  switching class (checked here directly for every glue).
- **Ours.** Atoms acting as one (ATOM-ONE), the native map (GENUS-READ), the trisum spaces and the junction reading (HANDLE-COUNT,
  TRISUM-READ).
- **New here.** The comparison, and the split of native creation into a part that sees the switching class and a part that sees the
  placement.

## Stress test

One size past ticket A's five pairs: the nine other placements HANDLE-COUNT A's generator gives (seeds 11, 34, 46, 96, 282 and 288; 56
to 60 points), mapped exactly in the background (`docs/LONG_RUNNING.md`, SWITCH-READ-M1) and compared with every other placement of
their glues. The maps are `stress_test_m1_maps.json.gz`, made as `stress_test_m1_map.py` makes them; the comparison is
`stress_test_m1.py`.

| Check | Result |
| --- | --- |
| Pairs of placements of one glue | 17, on 11 glues, 38 to 60 points |
| Glue block identical | 17 of 17 |
| Whole maps isomorphic, glue lines fixed or under any bijection | 0 of 17 |
| Difference only from atom removals | 17 of 17: removing a glue line creates at the atom lines alike, and in every pair some glue line's column from atom removals changes |
| Glue block against the signed glue's own map (SWITCH-PROOF's corollary) | the 9 new placements, 1,936 entries, all equal |
| TRISUM-READ's P1 to P7 on the 14 alternative placements | hold on 13; on seed 11's second placement (hash seed 3) P1 fails: loaded line 8 and unloaded line 9 share a diagonal class |
| Seed 11's failure | a symmetry, as in seed 5: exchanging lines 1 and 3, 8 and 9, 10 and 11 preserves the native map and fixes every atom line, and the one skeleton automorphism inducing it keeps the switching class and moves the atoms' places |

- **Verdict: passed.** Every conclusion of ticket A holds one size past. Seed 11's second placement is a second symmetric placement,
  the case that the narrowed reading of `TRISUM-READ-20261107-001-D002` already allows.
- **Rerun passed.** The script's full rerun, which also recomputes the last row of each new map, reproduces every number above
  (`stress_test_m1.json`; `docs/LONG_RUNNING.md`, SWITCH-READ-M2).

## Pending

- **Still open from earlier epics.** `JUNCTION-READ-20261106-001`, left open by an interrupted session, asks the question TRISUM-READ
  answered; qualifying `FAR-READ-20261106-001-D002` and the second sentence of D001; qualifying `PHASE-HALO-20261103-001-D001` and
  `FACE-CLAIM-20261103-001-D003`; the SELECTION-NOTE erratum; superseding `KNOT-COMPOSE-20261101-001-D001`; whether counted length
  should ever count as a native magnitude.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — native creation and the switching class | **Status:** Successful | Answered: the glue block sees the class, atom removals see the placement |
| Local direction — reading signings from creation | Continue | A proof of the glue block's invariance is in reach |
| Broader exploration — native creation against counting | Unmapped | Whether creation's glue block determines the counts is untested |
| Long-term goal — G4 Emergence lives in handles | Capability gained | Native creation's view of a signing is now located |

**Corrections:** TRISUM-READ-20261107-001-D002 narrowed (Narrowing, overreading): its title said native creation cannot see where an
atom sits within its switching class; it can, except where a symmetry of the glue moves the atom.
**Goals:** G4 checkpoint (capability gained); backlog B5 marked taken.
**Assumptions:** A29 overturned: an atom's place within its switching class matters for native creation, though not for the glue block
or for TRISUM-READ's statements.
**Stress test:** passed one size past (17 pairs, 38 to 60 points; folded in 2026-11-08, and the script's full rerun passed).

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Prove the glue block depends only on the class | 2/3 — Substantial | 2/3 — Testable | Atoms as negations plus switching as complement → a proof or a gap | Selected · done (`SWITCH-PROOF-20261108-001`) |
| 2 | Glue block against Pfaffian counts | 2/3 — Substantial | 1/3 — Stated | Compare the glue block's classes with counting's data → a match or a split | Alternative · deferred |
| 3 | Fold in the nine remaining placements | 1/3 — Incremental | 3/3 — Ready | Running → fold the comparisons in | Alternative · done (stress test) |

1. **A proof.** It would turn a computed split into a theorem about what native creation sees, the strongest statement this line can
   make about G4; the route is concrete (an intact atom acts as one negation, switching complements points, the creation test ignores
   complementing), and the main uncertainty is whether the test's far sides are invariant under complementing a gluing line's points.
2. **Counting.** If the glue block carries the same information as the Pfaffian count, native creation and counting would see a signing
   alike, a bridge from G4 to G3; the comparison is not yet posed precisely.
3. **The remaining placements.** They extend the computed range, and are already running in the background. (Folded in on
   2026-11-08: the stress test above.)
