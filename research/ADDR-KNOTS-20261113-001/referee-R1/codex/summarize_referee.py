"""Summarize retained referee outputs; this does not run a SAT solver."""
from __future__ import annotations

import collections
import hashlib
import importlib.metadata
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def summarize(folder):
    cases = [json.loads(p.read_text()) for p in sorted((HERE / folder).glob('*.json'))]
    levels = [level for case in cases for level in case['levels']]
    assert all(len(case['levels']) == 12 for case in cases)
    assert all(case['hash_matches'] and case['counts_match'] and case['joins_match'] and case['fate_agrees'] for case in cases)
    assert all(level['agrees'] for level in levels)
    assert all(level['certified'] for level in levels if level['verdict'] is not None)
    unknown = [{'key_id': case['key_id'], 'level': level['level'],
                'recorded_verdict': level['recorded_verdict'], 'reason': level.get('reason'),
                'attempts': level.get('refinements', [])}
               for case in cases for level in case['levels'] if level['verdict'] is None]
    return {
        'keys': len(cases), 'levels': len(levels),
        'alive_with_checked_assignments': sum(level['verdict'] == 1 for level in levels),
        'dead_with_checked_certificates': sum(level['verdict'] == 0 for level in levels),
        'symmetry_reduced_certificates': sum(level['verdict'] == 0 and bool(level.get('symmetry_reduction')) for level in levels),
        'unknown_count': len(unknown), 'unknown': unknown,
        'all_levels_certified_keys': sum(case['all_levels_certified'] for case in cases),
        'certified_returns': sum(case.get('fresh_return', False) for case in cases),
        'first_death_agreements': sum(case['fresh_first_death'] == case['recorded_first_death'] for case in cases),
        'sizes': sorted({case['key'][0] for case in cases}),
        'placement_counts': sorted({len(case['key'][4]) for case in cases}),
        'fates': dict(collections.Counter(case['fresh_fate'] for case in cases)),
        'hash_mismatches': 0, 'knot_count_mismatches': 0, 'joining_count_mismatches': 0, 'decided_verdict_mismatches': 0,
        'rows': [{'key_id': case['key_id'], 'alternating': case['alternating'],
                  'verdict_string': ''.join('?' if level['verdict'] is None else str(level['verdict']) for level in case['levels']),
                  'first_death': case['fresh_first_death'], 'return': case['fresh_return'],
                  'all_levels_certified': case['all_levels_certified']}
                 for case in cases]
    }


def main():
    returns = summarize('returns')
    sample = summarize('sample')
    assert returns['keys'] == 48 and returns['certified_returns'] == 48
    alternating_ids = {r['key_id'] for r in returns['rows'] if r['alternating']}
    alt_cases = [json.loads((HERE / 'returns' / f'{key}.json').read_text()) for key in alternating_ids]
    assert len(alt_cases) == 7 and all(case['all_levels_certified'] for case in alt_cases)
    alt_levels = [level for case in alt_cases for level in case['levels']]
    result = {'returns': returns, 'sample': sample,
              'alternating': {'keys': 7, 'levels': len(alt_levels),
                              'alive': sum(level['verdict'] == 1 for level in alt_levels),
                              'dead': sum(level['verdict'] == 0 for level in alt_levels),
                              'all_levels_certified': True},
              'relative_activity': json.loads((HERE / 'relative_activity.json').read_text()),
              'joining': json.loads((HERE / 'joining_check.json').read_text()),
              'environment': {'python': platform.python_version(), 'python_sat': importlib.metadata.version('python-sat'),
                              'network_used': False, 'child_compute_process_cap': 3,
                              'main_solver_address_space_cap_gib': 3},
              'code_sha256': {str(path.relative_to(HERE)): sha256(path) for path in sorted(HERE.glob('*.py'))}}
    assert result['relative_activity']['summary']['sampled_keys'] == 80
    assert result['relative_activity']['summary']['relative_class_degree_mismatches'] == 0
    assert result['relative_activity']['summary']['action_mismatches'] == 0
    assert result['joining']['summary']['levels_checked'] == 240
    assert result['joining']['summary']['k1_join_mismatches'] == 0
    assert result['joining']['summary']['pattern_hash_mismatches'] == 0
    result['code_sha256'].update({name: sha256(HERE / name) for name in ('check_rup_fast.cpp', 'check_rup_fast')})
    result['execution_notes'] = json.loads((HERE / 'execution_notes.json').read_text())
    manifest = json.loads((HERE / 'audit_manifest.json').read_text())
    result['input_sha256'] = {path: sha256(ROOT / path) for path in manifest['inputs']}
    (HERE / 'referee_summary.json').write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    table = ['| Key (first 12 SHA-256 digits) | Levels 1–12 | First death | Return certified |',
             '| --- | --- | ---: | --- |']
    for row in sorted(returns['rows'], key=lambda r: (not r['alternating'], r['key_id'])):
        mark = ' †' if row['alternating'] else ''
        table.append(f"| [{row['key_id'][:12]}](returns/{row['key_id']}.json){mark} | `{row['verdict_string']}` | {row['first_death']} | yes |")
    (HERE / 'certified_verdicts.md').write_text('\n'.join(table) + '\n')
    unknown_decided = [row for row in returns['unknown'] if row['recorded_verdict'] is not None]
    alt = result['alternating']
    certificate_method = ('All accepted certificates prove the original CNF without a symmetry unit. '
                          'The completed refinement certificate expands a proof of one complement-symmetry half into unconditional DRUP before checking. '
                          'Unfinished candidate proofs, including a reduced proof, are retained without crediting a verdict.'
                          if not returns['symmetry_reduced_certificates'] else
                          'Some certificates use a declared complement-symmetry unit. The replay checks complement invariance of F; '
                          'any model of F could be complemented to satisfy the unit, so unsatisfiability of that half proves unsatisfiability of F.')
    report = f'''Confirmed with fixes

Fresh code was written from the frozen specification and the mathematics; neither forbidden implementation was opened or imported. This is AI-authored independent recomputation, with activity and wording reviews by subagents in this task. All fate and joining-frequency conclusions concern the registered records and levels 1–12; activity classes are computed exactly from their finite automata. No human or external replication is claimed.

Validation independence is V2 for the fresh reconstruction against the study implementation. Comparisons between this task's Python and compiled checkers are same-task checks; no V3 claim is made.

## 1. Certified returns

All **48/48 returns** are independently certified: each has an independently proved dead level followed by a directly checked alive level. All 48 first deaths and F2 labels agree. The **seven parity-alternating descriptions have all 84 levels certified: {alt['alive']} alive and {alt['dead']} dead**, with no missing dead-level certificate.

Across all 48 descriptions, **{returns['alive_with_checked_assignments']} alive levels** have assignments checked directly against every reconstructed knot, **{returns['dead_with_checked_certificates']} dead levels** have checked unsatisfiability certificates, and **{returns['unknown_count']} levels remain uncertified**. {returns['all_levels_certified_keys']} descriptions have all twelve levels certified. There are no conflicting certified verdicts. The unresolved levels include {len(unknown_decided)} originally decided verdicts and {returns['unknown_count'] - len(unknown_decided)} original nulls; solver budget exhaustion or an incomplete certificate check neither confirms nor contradicts that original level. Exact levels, attempts, assignments and certificate paths are in [referee_summary.json](referee_summary.json) and each linked case below.

The fresh NAE encoding has exactly two clauses per distinct triple. {certificate_method} Both checkers use only unit propagation and never call a solver; ignored deletion lines are sound because every retained addition has already been proved RUP. The Python checker passed 4,000 comparisons with separate plain propagation, an exhaustively checked Fano example, and invalid/truncated-proof controls. The compiled checker passed 300 further plain-propagation comparisons and agrees with the Python checker on 20 saved certificates. Certificate replay files state which checker was used. No completed check of a retained solver certificate failed; interrupted checks remain uncredited.

**Narrowing:** F2 records an observed alive-then-dead pair, not permanent extinction. The supplied Glucose recheck confirms a return for every key but leaves 26 individual levels null; its `agree: true` does not certify all twelve levels.

`1` = directly verified alive; `0` = independently certified dead; `?` = uncertified in this audit. † identifies the seven alternating descriptions. Full keys and level evidence are linked.

''' + '\n'.join(table) + f'''

## 2. Fresh patterns and fates

The separate deterministic sample contains **{sample['keys']} records**, spanning state counts {sample['sizes']} and distinct placement counts {sample['placement_counts']}. All twelve knot counts, joining counts and full pattern hashes agree for every sampled record; every sampled level is directly verified alive, and its {sample['fates'].get('F0', 0)} F0 and {sample['fates'].get('F3', 0)} F3 fates agree. The empty cases are weak pattern controls; the 48 nonempty returning F2 descriptions supply an additional 576 reconstructed levels, and section 4 checks another 20 nonempty patterns. SHA-1 serialization is signed little-endian int64 level, row count, then lexicographically sorted distinct triples in row order.

Two separate builders—induction on suffix length and scalar letter-by-letter composition—agree on 200 further small pattern cases; reversing the specified product order is detected in 63 controls. Words `(q,r)` apply r first and then q. **Not a block:** no sampled reconstruction, hash or fate discrepancy was found. This is a stratified check, not an accuracy estimate for the entire census.

## 3. Relative activity classes

**80 nonempty distinct (pattern hash, relative class) units, 20 per class**, agree on relative class and polynomial degree. The independently built signed product automata include every ordered pair in each placement: 1,528 distinct products, 1,644 ordered pairs, and 780,808 finite action/address comparisons, all matching. Identity sections are detected behaviorally; the complete reachable component calculation, preserving parallel transitions, supplies the exact class. Analytic finitary, bounded, polynomial-degree-one/two and exponential controls, inverse identities, and deliberate wrong-action controls pass. Details: [relative_activity_notes.md](relative_activity_notes.md), [relative_activity.json](relative_activity.json).

**Narrowing:** as specified, V-rel checks relative **actions**, while V-act-class checks the original **letter maps**. Neither directly validates the primary inverse-product class calculation. This audit fills that gap on its 80-unit sample; a finite count discriminator alone would not prove an asymptotic class for every product automaton.

## 4. Joining counts and tail classes

For **20 globally distinct nonempty patterns, five per class**, all **240** level checks match `join_n`, knot counts and pattern hashes. Joining was counted independently using explicit suffix partitions. The registered `join_n` uses **k=1**, namely mixed last letters; the separately retained k=2 counts have no registered comparator. See [joining_check.json](joining_check.json).

**Block:** the assertion that every tail class has the same inner knots is false. In the proof note around line 110 and `addr_knots.md` around line 23, prefix action is mistaken for equality of the actual internal knot subsets. A two-state counterexample has `sw=[1,0]`, `d0=[1,0]`, `d1=[1,1]` and a single placement with word indices `(2,3,5)`, i.e. words `(1,)`, `(0,0)`, `(1,0)`. At level 4, after dropping the last two letters, suffix classes **00 and 01 have no internal triples**, while **10 and 11 each have {{(0,1,2),(0,1,3)}}**. The raw key's two additional placements add no level-4 triples. The total is 14 knots and agrees with the record. This was reconstructed separately by both the wording reviewer and the lead; full fixture: [pattern_controls.json](pattern_controls.json).

Fix: “A map's prefix action is independent of the suffix; its section determines the output suffix. Both internal knot subsets and joining knots may therefore depend on the tail.” This blocks the stated identical-copy interpretation, **not** the checked census or the separately stated B0 induction. Relative activity still bounds joining from above.

## 5. Wording and denominators

The note has correct explicit level-12 and weighting qualifications in its scope paragraph. Several headlines and the Answer nevertheless exceed those qualifications. Exact quotations, calculations and proposed replacements are in [wording_notes.md](wording_notes.md) and [wording_audit.json](wording_audit.json).

- **Narrowing:** “bounded joining is rare” should give frequencies and name **bounded relative activity**. It accounts for **453/5,759 = 7.87%** of nonempty W draws, versus **146/3,993 = 3.66%** of nonempty W pattern/class units, and **292/8,948 = 3.26%** in E. “About 8% of weight and patterns” conflates denominators. “A minority” is better calibrated; no threshold for “rare” was registered.
- **Narrowing:** class counts use `(hash, class)`, not distinct hashes: W has **3,997 memberships but 3,990 hashes**; E has **8,952 memberships but 8,937 hashes**. A pattern can be counted in multiple classes.
- **Narrowing:** exponential activity is an upper bound, not a lower bound on actual joining. Exponential-class key `cb20b8fe2c4262bab1f0cf6a4b0124c0f082e6e72267baf75842775b08776d97` has recorded joining counts `[0,4,4,…,4]`. Replace “almost every pattern doubles with each level” by the measured class averages at levels 10–12 under the registered weighting; “late ends need growing joining” becomes the observed association with exponential activity through level 12.
- **Narrowing:** the eligible comparison is where **few**, not zero, deaths occur: bounded has 0 deaths/36 units; exponential has 8 F2 and 16 FU among 1,108 units (1,092 decided). Its frozen equivalence verdict is within a ten-percentage-point margin, not equality. The density bins show association, rather than establishing that density determines fate.
- **Narrowing:** settlement is **74.8%** under each draw's own description flags (314/1,452 = 21.6% F2 among the rest), versus **79.9%** under the addendum's inherited pattern settlement (314/1,155 = 27.2%). Label which definition is used. The stated 61.8% one-state plus 18.2% other-empty raw composition is correct.
- **Narrowing:** qualify Lemma A's interpretation to its three uniform list forms, and qualify the gate-pass statement to the frozen summary's core checks with skipped ambiguous assertions. The unchecked finite-types remark is not promoted by this audit.
- **Not a block:** B0 and first-letter settlement have separately stated mathematical all-level scope; the finite census does not establish all-level survival, alternation, or per-pattern joining growth.

## Files and execution

Reconstruction and checks: `fresh_patterns.py`, `recompute.py`, `pattern_controls.py`, `check_rup.py`, `check_rup_fast.cpp`, compiled `check_rup_fast`, `fast_certificates.py`, `refine_unknowns.py`, `replay_certificates.py`, `relative_activity.py`, `joining_check.py`, `linear_assignments.py`, `cadical_families.py`, and `summarize_referee.py`. The bounded linear-colouring probe found no candidates for the initially unresolved levels and supplies no unsatisfiability conclusion. CaDiCaL family trajectories retain separately checked models and do not promote unlogged refutations.

Evidence: `returns/` (48 per-key JSON records), `sample/` ({sample['keys']} records), `certificates/` (accepted proofs plus explicitly unaccepted candidates), `certified_verdicts.md`, `referee_summary.json`, the activity/joining/wording files and notes, the control and selection JSON files, `audit_manifest.json`, `execution_notes.json`, replay JSON files, and execution logs. Source and code hashes are in the JSON records. Existing brief and last-message files were preserved.

**Not a block to the mathematics; procedural deviation:** initial PySAT calls used anonymous system-temporary proof files before its default was noticed. Their descriptors were closed; subsequent solver and verifier scratch and compiler temporary files are explicitly confined to this directory. This write-scope deviation is disclosed in [execution_notes.json](execution_notes.json); it is not a claim of perfect procedural compliance. No forbidden implementation, network, Git mutation or publishing was used.

Replay, without a SAT solver:

```sh
TMPDIR="$PWD/research/ADDR-KNOTS-20261113-001/referee-R1/codex" g++ -O2 -std=c++17 research/ADDR-KNOTS-20261113-001/referee-R1/codex/check_rup_fast.cpp -o research/ADDR-KNOTS-20261113-001/referee-R1/codex/check_rup_fast -lz
/home/jscul/p-vs-np-contact-first/.venv/bin/python -B research/ADDR-KNOTS-20261113-001/referee-R1/codex/replay_certificates.py all --fast
```

Report generated {datetime.now(timezone.utc).isoformat(timespec='seconds')}. The retained files, rather than unaccepted solver refutations, determine the verdict counts.
'''
    (HERE / 'codex_report.md').write_text(report)
    for label, values in [('returns', returns), ('sample', sample), ('alternating', result['alternating'])]:
        print(label, json.dumps({key: value for key, value in values.items() if key not in ('rows', 'unknown')}))


if __name__ == '__main__':
    main()
