# Knot laboratory

Standard-library tools for testing the logical knot described in
[INTUITIONS.md](../../INTUITIONS.md). Every verdict is computed from the set of
allowed states, so writing the same constraints differently cannot change it.
Python 3.9 or later; nothing to install.

Names such as `KNOT-LOOPS-20261019-001` in the code and output are record
labels from our private research log. [FINDINGS.md](../../FINDINGS.md) maps
them to what is published here.

From the repository root:

```bash
PYTHONPATH=tools python3 -B -m knotlab demo
PYTHONPATH=tools python3 -B -m knotlab worlds
PYTHONPATH=tools python3 -B -m knotlab presence
PYTHONPATH=tools python3 -B -m knotlab patterns
PYTHONPATH=tools python3 -B -m knotlab competition
PYTHONPATH=tools python3 -B -m knotlab rings
PYTHONPATH=tools python3 -B -m knotlab holonomy
PYTHONPATH=tools python3 -B -m knotlab depth
PYTHONPATH=tools python3 -B -m knotlab choice
PYTHONPATH=tools python3 -B -m knotlab space
PYTHONPATH=tools python3 -B -m knotlab check --cnf "~A ~B c" --loops A B --contact c
PYTHONPATH=tools python3 -B -m knotlab check --cnf "w ~A ~B; ~w ~C d" \
  --loops A B C --contact d --witnesses w
python3 -B -m unittest tests.test_knotlab
```

Separate clauses with `;` and negate with `~`. A `-` also negates, but then
pass the clauses as `--cnf="-A -B c"` so the shell argument is not read as an
option. Add `--json` to `check` for machine-readable output.

Erasure is read as forgetting, the canonical reading since 2026-10-19: a knot
is constrained as a whole and unconstrained in every part. Pass
`--erasure absence` to `check`, or `erasure="absence"` to `check_knot`, for
the earlier reading, in which a loop's variable is its presence.

## What it computes

- `relations.py`: the allowed states of clauses with witnesses quantified
  away; shadows (the relation seen on fewer variables); erasure (fixing a loop
  to absent); majority closure, which holds exactly when a 2-CNF with witnesses
  can define the relation; closure under AND, which holds exactly when
  requirements (Horn clauses) can; and the narrowest clause width that defines
  it without witnesses.
- `knots.py`: the K1–K3 check under either reading of erasure, with a plain
  explanation of each failure; the atom; and the witness chain that binds any
  number of loops using clauses of exactly three literals.
- `loops.py`: loops written with 2-clauses (implication loops and
  equal/unequal loops), how much of them survives, and the equal/unequal
  signature of two points as a witness of the interior.
- `executor.py`: compares checking each loop's guard always with checking it
  only while the loop runs, and reports when the second reading supplies an
  input.
- `examples.py`: reference cases with their expected verdicts; `demo` exits
  nonzero if any verdict changes.
- `worlds.py`: forced worlds, the least world that requirements leave given
  what is present, computed by linear propagation; which present things are
  essential to a result; trees and open-ended threads of atoms; gates and
  addition carried on two rails, each bit as which of two things exists; the
  ways of making open distinctions that reach a target; minimal worlds under
  choice; and the rebuilding of any three-place relation from atoms and
  distinctions. `worlds` runs these checks and exits nonzero if one changes.
- `presence.py`: the retired exploration of where a loop's presence comes
  from, under the absence reading. Static loops collapse to
  one bit. Under an update, copy rings and inverter rings are running (on a
  cycle of length two or more) or frozen. Two rings and a contact bit are
  tested under four contact rules over every initial state. `presence` runs
  these checks.
- `patterns.py`: the original post's questions. It computes emergent
  information (what a whole rules out that its pairs do not), controllers (a
  variable that changes how two others relate), and patterns unconstrained in
  every part. It also builds parity and its width-3 chain of named matches,
  and entwinement under the forgetting and absence readings of erasure.
  `patterns` runs these checks. Two further functions are checked in the
  tests: co-information, the statistical measure of synergy, and the states
  that break the fewest clauses, which is how competing preferences allow
  states ([INTUITIONS.md](../../INTUITIONS.md#43-knots-from-competing-pairs), lesson 4.3).
- `choice.py`: whether the base has real alternatives. It covers:
  - the 34 two-loop knots;
  - open variables;
  - negating variables;
  - closure under OR, which is a requirement read with the other value as
    "exists";
  - minimal worlds given some values, under either reading.

  `choice` runs these checks.
- `space.py`: whether contact structure becomes space-like. It computes:
  - free sets, which form the system's shape: a simplicial complex whose
    sets are the ones a family of assignments shatters, in learning-theory
    terms;
  - bonds, the knots inside a system;
  - ties, constrained pairs;
  - the shape's holes, as homology over GF(2);
  - the composite of two bonds that share a variable;
  - the smallest bond joining two variables.

  `space` runs these checks.
- `competition.py`: both readings of rules that cannot all hold
  (epic `KNOT-COMPETITION-20261019-001`). It covers:
  - the states that agree-or-differ preferences allow under the strict
    reading (break no rule) or the competition reading (break the fewest);
  - the frustrated triangle;
  - which knots are least sets of a sum of terms on pairs;
  - the separation of each pair, the size of the smallest bond or tie
    containing it;
  - strips and rings of triangles counted per triangle or per pair.

  `competition` runs these checks.
- `rings.py`: which knots remember a loop (epic `KNOT-LOOPS-20261019-001`). It
  covers:
  - a link's transfers, the (witness in, witness out) pairs it allows for each
    value of its other variables;
  - rings of copies and networks with one copy per edge, witnesses forgotten;
  - the ring theorem's excluded patterns and memory kind;
  - how many bits a composite keeps.

  `rings` runs these checks.
- `holonomy.py`: what networks of permutation contact remember (epic
  `HOLES-COHOMOLOGY-20261019-001`). It covers:
  - whether a network's permutations are allowed together, read off the
    label-extended covering, and the holonomy's orbit sizes;
  - the relation on loop selectors of a bouquet, and the nerve of the
    holonomies' fixed-point sets that is its shape;
  - knots among loops, with the star transpositions as the smallest;
  - the memory of uniform group contact, and when two-witness linear
    reasoning over Q, Z or F_p misses an impossible network.

  `holonomy` runs these checks.
- `depth.py`: how deep a network's hole is (epic `DEEP-HOLES-20261020-001`). It
  covers:
  - the hole rank of one knot's scope in the complex of partial solutions
    (every non-atom knot has one);
  - the toggle width and cutwidth of a graph, and a few small cubic graphs by
    name;
  - the depth of an impossible charge network over a field: one knot's size
    when the field computes in the charge group, the toggle width otherwise,
    which is cutwidth + 1 on graphs of maximum degree at most 3.

  `depth` runs these checks.

## Limits

Relations are enumerated exhaustively, so keep the visible and witness
variables together to about twenty. Forced worlds are computed by propagation
and scale to hundreds of thousands of rules, while `choices_reaching` tries
every way of making the open distinctions and doubles in cost with each one.
The tools test definitions on finite cases; a uniform claim still needs a
proof or a cited theorem.
