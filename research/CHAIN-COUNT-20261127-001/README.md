# Proving the chain counting on node cores

> **Referee report R1, 27 November 2026: confirmed with fixes — no Block on the theorem under N1 to N3 (with a relay
> correction); Block on dropping N2, on Lemma D as stated (it needs N2), and on Lemma C's pair clause (repaired)**
> ([the report](referee-R1/report.md)). The referee rebuilt the node core and extended nodes independently and found all
> 100 in-class growth comparisons of a fresh sample and all 19 on built starts agree, and all out-of-class ones differ.
> - **N1 alone does not suffice.** A 13-knot start meets N1 and N3 but fails N2: the last core node's two parents both hold
>   both chain bases, and their two common parents hold one base each. Growth makes two three-parent joins where the
>   reading makes one four-parent join, and two births get three fresh distinctions where the reading gives two (round 9,
>   both laws). The cycle study's referee found the same with a nine-knot start. So failed lifts are a second
>   obstruction beside chained twins; whether N1 implies N3 is still open (the referee reduces N3 to a triple test).
> - **Repairs.** Lemma C's pair clause omitted a neighbour one chain total below (repaired: every family holding the pair
>   still has the pair's common parent); Lemma D needs N2; the class is connected, with a loose distinction, and two for
>   parity (a lone offshoot under parity closes); a relaying terminal birth gets f + 1 = 1 fresh distinction; N2 is for
>   distinct parents and nonempty B; 26 sample rows passed the cap, not 2. Read this record with these changes.

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

**Open.** ~~Whether N1 alone implies N2 and N3 (no sample start separates them);~~ *(R1: N1 does not imply N2; whether it implies N3 is open)*; reading chained twins (the proof names the
one family that breaks the lemma there); chains on cores that never finish.

Status: proved on the class N1 to N3, machine-checked; referee pending. The advisor could not be consulted (its usage limit
was reached when asked); the independent check is the referee.
