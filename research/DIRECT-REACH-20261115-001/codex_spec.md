# Codex specification: direct reach across levels (DIRECT-REACH-20261115-001A)

You are computing, not designing. Follow this exactly. If anything is ambiguous or seems wrong, write it in `REPORT.md` under
"Ambiguities" and skip only the affected part.

## Rules

- Work from `/home/jscul/p-vs-np-contact-first`; write **only** in
  `experiments/DIRECT-REACH-20261115-001A/DIRECT-REACH-20261115-001A-E001_direct_reach/codex/` (CODEX). No git writes, no network.
- `.venv/bin/python -B`; at most 4 processes; under 8 GB. Reuse read-only, by import or copy:
  `experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex/` (`pattern.py`, `job.py`'s `compute`,
  `search.py`, `certificates.py`, the compiled `lrat_check`) and the census records
  `artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/records_slim.jsonl.gz`.
- Every refutation's CNF and LRAT proof is kept (gzip, named by the CNF's SHA-256, hashes in the records), including union fates.
- Write the code, run the gates and a 10-case smoke through `scripts/longrun.py run --foreground --limit 10`, then stop. The thread runs
  the full jobs.

## Populations (from the census records; deterministic order by case id)

- **D:** every description with an alive union whose L(1..4) is constant (L = 2 or 3 at every s), or equal to [3, 3, 4, 4]: about 145.
- **U:** every description with an E_R membership, bounded relative activity, and an undecided L at some s: 88.

## Computations per description (N = 9 unless stated)

1. **Tie classes.** All forced pairs (u, v) among the 1,023 addresses (forced equal or forced unequal in every state), by sampling at
   least 64 random states (CaDiCaL with random phases) to propose candidate pairs, then confirming each candidate with two SAT calls;
   union-find with signs. Record: the classes as lists, and for s = 1..6 with top level 3 (and top level 2), whether one class meets the
   top level and level top + s. A confirmed tie is certified by its two refutations (kept).
2. **Threshold reach.** With the census search (`compute` with its `k_max` set), for top level k0 ∈ {2, 3} and s = 1..(9 − k0 − 1):
   whether a bond of size ≤ 3 meets level k0 and level k0 + s, and, for the [3, 3, 4, 4] ones, whether one of size ≤ 4 does; budget
   300 s per (k0, s) query; answer yes (with the bond and its certificates), no (exhausted), or undecided.
3. **Homomorphisms.** For each candidate map σ in the family {x ↦ c·x, x ↦ x·c, x ↦ c·m(x), x ↦ m(x)·c : c ∈ {0, 1}, m a state map or
   word of length ≤ 2 of the description}: whether σ sends every knot of the depth-8 pattern to a knot of the depth-9 pattern (three
   distinct images). Record the maps that do.
4. **Life to depth 12.** The union fate at N = 10, 11, 12 (certified; a budget of 600 s each; undecided otherwise).
5. For U only: the census search at k0 = 3 with a 900 s budget per s, only at the s where the census was undecided, after steps 1 and 2
   have answered what they can.

## Gates (write `CODEX/gates.json`)

- **G-tie:** on 50 tiny random descriptions (N = 4), the tie classes equal those from enumerating every state.
- **G-reach:** steps 1 and 2 agree with the census's L at k0 = 3, s = 1..4 on every population D description (L = 2 iff a spanning
  class; L ≤ 3 iff the threshold answers yes).
- **G-hom:** a hand-made map that is not a homomorphism is rejected; on 20 random descriptions every accepted σ is checked knot by knot
  by a second, plain implementation.

## Shared runner

`CODEX/job.py` with `setup(params)` (`pop=D` or `pop=U`), `cases()`, `run()`; per-case work directory removed at start and end;
per-case results as JSON. Report per-case times from the smoke and an estimate for each population at 6 workers.

## REPORT.md

What you wrote, the gates, the smoke, the estimates, the launch commands, "Ambiguities".
