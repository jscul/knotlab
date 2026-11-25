# What widens at one round

A witnessed step uses a third knot that shares a distinction with both members. At the end of an ordinary round, births from the same parent can witness each other in this sense. The proof identifies every such step. Earlier work counted births through a round and supplied the description by down-closed sets. The fixed-round roster, its extra members, the exact finite range of each count, and the effects of short supply are the results here. [Earlier proposition](../../proofs/FIRST-KNOT-20261118-001A/FIRST-KNOT-20261118-001A-P001_two_knots/proof.md) · [Fresh count](../../research/FRESH-COUNT-20261118-001/fresh_count.md)

## The four kinds

In the specified start each of the m knots holds two loose distinctions and has its own shared distinction with each of the other m−1 knots. For every m≥3 and completed round t≥1, take all ordered m-term sums of t−1. Moving one unit between terms is a witnessed step. Attach one further member to each of the m sums with all units in its term. At round one all m attach to the same zero sum. This gives exactly C(t+m−2,m−1)+m members. The count is greatest from a sum as evenly divided as possible at every radius, including after the count departs from its unrestricted value. The cap preserves the description when it supplies at least m distinctions. With m=2 there is no third knot to witness the first join. Both programs give four offshoots in two pairs. [Proof and finite count](../../proofs/WIDENING-ROSTERS-20261125-001A/WIDENING-ROSTERS-20261125-001A-P001_unit_transfers/proof.md) · [Two-knot control](boundary-controls.md)

All 23 starts have one common first join. What distinguishes the four kinds is the number of offshoots that each starting knot makes alongside it. A starting knot that makes one gives an entry that can grow without bound. One that makes two gives two entries each available only once. A starting knot that supplies only the join contributes neither. This identifies the named census cases and gives a sufficient condition on other starts with the same first-round witnesses. It does not classify arbitrary starts after several unrelated joins.

| Starts | Offshoot counts after omitting zeros | Greatest count including the source | Exact range at a fixed round |
| --- | --- | --- | --- |
| Nine census starts | 1, 1, 1 | 3r²+3r+1 | 3r≤t−1 |
| Four census starts | 1, 1, 1, 1 | (2r+1)(5r²+5r+3)/3 | 4r≤t−1 |
| Eight denser starts | 1, 1, 1, 2 | 12r²+2 | r≥1 and t≥3r+2 |
| Two denser starts | 1, 1, 1, 2, 2 | 48r²−48r+24 | r≥2 and t≥3r+3 |

For the denser starts, from t=3 the entries are three nonnegative integers and two or four entries bounded by one, with total t−1. There is one additional member on each pure integer sum. The three unbounded entries account for the quadratic degree in both cases. The once-only choices give different coefficients and cutoffs. In the last row, the greatest one-step count is 23 including the source once t≥6. [Dense-roster proof](../../proofs/WIDENING-ROSTERS-20261125-001B/WIDENING-ROSTERS-20261125-001B-P001_dense_rosters/proof.md)

All six tested growth laws preserve the first row. The ordinary count, ordinary count with retiring, and cap of four with retiring preserve the second. In round two a cap of three cancels every group requiring the short central member. Its four continuing offshoots each begin their own part. Retiring leaves four parts. Waiting or making offshoots leaves a fifth. Some early three-member parts have all pairs one step apart. In every part of size n the greatest count is min(2r+1,n). Only the two uncapped treatments preserve either dense row among the six laws. At round two a retiring cap even gives the same totals, 9 and 12, as ordinary growth while splitting those members into parts.

## The next stages

The archived order fixes a panel of twelve five-knot starts beyond the first thousand, independent of how any of them grew. Two programs grew the starts under both knot laws and counted all members, unique one-step pairs, part sizes and distinct members within each registered radius. They agree at all 4,274 reached stage/law observations. In all 2,350 observations covered by the explicit finite model, a third calculation from its sums matches every member's reach vector up to permutation. The uniform statements above depend on their proofs. [Frozen predictions and cases](../../experiments/WIDENING-ROSTERS-20261125-001C/WIDENING-ROSTERS-20261125-001C-E001_recount/contract.json) · [Exact comparison](../../artifacts/WIDENING-ROSTERS-20261125-001C/WIDENING-ROSTERS-20261125-001C-E001_recount/analysis/comparison.json)

| Actual start and ordinary round | Members | A distinguishing reach count |
| --- | ---: | --- |
| Six knots, each sharing once with each other knot, round 13 | 6,194 | 31, 271, 1,071 and 2,571 within one to four steps |
| Three mutually sharing knots, round 67 | 2,281 | 1,519 within 22 steps |
| Three unbounded entries and two once-only entries, round 41 | 3,284 | 2,030 within 13 steps |
| Three unbounded entries and four once-only entries, round 31 | 6,971 | 3,480 within nine steps |

Seven of the twelve new five-knot inputs reached round eight. Five stalled at round one under the ordinary law, leaving 40 later scheduled stage/law observations unreached. The seven included both single and split rosters. This finite panel has no associated estimate of how common a roster is elsewhere. [Independent stage records](../../artifacts/WIDENING-ROSTERS-20261125-001C/WIDENING-ROSTERS-20261125-001C-E001_recount/referee/stages.jsonl)

## The knot test in full

For each existing knot, project the whole allowed stage onto that knot's own distinctions. The verifier checked that some joint state remains, that the relation excludes at least one state, and that forgetting any one distinction leaves every choice of the others possible. A check at birth with an extension argument and a separate check using the completed support system gave identical verdicts. All 26,668,466 knot-at-stage checks under not-all-equal passed. All 26,668,466 under parity passed. These totals count a persisting knot again at each reached stage and count repeated starts under each registered law. Across final histories the denominator is 2,682,727 knots per knot law. The two growth programs independently agree on the knot totals in each scheduled prefix. Full truth tables were passed to the knotlab test once per distinct projected relation up to renaming, at 3 through 12 places and at 15 places under each law. The wide-table adapter preserves the canonical forgetting test and accelerates ancillary work. [Complete histories](../../artifacts/WIDENING-ROSTERS-20261125-001C/WIDENING-ROSTERS-20261125-001C-E001_recount/knot_test/history/results.jsonl)

## Prior work in the program

Before selecting the order, the objects index was searched for a fixed-round roster and its witnessed steps, and for a first meeting through a further-reaching take. The first search led to the fixed start already described by the proofs linked above and to the widening-roster probe. The older total through a round does not determine which births at that round are one step apart. The second search led to the studies of parts that meet again and the source probe of the most-held rule. Those records measured a growth course after barring parts, while the present question asks which joint states their actual linking distinctions allow. That makes the roster proof the first target and the link test the second. [Earlier fixed-round probe](../KNOTS-WITHIN-REACH-20261125-001/checks/roster_probe/README.md) · [Earlier further-reaching probe](../WHAT-A-BIRTH-CARRIES-20261125-001/checks/reach_further/README.md)

## Roster checkpoint

| Scope | Verdict | Why |
| --- | --- | --- |
| Fixed-round widening rosters | **Status:** Successful | Every member and witnessed step on the named families |
| Local direction — bounded supply | Settled for the six laws | Finite cutoff and cap-three split proved |
| Broader exploration — growth from other starts | Known alternatives | Seven of twelve unused five-knot starts reached round eight |
| G1 Space from a law, G2 Dimension three and G5 Dynamics | Capability gained | Explicit fixed-round counts at every admissible size |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The further-reaching first meetings | 3/3 — decides contact at a meeting | 3/3 — both laws and full records available | Check each physical link and swap the taking law → classify the links and compare actual reach | Selected · started |
| 2 | Enlarge the widening-roster census further | 1/3 — finite coverage | 3/3 — catalog already ordered | Check a second five-knot prefix → finish that prefix | Alternative · deferred |

**STOP** for the four stated widening families. **GO** to the two-step taking rule. Uniform proofs and the independent census settled the fixed-round target, while a separate pair of physical distinctions could overturn the interpretation of the older meeting.
  
**Corrections:** Narrowing. The dense size formulas begin at round three; a finite part saturates.  
**Goals:** B334 substantiated for G1, with G2 and G5.  
**Assumptions:** The marked finite start list and the six growth laws set the census scope.  
**Scaffolds:** The two knot laws and the treatments of short supply were swapped. The first-round offshoot count explains which family each named start enters.
