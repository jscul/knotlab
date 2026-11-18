Colleague question before I freeze a small study. Please answer in under 600 words: check the design, say which predictions you
expect to fail and why, and propose anything sharper.

Setting (parity growth, the program's "cheapest counts" law). A presentation is a set of junctions; each junction is a parity
knot on a set of distinctions (bits); each distinction lies in one junction (loose) or two (shared). Growth runs in complete
rounds: the newest junctions with loose distinctions are live; groups of live junctions that share a common lower neighbour
join (one new junction consuming one loose distinction from each parent), leftover loose distinctions get one-parent junctions,
and each new junction receives the fewest fresh distinctions that keep the next round available. Start: a ring of five junctions,
four with 4 distinctions and one with 5 (each shares one distinction with each ring neighbour). Known (RING-GROWTH-20261118-001):
counts c(t) = c(t-5) + c(t-6); junction sizes grow: the largest junction has 6 distinctions from round 5, 7 from round 10, 8 from
15, 9 from 20; parent counts up to 6-7.

Bond distance of two distinctions = (fewest distinctions in a minimal parity consequence, i.e. a circuit of the cut space,
containing both) - 1. Equivalently: in the junction graph with one extra "outside" vertex o that ends every loose distinction,
a circuit is a bond (minimal edge cut) delta(J), J and its complement both connected. A proved reader (BOND-NEXT-JOIN) recovers
the junctions from the table at distances <= 5 when every junction has at most six distinctions: at each support size s = 3..6 it
takes maximal cliques of {pairs with distance < s}, after removing pairs that cross between two already-read junctions whose
union bond has size <= s. Its key lemma: a sum of three or more junctions has support >= 7. Codex's newest reader
(VARIABLE-OUTPUT-READER-001G) is all-size but needs every junction <= 4 distinctions.

Scouting (already run, disclosed): through round 9 the reader recovers the ring exactly and the next round grown from the
recovered junctions alone (no rounds, no parents) matches. At round 10 (stage s = 7 runs for the first time) the reader run on to
s = 7 gives three spurious cliques (sizes 5, 5, 4), none missed, all near the round-1 one-parent junction of 3 distinctions and
the five-place seed knot: bonds of three junctions with support 7 (e.g. 3 + 4 + 4 - 4). Tables computed by enumerating connected
sides J (o not in J) of at most m junctions with connected complement; m = 3 and 4 gave the same table at round 10.

Design for rounds T = 10, 12, 14, 15, 16, 18, 20:
- Table: the enumeration at m = 4, with m = 5 as a completeness check where it runs.
- R1: the reader run on to the largest junction size (expected to fail).
- R2: R1's candidates from every stage, then repair: remove candidates until every distinction lies in at most two, keeping
  every repair that leaves a legal incidence covering all distinctions; then keep only repairs whose own bond table equals the
  given table. "Works" = exactly one survivor and it is the true junction set.
- Regrowth: one round grown from R2's junctions alone, compared with the true next round as the multiset of (parent junctions,
  fresh count).
- Rigidity: whether the junction graph with o is 3-connected (then, by Whitney's 2-isomorphism theorem, the allowed states fix
  the junctions up to which vertex is the outside; settled by construction: choosing another vertex as outside gives the same
  table, with a junction of all the old loose distinctions, which the law's sizes exclude).

Predictions:
P1 m = 4 and m = 5 tables agree wherever both run.
P2 R1 gives spurious junctions at every T >= 10.
P3 R2 has exactly one survivor, the true junctions, at every T.
P4 the regrown round equals the true next round at every T.
P5 the junction graph with o is 3-connected at every T.
P6 the smallest horizon H (distances above H pooled) at which R2 still works is (largest junction size) - 1.

Questions: (1) Is the m-bounded enumeration a sound table here, or can a small bond have both sides large (a belt around the
ring: the layer cut has about 2 c(t) distinctions)? A proof idea for completeness would help. (2) Is R2 a reasonable reader, or
is there a principled generalisation of the pairwise prune (sums of k junctions) with a lemma like "a sum of k junctions has
support >= f(k)" in this growth? (3) Which of P1-P6 would you bet against? (4) Do you see a way to two different legal ring
histories, or incidences, with one table (a Whitney twist at a 2-separation, swapping interchangeable loose distinctions, ...)?
