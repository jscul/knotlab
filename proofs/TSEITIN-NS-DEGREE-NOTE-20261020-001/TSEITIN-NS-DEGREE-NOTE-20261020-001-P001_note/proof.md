# A checkable note: the Nullstellensatz degree of Tseitin formulas is the toggle width

Status: Proved

Ticket `TSEITIN-NS-DEGREE-NOTE-20261020-001`, 2026-10-20. This ticket turns
two closed results into a self-contained note for proof-complexity readers,
with a standalone replay script:
- `DEEP-HOLES-20261020-001B-P001`: the depth of a charge hole is the toggle
  width;
- `CUTWIDTH-DEPTH-20261020-001B-P001`: the toggle width is cutwidth + 1 at
  maximum degree three.

Sharing the note outside the repository is the owner's decision. Nothing has
been sent.

## Statement

Let G be a connected graph and c an odd charge on its vertices. T(G, c) is the
Tseitin formula, written as polynomials clause by clause:
- one polynomial χ_{v,β} for each vertex v and each assignment β of its edges
  that violates its constraint;
- plus the Boolean axioms x² − x.

The degree of a refutation is the largest degree of a product it uses.

- **Theorem 1.** Over a field of characteristic 2 the Nullstellensatz degree
  of T(G, c) is the maximum degree Δ(G). Over every other field it is the
  toggle width tgw(G), whatever the charge.
- **Theorem 2** (from `CUTWIDTH-DEPTH-20261020-001B`). If G has at least three
  vertices, then cw(G) + 1 ≤ tgw(G) ≤ cw(G) + ⌊Δ(G)/2⌋.
- **Corollary 3.** When the maximum degree is at most three and the
  characteristic is not 2, the degree is cw(G) + 1.
- **The ±1 encoding** (a remark in the note). Put y_e = 1 − 2x_e, and write
  vertex v's constraint as the single binomial y_{E(v)} − (−1)^{c(v)}.
  - Measured after reduction modulo y² = 1, the degree is exactly cw(G), for
    every connected G.
  - Measured before reduction, it lies between tgw(G) and cw(G) + Δ(G).

## What is new here

- **The duality lemma.**
  - Degree-d refutations in the clause encoding fail to exist exactly when a
    level-d pseudo-distribution exists.
  - A pseudo-distribution is a family of signed local functions on edge sets
    of size at most d. They must be consistent under marginals, equal 1 on the
    empty set, and vanish on every assignment that violates a vertex whose
    edges all lie in the set.
  - The lemma turns the depth of `DEEP-HOLES-20261020-001B` into a
    Nullstellensatz degree.
- **The sweep as an identity.** The sweep refutation, written with parity
  indicators of cuts, is an exact identity over the integers. It needs no
  Boolean axioms.
- **The ±1 statements.**
  - After reduction, a product y_A(y_{E(v)} − s_v) becomes the two-term
    relation y_{A△E(v)} − s_v·y_A. The step cost is then the larger of the
    two cuts, and Lemma 9 of the note (Fomin and Thilikos) finishes the lower
    bound.
  - Before reduction, the substitution y = 1 − 2x carries every refutation
    into the clause encoding.
- **Inherited.**
  - Depth equals toggle width: `DEEP-HOLES-20261020-001B`.
  - The sandwich, peak elimination and the restated Fomin–Thilikos lemma:
    `CUTWIDTH-DEPTH-20261020-001B`.

## The package

| File | What it is |
| --- | --- |
| `note/tseitin_ns_degree.tex` | Source of the 7-page note. `check.py --write` builds `note/tseitin_ns_degree.pdf`, which is git-ignored here. The note has the results and a table of values, the duality lemma, both bounds with proofs, the toggle-width sandwich with proofs, remarks (the ±1 encoding, Sherali–Adams, Tseitin mod p, search number, resolution), a novelty statement, and a description of the replay. Its byline is the lab. A footnote says it was prepared with Claude and has had no expert review. |
| `replay.py` | A standalone script, standard library only, about 25 s. On ten cubic graphs (K₄, the prism, K₃,₃, the five eight-vertex cubic graphs, a ten-vertex graph and the Petersen graph) it checks: the widths; the sweep refutation as an integer identity; the closed-form design at level tgw − 1 against every axiom multiple, over F₃, F₅ and (up to 12 edges) Q; the characteristic-2 refutation; the degrees by direct elimination over F₂ and F₃; peak elimination and uncrossing; the ±1 degrees by signed union-find; and treewidths. Four controls must fail, and do: even charge in both encodings, the design at level tgw, and the sweep with a step removed. |
| `check.py` | Ties the note to the replay; see below. |

## Values

| Graph | n | edges | tw | tw of line graph | cw | tgw | degree, char ≠ 2 | degree, char 2 | ±1 after / before reduction |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| K₄ | 4 | 6 | 3 | 4 | 4 | 5 | 5 | 3 | 4 / 6 |
| prism | 6 | 9 | 3 | 4 | 4 | 5 | 5 | 3 | 4 / 6 |
| K₃,₃ | 6 | 9 | 3 | 5 | 5 | 6 | 6 | 3 | 5 / 7 |
| cubic8-a | 8 | 12 | 3 | 4 | 4 | 5 | 5 | 3 | 4 / 6 |
| cubic8-b | 8 | 12 | 3 | 4 | 4 | 5 | 5 | 3 | 4 / 6 |
| cubic8-c | 8 | 12 | 3 | 5 | 5 | 6 | 6 | 3 | 5 / 7 |
| cube | 8 | 12 | 3 | 5 | 5 | 6 | 6 | 3 | 5 / 7 |
| Wagner | 8 | 12 | 4 | 5 | 5 | 6 | 6 | 3 | 5 / 7 |
| cubic10 | 10 | 15 | 3 | 4 | 5 | 6 | 6 | 3 | 5 / 7 |
| Petersen | 10 | 15 | 4 | 6 | 6 | 7 | 7 | 3 | 6 / 8 |

On cubic10, Sherali–Adams refutes at level tw(L(G)) + 1 = 5. Nullstellensatz
needs 6 there.

## Literature search

The search ran on 2026-10-20, before writing. It covered Tseitin formulas with
Nullstellensatz, polynomial calculus, Sherali–Adams and affine relaxations,
rank, cutwidth and Weisfeiler–Leman, and it found no statement of the exact
degree. The relevant sources:
- Grigoriev (FOCS 1998): linear Nullstellensatz lower bounds on expanders.
- Buss, Grigoriev, Impagliazzo and Pitassi (JCSS 2001): linear bounds for
  polynomial calculus.
- Galesi, Talebanfard and Torán
  ([ECCC TR18-170](https://eccc.weizmann.ac.il/report/2018/170); ACM TOCT
  2020): an exact cops-and-robber characterization of resolution width,
  variable space and depth.
- Itsykson et al.: bounds of 2^Θ(tw) for regular resolution and OBDDs.
- Wainwright and Jordan (2004): Sherali–Adams is exact at treewidth.
- Makedon and Sudborough (DAM 1989): cutwidth equals the search number at
  maximum degree three.
- Fomin and Thilikos (DAM 2003), read through their ALCOM-FT technical report.

Wikipedia's [Cutwidth](https://en.wikipedia.org/wiki/Cutwidth) article says
cutwidth equals pathwidth + 1 on subcubic graphs. P₃ (both 1) and K₃,₃
(cutwidth 5, pathwidth 3) contradict that. The note cites Makedon and
Sudborough's search-number statement instead.

## What `check.py` establishes

| Check | Result |
| --- | --- |
| `replay.py` imports only the standard library, and run in an isolated interpreter it passes every check on all ten graphs in under two minutes | pass |
| The note's table, parsed from the source, matches the replay in every cell, and the degree there equals tgw = cw + 1 | pass |
| The note's remark numbers match the replay. Sherali–Adams example: edge list, line-graph treewidth 4, cw 5, degree 6 against 5. ±1 degrees: cw after reduction, tgw + 1 before, on all ten graphs. Caption: K₄ and K₃,₃ share treewidth 3 but have degrees 5 and 6 | pass |
| The roster is as described. Ten connected cubic graphs; K₄; K₃,₃ bipartite and the prism with a triangle; five pairwise non-isomorphic eight-vertex graphs (the known count), with the cube and the Wagner graph identified; Petersen identified by girth 5 | pass |
| The note builds with pdflatex with no warnings or overfull lines (7 pages), and any stored PDF has the same text as a fresh build | pass |
| The parent bindings match | pass |
| Controls: a table entry, a replay value, a remark's number, a parent digest and the roster are each tampered with | each caught |

## Corrections made while writing

- **±1 remark.** The first draft said the ±1 degree lies between tgw and
  tgw + 3. That is wrong in general: before reduction the upper bound is
  cw + Δ, and after reduction the degree is exactly cw. The note now states
  the correct claims, and the replay checks them.
- **Grigoriev's bound.** The first draft said Theorem 1 "contains" Grigoriev's
  bound. His encoding is not the clause encoding, so the note now says the
  degrees are in line with his bound.
- **Peaks.** The first draft's peak-elimination proof said peaks are isolated,
  without proof. The argument does not need it, so the claim was removed.

## Scope

- **Kind of proof.** The proofs are in prose; no kernel checks them. The
  replay checks certificates on ten graphs, which illustrates the proofs but
  does not prove them.
- **Not claimed.**
  - Polynomial calculus degree, the exact Sherali–Adams degree, and any size
    bound.
  - Novelty beyond "not found after a targeted search". The ±1 statement after
    reduction may be close to known arguments for binomial systems.
- **Not done.** No human expert has reviewed the note, and nothing has been
  sent or shared.
