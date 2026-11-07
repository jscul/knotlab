# Reading the atoms through glue

Status: Proved (the rule reads every Fano tree whose atoms have at most four cuts; exact computation on 191 spaces, with an obstruction
for the yes/no creation relation)

Ticket `GLUE-READ-20261106-001C`, 2026-11-06.

## Question

- **The goal.** CHAIN-TRANSFER C's twin rule reads the atoms of Fano trees. Can one rule read the atoms, and so the genus, of every
  three-fold space, plane glue included?
- **What it must survive (ticket B).** Two disturbances:
  - a doubled-square line can join an atom's twin class;
  - an atom that emits into a planar brace splits by the points of its emitted line, its classes differing only on glue lines.

## Dependencies

- **`GLUE-READ-20261106-001B`.** The 191 spaces and their exact creation maps (`maps.json.gz`, bound by hash), and the two disturbances.
- **`GLUE-READ-20261106-001A`.** The receiving-cut law.
- **`CHAIN-TRANSFER-20261106-001C`.** The twin rule for Fano trees.

## The rule (two stages)

1. **Twins.** Two lines are twins when they create at each other and at the same other lines. The lines in twin classes of two or more
   are the atom lines.
2. **Atom twins.** Two atom lines are atom twins when they create at each other and at the same other atom lines. Glue lines are
   ignored. Their classes are read as the atoms.

**Why the second stage.** By ticket B, the split classes of an atom differ only on glue lines, so comparing on atom lines alone heals the
split. A joined doubled-square line stays inside its atom's class.

## Theorem (Fano trees)

**On every Fano tree whose atoms have at most four cuts, the two-stage rule returns the atoms.**

*Proof.*
- **Twins are atoms.** By CHAIN-TRANSFER C, the twin classes are the atoms.
- **No line is lost.** Each atom keeps at least three lines, so every line is an atom line.
- **So the stages agree.** The second stage compares on all lines, which is the first stage. ∎

Check 1 confirms the agreement on the 20 Fano trees among the 191 spaces.

## Results (computed)

| Spaces | Two-stage rule reads the atoms | Plain twin rule | Source rule counts them |
| --- | --- | --- | --- |
| Census, Fano trees | 17 of 17 | 17 | 17 |
| Census, plane glue | 93 of 93 | 83 | 93 |
| Census, census 58 | 1 of 1 | 1 | 0 |
| Random, Fano trees | 3 of 3 | 3 | 3 |
| Random, plane glue (18 to 38 points) | 54 of 77 | 36 | 67 |

- **Extra lines.** The only lines the rule adds to an atom are doubled-square lines.
- **Where it fails (23 random spaces), it does one of two things:**
  - merges atoms that meet one planar brace (19);
  - drops a line of an atom (4).

## An obstruction for the yes/no relation

**In 15 of the 23 failing spaces, two lines of different atoms create at each other, and at exactly the same lines, and are created at by
exactly the same lines.**
- **A symmetry.** Exchanging the two lines then preserves the yes/no creation relation.
- **Its consequence.** Any rule that reads only whether creation occurs, and treats lines alike, must return a partition that the exchange
  preserves. The atom partition is not preserved: the exchange moves a line from one atom to another.
- **So.** No such rule can return the atoms of those spaces.
- **Where it happens.** In every one, the atoms involved meet one planar brace.
- **Not in the census.** No census space has such lines.

## What the far sides carry (check 4)

- **They separate.** Which far side creates separates every two lines of different atoms, in all 191 spaces. The information is there.
- **They also vary inside atoms.** Census 6 responds to the deeper relations that ticket A shows never decide whether creation occurs. So
  twins far side by far side read no space's atoms, not even a Fano tree's.

## Answer

- **The rule reads the census.** The two-stage rule reads the atoms, and so the genus, of every three-fold space of up to 26 points in
  BRACE-TREE C's census, and of every Fano tree whose atoms have at most four cuts (proved).
- **It does not read every three-fold space.** Through a planar brace that several atoms meet, the yes/no creation relation can fail to
  tell their lines apart, so no rule based on it can.
- **What would.** Reading every three-fold space needs a rule that uses which far side creates, where the distinction is kept.

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings (ticket B's maps included); upstream proofs Proved | pass |
| 1 | On Fano trees the rule is CHAIN-TRANSFER C's | 20 of 20 |
| 2 | The rule on 191 spaces, against the plain twin rule and the source rule | the table above |
| 3 | Failures and the obstruction | 15 indistinguishable merges, 4 distinguishable merges, 4 dropped lines; no census space obstructed |
| 4 | Far sides | separate every cross-atom pair in all 191 spaces; twins far side by far side read no space |

## What this does not establish

- **A rule for every three-fold space.** None is found. One that uses the far sides is open.
- **Counting only.** Counting the atoms is a weaker goal. The source rule counts them in 67 of the 77 random glued spaces, but it fails on
  Fano trees of six atoms (CHAIN-TRANSFER B).
- **Larger spaces.** Nothing beyond 38 points.
- **Non-Fano handles.** The census-58 handle is not read as an atom.

## Novelty

- **New here.** The two-stage rule, its record on 191 spaces, and the obstruction for the yes/no relation.
- **The argument.** That an automorphism of the relation forbids an invariant rule from separating the lines it swaps is elementary.
