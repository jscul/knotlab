# Is distance the only form of information

Epic `DISTANCE-INFO-20261117-001`, 17 November 2026, by Claude; challenges assumption A97, the owner's reading. Goals G1 and G16.
Refereed: report [R1](referee-R1/report.md), a Block and two Narrowings, folded in on 17 November (see Referee). Pre-registration:
[preregistration.md](preregistration.md), frozen in commit `d8e3b518c` at 17:41:21 UTC; the census ran 17:41:27 to 17:46:38 UTC.
Code: [tables.py and census.py](../../experiments/DISTANCE-INFO-20261117-001A/DISTANCE-INFO-20261117-001A-E001_tables/);
results: [census.json](../../artifacts/DISTANCE-INFO-20261117-001A/DISTANCE-INFO-20261117-001A-E001_tables/census.json).

## The answer

**Which distance is meant decides it.** The test covers bases of up to seven distinctions. It does not test "the smallest emergent
unit", one knot, where every reading here determines the allowed states trivially.
- **Bond distance between pairs**, how large a knot it takes to tie two distinctions, does not carry all of a base's information.
  It fails already at four distinctions, and at six, 10,012 tables cover 97,248 not-all-equal bases. Which sets of distinctions are
  bonds is not enough either.
- **How often two distinctions differ**, the number of allowed states in which this and that take different values, is a plain
  pairwise distance with no sets and no signs. It determined every not-all-equal base through six distinctions, and every sampled
  one at seven. This is the referee's reading (e), recomputed here with this study's code. It is computed, not proved, and it was
  not a frozen prediction.

The first answer of this note is withdrawn (referee R1, Block). It said that each bond together with the joint states it excludes,
"how far, and which way", is what carries everything, and that the owner's reading survives only if distance includes that
"orientation". Another pairwise distance carries everything without it. That bond reading also worked only because two-place ties
were counted as bonds, which the glossary does not do: with bonds of three or more distinctions it fails at five, with 883
readings for 1,023 relations.

**The owner's answer**, in his words (17 November 2026, 18:09 UTC), to "does your distance include which way, or only how far?":
"Distance is topological, so it will have some starting point, then go off outward from there. So for example, 0 might be a
starting point on the number line. In my view, there isn't really any such thing as "direction". Everything is just "relative",
but it's also topological, so if you're at 3 on the number line, you can't just skip 4 to get to 5, so there is an order." His
distance has no direction, so nothing is to be added to it. What he adds, that nothing is skipped and so distance gives an order,
is a separate property, tested next.

| Reading of a base's "distance information" | Distinct readings / relations, n = 4 | n = 5 | n = 6 | n = 7 (sampled) |
| --- | --- | --- | --- | --- |
| (a) bond distance of every pair | 12 / 16 | 293 / 1,023 | 10,012 / 97,248 | 88,428 / 258,384 |
| (b) the same, ties signed equal or unequal | 12 / 16 | 362 / 1,023 | 11,560 / 97,248 | 94,987 / 258,384 |
| (c) which sets are bonds (distance between sets) | 16 / 16 | 593 / 1,023 | 54,229 / 97,248 | 217,969 / 258,384 |
| (c-s) the same, ties signed | 16 / 16 | 662 / 1,023 | 56,722 / 97,248 | 227,282 / 258,384 |
| (c′) every bond with the joint states it excludes, ties counted as bonds | 16 / 16 | 1,023 / 1,023 | 97,248 / 97,248 | 258,384 / 258,384 |
| (c′) the same, bonds of three or more only (referee) | 16 / 16 | 883 / 1,023 | 94,328 / 97,248 | 45,394 / 46,445, the referee's sample |
| (e) how many allowed states tell each pair apart (referee) | 16 / 16 | 1,023 / 1,023 | 97,248 / 97,248 | 258,384 / 258,384 |
| (d) prime implicates (control) | 16 / 16 | 1,023 / 1,023 | 5,000 / 5,000 checked | 5,000 / 5,000 checked |

A distinct reading for every relation means the reading determines the allowed states. The two referee rows were added after the
read-out and were not predicted. The referee computed (e) at n ≤ 6 and on its own 46,445 sampled relations at n = 7; this study's
code gives the same at n ≤ 6 and on its own 258,384 at n = 7.
- **Ties as bonds.** In (a) to (c′) the study counted two-place ties as bonds of size two. That was a choice, and it goes against the
  glossary: "a chain of two-place ties has no knot, and so no bond distance" (`LOGIC-AXIS-20261107-001`). Without ties, (a) still
  fails at n = 4, where no pair is tied (referee: 12, 212 and 8,040 tables at n = 4, 5 and 6).
- **Bases are relations.** The bases counted are relations, not knot patterns. At six distinctions, 999,018 satisfiable knot sets
  give only 97,248 relations (see Referee).

**The smallest failures.**
- **Four distinctions, pairwise bond distance.** Three of the four knots on four distinctions allow 8 states; all four allow only
  the 6 states of weight two. In both, every pair lies in a knot of three, so every pair is at bond distance 2. The tables agree and
  the allowed states differ, and the two are not the same up to renaming (8 against 6 states). The differ counts tell them apart:
  in the first, the distinction shared by all three knots differs from each other one in 6 of the 8 states, and the rest differ in
  4; in the second, every pair differs in 4 of the 6.
- **Five distinctions, distance between sets.** A base whose states are a single state and its flip has every pair tied, at
  distance 1, and its bonds are all the pairs; which state it is cannot be read from bond distances, only from the signs of the
  ties.
- **Five distinctions, sets with signed ties.** Two bases have the same bonds (two unequal pairs and four bonds of three) and the
  same tie signs. They differ in which pair of complementary joint states each three-place bond excludes: 000/111 in one, 001/110
  in the other.

**What it means for A97.** The outcomes stated before the run were all read from bonds. Read that way, (a) colliding and only (c′)
separating would have meant A97 survives only as "signed set-distance". That reading of the outcome was too narrow, since a
pairwise distance read from the allowed states in another way separates every base tested. So the test does not overturn A97 in
any reading. It fails for pairwise bond distance, and holds, in every base tested, for how often two distinctions differ. A97
stays under challenge, now with the owner's answer: his distance has no direction and gives an order in which nothing is skipped.

**What the knot picture explained.** "This versus that" can be read pairwise in two ways. Bond distance asks how large a knot it
takes to tie this to that. The differ count asks in how many allowed states this is not that. The census shows that the first loses
information the second keeps. In the literature's terms, with values written as ±1, the number of allowed states minus twice the
differ count is the sum of the two values' product over the allowed states. So the differ table is the allowed states' pair
correlations, their degree-two Fourier coefficients up to scale; the odd ones vanish, since every relation here is closed under
flipping all values. A set of joint states is not determined by such low-degree data in general, so that these not-all-equal
relations are, in the range tested, would be a property of the law; it is the next study's question. The rest is classical. Bonds
are the minimal non-shattered sets, so (c) is the shattered-set complex, which does not determine a set system in general (Pajor
1985 and the lopsided-family literature). A relation is not determined by its binary projections taken as sets of allowed pairs
(Montanari 1974). The referee notes that the counts of the binary projections do determine these relations, through n = 6.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| G | (d) collides nowhere | held | none at n ≤ 5, nor in 5,000 checked at n = 6 and 7 |
| D1 | (a) collides at n = 4, 12 tables for 16 relations, not isomorphic | held | 12 / 16; one group of 5 (four of 8 states, one of 6) |
| D2 | (b) same at n = 4, finer than (a) at n = 5 | held | 12 at n = 4; 362 against 293 at n = 5 |
| D3 | (c) clean at n = 4, collides at n = 5 (isomorphic) | held | 16 / 16; 593 / 1,023, smallest collisions isomorphic |
| D4 | (c-s) clean at n = 5 | **failed** | 662 / 1,023: three-place bonds exclude a complementary pair that signed ties do not record |
| D5 | (c′) clean at n ≤ 6 | held, with ties counted as bonds | 97,248 / 97,248, and 258,384 / 258,384 sampled at n = 7; without ties it fails at n = 5 (referee) |

4 of 5 held, and the control; D4 failed. D5 held only under the study's choice to count ties as bonds.

## Limitations

- Bases of not-all-equal knots only, n ≤ 6 exhaustively and n = 7 sampled (400,000 random knot sets of 1 to 12 knots); the
  control (d) is checked on all relations only at n ≤ 5.
- Every result here is a census, not a theorem, including (e).
- The bases are relations; at n ≥ 6 a relation does not determine its knot set, so no reading can recover the knots there.
- "Distance" was taken as the glossary's bond distance, with ties counted as bonds; the referee's (e) is a second reading, and the
  owner's answer gives a third property, order with nothing skipped, that neither reading was tested for.

## Reproduce

```sh
.venv/bin/python -B experiments/DISTANCE-INFO-20261117-001A/DISTANCE-INFO-20261117-001A-E001_tables/census.py
.venv/bin/python -B research/DISTANCE-INFO-20261117-001/referee-R1/referee_census.py
```

## Advisor

Consulted before the freeze. It found by hand the collisions behind D1 and D3, proposed readings (c′) and (d), the isomorphism tag
and the literature (shattered sets, Pajor's lemma, lopsided families; binary projections, Montanari), and gave the four readings of
the outcome. Its guess D4 failed. Its remark that distinct satisfiable knot sets give distinct relations for n ≤ 7, copied into the
pre-registration, is false at n = 6 (referee). It was not asked about the word "orientation", which the withdrawn answer used; the
word is no longer used here.

## Referee

Report [R1](referee-R1/report.md), 17 November 2026, by a background referee thread with fresh code and no Codex. Every frozen count
recomputes exactly. Folded in the same day; each item is logged in `docs/CORRECTIONS.md` and knotlab's `HISTORY.md`.
1. **Block** on "A97's plain reading is overturned" and "it survives only if distance includes orientation". How often two
   distinctions differ in the allowed states determines every relation tested, so the answer turns on which distance the owner
   means. The answer, the A97 meaning paragraph, the position rows, A97's challenge and history, the notebook, the goals checkpoint
   and G16's entry, the objects row, the tickets and the closure ledger are corrected. The final report below is kept as sent, and
   its question was corrected in the owner's thread.
2. **Narrowing.** (c′) determines every relation only when two-place ties count as bonds; with the glossary's bonds it fails at
   n = 5. The choice is now stated, and (c′) is reported both ways.
3. **Narrowing.** The pre-registration says "for n ≤ 7 distinct satisfiable knot sets give distinct relations, so the census asks
   whether a reading recovers the knots". That is false at n = 6: 999,018 satisfiable knot sets give 97,248 relations, and 51,697 of
   the relations come from more than one knot set (for example {012, 013, 015, 023, 025, 035, 045, 125, 135, 235} with and without
   014). Other knots can force values so that no state breaks only one knot; {abd, abe, abf, def} forces a ≠ b and so implies every
   knot abx. No count changes, since the census enumerates relations. The frozen pre-registration is left as it is.
4. **Not a block.** The word "orientation" was not put to the advisor, as the glossary's rules ask; it is withdrawn with the
   reading it named.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: is distance the only form of information | **Status:** Successful (refereed, corrected) | Pairwise bond distance fails at n = 4; how often two distinctions differ determined every base tested through n = 6 and sampled at n = 7 |
| Local direction: distance as information | Promising | The owner's distance has no direction and gives an order with nothing skipped; whether the differ count always determines the base, and which distances have no gaps, is the next study |
| Broader exploration: what determines a relation | Known alternatives | Prime implicates determine it; binary projections as sets and shattered sets do not; pair correlations do here, which is not true of sets in general |
| Long-term goal: G1 and G16 | Obstruction learned | Bond distance between pairs is not all a base holds; a second pairwise distance, read from the allowed states alone, was in every case tested |

**Next step:** Continue. On the coordinator's go-ahead (17 November, 18:09 UTC), the next study tests the owner's no-skipping
property for the candidate distances, and tries to prove or refute that the differ count determines every not-all-equal base.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Does the differ count determine every not-all-equal relation, and does each candidate distance (differ count, bond distance, steps apart) have no gaps, so that betweenness gives an order from any starting distinction | 3/3, would test the owner's premise as he now states it | 2/3, a census to n = 7 or 8 with a proof attempt beside it | Freeze readings and predictions with the advisor → stop at a proof or a counterexample for each | Selected |
| 2 | Bonds with excluded states, ties counted, as an exact statement | 1/3, superseded by direction 1 | 2/3 | — | Retired |

**Corrections:** a Block and two Narrowings from referee R1, and one Not a block; all logged.

**Goals:** G1 and G16 checkpoint (obstruction learned, corrected); no goal changed.

**Assumptions:** A97 stays Under challenge, with the owner's answer added in his words; no new entry.

**Basket:** read; nothing in it is this question.

## Final report as sent

Kept as sent. Its answer and its question were withdrawn by the referee (see Referee): "survives only if distance includes that
orientation" is false, since a pairwise distance without it carried every base tested.

Posted to the owner's project thread on 2026-11-17 at about 17:50 UTC:

**Result of testing "distance is the only form of information": read as the program's distance between pairs, it fails.** It fails at the smallest possible size. On four distinctions, three of the four knots give the same pairwise distances as all four knots, yet they allow different states (8 against 6). At six distinctions, 10,012 distance tables cover 97,248 different not-all-equal bases.

Knowing which whole sets are knots, or whether tied pairs are equal or opposite, still isn't enough. What does carry everything (every base up to six distinctions, and every sampled one at seven) is each knot together with which joint states it rules out. In other words: how far, and which way.

So your reading holds only if "distance" includes that orientation. **Does your "distance" include which way, or only how far?** I've marked A97 "under challenge" until you say. 4 of 5 frozen predictions held.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: is distance the only information | **Status:** Successful (referee pending) | Pairwise distance fails at n = 4; distance with orientation determines every base tested |
| Local direction | Unresolved | Turns on your answer; then a proof for larger n |
| Broader exploration | Known alternatives | Shattered sets and binary projections are known not to suffice |
| G1, G16 | Obstruction learned | How-far alone can't be all a base holds |

**Next step:** no next action until you answer; then a proof attempt that orientation always suffices (payoff 2/3, concreteness 2/3).

**Corrections:** none here. **Goals:** G1/G16 checkpoint. **Assumptions:** A97 now under challenge. [Decision note](https://github.com/jscul/knotlab/blob/main/research/DISTANCE-INFO-20261117-001/distance_info.md)
