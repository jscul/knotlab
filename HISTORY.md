# History

Corrections are added here as new entries. Earlier versions stay in the git
history. A withdrawn result keeps its files, with a notice explaining the gap.

## 8 November 2026: general-resolution bounds for Sperner's lemma were known

- SPHERE-WIDTH-20261107-001-D002 said that for Itsykson, Malova, Oparin and
  Sokolov's Sperner CSP "only tree-like size was known". An outside
  prior-work check found Stefan Dantchev's "On the complexity of the Sperner
  lemma" (CiE 2006, Lecture Notes in Computer Science 3988, 115–124). It
  reduces the pigeonhole principle to Sperner's lemma and shows that the lemma
  has no short constant-depth Frege proofs. Resolution is such a system, so
  superpolynomial general-resolution lower bounds for Sperner formulas date
  from 2006.
- The record now carries a pending qualification. New, as far as found, are
  the tight bounds: width Θ(m), and size 2^Θ(m) from COUNT-NOTE-20261107-001,
  with their direct proofs.
- Unchanged: every proof and bound of the sphere and grid-Sperner records.

## 8 November 2026: the knot's amplitude with non-planar glue

- The card "The knot's amplitude and signs" and
  THREEFOLD-AMPLITUDE-20261030-001-D001 gave the knot's factor on every
  three-fold space as 5 per Fano atom times Tutte's tree-trinity number per
  planar piece of glue. That holds when the glue is planar. The proof covers
  doubled squares, planar pieces and three cubes glued along a square, and the
  record's own computations show that a non-planar piece contributes an
  amplitude that depends on how it is glued: 13 or 14 for prisms of sizes 2, 3
  and 3 ([computation](proofs/THREEFOLD-AMPLITUDE-20261030-001B/THREEFOLD-AMPLITUDE-20261030-001B-P001_the_amplitude_by_computation/proof.md)).
- The card "Counted length" and SELECT-COUNT-20261101-001-D002 repeated the
  same formula for the glue's part, so both cards now state the general
  product, and both records carry pending qualifications.
- Unchanged: 5 per Fano atom on every three-fold space, the product over the
  pieces ([one amplitude](proofs/THREEFOLD-AMPLITUDE-20261030-001C/THREEFOLD-AMPLITUDE-20261030-001C-P001_one_amplitude_for_every_non_colourable_cubic_system/proof.md),
  Corollary 5), and every value computed.

## 8 November 2026: the pinwheel's coordinate-free rule was already known

- Kenyon and Stephenson's "Shape convergence for aggregate tiles in conformal
  tilings" (Proc. Amer. Math. Soc. 147, 2019) already gives the pinwheel a
  coordinate-free subdivision rule. Each tile there has four designated
  corners, the fourth at the midpoint of the long leg. They also prove that
  the geometry returns from the combinatorics alone: in the conformal tilings,
  clusters of tiles converge in shape to the Euclidean triangles ([decision note](research/PINWHEEL-NATIVE-20261107-001/pinwheel_native.md)).
- PINWHEEL-NATIVE-20261107-001-D001 now carries a pending qualification. The
  rule and its census of T-junctions are known in substance; new are the
  rule's form on knots and distinctions, its eleven-label alphabet and its
  exact check. The note's reading of the irrational angle was also corrected:
  the angle is a limit property of the law, not only of a drawing.
- Unchanged: the exact regrowth at levels 0–7, the census, the Whitney step,
  and the reading of labels within radius 2, which was not found in prior
  work.

## 7 November 2026: census 6 depends on how it is glued

- The creation test glues each census far side to a gluing line in the order
  in which the line's points are written. K4^(3), the Fano plane and census 58
  give the same verdict in every order. Census 6 does not: only two of the six
  orders are equivalent under its symmetries, and its verdict changed with the
  order in 8,046 of 11,552 sampled pairs ([proof](proofs/GENUS-READ-20261107-001A/GENUS-READ-20261107-001A-P001_census_6_depends_on_how_it_is_glued/proof.md)).
- Counting census 6 over its three gluings, every ordered pair of lines of a
  Fano atom in a Fano tree gets the same far-side vector ([proof](proofs/GENUS-READ-20261107-001B/GENUS-READ-20261107-001B-P001_natively_a_fano_atom_is_homogeneous/proof.md)). The
  four-step rule of FAR-READ-20261106-001-D002 then cuts every atom of six or
  seven lines, so its reading of every computed space depended on how lines
  were written. That record, and the sentence of FAR-READ-20261106-001-D001
  about census 6, now carry pending qualifications.
- Unchanged: every statement about whether creation occurs, and what K4^(3),
  the Fano plane and census 58 show. They still separate atoms where whether
  creation occurs cannot ([measurement](proofs/GENUS-READ-20261107-001C/GENUS-READ-20261107-001C-P001_native_far_sides_through_plane_glue/proof.md)).

## 7 November 2026: published entirely from the research workspace

- Everything in this repository now comes from our research workspace,
  which is the single source of truth for it and for jscul.dev. The pages,
  notes, Lean files, knot laboratory, tests and data inputs are written there
  and published with the records.
- The publisher moved into the workspace, so scripts/publish.py is removed
  here. [data/published.json](data/published.json) records the digest of
  every published file. A file edited here directly makes the next
  publication stop and report it instead of overwriting it, and
  `tests/test_records.py` reports it too.

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
  research workspace. [scripts/publish.py](https://github.com/jscul/knotlab/blob/ac8eb7c/scripts/publish.py) copies their
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
