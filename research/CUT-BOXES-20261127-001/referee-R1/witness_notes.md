# A strict box on a connected open system

One ordinary round from ten three-place not-all-equal knots creates two knots and a strict box. Both loose distinctions belong to its six pairwise disjoint carriers. Deleting **any one of the twelve laws** restores the missing upper word. The starting supports and choice of carriers were supplied by the [predecessor's counterexample](../../UPPER-GROWN-20261127-001/referee-R1/open_witness.json). The [independent assignment counts](witness_states.json) below use those supports and carriers as their only inputs.

Number the ten start knots from zero in the order shown.

```
(4,5,6)     (4,7,8)     (0,9,10)    (9,11,12)    (1,5,12)
(13,14,15)  (7,10,11)   (3,14,16)   (2,13,16)    (6,8,15)
```

The four loose distinctions are 0, 1, 2 and 3. Among their holders, knots 2 and 4 share with knot 3, and knots 7 and 8 share with knot 5. These are the only two eligible parent pairs. Each spends one loose distinction per parent. Their new laws are **(0,1,17)** and **(2,3,18)**. The independently reconstructed ordinary-growth rule gives exactly those births with zero further demand. The twelve knots are connected. Only 17 and 18 are loose. Identifying them makes a closed twelve-knot system, and separating the two occurrences recovers this example.

| Reading | A0 | A1 | B0 | B1 | C0 | C1 |
| --- | --- | --- | --- | --- | --- | --- |
| Carrier for agreement | (0,9,17) | (2,3,16) | (1,5,18) | (7,10,13) | (4,6,8) | (11,12,14) |

Of 524,288 raw assignments, **14,554** satisfy all twelve laws. At each of the eight choices of one A, one B and one C, exactly 111 is missing and all four words on each pair occur. For all 72 combinations of a source knot and a reading, fixing the knot leaves both reading values on at least two fixes. Each of the 18 carrier members has at least 766 allowed single changes that flip its reading.

Let P, Q and R record disagreement within the A, B and C pairs. If PQR were 111, precisely one A, one B and one C would be 1, violating the lower clause on those three choices. The source gives **34** words on the six readings. The eight lower clauses alone give **37**. Both give the seven upper words other than 111. Removing any one lower clause from their conjunction restores the upper word by setting precisely that clause's three readings to 1. All 24 combinations of a lower bond and an upper reading leave both upper values on at least five fixes on the source. The canonical K1–K3 test passes in all three contact roles for eight lower relations, the upper relation from the measured six-reading image, and the upper relation from the eight clauses. [Counts, word images and all 30 role checks](witness_states.json)

Deleting source laws 0 through 11 in turn restores upper 111 in **50, 62, 102, 186, 96, 24, 102, 112, 86, 24, 90 and 50** assignments. The last two are the two birth laws. Testing all 4,096 source-law subsets for each lower exclusion gives one minimal sufficient set apiece, of sizes **7, 3, 7, 3, 6, 3, 5 and 3** in product order. Every one omits at least one member of its three carriers. A local search requiring the sufficient essential holders to contain the carriers misses all eight of these bonds at any holder cap. [Single-deletion witnesses and omitted carrier members](witness_states.json)

## Which part of the opening argument holds

Consider a raw assignment that restores the forbidden upper word after deleting a single source law H. The signed box definition puts exactly one lower reading from each upper pair at its forbidden value. Thus exactly one lower clause is violated. Every distinction held only by H must be in one of that clause's three carriers. Otherwise flipping that private distinction repairs the violated not-all-equal law H, preserves every other source law and leaves the lower violation in place, which contradicts the original lower relation. In particular a necessary holder cannot have private distinctions confined to opposite readings of the same upper pair. This sharpens the unread-private-distinction argument and allows the two fresh distinctions here. The certificate checks the criterion on all 90 and 50 assignments restored by deletion of the two birth laws.

The displayed box persists on every later funded finite ordinary stage. At each of the four fixes of 17 and 18, each of the six readings still takes both values, with at least 190 raw assignments per value. Later knots can meet these twelve only through 17 and 18. Two old assignments agreeing there therefore admit the same future assignments. Every old assignment extends because each birth can satisfy its own law at a fresh distinction. It follows that no later knot determines any of the six readings, all word images persist, and all twelve deletion witnesses extend with the listed meeting pattern held fixed. For the single-member flip test, the following round adds (17,19,20) and (18,21,22). Choose opposite values on 19 and 20 and on 21 and 22. This gives the same extension on new distinctions for every old assignment. All single-member tests are preserved at all later funded finite stages. This reasoning uses finite stages only.

## Limit on which rounds can produce this whole system

With ordinary not-all-equal growth and at most two holders per distinction, a connected **whole stage** of twelve three-place knots with exactly two loose distinctions on distinct holders can arise after one round, as above. It cannot arise after two or more rounds. All older knots persist. Each birth has at least one fresh distinction and spends all earlier loose distinctions collectively with its siblings. The last round must therefore have consisted of exactly two births, each with two parents and one fresh distinction. The preceding ten-knot stage had four loose distinctions.

If that preceding stage had itself been born from an earlier stage, its four loose distinctions were distributed over two, three, or four newborns. A three-place birth with one fresh distinction has two parents, and one with two fresh distinctions has one parent.

- With two newborns, there is at most one distinct parent pair for the last round.
- With three, the newborn holding two loose distinctions must join each of the other two. That newborn has a single parent, so both others share this parent too. All three share with the same knot. They therefore require all three pair births, exhausting the two newborns holding just one loose distinction apiece.
- With four, the four were two-parent births. Their sources form a connected six-knot start with eight loose distinctions and five shared distinctions. Each shared distinction connects two different knots. Five is the minimum to connect six, so the sharing is a tree. A leaf holds two loose distinctions and must join two distinct live knots through its only neighbour. That neighbour must have three neighbours and its other two must both be live. If the tree has no knot with three neighbours this is impossible. If it has just one, all three leaves would need to adjoin it, leaving no room for the two other knots. If it has two, they adjoin each other and each holds no loose distinction, violating the leaf condition. These are all possibilities.

The finite check considered the 1,470 parent rosters in the three-newborn case and the 1,170 labelled six-knot trees of degree at most three in the four-newborn case. None satisfies the corresponding necessary condition. This limit concerns the twelve-knot stage itself. The same box can occur inside a later, larger stage. [Finite checks](witness_round_limit.json)

## Replay and search limits

Run from the repository root with one process, a 2 GiB virtual-memory cap and one numerical-library thread.

```sh
ulimit -v 2097152
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
r=research/CUT-BOXES-20261127-001/referee-R1
.venv/bin/python -B "$r/witness_states.py" --limit 24576 --out "$r/witness_pilot.json"
.venv/bin/python -B "$r/witness_states.py" --out "$r/witness_states.json"
.venv/bin/python -B "$r/witness_round_limit.py" --limit 40
.venv/bin/python -B "$r/witness_round_limit.py" > "$r/witness_round_limit.json"
```

The witness prefix took 0.036 seconds, giving a literal full-state estimate of under one second. The complete assignment and deletion check took 0.88 seconds and about 21 MiB. The 40-row round-limit pilot took under a millisecond of computation and the full check took 0.007 seconds. [Assignment checker](witness_states.py) · [Round-limit checker](witness_round_limit.py)

One additional exploratory control kept the same six carriers and two birth laws, exchanging shared distinctions between two starting knots. It screened all 234 distinct one-exchange and 24,777 new two-exchange support lists in the declared order. None both reproduced the two births from a connected start and realized the full 37-word abstract relation. These are labelled perturbations of this witness. Other carriers, exchanges beyond two, and the prevalence of such growth over starts were not tested here. The 1,000-case prefix at depth two took 0.10 seconds and the complete control took 1.82 seconds. [Procedure](witness_exchange.py) · [Counts](witness_exchange.json)

```sh
.venv/bin/python -B "$r/witness_exchange.py" --depth 2 --limit 1000 --stop-exact --out "$r/witness_exchange_pilot.json"
.venv/bin/python -B "$r/witness_exchange.py" --depth 2 --stop-exact --out "$r/witness_exchange.json"
```
