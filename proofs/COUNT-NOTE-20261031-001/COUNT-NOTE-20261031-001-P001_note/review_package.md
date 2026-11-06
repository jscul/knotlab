# External-review package

**Note:** "Counting 2-colourings of 3-regular hypergraphs with Pfaffian incidence graphs" (Prespatial Labs, draft of 31 October 2026).
- PDF: `note/counting_note.pdf`, rebuilt by `check.py`.
- Source: `note/counting_note.tex`.

**Status.**
- Prepared with Claude (Anthropic).
- No human expert has reviewed anything.
- Nothing has been sent. Whether and to whom to send it is the repository owner's decision.

## 1. The claims and their evidence

Paths are relative to the repository root. Every proof directory is `proofs/<ticket>/<ticket>-P001_<slug>/`, with `proof.md`,
`check.py` and the frozen `result.json`.

| # | Claim | Proved in | Check (runtime) | Independent replay | Novelty and folklore risk |
| --- | --- | --- | --- | --- | --- |
| 1 | A connected cubic signed system is non-colourable iff its signing is Pfaffian (Lemma 6) | `THREEFOLD-AMPLITUDE-20261030-001C` | (imported) | — | Signed form of Seymour's theorem; high |
| 2 | The trisum law A = ρ₁ρ₂ρ₃ − α₁α₂α₃ − β₁β₂β₃ (Theorem 8) | `SEYMOUR-COUNT-20261030-001A` | 16 s | — | No statement found; moderate |
| 3 | A leaf's split is two weighted Berman determinants (Proposition 9) | `SEYMOUR-COUNT-20261030-001B` | 50 s | — | Elementary given Berman; moderate |
| 4 | #col(H − L) polynomial on every non-2-colourable cubic triple system (Theorem 1) | same | same | Fano compositions by brute force (I5) | No statement found; moderate (a holographic algorithm on a Pfaffian matchgrid might reach it) |
| 5 | The junction similitude, multiplier α² + αβ + β² (Theorem 11) | `TWIST-COUNT-20261030-001A` | 4 s | symbolic, 32 cases (I6) | No statement found; low–moderate |
| 6 | Unbranched twists count in polynomial time (Theorem 2) | same | same | — | No statement found; low–moderate |
| 7 | No junction is an exact crossover; soft crossings exist, e.g. (40000, −1112, 3336, −192) (Proposition 12) | `TWIST-COUNT-20261030-001B` | 6 s | the soft crossing (I1) | Exact computation; low |
| 8 | Snakes, the lattice condition (5, 139, 3), universality inside Pfaffian graphs (Lemma 13, Theorem 14) | `SOFT-CROSS-20261031-001A` | 1 s | the multipliers (I1) | Standard method in a new setting; moderate |
| 9 | Hardness under signings (Theorem 3); source also replayed from NAE-3SAT | `SOFT-CROSS-20261031-001B`, `-001C` | 5 s, 5 s | — | Source known (Fan–Cai 2020); moderate for the Pfaffian setting |
| 10 | Signs are path lengths; hardness without signs (Lemma 15, Theorem 4) | `PLAIN-COUNT-20261031-001A` | 227 s | sign interpolation on K₃,₃ (I4) | Standard method in a new setting; moderate |
| 11 | Plain planar pages are twisted (Euler); the Fano plane is the only non-2-colourable one with a brace incidence graph (Propositions 16, 17) | `PLAIN-COUNT-20261031-001B` | 80 s | — | Proposition 14 likely known (RST); high |
| 12 | The ladder site is (NW)^k; the cube junction's characteristic polynomial (x² − 19x − 1)(x² + 7x + 13); the lattice condition (Lemmas 18, 19) | `PLAIN-BRACE-20261031-001A` | 29 s | NW and K₃,₃ counts (I2, I3) | No statement found; low–moderate |
| 13 | Hall, ladders, weaving, cube junction lemma; hardness on Pfaffian braces (Lemma 20, Theorem 5) | `PLAIN-BRACE-20261031-001B` | 42 s | — | No statement found; moderate |

The lemma and theorem numbers are those of the compiled note: one counter runs through theorems, lemmas, propositions and corollaries.

## 2. How to replay

From the repository root, with the workspace `.venv` (numpy, sympy, networkx, python-sat) and, for the PDF, a TeX installation:

```bash
cd proofs/COUNT-NOTE-20261031-001/COUNT-NOTE-20261031-001-P001_note
../../../.venv/bin/python -B replay.py        # reruns the eleven cited checks in a temporary copy; about 8 minutes; prints ALL OK
../../../.venv/bin/python -B independent.py   # fresh-code recomputation of the headline numbers; about 1 s
../../../.venv/bin/python -B check.py         # ties the note to both, compiles it, runs tampering controls
```

`replay.py` never writes into the repository unless given `--write`, and then only `replay_result.json` here. Two checks depend
on Python's per-run hash order. `SEYMOUR-COUNT-20261030-001B` labels a child square's two weights in that order, and
`TWIST-COUNT-20261030-001A` draws random signings. For those sections the replay accepts the stated equivalence and records it.
Expected output:

```text
ok  SEYMOUR-COUNT-20261030-001A    ~  16 s  ALL OK
ok  SEYMOUR-COUNT-20261030-001B    ~  50 s  ALL OK  (tolerated: hash order)
ok  TWIST-COUNT-20261030-001A      ~   4 s  ALL OK  (tolerated: hash order)
ok  TWIST-COUNT-20261030-001B      ~   6 s  ALL OK
ok  SOFT-CROSS-20261031-001A       ~   1 s  ALL OK
ok  SOFT-CROSS-20261031-001B       ~   5 s  ALL OK
ok  SOFT-CROSS-20261031-001C       ~   5 s  ALL OK
ok  PLAIN-COUNT-20261031-001A      ~ 227 s  ALL OK
ok  PLAIN-COUNT-20261031-001B      ~  80 s  ALL OK
ok  PLAIN-BRACE-20261031-001A      ~  29 s  ALL OK
ok  PLAIN-BRACE-20261031-001B      ~  42 s  ALL OK
ALL OK
```

## 3. Questions for a reviewer

1. **Theorem 1 (polynomial counting on non-2-colourable systems).** Is this known, perhaps as a consequence of a holographic algorithm on a
   Pfaffian matchgrid, or of the theory of sign-nonsingular matrices? The repository's searches found counting results for perfect
   matchings only.
2. **The trisum law.** Is the three-term law ρ₁ρ₂ρ₃ − α₁α₂α₃ − β₁β₂β₃ for counts on trisums an instance of a known gluing formula for
   Pfaffians along 4-cycles (for example in McCuaig's or Robertson, Seymour and Thomas's arguments)?
3. **Theorem 11.** The similitude's multiplier α² + αβ + β² is an Eisenstein norm. Is there a conceptual reason, beyond the symbolic
   verification, for example a holographic transformation that diagonalizes the split form?
4. **Theorems 3–5.** Is hardness on Pfaffian graphs, or on Pfaffian braces, for a problem that is planar-tractable by matchgates known for
   any Holant problem? We found none. The construction simulates crossings inside Pfaffian graphs by interpolation.
5. **Proposition 17.** Is the uniqueness of the Fano plane among non-2-colourable cubic systems with a brace incidence graph stated in the
   literature (Seymour 1974; Robertson, Seymour and Thomas 1999; McCuaig 2004)?
6. **Presentation.** Which parts deserve full proofs in a paper version, and which can stay as outlines with pointers to the checked
   repository proofs?
