# The second kind of check: what stands

Epic `SECOND-CHECK-20261126-001` (G18, at the coordinator's pick after `TWO-CLASS-SIGN-20261126-001`; the scaffolds of
A291), closed 26 November 2026. A check by the thread: computed, with an argument; advisor consulted read-only in the
repository; referee pending. [The note](README.md)


> **Refereed (R1, [report](referee-R1/report.md)): confirmed with fixes, no Block.** All 26 pinned exchanged holders pass the
> record's knot test, and neither reading of the exchange selects a relative sign. **Narrowings:** the pinned exchange
> was confirmed to give back the bare ring at five, seven and eight knots (not six); at eight knots two least free reads
> use only loose distinctions and two least pinned changes avoid every old ring distinction; short moves keep either
> relative sign, which a supplied class-changing read can tell apart. **Not a block:** exchanging twice does not give
> back the grown ring, so the intuition that the two are each other's dual fails; the repetition-code comparison is a
> comparison, not an equivalence; the two-ring square would need readers holding parent-to-child distinctions.
> **And a later correction by the thread** (the both-distances study, `BOTH-LONG-20261126-001`): "one distance is always
> short" holds after one round only; grown further, a ring's class has both distances equal to n on odd rings (from
> about (n − 1)/2 rounds), and on even rings one distance equal to n with the other growing by two a round. Logged in
> `docs/CORRECTIONS.md`.
## What stands

1. **The exchanged pattern** (each move read as a knot on the distinctions it changes) is lawful by the local test only
   with loose values pinned, and then it is the bare ring itself: the exchange undoes growth, and growth does not commute
   with it.
2. **One distance is always short** (free: read across n, change by 5; pinned: read by 3, change across n): a repetition
   code, not the toric code *(after one round only; corrected by `BOTH-LONG-20261126-001`)*.
3. **No native second check.** As a value law the exchanged knots are a further classical restriction; as invariance of
   the weighting they are the motion study's recorded reading, which leaves the relative sign free. The supplied change
   read shows the sign to one reader, and to two readers only as a table a shared hidden value reproduces.

**Not shown.** That no rule could make one; the two-ring Mermin–Peres square (a test of the supplied reading).

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — a second check in the exchanged pattern | **Status:** Successful (a negative with reasons) | Lawful only when pinned, and then it is the start; one distance always short |
| Local direction — sectors with a relative sign from the recorded laws | **STOP** (obstruction learned; referee pending) | The sign is a preparation; the only reading that shows it is supplied |
| Broader exploration — a law that makes both distances grow | Unmapped | Would need moves that are long in both readings: the literature's two-dimensional codes |
| Long-term goal — G18 Comparing growth laws | Obstruction learned | The recorded laws make a classical code and its sectors, never the conjugate check |

**Next step:** Research directions — the coordinator's call

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A start whose classes have both distances long (read and change both across the structure), from two crossing rings | 2/3 — the first structure the toric code's logic could live on | 2/3 — the map's programs read it | Build two rings sharing knots, map read and change distances → both grow, or one stays short | Proposed |
| 2 | The two-ring Mermin–Peres square under the supplied change read | 1/3 — tests the supplied rule | 3/3 | Compute it → the square is won as the quantum rule predicts, or not | Deferred |

**Intuition (an exact link, not evidence; R1: exchanging twice does not give back the grown ring, so this duality
fails).** The grown ring and its exchanged pattern are each other's dual in the literature's sense: the exchange of the
grown ring returns the start, as the dual of a dual returns the lattice. A ring is
one-dimensional, and one-dimensional codes are repetition codes, with one distance short: the toric code needs a
two-dimensional pattern, where both the cycle and the cut are long.

**Corrections:** none (the advisor's catches were fixed before anything left the thread: the commuting test had not run,
and the distances depend on the pinning).
**Goals:** checkpoint row added (G18); no goal changed.
**Assumptions:** A291 history (pinning decides which distance is short; with it the exchanged pattern is the start).
**Scaffolds:** loose values free or pinned (swapped; the result changes with it, so the lawfulness is the pinning's), the
move rule (A291), one round, rings. The absence of a native second check holds under both.
**Advisor:** consulted read-only in the repository with the advisor skill; its six catches (the commuting test never
ran; the distances; pinning; the local proxy for "lawful"; the exchange returns the start; the two-reader table) were
checked and taken; entry in `docs/ADVISOR_HIVEMIND.md`.
