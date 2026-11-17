# The navigating agent on signed knots (groundwork for the slow loop)

Ticket `SIGNED-NAV-20261117-001`, 2026-11-17, at the coordinator's request (no study and no claims). The slow loop of
`SLOW-LOOP-20261117-001`, `EARN-BUDGET-20261117-001` and `SPEC-MERGE-20261117-001` rebuilds patterns whose knots are signed: a merged
distinction can enter a knot negated. The learned agent of `MEET-TRANSFER-20261117-001` read only unsigned knots. This copy of its
engine adds signed knots and an optional initial state, so the slow loop can use the agent as its fast loop.

## What changed

Code: `experiments/SIGNED-NAV-20261117-001/SIGNED-NAV-20261117-001-E001_signed_engine/` (`nae_engine.c`, `engine.py`).

- **Signed knots.** Knot (a, b, c) with signs (sa, sb, sc) allows every joint state except the two in which x_a ^ sa, x_b ^ sb and
  x_c ^ sc are all equal (the slow loop's convention). The engine counts each knot's literals that are 1. A flip changes each of the
  flipped distinction's literals, and break and make read the literal, not the bare value. Every read of the agent is unchanged:
  break and make as fractions of a distinction's knots, relative ages, ranks.
- **An initial state** can be passed (`x0`), so a caller can start the agent where the slow loop left the state.
- **Python.** `Instance(n, knots, signs=...)` and `run(inst, "policy", theta=..., flags=..., x0=...)`. An Instance refuses a
  knot with a repeated member (break and make assume three distinct distinctions; the slow loop's rebuilds produce none).
- **Unsigned instances without `x0`** take the old code path unchanged.

## Gates (`check_signed.py`, all passed; `gates.json`)

| Gate | What it checks | Result |
| --- | --- | --- |
| G-id | Run-for-run identity with MEET-TRANSFER's engine on unsigned patterns: 8 rules and the D, Dr, Dn and L3sm policies, four families, 12 instances | 144 of 144 runs identical (flips and incidences) |
| G-zero | All-zero signs with a given start run exactly as the unsigned path with that start | 192 of 192 identical, final states too |
| G-gauge | Re-signing a random set of distinctions in every knot and flipping their starts gives the same run | 192 of 192 identical; final states differ exactly by the re-signed set |
| G-small | 300 small planted signed instances: brute force finds an allowed state, every rule and policy reports a state that satisfies every signed knot; CaDiCaL's model on the signed CNF checks (100); incremental counts equal recomputation over 60,000 flips | 3,600 of 3,600 runs solved and checked; 0 mismatches |
| G-Dr | Dr and D, unchanged, on 10 signed patterns the slow loop rebuilt (its eager policy "GO", Novelty+ fast loop; 6 local window 10 and 4 block patterns of 800 distinctions, rebuilt to 78 to 741 tie classes with 49 to 378 signed knots; `capture_rebuilt.py` imports the slow loop read-only) | every run of every policy solved and checked (5 runs each); median flips 0.55 (Dr) and 0.46 (D) times the better of Novelty+ (0.7, 0.01) and (0.8, 0.01) on the same patterns, within the "sensible" bar of 3 |

The G-Dr figures are a gate's sanity reading on ten patterns, not a result: Novelty+ was not re-tuned on them, and one local pattern
(0.03) is one where Novelty+ apparently stalls.

## For the slow loop

The slow loop's own fast loop keeps a persistent handle across rebuilds: the state, each distinction's last flip and the random
stream. This engine starts a fresh run from a given state, so the agent's memory (ages, ranks, the recurrent state) restarts at
each rebuild. If the slow loop needs the agent's memory carried across rebuilds, the next piece is a handle API like its
`fl_new`/`fl_run`/`fl_get`, keeping last-flip and last-visit times per original distinction and knot through the tie map.
