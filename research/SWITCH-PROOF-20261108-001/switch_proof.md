# Prove that creation between glue lines sees only the switching class

Epic `SWITCH-PROOF-20261108-001` (program topology), 2026-11-08.

## The question

- **Where it came from.** SWITCH-READ found, on five glues, that two placements of the atoms in one switching class give native maps
  that agree exactly between glue lines and differ through the atoms. Its selected next step was a proof of the first half; the
  coordinator approved it under the owner's standing mandate.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Theorem.** For every cubic glue, every two signings in one switching class, and every two glue lines a and b, removing a and gluing at b gives the same native creation verdict in the two plain edge-atom spaces, for each far side. | proved | A |
| 2 | **Why.** An edge atom's own lines force r0 = r1 = r2 = ¬p and leave its inner points free enough that no knot the two-round rule uses contains them; so creation between glue lines is creation in the signed glue, and switching only complements points. | proved (finite lemma exhaustive) | A |
| 3 | **Cross-checks.** The glue block equals the signed glue's creation map on 22 placements (3,500 entries); 136 random switchings of the 17 signed glues change no entry, census 6 included. | computed | A |

## Answer

- **Proved.** The part of native creation that lies between glue lines sees a signing only through its switching class, for every
  glue and every signing, not just the generator's.
- **And it is the signed glue's own map.** The atoms do nothing there but negate their incidences. They show their place only when a
  line of one is removed, which frees the incidence.

## Reading

- **What native creation sees.** Through the glue, a signing's switching class: for a bipartite glue, the parity of signs around every
  cycle. Through the atoms, where the signs sit. The first is the data Pfaffian counting uses on these spaces.
- **Doctrine.** Everything here is invariant under relabeling lines and re-listing their points.

## Literature

- **Classical.** Switching classes of signed graphs and their balance (Zaslavsky).
- **Ours.** The two-round rule (PENDANT-LINE), complementing points (CHAIN-TRANSFER), the comparison (SWITCH-READ).
- **New here.** The theorem and its proof.

## Pending

- **SWITCH-READ's nine remaining placements** were folded in on 2026-11-08 (SWITCH-READ's stress test): as the theorem predicts, the
  glue block of each equals the signed glue's own map, 1,936 entries, and every pair of placements has the same glue block.
- **Still open from earlier epics.** As listed in SWITCH-READ's ledger.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the switching-class theorem | **Status:** Successful | Proved for every glue and signing, with a finite lemma |
| Local direction — what native creation sees of a signing | Continue | Whether it sees the whole switching class is open |
| Broader exploration — native creation against counting | Unmapped | The theorem puts both on switching classes; nothing compared yet |
| Long-term goal — G4 Emergence lives in handles | Capability gained | What native creation reads of the glue is now a theorem |

**Corrections:** none.
**Goals:** G4 checkpoint (capability gained).
**Assumptions:** none added or changed.

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Does the glue block tell every switching class apart? | 2/3 — Substantial | 3/3 — Ready | All 512 classes of the smallest glue → distinct blocks or a collision | Selected · started |
| 2 | Glue block against Pfaffian counting | 2/3 — Substantial | 1/3 — Stated | Pose what "carries the same information" means → a test | Alternative · deferred |
| 3 | Fold in SWITCH-READ's nine placements | 1/3 — Incremental | 3/3 — Ready | Running → fold the comparisons in | Alternative · done |

1. **A complete invariant?** If the glue block separates every switching class, native creation between glue lines reads exactly the
   cycle parities of the signing, a clean description of what emergence sees in the glue; if not, the collisions say which parities it
   misses. The question is exact and cheap: the smallest glue has 512 classes, already computing in the background.
2. **Counting.** Both now live on switching classes; how they compare is not yet a precise question.
3. **The nine placements.** Running in the background since 07:40 UTC. (Folded in on 2026-11-08, as predicted.)
