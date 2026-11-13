# Codex specification: the reach census (REACH-CENSUS-20261113-001A)

You are computing, not designing. Follow this specification exactly. If anything is ambiguous or seems wrong, do not resolve it:
write the question in `REPORT.md` under "Ambiguities", choose nothing silently, and skip only the affected part.

## Rules

- Work from the repository root `/home/jscul/p-vs-np-contact-first`. Write files **only** inside
  `experiments/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/codex/` (call it CODEX below). Do not
  modify, move or delete any other file. Run no git command that changes anything (no add, commit, stash, checkout, reset).
- Use `.venv/bin/python -B` (Python 3.13 with numpy and python-sat). Use **at most 4 processes** at a time and keep your own runs
  under about 8 GB of memory in total: another heavy study is running on this machine. Do not touch any process you did not start.
- Use only repository material. Do not read `experiments/TRUE-BOND-20261113-001A/` (another study's work in progress).
- **Do not run the full census.** Write the code, run the validation and the smoke run below, and stop. The full run is launched
  afterwards by the thread from your runner, so it must be resumable and must not depend on your session.

## Inputs (read-only)

- `experiments/SHORT-DESC-20261112-001A/SHORT-DESC-20261112-001A-E001_description_census/dlang.py` (call it L): the description
  language, `sample`, `relations`, `depth_sequence`, `NAE`, `TOP`.
- `experiments/LIMIT-ONLY-20261112-001A/LIMIT-ONLY-20261112-001A-E001_limit_only/census.py`: its `sample(worker, tries)` shows how
  the 223,261 draws were made. Stored rows: `artifacts/LIMIT-ONLY-20261112-001A/LIMIT-ONLY-20261112-001A-E001_limit_only/sample_{w}.jsonl.gz`
  for w = 0..7 (one row per draw; `defs` stored only on some rows; a final `{"kind": "done"}` row).
- `experiments/LIMIT-STATE-20261112-001A/LIMIT-STATE-20261112-001A-E001_limit_states/census.py` (call it LS): `usual(defs)` and
  `relation_clauses`.
- `experiments/BOND-DEPTH-20261112-001A/BOND-DEPTH-20261112-001A-E001_spine_bonds/census.py` (call it BD): the one-definition ray
  DP (`block_relation`, `tables`, `run_family`, `ray_cnf`, `brute`, `families_one_def`, `INF`) and its records
  `artifacts/BOND-DEPTH-20261112-001A/BOND-DEPTH-20261112-001A-E001_spine_bonds/runs_merged.jsonl`.
- `experiments/PROVED-RATE-20261113-001A/PROVED-RATE-20261113-001A-E001_cycle_mean/codex/` (call it PR): validated code for the
  reachable graph (`ray_dp.py`, `run_rates.py`), trimming, SCCs, Karp and `bounded_all` (`graph_algorithms.py`), and its results
  `rates_all.jsonl` (keyed by `idx`, the index in `LS.families()`). Reuse its code where it fits.
- `research/PROVED-RATE-20261113-001/referee-R1/codex/recompute.py`: `exact_eventual_bound` (the exact residue test) and its
  results `recomputed.jsonl`. Reuse it.

## 1. The draws

Replay the sampler exactly: for w in 0..7, `rng = random.Random(int(hashlib.sha256(f"LO:{w}".encode()).hexdigest()[:16], 16))`,
150,000 calls of `L.sample(rng, **L.VARIANTS["main"])`, keeping a draw when `"defs" in d and d.get("t") is not None`. Pair the
j-th kept draw of worker w with the j-th stored row of `sample_{w}`. **Gate G0:** 223,261 draws in all; for every draw the stored
`bits` equals `d["bits"] - d["tbits"]` (to 1e-9), and where the row stores `defs` they equal the replayed `defs`. A family is the
replayed `defs` list; its key is its canonical JSON. Keep per draw: worker, try index, key, the stored `fate`, `limit_alive`,
`bits`. Write `draws.jsonl.gz`.

## 2. Each distinct family: the usual limit and the ray

For a family `defs`: `u = LS.usual(defs)[0]`; `G = L.depth_sequence(u, L.TOP)[2]` (a dict from each self-holding definition's
index to its limit relation, a boolean array over 8 port states); the **usual limit lives** iff `L.relations(u, G)[-1].any()`.
A definition is **self-holding** when its own calls include SELF.

**Inlining.** The flat body of definition i: its ports 0..k−1, then its own distinctions, then the own distinctions of every inlined
callee, numbered in the order met; its calls are K calls and calls to self-holding definitions (SELF counts as a call to i itself).
Every call to a definition that is not self-holding is replaced by that definition's flat body on the call's arguments (with fresh
own distinctions), recursively, in body order (depth first). The **own distinctions** of a flat body are all its distinctions
except its ports.

**The ray.** Let main be the last definition, flattened. The ray definition **S** is main if main is self-holding; otherwise the
callee of main's first call (in flat order) to a self-holding definition. The **entry call** is main's first SELF call when main
is S, otherwise main's first call to S. In the flat body of S, the **ray call** is its first SELF call. Copies: C_0 = main;
C_1 = the copy made by the entry call; C_{j+1} = the copy made by the ray call inside C_j. Every other call to a self-holding
definition T, in main or in S, is a **side call**, read as its limit relation G[T] on its arguments.

**Blocks.** As `BD.block_relation`, generalised: the allowed assignments of a flat body's distinctions are those satisfying NAE on
every K call and G[T] on every side call. In a middle block (S) the ray call's arguments are the outgoing interface (8 states); in
the closing block (S, the deepest copy C_s) the ray call is read as G[S] and there is no outgoing interface. The start block is
main with the entry call as its outgoing interface and **no incoming interface**: every assignment of its distinctions is
available (for main = S this is exactly BD's `START = (frozenset([255]), frozenset())`). A middle or closing block's incoming
interface is its three ports.

**The DP.** Exactly BD's (F, Gf) semantics, generalised to these blocks: W in the start block ranges over all non-empty subsets of
main's distinctions containing at least one of main's ports (k may be 3 to 6); W in a middle block over all subsets of S's own
distinctions, including the empty set; W in the closing block over all non-empty subsets of S's own distinctions, accepting when
`0 in F' and 0 not in G'`. Cost |W|. L_ray(s) for s ≥ 1 is the least total cost of a start, s − 1 middle transitions and an
accepting closing (C_s the closing block). Any way of computing the tables is allowed if it gives identical maps (gate G1 checks it
on the one-definition families). Note that a forgotten-member table is the full table of W with that member removed.

## 3. Settled classes (applied first, in this order; no DP)

- **S1 limit dead**: the usual limit does not live.
- **S2 no copy**: main's flat body has no call to a self-holding definition.
- **S3 no own distinctions**: S's flat body has exactly 3 distinctions.
- **S4 free own distinctions**: no own distinction of S lies in a K call of S's flat body, in a side call of S's flat body whose
  G[T] is not all true, or among the ray call's arguments.

## 4. Computed families: graph and classes

For every other family: build the reachable graph by breadth-first search from the start nodes through middle transitions, as in
PR's `build_graph`. Caps: **300,000 nodes**, **300 seconds** of computation per family, and **block size**: if main's or S's flat
body has more than **12 distinctions**, build nothing. `complete` = the frontier empties before the node cap. On the graph: the
trimmed graph (reachable from a start and co-reachable to a node with an accepting closing), its strongly connected components,
λ (Karp, exact fraction, `None` if the trimmed graph has no cycle), `bounded_all` as in PR, and the referee's
`exact_eventual_bound` (period, onset depth, uniform cost bound, missing residues; its product-size gate of 8,000,000). Recompute
L_ray(s) for s = 1..30 from the graph by min-plus layers (as PR's `recompute_layers`).

Class of a computed family (first that applies):

1. **unresolved**: block size over 12, timeout, error, or an incomplete graph without a positive certificate (a positive certificate
   on an incomplete graph is `bounded_all` true or `eventually_bounded` true; such a family is **bounded**); also a complete graph
   whose exact test hit its product-size gate while λ = 0.
2. **none at any depth**: complete, and the trimmed graph is empty (L_ray(s) = INF for every s).
3. **lost at large depths**: complete, trimmed graph non-empty and acyclic.
4. **bounded**: `eventually_bounded` true (or `bounded_all` true).
5. **grows**: complete, λ > 0.
6. **mixed by residue**: complete, λ = 0, `eventually_bounded` false.

Record per family: key, number of definitions, k of main, own-distinction counts of main and S, nodes, complete, trimmed nodes,
λ (string and float), bounded_all, the exact test's fields, L_ray(1..30), class, seconds, status.

## 5. The alternative ray (robustness)

The **last-call ray**: the entry call is main's last SELF call (main = S) or last call to S, and the ray call is S's last SELF
call; S unchanged. On the computed families where it differs from the first-call ray, run the same computation and classes. In the
full run this covers a frozen sample: 3,000 such families drawn uniformly by `random.Random(20261113).sample` from their sorted
keys (all of them if fewer). Write its records separately.

## 6. Gates (run all in validation, on the sizes given)

- **G0** (section 1).
- **G1, one definition.** For the 664 families of `BD.families_one_def()` whose PR record has `complete` true and `nodes` ≤ 20,000:
  your `nodes`, `complete`, `lambda`, `bounded_all` and L_ray(s) at every depth recorded in `runs_merged.jsonl` equal PR's and BD's;
  and for the families in the referee's `recomputed.jsonl`, the exact test's `eventually_bounded`, period and missing residues equal
  the referee's. Report every mismatch. (The full run repeats G1 on all 664 at the census caps.)
- **G2, metamorphic.** For the same families, wrap each as `[D_0, (3, 0, [(0, (0, 1, 2))])]` (a new main calling D_0 on its ports):
  require the same λ, `complete` and class, and L'_ray(s) = L_ray(s − 1) for s = 2..30.
- **G3, independent brute force.** Write a check that shares no code with your DP: build the ray's CNF for C_0..C_s (K calls as NAE
  clauses, side calls and the deepest ray call as their relations' clauses, as in `BD.ray_cnf`, generalised), enumerate its
  satisfying assignments over the ray's distinctions (at most 22), and find the least W containing a port of main and an own
  distinction of C_s that is constrained (not every assignment of W occurs) and minimal (every W minus one member is
  unconstrained), searching sizes up to 7 (report "none up to 7" otherwise). Run it at s = 1..s_max, s_max the largest s with at
  most 22 ray distinctions (at most 10), on 150 computed families chosen by `random.Random(7)` among the smallest-block families:
  at least 10 of each computed class where that many exist and at least 40 with more than one definition. Report every
  disagreement with L_ray(s) (a DP value above 7 agrees with "none up to 7").
- **G4.** No family with stored fate `forever` has a dead usual limit (compactness).

## 7. Smoke run

Run sections 2 to 4 on 1,000 distinct families drawn by `random.Random(1113).sample` from the sorted keys of all distinct
families, and section 5 on up to 200 of the eligible ones among them. Report timings by class and by block size, memory peak, and
the projected time of the full run on 4 workers. Do not report class shares from the smoke run (write them only to its output
file).

## 8. The runner and the summary (for the thread's full run)

- `run_census.py --workers N --out DIR [--only-gate664] [--alt-ray]`: all distinct families (settled and computed), appending one
  JSON line per family as it finishes, skipping keys already in the output (resumable), each family in a worker process with its
  own time cap; a worker whose memory passes 3 GB stops that family as unresolved (state this in the record). Gate G1 at census
  caps on all 664 (`--only-gate664` runs only that).
- `summarize.py DIR`: joins the draws with the family records and writes `summary.json` with, for each cell (all; forever; dies
  with a dead usual limit; alive only in the limit, i.e. stored fate not `forever` and usual limit alive) and in total:
  - counts by draws and by distinct families of every settled class (S1–S4) and every computed class;
  - the same split by number of definitions (1, more than 1) and by S's own-distinction count;
  - within the computed draws of each cell, each class's share with unresolved counted against it (low) and for it (high), and a
    95% interval by bootstrap over draws (2,000 resamples, `random.Random(20261113)`): the 2.5% quantile of low, the 97.5% of high;
  - the conditional share used by P1: bounded among computed draws in {grows, bounded, mixed by residue, unresolved}, low and high
    as above, with its bootstrap interval;
  - the difference used by P3: grows share (limit-only cell) minus grows share (forever cell), among computed draws, with unresolved
    assigned against the difference (low) and for it (high), point values and the bootstrap 2.5% quantile of low;
  - the unresolved share of computed weight per cell;
  - λ distribution, bounded values (uniform cost bounds and onsets), and the alternative-ray agreement matrix (first-call class
    against last-call class, by distinct families).
  Shares by distinct families are exact counts of the sampled set, with no interval.

## Outputs (all inside CODEX)

Your code; `draws.jsonl.gz`; `gates.json` (G0–G4 results with every mismatch); `smoke_families.jsonl`, `smoke_alt.jsonl`,
`smoke_summary.json`; `REPORT.md`: what you ran, exact commands for the full run, timings, memory, deviations, and "Ambiguities".
Do not interpret results.
