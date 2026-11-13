# Codex specification: the true least bond with side branches (TRUE-BOND-20261113-001A)

You write and validate code; you do **not** run the full computation (the thread launches it). If anything is ambiguous or seems
wrong, do not resolve it: write the question under "Ambiguities" in `REPORT.md` and skip only the affected part.

## Rules

- Repository root `/home/jscul/p-vs-np-contact-first`. Write files **only** inside
  `experiments/TRUE-BOND-20261113-001A/TRUE-BOND-20261113-001A-E001_side_branches/codex/` (CODEX). Change nothing else; no git
  commands that change anything. Use `.venv/bin/python -B`. Keep every command in the foreground and finish each before your session
  ends; any single command must finish within 20 minutes. At most 4 processes at a time.

## Objects

- **Families.** `families_one_def()` in `experiments/BOND-DEPTH-20261112-001A/BOND-DEPTH-20261112-001A-E001_spine_bonds/census.py`
  (BD) returns `(idx, defs)`; `defs = [(3, l, calls)]`, one definition with ports 0, 1, 2, own distinctions 3 .. 2 + l, and `calls` a
  list of `("K", (a, b, c))` (a knot: not all equal on those three) or `("SELF", (a, b, c))` (a copy of the definition whose ports are
  a, b, c). The study set is the 226 families with `lambda_float > 0` and `complete` true in
  `artifacts/PROVED-RATE-20261113-001A/PROVED-RATE-20261113-001A-E001_cycle_mean/rates_all.jsonl`.
- **The infinite pattern.** The tree of copies: the main copy C_0 has ports = the top distinctions; each SELF call in a copy makes a
  child copy whose ports are the call's arguments and whose own distinctions are fresh. A knot (K call) constrains its three
  distinctions to be not all equal. **G** = the limit relation, an 8-bit mask over port states (bit b of a state = port b): use
  `_, _, Gd = BD.L.depth_sequence(defs, BD.L.TOP)` and `G = Gd[0]` (boolean array of 8). Any subtree containing no chosen
  distinction is replaced by the constraint "its root's ports take a state in G".
- **The ray.** C_j is the child made by the **first** SELF call (in `calls` order) of C_{j−1}. The other SELF calls of a copy make
  **side** children.
- **Bond.** A finite set W of distinctions is constrained if some assignment of W extends to no state of the infinite pattern; a bond
  is a constrained W all of whose proper subsets are unconstrained (single deletions suffice). The study quantity: **L(s)** = the least
  |W| over bonds W that contain at least one port of C_0 and at least one own distinction of C_s; W may contain any distinctions of
  any copies. **L_ray(s)** is the same with W restricted to own distinctions of C_0 .. C_s and the ports of C_0 (BD's `run_family`).

## Method (implement exactly)

Distinctions are assigned to the copy that creates them (ports of C_0 to C_0; each copy's own distinctions to it).
- **Summary of a subtree S** with chosen set W_S (inside S): `F_S` = the set, over assignments α of W_S, of the 8-bit masks of root
  port states of S consistent with α (some state of S's insides extends them); `G_S` = the set, over w in W_S and assignments of
  W_S − w, of the same masks with w forgotten. Build G_S from paired masks (union of the two masks that differ only in w), never from
  F_S alone. The empty choice gives the summary `({G}, {})` at cost 0.
- **Combining at a copy P** with chosen own distinctions W_P and child summaries (F_c, G_c) (side children not chosen use
  `({G}, {})`): for α_P and a choice R_c ∈ F_c per child, R_P = {σ : some assignment of P's env with ports σ, α_P on W_P, all of P's
  knots satisfied, and each child's argument state in R_c}. F_P = all such R_P. G_P = those with one w ∈ W_P forgotten (others from
  F) together with those using one child's mask from G_c (all others from F).
- **Generic table** (side subtrees): least cost per summary, cost = |W_S|, by iterating the combination over heights h = 1, 2, … from
  the base until no summary's least cost changes (a least fixed point), with costs capped at `cap(s) = L_ray(s) − 2`. Prune (exactly):
  side summaries with an empty mask in F_S (they contain a bond without a top port), summaries with cost > 0 and F_S = {G} (their
  members are inessential), and any summary with an empty mask in G_S.
- **Ray summaries**: at C_s, W_{C_s} must contain at least one own distinction of C_s (its ray child and side children from the
  generic table); upward, C_j combines its ray child's ray summary with side children from the generic table. At the root C_0 (whose
  ports are its own), W_0 must contain at least one port; a choice is a **bond** iff some combination gives the empty mask (i.e. no
  state) and every one-forgotten combination is non-empty. L(s) = the least total cost of a bond.

## Validation (do all; report each case)

1. **Brute force.** For truncations: the pattern down to depth s + h with every SELF call below that depth replaced by "args in G";
   W over all distinctions of the truncation containing a C_0 port and a C_s own distinction; constrained and minimal tested by
   direct satisfiability (python-sat) of the truncated CNF under assumptions (no masks). Compare the **number of bonds of each size**
   up to the least size + 1 with the height-limited DP (generic table iterated only h levels) at the same truncation. Cases: 10
   small families from the study set, s = 1, 2, 3, h = 2; and the smallest family with h = 3.
2. **Shortening case.** Search the validation families (and others in the study set if needed, s ≤ 3) for one with L(s) < L_ray(s);
   include it in the brute-force comparison. If none exists in what you can brute-force, say so.
3. **Mutant.** Run the comparison with G_S replaced by F_S; it must disagree on some case. Report.
4. **Ray check.** With side children forced to `({G}, {})`, the DP must give L_ray(s) for s ≤ 12 equal to BD's `run_family`.

## Deliverables (inside CODEX)

- The code: a module and a runner `run_true.py --workers N --only IDX... --smax 12` that writes one JSON line per family to
  `true_rates.jsonl` (append; skip families already present), each with `idx`, `L` (list for s = 1..12, `null` when not reached),
  `L_ray` (the same, from the ray check), `generic_summaries` (table size), `seconds`, `peak_mb`, `status`.
- `validation.json` with every case of 1–4 and pass/fail.
- A smoke run of the runner on 5 families (the smallest and four random from the study set), with per-family time and peak memory,
  in `smoke_true.jsonl`, and an estimate of time and memory per worker for all 226.
- `REPORT.md`: what was written, the validation results, the smoke timings and memory, deviations, and "Ambiguities".
