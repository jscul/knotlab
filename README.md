# Knotlab

Findings and intuitions from the contact-first research program of Prespatial
Labs. The program asks whether logic can build structure, such as holes,
paths and spaces, without assuming a space to start from.

This repository holds only what we consider established. Every finding has a
complete proof, and a script or Lean file here checks it. The focus is the
intuitions behind the program, stated plainly and tied to those proofs.

## The idea in five lines

- A **loop** brings an open distinction: a bit it leaves free.
- A **knot** binds loops through a contact so that the whole is constrained
  but every part is free, like Borromean rings.
- **Pairs cannot make a knot; three places can.** Two-literal clauses never
  define one, and three-literal clauses define every one.
- **A knot hides at most one bit**, and only parity hides a full bit.
- **Hidden bits have depth**: to see one, an observer must hold a part of the
  network as wide as the network's layout.

Read [INTUITIONS.md](INTUITIONS.md) for the full picture, then
[FINDINGS.md](FINDINGS.md) for the list of results and their status.

## Check it yourself

```bash
# the knot laboratory: Python 3.9+, standard library only
PYTHONPATH=tools python3 -m knotlab demo
PYTHONPATH=tools python3 -m knotlab check --cnf "~A ~B c" --loops A B --contact c
python3 -m unittest tests.test_knotlab          # 80 tests, a few seconds

# the Lean proofs: core Lean 4, toolchain pinned in lean/lean-toolchain
cd lean && python3 check.py && cd ..

# the notes
(cd notes/tseitin-nullstellensatz-degree && python3 replay.py)        # standard library
(cd notes/pfaffian-hypergraph-colourings && python3 independent.py)   # numpy, sympy, networkx
(cd notes/knot-group-counting/links && python3 run_all.py)           # numpy; about 3 minutes
```

## Contents

| Path | What it is |
| --- | --- |
| [INTUITIONS.md](INTUITIONS.md) | The intuitions, each labelled as proved, checked, classical or reading |
| [FINDINGS.md](FINDINGS.md) | The findings, their kind (new result, new proof, new reading) and their status |
| [tools/knotlab](tools/knotlab/) | Tools that test the knot definition on any finite system of constraints |
| [tests](tests/) | Exhaustive checks of the finite facts the intuitions rely on |
| [lean](lean/) | Five kernel-checked proofs: the knot test, competing pairs, the ring theorem, loop nerves |
| [notes](notes/) | Three self-contained notes with PDFs, sources and check scripts |
| [HISTORY.md](HISTORY.md) | Releases and corrections |

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
