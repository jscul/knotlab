# Knotlab

By John Cullen.

Findings and intuitions from the contact-first research program of Prespatial
Labs. The program asks whether logic can build structure, such as holes,
paths and spaces, without assuming a space to start from.

The repository has two layers:

- **The introduction.** [INTUITIONS.md](INTUITIONS.md) teaches the program's
  intuitions plainly, as a textbook whose seven chapters start from bits and
  rules. [THEORY.md](THEORY.md) states the thesis and the main
  claims, each labelled by how it is supported and linked to its evidence.
  [FINDINGS.md](FINDINGS.md) lists eleven findings we packaged for outside
  readers, each with Lean proofs, a note or exhaustive checks that run here.
  [docs/ASSUMPTIONS.md](docs/ASSUMPTIONS.md) lists what the program assumes
  but could challenge, each with its status and what rests on it.
- **The full record.** [RESULTS.md](RESULTS.md) lists, with dates, every result
  recorded since the knot test K1–K3 became canonical on 19 October 2026:
  <!-- counts -->228 current results and 5 superseded ones<!-- /counts -->.
  They are stated in the program's own language and linked to their proofs,
  experiments and working notes, which are published as recorded, together
  with the [tickets](tickets/) that set each piece of work. New epics are
  published automatically when they close. The documents that define the
  working perspective are in [docs/](docs/).

## The idea in five lines

- A **loop** brings an open distinction: a bit it leaves free.
- A **knot** binds loops through a contact so that the whole is constrained
  but every part is free, like Borromean rings.
- **Pairs cannot make a knot; three places can.** Two-literal clauses never
  define one, and three-literal clauses define every one.
- **A knot hides at most one bit**, and only parity hides a full bit.
- **Hidden bits have depth**: to see one, an observer must hold a part of the
  network as wide as the network's layout.

Read [INTUITIONS.md](INTUITIONS.md) for the picture,
[THEORY.md](THEORY.md) for the thesis and its main claims,
[FINDINGS.md](FINDINGS.md) for the packaged findings, and
[RESULTS.md](RESULTS.md) for everything, by line of work and date.

## Check it yourself

```bash
# the knot laboratory: Python 3.9+, standard library only
PYTHONPATH=tools python3 -m knotlab demo
PYTHONPATH=tools python3 -m knotlab check --cnf "~A ~B c" --loops A B --contact c
python3 -m unittest tests.test_knotlab          # 80 tests, a few seconds
python3 -m unittest tests.test_theory           # THEORY.md: labels, evidence and links
python3 -m unittest tests.test_assumptions      # docs/ASSUMPTIONS.md: statuses, entries and links
python3 -m unittest tests.test_records tests.test_curation  # the record is complete and current

# the Lean proofs: core Lean 4, toolchain pinned in lean/lean-toolchain
cd lean && python3 check.py && cd ..

# the notes
(cd notes/tseitin-nullstellensatz-degree && python3 replay.py)        # standard library
(cd notes/pfaffian-hypergraph-colourings && python3 independent.py)   # numpy, sympy, networkx
(cd notes/knot-group-counting/links && python3 run_all.py)           # numpy; about 3 minutes

# any record in the full record: run its check from its own folder
(cd proofs/DEEP-HOLES-20261020-001B/DEEP-HOLES-20261020-001B-P001_charge_depth && python3 check.py)
```

Each `check.py` recomputes its proof's facts, runs controls that must fail,
and compares the outcome with the frozen `result.json` beside it. Some checks
need the libraries in [requirements.txt](requirements.txt)
(`pip install -r requirements.txt`) or a Lean toolchain, and a few run for
hours.

## Contents

| Path | What it is |
| --- | --- |
| [INTUITIONS.md](INTUITIONS.md) | The intuitions, taught in chapters and lessons, each labelled as proved, checked, classical or reading |
| [THEORY.md](THEORY.md) | The thesis and the main claims, each labelled premise, proved, checked, conjecture, reading or open, with links to the evidence |
| [FINDINGS.md](FINDINGS.md) | The findings, their kind (new result, new proof, new reading) and their status |
| [tools/knotlab](tools/knotlab/) | Tools that test the knot definition on any finite system of constraints |
| [tests](tests/) | Exhaustive checks of the finite facts the intuitions rely on, and checks of the labels and links of THEORY.md and the register of assumptions |
| [lean](lean/) | Five kernel-checked proofs: the knot test, competing pairs, the ring theorem, loop nerves |
| [notes](notes/) | Three self-contained notes with PDFs, sources and check scripts |
| [RESULTS.md](RESULTS.md) | Every result since 19 October 2026, dated, grouped by line of work, with links |
| [RANKING.md](RANKING.md) | The results ranked in five tiers by significance to the theory |
| [tickets](tickets/) | The ticket that set each piece of work: objective, stop rule and outcome |
| [data](data/) | The inputs of the generated files (lines of work, ranking tiers, notes, pending qualifications) and the results as JSON |
| [scripts](scripts/) | `build.py` regenerates RESULTS.md, RANKING.md and the JSON in data/ |
| [docs](docs/) | The working perspective: the knot intuition, the foundational thesis, the foundation's classical sources, the program's vocabulary, and the register of assumptions |
| [proofs](proofs/) | Every proof since 19 October 2026: `proof.md`, `check.py`, frozen results and manifests |
| [experiments](experiments/), [artifacts](artifacts/) | Frozen experiment contracts and their outputs |
| [research](research/) | Working notes, decision notes and discovery records for each epic |
| [HISTORY.md](HISTORY.md) | Releases and corrections |

The full record is copied byte for byte from our research workspace, so the
SHA-256 hashes in its manifests and contracts still verify. As a result, some
scripts and logs still contain absolute paths from that workspace. Records
refer to each other by labels such as `KNOT-LOOPS-20261019-001B`, which are
also their folder names.

## How this was produced

The work was done in Prespatial Labs' research workspace, where AI agents
(Anthropic's Claude and OpenAI's Codex) carried out most of the proofs,
computations, reviews and writing under the direction of the repository
owner. No human expert has reviewed these results. We publish them so that
they can be checked, and every claim comes with the means to check it.

Corrections and prior statements we missed are welcome as
[GitHub issues](https://github.com/jscul/knotlab/issues). Corrections
are recorded in [HISTORY.md](HISTORY.md), and earlier versions stay in the
history.

## How this repository is updated

Everything here is published from our research workspace, which is the source
of truth for this repository and for [jscul.dev](https://jscul.dev).

- **Records, automatically.** Every commit in the workspace publishes itself
  here shortly after it is made: an epic's committed proofs, experiments,
  working notes and tickets byte for byte, and the documents in docs/. Work
  that has not been committed is never copied.
- **Pages, code and data, from the workspace too.** INTUITIONS.md, THEORY.md,
  FINDINGS.md, this README, the notes, the Lean files, the knot laboratory,
  the tests, and the inputs in data/ (lines of work, ranking tiers, notes and
  pending qualifications) are written in the workspace and published with the
  records. [data/published.json](data/published.json) records what was last
  published. A file edited here directly is reported, not overwritten, until
  the change is made in the workspace.
- **Generated here.** [scripts/build.py](scripts/build.py) rebuilds
  RESULTS.md, RANKING.md and the JSON in data/ from the records, and the tests
  run before every push. If a later result supersedes or qualifies a record
  that a THEORY.md claim cites, `tests/test_curation.py` fails until the claim
  says so.
- **The site follows.** A GitHub Actions workflow in the site's repository
  copies what jscul.dev shows from here, checks and builds it, and pushes. It
  starts after each publication, and also runs every six hours.
- **Corrections.** A pending qualification is entered once, in
  [data/qualifications.json](data/qualifications.json). It then appears in
  RESULTS.md, on jscul.dev and in the checks of THEORY.md. Corrections are
  recorded in [HISTORY.md](HISTORY.md), and are welcome as
  [issues](https://github.com/jscul/knotlab/issues).

## What this does not claim

The boundary between two-place and three-place constraints is a boundary of
expressibility. It is not the boundary between P and NP, and nothing here
addresses that question. Nothing here is physics. Where the program reads the
mathematics philosophically, [INTUITIONS.md](INTUITIONS.md) labels the reading
as such.

## License and citation

The text and notes are licensed under CC BY 4.0 and the code under the MIT
License; see [LICENSE](LICENSE). To cite a note, use its title and this
repository's URL. To cite the repository, see [CITATION.cff](CITATION.cff).
