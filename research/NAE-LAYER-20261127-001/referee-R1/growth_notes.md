# Ordinary growth and the loose projection

On all 5,111 funded census starts, every pattern on the round-one loose distinctions occurs. This includes all 500 recorded cases and all 4,611 eligible cases outside the recorded prefix. The recorded 500 include eight of the ten funded tree-shaped starts. A connected two-holder start with at least three knots has a free loose set at every funded round from round one on. A single ternary knot gives 62 of 64 patterns after a funded first round, and two ternary knots sharing one distinction give 254 of 256. Both become free on the current loose set at round two. [Counts and witnesses](growth_results.json)

## Why the current loose set becomes free

Use the mathematical multigraph whose members are knots and whose links are shared distinctions. Each distinction has at most two holders. Each knot has at least three places. Parallel links represent two shared distinctions of the same pair of knots. Treat each connected component separately.

**A component containing a cycle admits every assignment on its loose distinctions.** Fix those values and choose one cycle, allowing a parallel pair. Choose a spanning forest of the other knots rooted at the members of that cycle. Give arbitrary values to shared distinctions outside the cycle and the forest. Process knots in the forest in leaf-to-root order. At a nonroot knot, choose the value on the one shared distinction to its parent last. If its other values agree, choose the opposite value. Otherwise either value works. For an even cycle, assign alternating values around it. For an odd cycle, choose one cycle member as the exception. Its third or later place already has an assigned value. Alternate the cycle values with both cycle distinctions at that one knot opposite its assigned value. All knots now satisfy not-all-equal.

**A component with no cycle excludes exactly two complementary loose patterns.** Root the tree. At every nonroot knot, given all loose values below it, the part below it permits either both values of its shared distinction to its parent or exactly one. If a child permits both values, that child can take the opposite of the parent value. If every child permits only one, the parent value is forced precisely when the child values and the knot's own loose values all agree. At a leaf the same condition tests its loose values alone. Induction gives exactly one loose pattern below a nonroot knot forcing parent value 0 and exactly one forcing parent value 1, with the two patterns complementary. At the root an assignment fails exactly when every child is forced and all the root's known values agree. This gives two complementary failures, including the isolated-knot case.

**A funded round on a connected tree of at least three knots creates a cycle.** If every knot holds a loose distinction, take two neighbours of any knot of degree at least two. If some knots hold no loose distinction, take the smallest connected subtree containing all of them. An end knot of this subtree holds no loose distinction. It has at least three distinct neighbours in the original tree and at most one inside the subtree, so two of its neighbours hold loose distinctions. In either case the two live knots have a common old neighbour. The policy includes their pair or a larger group containing it. That birth, its two parents and their common neighbour close a cycle. The cycle persists because the rule appends knots and keeps all old distinctions and their old holders. For a one- or two-knot tree, the first round makes only offshoots, and leaves the component a tree. At least two offshoots of one parent then qualify for a join in round two.

## Why fixed earlier readouts are preserved

Every new knot has at least one fresh distinction in this two-holder class. To prove that its law is never already implied, fix all its old inputs to 0 and temporarily remove them from the earlier presentation. Each old knot loses at most one place, so the remaining arity is at least two. The shared distinctions and the connected components are retained. In a component with a loose distinction left, choose a spanning tree rooted at a holder of such a distinction. Process the other knots as above, using the loose distinction at the root last. A component with no loose distinction has a cycle. The cycle argument works whenever it is even or its odd cycle has a knot with another place. The remaining case is a component that is entirely an odd cycle with arity two. Every knot there lost exactly one input to the new knot. Give all residual distinctions value 1, then restore the removed zeros. This satisfies all old knots with the inputs to the proposed birth all equal. It rules out the zero-fresh case. The least fresh count is consequently the maximum of one, three minus the input count, and the lookahead demand. [Earlier growth freeze](../../NAE-GROWTH-20261119-001/preregistration.md) · [Earlier no-implication result](../../NAE-GROWTH-20261119-001/nae_growth.md#why-it-holds)

Given an earlier allowed state, each birth can use its own fresh distinctions to get both values on its support. The new fresh sets are disjoint. Thus restriction onto the earlier distinctions is surjective, preserving the exact range of every fixed readout on them. Each new knot has enough loose distinctions for the next complete round, by the lookahead count. These observations apply inductively at every later finite round. [Earlier projection argument](../../BINDING-20261126-001/referee-R1/report.md#what-holds)

For example, the funded six-knot chain has ten original loose distinctions and misses two patterns there. Both are still missing on those same ten distinctions through round four. The current ten loose distinctions are fully free at every measured round from one through four. The single-knot start gives three offshoots in round one. Each offshoot reads its own fresh pair as + on 00, − on 11 and 0 on a mixed pair. The three readouts give 25 of 27 triples and each pair gives all nine. They still have exactly that joint range after round two, when the stage contains cycles. The six carrier distinctions have then been taken into new knots, and the current three loose distinctions give all eight patterns. The Boolean indicators of the three 00 reads give seven of eight triples, with only 111 missing. This relation passes K1–K3 at round two. Deleting the original knot allows 111 and all other triples. [Exact projection data](growth_results.json) · [Round-two check](growth_relation_round2.json) · [Deletion control](growth_relation_delete.json)

## Replay

The reconstruction derives the joining roster from pairwise overlap witnesses and maximal candidate sets. It uses the archived allocation order only to match literal distinction names. On 33 earlier saved not-all-equal round-one stages, the result matches every recorded support, parent set, consumed and fresh identity, and demand at birth. This comparison covers 359 support rows and 199 births. The reconstruction imports neither the author's readers nor the shared growth implementation. The 7,075 starts are read as literal raw inputs. [Earlier archive](../../../artifacts/ENTANGLEMENT-READ-20261120-001B/ENTANGLEMENT-READ-20261120-001B-E001_separated_readings/exact_readings.json.gz) · [Implementation](growth_rule.py) · [Audit](growth_audit.py)

The census has 1,734 stalls and 230 already closed starts. All 5,111 funded first rounds meet the 14-loose cap. The archived prefix ends at index 707 of the raw starts. The 500 archived rows represent 64,470 allowed patterns, and the additional 4,611 funded rows represent 196,434. The funded seven-knot tree has 55,566 start states and 4,094 of 4,096 start loose patterns. It has 16 knots and 32,768 of 32,768 loose patterns after the first round. After round two its 19 loose distinctions are also fully free by direct query. Rounds three and four were reconstructed and checked by the structural condition.

The extension used 30 labelled draws with replacement at each of six, seven and eight knots. Each pair meets with probability one third, meeting multiplicities are uniform on one or two, and loose counts are uniform on zero, one or two. A draw is retained when it is connected, has at most 18 distinctions and every knot has at least three places. The seeds are 20261127 plus the knot count. Of the 90 draws, 31 funded the first round and all 31 were followed through round four. The small-arity and connectivity checks certify each reconstruction. Complete direct projection queries were also run for 31, 30, 24 and 18 of those stages at rounds one to four, respectively, using a loose count cap of 16. The other direct queries and rounds beyond four were not run. The full replay took 3.77 seconds and peaked at 119,820 KiB under the two-GiB virtual memory cap. [Pilot](growth_pilot.json) · [Run](growth_results.json)

```bash
r=research/NAE-LAYER-20261127-001/referee-R1
ulimit -v 2097152
/usr/bin/time -f 'wall=%es peak=%MKiB' .venv/bin/python -B "$r/growth_audit.py" --pilot > "$r/growth_pilot.json"
/usr/bin/time -f 'wall=%es peak=%MKiB' .venv/bin/python -B "$r/growth_audit.py" > "$r/growth_results.json"
```

The three Boolean indicators are `a`, `b`, and `c`. The clause lists below derive each from one offshoot's fresh pair. The round-one check pilots the same projection on a smaller support. The two round-two checks include the full grown relation and the deletion of the source law.

```bash
r=research/NAE-LAYER-20261127-001/referee-R1
ulimit -v 2097152
export PYTHONPATH=tools
source_law='d0 d1 d2; ~d0 ~d1 ~d2'
round_one='d0 d3 d4; ~d0 ~d3 ~d4; d1 d5 d6; ~d1 ~d5 ~d6; d2 d7 d8; ~d2 ~d7 ~d8'
round_two='d3 d5 d9; ~d3 ~d5 ~d9; d4 d7 d10; ~d4 ~d7 ~d10; d6 d8 d11; ~d6 ~d8 ~d11'
readouts='~a ~d3; ~a ~d4; a d3 d4; ~b ~d5; ~b ~d6; b d5 d6; ~c ~d7; ~c ~d8; c d7 d8'
/usr/bin/time -f 'wall=%es peak=%MKiB' .venv/bin/python -B -m knotlab check \
  --cnf "$source_law; $round_one; $readouts" --loops a b --contact c \
  --witnesses d0 d1 d2 d3 d4 d5 d6 d7 d8 --json > "$r/growth_relation_pilot.json"
.venv/bin/python -B -m knotlab check --cnf "$source_law; $round_one; $round_two; $readouts" \
  --loops a b --contact c --witnesses d0 d1 d2 d3 d4 d5 d6 d7 d8 d9 d10 d11 \
  --json > "$r/growth_relation_round2.json"
.venv/bin/python -B -m knotlab check --cnf "$round_one; $round_two; $readouts" \
  --loops a b --contact c --witnesses d0 d1 d2 d3 d4 d5 d6 d7 d8 d9 d10 d11 \
  --json > "$r/growth_relation_delete.json"
```
