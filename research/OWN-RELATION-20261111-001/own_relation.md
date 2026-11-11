# Does a knot space read its own relation?

Epic `OWN-RELATION-20261111-001` (direction #1 of `HOLD-COUNT-20261111-001`, G8 with G15; program mathematics), 2026-11-11, at the
coordinator's go-ahead. Pre-registered in [preregistration.md](preregistration.md), frozen in commit `bce78f40c` before the census ran.
Proof family: `proofs/OWN-RELATION-20261111-001A/`.

Words, after the owner's rule of 2026-11-11 that spatial words are not literal yet: a knot world here is a set of distinctions in which
every distinction lies in three knots and every knot (a not-all-equal relation) joins three distinctions. Its loop count is the number
of independent loops of distinctions that no patch of knots fills; the literature calls half of it the genus of the drawn surface.

## The question

To count held distinctions in threes, a knot world with one fixed value would need a distinction that reads one of two maps of four
held distinctions: a ⊕ NAE(b, c, d), the knot's own relation read against a fourth distinction, or a switch between the parity and the
majority of three. `HOLD-COUNT-20261111-001` found neither on 1,128 worlds of up to 20 distinctions, only the two other kinds of map
that use four held distinctions. Is that a property of the knot law, or of small worlds?

## The answer

**No knot world in range reads its own relation, and the reason is not the law alone.**

- **Not forced (proved).** All four kinds are self-dual, so theorem D allows them; not-all-equal with hidden distinctions builds every
  relation closed under flipping every value, so knot systems without the world structure (three knots per distinction, the drawn
  surface, the Kasteleyn law) realise both missing kinds.
- **Not found (exact, frozen, refereed).** 453 random knot worlds of 16, 18 and 20 distinctions with 4, 6 or 8 unfilled loops, every
  class, 179.6 million free sets of four held distinctions: 4,303 readings of the weighted majority, 33 of maj(a, b, a ⊕ c ⊕ d), none of
  the switch or of a ⊕ NAE. With `HOLD-COUNT-20261111-001`, no world of up to 20 distinctions in 1,581 does it.
- **Readings thin out (exact; P2 failed).** I predicted the rare kind would grow with size; instead every four-point reading gets
  rarer past 16 distinctions (the weighted majority: 1,859 readings on 100 worlds of 16 distinctions with 8 loops, 26 on 77 worlds of
  20). Larger random worlds leave held distinctions too much freedom to force anything, so a bigger random census would not settle it.
- **The proof attempt: not found.** As majorities of parities, the kinds seen take at most one parity input, and a ⊕ NAE needs two
  (maj(a, a ⊕ b ⊕ c, a ⊕ b ⊕ d)). That is a conjecture, not a result. The route most likely to prove a bound is the Pfaffian
  (matchgate) form of floor-state counts with held distinctions.

## What is proved and what is computed

| Claim | Evidence class |
| --- | --- |
| Four kinds of self-dual map use four held distinctions; only two can count in threes | proved by exhaustion; recomputed by fresh code |
| Neither is forced away by the law: general not-all-equal systems realise both | proved (Schaefer's construction) |
| No world of 16 to 20 distinctions in the census reads either | exact census of 453 worlds; positive control passed; refereed on 46 |
| Four-point readings get rarer past 16 distinctions | exact census |
| Readings take at most one parity input | conjecture, read from the census |

## Against the pre-registration

- P1 held (none of either kind). **P2 failed:** the rare kind did not grow with size. No world was dropped; the census was not
  inconclusive. The referee was run through `referee_parallel.py`, which calls the frozen referee's functions unchanged in parallel,
  because the serial run would have taken about two hours.
- 447 of the 900 jobs never reached their loop count in the steering walk (with 4 loops: all 100 at 20 distinctions and 98 of 100 at 18),
  as in `PARITY-NEEDS-20261111-001`; they are counted, not read.

## What it changes

- **For the owner's knapsack question.** Counting in twos is native and counting in threes is not, in any knot world this census
  reaches, even with a fixed value supplied: no distinction reads whether three others are not all equal against a fourth. Whether a
  larger or composed world can is open.
- **For the program.** The decided readings of held distinctions look like a small clone: majorities with at most one parity input.
  If that is a theorem, the knot law's own arithmetic is binary at every size.

## Assumptions

None added or changed. Relied on: A47, A58. A65 not used (no reference held).

## Corrections

None.

## In the owner's words

A knot world can hold a count in twos, as binary digits. To hold one in threes it would need a distinction that tells whether three
others are not all equal, which is the knot's own relation, read against a fourth. Nothing in the rules forbids it, but none of the
1,581 small worlds tried does it, and bigger random worlds force less, not more.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — does a knot world read its own relation? | **Status:** Partially successful | none in 453 worlds of 16 to 20; proof not found |
| Local direction — four-point readings in random worlds | Practically exhausted | readings thin out past 16 distinctions |
| Broader exploration — arithmetic and learning lines | Known alternatives | targeted search, a matchgate bound, composing counters |
| Long-term goal — G8 From spacing to arithmetic and sets | Obstruction learned | counting in threes not reached in one small world |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A targeted search for a ⊕ NAE | 2/3 — Substantial | 2/3 — Testable | local search over knot incidences of 12 to 16 distinctions scoring agreement with a ⊕ NAE → a world that reads it, or the best score plateaus below it | Selected · awaiting go-ahead |
| 2 | A bound from the Pfaffian form | 2/3 — Substantial | 1/3 — Stated | write a held-distinction count as a sum of Pfaffian signatures at one handle → which four-point maps one or two handles can read | Alternative · deferred |
| 3 | Binary counters from composed worlds (sub-goal B148) | 3/3 — Major | 2/3 — Testable | as filed in the learning line | Alternative · awaiting go-ahead |
| 4 | Totals carried as phases in signed laws | 2/3 — Substantial | 1/3 — Stated | a signed law whose phase counts mod 3 | Alternative · deferred |

- **#1** is the cheapest honest discriminator left: random worlds thin out, but a search that rewards worlds for coming closer to the
  map may reach it or show a plateau. A yes would refute the conjecture; a plateau would not prove it. A few hours of compute.
- **#2** would make the conjecture a theorem at low handle counts; no method is in hand yet.
- **#3** is the paused learning line's step, the owner's call; composition is the other way a world could read a ⊕ NAE.
- **#4** waits on the interference reading the owner has not decided.

**Corrections:** none. **Goals:** G8 checkpoint (obstruction learned; no goal change). **Assumptions:** none new or changed.
**Basket:** #1 and #2 recorded; B148 unchanged.
