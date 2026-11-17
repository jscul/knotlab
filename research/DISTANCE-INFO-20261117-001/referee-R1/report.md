# Referee report DISTANCE-INFO-R1 (fresh code, no Codex)

**Verdict: the census is confirmed, but its reading of A97 is a Block.** Every frozen count recomputes exactly with the referee's
own code. Three things change what the census says about A97, the owner's reading that distance is the only form of information.

1. **Another pairwise distance carries everything.** Take the distance between two distinctions to be how many allowed states
   tell them apart. That plain pairwise table determines every not-all-equal relation at n = 4, 5 and 6: 16 of 16, 1,023 of
   1,023 and 97,248 of 97,248. It also determines all 46,445 relations sampled at n = 7.
   - So "A97's plain reading is overturned" holds only for bond distance.
   - "It survives only if distance includes orientation" is false.
   - **Block** on those readings and on A97's new status text.
2. **The orientation result rests on counting ties as bonds.** The study counts two-place ties as bonds of size two. The glossary
   says "a chain of two-place ties has no knot, and so no bond distance" (LOGIC-AXIS, proved). With the glossary's bonds,
   "bonds with their excluded states" fails at n = 5: 883 readings for 1,023 relations. **Narrowing.**
3. **The pre-registration's injectivity claim is false at n = 6.** It says distinct satisfiable knot sets give distinct relations
   for n ≤ 7. In fact 999,018 satisfiable knot sets give 97,248 relations. The census counts relations, so no number changes, but
   "bases" are relations, not knot patterns. **Narrowing.**

## What holds

- **Order.** The freeze, `d8e3b518c`, is at 17:41:21 UTC; the census ran from 17:41:27 to 17:46:38.
- **The definitions.** The pre-registration states up front that "distance" is bond distance and not steps apart. It also states
  that SPACE-ORDER's withdrawn reading is not used, and what each outcome would mean.
- **The census recomputes exactly** (`referee_census.py`, `.json`). The referee's code is independent: knot sets by a subset
  recursion; projections, bonds and readings by bit masks over the 2^n states.
  - **Relations.** 16, 1,023 and 97,248 at n = 4, 5 and 6.
  - **The readings** under the study's bond definition (bonds of size 2 or more):

    | Reading | n = 4 | n = 5 | n = 6 |
    | --- | ---: | ---: | ---: |
    | (a) | 12 | 293 | 10,012 |
    | (b) | 12 | 362 | 11,560 |
    | (c) | 16 | 593 | 54,229 |
    | (c-s) | 16 | 662 | 56,722 |
    | (c′) | 16 | 1,023 | 97,248 |

    Every count is as published. (c′) is also injective on the referee's own 46,445 sampled relations at n = 7.
  - **The verdicts.** D1 to D5, D4's failure included, follow.
- **The smallest collisions are as decoded.** At n = 4 three knots allow 8 states and four knots allow 6, and every pair is at bond
  distance 2 in both.
- **Size-two bonds are exactly ties here.** The relations are closed under flipping every value, so a two-place projection that is
  not full keeps 2 of its 4 joint states: equal or unequal. "Size-2 bonds = ties" is therefore right for the study's definition.
  Whether such bonds should count is §2.

## 1. Another pairwise distance carries everything (Block on "plain reading overturned" and "only with orientation")

A97 in the owner's words: "Distance is the only form of information. That's the entire basis of the 'this versus that' distinction
in the smallest emergent unit." The study formalizes "distance" as the glossary's bond distance and tests whether the pairwise
table determines the allowed states. That is one formalization. Another, read from the allowed states alone and pairwise, is how
far apart two distinctions are across the allowed states:

**(e)** d(u, v) = the number of allowed states in which u and v differ.

It is a distance: d(u, u) = 0, and it obeys the triangle inequality, since u ≠ w forces u ≠ v or v ≠ w. It reads "this versus that"
directly: how often the two take different values. A97's own Challenge cites `OVERLAP-READ-20261111-001`, "equal pair counts give
equal states", which is this kind of reading.

| Reading | n = 4 | n = 5 | n = 6 | n = 7 (sampled) |
| --- | --- | --- | --- | --- |
| (a) bond distance of every pair (the study's "plain reading") | 12 / 16 | 293 / 1,023 | 10,012 / 97,248 | 24,063 / 46,445 |
| (e) states telling each pair apart | **16 / 16** | **1,023 / 1,023** | **97,248 / 97,248** | **46,445 / 46,445** |

So a plain pairwise distance table, with no sets, no signs and no orientation, determines every not-all-equal relation through six
distinctions, and every sampled one at seven.

**What this changes.**
- *What stands.* "Pairwise bond distance does not determine the allowed states (fails at n = 4)." It is correctly computed.
- *What does not stand:*
  - "The plain reading, that a base's information is carried by how far its distinctions are from one another, is false at the
    smallest size" (the note's answer, A97's Challenge and History);
  - "The owner's reading survives only if 'distance' includes orientation" (the note's answer and the final report);
  - "Space-like distance alone cannot be the whole of what a base holds; orientation is needed", and "How-far alone can't be all a
    base holds" (the position tables).
- *Why not.* Under (e), how far alone is enough in the whole range tested.
- *A fair reading.* "Pairwise bond distance does not carry the information, but pairwise disagreement counts do through n = 6, and
  on a sample at n = 7. Whether A97 holds depends on which distance the owner means. Bond distance (how large a knot ties the two)
  is not enough; how often the two differ is."
- *A97's status* should say so, not "plain reading overturned".

Two further points of fairness:
- **The test is about bases of up to seven distinctions.** The owner's sentence speaks of "the smallest emergent unit", one knot,
  where every reading here determines the relation trivially. The census tests the general first sentence, not the second.
- **Scoping.** The note's opening sentence ("Read as the program's bond distance between pairs") and its Limitations ("another
  reading of the owner's word would need its own test") do scope it. The status change, the final report's question to the owner,
  and the G1/G16 row do not.

**Block** on those readings, judged against the theory under test (A97). No count is wrong.

## 2. The orientation result rests on counting ties as bonds (Narrowing)

- **The study's definition.** "a bond is a set of at least two distinctions".
- **The glossary's.** "A bond of a system is a set of its distinctions on which its allowed states ... form a knot". With it,
  "A chain of two-place ties has no knot, and so no bond distance" (`LOGIC-AXIS-20261107-001`, proved). The canonical knot is a
  relation over two loops' distinctions and one contact, so at least three.
- **Later usage.** Some later studies do speak of "a bond of two". So the program's usage is split, and the study's choice should
  be stated as a choice.
- **With the glossary's bonds (size 3 or more)** (`referee_census.json`, the ">=3" readings):

  | Reading | n = 4 | n = 5 | n = 6 | n = 7 (sampled) |
  | --- | ---: | ---: | ---: | ---: |
  | (a) | 12 | 212 | 8,040 | 22,111 |
  | (c) | 16 | 512 | 51,852 | 40,019 |
  | (c′) | 16 | **883 / 1,023** | **94,328 / 97,248** | 45,394 / 46,445 |

- **What survives.** The n = 4 counterexample to (a) involves no tie, so it stands under either definition.
- **What does not.** "Each bond with the joint states it excludes determines every relation tested" holds only when two-place
  ties count as bonds. Say so wherever (c′) is quoted: the note's answer, the A97 Challenge, the final report and the position
  rows.

## 3. The pre-registration's injectivity claim is false at n = 6 (Narrowing)

- **The claim.** "For n ≤ 7 distinct satisfiable knot sets give distinct relations (advisor: a state with a = b = c = 0 and every
  other knot satisfied breaks only knot abc)."
- **The test.** At n = 4 and 5 it holds: 16 and 1,023 satisfiable sets, as many relations.
- **The failure.** At n = 6 the 999,018 satisfiable knot sets give only 97,248 relations, and 51,697 relations arise from more than
  one knot set. For example, the knot set
  {012, 013, 015, 023, 025, 035, 045, 125, 135, 235} and the same set plus 014 allow the same states.
- **Why the argument fails.** The other knots can force the remaining distinctions so that no state with a = b = c = 0 survives.
  A smaller example: {abd, abe, abf, def} forces a ≠ b, so it already implies every knot abx.
- **What it changes.** No census count, since the census enumerates relations. But at n ≥ 6 a "base" in the tables is a relation,
  not a knot pattern, and "the census asks whether a reading recovers the knots" is ill-posed there. A relation does not determine
  its knot set.

## 4. Smaller points (Not a block)

- **Prior work.** It is named well: the shattered-set complex, Pajor's lemma, lopsided families, Montanari's minimal networks.
  The (e) result sits beside Montanari: binary projections as sets of allowed pairs do not determine a relation, but here the
  pair counts do, through n = 6.
- **Words.** "Orientation" for which joint states a knot excludes is a new use of a spatial-flavoured word. It was not run past the
  advisor, as the common-verbiage skill asks.

## Fixes for the thread (listed for the owner, not folded in)

1. **"Plain reading overturned".** Withdraw "plain reading overturned" and "survives only if distance includes orientation" (note's
   answer, A97's status, Challenge and History, the final report, and the G1/G16 rows).
   - **The replacement.** "Pairwise bond distance fails at n = 4. Pairwise disagreement counts, how often two distinctions differ in
     the allowed states, determine every relation through n = 6 and every sampled one at n = 7. A97 turns on which distance the
     owner means."
   - **The owner's question** should offer both. **Block** (on these readings).
2. **The bond definition.** State it as a choice, against the glossary's "ties have no bond distance". Report (c′) under both
   definitions: it fails at n = 5 without ties. **Narrowing.**
3. **Injectivity.** Withdraw the pre-registration's injectivity claim for n = 6 and 7 (999,018 sets, 97,248 relations), and say the
   bases counted are relations. **Narrowing.**
4. **Orientation.** Run the word past the advisor before it enters the glossary. **Not a block.**

## How the work was split

- **The referee:**
  - read the pre-registration, the note, `tables.py`, `census.py`, A97, the glossary's bond definition and LOGIC-AXIS;
  - wrote an independent census (`referee_census.py`) with both bond definitions and the pair-count readings;
  - checked knot-set injectivity and sampled n = 7.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- `referee_census.py` and `.json`: relations, knot-set injectivity, readings (a), (b), (c), (c-s) and (c′) under both bond
  definitions, (e) and (e+), at n = 4, 5 and 6, and a sample at n = 7.
