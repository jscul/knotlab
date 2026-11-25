# The least record: what stands

Epic `LEAST-RECORD-20261124-001` (sub-goal B325 after its first step; goals G5 with G18), closed 2026-11-25, on the owner's
go-ahead of 24 November. One frozen study, computed, scientific referee pending.
[Ticket A: result](../LEAST-RECORD-20261124-001A/results.md) ·
[pre-registration](../LEAST-RECORD-20261124-001A/preregistration.md) · [referee hand-off](referee_handoff.md) ·
[advisor review before the freeze](advisor/README.md) · [the thread's check](checks/thread_checks.txt)

## The answer

The parents of a knot cannot be found from what is built alone. The question was how little has to be written for them to
be found.

1. **One of three values on each knot is enough.** A new knot writes its generation counted in threes: one step on from
   its parents' value. The other holder of a shared place is then a parent exactly when its value is one less. This gave
   every place of every structure reached, half-built ones included, under all four laws, looking one holder step.
2. **Why it works.** Wherever the knots that join were made together, every birth's parents are the same number of births
   from the start, so a child is exactly one further on than each parent. The advisor gave a proof sketch with one leak; no
   exception was found in 34,243 births outside that leak.
3. **Where it fails.** On the one start built so that a start knot waits while the knots it meets act, a later join has
   parents a generation apart. Counting in fives works there.
4. **Two values, as tried, are not enough.** None of five two-valued stamps works under every law. The smallest failures
   have two or three knots, or are the finished structure of 16 knots.
5. **Under holding it still worked** on the sixteen runs tried, against the advisor's expectation.

Nine predictions and four checks of the code were frozen. Eight predictions and the checks hold or are reported; one
fails, the lean about holding.

## What it is and is not

The stamp is written by hand, by a rule a new knot can follow from its parents' stamps alone. It is the order of descent
cut down to three values. So the result measures the size of the record that the one-birth-at-a-time laws need, and does
not show that the growth can supply it or do without it.

## Scaffolds, and what survived their swaps

| Scaffold | Swapped for | Survived? |
| --- | --- | --- |
| The stamp | ten stamps, from two values to the full generation | The three-valued generation and the full generation work everywhere the condition holds; the rest do not. |
| The laws that built the structures | four laws, and four more with holding | The three-valued stamp works under each. |
| The start | twenty starts and laws | One start breaks it, by design; five values repair it there. |
| Who writes the stamp | not swapped | Supplied. |

## Assumptions relied on

A242 (every birth writes its parents), which this bears on directly, and one entry added here for the stamp.

## Limits

Finite and computed on the structures of the earlier search and sixteen runs under holding. That parents have equal
generations is argued, not proved. A guard run with the stamp in place of the record was not run; that it would decide the
same follows by construction from the parents being recovered exactly.

## Final report as sent (2026-11-25 01:02 UTC)

The least-record study has reached its stop and is closed, referee pending. **Three values are enough. If every new knot writes one of three values, one step on from its parents' value, any knot can tell its parents from its children by comparing values with the knots it meets.**

- **It works at one step, everywhere tried.** The rule is: the other holder of a shared place is a parent exactly when its value is one less, counting in threes. It gave every place of every structure reached, half-built ones included, under all four laws.
- **Why.** Wherever the knots that join were made together, every parent of a birth is the same number of births from the start, so a child is exactly one further on. No exception turned up in 34,243 births.
- **Where it fails.** On the one start built so that a start knot waits while the knots it meets act, a later knot has parents a generation apart, and the rule reads one of its places backwards. Counting in fives works there.
- **Two values, as tried, are not enough.** None of the five two-valued stamps works under every law. With "has made a birth", a start knot and a new offshoot hanging off the same knot look exactly alike. With the generation counted in twos, the finished structure of 16 knots defeats it.
- **The number of a knot's parents** is enough at two steps under two of the laws on finished rounds, but not on half-built structures.
- **Under holding it still worked** on the sixteen runs tried. The advisor had expected it not to.

What the stamp is: the order of descent cut down to three values, written by hand. A new knot can write it knowing only its parents' stamps. So this says how small the record can be, not that the growth supplies it or can do without it.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — ten stamps added to the search for look-alike places | **Status:** Successful | The stop is met: a stamp of fewest values that recovers the parents is named with its rule, and each smaller one has its failure written out. |
| Local direction — the record that births made one at a time need | Continue | The record is now three values per knot; whether the structure can hold those values itself is open. |
| Broader exploration — growth laws compared | Known alternatives | The copier study is at its first two steps; its laws look at this same order of descent. |
| Long-term goal — G5 Dynamics, with G18 Comparing growth laws | Capability gained | The before and after that these laws need is a count of three values handed from parent to child, with the one start where it breaks identified. |

One prediction failed: the lean that holding would give parents of unequal generations. One of my two safeguards against small-structure artifacts turned out to be redundant by a slip in the design; the other did its job.

**Next step:** Research directions — selected: #1.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The copier (your lead B327) | 3/3 — the first made pattern that does something to another | 2/3 — its claim is being stated | Its first two steps → its stop as you set it | Selected · started |
| 2 | The count held by the structure itself: three values of descent carried by distinctions, not written beside them | 3/3 — would make your "time as a pattern" a made thing in these laws | 1/3 — no construction known | Ask what a knot could hold that is one step on from what its parents hold → stop at a law that carries it, or a reason a knot's own places cannot | Alternative · deferred |
| 3 | The one-birth-at-a-time guard run with only the three-valued stamp | 2/3 — confirms by a run what now follows by construction | 3/3 — both programs exist | Replace the record by the stamp in the guard and rerun its comparison → stop at a match in every order searched, or the first mismatch | Alternative · deferred |
| 4 | A two-valued stamp read over a longer distance | 2/3 — would settle whether one bit per knot can do | 1/3 — the advisor's sketch did not hold together | Search two-valued words by generation modulo small numbers → stop at one that works, or none up to a stated size | Alternative · deferred |

1. Already running at your instruction.
2. I have filed it as a sub-goal, B328, since it is rated 3/3 and not taken.
3. Cheap, and it would close the loop with the study that needed the record.
4. The least certain of the four.

**STOP on this objective.** Its stop is met; no successor on the same question is started.

**Corrections:** none.
**Goals:** one checkpoint row (G5, G18: capability gained); no goal changed. One sub-goal added: B328, a count of descent held by the structure itself. B325 has a note with this result.
**Assumptions:** one new entry, Assumed, a scaffold: A247 (each knot carries a stamp written at its birth). A history line on A242: three values per knot can stand in for the full record wherever the knots that join were made together. Still uncommitted in the tracker.
**Scaffolds:** ten stamps were tried; the three-valued one survives the swap of law, of start (but for the one built to break it) and of release for holding. Who writes the stamp was not swapped: it is supplied.
**Basket:** direction #1 already taken; B328 (3/3, 1/3), direction #3 (2/3, 3/3) and #4 (2/3, 1/3) deferred.
