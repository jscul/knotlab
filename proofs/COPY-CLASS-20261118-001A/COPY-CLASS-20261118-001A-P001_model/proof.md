# The copy step is decided on the end pairs' splits and one model's crossers

Status: Proved

Ticket `COPY-CLASS-20261118-001A`, 18 November 2026, by Claude. Epic `COPY-CLASS-20261118-001`. Written before the run.

## Words

As in `MID-RULE-20261118-001A` and `COPY-READ-20261118-001A`. For a crossing-making fill with certificate knots, its **end pairs**
are the old pairs of its end knots, and its **middle pair** the old pair of its middle knot. SEED's second phase accepts a fill
when two clauses hold:
- (a) it makes no new crossing between two splits that already crossed something;
- (b) every split that crossed nothing and gains crossings ends with exactly the crossers of a split that already crossed something,
  its **model**.

## Statements

- **C1. New crossings join the two end pairs' splits.** Every new crossing a fill makes joins a split separating one of its end
  pairs to a split separating another.
- **C2. SEED's verdict is read on those splits and a model's crossers.** Clause (a) is decided on the splits separating the end
  pairs. Clause (b) is decided by those splits and, for each split gaining crossings, the crosser set of some crossed split.
- **C3. In a full two-way grid a model's crossers are a whole order.** There, every split crosses every split of the other chain
  and none of its own. So a split absorbed by copying a model gains every split of the other order. A rule that checks the copy
  exactly must see one whole order of the grid, not a bounded part of it.

## Proofs

**C1.**
- By `MID-RULE-20261118-001A`, E1, the two states realising a new crossing are pinned by two different end knots.
- An end knot B(x, y, r) pins only the states where x ≠ y, that is the two states of each split separating x from y.
- So one of the two newly crossing splits separates one end pair, and the other separates the other end pair. ∎

**C2.**
- *Clause (a).* It concerns only new crossings, which C1 places among those splits, together with whether each split already
  crossed something.
- *Clause (b).* The splits that gain crossings are among those splits (C1). Their crossers after the fill are their new crossers,
  which also lie among those splits.
- *The model.* The comparison needs the crosser set of a crossed split. ∎

**C3.** A full two-way grid's crossing graph is complete bipartite on its two chains (`NEVER-NEST-20261118-001A`, N3). A split's
crossers are therefore the whole other chain, and a split copying them crosses the whole other order. ∎

## What this leaves to the computation

Whether the model can always be found among the splits of the end pair that shares a distinction with the middle pair (the
advisor's reading of the copy class), so that a rule naming only the move's own pairs decides SEED's verdict exactly.

## Provenance

Local; builds on `MID-RULE-20261118-001A` (E1), `COPY-READ-20261118-001` and `NEVER-NEST-20261118-001A`. The advisor, consulted before
the freeze, proposed the roles of the three knots (tail, crossers, model), the classifier scoring and the refusal breakdown, and
advised cutting the knot-radius tiers as vacuous.
