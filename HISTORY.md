# History

Corrections are added here as new entries. Earlier versions stay in the git
history. A withdrawn result keeps its files, with a notice explaining the gap.

## 7 November 2026: publication at epic closure

- Publication now runs from the workspace's epic-closure command, in place
  of a commit hook that was never installed. scripts/install_hook.py is
  removed.
- jscul.dev follows through a GitHub Actions workflow in its own
  repository. publish.py starts it after each publication, and it also runs
  every six hours.
- In data/lines.json, the far-side and acts-as-one epics are placed under
  native creation, and the four epics on the sphere's count under depth and
  proof complexity.

## 6 November 2026: automatic publication, and the tickets

- New epics are now published here automatically when they close in our
  research workspace. [scripts/publish.py](scripts/publish.py) copies their
  committed records and tickets and the documents in docs/, rebuilds the
  generated files, runs the tests and pushes, then updates jscul.dev.
- [tickets/](tickets/) holds the tickets of every published folder and epic,
  566 so far, so the archived epic-closure checks can run here.
- The generated files come from [scripts/build.py](scripts/build.py) and
  [data/](data/): the lines of work, the ranking tiers, the notes and the
  pending qualifications, each now entered once. The build reproduced the
  earlier RESULTS.md and RANKING.md exactly, apart from one new sentence in
  RESULTS.md saying that new epics appear automatically.
- [tests/test_records.py](tests/test_records.py) checks that the generated
  files are current and that every link and ticket is there.
  [tests/test_curation.py](tests/test_curation.py) fails when a THEORY.md
  claim cites a superseded or qualified record without saying so. GitHub
  Actions runs the tests on every push.
- [requirements.txt](requirements.txt) lists the libraries some archived
  checks need.

## 6 November 2026: the theory page, and four more epics

- [THEORY.md](THEORY.md) states the program's thesis and its main claims: 60
  claims in nine sections, each with one label (premise, proved, checked,
  conjecture, reading or open), its date and links to its evidence. The
  pending qualifications appear on the claims they affect:
  `KNOT-COMPOSE-20261101-001-D001`, `PHASE-HALO-20261103-001-D001` with
  `FACE-CLAIM-20261103-001-D003`, counted length
  (`SELECT-COUNT-20261101-001-D002`), and the selection note's erratum.
  [tests/test_theory.py](tests/test_theory.py) checks its labels, evidence and
  links.
- [RESULTS.md](RESULTS.md) adds the four epics recorded on 5 and 6 November,
  after the full record: `TWO-BIT-SCREEN-20261105-001`,
  `PENDANT-LINE-20261106-001`, `CHAIN-TRANSFER-20261106-001` and
  `GLUE-READ-20261106-001`. Their [proofs/](proofs/) and
  [research/](research/) folders are copied byte for byte from our workspace.
  The record now holds 178 current results and 5 superseded ones from 131
  epics.
- [docs/KNOT_INTUITION.md](docs/KNOT_INTUITION.md) now matches our workspace,
  with the entries for those epics and a note that the brace-tree source rule
  fails at six atoms.

## 6 November 2026: review clarifications in the knot-group counting note

[The note](notes/knot-group-counting/) now covers the three points an
independent review asked for before submission. None changes a result.

- **Interpolation cost.** A paragraph in the S₄ hardness proof bounds the bit
  length of every number in the interpolation. The reduction is a
  polynomial-time Turing reduction with K queries.
- **Mixed-exponent kernels.** The polynomial side counts lifts through an
  abelian kernel with cyclic factors of different orders by the Smith normal
  form. It does not assume that a primary part is free over a single Z/p^a.
- **Crossing signs.** The Wirtinger rule now states the sign of each
  crossing. Individual signs matter, except for involutions. Reversing the
  convention at every crossing at once only inverts each colouring.

## 5 November 2026: authorship and the Rowell note for arXiv

- The three notes and [CITATION.cff](CITATION.cff) now name John Cullen as
  the author, in place of "Prespatial Labs".
- [notes/knot-group-counting](notes/knot-group-counting/) is now the version
  prepared for arXiv. A first-page footnote states the AI assistance, and the
  evidence section points to this repository. One citation was corrected:
  Matveev's 1987 paper is "Generalized *surgery* of three-dimensional
  manifolds and representations of homology spheres". All 17 references were
  checked against their published records, and the note's replay of its ten
  cited checks passes from this repository.
- The counting note's footnote now points to this repository.

## 5 November 2026: the ranking

- [RANKING.md](RANKING.md): the proved results since 19 October 2026 ranked
  in five tiers by significance to the theory, from what the theory stands on
  to local proofs kept visible. Computed results and conjectures are left out.

## 5 November 2026: the full record

- [RESULTS.md](RESULTS.md): every result recorded since the knot test K1–K3
  became canonical on 19 October 2026, with the date it was recorded. That is
  166 current results and 5 superseded ones from 127 epics, plus 5 notes. Four
  current results and one note carry a pending qualification, stated in their
  entries.
- [docs/](docs/): the documents that define the working perspective,
  unchanged.
- [proofs/](proofs/), [experiments/](experiments/), [artifacts/](artifacts/)
  and [research/](research/): every committed record from those epics, copied
  byte for byte from our workspace. Work in progress that had not been
  committed is not included.
- [INTUITIONS.md](INTUITIONS.md) and [FINDINGS.md](FINDINGS.md) now point to
  the full record.

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
