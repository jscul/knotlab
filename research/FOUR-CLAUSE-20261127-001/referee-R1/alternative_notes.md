# Four clauses on the same six carriers

Counting the frozen alternating assignment gives **1 of 408** census starts with a grown stage read. Allowing any four three-place, single-word lower clauses on the same six disjoint agreement carriers to force upper 111 absent gives **2 of 408**. The additional start is census entry 426 after two ordinary rounds. Its four choices of upper readings all need a birth. Both positive stages occur among the 233 second rounds read. The broader figure is a retrospective count on the same measured stages. [Fixed-sign counts](alternative_full.json) · [Changing-sign counts](alternative_signed_full.json)

## Which assignments work

Call each signed lower reading true at the agreement value its upper reading counts. A requires both its members, B and C either member. A lower clause using both members of any one pair would determine that upper reading. Four qualifying clauses on these six must therefore each use one member per pair. With A0 and A1 true, choose the only true B to be B_j and the only true C to be C_k. There are four choices of `(j,k)`. Any single-word lower clause excludes at most one of these choices, so each of four clauses must exclude a different one.

When a carrier has the same excluded sign in all its clauses, the A signs must match the upper reading to exclude their assigned choices. Set both B members opposite their excluded signs. All four clauses then allow every choice of the other four readings. To exclude upper 111, that B assignment must make B false. This fixes the upper signs for both B members. The same argument fixes C. For each `(j,k)` one can now use either A member, giving 16 labeled assignments. Every such choice suffices, since any upper 111 has some true B_j and some true C_k.

| A index across the four B,C choices | Labeled assignments | Result on the stages read |
| --- | ---: | --- |
| Alternates on changing either index | 2 | The frozen pattern occurs once and gives three upper readings |
| Depends only on which B holds or only on which C holds | 4 | No all-six cover |
| One A member occurs three times, its mate once | 8 | Four covers, each a distinct upper step on census entry 426 after two rounds |
| Uses the same A member all four times | 2 | 101 five-carrier families across nine stages |

All 16 abstract choices have seven upper words and each single lower-clause deletion restores 111. The last two assignments use five carriers in the clauses. A sixth could be appended freely, so those 101 families are excluded from the all-six count. The earlier positive stage from census entry 420, excluded when drawing the held-out sample, has 44 further three-to-one steps, each needing a birth, as well as 158 five-carrier families. [Abstract checks](alternative_pilot.json) · [Excluded-stage control](alternative_prior_control.json)

A carrier can instead have opposite excluded signs in different clauses. Starting with those two clauses gives four or five raw carriers. Any remaining carrier occurs in another clause along with one or two of the known carriers. Completing those choices and testing every four-clause subset and signed pairing screened all 1,241 measured stages. Across 1,687,769 eligible lower bonds there were 150 six-carrier candidates with at least four lower clauses and a possible sign change. None of their four-clause conjunctions forced the chosen upper 111 absent. On abstract six-bit inputs the test can succeed. Among all 4,096 assignments of clauses to the four singly true B,C choices, 1,480 used all six carriers, four distinct supports and a sign change. Direct truth tables found 332 that excluded 111. The search agreed on all 1,480. [Actual counts](alternative_signed_full.json) · [Full abstract check](alternative_sign_controls.json)

## The four additional readings

On census entry 426 after two rounds the six carriers in one example are A0 `(0,2,5)`, A1 `(8,13,14)`, B0 `(1,7)`, B1 `(9,10,15)`, C0 `(6,11,12)` and C1 `(3,4,16)`. B0 counts disagreement as true. The other five count agreement. In B,C order 00, 01, 10, 11 the clauses use A indices **0, 0, 1, 0**. The underlying four source knots grow to nine. The source has 12,312 allowed assignments among 131,072. Three of the lower clauses share A0, ruling out the frozen form under any renaming.

Only A1, B1 and C1 differ between the four certificates. Each row has the counts directly below the table. [All four certificates and their projected relations](alternative_witnesses.json)

| A1 | B1 | C1 |
| --- | --- | --- |
| `(8,13,14)` | `(9,10,15)` | `(3,4,16)` |
| `(8,13,14)` | `(9,10,16)` | `(3,4,15)` |
| `(8,15,16)` | `(9,10,13)` | `(3,4,14)` |
| `(8,15,16)` | `(9,10,14)` | `(3,4,13)` |

- Each realizes **all 43** six-reading words its four clauses allow. The source assignments per upper word from 000 to 111 are **4,336, 2,000, 4,164, 1,578, 104, 40, 90, 0**. The canonical knot test passes on each of the four independently projected relations.
- Each of 16 named-clause projections, four per certificate, has exactly seven words. All **48 of 48** comparisons of a named clause against an upper reading exhibit variation at a fixed lower triple. The numbers of such lower triples for A,B,C are `(3,4,3)`, `(3,3,3)`, `(3,4,4)` and `(3,3,4)` in clause order for every certificate. Across **275,880** comparisons against all 22,990 bonds of the stage, no bond determines an upper reading. Flipping each signed member while holding the other five fixed also changes its own upper reading on 7, 7, 10, 9, 9 and 10 pairs of attained six-reading words, respectively.
- Deleting each of the four clauses in the abstract conjunction restores upper 111 in every certificate. Deleting each source law in the actual stage restores **50, 18, 24, 18, 12, 10, 30, 6, 6** assignments with upper 111, in source-law order. The first four are start laws and the last five are births. All five births are individually necessary. The four certificates are exchanged by renamings that preserve the start and each grown stage.

The broader count concerns four clauses that by themselves forbid all three chosen readings holding together. Other upper Boolean functions, source exclusions needing additional constraints and the broadened family on the 211 omitted stages were not tested in this search.

## Replay

Use the compilation and signed-clause export commands in the read-stage replay first. The complete input has one row per measured stage. The per-case snapshots can also be created by `read_recount.py --pilot 426/2,5260/2,420/2 --export-pilot-bonds --out read_controls.json`. The upper tests reconstruct ordinary growth with the earlier independent growth rule. Their 426 source stages and bond total agree with the separately enumerated stage snapshot. [Read-stage replay and checks](read_notes.md)

```sh
cd research/FOUR-CLAUSE-20261127-001/referee-R1
ulimit -v 2097152
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
py=../../../.venv/bin/python
"$py" -B alternative_read.py read_all_bonds_5260_2.json.gz --controls --output alternative_pilot.json
"$py" -B alternative_read.py read_signed_0.jsonl.gz --output alternative_full.json
"$py" -B alternative_read.py read_all_bonds_420_2.json.gz --output alternative_prior_control.json
"$py" -B alternative_signed.py read_all_bonds_5260_2.json.gz --output alternative_signed_pilot.json
"$py" -B alternative_signed.py read_signed_0.jsonl.gz --output alternative_signed_full.json
"$py" -B alternative_sign_controls.py --limit 128 --output alternative_sign_controls_pilot.json
"$py" -B alternative_sign_controls.py --output alternative_sign_controls.json
"$py" -B alternative_witness.py read_all_bonds_426_2.json.gz --limit 32 --output alternative_witness_pilot.json
"$py" -B alternative_witness.py read_all_bonds_426_2.json.gz --output alternative_witnesses.json
```

The two one-stage search pilots took under a second each. Each full inventory then took under two seconds in one process with the input ready. The four-certificate full-state replay, including the 275,880 comparisons, took under two seconds. Peak memory stayed below 112 MiB.
