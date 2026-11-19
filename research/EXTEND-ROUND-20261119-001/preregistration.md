# Does a table isometry that keeps what the round reads extend one round? Pre-registration

Epic `EXTEND-ROUND-20261119-001` (`CREATED-PAIR-20261119-001#1`, the coordinator's go-ahead; A97, A108, G1), 2026-11-19.
Frozen before the run. The canonical K1–K3 test is unchanged.

## The question

GROW-SMALL's 86 carried meet-once pairs share a full table with other states and stay together a round further; the one created
pair parts. CREATED-PAIR traced the difference to whether a table isometry keeps the growing end. So: state exactly what one
complete round reads, and decide whether a table isometry that keeps it extends to an isometry of the next round's tables. If it
does, distance plus the growing end carries what grows, the clean form of the owner's premise.

## What the round reads (stated before the advisor saw it, as asked)

In a connected arrangement, the round reads **R(a)**:
- the live junctions L (those holding a loose distinction), with their loose counts;
- the family F of sets of live junctions that some one junction meets.

Which live junctions meet each other is redundant, as the advisor notes. **Lemma A (proved, the note):** the round's output, the
new junctions' parent sets and fresh counts, is a function of R up to relabelling.
- **Candidates and sets.** The candidate pairs are the pairs in F. The sets are the maximal candidate cliques with no member of
  F containing them. The stall test reads the loose counts.
- **The fresh counts.** After the round the live junctions are the new ones, each meeting only its parents. So the demand and the
  fresh counts read only the parent sets.
- **The implied test.** In a connected arrangement a set of loose distinctions is implied exactly when it is all of them
  (PARENT-RULE Lemma 2).

The connectedness hypothesis is a standing assumption; it holds for every arrangement here.

A table isometry φ: a → b **keeps the reading** when:
- it carries the loose distinctions onto the loose distinctions;
- it carries each live junction's distinctions onto a live junction's, which defines ψ on L;
- ψ carries F onto F.

**Claim B (the question):** if φ keeps the reading, its extension φ′ is an isometry of the next tables. The extension matches new
junctions through ψ of their parent sets, matches taken and fresh distinctions, and re-pairs the loose distinctions inside each
live junction, which are twins.

**Claim B\* (proved, the advisor's three lines, recorded):** if φ also carries the equations, φ′ carries the next equations, so the
pair stays together in every later round. Every pair tested here has other states, so B\* never applies. The test is of Claim B
alone.

## Prior work in the program

`python3 -B scripts/track.py objects "isometry keeps what the round reads extends one round growing end" --until 2026-11-19 --exclude EXTEND-ROUND-20261119-001`

- `CREATED-PAIR-20261119-001`: the growing end, loose-keeping isometries, the 6 pairs.
- `GROW-SMALL-20261119-001`: the 87 pairs and their persistence.
- `PARENT-RULE-20261119-001`: the static pairs, Lemma 2.
- `MEET-TWIST-20261118-001`: two presentations with one meeting pattern grow by one law, a coupling of rounds (a relative, under
  another law).
- `KEEP-REACH-20261117-001`: what keeps a bound from pair projections (a distant relative).
Also `FRESH-COUNT-20261118-001` (the round).

## Design-stage observations (disclosed)

A smoke test on 10 pairs:
- the 6 static pairs looked at have no isometry keeping R;
- neither does the created pair;
- neither do three 9-junction carried pairs, yet their next tables are isometric. Those three are among CREATED-PAIR's 6 that fail
  the growing-end test.

## Method

`extend.py` takes PARENT-RULE's 1,034 static pairs and GROW-SMALL's 64 reached pairs whose members have at most 15 vertices.
- It enumerates every full-table isometry (cap 20,000).
- For each isometry it tests whether R is kept.
- For up to 50 that keep R, it builds the extension and checks it entry by entry on the next full tables. These come from bonds,
  or from exact_table_v2 with no bound, under a 600 s alarm.
- It records whether the next tables are isometric at all.
- Where they are, it records whether some next isometry carries the old distinctions onto the old ones (the advisor's split).

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| X1 | Every tested extension of an R-keeping isometry is an isometry of the next tables (mine 50%, the advisor's 60%) | one is not |
| X1′ | Every pair with an R-keeping isometry has one whose extension is an isometry (the advisor's 80%) | a pair has none |
| X2 | Lemma A: every R-keeping isometry gives corresponding rounds (the extension is defined) | one does not |

Reported without a prediction, in the advisor's three classes:
- pairs with an R-keeping isometry;
- pairs with none (the equation-isomorphism class is empty by construction);
- persistence and age-respecting next isometries in each.

Also reported: what CREATED-PAIR's 6 are.

## Advisor

Fable 5.2 before the freeze ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md)).
- **What it confirmed.** Lemma A, with connectedness as the caveat.
- **Its proof.** B\*: equations plus R give persistence forever.
- **Its argument against Claim B.** After the split, new bonds can put new junctions on the inside and discount their parents.
  So the next table reads more than the old table, three-way readings among it, and Claim B "has no reason to hold". It
  expects any counterexample at a pair-junction with one fresh distinction.
- **Taken:** the three classes and the age-respecting check.
- **Its bets:** Claim B in general 25%; no counterexample here, "some" form 80%, "every" form 60%.

## Runs and stop rule

`extend.py` once (minutes); then stop.
