Nothing was run (I have no shell): every claim below is either read in a file at the line given, or worked by hand and `unverified`.

**Bottom line.** Both directions are one question at two layers: under parity a presentation is a completed system (every distinction held twice) with one knot left out, and the loose set names that knot. `STATES-GROWTH-20261119-001` (D1, refereed) already has this for the first layer; neither study applies it to the nine facts.

## 1. Tree or loop

Read in the files:
- **Carriers.** Each ring fact R_i is carried by the ring's eight start loose distinctions (12–19, 20–27, 28–35), and p_i, q_i by round-1 fresh distinctions (`natural_places.json` 164–254). So R_i's carrier is exactly the inputs of the six births whose fresh distinctions carry p_i and q_i.
- **Deletion test.** `natural_places.py` line 434 deletes first-round births only (`born_in[0]`). "Frees only its quadruple" was never tested on the 18 start laws.

By hand:
- **Law sets.** The tree's four relations are the 18 start laws and each ring's six round-1 births, pairwise disjoint. Each quadruple is the 18 start laws plus one ring's six. Check: deleting any start law should free all three quadruples.
- **Holders.** The loop basis gives every R_i three holders (root and two quadruples); the 12 against 15 place occurrences is exactly this. No basis containing two quadruples keeps every place at two holders or fewer.
- **Count to check.** Of the 840 bases, I predict 20 keep every place at two holders, and 12 of those have four knots meeting in a ring. One such is root, T1, T2 and the six-place relation, with R3, p3, q3 loose. Exactly one of the 20 has the six family facts loose: the tree.
- **What chooses.** The holder rule (the engine's own, `rival_growth.py` 86–87) excludes the loop but not a ring. Among the 20, the choice is which places are loose, which is direction 2's datum.
- **Later rounds and K1–K3.** Neither chooses. Relations among old distinctions never change, and all 11 pass (`natural_places.py` 413).

Why "shorter" is ours, three counterexamples:
- **Counted in distinctions.** A ring triple is six births' laws side by side (20 distinctions; births of one round share nothing), so it is not a minimal relation and fails the glossary's knot definition at that level. Each quadruple (28) is one minimal relation: the start with one ring's births is connected.
- **Unequal rings.** On rings of 10, 4 and 4 knots the big ring's quadruple should be shorter than its triple in distinctions (36 against 40) and longer in places.
- **The first layer itself.** Its knots are not a shortest basis. On census start 3097 (as described in the hivemind), knot 4 has six places and knot 3 + knot 4 has five.

## 2. Marking the loose distinctions

Read: the referee's witness is one completed system of 16 knots with row 0 or row 5 left out (`metric_witness.py` 56–79). Its two presentations have different loose sets after round 1: 15–20 against 21–26 (`metric_witness.json`, births). So it is not a counterexample once loose is marked.

By hand: the family partition and the tree are a function of (allowed states, loose set) at every funded round. No pair with the same states and loose set differs in them.
- **Same holder.** Two loose distinctions have one holder when the pair is itself an allowed change.
- **Candidates.** Their holders are candidates when some allowed change of four distinctions holds both and no other loose one (matches `fastlib.candidates`, 12–22).
- **Direct cost.** d + 2t + 2 is the least allowed change holding exactly one loose distinction of each family.
- **Growth.** The same holds for everything Lemma R says growth reads. From round 1 on, the loose set is the distinctions new that round, so two successive stages suffice.

Checks: apply the three rules to the 4,096 states with each loose set (expect 5, 8 and 7, 7). Then, on `STATES-GROWTH`'s 2,802 same-state pairs, take those with equal loose sets (expect the same next round in all).

Smallest pairs:

| What is the same | What differs | Presentations |
| --- | --- | --- |
| 16 states, 7 distinctions | loose sets; families 2 against 1 | (x1 x2 y), (y z1 z2 w), (z1 z2 v) against (x1 x2 v w), (y z1 z2 w), (z1 z2 v) |
| 16 states, 8 distinctions, no doubled sharing | loose sets; families 2 against 1 | a ring of four with one loose each, against the same completed system (a fifth knot sharing one distinction with each ring knot) with a ring knot left out |
| 8 states and the loose set {l, m} | holdings only; families the same | (a1 a2 c l), (b c m), (a1 a2 b) against (b c l), (a1 a2 c m), (a1 a2 b) |

I did not search for the smallest pair with three families each.

## 3. What both overlook

- **The loop is not a lead for the tower.** On the six family facts both bases are one relation, the sum of the start's laws: the tree is that relation plus three definitions, the loop is it written four times. With four rings, each ring fact lies in three of the four five-place relations, so the cycle of three is special to three rings.
- **Recursion test.** Run ordinary growth on the four-knot tree presentation (places 3, 3, 3, 3; loose 0, 2, 2, 2) and compare with what growth does to the nine facts. I predict they differ: growth adds one two-place copy per family per round, and ordinary growth never makes a two-place birth.
- **A referee would press** that two holders at the second layer is our requirement, and that direction 2's function is entailed, so archive agreement is not evidence.
- **Word.** "Family" has two senses in the record (`FAMILIES-THAT-MEET` and the classes of live start knots), and I found no glossary entry for it.

**Third direction.** I would take one short statement covering both layers, with the checks above, then put the same two questions under not-all-equal. There no law is a sum of others, and the states fix the presentation on 79.8% of small stages (`STATES-GROWTH`), so nothing is entailed.

One entry added to `docs/ADVISOR_HIVEMIND.md`, dated 2026-11-27 to match the studies (the session clock says 26 November); nothing else touched.