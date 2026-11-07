# Counts by number of atoms

Status: Proved

Ticket `HANDLE-COUNT-20261106-001B`, 2026-11-06.

**What it uses:**
- **`HANDLE-COUNT-20261106-001A`:** the decomposition (Theorem 1), the bound (Theorem 2), the edge-atom construction (Proposition 6) and its
  library (`junction_lib.py`, `families.py`).
- **`GLUE-READ-20261106-001B`:** its 191 saved spaces (`maps.json.gz`): `BRACE-TREE-20261105-001C`'s 111 census spaces of 23 to 26 points
  and trees, and 80 random spaces with plane glue.
- **`THREEFOLD-GRAMMAR-20261030-001B`:** `census_lib`, which builds the census up to 22 points (`gen_census22.py` here; `census22.json`
  was written by it once, 2383 s, and matches the class counts of `THREEFOLD-SURFACES-20261030-001B`: 8 untwisted, 24 twisted).
- **`THREEFOLD-SURFACES-20261030-001A`:** the SAT genus model, for the genera of trisum braces.
- **`THREEFOLD-SPINSUM-20261030-001A`:** the in-repository instance of the classical genus route (cited, not recomputed).

## Standard statement

On a fixed finite list of 3-regular 3-uniform hypergraphs that are not 2-colourable under their incidence signs (the census of such
hypergraphs up to 26 points, eighty random ones with planar glue, six larger ones, and fresh ones whose glue is a non-planar Pfaffian
brace), we tabulate by the number a of Heawood braces in the tight-cut decomposition of the incidence graph:
- the number J of Robertson–Seymour–Thomas 4-sum junctions and p of planar braces, against the bound J + p ≤ a + s − 2 of ticket A
  (s the fewest signs in the space's switching class);
- weighted 2-colouring counts at λ = 2 and λ = 1 + i (couplings at which counting is #P-hard on these spaces in general), and 2-colouring
  counts under a random signing of the incidence graph, computed through ticket A's decomposition and by an independent elimination;
- how many junctions leave the matchgate class, and how many planar evaluations the decomposition needs.

## Nearest known result

Finite computation; no external result is claimed. The algorithm and the bound are ticket A's; the spaces come from
`THREEFOLD-GRAMMAR-20261030-001B`, `GLUE-READ-20261106-001B` and `THREEFOLD-SURFACES-20261030-001B`.

## Results

**The spaces (257).** The census up to 22 points (32 classes, the Fano plane among them), `GLUE-READ-20261106-001B`'s 111 census spaces
of 23 to 26 points and trees and its 80 random spaces with plane glue, six larger spaces of `THREEFOLD-SURFACES-20261030-001B`, and 28
fresh spaces whose glue is a trisum brace of cubes or prisms: 23 with an edge atom on each sign of a fewest-sign Pfaffian signing, 5 with
T14 decorations. 31 spaces have trisum glue.

**The bound of ticket A (Theorem 2) holds on all 256 spaces it covers** (the Fano plane is excluded by the theorem), with s the fewest signs
in each space's switching class (MaxSAT).
- **Slack 0 is attained** by the 13-point Fano splice (a = 2), by twisted classes with one planar brace (a = 2, p = 1, s = 1), by the
  twisted 22-point class with trisum glue (a = 2, J = 1, s = 1), and by the 29-point plain space of Proposition 6 (a = 3, J = 1).
- The edge-atom chains of two and three cube trisums have slack 1: one atom more than the bound requires.

**The counts.** At λ = 2 and λ = 1 + i, and for 2-colourings under a random signing of each incidence graph, ticket A's decomposition
equals an independent elimination over point colours in all 771 counts.

**By number of atoms.**

| Atoms | Spaces | With trisum glue | Max J | Max planar braces | Min slack | Max junctions violating MGI at one piece (λ = 2 / 1 + i / colourings) |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 1 (Fano, excluded) | 0 | 0 | 0 | — | 0 / 0 / 0 |
| 2 | 21 | 2 | 1 | 1 | 0 | 0 / 0 / 0 |
| 3 | 81 | 7 | 1 | 1 | 0 | 1 / 1 / 1 |
| 4 | 97 | 3 | 1 | 1 | 1 | 1 / 1 / 1 |
| 5 | 33 | 7 | 2 | 1 | 1 | 1 / 1 / 1 |
| 6 | 24 | 12 | 3 | 1 | 1 | 1 / 1 / 1 |

- **Junctions are the only cost.** Spaces with planar glue never split a junction (they have none). With trisum glue, at most one junction
  per piece violates the matchgate identity, so each piece is evaluated at most twice; the totals grow with J, never with a.
- **Two census spaces with trisum glue never split** (the twisted 22-point class and `design 7`, two atoms each): their junctions stay
  matchgates at every coupling tested.
- **The glue's genus is not J.** The trisum braces' genera (SAT) are 1 for one or two junctions and 2 for three, so on these spaces the
  classical route pays 4^{a + glue genus} determinants where ticket A's pays 2^J.

## What the computation checks

`check.py` (513 s):
- **0.** Dependency artifacts bound by hash.
- **1.** Every space is cubic, simple and not 2-colourable under its signing (SAT).
- **2.** Theorem 2 of ticket A on every space other than the Fano plane (whose incidence graph is the Heawood graph, excluded by the
  theorem), with s computed by MaxSAT over switchings; trisum braces' genera by SAT.
- **3.** Each count through ticket A's decomposition equals an independent elimination over point colours; each piece is evaluated
  2^{(violating junctions)} times; ternary tensors are even.
- **4.** The table by number of atoms.
- **5. Controls**, each of which must fire:
  - doubling a split's remainder makes the decomposition disagree with the direct count;
  - with the signs ignored, the bound fails on a signed space with trisum glue;
  - changing one line's table inside the decomposition (doubling a complementary pair of entries, so the table stays even and the
    decomposition runs) makes it disagree with the direct count. A first version doubled a single entry; that breaks evenness, and the
    decomposition's own evenness assertion stopped the run before any count was compared.

## Reading

- **Counting cost follows the junctions, and on the knot's plain spaces the atoms bound the junctions.** Across all 257 spaces the number
  of evaluations rises only where trisum glue is present, and the bound J + p ≤ a − 2 is met with equality on the smallest example.
- **The atoms themselves never show up in the cost.** Spaces with six atoms and no trisum glue are counted with no split at all.

## Nonclaims

- **Finite.** The table describes these spaces only; it proves nothing beyond ticket A's theorems.
- **Cost proxies.** Planar evaluations are counted, not timed; the pieces are evaluated exactly by elimination, not by FKT.
