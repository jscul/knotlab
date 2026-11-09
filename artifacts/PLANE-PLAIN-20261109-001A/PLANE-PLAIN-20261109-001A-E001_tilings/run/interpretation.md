# Which contacts of periodic plane tilings persist: interpretation

Experiment `PLANE-PLAIN-20261109-001A-E001` (exploratory), run once on 2026-11-09 under the frozen contract (pre-registered in
6733e3bc6), in 1.3 s on 16 workers, after a first launch that stopped on an exception before writing anything (below). Exact: return
parities to length n + 1, and map automorphisms built from one dart. Every row is in `result.json`.

## Control

Every contact of every torus of the three regular lattices persists and has a flip (319 tori, 7,689 contacts).

## Primary observable

| Tiling | Tori read | Contacts that persist | Tori with every contact persistent |
| --- | --- | --- | --- |
| square, triangular, honeycomb | 103, 93, 123 | all (1,866, 2,574, 3,249) | all |
| 4.8.8, 3.12.12, tetrakis square, triakis triangular | 103, 123, 103, 93 | exactly the contacts of the base lattice (1,866 of 5,598; 3,249 of 9,747; 1,866 of 5,598; 2,574 of 7,722) | none |
| kagome 3.6.3.6, 3.4.6.4, 4.6.12, rhombille, deltoidal trihexagonal, kisrhombille | 123 each | none | none |

- **H1 holds on every torus read:** a contact persists exactly when it has a flip, an orientation-preserving automorphism fixing it and
  exchanging its two rings.
- **H2 holds:** only the three regular tilings keep every contact persistent. On the others the contacts that persist are those between
  two rings of the base lattice's kind, the only ones with a flip; a contact between rings of different degree, or between faces of
  different size, never has one, and none of them persists.

## Reading against the decision rule

H2 holds, so among these tilings a two-dimensional network of persistent contacts is a torus of a regular lattice, which
`GROW-PLAIN-20261109-001B`, Theorem 2, rules out as a plane read plainly at every size. No tiling here gives a plane read plainly.

## Deviations, recorded

- **A first launch stopped on an exception** before writing anything: a torus whose dual has an edge with one face on both sides joined
  a ring to itself, which the contract says to skip; run.py now skips it (14fb66075). Roster and hypotheses unchanged.

## Nonclaims

- **Exploratory and finite:** the roster only; the snub and elongated tilings, their duals, k-uniform tilings and non-periodic networks
  are not read.
- **Two-time knots only** (A30); equally spaced rings only.
