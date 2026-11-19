# Complete rounds keep backed pairs, and peel back exactly

## Standard statement

In the complete-round joining policy on even-parity constraints, started from a connected set of constraints, every stage after
the first round has these properties. The constraints holding a free variable pairwise share no variable. Any two constraints that
such a constraint shares a variable with also share a variable with a third constraint, which has no free variable. Deleting the
constraints with a free variable gives the previous stage exactly. And the least cocircuit (bond) through two variables of the
previous stage is never larger in the next stage.

## Nearest known result

`FRESH-COUNT-20261118-001A` and `FIRST-KNOT-20261118-001A` (the joining rule, its pieces and seeds). The properties here are read
off the same rule. Whitney's 2-isomorphism theorem says when two graphs have the same cycle matroid; it is used in ticket B only.
[Design](../../../research/PARENT-RULE-20261119-001/preregistration.md).

## 0. Setting

As in `FIRST-KNOT-20261118-001A` §0. Junctions are even-parity knots; a distinction is held by one junction (loose) or two
(shared). A junction is **live** when it holds a loose distinction. Junctions **meet** when they share a distinction. The rule runs
in complete rounds, as in `FRESH-COUNT-20261118-001B`'s `step`:
- in round r the junctions that may join are the round-(r−1) junctions holding a loose distinction (all start junctions in round
  1);
- two of them are **candidates** when some existing junction meets both;
- every maximal set of three or more pairwise candidates with no junction meeting them all gets one new junction, which takes one
  loose distinction from each;
- every candidate pair in no such set gets one;
- every other loose distinction gets a junction of its own (an offshoot);
- the round is unavailable (a stall) if some junction would have to give more loose distinctions than it holds.

Each new junction then gets fresh distinctions under the count rule. Under the fewest counts with elimination over GF(2) (the
census's rule), a new junction gets none only when its parity is implied by the equations already there.

The start is connected (two junctions are joined by a chain of junctions, each meeting the next). All 26,441 census starts are
connected, as checked.

## 1. The live junctions

**Lemma 1.** After round r ≥ 1:
1. every distinction that was loose before the round is shared by its old holder and one new junction;
2. two new junctions share no distinction;
3. a new junction meets exactly the junctions it took a distinction from (its parents), each once;
4. the live junctions are exactly the new junctions that got a fresh distinction.

*Proof.* By induction on r. Before round r the live junctions are exactly the round-(r−1) junctions with a fresh distinction (for
r = 1, the start junctions holding a loose one). This is item 4 at r − 1, and holds for the start.

In round r, each such junction gives each of its loose distinctions to exactly one new junction: one per set or pair it lies in,
the rest as offshoots. If it cannot, the round stalls and nothing changes. That gives item 1, and also that each old distinction
goes to one new junction. Fresh distinctions are new. So two new junctions share nothing, which is item 2.

A new junction's distinctions are one from each parent and its fresh ones, which are loose. So it meets its parents, once each, and
no one else, which is item 3.

After the round, the old junctions hold no loose distinction: by item 1 for those that were live, and by the induction hypothesis
for the rest. The new junctions with a fresh distinction are live. Those without are not, which is item 4. ∎

**Lemma 2 (closing).** Since the start is connected, every stage is connected, because a new junction meets its parents. In a
connected stage, a set of loose distinctions has its parity implied exactly when it is all of them. The equations are the cut
space of the junction graph, with the outside vertex holding the loose ends, and a cut made only of loose distinctions cuts off all
the junctions together. So a new junction without fresh distinctions holds every loose distinction. Then it is the only new
junction of its round, and the stage it makes is **closed**: no live junction. Every new junction of an **open** stage (one with a
live junction) is live. ∎

## 2. Backed pairs and live junctions never meeting

**Theorem 1.** Every stage of round r ≥ 1 satisfies:
- **(P2) live junctions never meet;**
- **(P1⁺) backed pairs:** for every live junction j and any two junctions u, v that j meets, some junction w other than j meets
  both u and v and holds no loose distinction.

*Proof.* By Lemma 1(4), the live junctions are round-r junctions, which share nothing (Lemma 1(2)); that gives P2.

Let j be live and u ≠ v two junctions it meets. By Lemma 1(3) they are parents of j, so both lie in the set or pair that j was made
for, and they were candidates. So some junction w that existed before round r meets both. Then w ≠ j, and by Lemma 1(4) w holds no
loose distinction after round r. ∎

Offshoots meet one junction, and closed stages have no live junction, so for them the properties hold with nothing to check. Round
0 (the start) is not covered: start junctions may meet each other and need no backing.

## 3. Peeling

**Theorem 2.** Removing the live junctions of an open stage of round r ≥ 1 gives the stage of round r − 1 exactly: the same
junctions, each with the same distinctions. Removing the last junction of a closed stage does the same. Hence the **peel depth** of
an open stage of round r is at least r. The peel depth is the number of successive removals of the live junctions, starting from
the stage, at each of which P1⁺ and P2 hold.

*Proof.* In an open stage the live junctions are exactly the round-r junctions (Lemmas 1 and 2). A junction's distinctions never
change after its round, so removing the round-r junctions leaves stage r − 1. That stage is open, since round r had junctions to
join, and has round r − 1. Repeating, stages r, r − 1, …, 1 each satisfy P1⁺ and P2 by Theorem 1. A closed stage is stage r − 1
plus its single closing junction (Lemma 2). ∎

## 4. Peeling never lengthens a distance

**Theorem 3.** Let stage r ≥ 1 be open, and let x, y be distinctions of stage r − 1. Let D_s(x, y) be the smallest bond of stage s
containing both, less one, read as infinite if there is none. Then D_r(x, y) ≤ D_{r−1}(x, y).

*Proof.* Take a bond of stage r − 1 through x and y: a cut between a connected set S of junctions and its complement, with the
complement also connected. Choose S to be the side without the outside vertex o.
- **The same cut in stage r.** Keep the same S in stage r.
  - The distinctions between S and the other old junctions are unchanged.
  - The distinctions between S and o were S's loose distinctions. They now lie between S and round-r junctions, which are on the
    other side (Lemma 1(1)).
  - Round-r junctions meet only their parents (Lemma 1(3)).
  - So the cut holds exactly the same distinctions.
- **Both sides stay connected.** S is unchanged, so it stays connected. In stage r − 1 the other side was connected, possibly
  through o. Every link through o went along a loose distinction of an old junction, and that distinction now leads to a round-r
  junction. That junction holds a fresh distinction, since the stage is open (Lemma 2), so it meets o.

So the cut is a bond of stage r through x and y of the same size. ∎

The inequality can be strict, as when x and y are two distinctions that one new junction takes. Ticket B measures how often.

## 5. What this does and does not give

- **What it gives.** Theorems 1 and 2 hold at every size. Every reached stage of round ≥ 1 is backed (P1⁺), keeps its live
  junctions apart (P2) and peels back to its start. UNIQUE-TABLE's 11 static rivals all fail backed pairs (P1) (`research/PARENT-RULE-20261119-001/preregistration.md`, a design-stage observation), so the law cannot build them. That is the reason, at every size, that those rivals are never reached.
- **What it does not give.** It does not yet give "no reached meet-once collision with other states" at every size. That needs a
  second statement: two arrangements that meet once, are backed (or peel deep enough) and have isomorphic tables have the same
  states. Ticket B tests it on every small arrangement. It is a conjecture until proved.
