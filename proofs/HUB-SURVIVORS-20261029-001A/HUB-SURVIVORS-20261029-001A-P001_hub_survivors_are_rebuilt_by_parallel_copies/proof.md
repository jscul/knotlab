# Hub survivors: which knot classes are rebuilt by hub gadgets of their own copies

Status: Proved

Ticket `HUB-SURVIVORS-20261029-001A`, 2026-10-29.

## Standard statement

The 34 relations on three bits in which every two coordinates are unconstrained, other than the full cube, form 16 classes under
permutations of the coordinates. A *hub gadget* of such a relation K joins copies of K, each with any order of its coordinates. Three
variables (the legs) lie in one copy each, every other variable lies in at least two distinct copies, no copy repeats a variable, and
the copies are connected. Its relation is the projection onto the legs. K is *rebuilt* when some gadget of at least two copies gives a
coordinate permutation of K.
- Copies that share all three variables intersect. From some classes this reaches a parity relation or an equality between two
  coordinates; from others it reaches neither.
- Among gadgets of at most six copies, exactly seven classes are rebuilt. The two parity classes are rebuilt from three copies.
  From four copies come the two "x or (y ≠ z)" classes, the two three-excluded classes with a symmetry of order two, and twisted
  not-all-equal.
- The two monotone atoms, excluding only 000 or only 111, are never rebuilt.

## Nearest known result

- **In the repository.** `GEOMETRY-LAW-20261029-001A`: without hubs (every variable in at most two copies) only parity is rebuilt,
  and the other classes lose excluded tuples. `HUB-SURVIVORS-20261029-001B`: not-all-equal is rebuilt at seven copies, by the
  punctured Fano plane, and not below.
- **Outside.** pp-definability and Holant clones describe which relations gadgets can define. Gadgets with hubs and constants define
  every relation from not-all-equal (Schaefer; `SURFACE-GLUING-20261024-001B`). None of these asks which relation is rebuilt by
  gadgets of its own copies without constants.
- **Classification.** No overlap found (candidate local delta).

## Setting

- **Classes.** Named by their excluded sets up to coordinate permutation. Two of them, "x or (y ≠ z)", are {000, 011} and {001, 111}.
  Twisted not-all-equal is {001, 110}, not-all-equal with one coordinate negated.
- **Parallel copies.** Two copies on the same three variables, in placements P and Q, impose P ∩ Q. Their excluded set is the union
  of theirs, so parallel copies can only add excluded tuples, and the union may contain adjacent tuples.
  - Gluing along one shared variable keeps excluded tuples pairwise non-adjacent and can only dilute them
    (`SURFACE-GLUING-20261024-001B-P001`, Lemmas 2 to 4).
  - Parallel copies need hubs: each shared variable lies in at least two copies, and in at least three as soon as a third copy
    reaches it.

## Theorem 1 (what parallel copies reach; computation)

Close each class's set of placements under intersection (check 2).
- **"x or (y ≠ z)" and the three-excluded classes with a symmetry of order two** reach a parity relation. For example
  {000, 011} ∪ {000, 101} = {000, 011, 101}, and adding {000, 110} gives the even class.
- **Twisted not-all-equal** reaches an equality on two coordinates: {001, 110} ∪ {100, 011} excludes exactly the tuples with
  x₁ ≠ x₃.
- **The remaining classes** reach neither:
  - "x or (y = z)" ({001, 010} and {011, 101}) reaches only the no-lone-value class;
  - not-all-equal and the no-lone-value classes are symmetric and closed;
  - the asymmetric atoms reach "x or (y = z)" and the no-lone-value classes, but no parity relation and no equality.

## Theorem 2 (the census; computation)

Exhaustive over hub gadgets of three to six copies, every shape (3, 11, 104 and 1065 shapes) and every placement (check 4):
| class (excluded set) | rebuilding shapes with 3 / 4 / 5 / 6 copies |
| --- | --- |
| parity, even class {000, 011, 101, 110} | 2 / 2 / 30 / 186 |
| parity, odd class {001, 010, 100, 111} | 2 / 2 / 30 / 186 |
| twisted not-all-equal {001, 110} | 0 / 2 / 16 / 179 |
| x or (y ≠ z) {000, 011} | 0 / 1 / 8 / 77 |
| ¬x or (y ≠ z) {001, 111} | 0 / 1 / 8 / 77 |
| three excluded {000, 011, 101} | 0 / 1 / 10 / 93 |
| three excluded {001, 010, 111} | 0 / 1 / 10 / 93 |

No gadget of at most six copies rebuilds any of the other nine classes:
- the atoms {000}, {001}, {011} and {111};
- not-all-equal {000, 111};
- "x or (y = z)": {001, 010} and {011, 101};
- no lone one {001, 010, 100} and no lone zero {011, 101, 110}.

**Smallest gadgets.** Each survivor except parity is rebuilt by four copies, and every such gadget contains copies in parallel:
- **"x or (y ≠ z)".** Legs a, b on one copy with a hub d. Two further copies are in parallel on (d, e, f), and the third leg's copy is
  (c, e, f).
- **The three-excluded classes.** One leg on each of three copies. Three hubs d, e, f each lie in three copies, and a fourth copy
  holds (d, e, f).
- **Twisted not-all-equal.** Legs a, b on one copy with a hub d that lies in all four copies. Two copies are in parallel on
  (d, e, f), and the third leg's copy is (c, d, e).

## Theorem 3 (the monotone atoms are never rebuilt)

Let K exclude only 000 (OR), or only 111 (NAND). No hub gadget of at least two copies of K is rebuilt; its relation is full.

*Proof.* A copy holding all three legs has no hidden variable, so it is disconnected from the others unless it is the whole gadget.
So in a gadget of at least two copies every copy holds a hidden variable. Setting every hidden variable to 1 (for OR) puts a 1 in
every copy, so every copy is satisfied whatever the legs; for NAND set them to 0. So every leg tuple is allowed. ∎

## Reading

- **What hubs change.** Without hubs, gluing composes in series and only dilutes exclusion, so only parity survives patterns of
  patterns. Hubs let copies run in parallel, which intersects them. When the intersections reach parity or an equality, the knot is
  rebuilt from a small gadget.
- **Not-all-equal.** It survives by a different, global mechanism: its copies on the Fano plane cannot be 2-coloured (ticket B). This
  is why the census of at most six copies does not decide the remaining classes.
- **The two/three reading.** Hubs are equality fan-out, pairwise structure (`docs/COMMON_VERBIAGE.md`, common hub). What they add is
  parallel composition, which pairwise relations alone cannot use to create anything: equalities in parallel are still equalities.
  Applied to three-place knots, it lets their emergence persist across scales.

## Checks

`check.py` (numpy) on the library `hub_lib.py`, with `result.json`:
- **0.** The dependency artifacts are bound by hash.
- **1.** 34 knots in 16 classes.
- **2.** The intersection closures of Theorem 1.
- **3.** The enumeration (lowest unfilled copy first, hidden variables in lexicographic order) gives the same shapes as a full
  canonical enumeration at three, four and five copies (3, 11, 104). The control: ordering the hidden variables by size first finds
  only 7 of the 11 shapes at four copies. That was an error in the first scoping, corrected here.
- **4.** The census of Theorem 2.
- **5.** Every enumerated gadget has a hidden variable in every copy, and neither monotone atom is rebuilt.
- **6.** Controls:
  - gadgets without hubs rebuild only the two parity classes (agreeing with `GEOMETRY-LAW-20261029-001A`);
  - all-equal, which is not a knot, is rebuilt.

## Provenance and novelty

| Result | Where it came from | Novelty |
| --- | --- | --- |
| Theorem 1 | Intersections of coordinate permutations | Elementary, computed |
| Theorem 2 | Exhaustive census | Candidate local delta |
| Theorem 3 | Monotonicity | Elementary |
| The question and its reading | Patterns of patterns with hubs (`HUB-SURVIVORS-20261029-001`) | From the program |

## What this does not show

- That the classes not rebuilt by six copies are never rebuilt: not-all-equal is rebuilt at seven.
- Anything about counts of hidden witnesses.
- The shapes of the survivors' towers beyond the smallest gadgets.
