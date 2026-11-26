# The advisor's answer (26 November 2026), read-only in the repository

# Advisor's answer: both distances on grown rings

I read `distances.py`, `classes.py`, all of `rings_dist.jsonl`, the relevant lines of `forbid.py` and `sides.py`, and searched the census and extension files by pattern. I ran nothing (no shell), so every argument below is by hand and `unverified` unless I say it was read from a file.

## 1. The two programs

**Horton search (`horton_change`): gives the true minimum, given H.** Status: an argument, `unverified`.
- Take C a least element of S outside H; it can be taken to be a simple cycle. Pick a vertex s on C and the code's tree from s.
- C is the sum of the tree's fundamental cycles over the non-tree edges of C, so one of them, for an edge e = (u, v) of C, is outside H.
- Its size is at most d(s,u) + d(s,v) + 1 ≤ |C|, since C itself supplies the two paths.
- This holds for any tie-breaking, with parallel edges (the code loops over every keyed edge) and with the extra unconstrained vertex, which is an ordinary vertex here.
- `nx.single_source_shortest_path` builds each path as its parent's path plus one vertex, so it is a consistent tree; I read this from memory of networkx, not from its source.

**The weak point is H, not the search.**
- `shortest_paths_edges` stops at `TIE_CAP = 64` ties and no row records whether the cap was hit. A truncated H can only be too small, which gives spurious classes or a too-small d_change.
- Ties that differ only by a parallel edge are harmless, because the 2-cycle is itself a move. Ties through different vertices are not covered by that.
- Check: count cap hits per row. `classes.py` enumerates exactly up to dimension 22; the one overlap I could confirm is ring 5 round 1 (dim S 15, dim H 14, the upheld 32,768 states in two classes). Run it on every row that fits.

**`graph()` sends any distinction that does not have exactly two holders to the extra vertex when free, and drops it when pinned.**
- `elif not pinned` catches three or more holders as well as one.
- I found no guard on the holder count in `forbid.py` (pattern search only). Add an assert that it is 1 or 2 on every grown stage.

**Solver (`read_distance`): exact for two classes, an upper bound for four or more.**
- With two classes, every g outside H imposes the same condition, so one generator is enough.
- With four or more, `gens[:4]` can all fall in the same class mod H, and labels even on that class are missed.
- Read from the files: no census row with distances has four or more classes; six extension entries do (on five lines: 61, 63 twice, 87, 93, 239), all with d_read 2. Those values are upper bounds, so the "3 or less" claim is not affected.
- A timeout returns "not run" and discards the best found so far (one row: ring 10 pinned, round 6).

**Duality flags: one is wrong and two say nothing.**
- **"The least change is also a class label" is falsely true on pinned even rings.** It tests only even overlap with H, never odd overlap with some cycle. On n = 8 and 10 pinned (lines 30–35, 44–48) it is true with d_change even. There r·r = 0 and S = H + ⟨r⟩, so r is even on every allowed change: a sum of knot laws, not a label. Your sentence "on even rings the least change is not a label" is right; the file contradicts it by this error.
- **"Overlap oddly" is forced with two classes** (a label is odd on everything outside H), so "share no distinction" is forced false. Neither carries information in any ring row.
- **The flags describe one minimiser each, chosen by z3 and by loop order.** Ring 9 free round 2 has "label is an allowed change: true" once, and the settled odd rows have it false although r is a least label there.
- **Nothing in the file shows r is the old ring.** Write z and r as lists of distinctions and check r against the n old shared ones.

## 2. Counterexamples to the reading

**"Both distances growing": the start's length caps it.**
- Read from all 56 rows: min(read, change) ≤ n in every one.
- Odd rings: both equal n and stay there.
- Even free: read stays n while change is 2r + 3.
- Even pinned: change stays n while read is 2r + 1.
- So growth makes the class (round 0 has one class everywhere), but the long distance is the supplied ring's n. No row has both above n, and none has both growing with the rounds.
- The even pinned case rests on n = 8 and 10 only; n = 4 and 6 pinned have one class, and n = 12 was not run.
- H comes from the motion study's rule that only least changes through each distinction are moves. The class and both distances are relative to that supplied rule; a referee will press this first.

**Is (−1)^(r·x) move-invariant and r-odd?** Yes where the flag is true and d_change is odd: r·h = 0 on a basis of H gives invariance, and r·r = n odd gives the sign change. Those rows are:

| n | Free, rounds | Pinned, rounds |
|---|---|---|
| 5 | 1–6 | 1–6 |
| 7 | 2–6 | 1–6 |
| 9 | 3–6 | 1–6 |
| 11 | 4–6 | 1–6 |

It fails in the early free rows (7 at round 1, 9 at rounds 1–2, 11 at rounds 1–3), where the least change is 2r + 3 and not a label.

**"Odd rings single out the signed weighting" fails: every two-class row has it.**
- With two classes, any two labels differ by something even on all of S, so every label gives the same function on the allowed states: +1 on the class of the all-zero state, −1 on the other.
- Ring 4 free round 1 has it through its label of 4 distinctions.
- What odd rings add is narrower: one set r is both a least change and a least label.
- The "plus" class is fixed only because the all-zero state is allowed; with loose pinned at other values there is no canonical choice.
- This character sums to zero over the allowed states, so it is a signed function and cannot be a weighting of samples (the same point as the earlier SIDE-SIGN entry).

**Is anything recorded weighting by it?** Not in `sides.py` lines 203–232, which I read: W1 and W1c are quadratic, W2 is a product of two parities, W3 and W3m are differences of indicators, W4 is the sign of a count difference. The motion study uses the old-ring parity as a read, per the upheld standing fact. I did not search the rest of the record, so "no recorded reading" is `unverified` beyond that file.

## 3. Do these rings answer the next-layer question?

No. One ring gives one two-valued whole-loop fact with nothing to relate it to; that is a candidate distinction, not a layer.

What would answer it, in the same linear terms:
- **Next-layer distinctions:** the labels z_i of several rings in one structure.
- **Next-layer knot:** a set of them whose sum is in the span of the knot laws, so their parity is forced on every allowed state while no single z_i is.
- **Next-layer move:** a least class change that changes exactly two of them.

The test: grow two or three odd rings that meet (the meeting-clusters arrangements), then compute dim S/H and the labels. If S/H has one independent bit per ring and no forced parity, the facts are free bits and no next-layer law exists there. If three rings give a forced z_a + z_b + z_c, that is a next-layer parity knot. Predict which before running. TWO-CLASS-SIGN found growth treats the classes alike, so my guess is free bits unless the rings share knots; that guess is `unverified`.

The hivemind entry is added. I touched nothing else.