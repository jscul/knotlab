# RING-IN-BALANCE-20261123-001A-E001: the ring on real knots

An independent engine written from the frozen text alone: `research/RING-IN-BALANCE-20261123-001/definitions.md`,
`research/RING-IN-BALANCE-20261123-001A/preregistration.md` and the text of "The operator on the present end" in
`research/ORDINARY-DYNAMICS-20261120-001/end_operator.md`. No earlier program of the repository was opened or imported.
The readings taken where the text left a choice are in `deviations.md` (written before the registered runs).

## Files

- `engine.py`: the module other tickets import. Starts (`ring`, `d2`, `dw`, `from_stars`, `generator7`), `Law` (every
  ration, treatment, release rule and extra), `round_step` (steps 1 to 8), `part_round_step` (one complete round of one
  part), the live roster (`live_roster`, `Roster`), exact sameness (`same_rosters`, `same_parts`: invariants first, then
  VF2 isomorphism with h and k as colours), lines of descent, returns, balance, kinds (`Run`), and the knot tests
  (`parity_knot_test`: GF(2) ranks and the cut test; `nae_knot_test`: SAT; `extension_test_parity`).
- `test_engine.py`: self-checks against a deliberately naive second implementation and brute force.
- `gate.py`, `traces.py`, `a1.py` to `a7.py`, `summarize.py`: the gate, the two trace files, the registered runs, the
  verdicts. `common.py` and `knotcheck.py` are shared helpers.

Outputs go to `artifacts/RING-IN-BALANCE-20261123-001A/RING-IN-BALANCE-20261123-001A-E001_ring/` (one JSON per script,
one log per script).

## Commands (from the repository root)

```bash
cd experiments/RING-IN-BALANCE-20261123-001A/RING-IN-BALANCE-20261123-001A-E001_ring
ART=../../../artifacts/RING-IN-BALANCE-20261123-001A/RING-IN-BALANCE-20261123-001A-E001_ring
PY=../../../.venv/bin/python
ulimit -v 4000000
for s in test_engine gate traces a1 a2 a3 a4 a5 a6 a7 summarize; do
  timeout 600 $PY -B -u $s.py > $ART/$s.log 2>&1 || echo "$s failed"
done
cat $ART/summarize.log
```

`test_engine.py` must run before `gate.py` (the gate reads its result). `a4.py --ring 5` (or 7, 9) runs one ring of A4
alone and writes `a4_n<n>.json`; the summary reads `a4.json`. Every script finished in under 40 s and 200 MB on
2026-11-23; all outputs are deterministic (identical on rerun with another `PYTHONHASHSEED`, apart from the
`resources` timing fields).
