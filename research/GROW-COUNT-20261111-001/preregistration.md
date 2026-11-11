# The count from growth: pre-registration

Epic `GROW-COUNT-20261111-001` (RULER-20261111-001 direction 2; G1, question 9; the challenge of A64), 2026-11-11, at the owner's
go-ahead. Frozen before any registered run. The canonical K1–K3 test is unchanged.

## The question

A world of three-place knots alone is read faithfully by the not-all-equal law (NAE) on long-loop flat worlds, and NAE then measures
it exactly (`LONG-LOOP-20261111-001`, `RULER-20261111-001`). But the count of how knots meet, each co-knotted pair in two knots, each
link one cycle, six knots per distinction, was put in, and a static faithful reading does not supply it (`NAE-SURFACE-20261111-001`).
Can growth supply it? A world grows from one knot by adding knots, each accepted only while NAE still reads the world faithfully.

## The growth rules (frozen)

A move proposes a knot {x, y, z} on a co-knotted pair {x, y}, z an existing distinction (with probability b, the closing bias) or a new
one; it is kept if it passes the rule and NAE still reads the world faithfully (no frozen distinction, no tie, three-place bonds
exactly the knots; KNOTS-ALONE's frozen `read_law_sat`, hash checked). A run stops at 80 knots or after 400 rejected proposals in a row.

| Rule | Names, by definition | Leaves to the law |
| --- | --- | --- |
| free | nothing | two per pair, one link, the degree |
| open | at most two knots per pair (proposals only on pairs in one knot) | one link, the degree |
| disc | that, and every link a single path or cycle | the degree |

No rule names a degree. Each rule runs at b = 0.3, 0.6, 0.9 with seeds 0 to 9, under NAE and, as the frozen comparison, under the
clause law (OR), which reads every world faithfully and so accepts every legal move (KNOTS-ALONE's D4): 180 runs. What OR grows is
what the proposal order alone produces; what NAE adds is the law's part.

## Settled by definition, said up front (the GROW-FACE lesson)

- Under **open** and **disc** the pair count "at most two" is the rule's, not the law's: they cannot test it. Under **disc** the
  single link is the rule's too. Only **free** tests the pair count and **open** the link; **disc** tests only the degree.
- No outcome is settled: each prediction below fails if NAE's faithfulness rejects the moves in question, which it is free to do.

## Predictions (frozen)

- **P1.** Under free, every NAE run has a pair in three or more knots: the law does not supply "two per pair". *Fails* if some run
  has none.
- **P2.** Under open, some NAE run has a pinched link: the law does not supply "one link". *Fails* if none does.
- **P3.** Under disc, the closed distinctions of the NAE runs take at least three different degrees, and in no run is degree 6 at
  least 90% of them: the law does not supply the degree. *Fails* otherwise.
- **P4.** No disc NAE run closes into a flat closed surface. *Fails* if one does.
- **P5** (suggested by the pilot, below). Under disc, NAE rejects every proposal that would close a link at degree 3. *Fails* if it
  accepts one.

## Decision rules

- **P1 to P3 hold.** Faithful growth does not supply the count: each part must be put in, as A64 reads it. The line closes for
  growth by faithfulness; what NAE does reject (P5's degree 3, or others) is reported as the law's only part.
- **P3 fails** (degree 6 at least 90% in some run, or fewer than three degrees). NAE's faithfulness chooses flatness once the pair
  count and the link are given: the degree would come from the law. A finding to be stress-tested before it is read.
- **P1 or P2 fails.** That part of the count comes from the law under faithful growth.

## Disclosed before freezing

- Controls ran the whole pipeline: under OR (accepting every legal move) and as a pilot under both laws with seeds 98 and 99, outside
  the registered seeds, for every rule at b = 0.6. In the pilot NAE rejected moves under every rule, and under disc all five of its
  rejected closings would have closed a link at degree 3; its disc runs closed distinctions of degrees 4, 5, 6 and 7. P5 is registered
  because of that pilot. No registered run was made.
- The coverage check (every registered run ran) reports false in control mode, so it can fail.
- Expected runtime: about a quarter of an hour on 12 workers; registered in `docs/LONG_RUNNING.md`, run under
  `systemd-run --user -p MemoryMax=16G -p MemorySwapMax=0`.

## Stop rule

One run on the frozen design; no second epic in this line without a new route named first. Report and hold for a go-ahead.
