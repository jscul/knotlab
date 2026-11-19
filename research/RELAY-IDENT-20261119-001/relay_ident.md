# Relays: the count when a finished piece goes on, and why two is typical

Epic `RELAY-IDENT-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead for `RING-IDENT-20261119-001#1`, with
the census tally as its short follow-up. Goal G17. **Referee pending.**

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
  - Every growing tree-shaped start of up to five knots is one- or two-dimensional, and 93% are two-dimensional (3,753 of 4,055).
  - A start can only be one-dimensional if each of its two pieces has exactly one chain. If either piece has none, it relays and
    feeds two. More than two needs three chains in one piece, which takes at least seven knots.
  - So two is what small trees almost always give, and in 71% of them a relay is part of the reason (2,678 of 3,753).
  - The rule matches the census's measured dimension on all 307 simple trees. On tree-shaped starts with knots touching twice it
    matches 3,980 of 4,012, outside the proof; the 32 others have two knots sharing three or four distinctions.
- **What it leaves open.** These tree-shaped starts are 39% of the census's two-dimensional growths (3,753 of 9,564). The other 61%
  have a cycle of three or four knots, where the proofs' conditions fail. CLUSTER-ALL's computed rule (groups of three as their
  own blocks) gives their chains too, but that part is not proved.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| T1 | on simple census trees that do not stall, Theorem 5's dimension equals the measured one | **held** | 307 of 307 (disclosed pilot of the same computation) |

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
