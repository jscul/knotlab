# A census of growth steps: interpretation

Experiment `GROW-NET-20261108-001B-E001` (exploratory), run 2026-11-08 under the frozen contract: 795,042 attachments of one new ring to
16 balanced seeds, and the truncations and rectifications of the five Platonic networks. Exact, with no lag cutoff. Counts are in
`result.json`.

## Control

`grow_lib`'s exact test agreed with `loopnet_lib.odd_returns` on 1,276 random attachments before freezing; `GROW-NET-20261108-001A`
proves the one- and two-contact cases.

## Primary observable

| Seed | Attachments keeping every contact persistent, by contacts of the new ring (1, 2, 3, 4) |
| --- | --- |
| Loop of 3 rings | 0, 0, 2 of 160, 15 of 1,440 |
| Two rings sharing 3 contacts | 0, 0, 4 of 216, 32 of 2,430 |
| Tetrahedron | 0, 0, 0, 51 of 17,010, every one with two cancelling corners |
| Loops of 4 to 6 rings; two rings sharing 4 or 5 contacts; cube; octahedron | none (up to 4 contacts) |
| Dodecahedron; icosahedron; 3 × 3 and 4 × 4 tori; the genus-2 network of 16 rings | none (up to 3 contacts) |

Every truncation and rectification of a Platonic network loses persistence except the rectified tetrahedron, which is the octahedron.

## Reading against the decision rule

- **H1 holds.** No attachment by one or two contacts keeps persistence, as `GROW-NET-20261108-001A` proves, and none by three or four
  does on any seed of more than four rings. Growing one ring at a time keeps every contact persistent only in the first steps from the
  smallest seeds.
- **H2 holds.** Uniform refinement of the sphere's regular networks loses persistence.

## Nonclaims

- **One growth step** from these seeds; attachments by at most 4 contacts.
- **Two-time knots only** (A30).
