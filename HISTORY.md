# History

Corrections are added here as new entries. Earlier versions stay in the git
history. A withdrawn result keeps its files, with a notice explaining the gap.

## 5 November 2026: first release

- [INTUITIONS.md](INTUITIONS.md) and [FINDINGS.md](FINDINGS.md), written for
  this repository from the program's working notes.
- [tools/knotlab](tools/knotlab/) and its 80 tests, unchanged except that
  references to our private working notes now point to INTUITIONS.md.
- Five Lean files, unchanged, checked with Lean 4.32.2 by
  [lean/check.py](lean/check.py).
- Three notes:
  - *The Nullstellensatz degree of Tseitin formulas is the toggle width*,
    draft of 20 October 2026;
  - *Counting 2-colourings of 3-regular hypergraphs with Pfaffian incidence
    graphs*, draft of 31 October 2026;
  - *Counting homomorphisms from knot groups to solvable groups can be
    #P-hard*, draft of 26 October 2026.

  The sources are unchanged and the PDFs were rebuilt from them. Two check
  drivers were adjusted to run outside our workspace: `run_all.py` uses the
  interpreter that runs it, and the usage line of `independent.py` names its
  dependencies.

Before release, every check listed in [README.md](README.md) was run from this
repository and passed.
