# Proving the chain counting on node cores: what stands

Epic `CHAIN-COUNT-20261127-001` (G17 with G1; the coordinator's sequenced #3), closed 27 November 2026. Proved on a class
read off the start, machine-checked; referee pending. [The note](README.md) · [The proof](proof.md)

## What stands

1. **The node reading is a theorem on the class N1 to N3 (proved).** On a start whose node core has no chained twins
   (N1), whose lifts meet (N2) and whose base-holding families close (N3), ordinary growth's births of every round, with
   their parents and fresh counts, are the extended nodes, so `late.py`'s terms on the node core give every round, both
   readings, both laws. The step is one order lemma for extended nodes (Lemmas A to D) and a fresh table (Lemma F).
2. **The class holds every sample start without chained twins (computed, static).** N2, N3 and the order lemma hold on
   all 793 such starts whose cores finish; the lemma fails on all 67 with chained twins.
3. **The one obstruction is one family (proved).** Where the lemma fails under N2, it fails at the family of two lifts
   and two shortenings that chained twins make: the group the graded-order study's misses showed.

**Not shown.** That N1 implies N2 and N3; a reading of chained twins; chains on cores that do not finish.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the chain counting as a theorem | **Status:** Successful | Proved on a class read off the start that holds every sample start without chained twins |
| Local direction — reading a growth from its start | Continue | The class's two extra conditions are the only gap to "no chained twins" alone |
| Broader exploration — what a local reader keeps of a start | Capability gained | The late view is proved, not only computed, on 793 sample starts |
| Long-term goal — G17 with G1 | Capability gained | Typical meeting patterns of the samples are now read by a theorem |

**Next step:** Continue — #2 (the one 3/3 payoff), started in this thread once the cycle study's referee is folded in

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Prove that N1 implies N2 and N3, or build a start that separates them | 2/3 — the class becomes "no chained twins" alone | 2/3 — both failures sit at or after the twins' rank on every sample | Induct on rank with the first failing node; search built starts with cells → a proof, or a separating start | Proposed |
| 2 | Read chained twins: add the family {(T_1, a), (T_2, a), (D_1, a − δ), (D_2, a − δ)} to the round rule | 3/3 — removes the last exception seen | 2/3 — the family and its round are named by the proof | Extend the extended nodes by that family; test on the 67 chained-twin starts → every round, or the next obstruction | Selected |
| 3 | Chains on cores that never finish, by the unrolled map's copies | 2/3 — completes pieces with a cycle | 2/3 — `RING-IDENT`'s clusters | Lift nodes to the unrolled map; test on the cycle study's two unread starts and fresh rings → exact, or the miss | Proposed |

**Corrections:** none.
**Goals:** checkpoint row added (G17 with G1; capability gained).
**Assumptions:** none new; the proof's conditions N2 and N3 are stated hypotheses, not defaults.
**Scaffolds:** none added; the machine check reuses the cycle study's samples and caps (A307), and the proof uses none.
**Advisor:** not consulted (its usage limit was reached); the referee is the independent check.
