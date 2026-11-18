# Who picks two orders: the two-order line's closing summary

2026-11-18. Seven studies, run in one thread on the coordinator's picks, starting from `CUBE-DOUBLING-20261118-001`, which proved
that the cheapest growth gains one order at every doubling and never keeps two:
- `LOCAL-ROOM-20261118-001`
- `NEVER-NEST-20261118-001`
- `PICK-TWO-20261118-001`
- `KNOT-SWITCH-20261118-001`
- `KEEP-READ-20261118-001`
- `MID-RULE-20261118-001`
- `COPY-READ-20261118-001`
- `COPY-CLASS-20261118-001` (added after the summary, on the coordinator's go-ahead)
- `FAR-SIGN-20261118-001` (the last study, on the coordinator's go-ahead; refereed)

All are refereed and folded in. `MID-RULE`'s free-form runs, a check of proved statements, finished and held. The coordinator stopped the line here: it had come down to "is it local or not", with
returns shrinking on bases this small.

**Scope throughout.** Growth by A99's moves (one new distinction with one to three betweenness knots; every old state kept),
starting from a line and comparing rules for which step to take. "Two orders" means λ = 2 with a crossing graph whose crossings
split into two sides: the base sits in a grid of two chains. Prior uniform over the choices each rule allows.

## The question, in the owner's terms

Can a law grow a two-way grid forever from a line without being told the number two? If the two has to come from somewhere, where:
from a number written into the rule, from the start, or from the knots themselves? And can a rule that reads only what is next to
each step do it?

## The answer, in short

- **No rule here picks two out of nothing.**
- Told "at most d orders", a rule builds full d-way grids, whatever d is.
- Told a price on states against orders, it keeps the number the price works out to.
- Told nothing but "take one free step from the line, then never make a new crossing except by copying", it settles at exactly two.
  That is because a single new distinction has two values, so one step from a line always makes exactly two orders.
- The step where the two enters can be read in the knots: it is the first time four knots close on four distinctions.
- After one free fill, a rule taking only fills with at most one end knot never makes a third order. But free, it grows full grids
  only from a spanning first fill or the 2 × 2 pattern, and knot-local it never fills again. The step that grows the grid over the
  whole line, the copy step, is not decided by its own knots or the betweenness among its distinctions. But every copy step met
  has one shape of that betweenness, shared by under 2% of crossing-making fills: a local necessary condition.

## What is proved

| Result | Where |
| --- | --- |
| **Reach limits cannot hold two orders and fill them.** Within one split no free fill exists; within two or more the cheapest growth still makes the cube; no limit read from distances tells a grid's corner from three distinctions in a row. | `LOCAL-ROOM-20261118-001` (R1 to R3) |
| **Told the cap of two, a rule reading only the states grows full two-way grids forever.** From any line it fills the whole grid the line spans before it first lengthens, then refills every new row or column. It is given the cap "at most two orders" and its fallback step (a subdivision); uncapped, the same rule makes every order. | `NEVER-NEST-20261118-001` (N1 to N4) |
| **A cap of d gives exactly d.** From a full d-way grid, a rule capped at d refills every new layer. | `PICK-TWO-20261118-001` (S3) |
| **A price picks through its increments.** A greedy rule pricing states against orders raises at a full non-cube grid exactly when its price for one more order is below two states. A linear price either always raises or never leaves the line. | `PICK-TWO-20261118-001` (S4, S5) |
| **Conservative rules keep the start's number.** A corner completed only across two crossing splits never changes how any two splits relate, so it keeps one order on a line, two on the 2 × 2 pattern, three on a three-way start. | `PICK-TWO-20261118-001` (S2), `NEVER-NEST-20261118-001` (N5, N6) |
| **One fill on a line makes exactly two orders.** The new distinction lies inside some cuts and outside the rest; only pairs with one cut of each kind come to cross. | `PICK-TWO-20261118-001` (S6) |
| **A knot and its fill force a crossing.** Four distinctions carrying a knot and the three knots of its fill allow only two ways of splitting them, and those two cross. This holds in any presentation without copies. Along every growth here, the first fill makes the first such "filled knot" and the first crossing in the same step. | `KNOT-SWITCH-20261118-001` (W2, W3) |
| **A fill's own knots cannot tell keeping from raising.** One knot pattern, a corner, fills a grid cell or adds a third order depending only on whether the two splits it touches cross. | `KEEP-READ-20261118-001` (R1) |
| **A new crossing needs two end knots.** Each knot makes the new distinction copy an old one on the states it pins. So two different knots must pin a new crossing's two states, and neither can be a middle knot. A fill tied by at most one end knot therefore never changes the number of orders, on any base of betweenness knots. | `MID-RULE-20261118-001` (E1, E2; refereed) |
| **After one free fill, a rule taking only fills with at most one end knot never makes a third order.** Free, it grows full grids only from a spanning first fill or the 2 × 2 pattern (6 / (n (n − 1)) of lines); knot-local, it never fills again, and keeps two orders by lengthening. The one free fill is a given. | `MID-RULE-20261118-001` (E3 to E5; refereed) |

**Known results, and what this view adds.**
- *Lattice dimension* by chain covers of splits (Eppstein 2005); *Dilworth's* chain covers; *medians* in a product of chains (median
  graphs); the *Mayer–Vietoris* sequence for attaching a cone.
- What this view adds: where the number of orders comes from in a growth law (a cap, a price, the start, or the two values of one
  new distinction) and which of these a rule can read from the knots near each step.

## What is computed

- **The knot-sharing never-nest rule (B197)** grows full two-way grids in nearly every run to 40 distinctions (median fill rate
  0.80; a full grid again between 30 and 40 in 93% to 100% of runs). It is computed, not proved: 13 runs had a hole and 4 had no
  full grid by 40. (`NEVER-NEST-20261118-001`)
- **Caps and prices** behave as proved in every run, from lines of 5 to 12 and three-way starts. The number of orders equalled the
  largest set of pairwise crossing splits on every base reached. (`PICK-TWO-20261118-001`)
- **SEED** (one free fill while nothing crosses, then copy or conserve) is strong from every line of 5 to 12 and keeps three from
  three-way starts. It is equally strong with knots only on pairs that already share one, in 105 of 105 runs.
  (`PICK-TWO-20261118-001`, `KNOT-SWITCH-20261118-001`)
- **After the switch:**
  - About a fifth of the fills that keep two orders look, in their own knots and in the betweenness among their distinctions,
    exactly like fills that add a third.
  - A new distinction in the middle of two or more of its knots never added an order (2,179 cases to 40 distinctions, the
    referee's count).
  - (`KEEP-READ-20261118-001`)
- **The rule reading only the fill's knots, with knot-sharing,** starved: exactly one fill per run, then only lengthening, in 210 of
  210 runs to 60 distinctions. (`MID-RULE-20261118-001`)
- **What decides the copy step** (proved and computed). Every new crossing joins splits separating the fill's two end pairs, so
  the copy is decided on those splits and a model's crossers (proved).
  - The frozen local rule accepted no copy step, because its candidate set was always empty.
  - The "swapped" rule agreed with SEED everywhere, but trivially: it is SEED's own clause.
  - *Corrected after the referee (Block on the reading "named by the fill's own pairs"):* what decides the copy step, by the
    referee's exploratory finding, is one sign: the far end pair is separated by every crossed split. It held on 2,916 copy steps
    and none of 196,292 refused fills, and it reads every crossed split.
  - (`COPY-CLASS-20261118-001`, refereed)
- **Is that sign the copy step?** On SEEDK's own fills, exactly: 1,794 copy steps and none of 147,368 refused fills, on fresh runs
  to lines of 26 and n = 48, and the referee's 3,072 of 307,135 to lines of 42 at n = 64 (computed). As a theorem, no.
  - What the runs add is two facts. Every copy step's knot set of the treated shape has the sign, and no fill refused by clause (b)
    has that shape. L4 and L5 (proved) make them the equivalence.
  - On a seven-distinction base of two orders, a fill with the sign is refused and a copy step lacks it (proved).
  - Under the sign the copy step is one set comparison: the splits on which r leaves p's side must be one whole class. A pair pattern
    forces it.
  - The copy class's betweenness cannot read the sign, since it does not tell crossed splits from uncrossed ones. With one mark per
    split, crossed or not, the move's five distinctions read it exactly.
  - An ablation found that SEEDK's bases carry the sign's sufficiency. Its necessity failed only where the middle or near pair had no
    knot, though the data cannot separate those from the far pair's knot. In every copy step, p is a distinction of the starting line.
  - (`FAR-SIGN-20261118-001`, refereed)
- **The copy step** (pulling an uncrossed split into the grid without adding an order) is rare: 566 among about 1.8 million
  crossing-making fills, all early. No reading of its own knots or the betweenness among its distinctions decides it. But all of
  them fall in one closure class, which holds under 2% of crossing-making fills (the referee's count: 528 of 528, lift 57).
  (`COPY-READ-20261118-001`)

## What the referees narrowed

All logged in `docs/CORRECTIONS.md` with knotlab's `HISTORY.md`:
- `LOCAL-ROOM-20261118-001`: "two orders need memory" became "two orders need more than a reach limit" (Narrowing). The class law's
  classes nearly build the two orders in.
- `NEVER-NEST-20261118-001`: what the rule is given is the cap of two and the subdivision fallback, and the two is wholly the cap's
  (Narrowing). The corner rule "reads two splits", and is not strictly local (Not a block).
- `PICK-TWO-20261118-001`: SEED is given one order-making step, not a number. Arity makes the step one order, and the line has the
  first (Narrowing). From a branching tree one fill can give three. Three small fixes in the proof (Not a block).
- `KNOT-SWITCH-20261118-001`: the filled-knot reading of the switch holds both ways only along these growths. In general a filled
  knot forces a crossing, but a crossing seldom brings one: 2,772 of 2,776 random presentations with a crossing have none
  (Narrowing).
- `KEEP-READ-20261118-001`: "no local reading" narrowed to the fill's own knots and the betweenness among its distinctions. On bases
  of 24, one step out is most of the base and could not be tested (Narrowing).
- `COPY-READ-20261118-001`: "no sign" became "no exact reading, but one closure class holding every copy step and under 2% of
  crossing-making fills" (Narrowing).
- `COPY-CLASS-20261118-001`: **Block on a reading.** "The copy step is named by the fill's own pairs" withdrawn, along with its G1
  capability. The agreement was SEED's own clause restated. The referee's sign (the far end pair separated by every crossed split)
  decides the step and reads every crossed split.
- `FAR-SIGN-20261118-001`: four narrowings of wording, no Block. The eight predictions are two computed facts stated several ways.
  "Two orders" in L5 became "two classes". The ablation does not show which pairs' knots carry necessity. Every copy step's p lies on
  the starting line, so the untested region is never reached.
- `MID-RULE-20261118-001`: "keeps two orders, told no number, reading only the fill's knots" scoped. Knot-local it never fills again,
  free it grows full grids only from a spanning first fill or 2 × 2, and the free fill is a given (Narrowing). "Any base" means any
  base of betweenness knots (Not a block).

## What is open

| Direction | Payoff | Concreteness | Where to start |
| --- | --- | --- | --- |
| **The witness radius.** For each copy step, how many knot-steps away the split it copies sits, on larger grids. A local copy rule exists only if this stays bounded. | 2/3 | 3/3 | `COPY-READ-20261118-001`'s engine on bases grown by NNF from long lines |
| **Who picks two, with no switch at all.** Every rule here that settles at two is told something: a cap, a price, or one free step. Is there a law whose own knots end the free phase, so that it never needs to be told? | 3/3 | 1/3 | `KNOT-SWITCH-20261118-001` (the filled knot), `PICK-TWO-20261118-001` (S6) |
| **A first fill that spans the line, read from the states.** With it, the local rule (at most one end knot) would grow full grids from every line. | 2/3 | 3/3 | `MID-RULE-20261118-001` (E5) |
| **Proofs of the computed parts.** The knot-sharing never-nest rule's growth, and its 13 holes; why λ equals the largest set of pairwise crossing splits on grown bases. | 2/3 | 2/3 | `NEVER-NEST-20261118-001`, `PICK-TWO-20261118-001` |
| **The copy predicate.** The advisor's "the end pair shares a knot with an active split's ends", fixed on some runs and scored on others. | 2/3 | 3/3 | `COPY-READ-20261118-001` |

One direction rates 3/3 for payoff: a law that never needs to be told. It is 1/3 concrete, so it is filed for the coordinator, not
started.

## What the line says about A101 and G1

A101, "the number of orders a growth rule keeps is given: two", is under challenge, and the line locates the two. A cap writes it in;
a price writes it in through its increments; a conservative rule copies the start's. The one route that names no number goes
through the move itself: a new distinction has two values, so one free step from a line makes exactly two orders. In the knots, that
step is the first knot and its fill closing on four distinctions. What is still handed over is how many free steps to take, one. For
G1 this is real progress: a law that grows two orders forever from a line, read from the states, exists (proved), and the second
order's entry is a knot event. But the copy step that grows the grid over the whole line reads the crossings of the whole base, and
no study here found it near the step.

## Records

Decision notes:
- [LOCAL-ROOM](../LOCAL-ROOM-20261118-001/local_room.md)
- [NEVER-NEST](../NEVER-NEST-20261118-001/never_nest.md)
- [PICK-TWO](../PICK-TWO-20261118-001/pick_two.md)
- [KNOT-SWITCH](../KNOT-SWITCH-20261118-001/knot_switch.md)
- [KEEP-READ](../KEEP-READ-20261118-001/keep_read.md)
- [MID-RULE](../MID-RULE-20261118-001/mid_rule.md)
- [COPY-READ](copy_read.md)

The advisor model (Fable 5.2) was consulted before every freeze but COPY-READ's, where it came after the freeze and before the
read-out (a lapse). It corrected a claim before the freeze twice: KNOT-SWITCH's first homology claim and MID-RULE's lemma, which it
turned into the end-knot theorem. Each refereed study has its report in its `referee-R1/` directory.
