# Time as a fold: what stands

Epic `FOLD-SIGN-20261126-001` (G18, at the coordinator's pick with the owner's intuition), closed 26 November 2026. An
argument reviewed with the advisor; nothing computed; referee pending. [The note](README.md) ·
[advisor's question](advisor_question.md) and [answer](advisor_answer.md)


> **Refereed (R1, [report](referee-R1/report.md)): confirmed with fixes, no Block.** On 28 starts and 241 history
> prefixes (two growth programs agreeing), all 66 with twin births have sign-imbalance zero; of the 175 without twins,
> 148 have zero, 23 have +1, 2 have −1 and 2 have +2. **Narrowings:** ordinary growth adds no orders, but earlier studies
> did supply mixtures and signed sums over orders (the reordering line), so "nothing in the record sums over orders"
> holds for the laws, not for the record; order independence holds for complete readings of a fixed birth map (an
> allocation among interchangeable distinctions, or demand recomputed during growth, can change the end); the twin swap
> cancels when the two births are exchanged alone, not with their children; a supplied sign needs no comparison
> direction; a character gives a sign only on one orbit of readings, and one end can have imbalance 2 from one start and
> 0 from another; equal characters at the two ends need a transport law. Logged in `docs/CORRECTIONS.md`.
## What stands

1. **On the orders of one history, a sign is +1 around every square unless something tells the two births apart.**
   What the law makes at a step is the same in every order, twins give +1, and a −1 needs a chosen attribute and
   direction (the exchange sign is one such choice). The law makes none.
2. **On the readings of one end, the sign is a chosen character,** and carried along growth it reduces to the exchange
   sign or to the start's own sign.
3. **Nothing in the law sums over orders.** Every order reaches the same end, so even a chosen sign cancels nothing:
   the missing piece is a sum over histories, not a sign.

**Not shown.** That no future law sums over orders; the renaming census (kept, not run; another thread studies swap
symmetries).

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — a native sign on the path of reading | **Status:** Successful (an argument) | Every candidate needs a supplied attribute, character or exchange rule |
| Local direction — signs from the order of births | **STOP** (obstruction learned; referee pending) | The law makes no sign on paths and adds no paths |
| Broader exploration — a rule that sums over histories | Unmapped | Its first form has a literature (a partial order's sign-imbalance) |
| Long-term goal — G18 Comparing growth laws | Obstruction learned | The quantum part needs a sum over histories, which no recorded law performs |

**Next step:** Research directions — #1 proposed; the coordinator has assigned the contact study next

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The sign-imbalance of growth histories: weight each end by the signed count of its reading orders | 2/3 — the first sum over histories, though with a supplied sign | 3/3 — the histories are recorded | Compute it on small starts → an end whose imbalance survives its twins, or none | Proposed |
| 2 | The renaming census of `fold.py` | 1/3 — expected foregone | 3/3 — written | Run it → as the advisor predicts, or a counterexample to the twin lemma | Deferred (the swap-symmetry thread) |

**Corrections:** none.
**Goals:** checkpoint row added (G18); no goal changed.
**Assumptions:** none entered (nothing run; the test's choices would be registered if it runs).
**Scaffolds:** none used in the argument; the kept test names its engine (two engines) and its characters (three) as
choices.
**Advisor:** consulted before freezing; its repairs to part A (squares decide, twins, distinguishable pairs, the missing
sum) and its analysis of part B were taken.
