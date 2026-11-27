# Proving the chain counting on node cores

Epic `CHAIN-COUNT-20261127-001`, under G17 with G1, the coordinator's sequenced pick after `CYCLE-READ-20261127-001`
(that study's direction 1). Proof work; no growth was run.

**The question.** The node reading (`GRADED-ORDER-20261126-001`) reads ordinary growth off a start: the core's births by
Lemma R's round rule from the round-1 groups and offshoots, the births along endless chains by `late.py`'s binomial terms
on those core births, and the relay. Referee R2 of the graded-order study proved the core part on starts without chained
twins. Is the chain part a theorem too?

**The answer** ([the proof](proof.md)): yes, on the class of starts whose node core satisfies three conditions read off the
start without growing: no chained twins (N1), any two parents of one core node that hold a set of chain bases share a
parent holding it (N2), and every maximal family of core nodes of one rank that hold a set of bases and pairwise share a
parent holding it has a common parent holding it or a common child (N3). There every round's births, with their parents
and fresh counts, are the **extended nodes**: a core node with a length along each of some chains based at its points.
The proof reduces the theorem to one order lemma for extended nodes and a fresh-count table, following
`CHAIN-IDENT-20261119-001A`'s proof of the tree case, with referee R2's argument for the pure part.

**Checked** ([ext.py](ext.py), structure only, through round 10): the order lemma for extended nodes and N2 and N3 hold
on all 793 sample starts without chained twins whose cores finish (678 with tree pieces, 115 with a piece `late.py` counts
as a cycle), so the theorem covers every one of them; the lemma fails on all 67 with chained twins, where N2 fails on 32
and N3 on 4. ([tree pieces](ext_samples.txt), [pieces with a cycle](ext_cycles.txt); [convex.py](convex.py) checks N2's
single-base form.)

**Open.** Whether N1 alone implies N2 and N3 (no sample start separates them); reading chained twins (the proof names the
one family that breaks the lemma there); chains on cores that never finish.

Status: proved on the class N1 to N3, machine-checked; referee pending. The advisor could not be consulted (its usage limit
was reached when asked); the independent check is the referee.
