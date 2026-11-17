# The navigating agent on signed knots (groundwork for the slow loop)

Ticket `SIGNED-NAV-20261117-001`, 2026-11-17, at the coordinator's request (no study and no claims). The slow loop of
`SLOW-LOOP-20261117-001`, `EARN-BUDGET-20261117-001` and `SPEC-MERGE-20261117-001` rebuilds patterns whose knots are signed: a merged
distinction can enter a knot negated. The learned agent of `MEET-TRANSFER-20261117-001` read only unsigned knots. This copy of its
engine adds signed knots and an optional initial state, so the slow loop can use the agent as its fast loop, and a handle that carries the agent's memory across the slow loop's
rebuilds.

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

## The handle: memory that persists across rebuilds

Added at the coordinator's second request (memory persisting across structure changes is central to the owner's idea).

**The C handle** (`na_new`, `na_run`, `na_get`, `na_free` in `nae_engine.c`). It keeps a run's whole state between calls:
- the state;
- each distinction's last flip and recent-flip count;
- each knot's last visit and recent-visit count;
- the random stream, the step counter and the recurrent state;
- the last flipped distinction, the order of the violated list, and the knots the last flip violated.

`na_new` starts a handle from any such state (or fresh from a seed), `na_run` runs a budget of steps, and `na_get` reads the
state back. The search loop is now one function shared by the plain run and the handle.

**The Python side** (`handle.py`). `AgentHandle` wraps the handle. `carry(state, n_new, m_new, dist_from, par, knot_from,
x_new)` is the rule that carries the memory across a rebuild. The caller lists, for each new distinction and each new knot,
the old ones it comes from: several for a merge, one listed under several for a split, itself for an unchanged one.
- **Value.** The caller's (the slow loop's vote) or the first member's, corrected by its parity.
- **Last flip, last visit.** The most recent among the members; never only if none was.
- **Recent counts.** One member keeps its count as it stands. Several are decayed to the present and summed. A split part
  inherits the whole.
- **New knots** (no old knot) are never visited.
- **The rest.** The random stream, t, the recurrent state and the last flipped distinction (mapped) carry unchanged.
- **Attention.** The violated list keeps its order for surviving knots, and the knots the last flip violated are mapped.

**Gates** (`check_handle.py`, all passed; `handle_gates.json`). The first four cover 54 runs each: 5 rules and the D, Dr, Dn
and L3sm policies, on 3 unsigned and 3 signed patterns.

| Gate | What it checks | Result |
| --- | --- | --- |
| H-plain | A handle run of the whole budget equals the plain run: flips, total incidences, final state | 54 of 54 |
| H-epochs | The run split into epochs of random lengths equals it | 54 of 54 |
| H-rebuild-identity | The run split into epochs, rebuilt onto the unchanged pattern at every boundary (state read, carried by the rule, a new handle), equals it: the carried state is the whole state | 54 of 54 |
| H-rebuild-gauge | Re-signing random distinctions at every rebuild continues the run exactly, with final states differing by the accumulated re-signing | 54 of 54 |
| H-merge | The slow loop's real rebuild sequences: 10 patterns of 800 distinctions with 5 to 18 tie-merge rebuilds each, replayed with Dr and D. Memory is carried by the rule at each merge, with a fresh restart at each merge as context. Every run solves, its state mapped back satisfies every original knot, and no carried last flip or visit lies after t | 40 of 40 |

The merge replay is a gate, not a measurement. Its single runs show no consistent difference between carrying the memory and
restarting at each merge (4 of 10 patterns fewer flips with memory for Dr, 5 of 10 for D). Whether carried memory helps is a
question for the slow loop's own study.

After the loop was moved into a shared function, the signed gates (`check_signed.py`) were rerun, including G-id, the run-for-run
identity with MEET-TRANSFER's engine.

## For the slow loop

- Create `AgentHandle(inst, "policy", (), theta, flags, seed, x0=...)` on the pattern.
- Run it in epochs with `run(budget)`.
- At a rebuild, call `carry(h.state(), ...)` with the tie map and open a new handle with `state=`.
- Signed knots follow the slow loop's convention.
