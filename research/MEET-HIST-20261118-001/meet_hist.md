# Can the order of growth be read from a grown base without names?

Epic `MEET-HIST-20261118-001`, 18 November 2026, by Claude, on the coordinator's go-ahead. It takes `MEET-DIST-20261118-001`'s
first direction as regraded after that study's referee's Block. Goal G16; tests A97. Referee pending.

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `625cfd109` at about 04:48 UTC on 18 November. The
  run (long run MEET-HIST-B1, 193 cases on the shared runner) ended at 04:52 UTC, 193 of 193 ok.
- Code: [job.py, checks.py, merge.py and melib.py](../../experiments/MEET-HIST-20261118-001B/MEET-HIST-20261118-001B-E001_names/).
- Results: [results.json](../../artifacts/MEET-HIST-20261118-001B/MEET-HIST-20261118-001B-E001_names/results.json).

## The answer

- **The share of the knots' nesting that one grown base's unnamed states miss is carried mostly by the order of growth, and that
  order cannot be read from the states, even with the line's distinctions named** (computed, exact, every presentation of 5 to 8
  distinctions; prior uniform over labelled presentations). Shares of the information about the bare bracketing, read three ways:

  | Line of, k | Unnamed | The line's distinctions named | All named (the order of growth too) |
  | --- | --- | --- | --- |
  | 5, k = 2 / 3 / 4 | 0.60 / 0.39 / 0.22 | 0.70 / 0.69 / 0.51 | 1.0 / 1.0 / 1.0 |
  | 6, k = 2 / 3 / 4 | 0.65 / 0.63 / 0.53 | 0.67 / 0.71 / 0.64 | 0.83 / 0.91 / 0.93 |
  | 7, k = 2 / 3 / 4 | 0.57 / 0.62 / 0.58 | 0.58 / 0.65 / 0.64 | 0.68 / 0.79 / 0.83 |
  | 8, k = 2 / 3 | 0.51 / 0.58 | 0.51 / 0.59 | 0.58 / 0.70 |

  - Knowing which distinctions are the line's adds 0.005 to 0.30 (H3); the order of growth among the new ones adds more, 0.07 to
    0.49, at every k ≥ 2 (H4).
  - With all names the share keeps rising with k; without them it falls after a peak (for five to seven).
  - The order is not readable from the states with the line named: its conditional entropy is 0.9 to 3.9 bits at k = 2 to 4 (H1),
    and it grows with k.
- **Through the knots it is immediate** (settled by construction): the grown base's knots include the presentation's own, so
  reading which knots meet gives the nesting at every k. The question is about the states, which here are the distances
  (`DISTANCE-ORDER-20261117-001`, 3(a)).
- **Naming the order names the line** (by construction; the sanity row held at every k): with the new distinctions marked and
  ordered, the line's distinctions are a chain of nested cuts that the states order up to reversal.

**In the owner's terms.**
- What one grown base's distances miss of how the knots nest is mostly the order in which its distinctions were added. That order
  is history: the states and their distances do not record it, even when the line's own distinctions are known.
- The knots record it at once: a base read with its knots shows how they nest.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| G | 4 gate checks pass | held | the referee's named shares at five reproduce |
| H1 | H(order of growth \| line named) > 0 at every k ≥ 2 | held | 0.90 to 3.92 bits |
| H2 | All named > line named at every k ≥ 2 | held | every n0 and k |
| H3 | Line named > unnamed at every k ≥ 2 | held | by 0.005 to 0.30 (smallest at eight, k = 2) |
| H4 | The order's increment exceeds the line's at every k ≥ 2 | held | every n0 and k |
| (sanity) | Order named = all named | held | by construction |

4 of 4 held. The advisor put H1 to H3 at about 0.97, 0.88 and 0.90 and showed the first H4 held by construction.

## What it means for A97 and the goals

- **A97** stays under challenge, with a sharper statement of what is not distance. The share of the nesting that one grown base's
  distances miss is held mostly in the order of growth, which the states do not record even with the line's distinctions named;
  the knots record the nesting directly. History and the knots' meeting are information that a single grown base's distances lack.
  (The foundation already says formation order alone is not physical time; this is about information, not time.)
- **G16:** capability gained. The missing share decomposed exactly by which names carry it.

## Limitations

- Fewest-knot presentations, KF3, one prior, k ≤ 4 (three at eight); all-named shares still below 1 for six to eight at the last k.
- "The order of growth" is the arrival order of the new distinctions; other records of history (which knots were added when) are
  not read separately.

## Reproduce

```sh
cd experiments/MEET-HIST-20261118-001B/MEET-HIST-20261118-001B-E001_names
../../../.venv/bin/python -B checks.py
cd ../../..
.venv/bin/python -B scripts/longrun.py launch experiments/MEET-HIST-20261118-001B/MEET-HIST-20261118-001B-E001_names/job.py \
  --out <dir> --unit <name> --workers 12 --case-mem 1200M
.venv/bin/python -B experiments/MEET-HIST-20261118-001B/MEET-HIST-20261118-001B-E001_names/merge.py <dir>
```

## Advisor

Consulted once before the freeze: the first H4 (the order named alone equals all named) holds by construction and became the
sanity row; probabilities for H1 to H3; ties scored as failures. Not consulted after the read-out.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: is the order of growth readable from a grown base without names | **Status:** Successful (referee pending) | Not from the states, even with the line named; it carries most of the share the unnamed distances miss; 4 of 4 held |
| Local direction: how knots meet as information under KF3 | Continue | Whether the new knots alone record the order, and the long-growth limits, are open |
| Broader exploration: A97 against history | Unmapped | One rule; history as information not yet read in other growths |
| Long-term goal: G16 Learning the rules behind what a system allows | Capability gained | The missing share located exactly |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Do the knots KF3 added, without the starting knots, record the order of growth (and so the nesting)? | 3/3 | 2/3 | Read the grown base with only its added knots (co-knotted pairs that hold a new distinction), unnamed, five to seven → stop when it reaches the all-named share, or at the part it misses | Selected · awaiting go-ahead |
| 2 | Long growth: named and unnamed shares to k = 20, sampled | 2/3 | 3/3 | Sample six and seven → the limits | Alternative · deferred |
| 3 | Which block of the table carries the unnamed share | 2/3 | 3/3 | Shares per block, exact | Alternative · deferred |

- **#1.** Payoff: it asks whether history is written into how the new knots meet, which would put it in the knots and not outside
  the base; A97's question about what is not distance. Concreteness: the added pairs are tracked by the engine; the reading must
  exclude the starting knots cleanly.
- **#2, #3** as in `MEET-DIST-20261118-001`.

**Corrections:** none.

**Goals:** a G16 checkpoint (capability gained); no goal changed; direction #1 filed as sub-goal B199.

**Assumptions:** A97 under challenge, with this finding added; A100 gains this study among what rests on it; no new entry.

**Basket:** read; `MEET-DIST-20261118-001#1` taken by this epic.
