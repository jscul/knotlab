# Every accretion law

Epic `GROW-FACE-20261110-001` (program topology, group `spacing`, `WEAK-APER-20261110-001` direction 2, the same as
`HARD-FLAT-20261107-001#3` and `GROW-COIN-20261107-001#2`; G1), 2026-11-10. Pre-registered in commit 9df96cd7f, with what would count,
the checks and the decision frozen there. It is the board line's deciding epic.

## The question

- **Where it comes from.** The line's static epics, `BOARD-DIST-20261110-001` to `PLACE-FLIP-20261110-001`, found that a uniform law
  chooses the plane only by naming a face. Growth was the one route left that could change that verdict. The coordinator's go-ahead of
  19:30 UTC asked for this epic to decide it, with what would count frozen first and checked against what is already closed.
- **The question.** Can an accretion law, one that grows a board from a seed, choose the plane without naming a face?

## The question in standard terms

Local growth rules that only add vertices and edges, run from a finite seed under every fair schedule: which limits they force,
whether the square grid is one of them without a rule that closes cycles, and what growth gives that a static local rule with the
same labels does not.

## Conclusions

| # | Conclusion | Kind | Ticket |
| --- | --- | --- | --- |
| 1 | **Without closing a cycle, only trees.** An accretion law none of whose actions closes a cycle grows, in each component, the seed's component with trees attached: asymptotic dimension at most 1, though the comb shows it can grow quadratically. Under the frozen definition closing a cycle is naming a face, so this follows from the definition. | proved; immediate from the definition | A (G1) |
| 2 | **A named square grows the plane, with or without an arrow.** A radius-2 law that closes squares grows the square spiral, one place at a time, in its only order. It needs no arrow: coordinates mod 3 alone suffice, because the head is the only place whose view looks like a head's. | proved; checked to 40 rings | A (G2, G2′) |
| 3 | **Growing everywhere at once, an order splits it.** For every radius r ≥ 2 and every fixed priority of the four offsets, the law that closes every square it sees has a fair order whose limit is not the grid. Two arms grow longer than its view, and the slit between them, filled from the top, gets two places at one position. | proved; checked for r = 2, 3, 4, 6 and all 24 priorities | A (G3) |
| 4 | **The same nine values, static and grown.** With coordinates mod 3 and a named square, a static law allows the plane's cylinders and tori (`BARE-NAMES-20261110-001A`, T4); grown from one seed it gives the plane itself. | proved, from 2 and T4 | A |
| 5 | **The checks.** P1 to P3 held as frozen; P4 and P5, added after the review, held. | computed | A |

## Answer

Not without closing cycles, and closing a cycle is what naming a face means here, so the frozen question could only be answered no.
The registration should have said so (`docs/CORRECTIONS.md`, 2026-11-10). The informative part is what happens with a named face:
- **Growth does choose the plane.** A square-closing law with coordinates mod 3 as its only values grows the square spiral in its
  only order (G2′).
- **Static laws with the same nine values cannot.** They allow the plane's cylinders and tori too, and only aperiodic tiles remove
  those. So growth from one seed adds one connected world with no quotient.
- **Growing everywhere at once fails.** The law that lets every place fill a missing neighbour, at any radius and in any fixed
  priority, is defeated by an order that grows two fronts apart and lets them meet beyond the view (G3).

The verdict stands, the plane needs a named face. For growth it holds by definition, and with a named face growth goes further than
static laws.

## The line's closing summary

The board as distinctions, 2026-11-10: the line that made the board itself part of the allowed states (the challenge of A51).

| Epic | Route | What it found |
| --- | --- | --- |
| `BOARD-DIST-20261110-001` | Static, names as words in two letters | A law that names no relation allows the tree whenever it allows an infinite board; a named square with aperiodic tiles forces exactly the plane |
| `LEIBNIZ-BOARDS-20261110-001` | Static, Leibniz's rule | Boards are the stabilizer quotients; no one-bit law forces the plane |
| `RIGID-WORLDS-20261110-001` | Static, identity at radius 2 | No one-bit law forces a two-dimensional torus |
| `WEAK-APER-20261110-001` | Static, Leibniz's rule, every law | Every infinite law has a free solution, so the tree is always a board and the plane is never forced |
| `BARE-NAMES-20261110-001` | Static, names without letters | Finitary laws allow structureless boards, count laws the tree; a named face gives planes one per component; boards are not frozen |
| `PLACE-FLIP-20261110-001` | Nativeness without letters | The board's knots with the values are native in worlds of finite pieces; on the free board most values are frozen |
| `GROW-FACE-20261110-001` | Growth from a seed | Without closing cycles only trees, by definition; a square-closing law with coordinates mod 3 grows the plane from its head alone; growing everywhere at once, an order splits it |

- **The line's verdict.** A uniform local law, static or growing, chooses the plane only by naming a face.
  - For static laws this is a theorem of the line: a law that names no relation allows the tree.
  - For growth it follows from the definition, since every cycle a local step closes is one it names.
- **What naming buys.** With a named face, static laws force the plane only with aperiodic tiles, and without letters only
  componentwise. Growth from one seed forces the plane itself, with nine periodic values. So growth adds:
  - one connected world with no quotient;
  - scale and a clock (`BOARD-READ-20261110-001`);
  - no face of its own.

  Nothing in the line found the plane emerging without a named face.
- **Routes closed.**
  - The static routes: laws that name no relation, Leibniz's rule, identity at a radius, names without letters.
  - The accretion route. It is answered rather than ruled out: growth does force the plane, by naming a face.
- **Left in the basket, not run.** Each would restate the verdict:
  - edge labels as in Radin's rules (B16, shared with the pinwheel line);
  - a growing radius for rigid worlds;
  - Leibniz's rule with abstract names.
- **What could reopen the line.** A finer reading of naming, the challenge of A61: a rule names a face only when it fixes the face's
  length or offsets. A law that closes whatever short cycles it sees, without coordinates, and still grows the plane would show the
  face emerging rather than written in. None is in the basket.
- **Parked.** The coordinator parked the line on 2026-11-10, at John's agreement to stop the easier lines while one hard direction
  is tried.

## Reading

**Interpretation, not a theorem.**
- **Why naming is unavoidable.** A local rule closes only the cycles it can see, so every face it closes, it names. A law that
  closes no cycle cannot make the plane's squares.
- **What growth adds.**
  - **Connectedness:** one world grown from one seed.
  - **No quotient:** a grown board's cycles are all closed inside views, so it never wraps around as a cylinder does.
  - **With a single growing point, one order:** the spiral's head is recognisable from its own view, with no marker needed.
  - **Not shape.**
- **For the owner's idea.** The axes can follow rules, and the board can be made of distinctions, but the rules have to say what a
  face is. That, not the drawing of places, is the input the line could not remove.
- **Nothing here is a length.**

## Lag cutoffs and census-only claims

- **Exact.** G1, G2, G2′ and G3 are proved for every radius in their statements. G2′ rests on a finite list of views, which Lemma S
  shows to be complete; the check reaches ring 40, well past the ring 20 the lemma needs.
- **Census-only.** None.

## Stress test

| Claim | One size past | Result |
| --- | --- | --- |
| G2, the spiral | 40 turns, 6,561 places | the expected block at every turn, one enabled action, the ring formula's order |
| G2′, no arrow | 40 rings at radius 2 | 77 head views and 366 others, no clash, one enabled site at every step; views repeat every three rings from ring 7 |
| G3, the slit | r = 2, 3, 4 and 6, with H = 2r + 6, all 24 priorities and the order-choosing version | the predicted heights double, and u and w share only v after further growth; the control order doubles none |

## Review

An independent referee read the proof before publication. Its first report found that none of G1 to G3 fails, but asked for
several fixes, all applied:
1. **G1 overstated dimension.** "Not of dimension two in any sense" was false, since the comb, a growing tree, has quadratic balls. It
   now says asymptotic dimension at most 1, per component, and the comb is given.
2. **G2's wording.** The cells without an inner neighbour are the first cell of each ring and three corners, not "the corners". The
   head's target cell is empty because the spiral visits each cell once.
3. **G3 needed repair.**
   - y₀ must be fixed at the end of the slit, because in a fair continuation the doubling spreads down without end.
   - "Each continues as its own sheet" was unproved and is dropped.
   - "At most three" now has its line (opposite pairs share only v, by the coordinates mod 3).
   - r = 2 doubles height 1 too, and for r ≤ 1 the law closes no square.
   - The view is read without names.
   - The frozen setting gives one action per view, so G3 now covers every fixed priority by a new order. The version that lets the
     order choose is kept as a remark.
4. **The verdict is definitional.** The frozen definition counts every cycle-closing join as naming a face, so G1 cannot fail. The
   pre-registration listed its failure as an outcome. This is said in the proof and the answer, and logged as a correction.
5. **"Only by carrying an arrow" was false.** The referee built the arrow-free spiral (radius 2, coordinates mod 3) and ran it to 30
   rings. It is now G2′, proved with Lemma S, and checked independently to 40 rings with the same counts.
6. **Like for like.** Growth with values was compared with static laws without letters. The comparison is now with the same nine
   values: static laws allow the cylinders and tori.

The referee's second look at the new parts, G2′ with Lemma S and G3 with a fixed priority, found both sound for every priority and
every r ≥ 2. It re-derived the position shifts, checked that every join in the order has one candidate, and found the constants
enough with margin. Its wording fixes are made:
- the radius-1 clashes are mostly a head going straight against a ring corner already passed;
- the metrics of the zones are named;
- the reason for r ≤ 1 covers displacements of length 2;
- the doubling of every height above is said.

It also ran the spiral without the residues: the shapes alone clash at radii 2 and 3, so the coordinates mod 3 are needed.

## Literature and provenance

- **Sources.** The square spiral; growth processes under adversarial schedules; quasi-isometry and asymptotic dimension (Gromov);
  `GROW-COIN-20261107-001`'s carried coin; `GROWTH-LAW-20261107-001`'s every-order standard; `BARE-NAMES-20261110-001A`, T4, for the
  static quotients.
- **Classification.** Elementary; folklore risk high. The arrow-free spiral is the referee's construction, proved here. The verdict
  for the board line and the like-for-like comparison are this epic's.

## Workspace assumptions

- **Relied on.** A54's setting of abstract names, through `BARE-NAMES-20261110-001`.
- **Bearing on A51.** The line closes on it: places and their neighbours need not be given before the rules, but a face must be named
  by them. Its history records the line's verdict.
- **Added.** A61, closing a cycle in a growth step names a face (a reading, Assumed). It is the frozen definition, which makes G1
  definitional; the finer reading in its challenge is the line's reopening route.

## Ratio

Since the epic opened:
- **Substantive.** Ticket A: G1 to G3, G2′ with Lemma S, and the checks.
- **Administrative.** This note, with the line's summary, the pre-registration, the review and the closure.

## Corrections

One, logged in `docs/CORRECTIONS.md` (2026-11-10, Narrowing). The pre-registration (9df96cd7f) presented the accretion route as able
to change the verdict, listing "a failure of G1" as an outcome, but its own definition made G1 hold. Its target G1 claimed more
than holds (a tree, nothing of dimension two). Its target G3 was headed "no marker", which reads as a claim about every marker-free
law, but it is about one law, and a marker-free law grows the plane (G2′). The verdict for the line stands, with the narrower
meaning given above.

## Next steps

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — every accretion law | **Status:** Successful | Growth chooses the plane only by closing cycles, which names faces by definition; with a named square it grows the plane from one seed with nine periodic values, which static laws cannot; growing everywhere at once fails |
| Local direction — the board line | Closed and parked | Its static and accretion routes are closed, by the summary above |
| Broader exploration — question 9 | Sharpened | The input no route removed is a named face; growth removes the quotients |
| Long-term goal — G1 Space from a law | Obstruction learned | A uniform local law chooses the plane only by naming a face |

**Corrections:** one, the pre-registration's decision and two of its targets (Narrowing). **Goals:** a G1 checkpoint (obstruction
learned); WEAK-APER-20261110-001#2 taken. **Assumptions:** A61 added (Assumed); A51's history records the line's verdict.

**Next step:** Full pivot — the board line closes here and is parked. Bounded next action: none in this line. Reassess only if the
finer reading of naming (A61's challenge) is taken up.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A face that emerges | 2/3 — Substantial | 1/3 — Stated | Fix a reading under which a rule names a face only when it fixes the face's length or offsets, then try a law without coordinates that closes whatever short cycles it sees → the plane in every fair order, or an order that defeats it | Alternative · not started |

1. **A face that emerges.** Payoff 2: it is the only route that could change the line's verdict. Concreteness 1: the reading of
   naming it needs is not yet fixed.

**Recommendation.** Full pivot: the line has answered its question and is parked.
