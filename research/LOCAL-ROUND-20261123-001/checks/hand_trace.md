# The thread's hand trace of the advisor's counterexample

Epic `LOCAL-ROUND-20261123-001`. Worked by hand before the freeze from the definitions alone, then compared with the earlier
study's engine ([new_start_check.txt](new_start_check.txt)) and, after the runs, with the study's engine
(the trace in `artifacts/LOCAL-ROUND-20261123-001A/LOCAL-ROUND-20261123-001A-E001_local_round/listings/`, the file of the
advisor's order). All three agree.

**The start.** The cycle of eight with three extra dead knots: members 0 to 7, a dead knot between each consecutive pair, and
three more between members 0 and 4, 1 and 5, 2 and 6. Each member holds three loose distinctions. Members 0, 1, 2, 4, 5, 6
are in three joinable pairs each; members 3 and 7 are in two. No three members are pairwise joinable. Write (i, j) for the
join of members i and j.

**Round 1 of the complete rounds.** Eleven joins and one offshoot each of members 3 and 7: 13 births. Under RATION-3 every
new knot holds three.

**Round 2.** The children of one member are pairwise joinable through it. A join whose two parents have three children each
is in four pairs and holds three, so it is short. Counting pairs for each join:

| Join | Pairs through its first parent | Pairs through its second parent | Owes |
| --- | --- | --- | --- |
| (0,1), (0,4), (1,2), (1,5), (2,6), (4,5), (5,6) | 2 | 2 | 4 |
| (0,7), (6,7) | 2 | 2, the offshoot of member 7 counted | 4 |
| (2,3), (3,4) | 2 | 2, the offshoot of member 3 counted | 4 |

All eleven joins are short and wait. The two offshoots owe two, are not short, lose both their groups, and release three
offshoots each: 6 births.

**Round 3.** The eleven waiters are read against one another. The offshoots of members 3 and 7 have acted, so the joins
(2,3), (3,4), (0,7) and (6,7) now owe three and are not short; the other seven owe four and wait a second time. The pairs
(2,3) with (3,4), and (0,7) with (6,7), have no short member and join.

**Round 4.** Seven waiters: (0,1), (0,4), (1,2), (1,5), (2,6), (4,5), (5,6). Now (1,5) is in two pairs through member 1 and
two through member 5, owes four and waits a third time; each of the others owes two or three and acts.

**The order that defeats R2.** Make every start birth except the offshoot of member 3: 12 births. Member 3 is still a
member, so the joins (2,3) and (3,4) are not weaned. Every other join is weaned, and so are all its brood-mates one step
away, so R2 lets the join (0,1) read. What it reads is the brood without the offshoot of member 3:

- First reading: (2,3) and (3,4) owe three, not four. They are read as not short, and their pair is read as a join.
- Second reading, without them: (0,1), (1,5) and (5,6) owe four and wait; the other six act.
- Third reading: (0,1), (1,5) and (5,6) alone. None is short, and the pairs (0,1) with (1,5), and (1,5) with (5,6), are read
  as joins.

R2 therefore allows a join of (0,1) with (1,5). The complete rounds never make it: there (0,1) acts in round 4, joining
(0,4) and (1,2), while (1,5) waits. That is a mismatch at the thirteenth birth. Under R3 the birth is not allowed, because
the brood is not all-weaned while member 3 is a member.

**What it shows.** Each further wait of a knot depends on which of its brood-mates were short one reading earlier, and that
depends on knots one more step away. A guard that checks a fixed number of steps is therefore exact only up to a fixed
number of waits.
