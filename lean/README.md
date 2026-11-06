# Lean proofs

Five single-file proofs in core Lean 4: no Mathlib, no imports. The toolchain
is pinned in [lean-toolchain](lean-toolchain) (Lean 4.32.2). With
[elan](https://github.com/leanprover/elan) installed, run from this folder:

```bash
python3 check.py
```

It compiles each file and prints the axioms each main theorem depends on. All
of them use only `propext` and `Quot.sound`, plus `Classical.choice` in three
files. No file contains `sorry`.

| File | What it proves | See |
| --- | --- | --- |
| [ForgettingKernel.lean](ForgettingKernel.lean) | The knot test with erasure read as forgetting, on three variables. The atom and parity are knots; a common hub and loops tied directly are not. A knot implies no clause on fewer than all its variables. A majority-closed relation whose pairs are free is full, so no 2-CNF defines a knot. Chains of three-literal clauses with witnesses define parity on any number of variables. | [INTUITIONS §2–3](../INTUITIONS.md#2-the-knot-test) |
| [KnotKernel.lean](KnotKernel.lean) | The earlier "absence" reading of the test, in which only the atom is a knot. The witness chain of three-literal clauses defines the atom on any number of loops. It also diagnoses relations that earlier versions of the program wrongly accepted. | [INTUITIONS §3](../INTUITIONS.md#3-pairs-cannot-make-a-knot-three-places-can) |
| [CompetitionKernel.lean](CompetitionKernel.lean) | Under competition (least-violation states), pairwise rules make exactly the four not-all-equal knots on three variables and none on four or more. With hidden variables they make every relation on three variables that allows some state. Under conjunction they make no knot. | [INTUITIONS §7](../INTUITIONS.md#7-knots-from-competing-pairs) |
| [RingKernel.lean](RingKernel.lean) | The ring theorem: a ring of knots excludes a pattern exactly when every transfer is a permutation and an odd number swap. Only parity has all its transfers permutations. | [INTUITIONS §8](../INTUITIONS.md#8-which-knots-remember-a-loop) |
| [LoopNerve.lean](LoopNerve.lean) | Loops with permutation contact. The shape of the loops that can be switched on together is the nerve of the holonomies' fixed-point sets, and every simplicial complex is such a nerve. Free contact binds no loops. A knot among k loops needs k + 1 witness values. | [INTUITIONS §5, §8](../INTUITIONS.md#8-which-knots-remember-a-loop) |

The statements are finite or are proved for every length by induction. The
uniform arguments that extend the three-variable statements to all relations
(Schaefer 1978; Baker and Pixley 1975) are cited in
[INTUITIONS.md](../INTUITIONS.md), not formalized.
