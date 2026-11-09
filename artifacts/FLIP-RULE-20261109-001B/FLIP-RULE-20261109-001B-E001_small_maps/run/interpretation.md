# Persistence without a flip, small maps: interpretation

Experiment `FLIP-RULE-20261109-001B-E001` (exploratory), run once on 2026-11-09 under the frozen contract (pre-registered in 7581ed1fa), in
3.8 s on 16 workers. Exact. Every reading is in `result.json`.

## Control

No contact with a flip fails to persist, at any size read.

## Primary observable

| Contacts | Maps | Contacts read | Persistent | With a flip | Persistent without a flip | Distinct maps with one |
| --- | --- | --- | --- | --- | --- | --- |
| 1, 2 (exhaustive) | 1, 6 | 1, 12 | 1, 4 | 1, 4 | 0 | 0 |
| 3 (exhaustive) | 112 | 336 | 192 | 96 | 96 | 1 |
| 4 (exhaustive) | 4,176 | 16,704 | 5,184 | 1,728 | 3,456 | 4 |
| 5 (exhaustive) | 258,048 | 1,290,240 | 403,200 | 72,960 | 330,240 | 37 |
| 6, 7 (sampled) | 19,824, 14,177 | 118,944, 99,239 | 29,429, 26,650 | 2,220, 821 | 27,209, 25,829 | 275, 3,349 |

- **H1 fails at three contacts.** The smallest map: a ring of one contact, a ring of three and a ring of two, the last two sharing two
  contacts in a row (a digon face). The two contacts of the digon persist without a flip: one sends nothing (its two arcs reach the same
  contact and cancel), the other hears nothing.

## Reading against the decision rule

H1 fails. A post-hoc classification of the exhaustive readings (not part of this contract) found every exception to five contacts
degenerate: the contact sends or hears nothing, or the map has a ring or a face of one or two contacts. E002 tests the refinement.

## Nonclaims

- **Exploratory and finite;** equally spaced rings; two-time knots only (A30).
