# Codex specification: is reading the whole rule (TOP-INFO-20261114-001A)

You are computing, not designing. Follow this exactly. If anything is ambiguous or seems wrong, do not resolve it: write the question
in `REPORT.md` under "Ambiguities", choose nothing silently, and skip only the affected part.

## Rules

Same as `research/READ-RULE-20261114-001/codex_spec.md`, with CODEX =
`experiments/TOP-INFO-20261114-001A/TOP-INFO-20261114-001A-E001_rule_check/codex/`. Write only there; no git; `.venv/bin/python -B`;
at most 2 processes and about 8 GB; shared runner for anything over about 10 minutes (smoke `--limit 20`, `launch --prepare-only`,
then stop: the thread launches). Repository material only.

## Read first

`research/TOP-INFO-20261114-001/preregistration.md` (frozen: checks 1 to 4, gate G, predictions T1 to T3),
`research/TOP-INFO-20261114-001/advisor_review_answer.md`, and READ-RULE's `codex/REPORT.md` (its five ambiguities; for R use the
theorem's quantifier: on a residue, R applies when some state of the repeating part has the knot's position carried and the exception
failing there).

## Inputs (read-only; reuse, do not copy)

- CARRY-BOUND: `experiments/CARRY-BOUND-20261114-001A/CARRY-BOUND-20261114-001A-E001_window/codex/` (code, `window_full/results.jsonl`
  streamed, `paths_full/`, `summary.json`), and the digest in `artifacts/CARRY-BOUND-20261114-001A/.../window_digest.jsonl.gz`. The
  final verdict after the path DP: bounded by window, or bounded by the path DP (`paths_full`), growing, undecided (83 in scope).
- READ-RULE: `experiments/READ-RULE-20261114-001B/READ-RULE-20261114-001B-E001_coverage/codex/` (`coverage.py`, `results.json`, the
  per-state tie flags).

## Tasks

1. **The rule's exceptions** (check 1): with the theorem's quantifier, the R flag per family and residue; cross-tabulate against the
   final verdict; list families bounded on a residue where R does not apply (by stratum: O, the 9 exception families, others), and
   any growing family where R applies (gate).
2. **Plain pinning** (check 2, T1): per residue, whether some repeating state has the window projection on main's ports V and the end
   copy's own distinctions X_c non-product. Cross-tabulate.
3. **Bond-pinning** (check 3, gate, T2): per residue, whether some repeating state has shattered T ⊆ V, shattered D ⊆ X_c, T ∪ D not
   full. Gate: no growing family is bond-pinned at a large depth.
4. **Two-block window** (check 4, gate, T3): extend CARRY-BOUND's window so that the top side is main's whole flattened block (its
   ports and own distinctions, with identity merging as before), not only its ports. State = (joint relation of main's block
   distinctions with the end copy's ports, identity partition). Same Q_s iteration and caps; least bond up to size 6 containing a port
   of main and an own distinction of the end copy. Run it on every in-scope and out-of-scope family whose final verdict is not
   bounded, and on 200 bounded families in sha256("TOP:" + key) order. Gates: on 100 certified-forgetting families (same order), U₂
   never below 2 + ⌊s/r⌋ (shifted for wrappers); U₂ ≤ U wherever both are finite; a separate brute-force unfolding on 30 families at
   s ≤ 3 matches the two-block projection.
5. **Hiding** (reported): among the undecided, families with a non-rectangular long trimmed product (CARRY-BOUND's G2 not certified)
   and no bond-pinning and no two-block bond.

## Outputs

`results.json` (per family flags), `summary.json` (every count and share; gate G; T1 to T3 computed), `REPORT.md` (what was built, gates,
timings, Ambiguities, and launch commands if a run was left for the thread).
