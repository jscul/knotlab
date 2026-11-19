# Advisor question 1 (CLUSTER-ALL-20261119-001, before the freeze)

Analysis please; I will check it. Background: RING-PAIR's cover model (your answer there). Here I extend it to every start of the
touch census (knots of 3 to 5 places sharing distinctions, any multiplicity, sizes fixed, not bare) and want to freeze a test.

## The extended rule (found on a pilot of every census arrangement of up to four knots; fitting)

For a start: open(k) = places - shared; live = open >= 1; round-1 groups from the policy; d(k) = groups containing k.
1. **Stall** if some live knot has d > open.
2. **Blocks.**
   - For every knot w, the simplex on its live neighbours.
   - Simplices sharing two or more knots merge into one block, whose clusters are the sets connected through its edges. This fixed
     every start with two knots having two common neighbours (rings of four etc.): 525 of 525 at up to four knots.
   - A round-1 group of three or more (three knots pairwise candidates with no common neighbour, such as three mutually touching
     knots) is a hyperedge block: its clusters are one knot or all of it, made in one round (weight y^(2 - |G|)). Pairs it covers
     are not edges.
3. **Pendants.** Each live knot has s = open - d surplus offshoots.
   - An offshoot's demand is open - 1.
   - open >= 3: a leaf (y).
   - open = 2: an endless chain (y/(1 - y)).
   - open = 1: a point carrying two endless chains (y/(1 - y)^2), unless it holds the start's only loose bit (then a leaf: implied,
     closes).
4. **Relay.** A finite component (a tree of blocks, no chains) closes at its top. If other live knots exist, the top is not
   implied: + y^(m+1)/(1 - y)^2 for a top of m points (FIRST-KNOT's relay: one fresh bit, then two chains).
5. **Count.** Dissymmetry over the block tree (deck orbits where there are cycles), knots weighted y Π(1 + U_pendant); non-live
   knots count once at round 0.

**Pilot result.** Every one of the 1,939 census arrangements of up to four knots regrown 20 rounds:
- 1,901 match the rule at every round: 801 grow, 242 close, 169 stall, and the merged-block and hyperedge cases are included;
- 38 are out of scope, every one having a hyperedge that shares two knots with another block. For example, a triangle of knots
  1-2-3 plus a knot 0 touching 3: the merged block {0,1,2,3} gives [4, 3, 2] where the growth gives [4, 3, 1] and closes. At
  round 2 the valid triple {J123, J01, J02} supersedes the pair J01-J02, so cluster {0,1,2} is not a junction.

## Planned frozen test

- **T1.** All 24,502 five-knot census arrangements, regrown 20 rounds or 20,000 junctions.
- **T2.** JOIN-GROWTH's 137 starts, already grown but never compared with this rule (the floor's chains, relays, chords).
- **T3.** 2,000 random six-knot arrangements.

Prediction: every arrangement in the scope equals the rule at every round; the scope fraction is reported.

## Questions

1. Is the renewal derivation right (an offshoot's demand = open - 1; floor max(d, 2) for one parent; the chain once d = 1)? Where
   could an offshoot's demand differ from open - 1 at five or six knots: offshoots of several knots pairing across a shared
   neighbour, or an offshoot candidate of a non-sibling?
2. The relay rule only fires for finite components. Can a finite component's top be implied while other live knots exist (e.g.
   other components whose loose bits are all forced)? Can a top of an infinite component exist?
3. The hyperedge weight y^(2 - |G|) and its round-2 failure when it overlaps another block in two knots: can you state the right
   rule for valid sets of round-t junctions in cluster terms (a cluster is a junction iff its parent set is not strictly inside a
   valid set's)? Is there a cheap fix to freeze, or should I keep them out of scope?
4. What is most likely to break at five and six knots? Name starts to add as falsifiers.
