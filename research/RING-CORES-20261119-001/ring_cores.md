# Which rings of knots feed themselves within five places

Epic `RING-CORES-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead, which joins the identification line to
the eddy line. Goal G17. **Referee pending.**

**Record.**
- **The proof** (ticket A):
  [proof.md](../../proofs/RING-CORES-20261119-001A/RING-CORES-20261119-001A-P001_rings/proof.md). It was frozen as Partial in
  commit `65485ebf7` with its checks K1–K6 stated before the run, then completed.
- **The machine check.**
  - Code: [ringlib.py, job.py, merge.py](../../proofs/RING-CORES-20261119-001A/RING-CORES-20261119-001A-P001_rings/).
  - Run through the shared runner: `RING-CORES-A1`, `runs/ring-cores`, 52 cases, all ok, 16:18 to 16:28 UTC.
  - Output: [machine_check.json](../../proofs/RING-CORES-20261119-001A/RING-CORES-20261119-001A-P001_rings/machine_check.json).
- **A pilot** of seven starts was run before the freeze and is disclosed in the advisor's question.
- **The advisor** checked the statement before the freeze ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md)).

## The answer

**In the owner's terms.**
- **Within five places, an eddy is a ring of knots carrying something extra, and nothing else is.** In the proved class, with every
  knot live and at most five places, a start grows exponentially exactly when its knots form one ring that carries:
  - a hung knot, which is a single knot touching one ring knot;
  - or a spare place, at a ring knot that is not next to a hung knot.

  A bare ring makes the same number of junctions every round, forever. Lines and stars of knots never grow exponentially (the cap
  study). This is proved for every size.
- **The rings themselves are forced by the cap.** Each has 5 knots, or 7 or more (three, four and six are out of the class). A
  ring knot carries at most one hung knot, and hung knots sit at least three apart. A spare can only go on a ring knot with no hung
  knot beside it, and a hung knot can carry up to two spares of its own.
- **Its rate is a product of three kinds of factor, and it is proved.** Going once round the ring multiplies the count by the
  round-weight W(y), and the rate x solves W(1/x) = 1. W is a product of:
  - y for each knot on the walk round the ring;
  - 1 + y for each spare;
  - 1 + y(1 + y)^b for each hung knot with b spares.
- **The walk goes two knots at a time,** because two ring knots join through the knot between them.
  - An odd ring is one walk of L knots.
  - An even ring is two walks of L/2. A hung knot feeds the walk of its ring knot's neighbours, and a spare feeds its own knot's
    walk.
- **The rate depends only on how many of each factor there are, not on where they sit.** Examples:
  - **one spare, or one hung knot with no spare, on a walk of n knots:** the root of x^(n+1) = x + 1, so the ring of seven with a hung
    knot grows at 1.0970;
  - **two spares on the ring of five:** 1.2628;
  - **three hung knots on the ring of nine:** x^4 = x + 1, so 1.2207.
- **Nothing within five places grows faster than the golden ratio.** A ring whose every knot carries a spare grows at
  1.6180, whatever its length. This is proved after the run: no hung knot can beat two spares.
- **It matches the program's own growth exactly.** All 23,098 decorated rings of 5 to 14 knots were grown. Their counts equal the
  formula on every round, from round 10 to round 40. Of 162,576 small starts of up to nine knots, every exponential one in the class
  is such a ring.
- **For A109: a complete catalogue, in this class.** The catalogue's ring family and its interfaces (`LOOP-CATALOGUE-20261119-001`)
  were measured. They are now proved, and proved complete within the cap: three kinds of factor generate every in-class eddy.
- **What stays outside, plainly.** The theorem says nothing about the following starts:
  - **Knots of six or more places.** The catalogue's hanging path of two knots, (1 + y)/(1 − y), needs one.
  - **Dead knots,** which already lift the cap's bound on chains.
  - **First-round groups of three, or two live knots with two common neighbours.** There the break-shape eddies and the explosive
    kind live (`BREAK-EDDIES-20261119-001`), which keep A109 under challenge.
  - **Stalls.**

## Theorem and checks

| Statement | Status | Evidence |
| --- | --- | --- |
| Lemma 1: a ring start's shape and open counts are forced, except spares (0 or 1 on plain ring knots, 0 to 2 on hung knots); every such shape is in the class | proved | K1: 23,098 words, every one in the class with the forced counts |
| Lemma 2: one ring of blocks for odd L, two for even; a hung knot feeds the opposite walk, a spare its own | proved | K3 (the even-L assignment checked on every even word) |
| Theorem 3: the per-round count is [z^(t+1)] of a rational function with denominator 1 − W | proved | K3: engine equal to the formula on every round of all 23,098; K4: closed form equal to the direct sum |
| Theorem 4: bare means n per round; otherwise exponential at the root of W(1/x) = 1 | proved | K2: dims.predict agrees on every word; K5: the advisor's four predicted rates |
| Corollary 5: within the cap, in the class, the eddies are exactly the decorated rings | proved | K6: 162,576 small starts, 1,098 exponential ones, all decorated rings |
| Proposition 6 (post hoc): no ring within the cap beats the golden ratio | proved | the run's fastest at every L is 1.6180 |

All six checks passed.

## Assumptions

- **A109** (eddies are few in kind and shared): history line. Within the class and the cap, the eddies are exactly the decorated
  rings, generated by three kinds of factor (proved). It stays **Under challenge** because of the explosive kind outside the class.
- No new entry: the epic took nothing by default.

## Known results, and what this adds

- **Known, cited once.**
  - Counting connected sets on a periodic decorated line by transfer: lattice animals on strips (Klarner 1967).
  - The rational generating function and its dominant pole (Pringsheim; Flajolet and Sedgewick, *Analytic Combinatorics*, IV–V).
  - The golden ratio as the growth of the simplest two-choice recurrence (Fibonacci).
- **What this adds.** The cheapest growth's eddies within five places, and in the class, with their rates:
  - their exact counts at every round;
  - the proof that the catalogue's three factors are all there is;
  - the golden ratio as the most a ring of such knots can reach.

## Limitations

- **Every knot live, at most five places, in the class.** Everything else is outside, as listed above.
- **The engine check** reaches 10 to 40 rounds per word, with a median of 14, up to rings of 14 knots. The theorem covers every
  length.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md)), before the
freeze, staying within its text.
- **It confirmed** the cluster structure, the orbit count and the dominant root, and it computed the four rates that K5 then
  confirmed.
- **It asked for** the even-L rule to be stated outright (a hung knot feeds the opposite walk, a spare its own).
- **It raised a possible S3 gap:** three knots around a hung knot's ring knot. This is not a gap. Those three share a common
  neighbour, so they are not a valid set and give three pairs; the proof now says so.
- **Its wording points were adopted:** "every knot live", star cores cited, and the round-weight per piece.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: rings within five places | **Status:** Successful (proved; 6 of 6 checks) | The in-class eddies within the cap are exactly the decorated rings, with a proved rate formula; 23,098 rings grow exactly as the formula says |
| Local direction: the eddy catalogue (A109) | Research directions | Complete in the class within the cap; outside it, the break-shape and explosive eddies remain |
| Broader exploration: what the cheapest growth builds | Known alternatives | Within five places with no dead knot: lines and stars give at most two dimensions, rings give one or exponential, and nothing else occurs |
| Long-term goal: G17 | Capability gained | Typical and rare growth within five places is now classified completely in the class, with rates |

**Next step:** Research directions — none selected yet (awaiting the coordinator)

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The explosive kind (`BREAK-EDDIES-20261119-001`): the eddies outside the class, whose groups of three overlap, the last part of A109's challenge | 3/3 — it decides A109 | 1/3 — the cover of blocks is the wrong object there | take the smallest explosive start and find what its groups of three do round by round → stop at a description, or a size where it changes kind | Alternative · proposed |
| 2 | Dead knots within the cap: classify the in-class starts with dead knots (dead hubs lift the chain bound) | 2/3 — completes the cap's classification | 2/3 — dead knots act as blocks only | extend Lemma 2 of the cap study with dead knots as blocks → stop at a shape theorem, or a start it misses | Alternative · proposed |
| 3 | Dimension grows linearly under random trees (`WEIGHTINGS-20261119-001#1`) | 2/3 | 3/3 | prove each parity class's chain-carrying leaves concentrate → stop at a proof, or a size where the measured dimension departs | Alternative · in the basket |
