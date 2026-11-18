# What holds the top: the addressed line's second closing summary

2026-11-18. This continues the [first closing summary](../MARK-RATE-20261116-001/line_summary.md) of the addressed-pattern line. John
reopened the line on 2026-11-17 ("let's see if we can uncover anything here"), and five studies followed:
`KEEP-REACH-20261117-001`, `CARRIER-20261117-001`, `TWO-ENDS-20261117-001`, `MODE-BOND-20261117-001` and `DECIDE-SMALL-20261117-001`.
The coordinator wrapped the line up after the last of them. All but `DECIDE-SMALL-20261117-001` are refereed and folded in;
its referee confirmed `DECIDE-SMALL-20261117-001` with fixes (2026-11-18), folded in here.

**Counting.** Counts are of distinct patterns: clause sets at a fixed depth, after CARRIER's referee found that many descriptions give
the same pattern. Where a count of descriptions is given, it is marked as such.

## The question

The first summary left two things open where the maps' orbits stay small (at most four addresses):
- whether "never forgets" is the same as "bounded";
- what holds the top to every depth when the reach is bounded.

Asked in the program's words: when a strand pair's relation never untangles, does it hold the top, and is that the only way?

## What is proved

| Result | Where |
| --- | --- |
| **Theorem K.** A bond inside two orbits, one at the top level and one s levels down, that survives at every s and depth bounds the reach. | `KEEP-REACH-20261117-001` |
| **Theorem F′.** Forgetting read on the values states take, from the top level down, forces growth. | `KEEP-REACH-20261117-001` |
| **Lemma E.** An exposed dependence between two orbits gives a bond inside them. | `KEEP-REACH-20261117-001` |
| **Theorem K\* and Lemma P.** A bond inside any exactly projected piece bounds the reach. An orbit with the lower orbit's block, and a stem (the top orbit with the lower orbit's next ancestors) with the lower orbit, project exactly. | `CARRIER-20261117-001` |
| **Conjecture C′ is false.** Five patterns keep the reach bounded at 5 with no two-orbit bond from the top. | `CARRIER-20261117-001` |
| **Theorem N (three ends).** A bond of bounded size can be moved, keeping its size and its two levels, until every member lies near the top, near the far member, or near the bottom few levels. Step 3 was repaired for clusters after the referee and has not been re-refereed. | `TWO-ENDS-20261117-001` |
| **Theorem D (no slow growth).** On each depth tier and residue of s, the reach is eventually constant or grows at least linearly. | `TWO-ENDS-20261117-001` |
| **Theorem G.** If every long composite of block steps is a product, the reach grows linearly. **Lemma J and Theorem G on a component:** a bond lies in one component, so the test can be read on the top's component alone. | `TWO-ENDS-20261117-001`, `MODE-BOND-20261117-001` |
| **The 13 mutants grow.** 5 patterns grow linearly, proved from the block types: the one link they carry lies in subtrees that no knot ties to the top. | `MODE-BOND-20261117-001` |

**Known results, and what this view adds.**
- *Pumping finite semigroup states along words.* Theorems N and D pump finite semigroup states along words, as for regular languages
  and tree automata (Thatcher and Wright; Doner), and as `READ-RULE-20261114-001` did for nested families. What this view adds is
  where the pumping must stop. At finite depth the bottom levels are read differently, so they form a third end, and the normal form
  says that what holds the top sits at the ends, never spread along the way.
- *Splitting along components.* Lemma J is the folklore fact that constraint satisfaction splits along components. What this view
  adds is that a never-forgetting strand can sit beside the top and still be irrelevant to it. KEEP-REACH's deep pair projections that
  "never become products" were such strands.

## What is computed

- **The census.** The 786 small-orbit descriptions alive at every depth (181 patterns): forgetting decides all of them (139 forget: 123 grow, and 16 have no bond across the ends at all), and
  the product test on the top's component agrees with forgetting on every one.
- **KEEP-REACH's fresh and mutated population.** 2,380 descriptions (583 patterns), all decided:
  - 229 patterns grow by forgetting, and 15 more pass it with no bond across the ends;
  - 323 are bounded by a two-orbit bond;
  - 6 grow by forgetting on actual values;
  - 5 are bounded by orbit-and-block or stem bonds;
  - 5 grow by the product test on the top's component.
- **A fresh sample ten times larger** (seed `DECIDE-1117`, KEEP-REACH's fair-coin weighting). 10,160 draws give 627 patterns, 476 of them
  new, and all are decided:
  - 408 grow by forgetting, and 44 more pass it with no bond across the ends;
  - 172 by two-orbit bonds;
  - 2 by block or stem bonds;
  - 1 by forgetting on actual values.

  167 certified readings of L₉ on 50 of them fit their verdicts.
- **Exact readings.** The pattern of 8db5da810c00-73 reads exactly 6 at s = 5, 6 (depth 11) and exactly 7 at s = 7, 8 (depth 12),
  certified by LRAT. The proved rate is one member per ten levels; the readings suggest one per two.
- **Growing orbits.** The census's 441 growing-orbit patterns, read through level 3's component at depth 12:
  - in 359 it covers half a level or more;
  - in 75 it never reaches below level 3 (no bond at all);
  - in 7 it is thin.

## What it means (interpretation)

On small orbits the top is held to every depth exactly when a bond between two bounded pieces, one at the top and one at the far
level, survives at every distance. In every pattern seen, that is a two-orbit bond, an orbit with the far orbit's block, or a stem.
Otherwise some strand between the ends forgets, and each stretch then costs a member: the reach grows, at least linearly. Or nothing
joins the ends at all, and there is no bond (the census's "no bond" class). Two
corrections shaped this reading:
- **a dependence can hide** inside two orbits, and a little more of either strand exposes it;
- **a strand that never forgets can sit beside the top** without touching it.

Holding the top is a bond between the two ends' pieces. It is never something spread along the way, and on small orbits it needs
no third end in any pattern seen.

## What is open

| # | Open item | Payoff | Concreteness | Backlog |
| --- | --- | --- | --- | --- |
| 1 | A decision procedure for bounded reach on small orbits: the summary automaton decides "L ≤ c" for each c, and totality needs regular cost functions (Colcombet and Löding) through evidence admission, or a long proof | 3/3 | 2/3 | B196 (sub-goal) |
| 2 | Exact growth rates on small orbits (one member per two levels read against one per ten proved) | 2/3 | 2/3 | B186 |
| 3 | Lower bounds where orbits grow: level 3's component covers half a level or more in 359 of 441 patterns; no finite interface yet | 2/3 | 1/3 | B188 |
| 4 | Two ends or three: a pattern whose bounded reach needs the bottom band (none among the small-orbit patterns) | 2/3 | 2/3 | `TWO-ENDS-20261117-001`#2 |
| 5 | Ties in nearly rigid patterns with growing orbits | 1/3 | 2/3 | B189 |
| 6 | The undecided bounded-activity descriptions | 1/3 | 1/3 | B190 |

## Lessons

These are kept in `docs/CORRECTIONS.md`:
- Count distinct patterns, not keys. A mutation that swaps a word for one acting the same changes nothing.
- Give each reading with its depth. Join readings into one sequence only where the quantity is shown to be monotone.
- In an induction that moves nodes of a tree, check two neighbours that block each other.
- Copy a summary's qualifiers from the theorem it summarises.
- Read a relation's missing pairs from both sides before naming what it carries.
- Check that a carrier shares a component with the end before reading it as a route.
