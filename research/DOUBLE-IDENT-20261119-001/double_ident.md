# Knots touching twice: the identification on most of the census

Epic `DOUBLE-IDENT-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead for `RELAY-IDENT-20261119-001#1`. Goal
G17. **Referee pending.**

**Record.**
- **The proof** (ticket A): [proof.md](../../proofs/DOUBLE-IDENT-20261119-001A/DOUBLE-IDENT-20261119-001A-P001_doubles/proof.md), with
  [machine_check.py](../../proofs/DOUBLE-IDENT-20261119-001A/DOUBLE-IDENT-20261119-001A-P001_doubles/machine_check.py), which ran on the
  whole touch census.
- **The census's growth classes** (ticket B, a computed readout with one stated check, D1):
  [dims.py](../../experiments/DOUBLE-IDENT-20261119-001B/DOUBLE-IDENT-20261119-001B-E001_dims/dims.py), output in
  [dims.json](../../artifacts/DOUBLE-IDENT-20261119-001B/DOUBLE-IDENT-20261119-001B-E001_dims/dims.json). The same computation ran
  once as a pilot before its contract, which says so.
- **The advisor** checked the statement before the freeze ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md)).

## The answer

**In the owner's terms.**
- **Touching twice changes nothing but the open counts.** From round 1 on, the growth reads a start only through two things: which
  live knots neighbour which, and how many open distinctions each live knot has. A second (or third) shared distinction between two
  knots only lowers their open counts. So the theorems proved for simple knot graphs hold for every multiplicity:
  - the clusters of the unrolled map;
  - the endless chains and relays;
  - the dimension of tree starts.
- **One edge case.** A start holding a single loose distinction closes at round 1. Its one offshoot takes every loose distinction,
  so its parity is already implied. All 32 census exceptions found by the relay tally are of this kind.
- **The census, round by round.**
  - All 11,512 arrangements in the class agree with the theorem in every round to round 6: each junction's parents and fresh count.
    11,075 of them have knots touching twice.
  - The 727 one-loose starts close as stated.
  - The class is 81% of the census starts that do not stall at once.
- **Why two is typical, now on 85% of the census's two-dimensional growths.** On every arrangement in the class, the growth class
  read off the map equals the measured one: 12,473 of 12,473 (closes, one dimension, two, or exponential). Of the census's 9,564
  two-dimensional growths, 8,108 are in the class.
  - A piece with two chains gives 3,525 of them.
  - A finished piece's relay gives 1,801.
  - Both together give 2,782.
- **What three shared distinctions do.** They only make knots dead or freeze a distinction (the advisor's analysis). A dead knot acts
  as a pure block and lowers its neighbours' open counts.
- **What is left.** 1,456 two-dimensional growths (15%) have a round-1 group of three, or two live knots with two common
  neighbours. That is the cycles direction, still open.
- **A correction to the relay report (not a block).** Most of the "61% with cycles" were outside the proofs only because their
  knots touch twice.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| D1 | on every census arrangement in the class, the growth class read off the relayed map equals the measured class | **held** | 12,473 of 12,473 (disclosed pilot of the same computation) |

## Known results, and what this adds

- **Known, cited once.** As RING-IDENT; GF(2) linear algebra for the implied test.
- **What this adds.** The identification and the dimension on the touch census's main class, with multiplicities. They are proved,
  and checked round by round on 11,512 arrangements.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: knots touching twice | **Status:** Successful (proved; D1 held, 12,473 of 12,473) | Multiplicity enters only through open counts; the census agrees round by round in the class |
| Local direction: an exact model of the cheapest parity growth | Continue | Proved on 81% of the census's growing starts; round-1 groups of three and double common neighbours remain |
| Broader exploration: what the cheapest growth builds | Known alternatives | The census's classes follow from the map: chains, relays, bare cycles, eddies |
| Long-term goal: G17 | Capability gained | Typical two dimensions explained on 85% of the census's two-dimensional growths |

**Next step:** Research directions — none selected yet (awaiting the coordinator)

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Round-1 groups of three and double common neighbours (`RING-IDENT-20261119-001#3`): the last 15% of two-dimensional growths and both of CLUSTER-ALL's breaks | 3/3 | 1/3 — the tree-of-blocks cover is the wrong object | find a complex whose clusters give CLUSTER-ALL's counts on the in-scope hyperedge starts → stop at one, or a start where none exists | Alternative · deferred |
| 2 | A write-up: one note on the identification line (RING-IDENT through DOUBLE-IDENT) for the owner and knotlab | 2/3 — the line's results in one place | 3/3 | draft from the four proofs → stop at a referee-ready note | Alternative · proposed |
