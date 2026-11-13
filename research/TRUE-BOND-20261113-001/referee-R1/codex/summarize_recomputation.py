"""Join own cold-SAT results, retain retries, and bind permitted inputs by hash."""
from collections import Counter
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform
import sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    attempts, latest = [], {}
    for name in ('recomputed.jsonl', 'recomputed_retries.jsonl'):
        for line in (OUT / name).read_text().splitlines():
            r = json.loads(line)
            attempts.append(r)
            latest[r['idx'], r['s'], r['h']] = r
    families = json.loads((OUT / 'selected_families.json').read_text())['families']
    profiles = []
    for f in families:
        by_h = {str(h): [latest[f['idx'], s, h]['L_trunc'] for s in (1, 2, 3)] for h in (1, 2, 3)}
        profiles.append(dict(idx=f['idx'], own_distinctions=f['locals'], self_calls=f['self_calls'],
                             L_trunc_by_h=by_h,
                             study_L=[latest[f['idx'], s, 2]['study_L'] for s in (1, 2, 3)],
                             study_L_ray=[latest[f['idx'], s, 2]['study_L_ray'] for s in (1, 2, 3)]))
    mismatches = [{k: r[k] for k in ('idx', 's', 'h', 'L_trunc', 'study_L')} for r in latest.values() if not r['agrees_with_study']]
    result = dict(cases=len(latest), final_statuses=dict(Counter(r['status'] for r in latest.values())),
                  attempts=len(attempts), attempt_statuses=dict(Counter(r['status'] for r in attempts)),
                  h2_h3_agreement=dict(agree=sum(r['agrees_with_study'] for r in latest.values() if r['h']>=2),
                                       total=sum(r['h']>=2 for r in latest.values())),
                  all_h_agreement=dict(agree=sum(r['agrees_with_study'] for r in latest.values()),total=len(latest)),
                  mismatches=mismatches, profiles=profiles,
                  total_attempt_seconds=sum(r['seconds'] for r in attempts),
                  max_attempt_seconds=max(r['seconds'] for r in attempts),
                  peak_reported_mb=max(r['peak_mb'] for r in attempts),
                  max_variables=max(r['n'] for r in latest.values()),
                  sum_sat_calls_over_attempts=sum(r['sat_calls'] for r in attempts),
                  finite_limit='Exact finite truncation minima; stable h<=3 does not prove the arbitrary-depth minimum for size-4 cases.',
                  retries='Two 10-second searches exhausted all smaller supports; reruns retested own earlier size-4 witnesses as upper bounds and freshly exhausted all smaller supports.')
    assert result['cases'] == 72 and result['final_statuses'] == {'exact': 72}
    assert result['h2_h3_agreement'] == {'agree':48,'total':48}
    assert mismatches == [dict(idx=112,s=2,h=1,L_trunc=4,study_L=3)]
    (OUT / 'recomputation_summary.json').write_text(json.dumps(result, indent=2) + '\n')
    inputs = [
        'research/TRUE-BOND-20261113-001/codex_spec.md',
        'research/TRUE-BOND-20261113-001/preregistration.md',
        'research/TRUE-BOND-20261113-001/true_bond.md',
        'experiments/BOND-DEPTH-20261112-001A/BOND-DEPTH-20261112-001A-E001_spine_bonds/census.py',
        'artifacts/PROVED-RATE-20261113-001A/PROVED-RATE-20261113-001A-E001_cycle_mean/rates_all.jsonl',
        'artifacts/TRUE-BOND-20261113-001A/TRUE-BOND-20261113-001A-E001_side_branches/true_rates_all.jsonl',
        'artifacts/TRUE-BOND-20261113-001A/TRUE-BOND-20261113-001A-E001_side_branches/summary.json']
    manifest = dict(scope_kind='epic',scope_id='TRUE-BOND-20261113-001', purpose='Independent referee R1 recomputation and critique',
                    branch='code_analysis', interface=dict(
                        question='Least bond through a top port and C_s own distinction, with finite truncation members anywhere',
                        inputs='Frozen spec; permitted BD definitions and prior study selection; true rows used only for post-computation comparison',
                        forbidden='All files under study implementation directory; no study summary-DP imports',
                        outputs='72 direct SAT minimum rows plus witness projections, deletion tests, subgroup and status counts',
                        observables='Exact L_trunc(s,h); study discrepancy; completion/shortener cross-tabulation',
                        controls='Known NAE chain and free pattern; greatest port fixed point; separate CNF and second SAT solver',
                        stop='Eight deterministic selected families, s=1,2,3 and h=1,2,3; bounded per-case commands',
                        nonclaims='No arbitrary-depth lower bound from finite stabilization; no asymptotic rate or typical behavior'),
                    inputs_sha256={name:digest(ROOT/name) for name in inputs},
                    code_sha256={p.name:digest(p) for p in sorted(OUT.glob('*.py'))},
                    python=sys.version, executable=sys.executable, python_sat=version('python-sat'),
                    platform=platform.platform(), process_budget=2, memory_budget_mb=6144,
                    recomputation_address_space_cap_mb=4096, verification_address_space_cap_mb=2048,
                    commands=[
                        '.venv/bin/python -B research/TRUE-BOND-20261113-001/referee-R1/codex/recompute_sat.py --controls',
                        '.venv/bin/python -B research/TRUE-BOND-20261113-001/referee-R1/codex/recompute_sat.py --h 1 --seconds 15',
                        '.venv/bin/python -B research/TRUE-BOND-20261113-001/referee-R1/codex/recompute_sat.py --h 2 3 --seconds 10',
                        '.venv/bin/python -B research/TRUE-BOND-20261113-001/referee-R1/codex/recompute_sat.py --only 137 911 --s 3 --h 3 --seconds 60 --output recomputed_retries.jsonl --warm-witnesses recomputed.jsonl',
                        '.venv/bin/python -B research/TRUE-BOND-20261113-001/referee-R1/codex/verify_recomputation.py',
                        '.venv/bin/python -B research/TRUE-BOND-20261113-001/referee-R1/codex/audit_claims.py',
                        '.venv/bin/python -B research/TRUE-BOND-20261113-001/referee-R1/codex/summarize_recomputation.py'],
                    execution_environment={'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'},
                    calibration='controls_initial.json preserves a first fixture with an incorrect expected chain size; a surviving top port made that fixture shorter. The fixture was replaced by a chain using three fresh distinctions per copy. All final controls pass.',
                    write_boundary=str(OUT), git_mutations=False, publication=False,
                    implementation_access=False)
    (OUT / 'run_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('profiles',)}))


if __name__ == '__main__':
    main()
