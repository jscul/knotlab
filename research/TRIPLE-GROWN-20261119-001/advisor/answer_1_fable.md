**Short version:** I think T1 and T2 are true by a lemma, not by luck, so the computation as planned may be a replay rather than a test. I'm answering from your description only and have not opened the THREE-WAY or PARENT-RULE records, so the lemma's two conditions are the thing to check first.

## 1. Flaws

- **Likely tautology (the main one).** If every junction is a three-place parity relation, a triple has three-way reading 2 exactly when it is a three-distinction bond.
  - The junctions are among those triples, and they generate every bond.
  - So the labelled graph contains a generating set of the arrangement, and an isomorphism of it carries one bond set onto the other.
  - Separation is then guaranteed whenever "state" means the arrangement up to renaming distinctions.
  - The pooled regime is covered as well, since reading 2 is far below the cap of 8.
- **What collided before.** On this view the pair table collides only because it records that two distinctions share a junction, not which third one completes it. The three-way reading at value 2 supplies exactly that.
- **Cheap check before freezing.** For each arrangement, confirm that the span of the reading-2 triples has the rank of the arrangement. If it does, write the lemma, run the computation as its sanity check, and record the cheapest separator (reading-2 triples alone, or the histogram of readings).
- **T2 is not independent of T1.** 86 of the 87 reached pairs are carried from the static ones. Report the one created pair separately; it is the only fresh evidence.
- **Pooling.** "None" and "above 8" must be one pooled class, attached or omitted identically on both sides. Choose the regime per pair, not per member.
- **Encoding.** Triple vertices need a colour distinct from distinction vertices and one colour per reading value. Pair readings need to be real edge colours; an unlabelled edge match would pass silently.
- **Stop rule.** Don't stop at the first agreement. The run is cheap, and the count and pattern of agreements is the result.

## 2. Bets

| Prediction | Bet | Note |
|---|---|---|
| T1: all 1,034 static pairs separated | 97% | 99% if the rank check passes |
| T2: all 87 reached pairs separated | 95% | I expect zero "undecided" among the 23 pooled pairs |

An "undecided" among the pooled pairs would itself signal a bug or a failed lemma condition, because reading 2 survives pooling.

## 3. If a pair agrees on both

Do not go to four-way first. Every k-way reading is a function of the bond set, so the first step is to compare the two full bond sets up to renaming (a canonical form of the bond hypergraph, exact, no pooling).

- **Bond sets isomorphic:** no reading of any arity can separate them. The states then differ in something bonds do not see, such as signs, which junctions are presented versus implied, or growth history. The next reading has to be of that kind, for example the sign carried round each smallest bond.
- **Bond sets differ:** the lemma's condition failed, most likely a junction with more than three places. Read off the smallest bond present in one and not the other; its size tells you the arity needed, which may or may not be four.

To check the agreement is real:

1. Recompute both members with exact bonds.
2. Confirm the isomorphism with a second, independent code path, and verify the returned map by hand against the triples.
3. Confirm the two states are distinct by an invariant that does not pass through the state-grouping code that produced the pair.
