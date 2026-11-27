# A presentation is a completed system with one knot left out: what stands


> **Referee R1: refuted, two Blocks** ([report](referee-R1/report.md)). The census counts hold and extend: one marked
> not-all-equal presentation on 7,074 of 7,075 census starts, every competitor class tried (other knot counts, two-place
> rules, disconnected, repeated supports) adding none; but the one ambiguity has no loose distinction, so the census
> never tested family recovery under not-all-equal. **Block:** in general it fails: two connected ten-knot
> presentations with the same 209,952 states and the same two loose distinctions have two families and one (each has
> two redundant laws; [witness](referee-R1/family_witness.json)). **Block:** at the second layer the loose set does not
> choose the basis: of 11 possible loose sets, 8 select one basis and 3 admit four each, with different knot sizes
> (3, 3, 3, 6 against 3, 3, 4, 5); the 20 bases come from four different completions. **Narrowings:** under parity the
> entailment holds with the cost restricted to changes holding exactly one loose distinction of each family and no other
> (a seven-knot start gives 8 against 6 for the earlier pair cost); the completion adds the parity law on the loose set
> (often of fewer than three places), and Whitney's twists cover the two-connected case; under not-all-equal the parity
> argument is what is not available, other recovery results hold (an earlier all-size classification covers connected
> presentations with every law essential, `THREE-READERS-AND-GROWTH-20261120-001B`); a3 as frozen measured law
> distinctions, 92 against 40, reversing the prediction (the carrier count 36 against 40 was not what the frozen code
> measured); what recurses: on the ring witness each family's live knots form a path that growth lengthens by one,
> and ordinary growth does permit a two-place birth that closes (three laws on abl, cdm, abcd give one on lm).

Epic `ONE-STATEMENT-20261127-001` (the coordinator's pick of the advisor's third direction; goals G17 with G18), closed
27 November 2026. A check by the thread, not registered: computed, each part frozen before its run; referee pending.
[The note](README.md) · [The statement](statement.md)

## What stands

1. **The advisor's four checks held** (a): of 840 bases of the relations among the nine facts of three rings of four,
   20 keep every fact in at most two relations, 12 meet in a ring and one is the tree; any start law frees all three
   four-place relations; "shorter" depends on what is counted (rings of 10, 4 and 4: 3 against 4 places, 40 against 36
   carrier distinctions, 40 against 92 law distinctions); the three marked-loose pairs behave as predicted.
2. **One statement for both layers** (b): under parity a presentation is a completed system with one knot left out,
   named by the loose set (Whitney's theorem, as in `STATES-GROWTH-20261119-001`); the marked-loose agreement on the
   families and the tree is entailed, so it checks the code; "at most two holders" at the second layer is our
   requirement (A306).
3. **No recursion here** (c): read as a start of its own, the tree presentation grows four three-place births and
   closes at round 3; on the grown witness the nine facts gain a two-place copy per family each round and never close.
4. **[Narrowed, R1: on the census; in general even the marked not-all-equal family partition can vary.] Under not-all-equal the states choose the knots** (d): with the loose set marked, one presentation on 1,193 of
   1,194 census starts read (parity: 509 of the same 1,194), and the same families and tree on all of them.

**Not shown.** Census starts 1,194 to 1,999 under not-all-equal (stopped at the time limit) and the rest of the census;
the tree-or-loop question under not-all-equal at the second layer (it has no class facts there to bind); larger starts.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the advisor's checks, the statement, recursion, the law swap | **Status:** STOP (refuted by R1 on two points; a3 as frozen reversed) | Parity's presentations are many and the states cannot choose among them; not-all-equal's states choose the knots |
| Local direction — what chooses the knots | Narrowed (R1) | On the census with the loose set marked, one presentation on 1,499 parity and 7,074 not-all-equal starts; outside the census even the marked not-all-equal family partition can vary |
| Long-term goal — G17 with G18 | Narrowed | Selection at a further layer is open (R1) |

**Next step:** Research directions — the coordinator's call

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Under not-all-equal the states name the knots: do they also name a second layer (facts held by the whole whose relations the states fix), now that the knots are not a choice? | 3/3 — the tower where the presentation is not ours | 1/3 — not-all-equal has one class wherever read | Read what not-all-equal growth keeps that no single knot reads (joint values of distant parts) → a fact, or none | Proposed |
| 2 | Finish the census under not-all-equal (starts 1,194 on), faster code | 1/3 | 3/3 | Rerun with a cheaper solver → the same, or an exception | Alternative |

**Corrections:** none from this study.
**Goals:** checkpoint row added.
**Assumptions:** A306 added (at most two holders at the second layer, a scaffold).
**Basket:** none.
**Scaffolds:** A306; the presentations searched (as many knots, at least three places, connected); the census prefix
under not-all-equal.
**Advisor:** its third direction and its checks, all confirmed; consulted before this study (TREE-PROOF-20261127-001/advisor).
