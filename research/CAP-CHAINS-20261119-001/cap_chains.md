# Chains under a cap on places: five bounds them at two, six bounds nothing

Epic `CAP-CHAINS-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead for `WEIGHTINGS-20261119-001#2`. Goal
G17. **Referee pending.**

**Record.**
- **The proof** (ticket A):
  [proof.md](../../proofs/CAP-CHAINS-20261119-001A/CAP-CHAINS-20261119-001A-P001_caps/proof.md), frozen as Partial in commit
  `6ef1bff5a` with its checks C1–C8 stated before the machine check ran, then completed.
- **The machine check:**
  [machine_check.py](../../proofs/CAP-CHAINS-20261119-001A/CAP-CHAINS-20261119-001A-P001_caps/machine_check.py), output in
  [machine_check.json](../../proofs/CAP-CHAINS-20261119-001A/CAP-CHAINS-20261119-001A-P001_caps/machine_check.json).
- **The advisor** checked the statements and the families before the freeze ([question](advisor/question_1.md),
  [answer](advisor/answer_1_fable.md)).

## The answer

**In the owner's terms.**
- **Without dead knots, five places allow at most two chains in any piece of the map.** This holds for every start in the proved
  class whose knots all have at most five places and keep at least one open distinction, multiplicities included.
  - **The reason is one count.** A knot's places must cover its touches and the pairs it joins in the first round. With five, no
    knot can touch three knots that themselves touch others.
  - **So the knot graph is one line or one ring of knots,** with single knots hung on it. A chain needs a knot with open places left
    after its joins. On a line only the two ends can carry one, and a ring carries none.
- **So a tree-shaped start of such knots closes, or grows in one or two dimensions.** This is now proved for every size, not only
  sampled.
  - A ring of knots carries no chains, but it can still grow exponentially. The ring of seven with one knot hung on it does, at about
    9% a round.
  - So five places bound the dimension of tree starts, and bound only the chains of the others.
- **Five is the largest cap that does this.** At six places, with every knot live, bare trees in the class carry any number of
  chains in one piece.
  - Take branch knots of degree three joined through single knots, with arms of two knots.
  - The seven-knot spider is three-dimensional, and the 19-knot tree with six arms is six-dimensional.
- **Dead knots lift the bound even at five places.** A dead knot is a knot whose places are all shared. It joins its neighbours
  without demanding a place for any pair, because it is no one's partner. A binary tree of dead three-place hubs gives any number of
  chains:
  - ten knots give three dimensions;
  - 31 knots give six.
- **Every family grows as predicted.** All six families are in the class, and their growth equals the relayed cover round by round
  to round 8. The engine's counts have exactly the degree the advisor predicted before they were grown: two to five for the
  six-place trees, and two and five for the dead-hub trees.
- **What this says about "dimension bounded by knot size."**
  - It is a statement about the knots: at most five places and no dead knot give at most two chains per piece.
  - The bound is sharp, and it needs both conditions.
  - The census's typical two fits this. Its starts have at most five knots, and no in-class census start carries three chains
    (exhaustive). The dead-hub tree above needs ten knots, and three or more in the census needs mutually touching knots.
  - Past the census, under SCALE-SHARE's weighting, dead-hub trees are rare enough that none appeared in the class.

## Theorem and checks

| Statement | Status | Evidence |
| --- | --- | --- |
| Lemma 1: in the class with every knot live, no cycle of 3, 4 or 6 knots; groups are candidate pairs; d_k = Σ (deg_w − 1) | proved | C4: 2,187 all-live 6-cycle starts all out of the class or stalling |
| Lemma 2: with cap 5 too, the non-leaves form one path or one cycle | proved | C1: 86 graphs to 12 knots, cores 58 paths, 22 cycles, 6 stars or less |
| Theorem 1: at most two rays in a piece, relay included | proved | C2: 200,597 open assignments; C5: the census's 963 all-live in-class arrangements |
| Corollary 2: tree starts close or grow in one or two dimensions; cycle cores carry no rays | proved (the cycle cores' growth class is the computed rule) | C3: 162,576 simple starts read by the program's code, none in the class three or more |
| Theorem 3: at cap 6 all live, and at cap 5 with dead knots, any number of rays in one piece | proved | C6, C7: S_3–S_6 and T_1, T_2 in the class, read and grown as R dimensions |
| The ring of seven with one leaf is exponential at cap 5 (the advisor's risky case) | computed | C8: in the class, read exponential, cover equal to round 8, engine ratio about 1.09 a round to round 60 |

8 of 8 checks passed.

## Assumptions

- **A106** gets a history line: the five-place cap is what bounds the chains of all-live starts, proved.
- No new entry: the epic took nothing by default.

## Known results, and what this adds

- **Known, cited once.**
  - Caterpillars, the trees whose non-leaves form a path: Harary and Schwenk (1973).
  - The identification line's theorems.
- **What this adds.** A bound on the cheapest growth's dimension from the size of knots alone, with its exact threshold:
  - five places with no dead knot allow at most two chains per piece;
  - six places allow any number;
  - dead knots lift the bound even at five.

## Limitations

- **Cycle cores.** Their growth class, one-dimensional or exponential, is DOUBLE-IDENT's computed rule, not proved here.
- **Dead knots.** They are allowed only in Theorem 3. How often a weighting makes dead hubs is not measured.
- **The engine's degree check** reaches 16 to 24 rounds per family.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md)), before the
freeze, staying within its text.
- **It confirmed** Claim 1's proof and both constructions.
- **It added** the 6-cycle step of Lemma 1 and asked for the relay's reading to be pinned down.
- **It caught the overclaim** in my headline: cyclic starts at cap 5 can grow exponentially. The headline now speaks of tree starts.
- **Its degrees held.** It miscounted one family's knots (17 for 19).

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: what the five-place cap forbids | **Status:** Successful (proved; 8 of 8 checks) | No dead knot and at most five places allow at most two chains per piece; sharp at six; dead knots lift it |
| Local direction: what the cheapest growth makes typical | Research directions | Dimension is bounded by knot size exactly when no knot is dead, and the bound is two at five places |
| Broader exploration: what the cheapest growth builds | Known alternatives | Tree starts: chains per piece; the cap fixes how many a knot can feed |
| Long-term goal: G17 | Capability gained | The census's two is now explained by a proved bound on knots, not only by sampling |

**Next step:** Research directions — none selected yet (awaiting the coordinator)

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Dimension grows linearly under random trees (`WEIGHTINGS-20261119-001#1`) | 2/3 | 3/3 | prove each parity class's chain-carrying leaves concentrate → stop at a proof, or a size where the measured dimension departs | Alternative · in the basket |
| 2 | Cycle cores at cap 5: prove that a bare ring is one-dimensional and every ring with a knot hung on it is exponential, completing what five places allow | 2/3 — the classification under the cap, proved | 2/3 — the cores are rings with sparse leaves | compute the ring's cover count with one leaf → stop at a proof, or a ring with a leaf that is not exponential | Alternative · proposed |
| 3 | Mutually touching knots (`SCALE-THEOREM-20261119-001#1`) | 2/3 | 1/3 | find the complex on the census's out-of-class starts → stop at one, or a start where none exists | Alternative · in the basket |
