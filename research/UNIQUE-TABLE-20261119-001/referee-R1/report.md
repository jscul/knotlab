# Referee report UNIQUE-TABLE-001-R1 (own tables, legality, growth and searches)

**Verdict: confirmed, with two wording points. No Block.**
- **The six pairs are real** (the owner's first point). All eleven rivals (five stages have two) were checked with the referee's
  own code:
  - each is legal as a static arrangement;
  - its exact table equals the truth's entry by entry, by two independent methods;
  - its allowed states differ, it is not isomorphic to the truth, and the truth's table has no junction-moving symmetry;
  - the least bond holding three distinctions differs on 116 to 208 triples.
- **Forcing with elimination is sound,** and **the Whitney enumeration with a per-block outside is complete** for the stated bound
  (the second and third points). An independent brute-force search for same-equation rivals gives the same verdict on every one
  of the 1,867 stages both searches decided.
- **None of the eleven rivals can be reached** (the coordinator's question):
  - **not by the cheapest growth in complete rounds,** from any start, after any number of rounds;
  - **not under Codex's serial mixed law.**

  So the six pairs **bound** the Codex line (reachable rivals) rather than contradict it: no reachable pair is known to collide this
  way.
- **Wording.** "The rival stalls" holds when each arrangement is taken as a new start, as the study did. Under the census's own
  continuation, the five rivals grow four junctions against the truth's three. The two still differ at the next step under either
  reading.

## 1. The six pairs (`referee_unique.py pairs`, `referee_unique_pairs.json`)

For each truth and each of its rivals (from `verify_rivals.json`, as data):

| Stage | Distinctions | Junctions | Both legal (static) | Tables equal (brute force; = shore enumeration on both) | Equation spaces | Isomorphic | Truth's table symmetries keep its junctions | Triples whose least containing bond differs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pop-0007 | 16 | 8 | yes | **yes** (yes, yes) | differ | no | yes | 116 of 560 |
| pop-0236 (2 rivals) | 20 | 8 | yes | **yes** | differ | no | yes | 192 of 1,140 |
| pop-0308 (2) | 17 | 7 | yes | **yes** | differ | no | yes | 144 of 680 |
| pop-0338 (2) | 20 | 8 | yes | **yes** | differ | no | yes | 192 of 1,140 |
| pop-0442 (2) | 20 | 8 | yes | **yes** | differ | no | yes | 192 of 1,140 |
| pop-0501 (2) | 21 | 8 | yes | **yes** | differ | no | yes | 208 of 1,330 |

- **Static legality**, as the bound says:
  - every distinction lies in one or two junctions, every junction has three or more, and no two share two;
  - every junction's removal leaves the wired graph connected, so every star is a bond and there is no cut vertex but the
    outside.
- **The tables** were computed by brute force over the allowed states' minimal non-free sets, and by the referee's closed-aware
  shore enumeration.
- **The symmetry lemma** checks. Since every table symmetry of the truth keeps its junctions, a rival equal to a renamed truth
  would be the truth.

**The next step** (`next_round`; the study's `pairs.py` was read to see how it grows):

| Reading | Truth | The five rivals that "stall" | pop-0007's rival |
| --- | --- | --- | --- |
| Each arrangement taken as a new start, every junction live (the study's) | 3 new junctions | **stall** | 3 |
| The census's own continuation: only the round-1 junctions live | 3 | **4 new junctions** | 3 |

So the growth law tells each pair apart at its next step under both readings, but "the rival stalls" is a statement about the
first reading. Since the truths are round-1 stages, the second is the one their own growth uses.

## 2. Forcing with elimination (argued)

The steps, as `unique_table.md` and `uniq.py` state them, with K = D + 1:
- **A pair at table distance d lies in some bond of d + 1 distinctions in every matching code.** Bonds are the minimal non-free
  sets, so they are invariants of the allowed states, and every pair inside that bond reads at most d.
- **A candidate strictly containing a forced word is not minimal.**
- **A candidate whose span with the forced words holds a word w lighter than the least bond through one of its distinctions z
  cannot be in the code.** A nonzero word is a disjoint union of bonds, so w would hold a bond through z of at most |w| < K(z, y)
  for its other member y. Words of one distinction cannot occur (every row is finite).
- **A pair left with one candidate forces it.**

Each step only removes candidates no matching code can contain, so forcing is sound.

## 3. The Whitney enumeration (complete for the bound) and an independent count

**The argument.**
- A rival with the same equations has the same cut space, and so the same graphic matroid on its wired graph.
- The bound (no cut vertex but the outside) makes the rival's blocks meet only at the outside vertex.
- Blocks are the matroid's connected components, and so fixed. Within a block, Whitney's theorem gives exactly the twist class.
- So the rivals are exactly the choices, block by block, of a member of its twist class and of the vertex that becomes the
  outside, filtered by legality: the per-block outside choice the advisor required.
- With the same rank and a connected rival, the junction count is the truth's.
- The enumeration is complete if each block's twist class is closed. The independent count checks that.

**Independent count** (`samecode.py`, `referee_unique_samecode.json`):
- **The method.** Every rival star is a bond of the common space, so the referee listed every minimal word of size three or more,
  and searched exhaustively, including or excluding each in turn, for every collection of at most n of them with:
  - every distinction in one or two words, and no two words sharing two;
  - the truth's span, and static legality.
- **Inputs.** The truth's stages were regrown by the referee's own engine.
- **The verdict agrees on every decided stage:** 1,867 of 1,867 stages of the population and controls agree on whether a
  same-equation rival exists. Both searches find one on 133. 49 stages reached the referee's search cap, and their verdicts were
  not compared.
- **Counts differ on 51 stages,** the study's usually one higher. Five of the study's stored rival examples have one junction
  more than the truth: the truth plus the loose set as a junction, closed. That is outside its frozen bound ("at most as many
  junctions as the truth"). No verdict rests on such a rival, since the verdicts agree.

**A bug found in the referee's own first count, and fixed.** It stopped adding junctions once every distinction was covered,
which missed rivals needing a further junction: for example, the loose set made a junction and an old junction made the outside.

## 4. Can the rivals be reached? (the coordinator's question; `referee_unique.py reach`)

- **By the cheapest growth in complete rounds.**
  - **The method.** A grown stage's start knots are among its junctions, with their full supports. So for each truth and rival,
    every connected subset of its junctions was taken as a start and grown by the referee's engine for one round or more, until it
    passed the target's size. Each stage was compared with the target as an arrangement.
  - **Every truth is reached,** at round 1 from its census start of 4 or 5 knots, as a check of the method.
  - **No rival is reached,** from any start after any number of rounds.
- **Under Codex's serial mixed law** (one to three parents, two or three fresh). By isomorphism with the referee's 001F census of
  every presentation the law reaches at the same width (16 to 21 distinctions), **no truth and no rival is reachable.** The census
  arrangements lie outside that law; their starts share distinctions in ways no serial history makes. Codex's families, with one
  ternary site, are narrower still.
- **So the six collisions are between a reachable arrangement and arrangements no growth law here builds.** They neither
  contradict Codex's reachable-rival results nor RING-READ. They show that those results' restriction to reachable rivals is doing
  work.
- **The two kinds of collision found so far are complementary.**
  - **Reachable collisions are related by a table symmetry:** 001K's width-28 pair, 001L's width-32 pair, 001N's width-31 pair.
  - **Collisions without a table symmetry have been unreachable** (these six).
  - The study's direction #1 (two grown stages with one table) is the test that would join them.

## 5. How it sits against A97

A97's challenge reads: "find two bases whose bond distances agree for every pair of distinctions but whose allowed states differ."
- **For static bases, these six meet it,** with no symmetry of the table to blame.
- **For bases a law builds, it is unmet:** the rivals are unreachable.

**Suggested wording for A97's history line:**

> `UNIQUE-TABLE-20261119-001`: six census stages have a legal, non-isomorphic arrangement with the same bond distance for every
> pair and different allowed states, with no symmetry of the table relating them. None of the rivals can be reached, by the
> cheapest growth in complete rounds from any start or under the serial mixed law. So, as a statement about every static
> arrangement, "distance carries the information" is false. As a statement about what a law builds, it is untested by these
> pairs. A97 remains under challenge, now with a sharper test: two reachable arrangements with one table and different states,
> with no table symmetry between them.

## Corrections for the owner (listed, not folded in)

1. **"In five the rival stalls."** True when each arrangement is grown as a new start. Under the census's own continuation (only
   the round-1 junctions live), those five rivals grow four junctions against the truth's three. Say which reading. **Not a block
   (wording).**
2. **Same-equation rival counts.** Some of the study's counts include the truth plus the loose set as an extra, closed junction:
   one junction more than the truth, outside the frozen bound. Verdicts are unaffected. **Not a block (counting).**

## How the work was split

- **The referee:**
  - read `unique_table.md`, the pre-registration and `pairs.py`;
  - wrote `referee_unique.py` (pairs, reach) and `samecode.py`, on its FRESH-COUNT-R1, FIRST-KNOT-R1, 001F-R1, NAE-GROWTH-R1 and
    CENSUS-READ-R1 code.
- **Read as data:** `verify_rivals.json`, and the per-stage records in `runs/unique-table*` (for the comparison counts and rival
  examples).
- **No study code was run.**
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.
