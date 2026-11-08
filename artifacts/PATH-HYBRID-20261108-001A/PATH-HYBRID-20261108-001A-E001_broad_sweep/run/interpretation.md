# A broad sweep of mixed four-ring paths: interpretation

Experiment `PATH-HYBRID-20261108-001A-E001` (exploratory), run 2026-11-08 under the frozen contract as the long-running unit
`path-hybrid-a1` (PATH-HYBRID-A1 in `docs/LONG_RUNNING.md`): 20,480,000 paths in 785 s on 16 workers. Every verdict is exact by the
row-sequence reduction. Paths whose three contacts all persist are in `paths.json`, and the totals are in `result.json`.

## Control

It passes. The ten smallest native paths give the same verdicts on their full state spaces.

## Primary observable

| Paths | Count |
| --- | --- |
| In the family | 20,480,000 |
| All three contacts persist | 17,192 |
| Native: the last contact binds the end rings at every lag from the light cone on | 16 |
| … and the last contact binds all four rings | 16 |
| … and the first contact binds the end rings too | 16 |

- **H1 holds.** Native paths exist with one rule on each ring.
- **The 16 are one construction.**
  - **End rings.** 3 cells running a shift, 170 or 240.
  - **Middle rings.** 5 cells running rule 150, with their contacts two cells apart. All four position pairs occur.
  - **Laws.** c1 and c3 read both of their neighbours on both rings. c2 reads one neighbour on each middle ring, the cell on the
    short arc toward that ring's other contact.

  The 16 are the two shift directions on each end ring times the four position pairs, each pair with its own c2 law.
- **None with middle rings of 4 cells.** At 3/4/4/3, 3,728 paths keep all three contacts and none is native.
- **Persistence alone is cheap.** Most persistent paths have frozen rings (rule 204), which keep their first row and carry nothing:
  rule 204 on all four rings accounts for 3,645 of the 17,192.

## Reading against the decision rule

- **Uniform rings suffice.** A native path needs no hybrid ring. Ticket B's hybrid rings give many more, 1,120 of 3,175,200 paths
  against 16 of 20,480,000 here.
- **The earlier tension is not forced.** `NATIVE-PATH-20261108-001` read its negative searches as a tension: a second middle ring
  must keep its own first row and carry the first ring's influence, and the additive rules seemed to keep the first but cancel the
  second. Here rule 150, an additive rule, does both as the second middle ring. How the 16 work, and why the same paths fail with
  rule 150 on their end rings, is in the epic's decision note (`research/PATH-HYBRID-20261108-001/`).

## Nonclaims

- **This family only.** No claim about other paths.
- **Two-time knots only** (A30).
