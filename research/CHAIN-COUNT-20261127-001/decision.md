# Proving the chain counting on node cores: what stands

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

Epic `CHAIN-COUNT-20261127-001` (G17 with G1; the coordinator's sequenced #3), closed 27 November 2026. Proved on a class
read off the start, machine-checked; referee pending. [The note](README.md) · [The proof](proof.md)

## What stands

1. **The node reading is a theorem on the class N1 to N3 (proved).** On a start whose node core has no chained twins
   (N1), whose lifts meet (N2) and whose base-holding families close (N3), ordinary growth's births of every round, with
   their parents and fresh counts, are the extended nodes, so `late.py`'s terms on the node core give every round, both
   readings, both laws. The step is one order lemma for extended nodes (Lemmas A to D) and a fresh table (Lemma F).
2. **The class holds every sample start without chained twins (computed, static).** N2, N3 and the order lemma hold on
   all 793 such starts whose cores finish; the lemma fails on all 67 with chained twins.
3. **The obstructions are two families (proved; corrected after R1).** Where the lemma fails under N2, it fails at the
   family of two lifts and two shortenings that chained twins make; where N2 fails, at two lifts that share no parent
   (R1's 13-knot start, without chained twins).

**Not shown.** That N1 implies N3 (it does not imply N2: R1); a reading of chained twins; chains on cores that do not finish.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the chain counting as a theorem | **Status:** Successful | Proved on a class read off the start that holds every sample start without chained twins |
| Local direction — reading a growth from its start | Continue | N2 is a real second condition (R1); N3's need is open |
| Broader exploration — what a local reader keeps of a start | Capability gained | The late view is proved, not only computed, on 793 sample starts |
| Long-term goal — G17 with G1 | Capability gained | Typical meeting patterns of the samples are now read by a theorem |

**Next step:** Continue — #2 (the one 3/3 payoff), started in this thread once the cycle study's referee is folded in

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Decide whether N1 and N2 imply N3 *(revised after R1: N1 does not imply N2)* | 2/3 — the class becomes two conditions | 2/3 — R1 reduces N3 to a triple test | Prove the triple test from N1 and N2, or build a start that fails it → a proof, or a separating start | Proposed |
| 2 | Read the two obstructions: the family chained twins make, and the split of a join whose lifts do not meet *(widened after R1)* | 3/3 — removes the exceptions seen | 2/3 — both families are named | Extend the extended nodes by both; test on the 67 chained-twin starts and the referees' failed-lift starts → every round, or the next obstruction | Selected |
| 3 | Chains on cores that never finish, by the unrolled map's copies | 2/3 — completes pieces with a cycle | 2/3 — `RING-IDENT`'s clusters | Lift nodes to the unrolled map; test on the cycle study's two unread starts and fresh rings → exact, or the miss | Proposed |

**Corrections:** one entry after R1 (three Blocks, two Narrowings, two Not a block); the conditional theorem stands.
**Goals:** checkpoint row added (G17 with G1; capability gained).
**Assumptions:** none new; the proof's conditions N2 and N3 are stated hypotheses, not defaults.
**Scaffolds:** none added; the machine check reuses the cycle study's samples and caps (A307), and the proof uses none.
**Advisor:** not consulted (its usage limit was reached); the referee is the independent check.
