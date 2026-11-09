# History

Corrections are added here as new entries. Earlier versions stay in the git
history. A withdrawn result keeps its files, with a notice explaining the gap.

## 8 November 2026: one row reads the contradiction only away from two-vertex cuts

- The knot intuition entry for CONTRA-READ-20261108-001 read its result as
  "native creation reads where the contradiction lives", without naming the
  trisum glues it was computed on. On random cubic glues with a class without
  solutions, one row fails to read the removed line's tie at every line lying in
  a two-vertex cut of the incidence graph
  ([decision note](research/CONTRA-PROOF-20261108-001/contra_proof.md)).
- The reading is narrowed to 3-connected glues, where it held on all 18 tested.
- Unchanged: every result of CONTRA-READ-20261108-001.

## 8 November 2026: which way the two-bit census points

- The preliminary record of TWO-BIT-20261108-001 said in its summaries that the
  products of one-bit decorations "escape the known crystals" in 97.7% of the
  classes and that 3,241 "escape every crystal tried". The census means the
  reverse: a known crystal gets through 136,415 of the 139,656 classes, which
  therefore fail, and no crystal tried gets through the other 3,241.
- Unchanged: every count and the stop rule.
- The [decision note](research/TWO-BIT-20261108-001/two_bit.md) and the closure
  ledger now say "lets a crystal through" and "no crystal gets through".

## 8 November 2026: the recurring-lag census counted families twice over

- RECUR-PATH-20261108-001 reported 452 families of paths that compose at
  recurring lags with every contact persistent at every size, 256 of them with
  contacts two apart. Each two-apart family had been listed four times, so the
  counts are 64 two-apart families and 260 in all, and 4,096 (not 16,384) with
  contacts binding at the composing lags.
- Unchanged: every verdict, and the overturn of A34, which needs one family.
  RECUR-PROOF-20261108-001 then proved the 64 at every ring size and length
  ([decision note](research/RECUR-PATH-20261108-001/recur_path.md)).

## 8 November 2026: intermittent composition can pass the gate

- INTERMITTENT-NET-20261108-001 kept the strict reading of composition across
  time, A34 (the far contact binds both ends at every lag), because "the
  contact gate asks for persistence, which intermittent composition fails".
- The gate asks every contact to persist and the composition to survive the
  admitted transports; it does not ask for binding at every lag.
  RECUR-PATH-20261108-001 found 260 families of paths whose contacts all
  persist and which compose at recurring lags, fixed by their own dynamics, at
  every size tested, while under A34 none composes at two sizes. A34 was
  overturned by that challenge's pre-registered rule and replaced by A37.
- The [decision note](research/INTERMITTENT-NET-20261108-001/intermittent_net.md)
  carries a correction section. Unchanged: every count of INTERMITTENT-NET.

## 8 November 2026: native paths with one rule per ring sit at more shapes

- NATIVE-PATH-20261108-001 found no native path with rule 150 on all four
  rings, searching end rings up to 5 cells. Its wider run finds 48, with end
  rings of 6 cells (6/5/5/6) or a middle ring of 8.
- PATH-HYBRID-20261108-001 said that with one rule per ring there is a single
  construction of 16 native paths. That holds for its sweep's two shapes:
  PATH-GROWTH-20261108-001 finds others at 5/6/6/5 and 4/7/7/5.
- PATH-HYBRID-20261108-001 also suggested, as a heuristic, that larger rings
  fail because their cycles grow long. Persistent paths of other families keep
  short cycles at every size and still do not compose, so the reason is open.
- Unchanged: every count at the sizes searched, and that no family of native
  paths survives one more cell
  ([native paths that survive growth](research/PATH-GROWTH-20261108-001/path_growth.md)).

## 8 November 2026: an additive middle ring can remember and transmit

- NATIVE-PATH-20261108-001 found no native path of four rings in three
  restricted families. It read this as a tension: a middle ring must keep its
  own first row and carry the first ring's influence, and "the additive rules
  keep the first row but cancel the influence", so no tested ring did both.
- PATH-HYBRID-20261108-001 found 16 native paths whose middle rings run rule
  150, the additive rule of that epic's first family, between 3-cell shift end
  rings. The same paths with rule 150 on their end rings keep none of their
  contacts, because such an end ring's two cells are equal after one step and
  the contact reads their sum. So rule 150 does both jobs as a middle ring, and
  the paths had failed at their end rings.
- The [decision note](research/NATIVE-PATH-20261108-001/native_path.md)
  carries a correction section. Unchanged: every count of the three searches,
  the light cone, the affine reduction, and the finding that a shift as the
  second middle ring keeps no path's contacts.

## 8 November 2026: the last decoration's forcing route needs every off-law parent to die

- LAST-BIT-20261108-001 said that if every parent collar of a plane obeying
  the last one-bit decoration's law (10101 / 00110) were a pinwheel collar, a
  level-by-level argument would prove that the plane is a pinwheel tiling.
  Pinwheel collars are not enough: the argument repeats one level up only if
  the parents' labelled collars obey the law, so the 50 surviving pinwheel
  collars with labels the law does not list have to die as well.
- Unchanged: every computed count, and the conclusion that the route stalls
  at its first step.
- The [decision note](research/LAST-BIT-20261108-001/last_bit.md) carries a
  correction note; CRYSTAL-UP-20261108-001 tests both kinds of off-law parent.

## 8 November 2026: persistent contacts do compose across time

- PROCESS-CHAIN-20261108-001 said that, at the sizes tested, two contacts
  that each persist across time never compose, and INTERMITTENT-NET-20261108-001
  said that persistent composition remains absent. Both were measured on chains
  with one rule on all three rings and one law at both contacts.
- AFFINE-WIRE-20261108-001 searched affine chains that mix rules and laws and
  found 2,376 in which both contacts persist and the far contact binds the end
  rings at every lag once the far ring can reach it, 430 of them through the
  middle ring's own cells. The smallest runs rule 150 on rings of 3, 5 and 3
  cells. The constructions are verified on their full state spaces.
- The two decision notes,
  [two contacts across time](research/PROCESS-CHAIN-20261108-001/process_chain.md)
  and [intermittent networks](research/INTERMITTENT-NET-20261108-001/intermittent_net.md),
  carry correction sections.
- Unchanged: every count of both censuses, and the result that intermittent
  composition is native only on affine substrates.

## 8 November 2026: those crystals are brick rows

- The entry below calls the 16 new planes rectangle grids. Their rows (or
  columns) are offset by half a domino: they are brick rows with diagonals
  of period 4. The counts are unchanged.

## 8 November 2026: more than one crystal passes after one cut

- The collar-plane epic's entry in the knot intuition doc said that of the
  atlas epic's periodic planes only the rhombus lattice obeys the collar law
  after one cut. The census's larger tori, run afterwards, found 16 rectangle
  grids with diagonals of period 4 that do too
  ([interpretation](artifacts/COLLAR-PLANE-20261108-001C/COLLAR-PLANE-20261108-001C-E001_periodic_planes_after_cutting/run/interpretation.md)).
- Unchanged: the theorem (one periodic plane suffices, and every radius
  fails) and every count of the census's main part.

## 8 November 2026: the pinwheel's undecorated law does not force roundness

- The pinwheel atlas epic found that none of 96,474 periodic planes obeys
  the pinwheel's own law, and read this as the plane perhaps needing no
  hidden information for roundness, unlike the sphere. One of those planes,
  the lattice of rhombi that four tiles make around a common right angle,
  obeys the collar law once cut by Conway's cut, and the 1,168-form
  radius-2 law once cut twice. For every radius a further cut obeys the
  pinwheel's undecorated law of that radius, so no such law forces
  roundness ([collar plane](research/COLLAR-PLANE-20261108-001/collar_plane.md)).
- The growth-as-a-law epic cited Dworkin and Shieh's theorem on aperiodic
  sets for the dead ends of the pinwheel's outward growth. The collar law
  and the radius-2 law are not aperiodic, so the theorem does not explain
  them; the dead ends themselves stand.
- Both decision notes carry a correction section. Unchanged: the atlas's
  finite law and its label theorem, every growth measurement, and every
  record's conclusion.

## 8 November 2026: native creation does see where atoms sit

- TRISUM-READ-20261107-001-D002 is titled "Native creation cannot see where an
  atom sits within its switching class". Its evidence is one space, seed 5,
  where a symmetry of the glue moves an atom and the native map cannot tell
  the two places apart. In general native creation does see where an atom
  sits. For five glues with two placements of their atoms in one switching
  class, removing a line of an atom creates differently at glue lines, so the
  whole native maps differ; only creation between glue lines is the same
  ([switch read](research/SWITCH-READ-20261108-001/switch_read.md)).
- The record now carries a pending qualification.
- Unchanged: the record's conclusion about seed 5, the junction reading
  (TRISUM-READ-20261107-001-D001) and every frozen statement, which also hold
  on the five other placements.

## 8 November 2026: knots across time, narrowed to the first row

- TIME-KNOTS-20261107-001-D001 and its decision note said that a process
  remembers its past only pairwise exactly when each future value is a single
  AND or OR. That holds for the knots joining a future value to the first row,
  which is what the proof shows. Through intermediate rows it fails. Rule 128,
  where each cell becomes the AND of three, never shows 1 0 1 after a step, so
  a cell on at time 1 and a cell on at time 2 can force a third cell on: a knot
  joining two times. Rules 136 and 160 do the same.
- The record now carries a pending qualification, and the
  [decision note](research/TIME-KNOTS-20261107-001/time_knots.md) a
  correction section with the computation.
- Unchanged: the three theorems, Life's step and every count of the census.

## 8 November 2026: the intuition guide becomes a textbook

- [INTUITIONS.md](INTUITIONS.md) is now written as a textbook, to be read in
  order: seven chapters divided into 26 lessons, then the glossary. What
  jscul.dev showed as four parts are now seven chapters, and what it called
  chapters are now lessons.
- Twelve lessons are new. They teach what the guide used without explaining:
  distinctions and joint states; the notation and what makes variables free;
  emergence in the Game of Life, read as a system of rules on a grid drawn in
  advance; how to read the atom A, B → c, the rule that forbids only A and B
  without c; forgetting and witnesses; knots on the cube of states; two-place
  rules and the majority vote; the shape of a system; easy and hard questions;
  refutations and their degree; and counting worlds. A twelfth, "What a shape
  is", gives the owner's definition of a shape, any structure that rules make,
  as a reading with the results that bear on it. Other lessons gained short
  definitions of the terms they use.
- Two former chapters are now two lessons each: "Which knots remember a loop"
  (rings, then networks) and "Counting what emerges" (one lesson per note).
- Every part of a lesson now opens with a bold lead, as most already did, so
  that jscul.dev's contents page can list each lesson's subsections and link
  to them.
- Lesson 1.5 ends with a short subsection, "CNFs in colour", that draws its
  three rules with one colour for each variable: a clause ties together exactly
  the colours in its row, and a CNF binds two loops when it rules something out
  but ties no pair of colours. Lesson 1.2 points to it.
- Unchanged: every claim, label, proof reference and command. Cross-references
  are renumbered, and the links from [THEORY.md](THEORY.md),
  [FINDINGS.md](FINDINGS.md), [lean/](lean/), the notes and
  [tools/knotlab](tools/knotlab/) point to the new lesson anchors.

## 8 November 2026: every workspace commit publishes itself

- Publication now starts from a commit hook in the research workspace, so
  every commit there, not only an epic's closure, is published here shortly
  after it is made, with no step left to whoever made it. Runs queue one at a
  time, and a run stopped midway is cleaned up by the next.
- A run that would change only the workspace commit named in
  [data/published.json](data/published.json) no longer makes a commit here.
- jscul.dev's sync, when its push loses a race with another push to the
  site, now syncs again on top of the new site instead of failing.

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
