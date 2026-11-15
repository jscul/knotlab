# Two repeated middle variables and a second way to group the hidden choices

Status: Proved

## Accepted conclusions

- On disjoint paths between opposite pinned repeated middles, ordinary satisfiability reduces exactly to the CNF of ways to break each path. With at most two normalized clause occurrences per pad, a linear orientation algorithm returns a witness; the minimal contradictory clause families are the unmarked tree components. [A, known-overlap-found](../../TWO-RELAY-PADDING-20261115-001A/TWO-RELAY-PADDING-20261115-001A-P001_track_regrouping/proof.md)
- A uniform family with two repeated middle names and at most three implication placements per shared pad realizes NP-complete strict 3-SAT by varying the visible input alone. The restricted instances use both binary equality and ternary data tests. [B, known-overlap-found](../../TWO-RELAY-PADDING-20261115-001B/TWO-RELAY-PADDING-20261115-001B-P001_two_middle_reduction/proof.md)
- NP-completeness survives simultaneous bounds of two middle occurrences and two edge-pad placements per name, including in a uniform fixed-wiring family. Conditioning the q pads required in both polarities gives an O(2^q r) solver on arbitrary middle wiring. [C, known-overlap-found](../../TWO-RELAY-PADDING-20261115-001C/TWO-RELAY-PADDING-20261115-001C-P001_pairwise_sharing/proof.md)
- For a fixed order of middle and pad occurrences in each stage, arbitrary nesting of repeated pairs permits linear indexed decision. If deleting k repeated names restores nesting, both finding the deletion set and conditioning it cost O(2^k r) in total, irrespective of nesting depth or the raw number of crossings. [D, known-overlap-found](../../TWO-RELAY-PADDING-20261115-001D/TWO-RELAY-PADDING-20261115-001D-P001_nested_pair_grouping/proof.md)

The synthesis binds the accepted conclusions and the decision note. The scientific arguments and independent checks are in the linked proof records.
