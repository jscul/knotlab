# Which cyclic sequences to fix

Epic `WHICH-SEQUENCES-20261112-001` (backlog B161, G15 with G16; program learning), 2026-11-12, at the coordinator's go-ahead.
Pre-registered in [preregistration.md](preregistration.md), frozen in commit `0954c916d` before the census. The design was checked cold with
the advisor model before freezing. Proof family: `proofs/WHICH-SEQUENCES-20261112-001A/`.

## The answer

**No rule of this kind, the same on every base, keeps a counting law at rest across bases: the knots alone do not choose where to look.**

- **The census (exact).** One copy of (2, 0, 4) and the first 12 undrawn bases of a frozen search; 16 rules fixing or equalizing the law's
  sums around its cyclic sequences of two or three knots. None passes on all 13 bases. The best, "all sums equal on sequences of two knots",
  holds the count on 2 (one copy, and the 6-distinction base U) and leaves no counting law at rest on the other 11. Every rule on sequences of
  three knots passes nowhere.
- **No chance pass.** With random laws as targets, no rule passed on all 13 in 1,000 draws, so the negative is not a matter of too many
  rules.
- **Symmetry, where there is any (exact).** On the two undrawn bases with symmetries, the counting law is fixed by them, which only 0.1% and
  3% of all laws are: resting at the laws a base's symmetries fix would hold the count far more densely than chance there. On the copy, whose
  symmetries move the interface, no counting law is fixed by them. And 10 of the 12 undrawn bases have no symmetry at all, so the rule would
  restrict nothing.

## What is known, and what is proved and computed

| Claim | Evidence class |
| --- | --- |
| Laws up to gauge are their sums around cyclic sequences; rules of this kind give affine rest sets | known (cycle space; the advisor's point, checked by the law counts) |
| No rule of 16 by length holds a counting law at rest on all 13 bases; the best on 2 | exhaustive |
| No rule passes on all 13 with random target laws (1,000 draws) | computed (seed 0) |
| The counting law is fixed by the symmetries on 2 of the 3 bases that have any; on the copy none is | exhaustive |

## Against the pre-registration

R0, as predicted. The orbit test was empty on 10 of 12 undrawn bases (no symmetry), which the pre-registration did not anticipate; on the
three bases with symmetry, counting laws were more often orbit-fixed than chance on two, against my prediction, and less on one.

## What it changes

- **The rest set cannot be chosen by sequence length.** Since the learner's search is blind (`SEARCH-AUDIT-20261112-001`), the cost of
  finding a count is laws at rest per counting law, and no target-blind rule of this family lowers it across bases. The cheaper path to
  learning is now a learner whose examples steer it (sub-goal B165), not a better rest set.
- **Symmetry is the one native handle found,** and only on bases whose symmetries keep the interface's place (B166).

## Assumptions

None added or changed. Relied on: A20, A21, A46, A47, A49, A50, A52, A58.

## Corrections

None.

## In the owner's words

Asking the knots to fix the sums around their own short cyclic sequences, one rule for every pattern, never keeps the counting rule in view across patterns: what
works on one pattern hides the count on the next. Only symmetry helps, and only on the few patterns that have it.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: which cyclic sequences to fix (B161) | **Status:** Successful | decided exactly: no rule by length serves the 13 bases; no chance pass |
| Local direction: native rest sets from the law's sums | Retire | none holds the count across bases |
| Broader exploration: learning program | Known alternatives | a learner whose examples steer (B165), rest at symmetric laws (B166), two histories (B159) |
| Long-term goal: G15 Learning: a point in a learned knot pattern | Obstruction learned | finding cannot be made cheap by a target-blind rest set of this kind |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A learner whose examples steer its search (B165) | 3/3 — Major | 2/3 — Testable | the advisor's three steering rules, frozen, on one copy and on undrawn bases with 32 and 64 laws at rest, 500 seeds each, against the exact blind median, with a target-swap control → a median at most half the blind median, or no rule beats blind search | Selected · awaiting go-ahead |
| 2 | Rest at the laws the base's symmetries fix (B166) | 2/3 — Substantial | 3/3 — Ready | on the bases with symmetries that keep the interface's place, the blind cost at rest against all laws, then the learner there → cheaper finding, or none | Alternative · deferred |
| 3 | Two histories (B159) | 2/3 — Substantial | 2/3 — Testable | as recorded | Alternative · deferred |

- **#1:** payoff 3/3, it is what would make the line's learning real; concreteness 2/3, three rules and a test are drafted, none coded.
  Awaiting a go-ahead: the coordinator asked to be told before it starts.
- **#2:** payoff 2/3, a native rest set on symmetric bases only; concreteness 3/3, the orbits are computed.

**Corrections:** none.
**Goals:** G15 checkpoint (obstruction learned, with G16); B161 taken; B166 added.
**Assumptions:** none new or changed.
**Basket:** B165 (selected, awaiting a go-ahead), B166, B159, B162, B157, B154, B155, B156, B150, B151, B130.
