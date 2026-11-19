# Advisor question 1 (ROUND-FREE-20261119-001, before the freeze)

Analysis please; I will check it. Background: the cheapest parity growth under the complete-round rule (A104). In each round
every live junction (one holding loose bits) is joined at once in the policy's groups, and every new junction gets fresh bits =
its demand in the next round (lookahead), floored to three places. RING-PAIR and CLUSTER-ALL found that, in scope, the round-t
junctions are exactly the clusters of t + 1 points of the unrolled candidate map (counted by size; algebraic). The owner says
"Time doesn't have ticks"; the coordinator asks for a round-free test:
- does growing one join at a time, in any order, build the same thing;
- do the ratios survive without rounds;
- do parts of one start grow at different speeds, stated without rounds;
- and no inside clock.

## Pilot (serial laws reading only the current presentation)

A move is one of the policy's groups among the current live junctions, minus sets already joined, or an offshoot for a loose bit
in no current group. A new junction's fresh bits = the fewest rule with its demand read from the current state. I ran two
policies, uniform over all moves and joins first, with 3 random orders each, 300 steps. Per-rank counts (rank = 1 + max parent
rank), against the rounds:

| Start | Rounds | Uniform, 3 orders | Joins first, 3 orders |
| --- | --- | --- | --- |
| two touching 3-place knots | 2, 4, 6, 8, 10 | 2,2,4,6,5 / 2,2,3,3,3 / closes after 8 junctions | all three close after 8 junctions |
| lone 4-place knot (closes in 2^4) | 1, 4, 6, 4, 1 | grows past 300 in all three | closes after 9–10 |
| ring 4,4,4,4,5 | 5, 6, 7, 8, 9 | 5,2,3,4,5 / 5,3,4,3,4 / 5,3,3,4,5 | 5,2,3,5,5 / 5,4,5,5,3 / 5,3,4,3,3 |
| ring 5,5,5,5,5 (golden ratio) | 5, 10, 15, 25, 40 | 5,3,4,5,7 / ... | thin, near-constant |

So both naive laws are order-dependent and build thinner things than the rounds, and the order can decide whether a growth lives
or dies. My reading is the fewest count: a junction's fresh bits must equal its future joins, which depend on junctions not yet
made. The round supplies that lookahead by synchrony; the cluster map supplies it statically.

## Plan

- **(A)** Freeze the order dependence of the two naive laws: 20 orders per start, on rings, a ring-plus-piece join, a two-ring join
  and census two-dimensional starts.
- **(B)** The round-free form is the cluster map: junctions are clusters, parents are clusters less a removable point, round =
  size − 1. Ratios are ratios of counts by size (golden ratio for the ring of five five-place knots; 1.1347; 2.6075 for two rings
  of five).
- **(C)** Part speeds by size: among clusters of size k, the shares lying in one part, in the other, or in both, for the
  ring-plus-piece and two-ring joins.

## Questions

1. Is there a natural serial law that reads only the current presentation, never stalls, and is order-independent with the round
   growth's result? For example, bits created on demand, with a junction's arity growing as joins take bits, plus a "complete
   sibling set" test. Or is there an argument that no presentation-local serial law can reproduce the fewest-count growth in every
   order (an impossibility I could state)?
2. Is "size of a cluster" an inside clock, in the sense the owner rejects? It is a property of each junction: how many points of
   the map it spans. How should I word it?
3. For (C), what round-free speed statement is meaningful? Shares by size, or under a uniform random serial order of the closure
   law (each buildable cluster equally likely next), the part shares once N junctions exist (a "time runs faster where more can
   happen" reading)? Which would you freeze?
4. Sharp predictions to freeze, and a falsifier.
