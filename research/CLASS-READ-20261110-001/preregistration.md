# Pre-registration: reading the class, not the bit

Epic `CLASS-READ-20261110-001` (backlog B122, G15), written on 2026-11-10 before any run, at the coordinator's go-ahead.

## The question

`GATES-20261110-001` found that cuts and names read only monotone functions of the stored acting bits. A leaf stores more than whether
it acts: its class, one of four. After that run, some name networks were seen to read whether a leaf's class lies on one line through its
acting class (classes (1,0) and (0,1) there), a reading that is not monotone in the class bits. That observation is post hoc; this epic
freezes it as a prediction and re-tests it on networks not used before, and asks what functions of the stored classes the networks read.

## Words

The four classes of a leaf form an affine plane over F2, with one distinguished point, the acting class ω (the torus's unsatisfiable
class). A **line through ω** is {ω, ω + v} for one of the three nonzero homology directions v. Networks are as in `GATES-20261110-001`
(closed components, three parity names, one top constraint of 10 kinds, read O = 1 when unsatisfiable), now read as functions of the
classes themselves.

## The networks, frozen (none used in `GATES-20261110-001`)

- **G1.** One leaf, the thin torus (3,2,2) closed, in each of its four classes; three names forming a multiset of its 15 point pairs; the
  10 tops: 6,800 networks, each read as a set of classes (those where O = 1).
- **G2.** Two leaves, both thin tori (3,2,2) closed; y_0 a pair of the first, y_1 a pair of the second, y_2 a pair of either; the 10 tops:
  67,500 networks, each read on the 16 class pairs.

## Predictions

- **R0 (proved, from `GATES-20261110-001` P2).** Every reading is 1 wherever some leaf is in its acting class.
- **R1 (the re-test of the parity reading).** Some network of G1 reads exactly a line through ω.
- **R2.** For every pair (t, t') of non-acting classes of the two leaves, some network of G2 reads exactly the class pairs where a leaf
  acts together with (t, t'): a joint minterm on the nine non-acting pairs.
- **What R2 would give.** A network made of independent parts has no satisfying state exactly when one part has none, so it reads the OR
  of its parts' readings. With R2, every function of the two stored classes that is 1 wherever a leaf acts is the OR of joint minterms and
  is read by one network: every function of the non-acting classes, each leaf a three-valued digit.
- **Failure line.** A reading that is 0 where a leaf acts (contradicts R0: a code or proof error).

## Stop rule (one epic)

The answer is R1's and R2's verdicts and the count of distinct readings on the non-acting pairs (of 512 possible). Other leaves and cut
leaves with names inside (backlog B123) are recorded, not run. The report says plainly whether these readings read stored memory or
something the law fixes.

Assumptions in force: A20, A21, A46, A47, A49, A50, A52. The census is expected to take under ten minutes; a run past that is registered in
`docs/LONG_RUNNING.md` before relaunch.
