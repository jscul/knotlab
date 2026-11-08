# Does creation between glue lines tell every switching class apart?

Epic `SWITCH-COMPLETE-20261108-001` (program topology), 2026-11-08.

## The question

- **Where it came from.** SWITCH-PROOF proved that creation between glue lines of a plain edge-atom space depends only on the
  switching class of its signing: the glue block is the signed glue's own creation map. Its selected next step asked the converse:
  does the glue block tell every switching class apart?
- **The go-ahead.** Taken at SWITCH-PROOF's close under the owner's standing mandate for autonomous research (2026-11-08).
- **The test.** Compute the glue block of every switching class of the smallest trisum glue (ticket A), and one size past, of the
  10-line glue (ticket B). Explain each collision by a symmetry of the glue or show that none does.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Not a complete invariant.** On the smallest glue (8 lines) the 512 classes give 448 distinct glue blocks; on the 10-line glue the 2,048 classes give 1,526. | computed | A, B |
| 2 | **Nearly complete up to symmetry on the smallest glue only.** There every collision but one lies inside an orbit of the glue's 24 symmetries: 41 values on 42 orbits. The exception is two orbits of signings that differ by moving one sign along a line, with 40 and 34 solutions. | computed | A |
| 3 | **Blindness grows.** On the 10-line glue the blocks take 429 values on its 576 orbits; 92 of the 98 groups of classes sharing a block span several orbits, and 76 mix solution counts. | computed | B |
| 4 | **Where nothing creates, creation sees nothing.** The largest group on the 10-line glue is exactly the 190 classes at which no far side creates anywhere: 66 orbits, 60 to 110 solutions. | computed | B |
| 5 | **Confirmed on the spaces, census 6 included.** A colliding pair at each size has identical glue blocks on its plain spaces themselves, and adding census 6 under every order of the gluing line separates neither pair. | computed | A, B |
| 6 | **The Pfaffian class stands out.** At both sizes the generator's signing lies in the only class without solutions, the class whose plain spaces are three-fold, and no other class shares its block. | computed | A, B |
| 7 | **Rows are coarse.** Each row depends only on the class on the glue without its line (by SWITCH-PROOF's theorem), and on the smallest glue it takes only 55 or 57 values on that glue's 128 classes. | computed, reduction proved | A |

## Answer

- **No.** Creation between glue lines does not tell switching classes apart. On the smallest glue it nearly does up to symmetry, but
  one size past it separates only 429 of 576 orbits.
- **It does not read the count.** Classes with one block differ in their numbers of solutions, the quantity that counting computes,
  by as much as 60 against 110.
- **It does single out the contradiction.** The one class whose plain spaces are three-fold has a block of its own at both sizes.

## Reading

- **Native creation sees a signing where it creates.** Through the glue it reads the switching class only as far as creation happens.
  For 190 of the 10-line glue's classes nothing creates, so it sees nothing of them. Through the atoms it reads where the signs sit
  (SWITCH-READ).
- **One row reads little.** On the smallest glue a row takes 55 or 57 values on 128 classes; what the block recovers comes from the
  rows together.
- **The count is invisible.** Creation is a qualitative reading, which knots a far side adds, and it does not carry the number of
  solutions. Whether it carries any part of what counting needs is open.
- **Contradiction is visible.** On both glues the class that makes the space contradictory is told apart from every other. That is the
  class the knot's three-fold spaces use.
- **Doctrine.** Everything here is invariant under relabeling lines and points; the spanning tree only names the classes.

## Literature

- **Classical.** Switching classes of signed graphs and the action of the graph's automorphisms on them (Zaslavsky).
- **Ours.** The theorem this inverts (SWITCH-PROOF), the placements (SWITCH-READ), the glues and the engine (TRISUM-READ,
  HANDLE-COUNT, CHAIN-TRANSFER, PENDANT-LINE), three-fold spaces (THREEFOLD-SPACES).
- **New here.** The computations, the growth of the blindness, and the Pfaffian class's own block.

## Stress test

The epic's stress test is ticket B: one size past ticket A, it ran in the background (`docs/LONG_RUNNING.md`, SWITCH-COMPLETE-S1) and
was then checked by ticket B's own script. It overturned the reading the smallest glue suggested, that creation is nearly complete
up to symmetry, before anything was published. The S1 run computed both 10-line glues, seeds 6 and 36, which are isomorphic, and got
the same statistics on both; it also reproduced ticket A's 512 blocks class by class.

## Correction (2026-11-08)

- **The count of 12-line glues.** The next step and ticket B's limits said "the four 12-line glues"; TRISUM-READ has five (seeds
  1, 192, 240, 246 and 300), and `CONTRA-READ-20261108-001` tested all five. Only the count changes; the closed ticket note and the
  ledger keep their wording (`docs/CORRECTIONS.md`).

## Pending

- **Still open from earlier epics.** As listed in SWITCH-READ's ledger.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — is the glue block a complete switching invariant? | **Status:** Successful | Answered: no, and less so as the glue grows |
| Local direction — what native creation sees of a signing | Continue | Whether it always singles out the contradictory class is open and testable |
| Broader exploration — native creation against counting | Obstruction learned | Creation between glue lines does not determine the count |
| Long-term goal — G4 Emergence lives in handles | Capability gained | What native creation reads of a signing is now located on both sides |

**Corrections:** none. The smallest glue's near-completeness was caught by the stress test before it was published.
**Goals:** G4 checkpoint (capability gained); G3 noted (creation does not read the count).
**Assumptions:** none added or changed.
**Stress test:** done, as ticket B: one size past changed the answer.

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Does creation always single out the contradictory class? | 2/3 — Substantial | 2/3 — Testable | The five 12-line glues (corrected from "four", 2026-11-08), pruned to classes matching the Pfaffian rows → a sharing class, or a proof attempt | Selected · done (`CONTRA-READ-20261108-001`) |
| 2 | Where nothing creates | 1/3 — Incremental | 3/3 — Ready | Compare the 190 empty classes with the rest → a characterization | Alternative · deferred |
| 3 | What of counting creation carries | 2/3 — Substantial | 1/3 — Stated | Pose which counts a block could fix → a test | Alternative · deferred |

1. **The contradictory class.** If the class whose plain spaces are three-fold always has a block of its own, native creation reads,
   from the glue with one line removed at a time, whether the whole signed glue is contradictory: emergence reading where the
   contradiction lives, which is G4's question. A counterexample would bound what creation sees. The test is cheap, since only
   classes whose rows match the Pfaffian class's rows need to be followed.
2. **The empty classes.** A characterization would say exactly what makes creation blind, but it describes the blindness rather than
   extending what creation reads.
3. **Counting.** Creation does not carry the count; whether it carries a parity or a sign is not yet a precise question.
