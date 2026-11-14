# Codex specification: least bonds across levels of addressed patterns (LEVEL-REACH-20261114-001A), stage 1

You are computing, not designing. Follow this exactly. If anything is ambiguous or seems wrong, do not resolve it: write the
question in `REPORT.md` under "Ambiguities", choose nothing silently, and skip only the affected part.

## Rules

- Work from `/home/jscul/p-vs-np-contact-first`. Write **only** inside
  `experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex/` (CODEX). Modify no other file; no git
  command that changes anything; no network.
- `.venv/bin/python -B` (numpy, python-sat). At most **4 processes**, under about 8 GB; other studies share the machine. Touch no
  process you did not start.
- Read-only inputs you may import or copy: `experiments/ADDR-KNOTS-20261113-001A/ADDR-KNOTS-20261113-001A-E001_addressed_census/codex/addr.py`
  (actions, words, product automata, activity classes, `gamma`); `experiments/LEVEL-RETURN-20261113-001A/LEVEL-RETURN-20261113-001A-E001_certified_levels/`
  (`certify.py`, `lrat_check.c`: copy the C file into CODEX and compile your own binary there); `docs/tooling/shared-runner.md`.
  The design is `research/LEVEL-REACH-20261114-001/design.md`.
- **Stage 1 only:** write the code, run the gates and a 20-case smoke through the shared runner (`scripts/longrun.py run
  --foreground --limit 20`), and stop. The thread runs the pilot and the registered run.

## Objects

- **Addresses and levels.** Binary words of length 0..N as in addr.py (integers with the first letter most significant, plus the
  length). Distinction id: `2**n - 1 + x` for the address x of length n (so ids 0 .. 2^(N+1) − 2; the root is id 0).
- **Automaton and words** exactly as addr.py (W_s; `(q, r)` means r first).
- **Terms.** T_s = W_s × {none, 0, 1}, in that order (word-major, then letter none, 0, 1). A term (w, a) sends an address x of length
  n to w(x) (length n) or w(x)·a (length n + 1, the letter appended as the new last letter).
- **Placement.** An unordered triple of distinct terms (sorted indices into T_s). At every address x of length n with 0 ≤ n ≤ N,
  for which all three images have length ≤ N, the triple of images is a knot when the three are distinct (as distinctions).
- **Description.** (s, sw, d0, d1, placements); key as in addr.py with placements of term triples.
- **Pattern up to N.** The union of the knots of all placements over all x, as sorted id triples, deduplicated.

## Weighting and populations

As the census (addr.py's `gamma`, fair coins, per-draw `random.Random(f"{seed}-{i}")`): s = gamma (s > 5 rejected); swap bits and
successors; r = gamma (r > 8 rejected); each placement a uniform index into the 3-subsets of range(|T_s|) in
`itertools.combinations` order (log₂ C(|T_s|, 3) bits). Populations (build them all, deterministically; stage 1 runs none in full):

- **Pilot P** (exploratory, run by the thread): W_P = draws 0..999 with seed `20261120`; E_P = 200 automata with s = 3 drawn uniformly
  by `random.Random("20261122-a")`, 2 placement lists each, list j of automaton a by `random.Random(f"20261122-{a}-{j}")` with
  r = 1 + gamma capped at 9.
- **Registered R** (sizes may be cut by the thread after the pilot, by a frozen rule, before the run): W_R = draws 0..3,999 with seed
  `20261121`; E_R = every s = 2 automaton (64) with 5 lists, and 1,000 automata with s = 3 drawn by `random.Random("20261123-a")` with
  2 lists, seeds `f"20261123-{s}-{a}-{j}"`.

## Fields per key (at k0 = 3, S = 4, N = 9; and N = 10 for the gate rows)

- **Settled flags:** `no_join` (no placement has both a term with a letter and a term without: then no knot joins two levels);
  `tree_only` (every distinct placement is the triple ((), none), ((), 0), ((), 1)); `s1`.
- **Classes:** letter and relative activity classes of the words used, by addr.py (letters ignored).
- **Union fate:** alive or dead or undecided (CaDiCaL 2.1.2 via the LEVEL-RETURN certifier: a checked model; or a refutation solved
  again with an LRAT proof on disk in the case's work directory, checked by your compiled `lrat_check`, then deleted).
- **For s = 1..S:** the top set A = level k0's 8 addresses, the target set B = level k0 + s's addresses.
  - `components`: whether some address of A and some of B lie in one connected component of the pattern's knot graph (distinctions
    adjacent when they share a knot). If not: `L = "none"` (no bond can hold both).
  - `L_N(s)`: the least size of a **bond** (a set of distinctions whose projection of the pattern's states is not all of its value
    combinations, while every proper subset's projection is) holding at least one address of A and at least one of B, members
    anywhere in levels 0..N; or `"> k_max"` (k_max = 10) when the search proves no bond of size ≤ k_max exists; or `"undecided"`
    when the budget (300 s per (key, s)) runs out. Only for an alive union.
  - `L_target(s)`: the same with members restricted to levels 0..k0 + s (so `L_target ≥ L_N`; equality means a least bond needs no
    member below its target).
  - The found bond (ids), its forbidden assignment, the certificate summary (below).
  - For s = 1 and 2 only: for every target address b in B, the least bond holding some address of A and b (members anywhere), as
    a histogram of sizes.

## The exact search (required properties; the algorithm is yours)

A set is not full exactly when some assignment on it is forbidden by the pattern (an implied clause). Search the smallest forbidden
partial assignment σ whose support holds an address of A and one of B, smallest support first, then test that every maximal proper
subset of σ's support is full (all its 2^(m−1) assignments extend to states); if some proper subset is not full, exclude every
support containing it and continue. The first support that passes is a least bond. Suggested route: an implicit hitting set over
soft unit literals (two per distinction, at most one per distinction in a candidate, at least one from A and one from B), with
correction sets from satisfiable candidates, minimum hitting sets by RC2 or an exact enumeration in increasing size; complement
symmetry halves the work. Record whether the search proved optimality.

**Certificates for each reported bond:** the forbidden assignment's refutation (LRAT, checked) and one checked state for every
assignment of every maximal proper subset. A `"> k_max"` claim rests on the search's exhaustion; say how it is ensured.

## Gates (all must pass; write `CODEX/gates.json` and report in `REPORT.md`)

- **G-brute:** 300 random tiny descriptions with N = 3, k0 = 1, S = 2 (15 distinctions): enumerate all states, then every set of up
  to 7 distinctions; the least bond sizes (and "none" / "> 7") equal the search's at every s.
- **G-tree:** the description with the single placement ((), none), ((), 0), ((), 1) (any automaton): L_N(s) = s + 2 for s = 1..4 at
  k0 = 3, N = 9, and L_target(s) = s + 2.
- **G-mono:** on 50 pilot keys with an alive union at N = 10: L_10(s) ≤ L_9(s) wherever both are numbers.
- **G-cert:** every bond reported in the smoke carries checked certificates; a corrupted certificate (one flipped value in a state,
  one changed hint in a proof) is rejected.
- **G-pattern:** for 200 random keys, the pattern equals a second, plain implementation in `CODEX/reference.py` (loops, no numpy).

## Shared runner

`CODEX/job.py` with `setup(params)` (builds the population named by `--param pop=P` or `pop=R`), `cases()` (one case per distinct
key) and `run()` (all fields above); a case works in `CODEX/work/<case>/`, removed at its start and end. Smoke: `scripts/longrun.py
launch CODEX/job.py --out CODEX/smoke --unit lr-reach-smoke --workers 3 --case-timeout 1800 --case-mem 2G --mem-max 8G
--param pop=P --prepare-only`, then `scripts/longrun.py run --out CODEX/smoke --foreground --limit 20`. Report per-case times.

## REPORT.md

What you wrote, the gates, the smoke timings and an estimate for the pilot and the registered run at 6 workers, the exact launch
commands for the thread, and "Ambiguities".
