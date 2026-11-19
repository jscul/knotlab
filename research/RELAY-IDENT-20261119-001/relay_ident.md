# Relays: the count when a finished piece goes on, and why two is typical

Epic `RELAY-IDENT-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead for `RING-IDENT-20261119-001#1`, with
the census tally as its short follow-up. Goal G17. **Refereed:** report [R1](referee-R1/report.md), Theorems 4 and 5 and Corollary 6 confirmed line by line, no Block; one
wording point on the tally's reach folded in on 19 November (see Referee).

**Record.**
- **The proof** (ticket A): [proof.md](../../proofs/RELAY-IDENT-20261119-001A/RELAY-IDENT-20261119-001A-P001_relays/proof.md), with
  [machine_check.py](../../proofs/RELAY-IDENT-20261119-001A/RELAY-IDENT-20261119-001A-P001_relays/machine_check.py) and its output.
- **The census tally** (ticket B, a computed readout with one stated check, T1):
  [tally.py](../../experiments/RELAY-IDENT-20261119-001B/RELAY-IDENT-20261119-001B-E001_tally/tally.py), output in
  [tally.json](../../artifacts/RELAY-IDENT-20261119-001B/RELAY-IDENT-20261119-001B-E001_tally/tally.json). The same computation ran
  once as a pilot before its contract, which says so.
- **The advisor** checked the statement before the freeze ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md)).

## The answer

**In the owner's terms.**
- **A relay is one point with two endless chains, hung on a finished piece.** Take a piece of the map of joins with no cycle and no
  chain. It finishes when its clusters reach the whole piece. If another piece is still growing, the finished top is not implied,
  so the floor gives it one fresh distinction. From there it grows exactly like a knot with one open distinction: one point
  carrying two chains, making k junctions in the k-th round after the top. If it is the only piece, it closes.
  - This is now proved for every start whose map has no cycle of two or three blocks.
  - All 218 small starts agree, round by round.
  - The advisor's two predictions, made before the larger cases were grown, held: the path of seven knots, and the nine-knot spider
    with four legs, whose counts are C(t + 3, 3) + t + 1.
- **So a tree start's dimension is simple.** It is the largest number of chains in one piece, and a finished piece counts as two.
- **Why two is typical.** This is the sentence for the census.
  - Every growing tree-shaped start of up to five knots is one- or two-dimensional. Among the simple growing trees, which this
    proof covers, 91% are two-dimensional (266 of 292). Counting the trees whose knots touch twice it is 93% (3,753 of 4,055), but
    that figure rests on `DOUBLE-IDENT-20261119-001`'s extension (corrected wording, referee R1).
  - A start can only be one-dimensional if each of its two pieces has exactly one chain. If either piece has none, it relays and
    feeds two. More than two needs three chains in one piece, which takes at least seven knots.
  - So two is what small trees almost always give. A relay is part of the reason in 244 of the 266 simple ones, and in 2,678 of the
    3,753 when double touches are counted; 2,434 of those are double-touch trees, outside this proof.
  - The rule matches the census's measured dimension on all 307 simple trees. 36 of them are not bare plus surplus: a dead knot has
    a live candidate there. They agree too, with d_k counted among the live knots, which is how the tally reads it. On tree-shaped starts with knots touching twice it
    matches 3,980 of 4,012, outside the proof; the 32 others have two knots sharing three or four distinctions.
- **What it leaves open.** These tree-shaped starts are 39% of the census's two-dimensional growths (3,753 of 9,564). The other 61%
  have a cycle in their underlying graph. The first version said "a cycle of three or four knots, where the proofs' conditions
  fail". That is corrected (not a block) by `DOUBLE-IDENT-20261119-001`: what kept most of them out was that knots touch twice, not
  the cycles. With (S3) and (S4) read on live knots, 8,108 of the 9,564 are in the proved class, and only 1,456 have a round-1
  group of three or two live knots with two common neighbours.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| T1 | on simple census trees that do not stall, Theorem 5's dimension equals the measured one | **held** | 307 of 307 (disclosed pilot of the same computation) |

## Referee

Report [R1](referee-R1/report.md), 19 November 2026, by the coordinator's background referee thread, read line by line, with its own
model to round 9. No study code was run.
- **Confirmed.** Theorems 4 and 5 and Corollary 6. Its own model agrees on 218 of 218. Theorem 5 holds on all 94 trees of 2 to 9
  knots. The path of seven and the four-legged spider regrow as stated. Its tally recount gives 307 agree, 119 stall, 0 differ, and
  3,753 of 4,055.
- **Folded in (wording, not a block).** The tally reaches beyond the proofs' Setting.
  - 36 of the 307 simple trees are not bare plus surplus. "The proofs use only open_k and d_k" now says "with d_k counted among live
    knots".
  - The 93% and the 2,678 include trees with double touches, so they rest on `DOUBLE-IDENT-20261119-001`. Among the simple growing
    trees the share is 266 of 292 (91%).
- **Its own correction.** Its earlier points on the fresh rule in RING-IDENT and CHAIN-IDENT were mistaken: `freelib.floored` gives
  exactly d at an implied junction, as the proofs said. Logged in `docs/CORRECTIONS.md`.

## Known results, and what this adds

- **Known, cited once.** As CHAIN-IDENT.
- **What this adds.**
  - The relay as a theorem: the pendant rule applied to a finished top.
  - The dimension of every tree start in the class.
  - A measured answer to why two is the census's typical dimension on tree-shaped starts.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: relays and the census tally | **Status:** Successful (proved; T1 held, 307 of 307) | A relay is one point with two chains on the finished top; 218 of 218 starts agree; tree-shaped census growths are two-dimensional in 93% |
| Local direction: an exact model of the cheapest parity growth | Continue | Proved for every start without cycles of two or three blocks; the cycles of three or four knots remain |
| Broader exploration: what the cheapest growth builds | Known alternatives | Tree starts: dimension = chains per piece, a finished piece counting two; cycles: rational or algebraic |
| Long-term goal: G17 | Capability gained | The census's typical two dimensions explained on tree-shaped starts; the rest located |

**Next step:** Research directions — none selected yet (awaiting the coordinator)

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Knots touching twice: extend the proofs to multiplicity two (3,980 of 4,012 already agree), and find what three shared distinctions do | 2/3 — the census's tree-shaped starts are mostly of this kind | 3/3 — the disagreements are named | check whether a double touch changes the map of joins or only open distinctions → stop at a proof, or the first double touch that changes the count | Alternative · proposed |
| 2 | Cycles of three and four knots (`RING-IDENT-20261119-001#3`): the other 61% of two-dimensional growths | 3/3 — the rest of "why two" | 1/3 — the tree-of-blocks cover is the wrong object | find the complex whose clusters give CLUSTER-ALL's chain count there → stop at one, or at a start where none exists | Alternative · deferred |

## Final report as sent (2026-11-19 14:20 UTC)

**Outcome:** Relays are now proved, and they explain why two is the census's typical dimension on tree-shaped starts. A piece of the map of joins with no cycle and no chain eventually finishes. If another piece is still growing, the finished top gets one fresh distinction from the floor. From there it grows like a knot with one open distinction: one point carrying two endless chains, making k junctions in the k-th round after the top. If it's the only piece, it closes. All 218 small starts agree round by round, and the census tally's one check held (307 of 307). Closed, referee pending.

- **The dimension of a tree start** is the largest number of chains in one piece, and a finished piece counts as two.
- **Why two is typical.** Every growing tree-shaped start of up to five knots is one- or two-dimensional, and 93% are two-dimensional (3,753 of 4,055).
  - A one-dimensional start needs each of its two pieces to hold exactly one chain.
  - A piece with no chain relays and feeds two.
  - Three chains in one piece takes at least seven knots.

  So small trees almost always give two, and a relay is part of the reason in 71% of them.
- **Checks.** The advisor's predictions, made before I grew the larger cases, held exactly. The path of seven grows 7, 7, 7, 8, 10, 12, …, and the nine-knot spider with four legs grows C(t + 3, 3) + t + 1. On the census, the rule matches the measured dimension on all 307 simple trees. It also matches 3,980 of 4,012 tree-shaped starts whose knots touch twice, which is outside the proof; the 32 exceptions all have two knots sharing three or four distinctions.
- **What stays open.** Tree-shaped starts are 39% of the census's two-dimensional growths (3,753 of 9,564). The other 61% have a cycle of three or four knots, where the proofs' conditions fail. CLUSTER-ALL's computed rule covers those, but it isn't proved.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: relays and the census tally | **Status:** Successful (proved; T1 held, 307 of 307) | A relay is one point with two chains on the finished top; 218 of 218 agree; 93% of growing tree-shaped census starts are two-dimensional |
| Local direction: an exact model of the cheapest parity growth | Continue | Proved for every start without cycles of two or three blocks; cycles of three or four knots remain |
| Broader exploration: what the cheapest growth builds | Known alternatives | Trees: dimension = chains per piece, a finished piece counting two; cycles: rational or algebraic |
| Long-term goal: G17 | Capability gained | The census's typical two dimensions explained on tree-shaped starts; the rest located |

**Next step:** Research directions — none selected yet (awaiting the coordinator)

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Knots touching twice: extend the proofs to multiplicity two (3,980 of 4,012 already agree) and find what three shared distinctions do | 2/3 | 3/3 | check whether a double touch changes the map or only open distinctions → stop at a proof, or the first double touch that changes the count | Alternative · proposed |
| 2 | Cycles of three and four knots: the other 61% of two-dimensional growths | 3/3 — the rest of "why two" | 1/3 — the tree-of-blocks cover is the wrong object | find a complex whose clusters give CLUSTER-ALL's chain count there → stop at one, or a start where none exists | Alternative · deferred |

**Corrections:** one, Not a block, from CHAIN-IDENT's referee (both proofs confirmed line by line). The chains proof's control count of relay starts is 115 of 137, not 137, because its check counted a non-live knot twice; the 22 stars close exactly as their clusters do. It's logged in docs/CORRECTIONS.md and HISTORY.md (581a639a2), along with four wording points. RING-IDENT's referee points are also folded in (94e027daf). **Goals:** G17 checkpoint (capability gained). **Assumptions:** none changed. **Basket:** `RING-IDENT-20261119-001#1` taken. **Advisor:** Fable 5.2, before the freeze, staying within its text. It found a hole in my implied-test case list and fixed it with one invariant over all pieces. It suggested stating the relay as the pendant rule applied to the top, and named the small cases. Its two predictions held exactly.

**Referee hand-off.** The proof is `proofs/RELAY-IDENT-20261119-001A/RELAY-IDENT-20261119-001A-P001_relays/proof.md`, the tally `experiments/RELAY-IDENT-20261119-001B/RELAY-IDENT-20261119-001B-E001_tally/tally.py`, and the decision note `research/RELAY-IDENT-20261119-001/relay_ident.md`. Please check:
- step 3's invariant;
- step 4's induction on the J(i, l);
- Theorem 5's assembly;
- that the tally reads the census's sizes (not bare) correctly.
