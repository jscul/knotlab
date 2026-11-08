# A shift as the second middle ring: interpretation

Experiment `NATIVE-PATH-20261108-001C-E001` (exploratory), run 2026-11-08 under the frozen contract: 3,059,280 paths in 1,352 s on
16 workers (registered as NATIVE-PATH-C1 in `docs/LONG_RUNNING.md`). Every verdict is exact by ticket A's reduction.

## Primary observable

- **H1 fails.** No native path exists in this family.
- **No path keeps its contacts.** Not one of the 3,059,280 paths keeps all three contacts persistent, so `paths.json` is empty. The
  control, verifying the smallest native paths, had nothing to verify.

## Why

A sample of 3,000 paths (600 random items of the family, 5 random completions each; not part of the contract) shows where
persistence breaks.

| Contacts that persist (c1, c2, c3) | Paths |
| --- | --- |
| none | 2,455 |
| c1 only | 498 |
| c1 and c2 | 26 |
| c3 only | 13 |
| c1 and c3 | 7 |
| c2 only | 1 |

- **The shift breaks persistence.** The ring copies each value one cell along per step, so its own first row is used up within
  one turn. From then on it holds only copies of its two contacts' pasts. Its contacts then lose their binding to ring C's own
  cells, and through the feedback c1 usually loses its binding too.
- **Carrying without mixing is not enough.** A carrier whose own first row does not last cannot be a middle ring of a native path.

## Reading against the decision rule

The absence is for this family only. It names the obstruction to examine: a second middle ring must keep its own first row and
still carry the first ring's influence. The shift does the second but not the first, and the additive rules of ticket B do the
first but cancel on the way.

## Nonclaims

- **This family only.** No claim about other paths.
- **Two-time knots only** (A30).
