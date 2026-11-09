# Persistence without a flip, non-degenerate maps: interpretation

Experiment `FLIP-RULE-20261109-001B-E002` (exploratory), run once on 2026-11-09 under the frozen contract (pre-registered in b28d92b98), in
7.2 s on 16 workers. Exact. Every reading is in `result.json`.

## Control

No contact with a flip fails to persist.

## Primary observable

| Contacts | Non-degenerate maps kept (of 4,000,000 draws) | Persistent contacts | With a flip | Without a flip | Of those, sending and hearing | Distinct maps |
| --- | --- | --- | --- | --- | --- | --- |
| 6 | 7,268 | 21,056 | 3,064 | 17,992 | 4,194 | 14 |
| 7 | 5,650 | 20,000 | 1,016 | 18,984 | 8,009 | 195 |
| 8 | 4,429 | 12,073 | 244 | 11,829 | 3,766 | 1,405 |
| 9 | 3,502 | 8,715 | 79 | 8,636 | 2,553 | 2,458 |

- **H1' fails at six contacts.** On maps whose rings and faces all have at least three contacts, most persistent contacts have no flip.
  An example: three rings of 3, 6 and 3 contacts on a surface of genus 2 with one face of 12, where a contact that sends and hears has
  closed walks back to it of lengths 3, 4, 5, … in the counts 2, 4, 4, 8, 24, 48, …: even at every length, with no symmetry fixing it.
- **Not a hidden symmetry either (post hoc).** Of the 14 sending-and-hearing examples kept at six and seven contacts, 11 have no
  automorphism of the contact graph that fixes the contact and exchanges its two in-arcs; the even counts are arithmetic, not paired.

## Reading against the decision rule

H1' fails, so the smallest exceptions are read for their mechanism: persistence on these maps comes from closed walks whose counts happen
to be even, not from a symmetry. The flip rule is a property of the periodic tilings read (`PLANE-PLAIN-20261109-001A`,
`FLIP-RULE-20261109-001A`), not of maps in general.

## Nonclaims

- **Exploratory and finite:** random samples; equally spaced rings; two-time knots only (A30).
